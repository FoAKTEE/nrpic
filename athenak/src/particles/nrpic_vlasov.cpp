//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_vlasov.cpp
//! \brief Direct 6+1D General-Relativistic Lagrangian-Basis Vlasov (GR-LBV) solver inside
//! NRPIC (<particles> pusher = vlasov_mfm).
//!
//! Architecture on GPU/CPU (Kokkos):
//!   - Physical state lives on meshless moving finite-volume elements a = 0 .. N-1,
//!     each carrying N_b <= MAX_BASIS covariant velocity basis distributions
//!     (m_{a,alpha}, P_{a,alpha,i}, Pi_{a,alpha,ij}) in 3+1 Eulerian Valencia form.
//!   - Strang-split advance over each step [t^n, t^{n+1}]:
//!       1. Half-kick (dt/2) via 27-point (or 1-point cold) cubature geodesic push
//!          using metric at t^n.
//!       2. Subcycled CFL-limited SSP-RK2 MFM advection + Anderson-Witting relativistic
//!          BGK + adaptive HLLC shock capture using midpoint metric 0.5*(g^n + g^{n+1}).
//!       3. Half-kick (dt/2) via cubature geodesic push using metric at t^{n+1}.
//!   - Source deposition onto T_{mu nu} reuses nrpic::CloudWeights + nrpic::CloudDeposit
//!     over cubature points of each basis, automatically inheriting AthenaK's filtering,
//!     1/sqrt(gamma), Lambda, and Z4c constraint evaluation.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <limits>
#include <string>
#include <utility>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "driver/driver.hpp"
#include "coordinates/adm.hpp"
#include "z4c/tmunu.hpp"
#include "z4c/z4c.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_metrics.hpp"
#include "particles/nrpic_mesh.hpp"
#include "particles/nrpic_cloud.hpp"
#include "particles/nrpic_vlasov_kernels.hpp"
#include "particles/nrpic_vlasov.hpp"
// last: this header defines the macro NDIM, which collides with a member of Tmunu
#include "z4c/fastflow.hpp"

namespace particles {
namespace nrpic_vlasov_detail {

//----------------------------------------------------------------------------------------
// Small inline math & packing helpers for Kokkos kernels
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

