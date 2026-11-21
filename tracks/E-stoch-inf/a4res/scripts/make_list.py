#!/usr/bin/env python3
"""Writes the card list of package a4res (format of ../../ladder/inputs/jobC.list: name,
input, overrides) for the six set-ups x four members of a4lib.

    python3 make_list.py > ../inputs/card.list"""
import os

import a4lib as A

MF = os.path.join(A.TRACK, "ladder", "inputs", "modes_n4096.txt")


def main():
    print("# a4res: resolution test of the strict A4 (JOURNAL entry 2); SR, one mode file "
          "(modes_n4096.txt), seed 20261115, tlim 4.5, dump_dt 0.125, H and M_i dumped")
    for s in A.SETUPS:
        n = s["N"]
        for mem, scale in A.MEMBERS:
            ov = [f"mesh/nx{i}={n}" for i in (1, 2, 3)] + \
                 [f"meshblock/nx{i}={n}" for i in (1, 2, 3)] + \
                 [f"scalar_field/noise_nmax2={s['nmax2']}",
                  f"scalar_field/noise_mode_file={MF}",
                  f"scalar_field/noise_mode_scale={scale}",
                  f"time/tlim={A.TLIM}", f"scalar_field/dump_dt={A.DUMP_DT}",
                  "scalar_field/dump_metric=false", "scalar_field/dump_constraints=true"]
            print(" ".join([A.run_name(s, mem), A.BASE_INPUT] + ov))


if __name__ == "__main__":
    main()
