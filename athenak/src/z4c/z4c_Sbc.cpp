//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file z4c_Sbc.cpp
//! \brief placeholder for Sommerfeld boundary condition

#include <algorithm>
#include <cinttypes>
#include <iostream>
#include <limits>

#include "athena.hpp"
#include "mesh/mesh.hpp"
#include "z4c/z4c.hpp"
#include "coordinates/cell_locations.hpp"

namespace z4c {

//----------------------------------------------------------------------------------------
//! \fn void Z4c::Z4cSommerfeld
//! \brief apply Sommerfeld BCs to the given set of points
KOKKOS_INLINE_FUNCTION
static void Z4cSommerfeld(const Z4c::Z4c_vars& z4c, const Z4c::Z4c_vars& rhs,
    const RegionIndcs &indcs, const DualArray1D<RegionSize> &size,
    const int m, const int k, const int j, const int i) {
  // -------------------------------------------------------------------------------------
  // Scratch data
  //

  // First derivatives
  // Scalars
  AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> dKhat_d;
  AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> dTheta_d;

  // Vectors
  AthenaPointTensor<Real, TensorSymm::NONE, 3, 2> dGam_du;

  // Tensors
  AthenaPointTensor<Real, TensorSymm::SYM2, 3, 3> dA_ddd;


  // Psuedoradial vector
  AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> s_u;

  Real idx[] = {1./size.d_view(m).dx1, 1./size.d_view(m).dx2, 1./size.d_view(m).dx3};

  // -------------------------------------------------------------------------------------
  // First derivatives
  // We force all derivatives to be calculated at second-order, as this was found to
  // be necessary for stability in Athena++.
  //
  for (int a = 0; a < 3; a++) {
    dKhat_d(a) = Dx<2>(a, idx, z4c.vKhat, m, k, j, i);
    dTheta_d(a) = Dx<2>(a, idx, z4c.vTheta, m, k, j, i);
  }
  for (int a = 0; a < 3; a++) {
    for (int b = 0; b < 3; b++) {
      dGam_du(b,a) = Dx<2>(b, idx, z4c.vGam_u, m, a, k, j, i);
    }
  }
  for (int a = 0; a < 3; a++) {
    for (int b = a; b < 3; b++) {
      for (int c = 0; c < 3; c++) {
        dA_ddd(c, a, b) = Dx<2>(c, idx, z4c.vA_dd, m, a, b, k, j, i);
      }
    }
  }

  // -------------------------------------------------------------------------------------
  // Compute psuedo-radial vector
  //
  Real &x1min = size.d_view(m).x1min;
  Real &x1max = size.d_view(m).x1max;
  Real &x2min = size.d_view(m).x2min;
  Real &x2max = size.d_view(m).x2max;
  Real &x3min = size.d_view(m).x3min;
  Real &x3max = size.d_view(m).x3max;

  Real x1v = CellCenterX(i-indcs.is, indcs.nx1, x1min, x1max);
  Real x2v = CellCenterX(j-indcs.js, indcs.nx2, x2min, x2max);
  Real x3v = CellCenterX(k-indcs.ks, indcs.nx3, x3min, x3max);

  Real r = sqrt(SQR(x1v) + SQR(x2v) + SQR(x3v));
  s_u(0) = x1v/r;
  s_u(1) = x2v/r;
  s_u(2) = x3v/r;

  // -------------------------------------------------------------------------------------
  // Boundary RHS for scalars
  //
  rhs.vTheta(m,k,j,i) = - z4c.vTheta(m,k,j,i)/r;
  rhs.vKhat(m,k,j,i) = - sqrt(2.) * z4c.vKhat(m,k,j,i)/r;
  for (int a = 0; a < 3; a++) {
    rhs.vTheta(m,k,j,i) -= s_u(a) * dTheta_d(a);
    rhs.vKhat(m,k,j,i) -= sqrt(2.) * s_u(a) * dKhat_d(a);
  }

  // -------------------------------------------------------------------------------------
  // Boundary RHS for Gamma
  //
  for (int a = 0; a < 3; a++) {
    rhs.vGam_u(m,a,k,j,i) = - z4c.vGam_u(m, a, k, j, i)/r;
    for (int b = 0; b < 3; b++) {
      rhs.vGam_u(m,a,k,j,i) -= s_u(b) * dGam_du(b,a);
    }
  }

  // -------------------------------------------------------------------------------------
  // Boundary RHS for A_ab
  //
  for (int a = 0; a < 3; a++) {
    for (int b = a; b < 3; b++) {
      rhs.vA_dd(m,a,b,k,j,i) = - z4c.vA_dd(m,a,b,k,j,i)/r;
      for (int c = 0; c < 3; c++) {
        rhs.vA_dd(m,a,b,k,j,i) -= s_u(c) * dA_ddd(c,a,b);
      }
    }
  }
}


//---------------------------------------------------------------------------------------
//! \fn TaskStatus Z4c::Z4cBoundaryRHS
//! \brief placeholder for the Sommerfield Boundary conditions for z4c
TaskStatus Z4c::Z4cBoundaryRHS(Driver *pdriver, int stage) {
  // radiative condition with a non-wave part (z4c_sbc_ext.hpp), off by default
  if (sbc.variant != 0) return Z4cBoundaryRHSNonwave(pdriver, stage);
  auto &pm = pmy_pack->pmesh;
  auto &mb_bcs = pmy_pack->pmb->mb_bcs;
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  auto &size = pmy_pack->pmb->mb_size;

  int nmb = pmy_pack->nmb_thispack;
  int is = indcs.is;
  int ie = indcs.ie;
  int js = indcs.js;
  int je = indcs.je;
  int ks = indcs.ks;
  int ke = indcs.ke;

  auto &z4c_ = z4c;
  auto &rhs_ = rhs;
  bool &user_Sbc = opt.user_Sbc;

  // We only need to apply this condition for outflow boundaries
  if (pm->mesh_bcs[BoundaryFace::inner_x1] == BoundaryFlag::outflow
      || pm->mesh_bcs[BoundaryFace::inner_x1] == BoundaryFlag::diode
      || pm->mesh_bcs[BoundaryFace::inner_x1] == BoundaryFlag::vacuum
      || pm->mesh_bcs[BoundaryFace::inner_x1] == BoundaryFlag::user
      || pm->mesh_bcs[BoundaryFace::outer_x1] == BoundaryFlag::outflow
      || pm->mesh_bcs[BoundaryFace::outer_x1] == BoundaryFlag::diode
      || pm->mesh_bcs[BoundaryFace::outer_x1] == BoundaryFlag::vacuum
      || pm->mesh_bcs[BoundaryFace::outer_x1] == BoundaryFlag::user) {
    par_for("z4crhs_bc_x1", DevExeSpace(), 0, (nmb-1), ks, ke, js, je,
    KOKKOS_LAMBDA(int m, int k, int j) {
      // Inner boundary
      switch(mb_bcs.d_view(m,BoundaryFace::inner_x1)) {
        case BoundaryFlag::diode:
        case BoundaryFlag::vacuum:
        case BoundaryFlag::outflow:
            Z4cSommerfeld(z4c_, rhs_, indcs, size, m, k, j, is);
          break;
        case BoundaryFlag::user:
            if (user_Sbc) {
              Z4cSommerfeld(z4c_, rhs_, indcs, size, m, k, j, is);
            }
          break;
        default:
          break;
      }
      // Outer boundary
      switch (mb_bcs.d_view(m,BoundaryFace::outer_x1)) {
        case BoundaryFlag::diode:
        case BoundaryFlag::vacuum:
        case BoundaryFlag::outflow:
            Z4cSommerfeld(z4c_, rhs_, indcs, size, m, k, j, ie);
          break;
        case BoundaryFlag::user:
            if (user_Sbc) {
              Z4cSommerfeld(z4c_, rhs_, indcs, size, m, k, j, ie);
            }
          break;
        default:
          break;
      }
    });
  }
  if (pm->mesh_bcs[BoundaryFace::inner_x2] == BoundaryFlag::outflow
      || pm->mesh_bcs[BoundaryFace::inner_x2] == BoundaryFlag::diode
      || pm->mesh_bcs[BoundaryFace::inner_x2] == BoundaryFlag::vacuum
      || pm->mesh_bcs[BoundaryFace::inner_x2] == BoundaryFlag::user
      || pm->mesh_bcs[BoundaryFace::outer_x2] == BoundaryFlag::outflow
      || pm->mesh_bcs[BoundaryFace::outer_x2] == BoundaryFlag::diode
      || pm->mesh_bcs[BoundaryFace::outer_x2] == BoundaryFlag::vacuum
      || pm->mesh_bcs[BoundaryFace::outer_x2] == BoundaryFlag::user) {
    par_for("z4crhs_bc_x2", DevExeSpace(), 0, (nmb-1), ks, ke, is, ie,
    KOKKOS_LAMBDA(int m, int k, int i) {
      // Inner boundary
      switch(mb_bcs.d_view(m,BoundaryFace::inner_x2)) {
        case BoundaryFlag::diode:
        case BoundaryFlag::vacuum:
        case BoundaryFlag::outflow:
            Z4cSommerfeld(z4c_, rhs_, indcs, size, m, k, js, i);
          break;
        case BoundaryFlag::user:
            if (user_Sbc) {
              Z4cSommerfeld(z4c_, rhs_, indcs, size, m, k, js, i);
            }
          break;
        default:
          break;
      }
      // Outer boundary
      switch (mb_bcs.d_view(m,BoundaryFace::outer_x2)) {
        case BoundaryFlag::diode:
        case BoundaryFlag::vacuum:
        case BoundaryFlag::outflow:
            Z4cSommerfeld(z4c_, rhs_, indcs, size, m, k, je, i);
          break;
        case BoundaryFlag::user:
            if (user_Sbc) {
              Z4cSommerfeld(z4c_, rhs_, indcs, size, m, k, je, i);
            }
          break;
        default:
          break;
      }
    });
  }
  if (pm->mesh_bcs[BoundaryFace::inner_x3] == BoundaryFlag::outflow
      || pm->mesh_bcs[BoundaryFace::inner_x3] == BoundaryFlag::diode
      || pm->mesh_bcs[BoundaryFace::inner_x3] == BoundaryFlag::vacuum
      || pm->mesh_bcs[BoundaryFace::inner_x3] == BoundaryFlag::user
      || pm->mesh_bcs[BoundaryFace::outer_x3] == BoundaryFlag::outflow
      || pm->mesh_bcs[BoundaryFace::outer_x3] == BoundaryFlag::diode
      || pm->mesh_bcs[BoundaryFace::outer_x3] == BoundaryFlag::vacuum
      || pm->mesh_bcs[BoundaryFace::outer_x3] == BoundaryFlag::user) {
    par_for("z4crhs_bc_x3", DevExeSpace(), 0, (nmb-1), js, je, is, ie,
    KOKKOS_LAMBDA(int m, int j, int i) {
      // Inner boundary
      switch(mb_bcs.d_view(m,BoundaryFace::inner_x3)) {
        case BoundaryFlag::diode:
        case BoundaryFlag::vacuum:
        case BoundaryFlag::outflow:
            Z4cSommerfeld(z4c_, rhs_, indcs, size, m, ks, j, i);
          break;
        case BoundaryFlag::user:
            if (user_Sbc) {
              Z4cSommerfeld(z4c_, rhs_, indcs, size, m, ks, j, i);
            }
          break;
        default:
          break;
      }
      // Outer boundary
      switch (mb_bcs.d_view(m,BoundaryFace::outer_x3)) {
        case BoundaryFlag::diode:
        case BoundaryFlag::vacuum:
        case BoundaryFlag::outflow:
            Z4cSommerfeld(z4c_, rhs_, indcs, size, m, ke, j, i);
          break;
        case BoundaryFlag::user:
            if (user_Sbc) {
              Z4cSommerfeld(z4c_, rhs_, indcs, size, m, ke, j, i);
            }
          break;
        default:
          break;
      }
    });
  }


  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn void Z4cRadiativeOp
//! \brief the wave operator R[f] = -v (s^k d_k f + f/r) of the Sommerfeld condition at
//! one cell for Theta, Khat, Gamma^i and A_ij (second-order centred derivatives, as in
//! Z4cSommerfeld), and the distance r of the cell from the origin.  Index of op:
//! 0 Theta, 1 Khat, 2-4 Gamma^i, 5-10 A_ij (xx, xy, xz, yy, yz, zz).
KOKKOS_INLINE_FUNCTION
static void Z4cRadiativeOp(const Z4c::Z4c_vars& z4c, const RegionIndcs &indcs,
    const DualArray1D<RegionSize> &size, const Real v_khat,
    const int m, const int k, const int j, const int i, Real op[11], Real &r) {
  Real idx[] = {1./size.d_view(m).dx1, 1./size.d_view(m).dx2, 1./size.d_view(m).dx3};
  Real &x1min = size.d_view(m).x1min;
  Real &x1max = size.d_view(m).x1max;
  Real &x2min = size.d_view(m).x2min;
  Real &x2max = size.d_view(m).x2max;
  Real &x3min = size.d_view(m).x3min;
  Real &x3max = size.d_view(m).x3max;
  Real x1v = CellCenterX(i-indcs.is, indcs.nx1, x1min, x1max);
  Real x2v = CellCenterX(j-indcs.js, indcs.nx2, x2min, x2max);
  Real x3v = CellCenterX(k-indcs.ks, indcs.nx3, x3min, x3max);
  r = sqrt(SQR(x1v) + SQR(x2v) + SQR(x3v));
  Real s_u[3] = {x1v/r, x2v/r, x3v/r};

  op[0] = - z4c.vTheta(m,k,j,i)/r;
  op[1] = - v_khat * z4c.vKhat(m,k,j,i)/r;
  for (int a = 0; a < 3; a++) {
    op[0] -= s_u[a] * Dx<2>(a, idx, z4c.vTheta, m, k, j, i);
    op[1] -= v_khat * s_u[a] * Dx<2>(a, idx, z4c.vKhat, m, k, j, i);
  }
  for (int a = 0; a < 3; a++) {
    op[2+a] = - z4c.vGam_u(m,a,k,j,i)/r;
    for (int b = 0; b < 3; b++) {
      op[2+a] -= s_u[b] * Dx<2>(b, idx, z4c.vGam_u, m, a, k, j, i);
    }
  }
  int n = 5;
  for (int a = 0; a < 3; a++) {
    for (int b = a; b < 3; b++) {
      op[n] = - z4c.vA_dd(m,a,b,k,j,i)/r;
      for (int c = 0; c < 3; c++) {
        op[n] -= s_u[c] * Dx<2>(c, idx, z4c.vA_dd, m, a, b, k, j, i);
      }
      ++n;
    }
  }
}

//---------------------------------------------------------------------------------------
//! \fn TaskStatus Z4c::Z4cBoundaryRHSNonwave
//! \brief radiative condition with a non-wave part (z4c_sbc_ext.hpp) in the outermost
//! active cells at the physical faces to which Z4cBoundaryRHS applies the Sommerfeld
//! condition.  Every such cell b is written once:
//!   rhs_b = R_b + (rhs_p - R_p) (r_p/r_b)^q,
//! with p one step inward along every direction in which b lies on such a face.  p is
//! never a boundary cell, so rhs_p is the full right-hand side of CalcRHS.
TaskStatus Z4c::Z4cBoundaryRHSNonwave(Driver *pdriver, int stage) {
  auto &pm = pmy_pack->pmesh;
  auto &mb_bcs = pmy_pack->pmb->mb_bcs;
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  auto &size = pmy_pack->pmb->mb_size;

  bool &user_Sbc = opt.user_Sbc;
  bool any = false;
  for (int f = 0; f < 6; ++f) {
    BoundaryFlag bf = pm->mesh_bcs[f];
    if (bf == BoundaryFlag::outflow || bf == BoundaryFlag::diode
        || bf == BoundaryFlag::vacuum || bf == BoundaryFlag::user) any = true;
  }
  if (!any) return TaskStatus::complete;

  int nmb = pmy_pack->nmb_thispack;
  int is = indcs.is, ie = indcs.ie;
  int js = indcs.js, je = indcs.je;
  int ks = indcs.ks, ke = indcs.ke;

  auto &z4c_ = z4c;
  auto &rhs_ = rhs;
  auto sbc_ = sbc;

  par_for("z4crhs_bc_nonwave", DevExeSpace(), 0, (nmb-1), ks, ke, js, je, is, ie,
  KOKKOS_LAMBDA(int m, int k, int j, int i) {
    // inward step along every direction in which the cell lies on a physical face
    int d[3] = {0, 0, 0};
    const int idxc[3] = {i, j, k};
    const int lo[3] = {is, js, ks};
    const int hi[3] = {ie, je, ke};
    for (int a = 0; a < 3; ++a) {
      if (idxc[a] == lo[a]) {
        BoundaryFlag bf = mb_bcs.d_view(m, 2*a);
        if (bf == BoundaryFlag::outflow || bf == BoundaryFlag::diode
            || bf == BoundaryFlag::vacuum
            || (bf == BoundaryFlag::user && user_Sbc)) d[a] = 1;
      }
      if (idxc[a] == hi[a]) {
        BoundaryFlag bf = mb_bcs.d_view(m, 2*a+1);
        if (bf == BoundaryFlag::outflow || bf == BoundaryFlag::diode
            || bf == BoundaryFlag::vacuum
            || (bf == BoundaryFlag::user && user_Sbc)) d[a] = -1;
      }
    }
    if (d[0] == 0 && d[1] == 0 && d[2] == 0) return;
    const int ip = i + d[0], jp = j + d[1], kp = k + d[2];

    Real opb[11], opp[11], rb, rp;
    Z4cRadiativeOp(z4c_, indcs, size, sbc_.v_khat, m, k, j, i, opb, rb);
    Z4cRadiativeOp(z4c_, indcs, size, sbc_.v_khat, m, kp, jp, ip, opp, rp);
    const Real ratio = rp/rb;
    const Real wk = pow(ratio, sbc_.q_khat);
    const Real wg = pow(ratio, sbc_.q_gam);
    const Real wa = pow(ratio, sbc_.q_a);

    if (sbc_.theta_nonwave) {
      rhs_.vTheta(m,k,j,i) = opb[0]
          + (rhs_.vTheta(m,kp,jp,ip) - opp[0]) * pow(ratio, sbc_.q_theta);
    } else {
      rhs_.vTheta(m,k,j,i) = opb[0];
    }
    rhs_.vKhat(m,k,j,i) = opb[1] + (rhs_.vKhat(m,kp,jp,ip) - opp[1]) * wk;
    for (int a = 0; a < 3; a++) {
      rhs_.vGam_u(m,a,k,j,i) = opb[2+a] + (rhs_.vGam_u(m,a,kp,jp,ip) - opp[2+a]) * wg;
    }
    int n = 5;
    for (int a = 0; a < 3; a++) {
      for (int b = a; b < 3; b++) {
        rhs_.vA_dd(m,a,b,k,j,i) = opb[n] + (rhs_.vA_dd(m,a,b,kp,jp,ip) - opp[n]) * wa;
        ++n;
      }
    }
  });

  return TaskStatus::complete;
}

} // end namespace z4c
