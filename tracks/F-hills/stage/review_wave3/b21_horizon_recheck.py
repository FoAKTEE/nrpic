#!/usr/bin/env python3
"""Horizon recheck of decision 0040 item 3 (lead, batch 21): every horizon statement that enters
F-hills' G1 package, rechecked search by search.

None of this track's runs set `<fastflow> diagnostics = true` (no horizon_status file exists
under scratch/F-hills), so whether a search found a horizon cannot be read from a status file.
The recheck uses the failure signature of the source instead (the route decision 0041 item 4
accepted for Track D): AthenaK z4c/fastflow.cpp keeps the properties of the last accepted
surface and writes them again when a search fails, so a failed search is a row whose columns
3-12 equal those of the row before; before the first success the row is NaN or zero. Every
number below is "made without the diagnostics".

Statements rechecked (JOURNAL.md batch 21, predictions H1-H4):
  H1 failed-search fraction per member finder (m/16 and m/12 below 1 percent before 96 M);
  H2 drift statements of G1 (RISKS R4; stage/G1 C8): m/8 members 1.0-1.7e-3 per M (P1, R8),
     m/16 below 1e-4 per M (R16n, A, A2), C's members 1.2-1.7e-4 per M; all-row slope within
     10 percent of the accepted-row slope;
  H3 P1's merger: finder 0 at 48.81 M (0.2686), finder 1 at 49.06 M (0.2693) accepted; tracker
     separation below 0.1 M at 48.79 M;
  H4 no common horizon of a member with M: heavy hole within 1 percent of its median, no member
     finder above 0.5.
Output (--out): b21_horizon_recheck.json, fig_b21_horizon_recheck.png/.pdf.
"""
import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/nr_first/scripts"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "python"))
import nrread as nr  # noqa: E402
import b11_cards as bc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

# name -> list of run directories joined (earliest first), member resolution, drift windows
SETS = {
    "P1": (["P1"], "m/8", [(10, 40)]),
    "R8": (["R8"], "m/8", [(10, 40)]),
    "R12": (["R12"], "m/12", [(3, 15), (10, 21)]),
    "R16n+B": (["R16n", "B"], "m/16", [(3, 15), (23, 60), (60, 108)]),
    "A+A2": (["A", "A2"], "m/16", [(3, 15), (15, 40), (40, 62), (65, 95)]),
    "C": (["C"], "m/12", [(3, 15), (15, 22)]),
}
T_CUT = 96.0


def raw_rows(path):
    """All searches of one summary file (last row of each time), with a flag 'ok'."""
    a = nr.read_table(path)
    if a.size == 0:
        return np.zeros((0, 12)), np.zeros(0, dtype=bool)
    a = nr.keep_last_per_time(a, col=1)
    ok = np.isfinite(a[:, 2]) & (a[:, 2] > 0)
    rep = np.zeros(len(a), dtype=bool)
    rep[1:] = np.all(a[1:, 2:] == a[:-1, 2:], axis=1)
    return a, ok & ~rep


def joined_rows(parts, n):
    rows, oks = [], []
    for p in parts:
        path = os.path.join(bc.RUNS[p], f"hills.horizon_summary_{n}.txt")
        if not os.path.exists(path):
            continue
        a, ok = raw_rows(path)
        if len(a) == 0:
            continue
        if rows:
            # the later part wins from its first time on (as b11_cards.horizons joins them)
            t0 = a[0, 1]
            keep = [r[:, 1] < t0 for r in rows]
            rows = [r[k] for r, k in zip(rows, keep)]
            oks = [o[k] for o, k in zip(oks, keep)]
        rows.append(a)
        oks.append(ok)
    if not rows:
        return np.zeros((0, 12)), np.zeros(0, dtype=bool)
    return np.vstack(rows), np.concatenate(oks)


