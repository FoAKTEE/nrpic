#!/usr/bin/env python3
"""Independent check of package claims3 from its artefacts (kb lead, batch 15).

Read-only. Opens the working database and the snapshot of batch 13 in mode=ro and checks:
  1. every LEDGER.tsv row against the database (label, status, successor link, locator rows);
  2. that the claims changed between the snapshot and the working database are exactly the
     ledger's claim ids (a claim is "changed" if its claims row, its claim_meta status/label
     fields or its locator rows differ, or if it is new);
  3. the sample rate, Clopper-Pearson interval and stratum-weighted estimate, recomputed from
     SAMPLE_VERDICTS.tsv and the stratum sizes (own code, not the package's);
  4. the weak class today, with the package's query (its script, run read-only).
Writes review.json, a five-claim reading list (own seed) and a figure into the output directory.

    python3 -I review_claims3.py OUTDIR
"""
import csv, hashlib, json, math, os, random, sqlite3, subprocess, sys

ROOT = "/data/haiyangw/nrpic"
WT = os.path.join(ROOT, "wt", "kb")
PKG = os.path.join(WT, "tracks", "kb", "claims3")
WORK = os.path.join(ROOT, "kb-data", "db", "kb.sqlite")
SNAP = os.path.join(ROOT, "kb-data", "db", "kb-20261124-9872d21.sqlite")


def ro(path):
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def claim_state(con):
    out = {}
    for row in con.execute("select * from claims order by claim_id"):
        out[row[0]] = {"claims": row}
    for row in con.execute("select claim_id, status, label_set_by, checked_by, checked_at,"
                           " status_detail from claim_meta"):
        out.setdefault(row[0], {})["meta"] = row[1:]
    for row in con.execute("select claim_id, ord, paper_id, version, file, line_start, line_end,"
                           " resolved from claim_locators order by claim_id, ord"):
        out.setdefault(row[0], {}).setdefault("locs", []).append(row[1:])
    return {k: hashlib.sha256(repr(sorted(v.items())).encode()).hexdigest() for k, v in out.items()}


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k + 1))


def cp_interval(k, n, alpha=0.05):
    def solve(f, lo=0.0, hi=1.0):
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if f(mid):
                hi = mid
            else:
                lo = mid
        return 0.5 * (lo + hi)
    lower = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k - 1, n, p) >= alpha / 2)
    upper = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) <= alpha / 2)
    return lower, upper


