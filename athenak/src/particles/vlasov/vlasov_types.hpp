#ifndef PARTICLES_VLASOV_VLASOV_TYPES_HPP_
#define PARTICLES_VLASOV_VLASOV_TYPES_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_types.hpp
//! \brief State structures, runtime options, inline Kokkos device helpers, and metric
//! adapters for the modular GR-LBV / hybrid Vlasov solver in NRPIC.

#include <cstdlib>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

#include "athena.hpp"
#include "coordinates/adm.hpp"
#include "mesh/mesh.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_metrics.hpp"
#include "particles/nrpic_mesh.hpp"
#include "particles/vlasov/vlasov_flux_kernels.hpp"
#include "particles/vlasov/vlasov_pushers.hpp"

namespace particles {

enum VlasovPairMode {
  VLASOV_PAIR_EB = 0,
  VLASOV_PAIR_VONLY = 1
};

enum VlasovSolverMode {
  VLASOV_MODE_MFM = 0,
  VLASOV_MODE_HYBRID = 1,
  VLASOV_MODE_SCP = 2
};

enum VlasovPusherKind {
  VLASOV_PUSH_MIDPOINT = 0,
  VLASOV_PUSH_GL4 = 1,
  VLASOV_PUSH_BORIS = 2
};

enum VlasovTimeInterpKind {
  VLASOV_TINTERP_LINEAR = 0,
  VLASOV_TINTERP_QUADRATIC = 1
};

// Indices of symmetric 3x3 tensor packed into 6 components: (0,0),(0,1),(0,2),(1,1),(1,2),(2,2)
enum VlasovSym6 {
  SYM_XX = 0,
  SYM_XY = 1,
  SYM_XZ = 2,
  SYM_YY = 3,
  SYM_YZ = 4,
  SYM_ZZ = 5,
  N_SYM6 = 6
};

struct VlasovOptions {
  int solver_mode = VLASOV_MODE_MFM;
  bool packet_mode = false;
  int scp_n_q = 14;
  bool scp_rotate = true;
  bool scp_s2_shell = false;
  int scp_s2_q = 14;
  int scp_pusher = VLASOV_PUSH_MIDPOINT;
  int time_interp = VLASOV_TINTERP_LINEAR;
  bool metric_grad_zero = false;
  bool metric_is_minkowski = false;
  int basis_kind = nrpic::vlasov::BASIS_TOPHAT;
  int n_perp = 3;
  int n_q_kick = 3;
  int n_q_dep = 3;
  int pair_mode = VLASOV_PAIR_EB;
  bool use_analytic_vf = false;
  Real cfl = 0.3;
  int fixed_substeps = 0;     // >0 overrides adaptive CFL subcycling (for parity tests)
  int max_substeps = 64;
  Real coll_sigma = 0.0;      // sigma / mu in M^{-1} (<= 0: collisionless)
  bool bgk_track_e = false;   // true on flat static mesh to pass E_cons override to BGK
  Real lim_eps_v = 0.1;       // velocity-crossing gradient limiter scale factor
  bool bnd_detect = false;    // detect & zero gradients on vacuum-boundary elements
  Real bnd_cm_tol = 0.35;
  int bnd_min_ngb = 12;
  Real noh_kappa = 0.5;       // harmonic-cs Noh/Price thermal conduction coeff in HLLC
  Real kerr_r_exc = 0.0;      // >0: excise elements with r_BL < kerr_r_exc * r_+ in analytic Kerr
  int substeps_last = 0;
  Real max_sig_last = 0.0;
};

struct VlasovState {
  VlasovOptions opt;
  int n_elem = 0;
  int n_basis = 0;
  int max_ngb = 64;
  int n_edges = 0;
  int edge_cap = 0;
  int grid_cap = 0;
  bool initialized = false;
  Real load_time = 0.0;
  Real dt_prev = -1.0;
  Real dt_step_cur = -1.0;
  bool met_prev_valid = false;

  // Spatial coordinate arrays (last index is element index a for coalesced GPU access)
  DvceArray2D<Real> x;        // (3, N)
  DvceArray2D<Real> x0;       // (3, N)
  DvceArray2D<Real> v_cell;   // (3, N)
  DvceArray2D<Real> v0_cell;  // (3, N)
  DvceArray2D<Real> u_bulk;   // (3, N)

  // Conservative basis moments
  DvceArray2D<Real> m;        // (Nb, N)
  DvceArray2D<Real> m0;       // (Nb, N)
  DvceArray2D<Real> dm;       // (Nb, N)
  DvceArray3D<Real> P;        // (Nb, 3, N)
  DvceArray3D<Real> P0;       // (Nb, 3, N)
  DvceArray3D<Real> dP;       // (Nb, 3, N)
  DvceArray3D<Real> Pi;       // (Nb, 6, N)  packed symmetric 3x3
  DvceArray3D<Real> Pi0;      // (Nb, 6, N)
  DvceArray3D<Real> dPi;      // (Nb, 6, N)

