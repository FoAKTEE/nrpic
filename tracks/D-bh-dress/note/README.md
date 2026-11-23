# note_v2: working note v2 of Track D (after gate G1) and the second Kerr sampler seed

Moved on 2026-11-22 by the lead (batch 10a): this directory replaced `note/` (v1) with `git mv
note_v2 note`; v1 stays in the history (commit 38520eda and earlier). Paths below that name
`note_v2/` now read `note/`.

Helper package of D-bh-dress, batch 6 (2026-11-21 afternoon; processors only, 0 card-hours).
Two deliverables:

1. **Working note v2** (REVTeX, `main.tex`, `main.pdf`): note v1 (`../note/`) brought to the
   state after gate G1 (signed 2026-11-21 with reservations, `coord/GATES.md` line 20), with
   every change that `../stage/G1/GATE_REVIEW.md` sections 5-6 asks of the note, the first G2
   result ES-F, and the relaxed-lapse finding (decisions 0022 item 3, 0025 item 3). Guide and
   notation one level above: `../WRITING_GUIDE.md`, `../NOTATION.md` (unchanged).
2. **Second sampler seed of the Kerr spike stationarity test** (gate review section 5 item 3:
   inner-range deficits 3.1, 1.8, 0.9 per cent of seed 1), prediction first (`JOURNAL.md` N1),
   outcome in `JOURNAL.md` N3 and in the note (ledger part 10, `fig_kerr_seeds`).

Predictions and outcomes: `JOURNAL.md` (N0-N4). v1's history: `../note/JOURNAL.md`.

## Where v2 lives

The package may write only here, so v2 is a full copy of the note directory: `note_v2/` has
the same layout as `../note/` (scripts, figures, tables, main.tex). `../note/` is v1 and is
untouched. **Request to the lead**: replace `../note/` by this directory (or point the stage
package at it); `nrpic-stage verify` looks for `tracks/D-bh-dress/note/`.

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | note v2 (REVTeX 4.2, PRD two-column) and its compiled pages |
| `figures/fig_*.{pdf,png}`, `fig_*_numbers.json` | data figures, each from `scripts/<same name>.py` and registered run outputs |
| `figures/schem_*.{png,svg}` | architecture (post-G1 chain) and stage timeline (G0 and G1 passed), `paperfig.py` |
| `tables/ledger.tex` | ten ledger tables: every number of the note with its run id (parts 7-10 new) |
| `tables/parameters.tex` | parameter table (Q16 and ES-F added) |
| `tables/claims.{md,json}` | v1's check of the lead's documents against the run outputs (unchanged inputs) |
| `scripts/common.py` | run ids the note reads (new: q16, q16_ana, q16_lost, v1b, hor_cmp, lead_y1, gate_review, v1gb, es1g, esf_data, esf, esf_ana, esf_crit, kerr2_*, kerr_seeds) |
| `scripts/fig_esf.py` | new: ES-F growth against the removed energy, closure, M_AH over the exact LTB mass |
| `scripts/fig_q16.py` | new: Newtonian-mode infall to a/a_i = 16 against matched shells and the self-similar profile |
| `scripts/fig_kerr_seeds.py` | new: the two Kerr seeds, time-averaged deficits and running means |
| `scripts/ledger.py` | v1's ledger plus parts 7-10 and the parameter rows |
| `scripts/schem_*.py` | schematics updated to the post-G1 state |
| `kerr_seed2/compare_seeds.py` | the pre-registered seed comparison of N1 (figure `fig_kerr_seeds` of its run) |
| `JOURNAL.md` | predictions and outcomes N0-N4 |

## Runs of this package (manifests under `../runs/`, outputs under `scratch/D-bh-dress/<id>/`)

