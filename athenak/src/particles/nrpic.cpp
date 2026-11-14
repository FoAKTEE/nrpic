//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic.cpp
//! \brief Numerical-relativity particle-in-cell module: collisionless massive particles
//! that follow geodesics of the mesh (or of an analytic) metric and source the Z4c
//! spacetime evolution through their deposited stress-energy.
//!
//! One cycle from t^n to t^{n+1}:
//!   1. NrpicSaveMetric  keep alpha, beta^i, gamma_ij at t^n
//!   2. (Z4c)            advance the spacetime with the sources deposited at t^n
//!   3. NrpicPush        advance (x^i, u_i) with the metric at t^n and t^{n+1}
//!   4. NrpicExcise      remove particles below the lapse threshold or outside the mesh,
//!                       reassign the others to their MeshBlocks
//!   5. NrpicDeposit     deposit E, S_i, S_ij at t^{n+1}, filter, update constraints
//!   6. NrpicDiagnostics probe, history, trajectories, snapshots
//!
//! The module assumes a single MPI rank: deposition and ownership are resolved by a
//! search over all MeshBlocks of the pack.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <string>
#include <utility>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "driver/driver.hpp"
#include "bvals/bvals.hpp"
#include "coordinates/adm.hpp"
#include "z4c/z4c.hpp"
#include "z4c/tmunu.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_metrics.hpp"
#include "particles/nrpic_mesh.hpp"
// last: this header defines the macro NDIM, which collides with a member of Tmunu
#include "z4c/fastflow.hpp"