  // Energy tracking & hoisted Noh conduction state for collisional HLLC+BGK
  DvceArray1D<Real> E0;       // (N)
  DvceArray1D<Real> E_cons;   // (N)
  DvceArray1D<Real> dE;       // (N)
  DvceArray2D<Real> cell_noh; // (8, N) precomputed cell HLLC state for Noh conduction

  // Primitive basis variables
  DvceArray2D<Real> D;        // (Nb, N)
  DvceArray3D<Real> u_bar;    // (Nb, 3, N)
  DvceArray3D<Real> Sigma;    // (Nb, 6, N)  packed symmetric 3x3

  // MFM element geometry & flags
  DvceArray1D<Real> h;        // (N)
  DvceArray1D<Real> V;        // (N)
  DvceArray2D<Real> Einv;     // (6, N)      packed symmetric 3x3
  DvceArray1D<int> active;    // (N)         1 = live, 0 = excised/escaped
  DvceArray1D<int> species;   // (N)
  DvceArray1D<int> blk_gid;   // (N)
  DvceArray1D<int> is_bnd;    // (N)

  // Limited MLS gradients
  DvceArray3D<Real> grad_D;   // (Nb, 3, N)
  DvceArray4D<Real> grad_u;   // (Nb, 3, 3, N)      (al, comp_u, grad_dir, a)
  DvceArray4D<Real> grad_S;   // (Nb, 6, 3, N)      (al, sym6, grad_dir, a)

  // Neighbor & persistent basis pairing tables
  DvceArray1D<int> ngb_cnt;   // (N)
  DvceArray2D<int> ngb_ids;   // (max_ngb, N)       sorted ascending per a
  DvceArray2D<int> new_pab;   // (max_ngb*Nb, N)    slot k * Nb + al -> beta
  DvceArray1D<int> prev_cnt;  // (N)
  DvceArray2D<int> prev_ids;  // (max_ngb, N)
  DvceArray2D<int> prev_pab;  // (max_ngb*Nb, N)

  // Unique unordered edges (a < b)
  DvceArray1D<int> edge_off;  // (N)
  DvceArray1D<int> edge_a;    // (edge_cap)
  DvceArray1D<int> edge_b;    // (edge_cap)

  // Spatial CSR hash grid buffers
  DvceArray1D<int> grid_cell_id;  // (N)
  DvceArray1D<int> grid_cnt;      // (grid_cap)
  DvceArray1D<int> grid_off;      // (grid_cap)
  DvceArray1D<int> grid_cur;      // (grid_cap)
  DvceArray1D<int> grid_elem;     // (N)

  // Restart staging buffers
  std::vector<double> restart_real;
  std::vector<int> restart_int;
  std::vector<int> restart_meta;
};

namespace nrpic_vlasov_detail {

//----------------------------------------------------------------------------------------
// Device-safe inline helpers (must remain in header when -rdc=true is OFF)
//----------------------------------------------------------------------------------------

KOKKOS_INLINE_FUNCTION
void PackSym6(const Real M[3][3], Real s[6]) {
  s[SYM_XX] = M[0][0];
  s[SYM_XY] = 0.5 * (M[0][1] + M[1][0]);
  s[SYM_XZ] = 0.5 * (M[0][2] + M[2][0]);
  s[SYM_YY] = M[1][1];
  s[SYM_YZ] = 0.5 * (M[1][2] + M[2][1]);
  s[SYM_ZZ] = M[2][2];
}

KOKKOS_INLINE_FUNCTION
void UnpackSym6(const Real s[6], Real M[3][3]) {
  M[0][0] = s[SYM_XX];
  M[0][1] = M[1][0] = s[SYM_XY];
  M[0][2] = M[2][0] = s[SYM_XZ];
  M[1][1] = s[SYM_YY];
  M[1][2] = M[2][1] = s[SYM_YZ];
  M[2][2] = s[SYM_ZZ];
}

KOKKOS_INLINE_FUNCTION
Real CubicSpline3D(Real r, Real h) {
  const Real q = r / h;
  if (q >= 2.0) return 0.0;
  const Real norm = 1.0 / (nrpic::vlasov::kPi * h * h * h);
  if (q < 1.0) {
    return norm * (1.0 - 1.5*q*q + 0.75*q*q*q);
  }
  const Real t = 2.0 - q;
  return norm * 0.25 * t * t * t;
}

KOKKOS_INLINE_FUNCTION
void WrapPos(const Real dmin[3], const Real dlen[3], const bool per[3], Real p[3]) {
  for (int d = 0; d < 3; ++d) {
    p[d] = nrpic::WrapCoord(p[d], dmin[d], dlen[d], per[d]);
  }
}

KOKKOS_INLINE_FUNCTION
void WrapDiff(const Real dlen[3], const bool per[3], const Real xa[3], const Real xb[3],
              Real dx[3]) {
  for (int d = 0; d < 3; ++d) {
    Real delta = xb[d] - xa[d];
    if (per[d] && dlen[d] > 0.0) {
      delta -= dlen[d] * round(delta / dlen[d]);
    }
    dx[d] = delta;
  }
}

KOKKOS_INLINE_FUNCTION
void Inv3GeomReg(const Real E_in[3][3], Real Einv_out[3][3]) {
  Real A[3][3];
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      A[i][j] = 0.5 * (E_in[i][j] + E_in[j][i]);
      Einv_out[i][j] = 0.0;
    }
  }
  const Real tr = A[0][0] + A[1][1] + A[2][2];
  if (tr <= 1.0e-300) return;

