# khsr_note: KHSR with newton3, P1 to its end, and the note's G1 close-out

Helper package of F-hills (wave 3, batch 6, 2026-11-21; no card time). Predictions and
outcomes: `JOURNAL.md` (entries K, P, N). Writes only this directory and `../runs/`.

## Results

| item | result | runs |
|---|---|---|
| (1) KHSR (arXiv:1201.4794, Sec. 6.2 / Fig. 4) | Reproduced with newton3's full three-body driver (M/m = 1e6, m1/m2 = 3, coplanar, r_a/r_t = 500, 200, 130, 100 and the parabola): the closed form E_bar = -2.667 at r_a/r_t = 100 (printed -2.7, ms.tex:746) and the start radii 12.22 / 17.42 r_t (printed 12.2 / 17.4, ms.tex:624-626); no preference for the parabola; the ejection probability falls between r_a/r_t = 500 and 100 (prograde, to 0.57 of P_dis at 100) and the secondary is preferred (primary/secondary 0.08-0.15 at 100), as the text says (ms.tex:762-769); KHSR's parabolic approximation agrees with the direct integration within 0.012 in probability except at D = 2, r_a/r_t = 100 (0 against 0.037), where the elliptic orbit's energy change is 3 percent smaller | scan F-20261121-212757-77cdc15; checks and figure F-20261121-213405-6596be1 (first scan F-20261121-212049-d91381f and its checks F-20261121-212703-276a88b kept failed integrations: superseded) |
| (2) P1 after the merger, t = 112-280 M | Remnant (0.268) passes M at 6.99 M (coordinate) at t = 154.6 M, swings round by about 3/4 turn and recedes (24.3 M at 280 M); no common horizon; remnant mass -0.42 percent over 60-280 M, spin 0.660 (0.677 during the approach); "recoil" 0.022 c in coordinate speed (a gauge readjustment: zero by symmetry); heavy hole +0.32 percent, spin estimate up to 3e-3 during the passage then back; H norm within 4.7e-5 - 8.8e-5 (no growth); E_rad by 280 M 2.0-3.0e-3 M at the four spheres, mostly from the passage (quadrupole estimate 1.4e-3 M); tree 736-1870, 12.58 card-hours | F-20261121-212240-c43f35f (package p1's readers), F-20261121-212441-1911b7d (`scripts/p1_280.py`) |
| (3) Note close-out | Working copy `note/` (v2, 24 pages): new Secs. IV B (elliptic orbits, Fig. 4), V E (P1 to its end, Fig. 13), V F (the binary alone, binary_conv, R19, Fig. 14); Kerr paragraph; junk numbers; 1PN reviewed; released parts as of core-v0.6 and the architecture schematic; the lead's corrections 1-7 (note/JOURNAL.md 2026-11-21); ledger tables I (+Kerr rows), III (new, elliptic orbits), VII (new); compiled, checker clean except accepted items, pages read | figure run F-20261121-214141-256f945 (outputs in `note/figures`, `note/tables`; first figure run F-20261121-213906-f4b2b30 superseded) |

Not done: a second agent's check of these results; the note's README/JOURNAL (they stay in
`../note/`); the reviewer step of the paper-writing procedure.

## Contents

| path | what |
|---|---|
| `scripts/khsr_ecc.py` | the KHSR scan: newton3 three-body driver on elliptic orbits, restricted parabolic lines, K1/K2 closed forms |
| `scripts/fig_khsr.py` | checks K1-K3 (`khsr_checks.json`) and the package figure `fig_khsr_ecc` |
| `scripts/p1_280.py` | P1 after the merger: remnant orbit, recoil, horizons, constraint norms, radiated energy, figure `fig_p1_280` |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |
| `results/` | `khsr_ecc.json`, `khsr_checks.json`, `p1_280.json`, `p1_checks_280.json`, `p1_ledger_280.json` (copied from the run directories above) |
| `figures/` | `fig_khsr_ecc`, `fig_p1_280`, p1's `fig_tracks_plane` and `fig_horizons` at 280 M (all read) |
| `note/` | the note, v2: `main.tex`, `main.pdf`, `references.bib`, `scripts/` (unchanged ones plus `fig_elliptic.py`, `fig_binary.py`, `fig_p1_end.py`; changed `common.py`, `ledger.py`, `run_all.py`, `schem_architecture.py`), `figures/`, `tables/` |

## How to rerun (from `/data/haiyangw/nrpic/wt/F-hills`)

    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/F-hills/khsr_note --cores 4 \
        --purpose "..." -- .venv/bin/python tracks/F-hills/khsr_note/scripts/khsr_ecc.py --workers 4      # 6 min
    harness/bin/nrpic-run submit ... --cores 1 -- .venv/bin/python tracks/F-hills/khsr_note/scripts/fig_khsr.py \
        /data/haiyangw/nrpic/scratch/F-hills/<scan run> '--out=$NRPIC_RUN_DIR'
    harness/bin/nrpic-run submit ... --cores 1 --parent F-20261119-150017-b45ec5f -- bash tracks/F-hills/p1/scripts/run_all.sh
    harness/bin/nrpic-run submit ... --cores 1 -- .venv/bin/python tracks/F-hills/khsr_note/scripts/p1_280.py
    harness/bin/nrpic-run submit ... --cores 1 -- .venv/bin/python tracks/F-hills/khsr_note/note/scripts/run_all.py  # 1 min
    # copy <run dir>/figures/* to note/figures/, <run dir>/tables/* to note/tables/, put the run id in appendix B, then
    cd tracks/F-hills/khsr_note/note && latexmk -pdf main.tex
    python3 ~/.claude/skills/synced/*/paper-writing/scripts/check_manuscript.py --main main.tex --forbid \
        'HRNA|newton3|geodesic_binary|three_punctures|nr_first|hrna\.py|nrpic_cf|puncture_setup|athinput|nrpic-run|core-v0|F-pre|lead_checks|anta|A100|KHSR|binary_conv|khsr_note'

## Requests

- **F-hills lead** (the note is package `note/`'s directory, which this package may not write):
  carry the working copy over with
  `cp -r tracks/F-hills/khsr_note/note/{main.tex,main.pdf,references.bib,scripts,figures,tables} tracks/F-hills/note/`
  (`note/README.md` and `note/JOURNAL.md` stay as they are);
  `common.py` finds `tracks/F-hills` from either directory, so the scripts run unchanged; then
  delete the copy here (`git rm -r tracks/F-hills/khsr_note/note`) and add a line to
  `note/README.md` naming run F-20261121-214141-256f945 as the figure run of v2. Also:
  stage/G1/STATUS.md T1 (KHSR now reproduced, runs above), RISKS R14 (retire), and the P1
  outcome rows (G1 T4: P1 complete to 280 M but no Hills passage).
- **F-hills lead**: the KHSR figure `note/figures/fig_elliptic.png` repeats the line legend in the
  right panel (cosmetic; fix in `fig_elliptic.py` when the note is next rerun).
- **orch / reviewer**: a second agent's check of K3 (give it `scripts/khsr_ecc.py`, the scan run
  and KHSR ms.tex:737-778, not this README) and of the P1 numbers of `results/p1_280.json`.
