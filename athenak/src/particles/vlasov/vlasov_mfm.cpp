//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_mfm.cpp
//! \brief Asymptotic-preserving MFM finite-volume Vlasov solver (SSP-RK2 advection,
//! tiered MLS gradients, HLLC+Noh shock capture, Maxwell-Juttner BGK, geodesic kick,
//! and excision).

#include <algorithm>
#include <cmath>
#include <utility>

#include "athena.hpp"
#include "coordinates/adm.hpp"
#include "mesh/mesh.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_metrics.hpp"
#include "particles/nrpic_mesh.hpp"
#include "particles/vlasov/vlasov_types.hpp"
#include "z4c/tmunu.hpp"
#include "z4c/z4c.hpp"
// last: this header defines the macro NDIM, which collides with a member of Tmunu
#include "z4c/fastflow.hpp"

namespace particles {
namespace nrpic_vlasov_detail {

namespace {

template <int MaxNb>
void ComputeGradientsImpl(VlasovState &st, const NrpicOptions &nropt) {
  const int N = st.n_elem;
  const int Nb = st.n_basis;
  if (N == 0) return;

  {
    const int *act = ContigPtr(st.active);
    const Real *mv = ContigPtr(st.m);
    const Real *Pv = ContigPtr(st.P);
    Real *ubv      = ContigPtr(st.u_bulk);
    Real *gDv      = ContigPtr(st.grad_D);
    Real *guv      = ContigPtr(st.grad_u);
    Real *gSv      = ContigPtr(st.grad_S);
    par_for("vlasov_grad", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
      const size_t nsz = static_cast<size_t>(N);
      if (!act[a]) {
        for (int i = 0; i < 3; ++i) ubv[static_cast<size_t>(i) * nsz + a] = 0.0;
        for (int al = 0; al < Nb; ++al) {
          for (int k = 0; k < 3; ++k) gDv[(static_cast<size_t>(al) * 3 + k) * nsz + a] = 0.0;
          for (int i = 0; i < 3; ++i) {
            for (int k = 0; k < 3; ++k) guv[((static_cast<size_t>(al) * 3 + i) * 3 + k) * nsz + a] = 0.0;
          }
          for (int s = 0; s < N_SYM6; ++s) {
            for (int k = 0; k < 3; ++k) gSv[((static_cast<size_t>(al) * N_SYM6 + s) * 3 + k) * nsz + a] = 0.0;
          }
        }
        return;
      }
      Real mt = 0.0, Pt[3] = {0.0, 0.0, 0.0};
      for (int al = 0; al < Nb; ++al) {
        mt += mv[static_cast<size_t>(al) * nsz + a];
        for (int i = 0; i < 3; ++i) Pt[i] += Pv[(static_cast<size_t>(al) * 3 + i) * nsz + a];
      }
      const Real mt_s = fmax(mt, 1.0e-300);
      for (int i = 0; i < 3; ++i) ubv[static_cast<size_t>(i) * nsz + a] = Pt[i] / mt_s;
    });
  }

  VlasovGradPtrs p;
  p.act   = ContigPtr(st.active);
  p.bnd   = ContigPtr(st.is_bnd);
  p.ncnt  = ContigPtr(st.ngb_cnt);
  p.nids  = ContigPtr(st.ngb_ids);
  p.pcnt  = ContigPtr(st.prev_cnt);
  p.pids  = ContigPtr(st.prev_ids);
  p.ppab  = ContigPtr(st.prev_pab);
  p.x     = ContigPtr(st.x);
  p.h     = ContigPtr(st.h);
  p.Einv  = ContigPtr(st.Einv);
  p.ub    = ContigPtr(st.u_bulk);
  p.D     = ContigPtr(st.D);
  p.u     = ContigPtr(st.u_bar);
  p.S     = ContigPtr(st.Sigma);
  p.gD    = ContigPtr(st.grad_D);
  p.gu    = ContigPtr(st.grad_u);
  p.gS    = ContigPtr(st.grad_S);
  for (int d = 0; d < 3; ++d) {
    p.dlen[d] = nropt.dom_len[d];
    p.per[d]  = nropt.periodic[d];
  }
  p.eps_v = (st.opt.coll_sigma > 0.0) ? 0.0 : st.opt.lim_eps_v;
  p.N     = N;
  p.Nb    = Nb;

  par_for("vlasov_mls", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    const size_t nsz = static_cast<size_t>(p.N);
    const int nb = (MaxNb < p.Nb) ? MaxNb : p.Nb;
    const int cnt = p.ncnt[a];
    const bool is_b = (p.bnd[a] == 1);
    if (!p.act[a] || cnt == 0 || (is_b && cnt < 4)) {
      for (int al = 0; al < nb; ++al) {
        for (int k = 0; k < 3; ++k) p.gD[(static_cast<size_t>(al) * 3 + k) * nsz + a] = 0.0;
        for (int i = 0; i < 3; ++i) {
          for (int k = 0; k < 3; ++k) p.gu[((static_cast<size_t>(al) * 3 + i) * 3 + k) * nsz + a] = 0.0;
        }
        for (int s = 0; s < N_SYM6; ++s) {
          for (int k = 0; k < 3; ++k) p.gS[((static_cast<size_t>(al) * N_SYM6 + s) * 3 + k) * nsz + a] = 0.0;
        }
      }
      return;
    }

    const Real xa[3] = {p.x[a], p.x[nsz + a], p.x[2 * nsz + a]};
    const Real ha = p.h[a];
    Real Einv_a[3][3], es6[N_SYM6];
    for (int s = 0; s < N_SYM6; ++s) es6[s] = p.Einv[static_cast<size_t>(s) * nsz + a];
    UnpackSym6(es6, Einv_a);
    const int pc = (MaxNb > 1) ? p.pcnt[a] : 0;
    constexpr int kKpCache = 96;
    int kp_cache[(MaxNb > 1) ? kKpCache : 1];
    if constexpr (MaxNb > 1) {
      if (pc > 0) {
        for (int idx_n = 0; idx_n < cnt && idx_n < kKpCache; ++idx_n) {
          kp_cache[idx_n] = BinaryFindSortedPtr(
              p.pids, a, p.N, pc, p.nids[static_cast<size_t>(idx_n) * nsz + a]);
        }
      }
    }

    for (int al = 0; al < nb; ++al) {
      Real dD_raw[3] = {0.0, 0.0, 0.0};
      Real du_raw[3][3] = {{0.0}};
      Real dS_raw[N_SYM6][3] = {{0.0}};

      const Real Da0 = p.D[static_cast<size_t>(al) * nsz + a];
      Real ua0[3], Sa0[N_SYM6];
      for (int i = 0; i < 3; ++i) ua0[i] = p.u[(static_cast<size_t>(al) * 3 + i) * nsz + a];
      for (int s = 0; s < N_SYM6; ++s) Sa0[s] = p.S[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a];

      Real d_min = Da0, d_max = Da0;
      Real u_min[3] = {ua0[0], ua0[1], ua0[2]};
      Real u_max[3] = {ua0[0], ua0[1], ua0[2]};
      Real S_min[N_SYM6], S_max[N_SYM6];
      for (int s = 0; s < N_SYM6; ++s) S_min[s] = S_max[s] = Sa0[s];

      for (int idx_n = 0; idx_n < cnt; ++idx_n) {
        const int b = p.nids[static_cast<size_t>(idx_n) * nsz + a];
        int be = al;
        if constexpr (MaxNb > 1) {
          if (pc > 0) {
            const int kp = (idx_n < kKpCache)
                           ? kp_cache[idx_n]
                           : BinaryFindSortedPtr(p.pids, a, p.N, pc, b);
            if (kp >= 0) be = p.ppab[static_cast<size_t>(kp * nb + al) * nsz + a];
            if (be < 0 || be >= nb) be = al;
          }
        }

        const Real xb[3] = {p.x[b], p.x[nsz + b], p.x[2 * nsz + b]};
        Real dvec[3];
        WrapDiff(p.dlen, p.per, xa, xb, dvec);
        const Real r = sqrt(dvec[0]*dvec[0] + dvec[1]*dvec[1] + dvec[2]*dvec[2]);
        const Real w = CubicSpline3D(r, ha);

        Real vec[3] = {0.0, 0.0, 0.0};
        for (int i = 0; i < 3; ++i) {
          for (int j = 0; j < 3; ++j) vec[i] += Einv_a[i][j] * dvec[j] * w;
        }

        const Real Db = p.D[static_cast<size_t>(be) * nsz + b];
        if (Db < d_min) d_min = Db;
        if (Db > d_max) d_max = Db;
        const Real dD = Db - Da0;
        for (int k = 0; k < 3; ++k) dD_raw[k] += dD * vec[k];

        for (int i = 0; i < 3; ++i) {
          const Real ubc = p.u[(static_cast<size_t>(be) * 3 + i) * nsz + b];
          if (ubc < u_min[i]) u_min[i] = ubc;
          if (ubc > u_max[i]) u_max[i] = ubc;
          const Real du = ubc - ua0[i];
          for (int k = 0; k < 3; ++k) du_raw[i][k] += du * vec[k];
        }
        for (int s = 0; s < N_SYM6; ++s) {
          const Real Sbc = p.S[(static_cast<size_t>(be) * N_SYM6 + s) * nsz + b];
          if (Sbc < S_min[s]) S_min[s] = Sbc;
          if (Sbc > S_max[s]) S_max[s] = Sbc;
          const Real dS = Sbc - Sa0[s];
          for (int k = 0; k < 3; ++k) dS_raw[s][k] += dS * vec[k];
        }
      }

      Real dS_norm = 0.0;
      for (int s = 0; s < N_SYM6; ++s) {
        for (int k = 0; k < 3; ++k) dS_norm += fabs(dS_raw[s][k]);
      }
      Real S0_mat[3][3] = {{0.0}};
      if (dS_norm > 0.0) UnpackSym6(Sa0, S0_mat);

      Real phi_D = 1.0;
      Real phi_v[3] = {1.0, 1.0, 1.0};
      Real phi_S = 1.0;
      const Real d_lo = d_min - Da0, d_hi = d_max - Da0;
      const int diag_idx[3] = {SYM_XX, SYM_YY, SYM_ZZ};
      const Real sig_a[3] = {
        sqrt(fmax(Sa0[SYM_XX], 0.0)),
        sqrt(fmax(Sa0[SYM_YY], 0.0)),
        sqrt(fmax(Sa0[SYM_ZZ], 0.0))
      };
      const Real u_lo[3] = {u_min[0] - ua0[0], u_min[1] - ua0[1], u_min[2] - ua0[2]};
      const Real u_hi[3] = {u_max[0] - ua0[0], u_max[1] - ua0[1], u_max[2] - ua0[2]};
      Real s_lo[N_SYM6], s_hi[N_SYM6];
      for (int s = 0; s < N_SYM6; ++s) {
        s_lo[s] = S_min[s] - Sa0[s];
        s_hi[s] = S_max[s] - Sa0[s];
      }

      for (int idx_n = 0; idx_n < cnt; ++idx_n) {
        const int b = p.nids[static_cast<size_t>(idx_n) * nsz + a];
        int be = al;
        if constexpr (MaxNb > 1) {
          if (p.eps_v > 0.0 && pc > 0) {
            const int kp = (idx_n < kKpCache)
                           ? kp_cache[idx_n]
                           : BinaryFindSortedPtr(p.pids, a, p.N, pc, b);
            if (kp >= 0) be = p.ppab[static_cast<size_t>(kp * nb + al) * nsz + a];
            if (be < 0 || be >= nb) be = al;
          }
        }
        const Real xb[3] = {p.x[b], p.x[nsz + b], p.x[2 * nsz + b]};
        Real dvec[3];
        WrapDiff(p.dlen, p.per, xa, xb, dvec);
        const Real hb = p.h[b];
        const Real psi = hb / (ha + hb);
        const Real xf[3] = {psi*dvec[0], psi*dvec[1], psi*dvec[2]};

        if (!is_b) {
          const Real dval = nrpic::vlasov::Dot3(dD_raw, xf);
          if (dval > 1.0e-300)       phi_D = fmin(phi_D, d_hi / dval);
          else if (dval < -1.0e-300) phi_D = fmin(phi_D, d_lo / dval);
        }

        for (int ic = 0; ic < 3; ++ic) {
          bool do_lim = (p.eps_v <= 0.0);
          if (!do_lim) {
            const Real sig_b = sqrt(fmax(p.S[(static_cast<size_t>(be) * N_SYM6 + diag_idx[ic]) * nsz + b], 0.0));
            const Real sc = fmax(fabs(ua0[ic] - p.ub[static_cast<size_t>(ic) * nsz + a]),
                            fmax(sig_a[ic],
                            fmax(fabs(p.u[(static_cast<size_t>(be) * 3 + ic) * nsz + b] - p.ub[static_cast<size_t>(ic) * nsz + b]),
                            fmax(sig_b, 1.0e-12))));
            const Real dv_full = fabs(nrpic::vlasov::Dot3(du_raw[ic], dvec));
            do_lim = (dv_full >= p.eps_v * sc);
          }
          if (do_lim) {
            const Real dval = nrpic::vlasov::Dot3(du_raw[ic], xf);
            if (dval > 1.0e-300)       phi_v[ic] = fmin(phi_v[ic], u_hi[ic] / dval);
            else if (dval < -1.0e-300) phi_v[ic] = fmin(phi_v[ic], u_lo[ic] / dval);
          }
        }

        for (int s = 0; s < N_SYM6; ++s) {
          const Real dval = nrpic::vlasov::Dot3(dS_raw[s], xf);
          if (dval > 1.0e-300)       phi_S = fmin(phi_S, s_hi[s] / dval);
          else if (dval < -1.0e-300) phi_S = fmin(phi_S, s_lo[s] / dval);
        }
        if (phi_S < 0.0) phi_S = 0.0;

        if (phi_S > 0.0 && dS_norm > 0.0) {
          Real dS_xf6[N_SYM6];
          for (int s = 0; s < N_SYM6; ++s) {
            dS_xf6[s] = dS_raw[s][0]*xf[0] + dS_raw[s][1]*xf[1] + dS_raw[s][2]*xf[2];
          }
          Real dS_mat[3][3];
          UnpackSym6(dS_xf6, dS_mat);
          Real cand[3][3];
          for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) cand[i][j] = S0_mat[i][j] + phi_S * dS_mat[i][j];
          }
          if (!nrpic::vlasov::IsSpd3Fast(cand, 0.0)) {
            if (SymMinEig3(S0_mat, dS_mat, phi_S) < 0.0) {
              Real lo = 0.0, hi = phi_S;
              for (int it = 0; it < 16; ++it) {
                const Real mid = 0.5 * (lo + hi);
                if (SymMinEig3(S0_mat, dS_mat, mid) >= 0.0) lo = mid;
                else hi = mid;
              }
              phi_S = lo;
            }
          }
        }
      }

