# Journal of the package E-pre-2 (code-base design review)

Owner: E-stoch-inf (helper for E-pre-2, under decision 0010). Entries are appended;
nothing is rewritten. Labels as in the brief: [VERIFIED], [BACKGROUND], [JUDGEMENT],
[TO VERIFY]. Run ids: `tracks/E-stoch-inf/runs/<run_id>/manifest.json`, outputs in
`/data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>/`.

## 2026-11-15 12:30 UTC: what was read

Code (worktree at a1c2237, merged with main): `athenak/src/z4c/` (z4c.hpp, z4c.cpp
options, z4c_calcrhs.cpp whole, z4c_tasks.cpp whole, z4c_update.cpp, z4c_newdt.cpp,
tmunu.{hpp,cpp}, z4c_adm.cpp constraint terms), `tasklist/numerical_relativity.hpp`,
`driver/driver.cpp` (integrators), `dyn_grmhd/dyn_grmhd.cpp` (task queue, SetTmunu),
`particles/nrpic.cpp` (cycle, NrpicStepSources, NrpicAddLambda, NrpicDeposit),
`particles/particles_tasks.cpp`, `particles/nrpic_io.cpp` (constraint statistics),
`utils/finite_diff.hpp`, `srcterms/turb_driver.cpp` (how random modes are built),
`pgen/nrpic/nrpic_cosmo.cpp` (header, options), `CMakeLists.txt` (FFTW). Branch
`core/rng`: `utils/rng.hpp`, `utils/rng_mesh.hpp`, `tracks/core/interfaces/rng.md`.
`cosmo/README.md`, `cosmo/TESTLOG.md` (timings), `cosmo/ic/cosmo_id.py` (header),
`coord/notes/design_wave2_initial_data.md`, Track B `periodic_z4c/README.md`.
Papers at the source: 2512.14649 v2 `PRD_v2.tex` (whole), 2401.08530 v2
`Stochastic_Inflation.tex` lines 596-720, 2502.06783 v3 `main_V2PRD.tex` (numerical
settings, grep), thesis 2610.32592 `chap_SINR.tex` lines 102-135, `chap_ICsim.tex`
(grep). Branch `core/scalar-field` has no interface document yet (checked 12:20).

## 2026-11-15 12:35 UTC: predictions before the four checks of this package

D1, memory and throughput of the vacuum spacetime solver in a periodic box, processor
executable (`.work/build_cpu_c1/src/athena`, problem `z4c_linear_wave`, rk4, nghost 4),
64^3 cells, two MeshBlock sizes (32^3 and 64^3), 4 cycles each, one thread.
Prediction: Z4c with its ADM, constraint and Weyl arrays holds about 95 doubles per cell
including ghost cells (u0, u1, u_rhs 66; constraints 7; ADM about 17; Weyl 2; coarse
copy 22/8), so the resident memory grows by 0.7 to 1.0 kB per cell with ghosts, plus a
fixed part below 0.3 GB. Throughput 1e4 to 3e4 zone-cycles per second on one core (Track
B measured about 1.4e4). Refuted if the slope is below 0.5 or above 1.5 kB per cell.

D2, synthesis of a band-limited real field on the mesh without a Fourier library. A
field f(x) = sum over integer wave vectors n with 0 < |n| <= n_max of c_n exp(2 pi i n.x/L)
(Hermitian c) is evaluated MeshBlock by MeshBlock by three successive one-dimensional
sums (z, then y, then x), each MeshBlock using only its own cell coordinates. Prediction:
agrees with numpy.fft.ifftn of the same coefficients to a relative 1e-13 or better
(N = 32 and 64, n_max = N/4, MeshBlocks of N/4, N/2, N cells), and the results for
different MeshBlock sizes agree to the same level. Refuted if any difference exceeds
1e-12 relative to the root-mean-square of the field.

