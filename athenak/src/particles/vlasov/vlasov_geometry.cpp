//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_geometry.cpp
//! \brief State allocation, spatial CSR hash grid, smoothing length iteration, neighbor
//! tables, unordered edge construction, and conservative-to-primitive repair for GR-LBV.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <utility>

#include "athena.hpp"
#include "particles/vlasov/vlasov_types.hpp"

namespace particles {
namespace nrpic_vlasov_detail {

void AllocateState(VlasovState &st, int n_elem, int n_basis, int max_ngb) {
  st.n_elem = n_elem;
  st.n_basis = n_basis;
  st.max_ngb = max_ngb;

  Kokkos::realloc(st.x,       3, n_elem);
  Kokkos::realloc(st.x0,      3, n_elem);
  Kokkos::realloc(st.v_cell,  3, n_elem);
  Kokkos::realloc(st.v0_cell, 3, n_elem);
  Kokkos::realloc(st.u_bulk,  3, n_elem);

  Kokkos::realloc(st.m,   n_basis, n_elem);
  Kokkos::realloc(st.m0,  n_basis, n_elem);
  Kokkos::realloc(st.dm,  n_basis, n_elem);
  Kokkos::realloc(st.P,   n_basis, 3, n_elem);
  Kokkos::realloc(st.P0,  n_basis, 3, n_elem);
  Kokkos::realloc(st.dP,  n_basis, 3, n_elem);
  Kokkos::realloc(st.Pi,  n_basis, N_SYM6, n_elem);
  Kokkos::realloc(st.Pi0, n_basis, N_SYM6, n_elem);
  Kokkos::realloc(st.dPi, n_basis, N_SYM6, n_elem);

  Kokkos::realloc(st.E0,     n_elem);
  Kokkos::realloc(st.E_cons, n_elem);
  Kokkos::realloc(st.dE,     n_elem);
  Kokkos::realloc(st.cell_noh, 8, (st.opt.coll_sigma > 0.0 && st.opt.noh_kappa > 0.0) ? n_elem : 0);

  Kokkos::realloc(st.D,     n_basis, n_elem);
  Kokkos::realloc(st.u_bar, n_basis, 3, n_elem);
  Kokkos::realloc(st.Sigma, n_basis, N_SYM6, n_elem);

  Kokkos::realloc(st.h,       n_elem);
  Kokkos::realloc(st.V,       n_elem);
  Kokkos::realloc(st.Einv,    N_SYM6, n_elem);
  Kokkos::realloc(st.active,  n_elem);
  Kokkos::realloc(st.species, n_elem);
  Kokkos::realloc(st.blk_gid, n_elem);
  Kokkos::realloc(st.is_bnd,  n_elem);

  Kokkos::realloc(st.grad_D, n_basis, 3, n_elem);
  Kokkos::realloc(st.grad_u, n_basis, 3, 3, n_elem);
  Kokkos::realloc(st.grad_S, n_basis, N_SYM6, 3, n_elem);

  Kokkos::realloc(st.ngb_cnt,  n_elem);
  Kokkos::realloc(st.prev_cnt, n_elem);
  Kokkos::realloc(st.ngb_ids,  max_ngb, n_elem);
  Kokkos::realloc(st.prev_ids, max_ngb, n_elem);
  Kokkos::realloc(st.new_pab,  max_ngb * n_basis, n_elem);
  Kokkos::realloc(st.prev_pab, max_ngb * n_basis, n_elem);

  Kokkos::realloc(st.edge_off, n_elem);
  st.edge_cap = std::max(1024, n_elem * 24);
  Kokkos::realloc(st.edge_a, st.edge_cap);
  Kokkos::realloc(st.edge_b, st.edge_cap);

  st.grid_cap = 4096;
  Kokkos::realloc(st.grid_cell_id, n_elem);
  Kokkos::realloc(st.grid_elem,    n_elem);
  Kokkos::realloc(st.grid_cnt,     st.grid_cap);
  Kokkos::realloc(st.grid_off,     st.grid_cap);
  Kokkos::realloc(st.grid_cur,     st.grid_cap);

  Kokkos::deep_copy(st.prev_cnt, 0);
  Kokkos::deep_copy(st.ngb_cnt,  0);
  Kokkos::deep_copy(st.is_bnd,   0);
}

void ResetMfmBuffers(VlasovState &st) {
  st.n_elem = 0;
  st.n_edges = 0;
  st.max_ngb = 0;
  st.edge_cap = 0;
  st.grid_cap = 0;
  st.x = DvceArray2D<Real>();
  st.x0 = DvceArray2D<Real>();
  st.v_cell = DvceArray2D<Real>();
  st.v0_cell = DvceArray2D<Real>();
  st.u_bulk = DvceArray2D<Real>();
  st.m = DvceArray2D<Real>();
  st.m0 = DvceArray2D<Real>();
  st.dm = DvceArray2D<Real>();
  st.P = DvceArray3D<Real>();
  st.P0 = DvceArray3D<Real>();
  st.dP = DvceArray3D<Real>();
  st.Pi = DvceArray3D<Real>();
  st.Pi0 = DvceArray3D<Real>();
  st.dPi = DvceArray3D<Real>();
  st.E0 = DvceArray1D<Real>();
  st.E_cons = DvceArray1D<Real>();
  st.dE = DvceArray1D<Real>();
  st.cell_noh = DvceArray2D<Real>();
  st.D = DvceArray2D<Real>();
  st.u_bar = DvceArray3D<Real>();
  st.Sigma = DvceArray3D<Real>();
  st.h = DvceArray1D<Real>();
  st.V = DvceArray1D<Real>();
  st.Einv = DvceArray2D<Real>();
  st.active = DvceArray1D<int>();
  st.species = DvceArray1D<int>();
  st.blk_gid = DvceArray1D<int>();
  st.is_bnd = DvceArray1D<int>();
  st.grad_D = DvceArray3D<Real>();
  st.grad_u = DvceArray4D<Real>();
  st.grad_S = DvceArray4D<Real>();
  st.ngb_cnt = DvceArray1D<int>();
  st.ngb_ids = DvceArray2D<int>();
  st.new_pab = DvceArray2D<int>();
  st.prev_cnt = DvceArray1D<int>();
  st.prev_ids = DvceArray2D<int>();
  st.prev_pab = DvceArray2D<int>();
  st.edge_off = DvceArray1D<int>();
  st.edge_a = DvceArray1D<int>();
  st.edge_b = DvceArray1D<int>();
  st.grid_cell_id = DvceArray1D<int>();
  st.grid_cnt = DvceArray1D<int>();
  st.grid_off = DvceArray1D<int>();
  st.grid_cur = DvceArray1D<int>();
  st.grid_elem = DvceArray1D<int>();
}

void GrowNeighborCapacity(VlasovState &st, int new_max_ngb) {
  const int old_cap = st.max_ngb;
  if (new_max_ngb <= old_cap) return;
  const int N = st.n_elem;
  const int Nb = st.n_basis;

  DvceArray2D<int> p_ids_new("vlasov_prev_ids", new_max_ngb, N);
  DvceArray2D<int> p_pab_new("vlasov_prev_pab", new_max_ngb * Nb, N);
  auto p_ids_old = st.prev_ids;
  auto p_pab_old = st.prev_pab;
  auto p_cnt     = st.prev_cnt;

  par_for("vlasov_grow_ngb", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    const int c = p_cnt(a);
    const int keep = (c < old_cap) ? c : old_cap;
    for (int k = 0; k < keep; ++k) {
      p_ids_new(k, a) = p_ids_old(k, a);
      for (int al = 0; al < Nb; ++al) {
        p_pab_new(k * Nb + al, a) = p_pab_old(k * Nb + al, a);
      }
    }
  });

