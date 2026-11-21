"""verify_g0: closed forms, start states, GR reading, cost arithmetic (claims K6-K9, K12, K14, K15, K19).

Independent of the track's code: reads only the two passage inputs (puncture positions and
momenta), the MeshBlock trees n(t) of the two mesh runs and the rates of the novelty run
(output files of registered runs, sha256 checked against the run's record where one exists),
and the 2406.11985 table (paper source, untrusted data: parsed as text).

Usage: python3 closed_forms.py --out DIR
Writes DIR/closed_forms.json and DIR/fig_scales.{png,pdf}.
"""
import argparse
import hashlib
import json
import os
import re
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

WT = "/data/haiyangw/nrpic/wt/F-hills"
TR = os.path.join(WT, "tracks/F-hills")
SCR = "/data/haiyangw/nrpic/scratch/F-hills"
KB = "/data/haiyangw/nrpic/kb-data/raw/arxiv"
INPUTS = {"q10": os.path.join(TR, "three_punctures/inputs/hills_q10_m8.athinput"),
          "q4": os.path.join(TR, "nr_first/inputs/p1_q4.athinput")}
CHECKED = []


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def run_file(run, rel):
    p = os.path.join(SCR, run, rel)
    s = os.path.join(SCR, run, "sha256sums.txt")
    state = "no sha256 record"
    if os.path.isfile(s):
        tab = {ln.split(None, 1)[1].strip().lstrip("*").removeprefix("./"): ln.split()[0]
               for ln in open(s) if len(ln.split(None, 1)) == 2}
        state = "sha256 ok" if tab.get(rel) == sha(p) else "sha256 MISMATCH or unlisted"
    CHECKED.append((run, rel, state, sha(p)))
    return p


def parse_input(path):
    blk, cur = {}, None
    for line in open(path):
        s = line.split("#")[0].strip()
        if not s:
            continue
        if s.startswith("<"):
            cur = s.strip("<>")
            blk[cur] = {}
        elif "=" in s and cur:
            k, v = [t.strip() for t in s.split("=", 1)]
            blk[cur][k] = v
    pr = blk["problem"]
    bodies = []
    for c in range(int(pr["ncomp"])):
        g = lambda k: float(pr[f"comp{c}_{k}"])  # noqa: E731
        bodies.append(dict(m=g("mass"), x=np.array([g("x1"), g("x2"), g("x3")]),
                           p=np.array([g("p1"), g("p2"), g("p3")])))
    return blk, bodies


def kepler(rel_x, rel_v, mu):
    r = np.linalg.norm(rel_x)
    v2 = rel_v @ rel_v
    eps = 0.5 * v2 - mu / r
    h = np.cross(rel_x, rel_v)
    evec = np.cross(rel_v, h) / mu - rel_x / r
    e = np.linalg.norm(evec)
    hh = h @ h
    rp = hh / mu / (1 + e)
    a = -mu / (2 * eps) if eps < 0 else np.inf
    return dict(r=r, eps=eps, e=e, rp=rp, a=a, L=np.sqrt(hh), h_z=h[2])


