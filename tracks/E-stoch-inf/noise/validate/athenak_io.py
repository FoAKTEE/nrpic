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


def read_run(path):
    """A run directory of AthenaK `bin` files, or an `.npz` file of the self-test."""
    if path.endswith(".npz"):
        return read_npz(path)
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
