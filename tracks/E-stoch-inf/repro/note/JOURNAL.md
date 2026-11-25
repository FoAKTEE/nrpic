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

## Entry 5 (2026-11-24 10:51): correction pass after the verifier; plan and predictions

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
- P3 amended before the run (10:53): 113 rows, not 112: one more row, the e-fold at which the SR
  flipped run ends (json key `RNC256.N_end_flip`; the verifier reads common records only to
  N = 0.39, VERIFIER.md:54, while our window holds a record at N >= 0.5), so the sign-flip window is
  stated with its end. A dry run of the new `ledger.py` on the outputs of R2 (unregistered, a test
  of the script in scratch/E-stoch-inf/tmp/ledgertest) gives 113 rows; checks: 65 yes, 16
  differs, 2 beyond reach, 11 quote, 14 rerun only, 5 none (4 pending, 1 new row).

## Entry 6 (2026-11-24 10:58): outcome of R3; a page overflow found on the pages; prediction for R4

R3 = E-20261124-185556-df39d1c (registered, production, two cores, 65 s, commit df39d1c).
- P1 held: twelve lattice jsons and langevin.json byte-equal to R2 (`checks.json`).
- P2 held: all 19 PNGs under `figures/` byte-equal to R2's; the committed PDFs (from R2) stay.
- P3 held as amended: 113 rows in 8 tables; checks 65 yes, 16 differs, 2 beyond reach, 11 quote,
  14 rerun only, 5 none; every verifier string found on its line.
- P4 held in part: compile clean (no undefined references or citations, no overfull hbox), 21
  pages. Checker (forbid list of the guide): only the accepted hits (5.1 verdict labels, 7.6 "no
  defect", 7.5/7.7 in the ledger tables and scripts, 9.3 in scripts); I removed two new 5.1 hits
  ("rather than") and four 4.3 hits (long decimals) from the new text.
- Found on reading every page (75 dpi): two ledger tables run off the bottom of their page, which
  neither the compile log nor the checker reports (a float taller than the page, no overfull hbox):
  constraints (page 18: the last two rows and the rule missing) and one patch (page 21: the last
  two rows missing). The fourth column made the rows taller. Fix: two more sections in
  `ledger.py` (sign flip; noise terms of the one-patch system); the main text's range reference
  now ends at the new last table.
Prediction for R4 (run_all at the commit of this fix): jsons and PNGs byte-equal to R3 as before;
ledger 113 rows in 10 tables with the same check counts; after the compile every ledger table
ends with its bottom rule on the page (read pages 15 to the end). Refuted if a json, PNG or count
differs or a table is still cut.

## Entry 7 (2026-11-24 11:00): outcome of R4; prediction for R5

R4 = E-20261124-185912-45510c2 (registered, production, two cores). Prediction of entry 6 held:
jsons and langevin.json byte-equal (`checks.json`), all 19 PNGs byte-equal to R3, 113 rows in 10
tables with the same check counts; compiled to 23 pages, and every ledger table now ends with its
bottom rule on its page (pages 18, 19, 22, 23 read). One new checker hit: the section name "noise
terms" is a term of the guide's dictionary (Sec. 6, prefer "stochastic sources"). Renamed the
section "One-patch drift and noise amplitude".
Prediction for R5 (run_all at the commit of the rename): identical to R4 except the caption and
label of the last ledger table; checker without the Sec. 6 hit; 23 pages. Refuted otherwise.

## Entry 8 (2026-11-24 11:05): outcome of R5; final state of the correction pass

R5 = E-20261124-190054-08f916a (registered, production, two cores). Prediction of entry 7 held:
jsons and langevin.json byte-equal, 19 PNGs byte-equal to R4, the ledger differs from R4 only in
the caption and label of its last table (diff with run ids masked); checker without the Sec. 6
hit; 23 pages, no undefined references, no overfull boxes. Tables copied from R5 (sha256 found
in its `sha256sums.txt`); figure PDFs stay from R2 (PNGs byte-equal R2 to R5).
Pages: 1-11 of the final build are pixel-identical to the R3 build that I read in full; 12-23
read on the final build. Every ledger table ends with its bottom rule on its page.
Corrections C1-C10 of entry 5 are applied: C1 rows 32, 77, 78 carry "about 3.5", "16",
"1 per cent"; C2 definitions in Sec. III B and in each ledger caption; C3 check column (65 yes,
16 differs, 2 beyond reach, 11 quote, 14 rerun only, 5 none); C4 flipped level 9.9e-8 (SR),
1.3e-7 (USR) against the printed 1e-5, in text and verdicts; C5 SR amplitude with eps1 = 5.2e-3
at the crossing; C6 widths 1-2 per cent, skewness about 10 per cent, loss criterion stated; C7
convergence "close to sixth order", factors 52 and 62 against 43 and 34; C8 SR backreaction "at
the bound"; C9 II's Fig. 4 reaches about 18 against its text's ten; C10 abstract, introduction,
Sec. III B, discussion, errata caption, Table IV check column.
One disagreement with the verifier kept and sent back as a request (README): P1:520's
`\textpertenthousand` is per ten thousand, not per mille as VERIFIER.md section 2 reads it.
Not done: no continued run has ended (all five PENDING in the queue at 11:02); the ablation
figure is unchanged.

## Entry 9 (2026-11-24 13:47 PST): update pass after the continued runs; plan and predictions

Input: repro/figs at bd9356bc (RESULTS.md and `fig/` from figure run E-20261124-213739-9776185,
which adds `--cl256s` and `--al2s` from pass E-20261124-213029-e937f69 to the arguments of the
earlier figure runs). Four of the five continued runs have ended (CL256S, CL256U, AL2S, RNC256);
RSF256 waits as queue entry q0034 (state "waiting" at 13:43 PST, `nrpic-queue show q0034`), not
waited for.

Plan: (1) bring the script copies up to date with repro/figs/figures (runs.py and joins.py as
they are; make_figs.py, fig_signflip.py, fig_conv.py with the new functions and the note's neutral
titles kept; fig_ablation.py and figlib.py unchanged, their differences are titles, the
"(pending)" rule and the path depth); (2) `run_all.py`: add `--cl256s` and `--al2s`; (3)
`ledger.py`: PENDING rows of the 256^3 rungs, of the SR sign flip and of SR level 2 at N_f become
value rows (check "none": the verifier saw none of these records); the withdrawn "orders of the
entry maximum 32 -> 64" (repro/figs JOURNAL entry 11, RESULTS Fig. 8 "Correction") are replaced by
the time-matched plateau ratios; the quotes of RESULTS.md move to their new lines; the SR per-cell
constraint row stays PENDING with RSF256 and q0034 named; (4) text, captions, Table IV, README.

Predictions for R6 (registered run_all after the commit of these edits):
- P1. Every json of repro/figs/fig (13, joins.json included) byte-equal to this run's
  `lattice/` (the note's scripts differ from repro/figs only in titles and labels, which no json
  carries); langevin.json equal. Refuted by any `false` in `checks.json`.
- P2. PNGs: fig_specconv, fig_constraints, fig_ablation, fig_signflip differ from R5's (new
  256^3 curves, SR level 2 at N_f, SR flipped run to N = 4.39, legend positions); the other 15
  byte-equal to R5's (fig_ablation_sr included: its json changes only in a record count, which the
  figure does not plot). Refuted if one of the 15 differs or one of the four does not.
