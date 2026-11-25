# Stage report: C-sidm G2

Date: 2026-11-25 · branch `track/C-sidm` at `e93561aad09a` · checklist
`tracks/C-sidm/stage/G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/C-sidm/G2-fail-20261125` (created and pushed by the orchestrator after review, decision 0003).

- 13 checklist items not PASS or NA: C1 FAIL, C2 FAIL, C5 OPEN, C6 OPEN, C7 FAIL, C9 FAIL, C10 OPEN, C11 OPEN, C13 OPEN, C15 OPEN, C16 OPEN, C17 OPEN
- verify reported FAIL: runs
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G2/STAGE_REPORT.md` | present |
| `stage/G2/EVIDENCE.md` | present |
| `stage/G2/OPEN.md` | present |
| `stage/G2/CHECKLIST.md` | present |
| `stage/G2/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G2/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G2 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The code paths used by the track pass their tests of §10 | Collision operator rows of brief section 10 pass (G1, signed; heat series: kappa/kappa_1 = 1.020 +- 0.004, run C-20261124-131012-f920f45). Row 'Einstein-Vlasov steady states and their stability threshold': the steady state FAILED at N = 1e5 on M/8 (controls of y0 = 0.334032, 0.344 collapse at 534.8, 549.3 M; C-20261124-130634-3338d9b, on record) and HOLDS at N = 1e6 (control N6c C-20261124-221122-928c9eb: no collapse in 600 M, alpha_c within [-0.0022, +0.0115]; analysis C-20261125-122010-fb3cc08, fig_nseries.png read; NS.1 held, NS.2 failed, JOURNAL 2026-11-25T12:21Z). The threshold part is not located: bracket at N = 1e6 queued (q0046 N6b344, q0047 N6b324). Stays FAIL until the bracket is read. Batch 20: block A closed (C-20261125-160056-a5b7282): the y0 = 0.324 control at N = 1e5 also crosses alpha_min 0.3 (599.99 M), so all three N = 1e5 controls fail; collapse times are lapse markers, no run had the horizon finder (C-20261125-160207-05b6db1, decision 0040 item 3). | FAIL |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | Particle number on M/8: N = 1e5 control collapses at 534.8 M, N = 1e6 holds 600 M (C-20261125-122010-fb3cc08); H-norm2 floor ratio 9.95 for N ratio 10; third point N4c queued (q0018); seed scatter at 1e5 from q0022, q0023. Mesh (collisional t_c, collision cells M/4): 206.64 (M/4), 163.41 (M/8), 158.42 M (M/16), differences 43.23 and 4.99 M (C-20261125-122020-031b67e, fig_d2.png read; M16.1, M16.2 held); the seed scatter at M/8 that judges the 3.1 per cent M/8->M/16 shift waits for q0024 (D2f2s2+). Gauge or boundary: no run yet; D2 with shift_eta 1.0 queued (q0048, B17.4). Collisionless mesh leg of the threshold (M/16 at N = 1e6) and its gauge leg (shift_eta 1.0): queued in batch 20 under ruling 0039 item 3 (A16b344, A16b324, N6b344e1, N6b324e1; predictions B20.1-B20.3, JOURNAL 2026-11-25T16:02Z; decks smoke-tested, C-20261125-155959-866b049). | FAIL |
| C3 | Constraints behave | H-norm2 of the controls flat after 50 M at a floor set by the deposit noise: 8.6e-4 (N = 1e5) and 8.5e-3 (N = 1e4) on M/4, ratio 9.97 = the N ratio (C-20261124-130021-5c9c207, fig_cc2_N.png, panel 3); on M/8 the floor is 9.3 times that of M/4 at equal N (drift entry 12), close to the factor 8 of the particles per cell. No growth before collapse in any run read; after collapse the guard or the excision ends the record. [JUDGEMENT: "behave" read as bounded and scaling with the particle noise; convergence of the floor with the mesh is not expected at fixed N.] | PASS |
| C4 | A first minimal full-GR kinetic run | Full-GR kinetic runs with and without collisions to 300-600 M on M/8 (release core-v0.6): D2 (C-20261122-103854-4670b59, -144455-6e0992e, -141414-399ad97, -181011-60baef9) and block A (15 chains, e.g. C-20261121-214601-40dc927). | PASS |
| C5 | Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md) | STAGE_REPORT.md written by nrpic-stage report in this session with EVIDENCE.md and OPEN.md; the verification it reports is incomplete (C1, C2, C7). | OPEN |
| C6 | Reproducibility package | Every run registered (tracks/C-sidm/runs/); decks and readers in tracks/C-sidm/longruns/ (README "How to rerun the analyses"); not yet a package that verifies the capability (C7 open). | OPEN |
| C7 | The collisionless threshold reproduces the literature value with three-way convergence | Not located. At N = 1e5 on M/8 block A is unfit by its own refutation rule (A.4 failed; C-20261124-130634-3338d9b, on record). N6c shows the cause is particle noise (NS.1 held), so the reading moves to N = 1e6: bracket y0 = 0.324 / 0.344 kicked inward at N = 1e6 queued (q0046, q0047; predictions B17.5, B17.6, JOURNAL 2026-11-25T12:01Z). Three-way convergence of the threshold: mesh (M/16) and gauge (shift_eta 1.0) members queued in batch 20 (B20.1-B20.3); the particle-number leg of the bracket has the N = 1e5 kin members of block A (0.344 kin collapses at 229.79 M, 0.324 kin holds 600 M; C-20261125-160056-a5b7282), whose controls fail. | FAIL |
| C8 | Once the collision module is in core, the budgets of conserved quantities close in curved spacetime | Collision budget in curved spacetime, coll_energy = particle, D2 on M/8: summed dH_particles / sum MH below 3.2e-16 up to the first excision for f = 1, 2, 4; rest-mass budget 2.7e-14; deposit identity 1e-15 (C-20261124-130442-0819c88, d2.json). Open item for the verifier: the collision-count test before t_c gives z = -3.39 at f = 4 (REVIEW-wave3 section 14). | PASS |
| C9 | Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013) | As C7: the threshold is not yet located; comparison with the turning point y_max = 0.334032 follows from the N = 1e6 bracket (q0046, q0047) at one mesh and one N; mesh and gauge legs of the bracket queued in batch 20 (ruling 0039 item 3; B20.1-B20.3). | FAIL |
| C10 | Schematic: Verification ladder | No verification-ladder schematic for G2 yet (G1 schematics in tracks/C-sidm/note/). | OPEN |
| C11 | Data figure: Convergence figures (one each for particle number, mesh, gauge) | Particle number: fig_nseries.png (C-20261125-122010-fb3cc08, N = 1e5 vs 1e6 on M/8; read) and fig_cc2_N.png, fig_diffusion.png (M/4; C-20261124-130021-5c9c207, -130222-6a4924d); mesh: fig_d2.png with M/16 (C-20261125-122020-031b67e; read); gauge: none until q0048. Note figures not drawn. | OPEN |
| C12 | Data figure: Constraint norms against time | Constraint norms against time: fig_cc2_N.png panel 3 (C-20261124-130021-5c9c207), looked at. | PASS |
| C13 | Data figure: At least one multi-scale slice mosaic with zoom boxes | No slice mosaic yet. | OPEN |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md, EVIDENCE.md, OPEN.md, CHECKLIST.md in stage/G2/; REVIEW is stage/REVIEW-wave3.md section 14; scoping text tracks/C-sidm/scope/. | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | Analysis figures exist in the run directories (each looked at); the note figures of G2 are not drawn. | OPEN |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | G2 schematics not drawn. | OPEN |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | The working note has its G1 sections only. | OPEN |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | No G2 verifier yet; what it must cover: OPEN.md section "What a G2 verifier must cover". | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | Failed predictions and runs on record: JOURNAL 2026-11-24T13:12Z (N.3, D2.2, A.1 kout part, A.3, A.4) and 2026-11-25T12:21Z (NS.2); withdrawn unqueued predictions B17.1-B17.3 (2026-11-25T12:01Z); failed analysis runs of batch 11 (own script bugs, rerun); preempted chains keep their manifests; six N = 1e5 continuations removed from the queue with the reason (stage/G2/OPEN.md). | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | Rewritten at the end of the batch-20 lead session (2026-11-25). | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-25T16:11:38Z, clean export of `e93561aad09a`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of e93561aad09a (HEAD) in /data/haiyangw/nrpic/scratch/C-sidm/tmp/stage-verify/C-sidm-G2-e93561a-20261125T161032Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 11 figures, each with its script |
| min-figs | PASS | 3 schematics and 8 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 1 of 246 runs have problems |
| run-notes | WARN | 25 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | output checksums not re-verified (--no-checksums) |
| status | PASS | STATUS.md has 34 lines |
| rerun | PASS | 11 of 11 scripts and commands ran cleanly in the export |
| compare | PASS | 22 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 22 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_box_step.* | note/scripts/fig_box_step.py | data | to be confirmed by the session |
| note/figures/fig_box_summary.* | note/scripts/fig_box_summary.py | data | to be confirmed by the session |
| note/figures/fig_cluster.* | note/scripts/fig_cluster.py | data | to be confirmed by the session |
| note/figures/fig_collisions.* | note/scripts/fig_collisions.py | data | to be confirmed by the session |
| note/figures/fig_heat.* | note/scripts/fig_heat.py | data | to be confirmed by the session |
| note/figures/fig_knudsen.* | note/scripts/fig_knudsen.py | data | to be confirmed by the session |
| note/figures/fig_onsets.* | note/scripts/fig_onsets.py | data | to be confirmed by the session |
| note/figures/fig_sequences.* | note/scripts/fig_sequences.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_dataflow.* | note/scripts/schem_dataflow.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported (`stage/G2/VERIFIER.md`, decision 0016).

