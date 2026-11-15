//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file scalar_field_io.cpp
//! \brief start of the scalar field, its diagnostics in double precision and its restart
//! file.
//!
//! <basename>.sf.hst (text, every hist_dcycle cycles): box means (weighted with the
//! coordinate volume of the cells) and constraint norms, see the header line.
//! <basename>.sf.NNNNN.dump (binary, every dump_dcycle cycles or dump_dt):
//!   8 bytes "NRSFDMP1"; int64 nmb, nx1, nx2, nx3, nvar, cycle, nnoise; double time;
//!   per MeshBlock: int64 level (above the root), lx1, lx2, lx3; double x1min, x1max,
//!   x2min, x2max, x3min, x3max; nvar arrays of nx3*nx2*nx1 doubles (first index
//!   fastest) of the active cells: phi, Pi, chi, K = Khat + 2 Theta, alpha, H, M_x, M_y,
//!   M_z, E (all matter), then the nnoise stochastic fields.
//! <restart file>.sf: 8 bytes "NRSFRST1"; int64 extents of u0 (5); u0; int64 dump
//!   number; double next dump time; int64 ny; the ny lockstep data of the stochastic
//!   sources.  Amplitudes and tables are rebuilt from their keys.

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
#include "coordinates/adm.hpp"
#include "z4c/z4c.hpp"
#include "z4c/tmunu.hpp"
#include "scalar_field/scalar_field.hpp"

namespace scalarfield {

namespace {
void IoFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in scalar_field_io.cpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}
} // namespace

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::Startup
//! \brief called once from Driver::Initialize, after the ghost cells have been set (and
//! after the particles have deposited): stochastic sources on the current mesh,
//! constraints with the sources of the field, initial diagnostics of a new run

