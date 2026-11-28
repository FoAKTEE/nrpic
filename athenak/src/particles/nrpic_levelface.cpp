//========================================================================================
// AthenaK astrophysical fluid dynamics & numerical relativity code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_levelface.cpp
//! \brief NRPIC: the compensation pass of the deposit made conservative across the faces
//! between refinement levels.
//!
//! NrpicCompensateLimited applies u_i - (F_{i+1/2} - F_{i-1/2}) on every MeshBlock, with
//! ghost values of the other level at a level face (prolongated on the fine side,
//! restricted on the coarse side).  The flux through such a face is then computed
//! twice, by the coarse block and by the fine blocks, from different data, and what
//! leaves one side is not what enters the other: the sums of the deposit over the mesh
//! are not conserved (0.13 per cent of the mass per level face in the test of a uniform
//! lattice, tracks/core/analysis/deposit_levels).  The two fluxes do not only differ
//! by truncation error.  The pass is u - c d2 u in cells of the level (it undoes a cloud
//! whose width is the cell of the level), so the flux per area, c dx^2 du/dx, is four
//! times larger on the coarse side: no flux is consistent with both sides, and a
//! conservative pass has to choose one.
//!
//! Here the flux of the fine side is chosen.  After the pass of one direction, and before
//! its result replaces the sources, the coarse cell at a level face gives back the flux
//! it used and takes the sum of the fluxes of the four fine faces, weighted by the ratio
//! of the volumes: with F in units of the update, F_coarse = (1/8) sum F_fine.  The fine
//! cells keep the pass as it was.  The fluxes of the fine block (with its limiter) are
//! read from the fine block's array, found through the neighbour table; a fine block on
//! another rank is not reached and that face keeps the two fluxes (several ranks: open).

#include <cmath>

#include "athena.hpp"
#include "globals.hpp"
#include "mesh/mesh.hpp"
#include "z4c/tmunu.hpp"
#include "particles/particles.hpp"

namespace {

//----------------------------------------------------------------------------------------
//! \fn NrpicFaceFlux
//! \brief the flux of the compensation pass through the face of cell (k,j,i) that lies in
//! the direction (dk,dj,di), counted positive when it leaves the cell:
//!   c (u_1 - u_0) - q (u_2 - 3 u_1 + 3 u_0 - u_-1),   q = c2/16
//! (the expressions fp and -fm of NrpicCompensateLimited)

KOKKOS_INLINE_FUNCTION
Real NrpicFaceFlux(const DvceArray5D<Real> &u, const int m, const int n, const int k,
                   const int j, const int i, const int dk, const int dj, const int di,
                   const Real c, const Real q) {
  const Real v0 = u(m,n,k,j,i);
  const Real v1 = u(m,n,k+dk,j+dj,i+di);
  const Real v2 = u(m,n,k+2*dk,j+2*dj,i+2*di);
  const Real vm = u(m,n,k-dk,j-dj,i-di);
  return c*(v1 - v0) - q*(v2 - 3.0*v1 + 3.0*v0 - vm);
}

//----------------------------------------------------------------------------------------
//! \fn NrpicFaceTheta
//! \brief the limiter of NrpicCompensateLimited at that face: the flux of the energy
//! density is held below lim times the smaller of the two energy densities

KOKKOS_INLINE_FUNCTION
Real NrpicFaceTheta(const DvceArray5D<Real> &u, const int m, const int ne, const int k,
                    const int j, const int i, const int dk, const int dj, const int di,
                    const Real c, const Real q, const Real lim) {
  const Real fe = NrpicFaceFlux(u, m, ne, k, j, i, dk, dj, di, c, q);
  const Real cap = lim*fmax(fmin(u(m,ne,k,j,i), u(m,ne,k+dk,j+dj,i+di)), 0.0);
  return (fabs(fe) > cap) ? cap/fabs(fe) : 1.0;
}

} // namespace

