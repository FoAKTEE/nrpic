# GATE_REVIEW.md: independent gate review of G2 of E-stoch-inf

Reviewer of batch 16 (decision 0019 item 3; decisions 0036 item 2, 0037 item 2), fresh context,
2026-11-25 04:28 to 05:05 UTC. I produced none of the work under review. No tag
`stage/E-stoch-inf/G2-pass-*` existed when I started (`git tag -l 'stage/E-stoch-inf/*'`: G0 and
G1 pass tags only). Worktree after `git merge --no-edit main`: 51a5c279 (main merged again before
this commit). Predictions of my own check were committed first, in daca69df (section 1).

**Read.** `CLAUDE.md`; `coord/CHARTER.md` to "Owners" and sheet 9.8 (G2: "the USR case is
reproduced; sensitivity to window-function parameters and resolution"); brief lines 674-686 (G2:
"the code paths used by the track pass their tests of section 10; three-way convergence in
particle number, mesh spacing, and gauge or boundary; constraints behave; a first minimal full-GR
kinetic run"); decisions 0010, 0013, 0016, 0019, 0026 item 3 (C4 does not apply before the
hand-over), 0028, 0029, 0030 item 2 (no rewording of the failed criterion; no gauge variant at G2),
0031, 0035, 0036 item 2, 0037 item 2; the package `stage/G2/` (STAGE_REPORT, CHECKLIST, EVIDENCE,
OPEN, VERIFIER, VERIFY_RESULTS, `verifier/`); `spec/scope/SCOPE.md` sections 4, 4b and 4c (the
criteria as fixed in 43dcc9cc, 2026-11-21 12:29 PST); `g2prod/JOURNAL.md` entries 1-4;
`stage/REVIEW-wave3.md` Part F (heading only); the outbox proposals of batch 15; note
`repro/note/manuscript/main.tex` Sec. IV (lines 214-288), abstract, ledger Table XVI
(`tables/ledger.tex` 268-297); `coord/INTERFACES/scalar_field_2.md` 3-4 and `scalar_field_3.md` 6.

**Opened as evidence** (named at each criterion): the manifests of the 13 card runs of `g2prod`
(status `completed`, exit 0, release card build `.work/build_gpu_v06/src/athena` sha256
ea473498500f..., which equals the file on disk now; one deck, sha256 ce4a60f2b1..., overrides as
the labels say) and of the analyses E-20261123-014858-8e72d4c, -020751-0baf597, -021730-a421438,
-024359-5dc3213, E-20261124-233223-51b52c0, E-20261125-033450-4c4a31c, -022309-d346f12,
-023427-6fb6400, -035757-340bd1e, E-20261124-213029-e937f69, E-20261121-154733-0d1fbda,
-203008-f104a3e, -202941-da16544 (all `completed`); the raw dumps and records of seven runs (my
own run, section 1); figures, each looked at with the Read tool: `fig_g2_halving`, `fig_g2_ua2`,
`fig_g2_resolution`, `fig_g2_records`, `fig_g2_control` (judge run E-20261123-024359-5dc3213),
`fig_g2_quarter` (E-20261125-033450-4c4a31c), `verifier/fig/fig_floor3.png`,
`verifier/fig/fig_constraints.png`, and the note's `fig_g2_halving`, `fig_ladder`, `fig_g2_mosaic`,
`fig_g2_resolution`, `fig_architecture`, `fig_timeline` (rendered from the committed PDFs).

