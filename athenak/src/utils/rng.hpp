#ifndef UTILS_RNG_HPP_
#define UTILS_RNG_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file rng.hpp
//! \brief Reproducible random numbers for device kernels.  Every draw is a pure function
//! of its key (seed, stream, entity, step, draw): there is no generator state, so the
//! numbers do not depend on the division into MeshBlocks, on the number of ranks or
//! threads, on the order of execution or on the position of a restart.
//!
//! The generator is Philox-4x64 with ten rounds (Salmon, Moraes, Dror & Shaw 2011), the
//! function behind numpy.random.Philox: a bijection of a 256-bit counter under a 128-bit
//! key.  The key holds (seed, stream), the counter (entity, entity_hi, step,
//! draw*256 + kind*16 + block); kind separates raw words, normal pairs and directions,
//! block counts the retries of a rejection step.
//!
//! Uniform, normal and direction draws are bit-identical on every platform with IEEE 754
//! double precision in round-to-nearest (processor, card, and the NumPy twin
//! python/nrpic/rng.py): they use integer arithmetic, exact conversions, and single
//! correctly rounded operations (product, quotient, square root) arranged so that no
//! inexact product feeds a sum, which leaves a fused multiply-add nothing to change.  No
//! library logarithm or trigonometric function is called.  Do not compile with options
//! that change floating-point values (-ffast-math).
//!
//! Rules for users, the registry of streams and the measured cost: docs/RNG.md and
//! coord/INTERFACES/rng.md.  The file has no dependence on the rest of AthenaK; define
//! NRPIC_STANDALONE to compile it outside the code.

#include <cmath>
#include <cstdint>

#ifdef NRPIC_STANDALONE
#ifndef KOKKOS_INLINE_FUNCTION
#define KOKKOS_INLINE_FUNCTION inline
#endif
#else
#include <string>
#include "athena.hpp"
#include "parameter_input.hpp"
#endif

