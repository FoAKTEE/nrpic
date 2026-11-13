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
//! tau = int alpha dt (trapezoidal rule).  At a MeshBlock corner the interpolation is
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
  const Real px = nropt.probe[0], py = nropt.probe[1], pz = nropt.probe[2];
  auto m1 = met1;
  const bool has_tm = nropt.deposit;
  DvceArray5D<Real> tm;
  if (has_tm) { tm = pmy_pack->ptmunu->u_tmunu; }

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
    const Real xf = xb[0] + ((c & 1) ? h[0] : 0.0);
    const Real yf = xb[1] + ((c & 2) ? h[1] : 0.0);
    const Real zf = xb[2] + ((c & 4) ? h[2] : 0.0);
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
    if (dt > 0.0) { tau_probe += 0.5*(alpha_probe + anew)*dt; }
    alpha_probe = anew;
    e_probe = se/sw;
  }
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
      lm += pr(IPM,p);
      lx += pr(IPM,p)*pr(IPVX,p);
      ly += pr(IPM,p)*pr(IPVY,p);
      lz += pr(IPM,p)*pr(IPVZ,p);
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
                 "[27]=int_Sz_filtered\n");
  }
  std::fprintf(fp, "%.15e %d %d %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e "
               "%.15e %.15e %.15e %.15e %d %.15e %d %.15e %d %d %d "
               "%.15e %.15e %.15e %.15e\n",
               time, ncycle, np, sum_m, sum_mw, sum_mu[0], sum_mu[1], sum_mu[2],
               dep_sum[0], dep_sum[1], dep_sum[2], dep_sum[3], alpha_probe, e_probe,
               tau_probe, amin, n_excised, mass_excised, n_escaped, mass_escaped,
               push_maxit, push_unconverged, pmy_pack->nmb_thispack,
               dep_sum_filt[0], dep_sum_filt[1], dep_sum_filt[2], dep_sum_filt[3]);
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
  // <basename>.trajmet.bin as records of 12 doubles: time, tag, alpha, beta^i, gamma_ij
  // (xx, xy, xz, yy, yz, zz), in the same order as the records of the trajectory file.
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
      DvceArray2D<Real> pmet("pmet", NRM_NVAR, np);
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
          for (int n=0; n<NRM_NVAR; ++n) { mbuf.push_back(mh(n,p)); }
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
//!   N records of 7 doubles (x^i, u_i, m), N int32 tags, N int32 species

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
//!   8 bytes "NRPRST02", int64 N, 7 doubles (tau_probe, alpha_probe, e_probe,
//!   mass_excised, mass_escaped, snap_next_time, curv_next_time), 4 int64 (n_excised,
//!   n_escaped, snap_number, curv_number), N records of 7 doubles, N records of 3 int32
//!   (gid, tag, species)

void Particles::NrpicWriteRestart(const std::string &fname) {
  std::FILE *fp = std::fopen(fname.c_str(), "wb");
  if (fp == nullptr) NrpicFatal("cannot open " + fname);
  const int np = nprtcl_thispack;
  const char magic[9] = "NRPRST02";
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
  if (std::fread(magic, 1, 8, fp) != 8 || std::strncmp(magic, "NRPRST02", 8) != 0) {
    NrpicFatal("bad magic in particle restart file " + fname);
  }
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
  if (res_flag) return;
  NrpicProbe(0.0);
  if (nropt.hist_dcycle > 0) {
    NrpicWriteHistory(pm->time, pm->ncycle, true);
  }
  if (nropt.traj_dcycle > 0 && nropt.traj_ntrack > 0) {
    NrpicWriteTrajectories(pm->time, true);
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
