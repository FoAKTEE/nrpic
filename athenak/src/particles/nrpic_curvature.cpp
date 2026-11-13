//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_curvature.cpp
//! \brief Kretschmann scalar I = R_abcd R^abcd of the spacetime from the 3+1 variables
//! and the deposited matter sources.  With the Gauss, Codazzi and Ricci equations,
//!   I = G_abcd G^abcd - 4 C_abc C^abc + 4 Z_ab Z^ab ,
//!   G_abcd = (3)R_abcd + K_ac K_bd - K_ad K_bc ,
//!   C_abc  = D_a K_bc - D_b K_ac ,
//!   Z_ab   = (3)R_ab + K K_ab - K_ac K^c_b - 8 pi [S_ab - gamma_ab (S - E)/2] ,
//! where the last line uses Einstein's equations for the projection with two normals.
//! In vacuum on a time-symmetric slice of Schwarzschild this gives 48 M^2/R^6.
//! The scalar is evaluated on the active cells at a given cadence; its maximum and the
//! maximum of the energy density go to <basename>.curv.hst, and the cells cut by a plane
//! y = const are written to <basename>.curv.NNNNN.bin.

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "coordinates/adm.hpp"
#include "coordinates/cell_locations.hpp"
#include "utils/finite_diff.hpp"
#include "z4c/z4c.hpp"
#include "z4c/tmunu.hpp"
#include "particles/particles.hpp"

