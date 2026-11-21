"""Gate reviewer's own checks for G1 of A-emd-pbh (GATE_REVIEW.md, section 2).

Recomputes from the raw AthenaK outputs four of the five Table IV rows of note v1 that no
fresh verifier recomputed (OPEN.md item 2), and recounts the Newtonian band of C8 from the
analysis CSV. Own code; imports nothing of the track; only the figure style.

usage: python review_checks.py OUTDIR
"""
import hashlib
import json
import os
import sys

import numpy as np

S = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
WT = "/data/haiyangw/nrpic/wt/A-emd-pbh"
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


def checked(run, rel):
    """Path of a raw file, checked against the run's sha256sums.txt."""
    path = os.path.join(S, run, rel)
    lst = os.path.join(S, run, "sha256sums.txt")
    if not os.path.exists(lst):
        # wave-1 run without its own record: the integrity listing of run
        # A-20261120-222620-0304d9d (g1close), one file <run id>.sha256 per run
        lst = os.path.join(S, "A-20261120-222620-0304d9d", run + ".sha256")
        log(f"note: {run} has no sha256sums.txt; using the listing {lst}")
    want = None
    with open(lst) as f:
        for line in f:
            h, name = line.split(None, 1)
            if name.strip().lstrip("*") == rel:
                want = h
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    ok = (want == h.hexdigest())
    log(f"sha256 {'ok' if ok else 'MISMATCH' if want else 'NOT LISTED'}: {run}/{rel}")
    if not ok:
        raise SystemExit(f"checksum failure: {run}/{rel}")
    return path


def load_hst(path):
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            try:
                rows.append([float(x) for x in line.split()])
            except ValueError:
                rows.append([np.nan] * len(rows[-1]))
    n = min(len(r) for r in rows)
    return np.array([r[:n] for r in rows])


res = {}

# ---------------------------------------------------------------------------------------
# A. geodesic slicing: largest |H| on the mesh at t = 20 (cstat column 9 = H_max)
SR1 = {"M": ("A-emd-pbh-20261115-155056-ec1b816", "sr1_n128"),
       "M/2": ("A-emd-pbh-20261115-153843-7172b66", "sr1"),
       "M/4": ("A-emd-pbh-20261115-164539-0b18e84", "sr1_n256_L32")}
res["A_Hmax_t20_sr1"] = {}
cst_series = {}
for k, (run, sub) in SR1.items():
    c = load_hst(checked(run, f"{sub}/ball.cstat.hst"))
    t, hmax = c[:, 0], c[:, 8]
    j = int(np.argmin(np.abs(t - 20.0)))
    res["A_Hmax_t20_sr1"][k] = dict(t=float(t[j]), H_max=float(hmax[j]))
    cst_series[k] = (t, hmax)
    log(f"A  SR-1 {k}: t = {t[j]:.4f}, H_max = {hmax[j]:.4g}")

# ---------------------------------------------------------------------------------------
# B, C. conformal-time slicing: central lapse against the scale factor of the core.
# Own exact reference: the core of data set 2t is homogeneous (closed dust), with common
# bang time t_i before the initial slice and turnaround tau_ta after it (data-set JSON of
# run A-emd-pbh-20261115-130609-947c898). Cycloid in eta: age = (A/pi)(eta - sin eta),
# A = t_i + tau_ta; a/a_i = (1 - cos eta)/(1 - cos eta_i).
ds = json.load(open(checked("A-emd-pbh-20261115-130609-947c898",
                            "expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75_w0p1875.json")))
t_i = ds["predictions"]["t_i"]
tau_ta = ds["predictions"]["core_tau_ta"]
A = t_i + tau_ta
eta = np.linspace(1e-6, 2 * np.pi - 1e-6, 400001)
age = A / np.pi * (eta - np.sin(eta))
eta_i = np.interp(t_i, age, eta)
a_of_eta = (1 - np.cos(eta)) / (1 - np.cos(eta_i))
sel = eta >= eta_i
tau_grid, a_grid = age[sel] - t_i, a_of_eta[sel]
res["exact_core"] = dict(t_i=t_i, tau_ta=tau_ta, eta_i=float(eta_i),
                         Rmax_over_Ri=float(2 / (1 - np.cos(eta_i))),
                         tau_crunch=float(A * 2 - t_i))
log(f"exact core: eta_i = {eta_i:.6f}, R_max/R_i = {2 / (1 - np.cos(eta_i)):.5f}, "
    f"tau_crunch = {2 * A - t_i:.4f} (data set: {ds['predictions']['core_tau_c']:.4f})")
