#ifndef PGEN_NRPIC_NRPIC_CLUMP_TABLE_HPP_
#define PGEN_NRPIC_NRPIC_CLUMP_TABLE_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_clump_table.hpp
//! \brief Table components of the problem generator nrpic_cf with a bulk momentum: an
//! equilibrium cluster (radial table of psi - 1 and the lapse) that moves.
//!
//! On a conformally flat slice, K_ij = psi^-2 Abar_ij, K = 0, the momentum constraint
//! with particles is d_j Abar_ij = 8 pi Stilde_i (nrpic_clump_curvature.hpp).  For any
//! polar l = 1 momentum density about a centre x_c,
//!   Stilde_i = V_i s_a(r) + n_i (V.n) s_b(r),   n = (x - x_c)/r,
//! the solution is the two lines of the Gaussian case with generalised moments,
//!   Abar_ij = 3 Q/(2 r^2) [P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n]
//!           + I4/(2 r^4)  [P_i n_j + P_j n_i + (delta_ij - 5 n_i n_j) P.n],
//!   Q(r)  = (4 pi/pmass) int_0^r (s_a + s_b/3) r'^2 dr'    (-> 1 outside the matter),
//!   I4(r) = (4 pi/pmass) int_0^r (s_a - s_b) r'^4 dr',     P = pmass V
//! (derivation: tracks/core/JOURNAL-clump2.md).  Q and I4 come from a "boost table"
//! written with the particles (python/nrpic/boosted_cluster.py: the static cluster on the
//! maximal slice of its boosted spacetime, Stilde_i = psi^6 (rho + P) alpha d_i T,
//! T = (V.n) F(r), with particles that carry exactly that momentum density).  The table
//! (format bst1) is plain text: header lines "# key = value" with
//!   format     bst1
//!   pmass      momentum per unit coordinate velocity far from the clump, P = pmass V
//!   ext_m, ext_kappa   beyond the last row the slice function is the vacuum form
//!              F = r + m + m^2/r + kappa/(r (r - m)), m = ext_m (half the mass)
//! and rows "r  Q/r^3  I4/r^5  ba  bb" on the uniform grid r_k = k dr from r = 0, which
//! must extend beyond the matter (Q and I4 are constant beyond the last row).
//!
//! The Hamiltonian constraint keeps a residual of second order in the momentum (the
//! curvature term -psi^-12 Abar_ij Abar_ij and the kinetic energy of the bulk motion).  A
//! correction of psi removes it for an isolated clump: a multipole table about the
//! direction of motion in the format of the puncture corrections (docs/FORMATS.md,
//! "mp1"), evaluated by nrpic_by::BYCorrection.
//!
//! With zero shift the coordinates do not follow the clump: its matter starts with the
//! coordinate velocity alpha^2 psi^-4 w.  comp<c>_boost_shift = true adds the shift of
//! the coordinates that move with the clump,
//!   beta^i = -(V^i ba(r) + n^i (V.n) bb(r)),   ba = 1 - alpha_0^2 psi_0^-4 F/r,
//!   bb = -alpha_0^2 psi_0^-4 (F' - F/r),
//! with alpha_0, psi_0 of the isolated clump; it falls off as 3 m V/r.
//!
//! Input, in <problem>, for a component c of type table (format 1):
//!   comp<c>_boost_file      boost table; without it nothing below is read
//!   comp<c>_p1, _p2, _p3    momentum of the clump, sum m u_i of its particles
//!                           (default 0; a clump with zero momentum gets nothing)
//!   comp<c>_corr            none (default) or table: correction of psi
//!   comp<c>_corr_file       table: file name
//!   comp<c>_corr_axis1..3   table: symmetry axis; default the axis of the file header,
//!                           else the direction of the momentum
//!   comp<c>_boost_shift     true: add the comoving shift (default false)

#include <cmath>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "pgen/nrpic/nrpic_bowen_york.hpp"

