#!/usr/bin/env python3
"""Package claims4: the unread machine-located claims, their three reading classes, and the
seeded reading order.

    python3 -I population.py count [--db PATH]
    python3 -I population.py order --seed SEED --out DIR [--db PATH]

Definition (JOURNAL.md entry 1, written before the order was drawn):

  M   claims with label fulltext, abstract or title_only whose label was set by the automatic
      seeder and locator check (claim_meta.label_set_by = 'auto'; status located or partial),
  minus every claim a person has read against its wording or processed by name:
      - an event by a reader of the earlier passes: the audit P2 helper, the wave-2 and wave-2b
        leads, the leads of batches 13, 15 and 17, package claims3 (by values in READ_BY);
        an event whose evidence starts '[audit 2026-11-21' (claims_tracks/AUDIT.md);
      - a claim in the verdict files of the first KB-G3 verifier (sample_verdicts.tsv,
        refutations.tsv), of the second (verifier2 item1.tsv, sample_verdicts.tsv), or in
        claims3's SAMPLE_VERDICTS.tsv;
      - the leftovers of the second verifier that this package handles by name (LEFTOVERS) and
        the claims claims3 handled by name (NAMED3).
  Classes, disjoint, in reading order:
      C  text begins or ends in a cut (cut_start / cut_end below: a connector word such as
         'and', 'i.e.', 'which', 'see', 'at', 'for' first, punctuation first, or a last word,
         punctuation or unbalanced bracket that leaves the sentence open). A text that merely
         starts with a lower-case noun (a list item of a note) is not C; it is flagged 'lower'
         and its rate is reported separately;
      T  not C, and cited by a track: its id is named in a file under tracks/<ID>/ on the
         track's own branch (pattern 'kb claim N', 'claims N-M' with M-N < 20, on a line that
         says 'kb' or 'knowledge'), or one of its locator rows (file, line range) overlaps a TeX
         locator written in such a file ('<name>.tex:L123', '<name>.tex L12-20',
         '`<name>.tex:123`') other than the claim's own origin file, where the TeX file name
         belongs to one paper only in claim_locators or the citing line names the paper id;
      R  the rest.
  Order: within each class a permutation by random.Random(SEED); the classes in the order
  C, T, R. A reader who stops early has read a seeded random part of the class being read.
Read-only on the database and on git; standard library only.
"""
import argparse
import csv
import json
import os
import random
import re
import sqlite3
import subprocess

HOME = "/data/haiyangw/nrpic"
DB = os.path.join(HOME, "kb-data", "db", "kb.sqlite")
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
STAGE = os.path.join(WT, "tracks", "kb", "stage", "KB-G3")

READ_BY = ("kb claims helper (manual read, audit P2)", "kb lead (wave 2), read at the source",
           "kb lead (wave 2b)", "kb-lead-b13", "kb-lead-b15", "kb-lead-b17", "kb-claims3")
AUDIT_PREFIX = "[audit 2026-11-21"
NAMED3 = {803, 805, 81, 84, 85, 171, 179, 187, 192, 213, 277, 290, 314, 424, 431, 549,
          619, 620, 621, 622, 623, 625}
LEFTOVERS = {741, 428, 804, 805, 313, 430, 864, 877}
TRACKS = (("A-emd-pbh", "track/A-emd-pbh"), ("B-emd-gw", "track/B-emd-gw"), ("C-sidm", "track/C-sidm"),
          ("D-bh-dress", "track/D-bh-dress"), ("E-stoch-inf", "track/E-stoch-inf"),
          ("F-hills", "track/F-hills"), ("core", "core/nrpic"))

START_WORDS = {"and", "or", "but", "which", "that", "i.e.", "e.g.", "see", "where", "while", "so",
               "thus", "hence", "then", "with", "for", "as", "since", "because", "of", "in", "to",
               "by", "at", "on", "from", "than", "also", "both", "its", "their", "it", "this",
               "these", "they", "is", "are", "was", "were", "used", "using", "via", "plus"}
END_WORDS = {"and", "or", "of", "the", "a", "an", "to", "with", "is", "are", "by", "for", "in",
             "on", "as", "that", "which", "from", "at", "than", "be", "its", "their"}


def cut_start(text):
    t = (text or "").lstrip()
    if not t:
        return "empty"
    if t[0] in ")],;:.|}-":
        return "punct"
    w = t.split()[0].lower().rstrip(",;:")
    if w in START_WORDS:
        return "word:" + w
    return ""


def lower_start(text):
    t = (text or "").lstrip()
    return bool(t) and t[0].islower()


def cut_end(text):
    t = (text or "").rstrip()
    if not t:
        return "empty"
    if t[-1] in ",;:(|-":
        return "punct"
    if t.count("(") > t.count(")") or t.count("`") % 2:
        return "unbalanced"
    w = re.sub(r"[^\w.]+$", "", t.split()[-1].lower())
    if w in END_WORDS:
        return "word:" + w
    return ""


def git(*args):
    return subprocess.run(("git", "-C", WT) + args, capture_output=True, text=True).stdout


ID_RX = re.compile(r"\b(?:kb\s+)?claims?\s+(?:no\.\s*)?(\d{1,3})(?:\s*(?:-|to)\s*(\d{1,3}))?\b", re.I)
TEX_RX = re.compile(r"([A-Za-z0-9_+.-]+\.tex)`?\s*[:,]?\s*`?L?(\d{1,5})(?:\s*[-–]\s*L?(\d{1,5}))?")


