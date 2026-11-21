#!/usr/bin/env python3
"""Test T4 of the initial-data solver: one plane wave on the torus against cosmo/ic
(tracks/core/JOURNAL-idsolve.md).

Reads the runs named torus_* in runs.json; computes from the same particle files the
references of idref.solve_torus (cosmo/ic/cosmo_id.py with its spectral Laplacian and
with the symbol of the seven-point Laplacian); writes torus_numbers.json and the figure
figs/torus_psi (PDF and PNG).
"""
import os
import sys

import numpy as np

import idlib
import idref
from nrpic import io as nio
from nrpic import figstyle as fs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BOX, HUBBLE, AMP = 2.0, 1.0, 0.1


def main():
    runs = idlib.load_json(os.path.join(idlib.HERE, "runs.json"))
    res, data, refs = {}, {}, {}
    for name in sorted(runs):
        r = runs[name]
        if r.get("test") != "t4" or not r["status"].startswith("exit 0"):
            continue
        d = idlib.run_dir(r["run_id"])
        b = idlib.read_idsolve_bin(os.path.join(d, "torus.idsolve.bin"))
        it, last = idlib.read_idsolve_txt(os.path.join(d, "torus.idsolve.txt"))
        fld = idlib.read_field(os.path.join(d, "torus.field.00000.bin"))
        n, ppc = r["n"], r["ppc"]
        key = (n, ppc)
        if key not in refs:
            x, u, m, _ = nio.read_nrp(os.path.join(idlib.SCRATCH, "idsolve_ic",
                                                   "wave_n%d_p%d.nrp" % (n, ppc)))
            refs[key] = dict(
                seven=idref.solve_torus(x, m, n, BOX, HUBBLE, "seven"),
                spectral=idref.solve_torus(x, m, n, BOX, HUBBLE, "spectral"))
        ref7, refs_ = refs[key]["seven"], refs[key]["spectral"]
        psi = b["psi"]
        rel = it[:, 1]
        fac = rel[1:]/rel[:-1] if len(rel) > 1 else np.array([])
        amp = 0.5*(psi.max() - psi.min())
        # difference of the two references along x: amplitude of the fundamental and
        # the largest value of the rest (the density of a displaced lattice has
        # structure at the scale of the cells, where the two symbols differ most)
        dref = (ref7["psi"] - refs_["psi"]).mean(axis=(1, 2))
        fk = np.fft.rfft(dref)/len(dref)
        fund = 2.0*abs(fk[1])
        fk[1] = 0.0
        fk[0] = 0.0
        rest = np.abs(np.fft.irfft(fk*len(dref), n=len(dref))).max()
        res[name] = dict(
            run_id=r["run_id"], n=n, ppc=ppc, mode=r["mode"], dx=BOX/n,
            iterations=int(it[-1, 0]), cg_steps=int(it[:, 10].sum()),
            cg_max_per_solve=int(it[:, 10].max()), v_cycles=int(it[:, 11].sum()),
            last_factors=[float(v) for v in fac[-4:]], rel_final=float(rel[-1]),
            psi_mean=float(psi.mean()), psi_amplitude=float(amp),
            diff_seven_max=float(np.abs(psi - ref7["psi"]).max()),
            diff_spectral_max=float(np.abs(psi - refs_["psi"]).max()),
            mean_minus_seven=float(psi.mean() - ref7["psi"].mean()),
            mean_minus_spectral=float(psi.mean() - refs_["psi"].mean()),
            ref_seven_iterations=len(ref7["hist"]), ref_seven_residual=ref7["hist"][-1],
            ref_spectral_iterations=len(refs_["hist"]),
            ref_spectral_residual=refs_["hist"][-1],
            ref_seven_minus_spectral_max=float(np.abs(ref7["psi"] - refs_["psi"]).max()),
            ref_difference_fundamental=float(fund), ref_difference_rest_max=float(rest),
            E_diff_max=float(np.abs(b["E"] - ref7["E"]).max()),
            H_before_max=float(it[0, 4]), H_after_max_solver=float(it[-1, 4]),
            H_after_rms_solver=float(it[-1, 5]),
            H_field_max=float(np.abs(fld["H"]).max()),
            H_field_rms=float(np.sqrt(np.mean(fld["H"]**2))),
            F7_after_max=float(it[-1, 6]), summary=last)
        data[name] = (b, it, fld, ref7, refs_)
    # linear theory: amplitude of psi - <psi>
    rho = 3.0*HUBBLE**2/(8.0*np.pi)
    k = 2.0*np.pi/BOX
    sigma = 12.0*np.pi*rho
    lin = 2.0*np.pi*rho*AMP/(k*k + sigma)
    idlib.save_json(os.path.join(idlib.HERE, "torus_numbers.json"),
                    dict(test="T4", box=BOX, hubble=HUBBLE, amp=AMP,
                         linear_amplitude=lin, mu=sigma/k**2, cases=res))

    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.2), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.95, wspace=0.27,
                        hspace=0.08)
    for colm, ppc in ((0, 1), (1, 2)):
        ax = axs[0, colm]
        for n, c in ((32, fs.PAL["red"]), (64, fs.PAL["blue"])):
            name = "torus_stencil_p%d_n%d" % (ppc, n)
            if name not in data:
                continue
            b, it, fld, ref7, refsp = data[name]
            x = idlib.centres(n, 0.0, BOX)
            ax.plot(x, (b["psi"][:, 0, 0] - 1.0)*1e3, color=c, label="code, N = %d" % n)
            ax.plot(x, (refsp["psi"][:, 0, 0] - 1.0)*1e3, ls=":", color="k", lw=1.0)
        ax.set_ylabel(r"$(\psi - 1)\times 10^3$")
        ax.set_title("%d particle(s) per cell and direction" % ppc, fontsize=10)
        ax.legend(fontsize=8)
        ax = axs[1, colm]
        for n, c in ((32, fs.PAL["red"]), (64, fs.PAL["blue"])):
            for mode, ls in (("stencil", "-"), ("code", "--")):
                name = "torus_%s_p%d_n%d" % (mode, ppc, n)
                if name not in data:
                    continue
                b, it, fld, ref7, refsp = data[name]
                x = idlib.centres(n, 0.0, BOX)
                ax.semilogy(x, np.abs(b["psi"][:, 0, 0] - refsp["psi"][:, 0, 0]) + 1e-17,
                            color=c, ls=ls, label="%s %d, spectral" % (mode, n))
                if mode == "stencil":
                    ax.semilogy(x, np.abs(b["psi"][:, 0, 0] - ref7["psi"][:, 0, 0]) + 1e-17,
                                color=c, ls=":", lw=1.0,
                                label="stencil %d, seven-point" % n)
        ax.set_ylim(1.0e-14, 1.0e-3)
        ax.set_xlabel(r"$x$")
        ax.set_ylabel(r"$|\psi - \psi_{\rm ref}|$")
        ax.legend(fontsize=7, ncol=2, loc="center", bbox_to_anchor=(0.53, 0.31),
                  columnspacing=1.0, handlelength=1.6)
    fs.save(fig, os.path.join(idlib.FIGS, "torus_psi"))
    plt.close(fig)

    print("linear amplitude %.4e, mu = %.3f" % (lin, sigma/k**2))
    for name in sorted(res):
        r = res[name]
        print("   references: seven - spectral max %.3e, fundamental %.3e, rest max %.3e" % (
            r["ref_seven_minus_spectral_max"], r["ref_difference_fundamental"],
            r["ref_difference_rest_max"]))
        print("%-24s it %2d cg %3d(max %d) vc %4d | amp %.4e mean-1 %+.3e | vs seven %.2e "
              "(mean %+.1e) vs spectral %.2e | E diff %.1e | H %.2e -> %.2e (field %.2e) "
              "fac %s" % (
                  name, r["iterations"], r["cg_steps"], r["cg_max_per_solve"], r["v_cycles"],
                  r["psi_amplitude"], r["psi_mean"] - 1.0, r["diff_seven_max"],
                  r["mean_minus_seven"], r["diff_spectral_max"], r["E_diff_max"],
                  r["H_before_max"], r["H_after_max_solver"], r["H_field_max"],
                  " ".join("%.2f" % f for f in r["last_factors"][-2:])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
