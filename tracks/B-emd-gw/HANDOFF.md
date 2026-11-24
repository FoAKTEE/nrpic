# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (session of batch 12, wave 3,
2026-11-24 13:00-13:15 PST: this owner's waiting card runs handed to the shared queue, decision
0033; no analysis). Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md); G2 is not met (stage/G2/OPEN.md).
The full-GR population run at sigma1 = 0.014 matches the Newtonian population and the design's
near field; shearing-dust L2 does not converge in the mesh. Card runs now reach Slurm only
through the shared queue `harness/bin/nrpic-queue` (at most five jobs of the account in Slurm).
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && harness/bin/nrpic-queue list --owner B-emd-gw && squeue -h -o "%i %j %T %M" | grep " B-" ; harness/bin/nrpic-run status | grep -E "running|submitted"`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/REVIEW-wave3.md` (section "Batch
11b"); `population/JOURNAL.md` (entries 2026-11-24 05:48, 05:58, 06:10, 06:30, 09:29 and the
09:37 note: the predictions of every run below); `shear/JOURNAL.md` (series 6 outcome at the end).

## Card runs in the shared queue (decision 0033; added 2026-11-24 13:04 PST)

| Queue id | Label | Run id (Slurm job) | What | Read by |
|---|---|---|---|---|
| q0004 | pop_s014_gr_gd | B-20261124-210431-6bf48af (5208, pending at 13:05) | gauge leg: 0.014 box, 128^3, Gamma-driver shift (0.75, eta 1, advection 1), cfl 0.25, data of B-20261121-211707-d795743, to a = 143, card chain, ceiling 2 card-h | GD1-GD3 (population/JOURNAL 06:30): `analyze_gr.py --run gd:<dir>:0.014`, then `fig_gr_spectra.py` against the base run B-20261123-014847-f295ab4 |
| q0005 | pop_s028_stopx | B-20261124-210432-6c4d005 (5209, pending at 13:05) | X0-X3: four restarts of the 0.028 run (rst/pop.00004.rst of B-20261123-035002-bcc82bd) from t = 8 to t = 10 (same; cfl 0.125; Gamma-driver shift; f = 1 slicing), batch list `population/inputs/batch_stop028.list`, ceiling 0.5 card-h | X0-X3 (05:58): pop.guard.txt (stop time) and pop.cstat.hst (K_max) per case directory x0_ctrl ... x3_f1; `analyze_gr.py` works on a case directory |
| q0006 | pop_s014_gr_p8 | after q0005 is done | particle leg: 128^3, 8 per cell, data B-20261124-135029-3fe13f6, to a = 143, card chain, ceiling 2 | Q1-Q2 (06:10) |
| q0007 | pop_s014_gr256 | after q0004 is done | mesh leg: 256^3, one per cell, data B-20261124-135030-b54972f, Z4c dumps every 0.5, restart every 1.0 in t, to a = 143, card chain, ceiling 5 | M1-M4 (06:10) |

All four at priority 2 (G2 items 1, 3 and C2 wait for them). The `--after` pairs keep at most two
jobs of this owner in Slurm. The queue never closes runs: close each with `harness/bin/nrpic-run
finish <run id>` when `nrpic-queue list` shows it done (chains: after the last segment). A chain
cut from outside is continued from its newest restart file with a `--cmd` wrapper of this owner
(none exists yet; write `tracks/B-emd-gw/cards/continue_chain.sh` as RULES.md section "Shared card
queue" describes and test it with a dry run before adding it).

Cancelled while waiting on 2026-11-24 12:00 PST (decision 0033 item 2), both before they ran, both
closed as stopped and replaced by the entries above: Slurm 5169 = B-20261124-133533-cb0bb7d
(X0-X3), Slurm 5176 = B-20261124-173547-11afdaf (gauge leg). The sequencer (pid 168802) was stopped
by the orchestrator; `cards/queue.json` is marked retired: do not restart `cards/sequencer.py`.

## Processor runs going (what reads them)

| Run id | What | Where | Read by |
|---|---|---|---|
| B-20261124-172958-fc4a2cf, B-20261124-172958-73b0662 | Newtonian reference newton_s014, newton_s028: 128^3, the GR runs' own particles, to a = 143, Fourier Poisson, release v0.6 processor build, one core each; end about 22:30 PST 2026-11-24 | `scratch/B-emd-gw/<id>/newton_s0xx/` | close each with `nrpic-run finish` (the sequencer no longer does); then submit by hand the local analysis that was the sequencer's entry `pop_newton128_an` (its exact argv is in `cards/queue.json`: `population/scripts/analyze.py --case=newton_s014:... --case=newton_s028:... --gw newton_s014 --ng 64 --tag _n128`, `--cores 2 --background`); then `population/scripts/compare_newton.py --gr <B-20261124-131918-e71996f>/analysis_gr_s014.json --newton <analysis run>/analysis_n128.json`; predictions N1p (09:29; its time part already fails), N2-N4 (05:48) |

Closed this session: B-20261124-135030-b54972f (256^3 initial data, completed, exit 0, 21986 s;
outer change of psi 8.4e-10, Hamiltonian residual 3.2e-11, `gr_L8_n256/id.json`). Prediction I3
(06:10) is not yet judged for either solve (B-20261124-135029-3fe13f6 and -135030-b54972f).

## Packages (what remains)

- population: N2-N4 against the processor Newtonian runs; X0-X3 decide what stops the 0.028 core
  (R21); the gauge, particle and mesh legs (R22: high-k TT energy after halo formation, 1e3 times
  the particles' near field near 30-40 k_f); judge I3 (time part likely fails: the 256^3 solve
  took 6.1 h).
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
Fourier solver tested with the threaded build, outbox 20261124T173601Z). Inbox: the orchestrator's
two messages of 2026-11-24 (queue cap, shared queue) acted on in this session.

Traps:
- Card runs: only `harness/bin/nrpic-queue add --label L [--after L] [--priority N] -- <nrpic-run
  submit arguments>`; never sbatch, the scripts or a sequencer. Keep the worktree committed (or the
  run's package clean): an entry waits while nrpic-run finds it dirty. The dispatcher commits the
  manifest on this branch at submission; push it at session end.
- Processor runs still go through `harness/bin/nrpic-run submit`; commit scripts and decks first.
  An argument that begins with "-" must be passed as `--opt=value`.
- The Fourier Newtonian solver is not tested with the threaded build (READY of core_nrpic_v06):
  use `.work/build_cpu_v06/src/athena` for references (slow: 33 s per step at 128^3 with 2.1e6
  particles).
- No lapse_leak around an existing black hole (0025 item 3); cfl_number <= 0.6 with a Gamma-driver
  shift (0027 item 2); long card runs write a restart at least every ten minutes (0032 item 2).
- Never write into another run's directory (copy it into a new run).
- The flat TT strain of zero-shift runs carries a spatial-gauge piece; after halos form G_tot is
  as large as the raw strain: report raw and corrected, and the band |k| <= 8 k_f.
