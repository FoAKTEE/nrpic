#ifndef SCALAR_FIELD_SCALAR_FIELD_HPP_
#define SCALAR_FIELD_SCALAR_FIELD_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file scalar_field.hpp
//! \brief A minimally coupled real scalar field phi with potential V(phi), evolved with
//! the Z4c spacetime (same time integrator, same finite-difference order, same
//! dissipation, same boundary and refinement machinery) and sourcing it through Tmunu.
//!
//! Conventions (G = c = 1, signature -+++, n^mu = (1, -beta^i)/alpha the unit normal of
//! the slices, K = -nabla_mu n^mu as in Z4c, so K = -3H in an expanding universe):
//!   T_munu = d_mu phi d_nu phi - g_munu [ (1/2) g^rs d_r phi d_s phi + V(phi) ]
//!   Pi     = n^mu d_mu phi = (d_t phi - beta^i d_i phi)/alpha      (evolved with phi)
//!   d_t phi = beta^i d_i phi + alpha Pi
//!   d_t Pi  = beta^i d_i Pi + alpha (D^i D_i phi + K Pi - dV/dphi)
//!             + gamma^ij d_i alpha d_j phi
//!   E    = Pi^2/2 + (1/2) gamma^ij d_i phi d_j phi + V        (energy density)
//!   S_i  = -Pi d_i phi                                         (momentum density)
//!   S_ij = d_i phi d_j phi + gamma_ij (Pi^2/2 - (1/2) gamma^kl d_k phi d_l phi - V)
//! The momentum conjugate to phi in the ADM sense is sqrt(gamma) Pi.
//!
//! Stochastic sources (scalar_field_noise.cpp): fields built from the Fourier modes of a
//! ball of wave vectors of a periodic cubic box, with amplitudes keyed by the wave
//! vector (utils/rng.hpp), added to the right-hand sides of phi and Pi (generic model)
//! or of Pi, Khat and At_ij (the sources of arXiv:2512.14649 as specified by Track E).
//! Off by default.

#include <cstdint>
#include <string>
#include <vector>

#include "athena.hpp"
#include "athena_tensor.hpp"
#include "parameter_input.hpp"
#include "tasklist/task_list.hpp"
#include "bvals/bvals.hpp"

// forward declarations
class Driver;
class MeshBlockPack;

