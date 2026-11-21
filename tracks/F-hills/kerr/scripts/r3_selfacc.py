"""R3: HRNA's spurious self-acceleration of a binary moving at V in flat space (M = 0), and its
effect on encounters (JOURNAL entries 1 and 2).

(a) Reproduction of run F-20261115-175620-df20ffe (stage/G0/second_check/flat_binary.py, its
    'hrna_py' arm): m1 = m2 = 0.05, a0 = 3, V = 0.28 along x in the binary plane, T = 300, the same
    hrna.integrate call and the same fit y = a t^2/2 to the step samples.  Earlier: -1.0647e-4.
(b) Scan: CM acceleration a_s = |Omega| V_par from the turning rate Omega of the in-plane CM
    velocity (the force is perpendicular to V, so V turns at constant size) over an integer number
    of relative-orbit periods (about 20), against
      leading order  a_lo  = (m1 m2/mb)(omega0/a0) V cos(psi) ((1 - e)/(1 + e))^(3/2),
                     e     = 1/(1 - V^2 - c3 w0^2) - 1,  c3 = (m1^3 + m2^3)/mb^3,  w0^2 = mb/a0;
      orbit form     a_orb = 2 pi m1 m2 V cos(psi) / (mb p P)  with p, P measured;
    direction -(L_hat_b x V).
(c) Effect on encounters: Delta L_cm = (k/2)(r0^2 - r_p^2) along L_hat_b with k = |a_s|/V
    (leading order k = (m1 m2/mb) omega0/a0), so Delta r_p / r_p and Delta beta / beta for the
    binaries and release radii the track uses; measured directly as the CM pericentre shift of
    HRNA encounters (law hrna, 'sch') against the Newtonian law (no such force), 2404's binary.

    <venv>/bin/python -I r3_selfacc.py <outdir> [--workers N]
"""
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, HERE)
import hrna_incl as H  # noqa: E402
import hrna  # noqa: E402


# ------------------------------------------------------------------------------------------
# (a) reproduction
# ------------------------------------------------------------------------------------------
def part_a():
    m1 = m2 = 0.05
    a0, V, T = 3.0, 0.28, 300.0
    y0 = H.flat_binary_y0(m1, m2, a0, V)
    out = hrna.integrate(hrna.LAW_HRNA, hrna.COORDS_SCH, hrna.PAIR_GRAVITY, 0.0, 0.0, m1, m2, 0.0, 0.0,
                         y0, 1.0, 1e-12, 1e-14, 1e300, 1e300, 0.0, T, 10_000_000, a0, 200000,
                         hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, hrna._work())
    t = np.array(out[4])
    Y = np.array(out[5])
    yc = (m1 * Y[:, 1] + m2 * Y[:, 7]) / (m1 + m2)
    dy = yc - yc[0]
    a_fit = float(np.sum(dy * t ** 2 / 2) / np.sum((t ** 2 / 2) ** 2))
    return dict(a_fit=a_fit, earlier=-1.06473294303476e-4, rel_diff=abs(a_fit / -1.06473294303476e-4 - 1),
                nsamples=int(len(t)))


# ------------------------------------------------------------------------------------------
# (b) scan
# ------------------------------------------------------------------------------------------
def predictions(m1, m2, a0, V, psi):
    mb = m1 + m2
    w0 = math.sqrt(mb / a0 ** 3)
    c3 = (m1 ** 3 + m2 ** 3) / mb ** 3
    e = 1.0 / (1.0 - V * V - c3 * mb / a0) - 1.0
    a_circ = (m1 * m2 / mb) * (w0 / a0) * V * math.cos(psi)
    return a_circ, a_circ * ((1 - e) / (1 + e)) ** 1.5, e


def extrema(t, r, kind):
    """Times and values of local minima (kind=-1) or maxima (+1) of r(t), parabolic refinement."""
    s = kind * r
    idx = np.where((s[1:-1] > s[:-2]) & (s[1:-1] >= s[2:]))[0] + 1
    tt, vv = [], []
    for i in idx:
        t0, t2 = t[i - 1] - t[i], t[i + 1] - t[i]          # local time origin at the sample
        y0, y1, y2 = r[i - 1], r[i], r[i + 1]
        A = np.array([[t0 ** 2, t0, 1], [0.0, 0.0, 1], [t2 ** 2, t2, 1]])
        c = np.linalg.solve(A, np.array([y0, y1, y2]))
        tm = -c[1] / (2 * c[0]) if c[0] != 0 else 0.0
        tt.append(t[i] + tm)
        vv.append(c[0] * tm ** 2 + c[1] * tm + c[2])
    return np.array(tt), np.array(vv)


