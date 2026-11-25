#!/usr/bin/env python3
"""The example problems/scalar/sr_stochastic_l2.athinput parses, runs, and is the run
"sr_stochastic.athinput with noise_level = 2" byte for byte (the options it names are
the defaults of level 2).

    example_check.py --exe ATHENA --out DIR [--nlim 10]

Writes DIR/summary.json; exit status 1 on a difference."""
import argparse
import filecmp
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nl2                     # noqa: E402

SUFFIX = (".dump", ".modes", ".rmodes", ".hst")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--nlim", type=int, default=10)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    common = {"scalar_field/noise_mode_file":
              os.path.join(nl2.PROB, "sr_stochastic_modes.txt"),
              "time/nlim": a.nlim, "scalar_field/dump_dt": -1.0,
              "scalar_field/dump_dcycle": a.nlim}
    ex = nl2.write_input(os.path.join(nl2.PROB, "sr_stochastic_l2.athinput"),
                         os.path.join(out, "example.athinput"), common)
    ref = nl2.write_input(os.path.join(nl2.PROB, "sr_stochastic.athinput"),
                          os.path.join(out, "reference.athinput"),
                          {**common, "scalar_field/noise_level": 2,
                           "scalar_field/noise_rmodes_dump": "true"})
    rc = [nl2.run(a.exe, os.path.join(out, "example"), ex),
          nl2.run(a.exe, os.path.join(out, "reference"), ref)]
    da, db = os.path.join(out, "example"), os.path.join(out, "reference")
    names = sorted(f for f in os.listdir(da) if f.endswith(SUFFIX))
    same = [f for f in names if os.path.exists(os.path.join(db, f))
            and filecmp.cmp(os.path.join(da, f), os.path.join(db, f), shallow=False)]
    res = dict(exe=os.path.abspath(a.exe), exit=rc, files=len(names), identical=len(same),
               differ=[f for f in names if f not in same])
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))
    sys.exit(1 if (res["differ"] or rc != [0, 0] or not names) else 0)


if __name__ == "__main__":
    main()
