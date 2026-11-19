#!/usr/bin/env python3
"""Figures of the tests T3 to T5 of work package mpi from their registered runs, into
tracks/core/analysis/mpi/figs (and the figs directory of each run).

    make_figs.py <figdir>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mpi_figs  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/core"
CASES = [
    ("t3_cluster", S + "/core-20261119-154814-ca46836/t3_cluster"),
    ("t3_cluster_ext", S + "/core-20261119-155306-ee6c92c/t3_cluster_ext"),
    ("t5_smr_cic", S + "/core-20261119-161206-421d7e3/t5_smr_cic"),
    ("t5_smr_tsc_cap", S + "/core-20261119-161208-421d7e3/t5_smr_tsc_cap"),
    ("t5_smr_pcs", S + "/core-20261119-161349-896e22c/t5_smr_pcs"),
    ("t5_smr_cluster", S + "/core-20261119-161503-32b23c0/t5_smr_cluster"),
    ("t5_amr_cluster", S + "/core-20261119-161351-896e22c/t5_amr_cluster"),
    ("t5_amr_offset", S + "/core-20261119-161801-9d336d6/t5_amr_offset"),
]
RESTARTS = [
    ("t4_ext_same", S + "/core-20261119-155306-ee6c92c/t3_cluster_ext",
     S + "/core-20261119-155721-89ebf16/t4_ext_same", [(1, 1), (2, 2), (4, 4)]),
    ("t4_ext_cross", S + "/core-20261119-155306-ee6c92c/t3_cluster_ext",
     S + "/core-20261119-160825-0e90ab7/t4_ext_cross", [(1, 4), (4, 1), (2, 4)]),
]


def main():
    figdir = os.path.abspath(sys.argv[1])
    for case, base in CASES:
        for p in mpi_figs.make(case, [1, 2, 4], base, figdir):
            print(p)
    for name, src, base, pairs in RESTARTS:
        sub = os.path.join(figdir, name)
        for p in mpi_figs.make_restart(src, pairs, base, sub):
            print(p)


if __name__ == "__main__":
    main()
