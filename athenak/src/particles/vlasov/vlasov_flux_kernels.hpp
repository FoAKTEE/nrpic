#ifndef PARTICLES_VLASOV_VLASOV_FLUX_KERNELS_HPP_
#define PARTICLES_VLASOV_VLASOV_FLUX_KERNELS_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_flux_kernels.hpp
//! \brief Face Riemann flux, Brent root-finding, covariant pairing, realizability
//! repair, relativistic HLLC + Noh thermal conduction, and Anderson-Witting MJ BGK.

#include <cmath>
#include "vlasov_math.hpp"

namespace nrpic {
namespace vlasov {

//----------------------------------------------------------------------------------------
// Orthonormal face triad wrt curved spatial metric gamma_{ij}
//----------------------------------------------------------------------------------------

KOKKOS_INLINE_FUNCTION
bool FaceTriad(const Real g[3][3], const Real A_cov[3],
               Real &normA, Real e_up[3][3], Real e_dn[3][3]) {
  Real gi[3][3];
  const Real det = Inv3Sym(g, gi);
  Real A_up[3] = {0.0, 0.0, 0.0};
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      A_up[i] += gi[i][j] * A_cov[j];
    }
  }
  const Real normA2 = Dot3(A_cov, A_up);
  if (normA2 <= 0.0) {
    normA = 0.0;
    return false;
  }
  normA = sqrt(normA2);
  Real e1[3] = {A_up[0] / normA, A_up[1] / normA, A_up[2] / normA};

  int k0 = 0;
  if (fabs(e1[1]) + 1.0e-10 < fabs(e1[k0])) k0 = 1;
  if (fabs(e1[2]) + 1.0e-10 < fabs(e1[k0])) k0 = 2;
  Real v[3] = {0.0, 0.0, 0.0};
  v[k0] = 1.0;
  const Real proj = MatVecDot3(v, g, e1);
  Real t2[3] = {v[0] - proj*e1[0], v[1] - proj*e1[1], v[2] - proj*e1[2]};
  Real n22 = MatVecDot3(t2, g, t2);
  if (n22 < 1.0e-300) n22 = 1.0e-300;
  const Real inv_n2 = 1.0 / sqrt(n22);
  Real e2[3] = {t2[0]*inv_n2, t2[1]*inv_n2, t2[2]*inv_n2};

  // Right-handed third vector: cross_cov = e1 x e2, e3 = (gi * cross_cov) * sqrt(det)
  const Real cross_cov[3] = {
    e1[1]*e2[2] - e1[2]*e2[1],
    e1[2]*e2[0] - e1[0]*e2[2],
    e1[0]*e2[1] - e1[1]*e2[0]
  };
  const Real sq_det = sqrt(det);
  Real e3[3] = {0.0, 0.0, 0.0};
  for (int i = 0; i < 3; ++i) {
    for (int l = 0; l < 3; ++l) {
      e3[i] += gi[i][l] * cross_cov[l];
    }
    e3[i] *= sq_det;
  }
  const Real inv_n3 = 1.0 / sqrt(MatVecDot3(e3, g, e3));
  for (int i = 0; i < 3; ++i) e3[i] *= inv_n3;

  for (int i = 0; i < 3; ++i) {
    e_up[0][i] = e1[i];
    e_up[1][i] = e2[i];
    e_up[2][i] = e3[i];
  }
  for (int a = 0; a < 3; ++a) {
    for (int i = 0; i < 3; ++i) {
      Real s = 0.0;
      for (int j = 0; j < 3; ++j) s += e_up[a][j] * g[j][i];
      e_dn[a][i] = s;
    }
  }
  return true;
}

//----------------------------------------------------------------------------------------
// Exact 1D-sliced + 2D-cubature one-sided relativistic vacuum Riemann flux
//----------------------------------------------------------------------------------------

KOKKOS_INLINE_FUNCTION
void Gl61dMoments(Real u_lo, Real b_r, Real m_perp, Real beta_F,
                  Real &j0, Real &j1, Real &j2, Real &jE) {
  const Real gl6_x[6] = {
    -9.32469514203151939e-01, -6.61209386466264482e-01, -2.38619186083196905e-01,
     2.38619186083196905e-01,  6.61209386466264482e-01,  9.32469514203151939e-01
  };
  const Real gl6_w[6] = {
    1.71324492379170273e-01, 3.60761573048138717e-01, 4.67913934572691037e-01,
    4.67913934572691037e-01, 3.60761573048138717e-01, 1.71324492379170273e-01
  };
  const Real half = 0.5 * (b_r - u_lo);
  const Real mid  = 0.5 * (b_r + u_lo);
  const Real m2   = m_perp * m_perp;
  j0 = j1 = j2 = jE = 0.0;
  for (int q = 0; q < 6; ++q) {
    const Real u  = mid + half * gl6_x[q];
    const Real w  = half * gl6_w[q];
    const Real W  = sqrt(m2 + u * u);
    const Real fl = u / W - beta_F;
    j0 += w * fl;
    j1 += w * u * fl;
    j2 += w * (u * u) * fl;
    jE += w * W * fl;
  }
}

KOKKOS_INLINE_FUNCTION
Real Gl61dI0(Real u_lo, Real b_r, Real m_perp, Real beta_F) {
  const Real gl6_x[6] = {
    -9.32469514203151939e-01, -6.61209386466264482e-01, -2.38619186083196905e-01,
     2.38619186083196905e-01,  6.61209386466264482e-01,  9.32469514203151939e-01
  };
  const Real gl6_w[6] = {
    1.71324492379170273e-01, 3.60761573048138717e-01, 4.67913934572691037e-01,
    4.67913934572691037e-01, 3.60761573048138717e-01, 1.71324492379170273e-01
  };
  const Real half = 0.5 * (b_r - u_lo);
  const Real mid  = 0.5 * (b_r + u_lo);
  const Real m2   = m_perp * m_perp;
  Real j0 = 0.0;
  for (int q = 0; q < 6; ++q) {
    const Real u = mid + half * gl6_x[q];
    const Real w = half * gl6_w[q];
    const Real W = sqrt(m2 + u * u);
    j0 += w * (u / W - beta_F);
  }
  return j0;
}

KOKKOS_INLINE_FUNCTION
void SliceTopHat1D(Real mu_par, Real s_par, Real m_perp, Real beta_F,
                   Real &I0, Real &I1, Real &I2, Real &IE) {
  if (beta_F >= 1.0) {
    I0 = I1 = I2 = IE = 0.0;
    return;
  }
  const bool has_cut = (beta_F > -1.0);
  const Real u_star = has_cut ? (beta_F * m_perp / sqrt(1.0 - beta_F*beta_F)) : -1.0e300;
  const Real scale = (m_perp > fabs(mu_par)) ? m_perp : fabs(mu_par);
  if (s_par <= 1.0e-14 * scale) {
    if (has_cut && mu_par <= u_star) {
      I0 = I1 = I2 = IE = 0.0;
      return;
    }
    const Real W = sqrt(m_perp*m_perp + mu_par*mu_par);
    const Real fl = mu_par / W - beta_F;
    I0 = fl;
    I1 = mu_par * fl;
    I2 = (mu_par * mu_par) * fl;
    IE = W * fl;
    return;
  }
  const Real hw = kSqrt3 * s_par;
  const Real a_r = mu_par - hw;
  const Real b_r = mu_par + hw;
  const Real u_lo = (has_cut && u_star > a_r) ? u_star : a_r;
  if (u_lo >= b_r) {
    I0 = I1 = I2 = IE = 0.0;
    return;
  }
  const Real inv_w = 1.0 / (2.0 * hw);
  Real j0, j1, j2, jE;
  if ((b_r - u_lo) < 0.25 * m_perp) {
    Gl61dMoments(u_lo, b_r, m_perp, beta_F, j0, j1, j2, jE);
  } else {
    const Real m2 = m_perp * m_perp;
    const Real Wl = sqrt(m2 + u_lo*u_lo);
    const Real Wr = sqrt(m2 + b_r*b_r);
    const Real al = asinh(u_lo / m_perp);
    const Real ar = asinh(b_r / m_perp);
    j0 = (Wr - beta_F*b_r) - (Wl - beta_F*u_lo);
    j1 = 0.5 * ((b_r*Wr - m2*ar - beta_F*b_r*b_r) - (u_lo*Wl - m2*al - beta_F*u_lo*u_lo));
    j2 = ((Wr*(b_r*b_r - 2.0*m2) - beta_F*b_r*b_r*b_r) -
          (Wl*(u_lo*u_lo - 2.0*m2) - beta_F*u_lo*u_lo*u_lo)) / 3.0;
    jE = 0.5 * ((b_r*b_r - beta_F*(b_r*Wr + m2*ar)) - (u_lo*u_lo - beta_F*(u_lo*Wl + m2*al)));
  }
  I0 = j0 * inv_w;
  I1 = j1 * inv_w;
  I2 = j2 * inv_w;
  IE = jE * inv_w;
}

