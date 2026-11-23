# HANDOFF of repro/scope to the next package (repro/figs)

State (2026-11-22 18:20 PST): map, audit, decks and card plan written; smoke test S0 passed; eight
card runs queued in an unattended sequencer (two submitted, both PENDING in Slurm at hand-over). No
card run of this package has produced output yet, so no outcome of JOURNAL entry 1 is recorded.

## The sequencer (outlives the session)

- See: `cat /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/state.tsv`;
  `tail -20 /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/seq.log`;
  `squeue -u $USER -o '%i %j %T %M' | grep ' E-'`.
- pid in `/data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/pid` (started 18:07 PST,
  pid 3079707). Stop: `touch .../repro_scope_seq/STOP` (exits within 5 min; running chains go on).
  Restart if it died (it skips labels submitted or finished):
  `cd /data/haiyangw/nrpic/wt/E-stoch-inf && setsid nohup bash tracks/E-stoch-inf/repro/scope/scripts/sequencer.sh > /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/nohup.out 2>&1 < /dev/null &`
- It closes finished runs (`nrpic-run finish`, which commits the manifest on this branch; push at the
  next session). Keep `tracks/E-stoch-inf/repro/scope/` committed (nrpic-run refuses a dirty package).
- It counts every E- job, the lead's too: if the lead loads the cards, the queue waits.

## Per figure: runs, files, reader

Outputs: `/data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>/` (chain runs: dumps `<basename>.sf.000NN.dump`,
records `<basename>.sf.hst`, `<basename>.sf.con.hst`, lockstep `.modes` beside each dump; batch runs:
one subdirectory per list name). Basenames: `sr` (SR decks), `usr` (USR decks). Read 256^3 dumps
sequentially (`usr/scripts/card_lib.py`), never through numpy's memmap (HANDOFF of E, traps).

| P1 figure | Runs (label: run id) | Files | Reader / script to start from |
|---|---|---|---|
| Fig. 1 mean rolls, 64 cells | M64S, M64U in SMALL: E-20261123-020704-2b99463/{M64S,M64U}; earlier Q64p (job C E-20261115-172625-416fec0), U64p (E-20261120-222621-ba66218) | `*.sf.con.hst` columns <phi>, <Pi>, <K> (SF2 section 3) | `nrpic.scalar_field.read_con_history`; references: SR E-20261115-135532-3f958a1, USR `usr/results/usr_reference.json` (table_half_efold) |
| Fig. 2 SR contrasts, 256 | RSF256 (sequencer; id in state.tsv) | 35 dumps: phi, Pi, K, chi, gt_ij (R^NR), H, Mx..Mz, Hmag, Mmag | `ladder/scripts/ladder_lib.py` (R^NR), percentiles 68/95/99/100 per dump |
| Fig. 3 SR spectra, 256 | RSF256, or P256v6 E-20261121-202935-31520bc (17 dumps) | dumps + `.modes` (R^MS) | `ladder/scripts/ladder_analysis.py judge`; bins with > 10 modes |
| Fig. 4 USR contrasts, 256 | USF256: E-20261123-021204-2f573ec | 41 dumps (same variables as RSF256) | `usr/scripts/card_lib.py` |
| Fig. 5 USR spectra, 256 | USF256, or U256ap E-20261121-211214-0377aab (21 dumps) | dumps + `.modes` | `usr/scripts/analyse_cards.py --group u256` |
| Fig. 6 K, K-tilde, sqrt(3KtKt/2) spectra | RSF256, USF256 (or P256v6, U256ap) | K, At_ij, chi | own spectra of At_ij/chi on the hemisphere |
| Fig. 7 spectral convergence (SR) | C32S, C64S, C128S in SMALL; CL256S | dumps every 0.5 with the metric | `ladder/scripts/analyse_all.py` + `verdicts.py` |
| Fig. 8 constraint convergence | SR: C32S..C128S, CL256S; USR: C32U..C128U, CL256U | `*.sf.con.hst` columns 4, 7 | `read_con_history` |
| Fig. 9 ablation | level 0: P256v6, U256ap; level 1: RL1, UL1 | dumps at N_f | shell spectra L1/L0 - 1 |
| P1:541 sign flip | RNC256 (SR), U256nc E-20261122-190341-0419be6 (USR) | records | ratio to RSF256 / U256ap per cycle |

Judge each run against `JOURNAL.md` entry 1 (P1-P7) before using it in a figure; write the outcome
there (or in the next package's journal with a pointer). P1 (bitwise repeat of P256v6 / U256ap at
common times) is the first check: if it fails, stop and report to core.

## Open

- Fig. 9 level 2: request `outbox_draft/core_noise_level2.md` (the lead posts it).
- Optional control of P1:488 (homogeneous slice at N* with the kicks): not queued (REPRO_MAP S27).
- TO VERIFY items of `SETUP_AUDIT.md` (3: SR Bunch-Davies start at k/aH = 100; 11: BSSN or CCZ4 in
  GRTeclyn; 16: P1's Courant factor; 21: P1's stage treatment of the noise).
- Card plan actual costs: fill the second table of `CARD_PLAN.md` as runs close.