## Null results and failed runs

- `C-20261115-165742-2c645f8`: failed (exit 1), box_tests T10 of collide/TESTS.md: bit reproducibility over 1/8/64 MeshBlocks and restarts every 37 cycles, seed control; release CPU executable
- `C-20261115-170221-b1a491c`: failed (exit 1), Offline checks of the N = 10000 models of run C-20261115-170126-b4f74af (M1 King regression at 1e4, M2 F21 solver, M3 per-model checks of equilibria/check_equilibria): tracks/C-sidm/models/JOURNAL.md
- `C-20261115-170231-4e68455`: failed (exit 1), Validation of the growth-rate and collapse-time pipeline (growth.py): synthetic signals and the first paper's cluster runs runs/st/* (read-only), published numbers of tab_outcomes.tex: predictions G1-G6 of tracks/C-sidm/models/JOURNAL.md
- `C-20261115-171137-9e3c807`: failed (exit 1), Offline checks of the N = 100000 models of run C-20261115-170742-84990ed (M1 King regression at 1e4, M2 F21 solver, M3 per-model checks of equilibria/check_equilibria): tracks/C-sidm/models/JOURNAL.md
- `C-20261119-143049-0cf699a`: failed (exit 1), box_rerun R5: T12 collisions in the static homogeneous curved metric (alpha0 0.8, psi0 1.1; static_conformal) against the flat twin and the analytic rate, coll_energy = particle (and cell once), 1e6 particles, 200 steps
- `C-20261119-154032-e450dfc`: failed (exit 1), heat T8 coarse: seven variants (dt, pmax, dx) at theta 0.003, k lambda 0.2, eps 0.2, 5e5 particles, transverse 8x8 cells of lambda/4
- `C-20261119-162015-d97abac`: failed (exit 1), heat T8 coarse, seed 2: seven variants (dt, pmax, dx) at theta 0.003, k lambda 0.2, eps 0.2, 5e5
- `C-20261120-222339-663f963`: failed (exit 1), models wave 3: unit tests U1-U5 of growth_fit_v2 and oscillation_period on synthetic signals (JOURNAL entry 9)
- `C-20261120-222852-7d55b7a`: failed (exit 1), heat T7 theta 0.003 eps 0.2 pooled: processor seeds 1-4, 11-14 (4e5) and card seed 5 (4e6)
- `C-20261120-222857-8ea9c42`: failed (exit 1), heat T7 theta 0.1 and 1, eps 0.2 pooled: processor seeds 1, 2 (4e5) and card seeds 1, 2 (2e6)
- `C-20261120-223424-f6ba00a`: failed (exit None), heat P-cc post hoc: chi^2 of card-vs-processor z and of same-executable seed pairs under the theta 0.003 noise model
- `C-20261121-080152-b8d0acd`: failed (exit 1), verify_g1 V4: own static Einstein-Vlasov equilibria (King b=1, F21 b=0.1), E_b maximum, F21 turning points, radial-pulsation onsets with 1+p/u and Juttner Gamma_1 (trial function and finite elements); F21 Table 1 check
- `C-20261121-155220-5c0d480`: failed (exit 1), lead batch 4a L25: note v1 ledger rows against run JSON; checker with --compile on a copy
- `C-20261121-163051-16356b2`: failed (exit 1), lead batch 4a L28: run (vi) joined with run (i), own reader (alpha_c, H-norm2, energy diffusion)
- `C-20261123-025228-6ecb543`: failed (exit 1), longruns A344s1o: A: block A M/8, y0 0.344 seed 1, kick out, 600 M (seq.sh; JOURNAL.md 2026-11-21T20:25Z)
- `C-20261123-222003-02195a0`: failed (exit 1), longruns A324s1o: A: block A M/8, y0 0.324 seed 1, kick out, 600 M (seq.sh; JOURNAL.md 2026-11-21T20:25Z)
- `C-20261124-035054-c06503f`: failed (exit 1), longruns D2f2s2: D2: CC2 Kn 10 particle mode M/8, coll_cell_factor 2, seed 2, 300 M (seq.sh; JOURNAL.md 2026-11-21T20:25Z)
- `C-20261124-053105-2fcc8af`: failed (exit 1), longruns A334s2c: A: block A M/8, y0 0.334032 seed 2, control, 600 M (seq.sh; JOURNAL.md 2026-11-21T20:25Z)
- `C-20261124-061134-ab6cc0a`: failed (exit 1), longruns A334s2i: A: block A M/8, y0 0.334032 seed 2, kick in, 600 M (seq.sh; JOURNAL.md 2026-11-21T20:25Z)
- `C-20261124-075153-72499e7`: failed (exit 1), longruns A334s2o: A: block A M/8, y0 0.334032 seed 2, kick out, 600 M (seq.sh; JOURNAL.md 2026-11-21T20:25Z)
- `C-20261124-082221-7f03a8e`: failed (exit 1), longruns A334s3c: A: block A M/8, y0 0.334032 seed 3, control, 600 M (seq.sh; JOURNAL.md 2026-11-21T20:25Z)
- `C-20261124-091733-b92f4e5`: failed (exit 1), longruns A334s3i: A: block A M/8, y0 0.334032 seed 3, kick in, 600 M (seq.sh; JOURNAL.md 2026-11-21T20:25Z)
- `C-20261124-120250-9e6a3ba`: stopped (exit 1), longruns A334s3o: A: block A M/8, y0 0.334032 seed 3, kick out, 600 M (seq.sh; JOURNAL.md 2026-11-21T20:25Z)
- `C-20261124-130433-e84cb43`: failed (exit 1), D2: t_c and collision rate against coll_cell_factor 1, 2, 4 on M/8 (D2.1-D2.3, control); lead batch 11
- `C-20261124-130951-36beb5c`: failed (exit 1), heat series: conductivity against cell size and step on the card (H.1-H.4); lead batch 11
- `C-20261124-131221-49d5fcc`: failed (exit 1), decks of the batch-11 follow-ups: N-series controls (N = 1e4, 1e6) and D2 on M/16; lead batch 11
- `C-sidm-20261115-120801-38ab057`: failed (exit 1), C-pre-4 Tests 1-2: paper values (2009.08163 table, gr-qc/0601112 Tables 1,2,4), Newtonian limit, King turning point, and the offline checks of the 13 equilibria and their 10^4-particle files