def measure(job):
    m1, m2, a0, V, psi, phase, n_orb = (job[k] for k in ("m1", "m2", "a0", "V", "psi", "phase", "n_orb"))
    mb = m1 + m2
    P0 = 2 * math.pi * math.sqrt(a0 ** 3 / mb)
    a_circ, a_lo, e_lo = predictions(m1, m2, a0, V, psi)
    T = n_orb * P0 * (1 + 3 * max(e_lo, 0.0)) * 1.3
    y0 = H.flat_binary_y0(m1, m2, a0, V, psi=psi, phase=phase)
    # the M = 0 metric is Minkowski; time stepping capped at P0/300 to resolve the orbit
    out = hrna.integrate(hrna.LAW_HRNA, hrna.COORDS_SCH, hrna.PAIR_GRAVITY, 0.0, 0.0, m1, m2, 0.0, 0.0,
                         y0, P0 / 300, 1e-12, 1e-14, 1e300, 1e300, 0.0, T, 10_000_000, a0, 2_000_000,
                         hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, hrna._work(), P0 / 300)
    t = np.array(out[4])
    Y = np.array(out[5])
    d = Y[:, 0:3] - Y[:, 6:9]
    r = np.linalg.norm(d, axis=1)
    vc = (m1 * Y[:, 3:6] + m2 * Y[:, 9:12]) / mb
    tp, rp = extrema(t, r, -1)
    ta, ra = extrema(t, r, +1)
    res = dict(job, P0=P0, a_circ=a_circ, a_lo=a_lo, e_lo=e_lo, nsamples=int(len(t)))
    if len(tp) < 3:
        res.update(ok=False)
        return res
    P = float(np.mean(np.diff(tp)))
    rpm, ram = float(np.mean(rp)), float(np.mean(ra)) if len(ra) else float("nan")
    p = 2 * rpm * ram / (rpm + ram)
    e_m = (ram - rpm) / (ram + rpm)
    a_orb = 2 * math.pi * m1 * m2 * V * math.cos(psi) / (mb * p * P)
    # The force -(k)(L_hat_b x V) is perpendicular to V: the CM velocity keeps its size and turns
    # about L_hat_b (the CM moves on a circle of radius V_par^2/a_s).  Measure the turning rate of
    # the in-plane CM velocity between the first and the last pericentre (integer periods).
    sel = (t >= tp[0]) & (t <= tp[-1])
    Lh = np.cross(d[0], Y[0, 3:6] - Y[0, 9:12])
    Lh /= np.linalg.norm(Lh)
    e1 = np.cross(np.array([0.0, 1.0, 0.0]) if abs(Lh[1]) < 0.9 else np.array([1.0, 0.0, 0.0]), Lh)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(Lh, e1)
    vpar = np.stack([vc @ e1, vc @ e2], axis=1)
    th = np.unwrap(np.arctan2(vpar[:, 1], vpar[:, 0]))
    Om = float(np.polyfit(t[sel], th[sel], 1)[0])
    Vpar = float(np.mean(np.linalg.norm(vpar[sel], axis=1)))
    # sign convention: the prediction a_s = -k (L_hat_b x V) turns V clockwise about L_hat_b (Om < 0)
    a_meas = -Om * Vpar
    speed = np.linalg.norm(vc, axis=1)
    # eccentricity of the first and of the last relative orbit in the window (q != 1 pumps e)
    def e_near(tt):
        k = int(np.argmin(np.abs(ta - tt))) if len(ta) else None
        if k is None:
            return float("nan")
        kp = int(np.argmin(np.abs(tp - tt)))
        return float((ra[k] - rp[kp]) / (ra[k] + rp[kp]))
    res.update(e_first=e_near(tp[0] + 0.5 * P), e_last=e_near(tp[-1] - 0.5 * P))
    res.update(ok=True, P=P, p=p, e_meas=e_m, n_periods=int(len(tp) - 1), a_meas=a_meas, Omega_turn=Om,
               Vpar_mean=Vpar, a_orb=a_orb, turn_angle=float(Om * (t[sel][-1] - t[sel][0])),
               dspeed_rel=float(np.ptp(speed[sel]) / np.mean(speed[sel])),
               dvz=float(np.ptp(vc[sel] @ Lh)))
    return res


