//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_newton.cpp
//! \brief Newtonian mode of the NRPIC particle module (<particles> pusher = newton): the
//! same particles, clouds, filter and interpolation as the relativistic mode, with
//! Newtonian gravity in place of the spacetime evolution, so that a relativistic run
//! and its Newtonian reference differ in the gravity only.
//!
//! Equations.  The time coordinate t of the run is conformal time, the positions x are
//! comoving, and the momentum slots hold p = a dx/dt per unit rest mass (the covariant
//! u_i of the relativistic run in the weak-field, slow-motion limit):
//!   dx/dt = p/a,      dp/dt = -grad Phi,      lap Phi = four_pi_G (rho - <rho>),
//! with rho the rest-mass density per coordinate volume deposited by the particles and
//! a(t) a prescribed scale factor.  The Newtonian potential is Phi/a.  The mean density
//! <rho> is removed on a mesh that is periodic in all directions and only there.
//! Without expansion (the default) a = 1, t is the Newtonian time and p the velocity.
//! <particles> newton_expansion = power selects a = (1 + H t/n)^n, with the Hubble rate
//! H = newton_hubble at t = 0 (where a = 1) and n = newton_exponent (2: matter era, the
//! form of cosmo/newton/pm.py; 1: radiation era).  The equation of motion of p has no
//! explicit time dependence, so the scale factor enters only through the drift.
//!
//! One cycle from t^n to t^{n+1} (kick-drift-kick):
//!   NrpicNewtonPush        p += (dt/2) g^n(x^n),  x += p int dt/a   (g = -grad Phi)
//!   NrpicExcise            wrap or remove particles, reassign them to MeshBlocks
//!   NrpicDeposit           existing deposit (rest mass: W = 1), filter, compensation
//!   NrpicNewtonFinishStep  Poisson solve for Phi^{n+1}, p += (dt/2) g^{n+1}(x^{n+1}),
//!                          particle sums of the synchronised state
//!   NrpicDiagnostics       history records
//!
//! The potential is kept in the lapse slot of the metric array met1, whose other slots
//! hold the flat metric: the deposit and the cubic interpolation of the relativistic
//! mode (nrpic::MeshMetric, Catmull-Rom or cubic spline) then serve unchanged, and the
//! gradient of the interpolated lapse is the gradient of the potential.  The existing
//! diagnostics that report the lapse (history, probes) report Phi in this mode.
//!
//! The Poisson equation is solved by the multigrid gravity module (<gravity> block;
//! isolated domains: mg_bc = multipole).  It returns the potential in the active cells;
//! ghost cells are filled here, between MeshBlocks and across periodic faces by the
//! mesh boundary exchange, at other faces by cubic extrapolation.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "driver/driver.hpp"
#include "bvals/bvals.hpp"
#include "coordinates/adm.hpp"
#include "z4c/z4c.hpp"
#include "z4c/tmunu.hpp"
#include "hydro/hydro.hpp"
#include "mhd/mhd.hpp"
#include "gravity/gravity.hpp"
#include "gravity/mg_gravity.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_mesh.hpp"

namespace particles {

namespace {

void NewtonFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_newton.cpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

// indices of the particle sums nw_sum of a synchronised state (all weighted with the
// rest mass m; x comoving position, p momentum per unit mass, v = dx/dt = p/a,
// acc = d^2x/dt^2 = g/a - (da/dt / a) v)
enum NewtonSumIndex {
  NWS_M = 0,       // sum m
  NWS_P2 = 1,      // sum m p.p
  NWS_PHI = 2,     // sum m Phi(x)
  NWS_P = 3,       // sum m p_i                       (3)
  NWS_L = 6,       // sum m (x cross p)_i             (3)
  NWS_X = 9,       // sum m x_i                       (3)
  NWS_I = 12,      // sum m x_i x_j                   (6: xx, xy, xz, yy, yz, zz)
  NWS_DI = 18,     // sum m (x_i v_j + v_i x_j)       (6)
  NWS_DDI = 24,    // sum m (2 v_i v_j + x_i acc_j + acc_i x_j)   (6)
  NWS_N = 30
};
// length of the state block of the restart file
constexpr int kNewtonState = 50;

//----------------------------------------------------------------------------------------
//! \struct NewtonBackground
//! \brief prescribed scale factor in conformal time: a = 1, or a = (1 + h t/n)^n

struct NewtonBackground {
  int kind;       // 0: a = 1; 1: power law
  Real h, n;

