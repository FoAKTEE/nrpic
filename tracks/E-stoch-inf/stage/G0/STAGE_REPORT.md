# Stage report: E-stoch-inf G0

Date: 2026-11-15 · branch `track/E-stoch-inf` at `c04f424c3b4e` · checklist
`tracks/E-stoch-inf/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/E-stoch-inf/G0-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 4 checklist items not PASS or NA: C2 FAIL, C8 OPEN, C18 OPEN, C20 OPEN
- verify ran on 5c1933b; files changed since: tracks/E-stoch-inf/ladder/JOURNAL.md, tracks/E-stoch-inf/runs/E-20261115-174008-7aee5ff/manifest.json (run verify again)
- verify reported FAIL: runs
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | present |
| `stage/G0/EVIDENCE.md` | present |
| `stage/G0/OPEN.md` | present |
| `stage/G0/CHECKLIST.md` | present |
| `stage/G0/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `spec/scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | spec/scope/SCOPE.md (owner's version 1): problem statement section 1, parameter ranges 2, exit criteria and the owner's decisions 4, test plan by row of brief 10 section 5; stage/G0/EVIDENCE.md | PASS |
| C2 | The statements of the key references verified in the knowledge base | verified at the raw store (kb-data/raw/arxiv, all eight references ingested by kb, inventory status ok) with file:line locators, SCOPE.md section 3; key P1, P2, BZ lines re-read by the lead; errata not yet knowledge-base claims: outbox 20261115T1410Z__to-kb__errata-s11-references.md | FAIL |
| C3 | Risk list | RISKS.md (R1-R14); SCOPE.md section 7 | PASS |
| C4 | Compute estimate | SCOPE.md section 8 (codebase/figs/cost.json, run E-stoch-inf-20261115-123936-b2ec5c7, rerun identical in E-20261115-140116-87c1cc5; GPU throughput docs/TESTLOG.md:46; processor throughput runs E-stoch-inf-20261115-122727-a1c2237 and E-20261115-135218-bdf4710). Card overhead now measured by core (run core-20261115-143907-cea4c86: 65 percent instead of the assumed 15); recomputed with it, one 256^3 realisation costs 0.57-0.71 (SR) and 0.71-0.88 (USR) card-hours, an extrapolation from 128^3 (note Sec. V, Fig. 6, note/scripts/costmodel.py, run E-20261115-173904-3be0405); the conclusion of SCOPE.md 9 holds | PASS |
| C5 | Working note v0 | note/main.tex, note/main.pdf (REVTeX, 9 pages: problem and acceptance criteria, set-up and corrected initial slice, freezing and delta-N references, noise validation, cost and decision, open items; appendices parameters, errata, ledger); figures and tables from run E-20261115-173904-3be0405; predictions and outcomes note/JOURNAL.md N1-N3; claims check note/tables/claims.md (59 numbers of the lead's documents, 54 agree, 5 differ, listed in note/README.md) | PASS |
| C6 | Architecture schematic | note/figures/schem_architecture.png (Fig. 2 of the note; script note/scripts/schem_architecture.py, run E-20261115-173904-3be0405; PNG looked at) | PASS |
| C7 | Stage timeline | table in SCOPE.md section 10; schematic note/figures/schem_timeline.png (Fig. 7 of the note; run E-20261115-173904-3be0405) | PASS |
| C8 | Reproduction specification, code-base assessment and compute estimate are complete, and the group decides to continue, to shrink or to downgrade | specification (spec/SPEC.md), code-base assessment (codebase/DESIGN_REVIEW.md; decision 0010) and compute estimate (SCOPE.md 8) complete and checked by the lead (EVIDENCE.md 2); the group's decision is pending: outbox 20261115T1410Z__to-orch__g0-decision-requested.md; recommendation SCOPE.md 9 (continue) | OPEN |
| C9 | Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013) | applied: the note's recommendation and timeline follow the ruling (continue to G1 and G2, scope of G3 decided at G2; note Sec. V, Fig. 7); the acceptance criteria of SCOPE.md section 4 are those of the note (Sec. II C). The group's decision itself is item C8 | PASS |
| C10 | Schematic: Track architecture (three states: exists, to be ported, new) | note/figures/schem_architecture.png: exists (green), to be ported (slate), new (red), deliverables (plum); PNG looked at | PASS |
| C11 | Schematic: Stage timeline | note/figures/schem_timeline.png: gates G0-G4 at the indicative times of SCOPE.md 10, requirements, needs between gates; PNG looked at | PASS |
| C12 | Data figure: None required | none required at G0 | NA |
| C13 | Data figure: Data from the literature may be redrawn | P1 Fig. 1 values redrawn against the reference: spec/fig/fig_background.png (run E-stoch-inf-20261115-123236-2e87364) | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md in stage/G0; scoping text spec/scope/SCOPE.md (named in the report); no separate REVIEW.md: the lead's re-check of the helpers is EVIDENCE.md section 2 (for the lead to confirm) | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | package figures (spec/fig, codebase/figs, langevin/fig, noise/fig) and the lead's (E-20261115-135532-3f958a1, E-20261115-140553-0b75e1e, E-20261115-140502-2957846) with python/nrpic/figstyle.py; the note's five data figures note/figures/fig_{background,freezing,deltan,noise,cost}.png with note/scripts/czstyle.py (unchanged copy), one script each, from checksum-verified outputs of registered runs (run E-20261115-173904-3be0405), every PNG looked at | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/scripts/schem_architecture.py and schem_timeline.py with note/scripts/paperfig.py (unchanged copy of harness/style/paperfig.py); both PNGs looked at | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | paper-writing guide and notation ../WRITING_GUIDE.md, ../NOTATION.md; check_manuscript.py --compile on note/main.tex: 0 undefined references, 0 undefined citations, 0 overfull boxes; remaining candidates are the run ids of the ledger appendix and the document names in the scripts, accepted by exception 1 of the guide; captions within five lines on the rendered pages (looked at). Reviewer subagents of the skill's step 4 not run | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | no VERIFIER_REPORT.md (OPEN.md item 4); the lead's independent checks are in EVIDENCE.md section 2; the note's ledger and the lead's numbers are recomputed from the run outputs by note/scripts/ledger.py (run E-20261115-173904-3be0405), which is not a fresh-context verifier | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | EVIDENCE.md section 4; failed runs E-stoch-inf-20261115-125316-dafadc4, -131526-629fed8, E-20261115-135532-5ec2b09 (library-log leaf), E-20261115-140116-87c1cc5 (timing leaves), E-20261115-140502-2957846 (diagnostic syntax error) kept with manifests; refuted predictions in the package journals and the owner JOURNAL | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md and HANDOFF.md describe the state before the merge of release core-v0.3 (scalar field on the unmerged branch, no card build; HANDOFF names wt/core-scalar executables); to be rewritten for wave 2 by the lead (note/README.md, Requests) | OPEN |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-15T17:40:45Z, clean export of `5c1933bc0f7d`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 5c1933bc0f7d (HEAD) in /data/haiyangw/nrpic/scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G0-5c1933b-20261115T174010Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: spec/scope/SCOPE.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 8 of 63 runs have problems |
| run-notes | WARN | 30 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 35 lines |
| rerun | PASS | 7 of 7 scripts and commands ran cleanly in the export |
| compare | PASS | 14 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_background.* | note/scripts/fig_background.py | data | to be confirmed by the session |
| note/figures/fig_cost.* | note/scripts/fig_cost.py | data | to be confirmed by the session |
| note/figures/fig_deltan.* | note/scripts/fig_deltan.py | data | to be confirmed by the session |
| note/figures/fig_freezing.* | note/scripts/fig_freezing.py | data | to be confirmed by the session |
| note/figures/fig_noise.* | note/scripts/fig_noise.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported.

## Null results and failed runs

- `E-20261115-135532-5ec2b09`: failed (exit 1), L-R noise: rerun of the E-pre-4 checks (twin, counts, self-test, dump adapter, reader on AthenaK output) and comparison with runs E-stoch-inf-20261115-125255-fcdcbdc, -132950-16a0168, -133731-2031735
- `E-20261115-140116-87c1cc5`: failed (exit 1), L-R codebase: rerun of the E-pre-2 checks D1-D4 and the cost model, comparison with run E-stoch-inf-20261115-123936-b2ec5c7
- `E-20261115-140502-2957846`: failed (exit 1), L-U2 and L-U3: per-mode diagnostic of the A1 difference (U6 Markov tanh, U1 frozen) and the three validations with each run's own input, on the outputs of run E-20261115-135523-a32c3a6
- `E-20261115-170651-885fc6e`: stopped (exit -15), Noise unit test, base case on processors (release core-v0.3): U2 (8 MeshBlocks, 64^3 x 300) as the reference of U9 (A14), then U4 = U2 restarted at cycle 150 (A12)
- `E-20261115-171628-1737ebe`: failed (exit 1), Constraint estimators of sfa.py on core's plane perturbation (N=16, 32) with the release processor executable: dump statistics against the code's history, convergence of |H|/[H] and |M|/[M]
- `E-20261115-171633-f574079`: failed (exit 1), ladder: mode files of the SR case (nmax2 = 256, 1024, 4096, kstart 100) with core's make_case.py of core/scalar-2 25daeed (extracted read-only by git archive)
- `E-20261115-172421-50ac4ce`: failed (exit 1), note v0: data figures (background, freezing, delta-N, noise validation, cost), the two schematics, the ledger and the check of the lead's numbers against the run outputs (predictions N1-N3 of note/JOURNAL.md)
- `E-20261115-172521-e098160`: stopped (exit -15), ladder: SR case at N = 32, nmax2 = 64 (L32 +-1 to t = 8.5; +-1/2 and negative control to t = 4.5) on core/scalar-2 a58e95b processor executable (A2, A3, A4, A5 bottom rung)
- `E-stoch-inf-20261115-125316-dafadc4`: failed (exit 1), V2: quadratic inflation m = M_Pl, phi_in = phi_UV = sqrt42 (2206.11234 Fig. 2): Monte Carlo (direct and importance sampling) vs closed-form characteristic function, BDF2 survival solver, moment recursion; pole structure
- `E-stoch-inf-20261115-131526-629fed8`: failed (exit 1), T-N6 of noise/JOURNAL.md: calibration of the A3 decisions (KS of |w|^2 and arg w, fourth moment) on correct amplitudes, 2000 seeds of the base case; single-decision calibration and family-wise false-alarm rate per validation

## Open risks


Rewritten by the lead on 2026-11-15 at the G0 package. Sources: `spec/scope/SCOPE.md`
section 3 (R1-R13 of the spec helper), `codebase/DESIGN_REVIEW.md`, `langevin/README.md`,
`noise/NOISE_SPEC.md`, and the lead's checks (`stage/G0/REPORT.md`). Labels as in the brief.

| Id | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| R1 | The reproduction waits for core: initial slice at N* (SPEC 5.3), constraint and R^NR diagnostics, a card build of `core/scalar-field` are not there yet (field, kicks and noise are, at 836ac86) | certain | high on the G1 date | `git log core/scalar-field`; outbox replies | requests in `outbox/`; the track supplies mode tables, references and the validators; nothing else waits |
| R2 | A defect in core's stochastic hook that the generator tests cannot see (kick signs, stage bookkeeping of the lockstep mode data) | medium | high | single-kick test L5 and temporal test L6 of DESIGN_REVIEW 8.1 | L5 with the sign flip as negative control (P1:541); L6 at three Courant factors |
| R3 | The papers leave the Courant factor, run lengths, Bunch-Davies form, noise stepping, binning and tolerances open (SPEC 8) and print wrong formulas (SPEC 9: delta Pi of the initial data, draw normalisation, extraction factors, 4 pi in the K equation) | certain | medium | SPEC 8, 9 | per-mode acceptance (A2, freezing) needs no published tolerance; errata checked by runs and by the lead's derivation (JOURNAL L-I) |
| R4 | The freezing criterion fails because of the level-0 backreaction or the window, not because of a defect | low | high (downgrade trigger) | per-mode drift after N_k + 4 against the full-MS reference | P1 reports level 2 vs 0 changes the spectrum by at most 1e-4 (P1:520); a failure is first checked at level 1 before the downgrade is invoked |
| R5 | Unit conversion G = 1 against Mpl = 100 of the papers | medium | high if wrong | A1 box means against the Friedmann reference | SPEC 2.5 mapping; core's FLRW test and A1 catch a wrong 8 pi |
| R6 | Geodesic slicing breaks down where perturbations collapse; USR outliers R ~ 10 (P1:534), an 11-sigma event under the band reference (`langevin/README.md`) | low for the test cases, high for science | medium | X contrast, outliers of R^NR | stop at the published N_f; a gauge study belongs to G2 |
| R7 | Momentum constraint ~ 1e-2 late in USR (P1:541) | medium | medium | M/[M] history | accept the published level at G2, resolution study |
| R8 | Window (s, sigma) and gauge dependence (brief 462); sigma = 1 at horizon crossing; separate-universe Langevin with sigma = 1 overestimates the variance by 42-45 percent (runs E-stoch-inf-20261115-130137/-130139-176cdd6) | medium | medium | sensitivity scan L9 | compare NR with the sigma <= 0.01 reference only (SPEC A8) |
| R9 | Tail statistics need many realisations: 1e3 realisations at 256^3 cost 400 to 5000 card-hours (0.4-5 each, SPEC 11.2) | high for G3 | high for S11 item 2 | cost per realisation measured at G1 | smaller boxes, importance sampling, or the downgrade path; Track A gets delta-N statistics now from `langevin/` |
| R10 | Competition with the group of the formalism (P1:587 announces the same science) | high | medium | arXiv listings of the authors | target what they leave open: tail statistics against delta-N, hand-over to EMD |
| R11 | The stochastic formalism itself is debated (brief 264) | medium | affects science, not the reproduction | literature | keep level 0 and level 1 as variants and state the dependence |
| R12 | Processor build too slow for N >= 64 tests (1.35e4 zone-cycles/s, run E-20261115-135218-bdf4710); the 64^3 x 300 unit-test base case costs 95 min per run | certain | low | | scaled tests on processors (N = 32); 64^3 and above on a card build |
| R13 | Budget: 10 card-hours to the next gate (decision 0006) | medium | medium | `harness/bin/nrpic-run budget` | Courant factor 0.25 (G0 decision); 0.025 only if L6 shows a dependence |
| R14 | Harness: hand-written run manifests broke `nrpic-run budget` (status "failed (exit 1)") | happened, fixed | low | `nrpic-run budget` | statuses normalised (commit after e303538); outbox note to orch |

## Decision requested from the group

One paragraph: accept G0 of E-stoch-inf, or what is missing.

TO WRITE by the track before the package is submitted (`nrpic-stage report ... --decision "..."`).
## Scoping text and the products of this package (written by the note helper, wave 2)

The scoping text is `spec/scope/SCOPE.md` (owner's version 1), with the specification
`spec/SPEC.md`, the code-base assessment `codebase/DESIGN_REVIEW.md`, the noise contract
`noise/NOISE_SPEC.md` and the delta-N references `langevin/README.md`. The products that
OPEN.md items 2, 3 and 5 listed as missing now exist: the working note v0
(`note/main.tex`, `note/main.pdf`, 9 pages), its five data figures and the two schematics
(`note/figures/`), the ledger and the claims check (`note/tables/`), all from the registered
run E-20261115-173904-3be0405 (inputs checked against the checksums of their run manifests);
guide and notation `WRITING_GUIDE.md`, `NOTATION.md`; package README and journal
`note/README.md`, `note/JOURNAL.md` (predictions N1-N3 and outcomes; the failed run
E-20261115-172421-50ac4ce and the two superseded runs E-20261115-172442-78cf53e,
E-20261115-173135-858482f, E-20261115-173402-641b6e2 are on record there).

## Notes on the verification

- `clean`: PASS in the verify above (5c1933b) and the first one (55ab078); a verify in
  between (fad8f4b) failed it on uncommitted files of the ladder helper of this track.
- `runs` FAIL: the runs named in `VERIFY_RESULTS.md` belong to other wave-2 helpers of
  this track (noise unit test at 64^3, analysis, ladder) and were still running or submitted
  when verify ran; none is a run of this package. Verify again once they are finished.
- Every check of the note passed in both verifications: note, note-pdf, style, fig-script,
  min-figs, rerun (7 of 7 scripts), compare (14 files within tolerance), regenerate.
- `run-notes` WARN: 30 hand-written manifests of wave 1 are read with defaults; the note's
  scripts read their outputs only after checking them against the checksums those manifests
  record (`outputs_sha256` or the list form), which verify does not read.
- A fresh-context verifier of wave 2 is working in `stage/G0/` (its `JOURNAL.md` and
  `scripts/` were present, uncommitted, when this report was written); C18 stays OPEN until
  its report is committed.

## Disagreements between the lead's documents and the files (the files win)

Details and locators: `note/README.md`; numbers: `note/tables/claims.md` (59 numbers of
SPEC.md, SCOPE.md, EVIDENCE.md and langevin/README.md recomputed from the run outputs; 54
agree within half a unit of their last printed digit).

1. Card overhead of the scalar field and the sources over Z4c: assumed 15 percent
   (SCOPE.md 8) and 30 percent (SPEC.md 11.2); measured 65 percent by core at 128^3 (run
   core-20261115-143907-cea4c86).
2. Cost of one 256^3 realisation: 0.4-0.5 card-hours (SCOPE.md 8, 9); with the measured
   throughput 0.57-0.71 (SR) and 0.71-0.88 (USR) card-hours, 1e3 realisations 570-880 card-hours
   (extrapolated from 128^3; run E-20261115-173904-3be0405). The recommendation of SCOPE.md 9
   is unchanged by it: still 5.7 to 8.8 times below the downgrade threshold.
3. USR eps1(N*): 1.3164e-2 (SPEC.md 6, reference run) against 1.31625e-2 (lead's integrator);
   already recorded in EVIDENCE.md.
4. SPEC.md 7.2 and the header of RISKS.md point to `stage/G0/REPORT.md`, which does not exist
   (decision 0012); the thresholds are in SCOPE.md section 4.
5. SCOPE.md 6, stage/G1/STATUS.md, HANDOFF.md, STATUS.md and RISKS.md R1 describe the scalar
   field on the unmerged branch at 836ac86 without a card build; release core-v0.3 merged it
   with card and processor executables, and the release forms the tanh window increment
   without the cancellation that made the Markov-tanh A1 test fail on the 836ac86 executable
   (`athenak/src/scalar_field/scalar_field_noise.cpp:570-577`, read); the analysis helper's
   run E-20261115-172423-5234cce shows the release passing A1 at 3.3e-15 against a
   cancellation-free reference (9.77e-11 against the track's reference), so the A1 failure
   recorded in EVIDENCE.md now sits in `noise/ref/noise_ref.py` (note Fig. 5, ledger R8).
6. The locator key "VS" of SCOPE.md for arXiv:1308.4754 names the wrong authors: the source
   is Fujita, Kawasaki, Tada and Takesako.

## Draft of the decision paragraph (for the lead; not yet the track's text)

G0 of E-stoch-inf: the reproduction specification, the code-base assessment and the compute
estimate are complete and checked (C1, C3, C4, C8 first half); the working note v0, both
schematics and the paper-writing check exist (C5-C7, C10, C11, C15-C17); the measured card
throughput raises the cost of one 256^3 realisation to 0.57-0.88 card-hours, which leaves
the recommendation to continue unchanged. Missing before acceptance: the group's decision
(C8; ruling 0013: continue to G1 and G2), the knowledge-base claims of the key references
(C2), the verifier report (C18), and STATUS/HANDOFF rewritten for wave 2 (C20).
