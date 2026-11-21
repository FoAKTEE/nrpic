//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_region.cpp
//! \brief Constraint norms inside and outside spheres, on any mesh (uniform, statically
//! or adaptively refined, periodic or not): <basename>.region.hst.
//!
//! The field dumps of the module exist on uniform meshes only, and the constraint
//! statistics (.cstat.hst) give maxima and cell means over the whole mesh.  A collapse
//! criterion of the kind "norm of the Hamiltonian constraint outside the horizon below
//! a fraction of the norm of 16 pi E there" needs norms over a region, with every leaf
//! cell weighted by its proper volume.  Options in <particles>, read only if present:
//!   region_dcycle            cycles between records (0 or absent: off)
//!   region_x1, _x2, _x3      centre of the spheres (default 0, 0, 0)
//!   region_radius1 .. 4      coordinate radii
//!   region_horizon           index n of a horizon finder: one more sphere, centred on
//!                            that finder, with region_horizon_factor (default 1) times
//!                            the mean coordinate radius of its last surface; radius
//!                            zero while no horizon is found (everything is outside)
//! In a periodic direction the distance to the centre is that to its nearest image.
//!
//! Record: time, cycle, then for the whole mesh
//!   V        proper volume, sum of sqrt(gamma) dV over the leaf cells
//!   K        proper-volume mean of K = Khat + 2 Theta
//!   alpha_V  proper-volume mean of the lapse
//!   alpha_c  coordinate-volume mean of the lapse
//!   H2       sqrt( <H^2> ),          <f> = sum f sqrt(gamma) dV / V of the region
//!   E2       sqrt( <(16 pi E)^2> )
//!   E1       <E>
//! and for every sphere its radius and, inside and then outside,
//!   V, H2, E2, E1, max |H|.
//! The bound of a threshold definition is H2/E2 of the region outside the horizon; the
//! norm of 16 pi (E - Ebar) follows from E2, E1 and a mean density Ebar.

#include <cmath>
#include <cstdio>
#include <iostream>
#include <string>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "coordinates/adm.hpp"
#include "z4c/z4c.hpp"
#include "z4c/tmunu.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_cosmo_ext.hpp"
// last: this header defines the macro NDIM, which collides with a member of Tmunu
#include "z4c/fastflow.hpp"

