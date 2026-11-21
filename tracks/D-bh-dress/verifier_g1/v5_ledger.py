"""V5: the numerical ledger of Track D's note at the pinned commit 78d470ca
(note/tables/ledger.tex), recomputed row by row by the verifier where that can be done with
own code from the raw output of the run the row names. Every row gets one of
  independent   : my own computation from the raw output (table, particle file, snapshots,
                  finder output) or from the model's closed form;
  recount       : a number read off the run's own log/manifest and recounted, not recomputed;
  not done      : with the reason.
No code of the track is imported; my own modules: vreaders.py, v1_es.py (exact radial orbit),
v3_kerr.py (spike densities), v4_kerr_stat.py (Kerr-Schild invariants, reference counts).
Writes v5_results.json, v5_ledger.md and figures into $NRPIC_RUN_DIR.
"""
import argparse
import glob
import json
import math
import os

import numpy as np

import vreaders as V

S = "/data/haiyangw/nrpic/scratch/D-bh-dress"
TRK = "/data/haiyangw/nrpic/wt/D-bh-dress/tracks/D-bh-dress"
P = S + "/D-bh-dress-20261115-"
ROWS = []


def row(part, quantity, ledger, mine, kind, runs, note="", tol=None):
    """ledger and mine: lists of numbers (or None). tol: relative tolerance for the verdict."""
    verdict = "not done"
    worst = None
    if kind in ("independent", "recount") and mine is not None and ledger is not None:
        dev = []
        for l, m in zip(ledger, mine):
            if l is None or m is None:
                continue
            dev.append(abs(m - l) / max(abs(l), 1e-300) if l != 0 else abs(m))
        worst = max(dev) if dev else None
        t = tol if tol is not None else 1e-3
        verdict = "agrees" if worst is not None and worst <= t else "differs"
    ROWS.append(dict(part=part, quantity=quantity, ledger=ledger, mine=mine, kind=kind,
                     runs=runs, note=note, max_rel_dev=worst, tol=tol, verdict=verdict))
    print(part, "|", quantity, "|", ledger, "|", mine, "|", kind, verdict, worst, flush=True)


