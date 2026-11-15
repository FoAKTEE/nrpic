#ifndef PARTICLES_NRPIC_COLLIDE_HPP_
#define PARTICLES_NRPIC_COLLIDE_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_collide.hpp
//! \brief Point kernels of the Monte Carlo collision operator of the NRPIC module
//! (nrpic_collide.cpp): the invariant gamma_rel - 1 of a pair, its Moller speed, the
//! cross-section per unit mass, elastic isotropic scattering in the centre-of-momentum
//! frame, the index of the mesh cell that contains a coordinate, and an in-place sort.
//! All momenta are components u_(m) of the momentum per unit rest mass in an orthonormal
//! frame; the physical particles have equal masses.
//!
//! The file has no dependence on the rest of AthenaK.  Define NRPIC_STANDALONE to
//! compile it outside the code (tracks/core/analysis/collisions/kernel_test.cpp).
//! Design and tests: tracks/core/interfaces/collisions.md.

#include <cmath>
#include <cstdint>

#ifdef NRPIC_STANDALONE
using Real = double;
#ifndef KOKKOS_INLINE_FUNCTION
#define KOKKOS_INLINE_FUNCTION inline
#endif
#else
#include "athena.hpp"
#endif

namespace nrpic {

// velocity dependence of the cross-section per unit mass (<particles> coll_sigma_model)
enum CollSigmaModel { kCollSigmaConstant = 0, kCollSigmaCutoff = 1 };

//----------------------------------------------------------------------------------------
//! \fn CollGammaRelM1
//! \brief g1 = gamma_rel - 1 = W_a W_b - u_a.u_b - 1 of two particles, without the
//! cancellation of that expression (which loses eps W^2/g1 relative).  Also returns the
//! Lorentz factors W = sqrt(1 + |u|^2).  With D = u_a - u_b, S = u_a + u_b, e = S/|S|:
//!   2 g1 = |D|^2 - (W_a - W_b)^2,  W_a - W_b = D.S/(W_a + W_b),
//!   (W_a + W_b)^2 - |S|^2 = 2 (g1 + 2),
//! so that with r = (D.e)^2/(W_a + W_b)^2:  g1 = (|D x e|^2 + 4 r)/(2 (1 - r)).  For
//! r > 1/2 (one particle much faster than the other, or nearly opposite directions) the
//! form g1 = [cosh(eta_a - eta_b) - 1] + a b (1 - cos psi) is used, with the rapidities
//! eta, a = |u_a|, b = |u_b| and the angle psi between the momenta.

KOKKOS_INLINE_FUNCTION
Real CollGammaRelM1(const Real ua[3], const Real ub[3], Real &wa, Real &wb) {
  const Real a2 = ua[0]*ua[0] + ua[1]*ua[1] + ua[2]*ua[2];
  const Real b2 = ub[0]*ub[0] + ub[1]*ub[1] + ub[2]*ub[2];
  wa = sqrt(1.0 + a2);
  wb = sqrt(1.0 + b2);
  const Real d[3] = {ua[0] - ub[0], ua[1] - ub[1], ua[2] - ub[2]};
  const Real s[3] = {ua[0] + ub[0], ua[1] + ub[1], ua[2] + ub[2]};
  const Real d2 = d[0]*d[0] + d[1]*d[1] + d[2]*d[2];
  const Real smax = fmax(fabs(s[0]), fmax(fabs(s[1]), fabs(s[2])));
  if (!(smax > 0.0)) return 0.5*d2;              // S = 0: W_a = W_b
  Real e[3] = {s[0]/smax, s[1]/smax, s[2]/smax};
  const Real ie = 1.0/sqrt(e[0]*e[0] + e[1]*e[1] + e[2]*e[2]);
  e[0] *= ie; e[1] *= ie; e[2] *= ie;
  const Real dpar = d[0]*e[0] + d[1]*e[1] + d[2]*e[2];
  const Real c[3] = {d[1]*e[2] - d[2]*e[1], d[2]*e[0] - d[0]*e[2], d[0]*e[1] - d[1]*e[0]};
  const Real dperp2 = c[0]*c[0] + c[1]*c[1] + c[2]*c[2];
  const Real wsum = wa + wb;
  const Real r = (dpar/wsum)*(dpar/wsum);
  if (r <= 0.5) return (dperp2 + 4.0*r)/(2.0*(1.0 - r));
  const Real a = sqrt(a2), b = sqrt(b2);
  const Real sh = (a - b)*(a + b)/(a*wb + b*wa);   // sinh(eta_a - eta_b)
  Real g1 = sh*sh/(sqrt(1.0 + sh*sh) + 1.0);
  if (a > 0.0 && b > 0.0) {
    const Real h[3] = {ua[0]/a - ub[0]/b, ua[1]/a - ub[1]/b, ua[2]/a - ub[2]/b};
    g1 += a*b*0.5*(h[0]*h[0] + h[1]*h[1] + h[2]*h[2]);
  }
  return g1;
}

//----------------------------------------------------------------------------------------
//! \fn CollMoller
//! \brief Moller speed sqrt(gamma_rel^2 - 1)/(W_a W_b) of a pair (between 0 and 2).  The
//! number of collisions per unit volume and time of the frame in which the two particle
//! densities are n_a W_a and n_b W_b is n_a W_a n_b W_b sigma v_Mol.

KOKKOS_INLINE_FUNCTION
Real CollMoller(const Real g1, const Real wa, const Real wb) {
  return sqrt(g1*(g1 + 2.0))/(wa*wb);
}

//----------------------------------------------------------------------------------------
//! \fn CollSigma
//! \brief cross-section per unit mass of a pair with the invariant g1 = gamma_rel - 1.
//! This is the only place where a velocity dependence enters: the relative speed of the
//! pair (the speed of one particle in the rest frame of the other) is
//! v_rel = sqrt(g1 (g1 + 2))/(g1 + 1).
//!   kCollSigmaConstant  sigma
//!   kCollSigmaCutoff    sigma / (1 + (v_rel/w)^2)^2

KOKKOS_INLINE_FUNCTION
Real CollSigma(const int model, const Real sigma, const Real w, const Real g1) {
  if (model == kCollSigmaCutoff) {
    const Real v2 = g1*(g1 + 2.0)/((g1 + 1.0)*(g1 + 1.0));
    const Real q = 1.0 + v2/(w*w);
    return sigma/(q*q);
  }
  return sigma;
}

//----------------------------------------------------------------------------------------
//! \fn CollScatter
//! \brief elastic scattering of two particles of equal mass: new momenta for the
//! direction nhat (unit vector) of particle a in the centre-of-momentum frame, which is
//! reached from the frame of the input by the boost without rotation.  With P = u_a +
//! u_b, E = W_a + W_b, s = E^2 - |P|^2 = 4 + 2 g1, |p*| = sqrt(g1/2), E* = sqrt(s)/2:
//!   u_a' = |p*| nhat + P [ |p*| (nhat.P)/(sqrt(s) (E + sqrt(s))) + 1/2 ],
//!   u_b' = P - u_a'.
//! The momentum of the pair is conserved by construction, its energy to rounding.

KOKKOS_INLINE_FUNCTION
void CollScatter(const Real ua[3], const Real ub[3], const Real wa, const Real wb,
                 const Real g1, const Real nhat[3], Real uan[3], Real ubn[3]) {
  const Real pt[3] = {ua[0] + ub[0], ua[1] + ub[1], ua[2] + ub[2]};
  const Real et = wa + wb;
  const Real rs = sqrt(4.0 + 2.0*g1);
  const Real ps = sqrt(0.5*g1);
  const Real ndp = nhat[0]*pt[0] + nhat[1]*pt[1] + nhat[2]*pt[2];
  const Real cf = ps*ndp/(rs*(et + rs)) + 0.5;
  for (int i=0; i<3; ++i) {
    uan[i] = ps*nhat[i] + cf*pt[i];
    ubn[i] = pt[i] - uan[i];
  }
}

//----------------------------------------------------------------------------------------
//! \fn CollCellIndex
//! \brief index i in [0, n) of the cell with face(i) <= x < face(i+1), for n cells
//! between xmin and xmax whose n+1 face positions are stored in face[0..n].  The first
//! guess from the division is corrected with the stored faces, so the result agrees
//! with comparisons against these faces (the edges of the MeshBlocks are among them).

template <class FaceViewT>
KOKKOS_INLINE_FUNCTION
std::int64_t CollCellIndex(const FaceViewT &face, const std::int64_t first,
                           const std::int64_t n, const Real x) {
  const Real xmin = face(first), xmax = face(first + n);
  std::int64_t i = static_cast<std::int64_t>(
      floor((x - xmin)/(xmax - xmin)*static_cast<Real>(n)));
  i = (i < 0) ? 0 : ((i > n-1) ? n-1 : i);
  while (i > 0 && x < face(first + i)) { --i; }
  while (i < n-1 && x >= face(first + i + 1)) { ++i; }
  return i;
}

//----------------------------------------------------------------------------------------
//! \fn CollHeapSort
//! \brief in-place heap sort of n items addressed by position 0..n-1.  less(i, j) says
//! whether the item at position i sorts before the item at position j (a strict total
//! order), swap(i, j) exchanges the two items.  No recursion, no allocation: usable in a
//! device kernel on the segment of one cell.

template <class LessT, class SwapT>
KOKKOS_INLINE_FUNCTION
void CollHeapSort(const int n, const LessT &less, const SwapT &swap) {
  for (int start = n/2 - 1; start >= 0; --start) {
    int root = start;
    while (true) {
      int child = 2*root + 1;
      if (child >= n) break;
      if (child + 1 < n && less(child, child + 1)) { ++child; }
      if (!less(root, child)) break;
      swap(root, child);
      root = child;
    }
  }
  for (int end = n - 1; end > 0; --end) {
    swap(0, end);
    int root = 0;
    while (true) {
      int child = 2*root + 1;
      if (child >= end) break;
      if (child + 1 < end && less(child, child + 1)) { ++child; }
      if (!less(root, child)) break;
      swap(root, child);
      root = child;
    }
  }
}

} // namespace nrpic
#endif // PARTICLES_NRPIC_COLLIDE_HPP_