namespace nrpic_tclump {

constexpr int kTClumpMax = 8;   // at most the number of components of nrpic_cf

struct TClump {
  int icomp;             // index of the component
  Real x[3];             // centre
  Real p[3];             // momentum
  Real v[3];             // coordinate velocity far from the clump, p/pmass
  int ntab, off;         // rows; offset of the first of the four columns
  Real dr, rlast;        // spacing and last radius
  Real q_last, i4_last;  // Q and I4 beyond the last row
  Real ext_m, ext_kappa; // vacuum form of the slice function beyond the last row
  int shift;             // 1: the comoving shift is added
};

struct TClumpSet {
  int n;                 // table components with a boost table and momentum
  int ncorr;             // corrections of psi among them
  bool shift;            // any comoving shift
  TClump c[kTClumpMax];
  nrpic_by::BYPuncture corr[kTClumpMax];
};

//----------------------------------------------------------------------------------------
//! \fn void TClumpAddCurvature
//! \brief adds the conformal curvature Abar_ij of one moving table clump at (x,y,z) to
//! ab[6], ordered xx, xy, xz, yy, yz, zz

KOKKOS_INLINE_FUNCTION
void TClumpAddCurvature(const TClump &b, const DvceArray1D<Real> &tab, const Real x,
                        const Real y, const Real z, Real ab[6]) {
  const Real d[3] = {x - b.x[0], y - b.x[1], z - b.x[2]};
  const Real r = sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2]);
  // at the centre the curvature vanishes (linearly in r) and n is undefined
  if (!(r > 1.0e-12*b.dr)) return;
  const Real n[3] = {d[0]/r, d[1]/r, d[2]/r};
  Real ca, cb;           // 3 Q/(2 r^2) and I4/(2 r^4)
  if (r >= b.rlast) {
    const Real ir2 = 1.0/(r*r);
    ca = 1.5*b.q_last*ir2;
    cb = 0.5*b.i4_last*ir2*ir2;
  } else {
    ca = 1.5*r*nrpic_by::BYCubic(tab, b.off, b.ntab, b.dr, r);
    cb = 0.5*r*nrpic_by::BYCubic(tab, b.off + b.ntab, b.ntab, b.dr, r);
  }
  const Real pn = b.p[0]*n[0] + b.p[1]*n[1] + b.p[2]*n[2];
  int k = 0;
  for (int i=0; i<3; ++i) {
    for (int j=i; j<3; ++j) {
      const Real dij = (i == j) ? 1.0 : 0.0;
      const Real pnn = b.p[i]*n[j] + b.p[j]*n[i];
      ab[k] += ca*(pnn - (dij - n[i]*n[j])*pn) + cb*(pnn + (dij - 5.0*n[i]*n[j])*pn);
      ++k;
    }
  }
}

//----------------------------------------------------------------------------------------
//! \fn void TClumpAddShift
//! \brief adds the comoving shift beta^i of one moving table clump at (x,y,z) to bt[3]

KOKKOS_INLINE_FUNCTION
void TClumpAddShift(const TClump &b, const DvceArray1D<Real> &tab, const Real x,
                    const Real y, const Real z, Real bt[3]) {
  if (b.shift == 0) return;
  const Real d[3] = {x - b.x[0], y - b.x[1], z - b.x[2]};
  const Real r = sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2]);
  const Real ir = (r > 1.0e-12*b.dr) ? 1.0/r : 0.0;
  const Real n[3] = {d[0]*ir, d[1]*ir, d[2]*ir};
  Real ba, bb;
  if (r >= b.rlast) {
    // vacuum: alpha_0 psi_0 = 1 - m/r, psi_0 = 1 + m/r, F = r + m + m^2/r + kappa F_2
    const Real mr = b.ext_m*ir;
    const Real rm = r - b.ext_m;
    const Real psi2 = (1.0 + mr)*(1.0 + mr);
    const Real c2 = (1.0 - mr)*(1.0 - mr)/(psi2*psi2*psi2);
    const Real wa = 1.0 + mr + mr*mr + b.ext_kappa*ir*ir/rm;
    const Real df = 1.0 - mr*mr - b.ext_kappa*(2.0*r - b.ext_m)*ir*ir/(rm*rm);
    ba = 1.0 - c2*wa;
    bb = -c2*(df - wa);
  } else {
    ba = nrpic_by::BYCubic(tab, b.off + 2*b.ntab, b.ntab, b.dr, r);
    bb = nrpic_by::BYCubic(tab, b.off + 3*b.ntab, b.ntab, b.dr, r);
  }
  const Real vn = b.v[0]*n[0] + b.v[1]*n[1] + b.v[2]*n[2];
  for (int a=0; a<3; ++a) {
    bt[a] -= b.v[a]*ba + n[a]*vn*bb;
  }
}

