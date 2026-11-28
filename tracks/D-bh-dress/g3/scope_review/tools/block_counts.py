#!/usr/bin/env python3
"""Calculation A of the scope review: MeshBlock counts of the G3 mesh members (athena -m, no physics).

Usage: block_counts.py OUTDIR   (run under nrpic-run; decks from tools/make_decks.py)
Writes OUTDIR/block_counts.json and one subdirectory per deck with mesh_structure.dat and the log.
"""
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

EXE = "/data/haiyangw/nrpic/.work/build_cpu_v08/src/athena"
HERE = Path(__file__).resolve().parent
DECKS = HERE.parent / "decks"


def count(deck, out):
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "athena.log", "w") as log:
        rc = subprocess.run([EXE, "-i", str(deck), "-m"], cwd=out, stdout=log, stderr=subprocess.STDOUT,
                            env={"OMP_NUM_THREADS": "1", "PATH": "/usr/bin:/bin"}).returncode
    ms = out / "mesh_structure.dat"
    levels = Counter(int(m.group(1)) for m in re.finditer(r"#  Logical level (\d+)", ms.read_text())) if ms.exists() else {}
    txt = deck.read_text()
    nxb = int(re.search(r"<meshblock>\s*\nnx1\s*=\s*(\d+)", txt).group(1))
    nroot = int(re.search(r"<mesh>.*?\nnx1\s*=\s*(\d+)", txt, re.S).group(1))
    nb = sum(levels.values())
    lmin = min(levels) if levels else 0
    return dict(deck=deck.name, returncode=rc, meshblock_nx=nxb, root_nx=nroot, n_blocks=nb,
                by_level={str(k - lmin): v for k, v in sorted(levels.items())},
                cells=nb * nxb ** 3, cells_with_ghosts=nb * (nxb + 8) ** 3)


def main():
    outdir = Path(sys.argv[1])
    res = {}
    for name in ("g8", "g12", "g16", "g16b"):
        res[name] = count(DECKS / f"{name}.athinput", outdir / name)
        print(json.dumps(res[name]))
    ref = res["g8"]
    for name, r in res.items():
        r["blocks_over_g8"] = r["n_blocks"] / ref["n_blocks"] if ref["n_blocks"] else None
        r["cells_over_g8"] = r["cells"] / ref["cells"] if ref["cells"] else None
        r["ghosted_cells_over_g8"] = r["cells_with_ghosts"] / ref["cells_with_ghosts"] if ref["cells"] else None
    (outdir / "block_counts.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
