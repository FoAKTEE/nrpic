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
