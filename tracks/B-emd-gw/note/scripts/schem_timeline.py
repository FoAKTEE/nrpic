"""Schematic: stage timeline of Track B (note v2, state of 2026-11-20).

Gates and targets: coord/CHARTER.md section 9.2 and the Track B sheet (9.5), as made concrete
in stage/G0/REPORT.md section 8 (targets weeks 3-4, months 3-4, 6-9, 10-12); state:
stage/G0/OPEN.md, stage/G1/STATUS.md; rulings: decision 0013 (stand-in matter struck,
multi-code row = shearing dust plus the code's Newtonian mode), decision 0014 (40 card-hours
to the next gate). G0 passed: coord/GATES.md on main (tag stage/B-emd-gw/G0-pass-20261119).
What G1 still needs: stage/G1/OPEN.md items 1-6; v2 state: criterion 1 run and analysed
(waves/README.md, final analysis B-20261119-164402-7438a99), its independent check under way
(PLAN-wave3.md round 1, stage/G1/verifier3), second first-source round run, particle and mesh
legs being analysed (first_source/README.md). Gate positions are evenly spaced; the labels
give the targets. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_timeline"
W, H = 30.0, 12.0
GATES = [
    ("G0 scoping", "passed", pf.GREEN_DARK,
     "first source fixed; ranges,\nexit criteria, risks, compute;\nnote and schematics"),
    ("G1 baseline", "weeks 3-4", pf.SLATE,
     "both diagnostics on an oblique\nand an expanding-box wave;\nNewtonian-mode baseline"),
    ("G2 capability", "months 3-4", pf.SLATE,
     "background and growth\nconverge in particle number;\nfirst source before crossing"),
    ("G3 science", "months 6-9", pf.RED,
     "eps and amplitude scan\nthrough crossing, converged\nthree ways; when GR matters"),
    ("G4 paper", "months 10-12", pf.RED,
     "manuscript and\nreproduction package"),
]


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    y0 = 5.2
    pf.timeline(ax, 0.3, 29.7, y0, color=pf.GREEN_DARK, lw=2.2, fade_in=True, head=9)
    xs = [3.2, 9.2, 15.2, 21.2, 27.0]
    for x, (title, when, col, body) in zip(xs, GATES):
        ax.add_patch(pf.Circle((x, y0), 0.32, fc=col, ec=pf.WHITE, lw=1.0, zorder=7))
        pf.text(ax, x, y0 - 0.85, when, size=7.5, color=pf.ROSE, italic=True)
        cw = 5.4
        pf.callout(ax, x - cw / 2 + 0.1, 6.3, cw, 3.6, title, body, bar=col, size=7.0,
                   title_size=8.0, band=0.8)
        pf.line(ax, (x, y0 + 0.35), (x, 6.3), color=pf.GREY_LINE)
    pf.text(ax, 0.9, 10.9, "now: both G1 waves and the second first-source round run; the G1 package being closed",
            size=7.5, ha="left", italic=True)
    ax.add_patch(pf.Polygon([(8.2, 5.75), (8.6, 5.75), (8.4, 5.45)], closed=True,
                            fc=pf.RED, ec="none", zorder=8))
    pf.text(ax, 8.4, 6.05, "now", size=7.0, color=pf.RED)
    pf.brace(ax, 3.6, 8.8, 3.6, "", below=True)
    pf.text(ax, 6.2, 2.25, "independent check of the waves;\nparticle and mesh legs analysed",
            size=7.0, color=pf.ROSE)
    pf.brace(ax, 9.6, 14.8, 3.6, "", below=True)
    pf.text(ax, 12.2, 2.0, "jitter without a wave, TT spectra\nin the run, data with a TT\npart; "
            "shearing-dust test", size=7.0, color=pf.ROSE)
    pf.brace(ax, 15.6, 20.8, 3.6, "", below=True)
    pf.text(ax, 18.2, 2.0, "second-order reference in the\ncode's gauge; thin boxes;\n"
            "compute budget of the scan", size=7.0, color=pf.ROSE)
    pf.brace(ax, 21.6, 26.6, 3.6, "", below=True)
    pf.text(ax, 24.1, 2.25, "Newtonian box spectra\nof the literature read", size=7.0,
            color=pf.ROSE)
    pf.text(ax, 0.6, 0.55, "needs between gates", size=7.5, italic=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
