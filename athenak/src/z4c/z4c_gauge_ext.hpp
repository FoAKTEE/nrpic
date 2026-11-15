#ifndef Z4C_Z4C_GAUGE_EXT_HPP_
#define Z4C_Z4C_GAUGE_EXT_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file z4c_gauge_ext.hpp
//! \brief Gauge terms for expanding matter and for black holes of unequal mass.
//!
//! Two additions to the moving-puncture gauge of Z4c::CalcRHS, both off unless their
//! parameters are present in <z4c> (nothing is added to the parameter list otherwise,
//! so that existing inputs run and write exactly as before):
//!
//! 1. Lapse: relaxation of the excess of the lapse over a reference value,
//!      d_t alpha += - (alpha/T) max(ln(alpha/alpha_0), 0),   1/T = lapse_leak.
//!    Where the normal observers diverge (expanding matter, Khat < 0) the 1+log
//!    condition d_t alpha = -2 alpha Khat lets the lapse grow as the logarithm of the
//!    volume element; with the term the lapse follows exp(-2 T Khat) instead, bounded
//!    and tending to alpha_0 as the expansion slows, and the difference of lapse across
//!    a surface where Khat jumps stays of order 2 T (jump of Khat) instead of growing.
//!    The principal part of the system is that of 1+log (the term has no derivative),
//!    and nothing changes where the lapse is below alpha_0: a collapsing region and a
//!    black hole are sliced by the plain 1+log condition.
//!
//! 2. Shift: damping coefficient that depends on the tracked black holes,
//!      eta(x) = eta_0 [1 + sum_A (M_ref/m_A - 1)/(1 + |x - x_A|^2/w_A^2)],
//!    with eta_0 = shift_eta, x_A and m_A the position and mass of compact-object
//!    tracker A (<z4c> co_<A>_mass), w_A = shift_eta_width times the smallest mass (or
//!    times m_A with shift_eta_width_local = true).  With M_ref = shift_eta_mref the
//!    coefficient tends to eta_0 M_ref/m_A at black hole A and to eta_0 far away; this
//!    is the profile of arXiv:2611.12831 (text below its shift equation), there with
//!    width 2.
//!
//! Derivation, tests and run ids: tracks/core/interfaces/cosmo_gauge.md and
//! tracks/core/JOURNAL-gauge.md.

#include <cmath>
#include <iostream>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"

namespace z4c {

//! largest number of tracked black holes that shape the damping coefficient
constexpr int kGaugeExtMaxPunc = 8;

//----------------------------------------------------------------------------------------
//! \struct GaugeExtOptions
//! \brief parameters of the two terms, read once in the Z4c constructor

struct GaugeExtOptions {
  Real lapse_leak = 0.0;         // rate 1/T of the relaxation of the excess lapse
  Real lapse_leak_alpha = 1.0;   // reference lapse alpha_0
  bool eta_profile = false;      // damping coefficient that follows the trackers
  Real eta_mref = 1.0;           // reference mass M_ref
  Real eta_width = 2.0;          // width of the profile in units of the mass
  bool eta_width_local = false;  // width from m_A instead of the smallest mass

