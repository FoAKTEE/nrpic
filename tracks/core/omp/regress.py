#!/usr/bin/env python3
"""Runs regression set-ups with several configurations (executable, threads, placement)
and compares every output file of each configuration with that of a reference
configuration: byte for byte, and number by number where the bytes differ.

    regress.py --configs S:1 O2:1 O2:4 O2:16 O2:4#2 --ref S:1 [--cases geo,dep,...]
               [--out DIR] [--tol 1e-8] [--pairs O2:4=O2:4#2 ...]

A configuration is EXE:THREADS[:BIND[:PLACES]][#REPEAT] with EXE one of R (release
core-v0.3, serial), S (serial build of this branch), O2 (OpenMP build with the flags of
S), O3 (OpenMP build, -O3 -DNDEBUG), or a path; `#k` distinguishes repeats of one
configuration. --pairs adds comparisons between two configurations (repeatability).
Output: DIR/<case>/<config>/ per run, DIR/summary.json, a table on stdout. DIR defaults
to $NRPIC_RUN_DIR (set by nrpic-run). Exit status 0 if no comparison shows a structural
difference (missing file, other size, non-finite number) or a difference above --tol
relative to the largest number of the file.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import omplib as L  # noqa: E402


def parse(cfg):
    body = cfg.split("#")[0]
    p = body.split(":")
    exe = L.EXES.get(p[0], p[0])
    return dict(label=cfg.replace(":", "_").replace("#", "_r").replace("/", "_"),
                exe=exe, threads=int(p[1]) if len(p) > 1 else 1,
                bind=p[2] if len(p) > 2 else "", places=p[3] if len(p) > 3 else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", nargs="+", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--cases", default=",".join(L.REGRESS))
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--tol", type=float, default=1.0e-8)
    ap.add_argument("--pairs", nargs="*", default=[])
    a = ap.parse_args()
    if not a.out:
        ap.error("--out or NRPIC_RUN_DIR")
    configs = list(dict.fromkeys([a.ref] + a.configs))
    summary = {"ref": a.ref, "configs": configs, "tol": a.tol, "cases": {},
               "executables": {c: {"path": parse(c)["exe"], "sha256": L.sha256(parse(c)["exe"])}
                               for c in configs}}
    bad = 0
    for case in a.cases.split(","):
        runs = {}
        for cfg in configs:
            c = parse(cfg)
            rd = os.path.join(a.out, case, c["label"])
            runs[cfg] = L.run_case(c["exe"], case, rd, c["threads"], c["bind"], c["places"])
            if runs[cfg]["exit"] != 0:
                bad += 1
        comps = {}
        pairs = [(a.ref, cfg) for cfg in configs if cfg != a.ref]
        pairs += [tuple(p.split("=")) for p in a.pairs]
        for x, y in pairs:
            r = L.compare_dirs(runs[x]["rundir"], runs[y]["rundir"])
            comps["%s vs %s" % (y, x)] = r
            flag = r["structural_difference"] or r["worst_rel_file"] > a.tol
            bad += 1 if flag else 0
            nd = len(r["differ"])
            print("%-7s %-22s vs %-10s identical %2d  differ %2d  worst %.2e%s  [exit %d, "
                  "%.1f s]" % (case, y, x, len(r["identical"]), nd, r["worst_rel_file"],
                               "  STRUCTURAL" if r["structural_difference"] else "",
                               runs[y]["exit"], runs[y]["wall_s"]))
            for n, v in sorted(r["differ"].items()):
                print("          %-34s %s" % (n, {k: (("%.2e" % w) if isinstance(w, float)
                                                     else w) for k, w in v.items()}))
            sys.stdout.flush()
        summary["cases"][case] = {"runs": runs, "comparisons": comps,
                                  "what": L.CASES[case]["what"]}
        L.dump(summary, os.path.join(a.out, "summary.json"))
    summary["failures"] = bad
    L.dump(summary, os.path.join(a.out, "summary.json"))
    print("failures: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
