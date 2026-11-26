#!/usr/bin/env python3
"""Judgement of the card check of core/restart-finder (list card/card_rf.list).

    python card_check.py --card DIR --cpu-restart DIR --cpu-finder DIR --out DIR

--card         output directory of the card run (one directory per line of the list)
--cpu-restart  output directory of restart_test.py on processors (its case A is the
               uninterrupted run of problems/tests/restart_outputs.athinput)
--cpu-finder   output directory of finder_test.py on processors (runs prod, pol, tight)

Checks (predictions K1 to K5 of JOURNAL-restart-finder.md):
  K1  rso_a     the deck on the card with restart files every seven cycles: tracker file
                with header and one record per cycle, twelve conservation records, the
                .prt of a restart file one cycle before a record larger by the block
  K2  rso_r27   the card continues a restart file that the processor build wrote at
                cycle 27, with the block: the first conservation record is that of
                t = 1.6875 and it agrees with the processor run
  K3  fp_*      masses of the polished search (1e-5 with 100 iterations) against the
                tight rule on the card where both are found, and card against processors
  K4  cost      flow iterations per search (status file) and wall time per run: seconds
                per search and per flow iteration on the card
  K5  fp_g04    no removal inside the horizon with ah_exc_max_growth = 0.4

Writes DIR/summary.json and DIR/fig_card_check.{pdf,png}; exit status 0 if the checks
hold.
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import finder_test as ft          # noqa: E402
import restart_test as rt         # noqa: E402

BLOCK = 8 + 32 + 8 + 4*4096*8     # NRPCNS01 block of the 16^3 deck


def table(path):
    return np.array([[float(v) for v in ln.split()] for ln in rt.data_lines(path)])


def status(d):
    """cycle, time, found, reason, flow iterations of every search."""
    rows = []
    for f in glob.glob(os.path.join(d, "*.horizon_status_0.txt")):
        for ln in open(f):
            if ln.strip() and not ln.startswith("#"):
                rows.append([float(v) for v in ln.split("#")[0].split()[:5]])
    return np.array(rows)


def wall(d):
    """Wall time of the main loop from the log of the run (cpu time used)."""
    for f in sorted(glob.glob(os.path.join(d, "*.log")) + glob.glob(os.path.join(d, "*.out"))):
        m = re.findall(r"cpu time used\s*=\s*([0-9.eE+-]+)", open(f, errors="replace").read())
        if m:
            return float(m[-1])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--cpu-restart", required=True)
    ap.add_argument("--cpu-finder", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    card, out = os.path.abspath(a.card), os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    ck, res = {}, {}
    cpuA = os.path.join(os.path.abspath(a.cpu_restart), "A")

    # K1
    d = os.path.join(card, "rso_a")
    trk = rt.tracker_table(os.path.join(d, "rso.co_0.txt"))
    trk_cpu = rt.tracker_table(os.path.join(cpuA, "rso.co_0.txt"))
    cons, cons_cpu = table(os.path.join(d, "rso.cons.hst")), table(os.path.join(cpuA, "rso.cons.hst"))
    prt = {os.path.basename(f): os.path.getsize(f) for f in sorted(glob.glob(os.path.join(d, "rst", "*.prt")))}
    small = min(prt.values()) if prt else 0
    with_block = sorted(k for k, v in prt.items() if v == small + BLOCK)
    dtrk = max(max(abs(x - y) for x, y in zip(va, vb)) for (_, va), (_, vb) in zip(trk, trk_cpu))
    rel = np.max(np.abs(cons[:, 1:] - cons_cpu[:, 1:])/np.maximum(np.abs(cons_cpu[:, 1:]), 1e-300)) \
        if cons.shape == cons_cpu.shape else float("nan")
    res["rso_a"] = dict(tracker_records=len(trk), tracker_headers=rt.header_count(os.path.join(d, "rso.co_0.txt")),
                        cons_records=len(cons), prt_bytes=prt, prt_with_block=with_block,
                        tracker_max_abs_diff_cpu=dtrk, cons_max_rel_diff_cpu=float(rel))
    ck["K1: tracker file with two header lines and the cycles of the processor run (%d)" % len(trk)] = (
        res["rso_a"]["tracker_headers"] == 2 and [t[0] for t in trk] == [t[0] for t in trk_cpu])
    ck["K1: conservation records at the times of the processor run (%d)" % len(cons)] = (
        cons.shape == cons_cpu.shape and bool(np.all(cons[:, 0] == cons_cpu[:, 0])))
    ck["K1: restart files one cycle before a record carry the block (%s)" % with_block] = (
        len(with_block) >= 1 and all(v in (small, small + BLOCK) for v in prt.values()))

    # K2
    d = os.path.join(card, "rso_r27")
    c2 = table(os.path.join(d, "rso.cons.hst"))
    t2 = rt.tracker_table(os.path.join(d, "rso.co_0.txt"))
    late = cons_cpu[cons_cpu[:, 0] > 1.68]
    rel2 = np.max(np.abs(c2[:, 1:] - late[:, 1:])/np.maximum(np.abs(late[:, 1:]), 1e-300)) \
        if c2.shape == late.shape else float("nan")
    res["rso_r27"] = dict(cons_first_time=float(c2[0, 0]) if len(c2) else None, cons_records=len(c2),
                          cons_max_rel_diff_cpu=float(rel2), tracker_first_cycle=t2[0][0] if t2 else None,
                          tracker_records=len(t2))
    ck["K2: the card continues the processor restart file; first conservation record at "
       "t = 1.6875"] = (len(c2) > 0 and abs(c2[0, 0] - 1.6875) < 1e-12)
    ck["K2: its records are those of the processor run after the cut (%d), relative "
       "difference %.1e (K1: %.1e)" % (len(c2), rel2, rel)] = (
        c2.shape == late.shape and bool(np.all(c2[:, 0] == late[:, 0])) and rel2 < max(10.0*rel, 1e-6))
    ck["K2: tracker file started at cycle 27 (no file to continue in a new directory)"] = (
        len(t2) > 0 and t2[0][0] == 27)

    # K3, K4, K5 (card run fp_pol is the run prodpol of finder_test.py: 1e-5 with 100)
    cpu_name = {"prod": "prod", "pol": "prodpol", "tight": "tight"}
    S = {n: ft.summary_rows(os.path.join(card, "fp_" + n)) for n in ("prod", "pol", "tight", "g04")}
    T = {n: status(os.path.join(card, "fp_" + n)) for n in ("prod", "pol", "tight")}
    cpu = os.path.abspath(a.cpu_finder)
    C = {n: ft.summary_rows(os.path.join(cpu, cpu_name[n])) for n in cpu_name}
    CT = {n: ft.status_rows(os.path.join(cpu, cpu_name[n])) for n in cpu_name}
    both = (T["pol"][:, 2] == 1.0) & (T["tight"][:, 2] == 1.0)
    dm = np.abs(S["pol"][:, 2] - S["tight"][:, 2])
    res["finder"] = dict(searches=len(S["pol"]), both_found=int(both.sum()),
                         pol_vs_tight_max=float(np.max(dm[both])) if both.any() else None)
    ck["K3: card, polished search within 2e-5 of the tight rule wherever both are found "
       "(%d searches, max %s)" % (both.sum(), res["finder"]["pol_vs_tight_max"])] = bool(
        both.any() and np.all(dm[both] < 2.0e-5))
    for n in cpu_name:
        # status() keeps five columns, ft.status_rows seven: compare the rows and the found
        # column (the first registered pass compared the shapes and gave nan; run
        # core-20261126-114526-2b1f001)
        nrow = len(T[n]) == len(CT[n]) and len(S[n]) == len(C[n])
        same = nrow and bool(np.all(T[n][:, 2] == CT[n][:, 2]))
        f = (T[n][:, 2] == 1.0) & (CT[n][:, 2] == 1.0) if nrow else np.zeros(0, bool)
        d_ = float(np.max(np.abs(S[n][f, 2] - C[n][f, 2]))) if f.any() else float("nan")
        res["finder"]["card_vs_cpu_" + n] = d_
        res["finder"]["card_vs_cpu_" + n + "_per_search"] = (
            np.abs(S[n][:, 2] - C[n][:, 2]).tolist() if nrow else None)
        res["finder"]["found_differs_at_cycles_" + n] = (
            T[n][T[n][:, 2] != CT[n][:, 2], 0].tolist() if nrow else None)
        ck["K3: card against processors, %s: the same searches found, masses within 1e-8 "
           "(max %.1e)" % (n, d_)] = (same and d_ < 1.0e-8)
    cost = {}
    for n in ("prod", "pol", "tight"):
        st = T[n]
        cost[n] = dict(wall_s=wall(os.path.join(card, "fp_" + n)), searches=int(len(st)),
                       flow_iterations=float(np.sum(st[:, 4])) if len(st) else None)
    res["cost"] = cost
    if all(cost[n]["wall_s"] and cost[n]["flow_iterations"] for n in ("prod", "pol")):
        dw = cost["pol"]["wall_s"] - cost["prod"]["wall_s"]
        di = cost["pol"]["flow_iterations"] - cost["prod"]["flow_iterations"]
        res["cost"]["seconds_per_flow_iteration"] = dw/di if di > 0 else None
        res["cost"]["seconds_per_search_of_100_polishing"] = 100.0*dw/di if di > 0 else None
        ck["K4: cost of a flow iteration on the card measured (%.3g s; 100 polishing "
           "iterations %.3g s per search)" % (dw/di, 100.0*dw/di)] = (di > 0 and dw/di < 0.05)
    else:
        ck["K4: cost of a flow iteration on the card measured"] = False
    r_g, r_p = ft.removed(os.path.join(card, "fp_g04")), ft.removed(os.path.join(card, "fp_prod"))
    n_g, n_p = int(np.sum(r_g[:, 3] == 3.0)), int(np.sum(r_p[:, 3] == 3.0))
    res["guard"] = dict(removed_inside_horizon=dict(no_option=n_p, growth_0p4=n_g))
    ck["K5: without the option particles are removed inside the horizon (%d), with "
       "ah_exc_max_growth = 0.4 none (%d)" % (n_p, n_g)] = (n_p > 0 and n_g == 0)

    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.96, wspace=0.42)
    ax = axs[0]
    ax.plot(cons_cpu[:, 0], cons_cpu[:, 1], color=fs.PAL["blue"], marker="o", ms=3, label="processors, uninterrupted")
    ax.plot(cons[:, 0], cons[:, 1], color=fs.PAL["red"], ls="--", label="card, uninterrupted")
    ax.plot(c2[:, 0], c2[:, 1], color=fs.PAL["green"], ls="none", marker="x", label="card, from cycle 27")
    ax.axvline(1.6875, **fs.MASK_LINE)
    ax.set_yscale("log")
    ax.set_xlabel("t"); ax.set_ylabel("mean of C^E_r (cons.hst)")
    ax.legend(loc="best", fontsize=7); fs.no_minor_labels(ax)
    ax = axs[1]
    ax.semilogy(S["pol"][both, 1], np.maximum(dm[both], 1e-17), color=fs.PAL["red"], marker="o",
                ms=3, label="card: polished - tight")
    for n, col, mk, lab in (("prod", fs.PAL["green"], "s", "1e-5"), ("pol", fs.PAL["yellow"], "^",
                            "1e-5 + 100"), ("tight", fs.PAL["blue"], "v", "tight")):
        if len(S[n]) == len(C[n]):
            ax.semilogy(S[n][:, 1], np.maximum(np.abs(S[n][:, 2] - C[n][:, 2]), 1e-17), color=col,
                        marker=mk, ms=3, ls=":", label="card - processors, " + lab)
    ax.axhline(2.0e-5, **fs.MASK_LINE)
    ax.set_xlabel("t / M"); ax.set_ylabel("|mass difference| (floor 1e-17)")
    ax.legend(loc="best", fontsize=7); fs.no_minor_labels(ax)
    ax = axs[2]
    names = ["prod", "pol", "tight"]
    ax.bar(range(3), [cost[n]["wall_s"] or 0.0 for n in names],
           color=[fs.PAL["green"], fs.PAL["red"], fs.PAL["blue"]], width=0.6)
    ax.set_xticks(range(3)); ax.set_xticklabels(["1e-5", "1e-5 + 100", "tight"], fontsize=8)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_ylabel("wall time of the run on the card / s")
    figs = fs.save(fig, os.path.join(out, "fig_card_check"))
    summary = dict(card=card, checks=ck, results=res, figures=figs, all_ok=all(ck.values()))
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str)
    for k, v in ck.items():
        print("%-4s %s" % ("ok" if v else "FAIL", k))
    print(json.dumps(res["cost"], indent=1))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
