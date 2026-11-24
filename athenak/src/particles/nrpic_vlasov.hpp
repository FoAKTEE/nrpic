#ifndef PARTICLES_NRPIC_VLASOV_HPP_
#define PARTICLES_NRPIC_VLASOV_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_vlasov.hpp
//! \brief Data structures and runtime options for the direct 6+1D General-Relativistic
//! Lagrangian-Basis Vlasov (GR-LBV) finite-volume / MFM solver inside NRPIC.

#include <vector>

#include "athena.hpp"
#include "particles/nrpic_vlasov_kernels.hpp"

namespace particles {

enum VlasovPairMode {
  VLASOV_PAIR_EB = 0,
  VLASOV_PAIR_VONLY = 1
};

// Indices of symmetric 3x3 tensor packed into 6 components: (0,0),(0,1),(0,2),(1,1),(1,2),(2,2)
enum VlasovSym6 {
  SYM_XX = 0,
  SYM_XY = 1,
  SYM_XZ = 2,
  SYM_YY = 3,
  SYM_YZ = 4,
  SYM_ZZ = 5,
  N_SYM6 = 6
};

struct VlasovOptions {
  int basis_kind = nrpic::vlasov::BASIS_TOPHAT;
  int n_perp = 3;
  int n_q_kick = 3;
  int n_q_dep = 3;
  int pair_mode = VLASOV_PAIR_EB;
  bool use_analytic_vf = false;
  Real cfl = 0.3;
  int fixed_substeps = 0;     // >0 overrides adaptive CFL subcycling (for parity tests)
  int max_substeps = 64;
  Real coll_sigma = 0.0;      // sigma / mu in M^{-1} (<= 0: collisionless)
  bool bgk_track_e = false;   // true on flat static mesh to pass E_cons override to BGK
  Real lim_eps_v = 0.1;       // velocity-crossing gradient limiter scale factor
  bool bnd_detect = false;    // detect & zero gradients on vacuum-boundary elements
  Real bnd_cm_tol = 0.35;
  int bnd_min_ngb = 12;
  int substeps_last = 0;
  Real max_sig_last = 0.0;
};

struct VlasovState {
  VlasovOptions opt;
  int n_elem = 0;
  int n_basis = 0;
  int max_ngb = 64;
  int n_edges = 0;
  int edge_cap = 0;
  int grid_cap = 0;
  bool initialized = false;
  Real load_time = 0.0;

  // Spatial coordinate arrays (last index is element index a for coalesced GPU access)
  DvceArray2D<Real> x;        // (3, N)
  DvceArray2D<Real> x0;       // (3, N)
  DvceArray2D<Real> v_cell;   // (3, N)
  DvceArray2D<Real> v0_cell;  // (3, N)
  DvceArray2D<Real> u_bulk;   // (3, N)

  // Conservative basis moments
  DvceArray2D<Real> m;        // (Nb, N)
  DvceArray2D<Real> m0;       // (Nb, N)
  DvceArray2D<Real> dm;       // (Nb, N)
  DvceArray3D<Real> P;        // (Nb, 3, N)
  DvceArray3D<Real> P0;       // (Nb, 3, N)
  DvceArray3D<Real> dP;       // (Nb, 3, N)
  DvceArray3D<Real> Pi;       // (Nb, 6, N)  packed symmetric 3x3
  DvceArray3D<Real> Pi0;      // (Nb, 6, N)
  DvceArray3D<Real> dPi;      // (Nb, 6, N)

  // Energy tracking for flat-space collisional HLLC+BGK
  DvceArray1D<Real> E0;       // (N)
  DvceArray1D<Real> E_cons;   // (N)
  DvceArray1D<Real> dE;       // (N)

  // Primitive basis variables
  DvceArray2D<Real> D;        // (Nb, N)
  DvceArray3D<Real> u_bar;    // (Nb, 3, N)
  DvceArray3D<Real> Sigma;    // (Nb, 6, N)  packed symmetric 3x3

  // MFM element geometry & flags
  DvceArray1D<Real> h;        // (N)
  DvceArray1D<Real> V;        // (N)
  DvceArray2D<Real> Einv;     // (6, N)      packed symmetric 3x3
  DvceArray1D<int> active;    // (N)         1 = live, 0 = excised/escaped
  DvceArray1D<int> species;   // (N)
  DvceArray1D<int> blk_gid;   // (N)
  DvceArray1D<int> is_bnd;    // (N)

  // Limited MLS gradients
  DvceArray3D<Real> grad_D;   // (Nb, 3, N)
  DvceArray4D<Real> grad_u;   // (Nb, 3, 3, N)      (al, comp_u, grad_dir, a)
  DvceArray4D<Real> grad_S;   // (Nb, 6, 3, N)      (al, sym6, grad_dir, a)

  // Neighbor & persistent basis pairing tables
  DvceArray1D<int> ngb_cnt;   // (N)
  DvceArray2D<int> ngb_ids;   // (max_ngb, N)       sorted ascending per a
  DvceArray2D<int> new_pab;   // (max_ngb*Nb, N)    slot k * Nb + al -> beta
  DvceArray1D<int> prev_cnt;  // (N)
  DvceArray2D<int> prev_ids;  // (max_ngb, N)
  DvceArray2D<int> prev_pab;  // (max_ngb*Nb, N)

  // Unique unordered edges (a < b)
  DvceArray1D<int> edge_off;  // (N)
  DvceArray1D<int> edge_a;    // (edge_cap)
  DvceArray1D<int> edge_b;    // (edge_cap)

  // Spatial CSR hash grid buffers
  DvceArray1D<int> grid_cell_id;  // (N)
  DvceArray1D<int> grid_cnt;      // (grid_cap)
  DvceArray1D<int> grid_off;      // (grid_cap)
  DvceArray1D<int> grid_cur;      // (grid_cap)
  DvceArray1D<int> grid_elem;     // (N)

  // Restart staging buffers
  std::vector<double> restart_real;
  std::vector<int> restart_int;
  std::vector<int> restart_meta;
};

}  // namespace particles

#endif  // PARTICLES_NRPIC_VLASOV_HPP_
