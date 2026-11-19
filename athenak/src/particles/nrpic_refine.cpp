//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_refine.cpp
//! \brief Adaptive mesh refinement in periodic cosmological runs of the NRPIC module.
//!
//! The problem generator nrpic_cosmo enrols CosmoRefine as the refinement function of
//! <amr_criterion0> method = user.  It first applies the criteria of the spacetime
//! solver (<z4c_amr>: trivial, tracker, chi, dchi, lohner, and the radii), as nrpic_cf
//! does, and then the criteria of the block <particles_amr>, each read only if present:
//!
//!   ppc_refine      refine a MeshBlock in which a cell holds more than this many
//!                   particles, n = sqrt(gamma) E dV / <m W> (deposited energy of the
//!                   cell over the mean energy of a particle);
//!   ppc_derefine    allow derefinement where every cell holds fewer (default
//!                   ppc_refine/16: the eight cells merged by a derefinement then hold
//!                   at most half the refinement threshold);
//!   lapse_ratio_<l> (l = 1, 2, ...) a MeshBlock of level l-1 (0: root) is refined where
//!                   min(alpha) falls below this fraction of the volume mean of alpha
//!                   over the mesh; in the conformal-time gauge alpha = a in the
//!                   homogeneous universe, and the lapse falls behind in a collapsing
//!                   region;
//!   chi_ratio_<l>   the same with the conformal factor chi, the cosmological form of
//!                   <z4c_amr> method = chi (chi itself falls everywhere as 1/a^2);
//!   hysteresis      a block of level l may be derefined where the monitored ratio
//!                   exceeds (1 + hysteresis) times the threshold of level l
//!                   (default 0.1);
//!   max_level       finest level the criteria of this block ask for (default: the
//!                   finest level of the mesh);
//!   verbose         print the flags of every check.
//!
//! A MeshBlock is refined if any criterion asks for it, and may be derefined only if
//! every active criterion allows it.  With <z4c_amr> method = trivial that block has
//! no opinion on derefinement; its radii (radius_<n>_rad, radius_<n>_reflevel) still
//! set a minimum level around the origin.
//!
//! None of the criteria refines the homogeneous universe: the particle number per cell
//! is that of the lattice, and both ratios are one.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "mesh/mesh_refinement.hpp"
#include "coordinates/adm.hpp"
#include "z4c/z4c.hpp"
#include "z4c/z4c_amr.hpp"
#include "z4c/tmunu.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_cosmo_ext.hpp"

