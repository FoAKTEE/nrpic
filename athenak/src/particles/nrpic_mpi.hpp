#ifndef PARTICLES_NRPIC_MPI_HPP_
#define PARTICLES_NRPIC_MPI_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_mpi.hpp
//! \brief Helpers of the NRPIC module for runs on more than one MPI rank
//! (tracks/core/interfaces/mpi.md): reductions of scalars over the ranks, which do
//! nothing in a serial build and on one rank, and the search of a point in the table of
//! all MeshBlocks of the mesh.

#include <cstddef>
#include <initializer_list>

#include "athena.hpp"
#include "globals.hpp"

namespace nrpic {

//----------------------------------------------------------------------------------------
//! \fn FindBlockGlobal
//! \brief index (global ID) of the MeshBlock of the whole mesh whose half-open extent
//! contains the point, or -1 if the point lies outside the mesh.  ext(g,0..5) holds
//! x1min, x1max, x2min, x2max, x3min, x3max of MeshBlock g (Particles::gb_ext).

KOKKOS_INLINE_FUNCTION
int FindBlockGlobal(const DvceArray2D<Real> &ext, const int nmb, const Real x,
                    const Real y, const Real z) {
  for (int g=0; g<nmb; ++g) {
    if (x >= ext(g,0) && x < ext(g,1) && y >= ext(g,2) && y < ext(g,3) &&
        z >= ext(g,4) && z < ext(g,5)) {
      return g;
    }
  }
  return -1;
}

//----------------------------------------------------------------------------------------
// Reductions over the ranks, in place.  The lists hold pointers to the scalars.

#if MPI_PARALLEL_ENABLED
namespace mpi_detail {
constexpr int kMaxList = 64;
inline void Reals(std::initializer_list<Real*> v, MPI_Op op) {
  if (global_variable::nranks == 1) return;
  Real buf[kMaxList];
  int n = 0;
  for (Real *p : v) { buf[n++] = *p; }
  MPI_Allreduce(MPI_IN_PLACE, buf, n, MPI_ATHENA_REAL, op, MPI_COMM_WORLD);
  n = 0;
  for (Real *p : v) { *p = buf[n++]; }
}
inline void Ints(std::initializer_list<int*> v, MPI_Op op) {
  if (global_variable::nranks == 1) return;
  int buf[kMaxList];
  int n = 0;
  for (int *p : v) { buf[n++] = *p; }
  MPI_Allreduce(MPI_IN_PLACE, buf, n, MPI_INT, op, MPI_COMM_WORLD);
  n = 0;
  for (int *p : v) { *p = buf[n++]; }
}
} // namespace mpi_detail

inline void MpiSum(std::initializer_list<Real*> v) { mpi_detail::Reals(v, MPI_SUM); }
inline void MpiMin(std::initializer_list<Real*> v) { mpi_detail::Reals(v, MPI_MIN); }
inline void MpiMax(std::initializer_list<Real*> v) { mpi_detail::Reals(v, MPI_MAX); }
inline void MpiSum(std::initializer_list<int*> v) { mpi_detail::Ints(v, MPI_SUM); }
inline void MpiMax(std::initializer_list<int*> v) { mpi_detail::Ints(v, MPI_MAX); }

//! sum over the ranks of an array of n Reals (or floats), in place
inline void MpiSumArray(Real *a, const std::size_t n) {
  if (global_variable::nranks == 1 || n == 0) return;
  MPI_Allreduce(MPI_IN_PLACE, a, static_cast<int>(n), MPI_ATHENA_REAL, MPI_SUM,
                MPI_COMM_WORLD);
}
#if !SINGLE_PRECISION_ENABLED
inline void MpiSumArray(float *a, const std::size_t n) {
  if (global_variable::nranks == 1 || n == 0) return;
  MPI_Allreduce(MPI_IN_PLACE, a, static_cast<int>(n), MPI_FLOAT, MPI_SUM,
                MPI_COMM_WORLD);
}
#endif
#else
inline void MpiSum(std::initializer_list<Real*> v) {}
inline void MpiMin(std::initializer_list<Real*> v) {}
inline void MpiMax(std::initializer_list<Real*> v) {}
inline void MpiSum(std::initializer_list<int*> v) {}
inline void MpiMax(std::initializer_list<int*> v) {}
inline void MpiSumArray(Real *a, const std::size_t n) {}
#if !SINGLE_PRECISION_ENABLED
inline void MpiSumArray(float *a, const std::size_t n) {}
#endif
#endif

} // namespace nrpic
#endif // PARTICLES_NRPIC_MPI_HPP_
