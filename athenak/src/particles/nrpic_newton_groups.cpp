//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_newton_groups.cpp
//! \brief second moments of groups of particles in the Newtonian mode of the NRPIC
//! module (nrpic_newton.cpp), about the centroid of each group, so that a patch can be
//! followed apart from the particles around it (a background, a second patch).
//!
//! <particles> newton_ngroup = n (at most 8); group g = 1 .. n holds the particles with
//!   species newton_group<g>_species (-1 or absent: every species) and
//!   newton_group<g>_tag_min <= tag <= newton_group<g>_tag_max (absent: no bound).
//! In a periodic direction a position enters as its image nearest to the reference
//! point newton_group<g>_x1 .. _x3 (default: the middle of the mesh): a patch narrower
//! than half the box around that point is not cut by the wrap of the coordinates.
//!
//! With d the displacement from the reference point, v = dx/dt = p/a and the
//! acceleration acc = g/a - (da/dt / a) v that the kick applies (as in the history of
//! the mode), the sums over the particles of a group with their rest masses m are
//!   M = sum m,  X = sum m d / M,  V = sum m v / M,  A = sum m acc / M,
//!   I_ij   = sum m d_i d_j                         - M X_i X_j,
//!   I'_ij  = sum m (d_i v_j + v_i d_j)             - M (X_i V_j + V_i X_j),
//!   I''_ij = sum m (2 v_i v_j + d_i acc_j + acc_i d_j) - M (2 V_i V_j + X_i A_j + A_i X_j):
//! the second moment about the centroid in comoving coordinates and its derivatives in
//! the time t of the run (conformal time with expansion).  The second moment in
//! physical coordinates r = a x and its derivatives in cosmic time T, dT = a dt, follow
//! without further sums:
//!   J = a^2 I,   dJ/dT = 2 a' I + a I',   d2J/dT2 = (2 a''/a) I + (3 a'/a) I' + I''
//! (primes of a: derivatives in t).  The third derivatives are difference quotients of
//! the second ones over the last step, in t and in T, and belong to the middle of that
//! step.  They are not formed after a step shorter than 1e-6 of the one before (the
//! remainder step with which a run reaches its end time): the earlier values stay.
//!
//! One record per record of <basename>.newton.hst goes to <basename>.newton.g<g>.hst.
//! The sums need the force at every particle once more; they are formed only for the
//! states that are recorded and the states one cycle before them.

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <string>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_mesh.hpp"

namespace particles {

namespace {

void GroupFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_newton_groups.cpp" << std::endl << msg
            << std::endl;
  std::exit(EXIT_FAILURE);
}

// indices of the sums of one group
enum GroupSumIndex {
  GS_N = 0,        // number of particles
  GS_M = 1,        // sum m
  GS_X = 2,        // sum m d_i                      (3)
  GS_V = 5,        // sum m v_i                      (3)
  GS_A = 8,        // sum m acc_i                    (3)
  GS_I = 11,       // sum m d_i d_j                  (6: xx, xy, xz, yy, yz, zz)
  GS_DI = 17,      // sum m (d_i v_j + v_i d_j)      (6)
  GS_DDI = 23      // sum m (2 v_i v_j + d_i acc_j + acc_i d_j)   (6)
};

// scale factor of the mode, its first two derivatives in the time of the run, and the
// cosmic time T = int_0^t a dt
struct GroupScale {
  Real a, da, d2a, tcos;
};

GroupScale Scale(const NrpicOptions &o, const Real t) {
  GroupScale s;
  if (o.newton_expansion == 0) {
    s.a = 1.0; s.da = 0.0; s.d2a = 0.0; s.tcos = t;
    return s;
  }
  const Real h = o.newton_hubble, n = o.newton_exponent;
  const Real b = 1.0 + h*t/n;
  s.a = std::pow(b, n);
  s.da = h*std::pow(b, n - 1.0);
  s.d2a = h*h*((n - 1.0)/n)*std::pow(b, n - 2.0);
  s.tcos = (n/(h*(n + 1.0)))*(std::pow(b, n + 1.0) - 1.0);
  return s;
}

// moments of one group about its centroid from its sums: mom[0..5] = I, [6..11] = I',
// [12..17] = I'' (comoving, time of the run), [18..23] = J, [24..29] = dJ/dT,
// [30..35] = d2J/dT2 (physical, cosmic time); cen[0..2] = X, [3..5] = V
void Central(const Real *s, const GroupScale &sc, Real *mom, Real *cen) {
  const Real mass = s[GS_M];
  Real xc[3] = {0.0, 0.0, 0.0}, vc[3] = {0.0, 0.0, 0.0}, ac[3] = {0.0, 0.0, 0.0};
  if (mass > 0.0) {
    for (int d=0; d<3; ++d) {
      xc[d] = s[GS_X+d]/mass;
      vc[d] = s[GS_V+d]/mass;
      ac[d] = s[GS_A+d]/mass;
    }
  }
  int c = 0;
  for (int i=0; i<3; ++i) {
    for (int j=i; j<3; ++j) {
      mom[c]    = s[GS_I+c] - mass*xc[i]*xc[j];
      mom[6+c]  = s[GS_DI+c] - mass*(xc[i]*vc[j] + vc[i]*xc[j]);
      mom[12+c] = s[GS_DDI+c] - mass*(2.0*vc[i]*vc[j] + xc[i]*ac[j] + ac[i]*xc[j]);
      mom[18+c] = sc.a*sc.a*mom[c];
      mom[24+c] = 2.0*sc.da*mom[c] + sc.a*mom[6+c];
      mom[30+c] = (2.0*sc.d2a/sc.a)*mom[c] + (3.0*sc.da/sc.a)*mom[6+c] + mom[12+c];
      ++c;
    }
  }
  for (int d=0; d<3; ++d) {
    cen[d] = xc[d];
    cen[3+d] = vc[d];
  }
}

} // namespace

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonGroupInit
//! \brief options of the groups; called at the end of NrpicNewtonInit.  Parameters that
//! are not in the input are not added to it.

