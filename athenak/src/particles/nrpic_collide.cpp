//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_collide.cpp
//! \brief Monte Carlo collisions between the massive particles of the NRPIC module:
//! elastic, isotropic two-body scattering in the centre-of-momentum frame, evaluated in
//! the orthonormal frame of the normal observer of each collision cell (an
//! Einstein-Boltzmann solver for a self-interacting species).  Design, options, outputs
//! and tests: tracks/core/interfaces/collisions.md.
//!
//! One collision step (task NrpicCollide, after the particles have been pushed and
//! assigned to their MeshBlocks, before the deposit):
//!   1. every massive particle inside the mesh gets its collision cell: the mesh cell
//!      (or a block of f^3 mesh cells) of the leaf MeshBlock that contains it, found
//!      from global face positions so that it does not depend on the MeshBlock division;
//!   2. the particles are bucketed by cell (count, prefix sum, fill);
//!   3. one kernel per cell: metric and triad of the cell, then for each sub-step the
//!      particles are ordered by a random word keyed by their tag, neighbours in that
//!      order form pairs, and a pair collides with the probability
//!        P = (N - 1) sigma_m M_max v_Mol alpha dt / (n_sub sqrt(gamma) dV).
//! All draws come from utils/rng.hpp with keys made of the seed, the particle tags, the
//! cycle and the sub-step; a cell is processed sequentially by one thread.  The result
//! therefore does not depend on the MeshBlock division, on the storage order of the
//! particles, on the order in which the cells are visited or on a restart.
//!
//! Options in <particles> (absent: no effect at all):
//!   collisions       = true       switches the operator on
//!   coll_sigma       = s          cross-section per unit mass (code units, a length)
//!   coll_sigma_model = constant   | cutoff: s/(1 + (v_rel/w)^2)^2, w = coll_sigma_w
//!   coll_pmax        = 0.1        largest pair probability per sub-step aimed at
//!   coll_subcycle    = measured   | conservative (bound v_Mol < 2)
//!   coll_nsub_max    = 1000       largest number of sub-steps of a cell
//!   coll_cell_factor = 1          | 2 | 4: collision cell = f^3 mesh cells
//!   coll_weights     = equal      | nanbu (unequal rest masses of macroparticles)
//!   coll_hist_dcycle = 1          cycles between records of <basename>.coll.hst
//!   coll_dump_cycle  = -1         cycle whose collision step is dumped (replay test)
//! The seed is <job> rng_seed.

#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "coordinates/adm.hpp"
#include "coordinates/cell_locations.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_metrics.hpp"
#include "particles/nrpic_mesh.hpp"
#include "particles/nrpic_collide.hpp"
#include "utils/rng.hpp"
#include "utils/rng_mesh.hpp"

namespace particles {

namespace {

// refinement levels (relative to the root mesh) for which face positions are tabulated
constexpr int kCollMaxLevel = 23;

struct CollFaceOffsets {
  int b[3][kCollMaxLevel + 1];     // first entry of (direction, level) in the face table
};

//----------------------------------------------------------------------------------------
//! \struct CollStats
//! \brief sums over the collision cells of one step (reduction type: sums are added,
//! extrema combined).  They go to the history file only and never into the particles.

struct CollStats {
  std::int64_t n_part = 0;     // particles in usable collision cells
  std::int64_t n_occ = 0;      // collision cells with at least one particle
  std::int64_t n_cells = 0;    // collision cells with at least two particles
  std::int64_t n_tested = 0;   // pairs tested, all sub-steps
  std::int64_t n_coll = 0;     // collisions
  std::int64_t n_upd = 0;      // momentum updates
  std::int64_t n_trunc = 0;    // tested pairs with probability above one
  std::int64_t n_bad = 0;      // occupied cells skipped (unusable metric)
  std::int64_t sum_nsub = 0;   // sub-steps summed over cells with at least two particles
  int max_nsub = 0;
  int min_n = std::numeric_limits<int>::max();
  Real sum_p = 0.0;            // sum of the probabilities of the tested pairs
  Real max_p = 0.0;
  Real max_dxmfp = 0.0;        // largest cell size over mean free path
  Real sum_mw = 0.0;           // sum of M W after the step (cell frames)
  Real sum_mu[3] = {0.0, 0.0, 0.0};   // sum of M u_i after the step
  Real de = 0.0;               // change of the pair energies, summed
  Real dp[3] = {0.0, 0.0, 0.0};       // change of the pair momenta (triad), summed
  Real abs_de = 0.0;           // sum of |change of a pair energy|
  Real abs_dp = 0.0;           // sum of the largest |change of a pair momentum component|

