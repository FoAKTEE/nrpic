"""Independent checks and figures of the K2-K3 ingestion on the real store (read-only).

    kb/.venv/bin/python -I kb/scripts/papers_checks.py <out_dir> [--priority 3] [--db PATH]

Checks (each against something the ingestion did not compute itself):
  C1 main file: the heuristics without the 00README hints, against the 00README.json
     "toplevel" entry, for every ingested paper that ships one;
  C2 .bib parsing: kbtool.bib_parse.parse_bib against bibtexparser 2.1 on every .bib file the
     ingestion used: same keys, same eprint and doi values;
  C3 bibliography size: entries stored against a plain count of \\bibitem (or biblatex
     \\entry) in the .bbl / flattened text;
  C4 equation labels: every label stored is written in flat.tex (\\label{...}), and every
     \\label inside a display environment of flat.tex is stored;
  C5 citation keys: fraction of \\cite keys with a bibliography entry.
Writes <out_dir>/papers_checks.json and the figures fig_papers_k2.png, fig_citations_k3.png.
"""
import argparse
import collections
import json
import os
import re
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(HERE)
WT = os.path.dirname(KB)
sys.path.insert(0, KB)
sys.path.insert(0, os.path.join(WT, "python"))

from kbtool import bib_parse as B  # noqa: E402
from kbtool import bib_resolve as R  # noqa: E402
from kbtool import tex_files as F  # noqa: E402
from kbtool.paths import layout  # noqa: E402


def check_main(lay, papers):
    out = []
    for pid, main, ver in papers:
        src = os.path.join(lay.raw_arxiv, pid.replace("/", "_"), ver, "src")
        hints = F.read_00readme(src)
        if not hints["toplevel"]:
            continue
        orig = F.read_00readme
        F.read_00readme = lambda root: {"toplevel": [], "ignore": []}
        try:
            blind = F.find_main(src)["main"]
        finally:
            F.read_00readme = orig
        out.append({"paper": pid, "readme": hints["toplevel"][0], "heuristic": blind, "stored": main,
                    "agree": os.path.normpath(hints["toplevel"][0]) == blind})
    return out


def check_bib(lay, con):
    import bibtexparser
    out = []
    rows = con.execute("SELECT paper_id, version, parse_json FROM papers").fetchall()
    for pid, ver, pj in rows:
        pj = json.loads(pj)
        if pj.get("bib_source") != "bib":
            continue
        src = os.path.join(lay.raw_arxiv, pid.replace("/", "_"), ver, "src")
        for b in pj.get("bib_files", []):
            p = F.safe_join(src, b)
            text = F.read_text(p)[0]
            mine = {e["cite_key"]: e["fields"] for e in B.parse_bib(text)}
            lib = bibtexparser.parse_string(text)
            theirs = {e.key: {k.lower(): str(v.value) for k, v in e.fields_dict.items()} for e in lib.entries}
            keys_equal = set(mine) == set(theirs)
            diff = 0
            compared = 0
            for k in set(mine) & set(theirs):
                for f in ("eprint", "doi"):
                    if f in theirs[k] or f in mine[k]:
                        compared += 1
                        a = (mine[k].get(f) or "").strip().strip("{}\"").strip()
                        t = (theirs[k].get(f) or "").strip().strip("{}\"").strip()
                        diff += a != t
            out.append({"paper": pid, "file": b, "keys_mine": len(mine), "keys_bibtexparser": len(theirs),
                        "keys_equal": keys_equal, "only_mine": sorted(set(mine) - set(theirs))[:5],
                        "only_theirs": sorted(set(theirs) - set(mine))[:5], "fields_compared": compared,
                        "fields_differ": diff, "bibtexparser_failed_blocks": len(lib.failed_blocks)})
    return out


def check_bbl_counts(lay, con):
    out = []
    for pid, ver, pj in con.execute("SELECT paper_id, version, parse_json FROM papers").fetchall():
        pj = json.loads(pj)
        src_kind = pj.get("bib_source")
        if src_kind not in ("bbl", "thebibliography"):
            continue
        n_db = con.execute("SELECT count(*) FROM bib_entries WHERE paper_id=?", (pid,)).fetchone()[0]
        if src_kind == "bbl":
            text = F.read_text(F.safe_join(os.path.join(lay.raw_arxiv, pid.replace("/", "_"), ver, "src"),
                                           pj["bib_files"][0]))[0]
        else:
            text = open(os.path.join(lay.build, "tex", pid.replace("/", "_"), "flat.tex"), encoding="utf-8").read()
        text = F.strip_comments_text(text)
        n_grep = len(re.findall(r"\\bibitem(?![A-Za-z@])", text)) or len(re.findall(r"\\entry\s*\{", text))
        out.append({"paper": pid, "source": src_kind, "stored": n_db, "grep": n_grep, "agree": n_db == n_grep})
    return out


