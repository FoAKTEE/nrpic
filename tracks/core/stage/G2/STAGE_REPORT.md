# Stage report: core G2

Date: 2026-11-15 · branch `core/nrpic` at `9377fe8bdd97` · checklist
`tracks/core/stage/G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/core/G2-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 11 checklist items not PASS or NA: C1 FAIL, C2 FAIL, C5 FAIL, C6 FAIL, C7 FAIL, C8 FAIL, C9 FAIL, C11 FAIL, C13 FAIL, C14 FAIL, C15 FAIL
- no VERIFY_RESULTS.json (run nrpic-stage verify)
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Criteria (coord/CHARTER.md, gate G2 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The code paths used by the track pass their tests of §10 | Rows 1 (geodesics) and 2 (dust collapse) PASS on the merged source 609a875 (runs core-20261115-065452-3629622, -065901-3629622); rows 3 (prolate/oblate) and 4 (cluster threshold) PARTIAL (verify/LADDER.md; OPEN.md items 2-3). New capabilities each pass their own tests (EVIDENCE.md). | FAIL |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | Shown piecewise only: dust collapse in particle number at fixed mesh (LADDER.md row 2), expanding ball in mesh (JOURNAL-id.md), Newtonian collapse in mesh (JOURNAL-newton.md); no single three-way study (OPEN.md item 4). | FAIL |
| C3 | Constraints behave | Dust collapse //H// equal to the earlier run (core-20261115-065901-3629622); homogeneous universe H-norm2 3.7e-10, /Theta/ 1.1e-11 (core-20261115-065903-3629622); format-2 data: vacuum momentum residual sixth order (JOURNAL-id.md test 1); Bowen-York residual sixth order (JOURNAL-mp.md test 1a); scalar plane perturbation orders 5.2-6.0 (JOURNAL-scalar.md test 3). Sharp surfaces leave a non-converging constraint sheet (OPEN.md item 7). | PASS |
| C4 | A first minimal full-GR kinetic run | Self-gravitating dust collapse with Z4c on the merged card executable, horizon mass to 6.3e-4 (core-20261115-065901-3629622); cluster with collisions at Kn = 30 and 3 (core-20261115-140316-8742cdf, -142625-67f8c1d). | PASS |
| C5 | Verification report | No REPORT.md: the write of tracks/core/stage/G2/REPORT.md was refused by this session's write guard for subagents; its content is in EVIDENCE.md, OPEN.md, this checklist, STAGE_REPORT.md (nrpic-stage report) and JOURNAL.md (lead entry of 2026-11-15T14:53Z). | FAIL |
| C6 | Reproducibility package | Manifests of every run committed (tracks/core/runs/), scripts in tracks/core/verify/regress/ and tracks/core/analysis/; nrpic-stage verify (clean-export rerun) not run. | FAIL |
| C7 | All of C3 passed, core-v0.1 released | C3 rows 3 and 4 PARTIAL; core-v0.1 not tagged yet (proposal verify/RELEASE.md; core-v0.3 proposal CHANGELOG.md). | FAIL |
| C8 | Schematic: Verification ladder | No schematic of the ladder yet. | FAIL |
| C9 | Data figure: Convergence figures (one each for particle number, mesh, gauge) | Convergence figures exist per package (analysis/mp/figs/static_convergence.png, analysis/id/figs/t1_exterior.png, notes/scalar_figs/fig_wave_convergence.png, analysis/newton/field_point.png), not the three of 13.4 for the coupled module. | FAIL |
| C10 | Data figure: Constraint norms against time | verify/figs/regress_os_core-20261115-065901-3629622.png (//H// against t), verify/figs/regress_flrw_core-20261115-065903-3629622.png, analysis/id/figs/t2_constraints.png, notes/scalar_figs/fig_flrw_conformal.png. | PASS |
| C11 | Data figure: At least one multi-scale slice mosaic with zoom boxes | No slice mosaic with zoom boxes in this package. | FAIL |
| C12 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | Figures of this wave use python/nrpic/figstyle.py (zoom style) and were drawn from registered runs; the ones the lead relied on were opened (EVIDENCE.md, column "looked at"); interfaces/figs/d1_*.png were not opened by the lead. | PASS |
| C13 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | No track architecture schematic or gate timeline. | FAIL |
| C14 | Working note written with /paper-writing; its manuscript checker passed with --compile | No working note under tracks/core/note/. | FAIL |
| C15 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | No VERIFIER_REPORT.md; the lead rechecked the packages from their artefacts (JOURNAL.md), which is not a fresh-context verifier. | FAIL |
| C16 | Null results and failed runs are on record (manifests and JOURNAL) | Failed runs and refuted predictions are in the journals (JOURNAL.md P5 first criterion; JOURNAL-id.md, -coll.md, -mp.md, -newton.md, -rng.md, -scalar.md) and their manifests are committed. | PASS |
| C17 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten at the end of this session. | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

Not run: `harness/bin/nrpic-stage verify core G2`.

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|

## Verifier report

MISSING: the verifier subagent has not reported.

## Null results and failed runs

- `core-20261115-113512-a5197ba`: failed (exit 1), Regression R on a card: two punctures at rest with adaptive mesh, trackers, horizon finder and tracers (problems/puncture/tracers_headon.athinput), 24 cycles, executable built from main
- `core-20261115-113513-a5197ba`: failed (exit 1), Regression R on a card: same input, executable of this branch
- `core-20261115-113844-c89b6e3`: failed (exit 1), Test 1a (iv): P = 0.3, closed-form correction
- `core-20261115-113848-c89b6e3`: failed (exit 1), Test 1a (iv): P = 0.3, closed-form correction
- `core-20261115-113849-c89b6e3`: failed (exit 1), Test 1a: P = 0.3, tabulated second-order correction (must agree with approx)
- `core-20261115-113850-c89b6e3`: failed (exit 1), Test 1a (iv): scaling with momentum, closed-form correction
- `core-20261115-113853-c89b6e3`: failed (exit 1), Test 1a (v): P = 0.3, tabulated full correction
- `core-20261115-113855-c89b6e3`: failed (exit 1), Test 1a (iv): P = 0.3, closed-form correction
- `core-20261115-113856-c89b6e3`: failed (exit 1), Test 1a (v): P = 0.3, tabulated full correction
- `core-20261115-113857-c89b6e3`: failed (exit 1), Test 1a (v): P = 0.3, tabulated full correction
- `core-20261115-113858-c89b6e3`: failed (exit 1), Test 1a (iv): scaling with momentum, closed-form correction
- `core-20261115-113859-c89b6e3`: failed (exit 1), Test 1a (vi): spin 0.4 along z, closed-form correction
- `core-20261115-113900-c89b6e3`: failed (exit 1), Test 1a (vi): momentum and spin not parallel, no correction
- `core-20261115-113901-c89b6e3`: failed (exit 1), Test 1a (iv): scaling with momentum, closed-form correction
- `core-20261115-113903-c89b6e3`: failed (exit 1), Test 1a (vi): momentum and spin not parallel, closed-form correction with cross term
- `core-20261115-113904-c89b6e3`: failed (exit 1), Test 1a (vi): spin 0.4 along z, no correction
- `core-20261115-113905-c89b6e3`: failed (exit 1), Test 1a (vi): spin 0.4 along z, closed-form correction
- `core-20261115-113906-c89b6e3`: failed (exit 1), Test 1a (vi): momentum and spin not parallel, no correction
- `core-20261115-113907-c89b6e3`: failed (exit 1), Test 1a (vii): two punctures, closed-form corrections
- `core-20261115-113908-c89b6e3`: failed (exit 1), Test 1a (vi): momentum and spin not parallel, closed-form correction with cross term
- `core-20261115-113909-c89b6e3`: failed (exit 1), Test 1a (vi): spin 0.4 along z, no correction
- `core-20261115-113910-c89b6e3`: failed (exit 1), Test 1a (vii): two punctures with momenta and a spin, no correction
- `core-20261115-113911-c89b6e3`: failed (exit 1), Test 1a (vii): two punctures, closed-form corrections
- `core-20261115-113912-c89b6e3`: failed (exit 1), Test 1a (vii): two punctures with momenta and a spin, no correction
- `core-20261115-115339-7a60df2`: failed (exit 1), Test 1b: Bowen-York puncture m = 1, P = 0.3 along x, closed-form correction, finest cells 1/32, to t = 40
- `core-20261115-115342-7a60df2`: stopped (exit 143), Test 1b reference: stock generator z4c_boosted_puncture, rest mass 1.0112, velocity 0.2844, same mesh, to t = 40

## Open risks


State 2026-11-15, after the wave-1 integration (core-v0.3 proposed at 609a875). Evidence
for each line: `stage/G2/OPEN.md` (item numbers) and the package journals.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| Collision steps raise the energy at the particles' own metric (1e-9 to 1e-8 per collision in a potential; OPEN 6) | certain for Track C science runs at 2 M cells | spurious heating of a collisional core over 1e3 collisions per particle; biases the collapsed-fraction curve | `coll_budget` columns of `.coll.hst`, cumulative gain against the rest mass | smaller collision cells now; decide with Track C on a pair-energy correction at the particles' positions before G3 |
| Lapse front from a sharp matter surface (expanding ball, vacuum bubble; OPEN 7) | high for Tracks A and D | non-convergent core shells after the front arrives (t ~ R/0.58 for the conformal-time lapse) | central lapse against a(tau), core-shell error against the exact solution | smooth edges; try lapse_kdriver, lapse_volume, a dust-slicing driver in wave 2; agree the choice with Track A |
| Paper details filled in independently (deposit order, filter passes, refinement treatment; brief 9.3 main risk) | certain (the paper states first-order CIC and an unstated number of binomial passes, main.tex 641, 680-682) | results differ from the authors' at the 1e-3 level | ladder rows 3-4 | report our choices with each result; no tuning to the paper's numbers |
| Ladder rows 3-4 stay PARTIAL (prolate mass 3-5 percent low at one resolution; cluster collapse times 1.4-1.75 times later than the paper) | medium | G2 of core and of Track C delayed | resolution series of the prolate run, bisection of the cluster threshold | first card runs of wave 2 (about 2 card-hours) |
| Layout dependence of the mesh-metric reconstruction (1e-13; OPEN 8) | low effect, certain occurrence | a stochastic decision u < P can differ between MeshBlock divisions | rng kick demo D2, collision reproducibility on the mesh path | apply the tested gather patch with new baselines, or document the limit |
| One shift damping for all punctures (OPEN 9) | high for Track F at mass ratio 10 | the heavy tracker lags, refinement and finder off-centre | tracker speed against P/M | mass-scaled eta in the Z4c gauge (wave 2) |
| Vacuum drift of light horizon masses in multi-hole runs (1.3-1.5 percent in 16 M at m/8; OPEN 10) | medium | the Hills energy budget and Track D's null test need horizon masses to 1e-3 | horizon mass of an isolated light hole at two resolutions | resolution study before Track F's first passage |
| Silent failures (status 0 with NaN or no particles; OPEN 11) | medium | wasted card time, wrong results taken as finished | exit status and particle count in every manifest | stop with non-zero status on non-finite state or empty particle set (wave 2, small) |
| Step ignores the lapse (`z4c_newdt.cpp`; OPEN 12) | medium in expanding regions with 1+log | effective Courant number above the nominal one (0.59 at 0.25 seen) | coordinate light speed alpha/sqrt(g_rr) | step limit on alpha/sqrt(gamma) as a separate small change |
| Card runs with deposit are not byte-reproducible | certain | a card byte regression cannot show identity | baseline twice against new | compare on processors, or against the baseline's scatter (scripts/README.md) |
| Single-rank particle module (no MPI), no adaptive refinement for the new modules (OPEN 18) | certain | caps problem size at one card (about 3000 MeshBlocks per card for punctures) | memory per MeshBlock in the logs | plan wave-2 science within one card; MPI is a larger core project |
| Upstream publishes an official NRPIC implementation (brief 9.3) | unknown | duplicate effort; merge decision | kb watch of the upstream repository | decide with the group when it appears |
| Shared release executables lag the source (OPEN 14) | happened | runs silently ignore newer options | option strings in the binary; manifests record the executable | name the core-v0.3 builds in CLAUDE.md after the tag (outbox to orch) |

## Decision requested from the group

Keep core at G2 in progress. Create the tags core-v0.1 (7daed19), core-v0.2 (52c44eb) and core-v0.3 (609a875) and merge core/nrpic into main; ladder rows 3 and 4 are the first runs of wave 2 (OPEN.md).
