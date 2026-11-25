#!/usr/bin/env python3
"""Answers to the fresh verifier of item C18 (stage/G2/VERIFIER-C18.md; decision 0040 items 2, 3),
from the registered card outputs of conv_ball and threshold_ball. Lead of batch 19.

    c18_answer.py --out DIR [--member NAME ...] [--jobs 4]

Per member:
  (1) searches from <base>.horizon_status_0.txt (the only record of found / not found; the
      summary repeats the last accepted surface after a failed search, cosmo_amr.md 2.3):
      number, found, first found, persistence start by the rule of threshold_ball entry 1,
      found in EVERY status row from that start or not; summary rows whose nearest status
      row says "not found" (stale repeats) are counted and dropped below.
  (2) the finder's m_irr against three exact masses on the code's slice, over the true finds:
      'lead'  = compare_tb.py / compare.py as committed (outermost sign change of the
                running median of 9 of tau_p - tau_AH(shell), linear in R_i);
      'last'  = shell of the outermost trapped tracked particle (no smoothing, no interpolation);
      'next'  = shell of the next tracked particle outward (the first untrapped one);
      the bracket of the exact mass the tracked set allows is [m(last), m(next)], so the
      median error lies in [median(err vs next), median(err vs last)];
      also the error over the README's windows (all rows the committed analysis used).
  (3) ddet at first detection (finder's mean radius) with four interpolations across the core
      edge: v2 (committed: tau and label linear in coordinate radius, exact tau_AH at the label),
      vd (tau_p - tau_AH(shell) linear in r), vn (nearest tracked particle), and the two
      bracketing particles' values; the spread is max - min.
  (4) the time measure at first detection: proper time at the finder's radius (tau_det), of the
      core edge's tracked particles, and of the outermost tracked particles (R_i in the top
      tenth of the tracked set), with coordinate time.
Writes c18.json, c18.md and fig_c18_mass_bracket.png, fig_c18_ddet_spread.png.
"""
import argparse
import concurrent.futures as cf
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TRACK, "conv_ball", "scripts"))
import common as C  # noqa: E402

XE = C.XE
S = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
TB = S + "/A-20261121-202812-cae4436"
CB = S + "/A-20261121-075356-1ad4c81"
# name: (run dir, prep dir, m_AH for the persistence rule, claims of the READMEs to compare)
MEMBERS = {
    "cb-A": (S + "/A-20261121-075926-d10c2c1/A", CB + "/nestA"),
    "cb-B": (S + "/A-20261121-075926-d10c2c1/B", CB + "/nestB"),
    "cb-C": (S + "/A-20261121-083336-6a82131", CB + "/nestC"),
    "B-d1.00": (S + "/A-20261122-054155-4b3d92e", TB + "/dc1p0/nestB"),
    "B-d0.70": (S + "/A-20261122-100756-829dcf9", TB + "/dc0p7/nestB"),
    "B-d0.50": (S + "/A-20261122-051554-7662f22", TB + "/dc0p5/nestB"),
    "B-d0.45": (S + "/A-20261122-003952-552f805", TB + "/dc0p45/nestB"),
    "B-d0.42": (S + "/A-20261121-204149-c48bd33", TB + "/dc0p42/nestB"),
    "B-d0.40": (S + "/A-20261121-204250-0bf45c7", TB + "/dc0p4/nestB"),
    "B-d0.35": (S + "/A-20261122-101357-9a73701", TB + "/dc0p35/nestB"),
    "B-d0.20": (S + "/A-20261122-132959-dfba903", TB + "/dc0p2/nestB"),
    "A-d0.42": (S + "/A-20261121-235851-d2200d7/A-d0.42", TB + "/dc0p42/nestA"),
    "A-d0.40": (S + "/A-20261121-235851-d2200d7/A-d0.40", TB + "/dc0p4/nestA"),
    "C-R1.25": (S + "/A-20261122-141100-f00cfc2", TB + "/R1p25/nestC"),
    "C-d0.42": (S + "/A-20261122-173202-f98c79f", TB + "/dc0p42/nestC"),
}
# values as printed in the READMEs (conv_ball/README.md, threshold_ball/README.md), for the table
CLAIM = {"cb-A": dict(dmmed=7.4e-3, ddet=0.193), "cb-B": dict(dmmed=-2.1e-3, ddet=0.068),
         "cb-C": dict(dmmed=-2.1e-4, ddet=0.017),
         "B-d1.00": dict(dmmed=-3.8e-4), "B-d0.70": dict(dmmed=-1.9e-3), "B-d0.50": dict(dmmed=-9.4e-3),
         "B-d0.45": dict(dmmed=1.9e-3), "B-d0.42": dict(dmmed=2.8e-3, ddet=0.0153),
         "B-d0.40": dict(dmmed=3.2e-4), "B-d0.35": dict(dmmed=2.4e-3),
         "A-d0.42": dict(dmmed=-3.8e-2), "A-d0.40": dict(dmmed=-4.6e-2),
         "C-R1.25": dict(ddet=0.040), "C-d0.42": dict(dmmed=2.36e-2, ddet=-0.0135)}


