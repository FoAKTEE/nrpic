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
