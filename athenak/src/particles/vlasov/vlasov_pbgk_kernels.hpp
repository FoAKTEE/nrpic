#ifndef PARTICLES_VLASOV_VLASOV_PBGK_KERNELS_HPP_
#define PARTICLES_VLASOV_VLASOV_PBGK_KERNELS_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_pbgk_kernels.hpp
//! \brief Standalone & GPU-safe device kernels for conservative relativistic Cell-BGK:
//!   - LorentzBoostMom: exact special-relativistic momentum boost without cancellation
//!   - SampleMaxwellJuttner: exact unified Gamma-mixture rejection across all Theta > 0
//!     driven by deterministic Philox RNG (utils/rng.hpp)
//!   - ProjectCellFourMomentumT: exact (E_c, P_c) 4-momentum projection for arbitrary
//!     particle weights and arbitrarily many particles per cell with O(N_c) cost.

#include <cmath>
#include <cstdint>

#include "vlasov_math.hpp"
#include "../../utils/rng.hpp"

namespace nrpic {
namespace vlasov {

//----------------------------------------------------------------------------------------
//! \fn LorentzBoostMom
//! \brief Special-relativistic momentum boost of rest-mass-normalized 3-momentum q
//! by 4-velocity (U0, U) where U0 = sqrt(1 + |U|^2):
//!   q' = q + [ (U.q)/(U0 + 1) + sqrt(1 + |q|^2) ] U.
//! Pass -U to boost into the rest frame of (U0, U).

KOKKOS_INLINE_FUNCTION
void LorentzBoostMom(Real U0, const Real U[3], const Real q[3], Real q_out[3]) {
  const Real w = sqrt(1.0 + q[0]*q[0] + q[1]*q[1] + q[2]*q[2]);
  const Real udq = U[0]*q[0] + U[1]*q[1] + U[2]*q[2];
  const Real denom = (U0 + 1.0 > 1.0) ? (U0 + 1.0) : 1.0;
  const Real fac = udq / denom + w;
  q_out[0] = q[0] + fac * U[0];
  q_out[1] = q[1] + fac * U[1];
  q_out[2] = q[2] + fac * U[2];
}

//----------------------------------------------------------------------------------------
//! \fn SampleMaxwellJuttner
//! \brief Exact isotropic Maxwell-Juttner momentum draw via Sobol/Gamma-mixture
//! rejection with global majorant:
//!   f(x) = x^{1/2} (1 + x) sqrt(2 + x) exp(-x / Theta)
//!        <= (sqrt(2) x^{1/2} + 2 x^{3/2} + x^2) exp(-x / Theta),  x = W - 1 >= 0.
//! Since (sqrt(2) + 2 t^2 + t^3)^2 - (1 + t^2)^2 (2 + t^2)
//!     = (4 sqrt(2) - 5) t^2 + 2 sqrt(2) t^3 + 4 t^5 >= 0  for all t = sqrt(x) >= 0,
//! the majorant holds globally across all Theta > 0 with >65% acceptance.

KOKKOS_INLINE_FUNCTION
void SampleMaxwellJuttner(Real theta, const rng::Key &key,
                          std::uint64_t draw_base, Real q_out[3]) {
  if (!(theta > 1.0e-12)) {
    q_out[0] = q_out[1] = q_out[2] = 0.0;
    return;
  }
  constexpr Real kSqrt2      = 1.4142135623730950488;
  constexpr Real kW2Coef     = 2.1213203435596425732;  // 3 / sqrt(2)
  constexpr Real kW3Coef     = 1.5957691216057307118;  // sqrt(8 / pi)
  const Real w2 = kW2Coef * theta;
  const Real w3 = kW3Coef * theta * sqrt(theta);
  const Real inv_tot = 1.0 / (1.0 + w2 + w3);
  const Real p1 = inv_tot;
  const Real p12 = (1.0 + w2) * inv_tot;

  Real x_acc = 0.0;
  bool accepted = false;
  for (int it = 0; it < 64; ++it) {
    const std::uint64_t d_off = draw_base + static_cast<std::uint64_t>(4 * it);
    double u4[4], z2[2];
    rng::Uniform4(key, d_off, u4);
    Real x = 0.0;
    if (u4[0] < p1) {
      // Gamma(3/2, theta)
      rng::Normal2(key, d_off + 1, z2);
      const Real z3 = rng::Normal(key, d_off + 2);
      x = 0.5 * theta * (z2[0]*z2[0] + z2[1]*z2[1] + z3*z3);
    } else if (u4[0] < p12) {
      // Gamma(5/2, theta) = Gamma(3/2, theta) + Exp(theta)
      rng::Normal2(key, d_off + 1, z2);
      const Real z3 = rng::Normal(key, d_off + 2);
      const Real e1 = -theta * log((u4[1] > 1.0e-300) ? u4[1] : 1.0e-300);
      x = 0.5 * theta * (z2[0]*z2[0] + z2[1]*z2[1] + z3*z3) + e1;
    } else {
      // Gamma(3, theta)
      const Real prod = ((u4[1] > 1.0e-100) ? u4[1] : 1.0e-100)
                      * ((u4[2] > 1.0e-100) ? u4[2] : 1.0e-100)
                      * ((u4[3] > 1.0e-100) ? u4[3] : 1.0e-100);
      x = -theta * log((prod > 1.0e-300) ? prod : 1.0e-300);
    }

    // Factor out sqrt(x) from both f(x) and h(x) to avoid 0/0 at x -> 0.
    const Real maj = kSqrt2 + x * (2.0 + sqrt(x));
    const Real tgt = (1.0 + x) * sqrt(2.0 + x);
    double u_acc = (u4[0] < p1) ? u4[1] : ((u4[0] < p12) ? u4[2] : rng::Uniform(key, d_off + 3));
    if (u_acc * maj <= tgt) {
      x_acc = x;
      accepted = true;
      break;
    }
  }
  if (!accepted) {
    // Fallback after 64 draws: mean kinetic energy (fallback prob < 1e-34)
    x_acc = 1.5 * theta;
  }
  const Real umag = sqrt(fmax(x_acc * (x_acc + 2.0), 0.0));
  double dir[3];
  rng::Direction(key, draw_base + 512, dir);
  q_out[0] = umag * dir[0];
  q_out[1] = umag * dir[1];
  q_out[2] = umag * dir[2];
}

//----------------------------------------------------------------------------------------
//! \fn ProjectCellFourMomentumT
//! \brief Exact relativistic 4-momentum projection of n unequal-weight particles in a
//! collision cell onto target (M_c, E_c, P_c):
//!   1. Boosts post-draw momenta q_p into their own COM frame (sum m_p q*_p = 0)
//!   2. Solves strictly convex F(s) = sum m_p sqrt(1 + s^2 |q*_p|^2) = M_inv via
//!      safeguarded Newton + bisection to |F - M_inv| <= 1e-15 * M_inv
//!   3. Boosts s* q*_p forward by (E_c, P_c)/M_inv.
//! Operates in O(n) memory via GetM, GetQ, SetQ callbacks.

template <typename GetM, typename GetQ, typename SetQ>
KOKKOS_INLINE_FUNCTION
bool ProjectCellFourMomentumT(int n, GetM &&get_m, GetQ &&get_q, SetQ &&set_q,
                              Real M_c, Real E_c, const Real P_c[3]) {
  if (n < 1 || !(M_c > 0.0)) return false;

  const Real P2_tgt = P_c[0]*P_c[0] + P_c[1]*P_c[1] + P_c[2]*P_c[2];
  const Real Minv2_tgt = E_c * E_c - P2_tgt;
  if (!(Minv2_tgt > M_c * M_c * (1.0 + 1.0e-28))) return false;
  const Real M_inv_tgt = sqrt(Minv2_tgt);

  Real Et = 0.0, Pt[3] = {0.0, 0.0, 0.0};
  for (int p = 0; p < n; ++p) {
    Real q[3];
    get_q(p, q);
    const Real mp = get_m(p);
    Et += mp * sqrt(1.0 + q[0]*q[0] + q[1]*q[1] + q[2]*q[2]);
    Pt[0] += mp * q[0];
    Pt[1] += mp * q[1];
    Pt[2] += mp * q[2];
  }
  const Real Minv2_post = Et * Et - (Pt[0]*Pt[0] + Pt[1]*Pt[1] + Pt[2]*Pt[2]);
  if (!(Minv2_post > M_c * M_c * (1.0 + 1.0e-28))) return false;
  const Real Minv_post = sqrt(Minv2_post);

  const Real Ut0 = Et / Minv_post;
  const Real Ut_inv[3] = {-Pt[0] / Minv_post, -Pt[1] / Minv_post, -Pt[2] / Minv_post};

  Real Pcom[3] = {0.0, 0.0, 0.0};
  for (int p = 0; p < n; ++p) {
    Real q[3], qcom[3];
    get_q(p, q);
    LorentzBoostMom(Ut0, Ut_inv, q, qcom);
    set_q(p, qcom);
    const Real mp = get_m(p);
    Pcom[0] += mp * qcom[0];
    Pcom[1] += mp * qcom[1];
    Pcom[2] += mp * qcom[2];
  }

  // Eliminate residual floating-point COM drift and check nonzero internal speed
  Real s2_sum = 0.0;
  for (int p = 0; p < n; ++p) {
    Real qc[3];
    get_q(p, qc);
    qc[0] -= Pcom[0] / M_c;
    qc[1] -= Pcom[1] / M_c;
    qc[2] -= Pcom[2] / M_c;
    set_q(p, qc);
    s2_sum += get_m(p) * (qc[0]*qc[0] + qc[1]*qc[1] + qc[2]*qc[2]);
  }
  if (!(s2_sum > 1.0e-28 * M_c)) return false;

  auto eval_F = [&](Real s, Real &F_val, Real &dF_val) {
    Real fv = 0.0, df = 0.0;
    const Real s2 = s * s;
    for (int p = 0; p < n; ++p) {
      Real qc[3];
      get_q(p, qc);
      const Real mp = get_m(p);
      const Real q2 = qc[0]*qc[0] + qc[1]*qc[1] + qc[2]*qc[2];
      const Real W = sqrt(1.0 + s2 * q2);
      fv += mp * W;
      df += mp * s * q2 / W;
    }
    F_val = fv;
    dF_val = df;
  };

  Real slo = 0.0;
  Real shi = sqrt(fmax(M_inv_tgt * M_inv_tgt / (M_c * M_c) - 1.0, 1.0));
  Real Fhi = 0.0, dFhi = 0.0;
  for (int b = 0; b < 48; ++b) {
    eval_F(shi, Fhi, dFhi);
    if (Fhi >= M_inv_tgt) break;
    slo = shi;
    shi *= 2.0;
  }
  if (!(Fhi >= M_inv_tgt)) return false;

  Real s = (1.0 > slo && 1.0 < shi) ? 1.0 : (0.5 * (slo + shi));
  for (int it = 0; it < 32; ++it) {
    Real Fs = 0.0, dFs = 0.0;
    eval_F(s, Fs, dFs);
    const Real diff = Fs - M_inv_tgt;
    if (fabs(diff) <= 1.0e-15 * M_inv_tgt) break;
    if (diff < 0.0) slo = s;
    else            shi = s;
    Real s_next = (dFs > 1.0e-30) ? (s - diff / dFs) : (0.5 * (slo + shi));
    if (!(s_next > slo && s_next < shi)) s_next = 0.5 * (slo + shi);
    if (fabs(s_next - s) <= 1.0e-15 * (1.0 + s)) {
      s = s_next;
      break;
    }
    s = s_next;
  }

  const Real U0_tgt = E_c / M_inv_tgt;
  const Real U_tgt[3] = {P_c[0] / M_inv_tgt, P_c[1] / M_inv_tgt, P_c[2] / M_inv_tgt};
  for (int p = 0; p < n; ++p) {
    Real qc[3], qs[3], qout[3];
    get_q(p, qc);
    qs[0] = s * qc[0];
    qs[1] = s * qc[1];
    qs[2] = s * qc[2];
    LorentzBoostMom(U0_tgt, U_tgt, qs, qout);
    set_q(p, qout);
  }
  return true;
}

}  // namespace vlasov
}  // namespace nrpic

#endif  // PARTICLES_VLASOV_VLASOV_PBGK_KERNELS_HPP_
