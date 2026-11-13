//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================

#include <algorithm>
#include <cstdio>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

#include "z4c/z4c_amr.hpp"
#include "athena.hpp"
#include "globals.hpp"
#include "mesh/mesh.hpp"
#include "parameter_input.hpp"
#include "z4c/compact_object_tracker.hpp"
#include "z4c/z4c.hpp"

#define SQ(X) ((X)*(X))

namespace z4c {

// set some parameters
Z4c_AMR::Z4c_AMR(ParameterInput *pin) {
  std::string ref_method = pin->GetOrAddString("z4c_amr", "method", "trivial");
  if (ref_method == "trivial") {
    method = Trivial;
  } else if (ref_method == "tracker") {
    method = Tracker;
  } else if (ref_method == "chi") {
    method = Chi;
    chi_thresh = pin->GetOrAddReal("z4c_amr", "chi_min", 0.2);
  } else if (ref_method == "dchi") {
    method = dChi;
    dchi_thresh = pin->GetOrAddReal("z4c_amr", "dchi_max", 0.01);
  } else if (ref_method == "lohner") {
    method = Lohner;
    lohner_refine   = pin->GetOrAddReal("z4c_amr", "lohner_refine", 0.2);
    lohner_derefine = pin->GetOrAddReal("z4c_amr", "lohner_derefine", 0.02);
    lohner_eps      = pin->GetOrAddReal("z4c_amr", "lohner_eps", 0.01);
  } else {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line "
              << __LINE__ << std::endl;
    std::cout << "Unknown refinement strategy: " << ref_method << std::endl;
    std::exit(EXIT_FAILURE);
  }

  for (int nr = 0; nr < 16; ++nr) {
    std::string name = "radius_" + std::to_string(nr) + "_rad";
    if (pin->DoesParameterExist("z4c_amr", name)) {
      radius.push_back(pin->GetReal("z4c_amr", name));
      reflevel.push_back(pin->GetOrAddInteger(
          "z4c_amr", "radius_" + std::to_string(nr) + "_reflevel", -1));
    } else {
      break;
    }
  }
}

// 1: refines, -1: de-refines, 0: does nothing
void Z4c_AMR::Refine(MeshBlockPack *pmy_pack) {
  if (method == Tracker) {
    RefineTracker(pmy_pack);
  } else if (method == Chi) {
    RefineChiMin(pmy_pack);
  } else if (method == dChi) {
    RefineDchiMax(pmy_pack);
  } else if (method == Lohner) {
    RefineLohner(pmy_pack);
  }
  RefineRadii(pmy_pack);
}

// refine region within a certain distance from each compact object
// using exact minimum distance via AABB clamping, which correctly handles
// all cases: tracker nearest to a face, edge, or corner of the block.
void Z4c_AMR::RefineTracker(MeshBlockPack *pmbp) {
  Mesh *pmesh       = pmbp->pmesh;
  auto &refine_flag = pmesh->pmr->refine_flag;
  auto &size        = pmbp->pmb->mb_size;
  int nmb           = pmbp->nmb_thispack;
  int mbs           = pmesh->gids_eachrank[global_variable::my_rank];

  std::vector<int> flag;
  flag.reserve(pmbp->pz4c->ptracker.size());

  for (int m = 0; m < nmb; ++m) {
    // current refinement level
    int level = pmesh->lloc_eachmb[m + mbs].level - pmesh->root_level;

    // extract MeshBlock bounds
    Real &x1min = size.h_view(m).x1min;
    Real &x1max = size.h_view(m).x1max;
    Real &x2min = size.h_view(m).x2min;
    Real &x2max = size.h_view(m).x2max;
    Real &x3min = size.h_view(m).x3min;
    Real &x3max = size.h_view(m).x3max;

    flag.clear();
    for (auto &pt : pmbp->pz4c->ptracker) {
      // clamp tracker position to box bounds: closest point on the box
      Real cx = fmax(x1min, fmin(pt->GetPos(0), x1max));
      Real cy = fmax(x2min, fmin(pt->GetPos(1), x2max));
      Real cz = fmax(x3min, fmin(pt->GetPos(2), x3max));

      Real dmin2 = SQ(pt->GetPos(0) - cx) \
                   + SQ(pt->GetPos(1) - cy) \
                   + SQ(pt->GetPos(2) - cz);

      // safety net for radius = 0: dmin2 = 0 inside the block but 0 < SQ(0) is false
      bool iscontained =
        (pt->GetPos(0) >= x1min && pt->GetPos(0) <= x1max) &&
        (pt->GetPos(1) >= x2min && pt->GetPos(1) <= x2max) &&
        (pt->GetPos(2) >= x3min && pt->GetPos(2) <= x3max);

      if (dmin2 < SQ(pt->GetRadius()) || iscontained) {
        if (pt->GetReflevel() < 0 || level < pt->GetReflevel()) {
          flag.push_back(1);
        } else if (level == pt->GetReflevel()) {
          flag.push_back(0);
        } else {
          flag.push_back(-1);
        }
      } else {
        flag.push_back(-1);
      }
    }
    refine_flag.h_view(m + mbs) = *std::max_element(flag.begin(), flag.end());
  }

  // sync host and device
  refine_flag.template modify<HostMemSpace>();
  refine_flag.template sync<DevExeSpace>();
}

// refine based on min{chi}
void Z4c_AMR::RefineChiMin(MeshBlockPack *pmbp) {
  Mesh *pmesh       = pmbp->pmesh;
  int nmb           = pmbp->nmb_thispack;
  int mbs           = pmesh->gids_eachrank[global_variable::my_rank];
  auto &refine_flag = pmesh->pmr->refine_flag;
  auto &indcs       = pmesh->mb_indcs;
  int &is = indcs.is, nx1 = indcs.nx1;
  int &js = indcs.js, nx2 = indcs.nx2;
  int &ks = indcs.ks, nx3 = indcs.nx3;
  const int nkji = nx3 * nx2 * nx1;
  const int nji  = nx2 * nx1;
  auto &u0       = pmbp->pz4c->u0;
  int I_Z4C_CHI  = pmbp->pz4c->I_Z4C_CHI;
  // note: we need this to prevent capture by this in the lambda expr.
  auto chi_thresh = this->chi_thresh;

  par_for_outer(
    "Z4c_AMR::ChiMin", DevExeSpace(), 0, 0, 0, (nmb - 1),
    KOKKOS_LAMBDA(TeamMember_t tmember, const int m) {
      Real team_dmin;
      Kokkos::parallel_reduce(
        Kokkos::TeamThreadRange(tmember, nkji),
        [=](const int idx, Real &dmin) {
          int k = (idx) / nji;
          int j = (idx - k * nji) / nx1;
          int i = (idx - k * nji - j * nx1) + is;
          j += js;
          k += ks;
          dmin = fmin(u0(m, I_Z4C_CHI, k, j, i), dmin);
        },
        Kokkos::Min<Real>(team_dmin));

      if (team_dmin < chi_thresh) {
        refine_flag.d_view(m + mbs) = 1;
      }
      if (team_dmin > 1.25 * chi_thresh) {
        refine_flag.d_view(m + mbs) = -1;
      }
    });

  // sync host and device
  refine_flag.template modify<DevExeSpace>();
  refine_flag.template sync<HostMemSpace>();
}

// refine based on max{dchi}
void Z4c_AMR::RefineDchiMax(MeshBlockPack *pmbp) {
  Mesh *pmesh       = pmbp->pmesh;
  int nmb           = pmbp->nmb_thispack;
  int mbs           = pmesh->gids_eachrank[global_variable::my_rank];
  auto &refine_flag = pmesh->pmr->refine_flag;
  auto &indcs       = pmesh->mb_indcs;
  int &is = indcs.is, nx1 = indcs.nx1;
  int &js = indcs.js, nx2 = indcs.nx2;
  int &ks = indcs.ks, nx3 = indcs.nx3;
  const int nkji = nx3 * nx2 * nx1;
  const int nji  = nx2 * nx1;
  auto &u0       = pmbp->pz4c->u0;
  int I_Z4C_CHI  = pmbp->pz4c->I_Z4C_CHI;
  // note: we need this to prevent capture by this in the lambda expr.
  auto dchi_thresh = this->dchi_thresh;

  par_for_outer(
    "Z4c_AMR::ChiMin", DevExeSpace(), 0, 0, 0, (nmb - 1),
    KOKKOS_LAMBDA(TeamMember_t tmember, const int m) {
      Real team_dmax;
      Kokkos::parallel_reduce(
        Kokkos::TeamThreadRange(tmember, nkji),
        [=](const int idx, Real &dmax) {
          int k = (idx) / nji;
          int j = (idx - k * nji) / nx1;
          int i = (idx - k * nji - j * nx1) + is;
          j += js;
          k += ks;
          Real d2 = SQR(u0(m,I_Z4C_CHI,k,j,i+1) - u0(m,I_Z4C_CHI,k,j,i-1));
          d2 += SQR(u0(m,I_Z4C_CHI,k,j+1,i) - u0(m,I_Z4C_CHI,k,j-1,i));
          d2 += SQR(u0(m,I_Z4C_CHI,k+1,j,i) - u0(m,I_Z4C_CHI,k-1,j,i));
          dmax = fmax((sqrt(d2)), dmax);
        },
        Kokkos::Max<Real>(team_dmax));

      if (team_dmax > dchi_thresh) {
        refine_flag.d_view(m + mbs) = 1;
      }
      if (team_dmax < 0.5 * dchi_thresh) {
        refine_flag.d_view(m + mbs) = -1;
      }
    });

  // sync host and device
  refine_flag.template modify<DevExeSpace>();
  refine_flag.template sync<HostMemSpace>();
}

// refine based on the Lohner-type indicator of q = alpha psi^7 = alpha chi^(7/N), with
// chi = psi^N.  With the centred difference D_a q_i = q_{i+e_a} - q_{i-e_a} and the
// amplitude S_ab,i = sum_{s,t=+-1} |q_{i+s e_a+t e_b}|, the indicator of a cell is
//   E_i^2 = sum_ab (D_a q_{i+e_b} - D_a q_{i-e_b})^2
//         / sum_ab (|D_a q_{i+e_b}| + |D_a q_{i-e_b}| + eps S_ab,i + delta)^2 ,
// and a MeshBlock is flagged with the maximum over its active cells.
void Z4c_AMR::RefineLohner(MeshBlockPack *pmbp) {
  Mesh *pmesh       = pmbp->pmesh;
  int nmb           = pmbp->nmb_thispack;
  int mbs           = pmesh->gids_eachrank[global_variable::my_rank];
  auto &refine_flag = pmesh->pmr->refine_flag;
  auto &indcs       = pmesh->mb_indcs;
  int &is = indcs.is, nx1 = indcs.nx1;
  int &js = indcs.js, nx2 = indcs.nx2;
  int &ks = indcs.ks, nx3 = indcs.nx3;
  const int nkji = nx3 * nx2 * nx1;
  const int nji  = nx2 * nx1;
  const int n1 = nx1 + 2*indcs.ng, n2 = nx2 + 2*indcs.ng, n3 = nx3 + 2*indcs.ng;
  auto &u0        = pmbp->pz4c->u0;
  int I_Z4C_CHI   = pmbp->pz4c->I_Z4C_CHI;
  int I_Z4C_ALPHA = pmbp->pz4c->I_Z4C_ALPHA;
  const Real expo      = 7.0/pmbp->pz4c->opt.chi_psi_power;
  const Real chi_floor = pmbp->pz4c->opt.chi_div_floor;
  auto thr_ref = this->lohner_refine;
  auto thr_der = this->lohner_derefine;
  auto eps     = this->lohner_eps;
  const Real delta = 1.0e-99;

  // monitored field on all cells, including ghost cells
  DvceArray4D<Real> q("lohner_q", nmb, n3, n2, n1);
  par_for("Z4c_AMR::LohnerQ", DevExeSpace(), 0, nmb-1, 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    q(m,k,j,i) = u0(m,I_Z4C_ALPHA,k,j,i)
                 *pow(fmax(u0(m,I_Z4C_CHI,k,j,i), chi_floor), expo);
  });

