#ifndef PARTICLES_NRPIC_METRICS_HPP_
#define PARTICLES_NRPIC_METRICS_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_metrics.hpp
//! \brief Analytic metric functors for the NRPIC pusher kernels (see nrpic_kernels.hpp
//! for the functor interface): Kerr in Cartesian Kerr-Schild, spherical Kerr-Schild and
//! Boyer-Lindquist coordinates, and a wrapper that samples any analytic metric on a
//! virtual uniform lattice of cell centres and reconstructs it with the same cubic
//! Hermite interpolation that is used on mesh data.
//!
//! Like nrpic_kernels.hpp this file does not depend on the rest of AthenaK.

#include "nrpic_kernels.hpp"

namespace nrpic {

//----------------------------------------------------------------------------------------
//! \struct KerrSchildCart
//! \brief Kerr metric in Cartesian Kerr-Schild coordinates (x,y,z),
//!   g = eta + 2 H l l,  H = M r^3/(r^4 + a^2 z^2),
//!   l_mu = (1, (r x + a y)/(r^2+a^2), (r y - a x)/(r^2+a^2), z/r).

struct KerrSchildCart {
  Real mass, spin;

  KOKKOS_INLINE_FUNCTION
  bool IsStatic() const { return true; }

  KOKKOS_INLINE_FUNCTION
  void operator()(const int, const Real x[3], AdmPoint &p) const {
    const Real a = spin;
    const Real a2 = a*a;
    const Real X = x[0], Y = x[1], Z = x[2];
    const Real b = X*X + Y*Y + Z*Z - a2;
    const Real r2 = 0.5*(b + sqrt(b*b + 4.0*a2*Z*Z));
    const Real r = sqrt(r2);
    const Real r3 = r2*r;

    // derivatives of r from r^4 - b r^2 - a^2 z^2 = 0
    const Real den = r*(2.0*r2 - b);
    const Real dr[3] = {X*r2/den, Y*r2/den, Z*(r2 + a2)/den};

    const Real q = r2*r2 + a2*Z*Z;
    const Real H = mass*r3/q;
    Real dH[3];
    for (int k=0; k<3; ++k) {
      Real dq = 4.0*r3*dr[k] + ((k == 2) ? 2.0*a2*Z : 0.0);
      dH[k] = mass*(3.0*r2*dr[k]*q - r3*dq)/(q*q);
    }

    const Real s = r2 + a2;
    const Real l[3] = {(r*X + a*Y)/s, (r*Y - a*X)/s, Z/r};
    Real dl[3][3];   // dl[k][i] = d_k l_i
    for (int k=0; k<3; ++k) {
      Real ds = 2.0*r*dr[k];
      Real n0 = dr[k]*X + ((k == 0) ? r : 0.0) + ((k == 1) ? a : 0.0);
      Real n1 = dr[k]*Y + ((k == 1) ? r : 0.0) - ((k == 0) ? a : 0.0);
      dl[k][0] = (n0*s - (r*X + a*Y)*ds)/(s*s);
      dl[k][1] = (n1*s - (r*Y - a*X)*ds)/(s*s);
      dl[k][2] = ((k == 2) ? 1.0/r : 0.0) - Z*dr[k]/r2;
    }

    const Real f = 1.0 + 2.0*H;
    p.alp = 1.0/sqrt(f);
    for (int i=0; i<3; ++i) {
      p.beta[i] = 2.0*H*l[i]/f;
      for (int j=0; j<3; ++j) {
        p.g[i][j] = ((i == j) ? 1.0 : 0.0) + 2.0*H*l[i]*l[j];
      }
    }
    for (int k=0; k<3; ++k) {
      p.dalp[k] = -dH[k]/(f*sqrt(f));
      for (int i=0; i<3; ++i) {
        p.dbeta[k][i] = 2.0*(dH[k]*l[i] + H*dl[k][i])/f - 4.0*H*l[i]*dH[k]/(f*f);
        for (int j=0; j<3; ++j) {
          p.dg[k][i][j] = 2.0*dH[k]*l[i]*l[j] + 2.0*H*(dl[k][i]*l[j] + l[i]*dl[k][j]);
        }
      }
    }
  }
};

//----------------------------------------------------------------------------------------
//! \struct KerrSchildSph
//! \brief Kerr metric in spherical Kerr-Schild (ingoing Kerr) coordinates (r,theta,phi),
//!   g = g_flat + (2 M r/Sigma) l l,  l = dt + dr - a sin^2(theta) dphi.

struct KerrSchildSph {
  Real mass, spin;

