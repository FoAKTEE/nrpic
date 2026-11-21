"""P0L (spherical periodic peak, relaxed 1+log lapse) against its exact LTB reference, in
invariants (package periodic_threshold, JOURNAL.md predictions P1-P4).

    compare_ltb.py --run DIR [--run DIR ...] --ref REFDIR --out DIR [--label P0L]

DIR: AthenaK run directory (segments of one run in time order); REFDIR: output of
ltb_reference.py (ltb_reference.json, .npz): reference B, the exact spherical future of the
code's own initial slice, shell by shell (M, E, age0 per tracked tag).

Measured:
  - per tracked particle (tags 1..316 of track_select.py; tag 0 sits on the centre) the
    areal radius R = r sqrt(g_T) of the round sphere through it, from the metric at the
    particle (peak.trajmet.bin), against its own proper time tau (same file), compared
    with the exact radius of its own shell: eps = R/R_B(tau) - 1;
  - turnaround: largest R and its tau (parabola through the three records around it)
    against tau_ta and R_max of B;
  - trapping: the proper time at which R falls through 2 M_B against tau_ah of B;
  - apparent-horizon finder (peak.horizon_summary_0.txt, status file): time and mass of
    every found surface against the exact mass expected on the same slice, M_B of the
    outermost axis shell whose own proper time on that slice has passed its tau_ah;
  - background: the lapse on the y line at |y| > 7 against the homogeneous solution of the
    relaxed lapse (R1, ltb_reference.npz), central and smallest lapse, constraint norms.
Readers read_traj_many, radial_tangential, areal_radius and read_horizon are copied from
tracks/A-emd-pbh/runs_ball/common.py at commit 9cddbfc6 (base name and columns as there).
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
import figstyle as fs                    # noqa: E402
import ltbref as R                       # noqa: E402
import analyse_scouting as AS            # noqa: E402  (read_cols, read_tab)

T_I = 2.0 / 3.0
BASE = "peak"


def fnum(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


# ------------------------------------------------- copied from runs_ball/common.py @ 9cddbfc6
def read_traj_many(dirs, base=BASE):
    """Tracked particles over one or several run directories (segments of one run, in
    time order). Records of 8 (traj.bin) and 17 (trajmet.bin) doubles; a particle missing
    from a record (removed) gets NaN. Returns dict(time[nt], tag[np], x[nt,np,3],
    u[nt,np,3], alpha, beta[...,3], g[...,6], tau, E)."""
    A, B = [], []
    for d in dirs:
        fa, fb = os.path.join(d, base + ".traj.bin"), os.path.join(d, base + ".trajmet.bin")
        if not (os.path.exists(fa) and os.path.exists(fb)):
            continue
        a = np.fromfile(fa, dtype="<f8")
        b = np.fromfile(fb, dtype="<f8")
        na, nb = len(a) // 8, len(b) // 17
        n = min(na, nb)
        A.append(a[:8 * n].reshape(n, 8))
        B.append(b[:17 * n].reshape(n, 17))
    a = np.concatenate(A)
    b = np.concatenate(B)
    key = np.round(a[:, 0], 12) * 1e7 + a[:, 1]
    _, last = np.unique(key[::-1], return_index=True)
    sel = len(key) - 1 - last
    a, b = a[sel], b[sel]
    times = np.unique(a[:, 0])
    tags = np.unique(a[:, 1]).astype(int)
    it = np.searchsorted(times, a[:, 0])
    ip = np.searchsorted(tags, a[:, 1].astype(int))
    nt, npart = len(times), len(tags)

    def grid(cols, src):
        out = np.full((nt, npart) + ((len(cols),) if len(cols) > 1 else ()), np.nan)
        out[it, ip] = src[:, cols] if len(cols) > 1 else src[:, cols[0]]
        return out
    return dict(time=times, tag=tags, x=grid([2, 3, 4], a), u=grid([5, 6, 7], a),
                alpha=grid([2], b), beta=grid([3, 4, 5], b), g=grid(list(range(6, 12)), b),
                tau=grid([12], b), E=grid([13], b))


def radial_tangential(x, S):
    r = np.sqrt(np.sum(x * x, axis=-1))
    n = x / r[..., None]
    xx, xy, xz, yy, yz, zz = (S[..., i] for i in range(6))
    A = (xx * n[..., 0] ** 2 + yy * n[..., 1] ** 2 + zz * n[..., 2] ** 2
         + 2.0 * (xy * n[..., 0] * n[..., 1] + xz * n[..., 0] * n[..., 2]
                  + yz * n[..., 1] * n[..., 2]))
    B = 0.5 * (xx + yy + zz - A)
    return A, B, r, n


def areal_radius(x, g):
    A, B, r, _ = radial_tangential(x, g)
    return r * np.sqrt(B), r, A


def read_horizon(dirs, base=BASE, n=0):
    """Rows (iter, time, mass, Sx, Sy, Sz, S, area, hrms, hmean, meanradius, minradius) with
    a finite mass."""
    rows = []
    for d in dirs:
        f = os.path.join(d, f"{base}.horizon_summary_{n}.txt")
        if os.path.exists(f):
            for line in open(f):
                if line.startswith("#") or not line.strip():
                    continue
                v = [float(t) for t in line.split()]
                if len(v) >= 12 and np.isfinite(v[2]):
                    rows.append(v[:12])
    return np.array(rows) if rows else np.zeros((0, 12))
# --------------------------------------------------------------------------------------


def read_status(dirs, base=BASE, n=0):
    rows = []
    for d in dirs:
        f = os.path.join(d, f"{base}.horizon_status_{n}.txt")
        if os.path.exists(f):
            for line in open(f):
                if line.startswith("#") or not line.strip():
                    continue
                head, _, why = line.partition("#")
                v = head.split()
                rows.append(dict(cycle=int(v[0]), time=float(v[1]), found=int(v[2]),
                                 reason=int(v[3]), iters=int(v[4]), why=why.strip()))
    return rows


def parabola_max(t, y, i):
    if i <= 0 or i >= len(t) - 1:
        return t[i], y[i]
    c = np.polyfit(t[i - 1:i + 2] - t[i], y[i - 1:i + 2], 2)
    if c[0] >= 0:
        return t[i], y[i]
    tm = -c[1] / (2 * c[0])
    return t[i] + tm, np.polyval(c, tm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="P0L")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    segs = a.run
    ref = json.load(open(os.path.join(a.ref, "ltb_reference.json")))
    refz = np.load(os.path.join(a.ref, "ltb_reference.npz"))
    eps_i = float(ref["eps_i"])
    t_H = float(ref["t_H"])
    shells = {int(s["tag"]): s for s in ref["B"]["shells"]}
    res = dict(label=a.label, runs=[os.path.abspath(s) for s in segs],
               ref=os.path.abspath(a.ref))

    # ------------------------------------------------ tracked shells
    T = read_traj_many(segs)
    tags = T["tag"]
    keep = np.array([int(tg) in shells for tg in tags])
    tags = tags[keep]
    for k in ("x", "u", "alpha", "beta", "g", "tau", "E"):
        T[k] = T[k][:, keep]
    t = T["time"]
    Rc, rc, _ = areal_radius(T["x"], T["g"])
    tau = T["tau"]
    M = np.array([shells[int(tg)]["M"] for tg in tags])
    E = np.array([shells[int(tg)]["E"] for tg in tags])
    age = np.array([shells[int(tg)]["age0"] for tg in tags])
    r0 = np.array([shells[int(tg)]["r0"] for tg in tags])
    lab = np.array([shells[int(tg)]["label"] for tg in tags])
    shB = R.Shells(M, E, age)
    evB = shB.events()
    with np.errstate(invalid="ignore"):
        RB = shB.R(np.where(np.isfinite(tau), tau, 0.0))
        RB = np.where(np.isfinite(tau), RB, np.nan)
        eps = Rc / RB - 1.0
    res["traj"] = dict(n_tracked=int(len(tags)), n_records=int(len(t)), t_first=fnum(t[0]),
                       t_last=fnum(t[-1]), n_alive_last=int(np.sum(np.isfinite(Rc[-1]))))
    axes = np.isin(lab, ["+x", "-x", "+y", "-y", "+z", "-z"])
    per = []
    for j in range(len(tags)):
        ok = np.isfinite(Rc[:, j]) & np.isfinite(tau[:, j])
        d = dict(tag=int(tags[j]), label=str(lab[j]), r0=fnum(r0[j]), M_B=fnum(M[j]),
                 tau_last=fnum(tau[ok, j][-1]) if ok.any() else None,
                 t_last_alive=fnum(t[ok][-1]) if ok.any() else None)
        if ok.sum() >= 3:
            tt, RR = tau[ok, j], Rc[ok, j]
            i = int(np.argmax(RR))
            d["turned"] = bool(i < len(RR) - 1)
            if d["turned"]:
                tm, Rm = parabola_max(tt, RR, i)
                d.update(tau_ta=fnum(tm), R_max=fnum(Rm), tau_ta_B=fnum(evB["tau_ta"][j]),
                         R_max_B=fnum(evB["R_max"][j]),
                         rel_tau_ta=fnum(tm / evB["tau_ta"][j] - 1.0),
                         rel_R_max=fnum(Rm / evB["R_max"][j] - 1.0))
                below = np.flatnonzero((RR[i:] <= 2.0 * M[j]))
                if len(below):
                    k = i + below[0]
                    f = (RR[k - 1] - 2 * M[j]) / (RR[k - 1] - RR[k])
                    tr = tt[k - 1] + f * (tt[k] - tt[k - 1])
                    d.update(tau_trap=fnum(tr), tau_ah_B=fnum(evB["tau_ah"][j]),
                             rel_tau_trap=fnum(tr / evB["tau_ah"][j] - 1.0))
            pre = tt <= (d.get("tau_ta") or tt[-1])
            d["max_abs_eps_to_turnaround"] = fnum(np.nanmax(np.abs(eps[ok, j][pre])))
            d["eps_last"] = fnum(eps[ok, j][-1])
        per.append(d)
    res["shells"] = per

    # ------------------------------------------------ finder against B
    hz = read_horizon(segs)
    st = read_status(segs)
    reasons = {}
    for s in st:
        reasons[s["why"]] = reasons.get(s["why"], 0) + 1
    res["finder"] = dict(calls=len(st), found=int(len(hz)), reasons=reasons)
    ax_idx = np.flatnonzero(axes)

    def expected_mass(tc):
        """M_B of the outermost axis shell whose own proper time at coordinate time tc has
        passed its tau_ah (and the same with the code's own R <= 2 M_B)."""
        mB, mC = 0.0, 0.0
        for j in ax_idx:
            ok = np.isfinite(tau[:, j])
            if not ok.any() or tc > t[ok][-1] + 1e-9:
                # removed (excised) before tc: it was inside the trapped region
                if ok.any() and np.isfinite(evB["tau_ah"][j]) and tau[ok, j][-1] >= 0.9 * evB["tau_ah"][j]:
                    mB, mC = max(mB, M[j]), max(mC, M[j])
                continue
            tj = np.interp(tc, t[ok], tau[ok, j])
            Rj = np.interp(tc, t[ok], Rc[ok, j])
            if np.isfinite(evB["tau_ah"][j]) and tj >= evB["tau_ah"][j]:
                mB = max(mB, M[j])
            if Rj <= 2.0 * M[j] and tj > evB["tau_ta"][j]:
                mC = max(mC, M[j])
        return mB, mC
    rows = []
    for r in hz:
        mB, mC = expected_mass(r[1])
        rows.append(dict(time=fnum(r[1]), mass=fnum(r[2]), area_mass=fnum(math.sqrt(r[7] / (16 * math.pi))),
                         meanradius=fnum(r[10]), expected_M_B_clock=fnum(mB),
                         expected_M_code_R=fnum(mC)))
    res["finder"]["rows"] = rows
    if rows:
        res["finder"]["first"] = rows[0]
        res["finder"]["t_first_over_tH"] = fnum((T_I + rows[0]["time"]) / t_H)

    # ------------------------------------------------ histories and lines
    hist = {}
    for name in ("cstat", "nrpic", "region"):
        cols = None
        for d in segs:
            p = os.path.join(d, f"{BASE}.{name}.hst")
            if os.path.exists(p):
                c = AS.read_cols(p)
                cols = c if cols is None else {k: np.concatenate([cols[k], c[k]]) for k in c if k in cols}
        hist[name] = cols
    c = hist["cstat"]
    if c is not None:
        res["cstat"] = dict(t_end=fnum(c["time"][-1]), chi_min_end=fnum(c["chi_min"][-1]),
                            Hr_max_max=fnum(np.nanmax(c["Hr_max"])),
                            Hr_max_at_end=fnum(c["Hr_max"][-1]))
        for thr in (0.1, 1.0):
            i = np.flatnonzero(c["Hr_max"] > thr)
            res["cstat"][f"t_Hr_max_above_{thr:g}"] = fnum(c["time"][i[0]]) if len(i) else None
    h = hist["nrpic"]
    if h is not None:
        res["nrpic"] = {k + "_end": fnum(h[k][-1]) for k in ("time", "ncycle", "alpha_min", "np",
                                                             "n_excised", "alpha_probe") if k in h}
        for thr in (0.5, 0.3, 0.1):
            i = np.flatnonzero(h["alpha_min"] < thr)
            res["nrpic"][f"t_alpha_min_below_{thr:g}"] = fnum(h["time"][i[0]]) if len(i) else None
    g = hist["region"]
    if g is not None and "H2_in_s1" in g:
        rr = g["H2_in_s1"] / g["E2_in_s1"]
        res["region"] = dict(H2_over_E2_in_s1_max_to_t50=fnum(np.nanmax(rr[g["time"] <= 50])),
                             H2_over_E2_in_s1_end=fnum(rr[-1]), t_end=fnum(g["time"][-1]))
    # background lapse on the y line, |y| > 7, against the homogeneous relaxed-lapse solution
    bg = []
    for d in segs:
        for p in sorted(glob.glob(os.path.join(d, "tab", f"{BASE}.alpha_y.*.tab"))):
            dd = AS.read_tab(p)
            far = np.abs(dd["x2v"]) > 7.0
            if far.any():
                bg.append((dd["time"], float(np.mean(dd["z4c_alpha"][far]))))
    bg = np.array(sorted(set(bg))) if bg else np.zeros((0, 2))
    if len(bg):
        aref = np.interp(bg[:, 0], refz["t_bg"], refz["alpha_bg"])
        dev = bg[:, 1] / aref - 1.0
        res["background_lapse"] = dict(
            max_abs_rel_dev_t_gt_1=fnum(np.max(np.abs(dev[bg[:, 0] > 1.0]))) if np.any(bg[:, 0] > 1) else None,
            at=[dict(t=fnum(tt), alpha=fnum(al), ref=fnum(ar)) for tt, al, ar in
                zip(bg[::max(1, len(bg) // 8), 0], bg[::max(1, len(bg) // 8), 1],
                    aref[::max(1, len(bg) // 8)])])
    # cost
    cost = []
    for d in segs:
        for lg in sorted(glob.glob(os.path.join(d, "athena.*.log"))) or [os.path.join(d, "athena.log")]:
            if os.path.exists(lg):
                txt = open(lg, errors="replace").read()
                for key in ("cpu time used", "MeshBlock-cycles", "Terminating"):
                    for ln in txt.splitlines():
                        if key in ln:
                            cost.append(ln.strip())
    res["log_lines"] = cost[-8:]
    with open(os.path.join(a.out, f"compare_ltb_{a.label}.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ------------------------------------------------ figures
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 9.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.06, top=0.98, wspace=0.3, hspace=0.33)
    pick_r0 = [0.3, 0.6, 0.91, 1.21, 1.52, 1.83, 2.15, 2.46]
    sel = []
    for rr in pick_r0:
        cand = np.flatnonzero((lab == "+x"))
        if len(cand):
            sel.append(cand[np.argmin(np.abs(r0[cand] - rr))])
    cc = fs.series_colors(len(sel))
    ax1 = fig.add_subplot(3, 2, 1)
    ax2 = fig.add_subplot(3, 2, 2)
    taug = np.linspace(0, np.nanmax(tau) if np.isfinite(tau).any() else 1.0, 600)
    for j, col in zip(sel, cc):
        ok = np.isfinite(Rc[:, j]) & np.isfinite(tau[:, j])
        ax1.plot(tau[ok, j], Rc[ok, j], color=col, lw=1.3,
                 label=f"r0={r0[j]:.2f}, M={M[j]:.3g}")
        RBg = R.Shells(M[j:j + 1], E[j:j + 1], age[j:j + 1]).R(taug[:, None])[:, 0]
        ax1.plot(taug, RBg, color=col, lw=0.9, ls="--")
        ax1.axhline(2 * M[j], color=col, lw=0.5, ls=":")
        ax2.plot(tau[ok, j], eps[ok, j], color=col, lw=1.2)
    ax1.set_xlabel(r"own proper time $\tau$")
    ax1.set_ylabel(r"areal radius $R$")
    ax1.set_title(r"solid: code; dashed: exact B; dotted: $2M$", fontsize=7)
    ax1.legend(fontsize=6.5, loc="upper right")
    ax2.axhline(0, **fs.THIN)
    ax2.set_xlabel(r"own proper time $\tau$")
    ax2.set_ylabel(r"$R/R_B - 1$ (+x shells)")
    lim = np.nanmax(np.abs(eps[:, sel])) if np.isfinite(eps[:, sel]).any() else 0.1
    ax2.set_ylim(-min(1.0, 1.1 * lim), min(1.0, 1.1 * lim))
    # (c) turnaround and trapping, all shells, against B
    ax3 = fig.add_subplot(3, 2, 3)
    for key, keyB, mk, col, name in (("tau_ta", "tau_ta_B", "o", fs.SERIES[0], "turnaround"),
                                     ("tau_trap", "tau_ah_B", "s", fs.SERIES[1], "R = 2M")):
        xs = [d["r0"] for d in per if d.get(key) is not None]
        ys = [d[key] / d[keyB] - 1.0 for d in per if d.get(key) is not None]
        ax3.plot(xs, ys, mk, ms=3, color=col, ls="none", label=name)
    ax3.axhline(0, **fs.THIN)
    ax3.set_xlabel(r"initial coordinate radius $r_0$")
    ax3.set_ylabel(r"$\tau_{\rm code}/\tau_B - 1$")
    ax3.legend(fontsize=7)
    # (d) horizon mass against coordinate time
    ax4 = fig.add_subplot(3, 2, 4)
    tg = np.linspace(t[0], t[-1], 300)
    eb = np.array([expected_mass(x) for x in tg]) if len(ax_idx) else np.zeros((len(tg), 2))
    ax4.plot(tg, eb[:, 0], color=fs.SERIES[0], lw=1.2, label=r"B: shells past $\tau_{AH}$")
    ax4.plot(tg, eb[:, 1], color=fs.SERIES[2], lw=1.0, ls="--", label=r"code shells with $R\leq 2M_B$")
    if len(hz):
        ax4.plot(hz[:, 1], hz[:, 2], "v", ms=3.5, color=fs.SERIES[1], label="finder")
    ax4.set_xlabel("coordinate time t")
    ax4.set_ylabel("horizon mass")
    ax4.legend(fontsize=7, loc="upper left")
    # (e) lapse
    ax5 = fig.add_subplot(3, 2, 5)
    if h is not None:
        ax5.plot(h["time"], h["alpha_min"], color=fs.SERIES[1], lw=1.2, label=r"$\alpha_{\min}$")
        if "alpha_probe" in h:
            ax5.plot(h["time"], h["alpha_probe"], color=fs.SERIES[3], lw=1.0, label=r"$\alpha$ at centre")
    if len(bg):
        ax5.plot(bg[:, 0], bg[:, 1], "o", ms=2.5, color=fs.SERIES[0], label=r"$\alpha$, $|y|>7$")
        ax5.plot(refz["t_bg"], refz["alpha_bg"], color=fs.SERIES[0], lw=0.8, ls="--",
                 label="homogeneous (R1)")
    ax5.set_xlim(t[0], max(t[-1], 1.0))
    ax5.set_xlabel("coordinate time t")
    ax5.set_ylabel("lapse")
    ax5.legend(fontsize=7)
    # (f) constraints
    ax6 = fig.add_subplot(3, 2, 6)
    if c is not None:
        ax6.semilogy(c["time"], np.maximum(c["Hr_max"], 1e-12), color=fs.SERIES[1], label=r"$H_r$ max")
        ax6.semilogy(c["time"], np.maximum(c["Hr_mean"], 1e-12), color=fs.SERIES[1], ls="--",
                     label=r"$H_r$ mean")
    if g is not None and "H2_in_s1" in g:
        ax6.semilogy(g["time"], g["H2_in_s1"] / g["E2_in_s1"], color=fs.SERIES[0],
                     label=r"$\|H\|/\|16\pi E\|$, $r<r_m$")
    ax6.set_xlabel("coordinate time t")
    ax6.set_ylabel("constraint")
    ax6.legend(fontsize=7)
    fs.save(fig, os.path.join(a.out, f"fig_compare_ltb_{a.label}"))
    print(json.dumps({k: v for k, v in res.items() if k != "shells"}, indent=1)[:6000])
    for d in per:
        if d["label"] == "+x":
            print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()})


if __name__ == "__main__":
    main()
