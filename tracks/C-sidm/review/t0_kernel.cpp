// T0 of collide/TESTS.md on core's committed kernel header (lead review of C-sidm).
// Reads lines "ua0 ua1 ua2 ub0 ub1 ub2 n0 n1 n2" (hexadecimal doubles) from stdin and
// prints u_a', u_b', g1, v_Mol in hexadecimal. Compiled against nrpic_collide.hpp taken
// with `git show <commit>:athenak/src/particles/nrpic_collide.hpp` (t0_kernel.py).
#define NRPIC_STANDALONE
#include <cstdio>
#include <cstdlib>
#include "nrpic_collide.hpp"
int main() {
  char buf[9][64];
  while (std::scanf("%63s %63s %63s %63s %63s %63s %63s %63s %63s", buf[0], buf[1], buf[2],
                    buf[3], buf[4], buf[5], buf[6], buf[7], buf[8]) == 9) {
    double ua[3], ub[3], nh[3], uan[3], ubn[3], wa, wb;
    for (int i = 0; i < 3; ++i) {
      ua[i] = std::strtod(buf[i], nullptr);
      ub[i] = std::strtod(buf[3 + i], nullptr);
      nh[i] = std::strtod(buf[6 + i], nullptr);
    }
    const double g1 = nrpic::CollGammaRelM1(ua, ub, wa, wb);
    const double vm = nrpic::CollMoller(g1, wa, wb);
    nrpic::CollScatter(ua, ub, wa, wb, g1, nh, uan, ubn);
    std::printf("%a %a %a %a %a %a %a %a\n", uan[0], uan[1], uan[2], ubn[0], ubn[1], ubn[2],
                g1, vm);
  }
  return 0;
}
