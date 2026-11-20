"""Lead check L11: shorthands whose body is two or more \begin{..}/\end{..} only
(\newcommand{\bea}{\begin{equation}\begin{aligned}}), and how often the body of each paper
uses them. Text only. Usage: python3 -I composite_scan.py <kb-data root>"""
import os, re, sys
root = sys.argv[1]
D = re.compile(r"\\(?:newcommand|renewcommand|providecommand|nc|newc|def)\*?\s*\{?\s*\\([A-Za-z]+)\s*\}?\s*\{\s*((?:\\(?:begin|end)\s*\{[A-Za-z*]+\}\s*){2,})\}")
raw = os.path.join(root, "raw", "arxiv"); tot = 0
for key in sorted(os.listdir(raw)):
    vs = sorted(v for v in os.listdir(os.path.join(raw, key)) if v.startswith("v"))
    if not vs: continue
    src = os.path.join(raw, key, vs[-1], "src"); text = ""
    for dp, dn, fn in os.walk(src):
        for f in fn:
            if f.endswith((".tex", ".sty")):
                try: text += open(os.path.join(dp, f), encoding="utf-8", errors="replace").read() + "\n"
                except OSError: pass
    text = re.sub(r"(?<!\\)%.*", "", text)
    defs = {m.group(1): m.group(2) for m in D.finditer(text) if "begin" in m.group(2)}
    if not defs: continue
    body = text.split("\\begin{document}", 1)[-1]
    uses = {n: len(re.findall(r"\\" + n + r"(?![A-Za-z@])", body)) for n in defs}
    if sum(uses.values()):
        tot += 1
        print(key, {n: (defs[n].strip()[:50], uses[n]) for n in defs})
print("papers using composite begin shorthands:", tot)
