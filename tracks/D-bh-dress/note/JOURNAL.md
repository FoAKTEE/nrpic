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
