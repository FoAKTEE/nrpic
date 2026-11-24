# repro/note: working note on the reproduction of arXiv:2401.08530 and arXiv:2512.14649

Package of Track E (decision 0028). The working note on the reproduction of both papers, written
with the paper-writing skill: `manuscript/main.pdf` (25 pages, REVTeX, PRD style). Predictions and
outcomes: `JOURNAL.md` (entries 1-4 first draft, 5-8 correction pass after the verifier, 9-11
update pass after the continued runs, 12-15 final correction pass after VERIFIER.md section 8).
State: 2026-11-24 14:50 PST, after the final correction pass (batch R3). Four of the five continued
runs are in the note and checked. The fifth, RSF256 (queue entry q0034, run
E-20261124-214913-5956891), ended at 14:23 PST and was joined bit-exactly by the independent check
(run E-20261124-222800-49ab461), but the figure package has not yet made its outputs: the two rows
that need it stay pending, named with q0034.

Paper I = arXiv:2401.08530 (one patch), Paper II = arXiv:2512.14649 (lattice). Independent
check = package repro/verify, `tracks/E-stoch-inf/repro/verify/VERIFIER.md` (sections 1-7 at
0de2198a; section 8, the continued runs, at f1bac41b and f738e127), an agent that produced none of
the runs and was given the raw outputs and the claims, not the conclusions. Every ledger row now
carries its check except three (the pending row and two rows added after the check).

## What the note claims

1. Equations: computer algebra confirms that the stochastic sources are gauge independent and
   leave the constraints unsourced at linear order; 17 misprints, none of which enters a code
   (8 of them rederived by the independent check: items 1, 3, 6, 7, 8, 10, 14, 15).
2. Lattice (Paper II): everything linear theory fixes is reproduced with an independent code
   (AthenaK Z4c with the stochastic sources): background, spectra and freezing, extrinsic
   curvature through the crossings, the convergence of the spectra on four lattices, second-order
   constraint plateaus and the first-order rise under a flipped source in both scenarios.
   Spectral convergence: close to sixth order up to 128^3 (factors 52 and 62 per doubling; 43
   and 34 with the verifier's own linear reference), then a factor 2.8 (order 1.48) from 128^3 to
   256^3 with our reading of the conformal factor, c[chi]/(2<chi>), and 5.8 (order 2.53) with the
   check's c[ln chi]/2: a floor at the longest shells (per-mode rms 7.1e-7 and 6.7e-7 at 128^3 and
   256^3 with ours, 4.0e-7 and 3.3e-7 with ln chi) that does not move when dx and dt both halve.
   The two readings differ by 4.14e-7 per mode (rms) on both lattices alike (run
   E-20261124-224228-8e20938, R8a), so the floor has the size of the second-order terms of the
   field [JUDGEMENT]; that it scales with the amplitude squared is [TO VERIFY] (half-amplitude run).
   The check's 256^3 digits (2.0e-7, order 2.3) are reproduced by R8a with its reader and its
   shells (both hemispheres, which add |n|^2 = 2).
3. The one-point bands of Paper II are 3.5 (SR) to 4 (USR) times wider than ours while its
   spectra agree with ours; for a Gaussian field the spectrum fixes the band, so the factor lies in
   the published real-space normalisation or plotting (the "amplitude factor"; cause open). The
   independent check found the same factor from its own reading of the published figures.
