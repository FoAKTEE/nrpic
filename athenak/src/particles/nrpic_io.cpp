//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_io.cpp
//! \brief Diagnostics and file I/O of the NRPIC module: probe of the lapse and energy
//! density, history file, trajectories of tracked particles, full particle snapshots,
//! particle input files and particle restart files.  All files are written by a single
//! rank in native byte order.

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
#include "coordinates/adm.hpp"
#include "z4c/z4c.hpp"
#include "z4c/tmunu.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_mesh.hpp"

namespace particles {

namespace {
void NrpicFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_io.cpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}
} // namespace

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicProbe
//! \brief trilinear (cloud-in-cell) interpolation of the lapse and of the deposited
//! energy density to the probe position, and proper time of the normal observer there,
//! tau = int alpha dt (third order in the step).  At a MeshBlock corner the interpolation is
//! the average of the eight surrounding cells.

void Particles::NrpicProbe(Real dt) {
  if (nropt.metric != NrpicMetric::mesh) return;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int nmb = pmy_pack->nmb_thispack;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
  const Real gmin[3] = {pm->mesh_size.x1min, pm->mesh_size.x2min, pm->mesh_size.x3min};
  const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3] = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
  auto m1 = met1;
  const bool has_tm = nropt.deposit;
  DvceArray5D<Real> tm;
  if (has_tm) { tm = pmy_pack->ptmunu->u_tmunu; }

  // probe 0 is <particles> probe_x1..3; probes 1..nprobe are probeN_x1..3
  for (int ip=0; ip<=nropt.nprobe; ++ip) {
    const Real px = (ip == 0) ? nropt.probe[0] : nropt.probes[ip-1][0];
    const Real py = (ip == 0) ? nropt.probe[1] : nropt.probes[ip-1][1];
    const Real pz = (ip == 0) ? nropt.probe[2] : nropt.probes[ip-1][2];
    Real sa = 0.0, se = 0.0, sw = 0.0;
    Kokkos::parallel_reduce("nrpic_probe", Kokkos::RangePolicy<DevExeSpace>(0, 8),
    KOKKOS_LAMBDA(const int c, Real &la, Real &le, Real &lw) {
      const int mp = nrpic::FindBlock(sz, nmb, 0, px, py, pz);
      if (mp < 0) return;
      const Real h[3] = {sz(mp).dx1, sz(mp).dx2, sz(mp).dx3};
      const Real xp[3] = {px, py, pz};
      Real xb[3], s[3];
      for (int d=0; d<3; ++d) {
        Real xi = (xp[d] - gmin[d])/h[d] - 0.5;
        Real fl = floor(xi);
        s[d] = xi - fl;
        xb[d] = gmin[d] + (fl + 0.5)*h[d];
      }
      const Real xf = nrpic::WrapCoord(xb[0] + ((c & 1) ? h[0] : 0.0),
                                       dmin[0], dlen[0], per[0]);
      const Real yf = nrpic::WrapCoord(xb[1] + ((c & 2) ? h[1] : 0.0),
                                       dmin[1], dlen[1], per[1]);
      const Real zf = nrpic::WrapCoord(xb[2] + ((c & 4) ? h[2] : 0.0),
                                       dmin[2], dlen[2], per[2]);
      const Real w = ((c & 1) ? s[0] : 1.0 - s[0])*((c & 2) ? s[1] : 1.0 - s[1])
                    *((c & 4) ? s[2] : 1.0 - s[2]);
      const int mb = nrpic::FindBlock(sz, nmb, mp, xf, yf, zf);
      if (mb < 0) return;
      int i = is + static_cast<int>(floor((xf - sz(mb).x1min)/sz(mb).dx1));
      int j = js + static_cast<int>(floor((yf - sz(mb).x2min)/sz(mb).dx2));
      int k = ks + static_cast<int>(floor((zf - sz(mb).x3min)/sz(mb).dx3));
      i = (i < is) ? is : ((i > ie) ? ie : i);
      j = (j < js) ? js : ((j > je) ? je : j);
      k = (k < ks) ? ks : ((k > ke) ? ke : k);
      la += w*m1(mb,NRM_ALP,k,j,i);
      if (has_tm) { le += w*tm(mb,Tmunu::I_Tmunu_E,k,j,i); }
      lw += w;
    }, Kokkos::Sum<Real>(sa), Kokkos::Sum<Real>(se), Kokkos::Sum<Real>(sw));

    if (sw > 0.0) {
      const Real anew = sa/sw;
      Real &tau = (ip == 0) ? tau_probe : tau_probes[ip-1];
      Real &alp = (ip == 0) ? alpha_probe : alpha_probes[ip-1];
      Real &eng = (ip == 0) ? e_probe : e_probes[ip-1];
      if (dt > 0.0) {
        // proper time of the normal observer over the step: third-order formula with
        // the lapse of the two previous times (trapezoidal rule on the first step).
        // The parabola through the lapse at -h0, 0 and dt is integrated over the step;
        // for equal steps this is dt (5 anew + 8 alp - aold)/12.
        const Real aold = alpha_probe_old[ip];
        if (aold > 0.0) {
          const Real h0 = (dt_probe_old > 0.0) ? dt_probe_old : dt;
          const Real s1 = (anew - alp)/dt, s0 = (alp - aold)/h0;
          const Real d1 = (s1*h0 + s0*dt)/(h0 + dt);
          const Real d2 = 2.0*(s1 - s0)/(h0 + dt);
          tau += dt*(alp + 0.5*dt*d1 + dt*dt*d2/6.0);
        } else {
          tau += 0.5*(alp + anew)*dt;
        }
        alpha_probe_old[ip] = alp;
      }
      alp = anew;
      eng = se/sw;
    }
  }
  if (dt > 0.0) { dt_probe_old = dt; }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicWriteHistory
//! \brief appends one record to <basename>.nrpic.hst