def status_rows(rd):
    p = os.path.join(rd, "ball.horizon_status_0.txt")
    rows = []
    if os.path.isfile(p):
        for ln in open(p):
            if ln.startswith("#") or not ln.strip():
                continue
            v = ln.split("#")[0].split()
            rows.append((float(v[1]), int(v[2])))
    a = np.array(rows) if rows else np.zeros((0, 2))
    keep, tn = [], np.inf                    # repeated times after a restart: last written wins
    for i in range(len(a) - 1, -1, -1):
        if a[i, 0] < tn:
            keep.append(i)
            tn = a[i, 0]
    return a[keep[::-1]]


def persistence(st, m_ah):
    found = st[:, 1] > 0 if len(st) else np.zeros(0, bool)
    for i in range(len(found)):
        if found[i:].all():
            n, span = len(found) - i, st[-1, 0] - st[i, 0]
            return (i if (n >= 3 and span >= 5 * m_ah) else None), int(found[:i].sum())
    return None, int(found.sum())


def one(name):
    rd, prep = MEMBERS[name]
    tr = C.load_json(os.path.join(prep, "tracked.json"))
    ex = C.load_json(os.path.join(prep, "exact.json"))
    ball = C.ball_from_spec(ex.get("spec"))
    m_ah = float(ex["first_trapped"]["m"])
    out = dict(name=name, run=rd, prep=prep, m_ah_core_edge=m_ah, tau_ah_core_edge=float(ex["first_trapped"]["tau"]))
    st = status_rows(rd)
    fi, iso = persistence(st, m_ah)
    out["status"] = dict(n=int(len(st)), found=int(st[:, 1].sum()) if len(st) else 0,
                         first_found_t=float(st[st[:, 1] > 0][0, 0]) if len(st) and st[:, 1].any() else None,
                         persistent_from_t=float(st[fi, 0]) if fi is not None else None,
                         n_from_persistence=int(len(st) - fi) if fi is not None else 0,
                         all_found_from_persistence=bool(st[fi:, 1].all()) if fi is not None else None,
                         isolated_before=iso, last_t=float(st[-1, 0]) if len(st) else None,
                         search_interval=float(np.median(np.diff(st[:, 0]))) if len(st) > 2 else None)
    hz = C.read_horizon([rd], "ball")
    if len(hz) == 0:
        out["summary"] = dict(n=0)
        return out
    # each summary row against the nearest status row; without a status file (runs made before
    # <fastflow> diagnostics existed) a row equal in mass, area and radius to the row before it
    # is taken as a repeat of the last accepted surface (inferred, said so in the output)
    if len(st) >= 2:
        stt = st[:, 0]
        j = np.clip(np.searchsorted(stt, hz[:, 1]), 1, len(stt) - 1)
        j = np.where(np.abs(stt[j - 1] - hz[:, 1]) <= np.abs(stt[j] - hz[:, 1]), j - 1, j)
        true_find = st[j, 1] > 0
        out["summary"] = dict(n=int(len(hz)), stale=int((~true_find).sum()), source="status file",
                              max_dt_match=float(np.max(np.abs(stt[j] - hz[:, 1]))))
    else:
        same = np.zeros(len(hz), bool)
        same[1:] = np.all(hz[1:, 2:11] == hz[:-1, 2:11], axis=1)
        true_find = ~same
        out["summary"] = dict(n=int(len(hz)), stale=int(same.sum()),
                              source="no status file: repeats inferred from identical consecutive rows")
        pst = np.column_stack([hz[:, 1], true_find.astype(float)])
        fi2, iso2 = persistence(pst, m_ah)
        out["status"].update(n=int(len(hz)), found=int(true_find.sum()), first_found_t=float(hz[0, 1]),
                             persistent_from_t=float(pst[fi2, 0]) if fi2 is not None else None,
                             n_from_persistence=int(len(pst) - fi2) if fi2 is not None else 0,
                             all_found_from_persistence=bool(pst[fi2:, 1].all()) if fi2 is not None else None,
                             isolated_before=iso2, last_t=float(pst[-1, 0]),
                             note="no status file; searches before the first find are not in the summary")
    # trajectories of the tracked particles (as compare_tb.py)
    T = C.read_traj_many([rd], "ball")
    keep = T["tag"] < tr["n_track"]
    tags = T["tag"][keep]
    for k in ("x", "g", "tau"):
        T[k] = T[k][:, keep]
    t = T["time"]
    Ri = np.array(tr["R_i"])[tags]
    r0 = np.array(tr["rbar0"])[tags]
    sh = XE.Shells(ball, Ri)
    _, r, _ = C.areal_radius(T["x"], T["g"])
    tau = T["tau"]
    m_sh = np.asarray(sh.m)
    outer = Ri >= np.quantile(Ri, 0.9)
    edge = np.abs(Ri - ex["first_trapped"]["R_i"]) <= 0.03
    rows = []
    for k_, row in enumerate(hz):
        th_, area, rmean = row[1], row[7], row[10]
        mirr = math.sqrt(area / (16.0 * math.pi)) if area > 0 else np.nan
        it = int(np.argmin(np.abs(t - th_)))
        jb = int(np.searchsorted(t, th_))
        if 0 < jb < len(t) and t[jb] > t[jb - 1]:
            wb = (th_ - t[jb - 1]) / (t[jb] - t[jb - 1])
            tp = (1.0 - wb) * tau[jb - 1] + wb * tau[jb]
            tp = np.where(np.isfinite(tp), tp, tau[it])
            ra = (1.0 - wb) * r[jb - 1] + wb * r[jb]
            ra = np.where(np.isfinite(ra), ra, r[it])
        else:
            tp, ra = tau[it], r[it]
        q = dict(t=float(th_), found=bool(true_find[k_]), m_irr=mirr, r_mean=float(rmean))
        okp = np.isfinite(tp) & np.isfinite(sh.tau_ah) & (Ri > ex["first_trapped"]["R_i"] - 0.05)
        q["m_lead"] = q["m_last"] = q["m_next"] = np.nan
        if np.any(okp):
            o = np.argsort(Ri[okp])
            Rs, d, ms = Ri[okp][o], (tp[okp] - sh.tau_ah[okp])[o], m_sh[okp][o]
            dm = np.array([np.median(d[max(0, i - 4):i + 5]) for i in range(len(d))]) if len(d) > 9 else d
            pos = np.nonzero(dm >= 0)[0]
            if len(pos) and pos.max() + 1 < len(dm):
                jj = pos.max()
                w = dm[jj] / (dm[jj] - dm[jj + 1])
                q["m_lead"] = float(ball.at(np.array([Rs[jj] + w * (Rs[jj + 1] - Rs[jj])]))["m"][0])
            pr = np.nonzero(d >= 0)[0]
            if len(pr) and pr.max() + 1 < len(d):
                q["m_last"], q["m_next"] = float(ms[pr.max()]), float(ms[pr.max() + 1])
                q["R_last"], q["R_next"] = float(Rs[pr.max()]), float(Rs[pr.max() + 1])
        # ddet variants at the finder's radius
        okh = np.isfinite(ra) & np.isfinite(tp) & np.isfinite(sh.tau_ah)
        oh = np.argsort(ra[okh])
        rr, tt_, lab, dd = ra[okh][oh], tp[okh][oh], r0[okh][oh], (tp - sh.tau_ah)[okh][oh]
        tau_h = float(np.interp(rmean, rr, tt_))
        lab_h = float(np.interp(rmean, rr, lab))
        tah_lab = float(XE.Shells(ball, np.array([min(float(ball.R_of_rbar(np.array([lab_h]))[0]),
                                                      ball.R_out)])).tau_ah[0])
        kb = int(np.clip(np.searchsorted(rr, rmean), 1, len(rr) - 1))
        q.update(tau_det=tau_h, ddet_v2=tau_h - tah_lab, ddet_vd=float(np.interp(rmean, rr, dd)),
                 ddet_vn=float(dd[int(np.argmin(np.abs(rr - rmean)))]),
                 ddet_in=float(dd[kb - 1]), ddet_out=float(dd[kb]),
                 r_in=float(rr[kb - 1]), r_out=float(rr[kb]), lab_h=lab_h,
                 tau_outer=float(np.nanmedian(tp[outer])),
                 tau_edge=float(np.nanmedian(tp[edge])) if edge.any() else None)
        rows.append(q)
    out["rows"] = rows
    tf = [q for q in rows if q["found"]]

    def med(key, sel):
        v = np.array([q["m_irr"] / q[key] - 1.0 for q in sel if np.isfinite(q[key])])
        return (float(np.median(v)), int(len(v))) if len(v) else (None, 0)
    out["mass"] = {}
    for lab_, sel in (("all_rows", rows), ("true_finds", tf)):
        dd_ = {}
        for key in ("m_lead", "m_last", "m_next"):
            dd_[key] = med(key, sel)
        # rows where both ends exist: per-row bracket and its median ends
        both = [q for q in sel if np.isfinite(q["m_last"]) and np.isfinite(q["m_next"])]
        dd_["bracket_median"] = ([float(np.median([q["m_irr"] / q["m_next"] - 1 for q in both])),
                                  float(np.median([q["m_irr"] / q["m_last"] - 1 for q in both]))]
                                 if both else None)
        dd_["bracket_width_rel_median"] = (float(np.median([q["m_next"] / q["m_last"] - 1 for q in both]))
                                           if both else None)
        out["mass"][lab_] = dd_
    f0 = tf[0] if tf else rows[0]
    v = [f0["ddet_v2"], f0["ddet_vd"], f0["ddet_vn"], f0["ddet_in"], f0["ddet_out"]]
    out["first"] = dict(f0, ddet_spread=float(max(v) - min(v)), ddet_min=float(min(v)), ddet_max=float(max(v)))
    return out


