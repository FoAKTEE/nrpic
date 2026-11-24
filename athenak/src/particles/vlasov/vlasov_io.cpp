//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_io.cpp
//! \brief Option parsing, unified GRLBV001/NRPIC001/inline initial-condition loading,
//! mesh initialization, history diagnostics, binary snapshots, and restarts for GR-LBV.

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
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/vlasov/vlasov_types.hpp"
#include "utils/rng.hpp"

namespace particles {

void Particles::NrpicVlasovInit(ParameterInput *pin) {
  if (vlv == nullptr) vlv = new VlasovState();
  VlasovOptions &opt = vlv->opt;

  const std::string ppush = pin->GetOrAddString("particles", "pusher", "vlasov_mfm");
  const std::string def_mode = (ppush == "vlasov_hybrid") ? "hybrid" : "mfm";
  const std::string mode_s = pin->GetOrAddString("particles", "vlasov_mode", def_mode);
  if (mode_s == "mfm") {
    opt.solver_mode = VLASOV_MODE_MFM;
  } else if (mode_s == "hybrid") {
    opt.solver_mode = VLASOV_MODE_HYBRID;
  } else if (mode_s == "scp") {
    opt.solver_mode = VLASOV_MODE_SCP;
  } else {
    nrpic_vlasov_detail::VlasovFatal("unknown <particles> vlasov_mode = " + mode_s);
  }

  opt.scp_n_q = pin->GetOrAddInteger("particles", "vlasov_scp_q", 14);
  if (opt.scp_n_q != 8 && opt.scp_n_q != 14 && opt.scp_n_q != 27) {
    nrpic_vlasov_detail::VlasovFatal("<particles> vlasov_scp_q must be 8, 14, or 27");
  }
  opt.scp_rotate   = pin->GetOrAddBoolean("particles", "vlasov_scp_rotate", true);
  opt.scp_s2_shell = pin->GetOrAddBoolean("particles", "vlasov_scp_s2_shell", false);
  opt.scp_s2_q     = pin->GetOrAddInteger("particles", "vlasov_scp_s2_q", 14);
  if (opt.scp_s2_q != 6 && opt.scp_s2_q != 12 && opt.scp_s2_q != 14 && opt.scp_s2_q != 26) {
    nrpic_vlasov_detail::VlasovFatal("<particles> vlasov_scp_s2_q must be 6, 12, 14, or 26");
  }

  const std::string push_s = pin->GetOrAddString("particles", "vlasov_pusher", "midpoint");
  if (push_s == "midpoint") {
    opt.scp_pusher = VLASOV_PUSH_MIDPOINT;
  } else if (push_s == "gl4") {
    opt.scp_pusher = VLASOV_PUSH_GL4;
  } else if (push_s == "boris") {
    opt.scp_pusher = VLASOV_PUSH_BORIS;
  } else {
    nrpic_vlasov_detail::VlasovFatal("unknown <particles> vlasov_pusher = " + push_s);
  }

  const std::string ti_s = pin->GetOrAddString("particles", "vlasov_time_interp", "linear");
  if (ti_s == "linear") {
    opt.time_interp = VLASOV_TINTERP_LINEAR;
  } else if (ti_s == "quadratic") {
    opt.time_interp = VLASOV_TINTERP_QUADRATIC;
  } else {
    nrpic_vlasov_detail::VlasovFatal("unknown <particles> vlasov_time_interp = " + ti_s);
  }

  // Lazily allocate 3rd time level metric array when quadratic time interpolation is selected
  if (opt.time_interp == VLASOV_TINTERP_QUADRATIC &&
      nropt.metric == NrpicMetric::mesh && !metric_is_static) {
    Mesh *pm = pmy_pack->pmesh;
    auto &indcs = pm->mb_indcs;
    const int nmb = std::max(pmy_pack->nmb_thispack, pm->nmb_maxperrank);
    const int nc1 = indcs.nx1 + 2 * indcs.ng;
    const int nc2 = indcs.nx2 + 2 * indcs.ng;
    const int nc3 = indcs.nx3 + 2 * indcs.ng;
    Kokkos::realloc(met_prev, nmb, NRM_NVAR, nc3, nc2, nc1);
    if (nropt.interp_bspline) {
      Kokkos::realloc(met_prevs, nmb, NRM_NVAR, nc3, nc2, nc1);
    }
  }

  const std::string basis_s = pin->GetOrAddString("particles", "vlasov_basis", "tophat");
  if (basis_s == "tophat") {
    opt.basis_kind = nrpic::vlasov::BASIS_TOPHAT;
  } else if (basis_s == "gaussian") {
    opt.basis_kind = nrpic::vlasov::BASIS_GAUSS;
  } else {
    nrpic_vlasov_detail::VlasovFatal("unknown <particles> vlasov_basis = " + basis_s);
  }

  opt.n_perp         = pin->GetOrAddInteger("particles", "vlasov_nperp", 3);
  opt.n_q_kick       = pin->GetOrAddInteger("particles", "vlasov_nq_kick", 3);
  opt.n_q_dep        = pin->GetOrAddInteger("particles", "vlasov_nq_dep", 3);
  const std::string pmode = pin->GetOrAddString("particles", "vlasov_pair_mode", "covariant");
  if (pmode == "covariant" || pmode == "eb") {
    opt.pair_mode = VLASOV_PAIR_EB;
  } else if (pmode == "v_only") {
    opt.pair_mode = VLASOV_PAIR_VONLY;
  } else {
    nrpic_vlasov_detail::VlasovFatal("unknown <particles> vlasov_pair_mode = " + pmode);
  }
  opt.use_analytic_vf = pin->GetOrAddBoolean("particles", "vlasov_analytic_vf", false);
  opt.cfl             = pin->GetOrAddReal("particles", "vlasov_cfl", 0.3);
  opt.fixed_substeps  = pin->GetOrAddInteger("particles", "vlasov_substeps", 0);
  opt.max_substeps    = pin->GetOrAddInteger("particles", "vlasov_max_substeps", 64);
  opt.coll_sigma      = pin->GetOrAddReal("particles", "vlasov_coll_sigma", 0.0);
  opt.bgk_track_e     = pin->GetOrAddBoolean("particles", "vlasov_bgk_track_e",
                          (pmy_pack->pz4c == nullptr && nropt.metric == NrpicMetric::mesh));
  opt.lim_eps_v       = pin->GetOrAddReal("particles", "vlasov_lim_eps_v", 0.1);
  const bool all_per  = nropt.periodic[0] && nropt.periodic[1] && nropt.periodic[2];
  opt.bnd_detect      = pin->GetOrAddBoolean("particles", "vlasov_bnd_detect", !all_per);
  opt.bnd_cm_tol      = pin->GetOrAddReal("particles", "vlasov_bnd_cm_tol", 0.35);
  opt.bnd_min_ngb     = pin->GetOrAddInteger("particles", "vlasov_bnd_min_ngb", 12);
  opt.noh_kappa       = pin->GetOrAddReal("particles", "vlasov_noh_kappa", 0.5);
  opt.kerr_r_exc      = pin->GetOrAddReal("particles", "vlasov_kerr_r_exc", 0.0);
  opt.pbgk_on         = pin->GetOrAddBoolean("particles", "vlasov_pbgk", false);
  opt.pbgk_cell_factor = pin->GetOrAddInteger("particles", "vlasov_pbgk_cell_factor", 1);
  if (opt.pbgk_cell_factor != 1 && opt.pbgk_cell_factor != 2 && opt.pbgk_cell_factor != 4) {
    nrpic_vlasov_detail::VlasovFatal("<particles> vlasov_pbgk_cell_factor must be 1, 2, or 4");
  }
  vlv->pbgk_seed = rng::RunSeed(pin);
  vlv_pbgk_on    = opt.pbgk_on;

  opt.packet_mode = (opt.solver_mode == VLASOV_MODE_SCP) ||
                    (opt.solver_mode == VLASOV_MODE_HYBRID &&
                     (opt.coll_sigma <= 0.0 || opt.pbgk_on));
  if (nr_multirank && !opt.packet_mode) {
    nrpic_vlasov_detail::VlasovFatal("GR-LBV MFM mode currently requires a single MPI rank");
  }

  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC Vlasov (GR-LBV): mode=" << mode_s
              << (opt.packet_mode ? " [SCP-packet]" : " [AP-MFM]")
              << ", pusher=" << push_s
              << ", time_interp=" << ti_s
              << ", basis=" << basis_s
              << ", pair=" << pmode
              << ", scp_q=" << opt.scp_n_q
              << (opt.scp_s2_shell ? (", s2_q=" + std::to_string(opt.scp_s2_q)) : "")
              << ", coll_sigma=" << opt.coll_sigma
              << ", kerr_r_exc=" << opt.kerr_r_exc
              << std::endl;
  }
}

