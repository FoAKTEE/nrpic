#!/usr/bin/env python3
"""Generate reference trajectories for the Kerr geodesic tests of arXiv:2611.12831 (Sec. Kerr geodesics).

Writes problems/kerr/ref/<orbit>_<system>.npz and problems/kerr/ref/initial_conditions.json.

Method (see README.md):
  * "Exact" states come from nrpic.kerr.MinoOrbit: the geodesic written in Mino time with the
    first integrals E, L_z, Q, solved by mpmath quadrature at 30 digits and rounded to double.
  * The stored trajectory is DOP853 (rtol = atol = 2.5e-14, max step 0.1 M) on the 3+1 equations of
    motion, restarted from the exact state every ANCHOR_DT = 10 M, sampled at t_i = fl(i/100).  The free-running
    DOP853 solution (no restarts) is computed too and its deviation is reported.
  * The final state at t_end in the npz/JSON is the exact (quadrature) one.

Usage:  python3 problems/kerr/make_reference.py [--workers 4] [--anchor-dt 10] [--quick]
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import mpmath as mp
import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "python"))

from nrpic import geodesic, kerr  # noqa: E402

A = 0.9
M = 1.0
DT_OUT = 0.01
DPS = 30
RTOL = ATOL = 2.5e-14
MAX_STEP = 0.1  # caps the DOP853 step so the dense-output samples are as accurate as the steps
SAMPLES_PER_M = 100  # 1 / DT_OUT

ORBITS = {
    "bl_equatorial_eccentric": dict(
        system="bl", out_systems=["bl"], n_periods=20,
        x0=[6.0, np.pi / 2, 0.0], u0=[0.0, 0.0, 3.144275],
        description="BL equatorial-eccentric orbit; paper: 6.00 <= r <= 11.61, 20 radial periods"),
    "bl_inclined": dict(
        system="bl", out_systems=["bl"], n_periods=18,
        x0=[8.0, np.pi / 2 - 0.35, 0.0], u0=[0.0, 0.9, 2.9],
        description="BL inclined orbit; paper: samples both hemispheres, 18 periods shown"),
    "ks_passage": dict(
        system="ks", out_systems=["ks", "cks"], t_end=230.0,
        x0=[20.0, np.pi / 2, 0.0], u0=[-0.20131797516752664, 1.4049911031746785, 2.4328],
        description="Kerr-Schild e = 0.99 off-equatorial passage; paper: E = 0.99738, "
                    "L_z = 2.4328, Q = 1.974, r_p ~ 1.8983, integrated to t = 230 M (KS time)"),
}


def f2(v):
    return float(v)


# ----------------------------------------------------------------------------------------------
# worker: exact states from the Mino-time quadrature solution
# ----------------------------------------------------------------------------------------------

def _exact_worker(args):
    """args = (orbit_name, list of times in the natural system, systems) ->
    list of (t, {sys: (t_sys, x[3], u[3])}) as floats."""
    name, times, systems = args
    spec = ORBITS[name]
    orb = kerr.MinoOrbit.from_state(spec["system"], 0.0, spec["x0"], spec["u0"], A, M, DPS)
    out = []
    lam = None
    for t in times:
        st, lam = orb.states_at_time(t, spec["system"], systems, guess=lam)
        out.append((t, {s: (f2(v[0]), [f2(c) for c in v[1]], [f2(c) for c in v[2]])
                        for s, v in st.items()}))
    return "exact", name, out


def _peri_worker(args):
    """Exact pericenter times (natural system) up to t_end."""
    name, t_end = args
    spec = ORBITS[name]
    orb = kerr.MinoOrbit.from_state(spec["system"], 0.0, spec["x0"], spec["u0"], A, M, DPS)
    per = orb.periods()
    with mp.workdps(DPS):
        lam_max = 2 * mp.mpf(t_end) / per["Gamma"] + 2 * per["Lambda_r"]
        lams = orb.pericenter_lambdas(lam_max)
        res = []
        for lam in lams:
            tt = orb.time_at_lambda(lam, spec["system"])
            if tt > t_end:
                break
            res.append(dict(t=f2(tt), t_bl=f2(orb.time_at_lambda(lam, "bl")),
                            t_ks=f2(orb.time_at_lambda(lam, "ks")), lam=f2(lam)))
    return "peri", name, res


def _chunks(seq, k):
    return [seq[i:i + k] for i in range(0, len(seq), k)]


# ----------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------

def orbit_setup(name):
    spec = ORBITS[name]
    sysn = spec["system"]
    x0, u0 = spec["x0"], spec["u0"]
    # invariants and initial states in all systems (mpmath, correctly rounded)
    init = {}
    with mp.workdps(DPS):
        for s in kerr.SYSTEMS:
            tt, xx, uu, E = kerr.convert_state_mp(0.0, x0, u0, sysn, s, A, M, DPS)
            init[s] = dict(t0=f2(tt), x=[f2(c) for c in xx], u=[f2(c) for c in uu], u_t=f2(-E))
        orb = kerr.MinoOrbit.from_state(sysn, 0.0, x0, u0, A, M, DPS)
        inv = dict(E=f2(orb.E), Lz=f2(orb.L), Q=f2(orb.Q))
        per = {k: f2(v) for k, v in orb.periods().items()}
        tp = dict(r_apo=f2(orb.r1), r_peri=f2(orb.r2), r3=f2(orb.r3), r4=f2(orb.r4),
                  e=f2(orb.e), p=f2(orb.p),
                  theta_min=f2(mp.acos(mp.sqrt(orb.zm))), theta_max=f2(mp.pi - mp.acos(mp.sqrt(orb.zm))),
                  chi_r0=f2(orb.chi_r0), chi_theta0=f2(orb.chi_th0))
    if tp["theta_min"] > np.pi / 2 - 1e-12:
        per["T_th"] = per["Lambda_th"] = per["Omega_th"] = None
    if "t_end" in spec:
        t_end = float(spec["t_end"])
    else:
        t_end = float(np.ceil(spec["n_periods"] * per["T_r"] / 10.0) * 10.0)
    return dict(init=init, inv=inv, periods=per, turning=tp, t_end=t_end)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--anchor-dt", type=float, default=10.0)
    ap.add_argument("--n-random", type=int, default=20, help="random exact checks per orbit")
    ap.add_argument("--orbits", nargs="*", default=list(ORBITS))
    ap.add_argument("--outdir", default=str(HERE / "ref"))
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    T0 = time.time()
    rng = np.random.default_rng(20261113)

    setups = {}
    for name in args.orbits:
        setups[name] = orbit_setup(name)
        s = setups[name]
        print(f"[{name}] E={s['inv']['E']!r} Lz={s['inv']['Lz']!r} Q={s['inv']['Q']!r} "
              f"r in [{s['turning']['r_peri']:.10f}, {s['turning']['r_apo']:.10f}] "
              f"T_r={s['periods']['T_r']:.10f} t_end={s['t_end']}", flush=True)

    # time grids, anchor and random check times
    grids, anchors, randoms = {}, {}, {}
    na = int(round(args.anchor_dt * SAMPLES_PER_M))
    for name in args.orbits:
        t_end = setups[name]["t_end"]
        n = int(round(t_end * SAMPLES_PER_M))
        assert abs(n / SAMPLES_PER_M - t_end) < 1e-12 and n % na == 0
        t = np.arange(n + 1) / SAMPLES_PER_M
        grids[name] = t
        anchors[name] = list(range(0, n + 1, na))
        cand = np.setdiff1d(np.arange(1, n), np.array(anchors[name]))
        randoms[name] = sorted(rng.choice(cand, size=args.n_random, replace=False).tolist())

    # exact states (parallel)
    tasks = []
    for name in args.orbits:
        systems = ORBITS[name]["out_systems"]
        idx = anchors[name] + randoms[name]
        idx = sorted(idx)
        for ch in _chunks(idx, 25):
            tasks.append((name, [float(grids[name][i]) for i in ch], systems))
    exact = {name: {} for name in args.orbits}
    peris = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(_exact_worker, tk) for tk in tasks]
        futs += [ex.submit(_peri_worker, (name, setups[name]["t_end"])) for name in args.orbits]
        for f in futs:
            kind, name, lst = f.result()
            if kind == "exact":
                for t, st in lst:
                    exact[name][t] = st
            else:
                peris[name] = lst
    print(f"exact states done ({time.time() - T0:.0f} s)", flush=True)

    meta_orbits = {}
    for name in args.orbits:
        spec = ORBITS[name]
        su = setups[name]
        t = grids[name]
        t_end = su["t_end"]
        inv_ref = (su["inv"]["E"], su["inv"]["Lz"], su["inv"]["Q"])
        orbit_meta = dict(description=spec["description"], natural_system=spec["system"],
                          initial_state=su["init"], invariants=su["inv"], turning_points=su["turning"],
                          periods=su["periods"], t_end=t_end, dt_out=DT_OUT,
                          n_radial_periods=t_end / su["periods"]["T_r"], files={},
                          final_state={}, accuracy={}, events={})
        orbit_meta["events"]["pericenter_exact"] = peris.get(name, [])
        for s in spec["out_systems"]:
            x0 = su["init"][s]["x"]
            u0 = su["init"][s]["u"]
            acc = {}
            # ---- anchored reference
            X = np.empty((len(t), 3))
            U = np.empty((len(t), 3))
            jumps = []
            nfev = 0
            for k in range(len(anchors[name]) - 1):
                i0, i1 = anchors[name][k], anchors[name][k + 1]
                _, xa, ua = exact[name][float(t[i0])][s]
                tr = geodesic.integrate(s, xa, ua, float(t[i1]), t0=float(t[i0]), t_eval=t[i0:i1 + 1],
                                        rtol=RTOL, atol=ATOL, a=A, M=M, max_step=MAX_STEP)
                nfev += tr.nfev
                X[i0:i1] = tr.x[:-1]
                U[i0:i1] = tr.u[:-1]
                _, xb, ub = exact[name][float(t[i1])][s]
                jumps.append(max(np.max(np.abs(tr.x_end - xb)), np.max(np.abs(tr.u_end - ub))))
            _, xe, ue = exact[name][float(t[-1])][s]
            X[-1], U[-1] = xe, ue
            acc["anchor_dt"] = args.anchor_dt
            acc["max_segment_end_error"] = float(max(jumps))
            # ---- random exact checks of the stored samples (dense output inside segments)
            rerr = []
            for i in randoms[name]:
                _, xr, ur = exact[name][float(t[i])][s]
                rerr.append(max(np.max(np.abs(X[i] - xr)), np.max(np.abs(U[i] - ur))))
            acc["max_error_at_random_exact_checks"] = float(max(rerr))
            acc["n_random_exact_checks"] = len(rerr)
            # ---- free-running integrations (tolerance study), error at t_end vs exact
            tol_study = {}
            free = None
            for rt in (1e-12, 1e-13, RTOL):
                tf = geodesic.integrate(s, x0, u0, t_end, t_eval=t, rtol=rt, atol=rt, a=A, M=M,
                                        turning_points=(rt == RTOL))
                err_end = max(np.max(np.abs(tf.x_end - xe)), np.max(np.abs(tf.u_end - ue)))
                tol_study[f"{rt:.1e}"] = dict(err_end_maxabs=float(err_end), nfev=int(tf.nfev),
                                              x_end=tf.x_end.tolist(), u_end=tf.u_end.tolist())
                if rt == RTOL:
                    free = tf
            acc["free_running_tolerance_study"] = tol_study
            dfree = np.maximum(np.max(np.abs(free.x - X), axis=1), np.max(np.abs(free.u - U), axis=1))
            acc["free_running_max_deviation_from_reference"] = float(dfree.max())
            # ---- invariants along the stored reference, relative to the exact invariants
            ih = geodesic.invariant_history(s, X, U, A, M, ref=inv_ref)
            acc["invariants_max_abs_error"] = dict(
                E=ih["max_abs_dE"], Lz=ih["max_abs_dLz"], Q=ih["max_abs_dQ"],
                Q_is_relative=bool(ih["dQ_relative"]))
            ihf = geodesic.invariant_history(s, free.x, free.u, A, M, ref=inv_ref)
            acc["free_running_invariants_max_abs_error"] = dict(
                E=ihf["max_abs_dE"], Lz=ihf["max_abs_dLz"], Q=ihf["max_abs_dQ"])
            orbit_meta["accuracy"][s] = acc
            # ---- events from the free-running integration in this system's time
            ev = {k: v[0].tolist() for k, v in free.events.items()}
            evr = {k: [float(kerr.cks_radius(y[:3], A)) if s == "cks" else float(y[0]) for y in v[1]]
                   for k, v in free.events.items()}
            orbit_meta["events"][s] = dict(peri_t=ev["peri"], peri_r=evr["peri"], apo_t=ev["apo"],
                                           apo_r=evr["apo"], theta_turn_t=ev["theta_turn"])
            # ---- radial range along the stored samples
            r_s = kerr.cks_radius(X, A) if s == "cks" else X[:, 0]
            orbit_meta.setdefault("sampled_r_range", {})[s] = [float(r_s.min()), float(r_s.max())]
            # ---- write npz
            fn = f"{name}_{s}.npz"
            np.savez(outdir / fn, t=t, x=X, u=U, t_end=np.float64(t_end), x_end=np.array(xe),
                     u_end=np.array(ue), x_end_free_dop853=free.x_end, u_end_free_dop853=free.u_end,
                     system=np.array(s), a=np.float64(A), M=np.float64(M),
                     E=np.float64(inv_ref[0]), Lz=np.float64(inv_ref[1]), Q=np.float64(inv_ref[2]),
                     t_anchor=t[anchors[name]],
                     x_anchor=np.array([exact[name][float(t[i])][s][1] for i in anchors[name]]),
                     u_anchor=np.array([exact[name][float(t[i])][s][2] for i in anchors[name]]))
            orbit_meta["files"][s] = f"ref/{fn}"
            orbit_meta["final_state"][s] = dict(t=t_end, x=list(xe), u=list(ue))
            print(f"[{name}/{s}] segment-end err {acc['max_segment_end_error']:.2e}, random-check err "
                  f"{acc['max_error_at_random_exact_checks']:.2e}, free-run dev {dfree.max():.2e}, "
                  f"tol study {[(k, '%.1e' % v['err_end_maxabs']) for k, v in tol_study.items()]}, "
                  f"inv {acc['invariants_max_abs_error']}", flush=True)
        # final state in all systems (exact) for convenience
        orb = kerr.MinoOrbit.from_state(spec["system"], 0.0, spec["x0"], spec["u0"], A, M, DPS)
        st, _ = orb.states_at_time(t_end, spec["system"], kerr.SYSTEMS)
        orbit_meta["final_state_all_systems"] = {
            s: dict(t=f2(v[0]), x=[f2(c) for c in v[1]], u=[f2(c) for c in v[2]]) for s, v in st.items()}
        meta_orbits[name] = orbit_meta

    meta = dict(
        description="Kerr (a = 0.9 M) timelike geodesic references for the NRPIC pusher tests "
                    "(arXiv:2611.12831, Sec. Kerr geodesics).  See problems/kerr/README.md.",
        generator="problems/kerr/make_reference.py",
        versions=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                      mpmath=mp.__version__),
        a=A, M=M, dt_out=DT_OUT, sample_times="t_i = fl(i / 100), i = 0..N, t_N = t_end",
        integrator=dict(method="DOP853", rtol=RTOL, atol=ATOL, max_step=MAX_STEP, anchor_dt=args.anchor_dt,
                        exact_solution="Mino-time quadrature (nrpic.kerr.MinoOrbit), mpmath dps = %d" % DPS),
        conventions=dict(
            state="x^i and covariant u_i (per unit mass); u_t = -E is the same number in all systems",
            bl="(t, r, theta, phi) Boyer-Lindquist",
            ks="(t, r, theta, phi) spherical Kerr-Schild, l = dt + dr - a sin^2 dphi",
            cks="(t, x, y, z), x + i y = (r + i a) e^{i phi_KS} sin theta, z = r cos theta",
            bl_to_ks="t_KS = t_BL + delta_t(r), phi_KS = phi_BL + delta_phi(r), "
                     "u_r^KS = u_r^BL + (2 M r E - a L_z)/Delta",
            delta_t="2M/(r+ - r-) [r+ ln((r - r+)/M) - r- ln((r - r-)/M)]",
            delta_phi="a/(r+ - r-) ln((r - r+)/(r - r-))",
            t0="initial_state[sys].t0 is the coordinate time of the initial event in that system "
               "(0 in the natural system); time translation and phi rotation are symmetries, so a "
               "run may start at t = 0 and add t0 when comparing"),
        orbits=meta_orbits,
        runtime_s=time.time() - T0,
    )
    with open(outdir / "initial_conditions.json", "w") as fh:
        json.dump(meta, fh, indent=1)
    print(f"done in {time.time() - T0:.0f} s -> {outdir}")


if __name__ == "__main__":
    main()
