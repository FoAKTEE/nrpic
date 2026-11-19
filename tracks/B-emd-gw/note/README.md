# note: working note of Track B (v1, gate G1)

Helper package of B-emd-gw. Wave 2 (2026-11-15) wrote note v0 for gate G0; wave 2b
(2026-11-19, package note2) added the G1 products on paper: the first source in full
relativity against the second-order strain, the spatial-gauge check, the Newtonian mode of
the code, the G1 schematics (architecture classified by evidence, data flow) and an updated
timeline. The REVTeX working note of S2 (gravitational waves from structure formation in an
early matter era), its data figures and schematics, the numerical ledger, and a check of the
numbers of the lead's G0 stage documents against the run outputs. Predictions and outcomes:
`JOURNAL.md`. Guide and notation of the note (paper-writing skill, one level above the
manuscript): `../WRITING_GUIDE.md`, `../NOTATION.md` (the lead's files; additions for v1 are
requested below).

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, two columns, 17 pages) and its compiled pages |
| `figures/fig_*.{pdf,png}` | data figures, each made by `scripts/<same name>.py` from registered run outputs: `fig_source`, `fig_waves`, `fig_pancake`, `fig_baseline` (wave 1), `fig_scan`, `fig_gauge`, `fig_newton` (wave 2) |
| `figures/schem_*.{png,svg}` | schematics (`paperfig.py`): `schem_architecture` (G1: verified in a run / on a tested branch / to be written, evidence per box in the script's docstring), `schem_dataflow` (G1), `schem_timeline` |
| `tables/ledger.tex` | the ledger appendix (Tables II-V): every number of the note with its run id |
| `tables/parameters.tex` | the parameter table of the scenarios (Table I) |
| `tables/claims.md`, `tables/claims.json`, `tables/claims_summary.tex` | numbers of the lead's G0 stage documents (as of commit a399d4e) checked against the files; the sentence the note prints |
| `tables/checked.md` | every file the scripts read, its run, its checksum check, and whether it equals the copy committed by its package |
| `scripts/common.py` | the run ids the note reads; checksum checks against `sha256sums.txt` or the manifest's `outputs_sha256`; `CLAIMS_REV` |
| `scripts/g1data.py` | the G1 reductions: per-dump diagnostics of the scan, own second-order reference s g(tau), departures, linearity, mesh comparison (cubic spline in tau), null, gauge differences, magnetic Weyl comparison, eps scaling |
| `scripts/run_all.py` | runs every `fig_*`, `schem_*` and `ledger.py` into one directory (the registered run) |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` |

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --launcher local --cores 1 \
        --package tracks/B-emd-gw/note --purpose "note v1: figures, schematics, ledger" -- \
        .venv/bin/python tracks/B-emd-gw/note/scripts/run_all.py
    # (local runs are finished by submit itself)
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/B-emd-gw/note && latexmk -pdf main.tex
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'gw_diag|gwdiag|periodic_z4c|verify_cosmo|first_source|make_east|nrpic_cosmo|z4c_linear_wave|athinput|pm\.py|nrpic-run|anta|A100|Slurm|newton_tests|fslib'

If `nrpic-run` refuses, `python scripts/run_all.py <dir>` writes the same outputs and a
`sha256sums.txt` into `<dir>` for a manifest written by hand. Each figure script also runs
alone (`python scripts/fig_scan.py --out DIR`), which is what `harness/bin/nrpic-stage verify`
does. The scripts read only registered run directories under `scratch/B-emd-gw/` (wave-1 and
wave-2 runs listed in `scripts/common.py`); the run takes about two minutes on one core.

## State (2026-11-19, wave 2b, package note2)

Done (each looked at or read):
- Registered run B-20261119-142957-ae8b4e2 (commit ae8b4e2, exit 0): all figures, schematics,
  ledger and parameter tables; `figures/` and `tables/` are copies of its outputs. It
  supersedes B-20261119-142525-2a55af7 (same figures byte for byte; ledger and parameter
  labels renamed after symbol collisions were found on the rendered pages).
- Note v1, 17 pages: new Sec. III B paragraph and equation (the spatial-gauge piece), III C
  (Newtonian mode, data flow), IV F (Newtonian mode of the code), IV G (second readings),
  V A-C (the first source before shell crossing, the spatial gauge, through shell crossing),
  VI (plan) and VII (summary) rewritten, abstract and introduction updated. latexmk: no
  undefined reference or citation, no overfull hbox; checker clean in the main text; every
  caption within five lines on the rendered page; all pages read.
- New figures: `fig_scan` (four panels), `fig_gauge` (three), `fig_newton` (two);
  schematics `schem_architecture` (G1), `schem_dataflow` (new), `schem_timeline` (state
  updated: G0 passed, now between G0 and G1).
- Ledger Tables IV and V: 46 rows of the wave-2 runs plus the second readings of the lead's
  review runs; the committed-copy check per run (14 of 14 identical).
- Predictions N6-N11 and outcomes in `JOURNAL.md`: N6, N7, N9, N10 hold; N8 partly refuted
  (the review's gauge numbers at a = 5 and 20 differ from the files; the files win); N11 holds
  except the page count.
- Post-hoc finding, labelled so: the departure from second order scales as 1 + eps^2 across the
  three ratios (ledger row `fs_scaled`), the pattern of the next order in the potential.

Not done:
- Step 4 of the paper-writing procedure for a new paper (reviewer subagents): this is an
  existing draft edited in place, so the procedure does not require it; no reviewer read v1.
- `WRITING_GUIDE.md` and `NOTATION.md` are outside this package's paths and were not edited
  (Requests 1-2).
- No independent verifier of the wave-2 G1 runs is part of this package (`stage/G1/OPEN.md`
  item 5); `nrpic-stage verify B-emd-gw G1` was not run by this package.
- The oblique and expanding-box waves (G1 criterion 1) are not in the note: their runs belong
  to another package of wave 2b and were not finished when this note was built.

## State at G0 (2026-11-15, 17:05Z)

Done: note v0 (`main.pdf`, 10 pages, REVTeX 4.2; checker clean in the main text, compiled
without undefined references or overfull boxes, every page read), four data figures and two
schematics (each looked at), ledger and parameter tables, the claims check (28 numbers and
statements of the lead's stage documents; 24 agree, 4 differ: `tables/claims.md`), the
checksum and committed-copy check of every file read (`tables/checked.md`), the G0 checklist
items of these products, `stage/G0/STAGE_REPORT.md` from `nrpic-stage report`.
Registered runs: B-20261115-165138-cb53c14, B-20261115-165231-9e29328 (both superseded, kept
on record), B-20261115-165556-a399d4e (the outputs the note uses).
`nrpic-stage verify` on the committed tip: the note's checks pass (export, note, PDF newer
than the sources, style copies, one script per figure, figures regenerated and compared);
it fails on the clean tree and the run manifests because of other helpers' work in flight
in the same worktree (`stage/G0/VERIFY_RESULTS.md`).
Not done: the reviewer subagents of step 4 of the paper-writing procedure for a new paper
(no subagent tool in this session); an independent verifier's recomputation of the ledger
(`stage/G0/VERIFIER_REPORT.md`, owed by the verifier helper, whose runs are in flight).

## Requests

To the lead of B-emd-gw (wave 2b):
1. `../WRITING_GUIDE.md` (outside this package): allowed numbers for v1 -- eps = 0.1, 0.3, 1
   and the meshes 64^3, 32^3 (figure parameters of `fig_scan`, `fig_gauge`); N = 16, 32, 64
   (Newtonian pancake) and 32, 64, 128 (ellipsoid); the exact factors a = 1 + 1/delta,
   (k Delta x)^2/12, 1 + eps^2; the slopes -2 and -1 of `fig_newton`; "seven-point"
   (structural). Figures table: rows for `fig_scan` (the strain follows s g over the first
   decade of expansion, the null stays at rounding, two meshes agree), `fig_gauge` (the
   computed piece reconciles two gauges; the magnetic Weyl part agrees where the strain does
   not), `fig_newton` (the error is the stencil's force excess; the crossing time converges
   at second order), `schem_dataflow`. Outline: Sec. IV F (the Newtonian mode of the code)
   and Sec. V (the first source in full relativity; subsections along "aspects of the
   strain": against the second-order formula, its spatial gauge, through shell crossing).
   Forbid list: add `newton_tests|fslib`.
2. `../NOTATION.md`: add c_+ (cosine part of the + amplitude at (k,k,0)), s = -(5/6) phi_x
   phi_y (now used in Sec. II B too; h_s is gone), x_T, xi, D_ki = d_i xi_k, J = 1 + D,
   h^R (TT plus homogeneous traceless part), h^L, G_tot ("the spatial-gauge piece", Eq. 8),
   F ("the force factor", Eq. 10), Delta x (mesh spacing; h stays the metric perturbation),
   alpha_e (deformation of the ellipsoid; alpha stays the lapse), t_k, M (mass only).
   Renames: h_s -> s; code coordinates x' -> x (prime is the conformal-time derivative);
   displacement gradient M -> D (M is the mass); residual metric A -> h^R (A is the
   linear-wave amplitude); mesh spacing h -> Delta x; deformation alpha -> alpha_e.
3. `stage/G1/OPEN.md` items 3 and 4 are delivered (schematics; G1 sections), item 9 in the
   note's text (the gauge piece is described and used; its adoption into `gw_diag` is the
   lead's); the G1 checklist can cite run B-20261119-142957-ae8b4e2 and `note/main.pdf`.
4. A test written in advance for the post-hoc (1 + eps^2) reading (JOURNAL, "Found while
   writing"), to be put into `first_source/JOURNAL.md` before the delta = 0.0025 runs are
   analysed (their initial data exist: run B-20261119-141249-2af0df8): at fixed a in 20-60
   the departure c_+/(s g) - 1 at delta = 0.0025 is 1/16 of that at delta = 0.01 (refuted
   outside 1/12-1/20), and divided by (1 + eps^2) it is the same for eps = 0.3 and 1 to 5
   percent.
5. `stage/REVIEW-wave2.md` quotes raw/corrected gauge differences at a = 5 and 20 (0.131,
   1.454; 0.005, 0.031 percent) that differ from the files (0.121, 1.468; 0.002, 0.030
   percent, helper summary and this package agree) and N3 constants from its own quadrature
   (0.0620684, 0.0772146) next to the helper's averaged values (0.0618, 0.0764) that the note
   prints; worth a line of erratum there.
6. Ask the first-source helper for the definition behind rho_GW/rho_bar = 3.5e-6 and 8.8e-9:
   (rho_kin + rho_grad)/rho_bar from the per-dump files gives 4.2e-6 and 1.2e-8 (JOURNAL).
7. When the oblique and expanding-box waves (package `waves`, runs in flight) and the
   round-2 scan (jitter, particle number, delta = 0.0025) finish, add their run ids to
   `scripts/common.py`, a subsection of Sec. IV A and of Sec. V, and rerun `run_all.py`.

To orch (repeat of wave 2, if still open):
8. `nrpic-stage verify` fails its `clean` and `runs` checks whenever another helper of the
   same owner has uncommitted files or runs in flight in the shared worktree (the case
   throughout this package); restricting both checks to the packages and finished runs named
   would let a helper verify its own package.

To core:
9. Release of `core/requests-b` (corrected oblique generator, double-precision mesh output,
   time label of Psi_4, thin boxes and jitter) into main, so the note can describe them as
   part of the code rather than of a tested branch.

To kb (repeat):
10. The key references of Track B as an indexed snapshot (G0 item C2); the note cites
    2212.00425 and 2312.12499 from their abstracts only.
