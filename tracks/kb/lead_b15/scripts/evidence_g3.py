#!/usr/bin/env python3
"""State of the evidence queue for KB-G3 criterion C1, from db/current (read-only).

Per track: claims, to_verify claims, to_verify claims with a processing event (any event other
than seed/add/remap), labels; brief seeds without a processing event; statuses. Writes
evidence.json and a figure into OUTDIR.

    python3 -I evidence_g3.py OUTDIR
"""
import json, os, sqlite3, sys
from collections import Counter, defaultdict

CUR = "/data/haiyangw/nrpic/kb-data/db/current"
PROC = ("verify", "refute", "annotate", "relocate", "check", "supersede", "supersedes", "withdraw")
NOT_G1 = {806, 807, 810, 811, 812}  # decision 0035 item 5


def main(out):
    os.makedirs(out, exist_ok=True)
    path = os.path.realpath(CUR)
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    rows = con.execute("SELECT c.claim_id, c.label, m.status, m.track FROM claims c JOIN claim_meta m"
                       " USING(claim_id)").fetchall()
    q = ",".join("?" * len(PROC))
    proc = {r[0] for r in con.execute(f"SELECT DISTINCT claim_id FROM claim_events WHERE action IN ({q})",
                                      PROC)}
    per = defaultdict(lambda: {"claims": 0, "to_verify": 0, "to_verify_processed": 0,
                               "labels": Counter(), "status": Counter()})
    unprocessed = []
    for cid, lab, st, tr in rows:
        t = per[tr or "none"]
        t["claims"] += 1
        t["labels"][lab] += 1
        t["status"][st] += 1
        if lab == "to_verify":
            t["to_verify"] += 1
            if cid in proc:
                t["to_verify_processed"] += 1
            else:
                unprocessed.append((cid, tr))
    res = {"snapshot": os.path.basename(path), "claims": len(rows),
           "per_track": {k: {**v, "labels": dict(v["labels"]), "status": dict(v["status"])}
                         for k, v in sorted(per.items())},
           "to_verify_unprocessed": unprocessed,
           "to_verify_unprocessed_bearing_on_g1": [c for c, _ in unprocessed if c not in NOT_G1],
           "status_all": dict(Counter(r[2] for r in rows)),
           "labels_all": dict(Counter(r[1] for r in rows))}
    json.dump(res, open(os.path.join(out, "evidence.json"), "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("snapshot", "claims", "to_verify_unprocessed",
                                          "to_verify_unprocessed_bearing_on_g1", "status_all")}))
    for k, v in res["per_track"].items():
        print(k, v["claims"], v["to_verify"], v["to_verify_processed"], v["labels"])

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    tracks = list(res["per_track"])
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    x = range(len(tracks))
    tv = [res["per_track"][t]["to_verify"] for t in tracks]
    tp = [res["per_track"][t]["to_verify_processed"] for t in tracks]
    ax.bar([i - 0.2 for i in x], tv, 0.4, color=fs.PAL["blue"], label="to_verify")
    ax.bar([i + 0.2 for i in x], tp, 0.4, color=fs.PAL["green"], label="with a processing event")
    ax.set_xticks(list(x))
    ax.set_xticklabels(tracks, rotation=30, ha="right")
    ax.set_ylabel("claims")
    ax.set_title(f"KB-G3 C1 on {res['snapshot']}: unprocessed bearing on G1 = "
                 f"{len(res['to_verify_unprocessed_bearing_on_g1'])}", fontsize=8)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_g3_queue"))


if __name__ == "__main__":
    main(sys.argv[1])
