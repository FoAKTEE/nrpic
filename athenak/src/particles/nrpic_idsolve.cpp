//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_idsolve.cpp
//! \brief Initial-data solver of the NRPIC particle module (<particles> id_solve = true):
//! the Hamiltonian constraint for the conformal factor, solved on the mesh of the run
//! with the matter sources that the module itself deposits.
//!
//! Slice: gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Abar_ij + (1/3) psi^4 delta_ij K.
//! The problem generator sets a trial state (conformally flat).  From it the solver
//! takes psi_t = (det gamma)^(1/12) and holds fixed
//!   K = gamma^ij K_ij,     Abar_ij = psi_t^2 (K_ij - (1/3) gamma_ij K),
//! and solves
//!   lap psi = -(1/8) psi^-7 Abar_ij Abar_ij + (1/12) psi^5 K^2 - 2 pi psi^5 E[psi],
//! where E[psi] is the energy density of the module for the metric psi^4 delta_ij:
//! deposit with the cloud of the run, division by sqrt(gamma), filter.  For particles
//! at rest in the slice and no filter psi^5 E = psi^-1 Etilde with Etilde the density
//! per coordinate volume.  Lapse and shift are not touched.
//!
//! Outer iteration (Newton with the seven-point Jacobian):
//!   F = residual, sigma = (7/8) psi^-8 Abar^2 + (5/12) psi^4 K^2 + 2 pi psi^4 E,
//!   (-lap_7 + sigma) d = F,  psi <- psi + d,
//! until max|F| <= id_tol times the largest sum of the absolute terms of the right side.
//! The residual is either the constraint monitor of the code (id_residual = code,
//! F = -(psi^5/8) H with H of Z4c::ADMConstraints: what the evolution sees at t = 0 is
//! driven to zero; the seven-point operator is then an approximate Jacobian) or the
//! seven-point stencil of the multigrid solver (id_residual = stencil).
//! Inner iteration: conjugate gradients for the symmetric positive operator
//! -lap_7 + sigma, preconditioned by the multigrid Poisson solver of the gravity module
//! (MGGravityDriver::SolvePoisson; <gravity> block with threshold = 0).  On a mesh
//! periodic in all directions the constant mode is preconditioned by 1/<sigma>.
//! Faces that are not periodic: psi - 1 and the corrections fall off as 1/r about the
//! centre of <gravity> mg_bc = robin (MGRobinFill in multigrid/multigrid.hpp).
//!
//! Called from NrpicStartup of a new run, between the creation of the particles and
//! NrpicInitializeSources; on exit the Z4c state holds the solved data.  A record of
//! the iteration goes to <basename>.idsolve.txt, with id_dump = true the fields go to
//! <basename>.idsolve.bin (docs/FORMATS.md).  Uniform meshes, single rank.
//! Design, tests and limits: tracks/core/interfaces/id_solver.md.

#include <algorithm>
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
#include "driver/driver.hpp"
#include "bvals/bvals.hpp"
#include "coordinates/adm.hpp"
#include "z4c/z4c.hpp"
#include "z4c/tmunu.hpp"
#include "gravity/gravity.hpp"
#include "gravity/mg_gravity.hpp"
#include "multigrid/multigrid.hpp"
#include "particles/particles.hpp"