DISPLAY = re.compile(r"\\begin\{(equation|align|gather|multline|eqnarray|flalign|alignat|dmath)(\*?)\}(.*?)"
                     r"\\end\{\1\2\}", re.S)


def check_labels(lay, con):
    out = []
    for (pid,) in con.execute("SELECT paper_id FROM papers WHERE source_kind='tex'").fetchall():
        flat = open(os.path.join(lay.build, "tex", pid.replace("/", "_"), "flat.tex"), encoding="utf-8").read()
        stored = {r[0] for r in con.execute("SELECT label FROM equations WHERE paper_id=? AND label IS NOT NULL",
                                            (pid,))}
        in_flat = set()
        for m in DISPLAY.finditer(flat):
            in_flat |= {x.strip() for x in re.findall(r"\\label\s*\{([^{}]*)\}", m.group(3))}
        # a multi-line row stores its first label only; count every label of the environment rows
        rows = con.execute("SELECT tex_raw FROM equations WHERE paper_id=?", (pid,)).fetchall()
        all_stored = set()
        for (t,) in rows:
            all_stored |= {x.strip() for x in re.findall(r"\\label\s*\{([^{}]*)\}", t)}
        out.append({"paper": pid, "labels_in_display_envs": len(in_flat), "labels_in_rows": len(all_stored),
                    "missing": sorted(in_flat - all_stored)[:5], "extra": sorted(all_stored - in_flat)[:5],
                    "stored_first_labels": len(stored)})
    return out


