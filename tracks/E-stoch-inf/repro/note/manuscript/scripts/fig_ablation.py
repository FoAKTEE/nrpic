"""Fig. 9 of arXiv:2512.14649 (P1:777-790, fig:ablationback): relative difference of the R^NR power
spectrum at N_f between backreaction levels 2 and 0, and 1 and 0, both scenarios, 256^3, same seed.

Level 0, 1, 2 with the mode equation of the noise on the mesh (repro/ablation; decision 0031 item 1):
AL0S, AL1S, AL2S (SR), AL0U, AL1U, AL2U (USR). Per injected shell with more than 10 modes:
r = sum_shell |c_L|^2 / sum_shell |c_L0m|^2 - 1 from the npz files of dumppass.py (last dump).
Beside it (right panel): the released level 0 on shells (P256v6, U256ap) against level 0 on the mesh
(control P-A3 (ii)), and the level-1 runs of repro/scope (RL1, UL1, release) against the released
level 0 (scope P4). Per mode (when the npz holds c_NR): rms and max over modes of |c_L - c_L0m|/|c_L0m|.
Records: <|H|/[H]> of each level-2 run over its level-0-mesh twin (P-A3 (iii)).

Usage: fig_ablation.py --out OUT --npz LABEL=DIR ... (DIR holds d<NNNNN>.npz of that label)
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figlib as fl  # noqa: E402
import runs as rr  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle as fs  # noqa: E402

MINCOUNT = 10


def last(d):
    return np.load(sorted(glob.glob(os.path.join(d, "d*.npz")))[-1])


def compare(za, zb):
    """Shell ratio za/zb - 1 (shells with > 10 modes) and per-mode relative differences."""
    assert abs(float(za["time"]) - float(zb["time"])) < 1e-9, (float(za["time"]), float(zb["time"]))
    cnt = za["inj_count"]
    sel = cnt > MINCOUNT
    r = (za["inj_pnr"] / zb["inj_pnr"] - 1.0)[sel]
    n2 = za["inj_n2"][sel]
    out = dict(n2=n2.tolist(), r=r.tolist(), rms=float(np.sqrt(np.mean(r * r))),
               max=float(np.max(np.abs(r))), frac_pos=float(np.mean(r > 0)),
               rms_n_le_32=float(np.sqrt(np.mean(r[n2 <= 1024] ** 2))),
               max_n_ge_56=float(np.max(np.abs(r[n2 >= 56 * 56]))) if np.any(n2 >= 3136) else None,
               max_n_le_16=float(np.max(np.abs(r[n2 <= 256]))),
               max_n_le_32=float(np.max(np.abs(r[n2 <= 1024]))),
               time=float(za["time"]), N=float(za["efolds_chi"]))
    # one sign over most shells with |r| > 1e-4
    big = np.abs(r) > 1e-4
    out["frac_pos_big"] = float(np.mean(r[big] > 0)) if big.any() else None
    out["n_big"] = int(big.sum())
    # rise towards the cut: median |r| in the top decile of shells over the bottom half
    q = np.argsort(n2)
    top = np.abs(r[q[int(0.9 * q.size):]])
    bot = np.abs(r[q[:q.size // 2]])
    out["top_over_bottom_median"] = float(np.median(top) / np.median(bot))
    if "inj_c_nr" in za.files and "inj_c_nr" in zb.files:
        ca, cb = za["inj_c_nr"], zb["inj_c_nr"]
        rel = np.abs(ca - cb) / np.abs(cb)
        out["mode_rel_rms"] = float(np.sqrt(np.mean(rel ** 2)))
        out["mode_rel_max"] = float(rel.max())
    return out


def record_ratio(la, lb):
    a = fl.read_con_joined(rr.con_paths(la))
    b = fl.read_con_joined(rr.con_paths(lb))
    ca, cb = a[:, 1].astype(int), b[:, 1].astype(int)
    common, ia, ib = np.intersect1d(ca, cb, return_indices=True)
    rh = a[ia, 3] / b[ib, 3]
    rm = a[ia, 6] / b[ib, 6]
    return dict(n_cycles=int(common.size), last_cycle_a=int(ca.max()), last_cycle_b=int(cb.max()),
                H_ratio_min=float(rh.min()), H_ratio_max=float(rh.max()),
                M_ratio_min=float(rm.min()), M_ratio_max=float(rm.max()),
                within_factor2=bool(np.all((rh > 0.5) & (rh < 2.0))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--npz", action="append", required=True)
    ap.add_argument("--name", default="fig9_ablation")
    ap.add_argument("--title", default="")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    D = dict(item.split("=") for item in args.npz)
    Z = {lab: last(d) for lab, d in D.items()}
    res = {}
    pairs = [("r20_sr", "AL2S", "AL0S"), ("r10_sr", "AL1S", "AL0S"),
             ("r20_usr", "AL2U", "AL0U"), ("r10_usr", "AL1U", "AL0U"),
             ("shells_vs_mesh_sr", "P256v6", "AL0S"), ("shells_vs_mesh_usr", "U256ap", "AL0U"),
             ("rl1_vs_released_sr", "RL1", "P256v6"), ("ul1_vs_released_usr", "UL1", "U256ap")]
    for key, a, b in pairs:
        if a in Z and b in Z:
            res[key] = compare(Z[a], Z[b])
        else:
            res[key] = "pending: " + ", ".join(x for x in (a, b) if x not in Z)
    for key, a, b in [("rec_l2_l0m_sr", "AL2S", "AL0S"), ("rec_l2_l0m_usr", "AL2U", "AL0U"),
                      ("rec_l1_l0m_sr", "AL1S", "AL0S"), ("rec_l1_l0m_usr", "AL1U", "AL0U")]:
        try:
            res[key] = record_ratio(a, b)
        except (OSError, ValueError) as e:
            res[key] = f"unavailable: {e}"
    # t = 0 controls (P-A3 (i)) come from bitcheck.py
    fs.use_style()
    controls = any(isinstance(res[k], dict) for k in
                   ("shells_vs_mesh_sr", "shells_vs_mesh_usr", "rl1_vs_released_sr",
                    "ul1_vs_released_usr"))
    if controls:
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.6), sharey=True)
        fig.subplots_adjust(left=0.09, right=0.99, bottom=0.14, top=0.9, wspace=0.0)
    else:  # no control in the inputs (e.g. the t = 7.5 comparison): one panel only
        fig, a0 = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH + 1.6, 3.6))
        fig.subplots_adjust(left=0.16, right=0.97, bottom=0.14, top=0.86)
        ax = [a0]
    style = {"r20_sr": (fs.PAL["red"], "level 2 - 0, quadratic"),
             "r20_usr": (fs.PAL["orange"], "level 2 - 0, inflection"),
             "r10_sr": (fs.PAL["blue"], "level 1 - 0, quadratic"),
             "r10_usr": (fs.PAL["green"], "level 1 - 0, inflection")}
    for key, (c, lab) in style.items():
        if isinstance(res[key], dict):
            case = "sr" if key.endswith("sr") else "usr"
            k = fl.k_p1(np.sqrt(np.array(res[key]["n2"], float)), case)
            ax[0].loglog(k, np.abs(res[key]["r"]), color=c, lw=0.6, label=lab)
        elif isinstance(res[key], str) and "AL2S" in res[key]:  # only the cut SR level-2 run waits
            ax[0].plot([], [], color=c, lw=0.6, label=lab + " (pending)")
    ax[0].set_title("Levels 1 and 2 against level 0, noise on the mesh", fontsize=9)
    ax[0].set_ylabel("relative difference of the power")
    style2 = {"shells_vs_mesh_sr": (fs.PAL["red"], "level 0, shells against mesh, quad."),
              "shells_vs_mesh_usr": (fs.PAL["orange"], "level 0, shells against mesh, infl."),
              "rl1_vs_released_sr": (fs.PAL["blue"], "level 1 against 0 on shells, quad."),
              "ul1_vs_released_usr": (fs.PAL["green"], "level 1 against 0 on shells, infl.")}
    for key, (c, lab) in style2.items():
        if controls and isinstance(res[key], dict):
            case = "sr" if key.endswith("sr") else "usr"
            k = fl.k_p1(np.sqrt(np.array(res[key]["n2"], float)), case)
            ax[1].loglog(k, np.abs(res[key]["r"]), color=c, lw=0.6, label=lab)
    if controls:
        ax[1].set_title("Controls: noise on shells", fontsize=9)
    for a in ax:
        a.set_xlabel(r"comoving wave number $k$ [$M_{\rm Pl}=100$]")
        a.legend(loc="lower right", fontsize=6.5)
        a.set_ylim(1e-12, 1e-1)
    if args.title:
        fig.suptitle(args.title, fontsize=9)
    fs.save(fig, os.path.join(args.out, args.name))
    plt.close(fig)
    with open(os.path.join(args.out, args.name + ".json"), "w") as fp:
        json.dump({k: ({kk: vv for kk, vv in v.items() if kk not in ("n2", "r")}
                       if isinstance(v, dict) else v) for k, v in res.items()}, fp, indent=1)
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk not in ("n2", "r")}
                          if isinstance(v, dict) else v) for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    main()
