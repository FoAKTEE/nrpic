"""The serve pipeline: track locators -> checked statements -> claims -> figure.

    python3 -I run_serve.py <run_dir> [--dry-run] [--run-id ID]

Steps (each writes into <run_dir>):
  1. extract_track_locators.py -> statements.jsonl (A, B, C, F reference documents)
  2. + claims/manual.jsonl (errata and notes of C, D, E, F written by hand) -> all.jsonl
  3. kb/serve_locate.py check (read-only, kb-data/db/kb.sqlite) -> checked.jsonl
  4. map_to_k8.py -> k8map.tsv (which statements a claim of the K8 seed already covers)
  5. kb/serve_locate.py sync-k8 (writer lock; --dry-run rolls back) -> sync.tsv
  6. served_claims.tsv, summary.json; fig_serve.py -> fig_locator_check.{png,pdf}
The committed copies (claims/served_claims.tsv, claims/summary.json, the figure) are
written into tracks/kb/served/ by the caller with --publish.
"""
import argparse
import collections
import json
import os
import shutil
import sqlite3
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SERVED = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(os.path.dirname(SERVED)))
DB = "/data/haiyangw/nrpic/kb-data/db/kb.sqlite"


def sh(*cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=WT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run-id", default="unregistered")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--write-claims", action="store_true",
                    help="really add the uncovered statements as claims (default: dry run, nothing written)")
    a = ap.parse_args()
    d = a.run_dir
    os.makedirs(d, exist_ok=True)
    sh("python3", "-I", os.path.join(HERE, "extract_track_locators.py"), os.path.join(d, "statements.jsonl"))
    with open(os.path.join(d, "all.jsonl"), "w") as g:
        for p in (os.path.join(d, "statements.jsonl"), os.path.join(SERVED, "claims", "manual.jsonl")):
            g.write(open(p).read())
    sh("python3", "-I", os.path.join(WT, "kb", "serve_locate.py"), "check", os.path.join(d, "all.jsonl"),
       os.path.join(d, "checked.jsonl"), "--db", DB)
    run_id = a.run_id if a.run_id != "unregistered" else os.path.basename(os.path.abspath(d))
    sh("python3", "-I", os.path.join(HERE, "map_to_k8.py"), os.path.join(d, "checked.jsonl"), DB,
       os.path.join(d, "k8map.tsv"))
    sync = ["python3", "-I", os.path.join(WT, "kb", "serve_locate.py"), "sync-k8", os.path.join(d, "checked.jsonl"),
            os.path.join(d, "k8map.tsv"), os.path.join(d, "sync.tsv"), "--run-id", run_id]
    sh(*(sync + ([] if a.write_claims and not a.dry_run else ["--dry-run"])))
    rows = [json.loads(l) for l in open(os.path.join(d, "checked.jsonl")) if l.strip()]
    sy = {}
    with open(os.path.join(d, "sync.tsv")) as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            sy[p[0]] = p
    k8lab = {}
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    for cid, lab, stt, sk in c.execute("SELECT c.claim_id, c.label, m.status, m.seed_key FROM claims c "
                                       "JOIN claim_meta m USING(claim_id)"):
        k8lab[cid] = (lab, stt, sk)
    uncovered = []
    with open(os.path.join(d, "served_claims.tsv"), "w") as g:
        g.write("key\towner\tpaper_id\ttrack_locator\tkb_locator\tnumbers_found/near/n\tnot_found\t"
                "claim_ids\tsource\tlabels\tstatuses\tseed_keys\n")
        for r in rows:
            p = sy[r["key"]]
            ids = [int(x) for x in p[2].split(",") if x]
            labs = [k8lab.get(i, ("?", "?", "?")) for i in ids] if p[1] == "k8" else []
            if p[1] != "k8":
                labs = [(p[3] or "-", p[4] or "-", "-")]
                ids = []
                if r["kb"]:
                    uncovered.append(dict(r, k8_label=p[3], k8_status=p[4]))
            tl = "; ".join(f"{k['file']}:{k['lo']}" + (f"-{k['hi']}" if k['hi'] != k['lo'] else "") for k in r["kb"])
            n = r["numbers"]
            ns = f"{n.get('found', 0)}/{n.get('near', 0)}/{n['n']}" if n.get("n") else "-"
            miss = " ".join(n.get("missing", [])) if n.get("n") else ""
            g.write(f"{r['key']}\t{r['owner']}\t{r['paper_id']}\t{tl}\t{r.get('kb_locator', '')}\t{ns}\t{miss}\t"
                    f"{','.join(map(str, ids))}\t{p[1]}\t{','.join(x[0] for x in labs)}\t"
                    f"{','.join(str(x[1]) for x in labs)}\t{','.join(str(x[2]) for x in labs)}\n")
    with open(os.path.join(d, "uncovered_seed.jsonl"), "w") as g:
        for r in uncovered:
            g.write(json.dumps(r) + "\n")
    summ = {"run_id": run_id, "statements": len(rows), "locators": sum(len(r["kb"]) for r in rows),
            "locators_resolved": sum(1 for r in rows for k in r["kb"] if k.get("status") == "resolved"
                                     and k.get("lines_in_file")),
            "statements_without_locator": [r["key"] for r in rows if not r["kb"]],
            "disposition": collections.Counter(sy[r["key"]][1] for r in rows),
            "added_by_label": collections.Counter(f"{sy[r['key']][3]}/{sy[r['key']][4]}" for r in rows
                                                  if sy[r["key"]][1] in ("added", "kept")),
            "numbers": collections.Counter(
                ("exact" if r["numbers"]["found"] == r["numbers"]["n"] else
                 "near" if r["numbers"]["near"] == r["numbers"]["n"] else "missing")
                for r in rows if r["numbers"].get("n"))}
    with open(os.path.join(d, "summary.json"), "w") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps(summ, indent=1))
    py = os.path.join(WT, "kb", ".venv", "bin", "python")
    sh(py, "-I", os.path.join(HERE, "fig_serve.py"), os.path.join(d, "served_claims.tsv"),
       os.path.join(d, "fig_locator_check"))
    if a.publish:
        os.makedirs(os.path.join(SERVED, "claims"), exist_ok=True)
        shutil.copy(os.path.join(d, "served_claims.tsv"), os.path.join(SERVED, "claims", "served_claims.tsv"))
        shutil.copy(os.path.join(d, "uncovered_seed.jsonl"), os.path.join(SERVED, "claims", "uncovered_seed.jsonl"))
        shutil.copy(os.path.join(d, "summary.json"), os.path.join(SERVED, "claims", "summary.json"))
        for ext in ("png", "pdf"):
            shutil.copy(os.path.join(d, f"fig_locator_check.{ext}"), os.path.join(SERVED, f"fig_locator_check.{ext}"))


if __name__ == "__main__":
    sys.exit(main())
