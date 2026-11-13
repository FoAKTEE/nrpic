#!/usr/bin/env python3
"""Remove the net momentum of an existing particle file in place.

    zero_momentum.py file.nrp [file2.nrp ...]

u_i -> u_i - sum(m u_i)/sum(m).  A sample of N particles carries a net momentum of
order sqrt(<u^2>/N) per unit mass, which makes the cluster drift across the mesh
(0.2 M in 300 M for N = 10^4 at y_c = 0.819).  make_ic.py applies the same shift
by default; this tool is for files written before that.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "python"))
from nrpic import io as nio  # noqa: E402


def main(paths):
    for path in paths:
        x, u, m, sp = nio.read_nrp(path)
        before = (m[:, None] * u).sum(0)
        u = u - before / m.sum()
        after = (m[:, None] * u).sum(0)
        nio.write_nrp(path, x, u, m, sp)
        print(f"{path}: N = {len(m)}, sum m u = "
              + " ".join(f"{v:+.3e}" for v in before) + "  ->  "
              + " ".join(f"{v:+.1e}" for v in after))


if __name__ == "__main__":
    main(sys.argv[1:])
