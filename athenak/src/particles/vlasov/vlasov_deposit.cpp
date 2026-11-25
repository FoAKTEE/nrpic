//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_deposit.cpp
//! \brief Stress-energy T_{mu nu} cloud deposition for GR-LBV MFM basis states.

#include <cmath>

#include "athena.hpp"
#include "mesh/mesh.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_mesh.hpp"
#include "particles/nrpic_cloud.hpp"
#include "particles/vlasov/vlasov_types.hpp"
#include "z4c/tmunu.hpp"

namespace particles {

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
        const Real nc = ep(mo, k - cg.ks, j - cg.js, i - cg.is);
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

}  // namespace particles

