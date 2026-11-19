"""Lead check L11 (corrected count): uses of composite environment shorthands over all .tex
files of a paper, comments and definition statements excluded; joins the database counts
before (l11_before.txt) and after. Usage: python3 -I composite_uses.py <kb-data root> <before> <out.tsv>"""
import os, re, sqlite3, sys
root, before_f, out = sys.argv[1:4]
D = re.compile(r"\\(?:newcommand|renewcommand|providecommand|nc|newc|def)\*?\s*\{?\s*\\([A-Za-z]+)\s*\}?\s*\{\s*((?:\\(?:begin|end)\s*\{[A-Za-z*]+\}\s*){2,})\}")
before = {l.split()[0]: int(l.split()[1]) for l in open(before_f)}
db = sqlite3.connect(f"file:{root}/db/kb.sqlite?mode=ro", uri=True)
with open(out, "w") as f:
    f.write("paper_id\tuses\trows_before\trows_after\n")
    for pid in before:
        d = os.path.join(root, "raw", "arxiv", pid)
        v = sorted(x for x in os.listdir(d) if x.startswith("v"))[-1]
        texts = []
        for dp, dn, fn in os.walk(os.path.join(d, v, "src")):
            for x in fn:
                if x.endswith(".tex"):
                    texts.append(re.sub(r"(?<!\\)%.*", "", open(os.path.join(dp, x), encoding="utf-8", errors="replace").read()))
        names = {m.group(1) for t in texts for m in D.finditer(t) if "begin" in m.group(2)}
        uses = 0
        for t in texts:
            t = D.sub("", t)
            for n in names:
                uses += len(re.findall(r"\\" + n + r"(?![A-Za-z@])", t))
        after = db.execute("select count(*) from equations where paper_id=?", (pid,)).fetchone()[0]
        f.write(f"{pid}\t{uses}\t{before[pid]}\t{after}\n")
print(open(out).read())
