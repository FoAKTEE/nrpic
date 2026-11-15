//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file scalar_field.cpp
//! \brief constructor of the ScalarField class and its tasks in the numerical-relativity
//! task list.
//!
//! One stage of the time integrator (names of the tasks in brackets):
//!   [SF_CopyU]     register u1, as for the spacetime variables
//!   [SF_CalcRHS]   stochastic fields of the stage (if on), right-hand side of phi and Pi
//!                  from the field and the Z4c state of the stage
//!   [SF_SetTmunu]  E, S_i, S_ij of the field plus the sources of the other matter
//!                  modules into Tmunu::tmunu_tot; Z4c_CalcRHS waits for it
//!   [SF_Kick]      stochastic sources of Khat and At_ij, after Z4c_CalcRHS; Z4c_ExplRK
//!                  waits for it, so the spacetime is not advanced before the field has
//!                  read it
//!   [SF_ExplRK]    update, then restriction, exchange, prolongation, boundary conditions
//! After the last stage the constraints are evaluated with the sources of the new state
//! (hook in Z4c::ADMConstraints), and Diagnostics writes the history and the dumps.

#include <algorithm>
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
#include "bvals/bvals.hpp"
#include "tasklist/numerical_relativity.hpp"
#include "z4c/z4c.hpp"
#include "z4c/tmunu.hpp"
#include "scalar_field/scalar_field.hpp"

namespace scalarfield {

char const * const ScalarField::SF_names[ScalarField::nsf] = {"sf_phi", "sf_Pi"};

namespace {
void SfFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in scalar_field.cpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}
} // namespace

//----------------------------------------------------------------------------------------
// constructor: options, potential, memory, boundary buffers