  st.prev_ids = p_ids_new;
  st.prev_pab = p_pab_new;
  Kokkos::realloc(st.ngb_ids, new_max_ngb, N);
  Kokkos::realloc(st.new_pab, new_max_ngb * Nb, N);
  st.max_ngb = new_max_ngb;
}

VlasovGridMeta RebuildSpatialGrid(VlasovState &st, const NrpicOptions &nropt,
                                  const VlasovReduceStats &rs, Real h_scale) {
  VlasovGridMeta gm;
  for (int d = 0; d < 3; ++d) {
    if (nropt.periodic[d]) {
      gm.gmin[d] = nropt.dom_min[d];
      gm.glen[d] = nropt.dom_len[d];
    } else {
      const Real lo = (d == 0) ? rs.xmin : ((d == 1) ? rs.ymin : rs.zmin);
      const Real hi = (d == 0) ? rs.xmax : ((d == 1) ? rs.ymax : rs.zmax);
      const Real span = std::max(hi - lo, 1.0e-6);
      gm.gmin[d] = lo - 0.01 * span;
      gm.glen[d] = span * 1.02;
    }
  }
  const Real h_ref = (rs.n_act > 0 && rs.h_sum > 0.0)
                     ? (rs.h_sum / static_cast<Real>(rs.n_act))
                     : rs.h_max;
  const Real cs = std::max(2.0 * h_scale * h_ref, 1.0e-12);
  for (int d = 0; d < 3; ++d) {
    int n = static_cast<int>(std::floor(gm.glen[d] / cs));
    if (n < 1) n = 1;
    if (n > 64) n = 64;
    gm.ng[d] = n;
  }
  while (static_cast<std::int64_t>(gm.ng[0]) * gm.ng[1] * gm.ng[2] > 131072) {
    int dm = 0;
    if (gm.ng[1] > gm.ng[dm]) dm = 1;
    if (gm.ng[2] > gm.ng[dm]) dm = 2;
    gm.ng[dm] = std::max(1, gm.ng[dm] / 2);
  }
  gm.n_cells = gm.ng[0] * gm.ng[1] * gm.ng[2];
  for (int d = 0; d < 3; ++d) {
    gm.inv_cdx[d] = static_cast<Real>(gm.ng[d]) / gm.glen[d];
  }

  if (gm.n_cells > st.grid_cap) {
    st.grid_cap = gm.n_cells;
    Kokkos::realloc(st.grid_cnt, st.grid_cap);
    Kokkos::realloc(st.grid_off, st.grid_cap);
    Kokkos::realloc(st.grid_cur, st.grid_cap);
  }

  auto gcnt = Kokkos::subview(st.grid_cnt, std::make_pair(0, gm.n_cells));
  auto goff = Kokkos::subview(st.grid_off, std::make_pair(0, gm.n_cells));
  auto gcur = Kokkos::subview(st.grid_cur, std::make_pair(0, gm.n_cells));
  Kokkos::deep_copy(DevExeSpace(), gcnt, 0);

  const int N = st.n_elem;
  auto xv = st.x;
  auto act = st.active;
  auto gcid = st.grid_cell_id;
  auto gelm = st.grid_elem;

  par_for("vlasov_grid_cnt", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    if (!act(a)) {
      gcid(a) = -1;
      return;
    }
    const Real pos[3] = {xv(0, a), xv(1, a), xv(2, a)};
    const int cid = GridCellOf(pos, gm.gmin, gm.inv_cdx, gm.ng);
    gcid(a) = cid;
    Kokkos::atomic_inc(&gcnt(cid));
  });