KOKKOS_INLINE_FUNCTION
Real SliceTopHatI0(Real mu_par, Real s_par, Real m_perp, Real beta_F) {
  if (beta_F >= 1.0) return 0.0;
  const bool has_cut = (beta_F > -1.0);
  const Real u_star = has_cut ? (beta_F * m_perp / sqrt(1.0 - beta_F*beta_F)) : -1.0e300;
  const Real scale = (m_perp > fabs(mu_par)) ? m_perp : fabs(mu_par);
  if (s_par <= 1.0e-14 * scale) {
    if (has_cut && mu_par <= u_star) return 0.0;
    const Real W = sqrt(m_perp*m_perp + mu_par*mu_par);
    return mu_par / W - beta_F;
  }
  const Real hw = kSqrt3 * s_par;
  const Real a_r = mu_par - hw;
  const Real b_r = mu_par + hw;
  const Real u_lo = (has_cut && u_star > a_r) ? u_star : a_r;
  if (u_lo >= b_r) return 0.0;
  const Real inv_w = 1.0 / (2.0 * hw);
  if ((b_r - u_lo) < 0.25 * m_perp) {
    return Gl61dI0(u_lo, b_r, m_perp, beta_F) * inv_w;
  }
  const Real m2 = m_perp * m_perp;
  const Real Wl = sqrt(m2 + u_lo*u_lo);
  const Real Wr = sqrt(m2 + b_r*b_r);
  return ((Wr - beta_F*b_r) - (Wl - beta_F*u_lo)) * inv_w;
}

KOKKOS_INLINE_FUNCTION
void SliceTopHatI0AndDeriv(Real mu_par, Real s_par, Real m_perp, Real beta_F,
                           Real &val, Real &dval) {
  if (beta_F >= 1.0) {
    val = 0.0;
    dval = 0.0;
    return;
  }
  const bool has_cut = (beta_F > -1.0);
  const Real u_star = has_cut ? (beta_F * m_perp / sqrt(1.0 - beta_F*beta_F)) : -1.0e300;
  const Real scale = (m_perp > fabs(mu_par)) ? m_perp : fabs(mu_par);
  if (s_par <= 1.0e-14 * scale) {
    if (has_cut && mu_par <= u_star) {
      val = 0.0;
      dval = 0.0;
      return;
    }
    const Real W = sqrt(m_perp*m_perp + mu_par*mu_par);
    val = mu_par / W - beta_F;
    dval = -1.0;
    return;
  }
  const Real hw = kSqrt3 * s_par;
  const Real a_r = mu_par - hw;
  const Real b_r = mu_par + hw;
  const Real u_lo = (has_cut && u_star > a_r) ? u_star : a_r;
  if (u_lo >= b_r) {
    val = 0.0;
    dval = 0.0;
    return;
  }
  const Real inv_w = 1.0 / (2.0 * hw);
  dval = -(b_r - u_lo) * inv_w;
  if ((b_r - u_lo) < 0.25 * m_perp) {
    val = Gl61dI0(u_lo, b_r, m_perp, beta_F) * inv_w;
    return;
  }
  const Real m2 = m_perp * m_perp;
  const Real Wl = sqrt(m2 + u_lo*u_lo);
  const Real Wr = sqrt(m2 + b_r*b_r);
  val = ((Wr - beta_F*b_r) - (Wl - beta_F*u_lo)) * inv_w;
}

KOKKOS_INLINE_FUNCTION
void OneSidedFluxTetrad(Real D_star, const Real u_bar_tet[3], const Real Sigma_tet[3][3],
                        Real beta_F, int basis_kind, int n_perp,
                        Real &Fm, Real FP[3], Real FPi[3][3], Real &FE) {
  Fm = 0.0;
  FE = 0.0;
  for (int i = 0; i < 3; ++i) {
    FP[i] = 0.0;
    for (int j = 0; j < 3; ++j) FPi[i][j] = 0.0;
  }
  if (D_star <= 0.0 || beta_F >= 1.0) return;

  const Real sig_par2 = (Sigma_tet[0][0] > 0.0) ? Sigma_tet[0][0] : 0.0;
  const Real c[2] = {Sigma_tet[1][0], Sigma_tet[2][0]};
  const Real S_pp[2][2] = {
    {Sigma_tet[1][1], Sigma_tet[1][2]},
    {Sigma_tet[2][1], Sigma_tet[2][2]}
  };
  Real L_p[2][2], L_pi[2][2];
  Chol2Safe(S_pp, L_p, L_pi);
  const Real g_vec[2] = {
    L_pi[0][0]*c[0] + L_pi[0][1]*c[1],
    L_pi[1][0]*c[0] + L_pi[1][1]*c[1]
  };
  const Real g2 = g_vec[0]*g_vec[0] + g_vec[1]*g_vec[1];
  const Real s_par2 = (sig_par2 > g2) ? (sig_par2 - g2) : 0.0;
  const Real s_par = sqrt(s_par2);

  const bool cold_perp = ((S_pp[0][0] + S_pp[1][1]) <= 1.0e-28);

  const Real gl2_xi[2] = {-9.99999999999999889e-01, 9.99999999999999889e-01};
  const Real gl2_w[2]  = {5.0e-01, 5.0e-01};
  const Real gl3_xi[3] = {-1.34164078649987384e+00, 0.0, 1.34164078649987384e+00};
  const Real gl3_w[3]  = {2.77777777777777846e-01, 4.44444444444444420e-01, 2.77777777777777846e-01};
  const Real gh3_xi[3] = {-1.73205080756887742e+00, 0.0, 1.73205080756887742e+00};
  const Real gh3_w[3]  = {1.66666666666666602e-01, 6.66666666666666852e-01, 1.66666666666666602e-01};

  int n1d = cold_perp ? 1 : ((basis_kind == BASIS_TOPHAT) ? ((n_perp == 3) ? 3 : 2) : 3);
  for (int i = 0; i < n1d; ++i) {
    const Real eta0 = cold_perp ? 0.0 : ((basis_kind == BASIS_TOPHAT) ? ((n_perp == 3) ? gl3_xi[i] : gl2_xi[i]) : gh3_xi[i]);
    const Real wi   = cold_perp ? 1.0 : ((basis_kind == BASIS_TOPHAT) ? ((n_perp == 3) ? gl3_w[i]  : gl2_w[i])  : gh3_w[i]);
    for (int j = 0; j < n1d; ++j) {
      const Real eta1 = cold_perp ? 0.0 : ((basis_kind == BASIS_TOPHAT) ? ((n_perp == 3) ? gl3_xi[j] : gl2_xi[j]) : gh3_xi[j]);
      const Real wj   = cold_perp ? 1.0 : ((basis_kind == BASIS_TOPHAT) ? ((n_perp == 3) ? gl3_w[j]  : gl2_w[j])  : gh3_w[j]);
      const Real wr   = wi * wj;
      const Real u1   = u_bar_tet[1] + L_p[0][0]*eta0 + L_p[0][1]*eta1;
      const Real u2   = u_bar_tet[2] + L_p[1][0]*eta0 + L_p[1][1]*eta1;
      const Real mp   = sqrt(1.0 + u1*u1 + u2*u2);
      const Real mup  = u_bar_tet[0] + g_vec[0]*eta0 + g_vec[1]*eta1;
      Real I0, I1, I2, IE;
      SliceTopHat1D(mup, s_par, mp, beta_F, I0, I1, I2, IE);
      if (I0 == 0.0 && I1 == 0.0 && I2 == 0.0) continue;
      const Real wD = wr * D_star;
      const Real w0 = wD * I0;
      const Real w1 = wD * I1;
      Fm        += w0;
      FP[0]     += w1;
      FP[1]     += w0 * u1;
      FP[2]     += w0 * u2;
      FPi[0][0] += wD * I2;
      FPi[0][1] += w1 * u1;
      FPi[1][0] += w1 * u1;
      FPi[0][2] += w1 * u2;
      FPi[2][0] += w1 * u2;
      FPi[1][1] += w0 * u1 * u1;
      FPi[1][2] += w0 * u1 * u2;
      FPi[2][1] += w0 * u1 * u2;
      FPi[2][2] += w0 * u2 * u2;
      FE        += wD * IE;
    }
  }
}

KOKKOS_INLINE_FUNCTION
void OneSidedFluxCoord(Real D_star, const Real u_bar_cov[3], const Real Sigma_cov[3][3],
                       Real alpha_f, Real normA, const Real e_up[3][3], const Real e_dn[3][3],
                       Real beta_F, int basis_kind, int n_perp,
                       Real &Fm, Real FP[3], Real FPi[3][3], Real &FE) {
  Real u_tet[3] = {0.0, 0.0, 0.0};
  Real Sig_tet[3][3];
  for (int m = 0; m < 3; ++m) {
    for (int i = 0; i < 3; ++i) u_tet[m] += e_up[m][i] * u_bar_cov[i];
    for (int n = 0; n < 3; ++n) {
      Real s = 0.0;
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) s += e_up[m][i] * Sigma_cov[i][j] * e_up[n][j];
      }
      Sig_tet[m][n] = s;
    }
  }
  Real FP_tet[3], FPi_tet[3][3];
  OneSidedFluxTetrad(D_star, u_tet, Sig_tet, beta_F, basis_kind, n_perp, Fm, FP_tet, FPi_tet, FE);
  const Real fac = alpha_f * normA;
  Fm *= fac;
  FE *= fac;
  for (int i = 0; i < 3; ++i) {
    Real ps = 0.0;
    for (int m = 0; m < 3; ++m) ps += e_dn[m][i] * FP_tet[m];
    FP[i] = fac * ps;
    for (int j = 0; j < 3; ++j) {
      Real pis = 0.0;
      for (int m = 0; m < 3; ++m) {
        for (int n = 0; n < 3; ++n) pis += e_dn[m][i] * FPi_tet[m][n] * e_dn[n][j];
      }
      FPi[i][j] = fac * pis;
    }
  }
}

