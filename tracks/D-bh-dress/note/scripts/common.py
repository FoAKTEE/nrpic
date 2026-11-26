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
    # wave 3 batch 3 (note v1 close): the fresh-context verifier's infall run (profile sensitivity)
    "verifier_v2": "D-20261121-031711-0d79cb3",
    # note v2 (batch 6): runs judged after gate G1
    "q16": "D-20261121-085652-7e189a2",      # Newtonian mode to a/a_i = 16 (threaded processor build)
    "q16_ana": "D-20261121-092757-34faefa",  # its analysis against matched shells and self-similar
    "q16_lost": "D-20261121-092757-3df1172", # particle census of every snapshot
    "v1b": "D-20261120-222625-63abd72",      # vacuum control with the faces at +-384 M (card)
    "hor_cmp": "D-20261121-130316-84a54d4",  # compare_horizons.py on ES-1G, V-1B, V-1
    "lead_y1": "D-20261121-154912-27e91c6",  # lead's check: V-1GB, ES-1GB, ES-1G, V-1B; Q16 points
    "gate_review": "D-20261121-165428-8440947",  # gate reviewer's own check (V-1B, Q16, D-pre-4)
    "v1gb": "D-20261121-125909-06f856e",     # V-1B with the relaxed lapse (card)
    "es1g": "D-20261119-142633-6f72922",     # bubble run with the relaxed lapse, faces +-192 M (card)
    "esf_data": "D-20261119-145022-2208a19", # ES-F data: dust down to 3 M, labels, exact growth
    "esf": "D-20261121-144631-aa7ce9b",      # ES-F: dust reaches the hole, card, 1+log, M/8, 200 M
    "esf_ana": "D-20261121-202137-7bc388e",  # esf_analyse.py (flux bracket, per label)
    "esf_crit": "D-20261121-202142-ce0f509", # esf_criteria.py ((iii), D1-D4)
    "kerr2_ic": "D-20261121-211717-7b6374b", # Kerr initial data, second sampler seed
    "kerr2_run": "D-20261121-212016-7e090f9",  # AthenaK on analytic Kerr-Schild, seed 2, 20000 M
    "kerr2_ana": "D-20261121-215955-0fb4ea2",  # its stationarity analysis (analyze_kerr.py)
    "kerr_seeds": "D-20261121-220011-d0deb0b", # pre-registered comparison of the two seeds
    "kerr_plunger": "D-20261121-220137-5123361",  # the one seed-2 particle that crossed r_+
    # note v3 (batch 25): the G2 card runs (release core-v0.6 card executable, plain 1+log, faces +-768 M;
    # every one made without <fastflow> diagnostics, decision 0041 item 4) and their registered readings
    "v1l": "D-20261121-203124-a34cf1f",      # V-1L vacuum control, M/8, 500 M
    "v1l16": "D-20261121-203151-37e7b2d",    # V-1L16 vacuum control, M/16, 300 M
    "v1l4": "D-20261123-022715-ab5d983",     # V-1L4 vacuum control, M/4, 300 M
    "esfl": "D-20261121-203150-15f2bad",     # ES-FL dust to the hole, M/8, 500 M (N)
    "ff4": "D-20261123-022727-1c17e73",      # FF4 ES-FL4, M/4 (outside the convergent regime)
    "fl16": "D-20261124-172745-72472ed",     # FL16 ES-FL16, M/16, 300 M
    "fk": "D-20261123-022725-a553496",       # FK ES-FLK, N, excision kept on, 400 M
    "fn4": "D-20261124-134157-b17938b",      # FN4 ES-FLK4N, 4N
    "fnq": "D-20261124-172725-2f426b6",      # FNQ ES-FLKQ, N/4
    "judge_long": "D-20261123-020550-f9a3482",  # criterion N at M/8 (judge_long.py)
    "judge_conv": "D-20261125-122227-3eb563a",  # null test at M/4, M/8, M/16 (judge_conv.py)
    "fp_ana": "D-20261124-172508-c847ee4",   # converged-finder re-search of the null pair (fp_analyse.py)
    "crit_esfl": "D-20261123-020614-7ba5874",  # criterion G of ES-FL
    "crit_fk": "D-20261125-115647-fd2f3f7",  # criterion G of FK
    "crit_fn4": "D-20261125-122827-c5735f8", # criterion G of FN4
    "crit_fnq": "D-20261126-054616-a13a888", # criterion G of FNQ
    "crit_ff4": "D-20261125-121123-143a007", # criterion G of FF4 with its own-mesh control
    "np_full": "D-20261126-054636-93618ee",  # particle sequence read whole (np_partial.py)
    "xq": "D-20261126-054718-afa783e",       # plane constraint norms, N/4, N, 4N (xc_plane.py)
    "region": "D-20261126-054736-10c837a",   # region shell norms, FN4 and FNQ (region_norms.py)
    "crit_fl16": "D-20261126-055158-30ae09c",  # criterion G of FL16 with its own-mesh control V-1L16
    "xl5": "D-20261126-055159-6c40115",      # plane constraint norms, ES-FL and ES-FL16 (xc_plane.py)
    "hz25": "D-20261126-055208-4e0fd0e",     # failed-search signature, FNQ and FL16 (hz_check.py)
    "conv3": "D-20261126-055249-505b079",    # three-way convergence of item C2 (conv3.py)
    "hz20": "D-20261125-160142-b1c51b5",     # failed-search signature, 13 summaries (hz_check.py)
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