      phi_D = fmax(0.0, fmin(1.0, phi_D));
      for (int k = 0; k < 3; ++k) {
        p.gD[(static_cast<size_t>(al) * 3 + k) * nsz + a] = is_b ? 0.0 : (phi_D * dD_raw[k]);
      }
      for (int ic = 0; ic < 3; ++ic) {
        phi_v[ic] = fmax(0.0, fmin(1.0, phi_v[ic]));
        for (int k = 0; k < 3; ++k) {
          p.gu[((static_cast<size_t>(al) * 3 + ic) * 3 + k) * nsz + a] = phi_v[ic] * du_raw[ic][k];
        }
      }
      phi_S = fmax(0.0, fmin(1.0, phi_S));
      for (int s = 0; s < N_SYM6; ++s) {
        for (int k = 0; k < 3; ++k) {
          p.gS[((static_cast<size_t>(al) * N_SYM6 + s) * 3 + k) * nsz + a] = phi_S * dS_raw[s][k];
        }
      }
    }
  });
}

// Tier-specialized MLS gradients matching ComputeEdgeFluxes (<1>, <2>, <4>, <MAX_BASIS>)
void ComputeGradients(VlasovState &st, const NrpicOptions &nropt) {
  const int Nb = st.n_basis;
  if (Nb <= 1)      ComputeGradientsImpl<1>(st, nropt);
  else if (Nb <= 2) ComputeGradientsImpl<2>(st, nropt);
  else if (Nb <= 4) ComputeGradientsImpl<4>(st, nropt);
  else              ComputeGradientsImpl<nrpic::vlasov::MAX_BASIS>(st, nropt);
}

inline int ResolveMetricKind(const VlasovState &st, const NrpicOptions &nropt) {
  if (st.opt.metric_is_minkowski) return 0;
  if (nropt.metric == NrpicMetric::kerr_schild) return 1;
  return 2;
}

template <int MetricKind, class LightOrFullMetT>
void ComputeCellVelocitiesImpl(VlasovState &st, const LightOrFullMetT &met, int slot_mode) {
  const int N = st.n_elem;
  const int Nb = st.n_basis;
  if (N == 0) return;
  const int *act = ContigPtr(st.active);
  const int *gid = ContigPtr(st.blk_gid);
  const Real *xv = ContigPtr(st.x);
  const Real *mv = ContigPtr(st.m);
  const Real *uv = ContigPtr(st.u_bar);
  const Real *Sv = ContigPtr(st.Sigma);
  Real *vc       = ContigPtr(st.v_cell);
  const int n_q  = st.opt.n_q_dep;

  par_for("vlasov_vcell", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    (void)met; (void)gid; (void)slot_mode;
    const size_t nsz = static_cast<size_t>(N);
    if (!act[a]) {
      vc[a] = vc[nsz + a] = vc[2 * nsz + a] = 0.0;
      return;
    }
    const Real pos[3] = {xv[a], xv[nsz + a], xv[2 * nsz + a]};
    Real alp = 1.0;
    Real beta[3] = {0.0, 0.0, 0.0};
    Real gi[3][3] = {{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}};
    if constexpr (MetricKind == 1) {
      Real g[3][3];
      met.EvalNoDeriv(pos, alp, beta, g);
      nrpic::Inv3Sym(g, gi);
    } else if constexpr (MetricKind == 2) {
      nrpic::AdmPoint adm;
      met(slot_mode, pos, gid[a], adm);
      alp = adm.alp;
      for (int i = 0; i < 3; ++i) beta[i] = adm.beta[i];
      nrpic::Inv3Sym(adm.g, gi);
    }

    Real tot_m = 0.0;
    Real vsum[3] = {0.0, 0.0, 0.0};
    for (int al = 0; al < Nb; ++al) {
      const Real ma = mv[static_cast<size_t>(al) * nsz + a];
      tot_m += ma;
      if (ma <= 0.0) continue;
      Real ua[3], s6[N_SYM6], Sa[3][3];
      for (int i = 0; i < 3; ++i) ua[i] = uv[(static_cast<size_t>(al) * 3 + i) * nsz + a];
      for (int s = 0; s < N_SYM6; ++s) s6[s] = Sv[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a];
      UnpackSym6(s6, Sa);

      Real pts[27][3], w[27];
      int n_pts = 0;
      nrpic::vlasov::BasisCubaturePoints(ua, Sa, n_q, pts, w, n_pts);
      for (int q = 0; q < n_pts; ++q) {
        Real uup[3] = {0.0, 0.0, 0.0};
        for (int i = 0; i < 3; ++i) {
          for (int j = 0; j < 3; ++j) uup[i] += gi[i][j] * pts[q][j];
        }
        const Real W = sqrt(1.0 + nrpic::vlasov::Dot3(pts[q], uup));
        for (int i = 0; i < 3; ++i) {
          vsum[i] += ma * w[q] * (alp * uup[i] / W - beta[i]);
        }
      }
    }
    const Real tm_s = fmax(tot_m, 1.0e-300);
    for (int i = 0; i < 3; ++i) vc[static_cast<size_t>(i) * nsz + a] = vsum[i] / tm_s;
  });
}

