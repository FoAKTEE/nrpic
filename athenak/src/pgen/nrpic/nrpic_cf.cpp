//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_cf.cpp
//! \brief Problem generator for conformally flat initial data,
//!   gamma_ij = psi^4 delta_ij,
//! with the conformal factor given as a superposition psi = 1 + sum_c u_c(x - x_c).
//! Without a table of format 2 the data are time-symmetric, K_ij = 0, beta^i = 0:
//! each component u_c solves the flat-space Poisson equation for a conformal source, so
//! the superposition solves the Hamiltonian constraint for the matter density
//! rho = rho~ psi^-5 with rho~ the sum of the conformal sources.  Components:
//!   table     spherical profile u(r) read from a radial table (docs/FORMATS.md),
//!             continued as u = M/(2r) outside the table.  A table of format 2
//!             (header line "# format = 2", columns rbar u KL KT alpha betar) carries
//!             in addition the extrinsic curvature
//!               K_ij = psi^4 [KT delta_ij + (KL - KT) n_i n_j],  n^i = (x - x_c)^i/rbar,
//!             (psi the full conformal factor), a lapse and a shift beta^i = betar n^i;
//!             its generator answers for the constraints.  One such component per run.
//!   puncture  u = m/(2r)                      (Brill-Lindquist black hole)
//!   gaussian  u = (m/2) erf(r/(sqrt(2) sigma))/r
//!   spheroid  u = -Phi_N of a homogeneous prolate spheroid of Newtonian mass M/2 with
//!             equatorial and polar semi-axes a < b, the polar axis along z
//! The initial lapse is selected by <problem> lapse:
//!   one           alpha = 1
//!   table         alpha(r) from the table of component lapse_comp, Schwarzschild
//!                 isotropic lapse (1 - M/2r)/(1 + M/2r) outside the table
//!   isotropic     alpha = (2 - psi)/psi
//!   precollapsed  alpha = psi^-2
//! (table of format 2: its alpha column, the last value outside the table), and with a
//! table of format 2 the initial shift by <problem> shift:
//!   zero          beta^i = 0
//!   table         beta^i = betar n^i from the table of component shift_comp
//! The matter is carried by the particles of the nrpic module, which reads them from
//! <particles> particle_file.
//! Punctures may carry linear momentum and spin (Bowen-York curvature, K_ij = psi^-2
//! Abar_ij) and a regular correction of their conformal factor: nrpic_bowen_york.hpp.
//! Gaussian components may carry linear momentum and spin (the Bowen-York curvature
//! smeared with the Gaussian, which solves the momentum constraint for a clump whose
//! particles carry that momentum density): nrpic_clump_curvature.hpp.
//! Table components (format 1) may carry a linear momentum: curvature from a boost
//! table, a correction of psi and a comoving shift (an equilibrium cluster that moves):
//! nrpic_clump_table.hpp.
//! <problem> puncture_setup = true adds a tracker, an initial refined region and a
//! horizon finder for every puncture: nrpic_puncture_setup.hpp.

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
#include "mesh/mesh.hpp"
#include "coordinates/adm.hpp"
#include "coordinates/cell_locations.hpp"
#include "z4c/z4c.hpp"
#include "z4c/z4c_amr.hpp"
#include "particles/particles.hpp"
#include "pgen/pgen.hpp"
#include "pgen/nrpic/nrpic_bowen_york.hpp"
#include "pgen/nrpic/nrpic_clump_curvature.hpp"
#include "pgen/nrpic/nrpic_clump_table.hpp"

