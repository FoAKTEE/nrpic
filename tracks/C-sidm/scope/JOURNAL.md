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

## 2026-11-15 11:54 UTC, outcomes

Development invocations (unregistered, outputs in `scratch/C-sidm/tmp/dev_*`, not quoted
anywhere) were used to debug the scripts and figure layout; the numbers below come only
from the three registered runs, which ran on commit eb8b752.

P1, run `C-sidm-20261115-115344-eb8b752` (3.3 s, one core): CONFIRMED.
- All five models of Wu and Most reproduce their printed z_c, R/M and M_0/M to the last
  printed digit (e.g. y_c = 0.605: z_c 0.59198, R/M 5.750187, M_0/M 1.0351713 against
  0.592, 5.7502, 1.035171).
- First maximum of E_b/M_0 at y_c = 0.67961, z_c = 0.45529, E_b/M_0 = 0.036058,
  R/M = 6.5524 (compactness 0.1526); first zero at y_c = 0.39045 (z_c = 1.1112).
  Inside the predicted bracket (0.605, 0.756).
- New observation, not predicted: y_c = 0.756 and 0.605 have equal E_b/M_0 to 2e-4
  relative (0.033983 and 0.033976): the two models of the first paper that bracket the
  threshold sit symmetrically on the two branches, at the same binding energy.
  Figure `figures/fig_seq_monoenergetic.png` (looked at: sequence, markers, maximum line
  as described).

P2, run `C-sidm-20261115-115348-eb8b752` (9.0 s): CONFIRMED, with a margin.
- At w(0) = 0.6, 1.9, 3.2, 4.0515 (b = 0.1) my M, E_rest, eps_b, Z(0), v(0), <gamma>,
  gamma_cr agree with the Table of arXiv:2108.11967 to 8e-5 relative or better; R and C
  differ by 1.6e-4 to 2.5e-3, the size expected from a radial grid of 1e-3 in r-hat.
  Figure `figures/fig_king_check.png` (looked at: all points below the 0.5 percent line,
  R and C the largest).
- Maximum of eps_b at b = 0.1: w(0) = 3.1652, eps_b = 0.035179, Z(0) = 0.5404,
  C = 0.04892, v(0) = 0.5035 c. The paper's "0.0352 at Z(0) = 0.548" is its grid point
  w(0) = 3.2; the true maximum is at Z(0) = 0.540. Within the predicted interval.
- <gamma> = gamma_cr at w(0) = 4.05115 (b = 0.1; paper 4.05150) and 1.73634 (b = 0.2;
  paper 1.73635), gamma = 1.62117 and 1.62278 (paper 1.62117, 1.62278).
- Maxima for b = 0.2, 0.3, 0.5, 1: eps_b = 0.035489, 0.035538, 0.035569, 0.035589 at
  Z(0) = 0.5225, 0.5176, 0.5142, 0.5119.

P3, same run: CONFIRMED.
- At b = 1 the first maximum of eps_b lies at y_0 = 0.33403 and the first zero at
  y_0 = 0.78452; arXiv:2009.08163 gives 0.334 and 0.784. The King model of 2009.08163 is the
  b = 1 member of the family of 2108.11967; the two references agree with each other and
  with this solver. Figure `figures/fig_king_sequence.png` (looked at: right panel, green
  curve b = 1 peaks on the left dotted line and crosses zero on the right one).

P4, run `C-sidm-20261115-115400-eb8b752` (3.4 s): CONFIRMED by a wide margin.
- With the near-threshold models scaled to M = 200 solar masses and sigma/m = 5 cm^2/g,
  Kn_c = lambda_c/H_c lies between 4.5e-20 (King b = 0.1 at the adiabatic criterion) and
  1.8e-19 (monoenergetic 0.756); for M = 1.9e9 solar masses it is 4e-13 to 2e-12. The
  cross-section per unit mass that would give Kn_c = 1 is 2e-19 to 9e-19 cm^2/g for
  200 solar masses. Figure `figures/fig_knudsen.png` (looked at).
- Requirements of a pairwise Monte Carlo operator at the first paper's step dt = M/16:
  Kn_c = 1 needs 600 to 1600 macroparticles and no subcycling; Kn_c = 0.1 needs
  6e5 to 1.6e6 macroparticles and 2 to 7 collision subcycles; Kn_c = 0.01 needs 6e8 to
  1.6e9 macroparticles (out of reach) and 18 to 65 subcycles.
- Measured costs (figure `figures/fig_costs.png`, looked at): 1.67 s per M (static,
  dx = M/2), 3.28 and 3.71 s per M (static, dx = M/4), 14.2 and 17.5 s per M (adaptive to
  M/16, collapsing models), all at N = 1e4 on one A100; particle work 4.1e-8 s per
  particle and cycle from the 2.1e6-particle periodic run (an estimate: the Z4c share of
  that run is taken from the throughput of docs/TESTLOG.md:46, not measured in it).

## 2026-11-15 12:30 UTC, reading results that change the plan; package closed

- arXiv:2105.05556 (fetched after the runs; it is the "Gunther:2021pbf" of Wu and Most)
  shows that for core-halo families the collisionless threshold can lie beyond the first
  binding-energy maximum, with two stability changes for some models (paper.tex:612).
  The King b = 0.1 family is core-halo (R/H_c = 21-36, run ...115400), so its eps_b
  maximum (Z(0) = 0.540) is treated in SCOPE.md as a lower bound, not as the threshold.
  No run of this package tested this; it is a reading.
- arXiv:2602.17487 has no collision operator (grep of all its files); recorded as a
  brief correction.
- Correction to my commit 5aacad7: its message says 15 sources; REFERENCES.md lists 14
  read at the source.
- Not done here: no AthenaK run; no specification of C-pre-1/C-pre-2; no King initial
  data in the code; collision cost unmeasured.
