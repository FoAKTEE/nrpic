//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file scalar_field_diag.cpp
//! \brief Constraint magnitudes of arXiv:2512.14649 (appendix "Convergence", eq.
//! abscons), their record <basename>.sf.con.hst, and the extended double-precision dump.
//!
//! Magnitudes: the sums of the absolute values of the terms of the constraints in their
//! BSSN form, in the units of the code (2/Mpl^2 = 16 pi, 1/Mpl^2 = 8 pi):
//!   [H]   = |R| + |(2/3) K^2| + |At_ij At^ij| + |16 pi E|
//!   [M_i] = |gt^kl Dt_k At_il| + |(3/2) gt^kl At_ik d_l chi/chi| + |(2/3) d_i K|
//!           + |8 pi S_i|
//!   [M]   = sqrt(sum_i [M_i]^2)
//! with Dt the covariant derivative of the conformal metric,
//!   gt^kl Dt_k At_il = gt^kl (d_k At_il - Gt^m_ki At_ml - Gt^m_kl At_im),
//! K = Khat + 2 Theta, and R recovered from the Hamiltonian constraint of
//! Z4c::ADMConstraints, H = R + (2/3) K^2 - At_ij At^ij - 16 pi E.  The momentum
//! constraint in these terms is
//!   M_i = gt^kl Dt_k At_il - (3/2) gt^kl At_ik d_l chi/chi - (2/3) d_i K - 8 pi S_i
//! (covariant components; chi_psi_power = -4), which is kept next to the M_i of
//! Z4c::ADMConstraints as a check of this file: the two are discretisations of the same
//! expression.  |M| = sqrt(sum_i M_i^2) with the M_i of Z4c::ADMConstraints.  Where
//! [M] = 0 (a homogeneous state) the ratio |M|/[M] is set to 0.
//! The sources are those the constraints were evaluated with (Tmunu::tmunu_tot when the
//! field is coupled).
//!
//! <basename>.sf.con.hst (text, every <scalar_field> con_dcycle cycles): see the header
//! line written by WriteConstraintHistory.  With <scalar_field> con_signed = true seven
//! columns follow (ConstraintSignedMeans): the signed box means <H>, <M_x>, <M_y>, <M_z>,
//! and with H' = H - <H> (the part that is not uniform) <|H'|/[H]>, max(|H'|/[H]),
//! rms(H').  Without the option the record is unchanged.
//!
//! Extended dump <basename>.sf.NNNNN.dump (written instead of the layout NRSFDMP1 of
//! scalar_field_io.cpp when one of dump_metric, dump_magnitudes, dump_constraints,
//! dump_noise is set away from its default):
//!   8 bytes "NRSFDMP2"; int64 nmb, nx1, nx2, nx3, nvar, cycle, nnoise; double time;
//!   nvar names of 16 bytes each (padded with zeros); then per MeshBlock as in NRSFDMP1:
//!   int64 level, lx1, lx2, lx3; double x1min, x1max, x2min, x2max, x3min, x3max; nvar
//!   arrays of nx3*nx2*nx1 doubles (first index fastest).  Variables: phi, Pi, chi, K,
//!   alpha; H, Mx, My, Mz, E (dump_constraints); gxx, gxy, gxz, gyy, gyz, gzz, Axx, Axy,
//!   Axz, Ayy, Ayz, Azz of the conformal metric and the conformal trace-free extrinsic
//!   curvature (dump_metric); Hmag, Mmag, MBx, MBy, MBz (dump_magnitudes: [H], [M] and
//!   the M_i of the BSSN form); noise0, ... (dump_noise).

#include <algorithm>
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
#include "coordinates/adm.hpp"
#include "z4c/z4c.hpp"
#include "z4c/tmunu.hpp"
#include "scalar_field/scalar_field.hpp"

namespace scalarfield {

namespace {
void DiagFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in scalar_field_diag.cpp" << std::endl << msg
            << std::endl;
  std::exit(EXIT_FAILURE);
}
} // namespace

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::DiagInit
//! \brief options of this file; a parameter is read only if the input has it

