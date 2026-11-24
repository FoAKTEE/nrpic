# RESULTS of repro/figs: the figures of arXiv:2512.14649 from our runs

P1 = `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex` (figures P1:428-470, 549-561, 754-781; the
figure files beside it were rendered for looking only, never copied). Map rows: `../scope/REPRO_MAP.md`.
Set-up differences: `../scope/SETUP_AUDIT.md`, the four items with the verdict "different": (A3) the
Bunch-Davies start of the SR shells above nmax2 = 64 at k/aH = 100; (A11) Z4c without damping instead
of BSSN; (A18) backreaction level 0 in our main runs, level 2 in P1's; (A19) per-shell mode functions
with the continuum k^2 instead of P1's real-space mode equation with the lattice gradients.
Labels [VERIFIED] (measured by the named run), [JUDGEMENT], [TO VERIFY]. Values read off P1's figures
are single comparison values with the panel named ("P1 Fig. 4, read"); they are approximate (about
10 per cent at best, a factor 2 on log axes) and stored nowhere else.

Verdicts: REPRODUCED (the statement or figure agrees by the stated measure), IN PART (the shape or
part agrees, a stated part does not), NOT REPRODUCED, PENDING (a run it needs has not ended; the run id
that completes it is named).

STATUS (2026-11-24 13:50 PST, update pass of batch R3): four of the five continued runs of package
repro/continue have ended at their tlim and are in the figures (RNC256, CL256U, CL256S, AL2S; joins
confirmed twice, JOURNAL entry 11). The committed figures in `fig/` and every number below come from
the registered figure run E-20261124-213739-9776185 (its jsons and PNGs equal those of
E-20261124-213532-3f00681 byte for byte except `fig_signflip.json`, which adds the scope-P2 maxima;
Figs. 1-6 equal those of the earlier figure run E-20261124-173254-420115f byte for byte; JOURNAL
entries 11, 12). One run is still out: RSF256 (SR 256^3 with metric dumps) is joined to cycle 895 (t =
5.49 of 8.5) and its fourth continuation waits in the shared card queue as **q0034**
(`harness/bin/nrpic-queue show q0034`; not dispatched at 13:27 PST). The rows PENDING below need it,
and only it (section 5).

## 1. Verdict per figure

