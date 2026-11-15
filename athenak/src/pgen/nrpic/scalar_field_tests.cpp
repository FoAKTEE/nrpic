//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file scalar_field_tests.cpp
//! \brief Problem generator for the scalar field (<scalar_field>) in a periodic box,
//! pgen_name = scalar_field.  <problem> id selects the initial data:
//!
//!  wave   flat spacetime (alpha = 1, zero shift), a homogeneous part plus a plane wave:
//!           phi = phi0 + amp cos(k.(x - x0)),  Pi = pi0 + amp omega sin(k.(x - x0)),
//!         k_i = 2 pi n_i / L_i (integers n1, n2, n3), omega = sqrt(k^2 + m^2) unless
//!         <problem> omega is given.  A wave travelling towards +k for alpha = 1.  The
//!         data satisfy the constraints only for a test field (<scalar_field> couple =
//!         false).  <problem> beta1, beta2, beta3 set a uniform shift (still flat
//!         spacetime, in coordinates that move with velocity -beta): the wave then has
//!         the coordinate frequency omega - k.beta.
//!  flrw   homogeneous flat universe: phi = phi0, Pi = pi0, conformally flat with
//!         psi = 1, K = -sqrt(24 pi (Pi^2/2 + V(phi))) (expanding), alpha = 1.
//!  plane  a plane perturbation that satisfies both constraints exactly:
//!           phi = phi0 + amp sin(k.(x - x0)),  psi = 1,  At_ij = 0,
//!           K = K(phi(x)),  Pi = K'(phi)/(12 pi).
//!         The momentum constraint -(2/3) d_i K = -8 pi Pi d_i phi holds identically, and
//!         because |grad phi|^2 = k^2 (amp^2 - (phi - phi0)^2) = G(phi) is a function of
//!         phi, the Hamiltonian constraint is the ordinary differential equation
//!           K'(phi)^2 = 12 pi K^2 - 144 pi^2 G(phi) - 288 pi^2 V(phi),
//!         integrated here from phi0 - amp, where K = -sqrt(24 pi (pi0^2/2 + V)), with
//!         the sign of K' that of pi0 (pi0 is the momentum where the gradient vanishes).
//!         The right-hand side must stay positive: the gradient energy must be smaller
//!         than the kinetic energy.  With <problem> control = true, Pi = pi0 everywhere
//!         (the momentum constraint is then violated at first order in amp).

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "coordinates/adm.hpp"
#include "coordinates/cell_locations.hpp"
#include "z4c/z4c.hpp"
#include "scalar_field/scalar_field.hpp"
#include "pgen/pgen.hpp"

namespace {

void SfTestFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in scalar_field_tests.cpp" << std::endl << msg
            << std::endl;
  std::exit(EXIT_FAILURE);
}

} // namespace

//----------------------------------------------------------------------------------------
//! \fn void ProblemGenerator::ScalarFieldTests
//! \brief initial data of a scalar field and its spacetime in a periodic box

