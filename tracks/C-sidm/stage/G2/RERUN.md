# C-sidm G2: rerun list

How to redo every number of the G2 package from the registered runs (state 2026-11-27, batch 32).
Every run has its manifest under `tracks/C-sidm/runs/<run_id>/manifest.json` (command, commit,
inputs with sha256, output directory `scratch/C-sidm/<run_id>/` with `sha256sums.txt`). Every
collapse time below is the alpha_min = 0.3 lapse marker; no run carried the horizon finder
(C-20261125-160207-05b6db1).

## 1. Card runs (release core-v0.6 card build, cfl_number 0.25, no dt_gauge; ruling 0039 item 3)

Decks: `tracks/C-sidm/longruns/scripts/make_decks.py` (block A, D2), `make_decks_b11.py`,
`make_decks_b17.py` (N-series, bracket at N = 1e6), `make_decks_b20.py` (M/16 and shift_eta 1.0
legs); each run is the chain `tracks/C-sidm/longruns/seq/qitem.sh <label>` entered through the
shared queue (`harness/bin/nrpic-queue add --label <label> --priority 2 --cmd
'tracks/C-sidm/longruns/seq/qitem.sh <label>'`), closed with `harness/bin/nrpic-run finish <run_id>`.

| Label | Run id | Model | N | Mesh | Gauge | Fate (lapse marker) |
|---|---|---|---|---|---|---|
| N4c | C-20261125-132112-edf3fbc | control y0 0.334032 | 1e4 | M/8 | eta 2 | t_c 295.78 M |
| A334s1c | C-20261121-214601-40dc927 | control y0 0.334032 | 1e5 | M/8 | eta 2 | t_c 534.81 M |
| N6c | C-20261124-221122-928c9eb | control y0 0.334032 | 1e6 | M/8 | eta 2 | holds 600 M |
| A344s1i | C-20261122-220118-ab099ac | y0 0.344 kicked in | 1e5 | M/8 | eta 2 | t_c 229.79 M |
| A324s1i | C-20261123-221955-a773578 | y0 0.324 kicked in | 1e5 | M/8 | eta 2 | holds 600 M |
| N6b344 | C-20261125-224959-d1d4494 | y0 0.344 kicked in | 1e6 | M/8 | eta 2 | t_c 252.31 M |
| N6b324 | C-20261126-020831-fabf2d7 | y0 0.324 kicked in | 1e6 | M/8 | eta 2 | holds 600 M |
| A16b344 | C-20261126-043714-8ea1c35 | y0 0.344 kicked in | 1e6 | M/16 | eta 2 | t_c 217.97 M |
| A16b324 | C-20261126-121449-1d37e77 | y0 0.324 kicked in | 1e6 | M/16 | eta 2 | holds 600 M |
| N6b344e1 | C-20261126-050124-00e10ae | y0 0.344 kicked in | 1e6 | M/8 | eta 1 | t_c 252.41 M |
| N6b324e1 | C-20261126-130519-1a79a66 | y0 0.324 kicked in | 1e6 | M/8 | eta 1 | holds 600 M |
| D2ctl, D2f1s1, D2f2s1, D2f4s1, D2f2s2 | C-20261122-103854-4670b59, -144455-6e0992e, -141414-399ad97, -181011-60baef9, C-20261124-035054-c06503f | CC2, Kn_c 10 (control without) | 1e5 | M/8 | eta 2 | collisional t_c 163.41-165.65 M |
| M16 | C-20261125-044843-2d048b6 | CC2, Kn_c 10 | 1e5 | M/16 | eta 2 | t_c 158.42 M |
| D2eta1 | C-20261126-034500-4b34b1c (failed on record: guard stop after collapse) | CC2, Kn_c 10 | 1e5 | M/8 | eta 1 | t_c 164.01 M |

