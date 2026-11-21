#!/usr/bin/env python3
"""Step 2 of package a4res (Track E): predictions of the first-order (odd) parts of H and
|M| from core's linear twin, before the card runs.

    python3 twin_predict.py --out DIR [--skip-cross] [--exact]

1. Extracts the twin (python/nrpic/{__init__,rng,scalar_field,sf_lattice}.py of branch
   core/scalar-3) with git show into DIR/twin/nrpic and imports it from there.
2. Cross-check on existing data (not an anchor: another mode file): CodeTwin at the steps
   of the ladder's runs L32, L64, L128 (nmax2 = 64, modes_n64.txt) and Q64 (nmax2 = 256,
   modes_n256.txt) against their measured odd parts (../../ladder/results/final/
   pair_*.json, absolute rms = relative x <[H]> or <[M]>).
3. Prediction for the six set-ups of a4lib.SETUPS (modes_n4096.txt): the CodeTwin (rk4
   stages at the predicted steps dt = 0.25 h, last step shortened to tlim) and the Twin
   (exact time, only with --exact: DOP853 at rtol 1e-11 takes about 30 s per 0.25 of
   time per set-up) at the predicted dump cycles; the floor model of the ladder; the even-part
   model (a4lib.EvenModel, [JUDGEMENT]); the predicted ratio odd/even and its maximum.
Writes DIR/prediction.json, DIR/cross.json, DIR/fig_prediction.png."""
import argparse
import os
import time

import numpy as np

import a4lib as A

LL = A.LL


def crosscheck(sl, sf):
    """CodeTwin against the ladder's measured odd parts."""
    import json
    cases = [("L32p_L32m", 32, 64, "modes_n64.txt"), ("L64p_L64m", 64, 64, "modes_n64.txt"),
             ("L128p_L128m", 128, 64, "modes_n64.txt"),
             ("Q64p_Q64m", 64, 256, "modes_n256.txt")]
    out = {}
    for name, nroot, nmax2, mf in cases:
        pj = json.load(open(os.path.join(A.TRACK, "ladder", "results", "final",
                                         f"pair_{name}.json")))
        rows = pj["rows"]
        hist = np.loadtxt(os.path.join(pj["run_p"], "sr.sf.hst"))
        times = hist[:, 0]
        cyc = [r["cycle"] for r in rows if r["cycle"] < times.size]
        ts = A.TwinSetup(sl, sf, dict(name=name, N=nroot, nmax2=nmax2),
                         modefile=os.path.join(A.TRACK, "ladder", "inputs", mf))
        t0 = time.time()
        tw = ts.code_twin(times, cyc)
        res = []
        for r in rows:
            m = [x for x in tw if x["cycle"] == r["cycle"]]
            if not m or r["cycle"] == 0:
                continue
            m = m[0]
            hm, mm = r["H_odd"]*r["Hmag"], r["M_odd"]*r["Mmag"]
            res.append(dict(time=r["time"], cycle=r["cycle"], H_meas=hm, H_twin=m["H"],
                            H_ratio=m["H"]/hm, M_meas=mm, M_twin=m["M"],
                            M_ratio=m["M"]/mm))
        out[name] = dict(N=nroot, nmax2=nmax2, modefile=mf, wall_s=round(time.time() - t0, 1),
                         alpha_core_maxdiff=ts.alpha_core_maxdiff, rows=res)
        print(f"cross {name}: " + " ".join(f"{x['time']:.2f}:{x['H_ratio']:.3f}"
                                            for x in res))
    return out


