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

## Entry 3 (2026-11-24 06:30 PST): outcomes of the SR pass (P256v6), the ablation pass and the rungs

Run: E-20261124-133251-42e8aab (P256v6 18 dumps; AL0S, AL1S, RL1 at t = 0 and 8.5; AL0U, AL1U, AL2U,
UL1, U256ap at t = 0 and 10.4375, with c_NR of every injected mode; C32-C128 S/U all dumps; seven
bit checks; 44 min on 6 cores). Figures made from it (test outputs, then the registered figure run)
and looked at.

- F2 (b) SR: FAILED as written. 68 per cent half-width of R^NR at N_f 2.281e-5 against the predicted
  sigma_R = 2.06e-5 within 3 per cent (+10.7 per cent). Cause, checked afterwards with a quantity that
  could have disagreed: the realisation's own linear field (same alpha_n, the npz sums) has sigma =
  2.2779e-5, and the NR field 2.2780e-5 (4e-5 relative). The prediction used the expectation over
  realisations; in SR (flat Delta) the variance is carried by the few lowest shells, and the relative
  standard deviation of sigma^2 over realisations is 7.9 per cent (computed from the shell weights),
  against 0.16 per cent in USR (where it passed). The bar of 3 per cent was wrong for SR, not the run.
- F2 (c) SR: PASS. delta phi/phi_b reaches 95 per cent of its final 68 per cent width at N = 3.91;
  delta Pi/Pi_b at N_f is 7.7e-5 of its maximum (2.8e-9 against 3.7e-5).
- S13: max |R^NR| over the dumps with N <= 4.2 is 1.14e-4 (N = 3.91), inside the predicted 4e-5 to
  1.5e-4; the 68 per cent half-width there is 2.3e-5.
- F3 SR: (a) FAILED: max over shells |Delta_NR/Delta_lin - 1| = 5.2e-3 (bar 1e-3); rms 1.1e-3; 1.0e-4
  for k <= k_max/2 (where the bar holds); the excess is in the top shells as in USR (audit items 19
  and 3). (b) PASS (99.6 per cent within 3/sqrt(count)). (c) PASS (above k_max 8.7e-14 of the cut).
