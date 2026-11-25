#!/usr/bin/env python3
"""Region (sphere) constraint norms of the particle-number runs (g2long entry 23, test R; C3, C11).

Reads `<base>.region.hst` (release core-v0.5 region diagnostic: proper-volume weighted
H2 = sqrt(<H^2>) inside and outside spheres of radius 6, 12, 30, 60 M about the origin and one
of 1.2 times the finder's mean radius, `_h0`). Since H2^2 V adds over volumes, shell norms are
    S_A1 = [1.2 r_AH, 6 M]:  (H2_in_s1^2 V_in_s1 - H2_in_h0^2 V_in_h0) / (V_in_s1 - V_in_h0)
    S_A2 = [6, 30 M]:        (H2_in_s3^2 V_in_s3 - H2_in_s1^2 V_in_s1) / (V_in_s3 - V_in_s1)
    S_A3 = [30, 60 M], and outside 60 M (H2_out_s4).
Checks R1 (volume identity), R2 (FN4's shells against its own z = 0 plane norms on the same
annuli, xc_plane.json), R3 (ratio of the N/4 run over the 4N run; particle noise gives 4).
A running chain is read only up to its second-newest restart time.

Usage: region_norms.py --out DIR --xc XC_PLANE_JSON [--running LABEL ...] LABEL=RUNDIR:BASE ...
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "flux_tools"))
import figstyle  # noqa: E402
import fluxio  # noqa: E402

NAME = re.compile(r"\[(\d+)\]=(\S+)")


def read_region(path):
    names, rows = None, []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                found = NAME.findall(line)
                if len(found) > 5:
                    names = [n for _, n in sorted(found, key=lambda p: int(p[0]))]
                continue
            s = line.strip()
            if s:
                rows.append([float(x) for x in s.split()])
    a = np.array(rows)
    d = {n: a[:, i] for i, n in enumerate(names)}
    return fluxio.dedupe(d)


def shell(d, inner, outer):
    vi, vo = d[f"V_in_{inner}"], d[f"V_in_{outer}"]
    hi, ho = d[f"H2_in_{inner}"], d[f"H2_in_{outer}"]
    num = ho ** 2 * vo - hi ** 2 * vi
    return np.sqrt(np.maximum(num, 0.0) / (vo - vi))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--xc", required=True)
    ap.add_argument("--xc-label", default="ES-FLK4N")
    ap.add_argument("--running", nargs="*", default=[], help="labels of chains still running")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R, out = {}, {}
    for s in a.runs:
        name, rest = s.split("=", 1)
        rd, base = rest.rsplit(":", 1)
        d = read_region(os.path.join(rd, base + ".region.hst"))
        tr = sorted(fluxio.restart_times(os.path.join(rd, "rst")))
        running = name in a.running
        t_ok = tr[-2] if (running and len(tr) >= 2) else np.inf
        keep = d["time"] <= t_ok + 1e-9
        d = {k: v[keep] for k, v in d.items()}
        sh = {"A1": shell(d, "h0", "s1"), "A2": shell(d, "s1", "s3"), "A3": shell(d, "s3", "s4"),
              "out60": d["H2_out_s4"]}
        vid = np.max(np.abs(d["V_in_s1"] + d["V_out_s1"] - d["V"]) / d["V"])
        nonfin = {k: [float(x) for x in d["time"][~np.isfinite(v)]][:6] for k, v in d.items()
                  if not np.all(np.isfinite(v))}
        fin = not nonfin
        R[name] = dict(t=d["time"], sh=sh, rh=d["radius_h0"])
        o = dict(dir=rd, running=running, t_read_to=float(d["time"][-1]), n=int(d["time"].size),
                 R1_volume_identity_max_rel=float(vid), R1_finite=bool(fin),
                 R1_nonfinite_columns_times=nonfin)
        for k, v in sh.items():
            o[k] = {str(T): float(np.interp(T, d["time"], v)) for T in (50.0, 100.0, 150.0, 200.0, 300.0, 400.0)
                    if d["time"][-1] >= T - 1e-9}
        out[name] = o
    X = json.load(open(a.xc))["summary"][a.xc_label]
    labs = list(R)
    R2 = {}
    fn4 = [n for n in labs if n == "FN4"]
    if fn4:
        for ann in ("A1", "A2"):
            for T in (100, 200):
                plane = X[ann].get(f"H2_{T}")
                sh = out["FN4"][ann].get(str(float(T)))
                if plane and sh:
                    R2[f"{ann}_{T}"] = dict(plane=plane, shell=sh, ratio_shell_over_plane=sh / plane)
    R3 = {}
    if "FNQ" in out and "FN4" in out:
        for ann in ("A1", "A2", "A3", "out60"):
            for T in ("50.0", "100.0", "150.0", "200.0", "300.0"):
                q, n4 = out["FNQ"][ann].get(T), out["FN4"][ann].get(T)
                if q and n4:
                    R3[f"{ann}_{T}"] = q / n4
    J = dict(runs=out, R2=R2, R3_ratio_NQ_over_4N=R3)
    with open(os.path.join(a.out, "region_norms.json"), "w") as f:
        json.dump(J, f, indent=1)

    figstyle.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.8))
    ls = {"FN4": "-", "FNQ": "--"}
    anns = [("A1", r"$[1.2r_{\rm AH},6M]$"), ("A2", r"$[6,30]M$"), ("A3", r"$[30,60]M$"), ("out60", r"$>60M$")]
    cols = figstyle.series_colors(len(anns))
    ax = axs[0]
    for n in labs:
        for j, (ann, lab) in enumerate(anns):
            ax.semilogy(R[n]["t"], R[n]["sh"][ann], ls=ls.get(n, ":"), color=cols[j], lw=0.9,
                        label=f"{n} {lab}")
    for ann, mk in (("A1", "s"), ("A2", "^")):
        for T in (100, 200, 300):
            v = X[ann].get(f"H2_{T}")
            if v:
                ax.plot([T], [v], mk, mfc="none", color="k", ms=6)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\sqrt{\langle H^2\rangle}$ on the shell")
    ax.set_title("(a) region shells; open marks: FN4 z = 0 plane (A1 s, A2 tri)", loc="left", fontsize=8.5)
    ax.legend(fontsize=5.5, ncol=2)
    ax = axs[1]
    if "FNQ" in R and "FN4" in R:
        tq = R["FNQ"]["t"]
        for j, (ann, lab) in enumerate(anns):
            r = R["FNQ"]["sh"][ann] / np.interp(tq, R["FN4"]["t"], R["FN4"]["sh"][ann])
            ax.plot(tq, r, color=cols[j], lw=0.9, label=lab)
        ax.axhline(4.0, color="k", ls="--", lw=0.8)
        ax.axhspan(2.8, 5.6, color="0.85", zorder=0)
        ax.axhline(1.5, color="C3", ls=":", lw=0.8)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"FNQ ($N/4$) / FN4 ($4N$)")
    ax.set_title("(b) ratio; band: R3 (noise gives 4), dotted: refutation 1.5", loc="left", fontsize=8.5)
    ax.legend(fontsize=7)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out, "region_norms." + ext), dpi=150)
    print(json.dumps(J, indent=1)[:4000])


if __name__ == "__main__":
    main()