def jobs_b():
    J = []
    mb = 0.1
    for ratio in (30.0, 100.0, 300.0, 1000.0):
        for V in (0.0, 0.02, 0.05, 0.1, 0.2, 0.28, 0.4, 0.5):
            J.append(dict(group="q1", m1=mb / 2, m2=mb / 2, a0=ratio * mb, V=V, psi=0.0, phase=0.0, n_orb=20))
    for q12 in (0.5, 0.25, 0.1):
        for V in (0.05, 0.28):
            m1 = mb / (1 + q12)
            J.append(dict(group="q", m1=m1, m2=mb - m1, a0=30 * mb, V=V, psi=0.0, phase=0.0, n_orb=20, q12=q12))
    for ratio in (30.0, 1000.0, 20000.0):                    # 2402.02178's mass ratio m2/m1 = 2/3
        for V in (0.14, 0.45):                               # CM speed at r = 100 M and 10 M
            m1 = mb / (1 + 2 / 3)
            J.append(dict(group="q2402", m1=m1, m2=mb - m1, a0=ratio * mb, V=V, psi=0.0, phase=0.0, n_orb=20, q12=2 / 3))
    for psi in (math.pi / 6, math.pi / 3, math.pi / 2):
        J.append(dict(group="psi", m1=mb / 2, m2=mb / 2, a0=30 * mb, V=0.28, psi=psi, phase=0.0, n_orb=20))
    J.append(dict(group="phase", m1=mb / 2, m2=mb / 2, a0=30 * mb, V=0.28, psi=0.0, phase=math.pi / 2, n_orb=20))
    return J


# ------------------------------------------------------------------------------------------
# (c) effect on encounters
# ------------------------------------------------------------------------------------------
def L_sch(rp):
    return math.sqrt(2 * rp * rp / (rp - 2))


def drp_from_dL(rp, dL):
    """Schwarzschild parabola: L^2 = 2 rp^2/(rp - 2), d(L^2)/d rp = 2 rp (rp - 4)/(rp - 2)^2."""
    L = L_sch(rp)
    return 2 * L * dL * (rp - 2) ** 2 / (2 * rp * (rp - 4))


def predicted_effects():
    rows = []
    cases = [("2404", 1e-6, 1.0, 1.013, (20.0, 50.0, 70.0), (1.0, 3.0, 4.7, 5.0, 10.0)),
             ("2402", 6.25e-6, 2 / 3, 0.125, None, None),
             ("F q=10 (SC0d)", 0.1, 1.0, 3.0, (4.0, 20.0), None)]
    for name, mb, q12, a0, r0s, betas in cases:
        m1 = mb / (1 + q12)
        m2 = mb - m1
        k = (m1 * m2 / mb) * math.sqrt(mb / a0 ** 3) / a0
        rt = (1 / mb) ** (1 / 3) * a0
        if name == "2402":
            r0_list = [100.0 / rt]
            rps = [6.0, 8.0, 10.0, 14.0, 20.0]
        elif name.startswith("F"):
            r0_list = list(r0s)
            rps = [7.0, 10.0, 13.0]
        else:
            r0_list = list(r0s)
            rps = [rt / b for b in betas]
        for r0r in r0_list:
            r0 = r0r * rt
            for rp in rps:
                dL = 0.5 * k * (r0 * r0 - rp * rp)
                drp = drp_from_dL(rp, dL)
                rows.append(dict(binary=name, mb=mb, q12=q12, a0=a0, k=k, rt=rt, r0_rt=r0r, r0=r0,
                                 rp=rp, beta=rt / rp, dL=dL, dL_over_L=dL / L_sch(rp),
                                 drp_over_rp=drp / rp, dbeta_over_beta=-drp / rp))
    return rows


def peri_job(job):
    o = hrna.run_encounter(law=job["law"], coords="sch", mb=1e-6, q12=1.0, a0=1.013, beta=job["beta"],
                           phase=job["phase"], sense=job["sense"], r0_rt=job["r0_rt"], rf_rt=job["r0_rt"])
    rt = 100.0 ** 1 * 1.013
    rp = rt / job["beta"]
    return dict(job, r_peri=o["r_peri"], rp=rp, outcome=o["outcome"])


def jobs_c():
    J = []
    for law in ("hrna", "newton"):
        for beta in (1.0, 3.0):
            for r0_rt in (20.0, 50.0, 70.0):
                for sense in (1, -1):
                    for phase in (0.0, 0.8, 1.6, 2.4):
                        J.append(dict(law=law, beta=beta, r0_rt=r0_rt, sense=sense, phase=phase))
    return J