void ScalarField::Startup(bool res_flag) {
  Mesh *pm = pmy_pack->pmesh;
  NoiseSetup(res_flag);
  z4c::Z4c *pz4c = pmy_pack->pz4c;
  pz4c->Z4cToADM(pmy_pack);
  switch (pm->mb_indcs.ng) {
    case 2: pz4c->ADMConstraints<2>(pmy_pack); break;
    case 3: pz4c->ADMConstraints<3>(pmy_pack); break;
    case 4: pz4c->ADMConstraints<4>(pmy_pack); break;
  }
  if (res_flag) return;
  dump_number = 0;
  dump_next_time = pm->time + opt.dump_dt;
  if (opt.hist_dcycle > 0) {
    WriteHistory(pm->time, pm->ncycle, true);
  }
  if (opt.dump_dcycle > 0 || opt.dump_dt > 0.0) {
    NoiseFieldsOfState();
    WriteDump(pm->time);
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::MeshMeans
//! \brief means over the active cells, weighted with their coordinate volume:
//! mean = (phi, Pi, K, chi, alpha, phi^2, Pi^2) and mean[7] = the volume

void ScalarField::MeshMeans(Real mean[8]) {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  auto &size = pmy_pack->pmb->mb_size;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmkji = (pmy_pack->nmb_thispack)*nx3*nx2*nx1;
  const int nkji = nx3*nx2*nx1;
  const int nji = nx2*nx1;
  auto u0_ = u0;
  auto z0 = pmy_pack->pz4c->u0;
  const int ichi = z4c::Z4c::I_Z4C_CHI, ikh = z4c::Z4c::I_Z4C_KHAT;
  const int ith = z4c::Z4c::I_Z4C_THETA, ial = z4c::Z4c::I_Z4C_ALPHA;
  array_sum::GlobalSum sum;
  Kokkos::parallel_reduce("sf_means", Kokkos::RangePolicy<>(DevExeSpace(), 0, nmkji),
  KOKKOS_LAMBDA(const int &idx, array_sum::GlobalSum &lsum) {
    int m = (idx)/nkji;
    int k = (idx - m*nkji)/nji;
    int j = (idx - m*nkji - k*nji)/nx1;
    int i = (idx - m*nkji - k*nji - j*nx1) + is;
    k += ks;
    j += js;
    const Real vol = size.d_view(m).dx1*size.d_view(m).dx2*size.d_view(m).dx3;
    const Real phi = u0_(m,I_SF_PHI,k,j,i), pi = u0_(m,I_SF_PI,k,j,i);
    array_sum::GlobalSum v;
    v.the_array[0] = vol*phi;
    v.the_array[1] = vol*pi;
    v.the_array[2] = vol*(z0(m,ikh,k,j,i) + 2.0*z0(m,ith,k,j,i));
    v.the_array[3] = vol*z0(m,ichi,k,j,i);
    v.the_array[4] = vol*z0(m,ial,k,j,i);
    v.the_array[5] = vol*phi*phi;
    v.the_array[6] = vol*pi*pi;
    v.the_array[7] = vol;
    for (int n=8; n<NREDUCTION_VARIABLES; ++n) { v.the_array[n] = 0.0; }
    lsum += v;
  }, Kokkos::Sum<array_sum::GlobalSum>(sum));
  const Real vol = sum.the_array[7];
  for (int n=0; n<7; ++n) { mean[n] = sum.the_array[n]/vol; }
  mean[7] = vol;
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::WriteHistory
//! \brief one record of <basename>.sf.hst.  The constraints are those of the last
//! evaluation (end of the step).  [H] is the sum of the magnitudes of the terms of the
//! Hamiltonian constraint, |R| + (2/3) K^2 + At_ij At^ij + 16 pi E.

void ScalarField::WriteHistory(Real time, int ncycle, bool header) {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  auto &size = pmy_pack->pmb->mb_size;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmkji = (pmy_pack->nmb_thispack)*nx3*nx2*nx1;
  const int nkji = nx3*nx2*nx1;
  const int nji = nx2*nx1;
  Real mean[8];
  MeshMeans(mean);
  const Real mphi = mean[0], mpi = mean[1];

  auto u0_ = u0;
  auto z0 = pmy_pack->pz4c->u0;
  auto ucon = pmy_pack->pz4c->u_con;
  const int ichi = z4c::Z4c::I_Z4C_CHI, ikh = z4c::Z4c::I_Z4C_KHAT;
  const int ith = z4c::Z4c::I_Z4C_THETA;
  const int igxx = z4c::Z4c::I_Z4C_GXX, iaxx = z4c::Z4c::I_Z4C_AXX;
  const int icH = z4c::Z4c::I_CON_H, icM = z4c::Z4c::I_CON_M;
  // energy density of all matter, if there is any
  Tmunu *ptm = pmy_pack->ptmunu;
  const bool has_e = (ptm != nullptr);
  DvceArray5D<Real> utm;
  if (has_e) { utm = ptm->use_total ? ptm->u_tmunu_tot : ptm->u_tmunu; }
  const int ite = Tmunu::I_Tmunu_E;

  array_sum::GlobalSum sum;
  Real hmax = 0.0, mmax = 0.0;
  Kokkos::parallel_reduce("sf_hist", Kokkos::RangePolicy<>(DevExeSpace(), 0, nmkji),
  KOKKOS_LAMBDA(const int &idx, array_sum::GlobalSum &lsum, Real &lhmax, Real &lmmax) {
    int m = (idx)/nkji;
    int k = (idx - m*nkji)/nji;
    int j = (idx - m*nkji - k*nji)/nx1;
    int i = (idx - m*nkji - k*nji - j*nx1) + is;
    k += ks;
    j += js;
    const Real vol = size.d_view(m).dx1*size.d_view(m).dx2*size.d_view(m).dx3;
    const Real dphi = u0_(m,I_SF_PHI,k,j,i) - mphi, dpi = u0_(m,I_SF_PI,k,j,i) - mpi;
    const Real ham = ucon(m,icH,k,j,i);
    const Real mom2 = ucon(m,icM,k,j,i);
    const Real theta = z0(m,ith,k,j,i);
    const Real trk = z0(m,ikh,k,j,i) + 2.0*theta;
    const Real en = has_e ? utm(m,ite,k,j,i) : 0.0;
    // At_ij At^ij with the conformal metric
    Real guu[6];
    const Real det = adm::SpatialDet(z0(m,igxx,k,j,i), z0(m,igxx+1,k,j,i),
                                     z0(m,igxx+2,k,j,i), z0(m,igxx+3,k,j,i),
                                     z0(m,igxx+4,k,j,i), z0(m,igxx+5,k,j,i));
    adm::SpatialInv(1.0/det, z0(m,igxx,k,j,i), z0(m,igxx+1,k,j,i), z0(m,igxx+2,k,j,i),
                    z0(m,igxx+3,k,j,i), z0(m,igxx+4,k,j,i), z0(m,igxx+5,k,j,i),
                    &guu[0], &guu[1], &guu[2], &guu[3], &guu[4], &guu[5]);
    const int sym[3][3] = {{0, 1, 2}, {1, 3, 4}, {2, 4, 5}};
    Real aa = 0.0;
    for (int a=0; a<3; ++a)
    for (int b=0; b<3; ++b)
    for (int c=0; c<3; ++c)
    for (int d=0; d<3; ++d) {
      aa += guu[sym[a][c]]*guu[sym[b][d]]*z0(m,iaxx+sym[a][b],k,j,i)
            *z0(m,iaxx+sym[c][d],k,j,i);
    }
    const Real k23 = (2.0/3.0)*trk*trk;
    const Real ricci = ham - k23 + aa + 16.0*M_PI*en;
    array_sum::GlobalSum v;
    v.the_array[0] = vol*dphi*dphi;
    v.the_array[1] = vol*dpi*dpi;
    v.the_array[2] = vol*en;
    v.the_array[3] = vol*fabs(ham);
    v.the_array[4] = vol*ham*ham;
    v.the_array[5] = vol*mom2;
    v.the_array[6] = vol*theta*theta;
    v.the_array[7] = vol*(fabs(ricci) + k23 + fabs(aa) + 16.0*M_PI*fabs(en));
    for (int n=8; n<NREDUCTION_VARIABLES; ++n) { v.the_array[n] = 0.0; }
    lsum += v;
    lhmax = fmax(lhmax, fabs(ham));
    lmmax = fmax(lmmax, mom2);
    (void) ichi;
  }, Kokkos::Sum<array_sum::GlobalSum>(sum), Kokkos::Max<Real>(hmax),
     Kokkos::Max<Real>(mmax));
  const Real vol = mean[7];

  const std::string fname = basename + ".sf.hst";
  std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
  if (fp == nullptr) { IoFatal("cannot open " + fname); }
  if (header) {
    std::fprintf(fp, "# scalar field history: box means with coordinate-volume weights\n");
    std::fprintf(fp, "# [1]=time [2]=cycle [3]=<phi> [4]=<Pi> [5]=<K> [6]=<chi> "
                 "[7]=<alpha> [8]=rms(phi-<phi>) [9]=rms(Pi-<Pi>) [10]=<E> [11]=<|H|> "
                 "[12]=rms(H) [13]=max|H| [14]=rms|M| [15]=max|M| [16]=rms(Theta) "
                 "[17]=<[H]> [18]=lockstep_time [19]=phi_b [20]=Pi_b [21]=ln_a\n");
  }
  const bool ny = (y0.size() >= 4);
  std::fprintf(fp, "%.17e %d %.17e %.17e %.17e %.17e %.17e %.17e %.17e %.17e %.17e %.17e"
               " %.17e %.17e %.17e %.17e %.17e %.17e %.17e %.17e %.17e\n",
               time, ncycle, mean[0], mean[1], mean[2], mean[3], mean[4],
               std::sqrt(sum.the_array[0]/vol), std::sqrt(sum.the_array[1]/vol),
               sum.the_array[2]/vol, sum.the_array[3]/vol,
               std::sqrt(sum.the_array[4]/vol), hmax, std::sqrt(sum.the_array[5]/vol),
               std::sqrt(mmax), std::sqrt(sum.the_array[6]/vol), sum.the_array[7]/vol,
               ny ? y0[0] : 0.0, ny ? y0[1] : 0.0, ny ? y0[2] : 0.0, ny ? y0[3] : 0.0);
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::WriteDump
//! \brief the fields of the active cells in double precision (format: top of this file)

void ScalarField::WriteDump(Real time) {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmb = pmy_pack->nmb_thispack;
  const int cycle = (time > pm->time) ? pm->ncycle + 1 : pm->ncycle;
  const int nnoise = noise_ready ? nfld : 0;
  const int nvar = 10 + nnoise;

  auto hu = Kokkos::create_mirror_view(u0);
  Kokkos::deep_copy(hu, u0);
  auto hz = Kokkos::create_mirror_view(pmy_pack->pz4c->u0);
  Kokkos::deep_copy(hz, pmy_pack->pz4c->u0);
  auto hc = Kokkos::create_mirror_view(pmy_pack->pz4c->u_con);
  Kokkos::deep_copy(hc, pmy_pack->pz4c->u_con);
  Tmunu *ptm = pmy_pack->ptmunu;
  const bool has_e = (ptm != nullptr);
  DvceArray5D<Real> utm;
  if (has_e) { utm = ptm->use_total ? ptm->u_tmunu_tot : ptm->u_tmunu; }
  auto ht = Kokkos::create_mirror_view(utm);
  if (has_e) { Kokkos::deep_copy(ht, utm); }
  auto hn = Kokkos::create_mirror_view(u_noise);
  if (nnoise > 0) { Kokkos::deep_copy(hn, u_noise); }
  auto &size = pmy_pack->pmb->mb_size;

  char fname[512];
  std::snprintf(fname, sizeof(fname), "%s.sf.%05d.dump", basename.c_str(), dump_number);
  std::FILE *fp = std::fopen(fname, "wb");
  if (fp == nullptr) { IoFatal(std::string("cannot open ") + fname); }
  const char magic[8] = {'N', 'R', 'S', 'F', 'D', 'M', 'P', '1'};
  std::fwrite(magic, 1, 8, fp);
  const std::int64_t head[7] = {nmb, nx1, nx2, nx3, nvar, cycle, nnoise};
  std::fwrite(head, sizeof(std::int64_t), 7, fp);
  const double t = time;
  std::fwrite(&t, sizeof(double), 1, fp);
  const int ichi = z4c::Z4c::I_Z4C_CHI, ikh = z4c::Z4c::I_Z4C_KHAT;
  const int ith = z4c::Z4c::I_Z4C_THETA, ial = z4c::Z4c::I_Z4C_ALPHA;
  const int icH = z4c::Z4c::I_CON_H, icMx = z4c::Z4c::I_CON_MX;
  std::vector<double> buf(static_cast<std::size_t>(nx1)*nx2*nx3);
  for (int m=0; m<nmb; ++m) {
    const LogicalLocation &ll = pm->lloc_eachmb[pmy_pack->gids + m];
    const std::int64_t loc[4] = {ll.level - pm->root_level, ll.lx1, ll.lx2, ll.lx3};
    std::fwrite(loc, sizeof(std::int64_t), 4, fp);
    const double ext[6] = {size.h_view(m).x1min, size.h_view(m).x1max,
                           size.h_view(m).x2min, size.h_view(m).x2max,
                           size.h_view(m).x3min, size.h_view(m).x3max};
    std::fwrite(ext, sizeof(double), 6, fp);
    for (int v=0; v<nvar; ++v) {
      std::size_t c = 0;
      for (int k=ks; k<ks+nx3; ++k) {
        for (int j=js; j<js+nx2; ++j) {
          for (int i=is; i<is+nx1; ++i) {
            double val = 0.0;
            switch (v) {
              case 0: val = hu(m,I_SF_PHI,k,j,i); break;
              case 1: val = hu(m,I_SF_PI,k,j,i); break;
              case 2: val = hz(m,ichi,k,j,i); break;
              case 3: val = hz(m,ikh,k,j,i) + 2.0*hz(m,ith,k,j,i); break;
              case 4: val = hz(m,ial,k,j,i); break;
              case 5: val = hc(m,icH,k,j,i); break;
              case 6: val = hc(m,icMx,k,j,i); break;
              case 7: val = hc(m,icMx+1,k,j,i); break;
              case 8: val = hc(m,icMx+2,k,j,i); break;
              case 9: val = has_e ? ht(m,Tmunu::I_Tmunu_E,k,j,i) : 0.0; break;
              default: val = hn(m,v-10,k,j,i); break;
            }
            buf[c++] = val;
          }
        }
      }
      std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
    }
  }
  std::fclose(fp);
  NoiseWriteState(time, dump_number, false);
  ++dump_number;
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::WriteRestart
//! \brief writes the state of the scalar field next to the mesh restart file

void ScalarField::WriteRestart(const std::string &fname) {
  std::FILE *fp = std::fopen(fname.c_str(), "wb");
  if (fp == nullptr) { IoFatal("cannot open " + fname); }
  const char magic[8] = {'N', 'R', 'S', 'F', 'R', 'S', 'T', '1'};
  std::fwrite(magic, 1, 8, fp);
  std::int64_t dims[5];
  for (int d=0; d<5; ++d) { dims[d] = static_cast<std::int64_t>(u0.extent(d)); }
  std::fwrite(dims, sizeof(std::int64_t), 5, fp);
  auto hu = Kokkos::create_mirror_view(Kokkos::HostSpace(), u0);
  Kokkos::deep_copy(hu, u0);
  std::fwrite(hu.data(), sizeof(Real), hu.size(), fp);
  const std::int64_t dn = dump_number;
  std::fwrite(&dn, sizeof(std::int64_t), 1, fp);
  const double dnext = dump_next_time;
  std::fwrite(&dnext, sizeof(double), 1, fp);
  const std::int64_t ny = static_cast<std::int64_t>(y0.size());
  std::fwrite(&ny, sizeof(std::int64_t), 1, fp);
  if (ny > 0) { std::fwrite(y0.data(), sizeof(Real), y0.size(), fp); }
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::ReadRestart
//! \brief reads the state written by WriteRestart (the mesh must be the same)

void ScalarField::ReadRestart(const std::string &fname) {
  std::FILE *fp = std::fopen(fname.c_str(), "rb");
  if (fp == nullptr) { IoFatal("cannot open " + fname); }
  char magic[9] = {0};
  if (std::fread(magic, 1, 8, fp) != 8 || std::strncmp(magic, "NRSFRST1", 8) != 0) {
    IoFatal("bad magic in " + fname);
  }
  std::int64_t dims[5];
  if (std::fread(dims, sizeof(std::int64_t), 5, fp) != 5) { IoFatal(fname + " truncated"); }
  for (int d=0; d<5; ++d) {
    if (dims[d] != static_cast<std::int64_t>(u0.extent(d))) {
      IoFatal("the scalar field in " + fname + " does not have the extents of the mesh");
    }
  }
  auto hu = Kokkos::create_mirror_view(Kokkos::HostSpace(), u0);
  if (std::fread(hu.data(), sizeof(Real), hu.size(), fp) != hu.size()) {
    IoFatal(fname + " truncated");
  }
  Kokkos::deep_copy(u0, hu);
  std::int64_t dn = 0, ny = 0;
  double dnext = 0.0;
  if (std::fread(&dn, sizeof(std::int64_t), 1, fp) != 1 ||
      std::fread(&dnext, sizeof(double), 1, fp) != 1 ||
      std::fread(&ny, sizeof(std::int64_t), 1, fp) != 1) {
    IoFatal(fname + " truncated");
  }
  dump_number = static_cast<int>(dn);
  dump_next_time = dnext;
  if (ny != static_cast<std::int64_t>(y0.size())) {
    IoFatal("the stochastic sources of " + fname + " do not match those of the input");
  }
  if (ny > 0 && std::fread(y0.data(), sizeof(Real), y0.size(), fp) != y0.size()) {
    IoFatal(fname + " truncated");
  }
  std::fclose(fp);
}

} // namespace scalarfield
