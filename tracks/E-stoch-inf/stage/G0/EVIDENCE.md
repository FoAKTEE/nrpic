# G0 evidence of E-stoch-inf: artefacts, run ids and the lead's verification

Paths relative to `tracks/E-stoch-inf/`. Run manifests: `runs/<run_id>/manifest.json`;
outputs: `/data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>/` (not committed). Runs
registered with `harness/bin/nrpic-run` carry the short owner id ("E-2026...").

## 1. Artefacts by package

| Package | Documents | Code | Figures | Runs |
|---|---|---|---|---|
| spec (E-pre-1) | `spec/SPEC.md`, `spec/scope/SCOPE.md` (owner's v1), `spec/README.md`, `spec/JOURNAL.md` | `spec/ref/ms_reference.py`, `norm_test.py`, `ic_constraint_check.py`, `make_figures.py` | `spec/fig/fig_background.png`, `fig_freezing.png`, `fig_spectra.png`, `fig_drift.png`, `fig_norm.png` | E-stoch-inf-20261115-122806-ef0d039 (T1, T2), -122934-9ac98d8 (T3), -123146-82d2fd4 (T4), -123201-82d2fd4 and -123236-2e87364 (figures, T2d) |
| codebase (E-pre-2) | `codebase/DESIGN_REVIEW.md`, `README.md`, `JOURNAL.md` | `codebase/ref/synth.py`, `d1_memory.py`, `d2_synthesis.py`, `d3_momentum.py`, `d4_stages_window.py`, `cost.py`; `codebase/inputs/mem.athinput` | `codebase/figs/d1_memory.png`, `d2_synthesis.png`, `d3_momentum.png`, `d4_stages_window.png`; `figs/cost.json` | E-stoch-inf-20261115-122727-a1c2237 (D1 AthenaK memory runs), -123936-b2ec5c7 (D1-D4, cost) |
| langevin (E-pre-3) | `langevin/README.md`, `JOURNAL.md` | `langevin/sdn/*.py`, `langevin/scripts/*.py` | `langevin/fig/v1_*`, `v2_quadratic_m1*`, `ref_quadratic_*`, `ref_inflection_*`, `ref_inflection_endinf` | V1: -125014-097160b, -125312-dafadc4, -125656-e3eaef3; V2: -125316-dafadc4 (failed at the JSON dump), -125658-e3eaef3; references: -130137-176cdd6 (USR), -130139-176cdd6 (SR); end of inflation: -130747-1b9bee4, -132724-cab7451; figures: -130917/-130919-74083ad, -131133/-131232-02047c4 |
| noise (E-pre-4) | `noise/NOISE_SPEC.md`, `RNG_REQUIREMENTS.md`, `README.md`, `JOURNAL.md` | `noise/ref/*.py`, `noise/validate/*.py`, `noise/validate/inputs/reader_test.athinput` | `noise/fig/*.png` (10) | T-N0 -125255-fcdcbdc; T-N1 -125434-742a681, -125603-39cb4dd; T-N2-T-N4 -131031-ec74943; T-N5 -131126-8eb199a; T-N6/T-N7 -131526-629fed8 (failed, syntax error), -131551-629fed8, -131820-629fed8; T-N3b/T-N4b -132950-16a0168; T-N8 -133731-2031735 |
| lead | owner `JOURNAL.md` (predictions L-R, L-B, L-N, L-I, L-U and outcomes), `RISKS.md`, this directory, `stage/G1/STATUS.md` | `analysis/lead/rerun_helper.sh`, `compare_json.py`, `lead_bg.py`, `lead_dn.py`, `u_runs.py`, `inputs/u_base.athinput`, `inputs/u_base32.athinput` | in the run directories: `bg/fig_lead_bg.png`, `bg/fig_lead_ms.png`, `dn/fig_lead_dn.png`, the validator figures of L-U | E-20261115-135218-bdf4710 (L-U smoke), -135523-a32c3a6 (L-U U1-U8 and validation), -135531-0c4e629 (rerun spec), -135532-3f958a1 (L-B, L-N), -135532-5ec2b09 (rerun noise), -140116-87c1cc5 (rerun codebase), -140502-f70b223 (rerun langevin), -140502-2957846 (L-U validations), -140553-0b75e1e (L-U diagnostic) |

## 2. The lead's verification, package by package

Method: rerun the package's scripts from the committed code into a new registered run and
compare every numeric leaf of the JSON outputs with the helper's run
(`analysis/lead/compare_json.py`); look at every figure the package cites; check the
central claims by an independent route where one exists; read the derivations.

### spec (E-pre-1)

Confirmed:
- Rerun E-20261115-135531-0c4e629: `summary.json` (545 numeric leaves), `quadratic.json`
  (272), `inflection.json` (273), `norm_test.json` (92) identical bit for bit; `ic_check.json`
  identical (symbolic residuals).
- Independent background (own fixing formula derived from the e-fold equations, own
  integrator, complex-step derivatives; run E-20261115-135532-3f958a1): phi0 = -14.094995,
  m = 1.734945e-6, eps1(N*) = 1.110706e-2, eps2(N*) = -2.21331e-2, V(N*) = 2.69006e-2 (Mpl =
  100), inflection dphi/dN = 0.1026820, H0 = 9.590198e-6, H* = 9.362350e-6, USR 2.5237 to
  6.5498, eps1 min 9.716e-13 at 8.33, late eps2 -2.7615e-2. Agreement with SPEC 6 to the
  printed digits except inflection eps1(N*) 1.31625e-2 against 1.3164e-2 (1.2e-4 relative,
  within the figure-reading level that matters here).
- Independent freezing check (flat-gauge field equation with and without the metric term,
  one SR mode leaving at N* + 1.5): with metric perturbations P_R(N_f) = 1.0108 H^2/(8 pi^2
  eps1) at exit and slope -5.8e-4 per e-fold between 3 and 6 e-folds after exit; without,
  slope -0.0519 against -4 eps1 = -0.0513, and 0.70 of the full spectrum at N_f (SPEC 7.3:
  1.010-1.012; -0.051 to -0.055; 0.65-0.79). USR mode leaving at N* + 0.7: deformed/full =
  2.08 at N_f, between the SPEC's 8.4 (k = dk) and 1.4 (k = 2.8 dk). Figure
  `bg/fig_lead_ms.png` looked at.
- Draw normalisation: re-derived by hand (f = L^(-3/2) IRFFTN{f_k s_k} with <|s_k|^2> = 1
  gives P = |f_k|^2); the two printed prefactors read at P2:876-884.
- delta-Pi erratum: re-derived from P2's own dictionary (JOURNAL L-I); in addition the
  printed formula was read: it carries -sqrt(2 eps1) H Mpl Psi_G, which is zero in the
  geodesic gauge (P2:490).

Wrong or imprecise, fixed by the lead: SPEC 5.3 said the printed eq. (17) "lacks" the term;
it prints a Psi_G term in its place (reworded). SPEC 5.4 keyed the white noise by cell;
aligned with the wave-vector keys of NOISE_SPEC and core's code (request L1 of the noise
package). SPEC 2.5 and 10 described core as having no scalar field and asked for a GPU FFT;
updated to core's 836ac86 (no FFT needed). SPEC 7.2 gained A8 (request of the langevin
package).

