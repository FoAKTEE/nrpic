#ifndef PGEN_NRPIC_NRPIC_PUNCTURE_SETUP_HPP_
#define PGEN_NRPIC_NRPIC_PUNCTURE_SETUP_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_puncture_setup.hpp
//! \brief Tracker, initial refinement and apparent-horizon finder of every puncture
//! component of the problem generator nrpic_cf, written into the input parameters before
//! the mesh and the physics modules are built (called from main() for new runs; a
//! restart finds the parameters in the restart file).
//!
//! Active for <problem> pgen_name = nrpic_cf with puncture_setup = true.  The punctures
//! are numbered n = 0, 1, .. in the order of their components c.  For each one:
//!   <z4c> co_<n>_type = BH, co_<n>_x, _y, _z, co_<n>_mass, co_<n>_radius,
//!         co_<n>_reflevel            tracker, followed by the refinement (z4c_amr)
//!   <refined_region_punc<n>>         cube of half-width radius at level reflevel
//!   <fastflow> use_puncture_<n> = n and the flow parameters of horizon n
//! with
//!   radius    comp<c>_radius, default puncture_radius (default 2) times the bare mass
//!   reflevel  comp<c>_level, default puncture_level - round(log2(mass/lightest mass)),
//!             puncture_level by default the finest level, <mesh_refinement> num_levels-1
//!   flow_alpha_beta_const_<n> = mass^2 (the flow step relative to the radius scales as
//!             this constant over the mass squared), mass_tol_<n> = 1e-5 mass
//! puncture_horizons = false leaves out the finders.  Parameters the input file sets
//! itself are kept, except the tracker parameters, which are an error to set twice.

#include <cmath>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"

namespace nrpic_by {

inline void SetupFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_puncture_setup.hpp" << std::endl << msg
            << std::endl;
  std::exit(EXIT_FAILURE);
}

//! writes a real with all its digits (ParameterInput::SetReal keeps six)
inline void SetupSetReal(ParameterInput *pin, const std::string &block,
                         const std::string &name, const Real value) {
  char buf[64];
  std::snprintf(buf, sizeof(buf), "%.17g", value);
  pin->SetString(block, name, buf);
}

//----------------------------------------------------------------------------------------
//! \fn void NrpicPunctureSetup
//! \brief adds trackers, refined regions and horizon finders of the punctures to pin

