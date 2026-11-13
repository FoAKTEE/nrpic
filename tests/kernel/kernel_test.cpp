// Standalone driver for the NRPIC pusher kernels (no AthenaK, no Kokkos).
//
//   kernel_test check
//       verifies the analytic metric derivatives against finite differences and the
//       Hermite lattice reconstruction against the analytic metric.
//
//   kernel_test run <metric> <pusher> <dt> <tend> <tol> <c0> <c1> <c2> <u0> <u1> <u2>
//                   [spin=0.9] [lattice_dx=0.025] [stride=0] [outfile]
//       metric: bl   Boyer-Lindquist (r,theta,phi), analytic
//               kss  spherical Kerr-Schild (r,theta,phi), analytic
//               ksc  Cartesian Kerr-Schild, analytic
//               lat  Cartesian Kerr-Schild sampled on a lattice, cubic Hermite
//       pusher: mid | boris (symmetric-gauge triad) | borisc (Cholesky triad)
//       The initial state (c, u_i covariant) is given in Boyer-Lindquist components for
//       metric bl and in spherical Kerr-Schild components otherwise.
//       With stride > 0 every stride-th step is written to outfile as binary doubles
//       (t, x[3], u[3], E, Lz, Q, r, theta, phi).
//
// Build: g++ -O2 -std=c++17 -DNRPIC_STANDALONE -I athenak/src/particles kernel_test.cpp

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "nrpic_kernels.hpp"
#include "nrpic_metrics.hpp"

using nrpic::AdmPoint;

namespace {

// spherical Kerr-Schild (r,theta,phi) of a Cartesian Kerr-Schild point
void CartToSph(const double a, const double x[3], double s[3]) {
  double b = x[0]*x[0] + x[1]*x[1] + x[2]*x[2] - a*a;
  double r = std::sqrt(0.5*(b + std::sqrt(b*b + 4.0*a*a*x[2]*x[2])));
  s[0] = r;
  s[1] = std::acos(x[2]/r);
  s[2] = std::atan2(r*x[1] - a*x[0], r*x[0] + a*x[1]);
}

// Jacobian J[i][j] = d x^i / d y^j of Cartesian (x,y,z) with respect to (r,theta,phi)
void Jacobian(const double a, const double s[3], double J[3][3]) {
  double r = s[0], st = std::sin(s[1]), ct = std::cos(s[1]);
  double sp = std::sin(s[2]), cp = std::cos(s[2]);
  J[0][0] = cp*st;             J[1][0] = sp*st;             J[2][0] = ct;
  J[0][1] = (r*cp - a*sp)*ct;  J[1][1] = (r*sp + a*cp)*ct;  J[2][1] = -r*st;
  J[0][2] = -(r*sp + a*cp)*st; J[1][2] = (r*cp - a*sp)*st;  J[2][2] = 0.0;
}

void SphToCartPos(const double a, const double s[3], double x[3]) {
  double r = s[0], st = std::sin(s[1]), ct = std::cos(s[1]);
  double sp = std::sin(s[2]), cp = std::cos(s[2]);
  x[0] = (r*cp - a*sp)*st;
  x[1] = (r*sp + a*cp)*st;
  x[2] = r*ct;
}

// u_sph_j = J[i][j] u_cart_i
void CartToSphMom(const double J[3][3], const double uc[3], double us[3]) {
  for (int j=0; j<3; ++j) {
    us[j] = J[0][j]*uc[0] + J[1][j]*uc[1] + J[2][j]*uc[2];
  }
}

// solve J^T uc = us
void SphToCartMom(const double J[3][3], const double us[3], double uc[3]) {
  double A[3][3];
  for (int i=0; i<3; ++i) for (int j=0; j<3; ++j) A[j][i] = J[i][j];
  double det = A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1])
             - A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0])
             + A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0]);
  for (int c=0; c<3; ++c) {
    double B[3][3];
    for (int i=0; i<3; ++i) for (int j=0; j<3; ++j) B[i][j] = (j == c) ? us[i] : A[i][j];
    double d = B[0][0]*(B[1][1]*B[2][2]-B[1][2]*B[2][1])
             - B[0][1]*(B[1][0]*B[2][2]-B[1][2]*B[2][0])
             + B[0][2]*(B[1][0]*B[2][1]-B[1][1]*B[2][0]);
    uc[c] = d/det;
  }
}

template <class MetricT>
double Energy(const MetricT &met, const double x[3], const double u[3]) {
  AdmPoint p;
  met(0, x, p);
  double gi[3][3], uup[3];
  nrpic::Inv3Sym(p.g, gi);
  double W = nrpic::LorentzFactor(gi, u, uup);
  return p.alp*W - (p.beta[0]*u[0] + p.beta[1]*u[1] + p.beta[2]*u[2]);
}

