"""Figures of the package pdf_meta (style: figstyle.py beside this file).

    kb/.venv/bin/python -I fig_pdf_meta.py <out_dir> <pdf_run_dir> <brief16_run_dir> <meta_run_dir>

fig_pdf_reader      per PDF paper: out-of-vocabulary fraction of the text before and after the
                    repairs; repairs by kind; similarity of the located abstract to the
                    arXiv-API abstract, on the raw and on the repaired text
fig_brief16         brief section 16 against the arXiv API: title classes, author classes,
                    agreement per group
fig_metadata        TeX title against the API title (similarity), TeX abstract against the API
                    abstract, papers per group (section 17 and manifest additions)
Numbers printed to <out_dir>/fig_numbers.json. Paper text is read from kb-data (build) and never
written out.
"""
import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "kb"))
import figstyle as fs                                           # noqa: E402
import matplotlib.pyplot as plt                                 # noqa: E402
import numpy as np                                              # noqa: E402
from kbtool import pdf_reader as P                              # noqa: E402

BUILD = "/data/haiyangw/nrpic/kb-data/build/tex"
META = "/data/haiyangw/nrpic/kb-data/meta/arxiv-api"


def tsv(path):
    return list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))


def main(out, pdf_run, b16_run, meta_run):
    fs.use_style()
    os.makedirs(out, exist_ok=True)
    nums = {}
    # ---------------------------------------------------------------- PDF reader
    rep = json.load(open(os.path.join(pdf_run, "pdf_ingest.json")))["papers"]
    ids = [r["id"] for r in rep]
    raw_sim = []
    for pid in ids:
        key = pid.replace("/", "_")
        raw = open(os.path.join(BUILD, key, "pdf_raw.txt"), encoding="utf-8").read()
        ab = json.load(open(os.path.join(META, key + ".json")))["abstract"]
        pages = [0] + [i + 1 for i, c in enumerate(raw) if c == "\x0c"]
        raw_sim.append(P.locate_abstract(raw, ab, pages[2] if len(pages) > 2 else len(raw))[2])
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    axs = [fs.inch_axes(fig, 0.55, 0.85, 1.75, 1.75), fs.inch_axes(fig, 3.55, 0.85, 1.75, 1.75),
           fs.inch_axes(fig, 5.95, 0.85, 1.75, 1.75)]
    x = np.arange(len(ids))
    w = 0.38
    axs[0].bar(x - w / 2, [100 * r["oov_raw"] for r in rep], w, color="0.6", label="pdftotext")
    axs[0].bar(x + w / 2, [100 * r["oov_repaired"] for r in rep], w, color=fs.PAL["red"], label="repaired")
    axs[0].set_ylabel("rare tokens (%)")
    axs[0].set_xticks(x, ids, rotation=25, ha="right", fontsize=8)
    axs[0].minorticks_off()
    axs[0].set_ylim(0, 11)
    axs[0].legend(loc="upper right", fontsize=8)
    kinds = ["ligature-dropped", "ligature-split", "ot1-ligature", "dehyphen", "accent-dropped", "cmmi-greek",
             "ot1-quote", "ot1-endash"]
    cols = fs.series_colors(len(ids))
    yk = np.arange(len(kinds))
    for j, r in enumerate(rep):
        v = [r["repairs"].get(k, 0) for k in kinds]
        axs[1].barh(yk + (j - 1) * 0.27, [max(t, 0.5) if t else 0 for t in v], 0.27, color=cols[j], label=r["id"])
    axs[1].set_xscale("log")
    axs[1].set_yticks(yk, kinds, fontsize=8)
    axs[1].invert_yaxis()
    axs[1].set_xlabel("repairs")
    axs[1].tick_params(axis="y", which="minor", left=False, right=False)
    axs[1].legend(loc="lower left", bbox_to_anchor=(-0.75, 1.0), ncol=3, fontsize=7, handlelength=1.0,
                  columnspacing=0.8)
    axs[2].bar(x - w / 2, raw_sim, w, color="0.6", label="pdftotext")
    axs[2].bar(x + w / 2, [r["abstract_similarity"] for r in rep], w, color=fs.PAL["red"], label="repaired")
    axs[2].axhline(P.ABSTRACT_FOUND, color="k", ls="--", lw=1.0)
    axs[2].set_ylim(0, 1.05)
    axs[2].set_ylabel("abstract similarity")
    axs[2].set_xticks(x, ids, rotation=25, ha="right", fontsize=8)
    axs[2].minorticks_off()
    axs[2].legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=7)
    fs.save(fig, os.path.join(out, "fig_pdf_reader"))
    nums["pdf"] = {r["id"]: {"oov_raw": r["oov_raw"], "oov_repaired": r["oov_repaired"],
                             "abstract_similarity_raw": round(s, 4), "abstract_similarity": r["abstract_similarity"],
                             "repairs": r["repairs"], "pages": r["pages"], "sections": r["sections"],
                             "bib_entries": r["bib_entries"], "citations": r["citations"]}
                   for r, s in zip(rep, raw_sim)}
    # ---------------------------------------------------------------- brief section 16
    b16 = tsv(os.path.join(b16_run, "brief16_comparison.tsv"))
    tcls = ["same", "format", "minor", "differs"]
    acls = ["match", "collaboration", "not-checked", "incomplete", "order", "mismatch"]
    tc = collections.Counter(r["title_class"] for r in b16)
    ac = collections.Counter(r["authors_class"] for r in b16)
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.30, top=0.88, wspace=0.35)
    good = {"same", "format", "match", "collaboration", "not-checked"}
    for ax, cls, cnt, lab in ((axs[0], tcls, tc, "title"), (axs[1], acls, ac, "authors")):
        b = ax.bar(range(len(cls)), [cnt.get(c, 0) for c in cls],
                   color=[fs.PAL["blue"] if c in good else fs.PAL["red"] for c in cls])
        ax.bar_label(b, fontsize=8)
        ax.set_yscale("log")
        ax.set_ylim(0.8, 2000)
        ax.set_xticks(range(len(cls)), cls, rotation=45, ha="right", rotation_mode="anchor", fontsize=8)
        ax.tick_params(axis="x", which="minor", bottom=False, top=False)
        ax.set_ylabel(f"entries ({lab})")
    groups = sorted({r["group16"] for r in b16})
    frac = []
    for g in groups:
        rr = [r for r in b16 if r["group16"] == g]
        frac.append(sum(r["agree"] == "True" for r in rr) / len(rr))
    axs[2].bar(range(len(groups)), frac, color=fs.PAL["blue"])
    axs[2].set_ylim(0.6, 1.02)
    axs[2].set_xticks(range(len(groups)), [g[1:] for g in groups], fontsize=7, rotation=90)
    axs[2].tick_params(axis="x", which="minor", bottom=False, top=False)
    axs[2].set_xlabel("group G")
    axs[2].set_ylabel("entries that agree")
    fs.save(fig, os.path.join(out, "fig_brief16"))
    nums["brief16"] = {"title": dict(tc), "authors": dict(ac), "agree_by_group": dict(zip(groups, frac)),
                       "group16_ne_17": sum(r["group16"] != r["group17"] for r in b16)}
    # ---------------------------------------------------------------- metadata in the papers table
    pm = tsv(os.path.join(meta_run, "papers_meta.tsv"))
    tex = [r for r in pm if r["source_kind"] == "tex"]
    tr = np.array([float(r["tex_title_ratio"]) for r in tex if r["tex_title_ratio"]])
    asim = np.array([float(r["abstract_similarity"]) for r in tex if r["abstract_similarity"]])
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.30, top=0.88, wspace=0.38)
    bins = np.linspace(0, 1, 21)
    axs[0].hist(tr, bins=bins, color=fs.PAL["red"])
    axs[0].axvline(0.9, color="k", ls="--", lw=1.0)
    axs[0].set_yscale("log")
    axs[0].set_xlabel("TeX title vs arXiv title")
    axs[0].set_ylabel("papers")
    axs[1].hist(asim, bins=bins, color=fs.PAL["red"])
    axs[1].axvline(0.8, color="k", ls="--", lw=1.0)
    axs[1].set_yscale("log")
    axs[1].set_xlabel("TeX abstract vs arXiv abstract")
    gl = sorted({r["grp"] for r in pm})
    base = [sum(1 for r in pm if r["grp"] == g and r["group_source"] == "brief17") for g in gl]
    add = [sum(1 for r in pm if r["grp"] == g and r["group_source"] == "addition") for g in gl]
    axs[2].bar(range(len(gl)), base, color=fs.PAL["blue"], label="section 17")
    axs[2].bar(range(len(gl)), add, bottom=base, color=fs.PAL["red"], label="additions")
    axs[2].set_xticks(range(len(gl)), [g[1:] for g in gl], fontsize=7, rotation=90)
    axs[2].tick_params(axis="x", which="minor", bottom=False, top=False)
    axs[2].set_xlabel("group G")
    axs[2].set_ylabel("papers")
    axs[2].set_ylim(0, 105)
    axs[2].legend(loc="upper right", fontsize=8)
    fs.save(fig, os.path.join(out, "fig_metadata"))
    nums["metadata"] = {"tex_papers": len(tex), "tex_title_ratio_n": int(tr.size),
                        "tex_title_ge_0p9": int((tr >= 0.9).sum()), "abstract_n": int(asim.size),
                        "abstract_ge_0p8": int((asim >= 0.8).sum()),
                        "groups": {g: [b, a] for g, b, a in zip(gl, base, add)}}
    with open(os.path.join(out, "fig_numbers.json"), "w") as f:
        json.dump(nums, f, indent=1)
    print(json.dumps(nums["metadata"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