# ------------------------------------------------------------------ part 1: ES data set
def part1(out):
    import v1_es
    rid = "D-bh-dress-20261115-043445-b782009"
    d = P + "043445-b782009"
    tab = V.Table2(d + "/es.tab")
    a = 1.0 + tab.a[0, 1]
    assert tab.a[0, 0] == 0.0
    m_p = 1.0 / a                      # Schwarzschild mass 1 in isotropic coordinates: m_p a = M
    row(1, "bare puncture mass m_p/M; a = 1 + u(0)", [1.0239688282, 0.9765922286], [m_p, a], "independent", [rid],
        "a from the first table row; m_p = M/a (isotropic Schwarzschild inside the bubble)", tol=1e-9)
    # areal radius and Misner-Sharp mass on the table rows
    rb = tab.a[1:, 0]
    sph = V.sphere_of_table(tab, m_p, rb)
    R, m, KT = sph["R"], sph["m"], sph["KT"]
    plateau = (R > 50) & (R < 90)
    H = float(np.median(np.abs(KT[plateau])))
    Hspread = float(np.ptp(np.abs(KT[plateau])) / H)
    row(1, "plateau Hubble rate HM; 1/H", [0.0055812, 179.2], [H, 1 / H], "independent", [rid],
        "H = |K_T| on 50 < R < 90 M (spread %.1e); 1/H printed to one decimal" % Hspread, tol=3e-4)
    # density from the Hamiltonian constraint on the table (4th-order differences)
    h = tab.dr
    u = tab.a[:, 1]
    KL = tab.a[:, 2]
    KTc = tab.a[:, 3]
    up = np.full_like(u, np.nan)
    upp = np.full_like(u, np.nan)
    up[2:-2] = (-u[4:] + 8 * u[3:-1] - 8 * u[1:-3] + u[:-4]) / (12 * h)
    upp[2:-2] = (-u[4:] + 16 * u[3:-1] - 30 * u[2:-2] + 16 * u[1:-3] - u[:-4]) / (12 * h * h)
    rr = tab.a[:, 0]
    with np.errstate(divide="ignore", invalid="ignore"):
        psi = 1 + u + m_p / (2 * rr)
        lap = upp + 2 * up / rr
        rho = (-8 * lap / psi ** 5 + 4 * KL * KTc + 2 * KTc ** 2) / (16 * math.pi)
    Rr = psi ** 2 * rr
    rho0 = 3 * H * H / (8 * math.pi)
    plat = (Rr > 46) & (Rr < 94) & np.isfinite(rho)
    rho0_c = float(np.median(rho[plat]))
    bub = (Rr > 2.5) & (Rr < 35) & np.isfinite(rho)
    row(1, "plateau density rho0 M^2", [3.7182e-6], [rho0_c], "independent", [rid],
        "Hamiltonian constraint on the table rows, median over 46 < R < 94 M; 3H^2/(8 pi) = %.6e" % rho0, tol=1e-4)
    row(1, "density from the table: bubble (largest |rho|/rho0); plateau (largest relative deviation)",
        [2.22e-5, 1.68e-7], [float(np.max(np.abs(rho[bub])) / rho0_c), float(np.max(np.abs(rho[plat] / rho0_c - 1)))],
        "independent", [rid], "my 4th-order differences of the table rows give smaller residuals than the ledger: both say 'zero to truncation', the ledger's values are upper bounds", tol=None)
    ROWS[-1]["verdict"] = "agrees (ledger value is an upper bound)"
    # masses from the particle file and from the table
    pf = V.read_particle_file(d + "/es.nrp")
    mt = pf["m"]
    tracer = mt <= 1e-30                # tracers carry the placeholder mass 1e-30
    dust = mt[~tracer]
    Mlat = float(dust.sum())
    Mtot = float(m[-1])                # Misner-Sharp mass in the exterior (last table row)
    row(1, "dust mass; total mass (M)", [14.5928, 15.5928], [Mtot - 1.0, Mtot], "independent", [rid],
        "Misner-Sharp mass of the last table row (exterior) and minus the hole", tol=1e-5)
    row(1, "HR at the Schuecking radius (R_b = 100); at the outer dust edge (R_out = 106)", [0.558, 0.592],
        [H * 100, H * 106], "independent", [rid], "my H; the radii are model inputs (table header)", tol=2e-3)
    row(1, "table rows; dust particles; tracers", [6096, 4746224, 140],
        [int(len(tab.a)), int(dust.size), int(tracer.sum())], "independent", [rid],
        "rows of es.tab; particles of es.nrp with mass > 1e-30; particles with the placeholder mass 1e-30 (tags %d-%d)" % (np.where(tracer)[0].min(), np.where(tracer)[0].max()), tol=0)
    row(1, "lattice dust mass against the continuum (relative)", [2.77e-8], [Mlat / (Mtot - 1.0) - 1], "independent", [rid],
        "sum of particle masses against my Misner-Sharp dust mass", tol=0.05)
    # Misner-Sharp mass at the inner dust edge R = 36
    lo, hi = 1.0, 60.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if V.sphere_of_table(tab, m_p, np.array([mid]))["R"][0] < 36.0:
            lo = mid
        else:
            hi = mid
    m36 = float(V.sphere_of_table(tab, m_p, np.array([0.5 * (lo + hi)]))["m"][0])
    row(1, "mass inside the wall (R = 36 M) minus M", [0.0], [m36 - 1.0], "independent", [rid],
        "Misner-Sharp mass at R = 36 M from the table; the ledger's 'wall radius against the closed form' (6.66e-16) not recomputed", tol=None)
    ROWS[-1]["verdict"] = "agrees" if abs(m36 - 1) < 1e-8 else "differs"
    # wall R_w(tau) and plateau scale factor
    Rw = [(36 ** 1.5 + 1.5 * math.sqrt(2) * t) ** (2.0 / 3.0) for t in (50, 100, 150, 200)]
    row(1, "wall radius at tau = 50, 100, 150, 200 M", [46.99, 56.80, 65.84, 74.29], Rw, "independent",
        ["D-bh-dress-20261115-145950-23fa1c7"], "closed form (36^(3/2) + (3/2) sqrt(2M) tau)^(2/3)", tol=1.5e-4)
    ap = (1 + 1.5 * H * 200) ** (2.0 / 3.0)
    row(1, "plateau scale factor at tau = 200 M; 1 + 6 ln a", [1.927, 4.93], [ap, 1 + 6 * math.log(ap)], "independent",
        ["D-bh-dress-20261115-145950-23fa1c7"], "EdS a = (1 + 3H tau/2)^(2/3) with my H", tol=1.5e-3)
    # proper time to R = 2M for the tracer groups R0 = 6, 10, 20
    x0 = pf["x"][:140]
    sp0 = V.sphere_of_table(tab, m_p, np.linalg.norm(x0, axis=1))
    Et2 = 1 - 2 * sp0["m"] / sp0["R"] + sp0["R"] ** 2 * sp0["KT"] ** 2
    taus = []
    for g in (0, 1, 2):
        p = 14 * g
        _, tc = v1_es.exact_orbit(sp0["R"][p], sp0["m"][p], Et2[p], sp0["KT"][p])
        taus.append(float(tc))
    row(1, "proper time to R = 2M from 6, 10, 20 M (closed form)", [14.83, 34.44, 244.74], taus, "independent", [rid],
        "my cycloid from the table and the tracer positions (R0 = %.3f, %.3f, %.3f)" % tuple(sp0["R"][[0, 14, 28]]), tol=4e-4)
    # symbolic identities: recount
    nok = [sum(1 for l in open(P + k + "/log.txt") if l.startswith("[OK]")) for k in ("042626-f3da881", "065141-5fdc744")]
    row(1, "symbolic identities passed (two runs)", [48, 48], nok, "recount",
        ["D-bh-dress-20261115-042626-f3da881", "D-bh-dress-20261115-065141-5fdc744"], "lines [OK] in log.txt; sympy not rerun", tol=0)
    # orders from the stored residuals
    off = json.load(open(P + "042704-f3da881/offline_check.json"))
    o3 = []
    for bx in off["check_3d"].values():
        hh = bx["h"]
        for q in ("H_max", "M_max"):
            e = [x[q] for x in bx["exact"]]
            if min(e) > 1e-15:
                o3.append(math.log(e[-2] / e[-1]) / math.log(hh[-2] / hh[-1]))
    row(1, "3D check, orders of the largest residuals, seven boxes (range)", [3.85, 4.07], [min(o3), max(o3)], "recount",
        ["D-bh-dress-20261115-042704-f3da881"], "finest-pair orders from the stored residual maxima (offline_check.json), residuals not recomputed", tol=2e-3)
    reg = off["check_1d"]["regions"]["curvature transition"]
    o1 = []
    for q in ("H", "M"):
        e = reg[q]["max_abs"]
        hh = reg["h"]
        o1.append(math.log(e[-2] / e[-1]) / math.log(hh[-2] / hh[-1]))
    row(1, "radial check, orders in the transition (H; M_r, finest pair)", [3.96, 3.99], o1, "recount",
        ["D-bh-dress-20261115-042704-f3da881"], "from the stored 1d residual maxima", tol=2e-3)
    ct = json.load(open(P + "043406-4df1e76/code_t0.json"))
    o_reg = []
    for regname in ("transition 4 < r < 30", "inner dust edge 34 < r < 46"):
        for q in ("H_max", "M_max"):
            e1, e2 = ct["dx=1"][regname][q], ct["dx=0.5"][regname][q]
            o_reg.append(math.log(e1 / e2) / math.log(2.0))
    row(1, "AthenaK t = 0, region 4 < r < 30 M, orders of H; M", [5.29, 4.69], o_reg[:2], "recount",
        ["D-bh-dress-20261115-043406-4df1e76"], "log2 of the stored maxima at dx = 1 and 1/2 (code_t0.json)", tol=2e-3)
    row(1, "AthenaK t = 0, inner dust edge, orders of H; M", [4.94, 3.20], o_reg[2:], "recount",
        ["D-bh-dress-20261115-043406-4df1e76"], "as above", tol=2e-3)
    row(1, "AthenaK t = 0, box 'mid transition', orders of H; M", [5.88, 5.76], None, "not done",
        ["D-bh-dress-20261115-043406-4df1e76"], "the box values are not in code_t0.json; the analysis was not rerun")
    erho = max(float(l.split(":")[1].strip().rstrip(",")) for l in open(P + "043406-4df1e76/log.txt") if '"E_minus_rho_max"' in l)
    row(1, "deposited density minus the exact density (largest)", [1.14e-13], [erho], "recount",
        ["D-bh-dress-20261115-043406-4df1e76"], "read from log.txt", tol=5e-3)
    row(1, "modelled cost, outer edge 60 M, 200 M: M/8; M/16; data set as generated (card-hours)", [1.37, 2.87, 11.3], None,
        "not done", ["D-bh-dress-20261115-145950-23fa1c7"], "cost model not rebuilt")
    row(1, "wall radius against the closed form (largest relative)", [6.66e-16], None, "not done", [rid],
        "which radius the ledger compares is not stated in the row; replaced by the mass row above")
    return dict(H=H, m_p=m_p, a=a)


