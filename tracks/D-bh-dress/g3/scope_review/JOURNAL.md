# JOURNAL of package g3/scope_review (Track D): independent review of the G3 scope before its runs

Helper of D-bh-dress, batch 34, 2026-11-27. I did not write `scope/SCOPE_G3.md` (lead of batch 34,
commits e92904aed and acb5f7202) nor any of the G2 runs read here. No card time; processors only, one
core per calculation.

## Entry 1 (2026-11-27 16:40 PST, before any calculation): what I test and what I expect

Read: CLAUDE.md; coord/CHARTER.md to "Owners"; brief lines 394-405, 766-783, 834-860; decision 0045;
`scope/SCOPE_G3.md` (whole); `scope/SCOPE.md` sections 1-5; `stage/G2/GATE_REVIEW.md` (whole);
`stage/G2/VERIFIER.md` (whole); `g2long/JOURNAL.md` entries 1, 4-6, 19, 24-27; `excguard/JOURNAL.md`
entries 1-2; `coord/INTERFACES/finder_stop.md`; docs/FORMATS.md line 123 (snapshots carry the proper
time of every particle).

Three registered calculations, each with predictions and what refutes them.

### A. Block counts of the three mesh members (AthenaK `-m`: mesh structure only, no physics)

Decks made by `tools/make_decks.py` from `g2long/inputs/esfl.athinput` (G-8) with exactly the change the
scope names: G-16 adds `<refined_region6> level = 8` over +-5.9 M (scope section 3 table); G-12 sets the
root to 144 cells over +-768 M with blocks of 24 (scope section 3 table). Executable: release core-v0.8,
`.work/build_cpu_v08/src/athena -m`.
- A1: G-8 has 456 MeshBlocks (g2long entry 4). Refuted if not 456 (then the -m count is not the run's).
- A2: G-16 as described has far more than the scope's "about 2.5 times the blocks" (1140): level 8 over
  the whole level-7 box (+-6 M) puts level-8 blocks next to level-6 blocks, and the 2:1 rule of the tree
  should cascade a refined shell out to the root; I expect at least 3000 blocks (my count: 512 + 8 x 448
  = 4096). Refuted (the scope's 2.5 holds) if at most 1500.
- A3: G-12 as described has 1539 blocks (189 leaves on each of levels 0-6 and 216 on level 7; scope's
  "about 3.4 times"). Refuted if outside [1400, 1700].
- A4 (added 16:42, before any run): a cheaper form of G-16, the same deck with blocks of 12 cells
  (G-16b): the cascade stops after two levels; I expect about 8000 blocks of 12^3 (2.3 times G-8's
  cells). Refuted outside [5000, 12000]. Informational: it tells the lead whether a +-6 M level 8 exists
  at the scope's cost at all (with 4 ghost cells a 12^3 block costs about twice a 24^3 block per cell
  [JUDGEMENT]).

### B. What the G3 criteria of Claim G can see, read on G2's registered outputs (one factor coarser)

Script `tools/g2_analogs.py`, reading only finder summaries (column 2 time, 3 mass) and the registered
`esf_criteria.json` of ES-FL, FK, FN4, FNQ, FL16 (run ids in the script) and nothing of the track's tools.
- B1 (G3-G4 analog): the ratio of the 50 M-window rms of M_N/4 - M_N to that of M_N - M_4N (FNQ, FK,
  FN4), windows 50-100, ..., 350-400 M. I expect at least one of the seven windows outside [1.4, 3]
  (G2's +-25 M windows gave 3.1, 2.5, 2.5, 1.9). Refuted if all seven inside.
- B2 (G3-G3 power): a Monte Carlo with noise surrogates (phase-randomised copies of the measured
  M_N - M_4N series, rescaled to one member at N) and a deterministic mesh difference of order p = 2
  normalised to G2's mean (Delta M_16 - Delta M_8) = +5.8e-4 over 250-299 M (gate review R5). I expect
  the probability that G3-G3 passes as written (env(D_8,12) > env(D_12,16) in every 50 M window after
  100 M, ratio in [1.5, 8]) below 0.2 even when the code converges at order 2. Refuted if above 0.5.
- B3 (G3-G2 analog): per 10 M bin of tau_rem (50-280 M, excision on in both), e_8 - e_16 (ES-FL minus
  FL16). Expected mean +1e-4 to +6e-4 (the lead bias alone: 6.6e-4 at M/8 minus 3.4e-4 at M/16), with
  bin-to-bin scatter comparable to the mean, so that the sign fails in at least 20 per cent of the bins.
  Refuted if the mean is negative or above 1e-3, or if the sign holds in every bin.
- B4 (model test of G3-G1 and G3-G5 with a known defect): ES-FL loses excision at 219.5 M, FK does not
  (g2long entry 19). G3-G1 (+-0.5 per cent) flags ES-FL (largest bin 0.62 per cent, known) and passes FK.
  For G3-G5 (slope d ln M_AH / d ln a over windows of 0.1 in ln a against the exact slope, tolerance 0.03)
  I expect ES-FL's largest deviation between 0.03 and 0.06 (a marginal detection of the excision end) and
  FK's below 0.03. Refuted (G3-G5 blind to the excision end) if ES-FL's largest deviation is below 0.03.
- B5 (arithmetic, no run): the lead bias on r (6e-4 at M/8, VERIFIER 4.1) is a tenth of G3-G1's band.

### C. What Claim D's statistic measures, on the exact solution and on a G2 snapshot

Script `tools/dress_model.py`: exact LTB shells (cycloid with E = -M/R0, R_max = m R0 / M; tested first
against `esf_growth.csv` tau_horizon), the real particle labels and rest masses (`esf_labels.npz` of data
run D-20261121-203042-82deeec) and the proper times of FK's snapshots (run D-20261123-022725-a553496;
docs/FORMATS.md line 123).
- C0 (closed-form test): my tau_H(R0) equals the csv's to 1e-8 relative. Refuted above 1e-6 (then the
  model is wrong and C1-C3 are not read).
