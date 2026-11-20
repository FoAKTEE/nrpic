# JOURNAL of note (helper of C-sidm, wave 2)

Working note v0 of C-sidm, its figures, schematics, numerical ledger, the check of the
lead's documents against the run outputs, and `stage/G0/STAGE_REPORT.md`. Entries are
appended; predictions are written before the run they concern, outcomes after it, failed
predictions included.

## 2026-11-15 N1 prediction: figures, schematics and ledger from the registered runs

Run to register: `scripts/run_all.py --out <run dir>` (every `fig_*`, `schem_*` and
`ledger.py`), processors, one core, no card time. Draft runs of the four figure scripts went
to `scratch/C-sidm/tmp/notefig/` to fix the layout (not registered, not used).

Predictions (each read from a registered output; a different value refutes the script or
the record it reads):

- P1 every input file the scripts read matches the sha256 its run recorded (in
  `sha256sums.txt` or in the manifest's output list) where one is recorded; the runs
  without a record are listed as such. A mismatch would mean an output changed after its
  run and stops the script.
- P2 `fig_sequences`: binding-energy maximum of the thermal core (b = 0.1) at Z(0) =
  0.54041, radial-pulsation onset with Gamma = 1 + p/u at 0.63482, with 5/3 at 0.77924,
  trial criterion at 0.75001 (run C-sidm-20261115-120722-38ab057, criteria.json); King
  maximum y0 = 0.334032 at Z0 = 0.51191; monoenergetic maximum y_c = 0.67961 at z_c =
  0.45529. In panel (b) the normalised omega_0^2 crosses zero at the two onsets and is
  positive at the binding-energy maximum.
- P3 `fig_knudsen`: K = 168.895 for the King threshold model and 154.3-206.5 over the 13
  models (run -131130-3077a99, X4); Kn_c for a 200 M_sun core at 5 cm^2/g between 6.8e-20
  and 9.1e-20 in the track's definition, about twenty decades below the planned scan.
- P4 `fig_collisions`: closed form against quadrature at most 5.2e-7 (theta = 1e-3) and
  about 2e-14 at theta = 100; Monte Carlo rate deviations between -1.3 and +1.0 standard
  errors; T0 passes with the largest velocity error 3.2e-3 of the tolerance and the
  four-momentum residual 0.33 of it.
- P5 `fig_box_step`: recomputed from the 31 snapshots of run -121302-313d399 with the
  track's analysis code at HEAD: largest position error 1.808e-12 L and the code's slab
  sums equal to those of free streaming of the same sample to rounding (relative 0); the
  deviations from the ensemble curve in noise units equal those of `step_step.json`
  (max 1.846, 1.848, 1.846; rms 1.012, 1.010, 0.823). Refuted if the reference modules
  changed since 313d399 in a way that moves the ensemble curve (abd9c2e touched the
  analysis); then the ensemble numbers differ and the reason is recorded.
- P6 `ledger.py`: the claims of the lead's documents agree with the files except where a
  number was rounded or quoted for a narrower range; candidates seen while drafting:
  (a) G1 STATUS "Table 1 ... all columns within 1.1e-4 relative except R": the summary of
  run -120722 lists B at 2.4e-4 and eps, ec0 at 1.3e-4 (row main.tex:503, w0 = 4.5);
  (b) REPORT section 1 "every phase ... lasts at least 1e5 dynamical times": the time-scale
  run gives a fastest phase of 8.5e4 dynamical times of the core (a lower bound);
  (c) REPORT section 3 "R/M = 20-26, r_core/M = 1.5-2.1" for Z(0) = 0.40-0.80: the
  initial-model run gives 19.8-28.1 and 1.27-2.56 over that range.
  Each is checked by the script; a claim the files support is marked as agreeing.

## 2026-11-15 N1 outcome (run C-20261115-170415-385069e, nrpic-run, completed, 1 core)

- P1 held: all 63 input files carry a recorded sha256 and match it (23 through
  `sha256sums.txt`, 40 through the manifest's own output list of a wave-1 run; common.py
  learned both forms before the run).
- P2 held: 0.5404129, 0.6348166, 0.7792440, 0.7500060; King y0 = 0.3340322 at
  Z0 = 0.5119106; mono y_c = 0.6796101 at z_c = 0.4552905; panel (b) crosses zero at the
  two onsets and is positive at the maximum (PNG looked at).
- P3 held: K = 168.8954, 154.33-206.49; Kn_c(200 M_sun, 5 cm^2/g) = 6.77e-20 to 9.06e-20,
  1.9e9 M_sun: 6.43e-13 to 8.61e-13 (PNG looked at).
- P4 held: 5.172e-7 at theta = 1e-3, 2.46e-14 at theta = 100; rate deviations -1.30 to
  +0.98; T0 3.22e-3 and 0.330 of the tolerances.
- P5 held, including the ensemble numbers: 1.808e-12 L, relative 0, max 1.846, 1.848,
  1.846, rms 1.012, 1.010, 0.823 (identical to `step_step.json` of run -121302); so the
  analysis change of abd9c2e does not move this test.
- P6 held: 23 claims, 20 agree, the three predicted ones differ (files win):
  (a) Table 1: B at 2.43e-4, eps and ec0 at 1.3e-4 (line 503); the 1.1e-4 bound holds for
  E and E_rest only; (b) the fastest gravothermal phase is >= 8.5e4 dynamical times
  (not 1e5); (c) R/M = 19.8-28.1 and r_core/M = 1.27-2.56 over Z(0) = 0.40-0.80 (the quoted
  20-26 and 1.5-2.1 fit narrower ranges). One more rounding noted but counted as agreeing:
  King solvers agree to 3.5e-8 (quoted "3e-8"). `tables/claims.md`.
- All six PNGs of the run were opened from `note/figures/` after copying.

## 2026-11-15 N2 prediction: rerun after layout and naming changes

Changes since N1 (no change of what is read or computed): the ledger table is split in two
(it was taller than a page), the parameter table is narrower (labels, four decimals of y),
every legend has `frameon=False` explicitly (the style already sets it), the run key `f21`
is renamed `thermal`, the architecture schematic names the code without its release tag.
Prediction: every number printed by the scripts and every claim verdict is identical to N1
(23 claims, 3 differ); the data PNGs look the same; only `ledger.tex`, `parameters.tex` and
`schem_architecture.png` change. A changed number would mean a script change leaked into
the computation.

## 2026-11-15 N2 outcome (run C-20261115-171741-0e0da67, nrpic-run, completed, 1 core)

Held. Every number printed by the scripts is identical to N1, the claims files are byte-identical
(23 claims, 3 differ), the four data PNGs are byte-identical to N1; `ledger.tex` (now two
tables), `parameters.tex` and `schem_architecture.png` changed as intended (new PNG opened:
subtitle of the middle column reads "AthenaK: spacetime, particles, collisions"). All 63
inputs matched their recorded sha256. The submit waited about ten minutes for a free core
(other helpers held the 16 of the allotment); no run was started outside the allotment.

## 2026-11-15 Stage check (no prediction was written before it; recorded as such)

`harness/bin/nrpic-stage verify C-sidm G0` on d567429 (clean export, harness stage check, not
a registered run): the note's checks pass (note, note-pdf, style copies, one script per
figure, 2 schematics and 4 data figures, 6 of 6 scripts rerun in the export, 12 regenerated
files equal to the committed ones within rtol 1e-6 and PNG rms 0.005); `clean` fails on
other helpers' uncommitted files, `runs` on 7 unfinished wave-2 runs of other helpers and the
10 wave-1 gravothermal manifests (fields of the nrpic-run schema missing). Then
`nrpic-stage collect` and `report`: verdict FAIL (C18 and C20 OPEN for the lead, verify FAIL).
Committed in b74c46b.