//----------------------------------------------------------------------------------------
// Safeguarded Brent root-finder & Mass-preserving face velocity beta_F
//----------------------------------------------------------------------------------------

template <typename Func>
KOKKOS_INLINE_FUNCTION
Real BrentRoot(Func &&f, Real a, Real b, Real xtol = 1.0e-12, Real rtol = 1.0e-12, int max_iter = 120) {
  Real fa = f(a);
  Real fb = f(b);
  if (fa == 0.0) return a;
  if (fb == 0.0) return b;
  if (fa * fb > 0.0) return 0.5 * (a + b);

  Real c = a, fc = fa;
  Real d = b - a, e = d;
  for (int iter = 0; iter < max_iter; ++iter) {
    if ((fb > 0.0 && fc > 0.0) || (fb < 0.0 && fc < 0.0)) {
      c = a; fc = fa;
      d = e = b - a;
    }
    if (fabs(fc) < fabs(fb)) {
      a = b; b = c; c = a;
      fa = fb; fb = fc; fc = fa;
    }
    const Real tol1 = 2.0 * 2.2204460492503131e-16 * fabs(b) + 0.5 * (xtol + rtol * fabs(b));
    const Real xm = 0.5 * (c - b);
    if (fabs(xm) <= tol1 || fb == 0.0) return b;
    if (fabs(e) >= tol1 && fabs(fa) > fabs(fb)) {
      const Real s = fb / fa;
      Real p, q;
      if (a == c) {
        p = 2.0 * xm * s;
        q = 1.0 - s;
      } else {
        const Real q1 = fa / fc;
        const Real r1 = fb / fc;
        p = s * (2.0 * xm * q1 * (q1 - r1) - (b - a) * (r1 - 1.0));
        q = (q1 - 1.0) * (r1 - 1.0) * (s - 1.0);
      }
      if (p > 0.0) q = -q;
      p = fabs(p);
      const Real min1 = 3.0 * xm * q - fabs(tol1 * q);
      const Real min2 = fabs(e * q);
      if (2.0 * p < ((min1 < min2) ? min1 : min2)) {
        e = d;
        d = p / q;
      } else {
        d = xm;
        e = d;
      }
    } else {
      d = xm;
      e = d;
    }
    a = b;
    fa = fb;
    if (fabs(d) > tol1) {
      b += d;
    } else {
      b += (xm >= 0.0) ? tol1 : -tol1;
    }
    fb = f(b);
  }
  return b;
}

template <int MaxNb>
struct FaceSidePrecompT {
  static constexpr int kMaxSlices = MaxNb * 9;
  int n = 0;
  Real w[kMaxSlices];
  Real mu[kMaxSlices];
  Real sp[kMaxSlices];
  Real mp[kMaxSlices];
  Real w_tot = 0.0;
};

using FaceSidePrecomp = FaceSidePrecompT<MAX_BASIS>;

template <int MaxNb>
KOKKOS_INLINE_FUNCTION
void PrecomputeFaceSide(int Nb, const Real D[], const Real u_tet[][3], const Real Sig_tet[][3][3],
                        bool reverse_normal, int basis_kind, int n_perp,
                        FaceSidePrecompT<MaxNb> &out) {
  out.n = 0;
  out.w_tot = 0.0;
  const Real gl2_xi[2] = {-9.99999999999999889e-01, 9.99999999999999889e-01};
  const Real gl2_w[2]  = {5.0e-01, 5.0e-01};
  const Real gl3_xi[3] = {-1.34164078649987384e+00, 0.0, 1.34164078649987384e+00};
  const Real gl3_w[3]  = {2.77777777777777846e-01, 4.44444444444444420e-01, 2.77777777777777846e-01};
  const Real gh3_xi[3] = {-1.73205080756887742e+00, 0.0, 1.73205080756887742e+00};
  const Real gh3_w[3]  = {1.66666666666666602e-01, 6.66666666666666852e-01, 1.66666666666666602e-01};
  const Real sgn = reverse_normal ? -1.0 : 1.0;

  for (int al = 0; al < Nb; ++al) {
    const Real Da = D[al];
    if (Da <= 0.0) continue;
    out.w_tot += Da;
    const Real u0 = sgn * u_tet[al][0];
    const Real u1_0 = u_tet[al][1];
    const Real u2_0 = u_tet[al][2];
    const Real sig_par2 = (Sig_tet[al][0][0] > 0.0) ? Sig_tet[al][0][0] : 0.0;
    const Real c[2] = {sgn * Sig_tet[al][1][0], sgn * Sig_tet[al][2][0]};
    const Real S_pp[2][2] = {
      {Sig_tet[al][1][1], Sig_tet[al][1][2]},
      {Sig_tet[al][2][1], Sig_tet[al][2][2]}
    };
    Real L_p[2][2], L_pi[2][2];
    Chol2Safe(S_pp, L_p, L_pi);
    const Real g_vec[2] = {
      L_pi[0][0]*c[0] + L_pi[0][1]*c[1],
      L_pi[1][0]*c[0] + L_pi[1][1]*c[1]
    };
    const Real g2 = g_vec[0]*g_vec[0] + g_vec[1]*g_vec[1];
    const Real s_par = sqrt((sig_par2 > g2) ? (sig_par2 - g2) : 0.0);
    if ((S_pp[0][0] + S_pp[1][1]) <= 1.0e-28) {
      const int idx = out.n++;
      out.w[idx]  = Da;
      out.mu[idx] = u0;
      out.sp[idx] = s_par;
      out.mp[idx] = sqrt(1.0 + u1_0*u1_0 + u2_0*u2_0);
    } else {
      const int n1d = (basis_kind == BASIS_TOPHAT && n_perp != 3) ? 2 : 3;
      const Real *xi1d = (basis_kind == BASIS_GAUSS) ? gh3_xi : ((n1d == 3) ? gl3_xi : gl2_xi);
      const Real *w1d  = (basis_kind == BASIS_GAUSS) ? gh3_w  : ((n1d == 3) ? gl3_w  : gl2_w);
      for (int i = 0; i < n1d; ++i) {
        const Real e0 = xi1d[i];
        const Real wi = w1d[i];
        for (int j = 0; j < n1d; ++j) {
          const Real e1 = xi1d[j];
          const Real wj = w1d[j];
          const Real u1 = u1_0 + L_p[0][0]*e0 + L_p[0][1]*e1;
          const Real u2 = u2_0 + L_p[1][0]*e0 + L_p[1][1]*e1;
          const int idx = out.n++;
          out.w[idx]  = Da * wi * wj;
          out.mu[idx] = u0 + g_vec[0]*e0 + g_vec[1]*e1;
          out.sp[idx] = s_par;
          out.mp[idx] = sqrt(1.0 + u1*u1 + u2*u2);
        }
      }
    }
  }
}

template <int MaxNb>
KOKKOS_INLINE_FUNCTION
Real EvalSideI0(const FaceSidePrecompT<MaxNb> &s, Real beta_F) {
  Real sum = 0.0;
  for (int q = 0; q < s.n; ++q) {
    sum += s.w[q] * SliceTopHatI0(s.mu[q], s.sp[q], s.mp[q], beta_F);
  }
  return sum;
}

template <int MaxNb>
KOKKOS_INLINE_FUNCTION
void EvalSideI0AndDeriv(const FaceSidePrecompT<MaxNb> &s, Real beta_F,
                        Real &val_out, Real &dval_out) {
  Real sv = 0.0, sd = 0.0;
  for (int q = 0; q < s.n; ++q) {
    Real v, dv;
    SliceTopHatI0AndDeriv(s.mu[q], s.sp[q], s.mp[q], beta_F, v, dv);
    sv += s.w[q] * v;
    sd += s.w[q] * dv;
  }
  val_out = sv;
  dval_out = sd;
}