namespace scalarfield {

//----------------------------------------------------------------------------------------
// Potential.  The parameters are plain data so that they can be captured by a kernel;
// the table (kind = kPotTable) is passed next to them as a view of the calling space.

enum SfPotentialKind {kPotQuadratic = 0, kPotQuartic = 1, kPotPlateau = 2,
                      kPotInflection = 3, kPotTable = 4};

struct SfPotential {
  int kind = kPotQuadratic;
  Real m2 = 0.0;        // quadratic, quartic: V = m2 phi^2/2 + lambda phi^4/4
  Real lambda = 0.0;    // inflection: V = lambda v^4 phi^2 P/(3 Q^2),
  Real v0 = 0.0;        //   P = 3 phi^2 + 2 sqrt(2) phi v + 6 v^2, Q = 3 phi^2 + 2 v^2
  Real mu = 1.0;        // plateau: V = v0 (1 - exp(-phi/mu))^2
  Real vev = 1.0;       // v of the inflection form
  Real offset = 0.0;    // constant added to V (all kinds): a cosmological constant
  int ntab = 0;         // table: points, first abscissa, spacing
  Real tab_min = 0.0, tab_dphi = 1.0;
};

//! V and dV/dphi.  tab(0,n) = V, tab(1,n) = dV/dphi at phi = tab_min + n tab_dphi;
//! between the points the cubic Hermite polynomial, beyond them the tangent at the end
//! point.
template <typename TableType>
KOKKOS_INLINE_FUNCTION
void SfPotentialEval(const SfPotential &p, const TableType &tab, const Real phi,
                     Real &v, Real &dv) {
  if (p.kind == kPotQuadratic) {
    v = 0.5*p.m2*phi*phi;
    dv = p.m2*phi;
  } else if (p.kind == kPotQuartic) {
    const Real phi2 = phi*phi;
    v = 0.5*p.m2*phi2 + 0.25*p.lambda*phi2*phi2;
    dv = p.m2*phi + p.lambda*phi2*phi;
  } else if (p.kind == kPotPlateau) {
    const Real e = exp(-phi/p.mu);
    v = p.v0*(1.0 - e)*(1.0 - e);
    dv = 2.0*p.v0*(1.0 - e)*e/p.mu;
  } else if (p.kind == kPotInflection) {
    const Real s2 = 1.4142135623730951;
    const Real vv = p.vev, phi2 = phi*phi;
    const Real pp = 3.0*phi2 + 2.0*s2*phi*vv + 6.0*vv*vv;
    const Real qq = 3.0*phi2 + 2.0*vv*vv;
    const Real dpp = 6.0*phi + 2.0*s2*vv;
    const Real dqq = 6.0*phi;
    const Real c = p.lambda*vv*vv*vv*vv/3.0;
    v = c*phi2*pp/(qq*qq);
    dv = c*((2.0*phi*pp + phi2*dpp)/(qq*qq) - 2.0*phi2*pp*dqq/(qq*qq*qq));
  } else {
    const Real s = (phi - p.tab_min)/p.tab_dphi;
    const Real smax = static_cast<Real>(p.ntab - 1);
    if (s <= 0.0) {
      dv = tab(1,0);
      v = tab(0,0) + dv*(phi - p.tab_min);
    } else if (s >= smax) {
      dv = tab(1,p.ntab-1);
      v = tab(0,p.ntab-1) + dv*(phi - (p.tab_min + smax*p.tab_dphi));
    } else {
      int n = static_cast<int>(s);
      if (n > p.ntab - 2) { n = p.ntab - 2; }
      const Real t = s - static_cast<Real>(n);
      const Real h = p.tab_dphi;
      const Real f0 = tab(0,n), f1 = tab(0,n+1), d0 = h*tab(1,n), d1 = h*tab(1,n+1);
      // cubic Hermite polynomial and its derivative
      const Real t2 = t*t, t3 = t2*t;
      v = (2.0*t3 - 3.0*t2 + 1.0)*f0 + (t3 - 2.0*t2 + t)*d0
        + (-2.0*t3 + 3.0*t2)*f1 + (t3 - t2)*d1;
      dv = ((6.0*t2 - 6.0*t)*f0 + (3.0*t2 - 4.0*t + 1.0)*d0
          + (-6.0*t2 + 6.0*t)*f1 + (3.0*t2 - 2.0*t)*d1)/h;
    }
  }
  v += p.offset;
}

//----------------------------------------------------------------------------------------
//! \struct SfOptions
//! \brief run-time options of the scalar field (<scalar_field> block)

struct SfOptions {
  bool couple;          // the sources enter the spacetime solver and the constraints
  Real diss;            // Kreiss-Oliger coefficient (default: <z4c> diss)
  int hist_dcycle;      // cycles between records of <basename>.sf.hst (0 = off)
  int dump_dcycle;      // cycles between double-precision dumps (0 = off)
  Real dump_dt;         // time between dumps (<= 0 = off)
};

//----------------------------------------------------------------------------------------
//! \struct SfNoiseOptions
//! \brief options of the stochastic sources (<scalar_field> noise_*)

enum SfNoiseModel {kNoisePower = 0, kNoiseMS = 1};
enum SfNoiseScheme {kNoiseFrozen = 0, kNoiseMarkov = 1};
enum SfNoiseWindow {kWindowTanh = 0, kWindowHeaviside = 1};

struct SfNoiseOptions {
  bool on = false;
  int model = kNoisePower;     // power: prescribed amplitude and window;
                               // mukhanov_sasaki: sources of arXiv:2512.14649
  int scheme = kNoiseFrozen;   // power model: frozen amplitudes, or new ones every step
  int window = kWindowTanh;
  Real sharpness = 5.0;        // s of W = (1 + tanh[s ln(k_sigma/k)])/2
  int nmax2 = 0;               // modes with 0 < |n|^2 <= nmax2
  std::uint64_t seed = 0;      // <job> rng_seed
  // power model: <|xi_n|^2> = amp^2 q^(tilt-3) L^-3 x (dW)^2 (frozen) or dW (markov),
  // q = |n|, dW the change of the window over the step, k_sigma/k_f = ksigma0
  // exp(hubble (t - t0)); sources c_phi xi/dt of phi and c_pi xi'/dt of Pi
  Real amp = 0.0, tilt = 0.0;
  Real ksigma0 = 1.0, hubble = 1.0, t0 = 0.0;
  Real c_phi = 0.0, c_pi = 0.0;
  int pi_dof = 1;              // degree of freedom of the noise of Pi (0: that of phi)
  // Mukhanov-Sasaki model
  Real sigma = 1.0;            // k_sigma = sigma a H
  int level = 0;               // background: 0 Friedmann equations integrated with the
                               // mode functions, 1 box means of the mesh
  int projector = 0;           // wave number of the trace-free projector: 0 that of the
                               // centred first difference, 1 the continuum one
  bool kick_pi = true, kick_k = true, kick_a = true;
  Real pi_sign = 1.0;          // -1: negative control (first-order constraint violation)
  std::string mode_file;       // mode functions at the start (see scalar_field_noise.cpp)
};

//----------------------------------------------------------------------------------------
//! \struct SfDiagOptions
//! \brief options of the constraint record <basename>.sf.con.hst and of the extended
//! dumps (scalar_field_diag.cpp).  Read only when present in the input, so that the
//! parameter list of existing inputs is unchanged.

struct SfDiagOptions {
  int con_dcycle = 0;            // cycles between records of <basename>.sf.con.hst
  bool dump_metric = false;      // dumps: add gt_ij and At_ij
  bool dump_magnitudes = false;  // dumps: add [H], [M] and M_i in BSSN form
  bool dump_constraints = true;  // dumps: H, M_i, E
  bool dump_noise = true;        // dumps: the stochastic fields
  bool con_signed = false;       // record: signed means of H, M_i and the spread of H
                                 // about its mean (scalar_field_diag.cpp)
};

//----------------------------------------------------------------------------------------
//! \class ScalarField

class ScalarField {
 public:
  ScalarField(MeshBlockPack *ppack, ParameterInput *pin);
  ~ScalarField();