  // slot_mode: 0 -> t^n, 1 -> t^{n+1}, 2 -> midpoint 0.5*(t^n + t^{n+1})
  KOKKOS_INLINE_FUNCTION
  void operator()(int slot_mode, const Real pos_in[3], int blk_hint, nrpic::AdmPoint &ap) const {
    Real pos[3] = {pos_in[0], pos_in[1], pos_in[2]};
    if (msrc == NrpicMetric::mesh) {
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
        nrpic::AdmPoint aq;
        met(0, pos, ap);
        met(1, pos, aq);
        nrpic::AverageAdm(ap, aq);
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

  // Pass 1: Symmetric gather-scatter over per-element stencil r < 2 * h_a
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

  // Pass 2: Reduce max neighbor count and sort ascending (local stack buffer when cnt <= 64)
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
                    Real cand_scale = 1.08) {
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

  // Step 1: Build single 1.05x mean-h spatial hash grid, converge h_a^3 * nbar_a = 1, V_a, Einv_a, is_bnd_a
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

      // Single stencil walk caching candidates within r < r_cand_max, then Newton-solve h_a
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

  // Build unique unordered edge list a < b
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
    const int nb = p.Nb;
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

      // Fused scalar BJ (D), velocity-crossing BJ (u_bar), componentwise BJ + SPD (Sigma) limiter
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

void ComputeGradients(VlasovState &st, const NrpicOptions &nropt) {
  if (st.n_basis <= 1) ComputeGradientsImpl<1>(st, nropt);
  else                 ComputeGradientsImpl<nrpic::vlasov::MAX_BASIS>(st, nropt);
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
    // Swap current neighbor->pair table into prev_* zero-copy
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

template <class SizeViewT>
void UpdateBlockGIDs(VlasovState &st, const NrpicOptions &nropt, const SizeViewT &sz,
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
VlasovMetric<SizeViewT> BuildMetricHelper(Particles *pthis, MeshBlockPack *ppack,
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
  m.sz   = sz;
  m.nmb  = ppack->nmb_thispack;
  m.gids = ppack->gids;
  return m;
}

template <class SizeViewT>
void ApplyMfmStep(VlasovState &st, const NrpicOptions &nropt,
                  const VlasovMetric<SizeViewT> &met, Real dt_sub, int slot_mode) {
  const int N  = st.n_elem;
  const int Nb = st.n_basis;
  const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3]  = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};

  // Snapshot x0, m0, P0, Pi0
  Kokkos::deep_copy(DevExeSpace(), st.x0,  st.x);
  Kokkos::deep_copy(DevExeSpace(), st.m0,  st.m);
  Kokkos::deep_copy(DevExeSpace(), st.P0,  st.P);
  Kokkos::deep_copy(DevExeSpace(), st.Pi0, st.Pi);
  if (st.opt.coll_sigma > 0.0 && st.opt.bgk_track_e) {
    ComputeEnergyArray(st, nropt, met, slot_mode, st.E0);
  }

  // Stage 1
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

  // Stage 2 (SSP-RK2: u^{n+1} = 0.5*u0 + 0.5*(u^{(1)} + dt*R(u^{(1)})))
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

}  // namespace nrpic_vlasov_detail

//----------------------------------------------------------------------------------------
//! \fn Particles::NrpicVlasovInit / NrpicVlasovFree
//----------------------------------------------------------------------------------------

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
  opt.scp_rotate = pin->GetOrAddBoolean("particles", "vlasov_scp_rotate", true);

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

  opt.packet_mode = (opt.solver_mode == VLASOV_MODE_SCP) ||
                    (opt.solver_mode == VLASOV_MODE_HYBRID && opt.coll_sigma <= 0.0);
  if (nr_multirank && !opt.packet_mode) {
    nrpic_vlasov_detail::VlasovFatal("GR-LBV MFM mode currently requires a single MPI rank");
  }

  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC Vlasov (GR-LBV): mode=" << mode_s
              << (opt.packet_mode ? " [SCP-packet]" : " [AP-MFM]")
              << ", basis=" << basis_s
              << ", pair=" << pmode
              << ", scp_q=" << opt.scp_n_q
              << ", scp_rotate=" << (opt.scp_rotate ? "true" : "false")
              << ", coll_sigma=" << opt.coll_sigma
              << ", noh_kappa=" << opt.noh_kappa
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

//----------------------------------------------------------------------------------------
//! \fn Particles::NrpicVlasovLoadFile
//! \brief Reads GRLBV001 binary initial condition file
//----------------------------------------------------------------------------------------

void Particles::NrpicVlasovLoadFile(const std::string &fname) {
  if (vlv == nullptr) nrpic_vlasov_detail::VlasovFatal("NrpicVlasovLoadFile called before NrpicVlasovInit");
  if (fname.empty()) nrpic_vlasov_detail::VlasovFatal("<particles> pusher=vlasov_mfm requires particle_file");

  std::FILE *fp = std::fopen(fname.c_str(), "rb");
  if (fp == nullptr) nrpic_vlasov_detail::VlasovFatal("cannot open GRLBV file " + fname);
  char magic[9] = {0};
  std::int64_t n64 = 0, nb64 = 0;
  double tfile = 0.0;
  if (std::fread(magic, 1, 8, fp) != 8 || std::strncmp(magic, "GRLBV001", 8) != 0) {
    nrpic_vlasov_detail::VlasovFatal("bad magic in GRLBV file " + fname + " (expected GRLBV001)");
  }
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

//----------------------------------------------------------------------------------------
//! \fn Particles::NrpicVlasovInitializeOnMesh
//----------------------------------------------------------------------------------------

void Particles::NrpicVlasovInitializeOnMesh() {
  if (vlv == nullptr) return;

  if (vlv->opt.packet_mode) {
    if (vlv->initialized) {
      if (nropt.metric == NrpicMetric::mesh) {
        NrpicAssignBlocks();
        NrpicRemoveFlagged();
      }
      return;
    }
    if (nprtcl_thispack > 0 && vlv->n_elem == 0) {
      if (nropt.metric == NrpicMetric::mesh) {
        NrpicAssignBlocks();
        NrpicRemoveFlagged();
      }
      vlv->initialized = true;
      return;
    }
    const int N  = vlv->n_elem;
    const int Nb = vlv->n_basis;
    if (N == 0) {
      vlv->initialized = true;
      return;
    }
    auto hx  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->x);
    auto hm  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->m);
    auto hu  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->u_bar);
    auto hS  = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->Sigma);
    auto hsp = Kokkos::create_mirror_view_and_copy(HostMemSpace(), vlv->species);

    Real xi_rule[27][3], w_rule[27];
    int n_pts_warm = 0;
    nrpic::vlasov::StroudCubatureRule(vlv->opt.scp_n_q, vlv->opt.basis_kind,
                                       xi_rule, w_rule, n_pts_warm);

    int n_pkt = 0;
    for (int a = 0; a < N; ++a) {
      for (int al = 0; al < Nb; ++al) {
        if (hm(al, a) <= 0.0) continue;
        const Real trS = hS(al, SYM_XX, a) + hS(al, SYM_YY, a) + hS(al, SYM_ZZ, a);
        n_pkt += (trS <= 1.0e-26) ? 1 : n_pts_warm;
      }
    }

    SetNumberOfParticles(n_pkt);
    HostArray2D<Real> rh("rh", nrdata, n_pkt);
    HostArray2D<int>  ih("ih", nidata, n_pkt);
    const int gids = pmy_pack->gids;
    const bool do_rot = vlv->opt.scp_rotate;

    int p = 0;
    for (int a = 0; a < N; ++a) {
      const Real xa[3] = {hx(0, a), hx(1, a), hx(2, a)};
      for (int al = 0; al < Nb; ++al) {
        const Real ma = hm(al, a);
        if (ma <= 0.0) continue;
        const Real u_c[3] = {hu(al, 0, a), hu(al, 1, a), hu(al, 2, a)};
        const Real s6[6] = {
          hS(al, SYM_XX, a), hS(al, SYM_XY, a), hS(al, SYM_XZ, a),
          hS(al, SYM_YY, a), hS(al, SYM_YZ, a), hS(al, SYM_ZZ, a)
        };
        const Real trS = s6[0] + s6[3] + s6[5];
        const int sp_val = (Nb > 1) ? al : hsp(a);
        if (trS <= 1.0e-26) {
          rh(IPX, p) = xa[0]; rh(IPY, p) = xa[1]; rh(IPZ, p) = xa[2];
          rh(IPVX, p) = u_c[0]; rh(IPVY, p) = u_c[1]; rh(IPVZ, p) = u_c[2];
          rh(IPM, p) = ma;
          rh(IPTAU, p) = 0.0;
          ih(PGID, p) = gids;
          ih(PTAG, p) = p;
          ih(PSP, p) = sp_val;
          ih(PPERI, p) = 0;
          ++p;
        } else {
          Real Sig[3][3], L[3][3];
          nrpic_vlasov_detail::UnpackSym6(s6, Sig);
          nrpic::vlasov::Chol3Safe(Sig, L);
          Real R[3][3];
          if (do_rot) {
            nrpic::vlasov::HaltonSO3(a * Nb + al, R);
          } else {
            for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) R[i][j] = (i == j) ? 1.0 : 0.0;
          }
          Real LR[3][3];
          for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
              LR[i][j] = L[i][0]*R[0][j] + L[i][1]*R[1][j] + L[i][2]*R[2][j];
            }
          }
          for (int q = 0; q < n_pts_warm; ++q) {
            rh(IPX, p) = xa[0]; rh(IPY, p) = xa[1]; rh(IPZ, p) = xa[2];
            rh(IPVX, p) = u_c[0] + LR[0][0]*xi_rule[q][0] + LR[0][1]*xi_rule[q][1] + LR[0][2]*xi_rule[q][2];
            rh(IPVY, p) = u_c[1] + LR[1][0]*xi_rule[q][0] + LR[1][1]*xi_rule[q][1] + LR[1][2]*xi_rule[q][2];
            rh(IPVZ, p) = u_c[2] + LR[2][0]*xi_rule[q][0] + LR[2][1]*xi_rule[q][1] + LR[2][2]*xi_rule[q][2];
            rh(IPM, p) = ma * w_rule[q];
            rh(IPTAU, p) = 0.0;
            ih(PGID, p) = gids;
            ih(PTAG, p) = p;
            ih(PSP, p) = sp_val;
            ih(PPERI, p) = 0;
            ++p;
          }
        }
      }
    }
    Kokkos::deep_copy(prtcl_rdata, rh);
    Kokkos::deep_copy(prtcl_idata, ih);
    nrpic_vlasov_detail::ResetMfmBuffers(*vlv);
    if (nropt.metric == NrpicMetric::mesh) {
      NrpicAssignBlocks();
      NrpicRemoveFlagged();
    }
    vlv->initialized = true;
    if (global_variable::my_rank == 0) {
      std::cout << "NRPIC Vlasov SCP: expanded " << N << " elements (Nb=" << Nb
                << ") into " << n_pkt << " symplectic packets (q=" << vlv->opt.scp_n_q
                << ", rotate=" << (do_rot ? "true" : "false") << ")" << std::endl;
    }
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

  // Two geometry passes on startup ensure h^3 * nbar = 1 is fully converged even if
  // seed h adjusted significantly
  nrpic_vlasov_detail::UpdateGeometry(*vlv, nropt, false, 1.8);
  nrpic_vlasov_detail::UpdateGeometry(*vlv, nropt, true,  1.2);
  nrpic_vlasov_detail::ConsToPrim(*vlv);

  // Detect static zero-grad / Minkowski mesh once at startup
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

