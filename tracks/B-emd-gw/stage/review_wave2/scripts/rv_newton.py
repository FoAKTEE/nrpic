"""Lead's independent recomputation of newton_tests (wave 2 review, R7-R9 of ../JOURNAL.md).

R7 (H1): the force error of the seven-point Laplacian on the fundamental mode,
    F = [(kh/2)/sin(kh/2)]^2, put into linear Zel'dovich growth in an Einstein-de Sitter
    background, D'' + (3/(2a)) D' - (3F/(2a^2)) D = 0 (' = d/da), D(1) = 1, D'(1) = 1;
    predicted largest sheet error in units of the displacement (a - 1) d/k:
    (D_F(a) - a)/(a - 1). Own integration; compared with the measured values the helper's
    registered analysis B-20261115-173904-a7297e3 wrote (pancake.json).
R8 (N1): first x crossing t_x (zero of dI_xx after its minimum, linear interpolation)
    and the quadrupole energy E = (1/5) int dddQ_ij dddQ_ij dt to t_x from the raw d3I
    columns of the history files (own reading of newton.newton.hst; trace removed;
    records after a step below half the nominal one dropped); Richardson extrapolation.
R9 (N3): E / (M (2 alpha)^(7/2)) and t_x / t_turn across the rescaled runs.

Usage: rv_newton.py OUTDIR
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

S = "/data/haiyangw/nrpic/scratch/B-emd-gw"
PANCAKE_JSON = f"{S}/B-20261115-173904-a7297e3/pancake.json"
ELL = {32: f"{S}/B-20261115-163613-790095f/ell32", 64: f"{S}/B-20261115-163615-7bc8b30/ell64",
       128: f"{S}/B-20261115-163617-085c093/ell128"}
DTCHECK = f"{S}/B-20261115-163618-ea94065"
SELF = {32: f"{S}/B-20261115-163620-5b286c1", 64: f"{S}/B-20261115-163621-0ae44f1"}
ALPHA_B, T_TURN_B, MASS = 0.11122237, 9.531621514886838, 0.75


def h1_error(n, a_out):
    kh = 2 * np.pi / n
    F = ((kh / 2) / np.sin(kh / 2)) ** 2

    def rhs(a, y):
        return [y[1], -1.5 / a * y[1] + 1.5 * F / a ** 2 * y[0]]
    sol = solve_ivp(rhs, (1.0, max(a_out)), [1.0, 1.0], method="DOP853", rtol=1e-12,
                    atol=1e-14, dense_output=True)
    D = sol.sol(np.array(a_out))[0]
    return F - 1.0, [(d - a) / (a - 1) for d, a in zip(D, a_out)]


def read_hst(path):
    with open(path) as f:
        hdr = [ln for ln in f if ln.startswith("#")]
    cols = {}
    for tok in hdr[-1].replace("#", "").split():
        i, name = tok.split("]=")
        cols[name] = int(i.strip("[")) - 1
    d = np.loadtxt(path)
    return {k: d[:, i] for k, i in cols.items()}


def crossing_and_energy(path, t_turn):
    h = read_hst(path)
    t = h["time"]
    dI = h["dI_xx"]
    # first zero of dI_xx from below after its minimum
    imin = int(np.argmin(dI))
    j = imin + int(np.argmax(dI[imin:] >= 0))
    tx = t[j - 1] + (0 - dI[j - 1]) * (t[j] - t[j - 1]) / (dI[j] - dI[j - 1])
    dt = h["dt"]
    nominal = np.median(dt[1:])
    keep = dt >= 0.5 * nominal
    keep[0] = False  # first record has no difference quotient
    td = h["time_d3I"]
    names = ["d3I_xx", "d3I_xy", "d3I_xz", "d3I_yy", "d3I_yz", "d3I_zz"]
    D = {n: h[n] for n in names}
    tr = (D["d3I_xx"] + D["d3I_yy"] + D["d3I_zz"]) / 3.0
    qq = ((D["d3I_xx"] - tr) ** 2 + (D["d3I_yy"] - tr) ** 2 + (D["d3I_zz"] - tr) ** 2
          + 2 * (D["d3I_xy"] ** 2 + D["d3I_xz"] ** 2 + D["d3I_yz"] ** 2))
    # each record's d3I is the mean over its step: rectangle rule over the steps,
    # the last step clipped at t_x
    t_prev = t - dt
    sel = keep & (t_prev < tx)
    w = np.minimum(t[sel], tx) - t_prev[sel]
    E = 0.2 * np.sum(qq[sel] * w)
    return {"t_x": float(t_turn + tx), "tx_rel_time": float(tx), "E": float(E),
            "E_over_M": float(E / MASS), "n_records": int(len(t)),
            "n_dropped_short": int((~keep[1:]).sum()), "nominal_dt": float(nominal),
            "mass_hst": float(h["mass"][0])}


def richardson(N, v):
    (n1, v1), (n2, v2), (n3, v3) = sorted(zip(N, v))
    r = n2 / n1
    p = np.log(abs((v2 - v1) / (v3 - v2))) / np.log(r)
    vinf = v3 + (v3 - v2) / (r ** p - 1)
    return float(p), float(vinf)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    res = {"R7": {}, "R8": {}, "R9": {}}
    pj = json.load(open(PANCAKE_JSON))
    for n in (16, 32, 64):
        key = f"P1_athenak_n{n}"
        targets = [2, 5, 10, 15]
        a_rec = [pj[key][f"a_rec_{a}"] for a in targets]
        eps, pred = h1_error(n, a_rec)
        meas = [pj[key][f"ex_cont_a{a}"] for a in targets]
        their = [pj[key][f"ex_h1_pred_a{a}"] for a in targets]
        res["R7"][n] = {"F_minus_1": eps, "a": a_rec, "pred_lead": pred,
                        "pred_helper": their, "measured_helper": meas,
                        "meas_over_pred_lead": [m / p for m, p in zip(meas, pred)],
                        "pred_lead_over_helper": [p / q for p, q in zip(pred, their)]}
    for N, p in ELL.items():
        res["R8"][N] = crossing_and_energy(f"{p}/newton.newton.hst", T_TURN_B)
    res["R8"]["dt0.01_N64"] = crossing_and_energy(_find_hst(DTCHECK), T_TURN_B)
    Ns = [32, 64, 128]
    res["R8"]["richardson_t_x"] = richardson(Ns, [res["R8"][n]["t_x"] for n in Ns])
    res["R8"]["richardson_E_over_M"] = richardson(Ns, [res["R8"][n]["E_over_M"] for n in Ns])
    for N, base in SELF.items():
        rows = {}
        for al in (0.05, 0.1, 0.2):
            s = ALPHA_B / al
            r = crossing_and_energy(f"{base}/alpha_{al}/newton.newton.hst", T_TURN_B * s ** 1.5)
            rows[str(al)] = {"E_scaled": r["E_over_M"] / (2 * al) ** 3.5,
                             "tx_over_tturn": r["t_x"] / (T_TURN_B * s ** 1.5)}
        rb = res["R8"][N]
        rows[str(ALPHA_B)] = {"E_scaled": rb["E_over_M"] / (2 * ALPHA_B) ** 3.5,
                              "tx_over_tturn": rb["t_x"] / T_TURN_B}
        Es = np.array([v["E_scaled"] for v in rows.values()])
        Ts = np.array([v["tx_over_tturn"] for v in rows.values()])
        res["R9"][N] = {"rows": rows, "E_spread_rel": float(Es.max() / Es.min() - 1),
                        "tx_spread_rel": float(Ts.max() / Ts.min() - 1)}
    with open(f"{out}/rv_newton.json", "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


def _find_hst(base):
    for root, _, files in os.walk(base):
        if "newton.newton.hst" in files:
            return os.path.join(root, "newton.newton.hst")
    raise FileNotFoundError(base)


if __name__ == "__main__":
    main()
