# Journal of repro/verify (fresh verifier of the reproduction of arXiv:2401.08530 and arXiv:2512.14649)

P0 = arXiv:2401.08530 (`kb-data/raw/arxiv/2401.08530/v2/src/Stochastic_Inflation.tex`),
P1 = arXiv:2512.14649 (`kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`). Line numbers are
those of these files.

## Entry 1, 2026-11-24 10:15 PST: what was read, predictions before any computation

Read so far: CLAUDE.md, CHARTER (to "Owners"), decisions 0010, 0028, 0032; P0:782-881 and
P0:1034-1076 (one-patch Langevin system, appendix D); P1:395-543, P1:697-791; the paper's
own figures of P0 (plot2v2.png, plot2bv2.png, plot4v2.png, looked at); the interface texts
`coord/INTERFACES/scalar_field_2.md` (dump layout NRSFDMP2, mode file, record columns) and
the input deck of the USR run. From the reproduction I took ONLY the list of claims (the
ledger `repro/note/manuscript/tables/ledger.csv`, column "quantity" and "value", and the
ERRATA table's first three columns) and the locations of raw outputs (run directories under
`scratch/E-stoch-inf/`). I did not read any README verdict, RESULTS.md, the note's text or a
journal of the other packages.

My own reading of P0's figures (no file is committed from it; single values only):
P0 Fig. 3 (plot4v2.png) shows dashed Gaussians "with the same first two moments"; their peak
heights give the standard deviations sigma = 1/(sqrt(2 pi) peak):
alpha - alpha_b at N_b = 3, 4, 5, 6: peaks 59, 3.4, 3.0, 3.28 -> sigma 0.0068, 0.117, 0.133, 0.122;
N - N_b: peaks 248, 9.4, 2.65, 2.12 -> sigma 0.0016, 0.042, 0.150, 0.188.
P0 Fig. 2 (plot2bv2.png): kappa3(alpha) rises to about 1.1 at N_b = 4.2 and stays near 1.1 to
6; kappa4(alpha) about 3 (noisy, spikes to 8); kappa3(N) and kappa4(N) peak near 0.6 and 0.8
at N_b = 4.3-4.4 and decay to about 0.3 and 0.2 at 6. P0 Fig. 1 (plot2v2.png): mean of
N - N_b over 100 paths stays within about 0.03 of zero; the paths' alpha - alpha_b reaches
-0.25 at the low side, +1 at the high side (right skew).

Analytic estimate before any code (P1 of this journal): on the plateau the e-fold
Klein-Gordon equation is pi' = -(3 - pi^2/2) pi (pi = dphi/dN, M_Pl = 1), so the field moves
by Delta phi = (1/sqrt 6) ln[(sqrt 6 + |pi*|)/(sqrt 6 - |pi*|)] = 0.93599 for pi* = -2.0001;
from phi* = 10 it stops at 9.06401, above phi_c = 9.056 (P0:847): the exact background never
reaches the slope.

Predictions (each with what would refute it):

V1 (P0 background). (a) An accurate integration (RK45, rtol 1e-12) stops on the plateau at
phi = 9.0640 +- 1e-4; refuted if it crosses phi_c. (b) Forward Euler with 0.01 e-folds
crosses phi_c, at N between 2.9 and 3.2 (P0:842 prints "slope reached at ~3.04"); refuted if
it stays on the plateau. (c) Forward Euler at 0.005 stays on the plateau (error halves:
phi_stop about 9.060); a second-order scheme (Heun) at 0.01 stays on the plateau. Refuted
if Euler 0.005 or Heun 0.01 cross.

V2 (Ito against Stratonovich reading of P0 eq. (eqUniFieldlapse), noise as printed, alpha^3
multiplier, Ito term alpha^3 <S^2>, background of V1(b), 50 000 paths, step 0.01, noise on
from N_b = 2 to 6). Prediction: the Ito (Euler-Maruyama) reading reproduces my read-off
widths of P0 Fig. 3 within 10 per cent at N_b = 4, 5, 6 for both alpha and N, and the
skewness of alpha near 1.1; the Stratonovich reading (extra drift (3/2) alpha^5 S^2) gives
widths larger by more than 15 per cent at N_b = 6, skewness above 1.4 and a mean of N - N_b
above 0.05 at N_b = 6 (outside the 100-path red curve of P0 Fig. 1 by more than 2 standard
errors). Refuted if Stratonovich matches the read-off widths better than Ito at two of the
three times. Firmness: widths read off a KDE figure carry about 5 per cent; I will call the
decision firm only if the two readings differ by more than three times that.

