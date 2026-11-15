# note: working note v0 of Track B (gate G0)

Helper package of B-emd-gw, wave 2 (2026-11-15). The REVTeX working note of S2
(gravitational waves from structure formation in an early matter era), its data figures and
the two schematics of the G0 stage check, the numerical ledger, a check of the numbers in the
lead's stage documents against the run outputs, and `stage/G0/STAGE_REPORT.md`. Predictions
and outcomes: `JOURNAL.md`. Guide and notation of the note (paper-writing skill, one level
above the manuscript): `../WRITING_GUIDE.md`, `../NOTATION.md`.

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, two columns) and its compiled pages |
| `figures/fig_*.{pdf,png}` | data figures, each made by `scripts/<same name>.py` from registered run outputs |
| `figures/schem_*.{png,svg}` | the two schematics of the stage check (architecture, timeline), `paperfig.py` |
| `tables/ledger.tex` | the ledger appendix: every number of the note with its run id |
| `tables/parameters.tex` | the parameter table of the scenarios |
| `tables/claims.md`, `tables/claims.json`, `tables/claims_summary.tex` | numbers of the lead's documents checked against the files; the sentence the note prints |
| `tables/checked.md` | every file the scripts read, its run, its checksum check, and whether it equals the copy committed by its package |
| `scripts/common.py` | the run ids the note reads; checksum checks against `sha256sums.txt` or the manifest's `outputs_sha256` |
| `scripts/run_all.py` | runs every `fig_*`, `schem_*` and `ledger.py` into one directory (the registered run) |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` |

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`):

    harness/bin/nrpic-run submit --kind scouting --gate G0 --package tracks/B-emd-gw/note \
        --purpose "note v0: figures, schematics, ledger, claims check" -- \
        .venv/bin/python tracks/B-emd-gw/note/scripts/run_all.py
    harness/bin/nrpic-run finish <run_id>
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/B-emd-gw/note && latexmk -pdf main.tex
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'gw_diag|gwdiag|periodic_z4c|verify_cosmo|first_source|make_east|nrpic_cosmo|z4c_linear_wave|athinput|pm\.py|nrpic-run|anta|A100|Slurm'

If `nrpic-run` refuses, `python scripts/run_all.py <dir>` writes the same outputs and a
`sha256sums.txt` into `<dir>` for a manifest written by hand. Each figure script also runs
alone (`python scripts/fig_pancake.py`, output to `figures/`), which is what
`harness/bin/nrpic-stage verify` does.

## State (2026-11-15, 17:05Z)

Done: note v0 (`main.pdf`, 10 pages, REVTeX 4.2; checker clean in the main text, compiled
without undefined references or overfull boxes, every page read), four data figures and two
schematics (each looked at), ledger and parameter tables, the claims check (28 numbers and
statements of the lead's stage documents; 24 agree, 4 differ: `tables/claims.md`), the
checksum and committed-copy check of every file read (`tables/checked.md`), the G0 checklist
items of these products, `stage/G0/STAGE_REPORT.md` from `nrpic-stage report`.
Registered runs: B-20261115-165138-cb53c14, B-20261115-165231-9e29328 (both superseded, kept
on record), B-20261115-165556-a399d4e (the outputs the note uses).
`nrpic-stage verify` on the committed tip: the note's checks pass (export, note, PDF newer
than the sources, style copies, one script per figure, figures regenerated and compared);
it fails on the clean tree and the run manifests because of other helpers' work in flight
in the same worktree (`stage/G0/VERIFY_RESULTS.md`).
Not done: the reviewer subagents of step 4 of the paper-writing procedure for a new paper
(no subagent tool in this session); an independent verifier's recomputation of the ledger
(`stage/G0/VERIFIER_REPORT.md`, owed by the verifier helper, whose runs are in flight).

## Requests

To the lead of B-emd-gw:
1. `stage/G0/OPEN.md`: items 1 and 2 are delivered (note, schematics); item 9 is answered by
   run B-20261115-164616-a6d9477 of the first-source helper (the late TT rise is not the
   spatial-gauge piece; it sits near the grid scale); `RISKS.md` R4 carries the old reading.
2. Correct the four statements that the files contradict (`tables/claims.md`):
   `stage/G0/REPORT.md:88` (lapse error 1.9e-7 at a = 4, 7.0e-8 at a = 36, not "1e-7");
   `stage/G1/STATUS.md:22` (Fourier-symbol agreement within 1 % except the production phase
   at 64 cells, 9.5 %); `stage/G1/STATUS.md:56` (the constraint numbers are those of the
   first record, t = 100 Mpc/h; at the end of the expansion 3.1e-8, 2.5e-9, 3.0e-9, not
   falling from 16 to 32 cells); `stage/G1/STATUS.md:47` (the Newtonian mode and its
   quadrupole history are on main since core-v0.3). Wording: `REPORT.md:50` gives box means
   as "void" values.
3. Write the "Decision requested" paragraph of `stage/G0/STAGE_REPORT.md` (a draft is there),
   re-judge C20 (STATUS, JOURNAL, HANDOFF current for wave 2) and C18 when the verifier
   writes `VERIFIER_REPORT.md`.
4. When the first-source and Newtonian-mode runs finish, add their run ids to
   `scripts/common.py`, rerun `scripts/run_all.py` through `nrpic-run`, and extend Sec. IV
   and V of the note.

To orch:
5. `nrpic-stage verify` fails its `clean` and `runs` checks whenever another helper of the
   same owner has an uncommitted file or a run in flight in the shared worktree, so a helper
   cannot obtain a passing verify for its own package; suggest restricting both checks to
   the packages and finished runs named, or reporting other helpers' state as a warning.
6. The paper-writing procedure for a new paper (step 4, reviewer subagents) needs a
   subagent tool that helper sessions do not have; either grant it or record the step as the
   lead's.

To kb:
7. The key references are still raw-store locators only (G0 item C2). This package read
   2212.00425 and 2312.12499 at the abstract only (method: N-body; hybrid N-body and lattice).

To core (repeat of wave 1):
8. The polarization sign of `athenak/src/pgen/tests/z4c_linear_wave.cpp` lines 107-112 is
   still unfixed on main; the oblique-wave test of G1 waits for it.