template <int MaxNb>
KOKKOS_INLINE_FUNCTION
Real SolveFaceBetaFT(int Na, const Real D_a[], const Real u_a_tet[][3], const Real Sig_a_tet[][3][3],
                     int Nb, const Real D_b[], const Real u_b_tet[][3], const Real Sig_b_tet[][3][3],
                     int basis_kind = BASIS_TOPHAT, int n_perp = 3) {
  FaceSidePrecompT<MaxNb> sa, sb;
  PrecomputeFaceSide<MaxNb>(Na, D_a, u_a_tet, Sig_a_tet, false, basis_kind, n_perp, sa);
  PrecomputeFaceSide<MaxNb>(Nb, D_b, u_b_tet, Sig_b_tet, true,  basis_kind, n_perp, sb);
  const Real scale_flux = (sa.w_tot > sb.w_tot) ? sa.w_tot : sb.w_tot;
  if (scale_flux <= 0.0) return 0.0;

  auto net_flux_deriv = [&](Real bF, Real &val, Real &dval) {
    Real va, dva, vb, dvb;
    EvalSideI0AndDeriv<MaxNb>(sa,  bF, va, dva);
    EvalSideI0AndDeriv<MaxNb>(sb, -bF, vb, dvb);
    val  = va - vb;
    dval = dva + dvb;  // <= 0 since d/db(vb(-b)) = -dvb
  };

  Real num = 0.0;
  for (int q = 0; q < sa.n; ++q) {
    const Real v = sa.mu[q] / sqrt(sa.mp[q]*sa.mp[q] + sa.mu[q]*sa.mu[q]);
    num += sa.w[q] * v;
  }
  for (int q = 0; q < sb.n; ++q) {
    const Real v = -sb.mu[q] / sqrt(sb.mp[q]*sb.mp[q] + sb.mu[q]*sb.mu[q]);
    num += sb.w[q] * v;
  }
  const Real denom_w = sa.w_tot + sb.w_tot;
  Real b0 = num / ((denom_w > 1.0e-300) ? denom_w : 1.0e-300);
  if (b0 >  0.99) b0 =  0.99;
  if (b0 < -0.99) b0 = -0.99;

  const Real lo_max = -0.999999999;
  const Real hi_max =  0.999999999;
  Real lo = lo_max, hi = hi_max;
  bool lo_checked = false, hi_checked = false;

  Real rts = b0, f_rts = 0.0, df_rts = 0.0;
  net_flux_deriv(rts, f_rts, df_rts);
  if (fabs(f_rts) <= 1.0e-14 * scale_flux) return rts;

  Real prev_abs_f = fabs(f_rts);
  int stall_cnt = 0;
  for (int iter = 0; iter < 48; ++iter) {
    if (f_rts > 0.0) lo = rts;
    else             hi = rts;

    if (f_rts > 0.0 && df_rts < -1.0e-30 && (rts - f_rts / df_rts) >= hi_max && !hi_checked) {
      Real fh, dfh;
      net_flux_deriv(hi_max, fh, dfh);
      hi_checked = true;
      if (fh >= 0.0) return hi_max;
    } else if (f_rts < 0.0 && df_rts < -1.0e-30 && (rts - f_rts / df_rts) <= lo_max && !lo_checked) {
      Real fl, dfl;
      net_flux_deriv(lo_max, fl, dfl);
      lo_checked = true;
      if (fl <= 0.0) return lo_max;
    }

    bool bisected = false;
    Real cand = 0.0;
    if (stall_cnt >= 3 || df_rts >= -1.0e-30) {
      cand = 0.5 * (lo + hi);
      bisected = true;
      stall_cnt = 0;
    } else {
      cand = rts - f_rts / df_rts;
      if (!(cand > lo && cand < hi)) {
        cand = 0.5 * (lo + hi);
        bisected = true;
        stall_cnt = 0;
      }
    }

    if ((hi - lo) <= 1.0e-13 || (!bisected && fabs(cand - rts) <= 1.0e-13)) {
      return cand;
    }
    rts = cand;
    net_flux_deriv(rts, f_rts, df_rts);
    const Real abs_f = fabs(f_rts);
    if (abs_f <= 1.0e-14 * scale_flux) return rts;
    if (abs_f > 0.5 * prev_abs_f) ++stall_cnt;
    else                          stall_cnt = 0;
    prev_abs_f = abs_f;
  }
  return rts;
}

KOKKOS_INLINE_FUNCTION
Real SolveFaceBetaF(int Na, const Real D_a[], const Real u_a_tet[][3], const Real Sig_a_tet[][3][3],
                    int Nb, const Real D_b[], const Real u_b_tet[][3], const Real Sig_b_tet[][3][3],
                    int basis_kind = BASIS_TOPHAT, int n_perp = 3) {
  const int mx = (Na > Nb) ? Na : Nb;
  if (mx <= 1) return SolveFaceBetaFT<1>(Na, D_a, u_a_tet, Sig_a_tet, Nb, D_b, u_b_tet, Sig_b_tet, basis_kind, n_perp);
  if (mx <= 2) return SolveFaceBetaFT<2>(Na, D_a, u_a_tet, Sig_a_tet, Nb, D_b, u_b_tet, Sig_b_tet, basis_kind, n_perp);
  if (mx <= 4) return SolveFaceBetaFT<4>(Na, D_a, u_a_tet, Sig_a_tet, Nb, D_b, u_b_tet, Sig_b_tet, basis_kind, n_perp);
  return SolveFaceBetaFT<MAX_BASIS>(Na, D_a, u_a_tet, Sig_a_tet, Nb, D_b, u_b_tet, Sig_b_tet, basis_kind, n_perp);
}

//----------------------------------------------------------------------------------------
// Covariant face-rest-frame pairing cost C^eb (Hopkins 2026 Eqs. 26-30)
//----------------------------------------------------------------------------------------

template <int MaxNb>
KOKKOS_INLINE_FUNCTION
void PairingCostMatrixT(int Na, const Real Da[], const Real ua_tet[][3], const Real Siga_tet[][3][3],
                        int Nb, const Real Db[], const Real ub_tet[][3], const Real Sib_tet[][3][3],
                        Real beta_F, Real C_eb[MaxNb][MaxNb],
                        Real lam_D = 0.25, Real eps_tau = 0.04, Real eps_eb = 0.01) {
  const bool use_boost = (fabs(beta_F) < 1.0 - 1.0e-12);
  const Real gam_F = use_boost ? (1.0 / sqrt(1.0 - beta_F*beta_F)) : 1.0;

  Real ua_b[MaxNb][3], ub_b[MaxNb][3];
  Real tra[MaxNb], trb[MaxNb];
  Real Da_tot = 0.0, Db_tot = 0.0;

  for (int al = 0; al < Na; ++al) {
    const Real ux = ua_tet[al][0], uy = ua_tet[al][1], uz = ua_tet[al][2];
    const Real W = sqrt(1.0 + ux*ux + uy*uy + uz*uz);
    ua_b[al][0] = use_boost ? gam_F*(ux - beta_F*W) : ux;
    ua_b[al][1] = uy;
    ua_b[al][2] = uz;
    tra[al] = Siga_tet[al][0][0] + Siga_tet[al][1][1] + Siga_tet[al][2][2];
    Da_tot += Da[al];
  }
  for (int be = 0; be < Nb; ++be) {
    const Real ux = ub_tet[be][0], uy = ub_tet[be][1], uz = ub_tet[be][2];
    const Real W = sqrt(1.0 + ux*ux + uy*uy + uz*uz);
    ub_b[be][0] = use_boost ? gam_F*(ux - beta_F*W) : ux;
    ub_b[be][1] = uy;
    ub_b[be][2] = uz;
    trb[be] = Sib_tet[be][0][0] + Sib_tet[be][1][1] + Sib_tet[be][2][2];
    Db_tot += Db[be];
  }
  if (Da_tot < 1.0e-300) Da_tot = 1.0e-300;
  if (Db_tot < 1.0e-300) Db_tot = 1.0e-300;

  for (int al = 0; al < Na; ++al) {
    const Real ua2 = Dot3(ua_b[al], ua_b[al]);
    Real C_fit = 1.0e300;
    Real C_row[MaxNb];
    for (int be = 0; be < Nb; ++be) {
      const Real ub2 = Dot3(ub_b[be], ub_b[be]);
      const Real du0 = ua_b[al][0] - ub_b[be][0];
      const Real du1 = ua_b[al][1] - ub_b[be][1];
      const Real du2 = ua_b[al][2] - ub_b[be][2];
      const Real diff2 = du0*du0 + du1*du1 + du2*du2;
      const Real uadub = fabs(Dot3(ua_b[al], ub_b[be]));
      const Real denom_u = ua2 + ub2 + 2.0*uadub + tra[al] + trb[be];
      const Real C_u = (denom_u > 0.0) ? (diff2 / denom_u) : 0.0;
      const Real C_D = fabs(Da[al] - Db[be]) / (Da[al] + Db[be] + 0.001*Da_tot);
      C_row[be] = C_u + lam_D * C_D;

      const Real denom_e = (denom_u > 1.0e-300) ? denom_u : 1.0e-300;
      const Real eps_vp2 = 1.0e-4 * denom_e;
      const Real term1 = diff2 / (diff2 + tra[al] + eps_vp2);
      const Real term2 = eps_tau / (1.0 + Db[be] / (eps_eb * Db_tot));
      const Real val = term1 + term2;
      if (val < C_fit) C_fit = val;
    }
    const Real x = (C_fit - 0.5*eps_tau) / eps_tau;
    const Real theta = (x <= 0.0) ? 0.0 : ((x >= 1.0) ? 1.0 : x*x*(3.0 - 2.0*x));
    const Real Da_safe = (Da[al] > 1.0e-300) ? Da[al] : 1.0e-300;
    for (int be = 0; be < Nb; ++be) {
      C_eb[al][be] = C_row[be] * (1.0 - theta / (1.0 + Db[be] / Da_safe));
    }
  }
}

