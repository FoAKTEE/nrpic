#!/usr/bin/env python3
"""Predictions T (timing) and P256v6 (slow roll 256^3 on the release card build against the run
of the tested branch, G1 reservation 2) of g2prod/JOURNAL.md entry 1.

    python3 judge_tp.py --timing RUN_T --p-new RUN_P/P256 --p-old OLD/P256 \
        --judge-new NEW_judge.json --judge-old OLD_judge.json --npz-new NEW.npz --npz-old OLD.npz --out OUT

Writes OUT/judge_tp.json and OUT/fig/fig_g2_timing.png, fig_g2_p256v6.png.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "usr", "scripts"))
import figstyle as fs  # noqa: E402


def timing(rundir):
    out = {}
    for lab, n in (("T256", 256), ("T320", 320), ("T384", 384)):
        p = os.path.join(rundir, lab, "athena.log")
        d = dict(N=n)
        for line in open(p, errors="replace"):
            s = line.strip()
            if s.startswith("cpu time used"):
                d["cpu_s"] = float(s.split("=")[1])
            elif s.startswith("zone-cycles/cpu_second"):
                d["zcps"] = float(s.split("=")[1])
            elif s.startswith("# exit="):
                for w in s[1:].split():
                    if w.startswith("gpu_mem_peak_MiB="):
                        d["mem_MiB"] = float(w.split("=")[1])
        d["steps"] = d["zcps"] * d["cpu_s"] / n**3
        d["s_per_step"] = d["cpu_s"] / round(d["steps"])
        out[lab] = d
    pred = dict(T256=(1.15, 1.45), T320=(2.4, 2.8), T384=(4.0, 4.8))
    mem = dict(T256=(18.6e3, 20.6e3), T320=(36e3, 42e3), T384=(62e3, 70e3))
    for k in out:
        out[k]["pred_s"] = pred[k]
        out[k]["pred_mem_MiB"] = mem[k]
        out[k]["s_in_band"] = bool(pred[k][0] <= out[k]["s_per_step"] <= pred[k][1])
        out[k]["mem_in_band"] = bool(mem[k][0] <= out[k]["mem_MiB"] <= mem[k][1])
    out["refuted"] = bool(abs(out["T256"]["s_per_step"] - 1.30) > 0.2 or "mem_MiB" not in out["T384"])
    return out


def records(new, old, name):
    a = np.loadtxt(os.path.join(new, name))
    b = np.loadtxt(os.path.join(old, name))
    hdr = [l for l in open(os.path.join(old, name)) if l.startswith("# [1]")][0]
    cols = [c.split("=", 1)[1] for c in hdr[2:].split()]
    same_cycles = bool(a.shape == b.shape and np.array_equal(a[:, 1], b[:, 1]))
    res = dict(rows=int(a.shape[0]), same_cycles=same_cycles, columns={})
    if not same_cycles:
        return res, None, cols
    den = np.maximum(np.abs(b), 1e-300)
    rel = np.where((a == 0) & (b == 0), 0.0, np.abs(a - b) / den)
    for j, c in enumerate(cols):
        res["columns"][c] = dict(max_rel=float(rel[:, j].max()), row=int(np.argmax(rel[:, j])),
                                 t=float(b[np.argmax(rel[:, j]), 0]))
    res["max_rel_all"] = float(rel[:, 2:].max())
    return res, (a, b, rel), cols


def main():
    ap = argparse.ArgumentParser()
    for k in ("timing", "p-new", "p-old", "judge-new", "judge-old", "npz-new", "npz-old", "out"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "fig"), exist_ok=True)
    R = dict(T=timing(a.timing))
    jn, jo = json.load(open(a.judge_new)), json.load(open(a.judge_old))
    A2n, A2o = jn["A2"]["max_D_half"], jo["A2"]["max_D_half"]
    P = dict(A2_new=A2n, A2_old=A2o, A2_rel_change=abs(A2n / A2o - 1.0),
             A2_all_new=jn["A2"]["max_D_all"], A2_all_old=jo["A2"]["max_D_all"],
             N_f_new=jn["N_f"], N_f_old=jo["N_f"])
    zn, zo = np.load(a.npz_new), np.load(a.npz_old)
    rn, ro = zn["rnr"][-1], zo["rnr"][-1]
    n2 = zo["n2"]
    sel = n2 <= 1024
    rms = np.sqrt(np.mean(np.abs(ro[sel])**2))
    P["per_mode_max_abs_diff_over_rms_k_le_32"] = float(np.max(np.abs(rn[sel] - ro[sel])) / rms)
    P["per_mode_max_rel_diff_k_le_32"] = float(np.max(np.abs(rn[sel] / ro[sel] - 1.0)))
    hst, hst_arr, hcols = records(a.p_new, a.p_old, "sr.sf.hst")
    con, con_arr, ccols = records(a.p_new, a.p_old, "sr.sf.con.hst")
    P["hst"], P["con"] = hst, con
    if con_arr is not None:
        cn, co, _ = con_arr
        P["rec_max_H_new"], P["rec_max_H_old"] = float(cn[1:, 3].max()), float(co[1:, 3].max())
        P["rec_max_M_new"], P["rec_max_M_old"] = float(cn[1:, 6].max()), float(co[1:, 6].max())
        P["rec_H_rel_change"] = abs(P["rec_max_H_new"] / P["rec_max_H_old"] - 1.0)
        P["rec_M_rel_change"] = abs(P["rec_max_M_new"] / P["rec_max_M_old"] - 1.0)
    worst = max(hst.get("max_rel_all", np.inf), con.get("max_rel_all", np.inf))
    P["record_rows_max_rel"] = worst
    P["refuted_A2"] = bool(P["A2_rel_change"] > 0.01)
    P["refuted_records"] = bool(worst > 1e-8)
    P["held_A2_1pct"] = not P["refuted_A2"]
    P["held_records_1e-10"] = bool(worst <= 1e-10)
    R["P256v6"] = P
    with open(os.path.join(a.out, "judge_tp.json"), "w") as fp:
        json.dump(R, fp, indent=1)
    print(json.dumps(R, indent=1)[:4000])

    fs.use_style()
    import matplotlib.pyplot as plt
    cols = fs.series_colors(6)
    # ---- timing
    T = R["T"]
    N = np.array([T[k]["N"] for k in ("T256", "T320", "T384")], float)
    fig, ax = plt.subplots(1, 2, figsize=(fs.COLUMN_WIDTH * 2.0, 2.8))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.95, bottom=0.17, wspace=0.3)
    for j, (key, pk, lab) in enumerate((("s_per_step", "pred_s", "s per step"), ("mem_MiB", "pred_mem_MiB", "peak card memory [MiB]"))):
        y = np.array([T[k][key] for k in ("T256", "T320", "T384")])
        for x, k in zip(N, ("T256", "T320", "T384")):
            lo, hi = T[k][pk]
            ax[j].plot([x, x], [lo, hi], color="0.7", lw=6, solid_capstyle="butt")
        ax[j].plot(N, y, "o", color=cols[0], label="measured (run E-20261121-202929-43dcc9c)")
        ax[j].plot(N, y[0] * (N / 256.0)**3, ls="--", color=cols[2], lw=0.8, label=r"$\propto N^3$ from 256")
        ax[j].set_xlabel("N (cells per side)")
        ax[j].set_ylabel(lab)
    ax[1].axhline(81920, **fs.GUIDE)
    ax[0].legend(loc="upper left", fontsize=6)
    fs.save(fig, os.path.join(a.out, "fig", "fig_g2_timing"))
    plt.close(fig)
    # ---- P256v6
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.6))
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.09, hspace=0.35)
    if con_arr is not None:
        cn, co, rel = con_arr
        e = co[:, 2]
        for j, c in ((3, ccols[3]), (6, ccols[6]), (16, ccols[16]), (18, ccols[18])):
            ax[0].semilogy(e[1:], np.maximum(rel[1:, j], 1e-18), lw=0.8, label=c)
        ax[0].axhline(1e-8, **fs.GUIDE)
        ax[0].axhline(1e-10, color="0.6", lw=0.6, ls=":")
        ax[0].set_xlabel(r"$N-N_*$")
        ax[0].set_ylabel("|release - tested| / |tested|\n(con record, per row)")
        ax[0].legend(loc="lower right", fontsize=6)
    hn = np.array([[h["efolds"], h["max_D_in_half"]] for h in jn["A2_history"]])
    ho = np.array([[h["efolds"], h["max_D_in_half"]] for h in jo["A2_history"]])
    ax[1].semilogy(ho[1:, 0], ho[1:, 1], "o-", ms=3, color=cols[0], label="P256 tested branch (E-20261115-172618-f948386)")
    ax[1].semilogy(hn[1:, 0], hn[1:, 1], "x--", ms=4, color=cols[3], label="P256v6 release v0.6 (E-20261121-202935-31520bc)")
    ax[1].axhline(0.02, **fs.GUIDE)
    ax[1].set_xlabel(r"$N-N_*$")
    ax[1].set_ylabel(r"A2: max $D_n$, $k\leq k_{\max}/2$")
    ax[1].legend(loc="lower right", fontsize=6)
    fs.save(fig, os.path.join(a.out, "fig", "fig_g2_p256v6"))
    plt.close(fig)


if __name__ == "__main__":
    main()
