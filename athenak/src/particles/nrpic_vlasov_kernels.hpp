#ifndef PARTICLES_NRPIC_VLASOV_KERNELS_HPP_
#define PARTICLES_NRPIC_VLASOV_KERNELS_HPP_
//========================================================================================
// General-Relativistic Lagrangian-Basis Vlasov (GR-LBV) standalone mathematical kernels.
// Works inside Kokkos GPU/CPU kernels (KOKKOS_INLINE_FUNCTION) and standalone C++17
// (-DNRPIC_STANDALONE). Zero heap allocation; exact twin of python/nrpic/vlasov_gr.py.
//========================================================================================

#include <cmath>
#include "nrpic_kernels.hpp"

namespace nrpic {
namespace vlasov {

constexpr int MAX_BASIS = 8;
constexpr int BASIS_TOPHAT = 0;
constexpr int BASIS_GAUSS  = 1;

constexpr Real kSqrt3 = 1.7320508075688772935;
constexpr Real kPi    = 3.14159265358979323846;
constexpr Real kEuler = 0.57721566490153286061;

//----------------------------------------------------------------------------------------
// Small matrix & Cholesky helpers (exact mirrors of python/nrpic/vlasov_gr.py)
//----------------------------------------------------------------------------------------

KOKKOS_INLINE_FUNCTION
Real Dot3(const Real a[3], const Real b[3]) {
  return a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
}

KOKKOS_INLINE_FUNCTION
Real MatVecDot3(const Real u[3], const Real g[3][3], const Real v[3]) {
  Real s = 0.0;
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      s += u[i] * g[i][j] * v[j];
    }
  }
  return s;
}

KOKKOS_INLINE_FUNCTION
void Chol3Safe(const Real S[3][3], Real L[3][3], Real tol = 1.0e-28) {
  Real A[3][3];
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      A[i][j] = 0.5 * (S[i][j] + S[j][i]);
      L[i][j] = 0.0;
    }
  }
  const Real d0 = (A[0][0] > 0.0) ? A[0][0] : 0.0;
  if (d0 > tol) {
    L[0][0] = sqrt(d0);
    L[1][0] = A[1][0] / L[0][0];
    L[2][0] = A[2][0] / L[0][0];
  }
  const Real d1_raw = A[1][1] - L[1][0]*L[1][0];
  const Real d1 = (d1_raw > 0.0) ? d1_raw : 0.0;
  if (d1 > tol) {
    L[1][1] = sqrt(d1);
    L[2][1] = (A[2][1] - L[2][0]*L[1][0]) / L[1][1];
  }
  const Real d2_raw = A[2][2] - L[2][0]*L[2][0] - L[2][1]*L[2][1];
  const Real d2 = (d2_raw > 0.0) ? d2_raw : 0.0;
  if (d2 > tol) {
    L[2][2] = sqrt(d2);
  }
}

KOKKOS_INLINE_FUNCTION
void Chol2Safe(const Real S2[2][2], Real L[2][2], Real Li[2][2], Real tol = 1.0e-28) {
  Real A00 = S2[0][0];
  Real A01 = 0.5 * (S2[0][1] + S2[1][0]);
  Real A11 = S2[1][1];
  L[0][0] = L[0][1] = L[1][0] = L[1][1] = 0.0;
  Li[0][0] = Li[0][1] = Li[1][0] = Li[1][1] = 0.0;
  const Real d0 = (A00 > 0.0) ? A00 : 0.0;
  if (d0 > tol) {
    L[0][0] = sqrt(d0);
    Li[0][0] = 1.0 / L[0][0];
    L[1][0] = A01 / L[0][0];
  }
  const Real d1_raw = A11 - L[1][0]*L[1][0];
  const Real d1 = (d1_raw > 0.0) ? d1_raw : 0.0;
  if (d1 > tol) {
    L[1][1] = sqrt(d1);
    Li[1][1] = 1.0 / L[1][1];
    if (L[0][0] > 0.0) {
      Li[1][0] = -L[1][0] * Li[0][0] * Li[1][1];
    }
  }
}

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

struct FaceSidePrecomp {
  static constexpr int kMaxSlices = MAX_BASIS * 9;
  int n = 0;
  Real w[kMaxSlices];
  Real mu[kMaxSlices];
  Real sp[kMaxSlices];
  Real mp[kMaxSlices];
  Real w_tot = 0.0;
};

