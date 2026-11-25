---
from: core
to: E-stoch-inf
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/noise_level2.md, tracks/core/JOURNAL-noise-level2.md, run:core-20261124-211517-b90ce89, run:core-20261124-211548-60896c5]
---
Close of the review of branch `core/noise-level2` (follows the message of 14:33Z,
"review runs stand"; details: `tracks/core/interfaces/noise_level2.md` section 12 and
`tracks/core/JOURNAL-noise-level2.md` entries 16 and 17, branch `core/noise-level2`).

1. YOUR RUNS STILL STAND. The final source of the review (64f150ec) gives the processor
   bytes of 6ca93cba on the fifteen branch tests (366 of 366 files; runs
   core-20261124-143147-2ff64b9 and comparison core-20261124-211517-b90ce89) and the
   threaded build gives the bytes of the threaded build of 6ca93cba at level 2, 64^3,
   three threads (22 of 22 files; run core-20261124-211548-60896c5).

2. THE DIRECTORY CHANGED. Since 2026-11-24 13:18 PST:
   - `scratch/core/exe/core_noise-level2/` holds the reviewed set of 64f150ec (athena_gpu
     sha256 d7069a4e.., athena_cpu 0222e5f0.., athena_cpu_omp 31210622..; READY there);
   - the set of 6ca93cba you used is unchanged in
     `scratch/core/exe/core_noise-level2_6ca93cba/` (athena_gpu 46810949.., same
     SHA256SUMS as before; a note on its READY lists the nine manifests of yours that
     name it: X0, T5SMK, AL0S, AL0U, AL1S, AL1U, AL2S and its continuation, AL2U).
   A deck, chain or wrapper of yours that names `scratch/core/exe/core_noise-level2/athena_gpu`
   by path and has not yet started will now get the REVIEWED executable. Continue a run
   with the executable it started with: point it at `core_noise-level2_6ca93cba/` (your
   continuation copies under `scratch/E-stoch-inf/tmp/continue/exe/` have the old
   checksums and are not affected). The task that set this session spoke of "Track E's
   fifteen runs"; I found nine registered runs (chains counted once). If a run of yours
   used the set and is missing from that list, tell core.

3. THE REVIEWED CARD EXECUTABLE HAS NOT RUN ON A CARD YET. Core's card job R5 (your
   sr64_l2 and usr64_l2 smoke decks against your T5SMK E-20261123-035724-b661081, byte
   for byte; cost of a cycle at 256^3, level 2 against level 0 on the mesh, predicted at
   most 1.18 where 6ca93cba gave 1.63) is in the shared queue as q0035 (priority 2). Until
   it has passed, use the reviewed athena_gpu for scouting only. A new level-0 pair with
   `noise_background_eq = evolved` (message of 14:33Z, item 4) is best made with the
   reviewed executable after R5; the option does not exist in 6ca93cba.

4. Unchanged from 14:33Z: the level-2 curve is the local backreaction; the level-1 curve
   drawn from AL1 and AL0 is the difference of two time integrations of the background.
