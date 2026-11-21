# note: working note v1 of C-sidm (gates G0 and G1)

Helper package of C-sidm. The REVTeX working note of S3 (relativistic collapse of a
self-interacting dark-matter core), its figures and schematics, the numerical ledger, and a
check of the lead's stage documents against the run outputs. Version v0 (wave 2,
2026-11-15) covered the scoping gate; version v1 (wave 3, 2026-11-21) adds the G1 sections:
the collision operator in the box (waves 2 and 2b), the fluid anchor (Juttner onsets of the
King family and the thermal core), heat conduction (processors and card), the first
collisional King clusters with their limits and the first follow-up runs, the data-flow
appendix. Predictions and outcomes: `JOURNAL.md`. Guide and notation (paper-writing skill,
one level above the manuscript): `../WRITING_GUIDE.md`, `../NOTATION.md`.

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, two columns, 16 pages) and its compiled pages |
| `figures/fig_*.{pdf,png}` | eight data figures, each made by `scripts/<same name>.py` from registered run outputs: G0 `fig_knudsen`, `fig_sequences`, `fig_collisions`, `fig_box_step`; G1 `fig_box_summary` (T1/T2 rate and conservation of the release and of `coll_energy = particle`, T12 rate factor), `fig_heat` (T6(b), T7 at theta = 0.003, and (d) T7 at theta = 0.003, 0.1, 1 from all seeds against the relativistic Chapman-Enskog conductivity), `fig_onsets` (King and thermal-core binding-energy maxima, Juttner and 1 + p/u fluid onsets, particle models, CC1/CC2), `fig_cluster` (central lapse of the first collisional King runs against their controls; scouting, one seed) |
| `figures/schem_*.{png,svg}` | three schematics drawn with `paperfig.py`: architecture (exists / to be ported / new, state of 2026-11-21), data flow (initial data -> AthenaK with its problem generators and options -> histories, snapshots, collision dumps -> analysis scripts -> figures and ledger), stage timeline |
| `tables/ledger.tex` | the four ledger tables of the appendix: every number of the note with its run id (79 rows) |
| `tables/parameters.tex` | the parameter table (models at the instability criteria) |
| `tables/runinfo.tex` | the id of the registered run that made the figures and tables |
| `tables/claims.md`, `tables/claims.json`, `tables/claims_summary.tex` | 23 numbers of the lead's G0 stage documents checked against the files: 20 agree, 3 differ |
| `scripts/common.py` | the run ids the note reads; every input checked against the sha256 its run recorded (`sha256sums.txt`, or the output list of a wave-1 manifest) |
| `scripts/fig_*.py`, `scripts/schem_*.py`, `scripts/ledger.py` | one script per figure; the ledger, parameter table and claims check |
| `scripts/run_all.py` | runs all of them into one directory (`$NRPIC_RUN_DIR` of a registered run) and writes its `sha256sums.txt` |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` |

`fig_box_step.py` imports the track's readers and references from `../collide/analysis/` and
`../collide/REFERENCES/`; `fig_heat.py` imports `../heat/scripts/isobaric.py` (unchanged).

## Checklist items of G1 met by this package

| Item | Met by |
|---|---|
| C9 updated architecture | `figures/schem_architecture.png` (`scripts/schem_architecture.py`), run C-20261121-130335-d0cfe2e: release operator, box tests, `coll_energy = particle` (in release core-v0.4, CHANGELOG line 147; the track's tests ran on the core/collisions-2 executable), T12 test bed, thermal-core (b = 0.1) and King particle models, Juttner onsets, heat conduction on processors and card, growth rate over a stated interval and collapse/crossing times as existing; radial perturbation as to be ported; collisions on refined meshes, ADM energy diagnostic, threshold scan, collapsed mass fraction, million-particle and rotating models as new |
| C10 data-flow diagram | `figures/schem_dataflow.png` (`scripts/schem_dataflow.py`), same run (unchanged since C-20261120-223007-fe3f39c). It labels `coll_energy` and `metric_kind` "(branch)", which is where the track's runs were made; both options are in release core-v0.4 since |
| C14 one script per G1 data figure from registered runs | `scripts/fig_box_summary.py`, `fig_heat.py`, `fig_onsets.py`, `fig_cluster.py` (plus the four G0 scripts); every input checked against its run's sha256 (126 "sha256 ok" in `log.txt` of run C-20261121-130335-d0cfe2e); every PNG looked at |
| C16 working note with the paper-writing checker passed with --compile | `main.tex`/`main.pdf` v1: checker with `--compile` and the guide's `--forbid` list: 0 undefined references or citations, 1 overfull box of 1.1 pt (parameter table, as in G0); remaining candidates are the accepted exceptions of `../WRITING_GUIDE.md` (run ids and locators in the ledger appendix, project names in the scripts and in the data-flow figure of the appendix, the theta = 0.003 that defines Fig. 8(c) in its caption). All 16 pages read |

## Registered runs of this package

| Run | What | Outcome |
|---|---|---|
| C-20261115-170415-385069e | N1: figures, schematics, ledger, claims (first layout) | completed; predictions P1-P6 held (`JOURNAL.md`) |
| C-20261115-171741-0e0da67 | N2: the same after layout changes (ledger in two tables, frameless legends, schematic subtitle) | completed; every number identical to N1 |
| C-20261120-223007-fe3f39c | N3: G1 figure scripts, data-flow schematic, redrawn architecture, G1 ledger rows | completed; P1-P6, P8 held, P7 not tested (cut before compiling) |
| C-20261121-130335-d0cfe2e | N4: heat panel (d), architecture and timeline of 2026-11-21, ledger rows for card T7/T8, growth fit, decisive and drift analyses | completed; predictions P1-P5 held (`JOURNAL.md`); these outputs are in `figures/` and `tables/` |

Draft runs for layout went to `scratch/C-sidm/tmp/notefig/` (wave 2) and
`scratch/C-sidm/tmp/note_b3/` (wave 3); not registered, not used.

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`),
after committing the package (nrpic-run refuses a dirty package):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/C-sidm/note --cores 2 \
        --purpose "note: figures, schematics, ledger" -- .venv/bin/python tracks/C-sidm/note/scripts/run_all.py
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/C-sidm/note
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'nrpic_cf|nrpic_geodesic|tmb\.py|evstatic|make_box|an_step|nrpic-run|athinput|F21|G26|core-v0|C-pre|anta|A100'

