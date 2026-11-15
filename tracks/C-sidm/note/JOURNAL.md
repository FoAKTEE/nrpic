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
