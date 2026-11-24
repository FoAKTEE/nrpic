# repro/figs: the figures of arXiv:2512.14649 from our runs (Track E, batch R2)

Package of the reproduction of arXiv:2512.14649 (P1, `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`;
decision 0028). Every figure of P1 remade from our registered runs in P1's layout and the project
style, and the analysis-only rows of `../scope/REPRO_MAP.md`. P1's sources and figures are never
copied here; nothing read off P1's figures is stored as data (single comparison values with their
locator stand in the text of `RESULTS.md`).

- `RESULTS.md`: verdict per figure and per statement of the map, with the ledger (number, run id,
  script).
- `JOURNAL.md`: predictions (entry 1, written before any analysis) and outcomes.
- `CARD_COSTS.md`: actual card costs of the fifteen reproduction runs (the second table of
  `../scope/CARD_PLAN.md`).
- `fig/`: the figures (PNG; the PDFs stay in the run directory) and their numbers (json), copied
  unchanged from the registered figure run E-20261124-173254-420115f
  (`scratch/E-stoch-inf/E-20261124-173254-420115f/`, `sha256sums.txt` there). Figures that need a
  continued run of repro/continue are made from what has ended and say so (PENDING in `RESULTS.md`,
  section 5 names the run that completes each).
- `figures/`: the scripts.

## Scripts

| Script | What |
|---|---|
| `figures/figlib.py` | readers (dumps through `ladder/scripts/ladder_lib.py`, sequential; `.modes`; records, joined over restarts and continuations), lattice shells with the hemisphere count, P1's units (Mpl = 100), own Friedmann integration, potentials as coded |
| `figures/dumppass.py` | one pass over the dumps of a run: percentiles of the contrasts, of R^NR(x) and of the constraint ratios; binned spectra of R^NR, K, Kt, sqrt(3 Kt Kt/2); per injected shell the NR power against the realisation's linear power; with `--save-modes` the coefficients c_NR of every injected mode |
| `figures/bitcheck.py` | bit identity of two dumps in their common variables |
| `figures/runs.py` | registry label -> run id (and continuation), analysis groups (`usr256`, `sr256v6`, `ablation`, `rungs`, `rsf256`, `cl256`, `al2s`), bit-check pairs |
| `figures/fig1_meanrolls.py` | Fig. 1 (M64S, M64U records against own Friedmann) |
| `figures/fig_contrasts.py` | Figs. 2, 4 (percentile bands) |
| `figures/fig_spectra.py` | Figs. 3, 5 (`--kind R`, with the ratio figure) and 6 (`--kind K`) |
| `figures/fig_conv.py` | Figs. 7, 8 |
| `figures/fig_ablation.py` | Fig. 9 (and its controls) |
| `figures/make_figs.py` | every figure from the outputs of the dump passes |
| `figures/figstyle.py` | copy of `python/nrpic/figstyle.py` |

## How to rerun

From the worktree root, each step registered (processors, at most 6 cores; 256^3 dumps are read
sequentially, about 100 s per 3.6 GB dump per reader):

```
cd /data/haiyangw/nrpic/wt/E-stoch-inf
P=tracks/E-stoch-inf/repro/figs
# one dump pass per group (usr256, sr256v6, ablation, rungs; rsf256, cl256, al2s once the
# continuations of repro/continue have ended and are named in figures/runs.py CONTINUED)
harness/bin/nrpic-run submit --kind production --gate G2 --package $P \
  --preregistered "$P/JOURNAL.md#entry-1" --cores 6 --background --purpose "..." \
  -- bash -c 'OMP_NUM_THREADS=2 python3 tracks/E-stoch-inf/repro/figs/figures/runs.py usr256 "$NRPIC_RUN_DIR" --workers 3 --fft-workers 2'
# then the figures from those pass directories (the committed figures: run E-20261124-173254-420115f,
# with S=/data/haiyangw/nrpic/scratch/E-stoch-inf; about 1 min on 2 cores)
harness/bin/nrpic-run submit --kind production --gate G2 --package $P --cores 2 --purpose "..." \
  -- bash -c "OMP_NUM_THREADS=2 python3 $P/figures/make_figs.py \"\$NRPIC_RUN_DIR\" \
     --usr256 $S/E-20261124-130628-6790851 --usr256kt $S/E-20261124-141807-8352509 \
     --usr256kt $S/E-20261124-172949-8b2255b --sr256 $S/E-20261124-133251-42e8aab \
     --ablation $S/E-20261124-133251-42e8aab --rungs $S/E-20261124-133251-42e8aab \
     --ablation75 $S/E-20261124-141807-8352509 [--rsf256 <pass>] [--cl256s <pass>] [--al2s <pass>]"
# then copy the PNGs and jsons of the run into fig/ and look at each
```

Groups of `figures/runs.py` and their registered passes: `usr256` E-20261124-130628-6790851,
`sr256v6` + `ablation` + `rungs` E-20261124-133251-42e8aab, `usr256kt` + `ablation75`
E-20261124-141807-8352509, `usr256kt8` E-20261124-172949-8b2255b; `rsf256`, `cl256`, `al2s` wait for
the continuations of repro/continue (`RESULTS.md` section 5).

The run ids used for the committed figures are in `RESULTS.md` (ledger).

## Requests

See `RESULTS.md`, section "Requests" (kept there with the verdicts they come from).