void Particles::NrpicWriteHistory(Real time, int ncycle, bool header) {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int np = nprtcl_thispack;

  // particle sums of rest mass and momentum
  Real sm = 0.0, sux = 0.0, suy = 0.0, suz = 0.0;
  if (np > 0) {
    auto pr = prtcl_rdata;
    Kokkos::parallel_reduce("nrpic_sums", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, Real &lm, Real &lx, Real &ly, Real &lz) {
      const Real mm = (pr(IPM,p) > 0.0) ? pr(IPM,p) : 0.0;   // null particles: none
      lm += mm;
      lx += mm*pr(IPVX,p);
      ly += mm*pr(IPVY,p);
      lz += mm*pr(IPVZ,p);
    }, Kokkos::Sum<Real>(sm), Kokkos::Sum<Real>(sux), Kokkos::Sum<Real>(suy),
       Kokkos::Sum<Real>(suz));
  }
  sum_m = sm; sum_mu[0] = sux; sum_mu[1] = suy; sum_mu[2] = suz;

  // minimum of the lapse over the mesh
  Real amin = 1.0;
  if (nropt.metric == NrpicMetric::mesh) {
    auto m1 = met1;
    const int nmb = pmy_pack->nmb_thispack;
    Kokkos::parallel_reduce("nrpic_amin",
      Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
        {0, indcs.ks, indcs.js, indcs.is},
        {nmb, indcs.ke+1, indcs.je+1, indcs.ie+1}),
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &lmin) {
      lmin = fmin(lmin, m1(m,NRM_ALP,k,j,i));
    }, Kokkos::Min<Real>(amin));
  }

  // mesh statistics: proper volume, volume-weighted mean of K, extrema of the lapse
  // and of the energy density
  Real vol = 0.0, kvol = 0.0, amax = 0.0, emax = 0.0, emin = 0.0;
  if (nropt.metric == NrpicMetric::mesh) {
    auto m1 = met1;
    auto sz = pmy_pack->pmb->mb_size.d_view;
    const int nmb = pmy_pack->nmb_thispack;
    const bool has_tm = nropt.deposit;
    const bool has_z4c = (pmy_pack->pz4c != nullptr);
    DvceArray5D<Real> tm;
    if (has_tm) { tm = pmy_pack->ptmunu->u_tmunu; }
    DvceArray5D<Real> u0;
    if (has_z4c) { u0 = pmy_pack->pz4c->u0; }
    const int ikhat = z4c::Z4c::I_Z4C_KHAT, itheta = z4c::Z4c::I_Z4C_THETA;
    Real lemin = 1.0e300;
    Kokkos::parallel_reduce("nrpic_meshstat",
      Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
        {0, indcs.ks, indcs.js, indcs.is},
        {nmb, indcs.ke+1, indcs.je+1, indcs.ie+1}),
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &lv,
                  Real &lk, Real &lamax, Real &lemax, Real &llemin) {
      const Real det = adm::SpatialDet(m1(m,NRM_GXX,k,j,i), m1(m,NRM_GXY,k,j,i),
                                       m1(m,NRM_GXZ,k,j,i), m1(m,NRM_GYY,k,j,i),
                                       m1(m,NRM_GYZ,k,j,i), m1(m,NRM_GZZ,k,j,i));
      const Real w = sqrt(fabs(det))*sz(m).dx1*sz(m).dx2*sz(m).dx3;
      lv += w;
      if (has_z4c) { lk += w*(u0(m,ikhat,k,j,i) + 2.0*u0(m,itheta,k,j,i)); }
      lamax = fmax(lamax, m1(m,NRM_ALP,k,j,i));
      if (has_tm) {
        lemax = fmax(lemax, tm(m,Tmunu::I_Tmunu_E,k,j,i));
        llemin = fmin(llemin, tm(m,Tmunu::I_Tmunu_E,k,j,i));
      }
    }, Kokkos::Sum<Real>(vol), Kokkos::Sum<Real>(kvol), Kokkos::Max<Real>(amax),
       Kokkos::Max<Real>(emax), Kokkos::Min<Real>(lemin));
    emin = (lemin < 1.0e299) ? lemin : 0.0;
  }

  std::string fname = nr_basename + ".nrpic.hst";
  std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
  if (fp == nullptr) NrpicFatal("cannot open " + fname);
  if (header) {
    std::fprintf(fp, "# NRPIC history\n");
    std::fprintf(fp, "# [1]=time [2]=ncycle [3]=np [4]=sum_m [5]=sum_mW [6]=sum_mux "
                 "[7]=sum_muy [8]=sum_muz [9]=int_E [10]=int_Sx [11]=int_Sy [12]=int_Sz "
                 "[13]=alpha_probe [14]=E_probe [15]=tau_probe [16]=alpha_min "
                 "[17]=n_excised [18]=m_excised [19]=n_escaped [20]=m_escaped "
                 "[21]=push_maxit [22]=push_unconverged [23]=nmb "
                 "[24]=int_E_filtered [25]=int_Sx_filtered [26]=int_Sy_filtered "
                 "[27]=int_Sz_filtered [28]=proper_volume [29]=mean_K [30]=alpha_max "
                 "[31]=E_max [32]=E_min");
    for (int n=0; n<nropt.nprobe; ++n) {
      std::fprintf(fp, " [%d]=alpha_probe%d [%d]=E_probe%d [%d]=tau_probe%d",
                   33+3*n, n+1, 34+3*n, n+1, 35+3*n, n+1);
    }
    std::fprintf(fp, "\n");
  }
  std::fprintf(fp, "%.15e %d %d %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e "
               "%.15e %.15e %.15e %.15e %d %.15e %d %.15e %d %d %d "
               "%.15e %.15e %.15e %.15e",
               time, ncycle, np, sum_m, sum_mw, sum_mu[0], sum_mu[1], sum_mu[2],
               dep_sum[0], dep_sum[1], dep_sum[2], dep_sum[3], alpha_probe, e_probe,
               tau_probe, amin, n_excised, mass_excised, n_escaped, mass_escaped,
               push_maxit, push_unconverged, pmy_pack->nmb_thispack,
               dep_sum_filt[0], dep_sum_filt[1], dep_sum_filt[2], dep_sum_filt[3]);
  std::fprintf(fp, " %.15e %.15e %.15e %.15e %.15e", vol, (vol > 0.0) ? kvol/vol : 0.0,
               amax, emax, emin);
  for (int n=0; n<nropt.nprobe; ++n) {
    std::fprintf(fp, " %.15e %.15e %.15e", alpha_probes[n], e_probes[n], tau_probes[n]);
  }
  std::fprintf(fp, "\n");
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicWriteConstraintStats
//! \brief appends one record to <basename>.cstat.hst: extrema over the mesh of the
//! conformal factor chi, of the trace K and of the energy density, and the largest value
//! and the cell average of the constraints, absolute and relative,
//!   H   = R + (2/3) K^2 - A_ij A^ij - 16 pi E,
//!   M_i = D_j A^j_i - (2/3) d_i K - 8 pi S_i,      |M| = sqrt(gamma^ij M_i M_j),
//!   H_r = |H| / sqrt(sum of the squares of the four terms of H),
//!   M_r = |M| / sqrt(sum over the three terms T of gamma^ij T_i T_j)
//! (Mertens, Giblin & Starkman 2016; Daverio, Dirian & Mitsou 2019).  The averages give
//! every cell the same weight (uniform mesh).

