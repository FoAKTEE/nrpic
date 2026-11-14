"""Effect of the cloud shape of the deposit on the runs of the single-wavelength problem
(cosmo/TESTLOG.md, T1a): constraint violation against the scale factor, observer density
contrast at the start, and collapse measures, for the linear, quadratic and cubic cloud.

    python3 shape_study.py [--runs runs/cosmo] [--n 64] [--deltas 0.0025,0.005,0.01,0.05]

Relativistic runs east_d<delta>_n<n>_{v2,tsc,pcs}; Newtonian runs newton_d<delta>_n<n>
(linear cloud) and newton_d<delta>_n<n>_{tsc,pcs}.
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

SHAPES = (("v2", "", "linear"), ("tsc", "_tsc", "quadratic"), ("pcs", "_pcs", "cubic"))


def cstat(rundir):
    f = os.path.join(rundir, "east.cstat.hst")
    if not os.path.exists(f):
        return None
    c = np.loadtxt(f)
    if c.ndim != 2:
        return None
    ok = np.isfinite(c).all(axis=1)
    n = len(ok) if ok.all() else int(np.argmin(ok))
    c = c[:n]
    return {"a": (1.0 + 0.5*c[:, 0])**2, "Hr_max": c[:, 10], "Hr_mean": c[:, 11],
            "Mr_max": c[:, 14], "Mr_mean": c[:, 15], "E_min": c[:, 5], "E_max": c[:, 6]}


def main():
    args = sys.argv[1:]
    opt = {args[i][2:]: args[i+1] for i in range(0, len(args) - 1, 2)}
    runs = opt.get("runs", os.path.join(REPO, "runs", "cosmo"))
    n = int(opt.get("n", "64"))
    deltas = [float(s) for s in opt.get("deltas", "0.0025,0.005,0.01,0.05").split(",")]
    fs.use_style()
    cols = {"v2": fs.PAL["red"], "tsc": fs.PAL["green"], "pcs": fs.PAL["blue"]}
    fig, axs = plt.subplots(2, len(deltas), figsize=(fs.FULL_WIDTH, 4.6), sharex="col",
                            sharey="row", squeeze=False)
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.11, top=0.93, wspace=0.08,
                        hspace=0.08)
    summ = {}
    for k, d in enumerate(deltas):
        s = summ.setdefault(f"{d:g}", {})
        for tag, nsuf, name in SHAPES:
            gdir = os.path.join(runs, f"east_d{d:g}_n{n}_{tag}")
            c = cstat(gdir)
            if c is not None:
                axs[0, k].loglog(c["a"][1:], c["Hr_mean"][1:], color=cols[tag], label=name)
                axs[1, k].loglog(c["a"][1:], c["Mr_mean"][1:], color=cols[tag])
                sel = c["a"] <= 4.0
                s.setdefault(tag, {}).update({
                    "Hr_mean_max_to_a4": float(c["Hr_mean"][sel].max()),
                    "Hr_max_max_to_a4": float(c["Hr_max"][sel].max()),
                    "Mr_mean_max_to_a4": float(c["Mr_mean"][sel].max()),
                    "Hr_mean_max": float(c["Hr_mean"].max()),
                    "Emin_over_Emax_min": float((c["E_min"]/c["E_max"]).min())})
            v = ec.load(runs, d, n, "_" + tag, nsuf)
            if v is None:
                continue
            g, nw, f = v["g"], v["nw"], v["f"]
            e = s.setdefault(tag, {})
            e["delta_obs_start_gr"] = [float(g["delta_obs_0"][0]), float(g["delta_obs_1"][0])]
            e["delta_obs_start_newton"] = [float(nw["delta_obs_0"][0]),
                                           float(nw["delta_obs_1"][0])]
            for lev in (1.0, 10.0, 100.0):
                ag = ec.rise(g["a_p_0"], g["delta_obs_0"], lev)
                an = ec.rise(nw["a_p_0"], nw["delta_obs_0"], lev)
                e[f"a_p_at_{lev:g}"] = [ag, an, ag/an]
            dg = ec.distances(f["x"], f["q"], f["axis"])
            apg = ec.a_of_tau(f["tau"])
            dn = ec.distances(np.mod(nw["x"], ec.L), nw["q_fid"], nw["axis_fid"])
            apn = ec.a_of_tau(nw["t_p"])
            for fr in ec.SHOWN:
                gg, nn = [], []
                for j in range(len(f["axis"])):
                    s0 = f["q"][j, f["axis"][j]] - ec.XPK
                    if abs(s0 - fr*ec.L) < 1e-9:
                        gg.append(ec.below(apg[:, j], dg[:, j], 0.1*dg[0, j]))
                        nn.append(ec.below(apn[:, j], dn[:, j], 0.1*dn[0, j]))
                if gg and np.isfinite(gg).all() and np.isfinite(nn).all():
                    e[f"a10_L/{1.0/fr:.0f}"] = [float(np.mean(gg)), float(np.mean(nn)),
                                                float(np.mean(gg)/np.mean(nn))]
            ok = np.isfinite(nw["delta_obs_1"])
            apn1 = nw["a_p_1"][ok]
            gi = np.interp(apn1, g["a_p_1"], g["delta_obs_1"])
            sel = apn1 <= g["a_p_1"][-1]
            e["underdensity_max_rel_diff"] = float(np.abs(
                (gi[sel] - nw["delta_obs_1"][ok][sel])/(1.0 + nw["delta_obs_1"][ok][sel])).max())
        axs[0, k].set_title(rf"$\bar\delta = {d:g}$", fontsize=8)
        axs[1, k].set_xlabel(r"scale factor $a$")
    axs[0, 0].set_ylabel(r"mean of $H_r$")
    axs[1, 0].set_ylabel(r"mean of $M_r$")
    axs[0, 0].legend(frameon=False, loc="lower right")
    figdir = os.path.join(HERE, "figs")
    fs.save(fig, os.path.join(figdir, "shape_study"))
    with open(os.path.join(HERE, "shape_study.json"), "w") as fp:
        json.dump(summ, fp, indent=1)
    lin = 3.0*(1.0 + 12.0/np.pi**2)
    for d, s in summ.items():
        print(f"== delta = {d}  (linear theory at a_p = 1: +-{lin*float(d):.6f})")
        for tag, _, name in SHAPES:
            e = s.get(tag)
            if not e:
                continue
            line = f"   {name:9s}"
            if "Hr_mean_max_to_a4" in e:
                line += (f" Hr mean/max to a=4: {e['Hr_mean_max_to_a4']:.1e}/"
                         f"{e['Hr_max_max_to_a4']:.1e}  Mr mean {e['Mr_mean_max_to_a4']:.1e}"
                         f"  Hr mean overall {e['Hr_mean_max']:.1e}  min E/E_max "
                         f"{e['Emin_over_Emax_min']:+.1e}")
            print(line)
            if "delta_obs_start_gr" in e:
                print(f"             delta_obs at start GR {e['delta_obs_start_gr'][0]:+.6f} "
                      f"{e['delta_obs_start_gr'][1]:+.6f}  N {e['delta_obs_start_newton'][0]:+.6f} "
                      f"{e['delta_obs_start_newton'][1]:+.6f}; underdensity largest density "
                      f"difference {e['underdensity_max_rel_diff']:.2e}")
                print("             overdensity a_p (GR, N, ratio): " + "  ".join(
                    f"{lev}: {e[f'a_p_at_{lev}'][0]:.2f} {e[f'a_p_at_{lev}'][1]:.2f} "
                    f"{e[f'a_p_at_{lev}'][2]:.4f}" for lev in ("1", "10", "100")))
                print("             distance below a tenth (GR, N, ratio): " + "  ".join(
                    f"{k[4:]}: {v[0]:.2f} {v[1]:.2f} {v[2]:.4f}"
                    for k, v in e.items() if k.startswith("a10_")))
    print(os.path.join(figdir, "shape_study.png"))


if __name__ == "__main__":
    main()
