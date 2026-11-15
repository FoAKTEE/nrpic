#!/usr/bin/env python3
"""K = 1/(rho_0c H_c) of the track definition (stage/G0/REPORT.md decision 2,
collide/SPEC.md section 1) for the 13 models of run C-20261115-170742-84990ed.

H_c = (v1^2/(4 pi rho_0c))^1/2 with v1^2 = (p + 2 p_T)/(3 rho_0), so for isotropic models
K = (4 pi/p_c)^1/2 in units M_ADM = 1; rho_0c = n_c (rest-mass density) and p_c, pT_c from
each model's JSON. sigma~ = K/Kn_c. Output: $NRPIC_RUN_DIR/rv_kn.json, rv_kn.{png,pdf}.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rvlib as rv  # noqa: E402

R_MOD = os.path.join(rv.SCR, "C-20261115-170742-84990ed")


def main():
    out = rv.outdir()
    res = {}
    for p in sorted(os.listdir(R_MOD)):
        if not (p.endswith("_s1.json") and "_stratified_N100000" in p):
            continue
        js = json.load(open(os.path.join(R_MOD, p)))
        n, pc, pt = js["n_c"], js["p_c"], js["pT_c"]
        v1sq = (pc + 2 * pt) / (3 * n)
        H = math.sqrt(v1sq / (4 * math.pi * n))
        K = 1.0 / (n * H)
        res[js["tag"]] = dict(Z0=js["Zc_infinity"], rho0c=n, p_c=pc, v1=math.sqrt(v1sq), H_c=H,
                              K=K, sigma_at_Kn10=K / 10, sigma_at_Kn1=K, role=js.get("role"))
        print(js["tag"], f"Z0 {js['Zc_infinity']:.5f} H_c {H:.4f} K {K:.2f}")
    json.dump(res, open(os.path.join(out, "rv_kn.json"), "w"), indent=1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(rv.WT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 3.0))
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.16, top=0.95)
    for fam, col, lab in (("king", fs.PAL["blue"], "King b = 1"), ("tmb01", fs.PAL["red"], "F21 b = 0.1")):
        pts = sorted((v["Z0"], v["K"]) for k, v in res.items() if k.startswith(fam))
        ax.plot([a for a, _ in pts], [b for _, b in pts], "o-", color=col, ms=4, label=lab)
    ax.set_xlabel(r"$Z(0)$")
    ax.set_ylabel(r"$K = 1/(\rho_{0c} H_c)$, $\tilde\sigma = K/\mathrm{Kn}_c$")
    ax.legend(fontsize=8, frameon=False)
    fs.save(fig, os.path.join(out, "rv_kn"))


if __name__ == "__main__":
    main()
