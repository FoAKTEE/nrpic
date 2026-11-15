---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-13
refs: [run:D-bh-dress-20261115-123734-25227d4, run:D-bh-dress-20261115-123801-25227d4, athenak/src/particles/nrpic.cpp]
---
In the analytic-metric mode the particles inside the horizon are never removed:
`NrpicExcise` acts only for `metric = mesh` (athenak/src/particles/nrpic.cpp:627, read on
main); a particle whose push turns non-finite is flagged (PGID < -1) but stays in the
arrays and is pushed every cycle (nrpic.cpp:462-533). Track D's probe-limit tests (D-pre-2)
therefore had to measure capture as "r < 2 in a snapshot".

Request: apply `alpha_exc` (the analytic lapse at the particle) also for
`metric = kerr_schild`, `kerr_schild_sph`, `boyer_lindquist` and `lattice`, remove flagged
particles for every metric source, and count them in `n_excised` / `m_excised` of the
history. Acceptance test supplied: `spike_lc.nrp` of IC run
D-bh-dress-20261115-123734-25227d4 with `particles/alpha_exc = 0.62` must reach
n_excised = 1200, each removal after the predicted crossing time (`tcross` in
`ic_meta.npz`) by the infall time from r = 2 to the excision lapse; none of the 1200 bound
probes and none of run A's particles (D-bh-dress-20261115-123755-25227d4) removed.
Priority below the format-2 merge and the tracer blocker.