- P3. Ledger: 121 rows in 10 tables (113; minus 2 withdrawn orders, minus 3 PENDING rows; plus
  256^3 maximum, its order 128 -> 256, two per-mode rms, four plateau-ratio rows, the USR
  background order 128 -> 256, SR median sign-flip ratio, three SR level-2 rows at N_f: 13 new);
  checks 61 yes, 15 differs, 2 beyond reach, 11 quote, 14 rerun only, 18 none (two yes rows
  withdrawn; two yes rows and one differs row whose values now come from the longer SR flipped
  record set to none; 13 new rows; one PENDING; one row added after the check). Refuted by
  another count or a stop of the script.
- P4. Compile without undefined references or overfull boxes; 23 or 24 pages; every ledger table
  ends on its page. Refuted otherwise (read the pages).

## Entry 10 (2026-11-24 13:56 PST; heading first written with 14:20, a wrong time): outcome of R6; three ledger tables off their pages; prediction for R7

R6 = E-20261124-215017-cb16c27 (registered, production, two cores, commit cb16c27).
- P1 held: all 13 jsons of repro/figs/fig byte-equal to R6's `lattice/` (joins.json included);
  langevin.json equal (`checks.json`).
- P2 held: fig_specconv, fig_constraints, fig_ablation, fig_signflip differ from R5; the other 15
  PNGs byte-equal (fig_ablation_sr included). Looked at all four: Fig. 7 has the 256^3 curve on
  the 128^3 curve at the longest shells and below it at the shortest; Fig. 8 has four lattices,
  the plateaus of 64-256 on each other during the entry, and late in the runs the finer lattices
  end higher in SR M and in both USR curves with the box mean kept (Paper II source line 750
  says the same of its runs; the text now says so); the sign-flip figure has the SR flipped run
  to N = 4.39 with the smallest gap at N = 4.1-4.4; Fig. 10 has the SR level-2 curve at N_f.
  Copied the four PDFs (sha256 in R6's sha256sums.txt).
- P3 held: 121 rows in 10 tables; checks 61 yes, 15 differs, 2 beyond reach, 11 quote, 14
  rerun only, 18 none.
- P4 failed in part: compile clean (no undefined references or citations, no overfull boxes),
  24 pages, checker only the accepted hits (5.1 two verdict labels, 7.6 one, 7.5/7.7 in scripts
  and ledger tables, 9.3 in scripts). On the pages (75 dpi, all 24 read): tables VIII
  (constraints), XI (convergence) and XII (backreaction) run off the bottom of their pages. The
  new long source strings (the 256^3 runs and the SR level-2 continuation in every row of the
  json) made each row four to eight lines tall.
Fix: row-level origins in `ledger.py` (rows on 32^3-128^3 keep their short source; rows with
256^3 data name "the 256^3 runs of the caption", whose run ids now stand once in the captions of
the constraints and convergence tables; SR level 2 at N_f names its two runs and the pass). A
test of the script on the figure package's jsons (scratch/E-stoch-inf/tmp/ledgertest9, not
registered, a test of the layout) compiled to 23 pages with every table on its page; a first
version of the caption wrote 256^3 outside math, which LaTeX set as math to the end of the
caption (seen on the page, fixed with $256^3$).
Prediction for R7 (registered run_all at the commit of this fix): jsons, langevin.json and all
19 PNGs byte-equal to R6; ledger 121 rows, same check counts, values equal to R6's
(ledger.csv differs only in the source column); compile 23 pages, every ledger table ends with
its bottom rule on its page. Refuted otherwise.