  // Indices of evolved variables
  enum {I_SF_PHI, I_SF_PI, nsf};
  // Names of the variables
  static char const * const SF_names[nsf];

  // data
  DvceArray5D<Real> u0;         // solution
  DvceArray5D<Real> u1;         // solution at the intermediate step
  DvceArray5D<Real> u_rhs;      // right-hand side
  DvceArray5D<Real> coarse_u0;  // coarse representation (refined meshes)

  struct SF_vars {
    AthenaTensor<Real, TensorSymm::NONE, 3, 0> phi;
    AthenaTensor<Real, TensorSymm::NONE, 3, 0> vPi;
  };
  SF_vars sf;
  SF_vars rhs;

  SfOptions opt;
  SfPotential pot;
  DualArray2D<Real> pot_tab;    // table of the potential (kind = table)
  Real diss;                    // dissipation parameter in the form used by Diss<NGHOST>

  // Boundary communication buffers and functions for u
  MeshBoundaryValuesCC *pbval_u;

  // ---- tasks
  void QueueTasks();
  TaskStatus InitRecv(Driver *d, int stage);
  TaskStatus ClearRecv(Driver *d, int stage);
  TaskStatus ClearSend(Driver *d, int stage);
  TaskStatus CopyU(Driver *d, int stage);
  TaskStatus SetTmunu(Driver *d, int stage);
  TaskStatus CalcRHS_(Driver *d, int stage);
  TaskStatus Kick(Driver *d, int stage);
  TaskStatus ExpRKUpdate(Driver *d, int stage);
  TaskStatus RestrictU(Driver *d, int stage);
  TaskStatus SendU(Driver *d, int stage);
  TaskStatus RecvU(Driver *d, int stage);
  TaskStatus Prolongate(Driver *d, int stage);
  TaskStatus ApplyPhysicalBCs(Driver *d, int stage);
  TaskStatus Diagnostics(Driver *d, int stage);

  // ---- field equations and sources (scalar_field_rhs.cpp)
  template <int NGHOST>
  void CalcRHS(Driver *d, int stage);
  template <int NGHOST>
  void AssembleSourcesT(const bool stage_sources);
  void AssembleSources(const bool stage_sources);

