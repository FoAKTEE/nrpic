//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_geodesic.cpp
//! \brief Problem generator for test particles in a fixed Kerr spacetime.
//!
//! The particles are created by the particle module (<particles> particle_file or the
//! inline list).  With <particles> metric = mesh and an <adm> block, the mesh carries
//! the Kerr metric in Cartesian Kerr-Schild coordinates sampled at the cell centres,
//! with mass and spin taken from <particles> bh_mass and bh_spin; the pushers then read
//! it through the cubic Hermite reconstruction.  With an analytic or lattice metric
//! source the mesh is not used.  <problem> metric_kind selects two other fixed metrics
//! on the mesh instead: homogeneous (constant lapse and spatial metric) and
//! static_conformal (conformally flat, optionally with a periodic modulation of lapse,
//! conformal factor and shift).

#include <cmath>
#include <iostream>

#include "athena.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "coordinates/adm.hpp"
#include "coordinates/cell_locations.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_metrics.hpp"
#include "pgen/pgen.hpp"

namespace {
// Kerr-Schild data on the mesh from the same functor that the analytic pushers use
void NrpicSetKerrSchild(MeshBlockPack *pmbp) {
  auto &indcs = pmbp->pmesh->mb_indcs;
  auto &size = pmbp->pmb->mb_size;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ng = indcs.ng;
  const int n1 = indcs.nx1 + 2*ng, n2 = indcs.nx2 + 2*ng, n3 = indcs.nx3 + 2*ng;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmb = pmbp->nmb_thispack;
  const Real mass = pmbp->ppart->nropt.mass;
  const Real spin = pmbp->ppart->nropt.spin;
  auto &adm = pmbp->padm->adm;
  par_for("nrpic_kerr_schild", DevExeSpace(), 0, nmb-1, 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    Real x[3];
    x[0] = CellCenterX(i-is, nx1, size.d_view(m).x1min, size.d_view(m).x1max);
    x[1] = CellCenterX(j-js, nx2, size.d_view(m).x2min, size.d_view(m).x2max);
    x[2] = CellCenterX(k-ks, nx3, size.d_view(m).x3min, size.d_view(m).x3max);
    nrpic::KerrSchildCart ks_met{mass, spin};
    nrpic::AdmPoint p;
    ks_met(0, x, p);
    adm.alpha(m,k,j,i) = p.alp;
    for (int a=0; a<3; ++a) {
      adm.beta_u(m,a,k,j,i) = p.beta[a];
      for (int b=a; b<3; ++b) {
        adm.g_dd(m,a,b,k,j,i) = p.g[a][b];
      }
    }
    Real det = adm::SpatialDet(p.g[0][0], p.g[0][1], p.g[0][2], p.g[1][1], p.g[1][2],
                               p.g[2][2]);
    adm.psi4(m,k,j,i) = pow(det, 1.0/3.0);
  });
}

// Static homogeneous metric on the mesh: constant lapse and constant spatial metric,
// zero shift (flat spacetime in oblique, rescaled coordinates).  Selected with
// <problem> metric_kind = homogeneous and set by alpha0, gxx, gxy, gxz, gyy, gyz, gzz.
// It exists to test operators that work in the orthonormal frame of the normal
// observers (the collision operator) where the lapse, the volume element and the triad
// are not trivial but the exact solution is known.
Real homog_alpha0 = 1.0;
Real homog_g[6] = {1.0, 0.0, 0.0, 1.0, 0.0, 1.0};   // xx, xy, xz, yy, yz, zz

void NrpicSetHomogeneous(MeshBlockPack *pmbp) {
  auto &indcs = pmbp->pmesh->mb_indcs;
  const int ng = indcs.ng;
  const int n1 = indcs.nx1 + 2*ng, n2 = indcs.nx2 + 2*ng, n3 = indcs.nx3 + 2*ng;
  const int nmb = pmbp->nmb_thispack;
  const Real alp = homog_alpha0;
  const Real gxx = homog_g[0], gxy = homog_g[1], gxz = homog_g[2];
  const Real gyy = homog_g[3], gyz = homog_g[4], gzz = homog_g[5];
  const Real det = adm::SpatialDet(gxx, gxy, gxz, gyy, gyz, gzz);
  auto &adm = pmbp->padm->adm;
  par_for("nrpic_homogeneous", DevExeSpace(), 0, nmb-1, 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    adm.alpha(m,k,j,i) = alp;
    adm.beta_u(m,0,k,j,i) = 0.0;
    adm.beta_u(m,1,k,j,i) = 0.0;
    adm.beta_u(m,2,k,j,i) = 0.0;
    adm.g_dd(m,0,0,k,j,i) = gxx;
    adm.g_dd(m,0,1,k,j,i) = gxy;
    adm.g_dd(m,0,2,k,j,i) = gxz;
    adm.g_dd(m,1,1,k,j,i) = gyy;
    adm.g_dd(m,1,2,k,j,i) = gyz;
    adm.g_dd(m,2,2,k,j,i) = gzz;
    adm.psi4(m,k,j,i) = pow(det, 1.0/3.0);
  });
}