| Fig. (P1 label) | Ours (`fig/`) | Runs | Verdict |
|---|---|---|---|
| 1 `fig:MeanRolls` | `fig1_meanrolls.png`, `fig1_residuals.png` | M64S, M64U (SMALL E-20261123-020704-2b99463) | REPRODUCED |
| 2 `fig:quad_contrast` | `fig2_sr_contrast_P256v6.png` | P256v6 E-20261121-202935-31520bc (field panels); RSF256 + continuations (constraint panels) | IN PART (field panels); constraint panels PENDING (RSF256, queue q0034) |
| 3 `fig:quad_spec` | `fig3_sr_spec_P256v6.png`, `..._ratio.png` | P256v6 (RSF256 repeats its deck and steps; bit-identical to t = 5.0) | REPRODUCED (the figure from RSF256 itself PENDING, queue q0034) |
| 4 `fig:usr_contrast` | `fig4_usr_contrast.png`, `fig4_usr_contrast_hzero.png` | USF256 E-20261123-021204-2f573ec | IN PART |
| 5 `fig:usr_spec` | `fig5_usr_spec.png`, `..._ratio.png` | USF256 | REPRODUCED |
| 6 `fig:specAK` | `fig6a_sr_Kspec_P256v6.png`, `fig6b_usr_Kspec.png` | P256v6; USF256 | REPRODUCED (figure); statement S26 IN PART |
| 7 `fig:specConvergence` | `fig7_specconv.png` | C32S, C64S, C128S (SMALL); CL256S + continuation E-20261124-130952-4be980b | REPRODUCED (monotone convergence 32-256; a floor near 1e-7 at the lowest shells, cause open) |
| 8 `fig:Convergence` | `fig8_convergence.png` | C32-C128 S/U (SMALL); CL256S/U + continuations | IN PART (plateau, decay, USR rise and convergence 32-256 as P1; levels below P1's) |
| 9 `fig:ablationback` | `fig9_ablation.png`, `fig9_ablation_sr_t75.png` | AL0S, AL1S, AL2S (+ continuation E-20261124-131359-49afe29), AL0U, AL1U, AL2U; RL1, UL1, P256v6, U256ap | IN PART (level 2 as P1's figure in both scenarios; USR top shells above P1:520's bound; SR level 1 above P1's) |
| (P1:541, no figure) | `fig_signflip.png` | RNC256 + continuation E-20261124-130629-61fe0b0 against RSF256 (joined to cycle 895); U256nc E-20261122-190341-0419be6 | IN PART (first order in both scenarios; our H/[H] about 1e2 below P1's "~1e-5") |
| (joins) | `fig_joins.png` | the five continued runs | the joined records equal our reader's, every junction smooth (JOURNAL entry 11, J) |

## 2. Per figure: what agrees, by which measure, what differs and why

### Fig. 1 (mean rolls at 64 cells): REPRODUCED

Ours: box means of the constraint record of M64S and M64U (64^3, k_max = 16 dk) against our own
Friedmann integration from the decks' (phi0, pi0), V in P1's units. Agreement: SR max |V/V_F - 1| =
9.8e-13, |eps1/eps1_F - 1| = 6.3e-12, |eps2 - eps2_F| = 2.2e-11 over 348 record lines; USR 1.1e-9,
4.6e-5, 4.4e-5 over 427 lines [VERIFIED, `fig/fig1.json`]. P1's "perfect agreement" (P1:440) holds
to these bars (scope P5 PASS). The shapes are P1's: SR V from 0.0269 to 0.0220, eps1 from 0.0111 to
0.0135, eps2 from -0.0222 to -0.0269; USR eps1 peak 0.024 near N = 1.65, eps2 plateau near 6 from N = 3
to 6, inset minimum of eps1 9.716e-13 at N = 8.335 (P1 Fig. 1b inset, read: about 0.97e-12 near 8.4);
eps2 = 3 crossed at N = 2.5234 and 6.5503 (own Friedmann 2.5234, 6.5503). Differs: the e-fold span.
Our SR runs end at N = 8.099 (tlim = 8.5), P1's axis at about 7.65 (P1 Fig. 1a, read); our USR at
10.0, P1's at about 9.6. P1's Table I gives only "~8" and "~10" (P1:419-420); we took the integers
(audit item 4, a judgement; the audit's "N* + 8.04" for SR is corrected to 8.10, request below). None
of A3, A11, A18, A19 enters the background at these bars (level 2 against 0 changes the box means at
second order [JUDGEMENT]).

### Fig. 2 (SR contrasts, 256^3): IN PART (field panels); constraint panels PENDING (q0034)

Ours from P256v6 (release build, the deck and steps of RSF256 with 18 dumps; the dumps of RSF256 and
P256v6 at t = 0, 4.0006 and 5.0008 are bit-identical in all 17 common variables [VERIFIED,
`bitcheck_rsf256bit.json` of E-20261124-213029-e937f69], scope P1 for SR as far as RSF256 has run).
P256v6's dumps carry no constraint fields, so the two lower panels say so; they come from RSF256 when
its fourth continuation (queue q0034) has ended: then `runs.py rsf256` and `make_figs.py --rsf256`
(section 5). Agrees (shape and timing,
P1:522): delta phi/phi_b, delta K/K_b and R^NR widen during the entry and freeze; delta phi/phi_b
reaches 95 per cent of its final 68 per cent width at N = 3.91, R^NR at 3.44 (P1 "3.5-4");
delta Pi/Pi_b stays near 1.5e-5 (68 per cent half-width; 3.7e-5 at N = 0) from N = 1 to 3.9 and
collapses at the last crossings, to 7.7e-5 of its maximum at N_f, as in P1's figure; the 100/68 band ratio at N_f is 4.97
(delta phi), 5.0 (R^NR), Gaussian for 1.7e7 correlated cells; R^NR one-point 68 per cent half-width
2.281e-5 equals the realisation's linear sigma 2.278e-5 (the NR field itself 2.2780e-5) [VERIFIED,
`fig/fig2_sr_contrast_P256v6.json`, JOURNAL entry 3]. Differs, the amplitudes by a factor of about
3.5: P1's 68 per cent bands read off P1 Fig. 2 are about 1.0e-6 (delta phi/phi_b and delta K/K_b at
N_f; ours 2.88e-7, 2.86e-7), 0.6e-4 (delta Pi/Pi_b before the entry; ours 1.5e-5) and 0.8e-4 (R^NR;
ours 2.28e-5). The same factor appears in USR (Fig. 4), while P1's spectra (Fig. 3, 5) agree with ours
in level: see Fig. 4 for why this is not in the shared physics. None of A3, A11, A18, A19 can make a
factor 3.5 in a linear amplitude.

### Fig. 3 (SR spectra, 256^3): REPRODUCED (from P256v6; RSF256 repeats its steps bit for bit to t = 5.0)

Agrees: Delta[R^NR] from N = 0 to N_f in P1's layout; the entering modes rise to the flat Delta =
1.0e-10 and freeze; at N = 0 the NR spectrum starts near 3e-17 at k_min as P1's does (P1 Fig. 3, read:
about 1e-17 to 1e-16); the MS expectation (dashed) is the vacuum k^2 rise at early times and the flat
1e-10 at the end. Measures at N_f (3395 shells): NR over the realisation's linear power within 1.0e-4
for k <= k_max/2 and within 5.2e-3 at every shell (rms 1.1e-3, the top shells); NR over MS within
3/sqrt(count) at 99.6 per cent of the shells; above k_max 8.7e-14 of Delta_MS(k_max) [VERIFIED,
`fig/fig3_sr_spec_P256v6.json`]. Differs: the top-shell departure (1e-3 to 5e-3 above |n| of about
50) is A19 (continuum k^2 in our noise R against the stencil in the NR field) with A3 (our shells above
nmax2 = 64 start from Bunch-Davies at k/aH = 100, an amplitude correction of order 1e-4); P1's
real-space R^MS has the stencil in it, so P1's top shells need not show it. P1's last time is
<N> = 7.57 (legend, read), ours N_f = 8.10 (the background span, Fig. 1).

### Fig. 4 (USR contrasts, 256^3): IN PART

Agrees (shape and timing, P1:532-541): the three top panels show the progressive entry within about 4
e-folds; delta phi/phi_b has P1's double feature (68 per cent half-width 8.0e-6 at N = 2.3, down to
2.9e-6 at N = 3.05, up to 4.7e-6 at N = 4.5, then frozen at 4.5e-6); delta K/K_b rises to 4.2e-7 at N
= 1.55 and falls by 5e5 to N_f without a second growth; delta Pi/Pi_b becomes large at late times
(1.24e-2 at N_f, against 3.95e-5 at N = 0); R^NR grows between N = 5 and 8 and is frozen after N = 9
(68 per cent width constant to 0.05 per cent); |M|/[M] rises by three decades between N = 2.5 and 4.5
and stays near 1e-3 to 3e-2 (P1 "around 1e-2"); |H - <H>|/[H] sits at 1e-13 to 3e-12 during the entry
and falls to about 1e-15 at N_f, as P1's |H|/[H] does. Measures: per-cell constraint means equal the
record to 2.6e-15 (F2 a); R^NR one-point 68 per cent half-width 0.890 = the linear expectation
sigma_R = 0.894 within 0.5 per cent; 100/68 band ratio 5.1 (Gaussian) [VERIFIED,
`fig/fig4_usr_contrast.json`, `fig/fig4_usr_contrast_hzero.json`].
Differs (1), the amplitudes, by a factor 2.3 to 4: P1's 68 per cent bands read off P1 Fig. 4 are about
2e-5 (delta phi/phi_b at N = 2; ours 8.5e-6), 0.95e-6 (delta K/K_b near N = 1.8; ours 4.2e-7), 5e-2
(delta Pi/Pi_b late; ours 1.24e-2), 3.4 (R^NR late; ours 0.89); P1's 100 per cent band of R^NR reaches
about 18 (P1:534 "~10 for the furthest outliers"; ours 4.57). Ours is consistent with its own spectrum
and with the linear (MS) normalisation (sigma_R from the mode functions, 0.894; Delta at k_max 1.016,
P1:536 "up to ~0.1-1"); a one-point width of 3.4 would need Delta of about 15 at k_max, which P1's
own Fig. 5 does not show. So the factor is not in the shared physics: P1's one-point percentiles and
P1's spectra imply different amplitudes, in both scenarios (Fig. 2: about 3.5) [JUDGEMENT from reading
P1's figures; P1 does not state the normalisation of its real-space draw]. None of the four set-up
differences can make a factor 2-4 in a linear amplitude: A18 is second order (Fig. 9: 1e-4), A19
changes the top shells by about 3e-3 (Fig. 5 ratio), A3 is SR only, A11 acts at the order of the
constraint violation. Differs (2): |H|/[H] with the box mean kept is dominated in our run at N = 2-3
and after N = 7 by the uniform residual of the background step (scope entry 0; a flat 3e-14 at late
times); it belongs to our time integration of the background with Z4c (A11 and the step), not to the
noise. With the box mean removed the panel has P1's shape. Differs (3): P1's dense time sampling (its
curves are jagged from step to step); ours has 41 dumps.

