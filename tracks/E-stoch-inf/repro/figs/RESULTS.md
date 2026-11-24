# RESULTS of repro/figs: the figures of arXiv:2512.14649 from our runs

P1 = `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex` (figures P1:428-470, 549-561, 754-781; the
figure files beside it were rendered for looking only, never copied). Map rows: `../scope/REPRO_MAP.md`.
Set-up differences: `../scope/SETUP_AUDIT.md`, the four items with the verdict "different": (A3) the
Bunch-Davies start of the SR shells above nmax2 = 64 at k/aH = 100; (A11) Z4c without damping instead
of BSSN; (A18) backreaction level 0 in our main runs, level 2 in P1's; (A19) per-shell mode functions
with the continuum k^2 instead of P1's real-space mode equation with the lattice gradients.
Labels [VERIFIED] (measured by the named run), [JUDGEMENT], [TO VERIFY]. Values read off P1's figures
are single comparison values with the panel named ("P1 Fig. 4, R panel, read"); they are approximate
(about 10 per cent) and stored nowhere else.

Verdicts: REPRODUCED (the statement or figure agrees by the stated measure), IN PART (the shape or
part agrees, a stated part does not), NOT REPRODUCED, PENDING (a run it needs has not ended).

STATUS: DRAFT, PAUSED at 06:30 PST 2026-11-24 (pause flag). The numbers below come from test runs
of the figure scripts on the registered pass outputs (ledger, section 4); the registered figure run and
the PNGs in `fig/` are not made yet (JOURNAL entry 4, next steps).

## 1. Verdict per figure

| Fig. (P1 label) | Ours (file in `fig/`) | Runs | Verdict |
|---|---|---|---|
| 1 `fig:MeanRolls` | `fig1_meanrolls.png`, `fig1_residuals.png` | M64S, M64U (SMALL E-20261123-020704-2b99463) | REPRODUCED |
| 2 `fig:quad_contrast` | `fig2_sr_contrast.png` | RSF256 + continuation | see section 2 |
| 3 `fig:quad_spec` | `fig3_sr_spec.png`, `fig3_sr_spec_ratio.png` | RSF256 + continuation (P256v6 beside it) | see section 2 |
| 4 `fig:usr_contrast` | `fig4_usr_contrast.png`, `fig4_usr_contrast_hzero.png` | USF256 E-20261123-021204-2f573ec | IN PART |
| 5 `fig:usr_spec` | `fig5_usr_spec.png`, `fig5_usr_spec_ratio.png` | USF256 | REPRODUCED |
| 6 `fig:specAK` | `fig6a_sr_Kspec.png`, `fig6b_usr_Kspec.png` | RSF256 / P256v6, USF256 | see section 2 |
| 7 `fig:specConvergence` | `fig7_specconv.png` | C32S, C64S, C128S (SMALL), CL256S + continuation | see section 2 |
| 8 `fig:Convergence` | `fig8_convergence.png` | C32-C128 S/U (SMALL), CL256S/U + continuations | see section 2 |
| 9 `fig:ablationback` | `fig9_ablation.png` | AL0S, AL1S, AL2S + continuation, AL0U, AL1U, AL2U; RL1, UL1, P256v6, U256ap | see section 2 |
| (P1:541, no figure) | `fig_signflip.png` | RNC256 + continuation, U256nc E-20261122-190341-0419be6 | see section 3, S16 |

## 2. Per figure: what agrees, by which measure, what differs and why

### Fig. 1 (mean rolls at 64 cells) — REPRODUCED

Ours: box means of the constraint record of M64S and M64U (64^3, k_max = 16 dk) against our own
Friedmann integration from the decks' (phi0, pi0), V in P1's units. Agreement: SR max |V/V_F - 1| =
9.8e-13, |eps1/eps1_F - 1| = 6.3e-12, |eps2 - eps2_F| = 2.2e-11 over 348 record lines; USR 1.1e-9,
4.6e-5, 4.4e-5 over 427 lines [VERIFIED, figure run]. P1's "perfect agreement" (P1:440) holds in
ours to these bars (scope P5 PASS). The shapes are P1's: SR V from 0.0269 to 0.0220, eps1 from 0.0111
to 0.0135, eps2 from -0.0222 to -0.0269; USR eps1 peak 0.024 near N = 1.65, eps2 plateau near 6 from
N = 3 to 6, inset minimum of eps1 9.716e-13 at N = 8.335 (P1 Fig. 1b inset, read: about 0.97e-12 near
8.4). Differs: the e-fold span. Our SR runs end at N = 8.10 (tlim = 8.5), P1's axis at about 7.65
(P1 Fig. 1a, read); our USR at 10.0, P1's at about 9.6 (Fig. 1b, read). P1's Table I gives only "~8"
and "~10" (P1:419-420); we took the integers (audit item 4, a judgement). None of the four
differences A3, A11, A18, A19 enters the background at this precision (level 0 against level 2 changes
the box means at second order, below these bars [JUDGEMENT]).

