#!/usr/bin/env python3
"""Lead check of batch 11 (F-hills): the card chains loaded in batch 5, read against the
predictions written before them (JOURNAL.md, batch 5, runs A-C) and the lead's checks Q1-Q4
(JOURNAL.md, batch 11).

Runs (directories under scratch/F-hills/):
  R16n  F-20261121-130351-04074e1  binary alone, members m/16, 0 to 23.34 M
  B     F-20261121-203156-03efdd3  the same run continued from R16n's restart 7 (23.34 M on)
  R12   F-20261121-153707-1eaa5d4  binary alone, m/12, 0 to 21 M
  R8    F-20261121-130358-6cf186a  binary alone, m/8
  A     F-20261121-203144-b2cf16b  passage P1b, m/16 (comp0 = m1, comp1 = m2, comp2 = M)
  C     F-20261121-203247-961801d  passage P1b, m/12
  P1    F-20261119-150017-b45ec5f  passage P1, m/8 (merged at 48.8 M)
  A2, B2, C2  the continuations of A, B, C registered in batch 11 (joined to them when present)
Readers: tracks/F-hills/nr_first/scripts/nrread.py (trackers joined across restarts, failed
horizon searches removed, history with the last row of each time).

Outputs in --out: b11_cards.json, fig_b11_binary.png/.pdf (separation, its difference from the
isolated m/16 run, orbital phase rate), fig_b11_health.png/.pdf (member horizon masses,
H-constraint rms, distances from the heavy hole in A and C).
"""
import argparse
import glob
import json
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/nr_first/scripts"))
sys.path.insert(0, os.path.join(WT, "python"))
import nrread as nr  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/F-hills"
RUNS = {
    "R16n": f"{S}/F-20261121-130351-04074e1",
    "B": f"{S}/F-20261121-203156-03efdd3",
    "R12": f"{S}/F-20261121-153707-1eaa5d4",
    "R8": f"{S}/F-20261121-130358-6cf186a",
    "A": f"{S}/F-20261121-203144-b2cf16b",
    "C": f"{S}/F-20261121-203247-961801d",
    "P1": f"{S}/F-20261119-150017-b45ec5f",
    # continuations registered in batch 11 (each starts from the newest restart of the run
    # before it; joined when their directories exist)
    "A2": f"{S}/F-20261124-141118-fbc6419",
    "B2": f"{S}/F-20261124-135408-1e6db58",
    "C2": f"{S}/F-20261124-141842-d5263e9",
}
# a name stands for the join of these run directories, earliest first
CHAIN = {"B": ["R16n", "B", "B2"], "A": ["A", "A2"], "C": ["C", "C2"]}


def parts(name):
    return [p for p in CHAIN.get(name, [name])
            if os.path.isdir(RUNS[p]) and glob.glob(os.path.join(RUNS[p], "*.z4c.user.hst"))]


def join_tracker(first, second):
    """Tracker dicts of a run and its continuation: rows of the first before the second's
    first time, then the second."""
    if len(second["t"]) == 0:
        return first
    k = first["t"] < second["t"][0]
    return {key: np.concatenate([first[key][k], second[key]]) for key in ("iter", "t", "x", "v")}


def trackers(name):
    ps = parts(name)
    tr = nr.read_trackers(RUNS[ps[0]])
    for p in ps[1:]:
        nxt = nr.read_trackers(RUNS[p])
        tr = {n: join_tracker(tr[n], nxt[n]) if n in nxt else tr[n] for n in tr}
    return tr


def pair(tr, i=0, j=1):
    a, b = tr[i], tr[j]
    t = a["t"]
    xb = np.stack([np.interp(t, b["t"], b["x"][:, c]) for c in range(3)], 1)
    d = a["x"] - xb
    s = np.linalg.norm(d, axis=1)
    ph = np.unwrap(np.arctan2(d[:, 1], d[:, 0]))
    return t, s, ph, d


def dist(tr, i, j):
    a, b = tr[i], tr[j]
    t = a["t"]
    xb = np.stack([np.interp(t, b["t"], b["x"][:, c]) for c in range(3)], 1)
    return t, np.linalg.norm(a["x"] - xb, axis=1)