## Open risks


State 2026-11-25 (lead, batch 20; rows 3, 5, 18, 19, 23 changed, 24 and 25 new). Numbers carry run ids or locators; see
`stage/G0/REPORT.md`, `stage/REVIEW-wave2.md` and `stage/REVIEW-wave3.md` for the sources.
L = likelihood, E = effect (high, medium, low).

| Risk | L | E | Watch | Response |
|---|---|---|---|---|
| 1. Stiff collision term at small Kn: N needed grows as Kn^-3 (King threshold: N >= 1.7e3 Kn^-3 for dx <= lambda and 20 per cell); sub-steps ~ dt Gamma/0.1 | high | high | T8 passed on one card seed (C-20261120-223321-3d088d4); max dx/lambda and min N per cell in `coll.hst` | scan stops at Kn_c = 0.3 unless N allows 0.1; the fluid end comes from the exact fluid onset with the Juttner Gamma_1 |
| 2. The collisionless threshold of core-halo families may not sit at the binding-energy maximum (2105.05556 `paper.tex:88-89, 599, 612`); on the M/4 mesh CC1 (at the E_b maximum) oscillates with a finite frequency (drift entry 4, JUDGEMENT) | medium | high | omega^2(y0) from the controls (CC1 399 M, CC2 355 M, D3 282 M at M/4); run (iii) CC1 at M/8 | locate the threshold also as the zero of omega^2(y0) measured on the controls; G2 wording of decision 0013 |
| 3. Mesh effect on the equilibrium: the outward excursion of the M/4 controls is numerical (C-20261121-075359-26e3b31); the collisional t_c converges with the mesh, 206.64, 163.41, 158.42 M on M/4, M/8, M/16 (C-20261125-122020-031b67e), the last step 3.1 per cent against an unknown seed scatter; the M/16 region covers only |x| < 1.95 M of a cluster of radius 12.5 M | medium | high | q0024 (D2 seed pair); A16b344, A16b324 (bracket on M/16 at N = 1e6, B20.1, B20.2) | read every fate against a control of the same mesh, N and seed; a third mesh if B20.2 fails |
| 4. Physical Kn of relativistic SIDM cores is ~1e-19 (run C-sidm-20261115-115400-eb8b752) against Kn >= 0.3 in the code | certain | high | — | frame the result as the collisionless-to-fluid bridge; physical statements through the Kn -> 0 anchor (Juttner Gamma_1 onset: Z(0) = 0.5331 for F21 b = 0.1, y0 = 0.32143 for King) |
| 5. Card budget: ruling 0039 item 3 sets 80 card-hours toward G2; `nrpic-run budget` still counts 60 (G2 used 31.09 after A324s1c+ was closed at 1.77); queued about 7.5 (q0046-q0048, q0018, q0022-q0024) plus about 18.4 for the four legs of batch 20 | medium | high | `nrpic-run budget`; actual cost of the first M/16 member | the M/16 cost is an estimate (ratio 2.4 from the collisional pair); if A16b344 costs more than 8, drop A16b324's last 200 M rather than ask |
| 6. Choice of initial model sways the answer: King models collapse with collisions after 2.5-15 collisions per particle; D3 (y0 = 0.26, 8.7 times CC2's distance from the onset) still collapses at Kn = 1 (100.5 M) and contracts at Kn = 10 (decisive, C-20261121-052720-75f3fff, -062412-7473ef1) | high | high | contraction per collision against model and Kn | report every model with its distance from both onsets; F21 b = 0.1 models in the scan |
| 7. Gravothermal contraction makes any model collapse eventually; on M/8 at N = 1e5 the collisionless controls collapse within 600 M by particle-noise relaxation (N6c at N = 1e6 holds, C-20261125-122010-fb3cc08) | high | high | contraction rate per collision; controls of the same N | collisional effects as collapse-time differences against controls of the same mesh, N, seed; collisionless threshold at N = 1e6 |
| 8. Particle noise and the intrinsic core oscillation near threshold; growth rates on runs are window-dependent (ln d concave on the first paper's y_c = 0.5 runs, models D2, C-20261120-223404-40668db) | high | medium | rates with their interval and seed scatter | three-way convergence of the omega^2 zero and of collapse times, not of a single growth rate |
| 9. Seed scatter near the threshold: t_c of CC1 at Kn = 10 scatters by about 3 M (sd 2.83 M over five runs; CC2 0.21 M over four), runs C-20261121-075202-1a37fb9 | certain | medium | seeds per model | at least three seeds per model within about 0.02 in y0 of the threshold |
| 10. Card runs are not byte-reproducible and the collisions-2 card executable differs from the release at rounding; the drift runs use the core-v0.3 card executable (sha256 f9f2dc12..., needed for exact restarts); core-v0.6's merged card executable had its card check pending at tagging (job 4800) | medium | low | core's RELEASE-v0.6.md | collisional comparisons by seed scatter; a scan block runs on one executable throughout, controls included |
| 11. Equal masses required for exact pairwise conservation and thermalisation (collide `SPEC.md` 4.4) | low | medium | `coll_weights = equal` fatal error | equal-mass sampling for every collisional run |
| 12. Reproducibility with the mesh metric only to rounding between MeshBlock divisions (core `rng.md` 5); collisions stop on more than one MPI rank (core-v0.5) | certain | low | T10 with the analytic metric | bitwise claims only for analytic-metric boxes; request to core (outbox collisions-several-ranks) |
| 13. Collapse leaves the static mesh unable to hold the black hole: histories not valid after the first excision, some runs go non-finite (decisive) | certain (static mesh) | medium | constraint norm after collapse; `<z4c_guard>` of core-v0.5 stops non-finite runs (exit 3) | refined mesh with collisions (request to core, open); excised fraction is a proxy until then |
| 14. Competition: Misner-Sharp group (2601.17117 `SIDM_MS.tex:514`), Gurian and May collisional Boltzmann SIDM (2505.15903), kinetic SIDM halos with a Kn-dependent collapse time (2610.28745, coord/FRONTIER.md) | medium | medium | kb watch | read 2505.15903 and 2610.28745 before G2; 2610.28745 as the Newtonian baseline of the Kn scan; keep the claim to the fully relativistic kinetic 3D calculation |
| 15. Usage limit cuts sessions mid-package (2026-11-19, 2026-11-20): uncommitted work stranded in the worktree; none stranded at the start of batch 4a | medium | medium | git status at every start | commit small and often; packages sized to one window (decision 0020) |
| 16. Conductivity: settled at the per-cent level by the card series (kappa/kappa_1 = 1.020 +- 0.004 at zero cell and k lambda, C-20261124-131012-f920f45); the relativistic reference V1a is still unreviewed | low | low | G2 verifier | retire after the verifier |
| 17. Test definitions named after the data (collide/TESTS.md 2c: T4 window, T6(b) and T9 reference temperatures; the strict T9 KS reading fails for one class of one seed) may be refused by the G1 reviewer | low | low | the reviewer's report | strict readings kept on record as failed; T9 is not among the tests the brief names in C-pre-1 |
| 18. Block A at N = 1e5 on M/8 is unfit for the scan (A.4 failed with all three controls, 534.8, 549.3, 599.99 M; C-20261125-160056-a5b7282); cause: particle-noise relaxation (NS.1 held). The bracket at N = 1e6 has one seed per model | medium | high | q0046, q0047 against B17.5, B17.6 | a second seed at N = 1e6 for the model nearest the threshold once the bracket is read |
| 19. Closing continued chains: fixed on main (decision 0039 item 5): `nrpic-run finish <run id>` closes them (A324s1c+ closed in batch 20); `qitem.sh close` still adds `--status` | low | low | qitem.sh close output | use `nrpic-run finish` directly for continued runs; retire the `--status` branch of qitem.sh |
| 20. Disk: restarts every 10 M for the continued and new runs (up to 66 GB per 600 M run; about 0.6 TB for the queue) under scratch/C-sidm; 18 TB free | medium | low | `du -sh scratch/C-sidm` | after analysis, remove restart files that are not multiples of 100 M by literal path |
| 21. Preemption by another user's jobs in the partition `priority`: ten chains ran out of segments 2026-11-23/24; N6c and M16 each lost their first segment to it and finished | high while it lasts | medium | chain events.log, `sacct` | restart every 10 M; resume items; segment floor 20; the core-v0.7 chain script does not count a signalled attempt |
| 22. The collision-count test before t_c deviates at the largest collision cells (z = -3.39 at f = 4; n_balance 2.6 per cent) | medium | low | `d2.json` count_z_before_tc | G2 verifier item (OPEN.md) |
| 23. Decks of batches 17 and 20 run on the core-v0.6 card build without `dt_gauge` (series continuity); ruled acceptable by 0039 item 3 (members on the executable and step rule of their control, cfl_number 0.25 below 0.47) | low | low | - | retire once the queue entries have run |
| 24. Collapse marker: every t_c is the alpha_min = 0.3 crossing, slicing-dependent; no run had the horizon finder (C-20261125-160207-05b6db1, decision 0040 item 3), and the v0.6 finder's outputs do not survive a chained restart (core-v0.8 fixes it) | certain | medium | B20.3 (gauge leg) against B17.4 | if t_c moves by more than 5 per cent with shift_eta, add the finder with `diagnostics = true` on core-v0.8 for the bracket members and read horizons only from the status file |
| 25. A chain cut before its first periodic restart restarts from the t = 0 file: A334s3c ran four segments that each began at t = 0 (history ends at 0.25 M); q0023 reruns it from t = 0 | certain for that run | low | chain events.log (`athena -r .../cc.00000.rst`) | restart every 10 M in every new chain (resume items pass output2/dt=10; new decks have dt 10) |

## Decision requested from the group

G2 NOT met (lead, batch 20): 7 of 20 items pass, 4 fail (C1, C2, C7, C9), 9 open. The threshold bracket at N = 1e6 (q0046, q0047) and its mesh and gauge legs (q0055-q0058, ruling 0039 item 3) wait in the shared queue; no collapse time rests on a horizon search (C-20261125-160207-05b6db1). verify: the one failing run is N4c, pending in Slurm (job 5297). Not ready for a verifier.
