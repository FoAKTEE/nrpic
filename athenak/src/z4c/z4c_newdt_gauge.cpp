//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file z4c_newdt_gauge.cpp
//! \brief Step limit of Z4c from the stability bound of the time integrator for the gauge
//! sectors, <z4c> dt_gauge.
//!
//! The limits of z4c_newdt.cpp count the cell size and, with dt_lightspeed, the
//! coordinate speed of light.  The gauge has speeds of its own, which do not fall with
//! the conformal factor as the speed of light does: the Gamma-driver shift
//!   d_t beta^i = mu Gam^i - eta beta^i,   d_t Gam^i = gt^jk d_j d_k beta^i + ...
//! propagates with sqrt(mu gt^dd) (transverse) and sqrt(4 mu/3 gt^dd) (longitudinal) in
//! coordinates, mu = shift_Gamma + alpha^2 shift_alpha2Gamma, and the lapse
//!   d_t alpha = -f alpha Khat - (relaxation),   d_t Khat = -chi gt^ij d_i d_j alpha + ...
//! with sqrt(f alpha chi gt^dd), sqrt(2 alpha chi gt^dd) for 1+log.  In an expanding box
//! the speed of light alpha sqrt(chi gt^dd) falls below both.
//!
//! What is evaluated in every cell is not a speed but the largest stable step of the
//! scheme for each of three pairs of fields with frozen coefficients (shift and Gam,
//! lapse and Khat, and a pair that moves with the speed of light): the eigenvalues of
//! the pair for the Fourier mode at the corner of the Brillouin zone, (pi, pi, pi),
//!   lambda = -(D + (e1 + e2)/2) +- sqrt(((e1 - e2)/2)^2 - Omega^2),
//!   Omega^2 = s2max sum_d (squared speed along d) / dx_d^2,
//! with s2max the symbol of the centred second derivative at pi, D the Kreiss-Oliger
//! term diss sum_d 1/dx_d, and e1, e2 the damping of the two members (shift damping eta
//! or lapse relaxation, and the advective derivative, whose symbol at pi is real and
//! negative).  At the corner the mixed derivatives vanish, so the three shift modes have
//! the transverse speed there.  The advective derivative also turns the phase, most at
//! theta near 0.68 pi; that largest rate, limag sum_d |beta^d|/dx_d, is added to Omega
//! (with the damping of the corner alone the bound was up to 1.56 times too large for
//! a shift of order one).  The step is stable when lambda dt lies inside the
//! stability region of the Runge-Kutta scheme; the radius of the region along the ray of
//! lambda comes from a table made once.  The mode without spatial structure adds the
//! bound (radius on the real axis)/(damping rate): lapse_leak dt <= 2.785 for rk4.
//!
//! Derivation, the scan of the whole Brillouin zone this was checked against, tests and
//! run ids: tracks/core/interfaces/step_limit.md, tracks/core/JOURNAL-step-limit.md,
//! tracks/core/analysis/step_limit/vonneumann_gauge.py (the function reduced_bound there
//! is the twin of PairBound here).

#include <math.h>

#include <algorithm>
#include <iostream>
#include <limits>
#include <string>

#include "athena.hpp"
#include "globals.hpp"
#include "mesh/mesh.hpp"
#include "driver/driver.hpp"
#include "coordinates/cell_locations.hpp"
#include "z4c/compact_object_tracker.hpp"
#include "z4c/z4c.hpp"

#if MPI_PARALLEL_ENABLED
#include <mpi.h>
#endif