**Ran.** (1) My own check, registered: run E-20261125-043414-daca69d FAILED (exit 1, a guard of my
script: at dump 17, after USR, e_1 fell below the level while e_{1/2} did not, math domain
error; its printed numbers for dumps 0-16 equal those of the rerun; the manifest names
`figstyle.py` but not the script, sha256 9499fd23e07c... then); run **E-20261125-044244-6dbd239**
(the guard fixed, script `scratch/E-stoch-inf/gate_review_G2/review_g2.py` sha256 5c4c22244f0f...
as input, 2 cores, 295 s, exit 0). (2) `harness/bin/nrpic-stage verify E-stoch-inf G2
--no-checksums` on ea4ccadb (section 4; log and results kept in
`scratch/E-stoch-inf/gate_review_G2/verify/`; the stage copies were restored to their committed
state, so this review changes no package file but this one). (3) `sha256sum` of the superseded
level-2 executable. No card-hours. No checksum pass over all run directories: I hashed the 29
files my check read (all match) and doubted no other file.

## 0. Verdict

**Recommendation: PASS WITH RESERVATIONS, with criterion U-A4'(a) of SCOPE 4c (CHECKLIST C3 and
C7) recorded in the gate record as FAILED as written.** The question set by rulings 0030 item 2
and 0036 item 2 is whether the gate can be passed with that failure stated. My answer is yes, for
the reasons of section 3: the failure is real and reproduced by a third independent reader to five
digits (3.92453); the one pre-registered alternative cause (a fourth-order term) was tested with a
run that could have confirmed it and was refuted; the cause the package names after the data (the
floor estimator of 4c) is now supported by two independent readers, and I can show from my own
numbers why the estimator is biased exactly where it fails; and every other pre-registered USR
criterion passes, most by two decades. The gate record must not say "the USR case is reproduced"
without the qualifier: as SCOPE 4c defines that phrase, it is not met.

The harness verify FAILs on two checks, neither a defect of the G2 evidence: `runs` (seven
ablation runs of the reproduction whose executable core replaced in place, plus two runs in
progress at the time, one of them mine) and `sync` (main moved during my review). Every rerun,
regeneration and comparison check passes.

## 1. My own check: predictions and outcomes

Predictions as committed in daca69df, before either run. Outcomes from run
E-20261125-044244-6dbd239 (`review_g2.json`, sha256 5590f5686d14...; figure
`fig_gate_review_g2.png`, looked at: top left the judged 4c factors inside the band except M at
cN 6.52, the three-amplitude factors all on 4; top right f and sigma coincide where the odd part
is all per-run part and separate during cN 4-6.5; bottom left rms(D2)/rms(D1) = 1 and corr =
-4/17 from cN 0.5 to 7, departing after USR; bottom right the control 5 decades above the proper
odd part over the entry).

| # | Prediction | Mine (E-20261125-044244-6dbd239) | Outcome |
|---|---|---|---|
| P1 | M judged at dumps 0, 4-13; dump 13 factor 3.9245 +- 0.002, the only one outside 4 +- 0.05 | judged 0, 4-13; dump 13 (cN 6.5248) **3.92453**; the other ten 3.9948-4.0126 | holds: U-A4'(a) FAILS as written |
| P1h | H judged at 0, 5-12, factors 3.991-4.043; dump 13 not judged | judged 0, 5-12; 3.99156-4.04240; dump 13 e_{1/2} 1.319e-14 < 3 f = 1.81e-14 | holds |
| P2 | M at dump 13: o = 1.0881e-11, 5.4407e-12, 2.7211e-12; e = 1.0418e-12, 2.6991e-13, 9.751e-14; f = 5.05e-14 | o = 1.08811e-11, 5.44073e-12, 2.72113e-12; e = 1.04178e-12, 2.69906e-13, 9.75109e-14; f = 5.0486e-14 (with the 1/3 of 4c) | holds (all within 1e-4 relative) |
| P3 | rms(D2)/rms(D1) 0.99-1.01 and corr -0.25 to -0.22 at dumps 1-13; sigma(M, 13) 7.30e-14; factor 3.9988 +- 0.001; sigma-judged factors within 4 +- 0.005 | ratio 0.9970-1.0013 (M), 0.9973-1.0011 (H); corr -0.2450 to -0.2338 (M), -0.2447 to -0.2341 (H); sigma 7.297e-14 (from D2: 7.275e-14); factor **3.99924**; largest deviation 4.46e-3 (H), 7.6e-4 (M) | holds |
| P4 | quarter pair, M at dump 13: 4.1275 +- 0.003, not judged | 4.12747; e_{1/4} = 9.75e-14 < 3 f_{hq} = 2.24e-13: not judged | holds |
| P5 | control ratio of maxima over cN <= ln 32: 2.38e5 single, 1.19e5 cross | 2.3816e5, 1.1908e5 (dumps 0-6; dump 7 at cN 3.546 excluded) | holds |
| P6 | record maxima: proper H' 1.1e-12 to 3.1e-12, M 8.0e-3 to 2.53e-2; 256^3 M equal at s = 1, 1/2, 1/4 within 1 percent; control 1.28e-7, 0.50 | H' 1.191e-12 (s = 1/4) to 3.026e-12 (320^3); M 8.086e-3 (320^3) to 2.5213e-2 (seed B); seed A 2.5193e-2, 2.5123e-2, 2.5128e-2; control 1.2814e-7, 0.5024 | holds |
| P7 | 21 dumps, equal recorded times, last at tlim, same MeshBlock header | 21 dumps; largest abs dt 0.0; last dump at tlim exactly; headers identical | holds |
| P8 | integrity of the files read | 29 of 29 equal their entries in each run's sha256sums.txt (dump 13 of six runs, control dump 6, both records of eleven runs) | holds |

