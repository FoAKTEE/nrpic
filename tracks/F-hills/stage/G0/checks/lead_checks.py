#!/usr/bin/env python3
"""Lead's independent checks of the F-hills helper packages (JOURNAL, lead session, V4-V6).

Written by the F-hills lead without importing the helpers' integrators:
  v4     restricted parabolic three-body problem of 0911.1136 (prp.tex:229-259, energy
         prp.tex:350-357), SciPy's Fortran DOP853 (scipy.integrate.ode), compared with
         newton3's per-sample scan (coplanar.npz of run F-hills-20261115-130237-cbfaf6b).
  v5     full Newtonian three-body integration of the start states written in
         three_punctures/inputs/hills_q{10,4}_m8.athinput (positions, momenta, bare masses).
  v6     geodesic baseline of the same states with geodesic_binary/hrna.py (the HRNA of
         2404.16270; hole fixed), from (a) the NR coordinate state relative to M and (b) the
         2404 construction (CM on the Schwarzschild parabola of r_p, release at the NR start
         radius, binary phase taken from the NR state); plus phase scans with law = newton
         (hole fixed) and hrna.
Usage: lead_checks.py v4|v5v6 <outdir>   (figures and JSON into <outdir>)
"""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy.integrate import ode

WT = "/data/haiyangw/nrpic/wt/F-hills"
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/F-hills"

# ----------------------------------------------------------------------------------------
# V4: restricted parabolic problem
# ----------------------------------------------------------------------------------------


def rhs_restricted(t, y):
    x, yy, z, vx, vy, vz, f = y
    c, s = math.cos(f), math.sin(f)
    k = (1 + c) ** 3 / 8.0
    r3 = (x * x + yy * yy + z * z) ** 1.5
    pr = x * c + yy * s
    return [vx, vy, vz,
            k * (-x + 3 * pr * c) - x / r3,
            k * (-yy + 3 * pr * s) - yy / r3,
            -k * z - z / r3,
            math.sqrt(2.0) * (1 + c) ** 2 / 4.0]


def t_of_f(f):
    tt = math.tan(f / 2)
    return math.sqrt(2.0) / 3.0 * tt * (3 + tt * tt)


def one_restricted(args):
    D, phi, S, k0, kend, rtol = args
    # start and end radii k0 r_t and kend r_t: r_m / r_p = k / D = 2 / (1 + cos f)
    f0 = -math.acos(2.0 * D / k0 - 1.0)
    fend = math.acos(2.0 * D / kend - 1.0)
    t0, tend = t_of_f(f0), t_of_f(fend)
    w = D ** 1.5
    r0 = 1.0 / D
    ph0 = S * w * t0 + phi
    y0 = [r0 * math.cos(ph0), r0 * math.sin(ph0), 0.0,
          -S * w * r0 * math.sin(ph0), S * w * r0 * math.cos(ph0), 0.0, f0]
    sol = ode(rhs_restricted).set_integrator("dop853", rtol=rtol, atol=rtol * 1e-3,
                                             nsteps=10 ** 7)
    sol.set_initial_value(y0, t0)
    rmin = r0
    # step in chunks to record the closest approach of the two members
    ts = np.linspace(t0, tend, 400)
    for tt in ts[1:]:
        sol.integrate(tt)
        if not sol.successful():
            return dict(ok=False)
        rmin = min(rmin, math.sqrt(sol.y[0] ** 2 + sol.y[1] ** 2 + sol.y[2] ** 2))
    x, yy, z, vx, vy, vz, f = sol.y
    r = math.sqrt(x * x + yy * yy + z * z)
    eb = 0.5 * (vx * vx + vy * vy + vz * vz) - 1.0 / r
    c, s = math.cos(f), math.sin(f)
    E1 = -(1.0 / D) * ((1 + c) ** 2 / 4.0 * (x * c + yy * s) + (-s * vx + (1 + c) * vy) / math.sqrt(2.0))
    state = "disrupted"
    if eb < 0:
        af = -1.0 / (2 * eb)
        h = np.cross([x, yy, z], [vx, vy, vz])
        ecc = math.sqrt(max(0.0, 1 + 2 * eb * float(h @ h)))
        apo = af * (1 + ecc)
        rH = (kend / D) * 3.0 ** (-1.0 / 3.0)       # Hill radius at the end, same units
        state = "survived" if apo < 0.5 * rH else "ambiguous"
        return dict(ok=True, state=state, E1=0.0, af_over_a=af * D, rmin=rmin * D)
    return dict(ok=True, state=state, E1=E1, af_over_a=math.inf, rmin=rmin * D)


