//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_accretion.cpp
//! \brief Accretion diagnostics of the NRPIC module.  All are off by default and none
//! changes the state of a run (the pericentre counter lives in an integer slot of its
//! own).
//!
//!  1. Record of removed particles (<particles> removal_record = true): every particle
//!     that leaves the run is appended to <basename>.removed.bin with its last state,
//!     the metric there and its energy at infinity per unit rest mass,
//!       E = -u_t = alpha W - beta^i u_i,
//!     which a geodesic conserves in a stationary spacetime.  A particle removed by the
//!     lapse or horizon rule was not pushed in its last step: its record belongs to the
//!     start of that step (t^n, x^n), where the rule was tested.
//!  2. Particle flux through coordinate spheres (acc_nsphere, acc_radius1 ..): a
//!     particle whose distance to the centre passes a radius during a step is counted,
//!     with its rest mass and its energy m E after the step, separately inwards and
//!     outwards; the sums since the start of the run are written to <basename>.acc.hst
//!     together with the number and rest mass of the particles inside each sphere.
//!     The centre is fixed (acc_x1 .. acc_x3) or follows a puncture tracker
//!     (acc_tracker = n); the distance is the Euclidean coordinate distance (nearest
//!     image in periodic directions), or the radial coordinate for the analytic metrics
//!     in spherical coordinates.
//!  3. Pericentre counter (peri_count = true): the distance of every particle to the
//!     same centre is followed from step to step; a passage is counted when the
//!     distance, having decreased, increases again (peri_rmax > 0: only when that
//!     happens closer to the centre than peri_rmax).
//!
//! In the Newtonian mode the lapse slot holds the potential Phi and the energy is the
//! Newtonian limit of -u_t, E = 1 + p^2/(2 a^2) + (Phi + Phi_ext)/a, with the momentum
//! as it is at the time of the count (after the first half of the kick).

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "driver/driver.hpp"
#include "z4c/z4c.hpp"
#include "z4c/compact_object_tracker.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_metrics.hpp"
#include "particles/nrpic_mesh.hpp"

