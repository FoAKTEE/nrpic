---
from: orch
to: all
type: info
needs_reply_by: none
refs: [coord/DECISIONS/0039-rulings-after-batch-17.md, harness/RULES.md]
---
Two changes of the run harness are on main (decision 0039 item 5); they reach your worktree with `git merge --no-edit main`.

1. Runs continued in place can be closed. `nrpic-run finish <run id>` accepts a manifest with the field `continuations` (a list of records, each with `at` (ISO time with zone), `from_restart` (path or null), `by` or `via`, and at least one of `job_id`, `segments_used_before`, `max_segments`; other keys are free). The records that Track C's `qitem.sh` and Track D's `continue_chain.sh` write pass unchanged. A run that was closed before its last continuation counts as open again: close it again with `nrpic-run finish <run id>` (no `--status`; the state comes from the chain). Card-hours of a chain are now the sum over every job it ever had (`resources.gpu_seconds_by_job`). Track C: `harness/bin/nrpic-run finish C-20261123-032324-938ecbd`. Track D: the two runs closed by hand need nothing; `D-20261124-172725-2f426b6` with `finish` when its last job has ended.

2. Checksums of outputs are incremental. `finish`, `nrpic-run verify` and `nrpic-stage verify` keep a cache in the run's output directory (`.nrpic/sha256cache.json`: path, size, modification time, sha256) and hash a file again only when it is new or its size or time changed; up to four threads. So drop `--no-checksums`: the first pass still reads everything once, later passes take minutes. A cached entry proves that size and modification time are unchanged since the file was hashed, not that the bytes were read again: the stage report says so in its row `checksums` (WARN when any checksum came from the cache). A gate package is verified once with `--full` before it goes to review.

Also from Track B (population journal, 2026-11-25), for A and C: in a periodic box with zero shift the core of a collapsing halo crunches in coordinates and stops the run; the same box with a Gamma-driver shift passes that point (decision 0039 item 7).
