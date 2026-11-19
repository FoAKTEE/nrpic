#!/usr/bin/env python3
"""Work package mpi: run one test case on several numbers of MPI ranks and compare the
outputs with those of one rank (tracks/core/interfaces/mpi.md, section 4).

    python3 tracks/core/analysis/mpi/mpi_tests.py --case t1_kerr [--ranks 1 2 4]
        [--exe PATH] [--out DIR] [--compare-only]

The output directory is $NRPIC_RUN_DIR/<case> (set by nrpic-run) unless --out is given.
Each rank count runs in <out>/np<N>; the comparison is written to <out>/compare.json and
printed; figures go to <out>/figs and, with --figdir, to that directory as well.

What is compared, always against the run on one rank:
  bytes     trajectories, metric at the tracked particles, snapshots, particle restart
            files, line and field dumps: identical byte for byte or not;
  numbers   every column of the histories (largest difference relative to the largest
            magnitude of the column), the particle snapshots (largest difference of a
            coordinate), the source fields of the binary dumps (largest difference
            relative to the largest magnitude of the component);
  identity  in each run by itself: mesh integrals of E, S_i against the particle sums.
"""
import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(REPO, "athenak", "vis", "python"))

MPIRUN = "/home/emost/codes/openmpi/bin/mpirun"
DEFAULT_EXE = os.path.join(REPO, ".work", "build_cpu_mpi", "src", "athena")


# ----------------------------------------------------------------------------------------
# particle files
# ----------------------------------------------------------------------------------------
def make_swarm(path, n=2000, seed=20261119, mass=1.0e-4):
    """Particles around a black hole of unit mass at the origin: radii 3 to 12, isotropic
    directions, speeds 0.3 to 1.2 of the circular speed (bound, some plunge), and one in
    twelve at 1.5 to 2.2 of it (they leave the box of half-width 16)."""
    from nrpic.io import write_nrp
    rng = np.random.default_rng(seed)
    r = rng.uniform(3.0, 12.0, n)
    def directions(k):
        v = rng.normal(size=(k, 3))
        return v/np.linalg.norm(v, axis=1)[:, None]
    x = r[:, None]*directions(n)
    f = rng.uniform(0.3, 1.2, n)
    fast = rng.uniform(size=n) < 1.0/12.0
    f[fast] = rng.uniform(1.5, 2.2, fast.sum())
    u = (f*np.sqrt(1.0/r))[:, None]*directions(n)
    m = np.full(n, mass)
    write_nrp(path, x, u, m)
    return n


def make_box(path, n=3000, seed=20261120, mass=1.0e-3):
    """Particles spread over the unit box with momenta up to 0.6 per unit mass."""
    from nrpic.io import write_nrp
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.0, 1.0, (n, 3))
    u = rng.uniform(-0.6, 0.6, (n, 3))
    m = mass*rng.uniform(0.5, 1.5, n)
    write_nrp(path, x, u, m)
    return n


# ----------------------------------------------------------------------------------------
# cases
# ----------------------------------------------------------------------------------------
KERR = "problems/tests/mpi_kerr_swarm.athinput"
BOX = "problems/tests/mpi_box_periodic.athinput"
DEP = ["particles/deposit=true"]

CASES = {
    # step 1: test particles in a fixed metric
    # (without deposit there are no sources to dump: the block <output2> is dropped)
    "t1_kerr": dict(input=KERR, particles=("swarm.nrp", make_swarm), args=[],
                    drop=["output2"]),
    "t1_kerr_boris": dict(input=KERR, particles=("swarm.nrp", make_swarm),
                          args=["particles/pusher=boris"], drop=["output2"]),
    "t1p_box": dict(input=BOX, particles=("box.nrp", make_box), args=[],
                    drop=["output2"]),
    # step 2: deposit across rank boundaries, fixed metric
    "t2p_box_cic": dict(input=BOX, particles=("box.nrp", make_box),
                        args=DEP + ["particles/deposit_shape=cic"]),
    "t2p_box_tsc": dict(input=BOX, particles=("box.nrp", make_box),
                        args=DEP + ["particles/deposit_shape=tsc", "particles/nfilter=2"]),
    "t2p_box_pcs": dict(input=BOX, particles=("box.nrp", make_box),
                        args=DEP + ["particles/deposit_shape=pcs", "particles/nfilter=0"]),
    "t2_kerr_cic": dict(input=KERR, particles=("swarm.nrp", make_swarm),
                        args=DEP + ["particles/deposit_shape=cic"]),
    "t2_kerr_pcs": dict(input=KERR, particles=("swarm.nrp", make_swarm),
                        args=DEP + ["particles/deposit_shape=pcs", "particles/nfilter=2"]),
}