  Kokkos::parallel_scan("vlasov_grid_scan", Kokkos::RangePolicy<DevExeSpace>(0, gm.n_cells),
  KOKKOS_LAMBDA(const int c, int &upd, const bool final) {
    if (final) {
      goff(c) = upd;
      gcur(c) = 0;
    }
    upd += gcnt(c);
  });

  par_for("vlasov_grid_fill", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    const int cid = gcid(a);
    if (cid < 0) return;
    const int k = Kokkos::atomic_fetch_add(&gcur(cid), 1);
    gelm(goff(cid) + k) = a;
  });

  return gm;
}

VlasovReduceStats GatherStats(VlasovState &st) {
  VlasovReduceStats rs;
  const int N = st.n_elem;
  if (N == 0) return rs;
  auto xv = st.x;
  auto hv = st.h;
  auto act = st.active;
  int n_act = 0;
  Real h_max = 0.0, h_sum = 0.0;
  Real xmin = 1.0e300, ymin = 1.0e300, zmin = 1.0e300;
  Real xmax = -1.0e300, ymax = -1.0e300, zmax = -1.0e300;
  Kokkos::parallel_reduce("vlasov_stats", Kokkos::RangePolicy<DevExeSpace>(0, N),
  KOKKOS_LAMBDA(const int a, int &ln, Real &lh, Real &lh_s, Real &lx0, Real &ly0, Real &lz0,
                Real &lx1, Real &ly1, Real &lz1) {
    if (!act(a)) return;
    ln += 1;
    const Real ha = hv(a);
    lh = fmax(lh, ha);
    lh_s += ha;
    lx0 = fmin(lx0, xv(0, a)); lx1 = fmax(lx1, xv(0, a));
    ly0 = fmin(ly0, xv(1, a)); ly1 = fmax(ly1, xv(1, a));
    lz0 = fmin(lz0, xv(2, a)); lz1 = fmax(lz1, xv(2, a));
  }, Kokkos::Sum<int>(n_act), Kokkos::Max<Real>(h_max), Kokkos::Sum<Real>(h_sum),
     Kokkos::Min<Real>(xmin), Kokkos::Min<Real>(ymin), Kokkos::Min<Real>(zmin),
     Kokkos::Max<Real>(xmax), Kokkos::Max<Real>(ymax), Kokkos::Max<Real>(zmax));
  rs.n_act = n_act;
  rs.h_max = h_max;
  rs.h_sum = h_sum;
  rs.xmin = xmin; rs.ymin = ymin; rs.zmin = zmin;
  rs.xmax = xmax; rs.ymax = ymax; rs.zmax = zmax;
  return rs;
}

