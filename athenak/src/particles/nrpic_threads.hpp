#ifndef PARTICLES_NRPIC_THREADS_HPP_
#define PARTICLES_NRPIC_THREADS_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_threads.hpp
//! \brief Where the deposit of the NRPIC module adds the cloud of a particle, for a
//! threaded processor build (Kokkos OpenMP, scripts/build_cpu_omp.sh).
//!
//! The deposit is a scatter: particles handled by different threads add to the same
//! cell.  Two ways to make that correct:
//!   atomic   (default, and the only way on a card or in the serial build) every
//!            addition is a Kokkos::atomic_add into the source array.  Correct, but the
//!            order in which two threads add to one cell is not fixed, so the last bits
//!            of the sources differ from run to run, as on a card.
//!   private  (<particles> deposit_threads = private, OpenMP build only) every thread
//!            adds, without atomics, to its own copy of the source array; the copies are
//!            then summed cell by cell in the order of the threads.  Kokkos gives each
//!            thread one contiguous range of particles (static schedule), so for a fixed
//!            number of threads the result is the same bit for bit from run to run; with
//!            one thread it equals the atomic result.  Memory: one source array (ten
//!            components on all cells of all MeshBlocks) per thread, zeroed and summed at
//!            every deposit; it pays where there are many additions per cell (several
//!            particles per cell, wide clouds) and costs where the mesh is much larger
//!            than the particle set.
//! The option is read only if it is present in the input file, so that the parameter
//! dump of a run that does not use it is unchanged.

#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>

#include "athena.hpp"
#include "parameter_input.hpp"

#if defined(KOKKOS_ENABLE_OPENMP)
#include <omp.h>
#endif

namespace nrpic {

//----------------------------------------------------------------------------------------
//! \struct DepositTarget
//! \brief the object the deposit kernel adds to (captured by value in the kernel)

struct DepositTarget {
  DvceArray5D<Real> tm;                 // the source array (zeroed before the deposit)
#if defined(KOKKOS_ENABLE_OPENMP)
  Kokkos::View<Real**, LayoutWrapper, HostMemSpace> priv;   // (thread, flattened cell)
  bool use_priv = false;
  std::size_t nv = 0, n3 = 0, n2 = 0, n1 = 0;               // extents of tm behind nmb
#endif

  KOKKOS_INLINE_FUNCTION
  void Add(const int m, const int n, const int k, const int j, const int i,
           const Real val) const {
#if defined(KOKKOS_ENABLE_OPENMP)
    if (use_priv) {
      const std::size_t idx = (((static_cast<std::size_t>(m)*nv + n)*n3 + k)*n2 + j)*n1 + i;
      priv(omp_get_thread_num(), idx) += val;
      return;
    }
#endif
    Kokkos::atomic_add(&tm(m,n,k,j,i), val);
  }
};

//----------------------------------------------------------------------------------------
//! \struct ThreadDeposit
//! \brief host state of the deposit target: the option and the private copies

struct ThreadDeposit {
  bool want_private = false;            // <particles> deposit_threads = private
#if defined(KOKKOS_ENABLE_OPENMP)
  Kokkos::View<Real**, LayoutWrapper, HostMemSpace> priv;
#endif

  //! reads <particles> deposit_threads (atomic | private) if it is in the input
  void Init(ParameterInput *pin) {
    want_private = false;
    if (!pin->DoesParameterExist("particles", "deposit_threads")) return;
    const std::string mode = pin->GetString("particles", "deposit_threads");
    if (mode.compare("private") == 0) {
      want_private = true;
    } else if (mode.compare("atomic") != 0) {
      std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__
                << std::endl << "<particles> deposit_threads = '" << mode
                << "' not recognized (atomic or private)" << std::endl;
      std::exit(EXIT_FAILURE);
    }
#if !defined(KOKKOS_ENABLE_OPENMP)
    if (want_private) {
      std::cout << "NRPIC deposit: deposit_threads = private applies to the OpenMP "
                << "build only; this executable adds atomically" << std::endl;
    }
#endif
  }

  //! the target of one deposit into tm; with private copies they are (re)allocated to
  //! the size of tm and zeroed, each by its own thread (first touch)
  DepositTarget Begin(const DvceArray5D<Real> &tm) {
    DepositTarget dep;
    dep.tm = tm;
#if defined(KOKKOS_ENABLE_OPENMP)
    if (want_private) {
      const std::size_t nt = static_cast<std::size_t>(DevExeSpace().concurrency());
      const std::size_t ntot = tm.size();
      if (priv.extent(0) != nt || priv.extent(1) != ntot) {
        priv = Kokkos::View<Real**, LayoutWrapper, HostMemSpace>(
                   Kokkos::view_alloc(Kokkos::WithoutInitializing, "nrpic_dep_priv"),
                   nt, ntot);
        std::cout << "NRPIC deposit: one private copy of the sources per thread ("
                  << nt << " threads, "
                  << static_cast<double>(nt*ntot*sizeof(Real))/1073741824.0 << " GiB)"
                  << std::endl;
      }
      auto pv = priv;
      Kokkos::parallel_for("nrpic_dep_zero",
                           Kokkos::RangePolicy<DevExeSpace>(0, static_cast<int>(nt)),
      KOKKOS_LAMBDA(const int t) {
        std::memset(static_cast<void*>(&pv(t,0)), 0, ntot*sizeof(Real));
      });
      dep.priv = priv;
      dep.use_priv = true;
      dep.nv = tm.extent(1); dep.n3 = tm.extent(2); dep.n2 = tm.extent(3);
      dep.n1 = tm.extent(4);
    }
#endif
    return dep;
  }

  //! after the particle loop: with private copies, tm = sum of the copies in the order
  //! of the threads (tm itself holds zeros until then)
  void End(const DepositTarget &dep) {
#if defined(KOKKOS_ENABLE_OPENMP)
    if (!dep.use_priv) return;
    auto pv = dep.priv;
    auto tm = dep.tm;
    const int nt = static_cast<int>(pv.extent(0));
    const std::size_t nv = dep.nv, n3 = dep.n3, n2 = dep.n2, n1 = dep.n1;
    par_for("nrpic_dep_merge", DevExeSpace(), 0, static_cast<int>(tm.extent(0))-1,
            0, static_cast<int>(nv)-1, 0, static_cast<int>(n3)-1,
            0, static_cast<int>(n2)-1, 0, static_cast<int>(n1)-1,
    KOKKOS_LAMBDA(const int m, const int n, const int k, const int j, const int i) {
      const std::size_t idx = (((static_cast<std::size_t>(m)*nv + n)*n3 + k)*n2 + j)*n1 + i;
      Real sum = 0.0;
      for (int t=0; t<nt; ++t) { sum += pv(t,idx); }
      tm(m,n,k,j,i) = sum;
    });
#else
    (void) dep;
#endif
  }
};

} // namespace nrpic
#endif // PARTICLES_NRPIC_THREADS_HPP_
