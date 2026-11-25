"""Schematic: architecture of Track E's calculation (stochastic inflation in numerical
relativity), state of gate G2 (2026-11-24, after release core-v0.7).

Four states (CLAUDE.md "What exists"; tracks/core/CHANGELOG.md):
- first releases (REL1) = core-v0.3 (coord/INTERFACES/scalar_field.md): Z4c with the scalar
  field, modes in lockstep, noise synthesis per MeshBlock, kicks at the stage times, exact
  restart, counter-based amplitudes;
- later releases (REL2) = core-v0.4 to v0.7: initial slice at N*, constraint record, dumps,
  noise_mode_scale (the amplitude lambda), inflection case, signed means, linear twin
  (scalar_field_2.md, scalar_field_3.md), level 2 of the backreaction and the noise on the mesh
  (core-v0.7, noise_level2.md); the USR ladder ran on the release card build of core-v0.6
  (g2prod/queue.txt);
- track = references and analysis outside the code (spec/ref, langevin/, noise/, usr/, window/,
  g2prod/, stage/G2/verifier/);
- ahead = a slice beyond first order, compaction statistics, the hand-over to Track A
  (spec/scope/SCOPE.md 10).
No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_architecture"
REL, BRANCH, TRACK, NEW = pf.GREEN_DARK, pf.SLATE, pf.OLIVE, pf.RED   # BRANCH: later releases
W, H = 30.0, 17.2


def column(ax, x, title, sub, items, w=9.4, top=16.7, bottom=3.6):
    pf.panel(ax, x, bottom, w, top - bottom, radius=0.9)
    pf.text(ax, x + w / 2, top - 0.62, title, size=9.5, bold=True)
    pf.text(ax, x + w / 2, top - 1.30, sub, size=7.5, italic=True)
    y = top - 2.45
    for label, state in items:
        pf.block(ax, x + 0.4, y - 0.45, w - 0.8, 0.90, label, fill=state, size=7.0, radius=0.22)
        y -= 1.06


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    column(ax, 0.2, "Initial slice and noise", "mode tables, slice at the start", [
        ("Friedmann background, both potentials", TRACK),
        ("Bunch-Davies modes to the start, all shells", TRACK),
        (r"mode tables $\mathcal{R}_k$, $\dot{\mathcal{R}}_k$ at the start", BRANCH),
        ("random amplitudes keyed by wave vector", REL),
        ("perturbed geodesic slice at the start", BRANCH),
        ("slice and mode table of the inflection case", BRANCH),
        (r"common amplitude $\lambda$ of sources and slice", BRANCH),
        ("box-mean and local coefficients (levels 1, 2)", BRANCH),
        ("slice beyond first order in the constraints", NEW),
        ])
    column(ax, 10.3, "Evolution", "AthenaK", [
        ("Z4c as BSSN, geodesic slicing, periodic", REL),
        ("scalar field coupled through the stress tensor", REL),
        ("modes in lockstep with every stage", REL),
        ("noise synthesis per MeshBlock, no FFT", REL),
        (r"kicks to $\Pi$, $K$ and $\tilde A_{ij}$ at stage times", REL),
        ("exact restart, layout-independent noise", REL),
        (r"record of $\mathcal{H}$, $\mathcal{M}$, $[\mathcal{H}]$, $[\mathcal{M}]$, signed means", BRANCH),
        ("dumps of fields and metric in double precision", BRANCH),
        ("ultra-slow-roll runs, $256^3$ and $320^3$, on cards", BRANCH),
        ("noise on the mesh, level 2 of the backreaction", BRANCH),
    ])
    column(ax, 20.4, "Analysis", "references and analysis outside the code", [
        ("full and deformed Mukhanov-Sasaki modes", TRACK),
        ("stochastic delta N, both potentials", TRACK),
        ("noise validator, tests A0-A15", TRACK),
        (r"dump reader, curvature perturbation $\mathcal{R}^\mathrm{NR}$", TRACK),
        ("per-mode amplitudes, freezing check", TRACK),
        ("odd and even constraint parts, three amplitudes", TRACK),
        ("linear twin of the mesh (constraint defect)", BRANCH),
        ("window sensitivity, resolution pair", TRACK),
        ("independent reader of the fresh check", TRACK),
        ("compaction statistics, hand-over to Track A", NEW),
    ])
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, 10.2), (x1, 10.2), lw=1.2, head=8)
    labels = ["slow roll reproduced (G1)", "ultra-slow roll (G2)",
              "tail statistics against delta N (G3)", "initial conditions to Track A"]
    widths = [6.6, 6.6, 8.0, 7.0]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.95, w, 0.95, lab, fill=pf.PLUM, size=7.0)
        x += w + 0.25
    pf.arrow(ax, (25.1, 3.6), (25.1, 2.95), lw=1.2, head=8)
    pf.text(ax, 0.6, 1.15, "deliverables of the track", size=7.5, italic=True, ha="left")
    pf.panel(ax, 8.2, 0.2, 21.2, 1.0, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((8.6, REL, "first release"), (13.4, BRANCH, "later releases"),
                         (18.6, TRACK, "track analysis"), (23.8, NEW, "ahead")):
        pf.rbox(ax, x0, 0.43, 1.2, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.5, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))
    fig.savefig(os.path.join(out, STEM + ".pdf"))   # vector copy for the note (small file)


if __name__ == "__main__":
    main()
