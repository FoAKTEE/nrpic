#!/usr/bin/env python3
"""Demonstration of the reproducible random numbers inside the code (docs/RNG.md).

Runs the test kick of ``athenak/src/particles/nrpic_kick.cpp`` on the existing
test-particle set-ups and compares the particle states bit by bit:

  --case analytic   D1, problems/tests/rng_kick_analytic.athinput (analytic metric):
      a0  no kick                      a1  key tag, one MeshBlock
      a2  key tag, 64 MeshBlocks       a3  a1 restarted halfway
      b1, b2  control key "block" on the two layouts
      s1, s3  control key "sequence", uninterrupted and restarted
      d1  key tag, another seed
      n1, n2, n3  mode "direction": two layouts and the restart
  --case mesh       D2, problems/tests/rng_kick_mesh.athinput (metric on the mesh):
      m1, m2  key tag on two layouts   m3, m4  the same without the kick
      m5, m6  plunging particles (removed at the lapse threshold), uninterrupted to
              t = 50 and restarted from t = 40

The script runs in the current directory, writes one sub-directory per run and
``summary.json``; with --ref DIR it also compares the checksums of the kicks with those
of another execution of the same case (another build). Exit status 0 only if every
comparison has the expected outcome.

Usage: run_kick_demo.py --exe ATHENA --case analytic|mesh [--np N] [--tlim T] [--ref DIR]
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def read_snapshot(path):
    """Snapshot of the particle module, sorted by tag: time, cycle, tags, records
    (N x 8: x^i, u_i, m, proper time)."""
    with open(path, "rb") as fp:
        raw = fp.read()
    if raw[:8] != b"NRPSNAP1":
        raise ValueError(f"{path}: bad magic")
    t = float(np.frombuffer(raw, dtype=np.float64, count=1, offset=8)[0])
    n, ncyc = (int(v) for v in np.frombuffer(raw, dtype=np.int64, count=2, offset=16))
    off = 32
    rec = np.frombuffer(raw, dtype=np.float64, count=7 * n, offset=off).reshape(n, 7)
    off += 56 * n
    tag = np.frombuffer(raw, dtype=np.int32, count=n, offset=off)
    off += 8 * n            # tags and species
    tau = np.frombuffer(raw, dtype=np.float64, count=n, offset=off)
    order = np.argsort(tag, kind="stable")
    data = np.concatenate([rec[order], tau[order, None]], axis=1)
    return t, ncyc, tag[order].copy(), np.ascontiguousarray(data)


def read_kicks(path):
    """Records of <basename>.kick.txt: cycle -> (particles, kicked, checksum); after a
    restart a cycle may appear twice, the last record counts."""
    out = {}
    with open(path) as fp:
        for line in fp:
            if line.startswith("#"):
                continue
            f = line.split()
            out[int(f[0])] = (int(f[2]), int(f[3]), f[4])
    return out


def compare_states(dir_a, dir_b, snap):
    """Bitwise comparison of the snapshot number snap of two runs."""
    ta, ca, tag_a, da = read_snapshot(os.path.join(dir_a, f"kick.part.{snap:05d}.bin"))
    tb, cb, tag_b, db = read_snapshot(os.path.join(dir_b, f"kick.part.{snap:05d}.bin"))
    res = {"time": [ta, tb], "cycle": [ca, cb], "particles": [len(tag_a), len(tag_b)]}
    if len(tag_a) != len(tag_b) or not np.array_equal(tag_a, tag_b):
        common, ia, ib = np.intersect1d(tag_a, tag_b, return_indices=True)
        da, db = da[ia], db[ib]
        res["same_tags"] = False
    else:
        res["same_tags"] = True
    diff = da.view(np.uint64) != db.view(np.uint64)
    res["particles_compared"] = int(da.shape[0])
    res["particles_differing"] = int(np.count_nonzero(diff.any(axis=1)))
    res["values_differing"] = int(np.count_nonzero(diff))
    dx = np.abs(da[:, 0:3] - db[:, 0:3]).max() if da.size else 0.0
    du = np.abs(da[:, 3:6] - db[:, 3:6]).max() if da.size else 0.0
    res["max_abs_dx"] = float(dx)
    res["max_abs_du"] = float(du)
    res["identical"] = bool(res["same_tags"] and ta == tb and ca == cb
                            and res["values_differing"] == 0)
    return res


def compare_kicks(dir_a, dir_b):
    """Checksums of the kicks of two runs, cycle by cycle."""
    ka = read_kicks(os.path.join(dir_a, "kick.kick.txt"))
    kb = read_kicks(os.path.join(dir_b, "kick.kick.txt"))
    common = sorted(set(ka) & set(kb))
    ndiff = sum(1 for c in common if ka[c][2] != kb[c][2])
    # a restarted run records only the cycles after the restart
    return {"cycles_compared": len(common), "cycles_differing": ndiff,
            "cycles": [len(ka), len(kb)],
            "identical": bool(common and ndiff == 0
                              and len(common) == min(len(ka), len(kb)))}


class Runner:
    def __init__(self, exe, top):
        self.exe = exe
        self.top = top
        self.runs = {}

    def run(self, name, args, restart_from=None):
        rundir = os.path.join(self.top, name)
        os.makedirs(rundir, exist_ok=True)
        if restart_from is None:
            cmd = [self.exe] + args + ["-d", rundir]
        else:
            cmd = [self.exe, "-r", restart_from, "-d", rundir] + args
        t0 = time.time()
        with open(os.path.join(rundir, "athena.log"), "w") as log:
            proc = subprocess.run(cmd, cwd=rundir, stdout=log, stderr=subprocess.STDOUT)
        wall = time.time() - t0
        self.runs[name] = {"command": cmd, "wall_time_s": round(wall, 2),
                           "exit_status": proc.returncode}
        print(f"  {name}: exit {proc.returncode}, {wall:.1f} s", flush=True)
        if proc.returncode != 0:
            raise RuntimeError(f"run {name} failed, see {rundir}/athena.log")
        return rundir


def make_cluster(out, n, extra):
    cmd = [sys.executable, os.path.join(REPO, "problems", "cluster_test",
                                        "make_cluster.py"), "--N", str(n), "--out", out]
    subprocess.run(cmd + extra, check=True, stdout=subprocess.DEVNULL)


def last_hist(rundir):
    """Last record of the particle history: particle number and number removed at the
    lapse threshold (columns 3 and 18 of <basename>.nrpic.hst, docs/FORMATS.md)."""
    rows = [ln.split() for ln in open(os.path.join(rundir, "kick.nrpic.hst"))
            if not ln.startswith("#")]
    return int(float(rows[-1][2])), rows[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--case", required=True, choices=["analytic", "mesh"])
    ap.add_argument("--np", type=int, default=10000)
    ap.add_argument("--tlim", type=float, default=40.0)
    ap.add_argument("--ref", default="")
    args = ap.parse_args()
    top = os.getcwd()
    exe = os.path.abspath(args.exe)
    r = Runner(exe, top)
    tl = args.tlim
    half = 0.5 * tl
    common = [f"time/tlim={tl}", f"particles/snap_dt={half}", f"output1/dt={half}"]
    summary = {"case": args.case, "exe": exe, "particles": args.np, "tlim": tl,
               "comparisons": {}, "expectations": {}}
    cmp_ = summary["comparisons"]
    exp = summary["expectations"]

    def expect(name, ok):
        exp[name] = bool(ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}", flush=True)

    if args.case == "analytic":
        inp = os.path.join(REPO, "problems", "tests", "rng_kick_analytic.athinput")
        ic = os.path.join(top, "bound_a0.9.nrp")
        make_cluster(ic, args.np, ["--a", "0.9", "--bound_only"])
        base = ["-i", inp, f"particles/particle_file={ic}"] + common
        lay2 = ["meshblock/nx1=8", "meshblock/nx2=8", "meshblock/nx3=8"]
        rst = os.path.join("rst", "kick.00001.rst")
        a0 = r.run("a0", base + ["particles/test_kick=false"])
        a1 = r.run("a1", base)
        a2 = r.run("a2", base + lay2)
        a3 = r.run("a3", [], restart_from=os.path.join(a1, rst))
        b1 = r.run("b1", base + ["particles/test_kick_key=block"])
        b2 = r.run("b2", base + lay2 + ["particles/test_kick_key=block"])
        s1 = r.run("s1", base + ["particles/test_kick_key=sequence"])
        s3 = r.run("s3", [], restart_from=os.path.join(s1, rst))
        d1 = r.run("d1", base + ["job/rng_seed=20261116"])
        mode = ["particles/test_kick_mode=direction"]
        n1 = r.run("n1", base + mode)
        n2 = r.run("n2", base + lay2 + mode)
        n3 = r.run("n3", [], restart_from=os.path.join(n1, rst))

        for name, (x, y) in {"a1_a2_layout": (a1, a2), "a1_a3_restart": (a1, a3),
                             "b1_b2_control_block": (b1, b2),
                             "s1_s3_control_sequence": (s1, s3),
                             "a1_d1_other_seed": (a1, d1), "a1_b1": (a1, b1),
                             "a1_s1": (a1, s1),
                             "n1_n2_layout": (n1, n2), "n1_n3_restart": (n1, n3),
                             "a0_a1_kick_size": (a0, a1)}.items():
            cmp_[name] = compare_states(x, y, 2)
            if name != "a0_a1_kick_size":
                cmp_[name]["kicks"] = compare_kicks(x, y)
        expect("tag key: states bit-identical for two layouts",
               cmp_["a1_a2_layout"]["identical"])
        expect("tag key: states bit-identical after a restart",
               cmp_["a1_a3_restart"]["identical"])
        expect("tag key: checksums identical (layouts, restart)",
               cmp_["a1_a2_layout"]["kicks"]["identical"]
               and cmp_["a1_a3_restart"]["kicks"]["identical"])
        expect("direction mode: states bit-identical (layouts, restart)",
               cmp_["n1_n2_layout"]["identical"] and cmp_["n1_n3_restart"]["identical"])
        expect("control block: states differ between layouts",
               cmp_["b1_b2_control_block"]["particles_differing"] > 0)
        expect("control sequence: states differ after a restart",
               cmp_["s1_s3_control_sequence"]["particles_differing"] > 0)
        expect("other seed: states differ",
               cmp_["a1_d1_other_seed"]["particles_differing"] > 0)
        expect("one MeshBlock: keys tag, block and sequence agree without a restart"
               " only for sequence", cmp_["a1_s1"]["identical"]
               and not cmp_["a1_b1"]["identical"])
        # size of the accumulated kick against sigma sqrt(t) (the flow mixes the
        # components, so this is a rough check)
        _, _, _, d0 = read_snapshot(os.path.join(a0, "kick.part.00002.bin"))
        _, _, _, dk = read_snapshot(os.path.join(a1, "kick.part.00002.bin"))
        rms = float(np.sqrt(np.mean((dk[:, 3:6] - d0[:, 3:6]) ** 2)))
        summary["kick_rms_du"] = rms
        summary["kick_expected_rms"] = 1.0e-3 * np.sqrt(tl)
        expect("accumulated kick within a factor 1.5 of sigma sqrt(t)",
               1.0 / 1.5 < rms / (1.0e-3 * np.sqrt(tl)) < 1.5)
        ref_runs = ["a1", "n1"]
    else:
        inp = os.path.join(REPO, "problems", "tests", "rng_kick_mesh.athinput")
        ic = os.path.join(top, "bound_a0.nrp")
        icp = os.path.join(top, "plunge_a0.nrp")
        make_cluster(ic, args.np, ["--a", "0.0", "--bound_only"])
        make_cluster(icp, args.np, ["--a", "0.0", "--fL", "0.3"])
        base = ["-i", inp, f"particles/particle_file={ic}"] + common
        lay2 = ["meshblock/nx1=32", "meshblock/nx2=32", "meshblock/nx3=32"]
        nok = ["particles/test_kick=false"]
        rst = os.path.join("rst", "kick.00001.rst")
        m1 = r.run("m1", base)
        m2 = r.run("m2", base + lay2)
        m3 = r.run("m3", base + nok)
        m4 = r.run("m4", base + lay2 + nok)
        # plunging particles (L = 0.3 L_circ): removed between t = 33 and 60; the run
        # ends at t = 50 and is restarted from t = 40, so particles are removed before
        # and after the restart
        pl = ["-i", inp, f"particles/particle_file={icp}", "time/tlim=50.0",
              "particles/snap_dt=50.0", "output1/dt=40.0"]
        m5 = r.run("m5", pl)
        m6 = r.run("m6", [], restart_from=os.path.join(m5, rst))
        cmp_["m1_m2_layout_kick"] = compare_states(m1, m2, 2)
        cmp_["m1_m2_layout_kick"]["kicks"] = compare_kicks(m1, m2)
        cmp_["m3_m4_layout_nokick"] = compare_states(m3, m4, 2)
        cmp_["m5_m6_restart_plunge"] = compare_states(m5, m6, 1)
        cmp_["m5_m6_restart_plunge"]["kicks"] = compare_kicks(m5, m6)
        n5, row5 = last_hist(m5)
        summary["plunge_particles_left"] = n5
        summary["plunge_particles_removed"] = args.np - n5
        expect("checksums of the kicks identical for two layouts",
               cmp_["m1_m2_layout_kick"]["kicks"]["identical"])
        expect("states differ between layouts without the kick (interpolation)",
               cmp_["m3_m4_layout_nokick"]["particles_differing"] > 0)
        expect("states differ between layouts with the kick by a comparable amount",
               0 < cmp_["m1_m2_layout_kick"]["max_abs_du"] < 1.0e-6)
        expect("restart with removed particles: states bit-identical",
               cmp_["m5_m6_restart_plunge"]["identical"])
        expect("restart with removed particles: some particles were removed",
               0 < n5 < args.np)
        expect("restart with removed particles: checksums identical",
               cmp_["m5_m6_restart_plunge"]["kicks"]["identical"])
        ref_runs = ["m1", "m5"]

    if args.ref:
        for name in ref_runs:
            c = compare_kicks(os.path.join(top, name), os.path.join(args.ref, name))
            cmp_[f"{name}_checksums_vs_ref"] = c
            expect(f"checksums of {name} identical to {args.ref}", c["identical"])
    summary["runs"] = r.runs
    summary["ok"] = all(exp.values())
    with open(os.path.join(top, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps({"ok": summary["ok"], "expectations": exp}, indent=1))
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