D3, first-order momentum constraint of the stochastic kick with the code's stencil.
Kick of 2512.14649 (BSSN form, its eq. RHSBSSN): dK = -eps1 S, dA_ij = eps1 P_ij S with
P_ij = delta_ij/3 - k_i k_j/k^2. Linearised about a homogeneous slice the momentum
constraint of the kick is D_j dA_ij - (2/3) D_i dK; with exact derivatives it vanishes.
With the sixth-order first derivative of `utils/finite_diff.hpp` (nghost 4), whose symbol
is k_eff h = (3/2) sin(kh) - (3/10) sin(2kh) + (1/30) sin(3kh), it does not, unless the
projector is built from k_eff instead of k. Prediction: (a) projector from k: relative
residual |M| / (|D dA| + (2/3)|D dK|) of 1e-5 or less for a shell at |n| ~ N/16 and
between 3e-3 and 1e-1 for a shell at |n| ~ N/4 (the largest wave number of the paper,
k_max = N k_sigma/4); (b) projector from k_eff: residual at rounding, below 1e-12, for
every shell. Refuted if (b) leaves more than 1e-12 or (a) at N/4 is outside [3e-3, 1e-1].

D4, stage times of the integrator and the window function. (a) The time at which the
low-storage RK4()4[2S] of `driver/driver.cpp` (Ketcheson 2010) evaluates its four
right-hand sides is found by running the scheme on u' = 1 (u = t): c_1 = 0,
c_2 = beta_1 = 1.1937..., c_3, c_4 from the recurrence; prediction: with the effective
weights b_i obtained from the same recurrence, sum b_i c_i^m = 1/(m+1) for m = 0..3 to
1e-14 (the scheme is fourth order for a source that depends on time only), and fails
for m = 4. Refuted otherwise. (b) Window W_k(t) = (1 + tanh(s ln(k_sigma/k)))/2, s = 5
(2512.14649, eq. ourWindow): the time derivatives are analytic,
dW/dt = (s/2) sech^2(u) d ln k_sigma/dt and
d2W/dt2 = (1/2) sech^2(u) [s d2 ln k_sigma/dt2 - 2 s^2 tanh(u) (d ln k_sigma/dt)^2],
u = s ln(k_sigma/k), d ln k_sigma/dt = H (1 - eps1). Check against centred differences
of W in time: agreement to 1e-8 relative at dt = 1e-4/H. Number of lattice modes of a
256^3 box with sech^2(u) > 1e-3 when k_sigma reaches k_max = 64 k_min: about
(4 pi/3) 64^3 (1 - 0.45^3) = 1.0e6, within 10 percent. Refuted otherwise.

## 2026-11-15 12:45 UTC: outcomes of D1 to D4

Runs: E-stoch-inf-20261115-122727-a1c2237 (D1, five AthenaK runs on one core) and
E-stoch-inf-20261115-123936-b2ec5c7 (analysis of D1, checks D2 to D4, cost table). The
first attempt of the analysis run used `python3 -I`, in which numpy is not visible; all
four scripts stopped at the import (logs in `attempt1/` of the run directory). Rerun
without `-I` (the scripts read no downloaded data). Figures in `figs/` (each inspected).

D1. Maximum resident memory 67.8, 123.7, 327.9, 499.5, 970.1 MB for 32^3/32^3,
32^3/16^3, 64^3/64^3, 64^3/32^3, 64^3/16^3 (mesh/MeshBlock); 1.45e4 to 1.54e4
zone-cycles per second on one core. A single slope per cell with ghosts does not describe
the five runs (it needs a negative intercept, -21 MB, and misses the many-block runs):
the ghost cells cost more than the interior cells because the boundary buffers scale
with them. Fit M = c0 + a N_int + b N_shell: c0 = 7.0 MB, a = 687 B per interior cell,
b = 1257 B per ghost cell, every run within 1 percent. Prediction (0.7 to 1.0 kB per
cell with ghosts; refuted below 0.5 or above 1.5): not refuted in range (0.69 and
1.26 kB), but the one-slope form of it was wrong. Throughput as predicted (Track B 1.4e4).
Extrapolation (d1.json): vacuum Z4c at 256^3 needs 15.7 GB with 128^3 MeshBlocks, 20.5 GB
with 64^3; with the scalar field, Tmunu and six noise fields 19.7 and 25.5 GB. 512^3 needs
126 to 204 GB: not on one 80 GB card. Host memory of the processor build stands in for
device memory of the card build [JUDGEMENT; to be checked on the first card run].

