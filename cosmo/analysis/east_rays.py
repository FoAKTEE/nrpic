"""Luminosity distance against redshift along light rays between the overdensity and
the underdensity: relativistic run, Newtonian reference, homogeneous universe
(cosmo/PLAN.md, C3; East, Wojtak & Pretorius, arXiv:1908.05683, Figs. 4 and 5).

    python3 east_rays.py [--runs runs/cosmo] [--n 64] [--deltas 0.0025,0.005,0.01,0.05]
                         [--gr-suffix _v2] [--newton-suffix _v2] [--suffix NAME]

Each bundle is followed from its emission to its first arrival at the other extremum
(coordinate path 2 sqrt(3) L / 4 along the diagonal). Left: D_L / D_FRW - 1 against z
for both calculations, where D_FRW is the homogeneous matter-dominated relation for an
emission at the proper time of the emitter. Right: D_L(GR) / D_L(Newtonian) - 1 at equal
redshift, on the part of the ray where the redshift increases monotonically.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, HERE)
from nrpic import figstyle as fs  # noqa: E402
import ray_obs as ar  # noqa: E402

L = 4.0
PATH = 2.0*np.sqrt(3.0)*L/4.0


def travelled(x):
    """Coordinate path length along the ray from its first record, unwrapped."""
    d = np.diff(x, axis=0)
    d -= L*np.round(d/L)
    return np.concatenate([[0.0], np.cumsum(np.sqrt((d*d).sum(axis=1)))])


def cut(b, x0):
    """Records up to the first arrival at the other extremum; finite values only."""
    x = np.vstack([x0[None, :], b["x"]])
    s = travelled(x)[1:]
    ok = (s <= PATH) & np.isfinite(b["z"]) & np.isfinite(b["D_L"])
    n = len(ok) if ok.all() else int(np.argmin(ok))
    return {k: (v[:n] if isinstance(v, np.ndarray) and v.ndim >= 1 and len(v) == len(ok)
                else v) for k, v in b.items()}


def monotonic(z):
    """Length of the leading part of z that increases."""
    d = np.diff(z) <= 0.0
    return len(z) if not d.any() else int(np.argmax(d)) + 1


def load_newton(path):
    d = np.load(path)
    out = []
    for i in range(int(d["nbundle"])):
        out.append({k[:-len(f"_{i}")]: d[k] for k in d.files if k.endswith(f"_{i}")})
    for o in out:
        for k in ("bundle", "kind"):
            o[k] = int(o[k])
        for k in ("tau_emit", "a_emit", "solid_angle"):
            o[k] = float(o[k])
    return out


def main():
    args = sys.argv[1:]
    opt = {args[i][2:]: args[i+1] for i in range(0, len(args) - 1, 2)}
    runs = opt.get("runs", os.path.join(REPO, "runs", "cosmo"))
    n = int(opt.get("n", "64"))
    deltas = [float(s) for s in opt.get("deltas", "0.0025,0.005,0.01,0.05").split(",")]
    gs, ns = opt.get("gr-suffix", "_v2"), opt.get("newton-suffix", "_v2")
    suffix = opt.get("suffix", "")
    fs.use_style()
    rows = []
    for d in deltas:
        gdir = os.path.join(runs, f"east_d{d:g}_n{n}{gs}")
        nfile = os.path.join(runs, f"newton_d{d:g}_n{n}{ns}", "newton_rays.npz")
        if os.path.exists(os.path.join(gdir, "rays.npz")) and os.path.exists(nfile):
            rows.append((d, gdir, nfile))
    if not rows:
        sys.exit("no pair of ray runs found")
    fig, axs = plt.subplots(len(rows), 2, figsize=(fs.FULL_WIDTH, 2.5*len(rows)),
                            squeeze=False)
    fig.subplots_adjust(left=0.10, right=0.985, bottom=0.07 if len(rows) > 1 else 0.17,
                        top=0.97, wspace=0.26, hspace=0.24)
    summary = {}
    for r, (d, gdir, nfile) in enumerate(rows):
        gb = {b["bundle"]: b for b in ar.gr_bundles(gdir)}
        nb = {b["bundle"]: b for b in load_newton(nfile)}
        ids = sorted(set(gb) & set(nb))
        cmap = fs.series_colors(max(len(ids)//2, 1) + 1)
        summ = summary.setdefault(f"{d:g}", [])
        for b in ids:
            g, w = gb[b], nb[b]
            kind = g["kind"]
            x0 = np.full(3, 0.25*L if kind == 0 else 0.75*L)
            g, w = cut(g, x0), cut(w, x0)
            if len(g["z"]) < 4 or len(w["z"]) < 4:
                continue
            c = cmap[(b//2) % len(cmap)]
            ls = "-" if kind == 0 else "--"
            ax = axs[r, 0]
            ax.plot(g["z"], g["D_L"]/g["D_FRW"] - 1.0, color=c, ls=ls, lw=1.2)
            ax.plot(w["z"], w["D_L"]/w["D_FRW"] - 1.0, color=c, ls=ls, lw=0.5)
            mg, mw = monotonic(g["z"]), monotonic(w["z"])
            zc = g["z"][:mg]
            sel = (zc >= w["z"][0]) & (zc <= w["z"][:mw][-1])
            if sel.sum() < 3:
                continue
            dn = np.interp(zc[sel], w["z"][:mw], w["D_L"][:mw])
            diff = g["D_L"][:mg][sel]/dn - 1.0
            axs[r, 1].plot(zc[sel], np.abs(diff), color=c, ls=ls, lw=1.0,
                           label=rf"$a_e = {g['a_emit']:.0f}$" if kind == 0 else None)
            big = int(np.argmax(np.abs(diff)))
            at = {zz: float(np.interp(zz, zc[sel], diff)) for zz in (0.1, 0.5, 1.0, 2.0)
                  if zc[sel][0] <= zz <= zc[sel][-1]}
            summ.append({"bundle": int(b), "kind": int(kind), "a_emit_gr": float(g["a_emit"]),
                         "a_emit_newton": float(w["a_emit"]), "z_end_gr": float(g["z"][-1]),
                         "z_end_newton": float(w["z"][-1]),
                         "frw_dev_gr_end": float(g["D_L"][-1]/g["D_FRW"][-1] - 1.0),
                         "max_abs_gr_minus_newton": float(np.abs(diff).max()),
                         "z_of_max": float(zc[sel][big]), "diff_at_z": at,
                         "blueshift_gr": bool(mg < len(g["z"])),
                         "blueshift_newton": bool(mw < len(w["z"]))})
        axs[r, 0].set_xscale("log")
        axs[r, 0].set_yscale("symlog", linthresh=1e-2)
        axs[r, 0].axhline(0.0, **fs.THIN)
        axs[r, 0].set_ylabel(rf"$D_L/D_{{\rm FRW}} - 1$, $\bar\delta = {d:g}$")
        axs[r, 1].set_xscale("log")
        axs[r, 1].set_yscale("log")
        axs[r, 1].set_ylim(1e-6, 1.0)
        axs[r, 1].set_ylabel(r"$|D_L^{\rm GR}/D_L^{\rm N} - 1|$")
        axs[r, 1].legend(frameon=False, fontsize=6, ncol=2, loc="upper left")
    for ax in axs[-1]:
        ax.set_xlabel(r"redshift $z$")
    figdir = os.path.join(HERE, "figs")
    fs.save(fig, os.path.join(figdir, "east_rays" + suffix))
    with open(os.path.join(HERE, "east_rays" + suffix + ".json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    for d, summ in summary.items():
        print(f"== delta = {d}")
        for s in summ:
            src = "OD" if s["kind"] == 0 else "UD"
            at = " ".join(f"z={k:g}:{v:+.2e}" for k, v in s["diff_at_z"].items())
            print(f"   {src} a_e {s['a_emit_gr']:6.1f} (N {s['a_emit_newton']:6.1f}) z_end "
                  f"{s['z_end_gr']:.3f}/{s['z_end_newton']:.3f}  D/FRW-1 at end "
                  f"{s['frw_dev_gr_end']:+.3f}  max|GR/N-1| {s['max_abs_gr_minus_newton']:.2e} "
                  f"at z={s['z_of_max']:.3f}  {at}  blueshift GR/N "
                  f"{int(s['blueshift_gr'])}/{int(s['blueshift_newton'])}")
    print(os.path.join(figdir, "east_rays" + suffix + ".png"))


if __name__ == "__main__":
    main()