def v4(out):
    run = os.path.join(SCR, "F-hills-20261115-130237-cbfaf6b", "coplanar.npz")
    ref = np.load(run)
    cases = [(+1, D) for D in (0.1, 0.5, 1.0, 1.5, 2.0)] + [(-1, D) for D in (0.1, 0.2, 0.3, 0.38)]
    nph = 600
    phis = np.linspace(0.0, math.pi, nph, endpoint=False)
    res = []
    with Pool(int(os.environ.get("NPROC", "8"))) as pool:
        for S, D in cases:
            outs = pool.map(one_restricted, [(D, p, S, 10.0, 30.0, 1e-11) for p in phis])
            ok = np.array([o["ok"] for o in outs])
            st = np.array([o.get("state", "fail") for o in outs])
            E = np.array([abs(o.get("E1", 0.0)) for o in outs])
            dis = st == "disrupted"
            j = int(np.argmin(abs(ref["D"] - D)))
            key = "pro" if S > 0 else "ret"
            rd = ref["disrupted_" + key][j]
            rE = np.abs(ref["E2_" + key][j])
            row = dict(sense=key, D=D, D_ref=float(ref["D"][j]), n=nph, n_fail=int((~ok).sum()),
                       n_ambiguous=int((st == "ambiguous").sum()),
                       P_dis=float(dis.mean()), P_dis_ref=float(rd.mean()),
                       Emean_dis=float(E[dis].mean()) if dis.any() else 0.0,
                       Emean_dis_ref=float(rE[rd].mean()) if rd.any() else 0.0,
                       Emean_all=float(np.where(dis, E, 0).mean()),
                       Emean_all_ref=float(np.where(rd, rE, 0).mean()),
                       Emax=float(E[dis].max()) if dis.any() else 0.0,
                       Emax_ref=float(rE[rd].max()) if rd.any() else 0.0,
                       phi=phis.tolist(), E_signed=[o.get("E1", 0.0) for o in outs],
                       state=st.tolist())
            res.append(row)
            print(f"{key} D={D}: P_dis {row['P_dis']:.4f} ref {row['P_dis_ref']:.4f}; "
                  f"<|E|>_dis {row['Emean_dis']:.4f} ref {row['Emean_dis_ref']:.4f}; "
                  f"max {row['Emax']:.3f} ref {row['Emax_ref']:.3f}; amb {row['n_ambiguous']}",
                  flush=True)
    summary = [{k: v for k, v in r.items() if k not in ("phi", "E_signed", "state")} for r in res]
    json.dump(dict(reference_run="F-hills-20261115-130237-cbfaf6b", rows=summary),
              open(os.path.join(out, "v4_summary.json"), "w"), indent=1)
    np.savez(os.path.join(out, "v4_samples.npz"),
             **{f"{r['sense']}_{r['D']}_E": np.array(r["E_signed"]) for r in res},
             **{f"{r['sense']}_{r['D']}_state": np.array(r["state"]) for r in res}, phi=phis)
    # figure: |E| against phase for each case, mine (line) against newton3 (points)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(3, 3, figsize=(fs.FULL_WIDTH, 6.6), sharex=True)
    for ax, r in zip(axs.ravel(), res):
        key = r["sense"]
        j = int(np.argmin(abs(ref["D"] - r["D"])))
        ph_ref = ref["phase_skr"]
        Eref = np.where(ref["disrupted_" + key][j], np.abs(ref["E2_" + key][j]), np.nan)
        Em = np.where(np.array(r["state"]) == "disrupted", np.abs(r["E_signed"]), np.nan)
        # newton3 stores retrograde phases with the opposite sign convention: map phi -> pi - phi
        # is NOT applied; the comparison of phase-averaged numbers is convention-free, the
        # curves are shown in each code's own convention
        ax.plot(ph_ref / math.pi, Eref, ".", ms=1.5, color=fs.PAL["red"], label="newton3")
        ax.plot(np.array(r["phi"]) / math.pi, Em, "-", lw=1.0, color=fs.PAL["blue"], label="lead")
        ax.set_title(f"{'prograde' if key == 'pro' else 'retrograde'} D = {r['D']}", fontsize=9)
        ax.text(0.03, 0.85, f"P {r['P_dis']:.3f} / {r['P_dis_ref']:.3f}", transform=ax.transAxes,
                fontsize=8)
    for ax in axs[-1]:
        ax.set_xlabel(r"phase $\phi/\pi$")
    for ax in axs[:, 0]:
        ax.set_ylabel(r"$|E|$")
    axs[0, 0].legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_v4_restricted"))
    return res


