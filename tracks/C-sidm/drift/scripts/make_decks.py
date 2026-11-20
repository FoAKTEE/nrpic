#!/usr/bin/env python3
"""Decks and batch lists of the drift package (drift/JOURNAL.md entry 2).

    python3 make_decks.py

(i), (iii)  cc2_kninf_M8, cc1_kninf_M8: the wave-2 control decks
            ../../threshold_scan/inputs/cc{2,1}_kninf.athinput with one more refinement
            level, a level-7 region inside |x|_inf < 3.9 M (cells of M/8; the mesh leg of
            ../../threshold_scan/SCAN.md block B), 300 M. Output cadence in time kept:
            the step halves (cfl 0.25 on M/8), so the cycle counts of the history (8), the
            constraint statistics (32), the trajectories with metric (800, every 25 M) and
            ndiag (1600) double; restart files every 100 M (a job cut by the queue can be
            continued). Everything else, particles and table included, is the wave-2 deck.
(ii), (iv)  cc2_kninf_A1000, cc1_kninf_A1000: continuation A' of SCAN.md, restart of the
            wave-2 runs from rst/cc.00001.rst (+ .prt), written at t = 300 M, to
            time/tlim = 1000. The batch launcher passes a file ending in .rst to athena as
            -r (scripts/gpu_run.sh); the restart files are only read, so they are named in
            place instead of copied, and the new output directory holds the continuation.
            The executable must be the wave-2 one (sha256 f9f2dc12...; the release card
            executable .work/build_gpu_v03/src/athena is byte-identical, JOURNAL entry 1).

(v)         cc2_kninf_N1e4 (optional particle-number leg): the wave-2 deck of cc2_kninf with
            the N = 1e4 file of wave 1, M/4 mesh, 300 M.

Every list line ends with `-t 00:52:00`: athena stops by itself before the Slurm limit
(55 min) and writes all outputs, a restart file included.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
TRACK = os.path.normpath(os.path.join(PKG, ".."))
WT = os.path.normpath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "threshold_scan"))
import make_decks as D  # noqa: E402  (set_key)

SCRATCH = "/data/haiyangw/nrpic/scratch/C-sidm"
WAVE2 = {"cc1": ("C-20261115-171058-c26cfad", "cc1_kninf"), "cc2": ("C-20261115-171059-4b70228", "cc2_kninf")}
WALL = "00:52:00"
REGION7 = """<refined_region2>
level = 7          # drift package: cells of M/8 inside |x|_inf < 3.9 M (SCAN.md block B, mesh leg)
x1min = -3.9
x1max = 3.9
x2min = -3.9
x2max = 3.9
x3min = -3.9
x3max = 3.9

"""


def m8_deck(mk):
    src = os.path.join(TRACK, "threshold_scan", "inputs", f"{mk}_kninf.athinput")
    text = open(src).read()
    head = (f"# drift {mk}_kninf_M8: {mk}_kninf of threshold_scan (wave-2 control, run "
            f"{WAVE2[mk][0]}) with a level-7 region (dx = M/8) inside |x|_inf < 3.9 M.\n"
            f"# Written by tracks/C-sidm/drift/scripts/make_decks.py from "
            f"{os.path.relpath(src, WT)}; do not edit by hand.\n")
    text = head + "\n".join(text.split("\n")[3:])   # the source's own three header lines dropped
    assert "<refined_region2>" not in text
    text = text.replace("<time>", REGION7 + "<time>", 1)
    text = D.set_key(text, "comment", "problem", f"King cluster {mk}_kninf_M8")
    text = D.set_key(text, "time", "ndiag", "1600")
    text = D.set_key(text, "particles", "hist_dcycle", "8", "every 0.25 M at dt = M/32")
    text = D.set_key(text, "particles", "cstat_dcycle", "32")
    text = D.set_key(text, "particles", "traj_dcycle", "800", "every 25 M at dt = M/32")
    text = D.set_key(text, "output2", "dt", "100")
    return text


def n1e4_deck(mk="cc2"):
    """Particle-number leg (optional, step 6 of the package): the wave-2 control deck with
    the N = 1e4 files of wave 1 (run C-sidm-20261115-120610-b4592be; same model, same seed,
    byte-identical table), M/4 mesh."""
    src = os.path.join(TRACK, "threshold_scan", "inputs", f"{mk}_kninf.athinput")
    text = open(src).read()
    tag = {"cc1": "king_y0p33403", "cc2": "king_y0p31400"}[mk]
    ic = os.path.join(SCRATCH, "C-sidm-20261115-120610-b4592be", f"{tag}_stratified_N10000_s1")
    head = (f"# drift {mk}_kninf_N1e4: {mk}_kninf of threshold_scan with the N = 1e4 particle file of wave 1\n"
            f"# (run C-sidm-20261115-120610-b4592be). Written by tracks/C-sidm/drift/scripts/make_decks.py from "
            f"{os.path.relpath(src, WT)}; do not edit by hand.\n")
    text = head + "\n".join(text.split("\n")[3:])
    text = D.set_key(text, "comment", "problem", f"King cluster {mk}_kninf_N1e4")
    text = D.set_key(text, "particles", "particle_file", ic + ".nrp")
    text = D.set_key(text, "particles", "traj_ntrack", "10000", "all particles")
    text = D.set_key(text, "problem", "comp0_file", ic + ".tab")
    return text


def main():
    out = os.path.join(PKG, "inputs")
    os.makedirs(out, exist_ok=True)
    rel = os.path.relpath(out, WT)
    for mk in ("cc2", "cc1"):
        name = f"{mk}_kninf_M8"
        with open(os.path.join(out, name + ".athinput"), "w") as f:
            f.write(m8_deck(mk))
        print("wrote", name)
    with open(os.path.join(out, "cc2_kninf_N1e4.athinput"), "w") as f:
        f.write(n1e4_deck("cc2"))
    print("wrote cc2_kninf_N1e4")
    jobs = {
        "job_i": ("cc2_kninf_M8", f"{rel}/cc2_kninf_M8.athinput", []),
        "job_ii": ("cc2_kninf_A1000", os.path.join(SCRATCH, WAVE2["cc2"][0], WAVE2["cc2"][1], "rst", "cc.00001.rst"),
                   ["time/tlim=1000"]),
        "job_iii": ("cc1_kninf_M8", f"{rel}/cc1_kninf_M8.athinput", []),
        "job_iv": ("cc1_kninf_A1000", os.path.join(SCRATCH, WAVE2["cc1"][0], WAVE2["cc1"][1], "rst", "cc.00001.rst"),
                   ["time/tlim=1000"]),
        "job_v": ("cc2_kninf_N1e4", f"{rel}/cc2_kninf_N1e4.athinput", []),
    }
    for job, (name, inp, args) in jobs.items():
        with open(os.path.join(out, f"{job}.list"), "w") as f:
            f.write(f"# drift card {job}: <name> <athinput | restart file> [athena args], one run per job\n")
            f.write(" ".join([name, inp] + args + ["-t", WALL]) + "\n")
        print("wrote", job)
    return 0


if __name__ == "__main__":
    sys.exit(main())
