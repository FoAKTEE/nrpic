//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file rng_test.cpp
//! \brief Unit test of the reproducible random numbers (utils/rng.hpp).  Everything is
//! evaluated inside kernels of the default execution space, so the same input tests the
//! processor build and the card build.  <problem> selects the parts:
//!   key_file    keys to evaluate (tracks/core/analysis/rng/make_keys.py writes it):
//!                 8 bytes "NRRNGKY1", int64 N, N records of 6 uint64
//!                 (seed, stream, entity, entity_hi, step, draw)
//!   table_file  draws for these keys (default rng_table.bin):
//!                 8 bytes "NRRNGTB1", int64 N, the N key records,
//!                 N records of 6 uint64 (the four words, Index with n = 1000003, upper
//!                 half of the product of the first two words),
//!                 N records of 9 doubles (Uniform4, Normal2, Direction)
//!   nstat       number of keys of the statistical sums (default 0: skipped); the sums
//!               and histograms go to <basename>.rng_stat.txt
//!   ntime       number of keys of the timing loops (default 0: skipped); the cost per
//!               call goes to <basename>.rng_time.txt
//!   nrepeat     repetitions of each timing loop, the fastest counts (default 3)
//!   cell_check  = true: draws keyed by the cells of the mesh of the run
//!               (utils/rng_mesh.hpp); per refinement level the number of cells and a
//!               checksum that does not depend on the division into MeshBlocks go to
//!               <basename>.rng_cells.txt
//! The seed of the statistical and timing parts is <job> rng_seed.

#include <algorithm>
#include <cinttypes>
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
#include "pgen/pgen.hpp"
#include "utils/rng.hpp"
#include "utils/rng_mesh.hpp"

namespace {

constexpr int kNSum = 40;

//! sums accumulated by the statistical kernels
struct RngSums {
  double v[kNSum];
  KOKKOS_INLINE_FUNCTION RngSums() {
    for (int n=0; n<kNSum; ++n) { v[n] = 0.0; }
  }
  KOKKOS_INLINE_FUNCTION RngSums(const RngSums &o) {
    for (int n=0; n<kNSum; ++n) { v[n] = o.v[n]; }
  }
  KOKKOS_INLINE_FUNCTION RngSums& operator=(const RngSums &o) {
    for (int n=0; n<kNSum; ++n) { v[n] = o.v[n]; }
    return *this;
  }
  KOKKOS_INLINE_FUNCTION RngSums& operator+=(const RngSums &o) {
    for (int n=0; n<kNSum; ++n) { v[n] += o.v[n]; }
    return *this;
  }
};

void RngFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in rng_test.cpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

using RngPolicy = Kokkos::RangePolicy<DevExeSpace, Kokkos::IndexType<std::int64_t>>;

//! fastest of nrep executions of a sum over n keys, in seconds
template <typename Functor>
double RngTime(const std::string &name, const std::int64_t n, const int nrep,
               const Functor &f, double &sum) {
  double best = 1.0e30;
  for (int r=0; r<nrep; ++r) {
    double s = 0.0;
    Kokkos::fence();
    Kokkos::Timer timer;
    Kokkos::parallel_reduce(name, RngPolicy(0, n), f, s);
    Kokkos::fence();
    best = std::min(best, timer.seconds());
    sum = s;
  }
  return best;
}

void RngWriteHist(std::FILE *fp, const char *name, const DvceArray1D<std::int64_t> &h) {
  auto hh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), h);
  std::fprintf(fp, "%s", name);
  for (size_t n=0; n<hh.extent(0); ++n) {
    std::fprintf(fp, " %" PRId64, hh(n));
  }
  std::fprintf(fp, "\n");
}

} // namespace

namespace Kokkos {
template <>
struct reduction_identity<RngSums> {
  KOKKOS_FORCEINLINE_FUNCTION static RngSums sum() { return RngSums(); }
};
} // namespace Kokkos

//----------------------------------------------------------------------------------------
//! \fn void ProblemGenerator::RngTest
//! \brief table of draws, statistical sums and cost of the random-number interface