- C1: between 1.5 R_AH and 10 M at the snapshot times 100, 200, 300 M there are O(1e3-1e4) particles at N
  in all, and at least one logarithmic bin (eight bins from 1.5 R_AH to 40 M) of the inner range holds
  fewer than 400 particles at N. Refuted if every inner bin holds more than 400.
- C2: the measured lead (M/8, N: 0.01, 0.17, 0.78, 0.92 M at R0 = 10, 20, 28, 36 M; v6_tracers.json of
  D-20261126-062436-72c04d3) makes |q| of D1 above 2 per cent in at least one inner bin before the
  correction. Refuted if |q| < 1 per cent in every bin (then D1 cannot see the lead).
- C3: the scope's exact side takes the proper time of a bin from the tracers of the nearest label (6, 10,
  20, 28, 36, 40, 48 M); with every particle's own proper time from the snapshot the exact enclosed mass
  differs; I expect the induced |q| above 2 per cent in some inner bin at 200 or 300 M (the estimator's
  reference is then wrong by more than D1's band). Refuted if below 0.5 per cent everywhere.

Figures: one per calculation (B and C), looked at before any number is used.

## Entry 2 (2026-11-27 16:44 PST): outcome of A (block counts)

Runs: D-20261128-004218-80cf6ab (first; its per-level labels counted from the coarsest level holding
leaves, wrong for G-16, whose root holds none; the counts themselves are right) and
D-20261128-004344-1119b6f (rerun with physical levels and the x1 extent of each level; the numbers below).
Release core-v0.8 processor build, `athena -m`, exit 0 for all four decks; outputs `block_counts.json`
and each deck's `mesh_structure.dat`.
- A1 HOLDS: G-8 456 blocks (56 on levels 0-6, 64 on level 7), level 7 (M/8) over +-6 M.
- A2 HOLDS (the scope's estimate is refuted): G-16 as described has 3648 blocks, 8.0 times G-8 (448 on
  each of levels 1-7, 512 on level 8 over +-6 M, none on the root): the 2:1 rule cascades a refined shell
  out to the root. With twice the steps that is about 16 times G-8's mesh work, not "2.5 times the blocks".
- A3 REFUTED as written, and worse than predicted: G-12 as described has 2176 blocks (4.8 times) and its
  finest level (M/12) covers only +-4 M, not +-6 M. With the root at 144 cells the refined regions of the
  ES-FL deck no longer fall on block boundaries: level extents +-512, 256, 128, 64, 16, 8, 4 M against
  G-8's +-384, ..., 12, 6 M. Per radius G-12 is FINER than G-8 in 0-4, 6-8, 12-16, 24-96 M and COARSER
  in 4-6 M (dx 0.167 against 0.125 M), 8-12 M (0.333 against 0.25) and 16-24 M (0.667 against 0.5). The
  late horizon (smallest radius 4.53 M at 399.5 M in FK, g2long entry 19) lies in the 4-6 M shell where
  G-12 is the coarser member. G-12 as written is not a refinement of G-8 and breaks the scope's own
  condition "the finest level must cover a cube of +-6 M".
- A4 HOLDS: G-16b (blocks of 12) has 8296 blocks (4096 on level 8 over +-6 M, 1216 on level 7 over
  +-9 M, 296 on level 6, 448 on levels 0-5): 2.27 times G-8's cells, 4.44 times its cells with ghosts.
No figure: block counts are integers read from the code's own mesh file.

## Entry 3 (2026-11-27 16:48 PST): outcome of B (G3 criteria of Claim G on G2's outputs)

Run D-20261128-004801-cd648e5 (`tools/g2_analogs.py`, one core, exit 0; byte-identical to an
unregistered dry run in scratch/D-bh-dress/tmp/scope_review). Figure g2_analogs.png looked at: (a) the
N/4 - N and N - 4N differences scatter as before, the M/16 - M/8 growth difference sits on a plateau near
+5e-4 with a scatter several times smaller than N - 4N; (b) the seven rms ratios between 2.1 and 2.9;
(c) e_h of the four M/8 members at +0.18 to +0.25 per cent before tau_rem ~ 285 M, FL16 (M/16) at +0.04 to
+0.09 per cent, the excision step of ES-FL and FL16 after it; (d) ES-FL's slope deviation reaches 0.0335 in
one fixed window (ln a 0.73-0.83), FK's stays below 0.005.
- B1 REFUTED (my prediction failed): all seven 50 M windows have rms(N/4 - N)/rms(N - 4N) inside
  [1.4, 3]: 2.43, 2.91, 2.48, 2.57, 2.11, 2.83, 2.14. The G3-G4 ratio test is passable when the noise
  scales as N^-1/2 (about mean-subtracted rms two windows would be 3.12 and 3.10: the scope's "rms" must stay
  the raw rms). Particle window means of e_h (50 M of tau_rem) of N/4, N, 4N differ by 1.3e-4 to 3.2e-4,
  a third of G3-G4's 0.1 per cent.
- Noise model: one member at N has sigma 3.9e-4 in M_AH (3.65e-4 after a 50 M running mean is removed);
  the high-pass part of Delta M_16 - Delta M_8 has sd 2.1e-4, so the particle noise of the two meshes is
  correlated with rho = 0.83 (same particles). Mean of Delta M_16 - Delta M_8 over 250-299 M +5.78e-4,
  envelope 9.97e-4 (gate review R5, reproduced).
- B2 HOLDS: with G2's mesh difference as the deterministic part, G3-G3 as written passes with
  probability 0.11-0.15 at p = 2 and 0.075-0.10 at p = 1 (1000 surrogates each, high-pass and full
  noise), 0.38-0.42 at twice and 0.67-0.72 at four times that amplitude. Median envelope ratio 1.3 (p = 2)
  against the band [1.5, 8]. A window-mean ordering (5 of 6 windows) passes with 0.34-0.47.
- B3 REFUTED (the size): e_8 - e_16 per 10 M bin of tau_rem (50-280 M, 23 bins) has mean +1.48e-3 and sd
  3.0e-4, positive in every bin; the lead alone accounts for about 3e-4 of it. The rest matches the
  converged vacuum horizon-mass offset of each mesh at 200 M (tight finder, A16: M/8 +9.93e-4, M/16
  -2.02e-4, M/4 -9.09e-3; fp_analyse D-20261124-172508-c847ee4, FP4 refuted as non-monotone): 1.2e-3 +
  3e-4 = 1.5e-3 [JUDGEMENT: a decomposition, not a separate run]. So e_h is not an error that goes to
  zero monotonically: it carries the mesh's horizon-area offset, which changes sign between M/4, M/8 and
  M/16.
- B4 HOLDS: G3-G1 flags ES-FL (largest bin 0.620 per cent) and passes FK (0.249), FN4 (0.237), FNQ
  (0.290). G3-G5 flags ES-FL marginally: 0.0335 with fixed windows of 0.1 in ln a from tau = 50 M, 0.052
  with sliding windows; FK 0.0048 (fixed), FN4 0.0013, FNQ 0.0066. A defect of the size of the excision end
  is seen by both, by G3-G1 with the clearer margin.
- B5 (arithmetic): the lead's bias on r, 6e-4 at M/8 and N, is 0.12 of G3-G1's band; G3-G1 cannot see it.
- B7 (reading of a registered output, no prediction): converged null difference at M/8 at most 7.31e-5
  (100-500 M, nine dumps), at M/16 at most 3.66e-5 (200-300 M, three dumps); ratio 1.99 over these
  windows, 1.78 over the common 200-300 M. G3-N1's factor-2 clause holds by 0.3 per cent on the full
  windows, and its numbers are already known: polishing equals the tight rule to 6e-9 (finder_stop.md
  section 6), and the tight re-search of the same restart files is FP/FP-ext.

## Entry 4 (2026-11-27 16:52 PST): outcome of C (Claim D's statistic on the exact solution)

Run D-20261128-005059-e65d075 (`tools/dress_model.py`, one core, exit 0). Figure dress_model.png looked
at: (a) the exact rest-mass density outside 1.5 R_AH on FK's own particle clocks at 100, 200, 300 M,
slope about -1.9 to -2.8 and lumpy where the lattice labels bunch; (b) q from the measured lead, -24 to
+3 per cent, largest in the two innermost bins; (c) q from the scope's nearest-tracer-label clock, -2 to
-73 per cent, everywhere below the band.
- C0 HOLDS: my tau_H(R0) equals esf_growth.csv to 6.0e-9 relative over 4000 shells.
- C1 REFUTED (my prediction failed): every inner bin (1.5 R_AH to 10 M, eight log bins to 40 M) holds
  more than 400 particles at N: 6080, 3696, 3744 particles in the inner range at 100, 200, 300 M, 848 to
  2568 per bin. D1's 400-particle floor excludes no bin. Poisson counting noise of the cumulative mass in
  the innermost bin is 3.0-3.4 per cent, above D1's 2 per cent band [JUDGEMENT: Poisson; the lattice is
  quieter, the dynamics adds scatter].