def main(out):
    os.makedirs(out, exist_ok=True)
    work, snap = ro(WORK), ro(SNAP)
    res = {"work_db": WORK, "snapshot": SNAP}

    # 1. ledger rows against the database
    ledger = list(csv.DictReader(open(os.path.join(PKG, "LEDGER.tsv")), delimiter="\t"))
    links = {(a, b) for a, b in work.execute(
        "select from_id, to_id from claim_links where relation='superseded_by'")}
    mism = []
    for r in ledger:
        cid = int(r["claim_id"])
        row = work.execute("select c.label, m.status from claims c join claim_meta m"
                           " using(claim_id) where claim_id=?", (cid,)).fetchone()
        if row is None:
            mism.append((cid, "missing"))
            continue
        if row[0] != r["label_after"] or row[1] != r["status_after"]:
            mism.append((cid, f"db {row} ledger {r['label_after']},{r['status_after']}"))
        if r["successor"]:
            if (cid, int(r["successor"])) not in links:
                mism.append((cid, f"no link to {r['successor']}"))
    res["ledger_rows"] = len(ledger)
    res["ledger_ids"] = len({int(r["claim_id"]) for r in ledger})
    res["ledger_mismatches"] = mism
    res["superseded_by_links"] = len(links)
    new = list(range(865, 882))
    locs = {cid: work.execute("select count(*), sum(resolved) from claim_locators where"
                              " claim_id=?", (cid,)).fetchone() for cid in new}
    res["new_claims_locators"] = {str(k): v for k, v in locs.items()}
    res["new_claims_without_resolved_locator"] = [k for k, v in locs.items() if not v[1]]

    # 2. changed claims between snapshot and working db
    a, b = claim_state(snap), claim_state(work)
    changed = sorted(k for k in b if a.get(k) != b[k])
    ledger_ids = {int(r["claim_id"]) for r in ledger}
    res["changed_claims"] = len(changed)
    res["changed_not_in_ledger"] = [k for k in changed if k not in ledger_ids]
    res["ledger_not_changed"] = sorted(k for k in ledger_ids if k not in changed)
    st_a = dict(snap.execute("select status, count(*) from claim_meta group by status").fetchall())
    st_b = dict(work.execute("select status, count(*) from claim_meta group by status").fetchall())
    res["status_snapshot"], res["status_work"] = st_a, st_b
    res["claims_snapshot"] = snap.execute("select count(*) from claims").fetchone()[0]
    res["claims_work"] = work.execute("select count(*) from claims").fetchone()[0]

    # 3. sample rate, own computation
    sv = list(csv.DictReader(open(os.path.join(PKG, "SAMPLE_VERDICTS.tsv")), delimiter="\t"))
    counts = json.load(open(os.path.join(PKG, "counts.json")))
    sizes = {h: v["N"] for h, v in counts["sample"]["strata"].items()}
    k = sum(int(r["right"]) for r in sv)
    n = len(sv)
    lo, hi = cp_interval(k, n)
    strata = {}
    for r in sv:
        s = strata.setdefault(r["stratum"], [0, 0])
        s[0] += 1
        s[1] += int(r["right"])
    W = sum(sizes.values())
    wrate = sum(sizes[h] / W * strata[h][1] / strata[h][0] for h in strata)
    # variance of a stratified mean with finite-population correction
    var = 0.0
    for h, (nh, kh) in strata.items():
        p = kh / nh
        if nh > 1:
            var += (sizes[h] / W) ** 2 * (1 - nh / sizes[h]) * p * (1 - p) / (nh - 1)
    res["sample"] = {"n": n, "right": k, "rate": k / n, "cp95": [lo, hi],
                     "strata": strata, "sizes": sizes, "W": W,
                     "weighted_rate": wrate, "weighted_se_fpc": math.sqrt(var),
                     "package": {"rate": counts["sample"]["rate"], "cp95": counts["sample"]["cp95"],
                                 "weighted_rate": counts["sample"]["weighted_rate"],
                                 "weighted_se": counts["sample"]["weighted_se"]}}
    unread = W - n
    res["extrapolation"] = {"unread": unread, "not_right_point": unread * (1 - k / n),
                            "not_right_cp95": [unread * (1 - hi), unread * (1 - lo)]}
    wrong = [r for r in sv if r["right"] == "0"]
    res["sample_wrong"] = [(r["claim_id"], r["stratum"], r["verdict"]) for r in wrong]

    # 4. weak class today (package query, read-only)
    p = subprocess.run([sys.executable, "-I", os.path.join(PKG, "scripts", "weak_class.py"),
                        "count"], capture_output=True, text=True)
    res["weak_class_today"] = {"exit": p.returncode, "stdout": p.stdout[-2000:],
                               "stderr": p.stderr[-500:]}

    # reading list for V2 (own seed)
    rng = random.Random(20261126)
    pool = [int(r["claim_id"]) for r in sv] + [869] + list(range(865, 869)) + list(range(870, 882))
    pick = sorted(rng.sample(pool, 5))
    rl = []
    for cid in pick:
        txt, lab = work.execute("select text, label from claims where claim_id=?", (cid,)).fetchone()
        st = work.execute("select status from claim_meta where claim_id=?", (cid,)).fetchone()[0]
        L = work.execute("select paper_id, version, file, line_start, line_end from claim_locators"
                         " where claim_id=? order by ord", (cid,)).fetchall()
        rl.append({"claim_id": cid, "label": lab, "status": st, "text": txt, "locators": L})
    res["reading_list"] = rl
    json.dump(res, open(os.path.join(out, "review.json"), "w"), indent=1, default=str)

    # figure
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.8))
    keys = sorted(set(st_a) | set(st_b), key=lambda s: -(st_b.get(s, 0)))
    x = range(len(keys))
    ax1.bar([i - 0.2 for i in x], [st_a.get(s, 0) for s in keys], 0.4, label="snapshot 9872d21",
            color=fs.PAL["blue"])
    ax1.bar([i + 0.2 for i in x], [st_b.get(s, 0) for s in keys], 0.4, label="working db",
            color=fs.PAL["orange"])
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(keys, rotation=40, ha="right")
    ax1.set_yscale("log")
    ax1.set_ylabel("claims")
    ax1.set_title(f"(a) status; changed {len(changed)}, outside ledger "
                  f"{len(res['changed_not_in_ledger'])}", fontsize=8)
    ax1.legend(fontsize=7)
    hs = sorted(strata)
    for i, h in enumerate(hs):
        nh, kh = strata[h]
        l, u = cp_interval(kh, nh)
        ax2.errorbar(i, kh / nh, yerr=[[kh / nh - l], [u - kh / nh]], fmt="o",
                     color=fs.PAL["blue"], capsize=3)
        ax2.text(i, 0.02, f"{kh}/{nh}\nN={sizes[h]}", ha="center", fontsize=6)
    ax2.errorbar(len(hs), k / n, yerr=[[k / n - lo], [hi - k / n]], fmt="s",
                 color=fs.PAL["orange"], capsize=3)
    ax2.axhline(wrate, color="0.4", lw=0.8, ls="--")
    ax2.text(len(hs), 0.02, f"{k}/{n}", ha="center", fontsize=6)
    ax2.set_xticks(list(range(len(hs) + 1)))
    ax2.set_xticklabels(hs + ["all"])
    ax2.set_ylim(0, 1.05)
    ax2.set_ylabel("right as worded")
    ax2.set_title(f"(b) recomputed: CP95 {lo:.3f}-{hi:.3f}, weighted {wrate:.3f}", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_review_claims3"))
    print(json.dumps({k2: res[k2] for k2 in ("ledger_rows", "ledger_mismatches", "changed_claims",
                                              "changed_not_in_ledger", "ledger_not_changed",
                                              "claims_snapshot", "claims_work",
                                              "superseded_by_links",
                                              "new_claims_without_resolved_locator")},
                     default=str))
    print(json.dumps(res["sample"], default=str))
    print(res["weak_class_today"]["stdout"][-600:])


if __name__ == "__main__":
    main(sys.argv[1])
