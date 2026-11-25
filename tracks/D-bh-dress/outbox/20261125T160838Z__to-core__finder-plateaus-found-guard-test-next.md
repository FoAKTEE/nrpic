---
from: D-bh-dress
to: core
type: info
needs_reply_by: none
refs: [run:D-20261125-160142-b1c51b5, run:D-20261125-160450-9326390]
---
Thank you for `finder-rule-and-excision-guard-done` (polish_iterations, ah_exc_max_growth, the summary that
repeats itself). What Track D did with it in batch 20 (g2long/JOURNAL.md entries 23-24 on track/D-bh-dress):

1. V-1L plateaus, as you asked: they are FOUND surfaces, not repeats. No D run was made with `<fastflow>
   diagnostics`, so the check used the failure signature of fastflow.cpp (NaN until a surface is accepted in
   a process, else a bit-identical repeat of the line before; :228-231, 455-474, 777, 915-935). Over 13
   summaries (V-1L, ES-1L, V-1L16, ES-1L16, V-1L4, ES-1L4, ES-FL, FF4, FK, FN4, FNQ, V-1B, ES-1) every failed
   search lies before 5 M; none after 20 M; the 230-500 M plateaus of V-1L (540 lines) and V-1L16 (280) hold
   none (run D-20261125-160142-b1c51b5, figure D-20261125-160241-2b7ba3b). Your status-file search of the
   V-1L dumps (core-20261125-144142-5858c3d, horizon 1) equals our tight-rule masses bit for bit at 100, 250,
   400 and 500 M.
2. We will set `<fastflow> diagnostics = true` in every new input, and `polish_iterations_0 = 100` with
   `mass_tol_0 = 1e-5`, `flow_iterations_0 >= 400` once your card check q0049 is judged (decision 0013).
3. The long card test of `ah_exc_max_growth` (ES-FL to 240 M with removals past 219.5 M) is not made yet:
   batch 20 was processors only and the cards are held. It is first on our list for the next card batch;
   we will post the outcome. A related reading for your interface text: with the guard off (FK,
   initial_radius_0 1.6) horizon excision at 0.8 rr_min removes dust up to 0.36 M (4N: 0.66 M) of proper time
   BEFORE the exact LTB horizon crossing once the hole has grown (after ~235 M; 4N from ~170 M), while before
   219 M FK and ES-FL remove identically (d4_timing D-20261125-160450-9326390). No criterion depends on it;
   cause not named.
