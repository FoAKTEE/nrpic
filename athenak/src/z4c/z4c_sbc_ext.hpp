#ifndef Z4C_Z4C_SBC_EXT_HPP_
#define Z4C_Z4C_SBC_EXT_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file z4c_sbc_ext.hpp
//! \brief radiative condition with a non-wave part at the outer faces of the Z4c
//! variables Khat, Gamma^i, A_ij (and Theta on request).  Selected by
//! <z4c> sbc_variant = nonwave; the default (sommerfeld) is the condition of
//! z4c_Sbc.cpp, untouched.
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
//!   d_t f |_b = R[f]_b + ( d_t f - R[f] )_p (r_p / r_b)^q,   R[f] = -v (s^k d_k f + f/r),
//!
//! with p the cell one step inward along every direction in which the cell b lies on a
//! physical face (so p is never a boundary cell itself, and edge and corner cells need
//! no special case).  For a stationary f ~ r^-n the bracket falls as r^-(n+1), so
//! q = n + 1 keeps f exactly stationary; with another q the residual is smaller than
//! the plain Sommerfeld error by (q - n - 1) dx / r.  The derivatives in R are centred
//! of second order as in z4c_Sbc.cpp.
//!
//! Options (block <z4c>):
//!   sbc_variant     = sommerfeld | nonwave      (default sommerfeld: z4c_Sbc.cpp)
//!   sbc_power_khat  = q of Khat                 (default 3)
//!   sbc_power_a     = q of A_ij                 (default 3)
//!   sbc_power_gam   = q of Gamma^i              (default 3)
//!   sbc_theta       = sommerfeld | nonwave      (default sommerfeld: Theta has no
//!                                                non-wave part to keep, it is a constraint)
//!   sbc_power_theta = q of Theta                (default 3; read if sbc_theta = nonwave)
//!   sbc_v_khat      = speed of Khat             (default sqrt 2, the 1+log lapse far
//!                                                from the sources; sqrt(f alpha) for
//!                                                d_t alpha = -f alpha Khat)

#include <cmath>
#include <iostream>
#include <string>

#include "athena.hpp"
#include "parameter_input.hpp"

namespace z4c {

//----------------------------------------------------------------------------------------
//! \struct SbcExt
//! \brief options of the radiative condition with a non-wave part
struct SbcExt {
  int variant = 0;        // 0: Sommerfeld of z4c_Sbc.cpp; 1: with the non-wave part
  bool theta_nonwave = false;
  Real v_khat = 1.4142135623730951;
  Real q_khat = 3.0;
  Real q_a = 3.0;
  Real q_gam = 3.0;
  Real q_theta = 3.0;

  // The options are read only if sbc_variant is present in the input, so that a run
  // without it has the same parameter dump as before.
  void Read(ParameterInput *pin) {
    if (!pin->DoesParameterExist("z4c", "sbc_variant")) return;
    const std::string v = pin->GetString("z4c", "sbc_variant");
    if (v.compare("sommerfeld") == 0) {
      variant = 0;
      return;
    } else if (v.compare("nonwave") == 0) {
      variant = 1;
    } else {
      std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__
                << std::endl << "<z4c> sbc_variant = '" << v
                << "' not recognized (sommerfeld, nonwave)" << std::endl;
      std::exit(EXIT_FAILURE);
    }
    q_khat = pin->GetOrAddReal("z4c", "sbc_power_khat", 3.0);
    q_a = pin->GetOrAddReal("z4c", "sbc_power_a", 3.0);
    q_gam = pin->GetOrAddReal("z4c", "sbc_power_gam", 3.0);
    v_khat = pin->GetOrAddReal("z4c", "sbc_v_khat", std::sqrt(2.0));
    const std::string th = pin->GetOrAddString("z4c", "sbc_theta", "sommerfeld");
    if (th.compare("nonwave") == 0) {
      theta_nonwave = true;
      q_theta = pin->GetOrAddReal("z4c", "sbc_power_theta", 3.0);
    } else if (th.compare("sommerfeld") != 0) {
      std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__
                << std::endl << "<z4c> sbc_theta = '" << th
                << "' not recognized (sommerfeld, nonwave)" << std::endl;
      std::exit(EXIT_FAILURE);
    }
  }
};

} // namespace z4c
#endif // Z4C_Z4C_SBC_EXT_HPP_
