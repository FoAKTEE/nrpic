#!/usr/bin/env python3
"""Test T0 of tracks/core/JOURNAL-scalar3.md: the mode entity and the mode stream of the
random-number interface (rng.mode_entity, rng.stochastic_mode_stream; twins of
ModeEntity and StochasticModeStream in athenak/src/utils/rng_mesh.hpp).

    python3 t0_modekey.py --philox-ref FILE [--out DIR]

FILE: tracks/E-stoch-inf/noise/ref/philox_ref.py of branch track/E-stoch-inf (Track E's
independent implementation of the keys and draws, written from rng.md), exported with
git show.  Writes DIR/summary.json; exit status 1 if a check fails."""
import argparse
import importlib.util
import os
import sys

import s3
from s3 import common, np, sf
from nrpic import rng


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--philox-ref", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    summ = {}
    ok = True

    # P0a: the entity is CellEntity(n + 2^20)
    n, _ = sf.mode_set(4096)
    off = 1 << 20
    new = rng.mode_entity(n[:, 0], n[:, 1], n[:, 2])
    old = rng.cell_entity(n[:, 0] + off, n[:, 1] + off, n[:, 2] + off)
    summ["modes_nmax2_4096"] = int(n.shape[0])
    summ["entity_differing"] = int((new != old).sum())
    corner = np.array([[-off, off - 1, 0], [off - 1, -off, -1], [0, 0, 0]])
    e1 = rng.mode_entity(corner[:, 0], corner[:, 1], corner[:, 2])
    e2 = rng.cell_entity(corner[:, 0] + off, corner[:, 1] + off, corner[:, 2] + off)
    summ["corner_differing"] = int((e1 != e2).sum())
    summ["corner_entities_hex"] = [hex(int(x)) for x in e1]
    refused = 0
    for bad in ([off, 0, 0], [0, -off - 1, 0]):
        try:
            rng.mode_entity(*[np.array([b]) for b in bad])
        except ValueError:
            refused += 1
    try:
        rng.mode_entity(np.array([0.5]), np.array([0]), np.array([0]))
    except TypeError:
        refused += 1
    summ["out_of_range_or_float_refused"] = refused
    s_new = rng.stochastic_mode_stream(np.arange(4))
    s_old = rng.stream(rng.STREAM_STOCHASTIC, (1 << 16) | np.arange(4))
    summ["stream_differing"] = int((s_new != s_old).sum())
    summ["stream_dof0_hex"] = hex(int(s_new[0]))
    ok &= summ["entity_differing"] == 0 and summ["corner_differing"] == 0 \
        and refused == 3 and summ["stream_differing"] == 0

    # P0b: amplitudes against Track E's independent reference, bit for bit
    spec = importlib.util.spec_from_file_location("philox_ref", a.philox_ref)
    pr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pr)
    n, _ = sf.mode_set(100)
    cmp = []
    for seed in (1, 20261115):
        for dof in (0, 1):
            for epoch in (0, 7):
                mine = sf.mode_alpha(seed, dof, epoch, n)
                ref = pr.mode_alpha(seed, dof, epoch, n)
                same = int((mine.view(np.uint64) == np.asarray(ref, dtype=complex)
                            .view(np.uint64)).all())
                cmp.append(dict(seed=seed, dof=dof, epoch=epoch, modes=int(n.shape[0]),
                                bit_identical=same,
                                max_abs_diff=float(np.abs(mine - ref).max())))
                ok &= bool(same)
    summ["against_track_E_reference"] = cmp
    summ["ok"] = bool(ok)
    common.dump_json(summ, os.path.join(out, "summary.json"))
    print("T0", "passed" if ok else "FAILED", os.path.join(out, "summary.json"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
