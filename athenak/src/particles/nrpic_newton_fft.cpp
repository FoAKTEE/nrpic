//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_newton_fft.cpp
//! \brief Fourier solver for the Poisson equation of the Newtonian mode of the NRPIC
//! module (<particles> newton_poisson = fft), for a uniform mesh that is periodic in all
//! directions:
//!   Phi_k = -four_pi_G rho_k / K^2(k)   (k != 0),      Phi_0 = 0,
//! with the symbol K^2 chosen by <particles> newton_fft_symbol:
//!   spectral     K^2 = k^2, the continuum operator: no truncation error of a difference
//!                Laplacian (the seven-point operator of the multigrid solver makes the
//!                force on a mode too strong by [(kh/2)/sin(kh/2)]^2 - 1 ~ (kh)^2/12);
//!   seven_point  K^2 = sum_d (2/h_d)^2 sin^2(k_d h_d/2), the symbol of the seven-point
//!                Laplacian: the solution of the multigrid solver to rounding, without
//!                its iteration (a check of both solvers against each other).
//! The mean of the density drops out with the mode k = 0, and the mean of the potential
//! is zero.  Deposit, filter, cloud compensation, ghost cells and the gather of the
//! force are those of the mode (nrpic_newton.cpp): only the solve is replaced.
//!
//! The transform is written here with Kokkos kernels (the code base has no Fourier
//! library): the density of all MeshBlocks is copied into one array of the mesh, and
//! each direction is transformed line by line, one line per thread, by an in-place
//! mixed-radix transform (decimation in time) for lengths with the prime factors 2, 3,
//! 5 and 7.  Complex data are held as two real arrays.  The cost is that of six passes
//! over the mesh per solve, each of n log n operations per line; the memory is four
//! real arrays of the size of the mesh.

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "z4c/tmunu.hpp"
#include "gravity/gravity.hpp"
#include "particles/particles.hpp"

