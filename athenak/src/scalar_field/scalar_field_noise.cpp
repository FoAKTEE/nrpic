//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file scalar_field_noise.cpp
//! \brief Stochastic sources of the scalar field in a periodic cubic box.
//!
//! A noise field is a real band-limited field
//!   xi(x) = sum_{n in H} 2 Re[ c_n exp(i k_n.(x - x0)) ],   k_n = 2 pi n / L,
//! over the wave vectors n of one hemisphere H (n_x > 0, or n_x = 0 and n_y > 0, or
//! n_x = n_y = 0 and n_z > 0) with 0 < |n|^2 <= nmax2; x0 is the lower corner of the
//! mesh.  The coefficient of a mode is
//!   c_n = (factor of its shell |n|^2) x alpha_n x (real factor of the field),
//! with one complex unit Gaussian alpha_n = (z1 + i z2)/sqrt(2) per mode and degree of
//! freedom, drawn with utils/rng.hpp:
//!   stream = Stream(kStreamStochastic, 2^16 + dof),
//!   entity = CellEntity(n_x + 2^20, n_y + 2^20, n_z + 2^20),  step = epoch,  draw 0
//! (the keys of tracks/E-stoch-inf/noise/ref/philox_ref.py).  The epoch is 0 for frozen
//! amplitudes and the cycle number reached at the end of the step for amplitudes that
//! are new in every step.  A draw depends on the wave vector, the epoch, the degree of
//! freedom and the seed of the run, and on nothing else.
//!
//! Synthesis: MeshBlock by MeshBlock, three one-dimensional sums (over n_z, n_y, n_x)
//! with tables of cos and sin of 2 pi n (g + 1/2)/N built from the global cell index g
//! on the level of the MeshBlock.  Every cell sums the same terms in the same order
//! whatever the division of the mesh, and a refined MeshBlock evaluates the same
//! function at its own cell centres.  No Fourier library is used.
//!
//! Models (<scalar_field> noise):
//!  power            prescribed amplitude and window (unit test of the generator, and the
//!                   generic hook): the field of a step is the increment
//!                     c_n = amp q^((tilt-3)/2) L^(-3/2) g(dW_q) alpha_n,   q = |n|,
//!                   dW_q the change over the step of the window W(k_sigma/k),
//!                   k_sigma/k_f = ksigma0 exp(hubble (t - t0)), k_f = 2 pi/L;
//!                   g = dW with frozen amplitudes (the sum over the steps is the
//!                   windowed field), g = sqrt(dW) with new amplitudes in every step
//!                   (white in time: independent increments of variance proportional
//!                   to dW).  Sources: c_phi xi_0/dt in d_t phi and c_pi xi_1/dt in
//!                   d_t Pi, held over the stages of the step, so that the step adds
//!                   exactly c_phi xi_0 and c_pi xi_1.
//!  mukhanov_sasaki  the sources of Launay, Rigopoulos & Shellard (arXiv:2512.14649) as
//!                   specified in tracks/E-stoch-inf/spec/SPEC.md (sections 2.1, 2.2, 3)
//!                   and codebase/DESIGN_REVIEW.md (section 5) of branch
//!                   track/E-stoch-inf: frozen alpha_n, complex mode functions R_q(t)
//!                   per shell with
//!                     d2R/dtau2 + (3 - eps2) H dR/dtau + (k/a)^2 R = 0,
//!                   S_R = R W'' + [2 R' + (3 - eps2) H R] W'  (primes: proper time of
//!                   the background), W = (1 + tanh[s ln(sigma a H/k)])/2, and the fields
//!                     I_R  = L^(-3/2) sum 2 Re[S_R alpha_n e^(ik.x)],
//!                     T_ij = the same with the factor qh_i qh_j/qh^2,
//!                   entering as  d_t Pi   += alpha_b (Pi_b/H) I_R,
//!                                d_t Khat += -alpha_b eps1 I_R,
//!                                d_t At_ij += alpha_b eps1 (delta_ij I_R/3 - T_ij),
//!                   eps1 = 4 pi Pi_b^2/H^2, eps2 = -dln eps1/dN = 6 + 2 V'/(H Pi_b)
//!                   - 2 eps1.  qh is the wave number of the centred first difference
//!                   of the mesh (projector = stencil) or n itself (continuum).  The
//!                   background (phi_b, Pi_b, a, H) is that of the Friedmann equations
//!                   integrated with the mode functions (level 0) or the box means of
//!                   the mesh (level 1); alpha_b is the box mean of the lapse.
//! The mode functions and the background are integrated on the host with the same
//! low-storage Runge-Kutta update as the fields, stage by stage, so that every stage
//! evaluates its sources with data of its own time.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "driver/driver.hpp"
#include "z4c/z4c.hpp"
#include "utils/rng.hpp"
#include "utils/rng_mesh.hpp"
#include "scalar_field/scalar_field.hpp"

