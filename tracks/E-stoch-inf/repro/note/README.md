# repro/note: working note on the reproduction of arXiv:2401.08530 and arXiv:2512.14649

Package of Track E (decision 0028, batch R2b). The working note on the reproduction of both
papers, written with the paper-writing skill: `manuscript/main.pdf` (23 pages, REVTeX, PRD
style). Predictions and outcomes: `JOURNAL.md` (entries 1-4 first draft, 5-8 correction pass
after the verifier). State: 2026-11-24 11:05 PST, after the correction pass.

Paper I = arXiv:2401.08530 (one patch), Paper II = arXiv:2512.14649 (lattice). Independent
check = package repro/verify, `tracks/E-stoch-inf/repro/verify/VERIFIER.md` (commit 0de2198a),
an agent that produced none of the runs and was given the raw outputs and the claims, not the
conclusions.

## What the note claims

1. Equations: computer algebra confirms that the stochastic sources are gauge independent and
   leave the constraints unsourced at linear order; 17 misprints, none of which enters a code
   (8 of them rederived by the independent check: items 1, 3, 6, 7, 8, 10, 14, 15).
2. Lattice (Paper II): everything linear theory fixes is reproduced with an independent code
   (AthenaK Z4c with the stochastic sources): background, spectra and freezing, extrinsic
   curvature through the crossings, spectral convergence (close to sixth order: factors 52 and 62
   per doubling; 43 and 34 with the verifier's own linear reference), second-order constraint
   plateaus and the first-order rise under a flipped source.
3. The one-point bands of Paper II are 3.5 (SR) to 4 (USR) times wider than ours while its
   spectra agree with ours; for a Gaussian field the spectrum fixes the band, so the factor lies in
   the published real-space normalisation or plotting (the "amplitude factor"; cause open). The
   independent check found the same factor from its own reading of the published figures.
4. Constraint levels are one to two decades below Paper II's (most of it the square of the
   amplitude factor); the flipped-sign level is about 1e-7, a hundred times below the printed
   1e-5, while the jump flipped/proper is within a decade of the published one.
