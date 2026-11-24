#!/usr/bin/env python3
"""Does each continuation join its original as one run? (package repro/continue, Track E)

For every label of runs.json that has continuation run ids in conts.json (both beside this
script; conts.json maps a label to the list of its continuation runs, in the order they ran).
A label may have several continuations (a continuation cut by a preemption is continued by the
next one); continuation k starts from the restart file named by `nrpic_resume=` in its launch
record, which is the newest restart of the original or of an earlier continuation. Every check
is made per continuation against everything that ran before it ("earlier" = the original's
segment blocks, then the blocks of continuations 0..k-1):

J1 start: the first record of continuation k has cycle c_k + 1 at t_k + dt (17 digits), the
   first progress line of its first segment log has c_k <= cycle < c_k + 100 and the time
   t_k + (cycle - c_k) dt to the printed seven digits, every printed dt is the restart's dt.
   The label is complete when the last continuation ends "Terminating on time limit".
J2 overlap: on every cycle that continuation k and an earlier block both recorded, the lines of
   <base>.sf.hst and <base>.sf.con.hst are compared as printed (17 digits): identical lines
   counted, the largest relative difference per column reported. Duplicated cycles between the
   original's own blocks are compared the same way.
J3 junction: per column, |x(c_k+1) - x(c_k)| (latest earlier record of cycle c_k, first record
   of continuation k) against the largest change between consecutive records among up to ten
   pairs before and ten after the junction; refuted above 3.
J4 dumps: the first dump number of continuation k is the dump counter stored in the sidecar of
   its restart file, at a time in [next dump time, next dump time + dt]; dumps (and .modes,
   .rmodes files) that continuation k and an earlier run both hold are compared byte for byte;
   the joined dump numbers have no gap.

The joined records are written into the output directory as <label>.sf.hst and
<label>.sf.con.hst (header of the original; for every cycle the line of the latest block that
holds it, blocks in the order original segments, then continuation segments), and
<label>.dumps.tsv lists, per dump number, the file to read (the latest run that has it), its
time and cycle. --next LABEL=PATH also checks the restart file a queued continuation of LABEL
will start from (header, size, sidecar, sha256 against the sha256sums.txt of the run that wrote
it). Writes join_check.json and fig_join.{pdf,png}.

    python3 join_check.py --out DIR [--labels A,B] [--no-bytes] [--next LABEL=PATH]
"""
import argparse
import json
import os
import re
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_restart import parse_rst, parse_sf, recorded_sha, sha256  # noqa: E402

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


def same_bytes(p, q, buf=1 << 24):
    if os.path.getsize(p) != os.path.getsize(q):
        return False
    with open(p, "rb") as f, open(q, "rb") as g:
        while True:
            a, b = f.read(buf), g.read(buf)
            if a != b:
                return False
            if not a:
                return True


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


def resume_of(rundir):
    nres = json.load(open(os.path.join(rundir, ".nrpic", "launch.json")))
    arg = [x for x in nres["argv"] if x.startswith("nrpic_resume=")]
    return arg[0].split("=", 1)[1] if arg else None


