#!/usr/bin/env python3
"""Test T12 of tracks/core/JOURNAL-scalar2.md: Track E's criterion A4 in its own form
(the constraint ratios of the record when the amplitude is halved) at N = 32 and 64, and
test T8 at N = 64.

    python3 t12_halving.py --exe EXE [--out DIR] [--n 64] [--tlim 3.2] [--workers 5]
                           [--analyse-only [--data DIR0]] [--ref32 DIR32 --ref32-s0 DIR32S0]
                           [--t8-ref32 DIRT8]

Runs problems/scalar/sr_stochastic.athinput at N^3 (nmax2 = 64, dumps every 0.4 with the
metric and the constraint fields) with the mode functions scaled by s = 1, -1, 1/2,
-1/2 and 0 (runs p1, m1, p05, m05, s0).  The 32^3 runs exist already: DIR32 is the
output of t23_evolve.py (bg025 = s 1, m1, p05, m05), DIR32S0/p0 that of t3b_parts.py
(s = 0); DIRT8 that of t8_rnr.py at N = 32 (summary.json).

From the records (<basename>.sf.con.hst, every cycle):
  F_H = <|H|/[H]>(s = 1) / <|H|/[H]>(s = 1/2),  F_M the same for <|M|/[M]>.
[H] is dominated by the background (about 12), [M] is first order in s, so a
second-order H gives F_H = 4 and a second-order M gives F_M = 2; first order gives 2
and 1; an amplitude-independent part gives 1 (H only).
From the dumps at equal times:
  H0 = H(s = 0) (time integration of the background), O(s) = [C(s) - C(-s)]/2 (first
  order), C2(s) = [C(s) + C(-s)]/2 - H0 (second order), and G_H = rms(H(1) - H0) /
  rms(H(1/2) - H0), G_M = rms|M(1)| / rms|M(1/2)| (4 for second order, 2 for first).
T8 at N = 64: R^NR_n of the run p1 against W R alpha_n of its record (t8_rnr.py).
Writes DIR/summary.json and DIR/fig_halving.png."""
import argparse
import glob
import json
import os

import common
from common import np
from nrpic import scalar_field as sf
import t8_rnr

INP = os.path.join(common.PROB, "sr_stochastic.athinput")
MODES = os.path.join(common.PROB, "sr_stochastic_modes.txt")
SCALES = (("p1", 1.0), ("m1", -1.0), ("p05", 0.5), ("m05", -0.5), ("s0", 0.0))
NAMES32 = {"p1": "bg025", "m1": "m1", "p05": "p05", "m05": "m05"}


def dumps(rundir, tmax):
    """Dumps of a run keyed by cycle, up to time tmax (the short runs cut their last step
    at tlim, the long one does not)."""
    out = {}
    for f in sorted(glob.glob(os.path.join(rundir, "sr.sf.?????.dump"))):
        d = sf.read_dump(f)
        if d["time"] <= tmax + 1e-9:
            out[int(d["cycle"])] = d
    return out


def rms(x):
    return float(np.sqrt((x*x).mean()))


def mvec(f):
    return np.stack([f["Mx"], f["My"], f["Mz"]])


def mnorm(v):
    return np.sqrt((v*v).sum(axis=0))


def factors(dirs, tmax):
    """F_H, F_M per cycle from the records of the runs s = 1 and s = 1/2."""
    c1 = sf.read_con_history(os.path.join(dirs["p1"], "sr.sf.con.hst"))
    c5 = sf.read_con_history(os.path.join(dirs["p05"], "sr.sf.con.hst"))
    cyc = np.intersect1d(c1["cycle"], c5["cycle"])
    i1 = np.searchsorted(c1["cycle"], cyc)
    i5 = np.searchsorted(c5["cycle"], cyc)
    keep = (np.abs(c1["time"][i1] - c5["time"][i5]) < 1e-9) & (c1["time"][i1] <= tmax
                                                                + 1e-9)
    i1, i5 = i1[keep], i5[keep]
    return dict(time=c1["time"][i1], efolds=c1["efolds"][i1],
                H1=c1["H_ratio"][i1], H05=c5["H_ratio"][i5],
                M1=c1["M_ratio"][i1], M05=c5["M_ratio"][i5],
                F_H=c1["H_ratio"][i1]/c5["H_ratio"][i5],
                F_M=c1["M_ratio"][i1]/c5["M_ratio"][i5])


