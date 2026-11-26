#!/usr/bin/env python3
"""V1 complement: rms of the Hamiltonian constraint over the shell, in units of 16 pi rho_b(tau), and the largest
|alpha - 1|, per dump of the Szekeres members; regions from the initial slice as in szk_verify.py (core: KT of the
central cell; outside: H_T t_i = 2/3; shell: the rest). Prediction P21 of szekeres/JOURNAL.md entry 8: the H order
between N128 and N256 at tau 10 and 20 equals the K-error order within 0.5.

    python -I szk_hcon.py --out DIR --prep PREPDIR --member N64=DIR ...
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from szk_verify import read_cosmo, read_field, T_I, HUB, CH  # noqa: E402


def kt_masks(prep):
    n, F = read_cosmo(os.path.join(prep, "fields.bin"))
    N = n[0]
    nc = N ** 3
    KT = np.empty(nc)
    for s0 in range(0, nc, CH):
        sl = slice(s0, min(nc, s0 + CH))
        psi, K = np.asarray(F[0, sl]), np.asarray(F[1, sl])
        A = [np.asarray(F[3 + i, sl]) / psi ** 6 for i in range(6)]
        xx, xy, xz, yy, yz, zz = A
        tr2 = xx ** 2 + yy ** 2 + zz ** 2 + 2 * (xy ** 2 + xz ** 2 + yz ** 2)
        det = xx * (yy * zz - yz ** 2) - xy * (xy * zz - yz * xz) + xz * (xy * yz - yy * xz)
        d = np.sign(det) * np.sqrt(1.5 * tr2)
        KT[sl] = K / 3 - d / 3
    mid = N // 2
    kc = KT[(mid * N + mid) * N + mid]
    core = np.abs(KT - kc) < 1e-10 * abs(kc)
    out = np.abs(-KT * T_I - 2 / 3) < 1e-12
    return N, dict(core=core, shell=~core & ~out, outside=out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--prep", required=True)
    ap.add_argument("--member", action="append", default=[])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rho_b0 = 3 * HUB ** 2 / (8 * math.pi)
    res = {}
    for spec in a.member:
        name, d = spec.split("=", 1)
        N, M = kt_masks(os.path.join(a.prep, name))
        rows = {}
        for f in sorted(glob.glob(os.path.join(d, "szk.field.*.bin"))):
            F = read_field(f)
            tau = F["t"]
            rb = rho_b0 * (T_I / (T_I + tau)) ** 2
            H = np.asarray(F["H"])
            al = np.asarray(F["alpha"])
            rows[f"{tau:.4f}"] = dict(tau=tau, **{f"H_rms_{k}": float(np.sqrt(np.nanmean((H[m] / (16 * math.pi * rb)) ** 2)))
                                                for k, m in M.items()},
                                      alpha_dev_max=float(np.nanmax(np.abs(al - 1))))
            print(name, rows[f"{tau:.4f}"], flush=True)
        res[name] = rows
    orders = {}
    for n1, n2 in (("N64", "N128"), ("N128", "N256")):
        if n1 in res and n2 in res:
            for k in sorted(set(res[n1]) & set(res[n2])):
                if float(k) > 0:
                    e1, e2 = res[n1][k]["H_rms_shell"], res[n2][k]["H_rms_shell"]
                    orders[f"{n1}->{n2} tau={float(k):g}"] = math.log2(e1 / e2) if e1 > 0 and e2 > 0 else None
    res["orders_H_shell"] = orders
    print(json.dumps(orders, indent=1))
    with open(os.path.join(a.out, "szk_hcon.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
