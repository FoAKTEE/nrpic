#!/usr/bin/env python3
"""Semi-axes, collapse times and hoop proxy from AthenaK particle snapshots, against the
homogeneous-ellipsoid reference (analysis of AthenaK output; decision 0010 allows it
outside athenak/src).

    python3 compare_snapshots.py --snaps '<run>/<base>.part.*.bin' --abg A B G \
        [--a0 A0] [--model isolated|embedded|added] [--time-offset T] \
        [--length-unit L] [--species S] --out <dir>
    python3 compare_snapshots.py --selftest --out <dir>

Snapshot layout (athenak/src/particles/nrpic_io.cpp, NrpicWriteSnapshot; docs/FORMATS.md
line 44): 8 bytes NRPSNAP1, float64 time, int64 N, int64 cycle, N x 7 float64 (x^i, u_i,
m), N int32 tags, N int32 species, and (current source) N float64 proper times.

Units: the reference uses those of arXiv:2605.04487 (r_g = 1, t_k = 2/3). A run in other
units is mapped with --length-unit (code length per reference length; 2 for the NRPIC001
convention M = 1) and --time-offset (reference time at code time 0; default t_0 of the
reference, i.e. a run that starts its clock at 0).

Semi-axes: A_i = sqrt(5 c_i), c_i the eigenvalues of the mass-weighted second-moment
tensor about the centre of mass, assigned to the coordinate axis their eigenvector is
closest to. Collapse time: vertex of a parabola fitted to c_i(t) over the five snapshots
around its minimum (c_i is smooth through a crossing, A_i^2 ~ (t - t_1)^2 + const).
"""
import argparse
import glob
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import ellipsoid as el  # noqa: E402
import tophat as th  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def read_snapshot(path):
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:8] != b"NRPSNAP1":
        raise ValueError(f"{path}: bad magic")
    t = np.frombuffer(raw, "<f8", 1, 8)[0]
    n = int(np.frombuffer(raw, "<i8", 1, 16)[0])
    cyc = int(np.frombuffer(raw, "<i8", 1, 24)[0])
    off = 32
    rec = np.frombuffer(raw, "<f8", 7 * n, off).reshape(n, 7)
    off += 56 * n
    tag = np.frombuffer(raw, "<i4", n, off)
    off += 4 * n
    sp = np.frombuffer(raw, "<i4", n, off)
    return dict(t=float(t), cycle=cyc, x=rec[:, :3], u=rec[:, 3:6], m=rec[:, 6], tag=tag,
                species=sp)


def write_snapshot(path, t, x, u, m, cycle=0, species=None):
    """Writer of the same layout, for the self-test only."""
    n = len(m)
    sp = np.zeros(n, "<i4") if species is None else np.asarray(species, "<i4")
    with open(path, "wb") as f:
        f.write(b"NRPSNAP1")
        f.write(np.array([t], "<f8").tobytes())
        f.write(np.array([n, cycle], "<i8").tobytes())
        f.write(np.hstack([x, u, m[:, None]]).astype("<f8").tobytes())
        f.write(np.arange(n, dtype="<i4").tobytes())
        f.write(sp.tobytes())
        f.write(np.zeros(n, "<f8").tobytes())


def moments(x, m):
    xc = (m[:, None] * x).sum(0) / m.sum()
    d = x - xc
    C = (m[:, None, None] * d[:, :, None] * d[:, None, :]).sum(0) / m.sum()
    w, V = np.linalg.eigh(C)
    c = np.empty(3)
    for k in range(3):                       # eigenvector k -> nearest coordinate axis
        c[np.argmax(np.abs(V[:, k]))] = w[k]
    return xc, c


