#!/usr/bin/env python3
"""Calculation C of the scope review: what Claim D's statistic q measures, on the exact LTB solution.

Exact shells: E = -M/R0 (M = 1), R_max = m R0, cycloid R = (R_max/2)(1 - cos eta),
tau = A [(eta - sin eta) - (eta0 - sin eta0)], A = (R_max/2) sqrt(R_max / (2 m)), from the expanding start R0.
Inputs (read only): labels and rest masses of the data run, FK's snapshots (tags and per-particle proper
time, docs/FORMATS.md line 123), FK's finder summary, the verifier's measured lead (v6_tracers.json).
Usage: dress_model.py OUTDIR
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

S = Path("/data/haiyangw/nrpic/scratch/D-bh-dress")
DATA = S / "D-20261121-203042-82deeec"
FK = S / "D-20261123-022725-a553496"
V6 = S / "D-20261126-062436-72c04d3" / "v6_tracers.json"
NTRACER = 140


def cycloid_consts(R0, m):
    Rmax = m * R0
    A = 0.5 * Rmax * np.sqrt(Rmax / (2.0 * m))
    eta0 = np.arccos(1.0 - 2.0 * R0 / Rmax)
    return Rmax, A, eta0


def tau_of_eta(eta, A, eta0):
    return A * ((eta - np.sin(eta)) - (eta0 - np.sin(eta0)))


def R_of_tau(tau, R0, m):
    """Areal radius at proper time tau (vectorised bisection on eta in [eta0, 2 pi))."""
    Rmax, A, eta0 = cycloid_consts(R0, m)
    lo, hi = eta0.copy(), np.full_like(eta0, 2 * np.pi)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        f = tau_of_eta(mid, A, eta0) - tau
        lo = np.where(f < 0, mid, lo)
        hi = np.where(f >= 0, mid, hi)
    eta = 0.5 * (lo + hi)
    return 0.5 * Rmax * (1 - np.cos(eta))


def tau_horizon(R0, m):
    Rmax, A, eta0 = cycloid_consts(R0, m)
    etaH = 2 * np.pi - np.arccos(1.0 - 4.0 * m / Rmax)
    return tau_of_eta(etaH, A, eta0)


def read_snapshot(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"NRPSNAP1"
        t = np.frombuffer(f.read(8), "<f8")[0]
        n = int(np.frombuffer(f.read(8), "<i8")[0])
        f.read(8)
        rec = np.frombuffer(f.read(56 * n), "<f8").reshape(n, 7)
        tags = np.frombuffer(f.read(4 * n), "<i4")
        f.read(4 * n)
        tau = np.frombuffer(f.read(8 * n), "<f8")
    return t, rec, tags, tau


def summary_mass(t):
    d = {}
    for line in open(FK / "esflk.horizon_summary_0.txt"):
        if line.startswith("#") or not line.strip():
            continue
        c = line.split()
        d[float(c[1])] = float(c[2])
    ts = np.array(sorted(d))
    return float(np.interp(t, ts, [d[x] for x in ts]))


def main():
    out = Path(sys.argv[1])
    res = {}
    lab = np.load(DATA / "esf_labels.npz")
    R0all, mall, rest = lab["R0"], lab["m_label"], lab["rest"]

    # ---- C0: closed-form test against the data maker's growth table
    csv = np.loadtxt(DATA / "esf_growth.csv", delimiter=",", skiprows=1)
    sel = csv[:, 4] > 2 * csv[:, 1] + 1e-9          # shells that start outside 2m
    tH = tau_horizon(csv[sel, 0], csv[sel, 1])
    rel = np.abs(tH / csv[sel, 2] - 1)
    res["C0"] = dict(n=int(sel.sum()), max_rel=float(rel.max()), holds=bool(rel.max() < 1e-6))
    if not res["C0"]["holds"]:
        (out / "dress_model.json").write_text(json.dumps(res, indent=1))
        print(res)
        return 1

    # ---- measured lead (M/8, N; and M/16, N) near the horizon (dtau at R = 4 M; negative = run ahead)
    v6 = json.load(open(V6))

    def lead_fn(run):
        xs, ys = [0.0], [0.0]
        for g in ("10.0", "20.0", "28.0", "36.0"):
            dd = v6[run][g]["dtau_at_R"]
            key = "4.000" if "4.000" in dd else (sorted(dd)[0] if dd else None)
            if key is None:
                continue
            xs.append(float(g)); ys.append(max(0.0, -dd[key]))
        xs, ys = np.array(xs), np.array(ys)
        return lambda r0: np.interp(r0, xs, ys), dict(zip(map(float, xs), map(float, ys)))
    lead8, lead8_tab = lead_fn("ES-FL")
    lead16, lead16_tab = lead_fn("FL16")
    res["lead_tables"] = {"M8_N": lead8_tab, "M16_N": lead16_tab}

    rows = []
    figdata = {}
    for snap in (4, 8, 12):
        t, rec, tags, tau = read_snapshot(FK / f"esflk.part.{snap:05d}.bin")
        MAH = summary_mass(t)
        RAH = 2.0 * MAH
        dust = tags >= NTRACER
        tg = tags[dust]
        R0, m, mu, tp = R0all[tg], mall[tg], rest[tg], tau[dust]
        Rex = R_of_tau(tp, R0, m)                               # exact radius at each particle's own clock
        Rlead8 = R_of_tau(tp + lead8(R0), R0, m)                # the run as measured at M/8, N
        Rlead16 = R_of_tau(tp + lead16(R0), R0, m)
        # scope's exact side: proper time of the nearest tracer label still present in the snapshot
        tr = tags < NTRACER
        trR0, trtau = R0all[tags[tr]], tau[tr]
        labels = np.unique(trR0)
        ltau = np.array([np.median(trtau[trR0 == L]) for L in labels])
        idx = np.abs(R0[:, None] - labels[None, :]).argmin(axis=1)
        Rscope = R_of_tau(ltau[idx], R0, m)
        # proper-time spread inside a 1 M label bin
        spread = []
        for b0 in range(6, 52):
            s = (R0 >= b0) & (R0 < b0 + 1) & (Rex > RAH)
            if s.sum() > 10:
                spread.append((b0, float(np.ptp(tp[s])), float(np.abs(tp[s].mean() - ltau[idx[s]].mean()))))
        edges = np.geomspace(1.5 * RAH, 40.0, 9)

        def prof(R):
            inside = R > RAH
            cum = np.array([mu[inside & (R < e)].sum() for e in edges[1:]])
            cnt = np.histogram(R[inside], bins=edges)[0]
            msh = np.histogram(R[inside], bins=edges, weights=mu[inside])[0]
            return cum, cnt, msh
        cum_ex, cnt_ex, m_ex = prof(Rex)
        cum_l8, cnt_l8, m_l8 = prof(Rlead8)
        cum_l16, _, m_l16 = prof(Rlead16)
        cum_sc, _, m_sc = prof(Rscope)
        mid = np.sqrt(edges[1:] * edges[:-1])
        rho_ex = m_ex / (4 * np.pi * mid ** 2 * np.diff(edges))
        inner = mid < 10.0

        def slope(mm):
            rr = mm / (4 * np.pi * mid ** 2 * np.diff(edges))
            ok = inner & (rr > 0)
            return float(np.polyfit(np.log(mid[ok]), np.log(rr[ok]), 1)[0]) if ok.sum() >= 2 else None
        # counting noise of the slope: bootstrap over particles of the exact profile
        rng = np.random.default_rng(snap)
        sl_bs = []
        insideR = Rex > RAH
        pool = np.flatnonzero(insideR & (Rex < 40.0))
        for _ in range(200):
            pick = rng.choice(pool, pool.size, replace=True)
            mm = np.histogram(Rex[pick], bins=edges, weights=mu[pick])[0]
            v = slope(mm)
            if v is not None:
                sl_bs.append(v)
        row = dict(t=float(t), M_AH=MAH, R_AH=RAH, edges=edges.tolist(), counts_exact=cnt_ex.tolist(),
                   counts_inner_total=int(cnt_ex[inner].sum()), n_inner_bins_below_400=int((cnt_ex[inner] < 400).sum()),
                   q_lead_M8=(cum_l8 / cum_ex - 1).tolist(), q_lead_M16=(cum_l16 / cum_ex - 1).tolist(),
                   q_scope_time=(cum_sc / cum_ex - 1).tolist(),
                   rho_ratio_lead_M8=(m_l8 / np.where(m_ex > 0, m_ex, np.nan) - 1).tolist(),
                   slope_exact=slope(m_ex), slope_lead_M8=slope(m_l8), slope_lead_M16=slope(m_l16),
                   slope_scope_time=slope(m_sc), slope_noise_sd=float(np.std(sl_bs)) if sl_bs else None,
                   count_noise_cum=(1 / np.sqrt(np.maximum(np.cumsum(cnt_ex), 1))).tolist(),
                   tau_spread_in_1M_label_bins_max=max(s[1] for s in spread) if spread else None,
                   tau_offset_scope_vs_own_max=max(s[2] for s in spread) if spread else None,
                   tracer_labels_present=labels.tolist())
        rows.append(row)
        figdata[snap] = (mid, rho_ex, cum_ex, cum_l8, cum_l16, cum_sc, edges)
        print(json.dumps({k: row[k] for k in row if k not in ("edges",)}, default=float)[:1500])
    res["snapshots"] = rows
    res["max_abs_q_lead_M8"] = max(max(abs(x) for x in r["q_lead_M8"]) for r in rows)
    res["max_abs_q_lead_M16"] = max(max(abs(x) for x in r["q_lead_M16"]) for r in rows)
    res["max_abs_q_scope_time"] = max(max(abs(x) for x in r["q_scope_time"]) for r in rows)
    (out / "dress_model.json").write_text(json.dumps(res, indent=1, default=float))

    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 3.2))
    cols = {4: fs.PAL["blue"], 8: fs.PAL["red"], 12: fs.PAL["yellow"]}
    for snap, (mid, rho, ce, c8, c16, cs, edges) in figdata.items():
        tt = rows[[4, 8, 12].index(snap)]["t"]
        ax[0].loglog(mid, rho, "o-", ms=3, color=cols[snap], label=f"t = {tt:.0f} M")
        ax[1].semilogx(edges[1:], (c8 / ce - 1) * 100, "o-", ms=3, color=cols[snap], label=f"lead M/8, {tt:.0f} M")
        ax[1].semilogx(edges[1:], (c16 / ce - 1) * 100, "s--", ms=3, color=cols[snap], alpha=0.6)
        ax[2].semilogx(edges[1:], (cs / ce - 1) * 100, "o-", ms=3, color=cols[snap], label=f"{tt:.0f} M")
    ax[0].set_xlabel("areal radius R / M"); ax[0].set_ylabel(r"rest-mass density (exact, own clocks)")
    ax[0].legend(fontsize=7); ax[0].set_title("(a) infalling matter outside 1.5 R_AH", fontsize=8)
    for a in ax[1:]:
        a.axhspan(-2, 2, color="0.92", zorder=0)
        a.axvline(10, color="0.6", lw=0.5, ls=":")
        a.set_xlabel("R / M"); a.set_ylabel("q / per cent")
    ax[1].set_title("(b) q from the measured lead (solid M/8, dashed M/16)", fontsize=8); ax[1].legend(fontsize=6)
    ax[2].set_title("(c) q from the scope's tracer-label clock", fontsize=8); ax[2].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "dress_model.png", dpi=150)
    fig.savefig(out / "dress_model.pdf")
    print("C0", res["C0"], "max|q| lead8", res["max_abs_q_lead_M8"], "lead16", res["max_abs_q_lead_M16"],
          "scope time", res["max_abs_q_scope_time"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
