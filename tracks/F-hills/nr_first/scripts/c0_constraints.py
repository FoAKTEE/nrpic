#!/usr/bin/env python3
"""E2 of nr_first/JOURNAL.md (run C0): Hamiltonian residual of the q = 4 three-black-hole
data at t = 0 against resolution.

For every case directory of a c0_t0.sh run (approx_L9..11, none_L9..11, plain_L10) reads the
full dumps bin/hills.con.00000.bin, bin/hills.adm_psi4.00000.bin and the history, and forms
  code    the history norm <H^2>^(1/2) = (sum H^2 sqrt(gamma) dV / sum sqrt(gamma) dV)^(1/2)
          over the cells with psi^4 <= 16 (core's definition, tracks/core/analysis/mp/
          triple_static.py; sqrt(gamma) = psi^6), recomputed from the dump and checked
          against the history file
  closed  the same norm of the closed-form residual of the same data on the same cells
          (core's mp_common.closed_forms with python/nrpic/bowen_york.py: H = -8 psi^-5 lap u
          - psi^-12 Abar^2, lap u in closed form)
  diff    the norm of code - closed (truncation error)
in all cells and by region (within 1 M of a member, within 4 M of the heavy hole, rest).
Writes <out>/c0_constraints.json and fig_c0_constraints.{png,pdf}.
Usage: c0_constraints.py <c0 run directory> [outdir]   (outdir default: the run directory)
"""
import json
import os
import sys

import numpy as np

WT = "/data/haiyangw/nrpic/wt/F-hills"
sys.path.insert(0, os.path.join(WT, "tracks/core/analysis/mp"))
import mp_common as mc  # noqa: E402  (core's readers and closed forms, read only)
from nrpic import figstyle as fs  # noqa: E402

CASES = [("none", 9), ("none", 10), ("none", 11), ("approx", 9), ("approx", 10),
         ("approx", 11), ("plain", 10)]
LABEL = {"none": "no correction", "approx": "closed form, background factor",
         "plain": "closed form, plain sum"}
COLOR = {"none": fs.PAL["blue"], "approx": fs.PAL["red"], "plain": fs.PAL["yellow"]}