void Particles::NrpicVlasovFree() {
  if (vlv != nullptr) {
    delete vlv;
    vlv = nullptr;
  }
}

void Particles::NrpicVlasovLoadFile(const std::string &fname) {
  if (vlv == nullptr) nrpic_vlasov_detail::VlasovFatal("NrpicVlasovLoadFile called before NrpicVlasovInit");

  // Support inline <particles> nparticles/p0_... when no file is given
  if (fname.empty()) {
    const int np = static_cast<int>(nr_inline.size() / 7);
    if (np == 0) {
      nrpic_vlasov_detail::VlasovFatal("<particles> pusher=vlasov requires particle_file or inline nparticles");
    }
    if (vlv->opt.packet_mode) {
      SetNumberOfParticles(np);
      HostArray2D<Real> rh("rh", nrdata, np);
      HostArray2D<int>  ih("ih", nidata, np);
      const int gids = pmy_pack->gids;
      for (int p = 0; p < np; ++p) {
        rh(IPX, p)  = nr_inline[7*p + 0]; rh(IPY, p)  = nr_inline[7*p + 1]; rh(IPZ, p)  = nr_inline[7*p + 2];
        rh(IPVX, p) = nr_inline[7*p + 3]; rh(IPVY, p) = nr_inline[7*p + 4]; rh(IPVZ, p) = nr_inline[7*p + 5];
        rh(IPM, p)  = nr_inline[7*p + 6];
        rh(IPTAU, p) = 0.0;
        ih(PGID, p) = gids;
        ih(PTAG, p) = p;
        ih(PSP, p)  = 0;
        ih(PPERI, p) = 0;
      }
      Kokkos::deep_copy(prtcl_rdata, rh);
      Kokkos::deep_copy(prtcl_idata, ih);
      return;
    }
    nrpic_vlasov_detail::AllocateState(*vlv, np, 1, 64);
    auto hx  = Kokkos::create_mirror_view(vlv->x);
    auto hm  = Kokkos::create_mirror_view(vlv->m);
    auto hP  = Kokkos::create_mirror_view(vlv->P);
    auto hPi = Kokkos::create_mirror_view(vlv->Pi);
    auto hu  = Kokkos::create_mirror_view(vlv->u_bar);
    auto hS  = Kokkos::create_mirror_view(vlv->Sigma);
    auto hsp = Kokkos::create_mirror_view(vlv->species);
    auto hac = Kokkos::create_mirror_view(vlv->active);
    auto hbg = Kokkos::create_mirror_view(vlv->blk_gid);
    const int gids = pmy_pack->gids;
    for (int a = 0; a < np; ++a) {
      for (int i = 0; i < 3; ++i) hx(i, a) = nr_inline[7*a + i];
      const Real ma = nr_inline[7*a + 6];
      const Real ua[3] = {nr_inline[7*a + 3], nr_inline[7*a + 4], nr_inline[7*a + 5]};
      hm(0, a) = ma;
      for (int i = 0; i < 3; ++i) {
        hu(0, i, a) = ua[i];
        hP(0, i, a) = ma * ua[i];
      }
      for (int s = 0; s < 6; ++s) hS(0, s, a) = 0.0;
      hPi(0, SYM_XX, a) = ma * ua[0]*ua[0];
      hPi(0, SYM_XY, a) = ma * ua[0]*ua[1];
      hPi(0, SYM_XZ, a) = ma * ua[0]*ua[2];
      hPi(0, SYM_YY, a) = ma * ua[1]*ua[1];
      hPi(0, SYM_YZ, a) = ma * ua[1]*ua[2];
      hPi(0, SYM_ZZ, a) = ma * ua[2]*ua[2];
      hsp(a) = 0; hac(a) = 1; hbg(a) = gids;
    }
    Kokkos::deep_copy(vlv->x, hx);
    Kokkos::deep_copy(vlv->m, hm);
    Kokkos::deep_copy(vlv->P, hP);
    Kokkos::deep_copy(vlv->Pi, hPi);
    Kokkos::deep_copy(vlv->u_bar, hu);
    Kokkos::deep_copy(vlv->Sigma, hS);
    Kokkos::deep_copy(vlv->species, hsp);
    Kokkos::deep_copy(vlv->active, hac);
    Kokkos::deep_copy(vlv->blk_gid, hbg);
    Kokkos::deep_copy(vlv->h, 0.0);
    return;
  }

  std::FILE *fp = std::fopen(fname.c_str(), "rb");
  if (fp == nullptr) nrpic_vlasov_detail::VlasovFatal("cannot open particle/Vlasov file " + fname);
  char magic[9] = {0};
  if (std::fread(magic, 1, 8, fp) != 8) {
    nrpic_vlasov_detail::VlasovFatal("short read on magic in " + fname);
  }

  // Auto-detect NRPIC001 format (seamlessly allows Wu & Most particle ICs in Vlasov mode)
  if (std::strncmp(magic, "NRPIC001", 8) == 0) {
    std::fclose(fp);
    if (vlv->opt.packet_mode) {
      NrpicLoadParticleFile(fname);
      return;
    }
    std::FILE *fp2 = std::fopen(fname.c_str(), "rb");
    char m2[8];
    std::int64_t n64 = 0;
    if (std::fread(m2, 1, 8, fp2) != 8 || std::fread(&n64, sizeof(std::int64_t), 1, fp2) != 1 || n64 <= 0) {
      nrpic_vlasov_detail::VlasovFatal("invalid NRPIC001 header in " + fname);
    }
    const int N = static_cast<int>(n64);
    std::vector<double> buf(7 * static_cast<size_t>(N));
    std::vector<std::int32_t> sp(static_cast<size_t>(N));
    if (std::fread(buf.data(), sizeof(double), buf.size(), fp2) != buf.size() ||
        std::fread(sp.data(), sizeof(std::int32_t), sp.size(), fp2) != sp.size()) {
      nrpic_vlasov_detail::VlasovFatal("truncated NRPIC001 file " + fname);
    }
    std::fclose(fp2);
    nrpic_vlasov_detail::AllocateState(*vlv, N, 1, 64);
    auto hx  = Kokkos::create_mirror_view(vlv->x);
    auto hm  = Kokkos::create_mirror_view(vlv->m);
    auto hP  = Kokkos::create_mirror_view(vlv->P);
    auto hPi = Kokkos::create_mirror_view(vlv->Pi);
    auto hu  = Kokkos::create_mirror_view(vlv->u_bar);
    auto hS  = Kokkos::create_mirror_view(vlv->Sigma);
    auto hsp = Kokkos::create_mirror_view(vlv->species);
    auto hac = Kokkos::create_mirror_view(vlv->active);
    auto hbg = Kokkos::create_mirror_view(vlv->blk_gid);
    const int gids = pmy_pack->gids;
    for (int a = 0; a < N; ++a) {
      hx(0, a) = buf[7*a + 0]; hx(1, a) = buf[7*a + 1]; hx(2, a) = buf[7*a + 2];
      const Real ua[3] = {buf[7*a + 3], buf[7*a + 4], buf[7*a + 5]};
      const Real ma = buf[7*a + 6];
      hm(0, a) = ma;
      for (int i = 0; i < 3; ++i) {
        hu(0, i, a) = ua[i];
        hP(0, i, a) = ma * ua[i];
      }
      for (int s = 0; s < 6; ++s) hS(0, s, a) = 0.0;
      hPi(0, SYM_XX, a) = ma * ua[0]*ua[0];
      hPi(0, SYM_XY, a) = ma * ua[0]*ua[1];
      hPi(0, SYM_XZ, a) = ma * ua[0]*ua[2];
      hPi(0, SYM_YY, a) = ma * ua[1]*ua[1];
      hPi(0, SYM_YZ, a) = ma * ua[1]*ua[2];
      hPi(0, SYM_ZZ, a) = ma * ua[2]*ua[2];
      hsp(a) = sp[a]; hac(a) = 1; hbg(a) = gids;
    }
    Kokkos::deep_copy(vlv->x, hx);
    Kokkos::deep_copy(vlv->m, hm);
    Kokkos::deep_copy(vlv->P, hP);
    Kokkos::deep_copy(vlv->Pi, hPi);
    Kokkos::deep_copy(vlv->u_bar, hu);
    Kokkos::deep_copy(vlv->Sigma, hS);
    Kokkos::deep_copy(vlv->species, hsp);
    Kokkos::deep_copy(vlv->active, hac);
    Kokkos::deep_copy(vlv->blk_gid, hbg);
    Kokkos::deep_copy(vlv->h, 0.0);
    return;
  }

  if (std::strncmp(magic, "GRLBV001", 8) != 0) {
    nrpic_vlasov_detail::VlasovFatal("bad magic in Vlasov file " + fname + " (expected GRLBV001 or NRPIC001)");
  }
  std::int64_t n64 = 0, nb64 = 0;
  double tfile = 0.0;
  if (std::fread(&n64, sizeof(std::int64_t), 1, fp) != 1 ||
      std::fread(&nb64, sizeof(std::int64_t), 1, fp) != 1 ||
      std::fread(&tfile, sizeof(double), 1, fp) != 1 ||
      n64 <= 0 || nb64 <= 0 || nb64 > nrpic::vlasov::MAX_BASIS) {
    nrpic_vlasov_detail::VlasovFatal("invalid GRLBV header in " + fname);
  }
  const int N  = static_cast<int>(n64);
  const int Nb = static_cast<int>(nb64);

  std::vector<double> x_raw(3 * static_cast<size_t>(N));
  std::vector<std::int32_t> sp_raw(static_cast<size_t>(N));
  std::vector<double> m_raw(static_cast<size_t>(N) * Nb);
  std::vector<double> u_raw(3 * static_cast<size_t>(N) * Nb);
  std::vector<double> s_raw(6 * static_cast<size_t>(N) * Nb);

  if (std::fread(x_raw.data(), sizeof(double), x_raw.size(), fp) != x_raw.size() ||
      std::fread(sp_raw.data(), sizeof(std::int32_t), sp_raw.size(), fp) != sp_raw.size() ||
      std::fread(m_raw.data(), sizeof(double), m_raw.size(), fp) != m_raw.size() ||
      std::fread(u_raw.data(), sizeof(double), u_raw.size(), fp) != u_raw.size() ||
      std::fread(s_raw.data(), sizeof(double), s_raw.size(), fp) != s_raw.size()) {
    nrpic_vlasov_detail::VlasovFatal("truncated GRLBV file " + fname);
  }
  std::fclose(fp);

  nrpic_vlasov_detail::AllocateState(*vlv, N, Nb, 64);
  vlv->load_time = tfile;

  auto hx  = Kokkos::create_mirror_view(vlv->x);
  auto hm  = Kokkos::create_mirror_view(vlv->m);
  auto hP  = Kokkos::create_mirror_view(vlv->P);
  auto hPi = Kokkos::create_mirror_view(vlv->Pi);
  auto hu  = Kokkos::create_mirror_view(vlv->u_bar);
  auto hS  = Kokkos::create_mirror_view(vlv->Sigma);
  auto hsp = Kokkos::create_mirror_view(vlv->species);
  auto hac = Kokkos::create_mirror_view(vlv->active);
  auto hbg = Kokkos::create_mirror_view(vlv->blk_gid);

  const int gids = pmy_pack->gids;
  for (int a = 0; a < N; ++a) {
    for (int i = 0; i < 3; ++i) hx(i, a) = x_raw[3*a + i];
    hsp(a) = sp_raw[a];
    hac(a) = 1;
    hbg(a) = gids;
    for (int al = 0; al < Nb; ++al) {
      const size_t idx = static_cast<size_t>(a) * Nb + al;
      const Real ma = m_raw[idx];
      hm(al, a) = ma;
      Real ua[3] = {u_raw[3*idx + 0], u_raw[3*idx + 1], u_raw[3*idx + 2]};
      Real sa6[6];
      for (int s = 0; s < 6; ++s) {
        sa6[s] = s_raw[6*idx + s];
        hS(al, s, a) = sa6[s];
      }
      for (int i = 0; i < 3; ++i) {
        hu(al, i, a) = ua[i];
        hP(al, i, a) = ma * ua[i];
      }
      hPi(al, SYM_XX, a) = ma * (sa6[SYM_XX] + ua[0]*ua[0]);
      hPi(al, SYM_XY, a) = ma * (sa6[SYM_XY] + ua[0]*ua[1]);
      hPi(al, SYM_XZ, a) = ma * (sa6[SYM_XZ] + ua[0]*ua[2]);
      hPi(al, SYM_YY, a) = ma * (sa6[SYM_YY] + ua[1]*ua[1]);
      hPi(al, SYM_YZ, a) = ma * (sa6[SYM_YZ] + ua[1]*ua[2]);
      hPi(al, SYM_ZZ, a) = ma * (sa6[SYM_ZZ] + ua[2]*ua[2]);
    }
  }

  Kokkos::deep_copy(vlv->x,       hx);
  Kokkos::deep_copy(vlv->m,       hm);
  Kokkos::deep_copy(vlv->P,       hP);
  Kokkos::deep_copy(vlv->Pi,      hPi);
  Kokkos::deep_copy(vlv->u_bar,   hu);
  Kokkos::deep_copy(vlv->Sigma,   hS);
  Kokkos::deep_copy(vlv->species, hsp);
  Kokkos::deep_copy(vlv->active,  hac);
  Kokkos::deep_copy(vlv->blk_gid, hbg);
  Kokkos::deep_copy(vlv->h,       0.0);

  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC Vlasov: read " << N << " elements x " << Nb
              << " velocity bases (time=" << tfile << ") from " << fname << std::endl;
  }
}

