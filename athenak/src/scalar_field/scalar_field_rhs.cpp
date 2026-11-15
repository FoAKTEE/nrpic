//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file scalar_field_rhs.cpp
//! \brief right-hand side of the scalar field and its sources of the spacetime, both
//! written with the Z4c variables of the current stage:
//!   gamma_ij = psi^4 gt_ij,  psi^-4 = chi^(-4/p),  d_i ln psi = d_i chi/(p chi),
//!   p = chi_psi_power (default -4: psi^-4 = chi),  K = Khat + 2 Theta,
//!   D^i D_i phi = psi^-4 [ gt^ij d_i d_j phi - Gt^k d_k phi + 2 gt^ij d_i ln psi d_j phi ]
//! with Gt^k = gt^ij Gammat^k_ij computed from the conformal metric (as the second
//! covariant derivative of the lapse in z4c_calcrhs.cpp), not the evolved Gamma.

#include <math.h>

#include <cmath>
#include <iostream>

#include "athena.hpp"
#include "mesh/mesh.hpp"
#include "driver/driver.hpp"
#include "coordinates/adm.hpp"
#include "z4c/z4c.hpp"
#include "z4c/tmunu.hpp"
#include "scalar_field/scalar_field.hpp"

namespace scalarfield {

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::CalcRHS
//! \brief d_t phi and d_t Pi (see scalar_field.hpp), the stochastic sources of phi and
//! Pi of this stage, and the Kreiss-Oliger dissipation

template <int NGHOST>
void ScalarField::CalcRHS(Driver *pdriver, int stage) {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  auto &size = pmy_pack->pmb->mb_size;
  int &is = indcs.is; int &ie = indcs.ie;
  int &js = indcs.js; int &je = indcs.je;
  int &ks = indcs.ks; int &ke = indcs.ke;
  int nmb = pmy_pack->nmb_thispack;

  auto &z4c = pmy_pack->pz4c->z4c;
  const Real chi_psi_power = pmy_pack->pz4c->opt.chi_psi_power;
  const Real chi_div_floor = pmy_pack->pz4c->opt.chi_div_floor;
  auto &sf_ = sf;
  auto &rhs_ = rhs;
  const SfPotential pot_ = pot;
  auto tab = pot_tab.d_view;

  // stochastic sources of this stage (NoiseStage has prepared the fields)
  const bool noise_power = noise_ready && nopt.model == kNoisePower;
  const bool noise_ms = noise_ready && nopt.model == kNoiseMS && nopt.kick_pi;
  const Real dt = pmy_pack->pmesh->dt;
  const Real src_phi = (noise_power && dt > 0.0) ? nopt.c_phi/dt : 0.0;
  const Real src_pi = (noise_power && dt > 0.0) ? nopt.c_pi/dt : 0.0;
  const Real kick_pi = kick_pi_fac;
  auto noise = u_noise;

  par_for("sf rhs loop",DevExeSpace(),0,nmb-1,ks,ke,js,je,is,ie,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> dphi_d;    // field 1st drvts
    AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> dalpha_d;  // lapse 1st drvts
    AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> dchi_d;    // chi 1st drvts
    AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> Gamma_u;   // Gamma from the metric
    AthenaPointTensor<Real, TensorSymm::SYM2, 3, 2> ddphi_dd;  // field 2nd drvts
    AthenaPointTensor<Real, TensorSymm::SYM2, 3, 2> g_uu;      // inverse of conf. metric
    AthenaPointTensor<Real, TensorSymm::SYM2, 3, 3> dg_ddd;    // metric 1st drvts
    AthenaPointTensor<Real, TensorSymm::SYM2, 3, 3> Gamma_ddd; // Christoffel 1st kind

    Real idx[] = {1/size.d_view(m).dx1, 1/size.d_view(m).dx2, 1/size.d_view(m).dx3};

    // derivatives
    for(int a = 0; a < 3; ++a) {
      dphi_d(a)   = Dx<NGHOST>(a, idx, sf_.phi,   m,k,j,i);
      dalpha_d(a) = Dx<NGHOST>(a, idx, z4c.alpha, m,k,j,i);
      dchi_d(a)   = Dx<NGHOST>(a, idx, z4c.chi,   m,k,j,i);
    }
    for(int a = 0; a < 3; ++a) {
      ddphi_dd(a,a) = Dxx<NGHOST>(a, idx, sf_.phi, m,k,j,i);
      for(int b = a + 1; b < 3; ++b) {
        ddphi_dd(a,b) = Dxy<NGHOST>(a, b, idx, sf_.phi, m,k,j,i);
      }
    }
    for(int a = 0; a < 3; ++a)
    for(int b = a; b < 3; ++b)
    for(int c = 0; c < 3; ++c) {
      dg_ddd(c,a,b) = Dx<NGHOST>(c, idx, z4c.g_dd, m,a,b,k,j,i);
    }

    // advective derivatives along the shift
    Real Lphi = 0.0, LPi = 0.0;
    for(int a = 0; a < 3; ++a) {
      Lphi += Lx<NGHOST>(a, idx, z4c.beta_u, sf_.phi, m,a,k,j,i);
      LPi  += Lx<NGHOST>(a, idx, z4c.beta_u, sf_.vPi, m,a,k,j,i);
    }

    // inverse conformal metric and its contracted Christoffel symbols
    const Real detg = adm::SpatialDet(z4c.g_dd(m,0,0,k,j,i), z4c.g_dd(m,0,1,k,j,i),
                                      z4c.g_dd(m,0,2,k,j,i), z4c.g_dd(m,1,1,k,j,i),
                                      z4c.g_dd(m,1,2,k,j,i), z4c.g_dd(m,2,2,k,j,i));
    adm::SpatialInv(1.0/detg,
               z4c.g_dd(m,0,0,k,j,i), z4c.g_dd(m,0,1,k,j,i), z4c.g_dd(m,0,2,k,j,i),
               z4c.g_dd(m,1,1,k,j,i), z4c.g_dd(m,1,2,k,j,i), z4c.g_dd(m,2,2,k,j,i),
               &g_uu(0,0), &g_uu(0,1), &g_uu(0,2),
               &g_uu(1,1), &g_uu(1,2), &g_uu(2,2));
    for(int c = 0; c < 3; ++c)
    for(int a = 0; a < 3; ++a)
    for(int b = a; b < 3; ++b) {
      Gamma_ddd(c,a,b) = 0.5*(dg_ddd(a,b,c) + dg_ddd(b,a,c) - dg_ddd(c,a,b));
    }
    Gamma_u.ZeroClear();
    for(int a = 0; a < 3; ++a)
    for(int b = 0; b < 3; ++b)
    for(int c = 0; c < 3; ++c)
    for(int d = 0; d < 3; ++d) {
      Gamma_u(a) += g_uu(b,c)*g_uu(a,d)*Gamma_ddd(d,b,c);
    }

    // conformal factor
    const Real chi_guarded = (z4c.chi(m,k,j,i) > chi_div_floor)
                             ? z4c.chi(m,k,j,i) : chi_div_floor;
    const Real oopsi4 = pow(chi_guarded, -4./chi_psi_power);

    // Laplacian of the field with the physical metric, times psi^4; d_i alpha d^i phi
    Real lap = 0.0, dadphi = 0.0;
    for(int a = 0; a < 3; ++a) {
      lap -= Gamma_u(a)*dphi_d(a);
      for(int b = 0; b < 3; ++b) {
        lap += g_uu(a,b)*(ddphi_dd(a,b)
                          + 2.0*dchi_d(a)/(chi_guarded*chi_psi_power)*dphi_d(b));
        dadphi += g_uu(a,b)*dalpha_d(a)*dphi_d(b);
      }
    }

    const Real K = z4c.vKhat(m,k,j,i) + 2.*z4c.vTheta(m,k,j,i);
    const Real alpha = z4c.alpha(m,k,j,i);
    const Real Pi = sf_.vPi(m,k,j,i);
    Real v, dv;
    SfPotentialEval(pot_, tab, sf_.phi(m,k,j,i), v, dv);

    rhs_.phi(m,k,j,i) = Lphi + alpha*Pi;
    rhs_.vPi(m,k,j,i) = LPi + alpha*(oopsi4*lap + K*Pi - dv) + oopsi4*dadphi;

    // stochastic sources
    if (noise_power) {
      rhs_.phi(m,k,j,i) += src_phi*noise(m,0,k,j,i);
      rhs_.vPi(m,k,j,i) += src_pi*noise(m,1,k,j,i);
    } else if (noise_ms) {
      rhs_.vPi(m,k,j,i) += kick_pi*noise(m,0,k,j,i);
    }
  });