def parts(dirs, tmax):
    dd = {k: dumps(v, tmax) for k, v in dirs.items()}
    rows = []
    for c in sorted(dd["s0"]):
        if any(c not in dd[k] for k in dd):
            continue
        t = [dd[k][c]["time"] for k in dd]
        if max(t) - min(t) > 1e-9:
            continue
        f = {k: dd[k][c]["fields"] for k in dd}
        h0 = f["s0"]["H"]
        row = dict(time=float(t[0]), cycle=c,
                   efolds=float(-0.5*np.log(f["p1"]["chi"].mean())),
                   H0_mean=float(h0.mean()), H0_std=float(h0.std()),
                   M0_rms=rms(mnorm(mvec(f["s0"]))))
        for tag, sp, sm in (("1", "p1", "m1"), ("05", "p05", "m05")):
            hp, hm = f[sp]["H"], f[sm]["H"]
            mp, mm = mvec(f[sp]), mvec(f[sm])
            row["H_odd_" + tag] = rms(0.5*(hp - hm))
            row["H_c2_" + tag] = rms(0.5*(hp + hm) - h0)
            row["H_c2_mean_" + tag] = float((0.5*(hp + hm) - h0).mean())
            row["H_minus_H0_" + tag] = rms(hp - h0)
            row["M_odd_" + tag] = rms(mnorm(0.5*(mp - mm)))
            row["M_even_" + tag] = rms(mnorm(0.5*(mp + mm)))
            row["M_" + tag] = rms(mnorm(mp))
        for key in ("H_odd", "H_c2", "M_odd", "M_even"):
            row[key + "_ratio"] = row[key + "_1"]/row[key + "_05"]
        row["G_H"] = row["H_minus_H0_1"]/row["H_minus_H0_05"]
        row["G_M"] = row["M_1"]/row["M_05"]
        rows.append(row)
    return rows


def rnr_complex(rundir, n, n2, al, length):
    """R^NR_n and the linear reference L^(-3/2) W R alpha_n per dump, complex (the
    extraction of t8_rnr.analyse, keyed by cycle)."""
    out = {}
    for f in sorted(glob.glob(os.path.join(rundir, "sr.sf.?????.dump"))):
        d = sf.read_dump(f)
        fl = d["fields"]
        head, tab = sf.read_modes(f.replace(".dump", ".modes"))
        chib = fl["chi"].mean()
        hub = -fl["K"].mean()/3.0
        pib = fl["Pi"].mean()
        psi, _ = sf.analyse(0.5*(fl["chi"]/chib - 1.0), n)
        nn = n.astype(float)
        for name, i, j in t8_rnr.SYM:
            c, _ = sf.analyse(fl[name] - (1.0 if i == j else 0.0), n)
            psi = psi + 0.25*(1.0 if i == j else 2.0)*nn[:, i]*nn[:, j]*c/n2
        dphi, _ = sf.analyse(fl["phi"] - fl["phi"].mean(), n)
        sh = tab[:, 0].astype(int)
        r = (tab[:, 1] + 1j*tab[:, 2])[np.searchsorted(sh, n2)]
        w, _ = t8_rnr.inf.window(n2, length, head["a"], head["H"], head["eps1"])
        out[int(d["cycle"])] = dict(time=float(d["time"]), efolds=float(np.log(head["a"])),
                                    q=np.sqrt(n2.astype(float)), w=w,
                                    rnr=psi + (hub/pib)*dphi, ref=length**-1.5*w*r*al)
    return out


def rows_of(dev_by_cycle, base):
    """Rows in the form t8_rnr.stats reads."""
    return [dict(time=base[c]["time"], cycle=c, efolds=base[c]["efolds"], q=base[c]["q"],
                 w=base[c]["w"], dev=dev) for c, dev in sorted(dev_by_cycle.items())]