namespace {

enum CFType {kCFTable = 0, kCFPuncture = 1, kCFGaussian = 2, kCFSpheroid = 3,
             kCFTable2 = 4};
enum CFLapse {kLapseOne = 0, kLapseTable = 1, kLapseIsotropic = 2, kLapsePre = 3,
              kLapseTable2 = 4};
enum CFExterior {kExtPG = 0, kExtZero = 1};
constexpr int kCFMaxComp = 8;
constexpr int kCFMaxBreak = 4;   // breaks of a table of format 2

struct CFComp {
  int type;
  Real x[3];      // centre
  Real mass;      // puncture: bare mass; gaussian: conformal mass; spheroid: ADM mass
  Real sigma;     // gaussian width
  Real a, b;      // spheroid semi-axes (equatorial, polar)
  int ntab, off;  // table: number of rows and offset into the concatenated tables
  Real dr;        // table spacing
  Real rlast, ulast;
  // table of format 2: pieces between the breaks (rows klo..khi), continuation beyond
  // the last row, and the last-row values of KL, KT, alpha, betar
  int npiece;
  int klo[kCFMaxBreak+1], khi[kCFMaxBreak+1];
  Real brk[kCFMaxBreak];
  int ext;
  Real kl_last, kt_last, a_last, b_last;
};

//! rows i-1..i+2 and weights of the cubic interpolation in a table of format 2
struct CFStencil {
  int i;
  Real w[4];
};

//! cubic (four-point Lagrange) interpolation in a uniform table starting at r = 0
KOKKOS_INLINE_FUNCTION
Real CFCubic(const DvceArray1D<Real> &tab, const int off, const int n, const Real dr,
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

//! cubic (four-point Lagrange) interpolation at r < rlast in a table of format 2: the
//! four rows are taken from the piece between breaks that contains r (a row belongs to
//! the piece outside a break when its radius is not smaller than the break), so that a
//! discontinuity at a break is never interpolated across
KOKKOS_INLINE_FUNCTION
CFStencil CFPieceStencil(const CFComp &c, const Real r) {
  int p = 0;
  for (int b=0; b<c.npiece-1; ++b) {
    if (r >= c.brk[b]) p = b + 1;
  }
  CFStencil st;
  const Real xi = r/c.dr;
  int i = static_cast<int>(floor(xi));
  i = (i < c.klo[p]+1) ? c.klo[p]+1 : i;
  i = (i > c.khi[p]-2) ? c.khi[p]-2 : i;
  const Real s = xi - static_cast<Real>(i);
  st.i = c.off + i;
  st.w[0] = -s*(s - 1.0)*(s - 2.0)/6.0;
  st.w[1] = (s + 1.0)*(s - 1.0)*(s - 2.0)/2.0;
  st.w[2] = -(s + 1.0)*s*(s - 2.0)/2.0;
  st.w[3] = (s + 1.0)*s*(s - 1.0)/6.0;
  return st;
}

//! conformal-factor excess u_c of one component at (x,y,z)
KOKKOS_INLINE_FUNCTION
Real CFExcess(const CFComp &c, const DvceArray1D<Real> &utab, const Real x, const Real y,
              const Real z) {
  const Real dx = x - c.x[0], dy = y - c.x[1], dz = z - c.x[2];
  const Real r = sqrt(dx*dx + dy*dy + dz*dz);
  if (c.type == kCFTable) {
    if (r >= c.rlast) return c.ulast*c.rlast/r;
    return CFCubic(utab, c.off, c.ntab, c.dr, r);
  } else if (c.type == kCFPuncture) {
    return 0.5*c.mass/fmax(r, 1.0e-12);
  } else if (c.type == kCFGaussian) {
    const Real q = r/(sqrt(2.0)*c.sigma);
    if (q < 1.0e-6) return c.mass/(sqrt(2.0*M_PI)*c.sigma);
    return 0.5*c.mass*erf(q)/r;
  } else if (c.type == kCFTable2) {
    if (r >= c.rlast) return c.ulast*c.rlast/r;
    const CFStencil st = CFPieceStencil(c, r);
    return st.w[0]*utab(st.i-1) + st.w[1]*utab(st.i) + st.w[2]*utab(st.i+1)
           + st.w[3]*utab(st.i+2);
  } else {
    const Real a2 = c.a*c.a, b2 = c.b*c.b;
    const Real f = sqrt(b2 - a2);
    const Real R2 = dx*dx + dy*dy, z2 = dz*dz;
    Real lam = 0.0;
    if (R2/a2 + z2/b2 > 1.0) {
      const Real B = a2 + b2 - R2 - z2;
      const Real C = a2*b2 - R2*b2 - z2*a2;
      lam = 0.5*(-B + sqrt(B*B - 4.0*C));
    }
    const Real s = sqrt(b2 + lam);
    const Real lg = log((s + f)/(s - f));
    const Real i0 = lg/f;
    const Real i1 = s/(f*f*(a2 + lam)) - 0.5*lg/(f*f*f);
    const Real i3 = lg/(f*f*f) - 2.0/(f*f*s);
    return 0.375*c.mass*(i0 - R2*i1 - z2*i3);
  }
}

void NrpicCFRefinement(MeshBlockPack *pmbp) {
  pmbp->pz4c->pamr->Refine(pmbp);
}

void CFFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_cf.cpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

std::string CFTrim(const std::string &str) {
  const size_t b = str.find_first_not_of(" \t\r");
  if (b == std::string::npos) return "";
  const size_t e = str.find_last_not_of(" \t\r");
  return str.substr(b, e - b + 1);
}

//! reads a table of format 2 (tracks/core/interfaces/spherical_id_format2.md): header
//! lines "# key = value" with the keys format, columns, exterior and optionally breaks,
//! then rows "rbar u KL KT alpha betar" on the uniform grid rbar_k = k drbar.  Fills the
//! geometry of the component and returns the columns; the other header lines go to
//! the log.
void CFReadTable2(const std::string &fname, CFComp &c, std::vector<Real> &u,
                  std::vector<Real> &a, std::vector<Real> &kl, std::vector<Real> &kt,
                  std::vector<Real> &br) {
  std::ifstream fin(fname);
  if (!fin.is_open()) CFFatal("cannot open radial table " + fname);
  std::vector<Real> r, brk;
  std::string line, columns, exterior;
  const bool log = (global_variable::my_rank == 0);
  while (std::getline(fin, line)) {
    if (line.empty()) continue;
    if (line[0] == '#') {
      const size_t eq = line.find('=');
      if (eq == std::string::npos) continue;
      const std::string key = CFTrim(line.substr(1, eq - 1));
      const std::string val = CFTrim(line.substr(eq + 1));
      if (key.compare("format") == 0) {
        if (val.compare("2") != 0) CFFatal(fname + ": format = " + val + " not known");
      } else if (key.compare("columns") == 0) {
        columns = val;
      } else if (key.compare("exterior") == 0) {
        exterior = val;
      } else if (key.compare("breaks") == 0) {
        std::istringstream iss(val);
        Real b;
        while (iss >> b) { brk.push_back(b); }
      } else if (log) {
        std::cout << "NRPIC: " << fname << ": " << key << " = " << val << std::endl;
      }
      continue;
    }
    std::istringstream iss(line);
    Real rr, uu, ll, tt, aa, bb;
    if (iss >> rr >> uu >> ll >> tt >> aa >> bb) {
      r.push_back(rr); u.push_back(uu); kl.push_back(ll); kt.push_back(tt);
      a.push_back(aa); br.push_back(bb);
    } else {
      CFFatal(fname + ": a row of a table of format 2 needs six values");
    }
  }
  {
    std::istringstream iss(columns);
    const char *want[6] = {"rbar", "u", "KL", "KT", "alpha", "betar"};
    std::string tok;
    int n = 0;
    while (iss >> tok) {
      if (n >= 6 || tok.compare(want[n]) != 0) { n = -1; break; }
      ++n;
    }
    if (n != 6) {
      CFFatal(fname + ": header line '# columns = rbar u KL KT alpha betar' is required");
    }
  }
  if (exterior.compare("pg") == 0) {
    c.ext = kExtPG;
  } else if (exterior.compare("zero") == 0) {
    c.ext = kExtZero;
  } else {
    CFFatal(fname + ": header line '# exterior = pg | zero' is required");
  }
  const int n = static_cast<int>(r.size());
  if (n < 8) CFFatal("radial table " + fname + " has fewer than 8 rows");
  const Real dr = r[1] - r[0];
  if (std::fabs(r[0]) > 1.0e-12*dr || std::fabs(r[n-1] - (n-1)*dr) > 1.0e-8*r[n-1]) {
    CFFatal("radial table " + fname + " is not uniform starting at r = 0");
  }
  // pieces between the breaks
  const int nb = static_cast<int>(brk.size());
  if (nb > kCFMaxBreak) CFFatal(fname + ": more than 4 breaks");
  c.npiece = nb + 1;
  int first = 0;
  for (int b=0; b<nb; ++b) {
    if (!(brk[b] > 0.0) || !(brk[b] < r[n-1]) || (b > 0 && !(brk[b] > brk[b-1]))) {
      CFFatal(fname + ": breaks must increase and lie inside the table");
    }
    int k = first;
    while (k < n && r[k] < brk[b]) { ++k; }      // first row not below the break
    if (std::fabs(r[k] - brk[b]) < 1.0e-6*dr || std::fabs(r[k-1] - brk[b]) < 1.0e-6*dr) {
      CFFatal(fname + ": a break coincides with a row; place it between two rows");
    }
    c.brk[b] = brk[b];
    c.klo[b] = first;
    c.khi[b] = k - 1;
    first = k;
  }
  c.klo[nb] = first;
  c.khi[nb] = n - 1;
  for (int p=0; p<c.npiece; ++p) {
    if (c.khi[p] - c.klo[p] + 1 < 4) {
      CFFatal(fname + ": every piece between breaks needs at least 4 rows");
    }
  }
  c.ntab = n;
  c.dr = dr;
  c.rlast = r[n-1];
  c.ulast = u[n-1];
  c.mass = 2.0*r[n-1]*u[n-1];
  c.kl_last = kl[n-1];
  c.kt_last = kt[n-1];
  c.a_last = a[n-1];
  c.b_last = br[n-1];
  if (log) {
    std::cout << "NRPIC: " << fname << ": format 2, " << n << " rows, exterior = "
              << exterior << ", " << nb << " break(s)" << std::endl;
  }
}

//! true if the file carries the header line "# format = 2"
bool CFIsFormat2(const std::string &fname) {
  std::ifstream fin(fname);
  if (!fin.is_open()) CFFatal("cannot open radial table " + fname);
  std::string line;
  while (std::getline(fin, line)) {
    if (line.empty() || line[0] != '#') continue;
    const size_t eq = line.find('=');
    if (eq == std::string::npos) continue;
    if (CFTrim(line.substr(1, eq - 1)).compare("format") == 0 &&
        CFTrim(line.substr(eq + 1)).compare("2") == 0) {
      return true;
    }
  }
  return false;
}

//! Extrinsic curvature of the component kc (a table of format 2) on all cells, added to
//! the curvature already set (zero, or the Bowen-York curvature of the punctures),
//!   K_ij += psi^4 [KT delta_ij + (KL - KT) n_i n_j],
//! with psi^4 as set before from all components, and on request the lapse and the shift
//! beta^i = betar n^i of that table.  Beyond the last row: exterior = pg continues KL
//! and KT as rbar^(-3/2) and betar as rbar^(-1/2) through the last row (exact for a
//! Painleve-Gullstrand exterior with psi = 1), exterior = zero sets them to zero; the
//! lapse keeps its last value.  xtab holds KL, KT, betar (first index).
void CFSetExtrinsic(MeshBlockPack *pmbp, const CFComp &kc, const DvceArray1D<Real> &atab,
                    const DvceArray2D<Real> &xtab, const bool set_lapse,
                    const bool set_shift) {
  auto &indcs = pmbp->pmesh->mb_indcs;
  auto &size = pmbp->pmb->mb_size;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ng = indcs.ng;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int n1 = nx1 + 2*ng, n2 = nx2 + 2*ng, n3 = nx3 + 2*ng;
  const int nmb = pmbp->nmb_thispack;
  auto &adm = pmbp->padm->adm;
  const CFComp c = kc;
  par_for("nrpic_cf_k", DevExeSpace(), 0, nmb-1, 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    const Real x = CellCenterX(i-is, nx1, size.d_view(m).x1min, size.d_view(m).x1max);
    const Real y = CellCenterX(j-js, nx2, size.d_view(m).x2min, size.d_view(m).x2max);
    const Real z = CellCenterX(k-ks, nx3, size.d_view(m).x3min, size.d_view(m).x3max);
    const Real d[3] = {x - c.x[0], y - c.x[1], z - c.x[2]};
    const Real r = sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2]);
    Real kl, kt, alp, br;
    if (r >= c.rlast) {
      alp = c.a_last;
      if (c.ext == kExtPG) {
        const Real q = c.rlast/r;
        const Real q32 = q*sqrt(q);
        kl = c.kl_last*q32;
        kt = c.kt_last*q32;
        br = c.b_last*sqrt(q);
      } else {
        kl = 0.0; kt = 0.0; br = 0.0;
      }
    } else {
      const CFStencil st = CFPieceStencil(c, r);
      kl = 0.0; kt = 0.0; alp = 0.0; br = 0.0;
      for (int q=0; q<4; ++q) {
        kl  += st.w[q]*xtab(0,st.i-1+q);
        kt  += st.w[q]*xtab(1,st.i-1+q);
        br  += st.w[q]*xtab(2,st.i-1+q);
        alp += st.w[q]*atab(st.i-1+q);
      }
    }
    // at the centre the direction is undefined and KL = KT for regular data
    const Real ir = (r > 1.0e-12*c.dr) ? 1.0/r : 0.0;
    const Real n[3] = {d[0]*ir, d[1]*ir, d[2]*ir};
    const Real psi4 = adm.psi4(m,k,j,i);
    for (int a=0; a<3; ++a) {
      if (set_shift) { adm.beta_u(m,a,k,j,i) = br*n[a]; }
      for (int b=a; b<3; ++b) {
        // added to what the main loop set (zero, or the Bowen-York curvature of
        // punctures with momentum or spin), so that both kinds of curvature combine
        adm.vK_dd(m,a,b,k,j,i) += psi4*(((a == b) ? kt : 0.0) + (kl - kt)*n[a]*n[b]);
      }
    }
    if (set_lapse) { adm.alpha(m,k,j,i) = alp; }
  });
}

} // namespace

