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
