#ifndef PARTICLES_NRPIC_CLOUD_HPP_
#define PARTICLES_NRPIC_CLOUD_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_cloud.hpp
//! \brief The cloud of the NRPIC deposit as functions that run inside device kernels:
//! the weights of a particle on the lattice of its deposition level, and the addition of
//! the cloud to the leaf cells of the MeshBlocks of a pack.
//!
//! These are steps (2) and (3) of the kernel of Particles::NrpicDepositSources
//! (nrpic.cpp), statement for statement.  The kernel keeps its own copy; the functions
//! here serve the deposit of clouds received from other MPI ranks (nrpic_mpi.cpp).  A
//! change of the cloud must be made in both places until the kernel calls these
//! functions (tracks/core/interfaces/mpi.md, section 3.3); the test of the conservation
//! identity on several ranks fails if the two differ.

#include "athena.hpp"
#include "mesh/mesh.hpp"
#include "z4c/tmunu.hpp"
#include "particles/nrpic_mesh.hpp"

namespace nrpic {

//----------------------------------------------------------------------------------------
//! \fn CloudWeights
//! \brief weights of the cloud on the lattice with spacing h: B-splines of degree one
//! (nb = 2 cells per direction), two (nb = 3) or three (nb = 4).  xb is the centre of the
//! first lattice cell of the cloud.

KOKKOS_INLINE_FUNCTION
void CloudWeights(const int nb, const Real xp[3], const Real gmin[3], const Real h[3],
                  Real xb[3], Real wt[3][4]) {
  for (int d=0; d<3; ++d) {
    Real xi = (xp[d] - gmin[d])/h[d] - 0.5;
    if (nb == 3) {
      Real fl = floor(xi + 0.5);
      Real dd = xi - fl;
      wt[d][0] = 0.5*SQR(0.5 - dd);
      wt[d][1] = 0.75 - dd*dd;
      wt[d][2] = 0.5*SQR(0.5 + dd);
      wt[d][3] = 0.0;
      xb[d] = gmin[d] + (fl - 0.5)*h[d];
    } else if (nb == 4) {
      Real fl = floor(xi);
      Real sd = xi - fl;
      wt[d][0] = (1.0 - sd)*(1.0 - sd)*(1.0 - sd)/6.0;
      wt[d][1] = (3.0*sd*sd*sd - 6.0*sd*sd + 4.0)/6.0;
      wt[d][2] = (-3.0*sd*sd*sd + 3.0*sd*sd + 3.0*sd + 1.0)/6.0;
      wt[d][3] = sd*sd*sd/6.0;
      xb[d] = gmin[d] + (fl - 0.5)*h[d];
    } else {
      Real fl = floor(xi);
      Real sd = xi - fl;
      wt[d][0] = 1.0 - sd;
      wt[d][1] = sd;
      wt[d][2] = 0.0;
      wt[d][3] = 0.0;
      xb[d] = gmin[d] + (fl + 0.5)*h[d];
    }
  }
}

//----------------------------------------------------------------------------------------
//! \struct CloudGeometry
//! \brief what the cloud loop needs to know about the mesh

struct CloudGeometry {
  int nb;                 // cells per direction of a cloud
  int is, js, ks, ie, je, ke;
  Real dmin[3], dlen[3];  // lower edge and length of the mesh
  bool per[3];            // periodic directions
};

//----------------------------------------------------------------------------------------
//! \fn CloudDeposit
//! \brief adds the amounts q (N_Tmunu of them) of one cloud to the leaf cells of the
//! MeshBlocks of the pack.  A lattice cell whose centre lies in no MeshBlock of the pack
//! is skipped: it is outside the mesh, or it belongs to another rank, which adds it from
//! its copy of the cloud.  ldep is the logical level of the lattice.

template <class SizeViewT, class LevViewT>
KOKKOS_INLINE_FUNCTION
void CloudDeposit(const CloudGeometry &cg, const SizeViewT &sz, const LevViewT &lev,
                  const int nmb, const int hint, const Real xb[3], const Real wt[3][4],
                  const Real h[3], const int ldep, const Real q[Tmunu::N_Tmunu],
                  const DvceArray5D<Real> &tm) {
  const int nb = cg.nb;
  const int is = cg.is, js = cg.js, ks = cg.ks;
  const int ie = cg.ie, je = cg.je, ke = cg.ke;
  int hb = hint;      // the MeshBlock found last is tried first
  for (int c=0; c<nb*nb*nb; ++c) {
    const int c1 = c % nb, c2 = (c/nb) % nb, c3 = c/(nb*nb);
    // centre of the lattice cell, wrapped into the mesh in periodic directions
    const Real xf = WrapCoord(xb[0] + c1*h[0], cg.dmin[0], cg.dlen[0], cg.per[0]);
    const Real yf = WrapCoord(xb[1] + c2*h[1], cg.dmin[1], cg.dlen[1], cg.per[1]);
    const Real zf = WrapCoord(xb[2] + c3*h[2], cg.dmin[2], cg.dlen[2], cg.per[2]);
    const Real w = wt[0][c1]*wt[1][c2]*wt[2][c3];
    const int mb = FindBlock(sz, nmb, hb, xf, yf, zf);
    if (mb < 0) continue;
    hb = mb;
    const int kd = lev(mb) - ldep;
    if (kd <= 0) {
      // leaf at the deposition level or coarser: the leaf cell containing the cell
      int i = is + static_cast<int>(floor((xf - sz(mb).x1min)/sz(mb).dx1));
      int j = js + static_cast<int>(floor((yf - sz(mb).x2min)/sz(mb).dx2));
      int k = ks + static_cast<int>(floor((zf - sz(mb).x3min)/sz(mb).dx3));
      i = (i < is) ? is : ((i > ie) ? ie : i);
      j = (j < js) ? js : ((j > je) ? je : j);
      k = (k < ks) ? ks : ((k > ke) ? ke : k);
      const Real wv = w/(sz(mb).dx1*sz(mb).dx2*sz(mb).dx3);
      for (int n=0; n<Tmunu::N_Tmunu; ++n) {
        Kokkos::atomic_add(&tm(mb,n,k,j,i), wv*q[n]);
      }
    } else {
      // finer leaves: the same density in every leaf cell inside the lattice cell
      const int nsub = 1 << kd;
      const Real wv = w/(h[0]*h[1]*h[2]);
      const int i0 = is + static_cast<int>(
          floor((xf - 0.5*h[0] - sz(mb).x1min)/sz(mb).dx1 + 0.5));
      const int j0 = js + static_cast<int>(
          floor((yf - 0.5*h[1] - sz(mb).x2min)/sz(mb).dx2 + 0.5));
      const int k0 = ks + static_cast<int>(
          floor((zf - 0.5*h[2] - sz(mb).x3min)/sz(mb).dx3 + 0.5));
      for (int kk=0; kk<nsub; ++kk) {
        const int k = k0 + kk;
        if (k < ks || k > ke) continue;
        for (int jj=0; jj<nsub; ++jj) {
          const int j = j0 + jj;
          if (j < js || j > je) continue;
          for (int ii=0; ii<nsub; ++ii) {
            const int i = i0 + ii;
            if (i < is || i > ie) continue;
            for (int n=0; n<Tmunu::N_Tmunu; ++n) {
              Kokkos::atomic_add(&tm(mb,n,k,j,i), wv*q[n]);
            }
          }
        }
      }
    }
  }
}

} // namespace nrpic
#endif // PARTICLES_NRPIC_CLOUD_HPP_
