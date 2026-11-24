"""Item 5: the parse rate by my own definition (JOURNAL entry 1, item 5), on the snapshot.

A paper is parsed when all hold:
 (i)   TeX source (source_kind tex);
 (ii)  body+appendix chunks hold >= 1500 words, or >= 50 % of the words of my flattening;
 (iii) an abstract chunk of >= 20 words;
 (iv)  section rows >= 70 % of my \\section/\\subsection count (when I count any);
 (v)   equation rows >= 70 % of my display count (when I count >= 3);
 (vi)  when I find cited keys: >= 80 % of them have a bibliography entry.

python3 -I parse_rate.py --out DIR  ->  DIR/parse_papers.tsv, DIR/parse_summary.json
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vcommon as vc  # noqa: E402
from draw_bib import my_cited_keys  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    c = vc.connect()
    papers = c.execute("select paper_id, version, source_kind, parse_status from papers order by paper_id").fetchall()
    words = collections.defaultdict(lambda: [0, 0])
    for pid, kind, text in c.execute("select paper_id, kind, text from chunks"):
        if kind in ("body", "appendix"):
            words[pid][0] += vc.word_count(text)
        elif kind == "abstract":
            words[pid][1] += vc.word_count(text)
    nsec = dict(c.execute("select paper_id, count(*) from sections group by paper_id"))
    neq = dict(c.execute("select paper_id, count(*) from equations group by paper_id"))
    keys = collections.defaultdict(set)
    for pid, k in c.execute("select paper_id, cite_key from bib_entries"):
        keys[pid].add(k)
    fails = collections.Counter()
    rows = []
    for pid, ver, kind, status in papers:
        r = {"paper_id": pid, "version": ver, "source_kind": kind, "recorded": status}
        f = []
        if kind != "tex":
            f.append("i")
            r.update(my_words=0, my_sections=0, my_displays=0, my_keys=0)
        else:
            main_, flat = vc.own_flat(pid, ver)
            flat = flat or ""
            mw = vc.word_count(vc.body_of(flat))
            ms = vc.section_count(flat)
            md = vc.display_count(flat)
            mk, _ = my_cited_keys(flat)
            r.update(my_main=main_, my_words=mw, my_sections=ms, my_displays=md, my_keys=len(mk))
            bw, aw = words.get(pid, [0, 0])
            if not (bw >= 1500 or (mw > 0 and bw >= 0.5 * mw)):
                f.append("ii")
            if aw < 20:
                f.append("iii")
            if ms > 0 and nsec.get(pid, 0) < 0.7 * ms:
                f.append("iv")
            if md >= 3 and neq.get(pid, 0) < 0.7 * md:
                f.append("v")
            if mk:
                have = sum(1 for k in mk if k in keys.get(pid, ()))
                r["keys_with_entry"] = have
                if have < 0.8 * len(mk):
                    f.append("vi")
        r.update(db_body_words=words.get(pid, [0, 0])[0], db_abstract_words=words.get(pid, [0, 0])[1],
                 db_sections=nsec.get(pid, 0), db_equations=neq.get(pid, 0), db_entries=len(keys.get(pid, ())),
                 fails=",".join(f), parsed=int(not f))
        for x in f:
            fails[x] += 1
        rows.append(r)
    cols = ["paper_id", "version", "source_kind", "recorded", "parsed", "fails", "my_words", "db_body_words",
            "db_abstract_words", "my_sections", "db_sections", "my_displays", "db_equations", "my_keys",
            "keys_with_entry", "db_entries", "my_main"]
    with open(os.path.join(a.out, "parse_papers.tsv"), "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(k, "")) for k in cols) + "\n")
    n = len(rows)
    ok = sum(r["parsed"] for r in rows)
    rec_ok = sum(1 for r in rows if r["recorded"] == "ok")
    both = collections.Counter((r["recorded"], r["parsed"]) for r in rows)
    summ = {"snapshot": vc.SNAPSHOT, "papers": n, "parsed_own": ok, "rate_own": ok / n,
            "recorded_ok": rec_ok, "rate_recorded": rec_ok / n,
            "fails_by_criterion": dict(fails),
            "only_one_failure": dict(collections.Counter(r["fails"] for r in rows if r["fails"] and "," not in r["fails"])),
            "recorded_vs_own": {"%s/%d" % k: v for k, v in sorted(both.items())}}
    with open(os.path.join(a.out, "parse_summary.json"), "w") as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
