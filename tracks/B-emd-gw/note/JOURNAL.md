# JOURNAL of note (helper package of B-emd-gw, wave 2)

Package: the working note v0 of Track B (REVTeX), its figures from registered runs, the two
schematics of the G0 stage check, the numerical ledger, a check of the numbers stated in the
lead's documents against the run outputs, and `stage/G0/STAGE_REPORT.md`. Predictions are
written before the run they concern; outcomes are appended below, also when a prediction
fails. Run ids are under `tracks/B-emd-gw/runs/`.

## Set-up (2026-11-15, before any run of this package)

Sources of every number of the note: the output directories of registered runs under
`/data/haiyangw/nrpic/scratch/B-emd-gw/<run_id>/`, checked against the sha256 the run recorded
(its `sha256sums.txt` or the manifest field `outputs_sha256`); wave-1 runs that recorded no
checksum are read as they are and listed so in the ledger, and for them the lead's re-check
L1 (run B-emd-gw-20261115-131016-03b1119) regenerated the same file bit for bit
(`stage/G0/REVIEW.md`), which the claims script tests where L1 holds a copy.

Runs the note reads (one per figure or table):
- periodic Z4c linear wave, convergence table: L1 export, regenerated
  `periodic_z4c/tables/lw_x.json` (B-emd-gw-20261115-131016-03b1119);
- diagnostics on AthenaK output: B-emd-gw-20261115-120128-7dfaa38 (`results_athenak.json`),
  analytic TT validation in L1 (`gw_tt/results_tt.json`);
- crossed-wave strain and plane-symmetric null: B-emd-gw-20261115-113148-4e5c33b;
- regime estimates (junk decay, virial frequency, cost): B-emd-gw-20261115-113632-2960145;
- symbolic checks: B-emd-gw-20261115-113102-bc5e082, lead checks B-emd-gw-20261115-131027-03b1119;
- pancake through shell crossing (analysis of the GR card runs -115217-69ab1db,
  -115902-a3207d7 and the Newtonian runs -115239-69ab1db, -122451-01801f6):
  B-emd-gw-20261115-123852-ea4475c;
- FLRW background: B-emd-gw-20261115-115414-7ffbde1;
- semi-analytic baseline T1-T8: B-emd-gw-20261115-115752-840e994.

## Predictions (written before the first run of the note scripts)

N1 (figures and ledger from registered outputs). Every data-figure script and `ledger.py`
runs to the end reading only the files above; every file with a recorded checksum matches
it. Refuted by a checksum mismatch or by a script that needs a file outside a registered
run directory.

N2 (agreement with the committed package results). Each file read from a run directory is
byte-identical to the copy committed in the helper package (`*/results/*.json`,
`periodic_z4c/tables/lw_x.json`), because L1 found every leaf bit-identical. Refuted by any
differing byte (other than the figure paths and wall times L1 named for
`baseline_results.json`).