void SeedHFromNearest(VlasovState &st, const NrpicOptions &nropt, const VlasovReduceStats &rs) {
  const int N = st.n_elem;
  if (rs.n_act <= 1) {
    Kokkos::deep_copy(st.h, 1.0);
    return;
  }
  auto xv = st.x;
  auto hv = st.h;
  auto act = st.active;
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3]  = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};

  if (N <= 16384) {
    par_for("vlasov_seed_h_nn", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
      if (!act(a)) {
        hv(a) = 0.0;
        return;
      }
      const Real xa[3] = {xv(0, a), xv(1, a), xv(2, a)};
      Real r2_min = 1.0e300;
      for (int b = 0; b < N; ++b) {
        if (b == a || !act(b)) continue;
        const Real xb[3] = {xv(0, b), xv(1, b), xv(2, b)};
        Real dx[3];
        WrapDiff(dlen, per, xa, xb, dx);
        const Real r2 = dx[0]*dx[0] + dx[1]*dx[1] + dx[2]*dx[2];
        if (r2 > 0.0 && r2 < r2_min) r2_min = r2;
      }
      hv(a) = fmax(1.3 * sqrt(r2_min), 1.0e-12);
    });
  } else {
    const Real bx = std::max(rs.xmax - rs.xmin, 1.0e-6);
    const Real by = std::max(rs.ymax - rs.ymin, 1.0e-6);
    const Real bz = std::max(rs.zmax - rs.zmin, 1.0e-6);
    const Real lx = per[0] ? dlen[0] : bx;
    const Real ly = per[1] ? dlen[1] : by;
    const Real lz = per[2] ? dlen[2] : bz;
    const Real h0 = std::max(1.3 * std::cbrt((lx * ly * lz) / static_cast<Real>(rs.n_act)),
                             1.0e-12);
    Kokkos::deep_copy(hv, h0);
  }
}

int FillNeighborsAndCount(VlasovState &st, const NrpicOptions &nropt,
                          const VlasovGridMeta &gm, bool fill_ids) {
  const int N = st.n_elem;
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3]  = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
  auto xv   = st.x;
  auto hv   = st.h;
  auto act  = st.active;
  auto goff = st.grid_off;
  auto gcnt = st.grid_cnt;
  auto gelm = st.grid_elem;
  auto ncnt = st.ngb_cnt;
  auto nids = st.ngb_ids;
  const int cap = st.max_ngb;

  Kokkos::deep_copy(DevExeSpace(), ncnt, 0);

  par_for("vlasov_ngb_scatter", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    if (!act(a)) return;
    const Real xa[3] = {xv(0, a), xv(1, a), xv(2, a)};
    const Real ha = hv(a);
    const Real r_cut_a = 2.0 * ha;
    const Real r_cut_a2 = r_cut_a * r_cut_a;

    int ix[3], lo[3], hi[3];
    bool full[3];
    GridCellIndices(xa, gm.gmin, gm.inv_cdx, gm.ng, ix);
    ComputeCellStencil(r_cut_a, gm.inv_cdx, gm.ng, lo, hi, full);

    constexpr int kLocNgb = 96;
    int loc_a[kLocNgb];
    int n_loc = 0;

    for (int dz = lo[2]; dz <= hi[2]; ++dz) {
      int cz = full[2] ? dz : (ix[2] + dz);
      if (!full[2]) {
        if (per[2]) cz = (cz + gm.ng[2]) % gm.ng[2];
        else if (cz < 0 || cz >= gm.ng[2]) continue;
      }
      for (int dy = lo[1]; dy <= hi[1]; ++dy) {
        int cy = full[1] ? dy : (ix[1] + dy);
        if (!full[1]) {
          if (per[1]) cy = (cy + gm.ng[1]) % gm.ng[1];
          else if (cy < 0 || cy >= gm.ng[1]) continue;
        }
        for (int dx_i = lo[0]; dx_i <= hi[0]; ++dx_i) {
          int cx = full[0] ? dx_i : (ix[0] + dx_i);
          if (!full[0]) {
            if (per[0]) cx = (cx + gm.ng[0]) % gm.ng[0];
            else if (cx < 0 || cx >= gm.ng[0]) continue;
          }
          const int cid = (cz * gm.ng[1] + cy) * gm.ng[0] + cx;
          const int beg = goff(cid);
          const int gc = gcnt(cid);
          for (int m = 0; m < gc; ++m) {
            const int b = gelm(beg + m);
            if (b == a) continue;
            const Real xb[3] = {xv(0, b), xv(1, b), xv(2, b)};
            Real dvec[3];
            WrapDiff(dlen, per, xa, xb, dvec);
            const Real r2 = dvec[0]*dvec[0] + dvec[1]*dvec[1] + dvec[2]*dvec[2];
            if (r2 < r_cut_a2) {
              if (n_loc < kLocNgb) {
                loc_a[n_loc++] = b;
              } else {
                const int ka = Kokkos::atomic_fetch_add(&ncnt(a), 1);
                if (fill_ids && ka < cap) nids(ka, a) = b;
              }
              const Real r_cut_b = 2.0 * hv(b);
              if (r2 >= r_cut_b * r_cut_b) {
                const int kb = Kokkos::atomic_fetch_add(&ncnt(b), 1);
                if (fill_ids && kb < cap) nids(kb, b) = a;
              }
            }
          }
        }
      }
    }
    if (n_loc > 0) {
      const int base = Kokkos::atomic_fetch_add(&ncnt(a), n_loc);
      if (fill_ids) {
        for (int k = 0; k < n_loc; ++k) {
          if (base + k < cap) nids(base + k, a) = loc_a[k];
        }
      }
    }
  });

  int max_needed = 0;
  Kokkos::parallel_reduce("vlasov_ngb_sort_max", Kokkos::RangePolicy<DevExeSpace>(0, N),
  KOKKOS_LAMBDA(const int a, int &lmax) {
    if (!act(a)) {
      ncnt(a) = 0;
      return;
    }
    const int cnt = ncnt(a);
    if (cnt > lmax) lmax = cnt;
    if (fill_ids && cnt > 1 && cnt <= cap) {
      if (cnt <= 64) {
        int loc[64];
        for (int i = 0; i < cnt; ++i) loc[i] = nids(i, a);
        for (int i = 1; i < cnt; ++i) {
          const int key = loc[i];
          int j = i - 1;
          while (j >= 0 && loc[j] > key) {
            loc[j + 1] = loc[j];
            --j;
          }
          loc[j + 1] = key;
        }
        for (int i = 0; i < cnt; ++i) nids(i, a) = loc[i];
      } else {
        for (int i = 1; i < cnt; ++i) {
          const int key = nids(i, a);
          int j = i - 1;
          while (j >= 0 && nids(j, a) > key) {
            nids(j + 1, a) = nids(j, a);
            --j;
          }
          nids(j + 1, a) = key;
        }
      }
    }
  }, Kokkos::Max<int>(max_needed));
  return max_needed;
}

