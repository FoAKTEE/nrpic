"""Calibrate the digitized vector content of arXiv:2402.02178 Figs. InclD and afin into numbers.

    <venv>/bin/python -I paper_2402.py <dir with dig_InclD.json, dig_afin10M2e4.json> <out.json>

Inputs are the raw outputs of digitize_2402.py (scratch, regenerable).  Calibration on the
tick marks and grid lines of each axes, read from the same content stream (values below).
Locators: kb-data/raw/arxiv/2402.02178/v1/src/main.tex (figure environments at lines
528-538 (afin) and 595-605 (InclD)); figure files InclD.pdf, afin10M2e4.pdf of the same source.
"""
import json
import math
import os
import sys

import numpy as np

# fiducial parameters of 2402.02178 (main.tex:486, 491-515)
M_SUN_M = 4e6
M12 = 25.0 / M_SUN_M
A0 = 20000 * M12
RT = (1 / M12) ** (1 / 3) * A0                     # = 6.786 M; beta = RT / rp (main.tex:513-515)

# ---- InclD axes (PDF points): x grid lines beta = 0.4, 0.6, 0.8 at 112.976149, 190.730296,
# 268.484444; y: iota = 0 at 71.69715, pi at 259.185579 (grid lines and the shaded polygon)
X04, X06 = 112.976149, 190.730296
Y0, YPI = 71.69715, 259.185579


def incl_beta(x):
    return 0.4 + (x - X04) / (X06 - X04) * 0.2


def incl_iota(y):
    return (y - Y0) / (YPI - Y0) * math.pi


FAMILY = {  # stroke/fill colour (rounded) -> family (legend of InclD, main.tex:597-604)
    (1.0, 0.498, 0.055): "s0.9_Lz_pos",
    (0.173, 0.627, 0.173): "s0.9_Lz_neg",
    (0.58, 0.404, 0.741): "s0.9_Lz_0",
    (0.839, 0.153, 0.157): "newtonian_criterion",
    (0.122, 0.467, 0.706): "s0_shaded",
}


def rgb_key(c):
    return tuple(round(v, 3) for v in c)


def incld(path):
    d = json.load(open(path))
    out = {}
    # markers (each placement is written six times by the figure; deduplicate)
    for m in d["markers"]:
        fam = FAMILY.get(rgb_key(m["rgb_fill"]))
        if fam is None:
            continue
        out.setdefault(fam, set()).add((round(m["x"], 3), round(m["y"], 3)))
    res = {}
    for fam, pts in out.items():
        pts = sorted(pts)
        res[fam] = [dict(beta=incl_beta(x), rp=RT / incl_beta(x), iota=incl_iota(y),
                         iota_over_pi=incl_iota(y) / math.pi) for x, y in pts]
    # the Newtonian criterion line (stroked, red) and the s = 0 polygon's lower edge
    for s in d["strokes"]:
        fam = FAMILY.get(rgb_key(s["rgb"]))
        if fam == "newtonian_criterion" and len(s["pts"]) > 50:
            pts = sorted(set((round(x, 3), round(y, 3)) for x, y in s["pts"]))
            res[fam] = [dict(beta=incl_beta(x), rp=RT / incl_beta(x), iota=incl_iota(y),
                             iota_over_pi=incl_iota(y) / math.pi) for x, y in pts]
    for f in d["fills"]:
        if FAMILY.get(rgb_key(f["rgb"])) == "s0_shaded" and len(f["pts"]) > 50:
            low = {}
            for x, y in f["pts"]:
                if y < YPI - 1e-3:
                    low[round(x, 3)] = min(low.get(round(x, 3), 1e9), y)
            xs = sorted(set(round(x, 3) for x, _ in f["pts"]))
            res["s0_shaded"] = [dict(beta=incl_beta(x), rp=RT / incl_beta(x),
                                     iota=incl_iota(low.get(x, Y0)),
                                     iota_over_pi=incl_iota(low.get(x, Y0)) / math.pi)
                                for x in xs]
    return res


# ---- afin axes: iota = 0 at x = 49.770712, pi at 317.610712; L_z ticks -5, 0, 4 at
# y = 59.640392, 165.560522, 250.296626; colour bar 0..2 (ticks 0, 0.5, ..., 2 at
# y = 52.074116 ... 269.514116), colour map YlGnBu (its first colour (1, 1, 0.851) is the cell
# colour of a_fin = 0)
AX0, AXPI = 49.770712, 317.610712
AY_m5, AY_0 = 59.640392, 165.560522


