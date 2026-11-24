# repro/figs: the figures of arXiv:2512.14649 from our runs (Track E, batches R2 to R4)

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
  unchanged from the registered figure run E-20261124-230839-0e1e13a
  (`scratch/E-stoch-inf/E-20261124-230839-0e1e13a/`, `sha256sums.txt` there), which includes all five
  continued runs at their tlim (RSF256 to t = 8.5 since batch R4: `fig2_sr_contrast`, `fig3_sr_spec*`,
  `fig6a_sr_Kspec`) and the junction check `fig_joins.png` / `joins.json`. No row of `RESULTS.md` is
  PENDING.
- `HANDOFF.md`: state for a reader with no memory, and what package repro/continue still has to do
  (append RSF256's fourth continuation E-20261124-214913-5956891 to its `conts.json`).
- `conts_rsf256.json`: repro/continue's `scripts/conts.json` with that continuation appended; input of
  this package's join check E-20261124-225720-444aecc (repro/continue's `join_check.py --conts`).
- `figures/`: the scripts.

## Scripts

| Script | What |
|---|---|
| `figures/figlib.py` | readers (dumps through `ladder/scripts/ladder_lib.py`, sequential; `.modes`; records, joined over restarts and continuations), lattice shells with the hemisphere count, P1's units (Mpl = 100), own Friedmann integration, potentials as coded |
| `figures/dumppass.py` | one pass over the dumps of a run: percentiles of the contrasts, of R^NR(x) and of the constraint ratios; binned spectra of R^NR, K, Kt, sqrt(3 Kt Kt/2); per injected shell the NR power against the realisation's linear power; with `--save-modes` the coefficients c_NR of every injected mode |
| `figures/bitcheck.py` | bit identity of two dumps in their common variables |
| `figures/runs.py` | registry label -> run id (RSF256's dumps by directory: `RSF256` original, `RSF256b` third continuation, `RSF256c` fourth), continuations (`CONTINUED`, as repro/continue `conts.json` plus RSF256's fourth, `../conts_rsf256.json`) and joined records (`JOINED`, the join-check run of repro/continue; for RSF256 this package's E-20261124-225720-444aecc), analysis groups (`usr256`, `sr256v6`, `ablation`, `rungs`, `rsf256`, `cl256`, `al2s`, `rsf256bit`), bit-check pairs |
| `figures/joins.py` | our own join of the record pieces against the joined records, the step across each junction (`fig_joins`, `joins.json`), and RSF256's joined record against P256v6's (scope P1, records) |
| `figures/fig1_meanrolls.py` | Fig. 1 (M64S, M64U records against own Friedmann) |
| `figures/fig_contrasts.py` | Figs. 2, 4 (percentile bands) |
| `figures/fig_spectra.py` | Figs. 3, 5 (`--kind R`, with the ratio figure) and 6 (`--kind K`) |
| `figures/fig_conv.py` | Figs. 7, 8 |
| `figures/fig_ablation.py` | Fig. 9 (and its controls) |
| `figures/fig_signflip.py` | the sign-flip control (P1:541; RNC256 against RSF256, U256nc against U256ap) and scope P2's record maxima of the proper SR run |
| `figures/make_figs.py` | every figure from the outputs of the dump passes |
| `figures/figstyle.py` | copy of `python/nrpic/figstyle.py` |

## How to rerun

From the worktree root, each step registered (processors, at most 6 cores; 256^3 dumps are read
sequentially, about 100 s per 3.6 GB dump per reader):

```
cd /data/haiyangw/nrpic/wt/E-stoch-inf
P=tracks/E-stoch-inf/repro/figs
# one dump pass per group (usr256, sr256v6, ablation, rungs, usr256kt, usr256kt8, ablation75; cl256,
# al2s, rsf256bit, rsf256 after the continuations)
harness/bin/nrpic-run submit --kind production --gate G2 --package $P \
  --preregistered "$P/JOURNAL.md#entry-1" --cores 6 --background --purpose "..." \
  -- bash -c 'OMP_NUM_THREADS=2 python3 tracks/E-stoch-inf/repro/figs/figures/runs.py usr256 "$NRPIC_RUN_DIR" --workers 3 --fft-workers 2'
# then the figures from those pass directories (the committed figures: run E-20261124-230839-0e1e13a,
# with S=/data/haiyangw/nrpic/scratch/E-stoch-inf; about 1 min on 2 cores)
harness/bin/nrpic-run submit --kind production --gate G2 --package $P --cores 2 --purpose "..." \
  -- bash -c "OMP_NUM_THREADS=2 python3 $P/figures/make_figs.py \"\$NRPIC_RUN_DIR\" \
     --usr256 $S/E-20261124-130628-6790851 --usr256kt $S/E-20261124-141807-8352509 \
     --usr256kt $S/E-20261124-172949-8b2255b --sr256 $S/E-20261124-133251-42e8aab \
     --ablation $S/E-20261124-133251-42e8aab --rungs $S/E-20261124-133251-42e8aab \
     --ablation75 $S/E-20261124-141807-8352509 --cl256s $S/E-20261124-213029-e937f69 \
     --al2s $S/E-20261124-213029-e937f69 --rsf256 $S/E-20261124-225826-0bf3842"
# then copy the PNGs and jsons of the run into fig/ and look at each
```

Groups of `figures/runs.py` and their registered passes: `usr256` E-20261124-130628-6790851,
`sr256v6` + `ablation` + `rungs` E-20261124-133251-42e8aab, `usr256kt` + `ablation75`
E-20261124-141807-8352509, `usr256kt8` E-20261124-172949-8b2255b, `cl256` + `al2s` + `rsf256bit`
E-20261124-213029-e937f69, `rsf256` E-20261124-225826-0bf3842 (after the join check
E-20261124-225720-444aecc, which `figures/runs.py` reads as RSF256's joined record; `RESULTS.md`
section 5).

The run ids used for the committed figures are in `RESULTS.md` (ledger).

## Requests

See `RESULTS.md`, section "Requests" (kept there with the verdicts they come from).