void Particles::NrpicWriteConstraintStats(Real time, bool header) {
  if (pmy_pack->pz4c == nullptr || !nropt.deposit) return;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  auto con = pmy_pack->pz4c->con;
  auto adm = pmy_pack->padm->adm;
  auto u0 = pmy_pack->pz4c->u0;
  auto tm = pmy_pack->ptmunu->u_tmunu;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int nmb = pmy_pack->nmb_thispack;
  const int ikhat = z4c::Z4c::I_Z4C_KHAT, itheta = z4c::Z4c::I_Z4C_THETA;
  const int ichi = z4c::Z4c::I_Z4C_CHI;
  const Real ncell = static_cast<Real>(nmb)*indcs.nx1*indcs.nx2*indcs.nx3;

  Real chimin = 1.0e300, chimax = -1.0e300, kmin = 1.0e300, kmax = -1.0e300;
  Real emin = 1.0e300, emax = -1.0e300, thmax = 0.0;
  Kokkos::parallel_reduce("nrpic_cstat1",
    Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
      {0, indcs.ks, indcs.js, indcs.is},
      {nmb, indcs.ke+1, indcs.je+1, indcs.ie+1}),
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &lcmin,
                Real &lcmax, Real &lkmin, Real &lkmax, Real &lemin, Real &lemax,
                Real &lth) {
    const Real chi = u0(m,ichi,k,j,i);
    const Real trk = u0(m,ikhat,k,j,i) + 2.0*u0(m,itheta,k,j,i);
    const Real e = tm(m,Tmunu::I_Tmunu_E,k,j,i);
    lcmin = fmin(lcmin, chi);
    lcmax = fmax(lcmax, chi);
    lkmin = fmin(lkmin, trk);
    lkmax = fmax(lkmax, trk);
    lemin = fmin(lemin, e);
    lemax = fmax(lemax, e);
    lth = fmax(lth, fabs(u0(m,itheta,k,j,i)));
  }, Kokkos::Min<Real>(chimin), Kokkos::Max<Real>(chimax), Kokkos::Min<Real>(kmin),
     Kokkos::Max<Real>(kmax), Kokkos::Min<Real>(emin), Kokkos::Max<Real>(emax),
     Kokkos::Max<Real>(thmax));

  Real hmax = 0.0, hsum = 0.0, hrmax = 0.0, hrsum = 0.0;
  Real mmax = 0.0, msum = 0.0, mrmax = 0.0, mrsum = 0.0;
  Kokkos::parallel_reduce("nrpic_cstat2",
    Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
      {0, indcs.ks, indcs.js, indcs.is},
      {nmb, indcs.ke+1, indcs.je+1, indcs.ie+1}),
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i, Real &lhmax,
                Real &lhsum, Real &lhrmax, Real &lhrsum, Real &lmmax, Real &lmsum,
                Real &lmrmax, Real &lmrsum) {
    Real g[3][3], kd[3][3], gi[3][3];
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) {
        g[a][b] = adm.g_dd(m,a,b,k,j,i);
        kd[a][b] = adm.vK_dd(m,a,b,k,j,i);
      }
    }
    nrpic::Inv3Sym(g, gi);
    Real trk = 0.0, kk = 0.0;
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) {
        trk += gi[a][b]*kd[a][b];
        for (int c=0; c<3; ++c) {
          for (int d=0; d<3; ++d) {
            kk += gi[a][c]*gi[b][d]*kd[a][b]*kd[c][d];
          }
        }
      }
    }
    const Real a2 = kk - trk*trk/3.0;
    const Real e16 = 16.0*M_PI*tm(m,Tmunu::I_Tmunu_E,k,j,i);
    const Real h = con.H(m,k,j,i);
    const Real k23 = 2.0*trk*trk/3.0;
    const Real ricci = h - k23 + a2 + e16;
    const Real hden = sqrt(ricci*ricci + k23*k23 + a2*a2 + e16*e16);
    const Real habs = fabs(h);
    const Real hr = (hden > 0.0) ? habs/hden : 0.0;
    lhmax = fmax(lhmax, habs);
    lhsum += habs;
    lhrmax = fmax(lhrmax, hr);
    lhrsum += hr;

    // gradient of K with fourth-order centred differences
    const Real idx[3] = {1.0/sz(m).dx1, 1.0/sz(m).dx2, 1.0/sz(m).dx3};
    Real dk[3];
    dk[0] = idx[0]*(8.0*((u0(m,ikhat,k,j,i+1) + 2.0*u0(m,itheta,k,j,i+1))
                         - (u0(m,ikhat,k,j,i-1) + 2.0*u0(m,itheta,k,j,i-1)))
                    - ((u0(m,ikhat,k,j,i+2) + 2.0*u0(m,itheta,k,j,i+2))
                       - (u0(m,ikhat,k,j,i-2) + 2.0*u0(m,itheta,k,j,i-2))))/12.0;
    dk[1] = idx[1]*(8.0*((u0(m,ikhat,k,j+1,i) + 2.0*u0(m,itheta,k,j+1,i))
                         - (u0(m,ikhat,k,j-1,i) + 2.0*u0(m,itheta,k,j-1,i)))
                    - ((u0(m,ikhat,k,j+2,i) + 2.0*u0(m,itheta,k,j+2,i))
                       - (u0(m,ikhat,k,j-2,i) + 2.0*u0(m,itheta,k,j-2,i))))/12.0;
    dk[2] = idx[2]*(8.0*((u0(m,ikhat,k+1,j,i) + 2.0*u0(m,itheta,k+1,j,i))
                         - (u0(m,ikhat,k-1,j,i) + 2.0*u0(m,itheta,k-1,j,i)))
                    - ((u0(m,ikhat,k+2,j,i) + 2.0*u0(m,itheta,k+2,j,i))
                       - (u0(m,ikhat,k-2,j,i) + 2.0*u0(m,itheta,k-2,j,i))))/12.0;
    Real md[3], t1[3], t2[3], t3[3];
    for (int a=0; a<3; ++a) {
      md[a] = con.M_d(m,a,k,j,i);
      t2[a] = -2.0*dk[a]/3.0;
      t3[a] = -8.0*M_PI*tm(m,Tmunu::I_Tmunu_Sx+a,k,j,i);
      t1[a] = md[a] - t2[a] - t3[a];
    }
    Real m2 = 0.0, d2 = 0.0;
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) {
        m2 += gi[a][b]*md[a]*md[b];
        d2 += gi[a][b]*(t1[a]*t1[b] + t2[a]*t2[b] + t3[a]*t3[b]);
      }
    }
    const Real mabs = sqrt(fmax(m2, 0.0));
    const Real mr = (d2 > 0.0) ? mabs/sqrt(d2) : 0.0;
    lmmax = fmax(lmmax, mabs);
    lmsum += mabs;
    lmrmax = fmax(lmrmax, mr);
    lmrsum += mr;
  }, Kokkos::Max<Real>(hmax), Kokkos::Sum<Real>(hsum), Kokkos::Max<Real>(hrmax),
     Kokkos::Sum<Real>(hrsum), Kokkos::Max<Real>(mmax), Kokkos::Sum<Real>(msum),
     Kokkos::Max<Real>(mrmax), Kokkos::Sum<Real>(mrsum));

  std::string fname = nr_basename + ".cstat.hst";
  std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
  if (fp == nullptr) NrpicFatal("cannot open " + fname);
  if (header) {
    std::fprintf(fp, "# NRPIC constraint statistics\n");
    std::fprintf(fp, "# [1]=time [2]=chi_min [3]=chi_max [4]=K_min [5]=K_max [6]=E_min "
                 "[7]=E_max [8]=Theta_max [9]=H_max [10]=H_mean [11]=Hr_max [12]=Hr_mean "
                 "[13]=M_max [14]=M_mean [15]=Mr_max [16]=Mr_mean\n");
  }
  std::fprintf(fp, "%.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e "
               "%.15e %.15e %.15e %.15e %.15e\n", time, chimin, chimax, kmin, kmax, emin,
               emax, thmax, hmax, hsum/ncell, hrmax, hrsum/ncell, mmax, msum/ncell,
               mrmax, mrsum/ncell);
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicWriteLine
//! \brief appends the fields along the mesh line through the first cells in x2 and x3
//! to <basename>.line.bin, as records of 1 + 5 n doubles: time, then chi, alpha, K, E and
//! S_x at the n cells of the line in order of increasing x1.  The header call writes
//! <basename>.line.txt with n and the cell centres.  Uniform mesh, one rank.

