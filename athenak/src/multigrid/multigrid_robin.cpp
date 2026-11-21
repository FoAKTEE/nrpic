//========================================================================================
// Athena++ astrophysical MHD code
// Copyright(C) 2014 James M. Stone <jmstone@princeton.edu> and other code contributors
// Licensed under the 3-clause BSD License, see LICENSE file for details
//========================================================================================
//! \file multigrid_robin.cpp
//! \brief Robin faces of the multigrid solver (<gravity> mg_bc = robin): the solution
//! falls off as 1/r about a centre, r u = const across the face (MGRobinFill in
//! multigrid.hpp).  The condition is linear and homogeneous and the solver is a full
//! approximation scheme, so the same fill serves every level of the MeshBlocks and of
//! the root grid.  Octets (refined meshes) are not covered: the driver of the gravity
//! module refuses mg_bc = robin on a multilevel mesh.
//! Used by the initial-data solver of the particle module (particles/nrpic_idsolve.cpp)
//! for the conformal factor, psi - 1 proportional to 1/r at the faces of the mesh.

#include "../athena.hpp"
#include "../mesh/mesh.hpp"
#include "../mesh/meshblock_pack.hpp"
#include "multigrid.hpp"

//----------------------------------------------------------------------------------------
//! \fn void MultigridDriver::RobinBoundaryBlocks()
//! \brief Robin ghost cells of the MeshBlocks at the current level of pmg; called at the
//! end of PhysicalBoundary, whose fill of these faces it replaces

void MultigridDriver::RobinBoundaryBlocks() {
  DvceArray5D<Real> u = pmg->GetCurrentData();
  const int nvar = u.extent_int(1);
  const int shift = pmg->GetLevelShift();
  const int ngh = pmg->GetGhostCells();
  const int nc = pmg->GetSize() >> shift;
  if (nc < 1) return;
  const int nmb = pmy_pack_->nmb_thispack;
  auto mb_bcs = pmy_pack_->pmb->mb_bcs.d_view;
  auto mb_size = pmy_pack_->pmb->mb_size.d_view;
  bool rob[6];
  for (int f = 0; f < 6; ++f) {
    rob[f] = (mg_mesh_bcs_[f] == BoundaryFlag::mg_robin);
  }
  const Real xo = robin_o_[0], yo = robin_o_[1], zo = robin_o_[2];
  const Real rnc = static_cast<Real>(nc);

  Kokkos::parallel_for("MGRobinBlocks", Kokkos::RangePolicy<DevExeSpace>(0, nmb),
  KOKKOS_LAMBDA(const int m) {
    bool face[6];
    bool any = false;
    for (int f = 0; f < 6; ++f) {
      face[f] = rob[f] && (mb_bcs(m,f) != BoundaryFlag::block) &&
                (mb_bcs(m,f) != BoundaryFlag::periodic);
      any = any || face[f];
    }
    if (any) {
      const Real d1 = (mb_size(m).x1max - mb_size(m).x1min)/rnc;
      const Real d2 = (mb_size(m).x2max - mb_size(m).x2min)/rnc;
      const Real d3 = (mb_size(m).x3max - mb_size(m).x3min)/rnc;
      MGRobinFill(u, m, nvar, ngh, nc, nc, nc, mb_size(m).x1min - xo,
                  mb_size(m).x2min - yo, mb_size(m).x3min - zo, d1, d2, d3, face);
    }
  });
}

//----------------------------------------------------------------------------------------
//! \fn void MultigridDriver::RobinBoundaryRoot()
//! \brief Robin ghost cells of the root grid at its current level; called at the end of
//! MGRootBoundary, which leaves these faces untouched

void MultigridDriver::RobinBoundaryRoot() {
  const int ll = mgroot_->GetNumberOfLevels() - 1 - mgroot_->GetCurrentLevel();
  const int ngh = mgroot_->ngh_;
  const int n1 = (mgroot_->indcs_.nx1 >> ll);
  const int n2 = (mgroot_->indcs_.nx2 >> ll);
  const int n3 = (mgroot_->indcs_.nx3 >> ll);
  if (n1 < 1 || n2 < 1 || n3 < 1) return;
  const RegionSize &ms = pmy_mesh_->mesh_size;
  const Real d1 = (ms.x1max - ms.x1min)/static_cast<Real>(n1);
  const Real d2 = (ms.x2max - ms.x2min)/static_cast<Real>(n2);
  const Real d3 = (ms.x3max - ms.x3min)/static_cast<Real>(n3);
  const Real x1 = ms.x1min - robin_o_[0];
  const Real x2 = ms.x2min - robin_o_[1];
  const Real x3 = ms.x3min - robin_o_[2];
  bool rob[6];
  for (int f = 0; f < 6; ++f) {
    rob[f] = (mg_mesh_bcs_[f] == BoundaryFlag::mg_robin);
  }
  if (!mgroot_->on_host_) {
    auto u = mgroot_->GetCurrentData();
    const int nvar = u.extent_int(1);
    Kokkos::parallel_for("MGRobinRoot", Kokkos::RangePolicy<DevExeSpace>(0, 1),
    KOKKOS_LAMBDA(const int) {
      bool face[6];
      for (int f = 0; f < 6; ++f) { face[f] = rob[f]; }
      MGRobinFill(u, 0, nvar, ngh, n1, n2, n3, x1, x2, x3, d1, d2, d3, face);
    });
    MarkRootDeviceModified();
  } else {
    auto u = mgroot_->GetCurrentData_h();
    const int nvar = u.extent_int(1);
    MGRobinFill(u, 0, nvar, ngh, n1, n2, n3, x1, x2, x3, d1, d2, d3, rob);
  }
}
