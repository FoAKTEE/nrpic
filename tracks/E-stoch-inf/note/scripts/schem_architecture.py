"""Schematic: architecture of Track E's calculation (stochastic inflation in numerical
relativity), state of gate G1 (2026-11-21, after releases core-v0.4 and core-v0.5).

Four states (CLAUDE.md "What exists"; tracks/core/CHANGELOG.md):
- v0.3     = in AthenaK release core-v0.3 (coord/INTERFACES/scalar_field.md): Z4c with the
             scalar field, modes in lockstep, noise synthesis per MeshBlock, kicks at the
             stage times, exact restart, counter-based amplitudes;
- v0.4/0.5 = released on 2026-11-21: core/scalar-2 a58e95b/207424d in core-v0.4 (initial
             slice at N* `id = stochastic`, constraint record sf.con.hst, NRSFDMP2 dumps,
             mode tables of make_case.py; coord/INTERFACES/scalar_field_2.md) and
             core/scalar-3 in core-v0.5 (inflection case at N*, signed constraint means,
             named mode keys, linear twin python/nrpic/sf_lattice.py;
             coord/INTERFACES/scalar_field_3.md). The G1 runs used the tested-branch
             executable of core/scalar-2 (decision 0013); the release processor build
             reproduces it word for word at 32^3 (stage/REVIEW-wave3.md, LR1);
- track    = the track's references and analysis outside the code (spec/ref, langevin/,
             noise/, analysis/, ladder/ scripts; stage/G1/EVIDENCE.md sections 1-4);
- new      = still to be done or under way: USR runs at 256^3 on cards (package usr),
             window and Courant sensitivity L9 (package window), level-1 and level-2
             coefficients, a slice beyond first order, compaction statistics, the hand-over
             to the particles of Track A (stage/G1/OPEN.md; spec/scope/SCOPE.md 4b and 10).
No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_architecture"
REL, BRANCH, TRACK, NEW = pf.GREEN_DARK, pf.SLATE, pf.OLIVE, pf.RED   # BRANCH: core-v0.4/v0.5
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
        ("slice beyond first order in the constraints", NEW),
        ("box-mean and local coefficients (levels 1, 2)", NEW),
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
        ("ultra-slow-roll runs at $256^3$ on cards", NEW),
    ])
    column(ax, 20.4, "Analysis", "references and analysis outside the code", [
        ("full and deformed Mukhanov-Sasaki modes", TRACK),
        ("stochastic delta N, both potentials", TRACK),
        ("noise validator, tests A0-A15", TRACK),
        (r"dump reader, curvature perturbation $\mathcal{R}^\mathrm{NR}$", TRACK),
        ("per-mode amplitudes, freezing check", TRACK),
        ("odd and even constraint parts, floor", TRACK),
        ("linear twin of the mesh (constraint defect)", BRANCH),
        ("window and Courant sensitivity (L9)", NEW),
        ("compaction function statistics", NEW),
        ("hand-over to the particles of Track A", NEW),
    ])
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, 10.2), (x1, 10.2), lw=1.2, head=8)
    labels = ["slow roll reproduced (G1)", "ultra-slow roll (G2)",
              "tail statistics against delta N (G3)", "initial conditions to Track A"]
    widths = [6.6, 5.6, 8.6, 7.4]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.95, w, 0.95, lab, fill=pf.PLUM, size=7.0)
        x += w + 0.25
    pf.arrow(ax, (25.1, 3.6), (25.1, 2.95), lw=1.2, head=8)
    pf.text(ax, 0.6, 1.15, "deliverables of S11", size=7.5, italic=True, ha="left")
    pf.panel(ax, 8.2, 0.2, 21.2, 1.0, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((8.6, REL, "core-v0.3"), (12.9, BRANCH, "core-v0.4, v0.5"),
                         (18.4, TRACK, "track analysis"), (23.6, NEW, "new, under way")):
        pf.rbox(ax, x0, 0.43, 1.2, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.5, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
