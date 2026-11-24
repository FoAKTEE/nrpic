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

STATUS: DRAFT, being filled (2026-11-24 05:40 PST).

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