# ------------------------------------------------------------------ part 2: floor
def horizon(run):
    d = np.loadtxt(P + run + "/punc.horizon_summary_0.txt")
    t, mm, s = d[:, 1], d[:, 2], d[:, 6]
    o = np.argsort(t, kind="stable")
    t, mm, s = t[o], mm[o], s[o]
    keep = np.concatenate([[True], np.diff(t) > 0])
    return t[keep], mm[keep], s[keep]


def rmean(t, y, t0, w):
    sel = np.abs(t - t0) <= w / 2 + 1e-9
    return float(y[sel].mean()) if (t0 - w / 2 >= t[0] - 1e-9 and t0 + w / 2 <= t[-1] + 1e-9) else float("nan")


def part2(out, plt, fs):
    res = {}
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.14, top=0.96)
    for key, run, col in (("M/8", "121313-284ec4f", fs.PAL["red"]), ("M/16", "121314-284ec4f", fs.PAL["blue"])):
        t, mm, s = horizon(run)
        m100 = float(np.interp(100.0, t, mm)) - 1
        dtm = np.median(np.diff(t))
        tl = [x for x in t if x - 10 >= t[0] - 1e-9 and x + 10 <= t[-1] + 1e-9]
        t_end = max(x for x in tl if x <= 490 + 1e-9)
        drift = rmean(t, mm, t_end, 20) - rmean(t, mm, 50, 20)
        win = [x for x in t if 50 <= x <= 210]
        maxd = max(abs(rmean(t, mm, x, 20) - rmean(t, mm, 50, 20)) for x in win if np.isfinite(rmean(t, mm, x, 20)))
        rm5 = [rmean(t, mm, x, 5) for x in t if 220 <= x <= 255]
        p2p = float(np.nanmax(rm5) - np.nanmin(rm5))
        smax = float(s[t > 5].max())
        res[key] = dict(M_minus_1_at_100=m100, drift_50_to_end=drift, t_end=t_end, maxchange_50_210=maxd,
                        p2p_rm5_220_255=p2p, max_S_after5=smax, dt=float(dtm), t_last=float(t[-1]))
        rm = [rmean(t, mm, x, 20) for x in t]
        ax.plot(t, np.array(rm) - rmean(t, mm, 50, 20), color=col, label=key + " (20 M mean, minus its value at 50 M)")
    ax.axhline(0, **fs.GUIDE)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\Delta M_{\rm AH}/M$")
    ax.legend(loc="upper left", fontsize=8)
    fs.save(fig, out + "/v5_floor")
    r8, r16 = res["M/8"], res["M/16"]
    runs = ["D-bh-dress-20261115-121313-284ec4f", "D-bh-dress-20261115-121314-284ec4f"]
    row(2, "M_AH/M - 1 at t = 100 M: M/8; M/16", [0.00150, -2.57e-4], [r8["M_minus_1_at_100"], r16["M_minus_1_at_100"]],
        "independent", runs, "finder output punc.horizon_summary_0.txt, linear interpolation to t = 100", tol=5e-3)
    row(2, "drift of the 20 M mean, 50 -> 490 M: M/8; M/16", [2.95e-4, 3.67e-5], [r8["drift_50_to_end"], r16["drift_50_to_end"]],
        "independent", runs, "centred 20 M means at 50 M and at the last full window <= 490 M (%.2f, %.2f M)" % (r8["t_end"], r16["t_end"]), tol=1e-2)
    row(2, "largest change of the 20 M mean on [50, 210] M, M/16", [8.22e-6], [r16["maxchange_50_210"]], "independent", runs[1:],
        "my definition: max |mean20(t) - mean20(50)|, t in [50, 210]", tol=1e-2)
    row(2, "peak to peak of the 5 M mean in 220-255 M: M/8; M/16", [9.33e-5, 9.28e-5], [r8["p2p_rm5_220_255"], r16["p2p_rm5_220_255"]],
        "independent", runs, "centred 5 M means at the finder samples in [220, 255]", tol=1e-2)
    row(2, "largest spin |S|/M^2 after 5 M: M/8; M/16", [1.78e-7, 5.65e-9], [r8["max_S_after5"], r16["max_S_after5"]],
        "independent", runs, "column S of the finder output, t > 5 M", tol=1e-2)
    ch = [json.load(open(TRK + "/runs/%s/manifest.json" % r))["resources"]["card_hours"] for r in runs]
    row(2, "card-hours of the two runs", [0.654, 1.523], ch, "recount", runs, "manifest resources.card_hours", tol=0)
    row(2, "smallest detectable change, M/16 (two rows)", [1.96e-5, 2.51e-5, 5.43e-5, 8.28e-5], None, "not done",
        ["D-bh-dress-20261115-130954-49ed46f"], "statistical floor method of the helper not reconstructed")
    return res