void Particles::NrpicWriteLine(Real time, bool header) {
  if (pmy_pack->pz4c == nullptr || !nropt.deposit) return;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int nx1 = indcs.nx1, is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nmb = pmy_pack->nmb_thispack;
  const int ng1 = pm->mesh_indcs.nx1;
  const Real x1min = pm->mesh_size.x1min;
  const Real dx1 = (pm->mesh_size.x1max - x1min)/static_cast<Real>(ng1);
  const Real tol = 1.0e-10*(pm->mesh_size.x2max - pm->mesh_size.x2min);

  // the MeshBlocks on the line, and the five fields along it
  auto sz = pmy_pack->pmb->mb_size.h_view;
  DvceArray3D<Real> line("nrpic_line", nmb, 5, nx1);
  auto u0 = pmy_pack->pz4c->u0;
  auto tm = pmy_pack->ptmunu->u_tmunu;
  const int ikhat = z4c::Z4c::I_Z4C_KHAT, itheta = z4c::Z4c::I_Z4C_THETA;
  const int ichi = z4c::Z4c::I_Z4C_CHI, ialp = z4c::Z4c::I_Z4C_ALPHA;
  par_for("nrpic_line", DevExeSpace(), 0, nmb-1, 0, nx1-1,
  KOKKOS_LAMBDA(const int m, const int i) {
    line(m,0,i) = u0(m,ichi,ks,js,is+i);
    line(m,1,i) = u0(m,ialp,ks,js,is+i);
    line(m,2,i) = u0(m,ikhat,ks,js,is+i) + 2.0*u0(m,itheta,ks,js,is+i);
    line(m,3,i) = tm(m,Tmunu::I_Tmunu_E,ks,js,is+i);
    line(m,4,i) = tm(m,Tmunu::I_Tmunu_Sx,ks,js,is+i);
  });
  auto lh = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), line);
  std::vector<double> buf(1 + 5*static_cast<size_t>(ng1), 0.0);
  buf[0] = time;
  for (int m=0; m<nmb; ++m) {
    if (std::abs(sz(m).x2min - pm->mesh_size.x2min) > tol ||
        std::abs(sz(m).x3min - pm->mesh_size.x3min) > tol) continue;
    const int i0 = static_cast<int>(std::floor((sz(m).x1min - x1min)/dx1 + 0.5));
    for (int v=0; v<5; ++v) {
      for (int i=0; i<nx1; ++i) {
        if (i0 + i >= 0 && i0 + i < ng1) {
          buf[1 + static_cast<size_t>(v)*ng1 + i0 + i] = lh(m,v,i);
        }
      }
    }
  }
  if (header) {
    std::string ftxt = nr_basename + ".line.txt";
    std::FILE *ft = std::fopen(ftxt.c_str(), "w");
    if (ft == nullptr) NrpicFatal("cannot open " + ftxt);
    std::fprintf(ft, "# records of 1 + 5 n doubles in the .line.bin file: time, chi, alpha, "
                 "K, E, S_x at the n cell centres below\n%d\n", ng1);
    for (int i=0; i<ng1; ++i) { std::fprintf(ft, "%.15e\n", x1min + (i + 0.5)*dx1); }
    std::fclose(ft);
  }
  std::string fname = nr_basename + ".line.bin";
  std::FILE *fp = std::fopen(fname.c_str(), header ? "wb" : "ab");
  if (fp == nullptr) NrpicFatal("cannot open " + fname);
  std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicWriteEnergyField
//! \brief writes the energy density E and the conformal factor chi of the whole uniform
//! mesh to <basename>.field.NNNNN.bin: 8 bytes "NRFIELD1", the time (double), 3 int64
//! (n1, n2, n3), then two arrays of n3*n2*n1 floats (E, chi), first index fastest.
//! With <particles> field_constraints = true the magic is "NRFIELD2" and seven more
//! arrays follow: the Hamiltonian constraint, the three components of the momentum
//! constraint, Khat, Theta and the lapse, all as doubles.

void Particles::NrpicWriteEnergyField(Real time, int index) {
  if (pmy_pack->pz4c == nullptr || !nropt.deposit) return;
  Mesh *pm = pmy_pack->pmesh;
  if (pm->multilevel) return;
  auto &indcs = pm->mb_indcs;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nmb = pmy_pack->nmb_thispack;
  const std::int64_t g1 = pm->mesh_indcs.nx1, g2 = pm->mesh_indcs.nx2;
  const std::int64_t g3 = pm->mesh_indcs.nx3;
  const Real d1 = (pm->mesh_size.x1max - pm->mesh_size.x1min)/static_cast<Real>(g1);
  const Real d2 = (pm->mesh_size.x2max - pm->mesh_size.x2min)/static_cast<Real>(g2);
  const Real d3 = (pm->mesh_size.x3max - pm->mesh_size.x3min)/static_cast<Real>(g3);
  auto tmh = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(),
                                                 pmy_pack->ptmunu->u_tmunu);
  auto u0h = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), pmy_pack->pz4c->u0);
  auto sz = pmy_pack->pmb->mb_size.h_view;
  const size_t ncell = static_cast<size_t>(g1)*g2*g3;
  std::vector<float> e(ncell), c(ncell);
  const int ichi = z4c::Z4c::I_Z4C_CHI;
  for (int m=0; m<nmb; ++m) {
    const std::int64_t i0 = static_cast<std::int64_t>(
        std::floor((sz(m).x1min - pm->mesh_size.x1min)/d1 + 0.5));
    const std::int64_t j0 = static_cast<std::int64_t>(
        std::floor((sz(m).x2min - pm->mesh_size.x2min)/d2 + 0.5));
    const std::int64_t k0 = static_cast<std::int64_t>(
        std::floor((sz(m).x3min - pm->mesh_size.x3min)/d3 + 0.5));
    for (int k=0; k<nx3; ++k) {
      for (int j=0; j<nx2; ++j) {
        for (int i=0; i<nx1; ++i) {
          const size_t idx = (static_cast<size_t>(k0 + k)*g2 + (j0 + j))*g1 + (i0 + i);
          e[idx] = static_cast<float>(tmh(m,Tmunu::I_Tmunu_E,ks+k,js+j,is+i));
          c[idx] = static_cast<float>(u0h(m,ichi,ks+k,js+j,is+i));
        }
      }
    }
  }
  char num[16];
  std::snprintf(num, sizeof(num), "%05d", index);
  std::string fname = nr_basename + ".field." + num + ".bin";
  std::FILE *fp = std::fopen(fname.c_str(), "wb");
  if (fp == nullptr) NrpicFatal("cannot open " + fname);
  const std::int64_t dims[3] = {g1, g2, g3};
  const double tt = time;
  std::fwrite(nropt.field_constraints ? "NRFIELD2" : "NRFIELD1", 1, 8, fp);
  std::fwrite(&tt, sizeof(double), 1, fp);
  std::fwrite(dims, sizeof(std::int64_t), 3, fp);
  std::fwrite(e.data(), sizeof(float), ncell, fp);
  std::fwrite(c.data(), sizeof(float), ncell, fp);
  if (nropt.field_constraints) {
    auto conh = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(),
                                                    pmy_pack->pz4c->u_con);
    const int src[7] = {z4c::Z4c::I_CON_H, z4c::Z4c::I_CON_MX, z4c::Z4c::I_CON_MY,
                        z4c::Z4c::I_CON_MZ, z4c::Z4c::I_Z4C_KHAT, z4c::Z4c::I_Z4C_THETA,
                        z4c::Z4c::I_Z4C_ALPHA};
    std::vector<double> buf(ncell);
    for (int n=0; n<7; ++n) {
      for (int m=0; m<nmb; ++m) {
        const std::int64_t i0 = static_cast<std::int64_t>(
            std::floor((sz(m).x1min - pm->mesh_size.x1min)/d1 + 0.5));
        const std::int64_t j0 = static_cast<std::int64_t>(
            std::floor((sz(m).x2min - pm->mesh_size.x2min)/d2 + 0.5));
        const std::int64_t k0 = static_cast<std::int64_t>(
            std::floor((sz(m).x3min - pm->mesh_size.x3min)/d3 + 0.5));
        for (int k=0; k<nx3; ++k) {
          for (int j=0; j<nx2; ++j) {
            for (int i=0; i<nx1; ++i) {
              const size_t idx = (static_cast<size_t>(k0 + k)*g2 + (j0 + j))*g1 + (i0 + i);
              buf[idx] = (n < 4) ? conh(m,src[n],ks+k,js+j,is+i)
                                 : u0h(m,src[n],ks+k,js+j,is+i);
            }
          }
        }
      }
      std::fwrite(buf.data(), sizeof(double), ncell, fp);
    }
  }
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicWriteTrajectories
//! \brief appends the state of the tracked particles (tag < traj_ntrack) to
//! <basename>.traj.bin as records of 8 doubles: time, tag, x^i, u_i

