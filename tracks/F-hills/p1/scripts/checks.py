#!/usr/bin/env python3
"""Numbers behind the decidable items of the P1 prediction on the data so far (package p1,
JOURNAL entry 3): health (trackers, gaps, joints, non-finite values, history Volume, tree and
rate), member and heavy-hole horizon growth, trajectory comparisons with the baselines, the
first approach of m1, the binary's separation and the radiated energy to the last time.
Writes <out>/p1_checks.json and prints it.
Usage: checks.py [--out=<dir>] [--rundir=<dir>] [--baselines-npz=<file>]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p1lib  # noqa: E402

nr = p1lib.nr


def local_minima(t, r):
    i = np.arange(1, len(r) - 1)
    k = i[(r[i] < r[i - 1]) & (r[i] <= r[i + 1])]
    return [(float(t[j]), float(r[j])) for j in k]


def main():
    out = p1lib.out_dir(sys.argv)
    rd = p1lib.rundir(sys.argv)
    res = {"rundir": rd}
    # ---- trackers
    trk = p1lib.trackers(rd)
    tk = {}
    for n, d in trk.items():
        t = d["t"]
        dt = np.diff(t)
        step = np.linalg.norm(np.diff(d["x"], axis=0), axis=1)
        med = float(np.median(step)) if len(step) else 0.0
        big = np.where(step > 10 * med)[0] if med > 0 else np.array([], int)
        tk[n] = dict(rows=int(len(t)), t0=float(t[0]), t1=float(t[-1]),
                     max_gap=float(dt.max()), median_dt=float(np.median(dt)),
                     max_step=float(step.max()), median_step=med,
                     jumps_over_10x=[(float(t[j]), float(step[j])) for j in big[:10]],
                     finite=bool(np.isfinite(d["x"]).all() and np.isfinite(d["v"]).all()),
                     n_files=len(nr.tracker_files(rd, n)))
    res["trackers"] = tk
    t, X, V = p1lib.tracker_common(rd)
    res["common_rows"] = int(len(t))
    res["t_end"] = float(t[-1])
    # ---- history
    h = p1lib.history(rd)
    if h is not None:
        vol = h["Volume"]
        fin = all(np.isfinite(v).all() for v in h.values())
        res["history"] = dict(t0=float(h["time"][0]), t1=float(h["time"][-1]),
                              rows=int(len(vol)), finite=bool(fin),
                              volume_rel_change_max=float(np.max(np.abs(vol / vol[0] - 1))),
                              H_t0=float(np.sqrt(h["H2"][0])), H_max=float(np.sqrt(h["H2"].max())),
                              t_H_max=float(h["time"][np.argmax(h["H2"])]),
                              H_end=float(np.sqrt(h["H2"][-1])))
    # ---- horizons
    good = p1lib.horizons_good(rd)
    hz = {}
    for n, g in good.items():
        d = dict(found=g["found"], missed=g["missed"], good=g["good"])
        if len(g["t"]):
            m0 = float(g["mass"][0])
            d.update(t_first_good=float(g["t"][0]), m_first_good=m0,
                     t_last_good=float(g["t"][-1]), m_last_good=float(g["mass"][-1]),
                     finite=bool(np.isfinite(np.column_stack([g[k] for k in
                                                              ("mass", "hrms", "area")])).all()))
            for tq in (50.0, 100.0, 110.0):
                w = (g["t"] > tq - 2) & (g["t"] < tq + 2)
                if w.any():
                    mq = float(np.median(g["mass"][w]))
                    d[f"m_at_{tq:.0f}"] = mq
                    d[f"growth_at_{tq:.0f}"] = mq / m0 - 1
                    d[f"n_rows_at_{tq:.0f}"] = int(w.sum())
            early = g["t"] < g["t"][0] + 2.0
            d["m_first_2M_median"] = float(np.median(g["mass"][early]))
            if "m_at_100" in d:
                d["growth_at_100_vs_first2M"] = d["m_at_100"] / d["m_first_2M_median"] - 1
        hz[n] = d
    res["horizons"] = hz
    # ---- tree and rate
    segs = p1lib.segment_logs(rd)
    res["segments"] = [dict(seg=s["seg"], job=s["job"], nmb_start=s["nmb_start"],
                            nmb_end=s["nmb_end"], t_first=s.get("t_first"), t_last=s.get("t_last"),
                            mbc_per_s=s.get("mbc_per_s"), cycles_per_s=s.get("cycles_per_s"),
                            exit=s["exit"], term=s["term"]) for s in segs]
    rst = p1lib.restart_headers(rd)
    res["restart_trees"] = [(r["file"], r["time"], r["nmb"]) for r in rst]
    trees = [r["nmb"] for r in rst] + [s["nmb_start"] for s in segs if s["nmb_start"]] + \
            [s["nmb_end"] for s in segs if s["nmb_end"]]
    res["tree_min"], res["tree_max"] = int(min(trees)), int(max(trees))
    # ---- trajectories against the baselines
    b = p1lib.baselines(p1lib.baseline_path(sys.argv, out))
    m = p1lib.MASSES
    r1 = np.linalg.norm(X[:, 0] - X[:, 2], axis=1)
    r2 = np.linalg.norm(X[:, 1] - X[:, 2], axis=1)
    r12 = np.linalg.norm(X[:, 0] - X[:, 1], axis=1)
    xc = (m[0] * X[:, 0] + m[1] * X[:, 1]) / (m[0] + m[1])
    rc = np.linalg.norm(xc - X[:, 2], axis=1)
    tn, Xn = b["newton_t"], b["newton_X"]
    r1n = np.linalg.norm(Xn[:, 0] - Xn[:, 2], axis=1)
    r2n = np.linalg.norm(Xn[:, 1] - Xn[:, 2], axis=1)
    r12n = np.linalg.norm(Xn[:, 0] - Xn[:, 1], axis=1)
    th, Yh = b["hrna_t"], b["hrna_y"]
    r1h = np.linalg.norm(Yh[:, 0:3], axis=1)
    r2h = np.linalg.norm(Yh[:, 6:9], axis=1)
    r12h = np.linalg.norm(Yh[:, 0:3] - Yh[:, 6:9], axis=1)
    a_b = p1lib.baselines_json()["a_b"]
    early = t <= 60.0
    rel1 = np.abs(r1[early] / np.interp(t[early], tn, r1n) - 1)
    rel2 = np.abs(r2[early] / np.interp(t[early], tn, r2n) - 1)
    k100 = t <= 100.0
    wide = r12 > 2 * a_b
    ic = int(np.argmin(rc))
    res["trajectories"] = dict(
        newton_rel_diff_r1M_max_t_le_60=float(rel1.max()),
        newton_rel_diff_r2M_max_t_le_60=float(rel2.max()),
        r12_max_t_le_100=float(r12[k100].max()), r12_min_t_le_100=float(r12[k100].min()),
        t_r12_first_above_2ab=float(t[np.argmax(wide)]) if wide.any() else None,
        two_a_b=2 * a_b,
        cm_min_distance=float(rc[ic]), t_cm_min=float(t[ic]),
        cm_min_is_interior=bool(ic < len(t) - 1),
        r1_minima=local_minima(t, r1)[:5], r2_minima=local_minima(t, r2)[:5],
        r12_minima=local_minima(t, r12)[:8],
        at_end=dict(t=float(t[-1]), r_1M=float(r1[-1]), r_2M=float(r2[-1]), r_12=float(r12[-1]),
                    dr1dt=float(np.polyfit(t[-200:], r1[-200:], 1)[0]),
                    dr2dt=float(np.polyfit(t[-200:], r2[-200:], 1)[0]),
                    newton=dict(r_1M=float(np.interp(t[-1], tn, r1n)),
                                r_2M=float(np.interp(t[-1], tn, r2n)),
                                r_12=float(np.interp(t[-1], tn, r12n))),
                    hrna=dict(r_1M=float(np.interp(t[-1], th, r1h)),
                              r_2M=float(np.interp(t[-1], th, r2h)),
                              r_12=float(np.interp(t[-1], th, r12h)))),
        r1_min_so_far=float(r1.min()), t_r1_min=float(t[np.argmin(r1)]),
        r2_min_so_far=float(r2.min()), t_r2_min=float(t[np.argmin(r2)]),
        heavy_displacement=float(np.linalg.norm(X[-1, 2] - X[0, 2])),
        newton_heavy_displacement_same_t=float(np.linalg.norm(
            np.array([np.interp(t[-1], tn, Xn[:, 2, k]) for k in range(3)]) - Xn[0, 2])))
    # ---- energies at the end (not conserved yet)
    Eu = p1lib.energy_unit()
    E = nr.member_energies(X, V, m, iM=2)
    res["energies_units"] = dict(unit_E=Eu, **{k: float(E[k][-1] / Eu) for k in
                                               ("E_0_bc", "E_1_bc", "E_0_M", "E_1_M", "E_bin")},
                                 E_bin_t_le_60_mean=float(np.mean(E["E_bin"][early]) / Eu))
    # ---- radiated energy so far
    wdir = os.path.join(rd, "waveforms")
    if os.path.isdir(wdir):
        res["E_rad_to_end"] = {}
        for R in sorted(int(f[-8:-4]) for f in os.listdir(wdir) if f.startswith("rpsi4_real_")):
            tw, modes = nr.read_rpsi4(rd, R)
            Er, _, _ = nr.radiated_energy(tw, modes)
            res["E_rad_to_end"][str(R)] = dict(t_end=float(tw[-1]), E=float(Er[-1]),
                                               finite=bool(np.isfinite(Er).all()))
    print(json.dumps(res, indent=1, default=str))
    json.dump(res, open(os.path.join(out, "p1_checks.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
