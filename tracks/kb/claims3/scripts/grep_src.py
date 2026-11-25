#!/usr/bin/env python3
"""Search the stored TeX source of one paper for a pattern (case-insensitive regex), as text.

    python3 -I grep_src.py PAPER_ID PATTERN [--version vN] [--max 20]

Prints file:line: text (cut to 220 characters) to the terminal only; nothing is written. Files
under kb-data/raw are read as text, never executed, imported or compiled. Standard library.
"""
import argparse
import os
import re

RAW = "/data/haiyangw/nrpic/kb-data/raw/arxiv"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper")
    ap.add_argument("pattern")
    ap.add_argument("--version")
    ap.add_argument("--max", type=int, default=20)
    a = ap.parse_args()
    base = os.path.join(RAW, a.paper.replace("/", "_"))
    vers = sorted((v for v in os.listdir(base) if re.fullmatch(r"v\d+", v)), key=lambda v: int(v[1:]))
    ver = a.version or vers[-1]
    src = os.path.join(base, ver, "src")
    rx = re.compile(a.pattern, re.I)
    n = 0
    for root, _dirs, files in os.walk(src):
        for fn in sorted(files):
            if not fn.lower().endswith((".tex", ".bbl", ".ltx", ".txt")):
                continue
            p = os.path.join(root, fn)
            with open(p, errors="replace") as f:
                for i, line in enumerate(f, 1):
                    if rx.search(line):
                        print(f"{os.path.relpath(p, src)}:{i}: {line.rstrip()[:220]}")
                        n += 1
                        if n >= a.max:
                            return 0
    print(f"# {n} hits in {a.paper}{ver}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
