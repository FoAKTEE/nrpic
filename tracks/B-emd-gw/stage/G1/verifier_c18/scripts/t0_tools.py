"""T0: tests of vlib on analytic fields and on pairs of dumps (predictions: JOURNAL entry 1)."""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", "/data/haiyangw/nrpic/scratch/B-emd-gw/tmp/t0")
os.makedirs(OUT, exist_ok=True)
SC = "/data/haiyangw/nrpic/scratch/B-emd-gw"
res = {}


def synth(n, L, fields):
    dx = L / n
    x = (np.arange(n) + 0.5) * dx
    Z, Y, X = np.meshgrid(x, x, x, indexing="ij")
    d = {"n": (n, n, n), "L": np.array([L, L, L]), "xmin": np.zeros(3), "dx": dx, "time": 0.0,
         "vsize": 8, "chi": np.ones((n, n, n))}
    return d, X, Y, Z


def put(d, gt):
    nm = {(0, 0): "xx", (0, 1): "xy", (0, 2): "xz", (1, 1): "yy", (1, 2): "yz", (2, 2): "zz"}
    for (a, b), s in nm.items():
        d["g" + s] = gt[a, b]
        d["A" + s] = np.zeros_like(gt[a, b])


# T0b: mode extraction and TT projection on an analytic field
n, L = 32, 4.0
k = 2 * np.pi / L
d, X, Y, Z = synth(n, L, None)
_, ep, ex = vlib.BASIS["K1"]
A, B = 3.0e-6, -1.7e-6
ph = k * (X + Y)
h = A * ep[:, :, None, None, None] * np.cos(ph) + B * ex[:, :, None, None, None] * np.sin(ph)
# a pure gradient (non-TT) part: d_i xi_j + d_j xi_i - (2/3) delta div xi, xi = 1e-5 (sin ky, sin kz, cos 2kx)
xi = np.array([np.sin(k * Y), np.sin(k * Z), np.cos(2 * k * X)]) * 1e-5
dxi = np.zeros((3, 3, n, n, n))   # dxi[j, i] = d_i xi_j
dxi[0, 1] = 1e-5 * k * np.cos(k * Y)
dxi[1, 2] = 1e-5 * k * np.cos(k * Z)
dxi[2, 0] = -1e-5 * 2 * k * np.sin(2 * k * X)
hL = vlib.traceless(dxi + np.swapaxes(dxi, 0, 1))
put(d, np.eye(3)[:, :, None, None, None] + h + hL)
r = vlib.measure(d, energies=False)
g = vlib.Grid(d)
Th = g.tt(g.fft_t(vlib.traceless(h + hL)))
amp_fft = g.amp_from_fft(Th, (1, 1, 0))
pp = vlib.pol({"K1": amp_fft, "K2": g.amp_from_fft(Th, (1, -1, 0))})
res["T0b"] = {"plus_direct": r["K1_plus"], "cross_direct": r["K1_cross"],
              "plus_fft_TT": [pp["K1"][0].real, pp["K1"][0].imag], "cross_fft_TT": [pp["K1"][1].real, pp["K1"][1].imag],
              "rel_err_plus": abs(r["K1_plus"][0] / A - 1), "rel_err_cross": abs(-r["K1_cross"][1] / B - 1),
              "rms_TT_over_exact": r["rms_TT"] / np.sqrt(np.mean((h ** 2).sum(axis=(0, 1)))),
              "TT_of_gradient_rel": float(np.abs(g.tt(g.fft_t(hL))).max() / np.abs(g.fft_t(hL)).max())}

# T0c: junk solution, closed form against DOP853
tau = np.linspace(0, 21.7, 2000)
gc, go = vlib.g_closed(tau), vlib.g_ode(tau)
res["T0c"] = {"max_abs_diff": float(np.abs(gc - go).max()), "g_at_tau": {f"{t:g}": float(vlib.g_closed(t)) for t in (1, 5, 10, 21.66)}}
env = np.abs(gc - 1.0)
res["T0c"]["envelope_x_a_late"] = [float(env[(tau > t0) & (tau < t0 + 2)].max() * vlib.a_of_tau(t0 + 1)) for t0 in (5, 10, 15)]