ScalarField::ScalarField(MeshBlockPack *ppack, ParameterInput *pin) :
  u0("u0 sf",1,1,1,1,1),
  u1("u1 sf",1,1,1,1,1),
  u_rhs("u_rhs sf",1,1,1,1,1),
  coarse_u0("coarse u0 sf",1,1,1,1,1),
  pot_tab("sf_pot_tab",1,1),
  pmy_pack(ppack) {
  Mesh *pm = pmy_pack->pmesh;
  if (pmy_pack->pz4c == nullptr) {
    SfFatal("<scalar_field> requires a <z4c> block (with <scalar_field> couple = false "
            "the spacetime is a test background)");
  }
  if (!(pm->three_d)) { SfFatal("<scalar_field> requires a 3D mesh"); }
  if (global_variable::nranks > 1) {
    SfFatal("<scalar_field>: the diagnostics and the stochastic sources run on a single "
            "MPI rank");
  }
  if (pm->adaptive) {
    SfFatal("<scalar_field>: adaptive mesh refinement is not supported (uniform and "
            "statically refined meshes are)");
  }

  // ---- options
  opt.couple = pin->GetOrAddBoolean("scalar_field", "couple", true);
  opt.diss = pin->GetOrAddReal("scalar_field", "diss", pmy_pack->pz4c->opt.diss);
  opt.hist_dcycle = pin->GetOrAddInteger("scalar_field", "hist_dcycle", 1);
  opt.dump_dcycle = pin->GetOrAddInteger("scalar_field", "dump_dcycle", 0);
  opt.dump_dt = pin->GetOrAddReal("scalar_field", "dump_dt", -1.0);
  basename = pin->GetString("job", "basename");
  auto &indcs = pm->mb_indcs;
  diss = opt.diss*pow(2., -2.*indcs.ng)*(indcs.ng % 2 == 0 ? -1. : 1.);

  // ---- potential
  {
    const std::string name = pin->GetOrAddString("scalar_field", "potential",
                                                 "quadratic");
    const Real mass = pin->GetOrAddReal("scalar_field", "mass", 0.0);
    pot.m2 = mass*mass;
    pot.lambda = pin->GetOrAddReal("scalar_field", "lambda", 0.0);
    pot.v0 = pin->GetOrAddReal("scalar_field", "v0", 0.0);
    pot.mu = pin->GetOrAddReal("scalar_field", "mu", 1.0);
    pot.vev = pin->GetOrAddReal("scalar_field", "vev", 1.0);
    pot.offset = pin->GetOrAddReal("scalar_field", "v_offset", 0.0);
    if (name.compare("quadratic") == 0) {
      pot.kind = kPotQuadratic;
    } else if (name.compare("quartic") == 0) {
      pot.kind = kPotQuartic;
    } else if (name.compare("plateau") == 0) {
      pot.kind = kPotPlateau;
    } else if (name.compare("inflection") == 0) {
      pot.kind = kPotInflection;
    } else if (name.compare("table") == 0) {
      pot.kind = kPotTable;
      // text file: lines "phi V dV/dphi", equally spaced in phi; '#' starts a comment
      const std::string fname = pin->GetString("scalar_field", "table_file");
      std::FILE *fp = std::fopen(fname.c_str(), "r");
      if (fp == nullptr) { SfFatal("cannot open the potential table " + fname); }
      std::vector<double> tp, tv, td;
      char line[512];
      while (std::fgets(line, sizeof(line), fp) != nullptr) {
        double a, b, c;
        if (line[0] == '#') continue;
        if (std::sscanf(line, "%lf %lf %lf", &a, &b, &c) == 3) {
          tp.push_back(a); tv.push_back(b); td.push_back(c);
        }
      }
      std::fclose(fp);
      const int nt = static_cast<int>(tp.size());
      if (nt < 2) { SfFatal("the potential table " + fname + " has fewer than 2 rows"); }
      const double dp = (tp[nt-1] - tp[0])/static_cast<double>(nt - 1);
      for (int n=0; n<nt; ++n) {
        if (std::fabs(tp[n] - (tp[0] + n*dp)) > 1.0e-9*std::fabs(dp)) {
          SfFatal("the potential table " + fname + " is not equally spaced in phi");
        }
      }
      pot.ntab = nt;
      pot.tab_min = tp[0];
      pot.tab_dphi = dp;
      Kokkos::realloc(pot_tab, 2, nt);
      for (int n=0; n<nt; ++n) {
        pot_tab.h_view(0,n) = tv[n];
        pot_tab.h_view(1,n) = td[n];
      }
      pot_tab.template modify<HostMemSpace>();
      pot_tab.template sync<DevExeSpace>();
    } else {
      SfFatal("<scalar_field> potential = '" + name + "' not recognized (quadratic, "
              "quartic, plateau, inflection, table)");
    }
  }

  // ---- memory
  int nmb = std::max((ppack->nmb_thispack), (pm->nmb_maxperrank));
  {
    int ncells1 = indcs.nx1 + 2*(indcs.ng);
    int ncells2 = indcs.nx2 + 2*(indcs.ng);
    int ncells3 = indcs.nx3 + 2*(indcs.ng);
    Kokkos::realloc(u0,    nmb, (nsf), ncells3, ncells2, ncells1);
    Kokkos::realloc(u1,    nmb, (nsf), ncells3, ncells2, ncells1);
    Kokkos::realloc(u_rhs, nmb, (nsf), ncells3, ncells2, ncells1);
    sf.phi.InitWithShallowSlice(u0, I_SF_PHI);
    sf.vPi.InitWithShallowSlice(u0, I_SF_PI);
    rhs.phi.InitWithShallowSlice(u_rhs, I_SF_PHI);
    rhs.vPi.InitWithShallowSlice(u_rhs, I_SF_PI);
  }
  if (pm->multilevel) {
    int nccells1 = indcs.cnx1 + 2*(indcs.ng);
    int nccells2 = indcs.cnx2 + 2*(indcs.ng);
    int nccells3 = indcs.cnx3 + 2*(indcs.ng);
    Kokkos::realloc(coarse_u0, nmb, (nsf), nccells3, nccells2, nccells1);
  }

  // boundary buffers: the Z4c flavour (same restriction, prolongation and exchange of
  // the coarse arrays as the spacetime variables)
  pbval_u = new MeshBoundaryValuesCC(ppack, pin, true);
  pbval_u->InitializeBuffers((nsf));

  NoiseInit(pin);
}

//----------------------------------------------------------------------------------------
// destructor

ScalarField::~ScalarField() {
  delete pbval_u;
}

//----------------------------------------------------------------------------------------
//! \fn  void ScalarField::QueueTasks
//! \brief queues the tasks of the scalar field into NumericalRelativity

