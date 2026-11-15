#!/usr/bin/env python3
"""Agreement of all implementations of the random-number interface on a table of keys.

Compiles standalone_table.cpp with several compiler options, evaluates the key file
with each executable, and then compares these tables and the tables given on the command
line (written by the problem generator rng_test on processors and on a card) with each
other, with the Python twin and with numpy.random.Philox (compare_table.py).

Usage: run_agreement.py --keys KEYS.bin TABLE.bin [TABLE.bin ...]
Runs in the current directory; writes agreement.json; exit status 0 only if nothing
differs.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

VARIANTS = {
    "O0": ["-O0"],
    "O2": ["-O2"],
    "O3_native_fma": ["-O3", "-march=native", "-ffp-contract=fast"],
    "O3_native_nofma": ["-O3", "-march=native", "-ffp-contract=off"],
    "O2_m32bit_products": ["-O2", "-U__SIZEOF_INT128__"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", required=True)
    ap.add_argument("tables", nargs="+")
    args = ap.parse_args()
    src = os.path.join(HERE, "standalone_table.cpp")
    tables = list(args.tables)
    built = {}
    for name, flags in VARIANTS.items():
        exe = os.path.abspath(f"standalone_{name}")
        cmd = ["g++", "-std=c++17"] + flags + ["-DNRPIC_STANDALONE", "-I",
                                               os.path.join(REPO, "athenak", "src"),
                                               src, "-o", exe]
        subprocess.run(cmd, check=True)
        out = os.path.abspath(f"table_{name}.bin")
        subprocess.run([exe, args.keys, out], check=True)
        dis = subprocess.run(["objdump", "-d", exe], capture_output=True, text=True).stdout
        built[name] = {"flags": flags, "table": out,
                       "fused_multiply_add_instructions": dis.count("vfmadd")
                       + dis.count("vfnmadd") + dis.count("vfmsub")
                       + dis.count("vfnmsub"),
                       "wide_multiply_instructions": dis.count("mulx") + dis.count("mulq")
                       + dis.count("\tmul ")}
        tables.append(out)
    proc = subprocess.run([sys.executable, os.path.join(HERE, "compare_table.py"),
                           "--numpy", "20000", "--json", "compare.json"] + tables)
    res = json.load(open("compare.json"))
    res["standalone"] = built
    with open("agreement.json", "w") as fp:
        json.dump(res, fp, indent=1)
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