Not confirmed: the unit mapping to G = 1 (SPEC 2.5) and the extraction factors E6 are hand
derivations not yet exercised by a run; core's FLRW test and the first noise run will
exercise the first.

### codebase (E-pre-2)

Confirmed: rerun E-20261115-140116-87c1cc5: d1.json (78 leaves), d3.json (68), d4.json (39) and cost.json (209) identical; in d2.json only the six wall-clock `seconds` leaves differ (exit status 1 of the run comes from them); figures d1-d4 looked at; the
design's central requests checked against core's source (SCOPE 6): stage-wise metric for
Tmunu, kicks with the stencil projector, lockstep mode data, separable synthesis; the
256^3 card-hour estimate re-derived by hand. The processor throughput of D1 (1.45e4-1.54e4
zone-cycles/s per core) is reproduced by the lead's smoke run of core's executable (1.35e4,
run E-20261115-135218-bdf4710).

Not confirmed: the assumed 15 percent overhead of field and kicks and 3e12 flop/s of the
synthesis on a card (need a card build of `core/scalar-field`); memory on the card (host
RSS was used).

### langevin (E-pre-3)

Confirmed: <N> and var N of the quadratic benchmark from the lead's own iterated
first-passage integrals (run E-20261115-135532-3f958a1, three grids, Richardson): <N> =
9.385995 +- 3e-6, var N = 4.5215404 +- 3e-9, against the helper's 9.38603 and 4.521540
(-3.8e-6 and +8e-8 relative). Rerun E-20261115-140502-f70b223: V2 (`v2_quadratic.json`, 94 numeric leaves) identical; the quadratic reference with 1e5 instead of 1e6 realisations agrees within its errors: var/var_lin 0.9966 +- 0.0043 (helper 0.9981) at sigma = 0.01, 1.0011 (1.0050) at 0.1, 1.4433 +- 0.0067 (1.4492) at sigma = 1, de Sitter 0.778 +- 0.007 (0.789), lattice sum 1.0863 (1.0866), linear 1.0101 +- 0.0087 (1.0019); var_lin 3.9248e-10 and lattice/continuum 1.0805 identical. Figures looked at:
`ref_quadratic_pdf.png`, `ref_inflection_pdf.png`, `v2_quadratic_m1.png`.

