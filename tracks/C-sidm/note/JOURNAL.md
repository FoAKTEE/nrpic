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