# conformal-time coordinate time of turnaround: t = (2 A/(pi Rmax/Ri)) (eta - eta_i)
t_ta_conf = 2 * A / (np.pi * 2 / (1 - np.cos(eta_i))) * (np.pi - eta_i)
res["exact_core"]["t_ta_conformal"] = float(t_ta_conf)
log(f"exact core: conformal-time coordinate time of turnaround {t_ta_conf:.4f}")

SR2 = {"M": ("A-emd-pbh-20261115-155056-ec1b816", "sr2_n128"),
       "M/2": ("A-emd-pbh-20261115-153845-7172b66", "sr2"),
       "M/4": ("A-emd-pbh-20261115-164541-0b18e84", "sr2_n256_L32")}
res["B_lapse_sr2"] = {}
lapse_series = {}
for k, (run, sub) in SR2.items():
    h = load_hst(checked(run, f"{sub}/ball.nrpic.hst"))
    t, alpha_c, tau_c = h[:, 0], h[:, 12], h[:, 14]
    a_ex = np.interp(tau_c, tau_grid, a_grid, right=np.nan)
    dev = alpha_c / a_ex - 1.0
    fin = np.isfinite(dev)
    over = np.nonzero(fin & (np.abs(dev) > 0.1))[0]
    t_first = float(t[over[0]]) if len(over) else None
    s15 = fin & (t <= 15.0)
    r = dict(t_first_dev_gt_0p1=t_first, maxdev_t_le_15=float(np.max(np.abs(dev[s15]))),
             alpha_c_at_t_ta=float(np.interp(t_ta_conf, t, alpha_c)),
             a_exact_at_t_ta=float(2 / (1 - np.cos(eta_i))),
             dev_t0=float(dev[0]), t_end=float(t[-1]))
    res["B_lapse_sr2"][k] = r
    lapse_series[k] = (t, dev)
    log(f"B  SR-2 {k}: first t with |alpha_c/a - 1| > 0.1: {t_first}; "
        f"max to t = 15: {r['maxdev_t_le_15']:.4f}; alpha_c at t_ta(conf) "
        f"{r['alpha_c_at_t_ta']:.4f} vs exact {r['a_exact_at_t_ta']:.4f}")

# ---------------------------------------------------------------------------------------
# D. geodesic slicing, dx = M/2: tracked particles stay at their coordinates and their
# proper time equals t. traj.bin: 8 float64 (t, tag, x, y, z, u_x, u_y, u_z);
# trajmet.bin: 17 float64, column 12 (0-based) = proper time (coord/INTERFACES/diagnostics.md 6).
run, sub = SR1["M/2"]
tr = np.fromfile(checked(run, f"{sub}/ball.traj.bin"), dtype="<f8")
tm = np.fromfile(checked(run, f"{sub}/ball.trajmet.bin"), dtype="<f8")
assert tr.size % 8 == 0 and tm.size % 17 == 0
tr = tr.reshape(-1, 8)
tm = tm.reshape(-1, 17)
assert tr.shape[0] == tm.shape[0]
tags = tr[:, 1].astype(np.int64)
ntag = int(tags.max()) + 1
first = {}
r = np.sqrt(tr[:, 2] ** 2 + tr[:, 3] ** 2 + tr[:, 4] ** 2)
t0 = tr[0, 0]
r0 = np.full(ntag, np.nan)
m0 = tr[:, 0] == t0
r0[tags[m0]] = r[m0]
rel = np.abs(r / r0[tags] - 1.0)
dtau = np.abs(tm[:, 12] - tm[:, 0])
fin = np.isfinite(rel) & np.isfinite(dtau)
times = np.unique(tr[:, 0])
per_t_rel = np.array([np.nanmax(np.where(fin[tr[:, 0] == tt], rel[tr[:, 0] == tt], np.nan))
                      if np.any(fin[tr[:, 0] == tt]) else np.nan for tt in times])
per_t_tau = np.array([np.nanmax(np.where(fin[tr[:, 0] == tt], dtau[tr[:, 0] == tt], np.nan))
                      if np.any(fin[tr[:, 0] == tt]) else np.nan for tt in times])