## Entry 11 (2026-11-24 14:00 PST): outcome of R7; final state of the update pass

R7 = E-20261124-215650-1de1ba5 (registered, production, two cores, 83 s, commit 1de1ba5).
Prediction of entry 10, item by item:
- held: 13 jsons byte-equal to repro/figs/fig, langevin.json equal (`checks.json`); all 19 PNGs
  byte-equal to R6 (so the four PDFs copied from R6 stay); ledger 121 rows, checks 61 yes,
  15 differs, 2 beyond reach, 11 quote, 14 rerun only, 18 none; every value and check equal to
  R6's, only the source column differs (ledger.csv compared row by row).
- held: every ledger table ends with its bottom rule on its page (pages 15-23 read at 75 dpi;
  page 24 pixel-identical to the R6 build's, read there). Tables copied from R7 (sha256 found in
  its `sha256sums.txt`).
- failed: 24 pages, not 23. The layout test of entry 10 ran with the label "ledgertest9" in
  place of a run id, which is shorter and saved a line per row; with the real id the one-patch
  table moves to page 23 and the drift table to page 24. No table is cut.
Compile clean (no undefined references or citations, no overfull boxes); checker with the
guide's forbid list: the accepted hits only (5.1 two verdict labels "not reproduced"; 7.6 one,
"no defect" about the reviewed code, guide exception 2; 7.5 and 7.7 only in `tables/ledger.tex`
and `scripts/`, exception 1; 9.3 only in `scripts/`, frames off through `figstyle.py`).
Pages 1-14 pixel-identical to the R6 build, which I read in full (entry 10).
State of RSF256: queue entry q0034 was dispatched while this pass ran, as run
E-20261124-214913-5956891 (Slurm job 5215, "submitted" at 13:58 PST); not waited for. Its rows
stay pending (Fig. 5 SR constraint rows, S14 SR per cell; ledger row and Table IV name it).

## Entry 12 (2026-11-24 14:41 PST): final correction pass after VERIFIER.md section 8; plan and predictions

Input: VERIFIER.md section 8 (commits f1bac41b, f738e127; lines 149-289). It checked the 16 rows
from the continued runs. Verdicts: joins bit-exact for all five runs, RSF256 included (q0034 ended
14:23 PST, joined by run E-20261124-222800-49ab461); rows 42, 49-52, 72-75 CONFIRMED; 48 CONFIRMED
for its window 0.5 <= N <= ln 64 (full span: 2.66e2 at the flipped run's last line); 65-67 now
CONFIRMED against the code's lockstep record (line 218); 77 and 81-83 CONFIRMED with shells of more
than ten independent modes; P1:520 is per ten thousand (8.5, our reading); USR level 2 fails it
above |n| of about 32; rows 68-71 (256^3 member of Fig. 7: 3.7e-7, order 1.48, per-mode rms 7.1e-7
and 6.7e-7) NOT CONFIRMED to the digits: the check finds 2.0e-7 (at |n| = sqrt 2), order 2.3-3.5,
per-mode 4.0e-7 and 3.3e-7, while it confirms the floor itself (independent of dx, dt and the
linear reference). Row 56 (SR per-cell rows) stays pending: RSF256 has ended, but the figure
package has not yet made its outputs (repro/figs RESULTS.md section 5).

What I found before any run, from the committed npz files and the check's cont.json (looked at, no
new number derived): the note's 256 maximum falls on |n|^2 = 6 (12 independent modes, 3.72e-7);
the check counts both hemispheres, so its selection includes |n|^2 = 2 (6 independent modes), and
its value on |n|^2 = 6 must lie below 2.0e-7. The two readers of R^NR differ in two places: the
note takes c[chi]/(2<chi>) and H_b = -<K>/(3<alpha>), the check c[ln chi]/2 and H = -<K>/3. At
32^3 and 64^3 their per-mode rms agree to 4 digits; at 128^3 and 256^3 the note's exceeds the
check's by about 6e-7 in quadrature at both.

