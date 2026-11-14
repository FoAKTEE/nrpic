# Cosmology with NRPIC: test log

Rules as in `docs/TESTLOG.md`: every explanation is written with a prediction before the
run that could refute it; later entries and entries titled "Correction" override earlier
ones; "not determined" where no run isolates a cause. Times are local (PST).

## Plan and design (2026-11-13, 23:40)

Sources of arXiv:1908.05683, 1711.06681, 1904.07841, 2001.07968, 1905.08890, 1101.3555
and 1111.2997 downloaded to `refs/`. Paper 1 and the method part of its predecessor read
in full by me; specifications of papers 2 and 3 being extracted by two agents into
`cosmo/notes/`. Plan in `cosmo/PLAN.md`; working paper `cosmo/paper/main.pdf`.

Design decisions and the estimates they rest on (to be checked by the first tests):
- Lapse condition d_t alpha = -(1/3) alpha^2 K gives alpha = a on the homogeneous
  solution, so t is conformal time and the time step can stay fixed. Estimate: a = 1 to
  56 takes 2 (sqrt(56) - 1)/H_0 = 13.0/H_0 = 3.2 box lengths (L = 4/H_0), i.e. 830 steps
  at 64 cells per side and a step of a quarter cell.
- Constraint solve with the particles held fixed: linearized Hamiltonian operator
  Laplacian - (5/12) K^2 - 2 pi E = Laplacian - (9/2) H^2 on the background.
- Relativistic Zel'dovich displacement: divergence of the displacement equals
  -(delta_N - 5 psi_N); for the single-wavelength data of paper 1 the displacement is
  (1 + 7.5 (H/k)^2) = 4.04 times the Newtonian one.

## C0, first test: homogeneous dust universe (23:40)

Code changes (commit follows the test): periodic wrap of particles and clouds, proper
time per particle, null particles in the midpoint pusher, additional probes, mesh
statistics in the history (proper volume, mean K, extrema), cosmological constant as a
source, problem generator for cosmological data (homogeneous, or fields from a file).
Run `cosmo/flrw_n32_cpu`: 32^3 cells, 32^3 lattice particles at rest, H_0 = 1, box 4,
conformal-time lapse condition, zero shift, to t = 2.
Written before the run: the fields have no spatial dependence, so the code integrates
ordinary differential equations with fourth-order Runge-Kutta at a step of 1/32. At
t = 2: lapse and scale factor 4 (relative error below 1e-5), mean K = -3/8, proper
volume 4096, probe energy density rho_0/64 = 1.8651e-3, probe proper time 14/3, all to
the same relative accuracy; every particle within 1e-10 of its lattice site and with
proper time 14/3; all 32768 particles kept. A larger error, a drift of particles, or
particles lost at the periodic boundary would mean a defect in the new code.

Result (`cosmo/flrw_n32_cpu`): the particle part behaves as predicted (no particle
lost, none displaced, deposited density uniform to the last digit, mesh integral equal
to the particle sum). The spacetime does not: at t = 2 the lapse is 3.682 against 4
(8 percent low), the density 4.2 percent high, the proper volume 4.0 percent low, the
proper time 4.50 against 4.67; the Hamiltonian-constraint norm rises from 3e-30 to 0.66
and the Z4c variable Theta to 2.0. Prediction refuted.
Cause, with its test. The coupling of the method holds the matter sources fixed during
the stages of a spacetime step. The energy density is the particle sum divided by the
volume element, and in an expanding universe the volume element changes at three times
the Hubble rate: 9 percent per step at the start of this run. Holding it fixed is a
first-order error in time with that coefficient. (In the isolated systems of the first
project the sources change little over a step.) Change: the particle module hands the
spacetime solver the sources as densities (sources times sqrt(gamma), which change only
through the motion and the Lorentz factors of the particles), and the solver multiplies
them by 1/sqrt(gamma) = chi^(3/2) of each stage (`<particles> source_density`).
Optionally the densities are extrapolated to the middle of the step from the last two
deposits (`source_extrap`), which makes the coupling second order in the slow part too.
The specification of paper 2 extracted in the meantime shows that its authors refresh
the same chi^(3/2) factor between particle updates.
Written before the rerun (`cosmo/flrw_n32_cpu_sd`): with densities converted per
stage the homogeneous run is again a set of ordinary differential equations integrated
at fourth order; lapse, density, volume, mean K and proper time agree with the exact
solution to better than 1e-5 at t = 2 and the constraint norm stays below 1e-8.

Result (`cosmo/flrw_n32_cpu_sd`, densities converted per stage, extrapolation on): at
all times to t = 2 (a = 4) the lapse agrees with a to 1.9e-7, the density with
rho_0 a^-3 to 1.1e-6, the mean K to 3.8e-7, the proper volume to 1.1e-6; the constraint
norm stays below 3.7e-10 and Theta below 1.1e-11. Confirmed for these. The proper time
of the probe and of every particle is 4.666747 against 14/3 = 4.666667, a relative
error of 1.7e-5, larger than the 1e-5 I wrote: the proper time is advanced with the
lapse averaged over the step (second order), whose error T dt^2 alpha''/24 = 8.1e-5 is
what is measured. It falls by four per halving of the step.
What the test establishes: periodic particles and clouds work; the cosmology setup
works; the lapse condition gives conformal time; with density-form sources the code
reproduces the matter-dominated universe to 1e-6 at 32 cells and a quarter-cell step.
The first-order error of the published coupling in an expanding background is the
first finding of this extension.

## C1: constraint-solved initial data; a deposit artifact of lattices at cell centres (00:10)

`cosmo/ic/cosmo_id.py` solves the Hamiltonian and momentum constraints on the torus for
given particles and K with Fourier transforms, forming the sources as the code does.
Checks: homogeneous lattice gives psi = 1 exactly; a manufactured conformal factor is
recovered to 1e-15; a transverse momentum density gives the analytic traceless
curvature. `cosmo/ic/make_east.py` builds the data of paper 1 (lattice, relativistic
Zel'dovich displacement, masses, dictionary K and lapse).
- First attempt, particles at cell centres: the solved conformal factor differed from
  the dictionary by 23 percent of its perturbation at an amplitude of 1e-4, where the
  two must agree. Cause: a particle at a cell centre sits on the cusp of the
  cloud-in-cell weight; where the displacement changes sign (density peak and trough)
  both neighbours leak into each other's cells, and the two cells next to the peak
  receive a contrast of 1.5 times the true one (seen directly in the deposit: 5.97e-4
  against 3.7e-4 in the neighbours). This is the same mechanism as the lattice beat of
  the dust ball in the first project.
- Lattice shifted by half a spacing (particles at cell corners, each shared by eight
  cells; the undisplaced lattice still deposits an exactly uniform density): the
  difference falls to 0.7 percent of the perturbation at 1e-4 and is 4 percent at 1e-2
  and 15 percent at 5e-2, i.e. second order in the amplitude, as paper 1 states for its
  own nonlinear correction. Two particles per cell and direction behave the same.
- The momentum constraint leaves a residual at the Nyquist wave number of the mesh
  when the sources are not filtered (1.5e-3 at 5e-2 amplitude; centred differences
  cannot balance it); one binomial pass removes it (1.6e-6). The cosmological runs use
  two passes with compensation.

First run with these data: `cosmo/east_d1e-4_n32_cpu`, amplitude 1e-4, 32^3 cells,
shifted lattice of 32^3 particles, to t = 18 (a = 100). Written before the run:
(1) the code's own Hamiltonian-constraint norm at t = 0 is below 1e-6 (the terms are of
order 6); (2) the observer density contrast at the two probes follows linear theory,
delta_obs = +-3 delta [a_p + 3 (H/k)^2 a_p^(-3/2)] with 3 (H/k)^2 = 1.216, where the
second term comes from the offset between the initial slice and a slice of constant
proper time; at 32 cells the probe value is reduced by cos(k h/2) and the deposit
window to 0.994 of this; agreement within 2 percent up to a_p = 30, and departures of
the order of the contrast itself beyond (the peak contrast reaches 0.03 at a_p = 100).
A failure of (1) means the solver and the code disagree on the constraints; a failure
of (2) by a constant factor means the dictionary or the displacement is wrong; a wrong
growth law means the evolution is wrong.

