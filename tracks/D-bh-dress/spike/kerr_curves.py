"""Digitize the Kerr curves of Ferrer, da Rosa & Will 2017 (arXiv:1707.06302, "FdRW") from
their matplotlib PGF sources: fig_rho_a, fig_rho_theta, fig_rho_hern, fig_angle_hern,
figequator1, figemin.

The PGF files are untrusted downloads: they are only read as text and tokenized by
paper_curves.pgf_paths (this directory), nothing in them is executed. Output goes to the
given directory (scratch, never committed). Standard library only; run with python3 -I.

Axis maps: x from the x tick labels (anchored "top" at the tick position), y from the
horizontal dotted grid lines paired in order with the y tick labels; the x grid lines are
used as an independent check of the x map (residual written to the output).

usage: python3 -I kerr_curves.py <kb-data/raw/arxiv root> <outdir>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # our own code, not the download
from paper_curves import pgf_paths, _fit  # noqa: E402

GRAY = (0.690196, 0.690196, 0.690196)
FIGS = {
    # name: (curve key by dash pattern prefix)
    "fig_rho_a": {"{9.6": "a=0", "{5.6": "a=0.5", "": "a=0.8"},
    "fig_rho_hern": {"{9.6": "a=0", "{5.6": "a=0.5", "": "a=0.8"},
    "fig_rho_theta": {"{9.6": "theta=0", "{5.6": "theta=pi/3", "": "theta=pi/2"},
    "fig_angle_hern": {"{9.6": "theta=0", "{5.6": "theta=pi/3", "": "theta=pi/2"},
    "figequator1": None,      # four curves, keys assigned below by dash pattern
    "figemin": {"": "Emin(10Gm)"},
}


def digitize(pgf):
    paths, texts = pgf_paths(pgf)
    grid = [p for p in paths if p["dash"].startswith("{1.000000pt}{1.000000pt}")]
    xg = sorted({round(p["pts"][0][0], 6) for p in grid
                 if abs(p["pts"][0][0] - p["pts"][1][0]) < 1e-9})
    yg = sorted({round(p["pts"][0][1], 6) for p in grid
                 if abs(p["pts"][0][1] - p["pts"][1][1]) < 1e-9})
    xlab = sorted((float(x), float(v)) for x, y, opt, v in texts if "top" in opt)
    ylab = sorted((float(y), float(v)) for x, y, opt, v in texts if "base" in opt)
    ax = _fit([p for p, _ in xlab], [v for _, v in xlab])
    info = {"n_xgrid": len(xg), "n_ygrid": len(yg), "n_xlab": len(xlab), "n_ylab": len(ylab)}
    if len(yg) != len(ylab):
        raise ValueError(f"{pgf}: {len(yg)} y grid lines for {len(ylab)} y labels")
    ay = _fit(yg, [v for _, v in ylab])
    # check: x grid lines against the x map (values should be the labels)
    if xg:
        xv = [ax[0] * g + ax[1] for g in xg]
        lv = [v for _, v in xlab]
        info["xgrid_vs_labels_maxabs"] = max(min(abs(a - b) for b in lv) for a in xv)
    curves = []
    for p in paths:
        if p["color"] is None or p["dash"].startswith("{1.0000") or len(p["pts"]) <= 10:
            continue
        if all(abs(c - g) < 1e-5 for c, g in zip(p["color"], GRAY)):
            continue
        curves.append({"x": [ax[0] * q[0] + ax[1] for q in p["pts"]],
                       "y": [ay[0] * q[1] + ay[1] for q in p["pts"]],
                       "color": p["color"], "dash": p["dash"]})
    info.update({"xfit": list(ax), "yfit": list(ay), "xlabels": xlab, "ylabels": ylab})
    return curves, info


def main(root, outdir):
    root, outdir = Path(root), Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    res = {}
    for name, keys in FIGS.items():
        curves, info = digitize(root / f"1707.06302/v2/src/{name}.pgf")
        named = {}
        if keys is None:      # figequator1: solid a=0, dashed 0.5, dot-dashed 0.8, dotted 0.998
            for c in curves:
                d = c["dash"]
                k = ("a=0" if d == "" else "a=0.5" if d.startswith("{5.6") else
                     "a=0.8" if d.startswith("{9.6") else "a=0.998")
                named.setdefault(k, c)
        else:
            for c in curves:
                for pre, k in keys.items():
                    if (pre == "" and c["dash"] == "") or (pre and c["dash"].startswith(pre)):
                        named.setdefault(k, c)
        res[name] = {"curves": named, "all_curves_n": len(curves), "axes": info}
    (outdir / "kerr_curves.json").write_text(json.dumps(res))
    for name, v in res.items():
        print(name, sorted(v["curves"]), "n", v["all_curves_n"],
              "xcheck", v["axes"].get("xgrid_vs_labels_maxabs"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
