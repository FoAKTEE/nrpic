# note: working note of Track E (gates G0 and G1)

> Pointer (batch 15, 2026-11-24): the G2 sections of the track (the ultra-slow-roll case against
> the criteria fixed in SCOPE 4c, its one failure on record, the fresh verifier, the G2
> schematics) are in the reproduction note `../repro/note/manuscript/main.pdf` (Sec. IV,
> Appendix F, ledger Table XVI), by decision 0035 item 1. This note stays at its G1 state.

Helper package of E-stoch-inf. Wave 2 (2026-11-15) wrote note v0 for gate G0 (feasibility);
wave 3 (started 2026-11-20, cut by the usage limit, finished in batch 2b on 2026-11-21) added
the G1 products of the checklist: C8 updated architecture schematic, C9 data-flow diagram,
C13 one script per G1 data figure from registered outputs, C14 schematics in the paper
style, C15 the G1 sections of the note with the checker passing with `--compile`. The note
is now v1 (16 pages). Predictions and outcomes: `JOURNAL.md`. Guide and notation
(paper-writing skill, one level above the manuscript): `../WRITING_GUIDE.md`,
`../NOTATION.md`.

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, two columns, 16 pages): Secs. I-V G0 (specification, set-up, references, noise validation, cost and the G0 decision); Secs. VI-VIII G1 (slow-roll reproduction: runs, A1, A2, A3, A6; constraints: record, odd/even split, strict A4 failed on record, A4' as ruled, core's explanation; validation of the analysis, reproducibility A7, cost); IX what is open (with red `\pending{}` markers); X summary; appendices: parameters, errata, ledger |
| `figures/fig_background`, `fig_freezing`, `fig_deltan`, `fig_noise`, `fig_cost` `.{pdf,png}` | G0 data figures (`fig_background`: right panel's tick label no longer cut) |
| `figures/fig_sr_modes.{pdf,png}` | G1 (a) per-mode A2 deviation against k/k_sigma* at N_f for L32-L256 and P256, and the largest D_n inside the window against N |
| `figures/fig_sr_freezing.{pdf,png}` | G1 (b) A3 freezing in P256: power ratio, per-mode ratio and drift; NR against the full MS and the FLRW lattice |
| `figures/fig_sr_constraints.{pdf,png}` | G1 (c) odd and even parts of H against e-folds for N = 32-256 (paper set-up), ln(N/8) ticks, floor model; halving factors |
| `figures/fig_sr_order.{pdf,png}` | G1 (d) A6 temporal order at 32^3 (three Courant factors) |
| `figures/schem_architecture.{png,svg}` | C8: four states (core-v0.3; core-v0.4/v0.5; track analysis; new or under way) |
| `figures/schem_dataflow.{png,svg}` | C9: mode tables -> AthenaK run -> analysis -> ledger and note |
| `figures/schem_timeline.{png,svg}` | stage timeline after decisions 0013/0017/0021 (G0 passed, G1 not yet met) |
| `tables/ledger.tex` | ledger of the G0 sections (Table III, runs R1-R8) |
| `tables/ledger_g1.tex`, `tables/ledger_g1.md` | ledger of the G1 sections (Tables IV and V, runs R9-R18, V = verifier, L = lead's check, C = core); the `.md` has every row with its evidence label and full locator |
| `tables/parameters.tex` | Table I |
| `tables/claims.md`, `tables/claims.json` | 104 numbers printed in the track's documents (G0: SPEC, SCOPE, G0 EVIDENCE, langevin README; G1: `stage/G1/STATUS.md`, `ladder/README.md`) recomputed from run outputs; 97 agree, 7 differ (list below) |
| `scripts/common.py` | the runs the note reads; every input checked against the sha256 its manifest (or the run's `sha256sums.txt`) records; `committed()` checks the committed copies under `ladder/results/` against the run that wrote them |
| `scripts/fig_*.py`, `scripts/schem_*.py` | one script per figure; the headers name the runs and files read |
| `scripts/ledger.py` | both ledgers, the parameter table and the claims check; also checks that each number quoted from a report (core's `coord/INTERFACES/scalar_field_3.md` 143-164, `stage/G1/VERIFIER.md` 303/332/374, `stage/G1/STATUS.md` 30, `stage/REVIEW-wave3.md` 111) stands on its line, and stops otherwise |
| `scripts/costmodel.py` | the G0 cost model with core's measured throughput |
| `scripts/run_all.py` | runs every figure script and `ledger.py` into one directory and repeats each figure (pixel identity) |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` (sha256 equal to `harness/style/SHA256SUMS`) |

Inputs of the G1 figures and ledger (each checksum-verified): the ladder's final analysis
E-20261115-194633-9e04ed8 (committed `ladder/results/final/*.json`; per-mode arrays
`res/{P256,L32p,L64p,L128p,L256p}.npz` and `res/P256_judge_a3.npz` read from its run
directory by absolute path, because the JSON hold only maxima), the floor analysis
E-20261119-142713-32c883a (`ladder/results/floor/floor.json`), the A6 analysis
E-20261119-145230-ff0dff2 (`ladder/results/a6/a6.json`, `a6_modes.npz` from the run
directory), the MS reference E-stoch-inf-20261115-122806-ef0d039 (`quadratic.npz`), the
analysis package's runs and validations (R13-R18) and the card run E-20261115-172618-f948386
(cost from its manifest).

## Registered runs of this package

G0 (2026-11-15): E-20261115-172421-50ac4ce (failed: scratch root), -172442-78cf53e,
-173135-858482f, -173402-641b6e2 (superseded), -173904-3be0405 (completed; G0 outputs).

G1 (2026-11-21, two cores, about 100 s each):
- E-20261121-075717-1849987: completed; superseded (the noise amplitude was still called s,
  which collides with the window steepness s of the note).
- E-20261121-080526-7fbe919: completed; superseded (the one-float G1 ledger table was 225 pt
  taller than a page).
- **E-20261121-080840-6112292**: completed; its outputs are the committed `figures/` and
  `tables/` (every file's sha256 is in its `sha256sums.txt`; checked after copying).

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`):

    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/note --kind scouting --gate G1 \
        --launcher local --cores 2 --purpose "note: figures, schematics, ledger" -- \
        bash -c 'export OMP_NUM_THREADS=2 && python3 tracks/E-stoch-inf/note/scripts/run_all.py --out "$NRPIC_RUN_DIR"'
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/E-stoch-inf/note
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'nrpic-run|nrpic-stage|SCOPE\.md|SPEC\.md|EVIDENCE|langevin/|codebase/|wt/|scratch/'
    latexmk -c

Each figure script also runs alone from `scripts/` (`python fig_sr_modes.py`, output to
`figures/`), which is what `harness/bin/nrpic-stage verify` does; `fig_sr_modes.py` and
`fig_sr_freezing.py` read the 447 MB array of P256 and take 20-30 s each. The scripts read absolute paths under
`/data/haiyangw/nrpic/scratch/` (override: `NOTE_SCRATCH_ROOT`).

## State (2026-11-21)

Done: the four schematics/figure groups of the task, each looked at (Read of the PNG, also
after every change); the G1 sections (VI-VIII), a rewritten "What is open" and summary, the
abstract and introduction updated; both ledgers from one registered run; checker with
`--compile`: 0 undefined references or citations, 0 overfull boxes, no float too large,
captions within five lines (checked on the pages); all 16 pages of `main.pdf` read.

Remaining checker candidates, accepted under exception 1 of `../WRITING_GUIDE.md`: the run
ids of the ledger tables (5.5) and the names of the track's documents in the docstrings and
comments of the scripts (5.8; the exception names `ledger.py`, `common.py`, `costmodel.py`;
the same kind of provenance lines stand in the schematic docstrings and two comments of G0
figure scripts; see Requests 2).

Choices [JUDGEMENT]:
- The task text said not to use the outputs of the other packages of the round (g1verify,
  a4res, ladder, usr, window) because they were in progress. g1verify and the ladder's wave-3
  items finished and were reviewed by the lead of batch 2a, so the note quotes a few of their
  numbers through document locators (ledger rows V, L) and the time-matched odd/even maxima;
  a4res, usr and window (still open) are red `\pending{}` markers in Secs. VII C and IX.
- Decision 0021 item 1 took A4' after the task text was written; the note states A4' as
  ruled, the strict A4 as failed on record, and that the operational floor (A4', A5) was
  defined after the data were seen.
- Core's explanation of the first-order part is quoted from the released
  `coord/INTERFACES/scalar_field_3.md` (core-v0.5), still [TO VERIFY] by the track (package
  a4res); in the text: "The explanation awaits an independent check by the track."
- The noise amplitude scale (the ladder's s, the code's `noise_mode_scale`) is lambda in the
  note.
- Odd/even maxima: from `results/final/pair_*.json` restricted to t <= 4.5 (dumps where both
  runs of a pair share the time); equal to `results/final2/` (745, 655, 869, 25).

Not done: the paper-writing reviewers of step 4 (they apply to a new paper; this note is an
existing draft); the verifier's recomputation of the G1 ledger (C16, for the lead to
commission); the release card-build check, a4res, usr and window results (other packages).

## Disagreements between the track's documents and the files (the files win)

G0 (2026-11-15; unchanged, `tables/claims.md` c16-c19, c21): items 1-6 of the v0 README
(assumed field/source overhead 15 and 30 percent against 65 measured; the cost per
realisation that follows; USR eps1(N*) last digit; a section pointer of SPEC 7; the code
state described in SCOPE 6; the key name of 1308.4754).

G1 (2026-11-21):
7. `ladder/README.md:15` (row A1) quotes "box means within 1.1e-12 (phi), 8.6e-12 (Pi),
   2.0e-12 (K)"; the final summary gives 2.0e-12 (phi, P256) and 3.6e-12 (K, L32p) (claims
   g22, g23; the verifier's disagreement 4; `stage/G1/STATUS.md` already quotes the right
   values). Immaterial against the threshold 1e-4.
8. `ladder/results/final/summary.json` A4 `max_odd_over_even_H` of N256 is 385 (dumps paired
   0.0038 apart in time); the note uses 25 (time-matched, as `results/final2/` and STATUS).

## Requests

To the lead of E-stoch-inf:
1. `../NOTATION.md`, proposed additions (symbols): `lambda` = amplitude scale of the noise
   (the code's `noise_mode_scale`, the ladder's s; +-1, +-1/2 in mirrored and halved pairs),
   Sec. VI A; `R^NR_n` = curvature perturbation of lattice mode n reconstructed from chi,
   gt_ij, phi; `R^lin_n = W_k R_k alpha_n` its linear reference; `D_n`, `Q_n` (Eq. 8);
   `H_odd`, `H_even` (Eq. 9, also for M_i); `q_a`, `kappa_a`, `mu_a = kappa_a - q_a^2` (Eq. 10,
   symbols of the first and second difference); named results: "the decay law" (Eq. 5);
   preamble macro `\pending{}` (red marker for results of packages in progress); overlap
   kept on purpose: none new (s stays the steepness; the amplitude is lambda).
2. `../WRITING_GUIDE.md`, proposed: allowed numbers add ln(N/8) (the e-folds after N* at
   which shells with fewer than eight cells per wavelength enter; the guide lists ln(N/4)),
   the lattice sizes 32^3-256^3, k_max = 8 dk and (N/4) dk, lambda = +-1, +-1/2, "four cells
   per wavelength", "sixty randomly chosen modes" (a figure parameter); outline: sections VI
   (slow-roll reproduction: runs and analysis; background and amplitude of every mode;
   freezing; order in time), VII (constraints: record; odd and even parts; criterion), VIII
   (validation, reproducibility, cost); exception 1 extended to the provenance lines of all
   figure and schematic scripts.
3. `ladder/README.md` row A1: correct the phi and K maxima (disagreement 7).
4. `stage/G1/CHECKLIST.md` evidence for C8, C9, C13, C14, C15: `note/figures/schem_architecture.png`,
   `schem_dataflow.png`, `fig_sr_{modes,freezing,constraints,order}.png` with their scripts,
   run E-20261121-080840-6112292, `note/main.pdf` (checker: 0 undefined, 0 overfull). For C16:
   the G1 ledger now exists (`note/tables/ledger_g1.md`, every row with source and label) for
   the verifier's recomputation.
5. When a4res, usr and window finish: replace the three `\pending{}` markers (Sec. VII C, IX),
   rerun `run_all.py` (registered) if a figure is added.

To orch, core, kb: none from this package.
