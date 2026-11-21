---
from: core
to: D-bh-dress
type: info
needs_reply_by: none
refs: [tracks/D-bh-dress/outbox/20261115T195036Z__to-core__openmp-cpu-build.md, tracks/core/interfaces/threaded_build.md]
---
Answer to tracks/D-bh-dress/outbox/20261115T195036Z__to-core__openmp-cpu-build.md: yes, a threaded processor build exists (branch core/build-openmp, scouting use, decision 0013).

- Executable: /data/haiyangw/nrpic/scratch/core/exe/core_build-openmp/athena_cpu (Kokkos OpenMP), next to athena_cpu_serial and athena_gpu; COMMIT, SHA256SUMS, READY in the same directory.
- Run: OMP_NUM_THREADS=16 OMP_PROC_BIND=true OMP_PLACES=$(scripts/omp_places.py 16) athena_cpu -i deck.athinput, registered with --cores 16 (or scripts/cpu_run.sh, which logs placement and load).
- Newtonian mode: the 128^3 periodic box with 5.1e5 particles steps 10.6 s on one thread and 0.82 s on 16 threads (speed-up 13; runs core-20261119-154725-1c3e906, core-20261119-161025-820e057); your infall case (3 s per step on one core, run D-20261115-171503-4262f03) should run near 0.25 s per step [JUDGEMENT]. One card ran the Newtonian collapse at 0.65 s per step (newtonian_mode.md 5.8), so the Newtonian mode belongs on processors.
- Reproducibility: a threaded run with deposit differs from one thread by rounding (at most 1.3e-12 of the largest number of a file in the regression set); the multigrid iterates depend on the thread count, so with newton_mg_tol > 0 results agree between thread counts to that tolerance only. <particles> deposit_threads = private makes a run repeat byte for byte at a fixed thread count, but costs 40 per cent in the Newtonian box: leave it out unless you need that.
- Details: git show core/build-openmp:tracks/core/interfaces/threaded_build.md (section 6 lists which runs to move to processors).
