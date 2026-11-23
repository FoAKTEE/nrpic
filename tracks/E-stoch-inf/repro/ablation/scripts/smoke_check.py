#!/usr/bin/env python3
"""Check of the card smoke batch T5SMK of repro/ablation (JOURNAL.md entry 1, prediction P-T5).

    smoke_check.py --run SMOKE_RUN_DIR --ref CORE_PROCESSOR_RUN_DIR --out DIR [--no-fig]

SMOKE_RUN_DIR is the batch run (scratch/E-stoch-inf/<run_id>/ with batch.list, batch.list.status and
one directory per list name); CORE_PROCESSOR_RUN_DIR is core's processor run of the same four decks
for 30 cycles (core-20261123-030705-6b6a4bd). Writes DIR/verdict.json ("verdict": PASS or FAIL, the
numbers of P-T5 (a)-(d)) and DIR/smoke_check.{pdf,png}. PASS gates the six 256^3 runs in
scripts/sequencer.sh: every run exit 0, reached tlim, finite records, the expected dumps and
.rmodes files, card/processor differences below 1e-5 relative (the defect threshold of P-T5).
Bands (b) 1e-12 / 1e-7, (c) and (d) are recorded as held or not; they do not change the verdict.
"""
import argparse
import glob
import json
import math
import os
import re
import sys

import numpy as np

REPO = "/data/haiyangw/nrpic/wt/E-stoch-inf"
# case -> (scenario, level, mesh mode equation, rmodes asked)
CASES = {"sr64_l0": ("SR", 0, False, False), "sr64_l2": ("SR", 2, True, False),
         "usr64_l0": ("USR", 0, False, False), "usr64_l2": ("USR", 2, True, False),
         "sr64_l1m": ("SR", 1, True, True), "usr64_l0m": ("USR", 0, True, True)}
REF_CASES = ["sr64_l0", "sr64_l2", "usr64_l0", "usr64_l2"]
COL_MEANS = [2, 3, 4, 5]      # <phi>, <Pi>, <K>, <chi> (record columns 3-6)
COL_RMS = [7, 8]              # rms(phi - <phi>), rms(Pi - <Pi>) (columns 8, 9)
DEFECT = 1e-5


def deck_value(deck, block, key):
    blk = None
    for ln in open(deck):
        s = ln.split("#", 1)[0].strip()
        m = re.match(r"<(\w+)>", s)
        if m:
            blk = m.group(1)
            continue
        if blk == block and "=" in s and s.split("=", 1)[0].strip() == key:
            return s.split("=", 1)[1].strip()
    return None


def read_rec(path):
    a = np.loadtxt(path, comments="#", ndmin=2)
    return a


def one_file(d, pattern):
    f = sorted(glob.glob(os.path.join(d, pattern)))
    return f[0] if f else None


