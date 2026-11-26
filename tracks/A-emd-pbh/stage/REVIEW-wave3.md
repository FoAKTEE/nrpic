# Lead's re-check of A-emd-pbh, wave 3 (batch 2b, 2026-11-21)

Lead session of batch 2b (window from 23:50 PST on 2026-11-20). No lead session ran between
the wave-2 lead (2026-11-15) and this one: the wave-2b lead did not return. Labels as in the
brief. Run ids are `nrpic-run` ids; outputs in `scratch/A-emd-pbh/<run id>/`.

## 0. What is reviewed

| Package | Session | State | Reviewed here |
|---|---|---|---|
| G1 verifier (`stage/G1/verifier/`, `VERIFIER.md`) | wave 2b | done | yes |
| `szekeres/` (reference solution, first AthenaK runs) | wave 3a | done | yes |
| `g1close/` (G1 close-out, note v1) | batch 1 | done | yes |
| G1 gate review (`stage/G1/GATE_REVIEW.md`) | batch 2a | done | yes (its checks), and its reservations answered in section 5 |
| `szekeres/` round 1 (card series) | wave 3 burst | cut 14:33 PST on 2026-11-20 | state; its stranded run closed and checked (L8) |
| `periodic_threshold/` round 1 | wave 3 burst | cut | state; its stranded run closed and checked (L9); four uncommitted files left alone |
| `verify_bh/` (independent check of BH-1R, BH-1) | wave 3 burst | cut, no registered run | state only |
| `runs_ball/` | batch 2b | finished during this session (00:29 PST, its entry 20) | yes: section 2b (L10-L13) |
| `conv_ball/` | batch 2b | running beside this session; card job 1 queued (Slurm 4776) | not reviewed (state in HANDOFF) |

Predictions L1-L9 were committed before any rerun (`../JOURNAL.md`, entry 2026-11-21T07:55Z,
commit 0f5972c4). Script `../analysis/review_wave3.py`. Runs: A-20261121-075605-351d611 (numbers
right, panel (a) of its figure empty because every difference was zero) and the repeat
A-20261121-075933-338a6ff with a legible figure, same numbers; figure
`fig_review_wave3.png` of the second run looked at.

## 1. Outcomes of the predictions

| # | What | Outcome | Verdict |
|---|---|---|---|
| L1 | G1 verifier `run_all.py` rerun against A-20261119-142905-c813c01 | all parts exit 0; six JSON files identical (217 + 101 + 137 + 79 row strings, 469 + 142 numbers, no difference); tallies 39/1/2, 19/19, 17/17, 12/12 | holds |
| L2 | g1close `check_findings.py` against A-20261120-222454-d16dbc6 | `findings.json` identical (133 numbers); the figure shows 9 of 14 points in the band | holds |
| L3 | g1close `wave1_sha256.py` against A-20261120-222620-0304d9d | `integrity.json` identical; 7 of 7 listings identical; 55 files, 0 mismatches | holds: the wave-1 outputs have not changed since 2026-11-20 |
| L4 | gate reviewer's `review_checks.py` against A-20261121-064537-2bcf310 | script sha256 4d72c147... as recorded; `review_checks.json` identical (111 numbers) | holds |
| L5 | Szekeres `run_ltb_limit`, `run_dipole_order`, `run_error_budget` against A-20261119-151501-9cff966, -151501-3e344a4, -153842-a1db5d6 | all three JSON files identical (22, 105, 393 numbers) | holds |
| L6 | Szekeres unit tests | 15 passed, 0 failed | holds |
| L7 | own reading of `N32/szk.cstat.hst` of A-20261119-152010-94a9461 | last finite record tau = 25.0 (largest abs(H) 60), first non-finite tau = 26.0; abs(H)_max already 1e-2 from tau = 1 and 0.58 at tau = 24 | holds (claim "fails between 24 and 28") |
| L8 | `prep_ppc1.json` of A-20261120-223422-8cc4241 | largest predicted relative E error of the deposit 1.2e-16 at every N; rest mass 1.91614944, 1.91616656, 1.91616676, 1.91616676 at N = 32 ... 256, successive differences 1.7e-5, 2.0e-7, 2.0e-10 | holds |
| L9 | P0L data run A-20261120-223123-f436c39 against the helper's prediction D3 | residuals 6.0e-12 (H), 1.0e-11 (M), at most 9.8e-12 per outer step; c = 0.088; delta_N max 0.118; alpha_min 0.805; inner iterations 29-32 (limit 60); largest offset 0.134 spacings | D3 holds |

