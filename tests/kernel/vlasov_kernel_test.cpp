// Standalone unit & Python-parity test for nrpic_vlasov_kernels.hpp.
// Compile: g++ -O3 -std=c++17 -DNRPIC_STANDALONE -Iathenak/src/particles
//   tests/kernel/vlasov_kernel_test.cpp -o $SCRATCH_ROOT/vlasov_kernel_test -lm

#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <string>
#include <vector>

#include "nrpic_vlasov_kernels.hpp"
#include "nrpic_metrics.hpp"

using namespace nrpic;
using namespace nrpic::vlasov;

namespace {

bool CheckClose(Real a, Real b, Real rtol = 1e-12, Real atol = 1e-13) {
  return fabs(a - b) <= (atol + rtol * fabs(b));
}

void RunEvalTable(const std::string &in_path, const std::string &out_path) {
  std::ifstream fin(in_path);
  std::ofstream fout(out_path);
  fout << std::setprecision(17);

  std::string tag;
  while (fin >> tag) {
    if (tag == "THERMO") {
      Real theta;
      fin >> theta;
      Real z = 1.0 / theta;
      Real k2 = Kve2(z), k3 = Kve3(z);
      Real wm, hr, cs2, ga;
      SyngeThermo(theta, wm, hr, cs2, ga);
      Real th_inv = SafeMjThetaFromW(wm);
      Real vm = MjVmol(theta);
      fout << "THERMO " << theta << " " << k2 << " " << k3 << " "
           << wm << " " << hr << " " << cs2 << " " << ga << " "
           << th_inv << " " << vm << "\n";
    } else if (tag == "FLUX") {
      Real g[3][3], A[3], D_s, u_bar[3], Sig[3][3], alpha_f, beta_F;
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fin >> g[i][j];
      for (int i = 0; i < 3; ++i) fin >> A[i];
      fin >> D_s;
      for (int i = 0; i < 3; ++i) fin >> u_bar[i];
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fin >> Sig[i][j];
      fin >> alpha_f >> beta_F;
      Real normA, e_up[3][3], e_dn[3][3];
      bool ok = FaceTriad(g, A, normA, e_up, e_dn);
      assert(ok);
      Real Fm, FP[3], FPi[3][3], FE;
      OneSidedFluxCoord(D_s, u_bar, Sig, alpha_f, normA, e_up, e_dn, beta_F,
                        BASIS_TOPHAT, 3, Fm, FP, FPi, FE);
      fout << "FLUX " << normA << " " << Fm << " "
           << FP[0] << " " << FP[1] << " " << FP[2] << " " << FE;
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fout << " " << FPi[i][j];
      fout << "\n";
    } else if (tag == "BETAF") {
      int Na, Nb;
      fin >> Na >> Nb;
      Real Da[MAX_BASIS], Db[MAX_BASIS];
      Real ua[MAX_BASIS][3], ub[MAX_BASIS][3];
      Real Sa[MAX_BASIS][3][3], Sb[MAX_BASIS][3][3];
      for (int a = 0; a < Na; ++a) {
        fin >> Da[a];
        for (int i = 0; i < 3; ++i) fin >> ua[a][i];
        for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fin >> Sa[a][i][j];
      }
      for (int b = 0; b < Nb; ++b) {
        fin >> Db[b];
        for (int i = 0; i < 3; ++i) fin >> ub[b][i];
        for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fin >> Sb[b][i][j];
      }
      Real bF = SolveFaceBetaF(Na, Da, ua, Sa, Nb, Db, ub, Sb, BASIS_TOPHAT, 3);
      Real Ceb[MAX_BASIS][MAX_BASIS];
      PairingCostMatrix(Na, Da, ua, Sa, Nb, Db, ub, Sb, bF, Ceb);
      fout << "BETAF " << bF;
      for (int a = 0; a < Na; ++a) for (int b = 0; b < Nb; ++b) fout << " " << Ceb[a][b];
      fout << "\n";
    } else if (tag == "KICK") {
      AdmPoint adm0;
      fin >> adm0.alp;
      for (int i = 0; i < 3; ++i) fin >> adm0.beta[i];
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fin >> adm0.g[i][j];
      for (int i = 0; i < 3; ++i) fin >> adm0.dalp[i];
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fin >> adm0.dbeta[i][j];
      for (int k = 0; k < 3; ++k) for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fin >> adm0.dg[k][i][j];
      Real dt, u[3], Sig[3][3];
      fin >> dt;
      for (int i = 0; i < 3; ++i) fin >> u[i];
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fin >> Sig[i][j];
      Real unew[3], Snew[3][3];
      CubatureGeodesicKick(u, Sig, adm0, nullptr, dt, 3, unew, Snew);
      Real gi[3][3];
      Inv3Sym(adm0.g, gi);
      Real Eint, Pint[3], Sint[3][3];
      BasisStressEnergy(1.5, unew, Snew, gi, 3, Eint, Pint, Sint);
      fout << "KICK " << unew[0] << " " << unew[1] << " " << unew[2];
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fout << " " << Snew[i][j];
      fout << " " << Eint << " " << Pint[0] << " " << Pint[1] << " " << Pint[2];
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fout << " " << Sint[i][j];
      fout << "\n";
    } else if (tag == "BGK_HLLC") {
      int Nb;
      fin >> Nb;
      AdmPoint adm;
      fin >> adm.alp;
      for (int i = 0; i < 3; ++i) fin >> adm.beta[i];
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fin >> adm.g[i][j];
      for (int i = 0; i < 3; ++i) adm.dalp[i] = 0.0;
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) adm.dbeta[i][j] = 0.0;
      for (int k = 0; k < 3; ++k) for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) adm.dg[k][i][j] = 0.0;
      Real V_a, sig_mu, dt, beta_F;
      fin >> V_a >> sig_mu >> dt >> beta_F;
      Real m[MAX_BASIS], u[MAX_BASIS][3], S[MAX_BASIS][3][3];
      for (int al = 0; al < Nb; ++al) {
        fin >> m[al];
        for (int i = 0; i < 3; ++i) fin >> u[al][i];
        for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fin >> S[al][i][j];
      }
      Real u_out[MAX_BASIS][3], S_out[MAX_BASIS][3][3];
      MjBgkRelaxCell(Nb, m, u, S, V_a, adm, sig_mu, dt, 3, u_out, S_out);
      Real FD, FP[3], FPi[3][3], FE;
      Real DL[MAX_BASIS], DR[MAX_BASIS];
      for (int al = 0; al < Nb; ++al) {
        DL[al] = m[al] / V_a;
        DR[al] = 0.5 * m[al] / V_a;
      }
      RelHllcFluxTetrad(Nb, DL, u, S, Nb, DR, u_out, S_out, beta_F, false, FD, FP, FPi, FE);
      fout << "BGK_HLLC";
      for (int al = 0; al < Nb; ++al) {
        for (int i = 0; i < 3; ++i) fout << " " << u_out[al][i];
        for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fout << " " << S_out[al][i][j];
      }
      fout << " " << FD << " " << FP[0] << " " << FP[1] << " " << FP[2] << " " << FE;
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) fout << " " << FPi[i][j];
      fout << "\n";
    }
  }
}