namespace particles {

namespace {

void IdFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_idsolve.cpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

//! norms of one evaluation of the residual (sums are weighted with the cell volume)
struct IdNorms {
  Real fmax = 0.0, frms = 0.0;     // residual used by the iteration
  Real scale = 0.0;                // largest sum of the absolute terms of the right side
  Real hmax = 0.0, hrms = 0.0;     // constraint monitor of the code
  Real smax = 0.0, srms = 0.0;     // residual with the seven-point stencil
  Real psimin = 0.0, psimax = 0.0;
  Real sigmean = 0.0;              // mean of sigma
  Real vol = 0.0;                  // volume of the mesh
};

} // namespace

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicIdSolveInit
//! \brief reads the options of the initial-data solver; nothing is added to the input
//! parameters unless <particles> id_solve is present

void Particles::NrpicIdSolveInit(ParameterInput *pin) {
  ids.on = false;
  if (!pin->DoesParameterExist("particles", "id_solve")) return;
  ids.on = pin->GetBoolean("particles", "id_solve");
  if (!ids.on) return;
  Mesh *pm = pmy_pack->pmesh;
  if (nropt.metric != NrpicMetric::mesh || pmy_pack->pz4c == nullptr || nropt.newton) {
    IdFatal("<particles> id_solve requires metric = mesh and a <z4c> block");
  }
  if (!nropt.deposit) {
    IdFatal("<particles> id_solve requires deposit = true");
  }
  if (pm->multilevel) {
    IdFatal("<particles> id_solve is implemented on uniform meshes only");
  }
  if (!pin->DoesBlockExist("gravity")) {
    IdFatal("<particles> id_solve requires a <gravity> block for the Poisson solver "
            "(four_pi_G = 1, threshold = 0; mg_bc = robin unless the mesh is periodic)");
  }
  const std::string res = pin->GetOrAddString("particles", "id_residual", "code");
  if (res.compare("code") == 0) {
    ids.residual = 0;
  } else if (res.compare("stencil") == 0) {
    ids.residual = 1;
  } else {
    IdFatal("<particles> id_residual = '" + res + "' not recognized (code or stencil)");
  }
  const std::string ini = pin->GetOrAddString("particles", "id_psi_init", "trial");
  if (ini.compare("trial") == 0) {
    ids.psi_init = 0;
  } else if (ini.compare("one") == 0) {
    ids.psi_init = 1;
  } else {
    IdFatal("<particles> id_psi_init = '" + ini + "' not recognized (trial or one)");
  }
  ids.tol       = pin->GetOrAddReal("particles", "id_tol", 1.0e-10);
  ids.maxit     = pin->GetOrAddInteger("particles", "id_maxit", 60);
  ids.lin_tol   = pin->GetOrAddReal("particles", "id_lin_tol", 1.0e-3);
  ids.lin_maxit = pin->GetOrAddInteger("particles", "id_lin_maxit", 50);
  ids.mg_tol    = pin->GetOrAddReal("particles", "id_mg_tol", 1.0e-3);
  ids.dump      = pin->GetOrAddBoolean("particles", "id_dump", false);
  if (!(ids.tol > 0.0) || !(ids.lin_tol > 0.0) || !(ids.mg_tol > 0.0)) {
    IdFatal("<particles> id_tol, id_lin_tol and id_mg_tol must be positive");
  }
  // the vector equation for the correction of Abar_ij: read only if present
  if (pin->DoesParameterExist("particles", "id_vector")) {
    ids.vector = pin->GetBoolean("particles", "id_vector");
  }
  if (ids.vector && pin->DoesParameterExist("particles", "id_vector_residual")) {
    const std::string vr = pin->GetString("particles", "id_vector_residual");
    if (vr.compare("code") == 0) {
      ids.vec_residual = 0;
    } else if (vr.compare("stencil") == 0) {
      ids.vec_residual = 1;
    } else {
      IdFatal("<particles> id_vector_residual = '" + vr + "' not recognized (stencil or "
              "code)");
    }
  }
  // the vector part with the monitor as residual decays slowly near the Nyquist
  // wavenumber: its own tolerance, 1e-6 by default (stencil form: id_tol)
  if (ids.vector) {
    ids.vec_tol = (ids.vec_residual == 0) ? 1.0e-6 : ids.tol;
    if (pin->DoesParameterExist("particles", "id_vector_tol")) {
      ids.vec_tol = pin->GetReal("particles", "id_vector_tol");
    }
  }
  // ghost cells of psi and of the corrections
  pbval_ids = new MeshBoundaryValuesCC(pmy_pack, pin, false);
  pbval_ids->InitializeBuffers(1);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicSolveInitialData
//! \brief solves the Hamiltonian constraint for the conformal factor with the sources
//! of the particles and writes the solved data into the ADM and Z4c variables

void Particles::NrpicSolveInitialData() {
  if (!ids.on) return;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  z4c::Z4c *pz4c = pmy_pack->pz4c;
  gravity::Gravity *pg = pmy_pack->pgrav;
  if (pg == nullptr || pg->pmgd == nullptr) {
    IdFatal("the initial-data solver found no gravity module");
  }
  if (nw_driver == nullptr) {
    IdFatal("the initial-data solver has no driver for the Poisson solver");
  }
  if (pmy_pack->pscalar != nullptr) {
    IdFatal("<particles> id_solve does not include the sources of a scalar field");
  }
  MGGravityDriver *pmgd = pg->pmgd;
  if (pmgd->Threshold() != 0.0) {
    IdFatal("<particles> id_solve requires <gravity> threshold = 0 (the solver sets the "
            "defect at which the V cycles end)");
  }
  const bool periodic = pm->strictly_periodic;
  const bool robin = pmgd->IsRobin();
  if (!periodic && !robin) {
    IdFatal("<particles> id_solve on a mesh that is not periodic in all directions "
            "requires <gravity> mg_bc = robin");
  }

  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
  const int ng = indcs.ng;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int n1 = nx1 + 2*ng, n2 = nx2 + 2*ng, n3 = nx3 + 2*ng;
  const int nmb = pmy_pack->nmb_thispack;
  const int nmb1 = nmb - 1;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  auto mb_bcs = pmy_pack->pmb->mb_bcs.d_view;
  {
    // the seven-point operator of the multigrid solver assumes cubic cells
    auto szh = pmy_pack->pmb->mb_size.h_view;
    for (int m=0; m<nmb; ++m) {
      if (std::fabs(szh(m).dx1 - szh(m).dx2) > 1.0e-12*szh(m).dx1 ||
          std::fabs(szh(m).dx1 - szh(m).dx3) > 1.0e-12*szh(m).dx1) {
        IdFatal("<particles> id_solve requires cubic cells");
      }
    }
  }
  const Real xo = pmgd->RobinOrigin(0), yo = pmgd->RobinOrigin(1);
  const Real zo = pmgd->RobinOrigin(2);
  const bool use_code = (ids.residual == 0);
  const Real lambda = nropt.lambda;

  auto &adm = pmy_pack->padm->adm;
  auto &con = pz4c->con;
  auto tm = pmy_pack->ptmunu->u_tmunu;

  // ---- work arrays (released at the end of the function)
  DvceArray5D<Real> psi("ids_psi", nmb, 1, n3, n2, n1);     // conformal factor
  DvceArray5D<Real> ab("ids_abar", nmb, 6, n3, n2, n1);     // Abar_ij
  DvceArray4D<Real> trk("ids_trk", nmb, n3, n2, n1);        // K
  DvceArray4D<Real> a2("ids_a2", nmb, n3, n2, n1);          // Abar_ij Abar_ij
  DvceArray4D<Real> sig("ids_sig", nmb, n3, n2, n1);        // sigma
  DvceArray5D<Real> wk("ids_wk", nmb, 2, n3, n2, n1);       // stencil residual, scale
  DvceArray5D<Real> res("ids_res", nmb, 1, n3, n2, n1);     // residual F
  DvceArray5D<Real> del("ids_del", nmb, 1, n3, n2, n1);     // correction d
  DvceArray5D<Real> cr("ids_cr", nmb, 1, n3, n2, n1);       // conjugate gradients
  DvceArray5D<Real> cz("ids_cz", nmb, 1, n3, n2, n1);
  DvceArray5D<Real> czo("ids_czo", nmb, 1, n3, n2, n1);
  DvceArray5D<Real> cp("ids_cp", nmb, 1, n3, n2, n1);
  DvceArray5D<Real> cq("ids_cq", nmb, 1, n3, n2, n1);
  // vector equation (id_vector): W_i, its residual F_i, the right side s_i, L W
  const bool vec = ids.vector;
  DvceArray5D<Real> wv[3], fv[3], sv[3], lw, vt, vp;
  DvceArray4D<Real> vsc;
  if (vec) {
    for (int c=0; c<3; ++c) {
      wv[c] = DvceArray5D<Real>("ids_w", nmb, 1, n3, n2, n1);
      fv[c] = DvceArray5D<Real>("ids_fw", nmb, 1, n3, n2, n1);
      sv[c] = DvceArray5D<Real>("ids_sw", nmb, 1, n3, n2, n1);
    }
    lw = DvceArray5D<Real>("ids_lw", nmb, 6, n3, n2, n1);
    vt = DvceArray5D<Real>("ids_vt", nmb, 1, n3, n2, n1);
    vp = DvceArray5D<Real>("ids_vp", nmb, 1, n3, n2, n1);
    vsc = DvceArray4D<Real>("ids_vsc", nmb, n3, n2, n1);
  }

  // ---- trial state: psi, K, Abar_ij from the ADM variables of the problem generator
  pz4c->Z4cToADM(pmy_pack);
  Real nonflat = 0.0;
  Kokkos::parallel_reduce("ids_trial",
    Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>({0, 0, 0, 0}, {nmb, n3, n2, n1}),
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &lmax) {
    const Real gxx = adm.g_dd(m,0,0,k,j,i), gxy = adm.g_dd(m,0,1,k,j,i);
    const Real gxz = adm.g_dd(m,0,2,k,j,i), gyy = adm.g_dd(m,1,1,k,j,i);
    const Real gyz = adm.g_dd(m,1,2,k,j,i), gzz = adm.g_dd(m,2,2,k,j,i);
    const Real det = adm::SpatialDet(gxx, gxy, gxz, gyy, gyz, gzz);
    const bool active = (k >= ks && k <= ke && j >= js && j <= je && i >= is && i <= ie);
    if (!(det > 0.0) || !(det < 1.0e300)) {
      // only ghost cells at a face of the mesh may hold such values; they are not used
      psi(m,0,k,j,i) = 1.0;
      trk(m,k,j,i) = 0.0;
      a2(m,k,j,i) = 0.0;
      for (int v=0; v<6; ++v) { ab(m,v,k,j,i) = 0.0; }
      if (active) { lmax = fmax(lmax, 1.0); }
    } else {
      const Real p4 = cbrt(det);
      const Real p1 = sqrt(sqrt(p4));
      const Real p2 = p1*p1;
      const Real p6 = p4*p2;
      if (active) {
        const Real dev = (fabs(gxy) + fabs(gxz) + fabs(gyz) + fabs(gxx - p4)
                          + fabs(gyy - p4) + fabs(gzz - p4))/p4;
        lmax = fmax(lmax, dev);
      }
      const Real tk = (adm.vK_dd(m,0,0,k,j,i) + adm.vK_dd(m,1,1,k,j,i)
                       + adm.vK_dd(m,2,2,k,j,i))/p4;
      psi(m,0,k,j,i) = p1;
      trk(m,k,j,i) = tk;
      Real s2 = 0.0;
      int v = 0;
      for (int a=0; a<3; ++a) {
        for (int b=a; b<3; ++b) {
          const Real aij = p2*adm.vK_dd(m,a,b,k,j,i) - ((a == b) ? p6*tk/3.0 : 0.0);
          ab(m,v,k,j,i) = aij;
          s2 += ((a == b) ? 1.0 : 2.0)*aij*aij;
          ++v;
        }
      }
      a2(m,k,j,i) = s2;
    }
  }, Kokkos::Max<Real>(nonflat));
  if (nonflat > 1.0e-10) {
    IdFatal("<particles> id_solve requires a conformally flat trial metric (largest "
            "relative deviation " + std::to_string(nonflat) + ")");
  }
  if (ids.psi_init == 1) {
    Kokkos::deep_copy(psi, 1.0);
  }

  // ---- ghost cells of a field: exchange between MeshBlocks and across periodic faces,
  //      1/r fall-off of (field - off) at the other faces
  auto fill_ghost = [&](DvceArray5D<Real> &fld, const Real off) {
    (void) pbval_ids->InitRecv(1);
    (void) pbval_ids->PackAndSendCC(fld, ids_coarse);
    (void) pbval_ids->ClearSend();
    (void) pbval_ids->ClearRecv();
    (void) pbval_ids->RecvAndUnpackCC(fld, ids_coarse);
    if (!periodic) {
      auto ff = fld;
      Kokkos::parallel_for("ids_robin", Kokkos::RangePolicy<DevExeSpace>(0, nmb),
      KOKKOS_LAMBDA(const int m) {
        bool face[6];
        bool any = false;
        for (int f=0; f<6; ++f) {
          face[f] = (mb_bcs(m,f) != BoundaryFlag::block) &&
                    (mb_bcs(m,f) != BoundaryFlag::periodic);
          any = any || face[f];
        }
        if (any) {
          MGRobinFill(ff, m, 1, ng, nx1, nx2, nx3, sz(m).x1min - xo, sz(m).x2min - yo,
                      sz(m).x3min - zo, sz(m).dx1, sz(m).dx2, sz(m).dx3, face, off);
        }
      });
    }
  };

  // ---- (L W)_ij = d_i W_j + d_j W_i - (2/3) delta_ij d_k W_k with central differences,
  //      on every cell that has both neighbours (the outermost ghost layer copies the
  //      layer inside it; the constraint monitor reaches ng - 1 ghost layers only)
  auto compute_lw = [&]() {
    auto w0 = wv[0], w1 = wv[1], w2 = wv[2];
    auto l = lw;
    par_for("ids_lw", DevExeSpace(), 0, nmb1, 0, n3-1, 0, n2-1, 0, n1-1,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      const int ic = (i < 1) ? 1 : ((i > n1-2) ? n1-2 : i);
      const int jc = (j < 1) ? 1 : ((j > n2-2) ? n2-2 : j);
      const int kc = (k < 1) ? 1 : ((k > n3-2) ? n3-2 : k);
      const Real h1 = 0.5/sz(m).dx1, h2 = 0.5/sz(m).dx2, h3 = 0.5/sz(m).dx3;
      Real d[3][3];   // d[a][b] = d_a W_b
      d[0][0] = (w0(m,0,kc,jc,ic+1) - w0(m,0,kc,jc,ic-1))*h1;
      d[0][1] = (w1(m,0,kc,jc,ic+1) - w1(m,0,kc,jc,ic-1))*h1;
      d[0][2] = (w2(m,0,kc,jc,ic+1) - w2(m,0,kc,jc,ic-1))*h1;
      d[1][0] = (w0(m,0,kc,jc+1,ic) - w0(m,0,kc,jc-1,ic))*h2;
      d[1][1] = (w1(m,0,kc,jc+1,ic) - w1(m,0,kc,jc-1,ic))*h2;
      d[1][2] = (w2(m,0,kc,jc+1,ic) - w2(m,0,kc,jc-1,ic))*h2;
      d[2][0] = (w0(m,0,kc+1,jc,ic) - w0(m,0,kc-1,jc,ic))*h3;
      d[2][1] = (w1(m,0,kc+1,jc,ic) - w1(m,0,kc-1,jc,ic))*h3;
      d[2][2] = (w2(m,0,kc+1,jc,ic) - w2(m,0,kc-1,jc,ic))*h3;
      const Real dv3 = (d[0][0] + d[1][1] + d[2][2])*(2.0/3.0);
      int v = 0;
      for (int a=0; a<3; ++a) {
        for (int b=a; b<3; ++b) {
          l(m,v,k,j,i) = d[a][b] + d[b][a] - ((a == b) ? dv3 : 0.0);
          ++v;
        }
      }
    });
  };

