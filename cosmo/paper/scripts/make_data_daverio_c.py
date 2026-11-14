"""Data of the random-field test of Daverio, Dirian & Mitsou (test C) for the working
paper: cell means of the relative constraints against redshift, and the departure of the
power spectrum of the energy-density contrast from linear theory at z = 100, 10, 1, for
both boxes, with and without the compensation of the cloud."""
import os

import numpy as np

from common import DATA, RUNS
import daverio_c as dc
import random_field as rf

CASES = {
    704.0: (220.0, ("dav_c704_n32_t", "dav_c704_n64_t", "dav_c704_n128_k",
                    "dav_c704_n32_dcompt", "dav_c704_n64_dcompt", "dav_c704_n128_dcompt",
                    "dav_c704_n32_pcsct", "dav_c704_n64_pcsct", "dav_c704_n128_pcsct",
                    "dav_c704_n32_pcs4bt", "dav_c704_n64_pcs4bt", "dav_c704_n128_pcs4bt",
                    "dav_c704_n32_k", "dav_c704_n32_cic", "dav_c704_n32_pcs")),
    256.0: (40.0, ("dav_c256_n64_t", "dav_c256_n128_t", "dav_c256_n64_dcompt",
                   "dav_c256_n64_pcsct", "dav_c256_n64_pcs4bt", "dav_c256_n128_pcs4bt",
                   "dav_c256_n64")),
}


def thin(n, m=400):
    return np.unique(np.linspace(0, n - 1, min(n, m)).astype(int))


out = {}
for box, (cut, cases) in CASES.items():
    kcut = 2.0*np.pi/cut
    for c in cases:
        d = dc.load(os.path.join(RUNS, c), box)
        if d is None:
            continue
        tag = c.replace("dav_", "")
        i = thin(len(d["z"]))
        for key in ("z", "Hr", "Mr"):
            out[f"{tag}_{key}"] = d[key][i]
        sp = d["spec"]
        if len(sp) < 2:
            continue
        k0 = sp[0]["k"]
        keep = k0 <= kcut*1.0001
        out[f"{tag}_k"] = k0[keep]
        for q in sp[1:]:
            zq = 1001.0/q["a"] - 1.0
            lin = dc.linear_field(sp[0]["delta"], box, q["a"])
            _, pan, _ = rf.measure_power(lin, box, nbins=None)
            name = f"{zq:.0f}" if zq > 0.5 else "0"
            out[f"{tag}_dev_z{name}"] = (np.abs(q["P"] - pan)/pan)[keep]
            out[f"{tag}_rms_z{name}"] = q["rms"]
np.savez_compressed(os.path.join(DATA, "daverio_c.npz"), **out)
print("wrote", os.path.join(DATA, "daverio_c.npz"),
      sorted({"_".join(k.split("_")[:-1]) for k in out if k.endswith("_z")}))