### Fig. 4 (USR contrasts, 256^3) — IN PART

Agrees (shape and timing, P1:532-541): the three top panels show the progressive entry within about 4
e-folds; delta phi/phi_b has P1's double feature (68 per cent half-width 8.0e-6 at N = 2.3, down to
2.9e-6 at N = 3.05, up to 4.7e-6 at N = 4.5, then frozen at 4.5e-6); delta K/K_b rises to 4.2e-7 at N
= 1.55 and falls by 5e5 to N_f without a second growth; delta Pi/Pi_b becomes large at late times
(1.24e-2 at N_f, against 3.95e-5 at N = 0); R^NR grows between N = 5 and 8 and is frozen after N = 9
(68 per cent width constant to 0.05 per cent); |M|/[M] rises by three decades between N = 2.5 and 4.5
and stays near 1e-3 to 3e-2 (P1 "around 1e-2"); |H - <H>|/[H] sits at 1e-13 to 3e-12 during the entry
and falls to about 1e-15 at N_f, as P1's |H|/[H] does. Measures: per-cell constraint means equal the
record to 2.6e-15 (F2 a); R^NR one-point 68 per cent half-width 0.890 = the linear expectation
sigma_R = 0.894 within 0.5 per cent; 100/68 band ratio 5.1 (Gaussian) [VERIFIED, figure run].
Differs (1), the amplitudes, by a factor that grows from about 2.4 to about 4: P1's 68 per cent bands
read off P1 Fig. 4 are about 2e-5 (delta phi/phi_b at N = 2; ours 8.5e-6), 0.95e-6 (delta K/K_b near N
= 1.8; ours 4.2e-7), 5e-2 (delta Pi/Pi_b late; ours 1.24e-2), 3.4 (R^NR late; ours 0.89); P1's 100 per
cent band of R^NR reaches about 18 (P1:534 "~10 for the furthest outliers"; ours 4.57). Ours is
consistent with its own spectrum and with the linear (MS) normalisation (sigma_R from the mode
functions, 0.894; Delta at k_max 1.016, P1:536 "up to ~0.1-1"); a one-point width of 3.4 would need
Delta of about 15 at k_max, which P1's own Fig. 5 does not show. So the factor is not in the shared
physics: P1's one-point percentiles and P1's spectra imply different amplitudes [JUDGEMENT from
reading P1's figures; P1 does not state the normalisation of the real-space draw]. None of the four
set-up differences can make a factor 4 in a linear amplitude: A18 (level 2) is a second-order effect
(our level-2 runs, section Fig. 9), A19 changes the top shells by about 3e-3 (Fig. 5 ratio), A3 is SR
only, A11 acts at the order of the constraint violation. Differs (2): |H|/[H] with the box mean kept is
dominated in our run at N = 2-3 and after N = 7 by the uniform residual of the background step
(scope entry 0; a flat 3e-14 at late times); it is a property of our time integration of the
background with Z4c (A11 and the step), not of the noise. With the box mean removed the panel has P1's
shape. Differs (3): the dense time sampling of P1 (its percentile curves are jagged from step to
step); ours has 41 dumps.

### Fig. 5 (USR spectra, 256^3) — REPRODUCED

Agrees: Delta[R^NR] from N = 0 to N_f in P1's layout (bins = lattice shells with more than 10 modes,
band = range in the bin), with the dashed MS expectation; the late spectra rise as k^4 to Delta = 1.0
at k_max (MS expectation 1.016 at |n| = 64), and above k_max a second-order shelf near 1e-8 that falls
at 2 k_max (P1's Fig. 5 shows the same shelf). Measures at N_f (3395 shells): NR shell power over the
realisation's linear power (same alpha_n) within 5.0e-3 at every shell (rms 1.0e-3; 3.6e-4 for k <=
k_max/2); NR over the MS expectation within 3/sqrt(count) at 99.6 per cent of the shells (cosmic
variance); power above k_max at most 1.3e-7 of Delta_MS(k_max) [VERIFIED, figure run]. Differs: our
top shells (|n| > 50) depart from the linear spectrum by 1e-3 to 5e-3, the mode-equation difference
A19 (our noise R uses the continuum k^2, the NR field the stencil) together with the second order at
Delta ~ 1; P1's real-space R^MS feels the stencil itself, so P1's agreement at the top shells need not
show it (A19, as `../scope/SETUP_AUDIT.md` predicted). P1's last spectrum is at <N> = 7.95 (legend,
read); ours at N_f = 10.0 (both after the USR growth has ended, so the late curves agree).