void Particles::NrpicVlasovInitializeOnMesh() {
  if (vlv == nullptr) return;
  vlv->met_prev_valid = false;
  vlv->dt_prev = -1.0;
  vlv->dt_step_cur = -1.0;

  if (vlv->opt.packet_mode) {
    nrpic_vlasov_detail::InitializeScpOnMesh(this, pmy_pack);
    return;
  }

  if (!vlv->restart_real.empty()) {
    const int N  = vlv->restart_meta[0];
    const int Nb = vlv->restart_meta[1];
    nrpic_vlasov_detail::AllocateState(*vlv, N, Nb, 64);

    auto hx  = Kokkos::create_mirror_view(vlv->x);
    auto hm  = Kokkos::create_mirror_view(vlv->m);
    auto hP  = Kokkos::create_mirror_view(vlv->P);
    auto hPi = Kokkos::create_mirror_view(vlv->Pi);
    auto hh  = Kokkos::create_mirror_view(vlv->h);
    auto hac = Kokkos::create_mirror_view(vlv->active);
    auto hsp = Kokkos::create_mirror_view(vlv->species);

    size_t off = 0;
    for (int i = 0; i < 3; ++i) for (int a = 0; a < N; ++a) hx(i, a) = vlv->restart_real[off++];
    for (int al = 0; al < Nb; ++al) for (int a = 0; a < N; ++a) hm(al, a) = vlv->restart_real[off++];
    for (int al = 0; al < Nb; ++al) for (int i = 0; i < 3; ++i) for (int a = 0; a < N; ++a) {
      hP(al, i, a) = vlv->restart_real[off++];
    }
    for (int al = 0; al < Nb; ++al) for (int s = 0; s < 6; ++s) for (int a = 0; a < N; ++a) {
      hPi(al, s, a) = vlv->restart_real[off++];
    }
    for (int a = 0; a < N; ++a) hh(a) = vlv->restart_real[off++];

    for (int a = 0; a < N; ++a) {
      hac(a) = vlv->restart_int[a];
      hsp(a) = vlv->restart_int[N + a];
    }
    Kokkos::deep_copy(vlv->x,       hx);
    Kokkos::deep_copy(vlv->m,       hm);
    Kokkos::deep_copy(vlv->P,       hP);
    Kokkos::deep_copy(vlv->Pi,      hPi);
    Kokkos::deep_copy(vlv->h,       hh);
    Kokkos::deep_copy(vlv->active,  hac);
    Kokkos::deep_copy(vlv->species, hsp);

    vlv->restart_real.clear(); vlv->restart_real.shrink_to_fit();
    vlv->restart_int.clear();  vlv->restart_int.shrink_to_fit();
    vlv->restart_meta.clear(); vlv->restart_meta.shrink_to_fit();
  }

  if (vlv->n_elem == 0) return;

  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int nmb  = pmy_pack->nmb_thispack;
  const int gids = pmy_pack->gids;
  nrpic_vlasov_detail::UpdateBlockGIDs(*vlv, nropt, sz, nmb, gids);

  nrpic_vlasov_detail::UpdateGeometry(*vlv, nropt, false, 1.8);
  nrpic_vlasov_detail::UpdateGeometry(*vlv, nropt, true,  1.2);
  nrpic_vlasov_detail::ConsToPrim(*vlv);

  vlv->opt.metric_grad_zero = false;
  vlv->opt.metric_is_minkowski = false;
  if (metric_is_static && nropt.metric == NrpicMetric::mesh && pmy_pack->pz4c == nullptr) {
    auto met = nrpic_vlasov_detail::BuildMetricHelper(this, pmy_pack, sz);
    auto act = vlv->active;
    auto xv  = vlv->x;
    auto gv  = vlv->blk_gid;
    int has_grad = 0;
    int non_mink = 0;
    Kokkos::parallel_reduce("vlasov_flat_chk", Kokkos::RangePolicy<DevExeSpace>(0, vlv->n_elem),
    KOKKOS_LAMBDA(const int a, int &lhas, int &lmink) {
      if (!act(a)) return;
      const Real pos[3] = {xv(0, a), xv(1, a), xv(2, a)};
      nrpic::AdmPoint ap;
      met(0, pos, gv(a), ap);
      if (nrpic_vlasov_detail::HasNonZeroGrad(ap)) lhas += 1;
      if (nrpic_vlasov_detail::IsNotMinkowski(ap)) lmink += 1;
    }, Kokkos::Sum<int>(has_grad), Kokkos::Sum<int>(non_mink));
    vlv->opt.metric_grad_zero = (has_grad == 0);
    vlv->opt.metric_is_minkowski = (has_grad == 0 && non_mink == 0);
  }
  vlv->initialized = true;
}

