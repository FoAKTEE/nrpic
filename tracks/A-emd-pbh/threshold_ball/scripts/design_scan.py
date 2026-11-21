#!/usr/bin/env python3
"""Design of the amplitude scan of package threshold_ball (A-emd-pbh, batch 5 of wave 3).

Exact (LTB) events of the compensated top-hat expanding ball of data set 3 (H R_b = 0.7,
R1 = 0.65 R_b, R2 = 0.95 R_b, M = 1, matter edge 4.25 M) as a function of the core contrast
delta_c: core turnaround and crunch, first trapped sphere (tau_AH, m, R_AH), largest 2m/R on
the slice, whether the compensating shell is bound, and the finite-duration outcome at the
end times of the scan.  Uses the exact solution of expball (A-pre-1) through the readers of
conv_ball (copied at 9cddbfc6 from runs_ball).  Writes design.json, design.md and a figure.

    python3 tracks/A-emd-pbh/threshold_ball/scripts/design_scan.py --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "conv_ball", "scripts"))
import common as C            # noqa: E402

sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
from nrpic import figstyle as fs   # noqa: E402


def events(dc, HRb=0.7, R1f=0.65, R2f=0.95, rm=4.25, M=1.0):
    Rb = 2.0 * M / HRb ** 2
    spec = dict(profile="tophat", HRb=HRb, M=M, delta_c=dc, R1=R1f * Rb, R2=R2f * Rb,
                edge_width=rm - Rb, R1_over_Rb=R1f, R2_over_Rb=R2f, rm=rm)
    ball = C.ball_from_spec(spec)
    summ = ball.summary()
    R1, R2 = spec["R1"], spec["R2"]
    grid = np.concatenate([np.linspace(0.005, R1, 300), np.linspace(R1 * (1 + 1e-12), R2, 1500),
                           np.linspace(R2 * (1 + 1e-9), ball.R_out * 0.99999, 200)])
    S = C.XE.Shells(ball, grid)
    out = dict(dc=dc, H=float(ball.H), Rb=float(ball.Rb), t_i=float(ball.t_i),
               max_2m_over_R=float(summ["max_2m_over_R"]), delta_u=float(summ["delta_u"]))
    core = C.XE.Shells(ball, np.array([0.1 * R1]))
    out["core_E"] = float(core.E[0])
    out["core_tau_ta"] = float(core.tau_ta[0]) if np.isfinite(core.tau_ta[0]) else None
    out["core_tau_c"] = float(core.tau_c[0]) if np.isfinite(core.tau_c[0]) else None
    fin = np.isfinite(S.tau_ah)
    if fin.any():
        fh = S.first_horizon()
        out.update(tau_AH=float(fh["tau_ah"]), m_AH=float(fh["m"]), R_AH=float(2 * fh["m"]),
                   R_i_AH=float(fh["R_i"]))
    else:
        out.update(tau_AH=None, m_AH=None, R_AH=None, R_i_AH=None)
    sh = S.E[(grid > R1) & (grid < R2)]
    out["shell_E_max"] = float(sh.max())
    out["shell_bound"] = bool(sh.max() < 0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--dc", type=float, nargs="*",
                    default=[-0.3, 0.0, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.85, 1.0, 1.2, 1.5, 2.0])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for dc in a.dc:
        try:
            r = events(dc)
        except Exception as exc:                      # a contrast the model refuses is recorded
            r = dict(dc=dc, error=repr(exc))
        rows.append(r)
        print(json.dumps(r))
    with open(os.path.join(a.out, "design.json"), "w") as f:
        json.dump(rows, f, indent=1)
    with open(os.path.join(a.out, "design.md"), "w") as f:
        f.write("| delta_c | core E | core tau_ta | core tau_c | tau_AH | m_AH | R_AH | max 2m/R | shell bound |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            if "error" in r:
                f.write(f"| {r['dc']} | error: {r['error']} |||||||\n")
                continue
            g = lambda k: ("-" if r.get(k) is None else f"{r[k]:.5g}")   # noqa: E731
            f.write(f"| {r['dc']} | {g('core_E')} | {g('core_tau_ta')} | {g('core_tau_c')} | {g('tau_AH')} | "
                    f"{g('m_AH')} | {g('R_AH')} | {g('max_2m_over_R')} | {r['shell_bound']} |\n")
    fs.use_style()
    import matplotlib.pyplot as plt
    ok = [r for r in rows if "error" not in r and r.get("tau_AH") is not None]
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    d = np.array([r["dc"] for r in ok])
    ax[0].plot(d, [r["tau_AH"] for r in ok], "o-", label=r"$\tau_{\rm AH}$ (first trapped sphere)")
    ax[0].plot(d, [r["core_tau_ta"] for r in ok], "s--", label=r"core turnaround")
    ax[0].plot(d, [r["core_tau_c"] for r in ok], "^:", label=r"core crunch")
    ax[0].set_xscale("log"); ax[0].set_yscale("log")
    ax[0].set_xlabel(r"core contrast $\delta_c$"); ax[0].set_ylabel(r"proper time [$M$]")
    ax[0].legend(fontsize=7)
    ax[1].plot(d, [r["m_AH"] for r in ok], "o-", label=r"$m_{\rm AH}$ at first trapping")
    ax[1].plot(d, [r["R_AH"] for r in ok], "s--", label=r"$R_{\rm AH}=2m$")
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"core contrast $\delta_c$"); ax[1].set_ylabel(r"[$M$]")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out, f"fig_design_scan.{ext}"), dpi=150)


if __name__ == "__main__":
    main()
