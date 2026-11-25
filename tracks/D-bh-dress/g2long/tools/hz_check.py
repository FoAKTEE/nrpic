#!/usr/bin/env python3
"""Recheck of the horizon searches behind every G2 horizon number (decision 0040 item 3).

No D run was made with `<fastflow> diagnostics = true`, so there is no horizon_status file.
A failed search is recognised by the two signatures the source fixes (athenak/src/z4c/
fastflow.cpp:228-231 and 455-474; g2long JOURNAL entry 23): the summary line prints
`ah_prop[]`, which only an accepted surface sets and which is NaN until the first one of a
process, so a failed search writes NaN (nothing accepted yet in this process) or the
bit-identical values (columns 3-12) of the line before it in the same file.

Reads (all registered outputs, read-only):
  runs      label=RUNDIR:BASE   production summaries (and removed.bin where present)
  --probes  DIR ...             re-search probe directories (FP, FP-ext): one fresh search per
                                horizon per dump, so a NaN line is a failed search
  --core    DIR                 core's re-search with the diagnostics (status files) of four
                                V-1L dumps, for a bit-for-bit match of the tight rule (horizon 1)
  --pair    ES=V                criterion N recomputed with failed lines dropped (judge_long's
                                definition: D = M - M(100 M), max |D_ES - D_V| on 100-500 M)
Writes hz_check.json and hz_check.png/.pdf into --out.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "flux_tools"))
import figstyle  # noqa: E402
import fluxio  # noqa: E402

T0 = 100.0


def raw_rows(path):
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                rows.append([float(x) for x in s.split()])
    return np.array(rows) if rows else np.zeros((0, 12))


def classify(a):
    """Per raw line: 0 found, 1 repeat of the line before (failed), 2 NaN (failed, none accepted)."""
    c = np.zeros(len(a), dtype=int)
    for i in range(len(a)):
        if not np.all(np.isfinite(a[i, 2:])):
            c[i] = 2
        elif i > 0 and np.array_equal(a[i, 2:], a[i - 1, 2:]) and a[i, 1] != a[i - 1, 1]:
            c[i] = 1
    return c


def dedupe_last(a, c):
    """The line fluxio.read_horizon keeps: the last record of each time, sorted by time."""
    t = a[:, 1]
    _, idx_rev = np.unique(t[::-1], return_index=True)
    idx = np.sort(t.size - 1 - idx_rev)
    idx = idx[np.argsort(t[idx], kind="stable")]
    return a[idx], c[idx]


def stretches(t, bad):
    out, i = [], 0
    while i < len(bad):
        if bad[i]:
            j = i
            while j + 1 < len(bad) and bad[j + 1]:
                j += 1
            out.append((float(t[i]), float(t[j]), j - i + 1))
            i = j + 1
        else:
            i += 1
    return out


def run_check(label, rd, base):
    path = os.path.join(rd, base + ".horizon_summary_0.txt")
    a = raw_rows(path)
    c = classify(a)
    ad, cd = dedupe_last(a, c)
    t = ad[:, 1]
    bad = cd > 0
    res = dict(dir=rd, base=base, n_raw=int(len(a)), n_dedup=int(len(ad)),
               n_repeat=int(np.sum(cd == 1)), n_nan=int(np.sum(cd == 2)),
               t_last=float(t[-1]) if t.size else None,
               status_file=bool(glob.glob(os.path.join(rd, base + ".horizon_status_*.txt"))))
    for lo, hi in ((0.0, 20.0), (20.0, 100.0), (100.0, 300.0), (300.0, 500.0), (230.0, 500.0)):
        w = (t >= lo) & (t <= hi)
        res[f"failed_{lo:g}_{hi:g}"] = [int(np.sum(bad & w)), int(np.sum(w))]
    w20 = t > 20.0
    res["frac_failed_after_20"] = float(np.mean(bad[w20])) if w20.any() else None
    st = stretches(t, bad)
    res["failed_stretches"] = st[:40]
    res["n_stretches"] = len(st)
    res["longest_stretch"] = max((s[2] for s in st), default=0)
    # removals whose first sample >= t_rem is a failed line (criteria G: (iii), D2, D3)
    rp = os.path.join(rd, base + ".removed.bin")
    if os.path.exists(rp):
        rem = fluxio.read_removed(rp)
        if np.any(np.diff(rem["time"]) < 0.0):
            rem, _ = fluxio.drop_overlaps(rem, fluxio.restart_times(os.path.join(rd, "rst")))
        hz = np.isin(rem["reason"], (2, 3))
        trem = rem["time"][hz]
        k = np.searchsorted(t, trem, side="left")
        ok = k < t.size
        fb = bad[k[ok]]
        res["removals"] = dict(n=int(trem.size), n_with_sample=int(ok.sum()),
                               n_first_sample_failed=int(fb.sum()),
                               frac_first_sample_failed=float(fb.mean()) if fb.size else None)
    return res, (t, ad[:, 2], cd)


def drift_found(t, m, c):
    keep = c == 0
    t, m = t[keep], m[keep]
    i = int(np.argmin(np.abs(t - T0)))
    return t, m - m[i]


def common(ta, ya, tb, yb):
    ka = np.round(ta * 8).astype(np.int64)
    kb = np.round(tb * 8).astype(np.int64)
    k, ia, ib = np.intersect1d(ka, kb, return_indices=True)
    return k / 8.0, ya[ia], yb[ib]


def probes(dirs):
    out = {}
    for d in dirs:
        for pd in sorted(glob.glob(os.path.join(d, "*_A*"))):
            if not os.path.isdir(pd):
                continue
            rec = {}
            for f in sorted(glob.glob(os.path.join(pd, "*.horizon_summary_*.txt"))):
                n = f.rsplit("_", 1)[1].split(".")[0]
                a = raw_rows(f)
                rec[n] = dict(n_lines=int(len(a)),
                              finite=bool(len(a) > 0 and np.all(np.isfinite(a[:, 2:]))),
                              time=float(a[0, 1]) if len(a) else None,
                              mass=float(a[0, 2]) if len(a) else None)
            out[os.path.basename(pd)] = rec
    return out


def core_match(core_dir, probe_res):
    """Core's horizon 1 (mass_tol 1e-9, 4000 iterations, from r = 1) against D's h1 (same rule)."""
    out = {}
    for sd in sorted(glob.glob(os.path.join(core_dir, "v1l.*"))):
        dump = os.path.basename(sd)          # v1l.00002
        st = raw_rows(os.path.join(sd, "v1l.horizon_status_1.txt"))
        sm = raw_rows(os.path.join(sd, "v1l.horizon_summary_1.txt"))
        found = int(st[0, 2]) if len(st) else None
        key = [k for k in probe_res if k.endswith("_" + dump + "_A16")]
        dm = probe_res[key[0]].get("1", {}).get("mass") if key else None
        cm = float(sm[0, 2]) if len(sm) else None
        out[dump] = dict(core_found=found, core_flow_iterations=int(st[0, 4]) if len(st) else None,
                         core_mass=cm, D_probe=key[0] if key else None, D_mass=dm,
                         bit_equal=(dm is not None and cm is not None and dm == cm),
                         diff=(dm - cm) if (dm is not None and cm is not None) else None)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--probes", nargs="*", default=[])
    ap.add_argument("--core", default=None)
    ap.add_argument("--pair", action="append", default=[])
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R, S = {}, {}
    for s in a.runs:
        name, rest = s.split("=", 1)
        rd, base = rest.rsplit(":", 1)
        R[name], S[name] = run_check(name, rd, base)
    J = dict(runs=R)
    N = {}
    for p in a.pair:
        es, v = p.split("=")
        out = {}
        for mode in ("all_lines", "found_only"):
            tE, mE, cE = S[es]
            tV, mV, cV = S[v]
            if mode == "all_lines":
                cE0, cV0 = np.zeros_like(cE), np.zeros_like(cV)
            else:
                cE0, cV0 = cE, cV
            te, de = drift_found(tE, mE, cE0)
            tv, dv = drift_found(tV, mV, cV0)
            tc, x, y = common(te, de, tv, dv)
            w = (tc >= T0) & (tc <= 500.0 + 1e-9)
            out[mode] = dict(max_abs=float(np.max(np.abs(x[w] - y[w]))) if w.any() else None,
                             n=int(w.sum()), t_end=float(tc[w][-1]) if w.any() else None)
        N[p] = out
    J["criterion_N"] = N
    if a.probes:
        P = probes(a.probes)
        J["probes"] = dict(n=len(P), n_lines_not_one=sum(1 for r in P.values() for h in r.values() if h["n_lines"] != 1),
                           n_not_finite=sum(1 for r in P.values() for h in r.values() if not h["finite"]),
                           detail=P)
        if a.core:
            J["core_match"] = core_match(a.core, P)
    with open(os.path.join(a.out, "hz_check.json"), "w") as f:
        json.dump(J, f, indent=1)

    figstyle.use_style()
    import matplotlib.pyplot as plt
    names = list(S)
    fig, axs = plt.subplots(2, 1, figsize=(7.0, 6.2), gridspec_kw=dict(height_ratios=[1.3, 1]))
    ax = axs[0]
    cols = figstyle.series_colors(len(names))
    for i, n in enumerate(names):
        t, m, c = S[n]
        ok = np.isfinite(m)
        ax.plot(t[ok], m[ok] - (m[ok][np.argmin(np.abs(t[ok] - T0))] if t[ok].max() >= T0 else 0) + 2e-4 * i,
                lw=0.7, color=cols[i], label=n)
        bad = (c == 1) & ok
        ax.plot(t[bad], (m[bad] - (m[ok][np.argmin(np.abs(t[ok] - T0))] if t[ok].max() >= T0 else 0)) + 2e-4 * i,
                "x", color="k", ms=4)
    ax.set_xlim(0, 510)
    ax.set_ylim(-1e-3, 2e-4 * len(names) + 1e-3)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$M_{\rm AH}(t)-M_{\rm AH}(100M)$ + offset")
    ax.set_title("(a) finder summaries; x = bit-identical repeat (failed search)", loc="left", fontsize=9)
    ax.legend(fontsize=6, ncol=3, loc="upper left")
    ax = axs[1]
    frac = [100 * (R[n]["frac_failed_after_20"] or 0.0) for n in names]
    ax.bar(range(len(names)), frac, color=cols)
    for i, n in enumerate(names):
        ax.text(i, frac[i], f"{R[n]['n_repeat']}+{R[n]['n_nan']}/{R[n]['n_dedup']}", ha="center",
                va="bottom", fontsize=6)
    ax.axhline(1.0, color="k", ls="--", lw=0.8)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=30, fontsize=7)
    ax.set_ylabel("failed lines after 20 M (%)")
    ax.set_title("(b) failed searches by signature (repeat + NaN / lines); dashed: bound of H1", loc="left",
                 fontsize=9)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out, "hz_check." + ext), dpi=150)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("failed_stretches",)} for k, v in R.items()},
                     indent=0))
    print("criterion_N", json.dumps(N))
    if "probes" in J:
        print("probes", J["probes"]["n"], "lines!=1", J["probes"]["n_lines_not_one"], "not finite",
              J["probes"]["n_not_finite"])
    if "core_match" in J:
        print("core_match", json.dumps(J["core_match"], indent=0))


if __name__ == "__main__":
    main()