  KOKKOS_INLINE_FUNCTION
  bool IsStatic() const { return true; }

  KOKKOS_INLINE_FUNCTION
  void operator()(const int, const Real x[3], AdmPoint &p) const {
    const Real a = spin;
    const Real a2 = a*a;
    const Real r = x[0];
    const Real sn = sin(x[1]), cs = cos(x[1]);
    const Real s2 = sn*sn;
    const Real sig = r*r + a2*cs*cs;
    const Real z = 2.0*mass*r/sig;
    const Real zr = 2.0*mass*(sig - 2.0*r*r)/(sig*sig);
    const Real zt = 4.0*mass*r*a2*sn*cs/(sig*sig);
    const Real f = 1.0 + z;

    for (int i=0; i<3; ++i) {
      p.beta[i] = 0.0;
      p.dalp[i] = 0.0;
      for (int j=0; j<3; ++j) {
        p.g[i][j] = 0.0;
        p.dbeta[i][j] = 0.0;
        for (int k=0; k<3; ++k) { p.dg[i][j][k] = 0.0; }
      }
    }
    p.alp = 1.0/sqrt(f);
    p.dalp[0] = -0.5*zr/(f*sqrt(f));
    p.dalp[1] = -0.5*zt/(f*sqrt(f));
    p.beta[0] = z/f;
    p.dbeta[0][0] = zr/(f*f);
    p.dbeta[1][0] = zt/(f*f);

    p.g[0][0] = f;
    p.g[1][1] = sig;
    p.g[0][2] = -a*f*s2;
    p.g[2][0] = p.g[0][2];
    p.g[2][2] = s2*(r*r + a2) + z*a2*s2*s2;

    p.dg[0][0][0] = zr;
    p.dg[1][0][0] = zt;
    p.dg[0][1][1] = 2.0*r;
    p.dg[1][1][1] = -2.0*a2*sn*cs;
    p.dg[0][0][2] = -a*zr*s2;
    p.dg[1][0][2] = -a*zt*s2 - 2.0*a*f*sn*cs;
    p.dg[0][2][0] = p.dg[0][0][2];
    p.dg[1][2][0] = p.dg[1][0][2];
    p.dg[0][2][2] = 2.0*r*s2 + zr*a2*s2*s2;
    p.dg[1][2][2] = 2.0*sn*cs*(r*r + a2) + zt*a2*s2*s2 + 4.0*z*a2*s2*sn*cs;
  }
};

//----------------------------------------------------------------------------------------
//! \struct BoyerLindquist
//! \brief Kerr metric in Boyer-Lindquist coordinates (r,theta,phi)

struct BoyerLindquist {
  Real mass, spin;

  KOKKOS_INLINE_FUNCTION
  bool IsStatic() const { return true; }