namespace nrpic {

namespace {

constexpr int kMaxLadder = 16;

struct RefineOptions {
  bool active = false;         // a criterion of <particles_amr> is present
  bool z4c_trivial = true;     // <z4c_amr> method = trivial
  Real ppc_refine = 0.0;       // > 0: criterion on the particle number per cell
  Real ppc_derefine = 0.0;
  int nlapse = 0;              // number of thresholds of the lapse ratio
  Real lapse_ratio[kMaxLadder];
  int nchi = 0;                // number of thresholds of the ratio of chi
  Real chi_ratio[kMaxLadder];
  Real hysteresis = 0.1;
  int max_level = 31;          // relative to the root level
  bool verbose = false;
  Real lambda8pi = 0.0;        // vacuum energy added to the sources (not particles)
};

RefineOptions ropt;

//! reads a ladder of thresholds <name>_1, <name>_2, ... until one is missing
int ReadLadder(ParameterInput *pin, const std::string &name, Real *val) {
  int n = 0;
  while (n < kMaxLadder &&
         pin->DoesParameterExist("particles_amr", name + "_" + std::to_string(n+1))) {
    val[n] = pin->GetReal("particles_amr", name + "_" + std::to_string(n+1));
    ++n;
  }
  return n;
}

} // namespace

//----------------------------------------------------------------------------------------
//! \fn void CosmoRefineInit
//! \brief reads the criteria of <particles_amr>

void CosmoRefineInit(ParameterInput *pin, Mesh *pm) {
  ropt = RefineOptions();
  if (pin->DoesParameterExist("z4c_amr", "method")) {
    ropt.z4c_trivial = (pin->GetString("z4c_amr", "method").compare("trivial") == 0);
  }
  if (pin->DoesParameterExist("particles_amr", "ppc_refine")) {
    ropt.ppc_refine = pin->GetReal("particles_amr", "ppc_refine");
    ropt.ppc_derefine = ropt.ppc_refine/16.0;
    if (pin->DoesParameterExist("particles_amr", "ppc_derefine")) {
      ropt.ppc_derefine = pin->GetReal("particles_amr", "ppc_derefine");
    }
    if (ropt.ppc_refine > 0.0 && 8.0*ropt.ppc_derefine > ropt.ppc_refine) {
      std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__
                << std::endl << "<particles_amr> ppc_derefine must not exceed ppc_refine/8: "
                << "a derefined MeshBlock would be refined again" << std::endl;
      std::exit(EXIT_FAILURE);
    }
  }
  ropt.nlapse = ReadLadder(pin, "lapse_ratio", ropt.lapse_ratio);
  ropt.nchi = ReadLadder(pin, "chi_ratio", ropt.chi_ratio);
  if (pin->DoesParameterExist("particles_amr", "hysteresis")) {
    ropt.hysteresis = pin->GetReal("particles_amr", "hysteresis");
  }
  if (pin->DoesParameterExist("particles_amr", "max_level")) {
    ropt.max_level = pin->GetInteger("particles_amr", "max_level");
  }
  if (pin->DoesParameterExist("particles_amr", "verbose")) {
    ropt.verbose = pin->GetBoolean("particles_amr", "verbose");
  }
  if (pin->DoesParameterExist("particles", "lambda")) {
    ropt.lambda8pi = pin->GetReal("particles", "lambda")/(8.0*M_PI);
  }
  ropt.active = (ropt.ppc_refine > 0.0 || ropt.nlapse > 0 || ropt.nchi > 0);
  if (ropt.active && global_variable::my_rank == 0) {
    std::cout << "NRPIC: refinement criteria of <particles_amr>:";
    if (ropt.ppc_refine > 0.0) {
      std::cout << " particles per cell above " << ropt.ppc_refine << " (derefine below "
                << ropt.ppc_derefine << ");";
    }
    if (ropt.nlapse > 0) { std::cout << " " << ropt.nlapse << " level(s) by lapse ratio;"; }
    if (ropt.nchi > 0) { std::cout << " " << ropt.nchi << " level(s) by chi ratio;"; }
    std::cout << " hysteresis " << ropt.hysteresis << std::endl;
  }
}

//----------------------------------------------------------------------------------------
//! \fn void CosmoRefine
//! \brief refinement function of nrpic_cosmo: sets Mesh::pmr->refine_flag

void CosmoRefine(MeshBlockPack *pmbp) {
  // the criteria of the spacetime solver (the request of Track A: adaptive refinement
  // with nrpic_cosmo called a null function pointer)
  pmbp->pz4c->pamr->Refine(pmbp);
  if (!ropt.active) return;

  Mesh *pmesh = pmbp->pmesh;
  auto &refine_flag = pmesh->pmr->refine_flag;
  auto &indcs = pmesh->mb_indcs;
  const int nmb = pmbp->nmb_thispack;
  const int mbs = pmesh->gids_eachrank[global_variable::my_rank];
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nkji = nx3*nx2*nx1, nji = nx2*nx1;
  auto sz = pmbp->pmb->mb_size.d_view;

  // ---- per MeshBlock: smallest lapse, smallest chi, their volume integrals, and the
  //      largest deposited energy of a cell
  DualArray2D<Real> blk("nrpic_refine_blk", nmb, 6);
  auto bd = blk.d_view;
  auto u0 = pmbp->pz4c->u0;
  const int ial = z4c::Z4c::I_Z4C_ALPHA, ichi = z4c::Z4c::I_Z4C_CHI;
  particles::Particles *ppart = pmbp->ppart;
  const bool use_ppc = (ropt.ppc_refine > 0.0 && ppart != nullptr && ppart->is_nrpic &&
                        ppart->nropt.deposit && pmbp->ptmunu != nullptr);
  DvceArray5D<Real> tm;
  if (use_ppc) { tm = pmbp->ptmunu->u_tmunu; }
  auto adm = pmbp->padm->adm;
  const Real lam = ropt.lambda8pi;
  // one thread per MeshBlock (the check runs every few cycles; a serial loop over the
  // cells of a block keeps the reduction per block simple on every back end)
  par_for("nrpic_refine_blk", DevExeSpace(), 0, nmb-1, KOKKOS_LAMBDA(const int m) {
    Real amin = 1.0e300, cmin = 1.0e300, asum = 0.0, csum = 0.0, emax = 0.0;
    for (int idx=0; idx<nkji; ++idx) {
      int k = idx/nji;
      int j = (idx - k*nji)/nx1;
      int i = (idx - k*nji - j*nx1) + is;
      j += js;
      k += ks;
      const Real al = u0(m,ial,k,j,i), ch = u0(m,ichi,k,j,i);
      amin = fmin(amin, al);
      cmin = fmin(cmin, ch);
      asum += al;
      csum += ch;
      if (use_ppc) {
        const Real det = adm::SpatialDet(adm.g_dd(m,0,0,k,j,i), adm.g_dd(m,0,1,k,j,i),
                                         adm.g_dd(m,0,2,k,j,i), adm.g_dd(m,1,1,k,j,i),
                                         adm.g_dd(m,1,2,k,j,i), adm.g_dd(m,2,2,k,j,i));
        if (det > 0.0) {
          emax = fmax(emax, (tm(m,Tmunu::I_Tmunu_E,k,j,i) - lam)*sqrt(det));
        }
      }
    }
    const Real vol = sz(m).dx1*sz(m).dx2*sz(m).dx3;
    bd(m,0) = amin;
    bd(m,1) = cmin;
    bd(m,2) = asum*vol;
    bd(m,3) = csum*vol;
    bd(m,4) = emax*vol;                          // largest energy of a cell
    bd(m,5) = vol*static_cast<Real>(nkji);       // coordinate volume of the MeshBlock
  });
  blk.template modify<DevExeSpace>();
  blk.template sync<HostMemSpace>();
  auto bh = blk.h_view;

  // volume means over the mesh
  Real vtot = 0.0, amean = 0.0, cmean = 0.0;
  for (int m=0; m<nmb; ++m) {
    vtot += bh(m,5);
    amean += bh(m,2);
    cmean += bh(m,3);
  }
#if MPI_PARALLEL_ENABLED
  {
    Real buf[3] = {vtot, amean, cmean};
    MPI_Allreduce(MPI_IN_PLACE, buf, 3, MPI_ATHENA_REAL, MPI_SUM, MPI_COMM_WORLD);
    vtot = buf[0]; amean = buf[1]; cmean = buf[2];
  }
#endif
  amean /= vtot;
  cmean /= vtot;
  // mean energy of a particle (the sum of m W of the last deposit)
  Real mbar = 0.0;
  if (use_ppc && pmesh->nprtcl_total > 0) {
    mbar = ppart->sum_mw/static_cast<Real>(pmesh->nprtcl_total);
  }

  // ---- flags of this block's criteria
  std::vector<int> f1(nmb, 0);
  int nup = 0, ndown = 0;
  for (int m=0; m<nmb; ++m) {
    const int level = pmesh->lloc_eachmb[m + mbs].level - pmesh->root_level;
    bool refine = false, keep = false;
    if (use_ppc && mbar > 0.0) {
      const Real n = bh(m,4)/mbar;
      if (n > ropt.ppc_refine) { refine = true; }
      if (n >= ropt.ppc_derefine) { keep = true; }
    }
    for (int c=0; c<2; ++c) {
      const int nl = (c == 0) ? ropt.nlapse : ropt.nchi;
      if (nl == 0) continue;
      const Real *thr = (c == 0) ? ropt.lapse_ratio : ropt.chi_ratio;
      const Real mean = (c == 0) ? amean : cmean;
      const Real ratio = (mean > 0.0) ? bh(m,c)/mean : 1.0;
      // level l-1 -> l where the ratio is below threshold l
      if (level < nl && ratio < thr[level]) { refine = true; }
      // a block of level l stays where the ratio is not above (1 + h) threshold l;
      // levels beyond the ladder are not wanted by this criterion
      if (level >= 1 && level <= nl &&
          !(ratio > (1.0 + ropt.hysteresis)*thr[level-1])) { keep = true; }
      // a ratio that is not a number keeps the block (the guard stops such a run)
      if (!(ratio == ratio)) { keep = true; }
    }
    if (refine && level < ropt.max_level) {
      f1[m] = 1;
      ++nup;
    } else if (!refine && !keep) {
      f1[m] = -1;
      ++ndown;
    }
  }

  // ---- combine with the flags of <z4c_amr>
  if (ropt.z4c_trivial) {
    for (int m=0; m<nmb; ++m) { refine_flag.h_view(m + mbs) = f1[m]; }
    refine_flag.template modify<HostMemSpace>();
    refine_flag.template sync<DevExeSpace>();
    pmbp->pz4c->pamr->RefineRadii(pmbp);       // the radii set a minimum level
  } else {
    for (int m=0; m<nmb; ++m) {
      refine_flag.h_view(m + mbs) = std::max(refine_flag.h_view(m + mbs), f1[m]);
    }
    refine_flag.template modify<HostMemSpace>();
    refine_flag.template sync<DevExeSpace>();
  }
  if (ropt.verbose && global_variable::my_rank == 0) {
    Real nmax = 0.0, armin = 1.0e300, crmin = 1.0e300;
    for (int m=0; m<nmb; ++m) {
      if (mbar > 0.0) { nmax = std::max(nmax, bh(m,4)/mbar); }
      armin = std::min(armin, bh(m,0)/amean);
      crmin = std::min(crmin, bh(m,1)/cmean);
    }
    std::cout << "NRPIC refine: cycle " << pmesh->ncycle << " time " << pmesh->time
              << " blocks " << nmb << " flagged +" << nup << " -" << ndown
              << "  max particles per cell " << nmax << "  min lapse ratio " << armin
              << "  min chi ratio " << crmin << std::endl;
  }
}

} // namespace nrpic
