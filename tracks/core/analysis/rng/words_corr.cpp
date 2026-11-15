// Covariances between the four words of one generator call (utils/rng.hpp), from a large
// number of calls: follow-up of the statistics run core-20261115-120536-5bdb22c.
//
//   words_corr <seed> <number of calls>
//
// Key as in the unit test: stream tests/1, entity = 0 .. n-1, step 7, draw 0. Prints
// n, the sums of d_a = u_a - 1/2 (4), of d_a^2 (4) and of d_a d_b for the pairs
// (0,1) (0,2) (0,3) (1,2) (1,3) (2,3).
//
// Build: g++ -std=c++17 -O3 -march=native -DNRPIC_STANDALONE -I athenak/src words_corr.cpp

#include <cstdint>
#include <cstdio>
#include <cstdlib>

#include "utils/rng.hpp"

int main(int argc, char *argv[]) {
  if (argc != 3) { return 2; }
  const std::uint64_t seed = std::strtoull(argv[1], nullptr, 0);
  const std::uint64_t n = static_cast<std::uint64_t>(std::strtod(argv[2], nullptr));
  const std::uint64_t st = rng::Stream(rng::kStreamTests, 1);
  long double tot[14];
  for (int k=0; k<14; ++k) { tot[k] = 0.0L; }
  const std::uint64_t chunk = 1ULL << 20;
  for (std::uint64_t lo=0; lo<n; lo+=chunk) {
    const std::uint64_t hi = (lo + chunk < n) ? lo + chunk : n;
    double s[14];
    for (int k=0; k<14; ++k) { s[k] = 0.0; }
    for (std::uint64_t i=lo; i<hi; ++i) {
      const rng::Key key{seed, st, i, 7};
      double u[4];
      rng::Uniform4(key, 0, u);
      const double d0 = u[0] - 0.5, d1 = u[1] - 0.5, d2 = u[2] - 0.5, d3 = u[3] - 0.5;
      s[0] += d0; s[1] += d1; s[2] += d2; s[3] += d3;
      s[4] += d0*d0; s[5] += d1*d1; s[6] += d2*d2; s[7] += d3*d3;
      s[8] += d0*d1; s[9] += d0*d2; s[10] += d0*d3;
      s[11] += d1*d2; s[12] += d1*d3; s[13] += d2*d3;
    }
    for (int k=0; k<14; ++k) { tot[k] += s[k]; }
  }
  std::printf("%llu", static_cast<unsigned long long>(n));
  for (int k=0; k<14; ++k) { std::printf(" %.17Le", tot[k]); }
  std::printf("\n");
  return 0;
}
