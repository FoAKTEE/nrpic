#ifndef PGEN_NRPIC_NRPIC_BOWEN_YORK_HPP_
#define PGEN_NRPIC_NRPIC_BOWEN_YORK_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_bowen_york.hpp
//! \brief Bowen-York extrinsic curvature of the puncture components of the problem
//! generator nrpic_cf, and regular corrections of their conformal factor.
//!
//! On a conformally flat slice, gamma_ij = psi^4 delta_ij, a puncture at x_c with linear
//! momentum P and spin S contributes the conformal, traceless curvature (Brandt &
//! Bruegmann, arXiv:gr-qc/9703066, Eq. 5; flat indices)
//!   Abar_ij = 3/(2 r^2) [P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n]
//!           + 3/r^3 [(S x n)_i n_j + (S x n)_j n_i],     n = (x - x_c)/r,
//! and K_ij = psi^-2 sum_c Abar_ij,c.  The sum is divergence free, so the momentum
//! constraint holds for any number of punctures (in vacuum).  The Hamiltonian constraint
//! requires psi = psi_BL + u with
//!   lap u = -(1/8) Abar_ij Abar^ij (psi_BL + u)^-7,     u -> 0 at infinity;
//! with the Brill-Lindquist factor alone its residual is H = -psi^-12 Abar_ij Abar^ij.
//! A regular correction u_c of each puncture may be added to psi:
//!   approx  closed form to second order in P and S of an isolated puncture (Lousto &
//!           Zlochower, arXiv:0711.1165, Eqs. 1 to 6): monopole and quadrupole about P,
//!           the same about S, and the cross term proportional to (P x S).n
//!   table   multipoles u(r, mu) = sum_l u_l(r) P_l(mu) about one axis, read from a file
//!           (docs/FORMATS.md; python/nrpic/bowen_york.py writes the solution of the full
//!           equation for an isolated puncture with P and S along one axis)
//! Either removes the residual of an isolated puncture to the stated order.  Near a
//! puncture c the other punctures add the nearly constant amount
//!   Lambda_c - 1 = sum_{j != c} m_j/(2 d_cj)
//! to psi, which changes the source by the factor ((Lambda_c + m_c/2r)/(1 + m_c/2r))^-7;
//! the sum of isolated corrections then overshoots and can leave a larger residual than
//! no correction at all (tracks/core/interfaces/multi_puncture.md).  The local equation
//! with that background is the isolated one with rescaled parameters, so that
//!   u_c = Lambda_c u_isolated(m_c/Lambda_c, P_c/Lambda_c^4, S_c/Lambda_c^4),
//! which approx uses unless <problem> corr_background = false.  A table is used as it
//! is.  The cross terms of the curvatures of different punctures remain.
//!
//! Input, in <problem>, for a component c of type puncture:
//!   comp<c>_p1, _p2, _p3    linear momentum (default 0)
//!   comp<c>_s1, _s2, _s3    spin (default 0)
//!   comp<c>_corr            none (default), approx, table
//!   comp<c>_corr_file       table: file name
//!   comp<c>_corr_axis1..3   table: symmetry axis; default the axis of the file header,
//!                           else the direction of P, else that of S
//!   corr_background         approx: rescale with the background of the other
//!                           punctures (default true)

#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"