void Particles::NrpicVlasovWriteHistory(Real time, int ncycle, bool header) {
  if (vlv == nullptr || global_variable::my_rank != 0) return;

  if (vlv->opt.packet_mode) {
    const int np = nprtcl_thispack;
    auto sz  = pmy_pack->pmb->mb_size.d_view;
    auto met = nrpic_vlasov_detail::BuildMetricHelper(this, pmy_pack, sz);
    auto pr  = prtcl_rdata;
    auto pi  = prtcl_idata;

    array_sum::GlobalSum s_acc;
    Real a_min = 1.0e300;
    if (np > 0) {
      Kokkos::parallel_reduce("vlasov_pkt_hist", Kokkos::RangePolicy<DevExeSpace>(0, np),
      KOKKOS_LAMBDA(const int p, array_sum::GlobalSum &ls, Real &lamin) {
        const Real mp = pr(IPM, p);
        if (mp <= 0.0) return;
        const Real pos[3] = {pr(IPX, p), pr(IPY, p), pr(IPZ, p)};
        const Real u[3]   = {pr(IPVX, p), pr(IPVY, p), pr(IPVZ, p)};
        nrpic::AdmPoint ap;
        met(1, pos, pi(PGID, p), ap);
        lamin = fmin(lamin, ap.alp);
        Real gi[3][3], uup[3];
        nrpic::Inv3Sym(ap.g, gi);
        const Real W = nrpic::LorentzFactor(gi, u, uup);
        ls.the_array[0] += mp;
        ls.the_array[1] += mp * W;
        ls.the_array[2] += mp * u[0];
        ls.the_array[3] += mp * u[1];
        ls.the_array[4] += mp * u[2];
      }, Kokkos::Sum<array_sum::GlobalSum>(s_acc), Kokkos::Min<Real>(a_min));
    } else {
      a_min = 0.0;
    }
    const std::string fname = nr_basename + ".vlasov.hst";
    std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
    if (fp == nullptr) nrpic_vlasov_detail::VlasovFatal("cannot open " + fname);
    if (header) {
      std::fprintf(fp, "# [0]=time [1]=ncycle [2]=n_active [3]=m_tot [4]=E_tot "
                       "[5]=P_x [6]=P_y [7]=P_z [8]=m_trSigma [9]=h_min [10]=h_max "
                       "[11]=alpha_min [12]=substeps [13]=max_sig [14]=n_excised [15]=m_excised\n");
    }
    std::fprintf(fp, "%.15e %d %d %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e %d %.15e %d %.15e\n",
                 time, ncycle, np, s_acc.the_array[0], s_acc.the_array[1],
                 s_acc.the_array[2], s_acc.the_array[3], s_acc.the_array[4],
                 0.0, 0.0, 0.0, a_min, 1, 0.0,
                 n_excised + n_escaped, mass_excised + mass_escaped);
    std::fclose(fp);
    sum_m     = s_acc.the_array[0];
    sum_mu[0] = s_acc.the_array[2];
    sum_mu[1] = s_acc.the_array[3];
    sum_mu[2] = s_acc.the_array[4];
    return;
  }

  const int N   = vlv->n_elem;
  const int Nb  = vlv->n_basis;
  const int n_q = vlv->opt.n_q_dep;
  auto sz  = pmy_pack->pmb->mb_size.d_view;
  auto met = nrpic_vlasov_detail::BuildMetricHelper(this, pmy_pack, sz);

  auto act  = vlv->active;
  auto xv   = vlv->x;
  auto hv   = vlv->h;
  auto gids = vlv->blk_gid;
  auto mv   = vlv->m;
  auto Pv   = vlv->P;
  auto uv   = vlv->u_bar;
  auto Sv   = vlv->Sigma;

  array_sum::GlobalSum s_acc;
  Real h_min = 1.0e300, h_max = 0.0, a_min = 1.0e300;
  int n_act = 0;

  if (N > 0) {
    Kokkos::parallel_reduce("vlasov_hist", Kokkos::RangePolicy<DevExeSpace>(0, N),
    KOKKOS_LAMBDA(const int a, int &ln, array_sum::GlobalSum &ls,
                  Real &lhmin, Real &lhmax, Real &lamin) {
      if (!act(a)) return;
      ln += 1;
      lhmin = fmin(lhmin, hv(a));
      lhmax = fmax(lhmax, hv(a));
      const Real pos[3] = {xv(0, a), xv(1, a), xv(2, a)};
      nrpic::AdmPoint ap;
      met(1, pos, gids(a), ap);
      lamin = fmin(lamin, ap.alp);
      Real gi[3][3];
      nrpic::Inv3Sym(ap.g, gi);

      Real ma_sum = 0.0, px = 0.0, py = 0.0, pz = 0.0, ea_sum = 0.0, s_tr = 0.0;
      for (int al = 0; al < Nb; ++al) {
        const Real ma = mv(al, a);
        if (ma <= 0.0) continue;
        ma_sum += ma;
        px += Pv(al, 0, a); py += Pv(al, 1, a); pz += Pv(al, 2, a);
        Real ua[3], s6[N_SYM6], Sa[3][3], ea, pa[3], sa[3][3];
        for (int i = 0; i < 3; ++i) ua[i] = uv(al, i, a);
        for (int s = 0; s < N_SYM6; ++s) s6[s] = Sv(al, s, a);
        nrpic_vlasov_detail::UnpackSym6(s6, Sa);
        nrpic::vlasov::BasisStressEnergy(ma, ua, Sa, gi, n_q, ea, pa, sa);
        ea_sum += ea;
        s_tr   += ma * (Sa[0][0] + Sa[1][1] + Sa[2][2]);
      }
      ls.the_array[0] += ma_sum;
      ls.the_array[1] += ea_sum;
      ls.the_array[2] += px;
      ls.the_array[3] += py;
      ls.the_array[4] += pz;
      ls.the_array[5] += s_tr;
    }, Kokkos::Sum<int>(n_act), Kokkos::Sum<array_sum::GlobalSum>(s_acc),
       Kokkos::Min<Real>(h_min), Kokkos::Max<Real>(h_max), Kokkos::Min<Real>(a_min));
  }
  if (n_act == 0) { h_min = 0.0; a_min = 0.0; }

  const std::string fname = nr_basename + ".vlasov.hst";
  std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
  if (fp == nullptr) nrpic_vlasov_detail::VlasovFatal("cannot open " + fname);
  if (header) {
    std::fprintf(fp, "# [0]=time [1]=ncycle [2]=n_active [3]=m_tot [4]=E_tot "
                     "[5]=P_x [6]=P_y [7]=P_z [8]=m_trSigma [9]=h_min [10]=h_max "
                     "[11]=alpha_min [12]=substeps [13]=max_sig [14]=n_excised [15]=m_excised\n");
  }
  std::fprintf(fp, "%.15e %d %d %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e %.15e %d %.15e %d %.15e\n",
               time, ncycle, n_act, s_acc.the_array[0], s_acc.the_array[1],
               s_acc.the_array[2], s_acc.the_array[3], s_acc.the_array[4],
               s_acc.the_array[5], h_min, h_max, a_min,
               vlv->opt.substeps_last, vlv->opt.max_sig_last,
               n_excised + n_escaped, mass_excised + mass_escaped);
  std::fclose(fp);

  sum_m     = s_acc.the_array[0];
  sum_mu[0] = s_acc.the_array[2];
  sum_mu[1] = s_acc.the_array[3];
  sum_mu[2] = s_acc.the_array[4];
}

