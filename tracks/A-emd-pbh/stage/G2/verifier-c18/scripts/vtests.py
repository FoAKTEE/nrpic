"""Tests V0a-V0f of the verifier's readers and reference on analytic fields
(JOURNAL.md entry 1). Usage: python -I vtests.py --out DIR [--tables T1 T2 ...]."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import figstyle as fs
import matplotlib.pyplot as plt
from vref import LTB
from vread import Tracks, read_summary
from vmeasure import bh_rule, line_ratio, line_mots


def write_table2(path, rbar, u, KL, KT, alpha, betar, extra=None):
    with open(path, "w") as f:
        f.write("# format = 2\n# columns = rbar u KL KT alpha betar\n# exterior = zero\n")
        for k, v in (extra or {}).items():
            f.write("# %s = %s\n" % (k, v))
        for row in zip(rbar, u, KL, KT, alpha, betar):
            f.write(" ".join("%.17e" % x for x in row) + "\n")


def v0a(out):
    am, eta0 = 10.0, 1.2
    a = am * (1 - np.cos(eta0)) / 2
    H = np.sin(eta0) / ((1 - np.cos(eta0)) * a)
    rbar = np.linspace(0, 2 * a, 4001)
    psi = np.sqrt(1.0 / (1 + rbar ** 2 / (4 * a * a)))
    n = rbar.size
    p = os.path.join(out, "v0a_closed_flrw.tab")
    write_table2(p, rbar, psi - 1, -H * np.ones(n), -H * np.ones(n), np.ones(n), np.zeros(n))
    L = LTB(p)
    chi = 2 * np.arctan(rbar / (2 * a))
    m_ex = am * np.sin(chi) ** 3 / 2
    ta_ex = (am / 2) * (np.pi - eta0 + np.sin(eta0))
    eta_ah = 2 * np.pi - np.arccos(1 - 2 * np.sin(chi) ** 2)
    ah_ex = (am / 2) * ((eta_ah - np.sin(eta_ah)) - (eta0 - np.sin(eta0)))
    w = (chi >= 0.1) & (chi <= 1.4)
    em = np.max(np.abs(L.m[w] / m_ex[w] - 1))
    eta_ = np.max(np.abs(L.tau_ta[w] / ta_ex - 1))
    eah = np.max(np.abs(L.tau_ah[w] / ah_ex[w] - 1))
    # V0b: areal radius at the events
    rb = rbar[w][::50]
    sh = L.shell(rb)
    Rah = L.areal_radius(rb, sh["tau_ah"])
    Rta = L.areal_radius(rb, sh["tau_ta"])
    eb1 = np.max(np.abs(Rah / (2 * sh["m"]) - 1))
    eb2 = np.max(np.abs(Rta / (am * np.sin(2 * np.arctan(rb / (2 * a)))) - 1))
    res = {"V0a": {"max_rel_m": em, "max_rel_tau_ta": eta_, "max_rel_tau_ah": eah,
                   "pass": bool(max(em, eta_, eah) < 1e-5)},
           "V0b": {"max_rel_R_at_tau_ah_vs_2m": eb1, "max_rel_R_at_tau_ta_vs_2A": eb2,
                   "pass": bool(max(eb1, eb2) < 1e-9)}}
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.93, wspace=0.3)
    ax[0].plot(chi, ah_ex, color=fs.PAL["blue"], label="exact closed FLRW")
    ax[0].plot(chi[::80], L.tau_ah[::80], "o", ms=3, color=fs.PAL["red"], label="vref from table")
    ax[0].set_xlabel(r"$\chi$")
    ax[0].set_ylabel(r"$\tau_{\rm AH}$")
    ax[0].legend()
    ax[1].semilogy(chi[w], np.abs(L.tau_ah[w] / ah_ex[w] - 1), color=fs.PAL["red"], label=r"$\tau_{\rm AH}$")
    ax[1].semilogy(chi[w], np.abs(L.m[w] / m_ex[w] - 1) + 1e-17, color=fs.PAL["yellow"], label="$m$")
    ax[1].set_xlabel(r"$\chi$")
    ax[1].set_ylabel("relative error")
    ax[1].legend()
    fs.save(fig, os.path.join(out, "fig_v0a"))
    plt.close(fig)
    return res


def v0c(out):
    nt, npart = 11, 5
    t = np.arange(nt) * 0.5
    recs, mrecs = [], []
    rng = np.random.default_rng(7)
    dirs = rng.normal(size=(npart, 3))
    dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    A, B = 1.7, 2.3

    def rec(ti, p, shift=0.0):
        r = 1.0 + 0.1 * p + 0.2 * ti + shift
        x = r * dirs[p]
        n = dirs[p]
        g = A * np.outer(n, n) + B * (np.eye(3) - np.outer(n, n))
        gl = [g[0, 0], g[0, 1], g[0, 2], g[1, 1], g[1, 2], g[2, 2]]
        tau = 0.9 * ti + shift
        return ([ti, p, *x, 0, 0, 0],
                [ti, p, 1.0, 0, 0, 0, *gl, tau, 0, 0, 0, 0])

    for ti in t:
        for p in range(npart):
            a_, b_ = rec(ti, p, shift=0.5)       # first pass, later overwritten for t >= 3.5
            recs.append(a_)
            mrecs.append(b_)
    for ti in t[t >= 3.5]:
        for p in range(npart):
            a_, b_ = rec(ti, p, shift=0.0)
            recs.append(a_)
            mrecs.append(b_)
    # the first pass for t < 3.5 must also be the truth: rewrite it without the shift
    recs2, mrecs2 = [], []
    for ti in t[t < 3.5]:
        for p in range(npart):
            a_, b_ = rec(ti, p, 0.0)
            recs2.append(a_)
            mrecs2.append(b_)
    tr = np.array(recs2 + recs[len(recs2):], float)
    me = np.array(mrecs2 + mrecs[len(mrecs2):], float)
    p1 = os.path.join(out, "v0c.traj.bin")
    p2 = os.path.join(out, "v0c.trajmet.bin")
    tr.astype("<f8").tofile(p1)
    me.astype("<f8").tofile(p2)
    T = Tracks(p1, p2)
    r_ex = 1.0 + 0.1 * np.arange(npart)[None, :] + 0.2 * t[:, None]
    e1 = np.max(np.abs(T.r - r_ex))
    e2 = np.max(np.abs(T.tau - 0.9 * t[:, None]))
    ti = 2.3
    e3 = np.max(np.abs(T.at(ti, T.r) - (1.0 + 0.1 * np.arange(npart) + 0.2 * ti)))
    e4 = np.max(np.abs(T.areal_radius() - T.r * np.sqrt(B)))
    return {"V0c": {"max_err_r": e1, "max_err_tau": e2, "max_err_interp": e3,
                    "max_err_areal": e4, "pass": bool(max(e1, e2, e3, e4) < 1e-13)}}


def write_summary(path, times, masses):
    with open(path, "w") as f:
        f.write("# 1:iter 2:time 3:mass 4:Sx 5:Sy 6:Sz 7:S 8:area 9:hrms 10:hmean 11:meanradius 12:minradius\n")
        for k, (ti, m) in enumerate(zip(times, masses)):
            if np.isfinite(m):
                A = 16 * np.pi * m * m
                f.write("%d %g %g 0 0 0 0 %.10g 0 0 0.4 0.39\n" % (k, ti, m, A))
            else:
                f.write("%d %g nan nan nan nan nan nan nan nan nan nan\n" % (k, ti))


def v0d(out):
    t = 10 + 0.25 * np.arange(40)
    res = {}
    # genuine finds differ from search to search (a bitwise repeat is a stale record)
    m = np.where(np.arange(40) >= 10, 0.3 + 1e-4 * np.arange(40), np.nan)
    p = os.path.join(out, "v0d_i.txt"); write_summary(p, t, m)
    r1 = bh_rule(read_summary(p))
    m2 = m.copy(); m2[-1] = np.nan
    p = os.path.join(out, "v0d_ii.txt"); write_summary(p, t, m2)
    r2 = bh_rule(read_summary(p))
    m3 = np.full(40, np.nan); m3[-3:] = [0.3, 0.3001, 0.3002]
    p = os.path.join(out, "v0d_iii.txt"); write_summary(p, t, m3)
    r3 = bh_rule(read_summary(p))
    # (iv): duplicate the last 5 times with failures appended after (restart)
    p = os.path.join(out, "v0d_iv.txt"); write_summary(p, t, m)
    with open(p, "a") as f:
        for k in range(35, 40):
            f.write("%d %g nan nan nan nan nan nan nan nan nan nan\n" % (k, t[k]))
    s4 = read_summary(p)
    r4 = bh_rule(s4)
    # (v): stale repeats. The finder repeats the last success after a failed search
    # (coord/INTERFACES/cosmo_amr.md 2.3): finds at 10-12 (distinct masses), then repeats of
    # search 12 to the end: not BH without a status file (repeats removed), and with a status
    # file that says found only at 10-12, not BH either; a status file that says found from
    # 10 to the end makes it BH.
    m5 = np.full(40, np.nan); m5[10:13] = [0.30, 0.301, 0.302]; m5[13:] = 0.302
    p = os.path.join(out, "v0d_v.txt"); write_summary(p, t, m5)
    r5 = bh_rule(read_summary(p))
    ps = os.path.join(out, "v0d_v_status.txt")
    with open(ps, "w") as f:
        for k in range(40):
            f.write("%d %.15e %d 0 1 1 1 1 1 1 1 0 0 0 0  # x\n" % (k, t[k], 1 if 10 <= k <= 12 else 0))
    r6 = bh_rule(read_summary(p, ps))
    with open(ps, "w") as f:
        for k in range(40):
            f.write("%d %.15e %d 0 1 1 1 1 1 1 1 0 0 0 0  # x\n" % (k, t[k], 1 if k >= 10 else 0))
    r7 = bh_rule(read_summary(p, ps))
    # (vi): summary times printed with %g (45.90625 -> 45.9062) against full-precision status
    t6 = 45.0 + 0.03125 * np.arange(96)
    m6 = np.where(np.arange(96) >= 29, 0.38 + 1e-5 * np.arange(96), np.nan)
    p = os.path.join(out, "v0d_vi.txt"); write_summary(p, t6, m6)
    ps = os.path.join(out, "v0d_vi_status.txt")
    with open(ps, "w") as f:
        for k in range(96):
            f.write("%d %.15e %d 0 1 1 1 1 1 1 1 0 0 0 0  # x\n" % (k, t6[k], 1 if k >= 29 else 0))
    s6 = read_summary(p, ps)
    r8 = bh_rule(s6)
    ok6 = (r8["bh"] and abs(r8["persistent_from"] - t6[29]) < 1e-12 and s6["status_matched"] == 96)
    ok = (ok6 and r1["bh"] and abs(r1["persistent_from"] - t[10]) < 1e-12 and not r2["bh"]
          and not r3["bh"] and not r4["bh"] and s4["time"].size == 40
          and not r5["bh"] and not r6["bh"] and r7["bh"])
    res["V0d"] = {"i": r1, "ii": r2, "iii": r3, "iv": r4, "v_repeats": r5, "v_status_short": r6,
                  "v_status_long": r7, "vi_g_format": r8, "pass": bool(ok)}
    return res


def write_tab(path, t, names, cols):
    with open(path, "w") as f:
        f.write("# Athena++ data at time=%e  cycle=0 \n" % t)
        f.write("# gid   i       " + "         ".join(names) + "     \n")
        for k in range(cols[0].size):
            f.write("00000 %04d " % (k % 10000) + " ".join("%.12e" % c[k] for c in cols) + "\n")


def v0e(out):
    M = 1.0
    x = np.arange(-16 + 0.025, 16, 0.05)
    r = np.abs(x) + 1e-300
    psi = 1 + M / (2 * r)
    g = psi ** 4
    z = np.zeros_like(x)
    names = ["x1v", "adm_gxx", "adm_gxy", "adm_gxz", "adm_gyy", "adm_gyz", "adm_gzz",
             "adm_Kxx", "adm_Kxy", "adm_Kxz", "adm_Kyy", "adm_Kyz", "adm_Kzz", "adm_psi4"]
    pa = os.path.join(out, "v0e.adm.tab")
    write_tab(pa, 0.0, names, [x, g, z, z, g, z, g, z, z, z, z, z, z, g])
    lm = line_mots(pa)
    xs, R, m, th = lm["pos_profile"]
    w = xs > 1
    em = float(np.max(np.abs(m[w] - M)))
    E = np.exp(-r ** 2 / 4)
    H = 0.3 * 16 * np.pi * E
    pc = os.path.join(out, "v0e.con.tab")
    pt = os.path.join(out, "v0e.tmunu.tab")
    write_tab(pc, 0.0, ["x1v", "con_C", "con_H", "con_M", "con_Z", "con_Mx", "con_My", "con_Mz"],
              [x, z, H, z, z, z, z, z])
    write_tab(pt, 0.0, ["x1v"] + ["tmunu_S%s" % k for k in ("xx", "xy", "xz", "yy", "yz", "zz")]
              + ["tmunu_E", "tmunu_Sx", "tmunu_Sy", "tmunu_Sz"], [x, z, z, z, z, z, z, E, z, z, z])
    lr = line_ratio(pc, pt, pa, r_in=0.5)
    er = max(abs(lr[k] - 0.3) for k in ("r2", "r2sg", "line"))
    mots_ok = all(lm[s] is not None and abs(lm[s]["x"] - 0.5) < 2e-3 and abs(lm[s]["m"] - 1) < 2e-3
                  for s in ("pos", "neg"))
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.93, wspace=0.3)
    ax[0].plot(xs, m, color=fs.PAL["red"], label="line Misner-Sharp mass")
    ax[0].axhline(M, color="k", ls="--", lw=1.0, label="exact $M$")
    ax[0].set_xscale("log")
    ax[0].set_ylim(0.9, 1.1)
    ax[0].set_xlabel(r"$\bar r$")
    ax[0].set_ylabel("$m$")
    ax[0].legend()
    ax[1].plot(xs, th, color=fs.PAL["red"], label=r"$dR/dl - R K_T$")
    ax[1].axvline(0.5, color="k", ls="--", lw=1.0, label=r"exact MOTS $\bar r = M/2$")
    ax[1].axhline(0, color="grey", lw=0.8)
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"$\bar r$")
    ax[1].legend()
    fs.save(fig, os.path.join(out, "fig_v0e"))
    plt.close(fig)
    return {"V0e": {"max_err_ms_mass_r_gt_1": em, "mots": {k: lm[k] for k in ("pos", "neg")},
                    "ratio": lr, "max_err_ratio": er,
                    "pass": bool(em < 1e-3 and mots_ok and er < 1e-12)}}


def v0f(tables):
    res = {}
    for name, path, expect in tables:
        L = LTB(path)
        e = L.at_break(0)
        # rows below rbar = 0.3 are left out: 1 - (dR/dl)^2 cancels there (V0a)
        cand = np.where((L.rbar > 0.3) & (L.tau_ah > 0), L.tau_ah, np.nan)
        first = int(np.nanargmin(cand))
        sh = L.shell([1.0, 2.0])
        d = {"core_edge_rbar": float(L.breaks[0]), "core_edge_R": e["R"],
             "tau_ta_edge": e["tau_ta"], "tau_ah_edge": e["tau_ah"], "m_edge": e["m"],
             "tau_ta_rbar1": float(sh["tau_ta"][0]), "tau_ta_rbar2": float(sh["tau_ta"][1]),
             "tau_ah_rbar1": float(sh["tau_ah"][0]),
             "first_trapped_rbar": float(L.rbar[first]), "first_trapped_tau": float(L.tau_ah[first]),
             "M_outer": float(L.m[-1])}
        if expect:
            d["expect"] = expect
            d["rel"] = {k: abs(d[k] / v - 1) for k, v in expect.items()}
            d["pass"] = bool(max(d["rel"].values()) < 1e-3)
        res[name] = d
    return {"V0f": res}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tables", default=None, help="json list of [name, path, {key: expected}]")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    res.update(v0a(a.out))
    res.update(v0c(a.out))
    res.update(v0d(a.out))
    res.update(v0e(a.out))
    if a.tables:
        res.update(v0f(json.load(open(a.tables))))
    with open(os.path.join(a.out, "vtests.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    for k, v in res.items():
        if "pass" in v:
            print(k, "PASS" if v["pass"] else "FAIL", {kk: vv for kk, vv in v.items() if kk != "pass" and not isinstance(vv, dict)})
    if "V0f" in res:
        for k, v in res["V0f"].items():
            print("V0f", k, v.get("pass"), {kk: round(vv, 6) for kk, vv in v.items() if isinstance(vv, float)})


if __name__ == "__main__":
    main()