def track_citations():
    """(ids, tex) where ids = {claim_id: [where]}, tex = [(track, path, line, file, l0, l1)]."""
    ids, tex = {}, []
    for tid, br in TRACKS:
        out = git("grep", "-I", "-n", "-E", r"(claim|\.tex)", br, "--", f"tracks/{tid}/")
        for line in out.splitlines():
            parts = line.split(":", 3)
            if len(parts) < 4:
                continue
            _br, path, ln, body = parts
            low = body.lower()
            if "kb" in low or "knowledge" in low:
                for m in ID_RX.finditer(body):
                    a = int(m.group(1))
                    b = int(m.group(2)) if m.group(2) else a
                    if b < a or b - a >= 20:
                        continue
                    for c in range(a, b + 1):
                        ids.setdefault(c, []).append(f"{tid}:{path}:{ln}")
            for m in TEX_RX.finditer(body):
                l0 = int(m.group(2))
                l1 = int(m.group(3)) if m.group(3) else l0
                if l1 < l0:
                    l1 = l0
                tex.append((tid, path, int(ln), m.group(1), l0, l1, body))
    return ids, tex


def verdict_ids():
    out = set()
    files = [os.path.join(STAGE, "verifier", "verdicts", n) for n in ("sample_verdicts.tsv", "refutations.tsv")]
    files += [os.path.join(STAGE, "verifier2", "verdicts", n) for n in ("item1.tsv", "sample_verdicts.tsv")]
    files += [os.path.join(WT, "tracks", "kb", "claims3", "SAMPLE_VERDICTS.tsv")]
    for p in files:
        with open(p) as f:
            for row in csv.DictReader(f, delimiter="\t"):
                try:
                    out.add(int(row["claim_id"]))
                except (KeyError, ValueError, TypeError):
                    pass
    return out


def population(con):
    rows = con.execute(
        "SELECT c.claim_id, c.label, m.status, m.track, c.paper_id, c.locator, c.text "
        "FROM claims c JOIN claim_meta m USING(claim_id) "
        "WHERE m.label_set_by='auto' AND c.label IN ('fulltext','abstract','title_only') "
        "AND m.status IN ('located','partial') ORDER BY c.claim_id").fetchall()
    read = {r[0] for r in con.execute(
        "SELECT DISTINCT claim_id FROM claim_events WHERE by IN (%s) OR evidence LIKE ?"
        % ",".join("?" * len(READ_BY)), READ_BY + (AUDIT_PREFIX + "%",))}
    ver = verdict_ids()
    excl = {"read_event": 0, "verdict_file": 0, "named": 0}
    pop = []
    for cid, label, status, track, pid, loc, text in rows:
        if cid in LEFTOVERS or cid in NAMED3:
            excl["named"] += 1
            continue
        if cid in ver:
            excl["verdict_file"] += 1
            continue
        if cid in read:
            excl["read_event"] += 1
            continue
        pop.append({"claim_id": cid, "label": label, "status": status, "track": track, "paper_id": pid,
                    "locator": loc or "", "text": text or ""})
    return len(rows), pop, excl


def classify(con, pop):
    ids, tex = track_citations()
    locs, papers_of = {}, {}
    for cid, pid, fn, l0, l1 in con.execute(
            "SELECT claim_id, paper_id, file, line_start, line_end FROM claim_locators"):
        if fn and l0:
            b = os.path.basename(fn)
            locs.setdefault(cid, []).append((pid, b, l0, l1 or l0))
            papers_of.setdefault(b, set()).add(pid)
    origin = {r[0]: r[1] for r in con.execute("SELECT claim_id, origin_path FROM claim_meta")}
    for r in pop:
        cid = r["claim_id"]
        cs, ce = cut_start(r["text"]), cut_end(r["text"])
        r["cut"] = ";".join(x for x in (("start=" + cs) if cs else "", ("end=" + ce) if ce else "") if x)
        r["lower"] = int(lower_start(r["text"]))
        cites = list(ids.get(cid, []))
        for pid, fn, a, b in locs.get(cid, []):
            for tid, path, ln, tfn, t0, t1, body in tex:
                if path == origin.get(cid) or tfn != fn or not (t0 <= b and a <= t1):
                    continue
                if len(papers_of.get(fn, ())) == 1 or (pid and pid in body):
                    cites.append(f"{tid}:{path}:{ln}")
        r["cited_by"] = ";".join(sorted(set(cites)))
        r["cls"] = "C" if r["cut"] else ("T" if cites else "R")
    return pop


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("count", "order"))
    ap.add_argument("--db", default=DB)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    n_m, pop, excl = population(con)
    pop = classify(con, pop)
    counts = {c: sum(1 for r in pop if r["cls"] == c) for c in "CTR"}
    info = {"db": a.db, "M_all": n_m, "M_unread": len(pop), "classes": counts, "excluded": excl,
            "lower_by_class": {c: sum(r["lower"] for r in pop if r["cls"] == c) for c in "CTR"},
            "by_track": {t: sum(1 for r in pop if r["track"] == t) for t in sorted({r["track"] for r in pop})}}
    if a.what == "count":
        print(json.dumps(info, indent=1))
        return 0
    if a.seed is None or not a.out:
        ap.error("order needs --seed and --out")
    rng = random.Random(a.seed)
    order = []
    for c in "CTR":
        part = sorted((r for r in pop if r["cls"] == c), key=lambda r: r["claim_id"])
        rng.shuffle(part)
        order += part
    os.makedirs(a.out, exist_ok=True)
    cols = ("k", "cls", "claim_id", "track", "paper_id", "cut", "lower", "cited_by", "locator", "text160")
    with open(os.path.join(a.out, "order.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for k, r in enumerate(order, 1):
            r["k"] = k
            r["text160"] = r["text"][:160].replace("\t", " ").replace("\n", " ")
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    info.update({"seed": a.seed})
    with open(os.path.join(a.out, "order.json"), "w") as f:
        json.dump(info, f, indent=1)
    print(json.dumps(info, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
