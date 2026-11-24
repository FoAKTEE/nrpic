# Actual card costs of the reproduction runs (read 2026-11-24 from the manifests)

Source: `tracks/E-stoch-inf/runs/<run_id>/manifest.json`, field `resources.gpu_hours` written by
`nrpic-run finish` (the sequencer closed every run). This is the second table of
`../scope/CARD_PLAN.md`, which the sequencer did not fill; this package may not edit `repro/scope`, so
the lead copies it there (README, Requests). "Cut" = closed as `failed` because the chain reached its
segment limit before tlim; continued by `repro/continue` (its own manifests carry the rest of the cost).

| Label | Run id | Status | Card-h | Wall of the chain (s) | Estimate (CARD_PLAN) |
|---|---|---|---|---|---|
| SMALL | E-20261123-020704-2b99463 | completed | 0.0808 | 291 | 0.15 |
| USF256 | E-20261123-021204-2f573ec | completed | 0.6628 | 2385 | 0.75 |
| RSF256 | E-20261123-035925-8439d79 | cut at t = 0.387 of 8.5 | 0.0644 | - | 0.65 |
| UL1 | E-20261123-040126-2d0323c | completed | 0.6350 | 2212 | 0.62 |
| RL1 | E-20261123-040327-ccae634 | completed | 0.5233 | 1811 | 0.51 |
| RNC256 | E-20261123-045030-c20bcb3 | cut at t = 0.712 of 4.5 | 0.0442 | - | 0.27 |
| CL256U | E-20261123-065855-265732a | cut at t = 4.77 of 10.44 | 0.2478 | - | 0.55 |
| CL256S | E-20261123-090727-4b6e5a5 | cut at t = 6.23 of 8.5 | 0.3522 | - | 0.45 |
| **scope total** | | | **2.611** | | 3.95 |
| T5SMK (ablation smoke) | E-20261123-035724-b661081 | completed | 0.0175 | 63 | 0.05 |
| AL2S | E-20261123-152119-38957ba | cut at t = 7.53 of 8.5 | 1.0397 | 3011 | 0.55-0.65 |
| AL2U | E-20261123-153146-d965002 | completed | 1.1592 | 1737 | 0.65-0.75 |
| AL0S | E-20261123-153347-18e7c21 | completed | 0.6014 | 2084 | 0.55-0.65 |
| AL0U | E-20261123-164235-49b0945 | completed | 0.7075 | 2546 | 0.65-0.75 |
| AL1S | E-20261123-183822-4abbcae | completed | 0.5789 | 2083 | 0.55-0.65 |
| AL1U | E-20261123-192948-348e2e5 | completed | 0.7064 | 2540 | 0.65-0.75 |
| **ablation total** | | | **4.811** | | 3.7-4.3 |

Notes. The cut chains were preempted by another user's priority jobs on 2026-11-23 (`repro/continue`
task text); their card-hours include the preempted segments. AL2S (1.04) and AL2U (1.16) are above the
ablation prediction's refutation bar "a 256^3 run above 1.0 card-hours" (`../ablation/JOURNAL.md`
entry 1, cost): the cost prediction failed for the two level-2 runs [VERIFIED from the manifests].
Both lost their first segment to preemption (`chain/events.log`): AL2U segment 1 (job 4985) ran from
09:26 to 10:06 PST and received SIGTERM, segment 2 (job 5007) resumed from `rst/usr256_l2.00003.rst`
and ran 29 min to tlim, so the work between that restart file and the SIGTERM was done twice; AL2S
segment 1 (job 4984) was likewise killed and segment 2 (job 5004) restarted from
`rst/sr256_l2.00000.rst`, i.e. from the start, and reached t = 7.53 at its wall limit. The column
"wall" is that of the last segment. The overrun is the preemption, not the level-2 path: AL0U ran in
one segment of 42 min [VERIFIED from the events logs; the cost per cycle of level 2 against level 0
is P-T5(c) of the ablation, 0.95-1.5, judged in `JOURNAL.md`].