## 2026-11-20 Wave 3, round 1, package "note": G1 note (checklist items C9, C10, C14, C16)

Helper of C-sidm, wave 3 round 1 (`../PLAN-wave3.md`, package 3). Worktree at 797bdbe5
(after 07538808 of the plan); no merge of main. Pause flag absent at 22:19 UTC; load 58.

### N3 prediction (written before the registered run of `scripts/run_all.py`)

Run to register: `scripts/run_all.py` (every `fig_*`, `schem_*` and `ledger.py`) into
`$NRPIC_RUN_DIR`, processors, 2 cores at most, no card time. New scripts: `schem_dataflow`,
`fig_box_summary`, `fig_heat`, `fig_onsets`, `fig_cluster`; `schem_architecture` redrawn;
`ledger.py` extended by G1 sections. Draft runs for layout go to `scratch/C-sidm/tmp/` and
are not used.

Predictions (each read from a registered output; a different value refutes the script or
the record it reads):

- P1 (inputs) Every file a script reads is listed in its run's `sha256sums.txt` (or the
  wave-1 manifest's output list) and matches it; the four G0 scripts still read their 63
  inputs with matching checksums. A mismatch stops the script.
- P2 (G0 numbers unchanged) The G0 rows of the ledger and the claims check are identical to
  run C-20261115-171741-0e0da67 (23 claims, 3 differ); the four G0 data PNGs are
  byte-identical to that run's (same scripts, same inputs, same style files).
