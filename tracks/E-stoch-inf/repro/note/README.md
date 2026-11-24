# repro/note: working note on the reproduction of arXiv:2401.08530 and arXiv:2512.14649

Package of Track E (decision 0028). The working note on the reproduction of both papers, written
with the paper-writing skill: `manuscript/main.pdf` (24 pages, REVTeX, PRD style). Predictions and
outcomes: `JOURNAL.md` (entries 1-4 first draft, 5-8 correction pass after the verifier, 9-11
update pass after the continued runs). State: 2026-11-24 14:00 PST, after the update pass (batch
R3): four of the five continued runs of repro/continue are in the note; the fifth, RSF256, was
dispatched from queue entry q0034 as run E-20261124-214913-5956891 (Slurm job 5215) and has not
ended; the rows that need it are pending.

Paper I = arXiv:2401.08530 (one patch), Paper II = arXiv:2512.14649 (lattice). Independent
check = package repro/verify, `tracks/E-stoch-inf/repro/verify/VERIFIER.md` (commit 0de2198a),
an agent that produced none of the runs and was given the raw outputs and the claims, not the
conclusions. It saw the runs before their continuation: the rows that come from the continued
runs carry no check (ledger: "none").

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
   256^3: a floor at the longest shells (per-mode rms 7.1e-7 at 128^3, 6.7e-7 at 256^3) that
   does not move when dx and dt both halve; cause open (R7 ledger, convergence table).
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
   flipped/proper 1.1e5 (SR, to N = 4.39) and 8.0e3 (USR).