  // ---- start, diagnostics, restart (scalar_field_io.cpp)
  void Startup(bool res_flag);
  void MeshMeans(Real mean[8]);
  void WriteHistory(Real time, int ncycle, bool header);
  void WriteDump(Real time);
  void WriteRestart(const std::string &fname);
  void ReadRestart(const std::string &fname);
  std::string basename;
  int dump_number = 0;
  Real dump_next_time = 0.0;

  // ---- stochastic sources (scalar_field_noise.cpp)
  SfNoiseOptions nopt;
  int nfld = 0;                      // number of synthesized fields
  DvceArray5D<Real> u_noise;         // the fields on the mesh (active cells)
  // modes of the hemisphere, ordered for the three one-dimensional sums:
  // by n_x, then n_y, then n_z
  int nmode = 0, npair = 0, nxval = 0, nshell = 0, nmax = 0;
  std::vector<int> mode_n;           // (n_x, n_y, n_z) of every mode
  std::vector<int> shell_n2;         // distinct |n|^2
  DvceArray1D<int> mode_nz, mode_shell, pair_start, pair_ny, xval_start, xval_nx;
  DvceArray2D<Real> alpha_re, alpha_im;   // (dof, mode) amplitudes
  DvceArray2D<Real> proj;                 // (field, mode) real factor of the coefficient
  DvceArray1D<int> fld_dof;               // degree of freedom of each field
  DvceArray1D<Real> shell_re, shell_im;   // complex factor of each shell at this stage
  DvceArray4D<Real> trig_c, trig_s;       // (MeshBlock, direction, n + nmax, cell)
  DvceArray3D<Real> g1_re, g1_im;         // work arrays of the synthesis
  DvceArray4D<Real> g2_re, g2_im;
  std::uint64_t alpha_epoch = 0;          // step word of the amplitudes held
  bool alpha_valid = false;
  int fields_cycle = -1;                  // cycle whose increments u_noise holds
  // mode data integrated in lockstep with the fields (host):
  // y = (t, phi_b, Pi_b, ln a, then Re R, Im R, Re dR, Im dR of every shell)
  std::vector<Real> y0, y1, yrhs;
  // quantities of the current stage used by the kicks
  Real kick_pi_fac = 0.0, kick_k_fac = 0.0, kick_a_fac = 0.0;
  Real stage_eps1 = 0.0, stage_eps2 = 0.0, stage_hub = 0.0, stage_a = 1.0;
  bool noise_ready = false;

  void NoiseInit(ParameterInput *pin);
  void NoiseSetup(bool res_flag);
  void NoiseDrawAlpha(const std::uint64_t epoch);
  void NoiseBackground(const std::vector<Real> &y, Real bg[8]);
  void NoiseModeRHS(const std::vector<Real> &y, std::vector<Real> &f);
  void NoiseShellFactors(const std::vector<Real> &y);
  void NoiseSynthesize();
  void NoiseStage(Driver *d, int stage);
  void NoiseCopy(Driver *d, int stage);
  void NoiseUpdate(Driver *d, int stage);
  void NoiseFieldsOfState();
  void NoiseWriteState(Real time, int ncycle, bool header);

  // ---- initial slice of the stochastic-inflation runs (scalar_field_slice.cpp)
  void InitialSlice(ParameterInput *pin, const Real phib0, const Real pib0);
  bool slice_done = false;           // the stochastic sources were set up by InitialSlice
  Real mode_scale = 1.0;             // factor on the mode functions of the mode file

  // ---- constraint magnitudes and extended dumps (scalar_field_diag.cpp)
  SfDiagOptions dopt;
  DvceArray5D<Real> u_mag;           // [H], [M], M_i in BSSN form (active cells)
  bool mag_alloc = false;
  void DiagInit(ParameterInput *pin);
  template <int NGHOST>
  void ConstraintMagnitudesT();
  void ConstraintMagnitudes();
  void WriteConstraintHistory(Real time, int ncycle, bool header);
  void ConstraintSignedMeans(Real out[7]);
  bool DumpIsExtended() const;
  void WriteDumpExtended(Real time);

 private:
  MeshBlockPack* pmy_pack;  // ptr to MeshBlockPack containing this ScalarField
};

} // namespace scalarfield
#endif // SCALAR_FIELD_SCALAR_FIELD_HPP_
