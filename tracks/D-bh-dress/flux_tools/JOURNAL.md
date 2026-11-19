# JOURNAL of flux_tools (Track D, wave 3a helper package)

Predictions are written before each test and not edited afterwards; outcomes are appended
below them, also when a prediction fails. Labels: [VERIFIED] measured here (run id),
[BACKGROUND], [JUDGEMENT], [TO VERIFY]. Units G = c = 1, M = initial hole mass.

## Entry 0 (2026-11-19 06:40 PST): scope

Package: readers of core's accretion diagnostics (branch core/requests-adf, executables
`scratch/core/exe/core_requests-adf/`, `tracks/core/interfaces/REQUESTS_ADF.md` sec. 2.3)
and of the finder, the comparison "horizon mass growth against the integrated m E carried
through the horizon" with an error budget from a vacuum control, tests on core's own
output (T3, T7) and on a processor run of test particles into a fixed hole, and the input
of the first matter run after the vacuum-bubble benchmark (dust filling the bubble) with
its predicted growth law. Card-hours named for this package: none, so 0 card-hours.

Design of the comparison (`compare.py`) [JUDGEMENT]: a particle is removed (reason 2,
lapse below `alpha_exc`; reason 3, inside 0.8 r_AH) only after it has crossed the
apparent horizon, so the cumulative m E of the removal records, F_rem(t), is a lower bound
of what has crossed by t; the net inward m E through a coordinate sphere outside the
horizon, F_sph(t), is an upper bound for monotone infall. The finder's dM(t) must lie in
[F_rem, F_sph] within the budget sigma(t) = (floor(t)^2 + mass_tol^2)^(1/2), floor(t) the
envelope of |dM| of the matched vacuum control (or a constant floor from D-pre-4).
E = alpha W - beta^i u_i is the conserved -u_t only where the gauge is stationary; the
bracket makes the lag between horizon crossing and removal explicit instead of modelling it.

## Entry 1 (2026-11-19, before the run): readers on core's T3 output

Data: run core-20261115-160245-727e96a (`scratch/core/core-20261115-160245-727e96a/`,
cases mesh, mesh_rs, analytic; input problems/tests/accretion_static.athinput of
core/requests-adf; particle file acc_static.nrp in each case directory). My own exact
references (`exact_ks.py`, written without reading core's reference code beyond the
particle set-up): E, L from the particle file and the exact Kerr-Schild metric; removal
radius r_exc where alpha_KS = 0.62; Kerr-Schild time of the first passage through r_exc
and through the spheres by quadrature.

Predictions:
1. Readers: 192 removal records in each case, all reason 2, species 0-2 only; the record
   count equals n_excised of the last acc.hst row and of the last nrpic.hst row; the sum of
   m over the records equals m_excised of both histories to 1e-15.
2. Content identity at every acc.hst record and sphere: n_inside = n_inside(0) + n_in -
   n_out - (removed inside that sphere), mass likewise to 1e-15 (all removals happen inside
   r = 4 M, so every removal counts for both spheres).
3. Energies: E of each removal record within 2e-5 of my exact E of that tag (mesh metric,
   dx = 0.25 M) and within 5e-6 (analytic metric); sum of m E of the records within 1e-5
   relative of the exact sum 0.1655716 (core's reference, which I recompute independently
   and expect to agree to 1e-10).
4. Times: each record time lies in [t_exc, t_exc + dt] with dt = 0.05 (removal at the start
   of the step after the crossing), t_exc my exact first-passage time through r_exc
   (expected 19.287, 28.926, 45.460 M for r0 = 6, 8, 11 from core's JSON; I predict my
   quadrature reproduces them to 1e-6).
5. Sphere fluxes: sphere 4 M: 192 in, 0 out, net m E = exact sum of the shells; sphere
   10 M: in = 64 (r0 = 11 shell) + orbit inward passages up to t = 800, out = orbit
   outward passages; counts equal to my exact orbit crossing counts; the step of each
   crossing is not resolved by acc.hst (records every 20 cycles), so I compare the
   cumulative counts at record times against the exact counts with a tolerance of one
   record interval (1 M).
6. The restart case (mesh_rs) gives the same removal records as mesh, byte for byte, and
   the same acc.hst rows.
Refuted by: a count mismatch, an identity error above 1e-12, an E error above 2e-5 (mesh)
or 5e-6 (analytic), a removal outside its predicted step, or a crossing count that differs
from the exact one by more than one record interval.
7. compare() on T3 (mesh) with a synthetic horizon history M_syn(t) = 1 + sum of m E_exact
   over particles whose exact passage through r = 2M (the horizon of the fixed hole) lies
   before t, sampled every 0.5 M, sphere 4 M as the upper bound, sigma = 1e-5 (finder
   tolerance only): no bracket violation beyond 3 sigma at any time (the code's E errors,
   at most 2e-5 relative on 0.17 M, are far below 3e-5 M), closure (dM - F_rem)/F_rem at
   800 M below 1e-4 in magnitude; the same history with the growth scaled by 0.95 violates
   the bracket by more than 3 sigma at the end (a deficit of 8e-3 M). Refuted by either
   outcome failing: then the comparison logic or the bound argument is wrong.

### Outcome of entry 1 (run D-20261119-143610-818e89f; `results/t_core.json`, `figs/t_core_t3.png`, `figs/t_core_t7.png`, both looked at)

All seven predictions held [VERIFIED, run above]:
1. 192 records per case, all reason 2, species 0-2; n_excised 192 in acc.hst and
   nrpic.hst; sum m = 0.192 in records and both histories (equal to 1e-16).
2. Content identity exact in the counts (0) and to 9.0e-17 in mass, both spheres, all cases.
3. max |E_rec/E_exact - 1| = 1.15e-5 (mesh, mesh_rs), 3.47e-6 (analytic); sum m E of the
   records 0.16557095 (mesh), 0.16557102 (analytic) against my exact 0.16557158518 (equal
   to core's reference to the last printed digit); relative 3.8e-6 and 3.4e-6.
4. My exact removal times 19.2874140, 28.9255690, 45.4597570 M agree with core's to
   3e-12; the records lie 0.25, 0.49, 0.80 steps after them, i.e. inside [t_exc, t_exc+dt].
   Exact horizon (r = 2M) passages: 18.0856, 27.7656, 44.3286 M, so the removal at
   alpha_exc = 0.62 lags the horizon by 1.13-1.20 M of Kerr-Schild time.
5. Sphere 4 M: 192 in, 0 out; sphere 10 M: 84 in, 16 out, equal to my exact orbit
   counts; no acc.hst record outside the one-interval tolerance.
6. mesh_rs: removal file identical byte for byte, every acc.hst column identical.
7. Synthetic horizon: max violation 9.7e-4 sigma (none), closure 3.8e-6; growth x 0.95:
   violation 828 sigma, closure -0.050. The bracket logic separates a 5 per cent deficit.
T7 (core-20261115-163129-a200caf): the removal file holds 0 records (no particle removed in
0.75 M), 1021 in / 963 out through the tracker sphere, count identity exact, centre equal
to the tracker row of the following time to 5.6e-17 over 24 rows (core's labelling rule
confirmed independently).
