"""C1: separation outcomes at rtol = 1e-10 against rtol = 1e-12 (S1 for beta = 3, 8; C2 r0 = 50 r_t
for beta = 4.7).

    <venv>/bin/python -I analysis_c1.py <c1.npz> <s1.npz> <c2_r50.npz> <outdir>
"""
import json
import os
import sys

import numpy as np


def main(c1, s1, c2, outdir):
    os.makedirs(outdir, exist_ok=True)
    a = np.load(c1)
    ma = json.loads(str(a["meta"]))
    res = {}
    for ref_path in (s1, c2):
        b = np.load(ref_path)
        mb = json.loads(str(b["meta"]))
        for ib, beta in enumerate(a["betas"]):
            kb = np.where(np.abs(b["betas"] - beta) < 1e-9)[0]
            if not len(kb):
                continue
            for law in ma["laws"]:
                for s in ma["senses"]:
                    i, j = ma["laws"].index(law), ma["senses"].index(s)
                    i2, j2 = mb["laws"].index(law), mb["senses"].index(s)
                    x = a["separated"][i, j, ib] > 0
                    y = b["separated"][i2, j2, kb[0]] > 0
                    va, vb = a["vinf"][i, j, ib], b["vinf"][i2, j2, kb[0]]
                    ok = x & y & (a["a_min"][i, j, ib] >= 1e-4) & (b["a_min"][i2, j2, kb[0]] >= 1e-4)
                    res[f"beta{beta:g}_{'pro' if s > 0 else 'retro'}_{law}"] = {
                        "sf_rtol1e-10": float(x.mean()), "sf_rtol1e-12": float(y.mean()),
                        "phases_different": int((x != y).sum()),
                        "vinf_median_rel_diff": (float(np.median(np.abs(va[ok] / vb[ok] - 1)))
                                                 if ok.any() else None)}
    with open(os.path.join(outdir, "c1_summary.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:5])
