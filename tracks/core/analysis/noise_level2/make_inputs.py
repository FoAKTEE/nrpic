#!/usr/bin/env python3
"""Input files of package noise-level2 (written into inputs/ next to this script):

  card/{sr,usr}64_l{0,2}.athinput   T5, card smoke at 64^3 (nmax2 = 256): the examples
      problems/scalar/sr_stochastic.athinput (to t = 8.44, 8 e-folds) and
      usr_stochastic.athinput (to its tlim) with the mode files up to |n|^2 = 4096 of
      Track E (ladder/inputs/modes_n4096.txt, usr/inputs/modes_usr_n4096.txt), level 0 as
      released and level 2
  ablation/{sr,usr}256_{l0m,l1m,l2}.athinput   the ablation of arXiv:2512.14649 Fig. 9 at
      256^3 for Track E: Track E's own set-up (repro/scope/inputs/{sr,usr}_paper.athinput
      of branch track/E-stoch-inf, read from its worktree), with R on the mesh at levels 0
      and 1 (noise_mode_eq = mesh) and level 2, nothing else changed

    python3 make_inputs.py
"""
import os

import nl2

E = "/data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf"
MODES = {"sr": os.path.join(E, "ladder", "inputs", "modes_n4096.txt"),
         "usr": os.path.join(E, "usr", "inputs", "modes_usr_n4096.txt")}
OUT = os.path.join(nl2.HERE, "inputs")


def main():
    os.makedirs(os.path.join(OUT, "card"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "ablation"), exist_ok=True)
    mesh = {f"{b}/nx{d}": 64 for b in ("mesh", "meshblock") for d in (1, 2, 3)}
    for case, src in (("sr", "sr_stochastic.athinput"), ("usr", "usr_stochastic.athinput")):
        base = {**mesh, "scalar_field/noise_nmax2": 256,
                "scalar_field/noise_mode_file": MODES[case]}
        if case == "sr":
            base["time/tlim"] = 8.44
        for lev, extra in (("l0", {}), ("l2", {"scalar_field/noise_level": 2})):
            nl2.write_input(os.path.join(nl2.PROB, src),
                            os.path.join(OUT, "card", f"{case}64_{lev}.athinput"),
                            {**base, **extra})
    for case in ("sr", "usr"):
        src = os.path.join(E, "repro", "scope", "inputs", f"{case}_paper.athinput")
        for lev, extra in (("l0m", {"scalar_field/noise_level": 0,
                                    "scalar_field/noise_mode_eq": "mesh"}),
                           ("l1m", {"scalar_field/noise_level": 1,
                                    "scalar_field/noise_mode_eq": "mesh"}),
                           ("l2", {"scalar_field/noise_level": 2})):
            nl2.write_input(src, os.path.join(OUT, "ablation", f"{case}256_{lev}.athinput"),
                            {**extra, "job/basename": f"{case}256_{lev}"})
    print("written under", OUT)


if __name__ == "__main__":
    main()