def schw_turning(E, L, r_start):
    """Largest turning point r < r_start of a Schwarzschild geodesic (M = 1)."""
    V2 = lambda r: (1 - 2 / r) * (1 + L * L / (r * r)) - E * E  # noqa: E731
    rs = np.linspace(2.0001, r_start, 200001)
    v = V2(rs)
    idx = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
    if len(idx) == 0:
        return None  # plunges
    i = idx[-1]
    return brentq(V2, rs[i], rs[i + 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R = {}

    # ---- K6 plunge bound and marginally bound orbit
    R["K6_plunge_bound"] = {f"q{q}": 4 * q ** (2 / 3) for q in (4, 9, 10, 20, 30, 100, 1000)}
    # the necessary condition if separation is possible out to the prograde edge D = 2.085
    R["K6_bound_at_prograde_edge_D2.085"] = {f"q{q}": 4 * q ** (2 / 3) / 2.085 for q in (10, 20, 30)}

    def Vmax_minus_1(L):
        rs = np.linspace(2.01, 50, 400001)
        V2 = (1 - 2 / rs) * (1 + L * L / rs ** 2)
        return V2.max() - 1.0
    Lmb = brentq(Vmax_minus_1, 3.5, 4.5, xtol=1e-12)
    rs = np.linspace(2.01, 50, 400001)
    rmb = rs[np.argmax((1 - 2 / rs) * (1 + Lmb ** 2 / rs ** 2))]
    R["K6_marginally_bound"] = dict(L_mb=Lmb, r_mb=float(rmb))

    # ---- K7 Peters time, equal-mass circular binary: T = (5/256) a^4 / (m1 m2 (m1+m2))
    mb = 0.1
    T = 5 / 256 * (30 * mb) ** 4 / ((mb / 2) ** 2 * mb)
    R["K7_peters_time_M"] = T
    R["K7_closed_5over64"] = 5 / 64 * 30 ** 4 * mb

    # ---- K8 scales
    sc = {}
    for q, ab in ((10, 3.0), (4, 5.0)):
        mb = 1.0 / q
        rt = ab * q ** (1 / 3)
        sc[f"q{q}"] = dict(ab_over_rgb=ab / mb, r_t=rt, v_member=0.5 * np.sqrt(mb / ab),
                           v_rel=np.sqrt(mb / ab), E_unit=(mb / 2) ** 2 / ab * q ** (1 / 3),
                           tidal_over_binding_at_4rt=2 * q * (ab / (4 * rt)) ** 3,
                           T_binary=2 * np.pi * np.sqrt(ab ** 3 / mb),
                           plunge_bound=4 * q ** (2 / 3))
    sc["q10"]["D_range_7_13"] = [7 / sc["q10"]["r_t"], 13 / sc["q10"]["r_t"]]
    sc["q10"]["D_rp8"] = 8 / sc["q10"]["r_t"]
    sc["q4"]["D_range_9.82_16"] = [9.82 / sc["q4"]["r_t"], 16 / sc["q4"]["r_t"]]
    sc["q10"]["alpha_r8"] = 3.0 / 8 ** 1.5
    sc["q10"]["alpha_r13"] = 3.0 / 13 ** 1.5
    sc["q10"]["two_point_one_rt"] = 2.1 * sc["q10"]["r_t"]
    sc["q4"]["two_point_one_rt"] = 2.1 * sc["q4"]["r_t"]
    R["K8_scales"] = sc

    # ---- K9 start states and K12 GR reading
    st = {}
    for key, path in INPUTS.items():
        blk, b = parse_input(path)
        m1, m2, M = b[0], b[1], b[2]
        Ptot = m1["p"] + m2["p"] + M["p"]
        mtot = m1["m"] + m2["m"] + M["m"]
        xbar = (m1["m"] * m1["x"] + m2["m"] * m2["x"] + M["m"] * M["x"]) / mtot
        v = {k: bb["p"] / bb["m"] for k, bb in zip(("1", "2", "M"), b)}
        mb = m1["m"] + m2["m"]
        xcm = (m1["m"] * m1["x"] + m2["m"] * m2["x"]) / mb
        vcm = (m1["p"] + m2["p"]) / mb
        bin_ = kepler(m1["x"] - m2["x"], v["1"] - v["2"], mb)
        Rx, Rv = xcm - M["x"], vcm - v["M"]
        orb = kepler(Rx, Rv, M["m"] + mb)
        q = M["m"] / mb
        rt = bin_["a"] * q ** (1 / 3)
        d = dict(P_total=Ptot.tolist(), barycentre=xbar.tolist(), a_b=bin_["a"], e_b=bin_["e"],
                 cm_rp=orb["rp"], cm_e=orb["e"], r0=orb["r"], r_t_from_a_b=rt,
                 r0_over_rt_nominal=orb["r"] / ((3.0 if key == "q10" else 5.0) * q ** (1 / 3)),
                 L_N_specific=orb["L"], L_N_parabola_closed=np.sqrt(2 * (M["m"] + mb) * orb["rp"]),
                 binary_sense=float(np.sign(np.cross(m1["x"] - m2["x"], v["1"] - v["2"])[2] * orb["h_z"])),
                 tlim=float(blk["time"]["tlim"]), x1max=float(blk["mesh"]["x1max"]),
                 num_levels=int(blk["mesh_refinement"]["num_levels"]))
        # GR reading A: coordinates are Schwarzschild, velocity = dx/dt (the HRNA hand-off)
        r = np.linalg.norm(Rx)
        vr = Rx @ Rv / r
        f = 1 - 2 / r
        G2 = 1.0 / (f - Rv @ Rv - (2 / (r - 2)) * vr * vr)
        EA = f * np.sqrt(G2)
        LA = np.sqrt(G2) * np.linalg.norm(np.cross(Rx, Rv))
        # GR reading B: puncture coordinates are isotropic, momentum per mass u_i = P/m
        psi = 1 + 1 / (2 * r)
        alpha = (1 - 1 / (2 * r)) / (1 + 1 / (2 * r))
        EB = alpha * np.sqrt(1 + (Rv @ Rv) / psi ** 4)
        LB = np.linalg.norm(np.cross(Rx, Rv))
        r_areal = r * psi ** 2
        d["GR_A_schw_coords"] = dict(E=EA, L=LA, r_turn=schw_turning(EA, LA, r))
        d["GR_B_isotropic_P_over_m"] = dict(E=EB, L=LB, r_areal_start=r_areal,
                                             r_turn_areal=schw_turning(EB, LB, r_areal))
        d["GR_parabola_with_rp_N"] = dict(L_needed=np.sqrt(2 * orb["rp"] ** 2 / (orb["rp"] - 2)))
        # each member against M (reading A)
        for k, bb in (("1", m1), ("2", m2)):
            xr, vv = bb["x"] - M["x"], v[k] - v["M"]
            rr = np.linalg.norm(xr)
            vrr = xr @ vv / rr
            ff = 1 - 2 / rr
            g2 = 1.0 / (ff - vv @ vv - (2 / (rr - 2)) * vrr * vrr)
            d[f"member{k}_GR_A"] = dict(E=ff * np.sqrt(g2), L=np.sqrt(g2) * np.linalg.norm(np.cross(xr, vv)))
        st[key] = d
    R["K9_K12_start_states"] = st

    # ---- K14 cost arithmetic from the trees n(t) of the two mesh runs
    cost = {}
    rates = None
    nov = json.load(open(run_file("F-hills-20261115-045438-f62d553", "results.json")))
    rates = {k: nov["vacuum"][k]["R_mbcyc_per_s"] for k in nov["vacuum"]
             if isinstance(nov["vacuum"][k], dict) and "R_mbcyc_per_s" in nov["vacuum"][k]}
    for run, cases, m in (("F-hills-20261115-131348-634fb86",
                           ("D205_m8_r1.8", "D205_m16_r1.8", "D205_m16_r1.2"), 0.05),
                          ("F-hills-20261115-131933-907e5fe",
                           ("D256q4_m8_r1.8", "D256q4_m16_r1.8", "D256q4_m16_r1.2"), 0.125)):
        mj = json.load(open(run_file(run, "mesh_count_b.json")))
        for c in cases:
            t = mj["tracks"][c]
            n = np.array(t["n"], float)
            res = 16 if "m16" in c else 8
            h = m / res
            dt = 0.25 * h
            span = float(t["span"])
            cyc = span / dt
            out = dict(n0=n[0], nmax=n.max(), nmean=n.mean(), span=span, h=h, dt=dt, cycles=cyc,
                       samples=len(n), t_first=t["t"][0], t_last=t["t"][-1])
            for lab, rate in (("median", 2201.0), ("slow", 2022.0), ("fast", 2310.0)):
                out[f"card_hours_{lab}"] = n.mean() * cyc / rate / 3600
            # trapezoid in time instead of the plain mean of the samples
            tt = np.array(t["t"], float)
            out["card_hours_median_trapz_over_samples"] = np.trapezoid(n, tt) / (tt[-1] - tt[0]) * cyc / 2201 / 3600
            out["track_card_hours"] = t["card_hours"]
            cost[c] = out
    cost["rates_from_novelty_run"] = rates
    cost["g1_run_200_of_240"] = [200 / 240 * cost["D205_m8_r1.8"]["card_hours_median"],
                                 200 / 240 * cost["D205_m8_r1.8"]["card_hours_slow"]]
    R["K14_cost"] = cost

    # ---- K15 programme sum
    items = dict(q4_triple=[15, 28, 41], two_large_rp=30, rerun_3BH1=12, clump_relax=5)
    R["K15_G2_sum_before_contingency"] = sum(items["q4_triple"]) + 30 + 12 + 5
    R["K15_G2_sum_with_corrected_m16"] = 15.2 + 28 + cost["D256q4_m16_r1.8"]["card_hours_median"] + 30 + 12 + 5

    # ---- K19 2406.11985 configurations (table parsed as data)
    tab = open(os.path.join(KB, "2406.11985/v1/src/massratio_table.tex")).read()

    def row(name):
        line = [ln for ln in tab.splitlines() if ln.strip().startswith(name)][0]
        return [float(x) for x in re.findall(r"-?\d+\.\d+", line)]
    m1H, m2H, m3H = row("$m_1^H/M$"), row("$m_2^H/M$"), row("$m_3^H/M$")
    d_, Dd = row("$d/M$"), row("$D/M$")
    cfg = {}
    for i, name in ((2, "3BH1q8"), (4, "3BH1q18")):
        mbin = m1H[i] + m2H[i]
        qq = m3H[i] / mbin
        rt = d_[i] * qq ** (1 / 3)
        cfg[name] = dict(q=qq, ab_over_rgb=d_[i] / mbin, D_over_rt=Dd[i] / rt,
                         plunge_bound=4 * qq ** (2 / 3))
    R["K19_2406"] = cfg
    R["inputs_checked"] = CHECKED

    with open(os.path.join(a.out, "closed_forms.json"), "w") as f:
        json.dump(R, f, indent=1, default=float)

    # ---- figure: left, the scale plane; right, the effective potential of the q = 10 CM
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 3.4))
    ax = fig.add_axes([0.08, 0.15, 0.39, 0.78])
    qq = np.logspace(0, 3, 200)
    ax.loglog(qq, 4 * qq ** (2 / 3), color=fs.PAL["blue"], label=r"$4q^{2/3}$ ($r_t=4M$)")
    ax.loglog(qq, 4 * qq ** (2 / 3) / 2.085, color=fs.PAL["blue"], ls="--",
              label=r"$4q^{2/3}/2.085$ (prograde edge at $4M$)")
    ax.fill_between([10, 30], 20, 60, color="grey", alpha=0.3, label="box of brief l. 275")
    ax.plot([10, 4], [30, 20], "o", color=fs.PAL["red"], label="first passages")
    ax.set_xlabel(r"$q=M/m_b$")
    ax.set_ylabel(r"$a_b/r_{gb}$")
    ax.set_xlim(1, 1000)
    ax.set_ylim(1, 1000)
    ax.legend(loc="upper left", fontsize=8)
    ax2 = fig.add_axes([0.58, 0.15, 0.39, 0.78])
    s = st["q10"]
    rr = np.linspace(3.0, 30, 2000)
    for lab, E, L, col in (("Schwarzschild reading", s["GR_A_schw_coords"]["E"], s["GR_A_schw_coords"]["L"], fs.PAL["red"]),
                           ("isotropic reading", s["GR_B_isotropic_P_over_m"]["E"], s["GR_B_isotropic_P_over_m"]["L"], fs.PAL["orange"])):
        ax2.plot(rr, (1 - 2 / rr) * (1 + L * L / rr ** 2), color=col, label=f"$V^2$, {lab} ($L={L:.3f}$)")
        ax2.axhline(E * E, color=col, ls=":", lw=1.0)
    Lg = s["GR_parabola_with_rp_N"]["L_needed"]
    ax2.plot(rr, (1 - 2 / rr) * (1 + Lg * Lg / rr ** 2), color=fs.PAL["blue"],
             label=f"$V^2$, GR parabola with $r_p=8$ ($L={Lg:.3f}$)")
    ax2.axhline(1.0, **fs.GUIDE)
    ax2.axvline(s["cm_rp"], **fs.MASK_LINE)
    ax2.set_xlabel(r"$r/M$")
    ax2.set_ylabel(r"$V^2=(1-2M/r)(1+L^2/r^2)$")
    ax2.set_ylim(0.9, 1.08)
    ax2.legend(loc="lower right", fontsize=7)
    fs.save(fig, os.path.join(a.out, "fig_scales"))
    print(json.dumps({k: R[k] for k in ("K6_marginally_bound", "K7_peters_time_M", "K15_G2_sum_before_contingency")}, default=float))


if __name__ == "__main__":
    main()
