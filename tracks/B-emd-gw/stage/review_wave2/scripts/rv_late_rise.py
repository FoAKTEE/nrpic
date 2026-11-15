"""Lead's independent check of the band split of the late TT rise (first_source P7,
wave 2 review R6b of ../JOURNAL.md).

Reads two restart dumps of each wave-1 cosmology run with gw_diag's restart reader (the
only shared code; reviewed in wave 1), projects h = tilde gamma - 1 onto its flat TT part
with its own projector, and sums the mean square in the bands m = |k| L / 2 pi < 10,
10 <= m < 20 and m >= 20 (Nyquist planes dropped, k = 0 dropped).

Usage: rv_late_rise.py OUTDIR
"""
import json
import os
import sys

import numpy as np

WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5))
sys.path.insert(0, os.path.join(WT, "tracks/B-emd-gw/gw_diag"))
from gwdiag import readers  # noqa: E402

RUNS = {"quadratic": "/data/haiyangw/nrpic/runs/cosmo/dav_c256_n128_t/rst",
        "cubic": "/data/haiyangw/nrpic/runs/cosmo/dav_c256_n128_pcs4bt/rst"}
DUMPS = ["east.00007.rst", "east.00013.rst"]
NAMES = {(0, 0): "gxx", (0, 1): "gxy", (0, 2): "gxz", (1, 1): "gyy", (1, 2): "gyz", (2, 2): "gzz"}


def bands(path):
    d = readers.read_rst(path)
    chi = d["chi"]
    a = float(np.mean(chi)) ** -0.5
    n = chi.shape
    H = np.zeros((3, 3, n[0], n[1], n[2] // 2 + 1), complex)
    for (i, j), nm in NAMES.items():
        F = np.fft.rfftn(d[nm] - (1.0 if i == j else 0.0))
        H[i, j] = F
        H[j, i] = F
    del d
    mz = np.fft.fftfreq(n[0]) * n[0]
    my = np.fft.fftfreq(n[1]) * n[1]
    mx = np.fft.rfftfreq(n[2]) * n[2]
    MZ, MY, MX = np.meshgrid(mz, my, mx, indexing="ij")
    m = np.sqrt(MX ** 2 + MY ** 2 + MZ ** 2)
    mm = m.copy(); mm[0, 0, 0] = 1.0
    kh = np.stack([MX, MY, MZ]) / mm
    P = np.eye(3)[:, :, None, None, None] - kh[:, None] * kh[None, :]
    LH = np.einsum("ia...,ab...,bj...->ij...", P, H, P) - 0.5 * P * np.einsum("ab...,ba...->...", P, H)
    pw = (np.abs(LH) ** 2).sum((0, 1))
    # traceless non-TT part: |H_traceless|^2 - |LH|^2
    trH = np.einsum("aa...->...", H)
    Htl = H - np.eye(3)[:, :, None, None, None] * trH / 3.0
    pnt = (np.abs(Htl) ** 2).sum((0, 1)) - pw
    w = np.full(mx.shape, 2.0); w[0] = 1.0
    if n[2] % 2 == 0:
        w[-1] = 0.0
    W = np.broadcast_to(w, pw.shape).copy()
    for ax, ln in enumerate(n[:2]):
        if ln % 2 == 0:
            sl = [slice(None)] * 3; sl[ax] = ln // 2
            W[tuple(sl)] = 0.0
    W[0, 0, 0] = 0.0
    norm = float(np.prod(n)) ** 2
    ms = lambda sel: float((pw * W)[sel].sum() / norm)  # noqa: E731
    out = {"file": os.path.basename(path), "a": a,
           "ms_total": ms(m >= 0), "ms_lt10": ms(m < 10), "ms_10_20": ms((m >= 10) & (m < 20)),
           "ms_ge20": ms(m >= 20), "ms_ge40": ms(m >= 40),
           "ms_nonTT": float((pnt * W).sum() / norm)}
    out["rms_total"] = out["ms_total"] ** 0.5
    out["rms_nonTT"] = out["ms_nonTT"] ** 0.5
    return out


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(outdir, exist_ok=True)
    res = {}
    for lab, base in RUNS.items():
        rows = [bands(f"{base}/{f}") for f in DUMPS]
        e, l = rows
        rise = l["ms_total"] - e["ms_total"]
        res[lab] = {"rows": rows,
                    "frac_rise_ge20": (l["ms_ge20"] - e["ms_ge20"]) / rise,
                    "frac_rise_ge40": (l["ms_ge40"] - e["ms_ge40"]) / rise,
                    "rms_lt10_early_late": [e["ms_lt10"] ** 0.5, l["ms_lt10"] ** 0.5],
                    "rms_10_20_early_late": [e["ms_10_20"] ** 0.5, l["ms_10_20"] ** 0.5],
                    "rms_ge20_early_late": [e["ms_ge20"] ** 0.5, l["ms_ge20"] ** 0.5]}
        print(lab, json.dumps(res[lab], indent=1), flush=True)
    res["deposit_ratio_rms_ge20_late"] = (res["cubic"]["rms_ge20_early_late"][1]
                                          / res["quadratic"]["rms_ge20_early_late"][1])
    res["deposit_ratio_rms_lt10_late"] = (res["cubic"]["rms_lt10_early_late"][1]
                                          / res["quadratic"]["rms_lt10_early_late"][1])
    with open(f"{outdir}/rv_late_rise.json", "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
