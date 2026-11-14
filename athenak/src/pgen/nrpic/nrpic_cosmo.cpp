//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_cosmo.cpp
//! \brief Problem generator for cosmological initial data on a periodic, uniform mesh:
//!   gamma_ij = psi^4 delta_ij,
//!   K_ij     = psi^-2 Ahat_ij + (1/3) psi^4 delta_ij K,
//!   beta^i   = 0,
//! with the conformal factor psi, the trace K, the conformal traceless part Ahat_ij and
//! the lapse given per cell.  <problem> id selects where they come from:
//!   flrw   homogeneous flat universe: psi = 1, Ahat_ij = 0, K = -3 hubble, alpha = 1
//!   file   read from <problem> id_file (cosmo/ic writes it), a binary file with
//!            8 bytes "NRCOSMO1", 3 int64 (n1, n2, n3),
//!            9 arrays of n3*n2*n1 doubles, first index fastest:
//!            psi, K, alpha, Ahat_xx, Ahat_xy, Ahat_xz, Ahat_yy, Ahat_yz, Ahat_zz,
//!          given at the cell centres of the root mesh, which must have n1 x n2 x n3
//!          cells; on refined MeshBlocks the fields are interpolated (cubic)
//! The matter is carried by the particles of the nrpic module (<particles>
//! particle_file); its sources are deposited after this function returns.
//!
//! Robustness test of Daverio, Dirian & Mitsou (arXiv:1904.07841, Sec. IV A): with
//! <problem> noise_amp > 0 every evolved field receives white noise, drawn uniformly and
//! independently per cell and component from (-A, A):
//!   alpha, chi and K are multiplied by 1 + eps        (A = noise_amp),
//!   the conformal metric receives  + eps_ij           (A = noise_amp),
//!   Atilde_ij receives  + eps_ij                      (A = noise_atilde),
//!   Theta receives  + eps                             (A = noise_theta),
//!   Gamma^i receives  + eps^i                         (A = noise_gamma).
//! The last three default to noise_amp; they carry units and are set by the caller.

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
#include "coordinates/cell_locations.hpp"
#include "z4c/z4c.hpp"
#include "pgen/pgen.hpp"

namespace {

void CosmoFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_cosmo.cpp" << std::endl << msg << std::endl;
  std::exit(EXIT_FAILURE);
}

//! uniform deviate in (-1, 1) from the global index of a cell, the index of a field
//! component and a seed (splitmix64); the same in a ghost cell and in its periodic image
KOKKOS_INLINE_FUNCTION
Real CosmoNoise(const std::uint64_t cell, const std::uint64_t comp,
                const std::uint64_t seed) {
  std::uint64_t z = cell*0x9E3779B97F4A7C15ULL + comp*0xBF58476D1CE4E5B9ULL
                    + seed*0x94D049BB133111EBULL + 0x2545F4914F6CDD1DULL;
  z = (z ^ (z >> 30))*0xBF58476D1CE4E5B9ULL;
  z = (z ^ (z >> 27))*0x94D049BB133111EBULL;
  z = z ^ (z >> 31);
  // 53 random bits to [0, 1), then to (-1, 1)
  const Real u = static_cast<Real>(z >> 11)*(1.0/9007199254740992.0);
  return 2.0*u - 1.0;
}

} // namespace

//----------------------------------------------------------------------------------------
//! \fn void ProblemGenerator::NrpicCosmology
//! \brief initial data of an expanding periodic universe for the Z4c evolution