  KOKKOS_INLINE_FUNCTION
  void operator+=(const CollStats &o) {
    n_part += o.n_part; n_occ += o.n_occ; n_cells += o.n_cells; n_tested += o.n_tested;
    n_coll += o.n_coll; n_upd += o.n_upd; n_trunc += o.n_trunc; n_bad += o.n_bad;
    sum_nsub += o.sum_nsub;
    max_nsub = (o.max_nsub > max_nsub) ? o.max_nsub : max_nsub;
    min_n = (o.min_n < min_n) ? o.min_n : min_n;
    sum_p += o.sum_p;
    max_p = (o.max_p > max_p) ? o.max_p : max_p;
    max_dxmfp = (o.max_dxmfp > max_dxmfp) ? o.max_dxmfp : max_dxmfp;
    sum_mw += o.sum_mw;
    de += o.de;
    abs_de += o.abs_de;
    abs_dp += o.abs_dp;
    for (int i=0; i<3; ++i) {
      sum_mu[i] += o.sum_mu[i];
      dp[i] += o.dp[i];
    }
  }
};

//----------------------------------------------------------------------------------------
//! \fn CollAnalyticMetric
//! \brief 3+1 fields of an analytic metric source of the module at the point x

KOKKOS_INLINE_FUNCTION
void CollAnalyticMetric(const NrpicMetric msrc, const Real mass, const Real spin,
                        const Real lat_dx, const Real x[3], nrpic::AdmPoint &ap) {
  if (msrc == NrpicMetric::kerr_schild) {
    nrpic::KerrSchildCart met{mass, spin};
    met(1, x, ap);
  } else if (msrc == NrpicMetric::kerr_schild_sph) {
    nrpic::KerrSchildSph met{mass, spin};
    met(1, x, ap);
  } else if (msrc == NrpicMetric::boyer_lindquist) {
    nrpic::BoyerLindquist met{mass, spin};
    met(1, x, ap);
  } else {
    nrpic::LatticeMetric<nrpic::KerrSchildCart> met{{mass, spin}, {0.0, 0.0, 0.0},
                                                    {lat_dx, lat_dx, lat_dx}};
    met(1, x, ap);
  }
}

void CollFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic collisions" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

//----------------------------------------------------------------------------------------
//! \fn CollWriteHistory
//! \brief starts <basename>.coll.hst (header) and/or appends the record of one
//! collision step to it

void CollWriteHistory(const std::string &fname, const bool header, const bool record,
                      const Real time, const int ncycle, const CollStats &st) {
  std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
  if (fp == nullptr) CollFatal("cannot open " + fname);
  if (header) {
    std::fprintf(fp, "# NRPIC collision history (one record: the collision step of that "
                 "cycle)\n");
    std::fprintf(fp, "# [1]=time [2]=ncycle [3]=n_part [4]=n_cells [5]=n_tested "
                 "[6]=sum_P [7]=n_coll [8]=n_updated [9]=n_trunc [10]=max_P "
                 "[11]=max_nsub [12]=mean_nsub [13]=min_N [14]=mean_N [15]=max_dx_mfp "
                 "[16]=sum_MW [17]=sum_Mu1 [18]=sum_Mu2 [19]=sum_Mu3 [20]=dE [21]=dP1 "
                 "[22]=dP2 [23]=dP3 [24]=abs_dE [25]=abs_dP [26]=n_bad_cells\n");
  }
  if (record) {
    const double mean_nsub = (st.n_cells > 0) ?
        static_cast<double>(st.sum_nsub)/static_cast<double>(st.n_cells) : 0.0;
    const double mean_n = (st.n_occ > 0) ?
        static_cast<double>(st.n_part)/static_cast<double>(st.n_occ) : 0.0;
    const int min_n = (st.n_occ > 0) ? st.min_n : 0;
    std::fprintf(fp, "%.15e %d %" PRId64 " %" PRId64 " %" PRId64 " %.15e %" PRId64
                 " %" PRId64 " %" PRId64 " %.15e %d %.15e %d %.15e %.15e %.17e %.17e"
                 " %.17e %.17e %.15e %.15e %.15e %.15e %.15e %.15e %" PRId64 "\n",
                 time, ncycle, st.n_part, st.n_cells, st.n_tested, st.sum_p, st.n_coll,
                 st.n_upd, st.n_trunc, st.max_p, st.max_nsub, mean_nsub, min_n, mean_n,
                 st.max_dxmfp, st.sum_mw, st.sum_mu[0], st.sum_mu[1], st.sum_mu[2],
                 st.de, st.dp[0], st.dp[1], st.dp[2], st.abs_de, st.abs_dp, st.n_bad);
  }
  std::fclose(fp);
}

} // namespace

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicCollideInit
//! \brief reads the options of the collision operator; nothing is added to the input
//! parameters unless <particles> collisions is present

void Particles::NrpicCollideInit(ParameterInput *pin) {
  coll.on = false;
  if (!pin->DoesParameterExist("particles", "collisions")) return;
  coll.on = pin->GetBoolean("particles", "collisions");
  if (!coll.on) return;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;

  coll.sigma = pin->GetOrAddReal("particles", "coll_sigma", 0.0);
  coll.sigma_w = pin->GetOrAddReal("particles", "coll_sigma_w", 1.0);
  coll.pmax = pin->GetOrAddReal("particles", "coll_pmax", 0.1);
  coll.nsub_max = pin->GetOrAddInteger("particles", "coll_nsub_max", 1000);
  coll.cell_factor = pin->GetOrAddInteger("particles", "coll_cell_factor", 1);
  coll.hist_dcycle = pin->GetOrAddInteger("particles", "coll_hist_dcycle", 1);
  coll.dump_cycle = pin->GetOrAddInteger("particles", "coll_dump_cycle", -1);
  const std::string model = pin->GetOrAddString("particles", "coll_sigma_model",
                                                "constant");
  const std::string sub = pin->GetOrAddString("particles", "coll_subcycle", "measured");
  const std::string wts = pin->GetOrAddString("particles", "coll_weights", "equal");
  if (model.compare("constant") == 0) {
    coll.model = nrpic::kCollSigmaConstant;
  } else if (model.compare("cutoff") == 0) {
    coll.model = nrpic::kCollSigmaCutoff;
  } else {
    CollFatal("<particles> coll_sigma_model = '" + model + "' not recognized "
              "(constant or cutoff)");
  }
  if (sub.compare("measured") == 0) {
    coll.subcycle = 0;
  } else if (sub.compare("conservative") == 0) {
    coll.subcycle = 1;
  } else {
    CollFatal("<particles> coll_subcycle = '" + sub + "' not recognized "
              "(measured or conservative)");
  }
  if (wts.compare("equal") == 0) {
    coll.weights = 0;
  } else if (wts.compare("nanbu") == 0) {
    coll.weights = 1;
  } else {
    CollFatal("<particles> coll_weights = '" + wts + "' not recognized "
              "(equal or nanbu)");
  }
  if (!(coll.sigma >= 0.0)) CollFatal("<particles> coll_sigma must not be negative");
  if (!(coll.sigma_w > 0.0)) CollFatal("<particles> coll_sigma_w must be positive");
  if (!(coll.pmax > 0.0)) CollFatal("<particles> coll_pmax must be positive");
  if (coll.nsub_max < 1) CollFatal("<particles> coll_nsub_max must be at least 1");
  const int f = coll.cell_factor;
  if (f != 1 && f != 2 && f != 4) {
    CollFatal("<particles> coll_cell_factor must be 1, 2 or 4");
  }
  if (indcs.nx1 % f != 0 || indcs.nx2 % f != 0 || indcs.nx3 % f != 0) {
    CollFatal("<particles> coll_cell_factor must divide the cells of a MeshBlock in "
              "every direction");
  }
  coll.seed = rng::RunSeed(pin);
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus Particles::NrpicCollide
//! \brief one collision step at t^{n+1}: positions, momenta and metric are those after
//! the push; the cycle counter still holds the number of the step that is being taken

TaskStatus Particles::NrpicCollide(Driver *pdriver, int stage) {
  if (!coll.on) return TaskStatus::complete;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int np = nprtcl_thispack;
  const int nmb = pmy_pack->nmb_thispack;
  const int gids = pmy_pack->gids;
  const int f = coll.cell_factor;
  const int nx[3] = {indcs.nx1, indcs.nx2, indcs.nx3};
  const int nc1 = nx[0]/f, nc2 = nx[1]/f, nc3 = nx[2]/f;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const std::int64_t ncell64 = static_cast<std::int64_t>(nmb)*nc3*nc2*nc1;
  if (ncell64 >= std::numeric_limits<int>::max()) {
    CollFatal("too many collision cells for a 32-bit index");
  }
  const int ncell = static_cast<int>(ncell64);
  const int ncyc = pm->ncycle + 1;
  const bool write_hist = (coll.hist_dcycle > 0);
  const bool dump = (pm->ncycle == coll.dump_cycle);

  // ---- (0) work arrays and face positions of the mesh on every level in use
  if (static_cast<int>(coll_cell.extent(0)) != np) {
    Kokkos::realloc(coll_cell, np);
    Kokkos::realloc(coll_list, np);
    Kokkos::realloc(coll_key, np);
  }
  if (static_cast<int>(coll_count.extent(0)) != ncell + 1) {
    Kokkos::realloc(coll_count, ncell + 1);
    Kokkos::realloc(coll_begin, ncell + 1);
  }
  int maxlev = 0;
  for (int m=0; m<nmb; ++m) {
    const int lev = pm->lloc_eachmb[gids + m].level - pm->root_level;
    maxlev = (lev > maxlev) ? lev : maxlev;
  }
  if (maxlev > kCollMaxLevel) CollFatal("too many refinement levels");
  const int mnx[3] = {pm->mesh_indcs.nx1, pm->mesh_indcs.nx2, pm->mesh_indcs.nx3};
  const Real mxmin[3] = {pm->mesh_size.x1min, pm->mesh_size.x2min, pm->mesh_size.x3min};
  const Real mxmax[3] = {pm->mesh_size.x1max, pm->mesh_size.x2max, pm->mesh_size.x3max};
  CollFaceOffsets fb;
  std::int64_t nface = 0;
  for (int d=0; d<3; ++d) {
    for (int l=0; l<=kCollMaxLevel; ++l) {
      fb.b[d][l] = static_cast<int>(nface);
      if (l <= maxlev) { nface += (static_cast<std::int64_t>(mnx[d]) << l) + 1; }
    }
  }
  if (nface >= std::numeric_limits<int>::max()) {
    CollFatal("face table too large");
  }
  if (coll.face_maxlev != maxlev) {
    // faces of the mesh on level l: the formula of the MeshBlock edges (meshblock.cpp)
    Kokkos::realloc(coll_face, nface);
    auto fh = Kokkos::create_mirror_view(coll_face);
    for (int d=0; d<3; ++d) {
      for (int l=0; l<=maxlev; ++l) {
        const int n = mnx[d] << l;
        for (int i=0; i<=n; ++i) {
          fh(fb.b[d][l] + i) = (i == 0) ? mxmin[d] :
              ((i == n) ? mxmax[d] : LeftEdgeX(i, n, mxmin[d], mxmax[d]));
        }
      }
    }
    Kokkos::deep_copy(coll_face, fh);
    coll.face_maxlev = maxlev;
    // the edges of the MeshBlocks must be among these faces, bit for bit: then the cell
    // of a particle does not depend on the division of the mesh into MeshBlocks
    auto &mbs = pmy_pack->pmb->mb_size;
    int nbad = 0;
    for (int m=0; m<nmb; ++m) {
      const LogicalLocation &ll = pm->lloc_eachmb[gids + m];
      const int l = ll.level - pm->root_level;
      const std::int64_t i0[3] = {static_cast<std::int64_t>(ll.lx1)*nx[0],
                                  static_cast<std::int64_t>(ll.lx2)*nx[1],
                                  static_cast<std::int64_t>(ll.lx3)*nx[2]};
      const Real lo[3] = {mbs.h_view(m).x1min, mbs.h_view(m).x2min, mbs.h_view(m).x3min};
      const Real hi[3] = {mbs.h_view(m).x1max, mbs.h_view(m).x2max, mbs.h_view(m).x3max};
      for (int d=0; d<3; ++d) {
        if (fh(fb.b[d][l] + i0[d]) != lo[d]) { ++nbad; }
        if (fh(fb.b[d][l] + i0[d] + nx[d]) != hi[d]) { ++nbad; }
      }
    }
    if (nbad > 0 && !coll.face_warned) {
      coll.face_warned = true;
      std::cout << "NRPIC collisions: " << nbad << " MeshBlock edge(s) differ from the "
                << "tabulated face positions; a particle within rounding of such an edge "
                << "may be put into a different collision cell for a different "
                << "MeshBlock division" << std::endl;
    }
  }
  auto off = rng::CellOffsets(pmy_pack);

  CollStats stats;
  if (np > 0) {
    auto pr = prtcl_rdata;
    auto pi = prtcl_idata;
    auto sz = pmy_pack->pmb->mb_size.d_view;
    auto pcell = coll_cell;
    auto lst = coll_list;
    auto skey = coll_key;
    auto cnt = coll_count;
    auto cbeg = coll_begin;
    auto face = coll_face;
    const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
    const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
    const bool per[3] = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};

    // ---- (1) collision cell of every particle (-1: takes no part), cell populations
    Kokkos::deep_copy(DevExeSpace(), cnt, 0);
    Real mmin = std::numeric_limits<Real>::max(), mmax = 0.0;
    Kokkos::parallel_reduce("nrpic_coll_cell", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, Real &lmin, Real &lmax) {
      pcell(p) = -1;
      if (pi(PGID,p) < 0) return;                 // flagged for removal
      const Real mp = pr(IPM,p);
      if (!(mp > 0.0)) return;                    // null particles and light rays
      Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
      if (!(Kokkos::isfinite(x[0] + x[1] + x[2]))) return;
      for (int d=0; d<3; ++d) { x[d] = nrpic::WrapCoord(x[d], dmin[d], dlen[d], per[d]); }
      const int m = nrpic::FindBlock(sz, nmb, pi(PGID,p) - gids, x[0], x[1], x[2]);
      if (m < 0) return;                          // outside the mesh
      const int lev = static_cast<int>(off(m,3));
      int ic[3];
      for (int d=0; d<3; ++d) {
        const std::int64_t ig = nrpic::CollCellIndex(face, fb.b[d][lev], off(m,4+d), x[d]);
        int il = static_cast<int>(ig - off(m,d));
        il = (il < 0) ? 0 : ((il > nx[d]-1) ? nx[d]-1 : il);
        ic[d] = il/f;
      }
      const int c = ((m*nc3 + ic[2])*nc2 + ic[1])*nc1 + ic[0];
      pcell(p) = c;
      Kokkos::atomic_add(&cnt(c), 1);
      lmin = fmin(lmin, mp);
      lmax = fmax(lmax, mp);
    }, Kokkos::Min<Real>(mmin), Kokkos::Max<Real>(mmax));
    if (coll.weights == 0 && mmax > 0.0 && (mmax - mmin) > 1.0e-12*mmax) {
      char buf[160];
      std::snprintf(buf, sizeof(buf), "%.17g and %.17g", mmin, mmax);
      CollFatal(std::string("<particles> coll_weights = equal, but the colliding ")
                + "particles have unequal rest masses (smallest and largest: " + buf
                + "); use equal masses or coll_weights = nanbu");
    }

    // ---- (2) particle lists of the cells: prefix sum of the populations, then fill
    int ntot = 0;
    Kokkos::parallel_scan("nrpic_coll_scan", Kokkos::RangePolicy<DevExeSpace>(0, ncell+1),
    KOKKOS_LAMBDA(const int c, int &upd, const bool final) {
      if (final) { cbeg(c) = upd; }
      upd += cnt(c);
    }, ntot);
    Kokkos::deep_copy(DevExeSpace(), cnt, cbeg);          // cursor of every cell
    par_for("nrpic_coll_fill", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
      const int c = pcell(p);
      if (c >= 0) {
        const int slot = Kokkos::atomic_fetch_add(&cnt(c), 1);
        lst(slot) = p;
      }
    });