namespace particles {

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicInit
//! \brief reads the <particles> options of the nrpic module and allocates mesh arrays

void Particles::NrpicInit(ParameterInput *pin) {
  Mesh *pm = pmy_pack->pmesh;
  if (!(pm->three_d)) {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "Particles of type nrpic require a 3D mesh" << std::endl;
    std::exit(EXIT_FAILURE);
  }
  if (global_variable::nranks > 1) {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "Particles of type nrpic run on a single MPI rank" << std::endl;
    std::exit(EXIT_FAILURE);
  }

  std::string msrc = pin->GetOrAddString("particles", "metric", "mesh");
  if (msrc.compare("mesh") == 0) {
    nropt.metric = NrpicMetric::mesh;
  } else if (msrc.compare("kerr_schild") == 0) {
    nropt.metric = NrpicMetric::kerr_schild;
  } else if (msrc.compare("kerr_schild_sph") == 0) {
    nropt.metric = NrpicMetric::kerr_schild_sph;
  } else if (msrc.compare("boyer_lindquist") == 0) {
    nropt.metric = NrpicMetric::boyer_lindquist;
  } else if (msrc.compare("lattice") == 0) {
    nropt.metric = NrpicMetric::lattice;
  } else {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "<particles> metric = '" << msrc << "' not recognized" << std::endl;
    std::exit(EXIT_FAILURE);
  }
  std::string triad = pin->GetOrAddString("particles", "triad", "symmetric");
  if (triad.compare("symmetric") == 0) {
    nropt.triad = nrpic::kTriadSymmetric;
  } else if (triad.compare("cholesky") == 0) {
    nropt.triad = nrpic::kTriadCholesky;
  } else {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "<particles> triad = '" << triad << "' not recognized" << std::endl;
    std::exit(EXIT_FAILURE);
  }
  nropt.tol        = pin->GetOrAddReal("particles", "tolerance", 1.0e-7);
  nropt.maxit      = pin->GetOrAddInteger("particles", "max_iterations", 50);
  nropt.mass       = pin->GetOrAddReal("particles", "bh_mass", 1.0);
  nropt.spin       = pin->GetOrAddReal("particles", "bh_spin", 0.0);
  nropt.lattice_dx = pin->GetOrAddReal("particles", "lattice_dx", 0.025);
  nropt.nfilter    = pin->GetOrAddInteger("particles", "nfilter", 1);
  nropt.filter_compensate = pin->GetOrAddBoolean("particles", "filter_compensate", false);
  nropt.filter_comp_c     = pin->GetOrAddReal("particles", "filter_comp_c", -1.0);
  nropt.deposit_max_level = pin->GetOrAddInteger("particles", "deposit_max_level", 31);
  if (nropt.deposit_max_level < 0) { nropt.deposit_max_level = 0; }
  if (nropt.deposit_max_level > 31 - pm->root_level) {
    nropt.deposit_max_level = 31 - pm->root_level;
  }
  nropt.deposit_adaptive  = pin->GetOrAddBoolean("particles", "deposit_adaptive", false);
  nropt.deposit_min_level = pin->GetOrAddInteger("particles", "deposit_min_level", 0);
  nropt.deposit_ppc       = pin->GetOrAddReal("particles", "deposit_ppc", 2.0);
  nropt.deposit_max_coarsen = pin->GetOrAddInteger("particles", "deposit_max_coarsen", 31);
  if (nropt.deposit_max_coarsen < 0) { nropt.deposit_max_coarsen = 0; }
  if (nropt.deposit_min_level < 0) { nropt.deposit_min_level = 0; }
  if (nropt.deposit_min_level > nropt.deposit_max_level) {
    nropt.deposit_min_level = nropt.deposit_max_level;
  }
  nropt.alpha_exc  = pin->GetOrAddReal("particles", "alpha_exc", -1.0);
  nropt.ah_exc_factor = pin->GetOrAddReal("particles", "ah_exc_factor", -1.0);
  nropt.hist_dcycle = pin->GetOrAddInteger("particles", "hist_dcycle", 1);
  nropt.traj_dcycle = pin->GetOrAddInteger("particles", "traj_dcycle", 0);
  nropt.cstat_dcycle = pin->GetOrAddInteger("particles", "cstat_dcycle", 0);
  nropt.line_dcycle = pin->GetOrAddInteger("particles", "line_dcycle", 0);
  // times at which the energy density on the (uniform) mesh is written: field_time1, ...
  nfield_times = 0;
  for (int n=1; n<=16; ++n) {
    const std::string key = "field_time" + std::to_string(n);
    if (!pin->DoesParameterExist("particles", key)) break;
    field_times[nfield_times++] = pin->GetReal("particles", key);
  }
  field_next = 0;
  nropt.traj_ntrack = pin->GetOrAddInteger("particles", "traj_ntrack", 0);
  nropt.snap_dt    = pin->GetOrAddReal("particles", "snap_dt", -1.0);
  nropt.curv_dt    = pin->GetOrAddReal("particles", "curv_dt", -1.0);
  nropt.curv_slice = pin->GetOrAddBoolean("particles", "curv_slice", false);
  nropt.curv_plane_y = pin->GetOrAddReal("particles", "curv_plane_y", 1.0e-6);
  nropt.probe[0]   = pin->GetOrAddReal("particles", "probe_x1", 0.0);
  nropt.probe[1]   = pin->GetOrAddReal("particles", "probe_x2", 0.0);
  nropt.probe[2]   = pin->GetOrAddReal("particles", "probe_x3", 0.0);
  nropt.nprobe     = pin->GetOrAddInteger("particles", "nprobe", 0);
  if (nropt.nprobe < 0) { nropt.nprobe = 0; }
  if (nropt.nprobe > 8) { nropt.nprobe = 8; }
  for (int n=0; n<8; ++n) {
    nropt.probes[n][0] = 0.0; nropt.probes[n][1] = 0.0; nropt.probes[n][2] = 0.0;
  }
  for (int n=0; n<nropt.nprobe; ++n) {
    const std::string pre = "probe" + std::to_string(n+1) + "_";
    nropt.probes[n][0] = pin->GetReal("particles", pre + "x1");
    nropt.probes[n][1] = pin->GetReal("particles", pre + "x2");
    nropt.probes[n][2] = pin->GetReal("particles", pre + "x3");
  }
  nropt.lambda     = pin->GetOrAddReal("particles", "lambda", 0.0);
  nropt.source_density = pin->GetOrAddBoolean("particles", "source_density", false);
  nropt.source_extrap  = pin->GetOrAddBoolean("particles", "source_extrap", false);
  {
    // shape of the particle cloud in the deposit, a B-spline of degree one, two or
    // three: cic (two cells per direction), tsc (three), pcs (four)
    const std::string shp = pin->GetOrAddString("particles", "deposit_shape", "cic");
    if (shp.compare("cic") == 0) {
      nropt.deposit_shape = 1;
    } else if (shp.compare("tsc") == 0) {
      nropt.deposit_shape = 2;
    } else if (shp.compare("pcs") == 0) {
      nropt.deposit_shape = 3;
    } else {
      std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__
                << std::endl << "<particles> deposit_shape = '" << shp
                << "' not recognized (cic, tsc or pcs)" << std::endl;
      std::exit(EXIT_FAILURE);
    }
  }
  // periodic directions of the mesh: particles and their clouds wrap around
  nropt.periodic[0] = (pm->mesh_bcs[BoundaryFace::inner_x1] == BoundaryFlag::periodic);
  nropt.periodic[1] = (pm->mesh_bcs[BoundaryFace::inner_x2] == BoundaryFlag::periodic);
  nropt.periodic[2] = (pm->mesh_bcs[BoundaryFace::inner_x3] == BoundaryFlag::periodic);
  nropt.dom_min[0] = pm->mesh_size.x1min;
  nropt.dom_min[1] = pm->mesh_size.x2min;
  nropt.dom_min[2] = pm->mesh_size.x3min;
  nropt.dom_len[0] = pm->mesh_size.x1max - pm->mesh_size.x1min;
  nropt.dom_len[1] = pm->mesh_size.x2max - pm->mesh_size.x2min;
  nropt.dom_len[2] = pm->mesh_size.x3max - pm->mesh_size.x3min;
  dtnew = pin->GetOrAddReal("particles", "dt",
                            static_cast<Real>(std::numeric_limits<float>::max()));
  nr_basename = pin->GetString("job", "basename");
  nr_particle_file = pin->GetOrAddString("particles", "particle_file", "");
  {
    const int ninl = pin->GetOrAddInteger("particles", "nparticles", 0);
    nr_inline.clear();
    for (int n=0; n<ninl; ++n) {
      const std::string pre = "p" + std::to_string(n) + "_";
      nr_inline.push_back(pin->GetReal("particles", pre + "x1"));
      nr_inline.push_back(pin->GetReal("particles", pre + "x2"));
      nr_inline.push_back(pin->GetReal("particles", pre + "x3"));
      nr_inline.push_back(pin->GetReal("particles", pre + "u1"));
      nr_inline.push_back(pin->GetReal("particles", pre + "u2"));
      nr_inline.push_back(pin->GetReal("particles", pre + "u3"));
      nr_inline.push_back(pin->GetOrAddReal("particles", pre + "m", 0.0));
    }
  }

  const bool mesh_metric = (nropt.metric == NrpicMetric::mesh);
  metric_is_static = (pmy_pack->pz4c == nullptr);
  nropt.deposit = pin->GetOrAddBoolean("particles", "deposit",
                                       (mesh_metric && pmy_pack->pz4c != nullptr));
  if (mesh_metric && pmy_pack->padm == nullptr) {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "<particles> metric = mesh requires a <z4c> or <adm> block" << std::endl;
    std::exit(EXIT_FAILURE);
  }
  if (nropt.deposit && !mesh_metric) {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "<particles> deposit = true requires metric = mesh" << std::endl;
    std::exit(EXIT_FAILURE);
  }

  auto &indcs = pm->mb_indcs;
  int nmb = std::max((pmy_pack->nmb_thispack), (pm->nmb_maxperrank));
  int ncells1 = indcs.nx1 + 2*(indcs.ng);
  int ncells2 = indcs.nx2 + 2*(indcs.ng);
  int ncells3 = indcs.nx3 + 2*(indcs.ng);
  if (mesh_metric) {
    if (indcs.ng < 2) {
      std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__
                << std::endl << "nrpic mesh metric needs at least 2 ghost cells"
                << std::endl;
      std::exit(EXIT_FAILURE);
    }
    Kokkos::realloc(met1, nmb, NRM_NVAR, ncells3, ncells2, ncells1);
    if (!metric_is_static) {
      Kokkos::realloc(met0, nmb, NRM_NVAR, ncells3, ncells2, ncells1);
    }
  }
  if (nropt.deposit) {
    Kokkos::realloc(tm_work, nmb, Tmunu::N_Tmunu, ncells3, ncells2, ncells1);
    if (nropt.deposit_adaptive) {
      Kokkos::realloc(e_prev, nmb, ncells3, ncells2, ncells1);
    }
    if (pm->multilevel) {
      int nccells1 = indcs.cnx1 + 2*(indcs.ng);
      int nccells2 = indcs.cnx2 + 2*(indcs.ng);
      int nccells3 = indcs.cnx3 + 2*(indcs.ng);
      Kokkos::realloc(coarse_tm, nmb, Tmunu::N_Tmunu, nccells3, nccells2, nccells1);
    }
    pbval_tm = new MeshBoundaryValuesCC(pmy_pack, pin, false);
    pbval_tm->InitializeBuffers(Tmunu::N_Tmunu);
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::SetNumberOfParticles
//! \brief (re)allocates the particle arrays for n particles; existing data are discarded

void Particles::SetNumberOfParticles(int n) {
  Mesh *pm = pmy_pack->pmesh;
  Kokkos::realloc(prtcl_rdata, nrdata, n);
  Kokkos::realloc(prtcl_idata, nidata, n);
  nprtcl_thispack = n;
  pm->nprtcl_thisrank = n;
  pm->nprtcl_eachrank[global_variable::my_rank] = n;
  pm->nprtcl_total = n;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicFillMetric
//! \brief copies alpha, beta^i and gamma_ij from the ADM variables (all cells, including
//! ghost cells) into the array read by the pushers

void Particles::NrpicFillMetric(DvceArray5D<Real> &met) {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  int n1 = indcs.nx1 + 2*(indcs.ng);
  int n2 = indcs.nx2 + 2*(indcs.ng);
  int n3 = indcs.nx3 + 2*(indcs.ng);
  int nmb1 = pmy_pack->nmb_thispack - 1;
  auto &adm = pmy_pack->padm->adm;
  auto met_ = met;
  par_for("nrpic_fillmet", DevExeSpace(), 0, nmb1, 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    met_(m,NRM_ALP,k,j,i) = adm.alpha(m,k,j,i);
    met_(m,NRM_BX,k,j,i)  = adm.beta_u(m,0,k,j,i);
    met_(m,NRM_BY,k,j,i)  = adm.beta_u(m,1,k,j,i);
    met_(m,NRM_BZ,k,j,i)  = adm.beta_u(m,2,k,j,i);
    met_(m,NRM_GXX,k,j,i) = adm.g_dd(m,0,0,k,j,i);
    met_(m,NRM_GXY,k,j,i) = adm.g_dd(m,0,1,k,j,i);
    met_(m,NRM_GXZ,k,j,i) = adm.g_dd(m,0,2,k,j,i);
    met_(m,NRM_GYY,k,j,i) = adm.g_dd(m,1,1,k,j,i);
    met_(m,NRM_GYZ,k,j,i) = adm.g_dd(m,1,2,k,j,i);
    met_(m,NRM_GZZ,k,j,i) = adm.g_dd(m,2,2,k,j,i);
  });
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus Particles::NrpicSaveMetric
//! \brief before the spacetime update, the metric of the previous cycle becomes the
//! old time level

TaskStatus Particles::NrpicSaveMetric(Driver *pdriver, int stage) {
  if (nropt.metric == NrpicMetric::mesh && !metric_is_static) {
    std::swap(met0, met1);
  }
  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus Particles::NrpicPush
//! \brief advances all particles from t^n to t^{n+1}

TaskStatus Particles::NrpicPush(Driver *pdriver, int stage) {
  Mesh *pm = pmy_pack->pmesh;
  const bool mesh_metric = (nropt.metric == NrpicMetric::mesh);
  if (mesh_metric && !metric_is_static) {
    NrpicFillMetric(met1);
  }
  push_maxit = 0;
  push_unconverged = 0;
  const int np = nprtcl_thispack;
  if (np == 0) return TaskStatus::complete;

  auto &indcs = pm->mb_indcs;
  auto &pr = prtcl_rdata;
  auto &pi = prtcl_idata;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int gids = pmy_pack->gids;
  const Real dt = pm->dt;
  const Real tnow = pm->time;
  const Real tol = nropt.tol;
  const int maxit = nropt.maxit;
  const int triad = nropt.triad;
  const bool boris = (pusher == ParticlesPusher::nrpic_boris);
  const NrpicMetric msrc = nropt.metric;
  const Real bh_mass = nropt.mass, bh_spin = nropt.spin, lat_dx = nropt.lattice_dx;
  const Real alpha_exc = nropt.alpha_exc;

  // apparent-horizon excision: particles inside ah_exc_factor times the minimum
  // coordinate radius of a found horizon are removed
  int nah = 0;
  Real ahc[4][3], ahr2[4];
  for (int n=0; n<4; ++n) {
    ahc[n][0] = 0.0; ahc[n][1] = 0.0; ahc[n][2] = 0.0;
    ahr2[n] = 0.0;
  }
  if (mesh_metric && nropt.ah_exc_factor > 0.0 && pmy_pack->pz4c != nullptr) {
    for (auto &pah : pmy_pack->pz4c->pfastflow) {
      // rr_min is -1 until a search of this run has succeeded: after a restart the
      // flag ah_found is restored from the dump but the radius and centre are not, so
      // the rule waits for the first successful search
      // A surface more than four times its starting radius is not accepted as a
      // region to empty (a search that ends on a spurious surface must not remove
      // the matter of the cluster).
      if (pah->ah_found && nah < 4 && Kokkos::isfinite(pah->rr_min)
          && pah->rr_min > 0.0 && pah->rr_min < 4.0*pah->initial_radius) {
        ahc[nah][0] = pah->center[0];
        ahc[nah][1] = pah->center[1];
        ahc[nah][2] = pah->center[2];
        ahr2[nah] = SQR(nropt.ah_exc_factor*pah->rr_min);
        ++nah;
      }
    }
  }

  nrpic::MeshMetric proto;
  if (mesh_metric) {
    proto.m1 = met1;
    proto.m0 = metric_is_static ? met1 : met0;
    proto.is_static = metric_is_static;
    proto.ist[0] = indcs.is; proto.ist[1] = indcs.js; proto.ist[2] = indcs.ks;
    proto.ncell[0] = indcs.nx1 + 2*indcs.ng;
    proto.ncell[1] = indcs.nx2 + 2*indcs.ng;
    proto.ncell[2] = indcs.nx3 + 2*indcs.ng;
  }

  int nun = 0, mxit = 0;
  Kokkos::parallel_reduce("nrpic_push", Kokkos::RangePolicy<DevExeSpace>(0, np),
  KOKKOS_LAMBDA(const int p, int &lnun, int &lmxit) {
    Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
    Real u[3] = {pr(IPVX,p), pr(IPVY,p), pr(IPVZ,p)};
    // a particle without rest mass follows a null geodesic (midpoint pusher only);
    // a negative mass -t_e marks a null particle that waits at its position until the
    // time t_e (a light ray emitted during the run)
    // The ray leaves at the step time nearest to t_e. Until then its momentum slots
    // hold the coordinate direction c^i of emission; at the launch they are replaced
    // by k_i = gamma_ij c^j / sqrt(gamma_kl c^k c^l), the null momentum of unit
    // frequency for the normal observer at the point of emission. The proper-time slot
    // of a null particle accumulates its affine parameter and is zero until the launch.
    const Real eps = (pr(IPM,p) > 0.0) ? 1.0 : 0.0;
    if (pr(IPM,p) < 0.0 && tnow + 0.5*dt < -pr(IPM,p)) return;
    const bool launch = (pr(IPM,p) < 0.0 && pr(IPTAU,p) == 0.0);
    Real dtau = 0.0;
    int it = 0;
    bool excise = false;
    if (msrc == NrpicMetric::mesh) {
      const int m = pi(PGID,p) - gids;
      nrpic::MeshMetric met = proto;
      met.m = m;
      met.xmin[0] = sz(m).x1min; met.xmin[1] = sz(m).x2min; met.xmin[2] = sz(m).x3min;
      met.idx[0] = 1.0/sz(m).dx1; met.idx[1] = 1.0/sz(m).dx2; met.idx[2] = 1.0/sz(m).dx3;
      if (launch) {
        nrpic::AdmPoint ap;
        met(0, x, ap);
        Real k[3] = {0.0, 0.0, 0.0};
        Real c2 = 0.0;
        for (int a=0; a<3; ++a) {
          for (int b=0; b<3; ++b) {
            k[a] += ap.g[a][b]*u[b];
            c2 += ap.g[a][b]*u[a]*u[b];
          }
        }
        const Real ic = 1.0/sqrt(c2);
        u[0] = k[0]*ic; u[1] = k[1]*ic; u[2] = k[2]*ic;
      }
      if (alpha_exc > 0.0) {
        nrpic::AdmPoint ap;
        met(0, x, ap);
        excise = (ap.alp < alpha_exc);
      }
      for (int n=0; n<nah; ++n) {
        const Real d2 = SQR(x[0] - ahc[n][0]) + SQR(x[1] - ahc[n][1])
                        + SQR(x[2] - ahc[n][2]);
        if (d2 < ahr2[n]) { excise = true; }
      }
      if (!excise) {
        if (boris) {
          it = nrpic::PushBoris(met, triad, dt, tol, maxit, x, u);
        } else {
          it = nrpic::PushMidpoint(met, dt, tol, maxit, x, u, eps, dtau);
        }
      }
    } else if (msrc == NrpicMetric::kerr_schild) {
      nrpic::KerrSchildCart met{bh_mass, bh_spin};
      it = boris ? nrpic::PushBoris(met, triad, dt, tol, maxit, x, u)
                 : nrpic::PushMidpoint(met, dt, tol, maxit, x, u);
    } else if (msrc == NrpicMetric::kerr_schild_sph) {
      nrpic::KerrSchildSph met{bh_mass, bh_spin};
      it = boris ? nrpic::PushBoris(met, triad, dt, tol, maxit, x, u)
                 : nrpic::PushMidpoint(met, dt, tol, maxit, x, u);
    } else if (msrc == NrpicMetric::boyer_lindquist) {
      nrpic::BoyerLindquist met{bh_mass, bh_spin};
      it = boris ? nrpic::PushBoris(met, triad, dt, tol, maxit, x, u)
                 : nrpic::PushMidpoint(met, dt, tol, maxit, x, u);
    } else {
      nrpic::LatticeMetric<nrpic::KerrSchildCart> met{{bh_mass, bh_spin},
                                                      {0.0, 0.0, 0.0},
                                                      {lat_dx, lat_dx, lat_dx}};
      it = boris ? nrpic::PushBoris(met, triad, dt, tol, maxit, x, u)
                 : nrpic::PushMidpoint(met, dt, tol, maxit, x, u);
    }
    if (it < 0) {
      lnun += 1;
      it = -it;
    }
    lmxit = (it > lmxit) ? it : lmxit;
    // a particle whose state is no longer finite is removed with the excised ones
    Real chk = x[0] + x[1] + x[2] + u[0] + u[1] + u[2];
    if (!(Kokkos::isfinite(chk))) { excise = true; }
    if (excise) {
      pi(PGID,p) = -2;
    } else {
      pr(IPX,p) = x[0]; pr(IPY,p) = x[1]; pr(IPZ,p) = x[2];
      pr(IPVX,p) = u[0]; pr(IPVY,p) = u[1]; pr(IPVZ,p) = u[2];
      pr(IPTAU,p) += dtau;
    }
  }, Kokkos::Sum<int>(nun), Kokkos::Max<int>(mxit));
  push_unconverged = nun;
  push_maxit = mxit;

  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAssignBlocks
//! \brief sets the grid ID of each particle to the MeshBlock that contains it, or to -1
//! if it has left the mesh.  Valid on uniform, statically and adaptively refined meshes.

void Particles::NrpicAssignBlocks() {
  const int np = nprtcl_thispack;
  if (np == 0) return;
  auto &pr = prtcl_rdata;
  auto &pi = prtcl_idata;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int gids = pmy_pack->gids;
  const int nmb = pmy_pack->nmb_thispack;
  const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3] = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
  par_for("nrpic_assign", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
    if (pi(PGID,p) >= 0) {
      pr(IPX,p) = nrpic::WrapCoord(pr(IPX,p), dmin[0], dlen[0], per[0]);
      pr(IPY,p) = nrpic::WrapCoord(pr(IPY,p), dmin[1], dlen[1], per[1]);
      pr(IPZ,p) = nrpic::WrapCoord(pr(IPZ,p), dmin[2], dlen[2], per[2]);
      int m = nrpic::FindBlock(sz, nmb, pi(PGID,p) - gids, pr(IPX,p), pr(IPY,p),
                               pr(IPZ,p));
      pi(PGID,p) = (m < 0) ? -1 : (m + gids);
    }
  });
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicRemoveFlagged
//! \brief removes particles with negative grid ID (-1 left the mesh, -2 excised) and
//! compacts the particle arrays, keeping the order of the remaining particles

void Particles::NrpicRemoveFlagged() {
  Mesh *pm = pmy_pack->pmesh;
  const int np = nprtcl_thispack;
  if (np == 0) return;
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  int nesc = 0, nexc = 0;
  Real mesc = 0.0, mexc = 0.0;
  Kokkos::parallel_reduce("nrpic_count", Kokkos::RangePolicy<DevExeSpace>(0, np),
  KOKKOS_LAMBDA(const int p, int &lnesc, int &lnexc, Real &lmesc, Real &lmexc) {
    if (pi(PGID,p) == -1) {
      lnesc += 1;
      lmesc += pr(IPM,p);
    } else if (pi(PGID,p) < -1) {
      lnexc += 1;
      lmexc += pr(IPM,p);
    }
  }, Kokkos::Sum<int>(nesc), Kokkos::Sum<int>(nexc), Kokkos::Sum<Real>(mesc),
     Kokkos::Sum<Real>(mexc));
  if (nesc + nexc == 0) return;

  n_escaped += nesc;
  n_excised += nexc;
  mass_escaped += mesc;
  mass_excised += mexc;

  const int nkeep = np - nesc - nexc;
  const int nr = nrdata, ni = nidata;
  DvceArray2D<Real> rnew("prtcl_rdata", nr, nkeep);
  DvceArray2D<int>  inew("prtcl_idata", ni, nkeep);
  int ntot = 0;
  Kokkos::parallel_scan("nrpic_compact", Kokkos::RangePolicy<DevExeSpace>(0, np),
  KOKKOS_LAMBDA(const int p, int &upd, const bool final) {
    if (pi(PGID,p) >= 0) {
      if (final) {
        for (int n=0; n<nr; ++n) { rnew(n,upd) = pr(n,p); }
        for (int n=0; n<ni; ++n) { inew(n,upd) = pi(n,p); }
      }
      upd += 1;
    }
  }, ntot);
  prtcl_rdata = rnew;
  prtcl_idata = inew;
  nprtcl_thispack = nkeep;
  pm->nprtcl_thisrank = nkeep;
  pm->nprtcl_eachrank[global_variable::my_rank] = nkeep;
  pm->nprtcl_total = nkeep;
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus Particles::NrpicExcise
//! \brief removes excised and escaped particles and updates the MeshBlock of the others

TaskStatus Particles::NrpicExcise(Driver *pdriver, int stage) {
  if (nropt.metric == NrpicMetric::mesh) {
    NrpicAssignBlocks();
    NrpicRemoveFlagged();
  }
  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicDepositSources
//! \brief deposits the ADM matter sources of all particles onto the mesh with the
//! first-order (cloud-in-cell) shape,
//!   E = sum m W S/(sqrt(gamma) dV),  S_i = sum m u_i S/(...),  S_ij = sum m u_i u_j S/(W ...).
//! Each particle is represented on a single refinement level, the finest among the
//! MeshBlocks that own its eight nearest cell centres, and the part of its cloud that
//! falls into a coarser MeshBlock is accumulated in the coarse cell that contains the
//! (virtual) fine cell.  The weights of a particle therefore sum to one over the leaf
//! cells of the mesh and the volume integrals of the sources equal the particle sums.
//! With <particles> deposit_max_level the representation level is capped: where the
//! mesh is finer than the cap, the cloud keeps the cell size of the cap level and its
//! density is spread uniformly over the leaf cells inside each lattice cell.  The
//! sums are conserved in the same way, and the particle size no longer shrinks with
//! the mesh, which matters when there are fewer particles than fine cells.
//! With deposit_adaptive the cap of each particle follows the local particle density:
//! it is the finest level, between deposit_min_level and deposit_max_level, whose cells
//! contain at least deposit_ppc particles at the coordinate density of the previous
//! deposit.

void Particles::NrpicDepositSources() {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  auto tm = pmy_pack->ptmunu->u_tmunu;
  // With the adaptive level cap, the coordinate density sqrt(gamma) E of the previous
  // deposit selects the representation level of each particle.  It is not available
  // for the first deposit on a new mesh, which then uses the lowest allowed level.
  const bool adaptive = nropt.deposit_adaptive;
  const bool have_prev = adaptive && e_prev_valid;
  auto ep = e_prev;
  if (have_prev) {
    auto mm = met1;
    const int nb1 = pmy_pack->nmb_thispack - 1;
    par_for("nrpic_eprev", DevExeSpace(), 0, nb1, indcs.ks, indcs.ke, indcs.js, indcs.je,
            indcs.is, indcs.ie,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      const Real det = adm::SpatialDet(mm(m,NRM_GXX,k,j,i), mm(m,NRM_GXY,k,j,i),
                                       mm(m,NRM_GXZ,k,j,i), mm(m,NRM_GYY,k,j,i),
                                       mm(m,NRM_GYZ,k,j,i), mm(m,NRM_GZZ,k,j,i));
      ep(m,k,j,i) = tm(m,Tmunu::I_Tmunu_E,k,j,i)*sqrt(det);
    });
  }
  Kokkos::deep_copy(DevExeSpace(), tm, 0.0);
  sum_mw = 0.0;
  for (int n=0; n<4; ++n) { dep_sum[n] = 0.0; }

  const int np = nprtcl_thispack;
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  auto lev = pmy_pack->pmb->mb_lev.d_view;
  const int gids = pmy_pack->gids;
  const int nmb = pmy_pack->nmb_thispack;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
  const Real gmin[3] = {pm->mesh_size.x1min, pm->mesh_size.x2min, pm->mesh_size.x3min};
  auto m1 = met1;
  // finest and coarsest (logical) levels on which a particle cloud is represented
  const int lcap_max = pm->root_level + nropt.deposit_max_level;
  const int lcap_min = pm->root_level + nropt.deposit_min_level;
  const int root_lev = pm->root_level;
  const Real ppc_target = nropt.deposit_ppc;
  const int max_coarsen = nropt.deposit_max_coarsen;
  const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3] = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
  const int nb = nropt.deposit_shape + 1;              // cells per direction of a cloud

  nrpic::MeshMetric proto;
  proto.m1 = met1;
  proto.m0 = met1;
  proto.is_static = true;
  proto.ist[0] = is; proto.ist[1] = js; proto.ist[2] = ks;
  proto.ncell[0] = indcs.nx1 + 2*indcs.ng;
  proto.ncell[1] = indcs.nx2 + 2*indcs.ng;
  proto.ncell[2] = indcs.nx3 + 2*indcs.ng;

  if (np > 0) {
    Real smw = 0.0;
    Kokkos::parallel_reduce("nrpic_deposit", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, Real &lsmw) {
      const int mo = pi(PGID,p) - gids;
      const Real xp[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
      const Real up[3] = {pr(IPVX,p), pr(IPVY,p), pr(IPVZ,p)};
      const Real mp = pr(IPM,p);
      if (mp <= 0.0) return;        // null particles and tracers carry no sources

      // Lorentz factor from the metric reconstructed at the particle
      nrpic::MeshMetric met = proto;
      met.m = mo;
      met.xmin[0] = sz(mo).x1min; met.xmin[1] = sz(mo).x2min; met.xmin[2] = sz(mo).x3min;
      met.idx[0] = 1.0/sz(mo).dx1; met.idx[1] = 1.0/sz(mo).dx2;
      met.idx[2] = 1.0/sz(mo).dx3;
      nrpic::AdmPoint ap;
      met(1, xp, ap);
      Real gi[3][3], uup[3];
      nrpic::Inv3Sym(ap.g, gi);
      const Real W = nrpic::LorentzFactor(gi, up, uup);
      lsmw += mp*W;

      Real q[Tmunu::N_Tmunu];
      q[Tmunu::I_Tmunu_Sxx] = mp*up[0]*up[0]/W;
      q[Tmunu::I_Tmunu_Sxy] = mp*up[0]*up[1]/W;
      q[Tmunu::I_Tmunu_Sxz] = mp*up[0]*up[2]/W;
      q[Tmunu::I_Tmunu_Syy] = mp*up[1]*up[1]/W;
      q[Tmunu::I_Tmunu_Syz] = mp*up[1]*up[2]/W;
      q[Tmunu::I_Tmunu_Szz] = mp*up[2]*up[2]/W;
      q[Tmunu::I_Tmunu_E]   = mp*W;
      q[Tmunu::I_Tmunu_Sx]  = mp*up[0];
      q[Tmunu::I_Tmunu_Sy]  = mp*up[1];
      q[Tmunu::I_Tmunu_Sz]  = mp*up[2];

      // (1) deposition level: the finest level among the owners of the eight nearest
      //     cell centres of the lattice at the level of the particle's own MeshBlock,
      //     but no finer than the cap lcap
      const int lev0 = lev(mo);
      Real h[3] = {sz(mo).dx1, sz(mo).dx2, sz(mo).dx3};
      // level cap of this particle: fixed, or the finest level whose cells hold at
      // least ppc_target particles at the local density of the previous deposit
      int lcap = lcap_max;
      if (adaptive) {
        lcap = lcap_min;
        if (have_prev) {
          int i = is + static_cast<int>(floor((xp[0] - sz(mo).x1min)/h[0]));
          int j = js + static_cast<int>(floor((xp[1] - sz(mo).x2min)/h[1]));
          int k = ks + static_cast<int>(floor((xp[2] - sz(mo).x3min)/h[2]));
          i = (i < is) ? is : ((i > ie) ? ie : i);
          j = (j < js) ? js : ((j > je) ? je : j);
          k = (k < ks) ? ks : ((k > ke) ? ke : k);
          const Real nc = ep(mo,k,j,i);
          if (nc > 0.0) {
            // smallest admissible cell size, and the finest level that respects it
            const Real dmin = cbrt(ppc_target*mp*W/nc);
            const Real droot = h[0]*static_cast<Real>(1 << (lev0 - root_lev));
            int lv = root_lev + static_cast<int>(floor(log2(droot/dmin)));
            lv = (lv < lcap_min) ? lcap_min : lv;
            lv = (lv > lcap_max) ? lcap_max : lv;
            lcap = lv;
          }
        }
      }
      // the cloud is at most max_coarsen levels coarser than the particle's own
      // MeshBlock: the mesh is refined to resolve the metric, and a cloud many cells
      // wide would spread a particle's energy and covariant momentum over a region
      // across which the metric changes
      if (lcap < lev0 - max_coarsen) { lcap = lev0 - max_coarsen; }
      int ldep = lev0;
      if (lev0 > lcap) {
        const Real fac = static_cast<Real>(1 << (lev0 - lcap));
        h[0] *= fac; h[1] *= fac; h[2] *= fac;
        ldep = lcap;
      } else {
        int lmax = lev0;
        Real xb0[3];
        for (int d=0; d<3; ++d) {
          Real xi = (xp[d] - gmin[d])/h[d] - 0.5;
          Real fl = (nb == 3) ? floor(xi + 0.5) - 1.0
                              : ((nb == 4) ? floor(xi) - 1.0 : floor(xi));
          xb0[d] = gmin[d] + (fl + 0.5)*h[d];
        }
        for (int c=0; c<nb*nb*nb; ++c) {
          const int c1 = c % nb, c2 = (c/nb) % nb, c3 = c/(nb*nb);
          Real xf = nrpic::WrapCoord(xb0[0] + c1*h[0], dmin[0], dlen[0], per[0]);
          Real yf = nrpic::WrapCoord(xb0[1] + c2*h[1], dmin[1], dlen[1], per[1]);
          Real zf = nrpic::WrapCoord(xb0[2] + c3*h[2], dmin[2], dlen[2], per[2]);
          int mb = nrpic::FindBlock(sz, nmb, mo, xf, yf, zf);
          if (mb >= 0) { lmax = (lev(mb) > lmax) ? lev(mb) : lmax; }
        }
        lmax = (lmax > lcap) ? lcap : lmax;
        if (lmax > lev0) {
          const Real fac = 1.0/static_cast<Real>(1 << (lmax - lev0));
          h[0] *= fac; h[1] *= fac; h[2] *= fac;
        }
        ldep = lmax;
      }
      // (2) weights of the cloud on the lattice of the deposition level: B-splines of
      //     degree one (cloud in cell, two cells per direction), two (triangular shaped
      //     cloud, three cells) or three (piecewise cubic, four cells)
      Real xb[3], wt[3][4];
      for (int d=0; d<3; ++d) {
        Real xi = (xp[d] - gmin[d])/h[d] - 0.5;
        if (nb == 3) {
          Real fl = floor(xi + 0.5);
          Real dd = xi - fl;
          wt[d][0] = 0.5*SQR(0.5 - dd);
          wt[d][1] = 0.75 - dd*dd;
          wt[d][2] = 0.5*SQR(0.5 + dd);
          wt[d][3] = 0.0;
          xb[d] = gmin[d] + (fl - 0.5)*h[d];
        } else if (nb == 4) {
          Real fl = floor(xi);
          Real sd = xi - fl;
          wt[d][0] = (1.0 - sd)*(1.0 - sd)*(1.0 - sd)/6.0;
          wt[d][1] = (3.0*sd*sd*sd - 6.0*sd*sd + 4.0)/6.0;
          wt[d][2] = (-3.0*sd*sd*sd + 3.0*sd*sd + 3.0*sd + 1.0)/6.0;
          wt[d][3] = sd*sd*sd/6.0;
          xb[d] = gmin[d] + (fl - 0.5)*h[d];
        } else {
          Real fl = floor(xi);
          Real sd = xi - fl;
          wt[d][0] = 1.0 - sd;
          wt[d][1] = sd;
          wt[d][2] = 0.0;
          wt[d][3] = 0.0;
          xb[d] = gmin[d] + (fl + 0.5)*h[d];
        }
      }
      for (int c=0; c<nb*nb*nb; ++c) {
        const int c1 = c % nb, c2 = (c/nb) % nb, c3 = c/(nb*nb);
        // centre of the lattice cell, wrapped into the mesh in periodic directions
        const Real xf = nrpic::WrapCoord(xb[0] + c1*h[0], dmin[0], dlen[0], per[0]);
        const Real yf = nrpic::WrapCoord(xb[1] + c2*h[1], dmin[1], dlen[1], per[1]);
        const Real zf = nrpic::WrapCoord(xb[2] + c3*h[2], dmin[2], dlen[2], per[2]);
        const Real w = wt[0][c1]*wt[1][c2]*wt[2][c3];
        // (3) leaf cells covered by this (real or virtual) lattice cell.  A lattice
        //     cell lies inside a single MeshBlock.
        const int mb = nrpic::FindBlock(sz, nmb, mo, xf, yf, zf);
        if (mb < 0) continue;
        const int kd = lev(mb) - ldep;
        if (kd <= 0) {
          // leaf at the deposition level or coarser: the leaf cell containing the cell
          int i = is + static_cast<int>(floor((xf - sz(mb).x1min)/sz(mb).dx1));
          int j = js + static_cast<int>(floor((yf - sz(mb).x2min)/sz(mb).dx2));
          int k = ks + static_cast<int>(floor((zf - sz(mb).x3min)/sz(mb).dx3));
          i = (i < is) ? is : ((i > ie) ? ie : i);
          j = (j < js) ? js : ((j > je) ? je : j);
          k = (k < ks) ? ks : ((k > ke) ? ke : k);
          const Real wv = w/(sz(mb).dx1*sz(mb).dx2*sz(mb).dx3);
          for (int n=0; n<Tmunu::N_Tmunu; ++n) {
            Kokkos::atomic_add(&tm(mb,n,k,j,i), wv*q[n]);
          }
        } else {
          // finer leaves: the same density in every leaf cell inside the lattice cell
          const int nsub = 1 << kd;
          const Real wv = w/(h[0]*h[1]*h[2]);
          const int i0 = is + static_cast<int>(
              floor((xf - 0.5*h[0] - sz(mb).x1min)/sz(mb).dx1 + 0.5));
          const int j0 = js + static_cast<int>(
              floor((yf - 0.5*h[1] - sz(mb).x2min)/sz(mb).dx2 + 0.5));
          const int k0 = ks + static_cast<int>(
              floor((zf - 0.5*h[2] - sz(mb).x3min)/sz(mb).dx3 + 0.5));
          for (int kk=0; kk<nsub; ++kk) {
            const int k = k0 + kk;
            if (k < ks || k > ke) continue;
            for (int jj=0; jj<nsub; ++jj) {
              const int j = j0 + jj;
              if (j < js || j > je) continue;
              for (int ii=0; ii<nsub; ++ii) {
                const int i = i0 + ii;
                if (i < is || i > ie) continue;
                for (int n=0; n<Tmunu::N_Tmunu; ++n) {
                  Kokkos::atomic_add(&tm(mb,n,k,j,i), wv*q[n]);
                }
              }
            }
          }
        }
      }
    }, Kokkos::Sum<Real>(smw));
    sum_mw = smw;
  }

  // divide by sqrt(gamma) at the receiving cell; accumulate the proper-volume integrals
  // of E and S_i, which equal the particle sums of m W and m u_i
  const int n1 = indcs.nx1, n2 = indcs.nx2, n3 = indcs.nx3;
  const int ncell = nmb*n3*n2*n1;
  Real se = 0.0, sx = 0.0, sy = 0.0, szz = 0.0;
  int nbad = 0;
  Kokkos::parallel_reduce("nrpic_normalize", Kokkos::RangePolicy<DevExeSpace>(0, ncell),
  KOKKOS_LAMBDA(const int idx, Real &lse, Real &lsx, Real &lsy, Real &lsz, int &lnbad) {
    int m = idx/(n3*n2*n1);
    int rem = idx - m*(n3*n2*n1);
    int k = rem/(n2*n1);
    rem -= k*(n2*n1);
    int j = rem/n1;
    int i = rem - j*n1;
    k += ks; j += js; i += is;
    const Real vol = sz(m).dx1*sz(m).dx2*sz(m).dx3;
    lse += tm(m,Tmunu::I_Tmunu_E,k,j,i)*vol;
    lsx += tm(m,Tmunu::I_Tmunu_Sx,k,j,i)*vol;
    lsy += tm(m,Tmunu::I_Tmunu_Sy,k,j,i)*vol;
    lsz += tm(m,Tmunu::I_Tmunu_Sz,k,j,i)*vol;
    const Real det = adm::SpatialDet(m1(m,NRM_GXX,k,j,i), m1(m,NRM_GXY,k,j,i),
                                     m1(m,NRM_GXZ,k,j,i), m1(m,NRM_GYY,k,j,i),
                                     m1(m,NRM_GYZ,k,j,i), m1(m,NRM_GZZ,k,j,i));
    // The ADM metric is the conformal metric divided by the evolved conformal factor
    // chi without a floor.  At a cell centre next to a moving puncture chi can
    // undershoot to zero or below; the determinant is then not positive (or not
    // finite) and 1/sqrt(det) would put a NaN into the sources of that cell, which the
    // filter passes spread over the mesh.  Such a cell lies inside the black hole:
    // its sources are set to zero and the cell is counted.
    const bool ok = (det > 0.0) && (det < 1.0e300);
    const Real isg = ok ? 1.0/sqrt(det) : 0.0;
    if (!ok) { lnbad += 1; }
    for (int n=0; n<Tmunu::N_Tmunu; ++n) {
      tm(m,n,k,j,i) *= isg;
    }
  }, Kokkos::Sum<Real>(se), Kokkos::Sum<Real>(sx), Kokkos::Sum<Real>(sy),
     Kokkos::Sum<Real>(szz), Kokkos::Sum<int>(nbad));
  dep_sum[0] = se; dep_sum[1] = sx; dep_sum[2] = sy; dep_sum[3] = szz;
  if (nbad > 0) {
    n_bad_det_total += nbad;
    if (n_bad_det_reports < 50) {
      ++n_bad_det_reports;
      // where they are: centroid, extent and cell sizes of the affected cells, and how
      // many of them have a non-finite determinant (as opposed to a non-positive one)
      Real cx = 0.0, cy = 0.0, cz = 0.0, xlo = 0.0, xhi = 0.0, dlo = 0.0, dhi = 0.0;
      int nnf = 0;
      Kokkos::parallel_reduce("nrpic_baddet", Kokkos::RangePolicy<DevExeSpace>(0, ncell),
      KOKKOS_LAMBDA(const int idx, Real &lx, Real &ly, Real &lz, Real &lxlo, Real &lxhi,
                    Real &ldlo, Real &ldhi, int &lnnf) {
        int m = idx/(n3*n2*n1);
        int rem = idx - m*(n3*n2*n1);
        int k = rem/(n2*n1);
        rem -= k*(n2*n1);
        int j = rem/n1;
        int i = rem - j*n1;
        const Real det = adm::SpatialDet(m1(m,NRM_GXX,k+ks,j+js,i+is),
            m1(m,NRM_GXY,k+ks,j+js,i+is), m1(m,NRM_GXZ,k+ks,j+js,i+is),
            m1(m,NRM_GYY,k+ks,j+js,i+is), m1(m,NRM_GYZ,k+ks,j+js,i+is),
            m1(m,NRM_GZZ,k+ks,j+js,i+is));
        if (!((det > 0.0) && (det < 1.0e300))) {
          const Real x = sz(m).x1min + (i + 0.5)*sz(m).dx1;
          const Real y = sz(m).x2min + (j + 0.5)*sz(m).dx2;
          const Real z = sz(m).x3min + (k + 0.5)*sz(m).dx3;
          lx += x; ly += y; lz += z;
          lxlo = (x < lxlo) ? x : lxlo;
          lxhi = (x > lxhi) ? x : lxhi;
          ldlo = (sz(m).dx1 < ldlo) ? sz(m).dx1 : ldlo;
          ldhi = (sz(m).dx1 > ldhi) ? sz(m).dx1 : ldhi;
          if (!(det == det) || !(det < 1.0e300) || !(det > -1.0e300)) { lnnf += 1; }
        }
      }, Kokkos::Sum<Real>(cx), Kokkos::Sum<Real>(cy), Kokkos::Sum<Real>(cz),
         Kokkos::Min<Real>(xlo), Kokkos::Max<Real>(xhi), Kokkos::Min<Real>(dlo),
         Kokkos::Max<Real>(dhi), Kokkos::Sum<int>(nnf));
      std::cout << "NRPIC: " << nbad << " cell(s) with a non-positive or non-finite "
                << "metric determinant at time " << pm->time
                << " (sources set to zero there); non-finite: " << nnf
                << "; centroid (" << cx/nbad << ", " << cy/nbad << ", " << cz/nbad
                << "), x from " << xlo << " to " << xhi << ", cell sizes " << dlo
                << " to " << dhi << std::endl;
    }
  }
  e_prev_valid = true;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicFilterSources
//! \brief applies nfilter passes of the binomial (1/4, 1/2, 1/4)^3 filter to each of the
//! ten source components.  Ghost cells are filled before every pass, by copy between
//! MeshBlocks at the same level and by restriction and prolongation across levels.
//!
//! With filter_compensate the binomial passes are followed by one pass with the weights
//! (-c, 1+2c, -c)^3.  n binomial passes have the response cos^{2n}(k dx/2) =
//! 1 - n (k dx)^2/4 + ..., i.e. they widen every cloud by a second moment n dx^2/2 per
//! dimension, which softens the self-gravity of the matter.  The compensation pass has
//! the response 1 + 4c sin^2(k dx/2); c = n/4 cancels the second moment, the combined
//! response (1-s)^n (1+ns), s = sin^2(k dx/2), is 1 - n(n+1)s^2/2 + ..., decreases
//! monotonically and still vanishes at the Nyquist wavenumber.  The weights sum to one,
//! so the pass conserves what the binomial passes conserve; it has small negative lobes.

void Particles::NrpicFilterSources() {
  if (nropt.nfilter <= 0 && !(nropt.filter_compensate && nropt.filter_comp_c > 0.0)) {
    for (int n=0; n<4; ++n) { dep_sum_filt[n] = dep_sum[n]; }
    return;
  }
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
  const int nmb1 = pmy_pack->nmb_thispack - 1;
  const int nv1 = Tmunu::N_Tmunu - 1;
  auto &tmu = pmy_pack->ptmunu->u_tmunu;
  auto tm = tmu;
  auto wk = tm_work;

  const int npass = nropt.nfilter + (nropt.filter_compensate ? 1 : 0);
  for (int pass=0; pass<npass; ++pass) {
    // one-dimensional weights (w1, w0, w1) of this pass
    Real w0 = 0.5, w1 = 0.25;
    if (pass >= nropt.nfilter) {
      const Real c = (nropt.filter_comp_c >= 0.0) ? nropt.filter_comp_c
                                                  : 0.25*static_cast<Real>(nropt.nfilter);
      w0 = 1.0 + 2.0*c;
      w1 = -c;
    }
    if (pm->multilevel) {
      pm->pmr->RestrictCC(tmu, coarse_tm);
    }
    (void) pbval_tm->InitRecv(Tmunu::N_Tmunu);
    (void) pbval_tm->PackAndSendCC(tmu, coarse_tm);
    (void) pbval_tm->ClearSend();
    (void) pbval_tm->ClearRecv();
    (void) pbval_tm->RecvAndUnpackCC(tmu, coarse_tm);
    if (pm->multilevel) {
      pbval_tm->FillCoarseInBndryCC(tmu, coarse_tm);
      pbval_tm->ProlongateCC(tmu, coarse_tm);
    }

    par_for("nrpic_filter", DevExeSpace(), 0, nmb1, 0, nv1, ks, ke, js, je, is, ie,
    KOKKOS_LAMBDA(const int m, const int n, const int k, const int j, const int i) {
      Real sum = 0.0;
      for (int c=-1; c<=1; ++c) {
        const Real wc = (c == 0) ? w0 : w1;
        for (int b=-1; b<=1; ++b) {
          const Real wb = (b == 0) ? w0 : w1;
          sum += wc*wb*(w1*tm(m,n,k+c,j+b,i-1) + w0*tm(m,n,k+c,j+b,i)
                        + w1*tm(m,n,k+c,j+b,i+1));
        }
      }
      wk(m,n,k,j,i) = sum;
    });
    par_for("nrpic_filter_copy", DevExeSpace(), 0, nmb1, 0, nv1, ks, ke, js, je, is, ie,
    KOKKOS_LAMBDA(const int m, const int n, const int k, const int j, const int i) {
      tm(m,n,k,j,i) = wk(m,n,k,j,i);
    });
  }

  // proper-volume integrals of the filtered E and S_i.  The filter acts on the sources
  // themselves (which carry 1/sqrt(gamma)) and across refinement boundaries, so these
  // integrals differ from the particle sums by a small amount, recorded in the history.
  auto sz = pmy_pack->pmb->mb_size.d_view;
  auto m1 = met1;
  const int n1 = indcs.nx1, n2 = indcs.nx2, n3 = indcs.nx3;
  const int ncell = (nmb1 + 1)*n3*n2*n1;
  Real se = 0.0, sx = 0.0, sy = 0.0, szz = 0.0;
  Kokkos::parallel_reduce("nrpic_filtsum", Kokkos::RangePolicy<DevExeSpace>(0, ncell),
  KOKKOS_LAMBDA(const int idx, Real &lse, Real &lsx, Real &lsy, Real &lsz) {
    int m = idx/(n3*n2*n1);
    int rem = idx - m*(n3*n2*n1);
    int k = rem/(n2*n1);
    rem -= k*(n2*n1);
    int j = rem/n1;
    int i = rem - j*n1;
    k += ks; j += js; i += is;
    const Real det = adm::SpatialDet(m1(m,NRM_GXX,k,j,i), m1(m,NRM_GXY,k,j,i),
                                     m1(m,NRM_GXZ,k,j,i), m1(m,NRM_GYY,k,j,i),
                                     m1(m,NRM_GYZ,k,j,i), m1(m,NRM_GZZ,k,j,i));
    const Real w = sqrt(det)*sz(m).dx1*sz(m).dx2*sz(m).dx3;
    lse += tm(m,Tmunu::I_Tmunu_E,k,j,i)*w;
    lsx += tm(m,Tmunu::I_Tmunu_Sx,k,j,i)*w;
    lsy += tm(m,Tmunu::I_Tmunu_Sy,k,j,i)*w;
    lsz += tm(m,Tmunu::I_Tmunu_Sz,k,j,i)*w;
  }, Kokkos::Sum<Real>(se), Kokkos::Sum<Real>(sx), Kokkos::Sum<Real>(sy),
     Kokkos::Sum<Real>(szz));
  dep_sum_filt[0] = se; dep_sum_filt[1] = sx; dep_sum_filt[2] = sy; dep_sum_filt[3] = szz;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicStepSources
//! \brief with <particles> source_density, writes the sources of the next spacetime
//! step in density form, D = sqrt(gamma) x (deposited and filtered sources).  The
//! particle sums change slowly, the volume element changes at the expansion rate: the
//! spacetime solver multiplies D by 1/sqrt(gamma) of each of its stages, which removes
//! the first-order error of sources held fixed over the step.  With source_extrap the
//! densities are extrapolated to the middle of the step from the last two deposits.

void Particles::NrpicStepSources() {
  if (!nropt.source_density) return;
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
  const int nmb1 = pmy_pack->nmb_thispack - 1;
  const int nv1 = Tmunu::N_Tmunu - 1;
  if (!pmy_pack->ptmunu->step_density) {
    // first call: the source container exists only after the particle module has
    // been constructed, so the step arrays are allocated here
    pmy_pack->ptmunu->AllocateStepSources();
    pmy_pack->ptmunu->lambda8pi = nropt.lambda/(8.0*M_PI);
    int nmb = std::max((pmy_pack->nmb_thispack), (pmy_pack->pmesh->nmb_maxperrank));
    Kokkos::realloc(tm_prev, nmb, Tmunu::N_Tmunu, indcs.nx3 + 2*indcs.ng,
                    indcs.nx2 + 2*indcs.ng, indcs.nx1 + 2*indcs.ng);
    tm_prev_valid = false;
  }
  auto tm = pmy_pack->ptmunu->u_tmunu;
  auto ts = pmy_pack->ptmunu->u_tmunu_step;
  auto tp = tm_prev;
  auto m1 = met1;
  const bool extrap = nropt.source_extrap && tm_prev_valid;
  par_for("nrpic_stepsrc", DevExeSpace(), 0, nmb1, 0, nv1, ks, ke, js, je, is, ie,
  KOKKOS_LAMBDA(const int m, const int n, const int k, const int j, const int i) {
    const Real det = adm::SpatialDet(m1(m,NRM_GXX,k,j,i), m1(m,NRM_GXY,k,j,i),
                                     m1(m,NRM_GXZ,k,j,i), m1(m,NRM_GYY,k,j,i),
                                     m1(m,NRM_GYZ,k,j,i), m1(m,NRM_GZZ,k,j,i));
    const Real d = (det > 0.0) ? tm(m,n,k,j,i)*sqrt(det) : 0.0;
    ts(m,n,k,j,i) = extrap ? (1.5*d - 0.5*tp(m,n,k,j,i)) : d;
    tp(m,n,k,j,i) = d;
  });
  tm_prev_valid = true;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAddLambda
//! \brief adds a cosmological constant Lambda to the sources as vacuum energy,
//!   E += Lambda/(8 pi),  S_ij -= Lambda/(8 pi) gamma_ij,
//! after the particle sources have been deposited and filtered

void Particles::NrpicAddLambda() {
  if (nropt.lambda == 0.0) return;
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
  const int nmb1 = pmy_pack->nmb_thispack - 1;
  auto tm = pmy_pack->ptmunu->u_tmunu;
  auto m1 = met1;
  const Real rl = nropt.lambda/(8.0*M_PI);
  par_for("nrpic_lambda", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    tm(m,Tmunu::I_Tmunu_E,k,j,i)   += rl;
    tm(m,Tmunu::I_Tmunu_Sxx,k,j,i) -= rl*m1(m,NRM_GXX,k,j,i);
    tm(m,Tmunu::I_Tmunu_Sxy,k,j,i) -= rl*m1(m,NRM_GXY,k,j,i);
    tm(m,Tmunu::I_Tmunu_Sxz,k,j,i) -= rl*m1(m,NRM_GXZ,k,j,i);
    tm(m,Tmunu::I_Tmunu_Syy,k,j,i) -= rl*m1(m,NRM_GYY,k,j,i);
    tm(m,Tmunu::I_Tmunu_Syz,k,j,i) -= rl*m1(m,NRM_GYZ,k,j,i);
    tm(m,Tmunu::I_Tmunu_Szz,k,j,i) -= rl*m1(m,NRM_GZZ,k,j,i);
  });
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus Particles::NrpicDeposit
//! \brief deposits and filters the matter sources at t^{n+1} and re-evaluates the
//! constraints with them

TaskStatus Particles::NrpicDeposit(Driver *pdriver, int stage) {
  if (!nropt.deposit) return TaskStatus::complete;
  NrpicDepositSources();
  NrpicFilterSources();
  NrpicStepSources();
  NrpicAddLambda();
  z4c::Z4c *pz4c = pmy_pack->pz4c;
  if (pz4c != nullptr) {
    switch (pmy_pack->pmesh->mb_indcs.ng) {
      case 2: pz4c->ADMConstraints<2>(pmy_pack); break;
      case 3: pz4c->ADMConstraints<3>(pmy_pack); break;
      case 4: pz4c->ADMConstraints<4>(pmy_pack); break;
    }
  }
  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicInitializeSources
//! \brief brings the particle module to a consistent state on the current mesh: metric
//! arrays, MeshBlock ownership and deposited sources.  Called at the start of a run,
//! after a restart, and after every change of the mesh by AMR.

void Particles::NrpicInitializeSources() {
  if (nropt.metric != NrpicMetric::mesh) return;
  z4c::Z4c *pz4c = pmy_pack->pz4c;
  if (pz4c != nullptr) {
    pz4c->Z4cToADM(pmy_pack);
  }
  NrpicFillMetric(met1);
  NrpicAssignBlocks();
  NrpicRemoveFlagged();
  if (nropt.deposit) {
    // the mesh may have changed: the sources of the previous deposit are not usable.
    // Two deposits give the adaptive level cap a density estimate on the new mesh.
    e_prev_valid = false;
    tm_prev_valid = false;
    NrpicDepositSources();
    if (nropt.deposit_adaptive) {
      NrpicDepositSources();
    }
    NrpicFilterSources();
    NrpicStepSources();
    NrpicAddLambda();
    if (pz4c != nullptr) {
      switch (pmy_pack->pmesh->mb_indcs.ng) {
        case 2: pz4c->ADMConstraints<2>(pmy_pack); break;
        case 3: pz4c->ADMConstraints<3>(pmy_pack); break;
        case 4: pz4c->ADMConstraints<4>(pmy_pack); break;
      }
    }
  }
}

} // namespace particles
