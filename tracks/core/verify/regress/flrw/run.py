#!/usr/bin/env python3
"""Regression F: homogeneous matter-dominated universe in conformal time, on a card.

The C0 test of the cosmology extension (cosmo/TESTLOG.md, "C0, first test: homogeneous
dust universe", run runs/cosmo/flrw_n32_cpu_sd): 32^3 cells, 32^3 lattice particles at
rest, H_0 = 1, box 4, lapse condition d_t alpha = -(1/3) alpha^2 K, zero shift,
density-form sources, to t = 2 (a = 4). Input problems/cosmo/flrw.athinput as it stands.

    python3 run.py --prepare      # new run id: particles, manifest; prints the batch line
    python3 judge.py <run_id>
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

INPUT = lib.WT / "problems" / "cosmo" / "flrw.athinput"
OLD = lib.OLD_RUNS / "cosmo" / "flrw_n32_cpu_sd"
ARGS = []


def prepare():
    run_id = lib.new_run_id()
    out = lib.run_dir(run_id)
    gen = ["python3", str(lib.WT / "cosmo" / "ic" / "make_lattice.py"), "--n", "32",
           "--ppc", "1", "--L", "4", "--H0", "1", "--out", str(out)]
    subprocess.run(gen, cwd=str(lib.WT), check=True, stdout=subprocess.DEVNULL)
    new, old = out / "particles.nrp", OLD / "particles.nrp"
    ic = dict(new=lib.sha256(new), earlier=lib.sha256(old),
              identical=lib.sha256(new) == lib.sha256(old))
    line = " ".join([str(out), str(INPUT)] + ARGS)
    lib.write_manifest(
        run_id, kind="scouting", test="F homogeneous universe",
        purpose="C3 regression of the cosmology extension: homogeneous dust universe to a = 4 "
                "against the exact solution and runs/cosmo/flrw_n32_cpu_sd",
        command=[" ".join(gen), f"scripts/gpu_batch.sh line: {line}",
                 f"athena -i {INPUT} -d {out} " + " ".join(ARGS)],
        cwd=str(out), executable=lib.exe_record(lib.EXE_GPU),
        inputs=[lib.file_record(INPUT), lib.file_record(new)],
        initial_data_vs_earlier=ic,
        resources=dict(device="A100 card", cores=1), status="prepared")
    print(run_id)
    print(line)
    return run_id, line


if __name__ == "__main__":
    prepare()
