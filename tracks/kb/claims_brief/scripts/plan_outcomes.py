#!/usr/bin/env python3
"""Plan the outcomes of the brief check for the brief seeds (package claims_brief, step 2).

Read only. Inputs: the join table of `kb claim seed-brief --join` (one row per CHECK.md row),
the ERRATA_ROWS.md files of the brief-check packages (git ref), coord/BRIEF_ERRATA.md, and the
knowledge-base database (read only) to resolve the TeX locators of each row.

Outputs (into --out):
  plan_rows.tsv    every CHECK.md row with its seed, its TeX locators and whether each resolves
                   in the database (paper ingested, file and lines found), its errata row ids
  plan_seeds.tsv   every seed that a row joined, with the action the rules below give
  sample.tsv       the review sample (stratified by package, seed recorded)
  summary.json     counts

Rules for a seed (claim) from the rows joined to it (JOURNAL entry "Rules of step 2"):
  judgement seed                 annotate (never verified or refuted from the literature, 12.8)
  any row CORRECTED whose errata row stands in section 1 (wrong or incomplete) or 3 (a TO
  VERIFY answered otherwise) of coord/BRIEF_ERRATA.md
                                 refute; evidence names the package rows and the errata rows
  rows CORRECTED, errata rows only in section 2 (imprecise)
                                 annotate-partial (status partial; label unchanged)
  all rows CONFIRMED or PRECISION, every row with >= 1 TeX locator that resolves in the
  database                       verify, locator = the first resolving locator of each row
  otherwise                      annotate (located, not checked)
Usage: python3 -I plan_outcomes.py --join J --kb KBDIR --repo REPO --ref REF --out DIR
"""
import argparse
import collections
import csv
import json
import os
import random
import re
import subprocess
import sys

PKGS = ["novelty", "s310", "s311", "s31_32", "s33", "s34_36", "s35", "s37_38", "s39_frontier", "s5_s6", "s7_s8"]
SAMPLE_SEED = 20261121
# 30 rows: 3 from each of the eight larger packages, 2 from the three smaller ones
SAMPLE_N = {"novelty": 2, "s7_s8": 2, "s39_frontier": 2}


def git_show(repo, ref, path):
    return subprocess.run(["git", "-C", repo, "show", f"{ref}:{path}"], capture_output=True, text=True,
                          check=True).stdout


