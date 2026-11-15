#!/usr/bin/env python3
"""Second-order reference of the box mode K1 = (k, k, 0) for the scan (P2 of JOURNAL.md).

    python3 reference_run.py OUTDIR

Writes OUTDIR/reference.json (g(tau), s(eps), predicted c_+ at selected a) and the figure
OUTDIR/reference.{png,pdf}.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from fslib import reference as ref  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
os.makedirs(out, exist_ok=True)
tau = np.linspace(0.0, ref.tau_of_a(140.0), 4001)
g, gp = ref.g_of_tau(tau)
a = ref.a_of_tau(tau)
res = {"delta": 0.01, "L": 4.0, "K": float(np.sqrt(2) * np.pi / 2), "period": float(2 * np.pi / (np.sqrt(2) * np.pi / 2)),
       "s": {str(e): ref.static_amplitude(0.01, e) for e in (0.1, 0.3, 1.0)},
       "phis_eps1": ref.phis(0.01, 1.0)}
sel = {}
for av in (2, 5, 10, 20, 40, 60, 100, 140):
    t = float(ref.tau_of_a(av))
    gv = float(np.interp(t, tau, g))
    sel[str(av)] = {"tau": t, "g": gv, "c_plus_over_eps": gv * ref.static_amplitude(0.01, 1.0)}
res["selected"] = sel
# envelope of g - 1 times a (check 3A: ~ constant)
dev = np.abs(g - 1)
i = np.where((dev[1:-1] > dev[:-2]) & (dev[1:-1] >= dev[2:]))[0] + 1
res["junk_envelope_times_a"] = [[float(a[j]), float(dev[j] * a[j])] for j in i[:12]]
with open(os.path.join(out, "reference.json"), "w") as f:
    json.dump(res, f, indent=1)
np.savez(os.path.join(out, "reference_g.npz"), tau=tau, a=a, g=g, gp=gp)

fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402
fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
ax[0].plot(a, g, color=fs.PAL["blue"], label=r"$g(\tau)$")
ax[0].axhline(1.0, **fs.GUIDE, label="quasi-static value")
ax[0].set_xscale("log")
ax[0].set_xlabel(r"$a$")
ax[0].set_ylabel(r"$c_+(K_1)/s$")
ax[0].legend(loc="lower right")
ax[1].loglog(a[i], dev[i], "o", color=fs.PAL["red"], ms=3, label=r"maxima of $|g-1|$")
ax[1].loglog(a, dev[i[2]] * a[i[2]] / a, **fs.GUIDE, label=r"$\propto 1/a$")
ax[1].set_xlabel(r"$a$")
ax[1].set_ylabel(r"$|g-1|$")
ax[1].legend(loc="upper right")
fig.suptitle(r"response of the mode $(k,k,0)$ from rest; $s=-(5/6)\phi_x\phi_y=%.3e\,\epsilon$"
             % ref.static_amplitude(0.01, 1.0), fontsize=10)
fig.tight_layout()
fs.save(fig, os.path.join(out, "reference"))
print(json.dumps({k: v for k, v in res.items() if k != "junk_envelope_times_a"}, indent=1))