# ------------------------------------------------------------------ part 3: spike
def part3(out, plt, fs, v3run, procs):
    import v3_kerr as K
    import v4_kerr_stat as W
    res = {}
    # constant f, Schwarzschild: peak with my invariant integral
    sp = K.Spike(0.0, "constf", nE=64, nL=64, npsi=8)
    rg = np.linspace(7.3, 7.9, 25)
    rho = np.array([sp.density(float(r))["rho"] / 1e8 for r in rg])
    pk = K.peak_of(np.stack([rg, rho], 1))
    res["constf_a0_peak"] = pk
    row(3, "constant f: peak density (1e8 GeV/cm^3) at r/Gm", [0.8699, 7.58], [pk[1], pk[0]], "independent",
        ["D-bh-dress-20261115-145636-5259f48"], "my phase-space integral (v3_kerr.py), 25 radii, parabola at the maximum", tol=3e-3)
    # Gondolo-Silk eq. (6) as quoted in SFW (1305.2619 SFWpaper.tex:440-443): peak at r = 2 rcut
    f0c3 = K.Spike(0.0, "constf").unit / 1e8
    gs = lambda c: (4 * math.pi / 3) * (1.0 / (2 * c)) ** 1.5 * f0c3
    row(3, "peak ratio relativistic / GS (8 Gm); GS(4 Gm) peak over relativistic - 1", [2.590, 0.0922],
        [pk[1] / gs(8.0), gs(4.0) / pk[1] - 1], "independent", ["D-bh-dress-20261115-145636-5259f48"],
        "GS closed form (4 pi f0/3)(2Gm/r)^(3/2)(1 - c/r)^(3/2), maximum (4 pi f0/3)(1/(2c))^(3/2) at r = 2c", tol=5e-3)
    row(3, "the constant-f peak read off SFW Fig. 1; deviation from the SFW curve 8.5-95 Gm", [0.8699, 7.58, 0.00263], None,
        "not done", ["D-bh-dress-20261115-145636-5259f48"], "SFW Fig. 1 is a PDF in the source; I have no digitiser for it")
    # Hernquist a = 0 from my V3 run
    v3 = json.load(open(v3run + "/v3_results.json"))["cases"]["hern_a0.0"]
    rn = np.array(v3["r_nodes_in_range"])
    rel = np.array(v3["rel_dev_at_nodes"])
    sel = (rn >= 5) & (rn <= 39)
    row(3, "Hernquist cusp, 4e6 Msun: peak (GeV/cm^3) at r/Gm", [2.437e18, 7.75], [v3["peak_mine"][1] * 1e18, v3["peak_mine"][0]],
        "independent", ["D-bh-dress-20261115-145636-5259f48"], "my V3 run %s" % os.path.basename(v3run), tol=6e-3)
    row(3, "largest deviation from the FdRW curve (a = 0), 5-39 Gm", [0.0101], [float(np.max(np.abs(rel[sel])))],
        "independent", ["D-bh-dress-20261115-145636-5259f48"], "my curve against my digitisation of fig_rho_hern.pgf", tol=0.3)
    # AthenaK Schwarzschild spike: invariants and counts from the snapshots
    chunks = sorted(glob.glob(P + "123755-25227d4/spike_*"), key=lambda p: int(p.rsplit("_", 1)[1]))
    dE, dL, counts, times, N = [], [], [], None, 0
    for ch in chunks:
        snaps = sorted(glob.glob(ch + "/*.part.*.bin"))
        e0 = l0 = None
        mdE = mdL = None
        cs, ts = [], []
        for spf in snaps:
            s = V.read_snapshot(spf)
            o = np.argsort(s["tag"])
            sel0 = s["sp"][o] == 0
            x, u = s["x"][o][sel0], s["u"][o][sel0]
            r, cth, E, Lz, Q = W.ks_invariants(x, u, a=0.0)
            L = np.linalg.norm(np.cross(x, u), axis=1)
            if e0 is None:
                e0, l0 = E.copy(), L.copy()
                mdE, mdL = np.zeros_like(E), np.zeros_like(E)
            mdE = np.maximum(mdE, np.abs(E / e0 - 1))
            mdL = np.maximum(mdL, np.abs(L / l0 - 1))
            cs.append(np.sum((r >= 4) & (r < 6)))
            ts.append(s["t"])
        N += len(e0)
        dE.append(mdE)
        dL.append(mdL)
        counts.append(cs)
        times = np.array(ts)
    dE, dL = np.concatenate(dE), np.concatenate(dL)
    C46 = np.sum(np.array(counts), axis=0)
    # reference: Hernquist DF at a = 0 cut at E < 0.99 (sampler arguments of D-bh-dress-20261115-123734-25227d4)
    class Ref0(W.Ref):
        def __init__(self):
            K.Spike.__init__(self, 0.0, "hern", nE=40, nL=40, npsi=16)
            self.ecut = 0.99
    R0 = Ref0()
    edges = [2.2, 4.0, 6.0, 10.0, 16.0, 40.0, 110.0]
    nr = [10, 8, 6, 6, 8, 10]
    vals = {}
    for k in range(len(nr)):
        xr, wr = np.polynomial.legendre.leggauss(nr[k])
        for ri, wi in zip(0.5 * (edges[k] + edges[k + 1]) + 0.5 * (edges[k + 1] - edges[k]) * xr,
                          0.5 * (edges[k + 1] - edges[k]) * wr):
            v, _ = R0.n_over_sin(float(ri), 0.0)      # spherically symmetric: one angle
            vals.setdefault(k, 0.0)
            vals[k] += v * wi
    tot = sum(vals.values())
    exp46 = N * vals[1] / tot
    half = len(times) // 2
    late = float(C46[half + 1:].mean())
    row(3, "AthenaK: particles; duration (M)", [48000, 20000], [N, float(times[-1])], "independent",
        ["D-bh-dress-20261115-123755-25227d4"], "species-0 particles in the snapshots; last snapshot time", tol=0)
    row(3, "chi^2 per degree of freedom, median", [0.98], None, "not done", ["D-bh-dress-20261115-125739-a18d74d"],
        "binning of the track's chi^2 not reconstructed")
    row(3, "largest |dE/E|; |dL/L| over the run", [1.33e-6, 1.93e-10], [float(dE.max()), float(dL.max())], "independent",
        ["D-bh-dress-20261115-123755-25227d4", "D-bh-dress-20261115-125739-a18d74d"],
        "my Kerr-Schild formulas at a = 0, L = |x x u|, maximum over particles and snapshots", tol=0.05)
    row(3, "count over equilibrium count, second half, 4-6 Gm", [0.976], [late / exp46], "independent",
        ["D-bh-dress-20261115-125739-a18d74d"], "my reference: Hernquist DF (a = 0, E < 0.99) integrated over r, normalised to all particles; expected %.1f, late mean %.1f" % (exp46, late), tol=0.01)
    row(3, "loss-cone probes: plunging that crossed; bound that crossed; crossing-time offsets", [1200, 0, -0.0241, -0.00604], None,
        "not done", ["D-bh-dress-20261115-124246-aa9dee7", "D-bh-dress-20261115-124249-aa9dee7"], "not reconstructed")
    res["spike_run"] = dict(N=N, t_end=float(times[-1]), dE_max=float(dE.max()), dL_max=float(dL.max()), expected_4_6=exp46,
                            late_mean_4_6=late, counts_4_6=C46.tolist(), times=times.tolist(),
                            ref_range_integrals={str(k): v for k, v in vals.items()})
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.2))
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.15, top=0.96)
    ax.plot(times, C46 / exp46, color=fs.PAL["red"])
    ax.axhline(1, **fs.GUIDE)
    ax.axhline(late / exp46, color=fs.PAL["blue"], lw=1)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel("count 4-6 Gm / my reference")
    fs.save(fig, out + "/v5_spike_counts")
    return res