def frac_slope(t, m, a, b):
    k = (t >= a) & (t <= b) & np.isfinite(m) & (m > 0)
    if k.sum() < 5:
        return None
    c = np.polyfit(t[k], m[k], 1)
    return float(c[0] / np.median(m[k]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    o = ap.parse_args()
    os.makedirs(o.out, exist_ok=True)
    res = {"note": "made without <fastflow> diagnostics: failed searches by the failure signature (decision 0041 item 4)",
           "runs": {k: [bc.RUNS[p] for p in v[0]] for k, v in SETS.items()}}
    data = {}
    for name, (parts, res_lab, wins) in SETS.items():
        r = {"resolution": res_lab, "finders": {}}
        for n in (0, 1, 2):
            a, ok = joined_rows(parts, n)
            if len(a) == 0:
                r["finders"][str(n)] = {"n_searches": 0}
                continue
            data[(name, n)] = (a, ok)
            t, m = a[:, 1], a[:, 2]
            pre = t < T_CUT
            fails_t = t[~ok]
            r["finders"][str(n)] = {
                "n_searches": int(len(t)), "n_failed": int((~ok).sum()),
                "frac_failed": float((~ok).mean()),
                "n_searches_before_96": int(pre.sum()), "n_failed_before_96": int((~ok & pre).sum()),
                "frac_failed_before_96": float((~ok & pre).sum() / max(pre.sum(), 1)),
                "first_failed_times": [float(x) for x in fails_t[:8]],
                "t_first": float(t[0]), "t_last": float(t[-1]),
                "mass_accepted_min": float(m[ok].min()) if ok.any() else None,
                "mass_accepted_max": float(m[ok].max()) if ok.any() else None,
                "mass_accepted_median": float(np.median(m[ok])) if ok.any() else None,
                "drift_accepted": {f"{x}-{y}": frac_slope(t[ok], m[ok], x, y) for x, y in wins},
                "drift_all_rows": {f"{x}-{y}": frac_slope(t, m, x, y) for x, y in wins},
            }
        res[name] = r

    # H1
    h1 = []
    for name in ("R12", "R16n+B", "A+A2", "C"):
        for n in ("0", "1"):
            f = res[name]["finders"][n]
            if f.get("n_searches"):
                h1.append((name, n, f["frac_failed_before_96"]))
    res["H1"] = {"member_finders_m16_m12": [[a, b, c] for a, b, c in h1],
                 "max": max(c for _, _, c in h1),
                 "m8": {nm: {n: res[nm]["finders"][n].get("frac_failed") for n in ("0", "1")} for nm in ("P1", "R8")},
                 "verdict": "MET" if max(c for _, _, c in h1) < 0.01 else "REFUTED"}

    # H2
    def drifts(name, key):
        return [res[name]["finders"][n]["drift_accepted"].get(key) for n in ("0", "1")]
    h2 = {"P1 10-40 (m/8)": drifts("P1", "10-40"), "R8 10-40 (m/8)": drifts("R8", "10-40"),
          "R16n+B 23-60 (m/16)": drifts("R16n+B", "23-60"), "R16n+B 60-108 (m/16)": drifts("R16n+B", "60-108"),
          "A 15-40 (m/16)": drifts("A+A2", "15-40"), "A 40-62 (m/16)": drifts("A+A2", "40-62"),
          "A2 65-95 (m/16)": drifts("A+A2", "65-95"), "C 15-22 (m/12)": drifts("C", "15-22")}
    rel = []
    for name in SETS:
        for n in ("0", "1", "2"):
            f = res[name]["finders"].get(n, {})
            for w, sa in (f.get("drift_accepted") or {}).items():
                sb = f["drift_all_rows"].get(w)
                if sa and sb and abs(sa) > 2e-5:
                    rel.append([name, n, w, sa, sb, abs(sb - sa) / abs(sa)])
    ok8 = all(v is not None and 1.0e-3 <= abs(v) <= 1.7e-3 for k in ("P1 10-40 (m/8)", "R8 10-40 (m/8)") for v in h2[k])
    ok16 = all(v is not None and abs(v) < 1e-4 for k in h2 if "m/16" in k for v in h2[k])
    okC = all(v is not None and 1.2e-4 <= abs(v) <= 1.7e-4 for v in h2["C 15-22 (m/12)"])
    okrel = all(r[-1] < 0.1 for r in rel)
    res["H2"] = {"drifts_accepted_per_M": h2, "all_vs_accepted": rel,
                 "m8_in_1.0-1.7e-3": ok8, "m16_below_1e-4": ok16, "C_in_1.2-1.7e-4": okC, "rel_below_10pc": okrel,
                 "verdict": "MET" if (ok8 and ok16 and okC and okrel) else "REFUTED in part"}

    # H3: P1 merger
    h3 = {}
    for n in (0, 1):
        a, ok = data[("P1", n)]
        k = np.where(a[:, 2] > 0.2)[0]
        if len(k):
            i = int(k[0])
            h3[f"finder{n}"] = {"t_first_above_0.2": float(a[i, 1]), "mass": float(a[i, 2]), "accepted": bool(ok[i]),
                                "accepted_after": int(ok[i:].sum()), "failed_after": int((~ok[i:]).sum())}
    trp = nr.read_trackers(bc.RUNS["P1"])
    tt, s, _, _ = bc.pair(trp, 0, 1)
    j = np.where(s < 0.1)[0]
    h3["tracker_t_s_below_0.1"] = float(tt[j[0]]) if len(j) else None
    h3["verdict"] = "MET" if (h3.get("finder0", {}).get("accepted") and h3.get("finder1", {}).get("accepted")
                              and abs(h3["finder0"]["t_first_above_0.2"] - 48.81) < 0.02
                              and abs(h3["finder1"]["t_first_above_0.2"] - 49.06) < 0.02
                              and h3["tracker_t_s_below_0.1"] is not None
                              and abs(h3["tracker_t_s_below_0.1"] - 48.79) < 0.02) else "REFUTED"
    res["H3"] = h3

    # H4
    h4 = {}
    okh4 = True
    for name in ("P1", "A+A2", "C"):
        a, ok = data[(name, 2)]
        m = a[ok, 2]
        dev = float(np.max(np.abs(m / np.median(m) - 1)))
        mem = max(float(data[(name, n)][0][data[(name, n)][1], 2].max()) for n in (0, 1))
        h4[name] = {"heavy_max_rel_dev": dev, "member_max_mass": mem}
        okh4 &= dev < 0.01 and mem < 0.5
    h4["verdict"] = "MET" if okh4 else "REFUTED"
    res["H4"] = h4

    with open(os.path.join(o.out, "b21_horizon_recheck.json"), "w") as f:
        json.dump(res, f, indent=1)

    # figure: failed searches over time per run and finder; member masses with failures marked
    fs.use_style()
    fig, axs = plt.subplots(3, 1, figsize=(6.6, 8.4))
    names = list(SETS)
    cols = fs.SERIES + ["#7B3FA0"]
    for i, name in enumerate(names):
        for n, mk in zip((0, 1, 2), ("o", "s", "^")):
            if (name, n) not in data:
                continue
            a, ok = data[(name, n)]
            y = i + 0.25 * (n - 1)
            axs[0].plot(a[~ok, 1], np.full((~ok).sum(), y), mk, color=cols[i % len(cols)], ms=3)
    axs[0].set_yticks(range(len(names)))
    axs[0].set_yticklabels([f"{nm}" for nm in names], fontsize=7)
    axs[0].set_xlabel(r"$t$ [$M$]")
    axs[0].set_title("searches with the failure signature (finder 0, 1, 2 offset; no status files: made without diagnostics)", fontsize=7)
    for i, name in enumerate(("R16n+B", "A+A2", "C")):
        for n in (0, 1):
            a, ok = data[(name, n)]
            m0 = np.median(a[ok, 2])
            axs[1].plot(a[ok, 1], a[ok, 2] / m0 - 1, lw=0.7, color=cols[i], alpha=0.9 if n == 0 else 0.5,
                        label=f"{name} finder {n}" if True else None)
            axs[1].plot(a[~ok, 1], a[~ok, 2] / m0 - 1, "x", color="k", ms=3)
    axs[1].set_ylabel(r"$m_{\rm AH}/\mathrm{median} - 1$ (accepted)")
    axs[1].set_ylim(-6e-3, 6e-3)
    axs[1].legend(fontsize=5, ncol=3)
    for n, col in ((0, fs.PAL["red"]), (1, fs.PAL["orange"])):
        a, ok = data[("P1", n)]
        axs[2].plot(a[ok, 1], a[ok, 2], lw=0.8, color=col, label=f"P1 finder {n} (accepted)")
        axs[2].plot(a[~ok, 1], a[~ok, 2], "x", color="k", ms=3)
    if h3.get("tracker_t_s_below_0.1"):
        axs[2].axvline(h3["tracker_t_s_below_0.1"], color=fs.PAL["blue"], lw=0.8, ls="--", label="trackers: s < 0.1 M")
    axs[2].set_xlim(30, 70)
    axs[2].set_ylabel(r"$m_{\rm AH}$ [$M$]")
    axs[2].set_xlabel(r"$t$ [$M$]")
    axs[2].legend(fontsize=6)
    fig.tight_layout()
    fs.save(fig, os.path.join(o.out, "fig_b21_horizon_recheck"))
    print(json.dumps({k: res[k] for k in ("H1", "H2", "H3", "H4")}, indent=1)[:7000])


if __name__ == "__main__":
    main()