template <class SizeViewT>
void ComputeCellVelocities(VlasovState &st, const NrpicOptions &nropt,
                           const VlasovMetric<SizeViewT> &met, int slot_mode) {
  const int mk = ResolveMetricKind(st, nropt);
  if (mk == 0)      ComputeCellVelocitiesImpl<0>(st, KerrSchildLight{0.0, 0.0}, slot_mode);
  else if (mk == 1) ComputeCellVelocitiesImpl<1>(st, KerrSchildLight{met.mass, met.spin}, slot_mode);
  else              ComputeCellVelocitiesImpl<2>(st, met, slot_mode);
}

template <int MaxNb, int MetricKind, class LightOrFullMetT>
void PrecomputeCellNohFluidImpl(VlasovState &st, const LightOrFullMetT &met, int slot_mode) {
  const int N = st.n_elem;
  const int Nb = st.n_basis;
  if (N == 0) return;
  if (static_cast<int>(st.cell_noh.extent(1)) < N) {
    Kokkos::realloc(st.cell_noh, 8, N);
  }
  const int *act = ContigPtr(st.active);
  const int *gid = ContigPtr(st.blk_gid);
  const Real *xv = ContigPtr(st.x);
  const Real *Dv = ContigPtr(st.D);
  const Real *uv = ContigPtr(st.u_bar);
  const Real *Sv = ContigPtr(st.Sigma);
  Real *cn       = ContigPtr(st.cell_noh);

  par_for("vlasov_cell_noh", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    (void)met; (void)xv; (void)gid; (void)slot_mode;
    const size_t nsz = static_cast<size_t>(N);
    if (!act[a]) {
      cn[a] = -1.0;
      return;
    }
    Real L_g[3][3]  = {{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}};
    Real Li_g[3][3] = {{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}};
    if constexpr (MetricKind == 1) {
      const Real pos[3] = {xv[a], xv[nsz + a], xv[2 * nsz + a]};
      Real alp_tmp, b_tmp[3], g[3][3];
      met.EvalNoDeriv(pos, alp_tmp, b_tmp, g);
      nrpic::Chol3(g, L_g, Li_g);
    } else if constexpr (MetricKind == 2) {
      const Real pos[3] = {xv[a], xv[nsz + a], xv[2 * nsz + a]};
      nrpic::AdmPoint adm;
      met(slot_mode, pos, gid[a], adm);
      nrpic::Chol3(adm.g, L_g, Li_g);
    }

    Real D_arr[MaxNb], u_tet[MaxNb][3], S_tet[MaxNb][3][3];
    for (int al = 0; al < Nb; ++al) {
      const Real Da = Dv[static_cast<size_t>(al) * nsz + a];
      D_arr[al] = Da;
      Real uc[3], s6[N_SYM6], Sc[3][3];
      for (int i = 0; i < 3; ++i) {
        uc[i] = uv[(static_cast<size_t>(al) * 3 + i) * nsz + a];
      }
      for (int s = 0; s < N_SYM6; ++s) s6[s] = Sv[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a];
      UnpackSym6(s6, Sc);
      if constexpr (MetricKind == 0) {
        for (int i = 0; i < 3; ++i) {
          u_tet[al][i] = uc[i];
          for (int j = 0; j < 3; ++j) S_tet[al][i][j] = Sc[i][j];
        }
      } else {
        for (int m = 0; m < 3; ++m) {
          Real us = 0.0;
          for (int i = 0; i < 3; ++i) us += Li_g[m][i] * uc[i];
          u_tet[al][m] = us;
          for (int n = 0; n < 3; ++n) {
            Real ss = 0.0;
            for (int i = 0; i < 3; ++i) {
              for (int j = 0; j < 3; ++j) ss += Li_g[m][i] * Sc[i][j] * Li_g[n][j];
            }
            S_tet[al][m][n] = ss;
          }
        }
      }
    }
    const nrpic::vlasov::HllcFluidState st_c =
        nrpic::vlasov::BuildHllcCellFluid(Nb, D_arr, u_tet, S_tet);
    if (!st_c.valid) {
      cn[a] = -1.0;
      return;
    }
    cn[0 * nsz + a] = st_c.D;
    cn[1 * nsz + a] = st_c.rho0;
    cn[2 * nsz + a] = st_c.p;
    cn[3 * nsz + a] = st_c.cs2;
    cn[4 * nsz + a] = st_c.w_m;
    if constexpr (MetricKind == 0) {
      cn[5 * nsz + a] = st_c.v[0];
      cn[6 * nsz + a] = st_c.v[1];
      cn[7 * nsz + a] = st_c.v[2];
    } else {
      for (int i = 0; i < 3; ++i) {
        cn[(5 + i) * nsz + a] = L_g[i][0] * st_c.v[0]
                              + L_g[i][1] * st_c.v[1]
                              + L_g[i][2] * st_c.v[2];
      }
    }
  });
}

