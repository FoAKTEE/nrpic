#ifndef PGEN_NRPIC_NRPIC_CLUMP_CURVATURE_HPP_
#define PGEN_NRPIC_NRPIC_CLUMP_CURVATURE_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_clump_curvature.hpp
//! \brief Extrinsic curvature of moving and rotating Gaussian matter clumps of the
//! problem generator nrpic_cf: the Bowen-York curvature smeared with the Gaussian.
//!
//! On a conformally flat slice, gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Abar_ij, K = 0,
//! the momentum constraint with particles reads (flat indices)
//!   d_j Abar_ij = 8 pi Stilde_i,  Stilde_i = psi^6 S_i = sum_p m_p u_(i,p) delta(x-x_p),
//! the coordinate density of the covariant particle momentum; psi drops out, the equation
//! is linear, and the curvatures of clumps and of Bowen-York punctures add.  For a
//! Gaussian component at x_c with width sigma, g = (2 pi sigma^2)^(-3/2)
//! exp(-r^2/(2 sigma^2)), t = r/(sqrt(2) sigma), n = (x - x_c)/r:
//!   momentum P, Stilde_i = P_i g:
//!     Abar_ij = 3 Q/(2 r^2) [P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n]
//!             + I4/(2 r^4)  [P_i n_j + P_j n_i + (delta_ij - 5 n_i n_j) P.n],
//!     Q  = 4 pi int_0^r g r'^2 dr' = erf(t) - (2/sqrt(pi)) t exp(-t^2),
//!     I4 = 4 pi int_0^r g r'^4 dr'
//!        = 3 sigma^2 [erf(t) - (2/sqrt(pi)) (t + 2 t^3/3) exp(-t^2)];
//!   spin S, Stilde_i = (S x (x - x_c))_i g/(2 sigma^2) (rigid rotation of the momentum
//!   density, angular momentum S):
//!     Abar_ij = 3 C/r^3 [(S x n)_i n_j + (S x n)_j n_i],   C = Q - (4 pi/3) r^3 g.
//! Far from the clump this is the Bowen-York curvature of P and S plus the regular term
//! 3 sigma^2/(2 r^4) [..]; at the centre it vanishes.  Derivation and symbolic check:
//! tracks/core/analysis/clump/derive_smeared_by.py; reference twin:
//! python/nrpic/smeared_bowen_york.py; interface tracks/core/interfaces/moving_clumps.md.
//!
//! The particles must carry that momentum density: P = sum_p m_p u_p of the clump's
//! particles, and for the constraint to hold in the continuum every particle the
//! momentum m_p u_(i,p) = [P_i + (S x (x_p - x_c))_i/(2 sigma^2)]/N at positions drawn
//! from g (problems/ic/make_ic.py, python/nrpic/clumps.py).  The Hamiltonian constraint
//! keeps the residual H = -psi^-12 Abar_ij Abar_ij, second order in P and S.
//!
//! Input, in <problem>, for a component c of type gaussian:
//!   comp<c>_p1, _p2, _p3    momentum of the clump (default 0)
//!   comp<c>_s1, _s2, _s3    spin of the clump (default 0)

#include <cmath>
#include <iostream>
#include <string>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"