namespace nrpic_by {

constexpr int kBYMaxPunc = 8;   // at most the number of components of nrpic_cf
constexpr int kBYMaxCol = 6;    // multipole columns of a correction table
constexpr int kBYMaxL = 12;     // highest multipole order of a correction table

enum BYCorr {kBYCorrNone = 0, kBYCorrApprox = 1, kBYCorrTable = 2};

struct BYPuncture {
  Real x[3];             // position
  Real m;                // bare mass
  Real p[3];             // linear momentum
  Real s[3];             // spin
  int corr;              // correction of the conformal factor
  Real lam;              // approx: background conformal factor of the other punctures
  Real axis[3];          // table: symmetry axis (unit vector)
  int ncol, ntab, off;   // table: multipole columns, rows, offset of the first column
  int lmax;              // table: highest multipole order
  int l[kBYMaxCol];      // table: multipole order of each column
  Real tail[kBYMaxCol];  // table: decay exponent of each column beyond the last row
  Real dr, rlast;        // table: spacing and last radius
};

struct BYSet {
  int n;                 // punctures with momentum, spin or a correction
  bool curv;             // any momentum or spin
  BYPuncture punc[kBYMaxPunc];
};

//----------------------------------------------------------------------------------------
//! \fn void BYAddCurvature
//! \brief adds the conformal Bowen-York curvature Abar_ij of one puncture at (x,y,z) to
//! ab[6], ordered xx, xy, xz, yy, yz, zz

KOKKOS_INLINE_FUNCTION
void BYAddCurvature(const BYPuncture &b, const Real x, const Real y, const Real z,
                    Real ab[6]) {
  const Real d[3] = {x - b.x[0], y - b.x[1], z - b.x[2]};
  const Real r = fmax(sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2]), 1.0e-12);
  const Real n[3] = {d[0]/r, d[1]/r, d[2]/r};
  const Real pn = b.p[0]*n[0] + b.p[1]*n[1] + b.p[2]*n[2];
  const Real sxn[3] = {b.s[1]*n[2] - b.s[2]*n[1], b.s[2]*n[0] - b.s[0]*n[2],
                       b.s[0]*n[1] - b.s[1]*n[0]};
  const Real cp = 1.5/(r*r), cs = 3.0/(r*r*r);
  int q = 0;
  for (int i=0; i<3; ++i) {
    for (int j=i; j<3; ++j) {
      const Real dij = (i == j) ? 1.0 : 0.0;
      ab[q] += cp*(b.p[i]*n[j] + b.p[j]*n[i] - (dij - n[i]*n[j])*pn)
             + cs*(sxn[i]*n[j] + sxn[j]*n[i]);
      ++q;
    }
  }
}

//----------------------------------------------------------------------------------------
//! \fn Real BYApproxU2P
//! \brief quadrupole radial function of the second-order correction of a boosted
//! puncture (arXiv:0711.1165, Eq. 4b), R = 2r/m; power series below R = 0.15, where the
//! closed form cancels

KOKKOS_INLINE_FUNCTION
Real BYApproxU2P(const Real R) {
  if (R < 0.15) {
    // coefficients of R^5 .. R^17 (the series starts with R^2/400)
    const Real c[13] = {-1.0/32.0, 7.0/48.0, -21.0/50.0, 21.0/22.0, -15.0/8.0,
                        693.0/208.0, -11.0/2.0, 429.0/50.0, -819.0/64.0, 5005.0/272.0,
                        -77.0/3.0, 663.0/19.0, -4641.0/100.0};
    Real s = 0.0;
    for (int k=12; k>=0; --k) {
      s = s*R + c[k];
    }
    return R*R*(0.0025 + R*R*R*s);
  }
  const Real l1 = 1.0/(1.0 + R);
  const Real l2 = l1*l1, l3 = l2*l1, l4 = l2*l2, l5 = l4*l1;
  return (15.0*l1 + 132.0*l2 + 53.0*l3 + 96.0*l4 + 82.0*l5 + 84.0*l5/R
          + 84.0*log(l1)/(R*R))/(80.0*R);
}

//----------------------------------------------------------------------------------------
//! \fn Real BYApprox
//! \brief second-order correction of an isolated puncture with momentum and spin
//! (arXiv:0711.1165, Eqs. 1 to 6) at displacement d, distance r, with mass m/Lambda and
//! momenta P/Lambda^4, S/Lambda^4, times Lambda (Lambda = b.lam, 1 without background)

KOKKOS_INLINE_FUNCTION
Real BYApprox(const BYPuncture &b, const Real d[3], const Real r) {
  const Real mt = b.m/b.lam;
  const Real lam4 = b.lam*b.lam*b.lam*b.lam;
  const Real R = 2.0*r/mt;
  const Real l1 = 1.0/(1.0 + R);
  const Real l2 = l1*l1, l3 = l2*l1, l4 = l2*l2, l5 = l4*l1;
  const Real pf = 2.0/(lam4*mt);
  const Real cp[3] = {pf*b.p[0], pf*b.p[1], pf*b.p[2]};
  const Real jf = 4.0/(lam4*mt*mt);
  const Real cj[3] = {jf*b.s[0], jf*b.s[1], jf*b.s[2]};
  const Real p2 = cp[0]*cp[0] + cp[1]*cp[1] + cp[2]*cp[2];
  const Real j2 = cj[0]*cj[0] + cj[1]*cj[1] + cj[2]*cj[2];
  Real u = 0.0;
  if (p2 > 0.0) {
    const Real mu = (r > 0.0) ? (d[0]*cp[0] + d[1]*cp[1] + d[2]*cp[2])/(sqrt(p2)*r) : 0.0;
    const Real u0 = (5.0/32.0)*(l1 - 2.0*l2 + 2.0*l3 - l4 + 0.2*l5);
    u += p2*(u0 + BYApproxU2P(R)*0.5*(3.0*mu*mu - 1.0));
  }
  if (j2 > 0.0) {
    const Real mu = (r > 0.0) ? (d[0]*cj[0] + d[1]*cj[1] + d[2]*cj[2])/(sqrt(j2)*r) : 0.0;
    const Real u0 = (l1 + l2 + l3 - 4.0*l4 + 2.0*l5)/40.0;
    u += j2*(u0 - 0.05*l5*R*R*0.5*(3.0*mu*mu - 1.0));
  }
  if (p2 > 0.0 && j2 > 0.0) {
    const Real c[3] = {cp[1]*cj[2] - cp[2]*cj[1], cp[2]*cj[0] - cp[0]*cj[2],
                       cp[0]*cj[1] - cp[1]*cj[0]};
    u += (2.0/mt)*(c[0]*d[0] + c[1]*d[1] + c[2]*d[2])*(1.0 + 5.0*R + 10.0*R*R)*l5/80.0;
  }
  return b.lam*u;
}

