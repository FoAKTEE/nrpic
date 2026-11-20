#!/usr/bin/env python3
"""G2M-1 of g2mesh: MeshBlock trees of P1's set-up at three resolutions and two block sizes.

Parts (all on processors; the model is tree3.py):
  A  tree3 against tree_check.Model of nr_first (single puncture, E11): equal level by level.
  B  the start rule against `athena -m` of the release processor executable (core-v0.3) for
     every variant and for core's by_triple (16^3 and 32^3): equal level by level.
  C  the regrid rule at P1's tracker positions against the trees of P1's restart files
     (header only: tracks/F-hills/nr_first/scripts/tree_check.read_rst_tree), and the mean
     MeshBlock count of each chain segment of P1 (MeshBlock-cycles / cycles of its log).
  D  every variant along P1's measured tracks (trackers joined over the segments with
     nr_first/scripts/nrread.read_trackers) and along the Newtonian tracks to 280 M (full
     three-body problem from P1's state, stage/G0/checks/lead_checks.newton_full), every
     0.25 M; maximum, mean, cells, MeshBlock-cycles of a 280 M passage.
Writes <out>/model.json. Usage: model_run.py <out> [--cores N]
All inputs are read only.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/nr_first/scripts"))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/stage/G0/checks"))
import tree3 as t3  # noqa: E402

P1_INPUT = os.path.join(WT, "tracks/F-hills/nr_first/inputs/p1_q4.athinput")
P1_RUN = "/data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f"
BY_TRIPLE = os.path.join(WT, "problems/puncture/by_triple.athinput")
EXE_CPU = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"
T_PASS = 280.0
DT_SAMPLE = 0.25
CFL = 0.25

# name: (root cells per side, num_levels); the block size is the second key
RES = {"R8": (64, 10), "R12": (96, 10), "R16n": (64, 11), "R16u": (128, 10)}
BLOCKS = (16, 32)


def variants():
    return [(r, b) for r in RES for b in BLOCKS]


def tree_for(inp, res, block):
    nx, nl = RES[res]
    return t3.Tree(inp, nx=nx, num_levels=nl, block=block)


# ------------------------------------------------------------------------------- B
def athena_m(inp_path, out, name, overrides):
    d = os.path.join(out, "athena_m", name)
    os.makedirs(d, exist_ok=True)
    cmd = [EXE_CPU, "-i", inp_path, "-d", d, "-m",
           "mesh_refinement/max_nmb_per_rank=1000000"] + overrides
    env = dict(os.environ, OMP_NUM_THREADS="1")
    p = subprocess.run(cmd, cwd=d, capture_output=True, text=True, env=env)
    with open(os.path.join(d, "stdout.txt"), "w") as f:
        f.write(" ".join(cmd) + "\n" + p.stdout + p.stderr)
    ms = os.path.join(d, "mesh_structure.dat")
    if os.path.exists(ms):
        os.remove(ms)                  # large; the counts are in stdout.txt
    tot = re.search(r"Total number of MeshBlocks = (\d+)", p.stdout)
    per = re.findall(r"Physical level = (\d+) \(logical level = \d+\): (\d+) MeshBlocks",
                     p.stdout)
    if tot is None:
        raise RuntimeError(f"athena -m {name}: no count\n{p.stdout[-2000:]}\n{p.stderr}")
    return int(tot.group(1)), {int(a): int(b) for a, b in per}


def part_b(out, inp):
    rows, ok = [], True
    pos = np.array([p[3] for p in t3.punctures(inp, 10)])
    for res, b in variants():
        nx, nl = RES[res]
        ov = [f"mesh/nx{a}={nx}" for a in (1, 2, 3)] + \
             [f"meshblock/nx{a}={b}" for a in (1, 2, 3)] + \
             [f"mesh_refinement/num_levels={nl}"]
        n_ex, per_ex = athena_m(P1_INPUT, out, f"{res}_b{b}", ov)
        mc = tree_for(inp, res, b).build(pos, start=True)
        eq = per_ex == mc
        ok &= eq
        rows.append(dict(case=f"{res}_b{b}", athena_m=n_ex, athena_m_levels=per_ex,
                         model=t3.total(mc), model_levels=mc, equal=eq))
        print("B", res, b, "athena -m", n_ex, "model", t3.total(mc), "equal" if eq else "DIFF")
    bt = t3.read_athinput(BY_TRIPLE)
    bpos = np.array([p[3] for p in t3.punctures(bt, int(bt["mesh_refinement"]["num_levels"]))])
    for b in BLOCKS:
        ov = [f"meshblock/nx{a}={b}" for a in (1, 2, 3)]
        n_ex, per_ex = athena_m(BY_TRIPLE, out, f"by_triple_b{b}", ov)
        T = t3.Tree(bt, block=b)
        mc = T.build(bpos, start=True)
        mr = T.build(bpos, start=False)
        eq = per_ex == mc
        ok &= eq
        rows.append(dict(case=f"by_triple_b{b}", athena_m=n_ex, athena_m_levels=per_ex,
                         model=t3.total(mc), model_levels=mc, equal=eq,
                         model_regrid=t3.total(mr), model_regrid_levels=mr))
        print("B by_triple", b, "athena -m", n_ex, "model", t3.total(mc),
              "regrid", t3.total(mr), "equal" if eq else "DIFF")
    return dict(rows=rows, all_equal=bool(ok), exe=EXE_CPU)


# ------------------------------------------------------------------------------- C
def part_c(inp):
    import nrread as nr                                        # read only
    import tree_check as tc                                    # read only
    trk = nr.read_trackers(P1_RUN)
    keys = sorted(trk)
    T = t3.Tree(inp)
    rows = []
    for p in sorted(glob.glob(os.path.join(P1_RUN, "rst", "*.rst"))):
        h = tc.read_rst_tree(p)
        pos = []
        for k in keys:
            i = int(np.argmin(np.abs(trk[k]["t"] - h["time"])))
            pos.append(trk[k]["x"][i])
        pos = np.array(pos)
        start = h["ncycle"] == 0
        mc = T.build(pos, start=start)
        # derefinement can lag: the model at the positions 8 and 16 cycles earlier too
        alt = {}
        for back in (8, 16, 32):
            pb = []
            for k in keys:
                i = int(np.argmin(np.abs(trk[k]["iter"] - (h["ncycle"] - back))))
                pb.append(trk[k]["x"][i])
            alt[back] = t3.total(T.build(np.array(pb), start=False)) if not start else None
        rows.append(dict(file=os.path.basename(p), time=h["time"], ncycle=h["ncycle"],
                         nmb=h["nmb"], levels=h["counts"], model=t3.total(mc),
                         model_levels=mc, rule="start" if start else "regrid",
                         equal_levels=(h["counts"] == mc), model_back=alt,
                         positions=pos.tolist()))
        print("C", rows[-1]["file"], "t %.2f" % h["time"], "rst", h["nmb"], "model",
              t3.total(mc), "equal" if rows[-1]["equal_levels"] else "DIFF", alt)
    # chain segments: mean MeshBlocks = MeshBlock-cycles / cycles
    segs = []
    for lg in sorted(glob.glob(os.path.join(P1_RUN, "chain", "seg*.log"))):
        s = open(lg, errors="replace").read()
        cyc = [int(c) for c in re.findall(r"cycle=(\d+)", s)]
        tim = [float(c) for c in re.findall(r"cycle=\d+ time=([0-9.e+-]+)", s)]
        mbc = re.search(r"MeshBlock-cycles = (\d+)", s)
        cpu = re.search(r"cpu time used\s*=\s*([0-9.e+-]+)", s)
        nfin = re.search(r"Current number of MeshBlocks = (\d+)", s)
        peak = re.search(r"gpu_mem_peak_MiB=(\d+)", s)
        last = re.search(r"time=([0-9.e+-]+) cycle=(\d+)\s*\n\s*tlim", s)
        if not cyc:
            continue
        c0 = cyc[0]
        c1 = int(last.group(2)) if last else cyc[-1]
        t1 = float(last.group(1)) if last else (tim[-1] if tim else None)
        row = dict(log=os.path.basename(lg), cycle0=c0, cycle1=c1,
                   t0=tim[0] if tim else None, t1=t1,
                   meshblock_cycles=int(mbc.group(1)) if mbc else None,
                   cpu_s=float(cpu.group(1)) if cpu else None,
                   n_final=int(nfin.group(1)) if nfin else None,
                   gpu_mem_peak_MiB=int(peak.group(1)) if peak else None)
        if mbc and cpu:
            row["mean_nmb"] = row["meshblock_cycles"] / (c1 - c0)
            row["rate_mb_cycles_per_s"] = row["meshblock_cycles"] / row["cpu_s"]
        segs.append(row)
        print("C seg", row)
    return dict(run=P1_RUN, trackers={k: [float(trk[k]["t"][0]), float(trk[k]["t"][-1])]
                                      for k in keys}, rst=rows, segments=segs,
                all_rst_equal=all(r["equal_levels"] for r in rows))


# ------------------------------------------------------------------------------- D
_INP = None


def _init(path):
    global _INP
    _INP = t3.read_athinput(path)


def _count(args):
    res, b, t, pos, start = args
    mc = tree_for(_INP, res, b).build(np.asarray(pos), start=start)
    return res, b, t, t3.total(mc), mc


def tracks():
    import nrread as nr
    import lead_checks as lc
    trk = nr.read_trackers(P1_RUN)
    t, X, _ = nr.common_times(trk, keys=sorted(trk), dt=DT_SAMPLE)
    m, x, p = lc.read_athinput(P1_INPUT)
    nout = int(round(T_PASS / DT_SAMPLE)) + 1
    ts, Y = lc.newton_full(m, x, p, t_end=T_PASS, nout=nout)
    XN = Y[:, :9].reshape(-1, 3, 3)
    return dict(p1=(t, X), newton=(ts, XN))


def part_d(inp, cores):
    tr = tracks()
    jobs = []
    for res, b in variants():
        for name, (t, X) in tr.items():
            for k in range(len(t)):
                jobs.append((res, b, (name, float(t[k])), X[k].tolist(), False))
        jobs.append((res, b, ("start", 0.0), tr["newton"][1][0].tolist(), True))
    t0 = time.time()
    with Pool(cores, initializer=_init, initargs=(P1_INPUT,)) as pool:
        got = pool.map(_count, jobs, chunksize=16)
    print("D: %d trees in %.0f s" % (len(jobs), time.time() - t0))
    out = {}
    for res, b in variants():
        T = tree_for(inp, res, b)
        hmin = T.h(T.lmax)
        dt = CFL * hmin
        v = dict(nx=RES[res][0], num_levels=RES[res][1], block=b, h_min=hmin,
                 dt=dt, cycles_280=T_PASS / dt, cells_per_block=b ** 3)
        for name in ("p1", "newton"):
            rows = sorted([(tt, n, mc) for (r, bb, (nm, tt), n, mc) in got
                           if r == res and bb == b and nm == name])
            tt = np.array([r[0] for r in rows])
            nn = np.array([r[1] for r in rows], dtype=float)
            imax = int(np.argmax(nn))
            v[name] = dict(t=tt.tolist(), n=nn.astype(int).tolist(), n_max=int(nn.max()),
                           t_max=float(tt[imax]), levels_at_max=rows[imax][2],
                           n_mean=float(np.trapezoid(nn, tt) / (tt[-1] - tt[0])),
                           t_end=float(tt[-1]))
        st = [(n, mc) for (r, bb, (nm, _), n, mc) in got if r == res and bb == b and nm == "start"]
        v["start"] = dict(n=st[0][0], levels=st[0][1])
        nmax = max(v["start"]["n"], v["newton"]["n_max"], v["p1"]["n_max"])
        v["n_max_all"] = nmax
        v["cells_max"] = nmax * b ** 3
        v["mb_cycles_280_newton"] = v["newton"]["n_mean"] * v["cycles_280"]
        v["zone_cycles_280_newton"] = v["mb_cycles_280_newton"] * b ** 3
        out[f"{res}_b{b}"] = v
        print("D", res, b, "start", v["start"]["n"], "max newton", v["newton"]["n_max"],
              "at", v["newton"]["t_max"], "mean", round(v["newton"]["n_mean"]),
              "| max p1", v["p1"]["n_max"], "mean", round(v["p1"]["n_mean"]),
              "| cells max %.1fM" % (v["cells_max"] / 1e6))
    return out


def main():
    out = sys.argv[1]
    cores = int(sys.argv[sys.argv.index("--cores") + 1]) if "--cores" in sys.argv else 1
    os.makedirs(out, exist_ok=True)
    inp = t3.read_athinput(P1_INPUT)
    res = {"p1_input": P1_INPUT, "p1_run": P1_RUN, "dt_sample": DT_SAMPLE,
           "variants": {k: dict(nx=v[0], num_levels=v[1]) for k, v in RES.items()}}
    res["A_tree_check"] = t3.test(os.path.join(out, "test_tree3.json"))
    res["B_athena_m"] = part_b(out, inp)
    res["C_p1_restarts"] = part_c(inp)
    res["D_tracks"] = part_d(inp, cores)
    with open(os.path.join(out, "model.json"), "w") as f:
        json.dump(res, f, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    print("written", os.path.join(out, "model.json"))


if __name__ == "__main__":
    main()