### Fig. 5 (USR spectra, 256^3): REPRODUCED

Agrees: Delta[R^NR] from N = 0 to N_f in P1's layout (bins = lattice shells with more than 10 modes,
band = range in the bin), with the dashed MS expectation; the late spectra rise as k^4 to Delta = 1.0
at k_max (MS 1.016 at |n| = 64), and above k_max a second-order shelf near 1e-8 that falls at 2 k_max
(P1's Fig. 5 shows the same shelf). Measures at N_f (3395 shells): NR shell power over the
realisation's linear power within 5.0e-3 at every shell (rms 1.0e-3; 3.6e-4 for k <= k_max/2); NR
over MS within 3/sqrt(count) at 99.6 per cent of the shells; power above k_max at most 1.3e-7 of
Delta_MS(k_max) [VERIFIED, `fig/fig5_usr_spec.json`]. Differs: our top shells (|n| > 50) depart from
the linear spectrum by 1e-3 to 5e-3, A19 together with the second order at Delta ~ 1; P1's real-space
R^MS feels the stencil itself. P1's last spectrum is at <N> = 7.95 (legend, read), ours at N_f = 10.0
(both after the USR growth has ended).

### Fig. 6 (K, Kt and sqrt(3 Kt Kt/2) spectra): REPRODUCED (figure); S26 IN PART

Ours: three panels per scenario in P1's units ((100 H*/Mpl)^2 times the code spectra), at P1's times
as near as our dumps allow (USR: 0, 0.78, 1.29, 2.05, 2.80, 3.55, 5.53, 8.01, 10.0; P1: 0, 1.31, 1.95,
2.59, 2.9, 3.53, 5.43, 7.95). The Kt panel is the invariant Kt_ij Kt^ij = At_ij At^ij (P1:564): USR
from the kt_version-2 passes E-20261124-141807-8352509 and E-20261124-172949-8b2255b (N = 8.01), SR
from the first version times <chi>^2 (exact to second order where delta chi/chi ~ 1e-4; JOURNAL entry
2 for the defect of version 1). Q = sqrt(3 Kt Kt/2) was the invariant in both versions (identical
values, entry 6).
Agrees, SR: Delta[K] reaches the flat 1e-19 (P1 Fig. 6a, read: the same level) and freezes (N_f over
N = 5.34: 0.998 median); Delta[Kt] peaks at the crossing and decays (N_f over N = 4.39: 2.8e-5); median
over injected shells of Kt/K: 0.39 (N = 0.5), 1.1-1.4 (N = 2-3.4), 1.1e-4 (5.34), 4.4e-8 (8.10); Q
below K at 99.9 per cent of the injected shells at N = 3.91 and at all from N = 4.39 (Q/K 1.5e-9
median at N_f) [VERIFIED,
`fig/fig6a_sr_Kspec_P256v6.json`]. USR: Delta[K] decays by 7e8 (median over shells, maximum to N_f,
1.41e-9); Kt/K median 0.46 (0.78), 1.1-1.2 (2.05-3.55), 3.3 (5.53), 1.6e-2 (8.01), 3.6e-6 (10.0); at N
= 8.01 the median Delta[Kt] is 6.5e-32, P1's curve at 7.95 about 3e-32 (P1 Fig. 6b, read) [VERIFIED,
`fig/fig6b_usr_Kspec.json`]. So P1:570 holds in ours: in SR the anisotropic power is negligible after
the crossings, in USR K decays as well and Kt is comparable with it (or above it) through the USR phase.
Differs: (1) after the USR phase our hierarchy comes back: the fraction of injected shells with Q
below K is below 0.2 for 0.26 <= N <= 3.05, 0.23-0.64 for N = 3.3-5.0, 0.72-1.0 for N = 5.3-6.3,
0.34-0.68 for N = 6.5-7.0, and 0.98-1.0 from N = 7.27 to N_f (41 dumps of 130628-6790851), where Q/K is 9.4e-7 (median); P1's "not present in
the USR case" (P1:572) is true of ours up to N of about 7, the end of P1's figure lies at the turn
(our Q/K median at 8.01 is 4.2e-3). (2) At matched times before the end, our Kt and Q are below P1's by
about 3-10 (N about 5.5, read), as expected for P1's larger real-space amplitude (Fig. 4); at 8.0 the
two agree within a factor 2 (read). A11 (Z4c) and A18 (level 0) act at second order on Kt and Q
[JUDGEMENT].