Result so far (`cosmo/east_d1e-4_n32_cpu`, at a = 17 of 100): (1) the code's own
constraint norms at t = 0 are 6e-10 (Hamiltonian) and 8e-10 (momentum): confirmed, the
solver and the code agree on the constraints. (2) The observer density contrast is
0.9955 to 0.9993 of linear theory at both probes up to a_p = 10 and agrees with the
Newtonian reference to 0.44 percent: confirmed so far. The Newtonian reference itself
(`cosmo/newton/pm.py`) is 0.992 to 0.993 of linear theory up to a_p = 30, the window
factor of the probe. (My first comparison of the Newtonian run with linear theory was
off by up to 77 percent at a = 2: the proper time of the observers was integrated with
the trapezoidal rule over four steps, whose error equals the signal at this amplitude;
the background part is now exact. The code's probe proper time is third order now.)

## C2: production runs of paper 1, written before the runs (00:20)

Runs `cosmo/east_d{0.0025,0.005,0.01,0.05}_n64`: 64^3 cells, 64^3 particles on the
shifted lattice, two filter passes with compensation, zero shift, conformal-time lapse
condition, to a = 1.4/delta (2.5 times the scale factor at which the linear contrast
of the peak reaches 1.686). Newtonian reference at the same mesh, filter and step.
Predictions:
(a) Underdensity: the two calculations agree in delta_obs(a_p) to better than 2
    percent of 1 + delta_obs for the three lower amplitudes (paper 1: indistinguishable).
(b) Overdensity: the peak density rises steeply at a_p near 0.56/delta in both; the
    relativistic rise comes later than the Newtonian one by an amount that grows with
    the amplitude: not resolvable at 0.0025, clear at 0.05 (paper 1: Newtonian collapse
    earlier, most pronounced at 0.05).
(c) Not known in advance: whether zero shift with this lapse condition carries the run
    through shell crossing and the formation of the bound region. Paper 1 used a damped
    harmonic gauge. If a run stops at the collapse, the gauge is the first suspect.

## C3, first test: light rays in the homogeneous universe (00:27)

Code: a ray waits at its point until its emission time; at the launch its coordinate
direction is turned into the null momentum of unit frequency for the normal observer
(`nrpic.cpp`). Initial data: bundles of five rays (centre and four neighbours at an
opening of 1e-4) from two points towards each other (`cosmo/ic/ray_ic.py`). Analysis:
redshift from the deposited matter velocity, area distance from the cross section of the
bundle over its solid angle at the emitter (`cosmo/analysis/ray_obs.py`).
Run `cosmo/flrw_rays_n32_cpu`: the homogeneous universe of C0 with bundles emitted at
t = 0 (a = 1) and t = 0.84375 (a = 2.022), to t = 2 (a = 4).
Written before the run: in conformal time the rays are straight lines at unit coordinate
speed, so the test checks the launch and the bookkeeping of the analysis, not the
integrator. (1) 1 + z = a(t)/a_e to 1e-5 along every central ray (largest z: 3 and
0.98). (2) D_L equals (2/H_e)(1+z)^2 (sqrt(1+z) - 1) to 1e-5 at all records. (3) The
solid angle per unit opening squared is 1 to 1e-7. A constant factor in (2) means a
wrong solid angle or projection; a drift with z means a wrong redshift or emission time.

## C1 result: linear regime to a = 100 (00:30)

`cosmo/east_d1e-4_n32_cpu` complete (576 steps, a = 100). Against the prediction of
00:10: (1) confirmed earlier. (2) The observer density contrast stays within 0.5
percent of linear theory at both probes up to a_p = 30 (predicted: within 2 percent)
and departs by +0.75 percent (overdensity) and -0.70 percent (underdensity) at
a_p = 100, where the contrast is 0.03; the Newtonian reference departs by +0.5 and -1.5
percent there. The two gravities differ by 0.30 percent (overdensity) and 0.77 percent
(underdensity) of the contrast at the end, i.e. by 1e-4 and 2.4e-4 of the density.
Confirmed. Figure `cosmo/analysis/figs/delta_obs_d1e-4_n32.png` (inspected: the three
curves coincide in the upper panels; the residuals are smooth, without oscillation).
Correction to the C0 entry: the constraint numbers quoted there (3.7e-10, 0.66) are the
history column, which is the square of the norm. The root mean square of the Hamiltonian
constraint over the box relative to its largest term 16 pi rho is 2e-6 with densities
converted per stage and 0.15 with sources held fixed (figure `cosmo/paper/figures/
fig_flrw.png`).
What C1 establishes: the initial data, the evolution in the conformal-time slicing and
the Newtonian reference with its dictionary agree with each other and with linear
theory over two decades of expansion at 32 cells per wavelength.

## C3, first test: result (00:35)

Result (`cosmo/flrw_rays_n32_cpu`; figure `cosmo/analysis/figs/ray_test_flrw.png`,
inspected): (1) redshift within 8.9e-7 of a/a_e - 1 on all bundles: confirmed. (3) solid
angle per unit opening squared 1 - 1.0e-8: confirmed. (2) D_L is low by 1.2e-4 at the
start of the rays emitted at a = 1 and by 6e-5 for those emitted at a = 2, falling
slowly along the ray: refuted at the 1e-5 I wrote. Cause, with its test: the pusher
takes the metric at the middle of the step as the mean of the two time levels, and the
mean of the lapse over the root of the mean of gamma_xx is 1 - (H_c dt)^2 / 8 for a
power-law expansion, H_c the conformal Hubble rate; the coordinate speed of light is low
by that. The distance error computed from this formula agrees with the measured one to
6e-7 on every record of every bundle. It is the second-order time error of the pusher,
not a defect of the ray bookkeeping; at 64 cells (step 1/64) it is 3e-5 at a = 1 and
falls as 1/a. The same factor multiplies the velocity terms of the matter particles.
What the test establishes: launch, solid angle, cross section and redshift are right.

## C2, first runs: outcome against the predictions written before them (00:38)

Runs `cosmo/east_d{0.0025,0.005,0.01,0.05}_n64` (25 steps per second on one GPU; 21 to
120 s each) and `cosmo/newton_d*_n64`; analysis `cosmo/analysis/east_c2.py`, figures
`cosmo/analysis/figs/east_{delta_obs,splash,rel_eff}.png` (first one inspected).
(c) Answered: with zero shift and the conformal-time lapse condition the three lower
    amplitudes run through shell crossing to the end (a = 140, 281, 561) with every
    particle kept. The extreme case stops at a = 18.6 of the background: from a = 14.6
    the lapse at the overdensity falls (10.8 to 4.1) while the density there rises
    without bound, then a negative lapse appears. The Newtonian dictionary fails
    earlier, at a = 14.4, where 1 + 2 psi_N turns negative (paper 1: |psi| ~ 1/2 after
    a 15-fold expansion; relativistic run not continued indefinitely, black hole
    forming). This slicing does not avoid the singularity; following the black hole
    needs another lapse condition near it and mesh refinement.
(b) Direction confirmed, size not credible: the relativistic collapse is later by 5,
    9, 14 and 23 to 28 percent in a_p of the first crossing of the fiducial observers.
(a) Refuted: the densities at the underdensity differ by up to 8, 15 and 24 percent
    for the three lower amplitudes, and the two curves differ already at a_p = 1 (at
    amplitude 0.05: delta_obs -0.43 against -0.33 at the underdensity, +0.24 against
    +0.33 at the overdensity).
Cause, with its test. The deposited density of the relativistic data is 0.5 percent
below its target at both probes at amplitude 0.01 and 7 and 14 percent below at 0.05,
i.e. quadratic in the amplitude, while its mean over the box is right. The
cloud-in-cell deposit of a lattice compressed by a fraction c is modulated by c^2 per
direction (the lattice harmonic no longer falls on a zero of the cloud shape), with a
long wavelength h/c that the filter does not remove, and a lattice point that sits on a
cell corner, as at both probes, is at the minimum of the modulation. The relativistic
data displaced the lattice by 1 + 7.5 (H/k)^2 = 4.04 times the Newtonian displacement
(so that equal masses give the coordinate density), hence 16 times the modulation of
the Newtonian run. For cold matter only the density and velocity fields matter, not how
the mass is divided among the particles, so the relativistic data can use the Newtonian
positions and carry the rest of the density in the masses; the two calculations then
start from identical positions and share the modulation.
Also found: (i) the constraint norms of the history are blank after a = 4 (the
diagnostic leaves out cells with chi < 1/16, meant for punctures; switched off with
`<z4c> excise_chi = 0` for cosmology). (ii) Up to a = 4 the constraint violation relative
to its largest term grows to 3e-4, 1e-2 and 1e-1 for amplitudes 0.0025, 0.01, 0.05
from 1e-11 to 4e-4 at t = 0: the deposit does not satisfy the continuity equation of the
mesh, and the violation follows the lattice modulation. This is the case for the
constraint-compatible deposit (T1). (iii) The filter with compensation leaves cells of
negative energy density next to the collapsed region (-1e-3 of the peak).
Written before the rerun (`cosmo/east_d*_n64_v2`: Newtonian positions, masses carry the
relativistic density; otherwise unchanged): the observer density contrasts of the two
calculations agree at a_p = 1 within 1 percent of the contrast at both probes for
amplitudes up to 0.01; the underdensity densities agree within 2 percent for the three
lower amplitudes at all times; the delay of the relativistic first crossings falls below
1, 2 and 4 percent for 0.0025, 0.005 and 0.01. If the delays stay at 5, 9 and 14 percent
the explanation is wrong.

Note on the times in the headings: from here on they are read from the clock when the
entry is written; the earlier ones were estimates and can be off by several minutes
(the order of the entries is the order of the work).

## T1a: sampling error of a compressed lattice against the cloud shape (00:49)

Question raised by the first C2 runs: does a smoother cloud remove the deposit error?
Expectation written in the previous entry's terms: the first lattice harmonic leaks
through the cloud shape as [sin(pi h/s)/(pi h/s)]^p, i.e. c^2 for the linear cloud
(p = 2) and c^3 for the quadratic one (p = 3).
Measured (`cosmo/paper/scripts/make_data_shape.py`, one dimension, uniform target
density, exact Jacobian in the masses, worst case over forty lattice offsets and over
the mesh; figure `cosmo/paper/figures/fig_shape.png`, inspected):
- linear cloud: 0.5 c (0.0092 at c = 0.02, 0.044 at 0.1, 0.079 at 0.2);
- quadratic: 0.4 c^2 (1.8e-4, 3.9e-3, 1.3e-2);
- cubic: 0.4 c^3 (4.2e-6, 3.9e-4, 2.5e-3);
after two filter passes with compensation; without the filter the errors are twice
these. Two particles per cell and direction halve them and cap them (0.02, 2e-3, 3e-4
for the three shapes); four per cell cap the linear cloud at 0.005.
So the expectation was wrong by one power of c: all harmonics of the lattice leak with
the same power, and where a particle meets a kink of the cloud shape they add up. The
c^2 that I measured at the probes of the first C2 runs is the special case of a lattice
point on a cell corner (exactly -c^2 per direction for c < 1/4), not the general size
of the error. The filter does not help because the pattern has the long wavelength
h/c. Consequences: (i) with the linear cloud and one particle per cell the deposited
density of a cold lattice is wrong by 5 to 10 percent in places once the compression
reaches 0.1 to 0.2, in both the relativistic and the Newtonian calculation; (ii) the
setup of paper 1 (linear cloud, four particles per cell and direction) is at 0.5
percent; (iii) a cubic cloud with two particles per cell is at 3e-4.
Code: `<particles> deposit_shape = cic | tsc | pcs` (B-splines of degree one to three;
the constraint solver and the Newtonian reference use the same shape).
Written before the runs `cosmo/east_d*_n64_{tsc,pcs}` (identical to the v2 runs except
for the shape): at amplitude 0.01 the constraint violation up to a = 4, relative to its
largest term, falls from 1e-2 (linear cloud, first runs) by at least a factor of ten
with the quadratic cloud and a further factor of five with the cubic one; the observer
density contrast at both probes at a_p = 1 is within 0.1 percent of 6.648 times the
amplitude for the cubic cloud; the first-crossing times of the two calculations change
by less than 2 percent between the shapes (the collapse is set by the large scales).

## C5, tests A0 and A of paper 2: homogeneous universe over a thousandfold expansion (01:00)

Paper 2 (Daverio, Dirian & Mitsou): box of 64 Mpc/h, 8, 16, 32 cells, one particle per
cell, step 0.1 of the cell, from z = 1000 to 0; test A0 exact data, test A white noise of
amplitude 1e-7/N_g^2 on every field and 1e-7/N_g^3 on the particles. In the units of this
code (initial Hubble rate 1, a = 1 at the start): box 0.67542 (its size in initial
Hubble radii), end at a = 1001, t = 61.277. Noise amplitudes carried over with their
units: Atilde and Theta times 0.09466, Gamma times 94.76, particle positions
1.055e-9/N_g^3, momenta 1.001e-4/N_g^3. Code: `<problem> noise_amp` etc. in the
cosmology problem generator, `make_lattice.py --noise-x --noise-u`, constraint
statistics (`<particles> cstat_dcycle`: maxima and cell means of the constraints,
absolute and relative to their terms; extrema of chi, K, E).
Runs `cosmo/dav_a0_n{8,16,32}` and `cosmo/dav_a_n{8,16,32}`.
Written before the runs:
A0. The fields stay homogeneous and the test is the time integration of ordinary
    differential equations. The relative errors of chi and of E against the exact
    solution converge at fourth order with the cell number at fixed step ratio (factor 16
    per halving), with levels of 1e-9 to 1e-8 at 8 cells at the end (paper 2: 2.6e-9 and
    3.8e-9), since the lapse condition is the same and both codes use fourth-order
    Runge-Kutta.
A.  The evolution is stable to a = 1001: the error of chi does not grow after an initial
    transient, the error of E grows more slowly than a, and the largest constraint
    violations fall by orders of magnitude (paper 2: H from 5e-4 to 4e-12, M from 1.5e-4
    to 2e-12 in its units), with finer meshes lower. Not known in advance: how fast the
    constraints fall in Z4c with a constant damping coefficient of 0.02, where paper 2
    damps at a rate proportional to the expansion rate. A blow-up, or a constraint
    violation that grows relative to its terms, would mean that the method does not
    tolerate grid-scale noise in an expanding background.

## C5, test B of paper 2: plane-wave linear mode over a thousandfold expansion (01:05)

Paper 2: delta = 1e-7 sin(2 pi x / L), L = 128 Mpc/h (1.35 initial Hubble radii, so the
mode starts outside the horizon and ends well inside), 32, 64, 128 cells, 27 particles
per cell, step 0.1 of the cell. Here: box 1.35085, amplitude 1e-7, quadratic cloud as in
paper 2 and no filter, 8 particles per cell, 32 and 64 cells, step 0.25 of the cell and
once 0.1 at 32 cells; constraint-solved data from `make_east.py --ratios 1,0,0`; fields
along the x line recorded (`<particles> line_dcycle`).
Check of the data at 16 cells: phi = (chi - 1)/2 has the amplitude 6.75e-9 against the
analytic 6.93e-9 (cloud window), density contrast 1.11e-7 against 1.139e-7.
Written before the runs `cosmo/dav_b_n{32,64}`, `cosmo/dav_b_n32_c01`:
(1) phi stays constant in time: the change of its amplitude over the run is below 5
    percent at 32 cells and falls by about four per doubling (paper 2: +4.9, +1.0,
    +0.25 percent at 32, 64, 128 cells).
(2) The density contrast follows delta(t) = -2 [1 + k^2/(3 H_c^2)] phi_0, H_c the
    conformal Hubble rate: largest departure over the mesh, relative to the largest
    contrast, below 5e-2 at 32 cells at the end, second order in the cell size (paper 2:
    3.6e-2, 9.1e-3, 2.4e-3).
(3) The largest relative Hamiltonian constraint stays below 1e-6 (paper 2: 5e-9 to 1e-7
    at the end, growing with resolution, which its authors do not understand).
(4) The step ratio 0.1 instead of 0.25 changes (1) and (2) by less than a tenth of
    their values (the error is spatial).

## E1, first step: a lapse condition for the collapsing overdensity (01:11)

The conformal-time condition d_t alpha = -(1/3) alpha^2 K keeps alpha / gamma^(1/6)
fixed at every point (zero shift), so the lapse reaches zero only with the volume
element: the extreme case ran into the singularity (C2 first runs). Alternative in the
same family, d_t alpha = -(1/3) gamma^(1/6) alpha K (`<z4c> lapse_volume = 1/3`,
`lapse_harmonic = 0`): the homogeneous universe again has alpha = a, and now
alpha - gamma^(1/6) is fixed at every point. At the overdensity that constant is
negative (about 2 psi_N = -0.18 for the amplitude 0.05), so the lapse goes to zero when
the local gamma^(1/6) has fallen to 0.18, before the volume element vanishes, and the
approach is exponential as with the 1+log condition (the right-hand side is linear in
alpha). No explicit time dependence and no global quantity is needed.
Check: homogeneous universe, 16 steps, alpha / a - 1 = -2e-8 (as with the old condition).
Written before the run `cosmo/east_d0.05_n64_lv` (data of the v2 run, new condition, no
particle removal): the lapse at the overdensity turns around near a = 15 as before,
then falls towards zero and stays positive; the run passes a = 18.6, where the old
condition failed, and reaches the end at a = 28 with every particle kept. Not known:
whether 64 cells without refinement can hold the gradients around the frozen region; a
failure by non-finite fields close to the overdensity after a = 19 would point to
resolution, a failure before a = 15 to the condition itself. The slices differ from
those of the other runs at first order in the potential, so only observer quantities
compare.

## C2, rerun with identical positions: outcome (01:22)

Runs `cosmo/east_d*_n64_v2` against `cosmo/newton_d*_n64`; figures
`cosmo/analysis/figs/east_{delta_obs,splash,rel_eff}_v2.png` (first inspected: the
underdensity curves of the two calculations now coincide for the three lower
amplitudes; the overdensity curves separate towards the collapse, more for larger
amplitude). Against the predictions written after the first runs:
- Contrast at a_p = 1: the two calculations differ by -0.33, -0.53, -0.94 percent at the
  overdensity and +0.06, +0.24, +0.60 percent at the underdensity for amplitudes
  0.0025, 0.005, 0.01 (-5.8 and +3.7 percent at 0.05): within 1 percent, confirmed.
  The difference is linear in the amplitude, i.e. second order: it is the nonlinear
  part of the constraint solve (paper 1 reads 4 percent at 0.05 and below 1 at 0.01 in
  its own data).
- Underdensity: densities agree within 0.5, 1.0 and 2.2 percent (predicted 2): confirmed
  for the two lower amplitudes, marginally exceeded at 0.01.
- Delay of the relativistic infall (scale factor at which the distance of a fiducial
  observer first falls below a tenth of its start): 1.4, 2.6, 5.2 percent for 0.0025,
  0.005, 0.01, the same for the four starting distances; predicted below 1, 2, 4:
  exceeded by a third. The first runs had 5, 9, 14: the deposit error accounted for
  most of those, as claimed, but a delay remains.
What remains is linear in the amplitude over a factor of twenty: 1.37, 2.60, 5.15 and
26 percent for 0.0025, 0.005, 0.01, 0.05, i.e. 5.2 times the amplitude, or 2.9 times the
depth of the initial potential at the overdensity. The density probe gives the same
(contrast of 10 reached later by 0.95, 1.9, 3.7, 16 percent). It is not a clock effect:
measured with the coordinate time the delays are the same to 0.1 percent of the scale
factor, and the ratio of proper-time to coordinate scale factor at the infall is the
same in the two calculations (0.9944, 0.9888, 0.9774). So the infall itself is later in
the relativistic calculation, by an amount of second order in the perturbation.
Comparison with paper 1 (read from its figures): 6 to 7, 6, 10 to 11 percent for the
fiducial observers and 1.9, 5.8, 6.9, 31 percent for the density contrast of 10. Its
Newtonian reference had a finer force resolution than its relativistic code, and its
text says that finite resolution delays the collapse; with the same mesh, deposit and
step in both calculations the delay is two to five times smaller for the three lower
amplitudes and proportional to the amplitude.
Not established: what the delay consists of. Candidates: the second-order offset of
the initial data (about 1 percent of the contrast at 0.01, which alone would give a
delay of that size), and second-order terms of horizon-scale origin in the evolution
(the wavelength is four Hubble radii at the start). A test: the same comparison with a
shorter wavelength, where the horizon-scale terms are smaller.

## C5, tests A0 and A: outcome (01:29)

Six runs `cosmo/dav_a0_n{8,16,32}`, `cosmo/dav_a_n{8,16,32}`, all to a = 1001 without
failure (7,258 to 29,031 steps; 20 s to 3 min each on one GPU). Analysis
`cosmo/analysis/daverio_a.py`, figure `cosmo/analysis/figs/daverio_a.png`.
A0 (exact data). Fourth-order convergence: confirmed (errors of chi at t = 100 Mpc/h:
3.9e-9, 2.4e-10, 1.55e-11, ratios 16.0 and 15.7; later 15.8 and 9 to 10 as the finest run
meets rounding). Levels: refuted. The error of chi grows through the run to 1.3e-7,
8.2e-9, 1.1e-9 at the end, where paper 2 has a plateau at 2.6e-9, 1.6e-10, 9.8e-12; the
error of E reaches 1.9e-7 at 8 cells (paper 2: 3.8e-9).
Cause, with numbers. At the end the lapse is alpha / a = 1 - 8.2e-8 and all other errors
are those of a homogeneous solution whose conformal time runs at that rate (chi a^2 - 1
= 1.3e-7 = 2 x 8.2e-8 x t/(2+t), etc.). The lapse condition of Z4c uses Khat = K - 2
Theta, so a nonzero Theta drives the lapse away from conformal time at the rate (2/3)
alpha Theta; Theta, produced by the truncation error of the first steps, is 1.1e-10 at
a = 23, and the integral of (2/3) alpha Theta over the run is a few 1e-8, as measured.
Theta decays slowly because the damping coefficient is constant (0.02) while paper 2
damps in proportion to the expansion rate.
A (noise). Stable: confirmed, at all three resolutions. Constraints: the largest H falls
from 1.2e-5 (t = 100) to 2.5e-10 (t = 3000) at 8 cells, |M| from 9.0e-6 to 1.1e-10, finer
meshes lower by 2 to 4 per halving; paper 2 has 7.4e-7 (t = 500) to 1.8e-10 (t = 3000)
for H: the same decay. Error of chi: follows the A0 error (1.3e-7 at 8 cells), i.e. the
noise does not add to it; refuted only in the sense of A0. Error of E: grows more slowly
than a (dE/a falls from 1.6e-6 to 6.9e-7 after t = 200 at 8 cells): confirmed. Its level
is 700 times that of paper 2 (6.9e-4 at the end against 8.9e-7).
On that factor: with the stated momentum noise (p_i / m uniform in +-1e-7/N_g^3) the
particles drift freely by 4.5e-6 cells over the run at 8 cells, which gives a density
noise of 1e-5 before any gravitational growth, ten times the final value of paper 2 at
every resolution, and its curve grows as the growing mode from the level set by the
noise of chi at the start. So the momentum noise in the runs of paper 2 was much smaller
than my reading of its text; my runs carry the stated amplitude and show its free
streaming followed by growth.
Written before the follow-up runs:
(i) `cosmo/dav_a0k_n{8,16,32}`: exact data with the damping rate fixed per unit of
    conformal time (`<z4c> damp_kappa1_over_alpha = true`, kappa1 = 1): the lapse offset
    and the error of chi at the end fall by more than ten at each resolution, and the
    convergence stays fourth order.
(ii) `cosmo/dav_anp_n{8,16,32}`: the noise of test A without the momentum noise of the
    particles: the error of E at the end comes within a factor of five of paper 2 (8.9e-7,
    1.9e-7, 6.7e-8).

## T1a: cloud-shape study, outcome (01:29)

Runs `cosmo/east_d*_n64_{v2,tsc,pcs}` with the Newtonian runs of the same shape;
analysis `cosmo/analysis/shape_study.py`. At amplitude 0.01 (all three shapes complete):
- Constraint violation up to a = 4, cell mean of the relative Hamiltonian constraint:
  2.0e-4 (linear), 6.0e-6 (quadratic), 9.9e-6 (cubic); relative momentum constraint
  3.8e-2, 1.6e-3, 1.9e-4. Predicted: a factor of at least ten from linear to quadratic
  (found 33 and 24: confirmed) and a further five to cubic (found none for H, 8 for M:
  refuted for H). The Hamiltonian constraint has reached a floor of 1e-5 that the cloud
  shape does not set.
- After the collapse the mean relative Hamiltonian constraint is 1e-2 for all shapes.
- Cells of negative energy density (compensated filter): the most negative value over
  the largest falls from -9e-3 to -7e-4 to -1.5e-4.
- Observer density contrast at a_p = 1 against linear theory 0.066476: relativistic
  +0.065701/-0.066781, +0.066135/-0.066608, +0.065945/-0.066438; Newtonian
  +0.066324/-0.066382, +0.066931/-0.066019, +0.066739/-0.065833 for the three shapes.
  Predicted within 0.1 percent for the cubic cloud: refuted; the values stay within 1
  percent, and the Newtonian ones move by 1 percent with the shape. The probe value
  carries a shape-dependent offset of the order of the compression squared in both
  calculations.
- Infall of the fiducial observers (distance below a tenth), relativistic / Newtonian:
  start L/32: 63.08/59.98, 58.88/56.29, 59.61/56.92; start L/4: 79.74/75.73,
  79.36/75.40, 79.55/75.55. Predicted: changes below 2 percent between shapes:
  refuted for the inner observers, which fall in 6 to 7 percent earlier with the smoother
  clouds in both calculations (the linear cloud holds the central density down); holds
  for the outer ones (0.5 percent).
- The relativistic delay does not depend on the shape: 5.2, 4.6, 4.7 percent (inner),
  5.3, 5.3, 5.3 percent (outer).
What this establishes: the deposit error of the linear cloud is what set the constraint
violation of the smooth phase and delayed the centre of the collapse by several
percent; the quadratic cloud removes most of both; the relativistic delay of C2 is not
an artifact of the deposit.

## C5, test B: first results (01:29)

`cosmo/dav_b_n32` (step 0.25 of the cell) and `cosmo/dav_b_n32_c01` (step 0.1; partial
at the time of writing); analysis `cosmo/analysis/daverio_b.py`.
(1) Amplitude of phi: -6.886e-9 at the start (analytic -6.933e-9), -7.005e-9 at the end:
    +1.7 percent (paper 2 at 32 cells: +4.9 percent). Confirmed.
(2) Largest departure of the density contrast from linear theory, mean over the line
    removed: 7.5e-3, 1.5e-2, 2.0e-2 at t = 100, 1000, 3000 Mpc/h (paper 2: 2.5e-3, 1.8e-2,
    2.9e-2). As paper 2 defines it (exact background) it is 6.4e-2 at t = 100 with the step
    0.25, because the error of the mean density (4.7e-7) exceeds the contrast (1e-7)
    early on; with the step 0.1 it is 8.9e-3. Confirmed.
(3) Largest relative Hamiltonian constraint at the end: 8.3e-8 (step 0.25), 4.4e-9
    (step 0.1; paper 2: 4.6e-9). Confirmed.
(4) Step 0.1 against 0.25: the departure of the density is unchanged (7.43e-3 against
    7.47e-3); the drift of phi is 1.4 against 1.7 percent, a change of a fifth, more
    than the tenth I wrote.
The 64-cell run is in progress.

## E1, first step: outcome (01:32)

`cosmo/east_d0.05_n64_lv`: refuted. The run ends at the same place as with the old
condition (a = 18.6): the lapse at the overdensity turns around at a = 15.8 (10.3) and
falls to 4.5 by t = 6.578 while the density there doubles every four steps; in the next
step 60,000 particles reach a non-finite state and are removed, then all of them. The
fields stay finite. No negative lapse this time.
Why the condition does not help: alpha - gamma^(1/6) is constant, and that constant is
-0.18 at the overdensity, so the lapse vanishes only when the local gamma^(1/6) has
fallen to 0.18. At the failure it is still 4.6: the volume element would have to shrink
by another factor of 17,000. The condition collapses the lapse only as fast as the
local scale factor itself. My estimate in the previous entry had the right formula and
drew the wrong conclusion from it.
What is needed is a lapse that falls by its own size when the local scale factor falls
by a factor of order one, as the 1+log condition does around an isolated object. That
requires a reference for "its own size", i.e. one global quantity. Candidate for the
second step: a driver towards constant mean curvature,
    d_t alpha = -(1/3) alpha^2 K - mu alpha_ref alpha (K - Kbar),
with Kbar the volume mean of K and alpha_ref the largest lapse, both taken once per
step. In a homogeneous universe the second term vanishes; where the matter contracts
relative to the mean the lapse falls exponentially; slices of constant mean curvature
are known to avoid the singularity of a black hole. It changes the slicing of every
region at first order, so it is for this extension only. Not started.

## C4: wavelength test and resolution test, written before the runs (01:35)

Wavelength test. Runs `cosmo/east_d0.01_n64_tsc_L{2,8}` with their Newtonian runs:
amplitude 0.01, quadratic cloud, 64 cells, wavelength 2 and 8 initial Hubble radii
instead of 4, so (H/k)^2 = 0.101 and 1.62 instead of 0.405. The Newtonian calculation
does not depend on the wavelength (its equations have no scale), so its infall times
are those of the 4-radii run; the relativistic one does.
If the relativistic delay is of horizon-scale origin it is proportional to the initial
potential, i.e. to (H/k)^2 at fixed amplitude: 4.6 to 5.3 percent at 4 radii becomes 1.2
to 1.3 percent at 2 radii and about 20 percent at 8. If it depends on the amplitude
alone it stays near 5 percent. I expect the first, possibly with a part that does not
scale. At 8 radii the potential is as deep as for the amplitude 0.04 at 4 radii, so I
expect both calculations to end near the collapse, as for the amplitude 0.05, with the
delay measurable only for the inner observers.
Resolution test. Runs `cosmo/east_d0.01_n{96,128}_tsc` with their Newtonian runs, one
particle per cell. Prediction: the delay changes by less than 0.3 percentage points
between 64, 96 and 128 cells; the infall itself comes earlier with resolution in both
calculations (less smoothing of the centre), by up to a few percent; the constraint
violation of the smooth phase falls with resolution.

## C5, test B: outcome (01:42)

All three runs complete (`cosmo/dav_b_n32`, `cosmo/dav_b_n32_c01`, `cosmo/dav_b_n64`;
figure `cosmo/analysis/figs/daverio_b.png`).
(1) Amplitude of phi, start to end: -6.886e-9 to -7.005e-9 (+1.72 percent) at 32 cells,
    -6.9215e-9 to -6.9518e-9 (+0.44 percent) at 64 cells; ratio 3.9, second order. Paper
    2: +4.9 and +1.0 percent from nearly the same starting values (6.868, 6.918).
    Confirmed.
(2) Largest departure of the density contrast from linear theory, mean removed, at
    t = 100, 1000, 3000 Mpc/h and at the end: 7.47e-03, 1.49e-02, 2.01e-02, 2.34e-02 (32 cells); 1.86e-03, 3.73e-03, 5.06e-03, 5.96e-03 (64 cells)
    (paper 2: 2.5e-3, 1.8e-2, 2.9e-2, 3.6e-2 and 6.2e-4, 4.6e-3, 7.3e-3, 9.1e-3). The
    ratio between the resolutions is 4.0 at all times: second order. Confirmed.
(3) Largest relative Hamiltonian constraint at the end: 8.3e-8 (32 cells), 1.4e-8 (64
    cells) with the step 0.25; 7.6e-9 at 32 cells with the step 0.1. It falls with
    resolution here, where paper 2 finds it growing (4.6e-9, 2.3e-8, 1.1e-7) and says so.
    Confirmed (below 1e-6). The largest relative momentum constraint is not a useful
    number in this test: it is taken at the nodes of the wave, where its terms vanish.
(4) Step 0.1 against 0.25 at 32 cells, both complete: drift of phi +1.70 against +1.72
    percent, density departure equal to three digits. Confirmed. (The "1.4 against 1.7"
    of the previous entry compared a run that had not finished with one that had.)
What test B establishes: in the linear regime the potential stays constant and the
density follows linear theory with second-order convergence in the cell size, with
errors a factor of 1.5 to 3 below those of paper 2 at equal cell number (8 particles per
cell here against 27 there).

## E1, second step: driver towards constant mean curvature (01:48)

Code: `<z4c> lapse_kdriver = mu` adds -mu alpha_ref alpha (Khat - Khat_ref) to the lapse
equation, with alpha_ref the largest lapse and Khat_ref the proper-volume mean of Khat.
First version: references refreshed once per step. Check on the homogeneous universe:
alpha / a - 1 = -2.5e-2 after 12 steps. Cause: K changes by 4.5 percent per step, so a
reference from the start of the step leaves a driver term of first order in the step.
Second version: references taken from the state of each stage (one reduction per
stage): alpha / a - 1 = -1.6e-7 after 12 steps, as without the driver.
Written before the linear-regime check `cosmo/east_d1e-4_n32_kd` (amplitude 1e-4,
32 cells, mu = 1, to a = 10): the observer density contrast at both probes stays within
1 percent of linear theory, as without the driver, because it does not depend on the
slicing; the lapse perturbation at the probes changes from the Newtonian-gauge value.
A departure of the contrast from linear theory would mean that the proper time of the
probe or the density is no longer that of the comoving observer (for example if the
driver made the lapse oscillate).
Written before the extreme case `cosmo/east_d0.05_n64_kd` (mu = 1, no particle
removal): the lapse at the overdensity falls below a tenth of the largest lapse while
the density there is still finite, and the run passes a = 18.6; whether 64 cells hold
the gradients is again open.

## C5, follow-up runs of tests A0 and A: outcome (01:58)

(i) `cosmo/dav_a0k_n{8,16,32}` (damping rate fixed per unit of conformal time, kappa1 =
    1). Error of chi at the end: 3.9e-8, 2.6e-9, 6.2e-10 against 1.3e-7, 8.2e-9, 1.1e-9
    with the constant coefficient: lower by 3.3, 3.2, 1.8, not by more than ten.
    Refuted. Fourth-order convergence holds (15.2 between 8 and 16 cells). Paper 2 is
    still 15 times lower at 8 cells.
    Correction of the previous entry: I wrote that the integral of (2/3) alpha Theta
    "is a few 1e-8, as measured". Redone with the recorded values: the lapse over the
    code's own scale factor, alpha chi^(1/2), is off by -1.7e-8 at the end, which is
    what that integral gives; the larger part of the error of chi (1.3e-7) is the
    difference between the code's homogeneous solution and the exact one in the
    normalization of conformal time, set by the truncation error of the early steps
    and not by Theta. The integrator of this code is a low-storage fourth-order
    Runge-Kutta scheme with about twice the principal error of the classical one
    (stated in its source); that explains a factor of two of the fifteen. The rest is
    not explained.
(ii) `cosmo/dav_anp_n{8,16,32}` (noise of test A without the momentum noise of the
    particles). Error of E at t = 10 Mpc/h: 9.0e-9, 2.3e-9, 5.5e-10 (paper 2: 7.7e-9,
    2.2e-9, 4.4e-10): the early level is the noise of chi in both. At the end: 2.4e-6,
    1.2e-6, 6.4e-7 against 8.9e-7, 1.9e-7, 6.7e-8: within a factor of five at 8 cells
    (2.6), not at 16 and 32 cells (6.3 and 9.5). Partly confirmed. With the momentum
    noise the error was 700 times that of paper 2, without it 3 to 10 times: the runs
    of paper 2 cannot have had momentum noise of the size its text states. The
    remaining factor grows with resolution; the deposit here is the linear cloud
    (paper 2: quadratic), which passes more of the grid-scale noise to the density.

## E1, second step: outcome (01:59)

Linear-regime check `cosmo/east_d1e-4_n32_kd` (mu = 1, to a = 10): the observer density
contrast over linear theory is 0.996 to 0.998 at both probes, equal to the run without
the driver to three digits; the lapse perturbation at the probes is 14 percent smaller
(-1.57e-4 against -1.83e-4 at the overdensity at t = 4.4). Confirmed.
Extreme case `cosmo/east_d0.05_n64_kd` (mu = 1): confirmed as far as predicted. The
lapse at the overdensity turns around at a = 15.6 (10.5), falls smoothly to 1.56 at
t = 7.03 (a = 20.5), 7.5 percent of the largest lapse, and the density there now rises
by half in a quarter time unit where it doubled every 0.06 before. The run passes a =
18.6. It ends at t = 7.05 (a = 20.6): the metric determinant turns non-positive in 48
cells around the overdensity (three cells across), the relative Hamiltonian constraint
there is of order one and Theta is 0.12. The driver does what it should; 64 cells do
not resolve the collapsing region, as feared.
Next: the same on a finer uniform mesh (128 cells) to see whether the end moves, then
static refinement around the overdensity with the adaptive cloud level of the first
project, interpolated initial data, and the horizon finder. A mass estimate: the matter
that starts within a quarter wavelength of the overdensity has M = 0.5 in these units,
a horizon of proper radius 1, i.e. 0.05 in comoving coordinates at a = 20, less than
one cell of the 64-cell mesh; three levels of refinement give it six to twelve cells.

## C3: luminosity distance along light rays, outcome (02:00)

Relativistic bundles from the v2 runs (emission at scale factors 1, 10, 28, ... as in
paper 1 plus a few more); Newtonian bundles emitted at the same proper times of the
emitters and integrated in the dictionary metric (`cosmo/newton_d*_n64_v2`). Analysis
`cosmo/analysis/east_rays.py`, figures `cosmo/analysis/figs/east_rays.png` and
`cosmo/paper/figures/fig_rays.png` (inspected). No prediction was written for these
runs beyond the homogeneous test; the comparison is with the values read from the
figures of paper 1 (`cosmo/notes/east_figures/SUMMARY.md`).
Deviation from the homogeneous relation, D_L/D_FRW - 1, at z = 0.1, 0.5, 1, 2
(relativistic; paper 1 in brackets):
- 0.01, overdensity, a_e = 1: -0.0069, -0.0043, -0.0042, -0.0108 (-0.0077, -0.0051,
  -0.0048, -0.0111); underdensity: +0.0073, +0.0045, +0.0041, +0.0099 (+0.0066,
  +0.0038, +0.0034, +0.0094). Newtonian: -0.0075, -0.0045, -0.0040, -0.0102 (-0.0076,
  -0.0046, -0.0041, -0.0104).
- 0.01, a_e = 28: overdensity +0.654, +0.025 (+0.605, +0.006); underdensity -0.176,
  -0.189 (-0.161, -0.173). a_e = 43: +0.805, -0.053 (+0.754, -0.073) and -0.215, -0.261
  (-0.205, -0.252). a_e = 52: +0.731, -0.102 (+0.676, -0.124) and -0.229, -0.303
  (-0.222, -0.288).
- 0.005, a_e = 1: -0.0035, -0.0022, -0.0021, -0.0053 (-0.0039, -0.0025, -0.0024,
  -0.0055); a_e = 28: +0.220, +0.034 (+0.211, +0.023) and -0.115, -0.089 (-0.103,
  -0.081); a_e = 58: +0.496, -0.040 (+0.478, -0.052) and -0.174 (-0.167).
- 0.0025, a_e = 1: -0.0018, -0.0011, -0.0011, -0.0026 (-0.0020, -0.0014, -0.0013,
  -0.0029); a_e = 28: +0.085, +0.023 (+0.086, +0.018); a_e = 59: +0.208, -0.021
  (+0.204, -0.025); a_e = 163: +0.320 (+0.309) and -0.205 (-0.200).
The redshift of rays from the underdensity turns back near the overdensity for the
amplitude 0.01 (largest redshift 0.73 to 0.77; paper 1: 0.735 to 0.796) and not for the
lower amplitudes at the emission times of paper 1, as there.
Relativistic against Newtonian at equal redshift: rays emitted at a = 1: at most 6e-4,
1.8e-4, 7e-5 for 0.01, 0.005, 0.0025 (paper 1: below 2e-3); later rays: percent level
where the ray starts or ends in the bound region (0.01: 5 percent at z = 0.03 for the
overdensity ray of a_e = 28, 8 percent at z = 0.73 for the underdensity ray; paper 1:
10 and 7 percent), below 1e-2 elsewhere. At 0.05 the Newtonian rays that reach the
overdensity after a = 12 enter the region where 1 + 2 psi_N is negative and their
redshift is meaningless.
What this establishes: the ray machinery of both calculations reproduces Fig. 4 of
paper 1 to about a tenth of the plotted deviations at lower particle number, and its
conclusion: large deviations from the homogeneous relation, small differences between
the two gravities except in the bound region.

## C4, wavelength test: outcome (02:09)

Runs `cosmo/east_d0.01_n64_tsc_L{2,8}` against their Newtonian runs and the 4-radii pair
of the same cloud. Delay of the relativistic infall (distance of the fiducial observers
below a tenth; four starting distances):
- 2 Hubble radii, (H/k)^2 = 0.101: 1.09, 0.98, 1.08, 1.17 percent;
- 4 Hubble radii, (H/k)^2 = 0.405: 4.6, 4.6, 4.8, 5.3 percent;
- 8 Hubble radii, (H/k)^2 = 1.62: 27.9, 28.2, 29.5 percent (three inner distances).
Predicted for a horizon-scale origin: 1.2 to 1.3 percent at 2 radii (found 1.0 to 1.2)
and about 20 at 8 (found 28 to 30); predicted for a dependence on the amplitude alone:
5 percent at all three. The first is confirmed; the delay rises somewhat faster than
(H/k)^2 at the long end (power 1.17 between 2 and 8 radii). At 8 radii both
calculations end near the collapse, as predicted: the relativistic run at a = 96 with
the lapse collapsing at the overdensity, the Newtonian dictionary at a = 91.
In terms of the depth of the initial potential at the overdensity, |psi_N| =
(9/2) (H/k)^2 times the amplitude: delay / |psi_N| = 2.4 (2 radii), 2.75 (4 radii,
amplitude 0.01), 2.85 (4 radii, 0.05), 3.9 (8 radii). The density probe agrees (contrast
of 10 reached later by 0.6, 3.0, 20 percent).
What this establishes: the delay of C2 belongs to the horizon scale. It is set by the
initial potential, about three times its depth, and vanishes for perturbations well
inside the horizon, where the Newtonian calculation with the dictionary is accurate.
Not established: its split between the second-order part of the initial data and of
the evolution.

## C5, test C of paper 2 (random field), larger box: written before the runs (02:14)

Paper 2, run C704: box 704 Mpc/h, power only above 220 Mpc/h, 32, 64, 128 cells, 27
particles per cell, step 0.05 of the cell, z = 1000 to 0, a spectrum from CLASS that it
does not specify. Here: Eisenstein-Hu spectrum with Planck 2018 parameters at z = 0
scaled to z = 1000 with D = a, sharp spherical cut at 2 pi / 220 h/Mpc, one seed with
the same large-scale modes at all resolutions (`cosmo/ic/spectrum.py`,
`random_field.py`, written by a helper agent, 22 checks passing; relativistic data from
the field with `cosmo/ic/make_field.py`, which reproduces `make_east.py` on the sine
waves: identical positions, masses to 9e-7). Quadratic cloud, no filter, 8 particles per
cell at 32 and 64 cells, 1 at 128; step 0.25 of the cell. The field has rms 8.3e-5 and
maximum 3.3e-4 at the start, so it stays linear to z = 0 (rms 0.08).
Data at 32 cells: the solved conformal factor differs from the dictionary by 7 percent
of its perturbation: the shortest waves are 10 cells long and the cloud window lowers
their deposited density by that much.
Predictions for `cosmo/dav_c704_n{32,64,128}`:
(1) Stable to z = 0 at all three resolutions.
(2) Mean relative Hamiltonian constraint below 1e-5 throughout at 64 cells, falling
    with resolution (paper 2: 3e-7 to 3.5e-6, 1e-7, 2.4e-8 to 5e-8 at 32, 64, 128 cells
    with a five times smaller step).
(3) Mean relative momentum constraint at z = 100 within a factor of three of paper 2
    (1.8e-2, 4.9e-3, 1.2e-3) and falling by about four per doubling between 32 and 64
    cells; the 128-cell run has fewer particles per cell and may not continue the trend.
(4) Power spectrum of E / mean - 1 at z = 100, 10, 1 against linear theory, P(t, k) =
    [(3 + k^2/H_c^2(t)) / (3 + k^2/H_c^2(0))]^2 P(0, k) with the measured initial
    spectrum: within 3 percent in every shell below half the cut-off at 64 cells, and
    the departure falling with resolution.

## C6 preparation: homogeneous universe with a cosmological constant (02:16)

The third paper works in a universe with dark energy. The code carries the constant as
a source (`<particles> lambda`: E gains Lambda / 8 pi, S_ij loses Lambda gamma_ij / 8 pi),
untested so far. Run `cosmo/flrw_lambda_n32_cpu`: matter fraction 0.3 and Lambda = 2.1 (in
units of the initial Hubble rate squared) at the start, lattice at rest, 32 cells, to
t = 0.75 (a = 5.5, deep in the accelerating phase).
Written before the run: the lapse condition gives conformal time for any homogeneous
universe, so alpha = a(t) with da/dt = a^2 sqrt(0.3 a^-3 + 0.7); lapse, matter density
(0.3 rho_c a^-3 at the probe) and mean K = -3 H(a) agree with the numerically integrated
solution to 1e-5, and the Hamiltonian constraint stays at the level of the matter-only
run (relative 1e-6). An error of order one in K or in the lapse would mean a wrong sign
or factor in the Lambda source.

Result (`cosmo/flrw_lambda_n32_cpu`, 02:17): confirmed. Lapse within 1.8e-6 of a(t), mean K
within 1.4e-6 of -3 H(a), energy density at the probe within 4e-7 of matter plus
Lambda / 8 pi, largest relative Hamiltonian constraint 1.7e-6, up to the end of the run.
(The end is at a = 3.05; the "a = 5.5" I wrote was a wrong estimate of the conformal
time, which does not affect the test.) The Lambda source is right.

## E1, third step: static refinement around the overdensity (02:26)

Code: the cosmology problem generator interpolates the initial data of the root mesh
onto refined blocks (cubic); input `problems/cosmo/east_bh.athinput` (three levels
around the overdensity, finest cell 0.0078, 1/512 of the wavelength,
lapse driver, cloud level chosen by the local particle density). Two-step check on CPU
at amplitude 1e-4: 176 blocks, particle sums conserved across levels, initial relative
Hamiltonian constraint 4e-5 at most on the refined blocks (2e-11 on the uniform mesh):
the root-level clouds are spread as constants over the fine cells while the metric is
interpolated smoothly.
Run `cosmo/east_d0.05_n64_bh1` (amplitude 0.05, data of the v2 run, 232 blocks, 4,393
steps planned; no prediction was written beyond "see whether the end moves"). Outcome:
it ends earlier, at t = 6.38 (a = 17.6; uniform mesh with the driver: 7.05). From t =
6.06 the smallest lapse falls from 9.7 to 1.9 (a tenth of the largest) in 0.3 time
units while the largest density rises twenty-fold; then the metric determinant turns
non-positive in 32 cells of the finest level at the overdensity.
Reading: on the fine mesh the collapse is followed to smaller scales and is faster; the
lapse driver acts in time; what fails is the spatial metric itself. With zero shift the
coordinate lines are dragged into the collapsing region and the conformal metric
stretches without bound, the known reason for a shift driver around black holes. This
is a hypothesis; its test is the next run.
Written before `cosmo/east_d0.05_n64_bh2` (as bh1, plus a shift driver d_t beta^i = 0.75
alpha^2 Gamma^i - 2 beta^i with advection, which leaves the homogeneous universe at zero
shift; lapse advected with the shift; clouds no finer than the second level; particles
removed where the lapse is below 0.3): if the stretching is the cause, the run passes
t = 6.4 and the smallest lapse falls below 1; a shift of order 0.1 to 1 develops only
within a few cells of the overdensity. If it ends at the same time with the same
symptom, the cause is elsewhere (the under-resolved caustic or the deposit).

## C4, resolution test: 64 against 96 cells (02:27)

`cosmo/east_d0.01_n96_tsc` and `cosmo/newton_d0.01_n96_tsc` against the 64-cell pair
(amplitude 0.01, quadratic cloud, one particle per cell).
- Delay of the relativistic infall at the four starting distances: 4.61, 4.55, 4.79,
  5.25 percent at 64 cells; 4.44, 4.51, 4.74, 5.27 percent at 96 cells. Largest change
  0.17 percentage points (predicted below 0.3): confirmed.
- The infall itself is earlier at 96 cells by 1.2 percent (relativistic, inner
  observers: a_p = 58.88 to 58.18) and 1.0 percent (Newtonian: 56.29 to 55.70), 0.5
  percent for the outer ones: confirmed (earlier, by up to a few percent).
- Density contrast of 10 at the overdensity: delay 3.04 and 3.01 percent.
The 128-cell pair is running (the Newtonian run takes about three hours on one core).

## C5, test C, larger box, 32 cells: outcome and a stiffness problem (02:28)

`cosmo/dav_c704_n32` (1,056 steps, 45 s). (1) It reaches z = 0 with finite fields, but
not cleanly: the mean relative Hamiltonian constraint is 5e-6 at z = 90, 4e-5 to 9e-5
from z = 30 to 1.6, and then grows by a factor of seven per 4.6 time units: 2e-4 at
z = 0.7, 1.8e-3 at 0.42, 1.2e-2 at 0.2, 0.39 at 0.03. Theta grows with it and the
relative momentum constraint jumps to 0.3. Prediction (2) fails at this resolution and
the late growth is an instability, not a truncation error.
Hypothesis: the constraint damping. Its rate per unit of coordinate time is 2 kappa1
alpha, and the lapse reaches 1000; with kappa1 = 0.02 and the step of this run (0.058,
larger than in any earlier run because the box is 7.4 Hubble radii) the product of rate
and step is 1.4 where the growth starts and 2.3 at the end, near the stability limit
of the integrator for a decaying mode (2.8). In the earlier runs it stayed below 0.5.
Written before `cosmo/dav_c704_n32_k` (same data; damping at a fixed rate per unit of
conformal time, `damp_kappa1_over_alpha = true`, kappa1 = 0.5): no late growth; the mean
relative Hamiltonian constraint stays below 2e-4 to z = 0. If the growth is still there
the damping is not the cause.
(4) Power spectrum against linear theory: departures of 11 to 14 percent below half the
cut-off at z = 100 to 0 and 16 to 33 percent up to the cut-off. Refuted as written for
64 cells only if it persists there; at 32 cells the shortest waves are 10 cells long and
test B showed a departure of 2 percent in amplitude at 32 cells per wave, which scales
to 20 percent here. Wait for 64 and 128 cells.

## E1, third step: outcome of the shift-driver run (02:42)

`cosmo/east_d0.05_n64_bh2`: refuted, and worse than without the shift. The run ends at
t = 1.97 (a = 3.9), long before the collapse: the largest relative Hamiltonian constraint
at the refined overdensity grows from 4e-2 at t = 1.25 to 0.86 at t = 1.94, then the
metric determinant turns non-positive in 2,908 cells centred on the overdensity and the
particles are lost. Without the shift (bh1) the same mesh ran to t = 6.4. So the shift
driver as set (0.75 alpha^2 Gamma^i - 2 beta^i with advection) is itself unstable on the
refined blocks, where the conformal connection carries the error of the interpolated
initial data and of the clouds spread over fine cells. The stretching hypothesis for
bh1 is neither confirmed nor refuted by this run.
State of E1: (i) a lapse driver towards constant mean curvature that passes the
homogeneous and linear checks and collapses the lapse at the overdensity; (ii) initial
data on refined meshes by interpolation; (iii) no stable run through the collapse yet.
Open, in order: a shift condition that is stable on refined blocks (smaller coefficient,
damping, or the shift of the first project switched on only near the collapse);
initial data that satisfy the constraints on the refined blocks; more particles in the
collapsing region. Paused here in favour of the remaining reproduction items.

## C5, test C: the late growth is the stiff damping (02:45)

`cosmo/dav_c704_n32_k` (damping at a fixed rate per unit of conformal time, kappa1 =
0.5): confirmed. No late growth: the mean relative Hamiltonian constraint is 6e-6 at
z = 100, 4e-5 at z = 10, 8e-5 at z = 1 and 9.6e-5 at z = 0.02 (predicted below 2e-4); the
mean relative momentum constraint stays between 1.4e-3 and 5.7e-3 (0.3 at the end
before). The power spectrum is unchanged (departures 5.7 to 9.4 percent below half the
cut-off at 32 cells, as before). The 64-cell run with the constant coefficient shows
the same growth more weakly (4e-4 and 0.13 at z = 0.02, where the product of rate and
step is 1.2), so the growth sets in well below the stability limit of a pure decay
term; I have not worked out the mode. From here on the runs over a thousandfold
expansion use the fixed-rate damping (input `problems/cosmo/daverio_field.athinput`).
The earlier runs are not affected: their product of rate and step stayed below 0.5
(tests A0, A, B: at most 0.42; the collapse runs: 0.35), and their constraints fall or
stay level to the end.
Against paper 2 at 32 cells: mean relative momentum constraint 5.7e-3, 1.8e-3, 1.5e-3
at z = 100, 10, 1 (paper 2: 1.8e-2, 1.3e-2, 9.1e-3); mean relative Hamiltonian
constraint 6e-6 to 1e-4 (paper 2: 3e-7 to 3.5e-6, with a five times smaller step).

## Restart of periodic runs (02:51)

Needed for runs longer than the one-hour job limit. Test on CPU (`cosmo/restart_test`,
amplitude 1e-4, 32 cells): one run of 16 steps with restart dumps, one run restarted from
the dump at step 8, compared at step 16.
First result: the sums over particles and over the mesh agreed to 1e-12, but the lapse
and the density at the probes differed by 2e-8 and 5e-8 and the proper time of the
probes by 2e-6. Two pieces of state were not in the dump: the lapse of the previous step
at each probe (the proper time is integrated at third order with it) and the source
densities handed to the spacetime solver for the coming step, which are extrapolated
from the last two deposits and cannot be rebuilt from the particles at one time.
With both written (particle restart format 04; 02 and 03 are still read): every
compared quantity (probe lapse, density and proper time at both probes, particle and
mesh sums, proper volume, mean K, constraint statistics) is identical to the last
digit. Field dumps written before a restart are not repeated after it.

## C5, test C: what sets the constraint level, written before the runs (02:57)

`cosmo/dav_c704_n64_k` (64 cells, fixed-rate damping) ran cleanly to z = 0: mean
relative Hamiltonian constraint 1.4e-6, 9.0e-6, 1.8e-5, 2.1e-5 at z = 100, 10, 1, 0.02
(32 cells: 6.2e-6, 4.2e-5, 8.3e-5, 9.6e-5: ratio 4.6, second order), mean relative
momentum constraint 3.0e-3, 1.1e-3, 1.4e-3, 5.6e-3. Prediction (2) of the entry before
the runs (below 1e-5 throughout at 64 cells) fails by a factor of two; paper 2 reports
1e-7 at this resolution. The momentum constraint is at or below paper 2's.
Two candidate causes, with different signatures:
(a) Smoothing mismatch. The deposited momentum density changes by the force
    interpolated to the particles and then smoothed by the cloud, while the field
    equations expect the unsmoothed force times the deposited density. To first order
    in the perturbation the momentum balance on the mesh is then violated by the
    fraction 1 - W(k) of the force: (k h)^2/12, /8, /6 for the linear, quadratic and
    cubic cloud.
    This drives the momentum constraint at relative size (k h)^2/8 (1e-3 to 1e-2 here,
    as measured) and through it the Hamiltonian constraint at about M_r times the
    density contrast (2.6e-6, 8e-6 at z = 100, 10; measured 1.4e-6, 9e-6).
    Signature: second order in the cell size, independent of the step, mildly LARGER
    for the smoother cloud (ratios 2 : 3 : 4).
(b) Sampling error of the lattice (T1a): c/2, 0.4 c^2, 0.4 c^3 for compression c.
    Signature: independent of the cell size at fixed particles per cell, strongly
    SMALLER for the smoother cloud.
(c) The step: second order in the step, so a five times smaller step would lower the
    constraints 25 times.
Runs at 32 cells (45 s to 4 min each), all with the fixed-rate damping:
`dav_c704_n32_cfl` (step 0.05 of the cell), `dav_c704_n32_cic`, `dav_c704_n32_pcs`
(linear and cubic cloud, initial data rebuilt with the same cloud),
`dav_c704_n32_k2` (damping rate 2 instead of 0.5).
Predictions, from (a):
(1) Step: both mean relative constraints at z = 100, 10, 1 change by less than 30
    percent.
(2) Cloud: the momentum constraint at z = 100 in the ratios 0.67 : 1 : 1.33 (linear :
    quadratic : cubic) within 25 percent. For the linear cloud the lattice error
    (first order in c) may add to the Hamiltonian constraint; for the quadratic and
    cubic clouds the Hamiltonian constraint follows the momentum constraint.
(3) Damping: four times the rate lowers the Hamiltonian constraint at z = 1 by a factor
    between 1.5 and 4 and leaves the power spectrum unchanged within 1 percentage
    point. (Paper 2 damps at a constant coefficient times the lapse, which grows a
    thousandfold, with a five times smaller step; this may be how it reaches 1e-7.)
If (1) fails by a large factor the cause is the step and (a) is wrong.

## C5, test C, smaller box: written before the runs (03:03)

Paper 2, run C256: box 256 Mpc/h, power only above 40 Mpc/h, 64, 128, 256 cells. This
is the box of its power-spectrum figure (departure from linear theory about 1e-2 at
worst at the best resolution, z = 100, 10, 1) and the one that becomes nonlinear: it
reports jumps of the constraints at z of about 10 and 1 after which they no longer
converge, with the means of the relative constraints staying below about 1e-6 and 1e-2.
Here: same spectrum, seed and cut as before; 64 cells with 8 particles per cell and 128
cells with 1 per cell (the same 2,097,152 particles on both meshes, so the pair tests
the mesh alone); quadratic cloud, fixed-rate damping 0.5, step 0.25 of the cell. The
128-cell run takes 11,600 steps (about an hour) and runs as a chain with restarts.
256 cells would take most of a day and is left out.
Data at 64 cells: rms of the contrast 5.5e-4, maximum 2.1e-3, so linear theory gives
rms 0.55 and maximum 2.1 at z = 0: the highest peaks collapse between z = 1 and 0.
Largest displacement 0.004 cells, potential at most 7e-5.
Predictions for `cosmo/dav_c256_n{64,128}`:
(1) Both reach z = 0 with finite fields.
(2) At z = 100 and 10 the power below half the cut-off is within 10 percent of linear
    theory at 64 cells and within 2.5 percent at 128 cells (the same cells per cut-off
    wave as the larger box at 32 and 64 cells). At z = 1 (linear rms 0.28) the
    departure in the upper half of the band is more than twice that at z = 10 at 128
    cells: nonlinear growth, not error.
(3) While linear, the mean relative Hamiltonian constraint is the larger-box value at
    the same cells per wave times the ratio of the amplitudes (6.7), if the smoothing
    mismatch of the previous entry is its cause: 4e-5 and 3e-4 at z = 100 and 10 at 64
    cells, 9e-6 and 6e-5 at 128 cells. The mean relative momentum constraint is as in
    the larger box (2e-3 to 6e-3 and 1e-3 to 3e-3).
(4) After the first collapse (z below 1) the constraint means rise by more than ten
    and the ratio between the resolutions falls below two, as in paper 2.

## T1: compensating the cloud in the deposit, written before the run (03:04)

If the smoothing mismatch (a) of the entry above sets the constraint level, it can be
removed at its leading order: one pass with the weights (-c, 1 + 2c, -c) per direction
on the deposited sources, with c chosen to cancel the second moment of the cloud
(c = 1/12, 1/8, 1/6 for the linear, quadratic and cubic cloud; the pass exists in the
code as the compensation of the binomial filter and can run alone). The deposited
density of a long wave is then the density of the particles to fourth order in the
cell size, and the force on a particle times the deposited density is the force
density the field equations expect. For a wave of 10 cells and the quadratic cloud the
mismatch falls from 4.8 percent to 0.3 percent, for 20 cells from 1.2 percent to 0.02
percent.
The same smoothing weakens the self-gravity of a wave: with the source of the growth
equation reduced by the fraction e, the growth exponent is 1 - 0.6 e, and over a
thousandfold expansion the power falls short by 8.3 e: 10 percent for a wave of 20
cells. That is the size of the departure measured at 32 cells below half the cut-off
(9.4 percent at z = 0), so the two findings may have one cause.
Run `cosmo/dav_c704_n32_comp`: quadratic cloud, c = 1/8 in the initial data and in the
evolution, otherwise as `dav_c704_n32_k`.
Predictions, from (a):
(1) Mean relative momentum constraint at z = 100 below 1.2e-3 (5.7e-3 without).
(2) Mean relative Hamiltonian constraint at z = 10 and 1 below 1e-5 and 2e-5 (4.2e-5,
    8.3e-5 without).
(3) Power below half the cut-off within 2 percent of linear theory at z = 100, 10, 1
    (5.7 to 9.1 percent without).
If the sampling error of the lattice (b) is the cause, the pass amplifies it (by up to
1.5 at the shortest wave) and the constraints rise.

## T1: the compensation must act on the density, not on the source (03:23)

Found in the initial data while the run above was queued. With the pass after the
division by sqrt(gamma) (the existing filter compensation) the solved conformal factor
still differs from the linear dictionary by 3.0 percent in every mode (5.4 percent
without the pass at the longest wave), although the deposited density of the particles
matches its target to 5e-5. Cause: the particles carry the density per coordinate
volume, rho sqrt(gamma), whose contrast at long waves is mostly the contrast of
sqrt(gamma) itself (delta_N - 2 psi_N - 3 psi_N; for the longest wave of this box the
last term is six times the first). The cloud smooths that product; the division by the
local sqrt(gamma) then leaves the smoothed-minus-unsmoothed part of sqrt(gamma) in the
source, and a pass applied after the division cannot remove it. Measured: contrast of E
against the dictionary -0.58, -0.97, -1.26 percent for the three longest waves, equal
to -(k h)^2/8 times 3 psi_N / (delta_N - 2 psi_N) as this predicts (-0.584 percent for
the first).
Fix: new option `deposit_comp_c` (code) and `DEP_COMP_C` (initial data): the pass
acts on the deposited densities before the division. Initial data at 32 cells with it:
conformal factor against the dictionary -0.05 percent (quadratic cloud), -0.03 percent
(cubic), -0.4 percent (linear; its lattice error is of first order); largest
difference 1.7e-7 against 5.1e-6 without (29 times smaller); Ahat 9e-8 against 2.9e-6.
The sensitivity is a relativistic one: it scales with (H/k)^2 and is largest for waves
longer than the Hubble radius.
Run `cosmo/dav_c704_n32_dcomp` (quadratic cloud, deposit_comp_c = 1/8 in data and
evolution). Predictions: as (1) to (3) of the entry above (momentum constraint at z =
100 below 1.2e-3, Hamiltonian constraint at z = 10 and 1 below 1e-5 and 2e-5, power
below half the cut-off within 2 percent), and better than `dav_c704_n32_comp` in the
Hamiltonian constraint at z = 100, where (H/k)^2 is still 0.14 for the longest wave.

## C5, test C: the Hamiltonian-constraint level was a rounded box size (03:28)

Outcome of the four runs at 32 cells (`dav_c704_n32_{cfl,cic,pcs,k2}`) and of the
128-cell run, and what they uncovered.
Mean relative Hamiltonian constraint at z = 100, 10, 1: identical to three digits for
the three clouds (6.18e-6, 4.24e-5, 8.25e-5); 4.8 to 6.2 times lower with the five times
smaller step (1.28e-6, 6.9e-6, 1.34e-5); and nearly the same at 64 and 128 cells
(1.35e-6, 9.0e-6, 1.75e-5 and 1.13e-6, 7.0e-6, 1.42e-5). Its maximum is close to its
mean. So prediction (1) fails for the Hamiltonian constraint and cause (a) is not what
sets it: it is a uniform offset, the sum of a term of fourth order in the step (the
background error of the integrator, 3.6e-5 at z = 10 for the largest step) and a floor
that depends on nothing I varied (1.2e-6, 6.9e-6, 1.4e-5, 2.0e-5 at z = 100, 10, 1, 0).
The floor is there at t = 0: mean |H| = 2.29e-6 at all three resolutions, although the
residual of the initial-data solver is 1e-12. Comparing the first field dump with the
solver's fields: the code's energy density is higher by a uniform 3.8e-7. Cause: the
input file had the box size rounded to six digits (7.42966) and the initial data use
7.429660943..., so the mesh volume was 3.8e-7 too small. A uniform excess of density
acts like spatial curvature: its share of the Hamiltonian constraint grows with the
expansion. This is an error of the set-up of test C in the larger box only (tests A
and B used the same rounded number on both sides; the smaller box was passed in full).
The momentum constraint is not affected by it: step 5.7e-3 to 5.1e-3 at z = 100
(prediction (1) holds for it); cloud 3.1e-3, 5.7e-3, 5.2e-3 for linear, quadratic,
cubic at z = 100 (prediction (2), ratios 0.67 : 1 : 1.33, fails for the cubic cloud),
and at z = 10 and 1 the cubic cloud is the lowest (1.0e-3, 7.8e-4) and the linear the
highest (4.1e-3, 1.7e-2). So (a) does not describe the momentum constraint either
beyond its order of magnitude; the linear cloud's growth points to the lattice error.
Power below half the cut-off at z = 10: 5.3, 7.9, 10.2 percent short for linear,
quadratic, cubic (ratios 0.67 : 1 : 1.29: this part of (a) holds, the smoothing of
self-gravity), unchanged by the step (7.6 percent) and 1.1 points lower with four
times the damping (6.8 percent; prediction (3) allowed 1 point).
Compensation (`dav_c704_n32_comp` after the division, `dav_c704_n32_dcomp` on the
density), against the predictions of the two T1 entries:
(1) Momentum constraint at z = 100: 3.6e-3 and 3.7e-3 (5.7e-3 without; predicted below
    1.2e-3: fails), and at z = 10, 1, 0 it is HIGHER than without (2.6e-3, 3.4e-3,
    8.1e-3 against 1.8e-3, 1.5e-3, 2.5e-3). With the ordering of the clouds above this
    says the momentum constraint is set by the sampling error of the lattice, which
    the pass amplifies, and not by the smoothing mismatch.
(2) Hamiltonian constraint: cannot be judged, it is the offset of the box size.
(3) Power below half the cut-off against linear theory at z = 100, 10, 1, 0:
    5.7, 7.9, 9.1, 9.4 percent without; 2.0, 1.8, 1.3, 0.9 percent with the pass after
    the division; 0.05, 0.05, 0.5, 1.0 percent with the pass on the density. Up to the
    cut-off (waves of 10 cells): 11 to 30 percent without, 0.5 to 1.6 percent with the
    pass on the density. Predicted within 2 percent: holds, by a factor of forty at
    z = 100 and 10. The growth of a wave ten cells long is now right to half a percent
    over a thousandfold expansion, at 32 cells.
All runs of the larger box are repeated with the exact box size before any of this
goes into the working paper. Old runs kept in `runs/cosmo/_rounded_box`.

## C5, test C: repeat with the exact box size, written before the runs (03:31)

The smaller box at 64 cells (`dav_c256_n64`, box passed in full) already shows the
level without the offset: mean relative Hamiltonian constraint 9.5e-8 at z = 100 and
1.2e-6 at z = 10 (my prediction (3) for it, 4e-5 and 3e-4, came from the wrong model
and is off by a factor of several hundred, in the good direction); these are the
values paper 2 reports (about 1e-7 to 1e-6). Its other numbers are in the outcome
entry below, once the 128-cell run exists.
Repeated runs, larger box: `dav_c704_n32_{k,cfl,cic,pcs,k2,dcomp}`,
`dav_c704_n64_{k,dcomp}`, `dav_c704_n128_k`; new: `dav_c256_n64_dcomp`.
Predictions:
(1) Mean relative Hamiltonian constraint at t = 0 below 1e-8 at every resolution.
(2) At 32 cells with the large step (0.058) it is set by the fourth-order error of the
    integrator on the background, about 2e-6 late (test A0: 3e-8 at a step of 0.021);
    with the small step and at 64 and 128 cells it stays below 5e-7 to z = 10.
(3) Momentum constraint and power as in the rounded-box runs, within a tenth.
(4) With the compensation on the density at 64 cells: power within 0.5 percent of
    linear theory up to the cut-off at z = 100 and 10.
(5) Smaller box at 64 cells with the compensation: reaches z = 0 (the pass has negative
    lobes; if the density turns negative in the voids after collapse the run may fail);
    power below half the cut-off within 1 percent at z = 100 and 10 (2.6 and 5.7
    percent without).

## Step limited by the expansion rate (03:43)

First repeated runs with the exact box (`dav_c704_n32_{k,dcomp,cic,pcs}`): the mean
relative Hamiltonian constraint at t = 0 is 1.2e-9 (prediction (1) holds), but through
the run it is nearly what it was (5.2e-6, 3.6e-5, 6.9e-5, 8.1e-5 at z = 100, 10, 1, 0),
uniform and identical for all clouds: prediction (2), about 2e-6, fails by forty. My
estimate used the wrong step for test A0 (its input has a step of 0.1 of the cell, so
0.0084, not 0.021). Scaled correctly, (0.058/0.0084)^4 times 3e-8 is 7e-5: the offset
IS the fourth-order error of the integrator on the background, committed in the first
steps, where the Courant step of this mesh is 6 percent of the expansion time (the box
is 7.4 Hubble radii wide), and carried from then on like spatial curvature.
New option `dt_expansion = f`: the step is at most f times the expansion time
3/|mean(alpha Khat)|. With it the step varies, so the extrapolation of the source
densities and the third-order proper time of the probes now use the ratio of
successive steps, and the restart file (format 05) carries the previous step.
Checks on CPU. Homogeneous universe, 16 cells, box 4, to a = 36: without the limit
(step 0.0625, 160 steps) the relative Hamiltonian constraint is 2.5e-5 and the error
of chi a^2 is 5e-5 at the end; with f = 0.01 (360 steps) 6.0e-8 and 1.0e-7.
Restart with the limit active and the compensation on (`cosmo/restart_test/a2, b2`):
all compared quantities identical to the last digit.
Predictions for the larger box at 32 cells with f = 0.01 (`dav_c704_n32_{t,dcompt}`):
mean relative Hamiltonian constraint below 3e-7 at z = 100 and below 3e-6 to z = 0
(the smaller box at 64 cells, whose step is 1 percent of the expansion time from the
start, has 9.5e-8 at z = 100); momentum constraint and power unchanged.

## C6: initial conditions of paper 3 (GRAMSES), outcome (03:45)

Done by a helper agent from the specification `cosmo/notes/spec_2001.07968.md`; its
expectations were written before its runs and are in `cosmo/notes/c6_report.md` with
the full tables. I reran the closed-form checks (20 of 20 pass) and looked at the six
figures (`cosmo/analysis/figs/gramses_*`). All tests of paper 3 are on initial data,
nothing is evolved. No radiation here (Eisenstein-Hu spectrum, growth of matter plus a
cosmological constant), 256^3 particles instead of 1024^3, boxes 4 Gpc/h and 256 Mpc/h,
z = 99 and 49.
Reproduced:
- finite-difference against two-step velocity: excess power 2.0003e-4, 5.0002e-5,
  1.2500e-5 at z = 99 and 8.0044e-4, 2.0002e-4, 4.9999e-5 at z = 49 for offsets 1, 0.5,
  0.25 (paper 3: 2.0e-4, 5.0e-5, 1.1e-5 and 8.0e-4, 2.0e-4, 5.1e-5), equal to
  2 dz^2/(1+z)^2 in every bin to 4e-13, same in both gauges;
- growth rate of the particle-number contrast reaches one half at k = 3.58e-3 and
  5.06e-3 h/Mpc (paper 3: 3.6e-3, 5.1e-3); its power at k = 1e-4 within 0.8 percent;
- power of the particle-number contrast over the synchronous one: equal to the linear
  ratio on the realized modes to 1.2e-4 in every bin; first bin of the large box 52.9
  and 16.9 against paper 3's 46.7 and 13.7, both inside the spread over realizations
  (38 to 57, 13 to 18); small box 1.0553, 1.0275 against 1.049, 1.024;
- lower-index velocity divergence over the Newtonian one follows k^2/(k^2 + m^2) mode
  by mode.
Different, with cause: paper 3's growth rates carry radiation (its synchronous rate is
0.9805 and 0.9903 on small scales; a Meszaros estimate gives 0.9807 and 0.9903); its
horizon-scale curves are 3 to 8 percent off the radiation-free closed forms. Not
reproducible without a Boltzmann code: the curves of its last figure that depend on the
radiation-era growth (modelled only).
Three of the agent's expectations failed, each with a cause found: two numbers in the
specification were figure readings that include radiation; the scatter at the smallest
offset is rounding of tabulated spectra to seven digits (1.3e-4, paper 3: 2 to 5e-4),
not single precision of the displacements (1.6e-7); the deposited velocity spectrum in
the small box at z = 49 exceeds linear theory above 0.5 h/Mpc at second order in the
amplitude.
For this code: the lapse condition keeps the Newtonian slicing while the potential is
constant (growing mode, matter domination); with zero shift the threading is the one
in which paper 3 defines the particle-number contrast, delta_S - 5 phi in matter
domination, which is the coordinate density of our initial data (displacement of
delta_S, the rest in the masses). With a cosmological constant the slicing drifts by
(1 - f) phi, of order phi by z = 0. So our data are the hyperbolic counterpart of
paper 3's without change; an evolved comparison would need its code.

