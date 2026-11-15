"""Digitize the printed curves of SFW (arXiv:1305.2619, Figs. 1 and 3) and of the Kerr
sequel (arXiv:1707.06302, Figs. fig_rho_a and fig_rho_hern) from their vector sources.

The figure files are untrusted downloads: they are only read and tokenized here (PDF
content stream after zlib inflation; matplotlib PGF text), nothing in them is executed.
The extracted curves are written to the output directory (scratch, never committed).
Standard library only, so that it runs under python3 -I (rule 8 of CLAUDE.md).

usage: python3 -I paper_curves.py <kb-data/raw/arxiv root> <outdir>
"""
import json
import re
import sys
import zlib
from pathlib import Path



def _fit(xs, ys):
    """Least-squares line ys = a xs + b; returns (a, b)."""
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    a = sxy / sxx
    return a, my - a * mx


def pdf_paths(pdf_file):
    """Stroked polylines of the first content stream: list of dicts with points (PDF pt),
    gray level, dash pattern and line width."""
    data = Path(pdf_file).read_bytes()
    m = re.search(rb"stream\r?\n", data)
    end = data.find(b"endstream", m.end())
    text = zlib.decompress(data[m.end():end]).decode("latin1")
    # drop text objects
    text = re.sub(r"BT.*?ET", " ", text, flags=re.S)
    toks = re.findall(r"\[[^\]]*\]|[-+]?\d*\.\d+|[-+]?\d+|[A-Za-z*']+", text)
    stack, path, cur, out = [], [], [], []
    gs = {"gray": 0.0, "dash": "[]", "w": 1.0}
    gstack = []
    for t in toks:
        if re.fullmatch(r"[-+]?\d*\.\d+|[-+]?\d+", t) or t.startswith("["):
            stack.append(t)
            continue
        if t == "m":
            if len(cur) > 1:
                path.append(cur)
            cur = [(float(stack[-2]), float(stack[-1]))]
        elif t == "l":
            cur.append((float(stack[-2]), float(stack[-1])))
        elif t == "c":
            cur.append((float(stack[-2]), float(stack[-1])))
        elif t in ("S", "B", "s"):
            if len(cur) > 1:
                path.append(cur)
            for p in path:
                out.append({"pts": [list(q) for q in p], **gs})
            path, cur = [], []
        elif t in ("f", "n", "h", "W"):
            if t in ("f", "n"):
                path, cur = [], []
        elif t == "G":
            gs["gray"] = float(stack[-1])
        elif t == "RG":
            gs["gray"] = tuple(float(v) for v in stack[-3:])
        elif t == "d":
            gs["dash"] = stack[-2]
        elif t == "w":
            gs["w"] = float(stack[-1])
        elif t == "q":
            gstack.append(dict(gs))
        elif t == "Q":
            gs = gstack.pop() if gstack else gs
        stack = []
    return out


def pgf_paths(pgf_file):
    """Stroked paths of a matplotlib PGF file with their colour and dash, in inches."""
    text = Path(pgf_file).read_text(encoding="latin1")
    out = []
    for scope in re.findall(r"\\begin\{pgfscope\}(.*?)\\end\{pgfscope\}", text, flags=re.S):
        if "pgfusepath{stroke}" not in scope:
            continue
        col = re.search(r"currentstroke\}\{rgb\}\{([\d.,]+)\}", scope)
        dash = re.search(r"\\pgfsetdash\{((?:\{[^}]*\})*)\}", scope)
        pts = re.findall(r"\\pgfpath(?:moveto|lineto)\{\\pgfqpoint\{([-\d.]+)in\}\{([-\d.]+)in\}\}",
                         scope)
        if len(pts) < 2:
            continue
        out.append({"pts": [[float(a), float(b)] for a, b in pts],
                    "color": tuple(float(v) for v in col.group(1).split(",")) if col else None,
                    "dash": dash.group(1) if dash else ""})
    texts = re.findall(r"\\pgftext\[x=([-\d.]+)in,y=([-\d.]+)in,([^\]]*)\]\{.*?\\displaystyle ([-\d.]+)\\\)\}",
                       text)
    return out, texts


