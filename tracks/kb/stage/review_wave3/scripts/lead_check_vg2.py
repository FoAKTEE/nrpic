"""Lead's independent check of the verify_g2 package (kb, wave 3 batch 3).

Reads, never writes: the frozen snapshot kb-20261119-a782f1e (mode=ro, immutable), the
verifier's registered raw search outputs and parse scan, three paper sources under
kb-data/raw (read as text, never executed), git and two run manifests. Writes check.json and a
figure into the run directory ($NRPIC_RUN_DIR). Prediction L1 in tracks/kb/JOURNAL.md.
"""
import collections
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys

import yaml  # noqa: F401  (kb/.venv provides PyYAML)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
WT = "/data/haiyangw/nrpic/wt/kb"
SCR = "/data/haiyangw/nrpic/scratch/kb"
RAW = "/data/haiyangw/nrpic/kb-data/raw/arxiv"
SNAP = "/data/haiyangw/nrpic/kb-data/db/kb-20261119-a782f1e.sqlite"
OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(SCR, "tmp", "lead_check"))
os.makedirs(OUT, exist_ok=True)

RUN_RAW = {"heldout": f"{SCR}/kb-20261120-222546-ea894c8/raw/heldout",
           "golden": f"{SCR}/kb-20261121-074940-08426cc/raw/golden"}
QFILES = {"heldout": f"{WT}/tracks/kb/verify_g2/heldout.yaml",
          "golden": f"{WT}/kb/golden/questions.yaml"}
SCAN = f"{SCR}/kb-20261120-223309-14e4cb6/scan.json"
GAPS = ("hep-ph/9809574,1201.4794,gr-qc/0304002,astro-ph/9607124,astro-ph/0306304,"
        "astro-ph/9306009,astro-ph/9510056,gr-qc/9604001,gr-qc/9906015").split(",")
VERIFIER = {"heldout": {"text": (21, 14), "hybrid": (22, 14), "rerank": (21, 14)},
            "golden": {"text": (27, 20), "hybrid": (28, 17), "rerank": (28, 19)}}
res = {}


def expected_papers(setname):
    d = yaml.safe_load(open(QFILES[setname]))
    qs = d["questions"]
    out = {}
    for q in qs:
        out[q["id"]] = str(q.get("paper_id") or q.get("paper"))
    return out


# 1. paper hits recounted from the raw hit lists
ret = {}
for s in ("heldout", "golden"):
    exp = expected_papers(s)
    ret[s] = {}
    for mode in ("text", "hybrid", "rerank"):
        hit = r1 = 0
        missing = []
        for qid, pid in exp.items():
            f = os.path.join(RUN_RAW[s], f"{qid}.{mode}.json")
            if not os.path.exists(f):
                missing.append(qid)
                continue
            hits = json.load(open(f))["hits"][:10]
            ids = [h["paper_id"] for h in hits]
            if pid in ids:
                hit += 1
                if ids[0] == pid:
                    r1 += 1
        ret[s][mode] = {"n": len(exp), "hit": hit, "rank1": r1, "missing_files": missing,
                        "verifier": VERIFIER[s][mode],
                        "agree": (hit, r1) == VERIFIER[s][mode]}
    # snapshot field on hits?
    one = json.load(open(sorted(glob.glob(os.path.join(RUN_RAW[s], "*.hybrid.json")))[0]))
    ret[s]["hit_keys"] = sorted(one["hits"][0].keys())
    ret[s]["info"] = one.get("info")
res["retrieval"] = ret

# 2. snapshot counts by SQL
c = sqlite3.connect(f"file:{SNAP}?mode=ro&immutable=1", uri=True)
q = lambda sql: c.execute(sql).fetchall()  # noqa: E731
res["parse_status"] = dict(q("select parse_status, count(*) from papers group by 1"))
nobib = q("""select p.paper_id, p.parse_status from papers p where p.source_kind='tex'
             and not exists (select 1 from bib_entries b where b.paper_id=p.paper_id)""")
res["tex_without_bib"] = {"n": len(nobib), "ok": sum(1 for _, s in nobib if s == "ok"),
                          "ids": sorted(p for p, _ in nobib)}
citnobib = q("""select distinct c.citing from citations c where not exists
                (select 1 from bib_entries b where b.paper_id=c.citing)""")
res["cit_rows_without_bib"] = {"n": len(citnobib), "ids": sorted(r[0] for r in citnobib)}
noabs = q("""select p.paper_id from papers p where not exists
             (select 1 from chunks k where k.paper_id=p.paper_id and k.kind='abstract')""")
res["no_abstract_chunk"] = len(noabs)
repos = q("""select r.repo_id, (select count(*) from code_chunks cc join code_files f
             on cc.file_id=f.file_id where f.repo_id=r.repo_id) from repos r""")
res["repos"] = {"n": len(repos), "without_code_chunks": sum(1 for _, n in repos if n == 0)}