namespace z4c {

namespace {

//! entries of the table of first-exit radii, at the angles (pi/2) i/(kNTab-1) from the
//! negative real axis
constexpr int kNTab = 129;

struct StabTable {
  Real rho[kNTab];
};

//! |R(z)| of the stability polynomial sum_{k <= order} z^k/k! (the two-register schemes
//! rk3 and rk4 of driver.cpp have it; checked in vonneumann_gauge.py)
Real AbsStabPoly(const int order, const Real re, const Real im) {
  Real pr = 1.0, pi = 0.0;        // Horner: p = 1 + z/order (...)
  for (int k = order; k >= 1; --k) {
    const Real tr = (pr*re - pi*im)/static_cast<Real>(k);
    const Real ti = (pr*im + pi*re)/static_cast<Real>(k);
    pr = 1.0 + tr;
    pi = ti;
  }
  return std::sqrt(pr*pr + pi*pi);
}

//! smallest radius at which the ray at the angle phi from the negative real axis leaves
//! the stability region
Real FirstExit(const int order, const Real phi) {
  const Real c = -std::cos(phi), s = std::sin(phi);
  const Real step = 2.0e-3, tol = 1.0e-12;
  for (Real r = step; r < 12.0; r += step) {
    if (AbsStabPoly(order, r*c, r*s) > 1.0 + tol) {
      Real lo = r - step, hi = r;
      for (int it = 0; it < 40; ++it) {
        const Real mid = 0.5*(lo + hi);
        if (AbsStabPoly(order, mid*c, mid*s) > 1.0 + tol) { hi = mid; } else { lo = mid; }
      }
      return lo;
    }
  }
  return 12.0;
}

StabTable MakeStabTable(const int order) {
  StabTable t;
  for (int i = 0; i < kNTab; ++i) {
    t.rho[i] = FirstExit(order, 0.5*M_PI*static_cast<Real>(i)/static_cast<Real>(kNTab-1));
  }
  return t;
}

//! order of the stability polynomial of the integrator; 0: not tabulated
int StabOrder(const std::string &integrator) {
  if (integrator == "rk4") { return 4; }
  if (integrator == "rk3") { return 3; }
  return 0;
}

//! radius of the stability region along the ray of the eigenvalue (re, im), re <= 0: the
//! smaller of the two neighbouring entries of the table
KOKKOS_INLINE_FUNCTION
Real StabRadius(const StabTable &tab, const Real re, const Real im) {
  Real x = atan2(fabs(im), -re)*(static_cast<Real>(kNTab-1)/(0.5*M_PI));
  x = fmin(fmax(x, 0.0), static_cast<Real>(kNTab-1));
  int i = static_cast<int>(x);
  if (i > kNTab-2) { i = kNTab-2; }
  return fmin(tab.rho[i], tab.rho[i+1]);
}

//! largest stable step of a pair of fields: om the frequency Omega of the corner mode
//! (wave part plus the phase rate of the advective derivative), dko the Kreiss-Oliger
//! rate, e1 and e2 the damping rates of the two members at the corner, dh the damping
//! rate of the mode without spatial structure
KOKKOS_INLINE_FUNCTION
Real PairBound(const StabTable &tab, const Real om, const Real dko, const Real e1,
               const Real e2, const Real dh) {
  const Real m = dko + 0.5*(e1 + e2);
  const Real h = 0.5*(e1 - e2);
  const Real disc = h*h - om*om;
  Real re, im;
  if (disc <= 0.0) {
    re = -m;
    im = sqrt(-disc);
  } else {
    re = -(m + sqrt(disc));
    im = 0.0;
  }
  const Real mod = sqrt(re*re + im*im);
  Real dt = static_cast<Real>(std::numeric_limits<float>::max());
  if (mod > 0.0) { dt = StabRadius(tab, re, im)/mod; }
  if (dh > 0.0) { dt = fmin(dt, tab.rho[0]/dh); }
  return dt;
}

const char *const kSector[3] = {"Gamma-driver shift", "lapse", "light"};

} // namespace

//----------------------------------------------------------------------------------------
//! \fn Real Z4c::GaugeTimeStep(Driver *pdriver, Real bound[3], bool leak_everywhere)
//! \brief smallest value over the cells of the largest stable step of the three pairs
//! (bound[0] shift, bound[1] lapse, bound[2] light) for the integrator of the driver;
//! returns the smallest of the three.  With leak_everywhere the relaxation of the lapse
//! counts in every cell, also where the lapse is below its reference (for the warning at
//! start-up).  Cells whose conformal factor is not positive, or whose fields are not
//! finite, are skipped.  Without a table for the integrator the bounds are the largest
//! float.

Real Z4c::GaugeTimeStep(Driver *pdriver, Real bound[3], const bool leak_everywhere) {
  const Real big = static_cast<Real>(std::numeric_limits<float>::max());
  bound[0] = big; bound[1] = big; bound[2] = big;
  const int order = StabOrder(pdriver->integrator);
  if (order == 0) { return big; }
  static int tab_order = 0;
  static StabTable tab_made;
  if (tab_order != order) {
    tab_made = MakeStabTable(order);
    tab_order = order;
  }
  const StabTable tab = tab_made;

  auto &indcs = pmy_pack->pmesh->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int n1 = indcs.nx1, n2 = indcs.nx2, n3 = indcs.nx3;
  const int ncell = (pmy_pack->nmb_thispack)*n3*n2*n1;
  auto &mbsize = pmy_pack->pmb->mb_size;
  auto u = u0;
  const int ial = I_Z4C_ALPHA, ichi = I_Z4C_CHI, ibx = I_Z4C_BETAX, igxx = I_Z4C_GXX;
  const Real expo = -4.0/opt.chi_psi_power;

  // symbols of utils/finite_diff.hpp: centred second derivative at theta = pi (s2max),
  // advective derivative at pi (aadv, real) and its largest imaginary part (limag)
  Real s2max = 272.0/45.0, aadv = 32.0/15.0, limag = 1.9501326011939233;
  if (indcs.ng == 2) { s2max = 4.0; aadv = 4.0; limag = 2.2018347375203207; }
  if (indcs.ng == 3) { s2max = 16.0/3.0; aadv = 8.0/3.0; limag = 1.9509966804685472; }
  const Real kdiss = fabs(opt.diss);
  // shift
  const Real mu0 = opt.shift_ggamma, mu2 = opt.shift_alpha2ggamma;
  const Real eta0 = fabs(opt.shift_eta), sadv = fabs(opt.shift_advect);
  // lapse: d_t alpha = -f alpha Khat with
  //   f = lapse_oplog lapse_harmonicf + lapse_harmonic alpha + lapse_volume/sqrt(chi)
  //       + lapse_kdriver alpha_ref
  const Real f0 = opt.lapse_oplog*opt.lapse_harmonicf
                  + opt.lapse_kdriver*opt.lapse_ref_alpha;
  const Real fh = opt.lapse_harmonic, fv = opt.lapse_volume;
  const Real ladv = fabs(opt.lapse_advect);
  // relaxation of the lapse and damping profile of the shift (z4c_gauge_ext.hpp)
  const GaugeExt gx = MakeGaugeExt(gext, ptracker);
  const Real leak = gx.leak_rate, log0 = gx.leak_log0;
  const bool eta_prof = (gx.npunc > 0);

  Real dts = big, dtl = big, dtc = big;
  Kokkos::parallel_reduce("Z4c dt gauge", Kokkos::RangePolicy<>(DevExeSpace(), 0, ncell),
  KOKKOS_LAMBDA(const int &idx, Real &min_s, Real &min_l, Real &min_c) {
    int m = idx/(n3*n2*n1);
    int rem = idx - m*(n3*n2*n1);
    int k = rem/(n2*n1);
    rem -= k*(n2*n1);
    int j = rem/n1;
    int i = rem - j*n1;
    k += ks; j += js; i += is;
    const Real gxx = u(m,igxx,k,j,i), gxy = u(m,igxx+1,k,j,i), gxz = u(m,igxx+2,k,j,i);
    const Real gyy = u(m,igxx+3,k,j,i), gyz = u(m,igxx+4,k,j,i), gzz = u(m,igxx+5,k,j,i);
    const Real det = gxx*(gyy*gzz - gyz*gyz) - gxy*(gxy*gzz - gyz*gxz)
                     + gxz*(gxy*gyz - gyy*gxz);
    const Real chi = u(m,ichi,k,j,i);
    const Real alp = u(m,ial,k,j,i);
    const Real bx = u(m,ibx,k,j,i), by = u(m,ibx+1,k,j,i), bz = u(m,ibx+2,k,j,i);
    if (!(det > 0.0) || !(chi > 0.0)
        || !(Kokkos::isfinite(alp + chi + det + bx + by + bz))) return;
    // inverse conformal metric; gt^ij k_i k_j is bounded by sum_d G_d k_d^2 with the
    // sums of the absolute values of the rows
    const Real uxx = (gyy*gzz - gyz*gyz)/det, uyy = (gxx*gzz - gxz*gxz)/det;
    const Real uzz = (gxx*gyy - gxy*gxy)/det;
    const Real uxy = fabs((gxz*gyz - gxy*gzz)/det), uxz = fabs((gxy*gyz - gxz*gyy)/det);
    const Real uyz = fabs((gxy*gxz - gxx*gyz)/det);
    const Real idx1 = 1.0/mbsize.d_view(m).dx1, idx2 = 1.0/mbsize.d_view(m).dx2;
    const Real idx3 = 1.0/mbsize.d_view(m).dx3;
    const Real q = (uxx + uxy + uxz)*idx1*idx1 + (uyy + uxy + uyz)*idx2*idx2
                   + (uzz + uxz + uyz)*idx3*idx3;
    if (!(q > 0.0) || !(Kokkos::isfinite(q))) return;
    const Real dko = kdiss*(idx1 + idx2 + idx3);
    const Real bsum = fabs(bx)*idx1 + fabs(by)*idx2 + fabs(bz)*idx3;
    const Real adv = aadv*bsum;              // damping of the corner mode by advection
    const Real oma = limag*bsum;             // largest phase rate of the advection
    const Real chig = pow(chi, expo);        // gamma^ij = chig gt^ij

    // shift and Gam
    Real eta = eta0;
    if (eta_prof) {
      eta *= gx.EtaFactor(
          CellCenterX(i - is, n1, mbsize.d_view(m).x1min, mbsize.d_view(m).x1max),
          CellCenterX(j - js, n2, mbsize.d_view(m).x2min, mbsize.d_view(m).x2max),
          CellCenterX(k - ks, n3, mbsize.d_view(m).x3min, mbsize.d_view(m).x3max));
    }
    const Real mu = fabs(mu0 + mu2*alp*alp);
    min_s = fmin(min_s, PairBound(tab, sqrt(s2max*mu*q) + oma, dko, eta + sadv*adv,
                                  adv, eta));

    // lapse and Khat
    const Real f = f0 + fh*alp + ((fv != 0.0) ? fv/sqrt(chi) : 0.0);
    Real delta = 0.0;
    if (leak > 0.0) {
      const Real ex = log(fmax(alp, 1.0e-30)) - log0;
      if (ex >= 0.0 || leak_everywhere) { delta = leak*(1.0 + fmax(ex, 0.0)); }
    }
    min_l = fmin(min_l, PairBound(tab, sqrt(s2max*fabs(f*alp)*chig*q) + oma, dko,
                                  delta + ladv*adv, adv, delta));

    // a pair with the speed of light
    min_c = fmin(min_c, PairBound(tab, sqrt(s2max*alp*alp*chig*q) + oma, dko, adv, adv,
                                  0.0));
  }, Kokkos::Min<Real>(dts), Kokkos::Min<Real>(dtl), Kokkos::Min<Real>(dtc));

  bound[0] = dts; bound[1] = dtl; bound[2] = dtc;
  return std::min(dts, std::min(dtl, dtc));
}

//----------------------------------------------------------------------------------------
//! \fn void Z4c::GaugeStepLimit(Driver *pdriver, Real dx_min)
//! \brief called at the end of Z4c::NewTimeStep with dtnew set by the cell size (dx_min)
//! and by dt_lightspeed.  With <z4c> dt_gauge = f > 0 the step is also kept at or below
//! f times the stability bound of GaugeTimeStep; dtnew is multiplied by cfl_number in
//! Mesh::NewTimeStep, so the bound is divided by it here.  At the first call the bound
//! is evaluated in any case: with the option a line states it; without it a warning is
//! printed when cfl_number x dx_min, the largest step the other limits allow, exceeds
//! it, and when lapse_leak times that step is beyond the bound of the relaxed lapse.
//! Nothing else is done without the option.

void Z4c::GaugeStepLimit(Driver *pdriver, const Real dx_min) {
  const bool first = ((dt_gauge_state & 1) == 0);
  if (!first && !(dt_gauge > 0.0)) { return; }
  const Real big = static_cast<Real>(std::numeric_limits<float>::max());
  const Real cfl = pmy_pack->pmesh->cfl_no;
  const bool tabulated = (StabOrder(pdriver->integrator) != 0);
  if (dt_gauge > 0.0 && !tabulated) {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "<z4c> dt_gauge needs <time> integrator = rk3 or rk4 (given: "
              << pdriver->integrator << ")" << std::endl;
    std::exit(EXIT_FAILURE);
  }

  const Real dt_other = dtnew;      // limit of the cell size and of dt_lightspeed
  const Real bmin = GaugeTimeStep(pdriver, dt_gauge_bound, false);
  int sec = 0;
  if (dt_gauge_bound[1] < dt_gauge_bound[sec]) { sec = 1; }
  if (dt_gauge_bound[2] < dt_gauge_bound[sec]) { sec = 2; }

  if (dt_gauge > 0.0 && bmin < big && cfl > 0.0) {
    const Real lim = dt_gauge*bmin/cfl;
    if (lim < dtnew) {
      dtnew = lim;
      // name each sector the first time it sets the step
      if ((dt_gauge_state & (2 << sec)) == 0) {
        dt_gauge_state |= (2 << sec);
        if (global_variable::my_rank == 0) {
          std::cout << "Z4c step limit: at time " << pmy_pack->pmesh->time
                    << " the step of Z4c is set by dt_gauge, sector " << kSector[sec]
                    << ": " << dt_gauge*bmin << " (cell size and dt_lightspeed allow "
                    << cfl*dt_other << ")" << std::endl;
        }
      }
    }
  }
  if (!first) { return; }
  dt_gauge_state |= 1;
  if (!tabulated) { return; }

  // ---- once at start-up: the bound, and a warning when the other limits exceed it
  Real bl[3];
  GaugeTimeStep(pdriver, bl, true);   // the lapse with its relaxation in every cell
  Real v[6] = {dt_gauge_bound[0], dt_gauge_bound[1], dt_gauge_bound[2], bl[1], dx_min,
               dt_other};
#if MPI_PARALLEL_ENABLED
  MPI_Allreduce(MPI_IN_PLACE, v, 6, MPI_ATHENA_REAL, MPI_MIN, MPI_COMM_WORLD);
#endif
  if (global_variable::my_rank != 0) { return; }
  int s = 0;
  if (v[1] < v[s]) { s = 1; }
  if (v[2] < v[s]) { s = 2; }
  const Real bound = v[s];
  const Real step_now = cfl*v[5];   // what Z4c allows at the first step
  const Real step_cap = cfl*v[4];   // what it may grow to: cfl_number x dx_min
  if (dt_gauge > 0.0) {
    std::cout << "Z4c step limit: dt_gauge = " << dt_gauge << " keeps the step at or "
              << "below that fraction of the stability bound of " << pdriver->integrator
              << " (nghost " << pmy_pack->pmesh->mb_indcs.ng << ", diss " << opt.diss
              << "); at the start, in units of the smallest cell " << v[4] << ": "
              << kSector[0] << " " << v[0]/v[4] << ", " << kSector[1] << " " << v[1]/v[4]
              << ", " << kSector[2] << " " << v[2]/v[4] << "; cfl_number " << cfl
              << std::endl;
    if (dt_gauge > 1.0) {
      std::cout << "### WARNING (Z4c step limit): dt_gauge = " << dt_gauge
                << " is above 1, the step may exceed the stability bound" << std::endl;
    }
  } else if (step_cap > bound) {
    std::cout << "### WARNING (Z4c step limit): cfl_number x (smallest cell) = "
              << step_cap << " exceeds the stability bound " << bound << " of "
              << pdriver->integrator << " for the sector " << kSector[s] << " ("
              << bound/v[4] << " cells; " << kSector[0] << " " << v[0]/v[4] << ", "
              << kSector[1] << " " << v[1]/v[4] << ", " << kSector[2] << " "
              << v[2]/v[4] << "). ";
    if (step_now > bound) {
      std::cout << "The first step " << step_now << " is already above it: growth at "
                << "the grid scale is expected. ";
    } else {
      std::cout << "The first step is " << step_now << "; the step may pass the bound "
                << "when the other limits (dt_lightspeed, particles) release it. ";
    }
    std::cout << "Set <z4c> dt_gauge = 0.9, or cfl_number at or below "
              << 0.9*bound/v[4] << "." << std::endl;
  }
  // the relaxation of the lapse alone
  if (gext.lapse_leak > 0.0 && !(dt_gauge > 0.0) && step_cap > v[3]) {
    std::cout << "### WARNING (Z4c step limit): lapse_leak x cfl_number x (smallest "
              << "cell) = " << gext.lapse_leak*step_cap << " is beyond the bound "
              << gext.lapse_leak*v[3] << " of the relaxed lapse (lapse_leak x step <= "
              << "2.785 for rk4 without spatial structure, less at the grid scale): "
              << "where the lapse exceeds lapse_leak_alpha the relaxation is stiff. Set "
              << "<z4c> dt_gauge = 0.9, or lower cfl_number or lapse_leak." << std::endl;
  }
  return;
}

} // namespace z4c