def check_next(spec, scratch):
    lab, path = spec.split("=", 1)
    r, s = parse_rst(path), parse_sf(path + ".sf")
    rundir = os.path.dirname(os.path.dirname(path))
    out = {"label": lab, "path": path, "run": os.path.basename(rundir)}
    out["rst"] = {k: r.get(k) for k in ("time", "ncycle", "dt", "size_ok", "no_holes",
                                         "tail_finite", "nz4c", "nz4c_integer", "bytes")}
    out["sf"] = {k: s.get(k) for k in ("magic", "dims", "dump_number", "dump_next_time",
                                        "size_ok", "no_holes", "tail_finite")}
    for p, key in ((path, "rst"), (path + ".sf", "sf")):
        rel = os.path.relpath(p, rundir)
        got, want = sha256(p), recorded_sha(rundir, rel)
        out[key]["sha256"] = got
        out[key]["sha256_recorded"] = want
        out[key]["sha256_ok"] = bool(want) and got == want
    out["ok"] = all([out["rst"]["size_ok"], out["rst"]["no_holes"], out["rst"]["tail_finite"],
                     out["sf"]["size_ok"], out["sf"]["magic"] == "NRSFRST1",
                     out["rst"]["sha256_ok"], out["sf"]["sha256_ok"]])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--labels", default=None)
    ap.add_argument("--no-bytes", action="store_true")
    ap.add_argument("--next", action="append", default=[], help="LABEL=PATH of a queued start")
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
        names = ["orig"] + [f"cont{k + 1}" for k in range(len(Cs))]
        e = {"orig": r["orig"], "conts": conts[lab]}
        rsts, sfs = [], []
        for C in Cs:
            rp = resume_of(C)
            rsts.append(parse_rst(rp))
            sfs.append(parse_sf(rp + ".sf"))
        e["restarts"] = [{"run": os.path.basename(C), **{k: rh[k] for k in
                          ("path", "time", "ncycle", "dt", "tlim")},
                          "sf_dump_number": sf["dump_number"], "sf_dump_next_time": sf["dump_next_time"]}
                         for C, rh, sf in zip(Cs, rsts, sfs)]
        # J1 (as amended in journal entry 3), per continuation
        j1 = []
        for C, rh in zip(Cs, rsts):
            logs = seg_logs(C)
            first, _, _ = progress(logs[0]) if logs else ([], None, None)
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
            # a continuation cut before its first progress line is judged on its record only
            start_ok = rec_ok and (log_ok or f0 is None)
            j1.append({"run": os.path.basename(C), "first_log_line": f0, "first_record": rec0,
                       "rst_cycle": rh["ncycle"], "rst_time": rh["time"], "rst_dt": rh["dt"],
                       "log_start_ok": log_ok, "record_start_ok": rec_ok, "start_ok": start_ok,
                       "dt_values": dts,
                       "dt_ok": all(abs(d - rh["dt"]) <= 5e-7 * rh["dt"] for d in dts),
                       "logs": [os.path.basename(x) for x in logs], "termination": term,
                       "final": final})
        e["J1"] = j1
        e["J1_start_pass"] = all(x["start_ok"] and x["dt_ok"] for x in j1)
        e["complete"] = bool(j1[-1]["termination"] and "time limit" in j1[-1]["termination"])
        e["J1_pass"] = e["J1_start_pass"] and e["complete"]
        # J2, J3 and the joined records
        e["records"] = {}
        for kind in ("sf.hst", "sf.con.hst"):
            ho, bo = read_blocks(os.path.join(O, f"{r['base']}.{kind}"))
            cblocks = []
            for C in Cs:
                p = os.path.join(C, f"{r['base']}.{kind}")
                hc, bc = read_blocks(p) if os.path.exists(p) else ([], [])
                cblocks.append((bc, bool(hc)))
            rec = {"orig_blocks": [[min(b), max(b)] for b in bo],
                   "cont_blocks": [[[min(b), max(b)] for b in bc] for bc, _ in cblocks],
                   "cont_has_header": [h for _, h in cblocks]}
            earlier = [(f"orig[{i}]", b) for i, b in enumerate(bo)]
            rec["overlap"], rec["junction"] = [], []
            for k, (bc, _) in enumerate(cblocks):
                c_k = rsts[k]["ncycle"]
                mine = [(f"{names[k + 1]}[{i}]", b) for i, b in enumerate(bc)]
                # J2: every block of continuation k against every earlier block and its own
                for i, (nb, b) in enumerate(mine):
                    for ne, eb in earlier + mine[:i]:
                        cyc = sorted(set(b) & set(eb))
                        if cyc:
                            d = compare_lines(eb, b, cyc)
                            d["pair"] = [ne, nb]
                            rec["overlap"].append(d)
                # J3 at the junction of continuation k
                lineage = {}
                for _, eb in earlier:
                    for c, line in eb.items():
                        if c <= c_k:
                            lineage[c] = line
                post_d = bc[0] if bc else {}
                pre = [vals(lineage[c]) for c in sorted(lineage)[-11:]]
                post = [vals(post_d[c]) for c in sorted(post_d)[:11]]
                if pre and post:
                    jump = np.abs(post[0] - pre[-1])
                    diffs = [np.abs(np.diff(np.array(pre), axis=0))] if len(pre) > 1 else []
                    if len(post) > 1:
                        diffs.append(np.abs(np.diff(np.array(post), axis=0)))
                    if diffs:
                        ref = np.max(np.vstack(diffs), axis=0)
                        ratio = np.where(ref > 0, jump / np.where(ref > 0, ref, 1.0),
                                         np.where(jump > 0, np.inf, 0.0))
                        ratio[:2] = 0.0          # time and cycle columns
                        jn = {"cont": names[k + 1], "last_before": sorted(lineage)[-1],
                              "first_after": min(post_d),
                              "pairs_before": len(pre) - 1, "pairs_after": len(post) - 1,
                              "max_ratio": float(np.max(ratio)),
                              "worst_column": int(np.argmax(ratio)) + 1,
                              "ratio_per_column": ratio.tolist()}
                        # the same measure on the earlier run's own step across c_k (journal
                        # entry 11): the latest earlier block that recorded c_k + 1, with as
                        # many lines after c_k as the continuation offers
                        cand = [(ne, eb) for ne, eb in earlier if c_k + 1 in eb]
                        full = [x for x in cand if sum(1 for c in x[1] if c > c_k) >= len(post)]
                        for ne, eb in (full or cand)[-1:]:
                            if True:
                                pe = [vals(eb[c]) for c in sorted(c for c in eb if c > c_k)[:len(post)]]
                                jump_e = np.abs(pe[0] - pre[-1])
                                de = list(diffs[:1]) if len(pre) > 1 else []
                                if len(pe) > 1:
                                    de.append(np.abs(np.diff(np.array(pe), axis=0)))
                                if de:
                                    ref_e = np.max(np.vstack(de), axis=0)
                                    ratio_e = np.where(ref_e > 0, jump_e / np.where(ref_e > 0, ref_e, 1.0),
                                                       np.where(jump_e > 0, np.inf, 0.0))
                                    ratio_e[:2] = 0.0
                                    jn.update({"earlier_block": ne, "earlier_max_ratio": float(np.max(ratio_e)),
                                               "earlier_ratio_per_column": ratio_e.tolist(),
                                               "same_as_earlier": bool(np.array_equal(ratio, ratio_e))})
                                break
                        jn["literal_ok"] = jn["max_ratio"] <= 3.0
                        jn["ok"] = jn["literal_ok"] or bool(jn.get("same_as_earlier"))
                        rec["junction"].append(jn)
                earlier += mine
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
            for _, b in earlier:
                joined.update(b)
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
                plotdata[lab] = {"bo": bo, "cb": [bc for bc, _ in cblocks],
                                 "c": [rh["ncycle"] for rh in rsts]}
        e["J2_pass"] = all(o["identical"] == o["n"] for rec in e["records"].values()
                           for o in rec["overlap"])
        e["J2_max_rel"] = max([o["max_rel_diff"] for rec in e["records"].values()
                               for o in rec["overlap"]] or [0.0])
        e["J2_lines"] = [sum(o["n"] for rec in e["records"].values() for o in rec["overlap"]),
                         sum(o["identical"] for rec in e["records"].values() for o in rec["overlap"])]
        e["J3_literal_pass"] = all(j["literal_ok"] for rec in e["records"].values()
                                   for j in rec["junction"])
        e["J3_pass"] = all(j["ok"] for rec in e["records"].values() for j in rec["junction"])
        e["J3_max_ratio"] = max([j["max_ratio"] for rec in e["records"].values()
                                 for j in rec["junction"]] or [0.0])
        e["records_gapless"] = all(not rec["joined"]["gaps"] for rec in e["records"].values())
        # J4 dumps
        do = dumps_of(O, r["base"])
        dcs = [dumps_of(C, r["base"]) for C in Cs]
        runs_d = [("orig", O, do)] + [(names[k + 1], C, d) for k, (C, d) in enumerate(zip(Cs, dcs))]
        j4 = {"orig_numbers": [min(do), max(do)] if do else None, "conts": [], "common": []}
        firsts_ok = True
        for k, (C, d) in enumerate(zip(Cs, dcs)):
            item = {"cont": names[k + 1], "numbers": [min(d), max(d)] if d else None,
                    "expected_first": sfs[k]["dump_number"],
                    "expected_time_from": sfs[k]["dump_next_time"]}
            if d:
                h = dump_header(d[min(d)])
                item["first_header"] = h
                item["first_ok"] = bool(min(d) == sfs[k]["dump_number"] and
                                        sfs[k]["dump_next_time"] - 1e-12 <= h["time"]
                                        <= sfs[k]["dump_next_time"] + rsts[k]["dt"] + 1e-12)
                firsts_ok = firsts_ok and item["first_ok"]
            else:
                item["first_ok"] = None          # cut before its first dump
            j4["conts"].append(item)
            for nm, R, de in runs_d[:k + 1]:
                for n in sorted(set(de) & set(d)):
                    it = {"number": n, "pair": [nm, names[k + 1]],
                          "a": dump_header(de[n]), "b": dump_header(d[n])}
                    if not a.no_bytes:
                        it["dump_identical"] = same_bytes(de[n], d[n])
                        for ext in ("modes", "rmodes"):
                            po, pc = de[n][:-4] + ext, d[n][:-4] + ext
                            if os.path.exists(po) and os.path.exists(pc):
                                it[f"{ext}_identical"] = same_bytes(po, pc)
                    j4["common"].append(it)
        rows = {}
        for _, _, d in runs_d:
            rows.update(d)
        with open(os.path.join(a.out, f"{lab}.dumps.tsv"), "w") as f:
            f.write("# number\ttime\tcycle\tfile (latest run that has it)\n")
            for n in sorted(rows):
                h = dump_header(rows[n])
                f.write(f"{n:05d}\t{h['time']:.12f}\t{h['cycle']}\t{rows[n]}\n")
        j4["joined_numbers"] = [min(rows), max(rows)] if rows else None
        j4["joined_gaps"] = [n for n in range(min(rows), max(rows) + 1) if n not in rows] if rows else None
        e["J4"] = j4
        e["J4_pass"] = bool(firsts_ok and any(dcs) and all(
            it.get("dump_identical", True) and it.get("modes_identical", True)
            and it.get("rmodes_identical", True) for it in j4["common"])
            and not j4["joined_gaps"])
        res[lab] = e
        print(f"{lab}: complete {e['complete']}; J1 start {e['J1_start_pass']} "
              f"({[(x['run'][-7:], x['first_record'], x['rst_cycle'], x['termination']) for x in j1]}); "
              f"J2 {e['J2_pass']} ({e['J2_lines'][1]} of {e['J2_lines'][0]} lines identical, max rel {e['J2_max_rel']:.3g}); "
              f"J3 {e['J3_pass']} (literal {e['J3_literal_pass']}, max ratio {e['J3_max_ratio']:.3g}, "
              f"earlier run's own step {[(j['cont'], j.get('earlier_block'), round(j.get('earlier_max_ratio', float('nan')), 3), j.get('same_as_earlier')) for rec in e['records'].values() for j in rec['junction']]}); "
              f"J4 {e['J4_pass']} (orig {j4['orig_numbers']}, conts {[c['numbers'] for c in j4['conts']]}, "
              f"common {[(it['number'], it['pair'][0], it['pair'][1], it.get('dump_identical')) for it in j4['common']]}); "
              f"joined records {e['records']['sf.hst']['joined']['first']}-{e['records']['sf.hst']['joined']['last']}, "
              f"dumps {j4['joined_numbers']}, gaps {j4['joined_gaps']}")
    out = {"labels": res}
    if a.next:
        out["next"] = [check_next(s, a.scratch) for s in a.next]
        for n in out["next"]:
            print(f"next {n['label']}: {n['path']}: t {n['rst']['time']}, cycle {n['rst']['ncycle']}, "
                  f"dump counter {n['sf']['dump_number']} (next {n['sf']['dump_next_time']}), ok {n['ok']}")
    json.dump(out, open(os.path.join(a.out, "join_check.json"), "w"), indent=1, default=str)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    n = len(plotdata)
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.8))
    w = 0.88 / max(n, 1)
    colors = [fs.PAL["red"], fs.PAL["green"], fs.PAL["orange"], fs.PAL["yellow"]]
    for i, (lab, d) in enumerate(plotdata.items()):
        cs = d["c"]
        lo, hi = min(cs) - 40, max(cs) + 60
        ax = fig.add_axes([0.08 + i * w + 0.01, 0.56, w - 0.035, 0.36])
        ax2 = fig.add_axes([0.08 + i * w + 0.01, 0.10, w - 0.035, 0.36])
        earlier = {}
        for k, b in enumerate(d["bo"]):
            cyc = np.array(sorted(c for c in b if lo <= c <= hi))
            if len(cyc):
                y = np.array([vals(b[c])[3] for c in cyc])
                ax.plot(cyc, y, color=fs.PAL["blue"], lw=2.0,
                        label="original" if k == len(d["bo"]) - 1 else None)
            earlier.update(b)
        nid, nall = 0, 0
        for k, bc in enumerate(d["cb"]):
            merged = {}
            for b in bc:
                merged.update(b)
            col = colors[k % len(colors)]
            cyc = np.array(sorted(c for c in merged if lo <= c <= hi))
            if len(cyc):
                y = np.array([vals(merged[c])[3] for c in cyc])
                ax.plot(cyc, y, color=col, lw=1.2, ls="--", label=f"cont. {k + 1}")
            oc = [c for c in sorted(merged) if c in earlier and lo <= c <= hi]
            if oc:
                diff = [abs(vals(merged[c])[3] - vals(earlier[c])[3]) / abs(vals(earlier[c])[3]) for c in oc]
                ax2.semilogy(oc, np.maximum(np.array(diff), 1e-18), "o", color=col, ms=2.0)
            ocall = [c for c in merged if c in earlier]
            nid += sum(merged[c] == earlier[c] for c in ocall)
            nall += len(ocall)
            earlier.update(merged)
        ax2.text(0.04, 0.92, f"{nid} of {nall} lines\nidentical", transform=ax2.transAxes,
                 fontsize=7, va="top")
        for x in (ax, ax2):
            for c in sorted(set(cs)):
                x.axvline(c + 0.5, color="k", lw=1.0, ls=":")
            x.set_xlim(lo, hi)
        ax2.set_yscale("log")
        ax2.set_ylim(1e-19, 1e-9)
        ax2.axhline(1e-12, color="k", lw=1.0, ls="--")
        ax.set_title(lab, fontsize=10)
        ax.tick_params(labelsize=7)
        ax2.tick_params(labelsize=7)
        ax2.set_xlabel("cycle", labelpad=-1, fontsize=8)
        ax.legend(loc="lower left", fontsize=6)
        if i == 0:
            ax.set_ylabel(r"record $\langle|H|/[H]\rangle$", fontsize=8)
            ax2.set_ylabel("|cont - earlier| / earlier\n(floor 1e-18)", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_join"))
    print("wrote", os.path.join(a.out, "join_check.json"))


if __name__ == "__main__":
    main()
