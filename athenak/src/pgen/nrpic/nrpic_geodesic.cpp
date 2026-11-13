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
//! source the mesh is not used.

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
    pmbp->padm->SetADMVariables = &NrpicSetKerrSchild;
    NrpicSetKerrSchild(pmbp);
  }
  return;
}
