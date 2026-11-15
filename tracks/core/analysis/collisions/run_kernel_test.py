#!/usr/bin/env python3
"""P0: unit test of the collision kernels (nrpic_collide.hpp) against the test vectors
of track C (REFERENCES/test_vectors.json at a pinned commit of track/C-sidm: inputs
exact, outputs from a 60-digit evaluation), for several compilations of the header and
for the Python twin; conservation of the pair four-momentum is evaluated at 50 digits.

  run_kernel_test.py OUTDIR
"""
import json
import os
import subprocess
import sys

import mpmath as mp
import numpy as np

import common
from nrpic import collide

TRACK_COMMIT = "4c76ca83f89e61bf209940c91d6d6274b7855b67"
VECTORS = "tracks/C-sidm/collide/REFERENCES/test_vectors.json"
BUILDS = {
    "O0": ["-O0"],
    "O2": ["-O2"],
    "O3_native_contract": ["-O3", "-march=native", "-ffp-contract=fast"],
    "O3_native_nocontract": ["-O3", "-march=native", "-ffp-contract=off"],
}
EPS = 2.0**-52


def main():
    out = os.path.abspath(sys.argv[1])
    os.makedirs(out, exist_ok=True)
    raw = subprocess.run(["git", "-C", common.REPO, "show", TRACK_COMMIT + ":" + VECTORS],
                         capture_output=True, check=True).stdout
    with open(os.path.join(out, "test_vectors.json"), "wb") as fp:
        fp.write(raw)
    cases = [c for c in json.loads(raw)["cases"]
             if float.fromhex(c["ma"]) == 1.0 and float.fromhex(c["mb"]) == 1.0]
    skipped = len(json.loads(raw)["cases"]) - len(cases)
    inp = np.array([[float.fromhex(s) for s in c["ua"] + c["ub"] + c["nhat"]]
                    for c in cases])
    exp = np.array([c["ua_out"] + c["ub_out"] for c in cases])
    vexp = np.array([c["vmol"] for c in cases])
    text = "".join(" ".join(float(x).hex() for x in row) + "\n" for row in inp)

    results = {}
    for name, flags in BUILDS.items():
        exe = os.path.join(out, "kernel_test_" + name)
        subprocess.run(["g++", "-std=c++17", "-DNRPIC_STANDALONE"] + flags
                       + ["-I", os.path.join(common.REPO, "athenak", "src"),
                          os.path.join(common.HERE, "kernel_test.cpp"), "-o", exe],
                       check=True)
        res = subprocess.run([exe], input=text.encode(), capture_output=True, check=True)
        results[name] = np.array([[float.fromhex(s) for s in ln.split()]
                                  for ln in res.stdout.decode().splitlines()])
    # Python twin
    g1, wa, wb = collide.gamma_rel_m1(inp[:, 0:3], inp[:, 3:6])
    uan, ubn = collide.scatter(inp[:, 0:3], inp[:, 3:6], inp[:, 6:9], g1, wa, wb)
    results["python_twin"] = np.column_stack([g1, collide.moller(g1, wa, wb), wa, wb, uan,
                                              ubn])

    scale = np.maximum(1.0, np.maximum(np.linalg.norm(inp[:, 0:3], axis=1),
                                       np.linalg.norm(inp[:, 3:6], axis=1)))
    mp.mp.dps = 50
    summary = {"track_commit": TRACK_COMMIT, "cases": len(cases),
               "skipped_unequal_physical_masses": skipped, "builds": {}}
    per_case = {}
    for name, r in results.items():
        err_u = np.max(np.abs(r[:, 4:10] - exp), axis=1)/scale
        # Moller speed: relative error, except where the reference is the rounding
        # noise of an exact zero (identical velocities: 4e-31 at 60 digits)
        err_v = np.where(vexp > 1e-25, np.abs(r[:, 1] - vexp)/np.maximum(vexp, 1e-300),
                         np.abs(r[:, 1] - vexp))
        # conservation at 50 digits, in units of eps x pair energy
        de = np.empty(len(cases))
        dp = np.empty(len(cases))
        for i in range(len(cases)):
            ua = [mp.mpf(float(x)) for x in inp[i, 0:3]]
            ub = [mp.mpf(float(x)) for x in inp[i, 3:6]]
            xa = [mp.mpf(float(x)) for x in r[i, 4:7]]
            xb = [mp.mpf(float(x)) for x in r[i, 7:10]]
            e0 = mp.sqrt(1 + sum(x*x for x in ua)) + mp.sqrt(1 + sum(x*x for x in ub))
            e1 = mp.sqrt(1 + sum(x*x for x in xa)) + mp.sqrt(1 + sum(x*x for x in xb))
            de[i] = float(abs(e1 - e0)/e0)/EPS
            dp[i] = float(max(abs(xa[k] + xb[k] - ua[k] - ub[k]) for k in range(3))/e0)/EPS
        per_case[name] = dict(err_u=err_u, err_v=err_v, de=de, dp=dp)
        summary["builds"][name] = {
            "max_err_u_over_scale": float(err_u.max()),
            "max_rel_err_vmol": float(err_v.max()),
            "max_energy_defect_eps": float(de.max()),
            "max_momentum_defect_eps": float(dp.max()),
            "identical_bits_to_O0": bool(np.array_equal(r, results["O0"])),
            "pass": bool(err_u.max() <= 1e-13 and de.max() <= 4.0 and dp.max() <= 4.0
                         and err_v.max() <= 1e-13),
        }
    summary["ok"] = all(b["pass"] for b in summary["builds"].values())
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    bulk = np.sqrt(1.0 + np.sum((0.5*(inp[:, 0:3] + inp[:, 3:6]))**2, axis=1))
    fig, axs = plt.subplots(1, 3, figsize=(8.0, 2.9))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.92, wspace=0.33)
    cols = {"O2": fs.PAL["red"], "O3_native_contract": fs.PAL["yellow"],
            "python_twin": fs.PAL["blue"]}
    for name, col in cols.items():
        pc = per_case[name]
        axs[0].loglog(bulk, np.maximum(pc["err_u"], 1e-18), ".", ms=3, color=col,
                      label=name.replace("_", " "))
        axs[1].loglog(bulk, np.maximum(pc["de"], 1e-3), ".", ms=3, color=col)
        axs[2].loglog(bulk, np.maximum(pc["err_v"], 1e-18), ".", ms=3, color=col)
    axs[0].axhline(1e-13, **fs.GUIDE)
    axs[1].axhline(4.0, **fs.GUIDE)
    axs[0].set_ylabel(r"error of $u'$ / max(1, $|u|$)")
    axs[1].set_ylabel(r"pair energy defect / $\epsilon E$")
    axs[2].set_ylabel(r"relative error of $v_{\rm Mol}$")
    for ax in axs:
        ax.set_xlabel("Lorentz factor of the pair's mean momentum")
    axs[0].legend(fontsize=7, loc="lower right")
    fig.savefig(os.path.join(out, "fig_kernel_test.png"), dpi=200)
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