All predictions held. My values for the three-amplitude reading differ from the verifier's in the
fourth digit (factor at dump 13: 3.99924 here, 3.9988 in VERIFIER.md 3.3 and ledger row 282;
largest M deviation 7.6e-4 here, 1.2e-3 there): I remove rms(D1)/sqrt 17, the verifier a level
combined from D1 and D2 (`verifier/scripts/floor3.py`, read after my run). No verdict depends on it.

Readings after the data, from the same JSON [JUDGEMENT, not predicted]:
- Where the odd part is entirely per-run part (dumps 1-7, cN 0.5-3.5) the 4c floor f equals
  sigma to 1 percent (f/sigma 0.99-1.00): the two estimators agree when the odd part has no
  s-dependent piece to cancel. At dumps 8-13, where the odd part is 10 to 1000 times the even part,
  f/sigma scatters 0.69-1.54. If the odd field is s A + s^3 C + F, then o_s^2 = s^2 a^2 +
  2 s^4 <A C> + s^6 c^2 + f_true^2, and the 4c combination gives 4 o_{1/2}^2 - o_1^2 =
  3 f_true^2 - (3/2) <A C> - (15/16) c^2. With f_true = sigma, the cross term needed at dump 13 is
  <A C>/a^2 = 2 (sigma^2 - f^2)/o_1^2 = 2 (5.3245e-27 - 2.5488e-27)/1.18399e-22 = 4.7e-5, the size
  of the third-order common mode the package measured in R^NR (4.1e-5, g2prod 2.3). So the bias
  of the 4c floor at the failing dump is of the size a known third-order term produces.
- After USR (dumps 14-20, cN 7.0-10) the per-run model is not supported: rms(D2)/rms(D1)
  0.70-1.15 and corr -0.33 to +0.17. No dump there is judged by 4c (e_{1/2} < 3 f), and the
  three-amplitude reading should be cited only for dumps 1-13.

## 2. Criteria, one by one

