"""Reduce the test-particle cluster runs to the arrays of fig_tp_cluster.py.

This is the only script of the cluster figure that reads the simulation outputs and the
analysis modules of the repository; the figure script reads paper/data/tp_cluster.npz
alone. Everything is for black hole spin a = 0.9 M and clusters of 10^4 particles:

- bound cluster on the mesh metric, implicit midpoint pusher: positions in the orbital
  plane at the snapshot times SNAP_T;
- bound cluster, five runs (analytic or mesh metric; implicit midpoint, spacetime Boris
  in the symmetric gauge, spacetime Boris in the Cholesky gauge on the analytic metric):
  median and 99th percentile over the particles of |E(t)/E(0) - 1| and
  |L_z(t)/L_z(0) - 1| with the exact Kerr invariants, at every snapshot (5 M);
- plunging cluster on the mesh metric, implicit midpoint pusher: every cycle, the
  relative difference of the proper-volume integral of the deposited energy density
  before the filter and the particle sum of m W; the number of refinement-level changes
  between snapshots (1 M); the cumulative number of particles removed by lapse excision;
  and the removal times that exact geodesics predict for the particles that the exact
  invariants of the initial data classify as plunging.

    python3 paper/scripts/make_data_tp_cluster.py
"""
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(REPO / "analysis" / "cluster_test"))
import ct_common as C  # noqa: E402

OUT = HERE.parent / "data" / "tp_cluster.npz"
A = 0.9
SNAP_T = (0.0, 100.0, 200.0, 1000.0)
SPECIES_1E4 = 2       # the N = 10^4 cluster inside the combined analytic runs
INV_RUNS = {          # key: (run, species or None)
    "ana_mid": ("ana_a0.9_mid", SPECIES_1E4),
    "ana_boris": ("ana_a0.9_boris", SPECIES_1E4),
    "ana_chol": ("ana_a0.9_bchol", SPECIES_1E4),
    "mesh_mid": ("mesh_a0.9_n10000_mid", None),
    "mesh_boris": ("mesh_a0.9_n10000_boris", None),
}
BOUND = "mesh_a0.9_n10000_mid"
PLUNGE = "plunge_a0.9_mid"
H = C.dc.H


def invariant_history(name):
    """Per-particle exact invariants on every snapshot: the analysis cache when it is
    newer than the snapshots, otherwise computed here (and not written anywhere)."""
    files = C.snapshots(name)
    cpath = os.path.join(C.CACHE, f"{name}_inv.npz")
    if (os.path.exists(cpath)
            and os.path.getmtime(cpath) > max(os.path.getmtime(f) for f in files)):
        z = np.load(cpath)
        return {k: z[k] for k in ("t", "species", "E", "L", "x")}
    t0, x0, u0, m0, tag0, sp0 = C.read_snap(files[0])
    N = len(tag0)
    idx = np.full(tag0.max() + 1, -1)
    idx[tag0] = np.arange(N)
    out = dict(t=np.zeros(len(files)), species=sp0,
               E=np.full((len(files), N), np.nan), L=np.full((len(files), N), np.nan),
               x=np.full((len(files), N, 3), np.nan))
    for k, f in enumerate(files):
        t, x, u, m, tag, sp = C.read_snap(f)
        j = idx[tag]
        E, L, _ = C.invariants(x, u, A)
        out["t"][k] = t
        out["E"][k, j], out["L"][k, j], out["x"][k, j] = E, L, x
    return out


def invariant_stats(name, species):
    h = invariant_history(name)
    sel = slice(None) if species is None else (h["species"] == species)
    res = {}
    for q in ("E", "L"):
        v = h[q][:, sel]
        e = np.abs(v / v[0][None, :] - 1.0)
        with np.errstate(all="ignore"):
            res[q + "_med"] = np.nanmedian(e, axis=1)
            res[q + "_p99"] = np.nanpercentile(e, 99, axis=1)
    return h["t"], res