namespace particles {

namespace {

//! Kretschmann scalar on the active cells of all MeshBlocks
template <int NGHOST>
void KretschmannKernel(MeshBlockPack *pmbp, DvceArray4D<Real> &kr) {
  auto &indcs = pmbp->pmesh->mb_indcs;
  auto &size = pmbp->pmb->mb_size;
  const int is = indcs.is, ie = indcs.ie;
  const int js = indcs.js, je = indcs.je;
  const int ks = indcs.ks, ke = indcs.ke;
  const int nmb1 = pmbp->nmb_thispack - 1;
  auto &adm = pmbp->padm->adm;
  const bool has_tm = (pmbp->ptmunu != nullptr);
  Tmunu::Tmunu_vars tmunu;
  if (has_tm) tmunu = pmbp->ptmunu->tmunu;
  auto kr_ = kr;

  par_for("nrpic_kretschmann", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    Real idx[] = {1/size.d_view(m).dx1, 1/size.d_view(m).dx2, 1/size.d_view(m).dx3};

    // metric, inverse, extrinsic curvature
    Real g[3][3], gu[3][3], K[3][3];
    for (int a=0; a<3; ++a) {
      for (int b=a; b<3; ++b) {
        g[a][b] = adm.g_dd(m,a,b,k,j,i);
        g[b][a] = g[a][b];
        K[a][b] = adm.vK_dd(m,a,b,k,j,i);
        K[b][a] = K[a][b];
      }
    }
    const Real det = adm::SpatialDet(g[0][0], g[0][1], g[0][2], g[1][1], g[1][2], g[2][2]);
    adm::SpatialInv(1.0/det, g[0][0], g[0][1], g[0][2], g[1][1], g[1][2], g[2][2],
                    &gu[0][0], &gu[0][1], &gu[0][2], &gu[1][1], &gu[1][2], &gu[2][2]);
    gu[1][0] = gu[0][1]; gu[2][0] = gu[0][2]; gu[2][1] = gu[1][2];

    // first derivatives dg[c][a][b] = d_c g_ab, dK[c][a][b] = d_c K_ab
    Real dg[3][3][3], dK[3][3][3];
    for (int c=0; c<3; ++c) {
      for (int a=0; a<3; ++a) {
        for (int b=a; b<3; ++b) {
          dg[c][a][b] = Dx<NGHOST>(c, idx, adm.g_dd, m, a, b, k, j, i);
          dg[c][b][a] = dg[c][a][b];
          dK[c][a][b] = Dx<NGHOST>(c, idx, adm.vK_dd, m, a, b, k, j, i);
          dK[c][b][a] = dK[c][a][b];
        }
      }
    }
    // second derivatives ddg[c][d][a][b] = d_c d_d g_ab
    Real ddg[3][3][3][3];
    for (int a=0; a<3; ++a) {
      for (int b=a; b<3; ++b) {
        for (int c=0; c<3; ++c) {
          ddg[c][c][a][b] = Dxx<NGHOST>(c, idx, adm.g_dd, m, a, b, k, j, i);
          ddg[c][c][b][a] = ddg[c][c][a][b];
          for (int d=c+1; d<3; ++d) {
            Real v = Dxy<NGHOST>(c, d, idx, adm.g_dd, m, a, b, k, j, i);
            ddg[c][d][a][b] = v; ddg[d][c][a][b] = v;
            ddg[c][d][b][a] = v; ddg[d][c][b][a] = v;
          }
        }
      }
    }
    // Christoffel symbols, Gl[e][a][b] = Gamma_eab, Gu[e][a][b] = Gamma^e_ab
    Real Gl[3][3][3], Gu[3][3][3];
    for (int e=0; e<3; ++e) {
      for (int a=0; a<3; ++a) {
        for (int b=0; b<3; ++b) {
          Gl[e][a][b] = 0.5*(dg[a][e][b] + dg[b][e][a] - dg[e][a][b]);
        }
      }
    }
    for (int e=0; e<3; ++e) {
      for (int a=0; a<3; ++a) {
        for (int b=0; b<3; ++b) {
          Gu[e][a][b] = gu[e][0]*Gl[0][a][b] + gu[e][1]*Gl[1][a][b] + gu[e][2]*Gl[2][a][b];
        }
      }
    }
    // Riemann tensor of the slice with all indices down, and the Gauss tensor
    //   R_abcd = (d_b d_c g_ad + d_a d_d g_bc - d_a d_c g_bd - d_b d_d g_ac)/2
    //          + Gamma_ebc Gamma^e_ad - Gamma_ebd Gamma^e_ac
    Real G4[3][3][3][3];
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) {
        for (int c=0; c<3; ++c) {
          for (int d=0; d<3; ++d) {
            Real r = 0.5*(ddg[b][c][a][d] + ddg[a][d][b][c] - ddg[a][c][b][d]
                          - ddg[b][d][a][c]);
            for (int e=0; e<3; ++e) {
              r += Gl[e][b][c]*Gu[e][a][d] - Gl[e][b][d]*Gu[e][a][c];
            }
            G4[a][b][c][d] = r + K[a][c]*K[b][d] - K[a][d]*K[b][c];
          }
        }
      }
    }
    // Ricci tensor of the slice, trace of K, mixed K^c_b
    Real Ric[3][3], Kmix[3][3];
    Real trK = 0.0;
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) {
        Real r = 0.0, km = 0.0;
        for (int c=0; c<3; ++c) {
          km += gu[a][c]*K[c][b];
          for (int d=0; d<3; ++d) {
            // gamma^cd R_cadb, with the K terms of the Gauss tensor removed again
            r += gu[c][d]*(G4[c][a][d][b] - K[c][d]*K[a][b] + K[c][b]*K[a][d]);
          }
        }
        Ric[a][b] = r;
        Kmix[a][b] = km;      // K^a_b
        trK += gu[a][b]*K[a][b];
      }
    }
    // matter sources
    Real E = 0.0, Smat[3][3], trS = 0.0;
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) { Smat[a][b] = 0.0; }
    }
    if (has_tm) {
      E = tmunu.E(m,k,j,i);
      for (int a=0; a<3; ++a) {
        for (int b=a; b<3; ++b) {
          Smat[a][b] = tmunu.S_dd(m,a,b,k,j,i);
          Smat[b][a] = Smat[a][b];
        }
      }
      for (int a=0; a<3; ++a) {
        for (int b=0; b<3; ++b) { trS += gu[a][b]*Smat[a][b]; }
      }
    }
    // Z_ab and C_abc
    Real Z[3][3], C[3][3][3];
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) {
        Real kk = 0.0;
        for (int c=0; c<3; ++c) { kk += K[a][c]*Kmix[c][b]; }
        Z[a][b] = Ric[a][b] + trK*K[a][b] - kk
                  - 8.0*M_PI*(Smat[a][b] - 0.5*g[a][b]*(trS - E));
        for (int c=0; c<3; ++c) {
          Real v = dK[a][b][c] - dK[b][a][c];
          for (int d=0; d<3; ++d) {
            v += -Gu[d][a][c]*K[b][d] + Gu[d][b][c]*K[a][d];
          }
          C[a][b][c] = v;
        }
      }
    }
    // contractions
    Real zz = 0.0;
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) {
        Real zu = 0.0;
        for (int c=0; c<3; ++c) {
          for (int d=0; d<3; ++d) { zu += gu[a][c]*gu[b][d]*Z[c][d]; }
        }
        zz += Z[a][b]*zu;
      }
    }
    Real cc = 0.0;
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) {
        for (int c=0; c<3; ++c) {
          Real cu = 0.0;
          for (int d=0; d<3; ++d) {
            for (int e=0; e<3; ++e) {
              const Real ge = gu[a][d]*gu[b][e];
              cu += ge*(gu[c][0]*C[d][e][0] + gu[c][1]*C[d][e][1] + gu[c][2]*C[d][e][2]);
            }
          }
          cc += C[a][b][c]*cu;
        }
      }
    }
    // G_abcd G^abcd: raise two index pairs in turn
    Real T1[3][3][3][3];      // G^ab_cd
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) {
        for (int c=0; c<3; ++c) {
          for (int d=0; d<3; ++d) {
            Real v = 0.0;
            for (int e=0; e<3; ++e) {
              for (int f=0; f<3; ++f) { v += gu[a][e]*gu[b][f]*G4[e][f][c][d]; }
            }
            T1[a][b][c][d] = v;
          }
        }
      }
    }
    Real gg = 0.0;
    for (int a=0; a<3; ++a) {
      for (int b=0; b<3; ++b) {
        for (int c=0; c<3; ++c) {
          for (int d=0; d<3; ++d) {
            // G^ab_cd G_ab^cd = T1[a][b][c][d] * T1[c][d][a][b] by the pair symmetry
            gg += T1[a][b][c][d]*T1[c][d][a][b];
          }
        }
      }
    }
    kr_(m,k,j,i) = gg - 4.0*cc + 4.0*zz;
  });
}

} // namespace

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicWriteCurvature
//! \brief evaluates the Kretschmann scalar and writes its maximum, the maximum of the
//! energy density, and the cut through the plane y = curv_plane_y