//----------------------------------------------------------------------------------------
//! \fn void ProblemGenerator::NrpicConformallyFlat
//! \brief conformally flat initial data for the Z4c evolution, time-symmetric unless
//! a table of format 2 gives the extrinsic curvature

void ProblemGenerator::NrpicConformallyFlat(ParameterInput *pin, const bool restart) {
  user_ref_func = NrpicCFRefinement;
  if (restart) return;

  MeshBlockPack *pmbp = pmy_mesh_->pmb_pack;
  auto &indcs = pmy_mesh_->mb_indcs;
  if (pmbp->pz4c == nullptr) {
    CFFatal("nrpic_cf requires a <z4c> block");
  }

  // ---- components of the conformal factor
  const int ncomp = pin->GetInteger("problem", "ncomp");
  if (ncomp < 1 || ncomp > kCFMaxComp) {
    CFFatal("<problem> ncomp must be between 1 and 8");
  }
  CFComp comp[kCFMaxComp];
  std::vector<Real> utab_h, atab_h;
  std::vector<Real> kltab_h, kttab_h, brtab_h;   // KL, KT, betar (format 2; else zero)
  int kcomp = -1;                                // the component of format 2
  for (int c=0; c<ncomp; ++c) {
    const std::string pre = "comp" + std::to_string(c) + "_";
    const std::string type = pin->GetString("problem", pre + "type");
    comp[c].x[0] = pin->GetOrAddReal("problem", pre + "x1", 0.0);
    comp[c].x[1] = pin->GetOrAddReal("problem", pre + "x2", 0.0);
    comp[c].x[2] = pin->GetOrAddReal("problem", pre + "x3", 0.0);
    comp[c].mass = 0.0; comp[c].sigma = 1.0; comp[c].a = 1.0; comp[c].b = 2.0;
    comp[c].ntab = 0; comp[c].off = 0; comp[c].dr = 1.0;
    comp[c].rlast = 0.0; comp[c].ulast = 0.0;
    comp[c].npiece = 1; comp[c].ext = kExtZero;
    comp[c].kl_last = 0.0; comp[c].kt_last = 0.0; comp[c].a_last = 1.0;
    comp[c].b_last = 0.0;
    for (int b=0; b<=kCFMaxBreak; ++b) { comp[c].klo[b] = 0; comp[c].khi[b] = 0; }
    for (int b=0; b<kCFMaxBreak; ++b) { comp[c].brk[b] = 0.0; }
    if (type.compare("table") == 0 &&
        CFIsFormat2(pin->GetString("problem", pre + "file"))) {
      if (kcomp >= 0) {
        CFFatal("only one component of a run may be a table of format 2");
      }
      kcomp = c;
      comp[c].type = kCFTable2;
      std::vector<Real> u, a, kl, kt, br;
      CFReadTable2(pin->GetString("problem", pre + "file"), comp[c], u, a, kl, kt, br);
      comp[c].off = static_cast<int>(utab_h.size());
      utab_h.insert(utab_h.end(), u.begin(), u.end());
      atab_h.insert(atab_h.end(), a.begin(), a.end());
      kltab_h.resize(comp[c].off, 0.0);
      kttab_h.resize(comp[c].off, 0.0);
      brtab_h.resize(comp[c].off, 0.0);
      kltab_h.insert(kltab_h.end(), kl.begin(), kl.end());
      kttab_h.insert(kttab_h.end(), kt.begin(), kt.end());
      brtab_h.insert(brtab_h.end(), br.begin(), br.end());
    } else if (type.compare("table") == 0) {
      comp[c].type = kCFTable;
      const std::string fname = pin->GetString("problem", pre + "file");
      std::ifstream fin(fname);
      if (!fin.is_open()) CFFatal("cannot open radial table " + fname);
      std::vector<Real> r, u, a;
      std::string line;
      while (std::getline(fin, line)) {
        if (line.empty() || line[0] == '#') continue;
        std::istringstream iss(line);
        Real rr, uu, aa;
        if (iss >> rr >> uu >> aa) {
          r.push_back(rr); u.push_back(uu); a.push_back(aa);
        }
      }
      const int n = static_cast<int>(r.size());
      if (n < 8) CFFatal("radial table " + fname + " has fewer than 8 rows");
      const Real dr = r[1] - r[0];
      if (std::fabs(r[0]) > 1.0e-12*dr ||
          std::fabs(r[n-1] - (n-1)*dr) > 1.0e-8*r[n-1]) {
        CFFatal("radial table " + fname + " is not uniform starting at r = 0");
      }
      comp[c].ntab = n;
      comp[c].off = static_cast<int>(utab_h.size());
      comp[c].dr = dr;
      comp[c].rlast = r[n-1];
      comp[c].ulast = u[n-1];
      comp[c].mass = 2.0*r[n-1]*u[n-1];
      utab_h.insert(utab_h.end(), u.begin(), u.end());
      atab_h.insert(atab_h.end(), a.begin(), a.end());
    } else if (type.compare("puncture") == 0) {
      comp[c].type = kCFPuncture;
      comp[c].mass = pin->GetReal("problem", pre + "mass");
    } else if (type.compare("gaussian") == 0) {
      comp[c].type = kCFGaussian;
      comp[c].mass = pin->GetReal("problem", pre + "mass");
      comp[c].sigma = pin->GetReal("problem", pre + "sigma");
    } else if (type.compare("spheroid") == 0) {
      comp[c].type = kCFSpheroid;
      comp[c].mass = pin->GetReal("problem", pre + "mass");
      comp[c].a = pin->GetReal("problem", pre + "a");
      comp[c].b = pin->GetReal("problem", pre + "b");
      if (!(comp[c].b > comp[c].a) || !(comp[c].a > 0.0)) {
        CFFatal("spheroid component needs 0 < a < b (prolate, polar axis along z)");
      }
    } else {
      CFFatal("<problem> " + pre + "type = '" + type + "' not recognized");
    }
  }
  // Bowen-York momentum and spin of the punctures, corrections of their psi
  std::vector<Real> bytab_h;
  const nrpic_by::BYSet by = nrpic_by::BYRead(pin, ncomp, bytab_h);
  const DvceArray1D<Real> bytab = nrpic_by::BYDeviceTable(bytab_h);
  // momentum and spin of the Gaussian components (smeared Bowen-York curvature)
  const nrpic_clump::ClumpSet clumps = nrpic_clump::ClumpRead(pin, ncomp);
  // momentum of table components (boost table, correction of psi, comoving shift)
  std::vector<Real> tctab_h, tccor_h;
  const nrpic_tclump::TClumpSet tcl =
      nrpic_tclump::TClumpRead(pin, ncomp, tctab_h, tccor_h);
  const DvceArray1D<Real> tctab = nrpic_by::BYDeviceTable(tctab_h);
  const DvceArray1D<Real> tccor = nrpic_by::BYDeviceTable(tccor_h);
  for (int c=0; c<tcl.n; ++c) {
    if (tcl.c[c].icomp == kcomp) {
      CFFatal("a table of format 2 cannot carry a boost table");
    }
  }

  const std::string lapse = pin->GetOrAddString("problem", "lapse", "one");
  const int lcomp = pin->GetOrAddInteger("problem", "lapse_comp", 0);
  int lmode = kLapseOne;
  if (lapse.compare("one") == 0) {
    lmode = kLapseOne;
  } else if (lapse.compare("table") == 0) {
    lmode = kLapseTable;
    if (lcomp >= 0 && lcomp < ncomp && comp[lcomp].type == kCFTable2) {
      lmode = kLapseTable2;   // set with the extrinsic curvature, after the metric
    } else if (lcomp < 0 || lcomp >= ncomp || comp[lcomp].type != kCFTable) {
      CFFatal("lapse = table requires component lapse_comp to be of type table");
    }
  } else if (lapse.compare("isotropic") == 0) {
    lmode = kLapseIsotropic;
  } else if (lapse.compare("precollapsed") == 0) {
    lmode = kLapsePre;
  } else {
    CFFatal("<problem> lapse = '" + lapse + "' not recognized");
  }

  // initial shift: zero, or that of the table of format 2
  bool shift_table = false;
  if (kcomp >= 0) {
    const std::string shift = pin->GetOrAddString("problem", "shift", "zero");
    const int scomp = pin->GetOrAddInteger("problem", "shift_comp", kcomp);
    if (shift.compare("table") == 0) {
      shift_table = true;
      if (scomp != kcomp) {
        CFFatal("shift = table requires shift_comp to be the table of format 2");
      }
    } else if (shift.compare("zero") != 0) {
      CFFatal("<problem> shift = '" + shift + "' not recognized");
    }
  } else if (pin->DoesParameterExist("problem", "shift") &&
             pin->GetString("problem", "shift").compare("zero") != 0) {
    CFFatal("<problem> shift other than zero requires a table of format 2");
  }

  // tables on the device
  const int ntot = static_cast<int>(utab_h.size());
  DvceArray1D<Real> utab("cf_utab", (ntot > 0) ? ntot : 1);
  DvceArray1D<Real> atab("cf_atab", (ntot > 0) ? ntot : 1);
  if (ntot > 0) {
    auto uh = Kokkos::create_mirror_view(utab);
    auto ah = Kokkos::create_mirror_view(atab);
    for (int n=0; n<ntot; ++n) {
      uh(n) = utab_h[n];
      ah(n) = atab_h[n];
    }
    Kokkos::deep_copy(utab, uh);
    Kokkos::deep_copy(atab, ah);
  }

  // ---- ADM variables on all cells, including ghost cells
  auto &size = pmbp->pmb->mb_size;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ng = indcs.ng;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int n1 = nx1 + 2*ng, n2 = nx2 + 2*ng, n3 = nx3 + 2*ng;
  const int nmb = pmbp->nmb_thispack;
  auto &adm = pmbp->padm->adm;
  const CFComp lc = comp[lcomp < ncomp ? lcomp : 0];
  par_for("nrpic_cf", DevExeSpace(), 0, nmb-1, 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    const Real x = CellCenterX(i-is, nx1, size.d_view(m).x1min, size.d_view(m).x1max);
    const Real y = CellCenterX(j-js, nx2, size.d_view(m).x2min, size.d_view(m).x2max);
    const Real z = CellCenterX(k-ks, nx3, size.d_view(m).x3min, size.d_view(m).x3max);
    Real psi = 1.0;
    for (int c=0; c<ncomp; ++c) {
      psi += CFExcess(comp[c], utab, x, y, z);
    }
    for (int c=0; c<by.n; ++c) {
      psi += nrpic_by::BYCorrection(by.punc[c], bytab, x, y, z);
    }
    for (int c=0; c<tcl.ncorr; ++c) {
      psi += nrpic_by::BYCorrection(tcl.corr[c], tccor, x, y, z);
    }
    const Real psi4 = psi*psi*psi*psi;
    adm.psi4(m,k,j,i) = psi4;
    for (int a=0; a<3; ++a) {
      adm.beta_u(m,a,k,j,i) = 0.0;
      for (int b=a; b<3; ++b) {
        adm.g_dd(m,a,b,k,j,i) = (a == b) ? psi4 : 0.0;
        adm.vK_dd(m,a,b,k,j,i) = 0.0;
      }
    }
    if (by.curv) {
      Real ab[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
      for (int c=0; c<by.n; ++c) {
        nrpic_by::BYAddCurvature(by.punc[c], x, y, z, ab);
      }
      const Real ipsi2 = 1.0/(psi*psi);
      int q = 0;
      for (int a=0; a<3; ++a) {
        for (int b=a; b<3; ++b) {
          adm.vK_dd(m,a,b,k,j,i) += ipsi2*ab[q++];
        }
      }
    }
    if (clumps.n > 0) {
      Real ab[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
      for (int c=0; c<clumps.n; ++c) {
        nrpic_clump::ClumpAddCurvature(clumps.c[c], x, y, z, ab);
      }
      const Real ipsi2 = 1.0/(psi*psi);
      int q = 0;
      for (int a=0; a<3; ++a) {
        for (int b=a; b<3; ++b) {
          adm.vK_dd(m,a,b,k,j,i) += ipsi2*ab[q++];
        }
      }
    }
    if (tcl.n > 0) {
      Real ab[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
      Real bt[3] = {0.0, 0.0, 0.0};
      for (int c=0; c<tcl.n; ++c) {
        nrpic_tclump::TClumpAddCurvature(tcl.c[c], tctab, x, y, z, ab);
        nrpic_tclump::TClumpAddShift(tcl.c[c], tctab, x, y, z, bt);
      }
      const Real ipsi2 = 1.0/(psi*psi);
      int q = 0;
      for (int a=0; a<3; ++a) {
        adm.beta_u(m,a,k,j,i) += bt[a];
        for (int b=a; b<3; ++b) {
          adm.vK_dd(m,a,b,k,j,i) += ipsi2*ab[q++];
        }
      }
    }
    Real alp = 1.0;
    if (lmode == kLapseTable) {
      const Real dx = x - lc.x[0], dy = y - lc.x[1], dz = z - lc.x[2];
      const Real r = sqrt(dx*dx + dy*dy + dz*dz);
      if (r >= lc.rlast) {
        const Real w = 0.5*lc.mass/r;
        alp = (1.0 - w)/(1.0 + w);
      } else {
        alp = CFCubic(atab, lc.off, lc.ntab, lc.dr, r);
      }
    } else if (lmode == kLapseIsotropic) {
      alp = (2.0 - psi)/psi;
    } else if (lmode == kLapsePre) {
      alp = 1.0/(psi*psi);
    }
    adm.alpha(m,k,j,i) = alp;
  });

  // ---- extrinsic curvature, and on request lapse and shift, of a table of format 2
  if (kcomp >= 0) {
    DvceArray2D<Real> xtab("cf_xtab", 3, ntot);
    auto xh = Kokkos::create_mirror_view(xtab);
    kltab_h.resize(ntot, 0.0);
    kttab_h.resize(ntot, 0.0);
    brtab_h.resize(ntot, 0.0);
    for (int n=0; n<ntot; ++n) {
      xh(0,n) = kltab_h[n];
      xh(1,n) = kttab_h[n];
      xh(2,n) = brtab_h[n];
    }
    Kokkos::deep_copy(xtab, xh);
    CFSetExtrinsic(pmbp, comp[kcomp], atab, xtab, (lmode == kLapseTable2), shift_table);
  }

  // ---- Z4c variables and constraints (the matter sources are deposited later)
  switch (indcs.ng) {
    case 2: pmbp->pz4c->ADMToZ4c<2>(pmbp, pin); break;
    case 3: pmbp->pz4c->ADMToZ4c<3>(pmbp, pin); break;
    case 4: pmbp->pz4c->ADMToZ4c<4>(pmbp, pin); break;
  }
  pmbp->pz4c->Z4cToADM(pmbp);
  switch (indcs.ng) {
    case 2: pmbp->pz4c->ADMConstraints<2>(pmbp); break;
    case 3: pmbp->pz4c->ADMConstraints<3>(pmbp); break;
    case 4: pmbp->pz4c->ADMConstraints<4>(pmbp); break;
  }
  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC: conformally flat initial data with " << ncomp
              << " component(s), lapse = " << lapse << std::endl;
    if (kcomp >= 0) {
      std::cout << "NRPIC: extrinsic curvature from component " << kcomp
                << " (table of format 2), shift = " << (shift_table ? "table" : "zero")
                << std::endl;
    }
  }
  return;
}
