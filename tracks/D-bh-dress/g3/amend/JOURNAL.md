# JOURNAL of package g3/amend (Track D): the lead's own check of the G3 scope review before the amendment

Owner D-bh-dress, lead of batch 35 (2026-11-27 evening). Purpose: decision 0048 item 4 and the review
`g3/scope_review/SCOPE_REVIEW.md` (verdict: do not queue the production set as written). The lead checks
the three blocking findings B1-B3 with numbers of its own, from the artefacts (decks, run outputs), with
code written here and not the reviewer's tools, and then amends `scope/SCOPE_G3.md` by dated amendments.

## Entry 1 (2026-11-27 18:03 PST, committed in c4079e991 before any run of this package): predictions and what refutes them

Tool: `tools/check_review.py` (one registered processor run, one core; `athena -m` of the processor build
of core-v0.8 for the mesh structure, then readers of registered outputs; one figure `check_review.png`).

C1 (B1, block counts, my own derivation). AthenaK refines by the 2:1 rule with every level at least one
block of its own size beyond the next finer region, aligned to the blocks of the coarser level. With blocks
of 24 cells and the ES-FL boxes (root 96 cells over +-768 M, `refined_region5` level 7 over +-1.5 M) every
level is 4 blocks wide and the inner 2^3 are refined: 7 x 56 + 64 = 456 blocks (G-8). A level 8 over +-5.9 M
makes level 8 8 blocks wide (+-6 M), and each coarser level must then be 8 blocks wide up to level 1:
7 x 448 + 512 = 3648 (G-16 as written). Level 8 over +-1.4 M (FL16's form) stays inside level 7: 456 - 8 + 64
= 512, level 8 over +-3 M. Blocks of 12 with level 8 over +-5.9 M (G-16b): the cascade stops at level 6:
4096 + 1216 + 296 + 5 x 448 + 448 = 8296. The uniform family (same physical boxes, cell size 2/3 and 1/2 of
G-8 everywhere): root 144 cells with blocks of 36 (G-12u) and root 192 with blocks of 48 (G-16u), each
456 blocks with G-8's level extents, finest dx 1/12 and 1/16 M, finest level +-6 M; root 144 with blocks
of 18: 3648 blocks with G-8's extents. Refuted if `athena -m` gives any other count or extent.
C2 (B1, the smoke rule). The finder at t = 0 (first record of the summaries): FK (M/8) 0.99152, FL16 (M/16)
0.99981 [both read at 18:01 PST, before entry 1 was committed, from the summaries of D-20261123-022725-a553496 and D-20261124-172745-72472ed];
the data's horizon is that of Schwarzschild of M = 1, so the offsets are -8.5e-3 and -1.9e-4, and the rule
"within 3e-4 of ES-F's 0.9915" rejects every finer deck. Refuted if a finer deck could land within 3e-4 of
0.9915 while converging toward 1, i.e. if FL16's t = 0 mass were within 3e-4 of 0.9915.
C3 (B2, the borrowed clock). In FK's snapshot at 200 M, dust particles binned by label R0 (1 M bins): the
spread (5-95 per cent) of their own proper times exceeds 2 M in the bins inside R0 = 30 M, and the median
of a bin differs from the proper time of the nearest surviving tracer label by more than 5 M in at least
one bin with 400 particles. Refuted if the spreads are below 0.5 M and the differences below 1 M in every
bin: then the tracer clock is harmless and B2's first point is wrong.
C4 (B3, power of G3-G3 as written). My own Monte Carlo (not tools/g3g3_power.py): finder samples every
0.5 M, noise per member of sd 3.9e-4 with correlation 0.83 between members (the reviewer's numbers from G2,
checked in C5), white and with a correlation time of 10 M; a converging signal e_h = C h^p with the M/8 -
M/16 difference A after 100 M; the anchor a single sample at 20 M. Prediction: at A = 5.8e-4 and p = 2 the
criterion as written ("env(D_8,12) > env(D_12,16) in every 50 M window, ratio in [1.5, 8]") passes with
probability below 0.3; the amended form (means over 100-400 M, anchor the mean over 20-40 M, a ratio whose
90 per cent interval lies in [1.2, 8]) has power above 0.5 at A = 1.2e-3. Refuted if the written form passes
with more than 0.5 at A = 5.8e-4.
C5 (the noise numbers themselves). High-pass residuals (minus a 20 M running median) of M_AH of FK (M/8, N)
and FL16 (M/16, N, same particle data) from 50 to 295 M: sd of each in [1e-5, 6e-4] and a correlation
between the two above 0.3. Not a criterion of the review; it says whether C4's inputs are in the right
range. Refuted if the correlation is below 0.3 (then the members' noise does not cancel in differences and
C4 is optimistic).
C6 (cost, an estimate and not a measurement). Two brackets for G-8's mesh cost to 400 M: 1.71 (the
reviewer's, from ES-FL and FN4) and 2.54 (mine: FK 2.70 minus one particle part of 0.163 from the matched
pair FK/FN4, EVIDENCE.md lines 59-61). The cost of a deck is G-8's mesh cost times its cells (lower) or
cells with ghost zones (upper) over G-8's, times the step ratio, plus the particle part times the step
ratio. Expected: G-16 as written 25-45 card-hours; G-12u 6-14; G-16u 18-42; G-16b 8-25.

