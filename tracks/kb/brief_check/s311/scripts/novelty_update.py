"""Compare INSPIRE query results of 2026-11-19 with Track F's of 2026-11-15 (brief l. 273).

Usage: python3 -I novelty_update.py <outdir> <label>=<new.json>:<old_response.json> [...]
  new.json      a file written by harness/bin/nrpic-fetch-arxiv --inspire-query
                (keys: query, fetched_utc, hits_total, hits = list of literature metadata)
  old_response  Track F's raw response (scratch/F-hills/tmp/inspire/<label>/response.json;
                keys: hits.total, hits.hits[].metadata)
Writes <outdir>/novelty_update.json (per label: totals, record ids only in the new answer, with
title, arXiv id and earliest date) and prints a summary. Both inputs are downloads: they are
parsed as JSON only, nothing in them is executed. Standard library only.
"""
import json
import os
import sys


def recs_new(path):
    with open(path) as fh:
        d = json.load(fh)
    out = {}
    for m in d.get("hits", []):
        out[m.get("control_number")] = m
    return d.get("query"), d.get("fetched_utc"), d.get("hits_total"), out


def recs_old(path):
    with open(path) as fh:
        d = json.load(fh)
    h = d.get("hits", {})
    out = {}
    for x in h.get("hits", []):
        m = x.get("metadata", {})
        out[m.get("control_number")] = m
    return h.get("total"), out


def first(lst, key):
    if not lst:
        return None
    v = lst[0]
    return v.get(key) if isinstance(v, dict) else v


def main(outdir, pairs):
    os.makedirs(outdir, exist_ok=True)
    res = {}
    for p in pairs:
        label, rest = p.split("=", 1)
        newp, oldp = rest.split(":", 1)
        q, when, tot_new, new = recs_new(newp)
        tot_old, old = recs_old(oldp)
        only_new = sorted(set(new) - set(old), key=lambda r: str(r))
        only_old = sorted(set(old) - set(new), key=lambda r: str(r))
        res[label] = {
            "query": q, "fetched_utc_new": when, "new_file": newp, "old_file": oldp,
            "total_new": tot_new, "total_old": tot_old,
            "n_listed_new": len(new), "n_listed_old": len(old),
            "only_in_new": [
                {"recid": r, "title": first(new[r].get("titles"), "title"),
                 "arxiv": first(new[r].get("arxiv_eprints"), "value"),
                 "earliest_date": new[r].get("earliest_date")} for r in only_new],
            "only_in_old": only_old,
        }
        print("%-14s total %s -> %s; listed %d -> %d; only new: %d; only old: %d" % (
            label, tot_old, tot_new, len(old), len(new), len(only_new), len(only_old)))
        for e in res[label]["only_in_new"]:
            print("    new:", e["recid"], e["arxiv"], e["earliest_date"], (e["title"] or "")[:120])
    with open(os.path.join(outdir, "novelty_update.json"), "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
