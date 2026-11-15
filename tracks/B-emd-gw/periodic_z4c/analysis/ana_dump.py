#!/usr/bin/env python3
"""Validation of the metric dumps written for the gw_diag package (set lw3d_dump):
32^3 box [-1/2, 1/2]^3, TT wave k = (1, 0, 0), A = 1e-6, two periods, a restart file
(double precision, all Z4c variables) and bin files (float32: z4c, adm, con, weyl)
every 1/16 period.

For every restart dump: largest error of gt_ij, At_ij and of the ADM gamma_ij, K_ij
(athena_dumps.z4c_to_adm) against refsol.tt_exact, relative to A; amplitude and phase of
the k = (1,0,0) Fourier coefficient of h_+ = (gamma_zz - gamma_yy)/2. Figure: error
history, an x-y slice of h_+ at the last dump, an x-y slice of Re psi4 from the weyl
bin output at the same time. Writes figs/dump_check.{pdf,png}, tables/dump_check.json.

    python3 ana_dump.py
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
KV = (1, 0, 0)


def main():
    fs.use_style()
    m = cm.find_run("lw3d_dump_N32")
    rst = sorted(glob.glob(os.path.join(m["output_dir"], "rst", "*.rst")))
    t, eg, ea, egam, eK, amp, ph = [], [], [], [], [], [], []
    last = None
    for p in rst:
        d = ad.read_rst(p)
        z, y, x = np.meshgrid(d["z"], d["y"], d["x"], indexing="ij")
        ex = rs.tt_exact(x, y, z, d["time"], *KV, A0)
        adm = ad.z4c_to_adm(d)
        t.append(d["time"])
        eg.append(max(np.max(np.abs(d["g" + c] - ex["g" + c])) for c in ad.SYM)/A0)
        ea.append(max(np.max(np.abs(d["A" + c] - ex["A" + c])) for c in ad.SYM)/(np.pi*A0))
        egam.append(max(np.max(np.abs(adm["g_" + c] - ex["g" + c])) for c in ad.SYM)/A0)
        eK.append(max(np.max(np.abs(adm["K_" + c] - ex["A" + c])) for c in ad.SYM)/(np.pi*A0))
        hp = 0.5*(adm["g_zz"] - adm["g_yy"])
        F = np.fft.rfftn(hp)/hp.size              # axes (z, y, x); x is the last axis
        # h_+ = A sin(2 pi (x - t)) sampled at x_i = x0 + i/N, x0 = x1min + dx/2:
        # F[0,0,1] = A exp(2 pi i (x0 - t))/(2i), so 2i F exp(-2 pi i x0) exp(2 pi i t) = A
        x0 = d["mesh"]["x1min"] + 0.5/d["mesh"]["nx1"]
        zz = 2j*F[0, 0, 1]*np.exp(-1j*2*np.pi*x0)*np.exp(1j*2*np.pi*d["time"])
        amp.append(abs(zz)/A0 - 1.0)
        ph.append(np.angle(zz))                   # numerical minus exact phase advance
        last = (d, hp)
    o = np.argsort(t)
    t, eg, ea, egam, eK, amp, ph = (np.asarray(v)[o] for v in (t, eg, ea, egam, eK, amp, ph))
    w = sorted(glob.glob(os.path.join(m["output_dir"], "bin", "*.weyl.*.bin")))[-1]
    wd = ad.read_bin(w)

    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    a1 = fs.inch_axes(fig, 0.62, 0.48, 2.5, 2.3)
    a2 = fs.inch_axes(fig, 3.75, 0.48, 1.85, 1.85)
    a3 = fs.inch_axes(fig, 5.95, 0.48, 1.85, 1.85)
    a1.semilogy(t[1:], eg[1:], color=fs.PAL["red"], label=r"$\tilde\gamma_{ij}$")
    a1.semilogy(t[1:], ea[1:], color=fs.PAL["blue"], label=r"$\tilde A_{ij}/\pi$")
    a1.semilogy(t[1:], egam[1:], color=fs.PAL["yellow"], ls="--", label=r"$\gamma_{ij}$")
    a1.semilogy(t[1:], np.abs(amp[1:]), color=fs.PAL["green"], ls=":", label="|A/A0-1| (FFT)")
    a1.set_xlabel("t")
    a1.set_ylabel("max error / A")
    a1.legend(fontsize=7, loc="lower right")
    d, hp = last
    ext = [d["mesh"]["x1min"], d["mesh"]["x1max"], d["mesh"]["x2min"], d["mesh"]["x2max"]]
    im = a2.imshow(hp[16]/A0, origin="lower", extent=ext, cmap="RdBu_r", vmin=-1, vmax=1,
                   interpolation="nearest", rasterized=True)
    a2.set_title(r"$h_+/A$, t = %.3f" % d["time"], fontsize=9)
    a2.set_xlabel("x")
    a2.set_ylabel("y")
    vm = np.max(np.abs(wd["weyl_rpsi4"]))
    a3.imshow(wd["weyl_rpsi4"][16], origin="lower", extent=ext, cmap="RdBu_r", vmin=-vm,
              vmax=vm, interpolation="nearest", rasterized=True)
    a3.set_title(r"Re $\psi_4$ (radial tetrad), t = %.3f" % wd["time"], fontsize=9)
    a3.set_xlabel("x")
    a3.set_yticklabels([])
    for a in (a2, a3):
        a.set_xticks([-0.4, 0.0, 0.4])
        a.set_yticks([-0.4, 0.0, 0.4])
    fs.save(fig, os.path.join(cm.FIGS, "dump_check"))
    out = dict(run_id=m["run_id"], output_dir=m["output_dir"], n_rst=len(rst),
               t=t.tolist(), err_gt_max=float(np.max(eg)), err_At_max=float(np.max(ea)),
               err_gamma_max=float(np.max(egam)), err_K_max=float(np.max(eK)),
               fft_amp_err_end=float(amp[-1]), fft_phase_err_end=float(ph[-1]),
               weyl_file=w, weyl_rpsi4_max=float(vm))
    cm.save_json(out, os.path.join(cm.TABLES, "dump_check.json"))
    print({k: v for k, v in out.items() if k != "t"})


if __name__ == "__main__":
    main()
