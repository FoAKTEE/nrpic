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

## Entry 2 (2026-11-19, before the run): P1, test particles into a fixed black hole (processors)

Set-up (`inputs/p1_fixed_bh.athinput`, `p1.py`): Schwarzschild M = 1 in Kerr-Schild
coordinates, static mesh metric (dx = 0.25 M, +-18 M) and, as a second case, the analytic
metric; executable `scratch/core/exe/core_requests-adf/athena_cpu` (removal record and
flux spheres; sha256 17ee5e28... in its COMMIT file); 3000 particles of m = 1e-4 (seed
20261119): A 2000 at rest relative to the static observers, uniform in volume over
3 <= r0 <= 14 M; B 600 from the apocentre r0 = 12 M with 0 <= L <= 3.98 M, kept 0.03 M
away from L_crit = 3.5777 M (my bisection on the effective potential); C 400 radial
E = 1 inflow from 14-16 M. Spheres r = 2 M (the horizon), 3 M, 8 M; alpha_exc = 0.65
(r_exc = 1.4632 M); dt = 0.05 M; tlim = 400 M; acc.hst every cycle.

Exact references (`exact_ks.py`, computed from the particle file before the run; numbers
from a development evaluation of the same code): 2935 captured (A 2000, B 535, C 400),
65 bound orbits with pericentres 5.82-11.52 M; all 2935 cross r = 2M by t = 174.8 M and
reach r_exc by 176.3 M; removal lags the horizon by 0.78-1.49 M; sum of m E over the
captured particles 0.26748510; sphere 3 M: 2935 in, 0 out; sphere 8 M: 2584 in, 28 out.

Predictions:
1. 2935 removal records per case, all reason 2, the tags equal to the captured set; no
   particle leaves the mesh (n_escaped = 0); 65 particles alive at the end.
2. |E_rec/E_exact - 1| <= 2e-5 on the mesh metric, <= 5e-6 on the analytic metric (T3
   gave 1.15e-5 and 3.5e-6 for radial infall; B's whirling near-threshold orbits may be
   worse: I allow 5e-5 for species 1 on the mesh and call it a failure above that).
3. Every record time in [t_exc, t_exc + dt].
4. Spheres: the counts equal the exact counts at every record except within one step of
   an exact crossing; final in/out counts exactly 2935/0, 2935/0, 2584/28; sum m E through
   r = 2M equals the exact 0.26748510 to 2e-5 relative.
5. The horizon sphere (r = 2M) reproduces the exact horizon flux at every record to within
   the crossings of one step (no record outside [F_exact(t - dt), F_exact(t)] beyond 1e-9).
6. compare() with the exact horizon history: no bracket violation above 3 sigma (sigma =
   1e-5), closure below 2e-5 in magnitude at 400 M; with the growth scaled by 0.97 the
   violation exceeds 3 sigma (deficit 8e-3 M); with the exact history delayed by 2 M
   (longer than the 0.78-1.49 M lag) it violates the lower bound F_rem: the comparison
   detects a horizon that responds too late, not only one that grows too little.
Refuted by any of these failing; a failure of 6 with 1-5 holding would mean the bracket
argument itself is wrong.

## Entry 3 (2026-11-19, before the analysis): ES-1 and V-1 (card runs of wave 2) through the tools

Data: ES-1 D-20261115-172726-60ba4c2 and V-1 D-20261115-172730-c6d151b (release core-v0.3,
no removal record; `es.nrpic.hst` has n_excised, m_excised; `traj.bin`/`trajmet.bin` hold
the 140 tracers, m = 1e-30, every 8 cycles), data set D-20261115-170213-d2c2131
(`es/es.json`: tracer groups 0-3 at R0 = 6, 10, 20, 28 M inside the bubble, LTB energies
E_LTB = -1/6, -0.09997, -0.0375, -0.00449). The es_finish helper analyses these runs for
the null test; this entry only applies the flux tools to them.

(a) Null comparison, NOT blind: I have seen the finder masses of both runs at t = 0, 20,
..., 199.5 M while checking the file format (ES-1 1.000955 at 100 M and 1.000614 at
199.5 M; V-1 1.000937 and 1.000801). Expected from those rows: flux m_excised = 4.2e-29
(tracers only, no dust enters the bubble); dM_ES(199.5) - 0 = -3.4e-4 against a V-1
envelope of about 1.4e-4 from t0 = 100 M, i.e. a bracket violation near 2.4 sigma at the
end. Recorded as an application of the tool, not as a test.