def figures(con, out_dir, summary):
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    import numpy as np
    fs.use_style()
    P = con.execute("SELECT paper_id, parse_score, priority, grp FROM papers ORDER BY paper_id").fetchall()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 6.2))
    # top left: parse score
    ax = fig.add_axes([0.08, 0.58, 0.38, 0.37])
    sc = np.array([p[1] for p in P])
    ax.hist(sc, bins=np.linspace(0, 1, 21), color=fs.PAL["red"], alpha=0.8, label=f"{len(sc)} papers")
    ax.axvline(0.75, color="k", ls="--", lw=1.0, label="review threshold")
    ax.set_xlabel("parse score")
    ax.set_ylabel("papers")
    ax.legend(loc="upper left")
    # top right: equations vs sections per paper
    ax = fig.add_axes([0.58, 0.58, 0.38, 0.37])
    q = con.execute("SELECT p.paper_id, (SELECT count(*) FROM sections s WHERE s.paper_id=p.paper_id), "
                    "(SELECT count(*) FROM equations e WHERE e.paper_id=p.paper_id), "
                    "(SELECT count(*) FROM equations e WHERE e.paper_id=p.paper_id AND e.label IS NOT NULL) "
                    "FROM papers p").fetchall()
    ax.scatter([max(r[1], 0.5) for r in q], [max(r[2], 0.5) for r in q], s=14, color=fs.PAL["red"],
               label="equation rows")
    ax.scatter([max(r[1], 0.5) for r in q], [max(r[3], 0.5) for r in q], s=10, color=fs.PAL["blue"],
               marker="x", label="with a label")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("sections per paper")
    ax.set_ylabel("equations per paper")
    ax.legend(loc="upper left")
    # bottom left: chunk sizes
    ax = fig.add_axes([0.08, 0.08, 0.38, 0.37])
    for kind, col in (("body", fs.PAL["red"]), ("appendix", fs.PAL["yellow"]), ("caption", fs.PAL["blue"])):
        n = np.array([r[0] for r in con.execute("SELECT n_tokens FROM chunks WHERE kind=?", (kind,))])
        if len(n):
            ax.hist(n, bins=np.arange(0, 700, 20), histtype="step", lw=1.5, color=col,
                    label=f"{kind} ({len(n)})")
    ax.axvspan(200, 400, color="grey", alpha=0.1, label="target 200-400")
    ax.set_xlabel("words per chunk")
    ax.set_ylabel("chunks")
    ax.set_yscale("log")
    ax.legend(loc="upper right")
    # bottom right: bibliography identifiers per paper
    ax = fig.add_axes([0.58, 0.08, 0.38, 0.37])
    b = con.execute("SELECT paper_id, count(*), sum(target_arxiv IS NOT NULL), "
                    "sum(target_arxiv IS NULL AND target_doi IS NOT NULL) FROM bib_entries GROUP BY paper_id "
                    "ORDER BY 3.0*1/count(*) DESC").fetchall()
    b = sorted(b, key=lambda r: -(r[2] / r[1]))
    x = np.arange(len(b))
    fa = np.array([r[2] / r[1] for r in b])
    fd = np.array([r[3] / r[1] for r in b])
    ax.bar(x, fa, width=1.0, color=fs.PAL["blue"], label="arXiv id")
    ax.bar(x, fd, width=1.0, bottom=fa, color=fs.PAL["yellow"], label="DOI only")
    ax.set_xlim(-0.5, len(b) - 0.5)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("papers (sorted)")
    ax.set_ylabel("fraction of bibliography entries")
    ax.legend(loc="lower left")
    fig.savefig(os.path.join(out_dir, "fig_papers_k2.png"))
    plt.close(fig)

    # citation figure: group matrix and frontier
    groups, m = R.group_matrix(con)
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.2))
    ax = fig.add_axes([0.08, 0.13, 0.36, 0.36 * fs.FULL_WIDTH / 4.2])
    if groups:
        M = np.zeros((len(groups), len(groups)))
        for (g1, g2), k in m.items():
            if g1 in groups and g2 in groups:
                M[groups.index(g1), groups.index(g2)] = k
        im = ax.imshow(np.where(M > 0, M, np.nan), cmap="magma_r", origin="upper", interpolation="nearest")
        ax.set_xticks(range(len(groups)))
        ax.set_xticklabels(groups, rotation=90, fontsize=7)
        ax.set_yticks(range(len(groups)))
        ax.set_yticklabels(groups, fontsize=7)
        ax.set_xlabel("group of the cited paper")
        ax.set_ylabel("group of the citing paper")
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
        cb.set_label("in-corpus edges")
    ax = fig.add_axes([0.62, 0.13, 0.35, 0.80])
    fr = R.frontier(con, 25)
    y = np.arange(len(fr))[::-1]
    cols = [fs.PAL["blue"] if r["in_manifest"] else fs.PAL["red"] for r in fr]
    ax.barh(y, [r["cited_by"] for r in fr], color=cols)
    ax.set_yticks(y)
    ax.set_yticklabels([r["arxiv"] for r in fr], fontsize=7)
    ax.set_xlabel("corpus papers citing it")
    ax.text(0.98, 0.02, "blue: in manifest (not yet ingested)\nred: not in manifest", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=8)
    fig.savefig(os.path.join(out_dir, "fig_citations_k3.png"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--db")
    a = ap.parse_args()
    lay = layout()
    os.makedirs(a.out_dir, exist_ok=True)
    con = sqlite3.connect(f"file:{a.db or lay.db_work}?mode=ro", uri=True)
    papers = con.execute("SELECT paper_id, main_tex, version FROM papers WHERE source_kind='tex'").fetchall()
    res = {"C1_main": check_main(lay, papers), "C2_bib": check_bib(lay, con), "C3_bbl_counts": check_bbl_counts(lay, con),
           "C4_labels": check_labels(lay, con)}
    c5 = con.execute("SELECT count(*), sum(bib_id IS NULL) FROM citations").fetchone()
    res["C5_cite_keys"] = {"citations": c5[0], "without_bib_entry": c5[1],
                           "examples": con.execute("SELECT citing, cite_key FROM citations WHERE bib_id IS NULL "
                                                   "LIMIT 10").fetchall()}
    summ = {
        "C1": {"papers_with_readme": len(res["C1_main"]), "agree": sum(r["agree"] for r in res["C1_main"]),
               "disagree": [r for r in res["C1_main"] if not r["agree"]]},
        "C2": {"bib_files": len(res["C2_bib"]), "keys_equal": sum(r["keys_equal"] for r in res["C2_bib"]),
               "fields_compared": sum(r["fields_compared"] for r in res["C2_bib"]),
               "fields_differ": sum(r["fields_differ"] for r in res["C2_bib"]),
               "files_not_equal": [r for r in res["C2_bib"] if not r["keys_equal"] or r["fields_differ"]]},
        "C3": {"papers": len(res["C3_bbl_counts"]), "agree": sum(r["agree"] for r in res["C3_bbl_counts"]),
               "disagree": [r for r in res["C3_bbl_counts"] if not r["agree"]]},
        "C4": {"papers": len(res["C4_labels"]),
               "labels_in_display_envs": sum(r["labels_in_display_envs"] for r in res["C4_labels"]),
               "labels_in_rows": sum(r["labels_in_rows"] for r in res["C4_labels"]),
               "papers_with_missing": [r for r in res["C4_labels"] if r["missing"]],
               "papers_with_extra": [r for r in res["C4_labels"] if r["extra"]]},
        "C5": res["C5_cite_keys"],
    }
    json.dump({"summary": summ, "detail": res}, open(os.path.join(a.out_dir, "papers_checks.json"), "w"), indent=1)
    figures(con, a.out_dir, summ)
    print(json.dumps(summ, indent=1)[:6000])


if __name__ == "__main__":
    main()
