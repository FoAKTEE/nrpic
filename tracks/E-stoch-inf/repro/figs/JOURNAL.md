# JOURNAL of package repro/figs (Track E, batch R2, 2026-11-24)

The figures of arXiv:2512.14649 (P1 = `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`, figures
P1:428-470, 549-561, 754-781) remade from our registered runs, in P1's layout and the project style
(`python/nrpic/figstyle.py`), and the analysis-only rows of `../scope/REPRO_MAP.md`. Inputs: the map,
`../scope/HANDOFF.md`, `../scope/SETUP_AUDIT.md` (the four set-up differences: item 3 Bunch-Davies
start of the SR high shells, item 11 Z4c instead of BSSN, item 18 backreaction level 0 instead of 2,
item 19 per-shell continuum mode equation instead of P1's real-space one), `../scope/CARD_PLAN.md`,
`../scope/JOURNAL.md` entry 1 (P1-P7), `../ablation/JOURNAL.md` entry 1 (P-T5, P-A1..A3). Predictions
are written here before each analysis runs; outcomes after, also when a prediction fails.

## Entry 0 (2026-11-24 05:05 PST): state of the runs at the start

- Every card run of `repro/scope` and `repro/ablation` is closed in its manifest (the sequencer closed
  them, `scratch/E-stoch-inf/repro_scope_seq/seq.log`, last line 2026-11-23 15:02 PST "nothing left to
  submit ... every run closed"). Ten completed: SMALL E-20261123-020704-2b99463, USF256
  E-20261123-021204-2f573ec, UL1 E-20261123-040126-2d0323c, RL1 E-20261123-040327-ccae634, T5SMK
  E-20261123-035724-b661081, AL2U E-20261123-153146-d965002, AL0S E-20261123-153347-18e7c21, AL0U
  E-20261123-164235-49b0945, AL1S E-20261123-183822-4abbcae, AL1U E-20261123-192948-348e2e5. Five closed
  as `failed` because their chains reached MAX_SEGMENTS before tlim (last record lines): RSF256
  E-20261123-035925-8439d79 at t = 0.387 (3 dumps), RNC256 E-20261123-045030-c20bcb3 at t = 0.712,
  CL256U E-20261123-065855-265732a at t = 4.77, CL256S E-20261123-090727-4b6e5a5 at t = 6.23, AL2S
  E-20261123-152119-38957ba at t = 7.53. They are continued by package `repro/continue` (beside this
  one); no `nrpic-run finish` is left to do here.
- Actual card costs (manifest `resources.gpu_hours`) are in `CARD_COSTS.md` of this package (the
  sequencer did not fill the second table of `../scope/CARD_PLAN.md`, which this package may not edit;
  request to the lead in README).
- The smoke check of the level-2 branch passed (`SMOKECHK` E-20261123-090718-6203c87, `verdict.json`:
  PASS, no fails).

## Entry 1 (2026-11-24 05:15 PST): predictions of the analyses, written before any of them runs

Quantities. Contrast of X: X/<X> - 1 per cell (box mean over the lattice of that dump). R^NR(x): the
linear extraction of `ladder/scripts/ladder_lib.py` / `usr/scripts/card_lib.py` (audit item 24) on the
whole lattice. Percentile bands: central 68, 95, 99, 100 per cent intervals (percentiles 16-84,
2.5-97.5, 0.5-99.5, min-max) [JUDGEMENT: P1:447 says "68, 95, 99 and 100 percentile contours"; the
central intervals reproduce the symmetric bands of its figures]. Spectrum: Delta = k^3 |X_k|^2/(2 pi^2)
= 4 pi |n|^3 |c_n|^2 in code units (c_n = N^-3 sum f e^{-i n.x}), binned on the lattice shells |n|^2 =
const, bins with more than 10 independent modes (hemisphere count) [JUDGEMENT: P1:454 "more than 10
realisations"; with this count the first bin is |n|^2 = 5, k = 2.12e-3 in P1's units, where P1's axes
begin]; line = bin mean, band = bin min to max (P1:454). Linear reference per mode: c_lin = L^-3/2 W(k,t)
R_k(t) alpha_n with R_k from the lockstep `.modes` file of the same dump (continuum k^2) and alpha_n from
Track E's own Philox (`noise/ref/philox_ref.py`). P1's units (Mpl = 100) for axes that carry units: k_P1
= |n| (H*/Mpl) 100, H*/Mpl = 9.4869151038149e-6 (SR, ladder_lib) and 9.36231877388068e-6 (USR,
`usr/results/usr_reference.json` T1.H_star); K-type spectra times (100 H*/Mpl)^2; V times 8 pi
(H*/Mpl)^2 1e8.

F1 (Fig. 1, M64S, M64U): scope P5 unchanged (SR |dV/V| < 1e-8, |d eps1/eps1| < 1e-6, |d eps2| < 1e-5;
USR |dV/V| < 1e-6, |d eps2| < 1e-2; eps2(N_f) = -0.0276 +- 0.002), against my own Friedmann integration
from (phi0, pi0) of the decks. Landmarks from the box means (S8): eps2 > 3 from N = 2.52 to 6.55 (the
reference, `usr/results/landmarks.csv`) within 0.05 e-folds each; eps1 minimum 9.7e-13 near N = 8.33
(S9; reference eps1_min 9.716e-13 at 8.331) within 1 per cent and 0.05 e-folds. Refuted by any value
outside.

F2/F4 (contrasts; USF256 now, RSF256 when continued, P256v6 meanwhile for the four field panels):
(a) reader check: my lattice means of |H|/[H] and |M|/[M] equal the record columns 4 and 7 at the same
cycle within 1e-6 relative (same definition, `.sf.con.hst` header). Refuted: a reader or definition
defect; the constraint panels are then withheld.
(b) one-point amplitude of R^NR at N_f: 68 per cent half-width = the linear expectation sigma_R =
sqrt(sum_shells count |R_k|^2/L^3) of the `.modes` file, which is 2.06e-5 (SR, P256v6 dump 17) and
0.894 (USR, USF256 dump 40), within 3 per cent (one realisation, about 1.1e6 modes); 100 per cent band
over the 68 per cent band between 4.5 and 6.5 (Gaussian over 1.7e7 correlated cells; P7: max between 3
and 8 in USR).
(c) SR: the 68 per cent band of delta phi/phi_b reaches 95 per cent of its final width between N = 3.6
and 4.6 (modes enter for ln 64 = 4.16 e-folds; P1:522 "3.5-4"); delta Pi/Pi_b collapses after the
entry (68 per cent width at N_f below 1e-2 of its maximum).
(d) USR: delta K/K_b rises during the entry and falls by more than 100 after N = 4 (P1:532); delta
Pi/Pi_b at N_f has a 68 per cent half-width above 1e-2 (P1:534 "relatively large"), R^NR grows
between N = 5 and 8 and is frozen after N = 8.5 (68 per cent width changes by less than 1 per cent
from N = 9 to N_f).
(e) constraints, per cell (USF256; RSF256 later): the 99th percentile of |H|/[H] stays below 1e-9 at
every dump (scope P2); max over cells of |M|/[M] reaches order 1 in USR after N = 4 (P1's figure shows
its top band near 1); the 68 per cent band of |M|/[M] in USR at late times between 1e-3 and 1e-1
(S18 "around 1e-2").
(f) bit identity (scope P1): USF256 and U256ap (E-20261121-211214-0377aab) at three common times (t =
0, 5.22, 10.44) agree bit for bit in phi, Pi, chi, K, gt_ij, At_ij; P256v6 against RSF256 likewise
once RSF256 has run. Refuted by any relative difference above 1e-12.

F3/F5 (spectra of R^NR): at N_f, per shell with more than 10 modes and |n| <= 64: (a) the shell mean
of the NR power over that of the realisation's linear power (same alpha_n) is 1 within 1e-3 (SR; ladder
A2 per mode 1.21e-4) and within 1e-2 (USR; usr pair 1.09e-4 per mode, but the top shells carry the
mode-equation difference of audit item 19 and the second order at Delta ~ 1); (b) against the MS
expectation Delta_MS = k^3 |R_k|^2/(2 pi^2) (P1's dashed line) the ratio scatters as cosmic variance:
|ratio - 1| < 3/sqrt(count) for at least 98 per cent of the shells; (c) above |n| = 64 the NR power at
N_f is at least 1e6 below Delta_MS(64) in SR (nothing is injected there; second order only) and at
least 1e2 below in USR (second order of an O(1) field). Refuted by any of (a), (b) outside.

F6 (K-type spectra, scope S24-S26): (a) SR: Delta[K] per shell (|n| <= 32) changes by less than 10
per cent between N = 5.5 and N_f (freezes); USR: falls by more than 1e4 between its maximum and N_f
(decays). (b) Delta[Kt] (sum over ij of |Kt_ij(k)|^2) falls by more than 1e2 after the crossing of
each shell in SR (between N = 4.5 and N_f, shells |n| <= 32). (c) sqrt(3 Kt Kt/2): at N_f its
spectrum is below Delta[K] by more than 1e2 at every shell |n| <= 64 in SR, and not in USR (within a
factor 1e2 of Delta[K] or above at most shells). Refuted by any of these; (c) is P1's own statement
(P1:572, "for most, although not all, times"), so a miss is recorded as a disagreement with P1.

F7 (scope P6(c)): max over shells |n| <= 8 of |1 - Delta_NR/Delta_lin| at N_f decreases monotonically
32 -> 64 -> 128 (-> 256 when CL256S is continued); below 1e-5 at 256. Here Delta_lin is the
realisation's linear spectrum (same alpha_n): P1's values (spec_conv) are far below cosmic variance,
so P1 too compares with the same draw [JUDGEMENT].

F8 (scope P6(a), (b)) unchanged.

F9 (ablation): repro/ablation entry 1, P-A1 (SR, needs AL2S), P-A2 (USR), P-A3 (controls), unchanged;
and scope P4 for RL1/UL1 against P256v6/U256ap (released level 0 on shells), unchanged.

Map rows answered here (`../scope/REPRO_MAP.md` section 3): S4 (c), S7-S9 (F1, (d)), S10 (P7), S11 (d),
S12 (F5), S13 (max |R^NR| over the dumps with N <= 4.2 in SR: between 4e-5 and 1.5e-4, i.e. the 100
per cent band of a 2e-5 field; P1 "~1e-5" read as the typical amplitude), S14 ((e) and P2), S16 (P3,
RNC256 when continued), S18 ((e)), S21-S22 (F7, F8), S24-S26 (F6).

## Entry 2 (2026-11-24 05:45 PST): outcomes of Fig. 1 and of the USR pass (Figs. 4, 5, 6b)

Runs: USR dump pass E-20261124-130628-6790851 (41 dumps of USF256 E-20261123-021204-2f573ec, 26 min
on 6 cores, bit check against U256ap inside it). Fig. 1 numbers from `figures/fig1_meanrolls.py`
(a test of the script on the M64 records outside a registered run; the registered figure run that
makes the committed figures is named in `RESULTS.md`, and these numbers are taken from it). The
figures were looked at.

- F1 / scope P5: PASS. SR: max |V/V_F - 1| = 9.8e-13, |eps1/eps1_F - 1| = 6.3e-12, |eps2 - eps2_F| =
  2.2e-11 over 348 record lines; USR: 1.1e-9, 4.6e-5, 4.4e-5 over 427 lines; eps2(N_f) = -0.02760.
  Landmarks (S8): eps2 = 3 crossed at N = 2.5234 and 6.5503 (own Friedmann 2.5234, 6.5503; reference
  2.52, 6.55); S9: eps1 minimum 9.716e-13 at N = 8.335 (reference 9.716e-13 at 8.331). The SR record
  ends at N = 8.099 (Friedmann 8.0989), not N* + 8.04 as `../scope/SETUP_AUDIT.md` item 4 and the
  scope deck header say: tlim = 8.5 is 8.10 e-folds [VERIFIED here; a correction for the lead].
- Scope P1 (USR half): PASS. USF256 against U256ap at t = 0, 5.2217, 10.4375: bit-identical in all
  17 common variables (`bitcheck_usr256.json`).
- F2 (a): PASS. Per-cell means of |H|/[H] and |M|/[M] equal the record columns at the 41 dump
  cycles within 2.6e-15 relative.
- F2 (b) USR: PASS. 68 per cent half-width of R^NR at N_f 0.8897 against sigma_R = 0.894 (0.5 per
  cent); 100/68 ratio 5.13. Scope P7: PASS (rms 0.8945 in 0.889-0.899; max |R^NR| 4.568 in 3-8).
- F2 (d) USR: PASS. delta K/K_b: 68 per cent half-width 4.2e-7 at N = 1.55, 8.9e-13 at N_f (falls by
  5e5); delta Pi/Pi_b at N_f 1.24e-2 (> 1e-2, barely); R^NR grows from 2e-3 (N = 4.5) to 0.85 (N =
  7.5), and from N = 9 to N_f its 68 per cent width changes by 0.05 per cent.
- F2 (e) USR: PASS for the 99th percentile of |H|/[H] (2.4e-11 at most, bar 1e-9) and for max
  |M|/[M] reaching order 1 (0.64). FAILED in part: the late 68 per cent band of |M|/[M] spans 8.4e-4
  to 3.2e-3, its lower edge below the predicted 1e-3 (centre about 1.6e-3, P1:541 "around 1e-2").
  The uniform residual H0 of the background step (scope entry 0) dominates |H|/[H] at N = 2-3 and
  after N = 7 (a flat 3e-14 floor): the figure is also made with the box mean of H removed
  (`fig4_usr_contrast_hzero`), where the band falls to 1e-15 at N_f as in P1's figure.
- F3/F5 USR (a) PASS: max over 3395 shells of |Delta_NR/Delta_lin - 1| = 5.0e-3 (rms 1.0e-3; 3.6e-4
  for k <= k_max/2; rising above |n| = 50 to the 3e-3 level, the top-shell mode-equation difference
  of audit item 19); (b) PASS: 99.6 per cent of shells within 3/sqrt(count) of Delta_MS; (c) PASS:
  above k_max the NR power is 1.3e-7 of Delta_MS(k_max) at most.
- F6 (a) USR PASS: Delta[K] falls by 1e9 (median over shells) from its maximum to N_f.
- A defect of my own script, found by looking at Fig. 6b against P1's: version 1 of `dumppass.py`
  binned sum_ij |(At_ij/chi)(k)|^2, the covariant components, which grow as a^4 relative to the
  invariant Kt_ij Kt^ij = At_ij At^ij (indices raised with gamma^ij = chi gt^ij); our late USR
  "Kt" sat near 1e-17 where P1's is near 1e-31. Fixed (`kt_version` 2, commit c3eb42e0);
  SR passes of version 1 are rescaled by <chi>^2 in `fig_spectra.py` (exact to second order since
  delta chi/chi ~ 1e-4 there); USR is rerun at the Fig. 6b dumps (group `usr256kt`). F6 (b), (c)
  are judged on the fixed spectra only.
