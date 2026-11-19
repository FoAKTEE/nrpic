//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_guard.cpp
//! \brief Stops a run whose spacetime fields are no longer finite.
//!
//! A run of the spacetime solver that has gone non-finite used to integrate the
//! non-finite state to its time limit and to exit with status zero.  The guard tests the
//! evolved fields of the spacetime solver after every cycle (and the initial data once);
//! when a value is not finite it prints where, writes <basename>.guard.txt, and tells
//! the driver to leave its loop.  The driver then writes every output once more (the
//! last state, for a post-mortem; a restart file of it cannot be continued) and the
//! executable exits with status kGuardStatus (3).
//!
//! The guard acts only in runs with the spacetime solver.  Input block <nrpic_guard>,
//! every option read only if present:
//!   stop_nonfinite       false switches the guard off (default: on)
//!   stop_chi_nonpositive true: also stop when the conformal factor chi is zero or
//!                        negative in a cell (default off: chi undershoots next to a
//!                        puncture, where the run survives it)
//!   stop_dt_below        > 0: also stop when the time step falls below this value
//!   stop_no_particles    true: also stop when a run that started with NRPIC particles
//!                        has none left
//!   check_dcycle         cycles between checks (default 1)
//! A check is one sum over the evolved fields, small against one evaluation of the
//! right-hand sides.

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <string>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "z4c/z4c.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_cosmo_ext.hpp"