template <bool Collisional, int MaxNb, int MetricKind, class LightOrFullMetT>
void ComputeEdgeFluxesImpl(VlasovState &st, const NrpicOptions &nropt,
                           const LightOrFullMetT &met, int slot_mode) {
  const int Nb = st.n_basis;
  const int N_e = st.n_elem;
  {
    Real *dm_v  = ContigPtr(st.dm);
    Real *dP_v  = ContigPtr(st.dP);
    Real *dPi_v = ContigPtr(st.dPi);
    Real *dE_v  = ContigPtr(st.dE);
    const int *ncnt = (MaxNb > 1) ? ContigPtr(st.ngb_cnt) : nullptr;
    int *npab       = (MaxNb > 1) ? ContigPtr(st.new_pab) : nullptr;
    par_for("vlasov_zero_pab", DevExeSpace(), 0, N_e - 1, KOKKOS_LAMBDA(const int a) {
      (void)ncnt; (void)npab;
      const size_t nsz = static_cast<size_t>(N_e);
      dE_v[a] = 0.0;
      for (int al = 0; al < Nb; ++al) {
        dm_v[static_cast<size_t>(al) * nsz + a] = 0.0;
        for (int i = 0; i < 3; ++i) dP_v[(static_cast<size_t>(al) * 3 + i) * nsz + a] = 0.0;
        for (int s = 0; s < N_SYM6; ++s) dPi_v[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a] = 0.0;
      }
      if constexpr (MaxNb > 1) {
        const int cnt = ncnt[a];
        for (int k = 0; k < cnt; ++k) {
          for (int al = 0; al < Nb; ++al) npab[static_cast<size_t>(k * Nb + al) * nsz + a] = al;
        }
      }
    });
  }
  if (st.n_edges == 0) return;

  if (Collisional && st.opt.noh_kappa > 0.0) {
    PrecomputeCellNohFluidImpl<MaxNb, MetricKind>(st, met, slot_mode);
  }

  VlasovDomain dom;
  for (int d = 0; d < 3; ++d) {
    dom.dmin[d] = nropt.dom_min[d];
    dom.dlen[d] = nropt.dom_len[d];
    dom.per[d]  = nropt.periodic[d];
  }

  VlasovFluxPtrs p;
  p.ea         = ContigPtr(st.edge_a);
  p.eb         = ContigPtr(st.edge_b);
  p.act        = ContigPtr(st.active);
  p.gid        = (MetricKind == 2) ? ContigPtr(st.blk_gid) : nullptr;
  p.ncnt       = (MaxNb > 1) ? ContigPtr(st.ngb_cnt) : nullptr;
  p.nids       = (MaxNb > 1) ? ContigPtr(st.ngb_ids) : nullptr;
  p.npab       = (MaxNb > 1) ? ContigPtr(st.new_pab) : nullptr;
  p.x          = ContigPtr(st.x);
  p.h          = ContigPtr(st.h);
  p.V          = ContigPtr(st.V);
  p.Einv       = ContigPtr(st.Einv);
  p.m          = Collisional ? ContigPtr(st.m) : nullptr;
  p.D          = ContigPtr(st.D);
  p.u          = ContigPtr(st.u_bar);
  p.S          = ContigPtr(st.Sigma);
  p.gD         = ContigPtr(st.grad_D);
  p.gu         = ContigPtr(st.grad_u);
  p.gS         = ContigPtr(st.grad_S);
  p.cnv        = (Collisional && st.opt.noh_kappa > 0.0) ? ContigPtr(st.cell_noh) : nullptr;
  p.dm         = ContigPtr(st.dm);
  p.dP         = ContigPtr(st.dP);
  p.dPi        = ContigPtr(st.dPi);
  p.dE         = ContigPtr(st.dE);
  p.coll_sigma = st.opt.coll_sigma;
  p.noh_kappa  = st.opt.noh_kappa;
  p.N          = N_e;
  p.Nb         = Nb;
  p.basis_kind = st.opt.basis_kind;
  p.n_perp     = st.opt.n_perp;
  p.pair_mode  = st.opt.pair_mode;
  p.analytic_v = st.opt.use_analytic_vf;

  par_for("vlasov_flux", DevExeSpace(), 0, st.n_edges - 1, KOKKOS_LAMBDA(const int e) {
    (void)met; (void)dom; (void)slot_mode;
    const size_t nsz = static_cast<size_t>(p.N);
    const int nb = p.Nb;
    const int a = p.ea[e];
    const int b = p.eb[e];
    if (!p.act[a] || !p.act[b]) return;

    const Real xa[3] = {p.x[a], p.x[nsz + a], p.x[2 * nsz + a]};
    const Real xb[3] = {p.x[b], p.x[nsz + b], p.x[2 * nsz + b]};
    Real dx_ba[3];
    WrapDiff(dom.dlen, dom.per, xa, xb, dx_ba);
    const Real r_ab = sqrt(dx_ba[0]*dx_ba[0] + dx_ba[1]*dx_ba[1] + dx_ba[2]*dx_ba[2]);
    const Real ha = p.h[a], hb = p.h[b];
    if (r_ab >= 2.0 * fmax(ha, hb)) return;

    const Real Wa = CubicSpline3D(r_ab, ha);
    const Real Wb = CubicSpline3D(r_ab, hb);
    Real Eia[3][3], Eib[3][3], s6a[N_SYM6], s6b[N_SYM6];
    for (int s = 0; s < N_SYM6; ++s) {
      s6a[s] = p.Einv[static_cast<size_t>(s) * nsz + a];
      s6b[s] = p.Einv[static_cast<size_t>(s) * nsz + b];
    }
    UnpackSym6(s6a, Eia);
    UnpackSym6(s6b, Eib);

    Real A_cov[3] = {0.0, 0.0, 0.0};
    const Real Va = p.V[a], Vb = p.V[b];
    for (int i = 0; i < 3; ++i) {
      Real va = 0.0, vb = 0.0;
      for (int j = 0; j < 3; ++j) {
        va += Eia[i][j] * dx_ba[j];
        vb += Eib[i][j] * dx_ba[j];
      }
      A_cov[i] = Va * va * Wa + Vb * vb * Wb;
    }

    const Real psi = hb / (ha + hb);
    const Real xf_a[3] = {psi * dx_ba[0], psi * dx_ba[1], psi * dx_ba[2]};
    const Real xf_b[3] = {(psi - 1.0) * dx_ba[0], (psi - 1.0) * dx_ba[1], (psi - 1.0) * dx_ba[2]};

    Real x_f[3] = {xa[0] + xf_a[0], xa[1] + xf_a[1], xa[2] + xf_a[2]};
    WrapPos(dom.dmin, dom.dlen, dom.per, x_f);

    Real alp_f = 1.0;
    Real g_f[3][3] = {{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}};
    if constexpr (MetricKind == 1) {
      Real b_tmp[3];
      met.EvalNoDeriv(x_f, alp_f, b_tmp, g_f);
    } else if constexpr (MetricKind == 2) {
      nrpic::AdmPoint adm_f;
      met(slot_mode, x_f, p.gid[a], adm_f);
      alp_f = adm_f.alp;
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) g_f[i][j] = adm_f.g[i][j];
    }

    Real normA = 0.0, e_up[3][3], e_dn[3][3];
    if (!nrpic::vlasov::FaceTriad(g_f, A_cov, normA, e_up, e_dn) || normA <= 1.0e-30) {
      return;
    }

    Real Da[MaxNb], Db[MaxNb];
    Real ua_t[MaxNb][3], ub_t[MaxNb][3];
    Real Sa_t[MaxNb][3][3], Sb_t[MaxNb][3][3];

    ReconstructFaceSidePtr<MaxNb>(a, nb, p.N, xf_a, e_up, p.D, p.u, p.S, p.gD, p.gu, p.gS, Da, ua_t, Sa_t);
    ReconstructFaceSidePtr<MaxNb>(b, nb, p.N, xf_b, e_up, p.D, p.u, p.S, p.gD, p.gu, p.gS, Db, ub_t, Sb_t);

    Real wc = 1.0;
    if constexpr (Collisional) {
      Real D_sum = 0.0;
      for (int al = 0; al < nb; ++al) D_sum += Da[al] + Db[al];
      const Real D_mean = 0.5 * D_sum;
      Real detg = 1.0;
      Real dx_prop2 = dx_ba[0]*dx_ba[0] + dx_ba[1]*dx_ba[1] + dx_ba[2]*dx_ba[2];
      if constexpr (MetricKind != 0) {
        detg = adm::SpatialDet(g_f[0][0], g_f[0][1], g_f[0][2],
                               g_f[1][1], g_f[1][2], g_f[2][2]);
        dx_prop2 = nrpic::vlasov::MatVecDot3(dx_ba, g_f, dx_ba);
      }
      const Real sqrt_g = sqrt(fmax(detg, 1.0e-30));
      const Real dx_prop = sqrt(fmax(dx_prop2, 0.0));
      wc = exp(-dx_prop * (D_mean / sqrt_g) * p.coll_sigma);
    }

    Real beta_F = 0.0;
    if (p.analytic_v) {
      const Real g_eye[3][3] = {{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}};
      Real Ea_tot = 0.0, Pa0 = 0.0;
      for (int al = 0; al < nb; ++al) {
        Real e1, p1[3], s1[3][3];
        nrpic::vlasov::BasisStressEnergy(Da[al], ua_t[al], Sa_t[al], g_eye, 3, e1, p1, s1);
        Ea_tot += e1; Pa0 += p1[0];
        nrpic::vlasov::BasisStressEnergy(Db[al], ub_t[al], Sb_t[al], g_eye, 3, e1, p1, s1);
        Ea_tot += e1; Pa0 += p1[0];
      }
      beta_F = Pa0 / fmax(Ea_tot, 1.0e-300);
    } else if (wc > 1.0e-6) {
      beta_F = nrpic::vlasov::SolveFaceBetaFT<MaxNb>(nb, Da, ua_t, Sa_t, nb, Db, ub_t, Sb_t,
                                                     p.basis_kind, p.n_perp);
    }

    int p_ab[MaxNb], p_ba[MaxNb];
    for (int al = 0; al < nb; ++al) { p_ab[al] = al; p_ba[al] = al; }
    if constexpr (MaxNb > 1) {
      if (wc > 1.0e-6) {
        Real C_ab[MaxNb][MaxNb];
        Real C_ba[MaxNb][MaxNb];
        if (p.pair_mode == VLASOV_PAIR_EB) {
          nrpic::vlasov::PairingCostMatrixT<MaxNb>(nb, Da, ua_t, Sa_t, nb, Db, ub_t, Sb_t, beta_F, C_ab);
          nrpic::vlasov::PairingCostMatrixT<MaxNb>(nb, Db, ub_t, Sb_t, nb, Da, ua_t, Sa_t, beta_F, C_ba);
        } else {
          for (int al = 0; al < nb; ++al) {
            for (int be = 0; be < nb; ++be) {
              Real d2 = 0.0;
              for (int i = 0; i < 3; ++i) {
                const Real du = ua_t[al][i] - ub_t[be][i];
                d2 += du * du;
              }
              C_ab[al][be] = d2;
              C_ba[be][al] = d2;
            }
          }
        }
        for (int al = 0; al < nb; ++al) {
          int best = 0;
          for (int be = 1; be < nb; ++be) if (C_ab[al][be] < C_ab[al][best]) best = be;
          p_ab[al] = best;
        }
        for (int be = 0; be < nb; ++be) {
          int best = 0;
          for (int al = 1; al < nb; ++al) if (C_ba[be][al] < C_ba[be][best]) best = al;
          p_ba[be] = best;
        }
      }

      const int kab = BinaryFindSortedPtr(p.nids, a, p.N, p.ncnt[a], b);
      const int kba = BinaryFindSortedPtr(p.nids, b, p.N, p.ncnt[b], a);
      if (kab >= 0) {
        for (int al = 0; al < nb; ++al) p.npab[static_cast<size_t>(kab * nb + al) * nsz + a] = p_ab[al];
      }
      if (kba >= 0) {
        for (int be = 0; be < nb; ++be) p.npab[static_cast<size_t>(kba * nb + be) * nsz + b] = p_ba[be];
      }
    }

    const Real fac = alp_f * normA;

    if constexpr (Collisional) {
      if (wc < 1.0 - 1.0e-14) {
        Real FD_c = 0.0, FP_c[3] = {0.0, 0.0, 0.0}, FPi_c[3][3], FE_c = 0.0;
        nrpic::vlasov::RelHllcFluxTetrad(nb, Da, ua_t, Sa_t, nb, Db, ub_t, Sb_t,
                                         beta_F, true, FD_c, FP_c, FPi_c, FE_c);
        Real FE_cond = 0.0;
        if (p.noh_kappa > 0.0) {
          nrpic::vlasov::HllcFluidState Lc, Rc;
          Lc.valid = (p.cnv[a] > 0.0);
          if (Lc.valid) {
            Lc.D = p.cnv[0 * nsz + a]; Lc.rho0 = p.cnv[1 * nsz + a]; Lc.p = p.cnv[2 * nsz + a];
            Lc.cs2 = p.cnv[3 * nsz + a]; Lc.w_m = p.cnv[4 * nsz + a];
            Lc.v[0] = e_up[0][0]*p.cnv[5 * nsz + a] + e_up[0][1]*p.cnv[6 * nsz + a] + e_up[0][2]*p.cnv[7 * nsz + a];
          }
          Rc.valid = (p.cnv[b] > 0.0);
          if (Rc.valid) {
            Rc.D = p.cnv[0 * nsz + b]; Rc.rho0 = p.cnv[1 * nsz + b]; Rc.p = p.cnv[2 * nsz + b];
            Rc.cs2 = p.cnv[3 * nsz + b]; Rc.w_m = p.cnv[4 * nsz + b];
            Rc.v[0] = e_up[0][0]*p.cnv[5 * nsz + b] + e_up[0][1]*p.cnv[6 * nsz + b] + e_up[0][2]*p.cnv[7 * nsz + b];
          }
          FE_cond = nrpic::vlasov::NohThermalConductFlux(Lc, Rc, p.noh_kappa);
        }
        const Real omw_fac = (1.0 - wc) * fac;
        const Real fm_tot  = omw_fac * FD_c;
        const Real fe_tot  = omw_fac * (FE_c + FE_cond);
        Real fp[3] = {0.0, 0.0, 0.0}, fpi[3][3];
        for (int i = 0; i < 3; ++i) {
          for (int m = 0; m < 3; ++m) fp[i] += e_dn[m][i] * FP_c[m];
          fp[i] *= omw_fac;
          for (int j = 0; j < 3; ++j) {
            Real s = 0.0;
            for (int m = 0; m < 3; ++m) {
              for (int n = 0; n < 3; ++n) s += e_dn[m][i] * FPi_c[m][n] * e_dn[n][j];
            }
            fpi[i][j] = omw_fac * s;
          }
        }
        Real fpi6[N_SYM6];
        PackSym6(fpi, fpi6);
        Real ma_tot = 0.0, mb_tot = 0.0;
        for (int al = 0; al < nb; ++al) {
          ma_tot += p.m[static_cast<size_t>(al) * nsz + a];
          mb_tot += p.m[static_cast<size_t>(al) * nsz + b];
        }
        ma_tot = fmax(ma_tot, 1.0e-300);
        mb_tot = fmax(mb_tot, 1.0e-300);

        Kokkos::atomic_add(&p.dE[a], -fe_tot);
        Kokkos::atomic_add(&p.dE[b],  fe_tot);
        for (int al = 0; al < nb; ++al) {
          const Real wa = p.m[static_cast<size_t>(al) * nsz + a] / ma_tot;
          if (fm_tot != 0.0) Kokkos::atomic_add(&p.dm[static_cast<size_t>(al) * nsz + a], -wa * fm_tot);
          for (int i = 0; i < 3; ++i) Kokkos::atomic_add(&p.dP[(static_cast<size_t>(al) * 3 + i) * nsz + a], -wa * fp[i]);
          for (int s = 0; s < N_SYM6; ++s) Kokkos::atomic_add(&p.dPi[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a], -wa * fpi6[s]);
        }
        for (int be = 0; be < nb; ++be) {
          const Real wb = p.m[static_cast<size_t>(be) * nsz + b] / mb_tot;
          if (fm_tot != 0.0) Kokkos::atomic_add(&p.dm[static_cast<size_t>(be) * nsz + b], wb * fm_tot);
          for (int i = 0; i < 3; ++i) Kokkos::atomic_add(&p.dP[(static_cast<size_t>(be) * 3 + i) * nsz + b], wb * fp[i]);
          for (int s = 0; s < N_SYM6; ++s) Kokkos::atomic_add(&p.dPi[(static_cast<size_t>(be) * N_SYM6 + s) * nsz + b], wb * fpi6[s]);
        }
      }
    }

    if (wc > 1.0e-6) {
      const Real wc_fac = wc * fac;
      for (int al = 0; al < nb; ++al) {
        if (Da[al] <= 0.0) continue;
        Real fm, fp[3], fpi[3][3], fe;
        nrpic::vlasov::OneSidedFluxTetrad(Da[al], ua_t[al], Sa_t[al], beta_F,
                                          p.basis_kind, p.n_perp, fm, fp, fpi, fe);
        AtomicAddTetFluxPtr(wc_fac, e_dn, a, al, b, p_ab[al], p.N, fm, fp, fpi, fe,
                            p.dm, p.dP, p.dPi, p.dE);
      }
      for (int be = 0; be < nb; ++be) {
        if (Db[be] <= 0.0) continue;
        const Real ub_rev[3] = {-ub_t[be][0], ub_t[be][1], ub_t[be][2]};
        const Real Sb_rev[3][3] = {
          { Sb_t[be][0][0], -Sb_t[be][0][1], -Sb_t[be][0][2]},
          {-Sb_t[be][1][0],  Sb_t[be][1][1],  Sb_t[be][1][2]},
          {-Sb_t[be][2][0],  Sb_t[be][2][1],  Sb_t[be][2][2]}
        };
        Real fm, fp_rev[3], fpi_rev[3][3], fe;
        nrpic::vlasov::OneSidedFluxTetrad(Db[be], ub_rev, Sb_rev, -beta_F,
                                          p.basis_kind, p.n_perp, fm, fp_rev, fpi_rev, fe);
        const Real fp_t[3] = {-fp_rev[0], fp_rev[1], fp_rev[2]};
        const Real fpi_t[3][3] = {
          { fpi_rev[0][0], -fpi_rev[0][1], -fpi_rev[0][2]},
          {-fpi_rev[1][0],  fpi_rev[1][1],  fpi_rev[1][2]},
          {-fpi_rev[2][0],  fpi_rev[2][1],  fpi_rev[2][2]}
        };
        AtomicAddTetFluxPtr(wc_fac, e_dn, b, be, a, p_ba[be], p.N, fm, fp_t, fpi_t, fe,
                            p.dm, p.dP, p.dPi, p.dE);
      }
    }
  });

  if constexpr (MaxNb > 1) {
    std::swap(st.prev_cnt, st.ngb_cnt);
    std::swap(st.prev_ids, st.ngb_ids);
    std::swap(st.new_pab, st.prev_pab);
  }
}