## C5, test C: exact box and compensation, first outcomes (03:53)

Larger box, exact box size, Courant step (`dav_c704_n{32,64}_{k,dcomp}`, `n32_cfl`).
Hamiltonian constraint (mean, relative) at z = 100, 10, 1: 5.2e-6, 3.6e-5, 6.9e-5 at 32
cells and 3.4e-7, 2.2e-6, 4.3e-6 at 64 cells: ratio 15 to 16, the fourth order of the
integrator in the step; with the step of 0.05 of a cell at 32 cells 7.2e-7, 7.1e-7,
1.5e-6. Momentum constraint at z = 100 and 10: 4.6e-3, 1.6e-3 at 32 cells and 1.1e-3,
5.2e-4 at 64 (ratio 4.0, 3.0); with the compensation 2.3e-3, 1.9e-3 and 5.7e-4, 5.3e-4:
half at z = 100, equal or higher later. Paper 2: 1.8e-2, 1.3e-2 and 4.9e-3, 4.1e-3.
Power with the compensation at 64 cells: checked with the step-limited runs below.
Smaller box at 64 cells (`dav_c256_n64`, `dav_c256_n64_dcomp`), against the
predictions of the two entries:
(1) both reach z = 0 with finite fields; the compensated one too (prediction (5)).
(2) power below half the cut-off at z = 100, 10: 2.6, 5.7 percent without (predicted
    within 10); up to the cut-off 9 and 18 percent. With the compensation 0.09 and 0.5
    percent up to the cut-off (predicted within 1 below half the cut-off: holds).
    Paper 2 at 64 cells: 0.9 to 13 percent at z = 100, 1.5 to 31 percent at z = 10.
    At z = 1 (rms contrast 0.26 and 0.30): 9 and 2 percent below half the cut-off.