void UpdateGeometry(VlasovState &st, const NrpicOptions &nropt, bool build_neighbors,
                    Real cand_scale) {
  const int N = st.n_elem;
  if (N == 0) {
    st.n_edges = 0;
    return;
  }
  VlasovReduceStats rs = GatherStats(st);
  if (rs.n_act <= 1) {
    st.n_edges = 0;
    return;
  }
  if (rs.h_max <= 0.0) {
    SeedHFromNearest(st, nropt, rs);
    rs = GatherStats(st);
  }

  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3]  = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
  const bool bnd_detect = st.opt.bnd_detect;
  const Real cm_tol     = st.opt.bnd_cm_tol;
  const int  min_ngb    = st.opt.bnd_min_ngb;

  VlasovGridMeta gm = RebuildSpatialGrid(st, nropt, rs, 1.05);
  {
    auto xv = st.x;
    auto hv = st.h;
    auto Vv = st.V;
    auto Ev = st.Einv;
    auto act = st.active;
    auto bnd = st.is_bnd;
    auto goff = st.grid_off;
    auto gcnt = st.grid_cnt;
    auto gelm = st.grid_elem;

    par_for("vlasov_geom", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
      if (!act(a)) {
        Vv(a) = 0.0;
        bnd(a) = 1;
        return;
      }
      const Real xa[3] = {xv(0, a), xv(1, a), xv(2, a)};
      int ix[3], lo[3], hi[3];
      bool full[3];
      GridCellIndices(xa, gm.gmin, gm.inv_cdx, gm.ng, ix);

      Real ha = hv(a);
      if (ha <= 0.0) ha = 1.0;

      constexpr int kMaxCand = 128;
      int cand_id[kMaxCand];
      Real cand_r[kMaxCand];
      int n_cand = 0;
      bool overflow = false;
      const Real r_cand_max = 2.0 * fmax(cand_scale, 1.05) * ha;
      const Real r_cand_max2 = r_cand_max * r_cand_max;
      ComputeCellStencil(r_cand_max, gm.inv_cdx, gm.ng, lo, hi, full);

      for (int dz = lo[2]; dz <= hi[2] && !overflow; ++dz) {
        int cz = full[2] ? dz : (ix[2] + dz);
        if (!full[2]) {
          if (per[2]) cz = (cz + gm.ng[2]) % gm.ng[2];
          else if (cz < 0 || cz >= gm.ng[2]) continue;
        }
        for (int dy = lo[1]; dy <= hi[1] && !overflow; ++dy) {
          int cy = full[1] ? dy : (ix[1] + dy);
          if (!full[1]) {
            if (per[1]) cy = (cy + gm.ng[1]) % gm.ng[1];
            else if (cy < 0 || cy >= gm.ng[1]) continue;
          }
          for (int dx_i = lo[0]; dx_i <= hi[0] && !overflow; ++dx_i) {
            int cx = full[0] ? dx_i : (ix[0] + dx_i);
            if (!full[0]) {
              if (per[0]) cx = (cx + gm.ng[0]) % gm.ng[0];
              else if (cx < 0 || cx >= gm.ng[0]) continue;
            }
            const int cid = (cz * gm.ng[1] + cy) * gm.ng[0] + cx;
            const int beg = goff(cid);
            const int cnt = gcnt(cid);
            for (int m = 0; m < cnt; ++m) {
              const int c = gelm(beg + m);
              if (c == a) continue;
              const Real xc[3] = {xv(0, c), xv(1, c), xv(2, c)};
              Real dvec[3];
              WrapDiff(dlen, per, xa, xc, dvec);
              const Real r2 = dvec[0]*dvec[0] + dvec[1]*dvec[1] + dvec[2]*dvec[2];
              if (r2 < r_cand_max2) {
                if (n_cand < kMaxCand) {
                  cand_id[n_cand] = c;
                  cand_r[n_cand] = sqrt(r2);
                  ++n_cand;
                } else {
                  overflow = true;
                  break;
                }
              }
            }
          }
        }
      }

      bool fast_ok = false;
      if (!overflow && n_cand > 0) {
        Real h_lo = 1.0e-12;
        Real h_hi = 0.5 * r_cand_max;
        for (int it = 0; it < 20; ++it) {
          Real sum_w = 1.0;
          Real sum_d = 0.0;
          for (int k = 0; k < n_cand; ++k) {
            const Real r = cand_r[k];
            if (r < 2.0 * ha) {
              const Real q = r / ha;
              if (q < 1.0) {
                const Real q2 = q * q;
                sum_w += 1.0 - 1.5 * q2 + 0.75 * q2 * q;
                sum_d += 3.0 * q2 - 2.25 * q2 * q;
              } else {
                const Real t = 2.0 - q;
                sum_w += 0.25 * t * t * t;
                sum_d += 0.75 * q * t * t;
              }
            }
          }
          const Real F = sum_w - nrpic::vlasov::kPi;
          if (fabs(F) <= 1.0e-13 * nrpic::vlasov::kPi) {
            if (2.0 * ha <= r_cand_max) fast_ok = true;
            break;
          }
          if (F < 0.0) h_lo = fmax(h_lo, ha);
          else         h_hi = fmin(h_hi, ha);
          Real h_try = 0.5 * (h_lo + h_hi);
          if (sum_d > 1.0e-30) {
            const Real h_nwt = ha - F * ha / sum_d;
            if (h_nwt > h_lo && h_nwt < h_hi) h_try = h_nwt;
          }
          if (h_try > 0.999 * (0.5 * r_cand_max) && F < 0.0) break;
          if (fabs(h_try - ha) <= 1.0e-14 * ha) {
            ha = h_try;
            if (2.0 * ha <= r_cand_max) fast_ok = true;
            break;
          }
          ha = h_try;
        }
      }

      if (!fast_ok) {
        for (int it = 0; it < 45; ++it) {
          ComputeCellStencil(2.0 * ha, gm.inv_cdx, gm.ng, lo, hi, full);
          Real nbar = 1.0 / (nrpic::vlasov::kPi * ha * ha * ha);
          for (int dz = lo[2]; dz <= hi[2]; ++dz) {
            int cz = full[2] ? dz : (ix[2] + dz);
            if (!full[2]) {
              if (per[2]) cz = (cz + gm.ng[2]) % gm.ng[2];
              else if (cz < 0 || cz >= gm.ng[2]) continue;
            }
            for (int dy = lo[1]; dy <= hi[1]; ++dy) {
              int cy = full[1] ? dy : (ix[1] + dy);
              if (!full[1]) {
                if (per[1]) cy = (cy + gm.ng[1]) % gm.ng[1];
                else if (cy < 0 || cy >= gm.ng[1]) continue;
              }
              for (int dx_i = lo[0]; dx_i <= hi[0]; ++dx_i) {
                int cx = full[0] ? dx_i : (ix[0] + dx_i);
                if (!full[0]) {
                  if (per[0]) cx = (cx + gm.ng[0]) % gm.ng[0];
                  else if (cx < 0 || cx >= gm.ng[0]) continue;
                }
                const int cid = (cz * gm.ng[1] + cy) * gm.ng[0] + cx;
                const int beg = goff(cid);
                const int cnt = gcnt(cid);
                for (int m = 0; m < cnt; ++m) {
                  const int c = gelm(beg + m);
                  if (c == a) continue;
                  const Real xc[3] = {xv(0, c), xv(1, c), xv(2, c)};
                  Real dvec[3];
                  WrapDiff(dlen, per, xa, xc, dvec);
                  const Real r = sqrt(dvec[0]*dvec[0] + dvec[1]*dvec[1] + dvec[2]*dvec[2]);
                  if (r < 2.0 * ha) {
                    nbar += CubicSpline3D(r, ha);
                  }
                }
              }
            }
          }
          const Real h_new = cbrt(1.0 / fmax(nbar, 1.0e-300));
          if (fabs(h_new - ha) < 1.0e-14 * ha) {
            ha = h_new;
            break;
          }
          ha = 0.2 * ha + 0.8 * h_new;
        }
      }
      hv(a) = ha;

      Real nbar = 1.0 / (nrpic::vlasov::kPi * ha * ha * ha);
      Real E_a[3][3] = {{0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}};
      Real dx_cm[3] = {0.0, 0.0, 0.0};
      int n_ngb_h = 0;

      if (fast_ok) {
        const Real r_cut = 2.0 * ha;
        for (int k = 0; k < n_cand; ++k) {
          const Real r = cand_r[k];
          if (r < r_cut) {
            const int c = cand_id[k];
            const Real xc[3] = {xv(0, c), xv(1, c), xv(2, c)};
            Real dvec[3];
            WrapDiff(dlen, per, xa, xc, dvec);
            ++n_ngb_h;
            const Real w = CubicSpline3D(r, ha);
            nbar += w;
            for (int i = 0; i < 3; ++i) {
              dx_cm[i] += w * dvec[i];
              for (int j = 0; j < 3; ++j) {
                E_a[i][j] += w * dvec[i] * dvec[j];
              }
            }
          }
        }
      } else {
        ComputeCellStencil(2.0 * ha, gm.inv_cdx, gm.ng, lo, hi, full);
        for (int dz = lo[2]; dz <= hi[2]; ++dz) {
          int cz = full[2] ? dz : (ix[2] + dz);
          if (!full[2]) {
            if (per[2]) cz = (cz + gm.ng[2]) % gm.ng[2];
            else if (cz < 0 || cz >= gm.ng[2]) continue;
          }
          for (int dy = lo[1]; dy <= hi[1]; ++dy) {
            int cy = full[1] ? dy : (ix[1] + dy);
            if (!full[1]) {
              if (per[1]) cy = (cy + gm.ng[1]) % gm.ng[1];
              else if (cy < 0 || cy >= gm.ng[1]) continue;
            }
            for (int dx_i = lo[0]; dx_i <= hi[0]; ++dx_i) {
              int cx = full[0] ? dx_i : (ix[0] + dx_i);
              if (!full[0]) {
                if (per[0]) cx = (cx + gm.ng[0]) % gm.ng[0];
                else if (cx < 0 || cx >= gm.ng[0]) continue;
              }
              const int cid = (cz * gm.ng[1] + cy) * gm.ng[0] + cx;
              const int beg = goff(cid);
              const int cnt = gcnt(cid);
              for (int m = 0; m < cnt; ++m) {
                const int c = gelm(beg + m);
                if (c == a) continue;
                const Real xc[3] = {xv(0, c), xv(1, c), xv(2, c)};
                Real dvec[3];
                WrapDiff(dlen, per, xa, xc, dvec);
                const Real r = sqrt(dvec[0]*dvec[0] + dvec[1]*dvec[1] + dvec[2]*dvec[2]);
                if (r < 2.0 * ha) {
                  ++n_ngb_h;
                  const Real w = CubicSpline3D(r, ha);
                  nbar += w;
                  for (int i = 0; i < 3; ++i) {
                    dx_cm[i] += w * dvec[i];
                    for (int j = 0; j < 3; ++j) {
                      E_a[i][j] += w * dvec[i] * dvec[j];
                    }
                  }
                }
              }
            }
          }
        }
      }

      Vv(a) = 1.0 / fmax(nbar, 1.0e-300);
      Real Einv_mat[3][3];
      Inv3GeomReg(E_a, Einv_mat);
      Real es6[6];
      PackSym6(Einv_mat, es6);
      for (int s = 0; s < N_SYM6; ++s) Ev(s, a) = es6[s];

      if (bnd_detect) {
        const Real ncm = sqrt(dx_cm[0]*dx_cm[0] + dx_cm[1]*dx_cm[1] + dx_cm[2]*dx_cm[2])
                         / (ha * fmax(nbar, 1.0e-300));
        bnd(a) = (ncm > cm_tol || n_ngb_h < min_ngb) ? 1 : 0;
      } else {
        bnd(a) = 0;
      }
    });
  }

  if (!build_neighbors) return;

  int max_needed = FillNeighborsAndCount(st, nropt, gm, true);
  if (max_needed > st.max_ngb) {
    GrowNeighborCapacity(st, std::max(max_needed + 16, 2 * st.max_ngb));
    FillNeighborsAndCount(st, nropt, gm, true);
  }

  auto ncnt = st.ngb_cnt;
  auto nids = st.ngb_ids;
  auto eoff = st.edge_off;
  int tot_edges = 0;
  Kokkos::parallel_scan("vlasov_edge_scan", Kokkos::RangePolicy<DevExeSpace>(0, N),
  KOKKOS_LAMBDA(const int a, int &upd, const bool final) {
    int c_hi = 0;
    const int cnt = ncnt(a);
    for (int k = 0; k < cnt; ++k) {
      if (nids(k, a) > a) ++c_hi;
    }
    if (final) eoff(a) = upd;
    upd += c_hi;
  }, tot_edges);

  st.n_edges = tot_edges;
  if (tot_edges > st.edge_cap) {
    st.edge_cap = std::max(tot_edges + 256, 2 * st.edge_cap);
    Kokkos::realloc(st.edge_a, st.edge_cap);
    Kokkos::realloc(st.edge_b, st.edge_cap);
  }
  if (tot_edges > 0) {
    auto ea = st.edge_a;
    auto eb = st.edge_b;
    par_for("vlasov_edge_fill", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
      const int cnt = ncnt(a);
      int pos = eoff(a);
      for (int k = 0; k < cnt; ++k) {
        const int b = nids(k, a);
        if (b > a) {
          ea(pos) = a;
          eb(pos) = b;
          ++pos;
        }
      }
    });
  }
}

