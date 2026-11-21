# periodic_diag: why the periodic set-up of periodic_threshold fails (Track A, batch 6)

Helper package of A-emd-pbh. Diagnosis on processors, without source changes, of the
constraint jump at t = 2.5 and the guard stops of card job 4799 (run
A-20261121-131600-02b5d41, deck `periodic_threshold/inputs/peak_leak.athinput`, release
core-v0.5): P0L stopped at t = 4.8, S1L at t = 15.1, and in both the norm of H jumped by
about 1e4 at t = 2.5. Everything here is analysis of AthenaK output, a reference stability
computation, decks and drivers; no source change and no simulation code (decision 0010).
Predictions and outcomes, also the refuted ones: `JOURNAL.md`.

## Verdict

(written at the end of the package; see the section at the bottom of JOURNAL.md)

## Files

| File | Content |
|---|---|
| `JOURNAL.md` | candidates, predictions before each test, outcomes |
| `inputs/diag_uniform.athinput` | the card deck's physics on the 64^3 root mesh without the static levels |
| `scripts/run_uniform.sh` | uniform-mesh cases U0..U7 (relaxed lapse) and G0..G4 (lapse frozen) |
| `scripts/run_uniform2.sh` | the seeded frozen-lapse cases G5 (cfl 1.0) and G6 (cfl 0.6) |
| `scripts/run_refined.sh` | the card deck itself on processors: R0 (as job 4799), R1 (cfl 0.5), R2 (zero shift) |
| `scripts/vonneumann.py` | Test B: RK4 amplification of the discrete Gamma-driver, 1+log/relaxation and light subsystems with the code's stencils |
| `scripts/card_onset.py` | Test A: the outputs of job 4799 read again (step against level 4, onset, grid-scale part of the line outputs, amplification of Test B along the card's own steps) |
| `scripts/analyse_runs.py` | histories, onset and grid-scale part of the processor runs |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |
| `figures/` | copies of the figures cited here (made in the run directories) |

## How to rerun

From the worktree root, every run through `harness/bin/nrpic-run` (package committed first):

```
P=tracks/A-emd-pbh/periodic_diag/scripts
R="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/A-emd-pbh/periodic_diag --launcher local"
$R --purpose "Test B" --cores 1 -- bash -c 'python -I '$P'/vonneumann.py --out "$NRPIC_RUN_DIR"'
$R --purpose "U0" --cores 6 -- bash -c ''$P'/run_uniform.sh "$NRPIC_RUN_DIR" 6 U0'
$R --purpose "G0-G2" --cores 2 -- bash -c ''$P'/run_uniform.sh "$NRPIC_RUN_DIR" 2 G0 G1 G2'
$R --purpose "G5-G6" --cores 2 -- bash -c ''$P'/run_uniform2.sh "$NRPIC_RUN_DIR" 2 G5 G6'
$R --purpose "R2" --cores 4 -- bash -c ''$P'/run_refined.sh "$NRPIC_RUN_DIR" 4 R2'
$R --purpose "Test A" --cores 1 -- bash -c 'python -I '$P'/card_onset.py --job /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-131600-02b5d41 --vn <Test B run dir> --out "$NRPIC_RUN_DIR"'
$R --purpose "analysis" --cores 1 -- bash -c 'python -I '$P'/analyse_runs.py --run G0=<dir>/G0 --run G1=<dir>/G1 ... --vn <Test B run dir> --out "$NRPIC_RUN_DIR"'
```

Costs on the threaded processor build of release core-v0.6
(`scratch/core/exe/core_nrpic_v06/athena_cpu_omp`): uniform 64^3 with the 262,144 particles
of P0L about 3.3 s per cycle on 6 threads, 9.6 s on 2 (60-120 cycles per case); the card
deck (288 blocks of 16^3) about 23 s per cycle on 4 threads.

## Requests

(at the end)