# ----------------------------------------------------------------------------------------
# V5: full Newtonian three-body from the athinput states
# ----------------------------------------------------------------------------------------


def read_athinput(path):
    blk, d = None, {}
    for line in open(path):
        line = line.split("#")[0].strip()
        if not line:
            continue
        if line.startswith("<"):
            blk = line.strip("<>")
            continue
        if "=" in line and blk == "problem":
            k, v = [s.strip() for s in line.split("=", 1)]
            d[k] = v
    n = int(d["ncomp"])
    m = np.array([float(d[f"comp{i}_mass"]) for i in range(n)])
    x = np.array([[float(d[f"comp{i}_x{k}"]) for k in (1, 2, 3)] for i in range(n)])
    p = np.array([[float(d[f"comp{i}_p{k}"]) for k in (1, 2, 3)] for i in range(n)])
    return m, x, p


def rhs_nbody(t, y, m):
    n = m.size
    X = y[:3 * n].reshape(n, 3)
    A = np.zeros((n, 3))
    for i in range(n):
        for j in range(n):
            if i != j:
                d = X[j] - X[i]
                A[i] += m[j] * d / np.linalg.norm(d) ** 3
    return np.concatenate([y[3 * n:], A.ravel()])


def kepler_elements(dx, dv, mu):
    r = np.linalg.norm(dx)
    eps = 0.5 * dv @ dv - mu / r
    h = np.cross(dx, dv)
    h2 = h @ h
    e = math.sqrt(max(0.0, 1 + 2 * eps * h2 / mu ** 2))
    rp = h2 / (mu * (1 + e))
    return eps, e, rp


def newton_full(m, x, p, t_end=1500.0, nout=15001):
    v = p / m[:, None]
    y0 = np.concatenate([x.ravel(), v.ravel()])
    sol = ode(rhs_nbody).set_integrator("dop853", rtol=1e-12, atol=1e-14, nsteps=10 ** 8)
    sol.set_initial_value(y0, 0.0).set_f_params(m)
    ts = np.linspace(0.0, t_end, nout)
    Y = np.empty((nout, y0.size))
    Y[0] = y0
    for i, tt in enumerate(ts[1:], 1):
        sol.integrate(tt)
        Y[i] = sol.y
    return ts, Y


def energies_vs_M(Y, m, iM=2):
    """Two-body energy of each member with M: mu_i (|v_i - v_M|^2 / 2 - (M + m_i)/r)."""
    n = m.size
    X = Y[:, :3 * n].reshape(-1, n, 3)
    V = Y[:, 3 * n:].reshape(-1, n, 3)
    out = []
    for i in range(n):
        if i == iM:
            continue
        dx = X[:, i] - X[:, iM]
        dv = V[:, i] - V[:, iM]
        mu = m[i] * m[iM] / (m[i] + m[iM])
        out.append(mu * (0.5 * np.sum(dv * dv, 1) - (m[i] + m[iM]) / np.linalg.norm(dx, axis=1)))
    return out, X, V


