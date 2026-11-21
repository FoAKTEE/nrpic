#ifndef PARTICLES_NRPIC_EXTERNAL_HPP_
#define PARTICLES_NRPIC_EXTERNAL_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_external.hpp
//! \brief external gravity of the Newtonian mode of the NRPIC module, evaluated at the
//! particles and added to the gradient of the mesh potential:
//!  - a fixed point mass M at x_c with the potential -G M/(|x - x_c|^2 + s^2)^(1/2) in
//!    the variables of the mode (Phi of nrpic_newton.cpp: the Newtonian potential is
//!    Phi/a, x is comoving).  The mass is not deposited: it is neither smeared over a
//!    cloud nor moved by the particles.  In a periodic direction the nearest image of
//!    the mass acts (no sum over images and no neutralising background: the mass is an
//!    isolated seed, and the force changes sign across the faces half a box away);
//!  - the acceleration -k x of a homogeneous background, k = (4 pi/3) G rho_b(t) with
//!    rho_b = 1/(6 pi G t^2), i.e. k = 2/(9 t^2) (matter era, physical coordinates,
//!    no expansion of the mesh), potential k x^2/2.

#include "athena.hpp"

namespace nrpic {

struct NewtonExternal {
  Real gm = 0.0;                    // G M of the point mass (0: none)
  Real xc[3] = {0.0, 0.0, 0.0};     // its position
  Real soft2 = 0.0;                 // square of the softening length at this time
  Real kbg = 0.0;                   // background: g = -kbg x
  bool per[3] = {false, false, false};
  Real len[3] = {0.0, 0.0, 0.0};    // box lengths (periodic directions)

  KOKKOS_INLINE_FUNCTION
  bool On() const { return (gm != 0.0) || (kbg != 0.0); }

  //! adds the external acceleration at x to g; returns the external potential at x
  KOKKOS_INLINE_FUNCTION
  Real Add(const Real x[3], Real g[3]) const {
    Real phi = 0.0;
    if (gm != 0.0) {
      Real d[3];
      Real r2 = soft2;
      for (int i=0; i<3; ++i) {
        d[i] = x[i] - xc[i];
        if (per[i]) { d[i] -= len[i]*floor(d[i]/len[i] + 0.5); }
        r2 += d[i]*d[i];
      }
      const Real ir = 1.0/sqrt(r2);
      const Real f = gm*ir*ir*ir;
      g[0] -= f*d[0]; g[1] -= f*d[1]; g[2] -= f*d[2];
      phi -= gm*ir;
    }
    if (kbg != 0.0) {
      g[0] -= kbg*x[0]; g[1] -= kbg*x[1]; g[2] -= kbg*x[2];
      phi += 0.5*kbg*(x[0]*x[0] + x[1]*x[1] + x[2]*x[2]);
    }
    return phi;
  }
};

} // namespace nrpic
#endif // PARTICLES_NRPIC_EXTERNAL_HPP_
