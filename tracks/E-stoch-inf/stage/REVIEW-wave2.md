# Lead's review of the helpers of waves 2 and 2b (E-stoch-inf)

Lead of wave 2b (Opus), 2026-11-19. The wave-2 lead never ran (usage limit of 2026-11-15),
so this review covers the wave-2 helpers (analysis, note, verifier) and the slow-roll ladder
of waves 2 and 2b. Method: from the artefacts, not from the helpers' conclusions. The
analyses were rerun from the registered outputs at the current commit, the central numbers
were recomputed with code the lead wrote without the helpers' modules, every figure relied
on was looked at (Read of the PNG), and every outcome was compared with the prediction its
helper wrote before the run. The lead's own predictions (LR1-LR5, LA1, LV1, LN1, LR1') were
committed before the checks ran: owner `JOURNAL.md`, entry 2026-11-19T14:58Z (commits
74b52ec8, c056cd41).

Not reviewed: the package `usr/` (preparation of the USR case). It belongs to the wave-3a
workflow, which runs beside wave 2b in this worktree; its run E-20261119-144116-8aa7c22 was
still running and `usr/scripts/analyse_runs.py` was uncommitted during this session. The
next lead reviews it.

## 1. The lead's runs

| Run | What | Outcome |
|---|---|---|
| E-20261115-174600-81652ff | verifier's V6/V7 run, left "running" in wave 2 (exit 0 at 17:51Z on 2026-11-15) | closed with `nrpic-run finish` (completed, 172 files checksummed) |
| E-20261119-145853-ef835c2 | LR1: full rerun of the ladder's final analysis from the raw dumps | STOPPED, recorded as failed (exit -15): the cold 128^3 and 256^3 dumps came through the ladder's memory map at 3.6 MB/s (the disk gives 124 MB/s sequentially); about 150 GB to read. The original analysis ran with the dumps in the page cache |
| E-20261119-150842-ca70d37 | LR1': 32^3 and 64^3 rungs re-extracted from the raw dumps, the other intermediate outputs taken from run E-20261115-194633-9e04ed8 (checksums verified, 101 files PASS); `verdicts.py`, `make_figures.py`, `floor_analysis.py`, `a6_analysis.py` rerun | CONFIRMED: 17 recomputed JSON files bit-identical to the originals (2295 numeric leaves; only the path string of the npz differs in the two judge files); `summary.json` (589 leaves), `floor.json` (436), `a6.json` (4013) bit-identical to `ladder/results/`; all eight figures pixel-identical to `ladder/fig/` |
| E-20261119-150238-b81e33f | LR3-LR5: the lead's own code `stage/G1/scripts/lead_check.py` (own NRSFDMP2 reader, complex FFT, amplitudes from core's twin `python/nrpic/scalar_field.mode_alpha` instead of the track's `noise/ref/philox_ref.py`, own Friedmann and Mukhanov-Sasaki integration with LSODA instead of DOP853, parameters from the decks in the run directories) | CONFIRMED, details below; `fig_lead_check.png` looked at. One development run before it (scratch `tmp/devcheck`, disclosed in the JOURNAL; a bug of mine, k = |n|^2 for the crossing, fixed before registration) |
| E-20261119-150346-a513bc8 | LA1: analysis package's synthetic tests T1-T5; LV1: verifier's V1-V5, V8 (`run_python_checks.sh`) | CONFIRMED: 15 of 15 tests pass, `test_sfa.json` 48 of 48 leaves identical to run E-20261115-171445-36152c4; V1 91, V2 288, V3 2, V4 37, V5 3, V8 9 leaves identical to run E-20261115-174606-3c67607 |
| E-20261119-150541-3210cd6 | LN1: unchanged validator with the reference fixed by the lead (tanh window increment without cancellation) on U6 of the card base case and of the scaled processor case, and on the frozen card validation | CONFIRMED: A1 = 4.57e-15 (card U6) and 4.02e-15 (processor U6) against the bound 1e-11; every test passes; frozen A1 5.3e-15 (9.8e-14 before, the power model takes the same increment); `fig_val_card_markov_tanh.png` looked at |