- F6 SR: (a) PASS: Delta[K] at N_f over N = 5.34: median 0.998 (0.991-1.0005). (b) PASS: Delta[Kt]
  at N_f over N = 4.39: median 2.8e-5 (version-1 pass, rescaled by <chi>^2). (c) PASS: Delta of
  sqrt(3 Kt Kt/2) over Delta[K] at N_f below 5.8e-9 at every injected shell. USR part of (c): FAILED
  at N_f (the ratio is 9.4e-7 median, a hierarchy of 1e6, weaker than SR's 1e9 but present); the
  fraction of shells with Q below K is 0 to 0.64 for N = 0.8-6.5 in USR and 0 to 0.39 for N <= 3.4 in
  SR, 1.0 after N = 3.9 in SR and after N = 7.5 in USR: the hierarchy sets in after the last crossing
  in SR and only after the USR phase in USR.
- Scope P1 (SR) and ablation P-A3 (i): the t = 0 dump of AL0S (level 0, mesh) is bit-identical to
  P256v6's, and AL0U's to U256ap's. FAILED for the levels: AL1S, RL1 (level 1) and AL1U, UL1, AL2U
  (levels 1, 2) differ from level 0 at t = 0 in phi, Pi, chi, K in 36 to 8140 cells, by at most 7.2e-10
  of the perturbation's range [VERIFIED, bitcheck_ablation.json]. Size and pattern are those of the last
  bits of a background taken from box means (a reduction) instead of phi0, pi0 [JUDGEMENT; core can
  say]. It is not a first-order difference; it does not move the spectra (below).
- P-A1 (SR, level 1): FAILED. |r10| up to 6.6e-7 (rms 3.5e-7), predicted below 1e-8; one sign over 90
  per cent of the shells; not above the refutation bar 1e-6. The released level 1 on shells (RL1)
  against the released level 0 (P256v6) shows the same, 6.6e-7 (rms 3.5e-7): the mesh mode equation
  is not the cause. Level 2 in SR: AL2S was cut at t = 7.53 and is continued (repro/continue); the t =
  7.5 comparison is run (E-20261124-141807-8352509).
- P-A2 (USR): PASS for r20 (rms 1.0e-4 in 1e-5..1e-3; max 7.0e-4 <= 3e-3; 52 per cent positive;
  larger at high k, top decile over bottom half 2.9) and for r10 (max 7.0e-7 < 1e-5, 91 per cent of
  one sign). Against P1's text bound (max |r20| <= 2e-4 "for all scales", P1:520): not met above |n| =
  32 (max 1.7e-4 up to |n| = 32, 6.0e-4 above |n| = 56) [VERIFIED]; P1's own Fig. 9 shows its
  inflection level-2 curve near 1e-4 to 1e-3 at the top shells (read), like ours.
- P-A3 (ii): PASS. Released level 0 on shells against level 0 on the mesh: 1.3e-2 (SR) and 1.7e-2
  (USR) at |n| >= 56, below 1e-5 for |n| <= 16, rising with k (top over bottom 46 and 211).
- P-A3 (iii): PASS. Records <|H|/[H]> and <|M|/[M]> of levels 1 and 2 within 5e-4 of level 0 on the
  mesh at every common cycle (SR to cycle 1227, USR all 1702).
- Scope P4: PASS. SR |Delta_RL1/Delta_P256v6 - 1| at most 6.6e-7 (bar 1e-6 at every shell); USR
  |Delta_UL1/Delta_U256ap - 1| at most 8.0e-7 (bar 1e-4 for k <= k_max/2).
- F7 / P6 (c) so far: max over the 44 shells |Delta_NR/Delta_lin - 1| at N_f = 3.2e-3 (32), 6.2e-5
  (64), 1.0e-6 (128), monotone (orders 5.7 and 5.9, the sixth-order stencils); 256 pending (CL256S).
- F8 / P6 (a) so far: entry maximum of <|H|/[H]>, order 32 -> 64: 4.15 (SR), 4.10 (USR, the
  background residual; 4.42 with the box mean of H removed): PASS; of <|M|/[M]>: 3.25 (SR), 3.45
  (USR): FAILED (band 4-6). From 64 to 128 the entry maxima are equal within 13 per cent in all four
  (the second-order plateau, P1:748). 256 pending (CL256S, CL256U). P6 (b): all decay after the entry
  except USR M, which rises again in the USR phase (as P1's Fig. 8b shows).

## Entry 4 (2026-11-24 06:30 PST): PAUSED (pause flag set at 06:14 PST, five-hour window at 80 per cent)

Stopped at the pause flag (`locks/PAUSE`), nothing new started. State:
- Closed registered analyses: E-20261124-130628-6790851 (USF256 pass), E-20261124-133251-42e8aab
  (P256v6, ablation finals, rungs), E-20261124-141807-8352509 (USF256 at the Fig. 6b dumps with the
  invariant Kt, kt_version 2; AL0S/AL1S/AL2S at t = 7.5; its outcomes are NOT yet looked at or judged:
  the bit check says AL2S differs from AL0S at t = 0 by 7.2e-10 of the perturbation, the same last-bit
  pattern as level 1 in entry 3).
- Not done: the registered figure run (`figures/make_figs.py`) that makes the committed figures; no
  PNG is in `fig/` yet. The figures were made only as tests in `scratch/E-stoch-inf/tmp/figs_test/`
  and looked at there; the numbers in entries 2 and 3 and in `RESULTS.md` come from those tests on
  the registered pass outputs (same scripts at the committed versions), and the figure run will
  reproduce them.
- Waiting: the five continuations of repro/continue (RSF256 E-20261124-130529-da8c917, RNC256
  E-20261124-130629-61fe0b0, CL256U E-20261124-130711-a5dec67, CL256S E-20261124-130952-4be980b,
  AL2S E-20261124-131359-49afe29) were all PENDING in Slurm at 06:19 PST behind other owners' jobs.

Next, in order, after the pause is lifted:
1. Figure run on what exists: `harness/bin/nrpic-run submit --kind production --gate G2 --package
   tracks/E-stoch-inf/repro/figs --preregistered "tracks/E-stoch-inf/repro/figs/JOURNAL.md#entry-1"
   --cores 2 --purpose "repro/figs: figures from the passes" -- bash -c 'OMP_NUM_THREADS=2 python3
   tracks/E-stoch-inf/repro/figs/figures/make_figs.py "$NRPIC_RUN_DIR" --usr256
   /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261124-130628-6790851 --usr256kt
   /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261124-141807-8352509 --sr256
   /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261124-133251-42e8aab --ablation
   /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261124-133251-42e8aab --rungs
   /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261124-133251-42e8aab --ablation75
   /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261124-141807-8352509'`; copy the PNGs into `fig/`,
   look at each, judge F6 (b, c) on the kt_version-2 USR spectra and the SR level 2 at t = 7.5
   (`fig9_ablation_sr_t75.json`), commit.
2. When the continuations have ended (repro/continue HANDOFF): passes `rsf256` (then Fig. 2 with
   the constraint panels, Fig. 3 and 6a from RSF256, bit check RSF256 against P256v6 = scope P1 SR),
   `cl256` (Fig. 7 at 256), `al2s` (Fig. 9 SR level 2 at N_f, P-A1), and the records of CL256U/S
   and RNC256 (Fig. 8 at 256, `fig_signflip`, scope P3); then the figure run again with `--rsf256`,
   `--cl256s`, `--al2s` and `--with256` (make_figs passes it with --cl256s).
3. RESULTS.md: replace the PENDING rows, add the ledger of the figure run, set STATUS.

## Entry 5 (2026-11-24 09:30 PST): resumed after the pause; predictions of the figure run, written before it runs

Resumed in batch R2b. The pause flag is absent; the five continuations of repro/continue are still
held by another user's job (both cards) until about the morning of 2026-11-25 and are not waited for.
The review of branch core/noise-level2 on Fable says "RESULTS UNCHANGED: the six ablation runs made with
6ca93cba stand" (coord/DECISIONS/0032 item 4), so the AL runs and the passes on them stand as they are.

Predictions (refuted by the stated miss):
- R1 (figure run = test runs): the registered figure run `make_figs.py` on the three closed passes
  (130628-6790851, 133251-42e8aab, 141807-8352509) gives the numbers of entries 2 and 3 to every printed
  digit (same scripts at the same commit, same inputs, deterministic numpy). Refuted by any differing
  digit of a number quoted in entries 2-3 or in RESULTS.md.
- R2 (Fig. 6b with the invariant Kt, kt_version 2, USF256): Delta[Kt] at late times sits near P1's level
  (P1 Fig. 6b, read: about 1e-31) within two decades, not near the 1e-17 of version 1; the USR ratio Q/K
  of sqrt(3 Kt Kt/2) to K at N_f has a median within a factor 3 of entry 3's 9.4e-7 [the version-1
  values for USR were rescaled by <chi>^2, which is not exact when R ~ 1; a larger miss means entry 3's
  USR number must be replaced]. Refuted by either.
- R3 (SR ablation at t = 7.5, N = 7.2; AL0S, AL1S, AL2S dump 15, all injected modes frozen by N = 4.2,
  entry 3 F2 c): P-A1 of repro/ablation applied at this time: r20 = Delta_L2/Delta_L0 - 1 per shell has
  rms over |n| <= 32 between 1e-7 and 1e-4, max over all shells <= 2e-4, 30-70 per cent of shells
  positive, no rise toward the cut; r10 equals its N_f value from entry 3 within 10 per cent (6.6e-7
  max, rms 3.5e-7; frozen modes and a level-1 shift set at the entry). Refuted by any of these; the
  r20 part is judged at t = 7.5 only and N_f stays PENDING (AL2S continuation E-20261124-131359-49afe29).
- R4 (bit check AL2S against AL0S at t = 0, `bitcheck_ablation75.json`): NOT a prediction: I read
  the first part of the json (phi to Azz) before writing this entry. Recorded under entry 6 as an
  observation only.

## Entry 6 (2026-11-24 09:35 PST): outcomes of the figure run E-20261124-172426-4780cbc (entry 5)

Run E-20261124-172426-4780cbc (`make_figs.py` on the passes 130628-6790851, 133251-42e8aab,
141807-8352509; 50 s on 2 cores). Every PNG was looked at.
- R1: PASS. Each json of the run equals the json of the test outputs (`scratch/E-stoch-inf/tmp/figs_test/`)
  in every number (ten of eleven files: zero differences, compared key by key); the eleventh,
  `fig6b_usr_Kspec`, differs as it must (it reads the kt_version-2 pass with 9 dumps instead of the
  version-1 pass with 41). So every number of entries 2-3 now stands on this registered run.
- R2, second part: PASS. Median of Q/K at N_f (USR) = 9.428e-7, identical to all digits to entry 3's
  value: the spectrum of sqrt(3 Kt Kt/2) was already the invariant in version 1 (only the Kt panel
  summed covariant components). First part: FAILED as written. Our version-2 Delta[Kt] at N_f = 10.0
  is near 3e-35 over the injected shells (Fig. 6b middle panel, read off our own figure), about 3e3
  below P1's last curve (about 1e-31.5 at <N> = 7.95, P1 Fig. 6b, read), not within two decades. The
  times differ (10.0 against 7.95) and Kt decays after the USR phase; at the nearest common time (ours
  5.53, P1's 5.43) ours is about 3e-28 and P1's about 1e-27 (both read), a factor 3-10, the size of the
  amplitude factor of Fig. 4 squared (about 16). Version 1's 1e-17 is gone. A like-for-like value
  needs a dump near N = 8.0 (entry 7).
- R3: PASS in every part. SR at t = 7.504 (N = 7.19): r20 rms over |n| <= 32 = 1.5e-5 (band 1e-7 to
  1e-4), max over all shells 7.9e-5 (<= 2e-4), 49.7 per cent of shells positive, largest at the lowest
  shells (max for |n| <= 16 is the global max; top over bottom median 0.51, no rise toward the cut);
  r10 max 6.575e-7 and rms 3.461e-7 against 6.553e-7 and 3.460e-7 at N_f (0.3 per cent). P-A1's r20
  part is met at t = 7.5 and is consistent with P1:520 (max |r20| <= 1e-4 at every shell). Records of
  AL2S against AL0S within 5.4e-4 at the 1228 common cycles. Looked at against P1 Fig. 9 (read): P1's
  red curve sits at about 5e-5 at k_min and falls to 1e-6..1e-5 at the top shells; ours (t = 7.5)
  starts at 3e-5 and falls likewise. N_f stays PENDING (E-20261124-131359-49afe29).
- R4 (observation, not a prediction): AL2S against AL0S at t = 0 differ in phi (36 cells), Pi (8140),
  chi (178), K (41) by at most 4.4e-16 absolute (7.2e-10 of the perturbation range); alpha, gt_ij,
  At_ij identical. The same last-bit pattern as levels 1 and 2 in entry 3.
- Correction of entry 3 (USR hierarchy, F6 c), from the 41-dump series that this run reproduces
  (`scratch/E-stoch-inf/tmp/figs_test/usr/fig6b.json`, identical inputs): the fraction of injected
  shells with Q below K is below 0.2 for N <= 3.05, 0.23-0.64 for N = 3.3-5.3, 0.91-1.0 for N =
  5.53-6.28, 0.34-0.68 for N = 6.52-7.02, and 0.98-1.0 from N = 7.27 to N_f. Entry 3's "0 to 0.64 for
  N = 0.8-6.5" was wrong for N = 5.5-6.3; RESULTS.md is corrected. The registered run of entry 7 makes
  this series again inside a registered figure run.
- Cosmetic defects seen in the PNGs (no number affected): the suptitle overlaps the panel title in
  Figs. 3, 5, 6; tick labels collide at panel joins (Fig. 1 left column, Fig. 8 x axis); the legend of
  Fig. 8 lists N = 256 without a curve; `fig9_ablation_sr_t75` has an empty right panel.

## Entry 7 (2026-11-24 09:40 PST): predictions for the pass at N = 8.0 and the second figure run

Plan: a registered pass `usr256kt8` over USF256 dump 32 (N = 8.01, kt_version 2), then a second figure
run that (i) draws Fig. 6b from the kt_version-2 dumps with targets that include 8.0 (P1's last curve
is at 7.95) while the measures over all dumps read the 41-dump pass too (K and Q are the same in both
versions; every plotted row is version 2); (ii) records the median over injected shells of
Delta[Kt]/Delta[K] and of Delta[Q]/Delta[K] at each plotted dump, both scenarios; (iii) fixes the
cosmetic defects of entry 6.
- R5 (USR, N = 8.01): Delta[Kt] over the injected shells has its median within a factor 30 of P1's
  last curve read at 1e-31.5 (the amplitude factor squared, 16, and reading); the median of
  Delta[Kt]/Delta[K] at N = 8.01 is between 1e-2 and 1e2 (P1:570, "all terms in K_ij are of similar
  magnitude" in USR). Refuted by either outside.
- R6 (SR, last dump): median Delta[Kt]/Delta[K] below 1e-3 (Kt fell to 2.8e-5 of its crossing value
  while K froze, entry 3); P1:570 "negligible in the quadratic case". Refuted above 1e-3.
- R7: every number of the first figure run that does not involve the new dump is unchanged (Figs. 1-5,
  7-9 jsons identical; Fig. 6b measures over all dumps equal the 41-dump test values).

## Entry 8 (2026-11-24 09:45 PST): outcomes of entry 7 (pass E-20261124-172949-8b2255b, figure runs E-20261124-173117-51c289f and E-20261124-173254-420115f)

Pass of USF256 dump 32 (t = 8.351, N = 8.014; 57 s). Figure run 173117 with Fig. 6b at N = 8.01 and the
new medians; figure run 173254 after the Fig. 1 tick fix, every json identical to 173117 (byte
compare): its PNGs are the ones copied to `fig/`. All new PNGs looked at (Figs. 1, 3, 6a, 6b, 8,
9 at t = 7.5).
- R5: PASS. USR at N = 8.01, medians over the injected shells: Delta[Kt] = 6.5e-32 in P1's units
  (P1's curve at <N> = 7.95 read near 3e-32: a factor 2), Delta[Kt]/Delta[K] = 1.6e-2 (inside 1e-2 to
  1e2, near its lower edge), Delta[Q]/Delta[K] = 4.2e-3. The series of Kt/K in USR: 0.46 (N = 0.78),
  0.73, 1.10, 1.13, 1.17 (3.55), 3.3 (5.53), 1.6e-2 (8.01), 3.6e-6 (10.0). So Kt is comparable with K
  or above it through the USR phase and falls below it after the USR phase ends (N about 7.5).
- R6: PASS. SR medians of Kt/K: 0.39 (N = 0.50), 0.70, 1.10, 1.33, 1.41 (3.44), 1.1e-4 (5.34), 4.4e-8
  (8.10).
- R7: PASS. All jsons of 173117 except Figs. 6a/6b equal those of 172426 byte for byte; Fig. 6a gains
  only the new key; Fig. 6b's measures over all dumps equal the 41-dump values (K_last_over_max median
  1.41e-9, Q_over_K_last, Q_below_K_frac_by_dump, K_last_over_N55 identical); Kt_last_over_N45 =
  5.6e-11 (version 2; version 1 rescaled gave another value and is not used for USR).
- Not a reading of P1 beyond the curves named: the factor of about 3.5 in the one-point bands of Fig. 2
  (SR: delta phi/phi_b 68 per cent half-width at N_f ours 2.88e-7, P1 Fig. 2 read about 1.0e-6; R^NR
  2.28e-5 against about 0.8e-4; delta Pi/Pi_b before the entry 1.5e-5 against about 0.6e-4) is the same
  as in USR (Fig. 4, factors 2.3 to 4), while the spectra (Figs. 3, 5) agree in level. Recorded for
  RESULTS; no cause named (P1 does not state the normalisation of its real-space draw).
