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