def errata_rows(repo, ref):
    """{(package, CHECK row n): [provisional errata id]} and {provisional id: section}."""
    by_check, sec_of = collections.defaultdict(list), {}
    for p in PKGS:
        try:
            md = git_show(repo, ref, f"tracks/kb/brief_check/{p}/ERRATA_ROWS.md")
        except subprocess.CalledProcessError:
            continue
        sec = ""
        for line in md.split("\n"):
            m = re.match(r"^## (\d+)\.", line)
            if m:
                sec = m.group(1)
            if not line.startswith("| ") or line.startswith("| #") or line.startswith("|---"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rid = cells[0]
            if not re.match(r"^[a-z0-9_]+\.\d+$", rid):
                continue
            sec_of[rid] = sec
            for n in re.findall(r"CHECK\s*#\s*(\d+)", line):
                by_check[(p, int(n))].append(rid)
            for grp in re.findall(r"CHECK\s*#\s*\d+(?:\s*(?:,|and|-|–)\s*#?\s*\d+)+", line):
                for n in re.findall(r"\d+", grp):
                    if rid not in by_check[(p, int(n))]:
                        by_check[(p, int(n))].append(rid)
    return by_check, sec_of


def final_ids(brief_errata):
    """{provisional id: final row number of coord/BRIEF_ERRATA.md} from its evidence cells."""
    out = {}
    for line in open(brief_errata, encoding="utf-8"):
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rid = cells[0]
        if not re.match(r"^\d+\.\d+$", rid):
            continue
        for prov in re.findall(r"\b((?:s\d+|nov|s5_s6|s78|s7|s8|s31|s33|s34|s35|s36|s37|s38|s39|s310|s311)\.\d+)\b",
                               line):
            out.setdefault(prov, rid)
    return out


def _secs(r):
    """Sections of coord/BRIEF_ERRATA.md (final ids) or, without one, of the package's
    ERRATA_ROWS.md, of the errata rows of a CHECK.md row."""
    fin = [x for x in r["errata_final"].split(",") if x]
    return fin if fin else [x for x in r["errata_section"].split(",") if x]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--join", required=True)
    ap.add_argument("--kb", required=True, help="the kb/ directory whose kbtool is imported")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sys.path.insert(0, a.kb)
    from kbtool import claims_check as ck
    from kbtool import claims_db as cdb
    from kbtool.claims_parse import Locator
    from kbtool.paths import layout

    lay = layout(None)
    con = cdb.connect(lay.db_work, ro=True)
    store = ck.Store(lay.raw_arxiv, os.path.join(lay.build, "tex"), con)
    by_check, sec_of = errata_rows(a.repo, a.ref)
    fin = final_ids(os.path.join(a.repo, "coord", "BRIEF_ERRATA.md"))
    rows = list(csv.DictReader(open(a.join, encoding="utf-8"), delimiter="\t"))
    labels = {cid: lab for cid, lab in con.execute(
        "SELECT c.claim_id, c.label FROM claims c JOIN claim_meta m USING(claim_id) WHERE m.seed_key LIKE 'brief:v2:%'")}
    in_db = {}
    out_rows = []
    for r in rows:
        locs = [x.strip() for x in r["tex_locators"].split(";") if x.strip()]
        res = []
        for loc in locs:
            m = cdb.RE_LOC.match(loc)
            if not m:
                res.append((loc, False, "unparsed"))
                continue
            pid = m.group("pid")
            if pid not in in_db:
                in_db[pid] = con.execute("SELECT version FROM papers WHERE paper_id=?", (pid,)).fetchone()
            lo = Locator(pid, m.group("ver") or "", m.group("file").strip(), int(m.group("a")),
                         int(m.group("b") or m.group("a")), loc, 0)
            rr = store.resolve(lo)
            ok = bool(rr.resolved and in_db[pid])
            res.append((loc, ok, "" if ok else (rr.problem or "paper not in the database")))
        prov = by_check.get((r["package"], int(r["n"])), [])
        out_rows.append(dict(r, n_tex=len(locs), n_resolved=sum(1 for x in res if x[1]),
                             first_resolved=next((x[0] for x in res if x[1]), ""),
                             problems="; ".join(f"{x[0]}: {x[2]}" for x in res if not x[1]),
                             errata_prov=",".join(prov),
                             errata_final=",".join(fin.get(p, "") for p in prov),
                             errata_section=",".join(sec_of.get(p, "") for p in prov)))
    os.makedirs(a.out, exist_ok=True)
    cols = list(out_rows[0].keys())
    with open(os.path.join(a.out, "plan_rows.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in out_rows:
            f.write("\t".join(str(r[c]).replace("\t", " ") for c in cols) + "\n")

    seeds = collections.OrderedDict()
    for r in out_rows:
        if r["claim_id"]:
            seeds.setdefault(int(r["claim_id"]), []).append(r)
    plan = []
    for cid, rs in seeds.items():
        lab = labels.get(cid, rs[0]["seed_label"])
        verdicts = [r["verdict"] for r in rs]
        ev_rows = ", ".join(f"{r['package']} CHECK.md row {r['n']}" for r in rs)
        corr = [r for r in rs if r["verdict"] == "CORRECTED"]
        if lab == "judgement":
            action, loc = "annotate", ""
        elif corr and any(sec[:1] in ("1", "3") for r in corr for sec in _secs(r)):
            action = "refute"
            loc = "; ".join(r["first_resolved"] for r in corr if r["first_resolved"])
        elif corr:
            # corrected, but the errata put the correction among the imprecisions (section 2)
            action, loc = "annotate-partial", ""
        elif all(v in ("CONFIRMED", "PRECISION") for v in verdicts) and all(r["n_resolved"] > 0 for r in rs):
            action = "verify"
            loc = "; ".join(dict.fromkeys(r["first_resolved"] for r in rs))
        else:
            action, loc = "annotate", ""
        why = ("judgement seed" if lab == "judgement" else
               "corrected rows: " + ", ".join(f"{r['package']}#{r['n']}" for r in corr) +
               (" (errata section 2 only: an imprecision)" if action == "annotate-partial" else "") if corr else
               "all rows confirmed, all located in the database" if action == "verify" else
               "not every row has a locator in the database" if all(v in ("CONFIRMED", "PRECISION") for v in verdicts)
               else "verdicts " + ",".join(sorted(set(verdicts))))
        errata = sorted({e for r in corr for e in (r["errata_final"] or r["errata_prov"]).split(",") if e})
        plan.append({"claim_id": cid, "seed_key": rs[0]["seed_key"], "label": lab, "brief_line": rs[0]["brief_line"],
                     "n_rows": len(rs), "packages": ",".join(sorted({r["package"] for r in rs})),
                     "verdicts": ",".join(f"{k}:{v}" for k, v in sorted(collections.Counter(verdicts).items())),
                     "action": action, "why": why, "locator": loc, "evidence_rows": ev_rows,
                     "errata": ",".join(errata),
                     "errata_prov": ",".join(sorted({e for r in corr for e in r["errata_prov"].split(",") if e}))})
    pcols = list(plan[0].keys())
    with open(os.path.join(a.out, "plan_seeds.tsv"), "w") as f:
        f.write("\t".join(pcols) + "\n")
        for p in plan:
            f.write("\t".join(str(p[c]).replace("\t", " ") for c in pcols) + "\n")

    # review sample: stratified by package, seeded, from the rows with at least one TeX
    # locator (the reviewer reads the source), preferring rows joined to a seed
    rng = random.Random(SAMPLE_SEED)
    sample = []
    for p in PKGS:
        k = SAMPLE_N.get(p, 3)
        pool = [r for r in out_rows if r["package"] == p and r["n_tex"] > 0 and r["claim_id"]]
        if len(pool) < k:
            pool = pool + [r for r in out_rows if r["package"] == p and r["n_tex"] > 0 and not r["claim_id"]]
        pool = sorted(pool, key=lambda r: int(r["n"]))
        sample += rng.sample(pool, min(k, len(pool)))
    scols = ["package", "n", "brief_line", "verdict", "label_col", "claim_id", "seed_label", "tex_locators",
             "n_resolved", "errata_prov"]
    with open(os.path.join(a.out, "sample.tsv"), "w") as f:
        f.write("\t".join(scols) + "\n")
        for r in sample:
            f.write("\t".join(str(r[c]) for c in scols) + "\n")
    summ = {"rows": len(out_rows), "rows_joined": sum(1 for r in out_rows if r["claim_id"]),
            "rows_with_tex": sum(1 for r in out_rows if r["n_tex"]),
            "rows_all_tex_resolved": sum(1 for r in out_rows if r["n_tex"] and r["n_tex"] == r["n_resolved"]),
            "rows_some_tex_resolved": sum(1 for r in out_rows if r["n_resolved"]),
            "seeds_joined": len(plan),
            "actions": dict(collections.Counter(p["action"] for p in plan)),
            "actions_by_label": {f"{k[0]}/{k[1]}": v for k, v in
                                 sorted(collections.Counter((p["label"], p["action"]) for p in plan).items())},
            "corrected_rows": sum(1 for r in out_rows if r["verdict"] == "CORRECTED"),
            "corrected_rows_joined": sum(1 for r in out_rows if r["verdict"] == "CORRECTED" and r["claim_id"]),
            "corrected_rows_with_errata_id": sum(1 for r in out_rows if r["verdict"] == "CORRECTED" and r["errata_prov"]),
            "sample_seed": SAMPLE_SEED, "sample_size": len(sample),
            "papers_not_in_db": sorted(p for p, v in in_db.items() if not v)}
    json.dump(summ, open(os.path.join(a.out, "summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