inline void NrpicPunctureSetup(ParameterInput *pin) {
  if (!pin->DoesParameterExist("problem", "pgen_name")) return;
  if (pin->GetString("problem", "pgen_name").compare("nrpic_cf") != 0) return;
  if (!pin->DoesParameterExist("problem", "puncture_setup")) return;
  if (!pin->GetBoolean("problem", "puncture_setup")) return;

  const int ncomp = pin->GetInteger("problem", "ncomp");
  std::vector<int> comp;
  std::vector<Real> mass;
  Real mmin = 0.0;
  for (int c=0; c<ncomp; ++c) {
    const std::string pre = "comp" + std::to_string(c) + "_";
    if (pin->GetString("problem", pre + "type").compare("puncture") != 0) continue;
    const Real m = pin->GetReal("problem", pre + "mass");
    if (!(m > 0.0)) SetupFatal("puncture_setup needs positive puncture masses");
    comp.push_back(c);
    mass.push_back(m);
    mmin = (mmin == 0.0 || m < mmin) ? m : mmin;
  }
  const int npunc = static_cast<int>(comp.size());
  if (npunc == 0) return;

  const std::string ref = pin->DoesParameterExist("mesh_refinement", "refinement") ?
                          pin->GetString("mesh_refinement", "refinement") : "none";
  const bool multilevel = (ref.compare("none") != 0);
  int lfine = 0;
  if (pin->DoesParameterExist("problem", "puncture_level")) {
    lfine = pin->GetInteger("problem", "puncture_level");
  } else if (pin->DoesParameterExist("mesh_refinement", "num_levels")) {
    lfine = pin->GetInteger("mesh_refinement", "num_levels") - 1;
  } else if (multilevel) {
    SetupFatal("puncture_setup needs <problem> puncture_level or <mesh_refinement> "
               "num_levels");
  }
  const Real rfac = pin->GetOrAddReal("problem", "puncture_radius", 2.0);
  const bool horizons = pin->GetOrAddBoolean("problem", "puncture_horizons", true);

  // ---- trackers and refined regions
  const char *tkeys[7] = {"type", "x", "y", "z", "mass", "radius", "reflevel"};
  for (int n=0; n<npunc; ++n) {
    const std::string pre = "comp" + std::to_string(comp[n]) + "_";
    const std::string co = "co_" + std::to_string(n) + "_";
    for (int k=0; k<7; ++k) {
      if (pin->DoesParameterExist("z4c", co + tkeys[k])) {
        SetupFatal("<problem> puncture_setup = true sets <z4c> " + co + tkeys[k]
                   + "; remove it from the input (use " + pre + "radius, " + pre
                   + "level)");
      }
    }
    Real x[3];
    x[0] = pin->GetOrAddReal("problem", pre + "x1", 0.0);
    x[1] = pin->GetOrAddReal("problem", pre + "x2", 0.0);
    x[2] = pin->GetOrAddReal("problem", pre + "x3", 0.0);
    const Real radius = pin->DoesParameterExist("problem", pre + "radius") ?
                        pin->GetReal("problem", pre + "radius") : rfac*mass[n];
    int level = lfine - static_cast<int>(std::lround(std::log2(mass[n]/mmin)));
    if (pin->DoesParameterExist("problem", pre + "level")) {
      level = pin->GetInteger("problem", pre + "level");
    }
    level = (level < 0) ? 0 : level;
    pin->SetString("z4c", co + "type", "BH");
    SetupSetReal(pin, "z4c", co + "x", x[0]);
    SetupSetReal(pin, "z4c", co + "y", x[1]);
    SetupSetReal(pin, "z4c", co + "z", x[2]);
    SetupSetReal(pin, "z4c", co + "mass", mass[n]);
    SetupSetReal(pin, "z4c", co + "radius", radius);
    pin->SetInteger("z4c", co + "reflevel", level);
    if (multilevel && level > 0) {
      const std::string blk = "refined_region_punc" + std::to_string(n);
      if (pin->DoesBlockExist(blk)) SetupFatal("<" + blk + "> is set by puncture_setup");
      pin->SetInteger(blk, "level", level);
      const char *lo[3] = {"x1min", "x2min", "x3min"};
      const char *hi[3] = {"x1max", "x2max", "x3max"};
      for (int a=0; a<3; ++a) {
        SetupSetReal(pin, blk, lo[a], x[a] - radius);
        SetupSetReal(pin, blk, hi[a], x[a] + radius);
      }
    }
  }
  if (pin->DoesParameterExist("z4c", "co_" + std::to_string(npunc) + "_type")) {
    SetupFatal("<problem> puncture_setup = true defines all trackers; remove <z4c> co_"
               + std::to_string(npunc) + "_type");
  }
  // the refinement follows the trackers unless the input file chose otherwise
  if (ref.compare("adaptive") == 0) {
    pin->GetOrAddString("z4c_amr", "method", "tracker");
    bool has_crit = false;
    for (auto it = pin->block.begin(); it != pin->block.end(); ++it) {
      if (it->block_name.compare(0, 13, "amr_criterion") == 0) has_crit = true;
    }
    if (!has_crit) pin->SetString("amr_criterion_punc", "method", "user");
  }

  // ---- apparent-horizon finders, one per puncture, centred on its tracker
  if (horizons) {
    const int nh = pin->GetOrAddInteger("fastflow", "num_horizons", npunc);
    if (nh < npunc) {
      SetupFatal("<fastflow> num_horizons is smaller than the number of punctures");
    }
    pin->GetOrAddInteger("fastflow", "npunct", npunc);
    pin->GetOrAddInteger("fastflow", "find_every", 16);
    pin->GetOrAddInteger("fastflow", "ntheta", 16);
    pin->GetOrAddInteger("fastflow", "lmax", 8);
    pin->GetOrAddString("fastflow", "metric_drvts", "interpolant");
    for (int n=0; n<npunc; ++n) {
      const std::string s = "_" + std::to_string(n);
      pin->GetOrAddInteger("fastflow", "use_puncture" + s, n);
      pin->GetOrAddInteger("fastflow", "flow_iterations" + s, 400);
      if (!pin->DoesParameterExist("fastflow", "flow_alpha_beta_const" + s)) {
        SetupSetReal(pin, "fastflow", "flow_alpha_beta_const" + s, mass[n]*mass[n]);
      }
      pin->GetOrAddReal("fastflow", "hmean_tol" + s, 100.0);
      if (!pin->DoesParameterExist("fastflow", "mass_tol" + s)) {
        SetupSetReal(pin, "fastflow", "mass_tol" + s, 1.0e-5*mass[n]);
      }
      pin->GetOrAddReal("fastflow", "start_time" + s, 0.0);
      pin->GetOrAddReal("fastflow", "stop_time" + s, 1.0e30);
    }
  }
  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC: trackers" << (horizons ? ", horizon finders" : "")
              << " and refined regions set for " << npunc << " puncture(s)" << std::endl;
  }
}

} // namespace nrpic_by

#endif // PGEN_NRPIC_NRPIC_PUNCTURE_SETUP_HPP_