void Particles::NrpicVlasovWriteSnapshot(Real time) {
  if (vlv == nullptr || global_variable::my_rank != 0) {
    snap_number++;
    return;
  }
  char number[32];
  std::snprintf(number, sizeof(number), ".vlasov.%05d.bin", snap_number);
  const std::string fname = nr_basename + number;
  std::FILE *fp = std::fopen(fname.c_str(), "wb");
  if (fp == nullptr) nrpic_vlasov_detail::VlasovFatal("cannot open " + fname);

  if (vlv->opt.packet_mode) {
    const int np = nprtcl_thispack;
    const char magic[9] = "GRLBV001";
    std::int64_t n64 = np;
    std::int64_t nb64 = 1;
    double t64 = time;
    std::fwrite(magic, 1, 8, fp);
    std::fwrite(&n64, sizeof(std::int64_t), 1, fp);
    std::fwrite(&nb64, sizeof(std::int64_t), 1, fp);
    std::fwrite(&t64, sizeof(double), 1, fp);
    if (np > 0) {
      auto rh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_rdata);
      auto ih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_idata);
      std::vector<double> x_out(3 * static_cast<size_t>(np));
      std::vector<std::int32_t> sp_out(static_cast<size_t>(np));
      std::vector<double> m_out(static_cast<size_t>(np));
      std::vector<double> u_out(3 * static_cast<size_t>(np));
      std::vector<double> s_out(6 * static_cast<size_t>(np), 0.0);
      for (int p = 0; p < np; ++p) {
        x_out[3*p + 0] = rh(IPX, p);  x_out[3*p + 1] = rh(IPY, p);  x_out[3*p + 2] = rh(IPZ, p);
        u_out[3*p + 0] = rh(IPVX, p); u_out[3*p + 1] = rh(IPVY, p); u_out[3*p + 2] = rh(IPVZ, p);
        m_out[p] = rh(IPM, p);
        sp_out[p] = ih(PSP, p);
      }
      std::fwrite(x_out.data(), sizeof(double), x_out.size(), fp);
      std::fwrite(sp_out.data(), sizeof(std::int32_t), sp_out.size(), fp);
      std::fwrite(m_out.data(), sizeof(double), m_out.size(), fp);
      std::fwrite(u_out.data(), sizeof(double), u_out.size(), fp);
      std::fwrite(s_out.data(), sizeof(double), s_out.size(), fp);
    }
    std::fclose(fp);
    snap_number++;
    return;
  }

  const int N  = vlv->n_elem;
  const int Nb = vlv->n_basis;

  auto hx  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->x);
  auto hm  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->m);
  auto hu  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->u_bar);
  auto hS  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->Sigma);
  auto hsp = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->species);
  auto hac = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->active);

  int n_act = 0;
  for (int a = 0; a < N; ++a) if (hac(a)) ++n_act;

  const char magic[9] = "GRLBV001";
  std::int64_t n64  = n_act;
  std::int64_t nb64 = Nb;
  double t64 = time;
  std::fwrite(magic, 1, 8, fp);
  std::fwrite(&n64, sizeof(std::int64_t), 1, fp);
  std::fwrite(&nb64, sizeof(std::int64_t), 1, fp);
  std::fwrite(&t64, sizeof(double), 1, fp);

  if (n_act > 0) {
    std::vector<double> x_out(3 * static_cast<size_t>(n_act));
    std::vector<std::int32_t> sp_out(static_cast<size_t>(n_act));
    std::vector<double> m_out(static_cast<size_t>(n_act) * Nb);
    std::vector<double> u_out(3 * static_cast<size_t>(n_act) * Nb);
    std::vector<double> s_out(6 * static_cast<size_t>(n_act) * Nb);

    int k = 0;
    for (int a = 0; a < N; ++a) {
      if (!hac(a)) continue;
      for (int i = 0; i < 3; ++i) x_out[3*k + i] = hx(i, a);
      sp_out[k] = hsp(a);
      for (int al = 0; al < Nb; ++al) {
        const size_t idx = static_cast<size_t>(k) * Nb + al;
        m_out[idx] = hm(al, a);
        for (int i = 0; i < 3; ++i) u_out[3*idx + i] = hu(al, i, a);
        for (int s = 0; s < 6; ++s) s_out[6*idx + s] = hS(al, s, a);
      }
      ++k;
    }
    std::fwrite(x_out.data(), sizeof(double), x_out.size(), fp);
    std::fwrite(sp_out.data(), sizeof(std::int32_t), sp_out.size(), fp);
    std::fwrite(m_out.data(), sizeof(double), m_out.size(), fp);
    std::fwrite(u_out.data(), sizeof(double), u_out.size(), fp);
    std::fwrite(s_out.data(), sizeof(double), s_out.size(), fp);
  }
  std::fclose(fp);
  snap_number++;
}

