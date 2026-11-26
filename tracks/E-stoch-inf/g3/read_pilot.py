#!/usr/bin/env python3
"""Reader of the G3 pilot (g3/JOURNAL.md entries 2, 4 and 5): per member, R^NR and zeta at N_f, health and cost.

    read_pilot.py OUT --run <pilot run dir> --deck <usr_prod.athinput> --lead-json <zeta_tests.json>
                  [--members b000,...] [--procs 4] [--msteps 4000] [--check-msteps 1000] [--check-cells 20000]

zeta is the lead's reader (zeta/zeta_reader.py: V, dV and map_rk4 taken verbatim from its source with the ast
module, as g3/zeta_verify/scripts/large_amp.py does), phi_e of its record (the deck's potential and slice are the
same as the 32^3 deck's: asserted). The map runs with --msteps (default 4000, the reader as cleared by the
verifier) for every cell and with --check-msteps (default 1000) on --check-cells random cells (P5-3: the cost of
a cheaper map). R^NR is read_seed.r_nr. Standardisation: R^NR with sigma_lin of the run's own record;
zeta with its own standard deviation for (T) (SCOPE 4d.9 A2), and with sigma_lin for the r(nu) report.
Sign convention: zeta in the delta-N convention (A2/A3), zeta = -R^NR at first order.
Writes OUT/pilot.json, OUT/<member>.json, OUT/<member>_hist.npz, OUT/fig_pilot.png (and .pdf).
"""
import argparse
import ast
import json
import os
import sys
import time
import types
from multiprocessing import Pool

import numpy as np
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
TRK = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TRK, "repro", "figs", "figures"))
import read_seed as RS  # noqa: E402
import figlib as fl  # noqa: E402
import figstyle as fs  # noqa: E402

NUS = (3.0, 4.0)
EDGES = np.linspace(-8.0, 8.0, 161)
H_COL, M_COL = 25, 7          # <|H-<H>|/[H]> and <|M|/[M]> of usr.sf.con.hst (1-based, header of the file)


def deck_value(path, block, key):
    blk = None
    for line in open(path):
        s = line.split("#")[0].strip()
        if s.startswith("<"):
            blk = s.strip("<>")
        elif "=" in s and blk == block and s.split("=")[0].strip() == key:
            return float(s.split("=")[1])
    raise KeyError(key)


def lead_namespace(src, lam, vev, phi_e, msteps):
    tree = ast.parse(open(src).read())
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("V", "dV", "map_rk4")]
    assert len(keep) == 3
    ns = dict(np=np, LAM=lam, VEV=vev, PHI_E=phi_e, SQ2=np.sqrt(2.0), PI4=4.0 * np.pi, PI8=8.0 * np.pi,
              a=types.SimpleNamespace(msteps=msteps))
    exec(compile(ast.Module(body=keep, type_ignores=[]), src, "exec"), ns)
    return ns


def moments(x):
    c = x - x.mean()
    v = float(np.mean(c ** 2))
    return float(np.sqrt(v)), float(np.mean(c ** 3) / v ** 1.5), float(np.mean(c ** 4) / v ** 2 - 3.0)


def tails(x, scale, tag):
    out = {}
    for nu in NUS:
        fp = float(np.mean(x > nu * scale))
        fm = float(np.mean(x < -nu * scale))
        q = float(norm.sf(nu))
        out[f"{tag}Fp{nu:g}"], out[f"{tag}Fm{nu:g}"] = fp, fm
        out[f"{tag}Fp{nu:g}_Q"], out[f"{tag}Fm{nu:g}_Q"] = fp / q, fm / q
        out[f"{tag}A{nu:g}"] = (fp - fm) / (fp + fm) if fp + fm > 0 else float("nan")
    return out


def health(run):
    rows = []
    with open(os.path.join(run, "usr.sf.con.hst")) as fh:
        for line in fh:
            if line.strip() and not line.startswith("#"):
                rows.append([float(t) for t in line.split()])
    a = np.array(rows)
    return dict(t_last=float(a[-1, 0]), nrec=int(a.shape[0]), finite=bool(np.all(np.isfinite(a))),
                max_Hp=float(np.max(a[:, H_COL - 1])), max_M=float(np.max(a[:, M_COL - 1])),
                last_Hp=float(a[-1, H_COL - 1]), last_M=float(a[-1, M_COL - 1]))


