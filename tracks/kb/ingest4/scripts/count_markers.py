#!/usr/bin/env python3
"""Independent count of the entries of the six old-style reference lists (prediction P6 of
JOURNAL.md), written before the parser ran on them. For each paper a marker chosen by reading the
source (journal entry 1) is counted on the lines after the paper's 'References' heading line, up
to the end marker named here; numeric lists also give their largest number. Reads the build copy
kb-data/build/tex/<key>/flat.tex (kb's own output, data) with the standard library only.

    python3 -I tracks/kb/ingest4/scripts/count_markers.py --out DIR
"""
import argparse
import os
import re

ROOT = "/data/haiyangw/nrpic/kb-data/build/tex"
# key: (heading regex, entry-marker regex at line start, end regex)
SPEC = {
    "astro-ph/0306304": (r"^References\s*$", r"^\s*\\item\b", r"\\end\{enumerate\}"),
    "astro-ph/9306009": (r"\\centerline\{\\bf References\}", r"^\\i\\[A-Za-z]+", r"\\centerline\{\\bf Figure captions\}"),
    "astro-ph/9510056": (r"\\begref\{References\}", r"^\\ref\s*$", r"\\endref"),
    "astro-ph/9607124": (r"\{\\Large \\noindent \\bf References\}", r"^\\noindent\[(\d+)\]", r"Figure Captions"),
    "gr-qc/9604001": (r"^\{\\bf References\}", r"^\[(\d+)\]", r"^\\end\s*$"),
    "gr-qc/9906015": (r"\\centerline\{\\rmm References\}", r"^\\ref\s*$", r"^\\bye"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for pid, (head, mark, end) in SPEC.items():
        p = os.path.join(ROOT, pid.replace("/", "_"), "flat.tex")
        lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
        hl = [k for k, l in enumerate(lines) if re.search(head, l)]
        start = hl[-1] + 1
        stop = next((k for k in range(start, len(lines)) if re.search(end, lines[k])), len(lines))
        n, nums = 0, []
        for l in lines[start:stop]:
            m = re.match(mark, l)
            if m:
                n += 1
                if m.groups():
                    nums.append(int(m.group(1)))
        rows.append((pid, hl[-1] + 1, stop + 1, mark, n, max(nums) if nums else ""))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "marker_counts.tsv"), "w") as fh:
        fh.write("paper\theading_line\tend_line\tmarker\tcount\tmax_number\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    for r in rows:
        print("\t".join(str(x) for x in r))


if __name__ == "__main__":
    main()