namespace nrpic_clump {

constexpr int kClumpMax = 8;        // at most the number of components of nrpic_cf
constexpr Real kClumpSeries = 0.5;  // below this t the power series are used
constexpr int kClumpTerms = 14;     // their number of terms (remainder below 1e-20)

struct Clump {
  Real x[3];     // centre
  Real sigma;    // width
  Real p[3];     // momentum
  Real s[3];     // spin
};

struct ClumpSet {
  int n;         // Gaussian components with momentum or spin
  Clump c[kClumpMax];
};

//----------------------------------------------------------------------------------------
//! \fn void ClumpMoments
//! \brief enclosed fraction Q, enclosed second moment I4/sigma^2 and the spin function
//! C = Q - (4 pi/3) r^3 g of the unit Gaussian at t = r/(sqrt(2) sigma).  The closed
//! forms cancel for small t (Q like t^3, I4 and C like t^5): power series below t = 0.5,
//!   Q  = (4/sqrt(pi)) sum_k (-1)^k t^(2k+3)/(k! (2k+3)),
//!   I4 = (8 sigma^2/sqrt(pi)) sum_k (-1)^k t^(2k+5)/(k! (2k+5)),
//!   C  = (8/(3 sqrt(pi))) sum_{k>=1} (-1)^(k+1) k t^(2k+3)/(k! (2k+3)).

KOKKOS_INLINE_FUNCTION
void ClumpMoments(const Real t, Real &q, Real &i4, Real &cs) {
  const Real isqpi = 0.5641895835477563;   // 1/sqrt(pi)
  if (t < kClumpSeries) {
    const Real t2 = t*t;
    Real term = 1.0;                        // (-1)^k t^(2k)/k!
    q = 0.0; i4 = 0.0; cs = 0.0;
    for (int k=0; k<kClumpTerms; ++k) {
      q += term/static_cast<Real>(2*k + 3);
      i4 += term/static_cast<Real>(2*k + 5);
      cs -= static_cast<Real>(k)*term/static_cast<Real>(2*k + 3);
      term = -term*t2/static_cast<Real>(k + 1);
    }
    const Real t3 = t2*t;
    q *= 4.0*isqpi*t3;
    i4 *= 8.0*isqpi*t3*t2;
    cs *= (8.0/3.0)*isqpi*t3;
  } else {
    const Real e = exp(-t*t);
    const Real ef = erf(t);
    q = ef - 2.0*isqpi*t*e;
    i4 = 3.0*(ef - 2.0*isqpi*(t + (2.0/3.0)*t*t*t)*e);
    cs = q - (4.0/3.0)*isqpi*t*t*t*e;
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ClumpAddCurvature
//! \brief adds the conformal curvature Abar_ij of one Gaussian clump at (x,y,z) to
//! ab[6], ordered xx, xy, xz, yy, yz, zz

KOKKOS_INLINE_FUNCTION
void ClumpAddCurvature(const Clump &b, const Real x, const Real y, const Real z,
                       Real ab[6]) {
  const Real d[3] = {x - b.x[0], y - b.x[1], z - b.x[2]};
  const Real r = sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2]);
  // at the centre the curvature vanishes (linearly in r) and n is undefined
  if (!(r > 1.0e-12*b.sigma)) return;
  const Real n[3] = {d[0]/r, d[1]/r, d[2]/r};
  Real q, i4, cs;
  ClumpMoments(r/(sqrt(2.0)*b.sigma), q, i4, cs);
  const Real ir2 = 1.0/(r*r);
  const Real ca = 1.5*q*ir2;                           // Bowen-York of the enclosed P
  const Real cb = 0.5*b.sigma*b.sigma*i4*ir2*ir2;      // regular solution
  const Real cj = 3.0*cs*ir2/r;                        // spin
  const Real pn = b.p[0]*n[0] + b.p[1]*n[1] + b.p[2]*n[2];
  const Real sxn[3] = {b.s[1]*n[2] - b.s[2]*n[1], b.s[2]*n[0] - b.s[0]*n[2],
                       b.s[0]*n[1] - b.s[1]*n[0]};
  int k = 0;
  for (int i=0; i<3; ++i) {
    for (int j=i; j<3; ++j) {
      const Real dij = (i == j) ? 1.0 : 0.0;
      const Real pnn = b.p[i]*n[j] + b.p[j]*n[i];
      ab[k] += ca*(pnn - (dij - n[i]*n[j])*pn) + cb*(pnn + (dij - 5.0*n[i]*n[j])*pn)
             + cj*(sxn[i]*n[j] + sxn[j]*n[i]);
      ++k;
    }
  }
}

//----------------------------------------------------------------------------------------
//! \fn ClumpSet ClumpRead
//! \brief reads momentum and spin of the Gaussian components of <problem>; components
//! without them, or with all six values zero, are left out (no curvature is added)

inline ClumpSet ClumpRead(ParameterInput *pin, const int ncomp) {
  ClumpSet cl;
  cl.n = 0;
  for (int c=0; c<ncomp; ++c) {
    const std::string pre = "comp" + std::to_string(c) + "_";
    if (pin->GetString("problem", pre + "type").compare("gaussian") != 0) continue;
    if (pin->DoesParameterExist("problem", pre + "corr") ||
        pin->DoesParameterExist("problem", pre + "corr_file")) {
      std::cout << "### FATAL ERROR in nrpic_clump_curvature.hpp" << std::endl
                << "<problem> " << pre << "corr is defined for punctures only"
                << std::endl;
      std::exit(EXIT_FAILURE);
    }
    bool any = false;
    for (int a=0; a<3; ++a) {
      any = any || pin->DoesParameterExist("problem", pre + "p" + std::to_string(a+1))
                || pin->DoesParameterExist("problem", pre + "s" + std::to_string(a+1));
    }
    if (!any) continue;
    Clump b;
    Real sum = 0.0;
    for (int a=0; a<3; ++a) {
      const std::string xa = pre + "x" + std::to_string(a+1);
      const std::string pa = pre + "p" + std::to_string(a+1);
      const std::string sa = pre + "s" + std::to_string(a+1);
      b.x[a] = pin->DoesParameterExist("problem", xa) ? pin->GetReal("problem", xa) : 0.0;
      b.p[a] = pin->DoesParameterExist("problem", pa) ? pin->GetReal("problem", pa) : 0.0;
      b.s[a] = pin->DoesParameterExist("problem", sa) ? pin->GetReal("problem", sa) : 0.0;
      sum += std::fabs(b.p[a]) + std::fabs(b.s[a]);
    }
    b.sigma = pin->GetReal("problem", pre + "sigma");
    if (!(sum > 0.0)) continue;
    if (!(b.sigma > 0.0)) {
      std::cout << "### FATAL ERROR in nrpic_clump_curvature.hpp" << std::endl
                << "<problem> " << pre << "sigma must be positive" << std::endl;
      std::exit(EXIT_FAILURE);
    }
    cl.c[cl.n++] = b;
  }
  if (cl.n > 0 && global_variable::my_rank == 0) {
    std::cout << "NRPIC: smeared Bowen-York curvature on " << cl.n
              << " Gaussian component(s)" << std::endl;
  }
  return cl;
}

} // namespace nrpic_clump

#endif // PGEN_NRPIC_NRPIC_CLUMP_CURVATURE_HPP_