# ------------------------------------------------------------------ part 4: infall
def infall_closed(eps, a_list, rmin=0.0):
    """Point mass 1 in EdS dust (uniform from rmin), Hubble flow H_i = eps at t_i = 2/(3 eps)."""
    ti = 2.0 / (3.0 * eps)
    ri = np.logspace(math.log10(max(rmin, 1e-3) + 1e-9), math.log10(2000.0), 400000)
    Mi = 1.0 + 0.5 * eps ** 2 * (ri ** 3 - rmin ** 3)
    E = 0.5 * eps ** 2 * ri ** 2 - Mi / ri
    ok = E < 0
    ri, Mi, E = ri[ok], Mi[ok], E[ok]
    rmax = Mi / (-E)
    th0 = np.arccos(np.clip(1 - 2 * ri / rmax, -1, 1))
    A = np.sqrt(rmax ** 3 / (8 * Mi))
    tta = ti + A * (np.pi - (th0 - np.sin(th0)))
    tc = ti + A * (2 * np.pi - (th0 - np.sin(th0)))
    out = {}
    for a in a_list:
        t = ti * a ** 1.5
        out[a] = dict(M_ta=float(np.interp(t, tta, Mi)), r_ta=float(np.interp(t, tta, rmax)), M_c=float(np.interp(t, tc, Mi)))
    # doubling of the mass that reached the centre
    t2 = float(np.interp(2.0, Mi, tc))
    out["a_Mc_2"] = (t2 / ti) ** (2.0 / 3.0)
    return out


