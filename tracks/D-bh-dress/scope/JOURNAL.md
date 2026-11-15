# JOURNAL of the G0 scoping package (tracks/D-bh-dress/scope)

Append-only, newest at the bottom. Predictions are written before a run, outcomes after.

## 2026-11-15T11:58Z  helper (G0 scoping)  run D-bh-dress-<pending>

did: read the brief by the ranges of the task (30-68, 232-238, 279-313, 394-405, 766-783,
834-860), CLAUDE.md, the charter to "Owners", decision 0010, the wave-2 initial-data note
and the orchestrator's derivations; fetched and read 15 arXiv sources (REFERENCES.md);
read docs/TESTLOG.md and docs/results_cluster_test.md for the measured behaviour of
particle clusters around black holes and for the measured costs.

Prediction for the scoping calculation `scoping_estimates.py`, written before it runs.
Set-up: Newtonian cold radial shells around a point mass M in an Einstein-de Sitter
background, starting at t_i = 2/(3 H_i) with the unperturbed Hubble velocity, G = c = M = 1,
epsilon = H_i M in {0.003, 0.01, 0.03, 0.1}. Before turnaround the shells do not cross, so
each shell is a radial Kepler orbit with the mass it encloses; the script computes the
turnaround of every shell twice, in closed form and by integrating the equation of motion.

1. The two methods agree: |t_ta(ODE)/t_ta(closed form) - 1| < 1e-6 for every shell.
   Refuted by a larger difference (an error in one of the two).
2. Energy of a shell: E = -M/r_i exactly (the background terms cancel), so r_max = r_i
   (1 + M_b/M), with M_b the background mass inside r_i.
3. Growth of the mass that has turned around, in my derivation (small delta_i limit of
   item 2): M_b,ta / M -> (4/(3 pi))^(2/3) (a/a_i) = 0.5648 (a/a_i), the same as the
   linear growing mode (3/5 of the initial contrast) reaching the top-hat turnaround
   contrast 1.0624. Prediction: the measured ratio M_b,ta / (M a/a_i) is within 1 percent
   of 0.5648 for a/a_i > 100 for every epsilon; it is independent of epsilon in these
   units. Refuted if the asymptotic coefficient differs by more than 1 percent or depends
   on epsilon.
4. Turnaround radius: r_ta / M -> (2/epsilon^2)^(1/3) (0.5648 a/a_i)^(4/3), i.e.
   r_ta proportional to t^(8/9); the logarithmic slope d ln r_ta / d ln a is within
   1 percent of 4/3 for a/a_i > 100. The frozen-in density (background density at the
   turnaround time, the estimate of arXiv:1901.08528 eq. (profile)) then falls as r^(-9/4).
   Refuted if the slope of ln rho_ta(r_ta) differs from -9/4 by more than 1 percent there.
5. Within one doubling of a (the length of a first null-test run) the decaying-mode
   transient is not negligible: the coefficient of item 3 is off by more than 10 percent
   at a/a_i = 2. (If it is within 10 percent already at a/a_i = 2, the transient is
   smaller than I think.)
