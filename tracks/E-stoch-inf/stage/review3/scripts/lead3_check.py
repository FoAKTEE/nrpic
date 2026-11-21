#!/usr/bin/env python3
"""Lead's own check of the wave-3 ladder items (E-stoch-inf, batch 2a review).

Predictions LW1-LW6 of the owner JOURNAL (entry of 2026-11-21, lead batch 2a), written before
this script ran.  Own code, or the lead's own code of wave 2b (stage/G1/scripts/lead_check.py:
reader, R^NR extraction, LSODA background and Mukhanov-Sasaki, amplitudes from core's twin
python/nrpic/scalar_field.mode_alpha); nothing of ladder/ or g1verify/ is imported.  The run
parameters are read from the run's own command line (the "# cmd:" line of athena.log) on top
of the deck copied into the run directory, so batch overrides (seed, mesh, nmax2) count.

    lead3_check.py OUT

LW1 seed 2 of P256 (A1, A2, A3 with own code)          run E-20261121-032828-fe18c5f
LW2 P256/P256m odd/even of H at time-matched dumps; the index-paired last dump
                                                        runs E-20261115-172618-f948386, -172629-312a82c
LW3 constraint-record maxima of P256 and P256s2         same
LW4 A6 at 64^3: Richardson orders, odd part of H vs Courant factor   E-20261121-025643-02526ff
LW5 L5: second order of H; first-order M of stencil and continuum projectors   same
LW6 L5 step test at 32^3: first-order M at Courant 0.25 over 0.125   E-20261121-034950-06f01f9
"""
import json
import os
import shlex
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
G1S = os.path.abspath(os.path.join(HERE, "..", "..", "G1", "scripts"))
sys.path.insert(0, G1S)
import lead_check as LC  # noqa: E402  (the lead's own code of wave 2b)

sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/E-stoch-inf"
LADDER_INPUTS = "/data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/ladder/inputs"
P256 = f"{S}/E-20261115-172618-f948386/P256"
P256M = f"{S}/E-20261115-172629-312a82c/P256m"
P256S2 = f"{S}/E-20261121-032828-fe18c5f/P256s2"
BC = f"{S}/E-20261121-025643-02526ff"
L5AB = f"{S}/E-20261121-034950-06f01f9"


def params(rundir):
    """Deck values with the overrides of the command line that the code logged."""
    vals = LC.deck(rundir)
    log = os.path.join(rundir, "athena.log")
    with open(log) as fp:
        for line in fp:
            if line.startswith("# cmd:"):
                for tok in shlex.split(line[len("# cmd:"):]):
                    if "=" in tok and "/" in tok.split("=", 1)[0]:
                        k, v = tok.split("=", 1)
                        vals[k.split("/", 1)[1]] = v
                break
    return vals


LC.deck = params  # a2_a3 and a1_record read their parameters through deck()


def rms(x):
    return float(np.sqrt(np.mean(x * x)))


def rms_vec(mx, my, mz):
    return float(np.sqrt(np.mean(mx * mx + my * my + mz * mz)))


def lw1():
    res, d = LC.a2_a3(P256S2, f"{LADDER_INPUTS}/modes_n4096.txt")
    res["A1"] = LC.a1_record(P256S2, 8.6)
    res["seed_used"] = int(params(P256S2)["rng_seed"])
    res["nmax2_used"] = int(params(P256S2)["noise_nmax2"])
    return res, d


def lw2():
    matched = LC.h_parts(P256, P256M, 4.6)
    fp, fm = LC.dumps(P256), LC.dumps(P256M)
    rec = LC.record(P256)
    # the pairing of waves 2-2b: by index, the last dump of P256m against P256's dump of
    # the same index, whatever its time
    i = len(fm) - 1
    ta, ca, xa = LC.read_dump(fp[i], ["H"])
    tb, cb, xb = LC.read_dump(fm[i], ["H"])
    hn = rec[np.argmin(np.abs(rec[:, 1] - ca)), 9]
    odd = 0.5 * (xa["H"] - xb["H"])
    even = 0.5 * (xa["H"] + xb["H"])
    idx = dict(t_p=ta, t_m=tb, cycle_p=int(ca), cycle_m=int(cb),
               odd=rms(odd) / hn, even=rms(even - even.mean()) / hn)
    idx["odd_over_even"] = idx["odd"] / idx["even"]
    for r in matched:
        r["odd_over_even"] = r["odd"] / r["even"]
    return dict(matched=matched, index_paired_last=idx,
                max_matched_odd_over_even=max(r["odd_over_even"] for r in matched),
                t_of_max=[r["t"] for r in matched if r["odd_over_even"] ==
                          max(x["odd_over_even"] for x in matched)][0])


