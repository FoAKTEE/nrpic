"""Figures and BEFORE_AFTER.tsv of package ingest3 from the JSON of registered runs.

  fig_bib_before_after   per paper of the 20: bibliography entries and citation rows with an
                         entry, before and after the re-ingest; cited keys of the parse as a mark
  fig_parse_status       parse-status counts and the parse success rate (recorded, and with "ok but
                         cites and has no entry" counted as a failure) at three states

Usage: python3 -I fig_before_after.py --before B.json --reingest R.json --final F.json
                                      --dry DIR --out DIR
(B, R, F: outputs of kbstate.py; DIR of --dry: the per-paper summaries of `kb ingest arxiv --dry-run`).
Writes only into --out.
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as FS  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def load(p):
    with open(p) as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--reingest", required=True)
    ap.add_argument("--final", required=True)
    ap.add_argument("--dry", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    B, R, F = load(a.before), load(a.reingest), load(a.final)
    dry = {}
    for p in glob.glob(os.path.join(a.dry, "*.json")):
        d = load(p)
        dry[d["paper_id"]] = d
    b20 = {r["paper_id"]: r for r in B["lists"]["zero20"]}
    f20 = {r["paper_id"]: r for r in F["lists"]["zero20"]}
    ids = [r["paper_id"] for r in B["lists"]["zero20"]]

    # ---- BEFORE_AFTER.tsv
    cols = ["parse_status", "bib_source", "bib_entries", "bib_with_arxiv", "citations", "citations_with_entry",
            "sections", "equations", "chunks", "claim_locator_rows"]
    lines = ["\t".join(["paper_id", "cited_keys_after"] + [f"{c}_before" for c in cols] + [f"{c}_after" for c in cols])]
    for pid in ids:
        lines.append("\t".join([pid, str(dry.get(pid, {}).get("cited_keys", ""))] +
                               [str(b20[pid].get(c)) for c in cols] + [str(f20[pid].get(c)) for c in cols]))
    for name in ("additions24", "frontier11"):
        for r in F["lists"].get(name, []):
            lines.append("\t".join([r["paper_id"] + f" ({name})", ""] + ["not in database"] + [""] * (len(cols) - 1) +
                                   [str(r.get(c)) for c in cols]))
    with open(os.path.join(a.out, "BEFORE_AFTER.tsv"), "w") as f:
        f.write("\n".join(lines) + "\n")

    FS.use_style()
    # ---- figure 1: per paper
    order = sorted(ids, key=lambda p: (f20[p]["bib_entries"], f20[p]["citations"]))
    y = np.arange(len(order))
    fig = plt.figure(figsize=(FS.FULL_WIDTH, 5.2))
    fig.subplots_adjust(left=0.17, right=0.98, bottom=0.10, top=0.93, wspace=0.08)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2, sharey=ax1)
    h = 0.38
    eb = [b20[p]["bib_entries"] for p in order]
    ea = [f20[p]["bib_entries"] for p in order]
    ck = [dry.get(p, {}).get("cited_keys") or 0 for p in order]
    run_b = os.path.basename(os.path.dirname(os.path.abspath(a.before)))
    run_f = os.path.basename(os.path.dirname(os.path.abspath(a.final)))
    ax1.barh(y + h / 2, eb, height=h, color=FS.PAL["blue"], label=f"before ({run_b[-15:]})")
    ax1.barh(y - h / 2, ea, height=h, color=FS.PAL["red"], label=f"after ({run_f[-15:]})")
    ax1.plot(ck, y - h / 2, ls="none", marker="|", ms=9, mew=1.5, color="k", label="distinct cited keys")
    ax1.set_xscale("symlog", linthresh=1)
    ax1.set_xlim(0, 300)
    ax1.set_yticks(y)
    ax1.set_yticklabels(order, fontsize=8)
    ax1.yaxis.set_minor_locator(plt.NullLocator())
    ax1.set_xlabel("bibliography entries")
    ax1.set_title("Entries per paper")
    ax1.legend(loc="lower right", fontsize=8)
    ax1.text(0.97, 0.30, "before: 0 entries for all 20", fontsize=8, ha="right", transform=ax1.transAxes)
    cb = [b20[p]["citations_with_entry"] for p in order]
    ca = [f20[p]["citations_with_entry"] for p in order]
    ct = [f20[p]["citations"] for p in order]
    ax2.barh(y + h / 2, cb, height=h, color=FS.PAL["blue"], label="with an entry, before")
    ax2.barh(y - h / 2, ca, height=h, color=FS.PAL["red"], label="with an entry, after")
    ax2.plot(ct, y - h / 2, ls="none", marker="|", ms=9, mew=1.5, color="k", label="all citation rows, after")
    ax2.set_xscale("symlog", linthresh=1)
    ax2.set_xlim(0, 300)
    ax2.set_xlabel("citation rows (one per cited key)")
    ax2.set_title("Citation rows per paper")
    plt.setp(ax2.get_yticklabels(), visible=False)
    ax2.legend(loc="lower right", fontsize=8)
    FS.save(fig, os.path.join(a.out, "fig_bib_before_after"))
    plt.close(fig)

    # ---- figure 2: parse status at three states
    states = [("baseline\n(710 papers)", B["overall"]), ("after re-ingest\n(710)", R["overall"]),
              ("final: 35 additions,\n31 redone (745)", F["overall"])]
    fig = plt.figure(figsize=(FS.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.2, top=0.9, wspace=0.28)
    ax1 = fig.add_subplot(1, 2, 1)
    x = np.arange(len(states))
    w = 0.2
    keys = [("ok", FS.PAL["red"]), ("ok, strict", FS.PAL["orange"]), ("review", FS.PAL["yellow"]),
            ("pdf", FS.PAL["green"])]
    for k, (key, colr) in enumerate(keys):
        vals = []
        for _, o in states:
            st = o["parse_status"]
            vals.append(st.get("ok", 0) - len(o["ok_cites_no_entry"]) if key == "ok, strict" else st.get(key, 0))
        bars = ax1.bar(x + (k - 1.5) * w, vals, width=w, color=colr, label=key)
        for xb, v in zip(x + (k - 1.5) * w, vals):
            ax1.text(xb, v + 8, str(v), ha="center", va="bottom", fontsize=7)
    ax1.set_yscale("symlog", linthresh=10)
    ax1.set_ylim(0, 3000)
    ax1.set_xticks(x)
    ax1.set_xticklabels([s for s, _ in states], fontsize=8)
    ax1.xaxis.set_minor_locator(plt.NullLocator())
    ax1.set_ylabel("papers")
    ax1.set_title("Parse status")
    ax1.legend(loc="upper left", ncol=4, fontsize=7)
    ax2 = fig.add_subplot(1, 2, 2)
    rec = [100 * o["rate_recorded_ok"] for _, o in states]
    strict = [100 * o["rate_strict_ok"] for _, o in states]
    ax2.plot(x, rec, marker="o", color=FS.PAL["red"], label="recorded status ok")
    ax2.plot(x, strict, marker="s", color=FS.PAL["orange"], ls="--",
             label='"ok, cites, no entry" counted as failure')
    ax2.axhline(95.0, **FS.GUIDE)
    ax2.text(0.62, 94.88, "KB-G2 bar 95 %", fontsize=8, transform=ax2.get_yaxis_transform())
    for xi, r, s in zip(x, rec, strict):
        ax2.text(xi + 0.07, r + 0.04, f"{r:.2f}", fontsize=7)
        if abs(r - s) > 0.01:
            ax2.text(xi + 0.09, s + 0.03, f"{s:.2f}", fontsize=7, color=FS.PAL["orange"])
    ax2.set_xticks(x)
    ax2.set_xticklabels([s for s, _ in states], fontsize=8)
    ax2.xaxis.set_minor_locator(plt.NullLocator())
    ax2.set_xlim(-0.4, 2.6)
    ax2.set_ylim(94.5, 97.0)
    ax2.set_ylabel("parse success rate (%)")
    ax2.set_title("Success rate")
    ax2.legend(loc="lower right", fontsize=7)
    FS.save(fig, os.path.join(a.out, "fig_parse_status"))
    plt.close(fig)
    print("\n".join(lines[:3]))
    print({s.split(chr(10))[0]: (o["parse_status"], o["rate_recorded_ok"], o["rate_strict_ok"]) for s, o in states})


if __name__ == "__main__":
    main()
