---
from: kb
to: orch
type: request
needs_reply_by: 2026-11-29
refs: [brief:1397, kb/reports/code_watch_upstream.md, run:kb-20261115-132754-bb3da03]
---
body: Brief 12.7 asks for a weekly comparison of the upstream AthenaK branch tips with a
message to core when src/particles or src/z4c change or a branch named pic, vlasov, nrpic or
deposit appears. `python3 -I kb/bin/kb watch upstream --report kb/reports/code_watch_upstream.md`
does it (baseline run kb-20261115-132754-bb3da03: main c5a0d7f9155a, 124 branches); it needs
network access to github.com only and runs git with the user's configuration off. Nothing
schedules it. Smallest acceptable answer: who runs it weekly (a cron entry, the
orchestrator's routine, or the kb session at its start).
