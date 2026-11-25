"""P1-P7: the passage P1b (A + A2) with the verifier's own readers, and its Newtonian reference.

Reads only the run directories (trackers and their kept copies, horizon summaries, history,
waveforms) and the deck. Runs unchanged on a longer A2: everything is computed to the last record
present, and the Newtonian reference to max(200, last NR time).

Run: python tracks/F-hills/stage/G1/verifier/scripts/vpassage.py --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vread  # noqa: E402
import vnewton  # noqa: E402
import figstyle  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/F-hills"
RUN_A = os.path.join(SCR, "F-20261121-203144-b2cf16b")
RUN_A2 = os.path.join(SCR, "F-20261124-210400-902c650")
HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "binary_conv", "inputs", "p1b_R16n.athinput"))
A_B = 5.0  # nominal semi-major axis of the deck's binary (deck comment: a_b = 5)


def slope(t, y, t0, t1):
    s = (t >= t0) & (t <= t1)
    if s.sum() < 3:
        return None
    return float(np.polyfit(t[s], y[s], 1)[0])


def binned_slope(t, m, t0, t1, w=1.0):
    """Fractional slope of the 1-M medians (robust against the alternating finder band)."""
    c, v = [], []
    for a in np.arange(t0, t1, w):
        sel = (t >= a) & (t < a + w)
        if sel.sum() >= 3:
            c.append(a + 0.5 * w)
            v.append(np.median(m[sel]))
    if len(c) < 3:
        return None
    c, v = np.array(c), np.array(v)
    return float(np.polyfit(c, v, 1)[0] / np.median(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = ap.parse_args().out
    os.makedirs(out, exist_ok=True)
    res = {"runs": {"A": RUN_A, "A2": RUN_A2}, "deck": DECK}

    # ---------------- trackers: join A + A2 (P2) ----------------
    trk, spans = {}, {}
    for n in (0, 1, 2):
        j, ov, sp = vread.joined_tracker([RUN_A, RUN_A2], n)
        trk[n] = j
        g = vread.gaps(j[:, 1])
        def cls(o):
            a = "A2" if "F-20261124-210400" in o["earlier"] else "A"
            b = "A2" if "F-20261124-210400" in o["later"] else "A"
            return a + "-" + b
        ovs = {}
        for o in ov:
            c = cls(o)
            ovs.setdefault(c, {"n_pairs": 0, "n_common": 0, "max_dx": 0.0})
            ovs[c]["n_pairs"] += 1
            ovs[c]["n_common"] += o["n_common"]
            ovs[c]["max_dx"] = max(ovs[c]["max_dx"], o["max_dx"])
        spans[n] = sp
        res[f"tracker{n}"] = {"n_files": len(sp), "coverage": g, "overlaps_by_class": ovs,
                              "n_steps_not_2^-9": int(np.sum(np.abs(np.diff(j[:, 1]) - 2.0 ** -9) > 1e-12))}
    t_last = float(min(trk[n][-1, 1] for n in (0, 1, 2)))
    res["t_last_nr"] = t_last
    A0, A1, A2_ = vread.common_times(trk[0], trk[1], trk[2])
    t = A0[:, 1]
    x0, x1, xM = A0[:, 2:5], A1[:, 2:5], A2_[:, 2:5]
    v0, v1, vM = A0[:, 5:8], A1[:, 5:8], A2_[:, 5:8]

    # ---------------- horizons (P5) ----------------
    hz = {}
    for tag, rd in (("A", RUN_A), ("A2", RUN_A2)):
        for n in (0, 1, 2):
            d = vread.read_horizon_summary(os.path.join(rd, f"hills.horizon_summary_{n}.txt"))
            acc = ~d["failed"]
            ta, ma = d["t"][acc], d["mass"][acc]
            med = float(np.median(ma))
            hz[(tag, n)] = d
            res[f"horizon_{tag}_{n}"] = {
                "n_raw": d["n_raw"], "n_times": int(len(d["t"])), "n_failed": int(d["failed"].sum()),
                "failed_t": d["t"][d["failed"]][:20].tolist(),
                "t_first": float(d["t"][0]), "t_last": float(d["t"][-1]),
                "max_dt": float(np.diff(d["t"]).max()),
                "median": med, "min": float(ma.min()), "max": float(ma.max()),
                "max_minus_min": float(ma.max() - ma.min()),
                "slope_65_95": slope(ta, ma, 65, 95) if tag == "A2" else slope(ta, ma, 20, 60),
                "slope_window": "65-95 M" if tag == "A2" else "20-60 M",
                "frac_slope": (slope(ta, ma, 65, 95) if tag == "A2" else slope(ta, ma, 20, 60)) / med,
                "max_dev_from_median_frac": float(np.abs(ma / med - 1).max()),
                "hrms_max": float(d["hrms"][acc].max()),
                "binned_median_frac_slope": binned_slope(ta, ma, 65, 95) if tag == "A2" else binned_slope(ta, ma, 20, 60)}
    m_h = [res[f"horizon_A2_{n}"]["median"] for n in (0, 1, 2)]
    res["masses_used"] = {"members_and_M": m_h, "source": "medians of A2's accepted searches"}

    # ---------------- closest approach of the pair (P3) ----------------
    s = np.linalg.norm(x0 - x1, axis=1)
    mins = vread.minima(t, s)
    maxs = [(tt, -dd) for tt, dd in vread.minima(t, -s)]
    after = [mm for mm in mins if mm[0] > 61.8]
    smin = min(mins, key=lambda q: q[1]) if mins else None
    res["pair"] = {"local_minima": mins, "local_maxima": maxs, "min_after_61.8": after,
                   "s_min_sampled": float(s.min()), "t_s_min_sampled": float(t[np.argmin(s)]),
                   "s_min_refined": smin, "s_end": float(s[-1]), "t_end": float(t[-1]),
                   "s_gt_1_throughout": bool(s.min() > 1.0),
                   "A2-1_window_63_75": bool(any(63 <= mm[0] <= 75 and 2.0 <= mm[1] <= 2.7 for mm in after))}

    # ---------------- centre of mass, distances, energies (P4) ----------------
    m0, m1, mM = m_h
    xc = (m0 * x0 + m1 * x1) / (m0 + m1)
    vc = (m0 * v0 + m1 * v1) / (m0 + m1)
    dcm = np.linalg.norm(xc - xM, axis=1)
    d0 = np.linalg.norm(x0 - xM, axis=1)
    d1 = np.linalg.norm(x1 - xM, axis=1)
    unit = (0.125 * 0.125 / A_B) * (1.0 / 0.25) ** (1.0 / 3.0)
    Epair = vnewton.two_body_energy(m0, m1, x0, x1, v0, v1)
    E0M = vnewton.two_body_energy(m0, mM, x0, xM, v0, vM)
    E1M = vnewton.two_body_energy(m1, mM, x1, xM, v1, vM)
    EcM = vnewton.two_body_energy(m0 + m1, mM, xc, xM, vc, vM)
    res["state_at_end"] = {
        "t": float(t[-1]), "d_cm": float(dcm[-1]), "d_cm_slope_last5": slope(t, dcm, t[-1] - 5, t[-1]),
        "d_cm_min": float(dcm.min()), "t_d_cm_min": float(t[np.argmin(dcm)]),
        "d_cm_minima": vread.minima(t, dcm),
        "d0": float(d0[-1]), "d1": float(d1[-1]),
        "E_pair_units": float(Epair[-1] / unit), "E_0M_units": float(E0M[-1] / unit),
        "E_1M_units": float(E1M[-1] / unit), "E_cmM_units": float(EcM[-1] / unit), "unit_E": unit,
        "E_pair_max_after_61.8_units": float(Epair[t > 61.8].max() / unit),
        "note": "coordinate Newtonian energies from tracker positions and coordinate velocities, horizon masses"}
    # sampled every 0.25 M as the lead's table for comparison
    samp = {}
    for tq in (10, 20, 40, 60, 80):
        k = int(np.argmin(np.abs(t - tq)))
        samp[str(tq)] = {"E_0M": float(E0M[k] / unit), "E_1M": float(E1M[k] / unit), "E_pair": float(Epair[k] / unit)}
    res["energies_at"] = samp

    # ---------------- Newtonian reference (P1) ----------------
    mN, xN, vN = vnewton.deck_state(DECK)
    t_end = max(200.0, t_last)
    tn, X, V, sol = vnewton.integrate(mN, xN, vN, t_end, dt_out=0.01)
    sN = np.linalg.norm(X[:, 0] - X[:, 1], axis=1)
    dN0 = np.linalg.norm(X[:, 0] - X[:, 2], axis=1)
    dN1 = np.linalg.norm(X[:, 1] - X[:, 2], axis=1)
    xcN = (mN[0] * X[:, 0] + mN[1] * X[:, 1]) / (mN[0] + mN[1])
    dcN = np.linalg.norm(xcN - X[:, 2], axis=1)
    E0N = vnewton.two_body_energy(mN[0], mN[2], X[:, 0], X[:, 2], V[:, 0], V[:, 2])
    E1N = vnewton.two_body_energy(mN[1], mN[2], X[:, 1], X[:, 2], V[:, 1], V[:, 2])
    EpN = vnewton.two_body_energy(mN[0], mN[1], X[:, 0], X[:, 1], V[:, 0], V[:, 1])
    # alternative energy convention: m v^2/2 relative to M's velocity, with the full m M / r
    E0Nalt = 0.5 * mN[0] * ((V[:, 0] - V[:, 2]) ** 2).sum(1) - mN[0] * mN[2] / dN0

    def gmin(tt, dd):
        k = int(np.argmin(dd))
        mm = vread.minima(tt, dd)
        best = min(mm, key=lambda q: q[1]) if mm else (float(tt[k]), float(dd[k]))
        return {"t": best[0], "d": best[1], "all_minima": mm[:10]}

    def fate(E, d):
        g = d[-1] - d[-int(10 / 0.01)]
        return "ejected" if (E[-1] > 0 and g > 0) else ("bound" if E[-1] < 0 else "undecided")

    v_inf0 = float(np.sqrt(2 * E0N[-1] / (mN[0] * mN[2] / (mN[0] + mN[2])))) if E0N[-1] > 0 else None
    v_inf1 = float(np.sqrt(2 * E1N[-1] / (mN[1] * mN[2] / (mN[1] + mN[2])))) if E1N[-1] > 0 else None
    res["newton"] = {
        "masses": mN.tolist(), "t_end": float(tn[-1]),
        "pair_min": gmin(tn, sN), "m0_M_min": gmin(tn, dN0), "m1_M_min": gmin(tn, dN1), "cm_M_min": gmin(tn, dcN),
        "fate": {"m1(comp0)": fate(E0N, dN0), "m2(comp1)": fate(E1N, dN1)},
        "E_0M_end_units": float(E0N[-1] / unit), "E_1M_end_units": float(E1N[-1] / unit),
        "E_pair_end_units": float(EpN[-1] / unit), "E_0M_end_alt_units": float(E0Nalt[-1] / unit),
        "E_0M_at_units": {str(q): float(E0N[int(round(q / 0.01))] / unit) for q in (10, 20, 40, 60, 80, 100, 150, 200)},
        "E_1M_at_units": {str(q): float(E1N[int(round(q / 0.01))] / unit) for q in (10, 20, 40, 60, 80, 100, 150, 200)},
        "v_inf_comp0": v_inf0, "v_inf_comp1": v_inf1,
        "speed_end": {"comp0_rel_M": float(np.linalg.norm(V[-1, 0] - V[-1, 2])),
                      "comp1_rel_M": float(np.linalg.norm(V[-1, 1] - V[-1, 2]))},
        "d_end": {"comp0_M": float(dN0[-1]), "comp1_M": float(dN1[-1]), "pair": float(sN[-1])},
        "dE_rel": float(np.abs(vnewton.energy(mN, X, V) / vnewton.energy(mN, X[:1], V[:1])[0] - 1).max())}
    # two-body conic of the pair's centre of mass about M from the initial state (point masses)
    mb = mN[0] + mN[1]
    rc = xcN[0] - X[0, 2]
    vcm = (mN[0] * V[0, 0] + mN[1] * V[0, 1]) / mb - V[0, 2]
    mu_c = mb + mN[2]
    hvec = np.cross(rc, vcm)
    eps = 0.5 * (vcm ** 2).sum() - mu_c / np.linalg.norm(rc)
    ecc = np.sqrt(1 + 2 * eps * (hvec ** 2).sum() / mu_c ** 2)
    res["newton"]["cm_conic"] = {"r_p": float((hvec ** 2).sum() / mu_c / (1 + ecc)), "e": float(ecc),
                                 "energy_per_mass": float(eps)}
    res["newton"]["note"] = "bare masses and v = p/m from the deck; G = 1"

    # ---------------- constraint norm (P6) ----------------
    for tag, rd in (("A", RUN_A), ("A2", RUN_A2)):
        h, nraw = vread.read_hst(os.path.join(rd, "hills.z4c.user.hst"))
        rms = np.sqrt(h["H-norm2"] / h["Volume"])
        res[f"hst_{tag}"] = {"n_raw": nraw, "n_times": int(len(h["time"])), "t_first": float(h["time"][0]),
                             "t_last": float(h["time"][-1]), "rmsH_max": float(rms.max()),
                             "t_rmsH_max": float(h["time"][np.argmax(rms)]),
                             "rmsH_last": float(rms[-1]), "Hnorm2_min": float(h["H-norm2"].min()),
                             "Hnorm2_max": float(h["H-norm2"].max()), "Volume_last": float(h["Volume"][-1])}
        res[f"hst_{tag}"]["_series"] = (h["time"], rms, h["H-norm2"])

    # ---------------- waveform samples (P7) ----------------
    for tag, rd in (("A", RUN_A), ("A2", RUN_A2)):
        wf = {}
        for r in (40, 48, 70, 90):
            for part in ("real", "imag"):
                p = os.path.join(rd, "waveforms", f"rpsi4_{part}_{r:04d}.txt")
                nraw, tu = vread.read_wave_times(p)
                gc = vread.grid_check(tu, tu[0], tu[-1], 0.25)
                wf[f"{r}_{part}"] = {"n_raw": nraw, "n_unique": int(len(tu)), "t_first": float(tu[0]),
                                     "t_last": float(tu[-1]), "n_missing_on_0.25_grid": gc["n_missing"],
                                     "missing": gc["missing"]}
        res[f"waveforms_{tag}"] = wf

    t0_A2 = None
    wj = {}
    for r in (40, 48, 70, 90):
        pa = os.path.join(RUN_A, "waveforms", f"rpsi4_real_{r:04d}.txt")
        pb = os.path.join(RUN_A2, "waveforms", f"rpsi4_real_{r:04d}.txt")
        ra, _ = vread.read_numeric(pa)
        rb, _ = vread.read_numeric(pb)
        la = {round(row[0], 6): row for row in ra}   # last row per time
        lb = {round(row[0], 6): row for row in rb}
        t0b = min(lb)
        ta = sorted(k for k in la if k < t0b)
        tall = np.array(ta + sorted(lb))
        common = sorted(set(la) & set(lb))
        dmax = max(float(np.abs(la[k][1:] - lb[k][1:]).max()) for k in common) if common else None
        amax = max(float(np.abs(lb[k][1:]).max()) for k in common) if common else None
        gc = vread.grid_check(tall, 0.0, tall[-1], 0.25)
        wj[str(r)] = {"n_joined": int(len(tall)), "t_last": float(tall[-1]), "n_missing": gc["n_missing"],
                      "n_common_A_A2": len(common), "common_from_to": [common[0], common[-1]] if common else None,
                      "max_abs_diff_common": dmax, "max_abs_value_common": amax}
    res["waveforms_joined_real"] = wj

    # ---------------- figures ----------------
    figstyle.use_style()
    import matplotlib.pyplot as plt
    P = figstyle.PAL
    fig, ax = plt.subplots(2, 2, figsize=(8, 6.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.97, wspace=0.28, hspace=0.28)
    a = ax[0, 0]
    kN = tn <= t_last
    a.plot(X[kN, 0, 0], X[kN, 0, 1], color=P["blue"], lw=1.0, label="Newton m1 (to NR end)")
    a.plot(X[kN, 1, 0], X[kN, 1, 1], color=P["blue"], lw=1.0, ls="--", label="Newton m2")
    a.plot(X[~kN, 0, 0], X[~kN, 0, 1], color=P["blue"], lw=0.6, alpha=0.4)
    a.plot(X[~kN, 1, 0], X[~kN, 1, 1], color=P["blue"], lw=0.6, ls="--", alpha=0.4)
    a.plot(X[:, 2, 0], X[:, 2, 1], color="grey", lw=1.0)
    a.plot(x0[:, 0], x0[:, 1], color=P["red"], lw=1.0, label="NR m1 (A+A2)")
    a.plot(x1[:, 0], x1[:, 1], color=P["red"], lw=1.0, ls="--", label="NR m2")
    a.plot(xM[:, 0], xM[:, 1], color="k", lw=1.0, label="NR M")
    a.set_aspect("equal"); a.set_xlabel("x"); a.set_ylabel("y"); a.legend(loc="lower right", fontsize=7)
    a = ax[0, 1]
    a.plot(tn[kN], sN[kN], color=P["blue"], label="Newton (bare masses)")
    a.plot(t, s, color=P["red"], label="NR A + A2")
    a.axvspan(63, 75, color=P["yellow"], alpha=0.2, label="A2-1 window")
    if smin:
        a.plot(smin[0], smin[1], "o", color="k", ms=4)
    a.set_xlabel("t [M]"); a.set_ylabel("pair separation s"); a.legend(loc="upper left", fontsize=8, ncol=1)
    a = ax[1, 0]
    a.plot(tn[kN], dcN[kN], color=P["blue"], label="Newton, pair c.o.m. to M")
    a.plot(t, dcm, color=P["red"], label="NR, pair c.o.m. to M")
    a.plot(t, d0, color=P["red"], lw=0.8, ls="--", label="NR m1 to M")
    a.plot(t, d1, color=P["red"], lw=0.8, ls=":", label="NR m2 to M")
    a.set_xlabel("t [M]"); a.set_ylabel("coordinate distance"); a.legend(loc="upper right", fontsize=8)
    a = ax[1, 1]
    y = 0
    for n in (0,):
        for name, (t0_, t1_, nl) in spans[n]:
            col = P["red"] if "F-20261124-210400" in name else P["blue"]
            a.plot([t0_, t1_], [y, y], color=col, lw=2)
            y += 1
    a.set_xlabel("t [M]"); a.set_ylabel("tracker file (oldest first)")
    a.text(2, y - 3, "blue: A copies, red: A2 copies\n(tracker 0)", fontsize=8)
    figstyle.save(fig, os.path.join(out, "fig_v_passage"))

    fig, ax = plt.subplots(2, 2, figsize=(8, 5.6))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.09, top=0.97, wspace=0.32, hspace=0.3)
    for n, a in zip((0, 1, 2), (ax[0, 0], ax[0, 1], ax[1, 0])):
        for tag, col in (("A", P["blue"]), ("A2", P["red"])):
            d = hz[(tag, n)]
            acc = ~d["failed"]
            a.plot(d["t"][acc], d["mass"][acc], color=col, lw=0.8, label=f"{tag} accepted")
            if d["failed"].any():
                a.plot(d["t"][d["failed"]], d["mass"][d["failed"]], "x", color="k", ms=3, label=f"{tag} failed")
        a.set_xlabel("t [M]"); a.set_ylabel(f"m_AH finder {n}"); a.legend(fontsize=7, loc="best")
    a = ax[1, 1]
    for tag, col in (("A", P["blue"]), ("A2", P["red"])):
        tt, rms, _ = res[f"hst_{tag}"]["_series"]
        a.semilogy(tt, rms, color=col, label=f"{tag}: sqrt(H-norm2/Volume)")
    a.set_xlabel("t [M]"); a.set_ylabel("rms H over the box"); a.legend(fontsize=8)
    figstyle.save(fig, os.path.join(out, "fig_v_horizons"))
    for tag in ("A", "A2"):
        res[f"hst_{tag}"].pop("_series")

    with open(os.path.join(out, "vpassage.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps({k: res[k] for k in ("t_last_nr", "pair", "state_at_end")}, default=float)[:3000])


if __name__ == "__main__":
    main()