//! cubic (four-point Lagrange) interpolation in a uniform table starting at r = 0
KOKKOS_INLINE_FUNCTION
Real BYCubic(const DvceArray1D<Real> &tab, const int off, const int n, const Real dr,
             const Real r) {
  Real xi = r/dr;
  int i = static_cast<int>(floor(xi));
  i = (i < 1) ? 1 : i;
  i = (i > n-3) ? n-3 : i;
  const Real s = xi - static_cast<Real>(i);
  const Real wm = -s*(s - 1.0)*(s - 2.0)/6.0;
  const Real w0 = (s + 1.0)*(s - 1.0)*(s - 2.0)/2.0;
  const Real w1 = -(s + 1.0)*s*(s - 2.0)/2.0;
  const Real w2 = (s + 1.0)*s*(s - 1.0)/6.0;
  return wm*tab(off+i-1) + w0*tab(off+i) + w1*tab(off+i+1) + w2*tab(off+i+2);
}

//----------------------------------------------------------------------------------------
//! \fn Real BYCorrection
//! \brief regular correction u_c of the conformal factor of one puncture at (x,y,z)

KOKKOS_INLINE_FUNCTION
Real BYCorrection(const BYPuncture &b, const DvceArray1D<Real> &tab, const Real x,
                  const Real y, const Real z) {
  if (b.corr == kBYCorrNone) return 0.0;
  const Real d[3] = {x - b.x[0], y - b.x[1], z - b.x[2]};
  const Real r = sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2]);
  if (b.corr == kBYCorrApprox) return BYApprox(b, d, r);
  // multipole table about the axis
  const Real mu = (r > 0.0) ? (d[0]*b.axis[0] + d[1]*b.axis[1] + d[2]*b.axis[2])/r : 0.0;
  Real pl[kBYMaxL+1];
  pl[0] = 1.0;
  pl[1] = mu;
  for (int l=2; l<=b.lmax; ++l) {
    pl[l] = ((2*l - 1)*mu*pl[l-1] - (l - 1)*pl[l-2])/static_cast<Real>(l);
  }
  Real u = 0.0;
  for (int q=0; q<b.ncol; ++q) {
    const int o = b.off + q*b.ntab;
    Real ul;
    if (r >= b.rlast) {
      ul = tab(o + b.ntab - 1)*pow(b.rlast/r, b.tail[q]);
    } else {
      ul = BYCubic(tab, o, b.ntab, b.dr, r);
    }
    u += ul*pl[b.l[q]];
  }
  return u;
}

inline void BYFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_bowen_york.hpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

//! value of an optional real parameter of <problem>, without adding it to the input
inline Real BYGetReal(ParameterInput *pin, const std::string &name, const Real def) {
  return pin->DoesParameterExist("problem", name) ? pin->GetReal("problem", name) : def;
}

//----------------------------------------------------------------------------------------
//! \fn void BYReadTable
//! \brief reads a puncture-correction table (docs/FORMATS.md) into b and appends its
//! columns to tab_h; returns true if the header gives the symmetry axis