# ----------------------------------------------------------------------------------------
# V6: HRNA from the same states
# ----------------------------------------------------------------------------------------


def hrna_mod():
    sys.path.insert(0, os.path.join(WT, "tracks/F-hills/geodesic_binary"))
    import hrna
    return hrna


def hrna_from_state(hrna, law, y0, m1, m2, a0, rt, t_max=3000.0, rec=200000):
    if hrna._WK is None:
        hrna._WK = hrna._work()
    lawc = hrna.LAW_NEWTON if law == "newton" else hrna.LAW_HRNA
    cc = hrna.COORDS_SCH
    r_plunge = 0.0 if law == "newton" else 2.5
    T0 = 2 * math.pi * math.sqrt(a0 ** 3 / (m1 + m2))
    status, t, y, diag, rec_t, rec_y, nrec, nsteps, nrej = hrna.integrate(
        lawc, cc, hrna.PAIR_GRAVITY, 1.0, 0.0, m1, m2, 0.0, 0.0, np.asarray(y0, float),
        T0 / 200.0, 1e-12, 1e-14, 30.0 * rt, 10.0 * rt, r_plunge, t_max, 20_000_000, a0, rec,
        hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, hrna._WK)
    summ = hrna.summarize(lawc, cc, 1.0, 0.0, m1, m2, a0, y, diag, T0)
    summ.update(status=int(status), t_end=float(t), nsteps=int(nsteps))
    return summ, np.array(rec_t[:nrec]), np.array(rec_y[:nrec])


def phase_scan_one(args):
    law, mb, a0, rp, phase, r0_rt = args
    hrna = hrna_mod()
    o = hrna.run_encounter(law=law, mb=mb, q12=1.0, a0=a0, rp=rp, phase=phase, sense=1,
                           r0_rt=r0_rt, rf_rt=30.0)
    # closest approach of each member to the hole is not returned by run_encounter; rerun
    # with a record would be costly: use the outcome code (6 = captured below 2.5 M)
    return dict(outcome=o["outcome"], E1=o["E1_u"], E2=o["E2_u"], plunged=o["plunged"],
                separated=o["separated"], status=o["status"])


