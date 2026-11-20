# g2mesh journal (helper of F-hills, wave 3 round 1)

Question: does the G2 resolution triple of the q = 4 passage fit one card? Slots above 2700
at 16^3 MeshBlocks, and 32^3 MeshBlocks on the three-hole mesh. Predictions are written
before each test, outcomes after, failed ones included.

## 2026-11-20 G2M-1. MeshBlock trees of P1's set-up at three resolutions (prediction)

Set-up: `tracks/F-hills/nr_first/inputs/p1_q4.athinput` (P1): domain +-256, root 64^3, 10
levels, members (m = 0.125) at level 9 with cells 1/64 = m/8, the heavy hole (M = 1) at
level 6 (M/8), wave zone level 2 within 48 and level 1 within 100 of the origin.

Resolutions (the domain is kept; [JUDGEMENT] on the choice):
- R8   nx = 64,  10 levels: members m/8, heavy M/8, wave zone cells 2 / 4 (P1 itself).
- R12  nx = 96,  10 levels: every cell 2/3 of R8: members m/12, heavy M/12, wave zone
       4/3 / 8/3. The root must be a multiple of the block (16 or 32), so 96 is the only
       root between 64 and 128 that serves both block sizes; m/11.3 (ratio sqrt 2) would need
       nx = 90.5 or a domain of +-271.5 with nx = 96.
- R16n nx = 64,  11 levels: members m/16, heavy M/16 (level 7), wave zone unchanged 2 / 4
       (the wave-1 row of SCOPING section 9, l. 179).
- R16u nx = 128, 10 levels: every cell 1/2 of R8, wave zone 1 / 2 (a uniform triple
       R8, R12, R16u with ratios 1.5 and 4/3).
Each for 16^3 and 32^3 MeshBlocks (32^3: root 2, 3, 2, 4 blocks per side).

Model: `scripts/tree3.py`, the rules of `nr_first/scripts/tree_check.py` (E11: exact against
the restart trees of one puncture) extended to several trackers, each with its own radius
(0.999 x 1.8 x mass) and level (`nrpic_puncture_setup.hpp` lines 113-132), and written level
by level with sets (fast enough for hundreds of trees). Two rules:
- start rule (cycle 0): `<refined_region_punc<n>>` cubes of half-width 1.8 x mass at the
  puncture's level, a block refined when it overlaps the open cube (`mesh/build_tree.cpp`
  lines 134-183), no wave-zone criterion (it acts only at regrids);
- regrid rule (cycle > 0): tracker spheres (`z4c/z4c_amr.cpp` lines 80-132) and the corner
  rule about the origin (lines 329-372), both with the 2:1 rule over all 26 neighbours.

Predictions:
1. The start rule at P1's input gives 1716 MeshBlocks, the start count of the P1 smoke on a
   card (`nr_first/JOURNAL.md` l. 620; log of run F-20261115-174602-c6879fe). Refuted if not.
2. The regrid rule at P1's tracker positions equals the trees of P1's restart files
   (`scratch/F-hills/F-20261119-150017-b45ec5f/rst/hills.000NN.rst`, t = 5, 10, ..., 110)
   level by level, or within 2 percent in total where derefinement lags behind the moving
   punctures. Refuted if a total differs by more than 2 percent.
3. R8 along the Newtonian track to 280 M (full Newtonian three-body problem from P1's
   state, `stage/G0/checks/lead_checks.newton_full`, as `nr_first/scripts/baselines_p1.py`):
   maximum between 1716 and 2080 (2080: the wave-1 maximum, SCOPING l. 178).
4. R16n, 16^3: start 2514 and maximum 2864 within 5 percent (SCOPING l. 179, made with
   `athena -m` and cube regions). So above the 2700 slots of P1: refuted if the maximum
   along either track stays below 2700.
5. R12, 16^3: maximum 1900-2600 [JUDGEMENT: the nests of the punctures, about 56-64 blocks
   per level each, do not change; the wave zone and the 2:1 padding of the coarse levels
   grow by up to (3/2)^3].
6. R16u, 16^3: 10-50 percent above R16n.
7. 32^3: 0.5-0.9 of the 16^3 count of the same mesh, so 4-7 times its cells [JUDGEMENT:
   a nest level has about the same number of blocks at any block size, the wave zone 8 times
   fewer].

## 2026-11-20 G2M-2. One card batch job, four short cases (prediction)

List `inputs/batch_g2mesh.list`, release core-v0.3 (`.work/build_gpu_v03/src/athena`), 64
cycles each, every file output off (`outputN/dt=-1`) except the history. Slots chosen from
run F-20261120-222636-46d03e0 (`scripts/bench_cases.py`: the start tree and the tree of the
first regrid, model equal to `athena -m` level by level for all 14 cases):
(i) `m16_b16_s3000` P1 at m/16 (R16n: 11 levels, 2514 blocks at the start, 2486 after the
first regrid), 16^3, 3000 slots; (ii) `bt7_b32_s460` core's three-hole mesh by_triple with 7
levels at 32^3 (456 blocks), 460 slots; (iii) `bt7_b16_s1000` the same mesh at 16^3 (932
blocks), 1000 slots; (iv) `m8_b32_s1150` P1 at m/8 with 32^3 blocks (1128 at the start, 1114
after the first regrid), 1150 slots.
Why not core's bench16 / bench32 lines: bench32 (by_triple, 8 levels, 32^3, 560 slots) needs
932 slots at the start (run F-20261120-222636-46d03e0, model and `athena -m`), so it would
stop at once (`mesh/build_tree.cpp` lines 275-281); (ii) and (iii) are the same comparison on
a by_triple that fits.