KOKKOS_INLINE_FUNCTION
void PairingCostMatrix(int Na, const Real Da[], const Real ua_tet[][3], const Real Siga_tet[][3][3],
                       int Nb, const Real Db[], const Real ub_tet[][3], const Real Sib_tet[][3][3],
                       Real beta_F, Real C_eb[MAX_BASIS][MAX_BASIS],
                       Real lam_D = 0.25, Real eps_tau = 0.04, Real eps_eb = 0.01) {
  PairingCostMatrixT<MAX_BASIS>(Na, Da, ua_tet, Siga_tet, Nb, Db, ub_tet, Sib_tet,
                                beta_F, C_eb, lam_D, eps_tau, eps_eb);
}

//----------------------------------------------------------------------------------------
// Intra-cell Realizability Repair D (exact cell m, P, Pi conservation)
//----------------------------------------------------------------------------------------

KOKKOS_INLINE_FUNCTION
void RealizabilityRepairCell(int Nb, Real m[], Real P[][3], Real Pi[][3][3],
                             Real eps_m = 1.0e-12, Real eps_S = 1.0e-12, Real S_floor = 1.0e-14) {
  Real m_tot = 0.0;
  Real P_tot[3] = {0.0, 0.0, 0.0};
  for (int al = 0; al < Nb; ++al) {
    m_tot += m[al];
    for (int i = 0; i < 3; ++i) P_tot[i] += P[al][i];
  }
  if (m_tot <= 0.0) return;

  const Real u_bulk[3] = {P_tot[0]/m_tot, P_tot[1]/m_tot, P_tot[2]/m_tot};
  Real floor_m = eps_m * m_tot / Real(Nb);
  if (floor_m < 1.0e-300) floor_m = 1.0e-300;

  bool bad[MAX_BASIS];
  int n_bad = 0;
  for (int al = 0; al < Nb; ++al) {
    bad[al] = (m[al] < floor_m);
    if (bad[al]) ++n_bad;
  }
  if (n_bad > 0 && n_bad < Nb) {
    Real dm_sum = 0.0;
    Real dP_sum[3] = {0.0, 0.0, 0.0};
    Real dPi_sum[3][3] = {{0}};
    Real m_good_sum = 0.0;
    for (int al = 0; al < Nb; ++al) {
      if (bad[al]) {
        dm_sum += m[al] - floor_m;
        for (int i = 0; i < 3; ++i) {
          dP_sum[i] += P[al][i] - floor_m * u_bulk[i];
          for (int j = 0; j < 3; ++j) {
            const Real pi_rst = floor_m * (u_bulk[i]*u_bulk[j] + ((i == j) ? S_floor : 0.0));
            dPi_sum[i][j] += Pi[al][i][j] - pi_rst;
            Pi[al][i][j] = pi_rst;
          }
          P[al][i] = floor_m * u_bulk[i];
        }
        m[al] = floor_m;
      } else {
        m_good_sum += m[al];
      }
    }
    for (int al = 0; al < Nb; ++al) {
      if (!bad[al]) {
        const Real w = m[al] / m_good_sum;
        m[al] += w * dm_sum;
        for (int i = 0; i < 3; ++i) {
          P[al][i] += w * dP_sum[i];
          for (int j = 0; j < 3; ++j) Pi[al][i][j] += w * dPi_sum[i][j];
        }
      }
    }
  }

  // SPD eigenvalue repair on Sigma_alpha
  Real dPi_accum[3][3] = {{0}};
  Real dPi_norm = 0.0;
  int good_idx = 0;
  for (int al = 1; al < Nb; ++al) {
    if (m[al] > m[good_idx]) good_idx = al;
  }
  for (int al = 0; al < Nb; ++al) {
    if (m[al] <= 0.0) continue;
    const Real ua[3] = {P[al][0]/m[al], P[al][1]/m[al], P[al][2]/m[al]};
    Real Sig[3][3];
    for (int i = 0; i < 3; ++i) {
      for (int j = 0; j < 3; ++j) {
        Sig[i][j] = 0.5*(Pi[al][i][j] + Pi[al][j][i])/m[al] - ua[i]*ua[j];
      }
    }
    const Real tr_raw = Sig[0][0] + Sig[1][1] + Sig[2][2];
    if (tr_raw > 0.0) {
      const Real lam_fast = eps_S * tr_raw / 3.0;
      const Real A_chk[3][3] = {
        {Sig[0][0] - lam_fast, Sig[0][1], Sig[0][2]},
        {Sig[1][0], Sig[1][1] - lam_fast, Sig[1][2]},
        {Sig[2][0], Sig[2][1], Sig[2][2] - lam_fast}
      };
      if (IsSpd3Fast(A_chk, 0.0)) continue;
    }
    Real V[3][3], evals[3];
    SymEig3(Sig, V, evals);
    Real tr = 0.0;
    for (int k = 0; k < 3; ++k) tr += (evals[k] > 0.0) ? evals[k] : 0.0;
    const Real lam_min = (tr > 0.0) ? (eps_S * tr / 3.0) : (1.0e-30 * Dot3(ua, ua));
    bool need = false;
    for (int k = 0; k < 3; ++k) {
      if (evals[k] < lam_min) {
        evals[k] = lam_min;
        need = true;
      }
    }
    if (need) {
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
          Real sf = 0.0;
          for (int k = 0; k < 3; ++k) sf += V[i][k] * evals[k] * V[j][k];
          const Real pi_old = Pi[al][i][j];
          Pi[al][i][j] = m[al] * (sf + ua[i]*ua[j]);
          dPi_accum[i][j] += pi_old - Pi[al][i][j];
        }
      }
    }
  }
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) dPi_norm += dPi_accum[i][j]*dPi_accum[i][j];
  }
  if (dPi_norm > 0.0 && m[good_idx] > 0.0) {
    const Real ug[3] = {P[good_idx][0]/m[good_idx], P[good_idx][1]/m[good_idx], P[good_idx][2]/m[good_idx]};
    Real Sig_c[3][3], Pi_c[3][3];
    for (int i = 0; i < 3; ++i) {
      for (int j = 0; j < 3; ++j) {
        Pi_c[i][j] = Pi[good_idx][i][j] + dPi_accum[i][j];
      }
    }
    for (int i = 0; i < 3; ++i) {
      for (int j = 0; j < 3; ++j) {
        Sig_c[i][j] = 0.5*(Pi_c[i][j] + Pi_c[j][i])/m[good_idx] - ug[i]*ug[j];
      }
    }
    Real V[3][3], evals[3];
    SymEig3(Sig_c, V, evals);
    if (evals[0] >= 0.0 && evals[1] >= 0.0 && evals[2] >= 0.0) {
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) Pi[good_idx][i][j] = Pi_c[i][j];
      }
    }
  }
}

//----------------------------------------------------------------------------------------
// Anderson-Witting Maxwell-Juttner BGK relaxation + Relativistic HLLC + Noh conduction
//----------------------------------------------------------------------------------------

