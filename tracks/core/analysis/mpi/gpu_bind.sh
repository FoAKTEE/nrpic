#!/usr/bin/env bash
# One card per MPI rank: rank r (local rank of Open MPI) sees only the r-th of the cards
# that Slurm gave the job, so that Kokkos on each rank uses device 0 of its own list.
#   mpirun -np 2 gpu_bind.sh athena -i ...
IFS=, read -ra devs <<< "${CUDA_VISIBLE_DEVICES:-0,1}"
r=${OMPI_COMM_WORLD_LOCAL_RANK:-0}
export CUDA_VISIBLE_DEVICES=${devs[$((r % ${#devs[@]}))]}
exec "$@"
