# usr: preparation of the ultra-slow-roll (inflection) case (E-stoch-inf, wave 3a)

The second test case of the specification (`../spec/SPEC.md` section 6): the Higgs
inflection potential of arXiv:2512.14649 (P1:405-424) with its ultra-slow-roll (USR) phase,
prepared for this repository's AthenaK: background and landmarks a run must reproduce,
the expected power spectrum and its enhancement, acceptance quantities with thresholds
(written before any run, `JOURNAL.md` entry 2), the inputs for core's branch executable
`scratch/core/exe/core_scalar-2` (initial slice at N*, `<problem> id = stochastic`) and
for release core-v0.3, and low-resolution processor runs. Predictions and outcomes:
`JOURNAL.md`. Results in short: `JOURNAL.md`, last entry.

## Contents

| Path | What |
|---|---|
| `scripts/usr_reference.py` | reference (ODEs and lattice sums only): T0 potential in Planck and code units, check of the coded V' (`athenak/src/scalar_field/scalar_field.hpp:84-93`); T1 background in e-folds from N0; T2 the code-time system (ADM form, exact) and the RK4()4[2S] twin of a homogeneous run (Z4c form, chi as variable); T3 landmarks; T4 mode functions (Bunch-Davies at N0 to N*), mode files, full and FLRW-lattice spectra to N_f, lattice variances |
| `scripts/reference_figures.py` | figures of the reference |
| `scripts/make_inputs.py` | writes `inputs/*.athinput` and `inputs/proc.list` from `results/usr_reference.json` |
| `scripts/run_list.sh` | runs a list on the processors, one executable per entry (`v03` release core-v0.3, `s2` core_scalar-2) |
| `scripts/usr_lib.py` | NRSFDMP2 reader, modes of the hemisphere, R^NR extraction, code-time MS reference (continuum or stencil k^2), homogeneous twin with a given step sequence |
| `scripts/analyse_runs.py` | the acceptance quantities U-A0 to U-A6 on the processor runs, `summary.json`, figures |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `results/usr_reference.json` | all numbers of the reference run E-20261119-143905-f2bcde3 (code inputs, landmarks, a table every 0.5 e-fold, twins, spectrum at N_f, lattice variances, mode-file checksums) |
| `results/landmarks.csv` | times and field values a run must reproduce (code units), one row per landmark |
| `results/usr_spectrum_Nf.csv` | per shell up to nmax2 = 4096: crossing, Delta_R at N_f (full MS, FLRW lattice), slow-roll estimate at crossing, enhancement |
| `results/runs/` | `summary.json` of the analysis of the processor runs |
| `inputs/modes_usr_n{16,64,256,1024,4096}.txt` | mode files (R, dR/dtau at N* per shell, code units; Bunch-Davies at N0 for every shell) |
| `inputs/usr_base.athinput` | 32^3 base input for core_scalar-2, initial slice at N* |
| `inputs/usr_256.athinput` | production set-up of P1 (256^3, nmax2 = 4096) for one card (not run here) |
| `inputs/usr_bg.athinput` | homogeneous background (id = flrw), runs on release core-v0.3 |
| `inputs/proc.list` | the processor runs of this package |
| `inputs/card_usr.list` | card runs proposed to the lead (ladder 64^3, 128^3 and 256^3), with costs; not submitted |
| `fig/fig_usr_*.png` | reference figures; `fig/fig_run_*.png` figures of the processor runs |

The case in code units (G = c = 1, time unit 1/H*, a* = 1, box 2 pi; SPEC 2.5), from run
E-20261119-143905-f2bcde3:

    <scalar_field> potential = inflection
                   lambda = 5.33317648526340e5   vev = 3.94952857597418e-2
    <problem>      phi0 = -1.64328188347203e-1   pi0 = 3.23658652791245e-2   (K0 = -3)
    <time>         tlim = 10.437508874065651     (N* + 10 e-folds)
    <scalar_field> noise_mode_file = inputs/modes_usr_n<nmax2>.txt

These equal core's `python/nrpic/sf_inflation.py` (branch core/scalar-2) to 1e-14, and the
mode file for nmax2 = 64 equals its `make_case.py` output to 2e-10 (JOURNAL entry 1).

## How to rerun

From the worktree root (`/data/haiyangw/nrpic/wt/E-stoch-inf`), with the worktree's
`.venv`:

    # reference (39 s on 4 cores)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/usr --kind scouting --gate G2 \
      --launcher local --cores 4 --purpose "..." -- bash -c 'cd tracks/E-stoch-inf/usr/scripts && \
      export OMP_NUM_THREADS=4 && python3 usr_reference.py --out "$NRPIC_RUN_DIR" && \
      python3 reference_figures.py --res "$NRPIC_RUN_DIR" --out "$NRPIC_RUN_DIR/fig"'
    # inputs from a reference
    (cd tracks/E-stoch-inf/usr/scripts && python3 make_inputs.py --ref ../results/usr_reference.json \
      --out ../inputs --run-id <reference run id>)
    # processor runs (9 serial runs at once, about 15 min on a loaded machine)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/usr --kind scouting --gate G2 \
      --launcher local --cores 9 --background --purpose "..." -- \
      bash tracks/E-stoch-inf/usr/scripts/run_list.sh tracks/E-stoch-inf/usr/inputs/proc.list
    # analysis of a run directory of the list
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/usr --kind scouting --gate G2 \
      --launcher local --cores 4 --purpose "..." -- bash -c 'cd tracks/E-stoch-inf/usr/scripts && \
      export OMP_NUM_THREADS=4 && python3 analyse_runs.py --runs <rundir> --ref ../results \
      --out "$NRPIC_RUN_DIR"'

Traps: `nrpic-run` starts its command without a shell (write `$NRPIC_RUN_DIR` only inside
`bash -c '...'`); a production run for G2 is refused before G1's sign-off, so these are
scouting runs; the dump times are the first step after each multiple of `dump_dt`, not
the multiples themselves (the analysis evaluates the reference at the recorded times).

## Requests

(filled at the end of the package; see the last JOURNAL entry)
