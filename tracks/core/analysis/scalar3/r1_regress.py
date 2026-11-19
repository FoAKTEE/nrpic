#!/usr/bin/env python3
"""Test R of tracks/core/JOURNAL-scalar3.md: existing behaviour is unchanged.

    python3 r1_regress.py --release EXE --scalar2 EXE --new EXE [--out DIR] [--workers 6]

Part a: the ten scalar-field cases of wave 1 with the executable of release core-v0.3 and
with the new one, every output file compared byte by byte (t6_regress.py of the second
package; the 36 unset header bytes of mesh restart files and the recorded restart path
are masked there).
Part b: the three stochastic-inflation examples (problems/scalar/sr_stochastic,
usr_stochastic, sr_stochastic_gauge; 32^3, 20 steps, records every step, dumps at cycles
0, 10, 20, mesh restart file at cycle 10 and a run restarted from it) with the published
executable of branch core/scalar-2 and with the new one: every file byte by byte.
Writes DIR/summary.json; exit status 1 if a file differs."""
import argparse
import filecmp
import glob
import os
import subprocess
import sys

import s3
from s3 import common

T6 = os.path.join(s3.HERE, "..", "scalar2", "t6_regress.py")
EXAMPLES = {
    "sr": ("sr_stochastic.athinput", "sr_stochastic_modes.txt"),
    "usr": ("usr_stochastic.athinput", "usr_stochastic_modes.txt"),
    "srg": ("sr_stochastic_gauge.athinput", "sr_stochastic_modes.txt"),
}
RST_BLOCK = ["<output9>", "file_type=rst", "dcycle=10"]


def compare(da, db):
    """Files of two run directories: (identical, differing, missing)."""
    names = set()
    for d in (da, db):
        for root, _, files in os.walk(d):
            for f in files:
                names.add(os.path.relpath(os.path.join(root, f), d))
    same, diff, miss = [], [], []
    for n in sorted(names):
        if n == "athena.log":
            continue
        fa, fb = os.path.join(da, n), os.path.join(db, n)
        if not (os.path.exists(fa) and os.path.exists(fb)):
            miss.append(n)
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(n)
        elif n.endswith(".rst"):
            sys.path.insert(0, os.path.dirname(T6))
            import t6_regress
            ok, note = t6_regress.rst_equal(fa, fb)
            (same if ok else diff).append(n + " [" + note + "]")
        else:
            diff.append(n)
    return same, diff, miss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", required=True)
    ap.add_argument("--scalar2", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--skip-a", action="store_true")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    summ = dict(release=os.path.abspath(a.release), scalar2=os.path.abspath(a.scalar2),
                new=os.path.abspath(a.new))
    ok = True
    # ---- part a
    if not a.skip_a:
        p = subprocess.run([sys.executable, T6, "--base", a.release, "--new", a.new,
                            "--out", os.path.join(out, "t6"), "--workers",
                            str(a.workers)], stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True)
        summ["part_a_exit"] = p.returncode
        summ["part_a_tail"] = p.stdout.splitlines()[-12:]
        ok &= p.returncode == 0
    # ---- part b
    exes = dict(scalar2=os.path.abspath(a.scalar2), new=os.path.abspath(a.new))
    cases = []
    for lab, exe in exes.items():
        for k, (inp, modes) in EXAMPLES.items():
            # an input file with a restart output block, written next to the runs; the
            # dump cadence goes into the file (a parameter that the file does not carry
            # cannot be set on the command line: parameter_input.cpp, line 400)
            src = open(os.path.join(common.PROB, inp)).read()
            lines = []
            for ln in src.splitlines():
                if ln.split("=")[0].strip() == "dump_dt":
                    lines += ["dump_dt          = -1.0", "dump_dcycle      = 10"]
                else:
                    lines.append(ln)
            assert "dump_dcycle      = 10" in lines, inp
            dst = os.path.join(out, f"{k}_rst.athinput")
            with open(dst, "w") as fp:
                fp.write("\n".join(lines) + "\n\n<output9>\nfile_type = rst\ndcycle    = 10\n")
            args = [f"scalar_field/noise_mode_file={os.path.join(common.PROB, modes)}",
                    "time/nlim=20"]
            if "con_signed" in src:
                # the example sets the option of this branch: off, so that the record
                # is that of the earlier executable
                args.append("scalar_field/con_signed=false")
            cases.append((os.path.join(out, "b", k, lab), dst, args))
    walls = {}
    for lab, exe in exes.items():
        sel = [c for c in cases if c[0].endswith(os.sep + lab)]
        walls[lab] = common.run_many(exe, sel, a.workers)
        # restart from cycle 10
        for k in EXAMPLES:
            rst = sorted(glob.glob(os.path.join(out, "b", k, lab, "rst", "*.00001.rst")))
            common.run_case(exe, os.path.join(out, "b", k + "_restart", lab), rst[0],
                            ["time/nlim=20"])
    summ["part_b_wall_s"] = walls
    res = {}
    for k in list(EXAMPLES) + [x + "_restart" for x in EXAMPLES]:
        same, diff, miss = compare(os.path.join(out, "b", k, "scalar2"),
                                   os.path.join(out, "b", k, "new"))
        res[k] = dict(identical=len(same), differ=diff, missing=miss,
                      masked=[x for x in same if "[" in x])
        ok &= not diff and not miss
    summ["part_b"] = res
    summ["ok"] = bool(ok)
    common.dump_json(summ, os.path.join(out, "summary.json"))
    print("R", "passed" if ok else "FAILED", os.path.join(out, "summary.json"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
