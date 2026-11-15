"""Read the noise unit test (NOISE_SPEC.md, section 9) from AthenaK output.

`read_run(dir)` reads every `*.bin` file of a run directory with the reader of this
repository (`athenak/vis/python/bin_convert.py: read_binary`, imported read-only),
assembles the MeshBlocks of a uniform mesh into arrays indexed [i, j, k] = (x, y, z), and
takes the parameters from the input file stored in the file header. It also reads the
`.npz` runs written by the self-test (`selftest.py`), which carry the same content.

Run dictionary: params (dict, NOISE_SPEC names), N, L, x0, precision ('double' or
'single'), outputs {cycle: {'time': t, 'fields': {name: array}}}.
"""
import glob
import json
import os
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "athenak", "vis", "python"))

NOISE_VARS = ("stoch_c0", "stoch_c1", "stoch_c2", "stoch_c3", "stoch_acc0")


def header_params(header):
    """{'<block>/key': value-string} from the input-file lines of a bin header."""
    out = {}
    block = "<none>"
    for line in header:
        if line.startswith("<"):
            block = line.strip()
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            out[f"{block}/{k.strip()}"] = v.strip()
    return out


def params_from_header(hp):
    """NOISE_SPEC section 9 parameters from the header dictionary (names proposed there;
    if core renames them, only this function changes)."""
    def g(key, default=None, typ=str):
        v = hp.get(key, default)
        return typ(v) if v is not None else None
    N = g("<mesh>/nx1", typ=int)
    x0 = g("<mesh>/x1min", typ=float)
    L = g("<mesh>/x1max", typ=float) - x0
    return dict(seed=g("<job>/rng_seed", "0", lambda s: int(s, 0)),
                scheme=g("<stochastic>/scheme", "frozen"),
                amplitudes=g("<stochastic>/amplitudes", "hemisphere"),
                nmax2=g("<stochastic>/nmax2", typ=int),
                N=N, L=L, x0=x0,
                window=g("<problem>/window", "tanh"),
                sharpness=g("<problem>/sharpness", "5.0", float),
                ksigma0=g("<problem>/ksigma0", typ=float),
                hubble=g("<problem>/hubble", typ=float),
                amp=g("<problem>/amp", "1.0", float),
                phase1=g("<problem>/phase1", typ=float),
                dt=g("<problem>/dt_test", typ=float),
                t0=0.0)


def assemble(fd, var):
    """Uniform-mesh array [i, j, k] of one variable from read_binary output."""
    levels = np.unique(fd["mb_logical"][:, 3])
    if levels.size != 1:
        raise ValueError("refined meshes are not handled by the noise validation")
    nx1, nx2, nx3 = fd["nx1_out_mb"], fd["nx2_out_mb"], fd["nx3_out_mb"]
    if (nx1, nx2, nx3) != (fd["nx1_mb"], fd["nx2_mb"], fd["nx3_mb"]):
        raise ValueError("output with ghost zones or a slice is not handled")
    out = np.full((fd["Nx1"], fd["Nx2"], fd["Nx3"]), np.nan)
    for m, blk in enumerate(fd["mb_data"][var]):
        lx1, lx2, lx3, _ = fd["mb_logical"][m]
        out[lx1 * nx1:(lx1 + 1) * nx1, lx2 * nx2:(lx2 + 1) * nx2,
            lx3 * nx3:(lx3 + 1) * nx3] = np.transpose(blk, (2, 1, 0))
    if np.isnan(out).any():
        raise ValueError("MeshBlocks do not cover the mesh")
    return out


def read_bin_file(path):
    from bin_convert import read_binary
    fd = read_binary(path)
    with open(path, "rb") as f:
        head = f.read(400).decode("latin-1")
    prec = "double" if "size of variable=8" in head else "single"
    return fd, prec


def parse_athinput(path):
    """{'<block>/key': value-string} of an AthenaK input file."""
    out, block = {}, "<none>"
    with open(path) as f:
        for line in f:
            line = line.split("#")[0].strip()
            if not line:
                continue
            if line.startswith("<"):
                block = line.split(">")[0] + ">"
            elif "=" in line:
                k, v = line.split("=", 1)
                out[f"{block}/{k.strip()}"] = v.strip()
    return out