def lw3():
    out = {}
    for tag, d in (("P256", P256), ("P256s2", P256S2), ("P256m", P256M)):
        rec = LC.record(d)
        w = rec[:, 0] <= 4.6 + 1e-9
        out[tag] = dict(H_max=float(rec[:, 3].max()), M_max=float(rec[:, 6].max()),
                        t_Hmax=float(rec[np.argmax(rec[:, 3]), 0]),
                        H_max_t46=float(rec[w, 3].max()), M_max_t46=float(rec[w, 6].max()),
                        t_end=float(rec[-1, 0]), rows=int(rec.shape[0]))
    return out, {k: LC.record(d) for k, d in (("P256", P256), ("P256s2", P256S2))}


def lw4():
    runs = {th: (LC.dumps(f"{BC}/T{th}p"), LC.dumps(f"{BC}/T{th}m")) for th in ("25", "12", "06")}
    rec = LC.record(f"{BC}/T25p")
    rows = []
    for j in range(len(runs["25"][0])):
        F = {}
        for th in ("25", "12", "06"):
            t, c, x = LC.read_dump(runs[th][0][j], ["phi", "chi", "K", "H"])
            tm, cm, xm = LC.read_dump(runs[th][1][j], ["H"])
            F[th] = (t, x, xm["H"], tm)
        ts = [F[th][0] for th in F]
        if max(ts) - min(ts) > 1e-9 or any(abs(F[th][0] - F[th][3]) > 1e-9 for th in F):
            rows.append(dict(t=ts, skipped="times differ"))
            continue
        t = ts[0]
        hn = rec[np.argmin(np.abs(rec[:, 0] - t)), 9]
        row = dict(t=t, efold=float(rec[np.argmin(np.abs(rec[:, 0] - t)), 2]))
        for v in ("phi", "chi", "K"):
            p = {th: F[th][1][v] - F[th][1][v].mean() for th in F}
            d1 = np.abs(p["25"] - p["12"]).max()
            d2 = np.abs(p["12"] - p["06"]).max()
            row[f"{v}_d1_rel"] = float(d1 / np.abs(p["06"]).max()) if np.abs(p["06"]).max() else 0.0
            row[f"order_{v}"] = float(np.log2(d1 / d2)) if d2 > 0 else None
        m = {th: F[th][1]["chi"].mean() for th in F}
        if abs(m["12"] - m["06"]) > 0:
            row["order_mean_chi"] = float(np.log2(abs(m["25"] - m["12"]) / abs(m["12"] - m["06"])))
        odd = {th: rms(0.5 * (F[th][1]["H"] - F[th][2])) / hn for th in F}
        row.update(H_odd_25=odd["25"], H_odd_12=odd["12"], H_odd_06=odd["06"],
                   H_odd_25_over_06=odd["25"] / odd["06"])
        rows.append(row)
    return rows


def l5_fields(rundir, names):
    out = []
    for f in LC.dumps(rundir):
        t, c, x = LC.read_dump(f, names)
        out.append((t, c, x))
    return out


