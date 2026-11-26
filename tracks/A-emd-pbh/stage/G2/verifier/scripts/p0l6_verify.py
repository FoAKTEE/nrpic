#!/usr/bin/env python3
"""Fresh verifier of gate G2 (Track A), item V3: the periodic chain P0L6 against the exact LTB shells, and the
horizon finder's status file, with readers of my own.

- trajectories (nrpic_io.cpp 955-975): <base>.traj.bin records of 8 doubles (time, tag, x^i, u_i) and
  <base>.trajmet.bin records of 17 doubles (time, tag, alpha, beta^i, gamma_xx..zz, proper time, E, S_i).
- areal radius of the round coordinate sphere through a particle: R = r sqrt(g_T), g_T = (tr gamma - n.gamma.n)/2.
- exact shell (my own cycloid): from (M, E, age at the initial slice) of reference B (ltb_reference.npz of run
  A-20261121-130103-e007f42; checked here at tau = 0 against the code's own R and dR/dtau):
  E < 0: R = M/(-2E) (1 - cos eta), t = M (-2E)^(-3/2) (eta - sin eta), t = age + tau; E > 0 hyperbolic.
- finder: <base>.horizon_status_0.txt columns (header of the file): cycle, time, found, reason, ..., area,
  area_mass, ...; a surface found at time t is compared with the trapped shells on that slice (R_code < 2 M and
  the shell's own tau past its exact trapping time).

    python -I p0l6_verify.py --run DIR --ref REFDIR --out DIR [--r0cut 1.5]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def cycloid_R(M, E, t):
    """R(t) of a dust shell with simultaneous-bang time 0 (t since the bang), vectorized in t."""
    t = np.asarray(t, float)
    if abs(E) < 1e-14:
        return (4.5 * M * t ** 2) ** (1 / 3)
    if E < 0:
        A = M / (-2 * E)
        B = M / (-2 * E) ** 1.5
        x = t / B
        lo, hi = np.zeros_like(x), np.full_like(x, 2 * math.pi)
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            f = mid - np.sin(mid) - x
            lo = np.where(f < 0, mid, lo)
            hi = np.where(f < 0, hi, mid)
        e = 0.5 * (lo + hi)
        R = A * (1 - np.cos(e))
        R = np.where(x >= 2 * math.pi, 0.0, R)
        return R
    A = M / (2 * E)
    B = M / (2 * E) ** 1.5
    x = t / B
    lo, hi = np.zeros_like(x), np.full_like(x, 50.0)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        f = np.sinh(mid) - mid - x
        lo = np.where(f < 0, mid, lo)
        hi = np.where(f < 0, hi, mid)
    e = 0.5 * (lo + hi)
    return A * (np.cosh(e) - 1)


def tau_trap(M, E, age):
    """Proper time after the initial slice at which R = 2M (collapsing branch for E < 0); None if never."""
    if E >= 0:
        return None
    A = M / (-2 * E)
    B = M / (-2 * E) ** 1.5
    c = 1 - 2 * M / A            # cos eta at R = 2M: 1 - cos eta = 2M/A = -4E
    if c < -1:
        return None
    e = 2 * math.pi - math.acos(c)
    return B * (e - math.sin(e)) - age


def test_cycloid():
    """Parametric cycloid against the solver, the turnaround radius M/(-E), the EdS limit, an unbound shell."""
    M, E = 1.0, -0.05
    A, B = M / (-2 * E), M / (-2 * E) ** 1.5
    e = np.linspace(0.01, 2 * math.pi - 0.01, 500)
    dev_b = float(np.max(np.abs(cycloid_R(M, E, B * (e - np.sin(e))) - A * (1 - np.cos(e)))) / A)
    E2 = 0.05
    A2, B2 = M / (2 * E2), M / (2 * E2) ** 1.5
    e2 = np.linspace(0.01, 5, 300)
    dev_u = float(np.max(np.abs(cycloid_R(M, E2, B2 * (np.sinh(e2) - e2)) - A2 * (np.cosh(e2) - 1))) / A2)
    eds = float(cycloid_R(1.0, 0.0, np.array([1.0]))[0])
    tah = tau_trap(M, E, 0.0)
    R_at = float(cycloid_R(M, E, np.array([tah]))[0])
    ok = dev_b < 1e-10 and dev_u < 1e-10 and abs(eds - 4.5 ** (1 / 3)) < 1e-12 and abs(R_at - 2 * M) < 1e-8
    return dict(dev_bound=dev_b, dev_unbound=dev_u, eds=eds, R_at_tau_ah=R_at, passed=bool(ok))


def read_traj(run):
    a = np.fromfile(os.path.join(run, "peak.traj.bin"), "<f8").reshape(-1, 8)
    b = np.fromfile(os.path.join(run, "peak.trajmet.bin"), "<f8").reshape(-1, 17)
    assert len(a) == len(b) and np.allclose(a[:, :2], b[:, :2])
    return a, b


def areal(a, b):
    x = a[:, 2:5]
    r = np.linalg.norm(x, axis=1)
    n = x / np.where(r > 0, r, 1)[:, None]
    g = b[:, 6:12]                      # xx xy xz yy yz zz
    G = np.empty((len(g), 3, 3))
    G[:, 0, 0], G[:, 0, 1], G[:, 0, 2], G[:, 1, 1], G[:, 1, 2], G[:, 2, 2] = g.T
    G[:, 1, 0], G[:, 2, 0], G[:, 2, 1] = G[:, 0, 1], G[:, 0, 2], G[:, 1, 2]
    tr = np.trace(G, axis1=1, axis2=2)
    nGn = np.einsum("pi,pij,pj->p", n, G, n)
    return r * np.sqrt(0.5 * (tr - nGn)), r


def read_status(path):
    rows = []
    with open(path) as f:
        for ln in f:
            if ln.startswith("#") or not ln.strip():
                continue
            v = ln.split()
            rows.append(dict(cycle=int(v[0]), t=float(v[1]), found=int(v[2]), reason=int(v[3]), area=float(v[5]),
                             mass=float(v[6]), meanr=float(v[7])))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--r0cut", type=float, default=1.5)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = dict(test=test_cycloid())
    print("cycloid test", res["test"], flush=True)
    z = np.load(os.path.join(a.ref, "ltb_reference.npz"))
    tagB, r0B, MB, EB, ageB = z["tagB"].astype(int), z["r0B"], z["MB"], z["EB"], z["ageB"]
    A, B = read_traj(a.run)
    R, r = areal(A, B)
    tag = A[:, 1].astype(int)
    t = A[:, 0]
    tau = B[:, 12]
    shells = {}
    for k, tg in enumerate(tagB):
        m = tag == tg
        if not np.any(m):
            continue
        tt, RR, ta = t[m], R[m], tau[m]
        o = np.argsort(tt)
        tt, RR, ta = tt[o], RR[o], ta[o]
        M, E, age = float(MB[k]), float(EB[k]), float(ageB[k])
        Rex = cycloid_R(M, E, age + ta)
        tah = tau_trap(M, E, age)
        # tau = 0 check: R and dR/dtau of the code against the shell
        R0 = float(RR[0])
        i2 = min(len(RR) - 1, 3)
        dR0 = float((RR[i2] - RR[0]) / (ta[i2] - ta[0])) if ta[i2] > ta[0] else float("nan")
        dRex = math.copysign(math.sqrt(max(2 * M / Rex[0] + 2 * E, 0)), 1.0)
        before = np.isfinite(RR) & (Rex > 0)
        if tah is not None:
            before &= ta < tah
        imax = int(np.nanargmax(RR))
        after = np.arange(len(RR)) >= imax
        trc = np.nonzero(after & (RR <= 2 * M))[0]
        t_trap_code = float(tt[trc[0]]) if len(trc) and imax < len(RR) - 1 else None
        eps = RR / Rex - 1
        # exact turnaround of the shell (E < 0): eta = pi
        tau_ta = (M / (-2 * E) ** 1.5 * math.pi - age) if E < 0 else None
        to_ta = before & ((ta <= tau_ta) if tau_ta is not None else True)
        shells[int(tg)] = dict(r0=float(r0B[k]), M=M, E=E, age=age, tau_ah=tah, R0_code=R0, R0_exact=float(Rex[0]),
                               dR0_code=dR0, dR0_exact=dRex,
                               eps_max=float(np.nanmax(np.abs(eps[before]))) if np.any(before) else None,
                               tau_last=float(ta[-1]), t_last=float(tt[-1]),
                               t_turn_code=float(tt[imax]), t_trapped_code=t_trap_code, tau_ta=tau_ta,
                               eps_max_to_ta=float(np.nanmax(np.abs(eps[to_ta]))) if np.any(to_ta) else None,
                               r_last=float(np.linalg.norm(A[m][o][-1, 2:5])),
                               eps_at_end_or_trap=float(eps[before][-1]) if np.any(before) else None)
    res["shells"] = shells
    res["eps_by_shell"] = sorted([(s["r0"], s["eps_max"], s["eps_max_to_ta"], s["tau_ta"], s["tau_ah"], s["tau_last"])
                                  for s in shells.values() if s["eps_max"] is not None])
    outer = [s for s in shells.values() if s["r0"] > a.r0cut and s["eps_max"] is not None]
    inner = [s for s in shells.values() if s["r0"] <= a.r0cut and s["eps_max"] is not None]
    res["summary"] = dict(
        n_outer=len(outer), n_inner=len(inner),
        outer_eps_max=max(s["eps_max"] for s in outer), outer_eps_median=float(np.median([s["eps_max"] for s in outer])),
        outer_eps_min=min(s["eps_max"] for s in outer),
        inner_eps_max=max(s["eps_max"] for s in inner) if inner else None,
        outer_eps_to_ta_max=max(s["eps_max_to_ta"] for s in outer if s["eps_max_to_ta"] is not None),
        outer_turned_eps_max=max((s["eps_max"] for s in outer if s["tau_ta"] is not None and s["tau_last"] > s["tau_ta"]),
                                 default=None),
        n_outer_turned=sum(1 for s in outer if s["tau_ta"] is not None and s["tau_last"] > s["tau_ta"]),
        t_first_code_trapped=min((s["t_trapped_code"] for s in shells.values() if s["t_trapped_code"] is not None),
                                 default=None),
        R0_rel_dev_max=max(abs(s["R0_code"] / s["R0_exact"] - 1) for s in shells.values()),
        dR0_rel_dev_max=max(abs(s["dR0_code"] / s["dR0_exact"] - 1) for s in shells.values() if s["dR0_exact"] > 0))
    print("summary", res["summary"], flush=True)
    # finder
    st = read_status(os.path.join(a.run, "peak.horizon_status_0.txt"))
    found = [s for s in st if s["found"] == 1]
    runs = []
    for srow in st:
        key = (srow["found"], srow["reason"])
        if runs and runs[-1]["key"] == key:
            runs[-1]["t1"] = srow["t"]
            runs[-1]["n"] += 1
        else:
            runs.append(dict(key=key, t0=srow["t"], t1=srow["t"], n=1))
    res["finder"] = dict(searches=len(st), found=len(found), t_first=st[0]["t"] if st else None,
                         t_last=st[-1]["t"] if st else None, found_rows=found[:20],
                         timeline=[dict(found=r["key"][0], reason=r["key"][1], t0=r["t0"], t1=r["t1"], n=r["n"])
                                   for r in runs])
    # trapped shells on the slice of each found surface and at the searches after 136
    ut = np.unique(t)

    def trapped_at(tq):
        i = int(np.argmin(np.abs(ut - tq)))
        tt = ut[i]
        m = t == tt
        out = []
        for tg in np.unique(tag[m]):
            if int(tg) not in shells:
                continue
            s = shells[int(tg)]
            mm = m & (tag == tg)
            RR = float(R[mm][0])
            out.append(dict(tag=int(tg), R=RR, M=s["M"], r=float(r[mm][0]), R_over_2M=RR / (2 * s["M"]), tau=float(tau[mm][0]),
                            past_tau_ah=bool(s["tau_ah"] is not None and float(tau[mm][0]) >= s["tau_ah"])))
        tr = [o for o in out if shells[o["tag"]]["t_trapped_code"] is not None and tt >= shells[o["tag"]]["t_trapped_code"]]
        return dict(t_record=float(tt), n_tracked=len(out), n_trapped_code=len(tr),
                    n_past_exact=int(sum(o["past_tau_ah"] for o in out)),
                    min_R_over_2M=min(o["R_over_2M"] for o in out) if out else None,
                    max_M_trapped=max((o["M"] for o in tr), default=None),
                    max_R_trapped=max((o["R"] for o in tr), default=None),
                    max_r_trapped=max((o["r"] for o in tr), default=None))
    res["finder"]["at_found"] = [dict(t=f["t"], area_mass=f["mass"], R_area=math.sqrt(f["area"] / (4 * math.pi)),
                                      shells=trapped_at(f["t"])) for f in found]
    late = [s for s in st if s["t"] >= 136.0]
    res["finder"]["after_136"] = dict(n=len(late), found=sum(s["found"] for s in late),
                                      reasons=sorted(set(s["reason"] for s in late)),
                                      shells_at_136=trapped_at(136.0), shells_at_end=trapped_at(float(ut[-1])))
    print(json.dumps(res["finder"]["at_found"], indent=1)[:3000])
    print(json.dumps(res["finder"]["after_136"], indent=1))
    print(json.dumps(res["finder"]["timeline"]))
    # figure: eps against tau for outer and inner shells; finder rows
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    ax = fs.inch_axes(fig, 0.6, 0.45, 3.4, 2.35)
    bx = fs.inch_axes(fig, 4.6, 0.45, 3.25, 2.35)
    tH = 9.797958971132712
    for k, tg in enumerate(tagB[::6]):
        if int(tg) not in shells:
            continue
        s = shells[int(tg)]
        m = tag == tg
        o = np.argsort(t[m])
        ta = tau[m][o]
        RR = R[m][o]
        Rex = cycloid_R(s["M"], s["E"], s["age"] + ta)
        ok = (RR > 2 * s["M"]) & (Rex > 0)
        c = fs.PAL["blue"] if s["r0"] > a.r0cut else fs.PAL["red"]
        ax.plot((ta[ok] + 2 / 3) / tH, (RR[ok] / Rex[ok] - 1) * 100, color=c, lw=0.6, alpha=0.8)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_ylim(-10, 10)
    ax.set_xlabel(r"$(\tau + t_i)/t_H$ along each shell")
    ax.set_ylabel(r"$R/R_{\rm LTB}-1$ (per cent)")
    ax.text(0.03, 0.92, f"blue: $r_0>{a.r0cut}$, red: inner", transform=ax.transAxes, fontsize=6)
    tt = np.array([s["t"] for s in st])
    bx.plot(tt, [s["mass"] for s in st], ".", ms=1.5, color="0.6", label="all searches (area mass)")
    bx.plot([f["t"] for f in found], [f["mass"] for f in found], "o", color=fs.PAL["red"], ms=4, label="found")
    # largest M of a trapped tracked shell (code R < 2M) against time
    ts = ut[::20]
    mt = []
    for tq in ts:
        mm = t == tq
        trm = [shells[int(g)]["M"] for g in tag[mm] if int(g) in shells and shells[int(g)]["t_trapped_code"] is not None
               and tq >= shells[int(g)]["t_trapped_code"]]
        mt.append(max(trm) if trm else np.nan)
    bx.plot(ts, mt, "-", color=fs.PAL["blue"], label=r"largest $M$ of a shell trapped in the code")
    bx.set_xlim(95, max(tt) + 2)
    bx.set_yscale("log")
    bx.set_ylim(1e-2, 1e3)
    bx.set_xlabel(r"$t$ (coordinate)")
    bx.set_ylabel("mass")
    bx.legend(fontsize=5.5, loc="upper left")
    res["figure"] = fs.save(fig, os.path.join(a.out, "fig_p0l6_verify"))
    with open(os.path.join(a.out, "p0l6_verify.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