KOKKOS_INLINE_FUNCTION
void PrecomputeFaceSide(int Nb, const Real D[], const Real u_tet[][3], const Real Sig_tet[][3][3],
                        bool reverse_normal, int basis_kind, int n_perp, FaceSidePrecomp &out) {
  out.n = 0;
  out.w_tot = 0.0;
  const Real gl2_xi[2] = {-9.99999999999999889e-01, 9.99999999999999889e-01};
  const Real gl2_w[2]  = {5.0e-01, 5.0e-01};
  const Real gl3_xi[3] = {-1.34164078649987384e+00, 0.0, 1.34164078649987384e+00};
  const Real gl3_w[3]  = {2.77777777777777846e-01, 4.44444444444444420e-01, 2.77777777777777846e-01};
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
      for (int i = 0; i < n1d; ++i) {
        const Real e0 = (n1d == 3) ? gl3_xi[i] : gl2_xi[i];
        const Real wi = (n1d == 3) ? gl3_w[i]  : gl2_w[i];
        for (int j = 0; j < n1d; ++j) {
          const Real e1 = (n1d == 3) ? gl3_xi[j] : gl2_xi[j];
          const Real wj = (n1d == 3) ? gl3_w[j]  : gl2_w[j];
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

KOKKOS_INLINE_FUNCTION
Real EvalSideI0(const FaceSidePrecomp &s, Real beta_F) {
  Real sum = 0.0;
  for (int q = 0; q < s.n; ++q) {
    sum += s.w[q] * SliceTopHatI0(s.mu[q], s.sp[q], s.mp[q], beta_F);
  }
  return sum;
}

KOKKOS_INLINE_FUNCTION
Real SolveFaceBetaF(int Na, const Real D_a[], const Real u_a_tet[][3], const Real Sig_a_tet[][3][3],
                    int Nb, const Real D_b[], const Real u_b_tet[][3], const Real Sig_b_tet[][3][3],
                    int basis_kind = BASIS_TOPHAT, int n_perp = 3) {
  FaceSidePrecomp sa, sb;
  PrecomputeFaceSide(Na, D_a, u_a_tet, Sig_a_tet, false, basis_kind, n_perp, sa);
  PrecomputeFaceSide(Nb, D_b, u_b_tet, Sig_b_tet, true,  basis_kind, n_perp, sb);
  const Real scale_flux = (sa.w_tot > sb.w_tot) ? sa.w_tot : sb.w_tot;
  if (scale_flux <= 0.0) return 0.0;

  auto net_flux = [&](Real bF) -> Real {
    return EvalSideI0(sa, bF) - EvalSideI0(sb, -bF);
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
  if (b0 > 0.99) b0 = 0.99;
  if (b0 < -0.99) b0 = -0.99;

  if (fabs(net_flux(b0)) <= 1.0e-14 * scale_flux) return b0;

  const Real lo_max = -0.999999999;
  const Real hi_max =  0.999999999;
  const Real dvs[2] = {0.04, 0.25};
  for (int k = 0; k < 2; ++k) {
    const Real lo_t = (lo_max > b0 - dvs[k]) ? lo_max : (b0 - dvs[k]);
    const Real hi_t = (hi_max < b0 + dvs[k]) ? hi_max : (b0 + dvs[k]);
    const Real fl = net_flux(lo_t);
    const Real fh = net_flux(hi_t);
    if (fabs(fl) <= 1.0e-14 * scale_flux) return lo_t;
    if (fabs(fh) <= 1.0e-14 * scale_flux) return hi_t;
    if (fl > 0.0 && fh < 0.0) {
      return BrentRoot(net_flux, lo_t, hi_t, 1.0e-12, 1.0e-12, 120);
    }
  }
  const Real flo = net_flux(lo_max);
  const Real fhi = net_flux(hi_max);
  if (flo <= 0.0) return lo_max;
  if (fhi >= 0.0) return hi_max;
  return BrentRoot(net_flux, lo_max, hi_max, 1.0e-12, 1.0e-12, 120);
}

//----------------------------------------------------------------------------------------
// Covariant face-rest-frame pairing cost C^eb (Hopkins 2026 Eqs. 26-30)
//----------------------------------------------------------------------------------------

KOKKOS_INLINE_FUNCTION
void PairingCostMatrix(int Na, const Real Da[], const Real ua_tet[][3], const Real Siga_tet[][3][3],
                       int Nb, const Real Db[], const Real ub_tet[][3], const Real Sib_tet[][3][3],
                       Real beta_F, Real C_eb[MAX_BASIS][MAX_BASIS],
                       Real lam_D = 0.25, Real eps_tau = 0.04, Real eps_eb = 0.01) {
  const bool use_boost = (fabs(beta_F) < 1.0 - 1.0e-12);
  const Real gam_F = use_boost ? (1.0 / sqrt(1.0 - beta_F*beta_F)) : 1.0;

  Real ua_b[MAX_BASIS][3], ub_b[MAX_BASIS][3];
  Real tra[MAX_BASIS], trb[MAX_BASIS];
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
    Real C_row[MAX_BASIS];
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

//----------------------------------------------------------------------------------------
// 27-point (or 8-point) cubature stress-energy and fixed-x geodesic kick
//----------------------------------------------------------------------------------------

KOKKOS_INLINE_FUNCTION
void BasisCubaturePoints(const Real u_bar[3], const Real Sigma[3][3], int n_q,
                         Real pts[27][3], Real w[27], int &n_pts) {
  const Real tr = Sigma[0][0] + Sigma[1][1] + Sigma[2][2];
  if (tr <= 1.0e-26) {
    n_pts = 1;
    pts[0][0] = u_bar[0];
    pts[0][1] = u_bar[1];
    pts[0][2] = u_bar[2];
    w[0] = 1.0;
    return;
  }
  Real L[3][3];
  Chol3Safe(Sigma, L);
  const Real gl2_xi[2] = {-9.99999999999999889e-01, 9.99999999999999889e-01};
  const Real gl2_w[2]  = {5.0e-01, 5.0e-01};
  const Real gl3_xi[3] = {-1.34164078649987384e+00, 0.0, 1.34164078649987384e+00};
  const Real gl3_w[3]  = {2.77777777777777846e-01, 4.44444444444444420e-01, 2.77777777777777846e-01};

  const int n1d = (n_q == 3) ? 3 : 2;
  n_pts = n1d * n1d * n1d;
  int q = 0;
  for (int i = 0; i < n1d; ++i) {
    const Real x0 = (n1d == 3) ? gl3_xi[i] : gl2_xi[i];
    const Real w0 = (n1d == 3) ? gl3_w[i]  : gl2_w[i];
    for (int j = 0; j < n1d; ++j) {
      const Real x1 = (n1d == 3) ? gl3_xi[j] : gl2_xi[j];
      const Real w1 = (n1d == 3) ? gl3_w[j]  : gl2_w[j];
      for (int k = 0; k < n1d; ++k) {
        const Real x2 = (n1d == 3) ? gl3_xi[k] : gl2_xi[k];
        const Real w2 = (n1d == 3) ? gl3_w[k]  : gl2_w[k];
        pts[q][0] = u_bar[0] + L[0][0]*x0 + L[0][1]*x1 + L[0][2]*x2;
        pts[q][1] = u_bar[1] + L[1][0]*x0 + L[1][1]*x1 + L[1][2]*x2;
        pts[q][2] = u_bar[2] + L[2][0]*x0 + L[2][1]*x1 + L[2][2]*x2;
        w[q] = w0 * w1 * w2;
        ++q;
      }
    }
  }
}

KOKKOS_INLINE_FUNCTION
void BasisStressEnergy(Real m_alpha, const Real u_bar[3], const Real Sigma[3][3],
                       const Real gi[3][3], int n_q,
                       Real &E_int, Real P_int[3], Real S_int[3][3]) {
  E_int = 0.0;
  for (int i = 0; i < 3; ++i) {
    P_int[i] = 0.0;
    for (int j = 0; j < 3; ++j) S_int[i][j] = 0.0;
  }
  if (m_alpha <= 0.0) return;
  Real pts[27][3], w[27];
  int n_pts = 0;
  BasisCubaturePoints(u_bar, Sigma, n_q, pts, w, n_pts);
  for (int q = 0; q < n_pts; ++q) {
    const Real W = sqrt(1.0 + MatVecDot3(pts[q], gi, pts[q]));
    const Real wm = m_alpha * w[q];
    E_int += wm * W;
    const Real wmW = wm / W;
    for (int i = 0; i < 3; ++i) {
      P_int[i] += wm * pts[q][i];
      for (int j = 0; j < 3; ++j) {
        S_int[i][j] += wmW * pts[q][i] * pts[q][j];
      }
    }
  }
}

KOKKOS_INLINE_FUNCTION
void GeodesicKickPoint(const AdmPoint &adm0, const AdmPoint *adm1, Real dt,
                       const Real u_in[3], Real u_out[3],
                       Real tol = 1.0e-12, int maxit = 50) {
  AdmPoint adm = adm0;
  if (adm1 != nullptr) AverageAdm(adm, *adm1);
  Real gi[3][3];
  Inv3Sym(adm.g, gi);
  Real u1[3] = {u_in[0], u_in[1], u_in[2]};
  for (int it = 0; it < maxit; ++it) {
    const Real ub[3] = {0.5*(u_in[0]+u1[0]), 0.5*(u_in[1]+u1[1]), 0.5*(u_in[2]+u1[2])};
    Real uup[3] = {0.0, 0.0, 0.0};
    for (int l = 0; l < 3; ++l) {
      for (int m = 0; m < 3; ++m) uup[l] += gi[l][m] * ub[m];
    }
    const Real W = sqrt(1.0 + Dot3(ub, uup));
    Real err = 0.0;
    for (int i = 0; i < 3; ++i) {
      Real geo = 0.0;
      for (int l = 0; l < 3; ++l) {
        for (int m = 0; m < 3; ++m) {
          geo += adm.dg[i][l][m] * uup[l] * uup[m];
        }
      }
      Real db = 0.0;
      for (int j = 0; j < 3; ++j) db += adm.dbeta[i][j] * ub[j];
      const Real rhs = -W * adm.dalp[i] + db + (0.5 * adm.alp / W) * geo;
      const Real un = u_in[i] + dt * rhs;
      const Real d = fabs(un - u1[i]);
      if (d > err) err = d;
      u1[i] = un;
    }
    if (err < tol) break;
  }
  u_out[0] = u1[0];
  u_out[1] = u1[1];
  u_out[2] = u1[2];
}

KOKKOS_INLINE_FUNCTION
void CubatureGeodesicKick(const Real u_bar[3], const Real Sigma[3][3],
                          const AdmPoint &adm0, const AdmPoint *adm1, Real dt,
                          int n_q, Real u_new[3], Real Sig_new[3][3], Real tol = 1.0e-12) {
  Real pts[27][3], pts_new[27][3], w[27];
  int n_pts = 0;
  BasisCubaturePoints(u_bar, Sigma, n_q, pts, w, n_pts);
  u_new[0] = u_new[1] = u_new[2] = 0.0;
  for (int q = 0; q < n_pts; ++q) {
    GeodesicKickPoint(adm0, adm1, dt, pts[q], pts_new[q], tol);
    for (int i = 0; i < 3; ++i) u_new[i] += w[q] * pts_new[q][i];
  }
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) Sig_new[i][j] = 0.0;
  }
  for (int q = 0; q < n_pts; ++q) {
    const Real du[3] = {pts_new[q][0] - u_new[0], pts_new[q][1] - u_new[1], pts_new[q][2] - u_new[2]};
    for (int i = 0; i < 3; ++i) {
      for (int j = 0; j < 3; ++j) Sig_new[i][j] += w[q] * du[i] * du[j];
    }
  }
  for (int i = 0; i < 3; ++i) {
    for (int j = i + 1; j < 3; ++j) {
      const Real sym = 0.5 * (Sig_new[i][j] + Sig_new[j][i]);
      Sig_new[i][j] = Sig_new[j][i] = sym;
    }
  }
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
// CUDA-device-safe Bessel K_n(z)*exp(z), Synge EOS, Moller rate, BGK, and HLLC
//----------------------------------------------------------------------------------------

KOKKOS_INLINE_FUNCTION
void Kve2And3Series(Real z, Real &k2e, Real &k3e) {
  const Real y = 0.25 * z * z;
  const Real ln_half = log(0.5 * z);
  Real psi_k = -kEuler;
  Real psi_k1 = -kEuler + 1.0;
  Real ti0 = 1.0, ti1 = 1.0;
  Real s_i0 = 1.0, s_k0 = psi_k;
  Real s_i1 = 1.0, s_k1 = 0.5 * (psi_k + psi_k1);
  for (int k = 1; k < 20; ++k) {
    ti0 *= y / Real(k * k);
    ti1 *= y / Real(k * (k + 1));
    psi_k += 1.0 / Real(k);
    psi_k1 += 1.0 / Real(k + 1);
    s_i0 += ti0;
    s_k0 += ti0 * psi_k;
    s_i1 += ti1;
    s_k1 += ti1 * 0.5 * (psi_k + psi_k1);
  }
  const Real I0 = s_i0;
  const Real I1 = 0.5 * z * s_i1;
  const Real K0 = -ln_half * I0 + s_k0;
  const Real K1 = ln_half * I1 + 1.0 / z - 0.5 * z * s_k1;
  const Real K2 = K0 + (2.0 / z) * K1;
  const Real K3 = K1 + (4.0 / z) * K2;
  const Real ez = exp(z);
  k2e = ez * K2;
  k3e = ez * K3;
}

KOKKOS_INLINE_FUNCTION
Real Kve2(Real z) {
  if (z < 1.0e-8) {
    return 2.0 * exp(z) / (z * z);
  }
  if (z < 2.0) {
    Real k2e, k3e;
    Kve2And3Series(z, k2e, k3e);
    return k2e;
  }
  if (z > 1.0e8) {
    return sqrt(kPi / (2.0 * z)) * (1.0 + 15.0 / (8.0 * z));
  }
  const Real c[22] = {
     1.5369562709347966e+00,  5.5848397424280200e-01,  2.0881208230680700e-02, -5.9855899178500930e-04,
     4.2825914991535946e-05, -4.4334910407642620e-06,  5.7252787593659550e-07, -8.6199405643664050e-08,
     1.4567477123573657e-08, -2.6978141135200220e-09,  5.3859570339007880e-10, -1.1455063160652075e-10,
     2.5724624450808940e-11, -6.0566602238571420e-12,  1.4864170500510971e-12, -3.7927237108512850e-13,
     1.0048023019687043e-13, -2.7886783791266433e-14,  6.8531039429134660e-15, -1.2818029466126807e-15,
     1.1354553660939100e-16, -1.7397699442705580e-15
  };
  const Real u = 4.0 / z - 1.0;
  Real b1 = 0.0, b2 = 0.0;
  for (int j = 21; j >= 1; --j) {
    const Real b0 = 2.0 * u * b1 - b2 + c[j];
    b2 = b1;
    b1 = b0;
  }
  return (u * b1 - b2 + c[0]) * sqrt(kPi / (2.0 * z));
}

KOKKOS_INLINE_FUNCTION
Real Kve3(Real z) {
  if (z < 1.0e-8) {
    return 8.0 * exp(z) / (z * z * z);
  }
  if (z < 2.0) {
    Real k2e, k3e;
    Kve2And3Series(z, k2e, k3e);
    return k3e;
  }
  if (z > 1.0e8) {
    return sqrt(kPi / (2.0 * z)) * (1.0 + 35.0 / (8.0 * z));
  }
  const Real c[22] = {
     2.9015710746079240e+00,  2.1887999942085252e+00,  2.9754370790629410e-01,  1.0019217529269042e-02,
    -2.7411895112389677e-04,  1.9185827578911812e-05, -1.9667333771163213e-06,  2.5315549516276420e-07,
    -3.8135857239783960e-08,  6.4630000543272360e-09, -1.2019289301208728e-09,  2.4116070756525170e-10,
    -5.1573856296727170e-11,  1.1650771256845681e-11, -2.7610035470037144e-12,  6.8190907466135860e-13,
    -1.7445640891496210e-13,  4.5448493453518910e-14, -1.4337016422545770e-14,  4.5569608692568930e-15,
    -2.0185873175002848e-15, -8.2762080017511670e-16
  };
  const Real u = 4.0 / z - 1.0;
  Real b1 = 0.0, b2 = 0.0;
  for (int j = 21; j >= 1; --j) {
    const Real b0 = 2.0 * u * b1 - b2 + c[j];
    b2 = b1;
    b1 = b0;
  }
  return (u * b1 - b2 + c[0]) * sqrt(kPi / (2.0 * z));
}

KOKKOS_INLINE_FUNCTION
void SyngeThermo(Real theta, Real &w_mean, Real &h_rel, Real &cs2, Real &gamma_ad) {
  if (theta <= 0.0) {
    w_mean = 1.0; h_rel = 1.0; cs2 = 0.0; gamma_ad = 5.0 / 3.0;
    return;
  }
  Real dh_dth = 0.0;
  if (theta <= 0.01) {
    const Real asym[10] = {
      1.0, 2.5, 1.875, -1.875, 1.0546875,
      1.40625, -7.2509765625, 21.09375, -58.152008056640625, 177.978515625
    };
    h_rel = 0.0;
    for (int k = 9; k >= 0; --k) h_rel = h_rel * theta + asym[k];
    dh_dth = 0.0;
    for (int k = 9; k >= 1; --k) dh_dth = dh_dth * theta + Real(k) * asym[k];
    w_mean = h_rel - theta;
  } else {
    const Real z = 1.0 / theta;
    const Real k2 = Kve2(z);
    const Real k3 = Kve3(z);
    h_rel = k3 / k2;
    w_mean = h_rel - theta;
    dh_dth = z * z * (1.0 + 5.0 * theta * h_rel - h_rel * h_rel);
  }
  const Real cv = (dh_dth - 1.0 > 1.5) ? (dh_dth - 1.0) : 1.5;
  gamma_ad = 1.0 + 1.0 / cv;
  cs2 = gamma_ad * theta / h_rel;
  if (cs2 < 0.0) cs2 = 0.0;
  if (cs2 > 1.0 / 3.0) cs2 = 1.0 / 3.0;
}

KOKKOS_INLINE_FUNCTION
Real SafeMjThetaFromW(Real w) {
  if (w <= 1.0 + 1.0e-15) return 0.0;
  if (w <= 1.0 + 1.0e-5) {
    const Real dw = w - 1.0;
    return (-1.5 + sqrt(2.25 + 7.5 * dw)) / 3.75;
  }
  if (w >= 1.0e5) return w / 3.0;
  auto f = [&](Real th) -> Real {
    Real wm, hr, cs2, ga;
    SyngeThermo(th, wm, hr, cs2, ga);
    return wm - w;
  };
  Real guess = (w < 2.0) ? ((w - 1.0) / 1.5) : ((w - 1.0) / 3.0);
  Real lo = guess * 0.25;
  Real hi = guess * 4.0;
  if (lo < 1.0e-8) lo = 1.0e-8;
  if (hi > 1.0e6) hi = 1.0e6;
  while (f(lo) > 0.0 && lo > 1.0e-12) lo *= 0.25;
  while (f(hi) < 0.0 && hi < 1.0e6) hi *= 4.0;
  return BrentRoot(f, lo, hi, 1.0e-14, 1.0e-13, 100);
}

KOKKOS_INLINE_FUNCTION
Real MjVmol(Real theta) {
  if (theta <= 0.0) return 0.0;
  if (theta < 1.0e-6) return sqrt(16.0 * theta / kPi);
  const Real z = 1.0 / theta;
  const Real k2 = Kve2(z);
  return 4.0 * Kve3(2.0 * z) / (z * k2 * k2);
}

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

  Real u_com_mean[MAX_BASIS][3], Sig_com[MAX_BASIS][3][3];
  for (int al = 0; al < Nb; ++al) {
    for (int i = 0; i < 3; ++i) {
      u_com_mean[al][i] = 0.0;
      for (int j = 0; j < 3; ++j) Sig_com[al][i][j] = 0.0;
    }
    if (m_vec[al] <= 0.0) continue;
    Real pts[27][3], pts_com[27][3], w[27];
    int n_pts = 0;
    BasisCubaturePoints(u_bar[al], Sigma[al], n_q, pts, w, n_pts);
    for (int q = 0; q < n_pts; ++q) {
      Real ptet[3] = {0.0, 0.0, 0.0};
      for (int m = 0; m < 3; ++m) {
        for (int i = 0; i < 3; ++i) ptet[m] += Li_g[m][i] * pts[q][i];
      }
      const Real W = sqrt(1.0 + Dot3(ptet, ptet));
      const Real fac = Dot3(ptet, U_cm) / (U0 + 1.0) - W;
      for (int m = 0; m < 3; ++m) {
        pts_com[q][m] = ptet[m] + fac * U_cm[m];
        u_com_mean[al][m] += w[q] * pts_com[q][m];
      }
    }
    for (int q = 0; q < n_pts; ++q) {
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
          Sig_com[al][i][j] += w[q] * (pts_com[q][i] - u_com_mean[al][i]) * (pts_com[q][j] - u_com_mean[al][j]);
        }
      }
    }
  }

  const Real sig_eq2_0 = theta * h_rel;
  Real u_com_new[MAX_BASIS][3], Sig_com_new[MAX_BASIS][3][3];
  for (int al = 0; al < Nb; ++al) {
    for (int i = 0; i < 3; ++i) u_com_new[al][i] = (1.0 - eta) * u_com_mean[al][i];
  }

  auto eval_com_energy = [&](Real scale_s, Real S_list[MAX_BASIS][3][3]) -> Real {
    Real Et = 0.0;
    for (int al = 0; al < Nb; ++al) {
      if (m_vec[al] <= 0.0) {
        for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) S_list[al][i][j] = 0.0;
        continue;
      }
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
          const Real s_ij = (1.0 - eta) * 0.5 * (Sig_com[al][i][j] + Sig_com[al][j][i])
                          + eta * (1.0 - eta) * u_com_mean[al][i] * u_com_mean[al][j]
                          + ((i == j) ? (eta * scale_s * sig_eq2_0) : 0.0);
          S_list[al][i][j] = s_ij;
        }
      }
      Real pts_c[27][3], w[27];
      int n_pts = 0;
      BasisCubaturePoints(u_com_new[al], S_list[al], n_q, pts_c, w, n_pts);
      for (int q = 0; q < n_pts; ++q) {
        const Real Wc = sqrt(1.0 + Dot3(pts_c[q], pts_c[q]));
        Et += m_vec[al] * w[q] * Wc;
      }
    }
    return Et;
  };

  Real S_zero[MAX_BASIS][3][3];
  const Real E_min_com = eval_com_energy(0.0, S_zero);
  if (M_inv <= E_min_com) {
    if (E_min_com > m_tot * (1.0 + 1.0e-14)) {
      auto eval_sc = [&](Real c, Real u_sc[MAX_BASIS][3], Real S_sc[MAX_BASIS][3][3]) -> Real {
        Real Etc = 0.0;
        const Real c2 = c * c;
        for (int al = 0; al < Nb; ++al) {
          if (m_vec[al] <= 0.0) {
            for (int i = 0; i < 3; ++i) {
              u_sc[al][i] = 0.0;
              for (int j = 0; j < 3; ++j) S_sc[al][i][j] = 0.0;
            }
            continue;
          }
          for (int i = 0; i < 3; ++i) {
            u_sc[al][i] = c * u_com_new[al][i];
            for (int j = 0; j < 3; ++j) S_sc[al][i][j] = c2 * S_zero[al][i][j];
          }
          Real pts_c[27][3], w[27];
          int n_pts = 0;
          BasisCubaturePoints(u_sc[al], S_sc[al], n_q, pts_c, w, n_pts);
          for (int q = 0; q < n_pts; ++q) {
            Etc += m_vec[al] * w[q] * sqrt(1.0 + Dot3(pts_c[q], pts_c[q]));
          }
        }
        return Etc;
      };
      auto f_sc = [&](Real c) -> Real {
        Real ut[MAX_BASIS][3], st[MAX_BASIS][3][3];
        return eval_sc(c, ut, st) - M_inv;
      };
      const Real c_opt = BrentRoot(f_sc, 0.0, 1.0, 1.0e-14, 1.0e-14, 80);
      Real ut[MAX_BASIS][3];
      eval_sc(c_opt, ut, Sig_com_new);
      for (int al = 0; al < Nb; ++al) {
        for (int i = 0; i < 3; ++i) u_com_new[al][i] = ut[al][i];
      }
    } else {
      for (int al = 0; al < Nb; ++al) {
        for (int i = 0; i < 3; ++i) {
          u_com_new[al][i] = 0.0;
          for (int j = 0; j < 3; ++j) Sig_com_new[al][i][j] = 0.0;
        }
      }
    }
  } else {
    Real S_tmp[MAX_BASIS][3][3];
    const Real Et1 = eval_com_energy(1.0, S_tmp);
    Real scale_opt = 1.0;
    if (fabs(Et1 - M_inv) > 1.0e-14 * M_inv) {
      Real lo_s = 0.0, hi_s = 2.5;
      while (eval_com_energy(hi_s, S_tmp) < M_inv && hi_s < 1.0e6) hi_s *= 4.0;
      if (eval_com_energy(hi_s, S_tmp) >= M_inv) {
        auto f_s = [&](Real s) -> Real {
          Real st[MAX_BASIS][3][3];
          return eval_com_energy(s, st) - M_inv;
        };
        scale_opt = BrentRoot(f_s, lo_s, hi_s, 1.0e-14, 1.0e-14, 80);
      } else {
        scale_opt = hi_s;
      }
    }
    eval_com_energy(scale_opt, Sig_com_new);
  }

  // Boost back to coordinate frame (pts_cov = pts_tet * L_g)
  for (int al = 0; al < Nb; ++al) {
    if (m_vec[al] <= 0.0) {
      for (int i = 0; i < 3; ++i) {
        u_out[al][i] = 0.0;
        for (int j = 0; j < 3; ++j) Sig_out[al][i][j] = 0.0;
      }
      continue;
    }
    Real pts_c[27][3], pts_cov[27][3], w[27];
    int n_pts = 0;
    BasisCubaturePoints(u_com_new[al], Sig_com_new[al], n_q, pts_c, w, n_pts);
    u_out[al][0] = u_out[al][1] = u_out[al][2] = 0.0;
    for (int q = 0; q < n_pts; ++q) {
      const Real Wc = sqrt(1.0 + Dot3(pts_c[q], pts_c[q]));
      const Real fac = Dot3(pts_c[q], U_cm) / (U0 + 1.0) + Wc;
      Real ptet[3];
      for (int m = 0; m < 3; ++m) ptet[m] = pts_c[q][m] + fac * U_cm[m];
      for (int i = 0; i < 3; ++i) {
        Real pc = 0.0;
        for (int m = 0; m < 3; ++m) pc += ptet[m] * L_g[m][i];
        pts_cov[q][i] = pc;
        u_out[al][i] += w[q] * pc;
      }
    }
    for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) Sig_out[al][i][j] = 0.0;
    for (int q = 0; q < n_pts; ++q) {
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
          Sig_out[al][i][j] += w[q] * (pts_cov[q][i] - u_out[al][i]) * (pts_cov[q][j] - u_out[al][j]);
        }
      }
    }
    for (int i = 0; i < 3; ++i) {
      for (int j = i + 1; j < 3; ++j) {
        const Real sym = 0.5 * (Sig_out[al][i][j] + Sig_out[al][j][i]);
        Sig_out[al][i][j] = Sig_out[al][j][i] = sym;
      }
    }
  }

  // Exact lab-frame P and E locking
  Real P_cur[3] = {0.0, 0.0, 0.0};
  for (int al = 0; al < Nb; ++al) {
    for (int i = 0; i < 3; ++i) P_cur[i] += m_vec[al] * u_out[al][i];
  }
  for (int al = 0; al < Nb; ++al) {
    for (int i = 0; i < 3; ++i) u_out[al][i] -= (P_cur[i] - P_cov_tot[i]) / m_tot;
  }

  auto lab_energy = [&](Real scale_lab) -> Real {
    Real Es = 0.0;
    for (int al = 0; al < Nb; ++al) {
      if (m_vec[al] <= 0.0) continue;
      Real S_sc[3][3];
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) S_sc[i][j] = scale_lab * Sig_out[al][i][j];
      Real ea, pa[3], sa[3][3];
      BasisStressEnergy(m_vec[al], u_out[al], S_sc, gi, n_q, ea, pa, sa);
      Es += ea;
    }
    return Es;
  };

  const Real E_min_lab = lab_energy(0.0);
  const Real E_target = (E_tot > E_min_lab) ? E_tot : E_min_lab;
  const Real E_cur = lab_energy(1.0);
  if (fabs(E_cur - E_target) > 1.0e-14 * E_target) {
    Real lo_l = 0.25, hi_l = 2.0;
    while (lab_energy(lo_l) > E_target && lo_l > 1.0e-12) lo_l *= 0.25;
    while (lab_energy(hi_l) < E_target && hi_l < 1.0e6)  hi_l *= 4.0;
    if (lab_energy(lo_l) <= E_target && E_target <= lab_energy(hi_l)) {
      auto f_l = [&](Real s) -> Real { return lab_energy(s) - E_target; };
      const Real s_lab = BrentRoot(f_l, lo_l, hi_l, 1.0e-14, 1.0e-14, 80);
      for (int al = 0; al < Nb; ++al) {
        for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) Sig_out[al][i][j] *= s_lab;
      }
    }
  }
}