def analyse(d):
    _, par, x, y, z, dx, con = mc.read_bin(os.path.join(d, "bin", "hills.con.00000.bin"))
    _, _, _, _, _, _, adm = mc.read_bin(os.path.join(d, "bin", "hills.adm_psi4.00000.bin"))
    hst = mc.read_hst(os.path.join(d, "hills.z4c.user.hst"))
    pts = np.stack([x, y, z], axis=-1)
    puncs = mc.punctures(par, d)
    _, _, han = mc.closed_forms(pts, puncs)
    psi4 = adm["adm_psi4"]
    dv = dx ** 3 * psi4 ** 1.5
    sel = psi4 <= 16.0
    vol = float(np.sum(dv[sel]))
    pos = [p["pos"] for p in puncs]
    heavy = int(np.argmax([p["m"] for p in puncs]))
    rm = np.min([np.linalg.norm(pts - pos[k], axis=1) for k in range(len(pos)) if k != heavy],
                axis=0)
    rh = np.linalg.norm(pts - pos[heavy], axis=1)
    regions = {"all": sel, "members (r < 1 M)": sel & (rm < 1.0),
               "heavy (r < 4 M)": sel & (rh < 4.0), "rest": sel & (rm >= 1.0) & (rh >= 4.0)}

    def norm(a, s):
        return float(np.sqrt(np.sum(a[s] ** 2 * dv[s]) / vol))

    H = con["con_H"]
    out = {"blocks": int(len(x) // 4096), "h_min": float(dx.min()),
           "lam": [float(p.get("lam", 1.0)) for p in puncs],
           "volume": vol, "hst_volume": float(hst["Volume"][0]),
           "hst_H": float(np.sqrt(hst["H-norm2"][0] / hst["Volume"][0])),
           "hst_M": float(np.sqrt(hst["M-norm2"][0] / hst["Volume"][0]))}
    for name, s in regions.items():
        out[name] = {"code": norm(H, s), "closed": norm(han, s), "diff": norm(H - han, s)}
    # profile along x through member 0 (cells nearest z = 0 and y = y0)
    y0 = pos[0][1]
    line = (z > 0) & (z <= dx) & (np.abs(y - y0) <= 0.5 * dx) & (np.abs(x - pos[0][0]) < 8)
    o = np.argsort(x[line])
    prof = {"x": x[line][o] - pos[0][0], "H": H[line][o], "Hc": han[line][o]}
    return out, prof


def main():
    run = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else run
    res, prof = {}, {}
    for kind, nl in CASES:
        name = f"{kind}_L{nl}"
        d = os.path.join(run, name)
        if not os.path.exists(os.path.join(d, "bin", "hills.con.00000.bin")):
            print("missing", name)
            continue
        res[name], prof[name] = analyse(d)
        e = res[name]
        print(f"{name:10s} blocks {e['blocks']:5d} h_min {e['h_min']:.5f} history H {e['hst_H']:.3e}"
              f" (volume {e['hst_volume']:.4e}, cells {e['volume']:.4e})", flush=True)
        for reg in ("all", "members (r < 1 M)", "heavy (r < 4 M)", "rest"):
            r = e[reg]
            print(f"     {reg:18s} code {r['code']:.3e}  closed {r['closed']:.3e}  diff {r['diff']:.3e}")
    # convergence orders of the difference between successive resolutions
    for kind in ("none", "approx"):
        ds = [res.get(f"{kind}_L{nl}", {}).get("all", {}).get("diff") for nl in (9, 10, 11)]
        if all(v is not None for v in ds):
            res[f"order_{kind}"] = [float(np.log2(ds[0] / ds[1])), float(np.log2(ds[1] / ds[2]))]
            print(kind, "order of the truncation error:", res[f"order_{kind}"])
    json.dump(res, open(os.path.join(out, "c0_constraints.json"), "w"), indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    for kind in ("none", "approx", "plain"):
        nls = [nl for k, nl in CASES if k == kind and f"{kind}_L{nl}" in res]
        if not nls:
            continue
        h = [res[f"{kind}_L{nl}"]["h_min"] / 0.125 for nl in nls]       # cells in units of m
        code = [res[f"{kind}_L{nl}"]["all"]["code"] for nl in nls]
        clo = [res[f"{kind}_L{nl}"]["all"]["closed"] for nl in nls]
        dif = [res[f"{kind}_L{nl}"]["all"]["diff"] for nl in nls]
        ax[0].loglog(h, code, "o-", color=COLOR[kind], label=LABEL[kind] + ": code")
        ax[0].loglog(h, clo, "s--", color=COLOR[kind], mfc="none", lw=1.0, label="closed form")
        ax[0].loglog(h, dif, "^:", color=COLOR[kind], lw=1.0, label="code - closed form")
    hh = np.array([1 / 4, 1 / 16])
    if "approx_L10" in res:
        ref = res["approx_L10"]["all"]["diff"]
        ax[0].loglog(hh, ref * (hh / 0.125) ** 4, **fs.THIN, ls="-.")
        ax[0].text(0.07, ref * 0.5 ** 4 * 0.6, r"$\propto h^4$", fontsize=8)
    ax[0].set_xlabel(r"finest cell $h/m$ at the members")
    ax[0].set_ylabel(r"$\langle H^2\rangle^{1/2}$ at $t=0$")
    ax[0].legend(frameon=False, fontsize=6, loc="lower right", ncol=1)
    ax[0].invert_xaxis()
    for name, ls in (("none_L11", "-"), ("approx_L11", "-"), ("approx_L9", ":")):
        if name not in prof:
            continue
        p = prof[name]
        kind = name.split("_")[0]
        ax[1].semilogy(p["x"], np.abs(p["H"]), ls=ls, color=COLOR[kind],
                       label=f"{LABEL[kind]}, h = m/{0.125 / res[name]['h_min']:.0f}")
        ax[1].semilogy(p["x"], np.abs(p["Hc"]), color="k", lw=0.7, ls="--")
    ax[1].set_xlim(-2, 2)
    ax[1].set_ylim(1e-8, 1e3)
    ax[1].set_xlabel(r"$x - x_{m_1}$ through member $m_1$ $[M]$")
    ax[1].set_ylabel(r"$|H|$ at $t=0$ (dashed: closed form)")
    ax[1].legend(frameon=False, fontsize=6, loc="upper right")
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(out, "fig_c0_constraints")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