namespace rng {

//----------------------------------------------------------------------------------------
// Registry of streams (the purpose of a draw).  A stream word is Stream(id, sub): the
// identifier in the upper 32 bits, a sub-stream chosen by the owner of the stream in
// the lower 32 bits.  New identifiers are added by a change of coord/INTERFACES/rng.md.

enum StreamId : std::uint32_t {
  kStreamInitialData = 1,   // sampling of particles and fields at the start of a run
  kStreamCollisions  = 2,   // Monte Carlo collisions (track C)
  kStreamStochastic  = 3,   // stochastic sources of fields (track E)
  kStreamTests       = 4    // tests of this interface and of the code
};

// kind of draw, part of the last counter word
enum DrawKind : std::uint64_t {kKindBits = 0, kKindNormal = 1, kKindDirection = 2};

//----------------------------------------------------------------------------------------
//! \struct Key
//! \brief everything that identifies a draw except its index.  The entity is a property
//! of the physical object (particle tag, global index of a cell, wave number), never of
//! its storage (array index, MeshBlock, rank, thread).

struct Key {
  std::uint64_t seed;           // seed of the run (<job> rng_seed)
  std::uint64_t stream;         // Stream(id, sub)
  std::uint64_t entity;         // particle tag, CellEntity(i, j, k), ...
  std::uint64_t step;           // number of the time step (cycle), restored by a restart
  std::uint64_t entity_hi = 0;  // second word of the entity (second tag of a pair,
                                // refinement level of a cell), zero if not needed
};

KOKKOS_INLINE_FUNCTION
std::uint64_t Stream(const std::uint32_t id, const std::uint32_t sub = 0) {
  return (static_cast<std::uint64_t>(id) << 32) | static_cast<std::uint64_t>(sub);
}

//! entity of a cell from its global indices on its own refinement level (each below
//! 2^21); the level relative to the root mesh belongs in Key::entity_hi
KOKKOS_INLINE_FUNCTION
std::uint64_t CellEntity(const std::uint64_t i, const std::uint64_t j,
                         const std::uint64_t k) {
  return i | (j << 21) | (k << 42);
}

//----------------------------------------------------------------------------------------
//! \fn MulHi64
//! \brief upper 64 bits of the 128-bit product of two unsigned 64-bit integers

KOKKOS_INLINE_FUNCTION
std::uint64_t MulHi64Portable(const std::uint64_t a, const std::uint64_t b) {
  const std::uint64_t a0 = a & 0xFFFFFFFFULL, a1 = a >> 32;
  const std::uint64_t b0 = b & 0xFFFFFFFFULL, b1 = b >> 32;
  const std::uint64_t p00 = a0*b0, p01 = a0*b1, p10 = a1*b0, p11 = a1*b1;
  const std::uint64_t mid = (p00 >> 32) + (p01 & 0xFFFFFFFFULL) + (p10 & 0xFFFFFFFFULL);
  return p11 + (p01 >> 32) + (p10 >> 32) + (mid >> 32);
}

KOKKOS_INLINE_FUNCTION
std::uint64_t MulHi64(const std::uint64_t a, const std::uint64_t b) {
#if defined(__CUDA_ARCH__)
  return __umul64hi(a, b);
#elif defined(__SIZEOF_INT128__)
  __extension__ typedef unsigned __int128 Uint128;
  return static_cast<std::uint64_t>((static_cast<Uint128>(a)*static_cast<Uint128>(b))
                                    >> 64);
#else
  return MulHi64Portable(a, b);
#endif
}

//----------------------------------------------------------------------------------------
//! \fn Philox4x64
//! \brief Philox-4x64-10: r = bijection_k(c).  Ten rounds, each two 64 x 64 -> 128 bit
//! products and a permutation; the key is advanced by the Weyl constants between rounds.

KOKKOS_INLINE_FUNCTION
void Philox4x64(const std::uint64_t c[4], const std::uint64_t k[2], std::uint64_t r[4]) {
  const std::uint64_t m0 = 0xD2E7470EE14C6C93ULL, m1 = 0xCA5A826395121157ULL;
  const std::uint64_t w0 = 0x9E3779B97F4A7C15ULL, w1 = 0xBB67AE8584CAA73BULL;
  std::uint64_t x0 = c[0], x1 = c[1], x2 = c[2], x3 = c[3];
  std::uint64_t k0 = k[0], k1 = k[1];
  for (int n=0; n<10; ++n) {
    if (n > 0) { k0 += w0; k1 += w1; }
    const std::uint64_t hi0 = MulHi64(m0, x0), lo0 = m0*x0;
    const std::uint64_t hi1 = MulHi64(m1, x2), lo1 = m1*x2;
    x0 = hi1 ^ x1 ^ k0;
    x1 = lo1;
    x2 = hi0 ^ x3 ^ k1;
    x3 = lo0;
  }
  r[0] = x0; r[1] = x1; r[2] = x2; r[3] = x3;
}

//----------------------------------------------------------------------------------------
//! \fn Words
//! \brief the four 64-bit words of one generator call for a key, a draw index (below
//! 2^56), a kind and a block

KOKKOS_INLINE_FUNCTION
void Words(const Key &key, const std::uint64_t draw, const std::uint64_t kind,
           const std::uint64_t block, std::uint64_t r[4]) {
  const std::uint64_t c[4] = {key.entity, key.entity_hi, key.step,
                              (draw << 8) | (kind << 4) | block};
  const std::uint64_t k[2] = {key.seed, key.stream};
  Philox4x64(c, k, r);
}

//! four independent raw words of draw number draw
KOKKOS_INLINE_FUNCTION
void Bits4(const Key &key, const std::uint64_t draw, std::uint64_t r[4]) {
  Words(key, draw, kKindBits, 0, r);
}

//! first raw word of draw number draw
KOKKOS_INLINE_FUNCTION
std::uint64_t Bits(const Key &key, const std::uint64_t draw) {
  std::uint64_t r[4];
  Words(key, draw, kKindBits, 0, r);
  return r[0];
}

//----------------------------------------------------------------------------------------
//! \fn ToUniform
//! \brief maps a word to the open interval (0,1): (n + 1/2) 2^-52 with n the upper 52
//! bits.  Exact; smallest value 2^-53, largest 1 - 2^-53, mean 1/2.

KOKKOS_INLINE_FUNCTION
double ToUniform(const std::uint64_t w) {
  return (static_cast<double>(w >> 12) + 0.5)*0x1.0p-52;
}

//! uniform deviate in (0,1) (first word of the draw)
KOKKOS_INLINE_FUNCTION
double Uniform(const Key &key, const std::uint64_t draw) {
  return ToUniform(Bits(key, draw));
}

//! four independent uniform deviates in (0,1) from one generator call
KOKKOS_INLINE_FUNCTION
void Uniform4(const Key &key, const std::uint64_t draw, double u[4]) {
  std::uint64_t r[4];
  Words(key, draw, kKindBits, 0, r);
  for (int n=0; n<4; ++n) { u[n] = ToUniform(r[n]); }
}

//! integer in [0, n) (first word of the draw, multiply-shift; the probabilities of the
//! values differ from 1/n by less than 2^-64)
KOKKOS_INLINE_FUNCTION
std::uint64_t Index(const Key &key, const std::uint64_t draw, const std::uint64_t n) {
  return MulHi64(Bits(key, draw), n);
}

//----------------------------------------------------------------------------------------
//! \fn DiskPoint
//! \brief one attempt of the rejection step shared by the normal and the direction
//! draws.  The upper 52 bits of the word give two odd integers v1, v2 in (-2^26, 2^26);
//! the attempt is accepted if s = v1^2 + v2^2 < 2^52, i.e. if (v1, v2) 2^-26 lies in the
//! unit disk (probability pi/4).  Integer arithmetic only; s is even and at least 2.

KOKKOS_INLINE_FUNCTION
bool DiskPoint(const std::uint64_t w, std::int64_t &v1, std::int64_t &v2,
               std::int64_t &s) {
  v1 = 2*static_cast<std::int64_t>(w >> 38) + 1 - (static_cast<std::int64_t>(1) << 26);
  v2 = 2*static_cast<std::int64_t>((w >> 12) & 0x3FFFFFFULL) + 1
       - (static_cast<std::int64_t>(1) << 26);
  s = v1*v1 + v2*v2;
  return (s < (static_cast<std::int64_t>(1) << 52));
}

//----------------------------------------------------------------------------------------
//! \fn NegLog52
//! \brief -ln(s 2^-52) for an integer 0 < s < 2^52 from the arithmetic-geometric mean:
//! ln(4/y) = pi / (2 agm(1, y)) (1 + O(y^2)) with y = 2^-30 (s 2^-52) <= 2^-30, so that
//! -ln(s 2^-52) = pi / (2 agm) - 32 ln 2.  Ten steps (nine reach the fixed point for
//! every s).  Absolute error below 3e-14; the result is not negative.  Only sums of
//! non-products, products, square roots, one quotient and one difference: the same
//! bits on every IEEE 754 platform.

KOKKOS_INLINE_FUNCTION
double NegLog52(const std::int64_t s) {
  double a = 1.0;
  double b = static_cast<double>(s)*0x1.0p-82;
  for (int n=0; n<10; ++n) {
    const double an = 0.5*(a + b);
    b = sqrt(a*b);
    a = an;
  }
  const double big = 0x1.921fb54442d18p+0/a;         // (pi/2) / agm
  const double l = big - 0x1.62e42fefa39efp+4;       // minus 32 ln 2
  return (l > 0.0) ? l : 0.0;
}

//----------------------------------------------------------------------------------------
//! \fn Normal2
//! \brief two independent standard normal deviates (polar form of the Box-Muller
//! transformation): z_i = v_i sqrt(-2 ln(s) / s) for a point (v1, v2) uniform in the unit
//! disk, s = v1^2 + v2^2.  |z| is below 8.5.

KOKKOS_INLINE_FUNCTION
void Normal2(const Key &key, const std::uint64_t draw, double z[2]) {
  for (std::uint64_t blk=0; blk<16; ++blk) {
    std::uint64_t r[4];
    Words(key, draw, kKindNormal, blk, r);
    for (int n=0; n<4; ++n) {
      std::int64_t v1, v2, s;
      if (DiskPoint(r[n], v1, v2, s)) {
        // v_i and s are in units of 2^-26 and 2^-52, which cancel in v_i / sqrt(s)
        const double f = sqrt((2.0*NegLog52(s))/static_cast<double>(s));
        z[0] = static_cast<double>(v1)*f;
        z[1] = static_cast<double>(v2)*f;
        return;
      }
    }
  }
  z[0] = 0.0; z[1] = 0.0;     // 64 rejections in a row: probability 1e-43
}

//! one standard normal deviate (the first of the pair of this draw)
KOKKOS_INLINE_FUNCTION
double Normal(const Key &key, const std::uint64_t draw) {
  double z[2];
  Normal2(key, draw, z);
  return z[0];
}

//----------------------------------------------------------------------------------------
//! \fn Direction
//! \brief unit vector with isotropic distribution (Marsaglia 1972): for a point (v1, v2)
//! uniform in the unit disk, n = (2 v1 sqrt(1-s), 2 v2 sqrt(1-s), 1 - 2 s).

KOKKOS_INLINE_FUNCTION
void Direction(const Key &key, const std::uint64_t draw, double n[3]) {
  for (std::uint64_t blk=0; blk<16; ++blk) {
    std::uint64_t r[4];
    Words(key, draw, kKindDirection, blk, r);
    for (int m=0; m<4; ++m) {
      std::int64_t v1, v2, s;
      if (DiskPoint(r[m], v1, v2, s)) {
        const double sr = static_cast<double>(s)*0x1.0p-52;       // exact
        const double h = sqrt(1.0 - sr);                          // exact difference
        n[0] = (static_cast<double>(v1)*0x1.0p-25)*h;
        n[1] = (static_cast<double>(v2)*0x1.0p-25)*h;
        n[2] = 1.0 - 2.0*sr;                                      // exact
        return;
      }
    }
  }
  n[0] = 0.0; n[1] = 0.0; n[2] = 1.0;     // 64 rejections in a row: probability 1e-43
}

#ifndef NRPIC_STANDALONE
//----------------------------------------------------------------------------------------
//! \fn RunSeed
//! \brief the seed of the run, <job> rng_seed in the input file (an unsigned integer of
//! up to 64 bits, decimal or with the prefix 0x; default 0).  It is stored with the
//! other parameters in a restart file.  Not a kernel function: read it once and capture
//! the value.

inline std::uint64_t RunSeed(ParameterInput *pin) {
  const std::string s = pin->GetOrAddString("job", "rng_seed", "0");
  return static_cast<std::uint64_t>(std::stoull(s, nullptr, 0));
}
#endif

} // namespace rng
#endif // UTILS_RNG_HPP_
