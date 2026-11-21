# GATE_REVIEW.md: independent gate review of G1 of A-emd-pbh

Reviewer of batch 2a (decision 0019 item 3), fresh context, 2026-11-20 22:29 to 23:00 PST
(2026-11-21 06:29 to 07:00 UTC). I produced none of the work under review and read the
track's conclusions only after opening the evidence they name. No tag `stage/A-emd-pbh/G1-pass-*`
existed when I started (`git tag -l`: only `stage/A-emd-pbh/G0-pass-20261119`).

**Read.** `CLAUDE.md`; `coord/CHARTER.md` to "Owners" and the track sheet 9.4 (G1: "the
constraint residuals of A-pre-1 converge at the expected order; the prediction table of
A-pre-2; the scan design from A-pre-3"); brief lines 674-686 (gate table: G1 "baseline results
obtainable without the NRPIC coupling; the analysis pipeline validated on them; interface
proposals submitted"); decisions 0012, 0013 (Track A: scan design met on the reference-based
design), 0016, 0019; the package `stage/G1/` (STAGE_REPORT, CHECKLIST, EVIDENCE, OPEN, REVIEW,
STATUS, README, VERIFIER, the verifier's JOURNAL), `g1close/JOURNAL.md`, `criteria/JOURNAL.md`
(outcomes F, T2 repeat), `runs_ball/JOURNAL.md` entries 11-15, the owner's `STATUS.md`,
`HANDOFF.md`, the end of `JOURNAL.md`, `note/main.tex` App. B and `note/tables/ledger.tex`.

**Opened as evidence** (each named below at the criterion it serves): the manifests and
outputs of the T1 convergence runs, the criteria check runs, the data-set run, the Newtonian
analysis, the SR-1/SR-2 raw histories and trajectories; eleven figures, each looked at with the
Read tool.

**Ran.** (1) `harness/bin/nrpic-stage verify A-emd-pbh G1` in full, with output checksums
(section 3). (2) My own checks, registered: run A-20261121-064537-2bcf310 (`nrpic-run`,
2 cores, 5 s, exit 0; script `scratch/A-emd-pbh/gate_review_G1/review_checks.py`, sha256
4d72c147... recorded in the manifest; it imports nothing of the track but the figure style),
after a failed first attempt A-20261121-064515-aa13c8f (section 1). (3) A recompile of the note
with the manuscript checker in a scratch copy of the committed tree
(`scratch/A-emd-pbh/gate_review_G1/notecheck/check.log`). No card-hours used.

## 0. Verdict

The three track criteria of G1 and the three common criteria are met by evidence I opened, and
the numbers I recomputed agree with the package. One package item fails: **C20**, the owner's
`STATUS.md`, `JOURNAL.md` and `HANDOFF.md` were last changed on 2026-11-15 (commits 8737de9b,
510fdb96) and still state that G0 is not passed and that C11 and C18 are open, and repeat the
sentence "14 scan points within 6.3e-4 of the ellipsoid" that the package itself corrected
(9 of 14; my check E below). The automated verify fails on `clean`, `sync` and `runs`, none of
them a defect of this package (section 3). **Recommendation: PASS WITH RESERVATIONS, to be
signed when the lead has closed C20; no science item blocks the gate.**

## 1. My own checks: predictions and outcomes

The predictions, with what would refute each, are the first version of this file (commit
aa13c8f2), committed before any check ran; in short: every value equal to the claim at its
printed precision (B within one history interval, C within 0.01), D below 1e-12 and 1e-10, E
9 of 14, F no checksum mismatch. The table gives the outcome of each. The first attempt,
run A-20261121-064515-aa13c8f, failed (exit 1) after part A: the data-set run
A-emd-pbh-20261115-130609-947c898 of wave 1 has no `sha256sums.txt`; the script now checks such
files against the integrity listing of run A-20261120-222620-0304d9d (recorded in commit
2bcf3104 before the rerun). Rerun A-20261121-064537-2bcf310: every raw file read matched its
recorded sha256 (check F).

| # | Quantity (row of `note/tables/ledger.tex`) | Claim | Mine (run A-20261121-064537-2bcf310) | Outcome |
|---|---|---|---|---|
| A | SR-1, largest abs(H) on the mesh at t = 20 M_0, dx = M_0, M_0/2, M_0/4 (`ball.cstat.hst` column 9 of runs A-emd-pbh-20261115-155056-ec1b816, -153843-7172b66, -164539-0b18e84) | 0.24, 0.051, 0.04 | 0.2428, 0.05126, 0.04007 | prediction holds |
| B | SR-2, first t with abs(alpha_c/a(tau_c) - 1) > 0.1, dx = M_0, M_0/2, M_0/4 (`ball.nrpic.hst` columns 13, 15 of -155056-ec1b816, -153845-7172b66, -164541-0b18e84), against my own cycloid of the core | 6.5, 6.625, 6.625 | 6.5, 6.625, 6.625 | holds |
| C | SR-2, dx = M_0/2, largest abs(alpha_c/a - 1) for t <= 15 | 0.39 | 0.3912 | holds |
| D | SR-1, dx = M_0/2, 1705 tracked particles over the whole record (t = 0 to 33.25): largest abs(r/r_0 - 1); largest abs(tau - t)/M_0 | 8.2e-15; 6.3e-12 | 8.22e-15; 6.30e-12 | holds |
| E | Newtonian first-collapse error t_1 in [+2.2e-4, +6.3e-4] (`newton_scan.csv` of A-emd-pbh-20261115-164420-4528861) | 9 of 14 | 9 of 14; outside: two 3.4e4-particle controls (-2.40e-4, -4.63e-4), two 64^3 controls (+8.77e-4, +1.54e-3), the spindle p = -0.2 (+1.51e-3) | holds |
| F | sha256 of every raw file read | as recorded | 10 of 10 match (9 against the run's own list, 1 against the integrity listing) | holds |

My reference for B and C: the core of data set 2t is homogeneous closed dust with common bang
time t_i = 10.667 and turnaround tau_ta = 16.894 after the initial slice (data-set JSON of run
A-emd-pbh-20261115-130609-947c898); with age = (t_i + tau_ta)(eta - sin eta)/pi and
a/a_i = (1 - cos eta)/(1 - cos eta_i) it gives R_max/R_i = 1.33980, crunch at tau = 44.4542 (the
data set's own 44.4542) and the conformal-time coordinate time of turnaround 13.8229 (ledger
13.82), all in the log of the run. Figure `scratch/A-emd-pbh/A-20261121-064537-2bcf310/
fig_review_checks.png`, looked at: top left H_max(t) of SR-1 with the t = 20 points on the
curves and the breakdown after t = 30 (dx = M_0) and 33 (M_0/2); top right the lapse departure
of SR-2, which crosses 0.1 near t = 6.5 on three nearly identical curves; bottom left the
tracked-particle residuals rising smoothly to the ledger values; bottom right the 14 Newtonian
points with the band.

Two observations from this run for G2, not defects of G1 [JUDGEMENT]: the SR-1 constraint
maximum at t = 20 falls only from 0.051 to 0.040 between dx = M_0/2 and M_0/4 (the M_0/4 run also
has half the box), so where it sits must be found before G2 claims "constraints behave"; and the
SR-2 lapse departure is the same at all three resolutions, i.e. a property of the gauge (the
lapse pulse of risk 1), not of the resolution.

With A to D, four of the five Table IV rows that OPEN.md item 2 lists as not recomputed by a
fresh verifier are now recomputed independently. Still not recomputed by anyone independent:
SR-2 "largest 2m/R on the axes 0.34; apparent horizons found 0" (needs the field dumps), the
predicted card-hours (a cost model), and the four cross-check differences (read from
`crosscheck.json` by the verifier, not re-run).

## 2. Criterion by criterion

| # | Criterion | Verdict | Evidence I opened, and what it shows |
|---|---|---|---|
| C1 | Baseline results obtainable without the NRPIC coupling | PASS | Data-set JSON of A-emd-pbh-20261115-130609-947c898 (total mass 1.00959, first trapped sphere tau 44.349, core crunch 44.454); `expball/figures/fig_exact_shells.png` (shells, trapping, star at the first trapped sphere) and the cross-check figure of A-20261115-130257-a7374a4 (two generators agree at 1e-15, cycloid surface shell, data-set shells), both looked at; criteria results of A-emd-pbh-20261115-161813-6c820fb; Newtonian references in `newton/`. All obtained without AthenaK's coupling. |
| C2 | The analysis pipeline validated on them | PASS WITH RESERVATION | The verifier's `figs/fig_v_ball.png` (run A-20261119-142905-c813c01, looked at): SR-1 core error at tau = 16.894 is 7.6e-4 at dx = M_0/4, the run's core shells follow the verifier's own cycloid; my checks A-D reproduce the wave-2 rows from the raw files. Reservation: the SR-2 turnaround number is estimator-dependent (verifier finding 6) and `runs_ball/JOURNAL.md` still carries "R2 ... FAILS" for it; the window-independent estimator of runs_ball entry 13 (prediction T) is written but not yet run (entry 15, paused). |
| C3 | Interface proposals submitted | PASS | `outbox/`: 7 messages of 2026-11-15T13:20Z and 18 of 18:37Z, to core (scouting runs, Newtonian mode and ball data, phase-1 generator, gauge, refinement, non-finite stop, step limit, periodic finder, constraint solve), orch, kb, B and D. |
| C4 | Baseline data and figures | PASS | Outputs of the runs above in `scratch/A-emd-pbh/<run id>/`, checksummed (section 3); figures under `expball/figures/`, `newton/figs/`. |
| C5 | Interface documents | PASS | `stage/G1/STATUS.md` section 3 (specification of SR-1/SR-2 with predictions and what refutes them), `newton/SCAN.md` sections 4-5 (inputs, acceptance quantities), `gauge/GAUGE.md`, `gauge/DIAGNOSTICS.md` present. |
| C6 | T1: constraint residuals of A-pre-1 converge at the expected order | PASS WITH RESERVATION | `convergence.json` of A-emd-pbh-20261115-130402-f5566fb: flat ball momentum L2 orders 2.00 / 4.00; taper over all cells 1.99 / 3.90 (pairs before 1.85, 1.96 / 3.43, 3.77); top hat smooth region 2.00 / 4.00 (H and M); of A-emd-pbh-20261115-122117-aa1c84d: smoothed top hat 256 -> 512 order 4: 3.98 (H), 3.94 (M). Figures `fig_constraint_convergence.png` (both runs) looked at: the smooth-region and taper lines follow h^2 and h^4; the all-cells momentum norms of every model with a sharp edge do not converge (order -0.50), as the track states. Reservation: the evolution data set 2t (smoothed top hat plus taper) is covered by its two parts, not tested as a whole over all cells; AthenaK's own t = 0 constraint norms of the format-2 table (OPEN.md item 5) have no resolution series yet. |
| C7 | T2: the prediction table of A-pre-2 | PASS WITH RESERVATION | `example_tables.txt` of A-emd-pbh-20261115-120425-80492f8: rows R1-R9 per parameter set with source locators. `results.json` of A-emd-pbh-20261115-161813-6c820fb (44 records: 37 pass, 3 fail T2.6a-c on a nan, 4 diagnostics) and of -163358-9b2d048 (20 records: 17 pass, 3 diagnostics): with T2 taken from the repeat, 41 checks pass and 4 are diagnostics, as claimed. Reservation (wording): the tally combines two runs; two wave-1 failures (T2.4a, T2.4c) pass after their agreement band was restated to the window the paper plots, two (T1.2b, T2.2d) became diagnostics after a rounding explanation, and part of prediction F5 was refuted (1.0416 at sigma_H = 0.017); all on record in `criteria/JOURNAL.md` outcomes F and the T2 repeat, confirmed in value by the verifier. Quote "41 of 41" with that history. The Monte Carlo checks (T1.3-T1.6, T5.2-T5.3) are confirmed in tally only. |
| C8 | T3: the scan design from A-pre-3 | PASS WITH RESERVATION | Met by decision 0013 on `newton/SCAN.md` sections 1-6; the Newtonian-mode runs exist as well: `fig_newton_scan_summary.png` and `fig_scan_hoop_time.png` looked at (hoop amplitudes on the ellipsoid curve; t_1 errors below 0.16 per cent); my count E: 9 of 14 points in the corrected band. Reservation: the energy drift during sub-cell crossings (1.1e-3 to 9.3e-3, spindle 3.0e-2; analysis A-emd-pbh-20261115-164420-4528861) has no established cause, and the full-relativity range of SCAN.md section 8 (`gr_range.py`) was not recomputed by the verifier. |
| C9 | Ruling 0013 applied | PASS | STATUS T3 judged on the reference-based design; reason of the ruling corrected in 0016 item 5 and `scope/SCOPE.md` 10.9. |
| C10 | Schematic: updated architecture | PASS WITH RESERVATION | `note/figures/schem_architecture.png` looked at: three columns, exists / to be ported / new, legible. Reservation: it names release core-v0.3; core-v0.4 (lapse relaxation `lapse_leak`, elliptic `id_solve`) is now on main and touches its "new" boxes; redraw before G2. |
| C11 | Schematic: data-flow diagram | PASS | `note/figures/schem_dataflow.png` looked at: four lanes from initial data through AthenaK and raw outputs to analysis, products, ledger and note, with run registration and the verifier's path; it is Fig. 7 of the note (App. B). |
| C12 | Data figure: baseline results | PASS | `fig_exact_shells.png`, `fig_constraint_convergence.png`, `fig_scan_hoop_time.png` looked at; `note/figures/fig_constraints.png` looked at (orders against h^2, h^4 guides). |
| C13 | Data figure: validation of the analysis pipeline | PASS | `newton/figs/fig_axes_selftest.png` (semi-axes from synthetic snapshots on the reference; the legend covers part of the top curve, cosmetic) and `fig_crosscheck.png` of A-20261115-130257-a7374a4, looked at. |
| C14 | Package documents of decision 0012 | PASS | All present in `stage/G1/`; `verify` check `package` PASS (section 3). |
| C15 | Data figures from registered runs, one script each, looked at | PASS | `verify`: fig-script, rerun (9 of 9), compare (14 files within tolerance), regenerate (14 of 14) PASS on the clean export. |
| C16 | Schematics: architecture and gate timeline | PASS | `note/figures/schem_timeline.png` looked at: G0 passed, "now" after G1, needs between gates. |
| C17 | Working note, manuscript checker with --compile | PASS | My recompile of the committed note (scratch copy): 12 pages, 0 undefined references, 0 undefined citations, 0 overfull boxes; candidates only under 5.5 (run ids, all in the appendix and ledger tables) and 5.8 (scripts), as g1close entry 6 reports. |
| C18 | Fresh verifier wrote VERIFIER.md; every number of the Supplemental Material recomputed | PASS WITH RESERVATION | VERIFIER.md read in full; predictions committed before its run (2256c860), sections 1-3 before reading the track's review; its corrections applied or partly rebutted with evidence (g1close entries 1-4; the rebuttal of "only four points" is right, my check E). With my checks A-D, all but three rows are now independently recomputed; open: compactness on the axes and horizon count of SR-2, predicted card-hours, four cross-check differences (section 1). |
| C19 | Null results and failed runs on record | PASS | STAGE_REPORT lists 20 failed or stopped runs; refuted predictions are written out in `criteria/`, `runs_ball/`, `newton/`, `periodic_threshold/` journals and `stage/REVIEW-wave2.md`; the SR-1 breakdown, no horizon in SR-1/SR-2/S1/S2, S1 non-finite are in the note and STATUS. My own failed run A-20261121-064515-aa13c8f is on record (section 1). |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md current | **FAIL** | Owner's `STATUS.md` lines 3-4 "G0 and G1 packages submitted for review 2026-11-15 (not passed) ... open: data-flow schematic (C11) and verifier (C18)", line 13 "14 scan points within 6.3e-4 of the ellipsoid" (9 of 14 in fact, check E); the headline's "errors converging at order 3-4" mixes a box change (verifier weak point 2). `git log` of the three files: last commits 8737de9b and 510fdb96 on 2026-11-15. G0 passed on 2026-11-19 (`coord/GATES.md`). |

## 3. Automated re-verification (`nrpic-stage verify A-emd-pbh G1`, full, with checksums)

Run by me on 2026-11-21T06:54:41Z (24 minutes, most of it hashing the outputs), clean export of
2ab02992 (the package at cc032d70 with main merged): **FAIL**, 12 PASS, 1 WARN, 3 FAIL. Result
files copied to `scratch/A-emd-pbh/gate_review_G1/VERIFY_RESULTS_reviewer.{md,json}`; the
committed `VERIFY_RESULTS.*` of the package are left as the lead wrote them.

| Check | Result | Cause |
|---|---|---|
| export, size, note, package, note-pdf, style, fig-script, min-figs, status, rerun (9 of 9), compare (14 files), regenerate (14 of 14) | PASS | |
| run-notes | WARN | 79 manifests read with defaults (hand-written, waves 1-2; decision 0016 item 3) |
| clean | FAIL | four uncommitted files of the periodic_threshold package (`JOURNAL.md`, `inputs/peak_leak.athinput`, `scripts/ltb_reference.py`, `scripts/ltbref.py`), stranded by a session cut on 2026-11-20; not package files |
| sync | FAIL | main gained commit 04636486 (orchestrator, decision 0020 amendment) while the verify ran |
| runs | FAIL | 163 of 167 manifests complete and their output checksums verify (this closes the checksum pass g1close could not finish). The four failures are unfinished manifests of other packages: A-20261119-164634-f1fe887 and A-20261120-223310-a9ce31a (runs_ball; "submitted", the second one's Slurm job 4748 COMPLETED on 2026-11-20 14:46-14:47 PST per `sacct`), A-20261120-223123-f436c39 (periodic_threshold) and A-20261120-223422-8cc4241 (szekeres), both "running" with no live process (their recorded PIDs 2064748, 2148437 do not exist). |

None of the three failures comes from the G1 evidence, but one touches it: note App. B names
A-20261119-164634-f1fe887 among the runs of Sec. V (plans), and that manifest has no checksums
yet.

## 4. Failed predictions, null results, numbers without a run id

- Failed predictions are kept, with outcomes, in the journals (C19); the package's own close-out
  records its refuted parts (g1close P2 upper end, P5 "only four points", the count "7 of 7").
- Null results on record: no apparent horizon in any full-relativity run (SR-1, SR-2, S1, S2);
  SR-1 breaks down before trapping; S1 non-finite at 21.9 t_H.
- Every row of the note's ledger carries a run id; every decimal number in the note's main text
  before the appendix also appears in the ledger tables (my text scan, not a registered run).
  The text quotes few numbers and points to the tables.

## 5. Recommendation

**PASS WITH RESERVATIONS, to be signed when C20 is closed.** Steps before the sign-off, none of
them science work: (1) the lead rewrites the owner's `STATUS.md`, `JOURNAL.md`, `HANDOFF.md`
for the state after wave 3 (the sentences to change are listed in `g1close/README.md`,
"Requests") and sets C20 to PASS; (2) the periodic_threshold, runs_ball and szekeres packages
commit or close their stranded files and manifests (`nrpic-run finish`/`stop`), or the
orchestrator waives these four run ids for this gate; (3) `nrpic-stage verify` on the commit with
main merged, then `nrpic-stage report`. If the orchestrator signs before (1)-(3), the tag should
be provisional with C20 named as its condition.

## 6. Reservations to carry to G2

1. **No horizon yet** in either set-up (carried from G0): the G2 slicing must reach trapping;
   the SR-2 lapse departs from the core's scale factor by more than 10 per cent from t = 6.5 at
   every resolution (check B), a gauge effect.
2. **SR-2 turnaround**: re-judge runs_ball prediction R2 with the window-independent estimator
   of runs_ball entry 13 before any turnaround number is used for G2 convergence.
3. **Mesh against box**: the dx = M_0/4 runs have half the box; the fixed-box job
   A-20261120-223310-a9ce31a has run and awaits its analysis (runs_ball entry 14, prediction F).
   Locate the SR-1 constraint maximum (0.051 -> 0.040 from M_0/2 to M_0/4, check A).
4. **Constraints of the evolution data**: show convergence of data set 2t as a whole and of
   AthenaK's t = 0 norms of the format-2 table in dx.
5. **Rows recomputed by nobody independent**: SR-2 compactness on the axes and the horizon count,
   the predicted card-hours, the four cross-check differences.
6. **Wave-1 provenance**: the outputs behind 18 ledger rows were checksummed only on 2026-11-20
   (run A-20261120-222620-0304d9d); rerun their producers through `nrpic-run` (verifier weak
   point 3).
7. **Newtonian energy drift** at sub-cell crossings, cause unknown (C8).
8. **Criteria tally**: quote "41 of 41" with the two restated bands and two diagnostics (C7).
9. **Architecture schematic** to be redrawn against core-v0.4 and later (C10).
10. **G2 horizon-mass criterion** may be unreachable as written (risk 17: the source's own
    Oppenheimer-Snyder test saw no monotonic convergence of the horizon mass); report the
    measured error with its N and dx dependence and ask the orchestrator early if it stalls.

## 7. Pending runs and requests (not the reviewer's)

- runs_ball helper: finish A-20261119-164634-f1fe887 and A-20261120-223310-a9ce31a and analyse
  them (runs_ball entry 15, steps 1-5).
- periodic_threshold helper: commit its four stranded files; close A-20261120-223123-f436c39.
- szekeres helper: close A-20261120-223422-8cc4241.
- Lead: C20 (above); the note's App. B may cite run A-20261121-064537-2bcf310 for the four
  Table IV rows it recomputes.
