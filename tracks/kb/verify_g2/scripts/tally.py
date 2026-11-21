"""Final tally of the KB-G2 verifier for C3 (parse success) from registered outputs:
the parse scan (scan.json), the leniency check (lenient.json) and the genuine gaps read at the
source (JOURNAL entry 9, passed as --gaps). Cross-tabulates the recorded parse_status against the
verifier's definition, lists the papers on which they disagree, and checks that the metadata
abstract is served to a reader for papers without an abstract chunk (`kb show --abstract` on
the snapshot), which the lenient component A' relies on.
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vg2common as C  # noqa: E402

WT = "/data/haiyangw/nrpic/wt/kb"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    ap.add_argument("--lenient", required=True)
    ap.add_argument("--gaps", required=True, help="comma-separated ids judged genuine gaps at the source")
    ap.add_argument("--letters", required=True, help="comma-separated ids of letters with run-in headings")
    a = ap.parse_args()
    rows = json.load(open(a.scan))["rows"]
    gaps, letters = set(a.gaps.split(",")), set(a.letters.split(","))
    n = len(rows)
    res = {"n": n}
    ok = {r["paper_id"] for r in rows if r["status"] == "ok"}
    strict = {r["paper_id"] for r in rows if r["success"]} - gaps
    mine = {r["paper_id"] for r in rows if r["success_lenient"]} - gaps
    res["status_ok"] = len(ok)
    res["mine_lenient_corrected"] = len(mine)
    res["mine_lenient_corrected_letters_failed"] = len(mine - letters)
    res["mine_strict_corrected"] = len(strict)
    for k in ("status_ok", "mine_lenient_corrected", "mine_lenient_corrected_letters_failed", "mine_strict_corrected"):
        res["rate_" + k] = round(res[k] / n, 4)
    res["bar_papers_needed"] = 0.95 * n
    st = {r["paper_id"]: r["status"] for r in rows}
    res["crosstab"] = dict(collections.Counter(f"{st[p]}|{'pass' if p in mine else 'fail'}" for p in st))
    byid = {r["paper_id"]: r for r in rows}

    def why(p):
        r = byid[p]
        f = [k for k in ("S", "E", "B") if not r[k]]
        if not r["A_lenient"]:
            f.append("A'")
        if p in gaps:
            f.append("gap at source (entry 9)")
        return f
    res["ok_but_fail_mine"] = {p: why(p) for p in sorted(ok - mine)}
    res["not_ok_but_pass_mine"] = {p: st[p] for p in sorted(mine - ok)}
    # sensitivity: S needs only >= 1 section; papers of mine with fewer than half of the
    # sectioning commands the verifier counts
    res["mine_with_partial_sections"] = sorted(p for p in mine if byid[p]["my_sec"] >= 2
                                               and byid[p]["db_sec"] < 0.5 * byid[p]["my_sec"])
    # A' relies on the metadata abstract being served: check kb show --abstract on papers
    # without an abstract chunk
    noabs = sorted(r["paper_id"] for r in rows if not r["db_abs_chunk"])
    con = C.open_ro()
    meta = dict(con.execute("select paper_id, abstract from papers").fetchall())
    served = {}
    for p in noabs[:8]:
        pr = subprocess.run([os.path.join(WT, "kb/.venv/bin/python"), "-I", os.path.join(WT, "kb/bin/kb"), "show", p,
                             "--abstract", "--db", C.SNAP], cwd=WT, capture_output=True, text=True, timeout=300)
        wm = set(re.findall(r"[a-z]{4,}", (meta.get(p) or "").lower()))
        wo = set(re.findall(r"[a-z]{4,}", pr.stdout.lower()))
        served[p] = dict(rc=pr.returncode, out_chars=len(pr.stdout),
                         recall_of_metadata_words=round(len(wm & wo) / len(wm), 3) if wm else None)
    res["papers_without_abstract_chunk"] = len(noabs)
    res["kb_show_abstract_on_them"] = served
    with open(os.path.join(C.run_dir(), "tally.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
