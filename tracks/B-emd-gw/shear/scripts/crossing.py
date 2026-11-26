"""Stream-crossing check of shear runs from the particle snapshots (decision 0046 item 2a).

The dust lattice of make_shear_ic.py is written in the order (ix, iy, iz), iz fastest,
after the tracers and rays, and the code tags particles in file order. Along each column
(ix, iz) the particles start in increasing y (spacing L/npy). A stream has crossed when,
in some column, two neighbours in iy have exchanged their order: with the displacement
along y taken as the periodic offset from the lattice point (|offset| < L/2), the
unwrapped positions must stay strictly increasing, including the periodic pair
(last, first + L). The script reports per snapshot the smallest neighbour spacing over
all columns in units of the lattice spacing (s_min; crossing when s_min <= 0) and the
first snapshot time with a crossing.

    python3 crossing.py --run RUNDIR --cases NAME[,NAME...] [--out DIR]
Reads RUNDIR/<case>/ic/meta.json and RUNDIR/<case>/*.part.*.bin; writes crossing.json and
crossing.png into DIR ($NRPIC_RUN_DIR by default).
"""
import argparse
import glob
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def read_snapshot(path):
    """Format of cosmo/ic/nrp_io.py read_snapshot: time, records (N, 7), tags."""
    with open(path, "rb") as f:
        f.read(8)
        t, = struct.unpack("d", f.read(8))
        n, = struct.unpack("q", f.read(8))
        f.read(8)
        d = np.fromfile(f, dtype=np.float64, count=7*n).reshape(n, 7)
        tag = np.fromfile(f, dtype=np.int32, count=n)
    return t, d, tag


def spacing(meta, d, tag):
    L = meta["L"]
    nxz, ppc_xz = meta["nxz"], meta.get("ppc_xz", 1)
    npx = nxz*ppc_xz
    npy = meta["ny"]*meta["ppc_y"]
    off = meta["n_tracers"] + len(meta["rays_A_tags"]) + len(meta["rays_B_tags"])
    sel = tag >= off
    idx = tag[sel] - off
    y = d[sel, 1]
    ix = idx // (npy*npx)
    iy = (idx // npx) % npy
    iz = idx % npx
    qy = -0.5*L + (iy + 0.5)*(L/npy)
    dy = y - qy
    dy -= L*np.round(dy/L)
    yu = qy + dy
    col = ix*npx + iz
    grid = np.full((npx*npx, npy), np.nan)
    grid[col, iy] = yu
    if np.isnan(grid).any():
        raise RuntimeError("missing dust particles in the snapshot")
    gaps = np.diff(np.concatenate([grid, grid[:, :1] + L], axis=1), axis=1)
    return float(gaps.min()/(L/npy)), float(np.abs(dy).max()/(L/npy))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    res = {}
    for case in a.cases.split(","):
        cdir = os.path.join(a.run, case)
        with open(os.path.join(cdir, "ic", "meta.json")) as f:
            meta = json.load(f)
        files = sorted(glob.glob(os.path.join(cdir, "*.part.*.bin")))
        ts, smin, dmax = [], [], []
        for p in files:
            t, d, tag = read_snapshot(p)
            s, dm = spacing(meta, d, tag)
            ts.append(t)
            smin.append(s)
            dmax.append(dm)
        first = next((t for t, s in zip(ts, smin) if s <= 0.0), None)
        res[case] = {"t": ts, "s_min": smin, "max_disp_over_dq": dmax,
                     "n_snapshots": len(files), "t_first_crossing": first,
                     "s_min_overall": (min(smin) if smin else None)}
        print("%s: %d snapshots, s_min overall %s, first crossing at t = %s"
              % (case, len(files), res[case]["s_min_overall"], first))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "crossing.json"), "w") as f:
        json.dump(res, f, indent=1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    try:
        import figstyle
        figstyle.use_style()
    except Exception:
        pass
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    for case, r in res.items():
        ax.plot(r["t"], r["s_min"], marker="o", ms=2, label=case)
    ax.axhline(0.0, color="k", lw=0.8)
    ax.set_xlabel("code time t")
    ax.set_ylabel(r"smallest neighbour spacing / $\Delta q_y$")
    ax.set_title("stream crossing when the curve reaches 0", fontsize=8)
    ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "crossing.png"), dpi=200)


if __name__ == "__main__":
    main()
