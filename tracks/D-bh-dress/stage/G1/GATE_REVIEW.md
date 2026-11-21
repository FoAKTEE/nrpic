# GATE_REVIEW.md: independent gate review of G1 of D-bh-dress

Reviewer of batch 4b (decision 0019 item 3; decision 0023 item 3), fresh context,
2026-11-21 16:48 to 17:12 UTC. I produced none of the work under review. No tag
`stage/D-bh-dress/G1-pass-*` existed when I started (`git tag -l`: only
`stage/D-bh-dress/G0-pass-20261120`). Worktree after `git merge --no-edit main`: 3771509c.

**Read.** `CLAUDE.md`; `coord/CHARTER.md` to "Owners" and sheet 9.7 (G1 of Track D:
"derivation and offline check of D-pre-1; the baselines of D-pre-2 and D-pre-3; the noise
floor of D-pre-4"); brief lines 674-686 (G1: "baseline results obtainable without the NRPIC
coupling; the analysis pipeline validated on them; interface proposals submitted"; products
"baseline data and figures; interface documents"); decisions 0013, 0016, 0021 (item 2: D-pre-3
judged on the growth of the dress against matched shells and on the profile against the
self-similar solution from a/a_i = 3 on; item 4: three waived manifests), 0022 (item 3), 0023
(item 3); the package `stage/G1/` (STAGE_REPORT, CHECKLIST, EVIDENCE, OPEN, REVIEW, STATUS,
VERIFIER, VERIFY_RESULTS); `stage/REVIEW-wave3.md` sections 9-10; `einstein_straus/DERIVATION.md`
in full; `secondary_infall/JOURNAL.md` 07:55Z-09:35Z (predictions P, E, Q16 and their outcomes);
`note/main.tex` (grep of the D-pre-3 and open-items paragraphs) and `note/tables/claims.md`.

**Opened as evidence** (named at each criterion): the manifests of the D-pre-1 runs
(D-bh-dress-20261115-042626-f3da881, -042704-f3da881, -043406-4df1e76) and their outputs
(`log.txt`: 48 lines `[OK]`, 0 failures; `offline_check.json`: finest-pair orders per sub-box);
the Q16 manifest D-20261121-085652-7e189a2 (completed, exit 0, core-v0.5 threaded build, 171
files) and its analyses (`nm_late.txt` of D-20261121-092757-34faefa, `nm_lost.json` of
-092757-3df1172: 520048 particles in all 146 snapshots); the D-pre-4 and V-1B horizon summaries;
the source locator `kerrdm.tex:125-127` of arXiv:1707.06302 v2 in kb-data ("M_BH >~ 4 x 10^6
M_sun"); the queue state of the two G2 card runs. Figures looked at with the Read tool (16):
`einstein_straus/figs/check_3d.png`, `code_t0.png`; `es_runs/figs/offline_check_3d_es.png`;
`note/figures/fig_spike.png`, `fig_kerr.png`, `fig_newton.png`, `fig_floor.png`,
`fig_esrun.png`, `schem_architecture.png`, `schem_timeline.png`;
`secondary_infall/figs/w3_Q16_late_profiles.png`, `w3_Q16_late_growth.png`;
`spike/figs/kerr_main_profile.png`; the verifier's `v3_hern_a0.8.png` (D-20261121-033209-9c0bd44);
the lead's `batch4a_profile.png` (D-20261121-155215-0611c24); my own `fig_review_checks.png`.

**Ran.** (1) `harness/bin/nrpic-stage verify D-bh-dress G1` on 3771509c (section 3; output kept
in `scratch/D-bh-dress/tmp/gate_review_G1/`; the stage copies of `VERIFY_RESULTS.{md,json}`
were restored to their committed state, so this review changes no package file but this one).
(2) My own check, registered: run **D-20261121-165428-8440947** (`nrpic-run`, one core, exit 0;
script `scratch/D-bh-dress/tmp/gate_review_G1/review_checks.py`, which imports nothing of the
track but a copy of `harness/style/figstyle.py`; predictions committed first in 5d1c2455). Its
first attempt D-20261121-165420-5d1c245 failed (overflow of `exp` in my step function at small
argument; fixed by a guard, nothing else changed); it stays on record. (3) The manuscript checker
`check_manuscript.py --main main.tex --compile` on a `git archive` export of the committed note
(`scratch/D-bh-dress/tmp/gate_review_G1/check.log`). No card-hours used.

## 0. Verdict

**Recommendation: PASS WITH RESERVATIONS.** Every track criterion and every common criterion of
G1 is met by evidence I opened. D-pre-1 (derivation, 48 symbolic identities, fourth-order offline
residuals) is the strongest item, and my own quadrature reproduces its puncture parameters to
5e-15. D-pre-4's floor reproduces from the raw finder output to 8e-4 relative. D-pre-2 reproduces
the Schwarzschild spike of SFW and the constant-f Kerr curves of FdRW within 1 per cent, and
AthenaK keeps the Kerr distribution stationary for 20000 M. D-pre-3 is met in the form decision
0021 item 2 rules, not in the brief's "reproduce r^(-9/4)" (which no run at reachable a/a_i can
show; errata row 1.7): Q16 follows matched shells to a/a_i = 16 and lies within 16 per cent of the
self-similar profile there, and my two independent estimators give its M_ta to 0.09 and 0.01 per
cent. The reservations (section 5) concern margins and wording, not missing evidence: one
pre-registered band of Q16 failed (M_ta at a/a_i = 16, recorded by the package), the profile
bound is sensitive to r_ta, Q16 has one resolution, a 4.5 per cent gap to a published Kerr curve
is assigned to that curve by judgement, the working note v1 predates Q16 and the ruling, and the
committed STAGE_REPORT/VERIFY_RESULTS still show the verify of 5ce52d25.