def one(job):
    label, run, cfg = job
    t0 = time.time()
    path = os.path.join(run, "usr.sf.00001.dump")
    Rx, h, N = RS.r_nr(path, 1)
    sig_lin, _ = RS.sigma_lin_of(path[:-len(".dump")] + ".modes", N)
    _, f = fl.ll.read_dump(path, ["phi", "Pi", "chi", "K"])
    H = -f["K"] / 3.0
    v = f["Pi"] / H
    n_back = int(np.sum(v <= 0))
    dphi = f["phi"] - f["phi"].mean()
    dPi = f["Pi"] - f["Pi"].mean()
    rel_slope = float(np.sum(dphi * dPi) / np.sum(dphi * dphi))
    rel_corr = float(np.corrcoef(dphi.ravel(), dPi.ravel())[0, 1])
    sR, skR, kuR = moments(Rx)
    rec = dict(label=label, run=run, time=float(h["time"]), N=int(N), sigma_lin=sig_lin,
               msteps=cfg["msteps"], n_cells_rolling_back=n_back,
               relation_slope=rel_slope, relation_corr=rel_corr,
               R_ratio=sR / sig_lin, R_skew=skR, R_exkurt=kuR,
               rms_dK_over_K=float(np.std(f["K"]) / abs(np.mean(f["K"]))))
    z = None
    if cfg["msteps"] > 0:   # zeta: the lead's map (batch 23: about 1.5 h a member at 1000 steps on the loaded machine)
        ns = lead_namespace(cfg["src"], cfg["lam"], cfg["vev"], cfg["phi_e"], cfg["msteps"])
        phi = f["phi"].ravel()
        vv = v.ravel()
        dn = ns["map_rk4"](phi, vv).reshape(f["phi"].shape)
        rng = np.random.default_rng(cfg["seed"])
        idx = rng.choice(phi.size, cfg["check_cells"], replace=False)
        nsc = lead_namespace(cfg["src"], cfg["lam"], cfg["vev"], cfg["phi_e"], cfg["check_msteps"])
        dc = nsc["map_rk4"](phi[idx], vv[idx]) - dn.ravel()[idx]
        z = -0.5 * np.log(f["chi"] / f["chi"].mean()) + dn
        z = z - z.mean()
        sZ, skZ, kuZ = moments(z)
        rec.update(check_msteps=cfg["check_msteps"], step_dev_max=float(np.max(np.abs(dc))),
                   step_dev_max_offset_removed=float(np.max(np.abs(dc - dc.mean()))),
                   zeta_ratio=sZ / sig_lin, zeta_skew=skZ, zeta_exkurt=kuZ, skew_sum=skZ + skR,
                   corr_zeta_R=float(np.corrcoef(z.ravel(), Rx.ravel())[0, 1]),
                   zeta_max=float(z.max() / sZ), zeta_min=float(z.min() / sZ))
    rec.update(tails(Rx, sig_lin, "R_"))
    if z is not None:
        rec.update(tails(z, sZ, "zeta_"))
        rec.update(tails(z, sig_lin, "zetalin_"))
    rec["health"] = health(run)
    hz = np.histogram(z / sZ, bins=EDGES)[0] if z is not None else np.zeros(len(EDGES) - 1, int)
    hr, _ = np.histogram(-Rx / sig_lin, bins=EDGES)
    np.savez(os.path.join(cfg["out"], f"{label}_hist.npz"), edges=EDGES, zeta=hz, minusR=hr)
    rec["wall_s"] = time.time() - t0
    with open(os.path.join(cfg["out"], f"{label}.json"), "w") as fp:
        json.dump(rec, fp, indent=1)
    print(json.dumps({k: rec.get(k) for k in ("label", "R_ratio", "zeta_ratio", "R_skew", "zeta_skew", "skew_sum",
                                              "step_dev_max", "relation_corr", "wall_s")}), flush=True)
    return rec


def cost(run, members):
    """Wall per member from the batch status file (end times) and the start of the first member's log."""
    ends = {}
    for line in open(os.path.join(run, "batch.list.status")):
        t, rc, d = line.split()
        ends[os.path.basename(d)] = (t, int(rc.split("=")[1]))
    first = sorted(p for p in os.listdir(os.path.join(run, members[0])) if p.startswith("athena.2") and p.endswith(".log"))[0]
    start = None
    for line in open(os.path.join(run, members[0], first)):
        if "start=" in line:
            start = line.split("start=")[1].split()[0][11:19]
            break

    def sec(hms):
        hh, mm, ss = (int(x) for x in hms.split(":"))
        return hh * 3600 + mm * 60 + ss
    walls, prev = {}, sec(start)
    for m in members:
        e = sec(ends[m][0])
        walls[m] = e - prev
        prev = e
    return dict(start=start, walls_s=walls, rc={m: ends[m][1] for m in ends},
                mean_card_h=float(np.mean(list(walls.values())) / 3600.0))


