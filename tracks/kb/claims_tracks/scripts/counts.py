#!/usr/bin/env python3
"""Counts of the tracks' evidence queue in kb.sqlite (read-only), as tables and a figure.

    python3 tracks/kb/claims_tracks/scripts/counts.py --out DIR [--before DIR/counts.json] [--tag baseline|after]

Writes DIR/counts.json, DIR/counts_track_label_status.tsv, DIR/queue.tsv (claim ids of the
queue: label to_verify, judgement or background), and DIR/fig_<tag>.{pdf,png}. With
--before it also draws the queue before and after by track (fig_before_after). The database
is opened read-only; nothing under kb-data is written.
"""
import argparse
import collections
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DB = "/data/haiyangw/nrpic/kb-data/db/kb.sqlite"
TRACKS = ["A-emd-pbh", "B-emd-gw", "C-sidm", "D-bh-dress", "E-stoch-inf", "F-hills", "core"]
QUEUE = ("to_verify", "judgement", "background")
ME = "kb-claims_tracks"


def gather(db):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=60)
    rows = con.execute("SELECT c.claim_id, m.track, c.label, m.status, m.source_label, c.paper_id, "
                       "m.checked_by, m.label_set_by FROM claims c JOIN claim_meta m USING(claim_id) "
                       "ORDER BY c.claim_id").fetchall()
    ann = {r[0]: r[1] for r in con.execute(
        "SELECT claim_id, count(*) FROM claim_events WHERE action='annotate' GROUP BY 1")}
    mine = {r[0] for r in con.execute("SELECT DISTINCT claim_id FROM claim_events WHERE by=?", (ME,))}
    con.close()
    tls = collections.Counter()
    for cid, t, l, s, src, pid, cb, sb in rows:
        tls[(t, l, s)] += 1
    out = {"db": db, "claims": len(rows), "max_claim_id": max(r[0] for r in rows),
           "by_label": dict(collections.Counter(r[2] for r in rows)),
           "by_status": dict(collections.Counter(r[3] for r in rows)),
           "track_label_status": [[t, l, s, n] for (t, l, s), n in sorted(tls.items(), key=lambda x: tuple(map(str, x[0])))],
           "fulltext_checked": sum(1 for r in rows if r[2] == "fulltext" and r[3] == "checked"),
           "fulltext_machine_located": sum(1 for r in rows if r[2] == "fulltext" and r[3] != "checked"),
           "queue": [], "annotated": len(ann), "touched_by_me": len(mine)}
    for cid, t, l, s, src, pid, cb, sb in rows:
        if l in QUEUE:
            out["queue"].append({"claim_id": cid, "track": t, "label": l, "status": s, "source_label": src,
                                 "paper_id": pid, "annotated": ann.get(cid, 0)})
    out["queue_by_track"] = {t: dict(collections.Counter(f"{q['label']}/{q['status']}" for q in out["queue"]
                                                         if q["track"] == t)) for t in TRACKS}
    out["mine_ids"] = sorted(mine)
    out["rows"] = [{"claim_id": r[0], "track": r[1], "label": r[2], "status": r[3], "checked_by": r[6]}
                   for r in rows]
    return out


def write_tables(out, d):
    with open(os.path.join(d, "counts_track_label_status.tsv"), "w") as f:
        f.write("track\tlabel\tstatus\tn\n")
        for t, l, s, n in out["track_label_status"]:
            f.write(f"{t}\t{l}\t{s}\t{n}\n")
    with open(os.path.join(d, "queue.tsv"), "w") as f:
        f.write("claim_id\ttrack\tlabel\tstatus\tsource_label\tpaper_id\tannotated\n")
        for q in out["queue"]:
            f.write("\t".join(str(q[k]) if q[k] is not None else "" for k in
                              ("claim_id", "track", "label", "status", "source_label", "paper_id", "annotated")) + "\n")