namespace particles {

namespace {

void FftFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_newton_fft.cpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

// source index of every element in the order in which the butterflies combine them:
// a transform of length n with the factors f[0..nf-1] is the combination, with radix
// f[0], of the transforms of its f[0] interleaved subsequences
void FftPermutation(const int n, const int *f, const int nf, const int offset,
                    const int stride, std::vector<int> &out) {
  if (nf == 0) {
    out.push_back(offset);
    return;
  }
  const int p = f[0];
  for (int r=0; r<p; ++r) {
    FftPermutation(n/p, f + 1, nf - 1, offset + r*stride, stride*p, out);
  }
}

// factors and tables of one direction, by value inside the kernels
struct FftLine {
  int n;
  int nfac;
  int fac[32];
};

// element e of the line (l1, l2) along direction dir
KOKKOS_INLINE_FUNCTION
Real &FftAt(const DvceArray4D<Real> &a, const int c, const int dir, const int e,
            const int l1, const int l2) {
  return (dir == 0) ? a(c,l2,l1,e) : ((dir == 1) ? a(c,l2,e,l1) : a(c,e,l2,l1));
}

} // namespace

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonFftInit
//! \brief option newton_poisson and the tables of the Fourier solver; called at the end
//! of NrpicNewtonInit.  Parameters that are not in the input are not added to it.

void Particles::NrpicNewtonFftInit(ParameterInput *pin) {
  nw_fft = false;
  if (!pin->DoesParameterExist("particles", "newton_poisson")) return;
  const std::string ps = pin->GetString("particles", "newton_poisson");
  if (ps.compare("multigrid") == 0) return;
  if (ps.compare("fft") != 0) {
    FftFatal("<particles> newton_poisson = '" + ps + "' not recognized (multigrid or fft)");
  }
  Mesh *pm = pmy_pack->pmesh;
  if (!(pm->strictly_periodic) || pm->multilevel) {
    FftFatal("<particles> newton_poisson = fft requires a uniform mesh that is periodic "
             "in all directions (use the multigrid solver otherwise)");
  }
  if (pmy_pack->nmb_thispack != pm->nmb_total) {
    FftFatal("<particles> newton_poisson = fft requires all MeshBlocks in one pack");
  }
  nw_fft_symbol = 0;
  if (pin->DoesParameterExist("particles", "newton_fft_symbol")) {
    const std::string ss = pin->GetString("particles", "newton_fft_symbol");
    if (ss.compare("spectral") == 0) {
      nw_fft_symbol = 0;
    } else if (ss.compare("seven_point") == 0) {
      nw_fft_symbol = 1;
    } else {
      FftFatal("<particles> newton_fft_symbol = '" + ss + "' not recognized (spectral "
               "or seven_point)");
    }
  }
  nw_fft = true;

  nw_fft_n[0] = pm->mesh_indcs.nx1;
  nw_fft_n[1] = pm->mesh_indcs.nx2;
  nw_fft_n[2] = pm->mesh_indcs.nx3;
  const Real len[3] = {pm->mesh_size.x1max - pm->mesh_size.x1min,
                       pm->mesh_size.x2max - pm->mesh_size.x2min,
                       pm->mesh_size.x3max - pm->mesh_size.x3min};
  for (int d=0; d<3; ++d) {
    const int n = nw_fft_n[d];
    // prime factors, the largest first (they are the radices of the last butterflies)
    int rest = n, nf = 0;
    const int primes[4] = {7, 5, 3, 2};
    for (int q=0; q<4; ++q) {
      while (rest % primes[q] == 0 && nf < 32) {
        nw_fft_fac[d][nf++] = primes[q];
        rest /= primes[q];
      }
    }
    if (rest != 1 || n < 2) {
      FftFatal("<particles> newton_poisson = fft: the number of cells in each direction "
               "must be a product of the factors 2, 3, 5 and 7 (found "
               + std::to_string(n) + ")");
    }
    nw_fft_nfac[d] = nf;
    std::vector<int> perm;
    perm.reserve(n);
    FftPermutation(n, nw_fft_fac[d], nf, 0, 1, perm);
    Kokkos::realloc(nw_fft_perm[d], n);
    Kokkos::realloc(nw_fft_tw[d], 2, n);
    Kokkos::realloc(nw_fft_k2[d], n);
    auto hp = Kokkos::create_mirror_view(nw_fft_perm[d]);
    auto ht = Kokkos::create_mirror_view(nw_fft_tw[d]);
    auto hk = Kokkos::create_mirror_view(nw_fft_k2[d]);
    const Real h = len[d]/static_cast<Real>(n);
    for (int e=0; e<n; ++e) {
      hp(e) = perm[e];
      const Real arg = 2.0*M_PI*static_cast<Real>(e)/static_cast<Real>(n);
      ht(0,e) = std::cos(arg);
      ht(1,e) = std::sin(arg);
      if (nw_fft_symbol == 1) {
        hk(e) = SQR((2.0/h)*std::sin(0.5*arg));
      } else {
        const int ne = (2*e <= n) ? e : e - n;
        hk(e) = SQR(2.0*M_PI*static_cast<Real>(ne)/len[d]);
      }
    }
    Kokkos::deep_copy(nw_fft_perm[d], hp);
    Kokkos::deep_copy(nw_fft_tw[d], ht);
    Kokkos::deep_copy(nw_fft_k2[d], hk);
  }
  Kokkos::realloc(nw_fft_a, 2, nw_fft_n[2], nw_fft_n[1], nw_fft_n[0]);
  Kokkos::realloc(nw_fft_b, 2, nw_fft_n[2], nw_fft_n[1], nw_fft_n[0]);

  // first cell of each MeshBlock in the array of the mesh
  const int nmb = pmy_pack->nmb_thispack;
  Kokkos::realloc(nw_fft_off, nmb, 3);
  auto ho = Kokkos::create_mirror_view(nw_fft_off);
  auto szh = pmy_pack->pmb->mb_size.h_view;
  auto &indcs = pm->mb_indcs;
  const int nb[3] = {indcs.nx1, indcs.nx2, indcs.nx3};
  for (int m=0; m<nmb; ++m) {
    const Real x0[3] = {szh(m).x1min, szh(m).x2min, szh(m).x3min};
    const Real dx[3] = {szh(m).dx1, szh(m).dx2, szh(m).dx3};
    const Real xm[3] = {pm->mesh_size.x1min, pm->mesh_size.x2min, pm->mesh_size.x3min};
    for (int d=0; d<3; ++d) {
      const int off = static_cast<int>(std::lround((x0[d] - xm[d])/dx[d]));
      if (off < 0 || off + nb[d] > nw_fft_n[d] || off % nb[d] != 0) {
        FftFatal("newton_poisson = fft: a MeshBlock does not lie on the uniform mesh");
      }
      ho(m,d) = off;
    }
  }
  Kokkos::deep_copy(nw_fft_off, ho);

  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC Newtonian mode: Fourier Poisson solver on " << nw_fft_n[0]
              << " x " << nw_fft_n[1] << " x " << nw_fft_n[2] << " cells, symbol "
              << ((nw_fft_symbol == 1) ? "seven_point" : "spectral") << std::endl;
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonFftLines
//! \brief transform of all lines along direction dir, from src into dst: the elements
//! of a line are copied in the order of the permutation, then combined in place with
//! one butterfly stage per factor.  Forward: sum_j x_j exp(-2 pi i j k/n); inverse: the
//! conjugate, without the factor 1/n.

void Particles::NrpicNewtonFftLines(const int dir, const bool inverse,
                                    DvceArray4D<Real> &src, DvceArray4D<Real> &dst) {
  FftLine ln;
  ln.n = nw_fft_n[dir];
  ln.nfac = nw_fft_nfac[dir];
  for (int q=0; q<32; ++q) { ln.fac[q] = (q < ln.nfac) ? nw_fft_fac[dir][q] : 1; }
  // extents of the two directions across the lines
  const int n1 = (dir == 0) ? nw_fft_n[1] : nw_fft_n[0];
  const int n2 = (dir == 2) ? nw_fft_n[1] : nw_fft_n[2];
  const Real sgn = inverse ? 1.0 : -1.0;
  auto perm = nw_fft_perm[dir];
  auto tw = nw_fft_tw[dir];
  auto a = src;
  auto b = dst;
  par_for("nrpic_newton_fft", DevExeSpace(), 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int l2, const int l1) {
    const int n = ln.n;
    for (int e=0; e<n; ++e) {
      const int s = perm(e);
      FftAt(b, 0, dir, e, l1, l2) = FftAt(a, 0, dir, s, l1, l2);
      FftAt(b, 1, dir, e, l1, l2) = FftAt(a, 1, dir, s, l1, l2);
    }
    int m = 1;                                  // length of the finished transforms
    for (int st=ln.nfac-1; st>=0; --st) {
      const int p = ln.fac[st];
      const int nb = m*p;                       // length after this stage
      const int tstep = n/nb;
      for (int b0=0; b0<n; b0+=nb) {
        for (int k=0; k<m; ++k) {
          if (p == 2) {
            const Real wr = tw(0,k*tstep), wi = sgn*tw(1,k*tstep);
            Real &xr0 = FftAt(b, 0, dir, b0 + k, l1, l2);
            Real &xi0 = FftAt(b, 1, dir, b0 + k, l1, l2);
            Real &xr1 = FftAt(b, 0, dir, b0 + k + m, l1, l2);
            Real &xi1 = FftAt(b, 1, dir, b0 + k + m, l1, l2);
            const Real tr = wr*xr1 - wi*xi1;
            const Real ti = wr*xi1 + wi*xr1;
            const Real yr = xr0, yi = xi0;
            xr0 = yr + tr; xi0 = yi + ti;
            xr1 = yr - tr; xi1 = yi - ti;
          } else {
            Real yr[7], yi[7];
            for (int r=0; r<p; ++r) {
              yr[r] = FftAt(b, 0, dir, b0 + r*m + k, l1, l2);
              yi[r] = FftAt(b, 1, dir, b0 + r*m + k, l1, l2);
            }
            for (int q=0; q<p; ++q) {
              Real sr = yr[0], si = yi[0];
              for (int r=1; r<p; ++r) {
                const int it = ((r*(k + q*m)) % nb)*tstep;
                const Real wr = tw(0,it), wi = sgn*tw(1,it);
                sr += wr*yr[r] - wi*yi[r];
                si += wr*yi[r] + wi*yr[r];
              }
              FftAt(b, 0, dir, b0 + q*m + k, l1, l2) = sr;
              FftAt(b, 1, dir, b0 + q*m + k, l1, l2) = si;
            }
          }
        }
      }
      m = nb;
    }
  });
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicNewtonFftSolve
//! \brief potential of the deposited (and filtered) rest-mass density in the active
//! cells of the potential array of the gravity module; the ghost cells are filled by
//! NrpicNewtonPotential as after a multigrid solve

void Particles::NrpicNewtonFftSolve() {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  gravity::Gravity *pg = pmy_pack->pgrav;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
  const int nmb1 = pmy_pack->nmb_thispack - 1;
  const int n1 = nw_fft_n[0], n2 = nw_fft_n[1], n3 = nw_fft_n[2];
  auto tm = pmy_pack->ptmunu->u_tmunu;
  auto off = nw_fft_off;
  auto fa = nw_fft_a;
  auto fb = nw_fft_b;

  par_for("nrpic_newton_fft_load", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    const int gi = off(m,0) + i - is, gj = off(m,1) + j - js, gk = off(m,2) + k - ks;
    fa(0,gk,gj,gi) = tm(m,Tmunu::I_Tmunu_E,k,j,i);
    fa(1,gk,gj,gi) = 0.0;
  });

  NrpicNewtonFftLines(0, false, nw_fft_a, nw_fft_b);
  NrpicNewtonFftLines(1, false, nw_fft_b, nw_fft_a);
  NrpicNewtonFftLines(2, false, nw_fft_a, nw_fft_b);

  auto k2x = nw_fft_k2[0];
  auto k2y = nw_fft_k2[1];
  auto k2z = nw_fft_k2[2];
  const Real fac = -(pg->four_pi_G)/(static_cast<Real>(n1)*static_cast<Real>(n2)*
                                     static_cast<Real>(n3));
  par_for("nrpic_newton_fft_green", DevExeSpace(), 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int k, const int j, const int i) {
    const Real kk = k2x(i) + k2y(j) + k2z(k);
    const Real g = (i == 0 && j == 0 && k == 0) ? 0.0 : fac/kk;
    fb(0,k,j,i) *= g;
    fb(1,k,j,i) *= g;
  });

  NrpicNewtonFftLines(0, true, nw_fft_b, nw_fft_a);
  NrpicNewtonFftLines(1, true, nw_fft_a, nw_fft_b);
  NrpicNewtonFftLines(2, true, nw_fft_b, nw_fft_a);

  auto phi = pg->phi;
  par_for("nrpic_newton_fft_store", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    const int gi = off(m,0) + i - is, gj = off(m,1) + j - js, gk = off(m,2) + k - ks;
    phi(m,0,k,j,i) = fa(0,gk,gj,gi);
  });
}

} // namespace particles