    // state before the collisions and per-particle records of the replay dump
    HostArray2D<Real> rbefore;
    DvceArray2D<Real> dmet;
    DvceArray2D<int> dint;
    if (dump) {
      rbefore = HostArray2D<Real>("coll_rbefore", nrdata, np);
      Kokkos::deep_copy(rbefore, prtcl_rdata);
      Kokkos::realloc(dmet, 8, np);
      Kokkos::realloc(dint, 2, np);
    }

    // ---- (3) the cells
    const bool mesh_metric = (nropt.metric == NrpicMetric::mesh);
    const NrpicMetric msrc = nropt.metric;
    const Real bh_mass = nropt.mass, bh_spin = nropt.spin, lat_dx = nropt.lattice_dx;
    const int triad = nropt.triad;
    auto m1 = met1;
    const Real dt = pm->dt;
    const Real sigma0 = coll.sigma, sigw = coll.sigma_w, pmax = coll.pmax;
    const int model = coll.model, nsub_max = coll.nsub_max;
    const bool conservative = (coll.subcycle == 1);
    const bool nanbu = (coll.weights == 1);
    const std::uint64_t seed = coll.seed;
    const std::uint64_t step = static_cast<std::uint64_t>(pm->ncycle);
    const std::uint64_t st_pair = rng::Stream(rng::kStreamCollisions, 0);
    const std::uint64_t st_acc = rng::Stream(rng::kStreamCollisions, 1);
    const std::uint64_t st_dir = rng::Stream(rng::kStreamCollisions, 2);
    const Real f3 = static_cast<Real>(f*f*f);

