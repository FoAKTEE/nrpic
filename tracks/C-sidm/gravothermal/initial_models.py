"""Candidate initial models of the full-relativity runs (to be sampled by C-pre-4).

    python3 -E initial_models.py <criteria.json> <outdir>

For each b the F21 family (b, w0) is an exact static isotropic Einstein-Vlasov solution with
f(E) = A (e^{-E/kT_inf} - e^{-E_c/kT_inf}) for E < E_c (JOURNAL.md, test P3), so a model is
fixed by (b, w0) and its mass. The bracket of the onset runs from the maximum of the
fractional binding energy (F21's turning point, main.tex:280) to the trial-function root
<gamma> = gamma_cr (main.tex:274), with the exact fluid onset omega_0^2 = 0 in between.
This script lists models at chosen central redshifts across that bracket, in the units of
the code (G = c = 1, ADM mass M = 1): R/M, compactness, central lapse, kT_inf/m and E_c/m,
plus the hatted columns of F21.
"""
import json
import math
import os
import sys

from scipy.optimize import brentq

import tmb

ZLIST = (0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80)


def model_at_Z(b, Z, lo, hi):
    w0 = brentq(lambda w: tmb.solve(b, w)["Z0"] - Z, lo, hi, xtol=1e-12)
    return tmb.solve(b, w0)


def code_units(e):
    b, w0, C = e["b"], e["w0"], e["C"]
    ePhiR = math.sqrt(1.0 - 2.0 * C)                     # lapse at the surface
    return dict(R_over_M=1.0 / C, alpha_c=(1.0 - b * w0) * ePhiR, alpha_R=ePhiR,
                kT_inf_over_m=b * ePhiR, Ec_over_m=ePhiR, M0_over_M=e["Erest"] / e["E"])


def main(crit_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    crit = json.load(open(crit_path))
    out = {}
    L = ["# Candidate initial models across the onset bracket", "",
         "Code units G = c = 1, M = 1. alpha_c, alpha_R: lapse at the centre and the surface; "
         "the distribution is f(E) proportional to exp(-E/kT_inf) - exp(-E_c/kT_inf) for "
         "E < E_c with E = -p_t/m the conserved energy per unit rest mass; M0/M = E_rest/E.",
         "", "| b | Z(0) | w0 | R/M | C | alpha_c | kT_inf/m | E_c/m | M0/M | eps | v(0)/c | "
         "side |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for b, c in crit.items():
        bf = float(b)
        lo = 0.2 * c["max_E"]["w0"]
        hi = min(0.97 / bf, 3.0 * c["gavg_eq_gcr"]["w0"])
        rows = []
        for Z in ZLIST:
            try:
                e = model_at_Z(bf, Z, lo, hi)
            except ValueError:
                continue
            cu = code_units(e)
            onset = c.get("omega2_zero_F21gamma")
            side = []
            side.append("eps-stable" if e["w0"] < c["max_eps"]["w0"] else "eps-unstable")
            if onset:
                side.append("fluid-stable" if e["w0"] < onset["w0"] else "fluid-unstable")
            side.append("trial-stable" if e["w0"] < c["gavg_eq_gcr"]["w0"] else "trial-unstable")
            row = {k: v for k, v in e.items() if not k.startswith("_")}
            row.update(cu)
            row["side"] = " ".join(side)
            rows.append(row)
            L.append(f"| {b} | {Z:.2f} | {e['w0']:.6f} | {cu['R_over_M']:.4f} | {e['C']:.5f} | "
                     f"{cu['alpha_c']:.5f} | {cu['kT_inf_over_m']:.5f} | {cu['Ec_over_m']:.5f} | "
                     f"{cu['M0_over_M']:.6f} | {e['eps']:.5f} | {e['v0']:.4f} | {row['side']} |")
        out[b] = rows
    json.dump(out, open(os.path.join(outdir, "initial_models.json"), "w"), indent=1)
    open(os.path.join(outdir, "initial_models.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