  const Real eps_tr = 1.0e-3 * tr;
  const Real A_chk[3][3] = {
    {A[0][0] - eps_tr, A[0][1], A[0][2]},
    {A[1][0], A[1][1] - eps_tr, A[1][2]},
    {A[2][0], A[2][1], A[2][2] - eps_tr}
  };
  if (!nrpic::vlasov::IsSpd3Fast(A_chk, 0.0)) {
    Real V_eig[3][3], evals[3];
    nrpic::SymEig3(A, V_eig, evals);
    const Real emin = fmin(evals[0], fmin(evals[1], evals[2]));
    const Real emax = fmax(evals[0], fmax(evals[1], evals[2]));
    if (emin <= 1.0e-3 * emax) {
      const Real reg = 1.0e-2 * tr;
      A[0][0] += reg;
      A[1][1] += reg;
      A[2][2] += reg;
    }
  }
  nrpic::Inv3Sym(A, Einv_out);
}

KOKKOS_INLINE_FUNCTION
int GridCellOf(const Real pos[3], const Real gmin[3], const Real inv_cdx[3], const int ng[3]) {
  int ix[3];
  for (int d = 0; d < 3; ++d) {
    int c = static_cast<int>(floor((pos[d] - gmin[d]) * inv_cdx[d]));
    if (c < 0) c = 0;
    if (c >= ng[d]) c = ng[d] - 1;
    ix[d] = c;
  }
  return (ix[2] * ng[1] + ix[1]) * ng[0] + ix[0];
}

KOKKOS_INLINE_FUNCTION
void GridCellIndices(const Real pos[3], const Real gmin[3], const Real inv_cdx[3],
                     const int ng[3], int ix[3]) {
  for (int d = 0; d < 3; ++d) {
    int c = static_cast<int>(floor((pos[d] - gmin[d]) * inv_cdx[d]));
    if (c < 0) c = 0;
    if (c >= ng[d]) c = ng[d] - 1;
    ix[d] = c;
  }
}

template <class ViewT>
inline auto ContigPtr(const ViewT &v) -> decltype(v.data()) {
  if (v.span() == 0) return static_cast<decltype(v.data())>(nullptr);
  if (!v.span_is_contiguous()) {
    std::cout << "### FATAL ERROR in " << __FILE__ << ": non-contiguous Vlasov View" << std::endl;
    std::exit(EXIT_FAILURE);
  }
  return v.data();
}

KOKKOS_INLINE_FUNCTION
int BinaryFindSorted(const DvceArray2D<int> &ids, int a, int cnt, int target) {
  int lo = 0, hi = cnt - 1;
  while (lo <= hi) {
    const int mid = lo + (hi - lo) / 2;
    const int v = ids(mid, a);
    if (v == target) return mid;
    if (v < target) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}

KOKKOS_INLINE_FUNCTION
int BinaryFindSortedPtr(const int *ids, int a, int N, int cnt, int target) {
  int lo = 0, hi = cnt - 1;
  while (lo <= hi) {
    const int mid = lo + (hi - lo) / 2;
    const int v = ids[static_cast<size_t>(mid) * N + a];
    if (v == target) return mid;
    if (v < target) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}

KOKKOS_INLINE_FUNCTION
void ComputeCellStencil(Real r_search, const Real inv_cdx[3], const int ng[3],
                        int lo[3], int hi[3], bool full[3]) {
  for (int d = 0; d < 3; ++d) {
    const int rad_d = static_cast<int>(floor(r_search * inv_cdx[d])) + 1;
    if (2 * rad_d + 1 >= ng[d]) {
      lo[d] = 0;
      hi[d] = ng[d] - 1;
      full[d] = true;
    } else {
      lo[d] = -rad_d;
      hi[d] = rad_d;
      full[d] = false;
    }
  }
}

KOKKOS_INLINE_FUNCTION
bool HasNonZeroGrad(const nrpic::AdmPoint &ap) {
  Real m = 0.0;
  for (int d = 0; d < 3; ++d) {
    m = fmax(m, fabs(ap.dalp[d]));
    for (int i = 0; i < 3; ++i) {
      m = fmax(m, fabs(ap.dbeta[d][i]));
      for (int j = 0; j < 3; ++j) {
        m = fmax(m, fabs(ap.dg[d][i][j]));
      }
    }
  }
  return m > 1.0e-12;
}

KOKKOS_INLINE_FUNCTION
bool IsNotMinkowski(const nrpic::AdmPoint &ap) {
  if (fabs(ap.alp - 1.0) > 1.0e-12) return true;
  for (int i = 0; i < 3; ++i) {
    if (fabs(ap.beta[i]) > 1.0e-12) return true;
    for (int j = 0; j < 3; ++j) {
      const Real tgt = (i == j) ? 1.0 : 0.0;
      if (fabs(ap.g[i][j] - tgt) > 1.0e-12) return true;
    }
  }
  return false;
}

KOKKOS_INLINE_FUNCTION
Real SymMinEig3(const Real A0[3][3], const Real dA[3][3], Real phi) {
  Real cand[3][3], Ve[3][3], ew[3];
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) cand[i][j] = A0[i][j] + phi * dA[i][j];
  }
  nrpic::SymEig3(cand, Ve, ew);
  return fmin(ew[0], fmin(ew[1], ew[2]));
}