void Particles::NrpicWriteCurvature(Real time) {
  if (nropt.metric != NrpicMetric::mesh || pmy_pack->pz4c == nullptr) return;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int nmb = pmy_pack->nmb_thispack;
  const int n1 = indcs.nx1 + 2*indcs.ng;
  const int n2 = indcs.nx2 + 2*indcs.ng;
  const int n3 = indcs.nx3 + 2*indcs.ng;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;

  DvceArray4D<Real> kr("kretschmann", nmb, n3, n2, n1);
  switch (indcs.ng) {
    case 2: KretschmannKernel<2>(pmy_pack, kr); break;
    case 3: KretschmannKernel<3>(pmy_pack, kr); break;
    case 4: KretschmannKernel<4>(pmy_pack, kr); break;
  }

  // maxima of |I| and of E over the cells where the lapse exceeds the excision value
  // (the interior of a black hole is left out), with their locations
  auto m1 = met1;
  const Real amin = (nropt.alpha_exc > 0.0) ? nropt.alpha_exc : 0.0;
  const bool has_tm = nropt.deposit;
  DvceArray5D<Real> tm;
  if (has_tm) { tm = pmy_pack->ptmunu->u_tmunu; }
  const int ncell = nmb*nx3*nx2*nx1;
  using MaxLocT = Kokkos::MaxLoc<Real, int>;
  MaxLocT::value_type kmax, emax;
  kmax.val = 0.0; kmax.loc = 0;
  emax.val = 0.0; emax.loc = 0;
  Kokkos::parallel_reduce("nrpic_kmax", Kokkos::RangePolicy<DevExeSpace>(0, ncell),
  KOKKOS_LAMBDA(const int idx, MaxLocT::value_type &lk, MaxLocT::value_type &le) {
    int m = idx/(nx3*nx2*nx1);
    int rem = idx - m*(nx3*nx2*nx1);
    int k = rem/(nx2*nx1);
    rem -= k*(nx2*nx1);
    int j = rem/nx1;
    int i = rem - j*nx1;
    k += ks; j += js; i += is;
    if (m1(m,NRM_ALP,k,j,i) < amin) return;
    const Real v = fabs(kr(m,k,j,i));
    if (v > lk.val) { lk.val = v; lk.loc = idx; }
    if (has_tm) {
      const Real e = tm(m,Tmunu::I_Tmunu_E,k,j,i);
      if (e > le.val) { le.val = e; le.loc = idx; }
    }
  }, MaxLocT(kmax), MaxLocT(emax));
  if (!(kmax.val > 0.0)) { kmax.val = 0.0; kmax.loc = 0; }
  if (!(emax.val > 0.0)) { emax.val = 0.0; emax.loc = 0; }

  auto &size = pmy_pack->pmb->mb_size;
  auto locate = [&](const int idx, Real x[3]) {
    int m = idx/(nx3*nx2*nx1);
    int rem = idx - m*(nx3*nx2*nx1);
    int k = rem/(nx2*nx1);
    rem -= k*(nx2*nx1);
    int j = rem/nx1;
    int i = rem - j*nx1;
    x[0] = CellCenterX(i, nx1, size.h_view(m).x1min, size.h_view(m).x1max);
    x[1] = CellCenterX(j, nx2, size.h_view(m).x2min, size.h_view(m).x2max);
    x[2] = CellCenterX(k, nx3, size.h_view(m).x3min, size.h_view(m).x3max);
  };
  Real xk[3], xe[3];
  locate(kmax.loc, xk);
  locate(emax.loc, xe);

  std::string fname = nr_basename + ".curv.hst";
  std::FILE *fp = std::fopen(fname.c_str(), (curv_number == 0) ? "w" : "a");
  if (fp != nullptr) {
    if (curv_number == 0) {
      std::fprintf(fp, "# [1]=time [2]=max|I| [3]=x [4]=y [5]=z [6]=max E [7]=x [8]=y "
                   "[9]=z [10]=file number\n");
    }
    std::fprintf(fp, "%.15e %.15e %.8e %.8e %.8e %.15e %.8e %.8e %.8e %d\n", time,
                 kmax.val, xk[0], xk[1], xk[2], emax.val, xe[0], xe[1], xe[2],
                 curv_number);
    std::fclose(fp);
  }

  // cut through the plane y = curv_plane_y: records of 7 doubles
  // (x, z, dx, I, E, alpha, sqrt(gamma))
  if (nropt.curv_slice) {
    auto krh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), kr);
    auto mh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), m1);
    HostArray5D<Real> tmh;
    if (has_tm) {
      tmh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), tm);
    }
    std::vector<double> buf;
    const Real y0 = nropt.curv_plane_y;
    for (int m=0; m<nmb; ++m) {
      const auto &s = size.h_view(m);
      if (!(y0 >= s.x2min && y0 < s.x2max)) continue;
      int j = js + static_cast<int>(std::floor((y0 - s.x2min)/s.dx2));
      if (j > indcs.je) j = indcs.je;
      for (int k=ks; k<ks+nx3; ++k) {
        for (int i=is; i<is+nx1; ++i) {
          const Real det = adm::SpatialDet(mh(m,NRM_GXX,k,j,i), mh(m,NRM_GXY,k,j,i),
                                           mh(m,NRM_GXZ,k,j,i), mh(m,NRM_GYY,k,j,i),
                                           mh(m,NRM_GYZ,k,j,i), mh(m,NRM_GZZ,k,j,i));
          buf.push_back(CellCenterX(i-is, nx1, s.x1min, s.x1max));
          buf.push_back(CellCenterX(k-ks, nx3, s.x3min, s.x3max));
          buf.push_back(s.dx1);
          buf.push_back(krh(m,k,j,i));
          buf.push_back(has_tm ? tmh(m,Tmunu::I_Tmunu_E,k,j,i) : 0.0);
          buf.push_back(mh(m,NRM_ALP,k,j,i));
          buf.push_back(std::sqrt(det));
        }
      }
    }
    char number[24];
    std::snprintf(number, sizeof(number), ".curv.%05d.bin", curv_number);
    std::string sname = nr_basename + number;
    std::FILE *fs = std::fopen(sname.c_str(), "wb");
    if (fs != nullptr) {
      const char magic[9] = "NRPCURV1";
      double t = time;
      std::int64_t nrec = static_cast<std::int64_t>(buf.size()/7);
      std::fwrite(magic, 1, 8, fs);
      std::fwrite(&t, sizeof(double), 1, fs);
      std::fwrite(&nrec, sizeof(std::int64_t), 1, fs);
      if (!buf.empty()) std::fwrite(buf.data(), sizeof(double), buf.size(), fs);
      std::fclose(fs);
    }
  }
  curv_number++;
}

} // namespace particles