## Entry 2 (2026-11-27 18:06 PST, committed in 50e2cb650): outcome of C1-C6 (run D-20261128-020346-c4079e9, figure looked at)

`check_review.json` and `check_review.png` in `scratch/D-bh-dress/D-20261128-020346-c4079e9/`.
- C1 held for every deck I predicted except one: g8 456, g16c 3648 (finest +-6 M), g16r 512 (+-3 M), g16b
  8296 (+-6 M), g12u 456 (dx 1/12, +-6 M), g16u 456 (dx 1/16, +-6 M), g12c 2176 (dx 1/12, +-4 M, the
  reviewer's G-12) [VERIFIED by athena -m]. FAILED prediction: g12s (root 144, blocks of 18) gives 2472
  blocks with the finest level over +-3 M, not 3648 over +-6 M: level 7 over +-1.5 M is aligned to level-6
  blocks of 3 M, so it covers +-3 M; I carried G-8's +-6 M over without the alignment. Not a candidate.
- C2 held: t = 0 masses FK 0.9915207, ES-FL 0.9915211, EG8 (polished) 0.9915147, FL16 0.9998147; offsets
  from 1 of -8.48e-3 (M/8) and -1.85e-4 (M/16). The written smoke rule rejects any M/16 deck.
- C3 held in its second part and in part in its first: FK at 200 M has dust only from R0 = 24 M out (inner
  labels swallowed); the 5-95 per cent spread of the particles' own proper times is 6.2 M (R0 25-26 M), 2.4 M
  (26-27 M) and 0.4-1.1 M at 27-30 M, so ">2 M in every bin inside 30 M" FAILED for 27-30 M; the
  nearest-tracer-label clock is off from the bin median by up to 12.5 M (R0 24-25 M, nearest label 28 M) and
  by 0.5-2 M across 27-52 M. The reviewer's "up to 15.4 M" is at other snapshots; same size.
- C4 held: the written G3-G3 passes a converging signal of A = 5.8e-4 with 0.14 (p = 2, white noise), 0.12
  (p = 2, 10 M correlation time), 0.10 and 0.09 (p = 1); the reviewer's 0.11-0.15 and 0.08-0.10 are
  reproduced by an independent model. The amended form has power 0.62 at A = 5.8e-4 and 0.997 at 1.2e-3 in
  white noise, but NONE (0.0 at 1.2e-3, 0.41 at 2.4e-3) with a 10 M correlation time: the anchor's noise
  (mean over 20-40 M) then dominates. The power of any G3-G3 form depends on the noise's correlation time,
  which must be measured before the criterion is fixed (amendment A3).
- C5: the high-pass residuals of M_AH (20 M running median removed) of FK and FL16 have sd 1.02e-3 and
  1.01e-3 with correlation 0.997; the high-pass sd of their difference is 2.24e-4, the model of C4 gives
  3.9e-4 x sqrt(2 x 0.17) = 2.27e-4. Prediction held. FL16 - FK is -1.1e-3 to -2.0e-3 over 50-295 M (panel d;
  FK starts the finder at 1.6 M, FL16 at 0.8 M; both unpolished), mean over 250-295 M -1.37e-3: the size of
  the reviewer's e_8 - e_16 = +1.48e-3 (B3).
- C6 (estimates): G-8 1.9-3.0 card-hours to 400 M; G-16 as written 25-37; G-12u 8.8-10.4; G-16u 26-27;
  G-16b 7.7-21; FL16's form 3.5-5.8 (+-3 M only). The particle part from the matched pair FK/FN4 is 0.163
  card-hours per N to 400 M (EVIDENCE.md: FK 2.70, FN4 3.19), not the reviewer's 0.37 (ES-FL at 500 M scaled
  against FN4): G-8-16N then costs 2.70 + 15 x 0.163 = 5.2 card-hours (reviewer 7.6, scope 5.5).