## 1. My own check: predictions and outcomes

Predictions as committed in 5d1c2455 (first version of this file), before the run. Run
D-20261121-165428-8440947, outputs `review_checks.json`, `review_checks_full.json`,
`fig_review_checks.png` in `scratch/D-bh-dress/D-20261121-165428-8440947/` (figure looked at:
(a) the 20 M means of the D-pre-4 horizon mass, M/8 rising by 1.5e-4 between 50 and 100 M (read by the
package as the end of its gauge transient) and then slowly, M/16 flat to 210 M then rising to 3.7e-5; (b) V-1B
within +-2e-5 except one dip to -4.8e-5 at t = 135 M; (c) Q16's median radial velocity by initial
radius changes sign from negative to positive at r0 = 26.4 M, the design's r_last(16) = 26.398 M
of `setup.json`).

| # | Quantity | Claim | Mine (D-20261121-165428-8440947) | Outcome |
|---|---|---|---|---|
| P1 | D-pre-1: a, m_p, rbar(R0) from my own quadrature of DERIVATION.md sections 3-4 | 0.9765922286441, 1.023968828206 M, 3.055588 M | 0.9765922286440953, 1.023968828206225, 3.0555883603 (quad error 3e-15) | holds (5e-15, 2e-13, 4e-7) |
| P2 | D-pre-4 drift D = Mbar(490) - Mbar(50), 20 M window | +2.9529e-4 (M/8), +3.6743e-5 (M/16) | +2.9553e-4, +3.6722e-5 | holds (+8.1e-4 and -5.8e-4 relative, inside 1e-3; [JUDGEMENT] the small difference is the window placement: `claims.md` says the ledger's last 20 M means end at 489.5 and 489.75 M, mine is centred on 490 M; not tested) |
| P3 | V-1B, largest abs(M(t)/M(100) - 1) on [100, 200] M | 4.8e-5 | 4.838e-5 at t = 135 M (200 searches) | holds |
| P4 | Q16 particle number and mass, first and last snapshot | 520048, 15.29505 M, none lost | 520048 and 520048; 15.295052737568776 M in both; the sorted tags identical | holds |
| P5 | Q16 M_ta at a/a_i = 15.956, Lagrangian and Eulerian | 9.3017 M (9.3030 flag-free) | 9.2934 M (r0_ta = 26.43 M), 9.3030 M (r_ta = 247.19 M; package 247.13) | holds (-0.089 and +0.014 per cent) |

All five predictions held. Not checked by me: the dress (needs the crossing history), the shell
references and the self-similar solution (the verifier and the lead each built one; section 2, C7).

## 2. Criteria, one by one

| # | Criterion | Evidence I opened | Verdict |
|---|---|---|---|
| C1 | Baseline results obtainable without the NRPIC coupling | D-pre-1: offline residuals (D-bh-dress-20261115-042704-f3da881) and the t = 0 check in AthenaK (-043406-4df1e76); D-pre-2: AthenaK geodesics on the analytic Kerr metric (D-bh-dress-20261115-172611-1e40191, `kerr_main_profile.png`); D-pre-3: AthenaK's Newtonian mode (Q16 D-20261121-085652-7e189a2; wave 2 N128c/N64c/N128Lc); D-pre-4: vacuum puncture, no particles (D-bh-dress-20261115-121313/121314-284ec4f). None needs the particle-spacetime coupling | PASS |
| C2 | The analysis pipeline validated on them | Fresh verifier V1-V4 with its own readers and references (VERIFIER.md; runs D-20261120-222209-871e07f ... -040826-9d5051a), the lead's independent re-checks (Y1-Y5, Z1-Z5), and my run D-20261121-165428-8440947 (P2-P5: finder summaries and particle dumps read with my own code reproduce the package's drifts, floor, particle count and M_ta). `fig_esrun.png` shows the ES-1/V-1 pipeline on full-relativity output (wall tracers within 3e-3 of the exact curve to tau = 200 M, crossings on the exact curves) | PASS |
| C3 | Interface proposals submitted | `outbox/20261115T1510Z__to-core__*.md` (eight to core: accretion diagnostics, analytic-metric excision, lapse for expanding dust, format-2 reader, Newtonian point mass, puncture on the torus, restart dump, tracer push) and later ones (38 outbox files); core's triage `tracks/core/interfaces/REQUESTS_ADF.md` on main, rows D1-D6 (five ACCEPTED and done, D6 deferred to wave 3) | PASS |
| C4 | Baseline data and figures | `fig_spike.png` (relativistic spike against the Newtonian one, stationarity in AthenaK), `fig_kerr.png` (three spins against FdRW's published points, counts over 20000 M), `fig_newton.png`, `w3_Q16_late_growth.png`, `fig_floor.png`, `check_3d.png` | PASS |
| C5 | Interface documents | D's specifications are documented as options by core: `coord/INTERFACES/pusher.md` (tracer mass convention, pericentre counter), `newtonian_mode.md` (`newton_pm_mass` and its tests), `spherical_id_format2.md` (the bubble wall), `REQUESTS_ADF.md` sections 2.1-2.5. D has no interface document of its own; at G1 none is required beyond the proposals [JUDGEMENT] | PASS |
| C6 | Derivation and offline check of D-pre-1 | `einstein_straus/DERIVATION.md` read in full: constraints in KT, KL; Misner-Sharp identity; the slice family and the conditions F1-F4 on f; puncture form with m_p = M/a; LTB mass conservation inside the comoving wall; eight documented disagreements with the orchestrator's item 2. Symbolic run D-bh-dress-20261115-042626-f3da881: 48 `[OK]`, 0 failures. Offline run -042704-f3da881 (`offline_check.json`): finest-pair orders of H 3.90-4.07 and of M 3.85-3.99 where above round-off, H at round-off (1e-19) in flat dust and exterior; `check_3d.png` and, for the run data set, `offline_check_3d_es.png` show h^4 throughout. AthenaK at t = 0 (`code_t0.png`): residuals fall with dx in the transition and stay at round-off outside 60 M, the throat region non-convergent as predicted. My P1 reproduces a and m_p to 5e-15 | PASS |
| C7 | The baselines of D-pre-2 and D-pre-3 | **D-pre-2**: `fig_spike.png` (a) and the ledger (peak 0.8699e8 GeV/cm^3 at 7.58 Gm, SFW Fig. 1 to 0.02 per cent at the peak and 0.26 per cent over the curve; D-bh-dress-20261115-145636-5259f48, confirmed by the verifier's V6); `fig_kerr.png` (constant f within 0.85-0.88 per cent, verifier V3); `v3_hern_a0.8.png` (two independent implementations agree to 0.6 per cent and both lie 4.5 per cent below FdRW's a = 0.8 Hernquist peak, which carries a narrow bump neither reproduces; [JUDGEMENT] that the gap lies in FdRW's curve); AthenaK stationarity `kerr_main_profile.png` (counts within 1 sigma of the reference in every band and angle after 20000 M; invariants to 1e-5, verifier V4); hole mass 4e6 M_sun is the track's choice consistent with `kerrdm.tex:127` ("M_BH >~ 4 x 10^6"). Axis curve not checked by a second agent. **D-pre-3** (decision 0021 item 2): Q16 analysis `nm_late.txt` at a/a_i = 15.956: M_ta 9.3017, dress 4.9109, relative to hybrid_cc +0.80 and +0.11 per cent, to kernel_cc +1.28 and +0.64 per cent; profile ratios 0.959-1.043 except 0.841 at lambda = 0.231, max 15.9 per cent, rms 7.6 per cent (prediction Q3: 20 per cent, rms 15, written before the run in `secondary_infall/JOURNAL.md` 08:56Z); `w3_Q16_late_growth.png` and `w3_Q16_late_profiles.png` show run and shells together from a/a_i = 2.3 on and the run on the self-similar line from lambda ~ 0.04 to 0.3; the lead's `batch4a_profile.png` against the verifier's seedless solution gives 16 per cent, 25 per cent with r_ta moved by -3 per cent. Wave 2 at a/a_i = 2-8 as confirmed by the verifier (V2, M_ta within 0.43 per cent, dress within 1.2 per cent from a/a_i = 3) | PASS WITH RESERVATION (section 5, items 1-3) |
| C8 | The noise floor of D-pre-4 | Manifests and summaries of D-bh-dress-20261115-121313-284ec4f (M/8, 0.654 card-hours) and -121314-284ec4f (M/16, 1.523); `fig_floor.png`; my P2 reproduces the drifts +2.955e-4 and +3.672e-5 over 50-490 M. The floor holds for an asymptotically flat vacuum puncture; the null test's own floor is the matched control V-1B (4.8e-5 over 100-200 M, my P3), as the package says | PASS |
| C9 | Schematic: updated architecture | `schem_architecture.png`: three stages, three states (exists / provided by core / new for Track D), core's wave-2 capabilities, run chain to the null test | PASS |
| C10 | Schematic: data-flow diagram | the same figure is drawn as a flow, initial data -> evolution -> analysis -> deliverables; one figure for both is acceptable at G1 [JUDGEMENT] | PASS |
| C11 | Data figure: baseline results | as C4 | PASS |
| C12 | Data figure: validation of the pipeline | `kerr_main_profile.png`, `fig_esrun.png`, `check_3d.png`, `code_t0.png`, the verifier's `v3_hern_a0.8.png`, my `fig_review_checks.png` | PASS |
| C13 | Package documents (decision 0012) | STAGE_REPORT, EVIDENCE, OPEN, CHECKLIST, VERIFIER, REVIEW, STATUS present; scoping text `scope/SCOPE.md`. The committed STAGE_REPORT and VERIFY_RESULTS carry the verify of 5ce52d25 (FAIL on clean and runs) and its figure table says "to be confirmed by the session" in the column "Looked at" | PASS WITH RESERVATION (formal: regenerate verify and report; section 6) |
| C14 | Data figures from registered outputs, one script each, every PNG looked at | verify (section 3): fig-script, rerun, compare, regenerate all PASS; the eight data figures of the note are drawn by their scripts from registered runs (`fig_*_numbers.json` beside each); I looked at five of them and both schematics | PASS |
| C15 | Schematics with paperfig: architecture and timeline | `schem_architecture.png`, `schem_timeline.png` (paperfig.py, style copies verified by the harness). The timeline's header still reads "G1 open for the infall profile criterion and this note" (cosmetic) | PASS |
| C16 | Working note with /paper-writing; checker with --compile | My rerun on the committed source: 0 undefined references, 0 undefined citations, 0 overfull boxes, 18 pages; the only candidates are the 94 run ids of the ledger (accepted exception). Every one of the 94 data rows of `tables/ledger.tex` names a run id. But note v1 predates Q16 and decision 0021: `main.tex` line 198 says the run to a larger scale factor "belongs to the next version", line 200 that the D-pre-3 criterion is open and "a ruling is requested", and that the cause of the late drift is open (V-1B has since shown it was the outer boundary in vacuum with 1+log) | PASS WITH RESERVATION (section 5, item 4) |
| C17 | Fresh verifier; Supplemental numbers recomputed | VERIFIER.md read in full: own readers and references; verdicts committed (102d696b) before the track's material was read; its own V4 error found after the verdicts and recorded openly as not blind. 34 ledger rows agree, none WRONG; 8 rows NOT CONFIRMED (box mid-transition orders, cost model, wall radius against the closed form, smallest detectable change (two rows), chi^2 median, SFW Fig. 1 read-off, loss-cone probes, self-similar lambda^(9/4), passed and captured fractions, radiation era), the Kerr axis curve not computed. The verifier's WRONG-as-worded item (dress at a/a_i = 2) is corrected in STATUS and the note | PASS WITH RESERVATION (eight rows without a second value) |
| C18 | Null results and failed runs on record | the failed and stopped runs of STAGE_REPORT keep their manifests; refuted predictions are written in the journals (`secondary_infall/JOURNAL.md`: P192's late predictions, Q2 at a/a_i = 16, W2 as worded, Q5's step count; `es_runs/JOURNAL.md`: prediction 4 and A2 refuted, 40 lines with "refuted" or "failed"; `fig_esrun.png` shows the failed horizon-level and drift predictions as grey bands); the P192 run to a/a_i = 30 is kept as failed past a/a_i ~ 12 with its cause (edge-layer energy) | PASS |
| C19 | STATUS, JOURNAL, HANDOFF current | last changed in b23712fc (2026-11-21 08:35 PST), after the lead's report; STATUS (38 lines) names the G1 state, Q16, the G2 runs and decision 0022 item 3 | PASS |

## 3. Harness verify

`harness/bin/nrpic-stage verify D-bh-dress G1` on 3771509c (16:50 to 17:09 UTC, with the output
checksums of every run): **FAIL on three formal checks, PASS on every check of content.**

| Check | Result | Reading |
|---|---|---|
| clean | FAIL | the three untracked tools of the open package `drift_controls` (`compare_runs.py`, `count_blocks.py`, `slice_profiles.py`), the same as at 5ce52d25; not G1 evidence |
| sync | FAIL | main moved while the verify ran (efd77b39 and nine earlier commits after 9aa74405, which I had merged at 16:48); the branch was in sync at the start |
| runs | FAIL | 1 of 238: ES-F D-20261121-144631-aa7ce9b (G2 card run, Slurm 4806, running at review time; status `submitted`, no `sha256sums.txt` yet). The other card run named in the package report, ES-1GB D-20261121-125900-ea4c442, is now closed (`failed`: chain capped at one segment, ends at t = 188 M; 0.83 card-hours). Every other manifest is complete and every output checksum of the 237 finished runs verifies, Q16's 171 files (6.1 GB) included |
| runs-waived | WARN | six: the two D-pre-4 card runs and their analysis (hand-written wave-1 manifests without `preregistered_in`, listed in `G0/EVIDENCE.md`, decision 0016 item 3) and the three runs of `coord/WAIVERS.md` (decision 0021 item 4) |
| run-notes | WARN | 100 runs read with defaults (hand-written manifests of waves 1 and 2) |
| export, size, note, package, note-pdf, style, fig-script, min-figs, status | PASS | 10 figures with a script each; 2 schematics and 8 data figures; 2 style copies equal `harness/style/SHA256SUMS`; STATUS 38 lines |
| rerun, compare, regenerate | PASS | 10 of 10 scripts ran cleanly in the clean export; 28 regenerated files equal to the committed ones (rtol 1e-6, PNG rms 0.005); all 20 committed figure files regenerated |

The results are kept in `scratch/D-bh-dress/tmp/gate_review_G1/VERIFY_RESULTS.{md,json}` and
`verify_stdout.txt`; the stage copies were restored to their committed state (5ce52d25's run).
C14 is therefore **PASS**: every data figure of the note is regenerated by its own script from
registered outputs, and the ones I looked at match their captions.

## 4. Failed predictions, null results, numbers without a run id

On record (C18). The note's ledger names a run id in each of its 94 data rows; its claims check
(`note/tables/claims.md`, generated by `note/scripts/ledger.py`) compares the lead's documents
with the files and lists every disagreement (one locator, "dress 0.625", since corrected in
STATUS to run D-bh-dress-20261115-125613-248fdaf). In the package documents every number I
traced carries a run id. One wording point: CHECKLIST C7 says "M_ta within 0.2 per cent of the
cell-centre shells at 4-12 and 0.8 at 16"; this holds against hybrid_cc only (against kernel_cc
0.42-0.62 per cent at 4-12 and 1.28 at 16, `nm_late.txt` and the 09:35Z journal entry).

## 5. Reservations to carry to G2

1. **D-pre-3 margins.** The pre-registered band of Q2 failed at a/a_i = 16 (M_ta +0.80 per cent
   over hybrid_cc against +0.5), recorded by the package with a mechanism (edge-layer energy) that
   is [JUDGEMENT] for Q16. The profile bound (15.9 per cent against a pre-registered 20) becomes
   21.6-24.9 per cent with r_ta moved by 3 per cent; at a/a_i = 8 it is about 25 per cent. Q16 has
   one resolution and one realisation; no clean run exists past a/a_i = 16 (P192 failed for a set-up
   reason) and the approach on lambda = 0.01-0.06 is not shown. G2/G3 parameters taken from D-pre-3
   should carry these margins.
2. **Criterion changed after the data.** D-pre-3 is judged under decision 0021 item 2, which
   replaced the brief's r^(-9/4) after the wave-2 runs; the note and the paper must say that the
   power law itself is not tested and why (errata row 1.7).
3. **Kerr reference.** The 4.5 per cent gap to FdRW's a = 0.8 Hernquist peak is assigned to the
   published curve by judgement (two implementations agree with each other); the axis curve and a
   second sampler seed for the inner-range deficits of AthenaK (3.1, 1.8, 0.9 per cent, each within
   1-2 sigma) are open. Before the strong-field spike is compared with the literature at G3, both
   should be closed.
4. **Note behind the package.** Note v1 says the D-pre-3 criterion is open and a ruling requested,
   the late drift unexplained, ES-1G "being analysed"; Q16, decision 0021 and V-1B are not in it.
   The next version should carry them before G2 is presented.
5. **Ledger independence.** Eight rows of the note's ledger have no second value (C17).
6. **Floor for the null test.** D-pre-4's 50-490 M drift at M/8 is half made in the rise between
   50 and 100 M, which the package reads as the end of the gauge transient (my `fig_review_checks.png` panel a); the excursions at 220-255 and
   300-340 M are unattributed (R4). G2 should quote the matched-control floor (V-1B, 4.8e-5 over
   100-200 M, 1+log, faces at +-384 M) and not D-pre-4, as the package already plans; decision 0022
   item 3 moves the null test off `lapse_leak`.

## 6. Formal items (not blocking)

- Regenerate `VERIFY_RESULTS.{md,json}` and `STAGE_REPORT.md` (`nrpic-stage verify`, `report`)
  after the three untracked `drift_controls/tools/*.py` are committed by their package and ES-F
  (D-20261121-144631-aa7ce9b, Slurm 4806, running at review time) is closed; fill the "Looked at"
  column of the figure table.
- Merge main again (`nrpic-ctx sync`) before the next verify (section 3, sync).
- CHECKLIST C7: name hybrid_cc as the reference of "within 0.2 per cent".
- `schem_timeline.png`: header still says G1 is open for the infall criterion and the note.