void Particles::NrpicWriteTrajectories(Real time, bool truncate) {
  std::string fname = nr_basename + ".traj.bin";
  std::FILE *fp = std::fopen(fname.c_str(), truncate ? "wb" : "ab");
  if (fp == nullptr) NrpicFatal("cannot open " + fname);
  const int np = nprtcl_thispack;
  const bool mesh_metric = (nropt.metric == NrpicMetric::mesh);
  // With a mesh metric the fields reconstructed at each tracked particle are written to
  // <basename>.trajmet.bin as records of 17 doubles: time, tag, alpha, beta^i, gamma_ij
  // (xx, xy, xz, yy, yz, zz), the proper time of the particle (affine parameter of a
  // null particle), and the deposited E and S_i interpolated to it with the
  // cloud-in-cell weights, in the same order as the records of the trajectory file.
  std::FILE *fpm = nullptr;
  if (mesh_metric) {
    std::string fmet = nr_basename + ".trajmet.bin";
    fpm = std::fopen(fmet.c_str(), truncate ? "wb" : "ab");
    if (fpm == nullptr) NrpicFatal("cannot open " + fmet);
  }
  if (np > 0) {
    auto rh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_rdata);
    auto ih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_idata);
    HostArray2D<Real> mh;
    if (mesh_metric) {
      auto &indcs = pmy_pack->pmesh->mb_indcs;
      auto pr = prtcl_rdata;
      auto pi = prtcl_idata;
      auto sz = pmy_pack->pmb->mb_size.d_view;
      const int gids = pmy_pack->gids;
      const int ntrack = nropt.traj_ntrack;
      nrpic::MeshMetric proto;
      proto.m1 = met1;
      proto.m0 = met1;
      proto.is_static = true;
      proto.ist[0] = indcs.is; proto.ist[1] = indcs.js; proto.ist[2] = indcs.ks;
      proto.ncell[0] = indcs.nx1 + 2*indcs.ng;
      proto.ncell[1] = indcs.nx2 + 2*indcs.ng;
      proto.ncell[2] = indcs.nx3 + 2*indcs.ng;
      DvceArray2D<Real> pmet("pmet", NRM_NVAR + 5, np);
      const int nmb = pmy_pack->nmb_thispack;
      const int is = indcs.is, js = indcs.js, ks = indcs.ks;
      const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
      Mesh *pm = pmy_pack->pmesh;
      const Real gmin[3] = {pm->mesh_size.x1min, pm->mesh_size.x2min,
                            pm->mesh_size.x3min};
      const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
      const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
      const bool per[3] = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
      const bool has_tm = nropt.deposit;
      DvceArray5D<Real> tm;
      if (has_tm) { tm = pmy_pack->ptmunu->u_tmunu; }
      par_for("nrpic_trajmet", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
        if (pi(PTAG,p) >= ntrack) return;
        const int m = pi(PGID,p) - gids;
        nrpic::MeshMetric met = proto;
        met.m = m;
        met.xmin[0] = sz(m).x1min; met.xmin[1] = sz(m).x2min; met.xmin[2] = sz(m).x3min;
        met.idx[0] = 1.0/sz(m).dx1; met.idx[1] = 1.0/sz(m).dx2;
        met.idx[2] = 1.0/sz(m).dx3;
        const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
        nrpic::AdmPoint ap;
        met(1, x, ap);
        pmet(NRM_ALP,p) = ap.alp;
        pmet(NRM_BX,p) = ap.beta[0]; pmet(NRM_BY,p) = ap.beta[1];
        pmet(NRM_BZ,p) = ap.beta[2];
        pmet(NRM_GXX,p) = ap.g[0][0]; pmet(NRM_GXY,p) = ap.g[0][1];
        pmet(NRM_GXZ,p) = ap.g[0][2]; pmet(NRM_GYY,p) = ap.g[1][1];
        pmet(NRM_GYZ,p) = ap.g[1][2]; pmet(NRM_GZZ,p) = ap.g[2][2];
        pmet(NRM_NVAR,p) = pr(IPTAU,p);
        // deposited E and S_i at the particle (cloud-in-cell gather on its level)
        Real se = 0.0, sx = 0.0, sy = 0.0, sz3 = 0.0, sw = 0.0;
        if (has_tm) {
          const Real h[3] = {sz(m).dx1, sz(m).dx2, sz(m).dx3};
          Real xb[3], s[3];
          for (int d=0; d<3; ++d) {
            Real xi = (x[d] - gmin[d])/h[d] - 0.5;
            Real fl = floor(xi);
            s[d] = xi - fl;
            xb[d] = gmin[d] + (fl + 0.5)*h[d];
          }
          for (int c=0; c<8; ++c) {
            const Real xf = nrpic::WrapCoord(xb[0] + ((c & 1) ? h[0] : 0.0),
                                             dmin[0], dlen[0], per[0]);
            const Real yf = nrpic::WrapCoord(xb[1] + ((c & 2) ? h[1] : 0.0),
                                             dmin[1], dlen[1], per[1]);
            const Real zf = nrpic::WrapCoord(xb[2] + ((c & 4) ? h[2] : 0.0),
                                             dmin[2], dlen[2], per[2]);
            const Real w = ((c & 1) ? s[0] : 1.0 - s[0])*((c & 2) ? s[1] : 1.0 - s[1])
                          *((c & 4) ? s[2] : 1.0 - s[2]);
            const int mb = nrpic::FindBlock(sz, nmb, m, xf, yf, zf);
            if (mb < 0) continue;
            int i = is + static_cast<int>(floor((xf - sz(mb).x1min)/sz(mb).dx1));
            int j = js + static_cast<int>(floor((yf - sz(mb).x2min)/sz(mb).dx2));
            int k = ks + static_cast<int>(floor((zf - sz(mb).x3min)/sz(mb).dx3));
            i = (i < is) ? is : ((i > ie) ? ie : i);
            j = (j < js) ? js : ((j > je) ? je : j);
            k = (k < ks) ? ks : ((k > ke) ? ke : k);
            se += w*tm(mb,Tmunu::I_Tmunu_E,k,j,i);
            sx += w*tm(mb,Tmunu::I_Tmunu_Sx,k,j,i);
            sy += w*tm(mb,Tmunu::I_Tmunu_Sy,k,j,i);
            sz3 += w*tm(mb,Tmunu::I_Tmunu_Sz,k,j,i);
            sw += w;
          }
        }
        const Real isw = (sw > 0.0) ? 1.0/sw : 0.0;
        pmet(NRM_NVAR+1,p) = se*isw;
        pmet(NRM_NVAR+2,p) = sx*isw;
        pmet(NRM_NVAR+3,p) = sy*isw;
        pmet(NRM_NVAR+4,p) = sz3*isw;
      });
      mh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), pmet);
    }
    std::vector<double> buf, mbuf;
    buf.reserve(8*static_cast<size_t>(std::min(np, nropt.traj_ntrack)));
    for (int p=0; p<np; ++p) {
      if (ih(PTAG,p) < nropt.traj_ntrack) {
        buf.push_back(time);
        buf.push_back(static_cast<double>(ih(PTAG,p)));
        buf.push_back(rh(IPX,p)); buf.push_back(rh(IPY,p)); buf.push_back(rh(IPZ,p));
        buf.push_back(rh(IPVX,p)); buf.push_back(rh(IPVY,p)); buf.push_back(rh(IPVZ,p));
        if (mesh_metric) {
          mbuf.push_back(time);
          mbuf.push_back(static_cast<double>(ih(PTAG,p)));
          for (int n=0; n<NRM_NVAR+5; ++n) { mbuf.push_back(mh(n,p)); }
        }
      }
    }
    if (!buf.empty()) std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
    if (fpm != nullptr && !mbuf.empty()) {
      std::fwrite(mbuf.data(), sizeof(double), mbuf.size(), fpm);
    }
  }
  std::fclose(fp);
  if (fpm != nullptr) std::fclose(fpm);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicWriteSnapshot
