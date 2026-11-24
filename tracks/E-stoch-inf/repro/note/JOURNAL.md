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

## Entry 3 (2026-11-24 10:01): draft compiled, pages read; prediction for R2

main.tex written from the 1000-word story (notes/2026-11-24-story.md), checker run, compiled (19
pages, no undefined references, no overfull boxes after splitting two equations), every page
read at 75 dpi. Found on the pages: the SR panel of the ablation (Fig. 11) labelled the USR
curves "(pending)" although they are only absent from that comparison; the ledger used "MS",
which the guide's dictionary replaces. Fixed in the scripts (`fig_ablation.py`: only the cut SR
level-2 run is marked pending; `ledger.py`: wording, and PENDING rows naming the continuation
of every pending item: E-20261124-130529-da8c917, -130629-61fe0b0, -130711-a5dec67,
-130952-4be980b, -131359-49afe29).
Reviewers of skill step 10.1(4): this session has no tool that starts subagents, so none were
dispatched; one self-review in the role of a first-year graduate student is in the story notes.

Prediction for R2 (run_all at commit 679f9a0): every lattice json and langevin.json equal to R1
byte for byte (the change is a legend label and ledger wording); the ledger gains two rows (109
in 8 tables); only `fig_ablation_sr` changes among the figures. Refuted if any json differs.

## Entry 4 (2026-11-24 10:08): outcome of R2, final state

R2 = E-20261124-180038-4d4651a (registered, production, two cores). Prediction of entry 3 held:
every lattice json and langevin.json byte-equal (`checks.json`), ledger 109 rows in 8 tables.
Figures and tables copied from R2 (sha256 of each copied file found in the run's
`sha256sums.txt`). The PDFs differ from R1 only in their metadata (first differing byte near the
end of each file), so every committed PDF changed; request to core in README (deterministic
PDF metadata). Recompiled: 19 pages, no undefined references, no overfull boxes; checker as
listed in README (remaining hits accepted under the guide's exceptions). Pages 9 (ablation
legend now marks only the SR level-2 curve pending) and 16 (ledger with the two new PENDING
rows) read again; the other pages are unchanged in content from entry 3.
Voice pass (skill 10.2) done by reading the text for throat-clearing, participial tails, noun
stacks, flat cadence and contrastive negation; the checker's 5.3, 5.6, 5.7 and 1.3 are clean,
the two 5.1 hits are the verdict label "not reproduced".
Not done: parallel reviewer subagents (no tool in this session); the "Check" column waits for
repro/verify; five rows PENDING on the continuations of repro/continue.

## Entry 5 (2026-11-24 10:55): correction pass after the verifier; plan and predictions

Input: `repro/verify/VERIFIER.md` (commit 0de2198a, sections 1-7). No continuation of
repro/continue has run (all five still PENDING in the queue at 10:50, squeue); the ablation figure
stays as it is (no level-2 SR run at N_f exists), so its PENDING row stays.

Corrections the verifier calls for, and what I do with each:
- C1 (sec. 4, "ledger defects"): rows 32, 77, 78 carry cut text. Fix in `ledger.py`: a quote row
  may carry a display value; the needle still has to stand on its line. Values: SR factor
  "about 3.5" (RESULTS.md:68, the line that starts with "3.5:"), "16", "1 per cent".
- C2 (weakest point 2, sec. 7): the definitions behind about fifteen rows are only in the
  scripts. State them in the ledger quantities and in Sec. III B: shells with more than 10 modes;
  "linear" = the realisation's linear power from the code's lockstep mode functions with the same
  random amplitudes; 68 per cent band = central (16th to 84th percentile); entry window
  0.05 < N <= ln 8; sign-flip window 0.5 <= N <= ln 64; N95 on the dump cadence; a one-patch path
  is lost once |alpha| >= 50 or non-finite.
- C3: a "Check" column in every ledger table, filled from VERIFIER.md by line (ledger.py checks
  that the verifier's string stands on that line, as for quotes): yes / differs (with the
  verifier's value) / out of reach / quote / rerun only / pending.
- C4 (sec. 2 row "Sign-flip control"): the absolute flipped H/[H] is about 1e-7, a hundred times
  below P1:541's "~1e-5". New ledger rows from the existing json keys `H_flip_max`; text and
  verdict: first-order rise reproduced, level not.
- C5 (sec. 1, last row; ledger 109): the SR amplitude ratio depends on eps1 at the crossing (ours
  1.027 at eps1 = 0.0052, verifier 1.063 at 0.0124 and 1.123 at 0.0244). New ledger row: our eps1
  at the crossing (noise_amp.json SR.rows.2.eps1); text no longer says "holds closely".
- C6 (weakest point 3; rows 94, 101, 83): third moments differ between two implementations of
  the same equations (Ito skewness 1.04 against 1.116 +- 0.012; alpha^3 -> 1: -0.96 against
  -0.74) and the half-loss time (4.80 against 5.37). Text: widths to 1-2 per cent, skewness to
  about ten per cent; the published figure (about 1.1) lies nearer the verifier's value.
- C7 (sec. 2 "Convergence"; rows 61-63): with the verifier's linear reference the rungs fall by
  43 and 34 per doubling, ours by 52 and 62: text says "between fifth and sixth order", not
  "at the sixth order".
- C8 (rows 68, 70): maxima depend on the shell selection; with every |n|^2 shell the verifier
  finds 9.2e-4 (USR) and 1.4e-4 (SR at N = 7.19). Under P1:520 (\textpertenthousand of textcomp =
  per ten thousand, 1e-4) the SR comparison is then at the bound, not below it. Text softened.
  [The verifier wrote "P1:520's 1 per mille"; the printed sign is per ten thousand: checked in the
  source line 520 and its `\usepackage{textcomp}` (line 43). The note's reading stands.]
- C9 (sec. 1, row 35; sec. 6 point 1): the published "~10" outliers against the published Fig. 4
  full band (about 18): one clause in Sec. III E.
- C10: say in the note which claims the second agent confirmed: abstract, introduction, Sec.
  III B (paragraph on the check), the "Check" column of Table IV (verdicts) and of the ledger,
  the errata caption (items 1, 3, 6, 7, 8, 10, 14, 15 rederived independently).

Predictions for R3 (run_all after these edits; no figure script changes):
- P1. Every lattice json and langevin.json byte-equal to R2 (E-20261124-180038-4d4651a), as in
  R1 and R2. Refuted if any differs (`checks.json`).
- P2. Every PNG under `figures/` byte-equal to R2's (the PNGs of R1 and R2 were byte-equal
  except the one changed figure). Then the committed PDFs (from R2) stay and only `tables/` is
  copied. Refuted if a PNG differs.
- P3. Ledger: 112 rows in 8 tables (109 + two flipped-H levels + SR eps1 at the crossing); every
  check needle found on its VERIFIER.md line (else the script stops). Refuted by another count
  or a stop.
- P4. Compile: no undefined references, no overfull boxes; the ledger tables with a fourth
  column may move pages (expect 19-21 pages).