def wall_per_cycle(d):
    log = os.path.join(d, "athena.log")
    if not os.path.isfile(log):
        return None, None
    cyc = cpu = None
    for ln in open(log, errors="replace"):
        if ln.startswith("MeshBlock-cycles"):
            cyc = float(ln.split("=")[1])
        elif ln.startswith("cpu time used"):
            cpu = float(ln.split("=")[1])
    if cyc and cpu:
        return cpu / cyc, cpu
    return None, cpu


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-fig", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    decks, rcs = {}, {}
    for ln in open(os.path.join(a.run, "batch.list")):
        p = ln.split()
        if p and not p[0].startswith("#"):
            decks[os.path.basename(p[0])] = p[1] if os.path.isabs(p[1]) else os.path.join(REPO, p[1])
    st = os.path.join(a.run, "batch.list.status")
    if os.path.isfile(st):
        for ln in open(st):
            m = re.search(r"rc=(\d+)\s+(\S+)", ln)
            if m:
                rcs[os.path.basename(m.group(2))] = int(m.group(1))
    res, fails = {}, []
    recs = {}
    for c, (scen, lev, mesh, rm) in CASES.items():
        d = os.path.join(a.run, c)
        r = dict(scenario=scen, level=lev, mesh=mesh, rc=rcs.get(c))
        deck = decks.get(c)
        tlim = float(deck_value(deck, "time", "tlim")) if deck else float("nan")
        ddt = float(deck_value(deck, "scalar_field", "dump_dt")) if deck else float("nan")
        hst, con = one_file(d, "*.sf.hst"), one_file(d, "*.sf.con.hst")
        if hst is None or con is None:
            r["missing"] = "records"
            fails.append(f"{c}: records missing")
            res[c] = r
            continue
        h, k = read_rec(hst), read_rec(con)
        recs[c] = h
        r["finite"] = bool(np.all(np.isfinite(h)) and np.all(np.isfinite(k)))
        r["t_end"], r["tlim"], r["cycles"] = float(h[-1, 0]), tlim, int(h[-1, 1])
        r["reached_tlim"] = bool(abs(h[-1, 0] - tlim) <= 1e-9 * tlim)
        r["rms_phi_end"], r["rms_pi_end"] = float(h[-1, 7]), float(h[-1, 8])
        r["dumps"] = len(glob.glob(os.path.join(d, "*.sf.*.dump")))
        r["dumps_expected"] = int(math.floor(tlim / ddt + 1e-9)) + 1
        r["rmodes"] = len(glob.glob(os.path.join(d, "*.sf.*.rmodes")))
        r["rmodes_expected"] = r["dumps_expected"] if rm else 0
        r["wall_per_cycle_s"], r["wall_s"] = wall_per_cycle(d)
        for key, ok in (("rc", r["rc"] == 0), ("finite", r["finite"]), ("tlim", r["reached_tlim"]),
                        ("dumps", r["dumps"] == r["dumps_expected"]),
                        ("rmodes", r["rmodes"] == r["rmodes_expected"])):
            if not ok:
                fails.append(f"{c}: {key}")
        res[c] = r
    # (b) card against processor, cycles in common
    cmp = {}
    for c in REF_CASES:
        rf = one_file(os.path.join(a.ref, c), "*.sf.hst")
        if c not in recs or rf is None:
            fails.append(f"{c}: no card/processor pair")
            continue
        hc, hp = recs[c], read_rec(rf)
        cp = {int(x[1]): x for x in hp}
        rows = [(x, cp[int(x[1])]) for x in hc if int(x[1]) in cp]
        dm = max(float(np.max(np.abs(x[COL_MEANS] - y[COL_MEANS]) / np.abs(y[COL_MEANS]))) for x, y in rows)
        dr = max(float(np.max(np.abs(x[COL_RMS] - y[COL_RMS]) / np.abs(y[COL_RMS]))) for x, y in rows)
        dt = max(abs(float(x[0] - y[0])) for x, y in rows)
        cmp[c] = dict(cycles=len(rows), max_rel_means=dm, max_rel_rms=dr, max_abs_time=dt,
                      per_cycle=[[int(x[1]),
                                  float(np.max(np.abs(x[COL_MEANS] - y[COL_MEANS]) / np.abs(y[COL_MEANS]))),
                                  float(np.max(np.abs(x[COL_RMS] - y[COL_RMS]) / np.abs(y[COL_RMS])))]
                                 for x, y in rows])
        if dm > DEFECT or dr > DEFECT or dt > 1e-12:
            fails.append(f"{c}: card/processor difference above {DEFECT}")
    bands = {}
    if cmp:
        bands["b_means_le_1e-12"] = all(v["max_rel_means"] <= 1e-12 for v in cmp.values())
        bands["b_rms_le_1e-7"] = all(v["max_rel_rms"] <= 1e-7 for v in cmp.values())
    # (c) timing, (d) preview of the ablation at 64^3
    tim = {}
    for s in ("sr", "usr"):
        w0 = res.get(f"{s}64_l0", {}).get("wall_per_cycle_s")
        w2 = res.get(f"{s}64_l2", {}).get("wall_per_cycle_s")
        tim[f"{s}_l2_over_l0"] = (w2 / w0) if (w0 and w2) else None
    bands["c_timing_in_0.95_1.5"] = (all(0.95 <= v <= 1.5 for v in tim.values())
                                     if all(v is not None for v in tim.values()) else None)
    prev = {}
    for name, (x, y, bar) in {"sr_l2_vs_l1m": ("sr64_l2", "sr64_l1m", 1e-4),
                              "usr_l2_vs_l0m": ("usr64_l2", "usr64_l0m", 1e-2),
                              "usr_l0m_vs_l0shells": ("usr64_l0m", "usr64_l0", None)}.items():
        if x in res and y in res and "rms_phi_end" in res[x] and "rms_phi_end" in res[y]:
            v = res[x]["rms_phi_end"] / res[y]["rms_phi_end"] - 1.0
            prev[name] = dict(rel=v, bar=bar, held=(abs(v) < bar) if bar else None)
    held = [v["held"] for v in prev.values() if v["bar"] is not None]
    bands["d_preview_held"] = all(held) if held else None
    verdict = "PASS" if not fails else "FAIL"
    out = dict(verdict=verdict, fails=fails, run=os.path.abspath(a.run), ref=os.path.abspath(a.ref),
               cases=res, card_vs_processor={k: {kk: vv for kk, vv in v.items() if kk != "per_cycle"}
                                              for k, v in cmp.items()},
               timing=tim, preview=prev, bands=bands)
    with open(os.path.join(a.out, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("verdict", "fails", "timing", "bands")}, indent=1))
    if not a.no_fig:
        figure(recs, cmp, res, tim, os.path.join(a.out, "smoke_check"))
    return 0