double Carter(const double a, const double E, const double th, const double uth,
              const double Lz) {
  double c = std::cos(th), s = std::sin(th);
  return uth*uth + c*c*(a*a*(1.0 - E*E) + Lz*Lz/(s*s));
}

template <class MetricT>
double CheckDerivs(const MetricT &met, const double x[3], const char *name) {
  AdmPoint p, pp, pm, pp2, pm2;
  met(0, x, p);
  double maxerr = 0.0;
  for (int k=0; k<3; ++k) {
    double h = 1.0e-3;
    double xp[3] = {x[0], x[1], x[2]}, xm[3] = {x[0], x[1], x[2]};
    double xp2[3] = {x[0], x[1], x[2]}, xm2[3] = {x[0], x[1], x[2]};
    xp[k] += h; xm[k] -= h; xp2[k] += 2*h; xm2[k] -= 2*h;
    met(0, xp, pp); met(0, xm, pm); met(0, xp2, pp2); met(0, xm2, pm2);
    auto fd = [&](double a2m, double am, double ap, double a2p) {
      return (a2m - 8.0*am + 8.0*ap - a2p)/(12.0*h);
    };
    maxerr = std::fmax(maxerr, std::fabs(fd(pm2.alp, pm.alp, pp.alp, pp2.alp) - p.dalp[k]));
    for (int i=0; i<3; ++i) {
      maxerr = std::fmax(maxerr, std::fabs(
          fd(pm2.beta[i], pm.beta[i], pp.beta[i], pp2.beta[i]) - p.dbeta[k][i]));
      for (int j=0; j<3; ++j) {
        maxerr = std::fmax(maxerr, std::fabs(
            fd(pm2.g[i][j], pm.g[i][j], pp.g[i][j], pp2.g[i][j]) - p.dg[k][i][j]));
      }
    }
  }
  std::printf("  %-4s derivative check at (%.3f,%.3f,%.3f): max abs error %.3e\n",
              name, x[0], x[1], x[2], maxerr);
  return maxerr;
}

