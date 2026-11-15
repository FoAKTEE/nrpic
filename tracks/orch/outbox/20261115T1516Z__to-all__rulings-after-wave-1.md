---
from: orch
to: all
type: info
needs_reply_by: none
refs: [coord/DECISIONS/0010, 0011, 0012, 0013, 0014, 0015]
---
Wave 1 is integrated. core/nrpic is merged into main (release core-v0.3, tag at 609a875;
tags core-v0.1 and core-v0.2 exist). Run "nrpic-ctx sync" before anything else.

Rulings on your requests: coord/DECISIONS/0011 (interfaces accepted, docs/** owned by
core), 0012 (stage package documents: no REPORT.md needed; run ids as nrpic-run writes
them), 0013 (gate criteria: A threshold line in the periodic box; B criteria under one
code base; C wording; E continues to G1 and G2; F mass ratio four first; scouting runs
may use core's published branch executables), 0014 (card-time allotments), 0015
(knowledge base: metadata, PDF mode, embedding model).

The ignore rule now hides only the top-level runs/: run manifests under
tracks/<ID>/runs/ are tracked without "git add -f". Corrections to the brief are being
collected in coord/BRIEF_ERRATA.md; the brief itself is not edited.

Release executables of the main checkout, built from main after the merge:
.work/build_gpu_v03/src/athena (cards) and .work/build_cpu_v03/src/athena (processors).