### Fig. 7 (spectral convergence, SR, k_max/dk = 8): REPRODUCED

Ours: |1 - Delta_NR/Delta_lin| per shell at N_f, Delta_lin the realisation's linear spectrum (P1's
values for N = 256, 1e-7 to 3e-6, are far below cosmic variance, so P1 too compares with its own draw
[JUDGEMENT]). Agrees: monotone convergence; max over the 44 shells 3.2e-3 (N = 32), 6.2e-5 (64), 1.0e-6
(128), 3.7e-7 (256), medians 4.2e-4, 7.5e-6, 1.8e-7, 6.3e-8; the curves rise with k as P1's do; P1's N
= 32 and 64 curves (P1 Fig. 7, read: about 1e-4 to 1e-2 and 5e-6 to 1e-4) are where ours are; our 256
curve (5e-9 to 3.7e-7) lies at or below P1's (read: about 1e-7 to 3e-6) [VERIFIED, `fig/fig7_fig8.json`,
CL256S from pass E-20261124-213029-e937f69]. Differs: (1) the order is about 6 up to 128 (the
stencils), then 1.5 from 128 to 256: below |n| of about 4 the 128 and 256 curves lie on each other at
1e-7 to 4e-7 (the maximum of both at the second shell), and the per-mode relative rms is 7.1e-7 at
128 and 6.7e-7 at 256. A floor that does not move when dx and dt both halve is neither the stencils
nor the time step; its cause is not established [TO VERIFY: the second order of the field is a
candidate, which a run at half the noise amplitude would test]; above |n| = 4 the 256 curve keeps
falling (up to 30 below 128 at the top shells). P1's convergence also slows (about order 3 from its
figure, read); its 128 curve is about ten times above ours [JUDGEMENT: A19, P1's real-space MS
reference carries its own stencil error].

### Fig. 8 (constraint convergence): IN PART (shape and convergence as P1, levels below P1's)

