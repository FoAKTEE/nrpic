"""Lead check L5: count numbered display lines of a single-file LaTeX source, independently
of kbtool. Reads the file as text; nothing is compiled. Rules (amsmath): equation = 1 line;
multline = 1 line; align/gather/eqnarray/flalign/alignat = top-level rows split at \\\\
outside aligned/split/cases/array/matrix environments and braces; an empty last row after a
trailing \\\\ IS numbered (pdflatex, run kb-20261115-155344-596b4ce; the wave-1 rule that
dropped it was wrong, corrected in wave 2, check W3); rows with \\nonumber or \\notag are not numbered; starred
environments are not numbered; \\tag rows are counted separately.
Usage: python3 -I eqcount.py main.tex
"""
import re, sys

src = open(sys.argv[1], encoding="utf-8", errors="replace").read()
# strip comments: % not preceded by a backslash
src = re.sub(r"(?<!\\)%.*", "", src)
body = src.split("\\begin{document}", 1)[1].split("\\end{document}", 1)[0]
NUM = ("equation", "align", "gather", "multline", "eqnarray", "flalign", "alignat")
INNER = ("aligned", "split", "cases", "array", "matrix", "pmatrix", "bmatrix", "gathered",
         "alignedat", "smallmatrix", "vmatrix")
pat = re.compile(r"\\begin\{(" + "|".join(NUM) + r")(\*?)\}(.*?)\\end\{\1\2\}", re.S)
total = 0
tags = 0
labels = []
for m in pat.finditer(body):
    env, star, inner = m.group(1), m.group(2), m.group(3)
    if star:
        continue
    if env in ("equation", "multline"):
        rows = [inner]
    else:
        # split at top-level \\ : blank out inner environments first
        s = inner
        for e in INNER:
            s = re.sub(r"\\begin\{" + e + r"\*?\}.*?\\end\{" + e + r"\*?\}",
                       lambda k: " " * len(k.group(0)), s, flags=re.S)
        cuts = [k.start() for k in re.finditer(r"\\\\", s)]
        rows, prev = [], 0
        for c in cuts:
            rows.append(inner[prev:c]); prev = c + 2
        rows.append(inner[prev:])
    for r in rows:
        if "\\nonumber" in r or "\\notag" in r:
            continue
        if "\\tag" in r:
            tags += 1
            continue
        total += 1
        lab = re.findall(r"\\label\{([^}]*)\}", r)
        labels.append(lab[0] if lab else None)
print("numbered (auto) lines:", total, " tagged:", tags, " labelled:", sum(1 for l in labels if l))
for i, l in enumerate(labels, 1):
    if l and i in (1, 10, 20, 40, 60, len(labels)):
        print(f"  ({i}) {l}")
