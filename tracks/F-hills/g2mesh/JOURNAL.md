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
