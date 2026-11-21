#!/usr/bin/env bash
# Configure and build a threaded CPU AthenaK (Kokkos OpenMP, g++ -O3 -DNDEBUG -g) for
# production runs on the processors of anta. The serial build (build_cpu.sh) is unchanged.
#
#   scripts/build_cpu_omp.sh [build_dir]
#
# Default build_dir: build_omp (built-in pgens), build_omp-<pgen> when PROBLEM is set,
# with "-debug" appended when DEBUG=1 (Kokkos debug mode + View bounds checking).
# Re-running is an incremental rebuild.
#
# Environment: PROBLEM=...  DEBUG=1  JOBS=16  HOST_ARCH=ICX  CMAKE_EXTRA="..."  RECONFIGURE=1
#              OMP_OPT=debug   compile with the flags of the serial build (-O2 -g, asserts)
# Running: set the thread count and the placement explicitly, for example
#   OMP_NUM_THREADS=16 OMP_PROC_BIND=spread OMP_PLACES=cores <build_dir>/src/athena -i ...
# (scripts/README.md, "Threaded processor runs", has the measured scaling and the rules).
# Prints the absolute path of the executable as the last line of output.
exec "$(dirname "${BASH_SOURCE[0]}")/_build.sh" omp "$@"