template <bool Collisional, int MaxNb, class SizeViewT>
void ComputeEdgeFluxesDispatchMetric(VlasovState &st, const NrpicOptions &nropt,
                                     const VlasovMetric<SizeViewT> &met, int slot_mode) {
  const int mk = ResolveMetricKind(st, nropt);
  if (mk == 0) {
    ComputeEdgeFluxesImpl<Collisional, MaxNb, 0>(st, nropt, KerrSchildLight{0.0, 0.0}, slot_mode);
  } else if (mk == 1) {
    ComputeEdgeFluxesImpl<Collisional, MaxNb, 1>(st, nropt, KerrSchildLight{met.mass, met.spin}, slot_mode);
  } else {
    ComputeEdgeFluxesImpl<Collisional, MaxNb, 2>(st, nropt, met, slot_mode);
  }
}

template <class SizeViewT>
void ComputeEdgeFluxes(VlasovState &st, const NrpicOptions &nropt,
                       const VlasovMetric<SizeViewT> &met, int slot_mode) {
  const int Nb = st.n_basis;
  if (st.opt.coll_sigma > 0.0) {
    if (Nb <= 1)      ComputeEdgeFluxesDispatchMetric<true, 1>(st, nropt, met, slot_mode);
    else if (Nb <= 2) ComputeEdgeFluxesDispatchMetric<true, 2>(st, nropt, met, slot_mode);
    else if (Nb <= 4) ComputeEdgeFluxesDispatchMetric<true, 4>(st, nropt, met, slot_mode);
    else              ComputeEdgeFluxesDispatchMetric<true, nrpic::vlasov::MAX_BASIS>(st, nropt, met, slot_mode);
  } else {
    if (Nb <= 1)      ComputeEdgeFluxesDispatchMetric<false, 1>(st, nropt, met, slot_mode);
    else if (Nb <= 2) ComputeEdgeFluxesDispatchMetric<false, 2>(st, nropt, met, slot_mode);
    else if (Nb <= 4) ComputeEdgeFluxesDispatchMetric<false, 4>(st, nropt, met, slot_mode);
    else              ComputeEdgeFluxesDispatchMetric<false, nrpic::vlasov::MAX_BASIS>(st, nropt, met, slot_mode);
  }
}

template <int MetricKind, class KickMetT>
void ApplyGeodesicHalfKickImpl(VlasovState &st, const NrpicOptions &nropt,
                               const KickMetT &met, Real half_dt, int slot_mode) {
  VlasovKickPtrs p;
  p.act       = ContigPtr(st.active);
  p.gid       = (MetricKind == 2) ? ContigPtr(st.blk_gid) : nullptr;
  p.x         = ContigPtr(st.x);
  p.m         = ContigPtr(st.m);
  p.P         = ContigPtr(st.P);
  p.Pi        = ContigPtr(st.Pi);
  p.u         = ContigPtr(st.u_bar);
  p.S         = ContigPtr(st.Sigma);
  p.half_dt   = half_dt;
  p.tol       = nropt.tol;
  p.N         = st.n_elem;
  p.Nb        = st.n_basis;
  p.n_q       = st.opt.n_q_kick;
  p.slot_mode = slot_mode;

  par_for("vlasov_geokick", DevExeSpace(), 0, p.N - 1, KOKKOS_LAMBDA(const int a) {
    (void)met;
    if (!p.act[a]) return;
    const size_t nsz = static_cast<size_t>(p.N);
    const Real pos[3] = {p.x[a], p.x[nsz + a], p.x[2 * nsz + a]};
    nrpic::AdmPoint adm;
    if constexpr (MetricKind == 1) {
      met(0, pos, adm);
    } else {
      met(p.slot_mode, pos, p.gid[a], adm);
    }
    if (!HasNonZeroGrad(adm)) return;

    for (int al = 0; al < p.Nb; ++al) {
      const Real ma = p.m[static_cast<size_t>(al) * nsz + a];
      Real u0[3], s6[N_SYM6], S0[3][3], u_new[3], S_new[3][3];
      for (int i = 0; i < 3; ++i) u0[i] = p.u[(static_cast<size_t>(al) * 3 + i) * nsz + a];
      for (int s = 0; s < N_SYM6; ++s) s6[s] = p.S[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a];
      UnpackSym6(s6, S0);

      nrpic::vlasov::CubatureGeodesicKick(u0, S0, adm, nullptr, p.half_dt, p.n_q, u_new, S_new, p.tol);

      Real s_new6[N_SYM6], pi_new[3][3], pi6[N_SYM6];
      PackSym6(S_new, s_new6);
      for (int i = 0; i < 3; ++i) {
        p.u[(static_cast<size_t>(al) * 3 + i) * nsz + a] = u_new[i];
        p.P[(static_cast<size_t>(al) * 3 + i) * nsz + a] = ma * u_new[i];
        for (int j = 0; j < 3; ++j) {
          pi_new[i][j] = ma * (S_new[i][j] + u_new[i] * u_new[j]);
        }
      }
      PackSym6(pi_new, pi6);
      for (int s = 0; s < N_SYM6; ++s) {
        p.S[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a] = s_new6[s];
        p.Pi[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a] = pi6[s];
      }
    }
  });
}

