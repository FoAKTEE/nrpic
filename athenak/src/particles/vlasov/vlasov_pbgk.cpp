//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_pbgk.cpp
//! \brief Asymptotic-preserving conservative relativistic Cell-BGK collision operator for
//! SCP/hybrid packets. Reuses global face-table cell bucketing (independent of MeshBlock
//! splits) and enforces exact per-cell 4-momentum (E_c, P_c) conservation to <1e-14
//! across arbitrary particle weights and arbitrary optical depths (O(1) cost as sigma->inf).

#include <cmath>
#include <cstdint>
#include <limits>
#include <string>

#include "athena.hpp"
#include "coordinates/adm.hpp"
#include "coordinates/cell_locations.hpp"
#include "mesh/mesh.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_metrics.hpp"
#include "particles/nrpic_mesh.hpp"
#include "particles/nrpic_collide.hpp"
#include "particles/vlasov/vlasov_types.hpp"
#include "utils/rng.hpp"
#include "utils/rng_mesh.hpp"

namespace particles {
namespace nrpic_vlasov_detail {

namespace {

constexpr int kPbgkMaxLevel = 23;

struct PbgkFaceOffsets {
  int b[3][kPbgkMaxLevel + 1];
};

}  // namespace

void CollideScpPbgk(Particles *pthis, MeshBlockPack *ppack) {
  VlasovState *vlv = pthis->vlv;
  if (vlv == nullptr || !vlv->opt.packet_mode || !vlv->opt.pbgk_on) return;
  const Real sigma0 = vlv->opt.coll_sigma;
  if (!(sigma0 > 0.0)) return;

  Mesh *pm = ppack->pmesh;
  const int np = pthis->nprtcl_thispack;
  if (np < 2) return;

  auto &indcs = pm->mb_indcs;
  const int nmb = ppack->nmb_thispack;
  const int gids = ppack->gids;
  const int f = vlv->opt.pbgk_cell_factor;
  const int nx[3] = {indcs.nx1, indcs.nx2, indcs.nx3};
  if (nx[0] % f != 0 || nx[1] % f != 0 || nx[2] % f != 0) {
    VlasovFatal("MeshBlock cells must be divisible by <particles> vlasov_pbgk_cell_factor");
  }
  const int nc1 = nx[0] / f, nc2 = nx[1] / f, nc3 = nx[2] / f;
  const std::int64_t ncell64 = static_cast<std::int64_t>(nmb) * nc3 * nc2 * nc1;
  if (ncell64 >= std::numeric_limits<int>::max()) {
    VlasovFatal("too many P-BGK collision cells for a 32-bit index");
  }
  const int ncell = static_cast<int>(ncell64);
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;

  if (static_cast<int>(vlv->pbgk_cell.extent(0)) < np) {
    Kokkos::realloc(vlv->pbgk_cell, np);
    Kokkos::realloc(vlv->pbgk_list, np);
    Kokkos::realloc(vlv->pbgk_q, np, 3);
  }
  if (static_cast<int>(vlv->pbgk_count.extent(0)) != ncell + 1) {
    Kokkos::realloc(vlv->pbgk_count, ncell + 1);
    Kokkos::realloc(vlv->pbgk_begin, ncell + 1);
  }

  int maxlev = 0;
  for (int m = 0; m < nmb; ++m) {
    const int lev = pm->lloc_eachmb[gids + m].level - pm->root_level;
    if (lev > maxlev) maxlev = lev;
  }
  if (maxlev > kPbgkMaxLevel) VlasovFatal("too many refinement levels for P-BGK");

  const int mnx[3] = {pm->mesh_indcs.nx1, pm->mesh_indcs.nx2, pm->mesh_indcs.nx3};
  const Real mxmin[3] = {pm->mesh_size.x1min, pm->mesh_size.x2min, pm->mesh_size.x3min};
  const Real mxmax[3] = {pm->mesh_size.x1max, pm->mesh_size.x2max, pm->mesh_size.x3max};
  PbgkFaceOffsets fb;
  std::int64_t nface = 0;
  for (int d = 0; d < 3; ++d) {
    for (int l = 0; l <= kPbgkMaxLevel; ++l) {
      fb.b[d][l] = static_cast<int>(nface);
      if (l <= maxlev) nface += (static_cast<std::int64_t>(mnx[d]) << l) + 1;
    }
  }
  if (nface >= std::numeric_limits<int>::max()) VlasovFatal("P-BGK face table too large");

  if (vlv->pbgk_face_maxlev != maxlev) {
    Kokkos::realloc(vlv->pbgk_face, nface);
    auto fh = Kokkos::create_mirror_view(vlv->pbgk_face);
    for (int d = 0; d < 3; ++d) {
      for (int l = 0; l <= maxlev; ++l) {
        const int n = mnx[d] << l;
        for (int i = 0; i <= n; ++i) {
          fh(fb.b[d][l] + i) = (i == 0) ? mxmin[d]
                             : ((i == n) ? mxmax[d] : LeftEdgeX(i, n, mxmin[d], mxmax[d]));
        }
      }
    }
    Kokkos::deep_copy(vlv->pbgk_face, fh);
    vlv->pbgk_face_maxlev = maxlev;
  }

  auto off = rng::CellOffsets(ppack);
  auto &pr = pthis->prtcl_rdata;
  auto &pi = pthis->prtcl_idata;
  auto sz = ppack->pmb->mb_size.d_view;
  auto pcell = vlv->pbgk_cell;
  auto lst = vlv->pbgk_list;
  auto cnt = vlv->pbgk_count;
  auto cbeg = vlv->pbgk_begin;
  auto face = vlv->pbgk_face;
  auto qbuf = vlv->pbgk_q;

  const Real dmin[3] = {pthis->nropt.dom_min[0], pthis->nropt.dom_min[1], pthis->nropt.dom_min[2]};
  const Real dlen[3] = {pthis->nropt.dom_len[0], pthis->nropt.dom_len[1], pthis->nropt.dom_len[2]};
  const bool per[3]  = {pthis->nropt.periodic[0], pthis->nropt.periodic[1], pthis->nropt.periodic[2]};

  // 1. Assign every active massive particle to its global mesh collision cell
  Kokkos::deep_copy(DevExeSpace(), cnt, 0);
  par_for("vlasov_pbgk_cell", DevExeSpace(), 0, np - 1, KOKKOS_LAMBDA(const int p) {
    pcell(p) = -1;
    if (pi(PGID, p) < 0) return;
    if (!(pr(IPM, p) > 0.0)) return;
    Real x[3] = {pr(IPX, p), pr(IPY, p), pr(IPZ, p)};
    if (!(Kokkos::isfinite(x[0] + x[1] + x[2]))) return;
    for (int d = 0; d < 3; ++d) x[d] = nrpic::WrapCoord(x[d], dmin[d], dlen[d], per[d]);
    const int m = nrpic::FindBlock(sz, nmb, pi(PGID, p) - gids, x[0], x[1], x[2]);
    if (m < 0) return;
    const int lev = static_cast<int>(off(m, 3));
    int ic[3];
    for (int d = 0; d < 3; ++d) {
      const std::int64_t ig = nrpic::CollCellIndex(face, fb.b[d][lev], off(m, 4 + d), x[d]);
      int il = static_cast<int>(ig - off(m, d));
      il = (il < 0) ? 0 : ((il > nx[d] - 1) ? (nx[d] - 1) : il);
      ic[d] = il / f;
    }
    const int c = ((m * nc3 + ic[2]) * nc2 + ic[1]) * nc1 + ic[0];
    pcell(p) = c;
    Kokkos::atomic_add(&cnt(c), 1);
  });

  // 2. Prefix sum to form contiguous per-cell slices [cbeg(c), cbeg(c+1))
  int ntot = 0;
  Kokkos::parallel_scan("vlasov_pbgk_scan", Kokkos::RangePolicy<DevExeSpace>(0, ncell + 1),
  KOKKOS_LAMBDA(const int c, int &upd, const bool final) {
    if (final) cbeg(c) = upd;
    upd += cnt(c);
  }, ntot);
  if (ntot < 2) return;

  Kokkos::deep_copy(DevExeSpace(), cnt, cbeg);
  par_for("vlasov_pbgk_fill", DevExeSpace(), 0, np - 1, KOKKOS_LAMBDA(const int p) {
    const int c = pcell(p);
    if (c >= 0) {
      const int slot = Kokkos::atomic_fetch_add(&cnt(c), 1);
      lst(slot) = p;
    }
  });

  // 3. Per-cell AP Maxwell-Juttner BGK resampling + exact 4-momentum projection
  const NrpicMetric msrc = pthis->nropt.metric;
  const bool mesh_metric = (msrc == NrpicMetric::mesh);
  const Real bh_mass = pthis->nropt.mass;
  const Real bh_spin = pthis->nropt.spin;
  const Real lat_dx  = pthis->nropt.lattice_dx;
  const int triad    = pthis->nropt.triad;
  auto m1            = pthis->met1;
  const Real dt      = pm->dt;
  const Real f3      = static_cast<Real>(f * f * f);
  const std::uint64_t seed   = vlv->pbgk_seed;
  const std::uint64_t step   = static_cast<std::uint64_t>(pm->ncycle);
  const std::uint64_t st_bgk = rng::Stream(rng::kStreamCollisions, 7);

  par_for("vlasov_pbgk_relax", DevExeSpace(), 0, ncell - 1, KOKKOS_LAMBDA(const int c) {
    const int b = cbeg(c);
    const int n = cbeg(c + 1) - b;
    if (n < 2) return;

    const int m = c / (nc3 * nc2 * nc1);
    int rem = c - m * (nc3 * nc2 * nc1);
    const int kc = rem / (nc2 * nc1);
    rem -= kc * (nc2 * nc1);
    const int jc = rem / nc1;
    const int icx = rem - jc * nc1;

    Real alp = 0.0;
    Real g[3][3];
    if (mesh_metric) {
      Real v[7] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
      for (int kk = 0; kk < f; ++kk) {
        for (int jj = 0; jj < f; ++jj) {
          for (int ii = 0; ii < f; ++ii) {
            const int k = ks + kc * f + kk, j = js + jc * f + jj, i = is + icx * f + ii;
            v[0] += m1(m, NRM_ALP, k, j, i);
            v[1] += m1(m, NRM_GXX, k, j, i);
            v[2] += m1(m, NRM_GXY, k, j, i);
            v[3] += m1(m, NRM_GXZ, k, j, i);
            v[4] += m1(m, NRM_GYY, k, j, i);
            v[5] += m1(m, NRM_GYZ, k, j, i);
            v[6] += m1(m, NRM_GZZ, k, j, i);
          }
        }
      }
      alp = v[0] / f3;
      g[0][0] = v[1] / f3; g[0][1] = v[2] / f3; g[0][2] = v[3] / f3;
      g[1][1] = v[4] / f3; g[1][2] = v[5] / f3; g[2][2] = v[6] / f3;
      g[1][0] = g[0][1]; g[2][0] = g[0][2]; g[2][1] = g[1][2];
    } else {
      const int lev = static_cast<int>(off(m, 3));
      const int cc[3] = {icx, jc, kc};
      Real xc[3];
      for (int d = 0; d < 3; ++d) {
        const std::int64_t i0 = fb.b[d][lev] + off(m, d) + cc[d] * f;
        xc[d] = 0.5 * (face(i0) + face(i0 + f));
      }
      nrpic::AdmPoint ap;
      if (msrc == NrpicMetric::kerr_schild) {
        nrpic::KerrSchildCart met{bh_mass, bh_spin};
        met(0, xc, ap);
      } else if (msrc == NrpicMetric::kerr_schild_sph) {
        nrpic::KerrSchildSph met{bh_mass, bh_spin};
        met(0, xc, ap);
      } else if (msrc == NrpicMetric::boyer_lindquist) {
        nrpic::BoyerLindquist met{bh_mass, bh_spin};
        met(0, xc, ap);
      } else {
        nrpic::LatticeMetric<nrpic::KerrSchildCart> met{
            {bh_mass, bh_spin}, {0.0, 0.0, 0.0}, {lat_dx, lat_dx, lat_dx}};
        met(0, xc, ap);
      }
      alp = ap.alp;
      for (int a = 0; a < 3; ++a) {
        for (int bb = 0; bb < 3; ++bb) g[a][bb] = ap.g[a][bb];
      }
    }

    const Real det = adm::SpatialDet(g[0][0], g[0][1], g[0][2], g[1][1], g[1][2], g[2][2]);
    nrpic::Triad tr;
    nrpic::BuildTriad(triad, g, tr);
    if (!(alp > 0.0) || !(det > 0.0)) return;
    const Real vol = sqrt(det) * sz(m).dx1 * sz(m).dx2 * sz(m).dx3 * f3;

    Real M_c = 0.0, E_c = 0.0, P_c[3] = {0.0, 0.0, 0.0};
    for (int k = 0; k < n; ++k) {
      const int p = lst(b + k);
      const Real mp = pr(IPM, p);
      const Real u0 = pr(IPVX, p), u1 = pr(IPVY, p), u2 = pr(IPVZ, p);
      Real uh[3];
      for (int a = 0; a < 3; ++a) uh[a] = tr.Si[a][0] * u0 + tr.Si[a][1] * u1 + tr.Si[a][2] * u2;
      qbuf(b + k, 0) = uh[0];
      qbuf(b + k, 1) = uh[1];
      qbuf(b + k, 2) = uh[2];
      const Real W = sqrt(1.0 + uh[0]*uh[0] + uh[1]*uh[1] + uh[2]*uh[2]);
      M_c += mp;
      E_c += mp * W;
      P_c[0] += mp * uh[0];
      P_c[1] += mp * uh[1];
      P_c[2] += mp * uh[2];
    }

    const Real M_inv2 = E_c * E_c - (P_c[0]*P_c[0] + P_c[1]*P_c[1] + P_c[2]*P_c[2]);
    if (!(M_inv2 > M_c * M_c * (1.0 + 1.0e-14))) return;
    const Real M_inv = sqrt(M_inv2);
    const Real w_com = M_inv / M_c;
    const Real theta = nrpic::vlasov::SafeMjThetaFromW(w_com);
    if (!(theta > 1.0e-12)) return;

    const Real vmol = nrpic::vlasov::MjVmol(theta);
    const Real U0 = E_c / M_inv;
    const Real U_cm[3] = {P_c[0] / M_inv, P_c[1] / M_inv, P_c[2] / M_inv};
    const Real tau_coll = (M_c * sigma0 * vmol * alp * dt) / (vol * U0 * U0);
    const Real p_coll = -expm1(-tau_coll);
    if (!(p_coll > 0.0)) return;

    int n_coll = 0;
    for (int k = 0; k < n; ++k) {
      const int p = lst(b + k);
      const std::uint64_t tag = static_cast<std::uint64_t>(pi(PTAG, p));
      const rng::Key key{seed, st_bgk, tag, step, 0ULL};
      if (rng::Uniform(key, 0ULL) < p_coll) {
        Real q_com[3], q_new[3];
        nrpic::vlasov::SampleMaxwellJuttner(theta, key, 1ULL, q_com);
        nrpic::vlasov::LorentzBoostMom(U0, U_cm, q_com, q_new);
        qbuf(b + k, 0) = q_new[0];
        qbuf(b + k, 1) = q_new[1];
        qbuf(b + k, 2) = q_new[2];
        ++n_coll;
      }
    }
    if (n_coll == 0) return;

    const bool ok = nrpic::vlasov::ProjectCellFourMomentumT(
        n,
        [&](int k) { return pr(IPM, lst(b + k)); },
        [&](int k, Real q[3]) { q[0] = qbuf(b + k, 0); q[1] = qbuf(b + k, 1); q[2] = qbuf(b + k, 2); },
        [&](int k, const Real q[3]) { qbuf(b + k, 0) = q[0]; qbuf(b + k, 1) = q[1]; qbuf(b + k, 2) = q[2]; },
        M_c, E_c, P_c);
    if (!ok) return;

    for (int k = 0; k < n; ++k) {
      const int p = lst(b + k);
      const Real q0 = qbuf(b + k, 0), q1 = qbuf(b + k, 1), q2 = qbuf(b + k, 2);
      pr(IPVX, p) = tr.S[0][0] * q0 + tr.S[0][1] * q1 + tr.S[0][2] * q2;
      pr(IPVY, p) = tr.S[1][0] * q0 + tr.S[1][1] * q1 + tr.S[1][2] * q2;
      pr(IPVZ, p) = tr.S[2][0] * q0 + tr.S[2][1] * q1 + tr.S[2][2] * q2;
    }
  });
}

}  // namespace nrpic_vlasov_detail
}  // namespace particles
