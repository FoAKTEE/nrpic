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
