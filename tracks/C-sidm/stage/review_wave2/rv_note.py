#!/usr/bin/env python3
"""Lead's recheck L11 of the note helper's claims check (note/tables/claims.md): the three
numbers that differ from the lead's wave-1 documents, read from the run outputs, and two
source locators read in the stored arXiv sources (kb-data/raw, read-only).
Output: $NRPIC_RUN_DIR/rv_note.json, rv_note.{png,pdf}.
"""
import csv
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rvlib as rv  # noqa: E402

S = rv.SCR
RAW = "/data/haiyangw/nrpic/kb-data/raw/arxiv"


def table1():
    rows = list(csv.DictReader(open(os.path.join(S, "C-sidm-20261115-120722-38ab057",
                                                 "table1_compare.csv"))))
    typos = {("491", "C"), ("493", "p0"), ("516", "C")}
    cols = [k[:-4] for k in rows[0] if k.endswith("_rel")]
    out = {}
    for c in cols:
        vals = [(abs(float(r[c + "_rel"])), r["line"], float(r["w0"])) for r in rows
                if r[c + "_rel"] not in ("", "nan") and (r["line"], c) not in typos]
        v = max(vals)
        out[c] = dict(max_rel=v[0], line=v[1], w0=v[2], n=len(vals))
    above = {c: d for c, d in out.items() if c != "R" and d["max_rel"] > 1.1e-4}
    return dict(rows=len(rows), columns=out, above_1p1e4_outside_R=above)


def timescales():
    d = json.load(open(os.path.join(S, "C-sidm-20261115-121412-d463e1a", "timescales.json")))
    txt = open(os.path.join(S, "C-sidm-20261115-121412-d463e1a", "timescales.md")).read()
    m = re.search(r"t0/t_dyn >= ([0-9.e+]+); fastest gravothermal time t_c ~ 0.1 t0 = ([0-9.e+]+) t_dyn", txt)
    return dict(t0_over_tdyn_min=float(m.group(1)), fastest_phase_tdyn_min=float(m.group(2)),
                json_keys=sorted(d)[:20])


def initial_models():
    txt = open(os.path.join(S, "C-sidm-20261115-121748-4e8d6b5", "initial_models.md")).read()
    rows = []
    for line in txt.splitlines():
        p = [q.strip() for q in line.strip().strip("|").split("|")]
        if len(p) > 10 and p[0] == "0.1":
            try:
                rows.append(dict(Z0=float(p[1]), R=float(p[3]), rcore=float(p[4]),
                                 alpha=float(p[8])))
            except ValueError:
                pass
    sel = [r for r in rows if 0.40 - 1e-9 <= r["Z0"] <= 0.80 + 1e-9]
    rng = lambda k: [min(r[k] for r in sel), max(r[k] for r in sel)]  # noqa: E731
    return dict(Z0=[r["Z0"] for r in sel], R_over_M=rng("R"), rcore_over_M=rng("rcore"),
                alpha_c=rng("alpha"))


def locator(path, pattern):
    hits = []
    for i, line in enumerate(open(path, errors="replace"), 1):
        if re.search(pattern, line):
            hits.append(i)
    return hits


def figure(r, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(rv.WT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.4, 2.9))
    fig.subplots_adjust(left=0.15, right=0.98, bottom=0.2, top=0.92)
    cols = r["table1"]["columns"]
    names = list(cols)
    v = [cols[c]["max_rel"] for c in names]
    ax.bar(range(len(names)), v, color=[fs.PAL["red"] if (x > 1.1e-4 and c != "R") else fs.PAL["blue"]
                                        for c, x in zip(names, v)])
    ax.axhline(1.1e-4, **fs.GUIDE)
    ax.set_yscale("log")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=60, fontsize=7)
    ax.set_ylabel("largest |relative residual|")
    ax.set_title("F21 Table 1 (56 rows, typos excluded); dashed: 1.1e-4", fontsize=8)
    fs.save(fig, os.path.join(out, "rv_note"))


def main():
    out = rv.outdir()
    r = dict(table1=table1(), timescales=timescales(), initial_models=initial_models())
    g26 = os.path.join(RAW, "2601.17117", "v2", "src", "SIDM_MS.tex")
    bs = os.path.join(RAW, "astro-ph_0111176", "v3", "src", "SMBH_SIDM_Xiv2.tex")
    r["locators"] = {
        "2601.17117 v2 SIDM_MS.tex: M_BH ~ 200 M_sun": locator(g26, r"M_\{\\text\{BH\}\} \\approx 200"),
        "2601.17117 v2 SIDM_MS.tex: t = 580 t_0": locator(g26, r"580 t_0"),
        "2601.17117 v2 SIDM_MS.tex: 3e-8 (3\\times10^{-8})": locator(g26, r"3\s*\\times\s*10\^\{\s*-\s*8\s*\}"),
        "astro-ph/0111176 v3 SMBH_SIDM_Xiv2.tex: 10^{-8}-10^{-6}": locator(bs, r"10\^\{-8\}-10\^\{-6\}"),
    }
    json.dump(r, open(os.path.join(out, "rv_note.json"), "w"), indent=1)
    figure(r, out)
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