template <int MaxNb>
KOKKOS_INLINE_FUNCTION
void ReconstructFaceSidePtr(
    int cell, int Nb, int N, const Real xf[3], const Real e_up[3][3],
    const Real *Dv, const Real *uv, const Real *Sv,
    const Real *gDv, const Real *guv, const Real *gSv,
    Real D_s[], Real u_t[][3], Real S_t[][3][3]) {
  for (int al = 0; al < Nb; ++al) {
    const size_t nsz = static_cast<size_t>(N);
    const size_t d_base = static_cast<size_t>(al) * 3 * nsz;
    Real D_r = Dv[static_cast<size_t>(al) * nsz + cell]
             + gDv[d_base + cell] * xf[0]
             + gDv[d_base + nsz + cell] * xf[1]
             + gDv[d_base + 2 * nsz + cell] * xf[2];
    if (D_r < 0.0) D_r = 0.0;
    D_s[al] = D_r;

    Real u_c[3], S_c6[N_SYM6], S_c[3][3];
    for (int i = 0; i < 3; ++i) {
      const size_t ub = (static_cast<size_t>(al) * 3 + i) * 3 * nsz;
      u_c[i] = uv[(static_cast<size_t>(al) * 3 + i) * nsz + cell]
             + guv[ub + cell] * xf[0]
             + guv[ub + nsz + cell] * xf[1]
             + guv[ub + 2 * nsz + cell] * xf[2];
    }
    for (int s = 0; s < N_SYM6; ++s) {
      const size_t sb = (static_cast<size_t>(al) * N_SYM6 + s) * 3 * nsz;
      S_c6[s] = Sv[(static_cast<size_t>(al) * N_SYM6 + s) * nsz + cell]
              + gSv[sb + cell] * xf[0]
              + gSv[sb + nsz + cell] * xf[1]
              + gSv[sb + 2 * nsz + cell] * xf[2];
    }
    UnpackSym6(S_c6, S_c);

    for (int m = 0; m < 3; ++m) {
      Real us = 0.0;
      for (int i = 0; i < 3; ++i) us += e_up[m][i] * u_c[i];
      u_t[al][m] = us;
      for (int n = 0; n < 3; ++n) {
        Real ss = 0.0;
        for (int i = 0; i < 3; ++i) {
          for (int j = 0; j < 3; ++j) ss += e_up[m][i] * S_c[i][j] * e_up[n][j];
        }
        S_t[al][m][n] = ss;
      }
    }
  }
}

KOKKOS_INLINE_FUNCTION
void AtomicAddTetFluxPtr(
    Real scale, const Real e_dn[3][3],
    int cell_src, int al_src, int cell_dst, int al_dst, int N,
    Real fm_t, const Real fp_t[3], const Real fpi_t[3][3], Real fe_t,
    Real *dm_v, Real *dP_v, Real *dPi_v, Real *dE_v) {
  const size_t nsz = static_cast<size_t>(N);
  const Real fm = scale * fm_t;
  const Real fe = scale * fe_t;
  Real fp[3] = {0.0, 0.0, 0.0}, fpi[3][3];
  for (int i = 0; i < 3; ++i) {
    for (int m = 0; m < 3; ++m) fp[i] += e_dn[m][i] * fp_t[m];
    fp[i] *= scale;
    for (int j = 0; j < 3; ++j) {
      Real s = 0.0;
      for (int m = 0; m < 3; ++m) {
        for (int n = 0; n < 3; ++n) s += e_dn[m][i] * fpi_t[m][n] * e_dn[n][j];
      }
      fpi[i][j] = scale * s;
    }
  }
  Real fpi6[N_SYM6];
  PackSym6(fpi, fpi6);
  if (fm != 0.0) {
    Kokkos::atomic_add(&dm_v[static_cast<size_t>(al_src) * nsz + cell_src], -fm);
    Kokkos::atomic_add(&dm_v[static_cast<size_t>(al_dst) * nsz + cell_dst],  fm);
  }
  for (int i = 0; i < 3; ++i) {
    if (fp[i] != 0.0) {
      Kokkos::atomic_add(&dP_v[(static_cast<size_t>(al_src) * 3 + i) * nsz + cell_src], -fp[i]);
      Kokkos::atomic_add(&dP_v[(static_cast<size_t>(al_dst) * 3 + i) * nsz + cell_dst],  fp[i]);
    }
  }
  for (int s = 0; s < N_SYM6; ++s) {
    if (fpi6[s] != 0.0) {
      Kokkos::atomic_add(&dPi_v[(static_cast<size_t>(al_src) * N_SYM6 + s) * nsz + cell_src], -fpi6[s]);
      Kokkos::atomic_add(&dPi_v[(static_cast<size_t>(al_dst) * N_SYM6 + s) * nsz + cell_dst],  fpi6[s]);
    }
  }
  if (fe != 0.0) {
    Kokkos::atomic_add(&dE_v[cell_src], -fe);
    Kokkos::atomic_add(&dE_v[cell_dst],  fe);
  }
}

