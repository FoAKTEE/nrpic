"""V5b: T9 end state, KS of each mass class against Maxwell-Juttner at (i) theta from the initial
energy, (ii) theta from the final energy, (iii) the class's own theta (JOURNAL entry 15)."""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import lib  # noqa: E402
from v2_box import theta_from_w  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
RUN = "C-20261115-170814-8a54b43"


def ks(um, th):
    smp = lib.MJSampler(th)
    return float(stats.kstest(um, lambda x: np.interp(x, smp.u, smp.cdf)).pvalue)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or lib.run_dir(SCR + "/tmp/verify_g1/v5b")
    os.makedirs(out, exist_ok=True)
    res = {}
    for d in sorted(glob.glob(f"{SCR}/{RUN}/T9_s*")):
        ss = sorted(glob.glob(d + "/box.part.*.bin"))
        s0, s1 = lib.read_snap(ss[0]), lib.read_snap(ss[-1])
        W0 = np.sqrt(1 + np.einsum("ij,ij->i", s0["u"], s0["u"]))
        W1 = np.sqrt(1 + np.einsum("ij,ij->i", s1["u"], s1["u"]))
        th_i = theta_from_w(math.fsum(s0["m"]*W0)/math.fsum(s0["m"]))
        th_f = theta_from_w(math.fsum(s1["m"]*W1)/math.fsum(s1["m"]))
        mmin = s1["m"].min()
        row = dict(theta_initial_energy=th_i, theta_final_energy=th_f)
        for lab, msk in [("light", s1["m"] < 1.5*mmin), ("heavy", s1["m"] >= 1.5*mmin)]:
            um = np.sqrt(np.einsum("ij,ij->i", s1["u"][msk], s1["u"][msk]))
            th_own = theta_from_w(W1[msk].mean())
            se = W1[msk].std(ddof=1)/np.sqrt(msk.sum())/lib.c_v(th_own)
            row[lab] = dict(theta_own=th_own, z_vs_final=(th_own - th_f)/se, KS_initial=ks(um, th_i),
                            KS_final=ks(um, th_f), KS_own=ks(um, th_own))
        res[os.path.basename(d)] = row
        print(os.path.basename(d), json.dumps(row, default=float))
    lib.save_json(os.path.join(out, "v5_t9ks.json"), res)
    from nrpic import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.17, top=0.9, wspace=0.3)
    names = list(res)
    x = np.arange(len(names))
    for j, (k, mk, col) in enumerate([("KS_initial", "o", P["red"]), ("KS_final", "s", P["blue"]), ("KS_own", "^", P["green"])]):
        for c, off in [("light", -0.12), ("heavy", 0.12)]:
            ax[0].semilogy(x + off, [res[n][c][k] for n in names], mk, color=col, ms=4, mfc=col if c == "light" else "none",
                           label=f"{k} ({c})")
    ax[0].axhline(1e-3, **figstyle.GUIDE)
    ax[0].set_xticks(x)
    ax[0].set_xticklabels([n.replace("T9_", "") for n in names], fontsize=7)
    ax[0].set_ylabel("KS p")
    ax[0].legend(fontsize=5, ncol=2)
    for c, col in [("light", P["blue"]), ("heavy", P["red"])]:
        ax[1].plot(x, [res[n][c]["z_vs_final"] for n in names], "o", color=col, label=c)
    ax[1].axhspan(-4, 4, color="grey", alpha=0.15)
    ax[1].set_xticks(x)
    ax[1].set_xticklabels([n.replace("T9_", "") for n in names], fontsize=7)
    ax[1].set_ylabel(r"z of $\theta_{class}$ vs $\theta$(final energy)")
    ax[1].legend(fontsize=6)
    fig.savefig(os.path.join(out, "v5_t9ks.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
