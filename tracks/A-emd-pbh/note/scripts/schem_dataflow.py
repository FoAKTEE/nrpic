"""Schematic: data flow of Track A from initial data to the note's ledger (checklist C11 of G1).

Four lanes, one per kind of calculation (expanding ball, periodic box, Newtonian mode,
analytic criteria and scope), through the stages: initial data and inputs -> AthenaK
(release core-v0.3) -> raw outputs under scratch/A-emd-pbh/<run id>/ -> the track's
analysis scripts -> products -> the working note (note/scripts/ledger.py checks every
input against its run's sha256sums.txt and writes tables/ledger.tex). Below: registration
of every run and the independent path of the G1 verifier (stage/G1/verifier/).
Every file named here exists in the worktree, except the cost logs of runs/jeans/, which
live in the main checkout (checked by the G1 verifier on 2026-11-19);
no data are read. Style: harness/style/paperfig.py (copy in this directory).
Usage: python schem_dataflow.py [--out DIR]   (default: ../figures)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_dataflow"
W, H = 36.0, 19.6
CODE, ATHK, PROD = pf.GREEN_DARK, pf.SLATE, pf.PLUM
TS = 6.1            # text size inside blocks

# columns: x, width, title, subtitle
COLS = [
    (0.3, 7.0, "Initial data and inputs", "track scripts, repository tools"),
    (8.0, 4.4, "AthenaK", "release core-v0.3"),
    (13.1, 6.4, "Raw outputs", "scratch/A-emd-pbh/<run id>/"),
    (20.2, 6.2, "Analysis", "track scripts, own references"),
    (27.1, 3.9, "Products", "numbers, tables, figures"),
    (31.7, 4.0, "Working note", "tracks/A-emd-pbh/note/"),
]
LANES = [  # label, y of the lane's block row
    ("expanding ball", 15.0),
    ("periodic box", 12.4),
    ("Newtonian mode", 9.8),
    ("criteria, scope", 7.2),
]
BH = 1.75   # block height


def cell(ax, col, y, label, fill, tcolor=pf.WHITE, dashed_box=False):
    x, w = COLS[col][0], COLS[col][1]
    if dashed_box:
        pf.rbox(ax, x + 0.15, y, w - 0.3, BH, fill=pf.WHITE, edge=pf.GREY_LINE, lw=0.9, dashed=True, radius=0.2, z=3)
        pf.text(ax, x + w / 2, y + BH / 2, label, size=TS, color=pf.INK)
    else:
        pf.block(ax, x + 0.15, y, w - 0.3, BH, label, fill=fill, tcolor=tcolor, size=TS, radius=0.2)


def right(col):
    return COLS[col][0] + COLS[col][1] - 0.15


def left(col):
    return COLS[col][0] + 0.15


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.235)
    # column panels and titles
    for x, w, title, sub in COLS:
        pf.panel(ax, x, 6.85, w, 11.9, radius=0.6)
        pf.text(ax, x + w / 2, 18.3, title, size=8.2, bold=True)
        pf.text(ax, x + w / 2, 17.7, sub, size=6.3, italic=True)
    for lab, y in LANES:
        pf.text(ax, 0.45, y + BH + 0.25, lab, size=6.4, italic=True, ha="left", color=pf.ROSE)

    # lane 1: expanding ball
    y = LANES[0][1]
    cell(ax, 0, y, "expball/scripts/make_dataset.py:\nradial table .tab, lattice .nrp;\nruns_ball/prep.py: tracked particles", CODE)
    cell(ax, 1, y, "pgen nrpic_cf, tables\nruns_ball/sr1, sr2.athinput\n(Z4c + particles)", ATHK)
    cell(ax, 2, y, "ball.traj.bin, ball.trajmet.bin\nball.*.hst, horizon summary,\nfield dumps, log", None, dashed_box=True)
    cell(ax, 3, y, "runs_ball/compare.py; exact shells:\nexpball/expball/exact.py\n(cycloid per particle)", CODE)
    cell(ax, 4, y, "numbers.json,\nseries.npz, figures", PROD)
    # lane 2: periodic box
    y = LANES[1][1]
    cell(ax, 0, y, "periodic_threshold/scripts/\nmake_peak_ic.py ->\ncosmo/ic/make_field.py", CODE)
    cell(ax, 1, y, "pgen nrpic_cosmo\ninputs/peak_smr4.athinput", ATHK)
    cell(ax, 2, y, "*.hst, horizon output,\nline and field dumps", None, dashed_box=True)
    cell(ax, 3, y, "periodic_threshold/scripts/\nanalyse_scouting.py", CODE)
    cell(ax, 4, y, "DESIGN.md numbers,\nfigures", PROD)
    # lane 3: Newtonian mode
    y = LANES[2][1]
    cell(ax, 0, y, "newton/make_deformed_ball.py:\nball.nrp, ball.json\n(cycloid, ellipsoid references)", CODE)
    cell(ax, 1, y, "pusher = newton\nproblems/newton/\nisolated.athinput", ATHK)
    cell(ax, 2, y, "newton.newton.hst\n(moments, energy),\nparticle snapshots", None, dashed_box=True)
    cell(ax, 3, y, "newton/analyze_newton.py,\ngr_range.py\n(tophat.py, ellipsoid.py)", CODE)
    cell(ax, 4, y, "newton_*.csv,\nSCAN.md 7-8, figures", PROD)
    # lane 4: criteria and scope (no simulation)
    y = LANES[3][1]
    cell(ax, 0, y, "paper sources, kb-data/raw/arxiv\n(formula locators);\ncost logs of runs/jeans", None, dashed_box=True)
    cell(ax, 3, y, "criteria/emd_criteria.py,\npredict.py, check_criteria.py;\nscope/scope_calc.py", CODE)
    cell(ax, 4, y, "results.json,\nscan_summary.json,\nscope_numbers.json", PROD)

    # arrows along the lanes
    for k, (_, y) in enumerate(LANES):
        ym = y + BH / 2
        if k < 3:
            for c in range(3):
                pf.arrow(ax, (right(c), ym), (left(c + 1), ym), lw=1.0, head=7)
        else:
            pf.arrow(ax, (right(0), ym), (left(3), ym), lw=1.0, head=7, dashed=True)
            pf.text(ax, (right(0) + left(3)) / 2, ym + 0.32, "no simulation", size=6.0, italic=True)
        pf.arrow(ax, (right(3), ym), (left(4), ym), lw=1.0, head=7)

    # note column: a stack fed by every lane
    x, w = COLS[5][0] + 0.2, COLS[5][1] - 0.4
    pf.block(ax, x, 14.7, w, 2.4, "scripts/common.py:\nrun ids; every input\nchecked against its\nrun's sha256sums.txt", fill=CODE, size=TS, radius=0.2)
    pf.block(ax, x, 11.75, w, 2.2, "scripts/ledger.py,\nfig_*.py, run_all.py\n(one registered run)", fill=CODE, size=TS, radius=0.2)
    pf.block(ax, x, 9.25, w, 1.75, "tables/ledger.tex,\nparameters.tex, figures/", fill=PROD, size=TS, radius=0.2)
    pf.block(ax, x, 7.15, w, 1.4, "main.tex -> main.pdf", fill=PROD, size=TS, radius=0.2)
    for y0, y1 in ((14.7, 13.95), (11.75, 11.0), (9.25, 8.55)):
        pf.arrow(ax, (x + w / 2, y0), (x + w / 2, y1), lw=1.0, head=7)
    for k, (_, y) in enumerate(LANES):
        ym = y + BH / 2
        pf.arrow(ax, (right(4), ym), (x, min(max(ym, 12.0), 16.6)), lw=0.9, head=6, color=pf.GREEN_MID)

    # registration (left) and the verifier's independent path (right)
    pf.rbox(ax, 0.3, 2.0, 17.4, 4.1, fill=pf.GREY_FILL, edge="none", radius=0.35, z=1)
    pf.text(ax, 0.75, 5.45, "Registration of every run", size=7.0, bold=True, ha="left")
    for k, ln in enumerate(("harness/bin/nrpic-run submit (hand-written manifests of waves 1-2",
                            "count, decision 0016) -> tracks/A-emd-pbh/runs/<run id>/manifest.json:",
                            "command, cwd, commit, inputs with sha256, output directory,",
                            "wall time, card-hours; the outputs are listed in sha256sums.txt")):
        pf.text(ax, 0.75, 4.75 - 0.62 * k, ln, size=6.1, ha="left")
    for c in (0, 1, 2):
        xc = COLS[c][0] + COLS[c][1] / 2
        pf.line(ax, (xc, 6.85), (xc, 6.1), color=pf.GREY_LINE, lw=0.9)
    pf.rbox(ax, 18.3, 2.0, 17.4, 4.1, fill=pf.WHITE, edge=pf.RED, lw=1.0, dashed=True, radius=0.35, z=1)
    pf.text(ax, 18.75, 5.45, "Independent check (G1 item C18)", size=7.0, bold=True, ha="left", color=pf.RED)
    for k, ln in enumerate(("stage/G1/verifier/v_ledger.py, v_criteria.py, v_newton.py,",
                            "v_ball.py read the raw outputs, the data-set table and the",
                            "paper sources with their own code and references",
                            "-> stage/G1/VERIFIER.md (verdict per number)")):
        pf.text(ax, 18.75, 4.75 - 0.62 * k, ln, size=6.1, ha="left")
    xr = COLS[2][0] + COLS[2][1] - 0.8
    pf.arrow(ax, (xr, 6.85), (xr + 6.0, 6.1), color=pf.RED, lw=1.0, dashed=True, head=7)

    # legend
    pf.panel(ax, 0.3, 0.25, 35.4, 1.25, radius=0.4, fill=pf.CREAM_LEG)
    items = ((1.0, CODE, False, "code of the track or the repository (outside athenak/src)"),
             (12.6, ATHK, False, "AthenaK (core)"),
             (17.6, pf.WHITE, True, "data files"),
             (21.6, PROD, False, "products read by the note"),
             (28.3, None, None, "verifier path"))
    for x0, col, dashed, lab in items:
        if col is None:
            pf.arrow(ax, (x0, 0.875), (x0 + 1.3, 0.875), color=pf.RED, lw=1.0, dashed=True, head=7)
        elif dashed:
            pf.rbox(ax, x0, 0.6, 1.3, 0.55, fill=pf.WHITE, edge=pf.GREY_LINE, lw=0.9, dashed=True, radius=0.12, z=3)
        else:
            pf.rbox(ax, x0, 0.6, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.65, 0.875, lab, size=6.4, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