struct KerrSchildLight {
  Real mass = 1.0, spin = 0.0;

  KOKKOS_INLINE_FUNCTION
  void EvalNoDeriv(const Real x[3], Real &alp, Real beta[3], Real g[3][3]) const {
    const Real a = spin;
    const Real a2 = a * a;
    const Real X = x[0], Y = x[1], Z = x[2];
    const Real b = X * X + Y * Y + Z * Z - a2;
    const Real r2 = 0.5 * (b + sqrt(b * b + 4.0 * a2 * Z * Z));
    const Real r = sqrt(r2);
    const Real r3 = r2 * r;
    const Real q = r2 * r2 + a2 * Z * Z;
    const Real H = mass * r3 / q;
    const Real s = r2 + a2;
    const Real l[3] = {(r * X + a * Y) / s, (r * Y - a * X) / s, Z / r};
    const Real f = 1.0 + 2.0 * H;
    alp = 1.0 / sqrt(f);
    const Real fac = 2.0 * H / f;
    for (int i = 0; i < 3; ++i) {
      beta[i] = fac * l[i];
      for (int j = 0; j < 3; ++j) {
        g[i][j] = ((i == j) ? 1.0 : 0.0) + 2.0 * H * l[i] * l[j];
      }
    }
  }
};

struct VlasovDomain {
  Real dmin[3];
  Real dlen[3];
  bool per[3];
};

struct VlasovGradPtrs {
  const int *act, *bnd, *ncnt, *nids, *pcnt, *pids, *ppab;
  const Real *x, *h, *Einv, *ub, *D, *u, *S;
  Real *gD, *gu, *gS;
  Real dlen[3], eps_v;
  int N, Nb;
  bool per[3];
};

struct VlasovFluxPtrs {
  const int *ea, *eb, *act, *gid, *ncnt, *nids;
  int *npab;
  const Real *x, *h, *V, *Einv, *m, *D, *u, *S, *gD, *gu, *gS, *cnv;
  Real *dm, *dP, *dPi, *dE;
  Real coll_sigma, noh_kappa;
  int N, Nb, basis_kind, n_perp, pair_mode;
  bool analytic_v;
};

struct VlasovKickPtrs {
  const int *act, *gid;
  const Real *x, *m;
  Real *P, *Pi, *u, *S;
  Real half_dt, tol;
  int N, Nb, n_q, slot_mode;
};

struct VlasovBgkPtrs {
  const int *act, *gid;
  const Real *x, *V, *m, *Ec;
  Real *P, *Pi, *u, *S;
  Real sigma_over_mu, dt_sub;
  int N, Nb, n_q, slot_mode;
  bool track_e;
};

template <class SizeViewT>
struct VlasovMetric {
  NrpicMetric msrc;
  bool is_static;
  Real mass, spin, lat_dx;
  Real dmin[3], dlen[3];
  bool per[3];
  nrpic::MeshMetric mesh_met;
  DvceArray5D<Real> mp_view;
  bool has_prev = false;
  Real dt_ratio = 1.0;
  SizeViewT sz;
  int nmb;
  int gids;

  KOKKOS_INLINE_FUNCTION
  void EvalMinkowski(nrpic::AdmPoint &ap) const {
    ap.alp = 1.0;
    for (int i = 0; i < 3; ++i) {
      ap.beta[i] = 0.0;
      ap.dalp[i] = 0.0;
      for (int j = 0; j < 3; ++j) {
        ap.g[i][j] = (i == j) ? 1.0 : 0.0;
        ap.dbeta[i][j] = 0.0;
        for (int k = 0; k < 3; ++k) ap.dg[i][j][k] = 0.0;
      }
    }
  }