def main(root, outdir):
    root, outdir = Path(root), Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    res = {}

    # ---- SFW Fig. 1 (phasespace2.pdf): x 0..100 r/Gm, y 0..1 (1e8 GeV/cm^3) ----------
    # axes rectangle from the clip path, tick 0 at x0 and tick 4 at x=54.388 (checked)
    f1 = root / "1305.2619/v1/src/phasespace2.pdf"
    x0, y0, w, h = 43.5170708719, 34.9297512259, 271.7808219178, 173.3881656109
    paths = pdf_paths(f1)
    curves = [p for p in paths if p["w"] > 1.0 and len(p["pts"]) > 20]
    for p, name in zip(curves, ["sfw_fig1_relativistic", "sfw_fig1_gs"]):
        X = [(q[0] - x0) / w * 100.0 for q in p["pts"]]
        Y = [(q[1] - y0) / h * 1.0 for q in p["pts"]]
        res[name] = {"x": X, "y": Y, "dash": p["dash"],
                     "x_is": "r/Gm", "y_is": "rho [1e8 GeV/cm^3]"}

    # ---- SFW Fig. 3 (bhhernquist.pdf): x 0..7 log10(r/R_S); y from tick labels -------
    f3 = root / "1305.2619/v1/src/bhhernquist.pdf"
    x0, y0, w, h = 41.7123456715, 35.6250655501, 271.7808219178, 173.3881656109
    paths = pdf_paths(f3)
    # y ticks: horizontal 4-pt segments starting on the left axis
    ticks = sorted({round(p["pts"][0][1], 4) for p in paths
                    if len(p["pts"]) == 2 and abs(p["pts"][0][0] - x0) < 1e-3
                    and abs(p["pts"][1][0] - x0) > 1.0 and abs(p["pts"][0][1] - p["pts"][1][1]) < 1e-6})
    # tick labels 10, 12, ..., 18 at the major ticks (every other tick if minor ones exist)
    res["sfw_fig3_yticks_pt"] = ticks
    # major (4 pt) y ticks at 61.0155 (label 10), 90.9047 (12), ..., 180.5723 (18) and
    # major x ticks every 38.8258 pt from x0 (labels 0..7), read with the tick lengths
    yt0, ypu = 61.0155, (180.5723 - 61.0155) / 8.0
    xpu = (313.4932 - 41.7123) / 7.0
    curves = [p for p in paths if p["w"] > 1.0 and len(p["pts"]) > 10]
    res["sfw_fig3_ncurves"] = len(curves)
    for k, p in enumerate(curves):
        res[f"sfw_fig3_curve{k}"] = {"x": [(q[0] - x0) / xpu for q in p["pts"]],
                                     "y": [10.0 + (q[1] - yt0) / ypu for q in p["pts"]],
                                     "gray": p["gray"], "dash": p["dash"],
                                     "x_is": "log10(r/R_S)", "y_is": "log10(rho [GeV/cm^3])"}
    res["sfw_fig3_axes_pt"] = [x0, y0, w, h]

    # ---- Kerr sequel PGF figures --------------------------------------------------------
    for name in ["fig_rho_a", "fig_rho_hern"]:
        paths, texts = pgf_paths(root / f"1707.06302/v2/src/{name}.pgf")
        grid = [p for p in paths if p["dash"].startswith("{1.000000pt}{1.000000pt}")]
        xg = sorted({p["pts"][0][0] for p in grid if abs(p["pts"][0][0] - p["pts"][1][0]) < 1e-9})
        yg = sorted({p["pts"][0][1] for p in grid if abs(p["pts"][0][1] - p["pts"][1][1]) < 1e-9})
        xlab = [(float(x), float(v)) for x, y, opt, v in texts if "top" in opt]
        ylab = [(float(y), float(v)) for x, y, opt, v in texts if "base" in opt]
        xlab.sort(); ylab.sort()
        # map: x gridlines carry the x labels (same x); y gridlines are paired in order
        xv = [v for _, v in xlab]; xp = xg[:len(xv)]
        yv = [v for _, v in ylab]; ypp = yg[:len(yv)]
        ax = _fit(xp, xv); ay = _fit(ypp, yv)
        cur = [p for p in paths if p["color"] is not None and not p["dash"].startswith("{1.0000")
               and len(p["pts"]) > 10]
        out = []
        for p in cur:
            out.append({"x": [ax[0] * q[0] + ax[1] for q in p["pts"]],
                        "y": [ay[0] * q[1] + ay[1] for q in p["pts"]],
                        "color": p["color"], "dash": p["dash"]})
        res[name] = {"curves": out, "xfit": list(ax), "yfit": list(ay),
                     "xlabels": xlab, "ylabels": ylab, "xgrid": xg, "ygrid": yg}
    (outdir / "paper_curves.json").write_text(json.dumps(res))
    print("wrote", outdir / "paper_curves.json")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