D2. Separable synthesis against numpy.fft.ifftn: largest difference 9.1e-15 (N = 32) and
1.2e-14 (N = 64) of the rms of the field, imaginary residue 7e-16 and 1.1e-15, for
MeshBlocks of N/4, N/2 and N; the results for different MeshBlock sizes are bitwise
identical (each cell sums the same terms in the same order). Operation count equals the
formula (N/b)^3 (M b + P b^2 + X b^3) in all six cases. Prediction confirmed. With the
half space of a real field, 256^3 and n_max = 64 cost 5.0e9 complex multiply-adds per
field with 64^3 MeshBlocks and 2.5e9 with 128^3 (299 and 149 per cell), against about
15 per cell for a radix-2 FFT.

D3. Projector from k: relative residual of the first-order momentum constraint 1.2e-7,
3.7e-6, 3.8e-5, 1.8e-4, 6.7e-4, 1.7e-3, 4.1e-3, 6.9e-3 for shells |n| = 2 ... 16 of a
64^3 box (k h = 0.20 ... pi/2), 4.6e-3 for the whole ball; zero (1e-15) for |n| = 1,
where every mode lies on an axis and the stencil error cancels. Projector from k_eff:
1.9e-16 to 1.0e-15 for every shell and 2.2e-16 for the ball. Prediction confirmed (shell
N/16: 3.7e-6 below 1e-5; shell N/4: 6.9e-3 inside [3e-3, 1e-1]; k_eff below 1e-12).

D4. (a) c = (0, 1.19374, 0.43140, 1.00000), effective weights b = (0.13586, -0.06484,
0.61832, 0.31067), coefficient of u_n 1 - 1.7e-15; sum b c^m - 1/(m+1) below 1.5e-15 for
m = 0..3, 4.0e-4 for m = 4. Confirmed. The second stage evaluates its right-hand side at
t + 1.19 dt, outside the step. For u' = cos t the error falls as dt^4 with the source at
the stage times (1.6e-9 to 2.9e-13 from 10 to 80 steps) and as dt with the source at
the start of the step. (b) Analytic dW/dt and d2W/dt2 against centred differences at
h = 1e-4/H: 8.2e-8 and 1.1e-7 relative. Prediction (1e-8) REFUTED at the stated level.
Follow-up (d4b_hscan.log, same run): the difference falls by 4.0 per halving of h
(1.3e-6, 3.3e-7, 8.2e-8, 2.0e-8 for dW/dt at h = 4e-4 ... 5e-5), so it is the h^2
truncation of the check and the analytic expressions stand; my threshold ignored the
s^4 = 625 in the truncation term. (c) Modes with sech^2(u) > 1e-3 when k_sigma reaches
k_max = 64 k_min in a 256^3 box: 1,006,630 of 1,097,916 in the ball (prediction 1.0e6).
Confirmed. The touched set grows as e^(3N) and holds about all modes from 3.4 e-folds
after the first crossing until the window has passed k_max.

The follow-up code of D4(b), run in `ref/`: for h in (4e-4, 2e-4, 1e-4, 5e-5) compare
`synth.window_dt` with centred first and second differences of `synth.window` at the 61
times of d4_stages_window.py (H = 1, eps1 = 0.01, eps2 = -0.02, s = 5); output
`d4b_hscan.log`.