res["D_tracked_sr1_M2"] = dict(n_tracked=int(m0.sum()), n_records=int(tr.shape[0]),
                               t_first=float(times[0]), t_last=float(times[-1]),
                               t_last_finite=float(times[np.isfinite(per_t_rel)][-1]),
                               max_rel_r=float(np.nanmax(per_t_rel)),
                               max_abs_tau_minus_t=float(np.nanmax(per_t_tau)),
                               max_rel_r_t_le_30=float(np.nanmax(per_t_rel[times <= 30])),
                               max_abs_tau_minus_t_t_le_30=float(np.nanmax(per_t_tau[times <= 30])))
log("D  SR-1 M/2 tracked:", json.dumps(res["D_tracked_sr1_M2"]))

# ---------------------------------------------------------------------------------------
# E. Newtonian scan band of C8: t1_vertex_rel in [+2.2e-4, +6.3e-4] (printed precision)
import csv  # noqa: E402
rows = list(csv.DictReader(open(checked("A-emd-pbh-20261115-164420-4528861", "newton_scan.csv"))))
pts = []
for row in rows:
    v = float(row["t1_vertex_rel"])
    pts.append(dict(name=row["name"], nx=int(row["nx"]), n=int(row["n"]), e=float(row["e"]),
                    p=float(row["p"]), t1_rel=v, in_band=bool(2.15e-4 <= v <= 6.35e-4)))
res["E_newton_band"] = dict(n_points=len(pts), n_in_band=sum(p["in_band"] for p in pts), points=pts)
log(f"E  Newtonian band: {res['E_newton_band']['n_in_band']} of {len(pts)} in [2.2e-4, 6.3e-4]")
for p in pts:
    log(f"   {p['name']:14s} nx={p['nx']:4d} n={p['n']:8d} e={p['e']:.3f} p={p['p']:+.2f} "
        f"t1_rel={p['t1_rel']:+.3e} {'in' if p['in_band'] else 'OUT'}")

# ---------------------------------------------------------------------------------------
json.dump(res, open(os.path.join(OUT, "review_checks.json"), "w"), indent=1)

fs.use_style()
fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.96, wspace=0.28, hspace=0.32)
cols = {"M": fs.PAL["yellow"], "M/2": fs.PAL["red"], "M/4": fs.PAL["green"]}
ax = axs[0, 0]
for k, (t, hm) in cst_series.items():
    ax.semilogy(t, hm, color=cols[k], label=f"dx = {k}")
    ax.plot([res["A_Hmax_t20_sr1"][k]["t"]], [res["A_Hmax_t20_sr1"][k]["H_max"]], "o",
            color=cols[k], ms=4)
ax.axvline(20.0, **fs.MASK_LINE)
ax.set_xlabel("t / M_0")
ax.set_ylabel("H_max on the mesh, SR-1")
ax.set_ylim(1e-5, 1e3)
ax.legend(frameon=False)
ax = axs[0, 1]
for k, (t, dev) in lapse_series.items():
    ax.semilogy(t, np.abs(dev), color=cols[k], label=f"dx = {k}")
ax.axhline(0.1, **fs.GUIDE)
ax.axvline(15.0, **fs.MASK_LINE)
ax.set_xlabel("t / M_0")
ax.set_ylabel("|alpha_c / a(tau_c) - 1|, SR-2")
ax.set_ylim(1e-6, 10)
ax.legend(frameon=False)
ax = axs[1, 0]
ax.semilogy(times, per_t_rel, color=fs.PAL["red"], label="max |r/r_0 - 1|")
ax.semilogy(times, per_t_tau, color=fs.PAL["blue"], label="max |tau - t| / M_0")
ax.set_xlabel("t / M_0")
ax.set_ylabel("tracked particles, SR-1, dx = M/2")
ax.legend(frameon=False)
ax = axs[1, 1]
for p in pts:
    c = fs.PAL["red"] if p["in_band"] else fs.PAL["blue"]
    mk = "o" if p["nx"] == 128 else "s"
    ax.plot(p["e"] + (0.004 if p["p"] > 0 else -0.004 if p["p"] < 0 else 0), p["t1_rel"] * 1e4,
            mk, color=c, ms=5)
ax.axhspan(2.2, 6.3, color=fs.PAL["red"], alpha=0.1)
ax.axhline(0, **fs.THIN)
ax.set_xlabel("ellipticity e")
ax.set_ylabel("t_1 / t_1,ref - 1  [1e-4]")
fs.save(fig, os.path.join(OUT, "fig_review_checks"))
open(os.path.join(OUT, "review_checks.log"), "w").write("\n".join(LOG) + "\n")
print("done")
