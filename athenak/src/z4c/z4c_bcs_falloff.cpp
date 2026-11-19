//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file z4c_bcs_falloff.cpp
//! \brief ghost cells of the Z4c variables at outflow (diode, vacuum) faces filled by
//! extrapolation with the asymptotic value and the fall-off of each variable
//! (<z4c> ghost_falloff = true; z4c_sbc_ext.hpp).  Called after the stock fill of
//! bvals/physics/z4c_bcs.cpp, which it overwrites at those faces in the same order
//! (x1 faces over the whole (k, j) range, then x2 faces over the whole (k, i) range, then
//! x3 faces), so edges and corners are built as in the stock fill.
//!
//! Along the face normal, with the cells s = 0, 1, ..., p-1 counted inward from the
//! outermost active cell and the ghost cell g = 1, ..., ng outward,
//!   G_s = (f_s - f_inf) r_s^q,   G_g = sum_s w_gs G_s,   f_g = f_inf + G_g / r_g^q,
//! with w_gs the weights of the Lagrange polynomial through the p = extrap_order cells
//! (the weights of the stock fill) and r the distance of the cell centre from the origin
//! of the mesh.  q = 0 and f_inf = 0 give back the stock fill.

#include <cmath>
#include <iostream>

#include "athena.hpp"
#include "mesh/mesh.hpp"
#include "z4c/z4c.hpp"
#include "coordinates/cell_locations.hpp"

