#ifndef UTILS_INLINE_INTERPOLATOR_HPP_
#define UTILS_INLINE_INTERPOLATOR_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file inline_interpolator.hpp
//! \brief The following is a wrapper of the Lagrange interpolator
//!             to be used inside a Kokkos kernel.
#include <cmath>
#include <iostream>
#include <list>

#include "athena.hpp"
#include "athena_tensor.hpp"
#include "coordinates/cell_locations.hpp"
#include "mesh/mesh.hpp"

template <int NGHOST>
struct IndAndWghts {
  int ii0, ii1, ii2, ii3;
  Real wght1[2 * NGHOST];
  Real wght2[2 * NGHOST];
  Real wght3[2 * NGHOST];
  bool point_exist;
};

template <int NGHOST>
KOKKOS_INLINE_FUNCTION
IndAndWghts<NGHOST> IndicesAndWeights(
  const RegionIndcs &indcs,
  const DualArray1D<RegionSize> &size,
  Real rcoords[3],
  int nmb
) {
  IndAndWghts<NGHOST> result;

  // **INTERPOLATION INDICES**
  result.ii0 = result.ii1 = result.ii2 = result.ii3 = -1;
  result.point_exist = false;

  for (int m = 0; m < nmb; ++m) {
    // extract MeshBlock bounds
    auto mb = size.d_view(m);

    // save MeshBlock and zone indicies for nearest position to spherical patch
    // center if this angle position resides in this MeshBlock
    if (
      (rcoords[0] >= mb.x1min && rcoords[0] < mb.x1max)
      && (rcoords[1] >= mb.x2min && rcoords[1] < mb.x2max)
      && (rcoords[2] >= mb.x3min && rcoords[2] < mb.x3max)) {
      result.point_exist = true;
      result.ii0 = m;
      result.ii1 = static_cast<int>(Kokkos::floor((rcoords[0]
                    - (mb.x1min + mb.dx1 / 2.0)) / mb.dx1));
      result.ii2 = static_cast<int>(Kokkos::floor((rcoords[1]
                    - (mb.x2min + mb.dx2 / 2.0)) / mb.dx2));
      result.ii3 = static_cast<int>(Kokkos::floor((rcoords[2]
                    - (mb.x3min + mb.dx3 / 2.0)) / mb.dx3));

      break;
    }
  }

  // **INTERPOLATION WEIGHTS**
  if (result.ii0 == -1) {
    for (int i = 0; i < 2 * NGHOST; ++i) {
      result.wght1[i] = 0.;
      result.wght2[i] = 0.;
      result.wght3[i] = 0.;
    }
  } else {
    // extract MeshBlock bounds
    auto mb0 = size.d_view(result.ii0);

    // set interpolation weights
    for (int i = 0; i < 2 * NGHOST; ++i) {
      result.wght1[i] = 1.;
      result.wght2[i] = 1.;
      result.wght3[i] = 1.;

      Real x1vpi1 = CellCenterX(result.ii1 - NGHOST + i + 1,
                                indcs.nx1, mb0.x1min, mb0.x1max);
      Real x2vpi1 = CellCenterX(result.ii2 - NGHOST + i + 1,
                                indcs.nx2, mb0.x2min, mb0.x2max);
      Real x3vpi1 = CellCenterX(result.ii3 - NGHOST + i + 1,
                                indcs.nx3, mb0.x3min, mb0.x3max);

      for (int j = 0; j < 2 * NGHOST; ++j) {
        if (j != i) {
          Real x1vpj1 = CellCenterX(result.ii1 - NGHOST + j + 1, indcs.nx1,
                                    mb0.x1min, mb0.x1max);
          result.wght1[i] *= (rcoords[0] - x1vpj1) / (x1vpi1 - x1vpj1);
          Real x2vpj1 = CellCenterX(result.ii2 - NGHOST + j + 1, indcs.nx2,
                                    mb0.x2min, mb0.x2max);
          result.wght2[i] *= (rcoords[1] - x2vpj1) / (x2vpi1 - x2vpj1);
          Real x3vpj1 = CellCenterX(result.ii3 - NGHOST + j + 1, indcs.nx3,
                                    mb0.x3min, mb0.x3max);
          result.wght3[i] *= (rcoords[2] - x3vpj1) / (x3vpi1 - x3vpj1);
        }
      }
    }
  }

  return result;
}

