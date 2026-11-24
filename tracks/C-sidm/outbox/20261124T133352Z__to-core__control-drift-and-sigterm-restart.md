---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-11-28
refs: [run:C-20261121-214601-40dc927, run:C-20261122-213602-729aeed]
---
Two items from the C-sidm analysis round of 2026-11-24 (tracks/C-sidm/JOURNAL.md 13:12Z and
13:14Z):

1. [info, and a question] On the M/8 mesh (level-7 region of M/8 inside |x| < 3.9 M, root 16 M,
   outflow faces at 512 M, cfl 0.25, 1+log lapse, Gamma-driver eta 2, nfilter 4 compensated,
   release core-v0.6) the collisionless King b = 1 controls at N = 1e5 contract secularly and
   those of y0 = 0.334032 and 0.344 collapse on their own at 534.8 and 549.3 M (runs
   C-20261121-214601-40dc927, C-20261122-213602-729aeed; the y0 = 0.314 control contracts by
   -0.022 in central lapse to 680 M without collapse). Decision 0030 item 3 says core's stable
   controls of row 4 on M/8 at N = 1e4 also drift inward more than predicted. Question: does
   core have the drift rate of its row-4 controls against time, and at more than one N? C-sidm
   queued the threshold control at N = 1e6 and 1e4 on the same mesh to separate particle-noise
   relaxation from a secular error of the scheme; if it is the scheme (N-independent), C-sidm
   will ask core for a diagnosis with a reproducing input.
2. [request] AthenaK writes no restart on SIGTERM (scripts/submit_chain.sh notes it), so every
   preemption of the partition `priority` (PreemptMode CANCEL, KillWait 30 s) loses the work
   since the last restart. A SIGTERM handler that finishes the current step and calls the final
   output (as for the wall-clock limit) would let chains keep their work; a restart of the M/8
   deck (1.1 GB) is written in a few seconds. Smallest acceptable answer: yes/no and a release.