Each figure script also runs alone (`.venv/bin/python scripts/fig_heat.py --out DIR`). About
40 s on one core. A changed or missing input stops the script with the run id and file.

## State (2026-11-21, wave 3 batch 3)

Done: note v1 (16 pages), G1 sections in the order of the argument: the fluid anchor
(Sec. IV B), the operator in the box (IV E), heat conduction with the card results (IV F),
the first collisional King clusters with the limits of `../stage/REVIEW-wave2.md` section 7
and the first follow-up runs (IV H), plan (V), data-flow appendix. Every number of these
sections has a ledger row with its run id (Tables IV, V). The trial-function onset of
arXiv:2108.11967 is labelled as such and the reference's remark on its insensitivity is cited
with its locator (`kb-data/raw/arxiv/2108.11967/v2/src/main.tex` lines 220, 274), as the G1
verifier asked (`../stage/G1/VERIFIER.md` section 2 item 4). The ledger names the KS
reference temperature of T9 (item 2) and the fit window of the number-mode bias (item 3).

Not done: the reviewer step of the paper-writing procedure for a new paper (Sec. 10 of the
skill; the note is an existing draft); a fresh-context check of the v1 ledger rows that the
G1 verifier did not recompute (card T7 at theta = 0.1, 1, T8 on the card, the growth-fit
rows, the follow-up cluster rows); figures for the follow-up cluster runs (they enter the
next version with their own script; their numbers are in Table V, the figures of the
decisive and drift analyses are in those runs' directories).

Differences between the lead's G0 documents and the files (unchanged since v0; the files
win; `tables/claims.md`):
1. `stage/G1/STATUS.md` item 2: "Table 1 ... all columns within 1.1e-4 relative except R":
   run C-sidm-20261115-120722-38ab057 has B at 2.43e-4 and eps, ec0 at 1.3e-4 (row
   `main.tex:503`, w0 = 4.5); the bound holds for E and E_rest only.
2. `stage/G0/REPORT.md` section 1: "every phase ... lasts at least 1e5 dynamical times":
   run C-sidm-20261115-121412-d463e1a gives a lower bound of 8.5e4 for the fastest phase.
3. `stage/G0/REPORT.md` section 3: thermal-core models Z(0) = 0.40-0.80 have "R/M = 20-26,
   r_core/M = 1.5-2.1": run C-sidm-20261115-121748-4e8d6b5 gives 19.8-28.1 and 1.27-2.56
   (the quoted ranges fit narrower ranges of Z(0)); the lapse range agrees.
4. Not counted as a difference: `STATUS.md` "three independent solvers agree to 3e-8": the
   King comparison is 3.5e-8 (run C-sidm-20261115-131130-3077a99, X3).
5. Locator: `stage/G0/REPORT.md` section 6 puts the 200 M_sun black hole of arXiv:2601.17117
   at `SIDM_MS.tex:476`; the statement is at line 481 (476 holds the strong-gravity
   discussion), and the 3e-8 fraction at line 68.

## Requests

- To the lead of C-sidm (CHECKLIST of G1): C16 can be set to met with this evidence: note v1
  `main.tex`/`main.pdf` (16 pages, every page read), checker with `--compile` passed (0
  undefined references and citations, 1 overfull box of 1.1 pt; remaining candidates are the
  guide's exceptions), figures and tables from registered run C-20261121-130335-d0cfe2e
  (126 inputs, every sha256 ok; G0 outputs byte-identical to the earlier runs). C9: the two
  boxes named in the checklist are updated in the same run ("heat conduction T6-T8,
  processors and card"; "growth rate over a stated fitting interval", now green), and "pair
  energy at each particle's metric" is green because the option is in release core-v0.4.
  C14: `fig_heat` gained panel (d) with the card T7 results; card T7/T8, the growth-fit
  validation and the first decisive and drift numbers are in the ledger (Tables IV, V).
- To the lead of C-sidm: Sec. IV H now says that the first follow-up runs show
  the M/4 drift of the CC2 control to be mostly numerical and a King model at y0 = 0.26 to
  collapse at Kn_c = 1; check that wording against your reading in `../stage/REVIEW-wave3.md`
  sections 2-3 (the note keeps the collisional threshold and the collapsed mass open).
- To the lead of C-sidm (from v0, still open where not done): the three G0 numbers listed
  above in `stage/G1/STATUS.md` item 2 and `stage/G0/REPORT.md` sections 1, 3 and the locator
  of section 6.
- To orch (from v0): `nrpic-stage verify` and the wave-1 gravothermal manifests (paths
  relative to the main checkout, schema fields); details `../stage/G0/VERIFY_RESULTS.md`.
- To kb: none new.