Test R8a (registered analysis, `scripts/reader_split.py`, 2 cores, 0 card-hours): the four readers
A (note), B (note with H = -<K>/3), C (note with ln chi), D (both, the check's) on dump 17 of C128S
and CL256S, against one linear reference.
- P1. A reproduces the ledger: per-mode rms 7.11e-7 (128), 6.71e-7 (256); largest shell over
  more than ten independent modes 1.04e-6 (128), 3.72e-7 (256). Refuted if any differs in the
  third digit (my reimplementation would then differ from dumppass.py).
- P2. D reproduces the check: per-mode rms 4.00e-7 (128), 3.30e-7 (256); largest shell over shells
  of more than ten modes in both hemispheres 1.00e-6 (128) and 2.00e-7 at |n|^2 = 2 (256). Refuted
  beyond 2 per cent (the readers would then differ in a third place: modes, alphas or the phase).
- P3. The difference A - D is the same at both lattices (rms of |c_D - c_A|/|c_lin| within 20 per
  cent at 128 and 256): a property of the reader, not of the lattice. One of B or C alone carries at
  least 80 per cent of it; I do not predict which (the lapse factor needs <alpha> - 1 of order 1e-6,
  the logarithm a second-order term of that size). Refuted if neither alone does.
- P4. 1 - W is below 1e-12 for every injected mode at N_f (the window plays no part).
If P1-P3 hold, rows 68-71 keep the note's values with the reader named, the check column gives the
check's values ("differs"), and the text says the floor's level depends on the reader at the factor
the run gives, while its existence does not.

Then: ledger.py (check column of the 16 rows, rows 65-67 and 77 to yes, labels of 48 and 81-82 name
window and shell count, the convergence note names the reader), main.tex (Table IV check column,
Secs. III and V, abstract), registered run_all (R8), checker, compile, pages, README.

## Entry 13 (2026-11-24 14:44 PST): outcome of R8a, the reader split

R8a = E-20261124-224228-8e20938 (registered, two cores, commit 8e20938); a first attempt,
E-20261124-224156-28cbf07, failed in the figure (an index into the shell array) after writing
its json; kept on record. Outcome, prediction by prediction:
- P1 held: reader A gives per-mode rms 7.111e-7 (128) and 6.709e-7 (256), largest shell over more
  than ten independent modes 1.0384e-6 (|n|^2 = 58) and 3.7245e-7 (|n|^2 = 6), the ledger's values.
- P2 held: reader D gives 3.9993e-7 and 3.2979e-7 (check 3.998e-7, 3.298e-7), and over shells
  counted in both hemispheres 9.9998e-7 (|n|^2 = 58) and 2.0032e-7 at |n|^2 = 2 (check 1.0000e-6,
  2.0032e-7 at |n| = sqrt 2). The readers differ in nothing else.
- P3 held, and the split is total: the logarithm alone (C) carries all of it, the lapse factor
  nothing (<alpha> - 1 = -1.0e-12 and -2.0e-12; B - A 9e-13 and 1.8e-12 rms over |c_lin|). The rms of
  C - A over |c_lin| is 4.1450e-7 at 128 and 4.1449e-7 at 256: the change of reader is a
  second-order term of the field, the same on both lattices.
- P4 held: 1 - W = 0 for every injected mode at N_f.
With our shells and the check's reader the 256^3 maximum is 1.73e-7 (|n|^2 = 6) and the order
128 -> 256 is 2.53 (a factor 5.8); with our reader 1.48 (2.8). Figure `fig_reader_split.png`
(looked at): rms per shell of the departure, readers A and B on one curve, C and D on the other;
up to |n| of about 5.5 the curves of 128 and 256 coincide for each reader, the ln-chi curve lies
a factor of about two below over all shells, and above |n| = 6 only 128 keeps its lattice error.
Judgement [JUDGEMENT]: the floor has the size of the second-order terms of the field (a change of
the reader at second order moves it by a factor of two on both lattices, identically); that it
scales with the square of the amplitude stays [TO VERIFY] (a run at half the noise amplitude). The
note keeps its reader for the ledger values and adds the check's reader as rows from R8a.

## Entry 14 (2026-11-24 14:46 PST): corrections applied; prediction for R8

Applied (commit 4a413e32): ledger.py fills the check column of the 16 rows of the continued runs
from VERIFIER.md section 8 (42, 48-52 [177-181, 201], 72-75 [194-197], 81-83 [242-244] yes; 68-71
differs, with the check's ln-chi values [212, 214, 220]; 56 stays pending, named with q0034 and
"ended"); rows 65-67 [212] and 77 [248] move from differs to yes (section 8 confirms them with the
code's lockstep record and with independent-mode shells); rows 48, 81, 82 name window and shells;
four rows from R8a (256^3 maximum and its order read with ln chi, per-mode rms read with ln chi,
the change of reader); the spectra, curvature, convergence and backreaction notes say "independent
modes" and the convergence note names the reading of chi. main.tex: abstract, Sec. II definitions
(reading of chi; independent modes), Sec. III convergence (2.8 vs 5.8; floor of the size of the
second-order terms, [JUDGEMENT] from R8a; the square-of-amplitude test open), sign flip (narrows to
2-3 decades after the entry, the check's count), backreaction (SR below the bound on our shells, at
it on all), Sec. V (second pass of the check; seventeen rows differ), summary item 1, Table IV
check column, the contrasts caption and the two pending markers (q0034 ended, panels not made).

Prediction for R8 (registered run_all at the commit of this entry):
- P1. 13 lattice jsons byte-equal to repro/figs/fig, langevin.json equal (`checks.json`): the
  figure scripts did not change. Refuted by any false.
- P2. All 19 PNGs byte-equal to R7's (E-20261124-215650-1de1ba5). Refuted if one differs.
- P3. Ledger: 125 rows in 10 tables; checks 78 yes, 17 differs, 2 beyond reach, 11 quote, 14 rerun
  only, 3 none (tested beforehand on a copy of R7's jsons, scratch/E-stoch-inf/tmp, a layout test,
  not registered). Refuted by another count or a stop of the script.
- P4. Compile without undefined references or overfull boxes, 24 or 25 pages; every ledger table
  ends with its bottom rule on its page (the convergence table grows by four rows: the risk).

## Entry 15 (2026-11-24 14:49 PST): outcome of R8; final state of the correction pass

R8 = E-20261124-224631-730b585 (registered, production, two cores, commit 730b585). Prediction of
entry 14, item by item:
- P1 held: all 13 lattice jsons byte-equal to repro/figs/fig, langevin.json equal (`checks.json`).
- P2 held: all 19 PNGs byte-equal to R7's, so the committed figure PDFs stay (R6 and R2 sources).
- P3 held: 125 rows in 10 tables; checks 78 yes, 17 differs, 2 beyond reach, 11 quote, 14 rerun
  only, 3 none (the pending SR per-cell row, the eps1 row added after the first check, the change
  of reader from R8a). Tables copied from R8, sha256 found in its `sha256sums.txt`.
- P4 held in its alternative: compile clean (no undefined references or citations, no overfull
  boxes), 25 pages; every ledger table ends with its bottom rule on its page (pages 17, 19-25 read;
  the convergence table XI fills page 22 to about four fifths).
Checker with the guide's forbid list: the accepted hits only (5.1 two verdict labels "not
reproduced", lines 47 and 410; 7.6 one, "no defect" about the reviewed code, exception 2; 7.5 and
7.7 only in `tables/ledger.tex` and `scripts/`, exception 1; 9.3 only in `scripts/`). A third 5.1
hit ("not yet analysed" in a pending marker) was rewritten ("analysis to come"). After the R8
compile one sentence of Sec. III A gained the reading of chi as a cause of differences; the
recompile changed page 3 only (pixel comparison of all 25 pages at 75 dpi), read again.
Pages read at 75 dpi: 1, 3, 4, 5, 6, 7, 8, 11, 15, 17, 19, 20, 21, 22, 23, 24, 25 (every page with
changed text and every ledger table that changed). Not read in this pass: 2, 9, 10, 12, 13, 14, 16,
18 (text and tables unchanged; their position may have moved by the extra page at 22).
State of RSF256: ended 14:23 PST (q0034, run E-20261124-214913-5956891), joined bit-exactly by the
check (run E-20261124-222800-49ab461); repro/figs has not yet run `runs.py rsf256` or a figure run
with `--rsf256`, so the SR constraint panels and the SR per-cell row stay pending.

## Entry 16 (2026-11-24 15:17 PST): last pass, RSF256 rows; plan and predictions (written before R9 runs)

Input: repro/figs has made the RSF256 outputs (join check E-20261124-225720-444aecc, pass
E-20261124-225826-0bf3842, figure run E-20261124-230839-0e1e13a; its RESULTS.md section 5 and
request to this package). Plan: copy the functional changes of repro/figs/figures (`runs.py`,
`joins.py`, `fig_signflip.py`, `make_figs.py`; the note's neutral titles kept) into
`manuscript/scripts/`; add `--rsf256 <pass 0bf3842>` to `LATTICE_ARGS`; take the SR one-point
figure from `fig2_sr_contrast` (RSF256, all six panels) in place of the P256v6 field-only version;
in `ledger.py` replace the PENDING row by value rows from this run's `fig2_sr_contrast.json` and
`fig_signflip.json` (check "run joined": the check joined RSF256 and compared its records with the
dump means, VERIFIER.md 8.6, but did not recompute the percentiles), and correct the label of the
USR per-cell row (its json key `pct_H_p99_max` holds the 99.5th percentile, index 7 of figlib.QUANT,
not the 99th); then the two `\pending` markers, the caption of the contrasts figure, the abstract,
the discussion and the ledger appendix text. Registered run R9 = run_all.

Definitions of the new numbers: per cell = percentiles of |H|/[H] (|M|/[M]) over the 256^3 cells
of one dump, [H] the sum of the magnitudes of the terms of H; 35 dumps of the SR run, t = 0 to 8.5;
"entry plateau" = the dumps with 0.75 <= N <= 3.2 (after the initial transient, before the rise of
the last crossings); record mean = <|H|/[H]> of the code's record.

Predictions for R9 (what would refute each):
- P1: checks.json: every lattice json of repro/figs/fig (now 17 with fig2_sr_contrast,
  fig3_sr_spec, fig6a_sr_Kspec) byte-equal to this run's; langevin equal. Refuted by any false.
- P2: of the 19 manuscript PNGs only fig_contrast_sr differs from R8's (new source); all others
  byte-equal (fig_signflip.py gains json keys only). Refuted by any other differing PNG.
- P3: ledger 133 rows in 10 tables (125 - 1 + 9); checks 80 yes, 17 differs, 2 beyond reach, 11
  quote, 14 rerun only, 7 run joined, 2 none. Values: largest 99.5th percentile of |H|/[H] 1.78e-10
  at N = 4.39; max over cells 3.63e-10; at N_f 6.48e-14; fall 2.7e3; entry plateau 3.38e-12 to
  4.50e-12; |M|/[M] 99.5th percentile 1.84e-3 at N = 4.86; record mean maximum 5.10e-11 at N =
  4.43; dump means against the record 4.1e-15 (H), 3.8e-15 (M) (values read beforehand from the
  committed `repro/figs/fig/fig2_sr_contrast.json` and `fig_signflip.json`, so not blind).
  Refuted by any other value or by ledger.py stopping on a verifier string.
- P4: compile clean, no `\pending` left in the text (the macro may stay defined); page count 25 or
  26; every ledger table ends on its page.

## Entry 17 (2026-11-24 15:22 PST): outcome of R9; the constraints table ran off its page; prediction for R10

R9 = E-20261124-231835-dba3192 (registered, production, two cores, commit dba3192, about a minute).
- P1 held: every lattice json of repro/figs/fig byte-equal to this run's (16 files, not the 17 I
  wrote: miscounted beforehand), langevin equal (`checks.json`).
- P2 held: of the 19 manuscript PNGs only `fig_contrast_sr.png` differs from R8's; looked at: six
  rows, no title, the constraint rows as repro/figs' figure (one layout remark: the top tick label
  of the |H|/[H] row touches the bottom of the R^NR row, as in the USR figure; no number depends on it).
