#!/usr/bin/env python3
"""Card cases of session dfix-3 (journal, "Card cases still missing"): T5 (pair horizon),
T7 (sphere on a moving tracker) and the peak card memory of the three-hole mesh at 2700
MeshBlock slots, judged against the processor runs and the earlier card run.

    card2_judge.py --t5 DIR --t7 DIR --mem DIR [--timing DIR ...] \
        --cpu-t5 DIR --cpu-t7 DIR --ref-mem DIR [--fig PREFIX]

--t5, --t7, --mem   case directories of the card runs (gpu_run.sh logs with the peak memory)
--timing            further case directories whose wall time and memory are only reported
--cpu-t5            processor case of T5 (run core-20261115-161025-3f75eb8, case new)
--cpu-t7            processor case of T7 (run core-20261115-163129-a200caf, directory run)
--ref-mem           card run of the three holes at 2400 slots (core-20261115-120834-d08c476)
Writes card2_judge.json into $NRPIC_RUN_DIR (or the current directory) and PREFIX.png.
"""
import argparse
import datetime
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "python")))
import t5_pair as t5        # noqa: E402
import t7_tracker as t7     # noqa: E402

MIB_PER_SLOT = 63059.0/2400.0          # three finders, run core-20261115-120834-d08c476
PRED_MEM = (68.9e3, 72.9e3)            # journal, session dfix-3


def runlog(d):
    """wall time, cycles, MeshBlocks, termination and card memory from a gpu_run.sh log"""
    path = os.path.join(d, "athena.log")
    txt = open(path, errors="replace").read()
    out = {"dir": d}
    m = re.search(r"start=(\S+)", txt)
    e = re.search(r"# exit=(-?\d+) end=(\S+) gpu_mem_baseline_MiB=(\S+) gpu_mem_peak_MiB=(\S+)", txt)
    if m and e:
        t0 = datetime.datetime.fromisoformat(m.group(1))
        t1 = datetime.datetime.fromisoformat(e.group(2))
        out.update(wall_s=(t1 - t0).total_seconds(), exit=int(e.group(1)),
                   mem_baseline_mib=float(e.group(3)), mem_peak_mib=float(e.group(4)))
    cyc = re.findall(r"cycle=(\d+) time=(\S+)", txt)
    out["last_cycle"] = int(cyc[-1][0]) if cyc else None
    out["last_time"] = float(cyc[-1][1]) if cyc else None
    nmb = re.findall(r"Total number of MeshBlocks = (\d+)", txt)
    out["meshblocks_start"] = int(nmb[0]) if nmb else None
    term = re.findall(r"Terminating on [^\n]*", txt)
    out["termination"] = term[-1].strip() if term else None
    zc = re.findall(r"zone-cycles/cpu_second = (\S+)", txt)
    out["zone_cycles_per_s"] = float(zc[-1]) if zc else None
    cpu = re.findall(r"cpu time used\s+= (\S+)", txt)
    out["athena_cpu_time_s"] = float(cpu[-1]) if cpu else None
    gm = sorted(f for f in os.listdir(d) if f.endswith(".gpumem.csv"))
    if gm:
        rows = []
        for ln in open(os.path.join(d, gm[-1])):
            if ln.startswith("#"):
                continue
            w = [x.strip() for x in ln.split(",")]
            try:
                ts = datetime.datetime.strptime(w[0], "%Y/%m/%d %H:%M:%S.%f")
                rows.append((ts, float(w[1])))
            except (ValueError, IndexError):
                continue
        if rows:
            out["gpumem_series"] = [((r[0] - rows[0][0]).total_seconds(), r[1]) for r in rows]
    return out


def judge_t5(card, cpu):
    a, b = t5.read(card), t5.read(cpu)
    out = {"records_card": {n: int(len(a[n])) for n in range(3)},
           "records_cpu": {n: int(len(b[n])) for n in range(3)}}
    if len(a[0]) == len(b[0]) and len(a[0]):
        out["mass_card"] = a[0][:, 2].tolist()
        out["mass_cpu"] = b[0][:, 2].tolist()
        out["mass_card_minus_cpu_max"] = float(np.abs(a[0][:, 2] - b[0][:, 2]).max())
        out["mean_radius_card_minus_cpu_max"] = float(np.abs(a[0][:, 10] - b[0][:, 10]).max())
        out["time_card"] = a[0][:, 1].tolist()
    return out, (a, b)