def fmt(x, f="%.3g"):
    return "-" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f % x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--member", action="append", default=None)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    names = a.member or list(MEMBERS)
    with cf.ProcessPoolExecutor(max_workers=a.jobs) as ex:
        res = dict(zip(names, ex.map(one, names)))
    json.dump(res, open(os.path.join(a.out, "c18.json"), "w"), indent=1, default=float)
    L = ["# C18 answers (c18_answer.py)", "",
         "## Searches from the status file", "",
         "| member | searches | found | first found | persistent from | rows from there | all found from there | isolated before | summary rows | stale summary rows |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for n in names:
        s, sm = res[n]["status"], res[n]["summary"]
        nosf = " (no status file)" if "note" in s else ""
        L.append(f"| {n}{nosf} | {s['n']} | {s['found']} | {fmt(s['first_found_t'], '%.5f')} | "
                 f"{fmt(s['persistent_from_t'], '%.5f')} | {s['n_from_persistence']} | {s['all_found_from_persistence']} | "
                 f"{s['isolated_before']} | {sm['n']} | {sm.get('stale', '-')} |")
    L += ["", "## Horizon mass: median of m_irr/m_exact - 1 over the true finds", "",
          "| member | README claim | lead convention (rows used before) | lead, true finds | vs last trapped particle | vs next particle | bracket of the median | bracket width (median, rel.) | n |",
          "|---|---|---|---|---|---|---|---|---|"]
    for n in names:
        if "mass" not in res[n]:
            continue
        M, Ma = res[n]["mass"]["true_finds"], res[n]["mass"]["all_rows"]
        br = M["bracket_median"]
        L.append(f"| {n} | {fmt(CLAIM.get(n, {}).get('dmmed'))} | {fmt(Ma['m_lead'][0])} (n {Ma['m_lead'][1]}) | "
                 f"{fmt(M['m_lead'][0])} | {fmt(M['m_last'][0])} | {fmt(M['m_next'][0])} | "
                 f"{'[' + fmt(br[0]) + ', ' + fmt(br[1]) + ']' if br else '-'} | {fmt(M['bracket_width_rel_median'])} | {M['m_last'][1]} |")
    L += ["", "## Detection time at the first true find: ddet (M) under four interpolations", "",
          "| member | README | v2 (committed) | vd (difference linear in r) | vn (nearest particle) | inner / outer bracketing particle | spread | finder r, bracketing r | t | tau_det | tau core edge | tau outer layers |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n in names:
        f = res[n].get("first")
        if not f:
            continue
        L.append(f"| {n} | {fmt(CLAIM.get(n, {}).get('ddet'))} | {f['ddet_v2']:+.4f} | {f['ddet_vd']:+.4f} | "
                 f"{f['ddet_vn']:+.4f} | {f['ddet_in']:+.4f} / {f['ddet_out']:+.4f} | {f['ddet_spread']:.4f} | "
                 f"{f['r_mean']:.4f} ({f['r_in']:.4f}, {f['r_out']:.4f}) | {f['t']:.5f} | {f['tau_det']:.4f} | "
                 f"{fmt(f['tau_edge'], '%.4f')} | {f['tau_outer']:.4f} |")
    open(os.path.join(a.out, "c18.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    # figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(TRACK, "periodic_threshold", "scripts"))
    import figstyle as fs
    fs.use_style()
    mn = [n for n in names if "mass" in res[n] and res[n]["mass"]["true_finds"]["bracket_median"]]
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.27, top=0.9, wspace=0.28)
    x = np.arange(len(mn))
    for i, n in enumerate(mn):
        M = res[n]["mass"]["true_finds"]
        lo, hi = M["bracket_median"]
        axs[0].plot([i, i], [lo, hi], color=fs.PAL["blue"], lw=4, alpha=0.5, solid_capstyle="butt")
        if M["m_lead"][0] is not None:
            axs[0].plot(i, M["m_lead"][0], "o", color="k", ms=4)
        c = CLAIM.get(n, {}).get("dmmed")
        if c is not None:
            axs[0].plot(i, c, "x", color=fs.PAL["red"], ms=6)
    axs[0].axhline(0, color="0.6", lw=0.6)
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(mn, rotation=60, fontsize=6)
    axs[0].set_ylabel(r"median $m_{\rm irr}/m_{\rm exact}-1$")
    axs[0].set_title("bar: exact mass between tracked particles; o lead; x README", fontsize=7)
    axs[0].set_ylim(-0.06, 0.06)
    dn = [n for n in names if res[n].get("first")]
    for i, n in enumerate(dn):
        f = res[n]["first"]
        axs[1].plot([i, i], [f["ddet_min"], f["ddet_max"]], color=fs.PAL["blue"], lw=4, alpha=0.5, solid_capstyle="butt")
        axs[1].plot(i, f["ddet_v2"], "o", color="k", ms=4)
        c = CLAIM.get(n, {}).get("ddet")
        if c is not None:
            axs[1].plot(i, c, "x", color=fs.PAL["red"], ms=6)
    axs[1].axhline(0, color="0.6", lw=0.6)
    axs[1].set_xticks(np.arange(len(dn)))
    axs[1].set_xticklabels(dn, rotation=60, fontsize=6)
    axs[1].set_ylabel(r"$\Delta\tau_{\rm det}$ (M) at first true find")
    axs[1].set_title("bar: four interpolations; o committed (v2); x README", fontsize=7)
    fig.savefig(os.path.join(a.out, "fig_c18_mass_bracket.png"), dpi=150)


if __name__ == "__main__":
    main()
