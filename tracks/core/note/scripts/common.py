"""Shared paths, run ids and readers of the working note of core (gate G2).

Every input a figure or the ledger reads is checked here against the sha256 its run
recorded: the `sha256sums.txt` of a registered run, or, for the pre-program directories
under runs/, the inventory of run core-20261121-231825-135474c. The outcome of each
check is printed ("sha256 ok", "sha256 not recorded") into the log of the run that
makes the figures.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WT = HERE.parents[3]                      # worktree root
ROOT = Path("/data/haiyangw/nrpic")
SCRATCH = ROOT / "scratch" / "core"
OLD = ROOT / "runs"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WT / "cosmo" / "ic"))
sys.path.insert(0, str(WT / "analysis" / "geodesic"))

# registered runs the note reads (ids as in tracks/core/runs/)
RUN = dict(
    G="core-20261115-065452-3629622",        # regression G, merged processor build
    O="core-20261115-065901-3629622",        # regression O, merged card build, to 25 M
    FLRW="core-20261115-065903-3629622",     # regression of the homogeneous universe
    PROLATE_M8="core-20261115-152845-5728b1d",
    BIS_A="core-20261115-152842-5728b1d",    # y_c 0.66, 0.70 at M/4
    BIS_B="core-20261115-152843-5728b1d",    # y_c 0.64, 0.72 at M/4
    BIS_C="core-20261115-154726-37450f2",    # y_c 0.67, 0.69 at M/4
    BIS_CTRL="core-20261115-155617-06f844b",  # 0.605 control at M/4
    INVENTORY="core-20261121-231825-135474c",
)

PRE = dict(  # pre-program directories (verify/preprogram/README.md)
    os_sc=(OLD / "os" / "nocap_sc", "os"),
    prolate_m16=(OLD / "prolate" / "e09_v8", "prol"),
    yc0900=(OLD / "st" / "yc0900_v4", "st"),
    yc0819=(OLD / "st" / "yc0819_v4", "st"),
    yc0605=(OLD / "st" / "yc0605_v5", "st"),
    yc0500=(OLD / "st" / "yc0500_v5", "st"),
    yc0283=(OLD / "st" / "yc0283_v5", "st"),
)

_inv = None
_sums = {}


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def _inventory():
    global _inv
    if _inv is None:
        _inv = {}
        f = SCRATCH / RUN["INVENTORY"] / "inventory.json"
        for d in json.loads(f.read_text()):
            for rec in d["hashed"]:
                _inv[str(Path(d["dir"]) / rec["path"])] = rec["sha256"]
    return _inv


def _run_sums(run_dir):
    if run_dir not in _sums:
        tab = {}
        f = run_dir / "sha256sums.txt"
        if f.exists():
            for line in f.read_text().splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    tab[str((run_dir / parts[-1].lstrip("*")).resolve())] = parts[0]
        _sums[run_dir] = tab
    return _sums[run_dir]


def checked(path):
    """Return the path after comparing its sha256 with the record of its run."""
    p = Path(path).resolve()
    want = None
    if str(p).startswith(str(OLD)):
        want = _inventory().get(str(p))
    else:
        for parent in p.parents:
            if parent.parent == SCRATCH:
                want = _run_sums(parent).get(str(p))
                break
    if want is None:
        print(f"sha256 not recorded: {p}", flush=True)
    else:
        got = _sha(p)
        if got != want:
            raise SystemExit(f"sha256 MISMATCH: {p}")
        print(f"sha256 ok: {p}", flush=True)
    return p


def history(path):
    from nrp_io import read_history
    return read_history(checked(path))


def horizon(path):
    """First horizon summary: unique times, masses (finite only)."""
    p = checked(path)
    a = np.loadtxt(p, comments="#", ndmin=2)
    t, m = a[:, 1], a[:, 2]
    _, idx = np.unique(t[::-1], return_index=True)
    idx = len(t) - 1 - idx
    t, m = t[idx], m[idx]
    ok = np.isfinite(m)
    return t[ok], m[ok]


def style():
    import matplotlib
    matplotlib.use("Agg")
    import figstyle
    figstyle.use_style()
    return figstyle


def put(numbers, key, value, source, verifier="", note=""):
    numbers[key] = dict(value=value, source=source, verifier=verifier, note=note)
