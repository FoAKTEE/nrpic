# stage/G2/verifier: fresh verifier of gate G2, Track C (checklist item C18)

Helper package of batch 33 (2026-11-27). Recomputes the G2 claims of Track C from the
registered card-run outputs with readers of its own, each tested first on a case with a known
answer. Processors only, one core per run, no card time.

## Contents

| Path | What |
|---|---|
| `VERIFIER.md` | the verdict per claim (sections 1-9) and, written after them, the comparison with the lead's verdicts (section 10) |
| `JOURNAL.md` | predictions before each recomputation and the outcomes, with commit times |
| `scripts/king_seq.py` | V1: King (b = 1) equilibrium sequence of arXiv:2009.08163, turning point, bracket members; tests T1 (Schwarzschild interior) and T2 (dh/dy = g + h) |
| `scripts/fates.py` | V2-V5: history reader with the restart rule (synthetic self-test), marker crossings, bands, constraint floors, deck diffs, horizon files, collision counts and energy budgets, sha256 of every file read; figure `fig_v2_fates` |
| `scripts/collrate.py` | V4.c: expected collision rate from particles and metric at t = 0 (equation 1 of collisions.md); tests of the Moller speed and of the pair sum |
| `scripts/extras.py` | X.1-X.7: block A controls and seeds, D2 control band, NS.1, D2eta1 guard stop, momentum and rest mass of the collision steps |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |

Registered runs (manifests in `tracks/C-sidm/runs/`, outputs in `scratch/C-sidm/<run_id>/`):
C-20261127-090849-dcfc1ae (V1, `fig_v1_king_sequence.png`), C-20261127-090942-697c4b3 (V2-V5,
`fig_v2_fates.png`, `fates.json`), C-20261127-090913-97ee992 (V4.c, `collrate.json`),
C-20261127-091307-f068e91 (X.1-X.7, `extras.json`). Superseded and kept:
C-20261127-090908-0053e80, C-20261127-091102-fd0c31b, C-20261127-091139-4b789b6.

## How to rerun

From `/data/haiyangw/nrpic/wt/C-sidm` (venv: `harness/bin/nrpic-env create --no-kokkos`):

    S="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/C-sidm/stage/G2/verifier --cores 1"
    V=tracks/C-sidm/stage/G2/verifier/scripts
    $S --purpose "V1" -- env OMP_NUM_THREADS=1 python3 $V/king_seq.py --out '$NRPIC_RUN_DIR'
    $S --purpose "V2-V5" -- env OMP_NUM_THREADS=1 python3 $V/fates.py --out '$NRPIC_RUN_DIR'
    $S --purpose "V4.c" -- env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 $V/collrate.py --out '$NRPIC_RUN_DIR' \
        D2f2s1=C-20261122-141414-399ad97 D2f1s1=C-20261122-144455-6e0992e D2f4s1=C-20261122-181011-60baef9 \
        M16=C-20261125-044843-2d048b6 D2eta1=C-20261126-034500-4b34b1c
    $S --purpose "X.1-X.7" -- env OMP_NUM_THREADS=1 python3 $V/extras.py --out '$NRPIC_RUN_DIR'

Each run takes seconds. The run ids read are written in the scripts (`fates.THRESH`,
`fates.COLL`, `extras.py`); the files read are checked against their runs' `sha256sums.txt`.

## Results in one paragraph

Every number claimed for G2 that I recomputed is reproduced to its printed digits: the
turning point y_max = 0.3340322 of the King b = 1 family, the marker crossings of all eleven
threshold runs and of the collisional series on three meshes, the bands of the stable members,
the 1/N fall of the integrated H^2, the collision rate (1.0008 for D2f2s1 over (0, t_c]) and the
collision energy budget (3e-16). Findings: BA.3 held as written (it is listed as failed); the
collision count test before t_c fails at about 3.5 sigma in two of six members (f = 4 and
shift_eta 1), so 1.0008 is the best member, not all; "controls collapse by particle noise" is
shown as a finite-N effect, not as a mechanism; the G2 result is a +-3 per cent bracket of one
family with a gauge leg that does not change the slicing, not the located and converged
threshold of two families that SCOPE.md asks for. Details: VERIFIER.md.

## Requests

- To the lead of C-sidm: (a) correct "BA.3 failed" (OPEN.md line 6, and wherever the failure
  list is repeated) or say what BA.3 meant; (b) state the collision count test per member and
  window (VERIFIER.md section 4) instead of the single 1.0008; (c) remove the stale note that
  A334s3c ends at 0.25 M; (d) mention that the M/4 seed-2 collisional run is broken after its
  first excision; (e) state in the note that the gauge leg changes the shift damping only.
- To the lead of C-sidm, runs that would turn "consistent" into "shown" (card time, for the
  lead to weigh): a second seed of the N = 1e4 control N4c, and N6c continued from its restart
  file to about 900 M (the log law of VERIFIER.md section 3 predicts a crossing near 830 M).
- To the orchestrator: whether a +-0.010 bracket in y0 of the King b = 1 family meets G2 as
  written in SCOPE.md:323-330 (two families, a located threshold) is a ruling, not a
  recomputation (VERIFIER.md section 5).
