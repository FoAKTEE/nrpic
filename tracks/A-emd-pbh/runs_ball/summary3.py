#!/usr/bin/env python3
"""Summaries of the wave-2b runs of the package runs_ball (JOURNAL entry 7), from the
<label>_numbers.json and <label>_series.npz written by compare.py.

  --sr <dir>:<label>:<dx>:<gauge> ...   (data set 2t: SR-1, SR-2 of wave 2 and SR-1L)
      table and orders of the core-shell error and the turnaround; figure
      fig_sr1l_comparison: core |eps| against tau for every run, central lapse against
      its reference (SR-2: a(tau_c); SR-1L: the relaxed-lapse reference), largest |H|
      on the mesh against t, central proper time against t.
  --bh <dir>:<label>:<dx> ...            (data set 3: BH-1)
      table of the first horizon (code time, proper time at the horizon minus the exact
      trapping time of that shell, first slice with a trapped sphere from the particles)
      and of the horizon-mass error against the exact mass of the same slice, orders
      between resolutions; figure fig_bh1_summary.

    summary3.py --prep2t <dir> --prep3 <dir> [--sr ...] [--bh ...] --out <dir> [--figdir <dir>]
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C   # noqa: E402


def load(spec, n):
    parts = spec.split(":")
    d, lab, dx = parts[0], parts[1], float(parts[2])
    g = parts[3] if len(parts) > 3 else None
    num = C.load_json(os.path.join(d, f"{lab}_numbers.json"))
    ser = np.load(os.path.join(d, f"{lab}_series.npz"))
    return dict(lab=lab, dx=dx, gauge=g or num["gauge"], num=num, ser=ser, dir=d)


def order(v0, v1, dx0, dx1):
    if v0 is None or v1 is None or not (np.isfinite(v0) and np.isfinite(v1)) or v0 == 0 or v1 == 0:
        return None
    return float(np.log(abs(v0) / abs(v1)) / np.log(dx0 / dx1))


def sr_part(a, runs, ex, fs, plt):
    table = []
    for r in runs:
        c = r["num"]["eps_groups"]["core"]
        ta = r["num"]["events"].get("core", {}).get("turnaround", {})
        h = r["num"]["history"]
        table.append(dict(label=r["lab"], gauge=r["gauge"], dx=r["dx"], t_end=r["num"]["traj"]["t_last"],
                          eps_core_tau8_max=c.get("eps_tau8", {}).get("maxabs"),
                          eps_core_tau16_9_max=c.get("eps_tau16.894", {}).get("maxabs"),
                          eps_core_tau24_max=c.get("eps_tau24", {}).get("maxabs"),
                          eps_core_tau30_max=c.get("eps_tau30", {}).get("maxabs"),
                          tau_ta_err_mean=ta.get("dtau_mean"), Rmax_err_rel_mean=ta.get("dRmax_rel_mean"),
                          tau_probe_end=h.get("tau_probe_end"), finite_end=h.get("finite_end"),
                          lapse_dev_maxabs_t_le_15=h.get("lapse_dev_maxabs_t_le_15"),
                          H_max_t20=r["num"]["cstat"].get("H_max_t20"), H_mean_t10=r["num"]["cstat"].get("H_mean_t10"),
                          H_mean_t40=r["num"]["cstat"].get("H_mean_t40"),
                          finder_n=r["num"]["finder"]["n"]))
    orders = []
    for g in sorted(set(t["gauge"] for t in table)):
        rr = sorted([t for t in table if t["gauge"] == g], key=lambda t: -t["dx"])
        for k in range(len(rr) - 1):
            o = dict(gauge=g, dx=[rr[k]["dx"], rr[k + 1]["dx"]])
            for key in ("eps_core_tau8_max", "eps_core_tau16_9_max", "tau_ta_err_mean", "Rmax_err_rel_mean"):
                o[key] = order(rr[k][key], rr[k + 1][key], rr[k]["dx"], rr[k + 1]["dx"])
            orders.append(o)
    # figure
    gst = {"sr1": dict(ls="--"), "sr2": dict(ls=":"), "leak": dict(ls="-")}
    col = {1.0: fs.PAL["yellow"], 0.5: fs.PAL["red"], 0.25: fs.PAL["blue"]}
    gname = {"sr1": "SR-1", "sr2": "SR-2", "leak": "SR-1L"}
    fig = plt.figure(figsize=(8.0, 6.2))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.95, wspace=0.30, hspace=0.40)
    ax = fig.add_subplot(2, 2, 1)
    for r in runs:
        s = r["ser"]
        core = s["Ri"] <= 2.4
        e = np.abs(s["eps"][:, core])
        tm = np.nanmedian(s["tau"][:, core], axis=1)
        with np.errstate(invalid="ignore"):
            ax.semilogy(tm, np.nanmax(e, axis=1), color=col.get(r["dx"], "k"), lw=1.6 if r["gauge"] == "leak" else 1.0,
                        label=f"{gname[r['gauge']]}, $\\Delta x={r['dx']:g}$", **gst[r["gauge"]])
    ax.axvline(ex["core"]["tau_ta"], **fs.MASK_LINE)
    ax.set_xlabel(r"proper time $\tau\,/M$")
    ax.set_ylabel(r"core: largest $|R/R_{\rm exact}-1|$")
    ax.set_ylim(1e-5, 1)
    ax.set_xlim(0, 46)
    ax.legend(fontsize=6, ncol=2, loc="lower right")
    ax.set_title("core shells (grey: exact turnaround)", fontsize=10)
    ax = fig.add_subplot(2, 2, 2)
    lr = None
    for r in runs:
        if r["gauge"] not in ("sr2", "leak"):
            continue
        h = r["ser"]["hst"]
        ok = np.all(np.isfinite(h[:, :16]), axis=1)
        ax.plot(h[ok, 0], h[ok, 12], color=col.get(r["dx"], "k"), lw=1.4, **gst[r["gauge"]],
                label=f"{gname[r['gauge']]}, $\\Delta x={r['dx']:g}$")
        if r["gauge"] == "leak" and lr is None:
            lr = C.relaxed_lapse_reference(np.array(ex["central"]["tau"])[:-1], np.array(ex["central"]["a"])[:-1], 8.0)
    if lr is not None:
        ax.plot(lr[0], lr[2], color="k", lw=1.0, label="relaxed lapse, homogeneous core")
    tt = np.linspace(0, 45, 400)
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel(r"central lapse $\alpha_c$")
    ax.set_xlim(0, 45)
    ax.legend(fontsize=6, loc="upper right")
    ax.set_title("central lapse", fontsize=10)
    ax = fig.add_subplot(2, 2, 3)
    for r in runs:
        if r["dx"] != 0.5:
            continue
        cst = r["ser"]["cst"]
        ok = np.all(np.isfinite(cst[:, :10]), axis=1) & (np.abs(cst[:, 8]) < 1e30)
        ax.semilogy(cst[ok, 0], np.abs(cst[ok, 8]), color={"sr1": fs.PAL["yellow"], "sr2": fs.PAL["blue"],
                                                          "leak": fs.PAL["red"]}[r["gauge"]],
                    lw=1.4, label=f"{gname[r['gauge']]}, $\\Delta x=M/2$")
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel(r"largest $|H|$ on the mesh")
    ax.set_ylim(1e-4, 1e2)
    ax.legend(fontsize=7, loc="upper left")
    ax.set_title("constraint violation, dx = M/2", fontsize=10)
    ax = fig.add_subplot(2, 2, 4)
    for r in runs:
        h = r["ser"]["hst"]
        ok = np.all(np.isfinite(h[:, :16]), axis=1)
        ax.plot(h[ok, 0], h[ok, 14], color=col.get(r["dx"], "k"), lw=1.4 if r["gauge"] == "leak" else 0.9,
                **gst[r["gauge"]])
    if lr is not None:
        ax.plot(lr[0], lr[1], color="k", lw=1.0)
    ax.axhline(ex["first_trapped"]["tau"], color="k", lw=1.0, ls=":")
    ax.axhline(ex["core"]["tau_c"], **fs.MASK_LINE)
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel(r"central proper time $\tau_c\,/M$")
    ax.set_xlim(0, 54)
    ax.set_ylim(0, 65)
    ax.set_title(r"centre's clock (dotted: first trapping 44.35)", fontsize=9)
    outs = fs.save(fig, os.path.join(a.out, "fig_sr1l_comparison"))
    plt.close(fig)
    return dict(table=table, orders=orders), outs


def bh_part(a, runs, ex, fs, plt):
    rows = []
    tau1 = ex["first_trapped"]["tau"]
    for r in runs:
        f = r["num"]["finder"]
        rows_f = [x for x in f.get("rows", [])]
        first = f.get("first")
        d = dict(label=r["lab"], dx=r["dx"], t_end=r["num"]["traj"]["t_last"], finder_n=f["n"],
                 finite_end=r["num"]["history"].get("finite_end"),
                 first_trapped_slice_t=r["num"].get("first_trapped_slice", {}).get("t_code"))
        if first:
            d.update(first_t=first["t"], first_m_irr=first["m_irr"], first_mass=first["mass"],
                     first_tau_at_horizon=first["tau_at_horizon"],
                     first_tau_minus_tauAH_shell=first["tau_at_horizon"] - first["tau_ah_exact_shell_at_r"]
                     if first.get("tau_ah_exact_shell_at_r") is not None else None,
                     first_tau_minus_tau_first=first["tau_at_horizon"] - tau1,
                     first_m_exact_slice=first["m_exact_slice"],
                     first_rel_err_slice=(first["m_irr"] / first["m_exact_slice"] - 1.0)
                     if first["m_exact_slice"] == first["m_exact_slice"] else None,
                     first_rel_err_core_mass=first["m_irr"] / ex["first_trapped"]["m"] - 1.0,
                     first_r_mean=first["r_mean"])
        for key in ("m_irr_rel_err_vs_m_exact_slice", "m_irr_rel_err_vs_m_exact_shell_at_r"):
            if key in f:
                d[key] = f[key]
        ev = r["num"]["events"]
        edge = [g for g in ev if g.startswith("R") and abs(float(g[1:]) - (ex["core"]["R1"] - 0.05)) < 0.02]
        if edge and "trapping" in ev[edge[0]]:
            d["edge_band_trapping"] = ev[edge[0]]["trapping"]
        d["first_trapped_tracked"] = ev.get("first_trapped_tracked")
        d["missed_trapping"] = ev.get("missed_trapping")
        rows.append(d)
    rr = sorted(rows, key=lambda t: -t["dx"])
    orders = []
    for k in range(len(rr) - 1):
        o = dict(dx=[rr[k]["dx"], rr[k + 1]["dx"]])
        for key in ("first_rel_err_slice", "first_rel_err_core_mass", "first_tau_minus_tauAH_shell"):
            o[key] = order(rr[k].get(key), rr[k + 1].get(key), rr[k]["dx"], rr[k + 1]["dx"])
        m0 = (rr[k].get("m_irr_rel_err_vs_m_exact_slice") or {}).get("median")
        m1 = (rr[k + 1].get("m_irr_rel_err_vs_m_exact_slice") or {}).get("median")
        o["median_rel_err_slice"] = order(m0, m1, rr[k]["dx"], rr[k + 1]["dx"])
        orders.append(o)
    col = {0.25: fs.PAL["yellow"], round(1 / 6, 6): fs.PAL["red"], 0.125: fs.PAL["blue"]}
    fig = plt.figure(figsize=(8.0, 6.2))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.95, wspace=0.32, hspace=0.40)
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)
    for r in runs:
        c_ = col.get(round(r["dx"], 6), "k")
        lab = f"$\\Delta x = M/{1 / r['dx']:.0f}$"
        fr = r["num"]["finder"].get("rows", [])
        if fr:
            ft = np.array([x["t"] for x in fr])
            mi = np.array([x["m_irr"] for x in fr])
            me = np.array([x["m_exact_slice"] for x in fr], dtype=float)
            ax1.plot(ft, mi, "o-", color=c_, ms=2.5, lw=1.0, label=lab)
            ax1.plot(ft, me, "-", color=c_, lw=0.8, ls="--")
            with np.errstate(invalid="ignore", divide="ignore"):
                ax2.semilogy(ft, np.abs(mi / me - 1.0), "o-", color=c_, ms=2.5, lw=1.0, label=lab)
            th = np.array([x["tau_at_horizon"] for x in fr])
            ax3.plot(ft, th, "o-", color=c_, ms=2.5, lw=1.0, label=lab)
        h = r["ser"]["hst"]
        ok = np.all(np.isfinite(h[:, :16]), axis=1)
        ax4.plot(h[ok, 0], h[ok, 12], color=c_, lw=1.3, label=lab)
    lr = ex.get("lapse_reference")
    if lr:
        ax4.plot(lr["t"], lr["alpha"], color="k", lw=1.0, ls="--", label="homogeneous reference")
    ax1.axhline(ex["first_trapped"]["m"], **fs.MASK_LINE)
    ax1.set_xlabel(r"coordinate time $t\,/M$")
    ax1.set_ylabel(r"horizon mass $/M$")
    ax1.legend(fontsize=7, loc="lower right")
    ax1.set_title("finder $\\sqrt{A/16\\pi}$ (dashed: exact, same slice)", fontsize=9)
    ax2.axhline(1e-3, **fs.GUIDE)
    ax2.set_xlabel(r"$t\,/M$")
    ax2.set_ylabel(r"$|m_{\rm irr}/m_{\rm exact}-1|$")
    ax2.legend(fontsize=7)
    ax2.set_title("mass error (dashed: source paper 1e-3)", fontsize=9)
    ax3.axhline(tau1, **fs.GUIDE)
    ax3.set_xlabel(r"$t\,/M$")
    ax3.set_ylabel(r"proper time at the horizon $\tau\,/M$")
    ax3.legend(fontsize=7)
    ax3.set_title(r"clock of the shells at the horizon (dashed: $\tau_{\rm AH}$ exact)", fontsize=9)
    ax4.set_xlabel(r"$t\,/M$")
    ax4.set_ylabel(r"central lapse")
    ax4.legend(fontsize=7)
    ax4.set_title("central lapse", fontsize=10)
    outs = fs.save(fig, os.path.join(a.out, "fig_bh1_summary"))
    plt.close(fig)
    return dict(table=rows, orders=orders), outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prep2t", default=None)
    ap.add_argument("--prep3", default=None)
    ap.add_argument("--sr", action="append", default=[])
    ap.add_argument("--bh", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--figdir", default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    res, outs = {}, []
    if a.sr:
        ex = C.load_json(os.path.join(a.prep2t, "exact.json"))
        res["sr"], o = sr_part(a, [load(s, i) for i, s in enumerate(a.sr)], ex, fs, plt)
        outs += o
    if a.bh:
        ex = C.load_json(os.path.join(a.prep3, "exact.json"))
        res["bh"], o = bh_part(a, [load(s, i) for i, s in enumerate(a.bh)], ex, fs, plt)
        outs += o
    C.write_json(os.path.join(a.out, "summary3.json"), res)
    for part in res.values():
        for t in part["table"]:
            print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in t.items()})
        for o in part["orders"]:
            print("order", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in o.items()})
    if a.figdir:
        import shutil
        os.makedirs(a.figdir, exist_ok=True)
        for f in outs:
            if f.endswith(".png"):
                shutil.copy(f, os.path.join(a.figdir, os.path.basename(f)))


if __name__ == "__main__":
    main()