- C2 HOLDS: with the lead measured by the verifier (M/8, N, at R = 4 M: 0.002, 0.177, 0.788, 0.92 M at
  R0 = 10, 20, 28, 36) |q| reaches 6.2, 23.6, 18.1 per cent at 100, 200, 300 M in the inner bins; with the
  M/16 lead (0.40 M at R0 = 28) still 6.2, 17.7, 14.0 per cent. At 300 M the innermost bin has |q| 14 per
  cent with the M/16 lead and 9 per cent with the M/8 lead although the M/16 lead is the smaller at every
  label: the ordering of |q| in a bin does not follow the ordering of the lead (lumpy labels). The inner
  slope moves by +0.26, +0.30, +0.51 (M/8 lead); its Poisson bootstrap sd is 0.042, 0.062, 0.073.
- C3 HOLDS, far beyond the prediction: the nearest-tracer-label clock gives |q| up to 44, 73, 69 per
  cent and inner slopes of -1.2, -1.1, -0.05 against the exact -1.9, -2.4, -2.8. At 200 M the inner tracer
  labels (6, 10, 20) are already swallowed and the nearest label left is 28 M; inside a 1 M label bin the
  particles' own proper times spread by 5.4-7.1 M and differ from the label's tracer time by up to 6.1,
  12.2, 15.4 M. The snapshots carry every particle's proper time (docs/FORMATS.md line 123).