  Real S(const Real t) const { return 1.0 + h*t/n; }
  Real A(const Real t) const {
    if (kind == 0) return 1.0;
    if (n == 2.0) return SQR(S(t));
    return std::pow(S(t), n);
  }
  Real DaDt(const Real t) const {
    if (kind == 0) return 0.0;
    if (n == 2.0) return h*S(t);
    return h*std::pow(S(t), n - 1.0);
  }
  // integral of dt/a from t1 to t2
  Real Drift(const Real t1, const Real t2) const {
    if (kind == 0) return t2 - t1;
    const Real s1 = S(t1), s2 = S(t2);
    if (n == 2.0) return (2.0/h)*(1.0/s1 - 1.0/s2);
    if (n == 1.0) return std::log(s2/s1)/h;
    return (n/(h*(1.0 - n)))*(std::pow(s2, 1.0 - n) - std::pow(s1, 1.0 - n));
  }
};

NewtonBackground Background(const NrpicOptions &o) {
  NewtonBackground bg;
  bg.kind = o.newton_expansion;
  bg.h = o.newton_hubble;
  bg.n = o.newton_exponent;
  return bg;
}

} // namespace

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonInit
//! \brief options and arrays of the Newtonian mode; called at the end of NrpicInit

void Particles::NrpicNewtonInit(ParameterInput *pin) {
  Mesh *pm = pmy_pack->pmesh;
  if (nropt.metric != NrpicMetric::mesh) {
    NewtonFatal("<particles> pusher = newton requires metric = mesh (the default)");
  }
  if (pmy_pack->pz4c != nullptr || pmy_pack->padm != nullptr) {
    NewtonFatal("<particles> pusher = newton cannot be combined with <z4c> or <adm>");
  }
  if (pmy_pack->phydro != nullptr || pmy_pack->pmhd != nullptr) {
    NewtonFatal("<particles> pusher = newton cannot be combined with <hydro> or <mhd>: "
                "the gravity module would take the gas density as its source");
  }
  if (!pin->DoesBlockExist("gravity")) {
    NewtonFatal("<particles> pusher = newton requires a <gravity> block (four_pi_G, "
                "threshold or niteration; mg_bc = multipole on an isolated domain)");
  }
  if (!nropt.deposit) {
    NewtonFatal("<particles> pusher = newton requires deposit = true");
  }
  const std::string ex = pin->GetOrAddString("particles", "newton_expansion", "none");
  if (ex.compare("none") == 0) {
    nropt.newton_expansion = 0;
  } else if (ex.compare("power") == 0) {
    nropt.newton_expansion = 1;
  } else {
    NewtonFatal("<particles> newton_expansion = '" + ex + "' not recognized (none or "
                "power)");
  }
  nropt.newton_hubble   = pin->GetOrAddReal("particles", "newton_hubble", 0.0);
  nropt.newton_exponent = pin->GetOrAddReal("particles", "newton_exponent", 2.0);
  nropt.newton_cfl      = pin->GetOrAddReal("particles", "newton_cfl", 0.0);
  nropt.newton_mg_tol   = pin->GetOrAddReal("particles", "newton_mg_tol", 0.0);
  // External gravity at the particles (nrpic_external.hpp).  Parameters that are not in
  // the input are not added to it (the parameter dump of existing set-ups is unchanged).
  {
    auto has = [&](const std::string &key) {
      return pin->DoesParameterExist("particles", key);
    };
    if (has("newton_pm_mass")) { next.pm_mass = pin->GetReal("particles", "newton_pm_mass"); }
    if (has("newton_pm_x1")) { next.pm_x[0] = pin->GetReal("particles", "newton_pm_x1"); }
    if (has("newton_pm_x2")) { next.pm_x[1] = pin->GetReal("particles", "newton_pm_x2"); }
    if (has("newton_pm_x3")) { next.pm_x[2] = pin->GetReal("particles", "newton_pm_x3"); }
    if (has("newton_pm_soft")) { next.pm_soft = pin->GetReal("particles", "newton_pm_soft"); }
    if (has("newton_pm_soft_frame")) {
      const std::string fr = pin->GetString("particles", "newton_pm_soft_frame");
      if (fr != "comoving" && fr != "physical") {
        NewtonFatal("<particles> newton_pm_soft_frame must be comoving or physical");
      }
      next.pm_soft_physical = (fr == "physical");
    }
    if (has("newton_bg_t0")) { next.bg_t0 = pin->GetReal("particles", "newton_bg_t0"); }
    if (next.pm_soft < 0.0) {
      NewtonFatal("<particles> newton_pm_soft must not be negative");
    }
  }
  if (nropt.newton_expansion == 1) {
    if (!(pm->strictly_periodic)) {
      NewtonFatal("<particles> newton_expansion = power requires a mesh that is periodic "
                  "in all directions");
    }
    if (!(nropt.newton_hubble > 0.0) || !(nropt.newton_exponent > 0.0)) {
      NewtonFatal("<particles> newton_expansion = power requires newton_hubble > 0 and "
                  "newton_exponent > 0");
    }
  }
  if (next.bg_t0 != 0.0 && (!(next.bg_t0 > 0.0) || nropt.newton_expansion != 0)) {
    NewtonFatal("<particles> newton_bg_t0 must be positive and needs "
                "newton_expansion = none (the term is the gravity of the background in "
                "physical coordinates)");
  }
  if (!(nropt.newton_cfl > 0.0) && !(dt_user < 1.0e30)) {
    NewtonFatal("<particles> pusher = newton requires a step: dt, or newton_cfl > 0");
  }
  for (int n=0; n<NWS_N; ++n) { nw_sum[n] = 0.0; }

  // ghost cells of the potential
  pbval_phi = new MeshBoundaryValuesCC(pmy_pack, pin, false);
  pbval_phi->InitializeBuffers(1);
  if (pm->multilevel) {
    auto &indcs = pm->mb_indcs;
    int nmb = std::max((pmy_pack->nmb_thispack), (pm->nmb_maxperrank));
    Kokkos::realloc(nw_coarse_phi, nmb, 1, indcs.cnx3 + 2*(indcs.ng),
                    indcs.cnx2 + 2*(indcs.ng), indcs.cnx1 + 2*(indcs.ng));
  }
}

//----------------------------------------------------------------------------------------
//! \fn  Real Particles::NrpicNewtonScale
//! \brief the scale factor a(t) of the Newtonian mode

Real Particles::NrpicNewtonScale(const Real time) {
  return Background(nropt).A(time);
}

//----------------------------------------------------------------------------------------
//! \fn  nrpic::NewtonExternal Particles::NrpicNewtonExternal
//! \brief the external gravity at the given time: point mass with G = four_pi_G/(4 pi)
//! of the <gravity> block and its softening length (fixed in the coordinates of the
//! run, or fixed in physical units, s/a), and the background term 2/(9 (t0 + t)^2)

nrpic::NewtonExternal Particles::NrpicNewtonExternal(const Real time) {
  nrpic::NewtonExternal ext;
  if (next.pm_mass != 0.0) {
    const Real four_pi_g = (pmy_pack->pgrav != nullptr) ? pmy_pack->pgrav->four_pi_G : 0.0;
    ext.gm = four_pi_g*next.pm_mass/(4.0*M_PI);
    ext.xc[0] = next.pm_x[0]; ext.xc[1] = next.pm_x[1]; ext.xc[2] = next.pm_x[2];
    const Real soft = next.pm_soft_physical ? next.pm_soft/Background(nropt).A(time)
                                            : next.pm_soft;
    ext.soft2 = soft*soft;
  }
  if (next.bg_t0 > 0.0) {
    ext.kbg = 2.0/(9.0*SQR(next.bg_t0 + time));
  }
  for (int d=0; d<3; ++d) {
    ext.per[d] = nropt.periodic[d];
    ext.len[d] = nropt.dom_len[d];
  }
  return ext;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonInitialize
//! \brief brings the Newtonian mode to a consistent state on the current mesh: flat
//! metric, MeshBlock ownership, deposited density, potential, particle sums.  Called at
//! the start of a run, after a restart, and after every change of the mesh.

void Particles::NrpicNewtonInitialize() {
  Mesh *pm = pmy_pack->pmesh;
  {
    auto &indcs = pm->mb_indcs;
    const int n1 = indcs.nx1 + 2*(indcs.ng);
    const int n2 = indcs.nx2 + 2*(indcs.ng);
    const int n3 = indcs.nx3 + 2*(indcs.ng);
    const int nmb1 = pmy_pack->nmb_thispack - 1;
    auto met_ = met1;
    par_for("nrpic_newton_flat", DevExeSpace(), 0, nmb1, 0, NRM_NVAR-1, 0, n3-1, 0, n2-1,
            0, n1-1,
    KOKKOS_LAMBDA(const int m, const int n, const int k, const int j, const int i) {
      met_(m,n,k,j,i) = (n == NRM_GXX || n == NRM_GYY || n == NRM_GZZ) ? 1.0 : 0.0;
    });
  }
  if (nropt.interp_bspline) { NrpicSharpenMetric(met1, met1s); }
  NrpicAssignBlocks();
  NrpicRemoveFlagged();
  e_prev_valid = false;
  tm_prev_valid = false;
  NrpicDepositSources();
  if (nropt.deposit_adaptive) {
    NrpicDepositSources();
  }
  NrpicFilterSources();
  NrpicNewtonPotential();
  NrpicNewtonKick(0.0, pm->time);
  // after a restart the diagnostic state continues from the dump
  if (static_cast<int>(nw_state_restart.size()) == kNewtonState) {
    const std::vector<double> &s = nw_state_restart;
    for (int n=0; n<NWS_N; ++n) { nw_sum[n] = s[n]; }
    nw_time = s[30]; nw_a = s[31]; nw_li = s[32];
    for (int n=0; n<6; ++n) { nw_d3i[n] = s[33+n]; }
    nw_d3i_time = s[39]; nw_pmax = s[40]; nw_defect = s[41];
    for (int n=0; n<6; ++n) { nw_mesh[n] = s[42+n]; }
    nw_gmax = s[48];
    nw_ncycle = static_cast<int>(s[49]);
  }
  nw_state_restart.clear();
  NrpicNewtonTimeStep(pm->time);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonPotential
//! \brief solves the Poisson equation for the deposited (and filtered) rest-mass
//! density, fills the ghost cells of the potential and stores it in the lapse slot of
//! met1.  On a mesh that is periodic in all directions the mean of the potential is set
//! to zero.  After a restart the potential of the dump is taken instead of a solve, so
//! that the run continues from the same starting potential.

void Particles::NrpicNewtonPotential() {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  gravity::Gravity *pg = pmy_pack->pgrav;
  if (pg == nullptr || pg->pmgd == nullptr) {
    NewtonFatal("the Newtonian mode found no gravity module");
  }
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
  const int ng = indcs.ng;
  const int n1 = indcs.nx1 + 2*ng, n2 = indcs.nx2 + 2*ng, n3 = indcs.nx3 + 2*ng;
  const int nmb = pmy_pack->nmb_thispack;
  const int nmb1 = nmb - 1;
  auto &tmu = pmy_pack->ptmunu->u_tmunu;

  bool from_dump = false;
  if (!nw_phi_restart.empty()) {
    bool same = true;
    for (int d=0; d<5; ++d) {
      same = same && (nw_phi_restart_dims[d] ==
                      static_cast<std::int64_t>(pg->phi.extent(d)));
    }
    if (same) {
      auto ph = Kokkos::create_mirror_view(Kokkos::HostSpace(), pg->phi);
      std::memcpy(ph.data(), nw_phi_restart.data(),
                  nw_phi_restart.size()*sizeof(double));
      Kokkos::deep_copy(pg->phi, ph);
      from_dump = true;
    }
    nw_phi_restart.clear();
    nw_phi_restart.shrink_to_fit();
  }
  if (!from_dump) {
    if (nw_driver == nullptr) {
      NewtonFatal("the Newtonian mode has no driver for the Poisson solver");
    }
    // defect norm at which the V cycles may end: the fraction newton_mg_tol of the
    // L2 norm of the source four_pi_G (rho - <rho>) (<rho> removed on a periodic mesh)
    Real tol = 0.0;
    if (nropt.newton_mg_tol > 0.0) {
      auto tm0 = tmu;
      auto sz0 = pmy_pack->pmb->mb_size.d_view;
      Real s1 = 0.0, s2 = 0.0, s0 = 0.0;
      Kokkos::parallel_reduce("nrpic_newton_srcnorm",
        Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
          {0, ks, js, is}, {nmb, ke+1, je+1, ie+1}),
      KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &l1,
                    Real &l2, Real &l0) {
        const Real vol = sz0(m).dx1*sz0(m).dx2*sz0(m).dx3;
        const Real r = tm0(m,Tmunu::I_Tmunu_E,k,j,i);
        l1 += r*vol;
        l2 += r*r*vol;
        l0 += vol;
      }, Kokkos::Sum<Real>(s1), Kokkos::Sum<Real>(s2), Kokkos::Sum<Real>(s0));
      if (s0 > 0.0) {
        const Real mean = (pm->strictly_periodic) ? s1/s0 : 0.0;
        const Real var = s2/s0 - mean*(2.0*s1/s0 - mean);
        tol = nropt.newton_mg_tol*(pg->four_pi_G)*std::sqrt((var > 0.0) ? var : 0.0);
      }
    }
    pg->pmgd->SolveSource(nw_driver, tmu, Tmunu::I_Tmunu_E, tol);
    nw_defect = pg->pmgd->last_defect;
    nw_ncycle = pg->pmgd->last_ncycle;
  }

  // mesh sums over the active cells: int rho Phi dV, int Phi dV, int rho dV, volume, and
  // the extrema of Phi
  auto phi = pg->phi;
  auto tm = tmu;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  Real srp = 0.0, sp = 0.0, sr = 0.0, sv = 0.0, pmin = 0.0, pmax = 0.0;
  Kokkos::parallel_reduce("nrpic_newton_mesh",
    Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
      {0, ks, js, is}, {nmb, ke+1, je+1, ie+1}),
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &lrp, Real &lp,
                Real &lr, Real &lv, Real &lmin, Real &lmax) {
    const Real vol = sz(m).dx1*sz(m).dx2*sz(m).dx3;
    const Real f = phi(m,0,k,j,i);
    const Real r = tm(m,Tmunu::I_Tmunu_E,k,j,i);
    lrp += r*f*vol;
    lp += f*vol;
    lr += r*vol;
    lv += vol;
    lmin = fmin(lmin, f);
    lmax = fmax(lmax, f);
  }, Kokkos::Sum<Real>(srp), Kokkos::Sum<Real>(sp), Kokkos::Sum<Real>(sr),
     Kokkos::Sum<Real>(sv), Kokkos::Min<Real>(pmin), Kokkos::Max<Real>(pmax));
  if (pm->strictly_periodic && !from_dump && sv > 0.0) {
    const Real mean = sp/sv;
    par_for("nrpic_newton_mean", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      phi(m,0,k,j,i) -= mean;
    });
    srp -= mean*sr;
    sp = 0.0;
    pmin -= mean;
    pmax -= mean;
  }
  nw_mesh[0] = srp; nw_mesh[1] = sp; nw_mesh[2] = sr; nw_mesh[3] = sv;
  nw_mesh[4] = pmin; nw_mesh[5] = pmax;

  // ghost cells: copies between MeshBlocks at the same level and across periodic
  // faces, restriction and prolongation across levels
  if (pm->multilevel) {
    pm->pmr->RestrictCC(pg->phi, nw_coarse_phi);
  }
  (void) pbval_phi->InitRecv(1);
  (void) pbval_phi->PackAndSendCC(pg->phi, nw_coarse_phi);
  (void) pbval_phi->ClearSend();
  (void) pbval_phi->ClearRecv();
  (void) pbval_phi->RecvAndUnpackCC(pg->phi, nw_coarse_phi);
  if (pm->multilevel) {
    pbval_phi->FillCoarseInBndryCC(pg->phi, nw_coarse_phi);
    pbval_phi->ProlongateCC(pg->phi, nw_coarse_phi);
  }

  // faces of the mesh that are not periodic: cubic extrapolation into the ghost cells,
  // one direction after the other over the full extent of the other two, so that
  // edges and corners are filled from values that are already valid
  if (!(pm->strictly_periodic)) {
    auto mb_bcs = pmy_pack->pmb->mb_bcs.d_view;
    for (int dir=0; dir<3; ++dir) {
      const int na = (dir == 2) ? n2 : n3;
      const int nb = (dir == 0) ? n2 : n1;
      const int s0 = (dir == 0) ? is : ((dir == 1) ? js : ks);
      const int e0 = (dir == 0) ? ie : ((dir == 1) ? je : ke);
      const int fin = 2*dir, fout = 2*dir + 1;
      par_for("nrpic_newton_extrap", DevExeSpace(), 0, nmb1, 0, na-1, 0, nb-1,
      KOKKOS_LAMBDA(const int m, const int a, const int b) {
        const bool lo = (mb_bcs(m,fin) != BoundaryFlag::block &&
                         mb_bcs(m,fin) != BoundaryFlag::periodic);
        const bool hi = (mb_bcs(m,fout) != BoundaryFlag::block &&
                         mb_bcs(m,fout) != BoundaryFlag::periodic);
        for (int n=1; n<=ng; ++n) {
          if (dir == 0) {
            if (lo) {
              const int c = s0 - n;
              phi(m,0,a,b,c) = 4.0*phi(m,0,a,b,c+1) - 6.0*phi(m,0,a,b,c+2)
                             + 4.0*phi(m,0,a,b,c+3) - phi(m,0,a,b,c+4);
            }
            if (hi) {
              const int c = e0 + n;
              phi(m,0,a,b,c) = 4.0*phi(m,0,a,b,c-1) - 6.0*phi(m,0,a,b,c-2)
                             + 4.0*phi(m,0,a,b,c-3) - phi(m,0,a,b,c-4);
            }
          } else if (dir == 1) {
            if (lo) {
              const int c = s0 - n;
              phi(m,0,a,c,b) = 4.0*phi(m,0,a,c+1,b) - 6.0*phi(m,0,a,c+2,b)
                             + 4.0*phi(m,0,a,c+3,b) - phi(m,0,a,c+4,b);
            }
            if (hi) {
              const int c = e0 + n;
              phi(m,0,a,c,b) = 4.0*phi(m,0,a,c-1,b) - 6.0*phi(m,0,a,c-2,b)
                             + 4.0*phi(m,0,a,c-3,b) - phi(m,0,a,c-4,b);
            }
          } else {
            if (lo) {
              const int c = s0 - n;
              phi(m,0,c,a,b) = 4.0*phi(m,0,c+1,a,b) - 6.0*phi(m,0,c+2,a,b)
                             + 4.0*phi(m,0,c+3,a,b) - phi(m,0,c+4,a,b);
            }
            if (hi) {
              const int c = e0 + n;
              phi(m,0,c,a,b) = 4.0*phi(m,0,c-1,a,b) - 6.0*phi(m,0,c-2,a,b)
                             + 4.0*phi(m,0,c-3,a,b) - phi(m,0,c-4,a,b);
            }
          }
        }
      });
    }
  }

  // the potential takes the place of the lapse in the array read by the interpolation
  auto m1 = met1;
  par_for("nrpic_newton_store", DevExeSpace(), 0, nmb1, 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    m1(m,NRM_ALP,k,j,i) = phi(m,0,k,j,i);
  });
  if (nropt.interp_bspline) { NrpicSharpenMetric(met1, met1s); }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonKick
//! \brief p += dt_kick g(x) for all particles, with g = -grad Phi gathered by the
//! interpolation of the relativistic mode, and the particle sums of the resulting
//! state, which belongs to the given time (dt_kick = 0: sums only)

void Particles::NrpicNewtonKick(const Real dt_kick, const Real time) {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int np = nprtcl_thispack;
  const NewtonBackground bg = Background(nropt);
  const Real a = bg.A(time);
  const Real ia = 1.0/a;
  const Real hub = bg.DaDt(time)*ia;          // (da/dt)/a

  nrpic::MeshMetric proto;
  proto.bspline = nropt.interp_bspline;
  proto.m1 = nropt.interp_bspline ? met1s : met1;
  proto.m0 = proto.m1;
  proto.is_static = true;
  proto.ist[0] = indcs.is; proto.ist[1] = indcs.js; proto.ist[2] = indcs.ks;
  proto.ncell[0] = indcs.nx1 + 2*indcs.ng;
  proto.ncell[1] = indcs.nx2 + 2*indcs.ng;
  proto.ncell[2] = indcs.nx3 + 2*indcs.ng;

  // external gravity (fixed point mass, background) at this time; off: nothing is added
  const nrpic::NewtonExternal ext = NrpicNewtonExternal(time);
  const bool ext_on = ext.On();

  array_sum::GlobalSum s1, s2;
  Real pmax2 = 0.0, gmax2 = 0.0;
  if (np > 0) {
    auto pr = prtcl_rdata;
    auto pi = prtcl_idata;
    auto sz = pmy_pack->pmb->mb_size.d_view;
    const int gids = pmy_pack->gids;
    Kokkos::parallel_reduce("nrpic_newton_kick", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, array_sum::GlobalSum &l1, array_sum::GlobalSum &l2,
                  Real &lpmax, Real &lgmax) {
      const int m = pi(PGID,p) - gids;
      const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
      Real u[3] = {pr(IPVX,p), pr(IPVY,p), pr(IPVZ,p)};
      nrpic::MeshMetric met = proto;
      met.m = m;
      met.xmin[0] = sz(m).x1min; met.xmin[1] = sz(m).x2min; met.xmin[2] = sz(m).x3min;
      met.idx[0] = 1.0/sz(m).dx1; met.idx[1] = 1.0/sz(m).dx2; met.idx[2] = 1.0/sz(m).dx3;
      nrpic::AdmPoint ap;
      met(1, x, ap);
      Real g[3] = {-ap.dalp[0], -ap.dalp[1], -ap.dalp[2]};
      // The potential energy sum counts the mesh potential once per pair (the factor
      // 1/2 of the history) and the external potential in full: twice here.
      Real phi_sum = ap.alp;
      if (ext_on) { phi_sum += 2.0*ext.Add(x, g); }
      u[0] += dt_kick*g[0]; u[1] += dt_kick*g[1]; u[2] += dt_kick*g[2];
      pr(IPVX,p) = u[0]; pr(IPVY,p) = u[1]; pr(IPVZ,p) = u[2];

      // sums of the synchronised state; tracers and null particles carry no mass
      const Real mp = (pr(IPM,p) > 0.0) ? pr(IPM,p) : 0.0;
      const Real v[3] = {u[0]*ia, u[1]*ia, u[2]*ia};
      const Real acc[3] = {g[0]*ia - hub*v[0], g[1]*ia - hub*v[1], g[2]*ia - hub*v[2]};
      array_sum::GlobalSum t1, t2;
      t1.the_array[NWS_M] = mp;
      t1.the_array[NWS_P2] = mp*(u[0]*u[0] + u[1]*u[1] + u[2]*u[2]);
      t1.the_array[NWS_PHI] = mp*phi_sum;
      t1.the_array[NWS_P]   = mp*u[0];
      t1.the_array[NWS_P+1] = mp*u[1];
      t1.the_array[NWS_P+2] = mp*u[2];
      t1.the_array[NWS_L]   = mp*(x[1]*u[2] - x[2]*u[1]);
      t1.the_array[NWS_L+1] = mp*(x[2]*u[0] - x[0]*u[2]);
      t1.the_array[NWS_L+2] = mp*(x[0]*u[1] - x[1]*u[0]);
      t1.the_array[NWS_X]   = mp*x[0];
      t1.the_array[NWS_X+1] = mp*x[1];
      t1.the_array[NWS_X+2] = mp*x[2];
      int c = 0;
      for (int ii=0; ii<3; ++ii) {
        for (int jj=ii; jj<3; ++jj) {
          t1.the_array[NWS_I+c] = mp*x[ii]*x[jj];
          t2.the_array[c]   = mp*(x[ii]*v[jj] + v[ii]*x[jj]);
          t2.the_array[6+c] = mp*(2.0*v[ii]*v[jj] + x[ii]*acc[jj] + acc[ii]*x[jj]);
          ++c;
        }
      }
      l1 += t1;
      l2 += t2;
      lpmax = fmax(lpmax, u[0]*u[0] + u[1]*u[1] + u[2]*u[2]);
      lgmax = fmax(lgmax, g[0]*g[0] + g[1]*g[1] + g[2]*g[2]);
    }, Kokkos::Sum<array_sum::GlobalSum>(s1), Kokkos::Sum<array_sum::GlobalSum>(s2),
       Kokkos::Max<Real>(pmax2), Kokkos::Max<Real>(gmax2));
  }
  for (int n=0; n<NWS_DI; ++n) { nw_sum[n] = s1.the_array[n]; }
  for (int n=0; n<12; ++n) { nw_sum[NWS_DI+n] = s2.the_array[n]; }
  nw_time = time;
  nw_a = a;
  nw_pmax = std::sqrt(pmax2);
  nw_gmax = std::sqrt(gmax2);
  nw_valid = true;
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus Particles::NrpicNewtonPush
//! \brief first half of the kick with the potential at t^n, then the drift over the
//! step with the exact integral of dt/a

