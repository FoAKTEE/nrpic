"""Shared helpers of the multi-puncture tests (tracks/core/JOURNAL-mp.md): readers of
AthenaK outputs, the run registry, and the closed forms the mesh data are compared
with (python/nrpic/bowen_york.py)."""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
RUNS = os.path.join(WT, "tracks", "core", "runs")
FIGS = os.path.join(HERE, "figs")
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "athenak", "vis", "python"))
import bin_convert  # noqa: E402
from nrpic import bowen_york as by  # noqa: E402
from nrpic import figstyle  # noqa: E402


# ----------------------------------------------------------------------------------------
# run registry
# ----------------------------------------------------------------------------------------
def manifests():
    out = []
    for p in sorted(glob.glob(os.path.join(RUNS, "*", "manifest.json"))):
        with open(p) as f:
            out.append(json.load(f))
    return out


def run_by_label(label, status="done"):
    """Newest registered run with this label (and status)."""
    hit = [m for m in manifests() if m.get("label") == label
           and (status is None or m.get("status") == status)]
    if not hit:
        raise KeyError("no registered run with label " + label)
    return hit[-1]


def run_dir(label):
    return run_by_label(label)["output_directory"]


# ----------------------------------------------------------------------------------------
# readers
# ----------------------------------------------------------------------------------------
def read_bin(path):
    """AthenaK binary dump -> (time, params, x, y, z, dx, vars) with flat float64 arrays
    over all cells; params is {block: {key: value}} of the parameter dump in the file."""
    fd = bin_convert.read_binary(path)
    par, blk = {}, None
    for line in fd["header"]:
        if line.startswith("<"):
            blk = line.strip("<>")
            par.setdefault(blk, {})
        elif "=" in line and blk is not None:
            k, v = line.split("=", 1)
            par[blk][k.strip()] = v.strip()
    xs, ys, zs, dxs = [], [], [], []
    n1, n2, n3 = fd["nx1_out_mb"], fd["nx2_out_mb"], fd["nx3_out_mb"]
    # each block: x1min, x1max, x2min, x2max, x3min, x3max (outputs/binary.cpp; the
    # docstring of bin_convert.py says otherwise). A sliced direction has one cell and
    # the full extent of the block: its coordinate is then the block centre, not the
    # position of the slice.
    for g in fd["mb_geometry"]:
        d1, d2, d3 = (g[1] - g[0]) / n1, (g[3] - g[2]) / n2, (g[5] - g[4]) / n3
        x = g[0] + (np.arange(n1) + 0.5) * d1
        y = g[2] + (np.arange(n2) + 0.5) * d2
        z = g[4] + (np.arange(n3) + 0.5) * d3
        Z, Y, X = np.meshgrid(z, y, x, indexing="ij")
        xs.append(X.ravel())
        ys.append(Y.ravel())
        zs.append(Z.ravel())
        dxs.append(np.full(X.size, d1))
    var = {k: np.concatenate([np.asarray(a, dtype=np.float64).ravel() for a in v])
           for k, v in fd["mb_data"].items()}
    return (fd["time"], par, np.concatenate(xs), np.concatenate(ys), np.concatenate(zs),
            np.concatenate(dxs), var)


def read_table_file(path, comment="#"):
    """Whitespace table with comment lines -> 2D array (rows that parse)."""
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith(comment):
                continue
            try:
                rows.append([float(t) for t in s.split()])
            except ValueError:
                continue
    n = min(len(r) for r in rows)
    return np.array([r[:n] for r in rows])


def read_hst(path):
    """Z4c history -> dict of columns by name (last record of each time kept)."""
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("#") and "[1]" in line:
                names = [t.split("=")[1] for t in line[1:].split()]
    a = read_table_file(path)
    _, idx = np.unique(a[:, 0][::-1], return_index=True)
    a = a[::-1][idx]
    return {nm: a[:, i] for i, nm in enumerate(names[:a.shape[1]])}


def read_tracker(path):
    """Tracker file -> dict t, x (N,3), v (N,3)."""
    a = read_table_file(path)
    return {"t": a[:, 1], "x": a[:, 2:5], "v": a[:, 5:8]}


def read_horizon(path):
    """Horizon summary -> dict of columns; rows without a horizon (nan mass) dropped."""
    a = read_table_file(path)
    cols = ["iter", "t", "mass", "Sx", "Sy", "Sz", "S", "area", "hrms", "hmean",
            "meanradius", "minradius"]
    ok = np.isfinite(a[:, 2])
    return {c: a[ok, i] for i, c in enumerate(cols)}, int(np.sum(~ok))


