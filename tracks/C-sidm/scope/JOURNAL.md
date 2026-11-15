# JOURNAL of the G0 scoping package (tracks/C-sidm/scope)

Helper of owner C-sidm. Predictions are written here before a run; outcomes after it,
also when the prediction fails. Run ids refer to `tracks/C-sidm/runs/<run_id>/manifest.json`.

## 2026-11-15 11:50 UTC, predictions before the three reference computations

Three semi-analytic computations (no simulation; processors only, one core each) support
the parameter ranges of `SCOPE.md`. Written before any of them ran.

P1, monoenergetic sequence (`scripts/seq_monoenergetic.py`, uses `python/nrpic/st_cluster.py`).
- Expect: the five models of Wu and Most (`kb-data/raw/arxiv/2611.12831/v1/src/main.tex`,
  lines 1024-1028) come out with their printed z_c, R/M and M_0/M to the last printed digit;
  the first maximum of E_b/M_0 lies between y_c = 0.756 and 0.605 (`docs/TESTLOG.md`:116).
- Refuted if a printed value differs beyond its last digit, or the maximum lies outside
  that bracket.

P2, truncated Maxwell-Boltzmann (relativistic King) sequence, my own solver of the
equations labelled eq:eos, eq:integrals and eq:tov of arXiv:2108.11967 (main.tex lines
122-145) (`scripts/king_sequence.py`).
- Expect, for b = 0.1 against its Table (main.tex lines 490-503): M-hat and E_rest-hat
  within 0.5 percent, the fractional binding energy within 1 percent, Z(0) within
  0.5 percent, <gamma> and gamma_cr within 0.002 at w(0) = 0.6, 1.9, 3.2 and 4.0515; the
  maximum of the fractional binding energy at w(0) in [2.9, 3.5] with value
  0.0352 +- 0.0003; <gamma> = gamma_cr within 0.005 of w(0) = 4.05.
  The printed radii end in ...001, which suggests a radial grid of 1e-3 in r-hat: R-hat
  and the compactness may differ from mine by up to 0.3 percent without refuting anything.
- Refuted if any of these tolerances fails at a row I check.

P3, cross-check between two references (same script).
- My reading [JUDGEMENT, derivation in SCOPE.md section 3.2]: the King model
  f = (exp(1 - E/E_0) - 1)_+ of arXiv:2009.08163 (paper.tex line 635) is the member b = 1
  of the family of arXiv:2108.11967, with y_0 = -ln(1 - b w(0)).
- Expect: at b = 1 the first maximum of the fractional binding energy at y_0 = 0.334 +-
  0.005 and its first zero at y_0 = 0.784 +- 0.01 (2009.08163, paper.tex line 953).
- Refuted if the maximum or the zero lies outside these intervals; then either my mapping
  or one of the two references is wrong, and the solver must be checked against a third
  source before it is used for initial data.

P4, Knudsen numbers and time scales (`scripts/knudsen_costs.py`).
- Expect: for the fiducial halo of arXiv:2601.17117 (seed of about 200 solar masses at
  horizon formation, sigma/m = 5 cm^2/g, SIDM_MS.tex lines 384 and 476) the central Knudsen
  number lambda/H of a near-threshold model scaled to that mass is below 1e-15 for every
  candidate family: the relativistic core is a fluid.
- Refuted if any family gives Kn_c above 1e-10.
