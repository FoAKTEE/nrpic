"""Step 3 scorer of the KB-G2 verifier (the verifier's own code).

Reads the raw `kb search --json` outputs of run_search.py and the expected answers, and
writes per question and mode: rank of the right paper, rank of the first hit at the answer
location (strict overlap, and overlap within SLACK characters), into score.<set>.json/.tsv
in $NRPIC_RUN_DIR, plus a summary.

Expected answers:
  heldout: tracks/kb/verify_g2/heldout.yaml (paper_id, version, locator {file, lines})
  golden : kb/golden/questions.yaml, read by load_golden (expected paper ids and locators).
Paper ids are compared after stripping a version suffix and an 'arXiv:' prefix.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vg2common as C  # noqa: E402
import locmap as L  # noqa: E402

import yaml

SLACK = 200


def norm_id(x):
    x = str(x or "").strip()
    x = re.sub(r"^(arxiv:)", "", x, flags=re.I)
    return re.sub(r"v\d+$", "", x)


def load_heldout(path, con):
    d = yaml.safe_load(open(path))
    out = []
    for q in d["questions"]:
        loc = q["locator"]
        out.append(dict(qid=q["id"], question=q["question"], papers=[norm_id(q["paper_id"])],
                        locs=[dict(paper=norm_id(q["paper_id"]), version=q["version"], file=loc["file"],
                                   a=loc["lines"][0], b=loc["lines"][1])]))
    return out


def _parse_loc_string(s):
    """'file.tex:L12-34' or 'file.tex:12-34' or 'file.tex:L12' -> (file, a, b) or None."""
    m = re.match(r"^\s*([^:\s]+):L?(\d+)(?:\s*-\s*L?(\d+))?\s*$", str(s))
    if not m:
        return None
    a = int(m.group(2))
    return m.group(1), a, int(m.group(3) or a)


def load_golden(path, con):
    d = yaml.safe_load(open(path))
    qs = d["questions"] if isinstance(d, dict) else d
    out = []
    for q in qs:
        qid = str(q.get("id") or q.get("qid"))
        text = q.get("question") or q.get("query") or q.get("q")
        papers = q.get("expect_papers") or q.get("papers") or q.get("expected_papers") or q.get("paper_ids") \
            or q.get("paper") or q.get("paper_id") or q.get("expect") or []
        if isinstance(papers, (str, int, float)):
            papers = [papers]
        papers = [norm_id(p if not isinstance(p, dict) else (p.get("paper") or p.get("paper_id"))) for p in papers]
        raw_locs = q.get("locators") or q.get("locator") or q.get("expect_locators") or q.get("answer_locators") or []
        if isinstance(raw_locs, (str, dict)):
            raw_locs = [raw_locs]
        locs = []
        for r in raw_locs:
            pid = papers[0] if papers else None
            if isinstance(r, dict):
                pid = norm_id(r.get("paper") or r.get("paper_id") or pid)
                if "char_start" in r or "chars" in r:
                    cs, ce = (r["chars"] if "chars" in r else (r["char_start"], r["char_end"]))
                    locs.append(dict(paper=pid, chars=(int(cs), int(ce))))
                    continue
                f = r.get("file")
                lines = r.get("lines")
                if f and lines:
                    if isinstance(lines, str):
                        m = re.match(r"L?(\d+)(?:-L?(\d+))?", lines)
                        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
                    else:
                        a, b = lines[0], lines[-1]
                    locs.append(dict(paper=pid, file=f, a=a, b=b))
                    continue
                s = r.get("loc") or r.get("source")
                if s:
                    t = _parse_loc_string(s)
                    if t:
                        locs.append(dict(paper=pid, file=t[0], a=t[1], b=t[2]))
            else:
                t = _parse_loc_string(r)
                if t:
                    locs.append(dict(paper=pid, file=t[0], a=t[1], b=t[2]))
        for l in locs:
            if "file" in l:
                row = con.execute("select version from papers where paper_id=?", (l["paper"],)).fetchone()
                l["version"] = row[0] if row else None
        out.append(dict(qid=qid, question=text, papers=papers, locs=locs))
    return out


def expected_ranges(q, con, cache):
    rngs = []
    for l in q["locs"]:
        pid = l["paper"]
        if "chars" in l:
            rngs.append(dict(paper=pid, start=l["chars"][0], end=l["chars"][1], how="chars", ok=True))
            continue
        key = (pid, l.get("version"), l["file"], l["a"], l["b"])
        if key in cache:
            rngs.append(cache[key])
            continue
        fp = L.flat_path(pid)
        row = con.execute("select flat_sha256 from papers where paper_id=?", (pid,)).fetchone()
        rec = dict(paper=pid, file=l["file"], a=l["a"], b=l["b"], how="lines")
        if not os.path.exists(fp) or row is None:
            rec.update(ok=False, reason="no flat.tex or paper not in snapshot")
        else:
            sha = L.sha256_file(fp)
            rec["flat_sha_matches_snapshot"] = (sha == row[0])
            m = L.map_lines(pid, l["version"], l["file"], l["a"], l["b"])
            rec.update(start=m["start"], end=m["end"], n_content=m["n_content"], n_found=m["n_found"])
            t = L.tool_range(pid, l["file"], l["a"], l["b"])
            rec["tool_range"] = t
            rec["ok"] = m["start"] is not None and rec["flat_sha_matches_snapshot"]
            if not rec["flat_sha_matches_snapshot"]:
                rec["reason"] = "flat.tex changed since the snapshot"
        cache[key] = rec
        rngs.append(rec)
    return rngs


def score_one(hits, q, rngs):
    paper_rank = loc_strict = loc_slack = None
    for h in hits:
        pid = norm_id(h.get("paper_id"))
        r = h.get("rank")
        if pid in q["papers"] and paper_rank is None:
            paper_rank = r
        cs, ce = h.get("char_start"), h.get("char_end")
        if cs is None or ce is None:
            continue
        for g in rngs:
            if not g.get("ok") or g["paper"] != pid:
                continue
            if cs < g["end"] and ce > g["start"] and loc_strict is None:
                loc_strict = r
            if cs < g["end"] + SLACK and ce > g["start"] - SLACK and loc_slack is None:
                loc_slack = r
    return paper_rank, loc_strict, loc_slack


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True)
    ap.add_argument("--questions", required=True)
    ap.add_argument("--raw", required=True, help="directory raw/<set> of a run_search run")
    ap.add_argument("--modes", default="text,hybrid,rerank")
    ap.add_argument("--db", default=C.SNAP)
    a = ap.parse_args()
    con = C.open_ro(a.db)
    qs = (load_heldout if a.set == "heldout" else load_golden)(a.questions, con)
    cache, rows = {}, []
    for q in qs:
        rngs = expected_ranges(q, con, cache)
        for mode in a.modes.split(","):
            p = os.path.join(a.raw, f"{q['qid']}.{mode}.json")
            try:
                d = json.load(open(p))
                hits = d["hits"] if isinstance(d, dict) else d
                err = None
            except Exception as e:  # missing or empty output counts as a miss, recorded
                hits, err = [], f"{type(e).__name__}"
            pr, ls, lk = score_one(hits, q, rngs)
            rows.append(dict(set=a.set, qid=q["qid"], mode=mode, expected=q["papers"], n_hits=len(hits),
                             paper_rank=pr, loc_rank_strict=ls, loc_rank_slack=lk,
                             loc_scorable=any(g.get("ok") for g in rngs), error=err,
                             top_papers=[h.get("paper_id") for h in hits[:10]]))
    rd = C.run_dir()
    summ = {}
    for mode in a.modes.split(","):
        rr = [r for r in rows if r["mode"] == mode]
        n = len(rr)
        ns = sum(r["loc_scorable"] for r in rr)
        summ[mode] = dict(n=n, paper_hits=sum(r["paper_rank"] is not None for r in rr),
                          loc_scorable=ns,
                          loc_hits_strict=sum(r["loc_rank_strict"] is not None for r in rr),
                          loc_hits_slack=sum(r["loc_rank_slack"] is not None for r in rr),
                          paper_rank1=sum(r["paper_rank"] == 1 for r in rr),
                          errors=sum(r["error"] is not None for r in rr))
        s = summ[mode]
        s["paper_rate"] = round(s["paper_hits"] / n, 4) if n else None
        s["loc_rate_strict"] = round(s["loc_hits_strict"] / n, 4) if n else None
        s["loc_rate_slack"] = round(s["loc_hits_slack"] / n, 4) if n else None
    out = dict(set=a.set, db=a.db, slack_chars=SLACK, summary=summ, rows=rows,
               expected_ranges={f"{k[0]}|{k[2]}|{k[3]}-{k[4]}": v for k, v in cache.items()},
               questions=[dict(qid=q["qid"], papers=q["papers"], n_locs=len(q["locs"])) for q in qs])
    with open(os.path.join(rd, f"score.{a.set}.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    with open(os.path.join(rd, f"score.{a.set}.tsv"), "w") as f:
        f.write("set\tqid\tmode\texpected\tpaper_rank\tloc_rank_strict\tloc_rank_slack\tloc_scorable\n")
        for r in rows:
            f.write(f"{r['set']}\t{r['qid']}\t{r['mode']}\t{','.join(r['expected'])}\t{r['paper_rank']}\t"
                    f"{r['loc_rank_strict']}\t{r['loc_rank_slack']}\t{r['loc_scorable']}\n")
    print(json.dumps(summ, indent=1))
    bad = [v for v in cache.values() if not v.get("ok")]
    print(f"expected ranges: {len(cache)}, not scorable: {len(bad)}")
    for v in bad:
        print("  not scorable:", {k: v.get(k) for k in ("paper", "file", "a", "b", "reason", "n_found")})
    agree = [v for v in cache.values() if v.get("ok") and v.get("tool_range")]
    for v in agree:
        t = v["tool_range"]
        d0 = abs((t["start"] or 0) - v["start"])
        print(f"  map check {v['paper']} {v['file']}:{v['a']}-{v['b']} mine [{v['start']},{v['end']}) "
              f"tool [{t['start']},{t['end']}) |d_start|={d0} found {v['n_found']}/{v['n_content']}")


if __name__ == "__main__":
    main()
