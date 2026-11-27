#!/usr/bin/env python3
"""Verifier's own readers of the G2 card runs of Track C (V2-V5).

Reads, from the registered output directories scratch/C-sidm/<run_id>/, the files
cc.nrpic.hst (particle history), cc.cstat.hst and cc.z4c.user.hst (constraints) and
cc.coll.hst (collision records), each checked against the sha256 its run recorded in
sha256sums.txt. Comment lines are skipped anywhere; the restart rule is applied: a row whose
time is not later than the last kept row replaces every kept row from its time on.

Collapse marker: the first record with alpha_min (column 16 of cc.nrpic.hst) below 0.3; the
time is the linear crossing between that record and the one before it. It is a marker on the
slice, not a horizon.

A self-test on a synthetic history with a known crossing and an overlapping continuation runs
first; the script stops if it fails.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import sys

import numpy as np

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
THRESH = {
    "N4c": "C-20261125-132112-edf3fbc", "A334s1c": "C-20261121-214601-40dc927",
    "N6c": "C-20261124-221122-928c9eb", "A344s1i": "C-20261122-220118-ab099ac",
    "A324s1i": "C-20261123-221955-a773578", "N6b344": "C-20261125-224959-d1d4494",
    "N6b324": "C-20261126-020831-fabf2d7", "A16b344": "C-20261126-043714-8ea1c35",
    "A16b324": "C-20261126-121449-1d37e77", "N6b344e1": "C-20261126-050124-00e10ae",
    "N6b324e1": "C-20261126-130519-1a79a66",
}
COLL = {
    "D2ctl": "C-20261122-103854-4670b59", "D2f1s1": "C-20261122-144455-6e0992e",
    "D2f2s1": "C-20261122-141414-399ad97", "D2f4s1": "C-20261122-181011-60baef9",
    "D2f2s2": "C-20261124-035054-c06503f", "M16": "C-20261125-044843-2d048b6",
    "D2eta1": "C-20261126-034500-4b34b1c",
    "M4s1": "C-20261120-221846-797bdbe/cc2_kn10_part_s1",
    "M4s2": "C-20261120-221846-797bdbe/cc2_kn10_part_s2",
}
CLAIMED = {  # what the package claims (RERUN.md section 1, Table VI of the note)
    "N4c": 295.78, "A334s1c": 534.81, "N6c": None, "A344s1i": 229.79, "A324s1i": None,
    "N6b344": 252.31, "N6b324": None, "A16b344": 217.97, "A16b324": None,
    "N6b344e1": 252.41, "N6b324e1": None,
    "D2f1s1": 164.01, "D2f2s1": 163.41, "D2f4s1": 165.97, "D2f2s2": 165.65, "M16": 158.42,
    "D2eta1": 164.01, "M4mean": 206.64, "D2ctl": None,
}
SHA_CHECKED = []


def run_dir(rid):
    return os.path.join(SCR, rid)


def sha_ok(path):
    """Compare the file's sha256 with the line of the run's sha256sums.txt (run root)."""
    d = os.path.dirname(path)
    rel = os.path.basename(path)
    # sha256sums.txt sits at the run root; batch members are one level deeper
    for root in (d, os.path.dirname(d)):
        f = os.path.join(root, "sha256sums.txt")
        if os.path.exists(f):
            relp = os.path.relpath(path, root)
            want = None
            for line in open(f):
                parts = line.split()
                if len(parts) >= 2 and parts[-1].lstrip("*").lstrip("./") == relp:
                    want = parts[0]
            if want is None:
                SHA_CHECKED.append((path, "not listed"))
                return False
            h = hashlib.sha256()
            with open(path, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 22), b""):
                    h.update(chunk)
            ok = h.hexdigest() == want
            SHA_CHECKED.append((path, "ok" if ok else "MISMATCH"))
            return ok
    SHA_CHECKED.append((path, "no sha256sums.txt"))
    return False


def read_hist(path, check=True):
    """Rows of a whitespace history file, comment lines skipped, restart rule applied."""
    if check:
        sha_ok(path)
    rows = []
    nrestart = 0
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            v = [float(x) for x in s.split()]
            if rows and v[0] <= rows[-1][0]:
                nrestart += 1
                while rows and rows[-1][0] >= v[0]:
                    rows.pop()
            rows.append(v)
    ncol = min(len(r) for r in rows)
    return np.array([r[:ncol] for r in rows]), nrestart


def crossing(t, a, level=0.3):
    below = np.where(a < level)[0]
    if len(below) == 0:
        return None, None
    i = below[0]
    if i == 0:
        return float(t[0]), 0
    t0, t1, a0, a1 = t[i - 1], t[i], a[i - 1], a[i]
    return float(t0 + (level - a0) * (t1 - t0) / (a1 - a0)), int(i)


def self_test(tmpdir):
    os.makedirs(tmpdir, exist_ok=True)
    p = os.path.join(tmpdir, "synthetic.hst")
    with open(p, "w") as fh:
        fh.write("# header\n# [1]=time [2]=alpha_min\n")
        for t in np.arange(0, 150.25, 0.25):  # first segment: false dip after 120 M
            fh.write(f"{t:.6e} {0.2 if t > 120 else 1 - 0.003 * t:.15e}\n")
        fh.write("# header repeated by the continuation\n")
        for t in np.arange(100, 300.25, 0.25):  # continuation from 100 M: the true values
            fh.write(f"{t:.6e} {1 - 0.003 * t:.15e}\n")
    h, nr = read_hist(p, check=False)
    tc, _ = crossing(h[:, 0], h[:, 1])
    ok = (nr == 1 and abs(tc - 700.0 / 3.0) < 1e-9 and len(h) == 1201
          and np.all(np.diff(h[:, 0]) > 0))
    # without the restart rule the false dip would give 120.25 M
    return dict(restarts_seen=nr, t_cross=tc, exact=700.0 / 3.0, rows=len(h), ok=bool(ok))


def deck_lines(path):
    out = []
    for line in open(path):
        s = line.split("#")[0].strip()
        if s:
            out.append(re.sub(r"\s+", " ", s))
    return out


def deck_diff(a, b):
    la, lb = deck_lines(a), deck_lines(b)
    d = [x for x in difflib.unified_diff(la, lb, lineterm="", n=0)
         if (x.startswith("+") or x.startswith("-")) and not x.startswith(("+++", "---"))]
    return d


def find_deck(rid):
    for c in ("chain/input.athinput",):
        p = os.path.join(run_dir(rid), c)
        if os.path.exists(p):
            return p
    d = run_dir(rid)
    for f in os.listdir(d):
        if f.endswith(".athinput"):
            return os.path.join(d, f)
    return None


def horizon_files(rid):
    hits = []
    pat = re.compile(r"(horizon|ahf|\.ah\.|fastflow|\.ah$)", re.I)
    for root, _dirs, files in os.walk(run_dir(rid)):
        for f in files:
            if pat.search(f):
                hits.append(os.path.relpath(os.path.join(root, f), SCR))
    return hits


def block_means(t, y, width=20.0, tmax=600.0):
    out = []
    for k in range(int(tmax / width)):
        m = (t >= k * width) & (t < (k + 1) * width)
        if m.sum() == 0:
            break
        out.append(float(y[m].mean()))
    return np.array(out)


def analyse_threshold(name, rid):
    d = run_dir(rid)
    h, nr = read_hist(os.path.join(d, "cc.nrpic.hst"))
    t, amin, ac = h[:, 0], h[:, 15], h[:, 12]
    tc, ic = crossing(t, amin)
    r = dict(run=rid, restarts=nr, t_end=float(t[-1]), n_rows=len(t), alpha_min_min=float(amin.min()),
             t_cross=tc, claimed=CLAIMED[name], np0=int(h[0, 2]),
             n_excised_max=int(h[:, 16].max()), t_first_excision=(float(t[np.argmax(h[:, 16] > 0)])
                                                                  if (h[:, 16] > 0).any() else None))
    if ic is not None:
        r["record_before"] = [float(t[ic - 1]), float(amin[ic - 1])]
        r["record_after"] = [float(t[ic]), float(amin[ic])]
    bm = block_means(t, ac - ac[0])
    r["alpha_c0"] = float(ac[0])
    r["block_means"] = bm.tolist()
    if tc is None:
        r["block_min"], r["block_max"] = float(bm.min()), float(bm.max())
    # constraints, 100-300 M
    cs, _ = read_hist(os.path.join(d, "cc.cstat.hst"))
    m = (cs[:, 0] >= 100) & (cs[:, 0] <= 300)
    r["H_mean_100_300"] = dict(mean=float(cs[m, 9].mean()), median=float(np.median(cs[m, 9])))
    r["H_max_100_300"] = dict(mean=float(cs[m, 8].mean()), median=float(np.median(cs[m, 8])))
    zu, _ = read_hist(os.path.join(d, "cc.z4c.user.hst"))
    m = (zu[:, 0] >= 100) & (zu[:, 0] <= 300)
    r["Hnorm2_100_300"] = dict(mean=float(zu[m, 3].mean()), median=float(np.median(zu[m, 3])))
    r["horizon_files"] = horizon_files(rid)
    deck = find_deck(rid)
    r["deck"] = os.path.relpath(deck, SCR) if deck else None
    if deck:
        txt = open(deck).read()
        r["deck_horizon_block"] = bool(re.search(r"<(fastflow|ahf|horizon)", txt, re.I))
    r["_series"] = dict(t=t, amin=amin, ac=ac)
    return r


def analyse_coll(name, rid):
    d = run_dir(rid)
    h, nr = read_hist(os.path.join(d, "cc.nrpic.hst"))
    t, amin = h[:, 0], h[:, 15]
    tc, _ = crossing(t, amin)
    exc = h[:, 16] > 0
    t_exc = float(t[np.argmax(exc)]) if exc.any() else None
    r = dict(run=rid, restarts=nr, t_end=float(t[-1]), t_cross=tc, claimed=CLAIMED.get(name),
             np0=int(h[0, 2]), t_first_excision=t_exc, horizon_files=horizon_files(rid),
             alpha_min_min=float(amin.min()), t_alpha_min_min=float(t[np.argmin(amin)]),
             nonfinite_rows=int((~np.isfinite(h)).any(axis=1).sum()))
    deck = find_deck(rid)
    if deck:
        r["deck"] = os.path.relpath(deck, SCR)
        r["deck_horizon_block"] = bool(re.search(r"<(fastflow|ahf|horizon)", open(deck).read(), re.I))
    cp = os.path.join(d, "cc.coll.hst")
    if os.path.exists(cp):
        c, ncr = read_hist(cp)
        tt = c[:, 0]
        w = (tt > 0) & (tt <= 100.0 + 1e-9)
        n, P = c[w, 6].sum(), c[w, 5].sum()
        r["coll_0_100"] = dict(n_coll=float(n), sum_P=float(P), ratio=float(n / P),
                               z=float((n - P) / np.sqrt(P)),
                               per_particle_per_M=float(n / r["np0"] / 100.0),
                               two_per_particle_per_M=float(2 * n / r["np0"] / 100.0))
        # count test by window: collisions against the code's expectation sum_P, and with the
        # accepted pairs left unscattered (n_noroot, column 34) and the detailed-balance
        # rejections (n_balance, column 36) added back
        r["count_windows"] = {}
        if tc is not None:
            for lab, lo, hi in (("0-100", 0.0, 100.0), ("0-tc", 0.0, tc), ("tc-tc+8", tc, tc + 8.0)):
                ww = (tt > lo) & (tt <= hi)
                nn, PP = c[ww, 6].sum(), c[ww, 5].sum()
                rej = c[ww, 33].sum() + c[ww, 35].sum() if c.shape[1] >= 36 else 0.0
                r["count_windows"][lab] = dict(
                    lo=lo, hi=float(hi), n_coll=float(nn), sum_P=float(PP), ratio=float(nn / PP),
                    z=float((nn - PP) / np.sqrt(PP)), rejected=float(rej),
                    ratio_with_rejected=float((nn + rej) / PP),
                    z_with_rejected=float((nn + rej - PP) / np.sqrt(PP)),
                    n_trunc=float(c[ww, 8].sum()), max_P=float(c[ww, 9].max()))
        upto = t_exc if t_exc is not None else tt[-1]
        w2 = tt <= upto
        r["coll_to_exc"] = dict(t_upto=float(upto), n_coll=float(c[w2, 6].sum()),
                                sum_P=float(c[w2, 5].sum()),
                                ratio=float(c[w2, 6].sum() / c[w2, 5].sum()),
                                z=float((c[w2, 6].sum() - c[w2, 5].sum()) / np.sqrt(c[w2, 5].sum())))
        if c.shape[1] >= 33:
            MH0 = c[0, 31]
            r["energy"] = dict(sum_MH0=float(MH0),
                               sum_dH_over_MH=float(c[w2, 32].sum() / MH0),
                               sum_abs_dH_over_MH=float(np.abs(c[w2, 32]).sum() / MH0),
                               max_abs_cum_dH_over_MH=float(np.abs(np.cumsum(c[w2, 32])).max() / MH0),
                               sum_dE_over_MH=float(c[w2, 30].sum() / MH0),
                               sum_abs_dE_over_MH=float(np.abs(c[w2, 30]).sum() / MH0))
        r["_coll"] = dict(t=tt, n=c[:, 6], P=c[:, 5])
    r["_series"] = dict(t=t, amin=amin, ac=h[:, 12])
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"self_test": self_test(os.path.join(a.out, "selftest"))}
    print("self test", res["self_test"])
    if not res["self_test"]["ok"]:
        sys.exit(1)
    res["threshold"] = {k: analyse_threshold(k, v) for k, v in THRESH.items()}
    res["collisional"] = {k: analyse_coll(k, v) for k, v in COLL.items()}
    m4 = [res["collisional"][k]["t_cross"] for k in ("M4s1", "M4s2")]
    res["M4_mean"] = float(np.mean(m4)) if None not in m4 else None
    # deck differences of the legs
    dk = {k: os.path.join(SCR, res["threshold"][k]["deck"]) for k in THRESH}
    res["deck_diffs"] = {
        "N6b344->A16b344": deck_diff(dk["N6b344"], dk["A16b344"]),
        "N6b344->N6b344e1": deck_diff(dk["N6b344"], dk["N6b344e1"]),
        "N6b324->A16b324": deck_diff(dk["N6b324"], dk["A16b324"]),
        "N6b324->N6b324e1": deck_diff(dk["N6b324"], dk["N6b324e1"]),
        "N6c->N6b344": deck_diff(dk["N6c"], dk["N6b344"]),
        "N6c->N6b324": deck_diff(dk["N6c"], dk["N6b324"]),
        "N6c->N4c": deck_diff(dk["N6c"], dk["N4c"]),
        "N6c->A334s1c": deck_diff(dk["N6c"], dk["A334s1c"]),
    }
    # gauge leg of the stable member: block-mean difference eta1 - eta2
    s1, s2 = res["threshold"]["N6b324e1"]["_series"], res["threshold"]["N6b324"]["_series"]
    n = min(len(s1["t"]), len(s2["t"]))
    assert np.allclose(s1["t"][:n], s2["t"][:n])
    diff = block_means(s1["t"][:n], s1["ac"][:n] - s2["ac"][:n])
    res["gauge_leg_stable_maxabs_blockdiff"] = float(np.abs(diff).max())
    # derived numbers
    T = res["threshold"]
    res["mesh_shift_unstable"] = (T["N6b344"]["t_cross"] - T["A16b344"]["t_cross"]) / T["N6b344"]["t_cross"]
    res["gauge_shift_unstable"] = (T["N6b344e1"]["t_cross"] - T["N6b344"]["t_cross"]) / T["N6b344"]["t_cross"]
    C = res["collisional"]
    res["seed_pair_diff"] = C["D2f2s2"]["t_cross"] - C["D2f2s1"]["t_cross"]
    res["sha_checks"] = SHA_CHECKED
    res["sha_all_ok"] = all(s == "ok" for _p, s in SHA_CHECKED)

    # figure
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    P = fs.PAL
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    ax = axs[0, 0]
    for k, c in (("N4c", P["orange"]), ("A334s1c", P["red"]), ("N6c", P["blue"])):
        s = T[k]["_series"]
        ax.plot(s["t"], s["amin"], color=c, lw=1.0, label=f"{k} (N={T[k]['np0']:.0e})")
        if T[k]["t_cross"]:
            ax.plot([T[k]["t_cross"]], [0.3], "x", color=c, ms=6)
    ax.axhline(0.3, **fs.GUIDE)
    ax.set_title("(a) controls $y_0=0.334032$, M/8", fontsize=8)
    ax = axs[0, 1]
    for k, c, ls in (("N6b344", P["red"], "-"), ("A16b344", P["red"], "--"), ("N6b344e1", P["orange"], ":"),
                     ("N6b324", P["blue"], "-"), ("A16b324", P["blue"], "--"), ("N6b324e1", P["green"], ":"),
                     ("A344s1i", P["yellow"], "-"), ("A324s1i", P["yellow"], "--")):
        s = T[k]["_series"]
        ax.plot(s["t"], s["amin"], color=c, lw=1.0, ls=ls, label=k)
        if T[k]["t_cross"]:
            ax.plot([T[k]["t_cross"]], [0.3], "x", color=c, ms=6)
    ax.axhline(0.3, **fs.GUIDE)
    ax.set_title("(b) kicked bracket members", fontsize=8)
    ax = axs[1, 0]
    for k, c, ls in (("N6b324", P["blue"], "-"), ("A16b324", P["blue"], "--"), ("N6b324e1", P["green"], ":"),
                     ("A324s1i", P["yellow"], "--"), ("N6c", "k", "-")):
        s = T[k]["_series"]
        ax.plot(s["t"], s["ac"] - s["ac"][0], color=c, lw=0.8, ls=ls, label=k)
    ax.axhline(0.03, **fs.MASK_LINE)
    ax.axhline(-0.03, **fs.MASK_LINE)
    ax.set_ylabel(r"$\alpha_c-\alpha_c(0)$")
    ax.set_title("(c) central lapse of the members that hold", fontsize=8)
    ax = axs[1, 1]
    for k, c, ls in (("D2f2s1", P["red"], "-"), ("D2f2s2", P["red"], ":"), ("D2f1s1", P["orange"], "-"),
                     ("D2f4s1", P["yellow"], "-"), ("M16", P["blue"], "--"), ("D2eta1", P["green"], ":"),
                     ("M4s1", "0.4", "-"), ("M4s2", "0.4", ":"), ("D2ctl", "k", "-")):
        s = C[k]["_series"]
        ax.plot(s["t"], s["amin"], color=c, lw=0.9, ls=ls, label=k)
        if C[k]["t_cross"]:
            ax.plot([C[k]["t_cross"]], [0.3], "x", color=c, ms=5)
    ax.axhline(0.3, **fs.GUIDE)
    ax.set_ylim(0.0, 0.85)  # M4s2 leaves the range after its first excision (alpha_min < -1e8)
    ax.set_title(r"(d) CC2, Kn$_c$=10: three meshes, seeds, cells, gauge", fontsize=8)
    for ax in axs.flat:
        ax.set_xlabel("$t/M$")
        ax.legend(fontsize=5.5, frameon=False, ncol=2)
    for ax in (axs[0, 0], axs[0, 1], axs[1, 1]):
        ax.set_ylabel(r"$\alpha_{\min}$")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_v2_fates"))

    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items() if not k.startswith("_")}
        return o
    json.dump(strip(res), open(os.path.join(a.out, "fates.json"), "w"), indent=1)
    # summary
    for k, v in T.items():
        print(f"{k:9s} tc={v['t_cross']} claimed={v['claimed']} t_end={v['t_end']} restarts={v['restarts']}"
              f" amin_min={v['alpha_min_min']:.4f} blocks=[{v.get('block_min', float('nan')):+.4f},"
              f"{v.get('block_max', float('nan')):+.4f}] Hmean={v['H_mean_100_300']['mean']:.3e}"
              f" Hn2={v['Hnorm2_100_300']['mean']:.3e} hor={v['horizon_files']} deckhor={v.get('deck_horizon_block')}")
    for k, v in C.items():
        print(f"{k:7s} tc={v['t_cross']} claimed={v['claimed']} t_end={v['t_end']} exc={v['t_first_excision']}"
              f" coll={v.get('coll_0_100')} E={v.get('energy')} hor={v['horizon_files']}")
        for lab, w in v.get("count_windows", {}).items():
            print(f"    {lab}: ratio {w['ratio']:.5f} z {w['z']:+.2f}; with rejected {w['ratio_with_rejected']:.5f}"
                  f" z {w['z_with_rejected']:+.2f}; n_trunc {w['n_trunc']:.0f} max_P {w['max_P']:.3f}")
    print("M4 mean", res["M4_mean"], "seed pair diff", res["seed_pair_diff"],
          "mesh shift", res["mesh_shift_unstable"], "gauge shift", res["gauge_shift_unstable"],
          "stable gauge blockdiff", res["gauge_leg_stable_maxabs_blockdiff"])
    for k, v in res["deck_diffs"].items():
        print(k, v)
    print("sha all ok", res["sha_all_ok"], [s for s in SHA_CHECKED if s[1] != "ok"])


if __name__ == "__main__":
    main()
