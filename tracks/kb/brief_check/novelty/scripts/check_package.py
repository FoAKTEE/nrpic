"""Tally, locator check and figures of work package "novelty" (adapted from s35/fig_verdicts.py).

1. CHECK.md: rows numbered 1..N without gaps; header totals ("Totals: N rows; a CONFIRMED, b
   CONFIRMED (precision), c CORRECTED, d NOT FOUND") equal the tally of the verdict column.
2. Every locator in backticks in CHECK.md, ERRATA_ROWS.md and NOVELTY.md:
   - `<key>/<v>/src/<file>:<lines>`: the file exists under kb-data/raw/arxiv and is long enough;
     short forms `<file>:<lines>` and `:<lines>` refer to the last full locator before them;
   - `meta:arxiv-api/<id>` (and `/<id>` after it): the metadata file exists;
   - a run id `kb-<date>-<time>-<sha7>`: tracks/kb/runs/<id>/manifest.json exists;
   - `inspire-query:<label>` (and a bare `<label>` after it): the label is in
     search/query_log.tsv, its record exists under kb-data/meta/inspire/query and has status ok.
   Spans that are paths of this repository or templates (containing "<") are skipped.
3. Every arXiv id written in NOVELTY.md, CHECK.md or ERRATA_ROWS.md must be in the store
   (kb-data/raw/arxiv or kb-data/meta/arxiv-api) or among the hits of a logged INSPIRE query:
   no identifier comes from memory.
4. Figures: verdicts per brief line and per label; the closest papers of the four novelty
   items by year and kind of calculation.
Writes check.json, fig_verdicts.{pdf,png}, fig_landscape.{pdf,png} into $NRPIC_RUN_DIR (or
argv[1]). Exit status 1 if a check fails. Files under kb-data are only read (JSON parsed, TeX
counted in lines); nothing there is executed or imported.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402  (vendored copy of harness/style/figstyle.py)
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PKG = os.path.dirname(HERE)
CHECK = os.path.join(PKG, "CHECK.md")
DOCS = [CHECK, os.path.join(PKG, "ERRATA_ROWS.md"), os.path.join(PKG, "NOVELTY.md")]
QLOG = os.path.join(PKG, "search", "query_log.tsv")
KB = "/data/haiyangw/nrpic/kb-data"
RAW = os.path.join(KB, "raw", "arxiv")
RUNS = os.path.join(os.path.dirname(os.path.dirname(PKG)), "runs")
CLASSES = ["CONFIRMED", "CONFIRMED (precision)", "CORRECTED", "NOT FOUND"]
COLORS = {"CONFIRMED": fs.PAL["blue"], "CONFIRMED (precision)": fs.PAL["yellow"],
          "CORRECTED": fs.PAL["red"], "NOT FOUND": "grey"}


def classify(verdict):
    v = verdict.strip()
    for c in ("CORRECTED", "NOT FOUND", "CONFIRMED (precision)", "CONFIRMED"):
        if v.startswith(c):
            return c
    raise ValueError("unknown verdict: %r" % verdict)


def label_class(label):
    lab = label.strip()
    for k in ("[VERIFIED]", "[BACKGROUND]", "[TO VERIFY]"):
        if lab.startswith(k):
            return k
    if lab.startswith("(unl.)"):
        return "unlabelled"
    raise ValueError("unknown label: %r" % label)


def read_rows(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            if not re.match(r"^\| \d+ \|", line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) != 7:
                raise ValueError("row with %d cells: %s" % (len(cells), line[:80]))
            rows.append({"n": int(cells[0]), "line": cells[1], "cls": classify(cells[4]),
                         "lab": label_class(cells[3]), "loc": cells[5]})
    return rows


def header_totals(path):
    text = open(path).read().replace("\n", " ")
    m = re.search(r"Totals: (\d+) rows; (\d+) CONFIRMED, (\d+) CONFIRMED \(precision\), "
                  r"(\d+) CORRECTED, (\d+) NOT FOUND", text)
    if not m:
        raise ValueError("no totals sentence in the header")
    n, a, b, c, d = (int(x) for x in m.groups())
    return n, {"CONFIRMED": a, "CONFIRMED (precision)": b, "CORRECTED": c, "NOT FOUND": d}


def line_numbers(spec):
    out = []
    for part in spec.split(","):
        part = part.strip()
        if part:
            out += [int(x) for x in part.split("-")]
    return out


NL = {}


def nlines(path):
    if path not in NL:
        with open(path, "rb") as fh:
            NL[path] = fh.read().count(b"\n") + 1
    return NL[path]


def read_qlog():
    q = {}
    with open(QLOG) as fh:
        for line in fh:
            c = line.rstrip("\n").split("\t")
            if len(c) >= 6 and c[0] != "label":
                q[c[0]] = {"utc": c[1], "total": c[2], "status": c[3], "record": c[4],
                           "query": c[5]}
    return q


SKIP = re.compile(r"(<|\.md$|^kb-data/|^harness/|^track/|^tracks/|^coord/|^scripts/|^search/|"
                  r"^python|^cd |^/data/|^\$)")
# words in backticks that are not locators: store key, package and branch names, row template
NOT_LOCATORS = {"gr-qc_0512031", "s5_s6", "nov.n", "kb/brief-check"}


def check_locators(path, qlog):
    problems, n = [], 0
    last_dir, last_file, last_meta = None, None, None
    text = open(path).read()
    for sp in re.findall(r"`([^`\n]+)`", text):
        sp = sp.strip()
        if SKIP.search(sp) or sp in NOT_LOCATORS:
            continue
        m = re.match(r"^([A-Za-z0-9._-]+)/(v\d+)/src/(.+?):([\d,\s-]+)$", sp)
        if m:
            key, ver, rel, lines = m.groups()
            last_dir = os.path.join(RAW, key, ver, "src")
            last_file = os.path.join(last_dir, rel)
            target = last_file
        else:
            m = re.match(r"^([A-Za-z0-9._/-]+\.tex):([\d,\s-]+)$", sp)
            if m and last_dir:
                last_file = os.path.join(last_dir, m.group(1))
                target, lines = last_file, m.group(2)
            else:
                m = re.match(r"^:([\d,\s-]+)$", sp)
                if m and last_file:
                    target, lines = last_file, m.group(1)
                else:
                    target = None
        if target is not None:
            n += 1
            if not os.path.isfile(target):
                problems.append("%s: missing file for %s" % (os.path.basename(path), sp))
            elif max(line_numbers(lines)) > nlines(target):
                problems.append("%s: %s beyond end (%d lines)" % (os.path.basename(path), sp,
                                                                 nlines(target)))
            continue
        if re.match(r"^kb-\d{8}-\d{6}-[0-9a-f]{7}$", sp):
            n += 1
            if not os.path.isfile(os.path.join(RUNS, sp, "manifest.json")):
                problems.append("no manifest for run %s" % sp)
            continue
        m = re.match(r"^meta:arxiv-api/(.+)$", sp) or (re.match(r"^/(\d{4}\.\d{4,5})$", sp)
                                                      if last_meta else None)
        if m:
            last_meta = True
            n += 1
            p = os.path.join(KB, "meta", "arxiv-api", m.group(1).replace("/", "_") + ".json")
            if not os.path.isfile(p):
                problems.append("missing metadata %s" % p)
            continue
        m = re.match(r"^(?:inspire-query:)?([a-z0-9]+_[a-z0-9]+)$", sp)
        if m and (sp.startswith("inspire-query:") or m.group(1) in qlog):
            n += 1
            lab = m.group(1)
            if lab not in qlog:
                problems.append("unknown query label %s" % lab)
                continue
            rec = qlog[lab]["record"]
            try:
                d = json.load(open(rec))
                if d.get("status") != "ok":
                    problems.append("query %s: status %s" % (lab, d.get("status")))
            except (OSError, ValueError):
                problems.append("query %s: record %s unreadable" % (lab, rec))
            continue
        # anything else in backticks is reported, so that no locator escapes the check
        problems.append("%s: unparsed span %r" % (os.path.basename(path), sp))
    return problems, n


def ids_known(qlog):
    known = set()
    for f in os.listdir(RAW):
        known.add(f.replace("_", "/"))
    for f in os.listdir(os.path.join(KB, "meta", "arxiv-api")):
        if f.endswith(".json"):
            known.add(f[:-5].replace("_", "/"))
    for lab, q in qlog.items():
        try:
            d = json.load(open(q["record"]))
        except (OSError, ValueError):
            continue
        if lab == "pre_c1":           # syntax not recognised by INSPIRE: not a search result
            continue
        for h in d.get("hits") or []:
            for e in h.get("arxiv_eprints") or []:
                known.add(e.get("value", ""))
            for r in h.get("references") or []:
                pass
    return known


def check_ids(qlog):
    known = ids_known(qlog)
    problems, seen = [], set()
    for path in DOCS:
        for aid in re.findall(r"(?<![\w.])((?:\d{4}\.\d{4,5})|(?:gr-qc|astro-ph|hep-th)/\d{7})"
                              r"(?![\d])", open(path).read()):
            seen.add(aid)
    for aid in sorted(seen):
        if aid not in known:
            problems.append("arXiv id %s neither in the store nor in a logged INSPIRE hit" % aid)
    return problems, len(seen)


# closest papers of NOVELTY.md (year, kind, arXiv id); kinds ordered from far to close
KINDS = ["analytic, semi-analytic or proof", "Newtonian N-body",
         "GR: vacuum, fluid or scalar field", "GR with particles"]
KCOL = {KINDS[0]: "grey", KINDS[1]: fs.PAL["yellow"], KINDS[2]: fs.PAL["blue"],
        KINDS[3]: fs.PAL["red"]}
LANDSCAPE = {   # (kind index into KINDS, arXiv id); the year is the arXiv year of the id
    "S5 free streaming": [(0, "2110.05982"), (2, "2303.07980"), (2, "2406.11417"),
                          (2, "2606.26532"), (0, "2607.09285"), (2, "2608.13206"),
                          (3, "2609.14218"), (2, "2109.04896")],
    "S7 Burnett": [(2, "1505.02959"), (2, "1801.08362"), (0, "1706.09501"), (0, "2009.08968"),
                   (2, "2108.09158"), (0, "2403.03470"), (0, "2506.21779"), (2, "2508.13294")],
    "S4 null test": [(2, "1306.4055"), (2, "1903.01490"), (0, "2302.07878"), (0, "2407.14549"),
                     (0, "2410.10459"), (0, "2609.38303")],
    "BBH in particle DM": [(1, "1805.09034"), (2, "2210.09254"), (2, "2311.18156"),
                           (1, "2402.13762"), (2, "2510.20037"), (3, "2611.12831")],
}

# phrases that must stand at the cited lines (the claims the verdicts rest on)
QUOTES = [
    ("2403.03470/v1/src/wavecoordinate.arxiv.240305.tex", 143, "first proof"),
    ("2403.03470/v1/src/wavecoordinate.arxiv.240305.tex", 143, "without symmetry assumptions"),
    ("2009.08968/v1/src/HFlimit.200918.tex", 101, "without any symmetry assumptions"),
    ("1907.10743/v2/src/main.tex", 87, "symmetry"),
    ("1903.01490/v2/src/spinning_BH_v2_CT.tex", 655, "0.1"),
    ("1903.01490/v2/src/spinning_BH_v2_CT.tex", 644, "e^2"),
    ("1903.01490/v2/src/spinning_BH_v2_CT.tex", 715, "is conserved"),
    ("2302.07878/v1/src/paper_couple_rev.tex", 130, "k=3.11"),
    ("2302.07878/v1/src/paper_couple_rev.tex", 132, "Kerr"),
    ("2611.12831/v1/src/main.tex", 1340, "64.15625"),
    ("2611.12831/v1/src/main.tex", 1358, "27.3"),
    ("2611.12831/v1/src/main.tex", 1362, "no inspiral signal"),
    ("2303.07980/v2/src/PBHs_QCD.tex", 357, "5.25/10.75"),
    ("2303.07980/v2/src/PBHs_QCD.tex", 367, "dedicated simulation"),
    ("2406.11417/v1/src/chapter.tex", 507, "dedicated simulation"),
    ("2406.11417/v1/src/chapter.tex", 508, "open question"),
    ("2409.16053/v1/src/main.tex", 110, "uniform time stepping across levels"),
    ("1011.4920/v2/src/inhomogeneities-paper.tex", 43, "traceless"),
    ("1505.02959/v1/src/letter-GWuni.tex", 64, "at most 3"),
    ("2402.13762/v1/src/main.tex", 238, "Newtonian"),
    ("2006.16182/v2/src/main_journal.tex", 1048, "3.045"),
    ("2409.01939/v2/src/LRCosmo.tex", 1072, "Isaacson"),
]


def check_quotes():
    problems = []
    for rel, line, phrase in QUOTES:
        path = os.path.join(RAW, rel)
        try:
            with open(path, "rb") as fh:
                text = fh.read().decode("utf-8", "replace").splitlines()
            if phrase not in text[line - 1]:
                problems.append("quote %r not at %s:%d" % (phrase, rel, line))
        except (OSError, IndexError):
            problems.append("quote file or line missing: %s:%d" % (rel, line))
    return problems


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    qlog = read_qlog()
    rows = read_rows(CHECK)
    problems = []
    if [r["n"] for r in rows] != list(range(1, len(rows) + 1)):
        problems.append("row numbers not consecutive")
    tally = {c: sum(1 for r in rows if r["cls"] == c) for c in CLASSES}
    n_head, t_head = header_totals(CHECK)
    if n_head != len(rows) or t_head != tally:
        problems.append("header totals %s (%d) differ from tally %s (%d)"
                        % (t_head, n_head, tally, len(rows)))
    n_loc = {}
    for d in DOCS:
        p, n = check_locators(d, qlog)
        problems += p
        n_loc[os.path.basename(d)] = n
    p, n_ids = check_ids(qlog)
    problems += p
    problems += check_quotes()
    for k, r in LANDSCAPE.items():
        for _k, aid in r:
            if aid not in ids_known(qlog):
                problems.append("landscape id %s unknown" % aid)
    lines = sorted({r["line"] for r in rows}, key=int)
    labs = ["[VERIFIED]", "[BACKGROUND]", "[TO VERIFY]", "unlabelled"]
    by_line = {l: {c: 0 for c in CLASSES} for l in lines}
    by_lab = {l: {c: 0 for c in CLASSES} for l in labs}
    for r in rows:
        by_line[r["line"]][r["cls"]] += 1
        by_lab[r["lab"]][r["cls"]] += 1
    res = {"rows": len(rows), "tally": tally, "locators_checked": n_loc, "arxiv_ids": n_ids,
           "queries_logged": len(qlog), "quotes_checked": len(QUOTES), "problems": problems,
           "corrected": [(r["n"], r["line"]) for r in rows if r["cls"] == "CORRECTED"]}
    with open(os.path.join(out, "check.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.4))
    ax1 = fig.add_axes([0.08, 0.12, 0.46, 0.74])
    ax2 = fig.add_axes([0.72, 0.12, 0.25, 0.74])
    short = {"[VERIFIED]": "VERIFIED", "[BACKGROUND]": "BACKGROUND", "[TO VERIFY]": "TO VERIFY",
             "unlabelled": "no label"}
    for ax, keys, table in ((ax1, lines, by_line), (ax2, labs, by_lab)):
        y = list(range(len(keys)))[::-1]
        left = [0] * len(keys)
        for c in CLASSES:
            w = [table[k][c] for k in keys]
            if sum(w) == 0:
                continue
            ax.barh(y, w, left=left, color=COLORS[c], height=0.7, label=c, edgecolor="white",
                    linewidth=0.5)
            left = [a + b for a, b in zip(left, w)]
        ax.set_yticks(y)
        ax.set_yticklabels([short.get(k, k) for k in keys])
        ax.tick_params(axis="y", which="minor", left=False, right=False)
        ax.set_xlabel("statements checked")
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=5, integer=True))
    ax1.set_ylabel("brief line")
    ax1.set_xlim(0, max(sum(by_line[l].values()) for l in lines) + 1)
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(labels), bbox_to_anchor=(0.5, 0.99))
    fs.save(fig, os.path.join(out, "fig_verdicts"))
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 4.2))
    items = list(LANDSCAPE)[::-1]
    for i, item in enumerate(items):
        pts = sorted((2000 + int(a[:2]), k, a) for k, a in LANDSCAPE[item])
        for j, (yr, k, aid) in enumerate(pts):
            dy = (j % 4 - 1.5) * 0.2
            ax.scatter(yr, i + dy, s=46, color=KCOL[KINDS[k]], edgecolor="k", linewidth=0.5,
                       zorder=3)
            ax.annotate(aid, (yr, i + dy), xytext=(4, 2), textcoords="offset points",
                        fontsize=6.5)
    for k in KINDS:
        ax.scatter([], [], s=46, color=KCOL[k], edgecolor="k", linewidth=0.5, label=k)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_ylim(-0.6, len(items) - 0.4)
    ax.set_xlim(2012, 2028.5)
    ax.set_xlabel("arXiv year of the closest papers found")
    ax.legend(fontsize=7, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.13))
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_landscape"))
    plt.close(fig)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
