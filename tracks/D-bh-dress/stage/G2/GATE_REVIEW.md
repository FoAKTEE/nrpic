# GATE_REVIEW.md: independent gate review of G2 of D-bh-dress

Gate reviewer of batch 27 (decision 0019 item 3), fresh context, 2026-11-26 03:44-04:30 PST.
I produced none of the work under review. No tag `stage/D-bh-dress/G2-pass-*` existed when I
started (`git tag -l`: `G0-pass-20261120`, `G1-pass-20261121` only). Worktree after `git merge
--no-edit main`: b1fefc58d (it holds the verifier's report, commits d8cec93fe..eeb228fd6).

**Read.** `CLAUDE.md`; `coord/CHARTER.md` to "Owners", section 9.2 and the Track D sheet 9.7 (G2:
"in the vacuum-bubble case the drift of the horizon mass does not exceed the noise floor; with
matter filled in, the mass growth agrees with the integrated particle flux through the horizon");
brief lines 674-686 (G2: "the code paths used by the track pass their tests of section 10;
three-way convergence in particle number, mesh spacing, and gauge or boundary; constraints behave;
a first minimal full-GR kinetic run"; products "verification report; reproducibility package");
decisions 0013, 0016, 0019, 0039 item 4, 0041 item 4, 0044 item 1; the package `stage/G2/`
(STAGE_REPORT, CHECKLIST, EVIDENCE, OPEN, LADDER, REVIEW, VERIFIER, VERIFY_RESULTS, rerun_g2.py,
the verifier's journal and commit order); `g2long/JOURNAL.md` entry 1 (criteria N and G as fixed
before the runs, committed 53afc1a) and the outcome entries 21 and 26-27 (grep); `flux_tools/JOURNAL.md`
entry 7 (criterion (iii), D1-D4); note `main.tex` section V and VI and ledger part 11
(`tables/ledger.tex` lines 188-210); core's G2 checklist on main (rows 1 and 2 that D depends on);
`coord/GATES.md` (G1 reservations; E's G2 precedent without a gauge leg).

**Opened as evidence** (named at each criterion): the manifests of the analyses judge_long
D-20261123-020550-f9a3482 and -131138-0b8ffc5, judge_conv D-20261125-122227-3eb563a, of the card runs
ES-FL, FL16, FNQ, ES-F (status completed, exit 0, release tags core-v0.6 / core-v0.5, card-hours
2.60 / 3.66 / 1.90 / 0.81); the raw finder summaries and removal records of eleven card runs (through
my own reader, below); conv3.json of D-20261126-055249-505b079; `nrpic-run budget` (G2: 31.07 of
40 card-hours used). Figures looked at with the Read tool (21): judge_long.png (-131138-0b8ffc5),
judge_conv.png (-122227-3eb563a), fp_analyse.png (-172508-c847ee4), esf_criteria.png of ES-FL
(-020614-7ba5874), FNQ (-054616-a13a888) and FL16 (-055158-30ae09c), conv3.png (-055249-505b079),
constraints_long.png (-021027-e3af9b8), xc_plane.png (-055159-6c40115), region_norms.png
(-054736-10c837a), boundary_gauge.png (-131657-89cd963), slice_mosaic_esfl_t500.png
(-134644-2389227), schem_ladder.png (-175505-a1053fa), hz_check.png (-055208-4e0fd0e); note
figures fig_g2conv.png, schem_architecture.png, schem_timeline.png; the verifier's v6_tracers.png
(D-20261126-062436-72c04d3); my own review_checks.png.

**Ran.** (1) `harness/bin/nrpic-stage verify D-bh-dress G2` on b1fefc58d: PASS, 0 failed checks
(section 3). (2) My own check, registered: run **D-20261126-114851-2287593** (`nrpic-run`, one core,
exit 0; script `scratch/D-bh-dress/tmp/gate_review_G2/review_checks.py`, which imports nothing of
the track or of the verifier, only numpy and a copy of `harness/style/figstyle.py`; predictions
R1-R9 committed first in 228759348, section 0). (3) The manuscript checker of `/paper-writing`
(`check_manuscript.py --compile`, the forbid list of note/README.md) on an export of the committed
note in `scratch/D-bh-dress/tmp/gate_review_G2/note_copy/`. This review changes no package file
but this one: the stage copies of `VERIFY_RESULTS.{md,json}` were restored to their committed state
(both my verify and the uncommitted full-checksum verify of a5bd88c are kept in
`scratch/D-bh-dress/tmp/gate_review_G2/`).

## 0. Predictions for the reviewer's own check run (committed in 228759348 before it ran) and outcomes

Script `scratch/D-bh-dress/tmp/gate_review_G2/review_checks.py` reads the raw finder summaries
(`*.horizon_summary_0.txt`, column 3; a time that repeats after a restart keeps its last line) and
the removal records (`*.removed.bin`, docs/FORMATS.md line 127) of the registered card runs, and
nothing else.

| # | Quantity (definition) | Claim in the package | Predicted (refuted if outside) | Outcome (D-20261126-114851-2287593) |
|---|---|---|---|---|
| R1 | N at M/8: max over 100 <= t <= 500 M of /D_ES1L - D_V1L/, D_X(t) = M_X(t) - M_X(100) | 2.28e-4 | [2.26e-4, 2.30e-4] | 2.283e-4 at 256.5 M, 800 samples, none NaN: HELD |
| R2 | F_V(500) = max /D_V1L/ on 100-500 M; bound 2 F_V | 1.253e-4 (2.51e-4) | F_V in [1.24e-4, 1.27e-4]; R1 < 2 F_V | 1.2528e-4, bound 2.506e-4: HELD |
| R3 | N at M/16 on 100-300 M | 1.99e-4 | [1.97e-4, 2.01e-4]; below 2 F_V16(300) | 1.986e-4 at 243 M, bound 2.685e-4: HELD |
| R4 | N at M/4 on 100-300 M | 4.57e-3, fails | [4.5e-3, 4.65e-3]; above 2 F_V4 | 4.572e-3 at 299 M, bound 3.952e-3: HELD (N fails at M/4) |
| R5 | /dM_FL16 - dM_ESFL/, dM = M(t) - M(20 M), at 100, 200, 299 M | 4.4e-4, 1.2e-4, 8.6e-5 | each within 5 % of the claim; all below 3e-3 | 4.40e-4, 1.16e-4, 8.65e-5: HELD. Not predicted, read from the same run: envelope over 20-299 M 9.97e-4, mean over 250-299 M +5.78e-4 |
| R6 | /M_4N - M_N/ <= /M_N - M_N/4/ at 100, 200, 300, 399.5 M | 4 of 4 | 4 of 4 | 4 of 4: HELD; at 200 M only just (3.57e-4 against 3.94e-4) |
| R7 | ES-FL removals: last reason 3, first reason 2 | 218.9, 224.0 M | [218, 220]; [219, 226]; no reason 1 or 4 | 218.875 M, 223.969 M; reasons 2 (84510 records) and 3 (63386) only: HELD |
| R8 | FK removals: reasons present to 400 M | reason 3 only | reason 3 only | 154190 records, all reason 3 (six steps back in time: restart overlaps, removed by the track's readers): HELD |
| R9 | ES-FL horizon mass at 499.5 M | 1.6090 | [1.6085, 1.6095] | 1.609002: HELD |

All nine held. The figure (review_checks.png, looked at) shows (a) the M/8 and M/16 null tests
inside the band and the M/4 one rising monotonically to 4.6e-3; (b) the M/16 - M/8 growth difference
rising from about zero to a plateau near +6e-4 after 150 M with sample-to-sample scatter of about
4e-4, the three named samples at 200 and 299 M lying at low points of that scatter; (c) the N - N/4
differences scattering to +-3e-3, the 4N - N ones to about +-1e-3. The verifier's 84496 reason-2
removals of ES-FL count dust only; the 14 more records in R7 are tracers (an interactive split by tag,
not registered, that supports no verdict here).

## 1. Recommendation

**PASS WITH RESERVATIONS.** Both track criteria hold as they were fixed before the runs (g2long
entry 1, 53afc1a): criterion N at M/8 (2.283e-4 against 2.506e-4) and M/16 (1.986e-4 against
2.685e-4), reproduced by the verifier and by my own reader from the raw finder output; criterion G
((iii) every 10 M bin within one per cent of the exact LTB mass, D2 at every sample) at N/4, N, 4N,
M/8 and M/16, reproduced by the verifier with an LTB reference of its own to three digits. Particle
number is a clean three-member leg (differences scale as N^-1/2 noise, window ratios 1.9-3.1 against
2). The mesh leg has two members inside the convergent regime and no order, as decisions 0039 item 4
and 0041 item 4 allow; the third axis is the boundary (three face distances), not the gauge. A
fresh verifier (C17) ran with predictions committed first and decided the lead's one open point.
The clean-checkout verify passes with no failed check, and a full checksum pass read all 701 GB of
outputs. M/4 fails the null test (on record, ruled). The reservations (section 5) are about the
weight of the mesh leg, a missing gauge leg, the finder floor and excision rule that G3 must design
around, and texts of the package that predate the last runs or the verifier; none rests on
missing evidence.

## 2. Criterion by criterion

| # | Criterion | Evidence I opened, and what it shows | Verdict |
|---|---|---|---|
| C1 | Code paths pass their tests of section 10 | D's own rows (LADDER.md): null test N holds at M/8 and M/16 (my R1-R3; judge_long.png panel c: both differences inside the dashed band after 100 M); converged-finder re-search FP (fp_analyse.png c: tight-finder differences 0-7.3e-5, no trend); growth G at five members (C8). Rows D depends on: core's G2 checklist on main passes row 1 (geodesics, 104/104) and row 2 (Oppenheimer-Snyder, 13/13) on the wave-1 source and carries them to core-v0.6 by byte regression (core's [JUDGEMENT]); core's G2 itself is FAIL on other rows. M/4 fails N (my R4, judge_conv.png c), ruled outside the convergent regime (0039 item 4). LADDER.md is stale: its rows for M/4, ES-FL4, ES-FLK, FN4, FNQ, FL16 still read PENDING or REGISTERED (state 2026-11-24 09:30) | PASS WITH RESERVATION (LADDER.md to be brought to the final state; core G2 unsigned) |
| C2 | Three-way convergence: particles, mesh, gauge or boundary | **Particles**: FNQ, FK, FN4 (N/4, N, 4N) read whole; ordering 4 of 4 (my R6; marginal at 200 M), window-rms ratios 3.12, 2.51, 2.51, 1.87 (conv3.json; verifier C2a); conv3.png a and my panel c show the noise halving with each factor four. **Mesh**: M/8 and M/16 inside the regime, no order claimed (0039 item 4, 0041 item 4); quoted single samples 4.4e-4, 1.2e-4, 8.6e-5 reproduced (R5), but the difference has a systematic part: mean +5.78e-4 over 250-299 M, envelope 9.97e-4 (R5; verifier 4.3; conv3.png b, c). Both well inside the 3e-3 tolerance of D2. M/4 drawn and labelled outside the regime. **Boundary**: boundary_gauge.png a: faces +-384 against +-768 M agree to 1e-15 until 170 M and to 5e-8 at 186 M in vacuum; +-192 M departs from about 90 M and reaches 1e-4 by 140-200 M. **Gauge**: none; boundary_gauge.png b shows why (the relaxed lapse drifts the vacuum horizon mass to 1.5e-3 by 200 M). The brief's "gauge or boundary" is met by the boundary; E's G2 passed with the same gap | PASS WITH RESERVATION (two mesh members, no order; the C2 row and the note quote samples instead of the envelope; boundary leg in vacuum only) |
| C3 | Constraints behave | constraints_long.png: volume norms bounded, but dominated by the puncture interior (V-1L about 0.3 throughout) and stepping down in ES-FL, presumably as the region the norm excludes grows [JUDGEMENT]: not informative on their own. xc_plane.png and region_norms.png: exterior norms bounded to 400-500 M with no exponential growth; FNQ/FN4 shell ratios scatter about 4 on [1.2 r_AH, 30 M] (sqrt(16) for shot noise), M/16 over M/8 on [1.2 r_AH, 6 M] 2.11 at 100 M and 1.00 at 300 M: the residual near the hole is particle sampling noise and does not fall with the mesh. The innermost shell grows slowly (FN4 about 1.5e-4 to 6e-4 over 400 M; ES-FL plane norm about 5e-4 to 2e-3 over 450 M). XC2 and R1 failures on record | PASS WITH RESERVATION (slow growth near the hole; no mesh convergence of the residual with matter) |
| C4 | A first minimal full-GR kinetic run | ES-FL D-20261121-203150-15f2bad: manifest completed, exit 0, core-v0.6, 2.60 card-hours, 850724 particles, finder to 500 M (my R9: 1.609002 at 499.5 M); ES-F D-20261121-144631-aa7ce9b (completed, core-v0.5, 200 M) before it; slice_mosaic shows the hole and the dust at four zooms | PASS |
| C5 | Verification report | STAGE_REPORT.md, EVIDENCE.md, OPEN.md, CHECKLIST.md, LADDER.md present. The committed STAGE_REPORT was generated before VERIFIER.md existed: its verdict reads FAIL (C17 open, no VERIFIER.md) and its closing section still says "Not ready for review (lead of batch 20)" | PASS WITH RESERVATION (regenerate the report once C17 is set) |
| C6 | Reproducibility package | `rerun_g2.py` lists every cited run with its command; tested rerun D-20261125-160651-29a730e byte-identical. My stage verify: rerun 14 of 14 scripts in the clean export, 40 regenerated files equal within tolerance, 28 committed figures regenerated. Full checksum pass (`--full`, started by the verifier on a5bd88c, ended 07:05Z): 15718 files, 701.22 GB read, PASS; my pass on b1fefc5 took 15734 from that cache and hashed 34 new | PASS |
| C7 | Vacuum bubble: drift not above the noise floor | Criterion N (fixed 53afc1a) holds at M/8 and M/16 (R1-R3, verifier N1-N2, judge_long.png b-c). The floor is the production finder's stopping rule: with the converged finder the bubble-minus-vacuum difference is 0 to 7.3e-5 at M/8 to 500 M and 2-4e-5 at M/16 (fp_analyse.png c), no trend. Failed searches rechecked by signature (hz_check.png: none after 20 M in FNQ or FL16; 13 summaries in batch 20), all numbers "made without the diagnostics" as 0041 item 4 asks. M/4 fails its pass condition (4.57e-3 against 3.95e-3) but does not meet the refutation clause (its own control drifts by -2.0e-3; verifier N3); "a factor 20" in the package is relative to M/8 | PASS (M/4 failure on record and ruled) |
| C8 | With matter, mass growth agrees with the integrated flux through the horizon | esf_criteria.png of ES-FL, FNQ, FL16: (iii) bin medians inside +-1 per cent (largest 0.62, 0.29, 0.485 per cent), D2 band held, M_AH - M_ctrl lying on F_rem. Verifier G1-G2 reproduce every maximum, bin count and sample count with its own LTB growth law. The step of (iii) at tau_rem about 285 M is the end of horizon excision at 4 x initial_radius: my R7 (last reason-3 removal 218.875 M, first reason-2 223.969 M) and R8 (FK, excision kept: reason 3 only), and FK's medians 0.16-0.24 per cent. Because of that end ES-FL's closure is +9.4e-3 at 500 M (verifier G5; FK +2.2e-3 at 399.5 M). FF4's "480 D2 samples with its own control" holds only with V-1L4 held at its last value after 299 M (280 within the control; verifier 4.2). D3 fails at N/4 after 221.6 M and at M/4 (on record, not part of G). The early removals before the exact crossing are decided by the verifier (shells run ahead of exact LTB by about 0.2 per cent of proper time at R0 = 28 M, converging with mesh and N: v6_tracers.png, looked at; clock right to 6e-7), but OPEN.md, CHECKLIST and the note still call the cause unknown | PASS WITH RESERVATION (FF4 ledger row; early-removal cause to be recorded; excision end) |
| C9 | Schematic: verification ladder | schem_ladder.png (D-20261124-175505-a1053fa): paperfig style, legible, but stale: particle number "queued", growth "holds, 1 mesh", M/4 "queued" | PASS WITH RESERVATION (redraw at the final state) |
| C10 | Convergence figures (particles, mesh, gauge) | conv3.png and the note's fig_g2conv (particles, mesh with and without controls, M/4 labelled); judge_conv.png (null test at three meshes, finder offset against h); fp_analyse.png d; boundary_gauge.png (boundary; gauge panel shows the failure that keeps the gauge axis out) | PASS |
| C11 | Constraint norms against time | constraints_long.png, xc_plane.png, region_norms.png (C3) | PASS |
| C12 | Slice mosaic with zoom boxes | slice_mosaic_esfl_t500.png: lapse and particle energy at four zoom levels (axis ticks to +-192, +-48, +-12, +-3 M) with zoom boxes and the horizon circle | PASS |
| C13 | Package documents of decision 0012 | all present, scope `scope/SCOPE.md`, REVIEW.md points to REVIEW-wave3 sections 13-24; CHECKLIST C17 still OPEN although VERIFIER.md is committed | PASS WITH RESERVATION (formal: C17, report) |
| C14 | Data figures from registered outputs, one script each, looked at | stage verify: fig-script PASS (14 figures, each with its script), regenerate PASS (28 files), compare PASS; fig_g2conv.png looked at by me; the STAGE_REPORT figure table still says "to be confirmed by the session" in its column "Looked at" (the CHECKLIST states the lead did, pages 11-14) | PASS |
| C15 | Schematics: architecture and timeline | schem_architecture.png (exists / provided by core / new for Track D; the excision guard marked as core's), schem_timeline.png ("G2 package assembled, waiting for its verifier and review"): current, legible | PASS |
| C16 | Working note with /paper-writing; checker with --compile | My rerun on the committed source: 0 undefined references, 0 undefined citations, 0 overfull boxes, 24 pages; candidates only in scripts and the ledger. Every row of ledger part 11 names a run id; section V's numbers map onto it. But: line 244 says the mesh members agree "to a few parts in a hundred thousand once each mesh's vacuum control is subtracted", which holds at the 200 and 300 M samples (2.9e-5, 1.3e-5) and is contradicted by its own Fig. g2conv(c) (about +6e-4 after 150 M); line 236 "below 7x10^-5 at both meshes" against 7.3e-5 at M/8 (fp_analyse.png c, 400 M); line 254 calls the early removals unexplained; section VI and the summary keep pre-G2 statements ("Long runs are on the cards", "The growth against the flux has one resolution and ends where the boundary signal arrives") | PASS WITH RESERVATION (four text corrections; the stale section VI repeats G1 reservation 3) |
| C17 | Fresh verifier; Supplemental numbers recomputed | VERIFIER.md read in full; its predictions committed (d8cec93fe, 22:13) before its first run (D-20261126-061541-31e3b4e); own readers and LTB reference, tested on closed forms; its own failed predictions and a failed run (D-20261126-061734-6b49970) on record. It reproduces every number it checked and decides the open point. Not recomputed by anyone independent: the converged-finder null difference 6.53e-5 (ledger), the plane-norm ratios XN, XQ and L5 | PASS (CHECKLIST to be updated by the lead; three ledger rows without a second value) |
| C18 | Null results and failed runs on record | g2long entries 5, 11, 12, 14, 19-21, 24, 26, 27 (grep: P5 REFUTED, P6, P13 FAILED, P12 with the M/8 control, D3 at M/4 and N/4, R1, T1, XC2); failed runs D-20261125-160123-f86d73c (status failed, exit 1) and the conv3 first reading D-20261126-055207-0137c53 (kept, labelled post hoc); STAGE_REPORT lists the failed manifests. My own nine predictions all held | PASS |
| C19 | STATUS, JOURNAL, HANDOFF current | rewritten at the end of batch 25 (commit 0f7bd90dc, 2026-11-25 22:03 PST); they predate the verifier's report, which the next session must take in | PASS |

## 3. Re-verification (`nrpic-stage verify D-bh-dress G2`)

On b1fefc58d, 2026-11-26T11:48:14Z: **PASS** (0 failed checks). package PASS with "verifier's
report VERIFIER.md"; runs PASS (331 manifests finished; four failures waived by coord/WAIVERS.md);
run-notes WARN (100 runs read with defaults: the hand-written manifests of waves 1-2, decision 0016
item 3); checksums WARN only because 15734 of 15768 files came from the cache of the full pass of
a5bd88c (that pass read every byte, 701.22 GB, PASS); rerun 14/14, compare 40 files, regenerate
28 files PASS. Logs: `scratch/D-bh-dress/tmp/gate_review_G2/stage_verify_reviewer_20261126-034511.log`,
`VERIFY_RESULTS_reviewer_b1fefc5.md`, `VERIFY_RESULTS_full_a5bd88c.md`. The committed
VERIFY_RESULTS.md (06:01Z, `--no-checksums`, before the verifier) is what the package still carries.

## 4. Failed predictions, null results, run ids

Failed predictions and their rulings are on record where the CHECKLIST says (C18); the refuted
P5 and the M/4 failure of N stay refuted and are labelled in the note. The verifier's own failed
predictions (V1b, the first reading of V1c) are in its report. Every number of section V of the note
maps onto ledger part 11, and every row there names a registered run (verify: runs PASS). The two
places where text and evidence disagree are wording, not missing run ids (C16).

## 5. Reservations to carry to G3

1. **Mesh leg.** The growth and the null test have two mesh members inside the convergent regime
   and no order. The M/16 - M/8 growth difference has a systematic part (+5.8e-4 mean over 250-299
   M, envelope 1.0e-3; R5); G3's convergence of the growth law needs a third member inside the
   regime and must quote envelopes, not samples at pre-named times.
2. **No gauge leg.** Every G2 run slices with plain 1+log; the relaxed lapse fails in vacuum and
   `lapse_leak_hole` is a mitigation (OPEN.md section 2). The boundary leg is measured in vacuum to
   200 M. A G3 run that needs another slicing needs its own vacuum control in that slicing.
3. **Finder floor.** The null test's floor is the production finder's stopping rule (2.28e-4 with
   it, at most 7.3e-5 converged). The G3 upper limit on a coupling exponent should be read with the
   converged finder (or core's fix) and with `<fastflow> diagnostics = true` (0041 item 5); every
   G2 horizon number was made without the diagnostics.
4. **Horizon excision ends at 4 x initial_radius** (nrpic.cpp:451-455): it moves the (iii) medians
   by about 0.35 per cent and the closure (ES-FL +9.4e-3 against FK +2.2e-3). G3 growth runs keep
   excision on (FK's set-up or core's guard).
5. **Shells ahead of exact LTB** by about 0.2 per cent of proper time at R0 = 28 M (0.78 M at M/8
   and N, 0.55 M at 4N, 0.40 M at M/16; verifier 4.1): converging, harmless to G, but it biases any
   dress or spike profile read from removal times; G3 must show it converge further.
6. **Particle noise.** D3 fails at N/4 after 220 M; single-sample horizon masses at N/4 jitter by
   up to 3e-3; the constraint residual near the hole is shot noise that grows 3-4 times over 400 M
   and does not fall with the mesh. G3 production at N or above.
7. **Rows without a second value**: converged-finder null difference 6.53e-5; plane-norm ratios
   XN, XQ, L5.
8. **From G1, still open**: the Kerr a = 0.8 comparison rests partly on judgement; the infall power
   law is untested (QR3, QR4 fail narrowly at the second resolution, LADDER.md).
9. **Core's G2 is unsigned**; D relies on its rows 1 and 2, carried to core-v0.6 by byte regression.

## 6. Corrections owed by the lead (formal; none changes a verdict)

a. CHECKLIST C17 to PASS with VERIFIER.md; rerun `nrpic-stage report` (the committed STAGE_REPORT
   reads FAIL for C17 and ends with the batch-20 "Not ready for review"); commit a verify of the
   final package commit.
b. LADDER.md and schem_ladder.png at the final state.
c. Ledger row of FF4: D2 "480 samples with the control held at its last value after 299 M; 280
   within the control".
d. CHECKLIST C2 and note line 244: quote the envelope of the mesh difference (max 1.0e-3, mean
   +5.8e-4 over 250-299 M) beside the samples; remove "a few parts in a hundred thousand".
e. Note line 236: "at most 7.3e-5" (or name the window of the 6.53e-5 row).
f. Note section VI and summary: remove the statements that predate the G2 runs.
g. OPEN.md, CHECKLIST C8, risk R28 and note line 254: record the verifier's decided cause of the
   early removals (VERIFIED for the tracers, JUDGEMENT for the dust, as the verifier labels it).
h. FK's D3 "min margin -1.4e-4" wording (verifier section 9).
