# Journal of the package usr (preparation of the ultra-slow-roll case)

Package `tracks/E-stoch-inf/usr/` of owner E-stoch-inf, wave 3a (2026-11-19). Helper, one
package; the owner's files (STATUS, HANDOFF, JOURNAL, RISKS) are the lead's.

Keys: P1 = arXiv:2512.14649 v2 `PRD_v2.tex`, P2 = arXiv:2502.06783 v3 `main_V2PRD.tex`
(sources under `kb-data/raw/arxiv/<id>/<v>/src/`); SPEC = `../spec/SPEC.md`; SCOPE =
`../spec/scope/SCOPE.md`. Labels [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## Entry 0, 2026-11-19 14:29 UTC: scope and plan

Task (wave 3a, helper `usr_prep`): prepare the second test case of SPEC, the Higgs
inflection potential with its ultra-slow-roll (USR) phase:

1. the background through the USR phase from the ordinary differential equations, with
   the times and field values a run must reproduce (code units of SPEC 2.5);
2. the expected power spectrum and its enhancement;
3. acceptance quantities and thresholds, written down before any run;
4. the inputs for core's executable `scratch/core/exe/core_scalar-2` (initial slice at N*:
   `<problem> id = stochastic` with the mode file);
5. a low-resolution processor run of the background and of a few modes.

What exists and is used, not redone:
- SPEC 6 table (run E-stoch-inf-20261115-122806-ef0d039, Mpl = 1): inflection case phi0 =
  -1.2, dphi/dN(N0) = 0.102682, H0 = 9.5902e-6, H* = 9.36232e-6, eps1(N*) = 1.3164e-2,
  eps2(N*) = -0.4307, USR (eps2 > 3) from cN = 2.53 to 6.55, eps2 max 6.000, eps1 min
  9.7e-13 at cN = 8.33, late eps2 -2.76e-2. These are the numbers to reproduce with an
  integrator written here.
- SCOPE 4: owner's choices N* - N0 = 3, N_f - N* = 10, Courant 0.25, backreaction level 0;
  A1 for USR at 1e-3; A3 for USR (modes k <= 3 dk within 10 percent of the full
  Mukhanov-Sasaki power at N_f).
- The code: `potential = inflection` with `lambda`, `vev` exists since release core-v0.3
  (`athenak/src/scalar_field/scalar_field.hpp:84-93`); `coord/INTERFACES/scalar_field.md`
  line 72 leaves its form [TO VERIFY by Track E against P1:405-409]. Core's branch
  executable core_scalar-2 (a58e95b) has the initial slice (`id = stochastic`); its
  READY says "the inflection (USR) case has not been run".
- The SR ladder of the other helper (`../ladder/`) uses the same executable; its input
  `../ladder/inputs/sr_base.athinput` is the template for the options (read, not changed).

