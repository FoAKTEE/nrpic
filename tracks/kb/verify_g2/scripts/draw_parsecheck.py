"""Step 4b of the KB-G2 verifier: draw 15 papers for the check of the parse scan against the
source (seeded; 5 with parse_status other than ok, 10 with ok) and print, for each, the scan
counts and the database counts next to direct counts in the raw source tree (all .tex files,
read as text only), so the verifier can read the source and judge.
"""
import argparse
import glob
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vg2common as C  # noqa: E402


def raw_counts(pid, version):
    src = os.path.join(C.RAW_ARXIV, C.id_dir(pid), version or "", "src")
    out = dict(tex_files=0, sec=0, env=0, bibitem=0, cite=0, abstract=0)
    for p in glob.glob(os.path.join(src, "**", "*.tex"), recursive=True):
        if os.path.islink(p) or not os.path.isfile(p):
            continue
        t = C.read_text(p, limit=32 << 20)
        t = re.sub(r"(?<!\\)%.*", "", t)          # crude comment strip, line by line
        out["tex_files"] += 1
        out["sec"] += len(re.findall(r"\\(?:sub)*section\*?\s*[\[{]", t))
        out["env"] += len(re.findall(r"\\begin\{(?:equation|align|eqnarray|gather|multline)\*?\}", t))
        out["bibitem"] += len(re.findall(r"\\bibitem", t))
        out["cite"] += len(re.findall(r"\\cite", t))
        out["abstract"] += len(re.findall(r"\\begin\{abstract\}|\\abstract\b", t))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--scan", required=True, help="scan.json of a parse_scan run")
    a = ap.parse_args()
    d = json.load(open(a.scan))
    rows = {r["paper_id"]: r for r in d["rows"]}
    con = C.open_ro()
    ver = dict(con.execute("select paper_id, version from papers").fetchall())
    main_tex = dict(con.execute("select paper_id, main_tex from papers").fetchall())
    rng = random.Random(a.seed)
    notok = sorted(p for p, r in rows.items() if r["status"] != "ok")
    ok = sorted(p for p, r in rows.items() if r["status"] == "ok")
    pick = rng.sample(notok, 5) + rng.sample(ok, 10)
    out = []
    for pid in pick:
        r = rows[pid]
        rc = raw_counts(pid, ver[pid])
        rec = dict(paper_id=pid, status=r["status"], version=ver[pid], main_tex=main_tex[pid], raw=rc,
                   scan={k: r[k] for k in ("my_sec", "my_eq", "my_eq_env", "my_eq_short", "my_cite_cmds",
                                           "my_bib", "my_bib_source", "my_abstract_env")},
                   db={k: r[k] for k in ("db_sec", "db_eq", "db_bib", "db_cit", "db_abs_chunk", "abs_recall")},
                   verdict={k: r[k] for k in ("S", "E", "B", "A", "success", "success_lenient")})
        out.append(rec)
        print(json.dumps(rec))
    with open(os.path.join(C.run_dir(), "parsecheck_draw.json"), "w") as f:
        json.dump(dict(seed=a.seed, scan=a.scan, picks=out), f, indent=1)


if __name__ == "__main__":
    main()
