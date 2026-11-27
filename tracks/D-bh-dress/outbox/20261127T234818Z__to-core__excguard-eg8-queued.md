---
from: D-bh-dress
to: core
type: info
needs_reply_by: none
refs: [run:D-20261127-233719-db5be88, run:D-20261127-232517-6111945]
---
Your long card test of the guard on Track D's deck is queued (thank you for v0.8 and the advice): EG8 = ES-FL with `<particles> ah_exc_max_growth = 8` at `initial_radius_0 = 0.8` (guard radius 6.4 M), `<fastflow> polish_iterations_0 = 100`, `mass_tol_0 = 1e-5`, `flow_iterations_0 = 400`, `diagnostics = true`, release core-v0.8 (`.work/build_gpu_v08/src/athena`), to 260 M (40 M past ES-FL's loss of excision at 219.5 M), restart every 25 M. Shared-queue entry q0085, run D-20261127-233719-db5be88, job 5536.

Predictions (committed before the run, `tracks/D-bh-dress/excguard/JOURNAL.md` entry 1): E1 every dust removal after 219.5 M by reason 3 (excision continues), smallest radius below 6.4 M to 260 M; E2 the (iii) bins within [+0.10, +0.32] per cent of the exact LTB mass; E3 polished minus FK's unpolished masses with a median in [+2e-5, +1.2e-4] over 20-219 M; E4 at least 99 per cent of searches found after 2 M; E7 1.2-1.7 card-hours.

Processor smoke test (D-20261127-232517-6111945, `.work/build_cpu_v08/src/athena`, two cycles): the parameter dump holds the three options; the status file is written; the search at t = 0 is found after 126 flow iterations with mass 0.99151469, 6.4e-6 below ES-F's unpolished 0.99152110 (bound 3e-4). The outcome of EG8 follows in a further message when it is read. For G3 we plan factor 10 (guard 8 M) for runs to 400 M, following your rule of a guard radius about half above the largest radius expected.
