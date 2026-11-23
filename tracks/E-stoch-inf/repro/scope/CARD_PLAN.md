# Card plan of repro/scope (arXiv:2512.14649 reproduction; package cap 8 card-hours)

Executable: release card build core-v0.6 `/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena`
(read-only). Kind production, gate G2, predictions `JOURNAL.md` entry 1 (written before the first
submission). Submitted by `scripts/sequencer.sh` from `queue.txt`: at most two card jobs of owner E
eligible at a time (the lead's jobs count), the rest wait in the sequencer; refused submissions are
retried every 15 minutes; the pause flag stops new submissions.

Allotment (`harness/bin/nrpic-run budget`, 2026-11-22 18:16 PST): G2 20 card-hours, used 9.28,
reserved 2.47 (SMALL + USF256 at their ceilings), left 8.25. A chain counts at its ceiling while it
runs and at its actual cost once closed.

| Label | Run id (Slurm) | What | Ceiling (card-h) | Estimate (card-h) | Basis of the estimate | Disk |
|---|---|---|---|---|---|---|
| SMALL | E-20261123-020704-2b99463 (4929) | batch of 8: M64S, M64U (Fig. 1), C32S-C128S, C32U-C128U (Figs. 7, 8) | 0.5 | 0.15 | group 1: 132 s per 128^3 USR run, 12 s at 64^3 (usr README) | < 20 GB |
| USF256 | E-20261123-021204-2f573ec (4931) | USR 256^3, 41 dumps with [H], [M] (Figs. 4, 5, 6b) | 1.97 | 0.75 | U256ap 0.619 + 20 more dumps of 3.6 GB | 148 GB |
| RSF256 | (sequencer) | SR 256^3, 35 dumps with [H], [M] (Figs. 2, 3, 6a) | 1.97 | 0.65 | P256v6 0.509 + 17 more dumps | 127 GB |
| UL1 | (sequencer) | USR 256^3 level 1 (Fig. 9) | 1.97 | 0.62 | U256ap | 48 GB |
| RL1 | (sequencer) | SR 256^3 level 1 (Fig. 9) | 1.97 | 0.51 | P256v6 | 41 GB |
| RNC256 | (sequencer) | SR 256^3 sign flip to t = 4.5 (P1:541) | 0.98 | 0.27 | U256nc 0.224 to t = 3.75 | 20 GB |
| CL256U | (sequencer) | USR 256^3, nmax2 = 64, records + constraint dumps (Fig. 8b) | 1.97 | 0.55 | U256ap minus the synthesis of 548958 modes | 28 GB |
| CL256S | (sequencer) | SR 256^3, nmax2 = 64, to N_f (Figs. 7, 8a) | 1.97 | 0.45 | P256v6 minus the synthesis | 41 GB |
| **Total** | | | | **3.95** | | **about 0.45 TB** |

Within the cap of 8 card-hours by a factor two; no single run above 1 card-hour expected. The
largest reservation at one time is 3.94 (two chains at their ceilings). If the allotment refuses a
submission (left < ceiling), the sequencer retries; lower the ceiling in `queue.txt` (and commit)
only after reading the actual cost of a finished chain of the same kind.

Reused instead of rerun (same set-up, registered): P256v6 and P256 (SR 256^3 level 0, Fig. 3 and
the level-0 side of Fig. 9), U256ap/U256am (USR 256^3, Fig. 5, level 0 of Fig. 9), U256nc (USR sign
flip), the s2/s3 ladders (earlier versions of Figs. 7-8), window scan (s = 5 justification). See
`REPRO_MAP.md`.

Actual cost: fill in at `nrpic-run finish` (the sequencer closes each run; `gpu_hours` in the
manifest under `resources`).

| Label | Actual (card-h) | Wall (s) | Status |
|---|---|---|---|
| SMALL | | | pending |
| USF256 | | | pending |
| RSF256 | | | queued in the sequencer |
| UL1 | | | queued |
| RL1 | | | queued |
| RNC256 | | | queued |
| CL256U | | | queued |
| CL256S | | | queued |