(b) Blind test of the energy the code reports in an evolving gauge. In the bubble the
spacetime is exactly Schwarzschild of mass M (Birkhoff), so each tracer has the conserved
Killing energy E_K = (1 + 2 E_LTB)^(1/2) = 0.816497, 0.894457, 0.961769, 0.995500 for
groups 0-3. The code's E = alpha W - beta^i u_i (computed here from traj.bin and
trajmet.bin at the tracer) is -u_t of the code's time vector, which equals the Killing
vector only where the gauge is stationary AND normalised to the Schwarzschild time; 1+log
slicing in this data drives the lapse away from 1 at large radius (dust K < 0; the
transition region of the f-slice has K != 0 in V-1 too), so I predict:
1. at t = 0, E_code = alpha_0(R0) (u_i = 0, W = 1) = psi^-2, not E_K;
2. at excision E_code differs from E_K by more than 1 per cent for at least one of
   groups 0-2, in both runs, with E_code > E_K where the lapse beyond the tracer has risen
   above 1 [JUDGEMENT];
3. E_code is not constant along a tracer path while the gauge evolves (variation above
   1 per cent over the first 50 M).
Refuted if E_code at excision matches E_K within 1e-3 for groups 0-2 in both runs: then
the code's E would be usable as the horizon flux energy in these runs. Consequence either
way: the G2 flux should use the energy fixed per particle by the initial data (conserved
Misner-Sharp energy of the shell, known per tag) when the code's E is gauge-contaminated.

### Outcome of entry 2 (run D-20261119-144040-3acb22f; analyses D-20261119-144246-238a592 and, with the per-species breakdown, D-20261119-144600-15dcc67; `results/p1_analysis.json`, `figs/p1_fixed_bh.png`, looked at)

Wall time 86 s (mesh) and 9 s (analytic) on one core.
1. HELD: 2935 records per case, all reason 2, the removed tags equal my captured set,
   n_escaped = 0.
2. FAILED in part: max |E_rec/E_exact - 1| by species, mesh 3.7e-5 (A), 1.8e-4 (B),
   8.8e-6 (C); analytic 2.3e-6, 8.4e-5, 2.3e-6. Predicted 2e-5 (mesh), 5e-6 (analytic),
   5e-5 for B on the mesh. The B errors are the same on both metrics and grow with the
   time spent whirling near the unstable circular orbit (figure, top left): they are
   pusher errors at dt = 0.05 M, not interpolation; the A excess on the mesh is confined
   to the earliest removals (r0 near 3 M). Effect on the flux sums: 1.0e-5 relative.
3. FAILED as worded: record time minus exact t_exc, in steps, by species (min, max,
   number early, number late): mesh A (-0.019, 1.004, 9, 3), B (-0.446, 1.042, 11, 4),
   C (-0.010, 1.008, 4, 2); analytic A (-0.0002, 0.9986, 1, 0), B (-0.072, 0.9988, 7, 0),
   C (0.003, 0.9997, 0, 0). So: exact to rounding on the analytic metric except the
   whirling B orbits (phase error), and up to 2 per cent of a step for radial infall on
   the mesh metric (lapse interpolated at r_exc); the B orbits lose up to 0.45 steps.
4. HELD: final counts 2935/0, 2935/0, 2584/28 on both metrics, no record outside the
   one-step tolerance; sum m E through r = 2M 0.26748438 (mesh) against 0.26748510,
   2.7e-6 relative.
5. FAILED as worded (6865 of 8001 records outside [F(t - dt), F(t)] by more than 1e-9):
   the 1e-9 tolerance ignored the accumulated energy errors (7e-7 M at the end). With a
   tolerance of half the smallest m E of one particle, 18 (mesh) and 5 (analytic) of
   8001 records differ by one particle: crossings registered one step off.
6. HELD: exact horizon history: max bracket violation 0.011 sigma, closure 1.04e-5
   (mesh) and 1.06e-5 (analytic); growth x 0.97: 802 sigma, closure -0.030; horizon late
   by 2 M: 1242 sigma. The bracket F_sph(3M) - F_rem is up to 0.017 M wide during the
   main infall (figure, bottom right): at a single time it constrains the growth only to
   that width; the closure after the infall is the sharp test (1e-5 here).
