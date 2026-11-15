#ifndef PARTICLES_PARTICLES_HPP_
#define PARTICLES_PARTICLES_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file particles.hpp
//  \brief definitions for Particles class

#include <cstdint>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include "athena.hpp"
#include "parameter_input.hpp"
#include "tasklist/task_list.hpp"
#include "bvals/bvals.hpp"

// forward declarations

// constants that enumerate ParticlesPusher options
enum class ParticlesPusher {drift, leap_frog, lagrangian_tracer, lagrangian_mc,
                            nrpic_midpoint, nrpic_boris, nrpic_newton};

// constants that enumerate ParticleTypes
enum class ParticleType {cosmic_ray, nrpic};

// Additional array indices used by particles of type "nrpic".  Positions are stored in
// IPX,IPY,IPZ and the covariant spatial four-velocity components u_i (momentum per unit
// rest mass) in IPVX,IPVY,IPVZ.
// rest mass and proper time.  m > 0: particle with sources; m = 0: tracer, a test
// particle on a timelike geodesic without sources (a null particle only with
// <particles> zero_mass = null); m = -t_e < 0: null particle (light ray) emitted at the
// time t_e, whose proper-time slot holds the affine parameter
enum NrpicRealIndex {IPM=6, IPTAU=7, NRPIC_NRDATA=8};
enum NrpicIntIndex  {PSP=2, NRPIC_NIDATA=3};       // species
// Layout of the metric arrays seen by the pushers
enum NrpicMetricIndex {NRM_ALP=0, NRM_BX=1, NRM_BY=2, NRM_BZ=3, NRM_GXX=4, NRM_GXY=5,
                       NRM_GXZ=6, NRM_GYY=7, NRM_GYZ=8, NRM_GZZ=9, NRM_NVAR=10};

// source of the metric used by the nrpic pushers
enum class NrpicMetric {mesh, kerr_schild, kerr_schild_sph, boyer_lindquist, lattice};

//----------------------------------------------------------------------------------------
//! \struct NrpicOptions
//  rief run-time options of the numerical-relativity particle-in-cell module