# T0d: exact pure-gauge metric; slopes of TT h and TT h - G in the gauge amplitude
def gauge_metric(e, with_tt):
    d, X, Y, Z = synth(32, L, None)
    xi = e * np.array([np.sin(k * Y) + 0.3 * np.cos(k * Z), np.sin(k * Z + 0.4), 0.5 * np.cos(k * X) + 0.2 * np.sin(k * Y)])
    D = np.zeros((3, 3, 32, 32, 32))  # D[a, b] = d_b xi_a
    D[0, 1] = e * k * np.cos(k * Y); D[0, 2] = -e * 0.3 * k * np.sin(k * Z)
    D[1, 2] = e * k * np.cos(k * Z + 0.4)
    D[2, 0] = -e * 0.5 * k * np.sin(k * X); D[2, 1] = e * 0.2 * k * np.cos(k * Y)
    J = np.eye(3)[:, :, None, None, None] + D
    # TT wave in transverse coordinates, evaluated at x_T = x + xi
    At = e if with_tt else 0.0
    xT = [X + xi[0], Y + xi[1], Z + xi[2]]
    hT = At * ep[:, :, None, None, None] * np.cos(k * (xT[0] + xT[1]))
    hT_x = At * ep[:, :, None, None, None] * np.cos(k * (X + Y))
    gT = np.eye(3)[:, :, None, None, None] + hT
    gc = np.einsum("aixyz,abxyz,bjxyz->ijxyz", J, gT, J)
    det = np.linalg.det(np.moveaxis(gc, (0, 1), (-2, -1)))
    gc = gc * det[None, None] ** (-1.0 / 3.0)
    put(d, gc)
    g = vlib.Grid(d)
    hh = vlib.traceless(gc - np.eye(3)[:, :, None, None, None])
    Fh = g.fft_t(hh)
    Th = g.tt(Fh)
    Gq, Gt = vlib.gauge_piece(hh, Fh, Th, g)
    ref = g.tt(g.fft_t(hT_x))
    nrm = lambda F: float(np.sqrt(g.power(F).sum()))
    return nrm(Th - ref), nrm(Th - ref - Gq), nrm(Th - ref - Gt)


for with_tt in (False, True):
    es = np.array([1e-3, 2e-3, 4e-3, 8e-3])
    vals = np.array([gauge_metric(e, with_tt) for e in es])
    slopes = [float(np.polyfit(np.log(es), np.log(vals[:, j]), 1)[0]) for j in range(3)]
    res[f"T0d_tt={with_tt}"] = {"eps": es.tolist(), "TT_h": vals[:, 0].tolist(), "TT_h_minus_Gq": vals[:, 1].tolist(),
                                "TT_h_minus_Gtot": vals[:, 2].tolist(), "slopes": slopes}

# T0a: readers on real dumps: double-precision bin vs single bin at the same time; rst vs bin
def times(files):
    out = {}
    for f in files:
        with open(f, "rb") as fh:
            head = fh.read(200).decode(errors="ignore")
        out[f] = float(head.split("time=")[1].split()[0])
    return out


run = f"{SC}/B-20261119-142833-19edd82/jit0p3/bin"
td = times(sorted(glob.glob(f"{run}/cw.z4cd.*.bin"))[:4])
ts = times(sorted(glob.glob(f"{run}/cw.z4c.*.bin"))[:45])
pairs = []
for fd, t in td.items():
    best = min(ts, key=lambda f: abs(ts[f] - t))
    if abs(ts[best] - t) < 1e-9:
        pairs.append((fd, best))
pa = []
for fd, fs in pairs:
    D8, D4 = vlib.read_bin(fd), vlib.read_bin(fs)
    pa.append({"double": os.path.basename(fd), "single": os.path.basename(fs), "time": D8["time"],
               "chi_rel": float(np.abs(D4["chi"] / D8["chi"] - 1).max()),
               "gxy_abs": float(np.abs(D4["gxy"] - D8["gxy"]).max()),
               "gxx_abs": float(np.abs(D4["gxx"] - D8["gxx"]).max()),
               "a_chi": float(np.mean(D8["chi"]) ** -0.5), "a_tau": float(vlib.a_of_tau(D8["time"]))})
res["T0a_bin_pairs"] = pa
rdir = f"{SC}/B-20261115-165353-b592d43/cw_eps1"
rst = sorted(glob.glob(f"{rdir}/rst/cw.*.rst"))
bins = times(sorted(glob.glob(f"{rdir}/bin/cw.z4c.*.bin")))
rp = []
for f in rst[1:4]:
    R = vlib.read_rst(f)
    best = min(bins, key=lambda b: abs(bins[b] - R["time"]))
    S = vlib.read_bin(best)
    rr = {"rst": os.path.basename(f), "bin": os.path.basename(best), "t_rst": R["time"], "t_bin": S["time"]}
    if abs(S["time"] - R["time"]) < 1e-9:
        rr.update({"chi_rel": float(np.abs(S["chi"] / R["chi"] - 1).max()),
                   "gxy_abs": float(np.abs(S["gxy"] - R["gxy"]).max()),
                   "alpha_rel": float(np.abs(S["alpha"] / R["alpha"] - 1).max())})
    rp.append(rr)
res["T0a_rst_pairs"] = rp

with open(os.path.join(OUT, "t0_tools.json"), "w") as f:
    json.dump(res, f, indent=1, default=float)
print(json.dumps(res, indent=1, default=float))
