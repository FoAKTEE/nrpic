"""Shared helpers of the figure and ledger scripts of Track D's working note v0.

Every number the scripts use is read from the output directory of a registered run,
/data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>/ (manifest under tracks/D-bh-dress/runs/).
A file is checked against the sha256 its run recorded in sha256sums.txt where the run wrote
one; the wave-1 runs without that file are read as they are and reported as such.
Outputs go to ../figures and ../tables next to this file unless --out DIR is given.
"""
import argparse
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
TRACK = os.path.dirname(NOTE)
SCRATCH = os.environ.get("NRPIC_D_SCRATCH", "/data/haiyangw/nrpic/scratch/D-bh-dress")

P = "D-bh-dress-20261115-"
# the registered runs the note reads (key -> run id)
RUNS = {
    "scoping": P + "120304-795eee9",        # scope calculation (turnaround, cost model)
    "scoping_lead": P + "145611-5259f48",   # lead's identical rerun
    "sym": P + "042626-f3da881",            # 48 symbolic identities of the bubble benchmark
    "sym_lead": P + "065141-5fdc744",       # lead's rerun (local-time id)
    "es_data": P + "043445-b782009",        # Einstein-Straus data set, first-run copy
    "es_checked": P + "042653-f3da881",     # the same rows, used by the checks
    "es_offline": P + "042704-f3da881",     # offline constraint check
    "es_t0_dx1": P + "043002-d51c7f2",      # AthenaK at t = 0, dx = 1 M
    "es_t0_dx05": P + "043033-4df1e76",     # AthenaK at t = 0, dx = 1/2 M
    "es_t0": P + "043406-4df1e76",          # analysis of the two t = 0 runs
    "first_run": P + "145950-23fa1c7",      # lead's first-run plan (references, cost)
    "drift8": P + "121313-284ec4f",         # vacuum puncture, M/8, 500 M (card)
    "drift16": P + "121314-284ec4f",        # vacuum puncture, M/16, 500 M (card)
    "drift_ana": P + "130954-49ed46f",      # helper's drift analysis
    "drift_lead": P + "145546-5259f48",     # lead's re-check from the raw finder output
    "tracer": P + "143918-a5c125a",         # tracer side finding (release card executable)
    "spike_ref": P + "145636-5259f48",      # probe-limit spike reference (lead's rerun)
    "spike_ref_helper": P + "123029-4df1e76",
    "spike_run": P + "123755-25227d4",      # 48000 geodesics on analytic Schwarzschild
    "spike_ana": P + "125739-a18d74d",      # stationarity analysis
    "losscone_dt": P + "124257-aa9dee7",    # loss-cone probes at two time steps
    "lc05": P + "124246-aa9dee7",           # loss-cone analysis, dt = 0.05
    "lc025": P + "124249-aa9dee7",          # loss-cone analysis, dt = 0.025
    "rd": P + "122051-bf0d6b1",             # radiation-era checks (1901.08528, 2106.07480)
    "selfsim": P + "123813-97afeea",        # self-similar solution with a seed
    "shells_ana": P + "125613-248fdaf",     # shell calculations: growth, capture, plan
    "infall_lead": P + "145610-5259f48",    # lead's closed-form re-check
    # wave 2 (note v1)
    "kerr_ref": P + "171615-8adbbdd",       # Kerr spike reference, deviations at own nodes
    "kerr_ic": P + "172335-9e5ccf9",        # Kerr initial data (48000 particles, KS slice)
    "kerr_run": P + "172611-1e40191",       # AthenaK on analytic Kerr-Schild a = 0.8, 20000 M
    "kerr_expected": P + "172646-ed6a510",  # reference grid of the binned counts
    "kerr_ana": P + "174954-786ddcc",       # stationarity analysis
    "nm128c": "D-20261115-171503-4262f03",  # Newtonian mode, dx = 1.06 M, to a/a_i = 4
    "nm64c": "D-20261115-171505-62940f4",   # Newtonian mode, dx = 2.125 M, to a/a_i = 4
    "nm128Lc": "D-20261115-171507-d1058a9", # Newtonian mode, dx = 2.75 M, to a/a_i = 8
    "nm_ana": "D-20261115-190541-e27453d",  # analysis of the three against matched shells
    "es2_data": "D-20261115-170213-d2c2131",  # bubble data with dust to 60 M, vacuum table
    "es1": "D-20261115-172726-60ba4c2",     # first bubble run, card, 1+log, M/8, 200 M
    "v1": "D-20261115-172730-c6d151b",      # its vacuum control
    "es_ana": "D-20261119-141839-8686bd7",  # analyse.py on both (es_runs entry 4)
    "es_extra": "D-20261119-142929-bb375ff",  # es_extra.py on both (entry 6)
}

CHECKED = []   # (run_id, relative path, "sha256 ok" | "no sha256sums.txt (wave-1 run)")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_dir(key):
    return os.path.join(SCRATCH, RUNS[key])


def run_file(key, rel):
    """Absolute path of output `rel` of the run named by `key`, checked against its sha256."""
    run_id = RUNS[key]
    rdir = os.path.join(SCRATCH, run_id)
    path = os.path.join(rdir, rel)
    if not os.path.isfile(path):
        raise SystemExit(f"missing output {path} of run {run_id}")
    sums = os.path.join(rdir, "sha256sums.txt")
    status = "no sha256sums.txt (wave-1 run)"
    if os.path.isfile(sums):
        table = {}
        for line in open(sums):
            parts = line.split(None, 1)
            if len(parts) == 2:
                table[parts[1].strip().lstrip("*").lstrip("./")] = parts[0]
        if rel in table:
            if table[rel] != _sha256(path):
                raise SystemExit(f"sha256 of {path} differs from the one run {run_id} recorded")
            status = "sha256 ok"
        else:
            status = "not listed in the run's sha256sums.txt"
    CHECKED.append((run_id, rel, status))
    return path


def load_json(key, rel):
    with open(run_file(key, rel)) as f:
        return json.load(f)


def out_dir(default_sub, argv=None):
    """--out DIR (for a registered run) or ../<default_sub> next to the scripts."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a, _ = ap.parse_known_args(argv)
    d = a.out or os.path.join(NOTE, default_sub)
    os.makedirs(d, exist_ok=True)
    return d


def report_checks(stem):
    seen = set()
    for run_id, rel, st in CHECKED:
        if (run_id, rel) in seen:
            continue
        seen.add((run_id, rel))
        print(f"{stem}: input {run_id}/{rel}: {st}")


def horizon_series(key):
    """(t, M_AH, S) of punc.horizon_summary_0.txt, sorted, duplicate times dropped
    (columns 1:iter 2:time 3:mass ... 7:S, written by the finder)."""
    import numpy as np
    d = np.loadtxt(run_file(key, "punc.horizon_summary_0.txt"))
    t, m, s = d[:, 1], d[:, 2], d[:, 6]
    o = np.argsort(t, kind="stable")
    t, m, s = t[o], m[o], s[o]
    keep = np.concatenate([[True], np.diff(t) > 0])
    return t[keep], m[keep], s[keep]


def running_mean(t, y, w):
    """Centred running mean over a window w; NaN where the window leaves the data."""
    import numpy as np
    out = np.full_like(y, np.nan)
    for i, ti in enumerate(t):
        if ti - w / 2 >= t[0] and ti + w / 2 <= t[-1]:
            out[i] = y[np.abs(t - ti) <= w / 2].mean()
    return out