N3 (claims of the lead's documents). Of the numbers stated in `stage/G0/REPORT.md`,
`stage/G1/STATUS.md` and `STATUS.md` that the claims script checks (about 40), all agree
with the files at the precision they are stated, except at most a few wordings that
round or drop a qualifier (one already seen while reading: G1/STATUS.md says the
linear-wave errors match the Fourier-symbol prediction "to 1 % up to 64 cells", while
`periodic_z4c/README.md` and `tables/lw_x.json` give 9.5 percent for the production phase
error at 64 cells). Refuted if more than five checked numbers disagree beyond their stated
precision, or if any disagreement changes a conclusion of the G0 report.

N4 (the note compiles). `latexmk -pdf` on `main.tex` gives no undefined reference or
citation; the paper-writing checker reports no hit in the main text outside the accepted
ledger exception of the writing guide. Refuted by an undefined reference, a figure caption
longer than five lines on the rendered page, or a project name in the main text.

N5 (figures). Each figure shows what `WRITING_GUIDE.md` (Figures) says the reader should
see; I look at every PNG with Read before citing it. Refuted, for example, if the pancake
departures at the two box sizes do not collapse onto each other after division by the
ratio of their (H/k)^2 at a = 10.

## Development runs (not cited)

Before the registered runs the scripts were run into `scratch/B-emd-gw/tmp/note/` while
the figures and the LaTeX were drafted (figure labels, legend frames, caption length,
ledger split into two tables, a bibliography style that needs `@misc` for preprints). One
finding there changed the text before any registered run: the claims check shows that the
Hamiltonian-constraint numbers that `stage/G1/STATUS.md` quotes for a thousandfold
expansion are the values of the first record (t = 100 Mpc/h) of `cosmo/analysis/daverio_a.json`.

## Registered runs

- B-20261115-165138-cb53c14 (nrpic-run, 1 core, 8 s): first full run; superseded because the
  first-source helper published the outcome of its late-rise analysis (run
  B-20261115-164616-a6d9477, commit 9719b17) while this package was being written, and the
  note's text on that rise had to follow it.
- B-20261115-165231-9e29328 (nrpic-run, 1 core): second full run, superseded by the next (nrpic-stage verify flagged the y label of fig_baseline cut at the figure edge; margin widened, commit 91026b8). `note/figures/` and
  `note/tables/` are copies of its `figures/` and `tables/`. A first submit at 16:51Z was
  refused (16 cores busy in other helpers' local runs, decision 0006); retried a minute later.

## Outcomes of N1-N5 (2026-11-15T17:00Z)

N1: HOLDS. Every script ran to exit 0 reading only registered run directories (14 files
from 13 runs, `tables/checked.md`); the 7 files whose runs recorded checksums match them;
7 files of wave-1 runs that recorded none were read as they are. Beyond N1 as written, the
claims check also reads the lead's stage documents (to locate the stated numbers) and one
committed file of the cosmology extension, `cosmo/analysis/daverio_a.json`.

N2: HOLDS. All 9 run outputs that have a committed copy in a helper package are
byte-identical to it (`tables/checked.md`).

N3: HOLDS (4 of 28 differ, none changes a G0 conclusion). `tables/claims.md`:
1. `stage/G0/REPORT.md:88`: "lapse = scale factor to 1e-7 at a = 4 and 36"; the files give
   1.9e-7 at a = 4 and 7.0e-8 at a = 36 (order of magnitude only).
2. `stage/G1/STATUS.md:22`: errors "matching the Fourier symbol of the scheme to 1 % up to
   64 cells"; the production phase error at 64 cells departs by 9.5 % (the package README
   says so; the others are within 1 %).
3. `stage/G1/STATUS.md:56`: "Hamiltonian constraint 1.6e-9, 1.1e-10, 3.2e-11 at 8, 16, 32
   cells over a thousandfold expansion"; these are the values at t = 100 Mpc/h, the first
   record; at t = 3000 Mpc/h (end) the values are 3.1e-8, 2.5e-9, 3.0e-9 and do not fall
   from 16 to 32 cells. The fourth-order convergence holds for the error of chi.
4. `stage/G1/STATUS.md:47`: the Newtonian mode and its quadrupole history "exist on
   `core/newton` (tip ce329f5, not on main)"; since the merge of release core-v0.3 they are
   on main (`coord/INTERFACES/newtonian_mode.md`, CLAUDE.md).
Two wordings agree in number but not in words: `REPORT.md:50` calls the box means of the
constraints (1.3e-3, 0.21 at a = 15) "pancake void" values (the dumps place most of the
violation in the void, but the numbers are box means); `REPORT.md:91` "plane symmetry to
1e-12" (largest transverse velocity 1.25e-12).
New since the G0 report, from another helper: the late TT rise in the wave-1 cosmology
dumps, flagged in REVIEW.md as a possible second-order gauge piece, is not that piece
(run B-20261115-164616-a6d9477, `first_source/JOURNAL.md` lines 158-193); the note follows
it. OPEN.md item 9 and RISKS.md R4 still carry the old reading (lead's files).

N4: HOLDS. `latexmk -pdf`: 0 undefined references and citations, 0 overfull hboxes (one
overfull vbox of 7 pt in the output routine, ledger page). Checker (paper-writing
`check_manuscript.py --compile` with the guide's forbid list): every principle clean in the
main text; the remaining hits are run ids and file names in the ledger appendix, its
generated tables and the scripts (exception 1 of WRITING_GUIDE.md). All ten pages read at
90 dpi: every caption within five lines, figures legible, ledger tables fit the page.

N5: HOLDS. Figures looked at (Read): fig_source, fig_waves, fig_pancake, fig_baseline,
schem_architecture, schem_timeline. In fig_pancake (a) the four-Hubble-radii curve divided by
16 lies on the one-Hubble-radius curves from a = 5 on (16.1 at a = 10); at a = 2 it lies
lower by a factor of two, the early transient the verify_cosmo journal reports (P2).

Not done: step 4 of the paper-writing procedure for a new paper (reviewer subagents with
the 1000-word version; no subagent tool in this session); `nrpic-stage verify` (see below).

## Registered run used by the note (17:00Z)

B-20261115-165556-a399d4e (nrpic-run, 1 core; one refusal for busy cores before it): the run
the note uses; `note/figures/` and `note/tables/` are copies of its outputs. Numbers and the
claims check are those of the previous run (only the margin of one figure changed).