Lesson for the G2 analysis: judge the closure after the inflow has stopped (or the
bracket over windows of the lag), not the instantaneous residual.

### Outcome of entry 3 (run D-20261119-144248-0143469; `results/es_apply.json`, `figs/es_tracer_energy.png`, `figs/es1_null_compare.png`, looked at)

(a) As expected from the rows already seen: excised rest mass 1.4e-29 after t0 = 100 M;
dM_ES(199.5) = -3.40e-4, V-1 envelope sigma = 1.37e-4, max violation 2.6 sigma, inside
3 sigma at all 200 finder times. V-1 alone against the D-pre-4 floor 2.8e-5: dM =
-1.36e-4 at the end, 4.6 sigma, 10 per cent of the times outside 3 sigma (the V-1 drift
after 170 M exceeds the D-pre-4 floor; the null test itself is the es_finish helper's).
(b) Predictions 1-3 HELD, and the size is large:
1. E_code(0)/E_K = 1.0593, 1.0517, 1.0322, 1.0043 for groups 0-3 (= psi^-2/E_K).
2. At excision E_code/E_K = 2.494 (group 0, t = 15 M), 1.654 (group 1, 27 M), 1.347
   (group 2, 178 M) in ES-1; 2.494, 1.370 in V-1 (group 2 not excised there by 200 M).
3. Along the paths E_code varies by 91-143 per cent of E_K over the first 50 M; late
   in the run the ratio of the groups still outside settles near the lapse at the
   bubble probes (about 1.35 in ES-1, 1.22 in V-1 at t = 200 M; figure, right panel)
   [JUDGEMENT: E_code ~ N(t) E_K with N the lapse normalisation of the bubble region].
Consequence [VERIFIED for these runs]: in the moving-puncture gauge of ES-1/V-1 the
code's E = alpha W - beta^i u_i is NOT the Killing energy, not even at late times; the
G2 flux must use the energy fixed per particle by the initial data (`compare.py
--energy_by_tag`), or E measured at a sphere in a gauge that is stationary and
normalised to the asymptotic time. Request to core in the README.

## Entry 4 (2026-11-19, before the runs): ES-F, the first matter run after ES-1 (dust filling the bubble)

Design [JUDGEMENT, derivation in README section "ES-F"]: ES-1's mesh, gauge, finder,
tracer positions and plateau density rho0 = 3.71818e-6 (H = 5.58116e-3/M, eps = H M),
but the bubble filled: dust from a smooth inner edge over 3 <= R <= 5 M (vacuum core
around the horizon, as RUNS.md section 4 of secondary_infall) to ES-1's outer edge
(52-60 M), at rest in the slice with the slicing f^2 = 1 - M/m(R), i.e. every shell has
the Newtonian energy -M/R0: the unperturbed Hubble flow around the seed, the set-up of
the wave-2 secondary-infall reference. Then the spatial metric is exactly Schwarzschild
of mass M (psi = 1 + M/(2 rbar), table u = 0, puncture m_p = M) and the Hamiltonian
constraint reads 4 KL KT + 2 KT^2 = 16 pi rho. Exact growth law (LTB, no shell crossing
before the horizon): M_AH = m(R0) when shell R0 crosses R = 2 m(R0), at its proper time
tau_H(R0) from the cycloid; each particle carries the conserved energy (1 - 2M/R0)^(1/2)
per unit rest mass (used as --energy_by_tag, because entry 3 showed the code's E is
gauge-contaminated). A development evaluation of the generator at hp = 2 M gave
M_AH = 1.0062, 1.0218, 1.0655, 1.1168, 1.1711, 1.2263, 1.2815 at tau = 25, 50, 100, 150,
200, 250, 300 M (the growth law does not depend on hp).

Predictions:
1. Data (hp = 1 M): about 8.5e5 dust particles plus 140 tracers; lattice rest mass equal
   to the continuum rest mass int rho dV_proper to 2e-5 (4.9e-5 at hp = 2); tau_H(R0)
   increases monotonically (no shell crossing before the horizon); growth law identical to
   the numbers above.
2. Offline constraints (esf_check.py), maximum over 0.6 <= rbar <= 330 M between rows:
   Hamiltonian residual converges at order 4 +- 0.5 from drbar = 0.04 to 0.02 to 0.01
   (four-point Lagrange interpolation of KL, KT); momentum residual (derivative of the
   interpolant) at order 3 +- 0.5. Refuted if either residual does not fall or the order
   is below 3 (H) or 2 (M).
3. Growth law against the wave-2 Newtonian reference (shells.py, absorbing, capture at the
   fixed r = 2M, core and edge matched in mass): M_LTB(tau) - M_shells(tau) in
   [-1e-4, 2e-3] for tau <= 600 M; positive because the LTB shell is inside the horizon
   at R = 2 m(R0) > 2M, before the proxy captures it (Delta tau below about 2 (m - M)).
4. Processor smoke run of the ES-F input (2 cycles, executable core_requests-adf
   athena_cpu, which has the removal record and the flux spheres): reads the table and
   all particles (np = 140 + n_dust); int_E = sum m W = sum m at t = 0 to 1e-12 relative;
   finder mass at t = 0 equal to 0.9924 +- 0.002 (ES-1 gave 0.99239 for the same
   Schwarzschild interior at the same resolution); acc.hst with three spheres, no removal
   record; history finite. The constraint norms at t = 0 are recorded against ES-1's smoke
   run D-20261115-172413-6412daf without a criterion (the 1 M lattice deposited on the
   M/8 to M/2 levels near the hole is noisier than ES-1's dust on 1-2 M cells).

### Outcome of entry 4, items 1-3 (data D-20261119-145022-2208a19, checks D-20261119-145026-2f11618; `results/esf.json`, `results/esf_check.json`, `results/esf_growth.csv`, `figs/esf_data.png`, `figs/esf_check.png`, looked at)

1. HELD: 850584 dust particles + 140 tracers; lattice rest mass 2.8156001 against the
   continuum 2.8156013 (-4.3e-7); lattice Misner-Sharp sum against D_tot = 2.7386556
   (-4.1e-7); tau_H monotonic; M_tot = 3.7386556 M; growth law identical to the
   development numbers.
2. HELD: max Hamiltonian residual / (16 pi rho0) = 7.1e-6, 4.9e-7, 3.2e-8 at drbar =
   0.04, 0.02, 0.01 (orders 3.86, 3.96), largest at the inner edge (rbar 2-4 M); momentum
   residual 3.3e-6, 4.1e-7, 4.5e-8 (orders 3.03, 3.17). The table (drbar = 0.02) is
   exact to 5e-7 of 16 pi rho0 between rows.
3. FAILED in size, held in sign: M_LTB - M_shells lies in [0, 2.9e-3] for tau <= 600 M
   (predicted [-1e-4, 2e-3]); 1.2e-4, 2.2e-4, 4.7e-4, 7.6e-4, 7.9e-4, 1.3e-3, 1.6e-3,
   2.0e-3, 2.5e-3 at tau = 25, 50, 100, 150, 200, 250, 300, 400, 600 M. The difference
   grows with the hole mass, as the capture radius 2 m(R0) of the exact solution moves
   out from the fixed 2M of the proxy; my estimate Delta tau ~ 2(m - M) was too small at
   late times. The wave-2 reference with fixed capture radius is therefore good to 0.25
   per cent of the mass in this run; the exact LTB law is the prediction of record.

## Entry 5 (2026-11-19, before the run): esf_analyse.py on a synthetic ES-F run

`t_esf_synth.py` builds a run from the exact LTB solution of the ES-F data (D-20261119-145022-2208a19):
code time t = tau/1.4, finder mass = exact growth law plus Gaussian noise of 1e-5, every
dust shell removed (reason 3) 30 per cent of the way from the horizon to the centre in
proper time, with the code energy 1.35 E_K (the gauge factor of entry 3), a flux sphere
at R = 5 M summed with the same contaminated energies; then esf_analyse.py, once on the
exact history and once with the growth scaled by 0.97. Predictions:
1. Exact history, initial-data energies: max bracket violation below 4.5 sigma (noise of
   1 sigma at 401 finder times; sigma = finder tolerance 1e-5, no control) and at least
   98 per cent of the times inside 3 sigma; per label M_AH(t_rem) - m(R0) >= -4.5e-5;
   no proper time outside [tau_H, tau_0].
2. Exact history, code energies: the lower bound F_rem exceeds dM by about 35 per cent of
   the accreted mass at the end: violation above 1000 sigma. (This is the failure the
   initial-data energies avoid.)
3. Growth x 0.97, initial-data energies: violation above 100 sigma (a deficit of
   about 5e-3 M at the end against a removal lag worth about 5e-4 M); per label minimum
   M_AH - m(R0) below -1e-3.
Refuted if 1 fails (then the analysis or the LTB labelling is wrong) or 2 or 3 pass
(then the comparison cannot see a 3 per cent or a gauge-factor error).

### Outcome of entry 5, first run (D-20261119-145851-944d6fd)

61592 shells removed, 849952 particles cross the sphere. Prediction 1 FAILED: with the
exact history and initial-data energies the bracket is violated by up to 91 sigma and
only 90 per cent of the times lie inside 3 sigma, while the per-label bound holds
(min M_AH(t_rem) - m(R0) = +6.3e-6) and no proper time is outside [tau_H, tau_0].
Predictions 2 (code energies: 8938 sigma) and 3 (growth x 0.97: 837 sigma, per label
-7.2e-3) HELD. Candidate cause [JUDGEMENT, to be tested by the rerun]: the upper bound
F_sph counts only matter that crosses the sphere after t0; the dust that starts inside
the sphere (here 3 <= R0 < 5 M, about 1e-3 M of Misner-Sharp mass, 100 sigma) reaches
the horizon without crossing it. The same defect would have hit the real ES-F run (dust
from R = 3 M, sphere at coordinate radius 5 M). Change: compare() adds the energy
content of the sphere at t0 to F_sph (`content0`); esf_analyse.py computes it from the
particle file for t0 = 0 (and checks its rest mass against m_inside of acc.hst); the
synthetic sphere sits at isotropic radius 5 M (areal 6.05 M) so that "inside" means the
same in both.

## Entry 5b (before the rerun)

Predictions for the rerun with the content term: 1 now holds (max violation below
4.5 sigma, at least 98 per cent inside 3 sigma); 2 and 3 still hold (above 1000 and
100 sigma); content check: the rest mass inside isotropic radius 5 M from the particle
file equals the synthetic m_inside to 1e-12 relative. Refuted (cause wrong or another
defect) if 1 still fails.

### Outcome of entry 5b (D-20261119-150029-06e4f7f)

Prediction 1 FAILED again, unchanged (91 sigma, 90 per cent inside 3 sigma): the cause
named in entry 5 was wrong. I had not checked which bound was violated before naming
it. A look at the synthetic run (development evaluation of compare() on its files): all
39 violations are of the LOWER bound, F_rem > dM by up to 9.1e-4 M (t = 193: F_rem =
0.24951, dM = 0.24860), none of the upper bound. The content term itself is right (the
sphere held 534 particles, rest mass 3.3177e-3, equal to the synthetic m_inside to
1e-16; m E_K 2.584e-3) and stays. New candidate cause: the synthetic finder history is
the CONTINUUM m(R0), while F_rem sums the LATTICE particles; the cumulative lattice sum of
m E_K up to a label differs from the continuum D(R0) by the lattice-counting error (of
order 1e-3 M at R0 ~ 25 M). The same mismatch would make the per-label criterion against
the continuum m(R0) fail in the real run, where the hole accretes the lattice.
Change: the per-label bound uses the lattice sum m_disc(R0) (esf_analyse.py reports the
continuum one too and delta_lat = max |m_disc - m|); the synthetic truth is the lattice
accretion (case exact), with the continuum truth kept as a third case.

## Entry 5c (before the rerun)

1. Case exact (lattice truth): max violation below 4.5 sigma, at least 98 per cent of the
   times inside 3 sigma; per label M_AH - m_disc >= -4.5e-5.
2. Case continuum_truth: lower-bound violations of up to about 9e-4 M (about 90 sigma)
   as in 5b; delta_lat of order 1e-3.
3. Code energies and growth x 0.97: above 1000 and 100 sigma as before.
Refuted if 1 fails: then the lattice is not the (only) cause.

### Outcome of entry 5c (D-20261119-150219-c40d908)

1. Bracket HELD with the lattice truth: max violation 3.06 sigma, 99.75 per cent of the
   401 times inside 3 sigma (noise of 1 sigma). Per-label part FAILED: min M_AH - m_disc
   = -4.9e-4 (predicted >= -4.5e-5). Candidate cause: M_AH at the removal time is
   interpolated linearly between finder samples 0.5 M apart, while the truth is a step
   function that rises by about 7.7e-4 M per 0.5 M of code time here (1.1e-3 per M of
   proper time times 0.7); the real finder samples every 16 cycles, also 0.5 M. Change:
   take the first finder sample at or after the removal.
2. HELD: continuum truth gives the lower-bound violation of 9.1e-4 M (91 sigma) as in
   5b; delta_lat = max |m_disc - m(R0)| = 3.9e-3 M over all labels.
3. HELD: code energies 9017 sigma; growth x 0.97: 773 sigma, per label -7.8e-3.

## Entry 5d (before the rerun)

Case exact: per label min M_AH(next sample) - m_disc >= -4.5e-5 (noise only); the rest
as in 5c. Refuted if the per-label minimum stays below -4.5e-5.

### Outcome of entry 5d (D-20261119-150306-d0e692e; `results/t_esf_synth.json`, `figs/synth_exact_bracket.png`, `figs/synth_exact_growth.png`, `figs/synth_continuum_bracket.png`, looked at)

HELD: case exact, bracket max 3.06 sigma (99.75 per cent inside 3 sigma), per label min
M_AH(next sample) - m_disc = -2.7e-5 (noise), no proper time outside [tau_H, tau_0];
growth x 0.97: 773 sigma and -7.7e-3 per label; code energies 9017 sigma; continuum
truth: 91 sigma at the lower bound, per label -9.1e-4 against m_disc. So the analysis of
the ES-F run, as it stands now, (a) passes an exact lattice history with finder-like
noise, (b) rejects a 3 per cent growth deficit and the gauge-contaminated code energies,
(c) needs the lattice sums, not the continuum m(R0), for anything sharper than
delta_lat = 3.9e-3 M, and (d) has a loose upper bound (F_sph - F_rem reaches 0.1 M at
200 M) while the sphere sums use the code's E: the crossing record requested from core
would make it tight. Three of my predictions in this entry failed before the analysis
was right (content term not the cause; lattice against continuum; sampling of the
finder); the record above keeps them.

### Outcome of entry 4, item 4: processor smoke runs (ES-F D-20261119-145325-934efd1, V-0 D-20261119-145332-744c881, reader check D-20261119-151910-cc05828)

HELD. Both inputs run two cycles to t = 0.0625 M with core_requests-adf athena_cpu (setup
about 3 min, 1182 s and 1089 s of processor time on a machine with load ~95; ES-F 24 GB
resident). ES-F at t = 0: np = 850724, sum m = 2.8156001402939 (the lattice rest mass),
int_E / sum m - 1 = -5.3e-14; finder mass 0.991521 (prediction 0.9924 +- 0.002; V-0 the
same 0.991521, so the dust does not change the finder's start value); acc.hst with three
spheres, sphere 1 (r = 5 M) holds 534 particles of rest mass 3.317710343e-3, equal to
the count from the particle file in esf_analyse.py to 2e-18; no removal record; no
unconverged push. Constraint norms (z4c.user.hst, squared, chi >= 0.0625) at t = 0:
H 8.40e-3, M 4.04e-4 (ES-F); H 6.50e-3, M 0 (V-0); ES-1's smoke run had H 9.17e-3,
M 4.68e-4; at t = 0.0625: H 7.88e-3 (ES-F), 6.31e-3 (V-0). Recorded without a criterion,
as predicted; the 1 M lattice near the hole did not raise the start norms above ES-1's.
No figure for this item: two cycles hold no time evolution worth plotting; the t = 0
numbers above are read from the files listed.

## Entry 6 (2026-11-20 14:23 PST, wave 3, a second helper who did not build ES-F): second-agent check of the ES-F construction, before any card time

Script: `check_esf_construction.py` (written here; it imports none of esf_data.py,
es_model.py, fluxio.py; density profile re-implemented from the README's statement, the
step S(x) = 1/(1 + exp(1/x - 1/(1-x))), rho0 = 3.718183334770104e-6 of ES-1's data
`es/es.json` of D-20261115-170213-d2c2131; own readers of the format-2 table and the
particle file; own quadrature with scipy.integrate.quad).

Part A (sympy) was evaluated once during development of the script before this entry was
written, so it is NOT blind: every identity reduced to 0 (KL = KT + R KT'/R' = d(R KT)/dR,
theta/phi components 0; Gamma^2 = (R - 2m(1-f^2))/R and = 1 - 2M/R for f^2 = 1 - M/m;
the isotropic psi = 1 + M/(2 rbar) has the same Gamma and R_3 = 0; R_3 = 0 on the slice;
4 KL KT + 2 KT^2 = 4 D'/R^2; Misner-Sharp mass of the data = M + D; LTB Einstein tensor
G^tau_tau = -8 pi rho with rho = m_r/(4 pi R^2 R_r), others 0; E = -M/R0 both from
Gamma^2 = 1 + 2E and from R_tau^2 = 2m/R + 2E with R_tau = -R KT; cycloid satisfies the
energy equation). The registered run repeats it; prediction: the same zeros.

Part B (numbers; blind, not evaluated before this entry). Predictions:
1. Table: format 2, exterior zero, u = 0 and betar = 0 at every row, K = 0 on the inner
   sheet (rbar < M/2), rbar_max 345 > mesh corner 332.6; KT and KL at every row with
   R >= 2M equal my closed forms -(2D/R^3)^(1/2) and d(R KT)/dR to <= 1e-11 of max|KT|
   (17 printed digits; the two quadratures agree to ~1e-13 relative).
2. Hamiltonian constraint with the table's own KL, KT at the rows: |4 KL KT + 2 KT^2 -
   16 pi rho| <= 1e-9 of 16 pi rho0; momentum constraint by fourth-order differences of
   the rows (truncation only) <= 1e-5 of max|KT| [JUDGEMENT: the steps have large high
   derivatives at the edges].
3. Particles: 850724 records, u_i = 0 exactly, tracers 140 with m = 1e-30 at their R0 to
   1e-12; dust on the half-integer lattice of h = 1 M, the same set of points as my own
   enumeration, m = rho psi^6 h^3 to 1e-12 relative.
4. energy_by_tag = (1 - 2M/R0)^(1/2) to 1e-14; labels: m(R0) = M + D(R0) to 1e-10 (all
   labels through a dense grid, a sample of 300 by direct quad), rest masses identical to
   the file, tau_H and tau_0 equal to my cycloid to 1e-10 relative; the closed-form
   tau_H equals a direct quadrature of dtau = dR/|R_tau| to 1e-7 relative (singular
   endpoint at R_max); tau_H(R0) monotonic.
5. Totals: D_tot = 2.7386556 (esf.json) to 1e-11; continuum rest mass 2.8156013 to
   1e-10; lattice sum m E_K / D_tot - 1 = -4.1e-7 and lattice rest / continuum - 1 =
   -4.3e-7 (the builder's numbers, reproduced to 2 digits).
6. Growth law: esf_growth.csv rows and esf.json M_AH(tau) at tau = 25 ... 600 M equal mine
   to 1e-9.
7. Input esf_dx8.athinput: table + puncture comp1_mass = 1.0, lapse precollapsed, shift
   zero, particle file of the data run, metric_drvts = interpolant, ah_exc_factor = 0.8.
Verdict rule: WRONG if any symbolic identity is non-zero, the table differs from the
closed forms by more than 1e-9 of max|KT|, a particle mass or energy by more than 1e-10,
a label or time by more than 1e-8, or the lattice set differs; then no card run and the
package is spent on fixing esf_data.py. A failure of the looser thresholds above (by less
than these) is recorded as a failed prediction without changing the verdict.

### Outcome of entry 6, first run (D-20261120-222314-ed5d325; 43 s on one core)

Part A: every identity reduced to 0, as in development (A1 to A4, the cycloid's start,
horizon and R_max conditions; dm/dmu = Gamma).
1. HELD: format 2, exterior zero, 17251 uniform rows, u = betar = 0 at every row, K = 0 on
   the inner sheet, rbar_max 345 > 332.55. FAILED as worded: max |KT_tab - KT_mine| =
   1.29e-10 and max |KL_tab - KL_mine| = 1.63e-7 of max|KT| (predicted <= 1e-11; the KL
   value is above the 1e-9 of my verdict rule). Both maxima sit at R = 3.050 M, the far
   tail of the inner edge, where the table has KT = KL = 0 and mine has D = 7.3e-24,
   KL = -9.1e-10. At the 18 sampled radii with D > 0 (3.2 to 330 M) table and closed form
   agree to <= 8.7e-18 absolute. Development diagnosis (to be registered in the rerun):
   the builder's step is evaluated as 0.5 (1 - tanh(g/2)), which rounds to 0 below
   S ~ 1e-17 and loses relative precision below S ~ 1e-8 (1.2e-8 at S = 3.4e-10,
   R = 3.088 M); my S uses expit. So its density is exactly 0 for R <~ 3.05 M and mine
   is not.
2. HELD: Hamiltonian residual with the table's own KL, KT 7.3e-16 of 16 pi rho0 at every
   row. FAILED: momentum residual by fourth-order differences 4.9e-5 of max|KT|
   (predicted <= 1e-5); location not recorded by this version.
3. HELD: 850724 records, u_i = 0, species 0, 140 tracers of m = 1e-30 at their R0
   (4.4e-16), dust on the half-integer lattice, the same 850584 points as my
   enumeration. FAILED as worded: max |m / (rho psi^6 h^3) - 1| = 0.25 (predicted 1e-12);
   dust spans R = 3.294 to 59.781 M, so the candidate is the outer tail, where 1 - S
   cancels (in the builder's code and in this version of mine alike).
4. HELD: energy_by_tag equal to (1 - 2M/R0)^(1/2) bit for bit; labels m(R0) to 2.0e-14
   (sample of 300 by direct quad: 9.8e-15); rest masses identical; tau_H, tau_0 to
   6.4e-15; closed-form tau_H against direct quadrature <= 4.4e-12 (20 radii); tau_H
   monotonic.
5. HELD: D_tot 2.7386556250326666 and continuum rest mass 2.815601343446499 equal to
   all digits; lattice sum m E_K / D_tot - 1 = -4.06e-7, lattice rest / continuum - 1 =
   -4.27e-7.
6. HELD for esf_growth.csv (m to 2e-14, tau_H to 4.4e-12, tau_0 3.2e-12, R_max 5.7e-15).
   FAILED as worded for the esf.json summary M_AH(tau): differences up to 8.3e-9 for
   tau <= 200 M and 3.4e-8 at tau = 600 M (predicted 1e-9). Candidate [JUDGEMENT]: the
   summary is np.interp on the 4000-point label grid, mine a root of tau_H(R0) = tau.
   Irrelevant at the 1e-3 level of criterion (iii).
7. HELD: table + puncture of mass 1.0, lapse precollapsed, shift zero, the data run's
   particle file, interpolant, 0.8.
Side numbers: U/(H R) = 0.967, 0.996, 0.9995 at R = 10, 20, 40 M (the "v = H R"
description of the plateau holds to 0.4 per cent from 20 M; the vacuum core lowers it
inside).

## Entry 6b (before the rerun): the cause of the tail differences

Changes: my density now has an outer complement without cancellation (expit); the script
also evaluates the builder's form 0.5 (1 - tanh(g/2)) of the same step (`S_tanh`, written
here from the formula) as the cause test, and reports absolute errors, their locations,
and the lattice set under both forms. Predictions:
(a) with the tanh form, the table equals the closed forms to <= 1e-12 of max|KT| at every
    row, the dust masses equal rho psi^6 h^3 to <= 1e-12 relative, and the lattice set is
    the file's;
(b) with my precise step, the largest table difference is at R < 3.1 M, <= 1e-9 absolute
    in KL; mass differences above 1e-12 relative only at R < 3.2 M or R > 59 M, absolute
    <= 1e-15 rho0 h^3; for 3.2 < R < 59 M <= 1e-12 relative;
(c) the momentum residual by differences is largest at the inner edge (3 < R < 5 M) and
    <= 1e-6 of max|KT| for 6 < R < 50 M;
(d) lattice points that carry dust only with the precise step: few, at the tails, each
    below 1e-14 rho0 h^3.
Refuted if (a) fails: then the data are not the stated construction with the builder's
step, and a defect of the construction is not excluded.