void ScalarField::QueueTasks() {
  using namespace numrel;  // NOLINT(build/namespaces)
  NumericalRelativity *pnr = pmy_pack->pnr;

  // Start task list
  pnr->QueueTask(&ScalarField::InitRecv, this, SF_Recv, "SF_Recv", Task_Start);

  // Run task list
  pnr->QueueTask(&ScalarField::CopyU, this, SF_CopyU, "SF_CopyU", Task_Run);
  pnr->QueueTask(&ScalarField::CalcRHS_, this, SF_CalcRHS, "SF_CalcRHS", Task_Run,
                 {SF_CopyU});
  pnr->QueueTask(&ScalarField::SetTmunu, this, SF_SetTmunu, "SF_SetTmunu", Task_Run,
                 {SF_CopyU}, {MHD_SetTmunu});
  pnr->QueueTask(&ScalarField::Kick, this, SF_Kick, "SF_Kick", Task_Run,
                 {SF_CalcRHS, Z4c_CalcRHS});
  pnr->QueueTask(&ScalarField::ExpRKUpdate, this, SF_ExplRK, "SF_ExplRK", Task_Run,
                 {SF_Kick, SF_SetTmunu});
  pnr->QueueTask(&ScalarField::RestrictU, this, SF_RestU, "SF_RestU", Task_Run,
                 {SF_ExplRK});
  pnr->QueueTask(&ScalarField::SendU, this, SF_SendU, "SF_SendU", Task_Run, {SF_RestU});
  pnr->QueueTask(&ScalarField::RecvU, this, SF_RecvU, "SF_RecvU", Task_Run, {SF_SendU});
  pnr->QueueTask(&ScalarField::Prolongate, this, SF_Prolong, "SF_Prolong", Task_Run,
                 {SF_RecvU});
  pnr->QueueTask(&ScalarField::ApplyPhysicalBCs, this, SF_BCS, "SF_BCS", Task_Run,
                 {SF_Prolong});

  // End task list
  pnr->QueueTask(&ScalarField::ClearSend, this, SF_ClearS, "SF_ClearS", Task_End);
  pnr->QueueTask(&ScalarField::ClearRecv, this, SF_ClearR, "SF_ClearR", Task_End,
                 {SF_ClearS});
}

//----------------------------------------------------------------------------------------
// communication tasks (as for the spacetime variables, z4c_tasks.cpp)

TaskStatus ScalarField::InitRecv(Driver *pdrive, int stage) {
  return pbval_u->InitRecv(nsf);
}

TaskStatus ScalarField::ClearRecv(Driver *pdrive, int stage) {
  return pbval_u->ClearRecv();
}

TaskStatus ScalarField::ClearSend(Driver *pdrive, int stage) {
  return pbval_u->ClearSend();
}

TaskStatus ScalarField::SendU(Driver *pdrive, int stage) {
  return pbval_u->PackAndSendCC(u0, coarse_u0);
}

TaskStatus ScalarField::RecvU(Driver *pdrive, int stage) {
  return pbval_u->RecvAndUnpackCC(u0, coarse_u0);
}

TaskStatus ScalarField::RestrictU(Driver *pdrive, int stage) {
  if (pmy_pack->pmesh->multilevel) {
    pmy_pack->pmesh->pmr->RestrictCC(u0, coarse_u0, true);
  }
  return TaskStatus::complete;
}

TaskStatus ScalarField::Prolongate(Driver *pdrive, int stage) {
  if (pmy_pack->pmesh->multilevel) {
    // physical boundary conditions on the coarse array first, then prolongation of the
    // fine ghost cells (the order of Z4c::Prolongate)
    if (!(pmy_pack->pmesh->strictly_periodic)) {
      pbval_u->Z4cBCsCoarse(pmy_pack, pbval_u->u_in, coarse_u0);
    }
    pbval_u->ProlongateCC(u0, coarse_u0, true);
  }
  return TaskStatus::complete;
}

