#ifndef PARTICLES_PARTICLES_HPP_
#define PARTICLES_PARTICLES_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file particles.hpp
//  \brief definitions for Particles class

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
                            nrpic_midpoint, nrpic_boris};

// constants that enumerate ParticleTypes
enum class ParticleType {cosmic_ray, nrpic};

// Additional array indices used by particles of type "nrpic".  Positions are stored in
// IPX,IPY,IPZ and the covariant spatial four-velocity components u_i (momentum per unit
// rest mass) in IPVX,IPVY,IPVZ.
// rest mass (zero: null particle, no sources) and proper time (affine parameter of a
// null particle)
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
};

//----------------------------------------------------------------------------------------
//! \struct ParticlesTaskIDs
//  \brief container to hold TaskIDs of all particles tasks

struct ParticlesTaskIDs {
  TaskID savemet;
  TaskID excise;
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
  void NrpicAssignBlocks();
  void NrpicRemoveFlagged();
  void NrpicDepositSources();
  void NrpicFilterSources();
  void NrpicAddLambda();
  void NrpicStepSources();
  void NrpicProbe(Real dt);
  void NrpicInitializeSources();
  void NrpicStartup(bool res_flag);
  void NrpicWriteHistory(Real time, int ncycle, bool header);
  void NrpicWriteConstraintStats(Real time, bool header);
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

 private:
  MeshBlockPack* pmy_pack;  // ptr to MeshBlockPack containing this Particles
};

} // namespace particles
#endif // PARTICLES_PARTICLES_HPP_