KOKKOS_INLINE_FUNCTION
void MjBgkRelaxCell(int Nb, const Real m_vec[], const Real u_bar[][3], const Real Sigma[][3][3],
                    Real V_a, const AdmPoint &adm, Real sigma_over_mu, Real dt, int n_q,
                    Real u_out[][3], Real Sig_out[][3][3],
                    const Real *E_override = nullptr) {
  for (int al = 0; al < Nb; ++al) {
    for (int i = 0; i < 3; ++i) {
      u_out[al][i] = u_bar[al][i];
      for (int j = 0; j < 3; ++j) Sig_out[al][i][j] = Sigma[al][i][j];
    }
  }
  Real m_tot = 0.0;
  for (int al = 0; al < Nb; ++al) m_tot += m_vec[al];
  if (m_tot <= 0.0 || sigma_over_mu <= 0.0) return;

  Real gi[3][3];
  const Real detg = Inv3Sym(adm.g, gi);
  const Real sqrt_g = sqrt(detg);
  Real L_g[3][3], Li_g[3][3];
  Chol3(adm.g, L_g, Li_g);

  Real E_tot = 0.0;
  Real P_cov_tot[3] = {0.0, 0.0, 0.0};
  for (int al = 0; al < Nb; ++al) {
    if (m_vec[al] > 0.0) {
      Real Ea, Pa[3], Sa[3][3];
      BasisStressEnergy(m_vec[al], u_bar[al], Sigma[al], gi, n_q, Ea, Pa, Sa);
      E_tot += Ea;
      for (int i = 0; i < 3; ++i) P_cov_tot[i] += Pa[i];
    }
  }
  if (E_override != nullptr) E_tot = *E_override;

  Real P_tet[3] = {0.0, 0.0, 0.0};
  for (int m = 0; m < 3; ++m) {
    for (int i = 0; i < 3; ++i) P_tet[m] += Li_g[m][i] * P_cov_tot[i];
  }
  const Real P2 = Dot3(P_tet, P_tet);
  const Real M_inv2 = E_tot * E_tot - P2;
  if (M_inv2 <= m_tot * m_tot * (1.0 + 1.0e-14)) return;
  const Real M_inv = sqrt(M_inv2);
  const Real U0 = E_tot / M_inv;
  const Real U_cm[3] = {P_tet[0]/M_inv, P_tet[1]/M_inv, P_tet[2]/M_inv};

  const Real w_com = M_inv / m_tot;
  const Real theta = SafeMjThetaFromW(w_com);
  if (theta <= 0.0) return;
  Real wm_tmp, h_rel, cs2_tmp, ga_tmp;
  SyngeThermo(theta, wm_tmp, h_rel, cs2_tmp, ga_tmp);
  const Real vmol = MjVmol(theta);
  const Real rho_proper = m_tot / (V_a * sqrt_g * U0);
  const Real nu_a = rho_proper * sigma_over_mu * vmol;
  const Real dtau_a = adm.alp * dt / U0;
  const Real eta = 1.0 - exp(-nu_a * dtau_a);
  if (eta <= 0.0) return;

  const Real sig_eq2_0 = theta * h_rel;
  const Real u_zero[3] = {0.0, 0.0, 0.0};

  auto eval_eq_com_w = [&](Real scale_s) -> Real {
    const Real v = scale_s * sig_eq2_0;
    const Real S_eq_c[3][3] = {{v, 0.0, 0.0}, {0.0, v, 0.0}, {0.0, 0.0, v}};
    Real pts_c[27][3], w[27];
    int n_pts = 0;
    BasisCubaturePoints(u_zero, S_eq_c, n_q, pts_c, w, n_pts);
    Real Wt = 0.0;
    for (int q = 0; q < n_pts; ++q) {
      Wt += w[q] * sqrt(1.0 + Dot3(pts_c[q], pts_c[q]));
    }
    return Wt;
  };

  Real s_com = 1.0;
  const Real w_eq1 = eval_eq_com_w(1.0);
  if (fabs(w_eq1 - w_com) > 1.0e-14 * w_com) {
    Real lo_s = 0.0, hi_s = 2.5;
    while (eval_eq_com_w(hi_s) < w_com && hi_s < 1.0e6) hi_s *= 4.0;
    if (eval_eq_com_w(hi_s) >= w_com) {
      auto f_eq = [&](Real s) -> Real { return eval_eq_com_w(s) - w_com; };
      s_com = BrentRoot(f_eq, lo_s, hi_s, 1.0e-14, 1.0e-14, 80);
    } else {
      s_com = hi_s;
    }
  }

  const Real veq = s_com * sig_eq2_0;
  const Real S_eq_com[3][3] = {{veq, 0.0, 0.0}, {0.0, veq, 0.0}, {0.0, 0.0, veq}};
  Real pts_eq_c[27][3], pts_eq_cov[27][3], w_eq[27];
  int n_eq_pts = 0;
  BasisCubaturePoints(u_zero, S_eq_com, n_q, pts_eq_c, w_eq, n_eq_pts);

  Real u_eq[3] = {0.0, 0.0, 0.0};
  for (int q = 0; q < n_eq_pts; ++q) {
    const Real Wc = sqrt(1.0 + Dot3(pts_eq_c[q], pts_eq_c[q]));
    const Real fac = Dot3(pts_eq_c[q], U_cm) / (U0 + 1.0) + Wc;
    Real ptet[3];
    for (int m = 0; m < 3; ++m) ptet[m] = pts_eq_c[q][m] + fac * U_cm[m];
    for (int i = 0; i < 3; ++i) {
      Real pc = 0.0;
      for (int m = 0; m < 3; ++m) pc += L_g[i][m] * ptet[m];
      pts_eq_cov[q][i] = pc;
      u_eq[i] += w_eq[q] * pc;
    }
  }
  Real Sig_eq[3][3] = {{0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}};
  for (int q = 0; q < n_eq_pts; ++q) {
    for (int i = 0; i < 3; ++i) {
      for (int j = 0; j < 3; ++j) {
        Sig_eq[i][j] += w_eq[q] * (pts_eq_cov[q][i] - u_eq[i]) * (pts_eq_cov[q][j] - u_eq[j]);
      }
    }
  }
  for (int i = 0; i < 3; ++i) {
    for (int j = i + 1; j < 3; ++j) {
      const Real sym = 0.5 * (Sig_eq[i][j] + Sig_eq[j][i]);
      Sig_eq[i][j] = Sig_eq[j][i] = sym;
    }
  }

  for (int al = 0; al < Nb; ++al) {
    if (m_vec[al] <= 0.0) {
      for (int i = 0; i < 3; ++i) {
        u_out[al][i] = 0.0;
        for (int j = 0; j < 3; ++j) Sig_out[al][i][j] = 0.0;
      }
      continue;
    }
    Real du[3];
    for (int i = 0; i < 3; ++i) {
      u_out[al][i] = (1.0 - eta) * u_bar[al][i] + eta * u_eq[i];
      du[i] = u_bar[al][i] - u_eq[i];
    }
    for (int i = 0; i < 3; ++i) {
      for (int j = 0; j < 3; ++j) {
        Sig_out[al][i][j] = (1.0 - eta) * Sigma[al][i][j]
                          + eta * Sig_eq[i][j]
                          + eta * (1.0 - eta) * du[i] * du[j];
      }
    }
    for (int i = 0; i < 3; ++i) {
      for (int j = i + 1; j < 3; ++j) {
        const Real sym = 0.5 * (Sig_out[al][i][j] + Sig_out[al][j][i]);
        Sig_out[al][i][j] = Sig_out[al][j][i] = sym;
      }
    }
  }

  Real u_eq_mom[3] = {P_cov_tot[0] / m_tot, P_cov_tot[1] / m_tot, P_cov_tot[2] / m_tot};
  Real P_cur[3] = {0.0, 0.0, 0.0};
  for (int al = 0; al < Nb; ++al) {
    if (m_vec[al] > 0.0) {
      for (int i = 0; i < 3; ++i) P_cur[i] += m_vec[al] * u_out[al][i];
    }
  }
  for (int al = 0; al < Nb; ++al) {
    if (m_vec[al] > 0.0) {
      for (int i = 0; i < 3; ++i) u_out[al][i] -= (P_cur[i] - P_cov_tot[i]) / m_tot;
    }
  }

  auto eval_zero_energy = [&](const Real u_arr[][3]) -> Real {
    Real Ez = 0.0;
    for (int al = 0; al < Nb; ++al) {
      if (m_vec[al] <= 0.0) continue;
      Real u2 = 0.0;
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) u2 += u_arr[al][i] * gi[i][j] * u_arr[al][j];
      }
      Ez += m_vec[al] * sqrt(1.0 + u2);
    }
    return Ez;
  };

  auto lab_energy_cur = [&]() -> Real {
    Real Es = 0.0;
    for (int al = 0; al < Nb; ++al) {
      if (m_vec[al] <= 0.0) continue;
      Real ea, pa[3], sa[3][3];
      BasisStressEnergy(m_vec[al], u_out[al], Sig_out[al], gi, n_q, ea, pa, sa);
      Es += ea;
    }
    return Es;
  };

  const Real E_zero = eval_zero_energy(u_out);
  const Real E_cur  = lab_energy_cur();
  const Real E_target = E_tot;
  if (fabs(E_cur - E_target) > 1.0e-14 * E_target) {
    if (E_target < E_zero) {
      auto eval_blend = [&](Real lam) -> Real {
        Real Ez = 0.0;
        for (int al = 0; al < Nb; ++al) {
          if (m_vec[al] <= 0.0) continue;
          Real ut[3] = {
            (1.0 - lam) * u_out[al][0] + lam * u_eq_mom[0],
            (1.0 - lam) * u_out[al][1] + lam * u_eq_mom[1],
            (1.0 - lam) * u_out[al][2] + lam * u_eq_mom[2]
          };
          Real u2 = 0.0;
          for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) u2 += ut[i] * gi[i][j] * ut[j];
          }
          Ez += m_vec[al] * sqrt(1.0 + u2);
        }
        return Ez;
      };
      const Real E_blend1 = eval_blend(1.0);
      Real lam_opt = 1.0;
      if (E_blend1 <= E_target && E_target <= E_zero) {
        auto f_b = [&](Real l) -> Real { return eval_blend(l) - E_target; };
        lam_opt = BrentRoot(f_b, 0.0, 1.0, 1.0e-14, 1.0e-14, 80);
      }
      for (int al = 0; al < Nb; ++al) {
        if (m_vec[al] <= 0.0) continue;
        for (int i = 0; i < 3; ++i) {
          u_out[al][i] = (1.0 - lam_opt) * u_out[al][i] + lam_opt * u_eq_mom[i];
          for (int j = 0; j < 3; ++j) Sig_out[al][i][j] = 0.0;
        }
      }
    } else if (E_target < E_cur) {
      auto eval_shrink = [&](Real s) -> Real {
        Real Es = 0.0;
        for (int al = 0; al < Nb; ++al) {
          if (m_vec[al] <= 0.0) continue;
          Real S_sc[3][3];
          for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) S_sc[i][j] = s * Sig_out[al][i][j];
          Real ea, pa[3], sa[3][3];
          BasisStressEnergy(m_vec[al], u_out[al], S_sc, gi, n_q, ea, pa, sa);
          Es += ea;
        }
        return Es;
      };
      if (E_zero <= E_target && E_target <= E_cur) {
        auto f_s = [&](Real s) -> Real { return eval_shrink(s) - E_target; };
        const Real s_opt = BrentRoot(f_s, 0.0, 1.0, 1.0e-14, 1.0e-14, 80);
        for (int al = 0; al < Nb; ++al) {
          for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) Sig_out[al][i][j] *= s_opt;
        }
      } else {
        for (int al = 0; al < Nb; ++al) {
          for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) Sig_out[al][i][j] = 0.0;
        }
      }
    } else {
      const Real tr_eq = Sig_eq[0][0] + Sig_eq[1][1] + Sig_eq[2][2];
      Real S_add[3][3];
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
          S_add[i][j] = (tr_eq > 1.0e-30) ? Sig_eq[i][j] : adm.g[i][j];
        }
      }
      auto eval_add = [&](Real delta) -> Real {
        Real Es = 0.0;
        for (int al = 0; al < Nb; ++al) {
          if (m_vec[al] <= 0.0) continue;
          Real S_ad[3][3];
          for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) S_ad[i][j] = Sig_out[al][i][j] + delta * S_add[i][j];
          Real ea, pa[3], sa[3][3];
          BasisStressEnergy(m_vec[al], u_out[al], S_ad, gi, n_q, ea, pa, sa);
          Es += ea;
        }
        return Es;
      };
      Real lo_d = 0.0, hi_d = 1.0;
      while (eval_add(hi_d) < E_target && hi_d < 1.0e12) hi_d *= 4.0;
      if (eval_add(lo_d) <= E_target && E_target <= eval_add(hi_d)) {
        auto f_d = [&](Real d) -> Real { return eval_add(d) - E_target; };
        const Real d_opt = BrentRoot(f_d, lo_d, hi_d, 1.0e-14, 1.0e-14, 80);
        for (int al = 0; al < Nb; ++al) {
          if (m_vec[al] <= 0.0) continue;
          for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
              Sig_out[al][i][j] = 0.5 * ((Sig_out[al][i][j] + d_opt * S_add[i][j])
                                       + (Sig_out[al][j][i] + d_opt * S_add[j][i]));
            }
          }
        }
      }
    }
  }
}