inline void TClumpFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_clump_table.hpp" << std::endl << msg
            << std::endl;
  std::exit(EXIT_FAILURE);
}

//----------------------------------------------------------------------------------------
//! \fn void TClumpReadTable
//! \brief reads a boost table (format bst1) into b and appends its four columns
//! (Q/r^3, I4/r^5, ba, bb) to tab_h; returns pmass

inline Real TClumpReadTable(const std::string &fname, TClump &b,
                            std::vector<Real> &tab_h) {
  std::ifstream fin(fname);
  if (!fin.is_open()) TClumpFatal("cannot open boost table " + fname);
  std::vector<Real> r;
  std::vector<std::vector<Real>> col(4);
  std::string line, format;
  Real pmass = 0.0;
  bool has_m = false, has_k = false;
  while (std::getline(fin, line)) {
    if (line.empty()) continue;
    if (line[0] == '#') {
      const std::size_t eq = line.find('=');
      if (eq == std::string::npos) continue;
      std::istringstream ks(line.substr(1, eq - 1));
      std::string key;
      ks >> key;
      std::istringstream vs(line.substr(eq + 1));
      if (key.compare("format") == 0) {
        vs >> format;
      } else if (key.compare("pmass") == 0) {
        vs >> pmass;
      } else if (key.compare("ext_m") == 0) {
        if (vs >> b.ext_m) has_m = true;
      } else if (key.compare("ext_kappa") == 0) {
        if (vs >> b.ext_kappa) has_k = true;
      }
      continue;
    }
    std::istringstream iss(line);
    Real v[5];
    if (!(iss >> v[0] >> v[1] >> v[2] >> v[3] >> v[4])) {
      TClumpFatal("boost table " + fname + ": a row needs five values");
    }
    r.push_back(v[0]);
    for (int q=0; q<4; ++q) col[q].push_back(v[q+1]);
  }
  if (format.compare("bst1") != 0) {
    TClumpFatal("boost table " + fname + ": header line '# format = bst1' is required");
  }
  if (!(pmass > 0.0) || !has_m || !has_k) {
    TClumpFatal("boost table " + fname + ": header needs pmass > 0, ext_m, ext_kappa");
  }
  const int n = static_cast<int>(r.size());
  if (n < 8) TClumpFatal("boost table " + fname + " has fewer than 8 rows");
  const Real dr = r[1] - r[0];
  if (std::fabs(r[0]) > 1.0e-12*dr || std::fabs(r[n-1] - (n-1)*dr) > 1.0e-8*r[n-1]) {
    TClumpFatal("boost table " + fname + " is not uniform starting at r = 0");
  }
  if (!(r[n-1] > 2.0*b.ext_m)) {
    TClumpFatal("boost table " + fname + " must extend beyond the matter (r > 2 ext_m)");
  }
  b.ntab = n;
  b.off = static_cast<int>(tab_h.size());
  b.dr = dr;
  b.rlast = r[n-1];
  b.q_last = col[0][n-1]*r[n-1]*r[n-1]*r[n-1];
  const Real r2 = r[n-1]*r[n-1];
  b.i4_last = col[1][n-1]*r2*r2*r[n-1];
  for (int q=0; q<4; ++q) {
    tab_h.insert(tab_h.end(), col[q].begin(), col[q].end());
  }
  return pmass;
}

//----------------------------------------------------------------------------------------
//! \fn TClumpSet TClumpRead
//! \brief reads boost table, momentum, correction and shift option of the table
//! components of <problem>; the boost tables are appended to tab_h, the correction
//! tables to corr_h.  A component without comp<c>_boost_file, or with zero momentum, is
//! left out.

