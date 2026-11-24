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
