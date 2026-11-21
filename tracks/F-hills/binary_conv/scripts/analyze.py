#!/usr/bin/env python3
"""Analysis of the isolated-binary runs of binary_conv (BC-3): separation and orbital phase
against time at m/8, m/12, m/16 with P1 and the references; time to merger or its lower
bound; horizon masses; constraint norm; convergence order; cost ledger.

Readers: tracks/F-hills/nr_first/scripts/nrread.py (trackers joined across restarts,
horizon summaries with failed searches removed, history). Nothing is computed from the
brief.

Usage:
  analyze.py --run R8=<rundir> [--run R12=<rundir>] [--run R16n=<rundir>]
             --p1 <P1 rundir> --refs <refs.json> --out <dir> [--g2model <g2mesh model.json>]

Order of convergence of Delta s(t) = s(0) - s(t) at fixed t, cells h = 1, 2/3, 1/2 (units of
m/8): three-point p from (D8 - D12)/(D12 - D16) = (1 - (2/3)^p)/((2/3)^p - (1/2)^p), and the
two-point p2 = log2(D8/D16) that assumes Delta s -> 0 in the continuum.
Stretch model [JUDGEMENT]: if the decay is numerical with a rate proportional to h^p, the
separation at cell h is the m/8 curve with time stretched, s_h(t) = s_8(lambda_h t); lambda_h is
fitted on the common window, and the merger time follows as t_merge,8 / lambda_h.
"""
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np
from scipy.optimize import brentq, minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/nr_first/scripts"))
sys.path.insert(0, HERE)
import nrread  # noqa: E402
import figstyle as fs  # noqa: E402

H_OF = {"R8": 1.0, "R12": 2.0 / 3.0, "R16n": 0.5, "P1": 1.0}
COL = {"R8": fs.PAL["red"], "R12": fs.PAL["orange"], "R16n": fs.PAL["green"], "P1": "0.45"}
TS = (2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0)


def orbit(rundir):
    tr = nrread.read_trackers(rundir)
    if 0 not in tr or 1 not in tr or len(tr[0]["t"]) == 0:
        return None
    a, b = tr[0], tr[1]
    n = min(len(a["t"]), len(b["t"]))
    t = a["t"][:n]
    if not np.allclose(t, b["t"][:n]):
        tb = b["t"]
        xb = np.stack([np.interp(t, tb, b["x"][:, k]) for k in range(3)], axis=1)
    else:
        xb = b["x"][:n]
    d = a["x"][:n] - xb
    s = np.linalg.norm(d, axis=1)
    ph = np.unwrap(np.arctan2(d[:, 1], d[:, 0]))
    com = 0.5 * (a["x"][:n] + xb)
    return dict(t=t, s=s, phase=ph - ph[0], com=com)


def horizons(rundir):
    out = {}
    for n, (h, nfail) in nrread.read_horizons(rundir).items():
        out[n] = dict(t=h["t"], mass=h["mass"], meanradius=h.get("meanradius", np.zeros(0)),
                      nfail=nfail)
    return out


