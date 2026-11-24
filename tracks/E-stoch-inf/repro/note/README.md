# repro/note: working note on the reproduction of arXiv:2401.08530 and arXiv:2512.14649

Package of Track E (decision 0028, batch R2b). The working note on the reproduction of both
papers, written with the paper-writing skill: `manuscript/main.pdf` (19 pages, REVTeX, PRD
style). Predictions and outcomes: `JOURNAL.md`. State: 2026-11-24 10:05 PST.

## What is in this directory

| Path | Content |
|---|---|
| `WRITING_GUIDE.md`, `NOTATION.md` | the per-paper layer of the skill (one level above the manuscript): journal, readers, outline, allowed numbers, expert dictionary, project names, the exceptions of the program (ledger with run ids; which code each run used) |
| `notes/2026-11-24-story.md` | skill 10.1: the story, the 300-word and the 1000-word versions, and the self-review that replaced the parallel reviewers |
| `manuscript/main.tex`, `references.bib`, `main.pdf` | the note: I introduction; II stochastic sources (computer-algebra checks); III lattice reproduction of 2512.14649 (set-up and five differences, methods, background, spectra, one-point statistics and the amplitude factor, shear, convergence and constraints, sign flip, momentum constraint at the cut, backreaction with core's review); IV one-patch reproduction of 2401.08530 (Langevin pair, background step and the plateau stop, Ito against Stratonovich reading, Ito term alpha^5, USR amplitude sigma^2/3, other statements); V discussion; VI summary; appendices A misprints (17), B parameters, C set-up item by item, D verdicts per figure and statement with the independent check, E ledger (109 rows) |
| `manuscript/figures/` | 19 figures, all from registered run E-20261124-180038-4d4651a (sha256 checked against its `sha256sums.txt`); one schematic (`fig_pipeline.png`, harness/style/paperfig.py) |
| `manuscript/tables/ledger.tex`, `ledger.csv` | the ledger, built by `scripts/ledger.py` in the same run |
| `manuscript/scripts/` | copies of `repro/figs/figures/*.py` and `repro/langevin/{lsde,analyse}.py` (titles and legends without run labels; `figlib.py` path one level deeper; `fig_ablation.py` marks only the cut SR level-2 run pending), `schem_pipeline.py`, `ledger.py`, `run_all.py`, `figstyle.py` (= python/nrpic/figstyle.py), `paperfig.py` (= harness/style/paperfig.py) |

## Registered runs of this package

| Run | What |
|---|---|
| E-20261124-174752-f387f2a | run_all 1 (113 s, two cores): every lattice json byte-equal to figure run E-20261124-173254-420115f, langevin.json equal to analysis E-20261123-021843-813759b (`checks.json`); superseded by run 2 for the copied files |
| **E-20261124-180038-4d4651a** | run_all 2: same jsons (byte-equal again); ablation legend fix; ledger with every PENDING row naming its continuation; the committed `figures/` and `tables/` come from it |

## How to rerun and rebuild

From the worktree root, with the package committed:

```text
harness/bin/nrpic-run submit --kind production --gate G2 --preregistered "tracks/E-stoch-inf/repro/note/JOURNAL.md#entry-<k>" \
  --purpose "..." --package tracks/E-stoch-inf/repro/note --cores 2 -- \
  bash -c 'OMP_NUM_THREADS=2 python3 tracks/E-stoch-inf/repro/note/manuscript/scripts/run_all.py "$NRPIC_RUN_DIR"'
R=/data/haiyangw/nrpic/scratch/E-stoch-inf/<run id>
cp $R/figures/fig_*.pdf $R/figures/fig_pipeline.png tracks/E-stoch-inf/repro/note/manuscript/figures/   # only the names already in figures/
cp $R/tables/* tracks/E-stoch-inf/repro/note/manuscript/tables/
cd tracks/E-stoch-inf/repro/note/manuscript
python3 /home/haiyangw/.claude/skills/paper-writing/scripts/check_manuscript.py --main main.tex --compile
```

`--compile` runs `latexmk -pdf` and rebuilds `main.pdf`. The run reads the dump passes and
records named in `run_all.py` (`LATTICE_ARGS`), the Langevin simulation E-20261123-021043-d00a314
and the equation checks E-20261123-022009-a53e7ee (checksum-checked); `ledger.py` stops if a quoted
line of RESULTS.md, the Langevin README, a4res/README.md or core's review message (branch
core/noise-level2) has moved.

When the continuations of repro/continue have ended: run the passes of repro/figs (RESULTS.md
section 5: `runs.py rsf256`, `cl256`, `al2s`), add their run directories to `LATTICE_ARGS` in
`run_all.py` (`--rsf256`, `--cl256s`, `--al2s`), add ledger rows for the new numbers in
`ledger.py` (the PENDING rows name what each completes), rerun, and replace the five
`\pending{...}` markers of `main.tex`.

## Checker (skill Sec. 8), last run on the committed text

Clean: 3.4, 3.5, 4.1, 4.3 (both), 1.3, 5.3, 5.6, 5.7, 2.5, 7.5 hardware and file names, Sec. 6
(both), 9.1; compile: no undefined references or citations, no overfull boxes. Remaining hits,
accepted: 5.1 (two: the verdict label "not reproduced"); 7.5 commit-hash pattern and 7.7 project
names (run ids and paths in the ledger appendix and in `scripts/`, guide exception 1); 7.6 (one:
"no defect" about the reviewed code, guide exception 2); 9.3 (legend calls in the scripts:
`figstyle.py` sets `legend.frameon = False` for every legend). Every page of the PDF was read
(75 dpi renders; JOURNAL entries 3 and 4).

## What is not done

- PENDING in the note, each with the continuation that completes it (ledger rows): 256^3 rungs of
  the convergence figures (E-20261124-130952-4be980b, E-20261124-130711-a5dec67), the SR level-2
  curve at the end of the run (E-20261124-131359-49afe29), the SR constraint rows of the
  one-point figure (E-20261124-130529-da8c917), the SR sign flip beyond the first e-fold
  (E-20261124-130629-61fe0b0). Not waited for (cards held by another user's job).
- The "Check" column of the verdict table: only the backreaction rows carry an independent check
  (core's review of branch core/noise-level2 on Fable, "runs stand"). The fresh verifier of this
  batch (package repro/verify) had produced nothing when the note was written; the correction
  pass fills the column.
- Skill 10.1 step 4: no parallel reviewer subagents (this session has no tool to start them);
  one self-review in their role (story notes).

## Requests

- repro/verify (fresh verifier): check from the artefacts (a) the plateau stop and the
  Euler-0.01 background, (b) that the one-patch figures follow the Ito reading at step 0.01,
  (c) the alpha^5 Ito term, (d) the USR amplitude factor sigma^2/3, (e) the amplitude factor of
  the one-point bands (a judgement from reading the published figures), (f) the level-1 reading
  of the ablation figure; their verdicts go into the "Check" column of Table IV.
- Lead of E: when the continuations end, the update described under "How to rerun"; SETUP_AUDIT
  item 4 still says N* + 8.04 for SR, the note uses 8.10 (request of repro/figs).
- core (minor, python/nrpic/figstyle.py): save PDFs without a creation date (or honour
  SOURCE_DATE_EPOCH), so a rerun of the figure scripts gives byte-identical PDFs; every rerun now
  changes all committed PDFs by their metadata only.
