# verify_bh: independent verifier of BH-1R (first horizon) and BH-1 (no horizon at uniform M/8)

Helper package of A-emd-pbh, wave 3, gate G2, card cap 0 (processors only). Decision 0009:
the claims C1-C5 of the plan (tracks/A-emd-pbh/PLAN-wave3.md) were checked from the
artefacts with my own readers and my own exact solution before the producer's analysis was
read. Verdicts: VERIFIER.md section 1; method and uncertainties section 2; what G2 still
lacks section 3; comparison with runs_ball entries 11-12 section 4.

Result in one paragraph: the exact solution of data set 3 (C1) and the code's initial slice
(C2) are confirmed to the table's precision. BH-1R finds a persistent horizon from
t = 10.875 (C3); its irreducible mass is 2.0e-2 above the exact mass of the same slice at
the first detection (claim of 3e-3: WRONG), within 3e-3 from t = 11.625 and within 6e-4 from
11.75 to 15.875; median over the first 4 M -4.6e-4 (confirmed). BH-1 at M/4-M/8 has no
finder result although trapped spheres exist on its lines from t = 11.0-12.0 (C4, the first
time depends by up to 0.75 M on the line's stencil at M/8); M/8 turns non-finite at 15.03,
not near 15.5. The core-shell error bounds of C5 fail for the tracked particles within
0.05 M (BH-1R) or 0.2 M (M/8) of the core edge and hold inside. All numbers agree with the
producer's own analysis where the estimators coincide (section 4).

## Contents

| Path | What |
|---|---|
| JOURNAL.md | predictions (entries 1, 3) and outcomes (entries 3, 4, 5) |
| VERIFIER.md | verdicts, method, G2 gaps, comparison |
| scripts/vbio.py | readers: format-2 table, .nrp, snapshots, traj/trajmet (record length from the file sizes), histories, horizon summary, table outputs |
| scripts/ltb.py | Lemaitre-Tolman-Bondi dust from the table alone (shell events, R(tau) per shell) |
| scripts/partdata.py | tracked particles as (time x tag) arrays, labels, areal radius from gamma at the particle |
| scripts/vbpaths.py | artefact paths (read-only inputs); output directory from NRPIC_RUN_DIR |
| scripts/c1_exact.py | C1 (run A-20261121-125359-22858c4) |
| scripts/c2_initial.py | C2 (A-20261121-125427-35117a2) |
| scripts/c3_horizon.py | C3 (A-20261121-125512-6df0ee3) |
| scripts/c3b_firstdetect.py | C3 follow-up: finder area, line mass at the finder radius (A-20261121-125921-9c96b3f) |
| scripts/c4_lines.py | C4 (A-20261121-125449-689b5ec) |
| scripts/c4b_stencil.py | C4 follow-up: four readings of the line (A-20261121-130002-56a4c88) |
| scripts/c5_shells.py | C5 (A-20261121-125646-166ae06) |
| scripts/c5b_edge.py | C5 follow-up: error against distance from the core edge (A-20261121-125939-80054f8) |
| scripts/figstyle.py | copy of harness/style/figstyle.py |
| figs/ | the eight figures of the runs above (PNG), copied from the run directories |

Run outputs (json, png, pdf, run.log) are in `scratch/A-emd-pbh/<run id>/`; manifests in
`tracks/A-emd-pbh/runs/<run id>/manifest.json`.

## How to rerun

From the worktree root, with the worktree's `.venv` (numpy, scipy, matplotlib):

```
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/A-emd-pbh/verify_bh \
  --launcher local --cores 1 --purpose '...' \
  -- bash -c 'OMP_NUM_THREADS=1 python tracks/A-emd-pbh/verify_bh/scripts/c1_exact.py'
```

and likewise c2_initial.py, c3_horizon.py bh_smr, c3b_firstdetect.py, c4_lines.py,
c4b_stencil.py, c5_shells.py, c5b_edge.py (each about a minute; c3, c5 read the trajectories
of all runs, c3 the 1.3e6-particle snapshots). Without NRPIC_RUN_DIR the scripts write to
`scratch/A-emd-pbh/tmp/verify_bh/dev/` (not evidence).

## Requests

- To the lead of A-emd-pbh: (1) decide whether the C3 clock item counts as refuted (the
  producer's -0.046 M at r_h, my -0.024) - VERIFIER.md section 4 recommends the producer's
  stricter verdict; (2) the open question whether the 2e-2 first-detection excess is in the
  slice or in the finder: the line at t = 11.25 (+9.9e-3 at the finder's radius) disagrees
  with the finder (-3.4e-3); a line or field output at the finder times 10.875-11.5 with the
  finder's own expansion evaluated on the line would decide it; (3) G2 tables should state
  the particle selection of shell errors or report the core-edge band separately (C5 holds
  only away from the edge).
- To core (through the lead): BH-1R's history column int_E at t = 0 is 7.9e-4 below sum_m
  (1.145039 against 1.145939), while the three uniform runs agree to 1e-15 (run
  A-20261121-125427-35117a2): is the deposit or the mesh integral across the two levels of a
  statically refined mesh short at t = 0?
