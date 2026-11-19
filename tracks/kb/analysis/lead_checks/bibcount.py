"""Lead check L6: count bibliography entries of stored papers independently of kbtool.
.bbl: count of \\bibitem (natbib/REVTeX) or \\entry{ (biblatex) after comment stripping.
.bib: count of @type{ entries other than @string/@comment/@preamble; also the number of
distinct keys cited in the main .tex. Reads files as text only.
Usage: python3 -I bibcount.py <kb-data root> <seed> <n>
"""
import os, random, re, sqlite3, sys

root, seed, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
db = sqlite3.connect(f"file:{root}/db/current?mode=ro", uri=True)
stored = dict(db.execute("select paper_id, count(*) from bib_entries group by paper_id"))


def latest(pid):
    d = os.path.join(root, "raw", "arxiv", pid.replace("/", "_"))
    v = sorted(x for x in os.listdir(d) if x.startswith("v"))[-1]
    return os.path.join(d, v, "src")


def files(src, ext):
    out = []
    for dp, dn, fn in os.walk(src):
        out += [os.path.join(dp, f) for f in fn if f.endswith(ext)]
    return out


def strip(t):
    return re.sub(r"(?<!\\)%.*", "", t)


papers = [r[0] for r in db.execute("select paper_id from papers where source_kind='tex' order by paper_id")]
with_bbl = [p for p in papers if os.path.isdir(latest(p)) and len(files(latest(p), ".bbl")) == 1]
random.seed(seed)
pick = random.sample(with_bbl, n)
print(f"papers with exactly one .bbl: {len(with_bbl)}; drawn: {pick}")
for p in ["2611.12831"] + pick:
    src = latest(p)
    bbl = files(src, ".bbl")
    if bbl:
        t = strip(open(bbl[0], errors="replace").read())
        k = len(re.findall(r"\\bibitem\b", t)) or len(re.findall(r"\\entry\{", t))
        print(f"{p}: .bbl items {k}  stored {stored.get(p, 0)}  {'EQUAL' if k == stored.get(p, 0) else 'DIFF'}")
    else:
        bibs = files(src, ".bib")
        ents = 0
        for b in bibs:
            t = open(b, errors="replace").read()
            ents += len([m for m in re.findall(r"@(\w+)\s*[{(]", t) if m.lower() not in ("string", "comment", "preamble")])
        tex = "".join(strip(open(f, errors="replace").read()) for f in files(src, ".tex"))
        keys = set()
        for m in re.finditer(r"\\(?:no)?cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", tex):
            keys |= {k.strip() for k in m.group(1).split(",") if k.strip()}
        print(f"{p}: .bib entries {ents}, distinct cited keys {len(keys)}, stored {stored.get(p, 0)}")
