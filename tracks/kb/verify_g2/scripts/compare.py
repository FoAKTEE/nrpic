"""Step 9 of the KB-G2 verifier (after the verdicts were committed): counts needed to compare
with the package. From the registered parse scan: TeX papers with no bibliography entry in the
snapshot, split by whether they cite (\\cite) and by recorded status. From the run manifests the
package names as failed: their recorded status and exit code.
Usage: compare.py --scan SCAN_JSON --runs RUN_ID[,RUN_ID...]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vg2common as C  # noqa: E402

WT = "/data/haiyangw/nrpic/wt/kb"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    ap.add_argument("--runs", required=True)
    a = ap.parse_args()
    rows = json.load(open(a.scan))["rows"]
    tex0 = [r for r in rows if r["kind"] == "tex" and r["db_bib"] == 0]
    res = dict(tex_papers_without_bib_entry=len(tex0),
               of_them_citing=sum(1 for r in tex0 if r["my_cite_cmds"] > 0),
               of_them_status_ok=sum(1 for r in tex0 if r["status"] == "ok"),
               of_them_status_ok_citing=sum(1 for r in tex0 if r["status"] == "ok" and r["my_cite_cmds"] > 0),
               ids=sorted(r["paper_id"] for r in tex0),
               ok_citing_ids=sorted(r["paper_id"] for r in tex0 if r["status"] == "ok" and r["my_cite_cmds"] > 0))
    runs = {}
    for rid in a.runs.split(","):
        p = os.path.join(WT, "tracks/kb/runs", rid, "manifest.json")
        if not os.path.exists(p):
            runs[rid] = "no manifest"
            continue
        m = json.load(open(p))
        runs[rid] = dict(status=m.get("status"), exit_code=m.get("exit_code"),
                         purpose=str(m.get("purpose"))[:100])
    res["named_runs"] = runs
    with open(os.path.join(C.run_dir(), "compare.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