(3) Hamiltonian constraint while linear: 9.5e-8 at z = 100 and 1.2e-6 at z = 10
    (2.3e-8 and 1.7e-6 with the compensation); paper 2: 2.5e-7, 2.0e-7. It rises from
    z of about 30 on, before any collapse. Momentum constraint 1.1e-3, 1.3e-3 (paper 2:
    7.6e-3, 7.2e-3).
(4) After the first collapse: Hamiltonian constraint 1.3e-4 at z = 1 and 6.9e-4 at
    z = 0, momentum constraint 5e-2 and 0.13 (paper 2: 9.6e-7, 5.3e-6 and 1.6e-2,
    6.7e-2). With the compensation they are three times higher still (2.7e-4, 2.0e-3
    and 0.20, 0.47): the pass amplifies the noise of the collapsed regions. The rms
    contrast at z = 0 is 0.86 with it against 0.63 without.
So before collapse this code is at or below paper 2's constraint levels and far closer
to linear theory with the compensation; after collapse its Hamiltonian constraint is a
hundred times higher. Two candidate causes, one run each (64 cells, no compensation,
step limit on):
`dav_c256_n64_p3t`: 27 particles per cell as in paper 2 instead of 8. Prediction:
    constraints after collapse lower by about sqrt(27/8) = 1.8 (noise), the rise from
    z = 30 to 10 lower by more than 2 (lattice error); not the factor of a hundred.