void Particles::NrpicVlasovWriteRestart(const std::string &fname) {
  if (vlv == nullptr || global_variable::my_rank != 0) return;
  std::FILE *fp = std::fopen(fname.c_str(), "wb");
  if (fp == nullptr) nrpic_vlasov_detail::VlasovFatal("cannot open " + fname);

  const char magic[9] = "NRPVLV01";
  const std::int64_t meta[2] = {vlv->opt.packet_mode ? -1 : vlv->n_elem, vlv->n_basis};
  std::fwrite(magic, 1, 8, fp);
  std::fwrite(meta, sizeof(std::int64_t), 2, fp);
  if (vlv->opt.packet_mode) {
    std::fclose(fp);
    return;
  }

  const int N  = vlv->n_elem;
  const int Nb = vlv->n_basis;
  if (N > 0) {
    auto hx  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->x);
    auto hm  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->m);
    auto hP  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->P);
    auto hPi = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->Pi);
    auto hh  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->h);
    auto hac = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->active);
    auto hsp = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->species);

    std::vector<double> rbuf;
    rbuf.reserve(static_cast<size_t>(N) * (4 + 10 * Nb));
    for (int i = 0; i < 3; ++i) for (int a = 0; a < N; ++a) rbuf.push_back(hx(i, a));
    for (int al = 0; al < Nb; ++al) for (int a = 0; a < N; ++a) rbuf.push_back(hm(al, a));
    for (int al = 0; al < Nb; ++al) for (int i = 0; i < 3; ++i) for (int a = 0; a < N; ++a) {
      rbuf.push_back(hP(al, i, a));
    }
    for (int al = 0; al < Nb; ++al) for (int s = 0; s < 6; ++s) for (int a = 0; a < N; ++a) {
      rbuf.push_back(hPi(al, s, a));
    }
    for (int a = 0; a < N; ++a) rbuf.push_back(hh(a));

    std::vector<std::int32_t> ibuf(2 * static_cast<size_t>(N));
    for (int a = 0; a < N; ++a) {
      ibuf[a]     = hac(a);
      ibuf[N + a] = hsp(a);
    }
    std::fwrite(rbuf.data(), sizeof(double), rbuf.size(), fp);
    std::fwrite(ibuf.data(), sizeof(std::int32_t), ibuf.size(), fp);
  }
  std::fclose(fp);
}

