#!/usr/bin/env python3
"""Lead's independent checks of wave 2 and 2b (F-hills JOURNAL.md, session wave 2b, V8 and V9).

Written by the lead without the helpers' readers (nrread.py, single_analysis.py,
nr_invariants.py): it parses AthenaK's raw files itself.

  review_check.py nr <out> <S-run dir> <P1-smoke run dir>
      V8: S3/S2 logs (stop), horizon summaries (failed searches = NaN rows or rows equal to
      the previous row in columns 3-12, as athenak/src/z4c/fastflow.cpp writes them), first
      good search, window medians, tracker speed ratio, P1 smoke log and card memory.
  review_check.py gr <out> <athinput> [<athinput> ...]
      V9: test-particle invariants of the members' centre of mass in the field of the heavy
      puncture (isotropic Schwarzschild, momenta read as m u), capture and turning point.

Writes <out>/review_<mode>.json and <out>/fig_review_<mode>.{png,pdf}.
"""
import glob
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))

P_OVER_MADM = 0.25 / 1.039063          # single_P025: P = 0.25, M_ADM (2nd-order corr.) = 1.039063 m


# ---------------------------------------------------------------- V8: raw AthenaK files
def read_log(path):
    txt = open(path, errors="replace").read()
    cyc = [(int(c), float(t)) for c, t in
           re.findall(r"cycle=(\d+) time=([0-9.eE+-]+)", txt)]
    fatal = re.findall(r"Number of MeshBlocks in this rank on new tree = (\d+).*?"
                       r"max_nmb_per_rank = (\d+)", txt)
    cur = re.findall(r"Current number of MeshBlocks = (\d+)", txt)
    zc = re.findall(r"zone-cycles/cpu_second = ([0-9.eE+-]+)", txt)
    cpu = re.findall(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
    lev = re.findall(r"Physical level = \d+ \(logical level = \d+\): (\d+) MeshBlocks", txt)
    return dict(cycles=cyc, fatal=[(int(a), int(b)) for a, b in fatal],
                current=[int(c) for c in cur], zone_cycles_per_s=[float(z) for z in zc],
                cpu=[float(c) for c in cpu], start_tree=sum(int(x) for x in lev) if lev else None)


def read_horizon(path):
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        rows.append([float(v) for v in line.split()])
    a = np.array(rows)
    failed = np.zeros(len(a), bool)
    for i in range(len(a)):
        if not np.all(np.isfinite(a[i, 2:12])):
            failed[i] = True
        elif i > 0 and np.all(np.isfinite(a[i - 1, 2:12])) and \
                np.array_equal(a[i, 2:12], a[i - 1, 2:12]):
            failed[i] = True
    return a, failed


def read_tracker(path):
    a = np.loadtxt(path, comments="#")
    # restart segments may repeat times; keep the last row of each time
    _, idx = np.unique(a[::-1, 1], return_index=True)
    return a[::-1][idx]


def horizon_stats(a, failed):
    t, m, hrms = a[:, 1], a[:, 2], a[:, 8]
    good = (~failed) & np.isfinite(hrms) & (hrms < 1e-3)
    first = int(np.argmax(good)) if good.any() else None

    def med(t0, t1):
        s = good & (t >= t0 - 1e-9) & (t <= t1 + 1e-9)
        return float(np.median(m[s])) if s.any() else None
    m46, m1214 = med(4, 6), med(12, 14)
    return dict(n=int(len(a)), failed=int(failed.sum()),
                failed_times=[float(x) for x in t[failed]],
                first_good=None if first is None else dict(t=float(t[first]),
                                                            mass=float(m[first])),
                t0=dict(mass=float(m[0]), hrms=float(hrms[0]), meanradius=float(a[0, 10])),
                median_4_6=m46, median_12_14=m1214,
                drift_4_6_to_12_14=None if (m46 is None or m1214 is None) else m1214 - m46,
                max_spin=float(np.nanmax(np.abs(a[~failed, 6]))))


def check_nr(out, srun, prun):
    res = {"S": {}, "P1smoke": {}}
    for name in ("S3", "S2"):
        d = os.path.join(srun, name)
        logs = sorted(glob.glob(os.path.join(d, "athena.2*.log")))
        lg = read_log(logs[-1])
        a, failed = read_horizon(os.path.join(d, "single.horizon_summary_0.txt"))
        tr = read_tracker(os.path.join(d, "single.co_0.txt"))
        t, x = tr[:, 1], tr[:, 2]
        xi = np.interp([10.0, 14.0], t, x)
        f = (xi[1] - xi[0]) / 4.0 / P_OVER_MADM
        # f(t) from centred differences over 1 m windows, for the figure
        tt = np.arange(1.0, t[-1] - 0.5, 0.25)
        ft = (np.interp(tt + 0.5, t, x) - np.interp(tt - 0.5, t, x)) / P_OVER_MADM
        res["S"][name] = dict(log=os.path.basename(logs[-1]), fatal=lg["fatal"],
                              last_logged_cycle=lg["cycles"][-1] if lg["cycles"] else None,
                              tracker_last=dict(iter=int(tr[-1, 0]), t=float(t[-1]),
                                                x=float(x[-1])),
                              tracker_max_abs_yz=float(np.max(np.abs(tr[:, 3:5]))),
                              f_10_14=float(f), horizon=horizon_stats(a, failed),
                              _series=dict(t=a[:, 1].tolist(), m=a[:, 2].tolist(),
                                           failed=failed.tolist(), ft_t=tt.tolist(),
                                           ft=ft.tolist()))
    d = os.path.join(prun, "P1smoke")
    logs = sorted(glob.glob(os.path.join(d, "athena.2*.log")))
    lg = read_log(logs[-1])
    mem = []
    for line in open(sorted(glob.glob(os.path.join(d, "athena.2*.gpumem.csv")))[-1]):
        if line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        try:
            mem.append(float(parts[1]))
        except (IndexError, ValueError):
            pass
    inp = {}
    for line in open(os.path.join(d, "p1_q4.athinput")):
        line = line.split("#")[0].strip()
        if "=" in line:
            k, v = (s.strip() for s in line.split("=", 1))
            inp[k] = v
    trk, hz = {}, {}
    for c in range(3):
        tr = read_tracker(os.path.join(d, f"hills.co_{c}.txt"))
        x0 = np.array([float(inp[f"comp{c}_x{k}"]) for k in (1, 2, 3)])
        trk[c] = dict(first_row_offset=float(np.max(np.abs(tr[0, 2:5] - x0))),
                      t_last=float(tr[-1, 1]),
                      finite=bool(np.all(np.isfinite(tr))))
        a, failed = read_horizon(os.path.join(d, f"hills.horizon_summary_{c}.txt"))
        hz[c] = dict(n=int(len(a)), failed=int(failed.sum()),
                     mass_t0=None if not np.isfinite(a[0, 2]) else float(a[0, 2]),
                     good_hrms_lt_1e3=int(((~failed) & (a[:, 8] < 1e-3)).sum()),
                     _t=a[:, 1].tolist(), _m=a[:, 2].tolist(), _failed=failed.tolist())
    zc = lg["zone_cycles_per_s"][-1] if lg["zone_cycles_per_s"] else None
    res["P1smoke"] = dict(log=os.path.basename(logs[-1]), start_tree=lg["start_tree"],
                          current=lg["current"], cpu=lg["cpu"],
                          zone_cycles_per_s=zc,
                          meshblock_cycles_per_s=None if zc is None else zc / 16 ** 3,
                          peak_mem_MiB=max(mem) if mem else None,
                          trackers=trk, horizons=hz,
                          cost_card_hours={str(n): 71680 * n / (zc / 16 ** 3) / 3600.0
                                           for n in (1744, 1905, 2080)} if zc else None,
                          _mem=mem)

    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.6))
    col = {"S3": fs.PAL["yellow"], "S2": fs.PAL["red"]}
    for name, r in res["S"].items():
        s = r["_series"]
        ax[0].plot(s["ft_t"], s["ft"], color=col[name], lw=1.0, label=name)
        t, m, fl = (np.array(s[k]) for k in ("t", "m", "failed"))
        ok = ~fl
        ax[1].plot(t[ok], m[ok] - 1.0, "o", ms=2, color=col[name], label=f"{name} found")
        ax[1].plot(t[fl], m[fl] - 1.0, "x", ms=4, color=col[name], label=f"{name} failed")
    ax[0].axhline(0.8, color="k", lw=0.6, ls=":")
    ax[0].set_xlabel(r"$t\,[m]$")
    ax[0].set_ylabel(r"$f$ (1 $m$ centred difference)")
    ax[0].legend(fontsize=6)
    ax[1].set_ylim(-0.02, 0.012)
    ax[1].set_xlabel(r"$t\,[m]$")
    ax[1].set_ylabel(r"$M_{\rm AH}/m - 1$ (raw rows)")
    ax[1].legend(fontsize=5, ncol=2)
    mem = res["P1smoke"]["_mem"]
    ax[2].plot(np.arange(len(mem)) * 0.5, np.array(mem) / 1024.0, color=fs.PAL["blue"], lw=1)
    ax[2].axhline(80.0, color="k", lw=0.6, ls=":")
    ax[2].set_xlabel("wall time of the smoke [s]")
    ax[2].set_ylabel("card memory [GiB]")
    ax[2].set_title("dotted: 80 GiB card", fontsize=7)
    fig.tight_layout()
    paths = fs.save(fig, os.path.join(out, "fig_review_nr"))
    for r in res["S"].values():
        r.pop("_series")
    for h in res["P1smoke"]["horizons"].values():
        for k in ("_t", "_m", "_failed"):
            h.pop(k)
    res["P1smoke"].pop("_mem")
    return res, paths