void ProblemGenerator::RngTest(ParameterInput *pin, const bool restart) {
  if (restart) return;
  const std::string basename = pin->GetString("job", "basename");
  const std::string key_file = pin->GetOrAddString("problem", "key_file", "");
  const std::string table_file = pin->GetOrAddString("problem", "table_file",
                                                     "rng_table.bin");
  const std::int64_t nstat = static_cast<std::int64_t>(
                                 pin->GetOrAddReal("problem", "nstat", 0.0));
  const std::int64_t ntime = static_cast<std::int64_t>(
                                 pin->GetOrAddReal("problem", "ntime", 0.0));
  const int nrep = pin->GetOrAddInteger("problem", "nrepeat", 3);
  const std::uint64_t seed = rng::RunSeed(pin);
  std::cout << "RNG test: execution space " << DevExeSpace::name() << ", seed " << seed
            << std::endl;

  // ---- 1. table of draws for the keys of a file -----------------------------------
  if (!key_file.empty()) {
    std::FILE *fp = std::fopen(key_file.c_str(), "rb");
    if (fp == nullptr) RngFatal("cannot open " + key_file);
    char magic[9] = {0};
    std::int64_t n64 = 0;
    if (std::fread(magic, 1, 8, fp) != 8 || std::strncmp(magic, "NRRNGKY1", 8) != 0 ||
        std::fread(&n64, sizeof(std::int64_t), 1, fp) != 1 || n64 <= 0) {
      RngFatal("bad header in " + key_file);
    }
    const int nk = static_cast<int>(n64);
    std::vector<std::uint64_t> kbuf(6*static_cast<size_t>(nk));
    if (std::fread(kbuf.data(), sizeof(std::uint64_t), kbuf.size(), fp) != kbuf.size()) {
      RngFatal(key_file + " is truncated");
    }
    std::fclose(fp);

    DvceArray2D<std::uint64_t> keys("rng_keys", nk, 6), ints("rng_ints", nk, 6);
    DvceArray2D<double> reals("rng_reals", nk, 9);
    auto kh = Kokkos::create_mirror_view(keys);
    for (int i=0; i<nk; ++i) {
      for (int n=0; n<6; ++n) { kh(i,n) = kbuf[6*static_cast<size_t>(i)+n]; }
    }
    Kokkos::deep_copy(keys, kh);
    int nbad = 0;
    Kokkos::parallel_reduce("rng_table", Kokkos::RangePolicy<DevExeSpace>(0, nk),
    KOKKOS_LAMBDA(const int i, int &lbad) {
      const rng::Key key{keys(i,0), keys(i,1), keys(i,2), keys(i,4), keys(i,3)};
      const std::uint64_t draw = keys(i,5);
      std::uint64_t w[4];
      rng::Bits4(key, draw, w);
      for (int n=0; n<4; ++n) { ints(i,n) = w[n]; }
      ints(i,4) = rng::Index(key, draw, 1000003ULL);
      ints(i,5) = rng::MulHi64(w[0], w[1]);
      // the product of the device and the portable one must agree
      if (ints(i,5) != rng::MulHi64Portable(w[0], w[1])) { lbad += 1; }
      if (w[0] != rng::Bits(key, draw)) { lbad += 1; }
      double u[4], z[2], d[3];
      rng::Uniform4(key, draw, u);
      rng::Normal2(key, draw, z);
      rng::Direction(key, draw, d);
      if (u[0] != rng::Uniform(key, draw) || z[0] != rng::Normal(key, draw)) {
        lbad += 1;
      }
      for (int n=0; n<4; ++n) { reals(i,n) = u[n]; }
      reals(i,4) = z[0]; reals(i,5) = z[1];
      reals(i,6) = d[0]; reals(i,7) = d[1]; reals(i,8) = d[2];
    }, Kokkos::Sum<int>(nbad));
    if (nbad != 0) {
      RngFatal("internal consistency of the draws failed for " + std::to_string(nbad)
               + " keys");
    }
    auto ih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), ints);
    auto rh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), reals);
    std::vector<std::uint64_t> ibuf(6*static_cast<size_t>(nk));
    std::vector<double> rbuf(9*static_cast<size_t>(nk));
    for (int i=0; i<nk; ++i) {
      for (int n=0; n<6; ++n) { ibuf[6*static_cast<size_t>(i)+n] = ih(i,n); }
      for (int n=0; n<9; ++n) { rbuf[9*static_cast<size_t>(i)+n] = rh(i,n); }
    }
    fp = std::fopen(table_file.c_str(), "wb");
    if (fp == nullptr) RngFatal("cannot open " + table_file);
    std::fwrite("NRRNGTB1", 1, 8, fp);
    std::fwrite(&n64, sizeof(std::int64_t), 1, fp);
    std::fwrite(kbuf.data(), sizeof(std::uint64_t), kbuf.size(), fp);
    std::fwrite(ibuf.data(), sizeof(std::uint64_t), ibuf.size(), fp);
    std::fwrite(rbuf.data(), sizeof(double), rbuf.size(), fp);
    std::fclose(fp);
    std::cout << "RNG test: wrote the draws of " << nk << " keys to " << table_file
              << std::endl;
  }

  // ---- 2. statistical sums ----------------------------------------------------------
  if (nstat > 0) {
    const std::string fname = basename + ".rng_stat.txt";
    std::FILE *fp = std::fopen(fname.c_str(), "w");
    if (fp == nullptr) RngFatal("cannot open " + fname);
    std::fprintf(fp, "# statistical sums of utils/rng.hpp, execution space %s\n",
                 DevExeSpace::name());
    std::fprintf(fp, "nstat %" PRId64 "\nseed %" PRIu64 "\n", nstat, seed);

    // uniform deviates: central moments, correlation with the deviate of the key in
    // which one field is larger by one, between the words of a call, between kinds
    {
      DvceArray1D<std::int64_t> hist("rng_hu", 1024);
      RngSums tot;
      const std::uint64_t st = rng::Stream(rng::kStreamTests, 1);
      Kokkos::parallel_reduce("rng_stat_u", RngPolicy(0, nstat),
      KOKKOS_LAMBDA(const std::int64_t i, RngSums &s) {
        const std::uint64_t e = static_cast<std::uint64_t>(i);
        const rng::Key key{seed, st, e, 7};
        double u[4];
        rng::Uniform4(key, 0, u);
        const double d = u[0] - 0.5;
        s.v[0] += d; s.v[1] += d*d; s.v[2] += d*d*d; s.v[3] += d*d*d*d;
        const rng::Key ke{seed, st, e + 1, 7};
        const rng::Key kt{seed, st, e, 8};
        const rng::Key ks{seed, st + 1, e, 7};
        const rng::Key ki{seed, rng::Stream(rng::kStreamTests + 1, 1), e, 7};
        const rng::Key kd{seed + 1, st, e, 7};
        const rng::Key kh{seed, st, e, 7, 1};
        s.v[4] += d*(rng::Uniform(ke, 0) - 0.5);
        s.v[5] += d*(rng::Uniform(kt, 0) - 0.5);
        s.v[6] += d*(rng::Uniform(key, 1) - 0.5);
        s.v[7] += d*(rng::Uniform(ks, 0) - 0.5);
        s.v[8] += d*(rng::Uniform(ki, 0) - 0.5);
        s.v[9] += d*(rng::Uniform(kd, 0) - 0.5);
        s.v[10] += d*(rng::Uniform(kh, 0) - 0.5);
        s.v[11] += d*(u[1] - 0.5);
        s.v[12] += d*(u[2] - 0.5);
        s.v[13] += d*(u[3] - 0.5);
        double z[2], dir[3];
        rng::Normal2(key, 0, z);
        rng::Direction(key, 0, dir);
        s.v[14] += d*z[0];
        s.v[15] += d*dir[2];
        s.v[16] += z[0]*dir[2];
        Kokkos::atomic_add(&hist(static_cast<int>(u[0]*1024.0)),
                           static_cast<std::int64_t>(1));
      }, Kokkos::Sum<RngSums>(tot));
      const char *names[17] = {"u_m1", "u_m2", "u_m3", "u_m4", "u_lag_entity",
          "u_lag_step", "u_lag_draw", "u_lag_substream", "u_lag_stream", "u_lag_seed",
          "u_lag_entity_hi", "u_word01", "u_word02", "u_word03", "u_normal", "u_dirz",
          "normal_dirz"};
      for (int n=0; n<17; ++n) { std::fprintf(fp, "%s %.17e\n", names[n], tot.v[n]); }
      RngWriteHist(fp, "hist_u", hist);
    }

    // normal pairs: raw moments up to the eighth of both members, their correlation,
    // numbers beyond 3, 4, 5 and 6, the largest modulus
    {
      DvceArray1D<std::int64_t> hist1("rng_hz1", 256), hist2("rng_hz2", 256);
      RngSums tot;
      double zmax = 0.0;
      const std::uint64_t st = rng::Stream(rng::kStreamTests, 2);
      Kokkos::parallel_reduce("rng_stat_z", RngPolicy(0, nstat),
      KOKKOS_LAMBDA(const std::int64_t i, RngSums &s, double &lmax) {
        const rng::Key key{seed, st, static_cast<std::uint64_t>(i), 7};
        double z[2];
        rng::Normal2(key, 0, z);
        for (int m=0; m<2; ++m) {
          double p = 1.0;
          for (int n=0; n<8; ++n) {
            p *= z[m];
            s.v[8*m+n] += p;
          }
          const double az = fabs(z[m]);
          if (az > 3.0) { s.v[18+4*m] += 1.0; }
          if (az > 4.0) { s.v[19+4*m] += 1.0; }
          if (az > 5.0) { s.v[20+4*m] += 1.0; }
          if (az > 6.0) { s.v[21+4*m] += 1.0; }
          lmax = (az > lmax) ? az : lmax;
        }
        s.v[16] += z[0]*z[1];
        s.v[17] += z[0]*z[0]*z[1]*z[1];
        int b1 = static_cast<int>(floor((z[0] + 8.0)*16.0));
        int b2 = static_cast<int>(floor((z[1] + 8.0)*16.0));
        b1 = (b1 < 0) ? 0 : ((b1 > 255) ? 255 : b1);
        b2 = (b2 < 0) ? 0 : ((b2 > 255) ? 255 : b2);
        Kokkos::atomic_add(&hist1(b1), static_cast<std::int64_t>(1));
        Kokkos::atomic_add(&hist2(b2), static_cast<std::int64_t>(1));
      }, Kokkos::Sum<RngSums>(tot), Kokkos::Max<double>(zmax));
      for (int m=0; m<2; ++m) {
        for (int n=0; n<8; ++n) {
          std::fprintf(fp, "z%d_m%d %.17e\n", m+1, n+1, tot.v[8*m+n]);
        }
        for (int n=0; n<4; ++n) {
          std::fprintf(fp, "z%d_gt%d %.17e\n", m+1, n+3, tot.v[18+4*m+n]);
        }
      }
      std::fprintf(fp, "z_z1z2 %.17e\nz_z1sqz2sq %.17e\nz_max %.17e\n", tot.v[16],
                   tot.v[17], zmax);
      RngWriteHist(fp, "hist_z1", hist1);
      RngWriteHist(fp, "hist_z2", hist2);
    }

    // directions: first and second moments, fourth moment of n_z, deviation from unit
    // length, histograms of n_z and of the azimuth
    {
      DvceArray1D<std::int64_t> histz("rng_hnz", 256), histp("rng_hphi", 256);
      RngSums tot;
      double nmax = 0.0;
      const std::uint64_t st = rng::Stream(rng::kStreamTests, 3);
      Kokkos::parallel_reduce("rng_stat_d", RngPolicy(0, nstat),
      KOKKOS_LAMBDA(const std::int64_t i, RngSums &s, double &lmax) {
        const rng::Key key{seed, st, static_cast<std::uint64_t>(i), 7};
        double d[3];
        rng::Direction(key, 0, d);
        s.v[0] += d[0]; s.v[1] += d[1]; s.v[2] += d[2];
        s.v[3] += d[0]*d[0]; s.v[4] += d[1]*d[1]; s.v[5] += d[2]*d[2];
        s.v[6] += d[0]*d[1]; s.v[7] += d[0]*d[2]; s.v[8] += d[1]*d[2];
        s.v[9] += d[2]*d[2]*d[2]*d[2];
        const double dev = fabs(d[0]*d[0] + d[1]*d[1] + d[2]*d[2] - 1.0);
        lmax = (dev > lmax) ? dev : lmax;
        int bz = static_cast<int>((d[2] + 1.0)*128.0);
        bz = (bz < 0) ? 0 : ((bz > 255) ? 255 : bz);
        const double phi = atan2(d[1], d[0]);
        int bp = static_cast<int>((phi*0.15915494309189535 + 0.5)*256.0);
        bp = (bp < 0) ? 0 : ((bp > 255) ? 255 : bp);
        Kokkos::atomic_add(&histz(bz), static_cast<std::int64_t>(1));
        Kokkos::atomic_add(&histp(bp), static_cast<std::int64_t>(1));
      }, Kokkos::Sum<RngSums>(tot), Kokkos::Max<double>(nmax));
      const char *names[10] = {"d_x", "d_y", "d_z", "d_xx", "d_yy", "d_zz", "d_xy",
                               "d_xz", "d_yz", "d_zzzz"};
      for (int n=0; n<10; ++n) { std::fprintf(fp, "%s %.17e\n", names[n], tot.v[n]); }
      std::fprintf(fp, "d_norm_dev_max %.17e\n", nmax);
      RngWriteHist(fp, "hist_dz", histz);
      RngWriteHist(fp, "hist_dphi", histp);
    }
    std::fclose(fp);
    std::cout << "RNG test: statistical sums of " << nstat << " keys in " << fname
              << std::endl;
  }

  // ---- 3. cost per call -------------------------------------------------------------
  if (ntime > 0) {
    const std::string fname = basename + ".rng_time.txt";
    std::FILE *fp = std::fopen(fname.c_str(), "w");
    if (fp == nullptr) RngFatal("cannot open " + fname);
    std::fprintf(fp, "# cost of utils/rng.hpp, execution space %s, fastest of %d loops\n"
                 "# name  seconds  ns_per_call  calls_per_second  checksum\n",
                 DevExeSpace::name(), nrep);
    std::fprintf(fp, "ntime %" PRId64 "\n", ntime);
    const std::uint64_t st = rng::Stream(rng::kStreamTests, 4);
    double sum = 0.0;
    auto report = [&](const char *name, const double t) {
      const double ns = 1.0e9*t/static_cast<double>(ntime);
      std::fprintf(fp, "%s %.6e %.4f %.4e %.17e\n", name, t, ns,
                   static_cast<double>(ntime)/t, sum);
      std::cout << "RNG test: " << name << " " << ns << " ns per call" << std::endl;
    };
    // loop without a draw
    double t = RngTime("rng_time_empty", ntime, nrep,
        KOKKOS_LAMBDA(const std::int64_t i, double &s) {
          s += rng::ToUniform(static_cast<std::uint64_t>(i)*0x9E3779B97F4A7C15ULL);
        }, sum);
    report("empty", t);
    t = RngTime("rng_time_bits4", ntime, nrep,
        KOKKOS_LAMBDA(const std::int64_t i, double &s) {
          const rng::Key key{seed, st, static_cast<std::uint64_t>(i), 7};
          std::uint64_t w[4];
          rng::Bits4(key, 0, w);
          s += rng::ToUniform(w[0] ^ w[1] ^ w[2] ^ w[3]);
        }, sum);
    report("bits4", t);
    t = RngTime("rng_time_uniform", ntime, nrep,
        KOKKOS_LAMBDA(const std::int64_t i, double &s) {
          const rng::Key key{seed, st, static_cast<std::uint64_t>(i), 7};
          s += rng::Uniform(key, 0);
        }, sum);
    report("uniform", t);
    t = RngTime("rng_time_uniform4", ntime, nrep,
        KOKKOS_LAMBDA(const std::int64_t i, double &s) {
          const rng::Key key{seed, st, static_cast<std::uint64_t>(i), 7};
          double u[4];
          rng::Uniform4(key, 0, u);
          s += u[0] + u[1] + u[2] + u[3];
        }, sum);
    report("uniform4", t);
    t = RngTime("rng_time_index", ntime, nrep,
        KOKKOS_LAMBDA(const std::int64_t i, double &s) {
          const rng::Key key{seed, st, static_cast<std::uint64_t>(i), 7};
          s += static_cast<double>(rng::Index(key, 0, 1000003ULL));
        }, sum);
    report("index", t);
    t = RngTime("rng_time_normal2", ntime, nrep,
        KOKKOS_LAMBDA(const std::int64_t i, double &s) {
          const rng::Key key{seed, st, static_cast<std::uint64_t>(i), 7};
          double z[2];
          rng::Normal2(key, 0, z);
          s += z[0] + z[1];
        }, sum);
    report("normal2", t);
    t = RngTime("rng_time_direction", ntime, nrep,
        KOKKOS_LAMBDA(const std::int64_t i, double &s) {
          const rng::Key key{seed, st, static_cast<std::uint64_t>(i), 7};
          double d[3];
          rng::Direction(key, 0, d);
          s += d[0] + d[1] + d[2];
        }, sum);
    report("direction", t);
    std::fclose(fp);
  }

  // ---- 4. draws keyed by the cells of the mesh ----------------------------------------
  if (pin->GetOrAddBoolean("problem", "cell_check", false)) {
    MeshBlockPack *pmbp = pmy_mesh_->pmb_pack;
    auto &indcs = pmy_mesh_->mb_indcs;
    const int is = indcs.is, js = indcs.js, ks = indcs.ks;
    const int nmb = pmbp->nmb_thispack;
    const std::uint64_t st = rng::Stream(rng::kStreamTests, 6);
    auto off = rng::CellOffsets(pmbp);
    const std::string fname = basename + ".rng_cells.txt";
    std::FILE *fp = std::fopen(fname.c_str(), "w");
    if (fp == nullptr) RngFatal("cannot open " + fname);
    std::fprintf(fp, "# draws keyed by cells: level, cells, checksum of the active "
                 "cells\n");
    std::fprintf(fp, "meshblocks %d\n", nmb);
    const int nlev = pmy_mesh_->max_level - pmy_mesh_->root_level + 1;
    for (int lev=0; lev<nlev; ++lev) {
      std::uint64_t csum = 0;
      std::int64_t ncell = 0;
      Kokkos::parallel_reduce("rng_cells",
        Kokkos::MDRangePolicy<DevExeSpace, Kokkos::Rank<4>>(
          {0, ks, js, is}, {nmb, indcs.ke+1, indcs.je+1, indcs.ie+1}),
      KOKKOS_LAMBDA(const int m, const int k, const int j, const int i,
                    std::uint64_t &lsum, std::int64_t &lnc) {
        if (off(m,3) != lev) return;
        const rng::Key key{seed, st, rng::CellEntity(off(m,0) + (i - is),
                                                     off(m,1) + (j - js),
                                                     off(m,2) + (k - ks)),
                           3, static_cast<std::uint64_t>(off(m,3))};
        const std::uint64_t zb = Kokkos::bit_cast<std::uint64_t>(rng::Normal(key, 0));
        lsum += rng::Bits(key, 0) ^ ((zb << 17) | (zb >> 47));
        lnc += 1;
      }, Kokkos::Sum<std::uint64_t>(csum), Kokkos::Sum<std::int64_t>(ncell));
      std::fprintf(fp, "level %d cells %" PRId64 " checksum %016" PRIx64 "\n", lev,
                   ncell, csum);
      std::cout << "RNG test: level " << lev << ", " << ncell << " cells, checksum "
                << std::hex << csum << std::dec << std::endl;
    }
    std::fclose(fp);
  }
  return;
}
