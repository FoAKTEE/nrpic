"""Initial data of a Hills run of the code in the form of the multi-puncture input.

Prints the <problem> block of nrpic_cf (coord/INTERFACES/multi_puncture.md section 2):
comp<c>_mass, _x1.._x3, _p1.._p3 (P = m v), _s1.._s3, _corr for the bodies in the order
--order (default m1, m2, M, as three_punctures/inputs), at the moment the binary's centre
of mass is at the requested distance from M on the way in; then the options of the
existing Hills inputs (corr_background, lapse, puncture_setup, puncture_radius). With
--json it also writes the state and its checks; with --predict it integrates the state
with full Newton and appends the predicted outcome as comment lines.

Examples (G = c = 1, lengths in units of the mass unit of M):
  python3 scripts/puncture_input.py --M 1 --m1 0.05 --m2 0.05 --a 3 --rp 8 \
      --phase-deg 130 --k0 4 --k-from 10            # the start of hills_q10_m8.athinput
  python3 scripts/puncture_input.py ... --r0 30 --k-from 10 --predict --json state.json

The masses are written as given: they are the bare masses of the punctures (see README,
"Initial data of the code", for what that means for the horizon and ADM masses).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from hills3 import threebody as T  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--M", type=float, required=True)
    ap.add_argument("--m1", type=float, required=True)
    ap.add_argument("--m2", type=float, required=True)
    ap.add_argument("--a", type=float, required=True, help="binary semi-major axis")
    ap.add_argument("--e-b", type=float, default=0.0)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--rp", type=float, help="pericentre of the centre-of-mass orbit")
    g.add_argument("--D", type=float, help="penetration factor r_p / r_t")
    ap.add_argument("--e-orb", type=float, default=1.0)
    ap.add_argument("--theta", type=float, default=np.pi / 2)
    ap.add_argument("--varphi", type=float, default=np.pi / 2)
    ap.add_argument("--varpi", type=float, default=0.0)
    ph = ap.add_mutually_exclusive_group(required=True)
    ph.add_argument("--phase", type=float, help="effective phase [rad] at the start of the approach")
    ph.add_argument("--phase-deg", type=float)
    r = ap.add_mutually_exclusive_group(required=True)
    r.add_argument("--r0", type=float, help="start distance of the binary's centre of mass from M")
    r.add_argument("--k0", type=float, help="start distance in units of r_t")
    ap.add_argument("--k-from", type=float, default=None,
                    help="integrate the approach from k_from r_t (default: place on the conic)")
    ap.add_argument("--order", default="m1,m2,M")
    ap.add_argument("--corr", default="approx", choices=["none", "approx"])
    ap.add_argument("--json", default=None, help="write the state and checks to this file")
    ap.add_argument("--predict", action="store_true",
                    help="integrate the state with full Newton to --t-end and report the outcome")
    ap.add_argument("--t-end", type=float, default=1500.0)
    a = ap.parse_args(argv)
    s = T.HillsSetup(M=a.M, m1=a.m1, m2=a.m2, a=a.a, e_b=a.e_b, rp=a.rp, D=a.D, e_orb=a.e_orb,
                     theta=a.theta, varphi=a.varphi, varpi=a.varpi,
                     phase=a.phase if a.phase is not None else np.radians(a.phase_deg))
    st = T.puncture_state(s, r0=a.r0, k0=a.k0, k_from=a.k_from)
    order = tuple(a.order.split(","))
    c = st["checks"]
    head = [f"# newton3 puncture_input: M = {a.M:g}, m1 = {a.m1:g}, m2 = {a.m2:g}, a = {a.a:g}, "
            f"r_p = {st['r_p']:.6g} (D = {st['r_p'] / st['r_t']:.4g}), phase = {s.phase:.6g} rad",
            f"# start: binary centre of mass at {c['cm_distance']:.10g} = {c['cm_distance'] / st['r_t']:.4g} r_t "
            f"from M ({st['mode']}); t = {st['t']:.6g} relative to the unperturbed pericentre",
            f"# binary a = {c['binary_a']:.6g}, e = {c['binary_e']:.4g}; centre-of-mass conic "
            f"r_p = {c['cm_conic_rp']:.6g}, e = {c['cm_conic_e']:.6g}; E_tot = {c['E_tot']:.6e} "
            f"({c['E_tot_units']:.4f} units); barycentric, total momentum zero; G = c = 1"]
    if a.predict:
        o = T.evolve_states(st["masses"][None], st["positions"][None], st["velocities"][None], 0.0,
                            a.t_end, rtol=1e-12)
        u = s.energy_unit
        en = o["_en"]
        oc = int(o["outcome"][0])
        line = f"# full Newton to t = {a.t_end:g} after the start: {T.OUTCOME_NAMES[oc]}"
        if oc in (T.EJECT1, T.EJECT2):
            ie = 1 if oc == T.EJECT1 else 2
            line += (f"; E_ej = {en[f'E{ie}'][0] / u:+.4f} units (= {en[f'E{ie}'][0]:+.4e}), captured "
                     f"a = {en['a_in'][0]:.4g}, e = {en['e_in'][0]:.4g}, r_p = {en['rp_in'][0]:.4g}")
        line += f"; closest approach to M {o['rMmin'][0].min():.4g}"
        head.append(line)
        st["prediction"] = dict(outcome=T.OUTCOME_NAMES[oc], t_end=a.t_end,
                                E1_units=float(en["E1"][0] / u), E2_units=float(en["E2"][0] / u),
                                captured_a=float(en["a_in"][0]), captured_e=float(en["e_in"][0]),
                                rmin=o["rMmin"][0].tolist())
    print("\n".join(head))
    print(T.multi_puncture_block(st, order=order, corr=a.corr), end="")
    if a.json:
        out = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in st.items()}
        out["order"] = list(order)
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