def v5v6(out):
    hrna = hrna_mod()
    cfgs = {"q10": os.path.join(WT, "tracks/F-hills/three_punctures/inputs/hills_q10_m8.athinput"),
            "q4": os.path.join(WT, "tracks/F-hills/three_punctures/inputs/hills_q4_m8.athinput")}
    expect = {"q10": dict(rp=8.0, a=3.0), "q4": dict(rp=1.2378 * 5.0 * 4.0 ** (1 / 3), a=5.0)}
    allres = {}
    fs.use_style()
    import matplotlib.pyplot as plt
    for name, path in cfgs.items():
        m, x, p = read_athinput(path)        # order: m1, m2, M (comp0, comp1, comp2)
        M, m1, m2 = m[2], m[0], m[1]
        mb = m1 + m2
        a0 = expect[name]["a"]
        rt = a0 * (M / mb) ** (1 / 3)
        Eu = m1 * m2 / a0 * (M / mb) ** (1 / 3)
        Ptot = p.sum(0)
        xbar = (m[:, None] * x).sum(0) / m.sum()
        v = p / m[:, None]
        xcm = (m1 * x[0] + m2 * x[1]) / mb
        vcm = (m1 * v[0] + m2 * v[1]) / mb
        eps, e_orb, rp_orb = kepler_elements(xcm - x[2], vcm - v[2], M + mb)
        epsb, e_b, _ = kepler_elements(x[0] - x[1], v[0] - v[1], mb)
        a_b = -mb / (2 * epsb)
        r0 = float(np.linalg.norm(xcm - x[2]))
        # V5: full Newton
        ts, Y = newton_full(m, x, p)
        (E1, E2), X, V = energies_vs_M(Y, m)
        r1M = np.linalg.norm(X[:, 0] - X[:, 2], axis=1)
        r2M = np.linalg.norm(X[:, 1] - X[:, 2], axis=1)
        r12 = np.linalg.norm(X[:, 0] - X[:, 1], axis=1)
        res = dict(Ptot=Ptot.tolist(), barycentre=xbar.tolist(), r0=r0, r0_over_rt=r0 / rt,
                   cm_orbit=dict(e=e_orb, rp=rp_orb, eps=eps),
                   binary=dict(a=a_b, e=e_b, sep0=float(np.linalg.norm(x[0] - x[1]))),
                   newton_full=dict(E1_u=float(E1[-1] / Eu), E2_u=float(E2[-1] / Eu),
                                    rmin_1M=float(r1M.min()), rmin_2M=float(r2M.min()),
                                    t_end=float(ts[-1]), r12_end=float(r12[-1]),
                                    t_peri_cm=float(ts[np.argmin(np.linalg.norm(
                                        (m1 * X[:, 0] + m2 * X[:, 1]) / mb - X[:, 2], axis=1))])),
                   unit_E=Eu)
        # captured member's orbit (Newtonian, two-body with M at the end)
        icap = 1 if E2[-1] < 0 else 0
        dxc = X[-1, icap] - X[-1, 2]
        dvc = V[-1, icap] - V[-1, 2]
        epsc, ec, rpc = kepler_elements(dxc, dvc, M + m[icap])
        res["newton_full"]["captured"] = dict(member=icap + 1, a=float(-(M + m[icap]) / (2 * epsc)),
                                              e=ec, rp=rpc)
        # V6a: HRNA and fixed-hole Newton from the NR coordinate state relative to M
        y0 = np.concatenate([x[0] - x[2], v[0] - v[2], x[1] - x[2], v[1] - v[2]])
        res["v6a"] = {}
        recs = {}
        for law in ("newton", "hrna"):
            s, rt_, ry = hrna_from_state(hrna, law, y0, m1, m2, a0, rt)
            r1 = np.linalg.norm(ry[:, 0:3], axis=1)
            r2 = np.linalg.norm(ry[:, 6:9], axis=1)
            recs[law] = (rt_, r1, r2, np.linalg.norm(ry[:, 0:3] - ry[:, 6:9], axis=1))
            # radial turning points of the bound member (pericentres)
            rb = r2 if s["E2_u"] < s["E1_u"] else r1
            peri = [float(rb[i]) for i in range(1, rb.size - 1) if rb[i] < rb[i - 1] and rb[i] <= rb[i + 1]]
            tperi = [float(rt_[i]) for i in range(1, rb.size - 1) if rb[i] < rb[i - 1] and rb[i] <= rb[i + 1]]
            res["v6a"][law] = dict(outcome=s["outcome"], E1_u=s["E1_u"], E2_u=s["E2_u"],
                                   plunged=s["plunged"], separated=s["separated"],
                                   status=s["status"], t_end=s["t_end"],
                                   rmin_1=float(r1.min()), rmin_2=float(r2.min()),
                                   bound_member_pericentres=peri[:6],
                                   bound_member_peri_times=tperi[:6])
        # V6b: 2404 construction with the NR start radius and the NR binary orientation
        ang_cm = math.atan2(*(xcm - x[2])[1::-1])
        d12 = x[0] - x[1]
        phase_nr = (math.atan2(d12[1], d12[0]) - ang_cm) % (2 * math.pi)
        rp_target = expect[name]["rp"]
        res["v6b"] = {}
        for law in ("newton", "hrna"):
            o = hrna.run_encounter(law=law, mb=mb, q12=m2 / m1, a0=a0, rp=rp_target, phase=phase_nr,
                                   sense=1, r0_rt=r0 / rt, rf_rt=30.0)
            res["v6b"][law] = dict(outcome=o["outcome"], E1_u=o["E1_u"], E2_u=o["E2_u"],
                                   plunged=o["plunged"], separated=o["separated"],
                                   status=o["status"], phase=phase_nr)
        # phase scans (2404 convention), 180 phases, release at the NR start radius
        phases = np.linspace(0, 2 * math.pi, 180, endpoint=False)
        scan = {}
        with Pool(int(os.environ.get("NPROC", "8"))) as pool:
            for law in ("newton", "hrna"):
                o = pool.map(phase_scan_one, [(law, mb, a0, rp_target, ph, r0 / rt) for ph in phases])
                oc = np.array([q["outcome"] for q in o])
                scan[law] = dict(separated=float(np.mean([q["separated"] for q in o])),
                                 captured_by_hole=float(np.mean(oc == 6)),
                                 single_ejection=float(np.mean((oc == 1) | (oc == 2))),
                                 survived=float(np.mean(oc == 0)),
                                 E_ej_mean=float(np.nanmean([max(q["E1"], q["E2"]) for q in o
                                                             if q["outcome"] in (1, 2)])),
                                 outcomes=oc.tolist(),
                                 Emax=[float(max(q["E1"], q["E2"])) for q in o])
        res["scan"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("outcomes", "Emax")}
                       for k, v in scan.items()}
        res["scan_phase_nr"] = phase_nr
        allres[name] = res
        print(name, json.dumps({k: v for k, v in res.items() if k != "scan"}, indent=1), flush=True)
        print(name, "scan", json.dumps(res["scan"]), flush=True)
        # figure: radii of the members from M against time, three models; phase scan outcomes
        fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
        ax = axs[0]
        ax.plot(ts, r1M, color=fs.PAL["blue"], lw=1.2, label=r"$m_1$ Newton, full")
        ax.plot(ts, r2M, color=fs.PAL["red"], lw=1.2, label=r"$m_2$ Newton, full")
        for law, ls in (("newton", ":"), ("hrna", "--")):
            t_, a1, a2, _ = recs[law]
            ax.plot(t_, a1, ls=ls, color=fs.PAL["blue"], lw=1.0, label=f"$m_1$ {law} (hole fixed)")
            ax.plot(t_, a2, ls=ls, color=fs.PAL["red"], lw=1.0, label=f"$m_2$ {law} (hole fixed)")
        ax.axhline(4.0, **fs.MASK_LINE)
        ax.axhline(2.5, **fs.MASK_LINE)
        ax.set_yscale("log")
        ax.set_xlim(0, 600)
        ax.set_ylim(1.5, 300)
        ax.set_xlabel(r"$t\,[M]$")
        ax.set_ylabel(r"distance from the heavy hole $[M]$")
        ax.legend(frameon=False, fontsize=6.5, loc="upper left", ncol=2)
        ax.set_title(f"{name}: start state of the input file", fontsize=9)
        ax = axs[1]
        for law, col in (("newton", fs.PAL["blue"]), ("hrna", fs.PAL["red"])):
            oc = np.array(scan[law]["outcomes"])
            ax.plot(phases / math.pi, np.where((oc == 1) | (oc == 2), scan[law]["Emax"], np.nan),
                    ".", ms=3, color=col, label=f"{law}: ejected member $E$")
            ax.plot(phases[oc == 6] / math.pi, np.full((oc == 6).sum(), -0.5 if law == "newton" else -0.8),
                    "|", color=col, ms=6, label=f"{law}: member below 2.5 M")
        ax.axvline(phase_nr / math.pi, **fs.MASK_LINE)
        ax.set_xlabel(r"release phase (2404 convention) $/\pi$")
        ax.set_ylabel(r"$E$ [units $(m_1m_2/a)(M/m)^{1/3}$]")
        ax.legend(frameon=False, fontsize=6.5, loc="upper right")
        ax.set_title(f"{name}: phase scan, $r_p$ = {rp_target:.2f}, hole fixed", fontsize=9)
        fig.tight_layout()
        fs.save(fig, os.path.join(out, f"fig_v5v6_{name}"))
    json.dump(allres, open(os.path.join(out, "v5v6_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    what, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    {"v4": v4, "v5v6": v5v6}[what](outdir)