  KOKKOS_INLINE_FUNCTION
  void operator()(const int, const Real x[3], AdmPoint &p) const {
    const Real a = spin;
    const Real a2 = a*a;
    const Real r = x[0];
    const Real sn = sin(x[1]), cs = cos(x[1]);
    const Real s2 = sn*sn;
    const Real sc = sn*cs;
    const Real del = r*r - 2.0*mass*r + a2;
    const Real sig = r*r + a2*cs*cs;
    const Real ra = r*r + a2;
    const Real A = ra*ra - a2*del*s2;
    const Real del_r = 2.0*r - 2.0*mass;
    const Real sig_r = 2.0*r;
    const Real sig_t = -2.0*a2*sc;
    const Real A_r = 4.0*r*ra - a2*del_r*s2;
    const Real A_t = -2.0*a2*del*sc;

    for (int i=0; i<3; ++i) {
      p.beta[i] = 0.0;
      p.dalp[i] = 0.0;
      for (int j=0; j<3; ++j) {
        p.g[i][j] = 0.0;
        p.dbeta[i][j] = 0.0;
        for (int k=0; k<3; ++k) { p.dg[i][j][k] = 0.0; }
      }
    }
    p.alp = sqrt(del*sig/A);
    p.dalp[0] = 0.5*p.alp*(del_r/del + sig_r/sig - A_r/A);
    p.dalp[1] = 0.5*p.alp*(sig_t/sig - A_t/A);
    p.beta[2] = -2.0*mass*a*r/A;
    p.dbeta[0][2] = -2.0*mass*a/A + 2.0*mass*a*r*A_r/(A*A);
    p.dbeta[1][2] = 2.0*mass*a*r*A_t/(A*A);

    p.g[0][0] = sig/del;
    p.g[1][1] = sig;
    p.g[2][2] = A*s2/sig;
    p.dg[0][0][0] = sig_r/del - sig*del_r/(del*del);
    p.dg[1][0][0] = sig_t/del;
    p.dg[0][1][1] = sig_r;
    p.dg[1][1][1] = sig_t;
    p.dg[0][2][2] = (A_r/sig - A*sig_r/(sig*sig))*s2;
    p.dg[1][2][2] = (A_t/sig - A*sig_t/(sig*sig))*s2 + 2.0*A*sc/sig;
  }
};

//----------------------------------------------------------------------------------------
//! \fn HermiteAccumulate
//! \brief adds the contribution of one lattice node with field values v to the
//! interpolated fields and derivatives.  w is the product of the three value weights and
//! dw[k] the product with the derivative weight in direction k (already divided by h_k).

KOKKOS_INLINE_FUNCTION
void HermiteZero(AdmPoint &p) {
  p.alp = 0.0;
  for (int i=0; i<3; ++i) {
    p.beta[i] = 0.0;
    p.dalp[i] = 0.0;
    for (int j=0; j<3; ++j) {
      p.g[i][j] = 0.0;
      p.dbeta[i][j] = 0.0;
      for (int k=0; k<3; ++k) { p.dg[i][j][k] = 0.0; }
    }
  }
}

KOKKOS_INLINE_FUNCTION
void HermiteAccumulate(const Real w, const Real dw[3], const Real alp,
                       const Real beta[3], const Real g[3][3], AdmPoint &p) {
  p.alp += w*alp;
  for (int i=0; i<3; ++i) {
    p.beta[i] += w*beta[i];
    for (int j=0; j<3; ++j) { p.g[i][j] += w*g[i][j]; }
  }
  for (int k=0; k<3; ++k) {
    p.dalp[k] += dw[k]*alp;
    for (int i=0; i<3; ++i) {
      p.dbeta[k][i] += dw[k]*beta[i];
      for (int j=0; j<3; ++j) { p.dg[k][i][j] += dw[k]*g[i][j]; }
    }
  }
}

//----------------------------------------------------------------------------------------
//! \struct LatticeMetric
//! \brief samples a static analytic metric at the cell centres x0 + (i+1/2) h of a
//! uniform lattice and reconstructs values and first derivatives with the tensor-product
//! cubic Hermite interpolation.  Equivalent to interpolating from a mesh that carries
//! the exact metric at its cell centres, without storing the mesh.

template <class BaseT>
struct LatticeMetric {
  BaseT base;
  Real x0[3];   // lattice origin (a cell face)
  Real h[3];    // lattice spacing

  KOKKOS_INLINE_FUNCTION
  bool IsStatic() const { return true; }

  KOKKOS_INLINE_FUNCTION
  void operator()(const int lev, const Real x[3], AdmPoint &p) const {
    int ib[3];
    Real w[3][4], dw[3][4];
    for (int d=0; d<3; ++d) {
      Real xi = (x[d] - x0[d])/h[d] - 0.5;
      Real fl = floor(xi);
      ib[d] = static_cast<int>(fl);
      HermiteWeights(xi - fl, w[d], dw[d]);
      for (int n=0; n<4; ++n) { dw[d][n] /= h[d]; }
    }
    HermiteZero(p);
    AdmPoint q;
    for (int c=0; c<4; ++c) {
      for (int b=0; b<4; ++b) {
        for (int a=0; a<4; ++a) {
          Real xn[3] = {x0[0] + (ib[0] + a - 1 + 0.5)*h[0],
                        x0[1] + (ib[1] + b - 1 + 0.5)*h[1],
                        x0[2] + (ib[2] + c - 1 + 0.5)*h[2]};
          base(lev, xn, q);
          Real ww = w[0][a]*w[1][b]*w[2][c];
          Real dww[3] = {dw[0][a]*w[1][b]*w[2][c],
                         w[0][a]*dw[1][b]*w[2][c],
                         w[0][a]*w[1][b]*dw[2][c]};
          HermiteAccumulate(ww, dww, q.alp, q.beta, q.g, p);
        }
      }
    }
  }
};

} // namespace nrpic
#endif // PARTICLES_NRPIC_METRICS_HPP_