Every rerun is bit-identical to its registered run, on processors, with the code at the tip of
the branch (only two docstrings of `szekeres/szekeres/model.py` changed since; checked with
`git diff --stat` before the run).

## 2. Per package

### G1 verifier (wave 2b)

- Confirmed: its recomputation reproduces exactly (L1), and its verdicts stand as written:
  39 confirmed, 2 WRONG, 1 NOT CONFIRMED in the ledger; criteria 19 of 19; Newtonian mode 17
  of 17; ball 12 of 12. The gate reviewer independently recomputed four further rows (A-D of
  GATE_REVIEW.md), and I reproduced those (L4).
- WRONG items and what the track did: (1) "median 0.86" for mu <= 0.15 is 0.843: corrected in
  the ledger (g1close, commit 2c115cb1), and the figure of A-20261120-222454-d16dbc6 shows both
  medians (looked at). (2) "common bang time for every shell": false in the taper (10.667 to
  13.588); corrected in the note (2c115cb1); the same figure shows the bang time rising only for
  R_i > 6.5. Both corrections confirmed by L2.
- NOT CONFIRMED: the predicted card-hours of the scouting runs (a cost model). The track keeps
  it as a prediction, not a result; at G2 it is compared with measured card time (`sacct`: job
  4642 27 min 8 s, job 4665 29 min 45 s, job 4748 1 min 28 s).
- Label defects (units M_0, thresholds row, checksum sentence): applied by g1close.
- Its open items for G2 (SR-2 turnaround estimator, a third resolution at fixed box, wave-1
  provenance): section 5, reservations 2, 3, 6.

### szekeres (wave 3a)

- Confirmed: the LTB limit against `expball` (agreement 4e-15 on the slice, 2.2e-14 in R(tau)
  up to 0.9 of the crunch), first-order dipole dependence (`fig_dipole_order.png` looked at:
  four quantities on lines of slope 1), the error budget, and the 15 unit tests, by exact
  reruns (L5, L6). The N = 32 geodesic-slicing run fails between tau = 25 and 26 by my own
  reading of its history (L7). Figures looked at: `fig_mesh_constraints.png` (order-4 stencil
  lines between slopes 2 and 4 steepening to about 4, Szekeres and LTB lines on top of each
  other, as claimed), `fig_code_geodesic.png` (E error at tau = 2 in the shell 1.2e-2 at N = 32
  and about 4e-3 at N = 64: the factor of about 3 per halving claimed).
- Not confirmed by me (not rerun, too long for this session): the symbolic checks
  (A-20261119-152233-d31f783, 200 s), the mesh-constraint orders (A-20261119-153846-81db254,
  600 s), the code runs other than the N32 failure time. The statement that the comoving
  Szekeres slice is conformally flat for arbitrary functions rests on exact random-point and
  polynomial checks in the run, not on a proof or a reference [TO VERIFY; kb request open].
- Wrong: nothing found. Failed predictions are on the package's record (P5 within 0.1 per cent
  of the crunch, P7 momentum order 3.61 < 3.7, P11 N = 32 fails, P14/P15 factor 3.2 not 4).
- Defect, cosmetic: the legend of the first panel of `fig_code_geodesic.png` covers the data.

### szekeres round 1 (cut)

Its file run A-20261120-223422-8cc4241 had ended with exit 0 and was left "running": closed by
me (`nrpic-run finish`, 14 files checksummed) and checked (L8). Choice eps = 0.2 and predictions
P16-P23 are committed (journal entries 7-8). Not done: the registered repeat of the eps choice
(P16), the card series N = 64, 128, 256 to tau = 40 (about 1.0-1.2 card-hours by the package's
estimate), the 8-particles-per-cell check. Nothing is queued.

### g1close (batch 1)

- Confirmed: the findings check and the integrity listing reproduce exactly (L2, L3). The note
  v1 was recompiled by the gate reviewer (12 pages, 0 undefined references, 0 overfull boxes);
  I did not recompile it again.
- Small defect, left: panel (c) of `fig_g1close_findings.png` (a run output, not in the note)
  has no y-axis label (it is the error of t_1).
- Requests of g1close to the lead, done in this session: STATUS/HANDOFF/JOURNAL (C20);
  `WRITING_GUIDE.md` exception 1 extended to `schem_dataflow.py` and Fig. 7 with a row in its
  figure table; C18 decided (section 4).

### G1 gate review (batch 2a)