//----------------------------------------------------------------------------------------
//! \fn Particles::NrpicVlasovPush
//----------------------------------------------------------------------------------------

void Particles::NrpicVlasovPush() {
  if (vlv == nullptr || vlv->n_elem == 0) return;
  Mesh *pm = pmy_pack->pmesh;
  const Real dt = pm->dt;
  if (dt <= 0.0) return;

  auto sz  = pmy_pack->pmb->mb_size.d_view;
  nrpic_vlasov_detail::UpdateBlockGIDs(*vlv, nropt, sz, pmy_pack->nmb_thispack, pmy_pack->gids);
  auto met = nrpic_vlasov_detail::BuildMetricHelper(this, pmy_pack, sz);

  const bool static_met = metric_is_static || (nropt.metric != NrpicMetric::mesh);
  auto compute_nsub = [&](Real &max_sig_out) -> int {
    const Real dt_cfl_unit = nrpic_vlasov_detail::ComputeMinCflTime(*vlv, nropt, met, 2, max_sig_out);
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
    // Subcycled Strang kick-drift-kick on static / analytic spacetimes
    Real max_sig = 0.0;
    const int n_sub = compute_nsub(max_sig);
    const Real dt_sub = dt / static_cast<Real>(n_sub);
    for (int isub = 0; isub < n_sub; ++isub) {
      nrpic_vlasov_detail::ApplyGeodesicHalfKick(*vlv, nropt, met, 0.5 * dt_sub, 2);
      nrpic_vlasov_detail::ApplyMfmStep(*vlv, nropt, met, dt_sub, 2);
      nrpic_vlasov_detail::ApplyGeodesicHalfKick(*vlv, nropt, met, 0.5 * dt_sub, 2);
    }
  } else {
    // Step 1: Strang half-kick (dt/2) at fixed positions using metric at t^n (slot 0)
    nrpic_vlasov_detail::ApplyGeodesicHalfKick(*vlv, nropt, met, 0.5 * dt, 0);

    // Step 2: Determine CFL subcycling count using midpoint metric (slot 2)
    Real max_sig = 0.0;
    const int n_sub = compute_nsub(max_sig);
    const Real dt_sub = dt / static_cast<Real>(n_sub);

    for (int isub = 0; isub < n_sub; ++isub) {
      nrpic_vlasov_detail::ApplyMfmStep(*vlv, nropt, met, dt_sub, 2);
    }

    // Step 3: Strang half-kick (dt/2) at final positions using metric at t^{n+1} (slot 1)
    nrpic_vlasov_detail::ApplyGeodesicHalfKick(*vlv, nropt, met, 0.5 * dt, 1);
  }
  nrpic_vlasov_detail::ConsToPrim(*vlv);
}