def params_from_scalar_field(hp):
    """Parameters of core's model `<scalar_field> noise = power` (branch core/scalar-field,
    athenak/src/scalar_field/scalar_field_noise.cpp, NoiseInit) in the names of
    noise_ref; defaults as in the code."""
    def g(key, default=None, typ=str):
        v = hp.get(key, default)
        return typ(v) if v is not None else None
    model = g("<scalar_field>/noise", "none")
    if model != "power":
        raise ValueError(f"noise = {model}: only the power model is validated here")
    N = g("<mesh>/nx1", typ=int)
    x0 = g("<mesh>/x1min", typ=float)
    return dict(seed=g("<job>/rng_seed", "0", lambda s: int(s, 0)),
                scheme=g("<scalar_field>/noise_scheme", "frozen"),
                amplitudes="hemisphere", frozen_form="increment",
                nmax2=g("<scalar_field>/noise_nmax2", typ=int),
                N=N, L=g("<mesh>/x1max", typ=float) - x0, x0=x0,
                window=g("<scalar_field>/noise_window", "tanh"),
                sharpness=g("<scalar_field>/noise_sharpness", "5.0", float),
                ksigma0=g("<scalar_field>/noise_ksigma0", "1.0", float),
                hubble=g("<scalar_field>/noise_hubble", "1.0", float),
                t0w=g("<scalar_field>/noise_t0", "0.0", float),
                amp=g("<scalar_field>/noise_amp", "1.0", float),
                tilt=g("<scalar_field>/noise_tilt", "0.0", float),
                pi_dof=g("<scalar_field>/noise_pi_dof", "1", int),
                phase1=0.0, dt=None, t0=0.0)


def read_nrsf_dump(path):
    """One NRSFDMP1 dump (scalar_field_io.cpp lines 12-17): cycle, time, the uniform
    mesh arrays [i, j, k] of all variables, MeshBlock size and count."""
    with open(path, "rb") as f:
        if f.read(8) != b"NRSFDMP1":
            raise ValueError(f"{path}: not an NRSFDMP1 dump")
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = np.frombuffer(f.read(56), dtype="<i8")
        time = float(np.frombuffer(f.read(8), dtype="<f8")[0])
        blocks = []
        for _ in range(int(nmb)):
            lev, lx1, lx2, lx3 = np.frombuffer(f.read(32), dtype="<i8")
            ext = np.frombuffer(f.read(48), dtype="<f8")
            data = np.frombuffer(f.read(8 * int(nvar * nx1 * nx2 * nx3)), dtype="<f8")
            blocks.append((int(lev), int(lx1), int(lx2), int(lx3), ext,
                           data.reshape(int(nvar), int(nx3), int(nx2), int(nx1))))
    if any(b[0] != 0 for b in blocks):
        raise ValueError("refined meshes are not handled by the noise validation")
    nb = [max(b[i] for b in blocks) + 1 for i in (1, 2, 3)]
    shape = (nb[0] * int(nx1), nb[1] * int(nx2), nb[2] * int(nx3))
    arrays = np.full((int(nvar),) + shape, np.nan)
    for lev, lx1, lx2, lx3, ext, d in blocks:
        arrays[:, lx1 * nx1:(lx1 + 1) * nx1, lx2 * nx2:(lx2 + 1) * nx2,
               lx3 * nx3:(lx3 + 1) * nx3] = np.transpose(d, (0, 3, 2, 1))
    if np.isnan(arrays).any():
        raise ValueError("MeshBlocks do not cover the mesh")
    xmin = min(b[4][0] for b in blocks)
    xmax = max(b[4][1] for b in blocks)
    return dict(cycle=int(cycle), time=time, nnoise=int(nnoise), nvar=int(nvar),
                arrays=arrays, nmb=int(nmb), N=shape[0], x0=float(xmin),
                L=float(xmax - xmin))


