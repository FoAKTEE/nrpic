#!/usr/bin/env python3
"""Test T8 of tracks/core/JOURNAL-scalar2.md: the curvature perturbation extracted from
the dumps against the coarse-grained linear solution W R alpha of the lockstep record.

    python3 t8_rnr.py --exe EXE --out DIR [--n 32] [--tlim 3.2] [--analyse-only]

Runs problems/scalar/sr_stochastic.athinput (nmax2 = 64) with the metric in the dumps
(every 0.4), once as it is and once with noise_pi_sign = -1.  For every dump:
  psi_n = (a^2 chi_n - 1)/2 + (1/4) n_i n_j (gt_ij - delta_ij)_n / n^2
  R^NR_n = psi_n + (H/Pi_b) delta phi_n,   H = -<K>/3,  Pi_b = <Pi>,  a^2 = 1/<chi>
against L^(-3/2) W(t) R(t) alpha_n, R(t) of <basename>.sf.NNNNN.modes.
Writes DIR/summary.json and DIR/fig_rnr.png."""
import argparse
import glob
import os

import common
from common import inf, np
from nrpic import scalar_field as sf

INP = os.path.join(common.PROB, "sr_stochastic.athinput")
MODES = os.path.join(common.PROB, "sr_stochastic_modes.txt")
SEED = 20261115
NMAX2 = 64
SYM = (("gxx", 0, 0), ("gxy", 0, 1), ("gxz", 0, 2), ("gyy", 1, 1), ("gyz", 1, 2),
       ("gzz", 2, 2))


def analyse(rundir, n, n2, al, length, windowed=True):
    rows = []
    for f in sorted(glob.glob(os.path.join(rundir, "sr.sf.?????.dump"))):
        d = sf.read_dump(f)
        fl = d["fields"]
        head, tab = sf.read_modes(f.replace(".dump", ".modes"))
        chib = fl["chi"].mean()
        hub = -fl["K"].mean()/3.0
        pib = fl["Pi"].mean()
        psi, _ = sf.analyse(0.5*(fl["chi"]/chib - 1.0), n)
        nn = n.astype(float)
        for name, i, j in SYM:
            c, _ = sf.analyse(fl[name] - (1.0 if i == j else 0.0), n)
            psi = psi + 0.25*(1.0 if i == j else 2.0)*nn[:, i]*nn[:, j]*c/n2
        dphi, _ = sf.analyse(fl["phi"] - fl["phi"].mean(), n)
        rnr = psi + (hub/pib)*dphi
        # linear solution of the lockstep record: shells in the order of the record
        sh = tab[:, 0].astype(int)
        idx = np.searchsorted(sh, n2)
        r = (tab[:, 1] + 1j*tab[:, 2])[idx]
        a = np.exp(head["ln_a"])
        w, _ = inf.window(n2, length, a, head["H"], head["eps1"])
        if not windowed:      # all modes in from the start, no sources
            w = np.ones(n2.size)
        ref = length**-1.5*w*r*al
        ratio = rnr/ref
        q = np.sqrt(n2.astype(float))
        row = dict(time=float(d["time"]), cycle=int(d["cycle"]), efolds=float(np.log(a)),
                   H=float(hub), q=q, w=w, dev=np.abs(ratio - 1.0), rnr=np.abs(rnr),
                   ref=np.abs(ref))
        rows.append(row)
    return rows