struct NrpicOptions {
  NrpicMetric metric;   // where the pushers take the metric from
  int triad;            // triad gauge of the Boris pusher (nrpic::TriadKind)
  Real tol;             // convergence threshold of the implicit iterations
  int maxit;            // maximum number of implicit iterations
  Real mass, spin;      // parameters of the analytic Kerr metrics
  Real lattice_dx;      // spacing of the virtual lattice (metric = lattice)
  bool deposit;         // deposit particle stress-energy onto the mesh
  int nfilter;          // number of binomial filter passes applied to the sources
  bool filter_compensate;  // follow them by one pass (-c, 1+2c, -c)^3 that cancels
                           // the second moment of the binomial passes (c = nfilter/4)
  Real filter_comp_c;      // c of that pass if >= 0 (default -1: nfilter/4)
  bool field_constraints;  // field dumps also hold the constraints, Khat, Theta, lapse
  bool interp_bspline;     // metric at the particles by the cubic spline through the
                           // nodes instead of the Catmull-Rom reconstruction
  Real dt_expansion;       // > 0: step limited to this fraction of the expansion time
                           // 3/|mean(alpha Khat)| (cosmological runs)
  Real deposit_comp_c;     // > 0: pass (-c, 1+2c, -c)^3 on the deposited densities, before
                           // the division by sqrt(gamma), compensating the cloud
  Real deposit_comp_limit; // > 0: that pass in flux form, each face flux at most this
                           // fraction of the smaller neighbouring energy density
  Real deposit_comp_c2;    // fourth-order term of the pass, (c2/16) x fourth difference
                           // (8/45, 37/120, 7/15 for the linear, quadratic, cubic cloud)
  int deposit_max_level;  // finest refinement level on which a cloud is represented
  bool deposit_adaptive;  // choose the level of each cloud from the local density
  int deposit_min_level;  // coarsest level of a cloud with the adaptive choice
  Real deposit_ppc;       // target number of particles per cloud cell
  int deposit_max_coarsen;  // a cloud is at most this many levels coarser than the
                            // particle's own MeshBlock (31: no limit)
  Real alpha_exc;       // particles with interpolated lapse below this are removed
  Real ah_exc_factor;   // particles inside this fraction of a horizon radius are removed
  int hist_dcycle;      // cycles between history records (0 = off)
  int traj_dcycle;      // cycles between trajectory records (0 = off)
  int cstat_dcycle;     // cycles between constraint-statistics records (0 = off)
  int cons_dcycle;      // cycles between records of the conservation of the deposited
                        // matter on the mesh (0 = off)
  int line_dcycle;      // cycles between records of the fields along an x1 line (0 = off)
  int traj_ntrack;      // particles with tag < traj_ntrack are recorded
  Real snap_dt;         // time between full particle snapshots (<= 0 = off)
  Real probe[3];        // position of the lapse/energy-density probe
  int nprobe;           // number of additional probes (at most 8)
  Real probes[8][3];    // their positions
  bool periodic[3];     // periodic mesh direction: particles and their clouds wrap
  Real dom_min[3];      // lower edge and length of the mesh in each direction
  Real dom_len[3];
  Real lambda;          // cosmological constant, added to the sources as vacuum energy
  bool source_density;  // hand the spacetime solver densities (sources x sqrt(gamma)),
                        // converted with the volume element of each of its stages
  bool source_extrap;   // ... extrapolated to the middle of the step from the last two
                        // deposits, D = 3/2 D^n - 1/2 D^(n-1)
  int deposit_shape;    // degree of the B-spline cloud of the deposit: 1 (cloud in
                        // cell), 2 (triangular shaped cloud), 3 (piecewise cubic)
  Real curv_dt;         // time between curvature diagnostics (<= 0 = off)
  bool curv_slice;      // also write the cut through the plane y = curv_plane_y
  Real curv_plane_y;
  // ---- Newtonian mode (<particles> pusher = newton; particles/nrpic_newton.cpp) ----
  bool newton = false;      // Newtonian gravity: Poisson equation and kick-drift-kick
  int newton_expansion = 0; // 0: no expansion (a = 1); 1: comoving coordinates and
                            // conformal time t with a = (1 + hubble t/n)^n
  Real newton_hubble = 0.0;    // Hubble rate at t = 0, where a = 1
  Real newton_exponent = 2.0;  // n (2: matter era, 1: radiation era)
  Real newton_cfl = 0.0;       // > 0: step at most this fraction of dx/max|dx/dt|
  Real newton_mg_tol = 0.0;    // > 0: the Poisson solve may end when the defect norm
                               // is this fraction of the norm of the source
  // ---- meaning of a particle without rest mass (<particles> zero_mass) ----
  bool zero_mass_null = false; // false (tracer): m = 0 is a test particle on a timelike
                               // geodesic that carries no sources; true (null): m = 0
                               // follows a null geodesic on the mesh metric, the rule of
                               // releases core-v0.2 and core-v0.3
};

//----------------------------------------------------------------------------------------
//! \struct NrpicKickOptions
//  \brief options and state of the test kick with reproducible random numbers
//  (nrpic_kick.cpp)

struct NrpicKickOptions {
  bool on = false;           // <particles> test_kick
  int mode = 0;              // 0: three normal deviates, 1: random direction
  int key = 0;               // 0: tag, 1: tag and MeshBlock, 2: tag and call count
  Real sigma = 0.0;          // size of the kick
  Real prob = 1.0;           // probability of a kick per step (mode 1)
  std::uint64_t seed = 0;    // seed of the run (<job> rng_seed)
  std::int64_t ncalls = 0;   // kicks applied since the executable started
};

//----------------------------------------------------------------------------------------
//! \struct NrpicCollideOptions
//  \brief options of the Monte Carlo collision operator (nrpic_collide.cpp)