# 3. the verifier's database columns against my SQL
mine_db = {}
for pid, kind in q("select paper_id, source_kind from papers"):
    mine_db[pid] = {"kind": kind}
for col, sql in (("db_sec", "select paper_id, count(*) from sections group by 1"),
                 ("db_eq", "select paper_id, count(*) from equations group by 1"),
                 ("db_bib", "select paper_id, count(*) from bib_entries group by 1"),
                 ("db_cit", "select citing, count(*) from citations group by 1"),
                 ("db_abs", "select paper_id, count(*) from chunks where kind='abstract' group by 1")):
    got = dict(q(sql))
    for pid in mine_db:
        mine_db[pid][col] = got.get(pid, 0)
meta_abs = dict(q("select paper_id, length(coalesce(abstract,''))>0 from papers"))
scan = json.load(open(SCAN))["rows"]
diff = collections.Counter()
diff_ids = collections.defaultdict(list)
for r in scan:
    m = mine_db[r["paper_id"]]
    for a, b in (("db_sec", "db_sec"), ("db_eq", "db_eq"), ("db_bib", "db_bib"), ("db_cit", "db_cit")):
        if r[a] != m[b]:
            diff[a] += 1
            diff_ids[a].append(r["paper_id"])
    if bool(r["db_abs_chunk"]) != (m["db_abs"] > 0):
        diff["db_abs_chunk"] += 1
        diff_ids["db_abs_chunk"].append(r["paper_id"])
res["scan_vs_sql"] = {"n": len(scan), "differences": dict(diff),
                      "ids": {k: v[:10] for k, v in diff_ids.items()}}

# 4. my evaluation of the verifier's definition from the scan's source counts and my db counts
comp = collections.Counter()
mine_pass = set()
disagree = collections.defaultdict(list)
for r in scan:
    pid = r["paper_id"]
    m = mine_db[pid]
    pdf = m["kind"] == "pdf"
    S = m["db_sec"] >= 1 or r["my_sec"] == 0
    E = pdf or r["my_eq"] == 0 or (m["db_eq"] >= 1 and m["db_eq"] >= 0.5 * r["my_eq"])
    cites = r["my_cite_cmds"] > 0
    B = pdf or (not cites) or (m["db_bib"] >= 1 and m["db_bib"] >= 0.5 * r["my_bib"] and m["db_cit"] >= 1)
    A = (m["db_abs"] > 0) or bool(meta_abs.get(pid))
    for k, v in (("S", S), ("E", E), ("B", B), ("A'", A)):
        comp[k] += v
        theirs = r["A_lenient"] if k == "A'" else r[k]
        if bool(v) != bool(theirs):
            disagree[k].append(pid)
    if S and E and B and A:
        mine_pass.add(pid)
letters = set()
tl = json.load(open(f"{SCR}/kb-20261121-080843-98907be/tally.json"))
man = json.load(open(f"{WT}/tracks/kb/runs/kb-20261121-080843-98907be/manifest.json"))
cmd = " ".join(man["command"]) if isinstance(man["command"], list) else man["command"]
mm = re.search(r"--letters\s+(\S+)", cmd)
if mm:
    letters = set(mm.group(1).strip("'\"").split(","))
res["definition"] = {"components": dict(comp), "lenient_pass": len(mine_pass),
                     "after_gaps": len(mine_pass - set(GAPS)),
                     "after_gaps_letters_failed": len(mine_pass - set(GAPS) - letters),
                     "letters_n": len(letters),
                     "disagree_with_scan": {k: v for k, v in disagree.items()},
                     "verifier_tally": {k: tl[k] for k in ("mine_lenient_corrected",
                                                           "mine_lenient_corrected_letters_failed",
                                                           "mine_strict_corrected")}}


# 5. three sources, read as text
def src_files(pid):
    base = os.path.join(RAW, pid.replace("/", "_"))
    vs = sorted(os.listdir(base))
    root = os.path.join(base, vs[-1], "src")
    out = []
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if fn.lower().endswith((".tex", ".bbl", ".ltx", ".txt")) or "." not in fn:
                out.append(os.path.join(dp, fn))
    return out


def grep_count(pid, pat):
    rx = re.compile(pat)
    n = 0
    for f in src_files(pid):
        try:
            n += len(rx.findall(open(f, encoding="latin-1").read()))
        except OSError:
            pass
    return n


res["sources"] = {
    "0710.5073": {"bibitem": grep_count("0710.5073", r"\\bibitem"),
                  "begin_references": grep_count("0710.5073", r"\\begin\{references\}")},
    "1201.4794": {"reference": grep_count("1201.4794", r"\\reference\b")},
    "gr-qc/0304002": {"def_bi": grep_count("gr-qc/0304002", r"\\def\\bi\{\\bibitem\}"),
                      "bi_uses": grep_count("gr-qc/0304002", r"\\bi\b")},
}

# 6. held-out commit before the first search
ct = subprocess.run(["git", "-C", WT, "show", "-s", "--format=%cI", "8fb37106"],
                    capture_output=True, text=True).stdout.strip()