def snaps(d):
    """{time: (tags, positions)} of the T7 snapshots"""
    out = {}
    for f in sorted(x for x in os.listdir(d) if x.startswith("atr.part.")):
        b = open(os.path.join(d, f), "rb").read()
        t = float(np.frombuffer(b[8:16], dtype="<f8")[0])
        n = int(np.frombuffer(b[16:24], dtype="<i8")[0])
        rec = np.frombuffer(b[32:32 + 56*n], dtype="<f8").reshape(n, 7)
        tag = np.frombuffer(b[32 + 56*n:32 + 60*n], dtype="<i4")
        o = np.argsort(tag)
        out[round(t, 9)] = (tag[o], rec[o, 0:3])
    return out


def judge_t7(card, cpu):
    rc, hc = t7.judge(card)
    rp, hp = t7.judge(cpu)
    out = {"card": rc, "cpu_counts": {k: rp[k] for k in ("n_in", "n_out", "n_excised",
                                                            "n_inside_end", "records")}}
    out["counts_equal_cpu"] = all(rc[k] == rp[k] for k in ("n_in", "n_out", "n_excised",
                                                              "n_inside_end", "records"))
    out["snapshot_contents_card"] = [s["inside_history"] for s in rc["snapshots"]]
    out["snapshot_contents_cpu"] = [s["inside_history"] for s in rp["snapshots"]]
    if hc.shape == hp.shape:
        out["history_count_columns_equal"] = bool(np.array_equal(hc[:, [15, 17, 20, 5]],
                                                                 hp[:, [15, 17, 20, 5]]))
        out["centre_card_minus_cpu_max"] = float(np.abs(hc[:, 2:5] - hp[:, 2:5]).max())
        dcen = np.abs(hc[:, 2:5] - hp[:, 2:5]).max(axis=1)
    else:
        dcen = None
    sc, sp = snaps(card), snaps(cpu)
    dpos = []
    for t in sorted(set(sc) & set(sp)):
        if np.array_equal(sc[t][0], sp[t][0]):
            dpos.append((t, float(np.abs(sc[t][1] - sp[t][1]).max())))
        else:
            dpos.append((t, None))
    out["snapshot_position_card_minus_cpu_max"] = dpos
    return out, (hc, hp, dcen, dpos)


def judge_mem(card, ref, tim):
    lg = runlog(card)
    out = {"run": {k: v for k, v in lg.items() if k != "gpumem_series"}}
    out["predicted_band_mib"] = PRED_MEM
    out["model_mib"] = MIB_PER_SLOT*2700
    pk = lg.get("mem_peak_mib")
    out["peak_in_band"] = bool(pk is not None and PRED_MEM[0] <= pk <= PRED_MEM[1])
    if pk is not None:
        out["mib_per_slot_2700"] = pk/2700.0
        out["slope_2400_to_2700_mib_per_slot"] = (pk - 63059.0)/300.0
    h = np.loadtxt(os.path.join(card, "by3.z4c.user.hst"))
    r = np.loadtxt(os.path.join(ref, "by3.z4c.user.hst"))
    rows = []
    for row in h:
        k = np.where(np.abs(r[:, 0] - row[0]) < 1e-9)[0]
        if len(k):
            rows.append((row, r[k[0]]))
    out["history_common_times"] = [float(a[0]) for a, _ in rows]
    rel = [float(np.max(np.abs(a - b)/np.maximum(np.abs(b), 1e-300))) for a, b in rows]
    out["history_max_rel_diff_per_time"] = rel
    out["history_identical_printed"] = bool(all(np.array_equal(a, b) for a, b in rows))
    if tim:
        tl = runlog(tim)
        out["timing_run_peak_mib"] = tl.get("mem_peak_mib")
    return out, lg


