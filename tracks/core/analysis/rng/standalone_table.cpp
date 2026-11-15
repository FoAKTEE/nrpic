// Standalone table of the random-number interface (no AthenaK, no Kokkos), in the format
// of the problem generator rng_test: used to show that the draws do not depend on the
// compiler options (optimisation level, fused multiply-add allowed or not).
//
//   standalone_table <key file> <table file>
//
// Build: g++ -std=c++17 <options> -DNRPIC_STANDALONE -I athenak/src standalone_table.cpp

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#include "utils/rng.hpp"

int main(int argc, char *argv[]) {
  if (argc != 3) {
    std::fprintf(stderr, "usage: standalone_table <key file> <table file>\n");
    return 2;
  }
  std::FILE *fp = std::fopen(argv[1], "rb");
  char magic[9] = {0};
  std::int64_t n64 = 0;
  if (fp == nullptr || std::fread(magic, 1, 8, fp) != 8 ||
      std::strncmp(magic, "NRRNGKY1", 8) != 0 ||
      std::fread(&n64, sizeof(std::int64_t), 1, fp) != 1 || n64 <= 0) {
    std::fprintf(stderr, "bad key file\n");
    return 1;
  }
  const size_t nk = static_cast<size_t>(n64);
  std::vector<std::uint64_t> keys(6*nk), ints(6*nk);
  std::vector<double> reals(9*nk);
  if (std::fread(keys.data(), sizeof(std::uint64_t), keys.size(), fp) != keys.size()) {
    std::fprintf(stderr, "key file is truncated\n");
    return 1;
  }
  std::fclose(fp);
  long nbad = 0;
  for (size_t i=0; i<nk; ++i) {
    const std::uint64_t *k = &keys[6*i];
    const rng::Key key{k[0], k[1], k[2], k[4], k[3]};
    const std::uint64_t draw = k[5];
    std::uint64_t w[4];
    rng::Bits4(key, draw, w);
    for (int n=0; n<4; ++n) { ints[6*i+n] = w[n]; }
    ints[6*i+4] = rng::Index(key, draw, 1000003ULL);
    ints[6*i+5] = rng::MulHi64(w[0], w[1]);
    if (ints[6*i+5] != rng::MulHi64Portable(w[0], w[1])) { ++nbad; }
    double u[4], z[2], d[3];
    rng::Uniform4(key, draw, u);
    rng::Normal2(key, draw, z);
    rng::Direction(key, draw, d);
    for (int n=0; n<4; ++n) { reals[9*i+n] = u[n]; }
    reals[9*i+4] = z[0]; reals[9*i+5] = z[1];
    reals[9*i+6] = d[0]; reals[9*i+7] = d[1]; reals[9*i+8] = d[2];
  }
  if (nbad != 0) {
    std::fprintf(stderr, "MulHi64 disagrees with the portable product %ld times\n", nbad);
    return 1;
  }
  fp = std::fopen(argv[2], "wb");
  if (fp == nullptr) { return 1; }
  std::fwrite("NRRNGTB1", 1, 8, fp);
  std::fwrite(&n64, sizeof(std::int64_t), 1, fp);
  std::fwrite(keys.data(), sizeof(std::uint64_t), keys.size(), fp);
  std::fwrite(ints.data(), sizeof(std::uint64_t), ints.size(), fp);
  std::fwrite(reals.data(), sizeof(double), reals.size(), fp);
  std::fclose(fp);
  return 0;
}
