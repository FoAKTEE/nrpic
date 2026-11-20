# C-sidm/drift: origin of the outward excursion of the collisionless King controls

Helper package of owner C-sidm, wave 3, round 1 (`../PLAN-wave3.md`, package 6). Question
(`../RISKS.md` item 3): the two collisionless King controls of wave 2 (cc1_kninf, y0 =
0.334032, run C-20261115-171058-c26cfad; cc2_kninf, y0 = 0.314, run
C-20261115-171059-4b70228; static mesh with M/4 cells, N = 1e5, 300 M) move their central
lapse up by 0.033 and 0.018 and back. Is this the mesh, particle noise, or a physical mode
excited by the initial data? The answer decides the mesh of block A of
`../threshold_scan/SCAN.md` (about 9.5 card-hours).

Predictions and outcomes: `JOURNAL.md` (entries 1-). Labels: [VERIFIED] computed in the
registered run named next to it; [JUDGEMENT]; [BACKGROUND]; [TO VERIFY].

## Contents

| Path | What it is |
|---|---|
| `scripts/controls.py` | Test D1: histories, snapshots and trajectories of a control (or of a run joined with its continuation): alpha_c excursion with two fit forms, coordinate and areal radii of the mass shells, mean Lorentz factor, H-norm2, Killing-energy sum, ripple periodogram; with `--pulsation` the lowest radial-pulsation eigenvalue of the King family (tmb b = 1, three adiabatic indices and a scaled proxy) as periods in M |
| `scripts/compare.py` | Tests M8 and A: several series side by side (M/4 against M/8, 0-1000 M), ratios of amplitudes and periods, extrema of the 40 M mean, H-norm2 floors |
| `scripts/make_decks.py` | Writes `inputs/`: the M/8 decks, the N = 1e4 deck, one batch list per card job |
| `inputs/cc{1,2}_kninf_M8.athinput` | (iii), (i): the wave-2 control decks with a level-7 region (M/8 cells) inside \|x\|_inf < 3.9 M; output cadence in time unchanged; restart files every 100 M |
| `inputs/cc2_kninf_N1e4.athinput` | (v), optional: the cc2 control deck with the N = 1e4 file of wave 1 (run C-sidm-20261115-120610-b4592be) |
| `inputs/job_{i,ii,iii,iv,v}.list` | one run per card job; (ii), (iv) restart the wave-2 runs from `rst/cc.00001.rst` (t = 300 M) to `time/tlim=1000`; every line ends with `-t 00:52:00` |
| `figs/` | copies of the figures of the registered runs (all looked at) |

## How to rerun

From the worktree root, Python environment of the worktree (`harness/bin/nrpic-env create
--no-kokkos` once):

    R=/data/haiyangw/nrpic/scratch/C-sidm
    # D1 (processors, 2 cores, about 20 s)
    harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/C-sidm/drift --cores 2 \
      --purpose "drift D1" -- python3 tracks/C-sidm/drift/scripts/controls.py --pulsation \
      --out '$NRPIC_RUN_DIR' cc1_kninf=$R/C-20261115-171058-c26cfad/cc1_kninf \
      cc2_kninf=$R/C-20261115-171059-4b70228/cc2_kninf
    # decks and lists
    python3 tracks/C-sidm/drift/scripts/make_decks.py
    # one card job (k = i, ii, iii, iv, v); check squeue first: at most one job of this package
    harness/bin/nrpic-run submit --launcher batch --list tracks/C-sidm/drift/inputs/job_<k>.list \
      --wall 00:55:00 --gpu-hours 0.75 --exe /data/haiyangw/nrpic/.work/build_gpu_v03/src/athena \
      --kind scouting --gate G2 --package tracks/C-sidm/drift --particles 100000 --purpose "drift (<k>)"
    # comparison of a card run with its M/4 control (processors)
    harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/C-sidm/drift --cores 2 \
      --purpose "drift M8 cc2" -- python3 tracks/C-sidm/drift/scripts/compare.py --out '$NRPIC_RUN_DIR' \
      --tag cc2_M8 cc2_M4=cc2:$R/C-20261115-171059-4b70228/cc2_kninf \
      cc2_M8=cc2:$R/<run (i)>/cc2_kninf_M8 --ratio cc2_M8/cc2_M4

The continuation of a wave-2 run needs the executable that wrote its restart file: the
wave-2 `batch.list.exe` and `.work/build_gpu_v03/src/athena` have the same sha256
(f9f2dc12...be3a1, JOURNAL entry 1).

## Results

(filled as the runs finish; see JOURNAL.md for the full outcomes)

| Test | Run id | Outcome |
|---|---|---|
| D1 processor analysis of the wave-2 controls | C-20261120-222211-aa1be86 | the excursion is a fundamental radial pulsation started at a turning point: P = 399-415 M (CC1), 355-393 M (CC2) (cosine and sine-with-trend fits), amplitude 0.0154 and 0.0086 in alpha_c, 9 % and 5 % in the areal radius of the 50 % shell; fluid fundamental mode with the F21 index 358 M and 305 M; D1.1-D1.4 pass, D1.5 failed |
| M/8 deck smoke (processors, nlim = 0) | C-20261120-222544-e5a7492 | 456 MeshBlocks, 8 physical levels; H-norm2(0) = 0.149 against 0.0235 at M/4 |
| (i) cc2_kninf_M8 | C-20261120-222533-ce50a86 | pending (Slurm 4741) |

## Pending runs

(ii), (iii), (iv) and the optional (v) are written and committed; each is submitted with
the batch command above once the previous job of this package has left the queue.

## Requests

(written at the end of the package)
