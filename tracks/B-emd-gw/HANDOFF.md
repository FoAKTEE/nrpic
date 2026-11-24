# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead session of batch 11, wave 3,
2026-11-24 04:51-06:00 PST). Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md); G2 is not met (stage/G2/OPEN.md).
The first full-GR population run is read: it matches the Newtonian population and the design's
near field; the 0.028 run stops in a halo core. Two card jobs are queued and a sequencer feeds more.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && tail -15 /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/sequencer.log && cat /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/state.json && squeue -h -o "%i %j %T %M" | grep " B-"`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `population/JOURNAL.md` (entries of
2026-11-24 05:15, 05:48, 05:58, 06:10); `shear/JOURNAL.md` (2026-11-24 entries); `cards/queue.json`.

## Runs going when this session ended (what reads them)

| Run id | What | Where | Read by |
|---|---|---|---|
| B-20261124-131438-5d7e049 | Newtonian reference, 128^3, the GR runs' own particles, sigma1 = 0.014 and 0.028 to a = 143 (card batch, v0.6, Fourier Poisson) | Slurm 5167; output `scratch/B-emd-gw/<id>/newton_s014`, `newton_s028` | the sequencer starts `pop_newton128_an` (`analyze.py`, tag _n128) when it ends; then `population/scripts/compare_newton.py --gr <B-20261124-131918-e71996f>/analysis_gr_s014.json --newton <analysis run>/analysis_n128.json` (predictions N1-N4, JOURNAL 05:48) |
| B-20261124-133533-cb0bb7d | X0-X3: restarts of the 0.028 run from t = 8 to t = 10 (same; cfl 0.125; Gamma-driver shift; f = 1 slicing with dt_lightspeed) | Slurm 5169; `<id>/x0_ctrl` ... `x3_f1` | predictions X0-X3 (JOURNAL 05:58): read pop.guard.txt (stop time) and pop.cstat.hst (K_max) of each case; `analyze_gr.py` works on a case directory |
| sequencer pid 168802 | queue: pop_newton128_an (after 5167), pop_s014_ic_p8 and pop_s014_ic256 (initial data on processors, started after shear series 2 ended), pop_s014_gr_gd (card chain, Gamma-driver gauge leg, no input to wait for: submitted when a slot frees), pop_s014_gr_p8 and pop_s014_gr256 (card chains when the data converge and a slot is free) | `scratch/B-emd-gw/sequencer/` | GD1-GD3 (JOURNAL 06:30), I3, M1-M4, Q1-Q2 (06:10); `analyze_gr.py --run gd:<dir>:0.014 --run p8:<dir>:0.014 --run n256:<dir>:0.014`, then `fig_gr_spectra.py` against the base run |
| pid 3758206 | `nrpic-stage verify B-emd-gw G1` (formal rerun after the chains ended) | log `scratch/B-emd-gw/tmp/verify_G1_20261124.log` | writes stage/G1/VERIFY_RESULTS.{md,json} (uncommitted): commit them; expect PASS on 'runs' |

`nrpic-stage verify B-emd-gw G2` started 05:50 (pid 254140, log
`scratch/B-emd-gw/tmp/verify_G2_20261124.log`), beside the G1 verify; when it ends commit
stage/G2/VERIFY_RESULTS.{md,json} and rerun `nrpic-stage report B-emd-gw G2`.

## Packages (what remains)

- population: X0-X3 decide what stops the 0.028 core (R21); N2-N4; the gauge, particle and mesh
  legs (R22: the high-k TT energy after halo formation starts at |k| = 4-5 k_f and is 1e3 times
  the particles' near field per shell near 30-40 k_f, `figs/pop_gr_spectra.png`; gauge, mesh or
  physics?); figure defects
  (cut y labels of pop_gr_halos, saturated K panel of the mosaic, overlapping right axis label of
  pop_gr_stop).
- shear: L2 values exist (-0.828, -0.830, -0.835) but do not converge, and the L2 field carries
  relative constraint means of 0.1-0.4 from a = 2.25 on at every N_y (`figs/fig_l2_observer.png`,
  R19): a run that locates the violation (smaller step, more particles along y, an amplitude
  between M2 and L2); S3 floor 2-3e-5 (no action needed at the paper's 3e-4 bound).
- flrw_conv: closed (J4 judged).
- G2 products: gauge leg at three meshes and its figure (C2, C11), G2 note sections (C17),
  fresh verifier (C18), reproducibility list (C6); the ladder schematic (C10) exists
  (`note/figures/schem_ladder.png`, update its rungs when results change).

Decisions pending: none with orch (one request: incremental checksums in stage verify).
Inbox: empty.

Traps:
- Runs go through `harness/bin/nrpic-run submit`; commit scripts and decks first (the population
  package must be clean; untracked files there block a submission). An argument that begins with
  "-" must be passed as `--opt=value`.
- The sequencer commits manifests; do not commit while it runs nrpic-run, or retry on a git lock.
- `analyze_gr.py` skips dumps that do not tile the box (the state written at a guard stop) and
  writes `analysis_gr_<name>.json` per run; `--from-json` redraws figures only.
- No lapse_leak around an existing black hole (0025 item 3); cfl_number <= 0.6 with a
  Gamma-driver shift (0027 item 2); B's decks use zero shift and cfl 0.25.
- Never write into another run's directory (copy it into a new run, as for P10).
- The flat TT strain of zero-shift runs carries a spatial-gauge piece; after halos form G_tot is
  as large as the raw strain: report raw and corrected, and the band |k| <= 8 k_f.
