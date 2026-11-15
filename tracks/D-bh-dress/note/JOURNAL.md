# JOURNAL of the note package (helper of D-bh-dress, wave 2)

Append-only. Predictions are written before the scripts that test them run; outcomes after.
The package makes the working note v0, its figures and schematics, the numerical ledger,
a check of the lead's documents against the run outputs, and `stage/G0/STAGE_REPORT.md`.
No simulation is run: every script reads outputs of runs registered in wave 1.

## 2026-11-15T16:58Z  predictions, written before any script of this package ran

Worktree at cbbdfe0 (main merged, up to date). Inputs: the run directories under
`/data/haiyangw/nrpic/scratch/D-bh-dress/` listed in `scripts/common.py`.

- P1 (claims check, `scripts/ledger.py`). Of the numbers that the lead's documents
  (`stage/G0/REPORT.md`, `stage/G1/STATUS.md`, `STATUS.md`, `HANDOFF.md`) state with a run
  id, I check about forty against the run outputs. Expected: all agree to the printed
  digits, with two exceptions I saw while reading the files: (a) "dress 0.625 M_ta" is
  attributed to run D-bh-dress-20261115-123813-97afeea, whose output prints the mass
  inside the outermost caustic, m(lambda_1) = 0.654; the 0.625 is `f_passed` = 0.6247 of
  the analysis run D-bh-dress-20261115-125613-248fdaf; (b) "order 5.8-5.9 in the curvature
  transition" holds for the box "mid transition" of run D-bh-dress-20261115-043406-4df1e76;
  over the whole region 4 < r < 30 M the same run gives 5.3 (H) and 4.7 (M). Refuted if
  more than three further numbers disagree, or if either (a) or (b) turns out to agree.
- P2 (`scripts/fig_floor.py`, my own code on the raw finder output of runs
  D-bh-dress-20261115-121313-284ec4f and -121314-284ec4f). The drift of a centred 20 M
  running mean from 50 to 490 M is +2.95e-4 (M/8) and +3.67e-5 (M/16), as the lead's
  re-check D-bh-dress-20261115-145546-5259f48. Refuted by a difference in the second digit.
- P3 (`scripts/fig_es.py`). The wall column of `es_reference.csv` (run
  D-bh-dress-20261115-043445-b782009) equals the marginally bound closed form
  R_w(tau) = (36^(3/2) + (3/2) sqrt(2) tau)^(2/3) M to 1e-10 relative, and the column "mass
  inside the wall" equals 1 to round-off. Refuted otherwise.
- P4 (`scripts/fig_es.py`). The tracers released at rest at R0 = 6 M and 10 M reach R = 2M
  at the proper times of the radial cycloid from rest, tau = sqrt(R0^3/2M) (eta + sin eta)/2
  with cos eta = 2(2M/R0) - 1 ... written as tau(R) = sqrt(R0^3/(2M)) [arccos(sqrt(R/R0)) +
  sqrt((R/R0)(1 - R/R0))]: 15.0 M and 34.6 M as `first_run_plan.json` says, and the csv
  crosses 2M within its 0.2 M sampling of these times. Refuted by a difference above 0.2 M.
- P5 (`scripts/fig_es.py`, density from the table). The Hamiltonian constraint evaluated
  on the table columns, 16 pi rho = -8 psi^-5 lap(psi) + 4 KL KT + 2 KT^2 with
  psi = 1 + u + m_p/(2 rbar), gives rho = 0 to 1e-9 rho_0 inside the bubble and in the
  exterior, and rho = rho_0 = 3.7182e-6 M^-2 on the plateau to 1e-4 relative (second-order
  differences of a smooth table at drbar = 0.02 M). Refuted by a nonzero density in the
  vacuum regions above 1e-6 rho_0 or a plateau off by more than 1e-3.
- P6 (all figure scripts). Every figure renders without a label cut at the figure edge
  (czstyle overflow check); the manuscript checker reports no hit outside the accepted
  ledger exception of the guide.

## 2026-11-15T17:15Z  outcomes of P1-P5 (run D-bh-dress-20261115-171128-38634d6, registered by hand)

`harness/bin/nrpic-run submit --package tracks/D-bh-dress/note` refused: an untracked
`es.horizon_summary_0.txt` (another helper's AthenaK output) sits in the worktree root.
The run was registered with `scripts/handreg.py` (manifest with the refusal, inputs with
sha256, `sha256sums.txt`). All eight scripts ran cleanly; figures and tables copied into
`figures/` and `tables/`. Every figure was looked at (PNG read): fig_es, fig_constraints,
fig_floor, fig_spike, fig_infall, schem_architecture, schem_timeline.

- P1 holds. 36 statements checked (`tables/claims.md`), 31 agree to the printed digits.
  (a) confirmed: "dress 0.625 M_ta" is `f_passed` = 0.6247 of run -125613-248fdaf; run
  -123813-97afeea prints m(lambda_1) = 0.654 (locator to be corrected). (b) confirmed: orders
  5.88 (H) and 5.76 (M) in the box "mid transition"; 5.29 and 4.69 over 4 < r < 30 M.
  Three further remarks, none a plain disagreement: the 0.02 per cent against the published
  SFW figure holds for the peak (1.5e-5 in height, 1.5e-4 in position), the whole curve
  deviates by up to 2.6e-3; the arrival times 15.0 and 34.6 M of the tracers are the first
  samples of the 0.2 M reference grid after the crossing, the exact values are 14.83 and
  34.44 M; the cost of the vacuum control (about 1.2 card-hours) is a judgement with no row
  in the cost table. Also: REPORT.md:101 cites the simulation run for |dE/E|, |dL/L|, whose
  values sit in the analysis run -125739-a18d74d.
- P2 holds: +2.952888e-4 (M/8) and +3.674327e-5 (M/16), equal to the lead's values to all
  digits. Not an independent method: like the lead, the 20 M mean is taken at its last
  finite point (489.5 and 489.75 M) for "490 M".
- P3 holds: wall against the closed form 6.7e-16 relative; mass inside the wall exactly 1.
- P4 partly refuted. As written (fall from rest) it holds for the 6 M group (closed form
  14.83 M, first sample below 2M at 15.0 M) and fails for the 10 M group (33.70 M against
  34.6 M, 0.9 M off). With each group's own energy from `es.json` (E = -0.09997 at 10 M, an
  outgoing start because K^theta_theta < 0 in the transition) the infall law gives 34.44 M
  and 244.74 M (20 M group), both within the 0.2 M sampling of the reference. The tracers
  start with the expansion of the slice, not at rest; my prediction ignored that.
- P5 refuted in the bubble at the stated threshold, holds elsewhere. Largest |rho| inside
  0.95 x 36 M is 2.2e-5 rho_0 (at R = 31.3 M), above 1e-6. On every second and fourth table
  row it is 8.9e-5 and 3.6e-4 rho_0: a factor 4.0 per doubling, the second-order truncation
  of my own differencing of u, not a property of the data (the offline check of the run
  -042704-f3da881 uses fourth-order differences). Plateau: rho/rho_0 - 1 at most 1.7e-7;
  exterior 3.3e-9 rho_0; -K/H = 1 on the plateau.
