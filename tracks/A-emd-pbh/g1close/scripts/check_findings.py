"""Check findings 1-5 of the G1 verifier (stage/G1/VERIFIER.md) and section 4 item 2 at their sources.

Reads only registered run outputs under /data/haiyangw/nrpic/scratch/A-emd-pbh/<run id>/,
each file checked against the run's sha256sums.txt where the run wrote one:

  (a) scope_numbers.json (A-20261115-130252-7877b7a): median of the read-off/top-hat ratio over
      mu <= 0.15 and over all six read-offs;
  (b) the shells table of data set 2t (A-emd-pbh-20261115-130609-947c898): time since the bang
      of every shell on the initial slice, t = 2 R^(3/2) int_0^1 s^2 ds / sqrt(2m + 2 E R s^2)
      (the integral of dR/v from R = 0, valid for every sign of E while the shell expands);
  (c) units of the scouting data: nominal mass M_0 = H^2 R_b^3 / 2 against the total
      Misner-Sharp mass M; the exact events (A-emd-pbh-20261115-153719-91b03d1) in units of M;
  (d) the wave-2 state of the criteria checks (A-emd-pbh-20261115-161813-6c820fb for T1, T3-T5,
      -163358-9b2d048 for T2 after its fix), against the wave-1 state (-130256-a7374a4);
  (f) the 14 Newtonian scan points (A-emd-pbh-20261115-164420-4528861): which lie in the band
      +2.2e-4 .. +6.3e-4 of the relative first-collapse time that stage/G1/STATUS.md T3 states.

Writes findings.json and fig_g1close_findings.{pdf,png} into $NRPIC_RUN_DIR (or --out DIR).
Style: python/nrpic/figstyle.py.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

SCRATCH = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
RUN = {
    "scope": "A-20261115-130252-7877b7a",
    "dataset2t": "A-emd-pbh-20261115-130609-947c898",
    "ball_exact": "A-emd-pbh-20261115-153719-91b03d1",
    "crit_w1": "A-emd-pbh-20261115-130256-a7374a4",
    "crit_full": "A-emd-pbh-20261115-161813-6c820fb",
    "crit_t2": "A-emd-pbh-20261115-163358-9b2d048",
    "newton": "A-emd-pbh-20261115-164420-4528861",
}
STEM2T = "expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75_w0p1875"
INPUTS = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_file(key, rel):
    rdir = os.path.join(SCRATCH, RUN[key])
    path = os.path.join(rdir, rel)
    sums = os.path.join(rdir, "sha256sums.txt")
    digest = sha256(path)
    if os.path.isfile(sums):
        table = {}
        for line in open(sums):
            p = line.split(None, 1)
            if len(p) == 2:
                table[p[1].strip()] = p[0]
        if table.get(rel) != digest:
            raise SystemExit(f"sha256 of {path} differs from its run's sha256sums.txt")
        state = "sha256 ok"
    else:
        state = "no sha256sums.txt"
    INPUTS.append(dict(run=RUN[key], file=rel, sha256=digest, check=state))
    return path


def age_on_slice(R, m, E, n=64):
    """Time since the bang of a shell of areal radius R, mass m, energy E, while it expands."""
    s, w = np.polynomial.legendre.leggauss(n)
    s, w = 0.5 * (s + 1.0), 0.5 * w
    return 2.0 * R ** 1.5 * np.sum(w * s ** 2 / np.sqrt(2.0 * m + 2.0 * E * R * s ** 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    out = ap.parse_args().out
    if not out:
        raise SystemExit("give --out DIR or run under nrpic-run")
    os.makedirs(out, exist_ok=True)
    res = {}

    # (a) median of the read-off / top-hat ratio
    S = json.load(open(run_file("scope", "scope/scope_numbers.json")))["T2"]
    mu = np.array(S["mu"])
    rat = np.array(S["ratio_read_to_tc_rm"])
    sel = mu <= 0.15
    res["a"] = dict(mu=mu.tolist(), ratio=rat.tolist(),
                    range_mu_le_0p15=[float(rat[sel].min()), float(rat[sel].max())],
                    median_mu_le_0p15=float(np.median(rat[sel])),
                    median_all_six=float(np.median(rat)),
                    median_ratio_key=S["median_ratio"])
    res["a"]["key_is_all_six"] = bool(abs(res["a"]["median_all_six"] - S["median_ratio"]) < 1e-12)

    # (b) bang times of data set 2t
    D = json.load(open(run_file("dataset2t", f"{STEM2T}.json")))["model"]
    sh = np.loadtxt(run_file("dataset2t", f"{STEM2T}_shells.txt"))
    Ri, m, E = sh[:, 0], sh[:, 2], sh[:, 3]
    age = np.array([age_on_slice(r, mm, e) for r, mm, e in zip(Ri, m, E)])
    t_i = D["t_i"]
    inner = Ri < 6.5
    taper = ~inner
    res["b"] = dict(t_i=t_i, n_shells=int(len(Ri)), n_inner=int(inner.sum()), n_taper=int(taper.sum()),
                    max_abs_dev_inner=float(np.max(np.abs(age[inner] - t_i))),
                    taper_age_min=float(age[taper].min()), taper_age_max=float(age[taper].max()),
                    taper_R_i=[float(Ri[taper].min()), float(Ri[taper].max())],
                    taper_max_abs_E=float(np.max(np.abs(E[taper]))),
                    first_R_i_dev_gt_1em6=float(Ri[np.argmax(np.abs(age - t_i) > 1e-6)]))

    # (c) units
    B = json.load(open(run_file("ball_exact", "exact.json")))
    M0 = 0.5 * D["H"] ** 2 * D["Rb"] ** 3
    M = D["M_misner_sharp"]
    res["c"] = dict(M0=M0, M=M, M_over_M0=M / M0,
                    in_units_of_M=dict(tau_ta=B["core"]["tau_ta"] / (M / M0),
                                       tau_AH=B["first_trapped"]["tau"] / (M / M0),
                                       m_AH_first=B["first_trapped"]["m"] / (M / M0),
                                       m_AH_crunch=B["m_ah"]["m"][-1] / (M / M0),
                                       R_b=D["Rb"] / (M / M0), t_i=t_i / (M / M0)))

    # (d) criteria state, wave 2
    full = json.load(open(run_file("crit_full", "results.json")))["checks"]
    t2 = json.load(open(run_file("crit_t2", "results.json")))["checks"]
    state = [c for c in full if not c["id"].startswith("T2")] + t2
    checks = [c for c in state if c["passed"] is not None]
    diags = [c["id"] for c in state if c["passed"] is None]
    w1 = json.load(open(run_file("crit_w1", "results.json")))["checks"]
    res["d"] = dict(wave1=dict(n_checks=len(w1), failing=[c["id"] for c in w1 if not c["passed"]]),
                    n_checks=len(checks), n_pass=int(sum(bool(c["passed"]) for c in checks)),
                    failing=[c["id"] for c in checks if not c["passed"]], diagnostics=diags,
                    full_run=dict(n_checks=len([c for c in full if c["passed"] is not None]),
                                  failing=[c["id"] for c in full if c["passed"] is False]))

    # (f) the Newtonian scan points
    N = json.load(open(run_file("newton", "newton_results.json")))["scan"]
    lo, hi = 2.15e-4, 6.35e-4   # the printed band 2.2e-4 .. 6.3e-4 at its printed precision
    pts = []
    for s in N:
        r = s["t1_vertex_rel"]
        pts.append(dict(name=s["name"], nx=s["nx"], n=s["n"], deltaL=s["deltaL"], e=round(s["e"], 3),
                        p=round(s["p"], 3), rotate=s["rotate"], t1_rel=r, in_band=bool(lo <= r <= hi)))
    res["f"] = dict(n_points=len(pts), n_in_band=sum(p["in_band"] for p in pts),
                    outside=[(p["name"], p["t1_rel"]) for p in pts if not p["in_band"]], points=pts)
    res["inputs"] = INPUTS

    with open(os.path.join(out, "findings.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ------------------------------------------------------------------ figure
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.97, wspace=0.27, hspace=0.32)
    a = ax[0, 0]
    a.plot(mu[sel], rat[sel], "o", color=fs.PAL["red"], label=r"read-off, $\mu\leq0.15$")
    a.plot(mu[~sel], rat[~sel], "o", mfc="none", color=fs.PAL["red"], label=r"read-off, $\mu=0.3$")
    a.axhline(res["a"]["median_mu_le_0p15"], color=fs.PAL["blue"], lw=1.0, label=r"median, $\mu\leq0.15$")
    a.axhline(res["a"]["median_all_six"], **dict(fs.GUIDE, lw=1.0), label="median, all six")
    a.set_xscale("log")
    a.set_xlabel(r"$\mu$")
    a.set_ylabel("read-off / top-hat collapse time")
    a.legend(ncol=1, fontsize=8, loc="upper left")
    a = ax[0, 1]
    a.plot(Ri, age, color=fs.PAL["red"], label="age of the shell on the initial slice")
    a.axhline(t_i, **dict(fs.GUIDE, lw=1.0), label=r"$t_i$ of the envelope")
    a.axvspan(6.5, Ri.max(), color="0.5", alpha=0.15, lw=0)
    a.text(6.6, 13.2, "surface\ntaper", fontsize=8)
    a.set_xlabel(r"$R_i/M_0$")
    a.set_ylabel(r"time since the bang $/M_0$")
    a.legend(fontsize=8, loc="upper left")
    a = ax[1, 0]
    x = np.arange(len(pts))
    col = [fs.PAL["red"] if p["in_band"] else fs.PAL["yellow"] for p in pts]
    a.axhspan(lo, hi, color=fs.PAL["blue"], alpha=0.2, lw=0)
    a.scatter(x, [p["t1_rel"] for p in pts], c=col, s=22, zorder=3)
    a.axhline(0, color="0.5", lw=0.8)
    a.set_xticks(x)
    a.set_xticklabels([p["name"] for p in pts], rotation=70, fontsize=7)
    a.minorticks_off()
    a.set_ylabel(r"relative error of $t_1$")
    a.text(0.02, 0.92, "band of the STATUS sentence (blue)", transform=a.transAxes, fontsize=8)
    a = ax[1, 1]
    labels = ["wave 1", "wave 2\nfull run", "wave 2\nstate"]
    w = res["d"]["wave1"]
    npass = [w["n_checks"] - len(w["failing"]),
             res["d"]["full_run"]["n_checks"] - len(res["d"]["full_run"]["failing"]), res["d"]["n_pass"]]
    nfail = [len(w["failing"]), len(res["d"]["full_run"]["failing"]), len(res["d"]["failing"])]
    a.bar(range(3), npass, color=fs.PAL["blue"], label="pass")
    a.bar(range(3), nfail, bottom=npass, color=fs.PAL["red"], label="fail")
    a.set_xticks(range(3))
    a.set_xticklabels(labels, fontsize=8)
    a.minorticks_off()
    a.set_ylabel("checks against the papers")
    a.set_ylim(0, 1.25 * max(np.add(npass, nfail)))
    a.legend(ncol=2, loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(out, "fig_g1close_findings"))
    print(json.dumps({k: v for k, v in res.items() if k in "abcd"}, indent=1))
    print("f:", res["f"]["n_in_band"], "of", res["f"]["n_points"], "in band; outside", res["f"]["outside"])


if __name__ == "__main__":
    main()
