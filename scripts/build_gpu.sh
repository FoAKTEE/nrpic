#!/usr/bin/env bash
# Configure and build AthenaK for one A100 (Kokkos CUDA, sm_80; no MPI, no OpenMP).
#
#   scripts/build_gpu.sh [build_dir]
#
# Default build_dir: build_gpu (built-in pgens), build_gpu-<pgen> when PROBLEM is set,
# with "-debug" appended when DEBUG=1. Re-running is an incremental rebuild; edits to
# athenak/src/CMakeLists.txt (new source files) are picked up automatically.
#
# Environment: PROBLEM=z4c/z4c_one_puncture  DEBUG=1  JOBS=16  CUDA_HOME=/usr/local/cuda-12.6
#              HOST_ARCH=ICX  CMAKE_EXTRA="..."  RECONFIGURE=1   (see scripts/_build.sh)
# Prints the absolute path of the executable as the last line of output.
exec "$(dirname "${BASH_SOURCE[0]}")/_build.sh" gpu "$@"
