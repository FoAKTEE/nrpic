# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (resumed lead session of batch 11b,
wave 3, 2026-11-24 09:23-09:40 PST, after the first session of the item was stopped by the
pause flag at about 07:20). Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md); G2 is not met (stage/G2/OPEN.md).
The full-GR population run at sigma1 = 0.014 matches the Newtonian population and the design's
near field; shearing-dust L2 does not converge in the mesh. The cards are held by another user
until about 2026-11-25 morning; the Newtonian reference runs on processors meanwhile.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && grep -v "pause flag" /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/sequencer.log | tail -15 && cat /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/state.json && squeue -h -o "%i %j %T %M" | grep " B-"`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/REVIEW-wave3.md` (section "Batch
11b"); `population/JOURNAL.md` (entries 2026-11-24 05:48, 05:58, 06:10, 06:30, 09:29 and the
09:37 note); `shear/JOURNAL.md` (series 6 outcome at the end); `cards/queue.json`.

## Runs going when this session ended (what reads them)

| Run id | What | Where | Read by |
|---|---|---|---|
| B-20261124-172958-fc4a2cf, B-20261124-172958-73b0662 | Newtonian reference newton_s014, newton_s028: 128^3, the GR runs' own particles, to a = 143, Fourier Poisson, release v0.6 processor build, one core each; 33 s per step, about 13 h (end about 22:30 PST 2026-11-24) | `scratch/B-emd-gw/<id>/newton_s0xx/` | the sequencer closes them (queue `finish` list) and then starts `pop_newton128_an` (`analyze.py`, tag _n128); then by hand `population/scripts/compare_newton.py --gr <B-20261124-131918-e71996f>/analysis_gr_s014.json --newton <analysis run>/analysis_n128.json`; predictions N1p (09:29; its time part already fails), N2-N4 (05:48) |
| B-20261124-135029-3fe13f6 | initial data 128^3 x 8 per cell (`--ppc 2`), 36 outer iterations max (stops below 1e-9) | `<id>/gr_L8_n128/make_ic.log`, id.json at the end | prediction I3 (06:10); the sequencer then queues card chain pop_s014_gr_p8 (Q1-Q2) |
| B-20261124-135030-b54972f | initial data 256^3, one per cell | `<id>/gr_L8_n256/` | I3; then card chain pop_s014_gr256 (M1-M4), restart every 1.0 in t |
| B-20261124-133533-cb0bb7d (Slurm 5169, pending: priority partition) | X0-X3: restarts of the 0.028 run from t = 8 to t = 10 (same; cfl 0.125; Gamma-driver shift; f = 1 slicing) | `<id>/x0_ctrl` ... `x3_f1` | predictions X0-X3 (05:58): pop.guard.txt (stop time) and pop.cstat.hst (K_max) per case; `analyze_gr.py` works on a case directory. The sequencer closes it |
| B-20261124-173547-11afdaf (Slurm 5176, pending) | gauge leg pop_s014_gr_gd (Gamma-driver shift 0.75, eta 1, advection 1; cfl 0.25) to a = 143, card chain | `<id>/` | GD1-GD3 (06:30): `analyze_gr.py --run gd:<dir>:0.014`, then `fig_gr_spectra.py` against the base run B-20261123-014847-f295ab4 |
| sequencer pid 168802 (alive, started 05:40) | queue: pop_newton128_an (after the two processor runs), pop_s014_gr_p8 and pop_s014_gr256 (card chains after their initial data converge and a slot frees) | `scratch/B-emd-gw/sequencer/` | it logs a 'waiting:' line per entry and reason; the 'waiting' block of state.json can be stale for entries already submitted (see `runs`) |

Card job 5167 (B-20261124-131438-5d7e049) was cancelled before it ran (its manifest says failed,
exit 1: it never started); the processor runs replace it.

## Packages (what remains)

- population: N2-N4 against the processor Newtonian runs; X0-X3 decide what stops the 0.028 core
  (R21); the gauge, particle and mesh legs (R22: high-k TT energy after halo formation, 1e3 times
  the particles' near field near 30-40 k_f); judge I3 when the solves end (time part likely fails:
  256^3 at about 16 min per outer iteration, about 9 h in all).
- shear: series 1-6 judged (README "Results of series 2-6"). L2 not converged in the mesh at 4 per
  cell (order about 0.25). Next: design an amplitude between M2 (beta 0.05) and L2 (beta 0.5) at
  HL = 4 at which no stream crosses before t_A (from `shear_ref.py` and the Zel'dovich collapse of
  the y mode; check the stream crossing in the particle output), runs at N_y = 64, 128, 256 with 4
  per cell, fans chosen from the linear cos(theta) (`cos_lin`), prediction first (R19).
- flrw_conv: closed.
- G2 products: gauge leg at three meshes and its figure (C2, C11), G2 note sections (C17), fresh
  verifier (C18), reproducibility list (C6); rerun `nrpic-stage verify B-emd-gw G2` when the open
  runs are closed (it takes about an hour; the 14:57Z verify failed only on four open runs).

Decisions pending: none with orch (requests open: incremental checksums in stage verify; to core:
Fourier solver tested with the threaded build, outbox 20261124T173601Z). Inbox: empty.

Traps:
- Runs go through `harness/bin/nrpic-run submit`; commit scripts and decks first (the package must
  be clean). An argument that begins with "-" must be passed as `--opt=value`.
- The sequencer commits manifests; if a commit fails on the git lock, retry.
- The Fourier Newtonian solver is not tested with the threaded build (READY of core_nrpic_v06):
  use `.work/build_cpu_v06/src/athena` for references (slow: 33 s per step at 128^3 with 2.1e6
  particles).
- No lapse_leak around an existing black hole (0025 item 3); cfl_number <= 0.6 with a Gamma-driver
  shift (0027 item 2); long card runs write a restart at least every ten minutes (0032 item 2).
- Never write into another run's directory (copy it into a new run).
- The flat TT strain of zero-shift runs carries a spatial-gauge piece; after halos form G_tot is
  as large as the raw strain: report raw and corrected, and the band |k| <= 8 k_f.
