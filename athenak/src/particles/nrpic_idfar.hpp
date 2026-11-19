#ifndef PARTICLES_NRPIC_IDFAR_HPP_
#define PARTICLES_NRPIC_IDFAR_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_idfar.hpp
//! \brief Far field of the initial-data solver of the NRPIC particle module
//! (nrpic_idsolve.cpp): exterior multipole expansion of the solution of a Poisson
//! equation, lap phi = s, about a centre,
//!   phi(x) = -(1/4 pi) sum_{l=0}^{lmax} M_l(n)/r^(l+1),
//!   M_l(n) = int s(x') r'^l P_l(n.n') d^3x'           (Legendre polynomials P_l),
//! from the raw moments T_abc = int s x'^a y'^b z'^c d^3x' of degree a + b + c <= 4.
//! r^l M_l(n) is a homogeneous polynomial of degree l in x whose coefficients are sums of
//! the moments of degree l: with P_l(t) = sum_k c_lk t^(l-2k),
//!   r^l M_l(n) = sum_k c_lk r^(2k) sum_{|al| = l-2k} (l-2k)!/al! x^al
//!                sum_{|be| = k} k!/be! T_(al+2be).
//! The solver uses it for the conformal factor (s the right side of the Hamiltonian
//! constraint) and, through W_i = (7/8) V_i - (1/8)(d_i U + x_j d_i V_j) with
//! lap V_i = s_i and lap U = -x_j s_j, for the vector potential of the momentum
//! constraint, whose far field depends on the direction already at order 1/r
//! (Bowen-York: W_i = -(7 P_i + n_i n.P)/(4 r)).
//! Design and tests: tracks/core/interfaces/id_solver2.md.

#include <cmath>

#include "athena.hpp"

