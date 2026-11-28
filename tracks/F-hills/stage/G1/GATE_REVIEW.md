# Gate review: F-hills G1 (independent reviewer, decision 0019 item 3)

Reviewer: fresh session (batch 34a, 2026-11-27 PST), not the author of any of the material
reviewed. Branch `track/F-hills` at `ec55f2a88` (main merged, "Already up to date"). No tag
`stage/F-hills/G1-pass-*` exists (`git tag -l`: only `stage/F-hills/G0-pass-20261120`).

**Recommendation: PASS WITH RESERVATIONS.** Every criterion of the gate is met in substance; two
departures from the letter (the passage ends at 186.0 M against the 200 M of scope criterion
(iv), and "found" horizons include unconverged surfaces) and the stale state of the package's own
records (STAGE_REPORT verdict FAIL, C18 OPEN, the second verifier's corrections not applied) are
stated below with what each needs. The failed predictions (A2-1, A2-2, A2-3, A2-4, the heavy-hole
clause of A2-5, H2 in part, H4, C25-1 and C25-3 in part, D34-1, D34-2 in part) are on record
before and after their runs and are failures of expectations about the physics and the
diagnostics, not of the run's health checks; the gate can be passed with them stated (section 3).

Criteria read: brief l. 674-686 (gate table: G1 "baseline results obtainable without the NRPIC
coupling; the analysis pipeline validated on them; interface proposals submitted"); charter
sheet 9.9 (G1: "F-pre-1 and F-pre-2 reproduce the curves of the literature; constraint residuals
and junk radiation of the three-puncture data are quantified; one complete vacuum passage is
done"); decisions 0005, 0013 (mass ratio four first; the first clump passage right after the
first black-hole passage), 0016 (items 4, 7), 0042 item 2 (A2 to "at least 170 M"), 0044 item 2;
the concrete G1 criteria (i)-(iv) of `../G0/SCOPING.md` l. 133-145.

## 0. Predictions for the reviewer's own check, and outcomes

Predictions committed in b85a9a540 before the run. Run **F-20261128-013351-b85a9a5**
(`nrpic-run`, local, one core, 0 card-hours; script
`scratch/F-hills/tmp/gate_review_g1/review_check.py`, sha256 in the manifest; outputs
`review_check.json`, `fig_review_g1.png`). My reader is my own: it joins every kept tracker copy
of A2 (`trk_keep/*/hills.co_<n>.txt`, 45 copies) and the live file, takes one row per distinct
time from the status files and summaries, and computes rms H from the history; it does not use
`nrread.py`, `b*_*.py` or the verifiers' readers.

| # | Quantity (definition) | Claim | Predicted band (refuted if outside) | Outcome (F-20261128-013351-b85a9a5) |
|---|---|---|---|---|
| R1 | last tracker time of A2 (all copies joined); largest step between consecutive distinct times, 61.8 M to the end | 186.0 M; one step (2^-9 M) | last in [185.95, 186.05] M; gap <= 2 x 2^-9 M | 186.0 M for all three trackers; largest gap 0.001953125 M = 2^-9 M; 63589 distinct times from 61.8047 M; 46 files per tracker. HELD |
| R2 | m2 (tracker 1) to M (tracker 2): minimum after 120 M and its time; value at the last record | 8.733 M at 134.3 M; 17.53 M | [8.70, 8.76] M at [134.1, 134.5] M; last in [17.4, 17.6] M | 8.73329 M at 134.3105 M; 17.5297 M at 186.0 M (13.84 M at 170 M). HELD |
| R3 | m1 (tracker 0) to M: first time below 1 M; value at the last record | 138.33-138.35 M; 1.3e-9 M | first in [138.2, 138.5] M; last < 1e-6 M | 138.3340 M (below 0.5 M at 140.5449 M); 1.32e-9 M. HELD |
| R4 | finder 2 (M) status file, A2, distinct times 133.0-186.0 M: found flag; first area mass > 1.05; last area mass | all 1697 found; 137.5 M; 1.1137 | all found; first in [137.4, 137.6] M; last in [1.110, 1.117] | 1697 distinct times (1771 raw rows), all found; first at 137.5 M (1.01121 one search before); 1.113750 at 186.0 M. HELD |
| R5 | finder 1 (m2) status file: found flag; area mass range | all found; 0.12954 within 6.4e-4 | all found; every mass in [0.1285, 0.1305] | all 1697 found; 0.128897 to 0.129639, median 0.129538. HELD |
| R6 | failure signature in the summaries (columns 3-12 equal to the previous distinct time's, or mass not finite or <= 0), restart repeats collapsed; A (0-64 M) and A2 (61.8-186 M) | finders 1, 2 none; finder 0 none before 139.5 M | as claimed, finder 0 failing after 141 M | A: 2049 times per finder, 0 failures in each. A2: 3975 times per finder; finders 1, 2: 0; finder 0: 1340, the first at 139.562 M, none before. HELD |
| R7 | rms H = sqrt(H-norm2 / Volume), A2 history: maximum and its time | 6.19e-5 at 135.5 M | [6.0e-5, 6.4e-5] at [134, 138] M; < 1e-4 everywhere | 6.1908e-5 at 135.5 M; below 1e-4 at all 274 records (62.0-186.002 M); 1.51e-5 at the end. HELD |

`fig_review_g1.png` read: the m1-M distance falls through 2.5 M at 133 M and flattens at zero
after about 141 M; m2-M has one shallow minimum and rises linearly; finder 2's status area mass
jumps from about 1.01 to 1.11 at 137.5 M while its summary (Christodoulou) mass sits about 0.01
higher; rms H rises to its peak at 135.5 M during m1's approach and falls to 1.5e-5 by 186 M,
never near 1e-4.

## 1. What I opened

- Package: STAGE_REPORT.md (verdict FAIL, written at da850964a before the verifier's part 2),
  CHECKLIST.md, STATUS.md, EVIDENCE.md, OPEN.md, REVIEW.md, VERIFIER.md parts 1 (batch 22) and 2
  (batch 34, sections 10-17), VERIFY_RESULTS.md (old and my rerun), `../G0/SCOPING.md` l. 100-175,
  `../G0/VERIFIER.md` K2, K3, K5, K20.
- The lead's journal: predictions A2-1..A2-5 (`../../JOURNAL.md` l. 828-839, batch 11, written
  before A2), batch 34 predictions D34 and outcomes (l. 1282-1421).
- Manifests: A (F-20261121-203144-b2cf16b, stopped, 11.77 card-hours), A2
  (F-20261124-210400-902c650, stopped, 46 jobs, 19.70 card-hours, one continuation in place by
  q0069 with `-i fastflow_diag.athinput`), the batch-34 readers F-20261127-232657-163727d,
  -232849-14345be, -232940-3f652bf (completed), and their outputs.
- Raw outputs of A and A2 (my run, section 0).
- Figures read (Read tool): fig_b34_horizons, fig_b21_a2_state, fig_b11_passage (batch-34 run
  directories); verifier-tail fig_t_branches; verifier fig_v_junk; newton3 fig_skr_curves;
  geodesic_binary s1_sepfrac; khsr_note fig_khsr_ecc; nr_first fig_test_nrread_synthetic and
  fig_c0_constraints; note schem_dataflow; my fig_review_g1.
- Note: `note/main.tex` (24 pages, last changed 2026-11-24) and `note/tables/ledger.tex`: 135
  data rows, every one with a run id or a source locator (a script over the rows; the six rows
  without one are table headers).
- `harness/bin/nrpic-run budget`: G1 used 49.89 of 60 card-hours.

## 2. Criterion by criterion

| # | Criterion | Evidence I opened | Verdict |
|---|---|---|---|
| C1 | Baseline results without the NRPIC coupling | Newtonian (newton3, newton3_fix) and geodesic (HRNA) references, both from P1's and P1b's start states; the vacuum passage itself runs on the release core-v0.5 card build with no new core source (A2 manifest) | PASS |
| C2 | Analysis pipeline validated on them | fig_test_nrread_synthetic (synthetic full-Newton tracker files, planted failures); two independent verifiers' readers reproduce the lead's passage numbers (VERIFIER 3.2, 11-12), and my own reader reproduces R1-R7. One known reader defect (nrread.read_table skips the status rows ending in '# <words>'; first batch-34 run F-20261127-232531-8d16e2c failed on it) is on record and was fixed in b34_horizons.py | PASS |
| C3 | Interface proposals submitted | `outbox/20261115T1507Z__to-core__*` (6 files), `20261119T1514*__to-core__*` (4), later requests (restart on SIGTERM, finder diagnostics on restart, found flag) | PASS |
| C4 | Baseline data and figures | figures listed in C4 exist and are drawn from registered runs; the stage check regenerated all 30 committed figure files | PASS |
| C5 | Interface documents | multi-puncture input per `coord/INTERFACES/multi_puncture.md`, reader and wrapper interfaces in `nr_first/README.md` | PASS |
| C6 | F-pre-1 and F-pre-2 reproduce the literature | 0911.1136 and 1804.02911: second agent at G0 (K2, K3 CONFIRMED, run F-20261121-030155-1061bcb; fig_skr_curves read: prograde curves on SKR's, retrograde edge 0.405 against the printed 0.44, explained by the survival criterion); BKRS fits followed to 1.5-1.7 times their stated accuracy (K3). KHSR (1201.4794): four prograde points recomputed by the G1 verifier within 0.41 sigma (F-20261125-180244-25c98a5). 2404.16270: K5 CONFIRMED by an independent HRNA (F-20261121-032337-9c6d87a, -032325-f58a391; s1_sepfrac read). Kerr (2402.02178): in part, not checked by any verifier; scope criterion (ii) names 2404.16270 only | PASS WITH RESERVATION (retrograde edge and BKRS accuracy as stated deviations; Kerr in part and unverified) |
| C7 | Constraint residuals and junk of the three-puncture data quantified | fig_c0_constraints read (t = 0 rms H 0.0119, 4.71e-5, 5.5e-7 at m/4, m/8, m/16; code against closed form); verifier 3.4 reproduces them and the junk window energies 2.28-2.73e-6 M at 40-90 M (fig_v_junk read: burst at u of about -33 M, then a flat-in-l steady flux) | PASS WITH RESERVATION: criterion (iii)'s "two radii within 20 percent" met at its edge (19.8 percent, all four radii); l <= 8; measured with P1's m/8 binary, not at P1b's spheres |
| C8 | One complete vacuum passage | My R1-R7 (F-20261128-013351-b85a9a5) and the two verifiers: A + A2 joined 0-186.0 M without a gap; pair's closest approach 2.11 M at 76.4 M; binary disrupted (two-body energy positive from about 125 M, fig_b11_passage); m1 captured by M with a common horizon from 137.5 M (finder 2 found at all 1697 searches, area mass 1.0112 -> 1.1137); m2's horizon found at every search to 186 M, m2 passes M at 8.733 M (134.31 M) and recedes to 17.53 M; no failed search of any finder before m1 is inside the common horizon (R6); rms H at most 6.19e-5; MeshBlocks below 2864 and card memory 78789 MiB of 81920 (verifier 12); Newton from the same deck gives the reverse fates (verifier 3.1, F-20261127-232940-3f652bf). Scope criterion (iv) as written: "all horizons found in every search until a merger" met by the flag and by the signature; "trackers until t = 200 M" NOT met as written (186.0 M, ended by a Slurm submission I/O failure, `chain/slurm-5492.out`); "outcome stated with the constraint norm" met (separated; one member captured; m2 receding, bound or not undecided) | PASS WITH RESERVATION: the 186-against-200 M departure must be accepted by the orchestrator or written as a dated amendment of criterion (iv) [JUDGEMENT: the last 14 M would not change the stated outcome; m2's binding is undecided in coordinates either way]; "found" includes unconverged surfaces (verifier F5: m2's finder at 160.6-179.2 M alternates with a found branch of hrms 0.15-0.23 after 6 flow iterations; 3.8-29 percent of member searches before the capture at hrms above 1e-2); one resolution only |
| C9 | Decision 0013: q = 4 first; clump passage right after the first black-hole passage | P1, P1b at q = 4 (`binary_conv/inputs/p1b_R16n.athinput`) | PASS; the first clump passage (object b) is now due by 0013 and is not yet scheduled in the package |
| C10 | Schematic: updated architecture | schem_architecture drawn as of core-v0.3 (two items marked "to be ported" exist since core-v0.4) | PASS WITH RESERVATION (out of date) |
| C11 | Schematic: data flow | schem_dataflow read: complete and legible; "wrapper keeps the tracker files" (to be ported) and "found flag" (new) now exist (core-v0.8, status files) | PASS (to refresh) |
| C12, C13 | Data figures: baselines; pipeline validation | figures named exist; those I read show what the captions claim | PASS |
| C14 | Package documents of decision 0012 | all present; STAGE_REPORT.md is stale (verdict FAIL from the pre-finish `runs` check and C18 OPEN, both overtaken) | PASS (regenerate the report) |
| C15, C16 | Figure style, scripts, schematics | stage check: 15 figures with scripts, style copies equal SHA256SUMS, 30 regenerated | PASS |
| C17 | Working note, checker passed | note v2, 24 pages, compiles; ledger rows all carry a run id or locator. The note predates the completed passage: it still calls the m/16 passage "queued" (main.tex l. 270) | PASS WITH RESERVATION: note v3 with the passage to 186 M is owed (OPEN item 4) |
| C18 | Verifier (fresh context) | Part 1 (batch 22) and part 2 (batch 34, another fresh agent) cover the passage to 186 M, the status files, the junk window, criterion (iii), P1 to 280 M, four KHSR points and ledger rows 122, 126 (part), 128, 168, 194, 200-207; the G0 verifier covered ledger tables 1-2 (57 of 57) and K2, K3, K5. The checklist's OPEN is stale. Not verified by anyone: Kerr, the EIH package, the rest of ledger tables 3-5, P1's remnant spin and radiated energy, S2g's junk | PASS WITH RESERVATION (the gaps listed; "every number of the Supplemental Material" is not literally met) |
| C19 | Null results and failed runs on record | failed and stopped runs listed in STAGE_REPORT with manifests; failed predictions in JOURNAL (batches 21, 25, 34), CHECKLIST C19, OPEN item 3, VERIFIER 4, 13, 14 | PASS |
| C20 | STATUS, JOURNAL, HANDOFF current | current as of the lead's batch 34 close (15:40 PST); not updated for the verifier's part 2 (16:37-16:52 PST) | PASS (update with the corrections below) |

## 3. The failed predictions and the gate question

The gate asks for a baseline without new core work: one complete vacuum passage with its checks.
The checks are the run's health and the readability of its outcome: trackers joined without a
gap, horizons found, the constraint norm bounded, the mesh inside the card, the outcome stated.
Each holds (section 0, R1-R7, and C8). The failed predictions are about something else:

- A2-1 (closest approach at 63-75 M): failed on timing only (76.37 M); its band 2.0-2.7 M held.
- A2-2 (centre of mass closest at 95-115 M and 8-11 M), A2-3 (one member beyond 30 M with
  positive energy, the other bound on a 4-8 M pericentre by 170 M), A2-4 (no common horizon of a
  member with M): the run's physics differs from the Newtonian expectation; m1 is captured. These
  are outcomes of the experiment, the reason to run it.
- A2-5's heavy-hole clause (change below 1e-3 to 200 M): refuted by the capture (+0.11); on the
  converged branch the heavy hole is constant to about 3e-5 from 86.6 to about 131 M by the
  summary's hrms (verifier part 2, F1; fig_t_branches read: the upper branch at hrms 1e-8, the
  lower branches at 1e-4 to 6.5e-4).
- H2 in part (m/8 drift band at the second digit) and H4 (P1's heavy finder 2.3 percent low in
  its first three searches): diagnostics of P1 (m/8, already ruled invalid by decision 0022),
  not of the gate's passage.
- C25-1's tracker clause (140.55 M, not by 140 M), C25-3's rate clause (5.2-5.3 M per segment),
  D34-1 (F1 not separated by the status file), D34-2 in part (117 spurious found surfaces of
  finder 0 after the capture): diagnostics, each stated.

Each was written before its run (JOURNAL l. 828-839 for A2-1..A2-5; l. 1297-1318 for D34) and
each outcome is recorded with its run id. None of them is a health check of criterion (iv). So
[JUDGEMENT] the gate can be passed with them stated, as the package states them. What they do
bear on is G2: A2-3/A2-4 make "m1 is captured" a one-resolution result that the m/12 member C2
(stopped at 106.69 M) must reproduce past 140 M before it is claimed; D34-1, D34-2 and finding F5
make every horizon statement depend on the residual of the surface, not on the found flag.

## 4. Stage check rerun

`harness/bin/nrpic-stage verify F-hills G1` on 2026-11-28T01:45:50Z, clean export of ec55f2a
(HEAD before my first commit): **PASS, 0 failed checks** (`VERIFY_RESULTS.md`, committed with
this review). `runs` now PASS: 280 manifests finished (A2, B2 and C2, open at the lead's check,
are closed); three wave-1 runs waived by `coord/WAIVERS.md`. WARN: `run-notes` (78 hand-written
manifests), `checksums` (3761 output files: 1509 hashed again, 110 GB; 2252 from the cache,
1851 GB: no `--full` pass is on record for this gate). rerun 15/15, compare 42/42, regenerate
30/30.

## 5. Recommendation

**PASS WITH RESERVATIONS.** Before the tag, two record-keeping steps that need no run:

1. The orchestrator accepts the passage's end at 186.0 M for scope criterion (iv) (or the lead
   writes a dated amendment, "trackers until the outcome is stated; 186.0 M", into
   `../G0/SCOPING.md` section 5) [the verifier's request 16(a) and section 17 item 1].
2. The lead applies the verifier's part-2 corrections, none applied yet (they postdate the lead's
   commits): (a) C8 says 186.0 M against 200 M; (b) F1 is decided for 86.6-131 M by hrms (upper
   branch 1.00422 converged), open only during m1's approach; (c) "m2's mass within 6.4e-4"
   says that the lower part of that range is an unconverged branch (160.6-179.2 M, hrms 0.15-0.23);
   (d) "1.55e-3 by 133 M" reads "by about 135 M, during m1's approach"; (e) the source of
   "MeshBlocks 1968-2584": I find 2584 in `b21_a2_state.json` at `S6.mb_and_memory.mb_max` of
   run F-20261127-232849-14345be, while the verifier's reading of the segment logs' start and
   end counts gives at most 2514; the lead says which count it is. Then CHECKLIST C18 is set
   from the two verifier parts, `nrpic-stage collect/report` regenerates STAGE_REPORT (its FAIL
   rests on two overtaken items), and STATUS/HANDOFF follow.

## 6. Reservations to carry to G2

1. One resolution. "m1 captured, m2 receding" holds at m/16 only; C2 (m/12, from 106.69 M)
   continues past at least 145 M, and the gauge leg follows, before the outcome is a result
   (risk R21: the passage's binary departs from the binary alone by -0.53 M at 60 M).
2. Horizons. "found" is not "converged" (F5, risk R25): quote masses with hrms or the mean
   expansion; drop accepted searches above hrms 1e-2 from drift fits (H2, S6); new runs with
   core-v0.8 polishing (`polish_iterations = 100`, `mass_tol = 1e-5`); the polished test of F1
   on A2's restart files between 87 and 133 M.
3. m2's fate is undecided in coordinates (two-body energy -0.04 to +0.12 units by the mass
   used, not conserved); a gauge-invariant measure or a longer record.
4. Junk at P1b's own spheres and the steady flux not yet identified; criterion (iii) at its
   edge (19.8 percent); extraction to l = 8.
5. Waves: the capture's signal reaches only r = 40 M before the record ends, with no ring-down;
   P1b's radiated energy is not measured; P1's remnant spin and radiated energy are unverified.
6. Verifier gaps: Kerr (2402.02178) part of F-pre-2, the EIH package, ledger tables 3-5 except
   the rows named in C18, S2g's junk scaling.
7. Note v3 with the passage; schematics refreshed to core-v0.8 (tracker files kept, status
   files exist); fig_b21_a2_state's title still says PARTIAL.
8. A `--full` checksum pass over the gate's runs (about 2 TB) is not on record; my verify took
   2252 files from the cache.
9. Decision 0013: the first clump passage (object b) is due now that the first black-hole
   passage is complete.