template <class SizeViewT>
void ApplyGeodesicHalfKick(VlasovState &st, const NrpicOptions &nropt,
                           const VlasovMetric<SizeViewT> &met, Real half_dt,
                           int slot_mode) {
  if (st.opt.metric_grad_zero) return;
  if (st.n_elem == 0 || fabs(half_dt) <= 0.0) return;
  if (nropt.metric == NrpicMetric::kerr_schild) {
    ApplyGeodesicHalfKickImpl<1>(st, nropt, nrpic::KerrSchildCart{met.mass, met.spin}, half_dt, slot_mode);
  } else {
    ApplyGeodesicHalfKickImpl<2>(st, nropt, met, half_dt, slot_mode);
  }
}

template <int MetricKind, class LightOrFullMetT>
void ApplyBgkRelaxationImpl(VlasovState &st, const LightOrFullMetT &met,
                            Real dt_sub, int slot_mode) {
  VlasovBgkPtrs p;
  p.act           = ContigPtr(st.active);
  p.gid           = (MetricKind == 2) ? ContigPtr(st.blk_gid) : nullptr;
  p.x             = ContigPtr(st.x);
  p.V             = ContigPtr(st.V);
  p.m             = ContigPtr(st.m);
  p.Ec            = ContigPtr(st.E_cons);
  p.P             = ContigPtr(st.P);
  p.Pi            = ContigPtr(st.Pi);
  p.u             = ContigPtr(st.u_bar);
  p.S             = ContigPtr(st.Sigma);
  p.sigma_over_mu = st.opt.coll_sigma;
  p.dt_sub        = dt_sub;
  p.N             = st.n_elem;
  p.Nb            = st.n_basis;
  p.n_q           = st.opt.n_q_dep;
  p.slot_mode     = slot_mode;
  p.track_e       = st.opt.bgk_track_e;

  par_for("vlasov_bgk", DevExeSpace(), 0, p.N - 1, KOKKOS_LAMBDA(const int a) {
    (void)met;
    if (!p.act[a]) return;
    const size_t nsz = static_cast<size_t>(p.N);
    nrpic::AdmPoint adm;
    if constexpr (MetricKind == 0) {
      adm.alp = 1.0;
      for (int i = 0; i < 3; ++i) {
        adm.beta[i] = 0.0;
        for (int j = 0; j < 3; ++j) adm.g[i][j] = (i == j) ? 1.0 : 0.0;
      }
    } else if constexpr (MetricKind == 1) {
      const Real pos[3] = {p.x[a], p.x[nsz + a], p.x[2 * nsz + a]};
      met.EvalNoDeriv(pos, adm.alp, adm.beta, adm.g);
    } else {
      const Real pos[3] = {p.x[a], p.x[nsz + a], p.x[2 * nsz + a]};
      met(p.slot_mode, pos, p.gid[a], adm);
    }

    Real ml[nrpic::vlasov::MAX_BASIS];
    Real ul[nrpic::vlasov::MAX_BASIS][3], u_out[nrpic::vlasov::MAX_BASIS][3];
    Real Sl[nrpic::vlasov::MAX_BASIS][3][3], S_out[nrpic::vlasov::MAX_BASIS][3][3];
    for (int al = 0; al < p.Nb; ++al) {
      ml[al] = p.m[static_cast<size_t>(al) * nsz + a];
      for (int i = 0; i < 3; ++i) ul[al][i] = p.u[(static_cast<size_t>(al) * 3 + i) * nsz + a];
      Real s6[N_SYM6];
      for (int s = 0; s < N_SYM6; ++s) s6[s] = p.S[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a];
      UnpackSym6(s6, Sl[al]);
    }

    const Real E_ov = p.Ec[a];
    nrpic::vlasov::MjBgkRelaxCell(p.Nb, ml, ul, Sl, p.V[a], adm, p.sigma_over_mu, p.dt_sub, p.n_q,
                                  u_out, S_out, p.track_e ? &E_ov : nullptr);

    for (int al = 0; al < p.Nb; ++al) {
      Real pi_m[3][3], pi6[N_SYM6], sig6[N_SYM6];
      for (int i = 0; i < 3; ++i) {
        p.u[(static_cast<size_t>(al) * 3 + i) * nsz + a] = u_out[al][i];
        p.P[(static_cast<size_t>(al) * 3 + i) * nsz + a] = ml[al] * u_out[al][i];
        for (int j = 0; j < 3; ++j) {
          pi_m[i][j] = ml[al] * (S_out[al][i][j] + u_out[al][i] * u_out[al][j]);
        }
      }
      PackSym6(S_out[al], sig6);
      PackSym6(pi_m, pi6);
      for (int s = 0; s < N_SYM6; ++s) {
        p.S[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a]  = sig6[s];
        p.Pi[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a] = pi6[s];
      }
    }
  });
}

template <class SizeViewT>
void ApplyBgkRelaxation(VlasovState &st, const NrpicOptions &nropt,
                        const VlasovMetric<SizeViewT> &met, Real dt_sub, int slot_mode) {
  if (st.n_elem == 0 || st.opt.coll_sigma <= 0.0 || dt_sub <= 0.0) return;
  const int mk = ResolveMetricKind(st, nropt);
  if (mk == 0)      ApplyBgkRelaxationImpl<0>(st, KerrSchildLight{0.0, 0.0}, dt_sub, slot_mode);
  else if (mk == 1) ApplyBgkRelaxationImpl<1>(st, KerrSchildLight{met.mass, met.spin}, dt_sub, slot_mode);
  else              ApplyBgkRelaxationImpl<2>(st, met, dt_sub, slot_mode);
}

template <int MetricKind, class LightOrFullMetT>
void ComputeEnergyArrayImpl(VlasovState &st, const LightOrFullMetT &met,
                            int slot_mode, DvceArray1D<Real> &E_out) {
  const int N = st.n_elem;
  const int Nb = st.n_basis;
  if (N == 0) return;
  const int *act = ContigPtr(st.active);
  const int *gid = (MetricKind == 2) ? ContigPtr(st.blk_gid) : nullptr;
  const Real *xv = (MetricKind != 0) ? ContigPtr(st.x) : nullptr;
  const Real *mv = ContigPtr(st.m);
  const Real *uv = ContigPtr(st.u_bar);
  const Real *Sv = ContigPtr(st.Sigma);
  Real *eo       = ContigPtr(E_out);
  const int n_q  = st.opt.n_q_dep;

  par_for("vlasov_e_cell", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    (void)met; (void)xv; (void)gid; (void)slot_mode;
    if (!act[a]) { eo[a] = 0.0; return; }
    const size_t nsz = static_cast<size_t>(N);
    Real gi[3][3] = {{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}};
    if constexpr (MetricKind == 1) {
      const Real pos[3] = {xv[a], xv[nsz + a], xv[2 * nsz + a]};
      Real alp_tmp, b_tmp[3], g[3][3];
      met.EvalNoDeriv(pos, alp_tmp, b_tmp, g);
      nrpic::Inv3Sym(g, gi);
    } else if constexpr (MetricKind == 2) {
      const Real pos[3] = {xv[a], xv[nsz + a], xv[2 * nsz + a]};
      nrpic::AdmPoint adm;
      met(slot_mode, pos, gid[a], adm);
      nrpic::Inv3Sym(adm.g, gi);
    }
    Real Et = 0.0;
    for (int al = 0; al < Nb; ++al) {
      const Real ma = mv[static_cast<size_t>(al) * nsz + a];
      if (ma <= 0.0) continue;
      Real ua[3], s6[N_SYM6], Sa[3][3], ea, pa[3], sa[3][3];
      for (int i = 0; i < 3; ++i) ua[i] = uv[(static_cast<size_t>(al) * 3 + i) * nsz + a];
      for (int s = 0; s < N_SYM6; ++s) s6[s] = Sv[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a];
      UnpackSym6(s6, Sa);
      nrpic::vlasov::BasisStressEnergy(ma, ua, Sa, gi, n_q, ea, pa, sa);
      Et += ea;
    }
    eo[a] = Et;
  });
}

template <class SizeViewT>
void ComputeEnergyArray(VlasovState &st, const NrpicOptions &nropt,
                        const VlasovMetric<SizeViewT> &met, int slot_mode,
                        DvceArray1D<Real> &E_out) {
  const int mk = ResolveMetricKind(st, nropt);
  if (mk == 0)      ComputeEnergyArrayImpl<0>(st, KerrSchildLight{0.0, 0.0}, slot_mode, E_out);
  else if (mk == 1) ComputeEnergyArrayImpl<1>(st, KerrSchildLight{met.mass, met.spin}, slot_mode, E_out);
  else              ComputeEnergyArrayImpl<2>(st, met, slot_mode, E_out);
}

