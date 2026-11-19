"""Test P of the KB-G1 verifier: twenty papers, knowledge base against my own TeX count.

Usage: python3 check_papers.py <outdir>   (db: kb-data/db/current, opened read-only)
Writes <outdir>/papers.json and <outdir>/papers.tsv. No paper text is written.
"""
import difflib
import json
import re
import os
import random
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import texcount  # noqa: E402  (my own module, not the knowledge base's)

ROOT = "/data/haiyangw/nrpic/kb-data"
DB = os.path.join(ROOT, "db", "current")
SEED = 20261119


def connect():
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def sample(c):
    rows = c.execute("select paper_id, priority from papers where source_kind='tex' "
                     "order by paper_id").fetchall()
    p3 = [r[0] for r in rows if r[1] == 3]
    rest = [r[0] for r in rows if r[1] != 3]
    rng = random.Random(SEED)
    return sorted(rng.sample(p3, 10)) + sorted(rng.sample(rest, 10))


def kb_numbers(c, pid):
    p = c.execute("select version, main_tex, parse_status, priority, grp from papers where paper_id=?",
                  (pid,)).fetchone()
    eq = dict(c.execute("select env, count(*) from equations where paper_id=? group by env",
                        (pid,)).fetchall())
    nums = [r[0] for r in c.execute("select number from equations where paper_id=? order by char_start",
                                    (pid,)).fetchall()]
    secs = c.execute("select level, number, title from sections where paper_id=? "
                     "order by char_start", (pid,)).fetchall()
    bib = dict(c.execute("select source, count(*) from bib_entries where paper_id=? group by source",
                         (pid,)).fetchall())
    return {
        "version": p[0], "main_tex": p[1], "parse_status": p[2], "priority": p[3], "grp": p[4],
        "eq_by_env": eq, "n_eq": sum(eq.values()),
        "n_numbered": sum(1 for n in nums if n), "numbers": nums,
        "max_int_number": max([int(n) for n in nums if n and n.isdigit()], default=0),
        "n_steps": len({re.sub(r"[a-z]$", "", n) for n in nums if n}),
        "sections": [{"level": l, "number": n, "title": t} for (l, n, t) in secs],
        "n_sec_by_level": {str(l): sum(1 for s in secs if s[0] == l) for l in (1, 2, 3)},
        "n_sec_level0": sum(1 for s in secs if s[0] == 0),
        "bib_by_source": bib, "n_bib": sum(bib.values()),
    }


def within(a, b):
    return abs(a - b) <= max(2, 0.03 * max(a, b))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    c = connect()
    ids = sample(c)
    res = []
    for pid in ids:
        kb = kb_numbers(c, pid)
        src = os.path.join(ROOT, "raw", "arxiv", pid.replace("/", "_"), kb["version"], "src")
        mine = texcount.analyse(src)
        # titles: fraction of my section titles found among the knowledge base's
        kb_t = [texcount.norm_title(s["title"] or "") for s in kb["sections"] if s["level"] in (1, 2, 3)]
        my_t = [texcount.norm_title(s["title"]) for s in mine.get("sections", [])]
        found = sum(1 for a, b in zip(my_t, kb_t)
                    if difflib.SequenceMatcher(None, a, b).ratio() >= 0.8)
        kb_src = max(kb["bib_by_source"], key=kb["bib_by_source"].get) if kb["bib_by_source"] else None
        my_same = mine.get("bib", {}).get(kb_src) if kb_src else None
        r = {
            "paper_id": pid, "kb": kb, "mine": mine, "src": src,
            "titles_found": found, "titles_mine": len(my_t),
            "kb_bib_source": kb_src, "my_bib_same_source": my_same,
            "eq_ok": (within(kb["n_eq"], mine.get("n_rec_rule", -99))
                      and within(kb["n_numbered"], mine.get("n_numbered", -99))
                      and within(kb["n_steps"], mine.get("n_steps_all", -99))),
            "sec_ok": all(within(kb["n_sec_by_level"][k], mine["n_sec_by_level"][k]) for k in "123"),
            "bib_ok": (my_same is not None and within(kb["n_bib"], my_same)),
        }
        # sections: strip positions for compact output
        for s in mine.get("sections", []):
            s.pop("pos", None)
        res.append(r)
    with open(os.path.join(out, "papers.json"), "w") as f:
        json.dump({"seed": SEED, "db": os.path.realpath(DB), "papers": res}, f, indent=1)
    with open(os.path.join(out, "papers.tsv"), "w") as f:
        f.write("paper_id\tprio\tkb_main\tmy_main\tkb_eq\tmy_envs\tmy_rec\tkb_numbered\tmy_numbered\tkb_maxint\tmy_steps_main\tkb_steps\tmy_steps_all\tkb_sec1/2/3\tmy_sec1/2/3\t"
                "eqno\ttitles_found\tkb_bib\tkb_bib_src\tmy_bib_same_src\tmy_bib_all\teq_ok\tsec_ok\tbib_ok\n")
        for r in res:
            kb, mi = r["kb"], r["mine"]
            ks = "/".join(str(kb["n_sec_by_level"][k]) for k in "123")
            ms = "/".join(str(mi["n_sec_by_level"][k]) for k in "123")
            mb = {k: v for k, v in mi["bib"].items() if k in ("bbl", "bib", "thebibliography", "aastex_references", "plain_ref_items") and v}
            f.write(f"{r['paper_id']}\t{kb['priority']}\t{kb['main_tex']}\t{mi['main']}\t{kb['n_eq']}\t"
                    f"{mi['n_eq']}\t{mi['n_rec_rule']}\t{kb['n_numbered']}\t{mi['n_numbered']}\t{kb['max_int_number']}\t{mi['n_steps_main']}\t{kb['n_steps']}\t{mi['n_steps_all']}\t{ks}\t{ms}\t{mi['eqno']}\t{r['titles_found']}/{r['titles_mine']}\t{kb['n_bib']}\t"
                    f"{r['kb_bib_source']}\t{r['my_bib_same_source']}\t{json.dumps(mb)}\t"
                    f"{int(r['eq_ok'])}\t{int(r['sec_ok'])}\t{int(r['bib_ok'])}\n")
    print(open(os.path.join(out, "papers.tsv")).read())


if __name__ == "__main__":
    main()