def lw5():
    names = ["H", "Mx", "My", "Mz"]
    R = {k: l5_fields(f"{BC}/{k}", names) for k in
         ("K1p", "K1m", "K2p", "K2m", "K0", "C1p", "C1m", "C2p", "C2m")}
    recK = LC.record(f"{BC}/K1p")
    recC = LC.record(f"{BC}/C1p")
    rows = []
    for j in range(len(R["K1p"])):
        t = R["K1p"][j][0]
        if any(abs(R[k][j][0] - t) > 1e-9 for k in R):
            continue
        row = dict(t=t, cycle=int(R["K1p"][j][1]))
        hk = recK[np.argmin(np.abs(recK[:, 0] - t)), 9]
        X = {k: R[k][j][2] for k in R}
        he1 = 0.5 * (X["K1p"]["H"] + X["K1m"]["H"]) - X["K0"]["H"]
        he2 = 0.5 * (X["K2p"]["H"] + X["K2m"]["H"]) - X["K0"]["H"]
        e1, e2 = rms(he1 - he1.mean()), rms(he2 - he2.mean())
        row["H_even1"] = e1 / hk
        row["H_even_factor"] = e1 / e2 if e2 > 0 else None
        for tag, (p1, m1, p2, m2), rec in (("K", ("K1p", "K1m", "K2p", "K2m"), recK),
                                            ("C", ("C1p", "C1m", "C2p", "C2m"), recC)):
            mm = rec[np.argmin(np.abs(rec[:, 0] - t)), 10]
            first = []
            for comp in ("Mx", "My", "Mz"):
                o1 = 0.5 * (X[p1][comp] - X[m1][comp])
                o2 = 0.5 * (X[p2][comp] - X[m2][comp])
                first.append((8.0 * o2 - o1) / 3.0)
            row[f"M_first_{tag}"] = rms_vec(*first) / mm
            row[f"_m1_{tag}"] = first
            row[f"Mmag_{tag}"] = mm
        if t > 0:
            d = [c - k for c, k in zip(row["_m1_C"], row["_m1_K"])]
            row["M_first_C_minus_K"] = rms_vec(*d) / row["Mmag_K"]
        for tag in ("K", "C"):
            row.pop(f"_m1_{tag}")
        rows.append(row)
    return rows