template <int MetricKind, class LightOrFullMetT>
Real ComputeMinCflTimeImpl(VlasovState &st, const LightOrFullMetT &met,
                           int slot_mode, Real &max_sig_out) {
  const int N = st.n_elem;
  const int Nb = st.n_basis;
  if (N == 0) {
    max_sig_out = 0.0;
    return 1.0e300;
  }
  const int *act = ContigPtr(st.active);
  const int *gid = (MetricKind == 2) ? ContigPtr(st.blk_gid) : nullptr;
  const Real *xv = (MetricKind != 0) ? ContigPtr(st.x) : nullptr;
  const Real *hv = ContigPtr(st.h);
  const Real *mv = ContigPtr(st.m);
  const Real *uv = ContigPtr(st.u_bar);
  const Real *Sv = ContigPtr(st.Sigma);

  Real min_dt = 1.0e300;
  Real max_s  = 0.0;
  Kokkos::parallel_reduce("vlasov_cfl", Kokkos::RangePolicy<DevExeSpace>(0, N),
  KOKKOS_LAMBDA(const int a, Real &ldt, Real &lsig) {
    (void)met; (void)xv; (void)gid; (void)slot_mode;
    if (!act[a]) return;
    const size_t nsz = static_cast<size_t>(N);
    Real alp = 1.0;
    Real beta[3] = {0.0, 0.0, 0.0};
    Real g[3][3] = {{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}};
    Real gi[3][3] = {{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}};
    if constexpr (MetricKind == 1) {
      const Real pos[3] = {xv[a], xv[nsz + a], xv[2 * nsz + a]};
      met.EvalNoDeriv(pos, alp, beta, g);
      nrpic::Inv3Sym(g, gi);
    } else if constexpr (MetricKind == 2) {
      const Real pos[3] = {xv[a], xv[nsz + a], xv[2 * nsz + a]};
      nrpic::AdmPoint adm;
      met(slot_mode, pos, gid[a], adm);
      alp = adm.alp;
      for (int i = 0; i < 3; ++i) {
        beta[i] = adm.beta[i];
        for (int j = 0; j < 3; ++j) g[i][j] = adm.g[i][j];
      }
      nrpic::Inv3Sym(g, gi);
    }
    const Real beta_mag = (MetricKind == 0) ? 0.0 : sqrt(nrpic::vlasov::MatVecDot3(beta, g, beta));
    Real sig_a = 1.0e-12;
    for (int al = 0; al < Nb; ++al) {
      if (mv[static_cast<size_t>(al) * nsz + a] <= 0.0) continue;
      Real ua[3], s6[N_SYM6], Sa[3][3];
      for (int i = 0; i < 3; ++i) ua[i] = uv[(static_cast<size_t>(al) * 3 + i) * nsz + a];
      for (int s = 0; s < N_SYM6; ++s) s6[s] = Sv[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + a];
      UnpackSym6(s6, Sa);
      const Real u2 = nrpic::vlasov::MatVecDot3(ua, gi, ua);
      const Real W2 = 1.0 + u2;
      const Real v_mag = alp * sqrt(u2 / W2) + beta_mag;
      Real tr_gi_S = 0.0;
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) tr_gi_S += gi[i][j] * Sa[i][j];
      }
      const Real cs_eff = alp * sqrt(fmin(fmax(tr_gi_S, 0.0) / W2, 1.0));
      const Real s_al = fmin(v_mag + cs_eff, 2.0 * fmax(alp, 1.0) + beta_mag);
      if (s_al > sig_a) sig_a = s_al;
    }
    const Real ha = fmax(hv[a], 1.0e-12);
    ldt  = fmin(ldt, ha / sig_a);
    lsig = fmax(lsig, sig_a);
  }, Kokkos::Min<Real>(min_dt), Kokkos::Max<Real>(max_s));
  max_sig_out = max_s;
  return min_dt;
}

template <class SizeViewT>
Real ComputeMinCflTime(VlasovState &st, const NrpicOptions &nropt,
                       const VlasovMetric<SizeViewT> &met, int slot_mode,
                       Real &max_sig_out) {
  const int mk = ResolveMetricKind(st, nropt);
  if (mk == 0)      return ComputeMinCflTimeImpl<0>(st, KerrSchildLight{0.0, 0.0}, slot_mode, max_sig_out);
  else if (mk == 1) return ComputeMinCflTimeImpl<1>(st, KerrSchildLight{met.mass, met.spin}, slot_mode, max_sig_out);
  else              return ComputeMinCflTimeImpl<2>(st, met, slot_mode, max_sig_out);
}

template <class SizeViewT>
void ApplyMfmStep(VlasovState &st, const NrpicOptions &nropt,
                  const VlasovMetric<SizeViewT> &met, Real dt_sub, int slot_mode) {
  const int N  = st.n_elem;
  const int Nb = st.n_basis;
  const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3]  = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};

  Kokkos::deep_copy(DevExeSpace(), st.x0,  st.x);
  Kokkos::deep_copy(DevExeSpace(), st.m0,  st.m);
  Kokkos::deep_copy(DevExeSpace(), st.P0,  st.P);
  Kokkos::deep_copy(DevExeSpace(), st.Pi0, st.Pi);
  if (st.opt.coll_sigma > 0.0 && st.opt.bgk_track_e) {
    ComputeEnergyArray(st, nropt, met, slot_mode, st.E0);
  }

  ComputeGradients(st, nropt);
  ComputeCellVelocities(st, nropt, met, slot_mode);
  ComputeEdgeFluxes(st, nropt, met, slot_mode);
  Kokkos::deep_copy(DevExeSpace(), st.v0_cell, st.v_cell);

  const int  *act  = ContigPtr(st.active);
  const Real *x0v  = ContigPtr(st.x0);
  Real       *xv   = ContigPtr(st.x);
  const Real *v0v  = ContigPtr(st.v0_cell);
  const Real *v1v  = ContigPtr(st.v_cell);
  const Real *m0v  = ContigPtr(st.m0);
  Real       *mv   = ContigPtr(st.m);
  const Real *dmv  = ContigPtr(st.dm);
  const Real *P0v  = ContigPtr(st.P0);
  Real       *Pv   = ContigPtr(st.P);
  const Real *dPv  = ContigPtr(st.dP);
  const Real *Pi0v = ContigPtr(st.Pi0);
  Real       *Piv  = ContigPtr(st.Pi);
  const Real *dPiv = ContigPtr(st.dPi);

  par_for("vlasov_rk2_s1", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    if (!act[a]) return;
    const size_t nsz = static_cast<size_t>(N);
    Real pos[3] = {x0v[a] + dt_sub * v0v[a],
                   x0v[nsz + a] + dt_sub * v0v[nsz + a],
                   x0v[2 * nsz + a] + dt_sub * v0v[2 * nsz + a]};
    WrapPos(dmin, dlen, per, pos);
    for (int i = 0; i < 3; ++i) xv[static_cast<size_t>(i) * nsz + a] = pos[i];
    for (int al = 0; al < Nb; ++al) {
      const size_t idx_m = static_cast<size_t>(al) * nsz + a;
      mv[idx_m] = m0v[idx_m] + dt_sub * dmv[idx_m];
      for (int i = 0; i < 3; ++i) {
        const size_t idx_p = (static_cast<size_t>(al) * 3 + i) * nsz + a;
        Pv[idx_p] = P0v[idx_p] + dt_sub * dPv[idx_p];
      }
      for (int s = 0; s < N_SYM6; ++s) {
        const size_t idx_pi = (static_cast<size_t>(al) * N_SYM6 + s) * nsz + a;
        Piv[idx_pi] = Pi0v[idx_pi] + dt_sub * dPiv[idx_pi];
      }
    }
  });
  if (st.opt.coll_sigma > 0.0 && st.opt.bgk_track_e) {
    const Real *E0v = ContigPtr(st.E0);
    const Real *dEv = ContigPtr(st.dE);
    Real *Ecv       = ContigPtr(st.E_cons);
    par_for("vlasov_rk2_s1_e", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
      if (act[a]) Ecv[a] = E0v[a] + dt_sub * dEv[a];
    });
  }
  UpdateBlockGIDs(st, nropt, met.sz, met.nmb, met.gids);
  UpdateGeometry(st, nropt, true);
  ConsToPrim(st);

  ComputeGradients(st, nropt);
  ComputeCellVelocities(st, nropt, met, slot_mode);
  ComputeEdgeFluxes(st, nropt, met, slot_mode);

  par_for("vlasov_rk2_s2", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    if (!act[a]) return;
    const size_t nsz = static_cast<size_t>(N);
    Real pos[3] = {x0v[a] + 0.5 * dt_sub * (v0v[a] + v1v[a]),
                   x0v[nsz + a] + 0.5 * dt_sub * (v0v[nsz + a] + v1v[nsz + a]),
                   x0v[2 * nsz + a] + 0.5 * dt_sub * (v0v[2 * nsz + a] + v1v[2 * nsz + a])};
    WrapPos(dmin, dlen, per, pos);
    for (int i = 0; i < 3; ++i) xv[static_cast<size_t>(i) * nsz + a] = pos[i];
    for (int al = 0; al < Nb; ++al) {
      const size_t idx_m = static_cast<size_t>(al) * nsz + a;
      mv[idx_m] = 0.5 * (m0v[idx_m] + mv[idx_m] + dt_sub * dmv[idx_m]);
      for (int i = 0; i < 3; ++i) {
        const size_t idx_p = (static_cast<size_t>(al) * 3 + i) * nsz + a;
        Pv[idx_p] = 0.5 * (P0v[idx_p] + Pv[idx_p] + dt_sub * dPv[idx_p]);
      }
      for (int s = 0; s < N_SYM6; ++s) {
        const size_t idx_pi = (static_cast<size_t>(al) * N_SYM6 + s) * nsz + a;
        Piv[idx_pi] = 0.5 * (Pi0v[idx_pi] + Piv[idx_pi] + dt_sub * dPiv[idx_pi]);
      }
    }
  });
  if (st.opt.coll_sigma > 0.0 && st.opt.bgk_track_e) {
    const Real *E0v = ContigPtr(st.E0);
    const Real *dEv = ContigPtr(st.dE);
    Real *Ecv       = ContigPtr(st.E_cons);
    par_for("vlasov_rk2_s2_e", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
      if (act[a]) Ecv[a] = 0.5 * (E0v[a] + Ecv[a] + dt_sub * dEv[a]);
    });
  }
  UpdateBlockGIDs(st, nropt, met.sz, met.nmb, met.gids);
  UpdateGeometry(st, nropt, true);
  ConsToPrim(st);

  if (st.opt.coll_sigma > 0.0) {
    ApplyBgkRelaxation(st, nropt, met, dt_sub, slot_mode);
    ConsToPrim(st);
  }
}

}  // namespace