- P3 `fig_box_summary` from runs C-20261115-165500-c67e036 (release) and
  C-20261119-141806-af19c1c (core/collisions-2, `coll_energy = particle`), and
  C-20261119-145925-dbcfb9c (T12): T2(b) ratio of summed pair probabilities to the
  Moller-averaged rate 0.999906-1.000096 in the 16 runs of each executable, the two equal
  within 1e-15 relative (identical counts in every step, `paired_counts_identical_all`);
  T2(b) z from -2.20 to +2.92; largest per-step |dE| of T1 at most 1.1e-7 of its bound in
  both; T12 rate per coordinate time and volume over the flat twin 1.4172488 = alpha0 psi0^6
  for all four pairs (z of order 1e-13); analytic ratio of the curved runs 0.99997-1.00009,
  |z| <= 2.4.
- P4 `fig_heat` from runs C-20261119-144535-2c7b6a4 (T6(b) runs) with analysis
  C-20261119-160003-287b389 (and the late window C-20261119-162440-296dad0), and
  C-20261119-144545-c606492, C-20261119-155434-8563453 with analysis
  C-20261119-161930-acd257b (T7): f = 1.029 and 1.063 (late window 1.036, 1.066), literal
  statistic 0.994 and 1.027; T7 rows f_S = 1.0232 +- 0.0039 (k lambda 0.1), 1.0174 +- 0.0047
  (0.2), 1.041 +- 0.011 (0.4); extrapolated kappa/kappa_1 = 1.019 +- 0.004. The isobaric
  reference that the figure recomputes with `heat/scripts/isobaric.py` at the fitted f
  reproduces the analysis's rms residual (0.0030 and 0.0023 per unit area) to 1e-6; a
  larger difference means the reference module changed after the analysis run.
- P5 `fig_onsets` from runs C-20261119-151502-cb831a8 (King family, `rv_king_onset.json`),
  C-20261115-165315-7b473b8 (thermal core b = 0.1, fluid onsets), C-sidm-20261115-120722-38ab057
  (thermal sequence) and C-20261115-170742-84990ed (particle models): King binding-energy
  maximum y0 = 0.334032, Juttner fluid onset y0 = 0.32143 (central lapse 0.6707), onset with
  Gamma = 1 + p/u at y0 = 0.37206; CC2 (y0 = 0.314) and CC1 (0.33403) on either side of the
  Juttner onset; thermal core: maximum Z(0) = 0.54041, Juttner onset (energy-matched
  temperature) 0.53306, at theta = p/n 0.53170, with 1 + p/u 0.63482. In the frequency
  panels the normalised omega_0^2 crosses zero at these onsets.
- P6 `fig_cluster` from the card runs C-20261115-171058-c26cfad, C-20261115-171059-4b70228,
  C-20261115-171059-35441e3 (histories `cc.nrpic.hst`): central lapse minus the control's
  first below -0.01 at 44.25 M (cc1_kn10), 46.0 M (cc2_kn10), 20.25 M (cc1_kn1), 21.25 M
  (cc2_kn1) (as run C-20261119-151944-08f3220); alpha_min < 0.3 at 184.25, 206.75, 72.5,
  77.75 M; the controls' central lapse rises by at most 0.0334 (CC1) and 0.0185 (CC2) above
  its first value. The figure states scouting, one seed, release operator.
- P7 `ledger.py`: the new rows hold every number the G1 sections quote, each with its run
  id; no G1 number appears in the main text without a ledger row (checked by reading the
  text against the table after compiling).
- P8 Both schematics are drawn by `paperfig.py` (copy unchanged, sha256 0c73c7e3...), no
  data read.

Refuted if any number above differs beyond its printed digits, if a checksum fails, or if a
G0 output changes.