def read_dump_run(path, input_file):
    """A run directory of NRSFDMP1 dumps of core's power model; parameters from the
    run's input file. Field 0 -> stoch_c0 (dof 0); field 1 -> stoch_c2 (noise_pi_dof = 1,
    independent) or stoch_c1 with phase1 = 0 (noise_pi_dof = 0, shared). Cycle 0 is
    skipped (no step has been taken); dt = time / cycle, checked to be constant."""
    p = params_from_scalar_field(parse_athinput(input_file))
    files = sorted(glob.glob(os.path.join(path, "**", "*.sf.*.dump"), recursive=True))
    if not files:
        raise FileNotFoundError(f"no .sf.*.dump files under {path}")
    name1 = "stoch_c2" if p["pi_dof"] == 1 else "stoch_c1"
    run = dict(params=p, N=p["N"], L=p["L"], x0=p["x0"], precision="double", outputs={},
               files=[], expected_vars=("stoch_c0", name1))
    dts = []
    for fp in files:
        d = read_nrsf_dump(fp)
        if d["cycle"] == 0:
            continue
        if d["nnoise"] != 2:
            raise ValueError(f"{fp}: {d['nnoise']} noise fields, the power model has 2")
        a = d["arrays"]
        if len(set(a.shape[1:])) != 1:
            raise ValueError("the noise validation needs a cubic mesh")
        p.update(N=d["N"], L=d["L"], x0=d["x0"])            # geometry of the dump itself
        run.update(N=d["N"], L=d["L"], x0=d["x0"])
        run["outputs"][d["cycle"]] = {"time": d["time"], "fields": {
            "stoch_c0": a[d["nvar"] - 2], name1: a[d["nvar"] - 1]}}
        dts.append(d["time"] / d["cycle"])
        run["files"].append(fp)
    if not dts:
        raise ValueError("no dump after cycle 0")
    dt = float(np.median(dts))
    if max(abs(x - dt) for x in dts) > 1e-12 * dt:
        raise ValueError(f"time step not constant: time/cycle = {dts}")
    p["dt"] = dt
    return run


def read_run(path, input_file=None):
    """A run directory of AthenaK `bin` files, of NRSFDMP1 dumps (with input_file), or an
    `.npz` file of the self-test."""
    if path.endswith(".npz"):
        return read_npz(path)
    if input_file is not None:
        return read_dump_run(path, input_file)
    files = sorted(glob.glob(os.path.join(path, "**", "*.bin"), recursive=True))
    if not files:
        raise FileNotFoundError(f"no .bin files under {path}")
    run = None
    for fp in files:
        fd, prec = read_bin_file(fp)
        names = [v for v in fd["var_names"] if v in NOISE_VARS]
        if not names:
            continue
        if run is None:
            p = params_from_header(header_params(fd["header"]))
            run = dict(params=p, N=p["N"], L=p["L"], x0=p["x0"], precision=prec,
                       outputs={}, files=[])
        cyc = int(fd["cycle"])
        o = run["outputs"].setdefault(cyc, {"time": float(fd["time"]), "fields": {}})
        for v in names:
            o["fields"][v] = assemble(fd, v)
        run["files"].append(fp)
    if run is None:
        raise ValueError(f"no noise variables in {path}")
    return run


def write_npz(path, run):
    arrays = {}
    for cyc, o in run["outputs"].items():
        for v, a in o["fields"].items():
            arrays[f"{v}@{cyc}"] = a
        arrays[f"time@{cyc}"] = np.array(o["time"])
    meta = dict(params={k: (list(v) if isinstance(v, tuple) else v)
                        for k, v in run["params"].items()},
                precision=run["precision"])
    np.savez(path, meta=np.array(json.dumps(meta)), **arrays)


def read_npz(path):
    d = np.load(path, allow_pickle=False)
    meta = json.loads(str(d["meta"]))
    p = meta["params"]
    run = dict(params=p, N=p["N"], L=p["L"], x0=p["x0"], precision=meta["precision"],
               outputs={}, files=[path])
    for key in d.files:
        if "@" not in key:
            continue
        v, cyc = key.split("@")
        o = run["outputs"].setdefault(int(cyc), {"time": None, "fields": {}})
        if v == "time":
            o["time"] = float(d[key])
        else:
            o["fields"][v] = d[key]
    return run