Ours: record means <|H|/[H]> and <|M|/[M]> against e-folds for N = 32, 64, 128, 256 (both scenarios;
USR with the box mean of H removed as a thin line; 256 from the joined records of CL256S and CL256U).
Agrees: the early plateau set by the second order of each kick, the same for N = 64, 128 and 256: the
median over N in [0.5, ln 8] of the time-matched ratio (finer over coarser) is 0.99 to 1.17 from 64 to 128 and 1.03 to 1.12
from 128 to 256 (SR H, SR M, USR M, USR H - <H>); the decay after the entry (end over entry end at 256:
3.5e-3 SR H, 1.9e-2 SR M, 5.2e-3 USR H - <H>); the late rise of |M|/[M] in USR (2.8e4 over its value
at the end of the entry) (P1:748-750); N = 32 sits above with the truncation error during the entry
(time-matched 32 -> 64: 2.43 SR H, 0.19 SR M, 0.35 USR M, 1.2/1.5 H - <H>, in log2) [VERIFIED,
`fig/fig7_fig8.json`]. Correction (JOURNAL entry 11): the "orders of the entry maximum 32 -> 64" given
here before (4.15, 3.25, 4.10, 3.45) were not convergence orders: the entry maximum of the 64-256 rungs
is the first record after N = 0.05 (the decaying initial transient; 256 samples it earlier, which is
why its maximum is 1.13-1.47 times 128's), while that of the 32 rung sits at the window's upper edge
on its truncation hump. Only the USR column with the box mean kept (the background residual, maximum
at N = 2.07 at every N) gives a clean order: 4.10, 4.05, 4.03, with 1.986e-11 at 256 against USF256's
1.973e-11 (same steps). Differs: (1) levels: our SR plateau of <|H|/[H]> is about
5e-13 against P1's about 2e-11 (P1 Fig. 8a, read), of <|M|/[M]> 5e-6 against 1.5e-5: H/[H] is second
order and M/[M] first order in the amplitude, so P1's larger real-space amplitude (Figs. 2, 4) predicts
factors of about 12-16 and 3.5-4, near the 40 and 3 seen; A11 (Z4c against BSSN) changes the level of
H by factors of order one [JUDGEMENT]. (2) Our USR <|H|/[H]> with the box mean kept is the uniform
residual of the background step (fourth order in dt: entry maxima 9.2e-8, 5.4e-9, 3.2e-10, 2.0e-11 for
32-256, order 4.0-4.1); P1's USR curves do not show it [TO VERIFY whether P1's background step error is
smaller or removed]; with the box mean removed our USR curves have P1's shape. (3) Our M order 32 -> 64
was quoted as 3.3 (SR) and 3.5 (USR); by the time-matched measure the noise part of both constraints
converges from 32 to 64 at order 0.2 to 2.4 and not at all from 64 on (second order of each kick), so
scope P6(a)'s "order 4-6" holds only for the background residual. (4) After the entry the 256 curves
level off above 128's in SR <|M|/[M]> (8e-8 against 3e-8) and USR <|H|/[H]> (4e-14 against 2e-14):
floors of the normalised constraints once the violation has decayed, where P1 says the test loses
meaning (P1:750) [JUDGEMENT; not tested].

### Fig. 9 (ablation of the stochastic backreaction): IN PART

Ours: level 2 and level 1 against level 0, all three with the mode equation on the mesh (AL runs,
branch build core/noise-level2 at 6ca93cba, decision 0031; the Fable review of the branch says the six
runs stand, decision 0032 item 4), same seed, per injected shell (more than 10 modes) at N_f; beside
it the controls; and SR at t = 7.504 (N = 7.19) (`fig9_ablation_sr_t75.png`). AL2S reached t = 8.5 in
its continuation E-20261124-131359-49afe29 (joined, JOURNAL entry 11).
Agrees: USR level 2 - level 0 (orange) scatters around zero (52 per cent of shells positive) with rms
1.0e-4, rising with k from about 1e-5 to 3e-4 (max 7.0e-4 at |n| >= 56): the magnitude and the rise of
P1's orange curve (P1 Fig. 9, read: about 1e-5 to 1e-3). SR level 2 - level 0 at N_f (t = 8.5): rms
over |n| <= 32 1.5054e-5, max 7.93e-5 at the lowest shells (|n| <= 16), 49.7 per cent positive,
falling toward the cut (top over bottom median 0.51), per-mode relative rms 2.2e-4; the same to four
digits as at t = 7.5 (frozen after the last injection): P1's red curve (read: about 5e-5 at k_min
falling to 1e-6..1e-5) and P1:520 ("<~ 1 per ten thousand for all scales") [VERIFIED,
`fig/fig9_ablation.json`, `fig/fig9_ablation_sr_t75.json`; ablation P-A1, r20 part, PASS at N_f]. Level 1 - level 0
(blue SR, green USR) rises smoothly from about 5e-10 at k_min to about 5e-7 at k_max, one sign over 90
per cent of the shells: the shape of P1's green curve (read: 1e-9 to 3e-6); P1's SR level-1 curve
(blue) stays near 1e-9 to 1e-8 where ours reaches 6.6e-7. The released level 1 on shells (RL1, UL1)
against the released level 0 gives the same 6.6e-7 / 8.0e-7, so the level-1 shift does not come from
the mesh mode equation. Controls: released level 0 on shells against level 0 on the mesh differs by up
to 1.3e-2 (SR) and 1.7e-2 (USR) at the top shells, rising as the stencil symbol (A19), which is why
decision 0031 compares the levels on the mesh. Records of levels 1, 2 within 5.4e-4 of level 0 at
every cycle (SR 1387, USR 1703) [VERIFIED, `fig/fig9_ablation.json`]. Differs: (1) P1:520's bound is not met by
the USR level 2 above |n| of about 32 (and is not met by P1's own orange curve as read), so P1's text
and P1's figure disagree; ours agrees with the figure. (2) Our SR level 1 is 20-60 times above P1's
blue curve at the top shells (request to core). (3) The t = 0 slices of levels 1 and 2 differ from
level 0 in the last bits (at most 4.4e-16 absolute, 7.2e-10 of the perturbation range, in phi, Pi,
chi, K; metric and At identical) [VERIFIED, `bitcheck_ablation.json`, `bitcheck_ablation75.json`].

### Sign flip (P1:541, no figure): IN PART

`fig_signflip.png`: flipping the sign of the Pi kick. USR (U256nc against U256ap, 613 common record
lines to N = 3.63): <|H|/[H]> 1.9e3 to 8.0e3 (median) times the proper run, <|M|/[M]> up to 0.50; SR
(RNC256 to t = 4.5, N = 4.39, against the joined RSF256 record, 735 common cycles): ratio at least
1.39e3 (median 1.06e5) over N in [0.5, ln 64], the minimum at N = 4.16 where the proper run's H rises
with the last crossings; <|M|/[M]> up to 0.216 [VERIFIED, `fig/fig_signflip.json`; scope P3 PASS].
P1: H/[H] ~ 1e-5, M/[M] ~ 1: ours shows the first order (H/[H] up to 9.9e-8 and 1.3e-7, three to five
decades above the proper runs; M/[M] of order 0.2-0.5). Our H/[H] is lower than P1's "~1e-5" by about
1e2, consistent with the amplitude factor (Fig. 4) only in part [JUDGEMENT]. The same json carries the
proper SR run's record maxima over N <= ln 64 (scope P2): <|H|/[H]> 3.43e-11 (band 3e-11 to 1e-10,
PASS), <|M|/[M]> 1.18e-4 (band 3e-4 to 5e-4, FAILED as written: both maxima are at the window's edge,
N = 4.158, still rising; 2.72e-4 by N = 4.39; JOURNAL entry 12).