namespace particles {

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicRegionInit
//! \brief reads the options of the region diagnostic

void Particles::NrpicRegionInit(ParameterInput *pin) {
  region = NrpicRegionOptions();
  if (!pin->DoesParameterExist("particles", "region_dcycle")) return;
  region.dcycle = pin->GetInteger("particles", "region_dcycle");
  if (pin->DoesParameterExist("particles", "region_x1")) {
    region.center[0] = pin->GetReal("particles", "region_x1");
  }
  if (pin->DoesParameterExist("particles", "region_x2")) {
    region.center[1] = pin->GetReal("particles", "region_x2");
  }
  if (pin->DoesParameterExist("particles", "region_x3")) {
    region.center[2] = pin->GetReal("particles", "region_x3");
  }
  region.nsphere = 0;
  for (int n=1; n<=4; ++n) {
    const std::string key = "region_radius" + std::to_string(n);
    if (!pin->DoesParameterExist("particles", key)) break;
    region.radius[region.nsphere++] = pin->GetReal("particles", key);
  }
  if (pin->DoesParameterExist("particles", "region_horizon")) {
    region.horizon = pin->GetInteger("particles", "region_horizon");
  }
  if (pin->DoesParameterExist("particles", "region_horizon_factor")) {
    region.horizon_factor = pin->GetReal("particles", "region_horizon_factor");
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicWriteRegion
//! \brief appends one record to <basename>.region.hst

void Particles::NrpicWriteRegion(Real time, int ncycle, bool header) {
  if (pmy_pack->pz4c == nullptr || !nropt.deposit) return;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int n1 = indcs.nx1, n2 = indcs.nx2, n3 = indcs.nx3;
  const int nmb = pmy_pack->nmb_thispack;
  const int ncell = nmb*n3*n2*n1;
  auto con = pmy_pack->pz4c->con;
  auto adm = pmy_pack->padm->adm;
  auto u0 = pmy_pack->pz4c->u0;
  auto tm = pmy_pack->ptmunu->u_tmunu;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int ikhat = z4c::Z4c::I_Z4C_KHAT, itheta = z4c::Z4c::I_Z4C_THETA;
  const int ialp = z4c::Z4c::I_Z4C_ALPHA;

  // ---- whole mesh
  Real vol = 0.0, cvol = 0.0, ksum = 0.0, asum = 0.0, acsum = 0.0;
  Real h2 = 0.0, e2 = 0.0, e1 = 0.0;
  Kokkos::parallel_reduce("nrpic_region0", Kokkos::RangePolicy<DevExeSpace>(0, ncell),
  KOKKOS_LAMBDA(const int idx, Real &lv, Real &lcv, Real &lk, Real &la, Real &lac,
                Real &lh2, Real &le2, Real &le1) {
    int m = idx/(n3*n2*n1);
    int rem = idx - m*(n3*n2*n1);
    int k = rem/(n2*n1);
    rem -= k*(n2*n1);
    int j = rem/n1;
    int i = rem - j*n1;
    k += ks; j += js; i += is;
    const Real det = adm::SpatialDet(adm.g_dd(m,0,0,k,j,i), adm.g_dd(m,0,1,k,j,i),
                                     adm.g_dd(m,0,2,k,j,i), adm.g_dd(m,1,1,k,j,i),
                                     adm.g_dd(m,1,2,k,j,i), adm.g_dd(m,2,2,k,j,i));
    const Real dv = sz(m).dx1*sz(m).dx2*sz(m).dx3;
    const Real w = sqrt(fabs(det))*dv;
    const Real h = con.H(m,k,j,i);
    const Real e = tm(m,Tmunu::I_Tmunu_E,k,j,i);
    lv += w;
    lcv += dv;
    lk += w*(u0(m,ikhat,k,j,i) + 2.0*u0(m,itheta,k,j,i));
    la += w*u0(m,ialp,k,j,i);
    lac += dv*u0(m,ialp,k,j,i);
    lh2 += w*h*h;
    le2 += w*SQR(16.0*M_PI*e);
    le1 += w*e;
  }, Kokkos::Sum<Real>(vol), Kokkos::Sum<Real>(cvol), Kokkos::Sum<Real>(ksum),
     Kokkos::Sum<Real>(asum), Kokkos::Sum<Real>(acsum), Kokkos::Sum<Real>(h2),
     Kokkos::Sum<Real>(e2), Kokkos::Sum<Real>(e1));

  // ---- spheres: the fixed ones, then the horizon
  int nsph = region.nsphere;
  Real cen[5][3], rad[5];
  for (int s=0; s<nsph; ++s) {
    for (int d=0; d<3; ++d) { cen[s][d] = region.center[d]; }
    rad[s] = region.radius[s];
  }
  if (region.horizon >= 0 &&
      region.horizon < static_cast<int>(pmy_pack->pz4c->pfastflow.size())) {
    auto &pah = pmy_pack->pz4c->pfastflow[region.horizon];
    for (int d=0; d<3; ++d) { cen[nsph][d] = pah->center[d]; }
    const Real rm = pah->MeanRadius();
    rad[nsph] = (pah->ah_found && rm > 0.0 && rm < 1.0e300)
                ? region.horizon_factor*rm : 0.0;
    ++nsph;
  }
  const bool per[3] = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  Real res[5][2][5];
  for (int s=0; s<nsph; ++s) {
    const Real cx = cen[s][0], cy = cen[s][1], cz = cen[s][2];
    const Real r2 = rad[s]*rad[s];
    for (int side=0; side<2; ++side) {
      Real v = 0.0, sh2 = 0.0, se2 = 0.0, se1 = 0.0, hmax = 0.0;
      Kokkos::parallel_reduce("nrpic_region", Kokkos::RangePolicy<DevExeSpace>(0, ncell),
      KOKKOS_LAMBDA(const int idx, Real &lv, Real &lh2, Real &le2, Real &le1,
                    Real &lhmax) {
        int m = idx/(n3*n2*n1);
        int rem = idx - m*(n3*n2*n1);
        int k = rem/(n2*n1);
        rem -= k*(n2*n1);
        int j = rem/n1;
        int i = rem - j*n1;
        Real dx = sz(m).x1min + (i + 0.5)*sz(m).dx1 - cx;
        Real dy = sz(m).x2min + (j + 0.5)*sz(m).dx2 - cy;
        Real dz = sz(m).x3min + (k + 0.5)*sz(m).dx3 - cz;
        if (per[0]) { dx = nrpic::MinImage(dx, dlen[0]); }
        if (per[1]) { dy = nrpic::MinImage(dy, dlen[1]); }
        if (per[2]) { dz = nrpic::MinImage(dz, dlen[2]); }
        const bool inside = (dx*dx + dy*dy + dz*dz < r2);
        if (inside != (side == 0)) return;
        k += ks; j += js; i += is;
        const Real det = adm::SpatialDet(adm.g_dd(m,0,0,k,j,i), adm.g_dd(m,0,1,k,j,i),
                                         adm.g_dd(m,0,2,k,j,i), adm.g_dd(m,1,1,k,j,i),
                                         adm.g_dd(m,1,2,k,j,i), adm.g_dd(m,2,2,k,j,i));
        const Real w = sqrt(fabs(det))*sz(m).dx1*sz(m).dx2*sz(m).dx3;
        const Real h = con.H(m,k,j,i);
        const Real e = tm(m,Tmunu::I_Tmunu_E,k,j,i);
        lv += w;
        lh2 += w*h*h;
        le2 += w*SQR(16.0*M_PI*e);
        le1 += w*e;
        lhmax = fmax(lhmax, fabs(h));
      }, Kokkos::Sum<Real>(v), Kokkos::Sum<Real>(sh2), Kokkos::Sum<Real>(se2),
         Kokkos::Sum<Real>(se1), Kokkos::Max<Real>(hmax));
      res[s][side][0] = v;
      res[s][side][1] = (v > 0.0) ? sqrt(sh2/v) : 0.0;
      res[s][side][2] = (v > 0.0) ? sqrt(se2/v) : 0.0;
      res[s][side][3] = (v > 0.0) ? se1/v : 0.0;
      res[s][side][4] = hmax;
    }
  }

  std::string fname = nr_basename + ".region.hst";
  std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
  if (fp == nullptr) {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "cannot open " << fname << std::endl;
    std::exit(EXIT_FAILURE);
  }
  if (header) {
    std::fprintf(fp, "# NRPIC region diagnostic: norms weighted with the proper volume of "
                 "the leaf cells; H2 = sqrt(<H^2>), E2 = sqrt(<(16 pi E)^2>), E1 = <E>\n");
    std::fprintf(fp, "# [1]=time [2]=ncycle [3]=V [4]=mean_K [5]=mean_alpha_V "
                 "[6]=mean_alpha_coord [7]=H2 [8]=E2 [9]=E1");
    int c = 10;
    for (int s=0; s<nsph; ++s) {
      const char *tag = (s < region.nsphere) ? "s" : "h";
      const int id = (s < region.nsphere) ? s + 1 : region.horizon;
      std::fprintf(fp, " [%d]=radius_%s%d", c++, tag, id);
      for (int side=0; side<2; ++side) {
        const char *io = (side == 0) ? "in" : "out";
        std::fprintf(fp, " [%d]=V_%s_%s%d [%d]=H2_%s_%s%d [%d]=E2_%s_%s%d "
                     "[%d]=E1_%s_%s%d [%d]=Hmax_%s_%s%d", c, io, tag, id, c+1, io, tag,
                     id, c+2, io, tag, id, c+3, io, tag, id, c+4, io, tag, id);
        c += 5;
      }
    }
    std::fprintf(fp, "\n");
  }
  std::fprintf(fp, "%.15e %d %.15e %.15e %.15e %.15e %.15e %.15e %.15e", time, ncycle, vol,
               (vol > 0.0) ? ksum/vol : 0.0, (vol > 0.0) ? asum/vol : 0.0,
               (cvol > 0.0) ? acsum/cvol : 0.0, (vol > 0.0) ? sqrt(h2/vol) : 0.0,
               (vol > 0.0) ? sqrt(e2/vol) : 0.0, (vol > 0.0) ? e1/vol : 0.0);
  for (int s=0; s<nsph; ++s) {
    std::fprintf(fp, " %.15e", rad[s]);
    for (int side=0; side<2; ++side) {
      for (int q=0; q<5; ++q) { std::fprintf(fp, " %.15e", res[s][side][q]); }
    }
  }
  std::fprintf(fp, "\n");
  std::fclose(fp);
}

} // namespace particles