## 2. Registered analyses (processors, one core each, seconds to minutes)

    S="harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 1"
    N=tracks/C-sidm/longruns/scripts/nseries.py
    # N-series of the control (NS.1-NS.3): C-20261126-120656-f5c62bb
    $S -- env OMP_NUM_THREADS=1 python3 $N --out '$NRPIC_RUN_DIR' N1e4=C-20261125-132112-edf3fbc N1e5=C-20261121-214601-40dc927 N1e6=C-20261124-221122-928c9eb
    # bracket at N = 1e6 and 1e5 on M/8 (B17.5, B17.6): C-20261126-121836-c7a76c1
    $S -- env OMP_NUM_THREADS=1 python3 $N --out '$NRPIC_RUN_DIR' --band 0.03 --control N1e6_c N1e6_c=C-20261124-221122-928c9eb N1e6_b344kin=C-20261125-224959-d1d4494 N1e6_b324kin=C-20261126-020831-fabf2d7 N1e5_b344kin=C-20261122-220118-ab099ac N1e5_b324kin=C-20261123-221955-a773578
    # mesh leg, unstable member (B20.2): C-20261126-124143-b485eac
    $S -- env OMP_NUM_THREADS=1 python3 $N --out '$NRPIC_RUN_DIR' --band 0.03 --control N1e6_b344kin N1e6_c=C-20261124-221122-928c9eb N1e6_b344kin=C-20261125-224959-d1d4494 N1e6_b344kin_M16=C-20261126-043714-8ea1c35
    # gauge leg, unstable member (B20.3 first half): C-20261126-123219-f734997 (same form, N1e6_b344kin_eta1=C-20261126-050124-00e10ae)
    # mesh leg, stable member (B20.1): C-20261127-084538-8e98060
    $S -- env OMP_NUM_THREADS=1 python3 $N --out '$NRPIC_RUN_DIR' --band 0.03 --control N1e6_b324kin N1e6_c=C-20261124-221122-928c9eb N1e6_b324kin=C-20261126-020831-fabf2d7 N1e6_b324kin_M16=C-20261126-121449-1d37e77
    # gauge leg, stable member (B20.3 second half): C-20261127-084417-79c0e4d
    $S -- env OMP_NUM_THREADS=1 python3 $N --out '$NRPIC_RUN_DIR' --band 0.03 --control N1e6_b324kin N1e6_c=C-20261124-221122-928c9eb N1e6_b324kin=C-20261126-020831-fabf2d7 N1e6_b324kin_eta1=C-20261126-130519-1a79a66
    # collisional series on three meshes and two gauges, budgets (D2, M16, B17.4): C-20261126-121702-b6b1eda
    #   tracks/C-sidm/longruns/scripts/d2_analysis.py (command in its manifest)
    # block A (15 runs, N = 1e5): C-20261125-160056-a5b7282 (blockA_delta.py, command in its manifest)
    # horizon status of every collapse time: C-20261125-160207-05b6db1 (horizon_audit.py)

## 3. The note (figures, schematics, ledger)

    harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/C-sidm/note --cores 2 \
        --purpose "note: figures, schematics, ledger" -- .venv/bin/python tracks/C-sidm/note/scripts/run_all.py
    # last run: C-20261127-084828-b6ca5ce (copy figures/ and tables/ into tracks/C-sidm/note/), then
    cd tracks/C-sidm/note && python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile --forbid '<as in note/README.md>'

`fig_g2_threshold.py` reads cc.nrpic.hst of the eleven threshold runs above and prints each
marker crossing (it agrees with nseries.py to all digits); `fig_g2_mosaic.py` reads particle
snapshots 0 and 22 of A16b344 and A16b324; both check every input against the sha256 its run
recorded.

## 4. Costs

The eleven threshold runs and the D2 series: see the card-hours in each manifest (nrpic-run
finish sums sacct ElapsedRaw over the chain). This batch closed A16b324 (6.3844) and N6b324e1
(2.6175). Analyses: under a minute each on one core.
