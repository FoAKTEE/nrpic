# JOURNAL of package repro/note (Track E): the working note on the reproduction of both papers

Predictions before each test, outcomes after, failed predictions kept. Times PST.

## Entry 1 (2026-11-24 09:45): state, plan, predictions

State found. The task text said an earlier session of this package had been stopped by the
pause flag after committing; no such work exists: `git log --all -- tracks/E-stoch-inf/repro/note`
is empty and no directory existed. The package starts here. Merged main (already up to date).

Inputs read: decisions 0010, 0028, 0029, 0031, 0032; `repro/scope/REPRO_MAP.md`,
`SETUP_AUDIT.md`; `repro/langevin/README.md`; `repro/equations/EQUATIONS.md`, `ERRATA.md`;
`repro/figs/RESULTS.md` (state 09:37, figure run E-20261124-173254-420115f); core's info
`tracks/core/outbox/20261124T143303Z__to-E-stoch-inf__noise-level2-review-runs-stand.md` (the
Fable review of branch core/noise-level2: results unchanged; level 1 against level 0 on the mesh
is a scheme difference, level 2 against level 0 is the level-2 effect to one per cent). The
skill: `/home/haiyangw/.claude/skills/paper-writing/SKILL.md` (loaded with the Skill tool).

Plan. (1) WRITING_GUIDE.md and NOTATION.md one level above the manuscript; (2) the story,
300- and 1000-word versions (`notes/2026-11-24-story.md`); reviewers: this session has no
subagent tool, so the step-4 reviewers are not dispatched (said in README and the note's
record), and one self-review in their role replaces them; (3) manuscript scripts: copies of
`repro/figs/figures/*.py` and `repro/langevin/{lsde,analyse}.py` with titles and legends that
name no run labels; a schematic of the two reproductions with `paperfig.py`; `ledger.py`
that reads every number from the outputs of this package's run and from the registered runs
of the other packages (checked by sha256 against their `sha256sums.txt`), and the papers'
printed values by file and line; `run_all.py` that runs all of it as one registered run;
(4) main.tex; (5) checker, compile, read every page; (6) README, commit.

No card time. Continued runs (repro/continue: RSF256 E-20261124-130529-da8c917, RNC256
E-20261124-130629-61fe0b0, CL256U E-20261124-130711-a5dec67, CL256S E-20261124-130952-4be980b,
AL2S E-20261124-131359-49afe29) are queued behind another user's job; every row they complete
is marked PENDING with that id. Not waited for.

Predictions for the registered run_all (R1):
- P1. The lattice figure jsons equal those of figure run E-20261124-173254-420115f byte for
  byte (the manuscript copies change only titles and legend strings and one path). Refuted if
  any json differs.
- P2. The Langevin numbers (`langevin.json`) equal `repro/langevin/results/langevin.json`
  of analysis E-20261123-021843-813759b except the key `simdir` (same path, so also equal):
  the bootstrap uses a fixed PCG64 seed. Refuted if any number differs.
- P3. Every ledger value that `repro/figs/RESULTS.md`, `repro/langevin/README.md` or
  `repro/equations/EQUATIONS.md` prints agrees with the recomputed value to the digits
  printed there. Refuted if one does not (the ledger script stops and names it).
- P4. Wall time below five minutes on two cores (the figure run took 36 s, the Langevin
  analysis about 2 min).

## Entry 2 (2026-11-24 09:52): outcome of R1 (run_all E-20261124-174752-f387f2a)

Registered run E-20261124-174752-f387f2a (production, two cores, 113 s; commit f387f2a).
- P1 held: all twelve lattice jsons equal those of figure run E-20261124-173254-420115f byte for
  byte (`checks.json`).
- P2 held: `langevin.json` equals the committed one of analysis E-20261123-021843-813759b (key
  `simdir` aside).
- P3 held in the form the script tests it: every quoted line stands where the ledger says
  (the script would have stopped), and the recomputed numbers are those of P1 and P2, so the
  values printed in RESULTS.md and the Langevin README are the ledger's to their digits.
- P4 held: 113 s.
Figures looked at (Read of each PNG in the run directory): pipeline schematic, background,
SR and USR spectra, SR and USR contrasts (the SR constraint panels are empty: the dumps of that
run carry no per-cell constraints; they wait for the continued run E-20261124-130529-da8c917),
K spectra (SR, USR; the legend of the USR panel overlaps two curves near the bottom left, kept),
spectral convergence (32-128 only; 256 pending), constraint convergence, sign flip, ablation and
its SR panel at N = 7.19, one-patch background (legend over the converged curve, kept), scheme
comparison, paths, PDFs. Not used in the manuscript: the step-and-seed figure and the log PDFs
(their statements are cited from the one-patch package with locators).
Copied `figures/` (one format per figure) and `tables/` into the manuscript; sha256 of every
copied file checked against the run's `sha256sums.txt` (all OK).