5. Backreaction: Paper II's bound (per ten thousand, P1:520 `\textpertenthousand`) holds at
   large scales, fails at the USR top shells (as Paper II's own figure shows), and the SR
   comparison at N = 7.19 sits at the bound (below it on shells with more than ten modes,
   1.4 times above with every shell). Level 1 against 0 is a difference of two time integrations
   of one background (core's review: runs stand).
6. One patch (Paper I): the published figures follow from a background integrated by forward
   Euler at 0.01 e-folds (the converged background stops on the plateau, closed form) and from the
   Ito reading of the printed equation; widths to 1-2 per cent, skewness to about ten per cent
   (1.04 ours, 1.12 independent, about 1.1 published). The Ito term carries alpha^5, not alpha^3;
   the USR noise amplitude is smaller than printed by sigma^2/3; the SR ratio exceeds one by
   about 5 eps1 at the crossing.

## Verdicts per figure and statement (Table IV of the note)

| Item | Verdict | Independent check | Pending run |
|---|---|---|---|
| II Fig. 1, background | reproduced | confirmed (two eps2 maxima beyond its reach) | |
| II Figs. 2, 4, one-point statistics | in part (shape, timing yes; amplitude no) | confirmed, factor 3.5 / 4, cause open | SR constraint rows: E-20261124-130529-da8c917 |
| II Figs. 3, 5, spectra | reproduced | confirmed; maxima 10-15 % apart (reference) | |
| II Fig. 6, K and shear spectra | reproduced; absent USR hierarchy in part | not redone | |
| II Fig. 7, spectral convergence | in part (three lattices; order 5-6) | convergence confirmed; rungs within 2.3 | 256^3 rung: E-20261124-130952-4be980b |
| II Fig. 8, constraint convergence | in part (plateaus, decay; levels lower) | records, entry maxima confirmed; field not recomputed | 256^3 rungs: E-20261124-130952-4be980b, E-20261124-130711-a5dec67 |
| II Fig. 9, backreaction | in part (USR as the figure; level 1 = scheme difference) | review of the code: runs stand; values confirmed | SR level 2 at N_f: E-20261124-131359-49afe29 |
| II: start of USR | reproduced as the figure shows it (text one e-fold late) | confirmed | |
| II: power to order unity, linear agreement | reproduced | confirmed | |
| II: outliers of order ten | not reproduced (amplitude factor) | confirmed; II's own figure reaches about 18 | |
| II: Hamiltonian violation at next order | in part (second order; level 1-2 decades lower) | records confirmed | |
| II: flipped sign gives first order | in part (USR first order; level 100x lower than printed) | confirmed, including the level | SR beyond 0.71 e-folds: E-20261124-130629-61fe0b0 |
| II: momentum constraint at last crossing | reproduced (second order above about 13 cells) | not redone | |
| II: backreaction below 1e-4 | in part (large scales yes; USR top shells no; SR at the bound) | values confirmed | SR at N_f: E-20261124-131359-49afe29 |
| I Fig. 1, paths | reproduced (Ito, Euler background) | confirmed | |
| I Fig. 2, skewness, kurtosis | reproduced (skewness to about 10 %) | widths confirmed; skewness 1.12 vs 1.04 | |
| I Figs. 3, 4, distributions | reproduced (Ito) | confirmed | |
| I: slope reached near 3.04 | reproduced only with Euler at 0.01 | confirmed (closed-form plateau stop) | |
| I: Stratonovich evolver | not matched (figures follow Ito) | confirmed (Stratonovich widths 15-19 % off) | |
| I: Ito term alpha^3 | corrected to alpha^5 | confirmed (derivation, Monte Carlo) | |
| I: amplitude valid in SR and USR | USR smaller by sigma^2/3; SR 1 + about 5 eps1 | USR confirmed; SR 1.06, 1.12 on its backgrounds | |
| I: noise off, alpha^3 -> 1, tails | reproduced; e-fold tails in part | left skew confirmed (one seed); tails not redone | |

Ledger: 113 rows in 10 tables, each with the verifier's verdict and the line of VERIFIER.md
(65 yes, 16 differs, 2 beyond reach, 11 quote, 14 rerun only, 5 none: 4 pending, 1 row added
after the check); `ledger.py` stops if a verifier string is not on its line.

## What is in this directory

| Path | Content |
|---|---|
| `WRITING_GUIDE.md`, `NOTATION.md` | per-paper layer of the skill: readers, outline, numbers, dictionary, project names (the forbid list), exceptions (ledger with run ids; which code each run used) |
| `notes/2026-11-24-story.md` | skill 10.1: story, 300- and 1000-word versions, self-review in place of parallel reviewers |
| `manuscript/main.tex`, `references.bib`, `main.pdf` | the note (I intro; II sources; III lattice; IV one patch; V discussion; VI summary; App. A misprints, B parameters, C set-up, D verdicts with check column, E ledger in 10 tables) |
| `manuscript/figures/` | 19 figures; PDFs from run E-20261124-180038-4d4651a (R2); runs R3-R5 reproduce every PNG byte for byte, so the PDFs were not replaced (their metadata alone would change) |
| `manuscript/tables/ledger.tex`, `ledger.csv`, `ledger_checks.json` | the ledger with the check column, from run E-20261124-190054-08f916a (R5), sha256 checked against its `sha256sums.txt` |
| `manuscript/scripts/` | figure scripts (copies of repro/figs and repro/langevin), `ledger.py` (rows, section definitions, verifier checks), `run_all.py`, `schem_pipeline.py`, `figstyle.py`, `paperfig.py` |

## Registered runs of this package

| Run | What |
|---|---|
| E-20261124-174752-f387f2a | R1: first run_all (jsons byte-equal to figure run E-20261124-173254-420115f) |
| E-20261124-180038-4d4651a | R2: ablation legend, PENDING rows; source of the committed figure PDFs |
| E-20261124-185556-df39d1c | R3: correction pass, ledger with check column (8 tables; two ran off their pages) |
| E-20261124-185912-45510c2 | R4: ledger split into 10 tables |
| **E-20261124-190054-08f916a** | R5: last section renamed (guide dictionary); source of the committed tables |

All five: production, two cores, about one minute each, 0 card-hours; every lattice json and
langevin.json byte-equal across R1-R5 (`checks.json` of each).

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

The checker does not see a float taller than its page: read every rendered page (pdftoppm -r 75).
When the continuations of repro/continue have ended: run the passes of repro/figs (RESULTS.md
section 5), add their run directories to `LATTICE_ARGS` in `run_all.py`, replace the PENDING rows
of `ledger.py` by value rows (the verifier column "none" until a check exists), rerun, and replace
the `\pending{...}` markers of `main.tex` (eight, all named in the table above).

## Checker and pages, last run on the committed text

Compile: 23 pages, no undefined references or citations, no overfull boxes. Checker with the
forbid list: remaining hits accepted under the guide: 5.1 (two: the verdict label "not
reproduced"), 7.6 (one: "no defect" about the reviewed code, exception 2), 7.5 and 7.7 only in
`tables/ledger.tex` and `scripts/` (exception 1), 9.3 in `scripts/` (`figstyle.py` turns frames
off). Every page read at 75 dpi (JOURNAL entries 6-8): pages 1-11 pixel-identical to the R3
build read in full, pages 12-23 read on the R5 build.

## What is still open

- PENDING (five continued runs of repro/continue, queued behind another user's job, not waited
  for): see the last column of the verdict table. The ablation figure is unchanged: the SR
  level-2 run at N_f does not exist yet (E-20261124-131359-49afe29).
- Not redone by the independent check: extrinsic-curvature spectra, momentum constraint against
  cells per wavelength, the gauge families, nine of the 17 misprints, the constraint field from
  the metric with an independent stencil, the tails of the one-patch distributions.
- Not resolved: the cause of the amplitude factor (only the authors' normalisation of the
  real-space draw can settle it); the 7 per cent difference of the Ito skewness between two
  implementations of the same equations (1.04 against 1.116 +- 0.012); the half-loss time on the
  converged background (4.80 ours, 5.36-5.38 independent, different loss criteria).
- Skill 10.1 step 4 (parallel reviewers) was not run: no subagent tool in these sessions.

## Requests

- repro/verify: VERIFIER.md section 2 ("All below P1:520's 1 per mille") reads
  `\textpertenthousand` as per mille; with textcomp (P1 source line 43) it is per ten thousand,
  1e-4. Under that reading your USR top-shell value (9.2e-4) and your SR value at N = 7.19
  (1.4e-4) exceed the bound; the note uses this reading. Please confirm or contest. Also your
  "overlap only N < 0.39" for the SR flipped run: our records give common records to N = 0.71
  (ledger, sign-flip table); please say which records you read.
- Lead of E: when the continuations end, the update under "How to rerun"; SETUP_AUDIT item 4 still
  says N* + 8.04 for SR, the note uses 8.10 (request of repro/figs, unchanged).
- core (minor, python/nrpic/figstyle.py): save PDFs without a creation date (or honour
  SOURCE_DATE_EPOCH), so reruns give byte-identical PDFs (unchanged request).
