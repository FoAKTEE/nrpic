"""Follow-up of test P (paper 1201.4794): how many TeX papers have no bibliography entry in
the knowledge base, and what reference list their source has.

Usage: python3 check_zero_bib.py <outdir>   (writes <outdir>/zero_bib.json and .tsv)
"""
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import texcount  # noqa: E402

ROOT = "/data/haiyangw/nrpic/kb-data"
DB = os.path.join(ROOT, "db", "current")


def fig_zero(res, out):
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    kinds = ["references_env_bibitem", "aastex_references", "bibitem_alias", "bbl_harvarditem",
             "plain_ref_items"]
    names = {"references_env_bibitem": r"\bibitem in references env.",
             "aastex_references": r"AASTeX \reference", "bibitem_alias": r"macro for \bibitem",
             "bbl_harvarditem": r"\harvarditem in .bbl", "plain_ref_items": r"plain TeX \ref"}
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 4.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.30, top=0.90)
    x = np.arange(len(res))
    bottom = np.zeros(len(res))
    for k, col in zip(kinds, cols):
        v = np.array([r["my_counts"].get(k, 0) for r in res], float)
        if v.any():
            ax.bar(x, v, bottom=bottom, color=col, label=names[k])
            bottom += v
    for i, r in enumerate(res):
        ax.text(i, bottom[i] + 2, "ok" if r["parse_status"] == "ok" else "rev", ha="center",
                fontsize=7, color="k" if r["parse_status"] == "ok" else "grey")
    ax.set_xticks(x)
    ax.set_xticklabels([r["paper_id"] for r in res], rotation=60, ha="right", fontsize=7)
    ax.set_ylabel("reference items in the source")
    ax.set_title("TeX papers with no bibliography entry in the knowledge base (KB count 0)")
    ax.set_ylim(0, max(bottom.max() * 1.2, 10))
    ax.legend(loc="upper right", fontsize=8)
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    fs.save(fig, os.path.join(out, "fig_zero_bib"))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = c.execute("select p.paper_id, p.version, p.parse_status from papers p where p.source_kind='tex' "
                     "and not exists(select 1 from bib_entries b where b.paper_id=p.paper_id) "
                     "order by p.paper_id").fetchall()
    n_tex = c.execute("select count(*) from papers where source_kind='tex'").fetchone()[0]
    res = []
    for pid, ver, status in rows:
        src = os.path.join(ROOT, "raw", "arxiv", pid.replace("/", "_"), ver, "src")
        a = texcount.analyse(src)
        b = a.get("bib", {})
        kinds = {k: b.get(k, 0) for k in ("bbl", "bib", "thebibliography", "aastex_references",
                                           "references_env_bibitem", "bibitem_alias",
                                           "bbl_harvarditem", "plain_ref_items") if b.get(k)}
        res.append({"paper_id": pid, "parse_status": status, "main": a.get("main"),
                    "my_counts": kinds, "bibliography_cmd": b.get("bibliography_cmd"),
                    "cited_keys": b.get("cited_keys")})
    json.dump({"n_tex": n_tex, "zero_bib": res}, open(os.path.join(out, "zero_bib.json"), "w"), indent=1)
    with open(os.path.join(out, "zero_bib.tsv"), "w") as f:
        f.write("paper_id\tparse_status\tmy_counts\tbibliography_cmd\tcited_keys\n")
        for r in res:
            f.write(f"{r['paper_id']}\t{r['parse_status']}\t{json.dumps(r['my_counts'])}\t"
                    f"{r['bibliography_cmd']}\t{r['cited_keys']}\n")
    fig_zero(res, out)
    print(f"{len(res)} of {n_tex} TeX papers have no bibliography entry in the knowledge base")
    print(open(os.path.join(out, "zero_bib.tsv")).read())


if __name__ == "__main__":
    main()