# ---------------------------------------------------------------- V9: GR invariants
def read_problem(path):
    blk, d = None, {}
    for line in open(path):
        line = line.split("#")[0].strip()
        if not line:
            continue
        m = re.match(r"<(\w+)>", line)
        if m:
            blk = m.group(1)
            continue
        if blk == "problem" and "=" in line:
            k, v = (s.strip() for s in line.split("=", 1))
            d[k] = v
    n = int(d["ncomp"])
    m = np.array([float(d[f"comp{i}_mass"]) for i in range(n)])
    x = np.array([[float(d[f"comp{i}_x{k}"]) for k in (1, 2, 3)] for i in range(n)])
    p = np.array([[float(d[f"comp{i}_p{k}"]) for k in (1, 2, 3)] for i in range(n)])
    return m, x, p


def V2(r, L, Mh):
    return (1.0 - 2.0 * Mh / r) * (1.0 + L * L / (r * r))


def capture_and_turning(E, L, Mh, r_start):
    """Schwarzschild geodesic moving inward from areal r_start: captured if E^2 exceeds the
    barrier top (or no barrier: L^2 < 12 Mh^2); else the turning point (outer root of V2 = E^2
    below r_start), by bisection."""
    if L * L < 12.0 * Mh * Mh:
        return True, None, None
    rb = (L * L - math.sqrt(L ** 4 - 12.0 * L * L * Mh * Mh)) / (2.0 * Mh)   # barrier top
    if E * E >= V2(rb, L, Mh):
        return True, None, rb
    lo, hi = rb, r_start
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if V2(mid, L, Mh) > E * E:
            lo = mid
        else:
            hi = mid
    return False, 0.5 * (lo + hi), rb


