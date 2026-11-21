# usr: the ultra-slow-roll (inflection) case (E-stoch-inf, waves 3a and 3)

The second test case of the specification (`../spec/SPEC.md` section 6): the Higgs
inflection potential of arXiv:2512.14649 (P1:405-424) with its ultra-slow-roll (USR) phase,
prepared for this repository's AthenaK: background and landmarks a run must reproduce,
the expected power spectrum and its enhancement, acceptance quantities with thresholds
(written before any run, `JOURNAL.md` entry 2), the inputs for core's branch executable
`scratch/core/exe/core_scalar-2` (initial slice at N*, `<problem> id = stochastic`) and
for release core-v0.3, and low-resolution processor runs (wave 3a); in wave 3 the card runs:
the ladder 64^3/128^3 with +-s pairs and a halving pair, and P1's production set-up 256^3
(core_scalar-3 athena_gpu 5cc2821; pre-registration JOURNAL entries 9-10). Predictions and
outcomes: `JOURNAL.md`. Results in short: section Results below.

## Contents

| Path | What |
|---|---|
| `scripts/usr_reference.py` | reference (ODEs and lattice sums only): T0 potential in Planck and code units, check of the coded V' (`athenak/src/scalar_field/scalar_field.hpp:84-93`); T1 background in e-folds from N0; T2 the code-time system (ADM form, exact) and the RK4()4[2S] twin of a homogeneous run (Z4c form, chi as variable); T3 landmarks; T4 mode functions (Bunch-Davies at N0 to N*), mode files, full and FLRW-lattice spectra to N_f, lattice variances |
| `scripts/reference_figures.py` | figures of the reference |
| `scripts/make_inputs.py` | writes `inputs/*.athinput` and `inputs/proc.list` from `results/usr_reference.json` |
| `scripts/run_list.sh` | runs a list on the processors, one executable per entry (`v03` release core-v0.3, `s2` core_scalar-2) |
| `scripts/usr_lib.py` | NRSFDMP2 reader, modes of the hemisphere, R^NR extraction, code-time MS reference (continuum or stencil k^2), homogeneous twin with a given step sequence |
| `scripts/analyse_runs.py` | the acceptance quantities U-A0 to U-A6 on the processor runs, `summary.json`, figures |
| `scripts/make_card_inputs.py` | writes `inputs/usr_card.athinput`, `inputs/usr_256s.athinput` and the card lists (dump_constraints, con_signed, dump_dt = tlim/40 or tlim/20 so the last dump is N_f) |
| `scripts/card_lib.py` | sequential dump reader (seek + numpy.fromfile, no memory map), R^NR extractor (linear and log chi forms, full lattice), per-shell code-time MS reference, linear realisation field, con_signed record columns, cost from athena.log |
| `scripts/analyse_cards.py` | the card runs against entries 9-10: `--group g1` (pairs, halving, ladder 64 -> 128, constraint parts odd/even in s) or `--group u256` (single run or pair; one-point statistics) |
| `scripts/quick_records.py` | records only (con.hst, lockstep .modes, athena.log): a check of a card job in seconds |
| `scripts/floor_split.py` | post-hoc: the s-independent floor of the constraint parts from the halving pair, floor-corrected halving factors |
| `scripts/lockstep_shells.py` | lockstep record per shell at N_f against the code-time MS reference (RK4 phase error k^5 dt^4/600), and the per-shell error of R^NR (single run and, with U256m, the odd part) against it |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `results/usr_reference.json` | all numbers of the reference run E-20261119-143905-f2bcde3 (code inputs, landmarks, a table every 0.5 e-fold, twins, spectrum at N_f, lattice variances, mode-file checksums) |
| `results/landmarks.csv` | times and field values a run must reproduce (code units), one row per landmark |
| `results/usr_spectrum_Nf.csv` | per shell up to nmax2 = 4096: crossing, Delta_R at N_f (full MS, FLRW lattice), slow-roll estimate at crossing, enhancement |
| `results/runs/summary_<run_id>.json` | numbers of the analyses: E-20261119-145842-74b52ec (first batch), E-20261119-152843-c201aad (both batches, final); cards: E-20261121-075307-4542ce1 (group 1), E-20261121-084815-63462b8 (U256), E-20261121-101756-6bffd0c (U256 with U256m); `quick_records_E-20261121-075022-7f76477.json`, `floor_split_E-20261121-080134-a0cc3eb.json`, `lockstep_shells_E-20261121-{090057-19571c7,103157-96fee1d}.json` |
| `inputs/modes_usr_n{16,64,256,1024,4096}.txt` | mode files (R, dR/dtau at N* per shell, code units; Bunch-Davies at N0 for every shell) |
| `inputs/usr_base.athinput` | 32^3 base input for core_scalar-2, initial slice at N* |
| `inputs/usr_256.athinput` | production set-up of P1 (256^3, nmax2 = 4096) without the dumps of H, M (base of `usr_256s.athinput`) |
| `inputs/usr_bg.athinput` | homogeneous background (id = flrw), runs on release core-v0.3 |
| `inputs/proc.list`, `inputs/proc2.list` | the processor runs of this package (first batch; second batch: halving s = 1/2, Courant 0.125) |
| `inputs/card_usr.list` | card runs proposed in wave 3a, with costs (superseded by the lists below) |
| `inputs/usr_card.athinput`, `inputs/usr_256s.athinput` | card inputs (64^3/128^3 ladder base; 256^3 production set-up) with H, M_i and metric dumps and con_signed |
| `inputs/card_g1.list`, `inputs/card_u256.list`, `inputs/card_u256m.list` | group 1 (U64p/m, U128p/m, U128hp/hm), U256 (s = +1), U256m (s = -1) |
| `fig/fig_usr_*.png` | reference figures; `fig/fig_run_*.png` figures of the processor runs; `fig/fig_card_g1_*.png` group 1 on the cards; `fig/fig_card_u256_*.png` U256; `fig/fig_card_u256pair_*.png` U256 with U256m; `fig/fig_card_lockstep.png` lockstep check |

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

    # card jobs (one batch job per list; the analysis right after the job)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/usr --kind scouting --gate G2 \
      --launcher batch --exe /data/haiyangw/nrpic/scratch/core/exe/core_scalar-3/athena_gpu \
      --list tracks/E-stoch-inf/usr/inputs/card_g1.list --gpu-hours 0.4 --wall 00:24:00 --purpose "..."
    #   (card_u256.list: --gpu-hours 0.97 --wall 00:58:00)
    #   (card_u256m.list: --gpu-hours 0.72 --wall 00:43:00)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/usr --kind scouting --gate G2 \
      --launcher local --cores 3 --purpose "..." -- bash -c 'cd tracks/E-stoch-inf/usr/scripts && \
      export OMP_NUM_THREADS=3 && python3 analyse_cards.py --group g1 --run <card run dir> \
      --ref ../results --out "$NRPIC_RUN_DIR" --workers 3'      # or --group u256
    # U256 with U256m: --group u256 --run <U256 run dir> --run <U256m run dir> (the pair is
    # formed across the two run directories); lockstep check:
    #   python3 lockstep_shells.py --g1 <group-1 run dir> --u256 <U256 run dir> \
    #     --coeffs <analysis run dir>/coeffs_N256.npz --ref ../results --out "$NRPIC_RUN_DIR"