V3 (Ito term). Ito's lemma for alpha = phidot_b/Z with dZ = ... + alpha S_Pi dW gives the
drift alpha^5 <S_Pi^2>/phidot_b^2, not the printed alpha^3 (P0:817). A Monte Carlo of the
pure-noise process at alpha0 = 2 and 1.5 measures the drift within 3 standard errors of
alpha^5 and more than 10 standard errors from alpha^3. Refuted otherwise.

V4 (appendix D amplitude). With R_k = A(1 + i k tau) e^(-i k tau), A ~ 1/sqrt(eps1):
SR (A constant): |bracket|/|printed bracket| = sqrt(1 + sigma^2/3 + sigma^4/9) (1.0017 at
sigma = 0.1); USR (A ~ a^3): bracket = -A sigma^2 e^(-ik tau), ratio sigma^2/3 (3.3e-3 at
0.1, 8.3e-2 at 0.5). My numerical solution of the Mukhanov-Sasaki equation on real
backgrounds (P0's plateau in USR; a slow-roll background) agrees with these within 10 per
cent in USR (where eps2 is within 0.1 of 6) and within 5 per cent in SR. Refuted if the USR
amplitude is of order one of the printed one.

V5 (P1 lattice, 256^3, from the raw dumps, own reader). At the last dump of each run:
(a) per mode, R^NR_n against L^(-3/2) W R_q alpha_n (R_q of my own Mukhanov-Sasaki solution,
alpha_n from the code's keys via the rng twin): median relative deviation below 1e-3 for
|n| <= 32, every mode within 2e-2 (lattice dispersion at k dx = pi/2); (b) shell power
against the per-realisation linear power within 1e-2 for every shell, and against the
ensemble Mukhanov-Sasaki power: about 99.7 per cent of shells within 3/sqrt(M); (c) freezing:
SR shells that entered by N = 4.5 change by less than 1e-3 between N = 6 and N_f; USR shells
change by less than 1 per cent between the last two dumps (after N = 8). Refuted by any
shell beyond these bounds.

V6 (constraints, records and dumps). <|H|/[H]> of the 256^3 runs stays below 1e-10 at all
times (P1:539 prints "~1e-10"), with a SR entry plateau of order 1e-12; <|M|/[M]> at most
1e-4 in SR and of order 1e-2 late in USR (P1:541). My own [H] from the dumped fields equals
the record's mean [H] to 1e-6. Sign-flip control: <|H|/[H]> rises by more than 1e3 and
<|M|/[M]> reaches above 0.1. Refuted if a flip leaves H below 1e2 times the proper run.

V7 (backreaction levels, convergence, slow roll). Level 2 against level 0: shell power
differs by at most 1e-3 (P1:520 bound 1 per mille); level 1 against 0 below 1e-5. SR
convergence: max |1 - Delta_NR/Delta_lin| falls by about 2^6 per doubling of N (6th-order
stencils), H entry maximum order about 4 from 32 to 64. USR at N_f: eps1 of order 1e-12,
eps2 = -0.028 +- 0.002 (P1:534).

V8 (errata sample, six of E1-E17 other than E14, E15 which V3, V4 cover): each of the six
chosen misprints is confirmed by my own sympy derivation. A refutation is a derivation
in which the printed form holds.

## Entry 2, 2026-11-24 10:25 PST: outcomes of V1-V4 (runs E-20261124-181218-1e5f85e, E-20261124-181431-d45be89)

Own code `scripts/onepatch.py`, `scripts/onepatch_seeds.py`; figures looked at:
`fig_p0_background.png`, `fig_p0_moments.png` (first version: unreadable, the Stratonovich
reading has rare explosive paths whose spikes fill the panels), `fig_p0_moments_clipped.png`
(second run), `fig_p0_ito_mc.png`, `fig_p0_noise_amp.png`.

V1 held. DOP853 (rtol 1e-12) stops on the plateau at phi = 9.0640187, equal to my analytic
9.0640187 to 1e-14; RK4 0.01 9.064019, Heun 0.01 9.06393, Euler 0.001 9.06321, Euler 0.005
9.05997: all on the plateau (phi_c = 9.056). Forward Euler 0.01 crosses phi_c at
N = 3.0435 (P0:842 "~3.04") and ends at 9.05580. On the Euler-0.01 background eps1 = 3.2e-5,
eps2 = 5.99994 at N = 2 (P0:842 "eps1 << 1, eps2 ~ 6 from 2 e-folds").

V2 held, firmly. Six seeds x 50 000 paths (mean +- sd over seeds), Ito reading of the printed
SDE: std(alpha - 1) at N_b = 4, 5, 6: 0.1168 +- 0.0006, 0.1321 +- 0.0008, 0.1210 +- 0.0004
against my read-off 0.117, 0.133, 0.122; std(N - N_b): 0.0425, 0.1494, 0.1851 against 0.042,
0.150, 0.188. Stratonovich reading: std(alpha - 1) 0.1263, (N_b = 5: 0.36 +- 0.44, dominated by
a few exploding paths; 68 per cent half-width 0.142 against Ito 0.122), 0.1450; std(N - N_b)
0.0461, 0.1704, 0.2169, i.e. +8, +14, +15 per cent above the read-off where Ito is within
2 per cent. Median skewness of alpha over N_b in [4.5, 6]: Ito 1.116 +- 0.012 (P0 Fig. 2 about
1.1), Stratonovich 1.562 +- 0.026. Mean of N - N_b at N_b = 6: Ito 0.0026 +- 0.0008,
Stratonovich 0.084 +- 0.001 (P0 Fig. 1 red curve about 0.015 +- 0.019 over its 100 paths:
Stratonovich 3.6 standard errors away). Variants (one seed): alpha^5 Ito term: widths +4 per
cent at N_b = 6, skewness 1.31; alpha^3 -> 1 multiplier: skewness of alpha -0.74 at N_b = 6
(left-skewed, as P0:875 says); Langevin step 0.001 on the same background: std(alpha - 1)
0.1233 at N_b = 4 (step dependence 5 per cent); on the converged (plateau) background 80 per
cent of the paths are lost (alpha <= 0, > 1e3 or not finite) by N_b = 6, half by 5.38.
Deviation from what I expected: none in direction; the Ito skewness is 1.116, not the 1.04 the
ledger prints (see V-ledger below).

V3 held. Monte Carlo of alpha = c/Z, dZ = alpha s dW (s/c = 0.1, 4e6 paths, control variate):
drift 0.32039 +- 0.00023 (alpha0 = 2, horizon 0.001; alpha^5 s^2/c^2 = 0.32, alpha^3 = 0.08)
and 0.075987 +- 0.000054 (alpha0 = 1.5; alpha^5: 0.075938, alpha^3: 0.03375). The printed
alpha^3 is excluded by more than 1000 standard errors; alpha^5 agrees within 1.7 and 0.9.
Derivation (by hand, in VERIFIER.md): f(Z) = phidot/Z, f'' = 2 alpha^3/phidot^2,
(dZ)^2 = alpha^2 S_Pi^2 dt, so (1/2) f'' (dZ)^2 = alpha^5 S_Pi^2/phidot^2.

V4: USR held exactly, SR prediction failed as worded. Exact USR (V constant): amplitude over
the printed one 8.333e-4, 3.3333e-3, 1.3333e-2, 8.3332e-2 at sigma = 0.05, 0.1, 0.2, 0.5,
i.e. sigma^2/3 to 5 digits. SR (quadratic, eps1 = 0.0124, eps2 = -0.0247 at the evaluation
time): 1.079, 1.063, 1.051, 1.066 at the same sigma; at eps1 = 0.0244: 1.156, 1.123, 1.094,
1.088. I predicted "within 5 per cent"; the excess is the slow-roll drift of H/sqrt(eps1)
between Hubble crossing and k = sigma a H (|R|/A = 1.069 at sigma = 0.1, eps1 = 0.0124), an
O(eps ln(1/sigma)) correction, not an error of the printed SR formula at leading order.

## Entry 3, 2026-11-24 10:40 PST: outcomes of V5-V8 and of the ledger rerun

Runs: lattice reader E-20261124-182136-518eee2 (SR, 18 dumps), E-20261124-182151-93742a3
(USR, 24 of 41 dumps); comparison E-20261124-182829-775329c (SR), E-20261124-183037-f2a8ebf
(USR); records/rungs/backreaction E-20261124-183222-02ff27c; background and one-point
E-20261124-183347-e15a95f; entry windows E-20261124-183618-c71832c; errata
E-20261124-182402-a2f56bb; rerun of the note's run_all.py E-20261124-183303-303e6c3. The first
two lattice runs (E-20261124-181756-14fc721, E-20261124-181817-059b3d5) were stopped by me
before use: I had taken Phi with the sign of a (1 + 2 psi) metric; P0:178 uses (1 - 2 Phi).
All figures named below were looked at.

V5 (spectra, per mode) held. R^NR = Phi + (H/Pi_b) dphi with Phi = (1/2) dln chi +
(1/4) khat khat : dgt (my derivation from P0:178) equals my linear solution
L^-3/2 W R_q alpha_n per mode at N_f: SR median relative deviation 1.7e-7 (|n| <= 8),
2.8e-5 (|n| <= 32), 9.1e-4 (all 548 958 modes), max 4.5e-3; USR 2.7e-4, 2.6e-4, 1.1e-3,
single modes up to 0.25 (nonlinear mode coupling at rms R = 0.89). Without the E term the
SR deviation is 5.3e-3 and with the opposite sign of Phi 0.11: the data fix both. Shell power
over the linear power of the same realisation: largest 6.7e-3 (SR) and 6.7e-3 (USR), 1.6e-4 and
5.9e-4 for |n| <= 32; within 3/sqrt(M) of the ensemble Mukhanov-Sasaki power: 99.65 per cent of
the 3414 shells in both cases. The code's lockstep mode functions (.modes) agree with mine to
median 4.5e-4, max 2.5e-3 (top shell), 7.7e-8 for |n| <= 8. Prediction V5(a) "every mode within
2e-2" failed for USR single modes (0.25); held for SR and for all medians.
V5(c) freezing: SR shell power at N = 6.27 differs from N_f by 0.4 per cent in the top band
(my bound 1e-3 failed there), by 3e-5 for |n| <= 4; it relaxes as e^(-2.5 N) and is within
1e-4 of N_f for all bands from N = 7.2. USR: all bands within 1e-4 between the last two dumps.

V6 held for the records, partly failed for the paper's printed magnitudes. My [H] equals the
dumped Hmag to 3.3e-16; record columns <|H|>, <[H]>, <|H|/[H]> and <|M|/[M]> equal my dump
statistics to 5e-15 at every dump. <|H|/[H]> largest 5.1e-11 (SR, N = 4.43), 2.3e-11 (USR,
N = 2.29); box-mean removed (USR) 2.9e-12; <|M|/[M]> largest 4.0e-4 (SR) and 2.519e-2 (USR).
P1:539 prints "~1e-10": same order. Sign flip: <|H|/[H]> rises by a median 6.0e4 (SR, first
0.39 e-folds only) and 1.0e4 (USR); flipped <|M|/[M]> reaches 0.16 and 0.50. P1:541 prints
"H/[H] ~ 1e-5" for a flip: ours is 1e-7, a factor 100 lower (first order in both).

V7: backreaction held (USR level 2 against 0: rms 1.04e-4, largest shell 9.2e-4, 52 per cent
positive; SR at N = 7.19: largest 1.4e-4; level 1 against 0: 6.6e-7 SR, 7.0e-7 USR; all
below P1:520's 1 per mille). Convergence: SR spectra 8.0e-3, 1.9e-4, 4.6e-6 at 32, 64, 128
(factors 43 and 41 per doubling, my prediction of about 64 roughly held); H entry maximum order
32 -> 64: 4.17 with the window [0, ln 8 + 0.5] but 5.53 when N < 0.5 is excluded; USR H order
64 -> 128: 4.06 in every window. Slow roll at N_f held: USR eps1 1.008e-12, eps2 -0.0276
(P1:534 prints -2.8e-2); SR eps1 0.01353, eps2 -0.0269. Background: 64^3 box means against my
Friedmann solution 9.8e-13 (SR V), 1.1e-9 (USR V), 4.6e-5 (USR eps1); eps2 = 3 crossed at
N = 2.523 and 6.550.

V8 held: all six misprints (E1, E3, E6, E7, E8, E10) confirmed by my sympy derivation.

Ledger rerun: run_all.py of the note, rerun unchanged, gives 109 rows with values identical
to the committed ledger.csv (only the run id in the source column differs).

Paper figures (P1 Figs. 2, 3, 4 rendered from the source PDFs into scratch, looked at, not
committed): the SR R^NR 68 per cent band of P1 Fig. 2 ends at about +-0.8e-4 and dphi/phi_b at
+-1.0e-6, against our 2.28e-5 and 2.9e-7 (factor about 3.5); P1 Fig. 3 shows the final SR
spectrum at about 1e-10, the level of ours; USR Fig. 4: 68 per cent band +-3.5, full band +-18,
against our 0.89 and 4.57 (factor about 4); P1:534 prints "~10" for the furthest outliers.

## Entry 4, 2026-11-24 10:45 PST: post-verdict check of definitions

After committing VERIFIER.md (02d8175a) I read the window and bin definitions in the note's
scripts (not their results) and applied them with my readers (run E-20261124-184028-36a685d;
the first attempt E-20261124-184003-71eb0a8 failed: empty shell selection at early dumps, fixed
in compare.py). With the window 0.05 < N <= ln 8 my reader gives the ledger's entry maxima and
orders (1.78e-12, 2.00e-12, 1.23e-5, 4.15, 3.25, 2.25e-12, 3.25e-10, 4.05); with shells of more
than 10 modes the spectral maxima come within a factor 2.3 (SR 4.5e-3 vs 5.2e-3, |n| <= 32
1.1e-4 vs 1.0e-4; USR 3.5e-4 vs 3.6e-4). VERIFIER.md section 7 records this; sections 1-6 are
unchanged.