A12 also checked from the registered checksums (no computation): `u.sf.00002.dump`,
`u.sf.00003.dump` and both `.modes` files of U4 have the sha256 of U2's in
`sha256sums.txt` of run E-20261115-170727-d15df12 (processors) and of runs
E-20261115-170645-3b21217 / E-20261115-180526-6b68c33 (card). The card and processor dumps
differ (A14 is a tolerance test, 2.2e-15 of the rms), their `.modes` files are identical.

## 2. Ladder (waves 2 and 2b; `ladder/`)

Predictions P1-P9 (entry 1), PA6a-c (entry 8) and the A12 restatement (entry 7) were written
before the runs; I compared each outcome in entries 2-11 with them.

Confirmed by the lead:
- A1 on L32p, L64p, L128p from the raw records with my own Friedmann integration: phi within
  6.4e-13, 6.8e-13, 1.2e-12; Pi 4.5e-12, 3.4e-12, 4.4e-12; K 3.5e-12, 4.9e-13, 1.2e-12;
  e-folds within 5.5e-6, 3.3e-7, 2.0e-8 (run E-20261119-150238-b81e33f). Threshold 1e-4.
- A2 on L32p with my extraction and core's amplitude twin: 8.76e-5 for |n| <= 4 (ladder
  8.8e-5), 4.08e-3 over all 1054 modes (ladder 4.08e-3). The other rungs (L64-L256, Q64,
  Q128, P256: 2.7e-6 to 1.21e-4) are confirmed only through the bit-identical rerun of the
  ladder's own scripts (LR1'), not by my code.
- A3 on L32p: 1051 modes, largest |Q(N_f)/Q(N_k + 4) - 1| 2.7e-6 (the ladder interpolates
  to N_k + 4 and gets 4.6e-6), drift at most 1.38e-4 per e-fold, NR minus linear 1.4e-6.
  Threshold 2.5e-3; the FLRW lattice would drift at -4 eps1 = -0.05.
- Record <|H|/[H]> at t = 8.5: 3.124e-12, 1.832e-13, 1.115e-14 (factors 17.05, 16.43:
  fourth order in the step, which scales with h).
- Odd and even parts of H at N = 32 from the dumps (my code): halving factors 2.000 (odd) and
  3.997-4.000 (even) at every dump from t = 0.54 to 3.53; odd/even 745 at t = 2.50; order of
  the odd part 32 -> 64 5.64, 5.60, 5.54, 5.54, 5.55 at t = 1.5-3.5 (entry 5: 5.64-5.54).
