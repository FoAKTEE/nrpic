#!/usr/bin/env python3
"""Does each continuation join its original as one run? (package repro/continue, Track E)

For every label of runs.json that has continuation run ids in conts.json (both beside this
script; conts.json maps a label to the list of its continuation runs, in order):

J1 start: the first progress line of the continuation's first segment log has the cycle and
   time of the restart header, every progress line has the restart's dt, and the last
   segment ends with "Terminating on time limit" at tlim.
J2 overlap: on every cycle that the original (any of its segment blocks) and a continuation
   both recorded after the restart cycle, the lines of <base>.sf.hst and <base>.sf.con.hst
   are compared as printed (17 digits): identical lines counted, the largest relative
   difference per column reported. Duplicated cycles between blocks of the original itself
   are compared the same way.
J3 junction: per column, |x(c_rst+1) - x(c_rst)| (last record of the lineage up to the restart,
   first record of the continuation) against the largest change between consecutive records
   among up to ten pairs before and ten after the junction; refuted above 3.
J4 dumps: numbers and times of the continuation's dumps continue the original's; dumps (and
   .modes, .rmodes files) present in both directories are compared byte for byte.

The joined records are written into the output directory as <label>.sf.hst and
<label>.sf.con.hst (header of the original; for every cycle the line of the latest block that
holds it, blocks in the order original segments, then continuation segments), and
<label>.dumps.tsv lists, per dump number, the file to read (the latest run that has it), its
time and cycle. Writes join_check.json and fig_join.{pdf,png}.

    python3 join_check.py --out DIR [--labels A,B] [--no-bytes]
"""
import argparse
import filecmp
import json
import os
import re
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_restart import parse_rst  # noqa: E402

SCRATCH = "/data/haiyangw/nrpic/scratch/E-stoch-inf"
PROG = re.compile(r"cycle=(\d+) time=([-+0-9.eE]+) dt=([-+0-9.eE]+)")


def read_blocks(path):
    """header lines and the data lines split into blocks at every rewind of the cycle"""
    head, blocks = [], []
    prev = None
    for line in open(path):
        if line.startswith("#"):
            head.append(line)
            continue
        if not line.strip():
            continue
        c = int(line.split()[1])
        if prev is None or c <= prev:
            blocks.append({})
        blocks[-1][c] = line
        prev = c
    return head, blocks


def vals(line):
    return np.array([float(x) for x in line.split()])


def compare_lines(a, b, cycles):
    """a, b: dict cycle -> line; on the given cycles: identical count, max rel diff/column"""
    same, worst = 0, None
    for c in cycles:
        if a[c] == b[c]:
            same += 1
        va, vb = vals(a[c]), vals(b[c])
        den = np.maximum(np.abs(va), np.abs(vb))
        rel = np.where(den > 0, np.abs(va - vb) / np.where(den > 0, den, 1.0), 0.0)
        worst = rel if worst is None else np.maximum(worst, rel)
    return {"cycles": [min(cycles), max(cycles)] if cycles else None, "n": len(cycles),
            "identical": same, "max_rel_diff": float(worst.max()) if worst is not None else None,
            "max_rel_diff_per_column": worst.tolist() if worst is not None else None}


def progress(log):
    rows, term, final = [], None, None
    for line in open(log, errors="replace"):
        m = PROG.search(line)
        if m and (line.startswith("elapsed=") or line.startswith("cycle=")):
            rows.append((int(m.group(1)), float(m.group(2)), float(m.group(3))))
        if line.startswith("Terminating on"):
            term = line.strip()
        if line.startswith("time=") and "cycle=" in line:
            final = line.strip()
    return rows, term, final


def seg_logs(rundir):
    c = os.path.join(rundir, "chain")
    return [os.path.join(c, f) for f in sorted(os.listdir(c))
            if re.match(r"seg\d+\.job\d+\.a\d+\.log$", f)]


