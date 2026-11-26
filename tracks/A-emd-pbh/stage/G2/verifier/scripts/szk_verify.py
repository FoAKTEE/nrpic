#!/usr/bin/env python3
"""Fresh verifier of gate G2 (Track A), item V1: the Szekeres series against a reference of my own.

Reference (JOURNAL.md entry 1, derived there): quasi-spherical Szekeres dust with a simultaneous bang has, per
fluid element, rho = rhobar/(1 + c G(t)) and K = d ln rho/dt = -3 H_T - c Gdot/(1 + c G), with c constant along
the element and the shell functions (H_T, rhobar, G) set by one number s = k^(3/2)/M per shell. Everything is
taken from the initial slice cell by cell: KT (transverse eigenvalue of K^i_j) fixes eta_i and s through
H_T t_i, rho_i (particle mass / (psi^6 h^3)) fixes c. KL is not used (it is the check V1.0). No code of the
track is imported; the formats are read from the AthenaK source (nrpic_cosmo.cpp lines 7-19, nrpic_io.cpp
546-552 and 1164).

    python -I szk_verify.py --out DIR --prep PREPDIR --member N64=DIR[,DIR2] ... [--test-only]

Before the data: test_closed_form() integrates the general dust equations of one element (Raychaudhuri,
continuity, the shell's Friedmann equation; no Szekeres formula) with scipy and compares with the closed form.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

HUB = 1.0 / 16.0                 # background Hubble rate at the initial slice (DESIGN 1, data set 2)
T_I = 2.0 / (3.0 * HUB)          # age of the initial slice, simultaneous bang at t = 0
L = 16.0                         # box [-8, 8]^3
SMALL = 0.08                     # series below this eta
CH = 1 << 21

# ------------------------------------------------------------------ shell functions (bound: sign +1, unbound: -1)


def _emsin(e, b):
    """eta - sin eta (b = +1) or sinh eta - eta (b = -1), series for small eta."""
    out = np.where(b > 0, e - np.sin(e), np.sinh(e) - e)
    sm = e < SMALL
    if np.any(sm):
        x = e[sm]
        bb = b[sm]
        x2 = x * x * bb       # eta^2 with the sign of the series (unbound: eta -> i eta flips alternate terms)
        ser = x ** 3 / 6 * (1 - x2 / 20 + x2 ** 2 / 840 - x2 ** 3 / 60480 + x2 ** 4 / 6652800)
        out = out.copy()
        out[sm] = ser
    return out


def _omc(e, b):
    """1 - cos eta or cosh eta - 1, without cancellation."""
    return np.where(b > 0, 2 * np.sin(e / 2) ** 2, 2 * np.sinh(e / 2) ** 2)


def _sn(e, b):
    return np.where(b > 0, np.sin(e), np.sinh(e))


def _f(e, b):
    """H_T t = sn (emsin)/omc^2."""
    out = _sn(e, b) * _emsin(e, b) / _omc(e, b) ** 2
    sm = e < SMALL
    if np.any(sm):
        x2 = e[sm] ** 2 * b[sm]
        out = out.copy()
        out[sm] = 2 / 3 - x2 / 30 - x2 ** 2 / 504 - x2 ** 3 / 10800 - x2 ** 4 / 266112
    return out


def _G(e, b):
    out = -1 + 1.5 * _f(e, b)
    sm = e < SMALL
    if np.any(sm):
        x2 = e[sm] ** 2 * b[sm]
        out = out.copy()
        out[sm] = -(x2 / 20 + x2 ** 2 / 336 + x2 ** 3 / 7200 + x2 ** 4 / 177408 + 691 * x2 ** 5 / 3302208000)
    return out


def _dG(e, b):
    """dG/d eta."""
    sn, om = _sn(e, b), _omc(e, b)
    cs = np.where(b > 0, np.cos(e), np.cosh(e))
    N = sn * _emsin(e, b)
    dN = cs * _emsin(e, b) + sn * om * np.where(b > 0, 1.0, 1.0)
    out = 1.5 * (dN / om ** 2 - 2 * N * sn / om ** 3)
    sm = e < SMALL
    if np.any(sm):
        x = e[sm]
        bb = b[sm]
        x2 = x * x * bb
        out = out.copy()
        out[sm] = -bb * x * (1 / 10 + x2 / 84 + x2 ** 2 / 1200 + x2 ** 3 / 22176 + 691 * x2 ** 4 / 330220800)
    return out


def _bisect(fun, lo, hi, target, n=80):
    lo, hi = lo.copy(), hi.copy()
    flo = fun(lo) - target
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        fm = fun(mid) - target
        same = np.sign(fm) == np.sign(flo)
        lo = np.where(same, mid, lo)
        flo = np.where(same, fm, flo)
        hi = np.where(same, hi, mid)
    return 0.5 * (lo + hi)


def eta_from_x(x, b):
    """eta on the expanding branch from H_T t = x (bound: x < 2/3, eta in (0, pi); unbound: eta in (0, 40))."""
    lo = np.full_like(x, 1e-12)
    hi = np.where(b > 0, math.pi - 1e-12, 40.0)
    return _bisect(lambda e: _f(e, b), lo, hi, x)


def eta_from_t(st, b):
    """eta from s t = emsin(eta) (monotonic in eta: up to 2 pi for bound shells)."""
    lo = np.full_like(st, 1e-12)
    hi = np.where(b > 0, 2 * math.pi - 1e-9, 60.0)
    return _bisect(lambda e: _emsin(e, b), lo, hi, st, n=90)


class Element:
    """Per-cell constants from the initial slice (KT, rho_i)."""

    def __init__(self, KT, rho_i, tol_eds=1e-12):
        x = -KT * T_I
        self.eds = np.abs(x - 2 / 3) < tol_eds
        b = np.where(x < 2 / 3, 1.0, -1.0)
        xx = np.where(self.eds, 0.6, x)               # placeholders for EdS cells
        bb = np.where(self.eds, 1.0, b)
        e = eta_from_x(xx, bb)
        self.b = bb
        self.s = _emsin(e, bb) / T_I
        rhobar = 3 / (4 * math.pi) * self.s ** 2 / _omc(e, bb) ** 3
        G = _G(e, bb)
        c = (rhobar / rho_i - 1) / G
        self.c = np.where(self.eds, 0.0, c)
        self.rho_i = rho_i
        self.eta_i = e

    def at(self, t, c=None):
        """rho, K at time t (age), optionally with another c (the LTB element of the same shell)."""
        c = self.c if c is None else c
        e = eta_from_t(self.s * t, self.b)
        om = _omc(e, self.b)
        HT = self.s * _sn(e, self.b) / om ** 2
        rhobar = 3 / (4 * math.pi) * self.s ** 2 / om ** 3
        G = _G(e, self.b)
        Gd = _dG(e, self.b) * self.s / om
        rho = rhobar / (1 + c * G)
        K = -3 * HT - c * Gd / (1 + c * G)
        # EdS cells: rho_i (t_i/t)^2, K = -2/t
        rho = np.where(self.eds, self.rho_i * (T_I / t) ** 2, rho)
        K = np.where(self.eds, -2.0 / t, K)
        return rho, K


# ------------------------------------------------------------------ analytic test: closed form against the ODEs


def test_closed_form():
    from scipy.integrate import solve_ivp
    rng = np.random.default_rng(7)
    rows = []
    for x, c in [(0.55, 0.3), (0.62, -0.2), (0.66, 1.5), (0.70, 0.4), (0.75, -0.3), (0.6666, 2.0), (0.5, 0.0)]:
        el = Element(np.array([-x / T_I]), np.array([1.0]), tol_eds=1e-14)
        # rescale rho_i so that c is the requested one: rho_i = rhobar_i/(1 + c G_i)
        e = el.eta_i
        rhobar_i = 3 / (4 * math.pi) * el.s ** 2 / _omc(e, el.b) ** 3
        rho_i = rhobar_i / (1 + c * _G(e, el.b))
        el = Element(np.array([-x / T_I]), rho_i, tol_eds=1e-14)
        r0, K0 = el.at(T_I)
        HT0 = x / T_I
        Th0 = -K0[0]
        y0 = [HT0, rhobar_i[0], Th0, r0[0]]

        def rhs(t, y):
            HT, rb, Th, rho = y
            HL = Th - 2 * HT
            return [-HT ** 2 - 4 * math.pi / 3 * rb, -3 * HT * rb,
                    -Th ** 2 / 3 - (2 / 3) * (HL - HT) ** 2 - 4 * math.pi * rho, -rho * Th]
        tend = T_I + 30.0
        sol = solve_ivp(rhs, (T_I, tend), y0, rtol=1e-12, atol=1e-16, dense_output=True)
        for tau in (0.0, 10.0, 20.0, 30.0):
            t = T_I + tau
            Y = sol.sol(t)
            rho, K = el.at(t)
            Hb = 2 / (3 * t)
            rows.append(dict(x=x, c=c, tau=tau, dK_over_H=float(abs(K[0] + Y[2]) / Hb),
                             drho_rel=float(abs(rho[0] - Y[3]) / Y[3])))
    worst = max(max(r["dK_over_H"], r["drho_rel"]) for r in rows)
    _ = rng
    return dict(rows=rows, worst=worst, passed=bool(worst < 1e-8))


# ------------------------------------------------------------------ readers (formats from the AthenaK source)


def read_cosmo(path):
    """NRCOSMO1: 8 bytes, 3 int64 (n1, n2, n3), 9 arrays of doubles, first index fastest."""
    with open(path, "rb") as f:
        assert f.read(8) == b"NRCOSMO1"
        n = tuple(int(v) for v in np.frombuffer(f.read(24), "<i8"))
    nc = n[0] * n[1] * n[2]
    mm = np.memmap(path, dtype="<f8", mode="r", offset=32, shape=(9, nc))
    return n, mm


def read_particles(path):
    """NRPIC001: 8 bytes, int64 N, N records of 7 doubles (x^i, u_i, m), N int32 species."""
    with open(path, "rb") as f:
        assert f.read(8) == b"NRPIC001"
        N = int(np.frombuffer(f.read(8), "<i8")[0])
    rec = np.memmap(path, dtype="<f8", mode="r", offset=16, shape=(N, 7))
    return rec


def read_field(path):
    """NRFIELD2: 8 bytes, double t, 3 int64, E and chi (float32), then H, Mx, My, Mz, Khat, Theta, alpha (f8)."""
    with open(path, "rb") as f:
        magic = f.read(8)
        t = float(np.frombuffer(f.read(8), "<f8")[0])
        n = tuple(int(v) for v in np.frombuffer(f.read(24), "<i8"))
    nc = n[0] * n[1] * n[2]
    off = 40
    E = np.memmap(path, dtype="<f4", mode="r", offset=off, shape=(nc,))
    chi = np.memmap(path, dtype="<f4", mode="r", offset=off + 4 * nc, shape=(nc,))
    out = dict(t=t, n=n, E=E, chi=chi, magic=magic)
    if magic == b"NRFIELD2":
        dd = np.memmap(path, dtype="<f8", mode="r", offset=off + 8 * nc, shape=(7, nc))
        for i, k in enumerate(("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha")):
            out[k] = dd[i]
    return out


# ------------------------------------------------------------------ initial slice per member


def initial(prep_dir):
    n, F = read_cosmo(os.path.join(prep_dir, "fields.bin"))
    N = n[0]
    h = L / N
    nc = N ** 3
    rec = read_particles(os.path.join(prep_dir, "particles.nrp"))
    assert rec.shape[0] == nc, "one particle per cell expected"
    rho_i = np.empty(nc)
    filled = np.zeros(nc, bool)
    for s0 in range(0, nc, CH):
        r = np.asarray(rec[s0:s0 + CH])
        ijk = np.floor((r[:, :3] + L / 2) / h).astype(np.int64)
        idx = (ijk[:, 2] * N + ijk[:, 1]) * N + ijk[:, 0]
        # offset of the particle from its cell centre: must be ~0
        off = np.max(np.abs(r[:, :3] - (-L / 2 + (ijk + 0.5) * h)))
        assert off < 1e-9 * h + 1e-12, off
        psi = np.asarray(F[0, idx])
        rho_i[idx] = r[:, 6] / (psi ** 6 * h ** 3)
        filled[idx] = True
    assert filled.all()
    KT = np.empty(nc)
    KL = np.empty(nc)
    Kf = np.empty(nc)
    for s0 in range(0, nc, CH):
        sl = slice(s0, min(nc, s0 + CH))
        psi, K = np.asarray(F[0, sl]), np.asarray(F[1, sl])
        A = [np.asarray(F[3 + i, sl]) / psi ** 6 for i in range(6)]   # xx xy xz yy yz zz of K^i_j - K/3
        xx, xy, xz, yy, yz, zz = A
        tr2 = xx ** 2 + yy ** 2 + zz ** 2 + 2 * (xy ** 2 + xz ** 2 + yz ** 2)
        det = xx * (yy * zz - yz ** 2) - xy * (xy * zz - yz * xz) + xz * (xy * yz - yy * xz)
        d = np.sign(det) * np.sqrt(1.5 * tr2)
        KL[sl] = K / 3 + 2 * d / 3
        KT[sl] = K / 3 - d / 3
        Kf[sl] = K
    return dict(N=N, h=h, rho_i=rho_i, KT=KT, KL=KL, K=Kf)


def masks(KT, KT_core, tol=1e-10):
    x = -KT * T_I
    core = np.abs(KT - KT_core) < tol * abs(KT_core)
    out = np.abs(x - 2 / 3) < 1e-12
    shell = ~core & ~out
    return dict(core=core, shell=shell, outside=out)


def ltb_c(KT, c, shell, nbins):
    """c of the LTB element of the same shell: 1/c linear in bn, midpoint of its extremes per bin of KT."""
    ks = KT[shell]
    inv = 1.0 / np.where(np.abs(c[shell]) > 0, c[shell], 1e-300)
    edges = np.quantile(ks, np.linspace(0, 1, nbins + 1))
    ib = np.clip(np.searchsorted(edges, ks, side="right") - 1, 0, nbins - 1)
    mx = np.full(nbins, -np.inf)
    mn = np.full(nbins, np.inf)
    np.maximum.at(mx, ib, inv)
    np.minimum.at(mn, ib, inv)
    mid = 0.5 * (mx + mn)
    cl = np.zeros_like(c)
    cl[shell] = 1.0 / mid[ib]
    return cl


# ------------------------------------------------------------------ main


def analyse_member(name, prep, dirs, nbins):
    ini = initial(prep)
    N = ini["N"]
    nc = N ** 3
    mid = N // 2
    ic = (mid * N + mid) * N + mid
    el = Element(ini["KT"], ini["rho_i"])
    KT_core = ini["KT"][ic]
    M = masks(ini["KT"], KT_core)
    cl = ltb_c(ini["KT"], el.c, M["shell"], nbins)
    # V1.0: KL predicted from (KT, rho_i) against the file's KL, and K
    rho0, K0 = el.at(T_I)
    out = dict(N=N, cells={k: int(v.sum()) for k, v in M.items()}, KT_core=float(KT_core))
    out["V1.0_KL_pred_max_over_Hi"] = float(np.max(np.abs((K0 - ini["KT"] * 2) - ini["KL"])) / HUB)
    out["V1.0_K_pred_max_over_Hi"] = float(np.max(np.abs(K0 - ini["K"])) / HUB)
    out["V1.0_rho_pred_max_rel"] = float(np.max(np.abs(rho0 / ini["rho_i"] - 1)))
    files = []
    for d in dirs:
        files += sorted(glob.glob(os.path.join(d, "szk.field.*.bin")))
    dumps = {}
    for fpath in files:
        Fd = read_field(fpath)
        tau = Fd["t"]
        key = f"{tau:.4f}"
        if key in dumps:
            continue
        t = T_I + tau
        Hb = 2.0 / (3.0 * t)
        rho_ex, K_ex = el.at(t)
        rhoL, KLtb = el.at(t, c=cl)
        Kc = np.asarray(Fd["Khat"]) + 2 * np.asarray(Fd["Theta"])
        E = np.asarray(Fd["E"], dtype=float)
        eK = np.abs(Kc - K_ex) / Hb
        eE = np.abs(E - rho_ex) / rho_ex
        sigK = np.abs(K_ex - KLtb) / Hb
        sigr = np.abs(rho_ex - rhoL) / rho_ex
        row = dict(tau=tau, file=fpath, nonfinite=int((~np.isfinite(Kc)).sum()),
                   alpha_dev_max=float(np.nanmax(np.abs(np.asarray(Fd["alpha"]) - 1))))
        for rn, m in M.items():
            v = eK[m]
            row[rn] = dict(K_rms=float(np.sqrt(np.nanmean(v ** 2))), K_max=float(np.nanmax(v)),
                           E_rms=float(np.sqrt(np.nanmean(eE[m] ** 2))), E_max=float(np.nanmax(eE[m])))
        row["shell"]["signal_K_max"] = float(np.max(sigK[M["shell"]]))
        row["shell"]["signal_rho_max"] = float(np.max(sigr[M["shell"]]))
        line = slice(ic - mid, ic - mid + N)        # x line through (j, k) = (N/2, N/2)
        row["line"] = dict(dK=((Kc - K_ex)[line] / Hb).tolist(), sig=((K_ex - KLtb)[line] / Hb).tolist())
        dumps[key] = row
        print(f"{name} tau={tau:8.4f} shell K rms={row['shell']['K_rms']:.4g} max={row['shell']['K_max']:.4g} "
              f"signal={row['shell']['signal_K_max']:.4g} core K rms={row['core']['K_rms']:.4g}", flush=True)
    out["dumps"] = dumps
    return out


def stops(dirs):
    """Where a member stops: guard file, last time of the history."""
    out = {}
    for d in dirs:
        g = os.path.join(d, "szk.guard.txt")
        if os.path.isfile(g):
            with open(g) as f:
                out["guard"] = f.readline().strip()
        h = os.path.join(d, "szk.nrpic.hst")
        if os.path.isfile(h):
            last = None
            with open(h) as f:
                for ln in f:
                    if ln.startswith("#") or not ln.strip():
                        continue
                    last = ln
            if last is not None:
                out.setdefault("hst_last_time", [])
                out["hst_last_time"].append(float(last.split()[0]))
    return out


def figure(res, path):
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    a = fs.inch_axes(fig, 0.6, 0.45, 3.3, 2.35)
    b = fs.inch_axes(fig, 4.55, 0.45, 3.3, 2.35)
    cols = {"N64": fs.PAL["yellow"], "N128": fs.PAL["orange"], "N256": fs.PAL["red"]}
    for name, m in res["members"].items():
        ts = sorted(m["dumps"].values(), key=lambda r: r["tau"])
        ts = [r for r in ts if r["tau"] > 0]
        a.semilogy([r["tau"] for r in ts], [r["shell"]["K_rms"] for r in ts], "o-", color=cols[name], label=f"{name} rms")
        a.semilogy([r["tau"] for r in ts], [r["shell"]["K_max"] for r in ts], "s--", color=cols[name], mfc="none",
                   label=f"{name} max")
    m = res["members"]["N256"]
    ts = sorted([r for r in m["dumps"].values() if r["tau"] > 0], key=lambda r: r["tau"])
    a.semilogy([r["tau"] for r in ts], [r["shell"]["signal_K_max"] for r in ts], "-", color=fs.PAL["blue"], lw=2,
               label="Szekeres$-$LTB (max)")
    a.set_xlabel(r"$\tau$")
    a.set_ylabel(r"shell $|K-K_{\rm ex}|/H(\tau)$")
    a.legend(fontsize=6, ncol=2, loc="lower right")
    # line through the centre at tau = 20, scaled by 16 per halving (fourth order)
    for name, m in res["members"].items():
        r = m["dumps"].get("20.0000")
        if r is None:
            continue
        N = m["N"]
        h = L / N
        x = -L / 2 + (np.arange(N) + 0.5) * h
        scale = {"N64": 1.0, "N128": 16.0, "N256": 256.0}[name]
        b.plot(x, np.array(r["line"]["dK"]) * scale, color=cols[name], label=f"{name} $\\times${scale:g}")
    r = res["members"]["N256"]["dumps"].get("20.0000")
    if r is not None:
        N = res["members"]["N256"]["N"]
        x = -L / 2 + (np.arange(N) + 0.5) * (L / N)
        b.plot(x, np.array(r["line"]["sig"]) * 0.1, color=fs.PAL["blue"], lw=1, ls=":", label="signal $\\times 0.1$")
    b.set_xlim(-7, 7)
    b.set_xlabel(r"$x$ (line $y=z=h/2$)")
    b.set_ylabel(r"$(K-K_{\rm ex})/H$ at $\tau=20$, scaled")
    b.legend(fontsize=6, loc="lower left")
    return fs.save(fig, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--prep", required=True)
    ap.add_argument("--member", action="append", default=[], help="NAME=DIR[,DIR2]")
    ap.add_argument("--nbins", type=int, default=0, help="bins of KT for the LTB element (0: N^3/2000, >= 60)")
    ap.add_argument("--test-only", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    test = test_closed_form()
    print("closed form against the element ODEs: worst", test["worst"], "passed", test["passed"], flush=True)
    res = dict(test=test, members={})
    if not a.test_only:
        for spec in a.member:
            name, dl = spec.split("=", 1)
            dirs = dl.split(",")
            N = int(name[1:])
            nb = a.nbins or max(60, N ** 3 // 20000)
            m = analyse_member(name, os.path.join(a.prep, name), dirs, nb)
            m["stops"] = stops(dirs)
            m["nbins"] = nb
            res["members"][name] = m
        # orders between successive members at the same tau
        names = [n for n in ("N64", "N128", "N256") if n in res["members"]]
        orders = {}
        for n1, n2 in zip(names[:-1], names[1:]):
            d1, d2 = res["members"][n1]["dumps"], res["members"][n2]["dumps"]
            for k in sorted(set(d1) & set(d2)):
                if float(k) == 0:
                    continue
                o = {}
                for q in ("K_rms", "E_rms", "K_max"):
                    e1, e2 = d1[k]["shell"][q], d2[k]["shell"][q]
                    o[q] = math.log2(e1 / e2) if e1 > 0 and e2 > 0 and math.isfinite(e1) and math.isfinite(e2) else None
                ec1, ec2 = d1[k]["core"]["K_rms"], d2[k]["core"]["K_rms"]
                o["core_K_rms"] = math.log2(ec1 / ec2) if ec1 > 0 and ec2 > 0 else None
                orders[f"{n1}->{n2} tau={float(k):g}"] = o
        res["orders"] = orders
        if all(n in res["members"] for n in ("N64", "N128", "N256")):
            res["figure"] = figure(res, os.path.join(a.out, "fig_szk_verify"))
    for m in res["members"].values():
        for r in m["dumps"].values():
            r.pop("line", None) if os.environ.get("SZK_DROP_LINES") else None
    with open(os.path.join(a.out, "szk_verify.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res.get("orders", {}), indent=1))


if __name__ == "__main__":
    main()