inline TClumpSet TClumpRead(ParameterInput *pin, const int ncomp,
                            std::vector<Real> &tab_h, std::vector<Real> &corr_h) {
  TClumpSet ts;
  ts.n = 0;
  ts.ncorr = 0;
  ts.shift = false;
  for (int c=0; c<ncomp; ++c) {
    const std::string pre = "comp" + std::to_string(c) + "_";
    if (!pin->DoesParameterExist("problem", pre + "boost_file")) continue;
    if (pin->GetString("problem", pre + "type").compare("table") != 0) {
      TClumpFatal("<problem> " + pre + "boost_file needs " + pre + "type = table");
    }
    TClump b;
    b.icomp = c;
    Real sum = 0.0;
    for (int a=0; a<3; ++a) {
      b.x[a] = nrpic_by::BYGetReal(pin, pre + "x" + std::to_string(a+1), 0.0);
      b.p[a] = nrpic_by::BYGetReal(pin, pre + "p" + std::to_string(a+1), 0.0);
      sum += std::fabs(b.p[a]);
    }
    if (!(sum > 0.0)) continue;
    b.ext_m = 0.0;
    b.ext_kappa = 0.0;
    const Real pmass =
        TClumpReadTable(pin->GetString("problem", pre + "boost_file"), b, tab_h);
    for (int a=0; a<3; ++a) {
      b.v[a] = b.p[a]/pmass;
    }
    b.shift = 0;
    if (pin->DoesParameterExist("problem", pre + "boost_shift") &&
        pin->GetBoolean("problem", pre + "boost_shift")) {
      b.shift = 1;
      ts.shift = true;
    }
    ts.c[ts.n++] = b;

    // correction of psi: a multipole table about the direction of motion
    std::string corr = "none";
    if (pin->DoesParameterExist("problem", pre + "corr")) {
      corr = pin->GetString("problem", pre + "corr");
    }
    if (corr.compare("table") == 0) {
      nrpic_by::BYPuncture &u = ts.corr[ts.ncorr];
      for (int a=0; a<3; ++a) {
        u.x[a] = b.x[a];
        u.p[a] = b.p[a];
        u.s[a] = 0.0;
        u.axis[a] = 0.0;
      }
      u.m = 0.0;
      u.lam = 1.0;
      u.corr = nrpic_by::kBYCorrTable;
      u.ncol = 0; u.ntab = 0; u.off = 0; u.lmax = 0; u.dr = 1.0; u.rlast = 0.0;
      for (int q=0; q<nrpic_by::kBYMaxCol; ++q) {
        u.l[q] = 0;
        u.tail[q] = 1.0;
      }
      const bool has_axis = nrpic_by::BYReadTable(
          pin->GetString("problem", pre + "corr_file"), u, corr_h);
      if (pin->DoesParameterExist("problem", pre + "corr_axis1")) {
        u.axis[0] = pin->GetReal("problem", pre + "corr_axis1");
        u.axis[1] = nrpic_by::BYGetReal(pin, pre + "corr_axis2", 0.0);
        u.axis[2] = nrpic_by::BYGetReal(pin, pre + "corr_axis3", 0.0);
      } else if (!has_axis) {
        for (int a=0; a<3; ++a) {
          u.axis[a] = b.p[a];
        }
      }
      const Real a2 = u.axis[0]*u.axis[0] + u.axis[1]*u.axis[1] + u.axis[2]*u.axis[2];
      if (!(a2 > 0.0)) TClumpFatal("<problem> " + pre + "corr = table needs an axis");
      for (int a=0; a<3; ++a) {
        u.axis[a] /= std::sqrt(a2);
      }
      ++ts.ncorr;
    } else if (corr.compare("none") != 0) {
      TClumpFatal("<problem> " + pre + "corr = '" + corr
                  + "' not recognized for a table component (none, table)");
    }
  }
  if (ts.n > 0 && global_variable::my_rank == 0) {
    std::cout << "NRPIC: curvature of " << ts.n << " moving table component(s), "
              << ts.ncorr << " correction(s) of psi, comoving shift "
              << (ts.shift ? "on" : "off") << std::endl;
  }
  return ts;
}

} // namespace nrpic_tclump

#endif // PGEN_NRPIC_NRPIC_CLUMP_TABLE_HPP_