def dump_header(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack("<7q", f.read(56))
        (time,) = struct.unpack("<d", f.read(8))
    return {"magic": magic.decode("ascii", "replace"), "nvar": nvar, "nnoise": nnoise,
            "cycle": cycle, "time": time}


def dumps_of(rundir, base):
    out = {}
    for f in os.listdir(rundir):
        m = re.fullmatch(re.escape(base) + r"\.sf\.(\d{5})\.dump", f)
        if m:
            out[int(m.group(1))] = os.path.join(rundir, f)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--labels", default=None)
    ap.add_argument("--no-bytes", action="store_true")
    ap.add_argument("--scratch", default=SCRATCH, help="parent of the run directories (tests)")
    ap.add_argument("--runs", default=os.path.join(HERE, "runs.json"))
    ap.add_argument("--conts", default=os.path.join(HERE, "conts.json"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    runs = json.load(open(a.runs))
    conts = json.load(open(a.conts))
    labels = a.labels.split(",") if a.labels else [l for l in runs if conts.get(l)]
    res = {}
    plotdata = {}
    for lab in labels:
        r = runs[lab]
        O = os.path.join(a.scratch, r["orig"])
        Cs = [os.path.join(a.scratch, c) for c in conts[lab]]
        e = {"orig": r["orig"], "conts": conts[lab], "segments": []}
        # restart each continuation started from: the newest of the run before it
        srcs = [O] + Cs[:-1]
        rsts = []
        for i, C in enumerate(Cs):
            nres = json.load(open(os.path.join(C, ".nrpic", "launch.json")))
            arg = [x for x in nres["argv"] if x.startswith("nrpic_resume=")]
            rp = arg[0].split("=", 1)[1] if arg else None
            rsts.append(parse_rst(rp))
        r0 = rsts[0]
        e["restart"] = {k: r0[k] for k in ("path", "time", "ncycle", "dt", "tlim")}
        # J1 (as amended in journal entry 3): AthenaK prints a progress line only every
        # ndiag cycles and with 7 digits, so the log is checked to its printed precision
        # and the exact start from the first record (cycle c_rst + 1 at t_rst + dt)
        j1 = []
        for C, rh in zip(Cs, rsts):
            logs = seg_logs(C)
            first, _, _ = progress(logs[0])
            allrows, term, final = [], None, None
            for lg in logs:
                rows, t, fi = progress(lg)
                allrows += rows
                term, final = t or term, fi or final
            dts = sorted({d for _, _, d in allrows})
            f0 = first[0] if first else None
            log_ok = bool(f0 and rh["ncycle"] <= f0[0] < rh["ncycle"] + 100 and
                          abs(f0[1] - (rh["time"] + (f0[0] - rh["ncycle"]) * rh["dt"]))
                          <= 5e-7 * max(1.0, abs(f0[1])))
            recp = os.path.join(C, f"{r['base']}.sf.con.hst")
            rec0 = None
            if os.path.exists(recp):
                for line in open(recp):
                    if not line.startswith("#") and line.strip():
                        rec0 = (float(line.split()[0]), int(line.split()[1]))
                        break
            rec_ok = bool(rec0 and rec0[1] == rh["ncycle"] + 1
                          and abs(rec0[0] - (rh["time"] + rh["dt"])) <= 1e-15 * abs(rec0[0]))
            j1.append({"run": os.path.basename(C), "first_log_line": f0, "first_record": rec0,
                       "rst_cycle": rh["ncycle"], "rst_time": rh["time"], "rst_dt": rh["dt"],
                       "log_start_ok": log_ok, "record_start_ok": rec_ok,
                       "start_ok": log_ok and rec_ok,
                       "dt_values": dts,
                       "dt_ok": bool(dts) and all(abs(d - rh["dt"]) <= 5e-7 * rh["dt"] for d in dts),
                       "logs": [os.path.basename(x) for x in logs], "termination": term,
                       "final": final})
        e["J1"] = j1
        e["J1_pass"] = all(x["start_ok"] and x["dt_ok"] for x in j1) and \
            bool(j1[-1]["termination"] and "time limit" in j1[-1]["termination"])
        # J2, J3 and the joined records
        e["records"] = {}
        for kind in ("sf.hst", "sf.con.hst"):
            ho, bo = read_blocks(os.path.join(O, f"{r['base']}.{kind}"))
            cblocks = []
            for C in Cs:
                p = os.path.join(C, f"{r['base']}.{kind}")
                hc, bc = read_blocks(p) if os.path.exists(p) else ([], [])
                cblocks.append(bc)
            rec = {"orig_blocks": [[min(b), max(b)] for b in bo],
                   "cont_blocks": [[[min(b), max(b)] for b in bc] for bc in cblocks],
                   "cont_has_header": False}
            c_rst = r0["ncycle"]
            # overlap of each original block (cycles > c_rst) with the first continuation
            first_c = {}
            for b in cblocks[0]:
                first_c.update(b)
            rec["overlap"] = []
            for i, b in enumerate(bo):
                cyc = sorted(c for c in b if c > c_rst and c in first_c)
                if cyc:
                    d = compare_lines(b, first_c, cyc)
                    d["orig_block"] = i
                    rec["overlap"].append(d)
            # duplicates between the original's own blocks
            rec["orig_duplicates"] = []
            for i in range(len(bo)):
                for j in range(i + 1, len(bo)):
                    cyc = sorted(set(bo[i]) & set(bo[j]))
                    if cyc:
                        d = compare_lines(bo[i], bo[j], cyc)
                        d["blocks"] = [i, j]
                        rec["orig_duplicates"].append(d)
            # joined: latest block holding each cycle
            joined = {}
            for b in bo:
                joined.update(b)
            for bc in cblocks:
                for b in bc:
                    joined.update(b)
            lineage = {}
            for b in bo:
                for c, line in b.items():
                    if c <= c_rst:
                        lineage[c] = line
            # J3 at the junction
            pre = [vals(lineage[c]) for c in sorted(lineage)[-11:]]
            post = [vals(first_c[c]) for c in sorted(first_c)[:11]]
            if pre and post:
                jump = np.abs(post[0] - pre[-1])
                diffs = [np.abs(np.diff(np.array(pre), axis=0))] if len(pre) > 1 else []
                if len(post) > 1:
                    diffs.append(np.abs(np.diff(np.array(post), axis=0)))
                ref = np.max(np.vstack(diffs), axis=0)
                ratio = np.where(ref > 0, jump / np.where(ref > 0, ref, 1.0),
                                 np.where(jump > 0, np.inf, 0.0))
                ratio[:2] = 0.0          # time and cycle columns
                rec["junction"] = {"last_before": sorted(lineage)[-1], "first_after": min(first_c),
                                   "max_ratio": float(np.max(ratio)),
                                   "worst_column": int(np.argmax(ratio)) + 1,
                                   "ratio_per_column": ratio.tolist()}
            outp = os.path.join(a.out, f"{lab}.{kind}")
            with open(outp, "w") as f:
                f.writelines(ho)
                for c in sorted(joined):
                    f.write(joined[c])
            cyc = sorted(joined)
            rec["joined"] = {"file": outp, "lines": len(cyc), "first": cyc[0], "last": cyc[-1],
                             "gaps": [c for c in range(cyc[0], cyc[-1] + 1) if c not in joined][:20]}
            e["records"][kind] = rec
            if kind == "sf.con.hst":
                plotdata[lab] = {"bo": bo, "cb": cblocks, "c_rst": c_rst}
        e["J2_pass"] = all(o["identical"] == o["n"] for rec in e["records"].values()
                           for o in rec["overlap"])
        e["J2_max_rel"] = max([o["max_rel_diff"] for rec in e["records"].values()
                               for o in rec["overlap"]] or [0.0])
        e["J3_pass"] = all(rec.get("junction", {}).get("max_ratio", 0.0) <= 3.0
                           for rec in e["records"].values())
        # J4 dumps
        do = dumps_of(O, r["base"])
        dcs = [dumps_of(C, r["base"]) for C in Cs]
        dc0 = dcs[0]
        first_num = min(dc0) if dc0 else None
        e["J4"] = {"orig_numbers": [min(do), max(do)] if do else None,
                   "cont_numbers": [[min(d), max(d)] if d else None for d in dcs],
                   "expected_first": None, "common": []}
        sf = rsts[0]
        e["J4"]["first_cont_dump"] = dump_header(dc0[first_num]) if dc0 else None
        common = sorted(set(do) & set(dc0))
        for n in common:
            item = {"number": n, "orig": dump_header(do[n]), "cont": dump_header(dc0[n])}
            if not a.no_bytes:
                item["dump_identical"] = filecmp.cmp(do[n], dc0[n], shallow=False)
                for ext in ("modes", "rmodes"):
                    po = do[n][:-4] + ext
                    pc = dc0[n][:-4] + ext
                    if os.path.exists(po) and os.path.exists(pc):
                        item[f"{ext}_identical"] = filecmp.cmp(po, pc, shallow=False)
            e["J4"]["common"].append(item)
        # joined dump list
        rows = {}
        for n, p in do.items():
            rows[n] = p
        for d in dcs:
            for n, p in d.items():
                rows[n] = p
        with open(os.path.join(a.out, f"{lab}.dumps.tsv"), "w") as f:
            f.write("# number\ttime\tcycle\tfile (latest run that has it)\n")
            for n in sorted(rows):
                h = dump_header(rows[n])
                f.write(f"{n:05d}\t{h['time']:.12f}\t{h['cycle']}\t{rows[n]}\n")
        e["J4"]["joined_numbers"] = [min(rows), max(rows)] if rows else None
        e["J4"]["joined_gaps"] = [n for n in range(min(rows), max(rows) + 1) if n not in rows] if rows else None
        e["J4_pass"] = bool(dc0 and (not common or all(
            it.get("dump_identical", True) and it.get("modes_identical", True)
            and it.get("rmodes_identical", True) for it in e["J4"]["common"]))
            and not e["J4"]["joined_gaps"])
        res[lab] = e
        print(f"{lab}: J1 {e['J1_pass']} (log {j1[0]['first_log_line']}, record {j1[0]['first_record']}, rst cycle {j1[0]['rst_cycle']}, "
              f"dt {j1[0]['dt_values']}, {j1[-1]['termination']}); J2 {e['J2_pass']} "
              f"(max rel {e['J2_max_rel']:.3g}; overlaps "
              + ", ".join(f"{k}:{[(o['n'], o['identical']) for o in v['overlap']]}"
                          for k, v in e["records"].items())
              + f"); J3 {e['J3_pass']} ("
              + ", ".join(f"{k}:{v.get('junction', {}).get('max_ratio', float('nan')):.3g}"
                          for k, v in e["records"].items())
              + f"); J4 {e['J4_pass']} (orig {e['J4']['orig_numbers']}, cont {e['J4']['cont_numbers']}, "
              f"common {[(it['number'], it.get('dump_identical')) for it in e['J4']['common']]})")
    json.dump(res, open(os.path.join(a.out, "join_check.json"), "w"), indent=1, default=str)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    n = len(plotdata)
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.6))
    w = 0.86 / max(n, 1)
    for i, (lab, d) in enumerate(plotdata.items()):
        c_rst = d["c_rst"]
        lo, hi = c_rst - 40, c_rst + 60
        ax = fig.add_axes([0.08 + i * w + 0.01, 0.55, w - 0.035, 0.38])
        ax2 = fig.add_axes([0.08 + i * w + 0.01, 0.10, w - 0.035, 0.38])
        for k, b in enumerate(d["bo"]):
            cyc = np.array(sorted(c for c in b if lo <= c <= hi))
            if len(cyc) == 0:
                continue
            y = np.array([vals(b[c])[3] for c in cyc])
            ax.plot(cyc, y, color=fs.PAL["blue"], lw=1.5, label="original" if k == len(d["bo"]) - 1 else None)
        merged = {}
        for b in d["cb"][0]:
            merged.update(b)
        cyc = np.array(sorted(c for c in merged if lo <= c <= hi))
        if len(cyc):
            y = np.array([vals(merged[c])[3] for c in cyc])
            ax.plot(cyc, y, color=fs.PAL["red"], lw=1.5, ls="--", label="continuation")
            # difference to the original on the overlap (latest original block holding it)
            ob = {}
            for b in d["bo"]:
                ob.update(b)
            oc = [c for c in cyc if c in ob]
            if oc:
                diff = [abs(vals(merged[c])[3] - vals(ob[c])[3]) / abs(vals(ob[c])[3]) for c in oc]
                diff = np.maximum(np.array(diff), 1e-18)
                ax2.semilogy(oc, diff, "o", color=fs.PAL["red"], ms=2.5)
                ax2.text(0.04, 0.9, f"{sum(merged[c] == ob[c] for c in oc)} of {len(oc)} lines identical",
                         transform=ax2.transAxes, fontsize=7, va="top")
            else:
                ax2.text(0.04, 0.9, "no overlap", transform=ax2.transAxes, fontsize=7, va="top")
        for x in (ax, ax2):
            x.axvline(c_rst + 0.5, color="k", lw=1.0, ls=":")
            x.set_xlim(lo, hi)
        ax2.set_ylim(1e-19, 1e-9)
        ax2.axhline(1e-12, color="k", lw=1.0, ls="--")
        ax.set_title(lab, fontsize=10)
        ax.tick_params(labelsize=7)
        ax2.tick_params(labelsize=7)
        ax2.set_xlabel("cycle", labelpad=-1, fontsize=8)
        if i == 0:
            ax.set_ylabel(r"record $\langle|H|/[H]\rangle$", fontsize=8)
            ax2.set_ylabel("|cont - orig| / orig\n(floor 1e-18)", fontsize=8)
            ax.legend(loc="lower left", fontsize=7)
    fs.save(fig, os.path.join(a.out, "fig_join"))
    print("wrote", os.path.join(a.out, "join_check.json"))


if __name__ == "__main__":
    main()
