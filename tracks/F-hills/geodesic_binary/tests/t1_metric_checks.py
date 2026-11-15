"""T1: metric identities, closed-form derivatives, CKS metric against python/nrpic/kerr.py, and
the flat-space (M = 0) limit of the HRNA equations for a circular binary.

Run: <venv>/bin/python -I tests/t1_metric_checks.py <outdir>
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "..", "..", "..", "python"))
import hrna  # noqa: E402
from nrpic import kerr  # noqa: E402


def fields(coords, x, a):
    g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
    hrna.metric(coords, np.asarray(x, float), 1.0, a, g, gi, dg)
    return g, gi, dg


def main(outdir):
    rng = np.random.default_rng(1)
    res = {}
    for coords, a, name in ((hrna.COORDS_SCH, 0.0, "sch"), (hrna.COORDS_CKS, 0.9, "cks_a0.9"),
                            (hrna.COORDS_CKS, -0.7, "cks_a-0.7"), (hrna.COORDS_CKS, 0.0, "cks_a0")):
        e_id, e_dg, e_ref = 0.0, 0.0, 0.0
        for _ in range(200):
            r = 10 ** rng.uniform(np.log10(3.0), 3.0)
            th = math.acos(rng.uniform(-1, 1))
            ph = rng.uniform(0, 2 * math.pi)
            x = r * np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)])
            g, gi, dg = fields(coords, x, a)
            e_id = max(e_id, np.max(np.abs(g @ gi - np.eye(4))))
            hstep = 1e-3 * r
            for k in range(3):
                d = np.zeros(3)
                d[k] = hstep
                gp1 = fields(coords, x + d, a)[0]
                gm1 = fields(coords, x - d, a)[0]
                gp2 = fields(coords, x + 2 * d, a)[0]
                gm2 = fields(coords, x - 2 * d, a)[0]
                fd = (-gp2 + 8 * gp1 - 8 * gm1 + gm2) / (12 * hstep)
                scale = np.max(np.abs(dg[k])) + 1e-300
                e_dg = max(e_dg, np.max(np.abs(fd - dg[k])) / scale)
            if coords == hrna.COORDS_CKS:
                gref = kerr.g4_cks(x, a, 1.0)
                e_ref = max(e_ref, np.max(np.abs(gref - g)))
        res[name] = dict(identity_max=e_id, dg_fd_rel_max=e_dg,
                         g_vs_python_nrpic_max=(e_ref if coords == hrna.COORDS_CKS else None))
    # flat-space limit: M = 0, circular binary, 100 periods; HRNA at two binary masses and Newton
    def flat_binary(law, mb, a0=1.0):
        m1 = m2 = mb / 2
        w = math.sqrt(mb / a0 ** 3)
        y0 = np.array([100.5, 0, 0, 0, 0.5 * w, 0, 99.5, 0, 0, 0, -0.5 * w, 0])  # CM off the origin
        T0 = 2 * math.pi / w
        out = hrna.integrate(law, hrna.COORDS_SCH, hrna.PAIR_GRAVITY, 0.0, 0.0, m1, m2, 0.0,
                             0.0, y0, T0 / 200, 1e-12, 1e-16, 1e300, 1e300, 0.0, 100 * T0, 10 ** 7,
                             a0, 200000, hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, hrna._work())
        rec_t, rec_y = out[4], out[5]
        sep = np.linalg.norm(rec_y[:, 0:3] - rec_y[:, 6:9], axis=1)
        v2 = (0.5 * w * a0) ** 2
        return dict(n_steps=int(out[7]), periods=float(rec_t[-1] / T0),
                    max_rel_sep_dev=float(np.max(np.abs(sep - a0)) / a0),
                    member_v2=v2, steps_per_period=float(out[7] / (rec_t[-1] / T0))), rec_t / T0, sep

    cases = (("hrna_mb1e-6", hrna.LAW_HRNA, 1e-6), ("hrna_mb1e-8", hrna.LAW_HRNA, 1e-8),
             ("newton_mb1e-6", hrna.LAW_NEWTON, 1e-6))
    curves = {}
    for name, law, mb in cases:
        res["flat_binary_" + name], tt, sep = flat_binary(law, mb)
        curves[name] = (tt, sep)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "t1_metric_checks.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 2.8))
    ax = fig.add_axes([0.2, 0.17, 0.75, 0.78])
    labels = {"hrna_mb1e-6": r"HRNA, $m_b=10^{-6}$", "hrna_mb1e-8": r"HRNA, $m_b=10^{-8}$",
              "newton_mb1e-6": r"Newton, $m_b=10^{-6}$"}
    for (name, _, _), c in zip(cases, (fs.PAL["red"], fs.PAL["yellow"], fs.PAL["blue"])):
        tt, sep = curves[name]
        ax.semilogy(tt, np.abs(sep - 1.0) + 1e-17, color=c, lw=0.8, label=labels[name])
    ax.set_ylim(1e-17, 1e-4)
    ax.set_xlabel(r"$t/T_0$")
    ax.set_ylabel(r"$|a - a_0|/a_0$ (flat space)")
    ax.legend(loc="upper left", ncol=1, fontsize=8)
    fs.save(fig, os.path.join(outdir, "t1_flat_binary"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