| # | Criterion | Evidence I opened | Verdict |
|---|---|---|---|
| C1 | Code paths used by the track pass their tests of section 10 (rows: SR and USR cases, power spectrum and freezing; reproducible random numbers) | P256v6 manifest (release card build, exe sha256 equal to the file now); g2prod 2.1: records identical to the tested-branch run, A2 1.20776e-4; U-A2' per mode and U-A3 on both seeds (VERIFIER.md table, recomputed by the verifier with its own reader, Philox and MS reference; `fig_g2_ua2`: odd-part D_n flat at 4e-5 below \|n\| 25, 4.5e-3 at the cut, bar 2e-2); restart byte-exact R0 (E-20261121-202941-da16544 completed); my P7, P8 | PASS |
| C2 | Three-way convergence in particle number, mesh spacing, gauge or boundary | Particle number: no particles before the hand-over (NA). Gauge: not required at G2 by ruling 0030 item 2 (NA by ruling). Mesh: U-R on 256^3 and 320^3 (`fig_g2_resolution`: power difference below both bars; per-shell factor 1.0 below \|n\| ~ 22, 2.5-3.1 above \|n\| 36, between (5/4)^4 and (5/4)^6); U-R (i) 2.10 against 2.0; SR 32-256 spectral convergence (G1, note Fig. 7) to a floor of about 1.5e-7 whose test FL128h/FL256h is still queued | PASS WITH RESERVATION: the USR mesh leg rests on two resolutions and passes its first clause by 5 percent on a part that does not depend on the spacing |
| C3 | Constraints behave | U-A4'(a) FAILS as written at one dump of M (my P1: 3.92453); (b) reported; (c) PASS (my P6); (d) PASS (my P5, `fig_g2_control`); `fig_g2_records` (records 300 times below their bars) | FAIL (as written; on record by rulings 0030, 0036) |
| C4 | A first minimal full-GR kinetic run | Decision 0026 item 3: does not apply before the hand-over | NA by ruling |
| C5 | Verification report | STAGE_REPORT, EVIDENCE, OPEN, CHECKLIST, VERIFIER.md present and read; finding F2 (stale text in STAGE_REPORT) | PASS WITH RESERVATION (text to update) |
| C6 | Reproducibility package | 13 card manifests complete with inputs and checksums; my rerun of nrpic-stage verify: rerun 12/12, compare 24/24, regenerate 24/24; `runs` FAIL on the seven ablation runs (finding F5) | PASS WITH RESERVATION |
| C7 | The USR case is reproduced | SCOPE 4c as written: every clause PASS but U-A4'(a) (VERIFIER.md section 2, my section 1) | FAIL (as written; on record) |
| C8 | Sensitivity to window-function parameters and resolution | U-W: manifests of the scan and its rerun; numbers recomputed by the verifier (1.870e-4, 9.13e-3 against 1e-3, 2e-2); the scan ran on the scouting build at 128^3, which 4c accepts. Resolution: as C2 | PASS WITH RESERVATION (window on a scouting build; resolution as C2) |
| C9 | Ruling 0013 (continue to G1 and G2; scope of G3 decided at G2) | coord/GATES.md rows of G0 and G1 | PASS |
| C10 | Schematic: verification ladder | `fig_ladder` looked at; finding F3 (box 1 lists the quarter amplitude among the items fixed before the runs) | PASS WITH RESERVATION (one box to correct) |
| C11 | Convergence figures | `fig_g2_resolution` (mesh) looked at; particle and gauge NA as in C2 | PASS |
| C12 | Constraint norms against time | `fig_g2_records` looked at (all release runs, both records, bars) | PASS |
| C13 | Multi-scale slice mosaic with zoom boxes | `fig_g2_mosaic` looked at (box, quarter, sixteen cells, zoom squares) | PASS |
| C14 | Package documents of decision 0012 | all present; scoping text SCOPE 4c | PASS |
| C15 | Data figures from registered runs, one script each, looked at | verify `fig-script`, `rerun`, `compare`, `regenerate` PASS; note figures name their source runs in ledger Table XVI | PASS |
| C16 | Schematics: architecture and gate timeline | `fig_architecture`, `fig_timeline` looked at; G2 state shown ("eight of nine criteria met; one failure on record") | PASS |
| C17 | Working note with /paper-writing, checker passed | `repro/note/manuscript/main.pdf` (32 pages, committed after the last .tex change: f9b73b02 after 340bd1e4); Sec. IV and the abstract state the failure and label the three-amplitude reading as after the data; ledger rows carry run ids. I did not rerun the checker. Finding F1 (equation of the floor misprinted) | PASS WITH RESERVATION (one equation to correct) |
| C18 | Fresh verifier, VERIFIER.md | read in full; its constraint numbers reproduced by my third reader (section 1); predictions committed before its runs (3804754c before E-20261125-022126) | PASS |
| C19 | Null results and failed runs on record | STAGE_REPORT lists 35 failed or stopped runs; failed predictions in g2prod 2.1-2.3 and 4.1 (384^3 memory band, U320 band, U-A2' at s = 1/2, U-A4'(a), Q-a, Q-b band missed by 0.03e-6) and in the note; my own failed run is on record too | PASS |
| C20 | STATUS, JOURNAL, HANDOFF current | STATUS.md (37 lines) and HANDOFF.md of batch 15 describe the G2 state and the queued q0037/q0038 | PASS |

