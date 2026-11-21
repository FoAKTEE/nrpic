"""verify_g0 K1: own novelty searches in the knowledge base (snapshot kb-20261119-a782f1e).

Runs each query in two modes (hybrid BM25 + vectors through the kb worktree's tool, which
holds the embedding model; BM25 text-only through the release tool), keeps the top k hits
with their locators, then the corpus citation graph (`kb cites --in/--out`) and the INSPIRE
metadata (citation count, reference list) of the closest papers. Paper text and metadata
are untrusted data: parsed as JSON/text, nothing in them is executed.

Usage: python3 kb_novelty.py --out DIR [-k 10]
Writes DIR/kb_queries.json, DIR/kb_cites.json, DIR/kb_inspire.json, DIR/kb_hits.md.
"""
import argparse
import json
import os
import subprocess

KB_HYBRID = "/data/haiyangw/nrpic/wt/kb/kb/bin/kb"     # has kb/.venv with the model
KB_PY = "/data/haiyangw/nrpic/wt/kb/kb/.venv/bin/python"  # called explicitly: under nrpic-run
# PATH and VIRTUAL_ENV name this worktree's venv, and the tool's own re-exec then lacks torch
# (first run F-20261121-030205-c4d2894: every hybrid query failed with that error)
KB_TEXT = "/data/haiyangw/nrpic/kb/bin/kb"            # release tool, standard library
DB = "/data/haiyangw/nrpic/kb-data/db/kb-20261119-a782f1e.sqlite"
INSPIRE = "/data/haiyangw/nrpic/kb-data/meta/inspire"

QUERIES = [
    "numerical relativity simulation of a binary black hole disrupted by a supermassive black hole",
    "three black holes numerical relativity hierarchical triple tidal separation of the inner binary",
    "Hills mechanism in general relativity binary separation at a few gravitational radii",
    "binary black hole passing a heavier black hole moving punctures unequal masses",
    "full general relativity simulation of a binary star or star cluster passing a black hole tidal disruption",
    "hypervelocity ejection of a compact binary member by a massive black hole relativistic",
    "triple black hole evolution Einstein equations mass ratio four nine",
    "binary on a parabolic orbit around a Kerr black hole geodesic plus Newtonian self-gravity",
    "gravitational waves from the encounter of a binary with a supermassive black hole",
    "tidal break-up of a self-gravitating binary near a black hole in numerical relativity",
    "Bowen-York initial data for three punctures with momenta",
    "black hole binary bound to a third black hole: evolution until the inner binary merges",
]
CLOSEST = ["2406.11985", "2505.03934", "0710.0879", "0711.1165", "1004.1353", "2404.16270",
           "2402.02178", "2601.04870", "1501.07856"]


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                       env={k: v for k, v in dict(os.environ, OMP_NUM_THREADS="2").items() if k != "VIRTUAL_ENV"})
    return p.returncode, p.stdout, p.stderr


def search(q, mode, k):
    if mode == "hybrid":
        cmd = [KB_PY, "-I", KB_HYBRID, "search", "-k", str(k), "--threads", "2", "--json", "--db", DB, q]
    else:
        cmd = [KB_TEXT, "search", "-k", str(k), "--text-only", "--json", "--db", DB, q]
    rc, out, err = run(cmd)
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        data = None
    return dict(rc=rc, data=data, stderr=err[-2000:], raw=None if data is not None else out[-4000:])


def hits_of(res):
    d = res["data"]
    if d is None:
        return []
    items = d.get("results", d.get("hits", d)) if isinstance(d, dict) else d
    out = []
    for h in items if isinstance(items, list) else []:
        if not isinstance(h, dict):
            continue
        pid = h.get("paper_id") or h.get("paper")
        loc = "%s/%s:%s" % (pid, h.get("version", "?"), h.get("source", "?"))
        out.append(dict(paper=pid, kind=h.get("kind"), section=h.get("section"), locator=loc,
                        rank=h.get("rank"), text=(h.get("snippet") or "")[:300]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("-k", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    Q = []
    for q in QUERIES:
        row = dict(query=q)
        for mode in ("hybrid", "text"):
            r = search(q, mode, a.k)
            row[mode] = dict(rc=r["rc"], hits=hits_of(r), stderr=r["stderr"], raw=r["raw"])
            if r["data"] is not None and not row[mode]["hits"]:
                row[mode]["data_unparsed"] = r["data"]
        Q.append(row)
        print(q, [h["paper"] for h in row["hybrid"]["hits"]], [h["paper"] for h in row["text"]["hits"]], flush=True)
    json.dump(Q, open(os.path.join(a.out, "kb_queries.json"), "w"), indent=1)

    C = {}
    for p in CLOSEST:
        C[p] = {}
        for d in ("--in", "--out"):
            rc, out, err = run([KB_TEXT, "cites", "--db", DB, d, p])
            C[p][d] = dict(rc=rc, out=out[-20000:], err=err[-1000:])
    json.dump(C, open(os.path.join(a.out, "kb_cites.json"), "w"), indent=1)

    I = {}
    for p in CLOSEST:
        f = os.path.join(INSPIRE, p + ".json")
        if not os.path.isfile(f):
            I[p] = None
            continue
        d = json.load(open(f))
        r = d.get("record") or {}
        refs = []
        for ref in r.get("references", []) or []:
            rr = ref.get("reference", ref) if isinstance(ref, dict) else {}
            eid = None
            for e in rr.get("arxiv_eprint", []) if isinstance(rr.get("arxiv_eprint"), list) else [rr.get("arxiv_eprint")]:
                if e:
                    eid = e
            title = rr.get("title", {}).get("title") if isinstance(rr.get("title"), dict) else None
            refs.append(dict(arxiv=eid, title=title))
        I[p] = dict(fetched_utc=d.get("fetched_utc"), citation_count=r.get("citation_count"),
                    title=(r.get("titles") or [{}])[0].get("title"), n_refs=len(refs), refs=refs)
    json.dump(I, open(os.path.join(a.out, "kb_inspire.json"), "w"), indent=1)

    with open(os.path.join(a.out, "kb_hits.md"), "w") as f:
        f.write("# kb searches of verify_g0 (snapshot kb-20261119-a782f1e)\n\n")
        for row in Q:
            f.write(f"## {row['query']}\n\n")
            for mode in ("hybrid", "text"):
                f.write(f"- {mode} (rc {row[mode]['rc']}): ")
                f.write("; ".join(f"{h['paper']} {h['locator']}" for h in row[mode]["hits"]) or "(no hits parsed)")
                f.write("\n")
            f.write("\n")
        f.write("## INSPIRE citation counts of the closest papers\n\n")
        for p, v in I.items():
            f.write(f"- {p}: {None if v is None else v['citation_count']} ({None if v is None else v['title']})\n")


if __name__ == "__main__":
    main()