  KOKKOS_INLINE_FUNCTION
  void GatherBlend3(int mb, Real wm1, Real w0, Real w1,
                    const Real pos[3], nrpic::AdmPoint &p) const {
    int ib[3];
    Real w[3][4], dw[3][4];
    const Real xmin[3] = {sz(mb).x1min, sz(mb).x2min, sz(mb).x3min};
    const Real idx[3]  = {1.0 / sz(mb).dx1, 1.0 / sz(mb).dx2, 1.0 / sz(mb).dx3};
    for (int d = 0; d < 3; ++d) {
      const Real xi = (pos[d] - xmin[d]) * idx[d] - 0.5;
      int i0 = mesh_met.ist[d] + static_cast<int>(floor(xi));
      i0 = (i0 < 1) ? 1 : i0;
      i0 = (i0 > mesh_met.ncell[d] - 3) ? (mesh_met.ncell[d] - 3) : i0;
      ib[d] = i0;
      if (mesh_met.bspline) {
        nrpic::BSplineWeights(xi - static_cast<Real>(i0 - mesh_met.ist[d]), w[d], dw[d]);
      } else {
        nrpic::HermiteWeights(xi - static_cast<Real>(i0 - mesh_met.ist[d]), w[d], dw[d]);
      }
      for (int n = 0; n < 4; ++n) dw[d][n] *= idx[d];
    }
    Real v[NRM_NVAR], dv[3][NRM_NVAR];
    for (int n = 0; n < NRM_NVAR; ++n) {
      v[n] = 0.0;
      dv[0][n] = 0.0; dv[1][n] = 0.0; dv[2][n] = 0.0;
    }
    const bool use_prev = has_prev && (wm1 != 0.0);
    for (int c = 0; c < 4; ++c) {
      const int k = ib[2] + c - 1;
      for (int b = 0; b < 4; ++b) {
        const int j = ib[1] + b - 1;
        const Real wyz = w[1][b] * w[2][c];
        const Real dwy = dw[1][b] * w[2][c];
        const Real dwz = w[1][b] * dw[2][c];
        for (int aa = 0; aa < 4; ++aa) {
          const int i = ib[0] + aa - 1;
          const Real ww  = w[0][aa] * wyz;
          const Real wdx = dw[0][aa] * wyz;
          const Real wdy = w[0][aa] * dwy;
          const Real wdz = w[0][aa] * dwz;
          for (int n = 0; n < NRM_NVAR; ++n) {
            const Real val = use_prev
                ? (wm1 * mp_view(mb, n, k, j, i) + w0 * mesh_met.m0(mb, n, k, j, i)
                   + w1 * mesh_met.m1(mb, n, k, j, i))
                : (w0 * mesh_met.m0(mb, n, k, j, i) + w1 * mesh_met.m1(mb, n, k, j, i));
            v[n]     += ww * val;
            dv[0][n] += wdx * val;
            dv[1][n] += wdy * val;
            dv[2][n] += wdz * val;
          }
        }
      }
    }
    p.alp = v[NRM_ALP];
    p.beta[0] = v[NRM_BX]; p.beta[1] = v[NRM_BY]; p.beta[2] = v[NRM_BZ];
    p.g[0][0] = v[NRM_GXX]; p.g[0][1] = v[NRM_GXY]; p.g[0][2] = v[NRM_GXZ];
    p.g[1][1] = v[NRM_GYY]; p.g[1][2] = v[NRM_GYZ]; p.g[2][2] = v[NRM_GZZ];
    p.g[1][0] = p.g[0][1]; p.g[2][0] = p.g[0][2]; p.g[2][1] = p.g[1][2];
    for (int d = 0; d < 3; ++d) {
      p.dalp[d] = dv[d][NRM_ALP];
      p.dbeta[d][0] = dv[d][NRM_BX];
      p.dbeta[d][1] = dv[d][NRM_BY];
      p.dbeta[d][2] = dv[d][NRM_BZ];
      p.dg[d][0][0] = dv[d][NRM_GXX]; p.dg[d][0][1] = dv[d][NRM_GXY];
      p.dg[d][0][2] = dv[d][NRM_GXZ]; p.dg[d][1][1] = dv[d][NRM_GYY];
      p.dg[d][1][2] = dv[d][NRM_GYZ]; p.dg[d][2][2] = dv[d][NRM_GZZ];
      p.dg[d][1][0] = p.dg[d][0][1]; p.dg[d][2][0] = p.dg[d][0][2];
      p.dg[d][2][1] = p.dg[d][1][2];
    }
  }

  KOKKOS_INLINE_FUNCTION
  int LocateMeshBlock(Real pos[3], int blk_hint) const {
    WrapPos(dmin, dlen, per, pos);
    int mb = nrpic::FindBlock(sz, nmb, blk_hint - gids, pos[0], pos[1], pos[2]);
    if (mb < 0) {
      Real clamped[3];
      for (int d = 0; d < 3; ++d) {
        const Real hi = dmin[d] + dlen[d];
        clamped[d] = (pos[d] < dmin[d]) ? (dmin[d] + 1.0e-12*dlen[d])
                   : ((pos[d] >= hi) ? (hi - 1.0e-12*dlen[d]) : pos[d]);
      }
      mb = nrpic::FindBlock(sz, nmb, blk_hint - gids, clamped[0], clamped[1], clamped[2]);
      for (int d = 0; d < 3; ++d) pos[d] = clamped[d];
    }
    return mb;
  }