namespace particles {

namespace {

// number of doubles of one record of <basename>.removed.bin
constexpr int kRemovedFields = 20;
// number of doubles of the state block of the restart file
constexpr int kAccState = 28;

void AccFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_accretion.cpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

//----------------------------------------------------------------------------------------
//! \fn AccAdm
//! \brief the 3+1 fields at the point x for every metric source of the module.  m is
//! the MeshBlock of the particle (mesh metric), level the time level (0: t^n, 1: t^n+1)

template <class SizeViewT>
KOKKOS_INLINE_FUNCTION
void AccAdm(const NrpicMetric msrc, const nrpic::MeshMetric &proto, const SizeViewT &sz,
            const int m, const int level, const Real bh_mass, const Real bh_spin,
            const Real lat_dx, const Real x[3], nrpic::AdmPoint &ap) {
  if (msrc == NrpicMetric::mesh) {
    nrpic::MeshMetric met = proto;
    met.m = m;
    met.xmin[0] = sz(m).x1min; met.xmin[1] = sz(m).x2min; met.xmin[2] = sz(m).x3min;
    met.idx[0] = 1.0/sz(m).dx1; met.idx[1] = 1.0/sz(m).dx2; met.idx[2] = 1.0/sz(m).dx3;
    met(level, x, ap);
  } else if (msrc == NrpicMetric::kerr_schild) {
    nrpic::KerrSchildCart met{bh_mass, bh_spin};
    met(level, x, ap);
  } else if (msrc == NrpicMetric::kerr_schild_sph) {
    nrpic::KerrSchildSph met{bh_mass, bh_spin};
    met(level, x, ap);
  } else if (msrc == NrpicMetric::boyer_lindquist) {
    nrpic::BoyerLindquist met{bh_mass, bh_spin};
    met(level, x, ap);
  } else {
    nrpic::LatticeMetric<nrpic::KerrSchildCart> met{{bh_mass, bh_spin},
                                                    {0.0, 0.0, 0.0},
                                                    {lat_dx, lat_dx, lat_dx}};
    met(level, x, ap);
  }
}

//----------------------------------------------------------------------------------------
//! \fn AccEnergy
//! \brief E = alpha W - beta^i u_i with W = sqrt(eps + gamma^ij u_i u_j); also returns W

KOKKOS_INLINE_FUNCTION
Real AccEnergy(const nrpic::AdmPoint &ap, const Real u[3], const Real eps, Real &w) {
  Real gi[3][3], uup[3];
  nrpic::Inv3Sym(ap.g, gi);
  w = nrpic::LorentzFactorEps(gi, u, eps, uup);
  return ap.alp*w - (ap.beta[0]*u[0] + ap.beta[1]*u[1] + ap.beta[2]*u[2]);
}

//----------------------------------------------------------------------------------------
//! \fn AccDistance
//! \brief distance of x to the centre c: the radial coordinate itself for the analytic
//! metrics in spherical coordinates, otherwise the Euclidean coordinate distance, to
//! the nearest image in periodic directions

KOKKOS_INLINE_FUNCTION
Real AccDistance(const bool radial, const Real x[3], const Real c[3], const bool per[3],
                 const Real len[3]) {
  if (radial) return x[0];
  Real r2 = 0.0;
  for (int i=0; i<3; ++i) {
    Real d = x[i] - c[i];
    if (per[i]) { d -= len[i]*floor(d/len[i] + 0.5); }
    r2 += d*d;
  }
  return sqrt(r2);
}

} // namespace

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccInit
//! \brief reads the options of the accretion diagnostics.  A parameter that is not in
//! the input is not added to it, so that the parameter dump inside the restart files of
//! existing set-ups does not change.

void Particles::NrpicAccInit(ParameterInput *pin) {
  auto has = [&](const std::string &key) {
    return pin->DoesParameterExist("particles", key);
  };
  if (has("removal_record")) { acc.record = pin->GetBoolean("particles", "removal_record"); }
  if (has("acc_nsphere")) { acc.nsphere = pin->GetInteger("particles", "acc_nsphere"); }
  if (acc.nsphere < 0 || acc.nsphere > 4) {
    AccFatal("<particles> acc_nsphere must be between 0 and 4");
  }
  for (int n=0; n<acc.nsphere; ++n) {
    acc.radius[n] = pin->GetReal("particles", "acc_radius" + std::to_string(n+1));
    if (!(acc.radius[n] > 0.0)) {
      AccFatal("<particles> acc_radius" + std::to_string(n+1) + " must be positive");
    }
  }
  if (has("acc_tracker")) { acc.tracker = pin->GetInteger("particles", "acc_tracker"); }
  if (has("acc_x1")) { acc.center[0] = pin->GetReal("particles", "acc_x1"); }
  if (has("acc_x2")) { acc.center[1] = pin->GetReal("particles", "acc_x2"); }
  if (has("acc_x3")) { acc.center[2] = pin->GetReal("particles", "acc_x3"); }
  if (has("peri_count")) { acc.peri = pin->GetBoolean("particles", "peri_count"); }
  if (has("peri_rmax")) { acc.peri_rmax = pin->GetReal("particles", "peri_rmax"); }
  if (has("acc_dcycle")) { acc.dcycle = pin->GetInteger("particles", "acc_dcycle"); }
  acc.on = (acc.nsphere > 0) || acc.peri;
  if (acc.tracker >= 0) {
    z4c::Z4c *pz4c = pmy_pack->pz4c;
    if (pz4c == nullptr || acc.tracker >= static_cast<int>(pz4c->ptracker.size())) {
      AccFatal("<particles> acc_tracker = " + std::to_string(acc.tracker) +
               " names no puncture tracker of this run (<z4c> co_<n>_...)");
    }
  }
  NrpicAccCentre(acc_c0);
  NrpicAccCentre(acc_c1);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccCentre
//! \brief the centre of the spheres now: the position of the puncture tracker, or the
//! fixed point of the input

void Particles::NrpicAccCentre(Real c[3]) {
  if (acc.tracker >= 0 && pmy_pack->pz4c != nullptr) {
    for (int i=0; i<3; ++i) { c[i] = pmy_pack->pz4c->ptracker[acc.tracker]->GetPos(i); }
  } else {
    for (int i=0; i<3; ++i) { c[i] = acc.center[i]; }
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccSaveCentre
//! \brief before the spacetime update: the centre at t^n

void Particles::NrpicAccSaveCentre() {
  if (!acc.on) return;
  NrpicAccCentre(acc_c0);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccBeforePush
//! \brief keeps the distance of every particle to the centre at t^n

void Particles::NrpicAccBeforePush() {
  if (!acc.on) return;
  const int np = nprtcl_thispack;
  if (np == 0) return;
  if (static_cast<int>(acc_dold.extent(0)) < np) {
    Kokkos::realloc(acc_dold, np);
  }
  auto pr = prtcl_rdata;
  auto dold = acc_dold;
  const bool radial = (nropt.metric == NrpicMetric::kerr_schild_sph ||
                       nropt.metric == NrpicMetric::boyer_lindquist);
  const Real c[3] = {acc_c0[0], acc_c0[1], acc_c0[2]};
  // nearest image only where the particles live on the mesh (the mesh of a run on an
  // analytic metric is a dummy)
  const bool pmesh_ = (nropt.metric == NrpicMetric::mesh);
  const bool per[3] = {pmesh_ && nropt.periodic[0], pmesh_ && nropt.periodic[1],
                       pmesh_ && nropt.periodic[2]};
  const Real len[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  par_for("nrpic_acc_before", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
    const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
    dold(p) = AccDistance(radial, x, c, per, len);
  });
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccAfterPush
//! \brief after the push: counts the particles that crossed each sphere during the
//! step and advances the pericentre counter.  Particles that the push flagged for
//! removal did not move and are not counted here.

void Particles::NrpicAccAfterPush() {
  if (!acc.on) return;
  const int np = nprtcl_thispack;
  if (np == 0) return;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  NrpicAccCentre(acc_c1);
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  auto dold = acc_dold;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int gids = pmy_pack->gids;
  const NrpicMetric msrc = nropt.metric;
  const bool radial = (msrc == NrpicMetric::kerr_schild_sph ||
                       msrc == NrpicMetric::boyer_lindquist);
  const Real c[3] = {acc_c1[0], acc_c1[1], acc_c1[2]};
  // nearest image only where the particles live on the mesh (the mesh of a run on an
  // analytic metric is a dummy)
  const bool pmesh_ = (nropt.metric == NrpicMetric::mesh);
  const bool per[3] = {pmesh_ && nropt.periodic[0], pmesh_ && nropt.periodic[1],
                       pmesh_ && nropt.periodic[2]};
  const Real len[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const Real bh_mass = nropt.mass, bh_spin = nropt.spin, lat_dx = nropt.lattice_dx;
  const bool zm_null = nropt.zero_mass_null && (msrc == NrpicMetric::mesh);
  const bool newton = nropt.newton;
  const Real tnew = pm->time + pm->dt;
  nrpic::NewtonExternal ext;
  Real ia = 1.0;
  if (newton) {
    ext = NrpicNewtonExternal(tnew);
    ia = 1.0/NrpicNewtonScale(tnew);
  }

  nrpic::MeshMetric proto;
  if (msrc == NrpicMetric::mesh) {
    proto.bspline = nropt.interp_bspline;
    proto.m1 = nropt.interp_bspline ? met1s : met1;
    proto.m0 = proto.m1;
    proto.is_static = true;
    proto.ist[0] = indcs.is; proto.ist[1] = indcs.js; proto.ist[2] = indcs.ks;
    proto.ncell[0] = indcs.nx1 + 2*indcs.ng;
    proto.ncell[1] = indcs.nx2 + 2*indcs.ng;
    proto.ncell[2] = indcs.nx3 + 2*indcs.ng;
  }

  for (int n=0; n<acc.nsphere; ++n) {
    const Real rad = acc.radius[n];
    Real nin = 0.0, min = 0.0, ein = 0.0, nout = 0.0, mout = 0.0, eout = 0.0;
    Kokkos::parallel_reduce("nrpic_acc_flux", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, Real &lnin, Real &lmin, Real &lein, Real &lnout,
                  Real &lmout, Real &leout) {
      if (pi(PGID,p) < 0) return;
      const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
      const Real d0 = dold(p);
      const Real d1 = AccDistance(radial, x, c, per, len);
      const bool in = (d0 >= rad && d1 < rad);
      const bool out = (d0 < rad && d1 >= rad);
      if (!in && !out) return;
      const Real u[3] = {pr(IPVX,p), pr(IPVY,p), pr(IPVZ,p)};
      const Real mp = (pr(IPM,p) > 0.0) ? pr(IPM,p) : 0.0;
      nrpic::AdmPoint ap;
      AccAdm(msrc, proto, sz, pi(PGID,p) - gids, 1, bh_mass, bh_spin, lat_dx, x, ap);
      Real e = 0.0;
      if (newton) {
        Real g[3] = {0.0, 0.0, 0.0};
        const Real phi = ap.alp + ext.Add(x, g);
        e = 1.0 + 0.5*(u[0]*u[0] + u[1]*u[1] + u[2]*u[2])*ia*ia + phi*ia;
      } else {
        const Real eps = (pr(IPM,p) > 0.0 || (pr(IPM,p) == 0.0 && !zm_null)) ? 1.0 : 0.0;
        Real w;
        e = AccEnergy(ap, u, eps, w);
      }
      if (in) {
        lnin += 1.0; lmin += mp; lein += mp*e;
      } else {
        lnout += 1.0; lmout += mp; leout += mp*e;
      }
    }, Kokkos::Sum<Real>(nin), Kokkos::Sum<Real>(min), Kokkos::Sum<Real>(ein),
       Kokkos::Sum<Real>(nout), Kokkos::Sum<Real>(mout), Kokkos::Sum<Real>(eout));
    acc_flux[n][0] += nin; acc_flux[n][1] += min; acc_flux[n][2] += ein;
    acc_flux[n][3] += nout; acc_flux[n][4] += mout; acc_flux[n][5] += eout;
  }

  if (acc.peri) {
    const Real rmax = acc.peri_rmax;
    par_for("nrpic_acc_peri", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
      if (pi(PGID,p) < 0) return;
      const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
      const Real d0 = dold(p);
      const Real d1 = AccDistance(radial, x, c, per, len);
      int st = pi(PPERI,p);
      if (d1 < d0) {
        st |= 1;                          // approaching
      } else if (d1 > d0) {
        if ((st & 1) && (rmax <= 0.0 || d0 < rmax)) { st += 2; }   // passage at d0
        st &= ~1;                         // receding
      }
      pi(PPERI,p) = st;
    });
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccRecordRemoved
//! \brief appends the particles flagged for removal to <basename>.removed.bin, records
//! of 20 doubles after a header of 8 bytes "NRPREM01" and one int64 (20):
//!   0 time, 1 tag, 2 species, 3 reason (1 left the mesh, 2 lapse below alpha_exc,
//!   3 inside a horizon, 4 state not finite), 4-6 x^i, 7-9 u_i, 10 rest mass,
//!   11 proper time, 12 alpha, 13-15 beta^i, 16 W, 17 E = alpha W - beta^i u_i,
//!   18 distance to the centre of the accretion diagnostics, 19 pericentre passages.
//! Reasons 2 to 4: state and metric at the start of the step in which the particle was
//! removed (it was not pushed).  Reason 1: state after the push, outside the mesh, no
//! metric (fields 12 to 17 are zero).  Called by NrpicRemoveFlagged before the arrays
//! are compacted; after_push tells whether a push preceded (false at start-up and
//! after a change of the mesh).

void Particles::NrpicAccRecordRemoved(const bool after_push) {
  if (!acc.record) return;
  const int np = nprtcl_thispack;
  if (np == 0) return;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  int nf = 0;
  Kokkos::parallel_reduce("nrpic_acc_nflag", Kokkos::RangePolicy<DevExeSpace>(0, np),
  KOKKOS_LAMBDA(const int p, int &ln) {
    if (pi(PGID,p) < 0) { ln += 1; }
  }, Kokkos::Sum<int>(nf));
  if (nf == 0) return;

  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int nmb = pmy_pack->nmb_thispack;
  const NrpicMetric msrc = nropt.metric;
  const bool radial = (msrc == NrpicMetric::kerr_schild_sph ||
                       msrc == NrpicMetric::boyer_lindquist);
  // a removed particle carries the state of t^n; the centre of that time
  Real cc[3];
  if (after_push && acc.on) {
    cc[0] = acc_c0[0]; cc[1] = acc_c0[1]; cc[2] = acc_c0[2];
  } else {
    NrpicAccCentre(cc);
  }
  const Real c[3] = {cc[0], cc[1], cc[2]};
  // nearest image only where the particles live on the mesh (the mesh of a run on an
  // analytic metric is a dummy)
  const bool pmesh_ = (nropt.metric == NrpicMetric::mesh);
  const bool per[3] = {pmesh_ && nropt.periodic[0], pmesh_ && nropt.periodic[1],
                       pmesh_ && nropt.periodic[2]};
  const Real len[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const Real bh_mass = nropt.mass, bh_spin = nropt.spin, lat_dx = nropt.lattice_dx;
  const bool zm_null = nropt.zero_mass_null && (msrc == NrpicMetric::mesh);
  const bool newton = nropt.newton;
  const Real t_old = pm->time;
  const Real t_new = after_push ? pm->time + pm->dt : pm->time;
  nrpic::NewtonExternal ext;
  Real ia = 1.0;
  if (newton) {
    ext = NrpicNewtonExternal(t_old);
    ia = 1.0/NrpicNewtonScale(t_old);
  }

  nrpic::MeshMetric proto;
  const bool mesh_metric = (msrc == NrpicMetric::mesh);
  if (mesh_metric) {
    // level 0 is t^n after a push of an evolving spacetime, the only level otherwise
    const bool two = after_push && !metric_is_static;
    proto.bspline = nropt.interp_bspline;
    if (nropt.interp_bspline) {
      proto.m1 = met1s;
      proto.m0 = two ? met0s : met1s;
    } else {
      proto.m1 = met1;
      proto.m0 = two ? met0 : met1;
    }
    proto.is_static = !two;
    proto.ist[0] = indcs.is; proto.ist[1] = indcs.js; proto.ist[2] = indcs.ks;
    proto.ncell[0] = indcs.nx1 + 2*indcs.ng;
    proto.ncell[1] = indcs.nx2 + 2*indcs.ng;
    proto.ncell[2] = indcs.nx3 + 2*indcs.ng;
  }

  DvceArray2D<Real> rec("nrpic_removed", kRemovedFields, nf);
  int ntot = 0;
  Kokkos::parallel_scan("nrpic_acc_record", Kokkos::RangePolicy<DevExeSpace>(0, np),
  KOKKOS_LAMBDA(const int p, int &upd, const bool final) {
    if (pi(PGID,p) >= 0) return;
    if (final) {
      const int code = pi(PGID,p);
      const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
      const Real u[3] = {pr(IPVX,p), pr(IPVY,p), pr(IPVZ,p)};
      const int q = upd;
      rec(0,q) = (code == -1) ? t_new : t_old;
      rec(1,q) = static_cast<Real>(pi(PTAG,p));
      rec(2,q) = static_cast<Real>(pi(PSP,p));
      rec(3,q) = static_cast<Real>(-code);
      rec(4,q) = x[0]; rec(5,q) = x[1]; rec(6,q) = x[2];
      rec(7,q) = u[0]; rec(8,q) = u[1]; rec(9,q) = u[2];
      rec(10,q) = pr(IPM,p);
      rec(11,q) = pr(IPTAU,p);
      for (int n=12; n<18; ++n) { rec(n,q) = 0.0; }
      rec(18,q) = AccDistance(radial, x, c, per, len);
      rec(19,q) = static_cast<Real>(pi(PPERI,p) >> 1);
      // metric at the particle: not for one that left the mesh
      int m = 0;
      bool have = (code < -1);
      if (have && mesh_metric) {
        m = nrpic::FindBlock(sz, nmb, 0, x[0], x[1], x[2]);
        have = (m >= 0);
      }
      if (have) {
        nrpic::AdmPoint ap;
        AccAdm(msrc, proto, sz, m, 0, bh_mass, bh_spin, lat_dx, x, ap);
        rec(12,q) = ap.alp;
        rec(13,q) = ap.beta[0]; rec(14,q) = ap.beta[1]; rec(15,q) = ap.beta[2];
        if (newton) {
          Real g[3] = {0.0, 0.0, 0.0};
          const Real phi = ap.alp + ext.Add(x, g);
          rec(16,q) = 1.0;
          rec(17,q) = 1.0 + 0.5*(u[0]*u[0] + u[1]*u[1] + u[2]*u[2])*ia*ia + phi*ia;
        } else {
          const Real eps = (pr(IPM,p) > 0.0 || (pr(IPM,p) == 0.0 && !zm_null)) ? 1.0
                                                                              : 0.0;
          Real w;
          rec(17,q) = AccEnergy(ap, u, eps, w);
          rec(16,q) = w;
        }
      }
    }
    upd += 1;
  }, ntot);

  auto rh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), rec);
  std::vector<double> buf(static_cast<size_t>(kRemovedFields)*nf);
  for (int q=0; q<nf; ++q) {
    for (int n=0; n<kRemovedFields; ++n) { buf[kRemovedFields*q + n] = rh(n,q); }
    // energy carried away by the excised matter (finite records only)
    if (rh(3,q) > 1.5 && rh(10,q) > 0.0 && std::isfinite(rh(17,q))) {
      acc_e_excised += rh(10,q)*rh(17,q);
    }
  }
  const std::string fname = nr_basename + ".removed.bin";
  // the header is written when the file does not exist yet (a new run creates it at
  // start-up; a continued run appends)
  bool exists = false;
  if (std::FILE *ft = std::fopen(fname.c_str(), "rb")) {
    exists = true;
    std::fclose(ft);
  }
  std::FILE *fp = std::fopen(fname.c_str(), "ab");
  if (fp == nullptr) AccFatal("cannot open " + fname);
  if (!exists) {
    const char magic[9] = "NRPREM01";
    const std::int64_t nfld = kRemovedFields;
    std::fwrite(magic, 1, 8, fp);
    std::fwrite(&nfld, sizeof(std::int64_t), 1, fp);
  }
  std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccStartRecord
//! \brief a new run starts its record of removed particles with the header alone

void Particles::NrpicAccStartRecord() {
  if (!acc.record) return;
  const std::string fname = nr_basename + ".removed.bin";
  std::FILE *fp = std::fopen(fname.c_str(), "wb");
  if (fp == nullptr) AccFatal("cannot open " + fname);
  const char magic[9] = "NRPREM01";
  const std::int64_t nfld = kRemovedFields;
  std::fwrite(magic, 1, 8, fp);
  std::fwrite(&nfld, sizeof(std::int64_t), 1, fp);
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccWriteHistory
//! \brief appends one record to <basename>.acc.hst (text): the centre, the removed
//! particles, the particles that have passed a pericentre, and per sphere the content
//! and the cumulative counts of the crossings

void Particles::NrpicAccWriteHistory(Real time, int ncycle, bool header) {
  if (!acc.on && !acc.record) return;
  const int np = nprtcl_thispack;
  const std::string fname = nr_basename + ".acc.hst";
  std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
  if (fp == nullptr) AccFatal("cannot open " + fname);
  if (header) {
    std::fprintf(fp, "# NRPIC accretion diagnostics\n");
    std::fprintf(fp, "# [1]=time [2]=ncycle [3]=centre_x [4]=centre_y [5]=centre_z "
                 "[6]=n_excised [7]=m_excised [8]=mE_excised [9]=n_escaped "
                 "[10]=m_escaped [11]=n_peri_ge1 [12]=m_peri_ge1 [13]=n_peri_ge2 "
                 "[14]=m_peri_ge2");
    for (int n=0; n<acc.nsphere; ++n) {
      const int c0 = 15 + 9*n;
      std::fprintf(fp, " [%d]=radius%d [%d]=n_inside%d [%d]=m_inside%d [%d]=n_in%d "
                   "[%d]=m_in%d [%d]=mE_in%d [%d]=n_out%d [%d]=m_out%d [%d]=mE_out%d",
                   c0, n+1, c0+1, n+1, c0+2, n+1, c0+3, n+1, c0+4, n+1, c0+5, n+1,
                   c0+6, n+1, c0+7, n+1, c0+8, n+1);
    }
    std::fprintf(fp, "\n");
  }
  Real cc[3];
  NrpicAccCentre(cc);
  const Real c[3] = {cc[0], cc[1], cc[2]};
  const bool radial = (nropt.metric == NrpicMetric::kerr_schild_sph ||
                       nropt.metric == NrpicMetric::boyer_lindquist);
  // nearest image only where the particles live on the mesh (the mesh of a run on an
  // analytic metric is a dummy)
  const bool pmesh_ = (nropt.metric == NrpicMetric::mesh);
  const bool per[3] = {pmesh_ && nropt.periodic[0], pmesh_ && nropt.periodic[1],
                       pmesh_ && nropt.periodic[2]};
  const Real len[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  Real n1 = 0.0, m1 = 0.0, n2 = 0.0, m2 = 0.0;
  if (np > 0 && acc.peri) {
    Kokkos::parallel_reduce("nrpic_acc_perisum", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, Real &ln1, Real &lm1, Real &ln2, Real &lm2) {
      const int cnt = pi(PPERI,p) >> 1;
      const Real mp = (pr(IPM,p) > 0.0) ? pr(IPM,p) : 0.0;
      if (cnt >= 1) { ln1 += 1.0; lm1 += mp; }
      if (cnt >= 2) { ln2 += 1.0; lm2 += mp; }
    }, Kokkos::Sum<Real>(n1), Kokkos::Sum<Real>(m1), Kokkos::Sum<Real>(n2),
       Kokkos::Sum<Real>(m2));
  }
  std::fprintf(fp, "%.15e %d %.15e %.15e %.15e %d %.15e %.15e %d %.15e %.0f %.15e %.0f "
               "%.15e", time, ncycle, c[0], c[1], c[2], n_excised, mass_excised,
               acc_e_excised, n_escaped, mass_escaped, n1, m1, n2, m2);
  for (int n=0; n<acc.nsphere; ++n) {
    const Real rad = acc.radius[n];
    Real ni = 0.0, mi = 0.0;
    if (np > 0) {
      Kokkos::parallel_reduce("nrpic_acc_inside", Kokkos::RangePolicy<DevExeSpace>(0, np),
      KOKKOS_LAMBDA(const int p, Real &lni, Real &lmi) {
        const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
        if (AccDistance(radial, x, c, per, len) < rad) {
          lni += 1.0;
          lmi += (pr(IPM,p) > 0.0) ? pr(IPM,p) : 0.0;
        }
      }, Kokkos::Sum<Real>(ni), Kokkos::Sum<Real>(mi));
    }
    std::fprintf(fp, " %.15e %.0f %.15e %.0f %.15e %.15e %.0f %.15e %.15e", rad, ni, mi,
                 acc_flux[n][0], acc_flux[n][1], acc_flux[n][2], acc_flux[n][3],
                 acc_flux[n][4], acc_flux[n][5]);
  }
  std::fprintf(fp, "\n");
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccWriteRestart
//! \brief the state of the accretion diagnostics, appended to the particle restart
//! file only when a diagnostic is on (files of other runs keep their format):
//!   8 bytes "NRPACC01", 28 doubles (4 x 6 flux sums, sum of m E of the excised
//!   particles, centre at t^n), int64 N, N int32 (state of the pericentre counter)

void Particles::NrpicAccWriteRestart(std::FILE *fp) {
  if (!acc.on && !acc.record) return;
  const int np = nprtcl_thispack;
  const char magic[9] = "NRPACC01";
  double s[kAccState];
  for (int n=0; n<4; ++n) {
    for (int k=0; k<6; ++k) { s[6*n + k] = acc_flux[n][k]; }
  }
  s[24] = acc_e_excised;
  s[25] = acc_c0[0]; s[26] = acc_c0[1]; s[27] = acc_c0[2];
  std::int64_t n64 = np;
  std::fwrite(magic, 1, 8, fp);
  std::fwrite(s, sizeof(double), kAccState, fp);
  std::fwrite(&n64, sizeof(std::int64_t), 1, fp);
  if (np > 0) {
    auto ih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_idata);
    std::vector<std::int32_t> st(np);
    for (int p=0; p<np; ++p) { st[p] = ih(PPERI,p); }
    std::fwrite(st.data(), sizeof(std::int32_t), st.size(), fp);
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccReadRestart
//! \brief reads the block written by NrpicAccWriteRestart if the file has one (fp
//! stands behind the particle data); fills the counter slot of the host array ih

void Particles::NrpicAccReadRestart(std::FILE *fp, const int np, HostArray2D<int> &ih) {
  char magic[9] = {0};
  if (std::fread(magic, 1, 8, fp) != 8 || std::strncmp(magic, "NRPACC01", 8) != 0) {
    return;      // a dump without the diagnostics: counters start at zero
  }
  double s[kAccState];
  std::int64_t n64 = 0;
  if (std::fread(s, sizeof(double), kAccState, fp) != kAccState ||
      std::fread(&n64, sizeof(std::int64_t), 1, fp) != 1 || n64 != np) {
    AccFatal("the accretion block of the particle restart file is truncated");
  }
  std::vector<std::int32_t> st(np);
  if (np > 0 && std::fread(st.data(), sizeof(std::int32_t), st.size(), fp) != st.size()) {
    AccFatal("the accretion block of the particle restart file is truncated");
  }
  for (int n=0; n<4; ++n) {
    for (int k=0; k<6; ++k) { acc_flux[n][k] = s[6*n + k]; }
  }
  acc_e_excised = s[24];
  acc_c0[0] = s[25]; acc_c0[1] = s[26]; acc_c0[2] = s[27];
  for (int p=0; p<np; ++p) { ih(PPERI,p) = st[p]; }
  acc_restart_read = true;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicAccWriteSnapshot
//! \brief with the pericentre counter on, a particle snapshot ends with N int32: the
//! number of pericentre passages of each particle

void Particles::NrpicAccWriteSnapshot(std::FILE *fp) {
  if (!acc.peri) return;
  const int np = nprtcl_thispack;
  if (np == 0) return;
  auto ih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_idata);
  std::vector<std::int32_t> cnt(np);
  for (int p=0; p<np; ++p) { cnt[p] = ih(PPERI,p) >> 1; }
  std::fwrite(cnt.data(), sizeof(std::int32_t), cnt.size(), fp);
}

} // namespace particles