//! \brief writes all particles to <basename>.part.NNNNN.bin:
//!   8 bytes "NRPSNAP1", double time, int64 N, int64 ncycle,
//!   N records of 7 doubles (x^i, u_i, m), N int32 tags, N int32 species, N doubles
//!   (proper time of each particle; affine parameter of a null particle)

void Particles::NrpicWriteSnapshot(Real time) {
  char number[16];
  std::snprintf(number, sizeof(number), ".part.%05d.bin", snap_number);
  std::string fname = nr_basename + number;
  std::FILE *fp = std::fopen(fname.c_str(), "wb");
  if (fp == nullptr) NrpicFatal("cannot open " + fname);
  const int np = nprtcl_thispack;
  const char magic[9] = "NRPSNAP1";
  double t = time;
  std::int64_t n64 = np, nc64 = pmy_pack->pmesh->ncycle;
  std::fwrite(magic, 1, 8, fp);
  std::fwrite(&t, sizeof(double), 1, fp);
  std::fwrite(&n64, sizeof(std::int64_t), 1, fp);
  std::fwrite(&nc64, sizeof(std::int64_t), 1, fp);
  if (np > 0) {
    auto rh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_rdata);
    auto ih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_idata);
    std::vector<double> buf(7*static_cast<size_t>(np));
    std::vector<std::int32_t> tag(np), sp(np);
    for (int p=0; p<np; ++p) {
      buf[7*p+0] = rh(IPX,p);  buf[7*p+1] = rh(IPY,p);  buf[7*p+2] = rh(IPZ,p);
      buf[7*p+3] = rh(IPVX,p); buf[7*p+4] = rh(IPVY,p); buf[7*p+5] = rh(IPVZ,p);
      buf[7*p+6] = rh(IPM,p);
      tag[p] = ih(PTAG,p);
      sp[p] = ih(PSP,p);
    }
    std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
    std::fwrite(tag.data(), sizeof(std::int32_t), tag.size(), fp);
    std::fwrite(sp.data(), sizeof(std::int32_t), sp.size(), fp);
    std::vector<double> tau(np);
    for (int p=0; p<np; ++p) { tau[p] = rh(IPTAU,p); }
    std::fwrite(tau.data(), sizeof(double), tau.size(), fp);
  }
  std::fclose(fp);
  snap_number++;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicLoadParticleFile
//! \brief reads a particle file (docs/FORMATS.md):
//!   8 bytes "NRPIC001", int64 N, N records of 7 doubles (x^i, u_i, m), N int32 species
//! Tags are the positions of the particles in the file.

