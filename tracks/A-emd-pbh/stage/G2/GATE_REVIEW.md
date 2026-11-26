# Gate review: A-emd-pbh, gate G2 (verified capability)

Independent gate reviewer (decision 0019 item 3), batch 30, 2026-11-26 15:16-15:45 PST. I produced
none of this work. Opus, processors only, 0 card-hours, one core. Labels as in the brief:
[VERIFIED] = recomputed here by a registered run or read by me from a registered output;
[BACKGROUND]; [JUDGEMENT]; [TO VERIFY].

No tag `stage/A-emd-pbh/G2-pass-*` exists (`git tag -l`: G0-pass-20261119, G1-pass-20261121 only).

## 0. What I read and opened

- Criteria: `coord/CHARTER.md` 9.2 and 9.4 (G2 row; Track A: "in the spherical case, the errors of
  the turnaround time and of the horizon-formation time relative to the exact solution converge in
  particle number, mesh spacing and ball radius; the horizon-mass error is of the same order as in
  the Oppenheimer-Snyder test of Wu and Most"), brief lines 674-686, section 10 rows owned by A;
  decisions 0013, 0016, 0039 item 2, 0040 items 2, 3, 6, 7, 0041 item 2, 0043 item 1, 0046 item 1;
  the track's own G2 exit criteria written at G0, `scope/SCOPE.md` sections 3 and 7.
- Package: STAGE_REPORT.md, CHECKLIST.md, EVIDENCE.md, OPEN.md, RERUN.md, VERIFIER.md (batch 29),
  VERIFIER-C18.md (batch 18), VERIFY_RESULTS.md; `stage/G1/GATE_REVIEW.md` section 6 (reservations
  carried to G2); journals `threshold_ball/JOURNAL.md` entries 1, 4, 6-9, 13-15,
  `periodic_threshold/JOURNAL.md` 2026-11-21 13:20Z, 23:15Z, 2026-11-25/26 (A2, AZ1, AZ2, A2X, A2H, D1-D5),
  `szekeres/JOURNAL.md` entries 12-14; note `main.tex` sections II.B and V-VII, `tables/ledger_g2.tex`.
- Outputs opened (raw): `convergence.md`, `convergence.json`, `turnaround.log` of
  A-20261121-120257-a2eb839; `threshold.md`, `threshold_series.json`, `C-R1.25_numbers.json` of
  A-20261124-131120-5c974ce; the horizon status files of S1L (A-20261123-025907-97bab8d), S1L-h
  (A-20261126-125306-0653547) and P0L6 (A-20261125-044641-7d5bd16); the manifest of
  A-20261121-120257-a2eb839 (status completed).
- Figures looked at (Read): `fig_edge.png` (A-20261126-212340-4ea9fb2), `fig_constraint_conv.png`
  (A-20261124-132342-d5dc06e), the verifier's `fig_c3_verify.png` (A-20261126-223246-89959bc),
  `fig_p0l6_verify.png` (A-20261126-223655-77df724), `fig_a2_verify.png` (A-20261126-223151-8310871),
  `fig_szk_verify.png` (A-20261126-222856-952faf8); the note's `fig_g2_convergence.png`,
  `fig_slice_mosaic.png`, `schem_ladder.png`; my own `fig_gr_checks.png` (section 2).
- Source locators checked in `refs/arxiv_2611.12831/src/main.tex`: line 945 "The fiducial run gives
  a relative error of Delta M/M_ADM <~ 10^-3" (final mass after excision against the ADM mass);
  line 1484 epsilon_M = 2.061e-3, 9.362e-4, 7.347e-4 (A1-A3, RMS over five seeds at t = 60 M).
  Both locators quoted in C8 are right [VERIFIED].

## 1. Stage check

- The full checksum pass started at 14:18 PST (pid 499738, log
  `scratch/A-emd-pbh/tmp/stage-verify-full-verifier-20261126-141818.log`) was **still running** at
  15:26 PST; its log is written at the end and was empty (0 bytes). Its result is not part of this
  review.
- I ran `harness/bin/nrpic-stage verify A-emd-pbh G2` with the cache at 15:17 PST on 6d1d18ad9 (main
  merged): **PASS**, 0 failed checks (log `scratch/A-emd-pbh/tmp/stage-verify-gatereview-20261126-151729.log`;
  committed `VERIFY_RESULTS.md` in 42c8c8f32). 327 manifests finished (102 hand-written), one waived
  run (A-20261121-064515-aa13c8f, coord/WAIVERS.md); 11 of 11 rerun commands clean in the export;
  21 regenerated files equal the committed ones; 20 figure files regenerated. WARN: 31,414 of 31,429
  output checksums taken from the cache (unchanged size and time, bytes not read again); 80 runs read
  with defaults by `nrpic-run lint`.
- The stage check passing says the package is reproducible; it does not say the criteria pass.

## 2. Reviewer's own checks (run A-20261126-232456-42c8c8f)

Predictions written before the run in `scratch/A-emd-pbh/tmp/gate_review_g2/PREDICTIONS.md` (an input
of the manifest, with its sha256); script `gr_checks.py` beside it; outputs `gr_checks.json`,
`fig_gr_checks.png` (looked at). G1 and G3 are recomputations (I had read the inputs), G2 and G4 were
predictions.

| check | outcome | status |
|---|---|---|
| G1 finder in the periodic box | S1L: 314 searches to t = 219.9, **0 found** (218 reason 6 "no convergence of the mass", 96 reason 4); every search from t = 86.8 ends with reason 6. S1L-h: 288 searches, 0 found. P0L6: 308 searches, 1 found at t = 118.12 (area mass 562, mean radius 18.2, the false acceptance), every search from t = 121.40 ends with reason 6 | [VERIFIED]; agrees with the verifier for P0L6 |
| G2 SCOPE section-3 bound in the ball members | In all 11 threshold_ball members the line ratio ||H||/||16 pi E|| outside the finder radius is above 0.1 at **every** sample with t > 0 (minimum over t > 0: 0.13-0.39); at the sample nearest the first persistent detection: B-d1.00 2.08, B-d0.70 0.38, B-d0.50 0.53, B-d0.45 0.46, **B-d0.42 1.11, B-d0.40 1.44**, B-d0.35 1.70, C-R1.25 2.96. 0 of 10 members with a detection meet the bound there | prediction G2 HOLDS |
| G3 ball-radius leg of the detection time | R0: 0.193, 0.0675, 0.0166 M (orders 1.51, 2.02). 1.25 R0: 0.1004, 0.0650, 0.0403 M (orders **0.63, 0.69**) | [VERIFIED] arithmetic on registered values |
| G4 note Fig. 7(a) | `fig_g2_convergence.py` line 41 labels the tick at h = 1/16 "1/64" and the tick at h = 1/64 "1/16"; the data sit at the right h, so the printed panel reads as if the error grew as the cells shrink | prediction G4 HOLDS: a figure defect |

Reading [JUDGEMENT]: in panel (b) of `fig_gr_checks.png` the failed searches of S1L from t ~ 87, of
P0L6 from t ~ 121 and of S1L-h from t ~ 155 each form a smooth sequence of slowly growing area mass;
in P0L6 that sequence coincides with tracked shells trapped in the code (verifier 2.3). The stall of the
finder is therefore common to all three periodic runs, and S1L may hold a trapped surface from about
8.9 t_H that nothing has read. Not tested.

## 3. Criteria

| # | criterion (as written) | verdict | evidence opened, and why |
|---|---|---|---|
| C1 | The code paths used by the track pass their tests of section 10 | **FAIL** | (i) Time-reversed Oppenheimer-Snyder (expanding ball): passes. Detection times reproduced to the printed digits by VERIFIER-C18 (section 3-4; tau_det 43.686, 46.402 around t_end = 45) and the exact references to all digits; I opened `threshold.md`. But "the code's bracket (0.40, 0.42] equals the exact one" holds only under the rule of threshold_ball entry 1, which leaves out the constraint clause of SCOPE section 3: under the outcome rule as written every member is UNDECIDED (my G2). (ii) LTB: **fails**, more than the horizon part. The finder accepts a non-trapped surface at t = 118.1 and fails every search from t = 121.4 while tracked shells are trapped (my G1; verifier 2.3); the shells r0 > 1.5 follow LTB within 3.3 per cent only up to their turnaround and depart by up to 42 per cent during collapse; the inner shells r0 <= 1.5 are worse on six levels than on four (D4 refuted) (`fig_p0l6_verify.png` looked at). (iii) Szekeres: passes with clauses refuted on record; the verifier reproduces Table V's rms errors within 4 per cent and its orders within 0.08 (K) and 0.14 (H) (`fig_szk_verify.png` looked at); P20 holds only with Table V's same-cell signal, not with the invariant same-shell signal at N256 tau 30 (5.1x) and N128 tau 20-30; at tau 40 the N256 error equals the invariant signal. (iv) Oblate/prolate (A2): **fails as written**: first crossing (6.19, 7.21] t_H coordinate, (5.99, 6.94] t_H on the dust's own clock, against [3.4, 5.0]; GR/Newton factor 1.65-1.9; A2H held its band (13.85, 14.36] in [12.5, 15.2], which narrows the cause to a class of effects first order in the amplitude without naming one (`fig_a2_verify.png` looked at) |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | PASS WITH RESERVATION | `convergence.md` of A-20261121-120257-a2eb839 opened: mesh leg ddet 0.193, 0.0675, 0.0166 M, dtrap -0.0925, -0.0224, -0.0077 M; particle leg at B 0.0675 against 0.0705 (x8); boundary leg identical to 1e-7 (A) and 1e-11 (B). Reservations: shown only for the expanding ball at one amplitude (delta_c = 1.5), nowhere in the periodic box where the threshold line is to be built (decision 0013; P0L/P0L6 is a mesh pair with D4 refuted); the detection-time order depends on the interpolation at the core edge (1.2-2.1, VERIFIER-C18 5e) and on the ball radius (0.63-0.69 at 1.25 R0, my G3); no mass order (C below the tracked-set resolution); gauge leg not run (allowed: "gauge or boundary") |
| C3 | Constraints behave | **FAIL** (as ruled, 0039 2(c), 0043 1(a)) | `fig_edge.png`, `fig_c3_verify.png`, `fig_constraint_conv.png` looked at: every member exceeds 0.1 by t = 1; from t ~ 1.5 all members (top hat, smoothed, PCS, CIC, M/16, M/32, x1, x8) lie on one curve rising to ~0.6 at t = 5; mesh order 0.34-0.36 at t = 0.75-1 (smoothed CIC), negative for the top hat; flat in particle number from t = 1 on (11-25 per cent apart at t = 0.25-0.75, verifier 2.4); K3 found the floor neither at refinement faces nor at density jumps. In the ball members the bound fails at every sample after t = 0 and at every detection (my G2). Cause unexplained |
| C4 | A first minimal full-GR kinetic run | PASS | conv_ball's 14 members and the eight mesh-B threshold members form horizons by the entry-1 rule, statuses checked against the status files (VERIFIER-C18 5a, decision 0040 item 3) |
| C5 | Verification report | PASS WITH RESERVATION | STAGE_REPORT.md, EVIDENCE.md, OPEN.md, RERUN.md exist; the note's section V is the text. STAGE_REPORT.md is stale: it still says "no VERIFIER.md" and "Verifier report MISSING"; EVIDENCE.md is headed "interim; G2 is NOT complete". Regenerate with `nrpic-stage report` |
| C6 | Reproducibility package | PASS | my stage verify (section 1): 11 of 11 reruns, 21 files compared, 20 figures regenerated; RERUN.md lists the commands. Byte checksums from the cache until the full pass ends |
| C7 | Spherical case: errors of turnaround time and horizon-formation time converge in particle number, mesh spacing and ball radius | PASS WITH RESERVATION | Horizon formation: mesh orders above; N flat at B. Ball radius: the radius dependence falls with the mesh, 0.09, 0.04, 0.024 M (A, B, C), but the 1.25 R0 series converges at 0.63-0.69 per halving (my G3) and T5 failed at 0.024 > 0.02. Turnaround (`convergence.md`, `turnaround.log`): dta -0.037, -0.033, -0.0082 M (A->B order 0.16, B->C 2.02); the estimator spread at C runs from -0.0006 (Cexp) to -0.0083 (P2), as large as the value: the B->C order rests on one estimator, and **neither verifier checked the turnaround columns** (VERIFIER-C18 6, VERIFIER 5) |
| C8 | Horizon-mass error of the same order as the Oppenheimer-Snyder test of Wu and Most | PASS WITH RESERVATION | Locators checked (section 0). Brackets from the tracked set [5.1e-3, 7.2e-3], [-2.7e-3, -1.6e-3], [-1.0e-3, +0.5e-3] (A, B, C; A-20261125-151126-7f79a83 after VERIFIER-C18) against <~ 1e-3 and 2.1e-3 to 7.3e-4: same order. Reservations: different quantities (mass of a newly formed horizon against the exact slice; the source: final mass after excision against M_ADM; risk 17); C lies below the tracked set's resolution; four near-threshold medians withdrawn |
| C9 | Ruling 0013: threshold line in the periodic box; ball the spherical verification case | PASS (compliance) | The package follows the ruling. It also makes C1 (ii), the finder in the box and C3 the load-bearing failures for this track's science. The evidence text ("peak_leak6 queued") is stale |
| C10 | Schematic: verification ladder | PASS | `schem_ladder.png` looked at; three red rungs below the threshold line, honestly coloured. The green rung "code bracket equals the exact one" carries the entry-1 rule (C1 (i)) |
| C11 | Convergence figures (particle number, mesh, gauge) | PASS WITH RESERVATION | `fig_g2_convergence.png` looked at: panel (a) has its cell-size tick labels reversed (my G4); correct before sign-off. No gauge-leg figure (boundary leg chosen) |
| C12 | Constraint norms against time | PASS | `fig_constraint_conv.png`, `fig_edge.png` looked at; they show the failure of C3 clearly |
| C13 | Multi-scale slice mosaic with zoom boxes | PASS | `fig_slice_mosaic.png` looked at: Szekeres N256 at tau 40, three magnifications, density and local H/(16 pi E) |
| C14 | Package documents of decision 0012 | PASS WITH RESERVATION | present; STAGE_REPORT.md and EVIDENCE.md stale (C5) |
| C15 | Data figures with the figure style, one script each, every PNG looked at | PASS WITH RESERVATION | style copies equal (stage verify); the reversed ticks of Fig. 7(a) passed the lead's look |
| C16 | Schematics: architecture and timeline | PASS | stage verify fig-script and min-figs PASS; architecture states core-v0.8 |
| C17 | Working note with /paper-writing; checker passed with --compile | PASS WITH RESERVATION | checker and compile on record; text to correct (section 6, items 1-7) |
| C18 | Fresh verifier wrote VERIFIER.md; every number of the Supplemental Material recomputed | PASS WITH RESERVATION | VERIFIER.md (batch 29) reproduces all 24 rows of Table V (presence test) and recomputes the Szekeres, S2c and S1L/S1L-h rows with its own readers; VERIFIER-C18.md recomputes conv_ball and threshold_ball. Not recomputed by anyone: the turnaround columns, A-R1.35's ddet (0.164 against 0.175), Delta t_trap(C) to its inputs. The checklist still says OPEN; the verifiers' findings (VERIFIER.md section 4, items 1-6) are not yet answered |
| C19 | Null results and failed runs on record | PASS WITH RESERVATION | Failed runs and refuted predictions are on record in large number (STAGE_REPORT null-result list; journals). Missing: predictions S1-S3 of S1L's card job 2 (periodic_threshold 2026-11-21 23:15Z: "judged ... when the chain reaches 220") were never judged; the chain reached 220 and S2 ("an apparent horizon is found between 10 and 22 t_H") is refuted as written (0 of 314 searches, my G1). OPEN.md's list omits P18 at tau 40 and AZ1's first clause (both on record in the journals). A2X (ii) "not decidable" was decidable from the snapshots (verifier finding 1) |
| C20 | STATUS, JOURNAL, HANDOFF current | PASS | rewritten at the end of batch 28; STATUS.md 31 lines (stage verify) |

The track's own G2 exit criteria, written at G0 (`scope/SCOPE.md` section 7, "Gate criteria"), are not
in the checklist; I judge them as written:

| SCOPE section 7, G2 | verdict | evidence |
|---|---|---|
| "A1 and A3 pass with three-way convergence" | **FAIL** (A3) | A1 = the ball: as C2/C7. A3 = LTB ("R(l) within the convergence error; horizon outcome as LTB until the first crossing"): the horizon outcome fails (C1 (ii)); no convergence series in the box (two meshes, inner shells worse on the finer) |
| "horizon mass error in A1 of the same order as the source paper's Oppenheimer-Snyder test" | PASS WITH RESERVATION | as C8 |
| "one triaxial particle run of phase 1 to horizon formation with the constraint bound of section 3" | **FAIL** | S1L (mu = 0.3, e = 0.2) ran to t = 220 (22.5 t_H) with no horizon found in 314 searches (my G1); the bound is met nowhere (C3) |

## 4. Findings the package does not state

1. The threshold as this track defined it before any run (SCOPE section 3; note section II.B: a run
   is a black-hole run only "with the Hamiltonian constraint outside the horizon small against the
   energy density there"; "every other run is undecided and enters no bracket") cannot be measured
   with the present capability in either set-up. In the ball no run can be classified (my G2); in the
   box no horizon has been found in any run (my G1). The claim of note section V.A and of C1 (i)
   that "its threshold bracket of the ball equals the exact bracket" holds under the entry-1 rule
   only, and the note must say so.
2. The finder's stall is common to the three periodic runs, not a property of P0L6 (my G1, figure
   panel b). The release core-v0.8 (on main) has the finder with polishing iterations
   (`<fastflow> polish_iterations_<n>`, recommended 100 with `mass_tol_<n> = 1e-5`); none of the
   periodic runs used it. Restart files of P0L6 (`rst/peak.000NN.rst`, last 00019) and S1L exist, so the
   finder can be retried on processors without a card [JUDGEMENT: whether polishing cures reason 6
   here is untested].
3. S1L's predictions S1-S3 of card job 2 were left unjudged (C19).
4. The detection-time order of the ball is not robust to the ball radius (my G3).
5. Fig. 7(a) of the note has reversed cell-size labels (my G4).
6. The constraint floor has the signature of a defect that does not depend on resolution at all:
   flat in mesh, particle number, step, source extrapolation (K, K2, K4), not localized at level faces
   or density jumps (K3), the same late curve for every data set and cloud (C3), and in
   `fig_constraint_conv.png` panel (a) the volume norm jumps within the first half time unit from
   its t = 0 value (about 2, 0.8, 0.35 on A, B, C, read off the figure) to the same peak of about 14
   on all three meshes [JUDGEMENT on a figure reading]. The two deposit defects at level
   faces that core will fix are one candidate; K3 already argues against them as the whole cause.

## 5. Recommendation

**FAIL: G2 cannot be passed now, not even with the failures stated.** The gate is a verified
capability for this track's science, the formation threshold of black holes in a matter era in the
expanding ball and in periodic boxes. What is verified is narrower: in spherical symmetry the code forms
the horizon of the expanding ball at the exact time, with errors that fall with the mesh, do not depend
on particle number or the outer boundary, and a horizon mass of the source's order; two independent
verifiers reproduce these numbers. What is not verified is what the threshold needs:

- the outcome rule of SCOPE section 3 cannot be applied: no ball run meets the constraint bound at any
  time after t = 0 (C3, my G2), so every run is UNDECIDED as written;
- in the periodic box, where decision 0013 puts the threshold line, the finder finds no horizon in any
  run and accepted a false one (C1 (ii), my G1), and the track's own G2 criterion of one triaxial
  run to horizon formation with the bound is not met;
- the first caustic of the triaxial collapse, the step that carries the ellipticity dependence of the
  threshold, lags Zel'dovich and Newton by a factor 1.65-1.9 for a reason not named (C1 (iv));
- two of the four general G2 items (C1, C3) fail.

Passing the gate "for the ball" would reword it; I do not recommend that. The items that pass (C2,
C4, C6-C8, C10-C20 with their reservations) need not be re-reviewed; a second review can be limited
to what changes.

What would change the answer (each by a run that could have failed, prediction first):

1. **C3.** The cause of the floor shown, and the line ratio of SCOPE section 3 below 0.1 outside the
   horizon at detection in ball members at the bracket (B-d0.42 and B-d0.40 or their smoothed CIC
   twins), falling with the mesh at fixed particles per cell. Answer to decision 0046 item 1: the
   retest after core's two deposit fixes is a condition of **G2**, not of G3, because the bound is
   part of the definition of the outcome; it must run to the horizon, not only to t = 1. Cheap tests
   that can separate causes now, on processors [JUDGEMENT]: H written every cycle over the first 0.25 M
   of S2c-A (does the jump happen in the first step: a mismatch of data, source or gauge at t = 0?); H
   recomputed offline from a 3D dump of metric and deposited E at one time on two meshes by an
   independent reader (diagnostic against evolution); a member without level faces in the matter.
2. **C1 (ii), periodic finder.** On P0L6's restart files (t ~ 122-140) and S1L's, the core-v0.8 finder
   with polishing and diagnostics finds the trapped surface without false acceptance, with an area
   mass at or above that of the largest tracked shell trapped in the code (M = 3.47 in P0L6, trapped
   tracks from t = 122.2; verifier 2.3); or core's fix (outbox finder-false-accept-and-stall-p0l6) does. Then S1L's S1-S3 judged.
3. **C1 (iv), A2.** The effect within the first-order class named by a run that could refute it (for
   example data at the same amplitude whose density contrast is the first-order Zel'dovich one without
   the nonlinear zeta-delta relation, or a quarter-amplitude member with its lag predicted from A2H).
   A2 stays failed as written (0040 item 7, 0043 1(d)); what G3 needs is the cause, so that a lag is
   not read as halting physics.
4. **SCOPE section 7.** One triaxial phase-1 run to a found horizon with the bound of section 3
   (follows from 1 and 2).
5. The corrections of section 6.

If the group signs nonetheless, items 1-4 should be conditions before any production run of G3, and no
threshold amplitude should be compared with arXiv:2609.14218 before 3 is closed.

## 6. Corrections the lead makes (none changes a verdict above)

1. Note section V.A and C1 (i): "classifies every ball as the exact solution does ... bracket equals the
   exact bracket" holds under threshold_ball's entry-1 rule; under section II.B every member is
   undecided (run A-20261126-232456-42c8c8f).
2. Note section V.D: "outer shells follow the LTB solution through turnaround and collapse" -> to their
   turnaround (3.3 per cent), departing by up to 42 per cent in collapse; "resolved by many cells" is
   disputed (verifier: outermost trapped track at 3.4 finest cells); the finder fails from t = 121.4.
3. Note section V.B: "the finest member reaches the end of the test" -> with finite fields; state
   which non-spherical signal Table V uses (same cell; the invariant one is 3.5-15 times smaller).
4. Table V: orders of Delta t_det "1.5, 2" -> the ranges under interpolation (1.2-1.5, 1.75-2.1).
5. Note section V.C: "Eight particles per cell leave it unchanged" -> from t = 1 on (11-25 per cent
   higher at t = 0.25-0.75; tenfold at t = 0).
6. Note section VI ("Since the first evolutions ...", "Open at this stage: the ball needs a slicing that
   reaches its first trapped sphere ...") and the last sentence of the Summary are G1 text that the G2
   results contradict.
7. Fig. 7(a): tick labels from h (`fig_g2_convergence.py` line 41).
8. STAGE_REPORT.md regenerated; EVIDENCE.md header; C9 evidence text; CHECKLIST C18 set; OPEN.md adds
   P18 at tau 40 and AZ1's first clause; S1-S3 of S1L judged in periodic_threshold/JOURNAL.md; the
   verifier's six findings answered.

## 7. Reservations to carry (to the second G2 review, then to G3)

1. The constraint bound of SCOPE section 3 stands (0039 2(c)); every threshold reported until it is met
   is under a rule without it and must say so.
2. Ball radius: the detection-time order at 1.25 R0 is 0.63-0.69; quote orders with the radius and the
   interpolation spread.
3. Turnaround errors: estimator-dependent at mesh C and unchecked by any verifier.
4. Horizon mass: compared quantity differs from the source's; C below the tracked set's resolution.
5. The finder in an expanding periodic box: three runs, no convergent search after trapping; every
   periodic run that reads a horizon uses `diagnostics = true`, the status file, and core-v0.8 polishing
   or later.
6. A2: the triaxial lag is first order in the amplitude and unnamed.
7. Szekeres: P20 depends on the signal's definition; N256 at tau 40 has error equal to the invariant
   signal.
8. Carried from G1, still open in part: the Newtonian energy drift at sub-cell crossings (G1 item 7).

## 8. Runs and pending work

- Run of this review: A-20261126-232456-42c8c8f (processors, one core, completed, manifest committed by
  `nrpic-run`). No card run was queued; no queue entry of Track A is waiting (`nrpic-queue list`).
- Running, not mine: the full checksum pass of `nrpic-stage verify --full` started 14:18 PST (pid
  499738); its result goes to `VERIFY_RESULTS.md` when it ends and should be read by the lead.