void AdvanceMfmStep(Particles *pthis, MeshBlockPack *ppack) {
  VlasovState *vlv = pthis->vlv;
  if (vlv == nullptr || vlv->n_elem == 0) return;
  Mesh *pm = ppack->pmesh;
  const Real dt = pm->dt;
  if (dt <= 0.0) return;

  auto sz  = ppack->pmb->mb_size.d_view;
  UpdateBlockGIDs(*vlv, pthis->nropt, sz, ppack->nmb_thispack, ppack->gids);
  auto met = BuildMetricHelper(pthis, ppack, sz);

  const bool static_met = pthis->metric_is_static || (pthis->nropt.metric != NrpicMetric::mesh);
  auto compute_nsub = [&](Real &max_sig_out) -> int {
    const Real dt_cfl_unit = ComputeMinCflTime(*vlv, pthis->nropt, met, 2, max_sig_out);
    vlv->opt.max_sig_last = max_sig_out;
    int ns = 1;
    if (vlv->opt.fixed_substeps > 0) {
      ns = vlv->opt.fixed_substeps;
    } else {
      const Real target = std::max(vlv->opt.cfl * dt_cfl_unit, 1.0e-30);
      ns = static_cast<int>(std::ceil(dt / target));
      if (ns < 1) ns = 1;
      if (ns > vlv->opt.max_substeps) ns = vlv->opt.max_substeps;
    }
    vlv->opt.substeps_last = ns;
    return ns;
  };

  if (static_met) {
    Real max_sig = 0.0;
    const int n_sub = compute_nsub(max_sig);
    const Real dt_sub = dt / static_cast<Real>(n_sub);
    for (int isub = 0; isub < n_sub; ++isub) {
      ApplyGeodesicHalfKick(*vlv, pthis->nropt, met, 0.5 * dt_sub, 2);
      ApplyMfmStep(*vlv, pthis->nropt, met, dt_sub, 2);
      ApplyGeodesicHalfKick(*vlv, pthis->nropt, met, 0.5 * dt_sub, 2);
    }
  } else {
    ApplyGeodesicHalfKick(*vlv, pthis->nropt, met, 0.5 * dt, 0);
    Real max_sig = 0.0;
    const int n_sub = compute_nsub(max_sig);
    const Real dt_sub = dt / static_cast<Real>(n_sub);
    for (int isub = 0; isub < n_sub; ++isub) {
      ApplyMfmStep(*vlv, pthis->nropt, met, dt_sub, 2);
    }
    ApplyGeodesicHalfKick(*vlv, pthis->nropt, met, 0.5 * dt, 1);
  }
  ConsToPrim(*vlv);
}

void ExciseMfmState(Particles *pthis, MeshBlockPack *ppack) {
  VlasovState *vlv = pthis->vlv;
  if (vlv == nullptr || vlv->n_elem == 0) return;

  pthis->acc_after_push = true;
  auto sz  = ppack->pmb->mb_size.d_view;
  auto met = BuildMetricHelper(pthis, ppack, sz);

  const int N  = vlv->n_elem;
  const int Nb = vlv->n_basis;
  const bool mesh_metric = (pthis->nropt.metric == NrpicMetric::mesh);
  const Real alpha_exc   = pthis->nropt.alpha_exc;
  const int gids         = ppack->gids;
  const int nmb          = ppack->nmb_thispack;
  const bool is_kerr_cks = (pthis->nropt.metric == NrpicMetric::kerr_schild ||
                            pthis->nropt.metric == NrpicMetric::lattice);
  const bool is_kerr_sph = (pthis->nropt.metric == NrpicMetric::kerr_schild_sph ||
                            pthis->nropt.metric == NrpicMetric::boyer_lindquist);
  const Real bh_M        = pthis->nropt.mass;
  const Real bh_a        = pthis->nropt.spin;
  const Real r_plus      = bh_M + sqrt(fmax(bh_M * bh_M - bh_a * bh_a, 0.0));
  const Real r_exc_bl    = (vlv->opt.kerr_r_exc > 0.0 && (is_kerr_cks || is_kerr_sph))
                           ? (vlv->opt.kerr_r_exc * r_plus) : 0.0;

  int nah = 0;
  Real ahc[4][3], ahr2[4];
  for (int n = 0; n < 4; ++n) {
    ahc[n][0] = ahc[n][1] = ahc[n][2] = 0.0;
    ahr2[n] = 0.0;
  }
  if (mesh_metric && pthis->nropt.ah_exc_factor > 0.0 && ppack->pz4c != nullptr) {
    for (auto &pah : ppack->pz4c->pfastflow) {
      if (pah->ah_found && nah < 4 && Kokkos::isfinite(pah->rr_min) &&
          pah->rr_min > 0.0 && pah->rr_min < 4.0 * pah->initial_radius) {
        ahc[nah][0] = pah->center[0];
        ahc[nah][1] = pah->center[1];
        ahc[nah][2] = pah->center[2];
        ahr2[nah] = SQR(pthis->nropt.ah_exc_factor * pah->rr_min);
        ++nah;
      }
    }
  }

  auto act  = vlv->active;
  auto xv   = vlv->x;
  auto gidv = vlv->blk_gid;
  auto mv   = vlv->m;
  auto Pv   = vlv->P;
  auto Piv  = vlv->Pi;
  auto Dv   = vlv->D;
  auto uv   = vlv->u_bar;
  auto Sv   = vlv->Sigma;

  const Real dmin[3] = {pthis->nropt.dom_min[0], pthis->nropt.dom_min[1], pthis->nropt.dom_min[2]};
  const Real dlen[3] = {pthis->nropt.dom_len[0], pthis->nropt.dom_len[1], pthis->nropt.dom_len[2]};
  const bool per[3]  = {pthis->nropt.periodic[0], pthis->nropt.periodic[1], pthis->nropt.periodic[2]};

  int nesc = 0, nexc = 0;
  Real mesc = 0.0, mexc = 0.0;

  Kokkos::parallel_reduce("vlasov_excise", Kokkos::RangePolicy<DevExeSpace>(0, N),
  KOKKOS_LAMBDA(const int a, int &lnesc, int &lnexc, Real &lmesc, Real &lmexc) {
    if (!act(a)) return;
    Real pos[3] = {xv(0, a), xv(1, a), xv(2, a)};
    Real chk = pos[0] + pos[1] + pos[2];
    Real m_tot = 0.0;
    for (int al = 0; al < Nb; ++al) {
      m_tot += mv(al, a);
      chk += mv(al, a);
      for (int i = 0; i < 3; ++i) chk += Pv(al, i, a);
      for (int s = 0; s < N_SYM6; ++s) chk += Piv(al, s, a);
    }

    bool do_esc = false;
    bool do_exc = !Kokkos::isfinite(chk);

    if (!do_exc && mesh_metric) {
      WrapPos(dmin, dlen, per, pos);
      xv(0, a) = pos[0]; xv(1, a) = pos[1]; xv(2, a) = pos[2];
      const int mb = nrpic::FindBlock(sz, nmb, gidv(a) - gids, pos[0], pos[1], pos[2]);
      if (mb < 0) {
        do_esc = true;
      } else {
        gidv(a) = mb + gids;
      }
    }

    if (!do_esc && !do_exc && (alpha_exc > 0.0 || nah > 0)) {
      nrpic::AdmPoint ap;
      met(1, pos, gidv(a), ap);
      if (alpha_exc > 0.0 && ap.alp < alpha_exc) {
        do_exc = true;
      }
      for (int h_i = 0; h_i < nah; ++h_i) {
        const Real dx = pos[0] - ahc[h_i][0];
        const Real dy = pos[1] - ahc[h_i][1];
        const Real dz = pos[2] - ahc[h_i][2];
        if (dx*dx + dy*dy + dz*dz < ahr2[h_i]) {
          do_exc = true;
        }
      }
    }

    if (!do_esc && !do_exc && r_exc_bl > 0.0) {
      Real r_bl = 1.0e300;
      if (is_kerr_cks) {
        const Real a2 = bh_a * bh_a;
        const Real b  = pos[0]*pos[0] + pos[1]*pos[1] + pos[2]*pos[2] - a2;
        const Real r2 = 0.5 * (b + sqrt(b*b + 4.0*a2*pos[2]*pos[2]));
        r_bl = sqrt(fmax(r2, 0.0));
      } else if (is_kerr_sph) {
        r_bl = pos[0];
      }
      if (r_bl < r_exc_bl) {
        do_exc = true;
      }
    }

    if (do_esc || do_exc) {
      act(a) = 0;
      gidv(a) = do_esc ? -1 : -2;
      for (int al = 0; al < Nb; ++al) {
        mv(al, a) = 0.0;
        Dv(al, a) = 0.0;
        for (int i = 0; i < 3; ++i) { Pv(al, i, a) = 0.0; uv(al, i, a) = 0.0; }
        for (int s = 0; s < N_SYM6; ++s) { Piv(al, s, a) = 0.0; Sv(al, s, a) = 0.0; }
      }
      if (do_esc) { lnesc += 1; lmesc += m_tot; }
      else        { lnexc += 1; lmexc += m_tot; }
    }
  }, Kokkos::Sum<int>(nesc), Kokkos::Sum<int>(nexc),
     Kokkos::Sum<Real>(mesc), Kokkos::Sum<Real>(mexc));

  if (nesc + nexc > 0) {
    pthis->n_escaped    += nesc;
    pthis->n_excised    += nexc;
    pthis->mass_escaped += mesc;
    pthis->mass_excised += mexc;
    UpdateGeometry(*vlv, pthis->nropt, true);
  }
  pthis->acc_after_push = false;
}

}  // namespace nrpic_vlasov_detail

void Particles::NrpicVlasovPush() {
  if (vlv == nullptr) return;
  if (vlv->opt.packet_mode) {
    nrpic_vlasov_detail::PushScpPackets(this, pmy_pack);
  } else {
    nrpic_vlasov_detail::AdvanceMfmStep(this, pmy_pack);
  }
}

void Particles::NrpicVlasovExcise() {
  if (vlv == nullptr) return;
  if (vlv->opt.packet_mode) {
    acc_after_push = true;
    if (nropt.metric == NrpicMetric::mesh) {
      NrpicAssignBlocks();
      NrpicRemoveFlagged();
    } else {
      NrpicRemoveFlagged();
    }
    acc_after_push = false;
  } else {
    nrpic_vlasov_detail::ExciseMfmState(this, pmy_pack);
  }
}

}  // namespace particles

