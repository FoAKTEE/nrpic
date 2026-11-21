//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file scalar_field_slice.cpp
//! \brief Initial slice of the stochastic-inflation runs (pgen scalar_field, id =
//! stochastic): a homogeneous background plus the linear perturbations of the
//! coarse-grained curvature perturbation, synthesized with the mode set, the amplitudes
//! alpha_n (epoch 0) and the per-MeshBlock sums of the stochastic sources, so that the
//! slice and the sources are one realisation.
//!
//! Specification: tracks/E-stoch-inf/spec/SPEC.md, section 5.3 (branch
//! track/E-stoch-inf), the geodesic-gauge data of arXiv:2502.06783 eq. (17) with the
//! corrected delta Pi.  In the variables of the code (G = 1, K = -3H, Pi = n.d phi, so
//! that sqrt(2 eps1) Mpl of the papers is Pi_b/H):
//!   A = R^> = W R,   B = dR^>/dtau = W' R + W R'   (per mode; R, R' from the mode file,
//!       W = (1 + tanh[s ln(sigma a H/k)])/2, W' = (s/2) sech^2 H (1 - eps1); with
//!       <problem> slice_window = false: A = R, B = R')
//!   Psi  = -eps1 H a^2 B/k^2                       (Bardeen potential, Phi_B = Psi_B)
//!   delta phi = (Pi_b/H) (A - Psi)
//!   delta K   = 3 eps1 H (A - Psi)                 (= 12 pi Pi_b delta phi)
//!   delta Pi  = (Pi_b/H) B - Pi_b (eps1 + eps2/2) (A - Psi)
//!   chi       = chi_b (1 - (p/2) Psi)              (p = chi_psi_power; -4: 1 + 2 Psi)
//!   gt_ij = delta_ij,  At_ij = 0,  Gamma^i = 0,  Theta = 0,  alpha = 1,  beta = 0.
//! The slice is the hypersurface of the longitudinal gauge at t*, so the perturbations
//! of K and Pi follow from the longitudinal-gauge momentum constraint and the unit
//! normal.  The linearised Hamiltonian constraint of these data is
//!   -4 (k^2/a^2) Psi - 4 eps1 H B = 0
//! for any pair (A, B), and the linearised momentum constraint holds through
//! delta K = 12 pi Pi_b delta phi.  With <problem> slice_k2 = stencil (default) k^2 is
//! the symbol of the second differences of the mesh (the operator of the Ricci scalar
//! in Z4c::ADMConstraints), so the discrete linearised constraints vanish to rounding;
//! continuum takes k^2 = (2 pi |n|/L)^2.  <problem> slice_delta_pi = printed adds
//! Pi_b Psi to delta Pi: the printed equation of arXiv:2502.06783, a negative control
//! with the linear Hamiltonian residual -4 eps1 H^2 Psi.

#include <cmath>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "z4c/z4c.hpp"
#include "scalar_field/scalar_field.hpp"

namespace scalarfield {

namespace {
void SliceFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in scalar_field_slice.cpp" << std::endl << msg
            << std::endl;
  std::exit(EXIT_FAILURE);
}

//! minus the symbol of the centred second difference with ng ghost cells (orders 2, 4,
//! 6) times h^2: Dxx exp(i k x) = -(kap2/h^2) exp(i k x), kap2 -> (k h)^2
Real StencilSecondSymbol(const Real kh, const int ng) {
  if (ng == 2) {
    return 2.0 - 2.0*std::cos(kh);
  } else if (ng == 3) {
    return 5.0/2.0 - (8.0/3.0)*std::cos(kh) + (1.0/6.0)*std::cos(2.0*kh);
  }
  return 49.0/18.0 - 3.0*std::cos(kh) + 0.3*std::cos(2.0*kh)
         - (1.0/45.0)*std::cos(3.0*kh);
}
} // namespace

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::InitialSlice
//! \brief adds the perturbations of the file header to the homogeneous data that the
//! problem generator has written with the field phib0, the momentum pib0 and psi = 1
//! (all cells; this function changes the active cells, the driver exchanges the ghost
//! cells before the run starts)

