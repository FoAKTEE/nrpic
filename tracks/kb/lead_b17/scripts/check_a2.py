#!/usr/bin/env python3
"""kb lead b17, check A2: after plan P1, compare the working database with snapshot
kb-20261125-2f97258 (read-only): label counts of live claims, the list of live claims with label
abstract and status unlocated that carry only their seed event, and the fate of the 26 claims
the plan names. Writes OUT/a2.json and OUT/fig_a2_labels.png.

    python3 -I check_a2.py OUT
"""
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

DB = "/data/haiyangw/nrpic/kb-data/db"
SNAP = os.path.join(DB, "kb-20261125-2f97258.sqlite")
WORK = os.path.join(DB, "kb.sqlite")
NAMED = [781, 223, 574, 553, 145, 169, 462, 773, 774, 706, 709, 710, 711, 712, 715, 794, 795, 796, 844]
LABELS = ["fulltext", "abstract", "title_only", "background", "judgement", "to_verify", "refuted"]


def ro(path):
    return sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)


def counts(con):
    q = ("SELECT c.label, count(*) FROM claims c JOIN claim_meta m USING(claim_id) "
         "WHERE m.status NOT IN ('superseded','withdrawn') GROUP BY 1")
    return dict(con.execute(q).fetchall())


def seed_only_abstract(con):
    q = ("SELECT c.claim_id FROM claims c JOIN claim_meta m USING(claim_id) "
         "WHERE c.label='abstract' AND m.status='unlocated' AND "
         "(SELECT count(*) FROM claim_events e WHERE e.claim_id=c.claim_id AND e.action NOT IN ('seed','add'))=0 "
         "ORDER BY 1")
    return [r[0] for r in con.execute(q)]


def fates(con):
    out = {}
    for cid in NAMED:
        r = con.execute("SELECT c.label, m.status FROM claims c JOIN claim_meta m USING(claim_id) WHERE claim_id=?",
                        (cid,)).fetchone()
        nxt = con.execute("SELECT to_id FROM claim_links WHERE from_id=? AND relation='superseded_by'",
                          (cid,)).fetchone()
        new = None
        if nxt:
            n = con.execute("SELECT c.label, m.status, (SELECT count(*) FROM claim_locators l WHERE l.claim_id=c.claim_id), "
                            "(SELECT coalesce(sum(resolved),0) FROM claim_locators l WHERE l.claim_id=c.claim_id) "
                            "FROM claims c JOIN claim_meta m USING(claim_id) WHERE claim_id=?", (nxt[0],)).fetchone()
            new = {"id": nxt[0], "label": n[0], "status": n[1], "loc_rows": n[2], "loc_resolved": n[3]}
        out[cid] = {"label": r[0], "status": r[1], "successor": new}
    return out


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    s, w = ro(SNAP), ro(WORK)
    res = {
        "snapshot": os.path.basename(SNAP),
        "claims_snapshot": s.execute("SELECT count(*) FROM claims").fetchone()[0],
        "claims_work": w.execute("SELECT count(*) FROM claims").fetchone()[0],
        "live_labels_snapshot": counts(s),
        "live_labels_work": counts(w),
        "abstract_unlocated_seed_only_snapshot": seed_only_abstract(s),
        "abstract_unlocated_seed_only_work": seed_only_abstract(w),
        "fates": fates(w),
    }
    res["to_verify_delta"] = res["live_labels_work"].get("to_verify", 0) - res["live_labels_snapshot"].get("to_verify", 0)
    json.dump(res, open(os.path.join(out, "a2.json"), "w"), indent=1, default=str)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    cols = fs.series_colors(2)
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    labs = [l for l in LABELS if l != "refuted"]
    x = range(len(labs))
    a = [res["live_labels_snapshot"].get(l, 0) for l in labs]
    b = [res["live_labels_work"].get(l, 0) for l in labs]
    ax.bar([i - 0.2 for i in x], a, width=0.4, color=cols[0], label="snapshot 2f97258")
    ax.bar([i + 0.2 for i in x], b, width=0.4, color=cols[1], label="after plan P1")
    for i in x:
        if a[i] != b[i]:
            ax.annotate(f"{b[i] - a[i]:+d}", (i + 0.2, b[i]), ha="center", va="bottom", fontsize=7)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labs)
    ax.set_yscale("log")
    ax.set_ylabel("live claims")
    ax.legend(frameon=False, fontsize=7)
    ax.set_title("Live claims by label before and after plan P1 (log scale)", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_a2_labels.png"), dpi=150)
    print(json.dumps({k: res[k] for k in ("claims_snapshot", "claims_work", "to_verify_delta",
                                          "abstract_unlocated_seed_only_snapshot",
                                          "abstract_unlocated_seed_only_work")}))


if __name__ == "__main__":
    main()
