"""P0: the verifier's readers and integrator on analytic cases (writes vtest.json, fig_v_tests).

Run: python tracks/F-hills/stage/G1/verifier/scripts/vtest.py --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vread  # noqa: E402
import vnewton  # noqa: E402
import figstyle  # noqa: E402


def kepler_xy(t, a=4.0, e=0.3, mtot=0.25, t_peri=1.3):
    n = np.sqrt(mtot / a ** 3)
    M = n * (t - t_peri)
    E = M.copy()
    for _ in range(60):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    x = a * (np.cos(E) - e)
    y = a * np.sqrt(1 - e * e) * np.sin(E)
    Ed = n / (1 - e * np.cos(E))
    vx = -a * np.sin(E) * Ed
    vy = a * np.sqrt(1 - e * e) * np.cos(E) * Ed
    return x, y, vx, vy


def write_tracker(path, it, t, x, y, vx, vy):
    with open(path, "w") as f:
        f.write("# Black Hole\n# 1:iter 2:time 3:x 4:y 5:z 6:vx 7:vy 8:vz\n")
        for k in range(len(t)):
            f.write(f"{it[k]} {float(t[k])!r} {float(x[k])!r} {float(y[k])!r} 0.0 {float(vx[k])!r} {float(vy[k])!r} 0.0\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = ap.parse_args().out
    tmp = os.path.join(out, "synthetic")
    os.makedirs(tmp, exist_ok=True)
    res = {}
    dt = 2.0 ** -9
    a, e, mt, tp = 2.0, 0.3, 0.25, 1.3
    P = 2 * np.pi * np.sqrt(a ** 3 / mt)

    # (a) tracker join: five segments; restarts at earlier times than the previous segment's end
    t_all = np.arange(0, 120001) * dt
    t_all = t_all[t_all <= 60.0]
    it_all = np.arange(len(t_all))
    x, y, vx, vy = kepler_xy(t_all, a, e, mt, tp)
    bounds = [(0.0, 13.0), (12.0, 25.5), (25.0, 25.3), (25.0, 44.0), (40.0, 60.0)]
    files = []
    for s, (t0, t1) in enumerate(bounds):
        sel = (t_all >= t0) & (t_all <= t1)
        p = os.path.join(tmp, f"seg{s}.txt")
        xs = x[sel].copy()
        if s == 3:  # inject a 1e-6 offset inside the overlap with segment 2 (t < 25.3)
            k = np.where(t_all[sel] < 25.3)[0]
            xs[k[5]] += 1e-6
        write_tracker(p, it_all[sel], t_all[sel], xs, y[sel], vx[sel], vy[sel])
        files.append(p)
    arrs = [vread.read_tracker(p) for p in files]
    joined, ov = vread.join_segments(arrs, [os.path.basename(p) for p in files])
    g = vread.gaps(joined[:, 1])
    ok_t = np.array_equal(joined[:, 1], t_all)
    # the 1e-6 offset lies in segment 3 before 40 (kept), so the join differs from truth there
    dx = np.abs(joined[:, 2] - x).max()
    ov_max = {f"{o['earlier']}>{o['later']}": o["max_dx"] for o in ov}
    res["a_join"] = {"times_exact": bool(ok_t), "gap": g, "max_dx_vs_truth": float(dx),
                     "overlaps": ov_max,
                     "pass": bool(ok_t and abs(g["max_step"] - dt) < 1e-15 and abs(dx - 1e-6) < 1e-12
                                  and all(abs(ov_max[k] - 1e-6) < 1e-12 for k in ("seg1.txt>seg3.txt", "seg2.txt>seg3.txt"))
                                  and all(v == 0.0 for k, v in ov_max.items()
                                          if k not in ("seg1.txt>seg3.txt", "seg2.txt>seg3.txt")))}

    # (b) closest approach on the eccentric orbit: pericentre r = a(1-e) at t_peri + k P
    r = np.hypot(x, y)
    mins = vread.minima(t_all, r)
    m0 = mins
    errs = [(abs(mm[1] - a * (1 - e)) / (a * (1 - e)), min(abs(mm[0] - tp - k * P) for k in range(3))) for mm in m0]
    res["b_minima"] = {"found": mins, "expected_r": a * (1 - e), "expected_t": [tp, tp + P],
                       "rel_err_r": [x_[0] for x_ in errs], "err_t": [x_[1] for x_ in errs],
                       "pass": bool(len(errs) >= 2 and max(x_[0] for x_ in errs) < 1e-8 and max(x_[1] for x_ in errs) < 1e-5)}

    # (c) Newton: Kepler ellipse after one period; three-body conservation
    m = np.array([0.125, 0.125])
    x0r, y0r, vx0r, vy0r = kepler_xy(np.array([0.0]), a, e, mt, tp)
    rel = np.array([x0r[0], y0r[0], 0.0])
    vrel = np.array([vx0r[0], vy0r[0], 0.0])
    X0 = np.array([0.5 * rel, -0.5 * rel])
    V0 = np.array([0.5 * vrel, -0.5 * vrel])
    tt, X, V, sol = vnewton.integrate(m, X0, V0, P, dt_out=P / 1000)
    ret = np.linalg.norm((X[-1, 0] - X[-1, 1]) - rel) / np.linalg.norm(rel)
    E = vnewton.energy(m, X, V)
    m3, x3, v3 = vnewton.deck_state(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..",
                                                  "binary_conv", "inputs", "p1b_R16n.athinput"))
    t3, X3, V3, _ = vnewton.integrate(m3, x3, v3, 200.0, dt_out=0.5)
    E3 = vnewton.energy(m3, X3, V3)
    L3 = vnewton.angmom(m3, X3, V3)[:, 2]
    res["c_newton"] = {"note": "bounds as predicted in JOURNAL P0(c); the Kepler energy bound 1e-11 is the one that failed",
                       "kepler_return_rel": float(ret), "kepler_dE_rel": float(np.abs(E / E[0] - 1).max()),
                       "three_body_dE_rel": float(np.abs(E3 / E3[0] - 1).max()),
                       "three_body_dLz_rel": float(np.abs(L3 / L3[0] - 1).max()),
                       "pass": bool(ret < 1e-9 and np.abs(E / E[0] - 1).max() < 1e-11
                                    and np.abs(E3 / E3[0] - 1).max() < 1e-9 and np.abs(L3 / L3[0] - 1).max() < 1e-9)}

    # (d) horizon summary with restart repeats, two failed searches and one NaN
    p = os.path.join(tmp, "hs.txt")
    rows = []
    for k in range(40):
        tk = 0.03125 * k
        rows.append([4, tk, 0.13 + 1e-6 * k] + [1e-7 * k] * 4 + [0.84, 1e-4, -1e-4, 0.1, 0.09])
    lines = ["# 1:iter 2:time 3:mass ..."]
    def fmt(r):
        return f"{r[0]} {r[1]:.6g} " + " ".join(f"{v:.15e}" for v in r[2:])
    for k, row in enumerate(rows):
        if k in (10, 25):       # failed: repeat of the previous row's columns 3-12 at the new time
            row = [row[0], row[1]] + rows[k - 1][2:]
            rows[k] = row
        if k == 30:
            row = [row[0], row[1], float("nan")] + row[3:]
        lines.append(fmt(row))
        if k == 20:             # a restart: rows 15-20 written again (same values)
            lines.append("# 1:iter 2:time 3:mass ...")
            for q in range(15, 21):
                lines.append(fmt(rows[q]))
    open(p, "w").write("\n".join(lines) + "\n")
    hs = vread.read_horizon_summary(p)
    res["d_horizon"] = {"n_kept": int(len(hs["t"])), "n_raw": hs["n_raw"], "n_failed": int(hs["failed"].sum()),
                        "failed_t": hs["t"][hs["failed"]].tolist(),
                        "pass": bool(len(hs["t"]) == 40 and hs["failed"].sum() == 3)}

    # (e) waveform times with duplicates
    p = os.path.join(tmp, "wf.txt")
    tw = list(np.arange(0, 10.01, 0.25)) + list(np.arange(5, 7.01, 0.25))
    open(p, "w").write("# 1:time 2:2-2\n" + "\n".join(f"{v:.6g} 0.0" for v in tw) + "\n")
    nraw, tu = vread.read_wave_times(p)
    gc = vread.grid_check(tu, 0, 10, 0.25)
    res["e_wave"] = {"n_raw": nraw, "n_unique": int(len(tu)), "grid": gc,
                     "pass": bool(nraw == 50 and len(tu) == 41 and gc["n_missing"] == 0)}
    res["all_pass"] = all(v["pass"] for v in res.values() if isinstance(v, dict))

    with open(os.path.join(out, "vtest.json"), "w") as f:
        json.dump(res, f, indent=1)

    figstyle.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(8, 2.8))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.88, wspace=0.42)
    ax[0].plot(t_all, np.abs(joined[:, 2] - x) + 1e-18, color=figstyle.PAL["red"], label="join - truth")
    for t0, t1 in bounds:
        ax[0].axvline(t0, **figstyle.MASK_LINE)
    ax[0].set_yscale("log"); ax[0].set_xlabel("t"); ax[0].set_ylabel("|x_join - x_true| (+1e-18)")
    ax[0].set_title("join of 5 segments", fontsize=10)
    ax[1].plot(t_all, r, color=figstyle.PAL["blue"], label="Kepler r(t)")
    for mm in mins:
        ax[1].plot(mm[0], mm[1], "o", color=figstyle.PAL["red"], ms=4)
    ax[1].axhline(a * (1 - e), **figstyle.GUIDE)
    ax[1].set_xlabel("t"); ax[1].set_ylabel("r"); ax[1].set_title("minima found", fontsize=10)
    ax[2].plot(t3, np.abs(E3 / E3[0] - 1) + 1e-18, color=figstyle.PAL["red"], label="|dE/E|")
    ax[2].plot(t3, np.abs(L3 / L3[0] - 1) + 1e-18, color=figstyle.PAL["blue"], ls="--", label="|dLz/Lz|")
    ax[2].set_yscale("log"); ax[2].set_xlabel("t"); ax[2].legend(loc="lower right")
    ax[2].set_title("three-body conservation", fontsize=10)
    figstyle.save(fig, os.path.join(out, "fig_v_tests"))
    print(json.dumps({k: v["pass"] for k, v in res.items() if isinstance(v, dict)}), "all", res["all_pass"])


if __name__ == "__main__":
    main()