// Static conformally flat metric on the mesh with a periodic modulation:
//   alpha = alpha0 (1 + alpha_amp cos(phi)),   psi = psi0 (1 + psi_amp cos(phi)),
//   gamma_ij = psi^4 delta_ij,   beta^x = shift_amp sin(phi),   beta^y = beta^z = 0,
//   phi = 2 pi [ n1 (x - x1min)/L1 + n2 (y - x2min)/L2 + n3 (z - x3min)/L3 ]
// with integer mode numbers n1, n2, n3 (periodic in a periodic box).  Selected with
// <problem> metric_kind = static_conformal.  It is not a solution of the Einstein
// equations and needs none: nothing evolves it.  It is a test bed for the particle
// module in a metric that is exactly known, time independent and not flat: with all
// amplitudes zero a constant lapse and conformal factor (collision rate in a curved
// frame); with amplitudes a static potential well in which alpha W - beta^i u_i of
// every particle is conserved by the geodesic motion and the distribution
// f = F(alpha W - beta^i u_i) is an exact equilibrium, also with collisions.
Real sc_alpha0 = 1.0, sc_psi0 = 1.0;
Real sc_alpha_amp = 0.0, sc_psi_amp = 0.0, sc_shift_amp = 0.0;
Real sc_k[3] = {0.0, 0.0, 0.0};       // 2 pi n_d / L_d
Real sc_x0[3] = {0.0, 0.0, 0.0};      // lower edge of the mesh

void NrpicSetStaticConformal(MeshBlockPack *pmbp) {
  auto &indcs = pmbp->pmesh->mb_indcs;
  auto &size = pmbp->pmb->mb_size;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ng = indcs.ng;
  const int n1 = indcs.nx1 + 2*ng, n2 = indcs.nx2 + 2*ng, n3 = indcs.nx3 + 2*ng;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmb = pmbp->nmb_thispack;
  const Real alp0 = sc_alpha0, psi0 = sc_psi0;
  const Real aamp = sc_alpha_amp, pamp = sc_psi_amp, samp = sc_shift_amp;
  const Real kx = sc_k[0], ky = sc_k[1], kz = sc_k[2];
  const Real x0 = sc_x0[0], y0 = sc_x0[1], z0 = sc_x0[2];
  auto &adm = pmbp->padm->adm;
  par_for("nrpic_static_conformal", DevExeSpace(), 0, nmb-1, 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    const Real x = CellCenterX(i-is, nx1, size.d_view(m).x1min, size.d_view(m).x1max);
    const Real y = CellCenterX(j-js, nx2, size.d_view(m).x2min, size.d_view(m).x2max);
    const Real z = CellCenterX(k-ks, nx3, size.d_view(m).x3min, size.d_view(m).x3max);
    const Real phi = kx*(x - x0) + ky*(y - y0) + kz*(z - z0);
    const Real cs = cos(phi);
    const Real psi = psi0*(1.0 + pamp*cs);
    const Real psi4 = (psi*psi)*(psi*psi);
    adm.alpha(m,k,j,i) = alp0*(1.0 + aamp*cs);
    adm.beta_u(m,0,k,j,i) = samp*sin(phi);
    adm.beta_u(m,1,k,j,i) = 0.0;
    adm.beta_u(m,2,k,j,i) = 0.0;
    adm.g_dd(m,0,0,k,j,i) = psi4;
    adm.g_dd(m,0,1,k,j,i) = 0.0;
    adm.g_dd(m,0,2,k,j,i) = 0.0;
    adm.g_dd(m,1,1,k,j,i) = psi4;
    adm.g_dd(m,1,2,k,j,i) = 0.0;
    adm.g_dd(m,2,2,k,j,i) = psi4;
    adm.psi4(m,k,j,i) = psi4;
  });
}
} // namespace

//----------------------------------------------------------------------------------------
//! \fn void ProblemGenerator::NrpicGeodesic
//! \brief test particles in a fixed Kerr spacetime