### Fig. 3 (SR spectra, 256^3) — REPRODUCED (from P256v6; RSF256 repeats its steps)

Ours from P256v6 (E-20261121-202935-31520bc, release build, the same deck and steps as RSF256 with
fewer dumps; scope entry 0 and the bit identity of their t = 0 dumps). Agrees: Delta[R^NR] from N = 0
to N_f in P1's layout; the entering modes rise to the flat Delta = 1.0e-10 and freeze; at N = 0 the
NR spectrum starts near 3e-17 at k_min as P1's does (P1 Fig. 3, read: about 1e-17 to 1e-16); the MS
expectation (dashed) is the vacuum k^2 rise at early times and the flat 1e-10 at the end. Measures at
N_f (3395 shells): NR over the realisation's linear power within 1.0e-4 for k <= k_max/2 and within
5.2e-3 at every shell (rms 1.1e-3, the top shells); NR over MS within 3/sqrt(count) at 99.6 per cent
of the shells; above k_max 8.7e-14 of Delta_MS(k_max) [VERIFIED, figure run]. Differs: the top-shell
departure (1e-3 to 5e-3 above |n| of about 50) is A19 (continuum k^2 in our noise R against the
stencil in the NR field) with A3 (our shells above nmax2 = 64 start from Bunch-Davies at k/aH = 100,
an amplitude correction of order 1e-4); P1's real-space R^MS has the stencil in it, so P1's top shells
need not show it. P1's last time is <N> = 7.57 (legend, read), ours N_f = 8.10 (the background span,
Fig. 1).

### Fig. 6 (K, Kt and sqrt(3 Kt Kt/2) spectra) — REPRODUCED in shape, see the hierarchy statement

Ours: three panels per scenario in P1's units ((100 H*/Mpl)^2 times the code spectra). The anisotropic
spectrum is the invariant Kt_ij Kt^ij = At_ij At^ij (sum_ij |At_ij(k)|^2, P1:564); the first version of
our script summed the covariant At_ij/chi and was too large by a^4 (journal entry 2; SR uses the
first-version pass rescaled by <chi>^2, exact to second order; USR the rerun E-20261124-141807-8352509).
Agrees, SR: Delta[K] reaches the flat 1e-19 (P1's level, P1 Fig. 6a, read) and freezes (N_f over N =
5.34: 0.998 median); Delta[Kt] peaks at the crossing and decays (N_f over N = 4.39: 2.8e-5); the
second-order sqrt(3 Kt Kt/2) is below Delta[K] by more than 1e8 at N_f (S25, S26). USR: Delta[K]
decays by 1e9 after the USR onset (S24). Differs: in USR the hierarchy sqrt(3 Kt Kt/2) << K holds at
N_f too (median ratio 9e-7), but between N = 0.8 and 7 most shells have it reversed (Q above K at up
to 100 per cent of the shells), so P1's "no hierarchy in USR" (P1:572) is true of our run during and
before the USR phase, not at its end; in SR the hierarchy is established from N = 3.9 on (all shells)
and reversed before N = 3.4. Magnitudes: our Kt and Q at late times are about 10-100 below P1's (P1
Fig. 6, read), as expected for second-order quantities if P1's real-space amplitude is larger (Fig. 4).

### Fig. 7 (spectral convergence, SR, k_max/dk = 8) — IN PART (256 PENDING)