def figure(recs, cmp, res, tim, path):
    sys.path.insert(0, os.path.join(REPO, "python"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    ax1 = fig.add_axes([0.085, 0.17, 0.24, 0.72])
    ax2 = fig.add_axes([0.445, 0.17, 0.24, 0.72])
    ax3 = fig.add_axes([0.81, 0.17, 0.17, 0.72])
    col = dict(zip(REF_CASES, fs.SERIES[:4]))
    floor = 1e-17
    for c, v in cmp.items():
        pc = np.array(v["per_cycle"])
        ax1.semilogy(pc[:, 0], np.maximum(pc[:, 2], floor), color=col[c], label=c)
        ax1.semilogy(pc[:, 0], np.maximum(pc[:, 1], floor), color=col[c], ls=":")
    ax1.axhline(1e-7, **fs.GUIDE)
    ax1.axhline(1e-12, color="k", lw=1.0, ls=":")
    ax1.set_xlabel("cycle")
    ax1.set_ylabel("card / processor, max rel. diff.")
    ax1.legend(loc="upper left", fontsize="small", ncol=2)
    ax1.set_title("rms (solid), box means (dotted)", fontsize="medium")
    cc = fs.series_colors(len(recs))
    for (c, h), cl in zip(recs.items(), cc):
        ax2.semilogy(h[:, 0], h[:, 7], color=cl, ls="-" if res[c]["mesh"] else "--", label=c)
    fs.no_minor_labels(ax2)
    ax2.set_xlabel("time [1/H*]")
    ax2.set_ylabel(r"rms($\phi - \langle\phi\rangle$)")
    ax2.legend(loc="lower right", fontsize="small", ncol=2)
    ax2.set_title("card runs (dashed: shells)", fontsize="medium")
    names = list(res.keys())
    w = [res[n].get("wall_per_cycle_s") or 0.0 for n in names]
    ax3.barh(range(len(names)), w, color=[fs.PAL["red"] if res[n]["level"] == 2 else fs.PAL["blue"]
                                         for n in names])
    ax3.set_yticks(range(len(names)))
    ax3.set_yticklabels(names, fontsize="small")
    ax3.set_xlabel("wall per cycle [s]")
    ax3.set_title("l2/l0: SR %s, USR %s" % tuple(
        "-" if tim.get(k) is None else f"{tim[k]:.2f}" for k in ("sr_l2_over_l0", "usr_l2_over_l0")),
        fontsize="medium")
    fs.save(fig, path)


if __name__ == "__main__":
    sys.exit(main())
