# Machine file of anta (brief section 11.4): read by harness/lib/nrpic_harness.py as KEY=VALUE
# lines (nothing is executed; ${VAR} refers to earlier keys or to HOME, USER, NRPIC_HOME, NRPIC_WT,
# NRPIC_TRACK). Its sha256 is part of the environment hash recorded in every run manifest.
# Shell-compatible, so `source` also works for a quick look.
NRPIC_HOST=anta
# toolchain (scripts/README.md): CUDA 12.6 pinned, host g++ 11.4, Kokkos 4.7.02 submodule
CUDA_HOME=/usr/local/cuda-12.6
NRPIC_PYTHON=/usr/bin/python3
PATH=${HOME}/.local/bin:/usr/local/cuda-12.6/bin:/usr/local/bin:/usr/bin:/bin
# shared download cache of uv (content-addressed; the venvs are copies, UV_LINK_MODE=copy)
UV_CACHE_DIR=${NRPIC_HOME}/cache/uv
# release executables of the main checkout, built from main after the merge of core-v0.3
# (CLAUDE.md); read-only for everyone. core-v0.2: .work/build_gpu_c3, .work/build_cpu_c1
NRPIC_GPU_EXE=${NRPIC_HOME}/.work/build_gpu_v03/src/athena
NRPIC_CPU_EXE=${NRPIC_HOME}/.work/build_cpu_v03/src/athena
# Slurm: two A100, partition preempt, 1 h per job, 4 cores in the partition
NRPIC_PARTITION=preempt
NRPIC_GPU_NAME=NVIDIA A100 80GB (Slurm partition preempt)
NRPIC_SLURM_MAX_TIME=01:00:00
NRPIC_CHAIN_SEGMENT=00:59:00