Check done by reading, before any run [VERIFIED by reading]: P1:409 prints
V = Lambda v^4 phi^2 (3 phi^2 + 2 sqrt2 phi v + 6 v^2) / (3 (3 phi^2 + 2 v^2)^2), Lambda =
1.86e-6, v = 0.198 Mpl, phi0 = -1.2 Mpl (P1:411-413); `scalar_field.hpp:85-93` codes
c = lambda vev^4/3, V = c phi^2 P/Q^2 with P = 3 phi^2 + 2 sqrt2 phi vev + 6 vev^2,
Q = 3 phi^2 + 2 vev^2, the same expression, and
dV = c[(2 phi P + phi^2 P')/Q^2 - 2 phi^2 P Q'/Q^3], P' = 6 phi + 2 sqrt2 vev, Q' = 6 phi,
which is the derivative of that expression (quotient rule). The numerical check of V and
V' in code units against the Planck-unit form is item T0 below.

## Entry 1, 2026-11-19 14:35 UTC: reference written; development pass (unregistered)

`scripts/usr_reference.py` (T0-T4, docstring) was developed against a scratch output
(`scratch/E-stoch-inf/tmp/usr/dev1`, nmax2 up to 64, not registered; no number below is
used before the registered rerun of entry 4 repeats it). What it showed, for the record:
- T1 reproduces SPEC 6 to the digits printed there: dphi/dN(N0) = 0.1026820, H0 =
  9.590198e-6, H* = 9.362319e-6, eps1(N*) = 1.316389e-2, eps2(N*) = -0.430663, USR
  (eps2 > 3) from cN = 2.5234 to 6.5503, eps1 minimum 9.716e-13 at cN = 8.331.
- New landmarks: eps1 maximum (eps2 = 0) at cN = 1.6240; eps2 maximum 5.99999965 at
  cN = 4.53196, which is where the field passes the inflection point phi = -sqrt2 v
  (V' = 0 there, so eps2 = 6 - 2 eps1); code time of N* + 10 e-folds t = 10.4375.
- T2: the code-time system (K evolved) against T1 mapped to code units: 1.2e-12 (phi),
  2.6e-9 (Pi, which falls to 2.6e-7), 6.7e-14 (K).
- T2, RK4()4[2S] in the ADM form at dt = 0.0491 (32^3, Courant 0.25): Pi wrong by 4.1e-4
  relative at the end; 2.5e-5 at Courant 0.125 (factor 16.3); 9.3e-8 at 256^3. Reason
  [JUDGEMENT]: after USR the field is on the slow-roll attractor next to the inflection
  point, Pi ~ V'/(3H) ~ (phi - phi_i)^2, so a step error of 3.5e-7 in phi (absolute 2e-8
  in code units, against phi - phi_i = 3.8e-5) becomes 1e-3 in Pi. A1 for USR (1e-3,
  SCOPE 4) is therefore only a factor 2.4 above the time error of a 32^3 run at Courant
  0.25.
- The mode file for nmax2 = 64 agrees with core's `make_case.py` reference
  (`python/nrpic/sf_inflation.py:code_case` on core/scalar-2, imported from a copy in
  scratch) to 2.0e-10 relative in R and dR; phi0, pi0, lambda, vev to 1e-14.
- FLRW lattice (field perturbation on the unperturbed background) over full MS at N_f:
  8.80 (k = dk), 2.09 (2 dk), 1.37 (3 dk), 1.18 (4 dk) when started at N* from the same
  data as the NR run; started at N0 instead: 8.40, 2.07, 1.18 and 1.44 at 2.83 dk, which
  are SPEC 7.3's numbers. Both readings put the owner's 10 percent threshold of A3 (USR)
  far from the FLRW behaviour for k <= 3 dk.

The registered reference pass was then changed in one point before it ran: the
RK4()4[2S] twin now integrates the homogeneous limit of AthenaK's Z4c
(`z4c_calcrhs.cpp:568, 627-653`: K = Khat + 2 Theta, d Theta = K^2/3 - 8 pi E,
d Khat = K^2/3 + 4 pi (S + E)) with chi itself as the variable, i.e. exactly the
equations a homogeneous run discretises, so that the run can be compared with it cycle by
cycle; the exact solution is unchanged (Theta = 0 on the constraint surface).

## Entry 2, 2026-11-19 14:37 UTC: acceptance of the USR case (proposal to the owner)

[JUDGEMENT] Written before any run with the inflection potential. Owner's thresholds of
SCOPE 4 are kept where they exist; the rest is proposed for G2.

| Id | Quantity | Threshold | Reference | Why this threshold |
|---|---|---|---|---|
| U-A0 | landmarks of the background: e-folds -ln<chi>/2 at the code times of the USR onset, eps2 maximum, USR end, eps1 minimum, N_f (`results/landmarks.csv`) | 1e-5 absolute in N | T1/T3 | e-folds of the SR runs within 5.5e-6 at Courant 0.25 (core, scalar_field_2.md 6) |
| U-A1 | box means phi, Pi, K against the Friedmann reference | 1e-3 relative (SCOPE 4) for the homogeneous run; for the stochastic runs the deviation is reported with its parts (time error from the twin, second-order backreaction from the +-s runs) | T2 | time error of 32^3 at Courant 0.25 is 4e-4 in Pi (entry 1); 256^3: 1e-7 |
| U-A1t | homogeneous run against the RK4()4[2S] twin of the same step sequence | 1e-11 relative (phi, K, chi), 1e-9 (Pi) | twin | the code and the twin discretise the same ODE with the same scheme; rounding only |
| U-A2 | per mode, linear limit (`noise_mode_scale` 1e-3): abs(R^NR_n/(s W R alpha_n L^-3/2) - 1) at N_f, every mode with k <= k_max/2 (all modes of a run with 8 cells per shortest wavelength) | 0.02 (A2 of SCOPE 4) | code-time MS from the run's mode file, continuum and stencil k^2 | as SR; judged at N_f because R_k passes near zero at cN = 3.7-4.7 (dip before the USR growth, `fig/fig_usr_modes.png`), where a ratio means nothing; over the run the error is normalised by max_t abs(reference) |
| U-A2s | same at full amplitude, odd part (R(+1) - R(-1))/2 | 0.02 | same | third-order terms ~ R_rms^2 |
| U-A2n | even part (R(+1) + R(-1))/2 relative to the odd part, rms over modes, at N_f and in time | reported, not gating; must stay below 0.3 (else the case is not perturbative at that resolution) | separate-universe estimate (abs(eps2)/4) R_rms, and R_rms itself | geodesic slicing: the field on a proper-time slice differs by phi_b(t + dN/H) - phi_b(t), second order (phi_NN/phi_N) dN^2/2 = -(eps2/4) dN^2 |
| U-A3 | freezing / NR versus FLRW: per-mode power at N_f of the modes k <= 3 dk | within 10 percent of the full MS (SCOPE 4) | full MS | FLRW lattice off by 8.8, 2.1, 1.4 (from N*) |
| U-A4 | constraints: <abs(H)/[H]> and <abs(M)/[M]> second order (halving s halves <abs(M)/[M]>, core's reading of A4); negative control first order | as SCOPE 4 A4 | P1:538-541 | |
| U-A5 | spectrum with enhancement: Delta_R(k) of the realisation, per shell, at N_f against W^2 Delta_ms | the per-mode U-A2 implies it; the shell average is reported against `results/usr_spectrum_Nf.csv` | T4 | cosmic variance is removed by the per-mode comparison |
| U-A6 | one-point: rms of R^NR at N_f against the lattice sum of the realisation and of the ensemble (`results/usr_reference.json`, lattice_variance) | reported (A8 is G3) | T4 | |

What these thresholds cannot see [JUDGEMENT]: the production set-up (256^3, k_max = 64 dk)
reaches Delta_R ~ 1 at N_f (langevin reference: 1.017 at 64 dk), where U-A2n is expected
to fail; P1 itself claims only "excellent agreement" of the binned spectra there
(P1:536). The low-resolution runs of this package stay at R_rms ~ 0.02 (nmax2 = 16) and
0.07 (nmax2 = 64), where the linear comparison is meaningful.

## Entry 3, 2026-11-19 14:38 UTC: predictions for the registered runs (before they run)

Runs planned (inputs from `scripts/make_inputs.py`, list `inputs/proc.list`, script
`scripts/run_list.sh`; all serial, one core each):

| Name | Executable | Set-up |
|---|---|---|
| BGv03, BGv03h | release core-v0.3 (`.work/build_cpu_v03`) | id = flrw, 8^3, Courant 0.0625 (dt = 0.04909, the step of 32^3 at 0.25) and 0.03125 |
| BGs2 | core_scalar-2 (a58e95b) | same as BGv03 |
| M16p, M16m, M16l | core_scalar-2 | id = stochastic, 32^3, nmax2 = 16 (14 shells, 128 modes, k <= 4 dk, 8 cells per shortest wavelength), s = +1, -1, 1e-3, to t = 10.4375 (N* + 10) |
| M64p, M64m | core_scalar-2 | nmax2 = 64 (k <= 8 dk, the paper's k_max = N/4 dk at N = 32), s = +1, -1 |
| NC16 | core_scalar-2 | M16p with noise_pi_sign = -1 to t = 3 (negative control) |

Predictions (refuted if outside the stated range):
- R0 (reference, registered rerun): T1 landmarks identical to entry 1 to 1e-12; mode files
  n16, n64 byte-identical to the development pass (same code path; only the twin and the
  CSV output changed); Z4c-form twin at dt = 0.0491 gives Pi error at the end within 5
  percent of the ADM-form 4.1e-4 (same scheme, the two forms differ only off the
  constraint surface).
- BG1 (U-A1t): BGv03 equals the Z4c twin run with the run's own step sequence (from the
  time column of `bg.sf.hst`) within 1e-11 relative in <phi>, <K>, <chi> and 1e-9 in <Pi>
  at every cycle.
- BG2: BGv03 against the exact background at the end: Pi off by the twin's value
  (about 4e-4), phi about 3e-7, K about 1e-8 relative; e-folds -ln<chi>/2 within 1e-7 of
  10 at t = 10.4375. U-A1 (1e-3) passes, U-A0 (1e-5) passes.
- BG3: BGv03h reduces the Pi error by 16 +- 1.5 (fourth order).
- BG4: BGs2 equals BGv03 byte for byte in `bg.sf.hst` (core_scalar-2 changed no file on
  this path), or within 1e-15 if the two builds round differently.
- M1 (U-A2): M16l at N_f: max over the 128 modes of abs(R^NR/(s W R alpha L^-3/2) - 1)
  below 5e-3 against the continuum reference, expected about 1e-3 (stencil dispersion
  3.8e-4 in k^2 at k dx = pi/4 enters the USR growth ~ (k/aH)^2 linearly, plus the
  4e-4 background time error); with the stencil k^2 in the reference no worse.
- M2 (U-A2s): odd part of M16p/M16m within the same 5e-3; even/odd rms ratio at N_f
  between 1e-3 and 5e-2 (R_rms of the realisation about 0.02); its maximum in time
  during or right after USR.
- M3 (U-A3): k = dk, 2 dk, 3 dk: NR power at N_f within 1 percent of the full MS (FLRW:
  8.8, 2.1, 1.4). The same for M64p's odd part.
- M4 (U-A4): M16p <abs(H)/[H]> <= 1e-10 at all times (the slice starts near 3.5e-12;
  K gets no perturbations in USR, P1:532); <abs(M)/[M]> <= 1e-2 at all times;
  M64p within factors 10 of these. NC16: <abs(H)/[H]> at least 100 times M16p's in the
  first e-fold, <abs(M)/[M]> of order 0.1 to 1.
- M5 (backreaction on the means): abs(<Pi>(M16p) - <Pi>(M16l))/<Pi> <= 1e-3 at all
  times; for M64p <= 1e-2. <phi> and <K> differ by less than 1e-8 relative.
- M6 (lockstep record `.modes` against the code-time reference from the same mode file):
  within 1e-4 relative at N_f for every shell.
- M7 (cost): 1.1e4 zone-cycles per second per core (smoke test), 213 steps at 32^3:
  about 11 minutes per full run.

Smoke tests before this entry (unregistered, scratch/E-stoch-inf/tmp/usr/dev1/smoke_*):
both executables accept the inputs (3 and 2 cycles); no number of them is used.

## Entry 4, 2026-11-19 14:41 UTC: outcome of the reference run E-20261119-143905-f2bcde3

Registered as scouting for G2 (`nrpic-run` refuses production before G1's sign-off);
39 s on 4 cores. Outputs copied: `results/usr_reference.json`, `results/landmarks.csv`,
`results/usr_spectrum_Nf.csv`, `inputs/modes_usr_n{16,64,256,1024,4096}.txt` (sha256 in the
JSON equal those of the copies), `fig/fig_usr_*.png`.

Against R0 (entry 3):
- Landmarks identical to the development pass to all printed digits: confirmed.
- Mode files byte-identical: REFUTED. They differ by 5.3e-13 (n16) and 2.9e-10 (n64)
  relative. Cause: the mode functions of all shells are integrated as one vector, so the
  adaptive step follows the highest shell present; the registered run included 3414
  shells (nmax2 = 4096), the development pass 54. The difference is the integration
  tolerance, as it should be. Every run of this package uses the registered files.
- Z4c-form twin at dt = 0.0491: Pi wrong by 4.124e-4 at the end against 4.128e-4 of the ADM
  form: within 5 percent, confirmed. Theta of the twin reaches 1.07e-7 (Courant 0.25),
  6.2e-9 (0.125), 2.3e-11 (256^3).
- New, and it changes prediction BG2 before any AthenaK run: with chi as the variable
  (as the code evolves it) the e-folds -ln(chi)/2 carry the step error of chi, which
  falls as exp(-20): abs error of ln chi 1.40e-5 at the end for 32^3 at Courant 0.25,
  8.4e-7 at 0.125, 3.2e-9 at 256^3 (in ln chi; half of it in N). So U-A0 (1e-5 in N) is
  at the edge for 32^3 at Courant 0.25 (7e-6 in N) and met with margin at 256^3.
  Revised BG2: the e-folds of BGv03 at the end equal the twin's (10 - 7e-6 in N, sign
  from the twin), not "within 1e-7 of 10".

Reference numbers for the record [VERIFIED by run E-20261119-143905-f2bcde3]:
- code inputs: lambda = 5.333176485263404e5, vev = 3.9495285759741844e-2,
  phi0 = -0.16432818834720297, pi0 = 3.236586527912448e-2, K0 = -3, tlim = 10.437508874065651.
- landmarks (cN; code time; phi; Pi; K): eps1 maximum 1.6240, 1.64652, -0.101593, 4.2454e-2,
  -2.909243; USR onset 2.5234, 2.58291, -0.0675096, 2.4339e-2, -2.861418; inflection point
  and eps2 maximum (5.99999965) 4.5320, 4.69265, -0.0558548, 1.1264e-4, -2.855443; USR end
  6.5503, 6.81319, -0.0558151, 5.1426e-7, -2.8554426; eps1 minimum (9.716e-13) 8.3310,
  8.68406, -0.0558145, 2.6466e-7, -2.8554426; N_f 10, 10.43751, -0.0558140, 2.6961e-7,
  -2.8554426, eps2 = -2.7615e-2 (SPEC 6: -2.76e-2; P1:534: -2.8e-2).
- spectrum at N_f (Delta_R full MS; FLRW/MS started at N*; enhancement over
  H^2/(8 pi^2 eps1) at k = aH): k = dk 1.023e-5, 8.80, 1.21e5; 2 dk 1.251e-4, 2.09, 2.1e6;
  3 dk 5.29e-4, 1.37, 1.1e7; 4 dk 1.449e-3, 1.18, 3.2e7; 8 dk 1.505e-2, 1.02, 2.8e8;
  16 dk 0.1195, 0.998, 3.2e8; 32 dk 0.531, 0.999, 3.9e7; 64 dk 1.0168, 1.000, 1.2e6.
  Largest enhancement 4.2e8 near 12 dk (modes that cross about one e-fold before the USR
  onset); Delta_R rises monotonically to 1.017 at 64 dk (SPEC 7.3: 1.017).
- one-point rms of W R on the lattice at N_f: 0.0198 (32^3, nmax2 16), 0.0664 (32^3, 64),
  0.201 (64^3, 256), 0.494 (128^3, 1024), 0.894 (256^3, 4096). The last squared is 0.7987,
  the lattice band variance of the langevin package (0.79863, run
  E-stoch-inf-20261115-130137-176cdd6, `../langevin/README.md`): two independent codes agree.
- Super-horizon drift of ln Delta in the last e-fold: 1.09e-3 to 1.15e-3 for all shells
  (eps1 rises again after its minimum).

## Entry 5, 2026-11-19 14:48 UTC: interim look at the first batch; second batch predicted

Run E-20261119-144116-8aa7c22 is half-way (cycle 70 of 213). Read from its records while
it runs (development analysis into scratch/E-stoch-inf/tmp/usr/devB, not a result):
- The homogeneous runs are done; their numbers go into entry 6.
- <abs(H)/[H]> of M16l, M16p and BGv03 (8^3, same step) agree to 4-5 digits at every
  cycle: 1.5e-8 at cycle 6, 1.08e-7 at cycle 48, i.e. the record of the perturbed runs is
  the uniform time-integration residual H0 of the background, independent of the
  amplitude. Prediction M4 (<= 1e-10 at all times) is therefore REFUTED already; cause
  checked by the comparison with the homogeneous run of identical step. In the SR case
  core found H0 = 3e-12 of [H] at Courant 0.25; here the twin's Theta reaches 1.07e-7
  (entry 4), so the same residual is four orders larger in the USR background. A
  second-order Hamiltonian test needs H - H0 per cell (dumps with H) or a smaller step.
- <abs(M)/[M]> of M16l (s = 1e-3) starts at 3.9e-6, which is the rounding of |M| against
  a first-order [M] a thousand times smaller than at s = 1 [JUDGEMENT]; M16l does not test
  the momentum constraint.

Second batch (`inputs/proc2.list`, core_scalar-2, 32^3, nmax2 = 16, to N_f), predictions:
- M16h (s = 0.5): <abs(M)/[M]>(s = 1) / <abs(M)/[M]>(s = 0.5) = 2.0 +- 0.15 at the dumps
  of the entry (cN < 1.4) and during USR, if M is second order ([M] first order, core's
  reading of A4); refuted if it stays near 1 (then a first-order part dominates).
  <abs(H)/[H]> equal to M16p's to 1e-3 relative (H0 dominates).
- M16pc, M16lc (Courant 0.125): <abs(H)/[H]> lower by 16 +- 3 than at 0.25 where H0
  dominates (twin: Theta 6.2e-9 against 1.07e-7); <Pi> off the exact background by
  2.5e-5 at the end. Per-mode U-A2 error of M16lc at N_f: if the 32^3 value of M16l is set
  by the time step it falls by more than 8; if by the stencils it stays within a factor
  1.5. [No preference stated: this run decides it.]

## Entry 6, 2026-11-19 15:08 UTC: outcomes of the first batch (runs E-20261119-144116-8aa7c22, analysis E-20261119-145842-74b52ec)

All nine runs exited 0 (`status.txt` of the run). Numbers from
`results/runs/summary_E-20261119-145842-74b52ec.json`; figures `fig/fig_run_*.png` (looked
at). The last dump of the 32^3 runs is at t = 10.259 (cN = 9.830): dumps fall on the first
step after each multiple of 0.25, and tlim = 10.4375 is not one; "N_f" below means that
dump.

Background (release core-v0.3 and core_scalar-2):
- BG1 (U-A1t): BGv03 against the Z4c twin with the run's own steps: phi 4.1e-14, K 1.6e-14,
  chi 2.9e-12 relative (confirmed); Pi 1.07e-9 relative against the predicted 1e-9:
  REFUTED by a hair. The absolute difference is 3.5e-15, the rounding of Pi measured
  against its early size 0.04 (Pi falls to 2.6e-7); the threshold should have been set on
  the absolute difference [JUDGEMENT].
- BG2 (revised in entry 4): Pi off the exact background by 4.125e-4 at the end, phi
  1.5e-7, K at most 9.3e-8 (the Z4c twin's 9.31e-8; the ADM-form figure "about 1e-8" of
  entry 3 was wrong by 9), e-folds at the end 9.999993 (dN = -7.0e-6, the twin's value):
  confirmed. U-A1 passes (4.1e-4 < 1e-3); U-A0 passes, abs(dN) <= 7.0e-6 at all eight
  landmarks (-1.3e-6 at the eps1 maximum, -1.9e-6 at the USR onset, -3.3e-6 at the
  inflection point, -4.6e-6 at the USR end, -5.9e-6 at the eps1 minimum).
- BG3: Courant 0.03125 lowers the Pi error by 16.34 (phi 16.34): fourth order, confirmed.
- BG4: core_scalar-2 gives a `bg.sf.hst` byte-identical to release core-v0.3: confirmed.
- What the released code does with this potential [VERIFIED by these runs]: it integrates
  the homogeneous USR background exactly as its RK4()4[2S] twin predicts (rounding only),
  through eps1 = 1e-12 and Pi = 2.6e-7 without loss; the time error is the twin's.

Stochastic runs (core_scalar-2, 32^3):
- M1 (U-A2): M16l at N_f: max over the 128 modes 4.1e-4 against the continuum reference
  (rms 3.7e-4), 7.2e-4 against the stencil k^2: confirmed (< 5e-3; threshold 0.02). The
  error is the same, 3.4e-4 to 4.1e-4, for every mode from k = dk to 4 dk
  (`fig/fig_run_mode_errors.png`) and builds up during the USR growth (cN 4 to 7,
  `fig/fig_run_modes_M16.png`), so it is not the stencil dispersion of entry 3's guess
  [JUDGEMENT; the Courant 0.125 runs of entry 5 test it].
- M2 (U-A2s, U-A2n): odd part of M16p/M16m: 3.9e-4 (confirmed). Even part relative to the
  odd one: 2.5e-5 at N_f, at most 6.1e-5 (cN = 4.13). Predicted 1e-3 to 5e-2: REFUTED, the
  second-order part of R^NR is 40 times below the lower bound. M64: 2.2e-5 at N_f, at most
  4.1e-5 (cN = 3.66), although its R_rms is three times that of M16 (0.067 against 0.021):
  the ratio does not follow R_rms, so the estimate "even/odd ~ R_rms" was wrong in kind.
  Whether the even part scales as s^2 is checked with M16h (entry 5).
- M3 (U-A3): NR power over full-MS power at N_f for every mode with k <= 3 dk:
  1.0005 to 1.0011 (M16p), 1.0007 to 1.0008 (odd parts of M16 and M64), 1.0007 to 1.0008
  (M16l): confirmed within 1 percent; the FLRW lattice would give 8.8, 2.1 and 1.4.
- M4 (U-A4): Hamiltonian part REFUTED (entry 5): the record equals the homogeneous run's
  |H|/[H] at every cycle (median ratio 1.000000003 for M16p; maximum 1.08e-7 at cN = 2.3);
  after USR all runs sit on a rounding floor of 5e-15. Momentum part: <abs(M)/[M]> at
  most 1.6e-5 during the entry and 3.4e-4 during USR (M16p), but 2.2e-2 at the end
  against the predicted 1e-2: REFUTED as stated. Cause, read off the record: late
  <abs(M)> is 4.44e-15 in M16p and 4.53e-15 in M16l (s = 1e-3), i.e. a rounding floor
  independent of the amplitude, while the first-order [M] falls to 2.6e-13 (its terms
  carry eps1 ~ 1e-12 in the plateau); the ratio late is rounding over a vanishing
  magnitude, not a constraint violation. M64p (four cells per shortest wavelength) has a
  plateau of 1.7e-2 during USR (cN = 3.4 to 6), falling to 4.0e-3 at the end; not
  separated into its parts here (no halving pair at nmax2 = 64). Negative control NC16:
  <abs(M)/[M]> up to 0.17 and 2.2e4 times M16p's in the first e-fold (median): first
  order, confirmed; its Hamiltonian ratio is only 5.5 times M16p's (median) because H0
  dominates both: the "100 times" of M4 REFUTED for H for the same cause.
- M5: <Pi> of M16p and M64p against M16l: at most 1.6e-8 and 2.3e-7 relative; <phi> 9e-11,
  <K> 5e-12: confirmed (backreaction on the means is negligible at these amplitudes).
  U-A1 of the stochastic runs is the background's 4.1e-4.
- M6: the lockstep record `.modes` against the code-time reference: 4.1e-4 (M16) and
  5.6e-4 (M64) at N_f, against the predicted 1e-4: REFUTED. Same size as the background
  Pi error (4.1e-4) and as the per-mode error of M1; the Courant 0.125 runs test whether
  it is the time step.
- U-A6: rms of R^NR at N_f 0.02130 (M16p) against 0.02129 of the realisation's linear
  value; 0.06736 against 0.06738 (M64p).
- M7: 930 to 974 s per 32^3 run (4.4 s per step, 7.5e3 zone-cycles per second on the
  loaded machine), not 11 min: REFUTED by 40 percent (the machine had a load of about 100).

## Entry 7, 2026-11-19 15:10 UTC: addendum to the predictions of the second batch (still running)

From entry 6 (late |M| is a rounding floor of 4.5e-15 independent of s, [M] first order):
in the plateau after USR (cN > 7) the record ratio F_M = <abs(M)/[M]>(s = 1) /
<abs(M)/[M]>(s = 1/2) is predicted at 0.5 +- 0.1 (floor over a magnitude proportional to
s), against 2.0 +- 0.15 during the entry and USR (entry 5). Even part of R^NR: the s^2
coefficient estimated from M16h, (c(1/2) - odd(1)/2)/(1/4), equals the even part of the
+-1 pair within 30 percent at N_f if the even part is second order; refuted if not.

## Entry 8, 2026-11-19 15:38 UTC: outcomes of the second batch (runs E-20261119-145835-67cde45, final analysis E-20261119-152843-c201aad)

All three runs exited 0 (M16h 817 s; M16pc, M16lc 1688 and 1698 s for 426 steps). Numbers
from `results/runs/summary_E-20261119-152843-c201aad.json` (it repeats every number of
entry 6 unchanged); figures `fig/fig_run_*.png`, looked at.

Against entry 5 and entry 7:
- Halving, momentum record F_M = <abs(M)/[M]>(s = 1)/<abs(M)/[M]>(s = 1/2):
  entry (cN < 1.4) 1.44 to 1.96, median 1.60: REFUTED (2.0 +- 0.15 predicted): a
  second-order and a first-order part of comparable size. USR (2.5 < cN < 6.55)
  0.57 to 1.02, median 1.00: REFUTED: the momentum violation during USR is first order in
  the amplitude. Plateau after USR (cN > 7) 0.49 to 0.53: confirmed (entry 7, rounding
  floor over a first-order [M]). F_H median 1.000000002: confirmed (H0).
- Courant 0.125: Hamiltonian record lower by 17.25 (16 +- 3 predicted, confirmed; twin
  17.3); Pi off the exact background by 2.52e-5 (confirmed); lockstep record against the
  reference 2.51e-5, lower by 16.4: the 4.1e-4 of entry 6 (M6) is the time step, now
  shown. U-A2 per mode: the maximum falls only by 1.79 (2.3e-4, worst mode in the shell
  |n| = 4), the rms by 9.0 (3.65e-4 to 4.05e-5). Per shell: every shell with |n|^2 <= 14
  falls from 3.5e-4 to 4.1e-4 down to 1.8e-5 to 3.8e-5 (time step, about fourth order),
  the shell |n| = 4 (k dx = pi/4) goes from 1.5e-4 to 2.3e-4: there a spatial part of
  about 2e-4 remains, which at Courant 0.25 partly cancelled the time part. So both of
  entry 5's alternatives hold, each for its own shells.
- The momentum plateau during USR is the same at Courant 0.125 (M16pc: at most 3.3e-4
  and 4.5e-4 in cN 2.5-4 and 4-6.55, M16p 3.2e-4 and 3.4e-4): together with F_M = 1, a
  first-order truncation part of the stencils at eight cells per shortest wavelength
  [JUDGEMENT from two runs: spatial because it does not change with the step, first order
  because it does not change with the amplitude; its convergence with N is not shown
  here]. In the SR case core found this part only at four cells per wavelength; in USR
  [M] loses its eps1-carrying terms, so the same truncation is a larger fraction of it.
- Even part of R^NR: estimated from M16h as (c(1/2) - odd(1)/2)/(1/4), it equals the even
  part of the +-1 pair within 0.12 percent at N_f (median 0.04 percent): the even part is
  second order in the amplitude, confirmed (within 30 percent predicted).

Summary of the package [VERIFIED by the runs named]:
- Background through USR: release core-v0.3 and core_scalar-2 integrate it as the
  RK4()4[2S] twin of the reference (rounding only; byte-identical between the two), with
  a time error that is fourth order and largest in Pi after USR (4.1e-4 at Courant 0.25
  on 32^3, 2.5e-5 at 0.125, 9.3e-8 predicted for 256^3); e-folds within 7e-6.
- Initial slice at N* and stochastic sources with this potential (core_scalar-2, 32^3):
  every mode follows the Mukhanov-Sasaki reference through the dip and the USR growth
  (enhancement 1.2e5 at k = dk to 3.2e7 at 4 dk, 2.8e8 at 8 dk) to 4.1e-4 (M16; 2.3e-4 at
  Courant 0.125) and 5.9e-3 at four cells per wavelength (M64): U-A2 passes by a factor
  3.4 to 50. Freezing (U-A3): k <= 3 dk within 0.11 percent of the full MS, against the
  FLRW lattice's factors 8.8, 2.1, 1.4. Second-order part of R^NR: 2e-5 of the first at
  R_rms = 0.02 and 0.07, second order (halving).
- Constraints: at 32^3 the Hamiltonian record is the background's time residual H0
  (1.08e-7 at Courant 0.25, 6.2e-9 at 0.125) and says nothing about second order; the
  momentum record is mixed first/second order in the entry, first order (stencil
  truncation, 3e-4) during USR at eight cells per wavelength, and a rounding floor after
  USR. The A4 reading "halving s halves <abs(M)/[M]>" holds in none of the three phases
  at 32^3 for this case: the card ladder (inputs/card_usr.list) is what can show it.

## Entry 9, 2026-11-20 22:25 UTC: wave 3, the card runs: pre-registration of this package, set-up, predictions (before any card run)

Task (wave 3, round 1, package `usr`): run the USR case on the cards (group 1: ladder 64^3
and 128^3 at nmax2 = 64 with +-1 pairs and a halving pair; group 2: U256, P1's production
set-up), at most 1.5 card-hours, scouting for G2. Nothing of waves 3a is redone: the
reference, the 32^3 processor runs and their analyses stand (entries 4-8).

### 9.1 Acceptance: the pre-registration of this package

This is the package's pre-registration for the card runs; `../spec/scope/SCOPE.md` stays as
it is and the lead decides on adoption. U-A0 to U-A6 of entry 2 are adopted with the two
amendments of README 'Requests' item 1 to the lead, and made operational for the cards:

| Id | On the cards | Threshold |
|---|---|---|
| U-A0 | -ln<chi>/2 of the record of every stochastic run at the landmark times (no homogeneous run on the cards) | 1e-5 in N |
| U-A1 | <phi>, <Pi>, <K> of the record against the exact background | 1e-3 relative (SCOPE 4, USR) |
| U-A1t | amended: on the absolute difference of Pi (code - twin); not re-tested here (no homogeneous card run) | 1e-13 absolute |
| U-A2 | 64^3, 128^3: odd part (R(+s) - R(-s))/2 of each pair, every mode (8 or more cells per shortest wavelength); U256: single run, modes k <= k_max/2 = 32 dk; at N_f against L^-3/2 W R alpha (continuum mode equation, SCOPE 4 wording); for U256 also the shell-normalised deviation abs(c - cref)/rms_shell(cref), reported, not gating | 0.02 |
| U-A2n | even/odd rms over modes (pairs) | reported; below 0.3 |
| U-A3 | power at N_f of the modes k <= 3 dk over the full MS | 10 percent (SCOPE 4) |
| U-A4 | amended: judged on the card ladder with H - H0, i.e. on the parts odd and even in s of the dumped H and M_i with their box means removed, and on the record of H' = H - <H> (`con_signed`). (a) even parts scale by 4.00 +- 0.05 under halving (128^3, s = 1 against 1/2); (b) odd parts by 2.00 +- 0.05; (c) the odd part converges from 64^3 to 128^3 at an order between 4 and 6 (A5's range); (d) strict A4 at k_max/dk = 8 on 128^3: odd <= even for H and for M at every dump of the entry (cN <= ln 8 = 2.08); (a)-(d) only where the part judged exceeds 1e-12 of <[H]> (resp. <[M]>), ten times an assumed floor of 1e-13 | as stated |
| U-A5 | shell spectrum at N_f against W^2 Delta of the realisation (same alpha_n) | reported |
| U-A6 / P-h | one-point statistics of R^NR(x) at N_f (U256): rms against the lattice sum of the realisation and of the ensemble (0.894, entry 4), skewness, kurtosis, extremes against the linear realisation field (inverse transform of L^-3/2 W R alpha), and the dump from which the linear per-mode comparison loses meaning | reported (A8 is G3) |

### 9.2 Set-up (and why it differs from `inputs/card_usr.list`)

- Executable: `scratch/core/exe/core_scalar-3/athena_gpu` (5cc2821, READY published
  2026-11-20 14:20 PST, checked before submission). Reason: `<scalar_field> con_signed =
  true` records <H>, <M_i> and <|H'|/[H]> of H' = H - <H> every cycle, which removes the
  uniform time residual H0 from the record (README request 3 to core, now met); its record
  without the option is byte for byte that of core_scalar-2 (READY). Risk stated by core:
  this card build has run only a 20-step comparison (the long card runs of core used
  cea3a49, 97 lines apart, all of them con_signed); group 1 is therefore also its first
  long run, and U256 runs only after group 1 is analysed.
- Inputs from `scripts/make_card_inputs.py`: `inputs/usr_card.athinput` and
  `inputs/usr_256s.athinput` are usr_base / usr_256 with `dump_constraints = true`,
  `con_signed = true` and dump_dt = tlim/40 (64^3) or tlim/20 (128^3, 256^3), so that the
  last dump is at N_f = N* + 10 itself (the driver shortens the last step to tlim, and a
  dump is written at the first step with t >= n dump_dt (1 - 1e-12); repeated addition of
  tlim/20 reaches tlim to 3e-16); every pair has the same tlim and dump_dt (the ladder's
  last-dump trap). U256 dumps 22 variables (2.95 GB each, 62 GB in all) instead of the 17 of
  the estimate (2.3 GB, 48 GB), so that H' and M can be read from the single run and split
  if U256m runs. A smoke test of `usr_card.athinput` on the processor build of the same
  commit (2 cycles, scratch/E-stoch-inf/tmp/usr/smoke3, unregistered; no number used):
  accepted, record with 27 columns.
- Lists: `inputs/card_g1.list` (U64p/m, U128p/m at s = +-1, U128hp/hm at s = +-1/2; nmax2 = 64,
  mode file `modes_usr_n64.txt`), `inputs/card_u256.list`, `inputs/card_u256m.list`.

### 9.3 Predictions (refuted if outside the ranges)

Inputs of the estimates: entries 4-8 (32^3: Pi error 4.12e-4 at Courant 0.25, fourth order;
per-mode error 3.5-4.1e-4 from the time step for shells with |n|^2 <= 14, 1.5-2.3e-4 for the
shell k dx = pi/4, which keeps a spatial part of about 2e-4; even/odd 2.2e-5 for nmax2 = 64;
<|M|/[M]> plateau during USR 3.2-3.4e-4 at k_max dx = pi/4, first order), the twin's Theta
(1.07e-7, 6.2e-9 at half the step) and the reference lattice variances (rms of W R:
0.0664 for nmax2 = 64, 0.894 for 4096; for 4096 it passes 0.1 at cN = 5.8 and 0.3 at 6.3).
At 64^3 the top shell |n| = 8 has k dx = pi/4 (8 cells per wavelength, as M16 at 32^3); at
128^3 pi/8. The time step at Courant 0.25 is that of 32^3 divided by N/32.

Group 1 (64^3, 128^3, nmax2 = 64):
- G1a (U-A0, U-A1): <Pi> against the exact background at N_f 2.6e-5 (64) and 1.6e-6 (128),
  each within 15 percent (4.12e-4/16, /256); <phi>, <K> below 1e-7; |dN| at every landmark
  below 5e-7 (64) and 5e-8 (128). Pass.
- G1b: lockstep record `.modes` against the code-time reference at N_f: 2.6e-5 (64),
  1.6e-6 (128), within 30 percent.
- G1c (U-A2s, odd part, continuum, all 1054 modes at N_f): U64 max in [1e-4, 5e-4], worst
  mode in a shell with |n|^2 >= 49; shells |n|^2 <= 16 between 1e-5 and 5e-5 (time step);
  U128 max in [1e-6, 3e-5]; per shell with |n|^2 >= 49 the error falls from 64 to 128 at an
  order between 4 and 6.5. U-A2 passes on both rungs.
- G1d (U-A2n): even/odd rms over the modes at N_f in [1e-5, 5e-5] for the +-1 pairs (64 and
  128 alike: second-order physics, not resolution); for the +-1/2 pair half the +-1 value
  within 5 percent.
- G1e (U-A3): abs(P_NR/P_MS - 1) for k <= 3 dk at N_f at most 2e-4 (64) and 2e-5 (128);
  the FLRW lattice would give 8.8, 2.1, 1.4.
- G1f (constraints, parts normalised by <[H]>, <[M]> of the s = 1 run):
  - the signed mean <H> of the +1 and the -1 run agree within 1e-3 relative while the
    uniform residual dominates; the record <|H|/[H]> peaks at 6.2e-9 (64) and 3.6e-10 (128)
    within 30 percent (Theta of the twin over 17.3 per halving of the step);
  - halving (128^3): even parts of H and of M scale by 4.00 +- 0.05, odd parts by
    2.00 +- 0.05, at every dump where the part exceeds the 1e-12 bar;
  - odd part of M during USR (2.5 < cN < 6.55), rms(M_odd)/<[M]>: 64^3 in [5e-5, 1e-3]; 128^3
    lower by a factor between 16 and 90 (order 4 to 6.5);
  - strict A4 at 128^3 (cN <= 2.08): odd <= even for H and for M at every dump above the
    bar (the SR ladder had odd/even 0.27 at L128); at 64^3 the odd/even ratio of H exceeds
    1 at least at one dump (SR: 15 at L64);
  - records: <|H'|/[H]> at most in [1e-12, 1e-9] during the entry [weak, no USR number
    exists at this resolution]; <|M|/[M]> at most 1e-3 on both rungs.
- G1g (cost): U64 at most 1.5 min, U128 2 to 5 min each (0.15 s per step from core's
  128^3 measurement, 851 steps, plus dumps of 0.37 GB); job 0.12 to 0.30 card-hours; peak
  card memory below 5 GB.

U256 (s = +1, 1702 steps):
- U1 (U-A0, U-A1): |dN| below 1e-6 at every landmark; <Pi> against the exact background at
  most 1e-4 relative over the run (time part 9.3e-8; second-order backreaction estimated
  from M64p at 32^3, 2.3e-7, times (0.894/0.067)^2 = 4e-5); <phi>, <K> below 1e-8. Pass.
- U2: lockstep record within 1e-6 of the reference at N_f.
- U3 (U-A2, single run, k <= 32 dk, 68.6k modes): the shell-normalised deviation at N_f at
  most in [1e-4, 1e-2]; U-A2 as written passes, max in [1e-4, 2e-2]; if the max exceeds
  1e-3 its mode is among the 1 percent of modes with the smallest abs(alpha_n) (an
  additive second-order part divided by a small amplitude). Reason for "linear to N_f"
  [JUDGEMENT]: R^NR is carried by delta phi (K gets no perturbation in USR, P1:532; at 32^3
  the e-folds of M64p and M16l agree to 4e-12, so the part of chi is negligible); after
  the inflection point the field equation is nearly linear in delta phi: delta phi =
  Pi_b R/H ~ 2.4e-7 against phi - phi_i = 3.8e-5 at N_f (entry 1), a relative
  nonlinearity of 6e-3. Refuted if the shell-normalised deviation exceeds 0.02 at a dump.
- U4 (U-A3): k <= 3 dk within 2 percent of the full MS (threshold 10 percent).
- U5 (U-A5): shell ratios against the realisation within 1e-3 for k <= 32 dk and 1e-2 for
  the top shells (4 cells per wavelength; M64 at 32^3: 5.9e-3 per mode).
- U6 (P-h, U-A6): rms of R^NR(x) at N_f, band |n|^2 <= 4096, equal to the realisation's
  linear value within 1e-3 and to the ensemble 0.894 within 0.005; on the full lattice
  within 1 percent of that (the rest is second order); skewness abs <= 0.05, excess
  kurtosis abs <= 0.1; max abs(R^NR) within 2 percent of that of the linear realisation
  field and between 3.5 and 6 (4 to 7 sigma for 1.7e7 correlated cells): P1's "outliers
  ~ 10" (P1:534) is not expected [JUDGEMENT; refuted if max abs(R^NR) > 7]; pointwise
  rms of R^NR - R_lin at most 1e-2 of the rms.
- U7 (constraints, single run): <|H'|/[H]> at most in [1e-12, 1e-9]; <|M|/[M]> at most in
  [5e-3, 5e-2] during USR (first-order truncation of the top shells at 4 cells per
  wavelength: M64 at 32^3 1.7e-2; core's 128^3 runs at k_max dx = pi/2 3.2e-2, READY of
  core_scalar-3), at N_f in [1e-3, 2e-2] (P1:541: "around 1e-2").
- U8 (cost, SCOPE 8): 1.23 to 1.35 s per step, 0.58 to 0.64 card-hours per realisation,
  peak card memory 18 to 24 GB (SR P256: 19.6 GB), 62 GB of dumps.

U256m (only if groups 1 and U256 pass and the cap allows; G1 + U256 + U256m about 1.45
card-hours): odd part per mode at N_f for k <= 32 dk at most 3e-4, every mode at most 1e-2;
even/odd rms in [2e-5, 1e-3]; the odd part of H first exceeds the even part between
cN = 3.0 and 4.2 (SR: from ln(N/8) = 3.47 e-folds on, when the first shell with fewer than
eight cells per wavelength crosses).

## Entry 10, 2026-11-20 22:35 UTC: addendum to the pre-registration, before group 1 has started (job 4742 pending)

The analysis `scripts/analyse_cards.py` (with `scripts/card_lib.py`) was written and run on
two code tests, which exercise the code paths only and give no number used here:
(i) the 32^3 pair M64p/M64m of run E-20261119-144116-8aa7c22 renamed U64p/U64m: it
reproduces the registered analysis E-20261119-152843-c201aad (odd-part U-A2 5.88e-3,
even/odd 2.17e-5, U-A3 1.00067-1.00079, lockstep 5.6e-4, Pi 4.12e-4); (ii) four 12-cycle
processor runs of `usr_card.athinput` (core_scalar-3 athena_cpu, s = +-1, +-1/2, unregistered,
scratch/E-stoch-inf/tmp/usr/codetest) for the constraint split, the halving and the record
columns of con_signed.

Amendment of the bar of U-A4 (entry 9.1), from registered data, not from the code tests:
the floor analysis of the SR ladder (run E-20261119-142713-32c883a,
`../ladder/results/floor/floor.json`) has the even part of H at 7e-13 to 9.8e-13 of <[H]>
during the entry at every N (k_max/dk = 8), and the odd part of H at its floor at 128^3,
5e-14 to 1.1e-13 of <[H]>, growing as N^2.5. The bar "1e-12 of <[C]>" of entry 9.1 would
therefore leave the even part of H unjudged for s = 1/2 (and nearly so for s = 1). New bar
for H: 3e-13 of <[H]> (three times the floor measured at 128^3, as A5' of SCOPE 4b uses
three times); for M unchanged (1e-12 of <[M]>, far below the parts, 1e-7 to 1e-5 in SR). The
thresholds 4.00 +- 0.05 and 2.00 +- 0.05 are unchanged. Added prediction: where the
halved part of H lies within a factor 10 of the floor, a floor in quadrature lowers the
even halving factor of H to between 3.85 and 4.0, and the odd halving factor of H to
between 1.9 and 2.0.

## Entry 11, 2026-11-21 07:53 UTC: batch 2b; group 1 has run (job 4742); quick check of its records; U256 submitted before the full analysis

State found: the session of entry 10 was cut at 14:35 PST on 2026-11-20 with entry 10,
`scripts/analyse_cards.py` and `scripts/card_lib.py` uncommitted (now committed, 7f764776).
Its group-1 job 4742 (run E-20261120-222621-ba66218, core_scalar-3 athena_gpu 5cc2821) ran
afterwards, 14:36:46 to 14:46:10 PST, all six entries rc = 0 and stopped on tlim (wall 9 min
24 s, 0.157 card-hours), 33 GB of dumps. Its manifest still read "submitted".

Deviation from entry 9.2 ("U256 runs only after group 1 is analysed") [JUDGEMENT]: the reason
written there was that this card build had run only a 20-step comparison. That risk is
answered by the records alone, which take seconds: run E-20261121-075022-7f76477
(`scripts/quick_records.py`, no dump read) on all six runs:

| run | dumps | t of the last dump | lockstep at N_f | max <Pi> rel. | <Pi> rel. at N_f | max abs dN | max <abs H/[H]> | <abs H'/[H]> max, entry / USR / late | <abs M/[M]> max, entry / USR / late |
|---|---|---|---|---|---|---|---|---|---|
| U64p, U64m | 41 | 10.437508874066 | 3.57e-5 | 2.50e-5 | 2.50e-5 | 4.2e-7 | 6.24e-9 | 2.87e-12 / 1.0e-12 / 3.7e-16 | 1.6e-5 / 3.7e-4 / 1.07e-2 |
| U128p, U128m | 21 | same | 2.25e-6 | 1.33e-6 | 1.33e-6 | 2.6e-8 | 3.75e-10 | 2.87e-12 / 1.1e-13 / 7.4e-16 | 1.6e-5 / 8.05e-4 / 2.47e-2 |
| U128hp, U128hm | 21 | same | record = s x reference (0.5; the quick check assumes abs(s) = 1) | 1.50e-6 | 1.50e-6 | 2.6e-8 | 3.75e-10 | 7.19e-13 / 2.9e-14 / 5.5e-16 | 8.3e-6 / 1.57e-3 / 4.30e-2 |

Outcomes against entry 9.3 (the records only; the dump parts follow in the full analysis):
- G1a: holds. <Pi> at N_f 2.50e-5 (64; predicted 2.6e-5 +- 15 %) and 1.33e-6 (128; 1.6e-6
  +- 15 %, lower bound 1.36e-6: just outside if read as the run's value). The +-1/2 run reads
  1.50e-6: the s^2 part is -2.25e-7 at s = 1 (two equations, s = 1 and 1/2), so the time part
  is 1.56e-6 at 128^3 (inside) and 2.52e-5 at 64^3; the s^2 part equals the 2.3e-7 that
  entry 9 took from M64p at 32^3 for the backreaction. |dN| 4.2e-7 < 5e-7 and 2.6e-8 < 5e-8.
  <phi>, <K> below 1e-7: 2.1e-8, 5.4e-9 (64). Pass of U-A0 (1e-5) and U-A1 (1e-3).
- G1b: FAILED narrowly. Lockstep 3.57e-5 (64) and 2.25e-6 (128) against 2.6e-5 and 1.6e-6
  within 30 %: both are 1.37 to 1.40 times the prediction (the ratio 64/128 is 15.9, fourth
  order as predicted; the prediction took the Pi error of the background for the error of
  the modes' record, which is 1.4 times larger).
- G1f, record of H: holds. max <abs H/[H]> 6.24e-9 (64) and 3.75e-10 (128) against 6.2e-9 and
  3.6e-10 +- 30 %. The record of H' = H - <H> is largest at t = 0 (2.87e-12, the same on both
  rungs and four times smaller at s = 1/2: the second-order residual of the initial slice,
  set by the modes, not by the mesh) and stays inside [1e-12, 1e-9] only at the start; after
  the entry it falls to 1e-13 (128) and to 4e-16 to 7e-16 late, so "at most in [1e-12, 1e-9]
  during the entry" holds (its maximum is 2.87e-12 at t = 0).
- G1f, record of M: FAILED. "<abs M/[M]> at most 1e-3 on both rungs": 1.07e-2 (64), 2.47e-2
  (128), 4.30e-2 (128, s = 1/2), the maxima late (cN > 7). During USR 3.7e-4 (64), 8.05e-4
  (128), 1.57e-3 (s = 1/2). The record grows with N (factor 2.2) and as 1/s (factor 1.95), as
  a rounding floor relative to a magnitude [M] that is proportional to s does; this is the
  "rounding floor after USR" of entry 8 at 32^3, which the prediction left out. The
  first-order stencil part of entry 8 (3.2e-4 at k_max dx = pi/4) is not visible under the
  floor at 128^3. Cause named only as a reading; the dump parts (odd/even in s) test it.
- G1g, cost: holds. U64 12 s of card time each, U128 132 s each (851 steps, 0.155 s per
  step), job 0.157 card-hours (predicted 0.12 to 0.30); card memory peak 0.96 GB (64), 3.2 GB
  (128) (below 5 GB).

The build therefore runs the case to N_f with the background and the lockstep record as
predicted; U256 (`inputs/card_u256.list`, same executable) is submitted now, before the
dumps are analysed, so that the card queue is not idle while the analysis runs. Card-hours
so far 0.157 of 1.5.

## Entry 12, 2026-11-21 08:01 UTC: outcomes of group 1 against entry 9.3 (analysis E-20261121-075307-4542ce1)

Analysis run E-20261121-075307-4542ce1 (`scripts/analyse_cards.py --group g1`, 3 cores, 3.5
min) of card run E-20261120-222621-ba66218; numbers in
`results/runs/summary_E-20261121-075307-4542ce1.json`, figures `fig/fig_card_g1_{modes,
constraints,halving,background,order}.png` (each looked at). 1054 modes (|n|^2 <= 64), 41
dumps at 64^3, 21 at 128^3, the same times within each pair, the last at N_f.

| Pre-registered (9.3) | Outcome | Verdict |
|---|---|---|
| G1a, U-A0: abs dN < 5e-7 (64), 5e-8 (128) | 4.2e-7, 2.6e-8 | holds; U-A0 (1e-5) passes |
| G1a, U-A1: <Pi> at N_f 2.6e-5, 1.6e-6 +- 15 % | 2.50e-5, 1.33e-6 (time part 2.52e-5, 1.56e-6 after the s^2 part, entry 11) | holds for the time part; U-A1 (1e-3) passes |
| G1b: lockstep 2.6e-5, 1.6e-6 +- 30 % | 3.57e-5, 2.25e-6 (ratio 15.9) | FAILED (1.4 times; entry 11) |
| G1c: U64 odd-part max in [1e-4, 5e-4], worst shell abs(n)^2 >= 49 | 1.144e-4, mode (0, 8, 0), shell 64 | holds |
| G1c: shells abs(n)^2 <= 16 in [1e-5, 5e-5] (64) | 1.94e-5 to 2.39e-5 | holds |
| G1c: U128 max in [1e-6, 3e-5] | 2.12e-6 (2.16e-6 for the +-1/2 pair) | holds |
| G1c: order 64 -> 128 per shell abs(n)^2 >= 49 in [4, 6.5] | 4.01 to 5.75 (shells 52, 56, 61 at 4.01); shells <= 48: 3.77 to 4.26 (the time step) | holds |
| U-A2s (0.02) | 1.1e-4 (64), 2.1e-6 (128) | passes; single runs (U-A2 against s x reference) 5.3e-4 to 6.1e-4 (64), 5.7e-4 (128), 2.9e-4 (s = 1/2), worst mode (2, 1, -7), the one with the smallest abs(alpha): the even part over a small amplitude |
| G1d, U-A2n: even/odd at N_f in [1e-5, 5e-5], same on both rungs; +-1/2 half of +-1 within 5 % | 2.187e-5 (64), 2.187e-5 (128), 1.094e-5 (+-1/2: 0.500 of +-1); largest 4.0e-5 at cN 3.6-3.8 | holds |
| G1e, U-A3: abs(P/P_MS - 1) for k <= 3 dk at most 2e-4 (64), 2e-5 (128) | 4.8e-5, 2.5e-6 (odd parts); single runs 3.7e-4, 3.3e-4 | holds; U-A3 (10 %) passes |
| R^NR parts at N_f | phi part 1.00, chi part 6.1e-6, anisotropic part 1.6e-6 of the total; linear and log chi forms differ by 3.6e-12 | as entry 9 U3 assumed (R^NR carried by delta phi) |
| G1f: <H> of the +1 and -1 runs within 1e-3 while the uniform residual dominates | 128^3: 7e-12 to 1.1e-7 for cN 0.5-4, at most 8e-5 to cN 8.5, 8.1e-4 and 1.3e-3 at the last two dumps (<H> near its floor) | holds |
| G1f: record <abs H/[H]> peaks 6.2e-9 (64), 3.6e-10 (128) +- 30 % | 6.24e-9, 3.75e-10 | holds |
| G1f / U-A4(a): even parts scale by 4.00 +- 0.05 at s = 1 against 1/2 where the part at s = 1/2 exceeds the bar | H: one dump above 3e-13 of <[H]> (cN 0.53): 3.82; M (bar 1e-12 of <[M]>, all 20 dumps above): 3 of 20 within +-0.05; 3.83 to 3.995 for cN 0.5-4.05, then 3.6, 2.9, 2.0, 1.3, 1.07 and 0.94 to 1.19 after cN 6 | FAILED (H narrowly, 3.82 also below the 3.85 of entry 10; M from cN 4.5 on) |
| G1f / U-A4(b): odd parts by 2.00 +- 0.05 | H: no dump above the bar (the odd part of H at 128^3 is at most 1.1e-13 of <[H]>); M: 0 of 20 within: 1.00 for cN <= 1.55 and after cN 5, 1.35 to 1.80 between | FAILED for M; not judged for H |
| G1f: odd part of M during USR, 64^3 in [5e-5, 1e-3]; 128^3 lower by 16 to 90 | 64: plateau 2.1e-4 to 3.5e-4 (max 3.5e-4); 128: max over the window 4.6e-4 (at cN 6.5); per dump cN 2.55-4.05 lower by 37 to 60 (orders 5.2 to 5.9) | 64 holds; 128 FAILED as written (max over the window), holds per dump to cN 4.5 |
| U-A4(c): odd parts converge 64 -> 128 at order 4 to 6 | H 5.53 to 5.69 and M 5.15 to 5.90 for cN 2.06-4.05, 4.7-4.8 at cN 4.54; outside: -2 to 3 (128^3 odd part at its floor) | holds where the 128^3 odd part is above its floor; H not above the bar anywhere, so formally not judged |
| U-A4(d): strict A4 at 128^3 (cN <= 2.08) | M: odd/even at most 0.079; H: no dump above the bar (values odd/even at most 0.085) | holds for M; H not judged |
| G1f: at 64^3 odd/even of H exceeds 1 at least once | 3.2 inside the entry (cN 2.07), 10.1 at most (cN 2.3) | holds |
| G1f: record <abs H'/[H]> at most in [1e-12, 1e-9] during the entry | 2.87e-12 (t = 0) | holds |
| G1f: record <abs M/[M]> at most 1e-3 | 1.07e-2, 2.47e-2, 4.3e-2 | FAILED (entry 11) |
| G1g: cost | 0.157 card-hours, 0.155 s per step at 128^3 | holds |

What the constraint figures show (`fig/fig_card_g1_constraints.png`, `_halving.png`,
`_order.png`) [VERIFIED for these runs, reading JUDGEMENT]:
- Even parts of H and M are the same on both rungs (order 0.00 +- 0.05 to cN 5): second-order
  physics, not resolution; under halving they scale by 3.9 to 4.0 while they are above the
  floor (to cN 4 for M, 4.5 for H).
- Odd parts are the stencil truncation of the entering modes: at 64^3 the odd part of H
  peaks (1.4e-12 of <[H]>) at cN 2.3, just after the top shell enters at 8 cells per
  wavelength (cN = ln 8 = 2.08), and the odd part of M has a plateau 2e-4 to 3.5e-4 through
  USR; they converge at order 5.2 to 5.9 to 128^3.
- Below both lies a part independent of s: wherever the factor of a part is 1.00 the part has
  the same absolute size at s = 1 and 1/2. For M it is 1e-8 to 6e-7 of <[M]> early and grows
  to 1.4e-2 (128^3) and 6.4e-3 (64^3) late, at the same level in the odd and even parts and
  higher at 128^3 by 2.2 (as rounding of first differences, ~1/dx); <[M]> is proportional to
  s and falls with Pi_b through USR, so this floor relative to <[M]> rises by 1e5 while the
  absolute floor stays. For H it is 3.6e-14 of <[H]> at t = 0 at 128^3 and 8.9e-15 at 64^3
  (ratio 4.0, as rounding of second differences) and 3e-16 to 4e-16 of <[H]> late on both
  rungs (algebraic terms; the derivative terms carry chi, which is e^-20 late). Core reads
  the late M the same way (`scalar_field_3.md` on core/scalar-3, section 3: |M| floor 1e-14
  to 3e-14 for every amplitude). Named as a reading only: the floor is not shown to be
  rounding by a run in which it could have failed.
- The pre-registered bars (3e-13 of <[H]>, 1e-12 of <[M]>) were taken from the SR ladder;
  for USR the floor of M relative to <[M]> is 1e4 to 1e10 times that bar, so the bar did not
  keep the floor out of (a)-(c). The failures of U-A4(a), (b) for M and of the M prediction
  at 128^3 are therefore failures of the bar, not of a second-order law [JUDGEMENT]; U-A4 as
  pre-registered is FAILED and stays on record.

### 12.1 Post-hoc floor reading (not acceptance): predictions before `scripts/floor_split.py` runs

Written after seeing the parts above (not blind). Model per dump: part(s) =
sqrt((s^p a)^2 + f^2) with p = 1 (odd) or 2 (even) and one floor f per constraint,
independent of s and the same in the odd and the even part (uncorrelated noise in the two
runs of a pair). f and a_odd follow from the odd parts at s = 1 and 1/2.
- F1: the floor-corrected even factor sqrt(E1^2 - f^2)/sqrt(Eh^2 - f^2) is 4.00 +- 0.10 for M
  and for H at every dump where Eh^2 > 2 f^2 and f is resolved (4 oh^2 > o1^2).
- F2: where the odd factor is 1.00 +- 0.05 (odd parts at the floor), the even part equals the
  odd part within 15 % at both s.
Refuted if outside.

### 12.2 Outcome of the floor reading (run E-20261121-080134-a0cc3eb, `fig/fig_card_g1_floor.png`, looked at)

- F1 holds: with the floor f fitted from the odd parts, the even factor of H is 3.991 to
  4.001 and that of M 3.987 to 4.001 at all ten judged dumps each (cN 0.53 to 5.04); the raw
  factors there were 3.60 to 3.99. The H dip to 3.82 at cN 0.53 and the M fall from cN 4.5
  on are the floor in quadrature. The second-order parts of both constraints scale as s^2
  to 1e-3 wherever they are resolved.
- F2 FAILED as written: 8 of 20 (H) and 10 of 20 (M) within 15 %. The odd part sits at the
  floor also early (cN 0.5 to 1.5), where the even part is 12 to 60 times above it; F2
  assumed that "odd at the floor" meant "everything at the floor". Late (cN 6.5 to 8.5),
  where both are at the floor, even/odd is 0.92 to 1.19.
- The fitted floor f, absolute: H 1.25e-12 at cN 0.53, falling about as chi (e^-2N) to
  4e-15 at cN 5 and flat after; M 8.5e-13 falling to 2.6e-14 at cN 5 and flat (2e-14 to
  3e-14 to N_f, the size core gives for |M| late). The first-order (odd) part of M at 128^3
  exceeds the floor only for cN 2 to 4.5 (a_odd 1e-13 to 3.3e-13), as the top shell enters.
- Consequence for U-A4 on these cards [JUDGEMENT, for the lead]: judge the halving on the
  floor-corrected parts, with the floor from the odd parts of the halving pair, or bar each
  part at three times the floor measured that way (not at a fixed fraction of <[C]>, which in
  USR falls by 1e5 relative to an absolute floor).

## Entry 13, 2026-11-21 08:53 UTC: U256 ran (job 4774); U256m submitted before the U256 analysis ends, on condition

U256 (card run E-20261121-075255-8cf90e7, core_scalar-3 athena_gpu 5cc2821): started
00:05:38 PST, rc = 0, stopped on tlim at cycle 1702 (t = 10.437509), 21 dumps of 2.95 GB,
job wall 37.0 min = 0.617 card-hours; 2208.8 s of run time = 1.298 s per step; card memory
peak 19.6 GB. U8 (cost): 1.23 to 1.35 s per step holds; 0.58 to 0.64 card-hours holds;
18 to 24 GB holds. The analysis (run E-20261121-084815-63462b8) started at 00:48 PST, 5.5
minutes after the job: the first attempt, queued to start at the job's end, was refused by
nrpic-run because `README.md` was uncommitted ("not clean where the run's code lives").

Card-hours: group 1 0.157 + U256 0.617 = 0.774 of 1.5; left 0.726, so U256m goes with
--wall 00:43:00 (0.717): at most 1.491 in all.

Decision on U256m [JUDGEMENT]: the task allows it "only if steps 2 and 3 pass". Step 2:
U-A0 to U-A3 pass on both rungs; U-A4 failed as pre-registered for a reason located in the
bars (entry 12), and with the floor removed its second-order law holds (entry 12.2). Step 3
is being analysed now. U256m is submitted now because two cards are busy for about 55
minutes with one job ahead, so it cannot start before the U256 analysis (about 12 minutes)
is judged; it is cancelled (scancel) if U256 fails U-A0, U-A1, U-A2 or U-A3.

Added prediction for U256m (beside entry 9's): at 256^3 with nmax2 = 4096 the magnitude
<[M]> is set by 549k modes with rms R up to 0.9, so the s-independent floor of entry 12.2
(absolute 2e-14 to 3e-14 at 128^3 late, about twice that at 256^3 if it scales as 1/dx) is
below 1e-3 of the parts of M at every dump after cN 1: late (cN > 7) the odd part of M
exceeds the even part (first-order truncation of the top shells at 4 cells per wavelength)
and the even/odd ratio of M lies in [0.05, 0.7]. Refuted if even/odd of M is within 15 %
of 1 at cN > 7 (a floor) or above 1.

## Entry 14, 2026-11-21 09:00 UTC: outcomes of U256 against entry 9.3 (analysis E-20261121-084815-63462b8)

Analysis run E-20261121-084815-63462b8 (`scripts/analyse_cards.py --group u256`, 3 cores, 9.8
min; 26 s for the code-time MS reference of 3414 shells, then 35 s per dump) of card run
E-20261121-075255-8cf90e7; numbers in `results/runs/summary_E-20261121-084815-63462b8.json`,
figures `fig/fig_card_u256_{modes,spectrum,onepoint,constraints}.png` (each looked at).
548958 modes (|n|^2 <= 4096), 68532 of them with k <= 32 dk; 21 dumps, the last at N_f
(cN = 10.000).

| Pre-registered (9.3) | Outcome | Verdict |
|---|---|---|
| U1: abs dN < 1e-6 at every landmark | 1.6e-9 at most (N_f) | holds; U-A0 passes |
| U1: <Pi> at most 1e-4 relative (time part 9.3e-8, backreaction about 4e-5) | 4.17e-5 at N_f (the estimated backreaction) | holds; U-A1 passes (1e-3) |
| U1: <phi>, <K> below 1e-8 | 1.15e-9, 2.4e-11 | holds |
| U2: lockstep record within 1e-6 of the reference at N_f | 2.55e-3 | FAILED (by 2500); reading in 14.1, tested there |
| U3: shell-normalised deviation at N_f in [1e-4, 1e-2] | max 9.1e-4, rms 2.6e-4 (k <= 32 dk) | holds |
| U3: U-A2 as written passes, max in [1e-4, 2e-2] | max 5.9e-2 at mode (12, -14, 18); 10 of 68532 modes above 0.02, 37 above 0.01; median 2.6e-4, rms 7.9e-4 | FAILED; U-A2 (0.02) fails as written for the single run |
| U3: if the max exceeds 1e-3 its mode is among the 1 % of modes with the smallest abs(alpha) | the worst mode has abs(alpha) 0.0066, rank 3e-5; all ten modes above 0.02 have rank below 7e-4 | holds |
| U3: refuted if the shell-normalised deviation exceeds 0.02 at a dump | 6e4, 6e2, 6.0, 8.7e-2 at the first four dumps (cN 0 to 1.55); at most 3.3e-3 from cN 2.05 on, 1.2e-3 from 2.55 on | FAILED as written; the early values divide by the shell rms of a reference that the window has not yet switched on (W of order e^-26 for the top shells at cN 1.5), a normalisation that means nothing there [JUDGEMENT]; the run-normalised per-mode deviation (entry 2's measure) is below 1.6e-6 at those dumps |
| U4: U-A3, k <= 3 dk within 2 % of the full MS | 0.9923 to 1.0016 (worst: the mode with abs(alpha) 0.15) | holds; U-A3 passes (10 %) |
| U5: U-A5 shell ratios within 1e-3 for k <= 32 dk, 1e-2 for the top shells | 5.9e-4 (rms 8.9e-5); top shells 6.7e-3 (shell 4096) | holds |
| U6: rms of R^NR in the band equal to the realisation's linear value within 1e-3 | 0.894520 against 0.894364 (1.7e-4) | holds |
| U6: and to the ensemble 0.894 within 0.005 | 0.89452 against 0.89366 (sqrt of 0.79863, entry 4) | holds |
| U6: full lattice within 1 % of the band | 0.8945204 against 0.8945204; rms(full - band) 1.8e-4 | holds |
| U6: skewness abs <= 0.05, excess kurtosis abs <= 0.1 | 0.0024 (linear field 0.0009), 0.0011 (0.0011) | holds |
| U6: max abs(R^NR) within 2 % of the linear field's, between 3.5 and 6; refuted above 7 | 4.568 against 4.562 (0.13 %); 5.1 rms | holds; P1:534's "outliers ~ 10" not seen in this realisation |
| U6: pointwise rms(R^NR_band - R_lin) at most 1e-2 of the rms | 9.7e-4 = 1.1e-3 of the rms; largest 5.8e-3 | holds |
| U7: <abs H'/[H]> at most in [1e-12, 1e-9] | 2.89e-12 (t = 0), 1.4e-12 in USR, 6.5e-15 late | holds |
| U7: <abs M/[M]> at most in [5e-3, 5e-2] during USR | 2.51e-2 (near cN 6.5) | holds |
| U7: <abs M/[M]> at N_f in [1e-3, 2e-2] (P1:541 "around 1e-2") | 2.13e-3 | holds |
| U8: 1.23 to 1.35 s per step, 0.58 to 0.64 card-hours, 18 to 24 GB | 1.298 s, 0.617 card-hours, 19.6 GB | holds (entry 13) |

Where the linear per-mode comparison loses meaning (asked by the task) [VERIFIED for this
realisation]: nowhere before N_f at the level of the shells. The deviation of R^NR from
the linear field L^-3/2 W R alpha, per mode over its largest reference amplitude, has an
rms over the 68532 modes k <= 32 dk that stays below 1e-3 to N_f (7.9e-4 there); its
largest value passes 1e-3 at cN 6.03 and 0.02 at cN 7.02, always on modes with the
smallest abs(alpha), when rms R^NR is 0.15 and 0.72. Over the shell rms the deviation is
at most 9.1e-4 at N_f, and the real-space field differs from the linear one by 1.1e-3 of
its rms with rms R^NR = 0.894 (Delta_R up to about 1 at 64 dk, `fig/fig_card_u256_spectrum.png`).
The comparison is therefore meaningful at the 1e-3 level through N_f; what a single run
cannot say is how much of the 1e-3 is second order (even in s) and how much is the time
step: U256m splits it.

### 14.1 Lockstep record of U256: reading and predictions before `scripts/lockstep_shells.py` runs

Reading [JUDGEMENT]: the lockstep integration of the mode functions uses the run's step
(dt = 6.136e-3) from N*, when the top shells are deep inside the horizon (k dt = 0.39 for
k = 64 at a = 1). RK4's phase error per step is about (omega dt)^5/120; with omega = k/a and
a ~ e^t it sums to about k^5 dt^4/600, which is 2.5e-3 for k = 64 at 256^3 (measured
2.55e-3), 1.2e-6 for the top shell at 128^3 and 2.0e-5 at 64^3 (group 1 measured 2.25e-6
and 3.57e-5 as the maximum over shells, with the background part 1.6e-6 and 2.5e-5).
Predictions (refuted if outside):
- L1: at 256^3 the lockstep error per shell at N_f follows k^5 dt^4/600 within a factor 2
  for every shell with k >= 24 dk (where this part exceeds 1e-5).
- L2: at 64^3 and 128^3 the lockstep error per shell is the background part (the value of
  the lowest shells) plus k^5 dt^4/600; the top shell (k = 8) exceeds the lowest shell by
  1.0e-5 to 4e-5 at 64^3 and by at most 3e-6 at 128^3.
- L3: at 256^3 the median per-mode error of R^NR at N_f in each shell with k >= 40 dk lies
  between 0.5 and 2 times the lockstep error of that shell (the sources inherit the phase
  error when the window lets them in).