def collapse_times(t, c, nfit=5):
    """Vertex of a parabola through the nfit snapshots around each local minimum."""
    out = []
    for i in range(3):
        y = c[:, i]
        mins = [k for k in range(1, len(y) - 1) if y[k] < y[k - 1] and y[k] <= y[k + 1]]
        res = []
        for k in mins:
            lo, hi = max(0, k - nfit // 2), min(len(y), k + nfit // 2 + 1)
            a, b, _ = np.polyfit(t[lo:hi], y[lo:hi], 2)
            res.append(float(-b / (2 * a)) if a > 0 else float(t[k]))
        out.append(res)
    return out


def analyse(paths, abg, a0=None, model="isolated", time_offset=None, length_unit=1.0,
            species=None, out=None, label="run"):
    lams = np.asarray(abg, dtype=float)
    ref = el.evolve(lams, a0=a0, model=model, n_collapse=2)
    if time_offset is None:
        time_offset = ref["t0"]
    rows = []
    for p in sorted(paths):
        s = read_snapshot(p)
        sel = np.ones(len(s["m"]), bool) if species is None else s["species"] == species
        _, c = moments(s["x"][sel] / length_unit, s["m"][sel])
        rows.append((s["t"] / length_unit + time_offset, c))
    t = np.array([r[0] for r in rows])
    c = np.array([r[1] for r in rows])
    A = np.sqrt(5.0 * c)
    tc = collapse_times(t, c)
    firsts = sorted((v[0], i) for i, v in enumerate(tc) if v)
    res = dict(label=label, model=model, abg=lams.tolist(), t0=ref["t0"],
               time_offset=time_offset, length_unit=length_unit, n_snap=len(t),
               ref_collapses=[dict(t=cc["t"], t_over_tk=cc["t_over_tk"], axis=cc["axis"],
                                   h=cc["h"]) for cc in ref["collapses"]],
               run_collapses=[dict(t=v, t_over_tk=v / th.T_K, axis=i) for v, i in firsts],
               h_run=[float(el.hoop_h(a)) for a in A])
    if firsts and ref["collapses"]:
        res["t1_rel"] = firsts[0][0] / ref["collapses"][0]["t"] - 1
        res["axis1_match"] = firsts[0][1] == ref["collapses"][0]["axis"]
    if out:
        os.makedirs(out, exist_ok=True)
        fs.use_style()
        fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.2))
        ax = fs.inch_axes(fig, 0.7, 0.55, 3.1, 2.5)
        for i, ls in enumerate(("-", "--", ":")):
            ax.plot(ref["t"] / th.T_K, np.abs(ref["A"][:, i]), color=fs.PAL["blue"], ls=ls,
                    label=f"reference ({model})" if i == 0 else None)
            ax.plot(t / th.T_K, A[:, i], "o", color=fs.PAL["red"], ms=2.5,
                    label=label if i == 0 else None)
        ax.set_xlabel(r"$t/t_k$")
        ax.set_ylabel(r"$A_i/r_g$")
        ax.set_xlim(t.min() / th.T_K, t.max() / th.T_K)
        ax.legend(loc="upper right")
        fs.save(fig, os.path.join(out, f"fig_axes_{label}"))
        plt.close(fig)
        with open(os.path.join(out, f"compare_{label}.json"), "w") as f:
            json.dump(res, f, indent=1)
    return res


def selftest(out):
    """Synthetic snapshots of the exact homogeneous ellipsoid in NRPIC001 units (lengths
    and times x 2, clock starting at 0), sampled with N = 20000 random particles."""
    lams = (0.1114, 0.0667, 0.0219)
    ref = el.evolve(lams, model="added", n_collapse=2)
    rng = np.random.default_rng(3)
    N = 20000
    xi = rng.normal(size=(N, 3))
    xi *= (rng.random(N) ** (1 / 3) / np.linalg.norm(xi, axis=1))[:, None]
    m = np.full(N, 1.0 / N)
    t1 = ref["collapses"][0]["t"]
    tgrid = np.unique(np.concatenate([np.linspace(ref["t0"], 1.25 * t1, 41),
                                      np.linspace(0.97 * t1, 1.03 * t1, 13)]))
    # reference axes at the snapshot times (signed through the pass-through)
    sd = os.path.join(out, "selftest_snaps")
    os.makedirs(sd, exist_ok=True)
    ts, As = ref["t"], ref["A"]
    sign = np.ones_like(As)
    for c in ref["collapses"]:
        sign[ts > c["t"], c["axis"]] *= -1
    Ai = np.array([np.interp(tgrid, ts, sign[:, i] * np.abs(As[:, i])) for i in range(3)]).T
    for k, (tt, a) in enumerate(zip(tgrid, Ai)):
        x = 2.0 * xi * a
        write_snapshot(os.path.join(sd, f"self.part.{k:05d}.bin"), 2.0 * (tt - ref["t0"]),
                       x, np.zeros_like(x), m, cycle=k)
    res = analyse(glob.glob(os.path.join(sd, "self.part.*.bin")), lams, model="added",
                  length_unit=2.0, out=out, label="selftest")
    # sampled ball: second moment of a unit ball is 1/5 up to sampling noise
    _, c0 = moments(xi, m)
    res["sampling_rel_err_axes"] = (np.sqrt(5 * c0) - 1).tolist()
    res["snapshot_spacing_near_t1"] = float(tgrid[1:][tgrid[1:] > 0.97 * t1][0]
                                            - tgrid[tgrid > 0.97 * t1][0])
    print(json.dumps({k: v for k, v in res.items() if k != "h_run"}, indent=1))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snaps")
    ap.add_argument("--abg", nargs=3, type=float)
    ap.add_argument("--a0", type=float, default=None)
    ap.add_argument("--model", default="isolated", choices=el.MODELS)
    ap.add_argument("--time-offset", type=float, default=None)
    ap.add_argument("--length-unit", type=float, default=1.0)
    ap.add_argument("--species", type=int, default=None)
    ap.add_argument("--label", default="run")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.selftest:
        selftest(a.out)
        return
    res = analyse(glob.glob(a.snaps), a.abg, a.a0, a.model, a.time_offset, a.length_unit,
                  a.species, a.out, a.label)
    print(json.dumps({k: v for k, v in res.items() if k != "h_run"}, indent=1))


if __name__ == "__main__":
    main()
