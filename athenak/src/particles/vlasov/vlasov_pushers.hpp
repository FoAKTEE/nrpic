#ifndef PARTICLES_VLASOV_VLASOV_PUSHERS_HPP_
#define PARTICLES_VLASOV_VLASOV_PUSHERS_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_pushers.hpp
//! \brief Geodesic cubature kicks, time-fraction metric evaluation (linear & quadratic),
//! and 4th-order symplectic Gauss-Legendre 2-stage IRK pusher (PushGL4).

#include <cmath>
#include <type_traits>
#include "vlasov_math.hpp"

namespace nrpic {
namespace vlasov {

namespace detail {
template <typename T, typename = void>
struct HasEvalAtFrac : std::false_type {};

template <typename T>
struct HasEvalAtFrac<T, decltype(void(
    std::declval<const T &>().EvalAtFrac(
        Real(0), static_cast<const Real *>(nullptr), std::declval<AdmPoint &>())))>
    : std::true_type {};
}  // namespace detail

KOKKOS_INLINE_FUNCTION
void BlendAdm2(Real w0, const AdmPoint &p0, Real w1, const AdmPoint &p1, AdmPoint &out) {
  out.alp = w0 * p0.alp + w1 * p1.alp;
  for (int i = 0; i < 3; ++i) {
    out.beta[i] = w0 * p0.beta[i] + w1 * p1.beta[i];
    out.dalp[i] = w0 * p0.dalp[i] + w1 * p1.dalp[i];
    for (int j = 0; j < 3; ++j) {
      out.g[i][j]     = w0 * p0.g[i][j]     + w1 * p1.g[i][j];
      out.dbeta[i][j] = w0 * p0.dbeta[i][j] + w1 * p1.dbeta[i][j];
      for (int k = 0; k < 3; ++k) {
        out.dg[i][j][k] = w0 * p0.dg[i][j][k] + w1 * p1.dg[i][j][k];
      }
    }
  }
}

KOKKOS_INLINE_FUNCTION
void BlendAdm3(Real wm1, const AdmPoint &pm1,
               Real w0,  const AdmPoint &p0,
               Real w1,  const AdmPoint &p1, AdmPoint &out) {
  out.alp = wm1 * pm1.alp + w0 * p0.alp + w1 * p1.alp;
  for (int i = 0; i < 3; ++i) {
    out.beta[i] = wm1 * pm1.beta[i] + w0 * p0.beta[i] + w1 * p1.beta[i];
    out.dalp[i] = wm1 * pm1.dalp[i] + w0 * p0.dalp[i] + w1 * p1.dalp[i];
    for (int j = 0; j < 3; ++j) {
      out.g[i][j]     = wm1 * pm1.g[i][j]     + w0 * p0.g[i][j]     + w1 * p1.g[i][j];
      out.dbeta[i][j] = wm1 * pm1.dbeta[i][j] + w0 * p0.dbeta[i][j] + w1 * p1.dbeta[i][j];
      for (int k = 0; k < 3; ++k) {
        out.dg[i][j][k] = wm1 * pm1.dg[i][j][k] + w0 * p0.dg[i][j][k] + w1 * p1.dg[i][j][k];
      }
    }
  }
}

// Evaluate ADM metric at time fraction frac in [0, 1] across [t^n, t^{n+1}].
template <class MetricT>
KOKKOS_INLINE_FUNCTION
void EvaluateAdmAtFrac(const MetricT &met, Real frac, const Real x[3], AdmPoint &p) {
  if constexpr (detail::HasEvalAtFrac<MetricT>::value) {
    met.EvalAtFrac(frac, x, p);
  } else if (met.IsStatic()) {
    met(0, x, p);
  } else {
    AdmPoint p0, p1;
    met(0, x, p0);
    met(1, x, p1);
    BlendAdm2(1.0 - frac, p0, frac, p1, p);
  }
}

// Fixed-x geodesic kick at pre-inverted metric gi.
KOKKOS_INLINE_FUNCTION
void GeodesicKickPointPreinv(const AdmPoint &adm, const Real gi[3][3], Real dt,
                            const Real u_in[3], Real u_out[3],
                            Real tol = 1.0e-12, int maxit = 50) {
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
void GeodesicKickPoint(const AdmPoint &adm0, const AdmPoint *adm1, Real dt,
                       const Real u_in[3], Real u_out[3],
                       Real tol = 1.0e-12, int maxit = 50) {
  AdmPoint adm = adm0;
  if (adm1 != nullptr) AverageAdm(adm, *adm1);
  Real gi[3][3];
  Inv3Sym(adm.g, gi);
  GeodesicKickPointPreinv(adm, gi, dt, u_in, u_out, tol, maxit);
}

KOKKOS_INLINE_FUNCTION
void CubatureGeodesicKick(const Real u_bar[3], const Real Sigma[3][3],
                          const AdmPoint &adm0, const AdmPoint *adm1, Real dt,
                          int n_q, Real u_new[3], Real Sig_new[3][3], Real tol = 1.0e-12) {
  AdmPoint adm = adm0;
  if (adm1 != nullptr) AverageAdm(adm, *adm1);
  Real gi[3][3];
  Inv3Sym(adm.g, gi);

  const Real tr = Sigma[0][0] + Sigma[1][1] + Sigma[2][2];
  if (tr <= 1.0e-26) {
    GeodesicKickPointPreinv(adm, gi, dt, u_bar, u_new, tol);
    for (int i = 0; i < 3; ++i) {
      for (int j = 0; j < 3; ++j) Sig_new[i][j] = 0.0;
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

  Real u_ref[3];
  GeodesicKickPointPreinv(adm, gi, dt, u_bar, u_ref, tol);

  Real du_mean[3] = {0.0, 0.0, 0.0};
  Real M2[3][3] = {{0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}};
  for (int i = 0; i < n1d; ++i) {
    const Real x0 = (n1d == 3) ? gl3_xi[i] : gl2_xi[i];
    const Real w0 = (n1d == 3) ? gl3_w[i]  : gl2_w[i];
    for (int j = 0; j < n1d; ++j) {
      const Real x1 = (n1d == 3) ? gl3_xi[j] : gl2_xi[j];
      const Real w1 = (n1d == 3) ? gl3_w[j]  : gl2_w[j];
      for (int k = 0; k < n1d; ++k) {
        const Real x2 = (n1d == 3) ? gl3_xi[k] : gl2_xi[k];
        const Real w2 = (n1d == 3) ? gl3_w[k]  : gl2_w[k];
        const Real wq = w0 * w1 * w2;
        const Real pt[3] = {
          u_bar[0] + L[0][0]*x0 + L[0][1]*x1 + L[0][2]*x2,
          u_bar[1] + L[1][0]*x0 + L[1][1]*x1 + L[1][2]*x2,
          u_bar[2] + L[2][0]*x0 + L[2][1]*x1 + L[2][2]*x2
        };
        Real pt_new[3];
        GeodesicKickPointPreinv(adm, gi, dt, pt, pt_new, tol);
        const Real du[3] = {pt_new[0] - u_ref[0], pt_new[1] - u_ref[1], pt_new[2] - u_ref[2]};
        for (int a = 0; a < 3; ++a) {
          du_mean[a] += wq * du[a];
          for (int b = 0; b < 3; ++b) M2[a][b] += wq * du[a] * du[b];
        }
      }
    }
  }
  for (int a = 0; a < 3; ++a) u_new[a] = u_ref[a] + du_mean[a];
  for (int a = 0; a < 3; ++a) {
    for (int b = a; b < 3; ++b) {
      const Real val = M2[a][b] - du_mean[a] * du_mean[b];
      Sig_new[a][b] = Sig_new[b][a] = val;
    }
  }
}

//----------------------------------------------------------------------------------------
//! \fn GeodesicRhsFromAdm
//! \brief Evaluates Hamiltonian geodesic RHS (dx^i/dt, du_i/dt), lapse, and W.

KOKKOS_INLINE_FUNCTION
void GeodesicRhsFromAdm(const AdmPoint &p, const Real u[3], const Real eps,
                        Real dx[3], Real du[3], Real &W_out) {
  Real gi[3][3], uup[3];
  Inv3Sym(p.g, gi);
  const Real W = LorentzFactorEps(gi, u, eps, uup);
  W_out = W;
  const Real invW = (W > 0.0) ? (1.0 / W) : 0.0;
  for (int i = 0; i < 3; ++i) {
    dx[i] = p.alp * uup[i] * invW - p.beta[i];
    Real geo = 0.0;
    for (int l = 0; l < 3; ++l) {
      for (int m = 0; m < 3; ++m) {
        geo += uup[l] * uup[m] * p.dg[i][l][m];
      }
    }
    Real db = 0.0;
    for (int j = 0; j < 3; ++j) db += u[j] * p.dbeta[i][j];
    du[i] = -W * p.dalp[i] + 0.5 * p.alp * geo * invW + db;
  }
}

//----------------------------------------------------------------------------------------
//! \fn PushGL4
//! \brief 4th-order symplectic 2-stage Gauss-Legendre implicit Runge-Kutta geodesic
//! pusher in coordinate variables (x^i, u_i):
//!   c = [1/2 - sqrt(3)/6, 1/2 + sqrt(3)/6],  b = [1/2, 1/2],
//!   A = [[1/4, 1/4 - sqrt(3)/6], [1/4 + sqrt(3)/6, 1/4]].
//! Uses EvaluateAdmAtFrac at the stage times c_1, c_2 (supports static metrics,
//! 2-level linear interpolation, and 3-level quadratic Lagrange time interpolation).
//! Returns iteration count (>0 if converged, <0 if unconverged within maxit).

template <class MetricT>
KOKKOS_INLINE_FUNCTION
int PushGL4(const MetricT &met, const Real dt, const Real tol, const int maxit,
            Real x[3], Real u[3], const Real eps, Real &dtau) {
  constexpr Real s3o6 = 0.28867513459481288225;  // sqrt(3)/6
  const Real c0 = 0.5 - s3o6;
  const Real c1 = 0.5 + s3o6;
  const Real a00 = 0.25, a01 = 0.25 - s3o6;
  const Real a10 = 0.25 + s3o6, a11 = 0.25;

  const Real x0[3] = {x[0], x[1], x[2]};
  const Real u0[3] = {u[0], u[1], u[2]};

  AdmPoint p_init;
  met(0, x0, p_init);
  Real k0x[3], k0u[3], W_init;
  GeodesicRhsFromAdm(p_init, u0, eps, k0x, k0u, W_init);

  Real yx[2][3], yu[2][3];
  for (int i = 0; i < 3; ++i) {
    yx[0][i] = x0[i] + dt * c0 * k0x[i];
    yu[0][i] = u0[i] + dt * c0 * k0u[i];
    yx[1][i] = x0[i] + dt * c1 * k0x[i];
    yu[1][i] = u0[i] + dt * c1 * k0u[i];
  }

  Real k1x[3] = {0.0, 0.0, 0.0}, k1u[3] = {0.0, 0.0, 0.0};
  Real k2x[3] = {0.0, 0.0, 0.0}, k2u[3] = {0.0, 0.0, 0.0};
  Real alp1 = p_init.alp, alp2 = p_init.alp, W1 = W_init, W2 = W_init;

  int it = 0;
  bool converged = false;
  while (it < maxit) {
    ++it;
    AdmPoint p1, p2;
    EvaluateAdmAtFrac(met, c0, yx[0], p1);
    EvaluateAdmAtFrac(met, c1, yx[1], p2);
    alp1 = p1.alp;
    alp2 = p2.alp;
    GeodesicRhsFromAdm(p1, yu[0], eps, k1x, k1u, W1);
    GeodesicRhsFromAdm(p2, yu[1], eps, k2x, k2u, W2);

    Real err = 0.0;
    for (int i = 0; i < 3; ++i) {
      const Real y0x_n = x0[i] + dt * (a00 * k1x[i] + a01 * k2x[i]);
      const Real y0u_n = u0[i] + dt * (a00 * k1u[i] + a01 * k2u[i]);
      const Real y1x_n = x0[i] + dt * (a10 * k1x[i] + a11 * k2x[i]);
      const Real y1u_n = u0[i] + dt * (a10 * k1u[i] + a11 * k2u[i]);
      err = fmax(err, fabs(y0x_n - yx[0][i]));
      err = fmax(err, fabs(y0u_n - yu[0][i]));
      err = fmax(err, fabs(y1x_n - yx[1][i]));
      err = fmax(err, fabs(y1u_n - yu[1][i]));
      yx[0][i] = y0x_n;
      yu[0][i] = y0u_n;
      yx[1][i] = y1x_n;
      yu[1][i] = y1u_n;
    }
    if (err < tol) {
      converged = true;
      break;
    }
  }

  for (int i = 0; i < 3; ++i) {
    x[i] = x0[i] + 0.5 * dt * (k1x[i] + k2x[i]);
    u[i] = u0[i] + 0.5 * dt * (k1u[i] + k2u[i]);
  }
  dtau = 0.5 * dt * (alp1 / W1 + alp2 / W2);
  return converged ? it : -it;
}

template <class MetricT>
KOKKOS_INLINE_FUNCTION
int PushGL4(const MetricT &met, const Real dt, const Real tol, const int maxit,
            Real x[3], Real u[3]) {
  Real dtau = 0.0;
  return PushGL4(met, dt, tol, maxit, x, u, 1.0, dtau);
}

}  // namespace vlasov
}  // namespace nrpic

#endif  // PARTICLES_VLASOV_VLASOV_PUSHERS_HPP_
