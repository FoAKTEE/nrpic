"""verifier_c18b, ledger lines 34-36, 61, 63, 70, 71: own recomputation.

    python3 small_rows.py OUTDIR

34  omega_vir/(c k1) at collapse, delta = 0.0025-0.05, box L = 4 (four Hubble radii):
    omega_GW = 2 omega_orb, omega_orb^2 = G M/R^3 = (4 pi/3) G Delta rho_bar = (Delta/2) H^2
    (H^2 = (8 pi/3) G rho_bar), conformal: omega_c = a omega = 2 sqrt(Delta/2) H_c,
    H_c = a'/a = a^-1/2 for a = (1 + t/2)^2; Delta = 18 pi^2 [BACKGROUND]; collapse at
    a_c = 1.686/(3 delta) (linear peak contrast of three waves of ratios 1, 0.9, 1.1,
    sum 3, reaching 1.686 [BACKGROUND]; cosmo/TESTLOG.md line 139 says 0.56/delta).
35-36 card-hours = steps * cells / rate, steps = ceil(t_end / dt), t_end = 2(sqrt(a_end) - 1),
    dt = 0.25 L/n (read in the logs: dt = 1.5625e-2 at 64, 7.8125e-3 at 128, L = 4), rate =
    zone-cycles per second from the cells, cycles and cpu time of the two AthenaK logs.
61  card-hours of the pancake jobs from Slurm accounting (sacct) of jobs 4373 and 4388.
63  homogeneous runs: alpha/(1 + t/2)^2 - 1 from the histories, Hr_max from cstat.hst.
70  ellipsoid energy: Q(t) built in mpmath at 50 digits, third derivative by mpmath.diff,
    P = (1/5) sum Q'''^2 integrated by mpmath.quad from t1 = 1 to t2 = lam_max^-3/2,
    against E = (8/15) M S (t2^1/3 - t1^1/3).
71  second-order lapse in a flat vacuum torus with a TT wave h_yy = -h_zz = A sin 2pi(x - t):
    <K> obeys d<K>/dt = <K_ij K^ij> = pi^2 A^2 (alpha = 1 + O(A^2); <D^2 alpha> = 0 on the
    torus), so the conformal-time lapse 1/alpha = 1 + (1/3) int K dt and the 1+log lapse
    ln alpha = -2 int K dt; mean of K_ij K^ij evaluated numerically on a grid.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import mpmath as mp
import numpy as np

RC = "/data/haiyangw/nrpic/runs/cosmo"
LOGS = {64: (f"{RC}/east_d0.01_n64_pcs4b/athena.20261114-072656.log",
             "c580392a74e276ccf27d25b7e6bfcafda58daa468d15fee289d9536bd394fe3e"),
        128: (f"{RC}/east_d0.01_n128_tsc/athena.20261114-021442.log",
              "c2d315aa785b5ea25d9bcac67d2096f8ed4a966d12a41bd114b51f66234e78ed")}
FLRW = {"flrw_n32_cpu_sd": (f"{RC}/flrw_n32_cpu_sd/flrw.nrpic.hst", None),
        "dtexp_test/lim": (f"{RC}/dtexp_test/lim/flrw.nrpic.hst", f"{RC}/dtexp_test/lim/flrw.cstat.hst")}
MANIFEST_FLRW = ("/data/haiyangw/nrpic/wt/B-emd-gw/tracks/B-emd-gw/runs/"
                 "B-emd-gw-20261115-115414-7ffbde1/manifest.json")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def hst(path):
    head = [ln for ln in open(path) if ln.startswith("# [")][0]
    names = [w.split("=")[1] for w in head[1:].split()]
    c = np.loadtxt(path)
    return {nm: c[:, i] for i, nm in enumerate(names)}


def regime():
    out = {}
    delta_vir = 18*np.pi**2
    k1 = 2*np.pi/4.0

    def ratio(d):
        ac = 1.686/(3*d)
        return 2*np.sqrt(delta_vir/2)*ac**-0.5/k1

    def ratio056(d):
        return 2*np.sqrt(delta_vir/2)*(0.56/d)**-0.5/k1
    out["closed_form"] = "omega/(c k1) = 2 sqrt(9 pi^2) sqrt(delta/a_c delta) / (pi/2) = 12 sqrt(delta/0.56) for a_c = 0.56/delta"
    out["endpoints_ac_0.56"] = [ratio056(0.0025), ratio056(0.05)]
    out["endpoints_ac_1.686_over_3"] = [ratio(0.0025), ratio(0.05)]
    # the sampled grid of the producing script's definition: 60 points log-spaced 1e-3..0.1
    g = np.logspace(-3, -1, 60)
    m = (g >= 0.0025) & (g <= 0.05)
    out["grid_first_last_delta"] = [float(g[m][0]), float(g[m][-1])]
    out["grid_ratio_min_max"] = [float(ratio056(g[m][0])), float(ratio056(g[m][-1]))]
    # cost
    rates = {}
    for n, (p, s) in LOGS.items():
        txt = open(p).read()
        cyc = int(re.findall(r"^time=\S+ cycle=(\d+)", txt, re.M)[-1])
        cpu = float(re.findall(r"cpu time used\s*=\s*(\S+)", txt)[-1])
        dts = sorted(set(float(x) for x in re.findall(r"dt=(\S+)", txt)))
        zc = float(re.findall(r"zone-cycles/cpu_second\s*=\s*(\S+)", txt)[-1])
        rates[n] = {"sha256_ok": sha(p) == s, "cycles": cyc, "cpu_s": cpu,
                    "rate_mine": n**3*cyc/cpu, "rate_code": zc, "dt_values": dts,
                    "dt_model": 0.25*4.0/n}
    out["rates"] = rates
    rows = []
    for d, aend in ((0.01, 140.0), (0.0025, 560.0)):
        t_end = 2*(np.sqrt(aend) - 1)
        for n, nz in ((64, 64), (128, 128), (256, 256), (256, 16)):
            steps = int(np.ceil(t_end/(0.25*4.0/n)))
            cells = n*n*nz
            rate = rates[64]["rate_mine"] if cells <= 64**3 else rates[128]["rate_mine"]
            rows.append({"delta": d, "n": n, "nz": nz, "steps": steps,
                         "card_hours": steps*cells/rate/3600.0})
    out["cost"] = rows
    # the measured run that the 64^3, delta = 0.01, a = 140 row describes
    out["measured_64_cpu_hours"] = rates[64]["cpu_s"]/3600.0
    return out


def slurm():
    out = {}
    try:
        r = subprocess.run(["sacct", "-j", "4373,4388", "-X", "-n", "-P",
                            "--format=JobID,ElapsedRaw,AllocTRES"], capture_output=True,
                           text=True, timeout=60)
        for ln in r.stdout.strip().splitlines():
            jid, el, tres = ln.split("|")
            out[jid] = {"elapsed_s": int(el), "card_hours": int(el)/3600.0, "tres": tres}
        out["total"] = sum(v["card_hours"] for v in out.values() if isinstance(v, dict))
    except Exception as e:  # noqa: BLE001
        out["error"] = repr(e)
    return out


def flrw():
    man = json.load(open(MANIFEST_FLRW))
    want = {i["path"]: i["sha256"] for i in man["inputs"]}
    out = {}
    for k, (p, pc) in FLRW.items():
        h = hst(p)
        t = h["time"]
        e = h["alpha_probe"]/(1 + 0.5*t)**2 - 1.0
        o = {"sha256_matches_manifest": want.get(p) == sha(p), "a_end": float((1 + 0.5*t[-1])**2),
             "max_rel_err_lapse": float(np.abs(e).max()), "records": int(len(t))}
        # also the lapse extrema columns, if present
        for col in ("alpha_min", "alpha_max"):
            if col in h:
                o[f"max_rel_err_{col}"] = float(np.abs(h[col]/(1 + 0.5*t)**2 - 1).max())
        if pc:
            c = hst(pc)
            o["cstat_sha256_matches_manifest"] = want.get(pc) == sha(pc)
            o["Hr_max_last"] = float(c["Hr_max"][-1])
            o["a_last_cstat"] = float((1 + 0.5*c["time"][-1])**2)
            o["Hr_max_largest"] = float(c["Hr_max"].max())
        out[k] = o
    return out


def ellipsoid():
    mp.mp.dps = 50
    lam = [mp.mpf("0.11122237"), mp.mpf("0.05"), mp.mpf("0.02")]
    M, RL = mp.mpf(3)/4, mp.mpf(3)/2

    def Q(i, t):
        a = t**(mp.mpf(2)/3)
        R2 = [(a*RL*(1 - a*li))**2 for li in lam]
        return M/15*(3*R2[i] - sum(R2))

    def P(t):
        return sum(mp.diff(lambda s: Q(i, s), t, 3)**2 for i in range(3))/5
    t1 = mp.mpf(1)
    t2 = max(lam)**(-mp.mpf(3)/2)
    E_num = mp.quad(P, [t1, 2, 4, 8, 16, t2])
    S = sum(li**4 for li in lam) - (lam[0]**2*lam[1]**2 + lam[0]**2*lam[2]**2 + lam[1]**2*lam[2]**2)
    E_closed = mp.mpf(8)/15*M*S*(t2**(mp.mpf(1)/3) - t1**(mp.mpf(1)/3))
    # the same in double precision with numpy (Gauss-Legendre in u = t^(1/3), exact
    # integrand of the closed form): shows the double-precision level of agreement
    x, w = np.polynomial.legendre.leggauss(40)
    l = np.array([0.11122237, 0.05, 0.02])
    S_d = (l**4).sum() - (l[0]**2*l[1]**2 + l[0]**2*l[2]**2 + l[1]**2*l[2]**2)
    u1, u2 = 1.0, float(t2)**(1/3)
    u = 0.5*(u2 - u1)*x + 0.5*(u2 + u1)
    # P dt = (8/45) M S t^(-2/3) dt = (8/45) M S u^-2 3 u^2 du
    E_gl = 0.5*(u2 - u1)*np.sum(w*(8/45)*0.75*S_d*3.0)
    E_cl_d = 8/15*0.75*S_d*(u2 - u1)
    return {"t2": float(t2), "S": float(S), "E_mpmath_quadrature": float(E_num),
            "E_closed": float(E_closed), "rel_dev_mpmath_50digits": float(abs(E_num/E_closed - 1)),
            "rel_dev_double_GL": float(abs(E_gl/E_cl_d - 1)),
            "P_over_closed_at_t": [float(P(mp.mpf(tt))/(mp.mpf(8)/45*M*S*mp.mpf(tt)**(-mp.mpf(2)/3)))
                                   for tt in (1, 3, 10, 26)]}


def lapse2():
    A, t = 1e-6, 10.0
    x = (np.arange(4096) + 0.5)/4096
    # K_ij = -(1/2) d_t h_ij for h_yy = -h_zz = A sin 2 pi (x - t)
    Kyy = -0.5*(-2*np.pi*A*np.cos(2*np.pi*(x - 0.37)))
    kk = float(np.mean(2*Kyy**2))
    # integrate the two lapse conditions with <K> = kk t
    from scipy.integrate import solve_ivp
    conf = solve_ivp(lambda s, y: [-(1/3)*y[0]**2*kk*s], (0, t), [1.0], rtol=1e-13, atol=1e-16)
    olog = solve_ivp(lambda s, y: [-2*y[0]*kk*s], (0, t), [1.0], rtol=1e-13, atol=1e-16)
    return {"mean_KijKij_over_pi2A2": kk/(np.pi**2*A**2),
            "conformal_alpha_minus_1": float(conf.y[0, -1] - 1),
            "onelog_alpha_minus_1": float(olog.y[0, -1] - 1),
            "closed_conformal": -np.pi**2*A**2*t**2/6, "closed_onelog": -np.pi**2*A**2*t**2}


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    res = {"regime": regime(), "slurm_pancake": slurm(), "flrw": flrw(),
           "ellipsoid": ellipsoid(), "lapse2": lapse2()}
    with open(os.path.join(out, "small_rows.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
    figure(res, out)


def figure(res, out):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    ax = axs[0]
    d = np.logspace(-3, -1, 400)
    ax.loglog(d, 12*np.sqrt(d/0.56), color=fs.PAL["blue"], label=r"$12\sqrt{\delta/0.56}$")
    g = np.logspace(-3, -1, 60)
    ax.loglog(g, 12*np.sqrt(g/0.56), "o", ms=2, color=fs.PAL["red"], label="60-point grid")
    ax.axvspan(0.0025, 0.05, color="grey", alpha=0.12)
    for v in res["regime"]["grid_ratio_min_max"]:
        ax.axhline(v, **fs.THIN)
    ax.set_xlabel(r"$\delta$")
    ax.set_ylabel(r"$\omega_{\rm vir}/(ck_1)$, $L=4$")
    ax.legend(fontsize=6, loc="upper left")
    ax.set_title("(a) line 34", fontsize=8)
    ax = axs[1]
    for k, (p, pc) in FLRW.items():
        h = hst(p)
        a = (1 + 0.5*h["time"])**2
        ax.semilogy(a, np.maximum(np.abs(h["alpha_probe"]/a - 1), 1e-12), label=k)
    ax.set_xscale("log")
    ax.set_xlabel(r"$a$")
    ax.set_ylabel(r"$|\alpha/(1+t/2)^2-1|$")
    ax.legend(fontsize=6)
    ax.set_title("(b) line 63", fontsize=8)
    ax = axs[2]
    tt = np.geomspace(1, res["ellipsoid"]["t2"], 50)
    ax.loglog(tt, (8/45)*0.75*res["ellipsoid"]["S"]*tt**(-2/3), color=fs.PAL["blue"],
              label="closed form $P(t)$")
    pr = res["ellipsoid"]["P_over_closed_at_t"]
    tp = [1, 3, 10, 26]
    ax.loglog(tp, [(8/45)*0.75*res["ellipsoid"]["S"]*t**(-2/3)*r for t, r in zip(tp, pr)], "o",
              ms=4, color=fs.PAL["red"], label="mpmath third derivative")
    ax.set_xlabel(r"$t/t_k$")
    ax.set_ylabel(r"$P_{\rm GW}$ ($G=c=1$)")
    ax.legend(fontsize=6)
    ax.set_title("(c) line 70", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "small_rows_c18b"))


if __name__ == "__main__":
    main()
