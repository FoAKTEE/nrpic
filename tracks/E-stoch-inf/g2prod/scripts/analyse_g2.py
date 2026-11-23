#!/usr/bin/env python3
"""Analysis of the g2prod chains (E-stoch-inf, gate G2) with the readers and metrics of
usr/scripts/analyse_cards.py, unchanged; this file only adds the groups of g2prod and maps
each chain directory (outputs directly in the run directory) to a run name.

    python3 analyse_g2.py --group g2a --map U256=<ap dir> --map U256m=<am dir> \
        --map U256h=<hp dir> --map U256hm=<hm dir> --ref ../../usr/results --out OUT --workers 3
    python3 analyse_g2.py --group u256 --map U256=<bp dir> --map U256m=<bm dir> ...   (seed B)
    python3 analyse_g2.py --group u320 --map U256=<U320ap dir> --map U256m=<U320am dir> ...

The map is realised as symbolic links OUT/links/<name> -> <dir>, so that analyse_cards.main()
finds <run>/<name>/usr.sf.con.hst as for the batch runs. Groups:
  g2a  seed A at s = +1, -1, +1/2, -1/2: pairs (U256, U256m), (U256h, U256hm), halving
       U256 over U256h (SCOPE 4c U-A2', U-A3, U-A4'(a)-(c)); one-point statistics.
  u256 the pair of analyse_cards (seed B: U-S with one-point statistics).
  u320 the pair at 320^3 without one-point statistics (U-R).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "usr", "scripts"))
import analyse_cards as ac  # noqa: E402

ac.GROUPS["g2a"] = dict(runs={"U256": 1.0, "U256m": -1.0, "U256h": 0.5, "U256hm": -0.5}, nmax2=4096,
                        pairs=[("U256", "U256m"), ("U256h", "U256hm")], halving=[("U256", "U256h")],
                        ladder=[], kmask=32.0, onepoint=True)
ac.GROUPS["u320"] = dict(runs={"U256": 1.0, "U256m": -1.0}, nmax2=4096, pairs=[("U256", "U256m")],
                         halving=[], ladder=[], kmask=32.0, onepoint=False)


def main():
    argv = sys.argv[1:]
    maps, rest, i = [], [], 0
    while i < len(argv):
        if argv[i] == "--map":
            maps.append(argv[i + 1])
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    out = rest[rest.index("--out") + 1]
    links = os.path.join(out, "links")
    os.makedirs(links, exist_ok=True)
    for m in maps:
        name, d = m.split("=", 1)
        p = os.path.join(links, name)
        if not os.path.islink(p):
            os.symlink(os.path.abspath(d), p)
        print(f"map {name} -> {os.path.realpath(p)}", flush=True)
    sys.argv = [sys.argv[0]] + rest + ["--run", links]
    ac.main()


if __name__ == "__main__":
    main()