  par_for_outer(
    "Z4c_AMR::Lohner", DevExeSpace(), 0, 0, 0, (nmb - 1),
    KOKKOS_LAMBDA(TeamMember_t tmember, const int m) {
      Real team_emax;
      Kokkos::parallel_reduce(
        Kokkos::TeamThreadRange(tmember, nkji),
        [=](const int idx, Real &emax) {
          int k = (idx) / nji;
          int j = (idx - k * nji) / nx1;
          int i = (idx - k * nji - j * nx1) + is;
          j += js;
          k += ks;
          const int c[3] = {i, j, k};
          Real num = 0.0, den = 0.0;
          for (int a = 0; a < 3; ++a) {
            for (int b = 0; b < 3; ++b) {
              int p[3], o[3];
              // D_a q at i + e_b and at i - e_b
              Real dq[2];
              for (int sgn = 0; sgn < 2; ++sgn) {
                p[0] = c[0]; p[1] = c[1]; p[2] = c[2];
                p[b] += (sgn == 0) ? 1 : -1;
                o[0] = p[0]; o[1] = p[1]; o[2] = p[2];
                p[a] += 1;
                o[a] -= 1;
                dq[sgn] = q(m,p[2],p[1],p[0]) - q(m,o[2],o[1],o[0]);
              }
              // amplitude scale
              Real sab = 0.0;
              for (int s1 = -1; s1 <= 1; s1 += 2) {
                for (int s2 = -1; s2 <= 1; s2 += 2) {
                  p[0] = c[0]; p[1] = c[1]; p[2] = c[2];
                  p[a] += s1;
                  p[b] += s2;
                  sab += fabs(q(m,p[2],p[1],p[0]));
                }
              }
              num += SQR(dq[0] - dq[1]);
              den += SQR(fabs(dq[0]) + fabs(dq[1]) + eps*sab + delta);
            }
          }
          emax = fmax(sqrt(num/den), emax);
        },
        Kokkos::Max<Real>(team_emax));

      if (team_emax > thr_ref) {
        refine_flag.d_view(m + mbs) = 1;
      }
      if (team_emax < thr_der) {
        refine_flag.d_view(m + mbs) = -1;
      }
    });