namespace z4c {

namespace {

//----------------------------------------------------------------------------------------
//! asymptotic value and power of variable n (Z4c ordering of z4c.hpp)
KOKKOS_INLINE_FUNCTION
void FalloffOf(const int n, const Real q_metric, const Real q_curv, Real &finf, Real &q) {
  switch (n) {
    case Z4c::I_Z4C_CHI:
    case Z4c::I_Z4C_GXX:
    case Z4c::I_Z4C_GYY:
    case Z4c::I_Z4C_GZZ:
    case Z4c::I_Z4C_ALPHA:
      finf = 1.0; q = q_metric; break;
    case Z4c::I_Z4C_GXY:
    case Z4c::I_Z4C_GXZ:
    case Z4c::I_Z4C_GYZ:
    case Z4c::I_Z4C_BETAX:
    case Z4c::I_Z4C_BETAY:
    case Z4c::I_Z4C_BETAZ:
      finf = 0.0; q = q_metric; break;
    default:  // Khat, A_ij, Gamma^i, Theta
      finf = 0.0; q = q_curv; break;
  }
}

//----------------------------------------------------------------------------------------
//! weight of node s (at -s) of the Lagrange polynomial through the nodes 0, -1, ...,
//! -(p-1), evaluated at +g
KOKKOS_INLINE_FUNCTION
Real LagrangeWeight(const int p, const int s, const int g) {
  Real w = 1.0;
  for (int l = 0; l < p; ++l) {
    if (l == s) continue;
    w *= static_cast<Real>(g + l)/static_cast<Real>(l - s);
  }
  return w;
}

//----------------------------------------------------------------------------------------
//! power r^q with the common integer cases exact
KOKKOS_INLINE_FUNCTION
Real PowR(const Real r, const Real q) {
  if (q == 0.0) return 1.0;
  if (q == 1.0) return r;
  return pow(r, q);
}

}  // namespace

//----------------------------------------------------------------------------------------
//! \fn void Z4c::GhostFalloff
//! \brief overwrite the ghost cells of u (fine array, or the coarse array if coarse) at
//! outflow, diode and vacuum faces with the fall-off extrapolation above.
void Z4c::GhostFalloff(DvceArray5D<Real> u, bool coarse) {
  auto &pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  auto &mb_bcs = pmy_pack->pmb->mb_bcs;
  auto &size = pmy_pack->pmb->mb_size;
  const int ng = indcs.ng;
  const int nx1 = coarse ? indcs.cnx1 : indcs.nx1;
  const int nx2 = coarse ? indcs.cnx2 : indcs.nx2;
  const int nx3 = coarse ? indcs.cnx3 : indcs.nx3;
  const int is = coarse ? indcs.cis : indcs.is, ie = coarse ? indcs.cie : indcs.ie;
  const int js = coarse ? indcs.cjs : indcs.js, je = coarse ? indcs.cje : indcs.je;
  const int ks = coarse ? indcs.cks : indcs.ks, ke = coarse ? indcs.cke : indcs.ke;
  const int n1 = nx1 + 2*ng;
  const int n2 = (nx2 > 1) ? (nx2 + 2*ng) : 1;
  const int n3 = (nx3 > 1) ? (nx3 + 2*ng) : 1;
  const int nvar = u.extent_int(1);
  const int nmb = pmy_pack->nmb_thispack;
  const int p = opt.extrap_order;
  const Real qm = sbc.ghost_q_metric;
  const Real qc = sbc.ghost_q_curv;

  // one face: ghost g of the line through (k, j, i) = outermost active cell, inward
  // step (dk, dj, di); positions of the cells from their indices
  auto is_out = [](BoundaryFlag f) {
    return f == BoundaryFlag::outflow || f == BoundaryFlag::diode
        || f == BoundaryFlag::vacuum;
  };

  // x1 faces
  if (pm->mesh_bcs[BoundaryFace::inner_x1] != BoundaryFlag::periodic
      && pm->mesh_bcs[BoundaryFace::inner_x1] != BoundaryFlag::shear_periodic) {
    const bool in_out = is_out(pm->mesh_bcs[BoundaryFace::inner_x1]);
    const bool out_out = is_out(pm->mesh_bcs[BoundaryFace::outer_x1]);
    if (in_out || out_out) {
      par_for("z4cbc_falloff_x1", DevExeSpace(), 0, (nmb-1), 0, (nvar-1), 0, (n3-1),
              0, (n2-1),
      KOKKOS_LAMBDA(int m, int n, int k, int j) {
        Real finf, q;
        FalloffOf(n, qm, qc, finf, q);
        const RegionSize &sz = size.d_view(m);
        const Real y = CellCenterX(j-js, nx2, sz.x2min, sz.x2max);
        const Real z = CellCenterX(k-ks, nx3, sz.x3min, sz.x3max);
        for (int side = 0; side < 2; ++side) {
          const BoundaryFlag bf = mb_bcs.d_view(m, side == 0 ? BoundaryFace::inner_x1
                                                             : BoundaryFace::outer_x1);
          if (!(bf == BoundaryFlag::outflow || bf == BoundaryFlag::diode
                || bf == BoundaryFlag::vacuum)) continue;
          const int i0 = (side == 0) ? is : ie;
          const int step = (side == 0) ? 1 : -1;  // inward
          Real G[4];
          for (int s = 0; s < p; ++s) {
            const int ii = i0 + s*step;
            const Real x = CellCenterX(ii-is, nx1, sz.x1min, sz.x1max);
            const Real r = sqrt(x*x + y*y + z*z);
            G[s] = (u(m,n,k,j,ii) - finf)*PowR(r, q);
          }
          for (int g = 1; g <= ng; ++g) {
            const int ig = i0 - g*step;
            const Real x = CellCenterX(ig-is, nx1, sz.x1min, sz.x1max);
            const Real r = sqrt(x*x + y*y + z*z);
            Real Gg = 0.0;
            for (int s = 0; s < p; ++s) Gg += LagrangeWeight(p, s, g)*G[s];
            u(m,n,k,j,ig) = finf + Gg/PowR(r, q);
          }
        }
      });
    }
  }
  if (pm->one_d) return;

  // x2 faces
  if (pm->mesh_bcs[BoundaryFace::inner_x2] != BoundaryFlag::periodic) {
    const bool in_out = is_out(pm->mesh_bcs[BoundaryFace::inner_x2]);
    const bool out_out = is_out(pm->mesh_bcs[BoundaryFace::outer_x2]);
    if (in_out || out_out) {
      par_for("z4cbc_falloff_x2", DevExeSpace(), 0, (nmb-1), 0, (nvar-1), 0, (n3-1),
              0, (n1-1),
      KOKKOS_LAMBDA(int m, int n, int k, int i) {
        Real finf, q;
        FalloffOf(n, qm, qc, finf, q);
        const RegionSize &sz = size.d_view(m);
        const Real x = CellCenterX(i-is, nx1, sz.x1min, sz.x1max);
        const Real z = CellCenterX(k-ks, nx3, sz.x3min, sz.x3max);
        for (int side = 0; side < 2; ++side) {
          const BoundaryFlag bf = mb_bcs.d_view(m, side == 0 ? BoundaryFace::inner_x2
                                                             : BoundaryFace::outer_x2);
          if (!(bf == BoundaryFlag::outflow || bf == BoundaryFlag::diode
                || bf == BoundaryFlag::vacuum)) continue;
          const int j0 = (side == 0) ? js : je;
          const int step = (side == 0) ? 1 : -1;
          Real G[4];
          for (int s = 0; s < p; ++s) {
            const int jj = j0 + s*step;
            const Real y = CellCenterX(jj-js, nx2, sz.x2min, sz.x2max);
            const Real r = sqrt(x*x + y*y + z*z);
            G[s] = (u(m,n,k,jj,i) - finf)*PowR(r, q);
          }
          for (int g = 1; g <= ng; ++g) {
            const int jg = j0 - g*step;
            const Real y = CellCenterX(jg-js, nx2, sz.x2min, sz.x2max);
            const Real r = sqrt(x*x + y*y + z*z);
            Real Gg = 0.0;
            for (int s = 0; s < p; ++s) Gg += LagrangeWeight(p, s, g)*G[s];
            u(m,n,k,jg,i) = finf + Gg/PowR(r, q);
          }
        }
      });
    }
  }
  if (pm->two_d) return;

  // x3 faces
  if (pm->mesh_bcs[BoundaryFace::inner_x3] == BoundaryFlag::periodic) return;
  {
    const bool in_out = is_out(pm->mesh_bcs[BoundaryFace::inner_x3]);
    const bool out_out = is_out(pm->mesh_bcs[BoundaryFace::outer_x3]);
    if (!(in_out || out_out)) return;
  }
  par_for("z4cbc_falloff_x3", DevExeSpace(), 0, (nmb-1), 0, (nvar-1), 0, (n2-1),
          0, (n1-1),
  KOKKOS_LAMBDA(int m, int n, int j, int i) {
    Real finf, q;
    FalloffOf(n, qm, qc, finf, q);
    const RegionSize &sz = size.d_view(m);
    const Real x = CellCenterX(i-is, nx1, sz.x1min, sz.x1max);
    const Real y = CellCenterX(j-js, nx2, sz.x2min, sz.x2max);
    for (int side = 0; side < 2; ++side) {
      const BoundaryFlag bf = mb_bcs.d_view(m, side == 0 ? BoundaryFace::inner_x3
                                                         : BoundaryFace::outer_x3);
      if (!(bf == BoundaryFlag::outflow || bf == BoundaryFlag::diode
            || bf == BoundaryFlag::vacuum)) continue;
      const int k0 = (side == 0) ? ks : ke;
      const int step = (side == 0) ? 1 : -1;
      Real G[4];
      for (int s = 0; s < p; ++s) {
        const int kk = k0 + s*step;
        const Real z = CellCenterX(kk-ks, nx3, sz.x3min, sz.x3max);
        const Real r = sqrt(x*x + y*y + z*z);
        G[s] = (u(m,n,kk,j,i) - finf)*PowR(r, q);
      }
      for (int g = 1; g <= ng; ++g) {
        const int kg = k0 - g*step;
        const Real z = CellCenterX(kg-ks, nx3, sz.x3min, sz.x3max);
        const Real r = sqrt(x*x + y*y + z*z);
        Real Gg = 0.0;
        for (int s = 0; s < p; ++s) Gg += LagrangeWeight(p, s, g)*G[s];
        u(m,n,kg,j,i) = finf + Gg/PowR(r, q);
      }
    }
  });
}

} // namespace z4c