- Confirmed: its checks A-F reproduce exactly (L4). Its script lived only in
  `scratch/A-emd-pbh/gate_review_G1/`; copied unchanged into `G1/gate_review/review_checks.py`
  (sha256 equal to its manifest's record), so the run can be redone from the repository.
- Its recommendation (PASS WITH RESERVATIONS once C20 is closed) is answered in sections 4-5.

### periodic_threshold round 1 (cut)

Its data run A-20261120-223123-f436c39 had ended with exit 0; closed by me and checked against
the helper's prediction D3, which holds (L9). Uncommitted and left alone (work in progress):
a one-line change of `JOURNAL.md` (time of entry D3), `inputs/peak_leak.athinput`,
`scripts/ltb_reference.py`, `scripts/ltbref.py` (LTB reference in box units, not yet run).
Remaining: the LTB reference run, the leak decks' smoke tests, predictions and the card job
(PLAN-wave3 row 6).

### verify_bh (cut)

No registered run, no verdict. Predictions P1-P5 are committed (99911b42) and its readers exist.
Its unregistered debug notes point at four places where the runs_ball claims about BH-1R and
BH-1 may not hold (first-detection mass about 2e-2 above the exact mass of its slice against
the claimed 3e-3; first trapped point of BH-1 at t = 11.25 rather than 11.0 depending on the
stencil; core |eps| at tau = 3.37 about 2.8e-3 and 5.3e-3 against the claimed bounds). They are
not results until its registered runs C1-C5 exist.

## 2b. runs_ball (batch 2b, finished during this session)

Predictions L10-L13 in `../JOURNAL.md` (written after the helper's entry 20, before my run);
run A-20261121-082814-6fadb30, script `../analysis/review_wave3_runs_ball.py`, figure
`fig_review_runs_ball.png` looked at (legend of panel c overlaps the markers; cosmetic).

- Confirmed: the BH-1R analysis (A-20261121-080558-02c3188) and the excision and breakdown
  analysis (A-20261121-081153-b92c08c) rerun with identical numbers (L10, L11; 1 652, 2 396,
  53 and 2 678 numbers). From the raw finder files with my own reader: BH-1R has a first
  apparent horizon at t = 10.875 (area mass 0.701, mean coordinate radius 0.44 M) and every one
  of the 41 later searches converges to t = 15.875 (L12); BH-1 at uniform M/8 never converges
  (L13). `bh_smr_horizon.png` (looked at): the finder mass follows the exact mass of the same
  slice to better than 1e-3 from t of about 11.7 M, after a first detection 2e-2 high; the
  largest 2m/R on the line passes 1 at t of about 10.9.
- Not confirmed by me: the exact-mass reference itself (runs_ball's `expball`-based mapping of
  the slice), the excision verdicts, prediction T's estimators and the fixed-box orders (entries
  18-19; reproduced only where L11 covers them). The independent check of BH-1R is verify_bh's
  (cut; its debug notes point at the first-detection mass, which this figure confirms is 2e-2
  high, so that point of runs_ball's claim stands as "2e-2 at first detection, below 1e-3 after
  t = 11.7").
- Wrong: nothing found. Its own failed predictions are on record (B1, B2, B5 refuted; S3
  second part refuted; R2 for SR-2 holds for the secular turnaround +0.0178 M and fails for the
  local maximum +0.035 M, entry 18).
- Defect noted for its next round: runs_ball attributes BH-1's missed detection to the start
  radius (entry 11, [JUDGEMENT]); core's message points at `hmean_tol` (section 3). Neither is
  tested; one finder rerun on the BH-1 M/8 data with BH-1R's settings and `hmean_tol_0 = 1e30`
  decides it (needs a restart file or a rerun of the card job).
- My own fault, on record: the rerun's exit status 1 came from my redirect of `--figdir` onto
  the output directory (SameFileError after the JSON files were written).

## 3. A finding for the packages in progress (not from a helper)

Core's message 20261120T223017Z (item 1) says that `<fastflow> hmean_tol_<n>` is compared with
the surface integral of the expansion, not its mean, so a value of 100 can stop every search at
its first flow iteration. Every deck of this track carries `hmean_tol_0 = 100` (`runs_ball/*`,
`conv_ball/decks/*`, `periodic_threshold/inputs/peak_smr4.athinput`). In BH-1 at uniform M/8
(`bh_n256` of A-20261119-144419-13d5601, initial radius 3 M) every search in
`ball.horizon_summary_0.txt` ends at iteration 4 with nan; in BH-1R (initial radius 1 M) the
finder does converge from t = 10.875. So "no finder detection at uniform M/8" is not evidence of
no horizon [JUDGEMENT; to be settled by the finder's status file]. Action for runs_ball,
verify_bh and conv_ball: set `hmean_tol_0 = 1e30` and `<fastflow> diagnostics = true` (core-v0.5)
in every new deck, and base the BH-1 verdict on the line diagnostics until a finder rerun exists.
Core's item 3 applies to the periodic decks: `alpha_exc` is an absolute lapse, of order a there.

## 4. Gate G1: what this session decides

- C18: PASS (lead's judgement). The fresh verifier recomputed the ledger, the criteria and the
  Newtonian mode; the gate reviewer recomputed four of the five rows added in note v1; L1 and L4
  show both recomputations reproduce. Rows recomputed by nobody independent, named in OPEN.md:
  SR-2 compactness on the axes and the horizon count, the predicted card-hours, the four
  cross-check differences.
- C20: closed by this session's STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md (the sentences
  g1close and the reviewer listed are corrected: G0 passed; C11, C18 closed; 9 of 14 points;
  41 of 41 with its history; units M_0; SR-1 breakdown times with their criterion; SR-2
  turnaround estimator-dependent).
- Stage package regenerated with `nrpic-stage collect`, `verify`, `report` (G1/STAGE_REPORT.md).

## 5. The gate reviewer's reservations, and what the track does

| # | Reservation | Answer |
|---|---|---|
| pre-1 | close C20 | done in this session (section 4) |
| pre-2 | stranded manifests | all four closed: A-20261120-223123-f436c39 and A-20261120-223422-8cc4241 by me (both exit 0), A-20261119-164634-f1fe887 and A-20261120-223310-a9ce31a by the runs_ball helper of this batch (both completed); no waiver needed |
| pre-3 | verify on a clean commit | run in this session (G1/VERIFY_RESULTS.md); `clean` fails only on files of packages in progress (periodic_threshold, and the two helpers running beside me) |
| 1 | no horizon yet | stays the main G2 risk; BH-1R (one static level, M/16) has a finder detection from t = 10.875 (raw file; runs_ball's registered analysis is in progress); conv_ball designs the three-mesh series around it |
| 2 | SR-2 turnaround estimator | runs_ball entry 13 (prediction T) is the window-independent estimator; its run is runs_ball's task in this batch; until then the note quotes the three-point value only and makes no pass/fail statement |
| 3 | mesh against box | fixed-box job A-20261120-223310-a9ce31a (Slurm 4748, 1 min 28 s) finished all three members with rc = 0, each to t = 24 (the dx = M/2 member: 192 cycles in 30.6 s, its `athena.log`); its analysis against prediction F is runs_ball's task in this batch. The constraint maximum is located there and in conv_ball, before G2 claims "constraints behave" |
| 4 | constraints of data set 2t as a whole | G2 item, kept in OPEN.md; core-v0.5 region norms (`<particles> region_dcycle`) give AthenaK's own t = 0 norms inside and outside the ball |
| 5 | rows nobody recomputed | listed in OPEN.md (C18) |
| 6 | wave-1 provenance | L3: unchanged since 2026-11-20; rerunning the wave-1 producers through nrpic-run is a G2 next action (minutes on processors) |
| 7 | Newtonian energy drift | cause named by core (message 20261121T081909Z, item 1; `newtonian_mode.md` section 7 on core/newton-2): the history's W is not an invariant of the scheme unless deposit and gather kernels coincide; the drift over a shell crossing is a property of the space discretisation (unchanged at half the step); with `deposit_shape = pcs` and `interp = bspline` the constant holds to 3.7e-6. The track re-tests one scan point with those settings before G2 [TO VERIFY by our own run] |
| 8 | "41 of 41" with history | STATUS.md quotes it with the two restated bands, two diagnostics and F5 partly refuted |
| 9 | architecture schematic names core-v0.3 | redraw against core-v0.5 before G2 (note scripts; HANDOFF next) |
| 10 | horizon-mass criterion may be unreachable | RISKS row 17 kept; conv_ball reports the error with its N and dx dependence; if it stalls the track asks the orchestrator to restate the criterion (to be sent with G2 evidence, not now) |
| note | App. B cites an unfinished manifest | A-20261119-164634-f1fe887 is finished (runs_ball, 00:05 PST, 2026-11-21) |

## 6. Batch 5 (2026-11-21 afternoon, lead; decision 0025 items 4-5: cards first)

Reviewed only what decided the next runs, from the artefacts.

| Package (batch) | Confirmed | Not confirmed | Wrong | What the track does |
|---|---|---|---|---|
| conv_ball (2b, finished 12:02 UTC) | the registered final table and figure of A-20261121-120257-a2eb839 (convergence.md, fig_convergence.png looked at) carry the reported numbers: ddet 0.193, 0.068, 0.017 M; dmmed +7.4e-3, -2.1e-3, -2.1e-4; dm at first detection +4.5e-2 on B; boundary leg identical | the analysis was not rerun by the lead (decision needed only the numbers); the G2 reading of JOURNAL entry 12 still lacks a second agent | none found | mesh B (M/32) is taken as the working mesh of the scan; the missing C-R1.25 member is queued (threshold_ball queue line 12, core_gauge as the series) |
| verify_bh (3) | its four findings bear on the scan: horizon-mass errors are judged on the median over detections, not at first detection (+2e-2 at BH-1R, +4.5e-2 at conv_ball B agree that the first-detection mass is not a usable measure); the C3 clock item is decided REFUTED (-0.046 M), as section 4 recommends | slice-or-finder origin of the first-detection excess: stays [TO VERIFY]; the scan writes field dumps at tau_AH - 2, tau_AH, tau_AH + 4 and lines every 0.25 M, from which the finder's radius can be checked on the line at first detection (the verifier's request) | "non-finite near 15.5" (runs_ball) is 15.03: corrected in the record by the verifier; nothing further | G2 tables state the particle selection of shell errors (edge band separately); int_E deficit of BH-1R at t = 0 (7.9e-4) posted to core (outbox bh1r-inte-deficit-two-levels) |
| periodic_threshold (3) and its card job 1 (Slurm 4799, ran 07:16-07:21 PST) | both members failed (exit 3, guard); the lead's reading A-20261121-203120-eaba95f: a common jump of norm(H) by ~1e4 at t = 2.506 in both members | cause (deck/step vs data) | P3, P4, S1, S2 refuted (periodic_threshold/JOURNAL.md, entry 20:44Z) | no periodic long run; request to core periodic-relaxed-lapse-blowup; note to B (do not take the deck) |

New package threshold_ball (this session): design run A-20261121-202520-3164672, data run
A-20261121-202812-cae4436 (nine data sets, all rc 0), smoke tests A-20261121-203156-d094c56
(failed: decks lacked `diagnostics`; fixed by copying the decks into the package) and
A-20261121-203211-6d3ce73 (exit 0), predictions T1-T6 committed before the first submission.
Twelve card runs queued behind a sequencer; at 12:43 PST two were submitted
(A-20261121-204149-c48bd33, Slurm 4838; A-20261121-204250-0bf45c7, Slurm 4845).

Gates: G0 and G1 are signed (coord/GATES.md); nothing to redo in stage/G0 and stage/G1. G2 is
not ready for review: the threshold scan and C-R1.25 are on the cards, the second-agent check of
conv_ball's G2 reading is owed, the architecture schematic still names core-v0.3.

## 7. Batch 11 (2026-11-24, lead; analysis round of the card runs, decisions 0026, 0027, 0030)

No helper package finished since batch 7; what ran were the sequencer's twelve card runs (queue
lines 3-15) and nothing else. The lead closed them, wrote the analysis scripts, ran every analysis
registered from the run outputs, looked at every figure and judged against predictions written
before the runs. Per package:

| Package | Confirmed (with run) | Not confirmed | Wrong / refuted | What the track does |
|---|---|---|---|---|
| threshold_ball | T1-T3 hold (A-20261124-131120-5c974ce): persistent horizons on mesh B for delta_c >= 0.35; ddet <= 0.14 M; the code's finite-duration bracket (0.40, 0.42] at t_end = 45 equals the exact one, the interpolated threshold 0.4103 equals the exact 0.4103 on mesh B; slice-or-finder answered (the excess at first detection is in the slice) | mesh C at threshold (C-d0.42 still running; C-d0.40 not run); the A-mesh guard stop's cause | T4's reason (A finds the horizon, then stops at the guard), T5 at its 0.02 bound (ball-radius effect on C 0.024 M), T6 (A guard stops; line constraint ratio 0.11-0.21 at t = 0, 0.3-3 later, bound 0.1) | C-d0.42 continued in place; C-d0.40 queued (T7); processor test G1-G3 of the guard stop running; orch asked to rule on the constraint bound |
| periodic_threshold | the cfl 0.5 remedy on the refined mesh (Q1a, Q1c, Q1d, Q2, Q3; A-20261124-130507-10510ac); P1 (far lapse to 2.2e-5); spherical symmetry kept to 1e-12 | S1-S3 (S1L at t = 66 of 220, continued); F2 (finder restarts) partly read | Q1b (data's own H_max 0.49 at t = 0), P2 in part, P3 (no horizon found), P4 in part, F1 (slice traps only from t = 132, at r ~ 0.075, under four finest cells) | outcome posted to core; six-level rerun peak_leak6 queued with predictions D0-D5 |
| conv_ball / G2 | constraint norms on three meshes and three particle numbers (A-20261124-132249-2e6b5f2, -132342-d5dc06e) | | K and K2 refuted: the early constraint floor falls with neither mesh nor particle number | C3 marked FAIL in stage/G2; smoothed-edge test proposed |

Own mistakes of this session, no damage: a first table of the journal gave the constraint-ratio
range as 1.6-3.8 (it is 1.6-5.9; corrected from threshold_series.json before the entry was used).

## 8. Batch 17 (2026-11-25, lead; analysis round of the queue entries that ended overnight)

No helper packages finished since batch 11; the lead's own work is checked from the artefacts.
- C-d0.42 (q0012): checked from the run's own files, not from a summary: chain events.log ends
  "finished: time=5.100000e+01 cycle=13056 ... DONE (tlim)"; the raw status file shows the first found
  search at t = 45.906 and every later search found (163 of 1119). analyse.py numbers agree with the
  raw file (first_found_t 45.906, n_found 163). Figures looked at: fig_threshold_slice_or_finder.png,
  C-d0.42_horizon.png, B-d0.42_horizon.png, fig_t4_common.png. CONFIRMED: black hole, tau_det 43.705,
  bracket upper end on M/64. WRONG (prediction, not code): T4's halving bounds were below the
  measure's resolution; recorded as refuted, the common-window measure beside it, labelled as a
  measurement made after the figures.
- t4_common.py defect (NaN for C, finder-row spacing taken for the search interval) found by reading
  its own output; fixed and rerun; the defective run stays on record.
- Not confirmed this session: G3 of the A-mesh guard-stop test (A-20261124-132016-ecf12c3); K4.

## 9. Batch 19 (2026-11-25, lead; the fresh verifier of C18 and K4)

Package checked: `stage/G2/verifier-c18/` (fresh verifier, batch 18; report `stage/G2/VERIFIER-C18.md`).
The lead did not rerun the verifier's own scripts; it answered each finding with its own registered
analysis from the card outputs (`threshold_ball/scripts/c18_answer.py`, run A-20261125-151126-7f79a83;
the two first attempts A-20261125-150848-401a271 and A-20261125-150943-69ea256 failed on a member
without a status file and in the figure, kept on record) and looked at fig_c18_mass_bracket.png.

| Verifier finding | Lead's recheck | What the track does |
|---|---|---|
| Classification, persistence times, tau_det, bracket reproduced | CONFIRMED from horizon_status_0.txt for every member; B-d0.35 has 14 isolated finds before 58.3125; C-d0.42 163 of 936 unique searches (batch 17's "1119" counted restart repeats) | READMEs keep the numbers; the "1119" corrected |
| Summary file repeats stale finds (5a) | CONFIRMED: A-d0.42 and A-d0.40 have 16 of 19 summary rows repeated; the committed analysis built A's mass medians (-3.8e-2, -4.6e-2) on them: WRONG | A medians withdrawn; brackets of 3 finds instead |
| Mass medians of B-d0.42, B-d0.40, B-d0.35, C-d0.42, conv_ball A not reproduced (NOT CONFIRMED by the verifier) | CONFIRMED the verifier: the committed convention (running median of 9, sign change linear in R_i) reproduces the README values, but they lie outside the bracket between the outermost trapped tracked particle and the next one outward; my brackets agree with the verifier's within 6e-4 (largest: C-d0.42 upper end 5.9e-3 against 6.5e-3) | READMEs and checklist C2, C8 carry the brackets; values below the bracket width are not measurements; C8's verdict (order 1e-3 on M/64) stands |
| ddet interpolation spread at the core edge (5e) | CONFIRMED and larger than I predicted (P12d refuted): 0.02-0.08 M on B threshold members over three interpolations, 0.058 M on C-d0.42, 0.001 M on conv_ball C | conv_ball orders stated as 1.2-1.5 and 1.75-2.1; T4's time half fails under every interpolation |
| Exact mass resolution of the tracked set (5f) | CONFIRMED: bracket widths 1.1e-3 to 9.9e-3 relative | T4's mass half is not decidable; named in OPEN.md; a denser tracked set near the core edge for G3 |
| C3 FAILED, also at t = 0 (5b) | not recomputed at t = 0 by the lead; K4 (below) consistent | C3 stays FAILED as written |
| Time measure (5g) | CONFIRMED: outer layers 46.52 M, core edge 43.76 M at B-d0.42's first detection | the gate text (CHECKLIST C1, threshold_ball README) names the core-edge proper time |
| A-R1.35 ddet 0.175 vs 0.164 | not rechecked | left open in conv_ball README and OPEN.md |

K4 (threshold_ball entry 10; run A-20261125-120525-8fb946e on processors, analysis A-20261125-150851-5545f8e,
fig_k4.png looked at): K4a, K4b, K4c HOLD (step 0.2 per cent, source extrapolation 0.8 per cent, card vs
processor 1e-3). K4 is not the smoothed-edge test named in decision 0039 item 2(c); that test has not run.

A2 (decision 0039 item 2(a)): the lead decides that S1L (A-20261123-025907-97bab8d, 20 particle snapshots
through the Zel'dovich epoch) serves as A2, with the prediction written before any snapshot is read
(periodic_threshold JOURNAL 2026-11-25 07:15 PST); no card time; the fallback (one oblate member, <= 6
card-hours) only if the snapshots cannot bracket the first crossing within the band.

## 10. Batch 20 (2026-11-25 morning, lead; processors only; decision 0040 items 6 and 7)

No helper package finished since batch 19; this section records the lead's own two tests, each with its
prediction committed before its runs (threshold_ball entry 13; periodic_threshold JOURNAL 2026-11-25 08:10 PST),
and what the track does about the open verifier finding on C3 (VERIFIER-C18 5b: "C3 FAILED, also at t = 0").

### 10.1 C3, the smoothed-edge test (in the place of K4, 0040 item 6)

| Step | Run | Outcome | What the track does |
|---|---|---|---|
| Data: `--edge-w` on data set 3 | A-20261125-160221-b68396f | FAILED: expball needs R2 <= R_b - w, so data set 3 admits w <= 0.204 M only (it has 0.168) | members S1 (smooth core, outer edge kept), S2 (smooth core, outer taper 0.8 M) instead; amendment dated before any AthenaK run |
| Data S1, S2 | A-20261125-160436-462452d | completed | lattices nestA, nestB |
| t = 0 slices on M/16, M/32 (PCS, the decks as they are) | A-20261125-160633-594a474, analysis A-20261125-160849-8c01b54 (fig_edge.png looked at) | ratio 0.278 / 0.185 / 0.134 (top hat / S1 / S2) on M/16, 0.174 / 0.146 / 0.116 on M/32: (a) REFUTED; the volume momentum norm of S2 falls 60-fold, (c) HOLDS | the momentum floor is the jumps [VERIFIED]; the Hamiltonian remainder is not |
| Test D: cloud at t = 0 | A-20261125-161039-cb046d7 (fig_edge_d.png looked at) | CIC 0.0064, PCS without compensation 0.089, repeat identical: the remainder is the PCS deposit at the level boundaries (spikes 0.33-0.61 against 0.44 in 16 pi E at x = 0.9-1.3) | request to core (outbox pcs-deposit-refinement-boundary) |
| Test F1: S2 with CIC, t = 0 | A-20261125-161154-62ce3dc phase 1, analysis A-20261125-161248-eecc672 | 6.4e-3 (M/16), 5.8e-4 (M/32): order 3.5; volume Hamiltonian norm order 4.0: HOLDS | F2 (evolution) read next session |
| Test F2: S2 with CIC evolved (M/16 to t = 5, M/32 to t = 1) and the PCS twin | A-20261125-161154-62ce3dc, A-20261125-160633-594a474 (running), partial reading A-20261125-165215-e3fe168 | REFUTED on M/16: ratio 0.129 at t = 1 (0.156 at 1.25); volume norm 57 times below the top hat's; PCS twin 0.53 at t = 4 | the mesh leg S2c-B decides whether the evolution's floor falls with the mesh |

Judgement under 0039 item 2(c): at t = 0 the floor of the top-hat members comes from the density jumps (momentum
constraint) and from the PCS deposit at the static refinement boundaries (Hamiltonian), shown on two meshes by runs
that could have failed. But the evolution rebuilds a floor of 0.1-0.6 within 1-5 M on M/16 whatever the data and the
cloud (F2 refuted). Smoothed members do NOT meet the bound; C3 stays FAILED, and unless the mesh leg (S2c-B) shows the
violation falling with the mesh, the review decides with the failure on record (0039 item 2(c)). The bound is not moved.
Two of the session's runs were stopped by hand to free cores (S1-A, S2-B with PCS, PIDs 2597153, 2597154), on record
in entry 13.

### 10.2 A2, the Newtonian control (0040 item 7)

| Step | Run | Outcome |
|---|---|---|
| Second derivation of the reference | periodic_threshold JOURNAL 08:10 PST | D = a on every scale for dust in EdS; a_H = r_m^2 = 6; lambda_z = 0.063: first crossing 4.35 t_H (DESIGN's 4.2 with 0.064) |
| N-z: S1L's positions, equal masses, Zel'dovich velocities, Newton (64^3 Fourier) | A-20261125-160633-e38d321; A-20261125-162905-d0ef1d7, -162951-bb0fb26 (figures looked at) | z first at 4.55 t_H, follows Zel'dovich to 0.02: AZ1 narrowly refuted (band edge 4.5) |
| N-f: S1L's file as it is under Newton | same run; A-20261125-165125-1640161 (figure looked at) | 0.43 t_H: direction holds, band refuted (the psi^6 masses read as a density excess of order one) |
| N-z128 | same run, continuing | next session |

What the track does: the lag of S1L (6.35 t_H, factor 1.46) is not in the reference, the clock, the reader or the initial
positions; it lies in the relativistic evolution or in the coordinates of the GR run, not named further. A2 stays
FAILED as written. Next: a gauge-invariant crossing measure in S1L or a GR member with zero shift, prediction first.
P0L6 (q0013): its chain has not ended (Slurm 5296 pending), so the find at t = 118.1 was not read this session.

## 11. Batch 23 (2026-11-25 evening, lead; analysis round of the entries and processor runs that ended)

No helper package. Ended since batch 20: q0013 (P0L6), q0040 and q0041 (Szekeres series), and the session's own
detached processor runs. Each was closed (`nrpic-run finish`) before its analysis, judged by a registered analysis
against the prediction written before it ran, and its figure looked at. Predictions written this session before any
reading: threshold_ball entry 14 (G), periodic_threshold 2026-11-25 18:21 PST (A2X).

| Run (closed as) | Prediction | Analysis | Outcome | What the track does |
|---|---|---|---|---|
| S2c-A, S2c-B: A-20261125-161154-62ce3dc (completed) | G (entry 14) | A-20261126-022624-c663e0f, fig_edge.png | REFUTED: orders 1.5, 1.07 at t = 0.25, 0.5 but 0.34, 0.36 at 0.75, 1.0; S2c-B 0.101 at t = 1 | C3 FAILED as written; defect to explain (0039 2(c)); next: particle-number leg of S2c-A on processors, prediction first |
| PCS twin A-20261125-160633-594a474 (failed, exit 143: S1-A, S2-B stopped by hand in batch 20) | F2 (twin) | same | S2-A reaches 0.64 by t = 5 | on record |
| N-z128: A-20261125-160633-e38d321 (completed) | AZ1 second clause | A-20261126-022631-dafbb4f, fig_a2_compare.png | REFUTED: 3.62 t_H against N-z 4.55 (26 per cent) | the converged Newtonian time is ahead of Zel'dovich; GR lag factor 1.65-1.9 |
| S1L snapshots (A-20261123-025907-97bab8d) | A2X | A-20261126-022220-99b7be8, -022338-0edc27c, -022438-a08cc5f (bound empty), -022545-5af99fb; fig_a2x.png | (i) holds: J changes sign between 6.19 and 7.21 t_H; (ii) not decidable as written; decided by the probe particle on a crossing worldline: (5.99, 6.80] t_H | lag is not a coordinate effect; no card member for it; candidate (nonlinear zeta-delta at zeta 0.3) to test at half amplitude, prediction first |
| P0L6: A-20261125-044641-7d5bd16 (completed, 4.87 card-hours) | D1-D5 | A-20261126-022753-f9e9c40, three figures | D1, D5 hold; D2, D3, D4 refuted; the 't = 118.1 found' is a false acceptance | request to core (finder); C1 (ii) stated as a failure on record |
| Szekeres N64, N128: A-20261125-213939-0ad9f29 (failed, guard exit 3 at tau 30.25, 37.47); N256: A-20261125-231808-0784bc9 (stopped at tau 21.2, MAX_SEGMENTS = 1 of the queue entry) | P17-P21 (entry 8) | A-20261126-022804-0bc68c2 | see szekeres/JOURNAL entry 11 | SZK_REVIEW_PLACEHOLDER |

The verifier findings of VERIFIER-C18 were answered in batch 19; nothing new from a verifier this batch. Card time
used by this session: none (q0013, q0040, q0041 were dispatched earlier: 4.87 + 0.40 + 0.83 card-hours).