def level_changes(name):
    """Particles whose refinement level changed between consecutive snapshots, per M,
    at the snapshot mid-times, and the total."""
    h = invariant_history(name)
    x = h["x"].astype(float)
    lev = np.where(np.isfinite(x[..., 0]), C.level_of(np.nan_to_num(x)), -1)
    both = (lev[1:] >= 0) & (lev[:-1] >= 0)
    n = np.sum(both & (lev[1:] != lev[:-1]), axis=1)
    return 0.5 * (h["t"][1:] + h["t"][:-1]), n / np.diff(h["t"]), int(n.sum())


def main():
    data = dict(a=A, snap_t=np.array(SNAP_T))

    # (i) positions in the orbital plane
    files = C.snapshots(BOUND)
    tsnap = np.array([C.read_snap(f)[0] for f in files[:2]])
    dt_snap = tsnap[1] - tsnap[0]
    xs = []
    for t in SNAP_T:
        ts, x, u, m, tag, sp = C.read_snap(files[int(round(t / dt_snap))])
        assert abs(ts - t) < 1e-6, (ts, t)
        xs.append(x[:, :2].astype(np.float32))
    n = max(len(x) for x in xs)
    xy = np.full((len(SNAP_T), n, 2), np.nan, dtype=np.float32)
    for k, x in enumerate(xs):
        xy[k, :len(x)] = x
    data["snap_xy"] = xy

    # (ii) invariants
    for key, (name, sp) in INV_RUNS.items():
        t, res = invariant_stats(name, sp)
        data["inv_t"] = t
        for q, v in res.items():
            data[f"inv_{key}_{q}"] = v

    # (iii) deposition identity before the filter, every cycle
    for key, name in (("plunge", PLUNGE), ("bound", BOUND)):
        h = C.history(name)
        data[f"dep_{key}_t"] = h[:, H["time"]]
        data[f"dep_{key}_res"] = h[:, H["int_e"]] / h[:, H["sum_mw"]] - 1.0
        tc, rate, ntot = level_changes(name)
        data[f"lev_{key}_t"], data[f"lev_{key}_rate"] = tc, rate
        data[f"lev_{key}_total"] = ntot

    # (iv) removal by lapse excision
    h = C.history(PLUNGE)
    data["exc_t"] = h[:, H["time"]]
    data["exc_n"] = h[:, H["n_excised"]].astype(np.int32)
    data["exc_escaped"] = h[:, H["n_escaped"]].astype(np.int32)
    cls = np.load(os.path.join(C.RUNS, "ic", "plunge_a0.9_n10000.class.npy"))
    pred = np.load(os.path.join(C.RUNS, "ic", "plunge_a0.9_pred_excision.npz"))
    data["n_pred_plunge"] = int((cls == 1).sum())
    data["pred_t"] = np.sort(pred["ncyc"][pred["ncyc"] >= 0] * C.DT)
    data["alpha_exc"] = C.ALPHA_EXC

    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.2f} MB")

    # spot checks against docs/results_cluster_test.md
    j = -1
    for key in INV_RUNS:
        print(f"t = {data['inv_t'][j]:.0f} M  {key:10s}  dE/E med {data[f'inv_{key}_E_med'][j]:.1e}"
              f" p99 {data[f'inv_{key}_E_p99'][j]:.1e}   dLz/Lz med {data[f'inv_{key}_L_med'][j]:.1e}"
              f" p99 {data[f'inv_{key}_L_p99'][j]:.1e}")
    for key in ("bound", "plunge"):
        print(f"deposition {key}: max |int E sqrt(g) dV / sum mW - 1| before filter "
              f"{np.max(np.abs(data[f'dep_{key}_res'])):.1e}; level changes "
              f"{data[f'lev_{key}_total']}")
    nb = lambda s: int(data["exc_n"][np.searchsorted(data["exc_t"], s - 1e-9)])
    print("excised (history) final", data["exc_n"][-1], "predicted plunging", data["n_pred_plunge"],
          "| by 100/200/300 M:", [nb(s) for s in (100, 200, 300)],
          "predicted", [int((data["pred_t"] <= s).sum()) for s in (100, 200, 300)])


if __name__ == "__main__":
    main()
