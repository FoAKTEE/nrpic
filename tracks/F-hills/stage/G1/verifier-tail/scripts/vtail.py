"""Second part of the G1 verification (F-hills): what the first verifier's readers do not read.

Reads A (F-20261121-203144-b2cf16b) and A2 (F-20261124-210400-902c650) directly, with the first
verifier's tracker and summary readers (../../verifier/scripts/vread.py, imported unchanged) and
readers written here for:
- the finder's status files `hills.horizon_status_<n>.txt` (A2 from 133 M; columns cycle, time,
  found, reason, flow_iterations, area, area_mass, meanradius, minradius, mean_expansion,
  min_abs_mean_expansion, points_outside_mesh, center_x..z, then '# reason in words'), joined to
  the summary rows by search time (multiples of 1/32 M);
- the overlaps of the tracker join listed per segment pair with their times;
- the members' fates with the remnant mass after the capture, and the (2,2) amplitude of rPsi4.

Self-test first (synthetic status and summary files with restart repeats, one failure that
repeats the last row and one failure that does not): `--self-test` only, or always at start.

Run: python vtail.py --out <dir>
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "verifier", "scripts")))
import vread  # noqa: E402  (first verifier's reader, unchanged)
import vnewton  # noqa: E402
sys.path.insert(0, HERE)
import figstyle  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/F-hills"
RUN_A = os.path.join(SCR, "F-20261121-203144-b2cf16b")
RUN_A2 = os.path.join(SCR, "F-20261124-210400-902c650")
STATUS_COLS = ["cycle", "t", "found", "reason", "flow_it", "area", "area_mass", "meanradius",
               "minradius", "mean_exp", "min_abs_mean_exp", "outside", "cx", "cy", "cz"]


def tkey32(t):
    return int(round(float(t) * 32.0))


def read_status(path):
    """-> dict of arrays (last row per search time, ordered), raw row count, reason words."""
    rows, words = {}, {}
    nraw = 0
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            num, _, w = s.partition("#")
            parts = num.split()
            if len(parts) != 15:
                continue
            nraw += 1
            r = [float(x) for x in parts]
            k = tkey32(r[1])
            rows[k] = r
            words[k] = w.strip()
    keys = sorted(rows)
    a = np.array([rows[k] for k in keys]).reshape(-1, 15)
    d = {c: a[:, i] for i, c in enumerate(STATUS_COLS)}
    d["key"] = np.array(keys, dtype=np.int64)
    d["words"] = [words[k] for k in keys]
    d["n_raw"] = nraw
    return d


def summary_by_key(path):
    d = vread.read_horizon_summary(path)
    d["key"] = np.array([tkey32(t) for t in d["t"]], dtype=np.int64)
    return d


def self_test(out):
    """Synthetic files: 6 searches, a restart repeat of t = 2/32, search 4 fails and repeats the
    last row (signature catches it), search 5 fails while the row differs from the previous kept
    row (only the status file knows)."""
    os.makedirs(out, exist_ok=True)
    ps, pu = os.path.join(out, "syn_status.txt"), os.path.join(out, "syn_summary.txt")
    hdr_s = "# 1:cycle 2:time 3:found ... # reason in words\n"
    hdr_u = "# 1:iter 2:time 3:mass ...\n"
    st = [(1, 1, 0), (2, 1, 0), (2, 1, 0), (3, 1, 0), (4, 0, 6), (5, 0, 3), (6, 1, 0)]
    su = [(1, 0.50), (2, 0.51), (2, 0.51), (3, 0.52), (4, 0.52), (5, 0.53), (6, 0.54)]
    with open(ps, "w") as f:
        f.write(hdr_s)
        for c, fo, re_ in st:
            vals = [c * 16, c / 32.0, fo, re_, 5] + [0.1] * 7 + [0.0, 0.0, 0.0]
            f.write(" ".join(repr(float(v)) if i in (1,) or i > 4 else str(int(v)) for i, v in enumerate(vals))
                    + ("  # found\n" if fo else "  # not found\n"))
    with open(pu, "w") as f:
        f.write(hdr_u)
        for c, m in su:
            extra = "0.1" if c != 5 else "0.2"
            f.write(f"4 {c / 32.0:.6g} {m} 0 0 0 0 1 {extra} 0 1 1\n")
    s = read_status(ps)
    u = summary_by_key(pu)
    ok = {"n_status_kept": int(len(s["t"])) == 6, "n_raw": s["n_raw"] == 7,
          "status_found": s["found"].tolist() == [1, 1, 1, 0, 0, 1],
          "signature_failed": u["failed"].tolist() == [False, False, False, True, False, False]}
    ok["all"] = all(ok.values())
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = args.out
    os.makedirs(out, exist_ok=True)
    res = {"runs": {"A": RUN_A, "A2": RUN_A2}}
    res["self_test"] = self_test(os.path.join(out, "synthetic"))
    if not res["self_test"]["all"]:
        print(json.dumps(res["self_test"]))
        raise SystemExit("self-test failed")

    # ---------------- trackers: joined record, overlaps per segment pair ----------------
    trk, ovl = {}, {}
    for n in (0, 1, 2):
        j, ov, sp = vread.joined_tracker([RUN_A, RUN_A2], n)
        trk[n] = j
        ovl[n] = ov
    big = []
    for n in (0, 1, 2):
        for o in ovl[n]:
            if o["max_dx"] > 1e-11:
                big.append({"tracker": n, "t_from": o["t_from"], "t_to": o["t_to"],
                            "max_dx": o["max_dx"], "earlier": os.path.basename(os.path.dirname(o["earlier"])),
                            "later": os.path.basename(os.path.dirname(o["later"]))})
    res["overlaps_above_1e-11"] = sorted(big, key=lambda q: (q["tracker"], q["t_from"]))
    a2a2 = {}
    for n in (0, 1, 2):
        ts = [(o["t_from"], o["max_dx"]) for o in ovl[n]
              if "F-20261124-210400" in o["earlier"] and "F-20261124-210400" in o["later"]]
        pre = [dx for t0, dx in ts if t0 < 133.0]
        post = [dx for t0, dx in ts if t0 >= 133.0]
        a2a2[str(n)] = {"n_pairs": len(ts), "max_before_133": max(pre) if pre else None,
                        "max_from_133": max(post) if post else None, "n_from_133": len(post)}
    res["overlaps_A2A2_split_133"] = a2a2

    A0, A1, AM = vread.common_times(trk[0], trk[1], trk[2])
    t = A0[:, 1]
    x0, x1, xM = A0[:, 2:5], A1[:, 2:5], AM[:, 2:5]
    v0, v1, vM = A0[:, 5:8], A1[:, 5:8], AM[:, 5:8]
    d0 = np.linalg.norm(x0 - xM, axis=1)
    d1 = np.linalg.norm(x1 - xM, axis=1)
    s01 = np.linalg.norm(x0 - x1, axis=1)

    def at(tq, y):
        return float(np.interp(tq, t, y))

    inside = d0 < 1.0
    k_in = int(np.argmax(inside)) if inside.any() else None
    stays = bool(inside[k_in:].all()) if k_in is not None else False
    k01 = np.where(d0 < 0.1)[0]
    m1min = vread.minima(t, d1)
    res["fates_positions"] = {
        "t_d0_below_1": float(t[k_in]) if k_in is not None else None, "d0_stays_below_1": stays,
        "t_d0_below_0.1": float(t[k01[0]]) if len(k01) else None,
        "d0_at": {str(q): at(q, d0) for q in (120, 130, 133, 135, 137, 137.5, 138, 140, 150, 170, 186)},
        "d0_max_after_140": float(d0[t >= 140].max()),
        "d1_minima": m1min, "d1_at": {str(q): at(q, d1) for q in (120, 130, 133, 140, 150, 160, 170, 180, 186)},
        "d1_rate_last5": float(np.polyfit(t[t >= 181], d1[t >= 181], 1)[0]),
        "s01_at_186": float(s01[-1])}

    # ---------------- horizons: status files (A2 from 133 M) joined to summaries ----------------
    hz = {}
    for n in (0, 1, 2):
        st = read_status(os.path.join(RUN_A2, f"hills.horizon_status_{n}.txt"))
        su = summary_by_key(os.path.join(RUN_A2, f"hills.horizon_summary_{n}.txt"))
        common, i_s, i_u = np.intersect1d(st["key"], su["key"], return_indices=True)
        found = st["found"][i_s] > 0.5
        sig_fail = su["failed"][i_u]
        reasons = {}
        for w, fo in zip([st["words"][i] for i in i_s], found):
            reasons[w] = reasons.get(w, 0) + 1
        blk = {"n_status_raw": st["n_raw"], "n_status_times": int(len(st["t"])),
               "t_status_first": float(st["t"][0]), "t_status_last": float(st["t"][-1]),
               "n_joined": int(len(common)), "n_found": int(found.sum()), "n_not_found": int((~found).sum()),
               "reasons": reasons,
               "agree_found_vs_signature": int(np.sum(found == ~sig_fail)),
               "not_found_but_signature_ok": int(np.sum(~found & ~sig_fail)),
               "found_but_signature_fail": int(np.sum(found & sig_fail)),
               "flow_it_found_median": float(np.median(st["flow_it"][i_s][found])) if found.any() else None,
               "flow_it_found_max": float(st["flow_it"][i_s][found].max()) if found.any() else None}
        tf = su["t"][i_u][found]
        mf = su["mass"][i_u][found]
        if found.any():
            blk.update({"t_last_found": float(tf.max()), "t_first_not_found": float(su["t"][i_u][~found].min()) if (~found).any() else None,
                        "mass_found_first_last": [float(mf[0]), float(mf[-1])],
                        "mass_found_min_max": [float(mf.min()), float(mf.max())]})
        mism = ~found & ~sig_fail
        blk["not_found_signature_ok_examples"] = [
            {"t": float(su["t"][i_u][k]), "mass": float(su["mass"][i_u][k]), "reason": st["words"][i_s[k]]}
            for k in np.where(mism)[0][:8]]
        hz[n] = (st, su, i_s, i_u, found)
        res[f"status_{n}"] = blk

    # finder 2: the jump (common horizon) and the masses after it
    st2, su2, is2, iu2, f2 = hz[2]
    S2 = vread.read_horizon_summary(os.path.join(RUN_A2, "hills.horizon_summary_2.txt"))
    tt, mm = S2["t"], S2["mass"]
    jumpk = int(np.argmax(mm > 1.06))
    t_jump = float(tt[jumpk])
    post = tt >= t_jump + 1.0
    res["heavy"] = {"t_first_mass_above_1.06": t_jump, "mass_before": float(mm[jumpk - 1]),
                    "mass_at_jump": float(mm[jumpk]),
                    "status_found_at_jump": int(st2["found"][np.searchsorted(st2["key"], tkey32(t_jump))]) if tkey32(t_jump) in set(st2["key"].tolist()) else None,
                    "post_median": float(np.median(mm[post])), "post_min": float(mm[post].min()),
                    "post_max": float(mm[post].max()),
                    "post_slope_per_M": float(np.polyfit(tt[post], mm[post], 1)[0]),
                    "S_at_end": float(S2["S"][-1]), "mass_end": float(mm[-1]),
                    "chi_end": float(S2["S"][-1] / mm[-1] ** 2),
                    "area_mass_end": float(st2["area_mass"][-1])}
    # F1: branches of the heavy hole from 86.6 M to the jump
    w = (tt >= 86.6) & (tt < t_jump)
    tw, mw, hw = tt[w], mm[w], S2["hrms"][w]
    split = 0.5 * (np.percentile(mw, 95) + np.percentile(mw, 5))
    up, lo = mw > split, mw <= split
    f1 = {"window": [86.6, t_jump], "split": float(split), "n_upper": int(up.sum()), "n_lower": int(lo.sum()),
          "upper_median": float(np.median(mw[up])), "lower_median": float(np.median(mw[lo])),
          "upper_slope_per_M": float(np.polyfit(tw[up], mw[up], 1)[0]),
          "lower_slope_per_M": float(np.polyfit(tw[lo], mw[lo], 1)[0]),
          "upper_hrms_median": float(np.median(hw[up])), "lower_hrms_median": float(np.median(hw[lo]))}
    # what the status file says in 133 M .. jump
    ks = (st2["t"] >= 133.0) & (st2["t"] < t_jump)
    kk = st2["key"][ks]
    mfrom = dict(zip(S2["t"].tolist(), S2["mass"].tolist()))
    keymass = {tkey32(a): b for a, b in mfrom.items()}
    br = []
    for k, fo, fi, me in zip(kk, st2["found"][ks], st2["flow_it"][ks], st2["mean_exp"][ks]):
        m = keymass.get(int(k))
        br.append((k / 32.0, m, int(fo), int(fi), float(me), "upper" if (m is not None and m > split) else "lower"))
    nu = [b for b in br if b[5] == "upper"]
    nl = [b for b in br if b[5] == "lower"]
    f1["status_133_to_jump"] = {
        "n": len(br), "n_upper": len(nu), "n_lower": len(nl),
        "found_upper": sum(b[2] for b in nu), "found_lower": sum(b[2] for b in nl),
        "flow_it_upper": sorted(set(b[3] for b in nu)), "flow_it_lower": sorted(set(b[3] for b in nl)),
        "mean_exp_upper_median": float(np.median([b[4] for b in nu])) if nu else None,
        "mean_exp_lower_median": float(np.median([b[4] for b in nl])) if nl else None,
        "first_rows": br[:12]}
    res["F1"] = f1

    # ---------------- masses for the energies after the capture ----------------
    m1 = float(np.median(hz[1][1]["mass"][~hz[1][1]["failed"]]))
    m0 = float(np.median(su["mass"][:0])) if False else 0.12949  # not used past the capture
    mrem = res["heavy"]["post_median"]
    MH = 1.00422  # heavy hole's median before the jump (first part; reader value 1.004220)
    unit = (0.125 * 0.125 / 5.0) * (1.0 / 0.25) ** (1.0 / 3.0)
    e_rem = vnewton.two_body_energy(m1, mrem, x1, xM, v1, vM)
    e_M = vnewton.two_body_energy(m1, MH, x1, xM, v1, vM)
    xc = (MH * xM + 0.12949 * x0) / (MH + 0.12949)
    vc = (MH * vM + 0.12949 * v0) / (MH + 0.12949)
    e_cm = vnewton.two_body_energy(m1, MH + 0.12949, x1, xc, v1, vc)
    vrel = np.linalg.norm(v1 - vM, axis=1)
    res["m2_energy"] = {"m2": m1, "M_remnant": mrem, "unit": unit,
                        "E_units_at": {str(q): {"remnant_at_M_tracker": float(np.interp(q, t, e_rem) / unit),
                                                "M_only_1.00422": float(np.interp(q, t, e_M) / unit),
                                                "cm_of_M_and_m1": float(np.interp(q, t, e_cm) / unit)}
                                       for q in (140, 150, 160, 170, 180, 186)},
                        "v_rel_end": float(vrel[-1]), "v_esc_end_remnant": float(math.sqrt(2 * (mrem + m1) / d1[-1])),
                        "note": "coordinate velocities of the trackers; G = 1; a reading of coordinates"}

    # ---------------- constraint norm and waveform amplitude ----------------
    hA, _ = vread.read_hst(os.path.join(RUN_A, "hills.z4c.user.hst"))
    hB, _ = vread.read_hst(os.path.join(RUN_A2, "hills.z4c.user.hst"))
    tH = np.concatenate([hA["time"][hA["time"] < hB["time"][0]], hB["time"]])
    rH = np.concatenate([np.sqrt(hA["H-norm2"] / hA["Volume"])[hA["time"] < hB["time"][0]],
                         np.sqrt(hB["H-norm2"] / hB["Volume"])])
    sel = tH >= 96.0
    res["rmsH"] = {"max_after_96": float(rH[sel].max()), "t_max_after_96": float(tH[sel][np.argmax(rH[sel])]),
                   "at_end": float(rH[-1]), "max_all": float(rH.max()), "t_max_all": float(tH[np.argmax(rH)])}

    wf = {}
    for r in (40, 48, 70, 90):
        amp = {}
        for tag, rd in (("A", RUN_A), ("A2", RUN_A2)):
            re_, _ = vread.read_numeric(os.path.join(rd, "waveforms", f"rpsi4_real_{r:04d}.txt"))
            im_, _ = vread.read_numeric(os.path.join(rd, "waveforms", f"rpsi4_imag_{r:04d}.txt"))
            for a_, b_ in zip(re_, im_):
                amp[round(a_[0], 6)] = (math.hypot(a_[5], b_[5]), tag)   # column 6 of the file: (2,2)
        ts = np.array(sorted(amp))
        av = np.array([amp[k][0] for k in ts])
        rstar = r + 2 * mrem * math.log(r / (2 * mrem) - 1)
        wf[str(r)] = {"t": ts, "a": av, "r_star": rstar}
    res["waves22"] = {}
    for r in ("40", "48", "70", "90"):
        ts, av = wf[r]["t"], wf[r]["a"]
        early = (ts > 60) & (ts < 130)
        late = ts >= t_jump + wf[r]["r_star"] - 10
        res["waves22"][r] = {"n": int(len(ts)), "t_last": float(ts[-1]), "r_star": wf[r]["r_star"],
                             "t_arrival_expected": t_jump + wf[r]["r_star"],
                             "median_60_130": float(np.median(av[early])),
                             "max_after_arrival_minus_10": float(av[late].max()) if late.any() else None,
                             "t_of_that_max": float(ts[late][np.argmax(av[late])]) if late.any() else None}

    # ---------------- figures ----------------
    figstyle.use_style()
    import matplotlib.pyplot as plt
    P = figstyle.PAL
    mN, xN, vN = vnewton.deck_state(os.path.normpath(os.path.join(
        HERE, "..", "..", "..", "..", "binary_conv", "inputs", "p1b_R16n.athinput")))
    tn, X, V, _ = vnewton.integrate(mN, xN, vN, 200.0, dt_out=0.05)
    dN0 = np.linalg.norm(X[:, 0] - X[:, 2], axis=1)
    dN1 = np.linalg.norm(X[:, 1] - X[:, 2], axis=1)

    fig, ax = plt.subplots(2, 2, figsize=(8, 6.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.97, wspace=0.3, hspace=0.32)
    a = ax[0, 0]
    a.plot(t, d0, color=P["red"], label="NR m1 (tracker 0) to M")
    a.plot(t, d1, color=P["blue"], label="NR m2 (tracker 1) to M")
    a.plot(tn, dN0, color=P["red"], lw=0.8, ls="--", label="Newton m1")
    a.plot(tn, dN1, color=P["blue"], lw=0.8, ls="--", label="Newton m2")
    a.axvline(t_jump, **figstyle.MASK_LINE)
    a.axvline(133.0, color="grey", lw=0.8, ls=":")
    a.set_xlabel("t [M]"); a.set_ylabel("coordinate distance to M"); a.legend(fontsize=7, loc="upper left")
    a = ax[0, 1]
    z = t >= 110
    a.semilogy(t[z], np.maximum(d0[z], 1e-12), color=P["red"], label="m1 to M")
    a.semilogy(t[z], d1[z], color=P["blue"], label="m2 to M")
    a.semilogy(t[z], s01[z], color=P["green"], lw=0.8, label="pair m1-m2")
    a.axvline(t_jump, **figstyle.MASK_LINE)
    a.axhline(1.0, color="k", lw=0.6, ls=":")
    a.set_xlabel("t [M]"); a.set_ylabel("distance (log)"); a.legend(fontsize=7, loc="lower left")
    a = ax[1, 0]
    a.plot(x0[:, 0], x0[:, 1], color=P["red"], lw=0.8, label="m1")
    a.plot(x1[:, 0], x1[:, 1], color=P["blue"], lw=0.8, label="m2")
    a.plot(xM[:, 0], xM[:, 1], color="k", lw=1.0, label="M")
    a.plot(x1[-1, 0], x1[-1, 1], "o", color=P["blue"], ms=3)
    a.set_aspect("equal"); a.set_xlabel("x"); a.set_ylabel("y"); a.legend(fontsize=7)
    a = ax[1, 1]
    for q in ("remnant_at_M_tracker", "M_only_1.00422", "cm_of_M_and_m1"):
        pass
    k2 = t >= 125
    a.plot(t[k2], e_rem[k2] / unit, color=P["blue"], label="m2 vs remnant mass at M's tracker")
    a.plot(t[k2], e_M[k2] / unit, color=P["blue"], lw=0.8, ls="--", label="m2 vs M = 1.00422 (first reader)")
    a.plot(t[k2], e_cm[k2] / unit, color=P["orange"], lw=0.8, label="m2 vs c.o.m. of M and m1")
    a.axhline(0, color="k", lw=0.6)
    a.axvline(t_jump, **figstyle.MASK_LINE)
    a.set_ylim(-3, 3)
    a.set_xlabel("t [M]"); a.set_ylabel("two-body energy [units]"); a.legend(fontsize=6.5, loc="lower right")
    figstyle.save(fig, os.path.join(out, "fig_t_fates"))

    fig, ax = plt.subplots(2, 2, figsize=(8, 6.4))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.97, wspace=0.34, hspace=0.32)
    for n, a in zip((0, 1), (ax[0, 0], ax[0, 1])):
        st, su, i_s, i_u, fo = hz[n]
        S = vread.read_horizon_summary(os.path.join(RUN_A2, f"hills.horizon_summary_{n}.txt"))
        z = S["t"] >= 120
        a.plot(S["t"][z], S["mass"][z], color="grey", lw=0.6, label="summary, every row")
        a.plot(su["t"][i_u][fo], su["mass"][i_u][fo], ".", color=P["blue"], ms=1.5, label="status found")
        a.plot(su["t"][i_u][~fo], su["mass"][i_u][~fo], "x", color=P["red"], ms=2, label="status not found")
        a.axvline(t_jump, **figstyle.MASK_LINE)
        a.axvline(133.0, color="grey", lw=0.8, ls=":")
        if n == 0:
            a.set_yscale("log")
        a.set_xlabel("t [M]"); a.set_ylabel(f"m_AH finder {n}"); a.legend(fontsize=7, loc="best")
    a = ax[1, 0]
    z = (S2["t"] >= 60)
    a.plot(S2["t"][z], S2["mass"][z], ".", color="grey", ms=1)
    zz = (S2["t"] >= 60) & (S2["t"] < t_jump)
    a.plot(S2["t"][zz], S2["mass"][zz], ".", color=P["blue"], ms=1.5)
    st, su, i_s, i_u, fo = hz[2]
    q = su["t"][i_u] < t_jump
    a.plot(su["t"][i_u][q & fo], su["mass"][i_u][q & fo], "o", color=P["green"], ms=2, mfc="none", label="status found (from 133 M)")
    a.axhline(split, color="k", lw=0.6, ls=":")
    a.axvline(86.6, color="grey", lw=0.8, ls=":")
    a.axvline(133.0, color="grey", lw=0.8, ls=":")
    a.set_xlim(60, t_jump + 1)
    lo_, hi_ = np.percentile(S2["mass"][zz], [0.5, 99.5])
    a.set_ylim(lo_ - 2e-4, hi_ + 2e-4)
    a.set_xlabel("t [M]"); a.set_ylabel("m_AH finder 2 (heavy), before the jump"); a.legend(fontsize=7, loc="lower left")
    a = ax[1, 1]
    a.semilogy(tH, rH, color=P["blue"], label="rms H (A + A2)")
    a.axvline(t_jump, **figstyle.MASK_LINE)
    a.axhline(1e-4, color="k", lw=0.6, ls=":")
    a.set_xlabel("t [M]"); a.set_ylabel("sqrt(H-norm2 / Volume)"); a.legend(fontsize=7)
    figstyle.save(fig, os.path.join(out, "fig_t_horizons"))

    fig, ax = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.3)
    a = ax[0]
    for col, r in zip((P["blue"], P["red"], P["green"], P["orange"]), ("40", "48", "70", "90")):
        a.semilogy(wf[r]["t"], wf[r]["a"], color=col, lw=0.8, label=f"r = {r} M")
        a.axvline(t_jump + wf[r]["r_star"], color=col, lw=0.6, ls=":")
    a.set_xlabel("t [M]"); a.set_ylabel("|r Psi4 (2,2)|"); a.legend(fontsize=7, loc="upper left")
    a = ax[1]
    for n, col in ((0, P["red"]), (1, P["blue"]), (2, "k")):
        for o in ovl[n]:
            a.semilogy([o["t_from"], o["t_to"]], [max(o["max_dx"], 1e-17)] * 2, color=col, lw=2)
    a.axvline(133.0, color="grey", lw=0.8, ls=":")
    a.set_xlabel("t [M] (overlap of two tracker files)"); a.set_ylabel("max |dx| in the overlap")
    a.text(5, 1e-9, "red m1, blue m2, black M", fontsize=7)
    figstyle.save(fig, os.path.join(out, "fig_t_waves_overlaps"))

    for r in wf:
        wf[r].pop("t"); wf[r].pop("a")
    with open(os.path.join(out, "vtail.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps({k: res[k] for k in ("self_test", "fates_positions", "heavy", "F1", "rmsH")}, default=float)[:4000])


if __name__ == "__main__":
    main()