inline bool BYReadTable(const std::string &fname, BYPuncture &b,
                        std::vector<Real> &tab_h) {
  std::ifstream fin(fname);
  if (!fin.is_open()) BYFatal("cannot open correction table " + fname);
  std::vector<int> lv;
  std::vector<Real> tl, r;
  std::vector<std::vector<Real>> col;
  bool has_axis = false;
  std::string line;
  while (std::getline(fin, line)) {
    if (line.empty()) continue;
    if (line[0] == '#') {
      const std::size_t eq = line.find('=');
      if (eq == std::string::npos) continue;
      std::istringstream ks(line.substr(1, eq - 1));
      std::string key;
      ks >> key;
      std::istringstream vs(line.substr(eq + 1));
      if (key.compare("l") == 0) {
        int v;
        while (vs >> v) lv.push_back(v);
      } else if (key.compare("tail") == 0) {
        Real v;
        while (vs >> v) tl.push_back(v);
      } else if (key.compare("axis") == 0) {
        if (vs >> b.axis[0] >> b.axis[1] >> b.axis[2]) has_axis = true;
      }
      continue;
    }
    if (lv.empty()) BYFatal("correction table " + fname + " has no header line '# l ='");
    if (col.empty()) col.resize(lv.size());
    std::istringstream iss(line);
    Real rr;
    if (!(iss >> rr)) continue;
    std::vector<Real> row(lv.size());
    bool ok = true;
    for (std::size_t q=0; q<lv.size(); ++q) {
      if (!(iss >> row[q])) ok = false;
    }
    if (!ok) BYFatal("correction table " + fname + ": a row has too few columns");
    r.push_back(rr);
    for (std::size_t q=0; q<lv.size(); ++q) col[q].push_back(row[q]);
  }
  const int ncol = static_cast<int>(lv.size());
  const int n = static_cast<int>(r.size());
  if (ncol < 1 || ncol > kBYMaxCol) {
    BYFatal("correction table " + fname + " must have between 1 and 6 multipoles");
  }
  if (n < 8) BYFatal("correction table " + fname + " has fewer than 8 rows");
  const Real dr = r[1] - r[0];
  if (std::fabs(r[0]) > 1.0e-12*dr || std::fabs(r[n-1] - (n-1)*dr) > 1.0e-8*r[n-1]) {
    BYFatal("correction table " + fname + " is not uniform starting at r = 0");
  }
  if (!tl.empty() && static_cast<int>(tl.size()) != ncol) {
    BYFatal("correction table " + fname + ": '# tail =' needs one exponent per column");
  }
  b.ncol = ncol;
  b.ntab = n;
  b.off = static_cast<int>(tab_h.size());
  b.dr = dr;
  b.rlast = r[n-1];
  b.lmax = 0;
  for (int q=0; q<ncol; ++q) {
    if (lv[q] < 0 || lv[q] > kBYMaxL) {
      BYFatal("correction table " + fname + ": multipole order outside 0..12");
    }
    b.l[q] = lv[q];
    b.lmax = (lv[q] > b.lmax) ? lv[q] : b.lmax;
    // without a stated exponent: exterior harmonic
    b.tail[q] = tl.empty() ? static_cast<Real>(lv[q] + 1) : tl[q];
    tab_h.insert(tab_h.end(), col[q].begin(), col[q].end());
  }
  return has_axis;
}

//----------------------------------------------------------------------------------------
//! \fn BYSet BYRead
//! \brief reads momentum, spin and correction of the puncture components of <problem>;
//! correction tables are appended to tab_h

