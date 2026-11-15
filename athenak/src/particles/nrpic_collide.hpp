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
//! frame, the pair kinematics that conserve the canonical energy with the metric at
//! each particle, the index of the mesh cell that contains a coordinate, and an
//! in-place sort.
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
//! \fn CollSigmaMax
//! \brief upper bound of CollSigma over all relative speeds (used for the number of
//! sub-steps); a new model must supply its bound here

KOKKOS_INLINE_FUNCTION
Real CollSigmaMax(const int model, const Real sigma, const Real w) {
  return sigma;          // constant, and cutoff (largest at v_rel = 0)
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
// Pair kinematics with the metric at each particle (<particles> coll_energy = particle).
//
// The two members of a pair sit at different points of one collision cell.  What a pair
// can conserve exactly, whatever the metric, is its canonical four-momentum: the sum of
// the covariant components u_i and the sum of the energies conjugate to the time
// coordinate,
//   H = alpha W - beta^i u_i,   W = sqrt(1 + gamma^ij u_i u_j),
// each with alpha, beta^i, gamma^ij at the particle's own position (the Hamiltonian of
// the geodesic motion that the pushers integrate; the Killing energy in a stationary
// spacetime).  The functions below work with triad components u_(m) of the collision
// cell and with the metric of a particle expressed in that triad (CollOwnMetric).
// Design and tests: tracks/core/interfaces/collisions.md, section 11.

//! \struct CollOwnMetric
//! \brief lapse, shift and inverse spatial metric at the position of one particle, in
//! the triad of its collision cell (coframe e^(m)_i = S[i][m]):
//!   b[m] = e^(m)_i beta^i,   g[m][n] = e^(m)_i e^(n)_j gamma^ij,
//! so that beta^i u_i = b[m] u_(m) and gamma^ij u_i u_j = g[m][n] u_(m) u_(n).  For a
//! particle at the cell centre g is the unit matrix.

struct CollOwnMetric {
  Real alp;
  Real b[3];
  Real g[3][3];
};

//----------------------------------------------------------------------------------------
//! \fn CollEnergy
//! \brief kinetic part of the canonical energy per unit rest mass of a particle with
//! triad momentum u, h = alpha (W - 1) - b.u (H = alpha + h; W - 1 without
//! cancellation), and its derivative v[m] = dh/du_(m) = alpha g[m][n] u_(n)/W - b[m],
//! the coordinate velocity dx^i/dt of the particle in triad components, e^(m)_i dx^i/dt.

KOKKOS_INLINE_FUNCTION
Real CollEnergy(const CollOwnMetric &m, const Real u[3], Real v[3]) {
  Real y[3];
  Real x = 0.0, bu = 0.0;
  for (int i=0; i<3; ++i) {
    y[i] = m.g[i][0]*u[0] + m.g[i][1]*u[1] + m.g[i][2]*u[2];
    x += y[i]*u[i];
    bu += m.b[i]*u[i];
  }
  const Real w = sqrt(1.0 + x);
  for (int i=0; i<3; ++i) { v[i] = m.alp*y[i]/w - m.b[i]; }
  return m.alp*x/(1.0 + w) - bu;
}

//----------------------------------------------------------------------------------------
//! \fn CollCentre
//! \brief momentum dl that particle b hands to particle a before the pair is treated as
//! a pair of the cell frame: u~_a = u_a - dl, u~_b = u_b + dl.  At fixed total momentum
//! P the energy of the pair is smallest where both members have the same coordinate
//! velocity, v_a(q) = v_b(P - q); that state takes the place of "both at P/2" of a pair
//! in one metric.  dl is the first Newton step from q = P/2 towards it, with the Hessian
//! of the cell centre (lapse alpc, unit spatial metric in the triad):
//!   dl = -(W0/(2 alpc)) [ d + q (q.d) ],  d = v_a(P/2) - v_b(P/2),  W0 = sqrt(1+|q|^2).
//! It vanishes identically for equal metrics and is of first order in the difference of
//! the metric between the two particles.

KOKKOS_INLINE_FUNCTION
void CollCentre(const Real alpc, const CollOwnMetric &ma, const CollOwnMetric &mb,
                const Real ua[3], const Real ub[3], Real dl[3]) {
  const Real q[3] = {0.5*(ua[0] + ub[0]), 0.5*(ua[1] + ub[1]), 0.5*(ua[2] + ub[2])};
  Real va[3], vb[3];
  CollEnergy(ma, q, va);
  CollEnergy(mb, q, vb);
  const Real d[3] = {va[0] - vb[0], va[1] - vb[1], va[2] - vb[2]};
  const Real w0 = sqrt(1.0 + q[0]*q[0] + q[1]*q[1] + q[2]*q[2]);
  const Real qd = q[0]*d[0] + q[1]*d[1] + q[2]*d[2];
  const Real c = -0.5*w0/alpc;
  for (int i=0; i<3; ++i) { dl[i] = c*(d[i] + q[i]*qd); }
}

//----------------------------------------------------------------------------------------
//! \fn CollScatterRel
//! \brief the part of CollScatter that is odd in the direction: wv = u_a' - P/2 for the
//! direction nhat, without the cancellation of that difference

KOKKOS_INLINE_FUNCTION
void CollScatterRel(const Real ua[3], const Real ub[3], const Real wa, const Real wb,
                    const Real g1, const Real nhat[3], Real wv[3]) {
  const Real pt[3] = {ua[0] + ub[0], ua[1] + ub[1], ua[2] + ub[2]};
  const Real et = wa + wb;
  const Real rs = sqrt(4.0 + 2.0*g1);
  const Real ps = sqrt(0.5*g1);
  const Real ndp = nhat[0]*pt[0] + nhat[1]*pt[1] + nhat[2]*pt[2];
  const Real cf = ps*ndp/(rs*(et + rs));
  for (int i=0; i<3; ++i) { wv[i] = ps*nhat[i] + cf*pt[i]; }
}

//----------------------------------------------------------------------------------------
//! \fn CollEnergyRoot
//! \brief new momenta of a pair that conserve the sum of the canonical energies of its
//! two members exactly: u_a' = ca + lam wv, u_b' = pt - u_a', with pt the momentum of
//! the pair, ca the share of particle a in the split at equal coordinate velocity
//! (P/2 + dl of CollCentre; cb = pt - ca), wv the relative momentum of the collision in
//! the cell frame (CollScatterRel) and lam > 0 the root of
//!   F(lam) = h_a(ca + lam wv) + h_b(cb - lam wv) - e0 = 0,
//! e0 the sum of the two energies before the collision.  F is convex in lam and F(0) < 0
//! when the split lies inside the energy surface, so the root is unique; Newton
//! iteration from lam = 1 (the collision of the cell frame) converges to it from any
//! side.  Returns false, with the momenta undefined, if F(0) >= 0 or no root is found
//! (a pair whose relative velocity is not resolved against the difference of the
//! metric): the caller leaves the pair as it is.  res is F at the returned momenta: at
//! most 16 units in the last place of the energies involved, or, if the iteration ends
//! without reaching that, 1e-12 of them.

KOKKOS_INLINE_FUNCTION
bool CollEnergyRoot(const CollOwnMetric &ma, const CollOwnMetric &mb, const Real pt[3],
                    const Real ca[3], const Real wv[3], const Real e0, Real uan[3],
                    Real ubn[3], Real &lam, Real &res) {
  const Real cb[3] = {pt[0] - ca[0], pt[1] - ca[1], pt[2] - ca[2]};
  Real va[3], vb[3];
  lam = 0.0;
  res = CollEnergy(ma, ca, va) + CollEnergy(mb, cb, vb) - e0;
  if (!(res < 0.0)) return false;
  lam = 1.0;
  Real scale = 0.0;
  for (int it=0; it<40; ++it) {
    for (int i=0; i<3; ++i) {
      uan[i] = ca[i] + lam*wv[i];
      ubn[i] = pt[i] - uan[i];
    }
    const Real ea = CollEnergy(ma, uan, va);
    const Real eb = CollEnergy(mb, ubn, vb);
    res = ea + eb - e0;
    scale = fabs(ea) + fabs(eb) + fabs(e0);
    if (fabs(res) <= 3.6e-15*scale) return true;
    const Real df = wv[0]*(va[0] - vb[0]) + wv[1]*(va[1] - vb[1]) + wv[2]*(va[2] - vb[2]);
    if (!(df > 0.0)) return false;
    lam -= res/df;
    if (!(lam > 0.0)) return false;          // also a lam that is not a number
  }
  // the last momenta belong to the lam before the last correction
  return (fabs(res) <= 1.0e-12*scale);
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
