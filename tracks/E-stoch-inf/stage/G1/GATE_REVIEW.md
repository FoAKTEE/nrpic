# GATE_REVIEW.md: independent gate review of G1 of E-stoch-inf

Reviewer of batch 4a (decision 0019 item 3), fresh context, 2026-11-21 15:45 to 15:56 UTC.
I produced none of the work under review. No tag `stage/E-stoch-inf/G1-pass-*` existed when I
started (`git tag -l`: only `stage/E-stoch-inf/G0-pass-20261120`). Worktree after `git merge
main`: ddfbc8fc.

**Read.** `CLAUDE.md`; `coord/CHARTER.md` to "Owners" and sheet 9.8 (G1: "the power spectrum of
the slow-roll case agrees with the analytic result, super-horizon modes freeze by the criterion
of arXiv:2606.14853, the constraints converge"); brief lines 674-686 (G1: "baseline results
obtainable without the NRPIC coupling; the analysis pipeline validated on them; interface
proposals submitted"); decisions 0013 (Track E: continue to G1 and G2; SCOPE 4 choices
accepted), 0016, 0019, 0021 item 1 (A4' adopted, strict A4 on record as failed), 0022; the
package `stage/G1/` (STAGE_REPORT, CHECKLIST, EVIDENCE, OPEN, REVIEW, STATUS, VERIFIER);
`spec/scope/SCOPE.md` sections 4 and 4b (thresholds A1-A8, A4', A5'); `stage/REVIEW-wave3.md`
B4; the source of the freezing criterion, arXiv:2606.14853 v2 `Manuscript.tex` lines 180-229
(kb-data, read only).

**Opened as evidence** (named at each criterion): eighteen run manifests; the result JSON of
the ladder (`ladder/results/final/P256_judge.json`, `final2/summary.json`,
`seed2/P256s2_judge.json`) and of the verifier (`g1verify/results/v123.json`, `v45.json`,
`v45_addendum.json`, byte-identical to the outputs of runs E-20261121-030207-fb6f090 and
E-20261121-031951-82984f8); the raw records `sr.sf.hst`, `sr.sf.con.hst` of eleven ladder runs;
the note's ledger `note/tables/ledger_g1.md` and claims check `claims.md`; fourteen figures,
each looked at with the Read tool (listed in section 2).

**Ran.** (1) `harness/bin/nrpic-stage verify E-stoch-inf G1 --no-checksums` on ddfbc8fc (section
3; output kept in `scratch/E-stoch-inf/gate_review_G1/VERIFY_RESULTS.{md,json}`, `verify.log`;
the stage copies were restored to their committed state, so this review changes no package
file but this one). (2) `nrpic-run verify` (output checksums) on eleven G1 runs: all PASS
(section 3). (3) My own check, registered: run **E-20261121-155055-bf2ef8c** (`nrpic-run`, 2
cores, exit 0; script `scratch/E-stoch-inf/gate_review_G1/review_checks.py`, which imports
nothing of the track but a copy of `harness/style/figstyle.py`; predictions committed first in
bf2ef8cd), section 1. (4) The manuscript checker with `--compile` on a scratch export of the
committed note (`scratch/E-stoch-inf/gate_review_G1/check.log`). No card-hours used.

## 0. Verdict

**Recommendation: PASS WITH RESERVATIONS.** The three track criteria and the three common
criteria are met by evidence I opened, with the constraint criterion met in the form ruled by
decision 0021 (A4'), not in the owner's original strict form (A4), which fails in the paper's
set-up and is on record as failed in the package, the ladder journal, the verifier's report and
the note (`note/main.tex` line 253 states that the floor definition was fixed after the data).
The spectrum and freezing results are strong: per-mode agreement 1.2e-4 against a threshold of
2e-2, freezing within 3e-6 against 1e-2, confirmed by a fresh verifier with its own code from
the raw dumps and, for the record quantities, by my own run. The harness verify passes every
check on ddfbc8fc (the package's own STAGE_REPORT still shows the FAIL of 13:33Z, caused by a
G2 card job that was pending then and is finished now). No science item blocks the gate.

## 1. My own check: predictions and outcomes

Predictions as committed in bf2ef8cd (first version of this file), before the run. Run
E-20261121-155055-bf2ef8c, outputs `review_checks.json` and `fig_review_checks.png` in
`scratch/E-stoch-inf/E-20261121-155055-bf2ef8c/` (figure looked at: A1 deviations flat at 1e-13
to 1e-11 over 8.1 e-folds, eight decades below the threshold; record maxima of the proper runs
at 4.8-5.1e-11 and 3.8-4.0e-4 during the entry, controls at 1e-7 and 0.2 early, falling late).

| # | Quantity | Claim | Mine (E-20261121-155055-bf2ef8c) | Outcome |
|---|---|---|---|---|
| F | sha256 of the 22 record files read, against each producing run's `sha256sums.txt` | (verifier: all dumps match) | 22 of 22 match | holds |
| B | A1 against my DOP853 Friedmann/Klein-Gordon background, max over all rows | phi 2.0e-12 (P256), Pi 8.6e-12, K 3.6e-12 (L32p) | phi 1.999e-12 (P256); Pi 8.56e-12 (P256, L256p); K 3.63e-12 (L32p); every one of 11 runs below 9e-12 | holds |
| C | e-fold error at the last row, -ln<chi>/2 against my ln a | 5.5e-6 (L32p), 3.3e-7, 2.0e-8, 1.3e-9 | 5.52e-6, 3.32e-7, 2.04e-8, 1.28e-9 (P256); factor 16.6 and 16.3 per doubling | holds |
| D | A4'(c) record maxima over the whole record, paper's set-up | H: Q64p 4.8e-11, Q128p 5.0e-11, P256 5.1e-11; M 3.8-4.0e-4 | H: 4.83e-11, 5.04e-11, 5.10e-11; M: 3.83e-4, 3.96e-4, 3.99e-4 | holds (limits 1e-9, 1e-3 kept by 20 and 2.5) |
| E | negative controls NC32p, NC64p, NC128p (sign flip confirmed in `proc32.list` and the job-C list) | H 9.8-9.9e-8; M 0.21-0.22 | H 9.80e-8, 9.91e-8, 9.91e-8; M 0.207, 0.213, 0.216 | holds |
| G | second seed P256s2 | (A1-A3 judged by the ladder) | A1 phi 1.98e-12, Pi 6.3e-12, K 1.97e-12; record maxima 5.11e-11 and 4.00e-4 (P256: 5.10e-11, 3.99e-4) | holds |

All six predictions held. In addition I read the last row of the constraint records for a
ledger row that `REVIEW-wave3.md` B4 lists as "track only" (row 26 of `ledger_g1.md`, record
<|H|/[H]> at N_f): L32p 3.124e-12, L64p 1.832e-13, L128p 1.115e-14 (Q128p 1.123e-14), against
the ledger's 3.12e-12, 1.83e-13, 1.12e-14; agrees. Of the 13 track-only rows, row 26 now has an
independent value and row 21 one in part (the controls' record levels of check E, not their
ratio 4e4-1.5e5 to the proper run).

## 2. Criteria, one by one

| # | Criterion | Evidence I opened | Verdict |
|---|---|---|---|
| C1 | Baseline results without the NRPIC coupling | Manifests (all `completed`) of the MS references E-stoch-inf-20261115-122806-ef0d039, E-20261115-135532-3f958a1, verifier E-20261115-174606-3c67607, rerun E-20261119-150346-a513bc8, and of the delta-N references E-stoch-inf-20261115-130137-176cdd6, -130139-176cdd6; the SR ladder itself is scalar field plus Z4c, no particles (deck `sr_base.athinput` of P256: no `<particles>` block) | PASS |
| C2 | Analysis pipeline validated on them | Manifests of E-20261115-171445-36152c4 (T1-T5), -171859-0b34449, -172935-ddfade0, -174214-74becdd (all completed); `nrpic-run verify` PASS on E-20261119-150238-b81e33f (lead's own extraction); figures `analysis/fig/fig_t2_extraction.png` (estimator error falls as the amplitude, i.e. second order; the sign-flipped and the anisotropy-free estimators fail as they should) and `stage/G1/fig/fig_lead_check.png` (own extraction on L32p: A2 below 1e-4 for k <= k_max/2, freezing drift 1e-4, halving 2 and 4); the verifier's independent pipeline (own reader, Philox, MS, R^NR) agrees with the track's numbers to three digits (VERIFIER.md comparison) | PASS |
| C3 | Interface proposals submitted | `tracks/E-stoch-inf/outbox/` holds the 2026-11-15 messages to core (card build, initial slice at N*, noise unit-test results, diagnostics and interface) and those of 2026-11-19 and 2026-11-21; `noise/NOISE_SPEC.md`, `noise/RNG_REQUIREMENTS.md` present | PASS |
| C4 | Baseline data and figures | result directories `ladder/results/{final,final2,floor,a6,a6_64,l5,seed2,a12}`; figures opened: `ladder/fig/final/fig_spectrum.png`, `note/figures/fig_sr_modes.png`, `fig_sr_freezing.png`, `fig_sr_constraints.png`, `fig_sr_order.png`, `g1verify/fig/fig_v3.png`, `fig_v4.png`, `fig_v5.png` | PASS |
| C5 | Interface documents | `coord/INTERFACES/scalar_field.md`, `scalar_field_2.md`, `scalar_field_3.md`, `rng.md` on main; track documents as in C3 | PASS |
| C6 | Spectrum agrees with the analytic result; super-horizon freezing by the criterion of arXiv:2606.14853; constraints converge | see the three paragraphs below this table | PASS WITH RESERVATION |
| C7 | Feasibility decision (0013) applied | SCOPE 4 choices used (Courant 0.25; A6 orders 3.93-4.10 in the verifier's V6); downgrade not triggered: cost 0.5031 card-hours per 256^3 SR realisation (manifest E-20261115-172618-f948386, `resources.gpu_hours`; 0.5008 for seed 2, E-20261121-032828-fe18c5f) against 5 | PASS |
| C8 | Updated architecture schematic | `note/figures/schem_architecture.png` opened: three stages, four states (core-v0.3, core-v0.4/v0.5, track analysis, new); legend predates core-v0.6 (cosmetic) | PASS |
| C9 | Data-flow schematic | `note/figures/schem_dataflow.png` opened: mode tables, AthenaK run, analysis (A1-A6, controls), ledger and note | PASS |
| C10 | Data figure: baseline results | `ladder/fig/final/fig_spectrum.png` (shell spectrum of P256 scattering about the full MS; NR over the reference with the same alpha equal to 1), `note/figures/fig_sr_modes.png` (D_n below 1.3e-4 for k <= k_max/2 at every rung, 4.5e-3 over all modes of P256) | PASS |
| C11 | Validation figures of the pipeline | as in C2 | PASS |
| C12 | Package documents (0012) | STAGE_REPORT, EVIDENCE, OPEN, CHECKLIST, VERIFIER, REVIEW, STATUS present; scoping text `spec/scope/SCOPE.md`. The committed STAGE_REPORT.md and VERIFY_RESULTS.md still carry the verify of 13:33Z (FAIL on `runs`: a4res job 4798 pending); that run is now finished and my rerun passes every check (section 3) | PASS WITH RESERVATION (formal: regenerate verify and report) |
| C13 | Data figures from registered outputs, one script each | verify: 12 figures with a script each, 12 of 12 scripts rerun cleanly in a clean export, 24 regenerated files equal to the committed ones (PNG rms below 0.005); `nrpic-run verify` PASS on the note run E-20261121-080840-6112292 (57 files) | PASS |
| C14 | Schematics with paperfig: architecture and timeline | `note/figures/schem_timeline.png` opened (G0 passed, G1 in progress, G2-G4 ahead); C8, C9 above; verify `style` PASS | PASS |
| C15 | Working note with /paper-writing; checker with --compile | my rerun of `check_manuscript.py --main main.tex --compile` on the committed note: 0 undefined references, 0 undefined citations, 0 overfull boxes; the only candidates are run ids in the ledger tables (accepted exception); `main.pdf` 16 pages; three red `\pending{}` markers stand for G2 packages | PASS |
| C16 | Fresh verifier; Supplemental numbers recomputed | VERIFIER.md opened in full: own code from the raw dumps, sha256 of every dump checked, verdicts committed (db88f631, 19:26 PST) before the comparison with the track's numbers (c43e050c, 19:28 PST); it saw two ladder numbers quoted in SCOPE 4 (it says so). Ledger: 45 rows, every row carries a run id or a source locator (I checked all rows of `ledger_g1.md`); 27 of 40 track rows agree with an independent value (B4), 13 were the track's alone, of which I have now read one more and part of another (section 1) | PASS WITH RESERVATION (12 ledger rows still without an independent value) |
| C17 | Null results and failed runs on record | the 16 failed or stopped runs listed in STAGE_REPORT keep their manifests; the explanation of the failed G0-ledger run E-20261115-140116-87c1cc5 (only wall-clock leaves differ) is in `stage/G0/EVIDENCE.md` line 63; prediction/refutation pairs and failed predictions are written in `ladder/JOURNAL.md`, `g1verify/JOURNAL.md` (e.g. its e-fold prediction of 1e-8 and its k^4 floor shape, both failed), `note/JOURNAL.md` (N8), owner `JOURNAL.md`; strict A4 failure in STATUS, CHECKLIST, the ladder README and the note | PASS |
| C18 | STATUS, JOURNAL, HANDOFF current | last changed 9edf5349 (2026-11-21 05:32 PST); STATUS says G1 complete for review and not passed; HANDOFF names this review and the P256 rerun on the release card build | PASS |

**C6, spectrum (A2).** `ladder/results/final/P256_judge.json`: max D_n over the 68532 modes with
k <= k_max/2 at N_f = 8.10 is 1.2078e-4 (threshold 0.02), over all 548958 modes 4.49e-3; the
verifier's `v123.json` gives 1.2078e-4 for P256 from its own extraction; seed 2
(`seed2/P256s2_judge.json`) 2.121e-4. Figures `fig_sr_modes.png`, `fig_spectrum.png`. The
shell spectrum sits 1.0-1.3 percent above the leading-order slow-roll formula, and the full MS
gives the same (VERIFIER V2); "the analytic result" is therefore read as the linear MS solution
with the same random amplitudes, which is the right reference for a per-mode test [JUDGEMENT].
The verifier's maxima over time are huge before modes enter (8.6e7 at t = 0 for P256): those
are modes outside the window with a vanishing reference; the criterion is at N_f, where every
rung passes. Met.

**C6, freezing (A3).** Source checked: arXiv:2606.14853 `Manuscript.tex` 186-213 (full MS: R_k
frozen on super-horizon scales; without the metric perturbation, the "deformed" equation, R_k^2
decays as (H/H_CMB)^4, i.e. d ln R^2/dN = -4 eps). The track's A3 tests exactly this
distinction. `v123.json`: 1051 modes per rung, |ratio_NR/ratio_MS - 1| at most 2.38e-6 to
3.20e-6 (threshold 1e-2); figures `fig_sr_freezing.png`, `g1verify/fig/fig_v3.png` (the
deformed equation sits at 0.1-0.17, the data at 1e-9 to 3e-6). Met with a margin of 3e3.

**C6, constraints (A4', A5).** `g1verify/results/v45.json`, `v45_addendum.json`: with the
non-scaling floor, odd-part halving 1.9989-2.0000 and even-part halving 3.986-4.000 on L32, Q64,
Q128; L128 and L256 even parts within 0.76 percent after each run's floor is removed (17 percent
raw); controls' ratio of maxima 1874, 1709, 1853 (NC32-NC128). With the out-band floor instead,
the same file gives odd halving down to 1.77 (Q64) and 1.43 (Q128): the A4' verdict depends on
the floor definition, which was chosen after the data. Spatial order (`fig_v5.png`): 5.5-5.6 for
L32 -> L64 over the whole odd part; for 64 -> 128 and 128 -> 256 only the in-band part (a band
the verifier chose) shows order 5.2-5.96, the whole odd part being at the rounding floor
(N^2.45-2.51). `fig_sr_constraints.png` and `fig_v4.png` show the strict-A4 failure plainly:
in the paper's set-up the odd part rises to 5-6e-11 at every N once shells with k dx ~ pi/4
enter, above the N-independent even plateau of 7e-13 (odd/even 745, 655, 869, 25 in
`final2/summary.json`). That is a discretisation error that halves exactly and converges where
the injected modes are held fixed, so "the constraints converge" holds in the sense of A4' as
ruled. Met with the reservations of section 5. Supporting but not reviewed by a lead yet: the
G2 package `a4res` (commits 371d5f1f, 080a4884) finds strict A4 holding at 12.8 and 16 cells
per shortest wavelength and failing at 10.7 and 8, confirming core's stencil explanation
(runs E-20261121-131000-b23055b, -152010-371d5f1); I did not review it.

## 3. Harness verify and checksums

`nrpic-stage verify E-stoch-inf G1 --no-checksums` on ddfbc8fc (2026-11-21 15:46 UTC): **PASS,
0 failed checks**: clean, sync, export, size, note, package, note-pdf, style (2 copies equal),
fig-script (12), min-figs (3 schematics, 9 data figures), runs (149 manifests finished, 30
hand-written read as decision 0012 allows), status (42 lines), rerun (12 of 12), compare (24
files, 0 beyond tolerance), regenerate (24); `run-notes` WARN for the 30 hand-written manifests
of waves 1-2 (waived, decision 0016 item 3). The full checksum pass reads about 150 GB and was
not run; instead `nrpic-run verify` recomputed the output checksums of E-20261115-194633-9e04ed8
(101 files), E-20261115-172636-ce98836 (178), E-20261119-150238-b81e33f,
E-20261121-025932-7a21f34, -030207-fb6f090, -030522-c6907b6, -030657-c1afe38, -031251-c48670d,
-031951-82984f8, -032413-0672bf9, -080840-6112292: all PASS. My run checked the 22 record
files of the 11 ladder runs (P256's 53 GB of dumps not re-hashed by me; the verifier hashed
every dump it read). Observation: the registered analysis runs record no input checksums
(`inputs: []` in E-20261115-194633-9e04ed8, E-20261121-030207-fb6f090, -031951-82984f8,
-080840-6112292); their inputs are the simulation outputs, whose checksums the producing runs
and the verifier hold.

## 4. Failed predictions, null results, numbers without a run id

On record (C17). Every one of the 45 rows of `note/tables/ledger_g1.md` names a run id (three
rows cite core's runs and are labelled [TO VERIFY]). The note's claims check
(`note/tables/claims.md`, run E-20261121-080840-6112292) finds 7 of 104 numbers of the lead's
documents differing from the files: c16-c19, c21 are G0 estimates superseded by measurement;
g22, g23 (A1 maxima of `ladder/README.md`) have since been corrected in the README to 2.0e-12
and 3.6e-12, which my run confirms. `claims.md` itself still shows the old comparison until the
ledger is regenerated (cosmetic).

## 5. Reservations to carry to G2

1. **Criteria fixed after the data.** A4' and A5' (the floor as the non-scaling part, (d) on
   the maxima over the entry) were formulated after the ladder was seen; with the verifier's
   first floor choice A4'(a),(b) fail at Q64/Q128 for t <= 2, and A4'(d) fails pointwise
   (control/proper odd part 89-179 at the end of the entry). G2's USR acceptance (U-A2', U-A4',
   decision 0022 item 2) carries the same weakness: fix definitions before the runs.
2. **Release executable.** All G1 runs used the tested branch `core/scalar-2` a58e95b
   (scouting, decision 0013). The release processor build equals it word for word at 32^3
   (E-20261121-064707-77ec326); no card run of a release has repeated P256 (0.5 card-hours,
   `ladder/inputs/jobA.list`). G2 production runs should use a release card build.
3. **Convergence evidence is thin at the top.** No halved pair at 256^3 or beyond 32^3 in the L
   set-up; P256's odd/even split stops at t = 4.0 (P256m ends at 4.5) before its k_max shell
   enters at t = 4.31; the order beyond 64 is that of an in-band part chosen by the verifier;
   the N^2.5 rounding floor is attributed to rounding by three measured properties plus
   judgement.
4. **Absolute constraint levels 40-100 times below P1's statements** while the control/proper
   ratio matches (risk R18, [TO VERIFY]): a definition mismatch of [H] or of the box statistic
   would change the magnitude clause A4'(c).
5. **Ledger independence.** 12 of the 40 track rows of the G1 ledger still have no
   independent value (rows 7, 16, 20, 21 in part, 23 for M, 24, 28-30, 35, 36, 40 of
   `ledger_g1.md`); core's three rows await the review of `a4res`.
6. **A7** is shown on processors, one rank, 32^3; the card build was not checked for layout
   invariance, and the rank count is untested.

## 6. Formal items (not blocking)

- Regenerate `VERIFY_RESULTS.{md,json}` and `STAGE_REPORT.md` (`nrpic-stage verify`, `report`):
  the committed copies show the FAIL of 13:33Z; the verify now passes (section 3).
- `note/tables/claims.md` to be regenerated with the ledger (g22, g23 corrected in the README).
- The architecture schematic's legend names core-v0.4/v0.5; the program is at core-v0.6.