Ours: |1 - Delta_NR/Delta_lin| per shell at N_f, Delta_lin the realisation's linear spectrum (P1's
values for N = 256, 1e-7 to 3e-6, are far below cosmic variance, so P1 too compares with its own draw
[JUDGEMENT]). Agrees: monotone convergence; max over the 44 shells 3.2e-3 (N = 32), 6.2e-5 (64),
1.0e-6 (128), medians 4.2e-4, 7.5e-6, 1.8e-7 (sixth order, the stencils); the curves rise with k as
P1's do; P1's N = 32 and 64 curves (P1 Fig. 7, read: about 1e-4 to 1e-2 and 5e-6 to 1e-4) are where
ours are. Differs: our N = 128 is about ten times below P1's (read: 2e-6 to 4e-5), i.e. our
convergence continues at order 6 where P1's slows to order 3 [JUDGEMENT: A19 and P1's real-space MS
reference, whose own stencil error is in the "reference"]. PENDING: N = 256 (CL256S, cut at t = 6.23,
continued by repro/continue as E-20261124-130952-4be980b; queued).

### Fig. 8 (constraint convergence) — IN PART (256 PENDING)

Ours: record means <|H|/[H]> and <|M|/[M]> against e-folds for N = 32, 64, 128 (both scenarios;
USR with the box mean of H removed as a thin line). Agrees: the early plateau set by the second order
of each kick, the same for N = 64 and 128 (entry maxima within 13 per cent), the exponential decay
after the entry in SR, the late rise of |M|/[M] in USR (P1:748-750); N = 32 sits above, with the
truncation error (order of the entry maximum 32 -> 64: 4.15 for H in SR). Differs: (1) levels: our SR
plateau of <|H|/[H]> is about 5e-13 against P1's about 2e-11 (P1 Fig. 8a, read), and of <|M|/[M]>
5e-6 against 1.5e-5: H/[H] is second order and M/[M] first order in the amplitude, so P1's larger
real-space amplitude (Fig. 4) predicts factors of about 16 and 4, close to the 40 and 3 seen; A11
(Z4c against BSSN) changes the level of H by factors of order one [JUDGEMENT]. (2) Our USR <|H|/[H]>
with the box mean kept is the uniform residual of the background step (fourth order in dt: entry
maxima 9.2e-8, 5.4e-9, 3.2e-10 for 32, 64, 128, order 4.1); P1's USR curves do not show it, so P1's
background step error is smaller or removed [TO VERIFY]; with the box mean removed our USR curves
have P1's shape. (3) Our M order 32 -> 64 is 3.3 (SR) and 3.5 (USR), not the 4-6 we predicted.
PENDING: N = 256 (CL256S and CL256U, continued as E-20261124-130952-4be980b and
E-20261124-130711-a5dec67; queued).

### Fig. 9 (ablation of the stochastic backreaction) — IN PART (SR level 2 at N_f PENDING)

Ours: level 2 and level 1 against level 0, all three with the mode equation on the mesh (AL runs,
branch build core/noise-level2, decision 0031), same seed, per injected shell (more than 10 modes) at
N_f; beside it the controls. Agrees: USR level 2 - level 0 (orange) scatters around zero (52 per cent
of shells positive) with rms 1.0e-4, rising with k from about 1e-5 to 3e-4 (max 7.0e-4 at |n| >= 56):
the magnitude and the rise of P1's orange curve (P1 Fig. 9, read: about 1e-5 to 1e-3). Level 1 -
level 0 (blue SR, green USR) rises smoothly from about 5e-10 at k_min to about 5e-7 at k_max, one sign
over 90 per cent of the shells: the shape of P1's green curve (read: 1e-9 to 3e-6); P1's SR level-1
curve (blue) stays near 1e-9 to 1e-8 where ours reaches 5e-7. The released level 1 on shells (RL1,
UL1) against the released level 0 gives the same 6.6e-7 / 8.0e-7, so the level-1 shift does not come
from the mesh mode equation. Controls: released level 0 on shells against level 0 on the mesh differs
by up to 1.3e-2 (SR) and 1.7e-2 (USR) at the top shells, rising as the stencil symbol (A19), which is
why decision 0031 compares the levels on the mesh. Records of levels 1, 2 within 5e-4 of level 0.
SR level 2 at t = 7.5 (N = 7.2, all modes frozen): `fig9_ablation_sr_t75` (run
E-20261124-141807-8352509). Differs: P1:520 states "<~ 1 per ten thousand for all scales"; our USR
level-2 change exceeds 1e-4 above |n| of about 32 (and so does P1's own orange curve as read), so P1's
text bound and P1's figure disagree; ours agrees with the figure. PENDING: SR level 2 at N_f (AL2S
continued as E-20261124-131359-49afe29; queued).