void ProblemGenerator::ScalarFieldTests(ParameterInput *pin, const bool restart) {
  if (restart) return;

  MeshBlockPack *pmbp = pmy_mesh_->pmb_pack;
  auto &indcs = pmy_mesh_->mb_indcs;
  if (pmbp->pz4c == nullptr || pmbp->pscalar == nullptr) {
    SfTestFatal("pgen scalar_field requires <z4c> and <scalar_field> blocks");
  }
  scalarfield::ScalarField *psf = pmbp->pscalar;

  const std::string id = pin->GetOrAddString("problem", "id", "wave");
  int kind = 0;
  if (id.compare("wave") == 0) {
    kind = 0;
  } else if (id.compare("flrw") == 0) {
    kind = 1;
  } else if (id.compare("plane") == 0) {
    kind = 2;
  } else {
    SfTestFatal("<problem> id = '" + id + "' not recognized (wave, flrw, plane)");
  }
  const Real phi0 = pin->GetOrAddReal("problem", "phi0", 0.0);
  const Real pi0 = pin->GetOrAddReal("problem", "pi0", 0.0);
  const Real amp = pin->GetOrAddReal("problem", "amp", 0.0);
  const int nw[3] = {pin->GetOrAddInteger("problem", "n1", 1),
                     pin->GetOrAddInteger("problem", "n2", 0),
                     pin->GetOrAddInteger("problem", "n3", 0)};
  const bool control = pin->GetOrAddBoolean("problem", "control", false);
  const Real bw1 = pin->GetOrAddReal("problem", "beta1", 0.0);
  const Real bw2 = pin->GetOrAddReal("problem", "beta2", 0.0);
  const Real bw3 = pin->GetOrAddReal("problem", "beta3", 0.0);
  if (kind != 0 && (bw1 != 0.0 || bw2 != 0.0 || bw3 != 0.0)) {
    SfTestFatal("<problem> beta1, beta2, beta3 are for id = wave only");
  }

  const Real gx1 = pmy_mesh_->mesh_size.x1min;
  const Real gx2 = pmy_mesh_->mesh_size.x2min;
  const Real gx3 = pmy_mesh_->mesh_size.x3min;
  const Real kw1 = 2.0*M_PI*nw[0]/(pmy_mesh_->mesh_size.x1max - gx1);
  const Real kw2 = 2.0*M_PI*nw[1]/(pmy_mesh_->mesh_size.x2max - gx2);
  const Real kw3 = 2.0*M_PI*nw[2]/(pmy_mesh_->mesh_size.x3max - gx3);
  const Real ksq = kw1*kw1 + kw2*kw2 + kw3*kw3;

  const scalarfield::SfPotential pot = psf->pot;
  auto tabh = psf->pot_tab.h_view;
  auto tab = psf->pot_tab.d_view;

  // frequency of the wave
  Real omega = 0.0;
  if (kind == 0) {
    Real v, dv0, dv1;
    const Real eps = 1.0e-4;
    scalarfield::SfPotentialEval(pot, tabh, phi0 + eps, v, dv1);
    scalarfield::SfPotentialEval(pot, tabh, phi0 - eps, v, dv0);
    const Real m2eff = (dv1 - dv0)/(2.0*eps);      // V''(phi0)
    omega = pin->GetOrAddReal("problem", "omega", std::sqrt(ksq + m2eff));
  }

  // K(phi) and K'(phi) of the plane perturbation on ntab intervals of [phi0 - amp,
  // phi0 + amp] (classical Runge-Kutta; the table is read with cubic Hermite polynomials)
  const int ntab = 4096;
  const Real tmin = phi0 - amp;
  const Real tdphi = (amp > 0.0) ? 2.0*amp/static_cast<Real>(ntab) : 1.0;
  DvceArray2D<Real> ktab("sf_ktab", 2, ntab + 1);
  if (kind == 2) {
    if (!(amp > 0.0) || pi0 == 0.0) {
      SfTestFatal("<problem> id = plane needs amp > 0 and pi0 != 0");
    }
    auto kh = Kokkos::create_mirror_view(ktab);
    const Real sgn = (pi0 > 0.0) ? 1.0 : -1.0;
    bool bad = false;
    auto slope = [&](const Real ph, const Real kk) -> Real {
      Real v, dv;
      scalarfield::SfPotentialEval(pot, tabh, ph, v, dv);
      const Real g = ksq*(amp*amp - (ph - phi0)*(ph - phi0));
      const Real rad = 12.0*M_PI*kk*kk - 144.0*M_PI*M_PI*g - 288.0*M_PI*M_PI*v;
      if (!(rad > 0.0)) { bad = true; return 0.0; }
      return sgn*std::sqrt(rad);
    };
    Real v, dv;
    scalarfield::SfPotentialEval(pot, tabh, tmin, v, dv);
    Real kk = -std::sqrt(24.0*M_PI*(0.5*pi0*pi0 + v));
    for (int n=0; n<=ntab; ++n) {
      // the end points are set exactly; rounding must not push G below zero there
      const Real ph = (n == ntab) ? phi0 + amp : tmin + n*tdphi;
      kh(0,n) = kk;
      kh(1,n) = slope(ph, kk);
      if (n == ntab) break;
      const Real k1 = kh(1,n);
      const Real k2 = slope(ph + 0.5*tdphi, kk + 0.5*tdphi*k1);
      const Real k3 = slope(ph + 0.5*tdphi, kk + 0.5*tdphi*k2);
      const Real pe = (n == ntab - 1) ? phi0 + amp : ph + tdphi;
      const Real k4 = slope(pe, kk + tdphi*k3);
      kk += tdphi*(k1 + 2.0*k2 + 2.0*k3 + k4)/6.0;
    }
    if (bad) {
      SfTestFatal("<problem> id = plane: K'(phi)^2 becomes negative (the gradient energy "
                  "exceeds the kinetic energy); lower amp or raise |pi0|");
    }
    Kokkos::deep_copy(ktab, kh);
  }

  // ---- ADM variables and the field on all cells, including ghost cells
  auto &size = pmbp->pmb->mb_size;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ng = indcs.ng;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int n1 = nx1 + 2*ng, n2 = nx2 + 2*ng, n3 = nx3 + 2*ng;
  const int nmb = pmbp->nmb_thispack;
  auto &adm = pmbp->padm->adm;
  auto u0 = psf->u0;
  const int iphi = scalarfield::ScalarField::I_SF_PHI;
  const int ipi = scalarfield::ScalarField::I_SF_PI;
  par_for("sf_tests", DevExeSpace(), 0, nmb-1, 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    const Real x = CellCenterX(i-is, nx1, size.d_view(m).x1min, size.d_view(m).x1max);
    const Real y = CellCenterX(j-js, nx2, size.d_view(m).x2min, size.d_view(m).x2max);
    const Real z = CellCenterX(k-ks, nx3, size.d_view(m).x3min, size.d_view(m).x3max);
    const Real phase = kw1*(x - gx1) + kw2*(y - gx2) + kw3*(z - gx3);
    Real phi = phi0, pi = pi0, trk = 0.0;
    if (kind == 0) {
      phi = phi0 + amp*cos(phase);
      pi = pi0 + amp*omega*sin(phase);
    } else if (kind == 1) {
      Real v, dv;
      scalarfield::SfPotentialEval(pot, tab, phi, v, dv);
      trk = -sqrt(24.0*M_PI*(0.5*pi*pi + v));
    } else {
      const Real sn = sin(phase);
      phi = phi0 + amp*sn;
      // cubic Hermite interpolation of K(phi) in the table; s in [0, ntab]
      Real s = (amp*sn + amp)/tdphi;
      if (s < 0.0) { s = 0.0; }
      if (s > static_cast<Real>(ntab)) { s = static_cast<Real>(ntab); }
      int n = static_cast<int>(s);
      if (n > ntab - 1) { n = ntab - 1; }
      const Real t = s - static_cast<Real>(n);
      const Real f0 = ktab(0,n), f1 = ktab(0,n+1);
      const Real d0 = tdphi*ktab(1,n), d1 = tdphi*ktab(1,n+1);
      const Real t2 = t*t, t3 = t2*t;
      trk = (2.0*t3 - 3.0*t2 + 1.0)*f0 + (t3 - 2.0*t2 + t)*d0
          + (-2.0*t3 + 3.0*t2)*f1 + (t3 - t2)*d1;
      const Real dk = ((6.0*t2 - 6.0*t)*f0 + (3.0*t2 - 4.0*t + 1.0)*d0
                     + (-6.0*t2 + 6.0*t)*f1 + (3.0*t2 - 2.0*t)*d1)/tdphi;
      pi = control ? pi0 : dk/(12.0*M_PI);
    }
    u0(m,iphi,k,j,i) = phi;
    u0(m,ipi,k,j,i) = pi;

    adm.psi4(m,k,j,i) = 1.0;
    const Real bw[3] = {bw1, bw2, bw3};
    for (int a=0; a<3; ++a) {
      adm.beta_u(m,a,k,j,i) = bw[a];
      for (int b=a; b<3; ++b) {
        const Real dab = (a == b) ? 1.0 : 0.0;
        adm.g_dd(m,a,b,k,j,i) = dab;
        adm.vK_dd(m,a,b,k,j,i) = dab*trk/3.0;
      }
    }
    adm.alpha(m,k,j,i) = 1.0;
  });

  // ---- Z4c variables; the constraints are evaluated with the sources of the field
  // when the run starts (ScalarField::Startup)
  switch (indcs.ng) {
    case 2: pmbp->pz4c->ADMToZ4c<2>(pmbp, pin); break;
    case 3: pmbp->pz4c->ADMToZ4c<3>(pmbp, pin); break;
    case 4: pmbp->pz4c->ADMToZ4c<4>(pmbp, pin); break;
  }
  pmbp->pz4c->Z4cToADM(pmbp);
  if (global_variable::my_rank == 0) {
    std::cout << "ScalarField: initial data, id = " << id << std::endl;
  }
  return;
}