Not confirmed by the lead: the end-of-inflation statistics after USR (runs -130747-1b9bee4,
-132724-cab7451), the importance sampling of the phase-space solver (not validated by the
helper either), the stochastic-lattice assessment (a reading, no run).

### noise (E-pre-4)

Confirmed: rerun E-20261115-135532-5ec2b09: T-N0 bit-identity reproduced (153684 lattice
keys and 2000 random keys, 0 words and 0 normal deviates differing); self-test
`selftest.json` (49 leaves) and T-N8 `dump_selftest.json` (112 leaves) identical; T-N1
counts reproduced (548958 modes, 13038 and 16298 steps); T-N5 reader on real AthenaK output
bitwise across 1, 8, 64 MeshBlocks, 5.4e-8 from the formula, 7e-2 with exchanged axes. The
run's exit status 1 comes from one leaf only: the maximum deviation of the library
logarithm (not used by the code) was 6.2e-13 against the helper's 1.16e-12, an environment
difference of `numpy.log` (median 1.1e-15 in both); the bit-identity results do not depend
on it. Then the validator was applied to output of core's code (L-U, section 3).

Not confirmed: rank-count independence (one rank only); the 64^3 x 300-cycle base case and
U9 on a card (pending).

## 3. Core's implementation, checked by the lead (L-U)

Read in the source (`git show core/scalar-field:athenak/src/scalar_field/scalar_field_noise.cpp`,
836ac86): kicks, projector, window derivatives, mode equation, eps2, lockstep update and keys
as listed in `spec/scope/SCOPE.md` section 6; each formula compared with SPEC 2-3 and
re-derived by hand where noted there.

Runs with core's processor executable `wt/core-scalar/.work/exe/athena_cpu_836ac86`
(sha256 65ff2162...00144, used read only):