struct NrpicCollideOptions {
  bool on = false;           // <particles> collisions
  Real sigma = 0.0;          // cross-section per unit mass (code units)
  int model = 0;             // velocity dependence (nrpic::CollSigmaModel)
  Real sigma_w = 1.0;        // its velocity scale
  Real pmax = 0.1;           // largest pair probability per sub-step aimed at
  int subcycle = 0;          // 0: sub-steps from the speeds of the cell, 1: v_Mol < 2
  int nsub_max = 1000;       // largest number of sub-steps of a cell
  int cell_factor = 1;       // a collision cell is a block of cell_factor^3 mesh cells
  int weights = 0;           // 0: equal rest masses required, 1: Nanbu-Yonemura
  int hist_dcycle = 1;       // cycles between records of <basename>.coll.hst
  int dump_cycle = -1;       // cycle whose collision step is dumped
  bool budget = false;       // record the energy with the metric at the particles
  std::uint64_t seed = 0;    // seed of the run (<job> rng_seed)
  int face_maxlev = -1;      // finest level of the tabulated face positions
  bool face_warned = false;  // the warning about MeshBlock edges has been printed
};

//----------------------------------------------------------------------------------------
//! \struct ParticlesTaskIDs
//  \brief container to hold TaskIDs of all particles tasks

struct ParticlesTaskIDs {
  TaskID savemet;
  TaskID excise;
  TaskID collide;
  TaskID deposit;
  TaskID diag;
  TaskID push;
  TaskID newgid;
  TaskID count;
  TaskID irecv;
  TaskID sendp;
  TaskID recvp;
  TaskID csend;
  TaskID crecv;
};

namespace particles {

//----------------------------------------------------------------------------------------
//! \class Particles

class Particles {
  friend class ParticlesBoundaryValues;
 public:
  Particles(MeshBlockPack *ppack, ParameterInput *pin);
  ~Particles();

  // data
  ParticleType particle_type;
  int nprtcl_thispack;             // number of particles this MeshBlockPack
  int nrdata, nidata;
//  DvceArray1D<int>  prtcl_gid;     // GID of MeshBlock containing each par
//  DvceArray2D<Real> prtcl_pos;     // positions
//  DvceArray2D<Real> prtcl_vel;     // velocities
  DvceArray2D<Real> prtcl_rdata;   // real number properties each particle (x,v,etc.)
  DvceArray2D<int>  prtcl_idata;   // integer properties each particle (gid, tag, etc.)
  Real dtnew;
  Real dt_user = 0.0;          // <particles> dt (upper limit of the step)
  DvceArray5D<Real> cons_new, cons_old, cons_d2;   // conservation diagnostic
  DvceArray5D<Real> met0s, met1s, met_work;        // sharpened metric (interp = bspline)
  int cons_valid = 0;
  Real cons_dt_prev = 0.0;
  Real dt_probe_old = -1.0;    // previous step (third-order proper time of the probes)

  ParticlesPusher pusher;

  // Boundary communication buffers and functions for particles
  ParticlesBoundaryValues *pbval_part;

  // container to hold names of TaskIDs
  ParticlesTaskIDs id;

  // functions...
  void CreateParticleTags(ParameterInput *pin);
  void AssembleTasks(std::map<std::string, std::shared_ptr<TaskList>> tl);
  TaskStatus Push(Driver *pdriver, int stage);
  TaskStatus NewGID(Driver *pdriver, int stage);
  TaskStatus SendCnt(Driver *pdriver, int stage);
  TaskStatus InitRecv(Driver *pdriver, int stage);
  TaskStatus SendP(Driver *pdriver, int stage);
  TaskStatus RecvP(Driver *pdriver, int stage);
  TaskStatus ClearSend(Driver *pdriver, int stage);
  TaskStatus ClearRecv(Driver *pdriver, int stage);