## 3. Statements of the map (analysis rows, and the run rows that feed the figures)

| # | P1 line | Statement | Ours (measure, run) | Verdict |
|---|---|---|---|---|
| S3 | 520, 790 | level 2 against 0: detectable, <~ 1e-4 in the power at all scales | USR: rms 1.0e-4, max 7.0e-4 (top shells), detectable (per-mode rms 3.0e-3); SR at N_f: max 7.9e-5, rms 1.1e-5, per-mode rms 2.2e-4 (`fig9_ablation.json`; the same at t = 7.5) | IN PART (SR within 1e-4 at every shell; USR above 1e-4 at the top shells, as P1's own figure) |
| S4 | 522 | quadratic: modes enter for about 3.5-4 e-folds | delta phi/phi_b reaches 95 per cent of its final 68 per cent width at N = 3.91; R^NR at 3.44 (P256v6) | REPRODUCED |
| S7 | 532 | inflection: entry of all modes within ~4 e-folds; double growth of the phi contrast, none in K; decay for 2 <~ N <~ 3, growth 3 <~ N <~ 4 | delta phi/phi_b 68 per cent: 8.0e-6 (N = 2.3), 2.9e-6 (3.05), 4.7e-6 (4.5); delta K/K_b peaks at 1.55 and decays by 5e5 (USF256) | REPRODUCED (shape and timing; amplitude see Fig. 4) |
| S8 | 534 | USR from N ~ 3.5 until ~ 8 | eps2 > 3 from N = 2.523 to 6.550 (box means of M64U = Friedmann within 1e-5) | REPRODUCED as P1's Fig. 1 shows it; P1's text is about one e-fold later than its own Fig. 1 (scope errata) |
| S9 | 534 | after the plateau (eps1, eps2) ~ (0, -2.8e-2); R freezes | eps1 = 1.008e-12, eps2 = -0.02760 at N_f (M64U); R^NR 68 per cent width constant to 5e-4 from N = 9 (USF256) | REPRODUCED |
| S10 | 534 | R^NR ~ 10 for the furthest outliers | max \|R^NR\| = 4.57 at N_f (USF256, 1.7e7 cells; 5.1 times the 68 per cent width, Gaussian) | NOT REPRODUCED in our realisation and normalisation (Fig. 4, factor about 4) |
| S11 | 534 | delta Pi/Pi_b relatively large at late times (inflection), unlike quadratic | 1.24e-2 (USR, N_f) against 2.8e-9 (SR, N_f) | REPRODUCED |
| S12 | 536 | Delta[R] up to ~0.1-1; excellent agreement with the linear spectrum at complete overlap | Delta(k_max) = 1.0 (MS 1.016); NR/linear within 5e-3 at every shell, 3.6e-4 for k <= k_max/2 | REPRODUCED |
| S13 | 539 | noise in R of maximum amplitude ~1e-5 in its entry phase | SR: 68 per cent half-width of R^NR 1.6e-5 to 2.3e-5 during the entry, max over cells 1.1e-4 (P256v6) | REPRODUCED (reading "~1e-5" as the typical amplitude) |
| S14 | 539 | H/[H] at the next order (~1e-10) in both scenarios, then damped | USR: per-cell 99th percentile <= 2.4e-11, box mean with H0 removed <= 2.9e-12 (record), decays to 1e-15; SR: record entry plateau 5e-13 (C64S, C128S); SR per cell at 256^3 pending | IN PART: second order and damped, yes; our level 10-100 below P1's ~1e-10 (amplitude, A11); SR per cell PENDING (RSF256, queue q0034) |
| S16 | 541 | flipping any sign of the noise gives first order: H/[H] ~1e-5, M/[M] ~1 | USR (U256nc, Pi sign): H ratio over the proper run >= 1.9e3, M/[M] up to 0.50; SR (RNC256 to t = 4.5, N = 4.39): ratio >= 1.39e3 (median 1.06e5), M/[M] up to 0.216 | IN PART (first order shown in both; H/[H] 1e2 below P1's) |
| S18 | 541 | inflection: \|M\|/[M] later around 1e-2 | late 68 per cent band 8.4e-4 to 3.2e-3, record mean 2.5e-2 at its maximum (N = 6.6) | REPRODUCED within the amplitude factor (Fig. 4) |
| S19 | 543, 746-752 | positive convergence of constraints and spectra (no orders printed) | spectra: orders 5.7 (32 -> 64), 5.9 (64 -> 128), 1.5 (128 -> 256, a floor near 1e-7 at the lowest shells); constraints during the entry, time-matched: 32 -> 64 decreasing (log2 0.2-2.4), equal within 17 per cent from 64 to 256 (second-order plateau); the background residual of USR at order 4.0-4.1 | REPRODUCED (32-256) |
| S21 | 748-750 | early plateau, decay after entry, test loses meaning later | Fig. 8 at 32-256 | REPRODUCED (32-256) |
| S22 | 752 | spectra converge toward MS with N | Fig. 7: 3.2e-3, 6.2e-5, 1.0e-6, 3.7e-7 | REPRODUCED (32-256; floor at the lowest shells, cause open) |
| S24 | 570 | K perturbations freeze (SR), decay (USR) | SR 0.998 of the N = 5.3 value at N_f; USR down by 7e8 from the maximum (median 1.41e-9) | REPRODUCED |
| S25 | 570 | anisotropic and isotropic comparable at first, anisotropic decays after crossing (SR); in USR K decays too and all terms of K_ij are of similar magnitude | SR Kt/K median 0.4-1.4 before N = 3.4, 1.1e-4 at 5.34, 4.4e-8 at N_f; USR Kt/K 0.46-3.3 for N = 0.78-5.53, 1.6e-2 at 8.01 | REPRODUCED (USR "similar magnitude" through the USR phase; 1.6e-2 at its end) |
| S26 | 572 | sqrt(3 Kt Kt/2) subdominant for most, not all, times; no such hierarchy in USR | SR: Q < K at all injected shells from N = 4.39 (99.9 per cent at 3.91; Q/K < 6e-9 at N_f), at <= 39 per cent before 3.44; USR: Q below K at <= 64 per cent of shells for 0.26 <= N <= 5.0 and 6.5-7.0, at 72-100 per cent for 5.3-6.3, at >= 98 per cent from 7.27 (Q/K 9.4e-7 at N_f) | IN PART (no USR hierarchy for most of the USR phase; it returns after N about 7) |

## 4. Ledger (registered runs this package made; all on processors, no card time)

| Run id | What | Numbers it carries |
|---|---|---|
| E-20261124-130628-6790851 | dump pass of USF256 (41 dumps) + bit check against U256ap | Figs. 4, 5, 6b (K, Q, all-dump measures); scope P1 (USR), P2 (USR per cell), P7 |
| E-20261124-133251-42e8aab | dump passes of P256v6 (18 dumps), AL0S/AL1S/RL1, AL0U/AL1U/AL2U/UL1/U256ap (t = 0, N_f), C32-C128 S/U; seven bit checks | Figs. 2 (fields), 3, 6a, 7, 9 (USR, level 1, controls); P-A2, P-A3, scope P4, P6 (a, c) |
| E-20261124-141807-8352509 | USF256 at the Fig. 6b dumps with the invariant Kt (kt_version 2); AL0S/AL1S/AL2S at t = 7.5; bit check AL2S t = 0 | Fig. 6b (Kt), Fig. 9 SR at t = 7.5 |
| E-20261124-172949-8b2255b | USF256 dump 32 (N = 8.01), kt_version 2 | Fig. 6b at N = 8.01 (R5) |
| E-20261124-172426-4780cbc | figure run 1 (`make_figs.py`, before the layout fixes) | R1: the test numbers of entries 2-3, now registered |
| E-20261124-173117-51c289f | figure run 2 (Fig. 6b at 8.01, Kt/K medians, layout fixes) | R5-R7 |
| E-20261124-173254-420115f | figure run 3 (Fig. 1 ticks); jsons byte-equal to run 2 | Figs. 1-6 (byte-equal in the runs below) |
| E-20261124-213029-e937f69 | CL256S dump 17; AL2S dump 17 with c_NR; bit check of RSF256 against P256v6 at t = 0, 4.0, 5.0 | Fig. 7 at 256, Fig. 9 SR level 2 at N_f (P-A1), scope P1 (SR so far) |
| E-20261124-213400-37465c2 | figure run 4 (continued runs; `joins.py`) | J, F7, F8, P3, P-A1 (JOURNAL entry 11) |
| E-20261124-213532-3f00681 | figure run 5 (Fig. 7 legend); jsons byte-equal to run 4 | as run 4 |
| E-20261124-213739-9776185 | figure run 6 (scope-P2 maxima in `fig_signflip.json`); all else byte-equal to run 5 | every PNG and json in `fig/` |

Scripts: `figures/` at the commit in each manifest; `figures/make_figs.py` makes every figure from the
pass directories. Fig. 1, Fig. 8 and the sign-flip figure read the records directly (no pass).
Record-based numbers of scope P2 (USR): max <|H - <H>|/[H]> = 2.885e-12, max <|M|/[M]> = 2.519e-2
(USF256 record; the same in U256ap), read with `figlib.read_con_joined`. The records of the continued
runs are read from the joined files of the join check E-20261124-212343-7e9c4b2 (package
repro/continue; `figures/runs.py` JOINED); `figures/joins.py` checks them against our own join of the
pieces in every figure run.

## 5. What completes the PENDING rows

Only RSF256 is still out. It is joined to cycle 895 (t = 5.49) from its original
E-20261123-035925-8439d79 and three continuations (E-20261124-130529-da8c917, -201031-4c41e7b,
-202134-0b1ce0c); its fourth continuation is queue entry **q0034** (label `rsf256-cont`, priority 0,
from 0b1ce0c's `rst/sr.00002.rst`). It completes: Fig. 2 constraint panels; Figs. 3 and 6a from RSF256
itself; scope P1 (SR) at t = 8.5 (bit check against P256v6 dump 17); scope P2 per cell for SR and the
record maximum over the whole run; S14 SR per cell.

Steps once q0034 has ended (repro/continue/HANDOFF.md, "RSF256: queue entry q0034"): (1)
repro/continue finishes the run, appends it to `conts.json` and reruns its join check (a new run id);
(2) here: append the run id to `CONTINUED["RSF256"]` and set `JOINED["RSF256"]` to the new join run in
`figures/runs.py`; (3) registered pass `runs.py rsf256` (RSF256 dump 0 and every dump of the last
continuation, the dumps 00000-00034 are spread over the original and four continuations: read the
joined `RSF256.dumps.tsv` and add a group per directory if `RSF256c` alone does not hold 1-34; bit
checks at t = 4.0 and 8.5 are in the group); (4) figure run as E-20261124-213739-9776185 plus
`--rsf256 <pass>`; copy into `fig/`, look at Figs. 2, 3, 6a, judge entry 1 F2 (e) for SR and scope P2
per cell, replace the PENDING rows.

## 6. Requests

- Lead of E (card time, if the floor matters for the note): the floor of Fig. 7 at 256 (per-mode
  relative rms 6.7e-7, the same as at 128) would be tested by CL256S at half the noise amplitude
  (`noise_mode_scale = 0.5`, about 0.5 card-hours): if it is the second order of the field it halves.
- Lead of E and repro/note: the Fig. 8 "orders 32 -> 64" quoted before this pass (4.15, 3.25, 4.10,
  3.45) are withdrawn (JOURNAL entry 11); use the time-matched plateau ratios of `fig/fig7_fig8.json`
  (`orders_time_matched`). Scope P6(a) ("order 4-6 from 32 to 64") holds only for the USR background
  residual; please note this in repro/scope's journal when it is next edited.
- Lead of E: copy `CARD_COSTS.md` into the second table of `../scope/CARD_PLAN.md` (this package may
  not edit repro/scope); correct `../scope/SETUP_AUDIT.md` item 4 and the SR deck header: tlim = 8.5
  is N* + 8.10 e-folds, not 8.04 (Fig. 1, own Friedmann integration and the M64S record).
- core: (1) the t = 0 dumps of backreaction levels 1 and 2 differ from level 0 in the last bits (up to
  4.4e-16 absolute, 7.2e-10 of the perturbation range, 36-8140 cells, in phi, Pi, chi, K only; release
  level 1 and branch levels 1, 2): please confirm that it is the box-mean background of the slice
  (round-off), not a level-dependent slice. (2) Level 1 changes the final power by a smooth, one-signed
  5e-10 (k_min) to 6.6e-7 (k_max) in both scenarios and both builds (RL1/UL1 release on shells,
  AL1S/AL1U branch on the mesh), the same at t = 7.5 as at N_f: larger than the 1e-8 predicted from box
  means equal to Friedmann within 1e-11 (ablation P-A1); an explanation is wanted before the note
  quotes level 1 against P1's (P1's quadratic level-1 curve is near 1e-9-1e-8).
- Note (repro/note): P1's one-point bands (Figs. 2, 4) are 2.3-4 times the width that P1's own spectra
  (Figs. 3, 5) and the linear normalisation imply, in both scenarios; our runs agree with the spectra.
  Say so as a judgement from reading P1's figures, not as P1's error; asking the authors is the
  group's step (nobody outside is contacted). P1:572 "no such hierarchy in the USR case": true in ours
  until N of about 7, with Q/K back to 1e-6 by N = 10, beyond the end of P1's Fig. 6b (7.95).
