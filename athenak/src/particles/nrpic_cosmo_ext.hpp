#ifndef PARTICLES_NRPIC_COSMO_EXT_HPP_
#define PARTICLES_NRPIC_COSMO_EXT_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_cosmo_ext.hpp
//! \brief Refined meshes in periodic cosmological runs of the NRPIC module:
//!   - the refinement function of the problem generator nrpic_cosmo and its criteria
//!     (particles/nrpic_refine.cpp, input block <nrpic_amr>),
//!   - the guard that stops a run whose fields are no longer finite
//!     (particles/nrpic_guard.cpp, input block <nrpic_guard>),
//!   - helpers for periodic meshes shared by the horizon finder, the compact-object
//!     tracker and the diagnostics (mapping into the box, minimum image).
//! Everything here is read from the input only if the option is present, so that the
//! parameter dump of an existing input does not change.

#include <cmath>

#include "athena.hpp"

class Mesh;
class MeshBlockPack;
class ParameterInput;

namespace nrpic {

//----------------------------------------------------------------------------------------
//! \fn PeriodicMap
//! \brief the coordinate x mapped into [xmin, xmin + len); the same arithmetic as
//! nrpic::WrapCoord, repeated here so that the spacetime solver does not include the
//! headers of the particle module.  A coordinate inside the interval is returned
//! unchanged, bit for bit.

KOKKOS_INLINE_FUNCTION
Real PeriodicMap(const Real x, const Real xmin, const Real len) {
  Real y = x;
  if (y < xmin) {
    y += len*ceil((xmin - y)/len);
  } else if (y >= xmin + len) {
    y -= len*floor((y - xmin)/len);
  }
  if (y >= xmin + len) { y = xmin; }      // rounding at the upper edge
  return y;
}

//----------------------------------------------------------------------------------------
//! \fn MinImage
//! \brief the separation d reduced to the nearest periodic image, in [-len/2, len/2]

KOKKOS_INLINE_FUNCTION
Real MinImage(const Real d, const Real len) {
  return d - len*floor(d/len + 0.5);
}

//----------------------------------------------------------------------------------------
//! \fn ShapeCdf
//! \brief cumulative distribution of the shape of a particle cloud at the distance t
//! (in cells of the cloud) from its centre.  The cloud of the deposit of degree p (1 cloud
//! in cell, 2 triangular shaped cloud, 3 piecewise cubic) is a B-spline of degree p - 1:
//! a top hat one cell wide, a triangle two cells wide, a quadratic spline three cells
//! wide.  The weight of the cloud in an interval is the difference of this function at
//! its ends; over a cell of the cloud's own lattice that gives the usual weights.

KOKKOS_INLINE_FUNCTION
Real ShapeCdf(const int degree, const Real t) {
  if (degree == 1) {
    return (t <= -0.5) ? 0.0 : ((t >= 0.5) ? 1.0 : t + 0.5);
  } else if (degree == 2) {
    if (t <= -1.0) return 0.0;
    if (t >= 1.0) return 1.0;
    return (t <= 0.0) ? 0.5*(1.0 + t)*(1.0 + t) : 1.0 - 0.5*(1.0 - t)*(1.0 - t);
  } else {
    if (t <= -1.5) return 0.0;
    if (t >= 1.5) return 1.0;
    if (t <= -0.5) { return (t + 1.5)*(t + 1.5)*(t + 1.5)/6.0; }
    if (t >= 0.5) { return 1.0 - (1.5 - t)*(1.5 - t)*(1.5 - t)/6.0; }
    return 1.0/6.0 + 0.75*(t + 0.5) - (t*t*t + 0.125)/3.0;
  }
}

// ---- refinement of periodic cosmological runs (nrpic_refine.cpp) ----
//! reads <nrpic_amr>; called by the problem generator, also on restart
void CosmoRefineInit(ParameterInput *pin, Mesh *pm);
//! the refinement function enrolled by nrpic_cosmo: the criteria of <z4c_amr>, then
//! those of <nrpic_amr>
void CosmoRefine(MeshBlockPack *pmbp);

// ---- guard against non-finite fields (nrpic_guard.cpp) ----
//! reads <nrpic_guard>; called once by the driver
void GuardInit(ParameterInput *pin, Mesh *pm);
//! true if the run must stop: the diagnostic has then been printed and written
bool GuardCheck(Mesh *pm);
//! exit status of the executable: 0, or kGuardStatus after a stop by the guard
int GuardExitStatus();
constexpr int kGuardStatus = 3;

} // namespace nrpic
#endif // PARTICLES_NRPIC_COSMO_EXT_HPP_