- P3 held: 133 rows in 10 tables; checks 80 yes, 17 differs, 2 beyond reach, 11 quote, 14 rerun
  only, 7 run joined, 2 none; every predicted value as printed (1.78e-10 at N = 4.39, 3.63e-10,
  6.48e-14, 2.7e+03, 3.38e-12 and 4.50e-12, 1.84e-03 at N = 4.86, 4.47e-02, 4.1e-15 and 3.8e-15,
  5.10e-11 at N = 4.43). Tables copied, sha256 found in R9's `sha256sums.txt`.
- P4 failed in part: compile clean (no undefined references, citations or overfull boxes), 25
  pages, no `\pending` used; but Table VIII (constraints, now 21 rows with five-line sources) runs
  off page 19 below the |M|/[M] rows: no bottom rule. The checker does not see it (README).
Text changed before the compile (paper-writing pass on each sentence): abstract last sentence
(the SR per-cell violation reaches the published level at the last crossings and then decays);
intro "pending" -> "open"; contrasts caption last sentence; one paragraph of Sec. III G (per-cell
tail: more than a decade below the stated order on the entry plateau, at it at the last crossings,
more than three decades lower at the end); discussion "Pending" sentence removed; Table IV caption
and the rows "Figs. 2 and 4" and "Hamiltonian violation"; ledger appendix text ("run joined").
Checker with the forbid list: 5.1 one (the verdict label "not reproduced", line 47), 7.6 one ("no
defect", exception 2), 7.5/7.7 only in `tables/ledger.tex` and `scripts/`, 9.3 only in `scripts/`.

Fix: the per-cell rows (the nine new SR rows and the USR per-cell row) go into their own section
"Per-cell constraints" (a table of its own after the constraints table), with the definitions in
its caption and the join and pass named there, so the per-row source shortens to the run and pass.
Prediction for R10 (same commit plus this change): lattice jsons, PNGs and langevin as R9; 133
rows in 11 tables, the same check counts and values; after the compile every ledger table ends with
its bottom rule on its page; page count 25 or 26. Refuted by any table off its page or any changed value.

## Entry 18 (2026-11-24 15:24 PST): outcome of R10; final state of the last pass

R10 = E-20261124-232241-08e1705 (registered, production, two cores, commit 08e1705, about a minute).
Prediction of entry 17, item by item:
- held: lattice jsons (16) byte-equal to repro/figs/fig, langevin equal; all 19 PNGs byte-equal to
  R9's (so the committed `fig_contrast_sr.pdf` from R9 stands; the other 18 PDFs stay from R6 and R2).
- held: 133 rows in 11 tables, checks 80 yes, 17 differs, 2 beyond reach, 11 quote, 14 rerun only,
  7 run joined, 2 none; every value as in R9 (csv compared row by row: only the source strings of
  the per-cell rows and the label of the USR per-cell row changed). Tables copied, sha256 found in
  R10's `sha256sums.txt`.
- held: compile clean (no undefined references or citations, no overfull boxes), 26 pages; every
  ledger table ends with its bottom rule on its page (Tables V-XV on pages 16-26; Table VIII, the
  constraints, on 19 and the new Table IX, per-cell constraints, on 20).
Checker with the forbid list: the accepted hits only (5.1 one, the verdict label "not reproduced",
line 47; 7.6 one, "no defect", exception 2; 7.5 and 7.7 only in `tables/ledger.tex` and `scripts/`;
9.3 only in `scripts/`).
Pages read at 75 dpi: in the R9 build 1, 6-15 (every page with changed text, the verdict table on
15) and 16-24; in the R10 build every page that differs from the R9 build: 12 and 16-26. Pages 2-5
are byte-identical renders to the committed R8 build. No pending marker is left in the text (the
`\pending` macro stays defined, unused).
State: the two rows that waited for RSF256 are filled; nothing of this note waits for a run.
The check joined RSF256 and compared its records with the dump means (VERIFIER 8.6) but has not
recomputed the per-cell percentiles: the seven "run joined" rows of Table IX.

## Entry 19 (2026-11-24 19:41 PST): G2 sections (ruling 0035 item 1); plan and predictions, written before R11 runs

Lead of batch 15. The G2 package of the track (SCOPE 4c, g2prod entries 2-4, stage/G2/VERIFIER.md)
enters this note as a new section after the lattice section: the criteria fixed before the runs,
the production ladder on the release card build, the resolution pair 256^3/320^3, the window, the
constraint scaling with its one failure, the quarter pair, the three-amplitude reading (after the
data, labelled so) and the fresh verifier. Four new scripts (each drafted into
scratch/E-stoch-inf/tmp/b15 and looked at before this entry): schem_ladder.py (verification
ladder), fig_g2_mosaic.py (slice mosaic of R^NR at N_f, U256ap, three magnifications), 
fig_g2_resolution.py (largest departure per shell at 256^3 and 320^3 and their ratio),
fig_g2_halving.py (factor of the even parts, three readings). ledger.py: a section "Ultra-slow-roll
criteria" with rows from the registered judge, quarter-pair and verifier runs (each json checked
against its run's sha256sums.txt), checks against stage/G2/VERIFIER.md lines; a check code "own"
for rows whose value is the verifier's own run (three-amplitude reading: no second check exists).
Predictions for R11 (run_all, registered):
- P1: the 16 lattice jsons equal the committed ones (checks.json all true), langevin equal; the
  PNGs of every figure of R10 repeat byte for byte (no input changed).
- P2: fig_g2_mosaic.json rms_R 0.89452 (= judge rms_R_end 0.894520 of U256ap), max 4.568.
- P3: fig_g2_halving.json: M fixed-level min 3.9245 (11 judged), H 3.9916-4.0424 (9), three-amplitude
  max deviation 1.2e-3 (M) and 4.4e-3 (H).
- P4: fig_g2_resolution.json: median ratio for |n| <= 20 within 0.99 +- 0.01 (third-order part, not
  resolution), for |n| >= 40 between (5/4)^4 = 2.44 and (5/4)^6 = 3.81 (2.9 in the draft).
- P5: the ledger builds (every verifier string on its line); about 24 new rows; the note compiles
  with no undefined reference; the new tables and figures stay on their pages (read every changed
  page). Refuted if any of these fails; then fixed and rerun as R12.

## Entry 20 (2026-11-24 19:50 PST): outcome of R11 (E-20261125-034431-d86678b); prediction for R12

R11 completed (exit 0, two cores, about a minute). P1 HELD: checks.json 16 of 16 lattice jsons
equal, langevin equal; every PNG of R10 repeats byte for byte in R11. P2 HELD: mosaic rms 0.89452,
max 4.568. P3 HELD: M fixed-level outside value 3.9245 at N = 6.52 of 11, H 3.9916-4.0424 (9),
three-amplitude 4.4e-3 (H), 1.2e-3 (M). P4 HELD: ratio medians 0.992 (|n| <= 20) and 2.91
(|n| >= 40). P5: ledger built, 154 rows in 12 tables (21 new; checks: yes 97, differs 18, beyond
reach 2, quote 11, rerun only 14, run joined 7, verifier's run 2, none 3); compile clean except
one overfull box (the odd-even split on one line: split into two aligned lines) and a caption
estimated at 5.4 lines (shortened). Figures looked at: fig_g2_halving (its legend wrote the
amplitude as s, which the note uses for the window steepness: changed to lambda), fig_ladder,
fig_g2_mosaic, fig_g2_resolution as drafted. Prediction for R12 (same command): everything of R11
repeats byte for byte except fig_g2_halving (legend only); the ledger repeats with its run id.

## Entry 21 (2026-11-24 19:56 PST): outcome of R12 (E-20261125-034702-3953daf); prediction for R13

R12 HELD its prediction: only fig_g2_halving.png differs from R11; checks all true; ledger values
equal. Compile: 30 pages, no undefined reference or citation, no overfull box. Checker: remaining
hits as accepted before (5.1 "not reproduced" verdict label; 7.6 "no defect" about the reviewed
code; 7.5, 7.7 only in scripts/ and tables/ledger.tex; 9.3 only in scripts/). Pages read at 75 dpi:
9, 10, 11, 12, 14, 30 (new section, its four figures, discussion and summary, the new ledger
table, which ends with its bottom rule on its page). Two places still wrote the noise amplitude as
s (the window steepness in this note): the ladder schematic and the caption and rows of the new
ledger table; changed to lambda. Prediction for R13: only fig_ladder.png and the ledger table
change (text only); every other PNG and json byte-equal to R12.

## Entry 22 (2026-11-24 19:58 PST): outcome of R13 (E-20261125-034920-07b5d5b); R14

R13 HELD: only fig_ladder.png differs from R12 (lambda in the amplitude box). One s was left in the
ledger caption (e(s)/e(s/2)); written e(lambda)/e(lambda/2). Prediction for R14: byte-equal to R13
except tables/ledger.tex (caption only). R14 is the source of the committed figures and tables.

## Entry 23 (2026-11-24 20:00 PST): outcome of R14 (E-20261125-035103-f18b379); C16 schematics; R15

R14 HELD: every PNG byte-equal to R13; ledger.tex differs only by the caption and the run id in its
"this run" sources. Compile clean (30 pages), pages 10 and 30 read again.
C16 of the G2 checklist (architecture and gate timeline at G2) was still missing: the G1 versions
(tracks/E-stoch-inf/note/scripts) are copied into this note's scripts and brought to the state of
2026-11-24 (G1 passed, G2 package ready for review; USR runs, window, resolution pair, three
amplitudes, level 2 in the later releases; drafts looked at in scratch/E-stoch-inf/tmp/b15); a short
appendix "The track: architecture and gates" carries them. Prediction for R15: every figure of R14
byte-equal; two new PNGs (fig_architecture, fig_timeline); the note compiles with no undefined
reference, about 32 pages; the appendix figures fit their pages.