Timing of predictions against runs, checked from git and the manifests: SCOPE 4c and g2prod entry
1 in 43dcc9cc (12:29:24 PST, 2026-11-21) before the first production submission (12:29:29); entry 3
(Q-a..Q-c) in 41026ee1 (2026-11-22 18:49 PST) before the quarter pair (2026-11-23 23:00 UTC); the
verifier's predictions in 3804754c before its first run. Entry 4.0 was written after the verifier's
numbers existed and says so ("a reconciliation rather than a blind test").

## 3. Can the gate pass with U-A4'(a) failed?

For passing with the failure stated:
1. The failure is not in doubt and is not hidden: three readers (the package, the fresh verifier,
   this review) give 3.9245 at cN 6.52, and the package, the note's abstract and Sec. IV C, the
   ledger and the timeline say "fails" in those words.
2. A cause that would condemn the evolution (a higher order in s) was named before a run that could
   show it (g2prod entry 3, Q-a) and was refuted by that run (4.1275, the other side of 4).
3. The reading after the data is now reproduced by a second independent reader, not only by the
   verifier (OPEN item 5 is closed by my run): the even parts of H and M are second order in s
   to a few parts in 1e3 at every dump where they stand above the per-run level, and the 4c
   estimator agrees with that level wherever it is well conditioned (dumps 1-7) and departs from
   it only where a known third-order part of the odd part must bias it (section 1).
4. The rest of the USR case passes as written on the release build: per-mode agreement 1.09e-4
   against 2e-2 on two seeds, freezing within 1 percent, background to 1.6e-9 in N, records 300
   times below their bars, the control 1.2e5 times above the proper run, the window bars by a
   factor 2 to 5.

Against, and why it does not decide: the criterion was fixed in advance, and the explanation came
after the data. That is what rulings 0030 and 0036 already provide for: the criterion stays
FAILED. Passing the gate does not reword it; it records that the capability G2 certifies (the
stochastic lattice of the USR case on the release build, with constraints that behave and a
spectrum that converges) is shown, and that one pre-registered scaling clause failed for a reason
of its estimator. If the group holds that a failed pre-registered clause must block a gate
whatever its cause, the verdict is FAIL; nothing in the evidence argues for that beyond the rule
itself.

## 4. Harness verify (my rerun)

`nrpic-stage verify E-stoch-inf G2 --no-checksums` on ea4ccadb (2026-11-25T04:36Z): FAIL on
`sync` (main gained 8137dc84 during the review; merged before this commit) and `runs` (9 of 291:
the seven ablation runs E-20261123-035724-b661081, -152119-38957ba, -153146-d965002,
-153347-18e7c21, -164235-49b0945, -183822-4abbcae, -192948-348e2e5, whose input
`scratch/core/exe/core_noise-level2/athena_gpu` now hashes d7069a4e09330f7a against the recorded
468109496c82...; and two runs not finished at that moment, E-20261125-041742-71d74fb (FL128h,
job 5245) and my E-20261125-043414-daca69d). PASS: clean, export, size, note, package, note-pdf,
style, fig-script, min-figs (3 schematics, 9 data figures), status, rerun (12 of 12), compare (24
regenerated files within tolerance), regenerate (24 of 24). WARN: run-notes (30 older manifests
read with defaults). This matches the package's own result of 04:07Z.

