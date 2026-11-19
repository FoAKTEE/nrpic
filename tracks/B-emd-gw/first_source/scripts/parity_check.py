#!/usr/bin/env python3
"""P15 parity: initial data of make_waves.py (core/requests-b) without jitter against
make_east.py for the same arguments (plane wave delta = 0.01, 64^3, 8 per cell).

    python3 parity_check.py <dir A> <dir B>        (output: $NRPIC_RUN_DIR/parity.json)

Compares particle positions, momenta and masses (same order expected: fiducial lines first,
then the lattice) and the fields psi, K, alpha, Ahat of fields.bin.
"""
import json
import os
import sys

import numpy as np


def read_particles(path):
    with open(path, "rb") as f:
        raw = f.read()
    assert raw[:8] == b"NRPIC001", path
    n = int(np.frombuffer(raw, np.int64, 1, 8)[0])
    rec = np.frombuffer(raw, np.float64, 7 * n, 16).reshape(n, 7)
    return rec


def read_fields(path):
    with open(path, "rb") as f:
        raw = f.read()
    assert raw[:8] == b"NRCOSMO1", path
    n1, n2, n3 = (int(v) for v in np.frombuffer(raw, np.int64, 3, 8))
    nc = n1 * n2 * n3
    return np.frombuffer(raw, np.float64, 9 * nc, 32).reshape(9, nc)


def main():
    a, b = sys.argv[1], sys.argv[2]
    pa, pb = read_particles(os.path.join(a, "particles.nrp")), read_particles(os.path.join(b, "particles.nrp"))
    fa, fb = read_fields(os.path.join(a, "fields.bin")), read_fields(os.path.join(b, "fields.bin"))
    out = {"A": a, "B": b, "N": [len(pa), len(pb)]}
    if len(pa) == len(pb):
        d = np.abs(pa - pb)
        # positions modulo the box (a particle on the boundary may wrap)
        dx = np.abs((pa[:, :3] - pb[:, :3] + 2.0) % 4.0 - 2.0)
        out["max_dx"] = float(dx.max())
        out["max_du"] = float(d[:, 3:6].max())
        out["max_dm_rel"] = float((d[:, 6] / np.abs(pb[:, 6])).max())
    names = ["psi", "K", "alpha", "Axx", "Axy", "Axz", "Ayy", "Ayz", "Azz"]
    out["fields_maxabs_diff"] = {n: float(np.abs(fa[i] - fb[i]).max()) for i, n in enumerate(names)}
    out["fields_maxabs"] = {n: float(np.abs(fb[i]).max()) for i, n in enumerate(names)}
    od = os.environ.get("NRPIC_RUN_DIR", ".")
    with open(os.path.join(od, "parity.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
