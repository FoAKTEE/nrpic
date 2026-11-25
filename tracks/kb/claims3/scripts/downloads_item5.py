#!/usr/bin/env python3
"""Item 5 (decision 0035 item 5): 0707.4654 and 1006.1632 leave the downloads table, their files stay.

    python3 -I downloads_item5.py [--out DIR]

Records the downloads rows and the sha256 of every file under kb-data/raw/arxiv/<id>/ for the two
ids, runs `kb verify-downloads` (which reads kb/manifests/downloads_excluded.tsv and rewrites the
table inside the writer lock), and records the same after. Writes DIR/downloads_item5.json and the
tool's output DIR/verify_downloads.log. Exit 0 when the two rows are gone, every other row id is
unchanged, the files are byte-identical, and verify-downloads failed only on the known
gr-qc/9412071 (or not at all); exit 1 otherwise. The raw files are only hashed, never opened as
code. Standard library only.
"""
import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys

HOME = "/data/haiyangw/nrpic"
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
DB = os.path.join(HOME, "kb-data", "db", "kb.sqlite")
RAW = os.path.join(HOME, "kb-data", "raw", "arxiv")
IDS = ("0707.4654", "1006.1632")
KNOWN = "gr-qc/9412071"


def files_sha(pid):
    out = {}
    base = os.path.join(RAW, pid.replace("/", "_"))
    for root, _d, files in os.walk(base):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for b in iter(lambda: f.read(1 << 20), b""):
                    h.update(b)
            out[os.path.relpath(p, base)] = h.hexdigest()
    return out


def table():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = {r[0]: r[1:] for r in con.execute("SELECT paper_id, in_manifest, status FROM downloads")}
    con.close()
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    before = {"rows": table(), "files": {i: files_sha(i) for i in IDS}}
    p = subprocess.run([sys.executable, "-I", os.path.join(WT, "kb", "bin", "kb"), "verify-downloads"],
                       capture_output=True, text=True, cwd=WT)
    with open(os.path.join(a.out, "verify_downloads.log"), "w") as f:
        f.write(p.stdout + "\n--- stderr ---\n" + p.stderr)
    after = {"rows": table(), "files": {i: files_sha(i) for i in IDS}}
    problems = sorted(k for k, v in after["rows"].items() if v[1] == "problem")
    res = {
        "verify_downloads_exit": p.returncode,
        "rows_before": len(before["rows"]), "rows_after": len(after["rows"]),
        "ids_before": {i: i in before["rows"] for i in IDS}, "ids_after": {i: i in after["rows"] for i in IDS},
        "other_ids_unchanged": sorted(set(before["rows"]) - set(IDS)) == sorted(after["rows"]),
        "files_unchanged": before["files"] == after["files"],
        "n_files": {i: len(after["files"][i]) for i in IDS},
        "problem_rows_after": problems,
        "gr-qc/0608095_present": "gr-qc/0608095" in after["rows"],
    }
    ok = (not any(res["ids_after"].values()) and res["other_ids_unchanged"] and res["files_unchanged"]
          and p.returncode in (0, 1) and set(problems) <= {KNOWN})
    res["predictions_hold"] = ok
    json.dump(res, open(os.path.join(a.out, "downloads_item5.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