  // ---- ADM variables of the current psi on all cells (with id_vector: Abar_ij of the
  //      trial plus L W, and Abar_ij Abar_ij from the sum)
  auto set_metric = [&]() {
    if (vec) { compute_lw(); }
    auto l = lw;
    par_for("ids_metric", DevExeSpace(), 0, nmb1, 0, n3-1, 0, n2-1, 0, n1-1,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      const Real p1 = psi(m,0,k,j,i);
      const Real p2 = p1*p1;
      const Real p4 = p2*p2;
      const Real tk3 = p4*trk(m,k,j,i)/3.0;
      adm.psi4(m,k,j,i) = p4;
      Real s2 = 0.0;
      int v = 0;
      for (int a=0; a<3; ++a) {
        for (int b=a; b<3; ++b) {
          adm.g_dd(m,a,b,k,j,i) = (a == b) ? p4 : 0.0;
          if (vec) {
            const Real aij = ab(m,v,k,j,i) + l(m,v,k,j,i);
            adm.vK_dd(m,a,b,k,j,i) = aij/p2 + ((a == b) ? tk3 : 0.0);
            s2 += ((a == b) ? 1.0 : 2.0)*aij*aij;
          } else {
            adm.vK_dd(m,a,b,k,j,i) = ab(m,v,k,j,i)/p2 + ((a == b) ? tk3 : 0.0);
          }
          ++v;
        }
      }
      if (vec) { a2(m,k,j,i) = s2; }
    });
  };

  // ---- residual of the current psi with the sources the module deposits for it
  auto evaluate = [&](IdNorms &nm) {
    set_metric();
    NrpicFillMetric(met1);
    if (nropt.interp_bspline) { NrpicSharpenMetric(met1, met1s); }
    // the calls of NrpicInitializeSources, so that the sources are those of the run
    e_prev_valid = false;
    tm_prev_valid = false;
    NrpicDepositSources();
    if (nropt.deposit_adaptive) {
      NrpicDepositSources();
    }
    NrpicFilterSources();
    NrpicAddLambda();
    switch (ng) {
      case 2: pz4c->ADMConstraints<2>(pmy_pack); break;
      case 3: pz4c->ADMConstraints<3>(pmy_pack); break;
      case 4: pz4c->ADMConstraints<4>(pmy_pack); break;
    }
    Real sf = 0.0, sh = 0.0, ss = 0.0, ssig = 0.0, svol = 0.0;
    Kokkos::parallel_reduce("ids_residual",
      Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
        {0, ks, js, is}, {nmb, ke+1, je+1, ie+1}),
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &lf, Real &lh,
                  Real &ls, Real &lsig, Real &lvol) {
      const Real p1 = psi(m,0,k,j,i);
      const Real p2 = p1*p1;
      const Real p4 = p2*p2;
      const Real p5 = p4*p1;
      const Real p7 = p5*p2;
      const Real en = tm(m,Tmunu::I_Tmunu_E,k,j,i);
      const Real t_m = 2.0*M_PI*p5*en;                      // matter term
      const Real t_k = p5*SQR(trk(m,k,j,i))/12.0;           // trace term
      const Real t_a = a2(m,k,j,i)/(8.0*p7);                // traceless term
      const Real lap = (psi(m,0,k,j,i+1) + psi(m,0,k,j,i-1) - 2.0*p1)/SQR(sz(m).dx1)
                     + (psi(m,0,k,j+1,i) + psi(m,0,k,j-1,i) - 2.0*p1)/SQR(sz(m).dx2)
                     + (psi(m,0,k+1,j,i) + psi(m,0,k-1,j,i) - 2.0*p1)/SQR(sz(m).dx3);
      const Real fst = lap + t_a - t_k + t_m;
      const Real hh = con.H(m,k,j,i);
      const Real fcode = -0.125*p5*hh;
      const Real ff = use_code ? fcode : fst;
      res(m,0,k,j,i) = ff;
      wk(m,0,k,j,i) = fst;
      wk(m,1,k,j,i) = fabs(t_m) + fabs(t_k) + fabs(t_a);
      // d(right side)/d psi; the vacuum energy lambda/(8 pi) is part of E
      const Real sg = (7.0*t_a + 5.0*t_k + t_m)/p1 - 1.5*lambda*p4;
      sig(m,k,j,i) = (sg > 0.0) ? sg : 0.0;
      const Real vol = sz(m).dx1*sz(m).dx2*sz(m).dx3;
      lf += ff*ff*vol;
      lh += hh*hh*vol;
      ls += fst*fst*vol;
      lsig += sig(m,k,j,i)*vol;
      lvol += vol;
    }, Kokkos::Sum<Real>(sf), Kokkos::Sum<Real>(sh), Kokkos::Sum<Real>(ss),
       Kokkos::Sum<Real>(ssig), Kokkos::Sum<Real>(svol));
    Real mf = 0.0, mh = 0.0, ms = 0.0, msc = 0.0, pmin = 0.0, pmax = 0.0;
    Kokkos::parallel_reduce("ids_resmax",
      Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
        {0, ks, js, is}, {nmb, ke+1, je+1, ie+1}),
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &lf, Real &lh,
                  Real &ls, Real &lsc, Real &lmin, Real &lmax) {
      lf = fmax(lf, fabs(res(m,0,k,j,i)));
      lh = fmax(lh, fabs(con.H(m,k,j,i)));
      ls = fmax(ls, fabs(wk(m,0,k,j,i)));
      lsc = fmax(lsc, wk(m,1,k,j,i));
      lmin = fmin(lmin, psi(m,0,k,j,i));
      lmax = fmax(lmax, psi(m,0,k,j,i));
    }, Kokkos::Max<Real>(mf), Kokkos::Max<Real>(mh), Kokkos::Max<Real>(ms),
       Kokkos::Max<Real>(msc), Kokkos::Min<Real>(pmin), Kokkos::Max<Real>(pmax));
    nm.vol = svol;
    nm.fmax = mf; nm.frms = std::sqrt(sf/svol);
    nm.hmax = mh; nm.hrms = std::sqrt(sh/svol);
    nm.smax = ms; nm.srms = std::sqrt(ss/svol);
    nm.scale = msc;
    nm.psimin = pmin; nm.psimax = pmax;
    nm.sigmean = ssig/svol;
  };

  // ---- volume-weighted sums over the active cells
  auto dot = [&](const DvceArray5D<Real> &a, const DvceArray5D<Real> &b) -> Real {
    Real s = 0.0;
    auto aa = a, bb = b;
    Kokkos::parallel_reduce("ids_dot",
      Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
        {0, ks, js, is}, {nmb, ke+1, je+1, ie+1}),
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &ls) {
      ls += aa(m,0,k,j,i)*bb(m,0,k,j,i)*sz(m).dx1*sz(m).dx2*sz(m).dx3;
    }, Kokkos::Sum<Real>(s));
    return s;
  };
  auto total = [&](const DvceArray5D<Real> &a) -> Real {
    Real s = 0.0;
    auto aa = a;
    Kokkos::parallel_reduce("ids_total",
      Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
        {0, ks, js, is}, {nmb, ke+1, je+1, ie+1}),
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &ls) {
      ls += aa(m,0,k,j,i)*sz(m).dx1*sz(m).dx2*sz(m).dx3;
    }, Kokkos::Sum<Real>(s));
    return s;
  };
  // y <- a y + b x on the active cells
  auto axpby = [&](DvceArray5D<Real> &y, const Real a, const DvceArray5D<Real> &x,
                   const Real b) {
    auto yy = y, xx = x;
    par_for("ids_axpby", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      yy(m,0,k,j,i) = a*yy(m,0,k,j,i) + b*xx(m,0,k,j,i);
    });
  };

  // ---- q = (-lap_7 + sigma) p; fills the ghost cells of p
  auto matvec = [&](DvceArray5D<Real> &p, DvceArray5D<Real> &q) {
    fill_ghost(p, 0.0);
    auto pp = p, qq = q;
    par_for("ids_matvec", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      const Real p0 = pp(m,0,k,j,i);
      const Real lap = (pp(m,0,k,j,i+1) + pp(m,0,k,j,i-1) - 2.0*p0)/SQR(sz(m).dx1)
                     + (pp(m,0,k,j+1,i) + pp(m,0,k,j-1,i) - 2.0*p0)/SQR(sz(m).dx2)
                     + (pp(m,0,k+1,j,i) + pp(m,0,k-1,j,i) - 2.0*p0)/SQR(sz(m).dx3);
      qq(m,0,k,j,i) = -lap + sig(m,k,j,i)*p0;
    });
  };

  // ---- z = M^-1 r: Poisson solve -lap z = r from a zero start; on a periodic mesh the
  //      mean of r is preconditioned by 1/<sigma>
  int ncycle_lin = 0;
  Real vol_mesh = 0.0, sigmean = 0.0;
  auto precond = [&](const DvceArray5D<Real> &r, DvceArray5D<Real> &z) {
    const Real s1 = total(r), s2 = dot(r, r);
    const Real mean = periodic ? s1/vol_mesh : 0.0;
    const Real var = s2/vol_mesh - mean*mean;
    const Real rms = std::sqrt((var > 0.0) ? var : 0.0);
    Kokkos::deep_copy(pg->phi, 0.0);
    if (rms > 0.0) {
      pmgd->SolvePoisson(nw_driver, r, 0, -1.0, ids.mg_tol*rms);
      ncycle_lin += pmgd->last_ncycle;
    }
    auto phi = pg->phi;
    auto zz = z;
    par_for("ids_precond", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      zz(m,0,k,j,i) = phi(m,0,k,j,i);
    });
    if (periodic) {
      const Real shift = mean/sigmean - total(z)/vol_mesh;
      par_for("ids_precond_mean", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
      KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
        zz(m,0,k,j,i) += shift;
      });
    }
  };

  // ---- vector equation (id_vector): residual of
  //        lap W_i + (1/3) d_i d_j W_j = 8 pi Stilde_i + (2/3) psi^6 d_i K - d_j Abar_ij(t)
  //      with the compact operator (seven-point Laplacian, three-point second and
  //      four-point mixed differences), right side with central differences;
  //      Stilde_i = psi^6 S_i of the deposit.  On a periodic mesh the mean of each
  //      component is removed (and reported).
  Real vmax = 0.0, vrms = 0.0, vscale = 0.0, vmean = 0.0, mmax = 0.0;
  const bool vec_code = (ids.vec_residual == 0);   // F_i = psi^6 M_i of the monitor
  auto evaluate_vector = [&]() {
    auto w0 = wv[0], w1 = wv[1], w2 = wv[2];
    auto f0 = fv[0], f1 = fv[1], f2 = fv[2];
    auto s0 = sv[0], s1 = sv[1], s2 = sv[2];
    auto sc = vsc;
    par_for("ids_vres", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      const Real dx = sz(m).dx1, dy = sz(m).dx2, dz = sz(m).dx3;
      const Real p2 = SQR(psi(m,0,k,j,i));
      const Real p6 = p2*p2*p2;
      const Real dk[3] = {(trk(m,k,j,i+1) - trk(m,k,j,i-1))/(2.0*dx),
                          (trk(m,k,j+1,i) - trk(m,k,j-1,i))/(2.0*dy),
                          (trk(m,k+1,j,i) - trk(m,k-1,j,i))/(2.0*dz)};
      // d_j Abar_ij of the trial; storage index of (a, b): 0 xx 1 xy 2 xz 3 yy 4 yz 5 zz
      const int ix[3][3] = {{0, 1, 2}, {1, 3, 4}, {2, 4, 5}};
      Real da[3];
      for (int a=0; a<3; ++a) {
        da[a] = (ab(m,ix[a][0],k,j,i+1) - ab(m,ix[a][0],k,j,i-1))/(2.0*dx)
              + (ab(m,ix[a][1],k,j+1,i) - ab(m,ix[a][1],k,j-1,i))/(2.0*dy)
              + (ab(m,ix[a][2],k+1,j,i) - ab(m,ix[a][2],k-1,j,i))/(2.0*dz);
      }
      // compact operator
      auto lap7 = [&](const DvceArray5D<Real> &w) -> Real {
        const Real c = w(m,0,k,j,i);
        return (w(m,0,k,j,i+1) + w(m,0,k,j,i-1) - 2.0*c)/(dx*dx)
             + (w(m,0,k,j+1,i) + w(m,0,k,j-1,i) - 2.0*c)/(dy*dy)
             + (w(m,0,k+1,j,i) + w(m,0,k-1,j,i) - 2.0*c)/(dz*dz);
      };
      const Real gd0 = (w0(m,0,k,j,i+1) + w0(m,0,k,j,i-1) - 2.0*w0(m,0,k,j,i))/(dx*dx)
        + (w1(m,0,k,j+1,i+1) - w1(m,0,k,j-1,i+1) - w1(m,0,k,j+1,i-1)
           + w1(m,0,k,j-1,i-1))/(4.0*dx*dy)
        + (w2(m,0,k+1,j,i+1) - w2(m,0,k-1,j,i+1) - w2(m,0,k+1,j,i-1)
           + w2(m,0,k-1,j,i-1))/(4.0*dx*dz);
      const Real gd1 = (w1(m,0,k,j+1,i) + w1(m,0,k,j-1,i) - 2.0*w1(m,0,k,j,i))/(dy*dy)
        + (w0(m,0,k,j+1,i+1) - w0(m,0,k,j+1,i-1) - w0(m,0,k,j-1,i+1)
           + w0(m,0,k,j-1,i-1))/(4.0*dx*dy)
        + (w2(m,0,k+1,j+1,i) - w2(m,0,k-1,j+1,i) - w2(m,0,k+1,j-1,i)
           + w2(m,0,k-1,j-1,i))/(4.0*dy*dz);
      const Real gd2 = (w2(m,0,k+1,j,i) + w2(m,0,k-1,j,i) - 2.0*w2(m,0,k,j,i))/(dz*dz)
        + (w0(m,0,k+1,j,i+1) - w0(m,0,k+1,j,i-1) - w0(m,0,k-1,j,i+1)
           + w0(m,0,k-1,j,i-1))/(4.0*dx*dz)
        + (w1(m,0,k+1,j+1,i) - w1(m,0,k+1,j-1,i) - w1(m,0,k-1,j+1,i)
           + w1(m,0,k-1,j-1,i))/(4.0*dy*dz);
      const Real lw3[3] = {lap7(w0) + gd0/3.0, lap7(w1) + gd1/3.0, lap7(w2) + gd2/3.0};
      Real smax = 0.0;
      for (int a=0; a<3; ++a) {
        const Real t_s = 8.0*M_PI*p6*tm(m,Tmunu::I_Tmunu_Sx + a,k,j,i);
        const Real t_k = (2.0/3.0)*p6*dk[a];
        const Real rhs = t_s + t_k - da[a];
        const Real f = vec_code ? p6*con.M_d(m,a,k,j,i) : lw3[a] - rhs;
        const Real sa = fabs(lw3[a] + da[a]) + fabs(t_k) + fabs(t_s);
        smax = fmax(smax, sa);
        if (a == 0) { f0(m,0,k,j,i) = f; s0(m,0,k,j,i) = rhs; }
        if (a == 1) { f1(m,0,k,j,i) = f; s1(m,0,k,j,i) = rhs; }
        if (a == 2) { f2(m,0,k,j,i) = f; s2(m,0,k,j,i) = rhs; }
      }
      sc(m,k,j,i) = smax;
    });
    vmean = 0.0;
    if (periodic) {
      Real mc[3];
      for (int c=0; c<3; ++c) {
        mc[c] = total(fv[c])/vol_mesh;
        vmean += SQR(mc[c]);
        auto ff = fv[c];
        const Real mm = mc[c];
        par_for("ids_vmean", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
        KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
          ff(m,0,k,j,i) -= mm;
        });
      }
      vmean = std::sqrt(vmean);
    }
    Real lmx = 0.0, lsq = 0.0, lsc = 0.0, lmm = 0.0;
    Kokkos::parallel_reduce("ids_vnorm",
      Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
        {0, ks, js, is}, {nmb, ke+1, je+1, ie+1}),
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &l1, Real &l2,
                  Real &l3, Real &l4) {
      const Real a0 = f0(m,0,k,j,i), a1 = f1(m,0,k,j,i), a2v = f2(m,0,k,j,i);
      l1 = fmax(l1, fmax(fabs(a0), fmax(fabs(a1), fabs(a2v))));
      l2 += (a0*a0 + a1*a1 + a2v*a2v)*sz(m).dx1*sz(m).dx2*sz(m).dx3;
      l3 = fmax(l3, sc(m,k,j,i));
      l4 = fmax(l4, sqrt(fabs(con.M(m,k,j,i))));
    }, Kokkos::Max<Real>(lmx), Kokkos::Sum<Real>(lsq), Kokkos::Max<Real>(lsc),
       Kokkos::Max<Real>(lmm));
    vmax = lmx;
    vrms = std::sqrt(lsq/vol_mesh);
    vscale = lsc;
    mmax = lmm;
  };

  // ---- one preconditioned Richardson step for W:
  //      W <- W - omega P^-1 F,  P^-1 F = lap^-1 [F - (1/4) grad lap^-1 div F]
  //      (the inverse of the continuum vector Laplacian; on a periodic mesh the
  //      eigenvalues of P^-1 times the compact operator lie in [1, 4/3]: omega = 6/7)
  int ncycle_vec = 0;
  auto poisson = [&](const DvceArray5D<Real> &r, const Real fac, DvceArray5D<Real> &z) {
    const Real s1 = total(r), s2 = dot(r, r);
    const Real mean = periodic ? s1/vol_mesh : 0.0;
    const Real var = s2/vol_mesh - mean*mean;
    const Real rms = std::sqrt((var > 0.0) ? var : 0.0);
    Kokkos::deep_copy(pg->phi, 0.0);
    if (rms > 0.0) {
      pmgd->SolvePoisson(nw_driver, r, 0, fac, ids.mg_tol*rms);
      ncycle_vec += pmgd->last_ncycle;
    }
    auto phi = pg->phi;
    auto zz = z;
    par_for("ids_vpois", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      zz(m,0,k,j,i) = phi(m,0,k,j,i);
    });
  };
  auto vector_step = [&]() {
    for (int c=0; c<3; ++c) { fill_ghost(fv[c], 0.0); }
    auto f0 = fv[0], f1 = fv[1], f2 = fv[2];
    auto t = vt;
    par_for("ids_vdiv", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      t(m,0,k,j,i) = (f0(m,0,k,j,i+1) - f0(m,0,k,j,i-1))/(2.0*sz(m).dx1)
                   + (f1(m,0,k,j+1,i) - f1(m,0,k,j-1,i))/(2.0*sz(m).dx2)
                   + (f2(m,0,k+1,j,i) - f2(m,0,k-1,j,i))/(2.0*sz(m).dx3);
    });
    poisson(vt, 1.0, vp);              // vp = lap^-1 div F
    fill_ghost(vp, 0.0);
    const Real omega = 6.0/7.0;
    for (int c=0; c<3; ++c) {
      auto fc = fv[c];
      auto p = vp;
      const int cc = c;
      par_for("ids_vq", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
      KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
        Real g;
        if (cc == 0) {
          g = (p(m,0,k,j,i+1) - p(m,0,k,j,i-1))/(2.0*sz(m).dx1);
        } else if (cc == 1) {
          g = (p(m,0,k,j+1,i) - p(m,0,k,j-1,i))/(2.0*sz(m).dx2);
        } else {
          g = (p(m,0,k+1,j,i) - p(m,0,k-1,j,i))/(2.0*sz(m).dx3);
        }
        t(m,0,k,j,i) = fc(m,0,k,j,i) - 0.25*g;
      });
      poisson(vt, -1.0, cz);           // cz = -lap^-1 q = -P^-1 F (component c)
      axpby(wv[c], 1.0, cz, omega);
      fill_ghost(wv[c], 0.0);
    }
  };

  // ---- record of the iteration
  const std::string flog = nr_basename + ".idsolve.txt";
  std::FILE *fl = std::fopen(flog.c_str(), "w");
  if (fl == nullptr) IdFatal("cannot open " + flog);
  std::fprintf(fl, "# NRPIC initial-data solve: id_residual = %s, id_tol = %.3e, "
               "id_lin_tol = %.3e, id_mg_tol = %.3e, id_psi_init = %s, faces = %s\n",
               use_code ? "code" : "stencil", ids.tol, ids.lin_tol, ids.mg_tol,
               (ids.psi_init == 1) ? "one" : "trial", periodic ? "periodic" : "robin");
  std::fprintf(fl, "# [1]=iter [2]=rel=max|F|/scale [3]=max|F| [4]=rms_F [5]=max|H| "
               "[6]=rms_H [7]=max|F7| [8]=rms_F7 [9]=psi_min [10]=psi_max [11]=cg_steps "
               "[12]=v_cycles [13]=lin_res\n");
  std::fprintf(fl, "# F: residual used (code: -(psi^5/8) H; stencil: F7), H: constraint "
               "monitor of the code, F7: seven-point residual; columns 11-13: the linear "
               "solve that followed\n");
  if (vec) {
    std::fprintf(fl, "# id_vector: [14]=relv=max|Fv|/scale_v [15]=max|Fv| [16]=rms_Fv "
                 "[17]=max|M| of the monitor [18]=|mean of Fv| removed (periodic) "
                 "[19]=v_cycles of the vector step that followed; Fv: residual of the "
                 "vector equation, %s; id_vector_tol = %.3e\n", vec_code ? "psi^6 M_i of "
                 "the constraint monitor (id_vector_residual = code)" : "stencil form",
                 ids.vec_tol);
  }

  std::vector<double> h_before;      // constraint monitor of the first evaluation
  auto to_host = [&](const int kind, std::vector<double> &out) {
    // kind 0: psi, 1: K, 2: Abar^2, 3: E, 4: H, 5: seven-point residual
    const std::int64_t g1 = pm->mesh_indcs.nx1, g2 = pm->mesh_indcs.nx2;
    const std::int64_t g3 = pm->mesh_indcs.nx3;
    out.assign(static_cast<size_t>(g1)*g2*g3, 0.0);
    auto szh = pmy_pack->pmb->mb_size.h_view;
    const Real d1 = (pm->mesh_size.x1max - pm->mesh_size.x1min)/static_cast<Real>(g1);
    const Real d2 = (pm->mesh_size.x2max - pm->mesh_size.x2min)/static_cast<Real>(g2);
    const Real d3 = (pm->mesh_size.x3max - pm->mesh_size.x3min)/static_cast<Real>(g3);
    auto psih = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), psi);
    auto trkh = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), trk);
    auto a2h = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), a2);
    auto tmh = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), tm);
    auto conh = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), pz4c->u_con);
    auto wkh = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), wk);
    for (int m=0; m<nmb; ++m) {
      const std::int64_t i0 = static_cast<std::int64_t>(
          std::floor((szh(m).x1min - pm->mesh_size.x1min)/d1 + 0.5));
      const std::int64_t j0 = static_cast<std::int64_t>(
          std::floor((szh(m).x2min - pm->mesh_size.x2min)/d2 + 0.5));
      const std::int64_t k0 = static_cast<std::int64_t>(
          std::floor((szh(m).x3min - pm->mesh_size.x3min)/d3 + 0.5));
      for (int k=0; k<nx3; ++k) {
        for (int j=0; j<nx2; ++j) {
          for (int i=0; i<nx1; ++i) {
            const size_t idx = (static_cast<size_t>(k0 + k)*g2 + (j0 + j))*g1 + (i0 + i);
            double v = 0.0;
            switch (kind) {
              case 0: v = psih(m,0,ks+k,js+j,is+i); break;
              case 1: v = trkh(m,ks+k,js+j,is+i); break;
              case 2: v = a2h(m,ks+k,js+j,is+i); break;
              case 3: v = tmh(m,Tmunu::I_Tmunu_E,ks+k,js+j,is+i); break;
              case 4: v = conh(m,z4c::Z4c::I_CON_H,ks+k,js+j,is+i); break;
              default: v = wkh(m,0,ks+k,js+j,is+i); break;
            }
            out[idx] = v;
          }
        }
      }
    }
  };

  // active cells of component comp of a cell-centred array, as one array on the mesh
  // (first index fastest), for the dump of the vector equation
  std::vector<double> m_before[3];   // monitor M_i of the first evaluation
  auto to_host5 = [&](const DvceArray5D<Real> &arr, const int comp,
                      std::vector<double> &out) {
    const std::int64_t g1 = pm->mesh_indcs.nx1, g2 = pm->mesh_indcs.nx2;
    const std::int64_t g3 = pm->mesh_indcs.nx3;
    out.assign(static_cast<size_t>(g1)*g2*g3, 0.0);
    auto szh = pmy_pack->pmb->mb_size.h_view;
    const Real d1 = (pm->mesh_size.x1max - pm->mesh_size.x1min)/static_cast<Real>(g1);
    const Real d2 = (pm->mesh_size.x2max - pm->mesh_size.x2min)/static_cast<Real>(g2);
    const Real d3 = (pm->mesh_size.x3max - pm->mesh_size.x3min)/static_cast<Real>(g3);
    auto h = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), arr);
    for (int m=0; m<nmb; ++m) {
      const std::int64_t i0 = static_cast<std::int64_t>(
          std::floor((szh(m).x1min - pm->mesh_size.x1min)/d1 + 0.5));
      const std::int64_t j0 = static_cast<std::int64_t>(
          std::floor((szh(m).x2min - pm->mesh_size.x2min)/d2 + 0.5));
      const std::int64_t k0 = static_cast<std::int64_t>(
          std::floor((szh(m).x3min - pm->mesh_size.x3min)/d3 + 0.5));
      for (int k=0; k<nx3; ++k) {
        for (int j=0; j<nx2; ++j) {
          for (int i=0; i<nx1; ++i) {
            const size_t idx = (static_cast<size_t>(k0 + k)*g2 + (j0 + j))*g1 + (i0 + i);
            out[idx] = h(m,comp,ks+k,js+j,is+i);
          }
        }
      }
    }
  };

  // ---- outer iteration
  // MeshBlock ownership of the particles, as NrpicInitializeSources does before its
  // deposit (it repeats these calls afterwards, then without effect)
  NrpicAssignBlocks();
  NrpicRemoveFlagged();
  fill_ghost(psi, 1.0);
  IdNorms nm, nm0;
  bool converged = false;
  int iter = 0;
  int cg_total = 0, cyc_total = 0;
  Real relv = 0.0, relv0 = 0.0, mmax0 = 0.0;
  int cyc_total_vec = 0;
  std::vector<Real> relv_hist;       // vector residual per outer iteration
  bool vstalled = false;             // id_vector_residual = code: the residual stalled
  bool vfrozen = false;              // id_vector_residual = code: W no longer updated
  for (iter = 0; ; ++iter) {
    evaluate(nm);
    vol_mesh = nm.vol;
    sigmean = nm.sigmean;
    if (vec) {
      evaluate_vector();
      relv = (vscale > 0.0) ? vmax/vscale : vmax;
      relv_hist.push_back(relv);
    }
    if (iter == 0) {
      nm0 = nm;
      if (ids.dump) { to_host(4, h_before); }
      if (vec) {
        relv0 = relv;
        mmax0 = mmax;
        if (ids.dump) {
          for (int c=0; c<3; ++c) {
            to_host5(pz4c->u_con, z4c::Z4c::I_CON_MX + c, m_before[c]);
          }
        }
      }
    }
    const Real rel = (nm.scale > 0.0) ? nm.fmax/nm.scale : nm.fmax;
    if (!(rel == rel) || !(relv == relv) || !(nm.psimin > 0.0)) {
      std::fclose(fl);
      IdFatal("the initial-data solve produced a non-finite residual or psi <= 0 in "
              "iteration " + std::to_string(iter));
    }
    int cg_steps = 0;
    Real lin_res = 0.0;
    ncycle_lin = 0;
    ncycle_vec = 0;
    // with the monitor as vector residual (id_vector_residual = code) the slowest modes
    // decay slowly and those at the Nyquist wavenumber not at all (first differences of
    // first differences): W is frozen once its residual is at id_vector_tol, or when it
    // fell by less than a factor 2 over the last ten outer iterations ("stalled"); the
    // scalar part then converges with the frozen W
    if (vec && vec_code && !vfrozen) {
      if (relv <= ids.vec_tol) {
        vfrozen = true;
      } else if (iter >= 10 && relv_hist[iter-10] < 2.0*relv) {
        vfrozen = true;
        vstalled = true;
      }
    }
    if (rel <= ids.tol && (!vec || (vec_code ? vfrozen : relv <= ids.vec_tol))) {
      converged = true;
    } else if (iter < ids.maxit) {
      if (periodic && !(sigmean > 0.0)) {
        std::fclose(fl);
        IdFatal("the initial-data solve on a periodic mesh needs K or matter (the "
                "linearised operator has a zero mode)");
      }
      // conjugate gradients for (-lap_7 + sigma) d = F with the Poisson solve as
      // preconditioner; Polak-Ribiere update (the preconditioner is a multigrid solve
      // to a tolerance, not exactly the same linear operator in every application)
      Kokkos::deep_copy(del, 0.0);
      Kokkos::deep_copy(cr, res);
      const Real bnorm = std::sqrt(dot(cr, cr));
      precond(cr, cz);
      Kokkos::deep_copy(cp, cz);
      Real rz = dot(cr, cz);
      Real rnorm = bnorm;
      while (cg_steps < ids.lin_maxit) {
        matvec(cp, cq);
        const Real pq = dot(cp, cq);
        if (!(pq > 0.0)) break;
        const Real alpha = rz/pq;
        axpby(del, 1.0, cp, alpha);
        axpby(cr, 1.0, cq, -alpha);
        ++cg_steps;
        rnorm = std::sqrt(dot(cr, cr));
        if (rnorm <= ids.lin_tol*bnorm) break;
        Kokkos::deep_copy(czo, cz);
        precond(cr, cz);
        const Real rz_new = dot(cr, cz);
        const Real beta = (rz_new - dot(cr, czo))/rz;
        rz = rz_new;
        axpby(cp, (beta > 0.0) ? beta : 0.0, cz, 1.0);
      }
      lin_res = (bnorm > 0.0) ? rnorm/bnorm : 0.0;
      cg_total += cg_steps;
      cyc_total += ncycle_lin;
      if (vec && !vfrozen) {
        vector_step();
        cyc_total_vec += ncycle_vec;
      }
    }
    std::fprintf(fl, "%4d %.6e %.6e %.6e %.6e %.6e %.6e %.6e %.15e %.15e %3d %4d %.3e",
                 iter, rel, nm.fmax, nm.frms, nm.hmax, nm.hrms, nm.smax, nm.srms,
                 nm.psimin, nm.psimax, cg_steps, ncycle_lin, lin_res);
    if (vec) {
      std::fprintf(fl, " %.6e %.6e %.6e %.6e %.6e %4d", relv, vmax, vrms, mmax, vmean,
                   ncycle_vec);
    }
    std::fprintf(fl, "\n");
    std::fflush(fl);
    if (converged || iter >= ids.maxit) break;

    // psi <- psi + d, halved until psi stays positive
    Real step = 1.0;
    for (int tries=0; tries<30; ++tries) {
      Real pmin = 0.0;
      const Real st = step;
      Kokkos::parallel_reduce("ids_psimin",
        Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
          {0, ks, js, is}, {nmb, ke+1, je+1, ie+1}),
      KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &lmin) {
        lmin = fmin(lmin, psi(m,0,k,j,i) + st*del(m,0,k,j,i));
      }, Kokkos::Min<Real>(pmin));
      if (pmin > 0.0) break;
      step *= 0.5;
    }
    axpby(psi, 1.0, del, step);
    fill_ghost(psi, 1.0);
  }

  if (ids.dump) {
    // <basename>.idsolve.bin: 8 bytes "NRIDSOL1", 3 int64 (n1, n2, n3), 6 doubles (x1min,
    // x1max, x2min, x2max, x3min, x3max), int64 number of fields (7), then the fields as
    // n3*n2*n1 doubles each, first index fastest: psi, K, Abar_ij Abar_ij, E, H of the
    // constraint monitor at the last evaluation, the seven-point residual there, H of
    // the monitor at the first evaluation
    const std::string fname = nr_basename + ".idsolve.bin";
    std::FILE *fp = std::fopen(fname.c_str(), "wb");
    if (fp == nullptr) IdFatal("cannot open " + fname);
    const std::int64_t dims[3] = {pm->mesh_indcs.nx1, pm->mesh_indcs.nx2,
                                  pm->mesh_indcs.nx3};
    const double box[6] = {pm->mesh_size.x1min, pm->mesh_size.x1max, pm->mesh_size.x2min,
                           pm->mesh_size.x2max, pm->mesh_size.x3min, pm->mesh_size.x3max};
    const std::int64_t nfld = 7;
    std::fwrite("NRIDSOL1", 1, 8, fp);
    std::fwrite(dims, sizeof(std::int64_t), 3, fp);
    std::fwrite(box, sizeof(double), 6, fp);
    std::fwrite(&nfld, sizeof(std::int64_t), 1, fp);
    std::vector<double> buf;
    for (int kind=0; kind<6; ++kind) {
      to_host(kind, buf);
      std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
    }
    std::fwrite(h_before.data(), sizeof(double), h_before.size(), fp);
    std::fclose(fp);
  }
  if (ids.dump && vec) {
    // <basename>.idvector.bin: 8 bytes "NRIDVEC1", then the header of .idsolve.bin and
    // 15 fields: W_i (3), right side s_i of the vector equation (3), its residual F_i in
    // stencil form (3, mean removed on a periodic mesh), M_i of the constraint monitor
    // at the last evaluation (3) and at the first (3)
    const std::string fname = nr_basename + ".idvector.bin";
    std::FILE *fp = std::fopen(fname.c_str(), "wb");
    if (fp == nullptr) IdFatal("cannot open " + fname);
    const std::int64_t dims[3] = {pm->mesh_indcs.nx1, pm->mesh_indcs.nx2,
                                  pm->mesh_indcs.nx3};
    const double box[6] = {pm->mesh_size.x1min, pm->mesh_size.x1max, pm->mesh_size.x2min,
                           pm->mesh_size.x2max, pm->mesh_size.x3min, pm->mesh_size.x3max};
    const std::int64_t nfld = 15;
    std::fwrite("NRIDVEC1", 1, 8, fp);
    std::fwrite(dims, sizeof(std::int64_t), 3, fp);
    std::fwrite(box, sizeof(double), 6, fp);
    std::fwrite(&nfld, sizeof(std::int64_t), 1, fp);
    std::vector<double> buf;
    for (int c=0; c<3; ++c) {
      to_host5(wv[c], 0, buf);
      std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
    }
    for (int c=0; c<3; ++c) {
      to_host5(sv[c], 0, buf);
      std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
    }
    for (int c=0; c<3; ++c) {
      to_host5(fv[c], 0, buf);
      std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
    }
    for (int c=0; c<3; ++c) {
      to_host5(pz4c->u_con, z4c::Z4c::I_CON_MX + c, buf);
      std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
    }
    for (int c=0; c<3; ++c) {
      std::fwrite(m_before[c].data(), sizeof(double), m_before[c].size(), fp);
    }
    std::fclose(fp);
  }

  std::fprintf(fl, "# %s after %d iteration(s), %d conjugate-gradient steps, %d V cycles; "
               "max|H| %.6e -> %.6e, rms H %.6e -> %.6e, psi in [%.12f, %.12f]\n",
               converged ? "converged" : "NOT CONVERGED", iter, cg_total, cyc_total,
               nm0.hmax, nm.hmax, nm0.hrms, nm.hrms, nm.psimin, nm.psimax);
  if (vec) {
    std::fprintf(fl, "# vector equation: relative residual %.6e -> %.6e%s, %d V cycles; "
                 "max|M| of the monitor %.6e -> %.6e\n", relv0, relv,
                 vstalled ? " (stalled)" : "", cyc_total_vec, mmax0, mmax);
  }
  std::fclose(fl);
  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC: initial-data solve (" << (use_code ? "code" : "stencil")
              << " residual) " << (converged ? "converged" : "did NOT converge")
              << " after " << iter << " iteration(s), " << cg_total
              << " conjugate-gradient steps, " << cyc_total << " V cycles; max|H| "
              << nm0.hmax << " -> " << nm.hmax << ", psi in [" << nm.psimin << ", "
              << nm.psimax << "]" << std::endl;
    if (vec) {
      std::cout << "NRPIC: vector equation: relative residual " << relv0 << " -> " << relv
                << (vstalled ? " (stalled)" : "") << ", " << cyc_total_vec
                << " V cycles; max|M| of the monitor " << mmax0
                << " -> " << mmax << std::endl;
    }
  }
  if (!converged) {
    IdFatal("the initial-data solve did not reach id_tol in id_maxit iterations (record "
            "in " + flog + ")");
  }

  // ---- hand the solved data to the spacetime solver: the ADM variables are those of
  //      the last evaluation; Z4c variables from them, then their ghost cells as at
  //      start-up (Driver::InitBoundaryValuesAndPrimitives)
  switch (ng) {
    case 2: pz4c->ADMToZ4c<2>(pmy_pack, nullptr); break;
    case 3: pz4c->ADMToZ4c<3>(pmy_pack, nullptr); break;
    case 4: pz4c->ADMToZ4c<4>(pmy_pack, nullptr); break;
  }
  (void) pz4c->RestrictU(nw_driver, 0);
  (void) pz4c->InitRecv(nw_driver, -1);
  (void) pz4c->SendU(nw_driver, 0);
  (void) pz4c->ClearSend(nw_driver, -1);
  (void) pz4c->ClearRecv(nw_driver, -1);
  (void) pz4c->RecvU(nw_driver, 0);
  (void) pz4c->Z4cBoundaryRHS(nw_driver, 0);
  (void) pz4c->Prolongate(nw_driver, 0);
  (void) pz4c->ApplyPhysicalBCs(nw_driver, 0);
}

} // namespace particles
