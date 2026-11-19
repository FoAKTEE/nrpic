#!/usr/bin/env python3
"""P16 of JOURNAL.md: shell spectra of the TT and non-TT parts of h = tilde gamma - delta (and
of tilde A) in selected dumps, to tell projector leakage at the mesh scale from a resolved
TT response.

    python3 null_spectrum.py name=<dump file> [name=<dump file> ...]     (output: $NRPIC_RUN_DIR)

Per dump: shell sums (|k| L/2pi in bins of width 1) of the mean square of Lambda h and of
the traceless non-TT part, their ratio per shell, the fraction of the TT power at
|k| L/2pi >= 16 (k h >= pi/2 at 64^3) and >= 8, and the same for tilde A. Writes
null_spectrum.json and null_spectrum.{png,pdf}.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from fslib import gauge, modes  # noqa: E402
from gwdiag import tt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def shells(F, g, kk):
    P = tt.power_tensor(F, g).copy()
    P[0, 0, 0] = 0.0
    m = (kk * g.L[0] / (2 * np.pi))
    nb = int(np.ceil(m.max())) + 1
    idx = np.rint(m).astype(int)
    return np.bincount(idx.ravel(), weights=P.ravel(), minlength=nb)


def one(path):
    t, g, chi, gt, At, trK, alpha, beta, d = modes.load(path)
    I = np.eye(3)[:, :, None, None, None]
    h = gauge.traceless(gt - I)
    k, kk, kh = tt._khat(g)
    out = {"file": path, "time": t, "a": float(np.mean(chi) ** -0.5), "n": list(g.n)}
    for key, f in (("h", h), ("A", gauge.traceless(At))):
        F = tt.tensor_rfft(f)
        T = tt.lambda_apply(F, kh)
        T[:, :, 0, 0, 0] = 0.0
        T[:, :, g.nyquist_mask(real=True)] = 0.0
        N = F - T
        N[:, :, 0, 0, 0] = 0.0
        sT, sN = shells(T, g, kk), shells(N, g, kk)
        tot = sT.sum()
        out[key] = {"shell_TT": sT.tolist(), "shell_nonTT": sN.tolist(),
                    "rms_TT": float(np.sqrt(tot)), "rms_nonTT": float(np.sqrt(sN.sum())),
                    "frac_TT_ge16": float(sT[16:].sum() / tot) if tot > 0 else None,
                    "frac_TT_ge8": float(sT[8:].sum() / tot) if tot > 0 else None}
    return out


def main():
    od = os.environ.get("NRPIC_RUN_DIR", ".")
    res = {}
    for arg in sys.argv[1:]:
        name, path = arg.split("=", 1)
        r = one(path)
        res[name] = r
        print(name, f"a={r['a']:.2f}", {k: (r['h'][k]) for k in ('rms_TT', 'rms_nonTT', 'frac_TT_ge16', 'frac_TT_ge8')}, flush=True)
    with open(os.path.join(od, "null_spectrum.json"), "w") as f:
        json.dump(res, f)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.0))
    for name, r in res.items():
        sT = np.array(r["h"]["shell_TT"])
        sN = np.array(r["h"]["shell_nonTT"])
        kb = np.arange(len(sT))
        m = (kb > 0) & (sN > 0)
        l, = ax[0].plot(kb[m], sT[m], label=f"{name} (a={r['a']:.0f}) TT")
        ax[0].plot(kb[m], sN[m], ls="--", color=l.get_color(), lw=0.8)
        with np.errstate(invalid="ignore", divide="ignore"):
            ax[1].plot(kb[m], sT[m] / sN[m], color=l.get_color(), label=name)
    kb = np.arange(1, 56)
    ax[1].plot(kb, 1e-6 * (kb / 4.0) ** 6, color="0.6", ls=":", label="slope (k h)^6")
    for a_ in ax:
        a_.set_xscale("log")
        a_.set_yscale("log")
        a_.set_xlabel("|k| L / 2 pi")
    ax[0].set_ylabel("shell power of h: TT (solid), non-TT (dashed)")
    ax[1].set_ylabel("P_TT / P_nonTT per shell")
    ax[0].legend(fontsize=5)
    ax[1].legend(fontsize=5)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"null_spectrum.{ext}"), dpi=150)


if __name__ == "__main__":
    main()
