"""Lead check L10: papers whose sources define an alias of a definition command
(\newcommand{\nc}{\newcommand}, \let\nc\newcommand, \def\nc{\newcommand}); count the uses
of environment shorthands defined through such an alias. Text only.
Usage: python3 -I alias_scan.py <kb-data root>"""
import os, re, sys
root = sys.argv[1]
KINDS = r"(newcommand|renewcommand|providecommand|def|gdef)"
AL = re.compile(r"\\(?:newcommand|renewcommand|providecommand)\*?\s*\{\s*\\([A-Za-z@]+)\s*\}\s*\{\s*\\" + KINDS + r"\s*\}"
                r"|\\(?:def|gdef)\s*\\([A-Za-z@]+)\s*\{\s*\\" + KINDS + r"\s*\}"
                r"|\\let\s*\\([A-Za-z@]+)\s*=?\s*\\" + KINDS + r"(?![A-Za-z@])")
hits = {}
raw = os.path.join(root, "raw", "arxiv")
for key in sorted(os.listdir(raw)):
    vs = sorted(v for v in os.listdir(os.path.join(raw, key)) if v.startswith("v"))
    if not vs: continue
    src = os.path.join(raw, key, vs[-1], "src")
    names = set()
    for dp, dn, fn in os.walk(src):
        for f in fn:
            if f.endswith((".tex", ".sty", ".ltx")):
                try:
                    t = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                t = re.sub(r"(?<!\\)%.*", "", t)
                for m in AL.finditer(t):
                    names.add(m.group(1) or m.group(3) or m.group(5))
    if names:
        hits[key.replace("_", "/", 1) if not key[0].isdigit() else key] = sorted(names)
print(len(hits), "papers define an alias of a definition command")
for k, v in hits.items():
    print(" ", k, v)