def window_stats(fac, lo, hi):
    sel = (fac["efolds"] >= lo) & (fac["efolds"] <= hi)
    if not sel.any():
        return None
    return {k: [float(fac[k][sel].min()), float(fac[k][sel].max())] for k in ("F_H", "F_M")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"),
                    help="default: $NRPIC_RUN_DIR of nrpic-run (which runs the command "
                         "without a shell, so a literal $NRPIC_RUN_DIR is not expanded)")
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--tlim", type=float, default=3.2)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--data", help="with --analyse-only: directory of an earlier "
                    "execution at N (summary and figure go to --out)")
    ap.add_argument("--ref32", help="output of t23_evolve.py at N = 32")
    ap.add_argument("--ref32-s0", help="output of t3b_parts.py at N = 32 (run p0)")
    ap.add_argument("--t8-ref32", help="output of t8_rnr.py at N = 32")
    a = ap.parse_args()
    if not a.out or "$" in a.out:
        ap.error(f"--out missing or unexpanded: {a.out!r}")
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    args = [f"scalar_field/noise_mode_file={MODES}", f"time/tlim={a.tlim}",
            "scalar_field/dump_dt=0.4", "scalar_field/dump_noise=false"
            ] + common.mesh_args(a.n)
    summ = dict(exe=os.path.abspath(a.exe), n=a.n)
    if not a.analyse_only:
        cases = [(os.path.join(out, k), INP, args + [f"scalar_field/noise_mode_scale={s}"])
                 for k, s in SCALES]
        summ["wall_s"] = dict(zip([k for k, _ in SCALES],
                                  common.run_many(os.path.abspath(a.exe), cases,
                                                  a.workers)))
    data = os.path.abspath(a.data) if (a.analyse_only and a.data) else out
    summ["data"] = data
    sets = {a.n: {k: os.path.join(data, k) for k, _ in SCALES}}
    if a.ref32 and a.ref32_s0:
        d32 = {k: os.path.join(os.path.abspath(a.ref32), v) for k, v in NAMES32.items()}
        d32["s0"] = os.path.join(os.path.abspath(a.ref32_s0), "p0")
        sets[32] = d32
    fac, prt = {}, {}
    for n, dirs in sorted(sets.items()):
        fac[n] = factors(dirs, a.tlim)
        prt[n] = parts(dirs, a.tlim)
        summ[f"N{n}"] = dict(
            factors_at_t0=dict(F_H=float(fac[n]["F_H"][0]), F_M=float(fac[n]["F_M"][0])),
            factors_efolds_0p15_0p3=window_stats(fac[n], 0.15, 0.3),
            factors_efolds_0p3_1p2=window_stats(fac[n], 0.3, 1.2),
            factors_efolds_0p3_1p6=window_stats(fac[n], 0.3, 1.6),
            max_F_H=[float(fac[n]["F_H"].max()),
                     float(fac[n]["efolds"][int(np.argmax(fac[n]["F_H"]))])],
            min_F_H=[float(fac[n]["F_H"].min()),
                     float(fac[n]["efolds"][int(np.argmin(fac[n]["F_H"]))])],
            factors_efolds_2p4_3p2=window_stats(fac[n], 2.4, 3.2),
            max_H_ratio_s1=float(fac[n]["H1"].max()),
            max_M_ratio_s1=float(fac[n]["M1"].max()),
            parts=prt[n])
    # T8 at N = n on the run p1
    nn, n2 = sf.mode_set(t8_rnr.NMAX2)
    al = sf.mode_alpha(t8_rnr.SEED, 0, 0, nn)
    rows8 = t8_rnr.analyse(sets[a.n]["p1"], nn, n2, al, 2.0*np.pi)
    summ["t8"] = t8_rnr.stats(rows8)
    # T12b: the part of R^NR odd in s (first order) and the run s = 1/2 alone
    cx = {k: rnr_complex(sets[a.n][k], nn, n2, al, 2.0*np.pi) for k in ("p1", "m1", "p05")}
    odd = {c: np.abs(0.5*(cx["p1"][c]["rnr"] - cx["m1"][c]["rnr"])/cx["p1"][c]["ref"] - 1.0)
           for c in cx["p1"] if c in cx["m1"]}
    half = {c: np.abs(cx["p05"][c]["rnr"]/cx["p05"][c]["ref"] - 1.0) for c in cx["p05"]}
    summ["t8_odd"] = t8_rnr.stats(rows_of(odd, cx["p1"]))
    summ["t8_half"] = t8_rnr.stats(rows_of(half, cx["p05"]))
    t8ref = None
    if a.t8_ref32:
        t8ref = json.load(open(os.path.join(os.path.abspath(a.t8_ref32),
                                            "summary.json")))["run"]
        summ["t8_ref32"] = t8ref
    common.dump_json(summ, os.path.join(out, "summary.json"))

    fs = common.style()
    import matplotlib.pyplot as plt
    col = {32: fs.PAL["red"], 64: fs.PAL["green"], 128: fs.PAL["blue"]}
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.07, top=0.915, wspace=0.25,
                        hspace=0.24)

    def guides(p, marks, ymax):
        for v, txt in marks:
            p.axhline(v, **fs.MASK_LINE)
            p.text(3.15, v + 0.04*ymax, txt, ha="right", va="bottom", fontsize=7,
                   color="grey")
        p.set_ylim(0.0, ymax)
        p.set_xlim(-0.1, 3.25)
    p = ax[0, 0]
    for n in sorted(fac):
        p.plot(fac[n]["efolds"], fac[n]["F_H"], color=col[n], label=f"$N={n}$, record")
        p.plot([r["efolds"] for r in prt[n]], [r["G_H"] for r in prt[n]], "o", ms=3.5,
               mfc="none", color=col[n], label=f"$N={n}$, $H-H_0$, dumps")
    top = max(4.6, 1.1*max(float(np.max(fac[n]["F_H"])) for n in fac))
    guides(p, ((4.0, "second order"), (2.0, "first order"), (1.0, "independent of $s$")),
           top)
    p.set_xlabel("e-folds after $N_*$", labelpad=1)
    p.set_ylabel(r"$\langle|H|/[H]\rangle_{s=1}\,/\,\langle|H|/[H]\rangle_{s=1/2}$")
    p.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=7, ncol=2)
    p = ax[0, 1]
    for n in sorted(fac):
        p.plot(fac[n]["efolds"], fac[n]["F_M"], color=col[n], label=f"$N={n}$, record")
        p.plot([r["efolds"] for r in prt[n]], [r["G_M"] for r in prt[n]], "s", ms=3.5,
               mfc="none", color=col[n], label=f"$N={n}$, rms $|M|$, dumps")
    guides(p, ((4.0, "rms $|M|$: second order"), (2.0, "record: second order"),
               (1.0, "record: first order")), 4.6)
    p.set_xlabel("e-folds after $N_*$", labelpad=1)
    p.set_ylabel(r"$\langle|M|/[M]\rangle_{s=1}\,/\,\langle|M|/[M]\rangle_{s=1/2}$")
    p.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=7, ncol=2)
    p = ax[1, 0]
    for n in sorted(prt):
        e = [r["efolds"] for r in prt[n]]
        ls = "-" if n == a.n else "--"
        p.plot(e, [abs(r["H0_mean"]) for r in prt[n]], ls, marker="^", ms=3.5,
               color=col[n], label=f"$|H_0|$, $N={n}$")
        p.plot(e, [r["H_c2_1"] for r in prt[n]], ls, marker="o", ms=3.5, color=col[n],
               mfc="white", label=f"second order, $N={n}$")
        p.plot(e, [r["H_odd_1"] for r in prt[n]], ls, marker="s", ms=3.5, color=col[n],
               mfc="none", label=f"first order, $N={n}$")
    p.set_yscale("log")
    p.set_xlabel("e-folds after $N_*$", labelpad=1)
    p.set_ylabel("rms of the parts of $H$ at $s=1$")
    p.legend(loc="lower right", fontsize=7, ncol=2)
    p = ax[1, 1]
    for lab, mk, lbl in (("n_le_2", "o", r"$|n|\leq2$"), ("n_le_4", "s", r"$|n|\leq4$"),
                         ("all_in", "^", "all with $W>1/2$")):
        r8 = [s for s in summ["t8"] if s["time"] > 0 and s[lab]["max_dev"] is not None]
        p.plot([s["efolds"] for s in r8], [s[lab]["max_dev"] for s in r8], "-",
               marker=mk, ms=3.5, color=col[a.n], label=f"{lbl}, $N={a.n}$")
        if t8ref:
            r3 = [s for s in t8ref if s["time"] > 0 and s[lab]["max_dev"] is not None]
            p.plot([s["efolds"] for s in r3], [s[lab]["max_dev"] for s in r3], "--",
                   marker=mk, ms=3.5, mfc="none", color=col[32], label=f"{lbl}, $N=32$")
    for key, mk, lbl in (("t8_odd", "D", r"$|n|\leq2$, odd in $s$"),
                         ("t8_half", "x", r"$|n|\leq2$, $s=1/2$")):
        r = [s for s in summ[key] if s["time"] > 0 and s["n_le_2"]["max_dev"] is not None]
        p.plot([s["efolds"] for s in r], [s["n_le_2"]["max_dev"] for s in r], ":",
               marker=mk, ms=3.5, mfc="none", color=fs.PAL["blue"],
               label=f"{lbl}, $N={a.n}$")
    p.axhline(2e-2, **fs.MASK_LINE)
    p.set_yscale("log")
    p.set_xlabel("e-folds after $N_*$", labelpad=1)
    p.set_ylabel(r"largest $|R^{\rm NR}_n/(W R\,\alpha_n)-1|$")
    p.legend(loc="upper left", fontsize=7, ncol=2)
    fig.savefig(os.path.join(out, "fig_halving.png"), dpi=200)
    print("T12 done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
