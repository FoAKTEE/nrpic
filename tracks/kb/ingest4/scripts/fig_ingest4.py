#!/usr/bin/env python3
"""Figures of package ingest4 from the outputs of registered runs (read-only inputs).

  fig_oldstyle      per paper of the six old-style lists: entries found by the parser after the
                    re-ingest against the independent marker count (R-count), and citation rows
                    with an entry; before the re-ingest both were zero
  fig_parse_status  parse-status counts and the recorded parse success rate before and after the
                    package, with the 95 per cent bar of decision 0016 item 6

Usage: python3 fig_ingest4.py --before DIR --after DIR --counts marker_counts.tsv --out DIR
(DIR: kbstate.py outputs with before.json / after.json and the per-list TSVs). Writes PNG and PDF
into --out and fig_data.tsv with the plotted numbers.
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as FS  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def tsv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--counts", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    FS.use_style()
    B = {r["paper_id"]: r for r in tsv(os.path.join(a.before, "before_oldstyle6.tsv"))}
    A = {r["paper_id"]: r for r in tsv(os.path.join(a.after, "after_oldstyle6.tsv"))}
    C = {r["paper"]: r for r in tsv(a.counts)}
    ids = list(C)
    ent_after = np.array([int(A[i]["bib_entries"]) for i in ids])
    ent_before = np.array([int(B[i]["bib_entries"]) for i in ids])
    ent_count = np.array([int(C[i]["count"]) for i in ids])
    cit_after = np.array([int(A[i]["citations_with_entry"]) for i in ids])
    cit_all = np.array([int(A[i]["citations"]) for i in ids])
    ch_b = np.array([int(B[i]["chunks"]) for i in ids])
    ch_a = np.array([int(A[i]["chunks"]) for i in ids])

    fig, axs = plt.subplots(1, 2, figsize=(FS.FULL_WIDTH, 3.0))
    x = np.arange(len(ids))
    w = 0.38
    ax = axs[0]
    ax.bar(x - w / 2, ent_after, w, color=FS.PAL["blue"], label="entries (parser)")
    ax.bar(x + w / 2, cit_after, w, color=FS.PAL["red"], label="citation rows with entry")
    ax.plot(x - w / 2, ent_count, ls="none", marker="_", ms=16, mew=2.0, color="k",
            label="independent count")
    ax.plot(x, ent_before, ls="none", marker="o", ms=4, color="grey", label="before (all zero)")
    ax.set_xticks(x)
    ax.set_xticklabels([i.replace("astro-ph/", "a/").replace("gr-qc/", "g/") for i in ids], rotation=30)
    ax.set_ylabel("count")
    ax.set_title("(a) old-style lists after re-ingest", loc="left")
    ax.legend(frameon=False, fontsize=7)
    ax = axs[1]
    ax.bar(x - w / 2, ch_b, w, color="grey", label="before")
    ax.bar(x + w / 2, ch_a, w, color=FS.PAL["blue"], label="after")
    ax.set_xticks(x)
    ax.set_xticklabels([i.replace("astro-ph/", "a/").replace("gr-qc/", "g/") for i in ids], rotation=30)
    ax.set_ylabel("chunks")
    ax.set_title("(b) chunks (list no longer body text)", loc="left")
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    FS.save(fig, os.path.join(a.out, "fig_oldstyle"))
    plt.close(fig)

    ob = json.load(open(os.path.join(a.before, "before.json")))["overall"]
    oa = json.load(open(os.path.join(a.after, "after.json")))["overall"]
    stats = ["ok", "review", "pdf", "failed"]
    fig, axs = plt.subplots(1, 2, figsize=(FS.FULL_WIDTH, 3.0))
    ax = axs[0]
    xs = np.arange(2)
    shown = [s for s in stats if ob["parse_status"].get(s, 0) or oa["parse_status"].get(s, 0)]
    xg = np.arange(len(shown))
    w2 = 0.38
    for j, (tag, o, col) in enumerate((("before", ob, "grey"), ("after", oa, FS.PAL["blue"]))):
        v = np.array([o["parse_status"].get(s, 0) for s in shown])
        ax.bar(xg + (j - 0.5) * w2, v, w2, color=col, label=f"{tag} ({o['papers']} papers)")
        for k in range(len(shown)):
            ax.text(xg[k] + (j - 0.5) * w2, v[k] * 1.15, str(v[k]), ha="center", va="bottom", fontsize=7)
    ax.set_yscale("log")
    ax.set_ylim(1, 3000)
    ax.set_xticks(xg)
    ax.set_xticklabels(shown)
    ax.set_ylabel("papers")
    ax.set_title("(a) parse status", loc="left")
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    ax = axs[1]
    rb, ra = 100 * ob["rate_recorded_ok"], 100 * oa["rate_recorded_ok"]
    ax.plot(xs, [rb, ra], marker="o", color=FS.PAL["blue"], label="recorded (status ok)")
    rb2, ra2 = 100 * ob["rate_recorded_ok_pdf"], 100 * oa["rate_recorded_ok_pdf"]
    ax.plot(xs, [rb2, ra2], marker="s", color=FS.PAL["green"], label="ok or pdf")
    ax.axhline(95.0, **FS.GUIDE, label="bar 95 %")
    for j, v in enumerate([rb, ra]):
        ax.annotate(f"{v:.2f} %", (xs[j], v), textcoords="offset points", xytext=(8, -12), fontsize=7)
    ax.set_xticks(xs)
    ax.set_xticklabels(["before", "after"])
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(94.0, 98.5)
    ax.set_ylabel("parse success rate (%)")
    ax.set_title("(b) rate against the bar", loc="left")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    fig.tight_layout()
    FS.save(fig, os.path.join(a.out, "fig_parse_status"))
    plt.close(fig)

    with open(os.path.join(a.out, "fig_data.tsv"), "w") as fh:
        fh.write("paper\tentries_before\tentries_after\tindependent_count\tcitations_after\t"
                 "citations_with_entry_after\tchunks_before\tchunks_after\n")
        for k, i in enumerate(ids):
            fh.write(f"{i}\t{ent_before[k]}\t{ent_after[k]}\t{ent_count[k]}\t{cit_all[k]}\t{cit_after[k]}\t"
                     f"{ch_b[k]}\t{ch_a[k]}\n")
        fh.write(f"# overall before: {json.dumps(ob['parse_status'])} rate {ob['rate_recorded_ok']}\n")
        fh.write(f"# overall after: {json.dumps(oa['parse_status'])} rate {oa['rate_recorded_ok']}\n")
    print("figures written to", a.out)


if __name__ == "__main__":
    main()