KOKKOS_INLINE_FUNCTION
HllcFluidState BuildHllcCellFluid(int Nb, const Real D_vec[], const Real u_tet[][3], const Real Sig_tet[][3][3]) {
  HllcFluidState st;
  Real D_tot = 0.0;
  for (int al = 0; al < Nb; ++al) D_tot += D_vec[al];
  if (D_tot <= 0.0) return st;
  Real E = 0.0, P[3] = {0.0, 0.0, 0.0};
  const Real g_eye[3][3] = {{1,0,0},{0,1,0},{0,0,1}};
  for (int al = 0; al < Nb; ++al) {
    if (D_vec[al] > 0.0) {
      Real ea, pa[3], sa[3][3];
      BasisStressEnergy(D_vec[al], u_tet[al], Sig_tet[al], g_eye, 3, ea, pa, sa);
      E += ea;
      for (int i = 0; i < 3; ++i) P[i] += pa[i];
    }
  }
  st.D = D_tot; st.E = E;
  for (int i = 0; i < 3; ++i) st.P[i] = P[i];
  ValenciaC2PSynge(D_tot, E, P, st.theta, st.h, st.cs2, st.w_m, st.U0, st.rho0, st.p, st.v);
  st.valid = true;
  return st;
}

KOKKOS_INLINE_FUNCTION
void HllcCharSpeeds(const HllcFluidState &st, Real &lam_m, Real &lam_p) {
  const Real vx = st.v[0];
  const Real v2 = Dot3(st.v, st.v);
  const Real cs2 = st.cs2;
  const Real s2 = (1.0 - v2*cs2 > 1.0e-12) ? (1.0 - v2*cs2) : 1.0e-12;
  const Real arg = cs2 * (1.0 - v2) * (1.0 - v2*cs2 - vx*vx*(1.0 - cs2));
  const Real disc = (arg > 0.0) ? sqrt(arg) : 0.0;
  const Real num1 = vx * (1.0 - cs2);
  lam_m = (num1 - disc) / s2;
  lam_p = (num1 + disc) / s2;
}

KOKKOS_INLINE_FUNCTION
void HllcStarFPiAle(Real D_s, Real E_s, const Real P_s[3], Real beta_use,
                    Real FPi_out[3][3]) {
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) FPi_out[i][j] = 0.0;
  }
  if (D_s <= 1.0e-300 || E_s <= 1.0e-300) return;

  Real th_s, h_s, cs2_s, wm_s, U0_s, n_s, p_s, v_s[3];
  ValenciaC2PSynge(D_s, E_s, P_s, th_s, h_s, cs2_s, wm_s, U0_s, n_s, p_s, v_s);
  Real v_s2 = Dot3(v_s, v_s);
  if (v_s2 >= 1.0 - 1.0e-12) {
    const Real sc = sqrt((1.0 - 1.0e-12) / v_s2);
    for (int i = 0; i < 3; ++i) v_s[i] *= sc;
    v_s2 = 1.0 - 1.0e-12;
    U0_s = 1.0 / sqrt(1.0 - v_s2);
    n_s = D_s / U0_s;
  }
  const Real U_s[3] = {U0_s * v_s[0], U0_s * v_s[1], U0_s * v_s[2]};
  const Real b3 = n_s * th_s * h_s;
  const Real a3 = n_s * (1.0 + 6.0 * th_s * h_s);
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      const Real M0 = (a3 * U0_s) * U_s[i] * U_s[j] + ((i == j) ? (b3 * U0_s) : 0.0);
      const Real del_ij = (i == j) ? 1.0 : 0.0;
      const Real del_xi = (i == 0) ? 1.0 : 0.0;
      const Real del_xj = (j == 0) ? 1.0 : 0.0;
      const Real M1 = (a3 * U_s[0]) * U_s[i] * U_s[j]
                    + b3 * (U_s[0]*del_ij + U_s[i]*del_xj + del_xi*U_s[j]);
      FPi_out[i][j] = M1 - beta_use * M0;
    }
  }
}

KOKKOS_INLINE_FUNCTION
Real NohThermalConductFlux(const HllcFluidState &Lc, const HllcFluidState &Rc, Real kappa) {
  if (kappa <= 0.0 || !Lc.valid || !Rc.valid) return 0.0;
  const Real csL = sqrt((Lc.cs2 > 0.0) ? Lc.cs2 : 0.0);
  const Real csR = sqrt((Rc.cs2 > 0.0) ? Rc.cs2 : 0.0);
  const Real cs_harm = 2.0 * csL * csR / (csL + csR + 1.0e-30);
  if (cs_harm <= 0.0) return 0.0;
  const Real rho_bar = 0.5 * (Lc.rho0 + Rc.rho0) + 1.0e-30;
  const Real dv_comp = (Lc.v[0] > Rc.v[0]) ? (Lc.v[0] - Rc.v[0]) : 0.0;
  const Real v_price = sqrt(fabs(Lc.p - Rc.p) / rho_bar) + dv_comp;
  const Real v_sig = (cs_harm < v_price) ? cs_harm : v_price;
  return kappa * 0.5 * (Lc.D + Rc.D) * v_sig * (Lc.w_m - Rc.w_m);
}