5. Backreaction: Paper II's bound (per ten thousand, P1:520 `\textpertenthousand`) holds at
   large scales, fails at the USR top shells (as Paper II's own figure shows); SR level 2 against
   0 at N_f: largest shell 7.93e-5, rms (|n| <= 32) 1.505e-5, the same to four digits as at
   N = 7.19 (frozen after the last crossing), so below the bound on shells with more than ten
   modes and at it with every shell (the check's 1.4e-4 at N = 7.19). Level 1 against 0 is a
   difference of two time integrations of one background (core's review: runs stand).
6. One patch (Paper I): the published figures follow from a background integrated by forward
   Euler at 0.01 e-folds (the converged background stops on the plateau, closed form) and from the
   Ito reading of the printed equation; widths to 1-2 per cent, skewness to about ten per cent
   (1.04 ours, 1.12 independent, about 1.1 published). The Ito term carries alpha^5, not alpha^3;
   the USR noise amplitude is smaller than printed by sigma^2/3; the SR ratio exceeds one by
   about 5 eps1 at the crossing.

## Verdicts per figure and statement (Table IV of the note), final for this pass

| Item | Verdict | Independent check | Pending run |
|---|---|---|---|
| II Fig. 1, background | reproduced | confirmed (two eps2 maxima beyond its reach) | |
| II Figs. 2, 4, one-point statistics | in part (shape, timing yes; amplitude no) | confirmed, factor 3.5 / 4, cause open | SR constraint rows: RSF256, queue q0034 (run E-20261124-214913-5956891, job 5215) |
| II Figs. 3, 5, spectra | reproduced | confirmed; maxima 10-15 % apart (reference) | |
| II Fig. 6, K and shear spectra | reproduced; absent USR hierarchy in part | not redone | |
| II Fig. 7, spectral convergence | reproduced (four lattices, monotone; order 5-6 to 128^3; floor at the longest shells of 256^3, cause open) | convergence confirmed on three lattices; 256^3 not redone | |
| II Fig. 8, constraint convergence | in part (plateaus equal on 64^3-256^3, decay; levels lower) | records, entry maxima confirmed on three lattices; 256^3 not redone | |
| II Fig. 9, backreaction | in part (USR as the figure; SR level 2 unchanged after the last crossing; level 1 = scheme difference) | review of the code: runs stand; values confirmed at N = 7.19 | |
| II: start of USR | reproduced as the figure shows it (text one e-fold late) | confirmed | |
| II: power to order unity, linear agreement | reproduced | confirmed | |
| II: outliers of order ten | not reproduced (amplitude factor) | confirmed; II's own figure reaches about 18 | |
| II: Hamiltonian violation at next order | in part (second order; level 1-2 decades lower) | records confirmed | SR per cell at 256^3: RSF256, q0034 |
| II: flipped sign gives first order | in part (first order in both scenarios through the entry; level 100x lower than printed) | confirmed, including the level, on the first SR e-fold | |
| II: momentum constraint at last crossing | reproduced (second order above about 13 cells) | not redone | |
| II: backreaction below 1e-4 | in part (large scales yes; USR top shells no; SR at the bound) | values confirmed | |
| I Fig. 1, paths | reproduced (Ito, Euler background) | confirmed | |
| I Fig. 2, skewness, kurtosis | reproduced (skewness to about 10 %) | widths confirmed; skewness 1.12 vs 1.04 | |
| I Figs. 3, 4, distributions | reproduced (Ito) | confirmed | |
| I: slope reached near 3.04 | reproduced only with Euler at 0.01 | confirmed (closed-form plateau stop) | |
| I: Stratonovich evolver | not matched (figures follow Ito) | confirmed (Stratonovich widths 15-19 % off) | |
| I: Ito term alpha^3 | corrected to alpha^5 | confirmed (derivation, Monte Carlo) | |
| I: amplitude valid in SR and USR | USR smaller by sigma^2/3; SR 1 + about 5 eps1 | USR confirmed; SR 1.06, 1.12 on its backgrounds | |
| I: noise off, alpha^3 -> 1, tails | reproduced; e-fold tails in part | left skew confirmed (one seed); tails not redone | |

Ledger: 121 rows in 10 tables, each with the verifier's verdict and the line of VERIFIER.md
(61 yes, 15 differs, 2 beyond reach, 11 quote, 14 rerun only, 18 none: 1 pending, 1 row added
after the check, 16 rows from the continued runs, which ended after the check); `ledger.py`
stops if a verifier string is not on its line.

## What is in this directory

| Path | Content |
|---|---|
| `WRITING_GUIDE.md`, `NOTATION.md` | per-paper layer of the skill: readers, outline, numbers, dictionary, project names (the forbid list), exceptions (ledger with run ids; which code each run used) |
| `notes/2026-11-24-story.md` | skill 10.1: story, 300- and 1000-word versions, self-review in place of parallel reviewers |
| `manuscript/main.tex`, `references.bib`, `main.pdf` | the note (I intro; II sources; III lattice; IV one patch; V discussion; VI summary; App. A misprints, B parameters, C set-up, D verdicts with check column, E ledger in 10 tables) |
| `manuscript/figures/` | 19 figures; PDFs of `fig_specconv`, `fig_constraints`, `fig_ablation`, `fig_signflip` from R6 (E-20261124-215017-cb16c27), the other 15 from R2 (E-20261124-180038-4d4651a); R7 reproduces every PNG of R6 byte for byte, and R3-R6 those of R2 for the 15 |
| `manuscript/tables/ledger.tex`, `ledger.csv`, `ledger_checks.json` | the ledger with the check column, from R7 (E-20261124-215650-1de1ba5), sha256 checked against its `sha256sums.txt` |
| `manuscript/scripts/` | figure scripts (copies of repro/figs/figures with neutral titles, and of repro/langevin), `ledger.py` (rows, section definitions, verifier checks, per-row sources), `run_all.py`, `schem_pipeline.py`, `figstyle.py`, `paperfig.py` |

## Registered runs of this package

| Run | What |
|---|---|
| E-20261124-174752-f387f2a | R1: first run_all (jsons byte-equal to figure run E-20261124-173254-420115f) |
| E-20261124-180038-4d4651a | R2: ablation legend, PENDING rows; source of 15 committed figure PDFs |
| E-20261124-185556-df39d1c | R3: correction pass, ledger with check column (8 tables; two ran off their pages) |
| E-20261124-185912-45510c2 | R4: ledger split into 10 tables |
| E-20261124-190054-08f916a | R5: last section renamed (guide dictionary) |
| E-20261124-215017-cb16c27 | R6: update pass with the four continued runs; source of 4 committed figure PDFs (three ledger tables ran off their pages) |
| **E-20261124-215650-1de1ba5** | R7: ledger sources per row group; source of the committed tables |

All seven: production, two cores, one to one and a half minutes each, 0 card-hours; every
lattice json equal to the committed jsons of the figure package at the time (`checks.json` of
each); langevin.json equal throughout.

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
a layout test with a short run label underestimates the row heights (JOURNAL entry 11).
`run_all.py` passes make_figs.py the arguments of repro/figs' figure run E-20261124-213739-9776185
(`--cl256s`, `--al2s` from pass E-20261124-213029-e937f69); the joined records of the continued
runs come through `runs.py` (JOINED, join check E-20261124-212343-7e9c4b2). When the scripts of
repro/figs/figures change, copy them and keep the note's neutral titles (`make_figs.py`,
`fig_signflip.py`, `fig1_meanrolls.py`, `fig_ablation.py`; `figlib.py` keeps its own path depth).

When RSF256 (q0034, run E-20261124-214913-5956891) has ended: repro/continue joins it and repro/figs
runs `runs.py rsf256` and a figure run with `--rsf256 <pass>` (repro/figs RESULTS.md section 5).
Then here: add `--rsf256 <pass>` to `LATTICE_ARGS`, switch FIGS "fig_contrast_sr" to the RSF256
contrast figure if repro/figs makes it the SR figure, replace the PENDING row of `ledger.py`
(Constraints, SR per-cell rows) by value rows (check "none"), rerun, and replace the two
`\pending{...}` markers of `main.tex` (Table IV rows "Figs. 2 and 4" and "Hamiltonian violation")
and the last sentence of the contrasts caption and of the abstract.

## Checker and pages, last run on the committed text

Compile: 24 pages, no undefined references or citations, no overfull boxes. Checker with the
forbid list: remaining hits accepted under the guide: 5.1 (two: the verdict label "not
reproduced"), 7.6 (one: "no defect" about the reviewed code, exception 2), 7.5 and 7.7 only in
`tables/ledger.tex` and `scripts/` (exception 1), 9.3 in `scripts/` (`figstyle.py` turns frames
off). Every page read at 75 dpi (JOURNAL entries 10-11): pages 1-24 of the R6 build, pages 15-23
of the R7 build (pages 1-14 and 24 pixel-identical to the R6 build). Every ledger table ends with
its bottom rule on its page.

## What is still open

- PENDING: RSF256 (SR 256^3 with dumps; queue q0034, dispatched as run
  E-20261124-214913-5956891, Slurm job 5215, not waited for): the SR constraint rows of the
  one-point figure and the SR per-cell part of "Hamiltonian violation at the next order".
- Not established: the cause of the floor of the spectral convergence at the longest shells of
  256^3 (candidate: second order of the field; a run at half the noise amplitude would test it,
  repro/figs request, about 0.5 card-hours); the cause of the amplitude factor (only the authors'
  normalisation of the real-space draw can settle it); the 7 per cent difference of the Ito
  skewness between two implementations (1.04 against 1.116 +- 0.012); the half-loss time on the
  converged background (4.80 ours, 5.36-5.38 independent, different loss criteria).
- Not redone by the independent check: every row from the continued runs (256^3 rungs, SR level
  2 at N_f, SR sign flip beyond its first e-fold), extrinsic-curvature spectra, momentum
  constraint against cells per wavelength, the gauge families, nine of the 17 misprints, the
  constraint field from the metric with an independent stencil, the tails of the one-patch
  distributions.
- Skill 10.1 step 4 (parallel reviewers) was not run: no subagent tool in these sessions.

## Requests

- repro/verify: (1) check the 16 ledger rows from the continued runs (column "none" except the
  pending row and the row added after the check): 256^3 rungs of Figs. 7 and 8 (joined records of
  E-20261124-212343-7e9c4b2, pass E-20261124-213029-e937f69), SR level 2 at N_f (same pass), SR
  sign flip to N = 4.39 (joined records). (2) Unchanged: VERIFIER.md section 2 reads P1:520's
  `\textpertenthousand` as per mille; with textcomp (P1 source line 43) it is per ten thousand,
  1e-4; please confirm or contest.
- Lead of E: SETUP_AUDIT item 4 still says N* + 8.04 for SR, the note uses 8.10 (request of
  repro/figs, unchanged); when q0034 ends, the steps under "How to rerun" for RSF256.
- core (minor, python/nrpic/figstyle.py): save PDFs without a creation date (or honour
  SOURCE_DATE_EPOCH), so reruns give byte-identical PDFs (unchanged request).
