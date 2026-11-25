#!/usr/bin/env python3
"""Timing decks of the review (journal entry 8): the ablation decks sr256_l2 and
sr256_l0m of inputs/ablation/ without the restart output and without dumps, 60 cycles.

    python3 make_review_inputs.py     (writes inputs/card/sr256_{l2,l0m}_time.athinput)
"""
import os

import nl2

OUT = os.path.join(nl2.HERE, "inputs")


def main():
    for lev in ("l2", "l0m"):
        src = os.path.join(OUT, "ablation", f"sr256_{lev}.athinput")
        lines = open(src).read().splitlines()
        cut = next(i for i, ln in enumerate(lines) if ln.strip() == "<output1>")
        tmp = os.path.join(OUT, "card", f"sr256_{lev}_time.athinput")
        open(tmp, "w").write("\n".join(lines[:cut]).rstrip() + "\n")
        nl2.write_input(tmp, tmp, {"job/basename": f"sr256_{lev}_time", "time/nlim": 60,
                                   "scalar_field/dump_dt": -1.0})
    print("written under", os.path.join(OUT, "card"))


if __name__ == "__main__":
    main()
