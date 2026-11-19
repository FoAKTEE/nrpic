//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file z4c_newdt.cpp
//! \brief function to compute z4c timestep across all MeshBlock(s) in a MeshBlockPack

#include <math.h>

#include <limits>
#include <iostream>
#include <algorithm>

#include "athena.hpp"
#include "mesh/mesh.hpp"
#include "driver/driver.hpp"
#include "z4c.hpp"

namespace z4c {

//----------------------------------------------------------------------------------------
//! \fn void Z4c::NewTimeStep()
//! \brief calculate the minimum timestep within a MeshBlockPack for z4c problems

TaskStatus Z4c::NewTimeStep(Driver *pdriver, int stage) {
  if (stage != (pdriver->nexp_stages)) {
    return TaskStatus::complete; // only execute last stage
  }

  auto &indcs = pmy_pack->pmesh->mb_indcs;
  int nx1 = indcs.nx1;
  int nx2 = indcs.nx2;
  int nx3 = indcs.nx3;

  Real dt1 = std::numeric_limits<float>::max();
  Real dt2 = std::numeric_limits<float>::max();
  Real dt3 = std::numeric_limits<float>::max();

  // capture class variables for kernel
  auto &mbsize = pmy_pack->pmb->mb_size;
  const int nmkji = (pmy_pack->nmb_thispack)*nx3*nx2*nx1;
  const int nkji = nx3*nx2*nx1;

  Kokkos::parallel_reduce("Z4c dt",Kokkos::RangePolicy<>(DevExeSpace(), 0, nmkji),
  KOKKOS_LAMBDA(const int &idx, Real &min_dt1, Real &min_dt2, Real &min_dt3) {
    // compute m,k,j,i indices of thread and call function
    int m = (idx)/nkji;

    min_dt1 = fmin((mbsize.d_view(m).dx1), min_dt1);
    min_dt2 = fmin((mbsize.d_view(m).dx2), min_dt2);
    min_dt3 = fmin((mbsize.d_view(m).dx3), min_dt3);
  }, Kokkos::Min<Real>(dt1), Kokkos::Min<Real>(dt2),Kokkos::Min<Real>(dt3));

  // compute minimum of dt1/dt2/dt3 for 1D/2D/3D problems
  dtnew = dt1;
  if (pmy_pack->pmesh->multi_d) { dtnew = std::min(dtnew, dt2); }
  if (pmy_pack->pmesh->three_d) { dtnew = std::min(dtnew, dt3); }

  // <z4c> dt_lightspeed: the step limit above assumes a coordinate speed of light of
  // one; here it is taken from the fields
  if (dt_lightspeed > 0.0 && pmy_pack->pmesh->three_d) {
    dtnew = std::min(dtnew, dt_lightspeed*LightSpeedTimeStep());
  }

  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! n Real Z4c::LightSpeedTimeStep()
//! rief smallest value over the cells and the three directions of dx_d / c_d with the
//! coordinate speed of light along the direction d,
//!   c_d = alpha sqrt(gamma^dd) + |beta^d|,   gamma^dd = chi^(-4/N) gtilde^dd
//! (chi = psi^N), from the evolved fields.  In the conformal-time gauge of the
//! homogeneous universe c_d = 1; in geodesic slicing of a collapsing region and with a
//! lapse that grows faster than the scale factor it exceeds one.  Cells whose conformal
//! factor is not positive, or whose fields are not finite, are skipped.

Real Z4c::LightSpeedTimeStep() {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int n1 = indcs.nx1, n2 = indcs.nx2, n3 = indcs.nx3;
  const int ncell = (pmy_pack->nmb_thispack)*n3*n2*n1;
  auto &mbsize = pmy_pack->pmb->mb_size;
  auto u = u0;
  const int ial = I_Z4C_ALPHA, ichi = I_Z4C_CHI, ibx = I_Z4C_BETAX, igxx = I_Z4C_GXX;
  const Real expo = -4.0/opt.chi_psi_power;
  Real dtl = std::numeric_limits<float>::max();
  Real cmax = 0.0;
  Kokkos::parallel_reduce("Z4c dt light", Kokkos::RangePolicy<>(DevExeSpace(), 0, ncell),
  KOKKOS_LAMBDA(const int &idx, Real &min_dt, Real &max_c) {
    int m = idx/(n3*n2*n1);
    int rem = idx - m*(n3*n2*n1);
    int k = rem/(n2*n1);
    rem -= k*(n2*n1);
    int j = rem/n1;
    int i = rem - j*n1;
    k += ks; j += js; i += is;
    const Real gxx = u(m,igxx,k,j,i), gxy = u(m,igxx+1,k,j,i), gxz = u(m,igxx+2,k,j,i);
    const Real gyy = u(m,igxx+3,k,j,i), gyz = u(m,igxx+4,k,j,i), gzz = u(m,igxx+5,k,j,i);
    const Real det = gxx*(gyy*gzz - gyz*gyz) - gxy*(gxy*gzz - gyz*gxz)
                     + gxz*(gxy*gyz - gyy*gxz);
    const Real chi = u(m,ichi,k,j,i);
    const Real alp = u(m,ial,k,j,i);
    if (!(det > 0.0) || !(chi > 0.0) || !(Kokkos::isfinite(alp + chi + det))) return;
    // diagonal of the inverse conformal metric
    const Real gi[3] = {(gyy*gzz - gyz*gyz)/det, (gxx*gzz - gxz*gxz)/det,
                        (gxx*gyy - gxy*gxy)/det};
    const Real fac = fabs(alp)*sqrt(pow(chi, expo));
    const Real dx[3] = {mbsize.d_view(m).dx1, mbsize.d_view(m).dx2, mbsize.d_view(m).dx3};
    for (int d=0; d<3; ++d) {
      const Real c = fac*sqrt(fmax(gi[d], 0.0)) + fabs(u(m,ibx+d,k,j,i));
      if (c > 0.0 && Kokkos::isfinite(c)) {
        min_dt = fmin(min_dt, dx[d]/c);
        max_c = fmax(max_c, c);
      }
    }
  }, Kokkos::Min<Real>(dtl), Kokkos::Max<Real>(cmax));
  cmax_light = cmax;
  return dtl;
}
} // namespace z4c
