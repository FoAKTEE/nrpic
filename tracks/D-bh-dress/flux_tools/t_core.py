#!/usr/bin/env python3
"""Test of the readers and the comparison on core's own test output (journal entries 1, 2).

    t_core.py --t3 <core T3 run dir> --t7 <core T7 run dir> [--out DIR]

T3 (run core-20261115-160245-727e96a): static Schwarzschild in Kerr-Schild coordinates,
cases mesh, mesh_rs (stopped and continued), analytic. Checked against this package's own
exact references (exact_ks.py): removal records (count, energy, step), the content
identity of the flux spheres, the crossing counts of the spheres, the restart case byte for
byte, and compare() with a synthetic horizon history (prediction 7).
T7 (run core-20261115-163129-a200caf): spheres on a moving puncture tracker: content
identity, centre against the tracker file, reader of the removal record.
Writes t_core.json and figures t_core_t3.png, t_core_t7.png into --out.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compare as cmp  # noqa: E402
import exact_ks as ek  # noqa: E402
import fluxio  # noqa: E402

ALPHA_EXC = 0.62
DT = 0.05
SPHERES = (4.0, 10.0)
TEND = 800.0


def exact_t3(nrp):
    E, L, ur, r0 = ek.invariants(nrp["x"], nrp["u"])
    r_exc = ek.r_of_alpha(ALPHA_EXC)
    orbs = [ek.Orbit(r0[i], E[i], L[i], ur[i]) for i in range(nrp["n"])]
    t_exc = np.array([o.t_in(r_exc) if o.captured else np.nan for o in orbs])
    t_hor = np.array([o.t_in(2.0) if o.captured else np.nan for o in orbs])
    cross = {}
    for rs in SPHERES:
        ins, outs = [], []
        for o in orbs:
            i_, o_ = o.crossings(rs, TEND)
            ins += i_
            outs += o_
        cross[rs] = (np.sort(ins), np.sort(outs))
    return dict(E=E, L=L, r0=r0, captured=np.array([o.captured for o in orbs]),
                t_exc=t_exc, t_hor=t_hor, r_exc=r_exc, cross=cross)


def check_case(d, ex, nrp):
    rem = fluxio.read_removed(os.path.join(d, "acc.removed.bin"))
    acc = fluxio.read_hst(os.path.join(d, "acc.acc.hst"))
    hst = fluxio.read_hst(os.path.join(d, "acc.nrpic.hst"))
    tag = rem["tag"]
    res = dict(n_records=int(rem["n"]), reasons=sorted(set(rem["reason"].tolist())),
               species=sorted(set(rem["species"].tolist())),
               n_excised_acc=int(acc["n_excised"][-1]), n_excised_hst=int(hst["n_excised"][-1]),
               m_records=float(rem["m"].sum()), m_excised_acc=float(acc["m_excised"][-1]),
               m_excised_hst=float(hst["m_excised"][-1]),
               mE_records=float((rem["m"] * rem["E"]).sum()),
               mE_excised_acc=float(acc["mE_excised"][-1]))
    dE = rem["E"] / ex["E"][tag] - 1.0
    res["E_relerr_max"] = float(np.abs(dE).max())
    lag = (rem["time"] - ex["t_exc"][tag]) / DT
    res["removal_lag_steps_min"] = float(lag.min())
    res["removal_lag_steps_max"] = float(lag.max())
    res["mE_exact_removed"] = float((nrp["m"][tag] * ex["E"][tag]).sum())
    # content identity: every removal happens inside both spheres (r_exc < 4)
    ident = {}
    for k in (1, 2):
        n_pred = acc[f"n_inside{k}"][0] + acc[f"n_in{k}"] - acc[f"n_out{k}"] - acc["n_excised"]
        m_pred = acc[f"m_inside{k}"][0] + acc[f"m_in{k}"] - acc[f"m_out{k}"] - acc["m_excised"]
        ident[k] = dict(n_maxerr=float(np.abs(acc[f"n_inside{k}"] - n_pred).max()),
                        m_maxerr=float(np.abs(acc[f"m_inside{k}"] - m_pred).max()))
    res["identity"] = ident
    # crossing counts against the exact orbits, at the acc.hst record times
    cc = {}
    t = acc["time"]
    for k, rs in zip((1, 2), SPHERES):
        ins, outs = ex["cross"][rs]
        n_in_ex = np.searchsorted(ins, t, side="right")
        n_out_ex = np.searchsorted(outs, t, side="right")
        # tolerance: exact crossings within one record interval (and a step) before t
        dtr = np.median(np.diff(t))
        amb_in = np.searchsorted(ins, t, side="right") - np.searchsorted(ins, t - dtr - DT, side="left")
        amb_out = np.searchsorted(outs, t, side="right") - np.searchsorted(outs, t - dtr - DT, side="left")
        bad_in = np.abs(acc[f"n_in{k}"] - n_in_ex) > amb_in
        bad_out = np.abs(acc[f"n_out{k}"] - n_out_ex) > amb_out
        cc[rs] = dict(n_in_end=int(acc[f"n_in{k}"][-1]), n_in_exact=int(len(ins)),
                      n_out_end=int(acc[f"n_out{k}"][-1]), n_out_exact=int(len(outs)),
                      records_outside_tolerance=int(bad_in.sum() + bad_out.sum()),
                      mE_in_end=float(acc[f"mE_in{k}"][-1]), mE_out_end=float(acc[f"mE_out{k}"][-1]))
    res["crossings"] = cc
    return res, rem, acc


def synthetic_compare(rem, acc, ex, nrp, scale=1.0):
    t = np.arange(0.0, TEND + 1e-9, 0.5)
    ok = np.isfinite(ex["t_hor"])
    mE = nrp["m"][ok] * ex["E"][ok]
    M = 1.0 + scale * cmp.step_cumsum(ex["t_hor"][ok], mE, t)
    hor = dict(time=t, mass=M)
    return cmp.compare(hor, 0.0, rem=rem, acc=acc, finder_tol=1e-5, sphere=1)


def check_t7(d):
    acc = fluxio.read_hst(os.path.join(d, "atr.acc.hst"))
    rem = fluxio.read_removed(os.path.join(d, "atr.removed.bin"))
    co = np.loadtxt(os.path.join(d, "atr.co_0.txt"))
    n_pred = acc["n_inside1"][0] + acc["n_in1"] - acc["n_out1"] - acc["n_excised"]
    # removals counted only if inside the sphere: record field dist
    inside = rem["dist"] < acc["radius1"][0]
    res = dict(n_records=int(rem["n"]), reasons=sorted(set(rem["reason"].tolist())),
               removed_inside_sphere=int(inside.sum()),
               n_excised_end=int(acc["n_excised"][-1]),
               n_in_end=int(acc["n_in1"][-1]), n_out_end=int(acc["n_out1"][-1]),
               identity_n_maxerr=float(np.abs(acc["n_inside1"] - n_pred).max()))
    # centre against the tracker: the row labelled t^n holds the position at t^(n+1);
    # compare acc.hst centre at time t with the tracker row whose NEXT time is t
    tt = co[:, 1]
    dt = np.median(np.diff(tt))
    errs = []
    for ti, cx, cy, cz in zip(acc["time"], acc["centre_x"], acc["centre_y"], acc["centre_z"]):
        j = np.where(np.abs(tt + dt - ti) < 1e-9 * max(1.0, ti))[0]
        if j.size:
            errs.append(np.abs(co[j[-1], 2:5] - [cx, cy, cz]).max())
    res["centre_tracker_maxerr"] = float(max(errs)) if errs else None
    res["centre_rows_compared"] = len(errs)
    return res, acc


def figures(out, cases, ex, nrp, syn, syn_bad, t7acc):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python", "nrpic"))
    import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(figstyle.FULL_WIDTH, 5.6))
    cols = dict(mesh=figstyle.PAL["blue"], mesh_rs=figstyle.PAL["yellow"],
                analytic=figstyle.PAL["red"])
    for name, (res, rem, acc) in cases.items():
        tag = rem["tag"]
        ax[0, 0].semilogy(ex["r0"][tag] + 0.05 * (name == "analytic"),
                          np.abs(rem["E"] / ex["E"][tag] - 1.0) + 1e-17, "o", ms=2.5,
                          color=cols[name], label=name)
        ax[0, 1].plot(ex["t_exc"][tag], (rem["time"] - ex["t_exc"][tag]) / DT, "o", ms=2.5,
                      color=cols[name], label=name)
    ax[0, 0].set_xlabel(r"$r_0\ [M]$ of the shell")
    ax[0, 0].set_ylabel(r"$|E_{\rm rec}/E_{\rm exact}-1|$")
    ax[0, 0].legend(fontsize=7)
    ax[0, 1].axhline(0, **figstyle.THIN)
    ax[0, 1].axhline(1, **figstyle.THIN)
    ax[0, 1].set_xlabel(r"exact $t_{\rm exc}\ [M]$")
    ax[0, 1].set_ylabel(r"$(t_{\rm rec}-t_{\rm exc})/\Delta t$")
    ax[0, 1].set_ylim(-0.5, 1.5)
    res, rem, acc = cases["mesh"]
    t = acc["time"]
    for k, rs, c in ((1, 4.0, figstyle.PAL["blue"]), (2, 10.0, figstyle.PAL["red"])):
        ins, outs = ex["cross"][rs]
        ax[1, 0].plot(t, acc[f"n_in{k}"], color=c, label=f"in, $r={rs:g}$ (code)")
        ax[1, 0].plot(t, acc[f"n_out{k}"], color=c, ls=":", label=f"out, $r={rs:g}$ (code)")
        ax[1, 0].step(ins, np.arange(1, len(ins) + 1), where="post", **dict(figstyle.GUIDE, lw=0.8))
        if len(outs):
            ax[1, 0].step(outs, np.arange(1, len(outs) + 1), where="post", **dict(figstyle.GUIDE, lw=0.8))
    ax[1, 0].set_xscale("log")
    ax[1, 0].set_xlim(5, TEND)
    ax[1, 0].set_xlabel(r"$t\ [M]$")
    ax[1, 0].set_ylabel("cumulative crossings")
    ax[1, 0].legend(fontsize=6, title="dashed: exact", title_fontsize=6)
    a = ax[1, 1]
    a.plot(syn["t"], syn["dM"], color=figstyle.PAL["blue"], label=r"synthetic $\Delta M_{\rm AH}$")
    a.step(syn["t"], syn["F_rem"], where="post", color=figstyle.PAL["red"], label=r"$F_{\rm rem}$")
    a.plot(syn["t"], syn["F_sph"], color=figstyle.PAL["green"], label=r"$F_{\rm sph}$, $r=4$")
    a.plot(syn_bad["t"], syn_bad["dM"], color="grey", ls="--", label=r"growth $\times 0.95$")
    a.set_xlim(0, 60)
    a.set_xlabel(r"$t\ [M]$")
    a.set_ylabel(r"$[M]$")
    a.legend(fontsize=6)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "t_core_t3"))
    plt.close(fig)
    fig, a = plt.subplots(figsize=(figstyle.COLUMN_WIDTH * 1.4, 3.0))
    a.plot(t7acc["time"], t7acc["n_in1"], label="in", color=figstyle.PAL["blue"])
    a.plot(t7acc["time"], t7acc["n_out1"], label="out", color=figstyle.PAL["red"])
    a.plot(t7acc["time"], t7acc["n_inside1"], label="inside", color=figstyle.PAL["green"])
    a.plot(t7acc["time"], t7acc["n_excised"], label="removed", color=figstyle.PAL["yellow"])
    a.set_xlabel(r"$t\ [M]$")
    a.set_ylabel("particles, sphere $r=2$ on the tracker")
    a.legend(fontsize=7)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "t_core_t7"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t3", required=True)
    ap.add_argument("--t7", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    nrp = fluxio.read_nrp(os.path.join(a.t3, "mesh", "acc_static.nrp"))
    ex = exact_t3(nrp)
    out = dict(exact=dict(r_exc=ex["r_exc"],
                          shells={str(r): dict(E=float(ex["E"][ex["r0"].round(6) == r][0]),
                                               t_exc=float(ex["t_exc"][ex["r0"].round(6) == r][0]),
                                               t_hor=float(ex["t_hor"][ex["r0"].round(6) == r][0]))
                                  for r in (6.0, 8.0, 11.0)},
                          mE_shells=float((nrp["m"] * ex["E"])[ex["captured"]].sum()),
                          crossings={str(rs): dict(n_in=len(v[0]), n_out=len(v[1]))
                                     for rs, v in ex["cross"].items()}))
    cases = {}
    for name in ("mesh", "mesh_rs", "analytic"):
        res, rem, acc = check_case(os.path.join(a.t3, name), ex, nrp)
        cases[name] = (res, rem, acc)
        out[name] = res
    b1 = open(os.path.join(a.t3, "mesh", "acc.removed.bin"), "rb").read()
    b2 = open(os.path.join(a.t3, "mesh_rs", "acc.removed.bin"), "rb").read()
    out["mesh_rs_removed_identical"] = b1 == b2
    acc1, acc2 = cases["mesh"][2], cases["mesh_rs"][2]
    out["mesh_rs_acc_identical"] = all(np.array_equal(acc1[k], acc2[k]) for k in acc1)
    rem, acc = cases["mesh"][1], cases["mesh"][2]
    syn = synthetic_compare(rem, acc, ex, nrp)
    syn_bad = synthetic_compare(rem, acc, ex, nrp, scale=0.95)
    out["synthetic"] = syn["summary"]
    out["synthetic_scaled_0.95"] = syn_bad["summary"]
    t7, t7acc = check_t7(os.path.join(a.t7, "run"))
    out["t7"] = t7
    figures(a.out, cases, ex, nrp, syn, syn_bad, t7acc)
    with open(os.path.join(a.out, "t_core.json"), "w") as f:
        json.dump(cmp.jsonable(out), f, indent=1)
    print(json.dumps(cmp.jsonable(out), indent=1))


if __name__ == "__main__":
    main()
