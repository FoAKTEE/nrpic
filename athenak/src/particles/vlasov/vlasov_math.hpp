#ifndef PARTICLES_VLASOV_VLASOV_MATH_HPP_
#define PARTICLES_VLASOV_VLASOV_MATH_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_math.hpp
//! \brief Standalone mathematical utilities, cubature rules (Stroud & S^2 Lebedev),
//! Cholesky helpers, Bessel K_n(z)*exp(z), Synge EOS, and Valencia C2P kernels.
//! Compiles inside Kokkos GPU/CPU kernels and standalone (-DNRPIC_STANDALONE).

#include <cmath>
#include "../nrpic_kernels.hpp"

namespace nrpic {
namespace vlasov {

constexpr int MAX_BASIS = 8;
constexpr int BASIS_TOPHAT = 0;
constexpr int BASIS_GAUSS  = 1;

constexpr Real kSqrt3 = 1.7320508075688772935;
constexpr Real kPi    = 3.14159265358979323846;
constexpr Real kEuler = 0.57721566490153286061;

//----------------------------------------------------------------------------------------
// Small matrix, vector & Cholesky helpers (exact mirrors of python/nrpic/vlasov_gr.py)
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
bool IsSpd3Fast(const Real A[3][3], Real eps = 0.0) {
  const Real a00 = A[0][0];
  if (a00 <= eps) return false;
  const Real d2 = a00 * A[1][1] - A[0][1] * A[0][1];
  if (d2 <= eps * eps) return false;
  const Real det = a00 * (A[1][1] * A[2][2] - A[1][2] * A[1][2])
                 - A[0][1] * (A[0][1] * A[2][2] - A[1][2] * A[0][2])
                 + A[0][2] * (A[0][1] * A[1][2] - A[1][1] * A[0][2]);
  return det > eps * eps * eps;
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

KOKKOS_INLINE_FUNCTION
Real HaltonBase(int index, int base) {
  Real f = 1.0, r = 0.0;
  int i = index;
  while (i > 0) {
    f /= static_cast<Real>(base);
    r += f * static_cast<Real>(i % base);
    i /= base;
  }
  return r;
}

KOKKOS_INLINE_FUNCTION
void HaltonSO3(int idx, Real R[3][3]) {
  const Real u1 = HaltonBase(idx + 1, 2);
  const Real u2 = HaltonBase(idx + 1, 3);
  const Real u3 = HaltonBase(idx + 1, 5);
  const Real s1 = sqrt(fmax(1.0 - u1, 0.0));
  const Real s2 = sqrt(fmax(u1, 0.0));
  const Real a1 = 2.0 * kPi * u2;
  const Real a2 = 2.0 * kPi * u3;
  const Real qx = s1 * sin(a1);
  const Real qy = s1 * cos(a1);
  const Real qz = s2 * sin(a2);
  const Real qw = s2 * cos(a2);

  const Real xx = qx * qx, yy = qy * qy, zz = qz * qz;
  const Real xy = qx * qy, xz = qx * qz, xw = qx * qw;
  const Real yz = qy * qz, yw = qy * qw, zw = qz * qw;
  R[0][0] = 1.0 - 2.0 * (yy + zz);
  R[0][1] = 2.0 * (xy - zw);
  R[0][2] = 2.0 * (xz + yw);
  R[1][0] = 2.0 * (xy + zw);
  R[1][1] = 1.0 - 2.0 * (xx + zz);
  R[1][2] = 2.0 * (yz - xw);
  R[2][0] = 2.0 * (xz - yw);
  R[2][1] = 2.0 * (yz + xw);
  R[2][2] = 1.0 - 2.0 * (xx + yy);
}

KOKKOS_INLINE_FUNCTION
void StroudCubatureRule(int n_q_scp, int basis_kind, Real xi[27][3], Real w[27], int &n_pts) {
  if (n_q_scp == 8) {
    n_pts = 8;
    int q = 0;
    for (int sx = -1; sx <= 1; sx += 2) {
      for (int sy = -1; sy <= 1; sy += 2) {
        for (int sz = -1; sz <= 1; sz += 2) {
          xi[q][0] = static_cast<Real>(sx);
          xi[q][1] = static_cast<Real>(sy);
          xi[q][2] = static_cast<Real>(sz);
          w[q] = 0.125;
          ++q;
        }
      }
    }
    return;
  }
  if (n_q_scp == 27) {
    const Real gl3_xi[3] = {-1.34164078649987384e+00, 0.0, 1.34164078649987384e+00};
    const Real gl3_w[3]  = {2.77777777777777846e-01, 4.44444444444444420e-01, 2.77777777777777846e-01};
    const Real gh3_xi[3] = {-1.73205080756887742e+00, 0.0, 1.73205080756887742e+00};
    const Real gh3_w[3]  = {1.66666666666666602e-01, 6.66666666666666852e-01, 1.66666666666666602e-01};
    const Real *x1d = (basis_kind == BASIS_GAUSS) ? gh3_xi : gl3_xi;
    const Real *w1d = (basis_kind == BASIS_GAUSS) ? gh3_w  : gl3_w;
    n_pts = 27;
    int q = 0;
    for (int i = 0; i < 3; ++i) {
      for (int j = 0; j < 3; ++j) {
        for (int k = 0; k < 3; ++k) {
          xi[q][0] = x1d[i]; xi[q][1] = x1d[j]; xi[q][2] = x1d[k];
          w[q] = w1d[i] * w1d[j] * w1d[k];
          ++q;
        }
      }
    }
    return;
  }
  // Default: degree-5 Stroud 14-point rule
  n_pts = 14;
  const bool is_gauss = (basis_kind == BASIS_GAUSS);
  const Real a  = is_gauss ? sqrt(2.5) : sqrt(1.9);
  const Real wa = is_gauss ? (4.0 / 25.0) : (40.0 / 361.0);
  const Real b  = is_gauss ? sqrt(5.0) : sqrt(19.0 / 11.0);
  const Real wb = is_gauss ? (1.0 / 200.0) : (121.0 / 2888.0);
  int q = 0;
  for (int d = 0; d < 3; ++d) {
    for (int s = -1; s <= 1; s += 2) {
      xi[q][0] = (d == 0) ? (s * a) : 0.0;
      xi[q][1] = (d == 1) ? (s * a) : 0.0;
      xi[q][2] = (d == 2) ? (s * a) : 0.0;
      w[q] = wa;
      ++q;
    }
  }
  for (int sx = -1; sx <= 1; sx += 2) {
    for (int sy = -1; sy <= 1; sy += 2) {
      for (int sz = -1; sz <= 1; sz += 2) {
        xi[q][0] = sx * b;
        xi[q][1] = sy * b;
        xi[q][2] = sz * b;
        w[q] = wb;
        ++q;
      }
    }
  }
}

//----------------------------------------------------------------------------------------
//! \fn SphericalCubatureRule
//! \brief Normalized cubature on S^2 (\sum w_q = 1, unit vectors dir_q):
//!   - 6:  octahedral vertices (degree 3 on S^2)
//!   - 12: regular icosahedron vertices (exact through l = 5)
//!   - 14: Lebedev-Laikov 14-point Oh rule (exact through l = 5)
//!   - 26: Lebedev-Laikov 26-point Oh rule (exact through l = 7: w1=1/21, w2=4/105, w3=9/280)

KOKKOS_INLINE_FUNCTION
void SphericalCubatureRule(int n_q_s2, Real dir[26][3], Real w[26], int &n_pts) {
  if (n_q_s2 == 6) {
    n_pts = 6;
    const Real w6 = 1.0 / 6.0;
    int q = 0;
    for (int d = 0; d < 3; ++d) {
      for (int s = -1; s <= 1; s += 2) {
        dir[q][0] = (d == 0) ? Real(s) : 0.0;
        dir[q][1] = (d == 1) ? Real(s) : 0.0;
        dir[q][2] = (d == 2) ? Real(s) : 0.0;
        w[q] = w6;
        ++q;
      }
    }
    return;
  }
  if (n_q_s2 == 12) {
    n_pts = 12;
    const Real phi = 0.5 * (1.0 + sqrt(5.0));
    const Real inv_n = 1.0 / sqrt(1.0 + phi * phi);
    const Real a = inv_n;
    const Real b = phi * inv_n;
    const Real w12 = 1.0 / 12.0;
    int q = 0;
    for (int s1 = -1; s1 <= 1; s1 += 2) {
      for (int s2 = -1; s2 <= 1; s2 += 2) {
        dir[q][0] = 0.0;      dir[q][1] = s1 * a; dir[q][2] = s2 * b; w[q] = w12; ++q;
        dir[q][0] = s2 * b;   dir[q][1] = 0.0;    dir[q][2] = s1 * a; w[q] = w12; ++q;
        dir[q][0] = s1 * a;   dir[q][1] = s2 * b; dir[q][2] = 0.0;    w[q] = w12; ++q;
      }
    }
    return;
  }
  if (n_q_s2 == 14) {
    n_pts = 14;
    const Real w1 = 1.0 / 15.0;
    const Real w2 = 3.0 / 40.0;
    const Real s3 = 1.0 / sqrt(3.0);
    int q = 0;
    for (int d = 0; d < 3; ++d) {
      for (int s = -1; s <= 1; s += 2) {
        dir[q][0] = (d == 0) ? Real(s) : 0.0;
        dir[q][1] = (d == 1) ? Real(s) : 0.0;
        dir[q][2] = (d == 2) ? Real(s) : 0.0;
        w[q] = w1;
        ++q;
      }
    }
    for (int sx = -1; sx <= 1; sx += 2) {
      for (int sy = -1; sy <= 1; sy += 2) {
        for (int sz = -1; sz <= 1; sz += 2) {
          dir[q][0] = sx * s3;
          dir[q][1] = sy * s3;
          dir[q][2] = sz * s3;
          w[q] = w2;
          ++q;
        }
      }
    }
    return;
  }
  // Lebedev 26-point octahedral rule (exact for all Y_lm up to l = 7)
  n_pts = 26;
  const Real w1 = 1.0 / 21.0;
  const Real w2 = 4.0 / 105.0;
  const Real w3 = 9.0 / 280.0;
  const Real s2 = 1.0 / sqrt(2.0);
  const Real s3 = 1.0 / sqrt(3.0);
  int q = 0;
  for (int d = 0; d < 3; ++d) {
    for (int s = -1; s <= 1; s += 2) {
      dir[q][0] = (d == 0) ? Real(s) : 0.0;
      dir[q][1] = (d == 1) ? Real(s) : 0.0;
      dir[q][2] = (d == 2) ? Real(s) : 0.0;
      w[q] = w1;
      ++q;
    }
  }
  for (int zero_d = 0; zero_d < 3; ++zero_d) {
    for (int s1 = -1; s1 <= 1; s1 += 2) {
      for (int s2sgn = -1; s2sgn <= 1; s2sgn += 2) {
        if (zero_d == 0) {
          dir[q][0] = 0.0;          dir[q][1] = s1 * s2; dir[q][2] = s2sgn * s2;
        } else if (zero_d == 1) {
          dir[q][0] = s1 * s2;      dir[q][1] = 0.0;     dir[q][2] = s2sgn * s2;
        } else {
          dir[q][0] = s1 * s2;      dir[q][1] = s2sgn * s2; dir[q][2] = 0.0;
        }
        w[q] = w2;
        ++q;
      }
    }
  }
  for (int sx = -1; sx <= 1; sx += 2) {
    for (int sy = -1; sy <= 1; sy += 2) {
      for (int sz = -1; sz <= 1; sz += 2) {
        dir[q][0] = sx * s3;
        dir[q][1] = sy * s3;
        dir[q][2] = sz * s3;
        w[q] = w3;
        ++q;
      }
    }
  }
}

//----------------------------------------------------------------------------------------
// Basis cubature points & stress-energy tensor quadrature (shared by MFM, BGK, HLLC)
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
  const Real tr = Sigma[0][0] + Sigma[1][1] + Sigma[2][2];
  if (tr <= 1.0e-26) {
    const Real W = sqrt(1.0 + MatVecDot3(u_bar, gi, u_bar));
    E_int = m_alpha * W;
    const Real wmW = m_alpha / W;
    for (int i = 0; i < 3; ++i) {
      P_int[i] = m_alpha * u_bar[i];
      for (int j = 0; j < 3; ++j) S_int[i][j] = wmW * u_bar[i] * u_bar[j];
    }
    return;
  }
  Real L[3][3];
  Chol3Safe(Sigma, L);
  const Real gl2_xi[2] = {-9.99999999999999889e-01, 9.99999999999999889e-01};
  const Real gl2_w[2]  = {5.0e-01, 5.0e-01};
  const Real gl3_xi[3] = {-1.34164078649987384e+00, 0.0, 1.34164078649987384e+00};
  const Real gl3_w[3]  = {2.77777777777777846e-01, 4.44444444444444420e-01, 2.77777777777777846e-01};
  const int n1d = (n_q == 3) ? 3 : 2;
  for (int i = 0; i < n1d; ++i) {
    const Real x0 = (n1d == 3) ? gl3_xi[i] : gl2_xi[i];
    const Real w0 = (n1d == 3) ? gl3_w[i]  : gl2_w[i];
    for (int j = 0; j < n1d; ++j) {
      const Real x1 = (n1d == 3) ? gl3_xi[j] : gl2_xi[j];
      const Real w1 = (n1d == 3) ? gl3_w[j]  : gl2_w[j];
      for (int k = 0; k < n1d; ++k) {
        const Real x2 = (n1d == 3) ? gl3_xi[k] : gl2_xi[k];
        const Real w2 = (n1d == 3) ? gl3_w[k]  : gl2_w[k];
        const Real pt[3] = {
          u_bar[0] + L[0][0]*x0 + L[0][1]*x1 + L[0][2]*x2,
          u_bar[1] + L[1][0]*x0 + L[1][1]*x1 + L[1][2]*x2,
          u_bar[2] + L[2][0]*x0 + L[2][1]*x1 + L[2][2]*x2
        };
        const Real W = sqrt(1.0 + MatVecDot3(pt, gi, pt));
        const Real wm = m_alpha * w0 * w1 * w2;
        E_int += wm * W;
        const Real wmW = wm / W;
        for (int a = 0; a < 3; ++a) {
          P_int[a] += wm * pt[a];
          for (int b = 0; b < 3; ++b) {
            S_int[a][b] += wmW * pt[a] * pt[b];
          }
        }
      }
    }
  }
}

//----------------------------------------------------------------------------------------
// CUDA-device-safe Bessel K_n(z)*exp(z), Synge EOS, Moller rate, and Valencia C2P
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
void Kve2And3(Real z, Real &k2e, Real &k3e) {
  if (z < 1.0e-8) {
    const Real ez = exp(z);
    const Real inv_z2 = 1.0 / (z * z);
    k2e = 2.0 * ez * inv_z2;
    k3e = 8.0 * ez * inv_z2 / z;
    return;
  }
  if (z < 2.0) {
    Kve2And3Series(z, k2e, k3e);
    return;
  }
  const Real sq = sqrt(kPi / (2.0 * z));
  if (z > 1.0e8) {
    k2e = sq * (1.0 + 15.0 / (8.0 * z));
    k3e = sq * (1.0 + 35.0 / (8.0 * z));
    return;
  }
  const Real c2[22] = {
     1.5369562709347966e+00,  5.5848397424280200e-01,  2.0881208230680700e-02, -5.9855899178500930e-04,
     4.2825914991535946e-05, -4.4334910407642620e-06,  5.7252787593659550e-07, -8.6199405643664050e-08,
     1.4567477123573657e-08, -2.6978141135200220e-09,  5.3859570339007880e-10, -1.1455063160652075e-10,
     2.5724624450808940e-11, -6.0566602238571420e-12,  1.4864170500510971e-12, -3.7927237108512850e-13,
     1.0048023019687043e-13, -2.7886783791266433e-14,  6.8531039429134660e-15, -1.2818029466126807e-15,
     1.1354553660939100e-16, -1.7397699442705580e-15
  };
  const Real c3[22] = {
     2.9015710746079240e+00,  2.1887999942085252e+00,  2.9754370790629410e-01,  1.0019217529269042e-02,
    -2.7411895112389677e-04,  1.9185827578911812e-05, -1.9667333771163213e-06,  2.5315549516276420e-07,
    -3.8135857239783960e-08,  6.4630000543272360e-09, -1.2019289301208728e-09,  2.4116070756525170e-10,
    -5.1573856296727170e-11,  1.1650771256845681e-11, -2.7610035470037144e-12,  6.8190907466135860e-13,
    -1.7445640891496210e-13,  4.5448493453518910e-14, -1.4337016422545770e-14,  4.5569608692568930e-15,
    -2.0185873175002848e-15, -8.2762080017511670e-16
  };
  const Real u = 4.0 / z - 1.0;
  Real b1_2 = 0.0, b2_2 = 0.0;
  Real b1_3 = 0.0, b2_3 = 0.0;
  for (int j = 21; j >= 1; --j) {
    const Real b0_2 = 2.0 * u * b1_2 - b2_2 + c2[j];
    b2_2 = b1_2;
    b1_2 = b0_2;
    const Real b0_3 = 2.0 * u * b1_3 - b2_3 + c3[j];
    b2_3 = b1_3;
    b1_3 = b0_3;
  }
  k2e = (u * b1_2 - b2_2 + c2[0]) * sq;
  k3e = (u * b1_3 - b2_3 + c3[0]) * sq;
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
void SyngeThermoDeriv(Real theta, Real &w_mean, Real &h_rel, Real &dh_dth,
                      Real &cs2, Real &gamma_ad) {
  if (theta <= 0.0) {
    w_mean = 1.0; h_rel = 1.0; dh_dth = 2.5; cs2 = 0.0; gamma_ad = 5.0 / 3.0;
    return;
  }
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
    Real k2, k3;
    Kve2And3(z, k2, k3);
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
void SyngeThermo(Real theta, Real &w_mean, Real &h_rel, Real &cs2, Real &gamma_ad) {
  Real dh_dth;
  SyngeThermoDeriv(theta, w_mean, h_rel, dh_dth, cs2, gamma_ad);
}

KOKKOS_INLINE_FUNCTION
Real SafeMjThetaFromW(Real w) {
  if (w <= 1.0 + 1.0e-15) return 0.0;
  if (w <= 1.0 + 1.0e-5) {
    const Real dw = w - 1.0;
    return (-1.5 + sqrt(2.25 + 7.5 * dw)) / 3.75;
  }
  if (w >= 1.0e5) return w / 3.0;

  Real th = (w < 2.0) ? ((w - 1.0) / 1.5) : ((w - 1.0) / 3.0);
  if (th < 1.0e-8) th = 1.0e-8;
  Real lo = 0.0, hi = -1.0;
  for (int it = 0; it < 32; ++it) {
    Real wm_t, hr_t, dh_t, cs2_t, ga_t;
    SyngeThermoDeriv(th, wm_t, hr_t, dh_t, cs2_t, ga_t);
    const Real f = wm_t - w;
    if (fabs(f) <= 1.0e-14 * w) break;
    if (f < 0.0) lo = th;
    else         hi = th;
    if (hi < 0.0 && th >= 1.0e8) { th = 1.0e8; break; }
    const Real df = dh_t - 1.0;
    Real th_new = (df > 1.0e-30) ? (th - f / df) : -1.0;
    if (hi > 0.0) {
      if (!(th_new > lo && th_new < hi)) th_new = 0.5 * (lo + hi);
    } else {
      if (th_new <= lo) th_new = (2.0 * th > 1.0e-2) ? (2.0 * th) : 1.0e-2;
    }
    if (th_new > 1.0e8) th_new = 1.0e8;
    const Real diff = fabs(th_new - th);
    th = th_new;
    if (diff <= 1.0e-14 * (1.0 + th)) break;
  }
  return th;
}

KOKKOS_INLINE_FUNCTION
Real MjVmol(Real theta) {
  if (theta <= 0.0) return 0.0;
  if (theta < 1.0e-6) return sqrt(16.0 * theta / kPi);
  const Real z = 1.0 / theta;
  const Real k2 = Kve2(z);
  return 4.0 * Kve3(2.0 * z) / (z * k2 * k2);
}

struct HllcFluidState {
  Real D = 0.0, E = 0.0, P[3] = {0.0, 0.0, 0.0}, v[3] = {0.0, 0.0, 0.0};
  Real U0 = 1.0, h = 1.0, cs2 = 0.0, p = 0.0, rho0 = 0.0, theta = 0.0, w_m = 1.0;
  bool valid = false;
};

KOKKOS_INLINE_FUNCTION
void ValenciaC2PSynge(Real D, Real E, const Real P[3],
                      Real &theta, Real &h_rel, Real &cs2, Real &w_m,
                      Real &U0, Real &rho0, Real &p, Real v[3]) {
  if (D <= 1.0e-300) {
    theta = 0.0; h_rel = 1.0; cs2 = 0.0; w_m = 1.0;
    U0 = 1.0; rho0 = 0.0; p = 0.0;
    v[0] = v[1] = v[2] = 0.0;
    return;
  }
  const Real P2 = Dot3(P, P);
  const Real E_cold = sqrt(D * D + P2);
  if (E <= E_cold * (1.0 + 1.0e-14)) {
    theta = 0.0; h_rel = 1.0; cs2 = 0.0; w_m = 1.0; p = 0.0;
    U0 = E_cold / D;
    rho0 = D / U0;
    const Real invE = (E_cold > 1.0e-300) ? (1.0 / E_cold) : 0.0;
    for (int i = 0; i < 3; ++i) v[i] = P[i] * invE;
    return;
  }

  Real th = (E - E_cold) / (1.5 * D);
  if (th < 1.0e-8) th = 1.0e-8;
  Real lo = 0.0, hi = -1.0;
  for (int it = 0; it < 32; ++it) {
    Real wm_t, hr_t, dh_t, cs2_t, ga_t;
    SyngeThermoDeriv(th, wm_t, hr_t, dh_t, cs2_t, ga_t);
    const Real Dh = D * hr_t;
    const Real Dh2 = Dh * Dh;
    const Real u0_t = sqrt(1.0 + P2 / Dh2);
    const Real f = Dh * u0_t - (D / u0_t) * th - E;
    if (fabs(f) <= 1.0e-14 * E) break;
    if (f < 0.0) lo = th;
    else         hi = th;
    if (hi < 0.0 && th >= 1.0e8) { th = 1.0e8; break; }
    const Real v2 = P2 / (Dh2 + P2);
    const Real df = (D / u0_t) * ((1.0 - th * v2 / hr_t) * dh_t - 1.0);
    Real th_new = (df > 1.0e-30) ? (th - f / df) : -1.0;
    if (hi > 0.0) {
      if (!(th_new > lo && th_new < hi)) th_new = 0.5 * (lo + hi);
    } else {
      if (th_new <= lo) th_new = (2.0 * th > 1.0e-2) ? (2.0 * th) : 1.0e-2;
    }
    if (th_new > 1.0e8) th_new = 1.0e8;
    const Real diff = fabs(th_new - th);
    th = th_new;
    if (diff <= 1.0e-14 * (1.0 + th)) break;
  }
  theta = th;

  Real ga_t;
  SyngeThermo(theta, w_m, h_rel, cs2, ga_t);
  const Real Dh = D * h_rel;
  U0 = sqrt(1.0 + P2 / (Dh * Dh));
  rho0 = D / U0;
  p = rho0 * theta;
  const Real inv_DhU0 = 1.0 / (Dh * U0);
  for (int i = 0; i < 3; ++i) v[i] = P[i] * inv_DhU0;
}

}  // namespace vlasov
}  // namespace nrpic

#endif  // PARTICLES_VLASOV_VLASOV_MATH_HPP_