namespace scalarfield {

namespace {
void NoiseFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in scalar_field_noise.cpp" << std::endl << msg
            << std::endl;
  std::exit(EXIT_FAILURE);
}

//! wave number times cell size of the centred first difference with ng ghost cells
//! (orders 2, 4, 6), D exp(i k x) = i (qh/h) exp(i k x)
Real StencilWaveNumber(const Real kh, const int ng) {
  if (ng == 2) {
    return std::sin(kh);
  } else if (ng == 3) {
    return (4.0/3.0)*std::sin(kh) - (1.0/6.0)*std::sin(2.0*kh);
  }
  return 1.5*std::sin(kh) - 0.3*std::sin(2.0*kh) + (1.0/30.0)*std::sin(3.0*kh);
}
} // namespace

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseInit
//! \brief options of the stochastic sources and the list of modes (constructor)

void ScalarField::NoiseInit(ParameterInput *pin) {
  Mesh *pm = pmy_pack->pmesh;
  const std::string model = pin->GetOrAddString("scalar_field", "noise", "none");
  if (model.compare("none") == 0) {
    nopt.on = false;
    return;
  } else if (model.compare("power") == 0) {
    nopt.model = kNoisePower;
  } else if (model.compare("mukhanov_sasaki") == 0) {
    nopt.model = kNoiseMS;
  } else {
    NoiseFatal("<scalar_field> noise = '" + model + "' not recognized (none, power, "
               "mukhanov_sasaki)");
  }
  nopt.on = true;
  nopt.seed = rng::RunSeed(pin);
  nopt.nmax2 = pin->GetInteger("scalar_field", "noise_nmax2");
  nopt.sharpness = pin->GetOrAddReal("scalar_field", "noise_sharpness", 5.0);
  {
    const std::string w = pin->GetOrAddString("scalar_field", "noise_window", "tanh");
    if (w.compare("tanh") == 0) {
      nopt.window = kWindowTanh;
    } else if (w.compare("heaviside") == 0) {
      nopt.window = kWindowHeaviside;
    } else {
      NoiseFatal("<scalar_field> noise_window must be tanh or heaviside");
    }
  }
  if (nopt.model == kNoisePower) {
    const std::string s = pin->GetOrAddString("scalar_field", "noise_scheme", "frozen");
    if (s.compare("frozen") == 0) {
      nopt.scheme = kNoiseFrozen;
    } else if (s.compare("markov") == 0) {
      nopt.scheme = kNoiseMarkov;
    } else {
      NoiseFatal("<scalar_field> noise_scheme must be frozen or markov");
    }
    nopt.amp = pin->GetOrAddReal("scalar_field", "noise_amp", 1.0);
    nopt.tilt = pin->GetOrAddReal("scalar_field", "noise_tilt", 0.0);
    nopt.ksigma0 = pin->GetOrAddReal("scalar_field", "noise_ksigma0", 1.0);
    nopt.hubble = pin->GetOrAddReal("scalar_field", "noise_hubble", 1.0);
    nopt.t0 = pin->GetOrAddReal("scalar_field", "noise_t0", 0.0);
    nopt.c_phi = pin->GetOrAddReal("scalar_field", "noise_c_phi", 0.0);
    nopt.c_pi = pin->GetOrAddReal("scalar_field", "noise_c_pi", 0.0);
    nopt.pi_dof = pin->GetOrAddInteger("scalar_field", "noise_pi_dof", 1);
    if (nopt.pi_dof != 0 && nopt.pi_dof != 1) {
      NoiseFatal("<scalar_field> noise_pi_dof must be 0 or 1");
    }
    nfld = 2;
  } else {
    nopt.scheme = kNoiseFrozen;
    nopt.sigma = pin->GetOrAddReal("scalar_field", "noise_sigma", 1.0);
    nopt.level = pin->GetOrAddInteger("scalar_field", "noise_level", 0);
    if (nopt.level != 0 && nopt.level != 1) {
      NoiseFatal("<scalar_field> noise_level must be 0 (Friedmann background) or 1 (box "
                 "means); level 2 of arXiv:2512.14649 is not implemented");
    }
    const std::string p = pin->GetOrAddString("scalar_field", "noise_projector",
                                              "stencil");
    if (p.compare("stencil") == 0) {
      nopt.projector = 0;
    } else if (p.compare("continuum") == 0) {
      nopt.projector = 1;
    } else {
      NoiseFatal("<scalar_field> noise_projector must be stencil or continuum");
    }
    nopt.kick_pi = pin->GetOrAddBoolean("scalar_field", "noise_kick_pi", true);
    nopt.kick_k = pin->GetOrAddBoolean("scalar_field", "noise_kick_k", true);
    nopt.kick_a = pin->GetOrAddBoolean("scalar_field", "noise_kick_a", true);
    nopt.pi_sign = pin->GetOrAddReal("scalar_field", "noise_pi_sign", 1.0);
    nopt.mode_file = pin->GetString("scalar_field", "noise_mode_file");
    if (nopt.window != kWindowTanh) {
      NoiseFatal("the Mukhanov-Sasaki sources need the derivatives of the window: "
                 "noise_window = tanh");
    }
    nfld = nopt.kick_a ? 6 : 1;
  }

  // ---- the box: periodic and cubic, cubic root mesh
  for (int f=0; f<6; ++f) {
    if (pm->mesh_bcs[f] != BoundaryFlag::periodic) {
      NoiseFatal("the stochastic sources need periodic boundaries in all directions");
    }
  }
  const Real l1 = pm->mesh_size.x1max - pm->mesh_size.x1min;
  const Real l2 = pm->mesh_size.x2max - pm->mesh_size.x2min;
  const Real l3 = pm->mesh_size.x3max - pm->mesh_size.x3min;
  const int ng1 = pm->mesh_indcs.nx1, ng2 = pm->mesh_indcs.nx2, ng3 = pm->mesh_indcs.nx3;
  if (std::fabs(l2 - l1) > 1.0e-12*l1 || std::fabs(l3 - l1) > 1.0e-12*l1 || ng2 != ng1
      || ng3 != ng1) {
    NoiseFatal("the stochastic sources need a cubic box with a cubic root mesh");
  }
  nmax = static_cast<int>(std::floor(std::sqrt(static_cast<double>(nopt.nmax2)) + 1e-9));
  if (nopt.nmax2 < 1 || 2*nmax >= ng1) {
    NoiseFatal("noise_nmax2 must be at least 1 and the cut must stay below the Nyquist "
               "wave number of the root mesh (2 n_max < N)");
  }

  // ---- modes of the hemisphere, ordered by n_x, then n_y, then n_z
  mode_n.clear();
  std::vector<int> h_pair_start, h_pair_ny, h_xval_start, h_xval_nx, h_mode_n2;
  for (int nx=0; nx<=nmax; ++nx) {
    bool new_x = true;
    for (int ny=-nmax; ny<=nmax; ++ny) {
      bool new_pair = true;
      for (int nz=-nmax; nz<=nmax; ++nz) {
        const int n2 = nx*nx + ny*ny + nz*nz;
        if (n2 < 1 || n2 > nopt.nmax2) continue;
        const bool hemi = (nx > 0) || (nx == 0 && ny > 0)
                          || (nx == 0 && ny == 0 && nz > 0);
        if (!hemi) continue;
        if (new_x) {
          h_xval_start.push_back(static_cast<int>(h_pair_ny.size()));
          h_xval_nx.push_back(nx);
          new_x = false;
        }
        if (new_pair) {
          h_pair_start.push_back(static_cast<int>(h_mode_n2.size()));
          h_pair_ny.push_back(ny);
          new_pair = false;
        }
        mode_n.push_back(nx); mode_n.push_back(ny); mode_n.push_back(nz);
        h_mode_n2.push_back(n2);
      }
    }
  }
  nmode = static_cast<int>(h_mode_n2.size());
  npair = static_cast<int>(h_pair_ny.size());
  nxval = static_cast<int>(h_xval_nx.size());
  h_pair_start.push_back(nmode);
  h_xval_start.push_back(npair);

  // shells: distinct |n|^2 in increasing order
  shell_n2 = h_mode_n2;
  std::sort(shell_n2.begin(), shell_n2.end());
  shell_n2.erase(std::unique(shell_n2.begin(), shell_n2.end()), shell_n2.end());
  nshell = static_cast<int>(shell_n2.size());
  std::map<int,int> shell_of;
  for (int s=0; s<nshell; ++s) { shell_of[shell_n2[s]] = s; }

  // ---- device copies
  Kokkos::realloc(mode_nz, nmode);
  Kokkos::realloc(mode_shell, nmode);
  Kokkos::realloc(pair_start, npair + 1);
  Kokkos::realloc(pair_ny, npair);
  Kokkos::realloc(xval_start, nxval + 1);
  Kokkos::realloc(xval_nx, nxval);
  const int ndof = (nopt.model == kNoisePower && nopt.pi_dof == 1) ? 2 : 1;
  Kokkos::realloc(alpha_re, ndof, nmode);
  Kokkos::realloc(alpha_im, ndof, nmode);
  Kokkos::realloc(proj, nfld, nmode);
  Kokkos::realloc(fld_dof, nfld);
  Kokkos::realloc(shell_re, nshell);
  Kokkos::realloc(shell_im, nshell);
  {
    auto h1 = Kokkos::create_mirror_view(mode_nz);
    auto h2 = Kokkos::create_mirror_view(mode_shell);
    for (int q=0; q<nmode; ++q) {
      h1(q) = mode_n[3*q+2];
      h2(q) = shell_of[h_mode_n2[q]];
    }
    Kokkos::deep_copy(mode_nz, h1);
    Kokkos::deep_copy(mode_shell, h2);
    auto h3 = Kokkos::create_mirror_view(pair_start);
    auto h4 = Kokkos::create_mirror_view(pair_ny);
    for (int p=0; p<=npair; ++p) { h3(p) = h_pair_start[p]; }
    for (int p=0; p<npair; ++p) { h4(p) = h_pair_ny[p]; }
    Kokkos::deep_copy(pair_start, h3);
    Kokkos::deep_copy(pair_ny, h4);
    // pairs of each n_x: h_xval_start counts pairs
    auto h5 = Kokkos::create_mirror_view(xval_start);
    auto h6 = Kokkos::create_mirror_view(xval_nx);
    for (int x=0; x<=nxval; ++x) { h5(x) = h_xval_start[x]; }
    for (int x=0; x<nxval; ++x) { h6(x) = h_xval_nx[x]; }
    Kokkos::deep_copy(xval_start, h5);
    Kokkos::deep_copy(xval_nx, h6);

    // real factor of every field: 1, or the trace-free projector components
    // (xx, xy, xz, yy, yz) built from the wave number of the first difference
    auto hp = Kokkos::create_mirror_view(proj);
    auto hd = Kokkos::create_mirror_view(fld_dof);
    const int ng = pm->mb_indcs.ng;
    for (int f=0; f<nfld; ++f) {
      hd(f) = (nopt.model == kNoisePower && f == 1) ? nopt.pi_dof : 0;
    }
    for (int q=0; q<nmode; ++q) {
      hp(0,q) = 1.0;
      if (nopt.model == kNoisePower) {
        hp(1,q) = 1.0;
      } else if (nfld == 6) {
        Real qh[3];
        for (int d=0; d<3; ++d) {
          const Real kh = 2.0*M_PI*static_cast<Real>(mode_n[3*q+d])
                          /static_cast<Real>(ng1);
          qh[d] = (nopt.projector == 0) ? StencilWaveNumber(kh, ng) : kh;
        }
        const Real q2 = qh[0]*qh[0] + qh[1]*qh[1] + qh[2]*qh[2];
        hp(1,q) = qh[0]*qh[0]/q2;
        hp(2,q) = qh[0]*qh[1]/q2;
        hp(3,q) = qh[0]*qh[2]/q2;
        hp(4,q) = qh[1]*qh[1]/q2;
        hp(5,q) = qh[1]*qh[2]/q2;
      }
    }
    Kokkos::deep_copy(proj, hp);
    Kokkos::deep_copy(fld_dof, hd);
  }

  // lockstep data: time, background, mode functions
  const int ny = 4 + ((nopt.model == kNoiseMS) ? 4*nshell : 0);
  y0.assign(ny, 0.0);
  y1.assign(ny, 0.0);
  yrhs.assign(ny, 0.0);
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseSetup
//! \brief tables and work arrays on the current mesh, initial amplitudes and mode data
//! (called from Startup, after the ghost cells have been set; on a restart the lockstep
//! data have been read from the restart file)

void ScalarField::NoiseSetup(bool res_flag) {
  if (!nopt.on) return;
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int nmb = pmy_pack->nmb_thispack;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nxm = std::max(nx1, std::max(nx2, nx3));

  // cos and sin of 2 pi n (g + 1/2)/N for the cells of every MeshBlock, the phase
  // reduced with integers: the tables depend on the global cell index only
  Kokkos::realloc(trig_c, nmb, 3, 2*nmax + 1, nxm);
  Kokkos::realloc(trig_s, nmb, 3, 2*nmax + 1, nxm);
  {
    auto off = rng::CellOffsets(pmy_pack);
    auto oh = Kokkos::create_mirror_view(off);
    Kokkos::deep_copy(oh, off);
    auto hc = Kokkos::create_mirror_view(trig_c);
    auto hs = Kokkos::create_mirror_view(trig_s);
    const int nd[3] = {nx1, nx2, nx3};
    for (int m=0; m<nmb; ++m) {
      for (int d=0; d<3; ++d) {
        const std::int64_t nlev = oh(m,4+d);
        for (int n=-nmax; n<=nmax; ++n) {
          for (int i=0; i<nd[d]; ++i) {
            const std::int64_t g = oh(m,d) + i;
            std::int64_t p = (static_cast<std::int64_t>(n)*(2*g + 1)) % (2*nlev);
            if (p < 0) { p += 2*nlev; }
            const double ang = M_PI*static_cast<double>(p)/static_cast<double>(nlev);
            hc(m,d,n+nmax,i) = std::cos(ang);
            hs(m,d,n+nmax,i) = std::sin(ang);
          }
        }
      }
    }
    Kokkos::deep_copy(trig_c, hc);
    Kokkos::deep_copy(trig_s, hs);
  }
  Kokkos::realloc(g1_re, nfld, npair, nx3);
  Kokkos::realloc(g1_im, nfld, npair, nx3);
  Kokkos::realloc(g2_re, nfld, nxval, nx3, nx2);
  Kokkos::realloc(g2_im, nfld, nxval, nx3, nx2);
  Kokkos::realloc(u_noise, nmb, nfld, nx3 + 2*indcs.ng, nx2 + 2*indcs.ng,
                  nx1 + 2*indcs.ng);

  // frozen amplitudes
  alpha_valid = false;
  if (nopt.scheme == kNoiseFrozen) { NoiseDrawAlpha(0); }

  const int ny = static_cast<int>(y0.size());
  if (res_flag) {
    if (y0[0] == 0.0 && pm->time != 0.0 && ny > 0) {
      NoiseFatal("the restart file of the scalar field holds no data of the stochastic "
                 "sources");
    }
  } else {
    // background from the box means of the initial data
    Real mean[8];
    MeshMeans(mean);
    y0[0] = pm->time;
    y0[1] = mean[0];
    y0[2] = mean[1];
    y0[3] = std::log(mean[3])*2.0/pmy_pack->pz4c->opt.chi_psi_power;   // ln a
    if (nopt.model == kNoiseMS) {
      // mode functions at the start: text file with the rows
      //   |n|^2  Re R  Im R  Re dR/dtau  Im dR/dtau
      // for every shell of the mode set (other rows are ignored; '#' starts a comment),
      // in the normalisation in which the field is L^(-3/2) sum R alpha e^(ik.x)
      std::FILE *fp = std::fopen(nopt.mode_file.c_str(), "r");
      if (fp == nullptr) { NoiseFatal("cannot open the mode file " + nopt.mode_file); }
      std::map<int,int> shell_of;
      for (int s=0; s<nshell; ++s) { shell_of[shell_n2[s]] = s; }
      std::vector<int> found(nshell, 0);
      char line[1024];
      while (std::fgets(line, sizeof(line), fp) != nullptr) {
        if (line[0] == '#') continue;
        long n2;
        double a, b, c, d;
        if (std::sscanf(line, "%ld %lf %lf %lf %lf", &n2, &a, &b, &c, &d) != 5) continue;
        auto it = shell_of.find(static_cast<int>(n2));
        if (it == shell_of.end()) continue;
        const int s = it->second;
        y0[4+4*s] = a; y0[5+4*s] = b; y0[6+4*s] = c; y0[7+4*s] = d;
        found[s] = 1;
      }
      std::fclose(fp);
      for (int s=0; s<nshell; ++s) {
        if (!found[s]) {
          NoiseFatal("the mode file " + nopt.mode_file + " has no row for |n|^2 = "
                     + std::to_string(shell_n2[s]));
        }
      }
    }
  }
  noise_ready = true;
  fields_cycle = -1;
  if (global_variable::my_rank == 0) {
    std::cout << "ScalarField: stochastic sources, " << nmode << " modes in " << nshell
              << " shells, " << nfld << " fields" << std::endl;
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseDrawAlpha
//! \brief the amplitudes alpha_n of every degree of freedom for the given epoch

void ScalarField::NoiseDrawAlpha(const std::uint64_t epoch) {
  if (alpha_valid && alpha_epoch == epoch) return;
  auto hr = Kokkos::create_mirror_view(alpha_re);
  auto hi = Kokkos::create_mirror_view(alpha_im);
  const int ndof = static_cast<int>(alpha_re.extent(0));
  const std::uint64_t off = static_cast<std::uint64_t>(1) << 20;
  const double rt = std::sqrt(0.5);
  for (int dof=0; dof<ndof; ++dof) {
    const std::uint64_t stream = rng::Stream(
        rng::kStreamStochastic, (1u << 16) | static_cast<std::uint32_t>(dof));
    for (int q=0; q<nmode; ++q) {
      const std::uint64_t ent = rng::CellEntity(
          static_cast<std::uint64_t>(mode_n[3*q] + static_cast<std::int64_t>(off)),
          static_cast<std::uint64_t>(mode_n[3*q+1] + static_cast<std::int64_t>(off)),
          static_cast<std::uint64_t>(mode_n[3*q+2] + static_cast<std::int64_t>(off)));
      const rng::Key key{nopt.seed, stream, ent, epoch};
      double z[2];
      rng::Normal2(key, 0, z);
      hr(dof,q) = z[0]*rt;
      hi(dof,q) = z[1]*rt;
    }
  }
  Kokkos::deep_copy(alpha_re, hr);
  Kokkos::deep_copy(alpha_im, hi);
  alpha_epoch = epoch;
  alpha_valid = true;
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseBackground
//! \brief background of the Mukhanov-Sasaki model at the state y of the lockstep data:
//! bg = (alpha_b, phi_b, Pi_b, H, a, eps1, eps2, dV/dphi)

void ScalarField::NoiseBackground(const std::vector<Real> &y, Real bg[8]) {
  Real mean[8];
  MeshMeans(mean);
  const Real p = pmy_pack->pz4c->opt.chi_psi_power;
  Real phib, pib, hub, a;
  Real v, dv;
  if (nopt.level == 0) {
    phib = y[1];
    pib = y[2];
    a = std::exp(y[3]);
    SfPotentialEval(pot, pot_tab.h_view, phib, v, dv);
    hub = std::sqrt((8.0*M_PI/3.0)*(0.5*pib*pib + v));
  } else {
    phib = mean[0];
    pib = mean[1];
    hub = -mean[2]/3.0;
    a = std::pow(mean[3], 2.0/p);
    SfPotentialEval(pot, pot_tab.h_view, phib, v, dv);
  }
  const Real eps1 = 4.0*M_PI*pib*pib/(hub*hub);
  const Real eps2 = (pib != 0.0) ? 6.0 + 2.0*dv/(hub*pib) - 2.0*eps1 : 0.0;
  bg[0] = mean[4];
  bg[1] = phib; bg[2] = pib; bg[3] = hub; bg[4] = a;
  bg[5] = eps1; bg[6] = eps2; bg[7] = dv;
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseModeRHS
//! \brief time derivative of the lockstep data at the state y (coordinate time; the
//! proper time of the background runs at the rate alpha_b), the shell factors of the
//! sources and the coefficients of the kicks

void ScalarField::NoiseModeRHS(const std::vector<Real> &y, std::vector<Real> &f) {
  f[0] = 1.0;
  if (nopt.model != kNoiseMS) {
    f[1] = 0.0; f[2] = 0.0; f[3] = 0.0;
    return;
  }
  Real bg[8];
  NoiseBackground(y, bg);
  const Real alp = bg[0], pib = bg[2], hub = bg[3], a = bg[4];
  const Real eps1 = bg[5], eps2 = bg[6], dv = bg[7];
  // Friedmann background (integrated also with level 1, as a diagnostic)
  {
    Real v, dvb;
    SfPotentialEval(pot, pot_tab.h_view, y[1], v, dvb);
    const Real hb = std::sqrt((8.0*M_PI/3.0)*(0.5*y[2]*y[2] + v));
    f[1] = alp*y[2];
    f[2] = alp*(-3.0*hb*y[2] - dvb);
    f[3] = alp*hb;
  }
  Mesh *pm = pmy_pack->pmesh;
  const Real len = pm->mesh_size.x1max - pm->mesh_size.x1min;
  const Real kf = 2.0*M_PI/len;
  const Real norm = 1.0/(len*std::sqrt(len));
  const Real s = nopt.sharpness;
  const Real dlnks = hub*(1.0 - eps1);
  const Real d2lnks = hub*hub*eps1*(eps2 - 1.0 + eps1);
  auto hr = Kokkos::create_mirror_view(shell_re);
  auto hi = Kokkos::create_mirror_view(shell_im);
  for (int n=0; n<nshell; ++n) {
    const Real k = kf*std::sqrt(static_cast<Real>(shell_n2[n]));
    const Real rr = y[4+4*n], ri = y[5+4*n], dr = y[6+4*n], di = y[7+4*n];
    const Real fric = (3.0 - eps2)*hub;
    const Real k2a2 = k*k/(a*a);
    f[4+4*n] = alp*dr;
    f[5+4*n] = alp*di;
    f[6+4*n] = alp*(-fric*dr - k2a2*rr);
    f[7+4*n] = alp*(-fric*di - k2a2*ri);
    // window and its first two proper-time derivatives
    const Real x = s*std::log(nopt.sigma*a*hub/k);
    const Real ch = std::cosh(x);
    const Real sech2 = 1.0/(ch*ch);
    const Real w1 = 0.5*s*sech2*dlnks;
    const Real w2 = 0.5*sech2*(s*d2lnks - 2.0*s*s*std::tanh(x)*dlnks*dlnks);
    hr(n) = norm*(rr*w2 + (2.0*dr + fric*rr)*w1);
    hi(n) = norm*(ri*w2 + (2.0*di + fric*ri)*w1);
  }
  Kokkos::deep_copy(shell_re, hr);
  Kokkos::deep_copy(shell_im, hi);
  kick_pi_fac = nopt.pi_sign*alp*pib/hub;
  kick_k_fac = -alp*eps1;
  kick_a_fac = alp*eps1;
  stage_eps1 = eps1; stage_eps2 = eps2; stage_hub = hub; stage_a = a;
  (void) dv;
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseShellFactors
//! \brief power model: shell factors of the increment of the step that starts at
//! y[0] = t and ends at t + dt

void ScalarField::NoiseShellFactors(const std::vector<Real> &y) {
  Mesh *pm = pmy_pack->pmesh;
  const Real len = pm->mesh_size.x1max - pm->mesh_size.x1min;
  const Real t0 = pm->time, t1 = pm->time + pm->dt;
  const Real ks0 = nopt.ksigma0*std::exp(nopt.hubble*(t0 - nopt.t0));
  const Real ks1 = nopt.ksigma0*std::exp(nopt.hubble*(t1 - nopt.t0));
  auto hr = Kokkos::create_mirror_view(shell_re);
  auto hi = Kokkos::create_mirror_view(shell_im);
  for (int n=0; n<nshell; ++n) {
    const Real q = std::sqrt(static_cast<Real>(shell_n2[n]));
    Real dw;
    if (nopt.window == kWindowTanh) {
      // W1 - W0 = (tanh x1 - tanh x0)/2 = sinh(x1 - x0)/(2 cosh x1 cosh x0): no
      // cancellation for modes far inside or outside the window
      const Real x0 = nopt.sharpness*std::log(ks0/q);
      const Real x1 = nopt.sharpness*std::log(ks1/q);
      dw = 0.5*std::sinh(nopt.sharpness*nopt.hubble*(t1 - t0))
           /(std::cosh(x1)*std::cosh(x0));
    } else {
      dw = ((q <= ks1) ? 1.0 : 0.0) - ((q <= ks0) ? 1.0 : 0.0);
    }
    if (!(dw > 0.0)) { dw = 0.0; }
    const Real base = nopt.amp*std::pow(q, 0.5*(nopt.tilt - 3.0))/(len*std::sqrt(len));
    hr(n) = base*((nopt.scheme == kNoiseFrozen) ? dw : std::sqrt(dw));
    hi(n) = 0.0;
  }
  Kokkos::deep_copy(shell_re, hr);
  Kokkos::deep_copy(shell_im, hi);
  (void) y;
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseSynthesize
//! \brief the fields on the active cells of every MeshBlock from the shell factors, the
//! amplitudes and the projector factors, by three one-dimensional sums

void ScalarField::NoiseSynthesize() {
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const int nmb = pmy_pack->nmb_thispack;
  const int nf = nfld, np = npair, nxv = nxval, nmx = nmax;
  auto pstart = pair_start, pny = pair_ny, xstart = xval_start, xnx = xval_nx;
  auto mnz = mode_nz, mshell = mode_shell, fdof = fld_dof;
  auto are = alpha_re, aim = alpha_im, prj = proj;
  auto shr = shell_re, shi = shell_im;
  auto tc = trig_c, ts = trig_s;
  auto g1r = g1_re, g1i = g1_im;
  auto g2r = g2_re, g2i = g2_im;
  auto noise = u_noise;

  for (int mb=0; mb<nmb; ++mb) {
    const int m = mb;
    // sum over n_z for every pair (n_x, n_y)
    par_for("sf_syn_z", DevExeSpace(), 0, nf-1, 0, np-1, 0, nx3-1,
    KOKKOS_LAMBDA(const int f, const int p, const int k) {
      Real re = 0.0, im = 0.0;
      const int dof = fdof(f);
      for (int q=pstart(p); q<pstart(p+1); ++q) {
        const int s = mshell(q);
        const Real ar = are(dof,q), ai = aim(dof,q);
        const Real cr = (shr(s)*ar - shi(s)*ai)*prj(f,q);
        const Real ci = (shr(s)*ai + shi(s)*ar)*prj(f,q);
        const Real c = tc(m,2,mnz(q)+nmx,k), sn = ts(m,2,mnz(q)+nmx,k);
        re += cr*c - ci*sn;
        im += cr*sn + ci*c;
      }
      g1r(f,p,k) = re;
      g1i(f,p,k) = im;
    });
    // sum over n_y for every n_x
    par_for("sf_syn_y", DevExeSpace(), 0, nf-1, 0, nxv-1, 0, nx3-1, 0, nx2-1,
    KOKKOS_LAMBDA(const int f, const int x, const int k, const int j) {
      Real re = 0.0, im = 0.0;
      for (int p=xstart(x); p<xstart(x+1); ++p) {
        const Real c = tc(m,1,pny(p)+nmx,j), sn = ts(m,1,pny(p)+nmx,j);
        re += g1r(f,p,k)*c - g1i(f,p,k)*sn;
        im += g1r(f,p,k)*sn + g1i(f,p,k)*c;
      }
      g2r(f,x,k,j) = re;
      g2i(f,x,k,j) = im;
    });
    // sum over n_x; the partner modes -n double the real part
    par_for("sf_syn_x", DevExeSpace(), 0, nf-1, 0, nx3-1, 0, nx2-1, 0, nx1-1,
    KOKKOS_LAMBDA(const int f, const int k, const int j, const int i) {
      Real re = 0.0;
      for (int x=0; x<nxv; ++x) {
        re += g2r(f,x,k,j)*tc(m,0,xnx(x)+nmx,i) - g2i(f,x,k,j)*ts(m,0,xnx(x)+nmx,i);
      }
      noise(m,f,k+ks,j+js,i+is) = 2.0*re;
    });
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseStage
//! \brief sources of this stage: derivative of the lockstep data, shell factors, fields

void ScalarField::NoiseStage(Driver *pdriver, int stage) {
  if (!noise_ready) return;
  Mesh *pm = pmy_pack->pmesh;
  if (nopt.model == kNoisePower) {
    NoiseModeRHS(y0, yrhs);
    // the increment of the step is formed once, in the first stage
    if (stage == 1 || fields_cycle != pm->ncycle) {
      if (nopt.scheme == kNoiseMarkov) {
        NoiseDrawAlpha(static_cast<std::uint64_t>(pm->ncycle) + 1);
      }
      NoiseShellFactors(y0);
      NoiseSynthesize();
      fields_cycle = pm->ncycle;
    }
  } else {
    NoiseModeRHS(y0, yrhs);
    NoiseSynthesize();
  }
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseCopy, NoiseUpdate
//! \brief the low-storage update of the fields (CopyU, ExpRKUpdate) applied to the
//! lockstep data

void ScalarField::NoiseCopy(Driver *pdriver, int stage) {
  if (!noise_ready) return;
  const std::size_t ny = y0.size();
  if (pdriver->integrator == "rk4") {
    if (stage == 1) {
      y1 = y0;
    } else {
      const Real delta = pdriver->delta[stage-1];
      for (std::size_t n=0; n<ny; ++n) { y1[n] += delta*y0[n]; }
    }
  } else {
    if (stage == 1) { y1 = y0; }
  }
}

void ScalarField::NoiseUpdate(Driver *pdriver, int stage) {
  if (!noise_ready) return;
  const Real gam0 = pdriver->gam0[stage-1];
  const Real gam1 = pdriver->gam1[stage-1];
  const Real beta_dt = (pdriver->beta[stage-1])*(pmy_pack->pmesh->dt);
  const std::size_t ny = y0.size();
  for (std::size_t n=0; n<ny; ++n) {
    y0[n] = gam0*y0[n] + gam1*y1[n] + beta_dt*yrhs[n];
  }
}

//----------------------------------------------------------------------------------------
//! \fn TaskStatus ScalarField::Kick
//! \brief Mukhanov-Sasaki model: sources of Khat and At_ij, added to the right-hand side
//! of the spacetime variables after Z4c::CalcRHS (T_zz = I_R - T_xx - T_yy)

TaskStatus ScalarField::Kick(Driver *pdriver, int stage) {
  if (!noise_ready || nopt.model != kNoiseMS) return TaskStatus::complete;
  if (!nopt.kick_k && !nopt.kick_a) return TaskStatus::complete;
  auto &indcs = pmy_pack->pmesh->mb_indcs;
  const int is = indcs.is, ie = indcs.ie;
  const int js = indcs.js, je = indcs.je;
  const int ks = indcs.ks, ke = indcs.ke;
  const int nmb1 = pmy_pack->nmb_thispack - 1;
  auto zrhs = pmy_pack->pz4c->u_rhs;
  auto noise = u_noise;
  const int ikh = z4c::Z4c::I_Z4C_KHAT, iaxx = z4c::Z4c::I_Z4C_AXX;
  const bool do_k = nopt.kick_k, do_a = nopt.kick_a;
  const Real fk = kick_k_fac, fa = kick_a_fac;
  par_for("sf_kick", DevExeSpace(), 0, nmb1, ks, ke, js, je, is, ie,
  KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
    const Real ir = noise(m,0,k,j,i);
    if (do_k) { zrhs(m,ikh,k,j,i) += fk*ir; }
    if (do_a) {
      const Real txx = noise(m,1,k,j,i), txy = noise(m,2,k,j,i), txz = noise(m,3,k,j,i);
      const Real tyy = noise(m,4,k,j,i), tyz = noise(m,5,k,j,i);
      const Real tzz = ir - txx - tyy;
      const Real third = ir/3.0;
      zrhs(m,iaxx  ,k,j,i) += fa*(third - txx);
      zrhs(m,iaxx+1,k,j,i) += fa*(-txy);
      zrhs(m,iaxx+2,k,j,i) += fa*(-txz);
      zrhs(m,iaxx+3,k,j,i) += fa*(third - tyy);
      zrhs(m,iaxx+4,k,j,i) += fa*(-tyz);
      zrhs(m,iaxx+5,k,j,i) += fa*(third - tzz);
    }
  });
  return TaskStatus::complete;
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseFieldsOfState
//! \brief Mukhanov-Sasaki model: the fields of the state reached at the end of a step
//! (for a dump; the stages of the next step form their own)

void ScalarField::NoiseFieldsOfState() {
  if (!noise_ready || nopt.model != kNoiseMS) return;
  std::vector<Real> f(y0.size());
  NoiseModeRHS(y0, f);
  NoiseSynthesize();
}

//----------------------------------------------------------------------------------------
//! \fn void ScalarField::NoiseWriteState
//! \brief text record of the lockstep data next to a dump: <basename>.sf.<number>.modes
//! with the time, the background, and per shell |n|^2, R, dR/dtau and the shell factor

void ScalarField::NoiseWriteState(Real time, int number, bool header) {
  if (!noise_ready) return;
  char fname[512];
  std::snprintf(fname, sizeof(fname), "%s.sf.%05d.modes", basename.c_str(), number);
  std::FILE *fp = std::fopen(fname, "w");
  if (fp == nullptr) { NoiseFatal(std::string("cannot open ") + fname); }
  std::fprintf(fp, "# time %.17e  lockstep time %.17e  alpha epoch %llu\n", time, y0[0],
               static_cast<unsigned long long>(alpha_epoch));
  std::fprintf(fp, "# phi_b %.17e  Pi_b %.17e  ln_a %.17e\n", y0[1], y0[2], y0[3]);
  std::fprintf(fp, "# H %.17e  a %.17e  eps1 %.17e  eps2 %.17e\n", stage_hub, stage_a,
               stage_eps1, stage_eps2);
  std::fprintf(fp, "# kick factors: Pi %.17e  Khat %.17e  At %.17e\n", kick_pi_fac,
               kick_k_fac, kick_a_fac);
  std::fprintf(fp, "# n2  Re_R  Im_R  Re_dR  Im_dR  Re_shell  Im_shell\n");
  auto hr = Kokkos::create_mirror_view(shell_re);
  auto hi = Kokkos::create_mirror_view(shell_im);
  Kokkos::deep_copy(hr, shell_re);
  Kokkos::deep_copy(hi, shell_im);
  const bool ms = (nopt.model == kNoiseMS);
  for (int n=0; n<nshell; ++n) {
    std::fprintf(fp, "%d %.17e %.17e %.17e %.17e %.17e %.17e\n", shell_n2[n],
                 ms ? y0[4+4*n] : 0.0, ms ? y0[5+4*n] : 0.0, ms ? y0[6+4*n] : 0.0,
                 ms ? y0[7+4*n] : 0.0, hr(n), hi(n));
  }
  std::fclose(fp);
  (void) header;
}

} // namespace scalarfield