TaskStatus Particles::NrpicNewtonPush(Driver *pdriver, int stage) {
  nw_driver = pdriver;
  Mesh *pm = pmy_pack->pmesh;
  push_maxit = 0;
  push_unconverged = 0;
  const int np = nprtcl_thispack;
  if (np == 0) return TaskStatus::complete;

  auto &indcs = pm->mb_indcs;
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int gids = pmy_pack->gids;
  const NewtonBackground bg = Background(nropt);
  const Real hdt = 0.5*(pm->dt);
  const Real drift = bg.Drift(pm->time, pm->time + pm->dt);
  const nrpic::NewtonExternal ext = NrpicNewtonExternal(pm->time);
  const bool ext_on = ext.On();

  nrpic::MeshMetric proto;
  proto.bspline = nropt.interp_bspline;
  proto.m1 = nropt.interp_bspline ? met1s : met1;
  proto.m0 = proto.m1;
  proto.is_static = true;
  proto.ist[0] = indcs.is; proto.ist[1] = indcs.js; proto.ist[2] = indcs.ks;
  proto.ncell[0] = indcs.nx1 + 2*indcs.ng;
  proto.ncell[1] = indcs.nx2 + 2*indcs.ng;
  proto.ncell[2] = indcs.nx3 + 2*indcs.ng;

  par_for("nrpic_newton_push", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
    const int m = pi(PGID,p) - gids;
    Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
    Real u[3] = {pr(IPVX,p), pr(IPVY,p), pr(IPVZ,p)};
    nrpic::MeshMetric met = proto;
    met.m = m;
    met.xmin[0] = sz(m).x1min; met.xmin[1] = sz(m).x2min; met.xmin[2] = sz(m).x3min;
    met.idx[0] = 1.0/sz(m).dx1; met.idx[1] = 1.0/sz(m).dx2; met.idx[2] = 1.0/sz(m).dx3;
    nrpic::AdmPoint ap;
    met(1, x, ap);
    if (ext_on) {
      Real g[3] = {-ap.dalp[0], -ap.dalp[1], -ap.dalp[2]};
      (void) ext.Add(x, g);
      for (int d=0; d<3; ++d) {
        u[d] += hdt*g[d];
        x[d] += drift*u[d];
      }
    } else {
      for (int d=0; d<3; ++d) {
        u[d] -= hdt*ap.dalp[d];
        x[d] += drift*u[d];
      }
    }
    // a particle whose state is no longer finite is removed with the excised ones
    const Real chk = x[0] + x[1] + x[2] + u[0] + u[1] + u[2];
    if (!(Kokkos::isfinite(chk))) {
      pi(PGID,p) = -4;
    } else {
      pr(IPX,p) = x[0]; pr(IPY,p) = x[1]; pr(IPZ,p) = x[2];
      pr(IPVX,p) = u[0]; pr(IPVY,p) = u[1]; pr(IPVZ,p) = u[2];
    }
  });
  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonFinishStep
//! \brief after the deposit at t^{n+1}: potential, second half of the kick, and the
//! quantities that combine two synchronised states, the Layzer-Irvine integral of
//! K da (trapezoidal rule) and the third time derivative of the second moment (the
//! difference quotient of the second derivative, which belongs to the middle of the
//! step)

void Particles::NrpicNewtonFinishStep(Driver *pdriver) {
  nw_driver = pdriver;
  Mesh *pm = pmy_pack->pmesh;
  const Real tnew = pm->time + pm->dt;
  const bool had = nw_valid;
  const Real t0 = nw_time, a0 = nw_a;
  const Real k0 = 0.5*nw_sum[NWS_P2]/(a0*a0);
  Real ddi0[6];
  for (int n=0; n<6; ++n) { ddi0[n] = nw_sum[NWS_DDI+n]; }

  NrpicNewtonPotential();
  NrpicNewtonKick(0.5*(pm->dt), tnew);

  if (had) {
    const Real k1 = 0.5*nw_sum[NWS_P2]/(nw_a*nw_a);
    nw_li += 0.5*(k0 + k1)*(nw_a - a0);
    if (tnew > t0) {
      for (int n=0; n<6; ++n) { nw_d3i[n] = (nw_sum[NWS_DDI+n] - ddi0[n])/(tnew - t0); }
      nw_d3i_time = 0.5*(tnew + t0);
    }
  }
  NrpicNewtonTimeStep(tnew);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonTimeStep
//! \brief upper limit of the coming step: <particles> dt and, with newton_cfl = c > 0,
//! the times in which the fastest particle crosses the fraction c of the smallest cell
//! and in which the largest acceleration moves a particle at rest across it

void Particles::NrpicNewtonTimeStep(const Real time) {
  dtnew = dt_user;
  if (!(nropt.newton_cfl > 0.0)) return;
  auto szh = pmy_pack->pmb->mb_size.h_view;
  Real dxmin = szh(0).dx1;
  for (int m=0; m<pmy_pack->nmb_thispack; ++m) {
    dxmin = std::min(dxmin, std::min(szh(m).dx1, std::min(szh(m).dx2, szh(m).dx3)));
  }
  const Real a = Background(nropt).A(time);
  if (nw_pmax > 0.0) {
    dtnew = std::min(dtnew, nropt.newton_cfl*dxmin*a/nw_pmax);
  }
  if (nw_gmax > 0.0) {
    dtnew = std::min(dtnew, std::sqrt(2.0*nropt.newton_cfl*dxmin*a/nw_gmax));
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonWriteHistory
//! \brief appends one record to <basename>.newton.hst.  With v = p/a the velocity
//! relative to the comoving coordinates and Phi/a the Newtonian potential:
//!   K = sum m v^2/2,   W = sum m Phi(x)/(2a)  (potential interpolated to the particles),
//!   W_mesh = int (rho - <rho>) Phi dV/(2a)    (mesh sum of the filtered density),
//!   C = a (K + W) + int K da,  constant in time (Layzer-Irvine; a = 1: the energy).
//! The second moment I_ij = sum m x_i x_j and its first and second time derivatives are
//! particle sums of the synchronised state; the third is the difference quotient of the
//! second over the last step and belongs to the time in the column after it.

void Particles::NrpicNewtonWriteHistory(Real time, int ncycle, bool header) {
  std::string fname = nr_basename + ".newton.hst";
  std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
  if (fp == nullptr) NewtonFatal("cannot open " + fname);
  if (header) {
    std::fprintf(fp, "# NRPIC Newtonian mode history\n");
    std::fprintf(fp, "# [1]=time [2]=ncycle [3]=a [4]=mass [5]=K [6]=W [7]=W_mesh "
                 "[8]=C [9]=int_K_da [10]=P_x [11]=P_y [12]=P_z [13]=L_x [14]=L_y "
                 "[15]=L_z [16]=X_x [17]=X_y [18]=X_z "
                 "[19]=I_xx [20]=I_xy [21]=I_xz [22]=I_yy [23]=I_yz [24]=I_zz "
                 "[25]=dI_xx [26]=dI_xy [27]=dI_xz [28]=dI_yy [29]=dI_yz [30]=dI_zz "
                 "[31]=d2I_xx [32]=d2I_xy [33]=d2I_xz [34]=d2I_yy [35]=d2I_yz "
                 "[36]=d2I_zz [37]=d3I_xx [38]=d3I_xy [39]=d3I_xz [40]=d3I_yy "
                 "[41]=d3I_yz [42]=d3I_zz "
                 "[43]=time_d3I [44]=Phi_min [45]=Phi_max [46]=p_max [47]=g_max "
                 "[48]=mg_defect [49]=dt [50]=mg_cycles\n");
  }
  const Real a = nw_a;
  const Real mass = nw_sum[NWS_M];
  const Real kin = 0.5*nw_sum[NWS_P2]/(a*a);
  const Real pot = 0.5*nw_sum[NWS_PHI]/a;
  const Real pot_mesh = 0.5*nw_mesh[0]/a;
  const Real cons = a*(kin + pot) + nw_li;
  std::fprintf(fp, "%.15e %d %.15e %.15e %.15e %.15e %.15e %.15e %.15e", time, ncycle,
               a, mass, kin, pot, pot_mesh, cons, nw_li);
  for (int n=0; n<6; ++n) { std::fprintf(fp, " %.15e", nw_sum[NWS_P+n]); }
  for (int n=0; n<3; ++n) {
    std::fprintf(fp, " %.15e", (mass > 0.0) ? nw_sum[NWS_X+n]/mass : 0.0);
  }
  for (int n=0; n<18; ++n) { std::fprintf(fp, " %.15e", nw_sum[NWS_I+n]); }
  for (int n=0; n<6; ++n) { std::fprintf(fp, " %.15e", nw_d3i[n]); }
  std::fprintf(fp, " %.15e %.15e %.15e %.15e %.15e %.15e %.15e %d\n", nw_d3i_time,
               nw_mesh[4], nw_mesh[5], nw_pmax, nw_gmax, nw_defect,
               (ncycle > 0) ? pmy_pack->pmesh->dt : 0.0, nw_ncycle);
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonWriteRestart
//! \brief writes the state of the Newtonian mode next to the particle restart file:
//!   8 bytes "NRPNWT01", 50 doubles (30 particle sums, time, a, Layzer-Irvine integral,
//!   6 third derivatives and their time, p_max, defect, 6 mesh sums, g_max, number of
//!   V cycles), 5 int64 (extents of the potential array), the potential including ghost
//!   cells

void Particles::NrpicNewtonWriteRestart(const std::string &fname) {
  std::FILE *fp = std::fopen(fname.c_str(), "wb");
  if (fp == nullptr) NewtonFatal("cannot open " + fname);
  const char magic[9] = "NRPNWT01";
  double s[kNewtonState];
  for (int n=0; n<NWS_N; ++n) { s[n] = nw_sum[n]; }
  s[30] = nw_time; s[31] = nw_a; s[32] = nw_li;
  for (int n=0; n<6; ++n) { s[33+n] = nw_d3i[n]; }
  s[39] = nw_d3i_time; s[40] = nw_pmax; s[41] = nw_defect;
  for (int n=0; n<6; ++n) { s[42+n] = nw_mesh[n]; }
  s[48] = nw_gmax;
  s[49] = static_cast<double>(nw_ncycle);
  std::fwrite(magic, 1, 8, fp);
  std::fwrite(s, sizeof(double), kNewtonState, fp);
  auto ph = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(),
                                                pmy_pack->pgrav->phi);
  std::int64_t dims[5];
  for (int d=0; d<5; ++d) { dims[d] = static_cast<std::int64_t>(ph.extent(d)); }
  std::fwrite(dims, sizeof(std::int64_t), 5, fp);
  std::fwrite(ph.data(), sizeof(double), ph.size(), fp);
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonReadRestart
//! \brief reads the file written by NrpicNewtonWriteRestart; the state is applied by
//! NrpicNewtonInitialize once the mesh arrays exist.  Without the file (a dump that was
//! not written in this mode) the potential is solved for and the diagnostic integrals
//! start again.

void Particles::NrpicNewtonReadRestart(const std::string &fname) {
  nw_state_restart.clear();
  nw_phi_restart.clear();
  std::FILE *fp = std::fopen(fname.c_str(), "rb");
  if (fp == nullptr) {
    if (global_variable::my_rank == 0) {
      std::cout << "NRPIC: no Newtonian restart state " << fname
                << "; the potential is solved for again" << std::endl;
    }
    return;
  }
  char magic[9] = {0};
  double s[kNewtonState];
  if (std::fread(magic, 1, 8, fp) != 8 || std::strncmp(magic, "NRPNWT01", 8) != 0) {
    NewtonFatal("bad magic in " + fname);
  }
  if (std::fread(s, sizeof(double), kNewtonState, fp) != kNewtonState ||
      std::fread(nw_phi_restart_dims, sizeof(std::int64_t), 5, fp) != 5) {
    NewtonFatal(fname + " is truncated");
  }
  size_t nt = 1;
  for (int d=0; d<5; ++d) { nt *= static_cast<size_t>(nw_phi_restart_dims[d]); }
  nw_phi_restart.resize(nt);
  if (std::fread(nw_phi_restart.data(), sizeof(double), nt, fp) != nt) {
    NewtonFatal(fname + " is truncated");
  }
  std::fclose(fp);
  nw_state_restart.assign(s, s + kNewtonState);
}

} // namespace particles