## Entry 3 (2026-11-27 18:06 PST, committed in 50e2cb650 before the runs): predictions for the smoke test of G-8 and the card timing runs of G-12u and G-16u

Decks `decks/g3g8*.athinput`, `g3g12u*`, `g3g16u*` (tools/make_g3_decks.py; diff against EG8: tlim 400 M,
initial_radius_0 1.6 with ah_exc_max_growth 4 (FK's guard radius 6.4 M), z4c slices every 5 M; G-12u root 144
and blocks of 36, G-16u root 192 and blocks of 48).
S-G8 (processors, `.work/build_cpu_v08/src/athena`, two cycles, one core): the input starts; the parameter
dump holds initial_radius_0 = 1.6, ah_exc_max_growth = 4, polish_iterations_0 = 100, diagnostics = true; the
status file has the search at t = 0 found; its mass equals EG8's polished t = 0 mass 0.9915147 within 1e-6
(polishing makes the start radius irrelevant). Refuted, and G-8 not queued, if the input fails, the search
is not found, or the mass differs by more than 1e-5.
T-12u, T-16u (cards, scouting, 2 M each, one job each, cap 0.3 card-hours each; they replace a processor smoke
test, which would take hours for these decks): the run starts and fits one card; the finder is found at t = 0
with masses 0.9990 +- 0.0007 (G-12u: offset -8.5e-3 (2/3)^5.5 from the M/8 and M/16 offsets) and 0.99981 +-
1e-4 (G-16u: FL16's resolution at the puncture); the measured wall seconds per M of evolution over G-8's (read
from EG8's segment logs) in [2.7, 6.6] for G-12u and [7.5, 21] for G-16u (C6's bounds widened by 30 per cent).
Refuted if a run does not fit a card, the search is not found, a mass falls outside its band, or a cost ratio
leaves its band; a cost above the band ends the full-time mesh leg as designed (amendment A1 then restricts it
in time).

## Entry 4 (2026-11-27 18:09 PST, committed in acee85249 before any amended criterion is read): predictions for SCOPE_G3 amendments A1-A4

- P-A1 (family): G-12u's and G-16u's timing runs fit one card; t = 0 masses as entry 3; T-16u's cost puts
  G-16u to 400 M at 18-30 card-hours, so t_16 lies in [270, 400] M [JUDGEMENT]. Refuted if t_16 < 200 M.
- P-A2 (Claim D): on G2's snapshots FN4's |median dtau| per read cell lies in [0.05, 1.0] M (the tracers' lead
  at R0 = 28 M is 0.55 M at 4N, VERIFIER 4.1), so D1* lands in [0.1, 2] M; D2 holds from M/8 to M/16 in at least
  four of five R cells (the lead fell from 0.78 to 0.40 M in G2). Refuted if FN4's medians exceed 2 M (the
  statistic then measures something other than the lead) or D2 fails in two cells or more.
- P-A3 (G3-G2): after the vacuum offset, e-bar_8 - e-bar_16 in [+2e-4, +8e-4] (the lead's part, review B3: about
  3e-4, plus the unpolished rule's 6e-5) and the three members ordered in at least four windows. Refuted if
  the offset-corrected difference changes sign between windows after 100 M.
- P-A3 (G3-G3 power): the phase-randomised surrogates of FK - FL16 noise give a power below 0.8 at 1.2e-3 (the
  difference has visible structure on 10-20 M scales in check_review.png panel d), so G3-G3 becomes a
  reported ratio. Refuted if the power is at least 0.8.
- P-A4 (S1): G-8-16N's measured cost within [4.5, 8] card-hours to 400 M.

## Entry 5 (2026-11-27 18:27 PST): outcome of S-G8 (run D-20261128-020622-50e2cb6, processors, one core, 1047 s)

HELD. The input starts; the parameters held by the restart file of cycle 0 are tlim 400, initial_radius_0 1.6,
ah_exc_max_growth 4.0, polish_iterations_0 100, diagnostics true; MeshBlock-cycles 912 = 456 x 2 (the count of
`athena -m`); the status file has the search at t = 0 found after 136 flow iterations (EG8's S1: 126 from
0.8 M), area mass 0.991514686070498, EG8's polished t = 0 mass 0.9915146860705 (difference about 1e-15,
prediction: within 1e-6). Two cycles, exit 0. No figure: the test checks integers, flags and one mass.
Core's message restart-parameters-and-finder-check item 3: no G3 deck sets `deposit_comp_c` or
`deposit_fine_shape` (grep of decks/*.athinput), so the candidate's deposit fixes do not touch these runs.
G-8 is queued next (priority 2, production, chain, cap 3.5 card-hours).

## Entry 6 (2026-11-27 23:40 PST, lead of batch 40, before the timing reader is run): what was seen, the reader

Seen before this entry (to close run D-20261128-055309-41ea07a): `batch.list.status` gives rc 0 for t12u and
rc 134 for t16u; sacct of job 5610 COMPLETED; t16u's log ends with "Kokkos ERROR: Cuda memory space failed to
allocate 10.74 GiB (label="dg")" after 456 blocks were set up (peak 76223 MiB); t12u's log, its peak (69043 MiB)
and the first line of its status file (found, mass 0.99975). The run was closed with `nrpic-run finish`
(status failed, exit 134 of the second member). Reader `tools/timing_read.py` (one registered processor run):
G-8's seconds per M from EG8's long segments, T-12u's from its log, the memory of the three decks with a line
through the two measured peaks, the cost to 400 M by A1's rule (seconds per M x 400 M x 1.15), and the checks
of entry 3 and P-A1 as written; one figure `timing_read.png`. What the reader cannot change is already plain:
T-16u does not fit one card, so entry 3's "fits a card" and P-A1 are refuted for G-16u before the reader runs.

## Entry 7 (2026-11-27 23:44 PST, lead of batch 40): outcome of T-12u and T-16u (run D-20261128-055309-41ea07a; reader runs D-20261128-074025-07d95a4, which found no G-8 segment through a parse defect, and D-20261128-074128-24b2565 after the fix; figure `timing_read.png` looked at)

Outputs: `scratch/D-bh-dress/D-20261128-074128-24b2565/timing_read.json`, `timing_read.png`.

T-12u (G-12u, root 144, blocks of 36):
- HELD: fits one card (peak 69043 MiB of 81920, 84 per cent); 456 blocks in eight physical levels (the `athena
  -m` count); the search at t = 0 found after 139 flow iterations; wall seconds per M 73.8 (2 M after a start-up
  of 12 s) against G-8's 19.4 (EG8's long segments, cpu seconds minus start-up over the span), ratio 3.81, band
  [2.7, 6.6]; A1's rule -1e-4 <= 1 - M_0 <= 8.5e-3 holds (1 - M_0 = 2.5e-4).
- FAILED: the mass band 0.9990 +- 0.0007 of entry 3. M_0 = 0.99975, 5e-5 above the band. The t = 0 offsets
  8.5e-3 (M/8), 2.5e-4 (M/12), 1.85e-4 (M/16 at the puncture, FL16) follow no power of h; my (2/3)^5.5 scaling
  was wrong. [JUDGEMENT: at t = 0 the horizon's coordinate radius is 0.5 M, four cells of M/8; the M/8 offset is
  a few-cell effect that has gone at M/12.] One search of the 2 M (t = 0.667 M) was not found (mean expansion
  above hmean_tol), as EG8's at t = 1.0 M.
T-16u (G-16u, root 192, blocks of 48): REFUTED, it does not fit one card. After the 456 blocks were set up,
  Kokkos failed to allocate 10.74 GiB (label "dg") with 76223 MiB in use; exit 134 at 3 s. The line through the
  two measured peaks (6.2 GiB fixed plus 1696 bytes per cell over the 456 blocks with ghost zones) gives 132.6 GiB
  for G-16u, 1.66 cards. The largest block of this family that fits one card at 97 per cent is 38 cells (M/12.7).
  [JUDGEMENT: 10.74 GiB is 18 doubles per cell of 456 blocks of 56^3, the metric derivatives that `metric_drvts =
  interpolant` keeps; dropping them alone would leave about 122 GiB.]
P-A1 REFUTED: G-16u's timing run does not fit; t_16 is not defined on one card. By A1, the full mesh leg as
  designed ends, and the orchestrator rules before G-16u is queued.

Cost of the mesh leg to 400 M by A1's rule (measured seconds per M x 400 M x 1.15): G-8 2.48 card-hours (q0100,
in Slurm), G-12u 9.43 (cap 11), G-16u 25.9 if it ran at one card's speed (cells x steps over G-8, times G-12u's
measured efficiency 0.98; on two cards the communication is not measured and adds to it). With G-16u at 400 M
the G3 total is about 51 card-hours (G-8 2.5, G-12u 9.4, G-16u 25.9, particle leg 3.2 + 5.2, gauge leg 2.7, EG8
1.5, timing 0.05), inside the 60; A1's cap of 20 card-hours for G-16u would stop it at about 309 M. The
obstacle is memory, not card-hours: no executable runs G-16u on this machine (one card per job; no card build on
two ranks is published). What is lost if the leg stays on one card: the M/16 member, and with it the third mesh
member that A3's G3-G2 order and G3-G3 ratio need; G-8 and G-12u alone give one difference and no order.

## Entry 8 (2026-11-28 08:03 PST, lead of batch 41, before the runs it predicts): ruling 0051 item 3; predictions for the M/6 checks, the build identity and the read of G-8

Ruling (coord/DECISIONS/0051 item 3): no run on two cards; the mesh leg is G-8 and G-12u and, if it qualifies,
a coarser uniform member G-6u (its timing run finds the horizon at t = 0 and a null test at M/6 stays within
the bound of criterion N); three members then give an order, otherwise the difference of the two finer members
is quoted with no order and FL16 (refined M/16, G2) stands beside them. Decks of A6 (tools/make_g3_decks.py,
function write_m6): g3g6u (root 72, blocks of 18; G-8's deck otherwise), g3g6u_t2 (tlim 2 M), n6es and n6v
(g2long's ES-1L and V-1L at root 72, blocks of 18, tlim 300 M, polished finder with diagnostics). The existing
decks are unchanged (git diff empty).

Seen before this entry: chain status DONE of q0100 (job 5691 COMPLETED, 400 M), sacct of its ten jobs (seven
PREEMPTED, three COMPLETED), and the last three lines of g3g8.horizon_status_0.txt and two of the summary (found;
area mass 1.4918 and smallest radius 4.528 M at 399.5 M). Nothing else of G-8's outputs. The radius at 399.5 M is
therefore not a prediction below.

Processor checks (tools/m6_smoke.py, one registered run, four cores, release core-v0.9 processor build):
- K1 (athena -m): g3g6u, n6es and n6v each 456 blocks in eight physical levels, finest dx 1/6 M over +-6 M (the
  uniform family's structure with blocks of 18; check_review's C1 rule). Refuted if any count or extent differs.
- K2 (two cycles each): every input starts, exit 0, 456 MeshBlocks. The search at t = 0 [JUDGEMENT; the horizon
  of the data is at coordinate radius 0.5 M, three cells of M/6]: found in g3g6u with area mass M_0 in
  [0.95, 0.9915] (further from 1 than G-8's 0.99151, since the offset falls with h: 8.5e-3 at M/8, 2.5e-4 at M/12);
  n6es and n6v found with masses equal to each other within 1e-6 (same puncture, the vacuum bubble out to 36 M).
  Refuted if a search at t = 0 is not found or a mass leaves its band. A not-found search at t = 0 on processors
  means the card timing run will not qualify G-6u either (processor and card finder agree to 2.2e-16 with
  polishing, finder_stop.md): G-6u is then not run, and the leg is the two finer members with no order.
- K3 (build identity): g3g8.athinput for two cycles with core-v0.9 gives every output of S-G8 (core-v0.8, run
  D-20261128-020622-50e2cb6, same command) byte for byte, the restart files included; at most the parameter
  block differs, if v0.9 records options with defaults. Reason: the deck sets neither deposit_comp_c (default
  0.0, athenak/src/particles/nrpic.cpp:99) nor deposit_fine_shape, and the three changes of v0.9 without an
  option act only with those or on a restart. Refuted if any output differs after its parameter block. If K3
  holds, the mesh family is one build in effect: G-8 (v0.8) beside G-12u and G-6u (v0.9). If K3 fails, G-12u and
  G-6u run on core-v0.8, the build of G-8 (one build per family).

Read of G-8 (run D-20261128-062142-c5666c4; reader tools/g8_read.py, one registered processor run, one figure):
- G3-G1 (scope section 4, fixed): every counted bin (10 M of tau_rem with at least 20 dust removals, tau_rem from
  50 M to the end) within +-0.5 per cent. Refuted if any bin lies outside.
- P-G1 (scope section 9): bins in [+0.05, +0.30] per cent before the lead correction, [-0.10, +0.25] after it.
- Sharper, from FK (the same deck without polishing: bins in [+0.162, +0.249] per cent, g2long entry 19) and EG8
  (polished, 0.18-0.25 per cent to 260 M, decision 0051 item 3): every bin in [+0.12, +0.30] per cent before the
  lead correction. Refuted if a bin lies below +0.10 or above +0.35 per cent.
- Lead carried as a bias (scope section 6): Delta tau_lead(R0) at M/8, N from the verifier's tracers (VERIFIER
  section 4.1: below 0.01, 0.17, 0.78 M at R0 = 10, 20, 28 M), linear between those points and two brackets
  beyond 28 M (held at 0.78 M; extrapolated with the 20-28 M slope). The shift of the bin medians from the lead
  correction, after tau_rem = 100 M, in [2e-4, 1.2e-3] (the verifier's 6e-4 at R0 = 28 M) for the held bracket.
  Not a criterion: the lead is measured per particle by A2's reader on G2's snapshots, which is not yet run.
- Excision (A1, section 2 flag rule): no dust removal by reason 2 after the first 2 M of a segment.
- Finder: at least 99 per cent of the searches after 2 M found (EG8's E4); G-8 minus FK at common search times
  20-399.5 M with median in [2e-5, 1.2e-4] (EG8's E3: polished minus unpolished).
- Slope s_8(a) = d ln M_AH / d ln a in windows of 0.1 in ln a from tau = 50 M (A4 S3) within 0.03 of s_LTB in every
  window. Information only: G3-G5 is read at the finest member.
- Cost: the sum of the elapsed times of the ten jobs in [1.9, 3.0] card-hours (entry 7: 2.48).
Claim D is not read from G-8: D1* is not yet fixed (A2).

## Entry 9 (2026-11-28 08:08 PST, lead of batch 41): outcome of the read of G-8 (run D-20261128-062142-c5666c4 closed by nrpic-run finish, 242 files, card-hours 2.1986 by sacct; reader D-20261128-160553-b500509 after D-20261128-160544-089d6f8 failed at a syntax error of the reader; figure g8_read.png looked at)

Outputs: `scratch/D-bh-dress/D-20261128-160553-b500509/g8_read.json`, `g8_read.png`. 119584 dust removals read
(R0 from 3.29 to 31.55 M, tau_rem to 492.3 M); the filtered summary dropped no row (every search after 2 M found).
- G3-G1 HELD: 45 counted bins from tau_rem = 50 M to the end, medians +0.172 to +0.254 per cent (limit +-0.5).
- P-G1 HELD: raw in [+0.05, +0.30] per cent; with the lead correction +0.115 to +0.241 per cent (held bracket) and
  +0.100 to +0.241 (extrapolated), inside [-0.10, +0.25].
- Entry 8's sharper band [+0.12, +0.30] per cent HELD (no bin below +0.10 or above +0.35).
- Lead bias: FAILED as predicted in size. The shift of the bin medians after 100 M is 1.05e-4 to 6.3e-4 (mean
  4.6e-4, held bracket; 1.05e-4 to 7.4e-4 extrapolated), not inside [2e-4, 1.2e-3]: the bins just after 100 M
  hold shells of R0 near 20 M whose lead is 0.17 M, which I did not weigh. The corrected medians fall with time
  (about +0.23 per cent at 50-130 M to +0.12-0.16 per cent after 300 M, panel b), the raw ones less (+0.24 to +0.20):
  the lead correction grows with R0 as the lead does. Not a criterion; A2's per-particle lead replaces the
  verifier's three tracer values when it runs.
- Excision HELD: all 119848 dust removals by reason 3 (FK: the same count to 399.5 M, g2long entry 19); no reason 2;
  smallest horizon radius 4.528 M and mass 1.4918 at 399.5 M (seen before entry 8, not a prediction).
- Finder HELD: 795 of 795 searches after 2 M found; t = 0 mass 0.99151469 (S-G8's 0.991514686, entry 5).
  G-8 minus FK: median 1.09e-4 in [2e-5, 1.2e-4] as written, BUT not constant (panel d): it rises nearly linearly
  from 6.5e-5 at 20 M to 1.6e-4 at 400 M and leaves the band after about 220 M, with a dip to -7e-5 at 38-50 M
  (its cause not read: a step of either finder; G-8's searches there are all found). Not predicted: the gap between the polished
  and the unpolished rule grows with the hole [JUDGEMENT: with the area, as the mass rule's stopping tolerance is
  relative]. Every G3 member uses the polished finder, so it does not enter member differences; it does enter
  any comparison with G2's unpolished FK, FN4, FNQ and FL16 (FL16's cross-check of A6 carries it).
- Slope (information): eight windows of 0.1 in ln a from tau = 50 M, |s_8 - s_LTB| at most 0.0027 (limit 0.03).
- Cost HELD: 2.21 card-hours from the segment logs, 2.20 by sacct, in [1.9, 3.0]; seven of ten jobs preempted.
Summary: at M/8 the code reproduces the exact LTB growth law to +0.17 to +0.25 per cent in every bin from 50 to
492 M of the swallowed dust's proper time, +0.10 to +0.24 per cent once the shells' lead is carried; the growth's
logarithmic slope agrees to 3e-3. One member: no mesh statement. Claim D not read (D1* not fixed).

## Entry 10 (2026-11-28 08:09 PST, lead of batch 41, before any of these runs is queued): predictions for the card runs of A6

Entries, all priority 2 (scope A6; queue ids in HANDOFF): T-6u (batch, one job, `decks/timing6.list`, cap 0.2),
N6-ES and N6-V (chains, caps 1.2 each), G-12u (chain, cap 11). Build: release core-v0.9 if K3 of entry 8 holds,
core-v0.8 otherwise (A6, builds).
- T-6u (Q1 of A6): starts and fits one card, peak memory in [12, 26] GiB (trap 33's line: 6.1 GiB plus 1696 bytes
  per cell over 456 blocks of 26^3 with ghost zones gives 18.8 GiB); 456 blocks; the search at t = 0 found, with the
  mass of the processor smoke test K2 within 1e-6 (the polished finder agrees between card and processors to
  2.2e-16, finder_stop.md); wall seconds per M of evolution in [6, 14] [JUDGEMENT: 0.32 of G-8's cells x steps on
  its mesh part of 17.9 s per M, blocks of 18 less efficient than 24 by up to 1.6, plus 1.1 s per M of particles], so
  G-6u to 400 M by A1's rule (x 1.15) in [0.8, 1.8] card-hours. Refuted if the search is not found (Q1 fails), the
  mass differs from K2's by more than 1e-6, or the seconds per M leave the band.
- N6-ES, N6-V (Q2 of A6): both reach 300 M, no guard file, exit 0; at least 99 per cent of the searches after 2 M
  found in each; t = 0 masses equal within 1e-6; max over common search times 100-300 M of |D_ES - D_V| in [3e-5,
  1.5e-4] [JUDGEMENT: G2's tight re-search at M/8 gave at most 7.3e-5, fp_analyse run D-20261124-172508-c847ee4; the
  production finder's floor was 2.28e-4 at M/8 and 1.99e-4 at M/16; M/6 resolves the vacuum hole with fewer cells,
  which moves both members alike]. Q2 holds (A6) if the maximum is at most 2.0e-4; refuted (and G-6u not run) above.
  Cost each in [0.4, 1.0] card-hours.
- G-12u: reaches 400 M inside its cap of 11 card-hours (measured rate 73.8 s per M: 8.2, 9.4 with A1's 15 per cent);
  every dust removal by reason 3; at least 99 per cent of the searches found; G3-G1 holds with raw bin medians in
  [+0.05, +0.25] per cent; the window means e-bar_12 below e-bar_8 in at least four of the six 50 M windows after
  100 M [JUDGEMENT: the lead falls with h, 0.78 M at M/8 to 0.53 M predicted at M/12]. Refuted for the direction if
  e-bar_12 exceeds e-bar_8 by three standard errors in any window after 100 M. No G-12u output is read for a
  criterion before the processor work of A5 is committed (A6).

## Entry 11 (2026-11-28 08:21 PST, lead of batch 41): the search at t = 0 at M/6 is not found; predictions for the smoke tests of the particle and gauge legs

Seen in the M/6 smoke tests of run D-20261128-160418-b618bff while it runs (the run is closed and its json read
in entry 12): the search at t = 0 is NOT found in any of the three M/6 decks. g3g6u (start 1.6 M): reason 6 (flow
iteration limit 400 reached without convergence of the mass), area mass 1.00533, mean radius 0.607 M, smallest
0.598 M. n6es and n6v (start 0.8 M): identical rows, reason 6, area mass 1.00092, mean radius 0.617 M. At M/8 the same
finder on the same data stops found after 136 iterations at 0.991515 (S-G8, entry 5). K2's prediction "found" is
REFUTED for all three; its "n6es and n6v equal" holds (identical rows). By entry 8 and A6, Q1 fails on processors:
the finder at M/6 cannot settle on the horizon of the data (coordinate radius 0.5 M, three cells), as M/4 lay outside
the convergent regime at G2. Consequence by A6: G-6u is not run; the null pair at M/6 is not queued (Q2 no longer
decides anything); the mesh error is the envelope of |e-bar_8 - e-bar_12| with no order, FL16 beside it. The card
timing run T-6u, the ruling's literal test, is queued once (one job, cap 0.2) so that the card's own search at
t = 0 is on record [JUDGEMENT: the same finder on a metric that differs at round-off will not converge either].
Not done: a retest with more flow iterations or another start radius at M/6; a setting chosen after seeing the
failure would not be the qualifying test the ruling names.

Next step the amended scope allows (A6 order 4-5): the particle leg G-8-4N and the gauge leg G-8-e1 (decks
`g3g84n`, `g3g8e1` from tools/make_g3_decks.py, function write_legs; the existing decks unchanged). Smoke tests
(tools/legs_smoke.py, one registered run, two cores, core-v0.9 processor build, two cycles each):
- S-4N: exit 0, 456 MeshBlocks, 3402632 particles read; the search at t = 0 found with area mass within 1e-9 of
  G-8's 0.991514686 (the metric data are the same table, `esf.tab` identical byte for byte; the particles do not
  enter the slice at t = 0); peak resident memory below 40 GiB. Refuted if any fails.
- S-e1: exit 0, 456 MeshBlocks, 850724 particles; the search at t = 0 identical to S-G8's row (shift_eta does not act
  before the first step). Refuted if the t = 0 row differs in any printed digit.
Card runs after them (if K3 holds, core-v0.9): G-8-4N to 400 M, cap 4 (FN4 cost 3.19 card-hours to 400 M at
release v0.6, EVIDENCE.md; prediction [2.6, 4.0]); G-8-e1 later (two D chains at most: G-12u and G-8-4N).
