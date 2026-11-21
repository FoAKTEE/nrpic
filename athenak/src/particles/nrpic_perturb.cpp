//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_perturb.cpp
//! \brief Dynamically accessible perturbation of a particle equilibrium: during an
//! initial interval every particle with rest mass feels the extra radial force
//!   du_i/dt = gamma (x^i - c^i)/|x - c|        (outwards for gamma > 0),
//! the perturbation of the characteristic system used for steady states of the
//! Einstein-Vlasov system in arXiv:2009.08163 (Guenther, Koerner, Lebeda, Poetzl, Rein,
//! Straub, Weber; paper.tex line 848, equation "perturb": the term gamma x/r added to
//! the momentum equation during [0, T_pert]; their momentum variable is not the
//! canonical one).  In the canonical variables (x^i, u_i) of the pushers the force
//! does not depend on the momentum; it is the flow of the Hamiltonian -gamma |x - c|
//! added to the geodesic one.  The flow of a Hamiltonian conserves the phase-space
//! density along the trajectories, hence all Casimir functionals of the distribution;
//! no new initial-data solve is needed, the spacetime follows through its evolution.
//!
//! The force is applied by splitting: half of the impulse of a step before the push and
//! half after it, u_i += gamma (x^i - c^i)/|x - c| w, where w is the length of the part
//! of the half step that lies inside [perturb_tstart, perturb_tstart + perturb_time].
//! Each kick is the exact flow of the added Hamiltonian, so the splitting is second
//! order in the step and symplectic, and the impulse summed over a run is gamma
//! perturb_time whatever the step size.
//!
//! Options in <particles> (absent or perturb_gamma = 0: no effect at all):
//!   perturb_gamma  = g      strength of the force per unit rest mass
//!   perturb_time   = T      duration T_pert of the force (required with perturb_gamma)
//!   perturb_tstart = 0      time at which it starts
//!   perturb_x1, perturb_x2, perturb_x3 = 0   centre c of the radial direction
//! Not available with pusher = newton.  Null particles and light rays are not kicked.

#include <iostream>
#include <string>

#include "athena.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "particles/particles.hpp"

namespace particles {

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicPerturbInit
//! \brief reads the options of the perturbing force; nothing is added to the input
//! parameters unless <particles> perturb_gamma is present

void Particles::NrpicPerturbInit(ParameterInput *pin) {
  pert.on = false;
  if (!pin->DoesParameterExist("particles", "perturb_gamma")) return;
  pert.gamma = pin->GetReal("particles", "perturb_gamma");
  if (pert.gamma == 0.0) return;
  if (nropt.newton) {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "<particles> perturb_gamma is not available with pusher = newton"
              << std::endl;
    std::exit(EXIT_FAILURE);
  }
  pert.duration = pin->GetReal("particles", "perturb_time");
  pert.tstart = pin->GetOrAddReal("particles", "perturb_tstart", 0.0);
  pert.centre[0] = pin->GetOrAddReal("particles", "perturb_x1", 0.0);
  pert.centre[1] = pin->GetOrAddReal("particles", "perturb_x2", 0.0);
  pert.centre[2] = pin->GetOrAddReal("particles", "perturb_x3", 0.0);
  if (!(pert.duration > 0.0)) {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "<particles> perturb_time must be positive" << std::endl;
    std::exit(EXIT_FAILURE);
  }
  pert.on = true;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicPerturbKick
//! \brief impulse of the perturbing force over the interval [t0, t1] at the present
//! positions (called by NrpicPush with the first and with the second half of a step)

void Particles::NrpicPerturbKick(const Real t0, const Real t1) {
  const Real lo = (t0 > pert.tstart) ? t0 : pert.tstart;
  const Real end = pert.tstart + pert.duration;
  const Real hi = (t1 < end) ? t1 : end;
  if (!(hi > lo)) return;
  const int np = nprtcl_thispack;
  if (np == 0) return;
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  const Real imp = pert.gamma*(hi - lo);
  const Real c[3] = {pert.centre[0], pert.centre[1], pert.centre[2]};
  par_for("nrpic_perturb", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
    if (pi(PGID,p) < 0) return;            // flagged for removal
    if (!(pr(IPM,p) > 0.0)) return;        // null particles and light rays
    const Real d[3] = {pr(IPX,p) - c[0], pr(IPY,p) - c[1], pr(IPZ,p) - c[2]};
    const Real r = sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2]);
    if (!(r > 0.0)) return;                // no direction at the centre
    const Real s = imp/r;
    pr(IPVX,p) += s*d[0];
    pr(IPVY,p) += s*d[1];
    pr(IPVZ,p) += s*d[2];
  });
}

} // namespace particles
