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

## 2026-11-15T12:05Z  outcome of run D-bh-dress-20261115-120304-795eee9

Output `scratch/D-bh-dress/D-bh-dress-20261115-120304-795eee9/` (scoping_table.txt,
scoping.json); figure `figs/scoping_estimates.png` (looked at: the four epsilon curves of
the top-left panel coincide, the frozen-in density follows the -9/4 guide beyond a few
turnaround radii of the first shell, the card-hour panel shows the vacuum lines below the
bubble markers).
1. Holds. Largest |t_ta(ODE)/t_ta(closed form) - 1| = 1.6e-8 (eps = 0.003), r_max 1.1e-8.
2. Holds to round-off: max |E r_i / M + 1| = 1.5e-10, the cancellation of the two
   background terms of order (eps r_i)^2.
3. Holds as a limit, fails at the stated threshold: the coefficient is 0.5641 at
   a/a_i = 1000 (0.13 percent below 0.5648) but 0.5581 at a/a_i = 100 (1.2 percent below);
   it enters the 1 percent band only at a/a_i = 121.5. The approach is ~1/a (0.12 and
   0.013 percent... i.e. 1.2e-2 at 100, 1.3e-3 at 1000), the O(M/M_b) terms of r_max and
   of the enclosed mass, not the decaying mode as I had assumed. Independent of epsilon:
   holds (identical to all printed digits for the four values).
4. Holds: d ln r_ta / d ln a = 1.3314 (0.15 percent from 4/3) at a/a_i = 100 and 1.3331 at
   1000; d ln rho_ta / d ln r_ta = -2.2533 and -2.2503.
5. Holds: the coefficient is 0.2627 at a/a_i = 2, 53 percent below the limit; 0.4997 at
   a/a_i = 10. Consequence for the run plan: over one doubling of a the dust that has
   turned around is 0.525 M (M_ta = 1.525 M including the hole), over a quadrupling
   1.63 M; r_ta = 33.4 M (eps = 0.01) and 16.1 M (eps = 0.03) at a/a_i = 2.
Cost model check (not predicted beforehand, recorded as found): the production run
`jeans/n1e4_v19` (matter, AMR, three horizons) took 19476 s for 3.05e7 block-cycles, 1.45
times what the vacuum-puncture rate (9.27e6 zone-cycles/s) gives; matter runs are
therefore costed with the run's own rate 6.4e6 zone-cycles/s.
changed my mind about: the size of the dust region. Marginally bound dust shells evolve
independently, so the Einstein-Straus null test needs only a thick shell outside the
bubble (1.5 R_w), not a ball out to the Hubble radius; that is what makes eps = 0.01 to
0.03 affordable (SCOPE.md, section 7).

## 2026-11-15T12:40Z  helper (G0 scoping)  commits 795eee9..(this)  runs D-bh-dress-20261115-120304-795eee9

Correction to the outcome entry above, item 3: the garbled parenthesis should read "the
relative offset from 0.5648 is 1.2e-2 at a/a_i = 100 and 1.3e-3 at 1000, i.e. it falls
as 1/a".
did: wrote SCOPE.md, REFERENCES.md, README.md; fetched 1707.06302, 1204.3568, 1801.01083
in addition (18 sources read in all).
found: (1) the arXiv sources cite Bertschinger 1985 for two different dress slopes
(1805.09034: 3/2; 1901.08528: 9/4); (2) 1305.2619 has no Kerr numbers, 1707.06302 does;
(3) 2302.07878 itself assigns k = 0 to Kerr, so the null test cannot test the claim;
(4) in the full-NR regime (r_ta = 16-34 M after one doubling at eps = 0.03-0.01) cold dust
is inside the capture cone L < 4 M unless its tangential speed at turnaround is 0.12-0.25:
cold runs measure the growth law, a spike needs dispersion or tidal torques [JUDGEMENT];
(5) the McVittie apparent horizon gives a definitional drift d ln M_AH / d ln a =
-12 (m H)^2 [JUDGEMENT, derived here, needs a second agent].
open: no second-agent review; the cold-infall growth law 0.356 (a/a_i) M is derived, not
computed; the cost model's two hand-evaluated rows (SCOPE.md section 7, marked).