- A6 (temporal order 3.93-4.08, top-shell deviation 94 percent spatial, late-entry odd part
  of H changing by at most 4 percent with the Courant factor), the floor analysis and every
  verdict of `summary.json`: bit-identical rerun (LR1'). Figures looked at:
  `fig/final/fig_a2_modes.png`, `fig_a3_freezing.png`, `fig_a4_paper.png`,
  `fig_spectrum.png`, `fig/floor/fig_floor.png`, `fig/a6/fig_a6.png`.
- A12 bit-identity (from the registered checksums, above).
- Cost: 1811 s wall, 0.503 card-hours, 1.30 s per step for P256 with one 256^3 MeshBlock
  (manifest of E-20261115-172618-f948386 read; not re-measured).

Not confirmed by the lead (taken from the rerun of the ladder's own code only, or not checked):
- A4 and A5 at 128^3 and 256^3 (Q128, P256, P256m, L128, L256): only the ladder's code read
  those dumps (the full rerun was stopped). The A5 pass rests on a floor model and a factor
  of three chosen after the data were seen (the ladder says so); the attribution of the
  floor to double-precision rounding is a [JUDGEMENT] that no run tests.
- The spectrum against the slow-roll formula (1.0104-1.0109 for |n| <= 7): rerun only.

Wrong or refuted (all on the ladder's own record, none hidden):
- P5 of entry 1 as written (early orders, floor of 1e-15; measured floor 6e-13 to 7e-15).
- Entry 6's [JUDGEMENT] that the |n|^4 growth of the A2 deviation is temporal: A6 shows it is
  94 percent spatial.
- A4 in the owner's strict form fails in P1's set-up (k_max = N/4) at every N from 32 to 256
  (odd part up to 385-870 times the even part from ln(N/8) e-folds after N*), as P4
  predicted and core's T12 found at 32 and 64. It holds in the k_max/dk = 8 set-up from
  N = 128 (odd/even 0.27 at L128).
- The ladder's request "A4 ... M/[M] of second order" in SCOPE was itself inconsistent with
  P1:540-541 ([M] is first order, so |M|/[M] is first order); SPEC P-e corrected by the lead.

Defects:
- Not fixed (listed): `analyse_all.py`/`verdicts.py` still compare t = 4.500 with
  t = 4.504-4.516 at the last dump of pairs with different `tlim`; the verdicts exclude
  those dumps, but `fig/final/fig_a4_paper.png` (middle panel) still shows the spike of the
  even halving factor at N = 4 for N = 64 and 128. A reader of that figure alone would be
  misled; `fig/floor/fig_floor.png` drops those dumps. To fix in the next ladder session.
- Not done (listed): USR (G2), a second seed, a halving pair at 256^3, A6 at 64^3 on a card
  (L6 asks 64^3; run at 32^3), L5 single kick, L9 sensitivity, a run in another precision for
  the floor.

## 3. Analysis package (wave 2; `analysis/`)

Confirmed: the synthetic tests T1-T5 (LA1, identical); the Markov-tanh A1 failure lay in the
track's reference, not in the code (LN1, after the lead's fix of `noise/ref/noise_ref.py`);
A12 (P5, P5') holds (checksums above; the ladder's validation run E-20261119-141654-c2a10d1);
journal predictions compared with outcomes (17:05-18:48): the failed ones (T2a absolute
threshold from a development run, the |M| norm with gt = delta, PS5 lockstep against SciPy at
N = 32) are on record; the development runs looked at before registration are disclosed.

Not confirmed (not rerun by the lead): the plane check of the constraint estimators against
the code's history (runs E-20261115-171628-1737ebe failed as predicted-wrong,
-171859-0b34449); the slow-roll scouting from the homogeneous slice (E-20261115-172349-0bdb97d,
-172347-a297a96), superseded by the ladder's initial slice at N*; U9/A14
(E-20261115-184748-9b010fa) beyond the checksum observation above; the card base-case
validations other than U1 and U6 (E-20261115-180533-24a7781).

Open items of the package and their state now:
- "rms M/rms [M] before any mode enters is not second order in R" [TO VERIFY]: in the
  ladder's set-up the early odd part of H and M at N = 32 is the fourth-order time error
  (A6, entry 11) and |M|/[M] is first order by P1:540-541; the homogeneous-start case was not
  rerun, so the item stays open at low priority.
- The 8.3e-5 per-mode residual: in the ladder set-up the analogous 8.8e-5 at |n| <= 4 is 92
  percent spatial (A6); the float32 gt of the bin output is no longer used (double dumps
  with gt_ij, `dump_metric`).
- Requests (a) gt_ij, At_ij in the double dump and (b) [M] in the record: done by core on
  `core/scalar-2` (NRSFDMP2, `sr.sf.con.hst`), not yet released; (d) R8 done there.
- Request to the noise package (window increment): done by the lead (LN1).
- Request to the lead (P-e): done (SPEC 7.1 row P-e and the note under 7.2).
- Requests to orch (launcher): `$NRPIC_RUN_DIR` is substituted from wave 2b
  (`coord/digests/harness-wave-2b.md`); the batch launcher's checksum of every deck at
  submission (a restart file made earlier in the same batch cannot be listed) is not in the
  digest; carried to orch in this session's outbox.

## 4. Note package (wave 2; `note/`)

Confirmed: the seven figures of the note looked at by the lead (`fig_background`,
`fig_freezing`, `fig_deltan`, `fig_noise`, `fig_cost`, `schem_architecture`,
`schem_timeline`); its stage-verify reruns (7 of 7 scripts, 14 files compared) were PASS on
5c1933b and are repeated by this session's `nrpic-stage verify` (stage/G0/VERIFY_RESULTS.md).
The cost model (0.57-0.71 SR, 0.71-0.88 USR card-hours per 256^3 realisation, extrapolated
from 128^3) is conservative against the measured 0.503 for SR with one 256^3 MeshBlock.

Not confirmed: the claims check (`note/tables/claims.md`, 59 numbers) was not redone by the
lead beyond the ones this review touched; the reviewer subagents of the paper-writing
procedure were not run (no subagent tool in that session either).

Carried out on its requests: disagreements 1, 2 (cost) and 4 (dead pointer) into SCOPE 8, 9
and SPEC 7.2, 11.2; 6 (locator key: FKTT for arXiv:1308.4754, authors read at the source);
5 (old state in STATUS, HANDOFF, RISKS R1, G1/STATUS) by rewriting those files; SCOPE 6 stays
as the record of 836ac86. The ledger is added to `stage/G0/VERIFY`. Small defects seen: the
right-hand x-axis label of `fig_background.png` is cut at the edge ("10"), and
`schem_timeline.png` still says "the group's decision pending" (decision 0017 accepted 0013);
both left for the G1 sections of the note.

## 5. Verifier of G0 (wave 2; `stage/G0/VERIFIER.md`) and what the track does

The verifier's computations were rerun bit-identically (LV1). Its findings:

| Finding | Verdict | What the track does |
|---|---|---|
| V1-V6, V8 | CONFIRMED | nothing to do; V6 run closed by the lead |
| V7 cost | NOT CONFIRMED (no card time) | measured since: 0.503 card-hours per SR realisation at 256^3 (one 256^3 MeshBlock), 1.13-1.30 s per step on jobs A-C; A6 shows theta = 0.25 is enough (time error of R^NR below 3e-4), so the theta = 0.025 case (6-15 card-hours) is not needed. Still open: USR cost (estimate 0.63 by step count), synthesis cost with smaller MeshBlocks (needed only for several cards). SCOPE 8, 9 updated |
| Weak point 1: cost and Courant factor coupled | | resolved by A6 and the measurement (above) |
| Weak point 2: G1 needs pieces missing from the release | | the pieces exist on core's tested branch `core/scalar-2` (initial slice at N*, record, NRSFDMP2) and the ladder used them (scouting, decision 0013); the A2 amplitude of the kicked field is now tested (P256: 1.21e-4 for |n| <= 32). Still true: none of it is in a release; RISKS R1; request to core |
| Weak point 3: USR at the drift/diffusion border | | new risk R15 in RISKS.md; to be stated as the validity window at G2 |
| Difference 3: release differs from 836ac86 | | confirmed by LN1: the release's increment is exact, the reference was not; reference fixed |
| Difference 6: unit mapping SPEC 2.5 and E6 not exercised | | E6 tested by run E-20261115-174214-74becdd (factor 1/4 to about 2 percent); the unit mapping is exercised by A1 at 1e-11 on every rung; the end-of-inflation delta-N statistics and the importance sampling remain unchecked |
| Difference 7: VERIFIER.md vs VERIFIER_REPORT.md | | decision 0016 item 1 accepts VERIFIER.md |
| Lead's USR eps1(N*) off by 1.1e-4 | | irrelevant for the plan (verifier); recorded in EVIDENCE |

The verifier's own failed predictions (continuum projector at 2 of 4 dumps, V7 timing ratio
undecidable, V2b bounds exceeded at 6 H/2pi) are on its record (`stage/G0/JOURNAL.md`).

## 6. Small defects fixed by the lead in this session

- `noise/ref/noise_ref.py`: tanh window increment without cancellation (LN1).
- `spec/SPEC.md`: P-e (|M|/[M] first order), the dead pointer to `stage/G0/REPORT.md`, the
  name of P2's initial-condition equation (the source numbers it 23rd, label
  eq:eqInitialConditions; "eq. (17)" is eq:Bardeen; kb found it first), the cost estimate
  marked as superseded.
- `spec/scope/SCOPE.md`: locator key FKTT, A2 reference wording, measured cost, section 4b
  with the proposed A4'/A5' (not in force; proposal to orch).
- `RISKS.md`: R1, R2, R5, R9, R12, R13 updated; R15-R17 new.
- Run E-20261115-174600-81652ff closed.

Large items listed, not fixed: G1 products (updated architecture and data-flow schematics,
G1 sections of the note, a fresh-context verifier of the G1 material), the last-dump
artefact of the ladder's analysis, the runs not done (section 2).
