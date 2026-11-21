"""Schematic: data flow of the slow-roll reproduction at gate G1, from the mode tables to
the ledger of this note.

Stages and their sources (states coloured as in schem_architecture.py):
- mode tables: core's case generator make_case.py (branch core/scalar-2, released in
  core-v0.4 on 2026-11-21; coord/INTERFACES/scalar_field_2.md section 2;
  ladder/inputs/modes_n*.txt), the counter-based Gaussian
  numbers of the release (utils/rng.hpp), the track's Mukhanov-Sasaki reference
  (spec/ref; the ladder checks the mode files against it, run E-20261115-174008-7aee5ff);
- AthenaK run: initial slice at N* (id = stochastic), stochastic sources at the stage
  times, Z4c with the scalar field; outputs the record <basename>.sf.con.hst and the
  NRSFDMP2 dumps (ladder/inputs/sr_base.athinput); the G1 runs used the tested-branch
  executable of core/scalar-2 a58e95b (decision 0013), which release core-v0.4 contains;
- analysis: ladder/scripts/ladder_analysis.py (extract: R^NR per mode, record, A1; pair:
  odd and even parts; judge: A2, A3, spectrum), verdicts.py, floor_analysis.py,
  a6_analysis.py, with the amplitudes recomputed by the independent twin
  noise/ref/philox_ref.py (ladder/README.md, JOURNAL entry 1);
- ledger and note: ladder/results/{final,floor,a6} (committed copies, checked against the
  run checksums by note/scripts/common.py), one script per figure, ledger.py, main.tex.
No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_dataflow"
REL, BRANCH, TRACK, NOTE = pf.GREEN_DARK, pf.SLATE, pf.OLIVE, pf.PLUM
W, H = 30.0, 14.2
TOP, BOT = 13.4, 1.8
R1, R2, R3, R4, R5 = 9.6, 7.8, 6.0, 4.2, 2.2      # bottoms of the rows of blocks
BH = 1.2                                         # block height


def panel(ax, x, w, title, sub, bottom=BOT):
    pf.panel(ax, x, bottom, w, TOP - bottom, radius=0.8)
    pf.text(ax, x + w / 2, TOP - 0.55, title, size=9.0, bold=True)
    pf.text(ax, x + w / 2, TOP - 1.15, sub, size=7.0, italic=True)


def box(ax, x, y, w, label, fill):
    pf.block(ax, x, y, w, BH, label, fill=fill, size=6.6, radius=0.2)


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    # 1. mode tables
    panel(ax, 0.2, 5.8, "Mode tables", "before the run")
    box(ax, 0.6, R1, 5.0, r"Gaussian numbers $\alpha_k$" "\nkeyed by wave vector", REL)
    box(ax, 0.6, R2, 5.0, "case generator: background,\n" r"$\mathcal{R}_k$, $\dot{\mathcal{R}}_k$ at $N_*$", BRANCH)
    box(ax, 0.6, R5, 5.0, "track reference: full\nMukhanov-Sasaki modes", TRACK)
    pf.arrow(ax, (3.1, R5 + BH), (3.1, R2 - 0.05), lw=0.9, head=6, dashed=True, color=pf.GREY_LINE)
    pf.text(ax, 3.3, 5.2, "checks the\ntables", size=6.2, ha="left", color=pf.ROSE)
    # 2. AthenaK run
    panel(ax, 6.6, 7.8, "AthenaK run", r"slow roll, $32^3$ to $256^3$", bottom=5.2)
    box(ax, 7.0, R1, 3.6, r"initial slice at $N_*$", BRANCH)
    box(ax, 7.0, R2, 3.6, "stochastic sources\nat the stage times", REL)
    box(ax, 7.0, R3, 3.6, "Z4c and scalar field,\nfour stages per step", REL)
    box(ax, 10.9, R1, 3.1, "dumps: fields,\nmetric, constraints", BRANCH)
    box(ax, 10.9, R3, 3.1, "record: box means,\nconstraint ratios", BRANCH)
    pf.arrow(ax, (5.6, R1 + BH / 2), (7.0, R1 + BH / 2), lw=1.1, head=7)
    pf.arrow(ax, (5.6, R2 + BH / 2), (7.0, R2 + BH / 2), lw=1.1, head=7)
    pf.arrow(ax, (8.8, R1), (8.8, R2 + BH), lw=1.1, head=7)
    pf.arrow(ax, (8.8, R2), (8.8, R3 + BH), lw=1.1, head=7)
    pf.arrow(ax, (10.6, R3 + BH / 2), (10.9, R3 + BH / 2), lw=1.1, head=6)
    pf.arrow(ax, (10.6, R3 + BH - 0.15), (12.45, R1), lw=1.1, head=7)
    # lane under the run: the reference goes straight to the analysis
    pf.arrow(ax, (5.6, R5 + BH / 2), (19.6, R5 + BH / 2), lw=1.1, head=7, dashed=True)
    pf.text(ax, 10.5, R5 + BH / 2 + 0.45, r"reference modes; the same $\alpha_k$ from an independent twin",
            size=6.4, color=pf.ROSE)
    # 3. analysis
    panel(ax, 15.0, 8.8, "Analysis", "registered runs of the track")
    box(ax, 15.4, R1, 3.9, "odd and even parts\n" r"of $\mathcal{H}$, $\mathcal{M}$ ($\lambda=\pm1$, $\pm\frac{1}{2}$)", TRACK)
    box(ax, 15.4, R2, 3.9, "A4, A5: halving,\norder, floor", TRACK)
    box(ax, 15.4, R3, 3.9, "negative control:\n" r"$\Pi$ kick flipped", TRACK)
    box(ax, 15.4, R4, 3.9, "A1 from the record;\nA6: three time steps", TRACK)
    box(ax, 19.6, R1, 3.8, r"$\mathcal{R}^\mathrm{NR}_n$ per mode" "\n" r"from $\chi$, $\tilde\gamma_{ij}$, $\phi$", TRACK)
    box(ax, 19.6, R2, 3.8, r"A2: $D_n$ against" "\n" r"$W_k\mathcal{R}_k\alpha_k$", TRACK)
    box(ax, 19.6, R3, 3.8, "A3: freezing ratio\nand drift per mode", TRACK)
    box(ax, 19.6, R5, 3.8, "linear reference\n" r"with the same $\alpha_k$", TRACK)
    pf.arrow(ax, (14.0, R1 + BH / 2), (15.4, R1 + BH / 2), lw=1.1, head=7)
    pf.arrow(ax, (12.45, R1 + BH), (21.5, R1 + BH), lw=1.1, head=7, rad=-0.15)
    pf.arrow(ax, (14.0, R3 + 0.2), (15.4, R4 + BH / 2), lw=1.1, head=7)
    pf.arrow(ax, (14.0, R3 + BH / 2), (15.4, R3 + BH / 2), lw=1.1, head=7)
    pf.arrow(ax, (17.35, R1), (17.35, R2 + BH), lw=1.1, head=7)
    pf.arrow(ax, (21.5, R1), (21.5, R2 + BH), lw=1.1, head=7)
    pf.arrow(ax, (21.5, R2), (21.5, R3 + BH), lw=1.1, head=7)
    pf.arrow(ax, (21.5, R5 + BH), (21.5, R3), lw=1.1, head=7)
    # 4. ledger and note
    panel(ax, 24.4, 5.4, "Ledger and note", "this working note")
    box(ax, 24.8, R1, 4.6, "verdicts and results,\ncommitted with checksums", TRACK)
    box(ax, 24.8, R2, 4.6, "one script per figure", NOTE)
    box(ax, 24.8, R3, 4.6, "ledger: value and run\nof every number", NOTE)
    box(ax, 24.8, R4, 4.6, "regeneration as one\nregistered run", NOTE)
    box(ax, 24.8, R5, 4.6, "working note", NOTE)
    pf.arrow(ax, (23.8, R1 + BH / 2), (24.8, R1 + BH / 2), lw=1.1, head=7)
    for y0, y1 in ((R1, R2 + BH), (R2, R3 + BH), (R3, R4 + BH), (R4, R5 + BH)):
        pf.arrow(ax, (27.1, y0), (27.1, y1), lw=1.1, head=7)
    # legend
    pf.panel(ax, 6.6, 0.2, 22.8, 1.0, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((7.0, REL, "release"), (11.2, BRANCH, "tested branch, in core-v0.4"),
                         (18.8, TRACK, "track analysis"), (24.0, NOTE, "this note")):
        pf.rbox(ax, x0, 0.43, 1.2, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.5, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
