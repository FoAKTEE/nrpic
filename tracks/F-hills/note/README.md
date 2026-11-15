# note: working note v0 of F-hills (gate G0)

Helper package of F-hills, wave 2 (2026-11-15). The REVTeX working note of S12 (the Hills
mechanism near a black hole), its figures and schematics, the numerical ledger, and a check
of the lead's stage documents against the run outputs. Predictions and outcomes:
`JOURNAL.md` (N1-N4). Guide and notation of the note (paper-writing skill, one level above
the manuscript): `../WRITING_GUIDE.md`, `../NOTATION.md`. The package also wrote
`../stage/G0/STAGE_REPORT.md` (from `nrpic-stage report`) and `../stage/G0/CHECKLIST.md`
(from `nrpic-stage collect`, items filled where this package has the evidence).

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, two columns, 11 pages) and its compiled pages |
| `figures/fig_*.{pdf,png}` | five data figures (restricted Newtonian scan, geodesic scan of arXiv:2404.16270, pericentre scan of both references at q = 4 and 10, the first passages in both references, MeshBlocks and card time), each made by `scripts/<same name>.py` from registered run outputs; `fig_*_numbers.json` holds the numbers each figure shows |
| `figures/schem_*.{png,svg}` | the two schematics of the stage check (architecture with exists / to be ported / new; stage timeline), `paperfig.py` |
| `tables/ledger.tex` | the two ledger tables of the appendix: every number of the note with its run id or paper locator |
| `tables/parameters.tex` | the parameter table of the two first passages (read from the inputs that run N1 recorded) |
| `tables/claims.md`, `tables/claims.json` | 17 numbers and statements of the lead's documents checked against the files: 13 agree, 2 differ, 2 superseded (below) |
| `scripts/common.py` | the run ids the note reads; every input checked against the sha256 its run recorded (`sha256sums.txt`, or the output list of a wave-1 manifest) |
| `scripts/passage_curves.py` | analysis run N1: time series of full Newton, hole-fixed Newton and the geodesic reference from the two passage inputs (uses `stage/G0/checks/lead_checks.py`, `nr_first/scripts/nrread.py` and `geodesic_binary/hrna.py`, read only; needs numba) |
| `scripts/fig_*.py`, `scripts/schem_*.py`, `scripts/ledger.py` | one script per figure; the ledger, parameter table and claims check |
| `scripts/run_all.py` | runs the figure, schematic and ledger scripts into one directory (`$NRPIC_RUN_DIR` of a registered run) |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` (sha256 equal to `harness/style/SHA256SUMS`) |

## How to rerun

From the worktree root `/data/haiyangw/nrpic/wt/F-hills`, with the worktree environment
(`harness/bin/nrpic-env create --no-kokkos`; the analysis run N1 needs numba, which is in
`scratch/F-hills/venv-gb`):

    # N1 (only if the passage inputs or the reference code change), about 70 s:
    harness/bin/nrpic-run submit --kind scouting --gate G0 --package tracks/F-hills/note --cores 1 \
        --purpose "note N1: ..." -- /data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python \
        tracks/F-hills/note/scripts/passage_curves.py
    # put the new run id into scripts/common.py (key "n1"), commit, then figures and tables, about 20 s:
    harness/bin/nrpic-run submit --kind scouting --gate G0 --package tracks/F-hills/note --cores 1 \
        --purpose "note: figures, schematics, ledger" -- .venv/bin/python tracks/F-hills/note/scripts/run_all.py
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, put the
    # run id into the ledger paragraph of main.tex (appendix B), then
    cd tracks/F-hills/note && latexmk -pdf main.tex
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'HRNA|newton3|geodesic_binary|three_punctures|nr_first|hrna\.py|nrpic_cf|puncture_setup|athinput|nrpic-run|core-v0|F-pre|lead_checks|anta|A100'

Each figure script also runs alone (`.venv/bin/python scripts/fig_rp_scan.py`, output to
`figures/`), which is what `harness/bin/nrpic-stage verify` does.

## Registered runs of this package

| Run | What | Outcome |
|---|---|---|
| F-20261115-174648-25514db | N1: time series of the two references for the passages at q = 4 and 10 | completed; every number equal to E6, V5, V5b, V6 (prediction met) |
| F-20261115-175639-ce844e5 | N2: figures, schematics, ledger, claims (first layout) | completed; numbers equal to the source analyses; claims: one difference I had not predicted (V4b, below) |
| F-20261115-180428-fc8172f | N3: the same after the text pass (four ledger rows added, table widths) | completed; PNGs byte-identical to N2 (prediction met) |
| F-20261115-180609-abc9f6e | N4: the same after one ledger format change | completed; PNGs and claims identical to N3; these outputs are in `figures/` and `tables/` and named in appendix B |

Draft figures went to `scratch/F-hills/tmp/note/` for layout only (not registered); each
committed PNG is byte-identical to the draft that was opened and read.

## State (2026-11-15)

Done: note v0 (11 pages, latexmk, every page read; checker clean in the main text: remaining
hits are run ids in the ledger appendix and data keys in the scripts, accepted by exception 1
of the guide); five data figures and two schematics, each PNG opened; ledger and parameter
table from registered runs; claims check; `stage/G0/CHECKLIST.md` and
`stage/G0/STAGE_REPORT.md` from the harness.

Not done: the reviewer step of the paper-writing procedure for a new paper (300- and
1000-word versions read by first-year-student reviewers, Sec. 10 of the skill; no subagent
tool in this session); a fresh-context verifier of the note's own ledger; the wave-2 runs
still running or queued when the note was written (t = 0 constraint residual E2, the
single-puncture card runs E3, newton3's corrected finite-q energies Q1-Q5, the second check
of G0) are named in the plan section but their results are not in the note.

Differences between the lead's documents and the files (the files win; `tables/claims.md`):
1. `stage/G1/STATUS.md` T1, `EVIDENCE.md` V4b and `STATUS.md`: "independent code agrees at
   nine (sense, D) points within 0.002 in P_dis and 0.4 percent in energy (V4b) ... all nine
   agree". V4b (run F-hills-20261115-145544-a314517) reran only retrograde D = 0.3 and 0.38
   (|dP| <= 0.0013, |dE|/E <= 0.0035). Retrograde D = 0.1 and 0.2 come from V4 (run
   F-hills-20261115-145246-090f5dc): |dP| = 0.0023 and 0.0063, |dE|/E = 0.0038 and 0.0116,
   with 8 and 14 wide bound samples that were not followed on. Probably the same
   classification effect as at D = 0.3 and 0.38, but not shown.
2. `stage/G0/SCOPING.md` section 9: "q = 4, m/16: 2416 / 2654 / 2348 MeshBlocks, 41
   card-hours" belongs to puncture radius 1.2; the inputs use 1.8, which gives 2514 / 2864 /
   2568 and 44.8 card-hours (run F-hills-20261115-131933-907e5fe; nr_first E1 measured 2514
   at the start with the release executable). 2864 is above the inputs' `max_nmb_per_rank =
   2700` and close to the card's about 3000 slots: an m/16 run at q = 4 needs that limit
   raised.
3. Superseded by later records: the allotment (STATUS: 40 card-hours, decision 0006; now 50,
   decision 0014) and the release state (HANDOFF, OPEN item 6: multi-puncture not released;
   now in core-v0.3).
4. Wording: the STATUS headline says the geodesic model "captures" a member in 69-96 percent
   of phases at r_p = 7-12 M; the files count a plunge (a member crosses r = 2.5 M inward);
   "Newton in none" holds for plunges, but at r_p = 7 M full Newton brings a member inside
   4 M in 62 percent of the phases.

## Requests

- To the lead of F-hills: (1) correct the V4b sentence in `stage/G1/STATUS.md` T1,
  `stage/G0/EVIDENCE.md` and `STATUS.md` (or rerun V4b for retrograde D = 0.1 and 0.2 with
  the wide bound samples followed on), and the q = 4 m/16 row of `stage/G0/SCOPING.md`
  section 9; (2) raise `max_nmb_per_rank` in any m/16 variant of the q = 4 input; (3) write
  the "Decision requested" paragraph of `stage/G0/STAGE_REPORT.md` (a draft is there) and
  close the OPEN items of `stage/G0/CHECKLIST.md` that need the lead (verifier report,
  STATUS/HANDOFF current); (4) when E2, E3 and the corrected newton3 energies finish, add a
  figure script per result under `note/scripts/` and extend Secs. IV and V of the note.
- To orch: none new from this package; `nrpic-run submit` worked for all four runs of this
  package (it commits the manifest itself, which is a second writer of the index next to
  the helpers).