void ScalarField::InitialSlice(ParameterInput *pin, const Real phib0, const Real pib0) {
  if (!nopt.on || nopt.model != kNoiseMS) {
    SliceFatal("<problem> id = stochastic needs <scalar_field> noise = mukhanov_sasaki "
               "(mode set, amplitudes and mode file of the stochastic sources)");
  }
  Mesh *pm = pmy_pack->pmesh;
  const bool windowed = pin->GetOrAddBoolean("problem", "slice_window", true);
  bool printed = false;
  {
    const std::string f = pin->GetOrAddString("problem", "slice_delta_pi", "corrected");
    if (f.compare("printed") == 0) {
      printed = true;
    } else if (f.compare("corrected") != 0) {
      SliceFatal("<problem> slice_delta_pi must be corrected or printed");
    }
  }
  bool stencil = true;
  {
    const std::string f = pin->GetOrAddString("problem", "slice_k2", "stencil");
    if (f.compare("continuum") == 0) {
      stencil = false;
    } else if (f.compare("stencil") != 0) {
      SliceFatal("<problem> slice_k2 must be stencil or continuum");
    }
  }

  // tables, amplitudes of epoch 0 and mode functions; Startup does not repeat this.
  // The background of the lockstep data is that of the problem generator itself: the
  // box means that NoiseSetup takes carry the rounding of a sum over all cells.
  NoiseSetup(false);
  slice_done = true;
  y0[1] = phib0;
  y0[2] = pib0;
  y0[3] = 0.0;      // a = 1: the problem generator sets psi = 1

  Real bg[8];
  NoiseBackground(y0, bg);
  const Real pib = bg[2], hub = bg[3], a = bg[4], eps1 = bg[5], eps2 = bg[6];
  if (!(hub > 0.0)) { SliceFatal("the background of the initial slice has H <= 0"); }

  const Real len = pm->mesh_size.x1max - pm->mesh_size.x1min;
  const Real kf = 2.0*M_PI/len;
  const Real norm = 1.0/(len*std::sqrt(len));
  const int nroot = pm->mesh_indcs.nx1;
  const Real hroot = len/static_cast<Real>(nroot);
  const int ng = pm->mb_indcs.ng;

  // ---- shell factors of A and B
  std::vector<Real> a_re(nshell), a_im(nshell), b_re(nshell), b_im(nshell);
  Real rms2 = 0.0;
  for (int n=0; n<nshell; ++n) {
    const Real rr = y0[4+4*n], ri = y0[5+4*n], dr = y0[6+4*n], di = y0[7+4*n];
    Real w = 1.0, w1 = 0.0;
    if (windowed) {
      const Real k = kf*std::sqrt(static_cast<Real>(shell_n2[n]));
      const Real x = nopt.sharpness*std::log(nopt.sigma*a*hub/k);
      const Real ch = std::cosh(x);
      w = 0.5*(1.0 + std::tanh(x));
      w1 = 0.5*nopt.sharpness*hub*(1.0 - eps1)/(ch*ch);
    }
    a_re[n] = norm*w*rr;
    a_im[n] = norm*w*ri;
    b_re[n] = norm*(w1*rr + w*dr);
    b_im[n] = norm*(w1*ri + w*di);
  }

  // ---- real factor of Psi for every mode: -eps1 H a^2/k^2
  DvceArray2D<Real> proj_one("sf_slice_proj", 1, nmode);
  auto hp = Kokkos::create_mirror_view(proj_one);
  auto hsh = Kokkos::create_mirror_view(mode_shell);
  Kokkos::deep_copy(hsh, mode_shell);
  std::vector<Real> psi_fac(nmode);
  for (int q=0; q<nmode; ++q) {
    Real k2 = 0.0;
    for (int d=0; d<3; ++d) {
      const Real kh = 2.0*M_PI*static_cast<Real>(mode_n[3*q+d])/static_cast<Real>(nroot);
      k2 += (stencil ? StencilSecondSymbol(kh, ng) : kh*kh)/(hroot*hroot);
    }
    psi_fac[q] = -eps1*hub*a*a/k2;
    // variance of A (both partners of a mode), for the message
    const int s = hsh(q);
    rms2 += 2.0*(a_re[s]*a_re[s] + a_im[s]*a_im[s]);
  }

  // ---- three fields by the synthesis of the stochastic sources (one field per call)
  auto &indcs = pm->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmb = pmy_pack->nmb_thispack;
  DvceArray4D<Real> wa("sf_slice_a", nmb, nx3, nx2, nx1);
  DvceArray4D<Real> wb("sf_slice_b", nmb, nx3, nx2, nx1);
  DvceArray4D<Real> wp("sf_slice_psi", nmb, nx3, nx2, nx1);

  const int nfld_keep = nfld;
  DvceArray2D<Real> proj_keep = proj;
  nfld = 1;
  proj = proj_one;
  auto hr = Kokkos::create_mirror_view(shell_re);
  auto hi = Kokkos::create_mirror_view(shell_im);
  for (int pass=0; pass<3; ++pass) {
    for (int n=0; n<nshell; ++n) {
      hr(n) = (pass == 0) ? a_re[n] : b_re[n];
      hi(n) = (pass == 0) ? a_im[n] : b_im[n];
    }
    for (int q=0; q<nmode; ++q) { hp(0,q) = (pass == 2) ? psi_fac[q] : 1.0; }
    Kokkos::deep_copy(shell_re, hr);
    Kokkos::deep_copy(shell_im, hi);
    Kokkos::deep_copy(proj_one, hp);
    NoiseSynthesize();
    auto noise = u_noise;
    auto dst = (pass == 0) ? wa : ((pass == 1) ? wb : wp);
    par_for("sf_slice_copy", DevExeSpace(), 0, nmb-1, 0, nx3-1, 0, nx2-1, 0, nx1-1,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      dst(m,k,j,i) = noise(m,0,k+ks,j+js,i+is);
    });
  }
  nfld = nfld_keep;
  proj = proj_keep;

  // ---- the perturbed slice
  auto u0_ = u0;
  auto z0 = pmy_pack->pz4c->u0;
  const int ichi = z4c::Z4c::I_Z4C_CHI, ikh = z4c::Z4c::I_Z4C_KHAT;
  const int iphi = I_SF_PHI, ipi = I_SF_PI;
  const Real p = pmy_pack->pz4c->opt.chi_psi_power;
  const Real c_phi = pib/hub;
  const Real c_k = 3.0*eps1*hub;
  const Real c_pi = pib*(eps1 + 0.5*eps2);
  const Real c_ctl = printed ? pib : 0.0;
  par_for("sf_slice", DevExeSpace(), 0, nmb-1, 0, nx3-1, 0, nx2-1, 0, nx1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    const Real psi = wp(m,k,j,i);
    const Real amp = wa(m,k,j,i) - psi;
    u0_(m,iphi,k+ks,j+js,i+is) += c_phi*amp;
    u0_(m,ipi,k+ks,j+js,i+is) += c_phi*wb(m,k,j,i) - c_pi*amp + c_ctl*psi;
    z0(m,ikh,k+ks,j+js,i+is) += c_k*amp;
    z0(m,ichi,k+ks,j+js,i+is) *= (1.0 - 0.5*p*psi);
  });

  if (global_variable::my_rank == 0) {
    std::printf("ScalarField: initial slice with the perturbations of %d modes (window "
                "%s, k^2 %s, delta Pi %s): H = %.6e, eps1 = %.6e, eps2 = %.6e, "
                "rms of R^> = %.3e\n", nmode, windowed ? "on" : "off",
                stencil ? "stencil" : "continuum", printed ? "printed" : "corrected",
                hub, eps1, eps2, std::sqrt(rms2));
  }
}

} // namespace scalarfield