template <int NGHOST>
KOKKOS_INLINE_FUNCTION
Real InterpolateLagrange(
  const DvceArray5D<Real> &val,
  int var,
  const RegionIndcs &indcs,
  IndAndWghts<NGHOST> indcs_wghts
) {
  Real ival = 0.;
  int is = indcs.is;
  int js = indcs.js;
  int ks = indcs.ks;

  if (indcs_wghts.ii0 == -1) { // point not on this rank
    ival = 0.0;
  } else {
    for (int i = 0; i < 2 * NGHOST; i++) {
      for (int j = 0; j < 2 * NGHOST; j++) {
        for (int k = 0; k < 2 * NGHOST; k++) {
          Real iwght = indcs_wghts.wght1[i] * indcs_wghts.wght2[j] * indcs_wghts.wght3[k];
          ival += iwght * val(indcs_wghts.ii0, var,
                              indcs_wghts.ii3 - (NGHOST - k - ks) + 1,
                              indcs_wghts.ii2 - (NGHOST - j - js) + 1,
                              indcs_wghts.ii1 - (NGHOST - i - is) + 1);
        }
      }
    }
  }

  return ival;
}

//----------------------------------------------------------------------------------------
//! \fn InterpolateLagrangeDeriv
//! \brief derivative along direction dir (0,1,2) of the Lagrange interpolant of val at the
//! point rcoords, on the stencil of IndicesAndWeights.  Differentiating the interpolant
//! of a field whose ghost cells are filled avoids interpolating a separately stored
//! derivative array, which would need ghost cells of its own.

template <int NGHOST>
KOKKOS_INLINE_FUNCTION
Real InterpolateLagrangeDeriv(
  const DvceArray5D<Real> &val,
  int var,
  const RegionIndcs &indcs,
  const DualArray1D<RegionSize> &size,
  const Real rcoords[3],
  const IndAndWghts<NGHOST> &iw,
  int dir
) {
  if (iw.ii0 == -1) { return 0.0; }
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  auto mb0 = size.d_view(iw.ii0);
  const int ii = (dir == 0) ? iw.ii1 : ((dir == 1) ? iw.ii2 : iw.ii3);
  const int nx = (dir == 0) ? indcs.nx1 : ((dir == 1) ? indcs.nx2 : indcs.nx3);
  const Real xmin = (dir == 0) ? mb0.x1min : ((dir == 1) ? mb0.x2min : mb0.x3min);
  const Real xmax = (dir == 0) ? mb0.x1max : ((dir == 1) ? mb0.x2max : mb0.x3max);
  const Real x = rcoords[dir];

  // nodes of the stencil and derivative of each Lagrange basis polynomial at x
  Real xn[2 * NGHOST], dw[2 * NGHOST];
  for (int i = 0; i < 2 * NGHOST; ++i) {
    xn[i] = CellCenterX(ii - NGHOST + i + 1, nx, xmin, xmax);
  }
  for (int i = 0; i < 2 * NGHOST; ++i) {
    Real sum = 0.0;
    for (int m = 0; m < 2 * NGHOST; ++m) {
      if (m == i) continue;
      Real prod = 1.0/(xn[i] - xn[m]);
      for (int j = 0; j < 2 * NGHOST; ++j) {
        if (j == i || j == m) continue;
        prod *= (x - xn[j])/(xn[i] - xn[j]);
      }
      sum += prod;
    }
    dw[i] = sum;
  }

  Real ival = 0.0;
  for (int i = 0; i < 2 * NGHOST; i++) {
    const Real w1 = (dir == 0) ? dw[i] : iw.wght1[i];
    for (int j = 0; j < 2 * NGHOST; j++) {
      const Real w2 = (dir == 1) ? dw[j] : iw.wght2[j];
      for (int k = 0; k < 2 * NGHOST; k++) {
        const Real w3 = (dir == 2) ? dw[k] : iw.wght3[k];
        ival += w1*w2*w3*val(iw.ii0, var,
                             iw.ii3 - (NGHOST - k - ks) + 1,
                             iw.ii2 - (NGHOST - j - js) + 1,
                             iw.ii1 - (NGHOST - i - is) + 1);
      }
    }
  }
  return ival;
}

#endif  // UTILS_INLINE_INTERPOLATOR_HPP_
