"""Lead check B3 (wave 2b): independent recheck of the KB-G1 verifier's WRONG items and defects.

Read-only, own code (imports neither kbtool nor the verifier's scripts). Raw sources are read as
text, never executed. Opens the snapshot the verifier used (db/current, kb-20261115-a848a06).
  1. TeX papers with zero bib_entries in the snapshot, with parse status;
  2. for the verifier's 20 zero-bibliography papers: counts of my own simple patterns in the
     stored source (\\bibitem, \\begin{references}, \\reference, \\harvarditem, \\bi/\\bib macros,
     \\cite) over all .tex/.bbl files of src/;
  3. gr-qc/9906015: live \\eqno count (lines not starting with %);
  4. claim 25: locator string and claim_locators rows (snapshot and working database);
  5. parameter index of local/nrpic: indexed commit, row count; on the commit given as MAIN_REV,
     the (block, name) pairs of literal pin->Get*(...) calls in four files the verifier named,
     and how many of them the index lacks.
Writes verifier_check.json into OUTDIR.
Usage: python3 -I w2b_verifier_check.py NRPIC_HOME ZERO_BIB_TSV MAIN_REV [--out D]
"""
import csv
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys

args = sys.argv[1:]
out = os.environ.get("NRPIC_RUN_DIR")
if "--out" in args:
    i = args.index("--out")
    out = args[i + 1]
    args = args[:i] + args[i + 2:]
home, zb_tsv, main_rev = args[:3]
os.makedirs(out, exist_ok=True)
kbdata = os.path.join(home, "kb-data")
snap = os.path.realpath(os.path.join(kbdata, "db", "current"))
c = sqlite3.connect(f"file:{snap}?mode=ro", uri=True)
w = sqlite3.connect(f"file:{kbdata}/db/kb.sqlite?mode=ro", uri=True)
R = {"snapshot": os.path.basename(snap)}

zero = c.execute("select p.paper_id, p.parse_status from papers p where p.source_kind='tex' and not exists "
                 "(select 1 from bib_entries b where b.paper_id=p.paper_id) order by 1").fetchall()
R["tex_papers"] = c.execute("select count(*) from papers where source_kind='tex'").fetchone()[0]
R["zero_bib"] = zero
R["zero_bib_ok"] = [p for p, s in zero if s == "ok"]

PAT = {"bibitem": r"\\bibitem\b", "begin_references": r"\\begin\{references\}", "reference": r"^\s*\\reference\b",
       "harvarditem": r"\\harvarditem\b", "bi_macro": r"^\s*\\bi[b]?\b", "cite": r"\\cite[a-z]*\{",
       "eqno": r"\\eqno\b", "plain_ref": r"^\s*\\ref\b"}


def src_counts(pid):
    key = pid.replace("/", "_")
    vs = sorted(glob.glob(os.path.join(kbdata, "raw", "arxiv", key, "v*")))
    cnt = {k: 0 for k in PAT}
    if not vs:
        return cnt
    for f in glob.glob(os.path.join(vs[-1], "src", "**", "*"), recursive=True):
        if not os.path.isfile(f) or not re.search(r"\.(tex|bbl|ltx|TEX)$|main\.tex$", f) and "." in os.path.basename(f):
            continue
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for line in txt.split("\n"):
            if line.lstrip().startswith("%"):
                continue
            for k, p in PAT.items():
                cnt[k] += len(re.findall(p, line))
    return cnt


zb = []
with open(zb_tsv) as f:
    for r in csv.DictReader(f, delimiter="\t"):
        zb.append({"paper": r["paper_id"], "status": r["parse_status"], "verifier": r["my_counts"],
                   "lead": src_counts(r["paper_id"])})
R["zero_bib_verifier_list"] = zb
R["zero_bib_verifier_count"] = len(zb)
R["gr-qc/9906015"] = src_counts("gr-qc/9906015")

for name, con in (("snapshot", c), ("working", w)):
    R[f"claim25_{name}"] = {
        "locator": con.execute("select locator from claims where claim_id=25").fetchone(),
        "rows": con.execute("select ord, file, line_start, line_end from claim_locators where claim_id=25 "
                            "order by ord").fetchall()}

R["local_repo"] = c.execute("select repo_id, commit_sha, commit_date from repos where repo_id like 'local%'").fetchall()
R["local_params"] = c.execute("select count(*) from params where repo_id='local/nrpic'").fetchone()[0]
have = set(c.execute("select block, name from params where repo_id='local/nrpic'").fetchall())
files = ["athenak/src/particles/nrpic_collide.cpp", "athenak/src/scalar_field/scalar_field.cpp",
         "athenak/src/particles/nrpic_kick.cpp", "athenak/src/pgen/nrpic/nrpic_cf.cpp"]
per = {}
for fpath in files:
    try:
        txt = subprocess.run(["git", "-C", home, "show", f"{main_rev}:{fpath}"], capture_output=True, text=True,
                             check=True).stdout
    except subprocess.CalledProcessError:
        per[fpath] = "missing at rev"
        continue
    pairs = set(re.findall(r'->Get\w*\(\s*"([^"]+)"\s*,\s*"([^"]+)"', txt))
    per[fpath] = {"literal_pairs": len(pairs), "absent_from_index": sorted(pairs - have)}
R["params_main"] = {"rev": main_rev, "files": per}
with open(os.path.join(out, "verifier_check.json"), "w") as f:
    json.dump(R, f, indent=1, default=str)
print(json.dumps(R, indent=1, default=str)[:7000])
