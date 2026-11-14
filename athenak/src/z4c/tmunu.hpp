#ifndef Z4C_TMUNU_HPP_
#define Z4C_TMUNU_HPP_

//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file tmunu.hpp
//! \brief definitions for Tmunu class, which represents the stress-energy tensor
//!  decomposed into E, S_i, and S_{ij}, all undensitized.

#include "athena.hpp"
#include "athena_tensor.hpp"
#include "mesh/mesh.hpp"
#include "eos/primitive-solver/ps_types.hpp"

// forward declarations
class MeshBlockPack;

//! \class Tmunu
class Tmunu {
 public:
  Tmunu(MeshBlockPack *ppack, ParameterInput *pin);
  ~Tmunu();

  // Indices of Tmunu variables
  enum {
    I_Tmunu_Sxx, I_Tmunu_Sxy, I_Tmunu_Sxz, I_Tmunu_Syy, I_Tmunu_Syz, I_Tmunu_Szz,
    I_Tmunu_E, I_Tmunu_Sx, I_Tmunu_Sy, I_Tmunu_Sz,
    N_Tmunu
  };
  // Names of Tmunu variables
  static char const * const Tmunu_names[N_Tmunu];

  // Number of spatial dimensions (3+1 gravity)
  int const NDIM = 3;

  struct Tmunu_vars {
    AthenaTensor<Real, TensorSymm::NONE, 3, 0> E;      // energy density
    AthenaTensor<Real, TensorSymm::NONE, 3, 1> S_d;    // momentum density
    AthenaTensor<Real, TensorSymm::SYM2, 3, 2> S_dd;   // stress tensor
  };

  Tmunu_vars tmunu;

  DvceArray5D<Real> u_tmunu;                          // Tmunu

  // Sources of the next spacetime step as densities (the sources times sqrt(gamma)),
  // provided by a matter module whose sources depend on the metric mainly through the
  // volume element (particles).  With step_density set, the spacetime solver reads
  // them and multiplies by 1/sqrt(gamma) of the current stage, and adds the vacuum
  // energy lambda8pi = Lambda/(8 pi) itself.  u_tmunu keeps the sources at the time
  // of the deposit for the constraints and the diagnostics.
  Tmunu_vars tmunu_step;
  DvceArray5D<Real> u_tmunu_step;
  bool step_density = false;
  Real lambda8pi = 0.0;
  void AllocateStepSources();

 private:
  MeshBlockPack* pmy_pack;
};

#endif  // Z4C_TMUNU_HPP_
