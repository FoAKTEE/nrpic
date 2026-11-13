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
enum NrpicRealIndex {IPM=6, NRPIC_NRDATA=7};       // rest mass
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
  int deposit_max_level;  // finest refinement level on which a cloud is represented
  bool deposit_adaptive;  // choose the level of each cloud from the local density
  int deposit_min_level;  // coarsest level of a cloud with the adaptive choice
  Real deposit_ppc;       // target number of particles per cloud cell
  Real alpha_exc;       // particles with interpolated lapse below this are removed
  int hist_dcycle;      // cycles between history records (0 = off)
  int traj_dcycle;      // cycles between trajectory records (0 = off)
  int traj_ntrack;      // particles with tag < traj_ntrack are recorded
  Real snap_dt;         // time between full particle snapshots (<= 0 = off)
  Real probe[3];        // position of the lapse/energy-density probe
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
  DvceArray4D<Real> e_prev;        // sqrt(gamma) E of the previous deposit
  bool e_prev_valid = false;       // e_prev belongs to the current mesh
  DvceArray5D<Real> coarse_tm;     // coarse sources (ghost exchange with SMR/AMR)
  MeshBoundaryValuesCC *pbval_tm = nullptr;
  bool metric_is_static = true;    // true unless Z4c evolves the spacetime
  // run statistics (persist across restarts)
  Real tau_probe = 0.0;            // proper time of the normal observer at the probe
  Real alpha_probe = 1.0;          // lapse at the probe
  Real e_probe = 0.0;              // deposited energy density at the probe
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

  void NrpicInit(ParameterInput *pin);
  void SetNumberOfParticles(int n);
  void NrpicCreateParticles();
  void NrpicLoadParticleFile(const std::string &fname);
  void NrpicFillMetric(DvceArray5D<Real> &met);
  void NrpicAssignBlocks();
  void NrpicRemoveFlagged();
  void NrpicDepositSources();
  void NrpicFilterSources();
  void NrpicProbe(Real dt);
  void NrpicInitializeSources();
  void NrpicStartup(bool res_flag);
  void NrpicWriteHistory(Real time, int ncycle, bool header);
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