  // slot_mode: 0 -> t^n, 1 -> t^{n+1}, 2 -> midpoint 0.5*(t^n + t^{n+1})
  KOKKOS_INLINE_FUNCTION
  void operator()(int slot_mode, const Real pos_in[3], int blk_hint, nrpic::AdmPoint &ap) const {
    Real pos[3] = {pos_in[0], pos_in[1], pos_in[2]};
    if (msrc == NrpicMetric::mesh) {
      const int mb = LocateMeshBlock(pos, blk_hint);
      if (mb < 0) {
        EvalMinkowski(ap);
        return;
      }
      nrpic::MeshMetric met = mesh_met;
      met.m = mb;
      met.xmin[0] = sz(mb).x1min; met.xmin[1] = sz(mb).x2min; met.xmin[2] = sz(mb).x3min;
      met.idx[0]  = 1.0/sz(mb).dx1; met.idx[1] = 1.0/sz(mb).dx2; met.idx[2] = 1.0/sz(mb).dx3;
      if (slot_mode == 1 || is_static) {
        met(1, pos, ap);
      } else if (slot_mode == 0) {
        met(0, pos, ap);
      } else {
        GatherBlend3(mb, 0.0, 0.5, 0.5, pos, ap);
      }
    } else if (msrc == NrpicMetric::kerr_schild) {
      nrpic::KerrSchildCart met{mass, spin};
      met(0, pos, ap);
    } else if (msrc == NrpicMetric::kerr_schild_sph) {
      nrpic::KerrSchildSph met{mass, spin};
      met(0, pos, ap);
    } else if (msrc == NrpicMetric::boyer_lindquist) {
      nrpic::BoyerLindquist met{mass, spin};
      met(0, pos, ap);
    } else {
      nrpic::LatticeMetric<nrpic::KerrSchildCart> met{{mass, spin},
                                                      {0.0, 0.0, 0.0},
                                                      {lat_dx, lat_dx, lat_dx}};
      met(0, pos, ap);
    }
  }

  // Evaluate ADM at continuous time fraction c in [0, 1] across [t^n, t^{n+1}].
  KOKKOS_INLINE_FUNCTION
  void EvalFrac(Real c, const Real pos_in[3], int blk_hint, nrpic::AdmPoint &ap) const {
    if (msrc != NrpicMetric::mesh || is_static) {
      operator()(0, pos_in, blk_hint, ap);
      return;
    }
    Real pos[3] = {pos_in[0], pos_in[1], pos_in[2]};
    const int mb = LocateMeshBlock(pos, blk_hint);
    if (mb < 0) {
      EvalMinkowski(ap);
      return;
    }
    if (has_prev) {
      const Real r = dt_ratio;
      const Real wm1 = (r * r * c * (c - 1.0)) / (1.0 + r);
      const Real w0  = (1.0 - c) * (1.0 + r * c);
      const Real w1  = (c * (1.0 + r * c)) / (1.0 + r);
      GatherBlend3(mb, wm1, w0, w1, pos, ap);
    } else {
      GatherBlend3(mb, 0.0, 1.0 - c, c, pos, ap);
    }
  }
};

// Adapter binding VlasovMetric + block hint to the pusher MetricT interface.
template <class SizeViewT>
struct BoundVlasovMetric {
  const VlasovMetric<SizeViewT> &parent;
  int blk_hint = 0;

  KOKKOS_INLINE_FUNCTION
  bool IsStatic() const { return parent.is_static || (parent.msrc != NrpicMetric::mesh); }

  KOKKOS_INLINE_FUNCTION
  void operator()(const int lev, const Real x[3], nrpic::AdmPoint &p) const {
    parent(lev, x, blk_hint, p);
  }

  KOKKOS_INLINE_FUNCTION
  void EvalAtFrac(Real frac, const Real x[3], nrpic::AdmPoint &p) const {
    parent.EvalFrac(frac, x, blk_hint, p);
  }
};

struct VlasovGridMeta {
  Real gmin[3] = {0.0, 0.0, 0.0};
  Real glen[3] = {1.0, 1.0, 1.0};
  Real inv_cdx[3] = {1.0, 1.0, 1.0};
  int ng[3] = {1, 1, 1};
  int n_cells = 1;
};

inline void VlasovFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in " << __FILE__ << ": " << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

struct VlasovReduceStats {
  int n_act = 0;
  Real h_max = 0.0;
  Real h_sum = 0.0;
  Real xmin = 1.0e300, ymin = 1.0e300, zmin = 1.0e300;
  Real xmax = -1.0e300, ymax = -1.0e300, zmax = -1.0e300;
};