## Entry 5 (2026-11-27 16:54 PST, before the run): power of a whole-run form of G3-G3

To give the lead a wording for G3-G3 that has power, the same surrogate model as B2 (noise of one N
member from FK - FN4, mesh correlation 0.83, deterministic part of order p normalised to G2's +5.78e-4)
is applied to a whole-run statistic: the means over 100-400 M of D_8,12 and D_12,16, passing if
|mean D_8,12| > |mean D_12,16| with ratio in [1.5, 8] (ratios: 2.86 for p = 2, 2.0 for p = 1).
- B2b: at G2's amplitude this passes with probability above 0.8 for p = 2 and above 0.6 for p = 1; with
  no convergence (deterministic parts equal, ratio 1) it passes with probability below 0.1. Refuted if
  the p = 2 power is below 0.5 or the false-pass rate above 0.2.

## Entry 6 (2026-11-27 16:54 PST): outcome of B2b; prediction B2c before its run

Run D-20261128-005416-65b4dde (`tools/g3g3_power.py`, one core, exit 0).
- B2b REFUTED: whole-run means pass with probability 0.30 (p = 2) and 0.29-0.30 (p = 1) at G2's
  amplitude, 0.54-0.60 at twice it; with no convergence the false-pass rate is 0.22-0.24. Cause named
  after this run (it could have failed): Delta M_h(t) = M_AH(t) - M_AH(20 M) anchors every member at ONE
  finder sample, so that sample's noise (about 2.1e-4 between meshes after the 0.83 correlation) becomes a
  constant offset of the whole series, which no window or whole-run average removes.
- B2c (prediction, before the run): anchoring at the mean over 20-40 M instead (40 samples) makes the
  whole-run form pass with probability above 0.7 at p = 2 and G2's amplitude, with a false-pass rate
  below 0.15. Refuted if the power is below 0.5 or the false-pass rate above 0.2.

## Entry 7 (2026-11-27 16:55 PST): outcome of B2c

Run D-20261128-005447-0705a41 (`tools/g3g3_power.py ... window`, one core, exit 0); figures
g3g3_power.png of this run and of D-20261128-005416-65b4dde looked at (full-noise curves; the x-axis
minor labels overlap, cosmetic).
- B2c HOLDS with the high-pass noise model and is REFUTED with the full one: anchored at the 20-40 M
  mean, the whole-run form passes at G2's amplitude with probability 0.945 (high-pass) and 0.663 (full)
  at p = 2, 0.82 and 0.59 at p = 1; the false-pass rate without convergence is 0.075 (high-pass) and
  0.249 (full). The full model counts the slow wander of N - 4N as noise (part of it is the N-dependence
  of the lead, so it is the pessimistic case). The window anchor is necessary; it is not sufficient for a
  pass/fail order at N: the noise must fall (the mesh leg at 4N halves it, B1) or the mesh difference must
  be quoted as a measured ratio with its surrogate interval instead of a pass/fail order.

Note (16:56): the times in the headers of entries 1-7 were corrected to the commit times (git log); the
first versions carried times written ahead of the clock. Each prediction was committed before its run
(A1-A3, B1-B5, C0-C3 in 5686fde65; A4 in 80cf6ab4a; B2b in 65b4dde5b; B2c in 0705a410e; each run's
manifest names the commit it ran on).

## Entry 8 (2026-11-27 17:04 PST): review written

SCOPE_REVIEW.md: verdict "do not queue the production set as written; change B1 (mesh members and
budget, from A), B2 (Claim D's statistic, from C), B3 (G3-G2 and G3-G3, from B, B2b, B2c) first, then
S1-S8". Failed predictions of this package, kept as written: A3 (G-12 worse than predicted), B1 (the
particle-leg ratio test passes one factor coarser), B3 (the mesh difference of e_h is five times the
lead), C1 (no inner bin below 400 particles), B2b (whole-run means with a single-sample anchor have no
power), B2c in its full-noise half (false-pass rate 0.25). Not done: no card run (none allowed); the
per-particle-clock reader on G2's snapshots and the polished vacuum offsets are proposed, not built;
card memory of the 3648-block deck not measured.
