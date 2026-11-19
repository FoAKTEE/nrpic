"""Lead check L10: like eqcount.py, after replacing shorthands defined (directly or through
an alias such as \nc) as \begin{env} / \end{env}. Usage: python3 -I eqcount_alias.py FILE"""
import re, sys, subprocess, os, tempfile
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
t = re.sub(r"(?<!\\)%.*", "", t)
defs = {}
for m in re.finditer(r"\\(?:nc|newc|newcommand|def)\s*\{?\s*\\([A-Za-z]+)\s*\}?\s*\{\s*(\\(?:begin|end)\s*\{[A-Za-z*]+\})\s*\}", t):
    defs[m.group(1)] = m.group(2)
body = t.split("\\begin{document}", 1)
pre, rest = body[0], body[1]
if defs:
    pat = re.compile(r"\\(" + "|".join(sorted(defs, key=len, reverse=True)) + r")(?![A-Za-z@])")
    rest = pat.sub(lambda m: defs[m.group(1)].replace("\\", "\\\\"), rest)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp_alias.tex")
open(out, "w").write(pre + "\\begin{document}" + rest)
print("shorthands:", defs)
print(subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "eqcount.py"), out],
                     capture_output=True, text=True).stdout.splitlines()[0])
