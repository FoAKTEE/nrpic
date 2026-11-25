# Stage report: E-stoch-inf G3

Date: 2026-11-25 · branch `track/E-stoch-inf` at `c42d4e521df2` · checklist
`tracks/E-stoch-inf/stage/G3/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/E-stoch-inf/G3-fail-20261125` (created and pushed by the orchestrator after review, decision 0003).

- 18 checklist items not PASS or NA: C1 OPEN, C2 OPEN, C3 OPEN, C4 OPEN, C5 OPEN, C6 OPEN, C7 OPEN, C9 OPEN, C10 OPEN, C11 OPEN, C12 OPEN, C13 OPEN
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)
- no stage/G3/EVIDENCE.md (decision 0012)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G3/STAGE_REPORT.md` | present |
| `stage/G3/EVIDENCE.md` | MISSING |
| `stage/G3/OPEN.md` | present |
| `stage/G3/CHECKLIST.md` | present |
| `stage/G3/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G3/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `spec/scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G3 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The pre-registered scan is complete | not started: scope fixed (spec/scope/SCOPE.md 4d with the dated amendments 4d.9, commit 905feb7c0, before any production run); pilot q0050, G3-C q0051, G3-R q0052, baseline q0053-q0054 in the shared queue (2026-11-25 batch 19) | OPEN |
| C2 | Robustness checks | planned: G3-C (4d.4 with A6), G3-R (4d.5 with A7), level 2 (4d.7 with A11); gauge leg withdrawn as a criterion, stated as a limitation (A8, decision 0040 item 1) | OPEN |
| C3 | Comparison with the literature | reference: corrected one-patch delta N of the 128 band (A1; pilot E-20261125-151340-743c38c passes the variance gate 0.9993 +- 0.0032); 4e6 direct E-20261125-152832-c301e92 (gate 0.99865 +- 0.00058, skewness 0.0199 +- 0.0012); importance-sampled nu = 4 E-20261125-160658-855db8c (g3/amend entry 10); sigma = 0.1 lattice E-20261125-160722-a6d1f26 (gate failed, bound of A10 not reached; entry 9); model and landmarks of the reference = the deck (TO VERIFY of 4d.3 settled, E-20261125-161456-8d3f43c) | OPEN |
| C4 | Null results and failed runs are on record | on record so far: smoke run E-20261125-152619-d917a14 preceded by the failed E-20261125-152419-40200ec (g3/amend/JOURNAL.md entry 5); refuted prediction LB2 (entry 4); batch 20: TS1 failed (entry 9), the constant shift of A9 failed its smoke test (entry 8), zeta Z1 along Pi and Z2(iii) failed as written (zeta/JOURNAL.md entries 6-7), rerun E-20261125-161757-fb0eb95 stopped (too slow) | OPEN |
| C5 | Result figures and tables | — | OPEN |
| C6 | The numerical ledger in the Supplemental Material | — | OPEN |
| C7 | Tail statistics, compared with E-pre-3 | the criterion of the track sheet; its statistic, estimator and criteria are SCOPE 4d + 4d.9 (A2 judges variance and tail shape apart) | OPEN |
| C8 | Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013) | decision 0013 concerned G0-G2; the scope of G3 was decided by decisions 0038 item 2 and 0040 item 1 and is written in SCOPE 4d with 4d.9 | NA |
| C9 | Schematic: Sketch of the parameter space | — | OPEN |
| C10 | Data figure: Main results | — | OPEN |
| C11 | Data figure: Robustness | — | OPEN |
| C12 | Data figure: Comparison with the literature | — | OPEN |
| C13 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | — | OPEN |
| C14 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | — | OPEN |
| C15 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | — | OPEN |
| C16 | Working note written with /paper-writing; its manuscript checker passed with --compile | — | OPEN |
| C17 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | — | OPEN |
| C18 | Null results and failed runs are on record (manifests and JOURNAL) | — | OPEN |
| C19 | STATUS.md, JOURNAL.md and HANDOFF.md are current | current at the end of batch 20 (STATUS.md, JOURNAL.md, HANDOFF.md) | OPEN |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-25T16:50:43Z, clean export of `c42d4e521df2`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of c42d4e521df2 (HEAD) in /data/haiyangw/nrpic/scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G3-c42d4e5-20261125T165017Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | WARN | stage/G3/ lacks EVIDENCE.md (decision 0012; STAGE_REPORT.md comes from `report`); scoping text: spec/scope/SCOPE.md; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 12 figures, each with its script |
| min-figs | PASS | 3 schematics and 9 data figures (brief 13.4 asks at least 1 and 1 at G3) |
| runs | PASS | 318 run manifests finished (30 hand-written, read as decision 0012 allows); failures of 7 runs waived by coord/WAIVERS.md (decision 0019) |
| runs-waived | WARN | failures of the manifest check waived: 7 runs named in main's coord/WAIVERS.md (decision 0019 item 6): E-20261123-035724-b661081: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-152119-38957ba: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-153146-d965002: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-153347-18e7c21: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-164235-49b0945: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1) |
| run-notes | WARN | 30 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | output checksums not re-verified (--no-checksums) |
| status | PASS | STATUS.md has 40 lines |
| rerun | WARN | re-run skipped (--no-rerun) |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_background.* | note/scripts/fig_background.py | data | to be confirmed by the session |
| note/figures/fig_cost.* | note/scripts/fig_cost.py | data | to be confirmed by the session |
| note/figures/fig_deltan.* | note/scripts/fig_deltan.py | data | to be confirmed by the session |
| note/figures/fig_freezing.* | note/scripts/fig_freezing.py | data | to be confirmed by the session |
| note/figures/fig_noise.* | note/scripts/fig_noise.py | data | to be confirmed by the session |
| note/figures/fig_sr_constraints.* | note/scripts/fig_sr_constraints.py | data | to be confirmed by the session |
| note/figures/fig_sr_freezing.* | note/scripts/fig_sr_freezing.py | data | to be confirmed by the session |
| note/figures/fig_sr_modes.* | note/scripts/fig_sr_modes.py | data | to be confirmed by the session |
| note/figures/fig_sr_order.* | note/scripts/fig_sr_order.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_dataflow.* | note/scripts/schem_dataflow.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported (`stage/G3/VERIFIER.md`, decision 0016).

## Null results and failed runs

- `E-20261115-135532-5ec2b09`: failed (exit 1), L-R noise: rerun of the E-pre-4 checks (twin, counts, self-test, dump adapter, reader on AthenaK output) and comparison with runs E-stoch-inf-20261115-125255-fcdcbdc, -132950-16a0168, -133731-2031735
- `E-20261115-140116-87c1cc5`: failed (exit 1), L-R codebase: rerun of the E-pre-2 checks D1-D4 and the cost model, comparison with run E-stoch-inf-20261115-123936-b2ec5c7
- `E-20261115-140502-2957846`: failed (exit 1), L-U2 and L-U3: per-mode diagnostic of the A1 difference (U6 Markov tanh, U1 frozen) and the three validations with each run's own input, on the outputs of run E-20261115-135523-a32c3a6
- `E-20261115-170651-885fc6e`: stopped (exit -15), Noise unit test, base case on processors (release core-v0.3): U2 (8 MeshBlocks, 64^3 x 300) as the reference of U9 (A14), then U4 = U2 restarted at cycle 150 (A12)
- `E-20261115-171628-1737ebe`: failed (exit 1), Constraint estimators of sfa.py on core's plane perturbation (N=16, 32) with the release processor executable: dump statistics against the code's history, convergence of |H|/[H] and |M|/[M]
- `E-20261115-171633-f574079`: failed (exit 1), ladder: mode files of the SR case (nmax2 = 256, 1024, 4096, kstart 100) with core's make_case.py of core/scalar-2 25daeed (extracted read-only by git archive)
- `E-20261115-172421-50ac4ce`: failed (exit 1), note v0: data figures (background, freezing, delta-N, noise validation, cost), the two schematics, the ledger and the check of the lead's numbers against the run outputs (predictions N1-N3 of note/JOURNAL.md)
- `E-20261115-172521-e098160`: stopped (exit -15), ladder: SR case at N = 32, nmax2 = 64 (L32 +-1 to t = 8.5; +-1/2 and negative control to t = 4.5) on core/scalar-2 a58e95b processor executable (A2, A3, A4, A5 bottom rung)
- `E-20261115-174515-4d30c15`: failed (exit 2), G0 verifier V6/V7: core's Mukhanov-Sasaki noise model with kicks and coupling (deck problems/scalar/noise_ms.athinput, N=32, nmax2=64) on the release processor executable: bit identity across three MeshBlock layouts and a restart, negative control (Pi sign) and continuum projector against the momentum constraint; processor timing of the synthesis vs MeshBlock size
- `E-20261119-145853-ef835c2`: failed (exit -15), Lead review LR1/LR2: rerun of the ladder's final analysis (analyse_all, verdicts, make_figures), floor analysis and A6 analysis at the current commit on the raw outputs of the ladder runs, for comparison with the committed ladder/results
- `E-20261121-030415-22d518b`: failed (exit 1), g1verify V7 (A7, cost): bit-identity of the noise unit-test dumps (U1/U2/U3 MeshBlock layouts on the card, U2 vs U4 restart on processors and card) on the files themselves, sha256 against the runs; card vs processor for information; cost of one 256^3 realisation from the manifests (JOURNAL entry 3, P-V7)
- `E-20261121-031936-16d6ae5`: failed (exit 1), g1verify V4/V5 analysis from my constraint pass E-20261121-030657-c1afe38: odd/even parts of H, M over <[H]>, <[M]>, dominance, halving factors above the floor, negative controls, record maxima and halving factors, strict A4 and A4' tests, spatial order L32-L256, floor against N (JOURNAL entry 3, P-V4, P-V5)
- `E-20261121-034609-f573ddc`: failed (exit 1), ladder item (c): L5 single-kick analysis of the eleven card runs K1p ... N1m of E-20261121-025643-02526ff (parts in s cell by cell, kick reference, verdicts PL1-PL3 of JOURNAL 14)
- `E-20261121-063758-d643396`: failed (exit 1), lead review wave 3 (batch 2a), checks LW1-LW6 with the lead's own code on the raw dumps: seed 2 of P256 (A1-A3), P256 odd/even of H time-matched and index-paired, record maxima, A6 at 64^3, L5 second order and first-order M, L5 step test at 32^3; predictions in JOURNAL entry 2026-11-21T06:35Z
- `E-20261123-015650-493cff5`: failed (exit 1), g2prod analysis u320: pair U320ap/U320am at N_f only (every U-R clause is stated at N_f), records whole: U-A0, U-A1, U-A3, U-A2' odd part, even/odd, lockstep; predictions entry 1
- `E-20261123-020746-78d0c54`: failed (exit 1), repro/langevin: figures, tail fits, bootstrap moments and variant comparison from run E-20261123-020327-e524721
- `E-20261123-035925-8439d79`: failed (exit 1), repro/scope RSF256: SR 256^3 as in the paper, seed A, s=+1, level 0, 35 dumps with metric, H, M_i, [H], [M] (Figs. 2, 3, 6a); arXiv:2512.14649 reproduction, release core-v0.6 card build; predictions repro/scope/JOURNAL.md entry 1
- `E-20261123-045030-c20bcb3`: failed (exit 1), repro/scope RNC256: SR 256^3 sign-flip control (noise_pi_sign = -1) to the end of the entry, seed A (P1:541); arXiv:2512.14649 reproduction, release core-v0.6 card build; predictions repro/scope/JOURNAL.md entry 1
- `E-20261123-065855-265732a`: failed (exit 1), repro/scope CL256U: USR 256^3 convergence rung k_max/dk = 8 (nmax2 = 64), seed A (Fig. 8b); arXiv:2512.14649 reproduction, release core-v0.6 card build; predictions repro/scope/JOURNAL.md entry 1
- `E-20261123-090727-4b6e5a5`: failed (exit 1), repro/scope CL256S: SR 256^3 convergence rung k_max/dk = 8 (nmax2 = 64) to N_f, seed A (Figs. 7, 8a); arXiv:2512.14649 reproduction, release core-v0.6 card build; predictions repro/scope/JOURNAL.md entry 1
- `E-20261123-152119-38957ba`: failed (exit 1), repro/ablation AL2S: SR 256^3 ablation, backreaction level 2 (local coefficients, mesh R), seed A, 18 dumps (Fig. 9); arXiv:2512.14649 Fig. 9, branch card build core_noise-level2 (6ca93cba, decision 0031 item 3); predictions repro/ablation/JOURNAL.md entry 1
- `E-20261124-130529-da8c917`: stopped (exit 1), repro/continue RSF256: E-20261123-035925-8439d79 (repro/scope) continued from its restart sr.00000.rst to tlim; SR 256^3 as in the paper, seed A, s=+1, level 0, 35 dumps with metric (Figs. 2, 3, 6a); same executable (byte copy rc-v06-gpu, sha256 ea473498), deck and overrides; predictions repro/continue/JOURNAL.md entry 1 and those of the original
- `E-20261124-130711-a5dec67`: stopped (exit 1), repro/continue CL256U: E-20261123-065855-265732a (repro/scope) continued from its restart usr.00002.rst to tlim; USR 256^3 convergence rung k_max/dk = 8 (nmax2 = 64), seed A (Fig. 8b); same executable (byte copy rc-v06-gpu, sha256 ea473498), deck and overrides; predictions repro/continue/JOURNAL.md entry 1 and those of the original
- `E-20261124-181756-14fc721`: failed (exit -15), repro/verify V5-V6: own reader of the 18 dumps of the SR 256^3 run E-20261121-202935-31520bc: R^NR per mode, shell power, constraints
- `E-20261124-181817-059b3d5`: failed (exit -15), repro/verify V5-V6: own reader of 24 of the 41 dumps of the USR 256^3 run E-20261123-021204-2f573ec: R^NR per mode, shell power, constraints and magnitudes
- `E-20261124-184003-71eb0a8`: failed (exit 1), repro/verify post-verdict: definitions of the note scripts (entry window 0.05<N<=ln 8, shells with >10 modes) applied with my own readers to explain the NOT CONFIRMED digits
- `E-20261124-201031-4c41e7b`: stopped (exit 1), repro/continue RSF256: E-20261123-035925-8439d79 (repro/scope) continued from its restart sr.00000.rst to tlim; SR 256^3 as in the paper, seed A, s=+1, level 0, 35 dumps with metric (Figs. 2, 3, 6a); same executable (byte copy rc-v06-gpu, sha256 ea473498), deck and overrides; predictions repro/continue/JOURNAL.md entry 1 and those of the original
- `E-20261124-202134-0b1ce0c`: stopped (exit 1), repro/continue RSF256: E-20261123-035925-8439d79 (repro/scope) continued from its restart sr.00000.rst to tlim; SR 256^3 as in the paper, seed A, s=+1, level 0, 35 dumps with metric (Figs. 2, 3, 6a); same executable (byte copy rc-v06-gpu, sha256 ea473498), deck and overrides; predictions repro/continue/JOURNAL.md entry 1 and those of the original
- `E-20261124-220850-3ef0c7f`: failed (exit 1), repro/verify update pass V9-V11a: joins of the five continued runs, SR sign flip over its full span, Fig. 8 records 32-256 (own code, records only)
- `E-20261124-221028-81db3d8`: failed (exit 1), repro/verify update pass V10-V12: constraint ratios from the dumps of RNC256 and RSF256, Fig. 7 256^3 rung against lockstep and my MS reference and between rungs, SR/USR level 2 against level 0 at N_f (own readers)
- `E-20261124-224156-28cbf07`: failed (exit 1), R8a: four readers of R^NR on dump 17 of C128S and CL256S against one linear reference (why the note's and the check's 256^3 members of Fig. 7 differ, ledger rows 68-71)
- `E-20261124-230810-9ae014e`: failed (exit 1), repro/figs figure run 7: every figure as E-20261124-213739-9776185 plus RSF256 to t = 8.5 (--rsf256 E-20261124-225826-0bf3842): Fig. 2 with constraint panels, Figs. 3 and 6a from RSF256, joins with RSF256 to 1386 and its record against P256v6, scope P2 whole-run maxima (entry 14)
- `E-20261125-022137-182e82c`: failed (exit -15), G2 verifier V1: own reference of the USR case (Friedmann + Klein-Gordon background, landmarks, continuum MS modes of 3415 shells from the mode file at N*, at every dump time of the release ladder), lattice rms at N_f, comparison with usr_reference.json and the lockstep record; predictions stage/G2/verifier/JOURNAL.md entry 1
- `E-20261125-043414-daca69d`: failed (exit 1), Gate review G2 of E (reviewer's own check): U-A4'(a)-(d) recomputed from the raw dumps of seed A at s = +-1, +-1/2, +-1/4 and the control with an own NRSFDMP2 reader; three-amplitude statistics; record maxima U-A4'(c) of the eleven release runs; dump-time pairing; sha256 of the files read. Predictions: stage/G2/GATE_REVIEW.md section 1 (commit daca69df)
- `E-20261125-152419-40200ec`: failed (exit 1), smoke run of the reference with the state at N_f (SCOPE 4d.9 A4): ref_spec.py inflection 2e4, NLAT 32, s0.01_lattice only, suffix _smoke; SM1-SM2 of g3/amend/JOURNAL.md entry 5
- `E-20261125-161757-fb0eb95`: failed (exit -15), zeta reader rerun with a second independent map for Z1 (DOP853 in N on (phi - phi_e, v)); everything else as E-20261125-161456-8d3f43c; prediction zeta/JOURNAL.md entry 6
- `E-stoch-inf-20261115-125316-dafadc4`: failed (exit 1), V2: quadratic inflation m = M_Pl, phi_in = phi_UV = sqrt42 (2206.11234 Fig. 2): Monte Carlo (direct and importance sampling) vs closed-form characteristic function, BDF2 survival solver, moment recursion; pole structure
- `E-stoch-inf-20261115-131526-629fed8`: failed (exit 1), T-N6 of noise/JOURNAL.md: calibration of the A3 decisions (KS of |w|^2 and arg w, fourth moment) on correct amplitudes, 2000 seeds of the base case; single-decision calibration and family-wise false-alarm rate per validation

## Open risks


Rewritten by the lead on 2026-11-15 at the G0 package; updated by the lead on 2026-11-19
(wave 2b) after the slow-roll ladder, the G0 verifier (`stage/G0/VERIFIER.md`) and the review
`stage/REVIEW-wave2.md`; updated by the lead of batch 2a on 2026-11-21 after the G1 verifier
(`stage/G1/VERIFIER.md`), the wave-3 ladder items and `stage/REVIEW-wave3.md`; updated by the lead of batch 3 on 2026-11-21 after the note and usr packages (`stage/REVIEW-wave3.md` Part B); updated by the lead of batch 13 on 2026-11-24 (R13, R23, R25, R27 changed; R28, R29 new); updated by the lead of batch 15 on 2026-11-24 (R25, R26 changed; R30, R31 new); updated by the lead of batch 17 on 2026-11-25 (R9, R28, R30 changed; R32-R34 new; G2 signed); updated by the lead of batch 19 on 2026-11-25 (R28 closed, R33 explained and closed, R34 changed; R35-R37 new); updated by the lead of batch 10a on 2026-11-22 after the g2prod ladder (R13, R24, R25-R27). Sources: `spec/scope/SCOPE.md` (sections 3, 4, 4b, 8),
`codebase/DESIGN_REVIEW.md`, `langevin/README.md`, `noise/NOISE_SPEC.md`, `ladder/README.md`.
Labels as in the brief.

| Id | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| R1 | The SR results of G1 were made with core's tested-branch executable `core/scalar-2` (a58e95b), the USR scouting card runs with `core_scalar-3` 5cc2821, not releases | low (both are in release core-v0.6) | medium | release processor build = scalar-2 word for word on L32p/L32m (run E-20261121-064707-77ec326); core's card check of core-v0.5 on the s3g and usr decks | P256 again on the release card build core-v0.6: run E-20261121-202935-31520bc (Slurm 4828, submitted 2026-11-21, prediction P256v6 of `g2prod/JOURNAL.md` entry 1); all G2 production runs of `g2prod` use the release core-v0.6 card build |
| R2 | A defect in core's stochastic hook that the tests cannot see | low | high | A6 at 32^3 and 64^3 (orders 3.82-4.10); L5 single kick (wave 3): H second order to 1e-6 in the halving factor, the kick's projector term equal to the one-step reference within 1.2 percent, remaining first-order M the fourth-order time error (A/B 15.5-19.5), no first-order stage-timing defect (runs E-20261121-034645-02a463e, -040015-436a615; lead LW5-LW6) | keep the sign-flip control in every set-up; "L5 never run" is closed |
| R3 | The papers leave the Courant factor, run lengths, Bunch-Davies form, noise stepping and tolerances open (SPEC 8) and print wrong formulas (SPEC 9) | certain | medium | SPEC 8, 9; kb claims 603-609 | per-mode acceptance needs no published tolerance; E6 (extraction factor 1/4) now tested by run E-20261115-174214-74becdd; the P2 initial-condition equation is "eq. (17)" in our older texts, but the source numbers it 23rd (SPEC 5.3 note) [TO VERIFY against the PDF] |
| R4 | The freezing criterion fails for a reason other than a defect | low | high (downgrade trigger) | A3 / U-A3 drift after N_k + 4 | SR passed on every rung (drift 1.4e-4 per e-fold against 2.5e-3); USR U-A3 passes at 64^3-256^3 (0.9923-1.0016 single run, 0.99992 odd part; runs E-20261121-084815-63462b8, -101756-6bffd0c) |
| R5 | Unit conversion G = 1 against Mpl = 100 | low (was medium) | high if wrong | A1 | A1 passes at 1e-11 on every rung (ladder; lead's check run E-20261119-150238-b81e33f) |
| R6 | Geodesic slicing breaks down where perturbations collapse; USR outliers R ~ 10 (P1:534) | low for the test cases, high for science | medium | X contrast, outliers of R^NR | stop at the published N_f; a gauge study belongs to G2 |
| R7 | Momentum constraint ~ 1e-2 late in USR (P1:541); first-order truncation part at four cells per wavelength | happened as expected | medium | M/[M] record, odd part of M | reproduced: <abs M/[M]> 2.5e-2 at cN 6.6, 2.1e-3 at N_f (U256); late it is an s-independent floor over a magnitude proportional to the amplitude, not an error of the solution (usr entries 12, 15); strict A4 failed on record in SR, A4' adopted (decision 0021); for USR U-A4' proposed to orch (outbox 20261121T131021Z) |
| R8 | Window (s, sigma) and gauge dependence (brief 462); sigma = 1 separate-universe Langevin overestimates the variance by 42-45 percent | window: low (scan done); gauge: medium | medium | scan L9 analysed (E-20261121-154733-0d1fbda; rerun by the lead E-20261121-203008-f104a3e): USR spectrum at N_f window-independent within numerical error (<= 1.9e-4 to k_max/2, <= 9.1e-3 to k_max); late constraint records depend on sigma (x0.14-x21.7, W6 refuted) | the window result is the G2 criterion U-W (SCOPE 4c); no further window run; compare NR with the sigma <= 0.01 reference only (A8); gauge: geodesic slicing only (R6) |
| R9 | Tail statistics need many realisations | lower now (G3 scope at 128^3) | high for S11 item 2 | power estimate E-20261125-115822-29795d6: a 128^3 USR box holds about 5.5e5 effectively independent cells, one box measures F(3) to 4 per cent; the seed count is set by the reach into the tail (S = 256 for nu = 4 to 1.2 per cent; SCOPE 4d.2); cost about 0.035 card-h per 128^3 seed (window scan), pilot q0045 measures it on core-v0.7 | full set only after the pilot; S raised to at most 512 if the measured scatter exceeds 1.4 times the Gaussian one; 256^3 single runs (0.5-0.6 card-h) stay for resolution checks only |
| R10 | Competition with the group of the formalism (P1:587 announces the same science) | high | medium | arXiv listings of the authors | target what they leave open: tail statistics against delta-N, hand-over to EMD |
| R11 | The stochastic formalism itself is debated (brief 264) | medium | affects science, not the reproduction | literature | keep level 0 and level 1 as variants and state the dependence |
| R12 | Processor build slow (1.2e4-1.35e4 zone-cycles/s serial); cold dumps at 128^3-256^3 read through a memory map at a few MB/s when the disk is busy (lead's rerun E-20261119-145853-ef835c2 stopped) | certain | low | | N = 32 on processors; analyse large dumps right after the card job (page cache) or read them sequentially |
| R13 | Budget: G2 allotment 30 card-hours (decisions 0031, 0032); used 19.32 at 2026-11-24 14:23 PST (manifest of E-20261124-214913-5956891); the reproduction used 8.99 in all (repro/scope/CARD_PLAN.md); floor test FL128h/FL256h asks 1.25 at its ceilings (0.4-0.65 expected) | certain | low | `nrpic-run budget`, manifests | queue only what a gate package or the note waits for; ceilings near measured cost |
| R14 | Harness: hand-written run manifests broke `nrpic-run budget` | happened, fixed | low | `nrpic-run budget` | statuses normalised; decision 0016 item 3 |
| R15 | USR ends at the border of diffusion domination (verifier weak point 3): classical drift per e-fold equals H/2pi at N* + 8.3 (ratio 0.98), Delta_R reaches 1 at 64 dk, one H/2pi kick moves the end of USR by about one e-fold; a delta-N end surface at N* + 10 sits just past the stationary inflection point | high for G2/G3 | high for the validity of linear-noise level-0 runs and of the delta-N reference | verifier V2b (run E-20261115-180056-d62ee5a: f_NL 0.011, response near-linear in the 256 box) | state the validity window at G2; do not enlarge the box or move the noise cut later without a level-1 comparison; place the delta-N end surface away from the inflection point |
| R16 | The double-precision rounding floor of the constraints grows as N^2.5 (6e-13 of <[H]> at 256^3 half an e-fold after N*) and limits what 256^3 shows during the first e-folds | certain | low (still 1e2 below P1's 1e-10) | odd part not scaling with s | the verifier measured three properties of rounding (does not scale with s; equal in odd and even parts; non-scaling parts in the ratio sqrt(17/5) of four independent noises) [VERIFIED, g1verify V5]; size and N^2.5 law [JUDGEMENT]; no run in another precision |
| R17 | Acceptance criteria reworded after the data (A4', A5', SCOPE 4b; for USR U-A2', U-A4') | happened | medium (credibility of the gate) | orchestrator's rulings | A4' adopted by decision 0021; for G2 the definitions (floor, clause on the maxima, U-R, U-S, U-W) are fixed in SCOPE 4c (commit 43dcc9cc) before any G2 production run, as decision 0023 item 1 asks; the strict forms stay failed on record |
| R18 | The absolute constraint levels are 40-100 times below P1's statements (proper ~1e-10, control ~1e-5, P1:538-541) while the ratio control/proper matches (verifier weak point 7) | open | medium (a definition mismatch would change the A4' magnitude clause (c)) | `stage/G1/VERIFIER.md` 7 | [TO VERIFY]: compare the definition of [H] and of the box statistic in P1 with core's record (`coord/INTERFACES/scalar_field_2.md`); no run needed |
| R19 | Packages cut by the usage limit leave uncommitted work and finished card jobs without analysis (wave 3: note and usr finished in batch 2b; a4res still has three untracked scripts; window's job ran, not analysed; usr entry 10 was first committed after the job it amends had run) | happened | medium (provenance of predictions; card time spent without result) | `git status`, `nrpic-run status` | the next session of each package commits its own files first; leads leave them alone; entry 10 rescued no verdict (`stage/REVIEW-wave3.md` B1) |
| R20 | Frontier items from the knowledge base (orch message 20261120T221329Z): hidden higher-derivative spikes of inflection potentials (2606.28005), UV sensitivity of mean-field backreaction to Bunch-Davies UV modes (2610.26669), non-Markovian noise (2602.11652, 2605.00476) | medium | medium for the USR acceptance discussion (G2) | `coord/FRONTIER.md` | check the test potential's derivatives and state the UV dependence in the G2 acceptance text; Markovian noise stays the reproduction's choice (P1) |
| R21 | The lockstep mode-function record integrates from N* with the run's step and carries RK4's phase error k^5 dt^4/600 into the injected top shells (2.55e-3 at k = 64 dk, 256^3) | certain in P1's set-up | low for U-A2 (k <= 32 dk: below 8e-5), medium for the top-shell spectrum (U-A5 6.7e-3) | usr entry 14.2 (L1: 0.973-1.023 of the law on 2934 shells) | request to core to sub-step the record (outbox 20261121T131020Z); until then quote top-shell numbers with this error |
| R22 | Late in the 256^3 USR pair the momentum parts are equal and flat at 1.6e-13-1.9e-13 absolute, seven times the 128^3 floor; cause not named | open | low (after USR, below the record's 2e-3) | usr entry 15 | the halving pair at 256^3 (U256hp/hm, s = +-1/2) is queued in `g2prod` (last but one; waits for the allotment) |
| R23 | Unattended card runs: own sequencers are retired (decisions 0033, 0034: one shared queue, cap of five jobs for the account); the g2prod sequencer ended by itself on 2026-11-23 20:06 PST after U256qp/qm | retired 2026-11-24 | - | `nrpic-queue list --owner E-stoch-inf` | queue entries carry --package so later edits elsewhere do not block them |
| R24 | 320^3 and 384^3 never ran | retired 2026-11-22 | - | timing E-20261121-202929-43dcc9c | 320^3 2.52 s per step, 36.4e3 MiB; 384^3 4.30 s, 61.1e3 MiB (fits one card); U320 pair ran in two segments each |
| R25 | U-A4'(a) misses at one dump of M (3.9245 at cN 6.52, bar 3.95-4.05): as written the USR case is not reproduced in full | happened; stays FAILED (rulings 0030 item 2, 0036 item 2) | high for the G2 verdict (the gate review decides) | g2prod entry 4: Q-a refuted (4.1275 from s = 1/2, 1/4), so no s^4 cause; verifier's three-amplitude reading (E-20261125-023427-6fb6400): the 4c floor estimator, every judged factor within 4 +- 0.005 | on record beside the reading after the data; proposal of a three-amplitude floor for later gates (outbox batch 15) |
| R26 | A common factor of all modes in the odd part, -4.107e-5 at s = 1, -9.87e-6 at 1/2, -2.07e-6 at 1/4 (a s^2 + b, a = -4.16e-5, b = +5.3e-7), arises after cN 5.5: a third-order term; it caps the k <= 32 maximum under resolution (U-R factor 2.10, ratio 0.992 below |n| ~ 25) | certain | low for U-A2', medium for U-R and for 1e-4 comparisons; a finer rung would fail U-R (i) as written | g2prod 4.1 (Q-b held); note Fig. 14 | which third-order term is not named; U-R clause on the discretisation part proposed for later gates (outbox batch 15) |
| R27 | Several sessions of E share this worktree (repro/*, decision 0028; finished on 2026-11-24): a commit without paths could take another session's staged files | lower now (the reproduction is complete) | medium | git status | path-limited commits only |
| R28 | The SR spectral convergence stops at a floor of about 1.5e-7 (power) at the lowest shells, the same at 128 and 256 cells | CLOSED (batch 19) | - | floor/JOURNAL.md entries 3-4: the floor halves with the amplitude at 128^3 (E-20261125-115344-a22128b) and at 256^3 (ratios 1.997, 2.000, no sign flip; E-20261125-151222-d5a5f2f of FL256h E-20261125-115534-8414659): the second order of the field | the note states it (repro/note JOURNAL entry 29) |
| R29 | The one-point spread of the fields is 3.5-4 times narrower in our runs than in the published one-point figures while the spectra agree (repro/note, open; verifier: Parseval check of P1 Fig. 2 against Fig. 3 inconsistent by that factor) | open | medium for the reproduction verdict, low for G2 | repro/note Table IV | a question to the authors is the group's step (nobody here contacts them); state it as [JUDGEMENT] |
| R30 | The three-amplitude statistics (D1, D2, sigma) exist only in the verifier's run; the package's reader has not recomputed them, and what the per-run part F_s is (deterministic, equal size at every s; rounding not shown) is open | open | medium if the reading is cited beyond 'after the data' | stage/G2/OPEN.md items 4, 5 | recompute D1, D2 with the track's reader before any later gate relies on a three-amplitude floor; SCOPE 4d.4 (G3) now requires the track's own reader for D1, D2 and sigma |

## Decision requested from the group

One paragraph: accept G3 of E-stoch-inf, or what is missing.

TO WRITE by the track before the package is submitted (`nrpic-stage report ... --decision "..."`).