namespace nrpic {

namespace {

struct GuardState {
  bool init = false;
  bool on = true;              // stop_nonfinite
  bool chi_nonpositive = false;
  Real dt_below = 0.0;
  bool no_particles = false;
  int dcycle = 1;
  bool had_particles = false;
  int status = 0;              // exit status of the executable
  std::string basename;
  Real last_good_time = -1.0;  // time of the last check that passed
  int last_good_cycle = -1;
};

GuardState gst;

} // namespace

//----------------------------------------------------------------------------------------
//! \fn void GuardInit
//! \brief reads <nrpic_guard>

void GuardInit(ParameterInput *pin, Mesh *pm) {
  gst = GuardState();
  gst.init = true;
  gst.basename = pin->GetString("job", "basename");
  if (pin->DoesParameterExist("nrpic_guard", "stop_nonfinite")) {
    gst.on = pin->GetBoolean("nrpic_guard", "stop_nonfinite");
  }
  if (pin->DoesParameterExist("nrpic_guard", "stop_chi_nonpositive")) {
    gst.chi_nonpositive = pin->GetBoolean("nrpic_guard", "stop_chi_nonpositive");
  }
  if (pin->DoesParameterExist("nrpic_guard", "stop_dt_below")) {
    gst.dt_below = pin->GetReal("nrpic_guard", "stop_dt_below");
  }
  if (pin->DoesParameterExist("nrpic_guard", "stop_no_particles")) {
    gst.no_particles = pin->GetBoolean("nrpic_guard", "stop_no_particles");
  }
  if (pin->DoesParameterExist("nrpic_guard", "check_dcycle")) {
    gst.dcycle = pin->GetInteger("nrpic_guard", "check_dcycle");
    if (gst.dcycle < 1) { gst.dcycle = 1; }
  }
}

//----------------------------------------------------------------------------------------
//! \fn int GuardExitStatus

int GuardExitStatus() {
  return gst.status;
}

//----------------------------------------------------------------------------------------
//! \fn bool GuardCheck
//! \brief true if the run must stop.  The state tested is that of Mesh::time.

bool GuardCheck(Mesh *pm) {
  if (!gst.init) return false;
  MeshBlockPack *pmbp = pm->pmb_pack;
  z4c::Z4c *pz4c = pmbp->pz4c;
  if (pz4c == nullptr) return false;
  if (!gst.on && !gst.chi_nonpositive && gst.dt_below <= 0.0 && !gst.no_particles) {
    return false;
  }
  particles::Particles *ppart = pmbp->ppart;
  const bool nrp = (ppart != nullptr && ppart->is_nrpic);
  if (nrp && pm->nprtcl_total > 0) { gst.had_particles = true; }
  if (pm->ncycle % gst.dcycle != 0) return false;

  auto &indcs = pm->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int n1 = indcs.nx1, n2 = indcs.nx2, n3 = indcs.nx3;
  const int nmb = pmbp->nmb_thispack;
  const int nvar = z4c::Z4c::nz4c;
  const int ichi = z4c::Z4c::I_Z4C_CHI;
  const int ncell = nmb*n3*n2*n1;
  auto u0 = pz4c->u0;

  // number of non-finite values, number of cells with chi <= 0, and the first cell
  // (in the order of the loop) of either kind
  std::int64_t nbad = 0, nchi = 0;
  int first = ncell, firstchi = ncell;
  const bool test_fin = gst.on, test_chi = gst.chi_nonpositive;
  if (test_fin || test_chi) {
    Kokkos::parallel_reduce("nrpic_guard", Kokkos::RangePolicy<DevExeSpace>(0, ncell),
    KOKKOS_LAMBDA(const int idx, std::int64_t &lbad, std::int64_t &lchi, int &lfirst,
                  int &lfirstchi) {
      const int m = idx/(n3*n2*n1);
      int rem = idx - m*(n3*n2*n1);
      const int k = rem/(n2*n1);
      rem -= k*(n2*n1);
      const int j = rem/n1;
      const int i = rem - j*n1;
      if (test_fin) {
        int nb = 0;
        for (int n=0; n<nvar; ++n) {
          if (!(Kokkos::isfinite(u0(m,n,k+ks,j+js,i+is)))) { ++nb; }
        }
        if (nb > 0) {
          lbad += nb;
          lfirst = (idx < lfirst) ? idx : lfirst;
        }
      }
      if (test_chi && !(u0(m,ichi,k+ks,j+js,i+is) > 0.0)) {
        lchi += 1;
        lfirstchi = (idx < lfirstchi) ? idx : lfirstchi;
      }
    }, Kokkos::Sum<std::int64_t>(nbad), Kokkos::Sum<std::int64_t>(nchi),
       Kokkos::Min<int>(first), Kokkos::Min<int>(firstchi));
  }
#if MPI_PARALLEL_ENABLED
  {
    std::int64_t buf[2] = {nbad, nchi};
    MPI_Allreduce(MPI_IN_PLACE, buf, 2, MPI_INT64_T, MPI_SUM, MPI_COMM_WORLD);
    nbad = buf[0]; nchi = buf[1];
  }
#endif

  std::string reason;
  if (test_fin && nbad > 0) {
    reason = "non-finite values in the evolved fields of the spacetime solver";
  } else if (test_chi && nchi > 0) {
    reason = "conformal factor chi not positive";
    first = firstchi;
  } else if (!(pm->dt == pm->dt) || !(pm->time == pm->time)) {
    reason = "time or time step is not a number";
  } else if (gst.dt_below > 0.0 && pm->ncycle > 0 && pm->dt < gst.dt_below) {
    reason = "time step below <nrpic_guard> stop_dt_below";
  } else if (gst.no_particles && gst.had_particles && pm->nprtcl_total == 0) {
    reason = "no particles left";
  }
  if (reason.empty()) {
    gst.last_good_time = pm->time;
    gst.last_good_cycle = pm->ncycle;
    return false;
  }

  // ---- diagnostic: per variable the number of non-finite values; the first cell
  gst.status = kGuardStatus;
  if (global_variable::my_rank != 0) return true;
  std::string fname = gst.basename + ".guard.txt";
  std::FILE *fp = std::fopen(fname.c_str(), "w");
  for (int pass=0; pass<2; ++pass) {
    std::FILE *out = (pass == 0) ? stdout : fp;
    if (out == nullptr) continue;
    std::fprintf(out, "\n### NRPIC guard: the run stops at time %.15e, cycle %d, dt %.6e\n"
                 "reason: %s\n", pm->time, pm->ncycle, pm->dt, reason.c_str());
    std::fprintf(out, "last check that passed: time %.15e, cycle %d\n",
                 gst.last_good_time, gst.last_good_cycle);
    std::fprintf(out, "MeshBlocks %d, cells %d, non-finite values %lld, cells with "
                 "chi <= 0 %lld%s\n", nmb, ncell,
                 static_cast<long long>(nbad), static_cast<long long>(nchi),
                 test_chi ? "" : " (not tested)");
  }
  if (nbad > 0) {
    for (int n=0; n<nvar; ++n) {
      std::int64_t cnt = 0;
      Kokkos::parallel_reduce("nrpic_guard_var",
                              Kokkos::RangePolicy<DevExeSpace>(0, ncell),
      KOKKOS_LAMBDA(const int idx, std::int64_t &lc) {
        const int m = idx/(n3*n2*n1);
        int rem = idx - m*(n3*n2*n1);
        const int k = rem/(n2*n1);
        rem -= k*(n2*n1);
        const int j = rem/n1;
        const int i = rem - j*n1;
        if (!(Kokkos::isfinite(u0(m,n,k+ks,j+js,i+is)))) { lc += 1; }
      }, Kokkos::Sum<std::int64_t>(cnt));
      if (cnt > 0) {
        for (int pass=0; pass<2; ++pass) {
          std::FILE *out = (pass == 0) ? stdout : fp;
          if (out == nullptr) continue;
          std::fprintf(out, "  %-12s %lld non-finite\n", z4c::Z4c::Z4c_names[n],
                       static_cast<long long>(cnt));
        }
      }
    }
  }
  if (first < ncell) {
    const int m = first/(n3*n2*n1);
    int rem = first - m*(n3*n2*n1);
    const int k = rem/(n2*n1);
    rem -= k*(n2*n1);
    const int j = rem/n1;
    const int i = rem - j*n1;
    auto &sz = pmbp->pmb->mb_size.h_view(m);
    const int mbs = pm->gids_eachrank[global_variable::my_rank];
    const int level = pm->lloc_eachmb[m + mbs].level - pm->root_level;
    auto uh = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(),
        Kokkos::subview(u0, m, Kokkos::ALL(), k+ks, j+js, i+is));
    for (int pass=0; pass<2; ++pass) {
      std::FILE *out = (pass == 0) ? stdout : fp;
      if (out == nullptr) continue;
      std::fprintf(out, "first such cell: MeshBlock %d (level %d, cell size %.6e), "
                   "cell (%d, %d, %d), position (%.6e, %.6e, %.6e)\n", m, level, sz.dx1,
                   i, j, k, sz.x1min + (i + 0.5)*sz.dx1, sz.x2min + (j + 0.5)*sz.dx2,
                   sz.x3min + (k + 0.5)*sz.dx3);
      std::fprintf(out, "fields there:");
      for (int n=0; n<nvar; ++n) {
        std::fprintf(out, " %s=%.6e", z4c::Z4c::Z4c_names[n], uh(n));
      }
      std::fprintf(out, "\n");
    }
  }
  if (nrp) {
    for (int pass=0; pass<2; ++pass) {
      std::FILE *out = (pass == 0) ? stdout : fp;
      if (out == nullptr) continue;
      std::fprintf(out, "particles: %d left, %d excised, %d escaped\n", pm->nprtcl_total,
                   ppart->n_excised, ppart->n_escaped);
    }
  }
  for (int pass=0; pass<2; ++pass) {
    std::FILE *out = (pass == 0) ? stdout : fp;
    if (out == nullptr) continue;
    std::fprintf(out, "The outputs written after this message hold the state that failed; "
                 "exit status %d.\n", kGuardStatus);
  }
  if (fp != nullptr) { std::fclose(fp); }
  std::fflush(stdout);
  return true;
}

} // namespace nrpic
