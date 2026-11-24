//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file scalar_field_noise_mesh.cpp
//! \brief The curvature perturbation R of the Mukhanov-Sasaki sources as a mesh field
//! (<scalar_field> noise_mode_eq = mesh; always with noise_level = 2), the form of
//! Launay, Rigopoulos & Shellard (arXiv:2512.14649, eq. (ReqISTORIZ1), PRD_v2.tex:312-323)
//! instead of one mode function per shell.  Design and choices:
//! tracks/core/interfaces/noise_level2.md.
//!
//! Variables (components I_SF_R, I_SF_PIR of u0, u1, u_rhs, so that the stages of the
//! driver, the ghost exchange and the restart file carry them):
//!   R,  Pi_R = Z n.d R,  Z = 9 Pi^2/K^2  (= Pi^2/H^2 with K = -3H, Pi = n.d phi)
//!   d_t R    = beta^i d_i R    + alpha Pi_R/Z
//!   d_t Pi_R = beta^i d_i Pi_R + alpha (K Pi_R + Z psi^-4 gt^ij d_i d_j R)
//! with the field's stencils and dissipation.  Coefficients (P1:783-788):
//!   level 2: local alpha, beta, K = Khat + 2 Theta, Pi, psi^-4 gt^ij.  The paper prints
//!   d_i d^i R with partial derivatives and names phi_b, K_b, alpha_b, beta_b (P1:323)
//!   and X_b (P1:487) as promoted to local values: psi^-4 gt^ij d_i d_j R is the default
//!   (the principal part of D^i D_i R, the light cone of the evolved metric);
//!   noise_level2_laplacian = covariant takes D^i D_i R, flat psi^-4 delta^ij d_i d_j R.
//!   The three differ at the order of level 2 itself (a metric perturbation times a
//!   derivative of R); Z uses Pi = n.d phi, the proper-time derivative of P1:237, 485;
//!   level 0, 1 with noise_mode_eq = mesh: the uniform background of the level (alpha_b,
//!   K_b = -3 H, Z_b = Pi_b^2/H^2, a^-2 delta^ij, no shift).
//! At every stage the stage's R and V = n.d R = Pi_R/Z are projected onto the mode set,
//!   c(n) = N^-3 sum_cells f(x) exp(-i k_n.(x - x0)),
//! the adjoint of NoiseSynthesize with its tables (exact for a band-limited field), and
//! the noise of mode n is S_R with these coefficients in place of L^-3/2 R_q alpha_n:
//!   d(n) = c_R W'' + (2 c_V + (3 - eps2) H c_R) W',
//! synthesized as before (window, H, eps1, eps2 and kicks from the background of
//! nopt.bg_level).  Everything here acts only if nopt.mesh_r.

#include <cmath>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "driver/driver.hpp"
#include "coordinates/adm.hpp"
#include "z4c/z4c.hpp"
#include "scalar_field/scalar_field.hpp"

namespace scalarfield {

namespace {
void MeshFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in scalar_field_noise_mesh.cpp" << std::endl << msg
            << std::endl;
  std::exit(EXIT_FAILURE);
}
} // namespace

//----------------------------------------------------------------------------------------
//! \fn bool ScalarField::MeshModeRequested
//! \brief true if the input asks for R on the mesh: noise = mukhanov_sasaki and
//! noise_mode_eq = mesh, or noise_level = 2 without noise_mode_eq.  Reads only
//! parameters that exist (the parameter record of other inputs is unchanged); called by
//! the constructor before the arrays are allocated, and by NoiseInit.

