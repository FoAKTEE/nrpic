#!/usr/bin/env python3
"""Regression L: linear growth at one wavelength in a matter-dominated universe, on a card.

Short version of the C1 run of the cosmology extension (cosmo/TESTLOG.md, "C1:
constraint-solved initial data" and "C1 result: linear regime to a = 100", run
runs/cosmo/east_d1e-4_n32_cpu): the data of East, Wojtak & Pretorius at amplitude 1e-4,
32^3 cells, shifted lattice of 32^3 particles, two compensated filter passes, to
t = 9 (a = 30.25) instead of t = 18 (a = 100). Input problems/cosmo/east.athinput.

    python3 run.py --prepare      # new run id: constraint-solved data, manifest; batch line
    python3 judge.py <run_id>
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

INPUT = lib.WT / "problems" / "cosmo" / "east.athinput"
OLD = lib.OLD_RUNS / "cosmo" / "east_d1e-4_n32_cpu"
TLIM = 9.0
ARGS = [f"time/tlim={TLIM}"]


def read_doubles(path):
    """The double-precision payload of an NRPIC001 particle file (x, u, m records) or an
    NRCOSMO1 field file (psi, K, alpha, Ahat), formats of cosmo/ic/nrp_io.py."""
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic == b"NRPIC001":
            n = int(np.frombuffer(f.read(8), dtype="<i8")[0])
            return np.fromfile(f, dtype="<f8", count=7 * n)
        if magic == b"NRCOSMO1":
            n1, n2, n3 = np.frombuffer(f.read(24), dtype="<i8")
            return np.fromfile(f, dtype="<f8", count=9 * int(n1 * n2 * n3))
    raise ValueError(f"unknown format: {path}")


def max_abs_diff(a, b):
    x, y = read_doubles(a), read_doubles(b)
    if x.size != y.size:
        return None
    return float(np.max(np.abs(x - y)))


def prepare():
    run_id = lib.new_run_id()
    out = lib.run_dir(run_id)
    gen = ["python3", str(lib.WT / "cosmo" / "ic" / "make_east.py"), "--delta", "1e-4",
           "--n", "32", "--ppc", "1", "--nfilter", "2", "--compensate", "--out", str(out)]
    subprocess.run(gen, cwd=str(lib.WT), check=True, stdout=subprocess.DEVNULL)
    ic = {}
    for f in ("particles.nrp", "fields.bin"):
        new, old = out / f, OLD / f
        ic[f] = dict(new=lib.sha256(new), earlier=lib.sha256(old),
                     identical=lib.sha256(new) == lib.sha256(old),
                     max_abs_diff_as_doubles=max_abs_diff(new, old))
    line = " ".join([str(out), str(INPUT)] + ARGS)
    lib.write_manifest(
        run_id, kind="scouting", test="L linear growth",
        purpose="C3 regression of the cosmology extension: observer density contrast at "
                "amplitude 1e-4 to a = 30 against linear theory and runs/cosmo/east_d1e-4_n32_cpu",
        command=[" ".join(gen), f"scripts/gpu_batch.sh line: {line}",
                 f"athena -i {INPUT} -d {out} " + " ".join(ARGS)],
        cwd=str(out), executable=lib.exe_record(lib.EXE_GPU),
        inputs=[lib.file_record(INPUT), lib.file_record(out / "particles.nrp"),
                lib.file_record(out / "fields.bin")],
        initial_data_vs_earlier=ic,
        resources=dict(device="A100 card", cores=1), status="prepared")
    print(run_id)
    print(line)
    return run_id, line


if __name__ == "__main__":
    prepare()
