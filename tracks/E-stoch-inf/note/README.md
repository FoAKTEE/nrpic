# note: working note v0 of Track E (gate G0, feasibility)

Helper package of E-stoch-inf, wave 2 (2026-11-15). The REVTeX working note of S11
(stochastic inflation in numerical relativity), its data figures and the two schematics of
the stage check, the numerical ledger, and a check of the numbers printed in the lead's
documents against the run outputs. Predictions and outcomes: `JOURNAL.md`. Guide and
notation (paper-writing skill, one level above the manuscript): `../WRITING_GUIDE.md`,
`../NOTATION.md`.

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, two columns, 9 pages) and its compiled pages |
| `figures/fig_*.{pdf,png}` | data figures, each made by `scripts/<same name>.py` from outputs of registered runs |
| `figures/schem_*.{png,svg}` | architecture (exists / to be ported / new) and stage timeline, `paperfig.py` |
| `tables/ledger.tex`, `tables/parameters.tex` | ledger appendix (numbers with run labels R1-R7) and parameter table, written by `scripts/ledger.py` |
| `tables/claims.md`, `tables/claims.json` | 59 numbers printed in SPEC.md, SCOPE.md, EVIDENCE.md and langevin/README.md, recomputed from the run outputs (written by `scripts/ledger.py`) |
| `scripts/common.py` | the runs the note reads; every input checked against the sha256 its manifest records |
| `scripts/costmodel.py` | the scoping cost model with core's measured card throughput in place of the assumed overhead |
| `scripts/run_all.py` | runs every `fig_*`, `schem_*` and `ledger.py` into one directory and repeats each figure (PNG identity) |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` |

Registered runs of this package: E-20261115-172421-50ac4ce (failed: scratch root taken from
the harness variable `NRPIC_SCRATCH`; JOURNAL 17:24), E-20261115-172442-78cf53e (completed;
superseded: legend of fig_deltan on the data, ledger column too narrow),
E-20261115-173135-858482f (completed; superseded: exponent format in two ledger rows), and
the run whose id is in the last commit touching `figures/` and `tables/` (see `JOURNAL.md`,
final entry), whose outputs are the committed figures and tables.

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`):

    harness/bin/nrpic-run submit --kind scouting --gate G0 --package tracks/E-stoch-inf/note \
        --purpose "note v0: figures, schematics, ledger" -- \
        bash -c '.venv/bin/python tracks/E-stoch-inf/note/scripts/run_all.py --out "$NRPIC_RUN_DIR"'
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/E-stoch-inf/note && latexmk -pdf main.tex
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'nrpic-run|nrpic-stage|SCOPE\.md|SPEC\.md|EVIDENCE|langevin/|codebase/|wt/|scratch/'

Each figure script also runs alone from `scripts/` (`python fig_cost.py`, output to
`figures/`), which is what `harness/bin/nrpic-stage verify` does. The scripts read absolute
paths under `/data/haiyangw/nrpic/scratch/` (override: `NOTE_SCRATCH_ROOT`).

## State (2026-11-15)

Done: note v0 compiled (checker: 0 undefined references or citations, 0 overfull boxes;
remaining candidates are the run ids of the ledger appendix and the document names in the
scripts, accepted by exception 1 of `../WRITING_GUIDE.md`); five data figures and two
schematics, each looked at; ledger and parameter table from registered runs; claims check
(59 numbers, 54 agree, 5 differ: list below); `../stage/G0/STAGE_REPORT.md` from
`nrpic-stage collect`, `verify` and `report`.

Not done: the reviewers of step 4 of the paper-writing procedure (no subagent tool in this
session); a verifier's recomputation of the ledger (C16 stays open); the end-of-inflation
statistics and the importance sampling of the delta-N package are cited only as open items.

## Disagreements between the lead's documents and the files (the files win)