  // ---- numerical-relativity particle-in-cell (particle_type = nrpic) ----
  bool is_nrpic = false;
  NrpicOptions nropt;
  std::string nr_basename;         // basename of the output files
  std::string nr_particle_file;    // particle input file of a new run (may be empty)
  std::vector<Real> nr_inline;     // particles listed in the input file (7 per particle)
  DvceArray5D<Real> met0;          // alpha, beta^i, gamma_ij at t^n
  DvceArray5D<Real> met1;          // alpha, beta^i, gamma_ij at t^{n+1}
  DvceArray5D<Real> tm_work;       // work array for the source filter
  DvceArray5D<Real> tm_prev;       // source densities of the previous deposit
  bool tm_prev_valid = false;      // tm_prev belongs to the current mesh
  DvceArray4D<Real> e_prev;        // sqrt(gamma) E of the previous deposit
  bool e_prev_valid = false;       // e_prev belongs to the current mesh
  DvceArray5D<Real> coarse_tm;     // coarse sources (ghost exchange with SMR/AMR)
  MeshBoundaryValuesCC *pbval_tm = nullptr;
  bool metric_is_static = true;    // true unless Z4c evolves the spacetime
  // run statistics (persist across restarts)
  Real tau_probe = 0.0;            // proper time of the normal observer at the probe
  Real alpha_probe = 1.0;          // lapse at the probe
  Real e_probe = 0.0;              // deposited energy density at the probe
  Real tau_probes[8] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};   // additional probes
  Real alpha_probes[8] = {1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0};
  Real e_probes[8] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
  // lapse at the probes one step earlier (index 0: the main probe) for the third-order
  // integration of their proper time; negative: not available
  Real alpha_probe_old[9] = {-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0};
  long n_bad_det_total = 0;        // cells whose sources were zeroed (det <= 0), summed
  int n_bad_det_reports = 0;       // number of such events reported so far
  Real mass_excised = 0.0;         // rest mass removed by excision
  Real mass_escaped = 0.0;         // rest mass removed at the domain boundary
  int  n_excised = 0, n_escaped = 0;
  int  snap_number = 0;
  Real snap_next_time = 0.0;
  int  curv_number = 0;
  Real curv_next_time = 0.0;
  int nfield_times = 0;          // times at which the energy density is dumped
  Real field_times[16];
  int field_next = 0;
  std::vector<double> ts_restart;      // source densities read from a restart file
  std::int64_t ts_restart_dims[5] = {0, 0, 0, 0, 0};
  // statistics of the last step
  int  push_maxit = 0, push_unconverged = 0;
  Real sum_m = 0.0, sum_mw = 0.0, sum_mu[3] = {0.0, 0.0, 0.0};
  Real dep_sum[4] = {0.0, 0.0, 0.0, 0.0};   // mesh integrals of E, S_i sqrt(gamma) dV
  Real dep_sum_filt[4] = {0.0, 0.0, 0.0, 0.0};   // the same after the filter

  void NrpicInit(ParameterInput *pin);
  void SetNumberOfParticles(int n);
  void NrpicCreateParticles();
  void NrpicLoadParticleFile(const std::string &fname);
  void NrpicFillMetric(DvceArray5D<Real> &met);
  void NrpicSharpenMetric(DvceArray5D<Real> &met, DvceArray5D<Real> &mets);
  void NrpicAssignBlocks();
  void NrpicRemoveFlagged();
  void NrpicDepositSources();
  void NrpicFilterPass(const Real w0, const Real w1);
  void NrpicWriteConservation(Real time, Real dt, bool header, bool write);
  void NrpicCompensateLimited(const Real c, const Real c2, const Real lim);
  void NrpicUpdateTimeStep();
  void NrpicFilterSources();
  void NrpicAddLambda();
  void NrpicStepSources();
  void NrpicProbe(Real dt);
  void NrpicInitializeSources();
  void NrpicStartup(bool res_flag);
  void NrpicReportMassless();
  void NrpicWriteHistory(Real time, int ncycle, bool header);
  void NrpicWriteConstraintStats(Real time, bool header);
  void NrpicWriteLine(Real time, bool header);
  void NrpicWriteEnergyField(Real time, int index);
  void NrpicWriteTrajectories(Real time, bool truncate);
  void NrpicWriteSnapshot(Real time);
  void NrpicWriteCurvature(Real time);
  void NrpicWriteRestart(const std::string &fname);
  void NrpicReadRestart(const std::string &fname);
  TaskStatus NrpicSaveMetric(Driver *pdriver, int stage);
  TaskStatus NrpicPush(Driver *pdriver, int stage);
  TaskStatus NrpicExcise(Driver *pdriver, int stage);
  TaskStatus NrpicDeposit(Driver *pdriver, int stage);
  TaskStatus NrpicDiagnostics(Driver *pdriver, int stage);

