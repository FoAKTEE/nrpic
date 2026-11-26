"""Schematic: architecture of Track B's calculation at gate G2, on release core-v0.7 (state of
2026-11-25, batch 21).

Each box is classified by evidence, not by authorship:
  verified (green)   used by the track in a registered run that passed its test;
  on the release (slate) in release core-v0.7 (CLAUDE.md, coord/INTERFACES/), not yet run by the
                     track, or queued in the shared card queue;
  to be written (red).
Evidence of the green boxes added since G1 (run ids under tracks/B-emd-gw/runs/; journals named):
  halo population box, constraint solve at 128^3 and 256^3, eight particles per cell (I3 holds):
    population/JOURNAL.md 2026-11-24 06:10 and the batch-17 entries;
  Z4c with particles, zero shift, to a = 143 at sigma1 = 0.014: B-20261123-014847-f295ab4,
    analysis B-20261124-131918-e71996f; its stop at sigma1 = 0.028 (a = 30.7): B-20261123-035002-bcc82bd,
    restarts X0-X2 B-20261124-210432-6c4d005, analysis B-20261125-115619-ad8b3f4;
  Gamma-driver shift in the population box: B-20261124-210431-6bf48af (gauge leg, to a = 143),
    analysis B-20261125-115558-2ab4161, comparison B-20261125-121830-9ecb59c;
  Newtonian mode with the Fourier Poisson solver, same particles: B-20261124-172958-fc4a2cf,
    -73b0662, analysis B-20261125-122434-060d53d, comparisons B-20261125-165836-70b17b6, -165845-0621554;
  FoF catalogue and halo matching; band strain against the particles: the same analyses;
  shearing dust of arXiv:2003.08014 (S1-S4, M1, L1): B-20261123-015919-dec4392;
  FLRW dust converging in mesh and particle number: flrw_conv (J3 B-20261121-202335-3e6a898).
Slate: restart on the termination signal and v0.7 chains (coord/INTERFACES/preempted_runs.md),
  step limit by the gauge speeds (step_limit.md), the 256^3 legs (q0007 zero shift, stopped; q0060 Gamma driver, to a = 143).
Green since batch 28: particle estimator without the rest-mass weight (analyze_gr.py --equal-mass, runs B-20261126-022356-52c2460 and -022407-87e8803). Red:
  halo masses by proper distance, York TT part on the curved slice, L2 of the shearing dust
  converged in the mesh (stage/G2/OPEN.md). No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_architecture_g2"
DONE, BRANCH, NEW = pf.GREEN_DARK, pf.SLATE, pf.RED
W, H = 30.0, 15.0


def column(ax, x, title, sub, items):
    pf.panel(ax, x, 3.3, 9.4, 11.3, radius=0.9)
    pf.text(ax, x + 4.7, 13.95, title, size=9.5, bold=True)
    pf.text(ax, x + 4.7, 13.25, sub, size=7.5, italic=True)
    y = 12.05
    for label, state in items:
        pf.block(ax, x + 0.4, y - 0.47, 8.6, 0.95, label, fill=state, size=7.2, radius=0.22)
        y -= 1.12
    return y


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    column(ax, 0.2, "Initial data", "constraint-solved on the torus", [
        ("scalar modes, spectral solve of the constraints", DONE),
        ("halo population box, 128^3 and 256^3 solves", DONE),
        ("eight particles per cell, same modes", DONE),
        ("Newtonian particles of the same field", DONE),
        ("shearing dust (arXiv:2003.08014)", DONE),
        ("crossed waves, plane-wave null (G1)", DONE),
        ("data with a TT part in the expanding box", NEW),
        ("thin periodic boxes", BRANCH),
    ])
    column(ax, 10.3, "Evolution", "AthenaK, release core-v0.7", [
        ("Z4c with particles, zero shift (stops at 0.028)", DONE),
        ("Gamma-driver shift in the population box", DONE),
        ("Newtonian mode, Fourier Poisson solver", DONE),
        ("non-finite stop and restarts from t = 8", DONE),
        ("256^3: zero shift stops, driven shift passes", DONE),
        ("restart on SIGTERM, v0.7 chains", BRANCH),
        ("step limit by the gauge speeds", BRANCH),
        ("refinement on particles per cell", BRANCH),
    ])
    column(ax, 20.4, "Analysis", "references outside the code", [
        ("flat TT projection, spatial-gauge piece", DONE),
        ("FoF halos, same-particle matching", DONE),
        ("radiated measure of the Newtonian box", DONE),
        ("metric strain against particle S^TT/k^2", DONE),
        ("particle estimator without rest-mass weight", DONE),
        ("halo masses by proper distance", NEW),
        ("York TT part on the curved slice", NEW),
        ("shearing-dust L2 converged in the mesh", NEW),
    ])
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, 8.4), (x1, 8.4), lw=1.2, head=8)
    labels = ["burst of a pancake through shell crossing", "spectrum of a halo box",
              "relativistic minus Newtonian, per k"]
    widths = [10.4, 6.6, 9.6]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.55, w, 0.95, lab, fill=pf.PLUM, size=7.2)
        x += w + 0.55
    pf.arrow(ax, (25.1, 3.3), (25.1, 2.55), lw=1.2, head=8)
    pf.text(ax, 0.6, 0.7, "deliverables of S2", size=7.5, italic=True, ha="left")
    pf.panel(ax, 12.2, 0.22, 17.2, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((12.7, DONE, "verified in a run"), (18.6, BRANCH, "release or queue"),
                         (24.5, NEW, "to be written")):
        pf.rbox(ax, x0, 0.42, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.6, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
