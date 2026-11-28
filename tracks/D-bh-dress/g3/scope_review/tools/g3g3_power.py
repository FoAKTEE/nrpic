#!/usr/bin/env python3
"""B2b of the scope review: power of a whole-run form of G3-G3 (means over 100-400 M) with the noise
surrogates of g2_analogs.py (FK - FN4 high-pass and full; mesh correlation from FL16 - ES-FL).
Usage: g3g3_power.py OUTDIR [sample|window]   (anchor of Delta M: the 20 M sample, or the mean over 20-40 M)
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g2_analogs as ga  # noqa: E402
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def main():
    out = Path(sys.argv[1])
    anchor = sys.argv[2] if len(sys.argv) > 2 else "sample"
    grid = np.arange(20.0, 399.75, 0.5)
    M = {n: ga.on_grid(n, grid) for n in ("FK", "FN4", "ES-FL")}
    g300 = grid[grid <= 299.0]
    M16 = ga.on_grid("FL16", g300)
    n_fk4 = M["FK"] - M["FN4"]
    hp = n_fk4 - ga.boxcar(n_fk4, 101)
    sig_hp = np.nanstd(hp[60:-60]) / np.sqrt(1.25)
    d16 = (M16 - M16[0]) - (M["ES-FL"][: g300.size] - M["ES-FL"][0])
    d16_hp = d16 - ga.boxcar(d16, 101)
    rho = float(np.clip(1.0 - np.nanvar(d16_hp[60:-60]) / (2 * sig_hp ** 2), 0.0, 0.95))
    A16 = float(np.nanmean(d16[(g300 >= 250) & (g300 <= 299)]))
    srcs = {"highpass": np.nan_to_num(hp - np.nanmean(hp)) / np.sqrt(1.25),
            "full": np.nan_to_num(n_fk4 - np.nanmean(n_fk4)) / np.sqrt(1.25)}
    ramp = np.clip((grid - 20.0) / 130.0, 0.0, 1.0)
    late = grid >= 100.0
    aw = (grid >= 20.0) & (grid < 40.0)

    def anc(x):
        return x[aw].mean() if anchor == "window" else x[0]
    h = {8: 1 / 8, 12: 1 / 12, 16: 1 / 16}
    rng = np.random.default_rng(271127)
    rows = []
    cases = [("p2", 2.0, False), ("p1", 1.0, False), ("none", 2.0, True)]
    for label, p, flat in cases:
        c = A16 / (h[16] ** p - h[8] ** p)
        for amp in (0.25, 0.5, 1.0, 2.0):
            for kind, src in srcs.items():
                ok, rat = 0, []
                for _ in range(1000):
                    com = ga.surrogate(src, rng)
                    nz = {k: np.sqrt(rho) * com + np.sqrt(1 - rho) * ga.surrogate(src, rng) for k in h}
                    if flat:   # no convergence: the 8-12 and 12-16 deterministic steps are equal
                        det = {8: 0.0, 12: 0.5 * amp * A16, 16: amp * A16}
                        dm = {k: det[k] * ramp + nz[k] - anc(nz[k]) for k in h}
                    else:
                        dm = {k: amp * c * h[k] ** p * ramp + nz[k] - anc(nz[k]) for k in h}
                    m1 = np.mean((dm[8] - dm[12])[late])
                    m2 = np.mean((dm[12] - dm[16])[late])
                    r = abs(m1) / max(abs(m2), 1e-30)
                    rat.append(r)
                    ok += (abs(m1) > abs(m2)) and (1.5 <= r <= 8.0) and (np.sign(m1) == np.sign(m2))
                rows.append(dict(case=label, p=p, amp=amp, noise=kind, P_pass=ok / 1000,
                                 ratio_q10_q50_q90=[float(np.quantile(rat, q)) for q in (0.1, 0.5, 0.9)]))
                print(rows[-1])
    res = dict(anchor=anchor, rho=rho, sigma_N_highpass=float(sig_hp), A16=A16, rows=rows)
    (out / "g3g3_power.json").write_text(json.dumps(res, indent=1))
    fs.use_style()
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    for label, mk in (("p2", "o"), ("p1", "s"), ("none", "x")):
        rr = [r for r in rows if r["case"] == label and r["noise"] == "full"]
        ax.plot([r["amp"] for r in rr], [r["P_pass"] for r in rr], mk + "-", label={"p2": "order 2", "p1": "order 1", "none": "no convergence"}[label])
    ax.set_xscale("log"); ax.set_xlabel("deterministic mesh difference / G2's (+5.8e-4)")
    ax.set_ylabel("P(pass), whole-run means"); ax.set_ylim(-0.02, 1.02); ax.legend(fontsize=7)
    ax.set_title(f"B2b/c: power of a whole-run G3-G3 (anchor: {anchor})", fontsize=8)
    fig.tight_layout(); fig.savefig(out / "g3g3_power.png", dpi=150); fig.savefig(out / "g3g3_power.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main())
