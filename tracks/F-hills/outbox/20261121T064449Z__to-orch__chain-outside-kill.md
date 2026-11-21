---
from: F-hills
to: orch
type: proposal
needs_reply_by: 2026-11-28
refs: [run:F-20261119-150017-b45ec5f]
---
Proposal for scripts/submit_chain.sh (owner orch), from F-hills package p1
(tracks/F-hills/p1/REQUESTS.md item 1, JOURNAL entry 0):

What happened [VERIFIED by p1]: segment 7 of P1 (run F-20261119-150017-b45ec5f, Slurm 4684) ended
2026-11-19 19:35:43 PST with "STATUS FAILED (athena exit status 143)". It was not a preemption:
sacct records FAILED with the chain script's own exit 1, the TERM trap of the batch script did not
fire, and the signal came from `pkill -x athena` run at that second by a session of another
project of the same Unix account (P1's process was named athena). AthenaK has no signal handler;
the chain saw rc 143 with its TERM flag unset and stopped. P1 was resumed by hand on 2026-11-20
and has run 7 more segments since.

Proposed:
1. When athena exits with 143 or 137 with no AthenaK termination message in the segment log and
   the chain's TERM flag unset, log "athena killed by signal N (not via the batch script)" and
   resubmit from the newest restart, at most twice in a row.
2. Run the real executable under a run-specific process name (a copy or hard link
   `chain/ak-<run id>`), so that `pkill -x athena` elsewhere cannot reach chained card runs. P1 does
   this by hand (`scratch/F-hills/tmp/p1/exe/p1-ak03-gpu`, byte-identical to the release build).
3. `--status` prints the last attempt's exit code and its cause.
4. For the user (decision 0017 item 5, information): sessions outside this program on anta use
   `pkill -x athena`, which kills every AthenaK process of the account, card jobs of this program
   included.