def ledger(rundir):
    rows = []
    for log in sorted(glob.glob(os.path.join(rundir, "chain", "seg*.log"))):
        m = re.search(r"seg(\d+)\.job(\d+)", log)
        txt = open(log, errors="replace").read()
        cyc = [(int(c), float(tt)) for c, tt in re.findall(r"cycle=(\d+) time=([0-9.eE+-]+)", txt)]
        mbc = re.search(r"MeshBlock-cycles = (\d+)", txt)
        cpu = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
        nmb = re.search(r"Current number of MeshBlocks = (\d+)", txt)
        peak = re.search(r"gpu_mem_peak_MiB=(\d+)", txt)
        term = re.search(r"Terminating on ([^\n]+)", txt)
        row = dict(seg=int(m.group(1)), job=int(m.group(2)), log=os.path.basename(log),
                   t0=cyc[0][1] if cyc else None, t1=cyc[-1][1] if cyc else None,
                   c0=cyc[0][0] if cyc else None, c1=cyc[-1][0] if cyc else None,
                   mb_cycles=int(mbc.group(1)) if mbc else None,
                   cpu_s=float(cpu.group(1)) if cpu else None,
                   mb_end=int(nmb.group(1)) if nmb else None,
                   gpu_peak_MiB=int(peak.group(1)) if peak else None,
                   ended=term.group(1).strip() if term else "no termination message")
        fin = re.search(r"time=([0-9.eE+-]+) cycle=(\d+)\s*\n\s*tlim", txt)
        if fin:
            row["t1"], row["c1"] = float(fin.group(1)), int(fin.group(2))
        if row["mb_cycles"] and row["cpu_s"]:
            row["mbc_per_s"] = row["mb_cycles"] / row["cpu_s"]
        try:
            r = subprocess.run(["sacct", "-n", "-X", "-P", "-j", str(row["job"]), "-o",
                                "ElapsedRaw,State"], capture_output=True, text=True, timeout=30)
            el, st = r.stdout.strip().splitlines()[0].split("|")
            row["elapsed_s"], row["sacct_state"] = int(el), st
            row["card_hours"] = int(el) / 3600.0
        except Exception:  # noqa: BLE001
            pass
        rows.append(row)
    return rows


def value_at(o, T):
    if o is None or o["t"][-1] < T - 1e-9:
        return None
    return float(np.interp(T, o["t"], o["s"]))


def three_point_order(d8, d12, d16):
    num, den = d8 - d12, d12 - d16
    if den == 0 or num / den <= 0:
        return None
    R = num / den

    def f(p):
        return (1 - (2 / 3) ** p) / ((2 / 3) ** p - 0.5 ** p) - R
    try:
        return brentq(f, 0.02, 20.0)
    except ValueError:
        return None


def stretch(o_ref, o, tmax):
    """lambda with s(t) ~ s_ref(lambda t) on 0 < t <= tmax (least squares)."""
    m = (o["t"] > 0.5) & (o["t"] <= tmax)
    t, s = o["t"][m], o["s"][m]

    def cost(lam):
        tt = lam * t
        ok = tt <= o_ref["t"][-1]
        if ok.sum() < 10:
            return 1e9
        return float(np.mean((np.interp(tt[ok], o_ref["t"], o_ref["s"]) - s[ok]) ** 2))
    r = minimize_scalar(cost, bounds=(0.02, 3.0), method="bounded")
    return float(r.x), float(np.sqrt(r.fun))