def afin(path):
    import matplotlib
    cmap = matplotlib.colormaps["YlGnBu"]
    lut = np.array([cmap(i / 255.0)[:3] for i in range(256)])
    d = json.load(open(path))
    cells = []
    for f in d["fills"]:
        xs = [p[0] for p in f["pts"]]
        ys = [p[1] for p in f["pts"]]
        if abs(max(xs) - min(xs) - 7.44) > 1e-3 or abs(max(ys) - min(ys) - 4.53) > 1e-3:
            continue
        xc, yc = 0.5 * (max(xs) + min(xs)), 0.5 * (max(ys) + min(ys))
        rgb = np.array(f["rgb"])
        k = int(np.argmin(((lut - rgb) ** 2).sum(1)))
        resid = float(np.sqrt(((lut[k] - rgb) ** 2).sum()))
        cells.append((xc, yc, 2.0 * k / 255.0, resid))
    iotas = sorted(set(round(c[0], 3) for c in cells))
    lzs = sorted(set(round(c[1], 3) for c in cells))
    A = np.full((len(lzs), len(iotas)), np.nan)
    R = np.zeros_like(A)
    for xc, yc, v, r in cells:
        A[lzs.index(round(yc, 3)), iotas.index(round(xc, 3))] = v
        R[lzs.index(round(yc, 3)), iotas.index(round(xc, 3))] = r
    iota_v = [(x - AX0) / (AXPI - AX0) * math.pi for x in iotas]
    lz_v = [(y - AY_0) / ((AY_0 - AY_m5) / 5.0) for y in lzs]
    # solid black boundary (survival/disruption), the longest solid stroke of width 1.5
    solid = [s for s in d["strokes"] if s["width"] == 1.5 and s["dash"].startswith("[]")
             and rgb_key(s["rgb"]) == (0.0, 0.0, 0.0)]
    bnd = []
    for s in solid:
        bnd.append([[(x - AX0) / (AXPI - AX0) * math.pi, (y - AY_0) / ((AY_0 - AY_m5) / 5.0)]
                    for x, y in s["pts"]])
    mergers = [dict(iota=(m["x"] - AX0) / (AXPI - AX0) * math.pi,
                    Lz=(m["y"] - AY_0) / ((AY_0 - AY_m5) / 5.0))
               for m in d["markers"] if m["xobj"] == "/M0"]
    return dict(iota=iota_v, Lz=lz_v, a_fin=A.tolist(), colour_residual_max=float(R.max()),
                boundary_solid=bnd, mergers=mergers)


def main(indir, out):
    res = dict(
        source="arXiv:2402.02178v1, kb-data/raw/arxiv/2402.02178/v1/src (figures parsed as data)",
        fiducial=dict(M_sun=M_SUN_M, m1=15, m2=10, spin=0.9, rp=10.0, E=1.0, r_ini=100.0,
                      a0_over_m12=20000, a0_M=A0, mb_M=M12, rt_M=RT, beta_fiducial=RT / 10.0,
                      locators="main.tex:486 (M, s, m1, m2), 491-502 (rp, E, Lz, r_ini), "
                               "504-515 (a0, beta = 0.6786)"),
        InclD=dict(locator="main.tex:582-605, InclD.pdf; survivors lie above a line or in the "
                           "shaded area (main.tex:584-585)",
                   data=incld(os.path.join(indir, "dig_InclD.json"))),
        afin=dict(locator="main.tex:524-562, afin10M2e4.pdf; a_fin/a0 from the cell colour "
                          "(YlGnBu, 0..2; a_fin = 0 is a disrupted binary)",
                  data=afin(os.path.join(indir, "dig_afin10M2e4.json"))),
    )
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    inc = res["InclD"]["data"]
    for fam, pts in inc.items():
        print(fam, [(round(p["rp"], 2), round(p["iota_over_pi"], 4)) for p in pts])
    af = res["afin"]["data"]
    A = np.array(af["a_fin"])
    print("afin grid", A.shape, "colour residual max", af["colour_residual_max"],
          "survived fraction", float((A > 0).mean()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