KOKKOS_INLINE_FUNCTION
void RelHllcFluxTetrad(int Na, const Real D_L[], const Real u_L_tet[][3], const Real Sig_L_tet[][3][3],
                       int Nb, const Real D_R[], const Real u_R_tet[][3], const Real Sig_R_tet[][3][3],
                       Real beta_F, bool use_contact_beta_F,
                       Real &FD_ale, Real FP_ale[3], Real FPi_ale[3][3], Real &FE_ale) {
  FD_ale = 0.0; FE_ale = 0.0;
  for (int i = 0; i < 3; ++i) {
    FP_ale[i] = 0.0;
    for (int j = 0; j < 3; ++j) FPi_ale[i][j] = 0.0;
  }
  const HllcFluidState L = BuildHllcCellFluid(Na, D_L, u_L_tet, Sig_L_tet);
  const HllcFluidState R = BuildHllcCellFluid(Nb, D_R, u_R_tet, Sig_R_tet);
  if (!L.valid || !R.valid) return;

  Real lmL, lpL, lmR, lpR;
  HllcCharSpeeds(L, lmL, lpL);
  HllcCharSpeeds(R, lmR, lpR);
  const Real S_L = (lmL < lmR) ? lmL : lmR;
  const Real S_R = (lpL > lpR) ? lpL : lpR;
  const Real dS = S_R - S_L;

  const Real FD_L = L.D * L.v[0];
  const Real FP_L[3] = {L.P[0]*L.v[0] + L.p, L.P[1]*L.v[0], L.P[2]*L.v[0]};
  const Real FE_L = L.P[0];
  const Real FD_R = R.D * R.v[0];
  const Real FP_R[3] = {R.P[0]*R.v[0] + R.p, R.P[1]*R.v[0], R.P[2]*R.v[0]};
  const Real FE_R = R.P[0];

  Real beta_use = beta_F;
  if (use_contact_beta_F) {
    if (dS <= 1.0e-12 * (1.0 + fabs(S_L) + fabs(S_R))) {
      beta_use = 0.5 * (S_L + S_R);
    } else {
      const Real F_hll_E0  = (S_R*FE_L - S_L*FE_R + S_L*S_R*(R.E - L.E)) / dS;
      const Real F_hll_Px0 = (S_R*FP_L[0] - S_L*FP_R[0] + S_L*S_R*(R.P[0] - L.P[0])) / dS;
      const Real U_hll_E0  = (S_R*R.E - S_L*L.E + FE_L - FE_R) / dS;
      const Real U_hll_Px0 = (S_R*R.P[0] - S_L*L.P[0] + FP_L[0] - FP_R[0]) / dS;
      const Real aq0 = F_hll_E0;
      const Real bq0 = -(U_hll_E0 + F_hll_Px0);
      const Real cq0 = U_hll_Px0;
      Real s_st = 0.0;
      if (fabs(aq0) < 1.0e-14 * (fabs(bq0) + fabs(cq0) + 1.0e-30)) {
        s_st = (fabs(bq0) > 1.0e-14) ? (-cq0 / bq0) : 0.0;
      } else {
        const Real disc0 = (bq0*bq0 - 4.0*aq0*cq0 > 0.0) ? (bq0*bq0 - 4.0*aq0*cq0) : 0.0;
        s_st = (-bq0 - sqrt(disc0)) / (2.0 * aq0);
      }
      if (s_st < S_L) s_st = S_L;
      if (s_st > S_R) s_st = S_R;
      beta_use = s_st;
    }
  }

  Real D_s = 0.0, E_s = 0.0, P_s[3] = {0.0, 0.0, 0.0};
  Real FD_s = 0.0, FP_s[3] = {0.0, 0.0, 0.0}, FE_s = 0.0;
  if (dS <= 1.0e-12 * (1.0 + fabs(S_L) + fabs(S_R))) {
    if (use_contact_beta_F) {
      FD_ale = 0.5 * (FD_L + FD_R) - beta_use * 0.5 * (L.D + R.D);
      FE_ale = 0.5 * (FE_L + FE_R) - beta_use * 0.5 * (L.E + R.E);
      for (int i = 0; i < 3; ++i) {
        FP_ale[i] = 0.5 * (FP_L[i] + FP_R[i]) - beta_use * 0.5 * (L.P[i] + R.P[i]);
      }
      Real FPi_L[3][3], FPi_R[3][3];
      HllcStarFPiAle(L.D, L.E, L.P, beta_use, FPi_L);
      HllcStarFPiAle(R.D, R.E, R.P, beta_use, FPi_R);
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) FPi_ale[i][j] = 0.5 * (FPi_L[i][j] + FPi_R[i][j]);
      }
      return;
    }
    const Real S_mid = 0.5 * (S_L + S_R);
    if (beta_use <= S_mid) {
      D_s = L.D; E_s = L.E; FD_s = FD_L; FE_s = FE_L;
      for (int i = 0; i < 3; ++i) { P_s[i] = L.P[i]; FP_s[i] = FP_L[i]; }
    } else {
      D_s = R.D; E_s = R.E; FD_s = FD_R; FE_s = FE_R;
      for (int i = 0; i < 3; ++i) { P_s[i] = R.P[i]; FP_s[i] = FP_R[i]; }
    }
  } else if (beta_use <= S_L) {
    D_s = L.D; E_s = L.E; FD_s = FD_L; FE_s = FE_L;
    for (int i = 0; i < 3; ++i) { P_s[i] = L.P[i]; FP_s[i] = FP_L[i]; }
  } else if (beta_use >= S_R) {
    D_s = R.D; E_s = R.E; FD_s = FD_R; FE_s = FE_R;
    for (int i = 0; i < 3; ++i) { P_s[i] = R.P[i]; FP_s[i] = FP_R[i]; }
  } else {
    const Real F_hll_E  = (S_R*FE_L - S_L*FE_R + S_L*S_R*(R.E - L.E)) / dS;
    const Real F_hll_Px = (S_R*FP_L[0] - S_L*FP_R[0] + S_L*S_R*(R.P[0] - L.P[0])) / dS;
    const Real U_hll_E  = (S_R*R.E - S_L*L.E + FE_L - FE_R) / dS;
    const Real U_hll_Px = (S_R*R.P[0] - S_L*L.P[0] + FP_L[0] - FP_R[0]) / dS;
    const Real aq = F_hll_E;
    const Real bq = -(U_hll_E + F_hll_Px);
    const Real cq = U_hll_Px;
    Real S_star = 0.0;
    if (fabs(aq) < 1.0e-14 * (fabs(bq) + fabs(cq) + 1.0e-30)) {
      S_star = (fabs(bq) > 1.0e-14) ? (-cq / bq) : 0.0;
    } else {
      const Real disc = (bq*bq - 4.0*aq*cq > 0.0) ? (bq*bq - 4.0*aq*cq) : 0.0;
      S_star = (-bq - sqrt(disc)) / (2.0 * aq);
    }
    if (S_star < S_L) S_star = S_L;
    if (S_star > S_R) S_star = S_R;

    const Real p_s = (F_hll_Px - S_star * F_hll_E > 0.0) ? (F_hll_Px - S_star * F_hll_E) : 0.0;
    const Real dS_safe = (dS > 1.0) ? dS : 1.0;

    if (use_contact_beta_F) {
      const Real denom_L = S_L - S_star;
      const Real denom_R = S_R - S_star;
      FD_ale = 0.0;
      FP_ale[0] = p_s; FP_ale[1] = 0.0; FP_ale[2] = 0.0;
      FE_ale = p_s * S_star;
      if (fabs(denom_L) <= 1.0e-12 * dS_safe || fabs(denom_R) <= 1.0e-12 * dS_safe) {
        const Real D_h = (S_R*R.D - S_L*L.D + FD_L - FD_R) / dS;
        Real P_h[3];
        for (int i = 0; i < 3; ++i) {
          P_h[i] = (S_R*R.P[i] - S_L*L.P[i] + FP_L[i] - FP_R[i]) / dS;
        }
        HllcStarFPiAle(D_h, U_hll_E, P_h, S_star, FPi_ale);
      } else {
        const Real vxL = L.v[0], vxR = R.v[0];
        const Real D_Ls = L.D * (S_L - vxL) / denom_L;
        const Real E_Ls = (L.E * (S_L - vxL) - L.p * vxL + p_s * S_star) / denom_L;
        const Real P_Ls[3] = {
          (L.P[0] * (S_L - vxL) - L.p + p_s) / denom_L,
          L.P[1] * (S_L - vxL) / denom_L,
          L.P[2] * (S_L - vxL) / denom_L
        };
        const Real D_Rs = R.D * (S_R - vxR) / denom_R;
        const Real E_Rs = (R.E * (S_R - vxR) - R.p * vxR + p_s * S_star) / denom_R;
        const Real P_Rs[3] = {
          (R.P[0] * (S_R - vxR) - R.p + p_s) / denom_R,
          R.P[1] * (S_R - vxR) / denom_R,
          R.P[2] * (S_R - vxR) / denom_R
        };
        Real FPi_L[3][3], FPi_R[3][3];
        HllcStarFPiAle(D_Ls, E_Ls, P_Ls, S_star, FPi_L);
        HllcStarFPiAle(D_Rs, E_Rs, P_Rs, S_star, FPi_R);
        for (int i = 0; i < 3; ++i) {
          for (int j = 0; j < 3; ++j) FPi_ale[i][j] = 0.5 * (FPi_L[i][j] + FPi_R[i][j]);
        }
      }
      return;
    }

    const HllcFluidState &st = (beta_use <= S_star) ? L : R;
    const Real S_K = (beta_use <= S_star) ? S_L : S_R;
    const Real vxK = st.v[0];
    const Real denom = S_K - S_star;
    if (fabs(denom) <= 1.0e-12 * dS_safe) {
      D_s = (S_R*R.D - S_L*L.D + FD_L - FD_R) / dS;
      E_s = U_hll_E;
      FD_s = (S_R*FD_L - S_L*FD_R + S_L*S_R*(R.D - L.D)) / dS;
      FE_s = F_hll_E;
      for (int i = 0; i < 3; ++i) {
        P_s[i]  = (S_R*R.P[i] - S_L*L.P[i] + FP_L[i] - FP_R[i]) / dS;
        FP_s[i] = (S_R*FP_L[i] - S_L*FP_R[i] + S_L*S_R*(R.P[i] - L.P[i])) / dS;
      }
    } else {
      D_s = st.D * (S_K - vxK) / denom;
      E_s = (st.E * (S_K - vxK) - st.p * vxK + p_s * S_star) / denom;
      P_s[0] = (st.P[0] * (S_K - vxK) - st.p + p_s) / denom;
      P_s[1] = st.P[1] * (S_K - vxK) / denom;
      P_s[2] = st.P[2] * (S_K - vxK) / denom;
      FD_s = D_s * S_star;
      for (int i = 0; i < 3; ++i) FP_s[i] = P_s[i] * S_star;
      FP_s[0] += p_s;
      FE_s = (E_s + p_s) * S_star;
    }
  }

  FD_ale = FD_s - beta_use * D_s;
  FE_ale = FE_s - beta_use * E_s;
  for (int i = 0; i < 3; ++i) FP_ale[i] = FP_s[i] - beta_use * P_s[i];
  HllcStarFPiAle(D_s, E_s, P_s, beta_use, FPi_ale);
}

}  // namespace vlasov
}  // namespace nrpic

#endif  // PARTICLES_VLASOV_VLASOV_FLUX_KERNELS_HPP_