  // sync host and device
  refine_flag.template modify<DevExeSpace>();
  refine_flag.template sync<HostMemSpace>();
}

// Enforce some minimum resolution within a certain spherical region
void Z4c_AMR::RefineRadii(MeshBlockPack *pmbp) {
  Mesh *pmesh       = pmbp->pmesh;
  auto &refine_flag = pmesh->pmr->refine_flag;
  auto &size        = pmbp->pmb->mb_size;
  int nmb           = pmbp->nmb_thispack;
  int mbs           = pmesh->gids_eachrank[global_variable::my_rank];

  for (int m = 0; m < nmb; ++m) {
    // current refinement level
    int level = pmesh->lloc_eachmb[m + mbs].level - pmesh->root_level;

    // extract MeshBlock bounds
    Real &x1min = size.h_view(m).x1min;
    Real &x1max = size.h_view(m).x1max;
    Real &x2min = size.h_view(m).x2min;
    Real &x2max = size.h_view(m).x2max;
    Real &x3min = size.h_view(m).x3min;
    Real &x3max = size.h_view(m).x3max;

    Real r2[8] = {
      SQ(x1min) + SQ(x2min) + SQ(x3min),
      SQ(x1max) + SQ(x2min) + SQ(x3min),
      SQ(x1min) + SQ(x2max) + SQ(x3min),
      SQ(x1max) + SQ(x2max) + SQ(x3min),
      SQ(x1min) + SQ(x2min) + SQ(x3max),
      SQ(x1max) + SQ(x2min) + SQ(x3max),
      SQ(x1min) + SQ(x2max) + SQ(x3max),
      SQ(x1max) + SQ(x2max) + SQ(x3max),
    };
    Real rmin2 = *std::min_element(&r2[0], &r2[8]);

    for (size_t ir = 0; ir < radius.size(); ++ir) {
      if (rmin2 < SQ(radius[ir])) {
        if (level < reflevel[ir]) {
          refine_flag.h_view(m + mbs) = 1;
        } else if (level == reflevel[ir] && refine_flag.h_view(m + mbs) == -1) {
          refine_flag.h_view(m + mbs) = 0;
        }
      }
    }
  }

  // sync host and device
  refine_flag.template modify<HostMemSpace>();
  refine_flag.template sync<DevExeSpace>();
}

} // namespace z4c