template <class SizeViewT>
inline VlasovMetric<SizeViewT> BuildMetricHelper(Particles *pthis, MeshBlockPack *ppack,
                                                 const SizeViewT &sz) {
  VlasovMetric<SizeViewT> m;
  m.msrc      = pthis->nropt.metric;
  m.is_static = pthis->metric_is_static;
  m.mass      = pthis->nropt.mass;
  m.spin      = pthis->nropt.spin;
  m.lat_dx    = pthis->nropt.lattice_dx;
  for (int d = 0; d < 3; ++d) {
    m.dmin[d] = pthis->nropt.dom_min[d];
    m.dlen[d] = pthis->nropt.dom_len[d];
    m.per[d]  = pthis->nropt.periodic[d];
  }
  auto &indcs = ppack->pmesh->mb_indcs;
  m.mesh_met.bspline   = pthis->nropt.interp_bspline;
  m.mesh_met.m1        = m.mesh_met.bspline ? pthis->met1s : pthis->met1;
  m.mesh_met.m0        = m.is_static ? m.mesh_met.m1 : (m.mesh_met.bspline ? pthis->met0s : pthis->met0);
  m.mesh_met.is_static = m.is_static;
  m.mesh_met.ist[0]    = indcs.is;
  m.mesh_met.ist[1]    = indcs.js;
  m.mesh_met.ist[2]    = indcs.ks;
  m.mesh_met.ncell[0]  = indcs.nx1 + 2 * indcs.ng;
  m.mesh_met.ncell[1]  = indcs.nx2 + 2 * indcs.ng;
  m.mesh_met.ncell[2]  = indcs.nx3 + 2 * indcs.ng;
  if (pthis->vlv != nullptr &&
      pthis->vlv->opt.time_interp == VLASOV_TINTERP_QUADRATIC &&
      !m.is_static && pthis->vlv->met_prev_valid &&
      pthis->vlv->dt_prev > 0.0 && ppack->pmesh->dt > 0.0) {
    m.mp_view  = m.mesh_met.bspline ? pthis->met_prevs : pthis->met_prev;
    m.has_prev = true;
    m.dt_ratio = ppack->pmesh->dt / pthis->vlv->dt_prev;
  }
  m.sz   = sz;
  m.nmb  = ppack->nmb_thispack;
  m.gids = ppack->gids;
  return m;
}

template <class SizeViewT>
inline void UpdateBlockGIDs(VlasovState &st, const NrpicOptions &nropt, const SizeViewT &sz,
                            int nmb, int gids) {
  const int N = st.n_elem;
  if (N == 0 || nropt.metric != NrpicMetric::mesh) return;
  auto act  = st.active;
  auto xv   = st.x;
  auto gidv = st.blk_gid;
  const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3]  = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};

  par_for("vlasov_blk_gid", DevExeSpace(), 0, N - 1, KOKKOS_LAMBDA(const int a) {
    if (!act(a)) return;
    Real pos[3] = {xv(0, a), xv(1, a), xv(2, a)};
    WrapPos(dmin, dlen, per, pos);
    xv(0, a) = pos[0]; xv(1, a) = pos[1]; xv(2, a) = pos[2];
    const int mb = nrpic::FindBlock(sz, nmb, gidv(a) - gids, pos[0], pos[1], pos[2]);
    gidv(a) = (mb >= 0) ? (mb + gids) : -1;
  });
}

// Host functions implemented in vlasov_geometry.cpp
void AllocateState(VlasovState &st, int n_elem, int n_basis, int max_ngb);
void ResetMfmBuffers(VlasovState &st);
void GrowNeighborCapacity(VlasovState &st, int new_max_ngb);
VlasovGridMeta RebuildSpatialGrid(VlasovState &st, const NrpicOptions &nropt,
                                  const VlasovReduceStats &rs, Real h_scale);
VlasovReduceStats GatherStats(VlasovState &st);
void SeedHFromNearest(VlasovState &st, const NrpicOptions &nropt, const VlasovReduceStats &rs);
int FillNeighborsAndCount(VlasovState &st, const NrpicOptions &nropt,
                          const VlasovGridMeta &gm, bool fill_ids);
void UpdateGeometry(VlasovState &st, const NrpicOptions &nropt, bool build_neighbors,
                    Real cand_scale = 1.08);
void ConsToPrim(VlasovState &st);

// Host functions implemented in vlasov_mfm.cpp
void AdvanceMfmStep(Particles *pthis, MeshBlockPack *ppack);
void ExciseMfmState(Particles *pthis, MeshBlockPack *ppack);

// Host functions implemented in vlasov_scp.cpp
void InitializeScpOnMesh(Particles *pthis, MeshBlockPack *ppack);
void PushScpPackets(Particles *pthis, MeshBlockPack *ppack);

}  // namespace nrpic_vlasov_detail
}  // namespace particles

#endif  // PARTICLES_VLASOV_VLASOV_TYPES_HPP_