def figure(t5d, t7d, memlg, timlg, prefix):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.97, wspace=0.30, hspace=0.36)
    a, b = t5d
    x = ax[0, 0]
    x.axhspan(t5.BAND[0], t5.BAND[1], color="grey", alpha=0.15)
    x.axhline(t5.EXPECT, **fs.GUIDE)
    if len(b[0]):
        x.plot(b[0][:, 1], b[0][:, 2], "o", ms=9, mfc="none", mec=fs.PAL["blue"],
               label="processors")
    if len(a[0]):
        x.plot(a[0][:, 1], a[0][:, 2], "x", ms=7, color=fs.PAL["red"], label="card")
    x.text(0.03, 0.06, "records of surfaces 1, 2 (card): %d, %d" % (len(a[1]), len(a[2])),
           transform=x.transAxes, fontsize=8)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel("T5: mass of the pair's horizon")
    x.set_xlim(-0.005, 0.025)
    x.set_xticks([0.0, 0.01, 0.02])
    x.set_ylim(1.0, 1.035)
    x.legend(loc="upper right", fontsize=8)
    hc, hp, dcen, dpos = t7d
    x = ax[0, 1]
    for col, lab, c in ((17, "crossed inwards", fs.PAL["blue"]), (20, "crossed outwards", fs.PAL["red"]),
                        (15, "inside", fs.PAL["yellow"])):
        x.plot(hc[:, 0], hc[:, col], color=c, label=lab + " (card)")
        x.plot(hp[:, 0], hp[:, col], color="k", ls=":", lw=1.0)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel("T7: particles (dotted: processors)")
    x.legend(loc="center left", fontsize=7)
    x = ax[1, 0]
    if dcen is not None:
        x.semilogy(hc[:, 0], dcen + 1e-20, "o-", ms=3, color=fs.PAL["blue"],
                   label="tracker centre")
    tp = [t for t, d in dpos if d is not None]
    dp = [d for t, d in dpos if d is not None]
    x.semilogy(tp, np.array(dp) + 1e-20, "s", ms=6, color=fs.PAL["red"],
               label="particles, largest")
    x.axhline(1e-8, **fs.GUIDE)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel("T7: |card - processors|")
    x.legend(loc="center left", fontsize=8)
    x = ax[1, 1]
    for lg, c, lab in ((memlg, fs.PAL["red"], "2700 slots, 32 cycles"),
                       (timlg, fs.PAL["sky"] if "sky" in fs.PAL else fs.PAL["blue"],
                        "2700 slots, timing run")):
        if lg and lg.get("gpumem_series"):
            s = np.array(lg["gpumem_series"])
            x.plot(s[:, 0], s[:, 1]/1e3, color=c, label=lab)
    x.axhspan(PRED_MEM[0]/1e3, PRED_MEM[1]/1e3, color="grey", alpha=0.15)
    x.axhline(MIB_PER_SLOT*2700/1e3, **fs.GUIDE)
    x.axhline(63.059, color="k", ls=":", lw=1.0)
    x.text(0.02, 63.059/80 + 0.01, "2400 slots (earlier run)", transform=x.transAxes, fontsize=7)
    x.set_ylim(0, 80)
    x.set_xlabel("seconds since start")
    x.set_ylabel(r"card memory used [$10^3$ MiB]")
    x.legend(loc="lower right", fontsize=8)
    fs.save(fig, prefix)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t5", required=True)
    ap.add_argument("--t7", required=True)
    ap.add_argument("--mem", required=True)
    ap.add_argument("--mem-timing")
    ap.add_argument("--timing", nargs="*", default=[])
    ap.add_argument("--cpu-t5", required=True)
    ap.add_argument("--cpu-t7", required=True)
    ap.add_argument("--ref-mem", required=True)
    ap.add_argument("--fig")
    a = ap.parse_args()
    res = {"wall": {}}
    for d in [a.t5, a.t7, a.mem] + ([a.mem_timing] if a.mem_timing else []) + a.timing:
        lg = runlog(d)
        res["wall"][d] = {k: v for k, v in lg.items() if k != "gpumem_series"}
    res["t5"], t5d = judge_t5(a.t5, a.cpu_t5)
    res["t7"], t7d = judge_t7(a.t7, a.cpu_t7)
    res["mem2700"], memlg = judge_mem(a.mem, a.ref_mem, a.mem_timing)
    timlg = runlog(a.mem_timing) if a.mem_timing else None
    outdir = os.environ.get("NRPIC_RUN_DIR") or "."
    with open(os.path.join(outdir, "card2_judge.json"), "w") as fp:
        json.dump(res, fp, indent=1, default=str)
        fp.write("\n")
    print(json.dumps(res, indent=1, default=str))
    if a.fig:
        figure(t5d, t7d, memlg, timlg, a.fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