inline BYSet BYRead(ParameterInput *pin, const int ncomp, std::vector<Real> &tab_h) {
  BYSet by;
  by.n = 0;
  by.curv = false;
  const char *keys[8] = {"p1", "p2", "p3", "s1", "s2", "s3", "corr", "corr_file"};
  for (int c=0; c<ncomp; ++c) {
    const std::string pre = "comp" + std::to_string(c) + "_";
    bool any = false;
    for (int k=0; k<8; ++k) {
      any = any || pin->DoesParameterExist("problem", pre + keys[k]);
    }
    if (!any) continue;
    // momentum and spin of a Gaussian component: nrpic_clump_curvature.hpp
    if (pin->GetString("problem", pre + "type").compare("gaussian") == 0) continue;
    if (pin->GetString("problem", pre + "type").compare("puncture") != 0) {
      BYFatal("<problem> " + pre + "p1..3, s1..3 and corr need " + pre
              + "type = puncture (p1..3, s1..3 also gaussian)");
    }
    if (by.n >= kBYMaxPunc) BYFatal("too many punctures with momentum or spin");
    BYPuncture &b = by.punc[by.n];
    b.x[0] = BYGetReal(pin, pre + "x1", 0.0);
    b.x[1] = BYGetReal(pin, pre + "x2", 0.0);
    b.x[2] = BYGetReal(pin, pre + "x3", 0.0);
    b.m = pin->GetReal("problem", pre + "mass");
    for (int a=0; a<3; ++a) {
      b.p[a] = BYGetReal(pin, pre + "p" + std::to_string(a+1), 0.0);
      b.s[a] = BYGetReal(pin, pre + "s" + std::to_string(a+1), 0.0);
      b.axis[a] = 0.0;
    }
    b.lam = 1.0;
    b.ncol = 0; b.ntab = 0; b.off = 0; b.lmax = 0; b.dr = 1.0; b.rlast = 0.0;
    for (int q=0; q<kBYMaxCol; ++q) {
      b.l[q] = 0;
      b.tail[q] = 1.0;
    }
    const Real p2 = b.p[0]*b.p[0] + b.p[1]*b.p[1] + b.p[2]*b.p[2];
    const Real s2 = b.s[0]*b.s[0] + b.s[1]*b.s[1] + b.s[2]*b.s[2];
    if (p2 > 0.0 || s2 > 0.0) by.curv = true;

    std::string corr = "none";
    if (pin->DoesParameterExist("problem", pre + "corr")) {
      corr = pin->GetString("problem", pre + "corr");
    }
    if (corr.compare("none") == 0) {
      b.corr = kBYCorrNone;
    } else if (corr.compare("approx") == 0) {
      b.corr = kBYCorrApprox;
      if (!(b.m > 0.0)) BYFatal("<problem> " + pre + "corr = approx needs mass > 0");
      // background conformal factor of the other punctures at this one
      const bool bg = pin->DoesParameterExist("problem", "corr_background") ?
                      pin->GetBoolean("problem", "corr_background") : true;
      for (int o=0; o<ncomp && bg; ++o) {
        const std::string po = "comp" + std::to_string(o) + "_";
        if (o == c || pin->GetString("problem", po + "type").compare("puncture") != 0) {
          continue;
        }
        const Real dx = BYGetReal(pin, po + "x1", 0.0) - b.x[0];
        const Real dy = BYGetReal(pin, po + "x2", 0.0) - b.x[1];
        const Real dz = BYGetReal(pin, po + "x3", 0.0) - b.x[2];
        const Real dist = std::sqrt(dx*dx + dy*dy + dz*dz);
        if (!(dist > 0.0)) BYFatal("two punctures at the same position");
        b.lam += 0.5*pin->GetReal("problem", po + "mass")/dist;
      }
    } else if (corr.compare("table") == 0) {
      b.corr = kBYCorrTable;
      const bool has_axis =
          BYReadTable(pin->GetString("problem", pre + "corr_file"), b, tab_h);
      if (pin->DoesParameterExist("problem", pre + "corr_axis1")) {
        b.axis[0] = pin->GetReal("problem", pre + "corr_axis1");
        b.axis[1] = BYGetReal(pin, pre + "corr_axis2", 0.0);
        b.axis[2] = BYGetReal(pin, pre + "corr_axis3", 0.0);
      } else if (!has_axis) {
        for (int a=0; a<3; ++a) {
          b.axis[a] = (p2 > 0.0) ? b.p[a] : b.s[a];
        }
      }
      const Real a2 = b.axis[0]*b.axis[0] + b.axis[1]*b.axis[1] + b.axis[2]*b.axis[2];
      if (!(a2 > 0.0)) {
        BYFatal("<problem> " + pre + "corr = table needs an axis: momentum, spin, "
                + pre + "corr_axis1..3 or '# axis =' in the file");
      }
      for (int a=0; a<3; ++a) {
        b.axis[a] /= std::sqrt(a2);
      }
    } else {
      BYFatal("<problem> " + pre + "corr = '" + corr + "' not recognized");
    }
    ++by.n;
  }
  if (by.n > 0 && global_variable::my_rank == 0) {
    std::cout << "NRPIC: Bowen-York curvature or correction on " << by.n
              << " puncture(s)" << std::endl;
  }
  return by;
}

//! correction tables on the device
inline DvceArray1D<Real> BYDeviceTable(const std::vector<Real> &tab_h) {
  const int ntot = static_cast<int>(tab_h.size());
  DvceArray1D<Real> tab("by_tab", (ntot > 0) ? ntot : 1);
  if (ntot > 0) {
    auto th = Kokkos::create_mirror_view(tab);
    for (int n=0; n<ntot; ++n) {
      th(n) = tab_h[n];
    }
    Kokkos::deep_copy(tab, th);
  }
  return tab;
}

} // namespace nrpic_by

#endif // PGEN_NRPIC_NRPIC_BOWEN_YORK_HPP_