Predictions:
1. (i) allocates and runs 64 cycles. Peak card memory 78.5 GB +- 1.0 GB: 70847 MiB at 2700
   slots (E7, `nr_first/JOURNAL.md` l. 626) + 300 x 25.65 MiB (core READY of core_requests-adf,
   MEMORY) = 78542 MiB, below the 81920 MiB of the card. Rate 1900-2300 MeshBlock-cycles/s
   (P1's chain segments 1963-2242, part C of run F-20261120-222426-86392c3; E7 2057).
   Refuted by an out-of-memory stop at the start, a peak above 80 GB, or a rate below 1700.
2. (ii) allocates. Memory per 32^3 slot 110-130 MiB [JUDGEMENT: the arrays of a slot hold
   ghost zones, (32+8)^3 / (16+8)^3 = 4.63 times a 16^3 slot = 119 MiB; 8 x 25.65 = 205 MiB
   if none did], so a peak of 52-62 GB (fixed part taken as 1.6 GB = 70847 - 2700 x 25.65 MiB).
   Refuted by an out-of-memory stop (more than about 175 MiB per slot) or by a peak outside
   45-70 GB.
3. Zone-cycles per second at 32^3 (ii) equal to or higher than at 16^3 (iii), up to 2 times
   [JUDGEMENT: the ghost-zone work per cell falls from 3.4 to 1.95 cells per cell]. Refuted
   by a lower rate at 32^3. (iii) runs 1800-2300 MeshBlock-cycles/s.
4. Problem time per wall second on the same mesh: (iii) 2-4 times faster than (ii), because
   the 32^3 tree has 3.9 times the cells (14.9 M against 3.8 M, run F-20261120-222636-46d03e0).
   Refuted if (ii) is as fast as (iii) or faster.
5. (iv) stops out of memory at the start: 1150 x 110-130 MiB = 124-146 GB. Refuted if it
   allocates (then a 32^3 slot is below 70 MiB and the 32^3 option must be looked at again).
Consequence planned: the cost table uses the measured memory and rates; 16^3 at about 3000
slots is the default if 1 holds.

## 2026-11-20 G2M-1, outcome (run F-20261120-222426-86392c3, `model.json`; figures `fig_model_check.png`, `fig_blocks_time.png` read)

Card job of G2M-2 submitted before this entry was written: run F-20261120-222810-e408386,
Slurm job 4744 (queued behind P1's chain, job 4738).
- Part A: tree3 equals tree_check of nr_first level by level at all 16 trees (8 positions, two
  rules) [VERIFIED].
- Part B: the start rule equals `athena -m` of core-v0.3 level by level for all 8 variants and
  core's by_triple at 16^3 (1100) and 32^3 (932) [VERIFIED].
1. Met: the start rule gives 1716 at P1's input.
2. Met [VERIFIED]: 22 of the 23 restart trees of P1 (t = 0 ... 110) equal the model level by
   level; the tree at t = 10 (1842) equals the model at the tracker positions 8 cycles earlier,
   the regrid before the output. So AthenaK keeps no block that the rules do not ask for: the
   model is the tree, given the positions at the last regrid. P1's trees range 1016-1870; the
   chain segments' mean counts (MeshBlock-cycles / cycles) are 1839, 1590, 1515, 1326, 1245,
   1262 and their rates 2242, 2186, 2171, 2061, 2028, 1963 MeshBlock-cycles/s.
3. FAILED (slightly): R8 along the Newtonian tracks reaches 2136 (t = 185.75), above the
   2080 of wave 1; along P1's measured tracks (0-112.4 M) max 1940, mean 1420, while the
   Newtonian tracks give mean 1578 over the same 0-112 M: P1's punctures sit less often on
   block edges than the Newtonian ones, which is chance, not a trend [JUDGEMENT].
4. Met: R16n start 2514 and maximum 2864 (t = 279.0, Newtonian), the wave-1 row exactly; along
   P1's tracks max 2584. So above 2700, by 6 percent.
5. FAILED high: R12 reaches 2750 (Newtonian; 2442 along P1), above the predicted 1900-2600:
   the wave zone and the coarse levels grow more than I allowed (178 + 260 blocks on levels
   0-1 at the maximum against 36 + 196 at R8).
6. Met: R16u reaches 3466 (Newtonian), 21 percent above R16n; at its first regrid already
   3130, so it does not fit 3100 slots even at the start.
7. Met: 32^3 trees are 0.62-0.84 of the 16^3 trees of the same mesh and hold 4.9-6.7 times the
   cells (maxima 58.5-70.0 M cells against 8.7-14.2 M). R16n and R16u at 32^3 are the same tree
   as R8 at 16^3 (same block edges and levels, at every sample).
The 16^3 series are spiky (a puncture nest crossing a block edge adds or removes 28-140
blocks at once), so the maximum at 0.25 M sampling may miss spikes between the regrids.

## 2026-11-20 G2M-1b. Maxima at the regrid cadence (prediction)

`scripts/fine_max.py`: every 16^3 variant at every 8th cycle of its own step (0.03125 M at
m/8, 0.0208 M at m/12, 0.015625 M at m/16), along P1's tracks (interpolated) and the Newtonian
tracks to 280 M. Prediction: the maxima are 0-3 percent above those at 0.25 M sampling (R8
2136-2200, R12 2750-2833, R16n 2864-2950, R16u 3466-3570), and R16n never exceeds 3000.
Refuted by a maximum more than 3 percent higher, or R16n above 3000.
