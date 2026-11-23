# HANDOFF of repro/ablation to repro/figs (Fig. 9 of P1) and to the lead of E

State (2026-11-22 20:00 PST): inputs checked and committed, parse check passed
(E-20261123-034420-0fe3c95), predictions written (JOURNAL entry 1), seven card runs queued in the
sequencer (smoke T5SMK first, the six 256^3 runs after the scope runs). No card run of this package
has been submitted yet: at hand-over two E jobs (SMALL 4929, USF256 4931) were pending in Slurm, so
the sequencer waits for a slot. No outcome of entry 1 exists yet.

## Where the runs are

- Run ids appear in `/data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/state.tsv` when the
  sequencer submits (labels below): `awk '$1=="AL2S"' .../state.tsv` (last line wins). The check of the
  smoke batch is the label `SMOKECHK` (status pass or fail; its run directory holds `verdict.json`,
  `smoke_check.png`).
- Sequencer: pid in `.../repro_scope_seq/pid` (started 19:52 PST, pid 18169), log `seq.log`; it closes
  finished runs with `nrpic-run finish` (manifests committed on this branch; the lead pushes). Restart
  if it died: header of `scripts/sequencer.sh`. It replaced the scope copy (do not start that one).

| Label | Deck | Level / mode equation | Output (scratch/E-stoch-inf/<run_id>/) |
|---|---|---|---|
| T5SMK | `inputs/smoke.list` (six 64^3 runs) | 0 shells, 2, 1 mesh (SR); 0 shells, 2, 0 mesh (USR) | one directory per name; `batch.list.status` |
| AL2S | `inputs/sr256_l2.athinput` | 2 (mesh implied) | `sr256_l2.sf.000NN.dump`, NN = 00..17 (t = 0.5 NN; N_f = 00017, t = 8.5) |
| AL2U | `inputs/usr256_l2.athinput` | 2 | `usr256_l2.sf.000NN.dump`, NN = 00..20 (t = NN tlim/20; N_f = 00020) |
| AL0S | `inputs/sr256_l0m.athinput` | 0, mesh | `sr256_l0m.sf.*` |
| AL0U | `inputs/usr256_l0m.athinput` | 0, mesh | `usr256_l0m.sf.*` |
| AL1S | `inputs/sr256_l1m.athinput` | 1, mesh | `sr256_l1m.sf.*` |
| AL1U | `inputs/usr256_l1m.athinput` | 1, mesh | `usr256_l1m.sf.*` |

Each 256^3 dump (NRSFDMP2) holds phi, Pi, chi, K, alpha, gt_ij, At_ij (17 variables, no H, M_i, E,
no magnitudes: the record `.sf.con.hst` has the constraint norms every cycle). Beside each dump:
`.modes` (lockstep shells, continuum k^2, the linear reference) and `.rmodes` (per mode `nx ny nz n2
Re_R Im_R Re_dR Im_dR`: the projections of the MESH R divided by L^-3/2 alpha_n). Records `.sf.hst`
(box means, rms, lockstep columns 18-21) and `.sf.con.hst`. Expected disk about 43 GB (SR) and 50 GB
(USR) per run plus restart files every 2.0.

## How to compare (decision 0031 item 1)

- Fig. 9: r20(k) = Delta_L2/Delta_L0m - 1 and r10(k) = Delta_L1m/Delta_L0m - 1 per shell at N_f, both
  scenarios, Delta = k^3 <|R^NR_k|^2>/(2 pi^2) in integer shells of |n|, shells with more than 10 modes
  (P1:454, 559). Level 0 ON THE MESH (AL0S, AL0U) is the reference, NOT P256v6/U256ap (level 0 on
  shells, release build): those differ at first order by the stencil and serve only as control P-A3
  (ii).
- R^NR: `tracks/E-stoch-inf/ladder/scripts/ladder_lib.py` (scope audit item 24). Read 256^3 dumps
  sequentially (`tracks/E-stoch-inf/usr/scripts/card_lib.py`), never through numpy's memmap.
- Judge against JOURNAL entry 1: P-A1 (SR), P-A2 (USR), P-A3 (controls: t = 0 dumps bit-identical
  across levels and with P256v6 / U256ap; L0m against shells; constraint records), and the
  refutation list (a first-order difference between levels, a one-signed r20, a (k dx)^6 rise, a
  guard stop): report a refutation to core before using the figure.
- Per mode, from `.rmodes`: rms over modes of |c_L2 - c_L0m|/|c_L0m| and of |c_L1m - c_L0m|/|c_L0m| at
  each dump (core's T1c quantity, 1.1e-4 rms in SR at 32^3): links the spectra to the noise field.
- The note says which executable each run used (decision 0031 item 3): AL* and T5SMK the branch card
  build `scratch/core/exe/core_noise-level2/athena_gpu` (source 6ca93cba), P256v6/U256ap the release
  card build core-v0.6. The [JUDGEMENT] choices of level 2 are in `tracks/core/interfaces/noise_level2.md`
  (branch core/noise-level2) sections 3 and 6.

## For the lead

- Post `outbox_draft/core_t5.md` (fill the outcome lines from SMOKECHK's `verdict.json`; look at
  `smoke_check.png` first). If the check FAILs, the six runs stay held: report to core with the
  verdict and the figure.
- RL1/UL1 of the scope queue are superseded for Fig. 9 (README, Requests): skip them in state.tsv if
  you agree; they cost about 1.1 card-hours and two queue slots.
- `repro/scope/HANDOFF.md` names the old restart command; point it to this package's sequencer.
- Card budget: this package's cap is 5 card-hours (sequencer guard; predicted 3.7-4.3); the
  allotment of E toward G2 is 30 (decision 0031): 18.25 left at 19:40 PST before these runs.

## Not done

- No card run of this package has started; no outcome of P-T5 or P-A1..A3 exists.
- The card executable still has run no step on a card (it will in T5SMK).
- No figure of the ablation (that is repro/figs, after the runs).
