#!/usr/bin/env python3
"""Write the input of passage P1b: P1's input (tracks/F-hills/nr_first/inputs/p1_q4.athinput,
run F-20261119-150017-b45ec5f) with the members at the resolution chosen by binary_conv.

  R16n  root 64^3 on +-256, 11 levels: members at level 10 (m/16), heavy hole at level 7
        (M/16), wave zone unchanged (cells 2 within 48, 4 within 100); 3000 MeshBlock slots
        (g2mesh card test F-20261120-222810-e408386: 3000 slots ran at 78785 MiB of 81920 with
        three finders; tree maximum 2864 along the Newtonian tracks to 280 M, model run
        F-20261120-222426-86392c3).
  R12   root 96^3, 10 levels: every cell 2/3 of P1 (members m/12, heavy M/12, wave zone 4/3 and
        8/3); 3000 slots (model maximum 2750).
Everything else is P1's: data, gauge (constant shift_eta = 2), outputs, tlim 280. The <problem>
block is copied unchanged, so P1's t = 0 constraint check (nr_first E2) applies.

Usage: make_p1b.py R16n|R12 <out.athinput>
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
P1 = os.path.join(WT, "tracks/F-hills/nr_first/inputs/p1_q4.athinput")

RES = {"R16n": dict(nx=64, levels=11, slots=3000, tag="m/16"),
       "R12": dict(nx=96, levels=10, slots=3000, tag="m/12")}


def main():
    res, out = sys.argv[1], sys.argv[2]
    c = RES[res]
    src = open(P1).read()
    body = src[src.index("\n<comment>\n") + 1:]
    body = re.sub(r"(nx[123]\s*=\s*)64", lambda m: m.group(1) + str(c["nx"]), body)
    body = re.sub(r"num_levels\s*=\s*10", f"num_levels          = {c['levels']}", body)
    body = re.sub(r"max_nmb_per_rank\s*=\s*2700[^\n]*", f"max_nmb_per_rank    = {c['slots']}", body)
    body = re.sub(r"problem\s*=\s*Hills passage P1[^\n]*",
                  f"problem   = Hills passage P1b, q = 4, a_b = 5, r_p = 9.8, members {c['tag']} "
                  "(binary_conv; prepared, not submitted)", body)
    body = body.replace("# full fields once at the start, for the constraint check of the data (run R0)\n",
                        "# full fields once at the start\n")
    head = (f"# Passage P1b of F-hills (binary_conv, wave 3 batch 3): P1 with the members at "
            f"{c['tag']} ({res}).\n"
            f"# Written by tracks/F-hills/binary_conv/scripts/make_p1b.py from "
            f"tracks/F-hills/nr_first/inputs/p1_q4.athinput;\n"
            f"# only <comment>, the root cells (nx = {c['nx']}), num_levels ({c['levels']}) and "
            f"max_nmb_per_rank ({c['slots']}) differ.\n"
            "# Data, gauge (constant shift_eta = 2), extraction, outputs and tlim 280 are P1's.\n"
            "# Chain it with tracks/F-hills/binary_conv/scripts/athena_keep_trackers_bc.sh "
            "(binary_conv README, P1b).\n\n")
    for k in ("nx1", "nx2", "nx3"):
        assert re.search(rf"{k}\s*=\s*{c['nx']}\b", body), k
    assert f"num_levels          = {c['levels']}" in body
    with open(out, "w") as f:
        f.write(head + body)


if __name__ == "__main__":
    main()