def stats(rows):
    out = []
    for r in rows:
        ent = r["w"] > 0.5
        s = dict(time=r["time"], cycle=r["cycle"], efolds=r["efolds"],
                 modes_in=int(ent.sum()))
        for lab, sel in (("n_le_2", ent & (r["q"] <= 2.0 + 1e-9)),
                         ("n_le_4", ent & (r["q"] <= 4.0 + 1e-9)),
                         ("all_in", ent), ("w_gt_1e-3", r["w"] > 1e-3)):
            s[lab] = dict(count=int(sel.sum()),
                          max_dev=float(r["dev"][sel].max()) if sel.any() else None,
                          rms_dev=float(np.sqrt((r["dev"][sel]**2).mean()))
                          if sel.any() else None)
        out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--tlim", type=float, default=3.2)
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--no-control", action="store_true")
    ap.add_argument("--nmax2", type=int, default=NMAX2)
    ap.add_argument("--no-window", action="store_true",
                    help="slice_window = false and the three kicks off: the initial-value "
                         "problem without sources; reference R alpha of the record")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    args = [f"scalar_field/noise_mode_file={MODES}", f"time/tlim={a.tlim}",
            "scalar_field/dump_dt=0.4", "scalar_field/dump_noise=false",
            "scalar_field/dump_constraints=false",
            f"scalar_field/noise_nmax2={a.nmax2}"] + common.mesh_args(a.n)
    if a.no_window:
        args += ["problem/slice_window=false", "scalar_field/noise_kick_pi=false",
                 "scalar_field/noise_kick_k=false", "scalar_field/noise_kick_a=false"]
    summ = dict(exe=os.path.abspath(a.exe), n=a.n)
    if not a.analyse_only:
        cases = [(os.path.join(out, "run"), INP, args)]
        if not a.no_control:
            cases.append((os.path.join(out, "ctl"), INP,
                          args + ["scalar_field/noise_pi_sign=-1.0"]))
        summ["wall_s"] = common.run_many(os.path.abspath(a.exe), cases, 2)
    n, n2 = sf.mode_set(a.nmax2)
    al = sf.mode_alpha(SEED, 0, 0, n)
    length = 2.0*np.pi
    wd = not a.no_window
    rows = analyse(os.path.join(out, "run"), n, n2, al, length, wd)
    ctl = [] if a.no_control else analyse(os.path.join(out, "ctl"), n, n2, al, length, wd)
    summ["run"] = stats(rows)
    summ["control"] = stats(ctl)
    common.dump_json(summ, os.path.join(out, "summary.json"))

    fs = common.style()
    import matplotlib.pyplot as plt
    from matplotlib import cm
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.14, top=0.96, wspace=0.26)
    cols = cm.viridis(np.linspace(0.0, 0.9, len(rows)))
    for r, cl in zip(rows, cols):
        sel = r["w"] > 0.5
        ax[0].plot(r["q"][sel], r["dev"][sel], ".", ms=2.5, color=cl,
                   label=f"$N={r['efolds']:.1f}$")
    ax[0].axhline(2e-2, **fs.MASK_LINE)
    ax[0].set_yscale("log")
    ax[0].set_xlabel(r"$|n|$", labelpad=-2)
    ax[0].set_ylabel(r"$|R^{\rm NR}_n/(W R\,\alpha_n)-1|$, modes with $W>1/2$")
    ax[0].legend(loc="lower right", fontsize=6.5, ncol=3)
    en = [s["efolds"] for s in summ["run"]]
    for lab, cl, lbl in (("n_le_2", fs.PAL["blue"], r"$|n|\leq2$"),
                         ("n_le_4", fs.PAL["green"], r"$|n|\leq4$"),
                         ("all_in", fs.PAL["orange"], "all with $W>1/2$")):
        ax[1].plot(en, [s[lab]["max_dev"] for s in summ["run"]], "o-", ms=3, color=cl,
                   label=lbl)
        ax[1].plot([s["efolds"] for s in summ["control"]],
                   [s[lab]["max_dev"] for s in summ["control"]], "s--", ms=3, mfc="none",
                   color=cl)
    ax[1].axhline(2e-2, **fs.MASK_LINE)
    ax[1].set_yscale("log")
    ax[1].set_xlabel("e-folds after $N_*$")
    ax[1].set_ylabel("largest deviation (dashed: control)")
    ax[1].legend(loc="lower right", fontsize=8)
    fig.savefig(os.path.join(out, "fig_rnr.png"), dpi=200)
    print("T8 done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