# ----------------------------------------------------------------------------------------
# closed forms on the mesh
# ----------------------------------------------------------------------------------------
def punctures(par, rundir):
    """Puncture components of a parameter dump as dicts for nrpic.bowen_york."""
    pr = par["problem"]
    out = []
    for c in range(int(pr["ncomp"])):
        pre = f"comp{c}_"
        if pr[pre + "type"] != "puncture":
            continue
        g = lambda k, d=0.0: float(pr.get(pre + k, d))  # noqa: E731
        p = {"pos": np.array([g("x1"), g("x2"), g("x3")]), "m": g("mass"),
             "P": np.array([g("p1"), g("p2"), g("p3")]),
             "S": np.array([g("s1"), g("s2"), g("s3")]),
             "corr": pr.get(pre + "corr", "none")}
        if p["corr"] == "table":
            p["table"] = by.read_table(os.path.join(rundir, pr[pre + "corr_file"]))
            ax = p["table"]["axis"]
            if pre + "corr_axis1" in pr:
                ax = [g("corr_axis1"), g("corr_axis2"), g("corr_axis3")]
            if ax is None:
                ax = p["P"] if np.any(p["P"] != 0.0) else p["S"]
            p["axis"] = np.asarray(ax, dtype=float)
        out.append(p)
    # background conformal factor of the other punctures (approx only)
    bg = pr.get("corr_background", "true").split()[0].lower() in ("true", "1")
    for c, p in enumerate(out):
        p["lam"] = 1.0
        if p["corr"] == "approx" and bg:
            p["lam"] += sum(0.5 * q["m"] / np.linalg.norm(q["pos"] - p["pos"])
                            for j, q in enumerate(out) if j != c)
    return out


def correction(pts, p):
    """Correction u_c of one puncture at pts as the generator evaluates it."""
    if p["corr"] == "approx":
        return by.approx_u(pts, p["pos"], p["m"], p["P"], p["S"], lam=p.get("lam", 1.0))
    if p["corr"] == "table":
        return by.eval_table(p["table"], pts, p["pos"], p["axis"])
    return np.zeros(len(pts))


def lap_fd(f, pts, h):
    """Flat Laplacian of f at pts by sixth-order central differences of step h (array
    per point allowed)."""
    c = np.array([1 / 90, -3 / 20, 3 / 2, -49 / 18, 3 / 2, -3 / 20, 1 / 90])
    out = 0.0
    for j in range(3):
        for k, ck in zip(range(-3, 4), c):
            e = np.zeros(3)
            e[j] = k
            out = out + ck * f(pts + e[None, :] * h[:, None])
    return out / h**2


def closed_forms(pts, puncs):
    """psi, K_ij (N,3,3) and the Hamiltonian residual H = -8 psi^-5 lap(u) - psi^-12
    Abar^2 at pts for a list of punctures with their corrections. The Laplacian of a
    correction is known in closed form: lap u_c = -(1/8) psi_c^-7 Abar_c^2 with
    psi_c = Lambda_c + m_c/(2 r_c) for `approx` (Lambda_c the background factor, 1 for
    an isolated puncture) and for a table of the second-order solution, and with
    psi_c = 1 + m_c/(2 r_c) + u_c for a table of the full solution (header entry
    nonlinear = 1), up to the accuracy of the table."""
    psi = by.psi_bl(pts, puncs)
    ab = 0.0
    lap = np.zeros(len(pts))
    for p in puncs:
        a = by.abar(pts, p["pos"], p["P"], p["S"])
        ab = ab + a
        if p["corr"] in ("approx", "table"):
            _, r = by._disp(pts, p["pos"])
            uc = correction(pts, p)
            lam = p.get("lam", 1.0) if p["corr"] == "approx" else 1.0
            psic = lam + 0.5 * p["m"] / r
            if p["corr"] == "table" and p["table"]["meta"].get("nonlinear") == "1":
                psic = psic + uc
            lap += -0.125 * np.sum(a * a, axis=(-1, -2)) / psic**7
            psi = psi + uc
    a2 = np.sum(ab * ab, axis=(-1, -2))
    ham = -8.0 * lap / psi**5 - a2 / psi**12
    return psi, ab / psi[:, None, None]**2, ham


def savefig(fig, name):
    os.makedirs(FIGS, exist_ok=True)
    path = os.path.join(FIGS, name)
    fig.savefig(path + ".png", dpi=200)
    fig.savefig(path + ".pdf")
    return path + ".png"
