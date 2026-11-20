"""Reference table of the shear package (prediction P1): the closed form
cos(theta_lin) of draft.tex:262 at the paper's HL = 2^n, n = -7 ... 2 (draft.tex:287),
against my first-order evaluation and against rays shot through the linear solution
(shear_ref.py), in the code's and in the paper's coordinates; the linear launch slopes of
the cases of SPEC.md section 6. Writes $NRPIC_RUN_DIR/ref_table.{json,png,pdf} and copies
the JSON and PNG into ../results and ../figs.
"""
import json
import os
import shutil
import sys
import warnings

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shear_ref as sr  # noqa: E402
import figstyle as fs  # noqa: E402

warnings.filterwarnings("ignore")


def main():
    out = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results"))
    rows = []
    for n in range(-7, 3):
        HL = 2.0**n
        b = 1e-7*HL**2
        cl = sr.cos_lin(1.0, HL)
        fo = sr.first_order_parts(1.0, HL)[3]
        ct, tA, tB = sr.cos_theta_traced(b, HL, 1.0, "code")
        ctp, _, _ = sr.cos_theta_traced(b, HL, 1.0, "paper")
        rows.append({"HL": HL, "cos_lin_over_b": cl, "first_order_rel": fo/cl - 1.0,
                     "traced_code_rel": ct/(b*cl) - 1.0, "traced_paper_rel": ctp/(b*cl) - 1.0,
                     "delay_traced_tiny_b": tB - tA})
    cases = {"S1": (0.005, 1.0), "S2": (0.005, 1/16), "S3": (0.005, 4.0),
             "S4": (0.005, 1/128), "M1": (0.05, 1.0), "M2": (0.05, 4.0),
             "L1": (0.5, 1.0), "L2": (0.5, 4.0)}
    crow = []
    for name, (beta, HL) in cases.items():
        b = beta*HL**2
        sA, sB, he, c1 = sr.first_order_parts(b, HL)
        crow.append({"case": name, "beta": beta, "HL": HL, "b": b, "b_max": sr.b_max(HL),
                     "cos_lin": sr.cos_lin(b, HL), "slope_A_lin": sA, "slope_B_lin": sB,
                     "h_end_lin": he})
    res = {"table": rows, "cases": crow,
           "limit_small": sr.cos_lin(1.0, 1e-4), "limit_large_times_HL2": sr.cos_lin(1.0, 1e4)*1e8}
    with open(os.path.join(out, "ref_table.json"), "w") as f:
        json.dump(res, f, indent=1)
    for r in rows:
        print(f"HL = {r['HL']:9.7f}: cos_lin/b = {r['cos_lin_over_b']:.12f}; first order "
              f"{r['first_order_rel']:+.1e}; traced (code) {r['traced_code_rel']:+.1e}, "
              f"(paper) {r['traced_paper_rel']:+.1e}")
    for r in crow:
        print(f"{r['case']}: b = {r['b']:.6g} (max {r['b_max']:.4g}), cos_lin = "
              f"{r['cos_lin']:.10g}, s_A = {r['slope_A_lin']:+.6g}, s_B = {r['slope_B_lin']:+.6g}")
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.95, wspace=0.3)
    hl = np.logspace(-2.5, 1.0, 200)
    axs[0].loglog(hl, [sr.cos_lin(1.0, h) for h in hl], color=fs.PAL["blue"],
                  label="closed form (draft.tex:262)")
    axs[0].loglog(hl, 0.75*np.ones_like(hl), **fs.GUIDE, label=r"$3/4$, $2/(HL)^2$")
    axs[0].loglog(hl, 2.0/hl**2, **fs.GUIDE)
    HLs = [r["HL"] for r in rows]
    axs[0].loglog(HLs, [r["cos_lin_over_b"]*(1 + r["traced_code_rel"]) for r in rows], "o",
                  color=fs.PAL["red"], ms=4, label="rays shot (code coordinates)")
    axs[0].set_ylim(0.1, 2.0)
    axs[0].set_xlabel(r"$H_* L$")
    axs[0].set_ylabel(r"$\cos\vartheta_{\rm lin} / b$")
    axs[0].legend(fontsize=7, loc="lower left")
    axs[1].loglog(HLs, [max(abs(r["traced_code_rel"]), 1e-16) for r in rows], "o-",
                  color=fs.PAL["red"], ms=4, label="rays shot, code coordinates")
    axs[1].loglog(HLs, [max(abs(r["traced_paper_rel"]), 1e-16) for r in rows], "s--",
                  color=fs.PAL["yellow"], ms=4, label="rays shot, paper coordinates")
    axs[1].loglog(HLs, [max(abs(r["first_order_rel"]), 1e-16) for r in rows], "^:",
                  color=fs.PAL["green"], ms=4, label="first-order integrals")
    axs[1].axhline(1e-6, **fs.MASK_LINE)
    axs[1].set_xlabel(r"$H_* L$")
    axs[1].set_ylabel("|relative difference| to the closed form")
    axs[1].legend(fontsize=7, loc="upper left")
    fs.save(fig, os.path.join(out, "ref_table"))
    for d, fn in (("results", "ref_table.json"), ("figs", "ref_table.png")):
        dd = os.path.join(HERE, "..", d)
        os.makedirs(dd, exist_ok=True)
        if os.path.abspath(out) != os.path.abspath(dd):
            shutil.copy(os.path.join(out, fn), dd)


if __name__ == "__main__":
    main()