def figure(recs, out):
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.COLUMN_WIDTH * 2.6, 2.9))
    c = 0.5 * (EDGES[1:] + EDGES[:-1])
    dx = EDGES[1] - EDGES[0]
    hz = sum(np.load(os.path.join(out, f"{r['label']}_hist.npz"))["zeta"] for r in recs)
    hr = sum(np.load(os.path.join(out, f"{r['label']}_hist.npz"))["minusR"] for r in recs)
    for hh, lab, col in ((hz, r"$\zeta/\sigma_\zeta$", fs.SERIES[0]), (hr, r"$-\mathcal{R}^{\rm NR}/\sigma_{\rm lin}$", fs.SERIES[1])):
        if hh.sum() == 0:
            continue
        p = hh / (hh.sum() * dx)
        m = p > 0
        ax[0].semilogy(c[m], p[m] / norm.pdf(c[m]), ".", ms=3, color=col, label=lab)
    ax[0].axhline(1.0, **fs.GUIDE)
    ax[0].set_xlim(-5.5, 5.5)
    ax[0].set_ylim(0.2, 5.0)
    ax[0].set_xlabel("standardised value")
    ax[0].set_ylabel("density / Gaussian (ten members)")
    ax[0].legend(fontsize=6.5, frameon=False)
    i = np.arange(len(recs))
    for key, lab, col, mk in (("zeta_Fp3_Q", r"$\zeta$: $F_+(3)/Q$", fs.SERIES[0], "o"),
                              ("zeta_Fm3_Q", r"$\zeta$: $F_-(3)/Q$", fs.SERIES[0], "v"),
                              ("R_Fp3_Q", r"$\mathcal{R}$: $F_+(3)/Q$", fs.SERIES[1], "o"),
                              ("R_Fm3_Q", r"$\mathcal{R}$: $F_-(3)/Q$", fs.SERIES[1], "v")):
        if key not in recs[0]:
            continue
        ax[1].plot(i, [r[key] for r in recs], mk, ms=3.5, color=col, mfc="none" if "Fm" in key else col, label=lab)
    ax[1].axhline(1.0, **fs.GUIDE)
    ax[1].set_xlabel("member (seed 20262000 + i)")
    ax[1].set_ylabel("exceedance / Gaussian at 3 (R: at 3 sigma_lin)")
    ax[1].legend(fontsize=6, frameon=False, ncol=2)
    if "zeta_skew" in recs[0]:
        ax[2].plot(i, [r["zeta_skew"] for r in recs], "o", ms=3.5, color=fs.SERIES[0], label=r"skew $\zeta$")
        ax[2].plot(i, [r["skew_sum"] for r in recs], "^", ms=3.5, color=fs.SERIES[2], label="sum")
        ax[2].axhspan(0.017, 0.023, color=fs.SERIES[2], alpha=0.15, lw=0, label="P5-5 band of the sum")
    ax[2].plot(i, [r["R_skew"] for r in recs], "s", ms=3.5, color=fs.SERIES[1], label=r"skew $\mathcal{R}^{\rm NR}$")
    sd1 = np.sqrt(6.0 / 5.5e5)
    ax[2].axhspan(-sd1, sd1, color=fs.SERIES[1], alpha=0.12, lw=0, label=r"$\pm\sqrt{6/N_{\rm eff}}$ (entry 1)")
    ax[2].axhline(0.0, **fs.GUIDE)
    ax[2].set_xlabel("member")
    ax[2].set_ylabel("skewness")
    ax[2].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_pilot"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--run", required=True)
    ap.add_argument("--deck", required=True)
    ap.add_argument("--lead-json", required=True)
    ap.add_argument("--members", default=",".join(f"b{i:03d}" for i in range(10)))
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--msteps", type=int, default=4000)
    ap.add_argument("--check-msteps", type=int, default=1000)
    ap.add_argument("--check-cells", type=int, default=20000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    L = json.load(open(a.lead_json))
    deck = dict(lam=deck_value(a.deck, "scalar_field", "lambda"), vev=deck_value(a.deck, "scalar_field", "vev"),
                phi0=deck_value(a.deck, "problem", "phi0"), pi0=deck_value(a.deck, "problem", "pi0"),
                tlim=deck_value(a.deck, "time", "tlim"))
    for k in deck:
        assert deck[k] == L["deck"][k], (k, deck[k], L["deck"][k])
    src = os.path.join(TRK, "zeta", "zeta_reader.py")
    members = a.members.split(",")
    jobs = [(m, os.path.join(a.run, m), dict(src=src, lam=deck["lam"], vev=deck["vev"], phi_e=L["phi_e"],
                                             msteps=a.msteps, check_msteps=a.check_msteps, check_cells=a.check_cells, seed=1000 + i, out=a.out))
            for i, m in enumerate(members)]
    with Pool(a.procs) as pool:
        recs = pool.map(one, jobs)
    res = dict(members=recs, deck=deck, phi_e=L["phi_e"], cost=cost(a.run, members))
    keys = [k for k in recs[0] if isinstance(recs[0][k], float) and all(k in r for r in recs)]
    res["mean"] = {k: float(np.mean([r[k] for r in recs])) for k in keys}
    res["sd"] = {k: float(np.std([r[k] for r in recs], ddof=1)) for k in keys}
    res["health_all"] = dict(finite=all(r["health"]["finite"] for r in recs),
                             t_last_min=min(r["health"]["t_last"] for r in recs),
                             max_Hp=max(r["health"]["max_Hp"] for r in recs),
                             max_M=max(r["health"]["max_M"] for r in recs))
    with open(os.path.join(a.out, "pilot.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(dict(mean=res["mean"], sd=res["sd"], health=res["health_all"], cost=res["cost"]), indent=1))
    figure(recs, a.out)


if __name__ == "__main__":
    main()
