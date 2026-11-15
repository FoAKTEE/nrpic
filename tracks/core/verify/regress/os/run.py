#!/usr/bin/env python3
"""Regression O: Oppenheimer-Snyder dust collapse, R_0 = 5 M, 9328 lattice particles
with the surface-corrected masses, adaptive mesh, cloud at the finest level, on a card.

Short version of the earlier run runs/os/nocap_sc (docs/TESTLOG.md, "Dust collapse with
corrected initial data, cloud at the finest level"; paper/sections/tables/tab_outcomes.tex,
table tab:outcomes_dust): to t = 25 M instead of 60 M, which covers the first apparent
horizon (16.39 M), the removal of all macroparticles and six M after it.

    python3 run.py --prepare      # new run id: initial data, manifest; prints the batch line
    python3 judge.py <run_id>

Initial data are regenerated with the current problems/ic/make_ic.py and compared, by
checksum, with those of the earlier run. Restart dumps are switched off (output2/dt)
because a dump of this mesh is about 1 GB.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

INPUT = lib.WT / "problems" / "os" / "os_amr.athinput"
OLD = lib.OLD_RUNS / "os" / "nocap_sc"
STEM = "os_R5_lattice_N9328_s1"
TLIM = 25.0
ARGS = [f"time/tlim={TLIM}", "particles/deposit_adaptive=false", "output2/dt=1.0e6"]


def prepare():
    run_id = lib.new_run_id()
    out = lib.run_dir(run_id)
    gen = ["python3", str(lib.WT / "problems" / "ic" / "make_ic.py"), "os", "--nlat", "26",
           "--sampler", "lattice", "--lattice-surface-correction", "--prefix", STEM,
           "--out", str(out)]
    subprocess.run(gen, cwd=str(lib.WT), check=True, stdout=subprocess.DEVNULL)
    ic = {}
    for ext in ("nrp", "tab"):
        new, old = out / f"{STEM}.{ext}", OLD / f"{STEM}.{ext}"
        ic[ext] = dict(new=lib.sha256(new), earlier=lib.sha256(old),
                       identical=lib.sha256(new) == lib.sha256(old))
    line = " ".join([str(out), str(INPUT)] + ARGS)
    lib.write_manifest(
        run_id, kind="scouting", test="O Oppenheimer-Snyder collapse",
        purpose="C3 regression: horizon mass of the dust collapse (9328 lattice particles, "
                "corrected masses, cloud at the finest level) to t = 25 M against runs/os/nocap_sc",
        command=[" ".join(gen), f"scripts/gpu_batch.sh line: {line}",
                 f"athena -i {INPUT} -d {out} " + " ".join(ARGS)],
        cwd=str(out), executable=lib.exe_record(lib.EXE_GPU),
        inputs=[lib.file_record(INPUT), lib.file_record(out / f"{STEM}.nrp"),
                lib.file_record(out / f"{STEM}.tab")],
        initial_data_vs_earlier=ic,
        resources=dict(device="A100 card", cores=1), status="prepared")
    print(run_id)
    print(line)
    return run_id, line


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", action="store_true")
    a = ap.parse_args()
    prepare()