def horizons(name):
    ps = parts(name)
    h = nr.read_horizons(RUNS[ps[0]])
    for p in ps[1:]:
        nxt = nr.read_horizons(RUNS[p])
        out = {}
        for n in h:
            b, nf0 = h[n]
            if n not in nxt:
                out[n] = (b, nf0)
                continue
            a, nf = nxt[n]
            k = b["t"] < (a["t"][0] if len(a["t"]) else np.inf)
            out[n] = ({c: np.concatenate([b[c][k], a[c]]) for c in a}, nf + nf0)
        h = out
    return h


def hst(name):
    ps = parts(name)
    d = nr.read_hst(glob.glob(os.path.join(RUNS[ps[0]], "*.z4c.user.hst"))[0])
    for p in ps[1:]:
        nxt = nr.read_hst(glob.glob(os.path.join(RUNS[p], "*.z4c.user.hst"))[0])
        k = d["time"] < nxt["time"][0]
        d = {c: np.concatenate([d[c][k], nxt[c]]) for c in nxt if c in d}
    return d


def mesh_ledger(name):
    """MeshBlocks at the end of each segment and the peak card memory (segment logs)."""
    nmb, peak = [], []
    logs = [lg for p in parts(name) for lg in sorted(glob.glob(os.path.join(RUNS[p], "chain", "seg*.log")))]
    for log in logs:
        txt = open(log, errors="replace").read()
        nmb += [int(x) for x in re.findall(r"Current number of MeshBlocks = (\d+)", txt)]
        peak += [int(x) for x in re.findall(r"gpu_mem_peak_MiB=(\d+)", txt)]
    return dict(mb_max=max(nmb) if nmb else None, mb_min=min(nmb) if nmb else None,
                gpu_peak_MiB=max(peak) if peak else None, n_mb_rows=len(nmb))


def local_extrema(t, s, width=4.0):
    """Minima and maxima of s(t) after smoothing over +-width/2 (tracker noise is 1e-4 M)."""
    dt = np.median(np.diff(t))
    n = max(1, int(round(width / dt)))
    ker = np.ones(n) / n
    ss = np.convolve(s, ker, mode="same")
    lo, hi = n, len(t) - n
    mins, maxs = [], []
    for k in range(lo + 1, hi - 1):
        if ss[k] < ss[k - 1] and ss[k] <= ss[k + 1]:
            mins.append((float(t[k]), float(s[k])))
        if ss[k] > ss[k - 1] and ss[k] >= ss[k + 1]:
            maxs.append((float(t[k]), float(s[k])))
    return mins, maxs


def drift_per_M(t, m, t0, t1):
    k = (t >= t0) & (t <= t1)
    if k.sum() < 5:
        return None
    c = np.polyfit(t[k], m[k], 1)
    return float(c[0] / np.median(m[k]))