  // dissipation, as for the spacetime variables
  if (diss != 0.0) {
    Real &diss_ = diss;
    auto &u0_ = u0;
    auto &u_rhs_ = u_rhs;
    par_for("sf K-O Dissipation",
    DevExeSpace(),0,nmb-1,0,nsf-1,ks,ke,js,je,is,ie,
    KOKKOS_LAMBDA(const int m, const int n, const int k, const int j, const int i) {
      Real idx[] = {1/size.d_view(m).dx1, 1/size.d_view(m).dx2, 1/size.d_view(m).dx3};
      for(int a = 0; a < 3; ++a) {
        u_rhs_(m,n,k,j,i) += Diss<NGHOST>(a, idx, u0_, m, n, k, j, i)*diss_;
      }
    });
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::AssembleSourcesT
//! \brief writes the sources of all matter modules into Tmunu::tmunu_tot (active cells):
//! E, S_i, S_ij of the scalar field from the current u0 and the current Z4c state, plus
//! the sources of the other modules.  stage_sources = true (before a right-hand side of
//! the spacetime): the others are u_tmunu, or, if they are given as densities of the
//! step (Tmunu::step_density), these times 1/sqrt(gamma) of this stage plus the vacuum
//! energy, exactly what the solver would form itself.  stage_sources = false (before the
//! constraints): the others are u_tmunu, the sources at the time of the state.

template <int NGHOST>
void ScalarField::AssembleSourcesT(const bool stage_sources) {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  auto &size = pmy_pack->pmb->mb_size;
  int &is = indcs.is; int &ie = indcs.ie;
  int &js = indcs.js; int &je = indcs.je;
  int &ks = indcs.ks; int &ke = indcs.ke;
  int nmb = pmy_pack->nmb_thispack;

  auto &z4c = pmy_pack->pz4c->z4c;
  const Real chi_psi_power = pmy_pack->pz4c->opt.chi_psi_power;
  const Real chi_div_floor = pmy_pack->pz4c->opt.chi_div_floor;
  auto &sf_ = sf;
  const SfPotential pot_ = pot;
  auto tab = pot_tab.d_view;

  Tmunu *ptm = pmy_pack->ptmunu;
  const bool mdens = stage_sources && ptm->step_density;
  const Real lam8 = mdens ? ptm->lambda8pi : 0.0;
  Tmunu::Tmunu_vars oth = mdens ? ptm->tmunu_step : ptm->tmunu;
  Tmunu::Tmunu_vars tot = ptm->tmunu_tot;

  par_for("sf tmunu loop",DevExeSpace(),0,nmb-1,ks,ke,js,je,is,ie,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> dphi_d;
    AthenaPointTensor<Real, TensorSymm::SYM2, 3, 2> g_uu;

    Real idx[] = {1/size.d_view(m).dx1, 1/size.d_view(m).dx2, 1/size.d_view(m).dx3};
    for(int a = 0; a < 3; ++a) {
      dphi_d(a) = Dx<NGHOST>(a, idx, sf_.phi, m,k,j,i);
    }
    const Real detg = adm::SpatialDet(z4c.g_dd(m,0,0,k,j,i), z4c.g_dd(m,0,1,k,j,i),
                                      z4c.g_dd(m,0,2,k,j,i), z4c.g_dd(m,1,1,k,j,i),
                                      z4c.g_dd(m,1,2,k,j,i), z4c.g_dd(m,2,2,k,j,i));
    adm::SpatialInv(1.0/detg,
               z4c.g_dd(m,0,0,k,j,i), z4c.g_dd(m,0,1,k,j,i), z4c.g_dd(m,0,2,k,j,i),
               z4c.g_dd(m,1,1,k,j,i), z4c.g_dd(m,1,2,k,j,i), z4c.g_dd(m,2,2,k,j,i),
               &g_uu(0,0), &g_uu(0,1), &g_uu(0,2),
               &g_uu(1,1), &g_uu(1,2), &g_uu(2,2));
    const Real chi_guarded = (z4c.chi(m,k,j,i) > chi_div_floor)
                             ? z4c.chi(m,k,j,i) : chi_div_floor;
    const Real oopsi4 = pow(chi_guarded, -4./chi_psi_power);
    // 1/sqrt(gamma) of this stage for sources given as densities
    const Real mfac = mdens ? pow(chi_guarded, -6./chi_psi_power) : 1.0;

    Real dphi2 = 0.0;
    for(int a = 0; a < 3; ++a)
    for(int b = 0; b < 3; ++b) {
      dphi2 += oopsi4*g_uu(a,b)*dphi_d(a)*dphi_d(b);
    }
    const Real Pi = sf_.vPi(m,k,j,i);
    Real v, dv;
    SfPotentialEval(pot_, tab, sf_.phi(m,k,j,i), v, dv);

    // coefficient of gamma_ij in S_ij, including the vacuum energy of the other modules
    const Real pres = 0.5*Pi*Pi - 0.5*dphi2 - v - lam8;

    tot.E(m,k,j,i) = mfac*oth.E(m,k,j,i) + lam8 + 0.5*Pi*Pi + 0.5*dphi2 + v;
    for(int a = 0; a < 3; ++a) {
      tot.S_d(m,a,k,j,i) = mfac*oth.S_d(m,a,k,j,i) - Pi*dphi_d(a);
      for(int b = a; b < 3; ++b) {
        tot.S_dd(m,a,b,k,j,i) = mfac*oth.S_dd(m,a,b,k,j,i) + dphi_d(a)*dphi_d(b)
                              + pres*z4c.g_dd(m,a,b,k,j,i)/oopsi4;
      }
    }
  });
}

template void ScalarField::CalcRHS<2>(Driver *pdriver, int stage);
template void ScalarField::CalcRHS<3>(Driver *pdriver, int stage);
template void ScalarField::CalcRHS<4>(Driver *pdriver, int stage);
template void ScalarField::AssembleSourcesT<2>(const bool stage_sources);
template void ScalarField::AssembleSourcesT<3>(const bool stage_sources);
template void ScalarField::AssembleSourcesT<4>(const bool stage_sources);

} // namespace scalarfield