`dav_c256_n64_kct`: damping with a constant coefficient 0.02 as paper 2 uses (rate
    grows with the lapse to 40 per unit of conformal time at the end; rate times step
    0.42, below the stiffness found before). Prediction: Hamiltonian constraint at
    z = 1 and 0 lower by more than ten, momentum constraint and power unchanged
    within a tenth. If so, the late level is a matter of how hard the constraint is
    damped, not of how well the dynamics is solved, as paper 2 itself cautions.

Added before the 128-cell chains of the smaller box (`dav_c256_n128_{t,dcompt}`, step
limit on): with the compensation the power up to the cut-off is within 0.5 percent of
linear theory at z = 100 and 10; the prediction for the run without it stands (2.5
percent below half the cut-off).

## C5, test C: step-limited runs of the larger box, and the cubic cloud with compensation (04:13)

`dav_c704_n{32,64}_{t,dcompt}` (step limit 0.01; 1,243 steps instead of 1,056 at 32
cells). Mean relative Hamiltonian constraint at z = 100, 10, 1, 0.02:
  32 cells: 7.1e-7, 6.6e-7, 1.5e-6, 4.9e-6; with compensation 5.0e-8, 1.3e-7, 2.0e-6, 9.5e-6
  64 cells: 1.8e-7, 1.9e-7, 4.2e-7, 5.3e-6; with compensation 2.1e-8, 8.5e-8, 6.4e-7, 1.0e-5
  paper 2:  3.1e-7, 5.1e-7, 2.6e-6, 3.5e-6 (32); 9.1e-8, 8.9e-8, 9.8e-8, 1.2e-7 (64).