//! Physical boundaries: phi and Pi are extrapolated (outflow) or mirrored (reflect) by
//! the routine of the spacetime variables, which treats components 0 and 1 as scalars.
TaskStatus ScalarField::ApplyPhysicalBCs(Driver *pdrive, int stage) {
  if (!(pmy_pack->pmesh->strictly_periodic)) {
    pbval_u->Z4cBCs((pmy_pack), (pbval_u->u_in), u0);
  }
  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus ScalarField::CopyU
//! \brief register u1 of the low-storage integrators, as Z4c::CopyU

TaskStatus ScalarField::CopyU(Driver *pdrive, int stage) {
  auto integrator = pdrive->integrator;
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  int is = indcs.is, ie = indcs.ie;
  int js = indcs.js, je = indcs.je;
  int ks = indcs.ks, ke = indcs.ke;
  int nmb1 = pmy_pack->nmb_thispack - 1;
  int nvar = nsf;
  auto &u0_ = u0;
  auto &u1_ = u1;

  if (integrator == "rk4") {
    Real &delta = pdrive->delta[stage-1];
    if (stage == 1) {
      Kokkos::deep_copy(DevExeSpace(), u1_, u0_);
    } else {
      par_for("sf_CopyU", DevExeSpace(),0, nmb1, 0, nvar-1, ks, ke, js, je, is, ie,
      KOKKOS_LAMBDA(int m, int n, int k, int j, int i){
        u1_(m,n,k,j,i) += delta*u0_(m,n,k,j,i);
      });
    }
  } else {
    if (stage == 1) {
      Kokkos::deep_copy(DevExeSpace(), u1_, u0_);
    }
  }
  NoiseCopy(pdrive, stage);
  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus ScalarField::CalcRHS_
//! \brief stochastic fields of this stage, then the right-hand side of phi and Pi

TaskStatus ScalarField::CalcRHS_(Driver *pdrive, int stage) {
  NoiseStage(pdrive, stage);
  switch (pmy_pack->pmesh->mb_indcs.ng) {
    case 2: CalcRHS<2>(pdrive, stage); break;
    case 3: CalcRHS<3>(pdrive, stage); break;
    case 4: CalcRHS<4>(pdrive, stage); break;
  }
  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus ScalarField::SetTmunu
//! \brief sources of all matter modules for the spacetime right-hand side of this stage

TaskStatus ScalarField::SetTmunu(Driver *pdrive, int stage) {
  if (opt.couple) { AssembleSources(true); }
  return TaskStatus::complete;
}

void ScalarField::AssembleSources(const bool stage_sources) {
  switch (pmy_pack->pmesh->mb_indcs.ng) {
    case 2: AssembleSourcesT<2>(stage_sources); break;
    case 3: AssembleSourcesT<3>(stage_sources); break;
    case 4: AssembleSourcesT<4>(stage_sources); break;
  }
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus ScalarField::ExpRKUpdate
//! \brief explicit Runge-Kutta update, as Z4c::ExpRKUpdate

TaskStatus ScalarField::ExpRKUpdate(Driver *pdriver, int stage) {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  int is = indcs.is, ie = indcs.ie;
  int js = indcs.js, je = indcs.je;
  int ks = indcs.ks, ke = indcs.ke;

  Real &gam0 = pdriver->gam0[stage-1];
  Real &gam1 = pdriver->gam1[stage-1];
  Real beta_dt = (pdriver->beta[stage-1])*(pmy_pack->pmesh->dt);
  auto &u0_ = u0;
  auto &u1_ = u1;
  auto &u_rhs_ = u_rhs;
  int nmb1 = pmy_pack->nmb_thispack - 1;
  int nvar = nsf;

  par_for("sf RK update",DevExeSpace(),
      0,nmb1,0,nvar-1,ks,ke,js,je,is,ie,
  KOKKOS_LAMBDA(const int m, const int n, const int k, const int j, const int i) {
    u0_(m,n,k,j,i) = gam0*u0_(m,n,k,j,i) + gam1*u1_(m,n,k,j,i)
                   + beta_dt*u_rhs_(m,n,k,j,i);
  });
  NoiseUpdate(pdriver, stage);
  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus ScalarField::Diagnostics
//! \brief after the step (list after_timeintegrator, behind the particle tasks): history
//! record and double-precision dump.  The mesh time is advanced by the driver only
//! after this list, so the new time is time + dt.

TaskStatus ScalarField::Diagnostics(Driver *pdriver, int stage) {
  Mesh *pm = pmy_pack->pmesh;
  const Real time = pm->time + pm->dt;
  const int ncycle = pm->ncycle + 1;
  if (opt.hist_dcycle > 0 && ncycle % opt.hist_dcycle == 0) {
    WriteHistory(time, ncycle, false);
  }
  bool dump = (opt.dump_dcycle > 0 && ncycle % opt.dump_dcycle == 0);
  if (opt.dump_dt > 0.0 && time >= dump_next_time - 1.0e-12*std::fabs(dump_next_time)) {
    dump = true;
    while (dump_next_time <= time*(1.0 + 1.0e-12)) { dump_next_time += opt.dump_dt; }
  }
  if (dump) {
    NoiseFieldsOfState();
    WriteDump(time);
  }
  return TaskStatus::complete;
}

} // namespace scalarfield