//----------------------------------------------------------------------------------------
//! \fn Particles::NrpicVlasovExcise
//----------------------------------------------------------------------------------------

void Particles::NrpicVlasovExcise() {
  if (vlv == nullptr || vlv->n_elem == 0) return;

  acc_after_push = true;
  auto sz  = pmy_pack->pmb->mb_size.d_view;
  auto met = nrpic_vlasov_detail::BuildMetricHelper(this, pmy_pack, sz);

  const int N  = vlv->n_elem;
  const int Nb = vlv->n_basis;
  const bool mesh_metric = (nropt.metric == NrpicMetric::mesh);
  const Real alpha_exc   = nropt.alpha_exc;
  const int gids         = pmy_pack->gids;
  const int nmb          = pmy_pack->nmb_thispack;
  const bool is_kerr_cks = (nropt.metric == NrpicMetric::kerr_schild ||
                            nropt.metric == NrpicMetric::lattice);
  const bool is_kerr_sph = (nropt.metric == NrpicMetric::kerr_schild_sph ||
                            nropt.metric == NrpicMetric::boyer_lindquist);
  const Real bh_M        = nropt.mass;
  const Real bh_a        = nropt.spin;
  const Real r_plus      = bh_M + sqrt(fmax(bh_M * bh_M - bh_a * bh_a, 0.0));
  const Real r_exc_bl    = (vlv->opt.kerr_r_exc > 0.0 && (is_kerr_cks || is_kerr_sph))
                           ? (vlv->opt.kerr_r_exc * r_plus) : 0.0;

  int nah = 0;
  Real ahc[4][3], ahr2[4];
  for (int n = 0; n < 4; ++n) {
    ahc[n][0] = ahc[n][1] = ahc[n][2] = 0.0;
    ahr2[n] = 0.0;
  }
  if (mesh_metric && nropt.ah_exc_factor > 0.0 && pmy_pack->pz4c != nullptr) {
    for (auto &pah : pmy_pack->pz4c->pfastflow) {
      if (pah->ah_found && nah < 4 && Kokkos::isfinite(pah->rr_min) &&
          pah->rr_min > 0.0 && pah->rr_min < 4.0 * pah->initial_radius) {
        ahc[nah][0] = pah->center[0];
        ahc[nah][1] = pah->center[1];
        ahc[nah][2] = pah->center[2];
        ahr2[nah] = SQR(nropt.ah_exc_factor * pah->rr_min);
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

  const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3]  = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};

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
      nrpic_vlasov_detail::WrapPos(dmin, dlen, per, pos);
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
    n_escaped    += nesc;
    n_excised    += nexc;
    mass_escaped += mesc;
    mass_excised += mexc;
    nrpic_vlasov_detail::UpdateGeometry(*vlv, nropt, true);
  }
  acc_after_push = false;
}