void ScalarField::DiagInit(ParameterInput *pin) {
  if (pin->DoesParameterExist("scalar_field", "con_dcycle")) {
    dopt.con_dcycle = pin->GetInteger("scalar_field", "con_dcycle");
  }
  if (pin->DoesParameterExist("scalar_field", "dump_metric")) {
    dopt.dump_metric = pin->GetBoolean("scalar_field", "dump_metric");
  }
  if (pin->DoesParameterExist("scalar_field", "dump_magnitudes")) {
    dopt.dump_magnitudes = pin->GetBoolean("scalar_field", "dump_magnitudes");
  }
  if (pin->DoesParameterExist("scalar_field", "dump_constraints")) {
    dopt.dump_constraints = pin->GetBoolean("scalar_field", "dump_constraints");
  }
  if (pin->DoesParameterExist("scalar_field", "dump_noise")) {
    dopt.dump_noise = pin->GetBoolean("scalar_field", "dump_noise");
  }
  if (pin->DoesParameterExist("scalar_field", "con_signed")) {
    dopt.con_signed = pin->GetBoolean("scalar_field", "con_signed");
  }
  if (pmy_pack->pz4c->opt.chi_psi_power != -4.0 &&
      (dopt.con_dcycle > 0 || dopt.dump_magnitudes)) {
    DiagFatal("the constraint magnitudes are written for <z4c> chi_psi_power = -4");
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::ConstraintMagnitudesT
//! \brief [H], [M] and the M_i of the BSSN form on the active cells, from the Z4c state
//! (ghost cells set), the constraints of the last evaluation and its sources

template <int NGHOST>
void ScalarField::ConstraintMagnitudesT() {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  auto &size = pmy_pack->pmb->mb_size;
  int &is = indcs.is; int &ie = indcs.ie;
  int &js = indcs.js; int &je = indcs.je;
  int &ks = indcs.ks; int &ke = indcs.ke;
  int nmb = pmy_pack->nmb_thispack;
  if (!mag_alloc) {
    Kokkos::realloc(u_mag, nmb, 5, indcs.nx3 + 2*indcs.ng, indcs.nx2 + 2*indcs.ng,
                    indcs.nx1 + 2*indcs.ng);
    mag_alloc = true;
  }

  auto &z4c = pmy_pack->pz4c->z4c;
  auto &con = pmy_pack->pz4c->con;
  Tmunu *ptm = pmy_pack->ptmunu;
  const bool has_t = (ptm != nullptr);
  Tmunu::Tmunu_vars tm;
  if (has_t) { tm = ptm->use_total ? ptm->tmunu_tot : ptm->tmunu; }
  auto mag = u_mag;

  par_for("sf con magnitudes",DevExeSpace(),0,nmb-1,ks,ke,js,je,is,ie,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> dchi_d;    // chi 1st drvts
    AthenaPointTensor<Real, TensorSymm::NONE, 3, 1> dK_d;      // K 1st drvts
    AthenaPointTensor<Real, TensorSymm::SYM2, 3, 2> g_uu;      // inverse of conf. metric
    AthenaPointTensor<Real, TensorSymm::SYM2, 3, 3> dg_ddd;    // metric 1st drvts
    AthenaPointTensor<Real, TensorSymm::SYM2, 3, 3> dA_ddd;    // At 1st drvts
    AthenaPointTensor<Real, TensorSymm::SYM2, 3, 3> Gamma_ddd; // Christoffel 1st kind
    AthenaPointTensor<Real, TensorSymm::SYM2, 3, 3> Gamma_udd; // Christoffel 2nd kind

    Real idx[] = {1/size.d_view(m).dx1, 1/size.d_view(m).dx2, 1/size.d_view(m).dx3};

    for(int a = 0; a < 3; ++a) {
      dchi_d(a) = Dx<NGHOST>(a, idx, z4c.chi, m,k,j,i);
      dK_d(a) = Dx<NGHOST>(a, idx, z4c.vKhat, m,k,j,i)
              + 2.0*Dx<NGHOST>(a, idx, z4c.vTheta, m,k,j,i);
    }
    for(int a = 0; a < 3; ++a)
    for(int b = a; b < 3; ++b)
    for(int c = 0; c < 3; ++c) {
      dg_ddd(c,a,b) = Dx<NGHOST>(c, idx, z4c.g_dd, m,a,b,k,j,i);
      dA_ddd(c,a,b) = Dx<NGHOST>(c, idx, z4c.vA_dd, m,a,b,k,j,i);
    }

    const Real detg = adm::SpatialDet(z4c.g_dd(m,0,0,k,j,i), z4c.g_dd(m,0,1,k,j,i),
                                      z4c.g_dd(m,0,2,k,j,i), z4c.g_dd(m,1,1,k,j,i),
                                      z4c.g_dd(m,1,2,k,j,i), z4c.g_dd(m,2,2,k,j,i));
    adm::SpatialInv(1.0/detg,
               z4c.g_dd(m,0,0,k,j,i), z4c.g_dd(m,0,1,k,j,i), z4c.g_dd(m,0,2,k,j,i),
               z4c.g_dd(m,1,1,k,j,i), z4c.g_dd(m,1,2,k,j,i), z4c.g_dd(m,2,2,k,j,i),
               &g_uu(0,0), &g_uu(0,1), &g_uu(0,2),
               &g_uu(1,1), &g_uu(1,2), &g_uu(2,2));
    for(int c = 0; c < 3; ++c)
    for(int a = 0; a < 3; ++a)
    for(int b = a; b < 3; ++b) {
      Gamma_ddd(c,a,b) = 0.5*(dg_ddd(a,b,c) + dg_ddd(b,a,c) - dg_ddd(c,a,b));
    }
    for(int c = 0; c < 3; ++c)
    for(int a = 0; a < 3; ++a)
    for(int b = a; b < 3; ++b) {
      Gamma_udd(c,a,b) = 0.0;
      for(int d = 0; d < 3; ++d) {
        Gamma_udd(c,a,b) += g_uu(c,d)*Gamma_ddd(d,a,b);
      }
    }

    // At_ij At^ij with the conformal metric
    Real aa = 0.0;
    for(int a = 0; a < 3; ++a)
    for(int b = 0; b < 3; ++b)
    for(int c = 0; c < 3; ++c)
    for(int d = 0; d < 3; ++d) {
      aa += g_uu(a,c)*g_uu(b,d)*z4c.vA_dd(m,a,b,k,j,i)*z4c.vA_dd(m,c,d,k,j,i);
    }

    // Hamiltonian constraint: the Ricci scalar from the constraint and its other terms
    const Real trk = z4c.vKhat(m,k,j,i) + 2.0*z4c.vTheta(m,k,j,i);
    const Real k23 = (2.0/3.0)*trk*trk;
    const Real en = has_t ? tm.E(m,k,j,i) : 0.0;
    const Real ricci = con.H(m,k,j,i) - k23 + aa + 16.0*M_PI*en;
    mag(m,0,k,j,i) = fabs(ricci) + k23 + fabs(aa) + 16.0*M_PI*fabs(en);

    // momentum constraint, component by component
    const Real ochi = 1.0/z4c.chi(m,k,j,i);
    Real msum = 0.0;
    for(int a = 0; a < 3; ++a) {
      Real t1 = 0.0, t2 = 0.0;
      for(int c = 0; c < 3; ++c)
      for(int d = 0; d < 3; ++d) {
        Real da = dA_ddd(c,a,d);
        for(int e = 0; e < 3; ++e) {
          da -= Gamma_udd(e,c,a)*z4c.vA_dd(m,e,d,k,j,i)
              + Gamma_udd(e,c,d)*z4c.vA_dd(m,a,e,k,j,i);
        }
        t1 += g_uu(c,d)*da;
        t2 -= 1.5*g_uu(c,d)*z4c.vA_dd(m,a,c,k,j,i)*dchi_d(d)*ochi;
      }
      const Real t3 = (2.0/3.0)*dK_d(a);
      const Real t4 = has_t ? 8.0*M_PI*tm.S_d(m,a,k,j,i) : 0.0;
      const Real ma = fabs(t1) + fabs(t2) + fabs(t3) + fabs(t4);
      msum += ma*ma;
      mag(m,2+a,k,j,i) = t1 + t2 - t3 - t4;
    }
    mag(m,1,k,j,i) = sqrt(msum);
  });
}

void ScalarField::ConstraintMagnitudes() {
  switch (pmy_pack->pmesh->mb_indcs.ng) {
    case 2: ConstraintMagnitudesT<2>(); break;
    case 3: ConstraintMagnitudesT<3>(); break;
    case 4: ConstraintMagnitudesT<4>(); break;
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::WriteConstraintHistory
//! \brief one record of <basename>.sf.con.hst: box statistics (coordinate-volume
//! weights) of the constraints of the last evaluation relative to their magnitudes

void ScalarField::WriteConstraintHistory(Real time, int ncycle, bool header) {
  ConstraintMagnitudes();
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  auto &size = pmy_pack->pmb->mb_size;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmkji = (pmy_pack->nmb_thispack)*nx3*nx2*nx1;
  const int nkji = nx3*nx2*nx1;
  const int nji = nx2*nx1;
  Real mean[8];
  MeshMeans(mean);

  auto ucon = pmy_pack->pz4c->u_con;
  auto mag = u_mag;
  const int icH = z4c::Z4c::I_CON_H, icMx = z4c::Z4c::I_CON_MX;
  array_sum::GlobalSum sum;
  Real rhmax = 0.0, rmmax = 0.0;
  Kokkos::parallel_reduce("sf_con_hist", Kokkos::RangePolicy<>(DevExeSpace(), 0, nmkji),
  KOKKOS_LAMBDA(const int &idx, array_sum::GlobalSum &lsum, Real &lhmax, Real &lmmax) {
    int m = (idx)/nkji;
    int k = (idx - m*nkji)/nji;
    int j = (idx - m*nkji - k*nji)/nx1;
    int i = (idx - m*nkji - k*nji - j*nx1) + is;
    k += ks;
    j += js;
    const Real vol = size.d_view(m).dx1*size.d_view(m).dx2*size.d_view(m).dx3;
    const Real ham = fabs(ucon(m,icH,k,j,i));
    Real mom2 = 0.0, dif2 = 0.0;
    for (int a=0; a<3; ++a) {
      const Real ma = ucon(m,icMx+a,k,j,i);
      const Real d = mag(m,2+a,k,j,i) - ma;
      mom2 += ma*ma;
      dif2 += d*d;
    }
    const Real mom = sqrt(mom2);
    const Real hmag = mag(m,0,k,j,i), mmag = mag(m,1,k,j,i);
    const Real rh = (hmag > 0.0) ? ham/hmag : 0.0;
    const Real rm = (mmag > 0.0) ? mom/mmag : 0.0;
    array_sum::GlobalSum v;
    v.the_array[0] = vol*rh;
    v.the_array[1] = vol*rm;
    v.the_array[2] = vol*hmag;
    v.the_array[3] = vol*mmag;
    v.the_array[4] = vol*ham;
    v.the_array[5] = vol*mom;
    v.the_array[6] = vol*ham*ham;
    v.the_array[7] = vol*mom2;
    v.the_array[8] = vol*dif2;
    for (int n=9; n<NREDUCTION_VARIABLES; ++n) { v.the_array[n] = 0.0; }
    lsum += v;
    lhmax = fmax(lhmax, rh);
    lmmax = fmax(lmmax, rm);
  }, Kokkos::Sum<array_sum::GlobalSum>(sum), Kokkos::Max<Real>(rhmax),
     Kokkos::Max<Real>(rmmax));
  const Real vol = mean[7];
  const Real *s = sum.the_array;

  const std::string fname = basename + ".sf.con.hst";
  std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
  if (fp == nullptr) { DiagFatal("cannot open " + fname); }
  if (header) {
    std::fprintf(fp, "# scalar field, constraints relative to their magnitudes [H], [M] "
                 "(arXiv:2512.14649 eq. abscons): box means with coordinate-volume "
                 "weights\n");
    std::fprintf(fp, "# [1]=time [2]=cycle [3]=efolds=-ln<chi>/2 [4]=<|H|/[H]> "
                 "[5]=max(|H|/[H]) [6]=<|H|>/<[H]> [7]=<|M|/[M]> [8]=max(|M|/[M]) "
                 "[9]=<|M|>/<[M]> [10]=<[H]> [11]=<[M]> [12]=<|H|> [13]=<|M|> "
                 "[14]=rms(H) [15]=rms|M| [16]=rms|M_bssn-M_adm| [17]=<phi> [18]=<Pi> "
                 "[19]=<K> [20]=<alpha>");
    if (dopt.con_signed) {
      std::fprintf(fp, " [21]=<H> [22]=<M_x> [23]=<M_y> [24]=<M_z> [25]=<|H-<H>|/[H]> "
                   "[26]=max(|H-<H>|/[H]) [27]=rms(H-<H>)");
    }
    std::fprintf(fp, "\n");
  }
  std::fprintf(fp, "%.17e %d %.17e %.17e %.17e %.17e %.17e %.17e %.17e %.17e %.17e %.17e"
               " %.17e %.17e %.17e %.17e %.17e %.17e %.17e %.17e",
               time, ncycle, -0.5*std::log(mean[3]), s[0]/vol, rhmax,
               (s[2] > 0.0) ? s[4]/s[2] : 0.0, s[1]/vol, rmmax,
               (s[3] > 0.0) ? s[5]/s[3] : 0.0, s[2]/vol, s[3]/vol, s[4]/vol, s[5]/vol,
               std::sqrt(s[6]/vol), std::sqrt(s[7]/vol), std::sqrt(s[8]/vol),
               mean[0], mean[1], mean[2], mean[4]);
  if (dopt.con_signed) {
    Real sg[7];
    ConstraintSignedMeans(sg);
    std::fprintf(fp, " %.17e %.17e %.17e %.17e %.17e %.17e %.17e", sg[0], sg[1], sg[2],
                 sg[3], sg[4], sg[5], sg[6]);
  }
  std::fprintf(fp, "\n");
  std::fclose(fp);
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::ConstraintSignedMeans
//! \brief signed box means (coordinate-volume weights) of the constraints of the last
//! evaluation, out[0..3] = <H>, <M_x>, <M_y>, <M_z>, and of the part of H that is not
//! uniform, H' = H - <H>: out[4] = <|H'|/[H]>, out[5] = max(|H'|/[H]), out[6] = rms(H').
//! A uniform residual of the background (the time integration of a homogeneous state)
//! sits in <H> and drops out of H'.  Needs the magnitudes of ConstraintMagnitudes.

void ScalarField::ConstraintSignedMeans(Real out[7]) {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  auto &size = pmy_pack->pmb->mb_size;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmkji = (pmy_pack->nmb_thispack)*nx3*nx2*nx1;
  const int nkji = nx3*nx2*nx1;
  const int nji = nx2*nx1;
  auto ucon = pmy_pack->pz4c->u_con;
  auto mag = u_mag;
  const int icH = z4c::Z4c::I_CON_H, icMx = z4c::Z4c::I_CON_MX;

  // first pass: signed means
  array_sum::GlobalSum s1;
  Kokkos::parallel_reduce("sf_con_signed", Kokkos::RangePolicy<>(DevExeSpace(), 0, nmkji),
  KOKKOS_LAMBDA(const int &idx, array_sum::GlobalSum &lsum) {
    int m = (idx)/nkji;
    int k = (idx - m*nkji)/nji;
    int j = (idx - m*nkji - k*nji)/nx1;
    int i = (idx - m*nkji - k*nji - j*nx1) + is;
    k += ks;
    j += js;
    const Real vol = size.d_view(m).dx1*size.d_view(m).dx2*size.d_view(m).dx3;
    array_sum::GlobalSum v;
    v.the_array[0] = vol;
    v.the_array[1] = vol*ucon(m,icH,k,j,i);
    for (int a=0; a<3; ++a) { v.the_array[2+a] = vol*ucon(m,icMx+a,k,j,i); }
    for (int n=5; n<NREDUCTION_VARIABLES; ++n) { v.the_array[n] = 0.0; }
    lsum += v;
  }, Kokkos::Sum<array_sum::GlobalSum>(s1));
  const Real vtot = s1.the_array[0];
  const Real hbar = s1.the_array[1]/vtot;

  // second pass: the part of H that is not uniform
  array_sum::GlobalSum s2;
  Real rmax = 0.0;
  Kokkos::parallel_reduce("sf_con_spread", Kokkos::RangePolicy<>(DevExeSpace(), 0, nmkji),
  KOKKOS_LAMBDA(const int &idx, array_sum::GlobalSum &lsum, Real &lmax) {
    int m = (idx)/nkji;
    int k = (idx - m*nkji)/nji;
    int j = (idx - m*nkji - k*nji)/nx1;
    int i = (idx - m*nkji - k*nji - j*nx1) + is;
    k += ks;
    j += js;
    const Real vol = size.d_view(m).dx1*size.d_view(m).dx2*size.d_view(m).dx3;
    const Real hp = ucon(m,icH,k,j,i) - hbar;
    const Real hmag = mag(m,0,k,j,i);
    const Real r = (hmag > 0.0) ? fabs(hp)/hmag : 0.0;
    array_sum::GlobalSum v;
    v.the_array[0] = vol*r;
    v.the_array[1] = vol*hp*hp;
    for (int n=2; n<NREDUCTION_VARIABLES; ++n) { v.the_array[n] = 0.0; }
    lsum += v;
    lmax = fmax(lmax, r);
  }, Kokkos::Sum<array_sum::GlobalSum>(s2), Kokkos::Max<Real>(rmax));
  out[0] = hbar;
  for (int a=0; a<3; ++a) { out[1+a] = s1.the_array[2+a]/vtot; }
  out[4] = s2.the_array[0]/vtot;
  out[5] = rmax;
  out[6] = std::sqrt(s2.the_array[1]/vtot);
}

//----------------------------------------------------------------------------------------
//! \fn bool ScalarField::DumpIsExtended
//! \brief true when the dump options ask for a variable set other than that of NRSFDMP1

bool ScalarField::DumpIsExtended() const {
  return dopt.dump_metric || dopt.dump_magnitudes || !dopt.dump_constraints
         || !dopt.dump_noise;
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::WriteDumpExtended
//! \brief the fields of the active cells in double precision, layout NRSFDMP2 (format:
//! top of this file)

void ScalarField::WriteDumpExtended(Real time) {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmb = pmy_pack->nmb_thispack;
  const int cycle = (time > pm->time) ? pm->ncycle + 1 : pm->ncycle;
  const int nnoise = (noise_ready && dopt.dump_noise) ? nfld : 0;
  if (dopt.dump_magnitudes) { ConstraintMagnitudes(); }

  // variables: (source, index); sources 0 field, 1 Z4c state, 2 K, 3 constraints,
  // 4 energy density, 5 magnitudes, 6 stochastic fields
  std::vector<std::string> names;
  std::vector<int> src, ind;
  auto add = [&](const char *name, const int s, const int n) {
    names.push_back(name); src.push_back(s); ind.push_back(n);
  };
  add("phi", 0, I_SF_PHI);
  add("Pi", 0, I_SF_PI);
  add("chi", 1, z4c::Z4c::I_Z4C_CHI);
  add("K", 2, 0);
  add("alpha", 1, z4c::Z4c::I_Z4C_ALPHA);
  if (dopt.dump_constraints) {
    add("H", 3, z4c::Z4c::I_CON_H);
    add("Mx", 3, z4c::Z4c::I_CON_MX);
    add("My", 3, z4c::Z4c::I_CON_MY);
    add("Mz", 3, z4c::Z4c::I_CON_MZ);
    add("E", 4, 0);
  }
  if (dopt.dump_metric) {
    const char *gn[6] = {"gxx", "gxy", "gxz", "gyy", "gyz", "gzz"};
    const char *an[6] = {"Axx", "Axy", "Axz", "Ayy", "Ayz", "Azz"};
    for (int n=0; n<6; ++n) { add(gn[n], 1, z4c::Z4c::I_Z4C_GXX + n); }
    for (int n=0; n<6; ++n) { add(an[n], 1, z4c::Z4c::I_Z4C_AXX + n); }
  }
  if (dopt.dump_magnitudes) {
    add("Hmag", 5, 0);
    add("Mmag", 5, 1);
    add("MBx", 5, 2);
    add("MBy", 5, 3);
    add("MBz", 5, 4);
  }
  for (int n=0; n<nnoise; ++n) {
    const std::string nm = "noise" + std::to_string(n);
    add(nm.c_str(), 6, n);
  }
  const int nvar = static_cast<int>(names.size());

  auto hu = Kokkos::create_mirror_view(u0);
  Kokkos::deep_copy(hu, u0);
  auto hz = Kokkos::create_mirror_view(pmy_pack->pz4c->u0);
  Kokkos::deep_copy(hz, pmy_pack->pz4c->u0);
  auto hc = Kokkos::create_mirror_view(pmy_pack->pz4c->u_con);
  if (dopt.dump_constraints) { Kokkos::deep_copy(hc, pmy_pack->pz4c->u_con); }
  Tmunu *ptm = pmy_pack->ptmunu;
  const bool has_e = (ptm != nullptr) && dopt.dump_constraints;
  DvceArray5D<Real> utm;
  if (has_e) { utm = ptm->use_total ? ptm->u_tmunu_tot : ptm->u_tmunu; }
  auto ht = Kokkos::create_mirror_view(utm);
  if (has_e) { Kokkos::deep_copy(ht, utm); }
  auto hn = Kokkos::create_mirror_view(u_noise);
  if (nnoise > 0) { Kokkos::deep_copy(hn, u_noise); }
  auto hm = Kokkos::create_mirror_view(u_mag);
  if (dopt.dump_magnitudes) { Kokkos::deep_copy(hm, u_mag); }
  auto &size = pmy_pack->pmb->mb_size;

  char fname[512];
  std::snprintf(fname, sizeof(fname), "%s.sf.%05d.dump", basename.c_str(), dump_number);
  std::FILE *fp = std::fopen(fname, "wb");
  if (fp == nullptr) { DiagFatal(std::string("cannot open ") + fname); }
  const char magic[8] = {'N', 'R', 'S', 'F', 'D', 'M', 'P', '2'};
  std::fwrite(magic, 1, 8, fp);
  const std::int64_t head[7] = {nmb, nx1, nx2, nx3, nvar, cycle, nnoise};
  std::fwrite(head, sizeof(std::int64_t), 7, fp);
  const double t = time;
  std::fwrite(&t, sizeof(double), 1, fp);
  for (int v=0; v<nvar; ++v) {
    char nm[16];
    std::memset(nm, 0, sizeof(nm));
    std::strncpy(nm, names[v].c_str(), sizeof(nm) - 1);
    std::fwrite(nm, 1, sizeof(nm), fp);
  }
  const int ikh = z4c::Z4c::I_Z4C_KHAT, ith = z4c::Z4c::I_Z4C_THETA;
  std::vector<double> buf(static_cast<std::size_t>(nx1)*nx2*nx3);
  for (int m=0; m<nmb; ++m) {
    const LogicalLocation &ll = pm->lloc_eachmb[pmy_pack->gids + m];
    const std::int64_t loc[4] = {ll.level - pm->root_level, ll.lx1, ll.lx2, ll.lx3};
    std::fwrite(loc, sizeof(std::int64_t), 4, fp);
    const double ext[6] = {size.h_view(m).x1min, size.h_view(m).x1max,
                           size.h_view(m).x2min, size.h_view(m).x2max,
                           size.h_view(m).x3min, size.h_view(m).x3max};
    std::fwrite(ext, sizeof(double), 6, fp);
    for (int v=0; v<nvar; ++v) {
      const int n = ind[v];
      std::size_t c = 0;
      for (int k=ks; k<ks+nx3; ++k) {
        for (int j=js; j<js+nx2; ++j) {
          for (int i=is; i<is+nx1; ++i) {
            double val = 0.0;
            switch (src[v]) {
              case 0: val = hu(m,n,k,j,i); break;
              case 1: val = hz(m,n,k,j,i); break;
              case 2: val = hz(m,ikh,k,j,i) + 2.0*hz(m,ith,k,j,i); break;
              case 3: val = hc(m,n,k,j,i); break;
              case 4: val = has_e ? ht(m,Tmunu::I_Tmunu_E,k,j,i) : 0.0; break;
              case 5: val = hm(m,n,k,j,i); break;
              default: val = hn(m,n,k,j,i); break;
            }
            buf[c++] = val;
          }
        }
      }
      std::fwrite(buf.data(), sizeof(double), buf.size(), fp);
    }
  }
  std::fclose(fp);
  NoiseWriteState(time, dump_number, false);
  ++dump_number;
}

template void ScalarField::ConstraintMagnitudesT<2>();
template void ScalarField::ConstraintMagnitudesT<3>();
template void ScalarField::ConstraintMagnitudesT<4>();

} // namespace scalarfield
