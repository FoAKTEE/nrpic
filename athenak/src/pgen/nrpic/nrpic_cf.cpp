//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_cf.cpp
//! \brief Problem generator for conformally flat, time-symmetric initial data,
//!   gamma_ij = psi^4 delta_ij,  K_ij = 0,  beta^i = 0,
//! with the conformal factor given as a superposition psi = 1 + sum_c u_c(x - x_c).
//! Each component u_c solves the flat-space Poisson equation for a conformal source, so
//! the superposition solves the Hamiltonian constraint for the matter density
//! rho = rho~ psi^-5 with rho~ the sum of the conformal sources.  Components:
//!   table     spherical profile u(r) read from a radial table (docs/FORMATS.md),
//!             continued as u = M/(2r) outside the table
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
//! The matter is carried by the particles of the nrpic module, which reads them from
//! <particles> particle_file.

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

namespace {

enum CFType {kCFTable = 0, kCFPuncture = 1, kCFGaussian = 2, kCFSpheroid = 3};
enum CFLapse {kLapseOne = 0, kLapseTable = 1, kLapseIsotropic = 2, kLapsePre = 3};
constexpr int kCFMaxComp = 8;

struct CFComp {
  int type;
  Real x[3];      // centre
  Real mass;      // puncture: bare mass; gaussian: conformal mass; spheroid: ADM mass
  Real sigma;     // gaussian width
  Real a, b;      // spheroid semi-axes (equatorial, polar)
  int ntab, off;  // table: number of rows and offset into the concatenated tables
  Real dr;        // table spacing
  Real rlast, ulast;
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

} // namespace

//----------------------------------------------------------------------------------------
//! \fn void ProblemGenerator::NrpicConformallyFlat
//! \brief conformally flat, time-symmetric initial data for the Z4c evolution

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
  for (int c=0; c<ncomp; ++c) {
    const std::string pre = "comp" + std::to_string(c) + "_";
    const std::string type = pin->GetString("problem", pre + "type");
    comp[c].x[0] = pin->GetOrAddReal("problem", pre + "x1", 0.0);
    comp[c].x[1] = pin->GetOrAddReal("problem", pre + "x2", 0.0);
    comp[c].x[2] = pin->GetOrAddReal("problem", pre + "x3", 0.0);
    comp[c].mass = 0.0; comp[c].sigma = 1.0; comp[c].a = 1.0; comp[c].b = 2.0;
    comp[c].ntab = 0; comp[c].off = 0; comp[c].dr = 1.0;
    comp[c].rlast = 0.0; comp[c].ulast = 0.0;
    if (type.compare("table") == 0) {
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

  const std::string lapse = pin->GetOrAddString("problem", "lapse", "one");
  const int lcomp = pin->GetOrAddInteger("problem", "lapse_comp", 0);
  int lmode = kLapseOne;
  if (lapse.compare("one") == 0) {
    lmode = kLapseOne;
  } else if (lapse.compare("table") == 0) {
    lmode = kLapseTable;
    if (lcomp < 0 || lcomp >= ncomp || comp[lcomp].type != kCFTable) {
      CFFatal("lapse = table requires component lapse_comp to be of type table");
    }
  } else if (lapse.compare("isotropic") == 0) {
    lmode = kLapseIsotropic;
  } else if (lapse.compare("precollapsed") == 0) {
    lmode = kLapsePre;
  } else {
    CFFatal("<problem> lapse = '" + lapse + "' not recognized");
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
    const Real psi4 = psi*psi*psi*psi;
    adm.psi4(m,k,j,i) = psi4;
    for (int a=0; a<3; ++a) {
      adm.beta_u(m,a,k,j,i) = 0.0;
      for (int b=a; b<3; ++b) {
        adm.g_dd(m,a,b,k,j,i) = (a == b) ? psi4 : 0.0;
        adm.vK_dd(m,a,b,k,j,i) = 0.0;
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
  }
  return;
}