| Run | What |
|---|---|
| D-20261121-211717-7b6374b | Kerr initial data, seed 20261121 (48000 particles, 6 files), `spike/sample_kerr.py` |
| D-20261121-212016-7e090f9 | AthenaK release core-v0.3 processor build on analytic Kerr-Schild a = 0.8, 20000 M, 6 cores, 2355 s |
| D-20261121-215955-0fb4ea2 | stationarity analysis of seed 2 (`spike/analyze_kerr.py`, reference grid of seed 1) |
| D-20261121-220011-d0deb0b | pre-registered seed comparison (`kerr_seed2/compare_seeds.py`; `fig_kerr_seeds.png`) |
| D-20261121-220137-5123361 | the one seed-2 particle that crossed r_+ (`kerr_seed2/plunger.py`; `plunger.png`) |
| D-20261121-220728-a41c2f0 | **final note build** (`scripts/run_all.py`, 14 of 14 scripts); its `figures/`, `tables/` are the committed ones |
| D-20261121-220354-daadc10, -220513-c666211, -220624-879d83e | earlier note builds of this session, superseded (kept on record) |

## How to rerun (from the worktree root, worktree venv)

    # Kerr seed 2
    harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/D-bh-dress/note_v2 --cores 4 -- \
      bash -c 'cd tracks/D-bh-dress/spike && python sample_kerr.py --out "$NRPIC_RUN_DIR" --n 48000 --nfiles 6 --a 0.8 --ecut 0.99 --slice ks --seed 20261121'
    harness/bin/nrpic-run submit ... --cores 6 -- bash -c 'cd tracks/D-bh-dress/spike && python3 drive_runs.py --ic <IC> --out "$NRPIC_RUN_DIR" \
      --exe /data/haiyangw/nrpic/.work/build_cpu_v03/src/athena --athinput kerr_geodesic.athinput --files kerr_0.nrp ... kerr_5.nrp \
      -- time/tlim=20000 particles/snap_dt=100 particles/dt=0.05'          # 40 min on 6 cores
    harness/bin/nrpic-run submit ... -- bash -c "cd tracks/D-bh-dress/spike && python analyze_kerr.py --ic <IC> \
      --ref /data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-172646-ed6a510 --runs <RUN>/kerr_0 ... <RUN>/kerr_5 --out \"\$NRPIC_RUN_DIR\" --tag kerr_seed2"
    #   (analyze_kerr.py also copies its PNGs into spike/figs/: delete those copies, they belong to the run)
    harness/bin/nrpic-run submit ... -- python tracks/D-bh-dress/note_v2/kerr_seed2/compare_seeds.py \
      --a <seed-1 analysis json> --b <seed-2 analysis json> --out '$NRPIC_RUN_DIR'
    harness/bin/nrpic-run submit ... -- bash -c 'python tracks/D-bh-dress/note_v2/kerr_seed2/plunger.py --ana <ANA> --ic <IC> --run <RUN> --out "$NRPIC_RUN_DIR"'
    # note: figures, schematics, ledger; copy <run>/figures/* to figures/ and <run>/tables/* to tables/; compile; check
    harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/D-bh-dress/note_v2 --cores 2 -- \
      bash -c 'python tracks/D-bh-dress/note_v2/scripts/run_all.py'
    cd tracks/D-bh-dress/note_v2 && latexmk -pdf main.tex
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
      --forbid 'ES-1|V-1|D-pre|nrpic_cf|nrpic_geodesic|make_es|athinput|nrpic-run|puncture_drift|secondary_infall|einstein_straus|anta|A100|Slurm'

## State (2026-11-21, batch 6, closed)

**Note v2: done.** 22 pages, built from run D-20261121-220728-a41c2f0; checker with `--compile`:
0 undefined references, 0 undefined citations, 0 overfull boxes (remaining hits: 4 negations the
content needs, run ids and project names only in the ledger and the scripts, exception 1 of the
guide); every page read after the last build. Changes against v1, each from
`../stage/G1/GATE_REVIEW.md` sections 5-6 or the task:
- old main.tex 198-200 rewritten: no "belongs to the next version", no "ruling requested"; the
  infall section says the criterion was changed after the first runs by a ruling (decision 0021
  item 2) and that the power law itself is not tested, with the reason (errata row 1.7);
