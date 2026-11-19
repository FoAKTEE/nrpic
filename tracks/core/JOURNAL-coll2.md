# JOURNAL of core, work package coll2 (collisions, second pass)

Append-only, newest at the bottom. Predictions are written before a test runs, outcomes
after. Labels: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Run outputs live under
`scratch/core/<run_id>/`, manifests under `tracks/core/runs/<run_id>/`.

## 2026-11-15 15:10-15:50 UTC  session core-coll2: reading, cause analysis, design

Worktree `wt/core-coll2`, branch `core/collisions-2`, merged `main` (4ebb05f, already up
to date). Read: `CLAUDE.md`; charter to the end of "Owners"; brief lines 493-553,
688-706, 834-860; rulings `tracks/orch/outbox/20261115T1516Z__to-all__rulings-after-wave-1.md`;
decisions 0010 to 0015; core's `HANDOFF.md`, `STATUS.md`, `stage/G2/OPEN.md` (core has no
`stage/G0` or `stage/G1` directory); `interfaces/collisions.md`; `JOURNAL-coll.md` (P11
and the cell-size follow-up); Track C on `track/C-sidm`: the five requests
`outbox/20261115T1320Z__to-core__{collision-operator,rng-stream2-table,static-curved-metric,perturbation-recipe,grhydro-reference}.md`,
`collide/SPEC.md`, `collide/TESTS.md`, `collide/RNG_REQUIREMENTS.md`; the source
`particles/nrpic_collide.{hpp,cpp}`, `nrpic.cpp` (init, push, excise), `nrpic_kernels.hpp`,
`nrpic_mesh.hpp`, `nrpic_metrics.hpp`, `nrpic_kick.cpp`, `particles.hpp`,
`particles_tasks.cpp`, `pgen/nrpic/nrpic_geodesic.cpp`, `python/nrpic/collide.py`;
arXiv:2009.08163 `paper.tex` lines 820-880 (perturbation).

Baseline executables: the release ones, `/data/haiyangw/nrpic/.work/build_{cpu,gpu}_v03/src/athena`
(built 07:16 and 07:19 local time from main; the last change of `athenak/src` on main is
609a875 at 06:50) [VERIFIED: `git log -- athenak/src`, file times]. Own builds:
`.work/build_cpu`, `.work/build_gpu` of this worktree.

### What wave 1 measured, restated

The operator of core-v0.3 takes both momenta of a pair to the triad of the cell centre,
u^_(m) = Si_c[m][j] u_j, scatters there, and writes u_j' = S_c[j][m] u^_(m)' back. Exactly
conserved per pair: sum of u_j (the map is linear and common) and the sum of
W_c = sqrt(1 + gamma_c^ij u_i u_j). Not conserved: sum of W_p = sqrt(1 + gamma^ij(x_p) u_i u_j),
the energy the deposit hands to the spacetime; in the cluster it grew by 1.05e-8, 2.3e-9,
1.1e-9 of sum M W per collision for cells of 2, 1, 0.5 M (runs core-20261115-140316-8742cdf,
core-20261115-142625-67f8c1d) [VERIFIED: `JOURNAL-coll.md` lines 610-650].

### Candidate cause, as an algebraic statement [JUDGEMENT, to be tested]

For a conformally flat metric let eps_p = (psi_c/psi_p)^4 - 1 (the spatial metric at the
particle against the one of the cell centre). Then W_p^2 = 1 + (1 + eps_p) |u^|^2, and to
first order in eps the change of the pair's energy at its own positions in one collision is
    Delta(W_a + W_b) = (eps_a/2) Delta K_a + (eps_b/2) Delta K_b,   K = |u^|^2/W_c,
which for slow particles is (eps_a - eps_b) Delta W_c,a: the energy that the collision
moves from b to a in the cell frame, times the difference of the spatial metric between
the two positions. Its mean over directions and pairs is not zero when the cell-frame
kinetic energy is correlated with the position in the cell: <Delta W_c,a> = -(T^c_a - T^c_b)
(pairs weighted with their relative speed) with the cell-frame temperature
T^c_p = theta_p (psi_p/psi_c)^4 of a gas of local temperature theta_p, so
    <Delta(W_a + W_b)> = -(eps_a - eps_b)(T^c_a - T^c_b)
                       = (1 - s/4) theta <(eps_a - eps_b)^2>   for theta_local ~ psi^-s.
Consequences that a test can contradict:
(a) the lapse does not enter: with a homogeneous spatial metric the sum of W_p is
    conserved to rounding whatever the gradient of the lapse;
(b) the sign follows the temperature law: positive for s < 4 (a gas of uniform local
    temperature, and a gas in equilibrium in a potential well, which is hotter where psi
    is larger), about zero at s = 4, negative for s > 4;
(c) the size is second order in the cell size and in the amplitude of the gradient.
The cluster of wave 1 is case s < 4 (hotter where deeper): a steady gain, as seen.

### The quantity that should be conserved [JUDGEMENT; derivation]

Neither sum of W at the cell centre nor sum of W_p is the conserved energy of the
physics. In a stationary metric the geodesic motion conserves, per particle, the energy
conjugate to the time coordinate, H = alpha W - beta^i u_i (the Hamiltonian that the
pushers integrate, `nrpic_kernels.hpp` lines 351-356), and a collision at one point
conserves the sum of H of the two partners because it conserves their four-momentum
there. For particles that source the spacetime, the first-order change of the total
mass under a redistribution of momenta at fixed positions is the sum of M delta H with
the fields held fixed: in the first post-Newtonian energy of N bodies the velocity-
dependent terms are (1/2) v^2 (1 + 3U) + (3/8) v^4 per unit mass (plus the terms
bilinear in two velocities), which is the expansion of alpha W with alpha = 1 - U,
psi^4 = 1 + 2U and coordinate velocity v [BACKGROUND: Einstein-Infeld-Hoffmann energy,
not re-read; the algebra H = 1 - U + v^2 (1 + 3U)/2 + 3 v^4/8 is mine]. So the pair must
conserve the sum of H_p with alpha, beta, gamma at each particle's own position. The
operator of core-v0.3 violates it by 1.5 times the defect of sum W_p in a weak field
(reference numbers below: 2.1e-4 against 1.4e-4 per collision in the test well).

Decision. `<particles> coll_energy = particle` (new; default `cell` = core-v0.3):
- The pair is evaluated in the frame of the cell centre, as before (one triad and one
  lapse per cell; cell lists, pairing, random numbers unchanged).
