#!/usr/bin/env python3
"""Analysis run of the note (N1): time series of the two baselines for the first passages.

For the start states of the two three-black-hole inputs (q = M/m_b = 4: the P1 input of
wave 2, tracks/F-hills/nr_first/inputs/p1_q4.athinput; q = 10: the wave-1 input
tracks/F-hills/three_punctures/inputs/hills_q10_m8.athinput) it integrates
  newton        the full Newtonian three-body problem (the heavy black hole moves);
  newton_fixed  Newtonian members about a point mass fixed at the origin;
  hrna          the geodesic baseline of arXiv:2404.16270 (exact Schwarzschild acceleration
                of each member plus the Newtonian pair force, black hole fixed),
from the same positions and velocities relative to M. It uses the lead's functions of
tracks/F-hills/stage/G0/checks/lead_checks.py (read_athinput, newton_full, hrna_from_state,
kepler_elements; read only) and the member energies of tracks/F-hills/nr_first/scripts/
nrread.py (two-body with M; against the barycentre of M and the other member). The same
functions made the lead's V5, V5b, V6 and the nr_first run E6, so every number printed here
must agree with theirs (prediction N1 of note/JOURNAL.md).

Writes <out>/passage_curves.npz (time series) and <out>/passage_summary.json. Needs numba
(python of scratch/F-hills/venv-gb). Usage: passage_curves.py [outdir] (default
$NRPIC_RUN_DIR).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TRACK, "stage", "G0", "checks"))
sys.path.insert(0, os.path.join(TRACK, "nr_first", "scripts"))
import lead_checks as lc  # noqa: E402
import nrread as nr  # noqa: E402

CASES = {
    "q4": ("nr_first/inputs/p1_q4.athinput", 5.0),            # nominal a_b of the design
    "q10": ("three_punctures/inputs/hills_q10_m8.athinput", 3.0),
}


def turning(t, r):
    i = np.arange(1, len(r) - 1)
    lo = i[(r[i] < r[i - 1]) & (r[i] <= r[i + 1])]
    return [(float(t[k]), float(r[k])) for k in lo]


def one(key):
    rel, a0 = CASES[key]
    m, x, p = lc.read_athinput(os.path.join(TRACK, rel))   # comp0 = m1, comp1 = m2, comp2 = M
    M, m1, m2 = m[2], m[0], m[1]
    mb = m1 + m2
    v = p / m[:, None]
    rt = a0 * (M / mb) ** (1 / 3)
    Eu = m1 * m2 / a0 * (M / mb) ** (1 / 3)
    xcm = (m1 * x[0] + m2 * x[1]) / mb
    vcm = (m1 * v[0] + m2 * v[1]) / mb
    _, e_cm, rp_cm = lc.kepler_elements(xcm - x[2], vcm - v[2], M + mb)
    epsb, e_b, _ = lc.kepler_elements(x[0] - x[1], v[0] - v[1], mb)
    S = dict(input=rel, M=M, m1=m1, m2=m2, a0=a0, r_t=rt, unit_E=Eu, a_b=-mb / (2 * epsb),
             e_b=e_b, cm_rp=rp_cm, cm_e=e_cm, r0=float(np.linalg.norm(xcm - x[2])))
    arr = {}
    ts, Y = lc.newton_full(m, x, p, t_end=1500.0, nout=30001)
    X = Y[:, :9].reshape(-1, 3, 3)
    V = Y[:, 9:].reshape(-1, 3, 3)
    E = nr.member_energies(X, V, m, iM=2)
    ie = 0 if E["E_0_bc"][-1] > 0 else 1
    ic = 1 - ie
    late = ts >= 300
    S["newton"] = dict(ejected=ie + 1, captured=ic + 1,
                       E_ej_bc_u=float(E[f"E_{ie}_bc"][-1] / Eu),
                       E_ej_bc_range_late_u=float(np.ptp(E[f"E_{ie}_bc"][late]) / Eu),
                       E_ej_M_late_min_u=float(E[f"E_{ie}_M"][late].min() / Eu),
                       E_ej_M_late_max_u=float(E[f"E_{ie}_M"][late].max() / Eu),
                       E_cap_M_u=float(E[f"E_{ic}_M"][-1] / Eu),
                       rmin_cap=float(E[f"r_{ic}M"].min()),
                       pericentres_cap=turning(ts, E[f"r_{ic}M"])[:3])
    arr[f"{key}_newton_t"] = ts
    for i in (0, 1):
        arr[f"{key}_newton_r{i + 1}"] = E[f"r_{i}M"]
        arr[f"{key}_newton_E{i + 1}_M"] = E[f"E_{i}_M"] / Eu
        arr[f"{key}_newton_E{i + 1}_bc"] = E[f"E_{i}_bc"] / Eu
    arr[f"{key}_newton_r12"] = E["r_12"]
    hrna = lc.hrna_mod()
    y0 = np.concatenate([x[0] - x[2], v[0] - v[2], x[1] - x[2], v[1] - v[2]])
    for law, name in (("hrna", "hrna"), ("newton", "newton_fixed")):
        s, t_, y_ = lc.hrna_from_state(hrna, law, y0, m1, m2, a0, rt)
        r1 = np.linalg.norm(y_[:, 0:3], axis=1)
        r2 = np.linalg.norm(y_[:, 6:9], axis=1)
        S[name] = dict(outcome=int(s["outcome"]), plunged=int(s["plunged"]),
                       E1_u=float(s["E1_u"]), E2_u=float(s["E2_u"]),
                       rmin_1=float(r1.min()), rmin_2=float(r2.min()), t_end=float(s["t_end"]),
                       first_pericentre_1=(turning(t_, r1) or [None])[0],
                       first_pericentre_2=(turning(t_, r2) or [None])[0])
        arr[f"{key}_{name}_t"] = t_
        arr[f"{key}_{name}_r1"] = r1
        arr[f"{key}_{name}_r2"] = r2
    return S, arr


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    summ, arrs = {}, {}
    for key in CASES:
        S, A = one(key)
        summ[key] = S
        arrs.update(A)
    np.savez_compressed(os.path.join(out, "passage_curves.npz"), **arrs)
    with open(os.path.join(out, "passage_summary.json"), "w") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
