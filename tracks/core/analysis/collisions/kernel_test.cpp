// Unit test of the kernels of athenak/src/particles/nrpic_collide.hpp outside the code:
//   g++ -std=c++17 -DNRPIC_STANDALONE -I<repo>/athenak/src kernel_test.cpp -o kernel_test
// Reads lines of nine doubles (u_a, u_b, nhat; hexadecimal or decimal) from the standard
// input and writes for each: g1 = gamma_rel - 1, the Moller speed, W_a, W_b, u_a', u_b'
// as hexadecimal doubles.  Driver: run_kernel_test.py.
#include <cstdio>
#include <cstdlib>

#include "particles/nrpic_collide.hpp"

int main() {
  char line[1024];
  while (std::fgets(line, sizeof(line), stdin) != nullptr) {
    double v[9];
    char *p = line;
    bool ok = true;
    for (int i=0; i<9; ++i) {
      char *end = nullptr;
      v[i] = std::strtod(p, &end);
      if (end == p) { ok = false; break; }
      p = end;
    }
    if (!ok) continue;
    const double ua[3] = {v[0], v[1], v[2]}, ub[3] = {v[3], v[4], v[5]};
    const double nh[3] = {v[6], v[7], v[8]};
    double wa, wb, uan[3], ubn[3];
    const double g1 = nrpic::CollGammaRelM1(ua, ub, wa, wb);
    const double vm = nrpic::CollMoller(g1, wa, wb);
    nrpic::CollScatter(ua, ub, wa, wb, g1, nh, uan, ubn);
    std::printf("%a %a %a %a %a %a %a %a %a %a\n", g1, vm, wa, wb, uan[0], uan[1], uan[2],
                ubn[0], ubn[1], ubn[2]);
  }
  return 0;
}