void ProblemGenerator::NrpicCosmology(ParameterInput *pin, const bool restart) {
  if (restart) return;

  MeshBlockPack *pmbp = pmy_mesh_->pmb_pack;
  auto &indcs = pmy_mesh_->mb_indcs;
  if (pmbp->pz4c == nullptr) {
    CosmoFatal("nrpic_cosmo requires a <z4c> block");
  }

  const std::string id = pin->GetOrAddString("problem", "id", "flrw");
  const Real hubble = pin->GetOrAddReal("problem", "hubble", 1.0);
  const bool from_file = (id.compare("file") == 0);
  if (!from_file && id.compare("flrw") != 0) {
    CosmoFatal("<problem> id = '" + id + "' not recognized (flrw or file)");
  }

  // mesh as a whole: the file holds one value per cell of the uniform mesh
  const int g1 = pmy_mesh_->mesh_indcs.nx1;
  const int g2 = pmy_mesh_->mesh_indcs.nx2;
  const int g3 = pmy_mesh_->mesh_indcs.nx3;
  const Real gx1 = pmy_mesh_->mesh_size.x1min;
  const Real gx2 = pmy_mesh_->mesh_size.x2min;
  const Real gx3 = pmy_mesh_->mesh_size.x3min;
  const Real gd1 = (pmy_mesh_->mesh_size.x1max - gx1)/static_cast<Real>(g1);
  const Real gd2 = (pmy_mesh_->mesh_size.x2max - gx2)/static_cast<Real>(g2);
  const Real gd3 = (pmy_mesh_->mesh_size.x3max - gx3)/static_cast<Real>(g3);

  const size_t ncell = static_cast<size_t>(g1)*g2*g3;
  DvceArray2D<Real> fld("cosmo_fld", 9, from_file ? ncell : 1);
  if (from_file) {
    const std::string fname = pin->GetString("problem", "id_file");
    std::FILE *fp = std::fopen(fname.c_str(), "rb");
    if (fp == nullptr) CosmoFatal("cannot open " + fname);
    char magic[9] = {0};
    std::int64_t n[3] = {0, 0, 0};
    if (std::fread(magic, 1, 8, fp) != 8 || std::strncmp(magic, "NRCOSMO1", 8) != 0) {
      CosmoFatal("bad magic in " + fname);
    }
    if (std::fread(n, sizeof(std::int64_t), 3, fp) != 3 || n[0] != g1 || n[1] != g2 ||
        n[2] != g3) {
      CosmoFatal("the fields in " + fname + " do not have the cell numbers of the mesh");
    }
    std::vector<double> buf(ncell);
    auto fh = Kokkos::create_mirror_view(fld);
    for (int v=0; v<9; ++v) {
      if (std::fread(buf.data(), sizeof(double), ncell, fp) != ncell) {
        CosmoFatal(fname + " is truncated");
      }
      for (size_t c=0; c<ncell; ++c) { fh(v,c) = buf[c]; }
    }
    std::fclose(fp);
    Kokkos::deep_copy(fld, fh);
  }

  // ---- ADM variables on all cells, including ghost cells (periodic images)
  auto &size = pmbp->pmb->mb_size;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ng = indcs.ng;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int n1 = nx1 + 2*ng, n2 = nx2 + 2*ng, n3 = nx3 + 2*ng;
  const int nmb = pmbp->nmb_thispack;
  auto &adm = pmbp->padm->adm;
  par_for("nrpic_cosmo", DevExeSpace(), 0, nmb-1, 0, n3-1, 0, n2-1, 0, n1-1,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    Real psi = 1.0, trk = -3.0*hubble, alp = 1.0;
    Real ah[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    if (from_file) {
      const Real x = CellCenterX(i-is, nx1, size.d_view(m).x1min, size.d_view(m).x1max);
      const Real y = CellCenterX(j-js, nx2, size.d_view(m).x2min, size.d_view(m).x2max);
      const Real z = CellCenterX(k-ks, nx3, size.d_view(m).x3min, size.d_view(m).x3max);
      // Position in units of the cells of the file, measured from the first cell
      // centre.  At a cell centre of the root mesh the value of the file is taken; on
      // refined MeshBlocks the fields are interpolated with cubic Lagrange polynomials
      // through the four nearest cell centres per direction (periodic).
      const Real xi = (x - gx1)/gd1 - 0.5;
      const Real yi = (y - gx2)/gd2 - 0.5;
      const Real zi = (z - gx3)/gd3 - 0.5;
      Real fx = floor(xi + 1.0e-9), fy = floor(yi + 1.0e-9), fz = floor(zi + 1.0e-9);
      const Real s[3] = {xi - fx, yi - fy, zi - fz};
      const int i0[3] = {static_cast<int>(fx), static_cast<int>(fy), static_cast<int>(fz)};
      const int gn[3] = {g1, g2, g3};
      Real val[9] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
      if (fabs(s[0]) < 1.0e-8 && fabs(s[1]) < 1.0e-8 && fabs(s[2]) < 1.0e-8) {
        const int ig = ((i0[0] % g1) + g1) % g1;
        const int jg = ((i0[1] % g2) + g2) % g2;
        const int kg = ((i0[2] % g3) + g3) % g3;
        const size_t c = (static_cast<size_t>(kg)*g2 + jg)*g1 + ig;
        for (int v=0; v<9; ++v) { val[v] = fld(v,c); }
      } else {
        Real w[3][4];
        int idx[3][4];
        for (int d=0; d<3; ++d) {
          const Real t = s[d];
          w[d][0] = -t*(t - 1.0)*(t - 2.0)/6.0;
          w[d][1] = (t + 1.0)*(t - 1.0)*(t - 2.0)/2.0;
          w[d][2] = -(t + 1.0)*t*(t - 2.0)/2.0;
          w[d][3] = (t + 1.0)*t*(t - 1.0)/6.0;
          for (int q=0; q<4; ++q) {
            idx[d][q] = (((i0[d] - 1 + q) % gn[d]) + gn[d]) % gn[d];
          }
        }
        for (int c3=0; c3<4; ++c3) {
          for (int c2=0; c2<4; ++c2) {
            for (int c1=0; c1<4; ++c1) {
              const size_t c = (static_cast<size_t>(idx[2][c3])*g2 + idx[1][c2])*g1
                               + idx[0][c1];
              const Real ww = w[0][c1]*w[1][c2]*w[2][c3];
              for (int v=0; v<9; ++v) { val[v] += ww*fld(v,c); }
            }
          }
        }
      }
      psi = val[0];
      trk = val[1];
      alp = val[2];
      for (int v=0; v<6; ++v) { ah[v] = val[3+v]; }
    }
    const Real psi2 = psi*psi;
    const Real psi4 = psi2*psi2;
    adm.psi4(m,k,j,i) = psi4;
    int v = 0;
    for (int a=0; a<3; ++a) {
      adm.beta_u(m,a,k,j,i) = 0.0;
      for (int b=a; b<3; ++b) {
        const Real dab = (a == b) ? 1.0 : 0.0;
        adm.g_dd(m,a,b,k,j,i) = psi4*dab;
        adm.vK_dd(m,a,b,k,j,i) = ah[v]/psi2 + psi4*dab*trk/3.0;
        ++v;
      }
    }
    adm.alpha(m,k,j,i) = alp;
  });

  // ---- Z4c variables and constraints (the matter sources are deposited later)
  switch (indcs.ng) {
    case 2: pmbp->pz4c->ADMToZ4c<2>(pmbp, pin); break;
    case 3: pmbp->pz4c->ADMToZ4c<3>(pmbp, pin); break;
    case 4: pmbp->pz4c->ADMToZ4c<4>(pmbp, pin); break;
  }
  // ---- white noise on the evolved fields
  const Real namp = pin->GetOrAddReal("problem", "noise_amp", 0.0);
  if (namp > 0.0) {
    const Real nat = pin->GetOrAddReal("problem", "noise_atilde", namp);
    const Real nth = pin->GetOrAddReal("problem", "noise_theta", namp);
    const Real ngm = pin->GetOrAddReal("problem", "noise_gamma", namp);
    const std::uint64_t seed = static_cast<std::uint64_t>(
        pin->GetOrAddInteger("problem", "noise_seed", 1));
    auto u0 = pmbp->pz4c->u0;
    const int ichi = z4c::Z4c::I_Z4C_CHI, igxx = z4c::Z4c::I_Z4C_GXX;
    const int ikh = z4c::Z4c::I_Z4C_KHAT, iaxx = z4c::Z4c::I_Z4C_AXX;
    const int igam = z4c::Z4c::I_Z4C_GAMX, ith = z4c::Z4c::I_Z4C_THETA;
    const int ial = z4c::Z4c::I_Z4C_ALPHA;
    par_for("nrpic_cosmo_noise", DevExeSpace(), 0, nmb-1, 0, n3-1, 0, n2-1, 0, n1-1,
    KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      const Real x = CellCenterX(i-is, nx1, size.d_view(m).x1min, size.d_view(m).x1max);
      const Real y = CellCenterX(j-js, nx2, size.d_view(m).x2min, size.d_view(m).x2max);
      const Real z = CellCenterX(k-ks, nx3, size.d_view(m).x3min, size.d_view(m).x3max);
      int ig = static_cast<int>(floor((x - gx1)/gd1));
      int jg = static_cast<int>(floor((y - gx2)/gd2));
      int kg = static_cast<int>(floor((z - gx3)/gd3));
      ig = ((ig % g1) + g1) % g1;
      jg = ((jg % g2) + g2) % g2;
      kg = ((kg % g3) + g3) % g3;
      const std::uint64_t c = (static_cast<std::uint64_t>(kg)*g2 + jg)*g1 + ig;
      u0(m,ial,k,j,i) *= 1.0 + namp*CosmoNoise(c, 0, seed);
      u0(m,ichi,k,j,i) *= 1.0 + namp*CosmoNoise(c, 1, seed);
      u0(m,ikh,k,j,i) *= 1.0 + namp*CosmoNoise(c, 2, seed);
      u0(m,ith,k,j,i) += nth*CosmoNoise(c, 3, seed);
      for (int a=0; a<3; ++a) {
        u0(m,igam+a,k,j,i) += ngm*CosmoNoise(c, 4+a, seed);
      }
      for (int a=0; a<6; ++a) {
        u0(m,igxx+a,k,j,i) += namp*CosmoNoise(c, 7+a, seed);
        u0(m,iaxx+a,k,j,i) += nat*CosmoNoise(c, 13+a, seed);
      }
    });
  }
  pmbp->pz4c->Z4cToADM(pmbp);
  switch (indcs.ng) {
    case 2: pmbp->pz4c->ADMConstraints<2>(pmbp); break;
    case 3: pmbp->pz4c->ADMConstraints<3>(pmbp); break;
    case 4: pmbp->pz4c->ADMConstraints<4>(pmbp); break;
  }
  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC: cosmological initial data, id = " << id << std::endl;
  }
  return;
}