void ProblemGenerator::NrpicGeodesic(ParameterInput *pin, const bool restart) {
  MeshBlockPack *pmbp = pmy_mesh_->pmb_pack;
  if (pmbp->ppart == nullptr || !(pmbp->ppart->is_nrpic)) {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "nrpic_geodesic requires <particles> particle_type = nrpic" << std::endl;
    exit(EXIT_FAILURE);
  }
  if (pmbp->pz4c != nullptr) {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "nrpic_geodesic uses a fixed metric and cannot be run with <z4c>"
              << std::endl;
    exit(EXIT_FAILURE);
  }
  // The mesh metric is static and is not stored in restart files in a form that the
  // particle module could reuse, so it is set on restarts as well.
  if (pmbp->padm != nullptr) {
    // (the option is read only if present, so that existing inputs are unchanged)
    if (pin->DoesParameterExist("problem", "metric_kind") &&
        pin->GetString("problem", "metric_kind").compare("homogeneous") == 0) {
      homog_alpha0 = pin->GetOrAddReal("problem", "alpha0", 1.0);
      homog_g[0] = pin->GetOrAddReal("problem", "gxx", 1.0);
      homog_g[1] = pin->GetOrAddReal("problem", "gxy", 0.0);
      homog_g[2] = pin->GetOrAddReal("problem", "gxz", 0.0);
      homog_g[3] = pin->GetOrAddReal("problem", "gyy", 1.0);
      homog_g[4] = pin->GetOrAddReal("problem", "gyz", 0.0);
      homog_g[5] = pin->GetOrAddReal("problem", "gzz", 1.0);
      const Real det = adm::SpatialDet(homog_g[0], homog_g[1], homog_g[2], homog_g[3],
                                       homog_g[4], homog_g[5]);
      if (!(homog_alpha0 > 0.0) || !(det > 0.0) || !(homog_g[0] > 0.0) ||
          !(homog_g[0]*homog_g[3] - homog_g[1]*homog_g[1] > 0.0)) {
        std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__
                  << std::endl << "<problem> metric_kind = homogeneous needs a positive "
                  << "lapse and a positive-definite spatial metric" << std::endl;
        exit(EXIT_FAILURE);
      }
      pmbp->padm->SetADMVariables = &NrpicSetHomogeneous;
      NrpicSetHomogeneous(pmbp);
      return;
    }
    if (pin->DoesParameterExist("problem", "metric_kind") &&
        pin->GetString("problem", "metric_kind").compare("static_conformal") == 0) {
      Mesh *pm = pmy_mesh_;
      sc_alpha0 = pin->GetOrAddReal("problem", "alpha0", 1.0);
      sc_psi0 = pin->GetOrAddReal("problem", "psi0", 1.0);
      sc_alpha_amp = pin->GetOrAddReal("problem", "alpha_amp", 0.0);
      sc_psi_amp = pin->GetOrAddReal("problem", "psi_amp", 0.0);
      sc_shift_amp = pin->GetOrAddReal("problem", "shift_amp", 0.0);
      const int mode[3] = {pin->GetOrAddInteger("problem", "mode_n1", 1),
                           pin->GetOrAddInteger("problem", "mode_n2", 0),
                           pin->GetOrAddInteger("problem", "mode_n3", 0)};
      const Real twopi = 6.283185307179586476925286766559;
      sc_x0[0] = pm->mesh_size.x1min;
      sc_x0[1] = pm->mesh_size.x2min;
      sc_x0[2] = pm->mesh_size.x3min;
      sc_k[0] = twopi*mode[0]/(pm->mesh_size.x1max - pm->mesh_size.x1min);
      sc_k[1] = twopi*mode[1]/(pm->mesh_size.x2max - pm->mesh_size.x2min);
      sc_k[2] = twopi*mode[2]/(pm->mesh_size.x3max - pm->mesh_size.x3min);
      if (!(sc_alpha0 > 0.0) || !(sc_psi0 > 0.0) || !(fabs(sc_alpha_amp) < 1.0) ||
          !(fabs(sc_psi_amp) < 1.0)) {
        std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__
                  << std::endl << "<problem> metric_kind = static_conformal needs "
                  << "alpha0 > 0, psi0 > 0 and amplitudes below one" << std::endl;
        exit(EXIT_FAILURE);
      }
      pmbp->padm->SetADMVariables = &NrpicSetStaticConformal;
      NrpicSetStaticConformal(pmbp);
      return;
    }
    pmbp->padm->SetADMVariables = &NrpicSetKerrSchild;
    NrpicSetKerrSchild(pmbp);
  }
  return;
}