4. Constraint levels are one to two decades below Paper II's (most of it the square of the
   amplitude factor). Plateau ratios (median over 0.5 <= N <= ln 8 of the time-matched ratio,
   finer over coarser) 0.99-1.17 from 64^3 to 128^3 and 1.03-1.12 from 128^3 to 256^3; late in
   the runs the finer lattices end higher in three curves, as Paper II says of its own runs
   (source line 750). The "orders of the entry maximum 32 -> 64" (4.15, 3.25) of the earlier
   ledger are withdrawn (repro/figs JOURNAL entry 11): replaced by the plateau ratios. Flipped
   sign: H/[H] about 1e-7 in both scenarios, a hundred times below the printed 1e-5; median jump
   flipped/proper 1.1e5 (SR, to N = 4.39) and 8.0e3 (USR); the SR gap is smallest within the entry
   at 1.4e3 and narrows to 2.7e2 at the end of the flipped run (the check's count).
5. Backreaction: Paper II's bound (per ten thousand, P1:520 `\textpertenthousand`; the check
   confirms the reading, VERIFIER 8.5) holds at large scales, fails at the USR top shells (24 per
   cent of all shells, as Paper II's own figure shows); SR level 2 against 0 at N_f: largest shell
   7.93e-5, rms (|n| <= 32) 1.505e-5, the same to four digits as at N = 7.19 (frozen after the last
   crossing), so below the bound on shells with more than ten independent modes and at it with
   every shell (3 sparse shells above it, at most 1.4e-4). Level 1 against 0 is a difference of two
   time integrations of one background (core's review: runs stand).
6. One patch (Paper I): the published figures follow from a background integrated by forward
   Euler at 0.01 e-folds (the converged background stops on the plateau, closed form) and from the
   Ito reading of the printed equation; widths to 1-2 per cent, skewness to about ten per cent
   (1.04 ours, 1.12 independent, about 1.1 published). The Ito term carries alpha^5, not alpha^3;
   the USR noise amplitude is smaller than printed by sigma^2/3; the SR ratio exceeds one by
   about 5 eps1 at the crossing.

## Verdicts per figure and statement (Table IV of the note), final for this pass (check column after VERIFIER.md section 8)

| Item | Verdict | Independent check | Pending run |
|---|---|---|---|
| II Fig. 1, background | reproduced | confirmed (two eps2 maxima beyond its reach) | |
| II Figs. 2, 4, one-point statistics | in part (shape, timing yes; amplitude no) | confirmed, factor 3.5 / 4, cause open | SR constraint rows: RSF256, queue q0034 (run E-20261124-214913-5956891; ended 14:23 PST, panels not yet made) |
| II Figs. 3, 5, spectra | reproduced | confirmed; maxima 10-15 % apart (reference) | |
| II Fig. 6, K and shear spectra | reproduced; absent USR hierarchy in part | not redone | |
| II Fig. 7, spectral convergence | reproduced (four lattices, monotone; order 5-6 to 128^3; floor at the longest shells of 256^3 of the size of the second-order terms) | confirmed on four lattices against the code's record; floor confirmed (independent of dx, dt, reference); 256^3 digits differ by the reading of chi | |
| II Fig. 8, constraint convergence | in part (plateaus equal on 64^3-256^3, decay; levels lower) | records, entry maxima, plateau ratios confirmed on four lattices | |
| II Fig. 9, backreaction | in part (USR as the figure; SR level 2 unchanged after the last crossing; level 1 = scheme difference) | review of the code: runs stand; values confirmed at N = 7.19 and N_f with our shells | |
| II: start of USR | reproduced as the figure shows it (text one e-fold late) | confirmed | |
| II: power to order unity, linear agreement | reproduced | confirmed | |
| II: outliers of order ten | not reproduced (amplitude factor) | confirmed; II's own figure reaches about 18 | |
| II: Hamiltonian violation at next order | in part (second order; level 1-2 decades lower) | records confirmed, SR to N_f | SR per cell at 256^3: RSF256, q0034 (ended, not yet analysed) |
| II: flipped sign gives first order | in part (first order in both scenarios through the entry; level 100x lower than printed) | confirmed, including the level, over the whole SR flipped run | |
| II: momentum constraint at last crossing | reproduced (second order above about 13 cells) | not redone | |
| II: backreaction below 1e-4 | in part (large scales yes; USR top shells no; SR at the bound) | values confirmed; USR above the bound on 24 % of all shells | |
| I Fig. 1, paths | reproduced (Ito, Euler background) | confirmed | |
| I Fig. 2, skewness, kurtosis | reproduced (skewness to about 10 %) | widths confirmed; skewness 1.12 vs 1.04 | |
| I Figs. 3, 4, distributions | reproduced (Ito) | confirmed | |
| I: slope reached near 3.04 | reproduced only with Euler at 0.01 | confirmed (closed-form plateau stop) | |
| I: Stratonovich evolver | not matched (figures follow Ito) | confirmed (Stratonovich widths 15-19 % off) | |
| I: Ito term alpha^3 | corrected to alpha^5 | confirmed (derivation, Monte Carlo) | |
| I: amplitude valid in SR and USR | USR smaller by sigma^2/3; SR 1 + about 5 eps1 | USR confirmed; SR 1.06, 1.12 on its backgrounds | |
| I: noise off, alpha^3 -> 1, tails | reproduced; e-fold tails in part | left skew confirmed (one seed); tails not redone | |

Ledger: 125 rows in 10 tables, each with the verifier's verdict and the line of VERIFIER.md
(78 yes, 17 differs, 2 beyond reach, 11 quote, 14 rerun only, 3 none: the pending SR per-cell
row, the eps1 row and the change-of-reader row added after the check); `ledger.py` stops if a
verifier string is not on its line. Section 8 moved rows 65-67 and 77 from differs to yes (the
code's lockstep record; independent-mode shells) and gave checks to the 16 rows of the continued
runs (12 yes; rows 68-71, the 256^3 member of Fig. 7 with our reader, differ); four rows from R8a
give the same quantities with the check's reader.

## What is in this directory

| Path | Content |
|---|---|
| `WRITING_GUIDE.md`, `NOTATION.md` | per-paper layer of the skill: readers, outline, numbers, dictionary, project names (the forbid list), exceptions (ledger with run ids; which code each run used) |
| `notes/2026-11-24-story.md` | skill 10.1: story, 300- and 1000-word versions, self-review in place of parallel reviewers |
| `manuscript/main.tex`, `references.bib`, `main.pdf` | the note (I intro; II sources; III lattice; IV one patch; V discussion; VI summary; App. A misprints, B parameters, C set-up, D verdicts with check column, E ledger in 10 tables) |
| `manuscript/figures/` | 19 figures; PDFs of `fig_specconv`, `fig_constraints`, `fig_ablation`, `fig_signflip` from R6 (E-20261124-215017-cb16c27), the other 15 from R2 (E-20261124-180038-4d4651a); R7 and R8 reproduce every PNG of R6 byte for byte, and R3-R6 those of R2 for the 15 |
| `manuscript/tables/ledger.tex`, `ledger.csv`, `ledger_checks.json` | the ledger with the check column, from R8 (E-20261124-224631-730b585), sha256 checked against its `sha256sums.txt` |
| `manuscript/scripts/` | figure scripts (copies of repro/figs/figures with neutral titles, and of repro/langevin), `ledger.py` (rows, section definitions, verifier checks, per-row sources; reads R8a's `reader_split.json` after a sha256 check), `run_all.py`, `schem_pipeline.py`, `figstyle.py`, `paperfig.py`, `reader_split.py` (R8a: four readers of R^NR on the final SR dumps of 128^3 and 256^3, json and figure) |

## Registered runs of this package

| Run | What |
|---|---|
| E-20261124-174752-f387f2a | R1: first run_all (jsons byte-equal to figure run E-20261124-173254-420115f) |
| E-20261124-180038-4d4651a | R2: ablation legend, PENDING rows; source of 15 committed figure PDFs |
| E-20261124-185556-df39d1c | R3: correction pass, ledger with check column (8 tables; two ran off their pages) |
| E-20261124-185912-45510c2 | R4: ledger split into 10 tables |
| E-20261124-190054-08f916a | R5: last section renamed (guide dictionary) |
| E-20261124-215017-cb16c27 | R6: update pass with the four continued runs; source of 4 committed figure PDFs (three ledger tables ran off their pages) |
| E-20261124-215650-1de1ba5 | R7: ledger sources per row group |
| E-20261124-224156-28cbf07 | R8a, first attempt: failed in its figure (index into the shell array) after writing its json; kept on record |
| **E-20261124-224228-8e20938** | R8a: reader split of the 256^3 member of Fig. 7 (`reader_split.py`; figure `fig_reader_split.png` looked at); read by `ledger.py` |
| **E-20261124-224631-730b585** | R8: final correction pass; source of the committed tables |

All: production, two cores, one to one and a half minutes each (R8a: under a minute), 0
card-hours; every run_all's lattice jsons equal to the committed jsons of the figure package at
the time (`checks.json` of each); langevin.json equal throughout.

## How to rerun and rebuild

From the worktree root, with the package committed:

```text
harness/bin/nrpic-run submit --kind production --gate G2 --preregistered "tracks/E-stoch-inf/repro/note/JOURNAL.md#entry-<k>" \
  --purpose "..." --package tracks/E-stoch-inf/repro/note --cores 2 -- \
  bash -c 'OMP_NUM_THREADS=2 python3 tracks/E-stoch-inf/repro/note/manuscript/scripts/run_all.py "$NRPIC_RUN_DIR"'
R=/data/haiyangw/nrpic/scratch/E-stoch-inf/<run id>
cp $R/tables/* tracks/E-stoch-inf/repro/note/manuscript/tables/
# figures: copy a PDF only if its PNG differs from the committed run's PNG (cmp figures/*.png)
cd tracks/E-stoch-inf/repro/note/manuscript
python3 /home/haiyangw/.claude/skills/paper-writing/scripts/check_manuscript.py --main main.tex --compile \
  --forbid 'nrpic-run|nrpic-stage|REPRO_MAP|SETUP_AUDIT|RESULTS\.md|P256v6|USF256|RSF256|CL256|AL[012][SU]|M64[SU]|repro/|scratch/|athena_gpu'
```

The checker does not see a float taller than its page: read every rendered page (pdftoppm -r 75);
a layout test with a short run label underestimates the row heights (JOURNAL entry 11). R8a is
rerun with `nrpic-run submit ... -- bash -c '... python3 .../scripts/reader_split.py "$NRPIC_RUN_DIR"'`
(uses the worktree's `.venv` for numpy, scipy, matplotlib); a new R8a needs its run id in `R8A` of
`ledger.py`.
`run_all.py` passes make_figs.py the arguments of repro/figs' figure run E-20261124-213739-9776185
(`--cl256s`, `--al2s` from pass E-20261124-213029-e937f69); the joined records of the continued
runs come through `runs.py` (JOINED, join check E-20261124-212343-7e9c4b2). When the scripts of
repro/figs/figures change, copy them and keep the note's neutral titles (`make_figs.py`,
`fig_signflip.py`, `fig1_meanrolls.py`, `fig_ablation.py`; `figlib.py` keeps its own path depth).

RSF256 (q0034, run E-20261124-214913-5956891) has ended (14:23 PST) and the check has joined it
(E-20261124-222800-49ab461). Still to do outside this package: repro/continue's join and repro/figs'
`runs.py rsf256` and figure run with `--rsf256 <pass>` (repro/figs RESULTS.md section 5).
Then here: add `--rsf256 <pass>` to `LATTICE_ARGS`, switch FIGS "fig_contrast_sr" to the RSF256
contrast figure if repro/figs makes it the SR figure, replace the PENDING row of `ledger.py`
(Constraints, SR per-cell rows) by value rows (check "none"), rerun, and replace the two
`\pending{...}` markers of `main.tex` (Table IV rows "Figs. 2 and 4" and "Hamiltonian violation")
and the last sentence of the contrasts caption and of the abstract.

## Checker and pages, last run on the committed text

Compile: 25 pages, no undefined references or citations, no overfull boxes. Checker with the
forbid list: remaining hits accepted under the guide: 5.1 (two: the verdict label "not
reproduced"), 7.6 (one: "no defect" about the reviewed code, exception 2), 7.5 and 7.7 only in
`tables/ledger.tex` and `scripts/` (exception 1), 9.3 in `scripts/` (`figstyle.py` turns frames
off). Pages read at 75 dpi in the final pass (JOURNAL entry 15): 1, 3-8, 11, 15, 17, 19-25 (every
page with changed text and every changed ledger table); pages 2, 9, 10, 12-14, 16, 18 carry text
and tables unchanged since the R6/R7 builds, where they were read. Every ledger table ends with
its bottom rule on its page.

## What is still open

- PENDING: RSF256 (SR 256^3 with dumps; queue q0034, run E-20261124-214913-5956891, ended 14:23
  PST, joined by the check): the SR constraint rows of the one-point figure and the SR per-cell
  part of "Hamiltonian violation at the next order" wait for repro/figs' pass on it; then add
  `--rsf256 <pass>` to `LATTICE_ARGS`, replace the PENDING row of `ledger.py` by value rows, rerun,
  and replace the two `\pending{...}` markers of Table IV, the caption of Fig. 5 and the last
  sentence of the abstract.
- Not established: that the floor of the spectral convergence at the longest shells of 256^3
  scales with the square of the amplitude (R8a shows it has the size of the second-order terms; a
  run at half the noise amplitude would test the scaling, repro/figs request, about 0.5
  card-hours); the cause of the amplitude factor (only the authors'
  normalisation of the real-space draw can settle it); the 7 per cent difference of the Ito
  skewness between two implementations (1.04 against 1.116 +- 0.012); the half-loss time on the
  converged background (4.80 ours, 5.36-5.38 independent, different loss criteria).
- Not redone by the independent check: extrinsic-curvature spectra, momentum constraint against
  cells per wavelength, the gauge families, nine of the 17 misprints, the constraint field from
  the metric with an independent stencil, the tails of the one-patch distributions, and the
  change-of-reader row from R8a (added after its section 8).
- Skill 10.1 step 4 (parallel reviewers) was not run: no subagent tool in these sessions.

## Requests

- repro/verify: the two requests of the update pass are answered (section 8: the 16 rows
  checked; P1:520 read as per ten thousand, confirmed in 8.5). New, optional: check R8a
  (E-20261124-224228-8e20938), the claim that the note's and the check's 256^3 digits of Fig. 7
  differ only by the reading of chi (rms 4.14e-7 per mode at 128^3 and 256^3).
- repro/figs: the RSF256 pass (`runs.py rsf256`, figure run with `--rsf256`), which the two pending
  rows of this note wait for; the half-amplitude run that would test the scaling of the floor.
- Lead of E: SETUP_AUDIT item 4 still says N* + 8.04 for SR, the note uses 8.10 (request of
  repro/figs, unchanged); when q0034 ends, the steps under "How to rerun" for RSF256.
- core (minor, python/nrpic/figstyle.py): save PDFs without a creation date (or honour
  SOURCE_DATE_EPOCH), so reruns give byte-identical PDFs (unchanged request).
