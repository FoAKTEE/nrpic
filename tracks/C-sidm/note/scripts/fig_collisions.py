"""Figure: the references of the collision operator and the kernel test on the code.

(a) thermally averaged Moller speed of a Maxwell-Juttner gas, closed form against an
independent three-dimensional quadrature over both momenta, with the two limits;
(b) relative difference of the two, and of the quadrature at two resolutions;
(c) Monte Carlo checks of the reference implementation in standard errors (pair-sampled
rate, two-temperature relaxation rate against quadrature, entropy estimator);
(d) kernel test T0 on the code's collision kernels: largest error over the test vectors as
a fraction of its tolerance (collide/TESTS.md T0: 1e-13 of max(1,|u|); 4 eps of the pair
energy), for three compiler settings.
Reads runs xchk (X1), collref (ref_numbers.json), t0 (t0.json).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as cm  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_collisions"
TOL_U = 1e-13      # collide/TESTS.md T0 (fixed before any run)
TOL_P = 4.0        # in eps of the pair energy, same place


def main():
    out = cm.out_dir("figures")
    x1 = cm.load_json("xchk", "crosscheck.json")["X1"]["rows"]
    ref = cm.load_json("collref", "ref_numbers.json")
    t0 = cm.load_json("t0", "t0.json")

    th = np.array([r["theta"] for r in x1])
    closed = np.array([r["closed"] for r in x1])
    quad = np.array([r["quad128"] for r in x1])
    rq = np.abs([r["rel_quad"] for r in x1])
    rres = np.abs([r["rel_quad_res"] for r in x1])

    cz.use_style()
    fig = plt.figure(figsize=(7.0, 4.6))
    axa = fig.add_axes([0.085, 0.57, 0.38, 0.38])
    axb = fig.add_axes([0.595, 0.57, 0.38, 0.38])
    axc = fig.add_axes([0.085, 0.105, 0.38, 0.345])
    axd = fig.add_axes([0.595, 0.105, 0.38, 0.345])

    tt = np.logspace(-3.3, 2.3, 200)
    axa.plot(th, closed, color=cz.PAL["blue"], label="closed form")
    axa.plot(th, quad, "o", ms=4, mfc="none", mec="k", mew=0.8, label="3D quadrature")
    axa.plot(tt, np.sqrt(16 * tt / np.pi), **cz.GUIDE, label=r"$\sqrt{16\theta/\pi}$")
    axa.axhline(1.0, color="0.5", lw=1.0, ls=":")
    axa.set_xscale("log")
    axa.set_yscale("log")
    axa.set_ylim(0.03, 2.0)
    axa.set_xlim(5e-4, 200)
    axa.set_xlabel(r"temperature $\theta=T/m$")
    axa.set_ylabel(r"$\langle v_{\rm M\o l}\rangle$")
    axa.legend(frameon=False, loc="lower right", fontsize=7.5)
    axa.text(0.04, 0.9, "(a)", transform=axa.transAxes, fontsize=9)

    axb.plot(th, rq, "o-", ms=3.5, color=cz.PAL["red"], label="closed form vs quadrature")
    axb.plot(th, rres, "s--", ms=3.0, color="0.45", lw=1.0, label="quadrature, two resolutions")
    axb.set_xscale("log")
    axb.set_yscale("log")
    axb.set_xlim(5e-4, 200)
    axb.set_xlabel(r"temperature $\theta$")
    axb.set_ylabel("relative difference")
    axb.legend(frameon=False, loc="lower left", fontsize=7.5)
    axb.text(0.92, 0.9, "(b)", transform=axb.transAxes, fontsize=9)

    axc.axhspan(-2, 2, color="0.85", lw=0)
    r = ref["rate_mc_dev_sigma"]
    axc.plot([float(k) for k in r], list(r.values()), "o", ms=4, color=cz.PAL["blue"],
             label="collision rate")
    rel = np.array(ref["relax_mc_over_quad"])
    axc.plot(rel[:, 0] * 1.15, (rel[:, 1] - 1) / rel[:, 2], "s", ms=4, color=cz.PAL["red"],
             label="relaxation rate")
    e = ref["entropy_estimator_dev_sigma"]
    axc.plot([float(k) * 0.87 for k in e], list(e.values()), "^", ms=4,
             color=cz.PAL["green"], label="entropy")
    axc.axhline(0, color="k", lw=0.6)
    axc.set_xscale("log")
    axc.set_xlim(5e-4, 200)
    axc.set_ylim(-4, 4)
    axc.set_xlabel(r"temperature $\theta$")
    axc.set_ylabel("deviation / standard error")
    axc.legend(frameon=False, loc="lower center", fontsize=7.0, ncol=3, columnspacing=0.5, handletextpad=0.1)
    axc.text(0.015, 0.9, "(c)", transform=axc.transAxes, fontsize=9)

    flags = list(t0["flags"].keys())
    lab = {"O0": "-O0", "O2": "-O2", "O3native_fma": "-O3, FMA"}
    x = np.arange(len(flags))
    fu = [t0["flags"][f]["max_err_u"] / TOL_U for f in flags]
    fp = [t0["flags"][f]["max_cons_eps"] / TOL_P for f in flags]
    axd.bar(x - 0.18, fu, 0.34, color=cz.PAL["blue"], label="post-collision velocity")
    axd.bar(x + 0.18, fp, 0.34, color=cz.PAL["yellow"], label="pair four-momentum")
    axd.axhline(1.0, **cz.GUIDE)
    axd.set_yscale("log")
    axd.set_ylim(1e-4, 1e2)
    axd.set_xticks(x)
    axd.set_xticklabels([lab.get(f, f) for f in flags])
    axd.minorticks_off()
    axd.set_yticks([1e-4, 1e-3, 1e-2, 1e-1, 1, 1e1, 1e2])
    axd.set_ylabel("largest error / tolerance")
    axd.legend(frameon=False, loc="upper right", fontsize=7.5)
    axd.text(-0.45, 1.35, "tolerance", fontsize=7.5, ha="left")
    axd.text(0.015, 0.9, "(d)", transform=axd.transAxes, fontsize=9)

    cz.save(fig, os.path.join(out, STEM))
    cm.report_checks(STEM)
    print(f"{STEM}: X1 max |closed - quad128|/closed = {rq.max():.3e} at theta = "
          f"{th[int(np.argmax(rq))]:g}; at theta = {th[-1]:g}: {rq[-1]:.2e}")
    print(f"{STEM}: MC rate deviations in sigma: min {min(r.values()):+.2f} max "
          f"{max(r.values()):+.2f}; relax (ratio-1)/err: "
          f"{', '.join(f'{v:+.2f}' for v in (rel[:, 1] - 1) / rel[:, 2])}")
    print(f"{STEM}: T0 pass = {t0['pass']}, cases {t0['n_cases']}, skipped {t0['n_skipped']}; "
          f"max err_u/tol {max(fu):.3e}; max cons/tol {max(fp):.3f}")


if __name__ == "__main__":
    main()
