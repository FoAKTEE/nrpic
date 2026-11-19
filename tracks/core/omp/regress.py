#!/usr/bin/env python3
"""Runs regression set-ups with several configurations (executable, threads, placement)
and compares every output file of each configuration with that of a reference
configuration: byte for byte, and number by number where the bytes differ.

    regress.py --configs S:1 O2:1 O2:4 O2:16 O2:4#2 --ref S:1 [--cases geo,dep,...]
               [--out DIR] [--tol 1e-8] [--pairs O2:4=O2:4#2 ...]

A configuration is EXE:THREADS[:BIND[:PLACES[:MODE]]][#REPEAT] with EXE one of R (release
core-v0.3, serial), S (serial build of this branch), O2 (OpenMP build with the flags of
S), O3 (OpenMP build, -O3 -DNDEBUG), or a path; MODE `priv` writes `deposit_threads =
private` into the <particles> block of the deck; `#k` distinguishes repeats of one
configuration. --pairs adds comparisons between two configurations (repeatability).
--jobs N runs N cases side by side (the caller keeps N x threads within its cores).
Output: DIR/<case>/<config>/ per run, DIR/summary.json, a table on stdout. DIR defaults
to $NRPIC_RUN_DIR (set by nrpic-run). Exit status 0 if no comparison shows a structural
difference (missing file, other size, non-finite number) or a difference above --tol in
the measure rel_floor of omplib.number_diff (each number against itself, with a floor of
1e-6 of the largest number of its file).
"""
import argparse
import concurrent.futures
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import omplib as L  # noqa: E402


def parse(cfg):
    body = cfg.split("#")[0]
    p = body.split(":")
    exe = L.EXES.get(p[0], p[0])
    return dict(label=cfg.replace(":", "_").replace("#", "_r").replace("/", "_"),
                exe=exe, threads=int(p[1]) if len(p) > 1 else 1,
                bind=p[2] if len(p) > 2 else "", places=p[3] if len(p) > 3 else "",
                mode=p[4] if len(p) > 4 else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", nargs="+", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--cases", default=",".join(L.REGRESS))
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--tol", type=float, default=1.0e-8)
    ap.add_argument("--pairs", nargs="*", default=[])
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--reuse", default="",
                    help="output directory of an earlier call: a configuration that has a "
                         "finished run of the case there is not run again")
    a = ap.parse_args()
    if not a.out:
        ap.error("--out or NRPIC_RUN_DIR")
    configs = list(dict.fromkeys([a.ref] + a.configs))
    summary = {"ref": a.ref, "configs": configs, "tol": a.tol, "cases": {},
               "executables": {c: {"path": parse(c)["exe"], "sha256": L.sha256(parse(c)["exe"])}
                               for c in configs}}
    lock = threading.Lock()

    def one_case(case):
        bad = 0
        lines = []
        runs = {}
        for cfg in configs:
            c = parse(cfg)
            rd = os.path.join(a.out, case, c["label"])
            old = os.path.join(a.reuse, case, c["label"]) if a.reuse else ""
            if old and "loop_s" in L.parse_log(os.path.join(old, "run.log")):
                runs[cfg] = dict(case=case, exe=c["exe"], threads=c["threads"], rundir=old,
                                 exit=0, wall_s=0.0, reused=True)
                runs[cfg].update(L.parse_log(os.path.join(old, "run.log")))
                continue
            runs[cfg] = L.run_case(c["exe"], case, rd, c["threads"], c["bind"], c["places"],
                                   mode=c["mode"])
            if runs[cfg]["exit"] != 0:
                bad += 1
        comps = {}
        pairs = [(a.ref, cfg) for cfg in configs if cfg != a.ref]
        pairs += [tuple(p.split("=")) for p in a.pairs]
        for x, y in pairs:
            r = L.compare_dirs(runs[x]["rundir"], runs[y]["rundir"])
            comps["%s vs %s" % (y, x)] = r
            flag = r["structural_difference"] or r["worst_rel_floor"] > a.tol
            bad += 1 if flag else 0
            nd = len(r["differ"])
            lines.append("%-7s %-22s vs %-14s identical %2d  differ %2d  worst %.2e%s  "
                         "[exit %d, %.1f s]" % (
                             case, y, x, len(r["identical"]), nd, r["worst_rel_floor"],
                             "  STRUCTURAL" if r["structural_difference"] else "",
                             runs[y]["exit"], runs[y]["wall_s"]))
            for n, v in sorted(r["differ"].items()):
                lines.append("          %-34s %s" % (
                    n, {k: (("%.2e" % w) if isinstance(w, float) else w)
                        for k, w in v.items()}))
        with lock:
            print("\n".join(lines))
            sys.stdout.flush()
            summary["cases"][case] = {"runs": runs, "comparisons": comps,
                                      "what": L.CASES[case]["what"]}
            L.dump(summary, os.path.join(a.out, "summary.json"))
        return bad

    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        bad = sum(pool.map(one_case, a.cases.split(",")))
    summary["failures"] = bad
    L.dump(summary, os.path.join(a.out, "summary.json"))
    print("failures: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