def at(t, y, T):
    return float(np.interp(T, t, y)) if len(t) and t[0] <= T <= t[-1] else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    o = ap.parse_args()
    os.makedirs(o.out, exist_ok=True)
    res = {"runs": RUNS}

    TR = {k: trackers(k) for k in ("B", "R12", "R8", "A", "C", "P1")}
    OR = {k: pair(TR[k]) for k in TR}

    # ---- Q1: isolated m/16 to 107.85 M
    t, s, ph, _ = OR["B"]
    mins, maxs = local_extrema(t, s)
    om = np.gradient(ph, t)
    q1 = dict(t_end=float(t[-1]), s0=float(s[0]), s_end=float(s[-1]), s_min=float(s.min()),
              t_at_s_min=float(t[np.argmin(s)]), s_max_after_20=float(s[t > 20].max()),
              minima=mins, maxima=maxs,
              s_at={f"{T:g}": at(t, s, T) for T in (10, 20, 23.34, 30, 40, 50, 60, 70, 80, 90,
                                                    100, 105, 107)},
              phase_total_rad=float(ph[-1] - ph[0]), orbits=float((ph[-1] - ph[0]) / (2 * np.pi)),
              omega_at={f"{T:g}": at(t, om, T) for T in (5, 20, 40, 60, 80, 100)},
              below_1M=bool(np.any(s < 1.0)), below_2p5M=bool(np.any(s < 2.5)),
              max_step=float(np.max(np.abs(np.diff(s)))))
    # rate of shrinking in windows
    for (a, b) in ((0, 20), (20, 40), (40, 60), (60, 80), (80, 100), (95, 107.8)):
        k = (t >= a) & (t <= b)
        if k.sum() > 5:
            q1[f"dsdt_{a}_{b}"] = float(np.polyfit(t[k], s[k], 1)[0])
    res["Q1_isolated_m16"] = q1

    # R12 vs B over the common window
    tr12, s12, _, _ = OR["R12"]
    tc = tr12[tr12 <= min(tr12[-1], t[-1])]
    res["R12_minus_R16n_max"] = float(np.max(np.abs(np.interp(tc, tr12, s12) - np.interp(tc, t, s))))

    # ---- Q2: P1b m/16 (A)
    tA, sA, phA, _ = OR["A"]
    kk = tA <= t[-1]
    dAB = np.interp(tA[kk], t, s) - sA[kk]
    t1M, r1M = dist(TR["A"], 0, 2)
    t2M, r2M = dist(TR["A"], 1, 2)
    k20 = tA <= 20
    q2 = dict(t_end=float(tA[-1]), s_min=float(sA.min()), s_end=float(sA[-1]),
              s_at={f"{T:g}": at(tA, sA, T) for T in (10, 20, 30, 40, 50, 60)},
              A_minus_B_max_to20=float(np.max(np.abs(dAB[tA[kk] <= 20]))),
              A_minus_B_max_all=float(np.max(np.abs(dAB))),
              A_minus_B_at={f"{T:g}": at(tA[kk], -dAB, T) for T in (10, 20, 30, 40, 50, 60)},
              r_m1_M_end=float(r1M[-1]), r_m2_M_end=float(r2M[-1]),
              r_m1_M_min=float(r1M.min()), r_m2_M_min=float(r2M.min()),
              r_cm_M_at={f"{T:g}": None for T in ()},
              mesh=mesh_ledger("A"))
    # centre of mass of the pair from M
    a, b, c = TR["A"][0], TR["A"][1], TR["A"][2]
    xb = np.stack([np.interp(tA, b["t"], b["x"][:, q]) for q in range(3)], 1)
    xc = np.stack([np.interp(tA, c["t"], c["x"][:, q]) for q in range(3)], 1)
    rcm = np.linalg.norm(0.5 * (a["x"] + xb) - xc, axis=1)
    q2["r_cm_M_at"] = {f"{T:g}": at(tA, rcm, T) for T in (0, 20, 40, 60)}
    q2["r_cm_M_end"] = float(rcm[-1])
    res["Q2_P1b_m16"] = q2

    # ---- Q3: P1b m/12 (C)
    tC, sC, _, _ = OR["C"]
    kc = tC <= tA[-1]
    dCA = np.interp(tC[kc], tA, sA) - sC[kc]
    res["Q3_P1b_m12"] = dict(t_end=float(tC[-1]), s_end=float(sC[-1]),
                             C_minus_A_max=float(np.max(np.abs(dCA))) if kc.any() else None,
                             C_minus_A_at={f"{T:g}": at(tC[kc], -dCA, T) for T in (5, 10, 15, 20)},
                             mesh=mesh_ledger("C"))
    tP, sP, _, _ = OR["P1"]
    res["P1_s_at"] = {f"{T:g}": at(tP, sP, T) for T in (10, 20, 30, 40, 48)}

    # ---- horizons and constraints
    HZ = {k: horizons(k) for k in ("B", "A", "C")}
    hres = {}
    for k, h in HZ.items():
        hres[k] = {}
        for n, (d, nf) in h.items():
            if len(d["t"]) == 0:
                hres[k][str(n)] = dict(n=0, nfail=nf)
                continue
            m = d["mass"]
            win = [(3, 15), (23, 60), (60, 108)] if k == "B" else [(3, 15), (15, 40), (40, 62)]
            hres[k][str(n)] = dict(
                n=int(len(m)), nfail=int(nf), t_first=float(d["t"][0]), t_last=float(d["t"][-1]),
                m_first=float(m[0]), m_last=float(m[-1]), m_med=float(np.median(m)),
                spin_last=float(d["S"][-1] / m[-1] ** 2) if "S" in d else None,
                drift={f"{a}-{b}": drift_per_M(d["t"], m, a, b) for a, b in win})
    res["horizons"] = hres
    H = {k: hst(k) for k in ("B", "A", "C")}
    res["H_rms"] = {k: {f"{T:g}": (float(np.sqrt(np.interp(T, v["time"], v["H2"])))
                                   if v["time"][-1] >= T else None)
                        for T in (1, 10, 20, 40, 60, 80, 100, 107)} for k, v in H.items()}
    res["H_finite"] = {k: bool(np.all(np.isfinite(v["H2"]))) for k, v in H.items()}
    res["H_max_after_5"] = {k: float(np.sqrt(np.max(v["H2"][v["time"] > 5]))) for k, v in H.items()}

    with open(os.path.join(o.out, "b11_cards.json"), "w") as f:
        json.dump(res, f, indent=1, default=lambda x: None)

    # ---- figures
    fs.use_style()
    col = {"B": fs.PAL["green"], "R12": fs.PAL["orange"], "R8": fs.PAL["red"],
           "A": fs.PAL["blue"], "C": "#7B3FA0", "P1": "0.55"}
    lab = {"B": "binary alone m/16 (R16n + B)", "R12": "binary alone m/12", "R8": "binary alone m/8",
           "A": "passage P1b m/16 (A)", "C": "passage P1b m/12 (C)", "P1": "passage P1 m/8"}
    fig, axs = plt.subplots(3, 1, figsize=(6.4, 7.6), sharex=True)
    for k in ("R8", "P1", "R12", "B", "A", "C"):
        tt, ss, pp, _ = OR[k]
        axs[0].plot(tt, ss, color=col[k], lw=1.6 if k in ("B", "A") else 1.0, label=lab[k])
    axs[0].axhline(2.5, color="0.6", ls=":", lw=0.8)
    axs[0].set_ylabel(r"separation $s$ [$M$]")
    axs[0].legend(fontsize=7, loc="lower left")
    for k in ("R12", "A", "C"):
        tt, ss, _, _ = OR[k]
        kq = tt <= t[-1]
        axs[1].plot(tt[kq], ss[kq] - np.interp(tt[kq], t, s), color=col[k], label=lab[k])
    axs[1].axhline(0, color="0.6", lw=0.6)
    axs[1].axhspan(-0.05, 0.05, color="0.9", zorder=0)
    axs[1].set_ylabel(r"$s - s_{\rm alone,\,m/16}$ [$M$]")
    axs[1].legend(fontsize=7)
    for k in ("B", "R12", "A", "C"):
        tt, ss, pp, _ = OR[k]
        w = np.gradient(pp, tt)
        n = max(1, int(round(2.0 / np.median(np.diff(tt)))))
        ws = np.convolve(w, np.ones(n) / n, mode="same")
        ok = (tt >= tt[0] + 1.0) & (tt <= tt[-1] - 1.0)     # the smoothing window is 2 M
        axs[2].plot(tt[ok], ws[ok], color=col[k], label=lab[k])
    axs[2].set_ylabel(r"$d\phi/dt$ [rad/$M$]")
    axs[2].set_xlabel(r"$t$ [$M$]")
    for ax in axs:
        ax.set_xlim(0, max(t[-1], tA[-1]) + 2)
    fig.tight_layout()
    fs.save(fig, os.path.join(o.out, "fig_b11_binary"))

    fig, axs = plt.subplots(3, 1, figsize=(6.4, 7.6), sharex=True)
    for k, h in HZ.items():
        for n, (d, nf) in h.items():
            if len(d["t"]) == 0:
                continue
            m = d["mass"]
            ls = "-" if n == 0 else ("--" if n == 1 else ":")
            axs[0].plot(d["t"], m / np.median(m[: max(3, len(m) // 20)]) - 1, color=col[k], ls=ls,
                        lw=1.0, label=f"{k} finder {n}")
    axs[0].set_ylabel(r"$m_{\rm AH}/m_{\rm AH}(t_0) - 1$")
    axs[0].legend(fontsize=6, ncol=3)
    for k, v in H.items():
        axs[1].semilogy(v["time"], np.sqrt(np.maximum(v["H2"], 1e-300)), color=col[k], label=lab[k])
    axs[1].set_ylabel(r"rms $\mathcal{H}$")
    axs[1].legend(fontsize=7)
    for k, i in (("A", 0), ("A", 1), ("C", 0), ("C", 1)):
        tt, rr = dist(TR[k], i, 2)
        axs[2].plot(tt, rr, color=col[k], ls="-" if i == 0 else "--", label=f"{k}: m{i + 1} to M")
    axs[2].set_ylabel(r"distance to $M$ [$M$]")
    axs[2].set_xlabel(r"$t$ [$M$]")
    axs[2].legend(fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(o.out, "fig_b11_health"))
    print(json.dumps({k: res[k] for k in ("Q1_isolated_m16", "Q2_P1b_m16", "Q3_P1b_m12")},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