void ConsToPrim(VlasovState &st) {
  const int N = st.n_elem;
  const int Nb = st.n_basis;
  if (N == 0) return;
  auto act   = st.active;
  auto mv    = st.m;
  auto Pv    = st.P;
  auto Piv   = st.Pi;
  auto Vv    = st.V;
  auto Dv    = st.D;
  auto uv    = st.u_bar;
  auto Sv    = st.Sigma;

  par_for("vlasov_c2p", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    if (!act(a)) {
      for (int al = 0; al < Nb; ++al) {
        Dv(al, a) = 0.0;
        for (int i = 0; i < 3; ++i) uv(al, i, a) = 0.0;
        for (int s = 0; s < N_SYM6; ++s) Sv(al, s, a) = 0.0;
      }
      return;
    }
    Real ml[nrpic::vlasov::MAX_BASIS];
    Real Pl[nrpic::vlasov::MAX_BASIS][3];
    Real Pil[nrpic::vlasov::MAX_BASIS][3][3];
    for (int al = 0; al < Nb; ++al) {
      ml[al] = mv(al, a);
      for (int i = 0; i < 3; ++i) Pl[al][i] = Pv(al, i, a);
      Real s6[N_SYM6];
      for (int s = 0; s < N_SYM6; ++s) s6[s] = Piv(al, s, a);
      UnpackSym6(s6, Pil[al]);
    }
    nrpic::vlasov::RealizabilityRepairCell(Nb, ml, Pl, Pil);

    const Real Va = fmax(Vv(a), 1.0e-300);
    for (int al = 0; al < Nb; ++al) {
      mv(al, a) = ml[al];
      for (int i = 0; i < 3; ++i) Pv(al, i, a) = Pl[al][i];
      Real pi_s[N_SYM6];
      PackSym6(Pil[al], pi_s);
      for (int s = 0; s < N_SYM6; ++s) Piv(al, s, a) = pi_s[s];

      Dv(al, a) = ml[al] / Va;
      const Real m_safe = fmax(ml[al], 1.0e-300);
      Real u_a[3];
      for (int i = 0; i < 3; ++i) {
        u_a[i] = Pl[al][i] / m_safe;
        uv(al, i, a) = u_a[i];
      }
      Real sig[3][3];
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
          sig[i][j] = Pil[al][i][j] / m_safe - u_a[i] * u_a[j];
        }
      }
      Real sig6[N_SYM6];
      PackSym6(sig, sig6);
      for (int s = 0; s < N_SYM6; ++s) Sv(al, s, a) = sig6[s];
    }
  });
}

}  // namespace nrpic_vlasov_detail
}  // namespace particles

