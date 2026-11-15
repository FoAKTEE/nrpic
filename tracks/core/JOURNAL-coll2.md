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