namespace particles {

constexpr int kIdFarLmax = 4;       // highest multipole order
constexpr int kIdFarN = 35;         // monomials of degree <= 4 in three variables
typedef array_sum::array_type<Real, kIdFarN> IdFarSum;   // moments as a reduction type

//! position of the monomial x^a y^b z^c in the list of moments (degree by degree)
KOKKOS_INLINE_FUNCTION
int IdFarIndex(const int a, const int b, const int c) {
  const int d = a + b + c;
  return d*(d + 1)*(d + 2)/6 + (d - a)*(d - a + 1)/2 + c;
}

//! adds w x^a y^b z^c for every monomial of degree <= lmax to t
KOKKOS_INLINE_FUNCTION
void IdFarAccumulate(Real t[kIdFarN], const Real w, const Real x, const Real y,
                     const Real z, const int lmax) {
  Real px[kIdFarLmax+1], py[kIdFarLmax+1], pz[kIdFarLmax+1];
  px[0] = 1.0; py[0] = 1.0; pz[0] = 1.0;
  for (int n=1; n<=lmax; ++n) {
    px[n] = px[n-1]*x; py[n] = py[n-1]*y; pz[n] = pz[n-1]*z;
  }
  for (int d=0; d<=lmax; ++d) {
    for (int a=d; a>=0; --a) {
      for (int b=d-a; b>=0; --b) {
        const int c = d - a - b;
        t[IdFarIndex(a, b, c)] += w*px[a]*py[b]*pz[c];
      }
    }
  }
}

//! coefficients c of the homogeneous polynomials H_l(x) = r^l M_l(n) = sum_{|ga| = l}
//! c_ga x^ga from the moments t (host; once per set of moments): with r^(2k) written as
//! sum_{|de| = k} k!/de! x^(2 de), the term of P_l in t^(l-2k) adds
//! c_lk (l-2k)!/al! k!/de! sum_{|be| = k} k!/be! T_(al+2be) to the coefficient of
//! x^(al+2de)
inline void IdFarCoefficients(const Real t[kIdFarN], const int lmax, Real c[kIdFarN]) {
  const Real fact[kIdFarLmax+1] = {1.0, 1.0, 2.0, 6.0, 24.0};
  // Legendre polynomials, coefficient of t^(l-2k)
  const Real leg[kIdFarLmax+1][3] = {{1.0, 0.0, 0.0}, {1.0, 0.0, 0.0}, {1.5, -0.5, 0.0},
                                     {2.5, -1.5, 0.0}, {4.375, -3.75, 0.375}};
  for (int q=0; q<kIdFarN; ++q) { c[q] = 0.0; }
  for (int l=0; l<=lmax; ++l) {
    for (int k=0; 2*k<=l; ++k) {
      const int p = l - 2*k;
      for (int a=p; a>=0; --a) {
        for (int b=p-a; b>=0; --b) {
          const int e = p - a - b;
          Real tr = 0.0;
          for (int i=k; i>=0; --i) {
            for (int j=k-i; j>=0; --j) {
              const int m = k - i - j;
              tr += fact[k]/(fact[i]*fact[j]*fact[m])
                    *t[IdFarIndex(a + 2*i, b + 2*j, e + 2*m)];
            }
          }
          const Real w = leg[l][k]*fact[p]/(fact[a]*fact[b]*fact[e])*tr;
          for (int i=k; i>=0; --i) {
            for (int j=k-i; j>=0; --j) {
              const int m = k - i - j;
              c[IdFarIndex(a + 2*i, b + 2*j, e + 2*m)] +=
                  w*fact[k]/(fact[i]*fact[j]*fact[m]);
            }
          }
        }
      }
    }
  }
}

//! the expansion phi = -(1/4 pi) sum_l H_l(x)/r^(2l+1) and its gradient at the point
//! (x, y, z) relative to the centre, from the coefficients of IdFarCoefficients
KOKKOS_INLINE_FUNCTION
void IdFarEval(const Real c[kIdFarN], const int lmax, const Real x, const Real y,
               const Real z, Real &phi, Real g[3]) {
  phi = 0.0;
  g[0] = 0.0; g[1] = 0.0; g[2] = 0.0;
  const Real r2 = x*x + y*y + z*z;
  if (!(r2 > 0.0)) return;
  Real px[kIdFarLmax+1], py[kIdFarLmax+1], pz[kIdFarLmax+1];
  px[0] = 1.0; py[0] = 1.0; pz[0] = 1.0;
  for (int q=1; q<=lmax; ++q) {
    px[q] = px[q-1]*x; py[q] = py[q-1]*y; pz[q] = pz[q-1]*z;
  }
  const Real ir2 = 1.0/r2;
  Real rp = sqrt(ir2);             // 1/r^(2l+1)
  int q = 0;
  for (int l=0; l<=lmax; ++l) {
    Real h = 0.0, hx = 0.0, hy = 0.0, hz = 0.0;
    for (int a=l; a>=0; --a) {
      for (int b=l-a; b>=0; --b) {
        const int e = l - a - b;
        const Real cc = c[q++];
        h += cc*px[a]*py[b]*pz[e];
        if (a > 0) { hx += cc*a*px[a-1]*py[b]*pz[e]; }
        if (b > 0) { hy += cc*b*px[a]*py[b-1]*pz[e]; }
        if (e > 0) { hz += cc*e*px[a]*py[b]*pz[e-1]; }
      }
    }
    const Real w = (2.0*l + 1.0)*h*ir2;
    phi += h*rp;
    g[0] += (hx - w*x)*rp;
    g[1] += (hy - w*y)*rp;
    g[2] += (hz - w*z)*rp;
    rp *= ir2;
  }
  const Real f = -1.0/(4.0*M_PI);
  phi *= f;
  g[0] *= f; g[1] *= f; g[2] *= f;
}

//! far field of the vector potential, W_i = (7/8) V_i - (1/8)(d_i U + x_j d_i V_j), from
//! the coefficients cv[0..2] of the expansion of V_i (source s_i) and cu of U (source
//! -x_j s_j), all about the same centre
KOKKOS_INLINE_FUNCTION
void IdFarVector(const Real cv[3][kIdFarN], const Real cu[kIdFarN], const int lmax,
                 const Real x, const Real y, const Real z, Real w[3]) {
  const Real xx[3] = {x, y, z};
  Real v[3], gv[3][3], u, gu[3];
  for (int a=0; a<3; ++a) {
    IdFarEval(cv[a], lmax, x, y, z, v[a], gv[a]);
  }
  IdFarEval(cu, lmax, x, y, z, u, gu);
  for (int i=0; i<3; ++i) {
    w[i] = 0.875*v[i]
         - 0.125*(gu[i] + xx[0]*gv[0][i] + xx[1]*gv[1][i] + xx[2]*gv[2][i]);
  }
}

} // namespace particles

namespace Kokkos {
template<>
struct reduction_identity<particles::IdFarSum> {
  KOKKOS_FORCEINLINE_FUNCTION static particles::IdFarSum sum() {
    return particles::IdFarSum();
  }
};
} // namespace Kokkos

#endif // PARTICLES_NRPIC_IDFAR_HPP_
