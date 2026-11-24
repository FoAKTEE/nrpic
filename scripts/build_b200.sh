#!/usr/bin/env bash
# Configure and build AthenaK for NVIDIA B200 (Kokkos CUDA, sm_100) + Xeon 8592+ (SPR).
# Default build directory lives under $SCRATCH_ROOT so home quota stays small.
set -euo pipefail

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SRC=${ATHENAK_SRC:-$REPO/athenak}
SCRATCH_ROOT=${SCRATCH_ROOT:-/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv}
PROBLEM=${PROBLEM:-built_in_pgens}
DEBUG=${DEBUG:-0}
JOBS=${JOBS:-15}
HOST_ARCH=${HOST_ARCH:-SPR}
GPU_ARCH=${GPU_ARCH:-BLACKWELL100}
CUDA_HOME=${CUDA_HOME:-/usr/local/cuda-12.8}

if command -v module >/dev/null 2>&1; then
  module load cmake/3.30.2 >/dev/null 2>&1 || true
fi

if [[ $# -ge 1 && -n $1 ]]; then
  BUILD_DIR=$1
else
  BUILD_DIR=$SCRATCH_ROOT/build_gpu
  if [[ $PROBLEM != built_in_pgens ]]; then BUILD_DIR+="-$(basename "$PROBLEM")"; fi
  if [[ $DEBUG == 1 ]]; then BUILD_DIR+="-debug"; fi
fi
mkdir -p "$BUILD_DIR"
BUILD_DIR=$(cd "$BUILD_DIR" && pwd)

if [[ ! -f $SRC/kokkos/CMakeLists.txt ]]; then
  echo "ERROR: $SRC/kokkos is empty; run: git -C $REPO submodule update --init" >&2
  exit 1
fi
if [[ ! -x $CUDA_HOME/bin/nvcc ]]; then
  echo "ERROR: no nvcc in CUDA_HOME=$CUDA_HOME" >&2
  exit 1
fi

WRAP=$BUILD_DIR/nvcc_wrapper_pinned
cat > "$WRAP.tmp" <<EOF
#!/bin/sh
CUDA_ROOT=$CUDA_HOME
NVCC_WRAPPER_DEFAULT_COMPILER=g++
export CUDA_ROOT NVCC_WRAPPER_DEFAULT_COMPILER
exec "$SRC/kokkos/bin/nvcc_wrapper" "\$@"
EOF
if [[ -f $WRAP ]] && cmp -s "$WRAP" "$WRAP.tmp"; then
  rm -f "$WRAP.tmp"
else
  mv "$WRAP.tmp" "$WRAP"
  chmod +x "$WRAP"
fi

if [[ $DEBUG == 1 ]]; then
  KDBG=ON
  BUILD_TYPE=RelWithDebInfo
  FLAGS_VAR=CMAKE_CXX_FLAGS_RELWITHDEBINFO
  FLAGS="-O2 -g -lineinfo"
else
  KDBG=OFF
  BUILD_TYPE=Release
  FLAGS_VAR=CMAKE_CXX_FLAGS_RELEASE
  FLAGS="-O3 -DNDEBUG"
fi

args=(
  -S "$SRC" -B "$BUILD_DIR"
  -G "Unix Makefiles"
  -DPROBLEM="$PROBLEM"
  -DAthena_ENABLE_MPI=OFF
  -DAthena_ENABLE_OPENMP=OFF
  -DCMAKE_CXX_COMPILER="$WRAP"
  -DCUDAToolkit_ROOT="$CUDA_HOME"
  -DKokkos_ENABLE_SERIAL=ON
  -DKokkos_ENABLE_CUDA=ON
  -DKokkos_ARCH_"$HOST_ARCH"=ON
  -DKokkos_ARCH_"$GPU_ARCH"=ON
  -DKokkos_ENABLE_DEBUG=$KDBG
  -DKokkos_ENABLE_DEBUG_BOUNDS_CHECK=$KDBG
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE
  -D$FLAGS_VAR="$FLAGS"
)

log=$BUILD_DIR/build.log
stamp=$BUILD_DIR/.configure_args
want=$(printf '%s\n' "${args[@]}")
if [[ ! -f $BUILD_DIR/Makefile || ! -f $stamp || ${RECONFIGURE:-0} == 1 ]] || \
   [[ "$(cat "$stamp")" != "$want" ]]; then
  rm -f "$stamp"
  cmake "${args[@]}" 2>&1 | tee "$log"
  [[ ${PIPESTATUS[0]} -eq 0 ]] || { echo "ERROR: cmake failed, see $log" >&2; exit 1; }
  printf '%s\n' "$want" > "$stamp"
fi

cmake --build "$BUILD_DIR" --parallel "$JOBS" 2>&1 | tee -a "$log"
EXE=$BUILD_DIR/src/athena
echo "Built: $EXE"
echo "$EXE"