BYTE_PATTERNS = ["*.traj.bin", "*.trajmet.bin", "*.part.*.bin", "rst/*.prt",
                 "*.line.bin", "*.field.*.bin"]
HIST_PATTERNS = ["*.nrpic.hst", "*.cstat.hst", "*.cons.hst", "*.z4c.user.hst",
                 "*.z4c.hst"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_table(path):
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            try:
                rows.append([float(t) for t in s.split()])
            except ValueError:
                continue
    if not rows:
        return np.zeros((0, 0))
    n = min(len(r) for r in rows)
    return np.array([r[:n] for r in rows])


def read_snapshot(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        assert magic == b"NRPSNAP1", magic
        t = np.frombuffer(f.read(8), "<f8")[0]
        n = int(np.frombuffer(f.read(8), "<i8")[0])
        f.read(8)
        rec = np.frombuffer(f.read(56*n), "<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4*n), "<i4")
    return t, rec, tag


def read_bin_blocks(path):
    """AthenaK binary dump -> {(x1min, x2min, x3min): {name: array}} per MeshBlock."""
    import bin_convert
    fd = bin_convert.read_binary(path)
    out = {}
    for b, g in enumerate(fd["mb_geometry"]):
        key = (round(float(g[0]), 12), round(float(g[2]), 12), round(float(g[4]), 12))
        out[key] = {k: np.asarray(v[b], dtype=np.float64) for k, v in fd["mb_data"].items()}
    return fd["time"], out


# ----------------------------------------------------------------------------------------
def input_without(src, dst, blocks):
    """Copy of an input file without the named blocks."""
    keep, out = True, []
    with open(src) as f:
        for line in f:
            s = line.strip()
            if s.startswith("<") and s.endswith(">"):
                keep = s.strip("<>") not in blocks
            if keep:
                out.append(line)
    with open(dst, "w") as f:
        f.writelines(out)


def run_case(case, ranks, exe, out, extra):
    spec = CASES[case]
    os.makedirs(out, exist_ok=True)
    pname, maker = spec["particles"]
    ppath = os.path.join(out, pname)
    npart = maker(ppath)
    inp = os.path.join(REPO, spec["input"])
    if spec.get("drop"):
        stripped = os.path.join(out, os.path.basename(inp))
        input_without(inp, stripped, spec["drop"])
        inp = stripped
    procs = []
    for n in ranks:
        d = os.path.join(out, "np%d" % n)
        os.makedirs(d, exist_ok=True)
        cmd = [MPIRUN, "--bind-to", "none", "-np", str(n), exe, "-i", inp, "-d", d,
               "particles/particle_file=" + ppath] + spec["args"] + extra
        log = open(os.path.join(d, "run.log"), "w")
        env = dict(os.environ, OMP_NUM_THREADS="1")
        procs.append((n, d, cmd, time.time(),
                      subprocess.Popen(cmd, cwd=d, stdout=log, stderr=subprocess.STDOUT,
                                       env=env), log))
    res = {}
    for n, d, cmd, t0, p, log in procs:
        rc = p.wait()
        log.close()
        res[n] = dict(dir=d, command=cmd, exit=rc, wall_s=round(time.time() - t0, 1))
        print("np=%d exit=%d wall=%.1f s" % (n, rc, res[n]["wall_s"]), flush=True)
    return npart, res


def compare_case(case, ranks, out):
    ref = os.path.join(out, "np%d" % ranks[0])
    result = dict(case=case, ranks=ranks, bytes={}, histories={}, snapshots={},
                  fields={}, identity={}, mpi={})
    # ---- bytes
    for pat in BYTE_PATTERNS:
        for f in sorted(glob.glob(os.path.join(ref, pat))):
            rel = os.path.relpath(f, ref)
            h0 = sha256(f)
            row = dict(size=os.path.getsize(f))
            for n in ranks[1:]:
                g = os.path.join(out, "np%d" % n, rel)
                row["np%d" % n] = (os.path.exists(g) and sha256(g) == h0)
                if rel.endswith(".prt") and os.path.exists(g):
                    # bytes 40 to 55 hold the rest mass removed by excision and at the
                    # boundary, two sums over particles whose order depends on the ranks
                    a, b = open(f, "rb").read(), open(g, "rb").read()
                    row["np%d_without_summed_masses" % n] = (
                        len(a) == len(b) and a[:40] == b[:40] and a[56:] == b[56:])
            result["bytes"][rel] = row
    # ---- histories
    for pat in HIST_PATTERNS:
        for f in sorted(glob.glob(os.path.join(ref, pat))):
            rel = os.path.relpath(f, ref)
            a = read_table(f)
            row = dict(records=int(a.shape[0]), columns=int(a.shape[1]) if a.size else 0)
            for n in ranks[1:]:
                g = os.path.join(out, "np%d" % n, rel)
                if not os.path.exists(g):
                    row["np%d" % n] = "missing"
                    continue
                b = read_table(g)
                if a.shape != b.shape:
                    row["np%d" % n] = "shape %s against %s" % (b.shape, a.shape)
                    continue
                fin = np.where(np.isfinite(a), a, 0.0)
                scale = np.maximum(np.abs(fin).max(axis=0), 1.0e-300)
                with np.errstate(invalid="ignore"):
                    diff = np.where(a == b, 0.0, np.abs(a - b))   # equal infinities: none
                d = diff.max(axis=0)/scale
                worst = int(np.argmax(d))
                row["np%d" % n] = dict(identical=bool(sha256(g) == sha256(f)),
                                       max_rel=float(d.max()), column=worst + 1,
                                       exact_columns=int((diff.max(axis=0) == 0).sum()))
            result["histories"][rel] = row
    # ---- snapshots, numerically (by tag)
    for f in sorted(glob.glob(os.path.join(ref, "*.part.*.bin"))):
        rel = os.path.relpath(f, ref)
        t, rec, tag = read_snapshot(f)
        row = dict(time=float(t), n=int(len(tag)), tags_ascending=bool(np.all(np.diff(tag) > 0)))
        for n in ranks[1:]:
            g = os.path.join(out, "np%d" % n, rel)
            if not os.path.exists(g):
                row["np%d" % n] = "missing"
                continue
            t2, rec2, tag2 = read_snapshot(g)
            if len(tag2) != len(tag) or not np.array_equal(tag, tag2):
                row["np%d" % n] = "different particles (%d against %d)" % (len(tag2), len(tag))
            else:
                row["np%d" % n] = float(np.abs(rec - rec2).max()) if len(tag) else 0.0
        result["snapshots"][rel] = row
    # ---- source fields of the binary dumps
    for f in sorted(glob.glob(os.path.join(ref, "bin", "*.bin"))):
        rel = os.path.relpath(f, ref)
        t, blk = read_bin_blocks(f)
        names = sorted(next(iter(blk.values())).keys())
        scale = {k: max(max(np.abs(b[k]).max() for b in blk.values()), 1.0e-300) for k in names}
        row = dict(time=float(t), blocks=len(blk),
                   max_abs={k: float(scale[k]) for k in names})
        for n in ranks[1:]:
            g = os.path.join(out, "np%d" % n, rel)
            if not os.path.exists(g):
                row["np%d" % n] = "missing"
                continue
            t2, blk2 = read_bin_blocks(g)
            if set(blk2.keys()) != set(blk.keys()):
                row["np%d" % n] = "different MeshBlocks"
                continue
            worst = {k: 0.0 for k in names}
            for key in blk:
                for k in names:
                    worst[k] = max(worst[k], float(np.abs(blk[key][k] - blk2[key][k]).max())/scale[k])
            row["np%d" % n] = dict(max_rel=max(worst.values()),
                                   component=max(worst, key=worst.get))
        result["fields"][rel] = row
    # ---- conservation identity, each run by itself (history columns 5-12)
    for n in ranks:
        g = glob.glob(os.path.join(out, "np%d" % n, "*.nrpic.hst"))
        if not g:
            continue
        a = read_table(g[0])
        if a.shape[1] < 12:
            continue
        smw = np.abs(a[:, 4])
        ok = smw > 0
        if not ok.any() or np.abs(a[:, 8]).max() == 0.0:
            continue
        dE = np.abs(a[ok, 8] - a[ok, 4])/smw[ok]
        dS = np.abs(a[ok, 9:12] - a[ok, 5:8]).max(axis=1)/smw[ok]
        result["identity"]["np%d" % n] = dict(max_dE_over_sum_mW=float(dE.max()),
                                              max_dS_over_sum_mW=float(dS.max()),
                                              records=int(ok.sum()))
    # ---- hand-overs and packets
    for n in ranks[1:]:
        g = glob.glob(os.path.join(out, "np%d" % n, "*.mpi.hst"))
        if g:
            a = read_table(g[0])
            result["mpi"]["np%d" % n] = dict(
                handed_over=int(a[:, 2].sum()), deposit_packets=int(a[:, 3].sum()),
                particles_per_rank_first=[int(v) for v in a[0, 4:]],
                particles_per_rank_last=[int(v) for v in a[-1, 4:]])
    return result


def summary_lines(result):
    lines = []
    ranks = result["ranks"]
    for rel, row in result["bytes"].items():
        def word(n):
            if row["np%d" % n]:
                return "identical"
            if row.get("np%d_without_summed_masses" % n):
                return "identical but for the two summed masses"
            return "DIFFERENT"
        lines.append("bytes   %-28s %s" % (rel, "  ".join(
            "np%d:%s" % (n, word(n)) for n in ranks[1:])))
    for rel, row in result["histories"].items():
        parts = []
        for n in ranks[1:]:
            v = row["np%d" % n]
            parts.append("np%d:%s" % (n, v if isinstance(v, str) else
                         ("identical" if v["identical"] else
                          "max rel %.2e (col %d; %d of %d columns exact)" %
                          (v["max_rel"], v["column"], v["exact_columns"], row["columns"]))))
        lines.append("history %-28s %s" % (rel, "  ".join(parts)))
    for rel, row in result["snapshots"].items():
        lines.append("snap    %-28s n=%d %s" % (rel, row["n"], "  ".join(
            "np%d:%s" % (n, row["np%d" % n] if isinstance(row["np%d" % n], str)
                         else "max diff %.2e" % row["np%d" % n]) for n in ranks[1:])))
    for rel, row in result["fields"].items():
        lines.append("field   %-28s %s" % (rel, "  ".join(
            "np%d:%s" % (n, row["np%d" % n] if isinstance(row["np%d" % n], str)
                         else "max rel %.2e (%s)" % (row["np%d" % n]["max_rel"],
                                                     row["np%d" % n]["component"]))
            for n in ranks[1:])))
    for k, v in result["identity"].items():
        lines.append("identity %s: |int E - sum mW|/sum mW <= %.2e, |int S_i - sum m u_i|/sum mW"
                     " <= %.2e over %d records" % (k, v["max_dE_over_sum_mW"],
                                                   v["max_dS_over_sum_mW"], v["records"]))
    for k, v in result["mpi"].items():
        lines.append("ranks   %s: %d particles handed over, %d deposit packets; per rank %s -> %s"
                     % (k, v["handed_over"], v["deposit_packets"],
                        v["particles_per_rank_first"], v["particles_per_rank_last"]))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True, choices=sorted(CASES))
    ap.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 4])
    ap.add_argument("--exe", default=DEFAULT_EXE)
    ap.add_argument("--out", default=None)
    ap.add_argument("--figdir", default=None)
    ap.add_argument("--compare-only", action="store_true")
    ap.add_argument("extra", nargs="*", help="further athena arguments (block/key=value)")
    a = ap.parse_args()
    base = a.out or os.path.join(os.environ.get("NRPIC_RUN_DIR", os.getcwd()), a.case)
    npart, runs = None, {}
    if not a.compare_only:
        npart, runs = run_case(a.case, a.ranks, a.exe, base, a.extra)
    result = compare_case(a.case, a.ranks, base)
    result["particles"] = npart
    result["runs"] = {str(k): v for k, v in runs.items()}
    result["exe"] = a.exe
    with open(os.path.join(base, "compare.json"), "w") as f:
        json.dump(result, f, indent=1)
    for line in summary_lines(result):
        print(line)
    try:
        import mpi_figs
        for path in mpi_figs.make(a.case, a.ranks, base, a.figdir):
            print("figure", path)
    except Exception as exc:                      # the numbers stand without the figure
        print("figures failed:", repr(exc))
    bad = [n for n, v in runs.items() if v["exit"] != 0]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
