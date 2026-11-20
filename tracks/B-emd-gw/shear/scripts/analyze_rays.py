"""Observable of the shearing-dust test from one AthenaK run (SPEC.md sections 4-5):
cos(theta) between the rays from A and B at the observer O, by shooting over the two fans
of null particles, with the parallel transport of the earlier arrival along the
observer's worldline (draft.tex:541-552) and gamma^ij at the later arrival.

    python3 analyze_rays.py RUNDIR [--plot]

RUNDIR holds ic/meta.json and the AthenaK files shear.traj.bin, shear.trajmet.bin,
shear.cstat.hst. Writes RUNDIR/rays.json (and RUNDIR/rays.{png,pdf} with --plot).
Also reported: conservation of k_x, k_z of the rays and u_x of the tracers (x, z are
Killing), the observer's position, gamma_xy and alpha at O against the linear solution,
and the constraint statistics.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
sys.path.insert(0, HERE)
import shear_ref as sr  # noqa: E402

SYM = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))


def read_history(path):
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("# [1]="):
                names = [w.split("=")[1] for w in line[1:].split()]
                break
    a = np.loadtxt(path, ndmin=2)
    return {n: a[:, i] for i, n in enumerate(names)}


def load_tracks(rundir, base="shear"):
    tr = np.fromfile(os.path.join(rundir, base + ".traj.bin")).reshape(-1, 8)
    tm = np.fromfile(os.path.join(rundir, base + ".trajmet.bin")).reshape(-1, 17)
    n = min(len(tr), len(tm))
    tr, tm = tr[:n], tm[:n]
    assert np.array_equal(tr[:, :2], tm[:, :2])
    tags = np.unique(tr[:, 1].astype(int))
    out = {}
    for tg in tags:
        sel = tr[:, 1].astype(int) == tg
        a, b = tr[sel], tm[sel]
        t, idx = np.unique(a[:, 0], return_index=True)   # one record per time
        a, b = a[idx], b[idx]
        g = np.empty((len(t), 3, 3))
        for q, (i, j) in enumerate(SYM):
            g[:, i, j] = b[:, 6 + q]
            g[:, j, i] = b[:, 6 + q]
        out[int(tg)] = {"t": t, "x": a[:, 2:5], "k": a[:, 5:8], "alpha": b[:, 2],
                        "beta": b[:, 3:6], "g": g, "tau": b[:, 12], "E": b[:, 13],
                        "S": b[:, 14:17]}
    return out


def unwrap(x, L):
    d = np.diff(x, axis=0)
    jumps = np.where(d < -0.5*L, 1.0, np.where(d > 0.5*L, -1.0, 0.0))
    return x + L*np.concatenate([np.zeros((1,) + x.shape[1:]), np.cumsum(jumps, axis=0)])


def lagrange(xs, ys, x):
    """Lagrange interpolation through the points xs (n,), ys (n, ...) at x."""
    out = 0.0
    for i in range(len(xs)):
        w = 1.0
        for j in range(len(xs)):
            if j != i:
                w *= (x - xs[j])/(xs[i] - xs[j])
        out = out + w*ys[i]
    return out


def root_cubic(xs, fs):
    """root of the cubic through 4 points (xs increasing in f), by bisection + Newton."""
    lo, hi = xs[1], xs[2]
    flo = lagrange(xs, fs, lo)
    for _ in range(200):
        mid = 0.5*(lo + hi)
        fm = lagrange(xs, fs, mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
        if hi - lo <= 1e-15*max(abs(lo), abs(hi), 1e-300):
            break
    return 0.5*(lo + hi)


def crossing(tk, axis, L):
    """Time, position, momentum and metric of a ray when its unwrapped coordinate along
    'axis' passes L (cubic interpolation in time through four records)."""
    t = tk["t"]
    x = unwrap(tk["x"], L)
    f = x[:, axis] - L
    i = np.flatnonzero((f[:-1] < 0.0) & (f[1:] >= 0.0))
    if len(i) == 0:
        return None
    i = int(i[0])
    sl = slice(max(i - 1, 0), max(i - 1, 0) + 4)
    ts, fs_ = t[sl], f[sl]
    if len(ts) < 4:
        return None
    tc = root_cubic(ts, fs_) if fs_[1] < 0.0 <= fs_[2] else None
    if tc is None:
        tc = ts[1] - fs_[1]*(ts[2] - ts[1])/(fs_[2] - fs_[1])
    return {"t": float(tc), "x": lagrange(ts, x[sl], tc), "k": lagrange(ts, tk["k"][sl], tc),
            "g": lagrange(ts, tk["g"][sl], tc)}


def shoot(fan, cross, axis_t):
    """Interpolates the fan to zero miss: returns the launch slope, arrival time and k at
    the root, from the cubic through the four rays around the sign change, and the same
    from the quadratic through three (as an interpolation error estimate)."""
    s = np.array(fan)
    miss = np.array([c["x"][axis_t] if c is not None else np.nan for c in cross])
    ok = np.isfinite(miss)
    s, miss = s[ok], miss[ok]
    cr = [c for c in cross if c is not None]
    order = np.argsort(s)
    s, miss = s[order], miss[order]
    cr = [cr[i] for i in order]
    sg = np.sign(miss)
    i = np.flatnonzero(sg[:-1] != sg[1:])
    if len(i) == 0:
        return {"ok": False, "s": s.tolist(), "miss": miss.tolist()}
    i = int(i[0])
    j0 = min(max(i - 1, 0), len(s) - 4)
    js = list(range(j0, j0 + 4))
    ss, ms = s[js], miss[js]
    # the cubic miss(s); root between s[i] and s[i+1]
    lo, hi = s[i], s[i + 1]
    flo = lagrange(ss, ms, lo)
    for _ in range(200):
        mid = 0.5*(lo + hi)
        fm = lagrange(ss, ms, mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    sr_ = 0.5*(lo + hi)
    tt = np.array([cr[j]["t"] for j in js])
    kk = np.array([cr[j]["k"] for j in js])
    # quadratic estimate (three rays nearest the root)
    jq = sorted(js, key=lambda j: abs(s[j] - sr_))[:3]
    jq.sort()
    sq = s[jq]
    lo, hi = s[i], s[i + 1]
    flo = lagrange(sq, miss[jq], lo)
    for _ in range(200):
        mid = 0.5*(lo + hi)
        fm = lagrange(sq, miss[jq], mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    sq_ = 0.5*(lo + hi)
    return {"ok": True, "s_root": float(sr_), "t": float(lagrange(ss, tt, sr_)),
            "k": lagrange(ss, kk, sr_), "s_root_quad": float(sq_),
            "k_quad": lagrange(sq, np.array([cr[j]["k"] for j in jq]), sq_),
            "t_quad": float(lagrange(sq, np.array([cr[j]["t"] for j in jq]), sq_)),
            "s": s.tolist(), "miss": miss.tolist()}


def transport(k, t1, t2, obs):
    """Parallel transport of the covector k along the observer at rest at O from t1 to
    t2: d k_i/dt = -alpha K^j_i k_j = (1/2) (gamma^-1 d_t gamma)_ji k_j (draft.tex:551)."""
    if t2 <= t1:
        return np.array(k, float)
    t = obs["t"]
    g = obs["g"]
    dg = np.gradient(g, t, axis=0)
    gi = np.linalg.inv(g)
    M = 0.5*np.einsum("tjl,tli->tji", gi, dg)
    n = max(int(np.ceil((t2 - t1)/(0.1*np.min(np.diff(t))))), 4)
    tt = np.linspace(t1, t2, n + 1)

    def Mat(tq):
        return np.array([[np.interp(tq, t, M[:, a, b]) for b in range(3)] for a in range(3)])
    kk = np.array(k, float)
    for q in range(n):
        h = tt[q + 1] - tt[q]
        f = lambda tq, kv: Mat(tq).T @ kv
        k1 = f(tt[q], kk)
        k2 = f(tt[q] + 0.5*h, kk + 0.5*h*k1)
        k3 = f(tt[q] + 0.5*h, kk + 0.5*h*k2)
        k4 = f(tt[q] + h, kk + h*k3)
        kk = kk + h*(k1 + 2*k2 + 2*k3 + k4)/6.0
    return kk


def interp_series(t, arr, tq):
    i = int(np.clip(np.searchsorted(t, tq) - 2, 0, len(t) - 4))
    return lagrange(t[i:i + 4], arr[i:i + 4], tq)


def cos_theta(kA, kB, g):
    gi = np.linalg.inv(g)
    return float(kA @ gi @ kB/np.sqrt((kA @ gi @ kA)*(kB @ gi @ kB)))


def analyze(rundir, plot=False):
    with open(os.path.join(rundir, "ic", "meta.json")) as f:
        meta = json.load(f)
    with open(os.path.join(rundir, "case.json")) as f:
        case = json.load(f)
    L, b = meta["L"], meta["b"]
    tk = load_tracks(rundir)
    obs = tk[0]
    res = {"name": case["row"]["name"], "beta": meta["beta"], "HL": meta["HL"],
           "b": b, "ny": meta["ny"], "ppc_y": meta["ppc_y"],
           "lapse": float(case["row"].get("lapse", 1.0/3.0)),
           "cfl": float(case["row"].get("cfl", 0.25)), "cos_lin": meta["cos_lin_closed"]}
    crA = [crossing(tk[tg], 0, L) for tg in meta["rays_A_tags"]]
    crB = [crossing(tk[tg], 1, L) for tg in meta["rays_B_tags"]]
    shA = shoot(meta["fan_A"], crA, 1)
    shB = shoot(meta["fan_B"], crB, 0)
    res["shoot_A"] = {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                      for k, v in shA.items()}
    res["shoot_B"] = {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                      for k, v in shB.items()}
    if shA["ok"] and shB["ok"]:
        out = {}
        for tag, kA, kB, tA, tB in (("cubic", shA["k"], shB["k"], shA["t"], shB["t"]),
                                    ("quad", shA["k_quad"], shB["k_quad"], shA["t_quad"],
                                     shB["t_quad"])):
            t1, t2 = min(tA, tB), max(tA, tB)
            if tA <= tB:
                kA2, kB2 = transport(kA, tA, tB, obs), np.array(kB)
            else:
                kA2, kB2 = np.array(kA), transport(kB, tB, tA, obs)
            g2 = interp_series(obs["t"], obs["g"], t2)
            ct = cos_theta(kA2, kB2, g2)
            ct_nt = cos_theta(np.array(kA), np.array(kB), g2)
            out[tag] = {"cos": ct, "cos_no_transport": ct_nt, "t_A": tA, "t_B": tB}
        res["cos"] = out["cubic"]["cos"]
        res["Delta"] = res["cos"]/res["cos_lin"] - 1.0
        res["Delta_quad"] = out["quad"]["cos"]/res["cos_lin"] - 1.0
        res["Delta_no_transport"] = out["cubic"]["cos_no_transport"]/res["cos_lin"] - 1.0
        res["t_A"], res["t_B"] = out["cubic"]["t_A"], out["cubic"]["t_B"]
        res["delay"] = res["t_B"] - res["t_A"]
        res["slope_A"], res["slope_B"] = shA["s_root"], shB["s_root"]
        res["slope_A_lin"], res["slope_B_lin"] = meta["slope_A_lin"], meta["slope_B_lin"]
    # exact conservation: k_x, k_z of every ray, u_x, u_z of the tracers
    dk = 0.0
    for tg in meta["rays_A_tags"] + meta["rays_B_tags"]:
        k = tk[tg]["k"]
        launched = tk[tg]["tau"] > 0.0
        if launched.sum() > 1:
            kk = k[launched]
            nrm = np.abs(kk).max()
            dk = max(dk, float(np.abs(kk[:, [0, 2]] - kk[0, [0, 2]]).max()/nrm))
    res["ray_kx_kz_drift"] = dk
    du = 0.0
    for tg in meta["tracer_tags"]:
        u = tk[tg]["k"]
        scale = max(np.abs(u[0, 0]), 1e-300)
        du = max(du, float(np.abs(u[:, 0] - u[0, 0]).max()/scale) if u[0, 0] != 0 else
                 float(np.abs(u[:, 0]).max()))
        du = max(du, float(np.abs(u[:, 2]).max()))
    res["tracer_ux_uz_drift"] = du
    res["observer_max_offset"] = float(np.abs(obs["x"]).max())
    res["observer_beta_max"] = float(np.abs(obs["beta"]).max())
    # metric at O against the linear solution: conformal time from alpha / a_O
    tO = obs["t"]
    aO = np.linalg.det(obs["g"])**(1.0/6.0)
    rate = obs["alpha"]/aO
    tau = 2.0 + np.concatenate([[0.0], np.cumsum(0.5*(rate[1:] + rate[:-1])*np.diff(tO))])
    a_bg = sr.scale_factor(tau)
    hxy = obs["g"][:, 0, 1]/aO**2
    hl = sr.h_lin(tau, 0.0, b, L)
    t_end = max(res.get("t_A", tO[-1]), res.get("t_B", tO[-1]))
    sel = (tO <= t_end) & (tO > 0)
    scale = np.abs(hl[sel]).max() if sel.any() else 1.0
    res["gxy_O_maxrel_dev"] = float(np.abs(hxy[sel] - hl[sel]).max()/scale) if sel.any() else None
    res["aO_over_abg_maxdev"] = float(np.abs(aO[sel]/a_bg[sel] - 1.0).max()) if sel.any() else None
    res["alpha_over_aO_maxdev"] = float(np.abs(obs["alpha"][sel]/aO[sel] - 1.0).max()) \
        if sel.any() else None
    res["tau_end"] = float(np.interp(t_end, tO, tau))
    res["a_end"] = float(np.interp(t_end, tO, aO))
    # constraints
    cs = read_history(os.path.join(rundir, "shear.cstat.hst"))
    i0 = 0
    sel = cs["time"] <= t_end
    res["cstat_t0"] = {k: float(cs[k][i0]) for k in ("Hr_mean", "Mr_mean", "H_mean",
                                                     "M_mean", "Hr_max", "Mr_max")}
    res["cstat_max_to_arrival"] = {k: float(cs[k][sel].max()) for k in
                                   ("Hr_mean", "Mr_mean", "H_mean", "M_mean")}
    res["cstat_series"] = {"t": cs["time"].tolist(), "Hr_mean": cs["Hr_mean"].tolist(),
                           "Mr_mean": cs["Mr_mean"].tolist(), "E_max": cs["E_max"].tolist(),
                           "E_min": cs["E_min"].tolist()}
    res["observer_series"] = {"t": tO[::4].tolist(), "tau": tau[::4].tolist(),
                              "hxy": hxy[::4].tolist(), "hxy_lin": hl[::4].tolist(),
                              "aO": aO[::4].tolist(), "alpha": obs["alpha"][::4].tolist()}
    with open(os.path.join(rundir, "rays.json"), "w") as f:
        json.dump(res, f, indent=1)
    if plot:
        make_plot(rundir, res)
    return res


def make_plot(rundir, res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.7))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.88, wspace=0.38)
    for key, col, lab in (("shoot_A", fs.PAL["blue"], "fan A"),
                          ("shoot_B", fs.PAL["red"], "fan B")):
        sh = res[key]
        axs[0].plot(sh["s"], sh["miss"], "o-", color=col, ms=3, label=lab)
        if sh.get("ok"):
            axs[0].axvline(sh["s_root"], color=col, lw=0.8, ls=":")
    axs[0].axhline(0.0, **fs.THIN)
    axs[0].set_xlabel("launch slope $s$")
    axs[0].set_ylabel("miss at the crossing")
    axs[0].legend(fontsize=7)
    ob = res["observer_series"]
    axs[1].plot(ob["tau"], ob["hxy"], color=fs.PAL["red"], label="code, at O")
    axs[1].plot(ob["tau"], ob["hxy_lin"], **fs.GUIDE, label="linear")
    axs[1].set_xlabel(r"conformal time $\tau$")
    axs[1].set_ylabel(r"$\gamma_{xy}/a_O^2$ at O")
    axs[1].legend(fontsize=7)
    cs = res["cstat_series"]
    axs[2].semilogy(cs["t"], np.maximum(cs["Hr_mean"], 1e-18), color=fs.PAL["blue"],
                    label="Hr mean")
    axs[2].semilogy(cs["t"], np.maximum(cs["Mr_mean"], 1e-18), color=fs.PAL["red"],
                    label="Mr mean")
    for tt in (res.get("t_A"), res.get("t_B")):
        if tt is not None:
            axs[2].axvline(tt, **fs.MASK_LINE)
    axs[2].set_xlabel("code time $t$")
    axs[2].set_ylabel("relative constraint")
    axs[2].legend(fontsize=7)
    d = res.get("Delta")
    fig.suptitle(f"{res['name']}: beta = {res['beta']}, HL = {res['HL']}, N_y = {res['ny']}"
                 + (f", Delta = {d:+.3e}" if d is not None else ""), fontsize=9)
    fs.save(fig, os.path.join(rundir, "rays"))


if __name__ == "__main__":
    r = analyze(sys.argv[1], plot="--plot" in sys.argv)
    keys = ("name", "cos", "cos_lin", "Delta", "Delta_quad", "Delta_no_transport", "t_A",
            "t_B", "ray_kx_kz_drift", "tracer_ux_uz_drift", "gxy_O_maxrel_dev",
            "alpha_over_aO_maxdev", "a_end", "cstat_t0", "cstat_max_to_arrival")
    print(json.dumps({k: r.get(k) for k in keys}, indent=1))