def part4(out, v2run):
    c = infall_closed(0.01, (2, 4, 8, 100))
    row(4, "turned-around mass M_ta/M at a/a_i = 2, 4, 8 (closed form, eps = 0.01)", [1.52542, 2.62815, 4.87098],
        [c[2]["M_ta"], c[4]["M_ta"], c[8]["M_ta"]], "independent", ["D-bh-dress-20261115-145610-5259f48"],
        "my Kepler closed form, uniform dust from r = 0, E = -M/r_i", tol=2e-5)
    row(4, "mass that reached the centre at a/a_i = 2, 4, 8", [1.1902, 1.8276, 3.2153], [c[2]["M_c"], c[4]["M_c"], c[8]["M_c"]],
        "independent", ["D-bh-dress-20261115-145610-5259f48"], "same closed form, time to r = 0", tol=1e-4)
    row(4, "(M_ta - M)/(M a/a_i) at a/a_i = 2; 100; limit (4/(3 pi))^(2/3)", [0.263, 0.5581, 0.5648],
        [(c[2]["M_ta"] - 1) / 2, (c[100]["M_ta"] - 1) / 100, (4 / (3 * math.pi)) ** (2.0 / 3.0)], "independent",
        ["D-bh-dress-20261115-145610-5259f48"], "", tol=2e-3)
    rta = [infall_closed(e, (2,))[2]["r_ta"] for e in (0.003, 0.01, 0.03, 0.1)]
    row(4, "turnaround radius at a/a_i = 2 for eps = 0.003, 0.01, 0.03, 0.1 (M)", [74.6, 33.4, 16.1, 7.2], rta, "independent",
        ["D-bh-dress-20261115-120304-795eee9"], "physical radius of the shell at turnaround, same closed form", tol=4e-3)
    row(4, "black-hole mass, radial dust absorbed, a/a_i = 2, 4; doubling at a/a_i", [1.193, 1.828, 4.52],
        [c[2]["M_c"], c[4]["M_c"], c["a_Mc_2"]], "independent", ["D-bh-dress-20261115-125613-248fdaf"],
        "approximation: absorbed when the shell reaches r = 0 (the run absorbs at a finite radius)", tol=5e-3)
    # self-similar rows from my V2 run
    z = np.load(v2run + "/v2_selfsimilar.npz")
    lam, m = z["lam"], z["m"]
    sres = json.load(open(v2run + "/v2_results.json"))["selfsimilar"]["main"]

    def slope(l0, l1):
        s = (lam > l0) & (lam < l1)
        return float(np.polyfit(np.log(lam[s]), np.log(m[s]), 1)[0])
    l1 = sres["lambda_caustic1"]
    row(4, "self-similar: slope of m on [1e-4, 1e-3]; on [3e-3, 3e-2]", [0.741, 0.705], [slope(1e-4, 1e-3), slope(3e-3, 3e-2)],
        "independent", ["D-bh-dress-20261115-123813-97afeea"],
        "my solution (V2 run) puts the shells beyond tau_max = 500 at the centre (2 per cent of M_ta), which flattens m at small lambda; the track's solution has a seed: different model", tol=0.03)
    ROWS[-1]["verdict"] = "not comparable (model differs)"
    row(4, "outermost caustic lambda_1; mass inside it (M_ta)", [0.3553, 0.654], [l1, float(np.interp(l1, lam, m))],
        "independent", ["D-bh-dress-20261115-123813-97afeea"], "my lambda_1 = first apocentre after the first passage, seedless; 0.3580 at tau_max = 30 (central mass 0.10 M_ta), 0.3618 at 200, 0.3630 at 500: a central mass moves it inward, so the seeded 0.3553 is plausible but not reproduced", tol=0.01)
    ROWS[-1]["verdict"] = "not comparable (model differs)"
    row(4, "lambda^(9/4) rho/rho_b below lambda = 1e-4; fraction that passed the centre; captured fractions; radiation era",
        [3.02, 0.6247, 1.0, 1.0, 0.974, 0.740, 1.3e-5], None, "not done",
        ["D-bh-dress-20261115-123813-97afeea", "D-bh-dress-20261115-125613-248fdaf", "D-bh-dress-20261115-122051-bf0d6b1"],
        "not reconstructed (my self-similar solution does not resolve lambda < 1e-4; shell-capture and radiation-era codes not rebuilt)")
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--v2run", default=S + "/D-20261121-031711-0d79cb3")
    ap.add_argument("--v3run", default=S + "/D-20261121-033209-9c0bd44")
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--parts", default="1,2,3,4")
    args = ap.parse_args()
    out = args.out
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    res = {}
    parts = args.parts.split(",")
    if "1" in parts:
        res["part1"] = part1(out)
    if "2" in parts:
        res["part2"] = part2(out, plt, fs)
    if "4" in parts:
        res["part4"] = {str(k): v for k, v in part4(out, args.v2run).items()}
    if "3" in parts:
        res["part3"] = part3(out, plt, fs, args.v3run, args.procs)
    res["rows"] = ROWS
    with open(out + "/v5_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    lines = ["| part | quantity | ledger | mine | kind | verdict | max rel. dev. | runs | note |", "|---|---|---|---|---|---|---|---|---|"]

    def fmt(v):
        if v is None:
            return "--"
        return ", ".join(("%.6g" % x) if isinstance(x, (int, float)) else str(x) for x in v)
    for r in ROWS:
        lines.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["part"], r["quantity"], fmt(r["ledger"]), fmt(r["mine"]), r["kind"], r["verdict"],
            "--" if r["max_rel_dev"] is None else "%.2g" % r["max_rel_dev"], ", ".join(r["runs"]), r["note"]))
    open(out + "/v5_ledger.md", "w").write("\n".join(lines) + "\n")
    n = {}
    for r in ROWS:
        n[(r["kind"], r["verdict"])] = n.get((r["kind"], r["verdict"]), 0) + 1
    print(n)


if __name__ == "__main__":
    main()
