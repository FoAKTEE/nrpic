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