struct HllcFluidState {
  Real D = 0.0, E = 0.0, P[3] = {0.0, 0.0, 0.0}, v[3] = {0.0, 0.0, 0.0};
  Real U0 = 1.0, h = 1.0, cs2 = 0.0, p = 0.0;
  bool valid = false;
};

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
  const Real P2 = Dot3(P, P);
  const Real dE2 = (E*E - P2 > D_tot*D_tot) ? (E*E - P2) : (D_tot*D_tot);
  const Real Minv = sqrt(dE2);
  const Real U0 = E / Minv;
  const Real w_com = Minv / D_tot;
  Real th = 0.0, h_rel = 1.0, cs2 = 0.0;
  if (w_com > 1.0 + 1.0e-12) {
    th = SafeMjThetaFromW(w_com);
    Real wm_t, ga_t;
    SyngeThermo(th, wm_t, h_rel, cs2, ga_t);
  }
  st.D = D_tot; st.E = E;
  for (int i = 0; i < 3; ++i) { st.P[i] = P[i]; st.v[i] = P[i] / E; }
  st.U0 = U0; st.h = h_rel; st.cs2 = cs2; st.p = (D_tot / U0) * th;
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

    const HllcFluidState &st = (beta_use <= S_star) ? L : R;
    const Real S_K = (beta_use <= S_star) ? S_L : S_R;
    const Real vxK = st.v[0];
    const Real p_s = (F_hll_Px - S_star * F_hll_E > 0.0) ? (F_hll_Px - S_star * F_hll_E) : 0.0;
    const Real denom = S_K - S_star;
    const Real dS_safe = (dS > 1.0) ? dS : 1.0;
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
  if (D_s <= 1.0e-300 || E_s <= 1.0e-300) return;

  Real v_s[3] = {P_s[0] / E_s, P_s[1] / E_s, P_s[2] / E_s};
  Real v_s2 = Dot3(v_s, v_s);
  if (v_s2 >= 1.0 - 1.0e-12) {
    const Real sc = sqrt((1.0 - 1.0e-12) / v_s2);
    for (int i = 0; i < 3; ++i) v_s[i] *= sc;
    v_s2 = 1.0 - 1.0e-12;
  }
  const Real U0_s = 1.0 / sqrt(1.0 - v_s2);
  const Real U_s[3] = {U0_s*v_s[0], U0_s*v_s[1], U0_s*v_s[2]};
  const Real M_inv_s = E_s / U0_s;
  const Real n_s = D_s / U0_s;
  const Real w_s = M_inv_s / D_s;
  Real th_s = 0.0, h_s = 1.0;
  if (w_s > 1.0 + 1.0e-12) {
    th_s = SafeMjThetaFromW(w_s);
    Real wm_t, cs2_t, ga_t;
    SyngeThermo(th_s, wm_t, h_s, cs2_t, ga_t);
  }
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
      FPi_ale[i][j] = M1 - beta_use * M0;
    }
  }
}

}  // namespace vlasov
}  // namespace nrpic

#endif  // PARTICLES_NRPIC_VLASOV_KERNELS_HPP_
