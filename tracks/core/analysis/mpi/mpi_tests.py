#!/usr/bin/env python3
"""Work package mpi: run one test case on several numbers of MPI ranks and compare the
outputs with those of one rank (tracks/core/interfaces/mpi.md, section 4).

    python3 tracks/core/analysis/mpi/mpi_tests.py --case t1_kerr [--ranks 1 2 4]
        [--exe PATH] [--out DIR] [--compare-only]
    python3 tracks/core/analysis/mpi/mpi_tests.py --restart-of DIR --pairs 1:1 2:2 1:4
        [--rst rst/cl.00001.rst] [--exe PATH] [--out DIR] [--compare-only]

The second form (test T4) restarts the runs of an earlier case (DIR is its output
directory, with np<N> inside) from the restart file written on w ranks, on r ranks
(pairs w:r), into <out>/w<w>r<r>, and compares what the restarted run wrote with the
uninterrupted runs on w and on r ranks: binary record files by their tails, histories by
their last records, snapshots and field dumps by name, the final particle restart file
byte for byte and the mesh restart file after its parameter header.

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
import shutil
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


def make_swarm_bound(path, n=4000, seed=20261121, mass=1.0e-4):
    """As make_swarm, radii 4 to 11, with the radial covariant momentum of a particle at
    rest in Kerr-Schild coordinates added, (2/r) u^t n_i with u^t about 1.15, so that
    most particles stay on bound orbits; one in twenty leaves the box."""
    from nrpic.io import write_nrp
    rng = np.random.default_rng(seed)
    r = rng.uniform(4.0, 11.0, n)
    def directions(k):
        v = rng.normal(size=(k, 3))
        return v/np.linalg.norm(v, axis=1)[:, None]
    nhat = directions(n)
    x = r[:, None]*nhat
    f = rng.uniform(0.5, 1.1, n)
    fast = rng.uniform(size=n) < 1.0/20.0
    f[fast] = rng.uniform(1.6, 2.2, fast.sum())
    u = (f*np.sqrt(1.0/r))[:, None]*directions(n) + (2.3/r)[:, None]*nhat
    m = mass*rng.uniform(0.5, 1.5, n)
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


def make_cluster(path, n=4000, seed=7, yc=0.605):
    """Shapiro-Teukolsky cluster (y_c = 0.605, isotropic radius 4.7 M) from
    problems/ic/make_ic.py: <stem>.nrp, <stem>.tab and <stem>.json next to path."""
    d = os.path.dirname(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    cmd = [sys.executable, os.path.join(REPO, "problems", "ic", "make_ic.py"), "st",
           "--yc", str(yc), "--N", str(n), "--seed", str(seed), "--out", d,
           "--prefix", stem]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                   env=dict(os.environ, OMP_NUM_THREADS="2"))
    return n


def make_cluster_offset(path):
    """The cluster of make_cluster moved to (4, 4, 4) (the table is moved with
    problem/comp0_x1..3)."""
    from nrpic.io import read_nrp, write_nrp
    n = make_cluster(path)
    x, u, m, sp = read_nrp(path)
    write_nrp(path, x + 4.0, u, m, sp)
    return n


def make_infall(path, n=2000, seed=20261122, mass=1.0e-8, centre=(0.1, -0.2, 0.05)):
    """Light particles around the puncture of mpi_puncture_exc.athinput: radii 0.3 to 2.5
    from it (the horizon of the unit-mass puncture has coordinate radius about 0.5), random
    momenta up to 0.4 per unit mass plus an inward radial part of 0 to 0.6, so that
    particles are inside the excision radius at the start and others cross it later."""
    from nrpic.io import write_nrp
    rng = np.random.default_rng(seed)
    r = rng.uniform(0.3, 2.5, n)
    v = rng.normal(size=(n, 3))
    nhat = v/np.linalg.norm(v, axis=1)[:, None]
    x = np.asarray(centre)[None, :] + r[:, None]*nhat
    u = rng.uniform(-0.4, 0.4, (n, 3)) - rng.uniform(0.0, 0.6, n)[:, None]*nhat
    m = mass*rng.uniform(0.5, 1.5, n)
    write_nrp(path, x, u, m)
    return n


REGRESS_IC = "/data/haiyangw/nrpic/scratch/core/regress/ic"


def copy_east16(path):
    """Particles (and, next to them, the fields) of the regression case east: periodic
    cosmology at 16^3 (tracks/core/JOURNAL-newton.md)."""
    d = os.path.join(REGRESS_IC, "east16")
    shutil.copyfile(os.path.join(d, "particles.nrp"), path)
    shutil.copyfile(os.path.join(d, "fields.bin"), os.path.join(os.path.dirname(path),
                                                                 "fields.bin"))
    return int(np.fromfile(path, "<i8", count=2)[1])


def copy_random(path):
    """The 10^4 particles of the regression case dep (tracks/core/JOURNAL-newton.md)."""
    shutil.copyfile(os.path.join(REGRESS_IC, "random.nrp"), path)
    return int(np.fromfile(path, "<i8", count=2)[1])


# ----------------------------------------------------------------------------------------
# cases
# ----------------------------------------------------------------------------------------
KERR = "problems/tests/mpi_kerr_swarm.athinput"
GEO = "problems/kerr/geodesic.athinput"
PUNC = "problems/tests/mpi_puncture_exc.athinput"
BOX = "problems/tests/mpi_box_periodic.athinput"
CLUSTER = "problems/tests/mpi_cluster.athinput"
CLUSTER_SMR = "problems/tests/mpi_cluster_smr.athinput"
CLUSTER_AMR = "problems/tests/mpi_cluster_amr.athinput"
SMR = "problems/tests/mpi_deposit_smr.athinput"
EAST = "problems/cosmo/east.athinput"
# the table of the cluster lies next to the particle file ({out} is the output directory)
CLT = ["problem/comp0_file={out}/cluster.tab"]
# (AthenaK changes on the command line only parameters that the input file has: the
# options of the refined-mesh cases are in mpi_deposit_smr.athinput)
SMRT = []
# with deposit every particle is tracked: the file with the metric at the tracked
# particles then samples the deposited E and S_i at all particles in double precision
# (the binary dumps of the sources are single precision)
DEP = ["particles/deposit=true", "particles/traj_ntrack=1000000"]

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
    "t2p_box_comp": dict(input=BOX, particles=("box.nrp", make_box),
                         args=DEP + ["particles/deposit_shape=tsc", "particles/nfilter=2",
                                     "particles/deposit_comp_c=0.125",
                                     "particles/filter_compensate=true",
                                     "particles/interp=bspline", "mesh/nghost=4"]),
    "t2_kerr_cic": dict(input=KERR, particles=("swarm.nrp", make_swarm_bound),
                        args=DEP + ["particles/deposit_shape=cic"]),
    "t2_kerr_pcs": dict(input=KERR, particles=("swarm.nrp", make_swarm_bound),
                        args=DEP + ["particles/deposit_shape=pcs", "particles/nfilter=2"]),
    # step 3: self-gravitating cluster with Z4c on a uniform mesh (also the source of the
    # restart files of test T4)
    "t3_cluster": dict(input=CLUSTER, particles=("cluster.nrp", make_cluster), args=CLT),
    "t3_cluster_ext": dict(input=CLUSTER, particles=("cluster.nrp", make_cluster),
                           args=CLT + ["particles/source_density=true",
                                       "particles/source_extrap=true"]),
    # step 5: statically refined meshes.  dep: 10^4 particles drifting across three
    # levels in flat spacetime (64 + 56 + 56 MeshBlocks); cluster: the cluster of T3 on
    # a mesh whose central MeshBlock is refined once (26 + 8 MeshBlocks)
    "t5_smr_cic": dict(input=SMR, particles=("random.nrp", copy_random),
                       args=SMRT + ["particles/deposit_shape=cic"]),
    "t5_smr_tsc_cap": dict(input=SMR, particles=("random.nrp", copy_random),
                           args=SMRT + ["particles/deposit_shape=tsc", "particles/nfilter=2",
                                        "particles/deposit_max_level=1"]),
    "t5_smr_pcs": dict(input=SMR, particles=("random.nrp", copy_random),
                       args=SMRT + ["particles/deposit_shape=pcs", "particles/nfilter=1"]),
    "t5_smr_cluster": dict(input=CLUSTER_SMR, particles=("cluster.nrp", make_cluster),
                           args=CLT),
    # level of the clouds from the density of the last deposit (deposit_adaptive)
    "t5_smr_adaptive": dict(input=SMR, particles=("random.nrp", copy_random),
                            args=SMRT + ["particles/deposit_shape=tsc",
                                         "particles/deposit_adaptive=true",
                                         "particles/deposit_ppc=8.0"]),
    # step 6: periodic cosmology with Z4c (the regression case east at 16^3: deposit,
    # filter and compensation, conformal-time lapse, density-form sources)
    "t6_cosmo_east": dict(input=EAST, particles=("particles.nrp", copy_east16),
                          args=["problem/id_file={out}/fields.bin", "mesh/nx1=16",
                                "mesh/nx2=16", "mesh/nx3=16", "meshblock/nx1=8",
                                "meshblock/nx2=8", "meshblock/nx3=8", "time/nlim=40",
                                "particles/snap_dt=0.2", "particles/traj_ntrack=1000000",
                                "particles/cstat_dcycle=1"]),
    # adaptive mesh with load balancing: the centre is refined at cycle 4 and the
    # MeshBlocks (and with them the particles) are redistributed over the ranks
    "t5_amr_cluster": dict(input=CLUSTER_AMR, particles=("cluster.nrp", make_cluster),
                           args=CLT),
    # the same with the cluster in one octant: the refined MeshBlocks all lie on the last
    # rank, and load balancing moves MeshBlocks (and their particles) to the others
    "t5_amr_offset": dict(input=CLUSTER_AMR, particles=("cluster.nrp", make_cluster_offset),
                          args=CLT + ["problem/comp0_x1=4.0", "problem/comp0_x2=4.0",
                                      "problem/comp0_x3=4.0"]),
    # step 7 (session mpi-2): what the first session left untested.
    # probes 1 to 7 of the cluster of T3: on the planes between the ranks, at the point
    # where the eight MeshBlocks meet, inside MeshBlocks of different ranks, in the matter
    # and outside; 16 cycles
    "t7_probes": dict(input=CLUSTER, particles=("cluster.nrp", make_cluster),
                      args=CLT + ["time/nlim=16"],
                      add={"particles": ["nprobe = 7",
                                         "probe1_x1 = 0.0", "probe1_x2 = 0.0", "probe1_x3 = 0.0",
                                         "probe2_x1 = 0.0", "probe2_x2 = 2.3", "probe2_x3 = -1.1",
                                         "probe3_x1 = 1.7", "probe3_x2 = 0.0", "probe3_x3 = 0.0",
                                         "probe4_x1 = -3.1", "probe4_x2 = 2.2", "probe4_x3 = 0.0",
                                         "probe5_x1 = 4.4", "probe5_x2 = 4.1", "probe5_x3 = 3.9",
                                         "probe6_x1 = -0.3", "probe6_x2 = -0.3", "probe6_x3 = -0.3",
                                         "probe7_x1 = -9.0", "probe7_x2 = 7.0", "probe7_x3 = -11.6"]}),
    # analytic metric (no MeshBlock is used by the particle: it stays on rank 0); the
    # geodesic of the regression case geo with the mesh cut into eight MeshBlocks
    "t7_analytic": dict(input=GEO, particles=None,
                        args=["time/tlim=20.0", "particles/hist_dcycle=100",
                              "meshblock/nx1=4", "meshblock/nx2=4", "meshblock/nx3=4"]),
    "t7_analytic_boris": dict(input=GEO, particles=None,
                              args=["time/tlim=20.0", "particles/hist_dcycle=100",
                                    "particles/pusher=boris", "particles/metric=lattice",
                                    "meshblock/nx1=4", "meshblock/nx2=4", "meshblock/nx3=4"]),
    # moving puncture with tracker, adaptive mesh and horizon finder; particles removed
    # inside 0.8 of the horizon radius (ah_exc_factor).  First as test particles (the
    # spacetime is that of the vacuum run), then with deposit
    "t7_ah_exc": dict(input=PUNC, particles=("infall.nrp", make_infall),
                      args=["particles/deposit=false"]),
    "t7_ah_exc_dep": dict(input=PUNC, particles=("infall.nrp", make_infall), args=[]),
}

BYTE_PATTERNS = ["*.traj.bin", "*.trajmet.bin", "*.part.*.bin", "rst/*.prt",
                 "*.line.bin", "*.field.*.bin"]
# all histories but *.mpi.hst (which differs by design); the records of the puncture
# tracker and of the horizon finder (text tables)
HIST_PATTERNS = ["*.hst", "*.co_*.txt", "*.horizon_summary_*.txt"]


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


def read_field(path):
    """<basename>.field.NNNNN.bin of the module: time and a dict of arrays (E and chi in
    single precision; with field_constraints the Hamiltonian constraint, the momentum
    constraint, Khat, Theta and the lapse in double precision)."""
    with open(path, "rb") as f:
        magic = f.read(8)
        t = float(np.frombuffer(f.read(8), "<f8")[0])
        n1, n2, n3 = (int(v) for v in np.frombuffer(f.read(24), "<i8"))
        n = n1*n2*n3
        out = dict(E=np.frombuffer(f.read(4*n), "<f4").astype(np.float64),
                   chi=np.frombuffer(f.read(4*n), "<f4").astype(np.float64))
        if magic == b"NRFIELD2":
            for name in ("H", "M_x", "M_y", "M_z", "Khat", "Theta", "alpha"):
                out[name] = np.frombuffer(f.read(8*n), "<f8")
    for k in out:
        out[k] = out[k].reshape(n3, n2, n1)
    return t, out


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


def input_with(src, dst, add):
    """Copy of an input file with lines added at the end of the named blocks."""
    out, cur = [], None
    with open(src) as f:
        lines = f.readlines()
    for line in lines + ["<end_of_file>\n"]:
        s = line.strip()
        if s.startswith("<") and s.endswith(">"):
            if cur in add:
                while out and not out[-1].strip():
                    out.pop()
                out.extend(x + "\n" for x in add[cur])
                out.append("\n")
            cur = s.strip("<>")
            if cur == "end_of_file":
                break
        out.append(line)
    with open(dst, "w") as f:
        f.writelines(out)


def run_case(case, ranks, exe, out, extra, max_cores=6):
    """Runs the case on each rank count; runs go side by side as long as their ranks
    together stay within max_cores (CLAUDE.md: six cores per session)."""
    spec = CASES[case]
    os.makedirs(out, exist_ok=True)
    npart, pargs = None, []
    if spec.get("particles"):
        pname, maker = spec["particles"]
        ppath = os.path.join(out, pname)
        npart = maker(ppath)
        pargs = ["particles/particle_file=" + ppath]
    inp = os.path.join(REPO, spec["input"])
    if spec.get("drop"):
        stripped = os.path.join(out, os.path.basename(inp))
        input_without(inp, stripped, spec["drop"])
        inp = stripped
    if spec.get("add"):
        added = os.path.join(out, os.path.basename(inp))
        input_with(inp, added, spec["add"])
        inp = added
    todo = sorted(ranks, reverse=True)
    running, res = [], {}

    def reap(block):
        for item in list(running):
            n, d, cmd, t0, p, log = item
            rc = p.wait() if block else p.poll()
            if rc is None:
                continue
            log.close()
            running.remove(item)
            res[n] = dict(dir=d, command=cmd, exit=rc, wall_s=round(time.time() - t0, 1))
            print("np=%d exit=%d wall=%.1f s" % (n, rc, res[n]["wall_s"]), flush=True)
            if block:
                return

    while todo or running:
        busy = sum(item[0] for item in running)
        fits = [n for n in todo if busy + n <= max_cores] or ([] if running else todo[:1])
        if fits:
            n = fits[0]
            todo.remove(n)
            d = os.path.join(out, "np%d" % n)
            os.makedirs(d, exist_ok=True)
            args = [x.replace("{out}", out) for x in spec["args"]]
            cmd = [MPIRUN, "--bind-to", "none", "-np", str(n), exe, "-i", inp, "-d", d] \
                + pargs + args + extra
            log = open(os.path.join(d, "run.log"), "w")
            env = dict(os.environ, OMP_NUM_THREADS="1")
            running.append((n, d, cmd, time.time(),
                            subprocess.Popen(cmd, cwd=d, stdout=log, stderr=subprocess.STDOUT,
                                             env=env), log))
            continue
        reap(False)
        if running and not [n for n in todo if sum(i[0] for i in running) + n <= max_cores]:
            time.sleep(1.0)
    return npart, {n: res[n] for n in ranks}


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
                    # the header holds seven doubles (bytes 16 to 71): proper time, lapse
                    # and deposited energy density at the probe, the rest mass removed
                    # by excision and at the boundary, two output times.  The energy
                    # density and the two masses are sums whose order depends on the
                    # ranks; everything else in the file must be identical.
                    a, b = open(f, "rb").read(), open(g, "rb").read()
                    da = np.frombuffer(a[16:72], "<f8")
                    db = np.frombuffer(b[16:72], "<f8")
                    sc = np.maximum(np.abs(da), 1.0e-300)
                    row["np%d_rest_identical" % n] = (
                        len(a) == len(b) and a[:16] == b[:16] and a[72:] == b[72:])
                    row["np%d_header_max_rel" % n] = float((np.abs(da - db)/sc).max())
                    row["np%d_header_exact" % n] = [bool(v) for v in (da == db)]
            result["bytes"][rel] = row
    # ---- metric and deposited sources at the tracked particles (records of 17 doubles:
    #      time, tag, 10 metric components, proper time, E, S_x, S_y, S_z)
    for f in sorted(glob.glob(os.path.join(ref, "*.trajmet.bin"))):
        a = np.fromfile(f, "<f8").reshape(-1, 17)
        result["trajmet"] = dict(records=int(a.shape[0]))
        for n in ranks[1:]:
            g = os.path.join(out, "np%d" % n, os.path.relpath(f, ref))
            b = np.fromfile(g, "<f8").reshape(-1, 17) if os.path.exists(g) else None
            if b is None or b.shape != a.shape:
                result["trajmet"]["np%d" % n] = "missing or of another size"
                continue
            sc = np.maximum(np.abs(a[:, 13:]).max(axis=0), 1.0e-300)
            result["trajmet"]["np%d" % n] = dict(
                metric_identical=bool(np.array_equal(a[:, :13], b[:, :13])),
                sources_max_rel=float((np.abs(a[:, 13:] - b[:, 13:]).max(axis=0)/sc).max()))
    # ---- histories
    for pat in HIST_PATTERNS:
        for f in sorted(glob.glob(os.path.join(ref, pat))):
            if f.endswith(".mpi.hst"):
                continue
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
    # ---- field dumps of the module and the line dump, numerically
    result["field_dumps"] = {}
    for f in sorted(glob.glob(os.path.join(ref, "*.field.*.bin"))):
        rel = os.path.relpath(f, ref)
        t, a = read_field(f)
        row = dict(time=t)
        for n in ranks[1:]:
            g = os.path.join(out, "np%d" % n, rel)
            if not os.path.exists(g):
                row["np%d" % n] = "missing"
                continue
            t2, b = read_field(g)
            row["np%d" % n] = {k: float(np.abs(a[k] - b[k]).max()/max(np.abs(a[k]).max(), 1e-300))
                               for k in a}
        result["field_dumps"][rel] = row
    result["line"] = {}
    for f in sorted(glob.glob(os.path.join(ref, "*.line.bin"))):
        rel = os.path.relpath(f, ref)
        txts = [t for t in [f[:-4] + ".txt"] + [os.path.join(out, "np%d" % n, rel[:-4] + ".txt")
                                                for n in ranks] if os.path.exists(t)]
        if not txts:          # (a restarted run writes no header of the line dump)
            continue
        ng = int(open(txts[0]).read().splitlines()[1])
        a = np.fromfile(f, "<f8").reshape(-1, 1 + 5*ng)
        row = dict(records=int(len(a)))
        for n in ranks[1:]:
            g = os.path.join(out, "np%d" % n, rel)
            b = np.fromfile(g, "<f8").reshape(-1, 1 + 5*ng) if os.path.exists(g) else None
            if b is None or b.shape != a.shape:
                row["np%d" % n] = "missing or of another size"
                continue
            row["np%d" % n] = {name: float(np.abs(a[:, 1+v*ng:1+(v+1)*ng] - b[:, 1+v*ng:1+(v+1)*ng]).max()
                                           / max(np.abs(a[:, 1+v*ng:1+(v+1)*ng]).max(), 1e-300))
                               for v, name in enumerate(("chi", "alpha", "K", "E", "S_x"))}
        result["line"][rel] = row
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


# ----------------------------------------------------------------------------------------
# test T4: restart on the same and on another number of ranks
# ----------------------------------------------------------------------------------------
def run_restart(src, pairs, exe, out, rst):
    procs = []
    for w, r in pairs:
        d = os.path.join(out, "w%dr%d" % (w, r))
        os.makedirs(d, exist_ok=True)
        cmd = [MPIRUN, "--bind-to", "none", "-np", str(r), exe, "-r",
               os.path.join(src, "np%d" % w, rst), "-d", d]
        log = open(os.path.join(d, "run.log"), "w")
        env = dict(os.environ, OMP_NUM_THREADS="1")
        procs.append(((w, r), d, cmd, time.time(),
                      subprocess.Popen(cmd, cwd=d, stdout=log, stderr=subprocess.STDOUT,
                                       env=env), log))
    res = {}
    for (w, r), d, cmd, t0, p, log in procs:
        rc = p.wait()
        log.close()
        res["%d:%d" % (w, r)] = dict(dir=d, command=cmd, exit=rc,
                                     wall_s=round(time.time() - t0, 1))
        print("restart w=%d r=%d exit=%d wall=%.1f s" % (w, r, rc, time.time() - t0),
              flush=True)
    return res


def _rst_data(path):
    """bytes of a mesh restart file after its parameter header (which holds the name of
    the file a run was restarted from, so it differs between the runs)"""
    b = open(path, "rb").read()
    k = b.find(b"<par_end>")
    return b[k:] if k >= 0 else b


def _tail_compare(full, part, nrec):
    """the records of part (binary file of nrec doubles per record) against the last
    records of full: identical bytes, or the largest difference relative to the largest
    magnitude of each column"""
    a = np.fromfile(full, "<f8").reshape(-1, nrec)
    b = np.fromfile(part, "<f8").reshape(-1, nrec)
    if len(b) > len(a) or len(b) == 0:
        return dict(records=int(len(b)), note="more records than the full run or none")
    a = a[len(a) - len(b):]
    if not np.array_equal(a[:, 0], b[:, 0]):
        return dict(records=int(len(b)), note="times differ")
    same = bool(np.array_equal(a, b))
    sc = np.maximum(np.abs(a).max(axis=0), 1.0e-300)
    return dict(records=int(len(b)), identical=same,
                max_rel=float((np.abs(a - b).max(axis=0)/sc).max()))


def compare_restart(src, pairs, out):
    result = {}
    for w, r in pairs:
        d = os.path.join(out, "w%dr%d" % (w, r))
        row = {}
        for label, n in (("same_ranks_as_writer", w), ("same_ranks_as_reader", r)):
            if label == "same_ranks_as_reader" and r == w:
                continue
            full = os.path.join(src, "np%d" % n)
            cmp = dict(full_run="np%d" % n, files={})
            # binary records
            for pat, nrec in (("*.traj.bin", 8), ("*.trajmet.bin", 17)):
                for f in sorted(glob.glob(os.path.join(d, pat))):
                    g = os.path.join(full, os.path.basename(f))
                    if os.path.exists(g):
                        cmp["files"][os.path.basename(f)] = _tail_compare(g, f, nrec)
            for f in sorted(glob.glob(os.path.join(d, "*.line.bin"))):
                g = os.path.join(full, os.path.basename(f))
                txt = os.path.join(full, os.path.basename(f)[:-4] + ".txt")
                if os.path.exists(g) and os.path.exists(txt):
                    ng = int(open(txt).read().splitlines()[1])
                    cmp["files"][os.path.basename(f)] = _tail_compare(g, f, 1 + 5*ng)
            # histories: the records of the restarted run against the last ones of the
            # full run
            for f in sorted(glob.glob(os.path.join(d, "*.hst"))):
                if f.endswith(".mpi.hst"):
                    continue
                g = os.path.join(full, os.path.basename(f))
                if not os.path.exists(g):
                    continue
                b = read_table(f)
                a = read_table(g)
                if b.size == 0 or a.shape[1] != b.shape[1] or len(b) > len(a):
                    cmp["files"][os.path.basename(f)] = dict(note="shapes %s %s" % (a.shape, b.shape))
                    continue
                a = a[len(a) - len(b):]
                fin = np.where(np.isfinite(a), a, 0.0)
                sc = np.maximum(np.abs(fin).max(axis=0), 1.0e-300)
                with np.errstate(invalid="ignore"):
                    diff = np.where(a == b, 0.0, np.abs(a - b))
                cmp["files"][os.path.basename(f)] = dict(
                    records=int(len(b)), identical=bool((diff == 0).all()),
                    times_equal=bool(np.array_equal(a[:, 0], b[:, 0])),
                    max_rel=float((diff.max(axis=0)/sc).max()))
            # snapshots and field dumps written by both
            for pat in ("*.part.*.bin", "*.field.*.bin"):
                for f in sorted(glob.glob(os.path.join(d, pat))):
                    g = os.path.join(full, os.path.basename(f))
                    if not os.path.exists(g):
                        continue
                    row_f = dict(identical=(sha256(f) == sha256(g)))
                    if ".part." in f and not row_f["identical"]:
                        t1, r1, g1 = read_snapshot(g)
                        t2, r2, g2 = read_snapshot(f)
                        row_f["max_diff"] = (float(np.abs(r1 - r2).max())
                                             if np.array_equal(g1, g2) else "particles differ")
                    cmp["files"][os.path.basename(f)] = row_f
            # final restart files
            for f in sorted(glob.glob(os.path.join(d, "rst", "*.rst"))):
                g = os.path.join(full, "rst", os.path.basename(f))
                if not os.path.exists(g):
                    continue
                cmp["files"]["rst/" + os.path.basename(f)] = dict(
                    identical_after_header=(_rst_data(f) == _rst_data(g)))
                if os.path.exists(f + ".prt") and os.path.exists(g + ".prt"):
                    cmp["files"]["rst/" + os.path.basename(f) + ".prt"] = dict(
                        identical=(sha256(f + ".prt") == sha256(g + ".prt")))
            row[label] = cmp
        result["%d:%d" % (w, r)] = row
    return result


def restart_lines(result):
    lines = []
    for pair, row in result.items():
        for label, cmp in row.items():
            parts = []
            for name, v in cmp["files"].items():
                if "note" in v:
                    parts.append("%s: %s" % (name, v["note"]))
                elif v.get("identical") or v.get("identical_after_header"):
                    parts.append("%s: identical" % name)
                elif "max_rel" in v:
                    parts.append("%s: max rel %.1e" % (name, v["max_rel"]))
                elif "max_diff" in v:
                    parts.append("%s: max diff %s" % (name, v["max_diff"]))
                else:
                    parts.append("%s: DIFFERENT" % name)
            lines.append("restart %s against %s: %s" % (pair, cmp["full_run"], "; ".join(parts)))
    return lines


def summary_lines(result):
    lines = []
    ranks = result["ranks"]
    for rel, row in result["bytes"].items():
        def word(n):
            if row["np%d" % n]:
                return "identical"
            if row.get("np%d_rest_identical" % n):
                return "identical but for header sums (max rel %.1e)" % \
                    row["np%d_header_max_rel" % n]
            if rel.endswith(".trajmet.bin") and "trajmet" in result:
                v = result["trajmet"].get("np%d" % n)
                if isinstance(v, dict):
                    return ("metric and proper time %s, E and S_i at the particles max rel"
                            " %.1e" % ("identical" if v["metric_identical"] else
                                       "DIFFERENT", v["sources_max_rel"]))
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
                         else "max rel %.2e (%s; single precision)" % (
                             row["np%d" % n]["max_rel"], row["np%d" % n]["component"]))
            for n in ranks[1:])))
    for rel, row in result.get("field_dumps", {}).items():
        lines.append("fdump   %-28s t=%.4g %s" % (rel, row["time"], "  ".join(
            "np%d:%s" % (n, row["np%d" % n] if isinstance(row["np%d" % n], str) else
                         "max rel %.1e (%s)" % (max(row["np%d" % n].values()),
                                                max(row["np%d" % n], key=row["np%d" % n].get)))
            for n in ranks[1:])))
    for rel, row in result.get("line", {}).items():
        lines.append("line    %-28s %d records %s" % (rel, row["records"], "  ".join(
            "np%d:%s" % (n, row["np%d" % n] if isinstance(row["np%d" % n], str) else
                         "max rel %.1e (%s)" % (max(row["np%d" % n].values()),
                                                max(row["np%d" % n], key=row["np%d" % n].get)))
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
    ap.add_argument("--case", choices=sorted(CASES))
    ap.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 4])
    ap.add_argument("--exe", default=DEFAULT_EXE)
    ap.add_argument("--out", default=None)
    ap.add_argument("--figdir", default=None)
    ap.add_argument("--compare-only", action="store_true")
    ap.add_argument("--max-cores", type=int, default=6,
                    help="ranks of the runs that go side by side (default 6)")
    ap.add_argument("--restart-of", default=None,
                    help="output directory of an earlier case (test T4)")
    ap.add_argument("--pairs", nargs="+", default=["1:1", "2:2", "4:4", "1:4", "4:2"],
                    help="w:r, restart the file written on w ranks on r ranks")
    ap.add_argument("--rst", default="rst/cl.00001.rst")
    ap.add_argument("extra", nargs="*", help="further athena arguments (block/key=value)")
    a = ap.parse_args()
    if a.restart_of:
        src = os.path.abspath(a.restart_of)
        base = os.path.abspath(a.out or os.path.join(os.environ.get("NRPIC_RUN_DIR",
                                                                     os.getcwd()), "t4_restart"))
        pairs = [tuple(int(v) for v in q.split(":")) for q in a.pairs]
        runs = {} if a.compare_only else run_restart(src, pairs, a.exe, base, a.rst)
        result = dict(source=src, rst=a.rst, runs=runs, exe=a.exe,
                      compare=compare_restart(src, pairs, base))
        with open(os.path.join(base, "compare.json"), "w") as f:
            json.dump(result, f, indent=1)
        for line in restart_lines(result["compare"]):
            print(line)
        try:
            import mpi_figs
            for path in mpi_figs.make_restart(src, pairs, base, a.figdir):
                print("figure", path)
        except Exception as exc:
            print("figures failed:", repr(exc))
        return 1 if any(v["exit"] != 0 for v in runs.values()) else 0
    if not a.case:
        ap.error("--case or --restart-of is required")
    base = os.path.abspath(a.out or os.path.join(os.environ.get("NRPIC_RUN_DIR",
                                                                 os.getcwd()), a.case))
    npart, runs = None, {}
    if not a.compare_only:
        npart, runs = run_case(a.case, a.ranks, a.exe, base, a.extra, a.max_cores)
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
