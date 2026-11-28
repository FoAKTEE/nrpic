# JOURNAL of package g3/amend (Track D): the lead's own check of the G3 scope review before the amendment

Owner D-bh-dress, lead of batch 35 (2026-11-27 evening). Purpose: decision 0048 item 4 and the review
`g3/scope_review/SCOPE_REVIEW.md` (verdict: do not queue the production set as written). The lead checks
the three blocking findings B1-B3 with numbers of its own, from the artefacts (decks, run outputs), with
code written here and not the reviewer's tools, and then amends `scope/SCOPE_G3.md` by dated amendments.

## Entry 1 (2026-11-27 18:05 PST, before any run of this package): predictions and what refutes them

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
0.99981 [both read at 18:01 from the summaries of D-20261123-022725-a553496 and D-20261124-172745-72472ed];
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

## Entry 2 (2026-11-27 18:25 PST): outcome of C1-C6 (run D-20261128-020346-c4079e9, figure looked at)

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

## Entry 3 (2026-11-27 18:28 PST, before the runs): predictions for the smoke test of G-8 and the card timing runs of G-12u and G-16u

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
