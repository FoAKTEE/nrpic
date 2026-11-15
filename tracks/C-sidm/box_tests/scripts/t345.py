#!/usr/bin/env python3
"""T3 (relaxation to Maxwell-Juttner), T4 (two-temperature initial rate) and T5 (entropy)
of collide/TESTS.md with the release executable.

    python3 t345.py DESIGN_JSON [--theta2 0.001,1.0] [--seeds 1,2] [--n 1000000]
                    [--nproc 8] [--exe PATH] [--tag cpu]

twotemp box (theta_1 = 3 theta_2, n1 = n2, rho_0 = 1, sigma = 1), N = 1e6, 16^3 cells
(244 particles per cell), dt = 0.005 tau_rel (design run). Per (theta_2, seed) two runs of
the same problem (same particle file, seed, dt; the collisional state is a function of
these only, T10):
  A  to 0.25 tau_rel, snapshots every 0.01 tau_rel (T4 window and early entropy),
  B  to 15 tau_rel, snapshots every 0.25 tau_rel (T3 end state, T5).
The snapshot of B at 0.25 tau_rel must equal the last one of A bit for bit (checked).
The analysis is the wave-1 one, unchanged: `collide/analysis/an_box.py relax` on a
directory that links A's snapshots and B's later ones in time order.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

import boxlib as bl

AN_BOX = os.path.join(bl.COLLIDE, "analysis", "an_box.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--theta2", default="0.001,1.0")
    ap.add_argument("--seeds", default="1,2")
    ap.add_argument("--n", type=int, default=1_000_000)
    ap.add_argument("--nproc", type=int, default=8)
    ap.add_argument("--exe", default=bl.EXE_CPU)
    ap.add_argument("--tag", default="cpu")
    a = ap.parse_args()
    des = json.load(open(a.design))["T3_T4_T5"]
    out = bl.outdir()
    jobs, cases = [], []
    for th2 in a.theta2.split(","):
        d = des[th2]
        tau, dt = d["tau_rel"], d["dt"]
        nA, nB = int(round(0.25 * tau / dt)), int(round(15 * tau / dt))
        for seed in [int(s) for s in a.seeds.split(",")]:
            base = f"T345_th{th2}_s{seed}"
            ic = os.path.join(out, base + "_ic")
            meta = bl.make_box(ic, "twotemp", n=a.n, theta=3 * float(th2),
                               theta2=float(th2), sigma=1.0, seed=seed)
            common = bl.mesh_overrides(16) + [
                f"particles/dt={dt!r}", "particles/coll_sigma=1.0", f"job/rng_seed={seed}",
                f"particles/particle_file={os.path.join(ic, 'box.nrp')}"]
            rdA = os.path.join(out, base + "_A")
            rdB = os.path.join(out, base + "_B")
            jobs.append((rdA, common + [f"time/nlim={nA}",
                                        f"particles/snap_dt={2 * dt * (1 - 1e-9)!r}"],
                         dict(exe=a.exe)))
            jobs.append((rdB, common + [f"time/nlim={nB}",
                                        f"particles/snap_dt={50 * dt * (1 - 1e-9)!r}"],
                         dict(exe=a.exe)))
            cases.append((base, ic, rdA, rdB, th2, seed, meta))
    # long runs first so that they start at once
    jobs.sort(key=lambda j: 0 if j[0].endswith("_B") else 1)
    rr = bl.run_many(jobs, a.nproc)
    walls = {os.path.basename(j[0]): dict(rc=r["rc"], wall=r["wall"]) for j, r in zip(jobs, rr)}
    res = dict(runs=walls, cases={})
    for base, ic, rdA, rdB, th2, seed, meta in cases:
        c = dict(theta2=th2, seed=seed)
        if walls[os.path.basename(rdA)]["rc"] or walls[os.path.basename(rdB)]["rc"]:
            c["failed"] = True
            res["cases"][base] = c
            continue
        fA = bl.snapshots(rdA)
        fB = bl.snapshots(rdB)
        sA = bl.snap.read_snapshot(fA[-1])
        sB = bl.snap.read_snapshot(fB[1])
        c["A_last_equals_B_at_quarter_tau"] = bool(
            sA["cycle"] == sB["cycle"] and np.array_equal(sA["u"], sB["u"]) and
            np.array_equal(sA["x"], sB["x"]))
        c["A_last_cycle"], c["B_second_cycle"] = sA["cycle"], sB["cycle"]
        merged = os.path.join(out, base + "_merged")
        os.makedirs(merged, exist_ok=True)
        files = fA + fB[2:]
        for k, f in enumerate(files):
            dst = os.path.join(merged, f"box.part.{k:05d}.bin")
            if not os.path.exists(dst):
                os.symlink(f, dst)
        an = os.path.join(out, "analysis")
        p = subprocess.run([sys.executable, AN_BOX, "relax", merged, "box",
                            os.path.join(ic, "box.json"), an],
                           capture_output=True, text=True)
        if p.returncode != 0:
            c["analysis_error"] = p.stderr[-2000:]
        else:
            r = json.load(open(os.path.join(an, "relax_box.json")))
            os.replace(os.path.join(an, "relax_box.json"), os.path.join(an, f"relax_{base}.json"))
            os.replace(os.path.join(an, "relax_box.png"), os.path.join(an, f"relax_{base}.png"))
            c.update(r)
        # conservation over the long run, exactly rounded sums (T1 information)
        s0 = bl.snap.read_snapshot(fB[0])
        s1 = bl.snap.read_snapshot(fB[-1])
        e0 = bl.fsum_cols((s0["m"] * bl.W(s0["u"]))[:, None])[0]
        e1 = bl.fsum_cols((s1["m"] * bl.W(s1["u"]))[:, None])[0]
        c["B_exact_dE_rel"] = float((e1 - e0) / e0)
        h = bl.coll_history(rdB)
        c["B_collisions"] = float(h["n_coll"].sum())
        c["B_n_trunc"] = float(h["n_trunc"].sum())
        c["B_max_nsub"] = float(h["max_nsub"].max())
        c["B_max_P"] = float(h["max_P"].max())
        bound = 1e-14 * np.sqrt(h["n_coll"] + 1)
        c["B_T1_step_pass"] = bool((np.abs(h["dE"]) / h["sum_MW"] < bound).all() and
                                   (np.max(np.abs(np.stack([h["dP1"], h["dP2"], h["dP3"]])), 0)
                                    / h["sum_MW"] < bound).all() and c["B_n_trunc"] == 0)
        res["cases"][base] = c
    ok = [c for c in res["cases"].values() if not c.get("failed")]
    res["T3_pass"] = bool(ok and all(c.get("T3_pass") for c in ok))
    res["T4_pass"] = bool(ok and all(c.get("T4_pass") for c in ok))
    res["T5_pass"] = bool(ok and all(c.get("T5_pass") for c in ok))
    bl.save_json(os.path.join(out, f"t345_{a.tag}.json"), res)
    keys = ("A_last_equals_B_at_quarter_tau", "tau_rel", "theta_eq", "slope_exact",
            "T4_slope", "T4_slope_se", "T4_ratio", "T4_pass", "T3_ks_p", "T3_u2W_over3",
            "T3_u2W_se", "T3_theta1_end", "T3_theta2_end", "T3_pass", "T5_s0", "T5_s_mix",
            "T5_s_end", "T5_s_eq", "T5_se", "T5_pass", "B_exact_dE_rel", "B_collisions",
            "B_T1_step_pass", "B_max_nsub", "analysis_error")
    print(json.dumps({k: {kk: c.get(kk) for kk in keys} for k, c in res["cases"].items()},
                     indent=1))
    print("T3", res["T3_pass"], "T4", res["T4_pass"], "T5", res["T5_pass"])


if __name__ == "__main__":
    sys.exit(main())
