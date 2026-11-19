#ifndef Z4C_Z4C_SBC_EXT_HPP_
#define Z4C_Z4C_SBC_EXT_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file z4c_sbc_ext.hpp
//! \brief options of the outer faces of Z4c beyond the stock Sommerfeld condition of
//! z4c_Sbc.cpp and the Lagrange extrapolation of the ghost cells of z4c_bcs.cpp.  Every
//! option is read only if it is present in the input, so that a run without any of them
//! has the same parameter dump, and the same results, as before.
//!
//! 1. Right-hand side of the outermost active cells (z4c_Sbc.cpp, Z4cBoundaryRHSExt).
//!
//! The Sommerfeld condition d_t f = -v (s^k d_k f + f/r) assumes f = u(r - v t)/r.  A
//! field with a part that is not a wave, f = u(r - v t)/r + h(t)/r^n (stationary
//! extrinsic curvature of a Painleve-Gullstrand exterior, n = 3/2, or of a Bowen-York
//! puncture, n = 2; slow gauge evolution), is driven by that condition at the rate
//! v (n - 1) f/r.  Following Alcubierre et al., arXiv:gr-qc/0206072 (section "Outer
//! boundary condition"), the part of the right-hand side that the wave operator does not
//! account for is measured one cell inside, where the full right-hand side is known, and
//! carried to the boundary cell with a power law:
//!
//!   d_t f |_b = R[f]_b + ( d_t f - R[f] )_p (r_p / r_b)^q,
//!   R[f] = -v (s^k d_k f + f/r) + a beta^k d_k f,
//!
//! with p the cell one step inward along every direction in which the cell b lies on a
//! physical face (so p is never a boundary cell itself, and edge and corner cells need
//! no special case).  For a stationary f ~ r^-n the bracket falls as r^-(n+1), so
//! q = n + 1 keeps f exactly stationary; with another q the residual is smaller than
//! the plain Sommerfeld error by (q - n - 1) dx / r.  The derivatives in R are centred
//! of second order as in z4c_Sbc.cpp.
//!
//! The speeds v (sbc_speed): unit (v = 1, v = sbc_v_khat for Khat, a = 0: the stock
//! condition); lapse (v = alpha, v = sqrt(f alpha) for Khat with d_t alpha = -f alpha
//! Khat, a = 1: arXiv:1212.2901 eqs. (Sommerfeld_first)-(Sommerfeld_last)); metric (the
//! coordinate speeds along s, v = alpha sqrt(chi / gt_ss) and sqrt(f alpha chi / gt_ss),
//! a = 1).
//!
//! Theta (sbc_theta): sommerfeld (R[Theta]); nonwave (as Khat, power sbc_power_theta);
//! cpbc (d_t Theta = -alpha s^k d_k Theta + beta^k d_k Theta, the condition of the
//! constraint-preserving set of arXiv:1212.2901, eq. after (eq:long_shift_BC): no 1/r
//! term, so a Theta that the interior sends out is not damped at the face but carried
//! out with the lapse).
//!
//! 2. Ghost cells (z4c_bcs_falloff.cpp, Z4c::GhostFalloff).
//!
//! The stock fill extrapolates f itself along the face normal with a polynomial through
//! extrap_order cells; a static far field f = f_inf + c/r then has ghost errors of
//! delta (delta + 1)/2 f'' dx^2 (linear) that every centred stencil near the face reads.
//! With ghost_falloff = true the polynomial extrapolates G = (f - f_inf) r^q instead and
//! the ghost value is f_inf + G/r^q: exact for f_inf + c/r^q, and for f ~ r^-m the
//! leading error is |m - q|/(m + 1) of the stock one.  Asymptotic values: chi, gt_xx,
//! gt_yy, gt_zz, alpha -> 1; all other variables -> 0.  Powers: ghost_power_metric for
//! chi, gt_ij, alpha, beta^i; ghost_power_curv for Khat, A_ij, Gamma^i, Theta.
//!
//! Options (block <z4c>; each is read only if present, except the dependent ones):
//!   sbc_variant     = sommerfeld | nonwave      (default sommerfeld)
//!   sbc_power_khat  = q of Khat                 (default 3; with nonwave)
//!   sbc_power_a     = q of A_ij                 (default 3; with nonwave)
//!   sbc_power_gam   = q of Gamma^i              (default 3; with nonwave)
//!   sbc_theta       = sommerfeld | nonwave | cpbc  (default sommerfeld)
//!   sbc_power_theta = q of Theta                (default 3; with sbc_theta = nonwave)
//!   sbc_v_khat      = speed of Khat for sbc_speed = unit (default sqrt 2)
//!   sbc_speed       = unit | lapse | metric     (default unit)
//!   ghost_falloff   = false | true              (default false)
//!   ghost_power_metric = power q of the ghost fill of chi, gt_ij, alpha, beta (default 1)
//!   ghost_power_curv   = power q of the ghost fill of Khat, A_ij, Gamma, Theta (default 1)

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <string>

