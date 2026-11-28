# JOURNAL of package g3/scope_review (Track D): independent review of the G3 scope before its runs

Helper of D-bh-dress, batch 34, 2026-11-27. I did not write `scope/SCOPE_G3.md` (lead of batch 34,
commits e92904aed and acb5f7202) nor any of the G2 runs read here. No card time; processors only, one
core per calculation.

## Entry 1 (2026-11-27 16:45 PST, before any calculation): what I test and what I expect

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
- A4 (added 16:50, before any run): a cheaper form of G-16, the same deck with blocks of 12 cells
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