    Kokkos::parallel_reduce("nrpic_collide", Kokkos::RangePolicy<DevExeSpace>(0, ncell),
    KOKKOS_LAMBDA(const int c, CollStats &ls) {
      const int b = cbeg(c);
      const int n = cbeg(c+1) - b;
      if (n < 1) return;
      const int m = c/(nc3*nc2*nc1);
      int rem = c - m*(nc3*nc2*nc1);
      const int kc = rem/(nc2*nc1);
      rem -= kc*(nc2*nc1);
      const int jc = rem/nc1;
      const int icx = rem - jc*nc1;

      // metric of the collision cell at its centre: lapse and spatial metric
      Real alp = 0.0;
      Real g[3][3];
      if (mesh_metric) {
        Real v[7] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        for (int kk=0; kk<f; ++kk) {
          for (int jj=0; jj<f; ++jj) {
            for (int ii=0; ii<f; ++ii) {
              const int k = ks + kc*f + kk, j = js + jc*f + jj, i = is + icx*f + ii;
              v[0] += m1(m,NRM_ALP,k,j,i);
              v[1] += m1(m,NRM_GXX,k,j,i);
              v[2] += m1(m,NRM_GXY,k,j,i);
              v[3] += m1(m,NRM_GXZ,k,j,i);
              v[4] += m1(m,NRM_GYY,k,j,i);
              v[5] += m1(m,NRM_GYZ,k,j,i);
              v[6] += m1(m,NRM_GZZ,k,j,i);
            }
          }
        }
        alp = v[0]/f3;
        g[0][0] = v[1]/f3; g[0][1] = v[2]/f3; g[0][2] = v[3]/f3;
        g[1][1] = v[4]/f3; g[1][2] = v[5]/f3; g[2][2] = v[6]/f3;
        g[1][0] = g[0][1]; g[2][0] = g[0][2]; g[2][1] = g[1][2];
      } else {
        const int lev = static_cast<int>(off(m,3));
        const int cc[3] = {icx, jc, kc};
        Real xc[3];
        for (int d=0; d<3; ++d) {
          const std::int64_t i0 = fb.b[d][lev] + off(m,d) + cc[d]*f;
          xc[d] = 0.5*(face(i0) + face(i0 + f));
        }
        nrpic::AdmPoint ap;
        CollAnalyticMetric(msrc, bh_mass, bh_spin, lat_dx, xc, ap);
        alp = ap.alp;
        for (int a=0; a<3; ++a) {
          for (int bb=0; bb<3; ++bb) { g[a][bb] = ap.g[a][bb]; }
        }
      }
      const Real det = adm::SpatialDet(g[0][0], g[0][1], g[0][2], g[1][1], g[1][2],
                                       g[2][2]);
      nrpic::Triad tr;
      nrpic::BuildTriad(triad, g, tr);
      Real chk = alp + det;
      for (int a=0; a<3; ++a) {
        for (int bb=0; bb<3; ++bb) { chk += tr.S[a][bb] + tr.Si[a][bb]; }
      }
      if (!(alp > 0.0) || !(det > 0.0) || !(Kokkos::isfinite(chk))) {
        ls.n_bad += 1;
        if (dump) {
          for (int q=0; q<n; ++q) {
            for (int v=0; v<8; ++v) { dmet(v,lst(b+q)) = 0.0; }
            dint(0,lst(b+q)) = 0;
            dint(1,lst(b+q)) = 0;
          }
        }
        return;
      }
      const Real vol = sqrt(det)*sz(m).dx1*sz(m).dx2*sz(m).dx3*f3;   // proper volume
      const Real dtau = alp*dt;                                      // proper time

      ls.n_occ += 1;
      ls.n_part += n;
      ls.min_n = (n < ls.min_n) ? n : ls.min_n;
      Real mcell = 0.0, msum = 0.0;
      for (int q=0; q<n; ++q) {
        const Real mp = pr(IPM,lst(b+q));
        mcell = fmax(mcell, mp);
        msum += mp;
      }
      ls.max_dxmfp = fmax(ls.max_dxmfp, cbrt(vol)*msum*sigma0/vol);
      if (dump) {
        for (int q=0; q<n; ++q) {
          const int p = lst(b+q);
          dmet(0,p) = alp;
          dmet(1,p) = g[0][0]; dmet(2,p) = g[0][1]; dmet(3,p) = g[0][2];
          dmet(4,p) = g[1][1]; dmet(5,p) = g[1][2]; dmet(6,p) = g[2][2];
          dmet(7,p) = vol;
          dint(0,p) = 0;
          dint(1,p) = 0;
        }
      }

      // triad components u_(m) = e^j_(m) u_j of the momentum of a particle
      auto to_triad = [&](const int p, Real uh[3]) {
        const Real u0 = pr(IPVX,p), u1 = pr(IPVY,p), u2 = pr(IPVZ,p);
        for (int a=0; a<3; ++a) {
          uh[a] = tr.Si[a][0]*u0 + tr.Si[a][1]*u1 + tr.Si[a][2]*u2;
        }
      };
      // order of the cell: by (pairing word, tag)
      auto less = [&](const int i, const int j) {
        const std::uint64_t ki = skey(b+i), kj = skey(b+j);
        if (ki != kj) return (ki < kj);
        return (pi(PTAG,lst(b+i)) < pi(PTAG,lst(b+j)));
      };
      auto swap = [&](const int i, const int j) {
        const std::uint64_t kt = skey(b+i);
        skey(b+i) = skey(b+j);
        skey(b+j) = kt;
        const int lt = lst(b+i);
        lst(b+i) = lst(b+j);
        lst(b+j) = lt;
      };

      int nsub = 0;
      if (n >= 2 && sigma0 > 0.0) {
        ls.n_cells += 1;
        // P = fac sigma_m M_max v_Mol for a full step
        const Real fac = static_cast<Real>(n - 1)*dtau/vol;
        // full-step probability of the pair at positions (qa, qb) of the ordered cell
        auto pair_prob = [&](const int qa, const int qb) {
          const int pa = lst(b+qa), pb = lst(b+qb);
          Real ua[3], ub[3], wa, wb;
          to_triad(pa, ua);
          to_triad(pb, ub);
          const Real g1 = nrpic::CollGammaRelM1(ua, ub, wa, wb);
          return fac*nrpic::CollSigma(model, sigma0, sigw, g1)
                 *fmax(pr(IPM,pa), pr(IPM,pb))*nrpic::CollMoller(g1, wa, wb);
        };
        nsub = 1;
        for (int s=0; s<nsub; ++s) {
          const std::uint64_t draw = static_cast<std::uint64_t>(s);
          for (int q=0; q<n; ++q) {
            const rng::Key key{seed, st_pair,
                               static_cast<std::uint64_t>(pi(PTAG,lst(b+q))), step};
            skey(b+q) = rng::Bits(key, draw);
          }
          nrpic::CollHeapSort(n, less, swap);
          const int q0 = (n % 2 == 1) ? 3 : 0;      // odd: the first three form a triple
          if (s == 0) {
            // number of sub-steps from the largest probability of this first pairing,
            // or from the bound v_Mol < 2
            Real pb = 0.0;
            if (conservative) {
              pb = fac*sigma0*mcell*2.0;
            } else {
              if (q0 == 3) {
                pb = fmax(pb, 0.5*pair_prob(0, 1));
                pb = fmax(pb, 0.5*pair_prob(1, 2));
                pb = fmax(pb, 0.5*pair_prob(2, 0));
              }
              for (int q=q0; q+1<n; q+=2) { pb = fmax(pb, pair_prob(q, q+1)); }
            }
            const Real rn = ceil(pb/pmax);
            if (!(rn < static_cast<Real>(nsub_max))) {
              nsub = nsub_max;
            } else if (rn > 1.0) {
              nsub = static_cast<int>(rn);
            }
          }
          const Real wsub = 1.0/static_cast<Real>(nsub);

          // test of one pair and, if it collides, its scattering
          auto collide = [&](const int qa, const int qb, const Real wgt) {
            int pa = lst(b+qa), pb = lst(b+qb);
            if (pi(PTAG,pa) > pi(PTAG,pb)) {       // "a" is the particle with the
              const int pt = pa;                   // smaller tag
              pa = pb;
              pb = pt;
            }
            const std::uint64_t ta = static_cast<std::uint64_t>(pi(PTAG,pa));
            const std::uint64_t tb = static_cast<std::uint64_t>(pi(PTAG,pb));
            Real ua[3], ub[3], wa, wb;
            to_triad(pa, ua);
            to_triad(pb, ub);
            const Real g1 = nrpic::CollGammaRelM1(ua, ub, wa, wb);
            const Real ma = pr(IPM,pa), mb = pr(IPM,pb);
            const Real mmx = fmax(ma, mb);
            const Real prob = wgt*fac*nrpic::CollSigma(model, sigma0, sigw, g1)*mmx
                              *nrpic::CollMoller(g1, wa, wb);
            ls.n_tested += 1;
            ls.sum_p += fmin(prob, 1.0);
            ls.max_p = fmax(ls.max_p, prob);
            if (prob > 1.0) { ls.n_trunc += 1; }
            double uu[4];
            rng::Uniform4(rng::Key{seed, st_acc, ta, step, tb}, draw, uu);
            if (!(uu[0] < prob)) return;
            double nh[3];
            rng::Direction(rng::Key{seed, st_dir, ta, step, tb}, draw, nh);
            Real uan[3], ubn[3];
            nrpic::CollScatter(ua, ub, wa, wb, g1, nh, uan, ubn);
            // unequal rest masses of the macroparticles: the lighter one always takes
            // its new momentum, the heavier one with probability M_min/M_max
            bool upa = true, upb = true;
            if (nanbu && ma != mb) {
              const bool heavy_updates = (uu[1] < fmin(ma, mb)/mmx);
              if (ma > mb) { upa = heavy_updates; } else { upb = heavy_updates; }
            }
            // change of the energy and momentum of the pair (rounding for equal masses)
            const Real wan = sqrt(1.0 + uan[0]*uan[0] + uan[1]*uan[1] + uan[2]*uan[2]);
            const Real wbn = sqrt(1.0 + ubn[0]*ubn[0] + ubn[1]*ubn[1] + ubn[2]*ubn[2]);
            const Real e0 = ma*wa + mb*wb;
            const Real e1 = ma*(upa ? wan : wa) + mb*(upb ? wbn : wb);
            ls.de += (e1 - e0);
            ls.abs_de += fabs(e1 - e0);
            Real dpm = 0.0;
            for (int a=0; a<3; ++a) {
              const Real p0 = ma*ua[a] + mb*ub[a];
              const Real p1 = ma*(upa ? uan[a] : ua[a]) + mb*(upb ? ubn[a] : ub[a]);
              ls.dp[a] += (p1 - p0);
              dpm = fmax(dpm, fabs(p1 - p0));
            }
            ls.abs_dp += dpm;
            // back to the coordinate components u_j = e^(m)_j u_(m)
            if (upa) {
              pr(IPVX,pa) = tr.S[0][0]*uan[0] + tr.S[0][1]*uan[1] + tr.S[0][2]*uan[2];
              pr(IPVY,pa) = tr.S[1][0]*uan[0] + tr.S[1][1]*uan[1] + tr.S[1][2]*uan[2];
              pr(IPVZ,pa) = tr.S[2][0]*uan[0] + tr.S[2][1]*uan[1] + tr.S[2][2]*uan[2];
              ls.n_upd += 1;
              if (dump) { dint(1,pa) += 1; }
            }
            if (upb) {
              pr(IPVX,pb) = tr.S[0][0]*ubn[0] + tr.S[0][1]*ubn[1] + tr.S[0][2]*ubn[2];
              pr(IPVY,pb) = tr.S[1][0]*ubn[0] + tr.S[1][1]*ubn[1] + tr.S[1][2]*ubn[2];
              pr(IPVZ,pb) = tr.S[2][0]*ubn[0] + tr.S[2][1]*ubn[1] + tr.S[2][2]*ubn[2];
              ls.n_upd += 1;
              if (dump) { dint(1,pb) += 1; }
            }
            ls.n_coll += 1;
          };

          if (q0 == 3) {
            collide(0, 1, 0.5*wsub);
            collide(1, 2, 0.5*wsub);
            collide(2, 0, 0.5*wsub);
          }
          for (int q=q0; q+1<n; q+=2) { collide(q, q+1, wsub); }
        }
        ls.sum_nsub += nsub;
        ls.max_nsub = (nsub > ls.max_nsub) ? nsub : ls.max_nsub;
      }
      if (dump) {
        for (int q=0; q<n; ++q) { dint(0,lst(b+q)) = nsub; }
      }

      // energy and momentum of the cell after the step, in its frame
      for (int q=0; q<n; ++q) {
        const int p = lst(b+q);
        Real uh[3];
        to_triad(p, uh);
        const Real mp = pr(IPM,p);
        ls.sum_mw += mp*sqrt(1.0 + uh[0]*uh[0] + uh[1]*uh[1] + uh[2]*uh[2]);
        ls.sum_mu[0] += mp*pr(IPVX,p);
        ls.sum_mu[1] += mp*pr(IPVY,p);
        ls.sum_mu[2] += mp*pr(IPVZ,p);
      }
    }, stats);