My prediction (below 3e-7 at z = 100, below 3e-6 to z = 0, at 32 cells) fails without
the compensation (7.1e-7; 4.9e-6 at the end) and holds with it up to z = 1. The offset
of the background is gone (55 times lower at z = 10); what remains depends on the cloud
after all: the compensation lowers it 14 and 9 times at z = 100, so cause (a) does act
on the Hamiltonian constraint once the offset no longer hides it.
From z of about 3 on the constraints rise at both resolutions to the same level
(5e-6 to 1e-5), local (largest value 30 times the mean), higher with the compensation:
the sampling of the distorted lattice (rms displacement a quarter to a half of the
particle spacing at the end). Momentum constraint: 3.8e-3, 1.6e-3, 1.4e-3, 2.4e-3 and
1.2e-3, 5.2e-4, 1.0e-3, 5.4e-3 without; 1.7e-3, 2.0e-3, 2.3e-3, 7.1e-3 and 6.0e-4,
5.3e-4, 1.3e-3, 9.6e-3 with (paper 2: 1.8e-2 to 7.8e-3 at 32, 4.9e-3 to 4.3e-3 at 64).
Power against linear theory, up to the cut-off, z = 100, 10, 1, 0: without 11, 21, 27,
29 percent (32 cells) and 2.8, 5.5, 7.4, 8.2 percent (64); with 0.26, 0.37, 0.98, 1.8
percent (32) and 0.05, 0.24, 0.99, 1.8 percent (64). Prediction (4), within 0.5
percent at z = 100 and 10 at 64 cells: holds. The departure of 1 to 2 percent at z = 1
and 0 is the same at both resolutions: growth of second order in the contrast (rms
0.04 and 0.08), not error.
128 cells, exact box, Courant step, one particle per cell, no compensation
(`dav_c704_n128_k`): Hamiltonian constraint 3.9e-8, 1.7e-7, 2.1e-6, 8.8e-6 (paper 2:
2.4e-8, 2.4e-8, 2.8e-8, 5.1e-8), momentum constraint 6.7e-4, 7.3e-4, 4.8e-3, 1.3e-2
(1.2e-3, 1.1e-3, 1.4e-3, 2.2e-3), power within 0.3 percent to z = 10.
Next, written before the runs `dav_c704_n32_pcsct` and `dav_c256_n64_pcsct`: cubic
cloud with its compensation (c = 1/6) and the step limit. The lattice error of the
cubic cloud is of third order in the compression (T1a) and its momentum constraint
was the lowest late in the uncompensated comparison; its smoothing of the growth was
the largest and is what the pass removes. Predictions: power as with the compensated
quadratic cloud (within 0.5 percent up to the cut-off at z = 100 and 10); constraints
from z = 3 on lower than with the compensated quadratic cloud by more than two in the
larger box; in the smaller box lower after the first collapse, by less.