  //! read the parameters that are present; absent ones keep their defaults and are
  //! not added to the parameter list
  void Read(ParameterInput *pin) {
    if (pin->DoesParameterExist("z4c", "lapse_leak")) {
      lapse_leak = pin->GetReal("z4c", "lapse_leak");
    }
    if (pin->DoesParameterExist("z4c", "lapse_leak_alpha")) {
      lapse_leak_alpha = pin->GetReal("z4c", "lapse_leak_alpha");
    }
    if (pin->DoesParameterExist("z4c", "shift_eta_profile")) {
      eta_profile = pin->GetBoolean("z4c", "shift_eta_profile");
    }
    if (pin->DoesParameterExist("z4c", "shift_eta_mref")) {
      eta_mref = pin->GetReal("z4c", "shift_eta_mref");
    }
    if (pin->DoesParameterExist("z4c", "shift_eta_width")) {
      eta_width = pin->GetReal("z4c", "shift_eta_width");
    }
    if (pin->DoesParameterExist("z4c", "shift_eta_width_local")) {
      eta_width_local = pin->GetBoolean("z4c", "shift_eta_width_local");
    }
    if (lapse_leak < 0.0 || lapse_leak_alpha <= 0.0 || eta_mref <= 0.0
        || eta_width <= 0.0) {
      std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__
                << std::endl
                << "<z4c> lapse_leak must not be negative; lapse_leak_alpha, "
                << "shift_eta_mref and shift_eta_width must be positive" << std::endl;
      std::exit(EXIT_FAILURE);
    }
    if (global_variable::my_rank == 0 && (lapse_leak > 0.0 || eta_profile)) {
      std::cout << "Z4c gauge:";
      if (lapse_leak > 0.0) {
        std::cout << " lapse excess over " << lapse_leak_alpha
                  << " relaxes at the rate " << lapse_leak << ";";
      }
      if (eta_profile) {
        std::cout << " shift damping follows the trackers (M_ref = " << eta_mref
                  << ", width " << eta_width << " times "
                  << (eta_width_local ? "each mass" : "the smallest mass") << ")";
      }
      std::cout << std::endl;
    }
  }
};

//----------------------------------------------------------------------------------------
//! \struct GaugeExt
//! \brief the two terms as they are evaluated in the kernel of Z4c::CalcRHS; a plain
//! aggregate that the kernel captures by value

struct GaugeExt {
  Real leak_rate;                 // 1/T; zero switches the term off
  Real leak_log0;                 // ln(alpha_0)
  int npunc;                      // number of black holes in the profile; zero: constant
  Real px[kGaugeExtMaxPunc];      // tracker positions
  Real py[kGaugeExtMaxPunc];
  Real pz[kGaugeExtMaxPunc];
  Real amp[kGaugeExtMaxPunc];     // M_ref/m_A - 1
  Real iw2[kGaugeExtMaxPunc];     // 1/w_A^2

  //! contribution to d_t alpha
  KOKKOS_INLINE_FUNCTION
  Real LapseLeak(const Real alpha) const {
    const Real ex = log(fmax(alpha, 1.0e-30)) - leak_log0;
    return (ex > 0.0) ? -leak_rate*alpha*ex : 0.0;
  }

  //! eta(x)/eta_0
  KOKKOS_INLINE_FUNCTION
  Real EtaFactor(const Real x1, const Real x2, const Real x3) const {
    Real f = 1.0;
    for (int n = 0; n < npunc; ++n) {
      const Real r2 = SQR(x1 - px[n]) + SQR(x2 - py[n]) + SQR(x3 - pz[n]);
      f += amp[n]/(1.0 + r2*iw2[n]);
    }
    return fmax(f, 0.0);
  }
};

//----------------------------------------------------------------------------------------
//! \fn GaugeExt MakeGaugeExt
//! \brief the terms for the current positions of the trackers (called once per stage).
//! TrackerList is the vector of pointers to CompactObjectTracker of the Z4c class; the
//! caller includes z4c/compact_object_tracker.hpp.

template <class TrackerList>
GaugeExt MakeGaugeExt(const GaugeExtOptions &go, const TrackerList &trackers) {
  GaugeExt gx;
  gx.leak_rate = go.lapse_leak;
  gx.leak_log0 = std::log(go.lapse_leak_alpha);
  gx.npunc = 0;
  for (int n = 0; n < kGaugeExtMaxPunc; ++n) {
    gx.px[n] = 0.0; gx.py[n] = 0.0; gx.pz[n] = 0.0;
    gx.amp[n] = 0.0; gx.iw2[n] = 0.0;
  }
  if (!go.eta_profile) { return gx; }

  // black holes with a stated mass, in the order of the trackers
  Real mmin = -1.0;
  for (auto &pt : trackers) {
    const Real m = pt->GetMass();
    if (m > 0.0 && (mmin < 0.0 || m < mmin)) { mmin = m; }
  }
  for (auto &pt : trackers) {
    const Real m = pt->GetMass();
    if (m <= 0.0) { continue; }
    if (gx.npunc == kGaugeExtMaxPunc) {
      std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__
                << std::endl << "shift_eta_profile takes at most "
                << kGaugeExtMaxPunc << " trackers with a mass" << std::endl;
      std::exit(EXIT_FAILURE);
    }
    const int n = gx.npunc++;
    gx.px[n] = pt->GetPos(0);
    gx.py[n] = pt->GetPos(1);
    gx.pz[n] = pt->GetPos(2);
    gx.amp[n] = go.eta_mref/m - 1.0;
    const Real w = go.eta_width*(go.eta_width_local ? m : mmin);
    gx.iw2[n] = 1.0/(w*w);
  }
  return gx;
}

} // namespace z4c
#endif // Z4C_Z4C_GAUGE_EXT_HPP_