def invariants(x, u, Mh):
    r = float(np.linalg.norm(x))
    psi = 1.0 + Mh / (2.0 * r)
    alpha = (1.0 - Mh / (2.0 * r)) / psi
    E = alpha * math.sqrt(1.0 + float(u @ u) / psi ** 4)
    L = float(x[0] * u[1] - x[1] * u[0])
    return E, L, r * psi * psi, r


def check_gr(out, inputs):
    res = {}
    curves = []
    for path in inputs:
        m, x, p = read_problem(path)
        heavy = int(np.argmax(m))
        mem = [i for i in range(len(m)) if i != heavy]
        mb = m[mem].sum()
        xc = (m[mem, None] * x[mem]).sum(0) / mb - x[heavy]
        rows = {}
        for lab, Mh, frame in (("hole_frame_M", m[heavy], True),
                               ("hole_at_rest_M", m[heavy], False),
                               ("hole_frame_M_plus_mb", m[heavy] + mb, True)):
            vh = p[heavy] / m[heavy] if frame else np.zeros(3)
            uc = p[mem].sum(0) / mb - vh
            E, L, rS, riso = invariants(xc, uc, Mh)
            cap, tp, rb = capture_and_turning(E, L, Mh, rS)
            rows[lab] = dict(M_h=float(Mh), E=E, L=L, L_over_Mh=L / Mh, r_iso=riso, r_S=rS,
                             captured=cap, turning_point_rS=tp, barrier_rS=rb)
            if lab == "hole_frame_M":
                curves.append((os.path.basename(path), E, L, Mh, tp))
        # Newtonian conic of the centre of mass about M + m_b (the inputs' r_p)
        v = p[mem].sum(0) / mb - p[heavy] / m[heavy]
        mu = m[heavy] + mb
        r = np.linalg.norm(xc)
        eps = 0.5 * float(v @ v) - mu / r
        h = abs(float(xc[0] * v[1] - xc[1] * v[0]))
        ecc = math.sqrt(max(0.0, 1.0 + 2.0 * eps * h * h / mu ** 2))
        rows["newton_conic"] = dict(e=ecc, r_p=h * h / mu / (1.0 + ecc), energy=eps, h=h)
        res[os.path.relpath(path, WT)] = rows

    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 2.8))
    rr = np.linspace(2.05, 40.0, 2000)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["yellow"]]
    for n, (name, E, L, Mh, tp) in enumerate(curves):
        ax.plot(rr, V2(rr, L, Mh), color=cols[n % 4], lw=1.0,
                label=f"{name}: $L={L:.2f}$")
        ax.axhline(E * E, color=cols[n % 4], lw=0.7, ls="--")
        if tp:
            ax.plot([tp], [E * E], "o", ms=4, color=cols[n % 4])
    ax.set_ylim(0.9, 1.1)
    ax.set_xlabel(r"areal radius $r_S\,[M]$")
    ax.set_ylabel(r"$V^2=(1-2M/r_S)(1+L^2/r_S^2)$")
    ax.set_title("dashed: $E^2$ of the members' centre of mass; dot: turning point",
                 fontsize=6)
    ax.legend(fontsize=5)
    fig.tight_layout()
    paths = fs.save(fig, os.path.join(out, "fig_review_gr"))
    return res, paths


def main():
    mode, out = sys.argv[1], sys.argv[2]
    if out == "-":
        out = os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    if mode == "nr":
        res, paths = check_nr(out, sys.argv[3], sys.argv[4])
    elif mode == "gr":
        res, paths = check_gr(out, sys.argv[3:])
    else:
        raise SystemExit(__doc__)
    with open(os.path.join(out, f"review_{mode}.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
    for p in paths:
        print("figure:", p)


if __name__ == "__main__":
    main()
