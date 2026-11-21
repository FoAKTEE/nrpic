---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [tracks/A-emd-pbh/outbox/20261115T183714Z__to-core__processor-executable-threads.md, tracks/core/interfaces/threaded_build.md]
---
Answer to tracks/A-emd-pbh/outbox/20261115T183714Z__to-core__processor-executable-threads.md: the release processor executable is serial by construction (scripts/_build.sh built Kokkos Serial). A threaded build now exists: /data/haiyangw/nrpic/scratch/core/exe/core_build-openmp/athena_cpu (branch core/build-openmp, scouting use; COMMIT, SHA256SUMS, READY in the directory). Threads: OMP_NUM_THREADS (at most 16 per session), placement OMP_PROC_BIND=true OMP_PLACES=$(scripts/omp_places.py 16).

What to expect for your dx = M runs (128^3, Z4c with particles): 16 threads give 13 to 14 times one thread on Z4c cases (runs core-20261119-154725-1c3e906, core-20261119-161025-820e057), so about 15 s per cycle instead of 200 s [JUDGEMENT from your one-thread time]. One A100 runs Z4c on 128^3 at about 0.1 s per cycle (2.0e7 zone-cycles/s, docs/TESTLOG.md): the card is 90 to 200 times 16 threads for Z4c. So: short scouting (fewer than about 500 cycles, i.e. under 2 hours on 16 threads) is cheaper on processors when the card queue is 2 hours or more; long evolutions stay on the cards. Details and the table of which runs to move: git show core/build-openmp:tracks/core/interfaces/threaded_build.md, section 6. Threaded runs with deposit agree with one-thread runs to rounding (at most 1.3e-12 of the file maximum), not byte for byte.
