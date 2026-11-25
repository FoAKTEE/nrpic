"""Figure: how the even (second-order) part of the constraints scales with the noise amplitude.

Reads (each checked against its run's sha256sums.txt):
- judge_g2.json of E-20261123-024359-5dc3213: the factor e(1)/e(1/2) of the even parts of the
  Hamiltonian and momentum constraints with the noise level fixed in advance removed, and which
  record times the fixed rule judges (e(1/2) > 3 f);
- judge_q.json of E-20261125-033450-4c4a31c: the same for the pair s = 1/2 and 1/4;
- floor3.json of E-20261125-023427-6fb6400 (the fresh verifier): the factor with the noise level
  taken from three amplitudes, and its own judged set.
Writes OUT/fig_g2_halving.{pdf,png,json}.

    fig_g2_halving.py OUT
"""
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/E-stoch-inf/"
JUDGE = S + "E-20261123-024359-5dc3213"
JQ = S + "E-20261125-033450-4c4a31c"
FL3 = S + "E-20261125-023427-6fb6400"
USR = (2.5234, 6.5503)   # eps2 = 3 crossed upward and downward (ledger, lattice background)


def sha_ok(run_dir, rel):
    want = None
    for ln in open(os.path.join(run_dir, "sha256sums.txt")):
        h, f = ln.split(None, 1)
        if f.strip().lstrip("*").lstrip("./") == rel:
            want = h
    got = hashlib.sha256(open(os.path.join(run_dir, rel), "rb").read()).hexdigest()
    if want != got:
        sys.exit(f"checksum of {run_dir}/{rel} does not match its sha256sums.txt")


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for d, f in ((JUDGE, "judge_g2.json"), (JQ, "judge_q.json"), (FL3, "floor3.json")):
        sha_ok(d, f)
    J = json.load(open(os.path.join(JUDGE, "judge_g2.json")))["UA4a_b"]
    Q = json.load(open(os.path.join(JQ, "judge_q.json")))
    F = json.load(open(os.path.join(FL3, "floor3.json")))
    cN = np.array(J["cN"])
    cNq = np.array(Q["cN"])
    rows = F["rows"]
    cNf = np.array([r["cN"] for r in rows])
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = fs.SERIES
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH, 4.6), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.98, bottom=0.1, hspace=0.08)
    summary = {}
    for k, lab in enumerate(("H", "M")):
        x = ax[k]
        x.axvspan(*USR, color=fs.PAL["yellow"], alpha=0.15, lw=0)
        x.axhspan(3.95, 4.05, color="0.88", lw=0)
        x.axhline(4.0, color="0.6", lw=0.8)
        c, s = np.array(J[lab]["corr"]), np.array(J[lab]["sel_a"])
        x.plot(cN[s], c[s], "s", mfc="none", ms=5, mew=1.1, color=cols[1],
               label=r"$\lambda=1$ over $\frac{1}{2}$, level fixed in advance")
        cq, sq = np.array(Q["UA4a_quarter"][lab]["corr"]), np.array(Q["UA4a_quarter"][lab]["sel_a"])
        x.plot(cNq[sq], cq[sq], "o", ms=3.5, color=cols[0],
               label=r"$\lambda=\frac{1}{2}$ over $\frac{1}{4}$, level fixed in advance")
        r3 = np.array([r[lab]["ratio_sigma_1h"] for r in rows])
        j3 = np.array([r[lab]["judged_sigma_1h"] for r in rows])
        x.plot(cNf[j3], r3[j3], "x", ms=5, mew=1.1, color="k",
               label=r"$\lambda=1$ over $\frac{1}{2}$, level from three amplitudes")
        x.set_ylim(3.85, 4.17)
        x.set_ylabel("factor of the even part")
        x.text(0.03, 0.94, ("(a) Hamiltonian constraint" if lab == "H" else "(b) momentum constraint"),
               transform=x.transAxes, va="top")
        summary[lab] = dict(fixed_1h_min=float(c[s].min()), fixed_1h_max=float(c[s].max()),
                            fixed_1h_n=int(s.sum()),
                            fixed_hq_n=int(sq.sum()),
                            three_amp_maxdev=float(np.abs(r3[j3] - 4.0).max()), three_amp_n=int(j3.sum()))
    ax[1].set_xlabel(r"$N - N_*$")
    ax[1].legend(loc="lower left", fontsize=6, frameon=False)
    ax[1].set_xlim(-0.3, 10.3)
    fs.save(fig, os.path.join(out, "fig_g2_halving"))
    json.dump(summary, open(os.path.join(out, "fig_g2_halving.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