def main(outdir, workers=1):
    os.makedirs(outdir, exist_ok=True)
    ra = part_a()
    print("a", ra, flush=True)
    with ProcessPoolExecutor(workers) as ex:
        rb = list(ex.map(measure, jobs_b()))
        rc = list(ex.map(peri_job, jobs_c()))
    eff = predicted_effects()
    # (c) measured pericentre shifts: HRNA minus Newton, per (beta, r0, sense), mean over phases
    meas = []
    for beta in (1.0, 3.0):
        for r0_rt in (20.0, 50.0, 70.0):
            for sense in (1, -1):
                sel = lambda law: [r for r in rc if r["law"] == law and r["beta"] == beta and r["r0_rt"] == r0_rt and r["sense"] == sense]  # noqa: E731
                h = np.array([r["r_peri"] for r in sel("hrna")])
                n = np.array([r["r_peri"] for r in sel("newton")])
                rp = sel("hrna")[0]["rp"]
                pr = [e for e in eff if e["binary"] == "2404" and abs(e["beta"] - beta) < 1e-9 and e["r0_rt"] == r0_rt][0]
                meas.append(dict(beta=beta, r0_rt=r0_rt, sense=sense, rp=rp,
                                 drp_hrna_over_rp=float(np.mean(h) / rp - 1), drp_newton_over_rp=float(np.mean(n) / rp - 1),
                                 spread_hrna=float(np.ptp(h) / rp), pred_drp_over_rp=sense * pr["drp_over_rp"]))
    # separation-fraction change implied by the R3 shift of beta, with the slope of 2404's HRNA
    # curve of geodesic_binary (results/s1_summary.json, run F-hills-20261115-130405-ce17dcf):
    # prograde binaries gain L (beta falls), retrograde ones lose it (beta rises)
    s1 = json.load(open(os.path.join(PKG, "..", "geodesic_binary", "results", "s1_summary.json")))
    bet = np.array(s1["betas"])
    dsf = []
    for e in eff:
        if e["binary"] != "2404":
            continue
        row = dict(beta=e["beta"], r0_rt=e["r0_rt"], drp_over_rp=e["drp_over_rp"])
        for sense, key in ((1, "pro_hrna"), (-1, "retro_hrna")):
            sf = np.array(s1[key]["sf"])
            slope = float(np.interp(e["beta"], bet, np.gradient(sf, bet)))
            dbeta = -sense * e["beta"] * e["drp_over_rp"]
            row[key + "_slope"] = slope
            row[key + "_dsf"] = slope * dbeta
        dsf.append(row)
    res = dict(a=ra, b=rb, c_pred=eff, c_meas=meas, c_dsf=dsf,
               c_note="C2 of geodesic_binary (F-hills-20261115-135732-cace755): HRNA retrograde s.f. at beta = 4.7 "
                      "0.6975 / 0.6725 / 0.68 at r0 = 20 / 50 / 70 r_t (geodesic_binary/JOURNAL.md l. 400-416)")
    with open(os.path.join(outdir, "r3_selfacc.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    q1 = [r for r in rb if r["group"] == "q1" and r["ok"] and r["V"] > 0]
    dev_lo = max(abs(r["a_meas"] / r["a_lo"] - 1) for r in q1)
    dev_orb = max(abs(r["a_meas"] / r["a_orb"] - 1) for r in rb if r["ok"] and r["V"] > 0 and abs(r["a_orb"]) > 1e-15)
    ctrl = [r for r in rb if r["V"] == 0.0 and r["ok"]]
    print(json.dumps(dict(a=ra, max_dev_lo_q1=dev_lo, max_dev_orb=dev_orb,
                          V0_control=[(r["a0"], r["a_meas"]) for r in ctrl],
                          meas=meas, dsf=dsf), indent=1))
    fig(res, outdir)


def fig(res, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    rb = res["b"]
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.9))
    ax1 = fs.inch_axes(fig, 0.75, 3.45, 3.0, 2.1)
    ax2 = fs.inch_axes(fig, 4.75, 3.45, 3.0, 2.1)
    ax3 = fs.inch_axes(fig, 0.75, 0.75, 3.0, 2.1)
    ax4 = fs.inch_axes(fig, 4.75, 0.75, 3.0, 2.1)
    cols = fs.series_colors(4)
    for ratio, c in zip((30.0, 100.0, 300.0, 1000.0), cols):
        rows = sorted([r for r in rb if r["group"] == "q1" and abs(r["a0"] / 0.1 - ratio) < 1e-9 and r["V"] > 0 and r["ok"]],
                      key=lambda r: r["V"])
        V = np.array([r["V"] for r in rows])
        sc = np.array([r["a_circ"] / r["V"] for r in rows])       # (m1 m2/mb) omega0/a0
        ax1.loglog(V, [r["a_meas"] for r in rows], "o", color=c, ms=4, label=f"$a_0/m_b={ratio:g}$")
        ax1.loglog(V, [r["a_lo"] for r in rows], "-", color=c, lw=1)
        ax2.semilogx(V, [r["a_meas"] / r["a_lo"] - 1 for r in rows], "o-", color=c, ms=3)
        ax2.semilogx(V, [r["a_meas"] / r["a_orb"] - 1 for r in rows], "s--", color=c, ms=3, mfc="none")
    ax1.set_xlabel(r"$V$ [$c$]")
    ax1.set_ylabel(r"$|a_s|$")
    ax1.set_title("(a) $q=1$: measured (dots), leading order (lines)", fontsize=7)
    ax1.legend(fontsize=6)
    ax2.axhline(0, **fs.MASK_LINE)
    ax2.set_xlabel(r"$V$ [$c$]")
    ax2.set_ylabel(r"$a_s/a_{\rm pred}-1$")
    ax2.set_title("(b) $q=1$: dots leading order, squares orbit form", fontsize=7)
    for ax in (ax1, ax2):
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    # q and psi groups
    rq = [r for r in rb if r["group"] in ("q", "q2402", "psi", "phase") and r["ok"]]
    lab = [("q=%.2g, V=%g, %g" % (r["q12"], r["V"], r["a0"] / 0.1)) if r["group"] in ("q", "q2402") else
           (r"$\psi=%.2f$" % r["psi"] if r["group"] == "psi" else r"phase $\pi/2$") for r in rq]
    x = np.arange(len(rq))
    ax3.plot(x, [r["a_meas"] / r["a_orb"] - 1 if r["a_orb"] != 0 else np.nan for r in rq], "s", color=cols[1], label="orbit form")
    ax3.plot(x, [r["a_meas"] / r["a_lo"] - 1 if r["a_lo"] != 0 else np.nan for r in rq], "o", color=cols[0], label="leading order")
    for i, r in enumerate(rq):
        if r["group"] == "psi" and abs(r["psi"] - math.pi / 2) < 1e-9:
            ax3.annotate(r"$|a_s|=%.1e$" % abs(r["a_meas"]), (i, 0), fontsize=6, rotation=90, va="bottom")
    ax3.set_xticks(x)
    ax3.set_xticklabels(lab, rotation=60, fontsize=5, ha="right")
    ax3.axhline(0, **fs.MASK_LINE)
    ax3.set_ylabel(r"$a_s/a_{\rm pred}-1$")
    ax3.set_title(r"(c) unequal masses ($q$, $V$, $a_0/m_b$), $\psi$, phase", fontsize=7)
    ax3.legend(fontsize=6)
    meas = res["c_meas"]
    for k, (beta, mk) in enumerate(((1.0, "o"), (3.0, "s"))):
        for sense, c in ((1, cols[0]), (-1, cols[1])):
            rows = [m for m in meas if m["beta"] == beta and m["sense"] == sense]
            r0 = [m["r0_rt"] for m in rows]
            ax4.plot(r0, [m["drp_hrna_over_rp"] - m["drp_newton_over_rp"] for m in rows], mk, color=c, mfc="none" if beta == 3 else c,
                     label=(r"$\beta=%g$, %s" % (beta, "pro" if sense > 0 else "retro")))
            ax4.plot(r0, [m["pred_drp_over_rp"] for m in rows], "-", color=c, lw=0.8)
    ax4.axhline(0, **fs.MASK_LINE)
    ax4.set_xlabel(r"release radius $r_0/r_t$ (2404 binary)")
    ax4.set_ylabel(r"$\Delta r_p/r_p$ (HRNA $-$ Newton)")
    ax4.set_title("(d) CM pericentre shift, 2404 binary (lines: R3)", fontsize=7)
    ax4.legend(fontsize=5.5, ncol=2)
    fs.save(fig, os.path.join(outdir, "r3_selfacc"))


if __name__ == "__main__":
    if "--figure" in sys.argv:            # figure only, from the JSON of an earlier run
        i = sys.argv.index("--figure")
        os.makedirs(sys.argv[i + 2], exist_ok=True)
        fig(json.load(open(sys.argv[i + 1])), sys.argv[i + 2])
        sys.exit(0)
    w = 1
    if "--workers" in sys.argv:
        w = int(sys.argv[sys.argv.index("--workers") + 1])
    main(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.environ["NRPIC_RUN_DIR"], w)