void Particles::NrpicNewtonGroupInit(ParameterInput *pin) {
  nw_ngroup = 0;
  for (int g=0; g<kNwGroupMax; ++g) {
    nw_grp_species[g] = -1;
    nw_grp_tag[g][0] = -1; nw_grp_tag[g][1] = -1;
    for (int d=0; d<3; ++d) { nw_grp_ref[g][d] = nropt.dom_min[d] + 0.5*nropt.dom_len[d]; }
    for (int n=0; n<kNwGroupSum; ++n) { nw_grp_sum[g][n] = 0.0; }
    for (int n=0; n<12; ++n) { nw_grp_ddi[g][n] = 0.0; nw_grp_d3[g][n] = 0.0; }
  }
  if (!pin->DoesParameterExist("particles", "newton_ngroup")) return;
  nw_ngroup = pin->GetInteger("particles", "newton_ngroup");
  if (nw_ngroup < 0 || nw_ngroup > kNwGroupMax) {
    GroupFatal("<particles> newton_ngroup must lie between 0 and "
               + std::to_string(kNwGroupMax));
  }
  for (int g=0; g<nw_ngroup; ++g) {
    const std::string pre = "newton_group" + std::to_string(g + 1) + "_";
    auto has = [&](const std::string &key) {
      return pin->DoesParameterExist("particles", pre + key);
    };
    if (has("species")) { nw_grp_species[g] = pin->GetInteger("particles", pre + "species"); }
    if (has("tag_min")) { nw_grp_tag[g][0] = pin->GetInteger("particles", pre + "tag_min"); }
    if (has("tag_max")) { nw_grp_tag[g][1] = pin->GetInteger("particles", pre + "tag_max"); }
    if (has("x1")) { nw_grp_ref[g][0] = pin->GetReal("particles", pre + "x1"); }
    if (has("x2")) { nw_grp_ref[g][1] = pin->GetReal("particles", pre + "x2"); }
    if (has("x3")) { nw_grp_ref[g][2] = pin->GetReal("particles", pre + "x3"); }
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonGroupSums
//! \brief sums of every group for the synchronised state of the given time and cycle
//! (the state after NrpicNewtonKick), and the third derivatives if the sums of the
//! cycle before exist.  States that are neither recorded nor followed by a recorded one
//! are skipped.

void Particles::NrpicNewtonGroupSums(const Real time, const int ncycle) {
  if (nw_ngroup <= 0) return;
  const int hd = nropt.hist_dcycle;
  if (hd <= 0) return;
  const bool need = (hd <= 2) || (ncycle % hd == 0) || ((ncycle + 1) % hd == 0) ||
                    (nw_grp_cycle < 0);
  if (!need) return;

  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int np = nprtcl_thispack;
  const GroupScale sc = Scale(nropt, time);
  const Real ia = 1.0/sc.a;
  const Real hub = sc.da*ia;

  nrpic::MeshMetric proto;
  proto.bspline = nropt.interp_bspline;
  proto.m1 = nropt.interp_bspline ? met1s : met1;
  proto.m0 = proto.m1;
  proto.is_static = true;
  proto.ist[0] = indcs.is; proto.ist[1] = indcs.js; proto.ist[2] = indcs.ks;
  proto.ncell[0] = indcs.nx1 + 2*indcs.ng;
  proto.ncell[1] = indcs.nx2 + 2*indcs.ng;
  proto.ncell[2] = indcs.nx3 + 2*indcs.ng;
  const nrpic::NewtonExternal ext = NrpicNewtonExternal(time);
  const bool ext_on = ext.On();
  const bool per[3] = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
  const Real len[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};

  const bool have_prev = (nw_grp_cycle >= 0 && nw_grp_cycle == ncycle - 1);
  const Real dt_step = time - nw_grp_time;
  const Real dt_ref = (nw_grp_dt > 0.0) ? nw_grp_dt : ((dt_user < 1.0e30) ? dt_user : 0.0);
  const bool quotient = have_prev && (dt_step > 0.0) && !(dt_step < 1.0e-6*dt_ref);
  for (int g=0; g<nw_ngroup; ++g) {
    array_sum::GlobalSum s1, s2;
    if (np > 0) {
      auto pr = prtcl_rdata;
      auto pi = prtcl_idata;
      auto sz = pmy_pack->pmb->mb_size.d_view;
      const int gids = pmy_pack->gids;
      const int gsp = nw_grp_species[g];
      const int tag0 = nw_grp_tag[g][0], tag1 = nw_grp_tag[g][1];
      const Real ref[3] = {nw_grp_ref[g][0], nw_grp_ref[g][1], nw_grp_ref[g][2]};
      Kokkos::parallel_reduce("nrpic_newton_group", Kokkos::RangePolicy<DevExeSpace>(0, np),
      KOKKOS_LAMBDA(const int p, array_sum::GlobalSum &l1, array_sum::GlobalSum &l2) {
        const Real mp = pr(IPM,p);
        if (!(mp > 0.0)) return;                // tracers and null particles: no mass
        if (gsp >= 0 && pi(PSP,p) != gsp) return;
        if (tag0 >= 0 && pi(PTAG,p) < tag0) return;
        if (tag1 >= 0 && pi(PTAG,p) > tag1) return;
        const int m = pi(PGID,p) - gids;
        const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
        const Real u[3] = {pr(IPVX,p), pr(IPVY,p), pr(IPVZ,p)};
        nrpic::MeshMetric met = proto;
        met.m = m;
        met.xmin[0] = sz(m).x1min; met.xmin[1] = sz(m).x2min; met.xmin[2] = sz(m).x3min;
        met.idx[0] = 1.0/sz(m).dx1; met.idx[1] = 1.0/sz(m).dx2; met.idx[2] = 1.0/sz(m).dx3;
        nrpic::AdmPoint ap;
        met(1, x, ap);
        Real gg[3] = {-ap.dalp[0], -ap.dalp[1], -ap.dalp[2]};
        if (ext_on) { (void) ext.Add(x, gg); }
        Real d[3], v[3], acc[3];
        for (int q=0; q<3; ++q) {
          d[q] = x[q] - ref[q];
          if (per[q]) { d[q] -= len[q]*floor(d[q]/len[q] + 0.5); }
          v[q] = u[q]*ia;
          acc[q] = gg[q]*ia - hub*v[q];
        }
        array_sum::GlobalSum t1, t2;
        t1.the_array[GS_N] = 1.0;
        t1.the_array[GS_M] = mp;
        for (int q=0; q<3; ++q) {
          t1.the_array[GS_X+q] = mp*d[q];
          t1.the_array[GS_V+q] = mp*v[q];
          t1.the_array[GS_A+q] = mp*acc[q];
        }
        int c = 0;
        for (int ii=0; ii<3; ++ii) {
          for (int jj=ii; jj<3; ++jj) {
            t1.the_array[GS_I+c] = mp*d[ii]*d[jj];
            t2.the_array[c]   = mp*(d[ii]*v[jj] + v[ii]*d[jj]);
            t2.the_array[6+c] = mp*(2.0*v[ii]*v[jj] + d[ii]*acc[jj] + acc[ii]*d[jj]);
            ++c;
          }
        }
        l1 += t1;
        l2 += t2;
      }, Kokkos::Sum<array_sum::GlobalSum>(s1), Kokkos::Sum<array_sum::GlobalSum>(s2));
    }
    for (int n=0; n<GS_DI; ++n) { nw_grp_sum[g][n] = s1.the_array[n]; }
    for (int n=0; n<12; ++n) { nw_grp_sum[g][GS_DI+n] = s2.the_array[n]; }

    Real mom[36], cen[6];
    Central(nw_grp_sum[g], sc, mom, cen);
    if (quotient) {
      const Real dtc = sc.tcos - nw_grp_tcos;
      for (int n=0; n<6; ++n) {
        nw_grp_d3[g][n] = (mom[12+n] - nw_grp_ddi[g][n])/dt_step;
        nw_grp_d3[g][6+n] = (dtc > 0.0) ? (mom[30+n] - nw_grp_ddi[g][6+n])/dtc : 0.0;
      }
    }
    for (int n=0; n<6; ++n) {
      nw_grp_ddi[g][n] = mom[12+n];
      nw_grp_ddi[g][6+n] = mom[30+n];
    }
  }
  if (quotient) {
    nw_grp_d3_time[0] = 0.5*(time + nw_grp_time);
    nw_grp_d3_time[1] = 0.5*(sc.tcos + nw_grp_tcos);
    nw_grp_dt = dt_step;
  }
  nw_grp_time = time;
  nw_grp_tcos = sc.tcos;
  nw_grp_cycle = ncycle;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonGroupWrite
//! \brief appends one record to <basename>.newton.g<g>.hst for every group; called with
//! every record of <basename>.newton.hst

void Particles::NrpicNewtonGroupWrite(Real time, int ncycle, bool header) {
  if (nw_ngroup <= 0) return;
  if (nw_grp_cycle != ncycle) {
    GroupFatal("the sums of the particle groups do not belong to the recorded cycle");
  }
  const GroupScale sc = Scale(nropt, time);
  for (int g=0; g<nw_ngroup; ++g) {
    const std::string fname = nr_basename + ".newton.g" + std::to_string(g + 1) + ".hst";
    std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
    if (fp == nullptr) GroupFatal("cannot open " + fname);
    if (header) {
      std::fprintf(fp, "# NRPIC Newtonian mode, particle group %d: species %d, tags %d "
                   "to %d (-1: no bound), reference point %.15e %.15e %.15e\n", g + 1,
                   nw_grp_species[g], nw_grp_tag[g][0], nw_grp_tag[g][1],
                   nw_grp_ref[g][0], nw_grp_ref[g][1], nw_grp_ref[g][2]);
      std::fprintf(fp, "# [1]=time [2]=ncycle [3]=a [4]=T_cosmic [5]=number [6]=mass "
                   "[7]=X_x [8]=X_y [9]=X_z [10]=V_x [11]=V_y [12]=V_z "
                   "[13..18]=I [19..24]=dI/dt [25..30]=d2I/dt2 [31..36]=d3I/dt3 "
                   "[37]=time_d3I [38..43]=J [44..49]=dJ/dT [50..55]=d2J/dT2 "
                   "[56..61]=d3J/dT3 [62]=T_d3J   (six components each: xx xy xz yy yz "
                   "zz; I comoving about the centroid, J = a^2 I physical)\n");
    }
    Real mom[36], cen[6];
    Central(nw_grp_sum[g], sc, mom, cen);
    std::fprintf(fp, "%.15e %d %.15e %.15e %.0f %.15e", time, ncycle, sc.a, sc.tcos,
                 nw_grp_sum[g][GS_N], nw_grp_sum[g][GS_M]);
    for (int d=0; d<3; ++d) { std::fprintf(fp, " %.15e", nw_grp_ref[g][d] + cen[d]); }
    for (int d=0; d<3; ++d) { std::fprintf(fp, " %.15e", cen[3+d]); }
    for (int n=0; n<18; ++n) { std::fprintf(fp, " %.15e", mom[n]); }
    for (int n=0; n<6; ++n) { std::fprintf(fp, " %.15e", nw_grp_d3[g][n]); }
    std::fprintf(fp, " %.15e", nw_grp_d3_time[0]);
    for (int n=0; n<18; ++n) { std::fprintf(fp, " %.15e", mom[18+n]); }
    for (int n=0; n<6; ++n) { std::fprintf(fp, " %.15e", nw_grp_d3[g][6+n]); }
    std::fprintf(fp, " %.15e\n", nw_grp_d3_time[1]);
    std::fclose(fp);
  }
}

} // namespace particles
