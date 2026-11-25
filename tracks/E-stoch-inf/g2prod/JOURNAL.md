# JOURNAL of package g2prod (E-stoch-inf, gate G2: USR production ladder on the release build)

## entry-1

2026-11-21 12:28 PST, lead of batch 5, written and committed before any run of this package.

Purpose. Leave the cards loaded with the G2 production runs of the USR case on the release card
build core-v0.6 (`/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena`; decision 0023 item 1:
production on a release build), plus the 256-cell slow-roll run P256 again (G1 reservation 2,
risk R1). Criteria: `spec/scope/SCOPE.md` section 4c, fixed in the same commit before the runs.
Deck `inputs/usr_prod.athinput` = `usr/inputs/usr_256s.athinput` (deck of the scouting pair
U256 E-20261121-075255-8cf90e7 and U256m E-20261121-085221-1f579fe, executable core_scalar-3
5cc2821) plus a restart output every 2.0 code time units for the chain helper.

Known from the scouting pair (usr/README.md tables, usr/JOURNAL.md entries 13-15): 1702 steps,
1.30 s per step, 37.0 min = 0.617 card-hours, 19.6 GB card memory, 21 dumps of 2.95 GB; odd part
D_n at N_f max 1.09e-4 for k <= 32 dk, every mode to 64 dk at most 4.5e-3; even/odd rms 2.533e-4
(lead's code, E-20261121-130236-e39e143); U-A3 0.9923-1.0016; one-point rms 0.89452; records
<abs H'/[H]> 2.9e-12, <abs M/[M]> 2.5e-2 (USR), 2.1e-3 at N_f; top-shell lockstep error 2.55e-3
= k^5 dt^4/600 (RK4 phase error).

Runs, in the order they go to the cards (at most two card jobs of E eligible at a time; the
first two submitted by the lead, the rest by `scripts/sequencer.sh` from `queue.txt`):

| Label | What | Card-hours (estimate; reservation) |
|---|---|---|
| T | timing: 40 steps at 256^3, 320^3, 384^3, no dumps (batch) | 0.15; 0.42 |
| P256v6 | SR 256^3, `ladder/inputs/jobA.list` (batch) | 0.5; 0.97 |
| U256ap, U256am | seed A (rng_seed 20261115), s = +1, -1, 256^3 | 0.65 each; 1.97 each (2 segments) |
| U320ap | seed A, s = +1, 320^3 | 1.6 (scaled: 2128 steps x 2.54 s); 2.95 (3 segments) |
| U256bp, U256bm | seed B (20261116), s = +1, -1 | 0.65 each |
| U320am | seed A, s = -1, 320^3 | 1.6 |
| U256hp, U256hm | seed A, s = +1/2, -1/2 | 0.65 each |
| U256nc | seed A, s = +1, noise_pi_sign = -1, to t = 3.75 (end of the entry) | 0.25; 0.98 |

Total about 8.0 card-hours; G2 has 8.23 left of the allotment of 10 (nrpic-run budget,
2026-11-21 12:23 PST). Reservations exceed it before the earlier runs are closed, so the
sequencer retries a refused submission every 15 minutes; the last runs (U256hp/hm, U256nc)
need either the earlier runs closed at their actual cost or a larger allotment (request to
orch, this session's outbox).

Predictions (each with what would refute it):

- R0 (processor restart check, before any chain relies on a restart): the deck at 32^3 on
  the release processor build, straight against restarted from the middle restart file: the
  final dump, its mode file and the last record lines byte-identical. Refuted by any byte.
- T (timing): step time 1.30 +- 0.15 s at 256^3 (release = scouting code path plus the
  non-finite guard); 2.4-2.8 s at 320^3; 4.0-4.8 s at 384^3 (cells scale); card memory
  19.6 +- 1 GB, 36-42 GB, 62-70 GB; 384^3 fits on one 80 GB card. Refuted if 256^3 is off by
  more than 0.2 s, or if 384^3 does not start (memory).
- P256v6: A2 max D_n at N_f for k <= k_max/2 = 1.2078e-4 within 1 percent
  (`ladder/results/final/P256_judge.json`, run E-20261115-172618-f948386); record maxima
  <abs H/[H]> 5.10e-11 and <abs M/[M]> 3.99e-4 within 1 percent; the record rows equal those of
  P256 to 1e-10 relative. Byte identity is not predicted (the release differs from scalar-2
  a58e95b by later merges; card reductions). Refuted if A2 moves by more than 1 percent or a
  record row differs by more than 1e-8 relative.
- U256ap/am (release repeat of the scouting pair): U-A2' max D_n (k <= 32 dk) = 1.09e-4 within 5
  percent, all modes to 64 dk <= 4.5e-3 (+5 percent); U-A3 within 0.9923-1.0016 (+-1e-4); one-point
  rms 0.89452 +- 1e-4; records as U256; U-A0, U-A1 pass. Per mode the release R^NR equals the
  scouting one to 1e-8 of the rms (same scalar-3 code). Refuted beyond these margins.
- U320ap/am (resolution, U-R): odd-part max D_n (k <= 32 dk) in [2.4e-5, 4.6e-5] (factor 2.4 to 4.5
  below 256^3: order 4 if the RK4 phase error dominates, order 6 for the spatial stencil); top
  shell (64 dk) lockstep error 2.55e-3 x (256/320)^4 = 1.04e-3 +- 10 percent; shell power at N_f
  of U320ap against U256ap within 1e-3 for k <= 32 dk and 1e-2 to 64 dk; even/odd rms 2.53e-4
  +- 5 percent (resolution-independent). Refuted if the factor is below 2.0 or above 4.5, or the
  even part moves by more than 5 percent.
- U256bp/bm (seed B, U-S): U-A2' max D_n <= 2e-4 (k <= 32 dk); U-A3 within 2 percent; one-point
  rms within 5e-3 of the ensemble lattice value 0.89366; skewness abs < 0.01. Refuted beyond.
- U256hp/hm (halving, U-A4'): with the floor of SCOPE 4c, even parts of H and M scale by
  4.00 +- 0.05 against U256ap/am at every dump where e_{s/2} > 3 f (group 1 at 128^3 gave
  3.987-4.001, E-20261121-080134-a0cc3eb); U-A2' max D_n unchanged within 5 percent (first-order
  relative error does not depend on s); even/odd rms of R at N_f halves: 1.27e-4 +- 5 percent.
  Refuted if any judged dump falls outside 3.95-4.05 or the even/odd rms does not halve.
- U256nc (control, U-A4'(d)): odd part of H of the control over that of U256ap/am, ratio of
  the maxima over the entry (cN <= ln 32 = 3.47) >= 1e3 (SR at G1: 1709-1874). Refuted below 1e3.

Analysis is not part of this session (decision 0025 item 4: sessions load cards; analysis
later). The analysis reuses `usr/scripts/` (pair analysis, lockstep) and `window/scripts/`
readers; the outcome goes into entry 2 against these predictions.

## entry-1 outcomes so far (lead of batch 5, 2026-11-21 12:43 PST)

- R0 HELD (run E-20261121-202941-da16544, release processor build core-v0.6, 32^3, nmax2 16):
  run A straight to N_f wrote 7 restart files (t = 0, 2, ..., 10 and the final one); run B
  restarted from usr.00003.rst (t = 6); the final dump usr.sf.00020.dump, its mode file and the
  last lines of usr.sf.hst and usr.sf.con.hst of A and B are byte-identical. A chain segment
  that restarts this deck continues the same run. Cost: A took 2.5 s per step on one core
  (213 steps), B half of it.
- T, P256v6: queued (Slurm 4827, 4828) at 12:43 PST behind other owners' jobs; nothing run yet.

## entry-2 (analysis of the ladder; lead of batch 10a, 2026-11-22)

### 2.0 Before any analysis ran (17:55 PST)

State: the sequencer exited at 13:49 PST ("queue empty and every run closed"); all eleven card
runs completed (state.tsv). Nothing of them has been analysed. The predictions are those of
entry 1; nothing is changed here. How each is read (written before the analyses):
- T: step time = cpu time / 40 from each athena.log; memory = gpu_mem_peak_MiB of the log.
- P256v6: `ladder_analysis.py extract` + `judge` as for P256 (seed 20261115), A2 max D_n
  (k <= k_max/2) against 1.2078e-4; record files sr.sf.hst and sr.sf.con.hst row by row against
  those of E-20261115-172618-f948386 at equal cycles (max relative difference per column).
- USR: `g2prod/scripts/analyse_g2.py` (the readers and metrics of `usr/scripts/analyse_cards.py`
  unchanged, groups of g2prod added): g2a = ap, am, hp, hm (seed A); u256 = bp, bm (seed B);
  u320 = U320ap, U320am. SCOPE 4c is then judged by `g2prod/scripts/judge_g2.py` from the
  summaries: the floor f^2 = max(0, (4 o_{1/2}^2 - o_1^2)/3) per dump for H and for M; U-A4'(a)
  at every dump with e_{1/2} > 3 f, and reported separately on the subset where also
  o_{1/2} > 3 f (U-A4'(b) wording "(a) judged only there"; both are given, the stricter
  reading decides) [JUDGEMENT: the two clauses of 4c read differently; neither is dropped].
- U-A4'(d): the control has no mirrored partner, so its odd part is read two ways, both
  reported, the smaller ratio decides: (i) (H_nc - H_am)/2 with box mean removed; (ii) H_nc
  with box mean removed (the control's even part is second order); against the odd part of
  the proper pair (ap, am), rms per dump, ratio of the maxima over dumps with cN <= ln 32.

### 2.1 Outcomes T and P256v6 (analysis E-20261123-015014-b4ecd4e, 1 core, 6 min)

- T HELD on step time, memory band missed at 384^3 (run E-20261121-202929-43dcc9c, 0.111
  card-hours): 1.374 s per step at 256^3 (predicted 1.30 +- 0.15), 2.522 s at 320^3 (2.4-2.8),
  4.300 s at 384^3 (4.0-4.8). Peak card memory 19589, 36393, 61077 MiB; the prediction was
  written in thousands of MiB (the scouting "19.6 GB" is 19589 MiB), so 384^3 at 61.1 lies 1.5
  percent below its band 62-70: that part of the prediction FAILED (low). Not refuted by the
  stated rule (256^3 within 0.2 s; 384^3 started and fits one 80 GB card with 20.8 GiB to
  spare). Cost scales slower than N^3 (zone-cycles per second rise from 1.22e7 to 1.32e7).
  Figure `fig_g2_timing.png` (looked at).
- P256v6 HELD, beyond the prediction (run E-20261121-202935-31520bc, 0.509 card-hours): A2 max
  D_n (k <= k_max/2) = 1.20776e-4 against 1.20776e-4 (relative change 1.8e-10, from the judge
  scripts' reference arithmetic); max D over all modes 4.4928e-3 both. Every row and column of
  sr.sf.hst and sr.sf.con.hst (1389 rows each, same cycles) is IDENTICAL to the tested-branch
  run E-20261115-172618-f948386 (max relative difference 0.0); R^NR per mode at N_f equal to
  1.4e-16 (division round-off). Byte identity was not predicted; the records are identical
  digit for digit. G1 reservation 2 ("no release card build has repeated the 256-cell run")
  is answered: the release card build core-v0.6 repeats it. Figure `fig_g2_p256v6.png` (looked
  at; the top panel plots the zero differences at the 1e-18 floor).

### 2.2 Outcomes U320ap/am and U256bp/bm (analyses E-20261123-020751-0baf597, E-20261123-021730-a421438)

Analysis defects of this session, on record: (i) E-20261123-015650-493cff5 FAILED: with one
dump only, analyse_cards' constraint part reduced an empty array; the --last mode now keeps the
dumps at N* and N_f. (ii) E-20261123-014905-2bf3570 (seed B, all 21 dumps) referred the runs to
seed A's realisation alpha_n (analyse_cards has no seed option): its per-mode numbers (D_n 241,
U-A3 0.03-46) are INVALID; its seed-independent numbers (records, one-point moments of R^NR,
even/odd rms) stand. The second pass with --seed 20261116 at N* and N_f is the one judged.

- U320ap/am (seed A, 320^3, 1.47 + 1.48 card-hours, two segments each, no outside kill):
  odd-part max D_n (k <= 32 dk) at N_f = 5.18e-5. Predicted [2.4e-5, 4.6e-5] (factor 2.4-4.5
  below 256^3): the band FAILED; the factor against the 256^3 pair is 2.10 (1.087e-4 / 5.18e-5,
  release seed-A value from 2.3 below; 2.10 against the scouting 1.089e-4). Not refuted by the
  stated rule (factor in 2.0-4.5) and U-R (i) holds, with little margin. Observation (figure
  `fig_card_u256_modes.png` of the 320 analysis, looked at): the odd-part shell maximum is flat
  at about 4.2e-5 for |n| < 30 at 320^3, and the median D_n barely moves (4.19e-5 at 256^3,
  4.08e-5 at 320^3): a part of the per-mode error that does not fall with N at fixed Courant
  (both dt and dx shrink) sets the k <= 32 maximum; cause NOT named (no run yet in which a
  candidate could have failed; the halving pair in 2.3 tests whether it depends on s).
  Top shell: all modes to 64 dk max 1.55e-3 (256^3: 4.5e-3); lockstep record at N_f 1.0465e-3
  against the predicted 2.55e-3 x (256/320)^4 = 1.04e-3 +- 10 percent: HELD (RK4 phase error
  k^5 dt^4/600). Even/odd rms (k <= 32) 2.53322e-4 against 2.53350e-4 at 256^3 (1.1e-4
  relative; predicted +- 5 percent): HELD. U-A0 6.6e-10 in N, U-A1 4.17e-5, U-A3 single run
  0.99230-1.00161 (ap) and 0.99823-1.00757 (am), odd pair 0.99992: pass.
- U256bp/bm (seed B, 0.62 card-hours each): U-A2' max D_n (k <= 32 dk) = 1.087e-4 (predicted
  <= 2e-4): HELD; all modes 4.51e-3; U-A3 single runs 0.9968-1.0019 (bp), 0.9980-1.0031 (bm),
  within 2 percent: HELD; one-point rms of R^NR at N_f 0.894109 and 0.894108 against the
  lattice value 0.89366 (difference 4.5e-4, bar 5e-3): HELD; skewness 0.0042 and -0.0012
  (|.| < 0.01): HELD. Even/odd rms 2.5348e-4. U-A0 1.6e-9, U-A1 4.17e-5. Figures of both passes
  looked at (one-point histogram Gaussian over 10 decades; slice).

### 2.3 Outcomes seed A (s = +-1, +-1/2), control, SCOPE 4c (analysis E-20261123-014858-8e72d4c, judge E-20261123-024359-5dc3213, check E-20261123-024806-3c0e139)

Figures looked at: fig_g2_ua2, fig_g2_halving, fig_g2_resolution, fig_g2_records, fig_g2_control,
fig_g2_common_mode (judge run, fig/).
- U256ap/am HELD in every part: R^NR per mode of the release runs is IDENTICAL to the scouting
  pair (core_scalar-3) at every dump (max |difference| 0.0); U-A2' 1.0894e-4, all modes 4.506e-3,
  U-A3 0.99230-1.00161 (ap), one-point rms 0.894520, records <|H'|/[H]> 2.885e-12, <|M|/[M]>
  0.0252; U-A0 1.6e-9, U-A1 4.2e-5.
- U256hp/hm: even/odd rms halves (1.2667e-4 against 2.5335e-4/2): HELD. U-A2' at s = 1/2 is
  1.242e-4 against 1.089e-4 at s = 1 (+14 percent): the prediction "unchanged within 5
  percent" FAILED. U-A4'(a) as written: H judged at 9 dumps (e_{1/2} > 3f), corrected even
  factors 3.992-4.042, all within 4.00 +- 0.05; M judged at 11 dumps, 10 within, ONE OUTSIDE:
  3.925 at cN = 6.52 (end of USR; also in the subset with o_{1/2} > 3f). The prediction "any
  judged dump outside 3.95-4.05 refutes" is REFUTED, and U-A4'(a) FAILS as written (clause on
  the maxima: no dump dropped). Raw odd halving 1.99994, even 3.99988 for R at N_f.
- Finding (the halving pair is the run in which it could have failed): the flat part of the
  odd-part error at k <= 32 dk (fig_g2_ua2) is a common factor of all modes (mean Re(O/c_ref -
  1) over k <= 16 dk = -4.107e-5 at s = 1 with scatter 4e-7; -4.138e-5 at 320^3) and scales
  as s^2: -9.87e-6 at s = 1/2 (ratio 4.16). It appears after cN = 5.5 and is constant after
  cN = 7.5 (fig_g2_common_mode). It is third order in the amplitude, not discretisation; which
  third-order term (the evolution or the nonlinear definition of R^NR) is NOT named. It is why
  U-R (i) gave 2.10 rather than 2.4-4.5: the k <= 32 maximum at 256^3 sits on it.
- U256nc (control): odd part of H over that of the proper pair, ratio of the maxima over the
  entry (cN <= ln 32): 1.19e5 (cross reading, decides) and 2.38e5 (single); pointwise 1.2e5 to
  8.7e5 after N*: HELD (>= 1e3). Its records <|H'|/[H]> 1.28e-7, <|M|/[M]> 0.50 (first order).
- U-A4'(c) on the nine proper release runs: <|H'|/[H]> max 1.28e-12 to 3.03e-12 (< 1e-9), <|M|/[M]>
  max 0.0081 (320^3) to 0.0252 (< 0.1): PASS. Read literally over every release run the control
  fails it by design; it is judged on the proper runs [JUDGEMENT]. The M record does NOT double
  at s = 1/2 at 256^3 (0.02512 against 0.02519), unlike 128^3 (2.47e-2 -> 4.3e-2).
- U-R: (i) 2.10 in 2.0-4.5 PASS; (ii) shell power 320 vs 256 at N_f 1.18e-4 (k <= 32 dk, bar
  1e-3) and 4.6e-3 (to 64 dk, bar 1e-2) PASS (prediction held); (iii) even/odd 3.5e-5 and 1.1e-4
  relative PASS. U-S PASS (2.2). U-W met by the scan (SCOPE 4c).

Verdict against SCOPE 4c's definition of "the USR case is reproduced": U-A0, U-A1, U-A2', U-A3
on the release build for seeds A and B PASS; U-R PASS; U-W met; U-A4'(c), U-S, U-A4'(d) PASS;
U-A4'(a) FAILS at one dump of M (3.925 at cN 6.52). As written, the USR case is NOT reproduced
in full; the gate decision belongs to orch (outbox of this session).

## entry-3 (predictions for the third amplitude, written before submission; lead of batch 10a, 2026-11-22 19:00 PST)

Runs U256qp/qm (s = +-1/4, seed A, 256^3, deck as U256ap; queue.txt; release card build
core-v0.6; 0.62 card-hours each expected, ceiling 1.97). They go behind the two card jobs of
repro/scope (the sequencer keeps at most two E jobs eligible). Why: the one failed dump of
U-A4'(a) (M, 3.925 at cN 6.52) could be a higher order in s in the even part (e = a s^2 + b s^4,
which the two-amplitude floor of SCOPE 4c ignores), and the common-mode floor scales as s^2.
Analysis: analyse_g2.py --group g2q (U256 = hp, U256m = hm, U256h = qp, U256hm = qm), then
judge_g2.py's halving and floor code on that summary.
- Q-a: the even factor of M at cN 6.52 from the pairs s = 1/2 and 1/4 (floor from their odd
  parts) is 3.98 +- 0.015 (a quarter of the deviation -0.075). Refuted if its deviation from 4 is
  not at most half that of (1, 1/2), i.e. if it is below 3.9625; H stays within 4.00 +- 0.05 at
  every judged dump.
- Q-b: the common-mode part of the odd-part error at N_f (k <= 16 dk) is -2.5e-6 +- 0.4e-6
  (s^2 law from -9.87e-6). Refuted outside [-3.3e-6, -1.7e-6].
- Q-c: U-A0, U-A1, U-A3 pass; records <|H'|/[H]> < 1e-9 and <|M|/[M]> < 0.1; even/odd rms
  (k <= 32 dk) 6.33e-5 +- 5 percent.
A cause of the U-A4'(a) miss is named only if Q-a holds.

## entry-4 (quarter-amplitude pair; lead of batch 15, 2026-11-24)

### 4.0 Before judge_q runs (19:35 PST)

The analysis E-20261124-233223-51b52c0 (group g2q) ended 2026-11-25T00:05Z, exit 0. The fresh
verifier (stage/G2/VERIFIER.md 3.2, 3.4; runs E-20261125-022309-d346f12, -023609-01d8feb) has
already recomputed the quarter pair with its own reader, so this is a reconciliation rather than a
blind test. Expected from judge_q.py on the g2q summary (judge_g2's floor code unchanged):
- Q-a REFUTED: the M factor at cN 6.52 from (1/2, 1/4) near 4.13 (verifier 4.127), outside
  3.9625-4.0375; M not judged there by 4c's own rule (e_{1/4} < 3 f).
- Q-b HOLDS: common mode at N_f for s = 1/4 near -2.07e-6 (verifier), inside [-3.3e-6, -1.7e-6];
  the half pair gives -9.87e-6 again.
- Q-c HOLDS: U-A0 ~1.6e-9, U-A1 ~2.5e-6, U-A3 0.998-1.0004, records 1.2e-12 and 0.025, even/odd
  rms ~6.334e-5.
What would show a defect of either reader: a difference from the verifier's numbers above 1e-3
relative in any of these (both read the same dumps).

### 4.1 Outcomes Q-a..Q-c (judge E-20261125-033357-a608cda; rerun after a figure fix E-20261125-033450-4c4a31c, same numbers)

Inputs: g2q analysis E-20261124-233223-51b52c0 (U256hp/hm s = +-1/2, U256qp E-20261123-230004-861aea7
and U256qm E-20261123-230507-a6246b1 s = +-1/4, release card build core-v0.6), the s = 1 over 1/2
judge E-20261123-024359-5dc3213. Figure looked at: fig/fig_g2_quarter.png of the rerun (the first
version's common-mode panel was dominated by the ill-defined sample at N*; the rerun plots from
cN = 1 on; numbers unchanged).
- Q-a REFUTED. The even factor of M at cN 6.525 from (1/2, 1/4) with judge_g2's floor is 4.1275,
  not 3.98 +- 0.015: its deviation from 4 (+0.127) is larger than that of (1, 1/2) (-0.075) and of
  the opposite sign. M is not even judged there by 4c's own rule (e_{1/4} < 3 f). Elsewhere the
  quarter pair judges H at 3 dumps (cN 3.05-4.04: 3.99988-4.00026) and M at 6 (cN 0-5.04:
  3.98537-4.00983), all within 4.00 +- 0.05. By the rule of entry 3 no cause of the U-A4'(a) miss
  is named from the s^4 hypothesis: it is not a higher order in s.
- Q-b HOLDS by its refutation rule: common mode of the odd-part error at N_f (k <= 16 dk) -2.0725e-6
  at s = 1/4 (window [-3.3e-6, -1.7e-6]); it lies 0.03e-6 outside the stated band -2.5e-6 +- 0.4e-6.
  The half pair repeats -9.872e-6; ratio 4.76, not 4: with the three amplitudes the common mode is
  a s^2 + b, a = -4.16e-5, b = +5.3e-7 (verifier, E-20261125-023609-01d8feb). In the figure the
  s = 1/4 curve times 4 sits about +1.5e-6 above the s = 1/2 curve from cN 1.5 on, i.e. an offset
  of about +4e-7 at s = 1/4 that does not scale as s^2; the drop after cN 5.5 does. No cause named.
- Q-c HOLDS: U-A0 1.61e-9 (both runs), U-A1 2.52e-6, U-A3 0.99809-1.00042 (qp) and 0.99957-1.00191
  (qm); records <|H'|/[H]> 1.191e-12, <|M|/[M]> 0.02513 (both, < 1e-9 and < 0.1); even/odd rms
  (k <= 32 dk) 6.3337e-5 against 6.33e-5 +- 5 percent; U-A2' of the quarter pair 1.289e-4 (s = 1/2:
  1.242e-4, s = 1: 1.089e-4).
- Reconciliation with the fresh verifier (stage/G2/VERIFIER.md 3.2, 3.4; own reader, own R^NR,
  own floor code): 4.127 (4.1275 here), -2.07e-6 (-2.0725e-6), U-A0 1.6e-9, U-A1 2.5e-6, U-A3
  0.99809-1.00042, records 1.19e-12 and 2.51e-2, even/odd 6.334e-5: every number agrees to the
  digits the verifier quotes. The expectation of 4.0 held.

### 4.2 The three-amplitude reading (a finding after the data; ruling 0036 item 2)

Not a test of this package: the verifier proposed and ran it (E-20261125-023427-6fb6400,
fig_floor3.png) after the runs. With D1 = E(1) - 4 E(1/2) and D2 = E(1/2) - 4 E(1/4), rms(D2)/
rms(D1) = 0.997 to 1.000 and corr(D1, D2) = -0.235 to -0.245 at every dump 1-13 for H and M,
the values of E(s) = s^2 A + F_s with a per-run part F_s of equal rms sigma at every s
(expected ratio 1, correlation -4/17 = -0.235); an s^4 term would give 1/16 and +1. With sigma in
place of the 4c floor the M factor at dump 13 is 3.9988 and every dump with e_{1/2} > 3 sigma lies
within 4 +- 0.0045 (H) and 4 +- 0.0012 (M). The 4c floor f = 4 o_{1/2}^2 - o_1^2 is the difference
of two numbers equal to 1e-4 where the odd part is 10 to 1000 times the even part, so a third-order
part of the odd part moves it by tens of percent (f/sigma 0.65-1.75 at dumps 8-13).
Status [JUDGEMENT on the cause; the numbers VERIFIED by the verifier's runs and not rerun here]:
the miss of U-A4'(a) comes from the floor estimator fixed in 4c, not from the evolution or a
higher order in s. U-A4'(a) stays FAILED as written (ruling 0030 item 2, 0036 item 2); this
reading stands beside it, labelled as made after the data. For later gates a three-amplitude floor
and a U-R clause on the discretisation part (Richardson in s^2) are proposals, not rewordings
(outbox to orch, batch 15).