- Exactly conserved per pair (equal rest masses): sum of u_i (covariant components, as
  before) and sum of H_p = alpha_p W_p - beta_p^i u_i with the metric interpolated to each
  particle (the pusher's reconstruction): the four components of the canonical momentum.
- Carrying. Before the collision, b hands a the momentum dl that makes "equal coordinate
  velocity" correspond to "equal momentum": at fixed total momentum P the energy of the
  pair is smallest at the split q with v_a(q) = v_b(P - q); dl is the first Newton step
  from P/2 to it. The collision of the cell frame is computed for u_a - dl, u_b + dl
  (probability from their Moller speed; direction; relative momentum wv). The new
  momenta are u_a' = P/2 + dl + lam wv, u_b' = P - u_a' with lam > 0 the root of
  sum H_p' = sum H_p (convex in lam, unique root, Newton from lam = 1).
- Why the transfer dl and not only a rescaling: with dl = 0 the scheme conserves the
  same quantities, but in an equilibrium state it still moves energy on average from the
  partner that is hotter in the cell frame to the other one, 3 theta Delta U per
  collision in a weak field (a numerical heat flux out of a potential well, relative
  size 0.27 (h/lambda)^2 of the physical conduction for cells of size h and mean free
  path lambda, my estimate). In the non-relativistic limit a pair in two different
  conformally flat metrics is a pair of two different inertial masses psi^4/alpha in the
  canonical variables; its elastic collision about the common coordinate velocity is an
  exact collision of unequal masses, whose equilibrium is equipartition of the energies
  at infinity, i.e. Tolman's law theta alpha = constant. dl realises this to first order
  in the metric difference; lam then restores exact conservation relativistically.
- Not exact: (i) sum of M W_p changes at first order per collision, as it must when heat
  moves between depths; (ii) the angular momentum x^i u_j - x^j u_i of the pair changes
  at first order in the separation, as in core-v0.3 and any scheme with partners at
  different points; (iii) detailed balance holds to first order in the metric
  difference in the non-relativistic limit; the remaining terms are of order theta
  times the metric difference (relativistic corrections) and, for a spatial metric with
  shear across the cell, an anisotropy of the scattering direction of first order;
  (iv) rate: the probability uses lapse, volume and triad of the cell centre.
Alternatives rejected: transport of each momentum to the cell centre at constant H
(right energies, but particles arriving from deeper positions are too cold by the
potential difference, a transfer bias of order Delta U per collision instead of
theta Delta U); own triads with unchanged triad components (conserves sum W_p, loses
sum u_i and sum H_p).

### Source written before any run of it (15:20-15:50 UTC)

`nrpic_collide.hpp`: `CollOwnMetric`, `CollEnergy`, `CollCentre`, `CollScatterRel`,
`CollEnergyRoot`. `nrpic_collide.cpp`: option `coll_energy` (read only if present),
per-particle metric pass, branches in the pair kernel, energy budget taken particle by
particle inside the cells when `coll_energy` is present (history columns 32-35), dump
version 2. `nrpic_geodesic.cpp`: `<problem> metric_kind = static_conformal`.
`nrpic_perturb.cpp` with two hooks in `NrpicPush`. `python/nrpic/collide.py`: the twin of
the new kernels and of the dump. `tracks/core/analysis/collisions/scbox.py`: the test
metric as the code reconstructs it (Catmull-Rom), particle files, and a Monte Carlo
reference over pairs that reads no file of the code.

### Reference numbers (quick, 4e5 pairs per case; the registered reference follows)

`gradient_ref.py`, test metric alpha = alpha0 (1 + a_alpha cos phi), psi = 1 + a_psi cos phi,
16 cells per wavelength, theta0 = 0.05; per collision and unit rest mass, standard errors
in brackets. dW: change of W_a + W_b at the particles; dH: of H_a + H_b; slope: regression
of the change of H of a particle on cos phi minus its cell mean (energy handed along the
modulation). Operator of core-v0.3 ("cell"):

| case | a_alpha, a_psi | temperature law | dW | dH | slope |
|---|---|---|---|---|---|
| psi_iso | 0, 0.1 | uniform | +9.0e-5 (0.5e-5) | = dW | -1.97e-2 |
| psi_iso_f2, _f4 | cells of 2, 4 mesh cells | | +3.2e-4, +1.30e-3 | | |
| psi_iso_half | 0, 0.05 | uniform | +2.5e-5 (0.3e-5) | | |
| psi_null | 0, 0.1 | psi^-4 | -1.2e-5 (0.6e-5) | | +2.6e-3 |
| psi_inverted | 0, 0.1 | psi^-8 | -1.26e-4 (0.7e-5) | | +2.8e-2 |
| lapse_tolman | -0.2, 0 | 1/alpha | 2.5e-19 | +2.8e-5 (0.3e-5) | -1.08e-2 |
| lapse_iso | -0.2, 0 | uniform | 1.8e-19 | -2.5e-6 (3.0e-6) | +0.9e-3 |
| well_tolman | -0.2, 0.1 | 1/alpha | +1.37e-4 | +2.12e-4 | -3.0e-2 |

New kinematics ("particle"), same cases: dH between 3.6e-17 and 1.1e-16 in all; slope
+0.3e-3, +0.04e-3, +0.8e-3 (standard error 1.2e-3) in the three states that are
equilibria of the static metric (psi_iso, lapse_tolman, well_tolman), against -1.97e-2,
-1.08e-2, -3.0e-2 of core-v0.3; no pair without a root; largest |lam - 1| 0.02 to 0.56.

### Predictions, written before any run of the new executable (15:55 UTC)

G1 Cause (operator of core-v0.3, `coll_energy = cell`, on the static conformal metric,
   frozen particles: one step of dt = 1e-6, cross-section chosen for a mean pair
   probability of about 0.15 without sub-steps, 4e6 to 8e6 particles, 16 x 4 x 4 cells).
   The history columns dE_particles and dH_particles divided by M n_coll equal the
   reference dW and dH of each case within 4 combined standard errors. In particular:
   (a) lapse_tolman and lapse_iso: |dW| below 1e-13 (rounding of the sums; the lapse
       does not enter); (b) psi_inverted: dW negative by more than 4 standard errors;
       psi_null: |dW| below a quarter of psi_iso; (c) psi_iso_f2/psi_iso = 3.6 and
       psi_iso_f4/psi_iso = 14.5 (reference), psi_iso/psi_iso_half = 3.6, each within 4
       standard errors.
   Refuted by: a gain above rounding with a homogeneous spatial metric; a positive gain
   in the inverted state; a gain off the reference by more than 4 standard errors in
   any case; no dependence on the cell factor.
G2 Correction (`coll_energy = particle`, same boxes, plus the case well_shift with a
   static shift beta^x = 0.05 sin phi and the cell factors 2 and 4):
   (a) |dH_particles| / (M n_coll) below 1e-15 in every case (reference: 1e-16);
   (b) every component of sum M u_i changes by less than 1e-14 of sum M |u| over the
       step (exact sums of the dump);
   (c) n_noroot = 0;
   (d) the slope equals the reference within 4 standard errors; in the three
       equilibrium states it is zero within 4 standard errors, where core-v0.3 has
       -1.1e-2 to -3.0e-2;
   (e) the Python twin replays the step from the dump: same tested and accepted pairs,
       momenta within 1e-13 of max(1, |u|), untouched particles bit-identical.
   Refuted by any of these failing.
G3 Homogeneous metric (P10 box, lapse 0.7, oblique gamma_ij): `coll_energy = particle`
   gives the same number of collisions in every step as `cell` and momenta within 1e-12
   at the end of 400 steps... restated: within 1e-9 (a rounding difference in a
   probability can flip an acceptance; if one flips, the states differ from then on and
   only the statistics can be compared: collisions within 4 sigma, relaxation as P10).
G4 Tolman equilibrium with streaming (well_tolman metric, 1e6 particles drawn from
   f ~ exp(-alpha W/theta_inf), theta_inf = 0.05, mean free path = one cell, 40 collision
   times, dt = 0.01):
   `particle`: the sum of M H changes by less than 1e-6 of its value over the run; the
   cos phi amplitude of ln(theta alpha) stays zero within 0.5 percent.
   `cell`: the sum of M H grows steadily by 2e-3 to 6e-3 of its value (20 collisions
   per particle times about 2e-4, as long as the state stays near Tolman's); the gas
   ends colder at the bottom of the well than Tolman's law, amplitude of ln(theta alpha)
   between -2 and -10 percent times cos phi (my estimate -5 percent from a numerical
   conductivity 0.09 (h/lambda)^2 of the physical one acting on grad T + 4 T grad ln psi).
   Refuted by: drift of sum M H in `particle` above 1e-6; a temperature mode in
   `particle` above 0.5 percent; no difference between the modes.
R  Regression: without `coll_energy` every output file of the wave-1 collisional boxes
   (snapshots, `coll.hst`, dump, particle history) and of the existing set-ups
   (`regress_relativistic.py`, `rng/run_regression.py`, `lead/cf_checks.py`) is
   byte-identical between the release executable and the new one, processor build.
   Card: particle snapshots of collisional boxes byte-identical; the floating-point
   sums of `coll.hst` may differ in the last digits if the larger reduction record
   changes the block size of the card's reduction [TO VERIFY by the run].
S  Perturbation (`perturb_gamma`): for one particle at rest in flat space the momentum
   after the interval is gamma T_pert x/r to rounding for any step size that does or
   does not divide T_pert; with the option absent the outputs are byte-identical (part
   of R).

## 2026-11-15 16:00 UTC  the reference refutes part of the design before any code run; detailed balance added

Harness: `harness/bin/nrpic-run submit ... --dry-run` fails in this worktree with
`KeyError: 'outputs'` (nrpic-run line 163, `is_live`: it reads the hand-written manifests
of wave 1, which have no field `outputs`). Runs of this package are therefore registered
by hand with `tracks/core/analysis/rng/runreg.py` (the helper of wave 1), which writes
`tracks/core/runs/<run_id>/manifest.json` with the same run-id pattern. Request to orch.

Reference at 4e6 pairs per case (run core-20261115-155153-5a61782, the kinematics as
first designed, i.e. without the acceptance step described below). Operator of
core-v0.3: psi_iso dW = +8.59e-5 (0.17e-5), f2 +3.356e-4, f4 +1.299e-3, half amplitude
+2.07e-5, psi_null -1.23e-5 (0.18e-5), psi_inverted -1.312e-4, lapse_tolman dW = -1e-19,
dH = +2.75e-5, lapse_iso dW = 4e-20, dH = -1.1e-6 (0.95e-6), well_tolman dW = +1.300e-4,
dH = +2.025e-4. These stand as the reference of G1.

New kinematics, as first designed: dH = 3.5e-17 to 1.1e-16 everywhere (the residual of
the root is always of one sign: the iteration approaches the root from the side F > 0).
But the slope in the equilibrium states is NOT zero: psi_iso +1.14e-3 (0.37e-3),
psi_iso_f2 +1.48e-3 (0.19e-3), psi_iso_f4 +1.25e-3 (0.10e-3), psi_iso_half +0.84e-3
(0.38e-3); lapse_tolman +0.18e-3 (0.37e-3). So where the spatial metric varies, the
collision still hands energy up the modulation in equilibrium, about 6 percent of what
core-v0.3 hands down (-1.9e-2), independent of the cell size, hence of first order in
the metric difference. This is the term I had listed as "relativistic corrections of
order theta times the metric difference"; my prediction G2(d) ("zero within 4 standard
errors") would have passed at the statistics of the code run (standard error 1.3e-3)
and is false at 4e6 pairs. Recorded as a failed prediction, found by the reference.

Cause [JUDGEMENT, tested below]: the transition rate between two states of a pair is
not symmetric. The collision is proposed with a rate proportional to the Moller speed
of the old state and an isotropic direction in the frame of the old state; in one
metric the density of that proposal on the surface of constant pair momentum and
energy is (1/4 pi) sqrt(s)/(E_a' E_b' p*), and together with v_Mol = p* sqrt(s)/(E_a E_b)
the rate s/(E_a E_b E_a' E_b') is symmetric (the invariant phase space). With two
metrics the surface is deformed and the product is no longer symmetric at first order
in the metric difference times theta.

Change (source and twin, before any run): `nrpic::CollBalance` computes
R = rate(new -> old)/rate(old -> new), both as densities on the surface: with the ray
construction u_a' = c + r L nhat (L the stretch of the centre-of-momentum frame,
det L = gamma) the measure delta(F) d^3q is gamma r^2 dOmega/(dF/dr), so the density of
a proposal is (1/4 pi)(dF/dr)/(gamma r^2), with dF/dr from the velocities at the end
point. The collision takes place with probability min(1, R) (third uniform deviate of
the acceptance key, unused so far). For equal metrics I checked the algebra by hand:
(v_a' - v_b').L nhat = E p*/(E_a' E_b'), so the density is the invariant one and R = 1;
the twin gives |R - 1| <= 1.2e-15 for six random pairs. History column 36 `n_balance`
counts the rejected collisions.

Quick reference with the acceptance step (1e6 pairs): slope psi_iso -0.96e-3 (0.74e-3),
psi_iso_f4 +0.22e-3 (0.19e-3) [was +1.25e-3 (0.10e-3)], well_tolman -0.35e-3 (0.74e-3);
at theta0 = 0.3: psi_iso_hot +5.2e-3 (4.5e-3), well_tolman_hot -4.1e-3 (4.4e-3);
rejected 1.2e-3 to 6e-3 of the proposals at theta0 = 0.05, 0.8 to 1.3 percent at 0.3.

### Predictions restated (16:00 UTC, before the registered reference and any code test)

G2(d) restated. Reference with the acceptance step, 4e6 pairs (to be run now, and
again with `--no-balance` for the hot cases): in the equilibrium states psi_iso,
psi_iso_f2, psi_iso_f4, psi_iso_half, lapse_tolman, well_tolman, well_tolman_f2,
psi_iso_hot, well_tolman_hot, well_tolman_hot_f2 the slope is zero within 4 standard
errors (standard errors 1e-4 to 4e-4 at theta0 = 0.05); without the acceptance step
the hot cases show a slope that differs from zero by more than 4 standard errors and
is larger, relative to the slope of core-v0.3, than at theta0 = 0.05. Refuted by a
slope beyond 4 standard errors in any equilibrium state with the acceptance step (the
derivation of R would then be wrong). The code must then reproduce the reference
slopes within 4 combined standard errors, and its number of rejected collisions over
the number proposed must equal the reference share within 4 sigma (binomial).
G2(a)-(c), (e), G1, G3, G4, R, S stand as written.

### Addition to prediction S (16:12 UTC, before the run)

`run_perturb.py`: besides the particle at rest (momentum gamma T_pert x/r to 1e-14
relative for steps 0.05, 0.037, 0.025, 0.0125, 0.00625, interval [0.1, 0.47]) a particle
that crosses the radial direction (u = (0.3, -0.8, 0.5) at distance 1.5 from the centre)
is compared at t = 1 with an independent integration of dx/dt = u/W, du/dt = gamma x/r
(scipy DOP853, rtol 1e-13): the error of the split kick falls as the square of the step
(measured order between 1.8 and 2.2 from the steps 0.025, 0.0125, 0.00625). With
`perturb_gamma = 0` the snapshot is byte-identical to that of a deck without the options.

### Outcome S, first run: core-20261115-160530-819d588 (16:14 UTC); one part of the prediction failed

- Particle at rest: |u - gamma T x/r|/|u| = 3.0e-16, 1.3e-15, 6.8e-16, 9.8e-16, 8.6e-16
  for the five steps (0.05 and 0.037 do not divide the interval). Passed.
- Null (`perturb_gamma = 0` against a deck without the options): byte-identical. Passed.
- Moving particle: errors of u at t = 1: 1.7e-5, 8.4e-7, 1.2e-6, 1.0e-6, 7.6e-8; "order"
  from the last three 0.23 and 3.8. FAILED as predicted. Reason [JUDGEMENT, tested by
  the rerun]: the interval ends at 0.47, which is 18.8, 37.6 and 75.2 of these steps;
  the last, partial kick is applied at the end point of its half step instead of the
  middle of the part inside the interval, an error of second order whose coefficient
  depends on where in the step the interval ends, so the error is not a smooth
  function of the step. The impulse itself is exact (particle at rest).
  Restated before the rerun: with steps 0.01, 0.005, 0.0025, for which 0.1 and 0.47
  are step boundaries, the order is between 1.8 and 2.2; if it is not, the reason
  above is wrong. Recommendation for users: choose perturb_tstart and perturb_time as
  multiples of the step.

### Outcome S, rerun: core-20261115-160559-819d588 (16:16 UTC)

Passed. Orders 2.000004 and 2.0000000 from the steps 0.01, 0.005, 0.0025 (errors of u
1.36e-7, 3.39e-8, 8.48e-9); the steps 0.05, 0.037, 0.02, of which 0.47 is not a
boundary, give 1.7e-5, 8.4e-7, 4.4e-6 (irregular, up to ten times above the line);
particle at rest 3e-16 to 4.7e-15; null byte-identical. Figure `fig_perturb.png` looked
at (the aligned steps lie on the dashed line of slope 2).

### Registered references with the acceptance step (16:20 UTC)

Runs core-20261115-160136-819d588 (psi_iso, _f2, _f4, _half, psi_null),
core-20261115-160137-819d588 (psi_inverted, lapse_tolman, lapse_iso, well_tolman, _f2),
core-20261115-160139-819d588 (well_shift, psi_iso_hot, well_tolman_hot, _hot_f2), control
without the step core-20261115-160140-819d588; 4e6 pairs per case. Slope in the
equilibrium states with the step, in units of 1e-3 (standard error): psi_iso -0.49
(0.37), _f2 +0.07 (0.19), _f4 -0.12 (0.10), _half +0.29 (0.37), lapse_tolman +0.02
(0.37), well_tolman +0.28 (0.37), well_tolman_f2 -0.05 (0.19); at theta0 = 0.3:
psi_iso_hot +0.4 (2.2), well_tolman_hot -1.1 (2.2), well_tolman_hot_f2 +1.0 (1.1). All
within 1.3 standard errors of zero: the restated G2(d) holds in the reference. Control
without the step at theta0 = 0.3: psi_iso_hot +66.1 (2.3), well_tolman_hot +112.6 (2.3)
against -95.9 and -169.4 of core-v0.3: without the step the transfer in equilibrium is
two thirds of the old one, of the opposite sign; at theta0 = 0.05 it was 6 percent. So
the term grows with the temperature as stated, and the acceptance step removes it (a
test in which the derivation of R could have failed at 29 standard errors).
Rejected share of the proposals: 0.6e-3 to 6.4e-3 at theta0 = 0.05 (largest for cells
of four mesh cells), 0.8 to 2.6 percent at theta0 = 0.3; pairs without a root at most
3e-5 (hot, cells of two mesh cells).

### Predictions for the card runs (16:22 UTC, before submission)

Rc Card regression. The five existing set-ups: verdicts as in wave 1 (the two set-ups
   whose baseline is reproducible identical; in the others only the files that differ
   between two runs of the baseline differ). Collisional boxes of wave 1 (rate, relax,
   repro, conv_dt, curved) against the card outputs of wave 1: particle snapshots
   byte-identical; `coll.hst` identical unless the larger reduction record changes the
   order of the card's sums, in which case only floating-point sum columns differ, by
   less than 1e-12 relative, and all integer columns agree.
Nc New tests on the card: as G1, G2, G4 on the processor (statistics; card and
   processor states need not be identical).
C  Cluster (P11 set-up, Kn = 3, collision cells of 2 M, 150 M, 1e4 particles), runs
   kn3_cell and kn3_particle. `cell`: the collision steps raise sum M W_p by 5.2e-5 of
   its value as in wave 1 (within 30 percent: 3.6e-5 to 6.8e-5) and sum M H_p by more,
   between 5e-5 and 1.5e-4. `particle`: the collision steps change sum M H_p by less
   than 1e-12 of its value (about 5000 collisions); no more than five pairs without a
   root; rejected collisions below 2 percent; the same number of collisions as `cell`
   within 4 sigma; central lapse at 150 M within 0.01 of the `cell` run (wave 1 saw
   0.7914, 0.7885, 0.7891 for three cell sizes), mass radii within 5 percent. Refuted by
   a change of sum M H_p in `particle` above 1e-12, or by a structural difference
   beyond these bounds.

### Processor fallbacks while the card queue is full (16:26 UTC; 17 jobs queued, mine are 4453 R, 4454 N, 4455 C)

Cp Cluster on the processor, two steps (0.25 M) with a cross-section 100 times that of
   Kn = 3 (Kn = 0.03, about 800 expected collisions in the two steps), runs
   kn0.03_cell and kn0.03_particle: `particle`: |sum of dH_particles| below 1e-12 of
   sum M H; `cell`: sum of dH_particles positive, of order 800 x 1.6e-8 = 1.3e-5 of
   sum M H (between 3e-6 and 5e-5; few collisions, wide band). Same refutation as C.
G4 and the replay cases of coll_energy run on the processor now with the predictions
already written.

### G4 on the processor: first attempt stopped (16:45 UTC), run core-20261115-160912-0656925

Stopped by me after 17 minutes (the four AthenaK processes killed by process id; the
driver then exits with status 1 and the manifest records a failed run): fewer than
100 of 600 steps done. The implicit midpoint push with the mesh metric and tolerance
1e-13 costs about 20 microseconds per particle and step on one core, i.e. more than
three hours for 1e6 particles and 600 steps. No result. The card would do it in
seconds (job 4454, queued). Processor version, same predictions: 1e5 particles (391
per cell), 400 steps (31 collision times); the standard error of the temperature
mode of one snapshot is then about 0.4 percent, of the late-time mean about 0.2
percent, enough for the predicted -2 to -10 percent against zero. The growth of
sum M H in `cell` over 31 collision times is predicted between 1.5e-3 and 5e-3
(restated for the shorter run: 15.5 collisions per particle times 2e-4).

### Predictions T12 and G3 restated as one run (16:55 UTC, before the run)

`run_static_homog.py` (5e4 particles, 200 steps, alpha0 = 0.8, psi0 = 1.1, two-temperature
start, 16 x 4 x 4 cells):
(a) `static_conformal` without amplitudes and `coll_energy = cell` gives snapshots
    byte-identical to the wave-1 generator `homogeneous` with gxx = gyy = gzz = psi0^4
    and no `coll_energy` (same metric arrays, same operator). Refuted by one byte.
(b) G3: `coll_energy = particle` has the same n_tested and n_coll in every step as
    `cell`, no rejected collision, no pair without a root, and momenta within 1e-9 at
    the end.
(c) T12: the number of collisions equals that of the flat box with the cross-section
    scaled by alpha0 within 4 sigma; the summed weight equals
    sigma M alpha0 dt/(2 psi0^6 V_cell) x sum N (N - 1) of the cell populations to 1e-10.
(d) sum M u_i conserved to 1e-12 of sum M |u| in all four runs; (e) the collision
    steps change sum M W and sum M H at the particles by less than 1e-12 relative.

## 2026-11-15 17:10 UTC  outcomes on the processor: replay, cluster (two steps), wave-1 reruns, first G4

### G2(e) replay: run core-20261115-160914-0656925. Passed.

Thirteen cases, 20000 particles each, collision step of cycle 5 replayed by the Python
twin from the dump: the seven cases of wave 1 and `static_cell`, `static_particle`
(12 sub-steps), `static_particle_factor2`, `static_particle_cholesky_boris`,
`static_particle_nanbu` (18 sub-steps, masses 1:4), `kerr_particle` (analytic
Kerr-Schild metric of a mass 20 at distance 173: shift, spatial metric not conformally
flat). In all: numbers of tested pairs and of collisions equal (e.g. 55913 and 2149
for static_particle), n_sub and updates per particle equal, sum_P to 6.9e-15, pairs
without a root 0 in code and twin, largest |lam - 1| equal to 1e-15 (0.18, 0.38, 0.18,
0.14, 0.005), momenta within 1.3e-14 of max(1, |u|) (criterion 1e-13), untouched
particles bit-identical. Figure `fig_replay.png` looked at (all histograms left of
1e-13; the legend covers part of the histograms).

### Cp cluster, two steps on the processor: run core-20261115-160913-0656925. Passed.

Relativistic cluster y_c = 0.819 with Z4c and six refinement levels, 1e4 particles,
collision cells of 2 M, cross-section of Kn = 0.03, two steps (0.25 M).
- `coll_energy = cell`: 773 collisions (sum_P 798.8); the collision steps raise
  sum M H by 1.48e-5 of its value and sum M W by 9.6e-6 (ratio 1.55; predicted
  about 1.5): 1.9e-8 and 1.2e-8 per collision (wave 1: 1.05e-8 of sum M W at Kn = 3).
- `coll_energy = particle`: 772 collisions (sum_P 796.9); change of sum M H in the
  collision steps 4.8e-18 of its value (predicted below 1e-12); no pair without a
  root, none rejected, largest |lam - 1| 1.6e-3; sum M W changes by -4.7e-6 (first
  order, either sign); pair defect 0.10 units in the last place.
- Both: rest mass identical to the bit, deposit identity 3.7e-15, lapse at the end
  within 1.4e-7 of the collisionless run.

### Reruns of wave 1 on the processor, executable built from 819d588, options absent

`rerun_wave1.py` (summary `scratch/core/tmp/coll2/rerun_wave1_819d588.json`): every
driver exits with status 0 (its own criteria). Output files against the run
directories of wave 1: replay 31 files, repro 135, smr 17, unequal 23, cells 57,
conv_dt 46, curved 23: all byte-identical (runs core-20261115-160336-819d588,
-160751-6537687, -160907-5c63a43, -160921-0656925, -161109-0656925, -161222-0656925,
-162952-74b3e87; kernel test -160318-819d588 has no comparable file). rate
(-161512-0656925): 9 of 43 files differ; relax (-162041-0656925): 4 of 116. All
differing files are `box.coll.hst`: the wave-1 runs of these two tests
(core-20261115-133533-0ca5e3b, -134036-5684674) were made with an earlier build of
wave 1 whose history had 26 columns (file sizes 86265 against 105146 bytes) and a
different order of the sum in column sum_MW (differences 4e-16 relative, 61 to 142
rows); the snapshots are identical. So the wave-1 directory is not a valid reference
for these two; they are rerun against the release executable (below). The three
existing regressions started at 15:52 (regress_relativistic, rng/run_regression,
lead/cf_checks) ran while the processor executable was rebuilt at 16:02 and are
discarded; rerun below with the frozen copy of the executable.

### G4, processor version at theta_inf = 0.05: run core-20261115-162714-abf9d27. Partly failed.

The analysis stopped with an error: bins of the temperature profile at the top of the
well are empty. At theta_inf = 0.05 the well (alpha from 0.8 to 1.2) is eight
temperatures deep and the density contrast is e^8; I had not looked at the density
before choosing the temperature. From the histories (evaluated by hand): 57
collisions per particle in 400 steps;
- `particle`: change of sum M H in the collision steps 2.4e-15 of its value in both
  seeds (2.84e6 collisions; predicted below 1e-12), total change including the push
  -8.7e-9 and +7.7e-9 (predicted below 1e-6); 1903 and 1900 collisions rejected
  (6.7e-4), none without a root. Passed.
- `cell`: sum M H grows by 8.22e-4 and 8.47e-4. Predicted band 2.8e-3 to 8.5e-3:
  FAILED, by a factor 3.4. Reason, checked: the band used the gain per collision of
  the reference with uniform density (2.0e-4); the gas sits at the bottom of the well
  where the gradient vanishes. The reference with the equilibrium density and cells
  weighted by their collision rate (run core-20261115-163914-74b3e87) gives 4.07e-5
  (0.17e-5) per collision; the code shows 4.25e-5 and 3.50e-5 in the first five steps
  (35000 collisions each, standard error about 1.3e-5) and then 2.5e-5 to 2.9e-5: the
  rate falls as the state leaves Tolman's law.

### G4 restated before the rerun (17:12 UTC)

theta_inf = 0.2 (density contrast e^2), 1e5 particles, 400 steps, two seeds, mean
free path one cell at the mean density; reference of the initial state (same run):
gain of H_a + H_b per collision 3.62e-4 (0.09e-4) for `cell`, 2.7e-16 for `particle`,
rejected share 5.7e-3.
`particle`: change of sum M H in the collision steps below 1e-12 of its value, total
below 1e-6; cos phi amplitude of ln(theta alpha), late-time mean, within 0.5 percent
of zero; no pair without a root.
`cell`: gain per collision in the first collision time equal to the reference within
4 standard errors; total growth between 0.3 and 1.2 of what the initial rate would
give; amplitude of ln(theta alpha) between -2 and -10 percent (my estimate -5).

## 2026-11-15 18:10-18:40 UTC  second session of coll2: outcomes of the runs left unrecorded

Merged `main` (b9fbf3e: harness and coord only, no change under `athenak/src`). The
previous session of this package ended after submitting the runs below; their manifests
were untracked (committed now, bdfb72d). Outcomes, read from the run directories:

### G1, G2 on the processor: run core-20261115-160707-6537687 (8e6 particles, 14 cases). Mixed.

Against the registered reference of 16:20 (runs core-20261115-160136/-160137/-160139-819d588):
- G1 (operator of core-v0.3) passed in its structural parts: (a) lapse_tolman and
  lapse_iso dW = +6.6e-21 and -3.3e-21 per collision (the lapse does not enter);
  (b) psi_inverted dW = -1.43e-4 (negative, 23 standard errors), psi_null -7.3e-6
  (below a quarter of psi_iso +8.33e-5); (c) cell-size ratios f2/iso 3.98 (reference
  3.91, se 0.28), f4/iso and iso/half within 4 se. So the candidate cause, the spatial
  metric differing between the partners' positions with a temperature that is
  correlated with position, survives a test in which (a), (b) or (c) could each have
  failed.
- G2 (coll_energy = particle) passed (a) |dH| per collision 3.5e-17 to 3.5e-16 in all
  14 cases (criterion 1e-15), (b) sum M u_i to 2e-20, (d) the slope in the ten
  equilibrium states is zero within 4 se.
- FAILED as written, five cases: psi_inverted slope z = +4.6 (cell) and +6.7 (particle);
  well_tolman_f2 dW(cell) z = -4.5 and rejected share z = -4.0; well_tolman_hot rejected
  z = -8.0; well_tolman_hot_f2 rejected z = -10.8 and 5 pairs without a root (G2(c)
  said none; the reference of 16:20 had already shown up to 3e-5 of the proposals
  without a root in this case, 5 of 3.6e5 = 1.4e-5: the prediction contradicted the
  reference, my error). The deficits are systematic: in all five "well" cases dW(cell)
  of the code is 7 to 15 percent below the reference (z -2.3 to -4.5) and the rejected
  share 3 to 11 percent below; the psi-only cases agree.
- Figure `fig_gradient.png` looked at: the dots sit on the bars except in the well
  cases and the slope of psi_inverted.

Candidate cause of the deficits [JUDGEMENT, tested next]: the reference, not the code.
`scbox.pair_reference` with uniform density draws the collision cell uniformly, but the
pair probability of the operator carries the factor alpha_c/sqrt(det gamma_c) =
alpha_c/psi_c^6 of the cell (rate per coordinate time and coordinate volume; the
reference applies this factor only in its "tolman" branch). Where the temperature (or
the metric gradient) is correlated with alpha/psi^6 the weighted mean differs: in the
well, deep cells (alpha small, psi large) are hotter and collide less in the code.

### G4 at theta_inf = 0.2: run core-20261115-164138-cdd7c88. Passed.

1e5 particles, 400 steps of 0.01, 57 collisions per particle, two seeds.
- `particle`: change of sum M H in the collision steps 6.41e-15 of its value (both
  seeds), total including the push -1.39e-7 and +6.1e-8 (criterion 1e-6); cos phi
  amplitude of ln(theta alpha), late mean, -0.24 (0.21) and -0.04 (0.21) percent
  (criterion 0.5 percent); no pair without a root; 16255 and 16183 collisions rejected
  (5.7e-3 of the proposals; reference 5.7e-3).
- `cell`: sum M H grows by 6.47e-3 and 6.18e-3 (0.77 and 0.74 of the initial rate
  8.4e-3; band 0.3 to 1.2); gain per collision in the first collision time 2.93e-4 and
  3.77e-4 against the reference 3.62e-4 (z -1.2, +0.3); temperature amplitude -3.8
  (0.2) and -3.4 (0.2) percent: the gas ends colder at the bottom of the well than
  Tolman's law, as predicted (band -2 to -10 percent).
- `fig_tolman.png` looked at: the energy of `cell` rises linearly over 50 collision
  times; its temperature mode falls to -4 percent within 8 collision times and stays;
  the `particle` mode scatters about zero; the end profile of `cell` is hotter at the
  top of the well (x/L = 0.5), the empty top bins (density contrast e^2) are skipped.

### R on the processor (executable of 819d588, options absent). Passed.

`regress_relativistic.py` geo, boris, dep, east, os, jeans, binary: all files identical
(runs core-20261115-164154 ... -165211-cdd7c88); rng `run_regression.py` c1-c5
identical, baseline twice identical (core-20261115-165253-cdd7c88); `cf_checks.py` P2
16 + 9 files identical, P5 combined curvature within float32 rounding (largest 0.998
of the bound) (core-20261115-170028-cdd7c88); wave-1 rate and relax against fresh runs
of the release executable: 43 and 116 files compared, none differs
(core-20261115-164153-cdd7c88, -165050-cdd7c88; baselines -164615, -165337).

### Card jobs 4453 (R), 4454 (N), 4455 (C): every run of the new executable crashed

All runs of `scratch/core/tmp/coll2/exe/819d588/athena_gpu` ended with SIGSEGV (exit
-11) after the mesh summary, before the particle file is read, with and without the new
options (runs core-20261115-171107, -171146, -171154, -171207, -171830, -171836,
-172012, -172059, -172122, -172223-cdd7c88); the release executable ran the same decks
in the same jobs. Card time spent: 0.07 card-hours. Candidate cause [JUDGEMENT, to be
tested]: a stale object in the incremental card build. `particles.hpp` (class
Particles gains members) changed at 07:40:08 local time while the first card build
(finished 07:42) was compiling; the incremental build at 07:44 recompiled only 13 of
the files that include it, so objects compiled from the old class layout may have been
linked. Test: a clean card build from a snapshot of the source (f46f159, identical
`athenak/src` to 819d588) must run the same decks; if it also crashes, the cause is in
the source and is searched there.

### Prediction for the corrected reference (18:40 UTC, before the run)

Reference rerun with the cell drawn in proportion to alpha_c/psi_c^6 (uniform positions;
`pair_reference(..., cell_rate=True)`, 4e6 pairs per case, the 14 cases), and the code
numbers of run core-20261115-160707-6537687 graded again against it (no new code run):
(a) every case of G1 and G2(d) within 4 combined standard errors, including the
    rejected shares; (b) the reference values in the psi-only cases with s_psi = 0 move
    by less than 2 standard errors (the weight psi^-6 enters there only at second
    order); (c) in the five well cases the reference dW(cell) falls by 4 to 15 percent;
    psi_inverted slope rises towards the code (+5.9e-2).
Refuted by: a case beyond 4 se after the change, or a well case whose reference does not
move: then the code and the pair model differ in something else and the cause above is
wrong.

### Outcome of the corrected reference (18:20 UTC): prediction held; G2(c) as written still fails

Reference with the cell rate: runs core-20261115-181655-b4b8e33, -181657-426b4a8,
-181700-726905c, -181702-c93920b (4e6 pairs per case, 2 to 4 min each). Code numbers of
run core-20261115-160707-6537687 graded again: run core-20261115-182037-e24d0d0
(`run_gradient.py --regrade`; `fig_gradient.png` looked at: every dot on its bar).
(a) Every comparison of G1 and G2(d) within 1.8 combined standard errors (before: five
    beyond 4): well_tolman_f2 dW(cell) z = -0.9 (was -4.5), rejected -0.0 (was -4.0);
    well_tolman_hot rejected +0.2 (was -8.0); well_tolman_hot_f2 rejected +1.1 (was
    -10.8); psi_inverted slope +0.7 (cell, was +4.6) and +1.4 (particle, was +6.7);
    well_shift dW -1.8 (was -3.8). Cell-size ratios f2/iso 3.98 (ref 4.07, se 0.28),
    f4/iso 15.8 (16.7, se 1.0), iso/half 4.06 (3.67, se 0.58).
(b) Psi-only cases: psi_iso moved from 8.59e-5 to 8.05e-5 (2.2 combined se of the two
    references), psi_iso_f4 from 1.299e-3 to 1.340e-3 (4 se). FAILED as written: my
    "second order, below 2 se" ignored that the weight psi^-6 has a first-order
    amplitude 0.6 at psi_amp = 0.1, whose square (with sin^2 phi of the gradient) shifts
    the mean by a few percent. The code agrees with the new values (z +0.6, -1.1).
(c) Well cases: reference dW(cell) fell by 7 to 10 percent (well_tolman 1.325e-4 ->
    1.205e-4, f2 5.28e-4 -> 4.90e-4, shift 1.339e-4 -> 1.230e-4, hot 5.98e-4 -> 5.32e-4,
    hot_f2 2.32e-3 -> 2.14e-3); psi_inverted particle slope rose 5.00e-2 -> 5.71e-2
    (code 5.94e-2). Held.
So the deficits came from the reference (cells drawn uniformly while the operator's
pair probability carries alpha_c/psi_c^6), not from the code. The code reproduces the
pair model of section 11 of `collisions.md` in all 14 cases.
G2(c) "no pair without a root": still 5 pairs in well_tolman_hot_f2. The corrected
reference has a share 3.1e-5 of the proposals without a root there (expected 11 of the
3.7e5 proposals, observed 5, z = -1.9), 3.6e-8 in well_tolman_hot, zero elsewhere. The
criterion contradicted the reference; it is restated as "n_noroot consistent with the
reference share". Unscattered pairs bias nothing that is conserved; they lower the rate
by their share.

## 2026-11-15 18:25 UTC  clean builds of f46f159; T12/G3 passed; the card crash and its likely cause

Builds from a `git archive` snapshot of f46f159 (`athenak/src` identical to 819d588):
`.work/build_gpu_f46f159` (293 s), `.work/build_cpu_f46f159`; frozen copies
`scratch/core/tmp/coll2/exe/f46f159/athena_{gpu,cpu}` (sha256 82a05ada..., adbf1b16...).

Evidence for the stale-object cause of the card crash (before any card run of the new
build): in the old card build directory the objects that include `particles.hpp`
and were finished between 07:40:10 and 07:40:34 local time (vtk_prtcl, particles_pushers,
particles, particles_tasks, nrpic_kick, nrpic_curvature, nrpic_newton, pgen, nrpic_io)
were completed 2 to 26 s after the header changed (07:40:08); a card compilation of
such a file takes tens of seconds, so they were compiled from the old class layout,
and the incremental build of 07:44 did not redo them (their objects are newer than the
header). `particles.cpp.o` (construction of the particle module) is among them. The
processor build of 07:35-07:43 compiled every such object at 07:43, after the last
header change; its executable passed every byte regression. The card smoke test of
job 4482/4483 decides it: the clean card build must run the decks.

### T12 of track C and G3: run core-20261115-182101-3a6e046 (processor, f46f159). Passed.

5e4 particles, 200 steps, alpha0 = 0.8, psi0 = 1.1, two-temperature start, 16 x 4 x 4
cells. (a) `static_conformal` without amplitudes with `coll_energy = cell`: every
snapshot byte-identical to the wave-1 generator `homogeneous` with gamma_ij = psi0^4
delta_ij. (b) `coll_energy = particle`: the same n_tested and n_coll in every step as
`cell` (248168 collisions), no rejection, no pair without a root, lam = 1 exactly,
momenta within 2.8e-14 at the end (criterion 1e-9), positions within 1.2e-12.
(c) 248168 collisions against 248192 in the flat box with the cross-section scaled by
alpha0 (ratio 0.99990, z = -0.03): the rate per coordinate time and coordinate volume
is alpha0 psi0^6 times the flat value at the same proper density (track C's T12);
summed weight against sigma M alpha0 dt/(2 psi0^6 V) sum N (N - 1): 1.8e-14.
(d) sum M u_i: at most 2.2e-18 of sum M |u|. (e) collision steps change sum M W and
sum M H at the particles by 3e-16 of their values. `fig_static_homog.png` looked at:
the per-step rates of the curved runs coincide and follow the flat run within its
scatter as the gas relaxes; the momentum differences sit at 1e-15.

### Processor checks of the clean build f46f159 (18:30 UTC)

- G2(e) replay: run core-20261115-182109-0b69dbe. Passed: 13 cases, numbers of tested
  pairs, collisions and updates identical between code and twin (and identical to the
  run of the 819d588 executable, e.g. 2149 collisions in static_particle, 1553 in
  kerr_particle); momenta within 1.27e-14 of max(1, |u|); sum_P to 2.1e-14; no pair
  without a root; untouched particles bit-identical. `fig_replay.png` looked at: every
  histogram ends below 2e-14, left of the line at 1e-13.
- Byte regression of seven existing set-ups, release executable core-v0.3 against the
  clean build: geo, boris, dep, east, os, jeans, binary all files identical (2, 2, 1,
  12, 16, 5, 1) (runs core-20261115-182302-c03e628 ... -183317-9ee0bde, summary
  `scratch/core/tmp/coll2/regress_relativistic_f46f159.json`).
- Wave-1 collision tests with the clean build, options absent, every compared output
  file byte-identical (19:15 UTC; `rerun_wave1.py`, summaries
  `scratch/core/tmp/coll2/rerun_{wave1,vs_release}_f46f159.json`): P11 cluster null on
  the processor, 26 files (core-20261115-182250-c03e628); replay 31 (-184440-84995cc);
  P7 repro 135 (-184822); static refinement 17 (-184919); unequal masses 23 (-184931);
  P8b cells 57 (-185041); P8a time step 46 (-185134); P10 curved box 23 (-185333);
  P2-P4 rate 43 files against a fresh run of the release executable (-190100 against
  -190502) and P5-P6 relaxation 116 (-190911 against -191143). Every driver exited with
  status 0 (its own criteria). P0 (kernels, compiled from the header) was rerun at
  819d588 (core-20261115-160318-819d588); the header is unchanged since. Figures
  `fig_curved_box.png` and `fig_rate_conservation.png` looked at: as in wave 1.
  P9 (the card) and P11 with collisions on the card: queued (below).

### Published for scouting runs (19:15 UTC)

`scratch/core/exe/core_collisions-2/`: athena_cpu, athena_gpu (the clean builds of
f46f159), COMMIT, SHA256SUMS, READY (options, one example input each, what is tested).
The card executable is marked in READY as not yet run on a card. Card jobs 4484 (R) and
4485 (N, C) wait in the queue (estimated start 01:48 and 02:28 UTC, behind 14 jobs of
other owners); `gpu_job3.sh` appends its verdict lines to `CARD_TESTS.log` there. Card
time used by this package: 0.07 card-hours (the crashed runs of the first session);
the queued jobs ask for at most 1.5 hours of wall limit, expected below 0.5
card-hours.

## 2026-11-15 19:20 UTC  end of the second session of coll2: state and what is open

Correction to the entry of 19:15: card time used by this package so far is 0.087
card-hours (sum of `card_hours` of the ten crashed card runs of 17:11-17:22 UTC), not 0.07.

Established (evidence in `interfaces/collisions.md` section 11.6 and the entries above):
1. Cause of the collision energy growth (core G2 OPEN item 6): the spatial metric differs
   between the partners' positions in a cell while the cell-frame kinetic energy is
   correlated with position; tested in 14 configurations where three consequences could
   each have failed (lapse does not enter, sign follows the temperature law, second
   order in the cell size).
2. Correction `coll_energy = particle`: per pair, sum u_i and sum (alpha W - beta^i u_i)
   at the particles' own metric conserved to rounding; equilibria of a static metric
   preserved (G2, G4); identical to `cell` in a homogeneous metric (G3); T12 passed.
3. Off by default: every compared file byte-identical on the processor (seven existing
   set-ups, rng and nrpic_cf regressions, all wave-1 collision tests and the curved box).
4. Track C's requests answered (outbox 20261115T191641Z__to-C-sidm__collisions-2-answers.md);
   executables published with READY.

Open:
- Card: P9 (card regression and wave-1 card tests), the new tests on the card, P11 with
  collisions at Kn = 3 over 150 M (both modes): Slurm jobs 4484 (part R) and 4485
  (parts N, C) queued behind 14 jobs (estimated start 00:35 and 01:15 UTC). Their
  verdicts land in `scratch/core/exe/core_collisions-2/CARD_TESTS.log`; their run
  manifests (runreg.py, hand-written, untracked until committed) in `tracks/core/runs/`.
  The next core session must commit those manifests, look at the figures, record the
  outcomes against the predictions Rc, Nc, C of 16:22 UTC (the C prediction: `cell`
  raises sum M W_p by 3.6e-5 to 6.8e-5, `particle` changes sum M H_p by less than 1e-12
  of its value, collisions within 4 sigma, central lapse within 0.01, mass radii within
  5 percent), and update READY. The stale-object cause of the first crash is supported
  by file times only until the smoke test runs.
- Not tested: `coll_energy` with an evolving metric over many collision times (the
  cluster run above is the first), adaptive refinement, MPI, heat conduction (T6-T8 of
  Track C).
- The comment of `NrpicCollideOptions::ext` in `particles.hpp` says columns 32 to 35;
  they are 32 to 36 (comment only; left so that the published build matches the source).
- Shared-file lines touched: `interfaces/collisions.md` section 11.5.

## 2026-11-19 14:00 UTC  closing session of coll2 (wave 2b): reading, state of the card jobs, predictions

Merged `main` (71acd0c: decision 0016, kb/main; no change under `athenak/src`). Read
`CLAUDE.md`, the charter to the end of "Owners", brief lines 688-706 and 834-860,
decisions 0010 and 0016, the wave-2 report of this package
(`scratch/orch/wave2_reports/core.md`, section core:coll2) and the harness report, this
journal. The previous session ended with card jobs 4484 and 4485 queued; 13 run
manifests of these jobs were untracked (committed now with a hand-written fourteenth,
0093aab).

### What the card jobs did (sacct; `CARD_TESTS.log`; logs `scratch/core/tmp/coll2/gpu3_{R.4484,NC.4485}.log`)

- 4484 (part R), 20:39-20:49 UTC on 2026-11-15, completed (0.169 card-hours of
  allocation): smoke test of the clean card build f46f159 (static metric with
  collisions, perturbing force) exit 0 and 0; the five existing set-ups
  (core-20261115-203944-6817f49); the wave-1 collisional boxes rate, relax, repro,
  conv_dt, curved with the new executable and with the release one
  (core-20261115-204006, -204416, -204635, -204655, -204831-6817f49 against the release
  runs -204242, -204534, -204645, -204741, -204921-6817f49).
- 4485 (parts N, C), 20:49-21:39 UTC, TIMEOUT at its 50-minute limit (0.837
  card-hours): completed the smoke test, gradient (core-20261115-204949-6817f49, 58 s)
  and replay (core-20261115-205047-6817f49, 149 s); the G4 run
  core-20261115-205317-6817f49 ran with the driver's defaults (1e6 particles, 600
  steps, not the 1e5 and 400 of the processor run) at 2.5 s per step on the card
  (`athena.log`: 1481 s and 1784 s for 600 steps, the two modes sharing one card):
  cell_s0 and particle_s0 complete, cell_s1 cut at cycle 528, particle_s1 at cycle
  335, no analysis. T12/G3 on the card and the cluster (part C) never started.
- Card time of this package so far: 0.087 (first session) + 0.169 + 0.837 = 1.09
  card-hours of allocation.
- The smoke test passed in both jobs: the clean card build runs the decks on which
  every run of the incremental build crashed (SIGSEGV at start, runs
  core-20261115-171107 ... -172223-cdd7c88).

### First look at the completed card tests (numbers from the run directories)

- Five existing set-ups (core-20261115-203944-6817f49, `run.log`): c1 and c2 identical
  to the release; c3, c4, c5 not reproducible run to run on the card in 2, 2, 3 files,
  and exactly these differ: the verdict of wave 1. First half of Rc held.
- Gradient (core-20261115-204949-6817f49, `run.log`, `fig_gradient.png` looked at): all
  four cases within 1.6 standard errors of the reference with the cell rate, both
  modes; `particle`: change of H_a + H_b per collision 6.7e-17 to 3.6e-16, no pair
  without a root, rejected shares within 0.9 se. Nc for G1/G2 held on the card.
- Replay (core-20261115-205047-6817f49, `summary.json`, `fig_replay.png` looked at): 13
  cases, numbers of tested pairs, collisions, updates equal between card and twin,
  momenta within 1.43e-14 of max(1, |u|) (criterion 1e-13), untouched particles
  bit-identical, pairs without a root equal (one in static_particle_factor2 in both).
  G2(e) held on the card.
- Collisional boxes against the release card executable (`rerun_wave1_card_f46f159.json`):
  25 of 43, 108 of 116, 111 of 135, 27 of 46, 18 of 23 files differ, among them particle
  snapshots (all after the initial one) and `box.nrpic.hst`. The second half of Rc
  ("particle snapshots byte-identical") FAILED. In the null run of the rate test
  (sigma = 0, operator on) only `box.coll.hst` differs. Both executables are
  reproducible on their own: each passes the reproducibility test (identical
  snapshots for 1, 8, 64 MeshBlocks; runs -204635 and -204645, `summary.json`
  `mesh_layouts_identical: true`). In the first three rows of the rate history
  (theta1_plain) n_tested, n_coll, n_updated agree and the pair defects dE (1e-20)
  differ.

### Predictions before the analyses of this session (14:20 UTC)

D  Card differences (`card_diff.py` on the five pairs above). Candidate cause
   [JUDGEMENT, to be bounded here]: the card compiler contracts the floating-point
   operations of the changed collision kernel differently (the processor build, which
   is byte-identical, does not use fused multiply-adds); the push is not involved.
   Predicted: (a) every integer column of every differing `coll.hst` (ncycle, n_part,
   n_cells, n_tested, n_coll, n_updated, n_trunc, max_nsub, min_N, n_bad_cells) is
   identical in every row; (b) every differing snapshot holds the same particles
   (tags) and differs by less than 1e-12 in x and in u/max(1, |u|); (c) the first
   differing snapshot of every run is the first one written after a collision step.
   Refuted by a differing count or a snapshot difference above 1e-12: then the two
   executables collide differently (an acceptance flipped, or a behaviour change),
   and only statistics can be compared.
G4c Equilibrium in the well on the card (analysis of run core-20261115-205317-6817f49
   with `run_tolman.py --analyse`; 1e6 particles, 600 steps of 0.01, theta_inf = 0.2,
   about 85 collisions per particle). Complete runs cell_s0 and particle_s0:
   `particle`: change of sum M H in the collision steps below 1e-12 of its value,
   total below 1e-6; late cos(phi) amplitude of ln(theta alpha) within 0.5 percent of
   zero (the standard error with 1e6 particles is about 0.07 percent, so also within
   4 se); no pair without a root; rejected share 5.7e-3 of the proposals (reference
   run core-20261115-163914-74b3e87) within 4 binomial sigma.
   `cell`: gain of H per collision in the first collision time equal to the reference
   3.62e-4 within 4 se; total gain between 0.3 and 1.2 of what the initial rate gives;
   late amplitude between -2 and -10 percent (processor: -3.8 and -3.4 percent).
   The cut seed-1 runs are reported to their last record, without a verdict.
   Refuted by any criterion failing on a complete run.
A  Analysis mode of `run_cluster.py` (new: `--prepare`, `--analyse RUNDIR --ic DIR`):
   applied to the processor run core-20261115-160913-0656925 (Kn = 0.03, two steps,
   both modes) it reproduces every number of that run's `summary.json` except the wall
   times. Refuted by any other difference (the split would then change the analysis).
Ct Step time of the cluster on the card (P11 deck, Z4c, six levels, 1e4 particles,
   Kn = 3, cells of 2 M, dt = M/8): wave 1 measured 0.21 s per step for `off`, `kn3`
   with the operator of core-v0.3 (runs core-20261115-140316-8742cdf,
   -142625-67f8c1d: 252 s for 1200 steps). Predicted for the new executable: 0.19 to
   0.25 s per step for off, kn3_cell and kn3_particle alike (the per-particle metric
   pass of `particle` costs one interpolation per particle, 1e4 particles). Measured
   with a card batch of the three runs to t = 5 M (40 steps); the full job is sized
   from it as 3 x 1200 x (measured step time) x 1.3 plus start-up.
C  Cluster at Kn = 3 over 150 M on the card (restated from 2026-11-15 16:22 UTC with the
   processor run Cp): `cell`: the collision steps raise sum M W_p by 3.6e-5 to 6.8e-5
   of its value (wave 1: 5.2e-5) and sum M H_p by more (ratio about 1.5 as in Cp:
   1.55), between 5e-5 and 1.5e-4. `particle`: the collision steps change sum M H_p by
   less than 1e-12 of its value (about 5000 collisions); at most five pairs without a
   root; rejected collisions below 2 percent of the proposals; collisions equal to
   those of `cell` within 4 sigma; central lapse within 0.01 of the `cell` run at all
   times; radii of 10, 50, 90 percent of the rest mass within 5 percent of the `cell`
   run; both modes: rest mass identical to the bit, no particle excised or escaped,
   deposit identity below 1e-12, collisions against sum_P within 4 sigma. Refuted by a
   change of sum M H_p in `particle` above 1e-12, or a structural difference beyond
   these bounds: then `particle` does not work in an evolving metric on the card.

## 2026-11-19 14:30 UTC  outcomes A, D, G4c; prediction for the crash test X

### A: analysis mode of run_cluster.py, run core-20261119-140950-7aacfe6. Passed.

`--analyse` on the processor run core-20261115-160913-0656925 reproduces its
`summary.json` with 0 differences outside the wall times (`compare.txt`); the new block
`compare_energy_modes` of that run: lapse 8.4e-9, radii 1.5e-11 apart between the modes,
773 against 772 collisions. `fig_cluster.png` looked at (as the original).

### D: card differences, run core-20261119-141059-f3ccf56. (a), (c) held; (b) FAILED as written.

`card_diff.json`, `fig_card_diff.png` (looked at).
(a) Every integer column of every differing `coll.hst` identical in every row, all five
    tests (n_tested, n_coll, n_updated, ...): the two executables test and accept the same
    pairs in every step; no acceptance flipped.
(b) Same particles (tags) in every snapshot; |du|/max(1, |u|) at most 2.1e-14 (rate),
    7.1e-15 (relax), 1.8e-15 (repro), 1.8e-14 (curved), conv_dt no snapshot differs; but
    |dx| reaches 2.4e-12, 2.6e-12, 1.9e-12 (rate, relax, curved), above my bound of 1e-12.
    The bound was absolute while the box lies at x = 100 to 101: 2.6e-12 is 2.6e-14 of the
    coordinate, the momentum differences of 1e-14 carried over up to 25 output intervals.
    Failed as written; the size is rounding of the coordinates.
(c) The first differing snapshot is number 1 (the first after a collision step) in every
    run; 2 in the restarted runs (restart from snapshot 1). The differing floating-point
    history columns are the sums over the collision step (sum_MW to 2.4e-16 relative,
    sum_Mu_i to 3e-14 of their small totals, sum_P 1e-15, max_P 2e-15) and the pair
    defects (dE, dP, abs_dE: values at rounding level, 1e-20, that differ by order one).
So the new card executable, with the options absent, is not byte-identical to the
release one in collisional runs; it collides the same pairs with momenta that differ by
rounding (2e-14 at most). Each executable is deterministic on its own (reproducibility
test passed for both). Cause [JUDGEMENT, not tested]: code generation of the card
compiler for the collision kernel, whose source gained the branches of `coll_energy`
around unchanged arithmetic; the processor build of the same source is byte-identical
to the release in all these tests (entries of 2026-11-15 18:25 and 19:15). Bound: the
push is not involved (the null run of the rate test, operator on with sigma = 0, has
identical snapshots), and the difference starts in the first collision step.

### G4c: G4 on the card, analysis run core-20261119-141051-b309a9f. Passed.

(`run_tolman.py --analyse` of run core-20261115-205317-6817f49; `fig_tolman.png` looked
at; the run's `run.log` holds the analysis output interleaved with the wrapper's exit
line, because both wrote to it; `summary.json` is complete.)
- particle_s0 (600 steps, 84.8 collisions per particle, 4.24e7 collisions): change of
  sum M H in the collision steps 9.6e-15 of its value (2.8e-16 per collision), total
  including the push +4.7e-9; late cos(phi) amplitude of ln(theta alpha) -0.21 (0.06)
  percent (criterion 0.5 percent; z = -3.5 with an error that treats the snapshots as
  independent; the drawn initial state of seed 0 itself reads -0.47 (0.17) percent, and
  the series scatters between -0.57 and +0.24); no pair without a root; rejected share
  5.704e-3 against 5.669e-3 of the reference (z = +0.6); largest |lam - 1| 0.66.
- cell_s0 (85.6 per particle): sum M H grows by 9.86e-3, 0.78 of the initial rate
  (band 0.3 to 1.2); gain per collision in the first collision time 3.20e-4 against
  3.62e-4 (z = -2.2); late amplitude -3.67 (0.06) percent (band -2 to -10; processor
  -3.8 and -3.4).
- Cut runs, without verdict: cell_s1 (528 steps) +8.70e-3, amplitude -3.65 percent;
  particle_s1 (335 steps) 5.4e-15 in the collision steps, amplitude -0.11 (0.08).
- Momentum along y and z (exact sums of the snapshots): below 1.4e-18 of sum M |u|.
So `coll_energy = particle` keeps Tolman's equilibrium on the card over 85 collisions
per particle with 1e6 particles, and `cell` drifts to -3.7 percent as on the processor.

### Prediction X: the first card crash (before the build and the run, 14:35 UTC)

The incremental card build `.work/build_gpu` still holds the crashed executable (sha256
87f19ec5..., identical to `scratch/core/tmp/coll2/exe/819d588/athena_gpu`), and its nine
objects finished between 07:40:10 and 07:40:35 local time, after the header change of
07:40:08 (particles.cpp.o 07:40:11, particles_pushers 07:40:10, particles_tasks 07:40:12,
nrpic_kick 07:40:19, nrpic_curvature 07:40:27, nrpic_newton 07:40:29, nrpic_io 07:40:34,
and vtk_prtcl, pgen); `athenak/src` has not changed since (git diff f46f159 HEAD:
empty). Test: keep copies of the nine objects, delete them in `.work/build_gpu`, rebuild
incrementally (only they are recompiled and the executable relinked), and run the two
smoke decks of `gpu_job3.sh` (static metric with collisions, 20000 particles, 5 steps;
perturbing force) on the card. Predicted: (a) the build recompiles exactly these nine
objects; (b) the relinked executable runs both decks with exit 0; (c) the snapshots of
the static deck are byte-identical to those of the clean build f46f159 in job 4485
(`scratch/core/tmp/coll2/smoke_card_4485/static`), or, if the two builds compile the
same source differently (different source paths), differ only at rounding with the
same collisions. Refuted by a crash in (b): then the nine stale objects are not the
cause, and the crash remains unexplained (the clean build still runs).

### Sizing of the cluster job (14:35 UTC, before its submission)

The queue filled while the measurement job 4633 waits (seven jobs ahead, four of them
submitted after it); a 150 M job submitted only after 4633 has run would start hours
later. So the 150 M job is submitted now and sized from the step time measured on the
card for this deck in wave 1 (0.21 s per step for `off` and `kn3` with the operator of
core-v0.3: 252 s for 1200 steps, runs core-20261115-140316-8742cdf and
-142625-67f8c1d): three runs of 1200 steps, about 13 minutes; wall limit 25 minutes
(room for a step time up to 0.40 s on average). Job 4633 runs before it in the queue;
if its step time (Ct) does not fit (average above 0.40 s per step over the three
modes), the 150 M job is cancelled before it starts and resubmitted with the measured
size.

### X, processor part (14:19 UTC): the rebuild; the card part is queued (job 4634)

- Before the change `make -n` in `.work/build_gpu` lists nothing to compile: the
  incremental build regards the nine objects as up to date, so the card executable
  built from it would never have been repaired by another incremental build.
- The nine objects were copied to `scratch/core/tmp/coll2close/stale_objs/` (with their
  times, `listing_before.txt`) and removed by name; `scripts/build_gpu.sh .work/build_gpu`
  (43 s) recompiled exactly these nine and relinked (`rebuild.log`). (a) held.
- Stale against recompiled object: eight have the same size (the bytes differ, as two
  card compilations of one source do); `particles.cpp.o`, which holds the constructor of
  the class Particles, is 412312 bytes stale and 411720 recompiled, the constructor and
  the lambdas of `CreateParticleTags` sit at other offsets, and three symbols of the
  stale object (a copy constructor of a Kokkos view tracker of `View<int**>`) are absent
  from the recompiled one. So the stale constructor was compiled from a different
  definition of the class than the source of 819d588 [VERIFIED by the object files]:
  the incremental card build linked objects of two class layouts.
- Relinked executable: `scratch/core/tmp/coll2close/stale_objs/athena_gpu_rebuilt9`
  (sha256 6adc74ce...); its card run (two smoke decks) is registered as run
  core-20261119-141940-2e6368f, Slurm job 4634, waiting behind other owners' jobs.

## 2026-11-19 15:50 UTC  outcomes Ct and X (card jobs 4633 and 4634)

### Ct: step time of the cluster deck on the card, run core-20261119-141042-70c2f5d (job 4633)

40 steps to t = 5 M, one card, the three runs in sequence (60 s of allocation,
0.0167 card-hours). "cpu time used" over 40 cycles (`athena.log`): off 0.261 s, kn3_cell
0.259 s, kn3_particle 0.239 s per step; set-up before the first step 14 s (first run on
the card), 3 s, 1.5 s. Wave 1, same deck over 1200 steps: 0.209 s per step. FAILED as
written for off and kn3_cell (band 0.19 to 0.25 s): 4 percent above it; the 40-step
average carries the work of the first step and of three snapshots, which 1200 steps
spread thinner [JUDGEMENT; the log has no line between cycle 0 and 40 to separate
them]. What matters for the sizing held: `particle` costs no more than `cell` (0.239
against 0.259), and three runs of 1200 steps need 3 x 1200 x 0.26 s = 16 minutes at
most, inside the 25-minute limit of job 4639; the job stays as submitted.

### X: the first card crash settled, run core-20261119-141940-2e6368f (job 4634). Passed.

The incremental card build `.work/build_gpu` with only the nine stale objects
recompiled (executable sha256 6adc74ce..., `athena_gpu_rebuilt9`) ran both smoke decks
with exit 0 (static metric with collisions 5 steps, perturbing force; 22 s of
allocation, 0.0061 card-hours) where the same build with the stale objects crashed at
start in all ten runs of 2026-11-15. (b) held. (c) held in its strict form: every
output file is byte-identical to that of the clean build f46f159 in job 4485
(`box.coll.hst`, `box.nrpic.hst`, `box.part.00000.bin`, `pert.part.0000{0,1}.bin`).
So the crash was caused by the nine objects that the incremental build had compiled
from the class layout before the header change of 07:40:08 and never recompiled
[VERIFIED: a test that could have crashed]. The source is not involved; the published
card executable is a clean build and is not affected. Rule for card builds of this
tree: after a change of `particles.hpp` during a running build, rebuild from clean or
delete the objects that finished after the change.