m6 = json.load(open(f"{WT}/tracks/kb/runs/kb-20261120-222546-ea894c8/manifest.json"))
res["heldout_order"] = {"commit_time": ct, "run_start": m6.get("started") or m6.get("start_time")
                        or m6.get("started_at"), "run_commit": m6.get("commit")}

# 7. snapshot id in kb show / kb cites output
KB = [f"{WT}/kb/.venv/bin/python", "-I", f"{WT}/kb/bin/kb"]
show = subprocess.run(KB + ["show", "2611.12831", "--abstract", "--db", SNAP],
                      capture_output=True, text=True, cwd=WT)
cites = subprocess.run(KB + ["cites", "2611.12831", "--out", "--db", SNAP],
                       capture_output=True, text=True, cwd=WT)
idrx = re.compile(r"a782f1e|kb-2026\d{4}-[0-9a-f]{7}")
res["c6b"] = {"show_rc": show.returncode, "show_has_id": bool(idrx.search(show.stdout + show.stderr)),
              "show_tail": (show.stdout + show.stderr)[-300:],
              "cites_rc": cites.returncode, "cites_has_id": bool(idrx.search(cites.stdout + cites.stderr)),
              "cites_tail": (cites.stdout + cites.stderr)[-300:],
              "hit_has_snapshot_field": any("snap" in k for k in ret["golden"]["hit_keys"])}

# 8. two wave-1 manifests
res["wave1_manifests"] = {}
for r in ("kb-20261115-154858-b0d8c8f", "kb-20261115-164121-5aca10c"):
    mm = json.load(open(f"{WT}/tracks/kb/runs/{r}/manifest.json"))
    res["wave1_manifests"][r] = {"status": mm.get("status"), "exit_code": mm.get("exit_code")}

json.dump(res, open(os.path.join(OUT, "check.json"), "w"), indent=1, default=str)

# figure
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle as fs  # noqa: E402

fs.use_style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
labels, ver, mine = [], [], []
for s in ("heldout", "golden"):
    for mode in ("text", "hybrid", "rerank"):
        labels.append(f"{s[:4]}\n{mode}")
        n = ret[s][mode]["n"]
        ver.append(100.0 * ret[s][mode]["verifier"][0] / n)
        mine.append(100.0 * ret[s][mode]["hit"] / n)
x = range(len(labels))
a1.bar([i - 0.2 for i in x], ver, 0.4, color=fs.PAL["blue"], label="verifier (VERIFIER.md)")
a1.bar([i + 0.2 for i in x], mine, 0.4, color=fs.PAL["red"], label="lead recount (raw hits)")
a1.axhline(80, **fs.GUIDE)
a1.set_xticks(list(x))
a1.set_xticklabels(labels, fontsize=7)
a1.set_ylim(0, 105)
a1.set_ylabel("right paper in top 10 [%]")
a1.legend(loc="lower right", fontsize=7)
a1.set_title("(a) retrieval, bar 80 %", fontsize=9)
meas = ["status ok", "lenient", "minus gaps", "letters failed"]
d = res["definition"]
vals_mine = [res["parse_status"].get("ok", 0), d["lenient_pass"], d["after_gaps"], d["after_gaps_letters_failed"]]
vals_ver = [684, json.load(open(SCAN))["summary"]["mine_lenient"], tl["mine_lenient_corrected"],
            tl["mine_lenient_corrected_letters_failed"]]
xx = range(len(meas))
a2.bar([i - 0.2 for i in xx], vals_ver, 0.4, color=fs.PAL["blue"], label="verifier")
a2.bar([i + 0.2 for i in xx], vals_mine, 0.4, color=fs.PAL["red"], label="lead (own SQL)")
a2.axhline(0.95 * 710, **fs.GUIDE)
a2.text(3.45, 0.95 * 710 + 1, "95 % bar", ha="right", va="bottom", fontsize=7)
a2.set_ylim(640, 700)
a2.set_xticks(list(xx))
a2.set_xticklabels(meas, fontsize=7)
a2.set_ylabel("papers parsed (of 710)")
a2.legend(loc="upper right", fontsize=7)
a2.set_title("(b) parse success", fontsize=9)
fig.tight_layout()
fs.save(fig, os.path.join(OUT, "fig_lead_check_vg2"))
print(json.dumps({k: res[k] for k in ("parse_status", "tex_without_bib", "cit_rows_without_bib",
                                      "no_abstract_chunk", "repos", "scan_vs_sql", "heldout_order",
                                      "wave1_manifests")}, default=str)[:3000])
print(json.dumps(res["definition"], default=str)[:2000])
print(json.dumps(res["sources"]))
print(json.dumps(res["c6b"])[:800])
for s in ret:
    for mode in ("text", "hybrid", "rerank"):
        print(s, mode, ret[s][mode]["hit"], ret[s][mode]["rank1"], ret[s][mode]["verifier"],
              ret[s][mode]["agree"], ret[s][mode]["missing_files"])