## 5. Findings (corrections for the lead; none changes a verdict)

- F1. Note `main.tex` line 258, eq. (floor): f^2 = 4 o(1/2)^2 - o(1)^2 lacks the factor 1/3 and the
  max(0, .) of SCOPE 4c; the package, the verifier and my check all use (4 o_{1/2}^2 - o_1^2)/3
  (my P2: 5.0486e-14 only with the 1/3). g2prod 4.2 line 275 writes "f = 4 o_{1/2}^2 - o_1^2"
  the same loose way.
- F2. STAGE_REPORT.md: the section "Decision requested from the group" (line 190) is the text of
  batch 10a ("no G2 verifier (C18); note G2 sections and figures C10-C13 missing; C2 gauge leg
  open"), all since done or ruled; the Verdict line names a tag `G2-fail-20261125` "created by
  the orchestrator after review" that does not exist; the Figures table lists the G1 note's
  figures "to be confirmed by the session", while the G2 figures live in `repro/note/` (the
  harness reads `note/` only).
- F3. `fig_ladder`, box "1 Fixed before the runs": "amplitudes +-1, +-1/2, +-1/4". The quarter
  amplitude was added after the halving outcome (g2prod entry 3, 41026ee1, written after entry
  2.3); its own predictions were fixed before its runs, but it was not part of SCOPE 4c. Move it
  to row 2 or mark it.
- F4. Ledger rows 282-283 quote the verifier's three-amplitude factor (3.9988, 1.2e-3); mine with
  the level from D1 alone gives 3.99924 and 7.6e-4. Name the estimator in the row.
- F5. The seven ablation runs (reproduction, decision 0031) point to an executable that core
  replaced in place; their provenance is owed by core (outbox 20261125T040618Z). Not G2 runs.
- F6. The record of U256qp holds 1902 rows against 1703 for the unchained runs: the duplicated
  rows of a continued chain (core's open restart defect). Maxima and the judged numbers are not
  affected.
- F7. My own run E-20261125-043414-daca69d failed on a guard of my script and its manifest lacks
  the script as an input; on record above.

## 6. Reservations to carry to G3

1. U-A4'(a) FAILED as written (C3, C7); the three-amplitude reading after the data holds for dumps
   1-13 only (not after USR). Any G3 constraint-scaling criterion is fixed in advance with three
   amplitudes and its model test (ratio and correlation of D1, D2), as the track proposes (outbox
   20261125T040230Z), and says over which e-folds it is judged.
2. Second-order scaling of the constraints is shown only during the entry and USR (cN about 2 to
   6.5); before, the odd parts are per-run part; after USR the even part does not scale with s.
3. Mesh convergence of the USR case rests on two resolutions, U-R (i) by 5 percent on a
   third-order part independent of the spacing: G3 judges the discretisation part (Richardson in
   s^2) or adds a resolution.
4. No gauge or boundary leg of convergence (ruling 0030 item 2: a G3 item); no particle leg until
   the hand-over.
5. The window scan ran on the scouting build at 128^3.
6. The SR convergence floor (risk R28): FL128h is on the cards (q0037, job 5245), FL256h waits
   (q0038).
7. What the per-run part F_s is: deterministic (release equals scouting bit for bit), not shown
   to be rounding.
8. Carried from G1 and still open: the absolute constraint levels 40-100 times below the paper's
   statements (R18, TO VERIFY); the one-point spread 3.5-4 times narrower than the published
   figures (R29), a reproduction question, not a G2 one.
9. Provenance of the superseded level-2 executable (F5), before the ablation enters a G3 claim.

Pending runs named in this review: q0037 FL128h (submitted, job 5245, run E-20261125-041742-71d74fb)
and q0038 FL256h (waiting); neither is a G2 criterion.
