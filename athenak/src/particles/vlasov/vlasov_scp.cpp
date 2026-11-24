//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_scp.cpp
//! \brief Symplectic Cubature Packet (SCP) expansion (Stroud 8/14/27 & S^2 Lebedev
//! shells) and high-order geodesic pushers (GL4 / Midpoint / Boris with linear or
//! quadratic metric time interpolation).

#include <cmath>
#include <iostream>

#include "athena.hpp"
#include "globals.hpp"
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

void InitializeScpOnMesh(Particles *pthis, MeshBlockPack *ppack) {
  VlasovState *vlv = pthis->vlv;
  if (vlv == nullptr) return;
  if (vlv->initialized) {
    if (pthis->nropt.metric == NrpicMetric::mesh) {
      pthis->NrpicAssignBlocks();
      pthis->NrpicRemoveFlagged();
    }
    return;
  }
  if (pthis->nprtcl_thispack > 0 && vlv->n_elem == 0) {
    if (pthis->nropt.metric == NrpicMetric::mesh) {
      pthis->NrpicAssignBlocks();
      pthis->NrpicRemoveFlagged();
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

  const bool use_s2 = vlv->opt.scp_s2_shell;
  Real xi_rule[27][3], w_rule[27];
  int n_pts_warm = 0;
  if (use_s2) {
    Real dir[26][3], w_s2[26];
    nrpic::vlasov::SphericalCubatureRule(vlv->opt.scp_s2_q, dir, w_s2, n_pts_warm);
    const Real s3 = nrpic::vlasov::kSqrt3;
    for (int q = 0; q < n_pts_warm; ++q) {
      xi_rule[q][0] = s3 * dir[q][0];
      xi_rule[q][1] = s3 * dir[q][1];
      xi_rule[q][2] = s3 * dir[q][2];
      w_rule[q] = w_s2[q];
    }
  } else {
    nrpic::vlasov::StroudCubatureRule(vlv->opt.scp_n_q, vlv->opt.basis_kind,
                                       xi_rule, w_rule, n_pts_warm);
  }

  int n_pkt = 0;
  for (int a = 0; a < N; ++a) {
    for (int al = 0; al < Nb; ++al) {
      if (hm(al, a) <= 0.0) continue;
      const Real trS = hS(al, SYM_XX, a) + hS(al, SYM_YY, a) + hS(al, SYM_ZZ, a);
      n_pkt += (trS <= 1.0e-26) ? 1 : n_pts_warm;
    }
  }

  pthis->SetNumberOfParticles(n_pkt);
  HostArray2D<Real> rh("rh", pthis->nrdata, n_pkt);
  HostArray2D<int>  ih("ih", pthis->nidata, n_pkt);
  const int gids = ppack->gids;
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
        UnpackSym6(s6, Sig);
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
  Kokkos::deep_copy(pthis->prtcl_rdata, rh);
  Kokkos::deep_copy(pthis->prtcl_idata, ih);
  ResetMfmBuffers(*vlv);
  if (pthis->nropt.metric == NrpicMetric::mesh) {
    pthis->NrpicAssignBlocks();
    pthis->NrpicRemoveFlagged();
  }
  vlv->initialized = true;
  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC Vlasov SCP: expanded " << N << " elements (Nb=" << Nb
              << ") into " << n_pkt << " symplectic packets ("
              << (use_s2 ? "S2-shell q=" : "Stroud q=") << n_pts_warm
              << ", rotate=" << (do_rot ? "true" : "false") << ")" << std::endl;
  }
}

void PushScpPackets(Particles *pthis, MeshBlockPack *ppack) {
  Mesh *pm = ppack->pmesh;
  const int np = pthis->nprtcl_thispack;
  pthis->push_maxit = 0;
  pthis->push_unconverged = 0;
  if (np == 0) return;

  if (pthis->pert.on) { pthis->NrpicPerturbKick(pm->time, pm->time + 0.5 * pm->dt); }

  auto &pr = pthis->prtcl_rdata;
  auto &pi = pthis->prtcl_idata;
  auto sz  = ppack->pmb->mb_size.d_view;
  const VlasovOptions vopt = (pthis->vlv != nullptr) ? pthis->vlv->opt : VlasovOptions{};
  const int pkind     = vopt.scp_pusher;
  const int triad     = pthis->nropt.triad;
  const Real dt       = pm->dt;
  const Real tnow     = pm->time;
  const Real tol      = pthis->nropt.tol;
  const int maxit     = pthis->nropt.maxit;
  const NrpicMetric msrc = pthis->nropt.metric;
  const Real bh_mass  = pthis->nropt.mass;
  const Real bh_spin  = pthis->nropt.spin;
  const Real lat_dx   = pthis->nropt.lattice_dx;
  const Real alpha_exc = pthis->nropt.alpha_exc;
  const bool zm_null  = pthis->nropt.zero_mass_null;
  const Real r_plus   = bh_mass + sqrt(fmax(bh_mass*bh_mass - bh_spin*bh_spin, 0.0));
  const Real r_exc_bl =
      (vopt.kerr_r_exc > 0.0 &&
       (msrc == NrpicMetric::kerr_schild || msrc == NrpicMetric::lattice ||
        msrc == NrpicMetric::kerr_schild_sph || msrc == NrpicMetric::boyer_lindquist))
      ? (vopt.kerr_r_exc * r_plus) : 0.0;

  int nah = 0;
  Real ahc[4][3], ahr2[4];
  for (int n = 0; n < 4; ++n) {
    ahc[n][0] = ahc[n][1] = ahc[n][2] = 0.0;
    ahr2[n] = 0.0;
  }
  const bool mesh_metric = (msrc == NrpicMetric::mesh);
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

  auto vmet = BuildMetricHelper(pthis, ppack, sz);

  int nun = 0, mxit = 0;
  Kokkos::parallel_reduce("vlasov_scp_push", Kokkos::RangePolicy<DevExeSpace>(0, np),
  KOKKOS_LAMBDA(const int p, int &lnun, int &lmxit) {
    Real x[3] = {pr(IPX, p), pr(IPY, p), pr(IPZ, p)};
    Real u[3] = {pr(IPVX, p), pr(IPVY, p), pr(IPVZ, p)};
    const Real eps = (pr(IPM, p) > 0.0 || (pr(IPM, p) == 0.0 && !zm_null)) ? 1.0 : 0.0;
    if (pr(IPM, p) < 0.0 && tnow + 0.5 * dt < -pr(IPM, p)) return;
    const bool launch = (pr(IPM, p) < 0.0 && pr(IPTAU, p) == 0.0);
    Real dtau = 0.0;
    int it = 0;
    bool excise = false;
    int code = -2;

    if (mesh_metric) {
      const int gid_hint = pi(PGID, p);
      BoundVlasovMetric<decltype(sz)> met{vmet, gid_hint};
      if (launch) {
        nrpic::AdmPoint ap;
        met(0, x, ap);
        Real k[3] = {0.0, 0.0, 0.0};
        Real c2 = 0.0;
        for (int a = 0; a < 3; ++a) {
          for (int b = 0; b < 3; ++b) {
            k[a] += ap.g[a][b] * u[b];
            c2 += ap.g[a][b] * u[a] * u[b];
          }
        }
        const Real ic = 1.0 / sqrt(c2);
        u[0] = k[0] * ic; u[1] = k[1] * ic; u[2] = k[2] * ic;
      }
      if (alpha_exc > 0.0) {
        nrpic::AdmPoint ap;
        met(0, x, ap);
        excise = (ap.alp < alpha_exc);
      }
      for (int n = 0; n < nah; ++n) {
        const Real d2 = SQR(x[0] - ahc[n][0]) + SQR(x[1] - ahc[n][1]) + SQR(x[2] - ahc[n][2]);
        if (d2 < ahr2[n]) {
          if (!excise) code = -3;
          excise = true;
        }
      }
      if (!excise) {
        if (pkind == VLASOV_PUSH_GL4) {
          it = nrpic::vlasov::PushGL4(met, dt, tol, maxit, x, u, eps, dtau);
        } else if (pkind == VLASOV_PUSH_BORIS) {
          it = nrpic::PushBoris(met, triad, dt, tol, maxit, x, u);
        } else {
          it = nrpic::PushMidpoint(met, dt, tol, maxit, x, u, eps, dtau);
        }
      }
    } else {
      auto run_analytic = [&](const auto &met) {
        if (alpha_exc > 0.0) {
          nrpic::AdmPoint ap;
          met(0, x, ap);
          excise = (ap.alp < alpha_exc);
        }
        if (!excise) {
          if (pkind == VLASOV_PUSH_GL4) {
            it = nrpic::vlasov::PushGL4(met, dt, tol, maxit, x, u, eps, dtau);
          } else if (pkind == VLASOV_PUSH_BORIS) {
            it = nrpic::PushBoris(met, triad, dt, tol, maxit, x, u);
          } else {
            it = nrpic::PushMidpoint(met, dt, tol, maxit, x, u, eps, dtau);
          }
        }
      };
      if (msrc == NrpicMetric::kerr_schild) {
        run_analytic(nrpic::KerrSchildCart{bh_mass, bh_spin});
      } else if (msrc == NrpicMetric::kerr_schild_sph) {
        run_analytic(nrpic::KerrSchildSph{bh_mass, bh_spin});
      } else if (msrc == NrpicMetric::boyer_lindquist) {
        run_analytic(nrpic::BoyerLindquist{bh_mass, bh_spin});
      } else {
        run_analytic(nrpic::LatticeMetric<nrpic::KerrSchildCart>{
            {bh_mass, bh_spin}, {0.0, 0.0, 0.0}, {lat_dx, lat_dx, lat_dx}});
      }
    }

    if (it < 0) {
      lnun += 1;
      it = -it;
    }
    lmxit = (it > lmxit) ? it : lmxit;

    if (!excise && r_exc_bl > 0.0) {
      Real r_bl = 1.0e300;
      if (msrc == NrpicMetric::kerr_schild || msrc == NrpicMetric::lattice) {
        const Real a2 = bh_spin * bh_spin;
        const Real b = x[0]*x[0] + x[1]*x[1] + x[2]*x[2] - a2;
        const Real r2 = 0.5 * (b + sqrt(b*b + 4.0*a2*x[2]*x[2]));
        r_bl = sqrt(fmax(r2, 0.0));
      } else {
        r_bl = x[0];
      }
      if (r_bl < r_exc_bl) {
        code = -3;
        excise = true;
      }
    }

    const Real chk = x[0] + x[1] + x[2] + u[0] + u[1] + u[2];
    if (!(Kokkos::isfinite(chk))) {
      if (!excise) code = -4;
      excise = true;
    }
    if (excise) {
      pi(PGID, p) = code;
    } else {
      pr(IPX, p) = x[0]; pr(IPY, p) = x[1]; pr(IPZ, p) = x[2];
      pr(IPVX, p) = u[0]; pr(IPVY, p) = u[1]; pr(IPVZ, p) = u[2];
      pr(IPTAU, p) += dtau;
    }
  }, Kokkos::Sum<int>(nun), Kokkos::Max<int>(mxit));

  pthis->push_unconverged = nun;
  pthis->push_maxit = mxit;
  if (pthis->pert.on) { pthis->NrpicPerturbKick(pm->time + 0.5 * pm->dt, pm->time + pm->dt); }
  if (pthis->kick.on) { pthis->NrpicTestKick(); }
}

}  // namespace nrpic_vlasov_detail
}  // namespace particles

