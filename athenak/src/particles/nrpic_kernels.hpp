#ifndef PARTICLES_NRPIC_KERNELS_HPP_
#define PARTICLES_NRPIC_KERNELS_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_kernels.hpp
//! \brief Point kernels for the NRPIC geodesic pushers: implicit midpoint in the
//! coordinate variables (x^i, u_i) and the spacetime (DGREM) Boris scheme in
//! (x^i, u_hat-i).  The kernels see the spacetime only through a metric functor that
//! returns the 3+1 fields and their first spatial derivatives at a point, so the same
//! code runs on mesh data, on analytic metrics, and in any spatial coordinate system.
//!
//! The file has no dependence on the rest of AthenaK.  Define NRPIC_STANDALONE to
//! compile it outside the code (see tst/nrpic).

#ifdef NRPIC_STANDALONE
#include <cmath>
using Real = double;
#ifndef KOKKOS_INLINE_FUNCTION
#define KOKKOS_INLINE_FUNCTION inline
#endif
#else
#include <cmath>
#include "athena.hpp"
#endif

namespace nrpic {

//----------------------------------------------------------------------------------------
//! \struct AdmPoint
//! \brief 3+1 metric fields and their first spatial derivatives at one point.

struct AdmPoint {
  Real alp;            // lapse
  Real beta[3];        // shift beta^i
  Real g[3][3];        // spatial metric gamma_ij
  Real dalp[3];        // dalp[k]     = d_k alpha
  Real dbeta[3][3];    // dbeta[k][i] = d_k beta^i
  Real dg[3][3][3];    // dg[k][i][j] = d_k gamma_ij
};

//----------------------------------------------------------------------------------------
//! \fn AverageAdm
//! \brief p0 <- (p0 + p1)/2 for all fields and derivatives

KOKKOS_INLINE_FUNCTION
void AverageAdm(AdmPoint &p0, const AdmPoint &p1) {
  p0.alp = 0.5*(p0.alp + p1.alp);
  for (int i=0; i<3; ++i) {
    p0.beta[i] = 0.5*(p0.beta[i] + p1.beta[i]);
    p0.dalp[i] = 0.5*(p0.dalp[i] + p1.dalp[i]);
    for (int j=0; j<3; ++j) {
      p0.g[i][j]     = 0.5*(p0.g[i][j] + p1.g[i][j]);
      p0.dbeta[i][j] = 0.5*(p0.dbeta[i][j] + p1.dbeta[i][j]);
      for (int k=0; k<3; ++k) {
        p0.dg[i][j][k] = 0.5*(p0.dg[i][j][k] + p1.dg[i][j][k]);
      }
    }
  }
}

//----------------------------------------------------------------------------------------
//! \fn Inv3Sym
//! \brief inverse and determinant of a symmetric 3x3 matrix

KOKKOS_INLINE_FUNCTION
Real Inv3Sym(const Real g[3][3], Real gi[3][3]) {
  Real c00 = g[1][1]*g[2][2] - g[1][2]*g[1][2];
  Real c01 = g[0][2]*g[1][2] - g[0][1]*g[2][2];
  Real c02 = g[0][1]*g[1][2] - g[0][2]*g[1][1];
  Real det = g[0][0]*c00 + g[0][1]*c01 + g[0][2]*c02;
  Real idet = 1.0/det;
  gi[0][0] = c00*idet;
  gi[0][1] = c01*idet;
  gi[0][2] = c02*idet;
  gi[1][1] = (g[0][0]*g[2][2] - g[0][2]*g[0][2])*idet;
  gi[1][2] = (g[0][1]*g[0][2] - g[0][0]*g[1][2])*idet;
  gi[2][2] = (g[0][0]*g[1][1] - g[0][1]*g[0][1])*idet;
  gi[1][0] = gi[0][1];
  gi[2][0] = gi[0][2];
  gi[2][1] = gi[1][2];
  return det;
}

//----------------------------------------------------------------------------------------
//! \fn Chol3
//! \brief Cholesky factor of a symmetric positive-definite 3x3 matrix, g = L L^T with L
//! lower triangular, together with L^{-1}.

KOKKOS_INLINE_FUNCTION
void Chol3(const Real g[3][3], Real L[3][3], Real Li[3][3]) {
  L[0][0] = sqrt(g[0][0]);
  L[1][0] = g[1][0]/L[0][0];
  L[2][0] = g[2][0]/L[0][0];
  L[1][1] = sqrt(g[1][1] - L[1][0]*L[1][0]);
  L[2][1] = (g[2][1] - L[2][0]*L[1][0])/L[1][1];
  L[2][2] = sqrt(g[2][2] - L[2][0]*L[2][0] - L[2][1]*L[2][1]);
  L[0][1] = 0.0; L[0][2] = 0.0; L[1][2] = 0.0;

  Li[0][0] = 1.0/L[0][0];
  Li[1][1] = 1.0/L[1][1];
  Li[2][2] = 1.0/L[2][2];
  Li[1][0] = -L[1][0]*Li[0][0]*Li[1][1];
  Li[2][1] = -L[2][1]*Li[1][1]*Li[2][2];
  Li[2][0] = -(L[2][0]*Li[0][0] + L[2][1]*Li[1][0])*Li[2][2];
  Li[0][1] = 0.0; Li[0][2] = 0.0; Li[1][2] = 0.0;
}

//----------------------------------------------------------------------------------------
//! \fn DChol3
//! \brief derivative of the Cholesky factor: given g = L L^T and a symmetric variation
//! dg, returns dL.  With Phi = L^{-1} dg L^{-T}, dL = L * (strict lower part of Phi plus
//! half its diagonal).

KOKKOS_INLINE_FUNCTION
void DChol3(const Real L[3][3], const Real Li[3][3], const Real dg[3][3],
            Real dL[3][3]) {
  Real T[3][3];                  // T = Li * dg
  for (int i=0; i<3; ++i) {
    for (int j=0; j<3; ++j) {
      Real s = 0.0;
      for (int k=0; k<=i; ++k) { s += Li[i][k]*dg[k][j]; }
      T[i][j] = s;
    }
  }
  Real P[3][3];                  // lower triangle of T * Li^T with halved diagonal
  for (int i=0; i<3; ++i) {
    for (int j=0; j<3; ++j) {
      if (j > i) {
        P[i][j] = 0.0;
      } else {
        Real s = 0.0;
        for (int k=0; k<=j; ++k) { s += T[i][k]*Li[j][k]; }
        P[i][j] = (i == j) ? 0.5*s : s;
      }
    }
  }
  for (int i=0; i<3; ++i) {      // dL = L * P
    for (int j=0; j<3; ++j) {
      Real s = 0.0;
      for (int k=j; k<=i; ++k) { s += L[i][k]*P[k][j]; }
      dL[i][j] = s;
    }
  }
}

//----------------------------------------------------------------------------------------
//! \fn SymEig3
//! \brief eigen-decomposition of a symmetric 3x3 matrix by cyclic Jacobi rotations,
//! A = V diag(w) V^T with the eigenvectors in the columns of V.

KOKKOS_INLINE_FUNCTION
void SymEig3(const Real Ain[3][3], Real V[3][3], Real w[3]) {
  Real A[3][3];
  for (int i=0; i<3; ++i) {
    for (int j=0; j<3; ++j) {
      A[i][j] = Ain[i][j];
      V[i][j] = (i == j) ? 1.0 : 0.0;
    }
  }
  for (int sweep=0; sweep<32; ++sweep) {
    Real off = fabs(A[0][1]) + fabs(A[0][2]) + fabs(A[1][2]);
    Real dia = fabs(A[0][0]) + fabs(A[1][1]) + fabs(A[2][2]);
    if (off <= 1.0e-17*dia) break;
    for (int p=0; p<2; ++p) {
      for (int q=p+1; q<3; ++q) {
        if (fabs(A[p][q]) <= 1.0e-300) continue;
        Real th = (A[q][q] - A[p][p])/(2.0*A[p][q]);
        Real t = ((th >= 0.0) ? 1.0 : -1.0)/(fabs(th) + sqrt(th*th + 1.0));
        Real c = 1.0/sqrt(t*t + 1.0);
        Real s = t*c;
        for (int k=0; k<3; ++k) {
          Real akp = A[k][p], akq = A[k][q];
          A[k][p] = c*akp - s*akq;
          A[k][q] = s*akp + c*akq;
        }
        for (int k=0; k<3; ++k) {
          Real apk = A[p][k], aqk = A[q][k];
          A[p][k] = c*apk - s*aqk;
          A[q][k] = s*apk + c*aqk;
        }
        for (int k=0; k<3; ++k) {
          Real vkp = V[k][p], vkq = V[k][q];
          V[k][p] = c*vkp - s*vkq;
          V[k][q] = s*vkp + c*vkq;
        }
      }
    }
  }
  w[0] = A[0][0];
  w[1] = A[1][1];
  w[2] = A[2][2];
}

//----------------------------------------------------------------------------------------
//! \struct Triad
//! \brief spatial triad of the normal observers.  The coframe is e^(m)_j = S[j][m] and
//! the frame vectors are e^j_(m) = Si[m][j], with Si the matrix inverse of S and
//! S S^T = gamma.  Two gauges are available:
//!   kTriadSymmetric  S = gamma^{1/2}, the symmetric positive square root.  V and sw
//!                    hold the eigenvectors of gamma and the square roots of its
//!                    eigenvalues, which are reused for the derivatives of S.
//!   kTriadCholesky   S = L, the lower-triangular Cholesky factor (Gram-Schmidt on the
//!                    coordinate basis vectors in index order).

enum TriadKind { kTriadSymmetric = 0, kTriadCholesky = 1 };

struct Triad {
  Real S[3][3];
  Real Si[3][3];
  Real V[3][3];
  Real sw[3];
};

KOKKOS_INLINE_FUNCTION
void BuildTriad(const int kind, const Real g[3][3], Triad &tr) {
  if (kind == kTriadCholesky) {
    Chol3(g, tr.S, tr.Si);
    return;
  }
  Real w[3];
  SymEig3(g, tr.V, w);
  for (int a=0; a<3; ++a) { tr.sw[a] = sqrt(w[a]); }
  for (int i=0; i<3; ++i) {
    for (int j=i; j<3; ++j) {
      Real s = 0.0, si = 0.0;
      for (int a=0; a<3; ++a) {
        s  += tr.V[i][a]*tr.sw[a]*tr.V[j][a];
        si += tr.V[i][a]*tr.V[j][a]/tr.sw[a];
      }
      tr.S[i][j] = s;   tr.S[j][i] = s;
      tr.Si[i][j] = si; tr.Si[j][i] = si;
    }
  }
}

//----------------------------------------------------------------------------------------
//! \fn TriadDeriv
//! \brief variation dS of the triad for a symmetric variation dg of the metric.  In the
//! symmetric gauge S dS + dS S = dg is solved in the eigenbasis of the metric.

KOKKOS_INLINE_FUNCTION
void TriadDeriv(const int kind, const Triad &tr, const Real dg[3][3], Real dS[3][3]) {
  if (kind == kTriadCholesky) {
    DChol3(tr.S, tr.Si, dg, dS);
    return;
  }
  Real T[3][3], M[3][3];
  for (int i=0; i<3; ++i) {      // T = dg V
    for (int b=0; b<3; ++b) {
      T[i][b] = dg[i][0]*tr.V[0][b] + dg[i][1]*tr.V[1][b] + dg[i][2]*tr.V[2][b];
    }
  }
  for (int a=0; a<3; ++a) {      // M = (V^T dg V)_ab / (sw_a + sw_b)
    for (int b=0; b<3; ++b) {
      M[a][b] = (tr.V[0][a]*T[0][b] + tr.V[1][a]*T[1][b] + tr.V[2][a]*T[2][b])
                /(tr.sw[a] + tr.sw[b]);
    }
  }
  for (int a=0; a<3; ++a) {      // T = M V^T
    for (int j=0; j<3; ++j) {
      T[a][j] = M[a][0]*tr.V[j][0] + M[a][1]*tr.V[j][1] + M[a][2]*tr.V[j][2];
    }
  }
  for (int i=0; i<3; ++i) {      // dS = V M V^T
    for (int j=0; j<3; ++j) {
      dS[i][j] = tr.V[i][0]*T[0][j] + tr.V[i][1]*T[1][j] + tr.V[i][2]*T[2][j];
    }
  }
}

//----------------------------------------------------------------------------------------
//! \fn HermiteWeights
//! \brief cubic Hermite (Catmull-Rom) weights and their derivatives for the four nodes
//! at offsets -1,0,1,2 from the base node, s = (x - x_base)/h.  The derivative weights
//! must be divided by h.

KOKKOS_INLINE_FUNCTION
void HermiteWeights(const Real s, Real w[4], Real dw[4]) {
  Real s2 = s*s;
  Real s3 = s2*s;
  w[0] = 0.5*(-s + 2.0*s2 - s3);
  w[1] = 0.5*(2.0 - 5.0*s2 + 3.0*s3);
  w[2] = 0.5*(s + 4.0*s2 - 3.0*s3);
  w[3] = 0.5*(-s2 + s3);
  dw[0] = 0.5*(-1.0 + 4.0*s - 3.0*s2);
  dw[1] = 0.5*(-10.0*s + 9.0*s2);
  dw[2] = 0.5*(1.0 + 8.0*s - 9.0*s2);
  dw[3] = 0.5*(-2.0*s + 3.0*s2);
}

//----------------------------------------------------------------------------------------
//! \fn BSplineWeights
//! \brief weights of the cubic B-spline and their derivatives for the four nodes at
//! offsets -1,0,1,2 from the base node, s = (x - x_base)/h in [0,1).  The derivative
//! weights must be divided by h.  Applied to nodal values that were sharpened with the
//! inverse of the sampled spline (Particles::NrpicSharpenMetric), this is the cubic
//! spline through the nodes: twice continuously differentiable, with a gradient whose
//! error does not depend on the position within the cell at second order, unlike the
//! Catmull-Rom weights (gradient low by (k h)^2/6 at the nodes and high by (k h)^2/12
//! midway between them for a wave of wavenumber k).

KOKKOS_INLINE_FUNCTION
void BSplineWeights(const Real s, Real w[4], Real dw[4]) {
  const Real t = 1.0 - s;
  const Real s2 = s*s;
  w[0] = t*t*t/6.0;
  w[1] = (3.0*s2*s - 6.0*s2 + 4.0)/6.0;
  w[2] = (-3.0*s2*s + 3.0*s2 + 3.0*s + 1.0)/6.0;
  w[3] = s2*s/6.0;
  dw[0] = -0.5*t*t;
  dw[1] = 0.5*(3.0*s2 - 4.0*s);
  dw[2] = 0.5*(-3.0*s2 + 2.0*s + 1.0);
  dw[3] = 0.5*s2;
}

//----------------------------------------------------------------------------------------
//! \fn LorentzFactor
//! \brief W = sqrt(1 + gamma^ij u_i u_j); also returns the raised components u^i

KOKKOS_INLINE_FUNCTION
Real LorentzFactor(const Real gi[3][3], const Real u[3], Real uup[3]) {
  Real usq = 0.0;
  for (int i=0; i<3; ++i) {
    uup[i] = gi[i][0]*u[0] + gi[i][1]*u[1] + gi[i][2]*u[2];
    usq += uup[i]*u[i];
  }
  return sqrt(1.0 + usq);
}

//----------------------------------------------------------------------------------------
//! \fn LorentzFactorEps
//! \brief W = sqrt(eps + gamma^ij u_i u_j): eps = 1 for a particle with rest mass,
//! eps = 0 for a null particle, for which W is the energy seen by the normal observer in
//! the units of u_i; also returns the raised components u^i

KOKKOS_INLINE_FUNCTION
Real LorentzFactorEps(const Real gi[3][3], const Real u[3], const Real eps,
                      Real uup[3]) {
  Real usq = 0.0;
  for (int i=0; i<3; ++i) {
    uup[i] = gi[i][0]*u[0] + gi[i][1]*u[1] + gi[i][2]*u[2];
    usq += uup[i]*u[i];
  }
  return sqrt(eps + usq);
}

//----------------------------------------------------------------------------------------
//! \fn PushMidpoint
//! \brief implicit midpoint update of (x^i, u_i) over one step dt,
//!   dx^i/dt = alpha gamma^ij u_j / W - beta^i,
//!   du_i/dt = -W d_i alpha + u_j d_i beta^j - (alpha/2W) u_j u_k d_i gamma^jk,
//! with the fields evaluated at the midpoint position and averaged between the two
//! stored time levels.  Solved by fixed-point iteration on the six endpoint values.
//!
//! The metric functor must provide
//!   bool IsStatic() const;
//!   void operator()(int level, const Real x[3], AdmPoint &p) const;  // level 0=t^n, 1
//! Returns the number of iterations used (negative if not converged within maxit).

template <class MetricT>
KOKKOS_INLINE_FUNCTION
int PushMidpoint(const MetricT &met, const Real dt, const Real tol, const int maxit,
                 Real x[3], Real u[3], const Real eps, Real &dtau) {
  const Real x0[3] = {x[0], x[1], x[2]};
  const Real u0[3] = {u[0], u[1], u[2]};
  AdmPoint p, q;
  Real gi[3][3], uup[3];

  // initial guess: explicit Euler in position with the old-level fields, momentum held
  met(0, x0, p);
  Inv3Sym(p.g, gi);
  Real W = LorentzFactorEps(gi, u0, eps, uup);
  Real x1[3], u1[3];
  for (int i=0; i<3; ++i) {
    x1[i] = x0[i] + dt*(p.alp*uup[i]/W - p.beta[i]);
    u1[i] = u0[i];
  }

  const bool is_static = met.IsStatic();
  int it = 0;
  bool converged = false;
  while (it < maxit) {
    ++it;
    Real xb[3], ub[3];
    for (int i=0; i<3; ++i) {
      xb[i] = 0.5*(x0[i] + x1[i]);
      ub[i] = 0.5*(u0[i] + u1[i]);
    }
    met(0, xb, p);
    if (!is_static) {
      met(1, xb, q);
      AverageAdm(p, q);
    }
    Inv3Sym(p.g, gi);
    W = LorentzFactorEps(gi, ub, eps, uup);

    Real err = 0.0;
    for (int i=0; i<3; ++i) {
      Real xn = x0[i] + dt*(p.alp*uup[i]/W - p.beta[i]);
      // -(alpha/2W) u_j u_k d_i gamma^jk = +(alpha/2W) u^l u^m d_i gamma_lm
      Real geo = 0.0;
      for (int l=0; l<3; ++l) {
        for (int m=0; m<3; ++m) {
          geo += uup[l]*uup[m]*p.dg[i][l][m];
        }
      }
      Real rhs = -W*p.dalp[i] + 0.5*p.alp*geo/W;
      for (int j=0; j<3; ++j) { rhs += ub[j]*p.dbeta[i][j]; }
      Real un = u0[i] + dt*rhs;
      err = fmax(err, fabs(xn - x1[i]));
      err = fmax(err, fabs(un - u1[i]));
      x1[i] = xn;
      u1[i] = un;
    }
    if (err < tol) { converged = true; break; }
  }

  for (int i=0; i<3; ++i) {
    x[i] = x1[i];
    u[i] = u1[i];
  }
  // proper time (affine parameter for eps = 0) elapsed over the step, with the lapse
  // and the Lorentz factor of the last midpoint evaluation: d tau = alpha dt / W
  dtau = dt*p.alp/W;
  return converged ? it : -it;
}

//----------------------------------------------------------------------------------------
//! \fn PushMidpoint
//! \brief the same for a particle with rest mass, without the proper time

template <class MetricT>
KOKKOS_INLINE_FUNCTION
int PushMidpoint(const MetricT &met, const Real dt, const Real tol, const int maxit,
                 Real x[3], Real u[3]) {
  Real dtau = 0.0;
  return PushMidpoint(met, dt, tol, maxit, x, u, 1.0, dtau);
}

//----------------------------------------------------------------------------------------
//! \fn PushBoris
//! \brief spacetime (DGREM) Boris update over one step dt.  Position is advanced in the
//! coordinate frame and momentum in the orthonormal frame of the normal observers with
//! spatial triad e^(m)_j = S[j][m] in the gauge selected by triad_kind.  In that frame
//! the geodesic equation reads
//!   du_(i)/dt^ = Et_(i) + eps_(ijk) u_(j) Bt_(k) / W,     dt^ = alpha dt,
//! with the gravito-electric and gravito-magnetic fields contracted with the momentum,
//!   Et_(i) = (1/alpha) e^k_(i) [ -W d_k alpha + u_l d_k beta^l
//!                                + beta^j u_(m) d_j e^(m)_k - u_(m) d_t e^(m)_k ],
//!   Bt_(k) = eps_(kij) e^p_(i) e^q_(j) u_(m) d_p e^(m)_q .
//! The fields are evaluated at the midpoint in position and time with the average of the
//! endpoint tetrad momenta, and the kick-rotate-kick sequence is iterated to convergence.
//! Returns the number of iterations used (negative if not converged within maxit).

template <class MetricT>
KOKKOS_INLINE_FUNCTION
int PushBoris(const MetricT &met, const int triad_kind, const Real dt, const Real tol,
              const int maxit, Real x[3], Real u[3]) {
  const Real x0[3] = {x[0], x[1], x[2]};
  AdmPoint p, q;
  Triad tr;

  // tetrad momentum at (t^n, x^n):  u_(m) = e^i_(m) u_i
  met(0, x0, p);
  BuildTriad(triad_kind, p.g, tr);
  Real uh0[3];
  for (int m=0; m<3; ++m) {
    uh0[m] = tr.Si[m][0]*u[0] + tr.Si[m][1]*u[1] + tr.Si[m][2]*u[2];
  }
  Real W = sqrt(1.0 + uh0[0]*uh0[0] + uh0[1]*uh0[1] + uh0[2]*uh0[2]);

  // initial guess: explicit Euler in position with the old-level fields, momentum held
  Real x1[3], uh1[3];
  for (int i=0; i<3; ++i) {
    Real uup = tr.Si[0][i]*uh0[0] + tr.Si[1][i]*uh0[1] + tr.Si[2][i]*uh0[2];
    x1[i] = x0[i] + dt*(p.alp*uup/W - p.beta[i]);
    uh1[i] = uh0[i];
  }

  const bool is_static = met.IsStatic();
  const Real idt = 1.0/dt;
  int it = 0;
  bool converged = false;
  while (it < maxit) {
    ++it;
    Real xb[3], ub[3];
    for (int i=0; i<3; ++i) {
      xb[i] = 0.5*(x0[i] + x1[i]);
      ub[i] = 0.5*(uh0[i] + uh1[i]);
    }
    W = sqrt(1.0 + ub[0]*ub[0] + ub[1]*ub[1] + ub[2]*ub[2]);

    // midpoint fields and time derivative of the spatial metric
    Real dtg[3][3];
    met(0, xb, p);
    if (!is_static) {
      met(1, xb, q);
      for (int i=0; i<3; ++i) {
        for (int j=0; j<3; ++j) { dtg[i][j] = (q.g[i][j] - p.g[i][j])*idt; }
      }
      AverageAdm(p, q);
    }
    BuildTriad(triad_kind, p.g, tr);

    // c[j][k] = u_(m) d_j e^(m)_k,   ct[k] = u_(m) d_t e^(m)_k
    Real c[3][3], ct[3], dS[3][3];
    for (int j=0; j<3; ++j) {
      TriadDeriv(triad_kind, tr, p.dg[j], dS);
      for (int k=0; k<3; ++k) {
        c[j][k] = dS[k][0]*ub[0] + dS[k][1]*ub[1] + dS[k][2]*ub[2];
      }
    }
    if (!is_static) {
      TriadDeriv(triad_kind, tr, dtg, dS);
      for (int k=0; k<3; ++k) {
        ct[k] = dS[k][0]*ub[0] + dS[k][1]*ub[1] + dS[k][2]*ub[2];
      }
    } else {
      ct[0] = 0.0; ct[1] = 0.0; ct[2] = 0.0;
    }

    // coordinate components of the midpoint momentum, u_l = e^(m)_l u_(m)
    Real ucov[3];
    for (int l=0; l<3; ++l) {
      ucov[l] = tr.S[l][0]*ub[0] + tr.S[l][1]*ub[1] + tr.S[l][2]*ub[2];
    }

    // alpha*Et_(i) = e^k_(i) Y[k]
    Real Y[3];
    for (int k=0; k<3; ++k) {
      Y[k] = -W*p.dalp[k] - ct[k];
      for (int l=0; l<3; ++l) {
        Y[k] += ucov[l]*p.dbeta[k][l] + p.beta[l]*c[l][k];
      }
    }
    Real aEt[3];
    for (int i=0; i<3; ++i) {
      aEt[i] = tr.Si[i][0]*Y[0] + tr.Si[i][1]*Y[1] + tr.Si[i][2]*Y[2];
    }

    // Bt_(k) = eps_(kij) T[i][j],  T[i][j] = e^p_(i) e^q_(j) c[p][q]
    Real T[3][3], cs[3][3];
    for (int pp=0; pp<3; ++pp) {
      for (int j=0; j<3; ++j) {
        cs[pp][j] = c[pp][0]*tr.Si[j][0] + c[pp][1]*tr.Si[j][1] + c[pp][2]*tr.Si[j][2];
      }
    }
    for (int i=0; i<3; ++i) {
      for (int j=0; j<3; ++j) {
        T[i][j] = tr.Si[i][0]*cs[0][j] + tr.Si[i][1]*cs[1][j] + tr.Si[i][2]*cs[2][j];
      }
    }
    Real Bt[3] = {T[1][2] - T[2][1], T[2][0] - T[0][2], T[0][1] - T[1][0]};

    // Boris kick-rotate-kick with dt^ = alpha dt
    const Real hk = 0.5*dt;                  // half kick: (dt^/2) Et = (dt/2) alpha Et
    const Real ft = 0.5*p.alp*dt/W;          // rotation vector t = (dt^/2W) Bt
    Real um[3], tv[3], sv[3], upr[3], upl[3], un[3];
    Real tsq = 0.0;
    for (int i=0; i<3; ++i) {
      um[i] = uh0[i] + hk*aEt[i];
      tv[i] = ft*Bt[i];
      tsq += tv[i]*tv[i];
    }
    for (int i=0; i<3; ++i) { sv[i] = 2.0*tv[i]/(1.0 + tsq); }
    upr[0] = um[0] + (um[1]*tv[2] - um[2]*tv[1]);
    upr[1] = um[1] + (um[2]*tv[0] - um[0]*tv[2]);
    upr[2] = um[2] + (um[0]*tv[1] - um[1]*tv[0]);
    upl[0] = um[0] + (upr[1]*sv[2] - upr[2]*sv[1]);
    upl[1] = um[1] + (upr[2]*sv[0] - upr[0]*sv[2]);
    upl[2] = um[2] + (upr[0]*sv[1] - upr[1]*sv[0]);
    for (int i=0; i<3; ++i) { un[i] = upl[i] + hk*aEt[i]; }

    // position with the same midpoint state: u^i = e^i_(m) u_(m)
    Real err = 0.0;
    for (int i=0; i<3; ++i) {
      Real uup = tr.Si[0][i]*ub[0] + tr.Si[1][i]*ub[1] + tr.Si[2][i]*ub[2];
      Real xn = x0[i] + dt*(p.alp*uup/W - p.beta[i]);
      err = fmax(err, fabs(xn - x1[i]));
      err = fmax(err, fabs(un[i] - uh1[i]));
      x1[i] = xn;
      uh1[i] = un[i];
    }
    if (err < tol) { converged = true; break; }
  }

  // endpoint coframe at (t^{n+1}, x^{n+1}):  u_i = e^(m)_i u_(m)
  met(is_static ? 0 : 1, x1, p);
  BuildTriad(triad_kind, p.g, tr);
  for (int i=0; i<3; ++i) {
    x[i] = x1[i];
    u[i] = tr.S[i][0]*uh1[0] + tr.S[i][1]*uh1[1] + tr.S[i][2]*uh1[2];
  }
  return converged ? it : -it;
}

} // namespace nrpic
#endif // PARTICLES_NRPIC_KERNELS_HPP_
