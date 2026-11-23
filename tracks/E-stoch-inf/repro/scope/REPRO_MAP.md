# Map of arXiv:2512.14649 to our runs (package repro/scope, 2026-11-22)

P1 = `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex` (v2, 791 lines, read whole). Every figure,
table and quantitative statement of P1, with its line, what P1 shows or states, which registered run
of ours already reproduces it (run id, script, figure) or what is missing: **A** an analysis of
existing outputs only, **R** a new run (queued here, `queue.txt`), **O** an option of the code
(request in `outbox_draft/`). Labels: [VERIFIED] read at the locator or measured by the named run,
[JUDGEMENT], [TO VERIFY]. "Release" = card build core-v0.6; "s2"/"s3" = core's tested branches
core/scalar-2 a58e95b / core/scalar-3 5cc2821 (scouting, decision 0013). Seed A = rng_seed 20261115.
Agreement is statistical (the authors' code and realisations are their own; decision 0028 item 2):
against the linear (Mukhanov-Sasaki, MS) solution and the numbers P1 prints. Nothing is read off P1's
figures.

New runs of this package (pending at the time of writing; ids in `CARD_PLAN.md`):
SMALL (M64S, M64U, C32S-C128S, C32U-C128U), USF256, RSF256, UL1, RL1, RNC256, CL256U, CL256S.

## 1. Figures

| Fig. (label, P1 line) | What P1 shows | Existing runs of ours | Missing / new | Reader for repro/figs |
|---|---|---|---|---|
| 1 `fig:MeanRolls` (428-442): (a) quadratic, (b) inflection, files `64quad_back__MeanRolls`, `64usr_back__MeanRolls` | V, eps1, eps2 against e-folds from the box of a 64-cell NR run and from Friedmann; "perfect agreement"; Mpl = 100 | SR: Q64p (64^3, nmax2 = 256, to t = 8.5) in job C E-20261115-172625-416fec0 (s2); A1 box means within 2.0e-12 (phi, P256) [VERIFIED, ladder final E-20261115-194633-9e04ed8]. USR: U64p (64^3 but nmax2 = 64) in group 1 E-20261120-222621-ba66218 (s3); U-A0 dN 4.2e-7, U-A1 <Pi> 2.5e-5 [VERIFIED, usr README card table] | **R** M64S, M64U (release, 64^3, k_max = N/4 = 16 dk as in P1:512 [JUDGEMENT: P1 does not state k_max of its 64-cell runs]); **A** V, eps1 = 4 pi <Pi>^2/H^2, eps2 = 6 + 2V'/(H<Pi>) - 2 eps1 from `.sf.con.hst` (<phi>, <Pi>, <K>) against the references E-20261115-135532-3f958a1 (SR), E-20261119-143905-f2bcde3 (USR) | `nrpic.scalar_field.read_con_history`; `usr/scripts/card_lib.py` (records) |
| 2 `fig:quad_contrast` (444-449), `256quad_back__Contrastfields` | 68/95/99/100 percentile contours over the lattice against time of the contrasts of phi, Pi, K, of R^NR, and of \|H\|/[H], \|M\|/[M] (quadratic, 256^3) | P256v6 E-20261121-202935-31520bc (release) and P256 E-20261115-172618-f948386 (s2): 17-18 dumps (every 0.5) with phi, Pi, chi, gt_ij, K, At_ij, H, M_i, E, but no [H], [M] per cell; records every cycle give mean and max of \|H\|/[H], \|M\|/[M] | **R** RSF256 (35 dumps every 0.25 with Hmag, Mmag); **A** percentiles per dump; R^NR per cell from chi, gt_ij, phi (ladder extraction, SPEC 9) | `ladder/scripts/ladder_lib.py` (reader, R^NR), `usr/scripts/card_lib.py` (sequential reader) |
| 3 `fig:quad_spec` (451-456), `256quad_back__spec_panels` | binned Delta = k^3 \|.\|^2/(2 pi^2) of R^NR (solid) and R^MS (dashed) from the first to the last time; bins with more than 10 modes; contours = range in the bin | P256v6 / P256 dumps and lockstep `.modes`; A2 per mode 1.21e-4, shell ratios within 1.9e-4 [VERIFIED, ladder final]; second seed P256s2 E-20261121-032828-fe18c5f | **A** binned spectra at every dump of P256v6 (or RSF256), bins with > 10 modes, band of the bin | `ladder/scripts/ladder_analysis.py judge` (shell spectrum) |
| 4 `fig:usr_contrast` (458-463), `256usr_back__Contrastfields` | as Fig. 2 for the inflection case | U256ap E-20261121-211214-0377aab (release, 21 dumps, no [H], [M] per cell); scouting U256 E-20261121-075255-8cf90e7 (s3) | **R** USF256 (41 dumps with Hmag, Mmag); **A** as Fig. 2 | `usr/scripts/card_lib.py` |
| 5 `fig:usr_spec` (465-470), `256usr_back__spec_panels` | as Fig. 3 for the inflection case | U256ap and its pair U256am E-20261121-214629-da64fb7; U-A2' (odd part per mode at N_f) judged by the lead in batch 10a (g2prod analyses E-20261123-014858-8e72d4c, running); scouting pair 1.09e-4 per mode [VERIFIED, STATUS] | **A** binned spectra per dump | `usr/scripts/analyse_cards.py --group u256`, `card_lib.py` |
| 6 `fig:specAK` (549-561), `256quad_back__Aij_spec_panels`, `256usr_back__Aij_spec_panels` | binned spectra of K, of K-tilde (Kt_ij(k) Kt^ij(k)*), and of sqrt(3 Kt_ij Kt^ij/2), both cases, first to last time | dumps of P256v6 and U256ap hold K, At_ij, gt_ij, chi (Kt_ij = At_ij/chi with A_ij = X Kt_ij, P1:676) | **A** only (new runs RSF256/USF256 give denser times); no code option needed | own spectra of At_ij/chi on the hemisphere (ladder_lib mode coefficients) |
| 7 `fig:specConvergence` (754-758), `spec_conv` | \|1 - Delta[R^NR]/Delta[R]\| for N = 32, 64, 128, 256 at k_max/dk = 8 (quadratic) | L32p E-20261115-172636-ce98836 (processors, s2), L64p, L128p (job C, to 8.5), L256p (job B E-20261115-172629-312a82c, only to t = 4.5); A2 per mode 8.8e-5 (L32) to 1.7e-6 (L256) [VERIFIED, ladder README] | **R** C32S, C64S, C128S (SMALL), CL256S (to N_f) on the release build; **A** shell ratios to MS per N | `ladder/scripts/analyse_all.py`, `verdicts.py` |
| 8 `fig:Convergence` (761-773): (a) `quad__convergence`, (b) `usr__convergence` | <\|H\|/[H]> and <\|M\|/[M]> against time for N = 32-256, k_max/dk = 8 | SR: records of the rungs above; odd-part orders 4.2-5.8 (H), 5.6-5.9 (M) [VERIFIED, ladder A5]. USR: U64p, U128p (+-, halving) of group 1 (s3); orders 5.5-5.7 (H), 5.2-5.9 (M) for cN 2-4 [VERIFIED, usr README] | **R** C32U, C64U, C128U (SMALL), CL256U (USR 32 and 256 do not exist); SR on release for one executable | `nrpic.scalar_field.read_con_history` (columns 4, 7) |
| 9 `fig:ablationback` (777-781), `stoch_ablation` | relative difference of the R^NR power spectrum between levels 2 and 0, and 1 and 0, both cases, 256^3, same seed | level 0: P256v6, U256ap | **R** RL1, UL1 (`noise_level = 1`); **O** level 2 not implemented (`athenak/src/scalar_field/scalar_field_noise.cpp:162-166` refuses it): `outbox_draft/core_noise_level2.md` | shell spectra at N_f of L1 against L0 |

## 2. Table

| Table (P1 line) | Content | Ours | Status |
|---|---|---|---|
| I `tab:scenarios` (400-426) | potentials, parameters, how the initial conditions are fixed, N* - N0 ~ 5 / ~ 3, N_f - N* ~ 8 / ~ 10 | `SETUP_AUDIT.md` items 1-4; derived values reproduced by two integrators (SCOPE 2: runs E-stoch-inf-20261115-122806-ef0d039, E-20261115-135532-3f958a1) | reproduced [VERIFIED]; integers 5, 3, 8, 10 chosen for the "~" (SCOPE 2) [JUDGEMENT] |

## 3. Quantitative statements of the text

| # | P1 line | Statement | Ours (run, number) | Missing |
|---|---|---|---|---|
| S1 | 509-511 | modes k = dk sqrt(a^2+b^2+c^2), dk = 2 pi/L; L k_sigma* = 2 pi | same lattice (`noise_nmax2`, box 2 pi/sigma) [VERIFIED, SETUP_AUDIT 6] | none |
| S2 | 512 | k_max = N k_sigma*/4 (64 dk at N = 256) | nmax2 = 4096 in P256, U256ap [VERIFIED, decks] | none |
| S3 | 520, 790 | ablation: "detectable but <~ 1 per ten thousand relative change in power spectrum for all scales" (level 2 vs 0) | none yet | **R** RL1, UL1 (level 1 vs 0); **O** level 2 |
| S4 | 522 | quadratic: modes enter for about 3.5-4 e-folds (growth of the contrasts) | design value ln(k_max/k_min) = ln 64 = 4.16 (P1:716) | **A** entry span from W_n(t) of the lockstep `.modes` or from the contrasts of RSF256 |
| S5 | 522 | R freezes in the super-Hubble regime (quadratic) | A3 PASS: drift 1.4e-4 per e-fold = full MS within 1.8e-6, 1051 modes per rung [VERIFIED, ladder final E-20261115-194633-9e04ed8] | none |
| S6 | 522 | R^NR agrees with R^MS once the window has rolled (quadratic) | A2 1.21e-4 per mode (P256), shell ratios 1.9e-4 [VERIFIED, ladder]; release repeat P256v6 judged in batch 10a (E-20261123-015014-b4ecd4e, running) | none (Fig. 3 analysis A) |
| S7 | 532 | inflection: progressive entry of all modes with full amplitude within about 4 e-folds; double growth of the phi contrast, none in K; fluctuations added for N <~ 2 decay during 2 <~ N <~ 3; growth 3 <~ N <~ 4 | not measured | **A** contrasts of USF256 (or U256ap at 21 times) |
| S8 | 534 | USR from N ~ 3.5 until N ~ 8 | reference: eps2 > 3 from N* + 2.52 to N* + 6.55 [VERIFIED, run E-20261119-143905-f2bcde3, `usr/results/landmarks.csv`]; P1's text is about one e-fold later than its own Fig. 1 (SCOPE errata) | **A** the same landmarks from the box means of M64U and USF256 |
| S9 | 534 | after the plateau (eps1, eps2) ~ (0, -2.8e-2); R^NR freezes | reference at N* + 10: eps1 = 1.01e-12, eps2 = -0.0276 [VERIFIED, `usr/results/usr_reference.json` table_half_efold]; freezing U-A3 k <= 3 dk within 2.5e-6 (128^3) [VERIFIED, usr README] | **A** from the NR box means (P5 of JOURNAL entry 1) |
| S10 | 534 | R^NR reaches ~ 10 for the furthest outliers in real space | rms of W R at N_f 0.894 at 256^3 (lattice sum) [VERIFIED, usr README]; the maximum not measured | **A** max \|R^NR\| at N_f of U256ap / USF256 (realisation-dependent) |
| S11 | 534 | delta Pi/Pi_b relatively large at late times (inflection), unlike the quadratic case | not measured | **A** contrasts |
| S12 | 536 | Delta[R] up to ~ 0.1-1; excellent agreement with the linear spectrum at complete overlap | reference Delta_R at N_f 1.02e-5 (k = dk) to 1.017 (64 dk) [VERIFIED, `usr/results/usr_spectrum_Nf.csv`]; NR against MS per mode: U-A2' (g2prod, batch 10a) | **A** binned spectra (Fig. 5) |
| S13 | 539 | the noise in R has a maximum amplitude ~ 1e-5 in its entry phase | not measured | **A** max \|R^NR\| per dump of RSF256 |
| S14 | 539 | Hamiltonian: violation at the next order (~ 1e-10) relative to [H], both scenarios; then damped by inflation | SR record max <\|H\|/[H]> 4.7e-11-5.1e-11 [VERIFIED, ladder final2 E-20261121-025932-7a21f34]; USR 2.9e-12 (U256; SCOPE 4c U-A4'(c)) [VERIFIED as recorded there], i.e. 30 times below P1's order in USR [JUDGEMENT: P1 gives an order only] | **A** percentiles per cell (RSF256, USF256) |
| S15 | 540 | momentum: [M] is first order, a second-order violation in the entry phase | strict A4 FAILS in P1's set-up: the first-order (odd) part dominates from cN = ln(N/8) (P256: odd/even up to 25 time-matched); record max <\|M\|/[M]> 3.3e-4-4.0e-4 [VERIFIED, ladder README A4 rows]; strict A4 holds at >= 12.8 cells per shortest wavelength (a4res) | none (documented difference: P1:541 itself names the gradient resolution) |
| S16 | 541 | flipping any sign of the noise gives first order: H/[H] ~ 1e-5, M/[M] ~ 1 | SR NC64, NC128 (job C): H 4e4-1.5e5 times the proper run, M/[M] 0.20-0.22 [VERIFIED, ladder negative control]; L5 Pi-kick flip 4.4e5 [VERIFIED]; USR U256nc E-20261122-190341-0419be6 (judged in batch 10a) | **R** RNC256 (SR at 256^3); only the sign of the Pi kick can be flipped (`noise_pi_sign`) [JUDGEMENT: enough for "any sign"] |
| S17 | 541 | quadratic: at the last mode crossing \|M\|/[M] momentarily above second order (gradient resolution); a smaller k_max fixes it | consistent: A4 passes at k_max/dk = 8 from N = 128 and fails at k_max = N/4 [VERIFIED, ladder README A4] | none |
| S18 | 541 | inflection: \|M\|/[M] later around 1e-2 | record late 1.07e-2 (64^3), 2.47e-2 (128^3, 4.3e-2 at s = 1/2), 2.5e-2 (U256) [VERIFIED, usr README; SCOPE 4c] | none |
| S19 | 543, 746-752 | positive convergence of constraints and spectra; no orders printed | orders 4.2-5.8 (H), 5.6-5.9 (M) SR; 5.5-5.7, 5.2-5.9 USR (above the floor) [VERIFIED, ladder A5, usr README]; A6 temporal 3.93-4.08 | **R** SMALL + CL256S/U for the series of Figs. 7-8 on one build |
| S20 | 746 | physicality: \|H\|/[H] second order, \|M\|/[M] first order (P1:746 says "first order" where 540 says "second-order violation": [M] is first order, so \|M\|/[M] of a second-order \|M\| is first order) | as S14-S15 | none [JUDGEMENT: the two lines agree once the ratio is read as \|M\| / [M]] |
| S21 | 748-750 | early plateau of the constraint ratios (each kick violates at second order), exponential decay after the entry; the test loses meaning later | records of the ladder show the plateau and decay [VERIFIED, ladder fig/final] | **R** CL256S/U, SMALL for the four-N figure |
| S22 | 752 | spectra converge toward MS with N | A2 per mode 8.8e-5 -> 1.7e-6 for L32 -> L256 [VERIFIED, ladder README] | **R** as Fig. 7 |
| S23 | 756, 771 | k_max/dk = 8 gives about ln 8 ~ 2 e-folds of sourcing | nmax2 = 64 rungs [VERIFIED, decks] | none |
| S24 | 570 | K perturbations freeze in the quadratic case, decay in USR | not measured | **A** K spectra (Fig. 6) |
| S25 | 570 | anisotropic and isotropic powers comparable at first; anisotropic decays after horizon crossing (quadratic) | not measured | **A** |
| S26 | 572 | sqrt(3 Kt Kt/2) subdominant to the isotropic modes for most, not all, times; no hierarchy in USR | not measured | **A** |
| S27 | 488 | without the coarse-grained initial slice (W at t*), a detectable inaccuracy of the first low-k modes | our slice has W(t*) (`slice_window = true`); the control (homogeneous slice at N* with the kicks) not run | **R, optional** (not queued): `<problem> id = flrw` at N* with the same kicks, 64^3 |
| S28 | 496 | the scheme satisfies the constraints up to O(noise^2) | as S14-S15; L5 single kick: H second order, factor 3.99999-4.0000001 under halving [VERIFIED, ladder L5] | none |
| S29 | 711 | RK4 on the stochastic part converges like Euler-Maruyama; little impact if perturbative | A6: order 3.93-4.08 with frozen alpha_k (smooth in time) [VERIFIED, runs E-20261119-142317-c851f27, E-20261119-145230-ff0dff2] | none (SETUP_AUDIT 13) |
| S30 | 716 | N^(x) = ln(k_max/k_min) = ln(N/n) | ln 64 = 4.16 (n = 4) [VERIFIED by arithmetic] | none |
| S31 | 721 | N_T ~ N sigma/(2 pi theta) (N^(x) + Delta N) | SR 256^3, theta = 0.25: proxy 1310, measured 1386 steps (P256); USR proxy 1630, U256 1701 (tlim/dt) [VERIFIED, ladder cost row; SCOPE 8] | none |
| S32 | 727, 730 | at most one mode per step if theta < n sigma/(2 pi) = 0.64; sigma >= 1 never more than one with a sharp window | theta = 0.25 [VERIFIED, decks] | none |
| S33 | 506 | s = 5 "should not have an impact on the result in the late-time limit" | window scan L9 (s = 2.5, 5, 10; sigma = 0.5, 1, 2): spectrum at N_f window-independent within 1.9e-4 to k_max/2, 9.1e-3 to k_max; late constraint records depend on sigma (up to x21.7) [VERIFIED, window E-20261121-154733-0d1fbda] | none |

## 4. What cannot be reproduced as P1 did it

- Level-2 backreaction (P1:487, 783-788) is P1's production setting and is not implemented here; all
  our runs are level 0 (and level 1 in RL1, UL1). P1 bounds the effect by about 1e-4 in the spectrum
  (P1:520): our level-0 runs stand for P1's level-2 runs within that bound [JUDGEMENT]. Request:
  `outbox_draft/core_noise_level2.md`.
- P1's figures are of its own realisation; ours are seeds A (20261115) and B (20261116). One-point
  percentiles and outliers (S10) agree only statistically.