bool ScalarField::MeshModeRequested(ParameterInput *pin) {
  if (!pin->DoesParameterExist("scalar_field", "noise")) return false;
  if (pin->GetString("scalar_field", "noise").compare("mukhanov_sasaki") != 0) {
    return false;
  }
  int level = 0;
  if (pin->DoesParameterExist("scalar_field", "noise_level")) {
    level = pin->GetInteger("scalar_field", "noise_level");
  }
  if (pin->DoesParameterExist("scalar_field", "noise_mode_eq")) {
    const std::string m = pin->GetString("scalar_field", "noise_mode_eq");
    if (m.compare("mesh") == 0) return true;
    if (m.compare("shells") == 0) return false;
    MeshFatal("<scalar_field> noise_mode_eq must be shells or mesh");
  }
  return (level == 2);
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseMeshAlloc
//! \brief work arrays of the projection and the maps mode -> pair -> row (NoiseSetup)

void ScalarField::NoiseMeshAlloc() {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  const int nx2 = indcs.nx2, nx3 = indcs.nx3;
  Kokkos::realloc(mode_cre, nmode);
  Kokkos::realloc(mode_cim, nmode);
  Kokkos::realloc(mode_pair, nmode);
  Kokkos::realloc(pair_xv, npair);
  Kokkos::realloc(shell_w1, nshell);
  Kokkos::realloc(shell_w2, nshell);
  h_w1.assign(nshell, 0.0);
  h_w2.assign(nshell, 0.0);
  Kokkos::realloc(prj_re, 2, nmode);
  Kokkos::realloc(prj_im, 2, nmode);
  Kokkos::realloc(pr2_re, 2, nxval, nx3, nx2);
  Kokkos::realloc(pr2_im, 2, nxval, nx3, nx2);
  Kokkos::realloc(pr1_re, 2, npair, nx3);
  Kokkos::realloc(pr1_im, 2, npair, nx3);
  if (nopt.level == 2) {
    Kokkos::realloc(prj_v, pmy_pack->nmb_thispack, nx3, nx2, indcs.nx1);
  }
  auto hps = Kokkos::create_mirror_view(pair_start);
  auto hxs = Kokkos::create_mirror_view(xval_start);
  Kokkos::deep_copy(hps, pair_start);
  Kokkos::deep_copy(hxs, xval_start);
  auto hmp = Kokkos::create_mirror_view(mode_pair);
  auto hpx = Kokkos::create_mirror_view(pair_xv);
  for (int p=0; p<npair; ++p) {
    for (int q=hps(p); q<hps(p+1); ++q) { hmp(q) = p; }
  }
  for (int x=0; x<nxval; ++x) {
    for (int p=hxs(x); p<hxs(x+1); ++p) { hpx(p) = x; }
  }
  Kokkos::deep_copy(mode_pair, hmp);
  Kokkos::deep_copy(pair_xv, hpx);
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseMeshUniform
//! \brief uniform coefficients of levels 0 and 1 at the lockstep state y0:
//! c = (alpha_b, K_b = -3 H, Z_b = Pi_b^2/H^2, a^-2)

void ScalarField::NoiseMeshUniform(Real c[4]) {
  Real bg[8];
  NoiseBackground(y0, bg);
  c[0] = bg[0];
  c[1] = -3.0*bg[3];
  c[2] = bg[2]*bg[2]/(bg[3]*bg[3]);
  c[3] = 1.0/(bg[4]*bg[4]);
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseMeshInit
//! \brief R and Pi_R at t* (Startup, new runs only): the synthesis of the shell factors
//! L^-3/2 R_q and L^-3/2 dR_q/dtau of the mode file with the amplitudes alpha_n (no
//! window), Pi_R = Z V with the Z of the level (local at level 2: that of the slice)

void ScalarField::NoiseMeshInit() {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmb = pmy_pack->nmb_thispack;
  const Real len = pm->mesh_size.x1max - pm->mesh_size.x1min;
  const Real norm = 1.0/(len*std::sqrt(len));

  // one field per synthesis, real factor 1 (as InitialSlice)
  DvceArray2D<Real> proj_one("sf_mesh_proj", 1, nmode);
  Kokkos::deep_copy(proj_one, 1.0);
  const int nfld_keep = nfld;
  DvceArray2D<Real> proj_keep = proj;
  nfld = 1;
  proj = proj_one;
  DvceArray4D<Real> wv("sf_mesh_v", nmb, nx3, nx2, nx1);
  auto hr = Kokkos::create_mirror_view(shell_re);
  auto hi = Kokkos::create_mirror_view(shell_im);
  auto u0_ = u0;
  const int ir = I_SF_R;
  for (int pass=0; pass<2; ++pass) {
    for (int n=0; n<nshell; ++n) {
      hr(n) = norm*y0[((pass == 0) ? 4 : 6) + 4*n];
      hi(n) = norm*y0[((pass == 0) ? 5 : 7) + 4*n];
    }
    Kokkos::deep_copy(shell_re, hr);
    Kokkos::deep_copy(shell_im, hi);
    syn_per_mode = false;
    NoiseSynthesize();
    auto noise = u_noise;
    if (pass == 0) {
      par_for("sf_mesh_init_r", DevExeSpace(), 0, nmb-1, 0, nx3-1, 0, nx2-1, 0, nx1-1,
      KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
        u0_(m,ir,k+ks,j+js,i+is) = noise(m,0,k+ks,j+js,i+is);
      });
    } else {
      par_for("sf_mesh_init_v", DevExeSpace(), 0, nmb-1, 0, nx3-1, 0, nx2-1, 0, nx1-1,
      KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
        wv(m,k,j,i) = noise(m,0,k+ks,j+js,i+is);
      });
    }
  }
  nfld = nfld_keep;
  proj = proj_keep;

  // Pi_R = Z V
  const bool local = (nopt.level == 2);
  Real c[4] = {0.0, 0.0, 0.0, 0.0};
  if (!local) { NoiseMeshUniform(c); }
  const Real zb = c[2];
  auto z0 = pmy_pack->pz4c->u0;
  const int ipr = I_SF_PIR, ipi = I_SF_PI;
  const int ikh = z4c::Z4c::I_Z4C_KHAT, ith = z4c::Z4c::I_Z4C_THETA;
  par_for("sf_mesh_init_pir", DevExeSpace(), 0, nmb-1, 0, nx3-1, 0, nx2-1, 0, nx1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    Real zz = zb;
    if (local) {
      const Real pi = u0_(m,ipi,k+ks,j+js,i+is);
      const Real kk = z0(m,ikh,k+ks,j+js,i+is) + 2.0*z0(m,ith,k+ks,j+js,i+is);
      zz = 9.0*pi*pi/(kk*kk);
    }
    u0_(m,ipr,k+ks,j+js,i+is) = zz*wv(m,k,j,i);
  });
  if (global_variable::my_rank == 0) {
    std::cout << "ScalarField: R and Pi_R on the mesh ("
              << (local ? "local coefficients, level 2" : "uniform coefficients, level ")
              << (local ? "" : std::to_string(nopt.level)) << "), started from the mode "
              << "file" << std::endl;
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseMeshExchange
//! \brief ghost cells of the field's arrays after NoiseMeshInit (the sequence of
//! Driver::InitBoundaryValuesAndPrimitives; the driver pointer is not used)

void ScalarField::NoiseMeshExchange() {
  (void) RestrictU(nullptr, 0);
  (void) InitRecv(nullptr, -1);
  (void) SendU(nullptr, 0);
  (void) ClearSend(nullptr, -1);
  (void) ClearRecv(nullptr, -1);
  (void) RecvU(nullptr, 0);
  (void) Prolongate(nullptr, 0);
  (void) ApplyPhysicalBCs(nullptr, 0);
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseMeshCoefficients
//! \brief projections of R and V = Pi_R/Z of the current state onto the mode set, then
//! the complex noise coefficient of every mode (needs the W', W'' and friction of the
//! stage from NoiseModeRHS)

void ScalarField::NoiseMeshCoefficients() {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmb = pmy_pack->nmb_thispack;
  const Real nroot = static_cast<Real>(pm->mesh_indcs.nx1);
  const Real inv = 1.0/(nroot*nroot*nroot);
  const int nxv = nxval, np = npair, nm = nmode, nmx = nmax;

  const bool local = (nopt.level == 2);
  Real c[4] = {0.0, 0.0, 1.0, 0.0};
  if (!local) { NoiseMeshUniform(c); }
  const Real izb = 1.0/c[2];

  auto u0_ = u0;
  auto z0 = pmy_pack->pz4c->u0;
  const int ir = I_SF_R, ipr = I_SF_PIR, ipi = I_SF_PI;
  const int ikh = z4c::Z4c::I_Z4C_KHAT, ith = z4c::Z4c::I_Z4C_THETA;
  auto tc = trig_c, ts = trig_s;
  auto xnx = xval_nx, pny = pair_ny, pxv = pair_xv, mnz = mode_nz, mpr = mode_pair;
  auto p2r = pr2_re, p2i = pr2_im;
  auto p1r = pr1_re, p1i = pr1_im;
  auto prr = prj_re, pri = prj_im;
  Kokkos::deep_copy(prj_re, 0.0);
  Kokkos::deep_copy(prj_im, 0.0);

  // level 2: V = n.d R = Pi_R/Z of every cell, formed once per call (the first sum below
  // reads every cell once per row n_x)
  auto pv = prj_v;
  if (local) {
    par_for("sf_prj_v", DevExeSpace(), 0, nmb-1, 0, nx3-1, 0, nx2-1, 0, nx1-1,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      const Real pi = u0_(m,ipi,k+ks,j+js,i+is);
      const Real kk = z0(m,ikh,k+ks,j+js,i+is) + 2.0*z0(m,ith,k+ks,j+js,i+is);
      pv(m,k,j,i) = u0_(m,ipr,k+ks,j+js,i+is)*kk*kk/(9.0*pi*pi);
    });
  }

  for (int mb=0; mb<nmb; ++mb) {
    const int m = mb;
    // sum over i: rows (field f, n_x, k, j); field 1 is V = Pi_R/Z of the cell
    par_for("sf_prj_x", DevExeSpace(), 0, 1, 0, nxv-1, 0, nx3-1, 0, nx2-1,
    KOKKOS_LAMBDA(const int f, const int x, const int k, const int j) {
      const int nx = xnx(x);
      Real re = 0.0, im = 0.0;
      for (int i=0; i<nx1; ++i) {
        Real v;
        if (f == 0) {
          v = u0_(m,ir,k+ks,j+js,i+is);
        } else if (local) {
          v = pv(m,k,j,i);
        } else {
          v = u0_(m,ipr,k+ks,j+js,i+is)*izb;
        }
        re += v*tc(m,0,nx+nmx,i);
        im -= v*ts(m,0,nx+nmx,i);
      }
      p2r(f,x,k,j) = re;
      p2i(f,x,k,j) = im;
    });
    // sum over j: pairs (n_x, n_y)
    par_for("sf_prj_y", DevExeSpace(), 0, 1, 0, np-1, 0, nx3-1,
    KOKKOS_LAMBDA(const int f, const int p, const int k) {
      const int x = pxv(p), ny = pny(p);
      Real re = 0.0, im = 0.0;
      for (int j=0; j<nx2; ++j) {
        const Real a = p2r(f,x,k,j), b = p2i(f,x,k,j);
        const Real cs = tc(m,1,ny+nmx,j), sn = ts(m,1,ny+nmx,j);
        re += a*cs + b*sn;
        im += b*cs - a*sn;
      }
      p1r(f,p,k) = re;
      p1i(f,p,k) = im;
    });
    // sum over k: modes, accumulated over the MeshBlocks in their order
    par_for("sf_prj_z", DevExeSpace(), 0, 1, 0, nm-1,
    KOKKOS_LAMBDA(const int f, const int q) {
      const int p = mpr(q), nz = mnz(q);
      Real re = 0.0, im = 0.0;
      for (int k=0; k<nx3; ++k) {
        const Real a = p1r(f,p,k), b = p1i(f,p,k);
        const Real cs = tc(m,2,nz+nmx,k), sn = ts(m,2,nz+nmx,k);
        re += a*cs + b*sn;
        im += b*cs - a*sn;
      }
      prr(f,q) += inv*re;
      pri(f,q) += inv*im;
    });
  }

  // noise coefficient of every mode: S_R with the projected R and n.d R
  auto mshell = mode_shell;
  auto w1 = shell_w1, w2 = shell_w2;
  auto mcr = mode_cre, mci = mode_cim;
  const Real fric = stage_fric;
  par_for("sf_prj_coef", DevExeSpace(), 0, nm-1,
  KOKKOS_LAMBDA(const int q) {
    const int s = mshell(q);
    const Real cr = prr(0,q), ci = pri(0,q), vr = prr(1,q), vi = pri(1,q);
    mcr(q) = cr*w2(s) + (2.0*vr + fric*cr)*w1(s);
    mci(q) = ci*w2(s) + (2.0*vi + fric*ci)*w1(s);
  });

  // a non-finite R or Z = 0 (Pi = 0 in a cell at level 2) makes every coefficient
  // non-finite; the kicks then carry it into the spacetime fields, where <z4c_guard>
  // stops the run at the end of the cycle.  Said once here, with the cause.
  if (!mesh_warned) {
    int nbad = 0;
    Kokkos::parallel_reduce("sf_prj_finite", Kokkos::RangePolicy<>(DevExeSpace(), 0, nm),
    KOKKOS_LAMBDA(const int q, int &lbad) {
      if (!(Kokkos::isfinite(mcr(q)) && Kokkos::isfinite(mci(q)))) { lbad += 1; }
    }, Kokkos::Sum<int>(nbad));
    if (nbad > 0) {
      mesh_warned = true;
      if (global_variable::my_rank == 0) {
        std::cout << "### WARNING ScalarField: " << nbad << " noise coefficients of the "
                  << "mesh path are not finite at time " << pm->time << " (R or Pi_R not "
                  << "finite, or Pi = 0 in a cell at noise_level = 2)" << std::endl;
      }
    }
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseMeshRHST
//! \brief right-hand sides of R and Pi_R (components I_SF_R, I_SF_PIR of u_rhs only),
//! with the dissipation of the field

template <int NGHOST>
void ScalarField::NoiseMeshRHST() {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  auto &size = pmy_pack->pmb->mb_size;
  const int is = indcs.is, ie = indcs.ie;
  const int js = indcs.js, je = indcs.je;
  const int ks = indcs.ks, ke = indcs.ke;
  const int nmb = pmy_pack->nmb_thispack;

  auto &z4c = pmy_pack->pz4c->z4c;
  const Real chi_psi_power = pmy_pack->pz4c->opt.chi_psi_power;
  const Real chi_div_floor = pmy_pack->pz4c->opt.chi_div_floor;
  AthenaTensor<Real, TensorSymm::NONE, 3, 0> tr, tp;
  tr.InitWithShallowSlice(u0, I_SF_R);
  tp.InitWithShallowSlice(u0, I_SF_PIR);
  auto u0_ = u0;
  auto rhs = u_rhs;
  const int ir = I_SF_R, ipr = I_SF_PIR, ipi = I_SF_PI;

  const bool local = (nopt.level == 2);
  const int lapk = nopt.lap_kind;
  Real c[4] = {0.0, 0.0, 0.0, 0.0};
  if (!local) { NoiseMeshUniform(c); }
  const Real ab = c[0], kb = c[1], zb = c[2], ia2 = c[3];
  const Real diss_ = diss;

  par_for("sf_mesh_rhs", DevExeSpace(), 0, nmb-1, ks, ke, js, je, is, ie,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    Real idx[] = {1/size.d_view(m).dx1, 1/size.d_view(m).dx2, 1/size.d_view(m).dx3};
    const Real pir = u0_(m,ipr,k,j,i);
    Real rr, rp;
    if (local) {
      AthenaPointTensor<Real, TensorSymm::SYM2, 3, 2> ddr_dd;  // 2nd drvts of R
      AthenaPointTensor<Real, TensorSymm::SYM2, 3, 2> g_uu;    // inverse conf. metric
      for (int a=0; a<3; ++a) {
        ddr_dd(a,a) = Dxx<NGHOST>(a, idx, tr, m,k,j,i);
        for (int b=a+1; b<3; ++b) {
          ddr_dd(a,b) = Dxy<NGHOST>(a, b, idx, tr, m,k,j,i);
        }
      }
      const Real detg = adm::SpatialDet(z4c.g_dd(m,0,0,k,j,i), z4c.g_dd(m,0,1,k,j,i),
                                        z4c.g_dd(m,0,2,k,j,i), z4c.g_dd(m,1,1,k,j,i),
                                        z4c.g_dd(m,1,2,k,j,i), z4c.g_dd(m,2,2,k,j,i));
      adm::SpatialInv(1.0/detg,
                 z4c.g_dd(m,0,0,k,j,i), z4c.g_dd(m,0,1,k,j,i), z4c.g_dd(m,0,2,k,j,i),
                 z4c.g_dd(m,1,1,k,j,i), z4c.g_dd(m,1,2,k,j,i), z4c.g_dd(m,2,2,k,j,i),
                 &g_uu(0,0), &g_uu(0,1), &g_uu(0,2),
                 &g_uu(1,1), &g_uu(1,2), &g_uu(2,2));
      Real lap = 0.0;
      for (int a=0; a<3; ++a) {
        for (int b=0; b<3; ++b) { lap += g_uu(a,b)*ddr_dd(a,b); }
      }
      Real lr = 0.0, lp = 0.0;
      for (int a=0; a<3; ++a) {
        lr += Lx<NGHOST>(a, idx, z4c.beta_u, tr, m,a,k,j,i);
        lp += Lx<NGHOST>(a, idx, z4c.beta_u, tp, m,a,k,j,i);
      }
      const Real chi_guarded = (z4c.chi(m,k,j,i) > chi_div_floor)
                               ? z4c.chi(m,k,j,i) : chi_div_floor;
      if (lapk == 2) {
        // only the conformal factor local: psi^-4 delta^ij d_i d_j R
        lap = ddr_dd(0,0) + ddr_dd(1,1) + ddr_dd(2,2);
      } else if (lapk == 1) {
        // psi^4 D^i D_i R = gt^ij d_i d_j R - Gt^k d_k R + 2 gt^ij d_i ln psi d_j R, with
        // Gt^k from the conformal metric, as for the field (scalar_field_rhs.cpp)
        AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> dr_d;      // R 1st drvts
        AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> dchi_d;    // chi 1st drvts
        AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> Gamma_u;   // Gamma from the metric
        AthenaPointTensor<Real, TensorSymm::SYM2, 3, 3> dg_ddd;    // metric 1st drvts
        AthenaPointTensor<Real, TensorSymm::SYM2, 3, 3> Gamma_ddd; // Christoffel 1st kind
        for (int a=0; a<3; ++a) {
          dr_d(a)   = Dx<NGHOST>(a, idx, tr,      m,k,j,i);
          dchi_d(a) = Dx<NGHOST>(a, idx, z4c.chi, m,k,j,i);
        }
        for (int a=0; a<3; ++a)
        for (int b=a; b<3; ++b)
        for (int d=0; d<3; ++d) {
          dg_ddd(d,a,b) = Dx<NGHOST>(d, idx, z4c.g_dd, m,a,b,k,j,i);
        }
        for (int d=0; d<3; ++d)
        for (int a=0; a<3; ++a)
        for (int b=a; b<3; ++b) {
          Gamma_ddd(d,a,b) = 0.5*(dg_ddd(a,b,d) + dg_ddd(b,a,d) - dg_ddd(d,a,b));
        }
        Gamma_u.ZeroClear();
        for (int a=0; a<3; ++a)
        for (int b=0; b<3; ++b)
        for (int d=0; d<3; ++d)
        for (int e=0; e<3; ++e) {
          Gamma_u(a) += g_uu(b,d)*g_uu(a,e)*Gamma_ddd(e,b,d);
        }
        for (int a=0; a<3; ++a) {
          lap -= Gamma_u(a)*dr_d(a);
          for (int b=0; b<3; ++b) {
            lap += g_uu(a,b)*2.0*dchi_d(a)/(chi_guarded*chi_psi_power)*dr_d(b);
          }
        }
      }
      const Real oopsi4 = pow(chi_guarded, -4./chi_psi_power);
      const Real kk = z4c.vKhat(m,k,j,i) + 2.*z4c.vTheta(m,k,j,i);
      const Real alpha = z4c.alpha(m,k,j,i);
      const Real pi = u0_(m,ipi,k,j,i);
      const Real zz = 9.0*pi*pi/(kk*kk);
      rr = lr + alpha*pir/zz;
      rp = lp + alpha*(kk*pir + zz*oopsi4*lap);
    } else {
      Real lap = 0.0;
      for (int a=0; a<3; ++a) { lap += Dxx<NGHOST>(a, idx, tr, m,k,j,i); }
      rr = ab*pir/zb;
      rp = ab*(kb*pir + zb*ia2*lap);
    }
    if (diss_ != 0.0) {
      for (int a=0; a<3; ++a) {
        rr += Diss<NGHOST>(a, idx, u0_, m, ir, k, j, i)*diss_;
        rp += Diss<NGHOST>(a, idx, u0_, m, ipr, k, j, i)*diss_;
      }
    }
    rhs(m,ir,k,j,i) = rr;
    rhs(m,ipr,k,j,i) = rp;
  });
}

void ScalarField::NoiseMeshRHS() {
  switch (pmy_pack->pmesh->mb_indcs.ng) {
    case 2: NoiseMeshRHST<2>(); break;
    case 3: NoiseMeshRHST<3>(); break;
    case 4: NoiseMeshRHST<4>(); break;
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseMeshWriteModes
//! \brief <basename>.sf.NNNNN.rmodes next to a dump (noise_rmodes_dump = true): per mode
//! n, |n|^2 and the projections divided by L^-3/2 alpha_n, i.e. the effective mode
//! functions R and dR/dtau of the mesh field, comparable to the shells of .modes

void ScalarField::NoiseMeshWriteModes(Real time, int number) {
  Mesh *pm = pmy_pack->pmesh;
  const Real len = pm->mesh_size.x1max - pm->mesh_size.x1min;
  const Real norm = 1.0/(len*std::sqrt(len));
  auto hr = Kokkos::create_mirror_view(prj_re);
  auto hi = Kokkos::create_mirror_view(prj_im);
  Kokkos::deep_copy(hr, prj_re);
  Kokkos::deep_copy(hi, prj_im);
  auto ar = Kokkos::create_mirror_view(alpha_re);
  auto ai = Kokkos::create_mirror_view(alpha_im);
  Kokkos::deep_copy(ar, alpha_re);
  Kokkos::deep_copy(ai, alpha_im);
  char fname[512];
  std::snprintf(fname, sizeof(fname), "%s.sf.%05d.rmodes", basename.c_str(), number);
  std::FILE *fp = std::fopen(fname, "w");
  if (fp == nullptr) { MeshFatal(std::string("cannot open ") + fname); }
  std::fprintf(fp, "# time %.17e  level %d  background %d  modes %d\n", time, nopt.level,
               nopt.bg_level, nmode);
  std::fprintf(fp, "# nx ny nz n2  Re_R Im_R Re_dR Im_dR  (projections / (L^-3/2 "
               "alpha_n); dR = n.d R)\n");
  for (int q=0; q<nmode; ++q) {
    const double a2 = ar(0,q)*ar(0,q) + ai(0,q)*ai(0,q);
    double v[4];
    for (int f=0; f<2; ++f) {
      // (x + i y)/(norm (u + i w)) = (x + i y)(u - i w)/(norm |alpha|^2)
      const double x = hr(f,q), y = hi(f,q);
      v[2*f] = (x*ar(0,q) + y*ai(0,q))/(norm*a2);
      v[2*f+1] = (y*ar(0,q) - x*ai(0,q))/(norm*a2);
    }
    const int nx = mode_n[3*q], ny = mode_n[3*q+1], nz = mode_n[3*q+2];
    std::fprintf(fp, "%d %d %d %d %.17e %.17e %.17e %.17e\n", nx, ny, nz,
                 nx*nx + ny*ny + nz*nz, v[0], v[1], v[2], v[3]);
  }
  std::fclose(fp);
}

template void ScalarField::NoiseMeshRHST<2>();
template void ScalarField::NoiseMeshRHST<3>();
template void ScalarField::NoiseMeshRHST<4>();

} // namespace scalarfield