void Particles::NrpicLoadParticleFile(const std::string &fname) {
  std::FILE *fp = std::fopen(fname.c_str(), "rb");
  if (fp == nullptr) NrpicFatal("cannot open particle file " + fname);
  char magic[9] = {0};
  std::int64_t n64 = 0;
  if (std::fread(magic, 1, 8, fp) != 8 || std::strncmp(magic, "NRPIC001", 8) != 0) {
    NrpicFatal("bad magic in particle file " + fname);
  }
  if (std::fread(&n64, sizeof(std::int64_t), 1, fp) != 1 || n64 < 0) {
    NrpicFatal("bad particle count in " + fname);
  }
  const int np = static_cast<int>(n64);
  std::vector<double> buf(7*static_cast<size_t>(np));
  std::vector<std::int32_t> sp(np);
  if (std::fread(buf.data(), sizeof(double), buf.size(), fp) != buf.size() ||
      std::fread(sp.data(), sizeof(std::int32_t), sp.size(), fp) != sp.size()) {
    NrpicFatal("particle file " + fname + " is truncated");
  }
  std::fclose(fp);

  SetNumberOfParticles(np);
  HostArray2D<Real> rh("rh", nrdata, np);
  HostArray2D<int>  ih("ih", nidata, np);
  const int gids = pmy_pack->gids;
  for (int p=0; p<np; ++p) {
    rh(IPX,p) = buf[7*p+0];  rh(IPY,p) = buf[7*p+1];  rh(IPZ,p) = buf[7*p+2];
    rh(IPVX,p) = buf[7*p+3]; rh(IPVY,p) = buf[7*p+4]; rh(IPVZ,p) = buf[7*p+5];
    rh(IPM,p) = buf[7*p+6];
    ih(PGID,p) = gids;
    ih(PTAG,p) = p;
    ih(PSP,p) = sp[p];
  }
  Kokkos::deep_copy(prtcl_rdata, rh);
  Kokkos::deep_copy(prtcl_idata, ih);
  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC: read " << np << " particles from " << fname << std::endl;
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicCreateParticles
//! \brief creates the particles of a new run, either from <particles> particle_file or
//! from the inline list <particles> nparticles, pN_x1, pN_x2, pN_x3, pN_u1, pN_u2,
//! pN_u3, pN_m (N = 0 ... nparticles-1), given in the coordinates of the run

void Particles::NrpicCreateParticles() {
  if (!nr_particle_file.empty()) {
    NrpicLoadParticleFile(nr_particle_file);
    return;
  }
  const int np = static_cast<int>(nr_inline.size()/7);
  if (np == 0) return;
  SetNumberOfParticles(np);
  HostArray2D<Real> rh("rh", nrdata, np);
  HostArray2D<int>  ih("ih", nidata, np);
  const int gids = pmy_pack->gids;
  for (int p=0; p<np; ++p) {
    rh(IPX,p) = nr_inline[7*p+0];  rh(IPY,p) = nr_inline[7*p+1];
    rh(IPZ,p) = nr_inline[7*p+2];
    rh(IPVX,p) = nr_inline[7*p+3]; rh(IPVY,p) = nr_inline[7*p+4];
    rh(IPVZ,p) = nr_inline[7*p+5];
    rh(IPM,p) = nr_inline[7*p+6];
    ih(PGID,p) = gids;
    ih(PTAG,p) = p;
    ih(PSP,p) = 0;
  }
  Kokkos::deep_copy(prtcl_rdata, rh);
  Kokkos::deep_copy(prtcl_idata, ih);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicWriteRestart
//! \brief writes the particle restart file that accompanies a mesh restart file:
//!   8 bytes "NRPRST05" (02 to 04 are still read), int64 N, 7 doubles (tau_probe, alpha_probe, e_probe,
//!   mass_excised, mass_escaped, snap_next_time, curv_next_time), 4 int64 (n_excised,
//!   n_escaped, snap_number, curv_number), N records of 7 doubles, N records of 3 int32
//!   (gid, tag, species)

void Particles::NrpicWriteRestart(const std::string &fname) {
  std::FILE *fp = std::fopen(fname.c_str(), "wb");
  if (fp == nullptr) NrpicFatal("cannot open " + fname);
  const int np = nprtcl_thispack;
  const char magic[9] = "NRPRST05";
  std::int64_t n64 = np;
  double dstate[7] = {tau_probe, alpha_probe, e_probe, mass_excised, mass_escaped,
                      snap_next_time, curv_next_time};
  std::int64_t istate[4] = {n_excised, n_escaped, snap_number, curv_number};
  std::fwrite(magic, 1, 8, fp);
  std::fwrite(&n64, sizeof(std::int64_t), 1, fp);
  std::fwrite(dstate, sizeof(double), 7, fp);
  std::fwrite(istate, sizeof(std::int64_t), 4, fp);
  if (np > 0) {
    auto rh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_rdata);
    auto ih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_idata);
    std::vector<double> buf(7*static_cast<size_t>(np));
    std::vector<std::int32_t> ibuf(3*static_cast<size_t>(np));
    for (int p=0; p<np; ++p) {
      buf[7*p+0] = rh(IPX,p);  buf[7*p+1] = rh(IPY,p);  buf[7*p+2] = rh(IPZ,p);
      buf[7*p+3] = rh(IPVX,p); buf[7*p+4] = rh(IPVY,p); buf[7*p+5] = rh(IPVZ,p);
      buf[7*p+6] = rh(IPM,p);
      ibuf[3*p+0] = ih(PGID,p);
      ibuf[3*p+1] = ih(PTAG,p);
      ibuf[3*p+2] = ih(PSP,p);
    }
    std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
    std::fwrite(ibuf.data(), sizeof(std::int32_t), ibuf.size(), fp);
    // version 03: proper time of each particle
    std::vector<double> tau(np);
    for (int p=0; p<np; ++p) { tau[p] = rh(IPTAU,p); }
    std::fwrite(tau.data(), sizeof(double), tau.size(), fp);
  }
  // version 03: state of the additional probes
  double pstate[24];
  for (int n=0; n<8; ++n) {
    pstate[3*n] = tau_probes[n]; pstate[3*n+1] = alpha_probes[n];
    pstate[3*n+2] = e_probes[n];
  }
  std::fwrite(pstate, sizeof(double), 24, fp);
  // version 04: lapse history of the probes (third-order proper time), and the source
  // densities handed to the spacetime solver for the coming step (extrapolated from the
  // last two deposits; they cannot be rebuilt from the particles at one time)
  std::fwrite(alpha_probe_old, sizeof(double), 9, fp);
  // version 05: the previous step (the step may vary, see dt_expansion)
  const double dtold = dt_probe_old;
  std::fwrite(&dtold, sizeof(double), 1, fp);
  std::int64_t has_ts = 0;
  if (nropt.deposit && nropt.source_density && nropt.source_extrap &&
      pmy_pack->ptmunu != nullptr && pmy_pack->ptmunu->step_density && tm_prev_valid) {
    has_ts = 1;
  }
  std::fwrite(&has_ts, sizeof(std::int64_t), 1, fp);
  if (has_ts == 1) {
    auto tsh = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(),
                                                   pmy_pack->ptmunu->u_tmunu_step);
    std::int64_t dims[5];
    for (int d=0; d<5; ++d) { dims[d] = static_cast<std::int64_t>(tsh.extent(d)); }
    std::fwrite(dims, sizeof(std::int64_t), 5, fp);
    std::fwrite(tsh.data(), sizeof(double), tsh.size(), fp);
  }
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicReadRestart
//! \brief reads the particle restart file written by NrpicWriteRestart