## T1: limited compensation, written before the runs (04:29)

The compensation raises the constraints once matter has collapsed (three times in the
smaller box). Candidate cause: at a density spike one cell wide the pass moves
density from the lower to the higher cell (it is anti-diffusion), sharpens the spike by
up to (1 + 2c)^3 and leaves negative values beside it. New option
`deposit_comp_limit = L`: the pass in flux form, direction by direction, each face
flux c (u_{i+1} - u_i) scaled so that the flux of the energy density is at most L times
the smaller of the two neighbouring energy densities; the same factor for all source
components at the face. In smooth flow the limiter is inactive (with c = 1/8 and
L = 0.1 it acts only where neighbouring cells differ by more than 80 percent) and the
result is the plain pass; the energy density stays positive for L <= 1/6; sums are
conserved.
Checks: the flux form equals the product stencil to 1e-15; on a lattice with position
noise of 0.3 cells (energy density between 0.1 and 2.7 times the mean) the code and the
initial-data solver agree to the precision of the dump (6e-8), across block boundaries;
unlimited, the same data give negative energy density.
Runs (64 cells, smaller box; 32 cells, larger box; step limit on; L = 0.1):
`dav_c256_n64_dclt`, `dav_c704_n32_dclt`. Predictions:
(1) Before collapse (z = 100, 10) power and constraints as with the plain pass, to a
    tenth.
(2) After collapse (z = 1, 0) the constraints of the smaller box lie between those of
    the runs without and with the plain pass. If they stay at the level of the plain
    pass, the amplified noise is of moderate contrast, spread over the multi-stream
    regions, and a limiter on the cell-to-cell contrast is the wrong tool.
(3) Larger box from z = 3 on: no change (the lattice there is distorted but smooth).

## T1: what the rise of the constraints before collapse is (Python experiment, 04:39)

Question: in the smaller box the constraints rise from z of about 30 on, long before
anything collapses (largest linear contrast 0.06 at z = 30, 0.2 at z = 10). Is this the
sampling error of the displaced lattice, and which remedy removes it?
Experiment (`cosmo/analysis/lattice_error.py`, no evolution): the same kind of field
(shortest wave ten cells, 32 cells), Zel'dovich displacements scaled by the growth
factor, deposited from lattices of 1, 2, 3 particles per cell and direction with the
three clouds, and from lattices refined by sub-particles at trilinearly interpolated
displacements (the Lagrangian sheet, 2 to 4 per direction). Reference: 8 per cell and
direction with exact displacements. Error of the density over the mean, rms:

    z     cloud      1/cell    2/cell    3/cell    2/cell + sheet 2
    32    linear     1.0e-4    7.9e-5    7.8e-5    1.1e-4
          quadratic  1.8e-4    2.2e-5    2.6e-5    8.5e-5
          cubic      4.6e-6    9.6e-7    3.9e-7    8.0e-5
    10    linear     1.9e-3    1.9e-3    2.0e-3    2.3e-3
          quadratic  6.6e-4    1.0e-4    1.5e-4    2.6e-4
          cubic      3.8e-5    8.7e-6    5.0e-6    2.4e-4
    4     linear     7.6e-3    8.8e-3    7.0e-3    5.9e-3
          quadratic  2.2e-3    7.1e-4    4.9e-4    6.4e-4
          cubic      1.8e-4    7.3e-5    3.8e-5    5.4e-4
    1     linear     4.9e-2    2.4e-2    1.3e-2    7.7e-3
          quadratic  9.3e-3    3.1e-3    1.2e-3    1.6e-3
          cubic      2.1e-3    4.8e-4    1.3e-4    1.5e-3

(largest errors are 5 to 10 times the rms.) Reading:
- Yes: with the quadratic cloud at 2 per cell the error grows from 2e-5 at z = 32 to
  1e-4 at z = 10 and 3e-3 at z = 1, the range and the timing of the rise in the run.
- More particles per cell do nothing for the linear cloud until z = 2 and little for
  the quadratic one (3 against 2 per cell: none at z = 10, 1.5 at z = 4, 2.6 at z = 1).
- The cubic cloud is 7 to 12 times better than the quadratic at equal particle number
  at every epoch, and gains from particles as well. This is the third-order law of T1a
  acting on a real field.
- The sheet refinement is worse than no refinement for the quadratic and cubic clouds
  until the contrast is of order one: the trilinear interpolation of the displacement
  is itself a second-order error in the particle spacing, larger than what the cloud
  leaves. It helps only the linear cloud late. Not worth building for this regime.
Consequence, sharpening the prediction for `dav_c256_n64_pcsct` (queued): between
z = 30 and z = 2 its Hamiltonian and momentum constraints are lower than those of the
compensated quadratic run by a factor of three or more (the compensation amplifies
short waves by up to (1 + 4c)^3 = 4.6 at the corner of the band for c = 1/6, typically
two, which eats part of the factor of ten). And for `dav_c256_n64_p3t` (27 per cell,
quadratic, no compensation): no gain at z = 10, a factor of 1.5 to 2.6 from z = 4 to 1.

## C5/T1: cubic cloud with compensation, larger box at 32 cells; the late rise (04:43)

`dav_c704_n32_pcsct` against `dav_c704_n32_dcompt` (quadratic, compensated), z = 100,
10, 1, 0.02. Momentum constraint 2.1e-4, 7.8e-4, 1.5e-3, 4.3e-3 against 1.7e-3, 2.0e-3,
2.3e-3, 7.1e-3: lower by 7.8, 2.5, 1.6, 1.7. Hamiltonian constraint 6.4e-8, 1.5e-7,
1.9e-6, 7.6e-6 against 5.0e-8, 1.3e-7, 2.0e-6, 9.5e-6: the same. Power up to the cut-off
0.23, 0.76, 1.7, 2.6 percent against 0.26, 0.37, 0.98, 1.8.
Against my predictions: power within 0.5 percent at z = 10: fails (0.76); constraints
from z = 3 on lower by more than two: fails (1.0 for the Hamiltonian, 1.6 for the
momentum constraint).
What the numbers say instead:
- The early Hamiltonian constraint follows the remainder of the compensation. The pass
  cancels the second moment; the fourth-order remainder of cloud times pass at the
  cut-off wave is 0.30 percent (quadratic) and 0.43 percent (cubic), ratio 1.4; the
  constraints at z = 100 are in the ratio 1.26, and both are 14 times below the
  uncompensated run, whose mismatch there is 4.8 percent (ratio 16). So the smoothing
  mismatch (cause (a) of the earlier entry) does set the Hamiltonian constraint of
  smooth flow, now that the offsets no longer hide it. The same remainder explains the
  slightly larger loss of power with the cubic cloud. A pass that also cancels the
  fourth-order term needs a five-point stencil: 1 - c d2 + (c2/16) d4 with d2, d4 the
  second and fourth differences and c2 = 8/45, 37/120, 7/15 for the three clouds.
- The late rise (from z of about 3, to the same level at 32 and 64 cells, local) is
  the same for both clouds, so it is NOT the lattice sampling error of the density,
  which is ten times smaller for the cubic cloud. Cause not determined.
Runs to find what the late rise depends on (32 cells, cubic cloud, compensated, step
limit; one change each): `_d01` Kreiss-Oliger dissipation 0.1 instead of 0.5; `_k2`
damping rate 2 instead of 0.5; `_p3` 27 particles per cell; `_tol` pusher tolerance
1e-14; `_cfl` step 0.125 of the cell. No prediction: I have no model that survives
the comparison above. Whichever run changes the level at z = 1 and 0 by more than a
factor of two names the direction to look in.

## T1: fourth-order compensation, written before the runs (04:47)

New option `deposit_comp_c2`: the pass per direction becomes u - c d2 u + (c2/16) d4 u
(five points), response 1 + 4c s + c2 s^2 with s = sin^2(k dx/2); c2 = 8/45, 37/120,
7/15 cancels the fourth-order term of the linear, quadratic, cubic cloud. Implemented
in the flux form of the limited pass (the limiter stays optional). Checks: response
equal to the formula to 1e-8 for waves of 16, 11, 6 cells; remainder of cloud times
pass at 10 cells per wave 0.02 percent (quadratic) and 0.03 percent (cubic) against
0.30 and 0.43 with the three-point pass; code and solver agree on the noisy lattice to
the precision of the dump with the fourth-order term and the limiter on.
Runs: `dav_c704_n32_tsc4t`, `dav_c704_n32_pcs4t` (32 cells, larger box, step limit
0.005 so that the background offset, 7e-8 late with 0.01, is 16 times lower).
Predictions:
(1) Mean relative Hamiltonian constraint at z = 100 below 1.5e-8 and at z = 10 below
    5e-8 for both clouds (5.0e-8 and 1.3e-7, 6.4e-8 and 1.5e-7 with the three-point
    pass): the early level follows the remainder.
(2) Power up to the cut-off within 0.15 percent of linear theory at z = 100 and within
    0.3 percent at z = 10.
(3) The late rise is unchanged.
If (1) fails the early level is not the remainder of the pass, and the agreement of
the ratios 1.26 and 14 above was a coincidence.

## T1/C5: outcomes of the limiter, the fourth-order pass, the damping style and the five variants (05:06)

Limiter (`dav_c704_n32_dclt`, `dav_c256_n64_dclt`, L = 0.1): identical to the plain
pass in the larger box (prediction (3) holds) and in the smaller box until z = 0.3;
at the end the Hamiltonian constraint is 1.7e-3 against 2.0e-3 and the momentum
constraint unchanged (0.47). Predictions (1) holds; (2) took its second branch: the
amplified noise is not at sharp spikes. The limiter stays as a safeguard for
positivity, it does not cure the noise.
Fourth-order pass (`dav_c704_n32_{tsc4t,pcs4t}`): Hamiltonian constraint at z = 100
4.3e-8 and 7.2e-8 (three-point pass: 5.0e-8, 6.4e-8). Prediction (1), below 1.5e-8:
FAILS. So the early level is not the remainder of the pass; the matching ratios were
a coincidence, as I said they would be in this case. Power, signed, shortest wave (10
cells), z = 100 and 10: quadratic three-point -0.26, -0.37 percent; quadratic
fourth-order +0.13, +0.40; cubic three-point +0.19, +0.53; cubic fourth-order +0.76,
+1.7. Prediction (2) fails for the cubic cloud: the sharper the pass, the more the
shortest wave OVERSHOOTS. At the two longer waves all compensated runs agree with each
other and with 64 cells (+0.1 to +0.2 percent at z = 10, +0.5 to +1 at z = 1, +1 to +2
at z = 0): that part is the growth of second order. The overshoot of the shortest wave
is not explained (candidate: the response of a deposited lattice differs from the
window of the cloud by aliased terms, as the C6 agent found for estimators).
Decision: the three-point pass is the default; the fourth-order term gains nothing.
Damping with a constant coefficient in the smaller box (`dav_c256_n64_kct`):
Hamiltonian constraint 1.8e-4 at z = 1 and 1.1e-3 at z = 0 against 1.3e-4 and 6.9e-4.
Prediction (lower by more than ten): FAILS; it is slightly higher.
Cubic cloud with compensation in the smaller box (`dav_c256_n64_pcsct`): Hamiltonian
constraint equal to the other two configurations from z = 30 to 10 (1.9e-7, 1.5e-6),
then 1.4 to 3.4 times below the compensated quadratic run; momentum constraint 2.4
times lower at z = 100, 1.5 at z = 10, 2.5 at z = 1. My sharpened prediction (three or
more between z = 30 and 2) fails for the Hamiltonian constraint. The density error of
the Python experiment is therefore not what sets it.
Five variants at 32 cells, larger box, cubic cloud, compensated (z = 100, 10, 1, 0):
  reference        H 6.4e-8, 1.5e-7, 1.9e-6, 7.6e-6   M 2.1e-4, 7.8e-4, 1.4e-3, 4.3e-3
  dissipation 0.1  H 6.1e-8, 1.3e-7, 1.8e-6, 7.4e-6   M 2.6e-4, 9.0e-4, 9.5e-4, 1.6e-3
  damping rate 2   H 2.0e-7, 4.9e-7, 6.3e-6, 2.2e-5   M 4.0e-4, 8.0e-4, 1.7e-3, 4.8e-3
  27 per cell      H 2.7e-8, 1.2e-7, 1.9e-6, 7.4e-6   M 2.6e-4, 7.9e-4, 1.5e-3, 4.2e-3
  tolerance 1e-14  identical to the reference
  step 0.125 cell  H 6.3e-8, 1.2e-7, 1.9e-6, 7.6e-6   M 1.9e-4, 2.3e-4, 1.4e-3, 4.3e-3
Reading: the Hamiltonian constraint is three times higher at every epoch with four
times the damping rate, and indifferent to everything else. The momentum constraint
in the middle of the run follows the square of the step (3.4 for a factor of two) and
late it falls with the dissipation (2.7 at z = 0).
Hypothesis: the particles keep a momentum-constraint error of 1e-3 alive (sampling,
step), and the damping terms of the formulation, which couple the constraint variable
Theta and the conformal connection into the evolution of K and of the connection,
turn part of it into a Hamiltonian-constraint error at a rate proportional to the
damping coefficient. Runs `dav_c704_n32_pcsct_{k01,k002,k0}` (damping rate 0.1, 0.02
and none). Predictions: Hamiltonian constraint at z = 10 and 1 falls roughly in
proportion down to rate 0.1 (to about 3e-8 and 4e-7) and then levels off at whatever
the sources themselves leave; without any damping the run stays stable to z = 0 in
this linear box (if it does not, the damping is needed and its rate is a trade).

## C4, resolution test: complete with the Newtonian run at 128 cells (05:08)

Amplitude 0.01, quadratic cloud, 64, 96, 128 cells (one particle per cell). Infall of
the observers that start at L/32, L/16, L/8, L/4 from the overdensity, delay of the
relativistic run against the Newtonian one in a_p:
   64 cells: 4.61, 4.55, 4.79, 5.25 percent
   96 cells: 4.44, 4.51, 4.74, 5.27 percent
  128 cells: 4.39, 4.48, 4.72, 5.31 percent
