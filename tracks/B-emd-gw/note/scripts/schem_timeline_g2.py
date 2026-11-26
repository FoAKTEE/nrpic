"""Schematic: stage timeline of Track B at gate G2 (state of 2026-11-25, batch 21).

Gates and targets: coord/CHARTER.md section 9.2 and the Track B sheet (9.5); G0 passed
2026-11-19 and G1 passed with reservations 2026-11-21 (coord/GATES.md); what G2 still lacks:
stage/G2/OPEN.md (batch 28: the GM analysis, rulings on C1 and C3, verifier C18). Gate
positions are evenly spaced; the labels give the targets. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_timeline_g2"
W, H = 30.0, 12.0
GATES = [
    ("G0 scoping", "passed 11-19", pf.GREEN_DARK,
     "first source fixed; ranges,\nexit criteria, risks, compute;\nnote and schematics"),
    ("G1 baseline", "passed 11-21", pf.GREEN_DARK,
     "both diagnostics on an oblique\nand an expanding-box wave;\nNewtonian-mode baseline"),
    ("G2 capability", "months 3-4", pf.SLATE,
     "FLRW converges; the\npopulation box in full GR,\ntwo gauges, Newtonian mode"),
    ("G3 science", "months 6-9", pf.RED,
     "amplitude scan through\ncrossing, converged three\nways; when GR matters"),
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
    pf.text(ax, 0.9, 10.9, "now: the Gamma-driver box at two meshes, eight particles per cell and twice the amplitude; mesh convergence being read",
            size=7.5, ha="left", italic=True)
    ax.add_patch(pf.Polygon([(14.2, 5.75), (14.6, 5.75), (14.4, 5.45)], closed=True,
                            fc=pf.RED, ec="none", zorder=8))
    pf.text(ax, 14.4, 6.05, "now", size=7.0, color=pf.RED)
    pf.brace(ax, 3.6, 8.8, 3.6, "", below=True)
    pf.text(ax, 6.2, 2.25, "wave diagnostics checked\nindependently (G1 review)",
            size=7.0, color=pf.ROSE)
    pf.brace(ax, 9.6, 14.8, 3.6, "", below=True)
    pf.text(ax, 12.2, 2.0, "FLRW dust converged; shearing\ndust run (L2 not converged);\n"
            "gauge leg of the population box", size=7.0, color=pf.ROSE)
    pf.brace(ax, 15.6, 20.8, 3.6, "", below=True)
    pf.text(ax, 18.2, 2.0, "strain at the second mesh read;\nrulings on L2 and constraints;\n"
            "fresh verifier", size=7.0, color=pf.ROSE)
    pf.brace(ax, 21.6, 26.6, 3.6, "", below=True)
    pf.text(ax, 24.1, 2.25, "Newtonian box spectra\nof the literature read", size=7.0,
            color=pf.ROSE)
    pf.text(ax, 0.6, 0.55, "needs between gates", size=7.5, italic=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
