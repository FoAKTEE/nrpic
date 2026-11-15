# Stage report: D-bh-dress G0

Date: 2026-11-15 · branch `track/D-bh-dress` at `18706fb80925` · checklist
`tracks/D-bh-dress/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/D-bh-dress/G0-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 8 checklist items not PASS or NA: C5 OPEN, C6 OPEN, C7 OPEN, C9 OPEN, C10 OPEN, C14 OPEN, C15 OPEN, C16 OPEN
- no VERIFY_RESULTS.json (run nrpic-stage verify)
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | written by this command |
| `stage/G0/EVIDENCE.md` | present |
| `stage/G0/OPEN.md` | present |
| `stage/G0/CHECKLIST.md` | present |
| `stage/G0/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `scope/SCOPE.md` |
| `stage/G0/REPORT.md` | written in wave 1, accepted as it is (decision 0012) |

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | REPORT.md sections 1-4; scope/SCOPE.md | PASS |
| C2 | The statements of the key references verified in the knowledge base | scope/REFERENCES.md (18 sources, locators); REPORT.md section 5 (re-read by the lead) | PASS |
| C3 | Risk list | REPORT.md section 6; RISKS.md; scope/SCOPE.md section 8 | PASS |
| C4 | Compute estimate | REPORT.md section 7; runs D-bh-dress-20261115-120304-795eee9, -145950-23fa1c7 | PASS |
| C5 | Working note v0 | no REVTeX note yet (OPEN.md item 1) | OPEN |
| C6 | Architecture schematic | not drawn (OPEN.md item 2) | OPEN |
| C7 | Stage timeline | text in REPORT.md section 8; schematic not drawn | OPEN |
| C8 | (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA) | the sheet has no G0-specific criterion | NA |
| C9 | Schematic: Track architecture (three states: exists, to be ported, new) | OPEN.md item 2 | OPEN |
| C10 | Schematic: Stage timeline | OPEN.md item 2 | OPEN |
| C11 | Data figure: None required | none required | NA |
| C12 | Data figure: Data from the literature may be redrawn | optional | NA |
| C13 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | scope/figs/scoping_estimates.png from run D-bh-dress-20261115-120304-795eee9 with python/nrpic/figstyle.py; looked at | PASS |
| C14 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | OPEN.md item 2 | OPEN |
| C15 | Working note written with /paper-writing; its manuscript checker passed with --compile | OPEN.md item 1 | OPEN |
| C16 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | OPEN.md item 3 (lead re-checks are not artefact-only) | OPEN |
| C17 | Null results and failed runs are on record (manifests and JOURNAL) | EVIDENCE.md lists failed and superseded runs; journals | PASS |
| C18 | STATUS.md, JOURNAL.md and HANDOFF.md are current | rewritten in the lead session of 2026-11-15 | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

Not run: `harness/bin/nrpic-stage verify D-bh-dress G0`.

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | to be confirmed by the session |
| note/figures/fig_es.* | note/scripts/fig_es.py | data | to be confirmed by the session |
| note/figures/fig_floor.* | note/scripts/fig_floor.py | data | to be confirmed by the session |
| note/figures/fig_infall.* | note/scripts/fig_infall.py | data | to be confirmed by the session |
| note/figures/fig_spike.* | note/scripts/fig_spike.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported.

## Null results and failed runs

- `D-bh-dress-20261115-121837-987643b`: failed (exit 1), Test 1 of D-pre-3: radiation-era turnaround of dark matter around a hole against the printed numbers of 2106.07480 (Table 1, eta_ta) and 1901.08528 (ratios 0.964, 0.999; radial-orbit factor 53 %)
- `D-bh-dress-20261115-122303-4e8e8af`: failed (exit -15), Test 2 of D-pre-3: Bertschinger-type self-similar collisionless infall onto a point-mass seed in Einstein-de Sitter by fixed-point iteration (inner slope, caustics, normalisation against the frozen-in estimate)
- `D-bh-dress-20261115-125449-60a62b8`: failed (exit 1), Analysis of tests 2 and 3 of D-pre-3 and the parameters of the AthenaK runs (closed-form checks, growth of turnaround, dress and hole mass, self-similarity at a/a_i=100, predicted profiles for eps 0.01 and 0.03, capture with angular momentum, cost from the scoping model)
- `D-bh-dress-20261115-125724-464611f`: failed (exit 1), P2a-d analysis of run A: stationarity, invariants, empty loss cone

## Open risks


| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R1 Release card executable pushes massless tracers wrongly (run D-bh-dress-20261115-143918-a5c125a: five of six leave the mesh near light speed, one excised at 0.31 M; earlier executable correct) | known, cause unknown | every particle result on cards is suspect; ES-1 tracer test meaningless | core's answer to outbox tracer-push-release-build | no matter run on cards before it is explained; ES-1 wall tracers are themselves the acceptance test |
| R2 No lapse for a puncture inside expanding dust: 1+log and conformal-time lapse send fronts from a surface (core JOURNAL-id entry 8); along the dust 1+log gives alpha = 1 + 6 ln a, 4.9 at tau = 200 M (run -145950-23fa1c7) | high | transients at the hole; drift above the floor; instability | lapse at the dust edges and at the hole in ES-1 | outbox lapse-for-expanding-dust; judge every gauge by M_AH = M exactly and the wall tracers |
| R3 The D-pre-4 floor (2.0-2.5e-5 at M/16) belongs to an asymptotically flat vacuum puncture with the boundary at 128 M, not to the ES configuration | certain | a floor that is too low or too high for the null test | V-1 against D-pre-4 | matched vacuum control V-1 for every ES run |
| R4 Boundary attribution of the D-pre-4 excursions (9.3e-5 at 220-255 M, 1.5e-4 at 300-340 M, same at M/8 and M/16) untested | medium | floor windows limited to before 210 M | boundary control | 500 M run at M/16 with the boundary at 256 M (about 1.8 card-hours) |
| R5 Particle resolution and noise next to the puncture (matter near the puncture gave non-finite cells at M/64 until horizon removal, TESTLOG:1949-2053) | high for matter runs | spurious accretion or crash | n_excised, NaN in nrpic.hst column 3 | `ah_exc_factor = 0.8`, cloud level cap, N scan |
| R6 Numerical relaxation of a dress (1e2-1e4 particle clusters, TESTLOG:690-1022) | medium | spike flattened, loss cone refilled | capture rate N vs 4N | relaxation control at G2 |
| R7 Format-2 reader only on core/id-extrinsic | until merged | ES-1 cannot use release executables | main | outbox merge-format2-reader |
| R8 Outer boundary with K_ij ~ r^(-3/2) (Painleve-Gullstrand exterior) | medium | reflections reach the hole | constraints near the boundary | boundary at >= 180 M; core request |
| R9 Cost of large dust regions: ES data as generated costs 11.3 card-hours at M/16 for 200 M | certain | budget | scoping model | outer dust edge at 60 M (1.4 / 2.9 card-hours at M/8 / M/16) |
| R10 Over-claiming the null result: the claim's paper itself assigns k = 0 to Kerr (2302.07878 `paper_couple_rev.tex:132`) | medium | a misleading paper sentence | wording review | SCOPE.md 3.5-3.6 wording, second-agent review requested |
| R11 Defaults: finder `metric_drvts = stored` (fastflow.cpp:89) and `ah_exc_factor` off (nrpic.cpp:118) on main | certain | horizon mass 2-6 per cent low; matter kept at the puncture | every input | every Track D input sets both explicitly |
| R12 Mixed time zones in run ids: einstein_straus ids 0426xx-0434xx and the lead's -065141-5fdc744 are local time (UTC-8) | done | ordering of runs by id misleads | | nrun.py uses UTC since 5259f48; ids kept, noted in JOURNAL.md |

## Decision requested from the group

One paragraph: accept G0 of D-bh-dress, or what is missing.

TO WRITE by the track before the package is submitted (`nrpic-stage report ... --decision "..."`).

## Products of the note package (helper of wave 2; for the lead to carry into CHECKLIST.md)

Written by the note helper after `nrpic-stage report` ran on 18706fb; the criteria table above
is generated from the lead's `CHECKLIST.md` of wave 1, which this helper may not edit. Paths
relative to `tracks/D-bh-dress/`. Proposed status of the items that the table shows OPEN:

| # | Item | Evidence | Proposed |
|---|---|---|---|
| C5, C15 | Working note v0, written with /paper-writing, checker with --compile | `note/main.tex`, `note/main.pdf` (10 pages, compiled with latexmk, no undefined reference or overfull box, pages read); guide and notation `WRITING_GUIDE.md`, `NOTATION.md`; checker clean on 14 of 16 checks, the two remaining (5.5 run ids, 5.8 project names) only in the ledger appendix and in the registration scripts, the exception of `WRITING_GUIDE.md` (plus one data key `..._a100` that matches the hardware pattern) | PASS |
| C6, C9, C14 | Architecture schematic (exists / to be ported / new), paperfig.py | `note/figures/schem_architecture.png` (`note/scripts/schem_architecture.py`), run D-bh-dress-20261115-171627-18706fb; looked at | PASS |
| C7, C10, C14 | Stage timeline schematic | `note/figures/schem_timeline.png` (`note/scripts/schem_timeline.py`), same run; looked at | PASS |
| C13 | Data figures from registered outputs, czstyle, one script each, PNG looked at | five data figures `note/figures/fig_{es,constraints,floor,spike,infall}.png`, each from its script in `note/scripts/` (vendored `czstyle.py`, unchanged), reading only outputs of registered wave-1 runs (`note/scripts/common.py`); every PNG read by the helper; registered run D-bh-dress-20261115-171627-18706fb (by hand: `nrpic-run` refused, see below) | PASS (adds to the lead's evidence) |
| C16 | Verifier subagent, VERIFIER_REPORT.md | not part of this package; a verifier helper works under `stage/G0/verify/` in the same wave | OPEN |
| C18 | STATUS, JOURNAL, HANDOFF current | they describe the end of wave 1 (note and schematics "missing"); to be rewritten by the lead | lead |

Figures of the table "Figures" above: all seven PNGs were looked at by the note helper
(`note/JOURNAL.md`, entry 17:15Z).

## Re-verification by the note helper (not `nrpic-stage verify`)

`nrpic-stage verify` was not run: it writes VERIFY_RESULTS into this directory, which the
note helper may not write. What was re-run instead: `note/scripts/run_all.py` twice as
registered runs D-bh-dress-20261115-171128-38634d6 and -171627-18706fb (the second after
script changes that touch only the ledger layout); all seven PNGs of the two runs are
byte-identical. The claims check (`note/tables/claims.md`) recomputes 36 numbers of
`stage/G0/REPORT.md`, `stage/G1/STATUS.md` and `STATUS.md` from the run outputs: 31 agree to
the printed digits, five need a remark (the files win):

1. `stage/G1/STATUS.md:13` "dress 0.625 M_ta (-123813-97afeea)": that run prints the mass
   inside the outermost caustic, m(lambda_1) = 0.654 M_ta; 0.625 is `f_passed` = 0.6247 of the
   analysis run D-bh-dress-20261115-125613-248fdaf. Locator to be corrected.
2. `stage/G1/STATUS.md:11` "order 5.8-5.9 in the curvature transition": 5.88 (H) and 5.76 (M)
   hold in the box "mid transition"; over the whole region 4 < r < 30 M the same run
   (-043406-4df1e76) gives 5.29 and 4.69.
3. `stage/G1/STATUS.md:12` "against digitized SFW Fig. 1 to 0.02 per cent": true for the peak
   (1.5e-5 in height, 1.5e-4 in position); the whole curve on 8.5-95 Gm deviates by up to
   2.6e-3 (run -145636-5259f48).
4. `stage/G1/STATUS.md:52` (and `REPORT.md` section 3, G2 (a)) "reach R = 2M at tau = 15.0 M
   and 34.6 M": these are the first samples of the 0.2 M grid of `es_reference.csv` after the
   crossing; the exact infall times from each group's energy are 14.83 M and 34.44 M (and
   244.74 M for the 20 M group). The G2 criterion should quote the exact values.
5. `stage/G1/STATUS.md:37` (and `REPORT.md` section 7) "V-1 about 1.2 card-hours": a
   judgement; the cost table of run -145950-23fa1c7 has no vacuum-control row (its 1.24 row is
   the dust run with particle spacing 2 M). To be computed with the model before submission.

Also: `REPORT.md:101` cites the simulation run -123755-25227d4 for |dE/E| <= 1.3e-6 and
|dL/L| <= 1.9e-10; the values are in the analysis run -125739-a18d74d.

## Draft for "Decision requested" (for the lead; not passed with --decision)

G0 of D-bh-dress is complete in content: the scoping text (`scope/SCOPE.md`, `REPORT.md`
sections 1-8), the risk list, the compute estimate, the working note v0 with five data
figures and the two schematics, and a check of the package's numbers against the run
outputs (five remarks above, none changing a conclusion). Missing before acceptance: the
fresh verifier's VERIFIER_REPORT.md, `nrpic-stage verify` on the committed tip, the transfer
of the proposed statuses into CHECKLIST.md, and the corrections 1-5 above. The group is asked
to accept G0 once these are in, and to note that G1 is met for the benchmark and the floor
and partly met for the spike (Kerr open) and the infall (AthenaK Newtonian mode open).
