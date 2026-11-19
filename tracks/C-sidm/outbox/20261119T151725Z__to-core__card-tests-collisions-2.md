---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-11-24
refs: [run:C-20261119-150335-73fd40f, run:C-20261119-150347-e100007]
---
Request from the C-sidm lead (wave 2b).

The card executable of core/collisions-2 (`scratch/core/exe/core_collisions-2/athena_gpu`,
sha256 82a05ada...) has five FAIL lines in its `CARD_TESTS.log` (job 4484, parts R:
rate_vs_release, relax_vs_release, repro_vs_release, conv_dt_vs_release, curved_vs_release;
"compared N differ M"). Card runs with deposition are not byte-reproducible, so a bytewise
comparison may fail for a harmless reason; the log does not say which.

The track's heat-conduction helper (package `tracks/C-sidm/heat/`, wave 3a) has two card jobs
queued with this executable (runs C-20261119-150335-73fd40f, C-20261119-150347-e100007), and
the lead's next card runs (the decisive cluster runs at Kn = 10 with coll_energy = particle,
`tracks/C-sidm/stage/REVIEW-wave2.md` section 7) need it too.

Asked: state in READY (or CARD_TESTS.log) whether the card executable passes the statistical
criteria of the processor tests (rates, relaxation, counts within 4 sigma; replay on the card),
and what the FAIL lines mean. Smallest acceptable answer: one line "card executable usable for
scouting: yes/no, because ...".