void Particles::NrpicReadRestart(const std::string &fname) {
  std::FILE *fp = std::fopen(fname.c_str(), "rb");
  if (fp == nullptr) NrpicFatal("cannot open particle restart file " + fname);
  char magic[9] = {0};
  std::int64_t n64 = 0;
  double dstate[7];
  std::int64_t istate[4];
  if (std::fread(magic, 1, 8, fp) != 8 || (std::strncmp(magic, "NRPRST02", 8) != 0 &&
                                           std::strncmp(magic, "NRPRST03", 8) != 0 &&
                                           std::strncmp(magic, "NRPRST04", 8) != 0 &&
                                           std::strncmp(magic, "NRPRST05", 8) != 0)) {
    NrpicFatal("bad magic in particle restart file " + fname);
  }
  const bool v5 = (std::strncmp(magic, "NRPRST05", 8) == 0);
  const bool v4 = v5 || (std::strncmp(magic, "NRPRST04", 8) == 0);
  const bool v3 = v4 || (std::strncmp(magic, "NRPRST03", 8) == 0);
  if (std::fread(&n64, sizeof(std::int64_t), 1, fp) != 1 ||
      std::fread(dstate, sizeof(double), 7, fp) != 7 ||
      std::fread(istate, sizeof(std::int64_t), 4, fp) != 4) {
    NrpicFatal("bad header in particle restart file " + fname);
  }
  const int np = static_cast<int>(n64);
  std::vector<double> buf(7*static_cast<size_t>(np));
  std::vector<std::int32_t> ibuf(3*static_cast<size_t>(np));
  if (std::fread(buf.data(), sizeof(double), buf.size(), fp) != buf.size() ||
      std::fread(ibuf.data(), sizeof(std::int32_t), ibuf.size(), fp) != ibuf.size()) {
    NrpicFatal("particle restart file " + fname + " is truncated");
  }
  std::vector<double> tau(np, 0.0);
  if (v3) {
    double pstate[24];
    if (std::fread(tau.data(), sizeof(double), tau.size(), fp) != tau.size() ||
        std::fread(pstate, sizeof(double), 24, fp) != 24) {
      NrpicFatal("particle restart file " + fname + " is truncated");
    }
    for (int n=0; n<8; ++n) {
      tau_probes[n] = pstate[3*n]; alpha_probes[n] = pstate[3*n+1];
      e_probes[n] = pstate[3*n+2];
    }
  }
  ts_restart.clear();
  if (v4) {
    std::int64_t has_ts = 0;
    double dtold = -1.0;
    if (std::fread(alpha_probe_old, sizeof(double), 9, fp) != 9 ||
        (v5 && std::fread(&dtold, sizeof(double), 1, fp) != 1) ||
        std::fread(&has_ts, sizeof(std::int64_t), 1, fp) != 1) {
      NrpicFatal("particle restart file " + fname + " is truncated");
    }
    dt_probe_old = dtold;
    if (has_ts == 1) {
      if (std::fread(ts_restart_dims, sizeof(std::int64_t), 5, fp) != 5) {
        NrpicFatal("particle restart file " + fname + " is truncated");
      }
      size_t nt = 1;
      for (int d=0; d<5; ++d) { nt *= static_cast<size_t>(ts_restart_dims[d]); }
      ts_restart.resize(nt);
      if (std::fread(ts_restart.data(), sizeof(double), nt, fp) != nt) {
        NrpicFatal("particle restart file " + fname + " is truncated");
      }
    }
  }
  std::fclose(fp);

  tau_probe = dstate[0]; alpha_probe = dstate[1]; e_probe = dstate[2];
  mass_excised = dstate[3]; mass_escaped = dstate[4]; snap_next_time = dstate[5];
  curv_next_time = dstate[6];
  n_excised = static_cast<int>(istate[0]);
  n_escaped = static_cast<int>(istate[1]);
  snap_number = static_cast<int>(istate[2]);
  curv_number = static_cast<int>(istate[3]);

  SetNumberOfParticles(np);
  HostArray2D<Real> rh("rh", nrdata, np);
  HostArray2D<int>  ih("ih", nidata, np);
  for (int p=0; p<np; ++p) {
    rh(IPX,p) = buf[7*p+0];  rh(IPY,p) = buf[7*p+1];  rh(IPZ,p) = buf[7*p+2];
    rh(IPVX,p) = buf[7*p+3]; rh(IPVY,p) = buf[7*p+4]; rh(IPVZ,p) = buf[7*p+5];
    rh(IPM,p) = buf[7*p+6];
    rh(IPTAU,p) = tau[p];
    ih(PGID,p) = ibuf[3*p+0];
    ih(PTAG,p) = ibuf[3*p+1];
    ih(PSP,p) = ibuf[3*p+2];
  }
  Kokkos::deep_copy(prtcl_rdata, rh);
  Kokkos::deep_copy(prtcl_idata, ih);
  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC: restarted " << np << " particles from " << fname << std::endl;
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicStartup
//! \brief called once from Driver::Initialize: builds the mesh state of the module and,
//! for a new run, writes the initial diagnostics

void Particles::NrpicStartup(bool res_flag) {
  Mesh *pm = pmy_pack->pmesh;
  if (!res_flag) {
    NrpicCreateParticles();
  }
  NrpicInitializeSources();
  if (res_flag) {
    // field dumps of earlier times were written before the restart
    while (field_next < nfield_times && field_times[field_next] < pm->time + 0.5*pm->dt) {
      ++field_next;
    }
    return;
  }
  NrpicProbe(0.0);
  if (nropt.hist_dcycle > 0) {
    NrpicWriteHistory(pm->time, pm->ncycle, true);
  }
  if (nropt.traj_dcycle > 0 && nropt.traj_ntrack > 0) {
    NrpicWriteTrajectories(pm->time, true);
  }
  if (nropt.cstat_dcycle > 0) {
    NrpicWriteConstraintStats(pm->time, true);
  }
  if (nropt.line_dcycle > 0) {
    NrpicWriteLine(pm->time, true);
  }
  if (nfield_times > 0) {
    NrpicWriteEnergyField(pm->time, 0);
  }
  if (nropt.snap_dt > 0.0) {
    NrpicWriteSnapshot(pm->time);
    snap_next_time = pm->time + nropt.snap_dt;
  }
  if (nropt.curv_dt > 0.0) {
    NrpicWriteCurvature(pm->time);
    curv_next_time = pm->time + nropt.curv_dt;
  }
}

//----------------------------------------------------------------------------------------
//! \fn  TaskStatus Particles::NrpicDiagnostics
//! \brief end-of-cycle diagnostics; the state now belongs to t^{n+1} = time + dt

TaskStatus Particles::NrpicDiagnostics(Driver *pdriver, int stage) {
  Mesh *pm = pmy_pack->pmesh;
  const Real tnew = pm->time + pm->dt;
  const int ncyc = pm->ncycle + 1;
  NrpicProbe(pm->dt);
  if (nropt.hist_dcycle > 0 && (ncyc % nropt.hist_dcycle == 0)) {
    NrpicWriteHistory(tnew, ncyc, false);
  }
  if (nropt.traj_dcycle > 0 && nropt.traj_ntrack > 0 &&
      (ncyc % nropt.traj_dcycle == 0)) {
    NrpicWriteTrajectories(tnew, false);
  }
  if (nropt.cstat_dcycle > 0 && (ncyc % nropt.cstat_dcycle == 0)) {
    NrpicWriteConstraintStats(tnew, false);
  }
  if (nropt.line_dcycle > 0 && (ncyc % nropt.line_dcycle == 0)) {
    NrpicWriteLine(tnew, false);
  }
  while (field_next < nfield_times && tnew >= field_times[field_next] - 0.5*pm->dt) {
    NrpicWriteEnergyField(tnew, field_next + 1);
    ++field_next;
  }
  if (nropt.snap_dt > 0.0 && tnew >= snap_next_time - 1.0e-10*nropt.snap_dt) {
    NrpicWriteSnapshot(tnew);
    snap_next_time += nropt.snap_dt;
  }
  if (nropt.curv_dt > 0.0 && tnew >= curv_next_time - 1.0e-10*nropt.curv_dt) {
    NrpicWriteCurvature(tnew);
    curv_next_time += nropt.curv_dt;
  }
  return TaskStatus::complete;
}

} // namespace particles