    // ---- replay dump: the state before and after this collision step
    if (dump) {
      char number[32];
      std::snprintf(number, sizeof(number), ".coll_dump.%d.bin", pm->ncycle);
      const std::string fname = nr_basename + number;
      std::FILE *fp = std::fopen(fname.c_str(), "wb");
      if (fp == nullptr) CollFatal("cannot open " + fname);
      auto rh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_rdata);
      auto ih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_idata);
      auto ch = Kokkos::create_mirror_view_and_copy(HostMemSpace(), coll_cell);
      auto mh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), dmet);
      auto dh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), dint);
      auto oh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), off);
      const char magic[9] = "NRPCOLD1";
      const std::int64_t head_i[3] = {np, pm->ncycle, f};
      const double head_d[4] = {pm->dt, coll.sigma, coll.sigma_w, coll.pmax};
      const std::int64_t head_j[4] = {coll.model, coll.weights, coll.subcycle,
                                      coll.nsub_max};
      const std::uint64_t seed64 = coll.seed;
      const std::int64_t triad64 = nropt.triad;
      std::fwrite(magic, 1, 8, fp);
      std::fwrite(head_i, sizeof(std::int64_t), 3, fp);
      std::fwrite(head_d, sizeof(double), 4, fp);
      std::fwrite(head_j, sizeof(std::int64_t), 4, fp);
      std::fwrite(&seed64, sizeof(std::uint64_t), 1, fp);
      std::fwrite(&triad64, sizeof(std::int64_t), 1, fp);
      std::vector<double> buf(18*static_cast<size_t>(np));
      std::vector<std::int32_t> ibuf(7*static_cast<size_t>(np));
      for (int p=0; p<np; ++p) {
        double *r = &buf[18*static_cast<size_t>(p)];
        std::int32_t *q = &ibuf[7*static_cast<size_t>(p)];
        r[0] = rbefore(IPX,p);  r[1] = rbefore(IPY,p);  r[2] = rbefore(IPZ,p);
        r[3] = rbefore(IPVX,p); r[4] = rbefore(IPVY,p); r[5] = rbefore(IPVZ,p);
        r[6] = rh(IPVX,p);      r[7] = rh(IPVY,p);      r[8] = rh(IPVZ,p);
        r[9] = rh(IPM,p);
        q[0] = ih(PTAG,p);
        const int c = ch(p);
        if (c < 0) {
          for (int v=0; v<8; ++v) { r[10+v] = 0.0; }
          q[1] = -1; q[2] = 0; q[3] = 0; q[4] = 0; q[5] = 0; q[6] = 0;
        } else {
          for (int v=0; v<8; ++v) { r[10+v] = mh(v,p); }
          const int m = c/(nc3*nc2*nc1);
          int rem = c - m*(nc3*nc2*nc1);
          const int kc = rem/(nc2*nc1);
          rem -= kc*(nc2*nc1);
          const int jc = rem/nc1;
          const int icx = rem - jc*nc1;
          q[1] = static_cast<std::int32_t>(oh(m,3));
          q[2] = static_cast<std::int32_t>(oh(m,0)/f + icx);
          q[3] = static_cast<std::int32_t>(oh(m,1)/f + jc);
          q[4] = static_cast<std::int32_t>(oh(m,2)/f + kc);
          q[5] = dh(0,p);
          q[6] = dh(1,p);
        }
      }
      std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
      std::fwrite(ibuf.data(), sizeof(std::int32_t), ibuf.size(), fp);
      std::fclose(fp);
    }
  }

  // record of the step; a new run starts a new file, a restarted run appends
  if (write_hist) {
    const bool fresh = (pm->ncycle == 0);
    const bool record = (ncyc % coll.hist_dcycle == 0);
    if (fresh || record) {
      CollWriteHistory(nr_basename + ".coll.hst", fresh, record, pm->time + pm->dt, ncyc,
                       stats);
    }
  }
  return TaskStatus::complete;
}

} // namespace particles
