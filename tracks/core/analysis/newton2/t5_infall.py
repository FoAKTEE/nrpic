#!/usr/bin/env python3
"""Test T5 of work package newton2: secondary infall of Track D onto a fixed point mass
(<particles> newton_pm_mass) in the Newtonian mode.

    t5_infall.py --predict CASEDIR            closed form only (before the run)
    t5_infall.py --run RUNDIR_OF_cases.py_t5 [--out DIR]

Closed form: a dust particle that starts at the distance r0 from the seed with the
Hubble velocity eps r0 and has the mass M_enc = 1 + (dust inside r0) inside it moves on
a radial Kepler orbit until a shell crosses it; shells are crossed only after their
turnaround, so its turnaround time t_ta(r0) is exact, and the mass that has turned
around by the time t is M_ta(t) = 1 + sum of the dust masses with t_ta <= t (the
definition of Track D's nm_analyze.py: seed plus the dust that has had v_r < 0).
Measured: the same sum over the particles whose radial velocity about the seed has been
negative at a snapshot up to t.  Writes DIR/t5_infall.json and DIR/t5_infall.{png,pdf}.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402

from nrpic import io as nio  # noqa: E402
from nrpic import newton as nw  # noqa: E402


def kepler_tta(r_i, v_i, m, t_i):
    """Turnaround time of a bound radial Kepler orbit through (r_i, v_i > 0) at t_i."""
    energy = 0.5*v_i**2 - m/r_i
    r_max = m/(-energy)
    eta = np.arccos(np.clip(1.0 - 2.0*r_i/r_max, -1.0, 1.0))
    return t_i + np.sqrt(r_max**3/(8.0*m))*(np.pi - (eta - np.sin(eta)))


def closed_form(case):
    setup = json.load(open(os.path.join(case, "setup.json")))
    x, u, m, _ = nio.read_nrp(os.path.join(case, "dust.nrp"))
    inp = open(os.path.join(case, "input.athinput")).read() if \
        os.path.exists(os.path.join(case, "input.athinput")) else ""
    c = np.zeros(3)
    for line in inp.split("\n"):
        for d in range(3):
            if line.startswith("newton_pm_x%d" % (d + 1)):
                c[d] = float(line.split("=")[1].split("#")[0])
    r0 = np.sqrt(((x - c)**2).sum(axis=1))
    order = np.argsort(r0, kind="stable")
    rs, ms = r0[order], m[order]
    # mass inside r0: strictly inside, plus half of the particles at the same radius
    uniq, inv, cnt = np.unique(np.round(rs, 9), return_inverse=True, return_counts=True)
    mshell = np.bincount(inv, weights=ms)
    below = np.concatenate([[0.0], np.cumsum(mshell)[:-1]])
    menc = 1.0 + below[inv] + 0.5*mshell[inv]
    eps, t_i = setup["eps"], setup["t_i"]
    tta = np.full(len(m), np.inf)
    bound = 0.5*(eps*rs)**2 - menc/rs < 0.0
    tta[order[bound]] = kepler_tta(rs[bound], eps*rs[bound], menc[bound], t_i)
    return setup, c, m, tta


def mta_closed(setup, m, tta, a_over_ai):
    t = setup["t_i"]*np.asarray(a_over_ai, dtype=float)**1.5
    return np.array([1.0 + m[tta <= tt].sum() for tt in np.atleast_1d(t)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict", default="")
    ap.add_argument("--run", default="")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    if a.predict:
        setup, c, m, tta = closed_form(a.predict)
        print("dust particles %d, dust mass %.6f, seed at %s" % (len(m), m.sum(), c))
        for aa in (1.5, 2.0, 3.0, 4.0):
            print("a/a_i = %.1f  M_ta (closed form) = %.5f" % (aa, mta_closed(setup, m, tta,
                                                                              aa)[0]))
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.065, right=0.99, bottom=0.17, top=0.93, wspace=0.36)
    cols = {"pm_vertex": fs.PAL["red"], "pm_centre": fs.PAL["yellow"]}
    for name in ("pm_vertex", "pm_centre"):
        case = os.path.join(a.run, name)
        setup, c, m, tta = closed_form(case)
        t_i = setup["t_i"]
        turned = np.zeros(len(m), dtype=bool)
        rows = []
        for f in sorted(glob.glob(os.path.join(case, "*.part.*.bin"))):
            t, cyc, x, u, mm, tag = nw.read_snapshot(f)
            d = x - c
            r = np.sqrt((d*d).sum(axis=1))
            vr = (d*u).sum(axis=1)/np.maximum(r, 1e-300)
            turned[tag[vr < 0.0]] = True
            a_ai = ((t_i + t)/t_i)**(2.0/3.0)
            rows.append((t, a_ai, 1.0 + m[turned].sum(), mta_closed(setup, m, tta, a_ai)[0],
                         len(mm), float(r.min()), float(np.abs(u).max())))
        rows = np.array(rows)
        hst = nw.read_newton_hst(os.path.join(case, "infall.newton.hst"))
        late = rows[:, 1] >= 1.5
        dev = rows[:, 2]/rows[:, 3] - 1.0
        out = dict(n_dust=int(len(m)), dust_mass=float(m.sum()), seed=c.tolist(),
                   steps=int(hst["ncycle"][-1]) if "ncycle" in hst else int(len(hst["time"])),
                   particles_left=int(rows[-1, 4]),
                   max_dev_after_1p5=float(np.max(np.abs(dev[late]))),
                   snapshots=int(len(rows)), snapshots_after_1p5=int(late.sum()),
                   dev_min_after_1p5=float(dev[late].min()),
                   dev_max_after_1p5=float(dev[late].max()),
                   dev_rms_after_1p5=float(np.sqrt(np.mean(dev[late]**2))),
                   snapshots_exact_after_1p5=int((dev[late] == 0.0).sum()),
                   a_over_ai=rows[:, 1].tolist(), mta_run=rows[:, 2].tolist(),
                   mta_closed=rows[:, 3].tolist(),
                   energy_drift=float(np.max(np.abs(hst["C"] - hst["C"][0]))
                                      / np.max(np.abs(hst["W"]))),
                   momentum_max=float(max(np.max(np.abs(hst["P_%s" % k])) for k in "xyz")),
                   u_max=float(rows[:, 6].max()))
        for aa in (2.0, 3.0, 4.0):
            # interpolated between snapshots: the measured count lags the closed form by
            # up to one snapshot interval (a particle is seen to have turned around only
            # at the next snapshot)
            out["mta_run_a%g" % aa] = float(np.interp(aa, rows[:, 1], rows[:, 2]))
            out["mta_closed_a%g" % aa] = float(mta_closed(setup, m, tta, aa)[0])
            # without the lag: both at the snapshot nearest to a
            k = int(np.argmin(np.abs(rows[:, 1] - aa)))
            out["snap_a_near_%g" % aa] = float(rows[k, 1])
            out["mta_run_snap_near_%g" % aa] = float(rows[k, 2])
            out["mta_closed_snap_near_%g" % aa] = float(rows[k, 3])
            out["dev_snap_near_%g" % aa] = float(dev[k])
        res[name] = out
        ax = axs[0]
        ax.plot(rows[:, 1], rows[:, 2], color=cols[name], label=name.replace("pm_", "seed at a "))
        if name == "pm_vertex":
            ag = np.linspace(1.0, 4.0, 200)
            ax.plot(ag, mta_closed(setup, m, tta, ag), color=fs.PAL["blue"], ls="--",
                    label="closed form")
        ax = axs[1]
        ax.plot(rows[1:, 1], 1e2*dev[1:], color=cols[name])
        ax = axs[2]
        ax.plot(((t_i + hst["time"])/t_i)**(2.0/3.0),
                1e2*(hst["C"] - hst["C"][0])/np.max(np.abs(hst["W"])), color=cols[name])
    res["placements_rel_diff_a2"] = res["pm_vertex"]["mta_run_a2"]/res["pm_centre"]["mta_run_a2"] - 1
    res["placements_rel_diff_a4"] = res["pm_vertex"]["mta_run_a4"]/res["pm_centre"]["mta_run_a4"] - 1
    for aa in (2, 4):
        res["placements_rel_diff_snap_near_%d" % aa] = \
            res["pm_vertex"]["mta_run_snap_near_%d" % aa] \
            / res["pm_centre"]["mta_run_snap_near_%d" % aa] - 1
    axs[0].set_xlabel(r"$a/a_i$", labelpad=-1)
    axs[0].set_ylabel(r"$M_{\rm ta}/M$")
    axs[0].legend(loc="upper left", fontsize=8)
    axs[1].axhline(0.0, color="k", lw=1.0, ls="--")
    axs[1].set_xlabel(r"$a/a_i$", labelpad=-1)
    axs[1].set_ylabel(r"$M_{\rm ta}$: run/closed $-$ 1 (per cent)")
    axs[2].set_xlabel(r"$a/a_i$", labelpad=-1)
    axs[2].set_ylabel(r"$(K + W - E_0)/\max|W|$ (per cent)")
    fs.save(fig, os.path.join(a.out, "t5_infall"))
    with open(os.path.join(a.out, "t5_infall.json"), "w") as f:
        json.dump(res, f, indent=1)
    short = {k: ({kk: vv for kk, vv in v.items()
                  if kk not in ("a_over_ai", "mta_run", "mta_closed")}
                 if isinstance(v, dict) else v) for k, v in res.items()}
    print(json.dumps(short, indent=1))


if __name__ == "__main__":
    main()