def lw6():
    out = {}
    for setname in ("A", "B"):
        d = f"{L5AB}/{setname}"
        R = {k: l5_fields(f"{d}/{k}", ["Mx", "My", "Mz"]) for k in ("K1p", "K1m", "K2p", "K2m")}
        rec = LC.record(f"{d}/K1p")
        rows = {}
        for j in range(len(R["K1p"])):
            t = R["K1p"][j][0]
            X = {k: R[k][j][2] for k in R}
            mm = rec[np.argmin(np.abs(rec[:, 0] - t)), 10]
            first = [(8.0 * 0.5 * (X["K2p"][c] - X["K2m"][c]) - 0.5 * (X["K1p"][c] - X["K1m"][c])) / 3.0
                     for c in ("Mx", "My", "Mz")]
            rows[round(t, 9)] = rms_vec(*first) / mm
        out[setname] = rows
    common = sorted(set(out["A"]) & set(out["B"]))
    ratio = [dict(t=t, M_first_A=out["A"][t], M_first_B=out["B"][t],
                  A_over_B=out["A"][t] / out["B"][t] if out["B"][t] > 0 else None)
             for t in common if t > 0]
    return ratio


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    R = {}
    r1, d1 = lw1()
    R["LW1_seed2"] = r1
    print("LW1", json.dumps({k: v for k, v in r1.items() if k != "A1"}, default=float), r1["A1"])
    R["LW2_P256_odd_even"] = lw2()
    print("LW2", R["LW2_P256_odd_even"]["max_matched_odd_over_even"],
          R["LW2_P256_odd_even"]["index_paired_last"])
    R["LW3_records"], recs = lw3()
    print("LW3", R["LW3_records"])
    R["LW4_A6_64"] = lw4()
    R["LW5_L5"] = lw5()
    R["LW6_L5_step"] = lw6()
    with open(os.path.join(out, "lead3_check.json"), "w") as fp:
        json.dump(R, fp, indent=1, default=float)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH * 1.5, fs.FULL_WIDTH * 0.9))
    ax = np.asarray(ax)
    # (a) seed 2, D_n at N_f against |n| (own extraction)
    k, D, low = d1["k"], d1["D"], d1["low"]
    a = ax[0, 0]
    a.semilogy(k[~low], D[~low], ".", ms=1.5, color="0.6", label=r"$|n| > k_{\max}/2$")
    a.semilogy(k[low], D[low], ".", ms=1.5, label=r"$|n| \leq k_{\max}/2$ (A2)")
    a.axhline(0.02, ls="--", color="k", lw=1, label="A2 threshold 0.02")
    a.set_xlabel(r"$|n|$")
    a.set_ylabel(r"$D_n=|R^{NR}_n/R^{lin}_n-1|$ at $N_f$")
    a.set_title("LW1: P256 seed 2, own extraction", fontsize=9)
    a.legend(fontsize=7, loc="lower right")
    # (b) P256 odd/even of H at time-matched dumps, and the index-paired last dump
    b = ax[0, 1]
    m = R["LW2_P256_odd_even"]["matched"]
    b.semilogy([r["t"] for r in m], [r["odd"] for r in m], "o-", label="odd part")
    b.semilogy([r["t"] for r in m], [r["even"] for r in m], "s-", label="even part (mean removed)")
    ip = R["LW2_P256_odd_even"]["index_paired_last"]
    b.semilogy([ip["t_p"]], [ip["even"]], "x", ms=9, color="C3",
               label=f"even, index-paired last dump (dt = {ip['t_p'] - ip['t_m']:.4f})")
    b.set_xlabel("t (code units)")
    b.set_ylabel(r"rms part of $H$ / $\langle[H]\rangle$")
    b.set_title(f"LW2: P256 odd/even, max matched {R['LW2_P256_odd_even']['max_matched_odd_over_even']:.1f}, "
                f"index-paired {ip['odd_over_even']:.0f}", fontsize=9)
    b.legend(fontsize=7)
    # (c) records of P256 and P256s2
    c = ax[0, 2]
    for tag, sty in (("P256", "-"), ("P256s2", "--")):
        rr = recs[tag]
        c.semilogy(rr[:, 0], rr[:, 3], sty, label=rf"{tag} $\langle|H|/[H]\rangle$")
        c.semilogy(rr[:, 0], rr[:, 6] * 1e-7, sty, label=rf"{tag} $\langle|M|/[M]\rangle \times 10^{{-7}}$")
    c.set_xlabel("t (code units)")
    c.set_title("LW3: constraint records, two seeds", fontsize=9)
    c.legend(fontsize=7)
    # (d) A6 at 64^3 orders
    d = ax[1, 0]
    rows = [r for r in R["LW4_A6_64"] if "skipped" not in r and r["t"] > 0.4]
    for v, mk in (("phi", "o"), ("chi", "s"), ("K", "^"), ("mean_chi", "d")):
        key = f"order_{v}"
        d.plot([r["t"] for r in rows if r.get(key) is not None],
               [r[key] for r in rows if r.get(key) is not None], mk + "-", label=v)
    d.axhspan(3.5, 4.5, color="0.9")
    d.set_ylim(0, 6)
    d.set_xlabel("t (code units)")
    d.set_ylabel("Richardson order (Courant 0.25/0.125/0.0625)")
    d.set_title("LW4: A6 at 64$^3$ (paper set-up)", fontsize=9)
    d.legend(fontsize=7)
    d2 = d.twinx()
    d2.plot([r["t"] for r in rows], [abs(r["H_odd_25_over_06"] - 1) for r in rows], "k:",
            label="|odd H(0.25)/odd H(0.0625) - 1|")
    d2.set_yscale("log")
    d2.legend(fontsize=7, loc="lower right")
    # (e) L5: even factor and first-order M
    e = ax[1, 1]
    L = [r for r in R["LW5_L5"] if r["t"] > 0]
    tl = [r["t"] for r in L]
    e.semilogy(tl, [r["M_first_K"] for r in L], "o-", ms=3, label="first-order M, stencil")
    e.semilogy(tl, [r["M_first_C"] for r in L], "s-", ms=3, label="first-order M, continuum")
    e.semilogy(tl, [r["M_first_C_minus_K"] for r in L], "^-", ms=3, label="continuum - stencil")
    e.semilogy(tl, [r["H_even1"] for r in L], "d-", ms=3, label=r"even part of $H$, $s=100$")
    e.set_xlabel("t (code units)")
    e.set_ylabel("rms / box mean of the magnitude")
    e.set_title("LW5: L5 single kick, 64$^3$ card runs", fontsize=9)
    e.legend(fontsize=7)
    e2 = e.twinx()
    e2.plot(tl, [r["H_even_factor"] - 4.0 for r in L], "k:", label="even factor - 4")
    e2.legend(fontsize=7, loc="lower left")
    # (f) L5 step test: A/B
    f = ax[1, 2]
    rr = R["LW6_L5_step"]
    f.semilogy([r["t"] for r in rr], [r["A_over_B"] for r in rr], "o-", ms=3,
               label="first-order M, Courant 0.25 / 0.125 (32$^3$)")
    f.axhline(16, color="k", ls="--", lw=1, label="fourth order: 16")
    f.axhline(2, color="C3", ls=":", lw=1, label="first order: 2")
    f.set_xlabel("t (code units)")
    f.set_title("LW6: L5 step test at 32$^3$", fontsize=9)
    f.legend(fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_lead3"))


if __name__ == "__main__":
    main()
