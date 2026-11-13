#!/usr/bin/env bash
# Configure and build a serial CPU AthenaK (Kokkos Serial, g++ -O2 -g, asserts on) for
# quick debugging on the login node, e.g. under gdb.
#
#   scripts/build_cpu.sh [build_dir]
#
# Default build_dir: build_cpu (built-in pgens), build_cpu-<pgen> when PROBLEM is set,
# with "-debug" appended when DEBUG=1 (Kokkos debug mode + View bounds checking).
# Re-running is an incremental rebuild.
#
# Environment: PROBLEM=...  DEBUG=1  JOBS=16  HOST_ARCH=ICX  CMAKE_EXTRA="..."  RECONFIGURE=1
# Prints the absolute path of the executable as the last line of output.
exec "$(dirname "${BASH_SOURCE[0]}")/_build.sh" cpu "$@"