1. Overhead of the scalar field and the stochastic sources over Z4c on a card: assumed 15
   percent (`spec/scope/SCOPE.md:191`, cost model `codebase/ref/cost.py`) and 30 percent
   (`spec/SPEC.md:499`); measured by core at 128^3 with the sources: Z4c 1.98e7, with the
   field 1.39e7, with the sources 1.20e7 zone-cycles/s, i.e. 65 percent (run
   core-20261115-143907-cea4c86, `summary.json`). Claims c16, c19.
2. Cost of one 256^3 realisation: 0.4-0.5 card-hours (`SCOPE.md:202`, `:223`, `:233`); with the
   measured throughput and the synthesis scaled by its operation count, 0.57-0.71 (SR) and
   0.71-0.88 (USR) card-hours; 1e3 realisations 570-880 instead of 400-500 card-hours
   (`scripts/costmodel.py`, an extrapolation from one measured box size; claims c17, c18). The
   conclusion of SCOPE.md 9 (far below the 5 card-hour threshold) still holds.
3. USR eps1(N*): 1.3164e-2 (`SPEC.md:304`, reference run E-stoch-inf-20261115-122806-ef0d039)
   against 1.31625e-2 of the lead's integrator (run E-20261115-135532-3f958a1); already
   recorded in `stage/G0/EVIDENCE.md:35`. Claim c21.
4. `spec/SPEC.md:374-375` says the thresholds are fixed "in `../stage/G0/REPORT.md` section 4";
   they are in `spec/scope/SCOPE.md` section 4 (no REPORT.md, decision 0012).
5. State of the code: `SCOPE.md` section 6, `stage/G1/STATUS.md` and `HANDOFF.md` describe the
   scalar field on the unmerged branch `core/scalar-field` (836ac86) and a missing card build;
   release core-v0.3 merged it with card and processor executables (CLAUDE.md; core's message
   `tracks/core/outbox/20261115T1510Z__to-E-stoch-inf__scalar-field-merged.md`). The release
   forms the tanh window increment as sinh(x1 - x0)/(2 cosh x1 cosh x0)
   (`athenak/src/scalar_field/scalar_field_noise.cpp:570-577`, read), unlike the 836ac86
   executable that the noise validation (E-20261115-140502-2957846) used.
6. Locator key `VS = 1308.4754` (`SCOPE.md:15`) suggests Vennin-Starobinsky; the source of
   1308.4754 v2 is Fujita, Kawasaki, Tada and Takesako, "A new algorithm for calculating the
   curvature perturbations in stochastic inflation" (its `\title` and `\author` lines in
   `kb-data/raw/arxiv/1308.4754/v2/src`). A naming issue only.

## Requests

- To the lead of E-stoch-inf: (1) carry disagreements 1, 2 and 4 into `SCOPE.md` sections 8
  and 9 and `SPEC.md` 7.2 and 11.2 (or state why the scoping numbers stay); (2) update
  `stage/G0/OPEN.md` items 2, 3 and 5 (note, schematics and stage check now exist) and
  `EVIDENCE.md` with the note's run; (3) add the line
  `cd tracks/E-stoch-inf/note/scripts && python ledger.py` to a `stage/G0/VERIFY` file so that
  `nrpic-stage verify` also regenerates the ledger and the claims check; (4) commission the
  verifier report (C16) and write the "Decision requested" paragraph of `STAGE_REPORT.md`
  (a draft is in it); (5) rewrite STATUS/HANDOFF for wave 2 (C18).
- To core (through the lead): a card measurement of one 256^3 step of the SR set-up with the
  sources (MeshBlock 64^3 and 128^3) would replace the extrapolation of disagreement 2.
- To orch: `nrpic-run` exports `NRPIC_SCRATCH` as the owner's scratch directory; a script
  that reads several owners' runs needs the scratch root as well (a variable such as
  `NRPIC_SCRATCH_ROOT` would avoid the failure of run E-20261115-172421-50ac4ce).
- To kb: the key statements and the errata of the references are still raw-store locators
  only (C2 of G0 stays FAIL).