- Q16 (run to a/a_i = 16) in the text, in `fig_q16` and in ledger part 7 (with the gate
  reviewer's two estimators);
- the matched vacuum control with the faces at +-384 M (V-1B) named as the floor of the null
  test, and the late drift of the first control traced to its outer boundary (ledger part 8);
- the relaxed-lapse finding (decisions 0022 item 3, 0025 item 3) as its own subsection
  (V-1GB, ES-1G, ES-1GB numbers in ledger part 8);
- ES-F, the first G2 result: subsection, `fig_esf` (my own reading of the raw outputs
  reproduces D1 raw 9.88e-3 and control-subtracted 1.47e-3, F_rem 0.2414, the (iii) median
  2.2e-3), ledger part 9, parameter rows;
- Kerr second seed: paragraph, `fig_kerr_seeds`, ledger part 10;
- timeline header and architecture chain at the post-G1 state; abstract, introduction, plan,
  open items and summary rewritten to match.

**Kerr second seed: done** (JOURNAL N1, N3, N4). Pre-registered test held: no bias indicated
(Z2 = -0.84 > -1.5; seed-2 deviations -1.06, -1.04, -0.04 per cent in 0-4, 4-6, 6-10 M against
seed 1's -4.10, -1.77, -1.04). Two side predictions failed: one particle (the one drawn closest
to the capture boundary, 7.2e-6 relative) plunged at its first pericentre and, with no excision on
the analytic metric in the core-v0.3 executable used for both seeds, sat at r = 0.4 M and raised the 0-4 count by 0.7 per cent; and the 10-16 M
range lay at +2.1 sigma. Without the plunged particle all three inner ranges are low in both
seeds (two-seed means -3.0 +- 2.7, -1.4 +- 1.4, -0.5 +- 0.7 per cent, combined z -1.66): a deficit
of one to two per cent inside 10 M is neither shown nor excluded.

**Not done**: no second agent has checked parts 7-10 of the ledger or the seed comparison; the
direct sampler test at t = 0 with many more particles (the way to settle the Kerr question) was
not run; the claims check of v1 has 15 locators that no longer resolve (the lead's documents
changed; values unchanged); the outermost radial bin of the Kerr profile (80-100 M) lies 7-9 per
cent low in seed 2 (outside the test's ranges; not examined); paper-writing reviewer subagents
(step 4) not run (no subagent tool).

## Requests

- **To the lead of D-bh-dress**:
  1. Replace `../note/` by this directory (or point `stage/` at `note_v2/`): v2 is a full copy
     with the same layout, so `git mv` of the directory (and of `note/JOURNAL.md` history into
     the stage evidence) is enough; `nrpic-stage verify` reads `tracks/D-bh-dress/note/`.
  2. The "Looked at" column of `stage/G1/STAGE_REPORT.md` (gate review section 6): every figure
     of the note was read as a PNG in this session (2026-11-21, 13:2x-14:0x PST): fig_es,
     fig_constraints, fig_floor, fig_esrun, fig_spike, fig_kerr, fig_infall, fig_newton,
     schem_architecture, schem_timeline (v1 figures and the redrawn schematics), plus the new
     fig_esf, fig_q16, fig_kerr_seeds; the stage report itself is not mine to edit.
  3. G1 reservation 3 (Kerr): the second seed holds the pre-registered no-bias test but does
     not exclude a 1-2 per cent inner deficit; if the gate wants it settled, a direct sampler
     test at t = 0 (several million particles from `spike/sample_kerr.py`, binned against the
     same reference grid; processors only, no AthenaK) is the cheap next step.
  4. Excision on the analytic metric exists since release core-v0.4 (`tracks/core/interfaces/REQUESTS_ADF.md`
     row D4: lapse threshold and removal on the analytic metrics); both Kerr seeds ran on the
     core-v0.3 executable on purpose (seed 2 repeats seed 1 with only the seed changed), so the
     plunged particle stayed in the counts. A further seed or the sampler test should use a
     release with that excision (and Track D's own acceptance run `spike_lc.nrp` named in row D4
     is still Track D's to run).
  5. A second agent for ledger parts 7-10 (C17-style), especially the ES-F closure and the seed
     comparison.
- **To core**: none.
- **To orch**: none.