int RunCheck() {
  const double a = 0.9;
  nrpic::KerrSchildCart ksc{1.0, a};
  nrpic::KerrSchildSph kss{1.0, a};
  nrpic::BoyerLindquist bl{1.0, a};
  double worst = 0.0;
  const double pc[2][3] = {{3.1, -2.2, 1.7}, {-1.4, 1.3, 0.9}};
  const double ps[2][3] = {{4.3, 1.1, 0.4}, {1.95, 2.0, 5.0}};
  for (int n=0; n<2; ++n) {
    worst = std::fmax(worst, CheckDerivs(ksc, pc[n], "ksc"));
    worst = std::fmax(worst, CheckDerivs(kss, ps[n], "kss"));
    worst = std::fmax(worst, CheckDerivs(bl, ps[n], "bl"));
  }

  // consistency of the Cartesian and spherical Kerr-Schild forms: g_sph = J^T g_cart J
  double cons = 0.0;
  for (int n=0; n<2; ++n) {
    double xc[3], J[3][3];
    SphToCartPos(a, ps[n], xc);
    Jacobian(a, ps[n], J);
    AdmPoint pcart, psph;
    ksc(0, xc, pcart);
    kss(0, ps[n], psph);
    for (int i=0; i<3; ++i) {
      for (int j=0; j<3; ++j) {
        double s = 0.0;
        for (int k=0; k<3; ++k) for (int l=0; l<3; ++l) s += J[k][i]*pcart.g[k][l]*J[l][j];
        cons = std::fmax(cons, std::fabs(s - psph.g[i][j]));
      }
      double bs = 0.0;   // beta^k_cart = J[k][i] beta^i_sph
      for (int k=0; k<3; ++k) bs += J[i][k]*psph.beta[k];
      cons = std::fmax(cons, std::fabs(bs - pcart.beta[i]));
    }
    cons = std::fmax(cons, std::fabs(pcart.alp - psph.alp));
  }
  std::printf("  Cartesian vs spherical Kerr-Schild consistency: %.3e\n", cons);
  worst = std::fmax(worst, cons);

  // Hermite lattice against the analytic metric: values and derivatives, two spacings
  double e_prev[2] = {0.0, 0.0};
  for (int lev=0; lev<3; ++lev) {
    double h = 0.1/std::pow(2.0, lev);
    nrpic::LatticeMetric<nrpic::KerrSchildCart> lat{ksc, {0.0, 0.0, 0.0}, {h, h, h}};
    const double x[3] = {2.31, 1.17, 0.83};
    AdmPoint pa, pl;
    ksc(0, x, pa);
    lat(0, x, pl);
    double ev = std::fabs(pa.alp - pl.alp), ed = 0.0;
    for (int i=0; i<3; ++i) {
      ed = std::fmax(ed, std::fabs(pa.dalp[i] - pl.dalp[i]));
      for (int j=0; j<3; ++j) {
        ev = std::fmax(ev, std::fabs(pa.g[i][j] - pl.g[i][j]));
        for (int k=0; k<3; ++k) {
          ed = std::fmax(ed, std::fabs(pa.dg[k][i][j] - pl.dg[k][i][j]));
        }
      }
    }
    std::printf("  lattice h=%.4f: value error %.3e", h, ev);
    if (lev > 0) std::printf(" (order %.2f)", std::log2(e_prev[0]/ev));
    std::printf(", derivative error %.3e", ed);
    if (lev > 0) std::printf(" (order %.2f)", std::log2(e_prev[1]/ed));
    std::printf("\n");
    e_prev[0] = ev; e_prev[1] = ed;
  }

  // symmetric-gauge triad and its derivative against finite differences
  {
    const double x[3] = {2.31, 1.17, 0.83};
    AdmPoint p, pp, pm;
    ksc(0, x, p);
    nrpic::Triad tr, trp, trm;
    double dS[3][3];
    nrpic::BuildTriad(nrpic::kTriadSymmetric, p.g, tr);
    double e = 0.0;
    for (int k=0; k<3; ++k) {
      double h = 1.0e-5;
      double xp[3] = {x[0], x[1], x[2]}, xm[3] = {x[0], x[1], x[2]};
      xp[k] += h; xm[k] -= h;
      ksc(0, xp, pp); ksc(0, xm, pm);
      nrpic::BuildTriad(nrpic::kTriadSymmetric, pp.g, trp);
      nrpic::BuildTriad(nrpic::kTriadSymmetric, pm.g, trm);
      nrpic::TriadDeriv(nrpic::kTriadSymmetric, tr, p.dg[k], dS);
      for (int i=0; i<3; ++i) for (int j=0; j<3; ++j) {
        e = std::fmax(e, std::fabs((trp.S[i][j] - trm.S[i][j])/(2*h) - dS[i][j]));
      }
    }
    double id = 0.0, sq = 0.0;   // S Si = 1 and S S = g
    for (int i=0; i<3; ++i) for (int j=0; j<3; ++j) {
      double s1 = 0.0, s2 = 0.0;
      for (int k=0; k<3; ++k) { s1 += tr.S[i][k]*tr.Si[k][j]; s2 += tr.S[i][k]*tr.S[k][j]; }
      id = std::fmax(id, std::fabs(s1 - ((i == j) ? 1.0 : 0.0)));
      sq = std::fmax(sq, std::fabs(s2 - p.g[i][j]));
    }
    std::printf("  triad: |S Si - 1| = %.3e, |S S - g| = %.3e, dS error vs FD = %.3e\n",
                id, sq, e);
    worst = std::fmax(worst, std::fmax(id, sq));
  }
  std::printf("check %s (worst analytic-derivative/consistency error %.3e)\n",
              (worst < 1.0e-8) ? "PASSED" : "FAILED", worst);
  return (worst < 1.0e-8) ? 0 : 1;
}

