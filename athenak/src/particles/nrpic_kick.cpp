//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_kick.cpp
//! \brief Test of the reproducible random numbers (utils/rng.hpp) inside the particle
//! module: a random kick of the momenta u_i at the end of every push.  It is not a
//! physical process (the kick acts on the covariant components and ignores the metric);
//! it exists to show that draws keyed by the particle tag and the cycle number give the
//! same particle states for any division into MeshBlocks and across a restart, and it
//! is the pattern to copy for a stochastic term in a kernel.  Options in <particles>:
//!   test_kick        = true      switches the kick on (absent: no effect at all)
//!   test_kick_sigma  = s         size of the kick
//!   test_kick_mode   = normal    u_i += s sqrt(dt) z_i, three normal deviates z_i
//!                    = direction u_i += s n_i with an isotropic unit vector n, applied
//!                                with probability test_kick_prob per step
//!   test_kick_key    = tag       key (seed, stream, tag, cycle): the reproducible choice
//!                    = block     control: the MeshBlock that contains the particle also
//!                                enters the key, as with one generator per MeshBlock
//!                    = sequence  control: the number of kicks since the executable
//!                                started replaces the cycle, as with a generator whose
//!                                state is not in the restart file
//! The seed is <job> rng_seed.  Every step appends a record to <basename>.kick.txt:
//! cycle, time after the step, particles, particles kicked, and a checksum of the
//! deviates (sum over the particles, modulo 2^64, of a hash of their bits weighted with
//! the tag; it does not depend on the order of the particles or on their states).

#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <string>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_mesh.hpp"
#include "utils/rng.hpp"

namespace particles {

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicKickInit
//! \brief reads the options of the test kick; nothing is added to the input parameters
//! unless <particles> test_kick is present

void Particles::NrpicKickInit(ParameterInput *pin) {
  kick.on = false;
  if (!pin->DoesParameterExist("particles", "test_kick")) return;
  kick.on = pin->GetBoolean("particles", "test_kick");
  if (!kick.on) return;
  kick.sigma = pin->GetOrAddReal("particles", "test_kick_sigma", 1.0e-3);
  kick.prob = pin->GetOrAddReal("particles", "test_kick_prob", 1.0);
  const std::string mode = pin->GetOrAddString("particles", "test_kick_mode", "normal");
  const std::string key = pin->GetOrAddString("particles", "test_kick_key", "tag");
  if (mode.compare("normal") == 0) {
    kick.mode = 0;
  } else if (mode.compare("direction") == 0) {
    kick.mode = 1;
  } else {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "<particles> test_kick_mode = '" << mode << "' not recognized"
              << std::endl;
    std::exit(EXIT_FAILURE);
  }
  if (key.compare("tag") == 0) {
    kick.key = 0;
  } else if (key.compare("block") == 0) {
    kick.key = 1;
  } else if (key.compare("sequence") == 0) {
    kick.key = 2;
  } else {
    std::cout << "### FATAL ERROR in " << __FILE__ << " at line " << __LINE__ << std::endl
              << "<particles> test_kick_key = '" << key << "' not recognized"
              << std::endl;
    std::exit(EXIT_FAILURE);
  }
  kick.seed = rng::RunSeed(pin);
  kick.ncalls = 0;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicTestKick
//! \brief kicks the momenta of all particles; called at the end of NrpicPush, while the
//! cycle counter still holds the number of the step that is being taken

void Particles::NrpicTestKick() {
  Mesh *pm = pmy_pack->pmesh;
  const int np = nprtcl_thispack;
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int gids = pmy_pack->gids;
  const int nmb = pmy_pack->nmb_thispack;
  const int mode = kick.mode;
  const bool by_block = (kick.key == 1);
  const std::uint64_t seed = kick.seed;
  const std::uint64_t stream = rng::Stream(rng::kStreamTests, 16);
  const std::uint64_t step = (kick.key == 2) ? static_cast<std::uint64_t>(kick.ncalls)
                                             : static_cast<std::uint64_t>(pm->ncycle);
  const Real amp = (mode == 0) ? kick.sigma*sqrt(pm->dt) : kick.sigma;
  const Real prob = kick.prob;

  std::uint64_t csum = 0;
  int nkick = 0;
  if (np > 0) {
    Kokkos::parallel_reduce("nrpic_kick", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, std::uint64_t &lsum, int &lnk) {
      if (pi(PGID,p) < 0) return;        // removed in this push
      const std::uint64_t tag = static_cast<std::uint64_t>(pi(PTAG,p));
      rng::Key key{seed, stream, tag, step};
      if (by_block) {
        const int m = nrpic::FindBlock(sz, nmb, pi(PGID,p) - gids, pr(IPX,p), pr(IPY,p),
                                       pr(IPZ,p));
        key.entity_hi = static_cast<std::uint64_t>(m + gids + 1);
      }
      double du[3] = {0.0, 0.0, 0.0};
      if (mode == 0) {
        rng::Normal2(key, 0, du);        // du[0], du[1]
        du[2] = rng::Normal(key, 1);
      } else {
        if (rng::Uniform(key, 0) >= prob) return;
        rng::Direction(key, 1, du);
      }
      pr(IPVX,p) += amp*du[0];
      pr(IPVY,p) += amp*du[1];
      pr(IPVZ,p) += amp*du[2];
      const std::uint64_t b0 = Kokkos::bit_cast<std::uint64_t>(du[0]);
      const std::uint64_t b1 = Kokkos::bit_cast<std::uint64_t>(du[1]);
      const std::uint64_t b2 = Kokkos::bit_cast<std::uint64_t>(du[2]);
      lsum += (b0 ^ ((b1 << 21) | (b1 >> 43)) ^ ((b2 << 42) | (b2 >> 22)))*(2*tag + 1);
      lnk += 1;
    }, Kokkos::Sum<std::uint64_t>(csum), Kokkos::Sum<int>(nkick));
  }

  // record of the step; a new run starts a new file, a restarted run appends
  const std::string fname = nr_basename + ".kick.txt";
  const bool fresh = (pm->ncycle == 0);
  std::FILE *fp = std::fopen(fname.c_str(), fresh ? "w" : "a");
  if (fp != nullptr) {
    if (fresh) {
      std::fprintf(fp, "# cycle  time  particles  kicked  checksum  key_step\n");
    }
    std::fprintf(fp, "%d %.17e %d %d %016" PRIx64 " %" PRIu64 "\n", pm->ncycle,
                 pm->time + pm->dt, np, nkick, csum, step);
    std::fclose(fp);
  }
  kick.ncalls += 1;
}

} // namespace particles