void RunSelfTests() {
  // 1. Face triad orthonormality on curved metric
  const Real g[3][3] = {{1.5, 0.2, -0.1}, {0.2, 1.3, 0.15}, {-0.1, 0.15, 0.9}};
  const Real A[3] = {1.2, -0.7, 0.4};
  Real normA, e_up[3][3], e_dn[3][3];
  assert(FaceTriad(g, A, normA, e_up, e_dn));
  for (int a = 0; a < 3; ++a) {
    for (int b = 0; b < 3; ++b) {
      Real dot = MatVecDot3(e_up[a], g, e_up[b]);
      assert(CheckClose(dot, (a == b) ? 1.0 : 0.0, 1e-13, 1e-13));
    }
  }

  // 2. BGK lab-frame (m, P, E) exact conservation
  AdmPoint adm;
  adm.alp = 0.85;
  adm.beta[0] = 0.1; adm.beta[1] = -0.05; adm.beta[2] = 0.02;
  for (int i = 0; i < 3; ++i) {
    adm.dalp[i] = 0.0;
    for (int j = 0; j < 3; ++j) {
      adm.g[i][j] = g[i][j];
      adm.dbeta[i][j] = 0.0;
      for (int k = 0; k < 3; ++k) adm.dg[k][i][j] = 0.0;
    }
  }
  Real gi[3][3];
  Inv3Sym(adm.g, gi);
  const Real m[3] = {0.4, 0.35, 0.25};
  const Real u0[3][3] = {{1.2, 0.3, -0.2}, {-0.8, 0.5, 0.4}, {0.1, -0.6, 0.2}};
  const Real S0[3][3][3] = {
    {{0.3, 0.0, 0.0}, {0.0, 0.1, 0.0}, {0.0, 0.0, 0.05}},
    {{0.15, 0.0, 0.0}, {0.0, 0.4, 0.0}, {0.0, 0.0, 0.2}},
    {{0.08, 0.0, 0.0}, {0.0, 0.08, 0.0}, {0.0, 0.0, 0.25}}
  };
  Real E0 = 0.0, P0[3] = {0, 0, 0};
  for (int al = 0; al < 3; ++al) {
    Real ea, pa[3], sa[3][3];
    BasisStressEnergy(m[al], u0[al], S0[al], gi, 3, ea, pa, sa);
    E0 += ea;
    for (int i = 0; i < 3; ++i) P0[i] += pa[i];
  }
  Real u1[3][3], S1[3][3][3];
  MjBgkRelaxCell(3, m, u0, S0, 0.5, adm, 10.0, 0.5, 3, u1, S1);
  Real E1 = 0.0, P1[3] = {0, 0, 0};
  for (int al = 0; al < 3; ++al) {
    Real ea, pa[3], sa[3][3];
    BasisStressEnergy(m[al], u1[al], S1[al], gi, 3, ea, pa, sa);
    E1 += ea;
    for (int i = 0; i < 3; ++i) P1[i] += pa[i];
  }
  assert(fabs(E1 - E0) / E0 < 1e-13);
  for (int i = 0; i < 3; ++i) assert(fabs(P1[i] - P0[i]) < 1e-13);

  // 3. Synge thermodynamics sanity across ultra-cold -> ultra-relativistic
  const Real th_list[7] = {1e-7, 1e-4, 1e-2, 0.1, 1.0, 10.0, 1000.0};
  for (int i = 0; i < 7; ++i) {
    Real th = th_list[i], wm, hr, cs2, ga;
    SyngeThermo(th, wm, hr, cs2, ga);
    Real th_rec = SafeMjThetaFromW(wm);
    assert(fabs(th_rec - th) <= 1e-13 * wm + 1e-15);
    assert(cs2 >= 0.0 && cs2 <= 1.0 / 3.0 + 1e-15);
  }

  // 4. Exact Valencia Synge C2P + symmetric HLLC contact + stationary contact Noh zero
  {
    const Real D_ref = 2.4, th_ref = 0.25;
    Real wm_r, hr_r, cs2_r, ga_r;
    SyngeThermo(th_ref, wm_r, hr_r, cs2_r, ga_r);
    const Real v_ref[3] = {sqrt(1.0 - 1.0 / (1.5 * 1.5)) * 0.8, 0.25, -0.1};
    const Real v2_r = Dot3(v_ref, v_ref);
    const Real U0_r = 1.0 / sqrt(1.0 - v2_r);
    const Real rho0_r = D_ref / U0_r;
    const Real p_ref = rho0_r * th_ref;
    const Real DhU0 = D_ref * hr_r * U0_r;
    const Real E_ref = DhU0 - p_ref;
    const Real P_ref[3] = {DhU0 * v_ref[0], DhU0 * v_ref[1], DhU0 * v_ref[2]};
    Real th_o, h_o, cs2_o, wm_o, U0_o, rho0_o, p_o, v_o[3];
    ValenciaC2PSynge(D_ref, E_ref, P_ref, th_o, h_o, cs2_o, wm_o, U0_o, rho0_o, p_o, v_o);
    assert(CheckClose(th_o, th_ref, 1e-13, 1e-14));
    assert(CheckClose(U0_o, U0_r, 1e-13, 1e-14));
    assert(CheckClose(p_o, p_ref, 1e-13, 1e-14));
    for (int i = 0; i < 3; ++i) assert(CheckClose(v_o[i], v_ref[i], 1e-13, 1e-14));

    // Stationary contact (equal p and v=0, unequal density): zero Noh flux and zero HLLC mass flux
    HllcFluidState Lc, Rc;
    Lc.D = 3.0; Lc.p = 0.5; Lc.U0 = 1.0; Lc.rho0 = 3.0; Lc.theta = 0.5 / 3.0;
    SyngeThermo(Lc.theta, Lc.w_m, Lc.h, Lc.cs2, ga_r); Lc.valid = true;
    Rc.D = 1.0; Rc.p = 0.5; Rc.U0 = 1.0; Rc.rho0 = 1.0; Rc.theta = 0.5;
    SyngeThermo(Rc.theta, Rc.w_m, Rc.h, Rc.cs2, ga_r); Rc.valid = true;
    assert(fabs(NohThermalConductFlux(Lc, Rc, 0.5)) < 1e-15);

    const Real DL[1] = {1.0}, DR[1] = {1.0};
    const Real uL[1][3] = {{1.0, 0.0, 0.0}}, uR[1][3] = {{-1.0, 0.0, 0.0}};
    const Real SL[1][3][3] = {{{1e-8,0,0},{0,1e-8,0},{0,0,1e-8}}};
    const Real SR[1][3][3] = {{{1e-8,0,0},{0,1e-8,0},{0,0,1e-8}}};
    Real FD_s, FP_s[3], FPi_s[3][3], FE_s;
    RelHllcFluxTetrad(1, DL, uL, SL, 1, DR, uR, SR, 0.0, true, FD_s, FP_s, FPi_s, FE_s);
    assert(fabs(FD_s) < 1e-15 && fabs(FE_s) < 1e-15 && fabs(FP_s[1]) < 1e-15 && fabs(FP_s[2]) < 1e-15);
    assert(fabs(FPi_s[0][0]) < 1e-12);
  }

  // 5. Stroud degree-5 14-point & 8-point cubature moments + HaltonSO3 + IsSpd3Fast
  {
    Real xi[27][3], w[27];
    int n_pts = 0;
    for (int bkind = 0; bkind <= 1; ++bkind) {
      StroudCubatureRule(14, bkind, xi, w, n_pts);
      assert(n_pts == 14);
      Real m0 = 0.0, m1[3] = {0,0,0}, m2[3][3] = {{0}}, m3 = 0.0, m4_diag = 0.0, m4_off = 0.0;
      for (int q = 0; q < n_pts; ++q) {
        assert(w[q] > 0.0);
        m0 += w[q];
        m3 += w[q] * xi[q][0] * xi[q][1] * xi[q][2];
        m4_diag += w[q] * xi[q][0] * xi[q][0] * xi[q][0] * xi[q][0];
        m4_off  += w[q] * xi[q][0] * xi[q][0] * xi[q][1] * xi[q][1];
        for (int i = 0; i < 3; ++i) {
          m1[i] += w[q] * xi[q][i];
          for (int j = 0; j < 3; ++j) m2[i][j] += w[q] * xi[q][i] * xi[q][j];
        }
      }
      assert(CheckClose(m0, 1.0, 1e-14, 1e-14));
      for (int i = 0; i < 3; ++i) assert(fabs(m1[i]) < 1e-14);
      for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) {
        assert(CheckClose(m2[i][j], (i == j) ? 1.0 : 0.0, 1e-14, 1e-14));
      }
      assert(fabs(m3) < 1e-14);
      const Real target_m4d = (bkind == BASIS_GAUSS) ? 3.0 : 1.8;
      assert(CheckClose(m4_diag, target_m4d, 1e-14, 1e-14));
      assert(CheckClose(m4_off, 1.0, 1e-14, 1e-14));
    }
    Real R[3][3];
    HaltonSO3(17, R);
    for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) {
      Real dot = R[0][i]*R[0][j] + R[1][i]*R[1][j] + R[2][i]*R[2][j];
      assert(CheckClose(dot, (i == j) ? 1.0 : 0.0, 1e-14, 1e-14));
    }
    const Real detR = R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1])
                    - R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0])
                    + R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0]);
    assert(CheckClose(detR, 1.0, 1e-14, 1e-14));
    Real S_test[3][3] = {{0.2, 0.05, -0.02}, {0.05, 0.15, 0.03}, {-0.02, 0.03, 0.12}};
    assert(IsSpd3Fast(S_test, 0.0));
    Real S_bad[3][3] = {{0.2, 0.3, 0.0}, {0.3, 0.1, 0.0}, {0.0, 0.0, 0.1}};
    assert(!IsSpd3Fast(S_bad, 0.0));
  }

  // 6. S^2 SphericalCubatureRule exactness up to l = 7 (Q = 6, 12, 14, 26)
  {
    const int q_list[4] = {6, 12, 14, 26};
    for (int qi = 0; qi < 4; ++qi) {
      Real dir[26][3], w[26];
      int n_pts = 0;
      SphericalCubatureRule(q_list[qi], dir, w, n_pts);
      assert(n_pts == q_list[qi]);
      Real sum_w = 0.0, mu1[3] = {0.0, 0.0, 0.0};
      Real m2[3][3] = {{0}}, m3_xyz = 0.0, m5_x3yz = 0.0;
      Real m4_x4 = 0.0, m4_x2y2 = 0.0, m6_x6 = 0.0, m6_x4y2 = 0.0, m6_x2y2z2 = 0.0;
      for (int q = 0; q < n_pts; ++q) {
        assert(w[q] > 0.0);
        const Real x = dir[q][0], y = dir[q][1], z = dir[q][2];
        assert(CheckClose(x*x + y*y + z*z, 1.0, 1e-14, 1e-14));
        sum_w += w[q];
        mu1[0] += w[q]*x; mu1[1] += w[q]*y; mu1[2] += w[q]*z;
        m3_xyz += w[q]*x*y*z;
        m5_x3yz += w[q]*x*x*x*y*z;
        m4_x4 += w[q]*x*x*x*x;
        m4_x2y2 += w[q]*x*x*y*y;
        m6_x6 += w[q]*x*x*x*x*x*x;
        m6_x4y2 += w[q]*x*x*x*x*y*y;
        m6_x2y2z2 += w[q]*x*x*y*y*z*z;
        for (int a = 0; a < 3; ++a)
          for (int b = 0; b < 3; ++b)
            m2[a][b] += w[q] * dir[q][a] * dir[q][b];
      }
      assert(CheckClose(sum_w, 1.0, 1e-14, 1e-14));
      for (int a = 0; a < 3; ++a) {
        assert(fabs(mu1[a]) < 1e-14);
        for (int b = 0; b < 3; ++b)
          assert(CheckClose(m2[a][b], (a == b) ? (1.0/3.0) : 0.0, 1e-14, 1e-14));
      }
      assert(fabs(m3_xyz) < 1e-14);
      assert(fabs(m5_x3yz) < 1e-14);
      if (q_list[qi] >= 12) {
        assert(CheckClose(m4_x4, 1.0/5.0, 1e-14, 1e-14));
        assert(CheckClose(m4_x2y2, 1.0/15.0, 1e-14, 1e-14));
      }
      if (q_list[qi] == 26) {
        assert(CheckClose(m6_x6, 1.0/7.0, 1e-14, 1e-14));
        assert(CheckClose(m6_x4y2, 1.0/35.0, 1e-14, 1e-14));
        assert(CheckClose(m6_x2y2z2, 1.0/105.0, 1e-14, 1e-14));
      }
    }
  }

  // 7. PushGL4 vs PushMidpoint on Kerr a=0.9M, e=0.99 passage (exact problems/kerr/geodesic.athinput)
  {
    const Real a = 0.9;
    KerrSchildSph kss{1.0, a};
    auto eval_ELQ = [&](const Real x[3], const Real u[3], Real &E, Real &Lz, Real &Q) {
      AdmPoint ap;
      kss(0, x, ap);
      Real gi[3][3], uup[3];
      Inv3Sym(ap.g, gi);
      const Real W = LorentzFactor(gi, u, uup);
      E = ap.alp * W - (ap.beta[0]*u[0] + ap.beta[1]*u[1] + ap.beta[2]*u[2]);
      Lz = u[2];
      const Real ct = cos(x[1]), st = sin(x[1]);
      Q = u[1]*u[1] + ct*ct*(a*a*(1.0 - E*E) + Lz*Lz/(st*st));
    };
    const Real x0[3] = {20.0, 0.5 * kPi, 0.0};
    const Real u0[3] = {-0.20131797516752664, 1.4049911031746785, 2.4328};
    Real E0, Lz0, Q0;
    eval_ELQ(x0, u0, E0, Lz0, Q0);
    const Real tend = 230.0;
    const Real dts[5] = {0.16, 0.08, 0.04, 0.02, 0.01};
    Real dE_gl4[5], dQ_gl4[5], dE_mid[5], dQ_mid[5];
    for (int k = 0; k < 5; ++k) {
      const int nst = static_cast<int>(llround(tend / dts[k]));
      Real x[3] = {x0[0], x0[1], x0[2]}, u[3] = {u0[0], u0[1], u0[2]}, dtau = 0.0;
      Real max_dE = 0.0, max_dQ = 0.0;
      for (int s = 0; s < nst; ++s) {
        int it = PushGL4(kss, dts[k], 2.0e-14, 200, x, u, 1.0, dtau);
        assert(it > 0);
        Real E, Lz, Q;
        eval_ELQ(x, u, E, Lz, Q);
        max_dE = fmax(max_dE, fabs(E - E0));
        max_dQ = fmax(max_dQ, fabs(Q - Q0));
        assert(fabs(Lz - Lz0) < 1e-12);
      }
      dE_gl4[k] = max_dE;
      dQ_gl4[k] = max_dQ;

      Real xm[3] = {x0[0], x0[1], x0[2]}, um[3] = {u0[0], u0[1], u0[2]}, dm = 0.0;
      Real max_dEm = 0.0, max_dQm = 0.0;
      for (int s = 0; s < nst; ++s) {
        int it = PushMidpoint(kss, dts[k], 2.0e-14, 200, xm, um, 1.0, dm);
        assert(it > 0);
        Real E, Lz, Q;
        eval_ELQ(xm, um, E, Lz, Q);
        max_dEm = fmax(max_dEm, fabs(E - E0));
        max_dQm = fmax(max_dQm, fabs(Q - Q0));
      }
      dE_mid[k] = max_dEm;
      dQ_mid[k] = max_dQm;
    }
    const Real p_E_gl4 = log(dE_gl4[0] / dE_gl4[3]) / log(dts[0] / dts[3]);
    const Real p_Q_gl4 = log(dQ_gl4[0] / dQ_gl4[3]) / log(dts[0] / dts[3]);
    const Real p_E_mid = log(dE_mid[0] / dE_mid[3]) / log(dts[0] / dts[3]);
    std::printf("[TEST7 KERR e=0.99] p_E_gl4=%.3f p_Q_gl4=%.3f p_E_mid=%.3f | dt=0.01: "
                "dE_gl4=%.3e vs mid=%.3e, dQ_gl4=%.3e vs mid=%.3e\n",
                p_E_gl4, p_Q_gl4, p_E_mid, dE_gl4[4], dE_mid[4], dQ_gl4[4], dQ_mid[4]);
    assert(p_E_gl4 >= 3.95 && p_Q_gl4 >= 3.95);
    assert(p_E_mid >= 1.95 && p_E_mid <= 2.10);
    // At dt = 0.01 (index 4), GL4 beats Midpoint by >= 1e6x in E and >= 1e5x in Q
    assert(dE_mid[4] / fmax(dE_gl4[4], 1e-16) >= 1.0e6);
    assert(dQ_mid[4] / fmax(dQ_gl4[4], 1e-16) >= 1.0e5);
  }

  // 8. PushGL4 on time-varying metric: linear BlendAdm2 (p~2) vs 3-level quadratic (p>=2.95)
  {
    auto eval_exact_at_t = [](Real t, const Real x[3], AdmPoint &p) {
      const Real phia = 2.3 * t + 0.4 * x[0] - 0.3 * x[1];
      const Real phib = 1.9 * t + 0.25 * x[2];
      const Real phig = 2.7 * t + 0.15 * x[0] + 0.2 * x[1];
      const Real a2 = 0.22 * cos(phia) + 0.07 * sin(3.7 * t - 0.2 * x[2]);
      p.alp = 1.0 + a2;
      p.dalp[0] = -0.22 * 0.4 * sin(phia);
      p.dalp[1] =  0.22 * 0.3 * sin(phia);
      p.dalp[2] = -0.07 * 0.2 * cos(3.7 * t - 0.2 * x[2]);
      p.beta[0] = 0.16 * sin(phib);
      p.beta[1] = 0.0;
      p.beta[2] = 0.0;
      for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
          p.dbeta[i][j] = 0.0;
      p.dbeta[2][0] = 0.16 * 0.25 * cos(phib);
      const Real gg = 1.0 + 0.12 * sin(phig);
      const Real dgg_0 = 0.12 * 0.15 * cos(phig);
      const Real dgg_1 = 0.12 * 0.20 * cos(phig);
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
          p.g[i][j] = (i == j) ? gg : 0.0;
          for (int k = 0; k < 3; ++k) p.dg[i][j][k] = 0.0;
        }
        p.dg[0][i][i] = dgg_0;
        p.dg[1][i][i] = dgg_1;
      }
    };
    struct LinMetric {
      Real t0, t1;
      decltype(eval_exact_at_t) fn;
      KOKKOS_INLINE_FUNCTION bool IsStatic() const { return false; }
      KOKKOS_INLINE_FUNCTION void operator()(int slot, const Real x[3], AdmPoint &p) const {
        fn((slot == 0) ? t0 : t1, x, p);
      }
    };
    struct QuadMetric {
      Real tm1, t0, t1, r;
      bool has_prev;
      decltype(eval_exact_at_t) fn;
      KOKKOS_INLINE_FUNCTION bool IsStatic() const { return false; }
      KOKKOS_INLINE_FUNCTION void operator()(int slot, const Real x[3], AdmPoint &p) const {
        fn((slot == 0) ? t0 : t1, x, p);
      }
      KOKKOS_INLINE_FUNCTION void EvalAtFrac(Real c, const Real x[3], AdmPoint &p) const {
        AdmPoint pm1, p0, p1;
        fn(t0, x, p0);
        fn(t1, x, p1);
        if (has_prev) {
          fn(tm1, x, pm1);
          const Real wm1 = (r * r * c * (c - 1.0)) / (1.0 + r);
          const Real w0  = (1.0 - c) * (1.0 + r * c);
          const Real w1  = (c * (1.0 + r * c)) / (1.0 + r);
          BlendAdm3(wm1, pm1, w0, p0, w1, p1, p);
        } else {
          BlendAdm2(1.0 - c, p0, c, p1, p);
        }
      }
    };
    struct ExactMetric {
      Real t0, dt;
      decltype(eval_exact_at_t) fn;
      KOKKOS_INLINE_FUNCTION bool IsStatic() const { return false; }
      KOKKOS_INLINE_FUNCTION void operator()(int slot, const Real x[3], AdmPoint &p) const {
        fn((slot == 0) ? t0 : (t0 + dt), x, p);
      }
      KOKKOS_INLINE_FUNCTION void EvalAtFrac(Real c, const Real x[3], AdmPoint &p) const {
        fn(t0 + c * dt, x, p);
      }
    };

    const Real x_init[3] = {0.3, -0.2, 0.1};
    const Real u_init[3] = {0.5, 0.35, -0.25};
    // Exact continuous reference (uniform small dt)
    Real xref[3] = {x_init[0], x_init[1], x_init[2]}, uref[3] = {u_init[0], u_init[1], u_init[2]};
    const Real Ttot = 1.6;
    {
      const int nref = 8000;
      const Real dtr = Ttot / nref;
      Real dtau = 0.0;
      for (int s = 0; s < nref; ++s) {
        ExactMetric em{s * dtr, dtr, eval_exact_at_t};
        int it = PushGL4(em, dtr, 2.0e-14, 200, xref, uref, 1.0, dtau);
        assert(it > 0);
      }
    }

    const int nbase[4] = {16, 32, 64, 128};
    Real err_lin[4], err_quad[4], hs[4];
    for (int k = 0; k < 4; ++k) {
      // Non-uniform alternating step sizes with ratio r = 1.27 and 1/1.27
      const int nsteps = nbase[k];
      std::vector<Real> dts(nsteps);
      Real sumt = 0.0;
      for (int s = 0; s < nsteps; ++s) {
        dts[s] = (s % 2 == 0) ? 1.0 : 1.27;
        sumt += dts[s];
      }
      for (int s = 0; s < nsteps; ++s) dts[s] *= Ttot / sumt;
      hs[k] = Ttot / nsteps;

      Real xl[3] = {x_init[0], x_init[1], x_init[2]}, ul[3] = {u_init[0], u_init[1], u_init[2]}, dtl = 0.0;
      Real xq[3] = {x_init[0], x_init[1], x_init[2]}, uq[3] = {u_init[0], u_init[1], u_init[2]}, dtq = 0.0;
      Real t = 0.0, tm1 = 0.0, dt_prev = 0.0;
      for (int s = 0; s < nsteps; ++s) {
        const Real dt = dts[s];
        LinMetric lm{t, t + dt, eval_exact_at_t};
        int itl = PushGL4(lm, dt, 2.0e-14, 200, xl, ul, 1.0, dtl);
        assert(itl > 0);

        QuadMetric qm{tm1, t, t + dt, (s > 0) ? (dt / dt_prev) : 1.0, (s > 0), eval_exact_at_t};
        int itq = PushGL4(qm, dt, 2.0e-14, 200, xq, uq, 1.0, dtq);
        assert(itq > 0);

        tm1 = t;
        dt_prev = dt;
        t += dt;
      }
      Real el = 0.0, eq = 0.0;
      for (int d = 0; d < 3; ++d) {
        el += (xl[d]-xref[d])*(xl[d]-xref[d]) + (ul[d]-uref[d])*(ul[d]-uref[d]);
        eq += (xq[d]-xref[d])*(xq[d]-xref[d]) + (uq[d]-uref[d])*(uq[d]-uref[d]);
      }
      err_lin[k]  = sqrt(el);
      err_quad[k] = sqrt(eq);
    }
    const Real p_lin  = log(err_lin[0]  / err_lin[3])  / log(hs[0] / hs[3]);
    const Real p_quad = log(err_quad[0] / err_quad[3]) / log(hs[0] / hs[3]);
    std::printf("[TEST8 TINTERP r=1.27] p_lin=%.3f p_quad=%.3f | h=%.4f: "
                "err_lin=%.3e err_quad=%.3e\n",
                p_lin, p_quad, hs[3], err_lin[3], err_quad[3]);
    assert(p_lin >= 1.90 && p_lin <= 2.15);
    assert(p_quad >= 2.95);
    assert(err_lin[3] / err_quad[3] >= 50.0);
  }

  // 9. Cell-BGK SampleMaxwellJuttner moments + ProjectCellFourMomentumT (<1e-14 on unequal m)
  {
    const Real thetas[4] = {1.0e-4, 0.1, 1.0, 5.0};
    for (int ti = 0; ti < 4; ++ti) {
      const Real th = thetas[ti];
      Real wm_ex = 0.0, hr_ex = 0.0, cs2_ex = 0.0, ga_ex = 0.0;
      SyngeThermo(th, wm_ex, hr_ex, cs2_ex, ga_ex);
      const Real e2_ex = 3.0 * th * hr_ex + (wm_ex * wm_ex - 1.0) - (wm_ex - 1.0) * 0.0;
      // Exact E[<W^2>]: in MJ, <u^2 / W> = 3 * Theta * w_m => wait: let's check <W> and <|q|^2/W> = 3*Theta!
      const int n_draw = 40000;
      Real sum_w = 0.0, sum_q2_w = 0.0, sum_q[3] = {0.0, 0.0, 0.0};
      for (int p = 0; p < n_draw; ++p) {
        rng::Key key{12345ULL, rng::Stream(rng::kStreamTests, 1), static_cast<std::uint64_t>(p),
                     static_cast<std::uint64_t>(ti), 0ULL};
        Real q[3];
        SampleMaxwellJuttner(th, key, 1ULL, q);
        const Real q2 = q[0]*q[0] + q[1]*q[1] + q[2]*q[2];
        const Real W = sqrt(1.0 + q2);
        sum_w += W;
        sum_q2_w += q2 / W;
        sum_q[0] += q[0]; sum_q[1] += q[1]; sum_q[2] += q[2];
      }
      const Real mean_w = sum_w / n_draw;
      const Real mean_q2w = sum_q2_w / n_draw;
      const Real rel_w = fabs(mean_w - wm_ex) / wm_ex;
      const Real rel_p = fabs(mean_q2w - 3.0 * th) / (3.0 * th);
      std::printf("[TEST9 MJ theta=%.4g] <W>=%.6f (exact=%.6f, rel=%.2e) <q^2/W>=%.6f (3Th=%.6f, rel=%.2e)\n",
                  th, mean_w, wm_ex, rel_w, mean_q2w, 3.0 * th, rel_p);
      assert(rel_w < 1.5e-2);
      assert(rel_p < 1.5e-2);
      for (int i = 0; i < 3; ++i) assert(fabs(sum_q[i] / n_draw) < 0.025 * sqrt(3.0 * th * hr_ex + 1e-12));
    }

    // Unequal-mass ProjectCellFourMomentumT exact conservation test
    const int n_p = 32;
    std::vector<Real> m_vec(n_p);
    std::vector<Real> q_buf(3 * n_p);
    Real M_c = 0.0, E_c = 0.0, P_c[3] = {0.0, 0.0, 0.0};
    for (int p = 0; p < n_p; ++p) {
      m_vec[p] = 0.5 + 0.1 * (p % 7);
      const Real sign = (p % 2 == 0) ? 1.0 : -1.0;
      const Real q0[3] = {sign * (1.4 + 0.05 * p), 0.3 * cos(0.7 * p), -0.2 * sin(0.4 * p)};
      q_buf[3*p+0] = q0[0]; q_buf[3*p+1] = q0[1]; q_buf[3*p+2] = q0[2];
      M_c += m_vec[p];
      E_c += m_vec[p] * sqrt(1.0 + q0[0]*q0[0] + q0[1]*q0[1] + q0[2]*q0[2]);
      P_c[0] += m_vec[p]*q0[0]; P_c[1] += m_vec[p]*q0[1]; P_c[2] += m_vec[p]*q0[2];
    }
    const Real M_inv = sqrt(E_c*E_c - (P_c[0]*P_c[0] + P_c[1]*P_c[1] + P_c[2]*P_c[2]));
    const Real th_c = SafeMjThetaFromW(M_inv / M_c);
    const Real U0_c = E_c / M_inv;
    const Real U_c[3] = {P_c[0]/M_inv, P_c[1]/M_inv, P_c[2]/M_inv};
    for (int p = 0; p < n_p; ++p) {
      rng::Key key{999ULL, rng::Stream(rng::kStreamTests, 2), static_cast<std::uint64_t>(p), 0ULL, 0ULL};
      Real qc[3], qt[3];
      SampleMaxwellJuttner(th_c, key, 1ULL, qc);
      LorentzBoostMom(U0_c, U_c, qc, qt);
      q_buf[3*p+0] = qt[0]; q_buf[3*p+1] = qt[1]; q_buf[3*p+2] = qt[2];
    }
    const bool ok_proj = ProjectCellFourMomentumT(
        n_p,
        [&](int p) { return m_vec[p]; },
        [&](int p, Real q[3]) { q[0]=q_buf[3*p+0]; q[1]=q_buf[3*p+1]; q[2]=q_buf[3*p+2]; },
        [&](int p, const Real q[3]) { q_buf[3*p+0]=q[0]; q_buf[3*p+1]=q[1]; q_buf[3*p+2]=q[2]; },
        M_c, E_c, P_c);
    assert(ok_proj);
    Real E_after = 0.0, P_after[3] = {0.0, 0.0, 0.0};
    for (int p = 0; p < n_p; ++p) {
      const Real *q = &q_buf[3*p];
      E_after += m_vec[p] * sqrt(1.0 + q[0]*q[0] + q[1]*q[1] + q[2]*q[2]);
      P_after[0] += m_vec[p]*q[0]; P_after[1] += m_vec[p]*q[1]; P_after[2] += m_vec[p]*q[2];
    }
    const Real dE_proj = fabs(E_after - E_c) / E_c;
    const Real dP_proj = sqrt((P_after[0]-P_c[0])*(P_after[0]-P_c[0])
                            + (P_after[1]-P_c[1])*(P_after[1]-P_c[1])
                            + (P_after[2]-P_c[2])*(P_after[2]-P_c[2])) / E_c;
    std::printf("[TEST9 PROJ] rel_dE=%.3e rel_dP=%.3e\n", dE_proj, dP_proj);
    assert(dE_proj < 1.0e-14 && dP_proj < 1.0e-14);
  }

  // 10. Iteration 3: Self-adjoint metric-weighted flux-conservative filter
  {
    // (a) 1D curved metric with >1000x volume-element contrast and singular cell isolation
    const int nx = 48;
    const Real dx = 0.25;
    std::vector<Real> sg(nx), u0(nx), u_cur(nx), v0(nx);
    for (int i = 0; i < nx; ++i) {
      const Real x = (i + 0.5 - 0.5 * nx) * dx;
      const Real psi = 1.0 + 2.5 * exp(-0.5 * x * x);
      sg[i] = pow(psi, 6.0);
    }
    auto apply_mcons_1d = [&](const std::vector<Real> &in, Real kappa,
                              const std::vector<Real> &sg_in) {
      const int n = static_cast<int>(in.size());
      std::vector<Real> flx(n + 1, 0.0), out(n, 0.0);
      for (int i = 1; i < n; ++i) {
        flx[i] = MetricFlux1D(kappa, dx, sg_in[i - 1], sg_in[i], in[i - 1], in[i]);
      }
      for (int i = 0; i < n; ++i) {
        out[i] = (sg_in[i] > 0.0) ? (in[i] + (flx[i + 1] - flx[i]) / (sg_in[i] * dx)) : 0.0;
      }
      return out;
    };
    // Constant preservation T == 1.7
    std::vector<Real> t_const(nx, 1.7);
    auto t_const_f = apply_mcons_1d(t_const, 0.25, sg);
    Real err_const = 0.0, err_naive_dens = 0.0;
    for (int i = 0; i < nx; ++i) {
      err_const = fmax(err_const, fabs(t_const_f[i] - 1.7));
      if (i > 0 && i < nx - 1) {
        const Real d_f = (0.25 * sg[i - 1] + 0.5 * sg[i] + 0.25 * sg[i + 1]) * 1.7 / sg[i];
        err_naive_dens = fmax(err_naive_dens, fabs(d_f - 1.7));
      }
    }
    assert(err_const < 1.0e-14);
    assert(err_naive_dens > 1.0e-2);

    // Conservation, self-adjointness, L^2(sqrt(gamma)) contraction
    for (int i = 0; i < nx; ++i) {
      u0[i] = 1.2 + 0.6 * cos(0.7 * i) + ((i == nx / 2) ? 3.5 : 0.0);
      v0[i] = 0.5 + 0.4 * sin(0.9 * i + 0.3);
    }
    auto u1 = apply_mcons_1d(u0, 0.25, sg);
    auto v1 = apply_mcons_1d(v0, 0.25, sg);
    Real sum_u0 = 0.0, sum_u1 = 0.0, norm_u0 = 0.0, norm_u1 = 0.0, inner_uv1 = 0.0, inner_u1v = 0.0;
    for (int i = 0; i < nx; ++i) {
      const Real w = sg[i] * dx;
      sum_u0 += w * u0[i];
      sum_u1 += w * u1[i];
      norm_u0 += w * u0[i] * u0[i];
      norm_u1 += w * u1[i] * u1[i];
      inner_uv1 += w * u0[i] * v1[i];
      inner_u1v += w * u1[i] * v0[i];
      assert(u1[i] > 0.0);
    }
    const Real rel_cons_1d = fabs(sum_u1 - sum_u0) / sum_u0;
    const Real rel_sa_1d = fabs(inner_uv1 - inner_u1v) / fmax(fabs(inner_uv1), 1.0);
    assert(rel_cons_1d < 1.0e-14);
    assert(rel_sa_1d < 1.0e-14);
    assert(norm_u1 <= norm_u0 + 1.0e-14);

    // Singular cell isolation + positivity
    std::vector<Real> sg_sing = sg, u_sing = u0;
    sg_sing[nx / 2] = 0.0;
    u_sing[nx / 2] = 0.0;
    auto u_sing_f = apply_mcons_1d(u_sing, 0.25, sg_sing);
    Real sum_s0 = 0.0, sum_s1 = 0.0;
    for (int i = 0; i < nx; ++i) {
      sum_s0 += sg_sing[i] * dx * u_sing[i];
      sum_s1 += sg_sing[i] * dx * u_sing_f[i];
      assert(u_sing_f[i] >= 0.0);
    }
    assert(u_sing_f[nx / 2] == 0.0);
    assert(fabs(sum_s1 - sum_s0) / sum_s0 < 1.0e-14);

    // Flat-space equivalence to (1/4, 1/2, 1/4)
    std::vector<Real> sg_flat(nx, 2.3);
    auto u_flat = apply_mcons_1d(u0, 0.25, sg_flat);
    for (int i = 1; i < nx - 1; ++i) {
      const Real exact_bin = 0.25 * u0[i - 1] + 0.5 * u0[i] + 0.25 * u0[i + 1];
      assert(CheckClose(u_flat[i], exact_bin, 1e-14, 1e-14));
    }

    // (b) 2-level coarse-fine AMR interface with exact fine-to-coarse refluxing
    // Coarse block C: 8 cells, dxC = 1.0, active x in [0, 8]
    // Fine block F: 16 cells, dxF = 0.5, active x in [8, 16] (1 ghost cell on left at x=7.75 via linear/const prolong)
    const int nC = 8, nF = 16;
    const Real dxC = 1.0, dxF = 0.5;
    std::vector<Real> sgC(nC + 1), sgF(nF + 1), tC(nC + 1), tF(nF + 1);
    auto sg_fn = [](Real x) { return 1.0 + 1.5 * exp(-0.05 * (x - 8.0) * (x - 8.0)); };
    for (int i = 0; i <= nC; ++i) sgC[i] = sg_fn((i + 0.5) * dxC);
    sgF[0] = sg_fn(8.0 - 0.5 * dxF);
    for (int i = 1; i <= nF; ++i) sgF[i] = sg_fn(8.0 + (i - 0.5) * dxF);
    Real max_amr_const_err = 0.0, max_amr_cons_err = 0.0;
    for (int pass = 0; pass < 2; ++pass) {
      const Real kappa = (pass == 0) ? 0.25 : -1.0;
      // Constant preservation
      std::fill(tC.begin(), tC.end(), 2.5);
      std::fill(tF.begin(), tF.end(), 2.5);
      std::vector<Real> flxC(nC + 1, 0.0), flxF(nF + 1, 0.0);
      for (int i = 1; i <= nC; ++i) flxC[i] = (i == nC) ? 0.0 : MetricFlux1D(kappa, dxC, sgC[i - 1], sgC[i], tC[i - 1], tC[i]);
      flxF[0] = MetricFlux1D(kappa, dxF, sgF[0], sgF[1], tF[0], tF[1]);
      for (int i = 1; i < nF; ++i) flxF[i] = MetricFlux1D(kappa, dxF, sgF[i], sgF[i + 1], tF[i], tF[i + 1]);
      flxC[nC] = flxF[0];  // fine-to-coarse reflux
      for (int i = 0; i < nC; ++i) max_amr_const_err = fmax(max_amr_const_err, fabs((tC[i] + (flxC[i + 1] - flxC[i]) / (sgC[i] * dxC)) - 2.5));
      for (int i = 1; i <= nF; ++i) max_amr_const_err = fmax(max_amr_const_err, fabs((tF[i] + (flxF[i] - flxF[i - 1]) / (sgF[i] * dxF)) - 2.5));

      // Non-trivial profile conservation across curved 2-level interface
      for (int i = 0; i < nC; ++i) tC[i] = 1.0 + 0.3 * sin(0.6 * i);
      tC[nC] = 0.5 * (tC[nC - 1] + 1.0);
      for (int i = 1; i <= nF; ++i) tF[i] = 1.0 + 0.25 * cos(0.4 * i);
      tF[0] = 0.75 * tC[nC - 1] + 0.25 * tF[1];  // prolongated ghost value (even arbitrary value must conserve!)
      tC[nC] = 0.75 * tF[1] + 0.25 * tC[nC - 1];  // restricted coarse ghost value
      Real I_before = 0.0, I_after = 0.0;
      for (int i = 0; i < nC; ++i) I_before += sgC[i] * dxC * tC[i];
      for (int i = 1; i <= nF; ++i) I_before += sgF[i] * dxF * tF[i];
      for (int i = 1; i < nC; ++i) flxC[i] = MetricFlux1D(kappa, dxC, sgC[i - 1], sgC[i], tC[i - 1], tC[i]);
      flxF[0] = MetricFlux1D(kappa, dxF, sgF[0], sgF[1], tF[0], tF[1]);
      for (int i = 1; i < nF; ++i) flxF[i] = MetricFlux1D(kappa, dxF, sgF[i], sgF[i + 1], tF[i], tF[i + 1]);
      flxC[nC] = flxF[0];  // exact refluxing
      for (int i = 0; i < nC; ++i) I_after += sgC[i] * dxC * (tC[i] + (flxC[i + 1] - flxC[i]) / (sgC[i] * dxC));
      for (int i = 1; i <= nF; ++i) I_after += sgF[i] * dxF * (tF[i] + (flxF[i] - flxF[i - 1]) / (sgF[i] * dxF));
      max_amr_cons_err = fmax(max_amr_cons_err, fabs(I_after - I_before) / I_before);
    }
    assert(max_amr_const_err < 1.0e-14);
    assert(max_amr_cons_err < 1.0e-14);
    std::printf("[TEST10 MCONS] const_err=%.2e (naive_dens=%.2e) sa=%.2e cons_1d=%.2e amr_const=%.2e amr_cons=%.2e\n",
                err_const, err_naive_dens, rel_sa_1d, rel_cons_1d, max_amr_const_err, max_amr_cons_err);
  }
  std::printf("C++ standalone GR-LBV kernel self-tests PASSED.\n");
}

}  // namespace

int main(int argc, char **argv) {
  if (argc == 4 && std::string(argv[1]) == "--eval-table") {
    RunEvalTable(argv[2], argv[3]);
    return 0;
  }
  RunSelfTests();
  return 0;
}
