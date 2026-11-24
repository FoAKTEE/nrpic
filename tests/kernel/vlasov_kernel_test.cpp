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