Traps: `nrpic-run` starts its command without a shell (write `$NRPIC_RUN_DIR` only inside
`bash -c '...'`); a production run for G2 is refused before G1's sign-off, so these are
scouting runs; the dump times are the first step after each multiple of `dump_dt`, not
the multiples themselves (the analysis evaluates the reference at the recorded times).

## Results (details and failed predictions: JOURNAL entries 4, 6, 8)

Runs: reference E-20261119-143905-f2bcde3; processors E-20261119-144116-8aa7c22 (9 runs)
and E-20261119-145835-67cde45 (3 runs); analyses E-20261119-145842-74b52ec and
E-20261119-152843-c201aad. All scouting, gate G2, no card time.

| Item | Result |
|---|---|
| Potential of the code (`potential = inflection`) against P1:409 | same form by reading; V and V' in code units equal the Planck form to 1.4e-15 and 1.2e-15 (T0) |
| Background landmarks (cN, code time) | eps1 max 1.6240, 1.6465; USR onset (eps2 = 3) 2.5234, 2.5829; inflection point = eps2 max (5.99999965) 4.5320, 4.6926; USR end 6.5503, 6.8132; eps1 min (9.716e-13) 8.3310, 8.6841; N_f 10, 10.4375 (`results/landmarks.csv`) |
| Spectrum at N_f | Delta_R from 1.02e-5 (k = dk) to 1.017 (64 dk); enhancement over the slow-roll value at crossing 1.2e5 to 4.2e8 (largest near 12 dk); FLRW lattice / full MS 8.8, 2.1, 1.4 for k = 1, 2, 3 dk (`results/usr_spectrum_Nf.csv`, `fig/fig_usr_spectrum.png`) |
| One-point rms of W R at N_f | 0.0198 (32^3, nmax2 16), 0.066 (32^3, 64), 0.20 (64^3), 0.49 (128^3), 0.894 (256^3; squared 0.7987 = langevin's lattice band variance 0.79863) |
| Homogeneous runs (core-v0.3, core_scalar-2) | equal the RK4()4[2S] twin to rounding; byte-identical to each other; Pi error 4.1e-4 at Courant 0.25 on 32^3 steps, fourth order (16.3); e-folds within 7e-6 (U-A0, U-A1 pass) |
| Per-mode R^NR against MS (U-A2) | 4.1e-4 (32^3, nmax2 16, Courant 0.25; time step), 2.3e-4 at Courant 0.125 (stencils, shell abs(n) = 4); 5.9e-3 at four cells per wavelength (nmax2 64); threshold 0.02 |
| Freezing (U-A3) | k <= 3 dk within 0.11 percent of the full MS |
| Second-order part of R^NR | 2e-5 of the first, scales as s^2 |
| Constraints (U-A4) | not testable at 32^3: H record = background time residual (1.1e-7 of [H] at Courant 0.25); M record mixed in the entry, first-order stencil truncation (3e-4) during USR, rounding floor after USR |

### Card runs (wave 3; JOURNAL entries 9-15)

Executable core_scalar-3 athena_gpu (5cc2821) throughout. Group 1: card run
E-20261120-222621-ba66218 (job 4742, 0.157 card-hours), record check
E-20261121-075022-7f76477, analysis E-20261121-075307-4542ce1, floor reading
E-20261121-080134-a0cc3eb. All scouting, gate G2.

| Item (pre-registration, entry 9.1) | 64^3 (nmax2 = 64, 8 cells per shortest wavelength) | 128^3 (16 cells) | Verdict |
|---|---|---|---|
| U-A0, max abs dN at the landmarks | 4.2e-7 | 2.6e-8 | pass (1e-5) |
| U-A1, <Pi> at N_f (time part after the s^2 part) | 2.50e-5 (2.52e-5) | 1.33e-6 (1.56e-6); s^2 part -2.25e-7 | pass (1e-3) |
| lockstep record against the code-time MS at N_f | 3.57e-5 | 2.25e-6 | fourth order; 1.4 x the prediction |
| U-A2s, odd part per mode at N_f, all 1054 modes | 1.14e-4 (shell 64) | 2.12e-6 | pass (0.02); order 4.0 to 5.75 per top shell |
| U-A2n, even/odd rms at N_f | 2.19e-5 | 2.19e-5 (s = 1/2: 1.09e-5) | second order in s, resolution-independent |
| U-A3, abs(P/P_MS - 1), k <= 3 dk | 4.8e-5 | 2.5e-6 | pass (10 %) |
| U-A4 (a, b) halving at 128^3 with the bars of entries 9-10 | | H even 3.82 (one judged dump); M even 3/20 within 4.00 +- 0.05; M odd 0/20 within 2.00 +- 0.05 | FAILED as pre-registered: an s-independent floor (absolute; M: 2e-14 to 8.5e-13, H: 4e-15 to 1.3e-12) lies far above the bars |
| the same with the floor removed (post-hoc, entry 12.2) | | even factors 3.987 to 4.001 (H and M, 10 dumps each) | second order holds wherever resolved |
| U-A4 (c), order of the odd parts 64 -> 128 | | H 5.5-5.7, M 5.2-5.9 for cN 2-4; above the floor only there | holds there |
| U-A4 (d), strict A4 at 128^3 in the entry (cN <= 2.08) | odd/even of H up to 3.2 (64) | M odd/even <= 0.079; H below the bar | holds for M |
| records <abs M/[M]> late | 1.07e-2 | 2.47e-2 (4.3e-2 at s = 1/2) | a floor over [M] proportional to s (P1:541's "1e-2" is no error measure) |
| cost on one A100 | 12 s per run | 132 s per run, 0.155 s per step | |

U256, P1's production set-up (256^3, nmax2 = 4096, k_max = 64 dk, s = +1): card run
E-20261121-075255-8cf90e7 (job 4774, 0.617 card-hours), analysis E-20261121-084815-63462b8,
lockstep check E-20261121-090057-19571c7 (JOURNAL entry 14).

| Item | Result | Verdict |
|---|---|---|
| U-A0, max abs dN | 1.6e-9 | pass |
| U-A1, <Pi> / <phi> / <K> | 4.2e-5 (the s^2 backreaction) / 1.2e-9 / 2.4e-11 | pass |
| U-A2, single run, per mode at N_f, k <= 32 dk (68532 modes) | median 2.6e-4, rms 7.9e-4, max 5.9e-2; 10 modes above 0.02, all with abs(alpha) in the smallest 0.07 % | FAILED as written (an additive part over a small amplitude); over the shell rms at most 9.1e-4 |
| U-A3, k <= 3 dk | 0.9923 to 1.0016 | pass |
| U-A5, shell power ratio at N_f | k <= 32 dk: 5.9e-4; top shells 6.7e-3 | as predicted |
| lockstep record of the mode functions | 2.55e-3 for the top shell = k^5 dt^4/600 (RK4 phase error from N*; within 3 % on 2934 shells); R^NR of the top shells inherits it | the U2 prediction (1e-6) failed; cause found |
| P-h one-point at N_f | rms R^NR 0.89452 (linear field of the realisation 0.89436, ensemble 0.89366); skewness 0.0024, excess kurtosis 0.0011; max abs 4.568 (linear 4.562; 5.1 rms); R^NR - R_lin rms 9.7e-4 | Gaussian, linear to 1e-3 of the rms; no "outliers ~ 10" (P1:534) in this realisation |
| where the linear per-mode comparison loses meaning | worst mode passes 1e-3 at cN 6.0 and 0.02 at cN 7.0 (rms R^NR 0.15, 0.72); the rms over modes stays below 1e-3 to N_f | meaningful at the 1e-3 level through N_f |
| records | <abs H'/[H]> 2.9e-12 at most; <abs M/[M]> 2.5e-2 in USR, 2.1e-3 at N_f | as predicted |
| cost per realisation (SCOPE 8) | 1702 steps, 1.30 s per step, 37.0 min on one A100 = 0.617 card-hours; 19.6 GB card memory; 21 dumps of 2.95 GB (62 GB) | |

U256m, the mirrored partner (s = -1): card run E-20261121-085221-1f579fe (job 4783, 0.612
card-hours), pair analysis E-20261121-101756-6bffd0c, lockstep check with the pair
E-20261121-103157-96fee1d (JOURNAL entry 15).

| Item | Result | Verdict |
|---|---|---|
| U-A2s, odd part per mode at N_f, k <= 32 dk | max 1.09e-4, median 4.2e-5; the ten single-run failures 3.4e-5 to 8.8e-5 | pass (0.02) |
| U-A2n, even/odd rms at N_f | 2.53e-4 (k <= 32 dk), 2.88e-4 (all) | second order, as predicted from group 1 scaled by rms R |
| odd part of the top shells | the lockstep phase error (shell median 1.01 to 1.76 times it, k >= 40 dk) | |
| U-A3 on the odd part | 8.4e-5 | pass |
| one-point skewness, part even in s | +0.0015 in both runs (linear field +-0.0009) | the non-Gaussian part of the evolution at N_f |
| constraints | M odd part = the record (2.3e-2 at cN 6.5, top shells at 4 cells per wavelength), even part 10 times lower; strict A4 in the entry holds (H 0.40, M 0.45); late M odd = even, flat at 1.8e-13 absolute | late M at a level not explained (7 x the 128^3 floor) |

## Requests

- To core:
  1. Done or answered (kept for the record): the inflection form of `scalar_field.md`
     (closed by core in scalar-3); this package's inputs as the USR test (used by core);
     signed constraint means (`con_signed`, core_scalar-3, used here).
  2. Information, no action: the card build of core_scalar-3 (athena_gpu 5cc2821), whose
     READY names only a 20-step card comparison, ran six 64^3/128^3 runs of 427 to 851 steps
     and the 256^3 production set-up (1702 steps) to N_f without fault; its con_signed
     columns behave as `scalar_field_3.md` section 6 says (H' carries the s^2 residual of
     the initial slice, 2.87e-12 of [H] at t = 0 at both 64^3 and 128^3, a quarter at
     s = 1/2). Group 1: run E-20261120-222621-ba66218, records E-20261121-075022-7f76477.
- To the lead of E-stoch-inf:
  1. Pre-registration of the card runs (JOURNAL entries 9, 10) for adoption or amendment;
     SCOPE is unchanged. Amendment proposed from group 1 (entries 12.1-12.2): judge U-A4's
     halving on the parts with the s-independent floor removed (floor from the odd parts of
     the halving pair, f^2 = (4 o_{s/2}^2 - o_s^2)/3), or bar each part at three times that
     floor, instead of the fixed bars 3e-13 of <[H]> and 1e-12 of <[M]>: in USR the floor of
     M relative to <[M]> rises by 1e5 (to 1.4e-2 at N_f, 128^3) because <[M]> falls with
     Pi_b while the absolute floor stays. With the floor removed the even parts of H and M
     scale by 3.987 to 4.001 (U-A4(a)); the odd parts of H and M are above their floor at
     128^3 only for cN 2 to 4.5, where they converge at order 5.2 to 5.9 from 64^3.
  2. The late <|M|/[M]> of about 1e-2 (P1:541) is reproduced (1.07e-2 at 64^3, 2.47e-2 at
     128^3) and is a floor over a magnitude proportional to the amplitude (4.3e-2 at
     s = 1/2), not an error of the solution; do not use it as an acceptance number.
  3. A1 for USR at 1e-3: from 64^3 on the margin is 40 (2.5e-5) and 750 (1.3e-6 at 128^3).
  4. Cost per USR realisation in P1's set-up, measured (SCOPE 8, RISKS R9): 0.617 card-hours
     on one A100 (1702 steps at 1.30 s per step with 21 dumps of 2.95 GB; 1.22 s per step
     between dumps), 19.6 GB of card memory; R9's "630 card-hours per 1e3 USR realisations"
     becomes 617 with these dumps, about 580 without them (run E-20261121-075255-8cf90e7).
  5. G2 criterion "the USR case is reproduced": the evidence of this package is U-A0, U-A1,
     U-A3, U-A5 and P-h passing on 64^3, 128^3 and 256^3; U-A2 passing on the ladder and on
     the odd part of the 256^3 pair (1.1e-4), and failing as written for the single 256^3
     run on 10 of 68532 modes (their deviation is the part even in s over a small alpha);
     U-A4 failing as pre-registered (bars) but holding with the floor removed (128^3). The
     lead decides whether that is "reproduced"; the pre-registration says U-A2 is judged on
     the single run for U256 (entry 9.1), so U-A2 for U256 stays failed as written.
  6. Not explained: the late momentum parts of the 256^3 pair are equal and flat at
     1.8e-13 absolute, 7 times the 128^3 floor (entry 15); a halving pair at 256^3
     (s = +-1/2, about 1.2 card-hours) would tell a floor from a nonlinear part.
- To core (new): the lockstep integration of the mode functions runs from N* with the
  run's step, so a shell deep inside the horizon accumulates RK4's phase error
  k^5 dt^4/600: 2.5e-3 for k = 64 dk at 256^3 (run E-20261121-090057-19571c7, within 3 %
  on 2934 shells), and the injected sources of the top shells carry it (U-A5 6.7e-3 in
  power for the top shell). Sub-stepping the lockstep record (n sub-steps lower it by n^4),
  or starting each shell from its Bunch-Davies form when k/(aH) falls below some bound,
  would remove it at no cost to the field evolution. Not blocking: U-A2 gates k <= 32 dk,
  where this part is below 8e-5.
- To nobody else.
