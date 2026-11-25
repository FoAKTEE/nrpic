"""Scope review of G3 (item 3, gauge leg): how far the geodesic slice of the USR box is from uniform expansion.

`lapse_kdriver` drives the mean curvature K towards its box mean. If K and the conformal factor chi are
already uniform on the geodesic slice, a K-driven slicing coincides with the geodesic one and the gauge leg
of SCOPE 4d.6 has no lever arm. This script reads every dump of one 128^3 USR run with the own parser of
`box_stats.py` and reports per dump: rms(K - <K>)/|<K>|, rms(chi/<chi> - 1), rms(alpha - 1), and the rms of
the curvature variable R^NR (from the same parts as box_stats.py) for scale.

Usage: kcheck.py OUTDIR --run DIR [--base usr]
Writes OUTDIR/kcheck.json and OUTDIR/fig_kcheck.{pdf,png}.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from box_stats import read_dump, read_modes, fs  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--run", required=True)
    ap.add_argument("--base", default="usr")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    files = sorted(p for p in os.listdir(a.run) if p.startswith(a.base + ".sf.") and p.endswith(".dump"))
    rows = []
    for name in files:
        stem = os.path.join(a.run, name[:-len(".dump")])
        h, f = read_dump(stem + ".dump", ["K", "chi", "alpha", "phi", "Pi"])
        md = read_modes(stem + ".modes")
        K, chi, al = f["K"], f["chi"], f["alpha"]
        hb = -K.mean() / (3.0 * al.mean())
        dphi = f["phi"] - f["phi"].mean()
        r_phi = (hb / f["Pi"].mean()) * dphi
        row = dict(dump=name, time=h["time"], ln_a=float(np.log(md["a"])),
                   rms_dK_over_K=float(np.std(K) / abs(K.mean())),
                   rms_dchi_over_chi=float(np.std(chi) / chi.mean()),
                   rms_alpha_minus_1=float(np.sqrt(np.mean((al - 1.0) ** 2))),
                   rms_Rphi=float(np.std(r_phi)))
        rows.append(row)
        print(row, flush=True)
        del f
    with open(os.path.join(a.out, "kcheck.json"), "w") as fp:
        json.dump(dict(run=a.run, rows=rows), fp, indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 3.0))
    cn = [r["ln_a"] for r in rows]
    ax.semilogy(cn, [max(r["rms_dK_over_K"], 1e-18) for r in rows], "o-", color=fs.SERIES[0], ms=3,
                label=r"rms $\delta K/|K|$")
    ax.semilogy(cn, [max(r["rms_dchi_over_chi"], 1e-18) for r in rows], "s-", color=fs.SERIES[1], ms=3,
                label=r"rms $\delta\chi/\chi$")
    ax.semilogy(cn, [max(r["rms_Rphi"], 1e-18) for r in rows], "^-", color=fs.SERIES[2], ms=3,
                label=r"rms $(H/\Pi)\,\delta\phi$")
    ax.set_xlabel(r"$N-N_*$ (ln $a$ of the record)")
    ax.set_ylabel("rms")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_kcheck"))


if __name__ == "__main__":
    main()