| Run | What | Result |
|---|---|---|
| E-20261115-135218-bdf4710 | smoke, 64^3, 4 cycles | 1.35e4 zone-cycles/s, serial; 64^3 x 300 would cost 95 min per run |
| E-20261115-135523-a32c3a6 | U1-U8 of NOISE_SPEC 9, scaled base case N = 32 (`analysis/lead/inputs/u_base32.athinput`) | all nine AthenaK runs completed; first validation pass: Markov Heaviside passes, Markov tanh fails A1, frozen validation stopped in the validator (U5a read with U1's nmax2; validator defect, fixed) |
| E-20261115-140502-2957846 | the three validations, each run with its own input | frozen tanh: A0-A8, A10, A11 (1 vs 8 and 1 vs 64 MeshBlocks bit-identical), A12 (restart at cycle 60 bit-identical), A13 (2.4e-15), A15 pass, A1 4.1e-14; Markov Heaviside: all pass; Markov tanh: all pass except A1 1.07e-10 (contract 1e-11); the diagnostic part of this run failed (syntax error) |
| E-20261115-140553-0b75e1e | per-mode diagnostic of the A1 difference (`fig_lu_diag.png`, looked at) | U6: modes with dW > 1e-6 agree to 4e-14 of their base amplitude, the difference grows like 1/sqrt(dW) on modes past crossing (ill-conditioned sqrt of a difference of numbers near 1); U1: 1e-15 floor everywhere. Prediction L-U2 held for its main part; its bound line (no rounding floor) is exceeded by a factor 1.5 at dW ~ 0.1, the FFT rounding floor |

The validator figures (`val_frozen/fig_val_run.png`, `val_markov_tanh/fig_val_markov_tanh.png`)
were looked at. The A2 shell means of shells 1-7 are the same numbers as in the helper's
synthetic self-test (1.58 at shell 1, 1.19 at 4, 0.91 at 5): the code draws the same
amplitudes as the reference because they are keyed by wave vector, independent of N.

## 4. Null results and failed runs on record

- spec: T2a (full-MS drift above 1e-3 per e-fold for 6 of 23 modes; cause found in T2d),
  T2b predictions (USR peak 1.017 above the predicted band; deformed vs full closer than
  predicted) in `spec/JOURNAL.md`.
- codebase: D4(b) refuted at its threshold (1e-7 instead of 1e-8; h^2 truncation of the
  finite-difference check); first attempt with `python3 -I` failed (`attempt1/`).
- langevin: P1d, P2c, R2f, E3 refuted (`langevin/JOURNAL.md`); run -125316-dafadc4 failed at
  the JSON dump.
- noise: T-N3 refuted (2 of 38 correct validations failed A3 at a fixed level); T-N0(ii) and
  T-N6 as worded; run -131526-629fed8 failed (syntax error).
- lead: the 64^3 x 300 base case of the unit test was replaced by a scaled case after the
  smoke run timed the processor build (JOURNAL); the noise rerun exit 1 (library-log leaf).

## 5. Added in waves 2 and 2b (lead of wave 2b, 2026-11-19)

| Item | Artefact | Runs |
|---|---|---|
| Working note v0 and schematics (C5-C7, C10, C11, C15-C17) | `note/main.tex`, `note/main.pdf`, `note/figures/`, `note/tables/` | E-20261115-173904-3be0405 (final); superseded or failed: -172421-50ac4ce, -172442-78cf53e, -173135-858482f, -173402-641b6e2 |
| Verifier report (C18) | `stage/G0/VERIFIER.md`, `stage/G0/JOURNAL.md`, `stage/G0/scripts/`, `stage/G0/results/`, `stage/G0/fig/` | E-20261115-174515-4d30c15 (failed), -174600-81652ff (closed by the lead today), -174606-3c67607, -175051-b67c97e, -180056-d62ee5a, -180348-d799c68, -180445-e72dad6 |
| Measured cost (C4) | `ladder/README.md`, SCOPE.md 8 | E-20261115-172618-f948386 (P256, 0.503 card-hours); core-20261115-143907-cea4c86 (128^3 throughput, core's run) |
| Lead's re-check of the helpers (C14) | `stage/REVIEW-wave2.md`, `stage/G0/REVIEW.md` | E-20261119-150842-ca70d37, -150238-b81e33f, -150346-a513bc8, -150541-3210cd6; stopped: -145853-ef835c2 |
| Decision of the gate (C8) | decisions 0013, 0017 | |
| Errata as knowledge-base claims (C2) | kb claims 603-609, snapshot kb-20261115-44b7406 | kb-20261115-154906-f19880f (kb's locator check) |