namespace particles {

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicCompensateLevelFaces
//! \brief correction of the pass of direction dir (0, 1, 2) at the faces between levels.
//! Called by NrpicCompensateLimited when the sources still hold the values the pass
//! read and tm_work holds its result; changes tm_work in the coarse cells at level faces.

void Particles::NrpicCompensateLevelFaces(const int dir, const Real c, const Real q,
                                          const Real lim) {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int nmb1 = pmy_pack->nmb_thispack - 1;
  const int nv = Tmunu::N_Tmunu;
  const int ne = Tmunu::I_Tmunu_E;
  auto tm = pmy_pack->ptmunu->u_tmunu;
  auto wk = tm_work;
  auto nghbr = pmy_pack->pmb->nghbr.d_view;
  auto lev = pmy_pack->pmb->mb_lev.d_view;
  const int gids = pmy_pack->gids;
  const int my_rank = global_variable::my_rank;
  const bool limit = (lim > 0.0);

  // first and last active cell and number of cells per direction; the two directions
  // across the pass in the order of the sub-faces of the neighbour table (x2 before x3
  // for a face of x1, x1 before x3 for x2, x1 before x2 for x3)
  const int s0[3] = {indcs.is, indcs.js, indcs.ks};
  const int e0[3] = {indcs.ie, indcs.je, indcs.ke};
  const int nn[3] = {indcs.nx1, indcs.nx2, indcs.nx3};
  const int t1 = (dir == 0) ? 1 : 0;
  const int t2 = (dir == 2) ? 1 : 2;
  const int nt1 = nn[t1], nt2 = nn[t2];
  // index of the first neighbour across the inner face of this direction (nghbr_index)
  const int base = (dir == 0) ? 0 : ((dir == 1) ? 8 : 24);

  par_for("nrpic_compface", DevExeSpace(), 0, nmb1, 0, 1, 0, nt2-1, 0, nt1-1,
  KOKKOS_LAMBDA(const int m, const int side, const int b, const int a) {
    // the neighbour across the quarter of the face that holds this cell
    const int f1 = (2*a >= nt1) ? 1 : 0;
    const int f2 = (2*b >= nt2) ? 1 : 0;
    const NeighborBlock nbk = nghbr(m, base + 4*side + f1 + 2*f2);
    if (nbk.gid < 0 || nbk.lev <= lev(m) || nbk.rank != my_rank) return;
    const int mf = nbk.gid - gids;

    // the coarse cell at the face and the direction out of it through the face
    const int oc = (side == 0) ? -1 : 1;
    int ic[3], dc[3] = {0, 0, 0};
    ic[dir] = (side == 0) ? s0[dir] : e0[dir];
    ic[t1] = s0[t1] + a;
    ic[t2] = s0[t2] + b;
    dc[dir] = oc;
    // the four fine cells on the other side of the face, and the direction out of them
    int jf[3], df[3] = {0, 0, 0};
    jf[dir] = (side == 0) ? e0[dir] : s0[dir];
    const int a0 = s0[t1] + 2*(a - f1*(nt1/2));
    const int b0 = s0[t2] + 2*(b - f2*(nt2/2));
    df[dir] = -oc;

    Real thc = 1.0;
    Real thf[4] = {1.0, 1.0, 1.0, 1.0};
    if (limit) {
      thc = NrpicFaceTheta(tm, m, ne, ic[2], ic[1], ic[0], dc[2], dc[1], dc[0], c, q, lim);
      for (int s=0; s<4; ++s) {
        jf[t1] = a0 + (s % 2);
        jf[t2] = b0 + (s / 2);
        thf[s] = NrpicFaceTheta(tm, mf, ne, jf[2], jf[1], jf[0], df[2], df[1], df[0],
                                c, q, lim);
      }
    }
    for (int n=0; n<nv; ++n) {
      // the flux the pass let out of the coarse cell, and what enters the fine cells
      const Real gc = NrpicFaceFlux(tm, m, n, ic[2], ic[1], ic[0], dc[2], dc[1], dc[0],
                                    c, q);
      Real gf = 0.0;
      for (int s=0; s<4; ++s) {
        jf[t1] = a0 + (s % 2);
        jf[t2] = b0 + (s / 2);
        gf += thf[s]*NrpicFaceFlux(tm, mf, n, jf[2], jf[1], jf[0], df[2], df[1], df[0],
                                   c, q);
      }
      // the pass took thc gc out of the coarse cell; the fine cells let 1/8 of the sum
      // of their fluxes (per coarse cell volume) out towards it
      wk(m,n,ic[2],ic[1],ic[0]) += thc*gc + 0.125*gf;
    }
  });
}

} // namespace particles
