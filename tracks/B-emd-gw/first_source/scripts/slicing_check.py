#!/usr/bin/env python3
"""P9 of JOURNAL.md: is the code's slicing the Newtonian one at first order?

    python3 slicing_check.py <run dir> [...]          (output: $NRPIC_RUN_DIR)

In the Newtonian gauge alpha = a (1 + Phi), gamma^(1/6) = a (1 - Psi) with Phi = Psi, so
alpha gamma^(1/6) = a^2 at first order while alpha and gamma^(1/6) separately carry Phi.
Per restart dump: rms of delta ln alpha, delta ln gamma^(1/6) (= -(1/2) delta ln chi) and
delta ln(alpha gamma^(1/6)), deviations from the volume means. Writes slicing_check.json
and slicing_check.{png,pdf}.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from gwdiag import readers  # noqa: E402


def rms_dev(x):
    return float(np.sqrt(np.mean((x - x.mean()) ** 2)))


def main():
    out = os.environ.get("NRPIC_RUN_DIR", ".")
    res = {}
    for rd in sys.argv[1:]:
        rows = []
        for f in sorted(glob.glob(os.path.join(rd, "rst", "*.rst"))):
            d = readers.read_rst(f)
            la = np.log(d["alpha"])
            lg = -0.5 * np.log(d["chi"])
            rows.append({"file": os.path.basename(f), "time": d["time"], "a": float(np.mean(d["chi"]) ** -0.5),
                         "rms_dln_alpha": rms_dev(la), "rms_dln_gamma16": rms_dev(lg),
                         "rms_dln_alpha_gamma16": rms_dev(la + lg),
                         "corr": float(np.corrcoef(la.ravel(), lg.ravel())[0, 1]) if rms_dev(la) > 0 else None})
            print(rd, rows[-1], flush=True)
        res[os.path.basename(rd.rstrip("/"))] = rows
    with open(os.path.join(out, "slicing_check.json"), "w") as f:
        json.dump(res, f, indent=1)
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.4, 3.0))
    for c, (name, rows) in zip(fs.SERIES, res.items()):
        rows = [r for r in rows if r["rms_dln_alpha"] > 0]
        a = [r["a"] for r in rows]
        ax.loglog(a, [r["rms_dln_alpha"] for r in rows], "o-", color=c, ms=3, label=r"$\delta\ln\alpha$ (%s)" % name)
        ax.loglog(a, [r["rms_dln_gamma16"] for r in rows], "s--", color=c, ms=3, label=r"$\delta\ln\gamma^{1/6}$")
        ax.loglog(a, [r["rms_dln_alpha_gamma16"] for r in rows], "^:", color=c, ms=4,
                  label=r"$\delta\ln(\alpha\gamma^{1/6})$")
    ax.set_xlabel(r"$a$")
    ax.set_ylabel("rms over the box")
    ax.legend(fontsize=6.5)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "slicing_check"))


if __name__ == "__main__":
    main()
