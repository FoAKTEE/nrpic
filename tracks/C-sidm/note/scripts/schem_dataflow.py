"""Schematic: data flow of the track's runs, from initial data to the note's figures and ledger
(note v1, 2026-11-20; checklist item C10 of gate G1).

Left to right: inputs (equilibrium tables, particle files, input decks), the code with the two
problem generators the track uses and the options it sets, the files a run writes, the
analysis that reads them (one directory per work package), and the figures and ledger of the
note. Every arrow is crossed by a registered run whose output directory carries the checksums
of its files; the note's scripts check them before they read a file. This diagram names files
and directories on purpose: it belongs to the ledger appendix (exception 1 of the writing
guide). No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_dataflow"
W, H = 41.6, 14.6
COLW = 7.6          # width of a column panel
GAP = 0.85          # gap between panels (arrows)
TOP, BOT = 13.9, 2.3


def col(ax, x, title, sub, items, fill):
    pf.panel(ax, x, BOT, COLW, TOP - BOT, radius=0.7)
    pf.text(ax, x + COLW / 2, TOP - 0.6, title, size=9.5, bold=True)
    pf.text(ax, x + COLW / 2, TOP - 1.2, sub, size=7.0, italic=True)
    y = TOP - 1.85
    centres = []
    for lab, h in items:
        pf.block(ax, x + 0.3, y - h, COLW - 0.6, h, "", fill=fill, radius=0.2)
        lines = lab.split("\n")
        for k, ln in enumerate(lines):
            yy = y - h / 2 + (len(lines) - 1) * 0.29 - k * 0.58
            pf.text(ax, x + COLW / 2, yy, ln, size=6.2 if k else 6.9, color=pf.WHITE,
                    bold=(k == 0), italic=(k > 0))
        centres.append(y - h / 2)
        y -= h + 0.28
    return centres


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.21)
    xs = [0.2 + k * (COLW + GAP) for k in range(5)]
    col(ax, xs[0], "Initial data", "generators in equilibria/, models/", [
        ("equilibrium tables\nradial metric of a model: <tag>.tab", 1.55),
        ("particle files\nsamples of f(E): <tag>.nrp, .json", 1.55),
        ("box samples\nJüttner gases from collide/analysis", 1.55),
        ("input decks\n<problem>, <particles>, rng_seed", 1.55),
        ("checks, Knudsen constant K\nequilibria/, models/, review runs", 1.55),
    ], pf.GREEN_DARK)
    col(ax, xs[1], "AthenaK", "one code base, branch or release", [
        ("nrpic_cf\ncluster from table and particles", 1.55),
        ("nrpic_geodesic\nperiodic box, fixed metric", 1.55),
        ("<particles> collisions\ncoll_sigma, coll_pmax", 1.55),
        ("coll_energy = particle (branch)\ncoll_budget, coll_dump_cycle", 1.55),
        ("<problem> metric_kind\nstatic_conformal (branch): T12", 1.55),
    ], pf.SLATE)
    col(ax, xs[2], "Run outputs", "scratch/C-sidm/<run id>/", [
        ("<base>.nrpic.hst\nlapse at the centre, sums, excision", 1.55),
        ("<base>.coll.hst\npairs tested, collisions, budgets", 1.55),
        ("snapshots\n<base>.part.*.bin: x, u, m, tags", 1.55),
        ("collision dumps\n<base>.coll_dump.*.bin: one step", 1.55),
        ("sha256sums.txt, manifest\nwritten when the run is finished", 1.55),
    ], pf.OLIVE)
    col(ax, xs[3], "Analysis", "registered analysis runs", [
        ("collide/analysis\nreaders, Maxwell-Jüttner references", 1.55),
        ("box_tests/scripts\nT0b-T12: replay, rate, budgets", 1.55),
        ("heat/scripts\nT6-T8 and the isobaric reference", 1.55),
        ("threshold_scan/analyze.py\ncluster histories, controls", 1.55),
        ("models/growth.py\ncollapse times, growth rate", 1.55),
    ], pf.RED)
    col(ax, xs[4], "Note", "note/scripts, one script per figure", [
        ("common.py\nrun table, sha256 check of inputs", 1.55),
        ("fig_*.py, schem_*.py\nfigures/*.pdf, *.png", 1.55),
        ("ledger.py\nledger.tex: each number, its run id", 1.55),
        ("run_all.py\nall of them in one registered run", 1.55),
        ("main.tex\nthe note; checker with --compile", 1.55),
    ], pf.PLUM)
    ymid = 0.5 * (TOP + BOT) - 0.3
    for k in range(4):
        pf.arrow(ax, (xs[k] + COLW + 0.08, ymid), (xs[k + 1] - 0.08, ymid), lw=1.3, head=9)
    # the checksum loop: outputs -> note scripts verify
    pf.arrow(ax, (xs[2] + COLW / 2, BOT - 0.05), (xs[4] + COLW / 2, BOT - 0.05), lw=1.0,
             head=8, dashed=True, rad=0.18, color=pf.GREY_LINE)
    pf.text(ax, 0.5 * (xs[2] + xs[4]) + COLW / 2, 0.55,
            "every file a figure or the ledger reads is checked against the checksum its run recorded",
            size=7.2, italic=True)
    pf.save(fig, os.path.join(out, STEM))
    print(f"{STEM}: drawn (no data read)")


if __name__ == "__main__":
    main()
