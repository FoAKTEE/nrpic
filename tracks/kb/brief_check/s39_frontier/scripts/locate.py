"""Locate phrases in the TeX sources of the knowledge-base store (read-only).

Usage: python3 -I locate.py <spec-file>
Each non-empty line of the spec file: <arxiv id> | <regex> [| <max hits>]
(fields separated by " | " with spaces; a bare "|" inside the regex is alternation)
Prints, for each spec line, the hits as <path relative to kb-data/raw/arxiv>:<line>: <text>
(text cut to 300 characters). Files are read as bytes and decoded leniently; nothing in the
store is executed or imported. Standard library only.
"""
import os
import re
import sys

RAW = "/data/haiyangw/nrpic/kb-data/raw/arxiv"


def src_dirs(aid):
    key = aid.replace("/", "_")
    base = os.path.join(RAW, key)
    if not os.path.isdir(base):
        return []
    vers = sorted(os.listdir(base), key=lambda v: int(v[1:]) if v[1:].isdigit() else 0)
    return [os.path.join(base, v, "src") for v in vers[-1:]]


def tex_files(d):
    out = []
    for root, _dirs, files in os.walk(d):
        for f in sorted(files):
            if f.endswith(".tex"):
                out.append(os.path.join(root, f))
    return out


def main(spec):
    with open(spec) as fh:
        lines = [l.rstrip("\n") for l in fh if l.strip() and not l.startswith("#")]
    for l in lines:
        # fields are separated by " | " (space, bar, space) so that the regex may use "|"
        parts = [p.strip() for p in l.split(" | ")]
        aid = parts[0]
        if len(parts) > 2 and parts[-1].isdigit():
            nmax, pat = int(parts[-1]), " | ".join(parts[1:-1])
        else:
            nmax, pat = 4, " | ".join(parts[1:])
        rx = re.compile(pat, re.I)
        print("### %s  /%s/" % (aid, pat))
        n = 0
        for d in src_dirs(aid):
            for f in tex_files(d):
                with open(f, "rb") as fh:
                    text = fh.read().decode("utf-8", "replace").splitlines()
                for i, t in enumerate(text, 1):
                    if t.lstrip().startswith("%"):
                        continue
                    m = rx.search(t)
                    if m:
                        s = max(0, m.start() - 120)
                        print("  %s:%d: %s" % (os.path.relpath(f, RAW), i, t[s:s + 300]))
                        n += 1
                        if n >= nmax:
                            break
                if n >= nmax:
                    break
        if n == 0:
            print("  (no hit)")


if __name__ == "__main__":
    main(sys.argv[1])