## 3. Statements of the map (analysis rows, and the run rows that feed the figures)

| # | P1 line | Statement | Ours (measure, run) | Verdict |
|---|---|---|---|---|
| S3 | 520, 790 | level 2 against 0: detectable, <~ 1e-4 in the power at all scales | USR: rms 1.0e-4, max 7.0e-4 (top shells), detectable (per-mode 3.0e-3 rms); SR at t = 7.5 in `fig9_ablation_sr_t75`; SR at N_f pending | IN PART (USR above 1e-4 at the top shells, as P1's own figure; SR at N_f PENDING) |
| S4 | 522 | quadratic: modes enter for about 3.5-4 e-folds | delta phi/phi_b reaches 95 per cent of its final 68 per cent width at N = 3.91; R^NR at 3.44 (P256v6) | REPRODUCED |
| S7 | 532 | inflection: entry of all modes within ~4 e-folds; double growth of the phi contrast, none in K; decay for 2 <~ N <~ 3, growth 3 <~ N <~ 4 | delta phi/phi_b 68 per cent: 8.0e-6 (N = 2.3), 2.9e-6 (3.05), 4.7e-6 (4.5); delta K/K_b peaks at 1.55 and decays by 5e5 (USF256) | REPRODUCED (shape and timing; amplitude see Fig. 4) |
| S8 | 534 | USR from N ~ 3.5 until ~ 8 | eps2 > 3 from N = 2.523 to 6.550 (box means of M64U = Friedmann within 1e-5) | REPRODUCED as P1's Fig. 1 shows it; P1's text "3.5 to 8" is about one e-fold later than its own Fig. 1 (scope errata) |
| S9 | 534 | after the plateau (eps1, eps2) ~ (0, -2.8e-2); R freezes | eps1 = 1.008e-12, eps2 = -0.02760 at N_f (M64U); R^NR 68 per cent width constant to 5e-4 from N = 9 (USF256) | REPRODUCED |
| S10 | 534 | R^NR ~ 10 for the furthest outliers | max |R^NR| = 4.57 at N_f (USF256, 1.7e7 cells; 5.1 times the 68 per cent width, Gaussian) | NOT REPRODUCED in our realisation and normalisation (see Fig. 4, factor about 4) |
| S11 | 534 | delta Pi/Pi_b relatively large at late times (inflection), unlike quadratic | 1.24e-2 (USR, N_f) against 2.8e-9 (SR, N_f) | REPRODUCED |
| S12 | 536 | Delta[R] up to ~0.1-1; excellent agreement with the linear spectrum at complete overlap | Delta(k_max) = 1.0 (MS 1.016); NR/linear within 5e-3 at every shell, 3.6e-4 for k <= k_max/2 | REPRODUCED |
| S13 | 539 | noise in R of maximum amplitude ~1e-5 in its entry phase | SR: 68 per cent half-width of R^NR 1.6e-5 to 2.3e-5 during the entry, max over cells 1.1e-4 (P256v6) | REPRODUCED (reading "~1e-5" as the typical amplitude) |
| S14 | 539 | H/[H] at the next order (~1e-10) in both scenarios, then damped | USR: per-cell 99th percentile <= 2.4e-11, box mean with H0 removed <= 2.9e-12 (record), decays to 1e-15; SR: record entry plateau 5e-13 (C64S, C128S); 256^3 SR per cell PENDING (RSF256) | IN PART: second order and damped, yes; our level is 10-100 below P1's ~1e-10 (amplitude, A11) |
| S16 | 541 | flipping any sign of the noise gives first order: H/[H] ~1e-5, M/[M] ~1 | USR (U256nc, Pi sign): H ratio over the proper run >= 1.9e3 in the entry, M/[M] up to 0.50; SR (RNC256 to t = 0.71 so far): ratio 7.3e4, M/[M] 0.16 | IN PART (first order shown; SR to t = 4.5 PENDING, RNC256 continued as E-20261124-130629-61fe0b0) |
| S18 | 541 | inflection: |M|/[M] later around 1e-2 | late 68 per cent band 8.4e-4 to 3.2e-3, record mean 2.5e-2 at its maximum (N = 6.6) | REPRODUCED within the amplitude factor (Fig. 4) |
| S21 | 748-750 | early plateau, decay after entry, test loses meaning later | Fig. 8 at 32-128 | REPRODUCED for 32-128 (256 PENDING) |
| S22 | 752 | spectra converge toward MS with N | Fig. 7: 3.2e-3, 6.2e-5, 1.0e-6 | REPRODUCED for 32-128 (256 PENDING) |
| S24 | 570 | K perturbations freeze (SR), decay (USR) | SR 0.998 of the N = 5.3 value at N_f; USR down by 1e9 | REPRODUCED |
| S25 | 570 | anisotropic and isotropic comparable at first, anisotropic decays after crossing (SR) | Kt peaks at crossing, falls to 2.8e-5 of its N = 4.4 value; early Q above K at most shells | REPRODUCED |
| S26 | 572 | sqrt(3 Kt Kt/2) subdominant for most, not all, times; no such hierarchy in USR | SR: Q < K at every shell from N = 3.9 (ratio < 6e-9 at N_f), not before 3.4; USR: Q above K at most shells for N = 0.8-7, below after 7.5 (ratio 9e-7 at N_f) | IN PART (the USR hierarchy is absent during the USR phase, present at its end) |

## 4. Ledger (registered runs this package made; all on processors)

| Run id | What | Numbers it carries |
|---|---|---|
| E-20261124-130628-6790851 | dump pass of USF256 (41 dumps) + bit check against U256ap | Figs. 4, 5, 6b (Q, K); scope P1 (USR), P2 (USR per cell), P7; F2, F3/F5, F6 USR |
| E-20261124-133251-42e8aab | dump passes of P256v6 (18 dumps), AL0S/AL1S/RL1, AL0U/AL1U/AL2U/UL1/U256ap (t = 0, N_f), C32-C128 S/U; seven bit checks | Figs. 3, 6a, 7, 9 (USR, level 1), field panels of Fig. 2; P-A2, P-A3, scope P4, P6 (a, c) |
| E-20261124-141807-8352509 | USF256 at the Fig. 6b dumps with the invariant Kt; AL0S/AL1S/AL2S at t = 7.5; bit check AL2S t = 0 | Fig. 6b (Kt), Fig. 9 SR at t = 7.5 (not yet judged) |
| (pending) | figure run `make_figs.py` | every figure in `fig/` |

Scripts: `figures/` at the commit named in each manifest. Fig. 1 and the sign-flip figure read the
records directly (no pass). Record-based numbers of scope P2 (USR): max <|H - <H>|/[H]> = 2.885e-12,
max <|M|/[M]> = 2.519e-2 (USF256 record; the same in U256ap), read with `figlib.read_con_joined`.

## 5. Requests

- Lead of E: copy `CARD_COSTS.md` into the second table of `../scope/CARD_PLAN.md` (this package may
  not edit repro/scope); correct `../scope/SETUP_AUDIT.md` item 4 and the SR deck header: tlim = 8.5
  is N* + 8.10 e-folds, not 8.04 (Fig. 1, own Friedmann integration and the M64S record).
- core: (1) the t = 0 dumps of backreaction levels 1 and 2 differ from level 0 in the last bits (up to
  7.2e-10 of the perturbation range, 36-8140 cells; release level 1 and branch levels 1, 2); please
  confirm that it is the box-mean background of the slice (roundoff), not a level-dependent slice.
  (2) Level 1 changes the final power by a smooth, one-signed 5e-10 (k_min) to 6.6e-7 (k_max) in both
  scenarios and in both builds (RL1/UL1 release on shells, AL1S/AL1U branch on the mesh): larger than
  the 1e-8 predicted from box means equal to Friedmann within 1e-11 (ablation P-A1); an explanation is
  wanted before the note quotes level 1 against P1's (P1's quadratic level-1 curve is near 1e-9-1e-8).
- Note (repro/note): P1's one-point bands (Figs. 2, 4) are about 4 times the width that P1's own
  spectra (Figs. 3, 5) and the linear normalisation imply, in both scenarios (Fig. 4 section); our runs
  agree with the spectra. Say so as a judgement from reading P1's figures, not as P1's error; asking the
  authors is the group's step (nobody outside is contacted).
