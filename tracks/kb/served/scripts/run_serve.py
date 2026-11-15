"""The serve pipeline: track locators -> checked statements -> claims -> figure.

    python3 -I run_serve.py <run_dir> [--dry-run] [--run-id ID]

Steps (each writes into <run_dir>):
  1. extract_track_locators.py -> statements.jsonl (A, B, C, F reference documents)
  2. + claims/manual.jsonl (errata and notes of C, D, E, F written by hand) -> all.jsonl
  3. kb/serve_locate.py check (read-only, kb-data/db/kb.sqlite) -> checked.jsonl
  4. kb/serve_locate.py load (writer lock; --dry-run writes nothing) -> claim_ids.tsv
  5. summary.json; fig_serve.py -> fig_locator_check.{png,pdf}
The committed copies (claims/claim_ids.tsv, claims/checked_summary.tsv, the figure) are
written into tracks/kb/served/ by the caller with --publish.
"""
import argparse
import collections
import json
import os
import shutil
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
    a = ap.parse_args()
    d = a.run_dir
    os.makedirs(d, exist_ok=True)
    sh("python3", "-I", os.path.join(HERE, "extract_track_locators.py"), os.path.join(d, "statements.jsonl"))
    with open(os.path.join(d, "all.jsonl"), "w") as g:
        for p in (os.path.join(d, "statements.jsonl"), os.path.join(SERVED, "claims", "manual.jsonl")):
            g.write(open(p).read())
    sh("python3", "-I", os.path.join(WT, "kb", "serve_locate.py"), "check", os.path.join(d, "all.jsonl"),
       os.path.join(d, "checked.jsonl"), "--db", DB)
    load = ["python3", "-I", os.path.join(WT, "kb", "serve_locate.py"), "load", os.path.join(d, "checked.jsonl"),
            os.path.join(d, "claim_ids.tsv"), "--run-id", a.run_id]
    sh(*(load + (["--dry-run"] if a.dry_run else [])))
    rows = [json.loads(l) for l in open(os.path.join(d, "checked.jsonl")) if l.strip()]
    ids = {}
    with open(os.path.join(d, "claim_ids.tsv")) as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            ids[p[0]] = p
    summ = {"statements": len(rows), "locators": sum(len(r["kb"]) for r in rows),
            "locators_resolved": sum(1 for r in rows for k in r["kb"] if k.get("status") == "resolved"
                                     and k.get("lines_in_file")),
            "statements_without_locator": [r["key"] for r in rows if not r["kb"]],
            "by_owner_label": collections.Counter(f"{r['owner']} {ids[r['key']][2]}" for r in rows),
            "numbers": collections.Counter(
                ("exact" if r["numbers"]["found"] == r["numbers"]["n"] else
                 "near" if r["numbers"]["near"] == r["numbers"]["n"] else "missing")
                for r in rows if r["numbers"].get("n"))}
    with open(os.path.join(d, "summary.json"), "w") as f:
        json.dump(summ, f, indent=1)
    # table of the check, one row per statement (our wording and the tracks' wording only)
    with open(os.path.join(d, "checked_summary.tsv"), "w") as g:
        g.write("key\tclaim_id\tlabel\towner\tpaper_id\ttrack_locator\tkb_locator\tnumbers\tnot_found\treason\n")
        for r in rows:
            p = ids[r["key"]]
            tl = "; ".join(f"{k['file']}:{k['lo']}" + (f"-{k['hi']}" if k['hi'] != k['lo'] else "") for k in r["kb"])
            n = r["numbers"]
            ns = f"{n.get('found', 0)}/{n.get('near', 0)}/{n['n']}" if n.get("n") else "-"
            miss = " ".join(n.get("missing", [])) if n.get("n") else ""
            reason = p[6].split("| kb check: ")[1] if "| kb check: " in p[6] else ""
            g.write(f"{r['key']}\t{p[1]}\t{p[2]}\t{r['owner']}\t{r['paper_id']}\t{tl}\t{r.get('kb_locator', '')}\t"
                    f"{ns}\t{miss}\t{reason}\n")
    print(json.dumps(summ, indent=1))
    py = os.path.join(WT, "kb", ".venv", "bin", "python")
    sh(py, "-I", os.path.join(HERE, "fig_serve.py"), os.path.join(d, "checked.jsonl"),
       os.path.join(d, "claim_ids.tsv"), os.path.join(d, "fig_locator_check"))
    if a.publish:
        os.makedirs(os.path.join(SERVED, "claims"), exist_ok=True)
        shutil.copy(os.path.join(d, "claim_ids.tsv"), os.path.join(SERVED, "claims", "claim_ids.tsv"))
        shutil.copy(os.path.join(d, "checked_summary.tsv"), os.path.join(SERVED, "claims", "checked_summary.tsv"))
        shutil.copy(os.path.join(d, "summary.json"), os.path.join(SERVED, "claims", "summary.json"))
        for ext in ("png", "pdf"):
            shutil.copy(os.path.join(d, f"fig_locator_check.{ext}"), os.path.join(SERVED, f"fig_locator_check.{ext}"))


if __name__ == "__main__":
    sys.exit(main())
