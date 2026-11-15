#!/usr/bin/env python3
"""Constraints of the initial data of z4c_linear_wave for an oblique (k = (1,1,1)) and
an axis-aligned (k = (1,0,0)) wave vector (set lw3d_check), against the prediction for
the polarization tensor of the generator:
  H = -d_i d_j h_ij at first order = (2 pi)^2 A (k.e.k) sin(phi)   (k in cycles),
  M_i = d_j At_ij = -2 pi^2 |k| A (e.k)_i sin(phi).
Writes figs/lw3d_check.{pdf,png} and tables/lw3d_check.json.
"""
import glob
import os

import numpy as np
import matplotlib.pyplot as plt

import common as cm
import athena_dumps as ad
import refsol as rs
from nrpic import figstyle as fs

A0 = 1.0e-6


def predicted(kv):
    e, kn = rs.tt_polarization(*kv)
    E = np.array([[e["xx"], e["xy"], e["xz"]], [e["xy"], e["yy"], e["yz"]],
                  [e["xz"], e["yz"], e["zz"]]])
    k = np.array(kv, float)
    Hamp = (2*np.pi)**2*A0*abs(k @ E @ k)
    Mamp = 2*np.pi**2*kn*A0*np.abs(E @ k)
    # volume norms of the history (integral of the square over the unit box)
    return dict(H_max=Hamp, M_max=Mamp.tolist(), H_norm2=Hamp**2/2,
                M_norm2=float(np.sum(Mamp**2)/2))


def main():
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH + 0.6, 3.0))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.95)
    out = {}
    for nm, kv, colr in (("diag", (1, 1, 1), fs.PAL["red"]), ("axis", (1, 0, 0), fs.PAL["blue"])):
        m = cm.find_run(f"lw3d_check_{nm}")
        h = np.loadtxt(glob.glob(os.path.join(m["output_dir"], "*.hst"))[0])
        h = h[h[:, 10] > 0]                      # the t = 0 row has no ADM data yet
        ax.semilogy(h[:, 0], h[:, 3], color=colr, ls="-", label=f"k = {kv}: H")
        ax.semilogy(h[:, 0], h[:, 4], color=colr, ls="--", label=f"k = {kv}: M")
        p = predicted(kv)
        if p["H_norm2"] > 0:
            ax.axhline(p["H_norm2"], **dict(fs.THIN, ls=":"))
        c = ad.read_bin(sorted(glob.glob(os.path.join(m["output_dir"], "bin",
                                                      "*.con.*.bin")))[1])
        out[nm] = dict(run_id=m["run_id"], k=kv, predicted=p,
                       H_norm2=float(h[0, 3]), M_norm2=float(h[0, 4]),
                       H_max=float(np.abs(c["con_H"]).max()),
                       Mx_max=float(np.abs(c["con_Mx"]).max()),
                       My_max=float(np.abs(c["con_My"]).max()),
                       Mz_max=float(np.abs(c["con_Mz"]).max()), t_dump=c["time"])
    ax.set_xlabel("t")
    ax.set_ylabel(r"$\int C^2\,dV$")
    ax.set_ylim(1e-24, 1e-7)
    ax.legend(fontsize=7, loc="center right")
    fs.save(fig, os.path.join(cm.FIGS, "lw3d_check"))
    cm.save_json(out, os.path.join(cm.TABLES, "lw3d_check.json"))
    for k, v in out.items():
        print(k, v)


if __name__ == "__main__":
    main()