def main():
    a = sys.argv[1:]
    runs = {}
    for i, x in enumerate(a):
        if x == "--run":
            k, v = a[i + 1].split("=", 1)
            runs[k] = v
    p1 = a[a.index("--p1") + 1]
    refs = json.load(open(a[a.index("--refs") + 1]))
    out = a[a.index("--out") + 1]
    os.makedirs(out, exist_ok=True)
    res = {"runs": runs, "p1": p1}
    O, HZ, HST = {}, {}, {}
    for k, d in list(runs.items()) + [("P1", p1)]:
        O[k] = orbit(d)
        HZ[k] = horizons(d)
        hp = glob.glob(os.path.join(d, "*.z4c.user.hst"))
        HST[k] = nrread.read_hst(hp[0]) if hp else None
    for k, o in O.items():
        r = {}
        if o is None:
            res[k] = dict(status="no tracker data")
            continue
        r["t_end"] = float(o["t"][-1])
        r["s0"] = float(o["s"][0])
        r["s_at"] = {f"{T:g}": value_at(o, T) for T in TS}
        r["ds_at"] = {f"{T:g}": (r["s0"] - v if v is not None else None)
                      for T, v in zip(TS, r["s_at"].values())}
        r["phase_at"] = {f"{T:g}": (float(np.interp(T, o["t"], o["phase"])) if o["t"][-1] >= T
                                    else None) for T in TS}
        below = np.nonzero(o["s"] < 0.1)[0]
        r["t_sep_below_0.1"] = float(o["t"][below[0]]) if len(below) else None
        r["s_min"] = float(o["s"].min())
        # horizons: members (mass < 0.2) and a common horizon (mass > 0.2) in either finder
        hz = {}
        tcommon = None
        for n, h in HZ[k].items():
            if n > 1:                      # P1's finder 2 is the heavy hole
                continue
            mem = h["mass"] < 0.2
            hz[n] = dict(n_found=int(len(h["t"])), n_failed=h["nfail"],
                         first_t=float(h["t"][0]) if len(h["t"]) else None,
                         mass_first=float(h["mass"][0]) if len(h["t"]) else None)
            for T in (5.0, 10.0, 15.0):
                sel = mem & (np.abs(h["t"] - T) <= 0.5)
                hz[n][f"mass_at_{T:g}"] = float(np.median(h["mass"][sel])) if sel.any() else None
            t_hi = min(15.0, float(o["t"][-1]))
            sel = mem & (h["t"] >= 3) & (h["t"] <= t_hi)
            if sel.sum() > 5:
                hz[n]["frac_growth_per_M"] = float(np.polyfit(h["t"][sel], h["mass"][sel], 1)[0]
                                                   / np.median(h["mass"][sel]))
                hz[n]["growth_window"] = [3.0, t_hi]
            sel8 = mem & (h["t"] >= 3) & (h["t"] <= 7.5)
            if sel8.sum() > 5:
                hz[n]["frac_growth_per_M_3_7.5"] = float(np.polyfit(h["t"][sel8], h["mass"][sel8], 1)[0]
                                                         / np.median(h["mass"][sel8]))
            big = np.nonzero((h["mass"] >= 0.2) & (h["mass"] < 0.6))[0]
            if len(big):
                tc = float(h["t"][big[0]])
                tcommon = tc if tcommon is None else min(tcommon, tc)
                hz[n]["common_mass_first"] = float(h["mass"][big[0]])
        r["horizons"] = hz
        r["t_common_horizon"] = tcommon
        if HST[k] is not None:
            hs = HST[k]
            r["H2_at"] = {f"{T:g}": (float(np.interp(T, hs["time"], hs["H2"])) if hs["time"][-1] >= T
                                     else None) for T in (0.0,) + TS}
            r["H2_finite"] = bool(np.all(np.isfinite(hs["H2"])))
        res[k] = r
    for k, d in runs.items():
        res[k]["ledger"] = ledger(d)
    # order and stretch
    conv = {}
    have = [k for k in ("R8", "R12", "R16n") if O.get(k) is not None]
    for T in TS:
        ds = {k: res[k]["ds_at"][f"{T:g}"] for k in have}
        row = {"ds": ds}
        if all(ds.get(k) is not None for k in ("R8", "R12", "R16n")):
            row["p3"] = three_point_order(ds["R8"], ds["R12"], ds["R16n"])
            if row["p3"]:
                p = row["p3"]
                row["ds_continuum"] = ds["R16n"] - (ds["R12"] - ds["R16n"]) * 0.5 ** p / (
                    (2 / 3) ** p - 0.5 ** p)
        if ds.get("R8") and ds.get("R16n") and ds["R8"] > 0 and ds["R16n"] > 0:
            row["p2_8_16"] = float(np.log2(ds["R8"] / ds["R16n"]))
        if ds.get("R8") and ds.get("R12") and ds["R8"] > 0 and ds["R12"] > 0:
            row["p2_8_12"] = float(np.log(ds["R8"] / ds["R12"]) / np.log(1.5))
        conv[f"{T:g}"] = row
    res["convergence"] = conv
    ref8 = O.get("R8") if O.get("R8") is not None and O["R8"]["t"][-1] > 40 else O["P1"]
    ref8_name = "R8" if ref8 is not O["P1"] else "P1"
    tm8 = res[ref8_name].get("t_sep_below_0.1")
    st = {}
    for k in ("R8", "R12", "R16n"):
        if O.get(k) is None:
            continue
        tmax = min(O[k]["t"][-1], ref8["t"][-1], tm8 if tm8 else 1e9)
        lam, rms = stretch(ref8, O[k], tmax)
        st[k] = dict(reference=ref8_name, lam=lam, rms=rms, window=[0.5, float(tmax)],
                     t_merge_estimate=(tm8 / lam if tm8 else None))
    res["stretch"] = st
    # P1b cost: g2mesh model trees of P1's set-up (run F-20261120-222426-86392c3, model.json
    # D_tracks: Newtonian three-body tracks to 280 M) times the cycles per M, divided by the
    # rate measured here (MeshBlock-cycles per second of computing), times the measured ratio of
    # Slurm elapsed time to computing time
    if "--g2model" in a:
        g2 = json.load(open(a[a.index("--g2model") + 1]))
        cost = {}
        rate_all = {k: [r["mbc_per_s"] for r in res[k]["ledger"] if r.get("mbc_per_s")]
                    for k in runs}
        over = [r["elapsed_s"] / r["cpu_s"] for k in runs for r in res[k]["ledger"]
                if r.get("elapsed_s") and r.get("cpu_s")]
        overhead = float(np.mean(over)) if over else 1.03
        for var, own in (("R16n", "R16n"), ("R12", "R12")):
            d = g2["D_tracks"][f"{var}_b16"]
            tt = np.array(d["newton"]["t"])
            nn = np.array(d["newton"]["n"])
            rates = rate_all.get(own) or rate_all.get("R16n") or rate_all.get("R8") or []
            if not rates:
                continue
            rate = float(np.median(rates))
            cyc_per_M = 1.0 / d["dt"]
            row = dict(rate_mbcps=rate, rate_from=own if rate_all.get(own) else "other run",
                       overhead_elapsed_over_cpu=overhead, cycles_per_M=cyc_per_M,
                       tree_max_280=int(nn.max()))
            for T in (150.0, 200.0, 280.0):
                sel = tt <= T
                mean = float(nn[sel].mean())
                ch = T * cyc_per_M * mean / rate / 3600.0 * overhead
                row[f"to_{T:g}"] = dict(tree_mean=mean, card_hours=ch,
                                        segments_of_50min=ch / (3000.0 * overhead / 3600.0))
            cost[var] = row
        res["p1b_cost"] = cost
    with open(os.path.join(out, "analysis.json"), "w") as f:
        json.dump(res, f, indent=1, default=lambda x: None)
    print(json.dumps({k: res.get(k) for k in ("convergence", "stretch", "p1b_cost")}, indent=1, default=str))
    for k in list(runs) + ["P1"]:
        r = res.get(k, {})
        print(k, "t_end", r.get("t_end"), "s_at", r.get("s_at"), "t_common", r.get("t_common_horizon"))

    # ------------------------------------------------------------------ figures
    fs.use_style()
    import matplotlib.pyplot as plt
    tr = np.array(refs["series"]["t"])
    tmax_plot = max([o["t"][-1] for k, o in O.items() if o is not None and k != "P1"] + [20.0])
    tmax_plot = min(max(tmax_plot * 1.15, 25.0), 100.0)
    fig, ax4 = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.2), constrained_layout=True)
    axs = [ax4[0, 0], ax4[0, 1], ax4[1, 1], ax4[1, 0]]   # s(t), phase, Delta s vs h, Delta s(t)
    for name, st_ in (("newton", dict(color=fs.PAL["blue"], lw=1.0, label="Newton")),
                      ("eih_c", dict(color=fs.PAL["blue"], lw=1.0, ls="--", label="EIH, P canonical"))):
        axs[0].plot(tr, refs["series"][name]["sep"], **st_)
        axs[1].plot(tr, refs["series"][name]["phase"], **st_)
        dsr = refs["series"][name]["sep"][0] - np.array(refs["series"][name]["sep"])
        axs[3].loglog(tr[1:], np.abs(dsr[1:]), **st_)
    smin_win = 5.0
    for k in ["P1"] + have:
        o = O[k]
        lab = {"P1": "P1 (three holes, m/8)", "R8": "alone, m/8", "R12": "alone, m/12",
               "R16n": "alone, m/16"}[k]
        ls = ":" if k == "P1" else "-"
        axs[0].plot(o["t"], o["s"], color=COL[k], lw=1.5, ls=ls, label=lab)
        live = o["s"] > 0.3                # phase only while the members are apart
        axs[1].plot(o["t"][live], o["phase"][live], color=COL[k], lw=1.5, ls=ls)
        ds = o["s"][0] - o["s"]
        ok = (o["t"] > 0) & (o["t"] <= tmax_plot)
        axs[3].loglog(o["t"][ok], np.abs(ds[ok]), color=COL[k], lw=1.5, ls=ls)
        win = o["t"] <= tmax_plot
        smin_win = min(smin_win, float(o["s"][win].min()))
    tt = np.array([1.0, tmax_plot])
    axs[3].loglog(tt, 0.0017 * tt ** 2, **fs.MASK_LINE)
    axs[3].text(tt[-1], 0.0017 * tt[-1] ** 2, " t^2", fontsize=6, va="center")
    axs[3].set_xlim(1.0, tmax_plot)
    axs[3].set_ylim(1e-4, 3.0)
    axs[3].set_xlabel("t [M]")
    axs[3].set_ylabel("|s(0) - s(t)| [M]")
    axs[0].set_xlim(0, tmax_plot)
    axs[1].set_xlim(0, tmax_plot)
    axs[0].set_ylim(max(0.0, smin_win - 0.1), 5.4)
    axs[0].set_xlabel("t [M]")
    axs[0].set_ylabel("coordinate separation [M]")
    axs[1].set_xlabel("t [M]")
    axs[1].set_ylabel("orbital phase [rad]")
    axs[0].legend(fontsize=6.5, frameon=False, loc="lower left")
    # Delta s against h at fixed t
    for T, mk in zip((5.0, 7.5, 10.0, 15.0, 20.0), ("o", "v", "s", "^", "D")):
        hs_, dv = [], []
        for k in have:
            v = res[k]["ds_at"][f"{T:g}"]
            if v is not None and v > 0:
                hs_.append(H_OF[k])
                dv.append(v)
        if dv:
            axs[2].loglog(hs_, dv, marker=mk, lw=1.0, label=f"t = {T:g} M")
    hh = np.array([0.5, 1.0])
    anchor = max([v for k in have for v in res[k]["ds_at"].values() if v] + [0.3])
    for p in (1, 2, 4):
        axs[2].loglog(hh, anchor * hh ** p, **fs.MASK_LINE)
        axs[2].text(0.49, anchor * 0.5 ** p, f"p={p}", fontsize=6, ha="right", va="center")
    axs[2].set_xticks([0.5, 2 / 3, 1.0])
    axs[2].set_xticklabels(["1/2", "2/3", "1"])
    axs[2].xaxis.set_minor_formatter(plt.NullFormatter())
    axs[2].set_xlim(0.4, 1.15)
    axs[2].set_xlabel("member cell h [m/8]")
    axs[2].set_ylabel("s(0) - s(t) [M]")
    axs[2].legend(fontsize=6.5, frameon=False)
    fs.save(fig, os.path.join(out, "fig_orbit_conv"))

    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8), constrained_layout=True)
    for k in ["P1"] + have:
        ls = ":" if k == "P1" else "-"
        for n, h in HZ[k].items():
            if k == "P1" and n == 2:
                continue
            axs[0].plot(h["t"], h["mass"], color=COL[k], lw=1.0, ls=ls,
                        label=(k if n == 0 else None))
        if HST[k] is not None:
            axs[1].semilogy(HST[k]["time"], np.sqrt(np.maximum(HST[k]["H2"], 1e-300)),
                            color=COL[k], lw=1.2, ls=ls, label=k)
    axs[0].set_xlim(0, tmax_plot)
    axs[0].set_ylim(0.12, 0.30)
    axs[0].set_xlabel("t [M]")
    axs[0].set_ylabel("horizon mass (finders 0, 1)")
    axs[0].legend(fontsize=6.5, frameon=False)
    axs[1].set_xlim(0, tmax_plot)
    axs[1].set_xlabel("t [M]")
    axs[1].set_ylabel("rms H (history)")
    axs[1].legend(fontsize=6.5, frameon=False)
    fs.save(fig, os.path.join(out, "fig_horizons_H"))


if __name__ == "__main__":
    main()
