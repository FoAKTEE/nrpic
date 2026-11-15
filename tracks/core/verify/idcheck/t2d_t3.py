#!/usr/bin/env python3
"""Open analysis of the initial data with extrinsic curvature (tracks/core/JOURNAL-id.md):
T2d (interior Hamiltonian residual of the smooth-edge runs: lattice and deposit noise?)
and T3 (bound ball through turnaround), including runs that lost particles.

Reuses tracks/core/analysis/id/test2_evolution.py (read-only) with two changes made
here, not in that file:
  - tracked-particle records are cut at the last record before the first tracked
    particle is removed (test2_evolution stops with ValueError on such runs);
  - field dumps whose snapshot has no ball particle left are skipped in the region
    statistics (test2_evolution takes the maximum of an empty array there: the crash
    on t3-bound-gs0-n160).
Writes t2d_t3_numbers.json into the working directory (the run's output directory) and
figures tracks/core/verify/figs/id_t2d_interior.{png,pdf}, id_t3_bound.{png,pdf}.

    python3 t2d_t3.py
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
IDDIR = os.path.join(WT, "tracks", "core", "analysis", "id")
FIGS = os.path.join(WT, "tracks", "core", "verify", "figs")
sys.path.insert(0, IDDIR)
sys.path.insert(0, os.path.join(WT, "python"))

import idlib  # noqa: E402
import test2_evolution as t2  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

_read_traj_orig = idlib.read_traj


def read_traj_cut(rundir, base="ball"):
    """As idlib.read_traj, but a run whose tracked particles are removed is cut at the
    last record at which all of them are present (records: time, tag, x, u)."""
    try:
        d = _read_traj_orig(rundir, base)
        d["cut_time"] = None
        return d
    except ValueError:
        pass
    a = np.fromfile(os.path.join(rundir, base + ".traj.bin"), dtype="<f8").reshape(-1, 8)
    b = np.fromfile(os.path.join(rundir, base + ".trajmet.bin"), dtype="<f8").reshape(-1, 17)
    times = np.unique(a[:, 0])
    tags0 = np.unique(a[a[:, 0] == times[0], 1])
    keep_t = [t for t in times if np.array_equal(np.unique(a[a[:, 0] == t, 1]), tags0)]
    # all records up to the first incomplete one
    first_bad = next((t for t in times if t not in set(keep_t)), None)
    keep_t = np.array([t for t in keep_t if first_bad is None or t < first_bad])
    sel = np.isin(a[:, 0], keep_t) & np.isin(a[:, 1], tags0)
    a, b = a[sel], b[sel]
    # non-finite records (a run that went to NaN with particles still present)
    fin = np.all(np.isfinite(a), axis=1) & np.all(np.isfinite(b), axis=1)
    bad_t = np.unique(a[~fin, 0])
    if len(bad_t):
        keep_t = keep_t[keep_t < bad_t.min()]
        sel = np.isin(a[:, 0], keep_t)
        a, b = a[sel], b[sel]
    nt, npart = len(keep_t), len(tags0)
    order = np.lexsort((a[:, 1], a[:, 0]))
    a = a[order].reshape(nt, npart, 8)
    b = b[order].reshape(nt, npart, 17)
    return dict(time=keep_t, tag=tags0.astype(int), x=a[:, :, 2:5], u=a[:, :, 5:8],
                alpha=b[:, :, 2], beta=b[:, :, 3:6], g=b[:, :, 6:12], tau=b[:, :, 12],
                E=b[:, :, 13], cut_time=float(first_bad) if first_bad is not None else None)


idlib.read_traj = read_traj_cut
t2.idlib.read_traj = read_traj_cut


def region_constraints_safe(d):
    """test2_evolution.region_constraints, skipping dumps without ball particles and
    non-finite dumps (recorded as such)."""
    out, skipped = [], []
    nt = d["meta"]["n_tracers"]
    snaps = {}
    for f in sorted(glob.glob(os.path.join(d["out"], "ball.part.*.bin"))):
        s = idlib.read_snapshot(f)
        snaps[round(s["time"], 6)] = s
    for f in sorted(glob.glob(os.path.join(d["out"], "ball.field.*.bin"))):
        fld = idlib.read_field(f)
        key = min(snaps, key=lambda t: abs(t - fld["time"])) if snaps else None
        if key is None or abs(key - fld["time"]) > 0.6 * d["dx"]:
            continue
        s = snaps[key]
        ballp = s["tag"] >= nt
        if not ballp.any():
            skipped.append(dict(time=fld["time"], reason="no ball particle left"))
            continue
        if not np.all(np.isfinite(fld["H"])):
            skipped.append(dict(time=fld["time"], reason="non-finite field"))
            continue
        rp = np.sqrt(np.sum(s["x"][ballp] ** 2, axis=1))
        rs = float(rp.max())
        r = idlib.cell_radius(fld["n"], d["half"])
        dx = d["dx"]
        edge = d["meta"]["edge"]
        reg = dict(interior=r < rs - 4.0 * dx - 2.0 * edge,
                   surface=(r >= rs - 4.0 * dx - 2.0 * edge) & (r <= rs + 4.0 * dx),
                   exterior=(r > rs + 4.0 * dx) & (r < 0.56 * d["half"]),
                   boundary=(r > 0.7 * d["half"]) & (r < d["half"] - 4.0 * dx),
                   all=np.ones_like(r, dtype=bool))
        rec = dict(time=fld["time"], r_surface=rs, E_centre=float(fld["E"][tuple(m // 2 for m in fld["H"].shape)]))
        for name, mask in reg.items():
            rec[name] = (dict(H_rms=float(np.sqrt(np.mean(fld["H"][mask] ** 2))),
                              H_mean_abs=float(np.mean(np.abs(fld["H"][mask]))),
                              n=int(mask.sum())) if mask.any() else None)
        out.append(rec)
    return out, skipped


def hst_summary(d):
    h = d["hst"]
    t, ac, npart = h[:, 0], h[:, 12], h[:, 2]
    bad = np.nonzero(~np.isfinite(ac) | (npart < npart[0]))[0]
    return dict(t=t.tolist(), alpha_centre=[float(v) if np.isfinite(v) else None for v in ac],
                np=npart.tolist(),
                first_loss_time=float(t[bad[0]]) if len(bad) else None,
                np_end=int(npart[-1]),
                alpha_centre_max_before_loss=float(np.nanmax(ac[:bad[0]] if len(bad) else ac)))


T2D = ["ct-edge2-n064", "ct-edge2-n128", "ct-edge2-n256", "ct-edge2-ext-n064",
       "ct-edge2-ext-n128", "ct-edge2-ext-n256", "ct-edge2-prod-n128", "ct-edge2-prod-n256"]


def main():
    res = dict(t2d={}, t3={})
    m2 = idlib.manifests("t2-")
    for k in T2D:
        m = m2["t2-" + k]
        d = t2.load(m)
        reg, skipped = region_constraints_safe(d)
        res["t2d"][k] = dict(run_id=m["run_id"], dx=d["dx"], regions=reg, skipped=skipped,
                             groups=t2.group_numbers(d))
        print(f"T2d {k:20s} {m['run_id']}  interior rms H: " + "  ".join(
            f"t={r['time']:.0f}:{r['interior']['H_rms']:.2e}" for r in reg))
    m3 = idlib.manifests("t3-")
    for tag in sorted(m3):
        m = m3[tag]
        k = tag[3:]
        d = t2.load(m)
        reg, skipped = region_constraints_safe(d)
        tr_cut = read_traj_cut(m["output_directory"]).get("cut_time")
        res["t3"][k] = dict(run_id=m["run_id"], dx=d["dx"], card_hours=m.get("card_hours"),
                            traj_cut_time=tr_cut, traj_t_end=float(d["t"][-1]),
                            tau_centre_end=float(np.max(d["tau"][-1])),
                            hst=hst_summary(d), regions=reg, skipped=skipped,
                            groups=t2.group_numbers(d))
        hs = res["t3"][k]["hst"]
        print(f"T3 {k:16s} {m['run_id']} dx={d['dx']:.3f} traj to t={float(d['t'][-1]):.2f}"
              f" (cut {tr_cut}), first loss {hs['first_loss_time']}, np_end {hs['np_end']},"
              f" skipped dumps {len(skipped)}")
        for g in ("core", "mid", "outer", "surface"):
            gg = res["t3"][k]["groups"][g]
            ta = gg.get("turnaround")
            e8 = gg.get("tau8", {}).get("maxabs")
            print(f"     {g:8s} max|eps| all {gg['maxabs_all']:.2e}  tau8 {e8 if e8 is None else f'{e8:.2e}'}"
                  + (f"  a_max {ta['a_max_mean']:.4f}+-{ta['a_max_spread']:.4f} at tau {ta['tau_mean']:.2f}" if ta else ""))
    with open("t2d_t3_numbers.json", "w") as f:
        json.dump(res, f)
    figures(res)


def figures(res):
    fs.use_style()
    os.makedirs(FIGS, exist_ok=True)
    # ---- T2d: interior rms of H against time, and at t = 8, 10 M against dx
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.90, wspace=0.36)
    fam = [("ct-edge2", "CIC, Hermite", fs.PAL["red"]),
           ("ct-edge2-ext", "CIC, extrapolated sources", fs.PAL["yellow"]),
           ("ct-edge2-prod", "production deposit", fs.PAL["blue"])]
    lss = {1.0: ":", 0.5: "--", 0.25: "-"}
    for f, lab, c in fam:
        keys = [k for k in T2D if k.rsplit("-n", 1)[0] == f]
        for k in keys:
            v = res["t2d"][k]
            t = [r["time"] for r in v["regions"]][1:]
            ax[0].semilogy(t, [r["interior"]["H_rms"] for r in v["regions"]][1:],
                           color=c, ls=lss[v["dx"]], marker="o", ms=3)
            ax[1].semilogy(t, [r["boundary"]["H_rms"] for r in v["regions"]][1:],
                           color=c, ls=lss[v["dx"]], marker="o", ms=3)
        dx = np.array([res["t2d"][k]["dx"] for k in keys])
        for tt, mk in ((8.0, "s"), (10.0, "o")):
            y = [next(r["interior"]["H_rms"] for r in res["t2d"][k]["regions"]
                      if abs(r["time"] - tt) < 1e-6) for k in keys]
            ax[2].loglog(dx, y, mk + "-", color=c, mfc="none" if tt == 8.0 else c,
                         label=lab if tt == 10.0 else None)
    ax[2].loglog([0.25, 1.0], [5e-5, 5e-5], **fs.GUIDE)
    ax[2].text(0.27, 5.6e-5, "T2d bound", fontsize=8)
    for ls, dxv in ((":", 1.0), ("--", 0.5), ("-", 0.25)):
        ax[0].plot([], [], color="k", ls=ls, label=r"$\Delta x=%g\,M$" % dxv)
    for f, lab, c in fam:
        ax[0].plot([], [], color=c, label=lab)
    ax[0].legend(fontsize=7, ncol=1, loc="lower right")
    ax[0].set_title("interior", fontsize=10)
    ax[1].set_title(r"boundary layer ($r>0.7\,L$)", fontsize=10)
    for a in ax[:2]:
        a.set_xlabel(r"coordinate time $t/M$", labelpad=-2)
        a.set_ylim(1e-6, 2e-3)
    ax[0].set_ylabel(r"rms of $H$ in the region")
    ax[2].set_xlabel(r"cell size $\Delta x/M$", labelpad=-2)
    ax[2].set_ylabel(r"interior rms $H$, $t=8$ (open), $10\,M$")
    ax[2].set_xticks([0.25, 0.5, 1.0])
    ax[2].set_xticklabels(["1/4", "1/2", "1"])
    ax[2].xaxis.set_minor_formatter(plt.NullFormatter())
    ax[2].legend(fontsize=7, loc="lower right")
    fs.save(fig, os.path.join(FIGS, "id_t2d_interior"))
    plt.close(fig)

    # ---- T3: central lapse, error of the shells, interior H
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.90, wspace=0.36)
    keys = sorted(res["t3"], key=lambda k: (k.split("-")[1], -res["t3"][k]["dx"]))
    cols = fs.series_colors(len(keys), cmap="turbo")
    for k, c in zip(keys, cols):
        v = res["t3"][k]
        h = v["hst"]
        ac = np.array([np.nan if a is None else a for a in h["alpha_centre"]])
        ax[0].plot(h["t"], np.clip(ac, -0.5, 3.0), color=c,
                   label=r"%s, $\Delta x=%g$" % (k.rsplit("-n", 1)[0].replace("bound-", ""), v["dx"]))
        if h["first_loss_time"] is not None:
            ax[0].axvline(h["first_loss_time"], color=c, lw=0.8, ls=":")
        reg = v["regions"]
        ax[2].semilogy([r["time"] for r in reg], [r["interior"]["H_rms"] if r["interior"] else np.nan
                                                  for r in reg], "o-", color=c, ms=3)
        g = v["groups"]
        tau = [2, 4, 6, 8, 10, 12]
        y = [max((g[n].get(f"tau{t}", {}).get("maxabs", np.nan) for n in ("core", "mid", "outer")),
                 default=np.nan) for t in tau]
        ax[1].semilogy(tau, y, "s-", color=c, ms=3)
    ax[0].set_ylim(-0.5, 3.0)
    ax[0].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[0].set_ylabel("lapse at the centre (clipped)")
    ax[0].legend(fontsize=6.5, loc="upper left")
    ax[1].set_xlabel(r"proper time of the shells $\tau/M$", labelpad=-2)
    ax[1].set_ylabel(r"largest $|R/R_{\rm exact}-1|$, ball shells")
    ax[2].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[2].set_ylabel(r"interior rms $H$")
    fs.save(fig, os.path.join(FIGS, "id_t3_bound"))
    plt.close(fig)


if __name__ == "__main__":
    main()