def predict_setup(sl, sf, s, even, floor, exact=False):
    nroot, K = s["N"], np.sqrt(s["nmax2"])
    times = A.step_times(nroot)
    cyc = A.dump_cycles(times)
    ts = A.TwinSetup(sl, sf, s)
    t0 = time.time()
    ct = ts.code_twin(times, cyc)
    tw = ts.twin(times[cyc]) if exact else [dict(H=None, M=None)]*len(ct)
    rows = []
    for a, b in zip(ct, tw):
        t = a["time"]
        hmag = float(even.Hmag(t))
        fh = float(floor.rel("H_odd", nroot, t))*hmag
        # [M] of the ladder's L64 is not the [M] of these set-ups; the floor of M is used
        # in absolute units relative to the even model of M at the same time instead
        eh, em = float(even.H(t, K)), float(even.M(t, K))
        oh = float(np.hypot(a["H"], fh))
        w = float(A.window(a["efolds"], a["hubble"], K))
        rows.append(dict(cycle=a["cycle"], time=t, efolds=a["efolds"], W_top=w,
                         H_codetwin=a["H"], M_codetwin=a["M"], H_twin=b["H"], M_twin=b["M"],
                         H_floor=fh, H_even_model=eh, M_even_model=em,
                         H_odd_pred=oh, ratio_H_pred=oh/eh, ratio_M_pred=a["M"]/em,
                         ratio_H_twin_only=a["H"]/eh))
    ent = [r for r in rows if r["time"] > 0]
    entw = []
    for r in ent:
        entw.append(r)
        if r["W_top"] >= 0.999:
            break
    best = max(ent, key=lambda r: r["ratio_H_pred"])
    bestm = max(ent, key=lambda r: r["ratio_M_pred"])
    summ = dict(name=s["name"], N=nroot, nmax2=s["nmax2"], cells=A.cells(s),
                modes=int(ts.n.shape[0]), classes=int(ts.nc.shape[0]),
                alpha_core_maxdiff=ts.alpha_core_maxdiff, steps=int(times.size - 1),
                dumps=len(cyc), wall_s=round(time.time() - t0, 1),
                max_ratio_H_pred=best["ratio_H_pred"], t_max_ratio_H=best["time"],
                max_ratio_M_pred=bestm["ratio_M_pred"], t_max_ratio_M=bestm["time"],
                max_ratio_H_pred_entry=max(r["ratio_H_pred"] for r in entw),
                t_entry_end=entw[-1]["time"],
                strict_A4_pred="holds" if max(best["ratio_H_pred"],
                                              bestm["ratio_M_pred"]) < 1 else "fails",
                rows=rows)
    print(f"{s['name']:9s} cells {A.cells(s):5.2f}: max odd/even H {best['ratio_H_pred']:.3g} "
          f"at t = {best['time']:.3f}, M {bestm['ratio_M_pred']:.3g} at {bestm['time']:.3f}; "
          f"classes {ts.nc.shape[0]}, wall {summ['wall_s']} s")
    return summ


def crossing(cells, ratio):
    """Cells at which a log-log interpolation of ratio(cells) passes 1 (None if not)."""
    c, r = np.log(np.asarray(cells)), np.log(np.asarray(ratio))
    o = np.argsort(c)
    c, r = c[o], r[o]
    for i in range(len(c) - 1):
        if (r[i] - 0.0)*(r[i+1] - 0.0) <= 0 and r[i] != r[i+1]:
            return float(np.exp(c[i] + (0.0 - r[i])*(c[i+1] - c[i])/(r[i+1] - r[i])))
    return None