void Particles::NrpicVlasovReadRestart(const std::string &fname) {
  if (vlv == nullptr) vlv = new VlasovState();
  std::FILE *fp = std::fopen(fname.c_str(), "rb");
  if (fp == nullptr) nrpic_vlasov_detail::VlasovFatal("cannot open Vlasov restart file " + fname);
  char magic[9] = {0};
  std::int64_t meta[2] = {0, 0};
  if (std::fread(magic, 1, 8, fp) != 8 || std::strncmp(magic, "NRPVLV01", 8) != 0 ||
      std::fread(meta, sizeof(std::int64_t), 2, fp) != 2) {
    nrpic_vlasov_detail::VlasovFatal("bad header in " + fname);
  }
  const int N  = static_cast<int>(meta[0]);
  const int Nb = static_cast<int>(meta[1]);
  if (N < 0) {
    std::fclose(fp);
    return;
  }
  vlv->restart_meta = {N, Nb};
  const size_t nreal = static_cast<size_t>(N) * (4 + 10 * Nb);
  vlv->restart_real.resize(nreal);
  vlv->restart_int.resize(2 * static_cast<size_t>(N));
  if (N > 0) {
    if (std::fread(vlv->restart_real.data(), sizeof(double), nreal, fp) != nreal) {
      nrpic_vlasov_detail::VlasovFatal("truncated real data in " + fname);
    }
    std::vector<std::int32_t> ibuf(2 * static_cast<size_t>(N));
    if (std::fread(ibuf.data(), sizeof(std::int32_t), ibuf.size(), fp) != ibuf.size()) {
      nrpic_vlasov_detail::VlasovFatal("truncated int data in " + fname);
    }
    for (size_t i = 0; i < ibuf.size(); ++i) vlv->restart_int[i] = ibuf[i];
  }
  std::fclose(fp);
}

}  // namespace particles