The changes from 96 to 128 cells are at most 0.05 points. Relativistic infall of the
innermost observers at a_p = 58.88, 58.18, 57.92 and Newtonian at 56.29, 55.70, 55.48:
each converges, and so does their ratio. The delay at this amplitude is 4.4 percent for
observers near the overdensity and 5.3 percent for those that start a quarter of the
box away, resolved to 0.1 points.
The mean relative Hamiltonian constraint at a = 20 and 40 is the same at the three
resolutions (1.0e-4 to 1.1e-4, 2.1e-4 to 2.3e-4): the resolution-independent level seen
in the random-field runs, where it follows the damping coefficient (entry above).

## C5: 27 particles per cell in the smaller box, outcome (05:11)

`dav_c256_n64_p3t` against `dav_c256_n64_t` (8 per cell), quadratic cloud, no
compensation. Mean relative Hamiltonian constraint at z = 30, 10, 5, 2, 1, 0.3, 0:
3.6e-7, 2.7e-6, 9.3e-6, 4.5e-5, 9.6e-5, 2.2e-4, 5.1e-4 against 1.8e-7, 1.2e-6, 7.3e-6,
5.0e-5, 1.3e-4, 3.5e-4, 6.9e-4. Momentum constraint 1.4e-3, 4.2e-3, 9.9e-3, 2.3e-2,
3.4e-2, 6.4e-2, 0.11 against 9.2e-4, 1.3e-3, 6.3e-3, 2.8e-2, 4.9e-2, 8.7e-2, 0.13.
Predictions: no gain at z = 10: holds (it is worse, as three per cell and direction
were slightly worse than two in the Python table); a factor of 1.5 to 2.6 from z = 4
to 1: fails (1.1 to 1.4); a factor of 1.8 after collapse: fails (1.35 to 1.6).
So 3.4 times the particles change the constraints after collapse by a third. The
level there is not shot noise. With the damping style, the cloud order, the
compensation and the limiter all tried, the remaining lead is the dependence on the
damping coefficient found in the larger box.

## C5/T1: damping rate, outcome; the constraint field goes into the dumps (05:35)

`dav_c704_n32_pcsct_{k01,k002,k0}` with the reference (0.5) and rate 2. Mean relative
Hamiltonian constraint at z = 100, 10, 1, 0.02:
   rate 2     2.0e-7, 4.9e-7, 6.3e-6, 2.2e-5
   rate 0.5   6.4e-8, 1.5e-7, 1.9e-6, 7.6e-6
   rate 0.1   4.7e-8, 1.7e-7, 1.9e-6, 6.8e-6
   rate 0.02  4.9e-8, 1.1e-7, 2.0e-6, 7.6e-6
   none       4.9e-8, 1.0e-7, 1.5e-6, 6.3e-6
Momentum constraint the same in all (7.8e-4 at z = 10, 4.0e-3 to 4.8e-3 at the end).
Prediction (falls in proportion down to rate 0.1): FAILS. The constraint rises with
the rate above 0.5 and is flat below it: stronger damping feeds the Hamiltonian
constraint, weaker damping does not lower it. The run is stable to z = 0 without any
damping. So the level of 1e-7, 1.5e-6, 6e-6 is intrinsic to the coupled scheme at this
amplitude: it does not depend on the damping (at or below 0.5), the cell size (from
z = 0.3 on), the step, the cloud order, the particle number, the pusher tolerance or
the dissipation; the compensation doubles it; it grows as the square of the contrast
(about 1e-3 times the squared rms contrast in both boxes). Rate 0.5 stays the default.
I stop guessing here. New output: with `field_constraints = true` the field dumps
also hold the Hamiltonian constraint, the momentum constraint, Khat, Theta and the
lapse (format NRFIELD2). Next: look at the constraint field itself (where it sits,
its spectrum, what it correlates with) in `dav_c704_n32_pcsct_f`.

## C5/T1: the constraint field, and a wrong inference of mine corrected (05:51)

`dav_c704_n32_pcsct_f` and `dav_c704_n64_pcsct` with the constraint fields in the
dumps (`cosmo/analysis/constraint_field.py`).
32 cells, z = 1 to 0: 90 percent of the power of the Hamiltonian-constraint field lies
between 4 and 6 times the fundamental wave number, above the cut-off of the initial
spectrum (3.2) and below twice it: the sum wave numbers of pairs of initial waves. The
field follows the Laplacian of the squared contrast (correlation 0.79; rms 1.8e-5 of
16 pi <E> at z = 0). These waves are 5 to 8 cells long at 32 cells.
64 cells, z = 0: that part is 37 times smaller (rms 4.8e-7); 94 percent of what is left
(rms 2.2e-6) lies above 13 times the fundamental, at the scale of the mesh.
Mean relative constraints of the cubic compensated run at 64 cells, z = 100, 10, 1,
0.3, 0.02: Hamiltonian 3.5e-8, 8.5e-8, 1.7e-7, 3.2e-7, 6.8e-7; momentum 2.2e-4, 2.3e-4,
2.4e-4, 3.8e-4, 7.3e-4. Quadratic compensated at 64 cells: 2.1e-8, 8.5e-8, 6.4e-7,
4.4e-6, 1.0e-5 and 6.0e-4, 5.3e-4, 1.3e-3, 4.6e-3, 9.6e-3. So at 64 cells the cubic
cloud is 15 times lower in the Hamiltonian and 13 times lower in the momentum
constraint at the end. Power up to the cut-off: 0.20, 0.45, 1.2, 2.0 percent at z =
100, 10, 1, 0 (the last two are growth of second order).
Correction. I wrote above that the late level "does not depend on the cell size, the
cloud order, ...", and called it intrinsic. That came from comparing the quadratic
cloud at 64 cells with both clouds at 32 cells, two changes at once. There are two
different errors of similar size:
- at 32 cells, the truncation error of the terms of second order in the contrast,
  which live at up to twice the cut-off wave number, here 5 cells per wave; it is
  the same for both clouds and falls fast with the cell size;
- at 64 cells with the quadratic cloud, the sampling error of the displaced lattice,
  which the cubic cloud lowers tenfold, as the Python experiment said it would.
The damping dependence (higher above rate 0.5) and the absence of a dependence on the
particle number at 32 cells stand as measured. The rule that follows: the cut-off of
the initial spectrum must be resolved with twenty cells, not ten, if the terms of
second order are to be resolved, and the cloud must be cubic.
Consequence for the smaller box: its 64-cell runs have 10 cells per cut-off wave, so
their rise from z = 30 on is the same truncation of second-order terms, and the cloud
could not help there. The 128-cell run with the cubic compensated cloud is the test.
Prediction for `dav_c256_n128_pcsct` (one particle per cell): mean relative
Hamiltonian constraint at z = 10 below 3e-7 (1.5e-6 at 64 cells) and at z = 5 below
1e-6 (5.4e-6); after the first collapse it rises as before.

## T1: conservation on the mesh, and the interpolation of the metric (06:09)

New diagnostic (`cons_dcycle`, file `.cons.hst`): the residuals of the energy and
momentum equations of the deposited matter on the mesh, in density form, relative to
the root of the sum of squares of their terms; the test of paper 2's last figure
(which reports 1e-2 for both at all resolutions and redshifts) in this code's variables.
First use, the small linear run of the restart test (one wavelength of 32 cells, linear
cloud, one particle per cell at the cell corners): momentum residual 1.27e-3, the same
in every cell; energy residual 4.2e-3 in the mean. With the compensation (c = 1/12):
1.0e-3. So it is not the cloud. It is the metric interpolation at the particles. The
Catmull-Rom reconstruction of the method has a gradient whose error depends on the
position in the cell at second order: for a wave of wavenumber k it is low by
(k h)^2/6 at the cell centres, high by (k h)^2/12 midway between them and high by
(k h)^2/48 at the quarter points (computed: -6.4, +3.1, +0.6 percent for a wave of ten
cells, the last with a part of 1.3 percent out of phase). The residual equals deposit
response times gradient response minus one: for this lattice (1 - (k h)^2/8)(1 +
(k h)^2/12) - 1 = -1.6e-3, over root two 1.15e-3: as measured.
Consequences: the force on a lattice particle is wrong by a fixed fraction that
depends on where the lattice sits in the cells (a growth error), and it changes as
the particles cross cells (a force with the period of the mesh).
New option `interp = bspline`: the cubic spline through the nodal values (B-spline
weights on values sharpened with the inverse of the sampled spline to second order;
same 64-point stencil, twice continuously differentiable); its gradient error is of
fourth order and independent of the position in the cell.
Same small run with it: momentum residual 3.5e-3 without compensation (now the
deposit response alone, -4.8e-3 over root two: as predicted), 1.26e-3 with c = 1/12,
1.3e-4 with c = 1/8 (the response of a linear cloud deposited from the cell corners is
1 - (k h)^2/8, not the window's 1/12), and with the cubic cloud and c = 1/6: momentum
residual 1.4e-4, energy residual 1.4e-5 (4.2e-3 with the linear cloud).
Runs (larger box, step limit, cubic cloud, spline interpolation, constraint fields and
conservation records): `dav_c704_n32_pcsbt`, `dav_c704_n64_pcsbt` (three-point pass)
and `dav_c704_n32_pcs4bt` (with the fourth-order term). Predictions:
(1) Momentum residual at z = 100 and 10 below 3e-4 at 32 cells (to be compared with the
    Catmull-Rom run `dav_c704_n32_pcsct_c`, same settings, started with them).
(2) Mean relative momentum constraint at z = 100 to 10 at least two times below the
    Catmull-Rom run (2.1e-4 to 7.8e-4 at 32 cells).
(3) Power of the shortest wave (ten cells): with the three-point pass now a DEFICIT
    (the overshoot of +0.2 to +0.5 percent came from the gradient error, which is
    gone; the remainder of the pass is -0.43 percent in the source, about -1 percent in
    the power at z = 100); with the fourth-order term within 0.2 percent at z = 100
    and 10.

## T1: spline interpolation, outcome at 32 cells; the fourth-order pass reinstated (06:19)

`dav_c704_n32_{pcsct_c,pcsbt,pcs4bt}` (cubic cloud, step limit; Catmull-Rom with the
three-point pass; spline with the three-point pass; spline with the fourth-order pass).
(1) Momentum residual on the mesh (mean, relative), constant through the run: 2.2e-3,
    4.3e-4, 9.8e-4. Five times lower with the spline; predicted below 3e-4: fails by a
    factor 1.4. The energy residual is 4.6e-3 in all three, the size of the fourth-order
    truncation of the diagnostic's own differences for waves of ten cells ((k h)^4/30 =
    5e-3), which also limits the momentum residual here; 64 cells will be cleaner.
(2) Momentum constraint: unchanged (3.1e-4 against 2.1e-4 at z = 100, equal later).
    Predicted two times lower: FAILS. Hamiltonian constraint at z = 100, 30, 10: 2.3e-8,
    6.0e-8, 1.1e-7 against 6.4e-8, 1.1e-7, 1.5e-7; equal later (second-order terms).
(3) Power, signed, three shells up to the cut-off (the last is the wave of ten cells):
      Catmull-Rom, three-point:  z = 100  +0.08 +0.23 +0.19   z = 10  +0.35 +0.76 +0.53
      spline, three-point:                -0.06 -0.23 -0.62           -0.01 -0.29 -1.26
      spline, fourth-order:               -0.01 -0.01 -0.06           +0.06 +0.11 -0.13
    (percent). Both predictions hold: a deficit with the three-point pass, and within
    0.2 percent with the fourth-order term. With deposit and force both right to
    fourth order, every wave of the initial data, down to ten cells, follows linear
    theory to about a thousandth over a hundredfold expansion at 32 cells.
Correction of the earlier decision ("the fourth-order term gains nothing"): its
overshoot with the Catmull-Rom interpolation was the gradient error of that
interpolation, which the more exact deposit no longer hid. With the spline the
fourth-order term is what is needed.
Production configuration from here on: cubic cloud, pass with c = 1/6 and c2 = 7/15,
spline interpolation, step limit, damping rate 0.5. The 128-cell chain of the smaller
box with the three-point pass and Catmull-Rom was stopped before it started.

Production runs with the consistent configuration, written before them:
`dav_c704_n{64,128}_pcs4bt`, `dav_c256_n64_pcs4bt` (batches) and `dav_c256_n128_pcs4bt`
(chain). Predictions: larger box, power within 0.2 percent of linear theory up to the
cut-off at z = 100 and 10 at both resolutions, constraints at or below those of the
three-point runs (Hamiltonian below 7e-7 to z = 0 at 64 and 128 cells). Smaller box at
64 cells: power within 0.4 percent at z = 100 and 10 (the contrast is 0.05 at z = 10, so
a few thousandths of second-order growth are expected); constraints as before (the
second-order terms are under-resolved at 64 cells). Smaller box at 128 cells: the
prediction written for the stopped chain stands (Hamiltonian constraint below 3e-7 at
z = 10 and below 1e-6 at z = 5; rise after the first collapse as before).

## C5/T1: spline interpolation at 64 cells; smaller box at 128 cells without the new elements (06:28)

`dav_c704_n64_pcsbt` (cubic cloud, three-point pass, spline). Conservation on the mesh
(mean, relative): momentum residual 2.6e-5 to 3.0e-5 from z = 100 to 2, 1.2e-4 at the end
(32 cells: 4.3e-4; ratio 16, fourth order); energy residual 4e-4 to z = 5, 3.9e-3 at the
end (32 cells: 4.6e-3). Paper 2 reports 1e-2 for both at every resolution and redshift,
without convergence (its measure divides by larger terms than this one, which uses the
density form in which the background terms cancel). Constraints: as with Catmull-Rom
from z = 10 on (Hamiltonian 8.5e-8, 1.7e-7, 6.8e-7 at z = 10, 1, 0; momentum 2.3e-4 to
7.4e-4); the Hamiltonian constraint at z = 100 is 2.2e-8 against 3.5e-8.
`dav_c256_n128_t` (quadratic cloud, no compensation, Catmull-Rom, one particle per
cell; chain of two segments, restart at t = 38.8): reaches z = 0. Mean relative
Hamiltonian constraint at z = 100, 30, 10, 1, 0: 6.0e-8, 5.5e-7, 4.4e-6, 2.1e-4, 8.6e-4;
momentum constraint 1.5e-3, 3.2e-3, 1.2e-2, 0.16, 0.37. From z = 30 on this is WORSE
than 64 cells with 8 particles per cell (1.8e-7, 1.2e-6, 1.3e-4, 6.9e-4 and 9.2e-4,
1.3e-3, 4.9e-2, 0.13): one quadratic cloud per cell samples the displaced lattice
poorly (the Python table: six times the error of two per direction). Power up to the
cut-off: 0.55 percent at z = 100 and 1.8 percent at z = 10 (64 cells: 9 and 18);
below half the cut-off 0.16 and 0.82 percent (predicted within 2.5: holds). Paper 2 at
128 cells: 0.3 to 3.5 percent at z = 100 and 0.3 to 10 percent at z = 10 across the
band; constraints 4.5e-8, 4.3e-8, 3.9e-7, 4.8e-6 and 2.0e-3, 2.8e-3, 7.1e-3, 4.2e-2.
