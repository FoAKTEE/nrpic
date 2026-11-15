"""Shared paths, model constants and readers of the threshold_scan package.

Units G = c = 1, ADM mass M = 1. Every number used as an input comes from a file of this
repository or of a registered run (named where it is read).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))

from nrpic import io as nio  # noqa: E402

SCRATCH = "/data/haiyangw/nrpic/scratch/C-sidm"
IC_RUN = "C-20261115-165832-fccee3a"          # make_ic.py, N = 10^5, seed 1
IC_DIR = os.path.join(SCRATCH, IC_RUN)
KNUDSEN_JSON = os.path.join(WT, "tracks", "C-sidm", "equilibria", "results", "knudsen.json")

# mesh of the runs (inputs/*.athinput): root [-512, 512]^3 M with 64^3 cells, 16^3
# MeshBlocks, one refined region of level 6 inside |x|_inf < 7.9 M; the octree makes the
# level-6 leaves cover |x|_inf < 8 M and level 5 cover |x|_inf < 16 M
X_MIN = -512.0
DX_ROOT = 16.0
LEVEL_EDGES = ((8.0, 6), (16.0, 5), (32.0, 4), (64.0, 3), (128.0, 2), (256.0, 1), (512.0, 0))
CFL = 0.25

MODELS = {
    "cc1": dict(tag="king_y0p33403", label="CC1, threshold y0 = 0.334032"),
    "cc2": dict(tag="king_y0p31400", label="CC2, stable side y0 = 0.314"),
}
KN_LIST = (None, 10.0, 1.0)          # None: collisionless control (operator absent)


def stem(tag, N=100000, seed=1):
    return f"{tag}_stratified_N{N}_s{seed}"


def load_model(tag, ic_dir=IC_DIR):
    """Particles, table and model summary of one model of the IC run."""
    s = stem(tag)
    meta = json.load(open(os.path.join(ic_dir, s + ".json")))
    x, u, m, sp = nio.read_nrp(os.path.join(ic_dir, s + ".nrp"))
    r_tab, u_tab, a_tab, _ = nio.read_tab(os.path.join(ic_dir, s + ".tab"))
    return dict(meta=meta, x=x, u=u, m=m, r_tab=r_tab, psi_tab=1.0 + u_tab, alpha_tab=a_tab,
                nrp=os.path.join(ic_dir, s + ".nrp"), tab=os.path.join(ic_dir, s + ".tab"))


def psi_alpha(model, r):
    """Conformal factor and static lapse of the equilibrium at isotropic radius r (table,
    Schwarzschild continuation beyond its last row)."""
    r = np.asarray(r, dtype=float)
    M = model["meta"]["M_ADM"]
    rt = model["r_tab"]
    psi = np.interp(r, rt, model["psi_tab"])
    alp = np.interp(r, rt, model["alpha_tab"])
    out = r > rt[-1]
    if np.any(out):
        h = M / (2.0 * r[out])
        psi[out] = 1.0 + h
        alp[out] = (1.0 - h) / (1.0 + h)
    return psi, alp


def kn_constant(meta):
    """K = 1/(rho0_c H_c): sigma~ = K/Kn with Kn = lambda_c/H_c (lead's definition,
    stage/G0/REPORT.md section 2); rho0 = n_c (rest-mass density of the static observer),
    H_c = (v1^2/(4 pi rho0_c))^(1/2), v1^2 = (p + 2 p_T)/(3 rho0)."""
    rho0 = meta["n_c"]
    v1sq = (meta["p_c"] + 2.0 * meta["pT_c"]) / (3.0 * rho0)
    H = np.sqrt(v1sq / (4.0 * np.pi * rho0))
    return 1.0 / (rho0 * H), H, np.sqrt(v1sq)


def sigma_of(meta, kn):
    return 0.0 if kn is None else kn_constant(meta)[0] / kn


def leaf_dx(x):
    """Cell size of the leaf MeshBlock that holds each position (static mesh above)."""
    a = np.max(np.abs(x), axis=1)
    dx = np.full(len(a), np.nan)
    for edge, lev in reversed(LEVEL_EDGES):
        dx[a < edge] = DX_ROOT / 2 ** lev
    return dx


def run_name(model_key, kn):
    return f"{model_key}_kn{'inf' if kn is None else f'{kn:g}'}"


# ------------------------------------------------------------------ AthenaK outputs

def read_hst(path):
    """A text history with a header line `# [1]=name [2]=name ...`; returns dict of
    arrays, keeping the last record of each cycle/time (restarts repeat records)."""
    names, rows = None, []
    with open(path) as fp:
        for line in fp:
            if line.startswith("#"):
                if "[1]=" in line:
                    toks = line[1:].split()
                    names = [t.split("=", 1)[1] for t in toks if "=" in t]
                continue
            if line.strip():
                rows.append([float(v) for v in line.split()])
    a = np.array(rows)
    if names is None:
        names = [f"c{i + 1}" for i in range(a.shape[1])]
    n = min(len(names), a.shape[1])
    return {names[i]: a[:, i] for i in range(n)}


def read_snapshot(path):
    with open(path, "rb") as f:
        if f.read(8) != b"NRPSNAP1":
            raise ValueError(path)
        t = np.frombuffer(f.read(8), "<f8")[0]
        n = int(np.frombuffer(f.read(8), "<i8")[0])
        cyc = int(np.frombuffer(f.read(8), "<i8")[0])
        rec = np.frombuffer(f.read(56 * n), "<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), "<i4")
        spc = np.frombuffer(f.read(4 * n), "<i4")
        tau = np.frombuffer(f.read(8 * n), "<f8")
    return dict(time=float(t), cycle=cyc, x=rec[:, 0:3], u=rec[:, 3:6], m=rec[:, 6], tag=tag,
                species=spc, tau=tau)


def read_traj(path_traj, path_met):
    """Records of .traj.bin (8 doubles) and .trajmet.bin (17 doubles), grouped by time."""
    tr = np.fromfile(path_traj, "<f8").reshape(-1, 8)
    mt = np.fromfile(path_met, "<f8").reshape(-1, 17)
    n = min(len(tr), len(mt))
    tr, mt = tr[:n], mt[:n]
    times = np.unique(tr[:, 0])
    out = []
    for t in times:
        k = tr[:, 0] == t
        out.append(dict(time=float(t), tag=tr[k, 1].astype(np.int64), x=tr[k, 2:5], u=tr[k, 5:8],
                        alpha=mt[k, 2], beta=mt[k, 3:6], g=mt[k, 6:12], tau=mt[k, 12]))
    return out


def killing_energy(rec):
    """-u_t = alpha W - beta^i u_i per unit rest mass, from a trajmet record; W with the
    inverse of gamma_ij (xx, xy, xz, yy, yz, zz)."""
    g = rec["g"]
    gxx, gxy, gxz, gyy, gyz, gzz = (g[:, i] for i in range(6))
    det = gxx * (gyy * gzz - gyz * gyz) - gxy * (gxy * gzz - gyz * gxz) + gxz * (gxy * gyz - gyy * gxz)
    ixx = (gyy * gzz - gyz * gyz) / det
    ixy = (gxz * gyz - gxy * gzz) / det
    ixz = (gxy * gyz - gxz * gyy) / det
    iyy = (gxx * gzz - gxz * gxz) / det
    iyz = (gxy * gxz - gxx * gyz) / det
    izz = (gxx * gyy - gxy * gxy) / det
    ux, uy, uz = rec["u"][:, 0], rec["u"][:, 1], rec["u"][:, 2]
    usq = (ixx * ux * ux + iyy * uy * uy + izz * uz * uz
           + 2.0 * (ixy * ux * uy + ixz * ux * uz + iyz * uy * uz))
    W = np.sqrt(1.0 + usq)
    bu = np.sum(rec["beta"] * rec["u"], axis=1)
    return rec["alpha"] * W - bu, W