def figure(pred, cross, out):
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.8))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.96, wspace=0.28,
                        hspace=0.3)
    cols = fs.series_colors(len(pred["setups"]))
    for s, c in zip(pred["setups"], cols):
        t = [r["time"] for r in s["rows"]]
        lab = f"$N={s['N']}$, $n^2_{{\\max}}={s['nmax2']}$ ({s['cells']:.1f})"
        ax[0, 0].plot(t, [r["H_codetwin"] for r in s["rows"]], "-", color=c, label=lab)
        ax[0, 0].plot(t, [r["H_even_model"] for r in s["rows"]], ":", color=c)
        ax[0, 1].plot(t, [r["ratio_H_pred"] for r in s["rows"]], "-", color=c, label=lab)
        ax[0, 1].plot(t, [r["ratio_M_pred"] for r in s["rows"]], "--", color=c, lw=1)
    ax[0, 0].set_yscale("log")
    ax[0, 0].set_ylim(1e-16, 1e-10)
    ax[0, 0].set_xlabel("$t$")
    ax[0, 0].set_ylabel(r"rms of $\mathcal{H}$: odd (twin, solid), even (model, dotted)")
    ax[0, 0].legend(fontsize=5.5, loc="lower left")
    ax[0, 1].axhline(1.0, **fs.MASK_LINE)
    ax[0, 1].set_yscale("log")
    ax[0, 1].set_xlabel("$t$")
    ax[0, 1].set_ylabel(r"predicted odd/even ($\mathcal{H}$ solid, $|\mathcal{M}|$ dashed)")
    # ratio max against cells
    cc = sorted(A.CORE_SCAN)
    ax[1, 0].plot(cc, [A.CORE_SCAN[c] for c in cc], "o-", mfc="none", color=fs.PAL["blue"],
                  label="core's scan ($n^2_{\\max}=64$, $N$ varied)")
    for nroot, mk in ((64, "s"), (128, "D")):
        ss = [s for s in pred["setups"] if s["N"] == nroot]
        ax[1, 0].plot([s["cells"] for s in ss], [s["max_ratio_H_pred"] for s in ss], mk,
                      color=fs.PAL["red"], label=f"prediction, $N={nroot}$, $\\mathcal{{H}}$")
        ax[1, 0].plot([s["cells"] for s in ss], [s["max_ratio_M_pred"] for s in ss], mk,
                      color=fs.PAL["red"], mfc="none",
                      label=f"prediction, $N={nroot}$, $|\\mathcal{{M}}|$")
    ax[1, 0].axhline(1.0, **fs.MASK_LINE)
    ax[1, 0].axvspan(11.0, 14.5, color="grey", alpha=0.12, lw=0)
    ax[1, 0].set_xscale("log")
    ax[1, 0].set_yscale("log")
    ax[1, 0].set_xlabel("cells per shortest source wavelength")
    ax[1, 0].set_ylabel("largest odd/even in time")
    ax[1, 0].legend(fontsize=5.5, loc="lower left")
    for (name, d), c in zip(cross.items(), fs.series_colors(len(cross))):
        t = [r["time"] for r in d["rows"]]
        ax[1, 1].plot(t, [r["H_twin"] for r in d["rows"]], "-", color=c,
                      label=f"{name.split('_')[0]}: twin")
        ax[1, 1].plot(t, [r["H_meas"] for r in d["rows"]], "o", mfc="none", ms=4, color=c,
                      label=f"{name.split('_')[0]}: measured")
    ax[1, 1].set_yscale("log")
    ax[1, 1].set_xlabel("$t$")
    ax[1, 1].set_ylabel(r"odd part of $\mathcal{H}$, ladder runs (rms)")
    ax[1, 1].legend(fontsize=5.5, ncol=2, loc="lower left")
    for i, x in enumerate(ax.ravel()):
        x.set_title("(%s)" % "abcd"[i], loc="left", fontsize=8)
    fig.savefig(os.path.join(out, "fig_prediction.png"), dpi=200)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-cross", action="store_true")
    ap.add_argument("--exact", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    prov = A.extract_twin(os.path.join(a.out, "twin"))
    sl, sf = A.import_twin(os.path.join(a.out, "twin"))
    print("twin from", prov["branch"], prov["commit"], sl.__file__)
    cross = {} if a.skip_cross else crosscheck(sl, sf)
    A.jdump(dict(twin=prov, cases=cross), os.path.join(a.out, "cross.json"))
    even, floor = A.EvenModel(), A.FloorModel()
    setups = [predict_setup(sl, sf, s, even, floor, a.exact) for s in A.SETUPS]
    fam = {}
    for nroot in (64, 128):
        ss = [s for s in setups if s["N"] == nroot]
        fam[str(nroot)] = dict(
            crossing_H=crossing([s["cells"] for s in ss], [s["max_ratio_H_pred"] for s in ss]),
            crossing_M=crossing([s["cells"] for s in ss], [s["max_ratio_M_pred"] for s in ss]))
    pred = dict(twin=prov, tlim=A.TLIM, dump_dt=A.DUMP_DT, cfl=A.CFL,
                modefile=os.path.relpath(A.MODE_FILE, A.REPO), families=fam,
                setups=setups, note="even part: a4lib.EvenModel [JUDGEMENT]; odd part "
                "predicted = hypot(CodeTwin, floor model)")
    A.jdump(pred, os.path.join(a.out, "prediction.json"))
    figure(pred, cross, a.out)
    print("families:", fam)


if __name__ == "__main__":
    main()