#include "athena.hpp"
#include "parameter_input.hpp"

namespace z4c {

//----------------------------------------------------------------------------------------
//! \struct SbcExt
//! \brief options of the outer faces beyond the stock conditions
struct SbcExt {
  int variant = 0;        // 0: Sommerfeld of z4c_Sbc.cpp; 1: with the non-wave part
  bool theta_nonwave = false;
  int theta_mode = 0;     // 0 sommerfeld, 1 nonwave, 2 cpbc
  int speed = 0;          // 0 unit, 1 lapse, 2 metric
  Real v_khat = 1.4142135623730951;
  Real q_khat = 3.0;
  Real q_a = 3.0;
  Real q_gam = 3.0;
  Real q_theta = 3.0;
  bool ghost_falloff = false;
  Real ghost_q_metric = 1.0;
  Real ghost_q_curv = 1.0;

  // true if the right-hand side of the boundary cells differs from the stock condition
  bool Extended() const { return variant != 0 || theta_mode != 0 || speed != 0; }

  static void Fatal(const char *file, int line, const std::string &msg) {
    std::cout << "### FATAL ERROR in " << file << " at line " << line << std::endl
              << msg << std::endl;
    std::exit(EXIT_FAILURE);
  }

  void Read(ParameterInput *pin) {
    if (pin->DoesParameterExist("z4c", "sbc_variant")) {
      const std::string v = pin->GetString("z4c", "sbc_variant");
      if (v.compare("sommerfeld") == 0) {
        variant = 0;
      } else if (v.compare("nonwave") == 0) {
        variant = 1;
      } else {
        Fatal(__FILE__, __LINE__, "<z4c> sbc_variant = '" + v +
              "' not recognized (sommerfeld, nonwave)");
      }
      if (variant == 1) {
        q_khat = pin->GetOrAddReal("z4c", "sbc_power_khat", 3.0);
        q_a = pin->GetOrAddReal("z4c", "sbc_power_a", 3.0);
        q_gam = pin->GetOrAddReal("z4c", "sbc_power_gam", 3.0);
        v_khat = pin->GetOrAddReal("z4c", "sbc_v_khat", std::sqrt(2.0));
        // as in the first version of this option: the Theta options are dumped with it
        (void) pin->GetOrAddString("z4c", "sbc_theta", "sommerfeld");
        q_theta = pin->GetOrAddReal("z4c", "sbc_power_theta", 3.0);
      }
    }
    if (pin->DoesParameterExist("z4c", "sbc_v_khat")) {
      v_khat = pin->GetReal("z4c", "sbc_v_khat");
    }
    if (pin->DoesParameterExist("z4c", "sbc_theta")) {
      const std::string th = pin->GetString("z4c", "sbc_theta");
      if (th.compare("sommerfeld") == 0) {
        theta_mode = 0;
      } else if (th.compare("nonwave") == 0) {
        theta_mode = 1;
        q_theta = pin->GetOrAddReal("z4c", "sbc_power_theta", 3.0);
      } else if (th.compare("cpbc") == 0) {
        theta_mode = 2;
      } else {
        Fatal(__FILE__, __LINE__, "<z4c> sbc_theta = '" + th +
              "' not recognized (sommerfeld, nonwave, cpbc)");
      }
      theta_nonwave = (theta_mode == 1);
    }
    if (pin->DoesParameterExist("z4c", "sbc_speed")) {
      const std::string sp = pin->GetString("z4c", "sbc_speed");
      if (sp.compare("unit") == 0) {
        speed = 0;
      } else if (sp.compare("lapse") == 0) {
        speed = 1;
      } else if (sp.compare("metric") == 0) {
        speed = 2;
      } else {
        Fatal(__FILE__, __LINE__, "<z4c> sbc_speed = '" + sp +
              "' not recognized (unit, lapse, metric)");
      }
    }
    if (pin->DoesParameterExist("z4c", "ghost_falloff")) {
      ghost_falloff = pin->GetBoolean("z4c", "ghost_falloff");
      if (ghost_falloff) {
        ghost_q_metric = pin->GetOrAddReal("z4c", "ghost_power_metric", 1.0);
        ghost_q_curv = pin->GetOrAddReal("z4c", "ghost_power_curv", 1.0);
      }
    }
  }
};

} // namespace z4c
#endif // Z4C_Z4C_SBC_EXT_HPP_