  // test kick with reproducible random numbers (nrpic_kick.cpp)
  NrpicKickOptions kick;
  void NrpicKickInit(ParameterInput *pin);
  void NrpicTestKick();

  // Monte Carlo collisions (nrpic_collide.cpp)
  NrpicCollideOptions coll;
  DvceArray1D<int> coll_cell, coll_list, coll_count, coll_begin;   // cell lists
  DvceArray1D<std::uint64_t> coll_key;                             // pairing words
  DvceArray1D<Real> coll_face;                                     // face positions
  void NrpicCollideInit(ParameterInput *pin);
  TaskStatus NrpicCollide(Driver *pdriver, int stage);

  // ---- Newtonian mode of the nrpic module (particles/nrpic_newton.cpp) ----
  // The potential of the Poisson equation is held in the lapse slot of met1 (the
  // other slots hold the flat metric), so that the deposit and the interpolation of
  // the relativistic mode serve unchanged.
  Driver *nw_driver = nullptr;      // the Poisson solver runs task lists of the driver
  MeshBoundaryValuesCC *pbval_phi = nullptr;   // ghost cells of the potential
  DvceArray5D<Real> nw_coarse_phi;  // coarse potential (ghost exchange, refined meshes)
  Real nw_sum[30];                  // particle sums of the last synchronised state
  Real nw_mesh[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};   // mesh sums of the last solve
  Real nw_time = 0.0, nw_a = 1.0;   // time and scale factor of that state
  Real nw_li = 0.0;                 // Layzer-Irvine integral of K da since the start
  Real nw_d3i[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};   // third derivative of the second
  Real nw_d3i_time = 0.0;           // moment, and the (mid-step) time it belongs to
  Real nw_pmax = 0.0;               // largest momentum per unit mass (step limit)
  Real nw_gmax = 0.0;               // largest acceleration (step limit)
  Real nw_defect = 0.0;             // defect norm of the last Poisson solve
  int nw_ncycle = 0;                // and its number of V cycles
  bool nw_valid = false;            // nw_sum holds a state of this run
  std::vector<double> nw_phi_restart;      // potential read from a restart file
  std::int64_t nw_phi_restart_dims[5] = {0, 0, 0, 0, 0};
  std::vector<double> nw_state_restart;    // diagnostic state read from a restart file

  void NrpicNewtonInit(ParameterInput *pin);
  void NrpicNewtonInitialize();
  void NrpicNewtonPotential();
  void NrpicNewtonKick(const Real dt_kick, const Real time);
  void NrpicNewtonFinishStep(Driver *pdriver);
  void NrpicNewtonTimeStep(const Real time);
  TaskStatus NrpicNewtonPush(Driver *pdriver, int stage);
  void NrpicNewtonWriteHistory(Real time, int ncycle, bool header);
  void NrpicNewtonWriteRestart(const std::string &fname);
  void NrpicNewtonReadRestart(const std::string &fname);

 private:
  MeshBlockPack* pmy_pack;  // ptr to MeshBlockPack containing this Particles
};

} // namespace particles
#endif // PARTICLES_PARTICLES_HPP_
