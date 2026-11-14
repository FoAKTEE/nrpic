#ifndef PARTICLES_NRPIC_MESH_HPP_
#define PARTICLES_NRPIC_MESH_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_mesh.hpp
//! \brief Mesh-side helpers of the NRPIC module that run inside device kernels: the
//! metric functor that reconstructs the 3+1 fields from cell-centred mesh data with
//! cubic Hermite interpolation, and the search for the MeshBlock that contains a point.

#include "athena.hpp"
#include "mesh/mesh.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"

namespace nrpic {

//----------------------------------------------------------------------------------------
//! \fn FindBlock
//! \brief index of the MeshBlock (within the pack) whose half-open extent
//! [xmin, xmax) contains the point, or -1 if the point lies outside the mesh.  The
//! MeshBlock with index hint is tested first.

template <class SizeViewT>
KOKKOS_INLINE_FUNCTION
int FindBlock(const SizeViewT &sz, const int nmb, const int hint,
              const Real x, const Real y, const Real z) {
  if (hint >= 0 && hint < nmb) {
    const auto &s = sz(hint);
    if (x >= s.x1min && x < s.x1max && y >= s.x2min && y < s.x2max &&
        z >= s.x3min && z < s.x3max) {
      return hint;
    }
  }
  for (int m=0; m<nmb; ++m) {
    const auto &s = sz(m);
    if (x >= s.x1min && x < s.x1max && y >= s.x2min && y < s.x2max &&
        z >= s.x3min && z < s.x3max) {
      return m;
    }
  }
  return -1;
}

//----------------------------------------------------------------------------------------
//! \fn WrapCoord
//! \brief maps a coordinate into [xmin, xmin + len) of a periodic direction; returns it
//! unchanged in a direction that is not periodic

KOKKOS_INLINE_FUNCTION
Real WrapCoord(const Real x, const Real xmin, const Real len, const bool periodic) {
  if (!periodic) return x;
  Real y = x;
  if (y < xmin) {
    y += len*ceil((xmin - y)/len);
  } else if (y >= xmin + len) {
    y -= len*floor((y - xmin)/len);
  }
  if (y >= xmin + len) { y = xmin; }      // rounding at the upper edge
  return y;
}

//----------------------------------------------------------------------------------------
//! \struct MeshMetric
//! \brief metric functor for the pusher kernels that reads the fields of one MeshBlock.
//! m0 and m1 hold alpha, beta^i and gamma_ij (layout NrpicMetricIndex) at the old and
//! new time levels, including ghost cells.  The four-point stencil is shifted inward
//! where it would leave the allocated cells, which turns the reconstruction into an
//! extrapolation with the same cubic polynomial.

struct MeshMetric {
  DvceArray5D<Real> m0, m1;
  int m;              // MeshBlock index within the pack
  Real xmin[3];       // lower edge of the active region of the MeshBlock
  Real idx[3];        // inverse cell spacing
  int ist[3];         // index of the first active cell in each direction
  int ncell[3];       // number of cells including ghost cells in each direction
  bool is_static;
  bool bspline = false;   // m0, m1 hold sharpened values: cubic B-spline weights

  KOKKOS_INLINE_FUNCTION
  bool IsStatic() const { return is_static; }

  KOKKOS_INLINE_FUNCTION
  void Gather(const DvceArray5D<Real> &a, const Real x[3], AdmPoint &p) const {
    int ib[3];
    Real w[3][4], dw[3][4];
    for (int d=0; d<3; ++d) {
      Real xi = (x[d] - xmin[d])*idx[d] - 0.5;      // cell-centre coordinate
      int i0 = ist[d] + static_cast<int>(floor(xi));
      i0 = (i0 < 1) ? 1 : i0;
      i0 = (i0 > ncell[d]-3) ? ncell[d]-3 : i0;
      ib[d] = i0;
      if (bspline) {
        BSplineWeights(xi - static_cast<Real>(i0 - ist[d]), w[d], dw[d]);
      } else {
        HermiteWeights(xi - static_cast<Real>(i0 - ist[d]), w[d], dw[d]);
      }
      for (int n=0; n<4; ++n) { dw[d][n] *= idx[d]; }
    }
    Real v[NRM_NVAR], dv[3][NRM_NVAR];
    for (int n=0; n<NRM_NVAR; ++n) {
      v[n] = 0.0;
      dv[0][n] = 0.0; dv[1][n] = 0.0; dv[2][n] = 0.0;
    }
    for (int c=0; c<4; ++c) {
      const int k = ib[2] + c - 1;
      for (int b=0; b<4; ++b) {
        const int j = ib[1] + b - 1;
        const Real wyz = w[1][b]*w[2][c];
        const Real dwy = dw[1][b]*w[2][c];
        const Real dwz = w[1][b]*dw[2][c];
        for (int aa=0; aa<4; ++aa) {
          const int i = ib[0] + aa - 1;
          const Real ww  = w[0][aa]*wyz;
          const Real wdx = dw[0][aa]*wyz;
          const Real wdy = w[0][aa]*dwy;
          const Real wdz = w[0][aa]*dwz;
          for (int n=0; n<NRM_NVAR; ++n) {
            const Real val = a(m,n,k,j,i);
            v[n] += ww*val;
            dv[0][n] += wdx*val;
            dv[1][n] += wdy*val;
            dv[2][n] += wdz*val;
          }
        }
      }
    }
    p.alp = v[NRM_ALP];
    p.beta[0] = v[NRM_BX]; p.beta[1] = v[NRM_BY]; p.beta[2] = v[NRM_BZ];
    p.g[0][0] = v[NRM_GXX]; p.g[0][1] = v[NRM_GXY]; p.g[0][2] = v[NRM_GXZ];
    p.g[1][1] = v[NRM_GYY]; p.g[1][2] = v[NRM_GYZ]; p.g[2][2] = v[NRM_GZZ];
    p.g[1][0] = p.g[0][1]; p.g[2][0] = p.g[0][2]; p.g[2][1] = p.g[1][2];
    for (int d=0; d<3; ++d) {
      p.dalp[d] = dv[d][NRM_ALP];
      p.dbeta[d][0] = dv[d][NRM_BX];
      p.dbeta[d][1] = dv[d][NRM_BY];
      p.dbeta[d][2] = dv[d][NRM_BZ];
      p.dg[d][0][0] = dv[d][NRM_GXX]; p.dg[d][0][1] = dv[d][NRM_GXY];
      p.dg[d][0][2] = dv[d][NRM_GXZ]; p.dg[d][1][1] = dv[d][NRM_GYY];
      p.dg[d][1][2] = dv[d][NRM_GYZ]; p.dg[d][2][2] = dv[d][NRM_GZZ];
      p.dg[d][1][0] = p.dg[d][0][1]; p.dg[d][2][0] = p.dg[d][0][2];
      p.dg[d][2][1] = p.dg[d][1][2];
    }
  }

  KOKKOS_INLINE_FUNCTION
  void operator()(const int lev, const Real x[3], AdmPoint &p) const {
    if (lev == 0 && !is_static) {
      Gather(m0, x, p);
    } else {
      Gather(m1, x, p);
    }
  }
};

} // namespace nrpic
#endif // PARTICLES_NRPIC_MESH_HPP_
