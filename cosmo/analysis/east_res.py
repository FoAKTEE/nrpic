"""Resolution dependence of the single-wavelength collapse at amplitude 0.01 (cosmo/PLAN.md,
C4; East, Wojtak & Pretorius, arXiv:1908.05683, Fig. 1 bottom and appendix).

    python3 east_res.py [--runs runs/cosmo] [--ns 64,96,128] [--tag tsc]

Observer density contrast at the overdensity for each cell number, relativistic and
Newtonian; infall of the fiducial observers and the relativistic delay; the constraint
violation against the scale factor (cell mean of the relative Hamiltonian constraint,
and the norm of the Hamiltonian constraint over the proper volume of the box, rescaled
by the square of the cell number).
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
import east_c2 as ec  # noqa: E402
import shape_study as ss  # noqa: E402
from delta_obs import gr_probes  # noqa: E402


def main():
    args = sys.argv[1:]
    opt = {args[i][2:]: args[i+1] for i in range(0, len(args) - 1, 2)}
    runs = opt.get("runs", os.path.join(REPO, "runs", "cosmo"))
    ns = [int(v) for v in opt.get("ns", "64,96,128").split(",")]
    tag = opt.get("tag", "tsc")
    d = 0.01
    fs.use_style()
    cols = [fs.PAL["blue"], fs.PAL["green"], fs.PAL["red"], fs.PAL["orange"]]
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.95, wspace=0.36)
    summ = {}
    for c, n in zip(cols, ns):
        gdir = os.path.join(runs, f"east_d{d:g}_n{n}_{tag}")
        if not os.path.exists(os.path.join(gdir, "east.nrpic.hst")):
            continue
        s = summ.setdefault(str(n), {})
        g, h = gr_probes(gdir)
        axs[0].loglog(g["a_p_0"], g["delta_obs_0"], color=c, label=rf"$N_g = {n}$")
        f = ec.gr_fiducial(gdir)
        dg = ec.distances(f["x"], f["q"], f["axis"])
        apg = ec.a_of_tau(f["tau"])
        nfile = os.path.join(runs, f"newton_d{d:g}_n{n}_{tag}", "newton.npz")
        nw = dict(np.load(nfile)) if os.path.exists(nfile) else None
        if nw is not None:
            ok = np.isfinite(nw["delta_obs_0"])
            axs[0].loglog(nw["a_p_0"][ok], nw["delta_obs_0"][ok], color=c, ls="--", lw=0.8)
            dn = ec.distances(np.mod(nw["x"], ec.L), nw["q_fid"], nw["axis_fid"])
            apn = ec.a_of_tau(nw["t_p"])
        for fr in ec.SHOWN:
            gg, nn = [], []
            for j in range(len(f["axis"])):
                s0 = f["q"][j, f["axis"][j]] - ec.XPK
                if abs(s0 - fr*ec.L) < 1e-9:
                    gg.append(ec.below(apg[:, j], dg[:, j], 0.1*dg[0, j]))
                    if nw is not None:
                        nn.append(ec.below(apn[:, j], dn[:, j], 0.1*dn[0, j]))
            s[f"a10_L/{1.0/fr:.0f}"] = [float(np.mean(gg)), float(np.mean(nn)) if nn else None]
        s["rise"] = [ec.rise(g["a_p_0"], g["delta_obs_0"], lev) for lev in (1.0, 10.0, 100.0)]
        cs = ss.cstat(gdir)
        if cs is not None:
            axs[1].loglog(cs["a"][1:], cs["Hr_mean"][1:], color=c)
            sel = cs["a"] <= 40.0
            s["Hr_mean_at_a"] = {str(av): float(np.interp(av, cs["a"], cs["Hr_mean"]))
                                 for av in (2.0, 5.0, 10.0, 20.0, 40.0, 100.0)}
        z = np.loadtxt(os.path.join(gdir, "east.z4c.user.hst"))
        az = (1.0 + 0.5*z[:, 0])**2
        ok = z[:, 10] > 0.0
        # root mean square of H over the proper volume, relative to 16 pi rho of the mean
        rel = np.sqrt(z[ok, 3]/z[ok, 10])/(6.0/az[ok]**3)
        axs[2].loglog(az[ok][1:], rel[1:]*(n/ns[0])**2, color=c)
        s["Hrms_rel_at_a"] = {str(av): float(np.interp(av, az[ok], rel))
                              for av in (2.0, 5.0, 10.0, 20.0, 40.0)}
    axs[0].set_xlim(10.0, 150.0)
    axs[0].set_ylim(0.3, 3e4)
    axs[0].set_xlabel(r"$a_p$")
    axs[0].set_ylabel(r"$\delta_{\rm obs}$ at the overdensity")
    axs[0].legend(frameon=False, loc="upper left")
    axs[1].set_xlabel(r"scale factor $a$")
    axs[1].set_ylabel(r"mean of $H_r$")
    axs[2].set_xlabel(r"scale factor $a$")
    axs[2].set_ylabel(r"rms of $H$ / largest term, $\times (N_g/%d)^2$" % ns[0])
    figdir = os.path.join(HERE, "figs")
    fs.save(fig, os.path.join(figdir, "east_res"))
    with open(os.path.join(HERE, "east_res.json"), "w") as fp:
        json.dump(summ, fp, indent=1)
    for n, s in summ.items():
        print(f"== N_g = {n}: contrast reaches 1, 10, 100 at a_p = "
              + ", ".join(f"{v:.2f}" for v in s["rise"]))
        for k, v in s.items():
            if k.startswith("a10_"):
                dl = f"  delay {100*(v[0]/v[1] - 1):.2f} percent" if v[1] else ""
                print(f"   infall from {k[4:]}: relativistic {v[0]:.2f}"
                      + (f", Newtonian {v[1]:.2f}" if v[1] else "") + dl)
        if "Hr_mean_at_a" in s:
            print("   mean H_r at a = 2, 5, 10, 20, 40, 100: "
                  + " ".join(f"{v:.2e}" for v in s["Hr_mean_at_a"].values()))
        print("   rms H / largest term at a = 2, 5, 10, 20, 40: "
              + " ".join(f"{v:.2e}" for v in s["Hrms_rel_at_a"].values()))
    print(os.path.join(figdir, "east_res.png"))


if __name__ == "__main__":
    main()
