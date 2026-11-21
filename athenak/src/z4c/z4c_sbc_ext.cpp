//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file z4c_sbc_ext.cpp
//! \brief reading of the options of the outer faces of Z4c (z4c_sbc_ext.hpp).  Kept out
//! of the header so that the files which include z4c.hpp are compiled as without it.

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <string>

#include "athena.hpp"
#include "parameter_input.hpp"
#include "z4c/z4c_sbc_ext.hpp"

namespace z4c {

namespace {

void Fatal(const char *file, int line, const std::string &msg) {
  std::cout << "### FATAL ERROR in " << file << " at line " << line << std::endl
            << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

}  // namespace

//----------------------------------------------------------------------------------------
//! \fn void SbcExt::Read
//! \brief read the options of block <z4c> that are present in the input; an option that
//! is absent is not added, so the parameter dump of a run without them is unchanged.
void SbcExt::Read(ParameterInput *pin) {
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
  // removed options: refuse them unless they are at their neutral value
  for (const char *old : {"sbc_damp_gam", "sbc_damp_theta"}) {
    if (pin->DoesParameterExist("z4c", old) && pin->GetReal("z4c", old) != 0.0) {
      Fatal(__FILE__, __LINE__, std::string("<z4c> ") + old + " was removed: unstable "
            "in the expanding-ball test (tracks/core/JOURNAL-faces.md, entry 11)");
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

} // namespace z4c