//----------------------------------------------------------------------------------------
//! \fn Particles::NrpicVlasovDepositLoop
//! \brief Deposits integrated basis (E, P_i, S_ij) clouds into tm using nrpic::CloudDeposit
//----------------------------------------------------------------------------------------

void Particles::NrpicVlasovDepositLoop(const DvceArray5D<Real> &tm, Real &sum_mw_out) {
  if (vlv == nullptr || vlv->n_elem == 0) {
    sum_mw_out = 0.0;
    return;
  }
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  auto sz  = pmy_pack->pmb->mb_size.d_view;
  auto lev = pmy_pack->pmb->mb_lev.d_view;
  auto met = nrpic_vlasov_detail::BuildMetricHelper(this, pmy_pack, sz);

  nrpic::CloudGeometry cg;
  cg.nb = nropt.deposit_shape + 1;
  cg.is = indcs.is; cg.js = indcs.js; cg.ks = indcs.ks;
  cg.ie = indcs.ie; cg.je = indcs.je; cg.ke = indcs.ke;
  for (int d = 0; d < 3; ++d) {
    cg.dmin[d] = nropt.dom_min[d];
    cg.dlen[d] = nropt.dom_len[d];
    cg.per[d]  = nropt.periodic[d];
  }

  const int N          = vlv->n_elem;
  const int Nb         = vlv->n_basis;
  const int n_q        = vlv->opt.n_q_dep;
  const int gids       = pmy_pack->gids;
  const int nmb        = pmy_pack->nmb_thispack;
  const int lcap_max   = pm->root_level + nropt.deposit_max_level;
  const int lcap_min   = pm->root_level + nropt.deposit_min_level;
  const int root_lev   = pm->root_level;
  const bool adaptive  = nropt.deposit_adaptive;
  const bool have_prev = adaptive && e_prev_valid;
  const Real ppc_t     = nropt.deposit_ppc;
  const int max_coarsen = nropt.deposit_max_coarsen;
  const Real gmin[3]   = {pm->mesh_size.x1min, pm->mesh_size.x2min, pm->mesh_size.x3min};

  auto ep   = e_prev;
  auto act  = vlv->active;
  auto xv   = vlv->x;
  auto gidv = vlv->blk_gid;
  auto mv   = vlv->m;
  auto uv   = vlv->u_bar;
  auto Sv   = vlv->Sigma;

  Real smw = 0.0;
  Kokkos::parallel_reduce("vlasov_deposit", Kokkos::RangePolicy<DevExeSpace>(0, N),
  KOKKOS_LAMBDA(const int a, Real &lsmw) {
    if (!act(a)) return;
    Real xp[3] = {xv(0, a), xv(1, a), xv(2, a)};
    nrpic_vlasov_detail::WrapPos(cg.dmin, cg.dlen, cg.per, xp);

    int mo = nrpic::FindBlock(sz, nmb, gidv(a) - gids, xp[0], xp[1], xp[2]);
    if (mo < 0) return;
    gidv(a) = mo + gids;

    nrpic::AdmPoint ap;
    met(1, xp, mo + gids, ap);
    Real gi[3][3];
    nrpic::Inv3Sym(ap.g, gi);

    Real E_tot = 0.0;
    Real P_tot[3] = {0.0, 0.0, 0.0};
    Real S_tot[3][3] = {{0.0}};
    Real m_tot = 0.0;

    for (int al = 0; al < Nb; ++al) {
      const Real ma = mv(al, a);
      if (ma <= 0.0) continue;
      m_tot += ma;
      Real ua[3], s6[N_SYM6], Sa[3][3];
      for (int i = 0; i < 3; ++i) ua[i] = uv(al, i, a);
      for (int s = 0; s < N_SYM6; ++s) s6[s] = Sv(al, s, a);
      nrpic_vlasov_detail::UnpackSym6(s6, Sa);

      Real Ea = 0.0, Pa[3], S_a[3][3];
      nrpic::vlasov::BasisStressEnergy(ma, ua, Sa, gi, n_q, Ea, Pa, S_a);
      E_tot += Ea;
      for (int i = 0; i < 3; ++i) {
        P_tot[i] += Pa[i];
        for (int j = 0; j < 3; ++j) S_tot[i][j] += S_a[i][j];
      }
    }
    if (m_tot <= 0.0) return;
    lsmw += E_tot;

    Real q[Tmunu::N_Tmunu];
    q[Tmunu::I_Tmunu_Sxx] = S_tot[0][0];
    q[Tmunu::I_Tmunu_Sxy] = 0.5 * (S_tot[0][1] + S_tot[1][0]);
    q[Tmunu::I_Tmunu_Sxz] = 0.5 * (S_tot[0][2] + S_tot[2][0]);
    q[Tmunu::I_Tmunu_Syy] = S_tot[1][1];
    q[Tmunu::I_Tmunu_Syz] = 0.5 * (S_tot[1][2] + S_tot[2][1]);
    q[Tmunu::I_Tmunu_Szz] = S_tot[2][2];
    q[Tmunu::I_Tmunu_E]   = E_tot;
    q[Tmunu::I_Tmunu_Sx]  = P_tot[0];
    q[Tmunu::I_Tmunu_Sy]  = P_tot[1];
    q[Tmunu::I_Tmunu_Sz]  = P_tot[2];

    const int lev0 = lev(mo);
    Real h[3] = {sz(mo).dx1, sz(mo).dx2, sz(mo).dx3};
    int lcap = lcap_max;
    if (adaptive) {
      lcap = lcap_min;
      if (have_prev) {
        int i = cg.is + static_cast<int>(floor((xp[0] - sz(mo).x1min)/h[0]));
        int j = cg.js + static_cast<int>(floor((xp[1] - sz(mo).x2min)/h[1]));
        int k = cg.ks + static_cast<int>(floor((xp[2] - sz(mo).x3min)/h[2]));
        i = (i < cg.is) ? cg.is : ((i > cg.ie) ? cg.ie : i);
        j = (j < cg.js) ? cg.js : ((j > cg.je) ? cg.je : j);
        k = (k < cg.ks) ? cg.ks : ((k > cg.ke) ? cg.ke : k);
        const Real nc = ep(mo, k, j, i);
        if (nc > 0.0) {
          const Real dmin_ad = cbrt(ppc_t * E_tot / nc);
          const Real droot = h[0] * static_cast<Real>(1 << (lev0 - root_lev));
          int lv = root_lev + static_cast<int>(floor(log2(droot / dmin_ad)));
          lv = (lv < lcap_min) ? lcap_min : ((lv > lcap_max) ? lcap_max : lv);
          lcap = lv;
        }
      }
    }
    if (lcap < lev0 - max_coarsen) lcap = lev0 - max_coarsen;
    int ldep = lev0;
    const int nb_c = cg.nb;
    if (lev0 > lcap) {
      const Real fac = static_cast<Real>(1 << (lev0 - lcap));
      h[0] *= fac; h[1] *= fac; h[2] *= fac;
      ldep = lcap;
    } else {
      int lmax = lev0;
      Real xb0[3];
      for (int d = 0; d < 3; ++d) {
        const Real xi = (xp[d] - gmin[d])/h[d] - 0.5;
        const Real fl = (nb_c == 3) ? (floor(xi + 0.5) - 1.0)
                                    : ((nb_c == 4) ? (floor(xi) - 1.0) : floor(xi));
        xb0[d] = gmin[d] + (fl + 0.5) * h[d];
      }
      for (int c = 0; c < nb_c*nb_c*nb_c; ++c) {
        const int c1 = c % nb_c, c2 = (c / nb_c) % nb_c, c3 = c / (nb_c * nb_c);
        const Real xf = nrpic::WrapCoord(xb0[0] + c1*h[0], cg.dmin[0], cg.dlen[0], cg.per[0]);
        const Real yf = nrpic::WrapCoord(xb0[1] + c2*h[1], cg.dmin[1], cg.dlen[1], cg.per[1]);
        const Real zf = nrpic::WrapCoord(xb0[2] + c3*h[2], cg.dmin[2], cg.dlen[2], cg.per[2]);
        const int mb = nrpic::FindBlock(sz, nmb, mo, xf, yf, zf);
        if (mb >= 0 && lev(mb) > lmax) lmax = lev(mb);
      }
      lmax = (lmax > lcap) ? lcap : lmax;
      if (lmax > lev0) {
        const Real fac = 1.0 / static_cast<Real>(1 << (lmax - lev0));
        h[0] *= fac; h[1] *= fac; h[2] *= fac;
      }
      ldep = lmax;
    }

    Real xb[3], wt[3][4];
    nrpic::CloudWeights(nb_c, xp, gmin, h, xb, wt);
    nrpic::CloudDeposit(cg, sz, lev, nmb, mo, xb, wt, h, ldep, q, tm);
  }, Kokkos::Sum<Real>(smw));
  sum_mw_out = smw;
}

//----------------------------------------------------------------------------------------
//! \fn Particles::NrpicVlasovWriteHistory
//----------------------------------------------------------------------------------------

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

//----------------------------------------------------------------------------------------
//! \fn Particles::NrpicVlasovWriteSnapshot
//! \brief Writes live active elements to <basename>.vlasov.NNNNN.bin in GRLBV001 format
//----------------------------------------------------------------------------------------

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

//----------------------------------------------------------------------------------------
//! \fn Particles::NrpicVlasovWriteRestart / NrpicVlasovReadRestart
//----------------------------------------------------------------------------------------

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