def fig_state(out, path, title):
    import figstyle as fs
    import matplotlib.pyplot as plt
    import numpy as np
    fs.use_style()
    cats = [("to_verify", "located"), ("to_verify", "partial"), ("to_verify", "unlocated"),
            ("to_verify", "unresolved"), ("judgement", None), ("background", None)]
    names = ["to verify, located", "to verify, partial", "to verify, unlocated", "to verify, unresolved",
             "judgement", "background"]
    cols = [fs.PAL["red"], fs.PAL["orange"], fs.PAL["yellow"], "k", fs.PAL["blue"], fs.PAL["green"]]
    cnt = collections.Counter()
    for q in out["queue"]:
        key = (q["label"], q["status"] if q["label"] == "to_verify" else None)
        cnt[(q["track"], key)] += 1
    ft = collections.Counter()
    for r in out["rows"]:
        if r["label"] == "fulltext":
            ft[(r["track"], "checked" if r["status"] == "checked" else "machine")] += 1
    fig = plt.figure(figsize=(8.0, 3.6))
    ax = fs.inch_axes(fig, 1.15, 0.55, 3.0, 2.75)
    ax2 = fs.inch_axes(fig, 5.0, 0.55, 2.8, 2.75)
    y = np.arange(len(TRACKS))[::-1]
    left = np.zeros(len(TRACKS))
    for (c, n, col) in zip(cats, names, cols):
        v = np.array([cnt[(t, c)] for t in TRACKS], float)
        ax.barh(y, v, left=left, color=col, height=0.7, label=n)
        left += v
    for yi, tot in zip(y, left):
        ax.text(tot + 0.8, yi, f"{int(tot)}", va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(TRACKS)
    ax.set_xlabel("claims in the queue")
    ax.set_xlim(0, max(left) * 1.25 + 1)
    ax.minorticks_off()
    ax.legend(loc="upper right", fontsize=7, frameon=False)
    ax.set_title(title, fontsize=10)
    l2 = np.zeros(len(TRACKS))
    for key, n, col in (("checked", "fulltext, read by a person", fs.PAL["blue"]),
                        ("machine", "fulltext, located by machine", "grey")):
        v = np.array([ft[(t, key)] for t in TRACKS], float)
        ax2.barh(y, v, left=l2, color=col, height=0.7, label=n, alpha=1.0 if key == "checked" else 0.5)
        l2 += v
    ax2.set_yticks(y)
    ax2.set_yticklabels([])
    ax2.set_xlabel("fulltext claims")
    ax2.set_xlim(0, max(l2) * 1.15 + 1)
    ax2.minorticks_off()
    ax2.legend(loc="center right", bbox_to_anchor=(1.0, 0.357), fontsize=7, frameon=False)
    return fs.save(fig, path)


def fig_before_after(before, after, path):
    import figstyle as fs
    import matplotlib.pyplot as plt
    import numpy as np
    fs.use_style()
    b = collections.Counter(q["track"] for q in before["queue"])
    a_un = collections.Counter(q["track"] for q in after["queue"] if q["label"] == "to_verify")
    a_ann = collections.Counter(q["track"] for q in after["queue"] if q["label"] != "to_verify" and q["annotated"])
    a_jb = collections.Counter(q["track"] for q in after["queue"] if q["label"] != "to_verify" and not q["annotated"])
    bq = {q["claim_id"]: q for q in before["queue"]}
    arow = {r["claim_id"]: r for r in after["rows"]}
    moved = collections.Counter()
    for cid, q in bq.items():
        r = arow.get(cid)
        if r and r["label"] != q["label"]:
            moved[(q["track"], r["label"])] += 1
    fig = plt.figure(figsize=(8.0, 3.4))
    ax = fs.inch_axes(fig, 1.15, 0.55, 6.5, 2.6)
    y = np.arange(len(TRACKS))[::-1] * 2.0
    vb = np.array([b[t] for t in TRACKS], float)
    ax.barh(y + 0.4, vb, height=0.7, color="grey", alpha=0.5, label="queue before (to verify + judgement + background)")
    left = np.zeros(len(TRACKS))
    for key, name, col in (("fulltext", "now fulltext (read by kb-claims_tracks)", fs.PAL["blue"]),
                           ("refuted", "refuted", fs.PAL["red"]),
                           ("abstract", "abstract only", fs.PAL["green"]),
                           ("title_only", "title only", fs.PAL["orange"])):
        v = np.array([moved[(t, key)] for t in TRACKS], float)
        if v.sum():
            ax.barh(y - 0.4, v, left=left, height=0.7, color=col, label=name)
            left += v
    for vals, name, col in ((a_ann, "judgement/background, annotated", fs.PAL["yellow"]),
                            (a_jb, "judgement/background, not annotated", "k"),
                            (a_un, "still to verify (reason recorded)", fs.PAL["orange"])):
        v = np.array([vals[t] for t in TRACKS], float)
        ax.barh(y - 0.4, v, left=left, height=0.7, color=col, label=name,
                alpha=0.55 if col == fs.PAL["orange"] else 1.0, hatch="//" if col == fs.PAL["orange"] else None)
        left += v
    ax.set_yticks(y)
    ax.set_yticklabels(TRACKS)
    ax.set_xlabel("claims (upper bar: before; lower bar: after)")
    ax.set_xlim(0, max(max(vb), max(left)) * 1.45)
    ax.minorticks_off()
    ax.legend(loc="lower right", fontsize=7, frameon=False)
    return fs.save(fig, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--db", default=DB)
    ap.add_argument("--before")
    ap.add_argument("--tag", default="baseline")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    out = gather(a.db)
    with open(os.path.join(a.out, "counts.json"), "w") as f:
        json.dump(out, f, indent=1)
    write_tables(out, a.out)
    fig_state(out, os.path.join(a.out, f"fig_queue_{a.tag}"), f"evidence queue ({a.tag})")
    if a.before:
        before = json.load(open(a.before))
        fig_before_after(before, out, os.path.join(a.out, "fig_queue_before_after"))
    print(json.dumps({k: out[k] for k in ("claims", "max_claim_id", "by_label", "by_status", "fulltext_checked",
                                         "fulltext_machine_located", "annotated", "touched_by_me")}, indent=1))
    print(json.dumps(out["queue_by_track"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
