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

## Entry 1, 2026-11-19 14:50 UTC: reference written; development pass (unregistered)

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

## Entry 2, 2026-11-19 15:00 UTC: acceptance of the USR case (proposal to the owner)

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

## Entry 3, 2026-11-19 15:05 UTC: predictions for the registered runs (before they run)

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