// pusher: 0 midpoint, 1 Boris with symmetric triad, 2 Boris with Cholesky triad.
// The invariants are always evaluated with the exact metric ex.
template <class MetricT, class ExactT>
int Evolve(const MetricT &met, const ExactT &ex, const bool cart, const int pusher,
           const double a,
           const double dt, const double tend, const double tol, double x[3], double u[3],
           const int stride, const char *outfile) {
  std::FILE *fp = nullptr;
  if (stride > 0 && outfile != nullptr) fp = std::fopen(outfile, "wb");
  auto diag = [&](double rec[13], double t) {
    double s[3], us[3];
    if (cart) {
      double J[3][3];
      CartToSph(a, x, s);
      Jacobian(a, s, J);
      CartToSphMom(J, u, us);
    } else {
      for (int i=0; i<3; ++i) { s[i] = x[i]; us[i] = u[i]; }
    }
    double E = Energy(ex, x, u);
    rec[0] = t;
    for (int i=0; i<3; ++i) { rec[1+i] = x[i]; rec[4+i] = u[i]; rec[10+i] = s[i]; }
    rec[7] = E; rec[8] = us[2]; rec[9] = Carter(a, E, s[1], us[1], us[2]);
  };
  double rec[13];
  diag(rec, 0.0);
  const double E0 = rec[7], L0 = rec[8], Q0 = rec[9];
  double eE = 0.0, eL = 0.0, eQ = 0.0, rmin = rec[10], rmax = rec[10], trmin = 0.0;
  long nsteps = std::lround(tend/dt);
  long iters = 0, nfail = 0;
  int itmax = 0;
  if (fp) std::fwrite(rec, sizeof(double), 13, fp);
  for (long n=1; n<=nsteps; ++n) {
    int it = (pusher == 0) ? nrpic::PushMidpoint(met, dt, tol, 200, x, u)
           : nrpic::PushBoris(met, (pusher == 1) ? nrpic::kTriadSymmetric
                                                 : nrpic::kTriadCholesky,
                              dt, tol, 200, x, u);
    if (it < 0) { ++nfail; it = -it; }
    iters += it;
    if (it > itmax) itmax = it;
    diag(rec, n*dt);
    eE = std::fmax(eE, std::fabs(rec[7]/E0 - 1.0));
    eL = std::fmax(eL, std::fabs(rec[8]/L0 - 1.0));
    eQ = std::fmax(eQ, std::fabs(rec[9]/Q0 - 1.0));
    if (rec[10] < rmin) { rmin = rec[10]; trmin = n*dt; }
    if (rec[10] > rmax) { rmax = rec[10]; }
    if (fp && (n % stride == 0)) std::fwrite(rec, sizeof(double), 13, fp);
  }
  if (fp) std::fclose(fp);
  std::printf("E0=%.10f Lz0=%.10f Q0=%.10f\n", E0, L0, Q0);
  std::printf("max rel err: E %.3e  Lz %.3e  Q %.3e\n", eE, eL, eQ);
  std::printf("r range [%.6f, %.6f], r_min at t=%.3f\n", rmin, rmax, trmin);
  std::printf("final t=%.6f r=%.12f theta=%.12f phi=%.12f\n", rec[0], rec[10], rec[11],
              rec[12]);
  std::printf("iterations: mean %.2f max %d unconverged %ld of %ld steps\n",
              static_cast<double>(iters)/nsteps, itmax, nfail, nsteps);
  return 0;
}

} // namespace

int main(int argc, char *argv[]) {
  if (argc >= 2 && std::strcmp(argv[1], "check") == 0) return RunCheck();
  if (argc < 13 || std::strcmp(argv[1], "run") != 0) {
    std::fprintf(stderr, "usage: see header of kernel_test.cpp\n");
    return 2;
  }
  std::string metric = argv[2];
  std::string pname = argv[3];
  int pusher = (pname == "boris") ? 1 : ((pname == "borisc") ? 2 : 0);
  double dt = std::atof(argv[4]), tend = std::atof(argv[5]), tol = std::atof(argv[6]);
  double c[3] = {std::atof(argv[7]), std::atof(argv[8]), std::atof(argv[9])};
  double us[3] = {std::atof(argv[10]), std::atof(argv[11]), std::atof(argv[12])};
  double a = (argc > 13) ? std::atof(argv[13]) : 0.9;
  double h = (argc > 14) ? std::atof(argv[14]) : 0.025;
  int stride = (argc > 15) ? std::atoi(argv[15]) : 0;
  const char *outfile = (argc > 16) ? argv[16] : nullptr;

  if (metric == "bl") {
    nrpic::BoyerLindquist met{1.0, a};
    return Evolve(met, met, false, pusher, a, dt, tend, tol, c, us, stride, outfile);
  } else if (metric == "kss") {
    nrpic::KerrSchildSph met{1.0, a};
    return Evolve(met, met, false, pusher, a, dt, tend, tol, c, us, stride, outfile);
  }
  double x[3], u[3], J[3][3];
  SphToCartPos(a, c, x);
  Jacobian(a, c, J);
  SphToCartMom(J, us, u);
  nrpic::KerrSchildCart ksc{1.0, a};
  if (metric == "ksc") {
    return Evolve(ksc, ksc, true, pusher, a, dt, tend, tol, x, u, stride, outfile);
  } else if (metric == "lat") {
    nrpic::LatticeMetric<nrpic::KerrSchildCart> met{ksc, {0.0, 0.0, 0.0}, {h, h, h}};
    return Evolve(met, ksc, true, pusher, a, dt, tend, tol, x, u, stride, outfile);
  }
  std::fprintf(stderr, "unknown metric %s\n", metric.c_str());
  return 2;
}
