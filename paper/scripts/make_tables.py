"""Appendix tables of the runs the paper rests on, built from the run directories.

For every run that a figure or a statement of the paper rests on, this script reads the
run directory itself:

- the parameter dump at the top of the first restart file, which is what the code read
  (command-line overrides and defaults included); for a run without restart files, the
  input file copied into the run directory plus the overrides on the command line of the
  log header. The copy plus overrides is also compared with the dump, and every
  difference is recorded;
- the log headers and summaries: command line, MeshBlocks at start, first time step,
  how the run ended, wall-clock time and zone-cycles per second of every job segment;
- the particle history (central lapse, particle number, rest mass, MeshBlocks), the
  constraint history and the apparent-horizon summary;
- every restart file with its particle restart file: the refinement level of the
  MeshBlocks that hold particles gives the cell spacing in the matter;
- the particle file of the run, matched by positions and masses to the metadata file
  that the initial-data generator wrote next to its original (sampler, seed,
  perturbation), and the header of the initial-data table (model parameters).

The two test-particle campaigns on fixed black holes have hundreds of run directories;
their setups are summarised from docs/results_geodesic.md and
docs/results_cluster_test.md, and their numbers are read from the result files those
documents are generated from (problems/kerr/results/, analysis/cluster_test/results/).
Values of the original paper come from refs/arxiv_2611.12831/src/main.tex (line given in
the ledger) or are read by eye from its figures (marked "read from figure").

Writes
    paper/data/runs.json                    one record per run (machine readable)
    paper/sections/tables/tab_setups.tex    setups, one row per scenario family
    paper/sections/tables/tab_outcomes.tex  measured numbers the text points to, one float per
                                            block: tab:outcomes (test particles, horizon check),
                                            tab:outcomes_dust, tab:outcomes_prolate,
                                            tab:outcomes_clusters, tab:outcomes_migration
    paper/data/ledger.txt                   one line per number of the two tables

    python3 paper/scripts/make_tables.py [--no-slice]

--no-slice skips the Misner-Sharp masses of seven restart dumps (a few minutes) and
writes "not computed" in their place. Extrema of long cluster runs, snapshot selection and
the values read off the original's figures are imported from the figure scripts
make_data_migration.py, make_data_nearcritical.py and make_data_clusters.py, so table and
figures agree; the horizon records and black-hole positions of the cluster with two
collapsing overdensities come from make_data_overdensities.reduce_run (the same filtering
of stale and common-horizon rows as the figure).
"""
import glob
import json
import re
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(REPO / "analysis" / "diag"))
sys.path.insert(0, str(REPO / "python"))
import slicemass as sm  # noqa: E402
from common import H, read_snapshot, read_traj_tagged  # noqa: E402
from nrpic import oppenheimer_snyder as osn  # noqa: E402
sys.path.insert(0, str(HERE))
# the definitions of the figure scripts, so that table and figures use the same extrema,
# snapshot selection and read-off values of the original
from make_data_clusters import shells as cl_shells  # noqa: E402
from make_data_migration import ORIGINAL as MIG_ORIGINAL  # noqa: E402
from make_data_migration import complete_snapshots as mig_complete_snapshots  # noqa: E402
from make_data_migration import extrema as mig_extrema  # noqa: E402
from make_data_nearcritical import ORIGINAL as NC_ORIGINAL  # noqa: E402
from make_data_overdensities import MESHES as OD_MESHES  # noqa: E402
from make_data_overdensities import reduce_run as od_reduce_run  # noqa: E402
from make_data_overdensities import rst_trackers as od_rst_trackers  # noqa: E402

RUNS_DIR = REPO / "runs"
ORIG = REPO / "refs" / "arxiv_2611.12831" / "src" / "main.tex"
GEO_JSON = REPO / "problems" / "kerr" / "results" / "kerr_summary.json"
TPC_DIR = REPO / "analysis" / "cluster_test" / "results"
OUT_JSON = HERE.parent / "data" / "runs.json"
OUT_LEDGER = HERE.parent / "data" / "ledger.txt"
OUT_TAB = HERE.parent / "sections" / "tables"
CITE = r"Ref.~\cite{Wu:2026nrpic}"

# Run directories (below runs/) and the scenario families they belong to. A run may
# belong to two families (the kicked stable model is in the sequence and in the
# particle-number family).
RUNS = {
    "puncture/single_v3": ["vacuum"], "puncture/hcal/dx4": ["vacuum"],
    "puncture/hcal/dx16": ["vacuum"], "puncture/hcal/dx8_fixed": ["vacuum"],
    "puncture/hcal/dx8_tight": ["vacuum"],
    "puncture/headon_v4": ["headon"],
    "os/nocap_sc": ["dust"], "os/nocap_v4": ["dust"],
    "os/adapt_sc": ["dustcap"], "os/adapt_mc2": ["dustcap"], "os/adapt_mc1": ["dustcap"],
    **{f"st/ctl/{k}": ["filter"] for k in ("s1_nf4", "s2_nf4", "s3_nf4", "s1_nf0",
                                           "s1_nf2", "s1_nf4c", "s2_nf4c", "s3_nf4c",
                                           "s1_nf2c")},
    "st/ctl/s1_nf4c": ["filter", "osc"],      # base run of the oscillation controls
    **{f"st/osc/{k}": ["osc"] for k in ("dt2", "k1_0p1", "k1_0", "ch0p05", "ccloud",
                                        "long", "long2", "dx2b")},
    "st/yc0819_n1e3_v4": ["nnum"], "st/yc0819_n1e2_v4": ["nnum"],
    "st/yc0819_mc_n100_v4": ["nnum"], "st/yc0819_mc_n1000_v4": ["nnum"],
    "st/yc0819_mc_n10000_v4": ["nnum"],
    "st/yc0900_v4": ["stable"], "st/yc0819_v4": ["stable", "nnum"],
    "st/yc0605_v5": ["unstable"], "st/yc0500_v5": ["unstable"],
    "st/yc0283_v5": ["unstable"],
    "st/dir_yc0500_plain": ["unpert"], "st/dir_yc0500_comp": ["unpert"],
    "st/dir_yc0500_comp_s2": ["unpert"], "st/dir_yc0500_comp_s3": ["unpert"],
    "st/migration_yc0500_v4": ["unpert"],
    "st/reconf_yc0756_hc": ["nearcrit_ad"], "st/reconf_yc0756_hc_m": ["nearcrit_ad"],
    "st/yc0756_unpert": ["nearcrit_st"], "st/reconf_yc0756_v4": ["nearcrit_st"],
    "os/mc_adapt2": ["dustmc_full"], "os/mc_adapt3": ["dustmc_full"], "os/mc_nocap4": ["dustmc_lf"],
    "os/mc_adapt4": ["dustmc_lf"],
    "os/mc_nocap2": ["dustmc_runaway"], "os/mc_nocap3": ["dustmc_runaway"],
    "prolate/e09_v8": ["prolate"],
    # Collapse and merger of two overdensities inside a cluster: the run with finest cells
    # M/64 from t = 0 to 100 M on a domain of +-80 M (the figure's M/64 curves; the M/128
    # comparison n1e4_v11 + n1e4_v18 is not tabulated).
    "jeans/n1e4_v19": ["jeans"],
}
# What the paper uses each run for (statement or figure).
ROLE = {
    "puncture/single_v3": "tracers around an evolved puncture (fig_tracers); finder check at dx = M/8 (fig_horizon_check)",
    "puncture/hcal/dx4": "finder check at dx = M/4 (fig_horizon_check)",
    "puncture/hcal/dx16": "finder check at dx = M/16 (fig_horizon_check)",
    "puncture/hcal/dx8_fixed": "corrected finder in a live run (fig_horizon_check)",
    "puncture/hcal/dx8_tight": "statement: a much tighter stopping rule leaves the deficit unchanged",
    "puncture/headon_v4": "tracers around a head-on collision (statements of the evolving-black-hole subsection)",
    "os/nocap_sc": "dust collapse, finest-level clouds, corrected lattice masses (fig_dust, red)",
    "os/nocap_v4": "dust collapse, published lattice masses (fig_dust, orange)",
    "os/adapt_sc": "dust collapse, level cap without limit (fig_dust, yellow)",
    "os/adapt_mc2": "statement: two levels of coarsening match the unlimited cap",
    "os/adapt_mc1": "dust collapse, at most one level of coarsening (fig_dust, green)",
    "st/osc/long": "continuation of sample 1 (compensated) to 600 M (fig_oscillation)",
    "st/osc/long2": "continuation of sample 1 (compensated) to 1200 M (fig_oscillation)",
    "st/osc/dx2b": "half the cell spacing (no figure; listed for completeness of the oscillation controls)",
    "st/reconf_yc0756_hc": "near-critical model compressed by ten percent, consistent initial data (statement)",
    "st/reconf_yc0756_v4": "statement: the compressed particles on the unperturbed metric contract alike",
    "st/reconf_yc0756_hc_m": "near-critical model expanded by ten percent (fig_nearcritical)",
    "st/yc0756_unpert": "unperturbed near-critical model to 800 M (fig_nearcritical)",
    "st/migration_yc0500_v4": "migration of the unperturbed y_c = 0.5 model to 2500 M (fig_migration)",
    "os/mc_adapt2": "random-sample dust ball, level cap, full depth, one plain pass (statement)",
    "os/mc_adapt3": "random-sample dust ball, level cap, full depth, four passes + c (statement)",
    "os/mc_nocap4": "random-sample dust ball, published rule, one level fewer (statement)",
    "os/mc_adapt4": "random-sample dust ball, level cap, one level fewer (statement)",
    "os/mc_nocap2": "random-sample dust ball, published rule, full depth, one plain pass: block limit exceeded (statement)",
    "os/mc_nocap3": "random-sample dust ball, published rule, full depth, four passes + c: block limit exceeded (statement)",
    "prolate/e09_v8": "prolate collapse, e = 0.9, b = 10 M (fig_prolate)",
    "jeans/n1e4_v19": "two collapsing overdensities in a cluster, finest cells M/64, to 100 M (fig_overdensities, solid)",
}
for _k in RUNS:
    if _k.startswith("st/ctl/"):
        ROLE.setdefault(_k, "filter controls of the stable model (fig_filter)")
    elif _k.startswith("st/osc/"):
        ROLE.setdefault(_k, "control of the core oscillation (fig_oscillation)")
    elif _k.startswith("st/yc0819_mc") or _k in ("st/yc0819_n1e3_v4", "st/yc0819_n1e2_v4"):
        ROLE.setdefault(_k, "particle number of the stable model (fig_oscillation, statements)")
    elif _k.startswith("st/yc0"):
        ROLE.setdefault(_k, "cluster sequence with the inward kick (fig_clusters)")
    elif _k.startswith("st/dir_"):
        ROLE.setdefault(_k, "unperturbed y_c = 0.5, plain against compensated filter (fig_filter)")


def rel(p):
    return str(Path(p).resolve().relative_to(REPO))


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def truthy(s):
    return str(s).strip().lower() in ("true", "1", "yes")


# ---------------------------------------------------------------------------------------
# readers
# ---------------------------------------------------------------------------------------
def parse_input(path):
    """{(block, key): value} of an input file in the <block> key = value format."""
    par, blk = {}, None
    for line in Path(path).read_text(errors="replace").splitlines():
        line = line.split("#")[0].strip()
        if line.startswith("<"):
            blk = line.strip("<>").strip()
        elif "=" in line and blk is not None:
            k, v = [s.strip() for s in line.split("=", 1)]
            par[(blk, k)] = v
    return par


def parse_log(path):
    """Header, first step, summary and warnings of one log of the code."""
    txt = Path(path).read_text(errors="replace")
    out = {"file": rel(path)}
    m = re.search(r"start=(\S+)", txt)
    out["start"] = m.group(1) if m else None
    m = re.search(r"^# exit=(\d+) end=(\S+)", txt, re.M)
    out["exit"], out["end"] = (int(m.group(1)), m.group(2)) if m else (None, None)
    m = re.search(r"^# cmd: (.*)$", txt, re.M)
    out["mode"], out["input"], out["overrides"] = None, None, {}
    if m:
        tok = m.group(1).split()[1:]
        i = 0
        while i < len(tok):
            if tok[i] in ("-i", "-r"):
                out["mode"] = "new" if tok[i] == "-i" else "restart"
                out["input"] = rel(tok[i + 1]) if Path(tok[i + 1]).exists() else tok[i + 1]
                i += 2
            elif tok[i] in ("-d", "-t"):
                i += 2
            elif "/" in tok[i] and "=" in tok[i] and not tok[i].startswith("-"):
                k, v = tok[i].split("=", 1)
                b, key = k.split("/", 1)
                out["overrides"][(b, key)] = v
                i += 1
            else:
                i += 1
    m = re.search(r"Total number of MeshBlocks = (\d+)", txt)
    out["nmb_start"] = int(m.group(1)) if m else None
    steps = re.findall(r"elapsed=(\S+) cycle=(\d+) time=(\S+) dt=(\S+)", txt)
    if steps:
        out["first_step"] = {"cycle": int(steps[0][1]), "time": float(steps[0][2]),
                             "dt": float(steps[0][3])}
        out["last_step"] = {"elapsed": float(steps[-1][0]), "cycle": int(steps[-1][1]),
                            "time": float(steps[-1][2])}
    m = re.search(r"Terminating on (.*)", txt)
    out["termination"] = m.group(1).strip() if m else None
    for key, pat, f in (("meshblock_cycles", r"MeshBlock-cycles = (\d+)", int),
                        ("wall_s", r"cpu time used\s*=\s*(\S+)", float),
                        ("zone_cycles_per_s", r"zone-cycles/cpu_second\s*=\s*(\S+)", float),
                        ("nmb_end", r"Current number of MeshBlocks = (\d+)", int)):
        m = re.search(pat, txt)
        out[key] = f(m.group(1)) if m else None
    out["unused_params"] = re.findall(r"input parameter <(\w+)>/(\w+) = .*? was not used", txt)
    m = re.search(r"MeshBlocks in this rank on new tree = (\d+) .*? exceeds \S+ = (\d+)", txt)
    out["block_limit_exceeded"] = (int(m.group(1)), int(m.group(2))) if m else None
    m = re.search(r"NRPIC: read (\d+) particles", txt)
    out["particles_read"] = int(m.group(1)) if m else None
    return out


def current(t_raw):
    """Mask of the records of an appended time series that no later record supersedes:
    a job segment restarted from an earlier dump rewrites every time from its start on,
    so a record is kept only if all later records have larger times (as in
    paper/scripts/make_data_migration.history)."""
    t_raw = np.asarray(t_raw, dtype=float)
    later = np.r_[np.minimum.accumulate(t_raw[::-1])[::-1][1:], np.inf]
    return t_raw < later


def read_hst(path):
    """Particle history (columns H of analysis/diag/common.py) without superseded records."""
    rows = [l.split() for l in open(path) if l.strip() and not l.startswith("#")]
    ncol = max((len(r) for r in rows if len(r) in (23, 27)), default=23)
    a = np.array([r + ["nan"] * (ncol - len(r)) for r in rows if len(r) in (23, 27)], dtype=float)
    return a[current(a[:, 0])]


def read_zhst(path):
    """Constraint history as a dict of columns, without superseded records."""
    names, rows = None, []
    for line in open(path):
        if line.startswith("#"):
            if "[1]=" in line:
                names = [w.split("=", 1)[1] for w in line[1:].split() if "]=" in w]
            continue
        x = line.split()
        if names and len(x) == len(names):
            rows.append(x)
    if not rows:
        return {}
    a = np.array(rows, dtype=float)
    a = a[current(a[:, 0])]
    return {n: a[:, i] for i, n in enumerate(names)}


def read_ah(path):
    """Horizon summary rows with a finite mass: time, mass, area, rms and mean expansion,
    mean radius (as analysis/diag/common.read_horizon), without superseded searches."""
    rows = [l.split() for l in open(path) if l.strip() and not l.startswith("#")]
    rows = [r for r in rows if len(r) >= 12]
    if not rows:
        return np.zeros((0, 6))
    t = np.array([float(r[1]) for r in rows])
    out = [[float(r[1]), float(r[2]), float(r[7]), float(r[8]), float(r[9]), float(r[10])]
           for r, k in zip(rows, current(t)) if k and r[2] != "nan"]
    return np.array(out) if out else np.zeros((0, 6))


def read_prt(path):
    """Particle restart file: positions, momenta, masses and (gid, tag, species)."""
    with open(path, "rb") as f:
        if f.read(8) != b"NRPRST02":
            return None, None
        n, = struct.unpack("<q", f.read(8))
        f.read(7 * 8 + 4 * 8)
        r = np.fromfile(f, "<f8", 7 * n).reshape(n, 7)
        i = np.fromfile(f, "<i4", 3 * n).reshape(n, 3)
    return r, i


def read_nrp(path):
    with open(path, "rb") as f:
        if f.read(8) != b"NRPIC001":
            return None
        n, = struct.unpack("<q", f.read(8))
        return np.fromfile(f, "<f8", 7 * n).reshape(n, 7)


def table_header(path):
    """'# key = value' lines of an initial-data table."""
    out = {}
    if not Path(path).exists():
        return out
    for line in open(path, errors="replace"):
        if not line.startswith("#"):
            break
        m = re.match(r"^#\s*([\w.]+)\s*=\s*(\S+)\s*$", line)
        if m:
            v = m.group(2).strip("'\"")
            out[m.group(1)] = num(v) if num(v) is not None else v
    return out


_GEN = None


def generator_files():
    """Particle files that have the generator's metadata file next to them."""
    global _GEN
    if _GEN is None:
        _GEN = []
        for j in sorted(glob.glob(str(RUNS_DIR / "**" / "*.json"), recursive=True)):
            p = Path(j[:-5] + ".nrp")
            if p.exists() and not p.is_symlink():
                try:
                    meta = json.load(open(j))
                except (OSError, ValueError):
                    continue
                if "sampler" in meta:
                    _GEN.append((p, meta))
    return _GEN


def match_ic(nrp):
    """Generator metadata of the particle file: the candidate with the same number of
    particles, positions and masses whose momenta differ least (the net momentum of
    some files was removed in place after they were copied)."""
    a = read_nrp(nrp)
    if a is None:
        return None
    best = None
    for p, meta in generator_files():
        b = read_nrp(p)
        if b is None or len(b) != len(a):
            continue
        if np.array_equal(a[:, :3], b[:, :3]) and np.array_equal(a[:, 6], b[:, 6]):
            du = float(np.abs(a[:, 3:6] - b[:, 3:6]).max())
            if best is None or du < best[0]:
                best = (du, p, meta)
    if best is None:
        return None
    du, p, meta = best
    keep = ("model", "sampler", "seed", "vpert", "vpert_profile", "dpert", "yc", "n_lat",
            "lattice_h", "R0_areal", "rbar0", "lattice_surface_correction", "M_rest", "M0",
            "alpha_c", "rho_c", "zc", "R_areal", "e", "a", "b", "symmetrize")
    out = {k: meta[k] for k in keep if k in meta}
    if "table_constraint" in meta:
        out["M_ADM_of_data"] = meta["table_constraint"].get("M_ADM")
    out["generator_file"] = rel(p)
    out["max_momentum_difference"] = du
    return out


# ---------------------------------------------------------------------------------------
# one run
# ---------------------------------------------------------------------------------------
CACHE = {}          # run -> arrays not written to the json
PARAMS = {}         # run -> {(block, key): value} that the code read


def find_logs(d):
    logs = sorted(p for p in d.glob("athena.2*.log"))
    logs += sorted((d / "chain").glob("seg*.log")) if (d / "chain").is_dir() else []
    return logs


def copied_input(d, first_log):
    cands = [p for p in d.iterdir() if p.is_file() and p.suffix.startswith(".ath")]
    if (d / "chain").is_dir():
        cands += [p for p in (d / "chain").iterdir() if p.suffix.startswith(".ath")]
    if first_log and first_log.get("input"):
        name = Path(first_log["input"]).name
        same = [p for p in cands if p.name == name]
        if same:
            return same[0]
    return cands[0] if cands else None


def same_value(a, b):
    fa, fb = num(a), num(b)
    if fa is not None and fb is not None:
        return abs(fa - fb) <= 1e-12 * max(1.0, abs(fa))
    ta, tb = str(a).strip().lower(), str(b).strip().lower()
    alias = {"1": "true", "0": "false"}
    return alias.get(ta, ta) == alias.get(tb, tb)


def levels(d, base):
    """Per restart dump: time, MeshBlocks, finest mesh level, and the coarsest and
    finest level of the MeshBlocks holding particles (from the particle restart file)."""
    out = []
    for p in sorted(d.glob(f"rst/{base}.[0-9][0-9][0-9][0-9][0-9].rst")):
        h = sm.rst_open(str(p))
        if h is None:
            continue
        lev = h["lloc"][:, 3] - h["root"]
        rec = {"file": rel(p), "time": float(h["time"]), "nmb": int(h["nmb"]),
               "root_dx": (h["mesh"]["x1max"] - h["mesh"]["x1min"]) / h["mesh_nx"][0],
               "mesh_level_max": int(lev.max()), "n_particles": None}
        prt = Path(str(p) + ".prt")
        if prt.exists():
            r, i = read_prt(prt)
            if r is not None:
                rec["n_particles"] = int(len(r))
                if len(r):
                    lp = lev[i[:, 0]]
                    rec["matter_level_min"], rec["matter_level_max"] = int(lp.min()), int(lp.max())
        out.append(rec)
    return out


def collect(key):
    d = RUNS_DIR / key
    rec = {"dir": rel(d), "families": RUNS[key], "role": ROLE.get(key, "")}
    logs = [parse_log(p) for p in find_logs(d)]
    first = logs[0] if logs else {}
    rsts = sorted(d.glob("rst/*.[0-9][0-9][0-9][0-9][0-9].rst"))
    cin = copied_input(d, first)
    eff = {}
    if cin is not None:
        eff = parse_input(cin)
    eff.update(first.get("overrides", {}))
    notes = []
    if rsts:
        par = sm.rst_params(str(rsts[0]))
        rec["param_source"] = rel(rsts[0]) + " (parameter dump)"
        if first.get("mode") == "new":
            diff = [f"{b}/{k}: copied input + command line {eff[(b, k)]!r}, dump {par[(b, k)]!r}"
                    for (b, k) in eff if (b, k) in par and not same_value(eff[(b, k)], par[(b, k)])]
            if diff:
                notes.append("copied input differs from the parameter dump: " + "; ".join(diff))
    else:
        par = eff
        rec["param_source"] = (rel(cin) if cin else "none") + " + command line (no restart dump)"
    for lg in logs:
        if lg["mode"] != "new":
            continue
        missing = [f"{b}/{k} = {par.get((b, k))}" for b, k in lg["unused_params"] if cin is not None
                   and (b, k) not in parse_input(cin) and (b, k) not in lg["overrides"]]
        if missing:
            notes.append(f"{Path(lg['file']).name}: the code read {', '.join(missing)}, which "
                         f"the copied input file {cin.name} lacks (input edited after the copy)")
    rec["copied_input"] = rel(cin) if cin else None
    rec["command"] = [{"log": lg["file"], "mode": lg["mode"], "input": lg["input"],
                       "overrides": {f"{b}/{k}": v for (b, k), v in lg["overrides"].items()}}
                      for lg in logs]

    PARAMS[key] = par
    g = lambda b, k, default=None: par.get((b, k), default)  # noqa: E731
    base = g("job", "basename")
    # ---- mesh
    x1min, x1max = num(g("mesh", "x1min")), num(g("mesh", "x1max"))
    nx = [int(g("mesh", f"nx{i}")) for i in (1, 2, 3)]
    mbx = [int(g("meshblock", f"nx{i}", g("mesh", f"nx{i}"))) for i in (1, 2, 3)]
    root_dx = (x1max - x1min) / nx[0]
    refinement = g("mesh_refinement", "refinement", "none")
    regions = []
    for b in sorted({b for b, _ in par if b.startswith("refined_region")}):
        regions.append({"level": int(g(b, "level")),
                        "half_width": max(abs(num(g(b, "x1min"))), abs(num(g(b, "x1max"))))})
    lv = levels(d, base) if rsts else []
    CACHE.setdefault(key, {})["levels"] = lv
    mesh = {"domain_half_width": x1max, "symmetric": abs(x1min + x1max) < 1e-9,
            "root_cells": nx, "cells_per_meshblock": mbx, "root_dx": root_dx,
            "refinement": refinement, "num_levels": num(g("mesh_refinement", "num_levels")),
            "refined_regions": regions}
    with_p = [x for x in lv if x.get("n_particles")]
    if with_p:
        x0 = with_p[0]
        mesh["matter_dx_start"] = [root_dx / 2 ** x0["matter_level_max"], root_dx / 2 ** x0["matter_level_min"]]
        mesh["matter_dx_start_time"] = x0["time"]
        mesh["matter_dx_finest_in_dumps"] = root_dx / 2 ** max(x["matter_level_max"] for x in with_p)
    if lv:
        mesh["finest_dx_start"] = root_dx / 2 ** lv[0]["mesh_level_max"]
        mesh["finest_dx_reached"] = root_dx / 2 ** max(x["mesh_level_max"] for x in lv)
    elif refinement == "static" and regions:
        mesh["finest_dx_start"] = mesh["finest_dx_reached"] = root_dx / 2 ** max(r["level"] for r in regions)
        notes.append("no restart dump: finest spacing from the refined regions of the input")
    rec["mesh"] = mesh
    # ---- particles and deposition
    nf = int(num(g("particles", "nfilter", 0)) or 0)
    comp = truthy(g("particles", "filter_compensate", "false"))
    cc = num(g("particles", "filter_comp_c", -1)) or -1.0
    dep = truthy(g("particles", "deposit", "false"))
    adaptive = truthy(g("particles", "deposit_adaptive", "false"))
    maxc = g("particles", "deposit_max_coarsen")
    maxc = 31 if maxc is None else int(num(maxc))
    rec["particles"] = {
        "pusher": g("particles", "pusher"), "metric": g("particles", "metric"),
        "tetrad_gauge": g("particles", "triad", "symmetric"),
        "deposit": dep, "nfilter": nf, "compensation": comp,
        "compensation_c": (cc if cc >= 0 else nf / 4.0) if comp else None,
        "deposition_rule": ("none (test particles)" if not dep else
                            ("level cap: " + ("any number of levels coarser" if maxc >= 31
                                              else f"at most {maxc} level(s) coarser")
                             + f", never coarser than level {g('particles', 'deposit_min_level')}"
                             f", {g('particles', 'deposit_ppc')} particles per cell")
                            if adaptive else "cloud at the finest local level"),
        "deposit_max_coarsen": maxc if adaptive else None,
        "alpha_exc": num(g("particles", "alpha_exc")),
        "particle_file": g("particles", "particle_file"),
        "tracers": int(num(g("particles", "nparticles", 0)) or 0),
    }
    # ---- spacetime
    rec["spacetime"] = {
        "kappa1": num(g("z4c", "damp_kappa1")), "kappa2": num(g("z4c", "damp_kappa2")),
        "c_H": num(g("z4c", "damp_ch", 0)), "c_H_dx": num(g("z4c", "damp_ch_dx", 0)),
        "shift_eta": num(g("z4c", "shift_eta")), "dissipation": num(g("z4c", "diss")),
        "cfl": num(g("time", "cfl_number")), "tlim": num(g("time", "tlim")),
    }
    nh = int(num(g("fastflow", "num_horizons", 0)) or 0)
    rec["horizon_finder"] = None if nh == 0 else {
        "derivatives": g("fastflow", "metric_drvts", "stored") or "stored",
        "mass_tolerance": num(g("fastflow", "mass_tol_0")),
        "angular_points": num(g("fastflow", "ntheta")), "lmax": num(g("fastflow", "lmax")),
        "search_every_cycles": num(g("fastflow", "find_every"))}
    # ---- model
    comps = []
    ncomp = int(num(g("problem", "ncomp", 0)) or 0)
    for c in range(ncomp):
        t = g("problem", f"comp{c}_type")
        item = {"type": t}
        if t == "puncture":
            item.update(mass=num(g("problem", f"comp{c}_mass")),
                        position=[num(g("problem", f"comp{c}_x{i}", 0)) for i in (1, 2, 3)])
        elif t == "table":
            tf = d / g("problem", f"comp{c}_file")
            item["table"] = rel(tf) if tf.exists() else str(tf)
            item["header"] = table_header(tf)
        comps.append(item)
    rec["model"] = {"components": comps, "initial_lapse": g("problem", "lapse")}
    pf = g("particles", "particle_file")
    if pf:
        ic = match_ic(d / pf) if (d / pf).exists() else None
        rec["model"]["particles"] = ic or "not matched to generator metadata"
    # ---- logs
    segs = []
    for lg in logs:
        w, src = lg["wall_s"], "log summary (cpu time used)"
        if w is None and lg.get("last_step"):
            w, src = lg["last_step"]["elapsed"], "last elapsed= line (no summary: job killed or running)"
        zc = lg["zone_cycles_per_s"]
        segs.append({"log": lg["file"], "wall_s": w, "wall_source": src,
                     "zone_cycles_per_s": zc, "meshblock_cycles": lg["meshblock_cycles"],
                     "termination": lg["termination"], "exit": lg["exit"],
                     "time_reached": lg["last_step"]["time"] if lg.get("last_step") else None})
    cells_mb = mbx[0] * mbx[1] * mbx[2]
    done = [s for s in segs if s["meshblock_cycles"] and s["zone_cycles_per_s"]]
    rec["performance"] = {
        "segments": segs,
        "wall_s_total": sum(s["wall_s"] for s in segs if s["wall_s"]) if segs else None,
        "zone_cycles_per_s": (sum(s["meshblock_cycles"] * cells_mb for s in done) /
                              sum(s["meshblock_cycles"] * cells_mb / s["zone_cycles_per_s"] for s in done))
        if done else None}
    rec["dt_start"] = first.get("first_step", {}).get("dt") if first.get("mode") == "new" else None
    rec["dt_start_source"] = f"{Path(first['file']).name}, first step line" if rec["dt_start"] else \
        "run restarted from another run's dump (see that run)"
    status = "finished"
    if (d / "chain" / "STATUS").exists():
        st = (d / "chain" / "STATUS").read_text().strip()
        if st == "RUNNING":
            status = "running"
        elif (d / "chain" / "STOP").exists():
            status = "stopped by hand"
    if logs and logs[-1]["termination"] is None and status == "finished":
        status = ("killed at the job time limit (exit %s)" % logs[-1]["exit"]) if logs[-1]["exit"] else "no summary"
    elif logs and logs[-1]["termination"] and "wall" in logs[-1]["termination"] and status == "finished":
        status = "wall-clock stop"
    if logs and logs[-1].get("block_limit_exceeded"):
        status = "stopped: MeshBlock limit exceeded"
    rec["status"] = status
    rec["block_limit_exceeded"] = logs[-1].get("block_limit_exceeded") if logs else None
    rec["notes"] = notes
    # ---- histories
    hp = d / f"{base}.nrpic.hst"
    hst = read_hst(hp) if hp.exists() else None
    zp = d / f"{base}.z4c.user.hst"
    z = read_zhst(zp) if zp.exists() else {}
    ap = d / f"{base}.horizon_summary_0.txt"
    ah = read_ah(ap) if ap.exists() else np.zeros((0, 6))
    CACHE[key].update(hst=hst, z=z, ah=ah, base=base, d=d)
    out = {}
    if hst is not None:
        t, a, n = hst[:, 0], hst[:, H["alpha_probe"]], hst[:, H["np"]]
        out["t_final"] = float(t[-1])
        out["np_start"], out["np_end"] = int(n[0]), int(n[-1])
        out["nmb_start_hist"], out["nmb_max"] = int(hst[0, H["nmb"]]), int(hst[:, H["nmb"]].max())
        out["central_lapse"] = {"t0": float(a[0]), "min": float(a.min()), "t_min": float(t[a.argmin()]),
                                "max": float(a.max()), "t_max": float(t[a.argmax()]), "end": float(a[-1])}
        nex = hst[:, H["n_excised"]]
        nes = hst[:, H["n_escaped"]]
        out["n_excised_end"], out["n_escaped_end"] = int(nex[-1]), int(nes[-1])
        out["escape_times"] = [float(t[j + 1]) for j in np.nonzero(np.diff(nes))[0]]
        out["removal_first_t"] = float(t[np.argmax(nex > 0)]) if (nex > 0).any() else None
        out["all_removed_t"] = float(t[np.argmax(n == 0)]) if (n == 0).any() else None
        live = (n > 0) & (hst[:, H["sum_m"]] > 0) & (nex == 0)     # before any removal
        if live.any():
            lw = hst[live, H["sum_mw"]] / hst[live, H["sum_m"]]
            out["mean_lorentz"] = {"start": float(lw[0]), "min": float(lw.min()), "max": float(lw.max()),
                                   "end_live": float(lw[-1]), "note": "records before the first removal"}
            pm = np.sqrt(sum(hst[live, H[k]] ** 2 for k in ("sum_mux", "sum_muy", "sum_muz"))) / hst[live, H["sum_m"]]
            out["net_momentum_max"] = float(pm.max())
        out["rest_mass_start"] = float(hst[0, H["sum_m"]])
        if hst.shape[1] > H["int_e_filt"] and np.isfinite(hst[0, H["int_e_filt"]]) and dep:
            ok = live & (hst[:, H["int_e"]] > 0)
            r = hst[ok, H["int_e_filt"]] / hst[ok, H["int_e"]] - 1.0
            out["filtered_energy_change"] = {"t0": float(r[0]), "mean": float(r.mean()), "end": float(r[-1])}
    if z:
        Hn = np.sqrt(z["H-norm2"])
        out["H_norm"] = {"start": float(Hn[0]), "max": float(Hn.max()), "t_max": float(z["time"][Hn.argmax()]),
                         "end": float(Hn[-1])}
        if "dt" in z:
            out["dt_halvings"] = [float(z["time"][i]) for i in range(1, len(z["dt"]))
                                  if z["dt"][i] < 0.75 * z["dt"][i - 1]][:6]
    if nh:
        if len(ah):
            out["horizon"] = {"first_t": float(ah[0, 0]), "first_mass": float(ah[0, 1]),
                              "last_t": float(ah[-1, 0]), "last_mass": float(ah[-1, 1]), "rows": int(len(ah))}
        else:
            out["horizon"] = "none found"
    else:
        out["horizon"] = "no finder"
    rec["outcomes"] = out
    return rec


# ---------------------------------------------------------------------------------------
# table cells with their sources
# ---------------------------------------------------------------------------------------
class Cell:
    def __init__(self, tex, src=""):
        self.tex, self.src = tex, src


def detex(s):
    rep = [(r"Ref.~\cite{Wu:2026nrpic}", "Ref. [Wu and Most]"), ("~", " "), (r"\quad", ""),
           (r"\times10^{", "e"), (r"\times 10^{", "e"), ("$", ""), (r"\,", " "), ("--", "-"),
           (r"\lesssim", "<~"), (r"\le", "<="), (r"\Delta\alpha", "Delta alpha"), (r"\to", "->"), (r"\infty", "inf"), (r"\pm", "+-"), (r"\simeq", "~"),
           (r"\approx", "~"), (r"\aexc", "alpha_exc"), (r"\Egeo", "E"), (r"\Ham", "H"),
           (r"\Delta ", "Delta "), (r"\Delta", "Delta"), (r"\kappa", "kappa"), (r"\alpha", "alpha"),
           (r"\tau", "tau"), (r"\ell", "l"), (r"\rm ", ""), (r"\textit", ""), (r"\mathrm", ""),
           (r"\%", "%"), ("\\", "")]
    for a, b in rep:
        s = s.replace(a, b)
    return re.sub(r"[{}]", "", s).strip()


def sci(x, sig=2):
    if x == 0:
        return "$0$"
    e = int(np.floor(np.log10(abs(x))))
    m = x / 10 ** e
    if round(abs(m), sig - 1) >= 10:
        m, e = m / 10, e + 1
    return rf"${m:.{sig - 1}f}\times10^{{{e}}}$"


def frac(x, digits=2):
    """M/k as 1/k when x is the inverse of a power of two, else a short decimal."""
    if x >= 1 and abs(x - round(x)) < 1e-9:
        return f"{int(round(x))}"
    if x >= 10:
        return f"{x:.0f}"
    k = 1.0 / x
    if abs(k - round(k)) < 1e-9 and (int(round(k)) & (int(round(k)) - 1)) == 0:
        return f"1/{int(round(k))}"
    nd = max(0, digits - 1 - int(np.floor(np.log10(abs(x)))))
    return f"{x:.{nd}f}"


def mode_and_others(vals, fmt, sep=", "):
    """Most common value, the other values in parentheses."""
    vs = [fmt(v) for v in vals]
    order = []
    for v in vs:
        if v not in order:
            order.append(v)
    main = max(order, key=lambda v: vs.count(v))
    rest = [v for v in order if v != main]
    return main + (f" ({sep.join(rest)})" if rest else "")


def orig_line(pattern):
    for i, line in enumerate(ORIG.read_text().splitlines(), 1):
        if pattern in line:
            return i
    raise RuntimeError(f"not found in the original: {pattern!r}")


def osrc(pattern, what):
    return f"{rel(ORIG)} line {orig_line(pattern)} ({what})"


FIG = "read from figure"


def figsrc(name, what):
    return f"{rel(ORIG.parent / 'Figures' / name)}, read by eye from the rendered figure: {what}"


# ---------------------------------------------------------------------------------------
# helpers on histories
# ---------------------------------------------------------------------------------------
def lapse(key):
    h = CACHE[key]["hst"]
    return h[:, 0], h[:, H["alpha_probe"]]


def at(t, y, t0):
    return float(np.interp(t0, t, y))


def first_cross(t, y, level):
    i = np.argmax(y >= level)
    if y[i] < level:
        return None
    return float(np.interp(level, [y[i - 1], y[i]], [t[i - 1], t[i]])) if i > 0 else float(t[0])


def smooth(t, y, width, dt=0.25):
    tt = np.arange(t[0], t[-1], dt)
    yy = np.interp(tt, t, y)
    k = max(1, int(round(width / dt)))
    ys = np.convolve(yy, np.ones(k) / k, mode="same")
    s = slice(k // 2, len(tt) - k // 2)
    return tt[s], ys[s]


def zigzag(t, y, thr):
    """Alternating extrema of y whose successive differences exceed thr."""
    ext, i0, mode = [(t[0], y[0], "start")], 0, None
    hi_i = lo_i = 0
    for i in range(1, len(y)):
        if y[i] > y[hi_i]:
            hi_i = i
        if y[i] < y[lo_i]:
            lo_i = i
        if mode in (None, "up") and y[hi_i] - y[i] > thr and hi_i > i0:
            ext.append((t[hi_i], y[hi_i], "max"))
            mode, i0, lo_i = "down", hi_i, i
        elif mode in (None, "down") and y[i] - y[lo_i] > thr and lo_i > i0:
            ext.append((t[lo_i], y[lo_i], "min"))
            mode, i0, hi_i = "up", lo_i, i
    return ext


def max_diff(ka, kb, tmax):
    ta, aa = lapse(ka)
    tb, ab = lapse(kb)
    s = (ta <= min(tmax, tb[-1]))
    return float(np.abs(aa[s] - np.interp(ta[s], tb, ab)).max())


def concat(keys):
    t, a = [], []
    for k in keys:
        tk, ak = lapse(k)
        if t:
            s = tk > t[-1][-1]
            tk, ak = tk[s], ak[s]
        t.append(tk)
        a.append(ak)
    return np.concatenate(t), np.concatenate(a)


def refine_steps(key):
    """Times at which the MeshBlock count of the particle history changes."""
    h = CACHE[key]["hst"]
    n = h[:, H["nmb"]]
    return [float(h[i + 1, 0]) for i in np.nonzero(np.diff(n))[0]]


def osc_fit(key):
    """Extrema and growth of the central-lapse oscillation as analysis/diag/cluster_osc.py:
    4 M boxcar, extrema at least 15 M apart between 8 M and t_end - 4 M, half the difference
    of successive alternating extrema fitted by a straight line in time."""
    from scipy.signal import argrelextrema
    t, a = lapse(key)
    a0 = float(a[0])
    dt = float(np.median(np.diff(t)))
    n = max(3, int(round(4.0 / dt)) | 1)
    sm_ = np.convolve(a, np.ones(n) / n, mode="same")
    order = max(2, int(round(15.0 / dt)))
    ext = sorted([(i, +1) for i in argrelextrema(sm_, np.greater, order=order)[0]] +
                 [(i, -1) for i in argrelextrema(sm_, np.less, order=order)[0]])
    ext = [(i, k) for i, k in ext if 8.0 < t[i] < t[-1] - 4.0]
    te, amp, mid = [], [], []
    for (i0, k0), (i1, k1) in zip(ext[:-1], ext[1:]):
        if k0 != k1:
            te.append(t[i1])
            amp.append(0.5 * abs(sm_[i1] - sm_[i0]))
            mid.append(0.5 * (sm_[i1] + sm_[i0]) - a0)
    p = np.polyfit(te, amp, 1)
    return {"a0": a0, "ext": [(float(t[i]), float(sm_[i] - a0)) for i, _ in ext], "slope": float(p[0]),
            "icpt": float(p[1]), "mid": float(mid[-1])}


def radii(key):
    """Snapshot times and radii about the origin enclosing 10, ..., 90 percent of the rest
    mass present, from the completely written snapshots (as the figure scripts)."""
    d = RUNS_DIR / key
    files = mig_complete_snapshots(d, R[key]["outcomes"]["t_final"])
    T, Rq, Nq, Mq, _ = cl_shells(files)
    return T, Rq, Nq, Mq


def slice_mass(key, t_target):
    """Misner-Sharp mass at the outermost 2m/R = 1 of the dump nearest to t_target."""
    d = RUNS_DIR / key
    best = None
    for p in sorted(d.glob("rst/*.[0-9][0-9][0-9][0-9][0-9].rst")):
        h = sm.rst_open(str(p))
        if h is not None and (best is None or abs(h["time"] - t_target) < abs(best[0] - t_target)):
            best = (h["time"], p)
    A = sm.analyse(sm.rst_open(str(best[1]), strict=True))
    X = A["X"][sm.NPER2_H]
    return {"time": float(A["time"]), "mass": float(X["RH"] / 2), "file": rel(best[1]),
            "unc_shells": float(A["dMH_shell"]), "unc_spread": float(A["dMH_spread"])}


def finder_at(key, t0):
    ah = CACHE[key]["ah"]
    j = int(np.argmin(np.abs(ah[:, 0] - t0)))
    return float(ah[j, 0]), float(ah[j, 1]), float(ah[j, 3])


def removal_mass(key):
    """Apparent-horizon mass at the record nearest to the removal of the last particle."""
    ah, o = CACHE[key]["ah"], R[key]["outcomes"]
    j = int(np.argmin(np.abs(ah[:, 0] - o["all_removed_t"])))
    return float(ah[j, 0]), float(ah[j, 1])


# ---------------------------------------------------------------------------------------
# setups table
# ---------------------------------------------------------------------------------------
def fam(name):
    return [k for k in RUNS if name in RUNS[k]]


def runs_src(keys, what):
    return f"{', '.join(R[k]['dir'] for k in keys)}: {what}"


def per_run(keys, f):
    return "; ".join(f"{Path(k).name} {f(k)}" for k in keys)


def nf_text(k):
    p = R[k]["particles"]
    if not p["deposit"]:
        return "--"
    return f"{p['nfilter']}" + ("+c" if p["compensation"] else "")


def dep_label(k):
    p = R[k]["particles"]
    if not p["deposit"]:
        return "none"
    c = p["deposit_max_coarsen"]
    if c is None:
        return "finest level"
    return "level-capped" + (r" ($\le" + f"{c}$)" if c < 31 else "")


def dep_text(keys):
    labs = [dep_label(k) for k in keys]
    caps = sorted({R[k]["particles"]["deposit_max_coarsen"] for k in keys
                   if R[k]["particles"]["deposit_max_coarsen"] is not None})
    if all(x.startswith("level-capped") for x in labs) and len(caps) > 1:
        return "level-capped (" + ", ".join(r"$\le" + f"{c}$" if c < 31 else "any" for c in caps) + ")"
    return mode_and_others(labs, str)


def sampler_text(k):
    ic = R[k]["model"].get("particles")
    if isinstance(ic, dict):
        return {"lattice": "lattice", "stratified": "stratified", "mc": "Monte Carlo"}.get(ic["sampler"], ic["sampler"])
    if R[k]["particles"]["tracers"]:
        return "tracers"
    return "not recorded"


def n_text(n):
    e = np.log10(n) if n > 0 else 0
    return f"$10^{int(round(e))}$" if n > 1 and abs(e - round(e)) < 1e-12 else f"{n}"


def dx_cell(keys):
    """Cell spacing in the matter at the start, and the finest spacing reached."""
    vals = []
    for k in keys:
        m = R[k]["mesh"]
        if "matter_dx_start" in m and R[k]["particles"]["deposit"]:
            lo, hi = m["matter_dx_start"]
            s = frac(lo) if abs(lo - hi) < 1e-12 else f"{frac(lo)}--{frac(hi)}"
            if m["finest_dx_reached"] < min(lo, hi) - 1e-12:
                s += r"$\to$" + frac(m["finest_dx_reached"])
        else:                                   # vacuum: finest spacing (at the puncture)
            s = frac(m.get("finest_dx_reached", float("nan")))
        vals.append(s)
    return vals


def dx_of(k, level):
    """Cell spacing of a physical refinement level of run k."""
    return R[k]["mesh"]["root_dx"] / 2 ** level


def fval(x):
    """Sort key of a table text such as 1/8, 0.30->0.038, 4+c (filter passes: plain
    before compensated, then by number)."""
    m = re.match(r"^(\d+)(\+c)?$", x.strip())
    if m:
        return (1 if m.group(2) else 0) * 100 + int(m.group(1))
    m = re.match(r"\s*(\d+)/(\d+)", x)
    if m:
        return -int(m.group(1)) / int(m.group(2))
    m = re.match(r"\s*([0-9.]+)", x)
    return -float(m.group(1)) if m else 0.0


def aggregate(keys, base, varied, vals, numeric=False):
    """Text of one column of a row. All equal: the value. A column the row varies: the
    values of its runs in the order of the model column (or coarse to fine for spacings).
    Otherwise the base run's value with the values of control runs in parentheses."""
    order = []
    for k in keys:
        v = vals[k]
        if v is not None and v not in order:
            order.append(v)
    if not order:
        return "--"
    if len(order) == 1:
        return order[0]
    sep = "; " if any("," in v for v in order) else ", "
    if varied:
        order = sorted(order, key=fval) if numeric else order
        tails = {v.split(": ", 1)[1] for v in order if ": " in v}
        if len(tails) == 1 and all(": " in v and ";" not in v for v in order):
            return ", ".join(v.split(": ", 1)[0] for v in order) + ": " + tails.pop()
        return sep.join(order)
    b = vals[base]
    return b + " (" + sep.join(v for v in order if v != b) + ")"


def mesh_text(k):
    return f"{R[k]['mesh']['refinement']}, {dx_cell([k])[0]}"


def setup_rows():
    """Rows of the setups table: (name, run keys, base run, set of varied columns, model Cell)."""
    def hdr(k):
        return R[k]["model"]["components"][0].get("header", {})

    def seeds(keys):
        return sorted({R[q]["model"]["particles"]["seed"] for q in keys})
    out = []
    k = "puncture/single_v3"
    out.append(("Vacuum black hole", fam("vacuum"), k, {"mesh", "dt"}, Cell(
        f"puncture of mass $M$; {R[k]['particles']['tracers']} tracers",
        runs_src(fam("vacuum"), "parameter dump, problem/comp0_type = puncture, comp0_mass; particles/nparticles "
                                "(all five runs carry the six tracers)"))))
    k = "puncture/headon_v4"
    c = R[k]["model"]["components"]
    out.append(("Head-on collision", [k], k, set(), Cell(
        rf"punctures $M/2$ at $x=\pm{abs(c[0]['position'][0]):g}M$; {R[k]['particles']['tracers']} tracers",
        runs_src([k], f"parameter dump, problem/comp0,1: masses {c[0]['mass']}, {c[1]['mass']}, "
                      f"x = {c[0]['position'][0]}, {c[1]['position'][0]}; particles/nparticles"))))
    k = "os/nocap_sc"
    ic = R[k]["model"]["particles"]
    out.append(("Dust collapse, lattice", fam("dust"), k, set(), Cell(
        rf"$R_0={ic['R0_areal']:g}M$; $n_{{\rm lat}}={ic['n_lat']}$ ($h={ic['lattice_h']:.2f}M$); masses corrected, "
        r"published",
        runs_src(fam("dust"), f"generator metadata matched to the particle file: R0_areal = {ic['R0_areal']}, "
                              f"n_lat = {ic['n_lat']}, lattice_h = {ic['lattice_h']:.6f}, lattice_surface_correction = "
                              + per_run(fam('dust'), lambda q: str(R[q]['model']['particles'].get('lattice_surface_correction', False)))))))
    out.append(("Dust collapse, lattice, level cap", fam("dustcap"), "os/adapt_sc", {"dep"}, Cell(
        r"as above, corrected masses",
        runs_src(fam("dustcap"), "generator metadata: " + per_run(
            fam("dustcap"), lambda q: f"n_lat={R[q]['model']['particles'].get('n_lat')}, "
                                      f"lattice_surface_correction={R[q]['model']['particles'].get('lattice_surface_correction')}")))))
    keys = fam("dustmc_full")
    out.append(("Dust collapse, random sample, full depth", keys, "os/mc_adapt2", {"nf"}, Cell(
        rf"$R_0={ic['R0_areal']:g}M$; positions drawn with density $\propto\psi^6$, equal masses",
        runs_src(keys, "generator metadata matched to the particle file (runs/os/ic_mc): sampler mc, equal masses "
                       "summing to the continuum rest mass; python/nrpic/sampling.sample_os: acceptance psi^6/psi(0)^6: " +
                 per_run(keys, lambda q: f"sampler {R[q]['model']['particles']['sampler']}")))))
    keys = fam("dustmc_lf")
    out.append(("Dust collapse, random sample, one level fewer", keys, "os/mc_nocap4", {"dep"}, Cell(
        "as above",
        runs_src(keys, "same particle file as the full-depth runs: " +
                 per_run(keys, lambda q: R[q]['model']['particles']['generator_file'])))))
    k = "prolate/e09_v8"
    pic = R[k]["model"]["particles"]
    out.append(("Prolate collapse", [k], k, set(), Cell(
        rf"spheroid $e={pic['e']:g}$, $b={pic['b']:g}M$, at rest",
        runs_src([k], f"generator metadata (runs/prolate/e09_n1e4, same particles): e = {pic['e']}, a = {pic['a']:.4f}, "
                      f"b = {pic['b']}, symmetrize = {pic.get('symmetrize')}; parameter dump problem/comp0_type = spheroid"))))
    keys = fam("filter")
    sd = seeds(keys)
    out.append(("Stable cluster, filter", keys, "st/ctl/s1_nf4", {"nf"}, Cell(
        rf"$y_c={hdr(keys[0])['yc']:g}$, unperturbed; seeds {sd[0]}--{sd[-1]}",
        runs_src(keys, "initial-data table header yc; generator metadata seed and vpert: " +
                 per_run(keys, lambda q: f"seed {R[q]['model']['particles']['seed']} vpert {R[q]['model']['particles']['vpert']}")))))
    keys = fam("osc")
    out.append(("Stable cluster, oscillation", keys, "st/ctl/s1_nf4c", set(), Cell(
        rf"$y_c={hdr(keys[0])['yc']:g}$, unperturbed; seed {seeds(keys)[0]}",
        runs_src(keys, "base run runs/st/ctl/s1_nf4c and its controls; initial-data table header yc; generator metadata "
                       "seed and vpert: " +
                 per_run(keys, lambda q: f"seed {R[q]['model']['particles']['seed']} vpert {R[q]['model']['particles']['vpert']}")))))
    keys = fam("nnum")
    out.append(("Particle number", keys, "st/yc0819_v4", set(), Cell(
        rf"$y_c={hdr(keys[0])['yc']:g}$; kick 0.01 (stratified) or none (Monte Carlo)",
        runs_src(keys, "initial-data table header yc; generator metadata sampler and vpert: " +
                 per_run(keys, lambda q: f"{R[q]['model']['particles']['sampler']} vpert {R[q]['model']['particles']['vpert']}")))))
    keys = fam("stable")
    out.append(("Sequence, stable", keys, keys[0], set(), Cell(
        r"$y_c=" + ", ".join(f"{hdr(q)['yc']:.3f}" for q in keys) + r"$; kick 0.01",
        runs_src(keys, "initial-data table header yc; generator metadata vpert: " +
                 per_run(keys, lambda q: f"yc {hdr(q)['yc']} vpert {R[q]['model']['particles']['vpert']}")))))
    keys = fam("unstable")
    out.append(("Sequence, unstable", keys, keys[0], set(), Cell(
        r"$y_c=" + ", ".join(f"{hdr(q)['yc']:.3f}" for q in keys) + r"$; kick 0.01",
        runs_src(keys, "initial-data table header yc; generator metadata vpert: " +
                 per_run(keys, lambda q: f"yc {hdr(q)['yc']} vpert {R[q]['model']['particles']['vpert']}")))))
    keys = fam("unpert")
    sd = seeds(keys)
    out.append(("Unperturbed unstable", keys, "st/migration_yc0500_v4", {"nf"}, Cell(
        rf"$y_c={hdr(keys[0])['yc']:.3f}$, unperturbed; seeds {sd[0]}--{sd[-1]}",
        runs_src(keys, "initial-data table header yc; generator metadata seed, vpert: " +
                 per_run(keys, lambda q: f"seed {R[q]['model']['particles']['seed']} vpert {R[q]['model']['particles']['vpert']}")))))
    keys = fam("nearcrit_ad")
    out.append(("Near-critical, consistent data", keys, keys[0], {"mesh"}, Cell(
        rf"$y_c={hdr(keys[0])['unperturbed.yc']:.3f}$; density $\times1.1$, $\times0.9$",
        runs_src(keys, "initial-data table header unperturbed.yc; generator metadata dpert: " +
                 per_run(keys, lambda q: f"dpert {R[q]['model']['particles']['dpert']}")))))
    keys = fam("nearcrit_st")
    out.append(("Near-critical, static mesh", keys, "st/yc0756_unpert", set(), Cell(
        rf"$y_c={hdr(keys[0])['yc']:.3f}$; unperturbed, or $\times1.1$ on its metric",
        runs_src(keys, "initial-data table header yc (unperturbed table in both runs); generator metadata dpert: " +
                 per_run(keys, lambda q: f"dpert {R[q]['model']['particles']['dpert']}")))))
    jr = jeans_setup_row()
    if jr:
        out.append(jr)
    return out


def setups():
    rows = []
    geo = "docs/results_geodesic.md"
    tpc = "docs/results_cluster_test.md"
    rows.append(("Kerr geodesics", [
        Cell(r"$a=0.9M$, $a\to0$; bound, $e=0.99$, plunging", f"{geo}, Setup and sections A-C, E"),
        Cell("1", f"{geo}: single test particle per run"),
        Cell("10--12", f"{geo}, A3 and E: mesh runs on [-10,10]^2x[-5,5], [-10,10]^2x[-2,2], [-12,12]^2x[-6,6] M"),
        Cell("uniform, 1/8--1/2; lattice 0.025", f"{geo}, A3 and E (uniform meshes of 20^3 to 48^3-cell blocks, dx = 0.125, "
                                                 f"0.25, 0.5 M); C (Hermite lattice dx = 0.025 M); analytic-metric runs need no mesh"),
        Cell("0.00125--0.08", f"{geo}, Summary (convergence orders): dt = 0.08 ... 0.005 M (spherical KS), down to 0.00125 M (Cartesian KS)"),
        Cell("--", "no deposition"), Cell("--", "no deposition"), Cell("--", "no excision in the single-particle runs"),
        Cell("--", "fixed metric"),
        Cell("77.5--4550", f"{geo}, A (plunge stopped at t = 77.52 M) and B (equatorial BL orbit to 4550 M)"),
    ]))
    rows.append(("Test-particle clusters", [
        Cell(r"$a=0.9M$, $a\to0$; Gaussian cloud about $r_0=10M$, widths $0.5M$, $0.02$ in velocity",
             f"{tpc}, section 1 (initial data: sigma_x = 0.5 M, sigma_v = 0.02, centre on the orbit with turning point at r_0 = 10 M)"),
        Cell(r"$10^2$--$10^4$, Gaussian", f"{tpc}, section 1, families table"),
        Cell("64", f"{tpc}, Mesh: [-64, 64]^3"),
        Cell(r"static, 1/4$\to$1/16", f"{tpc}, Mesh: six static levels; dx = 0.25 M over the cluster, 0.0625 M at the black hole"),
        Cell("0.05", f"{tpc}, Mesh: time step dt = 0.05 M"),
        Cell("2", f"{tpc}, Mesh: nfilter = 2"),
        Cell("finest level", f"{tpc}, Mesh: deposit_max_level default (finest), deposit not fed back"),
        Cell("0.62", f"{tpc}, Mesh: alpha_exc = 0.62"),
        Cell("--", "fixed metric"),
        Cell("500--1000", f"{tpc}, Mesh: 1000 M, plunging runs 500 M"),
    ]))
    SETUP_ROWS.clear()
    for name, keys, base, varied, model in setup_rows():
        SETUP_ROWS.append((name, keys, base, varied))
        cells = [model]
        ns = sorted({R[k]["outcomes"]["np_start"] for k in keys})
        smp = []
        for k in keys:
            if sampler_text(k) not in smp:
                smp.append(sampler_text(k))
        ntx = n_text(ns[0]) if len(ns) == 1 else f"{n_text(ns[0])}--{n_text(ns[-1])}"
        cells.append(Cell(f"{ntx}, {', '.join(smp)}",
                          runs_src(keys, "particle history, np of the first record; sampler from the generator metadata "
                                         "matched to the run's particle file") + " | " +
                          per_run(keys, lambda k: f"N={R[k]['outcomes']['np_start']} {sampler_text(k)}")))
        how = f" (base run {R[base]['dir']}; parentheses: control runs; lists: the runs of the row)"
        vals = {k: frac(R[k]["mesh"]["domain_half_width"]) for k in keys}
        cells.append(Cell(aggregate(keys, base, "L" in varied, vals, True),
                          runs_src(keys, "parameter dump, mesh/x1max (x1min = -x1max)" + how) + " | " +
                          per_run(keys, lambda k: vals[k])))
        refs = {R[k]["mesh"]["refinement"] for k in keys}
        if len(refs) == 1:
            dv = {k: dx_cell([k])[0] for k in keys}
            mtxt = f"{next(iter(refs))}, " + aggregate(keys, base, "mesh" in varied, dv, "mesh" in varied and len(keys) > 2)
        else:
            dv = {k: mesh_text(k) for k in keys}
            mtxt = aggregate(keys, base, "mesh" in varied, dv)
        cells.append(Cell(mtxt,
                          runs_src(keys, "parameter dump, mesh_refinement/refinement; "
                                         "root spacing (x1max - x1min)/nx1 halved per level; levels of the MeshBlocks holding "
                                         "particles in the first restart dump and its particle restart file (gid -> block level); "
                                         "finest level of any MeshBlock over all dumps; for vacuum runs the finest level (at the puncture)"
                                   + how) + " | " + per_run(keys, lambda k: mesh_text(k))))
        vals = {k: (frac(R[k]["dt_start"]) if R[k]["dt_start"] else None) for k in keys}
        cells.append(Cell(aggregate(keys, base, "dt" in varied, vals, True),
                          runs_src(keys, "log, dt of the first step line (cycle 0); runs restarted from another run's "
                                         "dump have none" + how) + " | " +
                          per_run(keys, lambda k: f"{R[k]['dt_start']:.6g}" if R[k]['dt_start'] else "restart")))
        vals = {k: nf_text(k) for k in keys}
        cells.append(Cell(aggregate(keys, base, "nf" in varied, vals, True),
                          runs_src(keys, "parameter dump, particles/nfilter and particles/filter_compensate" + how) + " | " +
                          per_run(keys, lambda k: vals[k])))
        vals = {k: dep_label(k) for k in keys}
        caps = sorted({R[k]["particles"]["deposit_max_coarsen"] for k in keys
                       if R[k]["particles"]["deposit_max_coarsen"] is not None})
        dtx = ("level-capped (" + ", ".join(r"$\le" + f"{c}$" if c < 31 else "any" for c in caps) + ")"
               if all(v.startswith("level-capped") for v in vals.values()) and len(caps) > 1
               else aggregate(keys, base, "dep" in varied, vals))
        cells.append(Cell(dtx, runs_src(keys, "parameter dump, particles/deposit, deposit_adaptive, deposit_max_coarsen" + how)
                          + " | " + per_run(keys, lambda k: vals[k])))
        vals = {k: f"{R[k]['particles']['alpha_exc']:g}" for k in keys}
        cells.append(Cell(aggregate(keys, base, False, vals), runs_src(keys, "parameter dump, particles/alpha_exc" + how)))
        vals = {k: f"{R[k]['spacetime']['kappa1']:g}" for k in keys}
        cells.append(Cell(aggregate(keys, base, False, vals), runs_src(keys, "parameter dump, z4c/damp_kappa1" + how)
                          + " | " + per_run(keys, lambda k: vals[k])))
        tf = [R[k]["outcomes"]["t_final"] for k in keys]
        tt = f"{tf[0]:.0f}" if max(tf) - min(tf) < 0.5 else f"{min(tf):.0f}--{max(tf):.0f}"
        cells.append(Cell(tt, runs_src(keys, "particle history, time of the last record") + " | " +
                          per_run(keys, lambda k: f"{R[k]['outcomes']['t_final']:.2f} ({R[k]['status']})")))
        rows.append((name, cells))
    return rows


SETUP_ROWS = []          # (name, keys, base) of the rows built from run directories
SETUP_HEAD = ["Scenario and model", r"$N$, sampling", r"$L/M$", r"Mesh, $\Delta x/M$", r"$\Delta t/M$",
              r"$n_{\rm f}$", "Deposition", r"$\aexc$", r"$\kappa_1$", r"$t_{\rm end}/M$"]
SETUP_COLS = [0.245, 0.09, 0.05, 0.135, 0.065, 0.055, 0.085, 0.035, 0.065, 0.06]   # fractions of the text width


def footnoted(rows, head, marks):
    """Attach footnote marks in reading order (row by row, left to right; marks on the
    header first) and return the footnote texts with their sources in that order."""
    names = [r[0] for r in rows]
    order = sorted(marks, key=lambda m: (-1 if m[0] is None else names.index(m[0]), m[1]))
    notes = []
    for i, (name, ci, text, src) in enumerate(order, 1):
        if name is None:
            head[ci] += rf"\footnotemark[{i}]"
        else:
            dict(rows)[name][ci].tex += rf"\footnotemark[{i}]"
        notes.append((text, src))
    return notes


def table_lines(label, caption, head, cols, rows, notes, sep="2pt"):
    spec = "".join(rf"p{{{w}\textwidth}}" for w in cols)
    L = [r"\begin{table*}", rf"\caption{{{caption}}}", rf"\label{{{label}}}", r"\footnotesize",
         rf"\setlength{{\tabcolsep}}{{{sep}}}", r"\begin{ruledtabular}", r"\begin{tabular}{" + spec + "}",
         " & ".join(rf"\raggedright {h}" for h in head) + r" \tabularnewline", r"\colrule"]
    for name, cells in rows:
        first = rf"{name}: {cells[0].tex}" if cells[0].tex else name
        L.append(" & ".join(rf"\raggedright {c}" for c in [first] + [c.tex for c in cells[1:]]) + r" \tabularnewline")
    L += [r"\end{tabular}", r"\end{ruledtabular}",
          *[rf"\footnotetext[{i}]{{{t}}}" for i, (t, _) in enumerate(notes, 1)], r"\end{table*}", ""]
    return L


def write_setups(rows):
    kch = [k for k in fam("osc") if R[k]["spacetime"]["c_H"]]
    kcc = [k for k in fam("osc") if R[k]["particles"]["compensation_c"] not in (None, R[k]["particles"]["nfilter"] / 4)]
    ch, chdx = R[kch[0]]["spacetime"]["c_H"], R[kch[0]]["spacetime"]["c_H_dx"]
    ccv = R[kcc[0]]["particles"]["compensation_c"]
    nf = R[kcc[0]]["particles"]["nfilter"]
    extra = 12 * (ccv - nf / 4)
    col = SETUP_HEAD.index
    marks = []                         # (row or None for the header, column index, text, source)
    marks.append(("Stable cluster, oscillation", col(r"$\kappa_1$"),
                  rf"One control adds parabolic relaxation of $\Ham$ with constant $c_H={ch:g}\,M$"
                  + (r" and no $\Delta x$-proportional term." if not chdx else "."),
                  runs_src(kch, f"parameter dump, z4c/damp_ch = {ch}, z4c/damp_ch_dx = {chdx}")))
    marks.append(("Stable cluster, oscillation", col(r"$n_{\rm f}$"),
                  rf"One control uses $c=n_{{\rm f}}/4+{extra:.0f}/12$, which also cancels the cloud width.",
                  runs_src(kcc, f"parameter dump, particles/filter_comp_c = {ccv!r}")))
    kt = [k for k in fam("dustmc_full") if R[k]["status"].startswith("killed")]
    if kt:
        marks.append(("Dust collapse, random sample, full depth", col(r"$t_{\rm end}/M$"),
                      f"{['No', 'One', 'Both', 'Three'][len(kt)]} run{'s' if len(kt) > 1 else ''} stopped at the time limit of "
                      f"{'their' if len(kt) > 1 else 'its'} job, at "
                      + " and ".join(f"$t={R[k]['outcomes']['t_final']:.0f}M$" for k in kt) + ".",
                      runs_src(kt, "log ends without a summary, exit 143; particle history, time of the last record: " +
                               per_run(kt, lambda q: f"{R[q]['outcomes']['t_final']:.3f}"))))
    kr = fam("dustmc_runaway")
    if kr:
        ex = [R[k]["block_limit_exceeded"] for k in kr]
        marks.append(("Dust collapse, random sample, full depth", 0,
                      r"Finest-level clouds at the full refinement depth passed the MeshBlock limit before a horizon "
                      r"formed: " + "; ".join(
                          f"$t={R[k]['outcomes']['t_final']:.1f}M$, {e[0]} asked for, limit {e[1]} "
                          rf"($n_{{\rm f}}={nf_text(k)}$)" for k, e in zip(kr, ex)) + ".",
                      runs_src(kr, "log, fatal error 'Number of MeshBlocks ... on new tree = N ... exceeds "
                                   "max_nmb_per_rank = L'; particle history, time of the last record; parameter dump, "
                                   "nfilter and filter_compensate: " +
                               per_run(kr, lambda q: f"t {R[q]['outcomes']['t_final']:.3f}, N {R[q]['block_limit_exceeded'][0]}, "
                                                     f"L {R[q]['block_limit_exceeded'][1]}"))))
    kj = fam("jeans")
    if kj:
        k = kj[0]
        m, p_ = R[k]["mesh"], PARAMS[k]
        lev = int(num(p_[("z4c", "co_0_reflevel")]))
        marks.append(("Two overdensities", col(r"Mesh, $\Delta x/M$"),
                      rf"Root grid of ${m['root_cells'][0]}^3$ cells ($\Delta x={frac(m['root_dx'])}M$) in "
                      rf"${m['cells_per_meshblock'][0]}^3$-cell MeshBlocks; cells of $M/{1 / dx_of(k, lev):.0f}$ within "
                      rf"${num(p_[('z4c', 'co_0_radius')]):g}M$ of each puncture tracker.",
                      runs_src(kj, f"parameter dump, mesh/nx1 = {m['root_cells'][0]}, x1max = {m['domain_half_width']:g}, "
                                   f"meshblock/nx1 = {m['cells_per_meshblock'][0]}, z4c/co_0_radius = "
                                   f"{p_[('z4c', 'co_0_radius')]}, co_1_radius = {p_[('z4c', 'co_1_radius')]}, "
                                   f"co_0_reflevel = {lev}")))
        marks.append(("Two overdensities", col(r"$\aexc$"),
                      rf"Also removed: macroparticles inside ${num(p_[('particles', 'ah_exc_factor')]):g}$ of the smallest "
                      r"coordinate radius of a found apparent horizon.",
                      runs_src(kj, f"parameter dump, particles/ah_exc_factor = {p_[('particles', 'ah_exc_factor')]}; "
                                   f"athenak/src/particles/nrpic.cpp line "
                                   f"{src_line(REPO / 'athenak/src/particles/nrpic.cpp', 'ahr2[nah] = SQR(nropt.ah_exc_factor')} "
                                   f"(radius ah_exc_factor times rr_min of each found horizon, individual and common)")))
    running = [k for k in RUNS if R[k]["status"] == "running"]
    for name, keys, base, _v in SETUP_ROWS:
        kk = [k for k in keys if k in running]
        if kk:
            marks.append((name, col(r"$t_{\rm end}/M$"), r"Run in progress; values up to its last record.",
                          runs_src(kk, "chain/STATUS = RUNNING; last record of the particle history at t = " +
                                   ", ".join(f"{R[k]['outcomes']['t_final']:.2f}" for k in kk))))
    head = list(SETUP_HEAD)
    notes = footnoted(rows, head, marks)
    # the caption states the root grid of every run except the two-overdensity run, which
    # has a footnote of its own
    cells_all = {(tuple(R[k]["mesh"]["root_cells"]), tuple(R[k]["mesh"]["cells_per_meshblock"]))
                 for k in RUNS if k not in kj}
    assert cells_all == {((64, 64, 64), (16, 16, 16))}, cells_all
    assert all(tuple(R[k]["mesh"]["cells_per_meshblock"]) == (16, 16, 16) for k in kj)
    caption = (r"Setups, one row per family of runs (numerical settings in Table~\ref{tab:setups_numerics}): macroparticle "
               r"number $N$ and sampling, domain half-width $L$, mesh and cell spacing $\Delta x$ in the matter at the start and "
               r"finest reached (vacuum: at the puncture), first step $\Delta t$, filter passes $n_{\rm f}$ (+c: compensation), "
               r"deposition, excision threshold $\aexc$, constraint damping $\kappa_1$, final time. Non-uniform meshes: $64^3$ "
               r"root cells, $16^3$-cell MeshBlocks. Lists follow the model column; parentheses: control runs.")
    L = table_lines("tab:setups", caption, head, SETUP_COLS, rows, notes)
    led = []
    for name, cells in rows:
        for h, c in zip(["Model"] + SETUP_HEAD[1:], cells):
            if re.search(r"\d", detex(c.tex)):
                led.append(f"tab:setups, {name}, {detex(h)}: {detex(c.tex)} <- {c.src}")
    for i, (t, s_) in enumerate(notes, 1):
        led.append(f"tab:setups, footnote {i}: {detex(t)} <- {s_}")
    led.append("tab:setups, caption: 64^3 root cells, 16^3-cell MeshBlocks <- " +
               runs_src([k for k in RUNS if k not in kj],
                        "parameter dump, mesh/nx1..3 = 64 and meshblock/nx1..3 = 16 in every run except the "
                        "two-overdensity run, which has its own footnote (checked); docs/results_cluster_test.md, Mesh, "
                        "for the test-particle clusters"))
    L2, led2 = write_numerics(rows)
    (OUT_TAB / "tab_setups.tex").write_text("\n".join(L + L2))
    return led + led2


NUM_HEAD = ["Scenario", "Refinement", "Levels", r"Minimum resolution: $\Delta x/M$ for $|x|/M$ below",
            "MeshBlock limit", r"Finder: start $t/M$ (first radius$/M$)", "Pusher tolerance, iterations",
            r"Level cap: particles per cloud cell, coarsest cloud $\Delta x/M$"]
NUM_COLS = [0.16, 0.095, 0.045, 0.155, 0.08, 0.105, 0.09, 0.13]


def numerics_values(k):
    """Numerical settings of one run, from its parameters (dict of column -> text) and the
    source description."""
    par = PARAMS[k]
    g = lambda b, key, d=None: par.get((b, key), d)  # noqa: E731
    m = R[k]["mesh"]
    out = {}
    meth = g("z4c_amr", "method", "trivial")
    out["ref"] = {"lohner": r"L\"ohner", "tracker": "puncture tracking", "trivial": "static"}.get(meth, meth) \
        if m["refinement"] == "adaptive" else "static"
    lv = CACHE[k]["levels"]
    if m["refinement"] == "adaptive":
        out["levels"] = f"{int(num(g('mesh_refinement', 'num_levels')))}"
    elif lv:
        out["levels"] = f"{max(x['mesh_level_max'] for x in lv) + 1}"
    else:
        out["levels"] = f"{max(r['level'] for r in m['refined_regions']) + 1}"
    boxes = {}                                   # extent text -> (finest level, half-widths)
    for b in sorted({b for b, _ in par if b.startswith("refined_region")}):
        lev = int(g(b, "level"))
        x1 = [num(g(b, "x1min")), num(g(b, "x1max"))]
        x2 = [num(g(b, "x2min")), num(g(b, "x2max"))]
        x3 = [num(g(b, "x3min")), num(g(b, "x3max"))]
        if abs(x1[0] + x1[1]) > 1e-9:            # box about a puncture off the origin
            ext, hw = f"{(x1[1] - x1[0]) / 2:g} about each puncture", 0.0
        else:
            hx, hy, hz = max(map(abs, x1)), max(map(abs, x2)), max(map(abs, x3))
            ext = f"{hx:g}" if abs(hx - hz) < 1e-9 and abs(hx - hy) < 1e-9 else f"{hx:g}, {hy:g}, {hz:g}"
            hw = min(hx, hy, hz)
        if ext not in boxes or lev > boxes[ext][0]:
            boxes[ext] = (lev, hw)
    parts = {}                                   # dx text -> [extents], finest first
    for ext, (lev, hw) in sorted(boxes.items(), key=lambda e: -e[1][0]):
        parts.setdefault(lev, []).append(ext)
    if g("z4c_amr", "radius_0_rad") is not None and m["refinement"] == "adaptive":
        rr, rl = num(g("z4c_amr", "radius_0_rad")), int(num(g("z4c_amr", "radius_0_reflevel")))
        inside = any(lev == rl and hw >= rr - 1e-9 for lev, hw in boxes.values())
        if not inside:
            parts.setdefault(rl, []).append(f"$r<{rr:g}$")
    out["region"] = "; ".join(f"{frac(dx_of(k, lev))}: " + " and ".join(exts)
                              for lev, exts in sorted(parts.items(), key=lambda e: -e[0]))
    out["limit"] = f"{int(num(g('mesh_refinement', 'max_nmb_per_rank')))}"
    if R[k]["horizon_finder"]:
        out["finder"] = f"{num(g('fastflow', 'start_time_0')):g} ({num(g('fastflow', 'initial_radius_0')):g})"
    else:
        out["finder"] = "--"
    tol = num(g("particles", "tolerance"))
    e = int(np.floor(np.log10(tol) + 1e-9))
    mant = tol / 10 ** e
    out["pusher"] = (rf"$10^{{{e}}}$" if abs(mant - 1) < 1e-9 else rf"${mant:g}\times10^{{{e}}}$") + \
        f", {int(num(g('particles', 'max_iterations')))}"
    if R[k]["particles"]["deposit_max_coarsen"] is not None:
        out["cap"] = f"{num(g('particles', 'deposit_ppc')):g}, {frac(dx_of(k, int(num(g('particles', 'deposit_min_level')))))}"
    else:
        out["cap"] = "--"
    return out


def write_numerics(rows):
    """Second setups float: refinement, finder, pusher and level-cap settings per row."""
    geo = "docs/results_geodesic.md"
    tpc = "docs/results_cluster_test.md"
    nrows = [("Kerr geodesics", [Cell(""), Cell("uniform", f"{geo}, A3 and E"), Cell("1", f"{geo}, A3 and E"),
                                 Cell("--", "uniform mesh"), Cell("--", "uniform mesh"), Cell("--", "no finder"),
                                 Cell(r"$2\times10^{-14}$, 200", f"{geo}, Setup: particles/tolerance=2.0e-14 "
                                                                  "particles/max_iterations=200"),
                                 Cell("--", "no deposition")]),
             ("Test-particle clusters", [Cell(""), Cell("static", f"{tpc}, Mesh"), Cell("6", f"{tpc}, Mesh: 6 levels"),
                                         Cell("1/4: 24, 24, 8; 1/16: 2", f"{tpc}, Mesh table: level 3 dx = 0.25 M on "
                                                                         "[-24,24]^2 x [-8,8] (cluster), level 5 dx = 0.0625 M "
                                                                         "on [-2,2]^3 (black hole)"),
                                         Cell("--", f"{tpc}, Mesh: static, 1128 MeshBlocks"), Cell("--", "no finder"),
                                         Cell(r"$10^{-12}$, 100", f"{tpc}, Mesh: fixed-point tolerance 1e-12, max_iterations = 100"),
                                         Cell("--", "finest-level clouds")])]
    cols = ["ref", "levels", "region", "limit", "finder", "pusher", "cap"]
    srcs = {"ref": "parameter dump, mesh_refinement/refinement and z4c_amr/method",
            "levels": "parameter dump, mesh_refinement/num_levels (adaptive); levels present in the restart dumps (static)",
            "region": "parameter dump, refined_region<n>/level and extents (box half-widths; requested values, expanded to "
                      "whole MeshBlocks by the code) and z4c_amr/radius_0_rad with radius_0_reflevel (sphere kept at least "
                      "at that level); dx of a level = root spacing / 2^level",
            "limit": "parameter dump, mesh_refinement/max_nmb_per_rank (one rank)",
            "finder": "parameter dump, fastflow/start_time_0 and initial_radius_0",
            "pusher": "parameter dump, particles/tolerance and max_iterations",
            "cap": "parameter dump, particles/deposit_ppc and deposit_min_level (as a cell spacing)"}
    rows_varied = [(n_, v_) for n_, _, _, v_ in SETUP_ROWS]
    for name, keys, base, _v in SETUP_ROWS:
        vals = {k: numerics_values(k) for k in keys}
        cells = [Cell("")]
        rv = [r for r in rows_varied if r[0] == name][0][1]
        for c in cols:
            v = {k: vals[k][c] for k in keys}
            vary = (c in ("levels", "region") and "mesh" in rv) or (c == "cap" and "dep" in rv) or \
                   (c == "limit" and bool(rv))
            txt = aggregate(keys, base, vary, v, c in ("levels", "region"))
            cells.append(Cell(txt, runs_src(keys, srcs[c]) + " | " + per_run(keys, lambda k: v[k])))
        nrows.append((name, cells))
    # common settings as footnotes on the header
    common_keys = [k for k in RUNS if PARAMS[k].get(("z4c", "damp_kappa1")) is not None]
    def common(b, key):
        vs = sorted({PARAMS[k].get((b, key)) for k in common_keys}, key=str)
        return vs
    for b, key, want in (("z4c", "damp_kappa2", ["0.0"]), ("z4c", "shift_eta", ["2.0"]), ("z4c", "shift_Gamma", ["0.75"]),
                         ("z4c", "diss", ["0.5"]), ("z4c", "lapse_oplog", ["2.0"]), ("z4c", "lapse_advect", ["1.0"]),
                         ("z4c", "shift_advect", ["1.0"]), ("z4c", "chi_div_floor", ["1.0e-5"]), ("time", "integrator", ["rk4"]),
                         ("mesh", "nghost", ["4"])):
        assert [str(x) for x in common(b, key)] == want, (b, key, common(b, key))
    cfl = sorted({num(PARAMS[k].get(("time", "cfl_number"))) for k in common_keys})
    lk = [k for k in RUNS if PARAMS[k].get(("z4c_amr", "method")) == "lohner"]
    for b, key, want in (("z4c_amr", "lohner_refine", ["0.2"]), ("z4c_amr", "lohner_derefine", ["0.02"]),
                         ("z4c_amr", "lohner_eps", ["0.01"]), ("mesh_refinement", "ncycle_check", ["4"]),
                         ("mesh_refinement", "refinement_interval", ["8"])):
        vs = sorted({str(PARAMS[k].get((b, key))) for k in lk})
        assert vs == want, (b, key, vs)
    fk = [k for k in RUNS if R[k]["horizon_finder"]]
    fvals = {}
    for key in ("find_every", "ntheta", "lmax", "mass_tol_0", "flow_iterations_0", "flow_alpha_beta_const_0", "hmean_tol_0"):
        fvals[key] = {k: PARAMS[k].get(("fastflow", key)) for k in fk}
    fmain = {key: max(set(v.values()), key=list(v.values()).count) for key, v in fvals.items()}
    kj = fam("jeans")                  # finder settings of their own, in a footnote of their row
    fctl = sorted({k for key, v in fvals.items() for k, x in v.items() if x != fmain[key]} - set(kj))
    assert fctl == ["puncture/hcal/dx8_tight"], fctl
    kt = fctl[0]
    marks = [(None, 0, r"Every Z4c run: fourth-order Runge--Kutta steps $\Delta t=" + f"{cfl[-1]:g}" + r"\,\Delta x_{\min}$ "
                       r"(one control " + f"{cfl[0]:g}" + r"), halving whenever a finer level appears; $\kappa_2=0$; "
                       r"$1+\log$ slicing and Gamma-driver shift with advection terms, $\mu_S=3/4$, $\eta=2$; Kreiss--Oliger "
                       r"dissipation $0.5$; floor $10^{-5}$ on $\chi$; four ghost cells (two in the test-particle meshes).",
              runs_src(common_keys, "parameter dump: time/integrator rk4, time/cfl_number, z4c/damp_kappa2, lapse_oplog 2 "
                                    "(1+log), lapse_advect, shift_advect, shift_Gamma, shift_eta, diss, chi_div_floor, "
                                    "mesh/nghost, identical in every run (checked; cfl " + ", ".join(f"{c:g}" for c in cfl) +
                                    "); problems/kerr/geodesic_mesh and problems/cluster_test/cluster_mesh inputs: nghost = 2")),
             (None, 1, r"L\"ohner indicator on $q=\alpha\chi^{-7/4}$: refine above $0.2$, derefine below $0.02$, "
                       r"$\epsilon_0=0.01$, $\delta_0=10^{-99}$; checked every 4 cycles, regrids at least 8 cycles apart.",
              runs_src(lk, "parameter dump z4c_amr/lohner_refine, lohner_derefine, lohner_eps, mesh_refinement/ncycle_check, "
                           "refinement_interval (identical in every run, checked); athenak/src/z4c/z4c_amr.cpp line "
                           + str(src_line(REPO / "athenak/src/z4c/z4c_amr.cpp", "const Real delta = 1.0e-99")) +
                           " (delta) and the definition of q in the same file (alpha chi^(7/chi_psi_power), chi_psi_power = -4)")),
             (None, 5, rf"Searches every {fmain['find_every']} cycles on {fmain['ntheta']} polar points up to degree "
                       rf"{fmain['lmax']}, stopping tolerance ${sci_plain(fmain['mass_tol_0'])}$ on the mass, at most "
                       rf"{fmain['flow_iterations_0']} flow iterations, flow constant {num(fmain['flow_alpha_beta_const_0']):g}; "
                       rf"the stopping-rule control: every {fvals['find_every'][kt]} cycles, "
                       rf"${sci_plain(fvals['mass_tol_0'][kt])}$, {fvals['flow_iterations_0'][kt]} iterations.",
              runs_src(fk, "parameter dump, fastflow/find_every, ntheta, lmax, mass_tol_0, flow_iterations_0, "
                           "flow_alpha_beta_const_0 (same in every run with a finder except " + R[kt]["dir"] +
                           "".join(f" and {R[q]['dir']} (footnote of its own row)" for q in kj) + ")"))]
    for k in kj:
        p_ = PARAMS[k]
        g_ = lambda key: p_.get(("fastflow", key))  # noqa: E731
        md = num(g_("merger_distance")) * (num(p_[("z4c", "co_0_mass")]) + num(p_[("z4c", "co_1_mass")]))
        assert g_("flow_alpha_beta_const_0") == g_("flow_alpha_beta_const_1"), k
        assert len({g_(f"flow_iterations_{i}") for i in range(3)}) == 1 and len({g_(f"mass_tol_{i}") for i in range(3)}) == 1, k
        marks.append(([n_ for n_, ks, _, _ in SETUP_ROWS if k in ks][0], 5,
                      rf"Three horizons: A and B about their trackers, flow constant {num(g_('flow_alpha_beta_const_0')):g}; "
                      rf"the common horizon (first radius ${num(g_('initial_radius_2')):g}M$), flow constant "
                      rf"{num(g_('flow_alpha_beta_const_2')):g}, searched only while the trackers are closer than "
                      rf"${md:.2f}M$; every {g_('find_every')} cycles, at most {g_('flow_iterations_0')} flow iterations, "
                      rf"stopping tolerance ${sci_plain(g_('mass_tol_0'))}$ on the mass.",
                      runs_src([k], "parameter dump, fastflow/num_horizons, flow_alpha_beta_const_0..2, initial_radius_2, "
                                    "flow_iterations_0..2, mass_tol_0..2, find_every, merger_distance, "
                                    "wait_until_punc_are_close_2 = " + str(g_("wait_until_punc_are_close_2")) +
                                    "; z4c/co_0_mass + co_1_mass; athenak/src/z4c/fastflow.cpp PuncAreClose (maximal "
                                    "tracker distance < merger_distance times the sum of the tracker masses)")))
    head = list(NUM_HEAD)
    notes = footnoted(nrows, head, marks)
    caption = (r"Numerical settings of the families of Table~\ref{tab:setups}: refinement and number of levels, regions "
               r"held at least at the given cell spacing (half-widths; three numbers: $x$, $y$, $z$), MeshBlock limit, "
               r"apparent-horizon finder, pusher iteration, and the level cap of the capped runs.")
    L = table_lines("tab:setups_numerics", caption, head, NUM_COLS, nrows, notes, sep="3pt")
    led = []
    for name, cells in nrows:
        for h, c in zip(NUM_HEAD[1:], cells[1:]):
            if re.search(r"\d", detex(c.tex)):
                led.append(f"tab:setups_numerics, {name}, {detex(h)}: {detex(c.tex)} <- {c.src}")
    for i, (t, s_) in enumerate(notes, 1):
        led.append(f"tab:setups_numerics, footnote {i}: {detex(t)} <- {s_}")
    return L, led


def src_line(path, pattern):
    for i, line in enumerate(Path(path).read_text().splitlines(), 1):
        if pattern in line:
            return i
    raise RuntimeError(f"{pattern!r} not in {path}")


def sci_plain(v):
    x = num(v)
    e = int(np.floor(np.log10(x) + 1e-9))
    mant = x / 10 ** e
    return f"10^{{{e}}}" if abs(mant - 1) < 1e-9 else rf"{mant:g}\times10^{{{e}}}"


# ---------------------------------------------------------------------------------------
# outcomes table
# ---------------------------------------------------------------------------------------
def outcomes(do_slice):
    G = []          # (group title, [(quantity, Cell here, Cell original)])
    NA = Cell("--", "not given in the original")

    # ---- Kerr geodesics and test-particle clusters (campaign result files)
    geo = json.load(open(GEO_JSON))
    runs = geo["C"]["runs"]
    gsrc = rel(GEO_JSON)
    rows = [(r"Passage $e=0.99$, largest relative errors of $\Egeo$, $L_z$, $Q$ ($\Delta t=0.01M$, to $230M$):",
             Cell(""), Cell(""))]
    for name, key, olab, pat in (
            ("implicit midpoint, analytic metric", "kerr_passage/mid_ks_dt0.01",
             r"$2.8\times10^{-8}$, round-off, $1.3\times10^{-7}$", "$2.8\\times10^{-8},1.3\\times10^{-7}$ for coordinate midpoint"),
            ("spacetime Boris, symmetric gauge, analytic", "kerr_passage/bsym_ks_dt0.01",
             r"$9.0\times10^{-8}$, $1.1\times10^{-8}$, $7.8\times10^{-7}$", "$9.0\\times10^{-8},7.8\\times10^{-7}$ for DGREM--Boris"),
            ("implicit midpoint, Hermite lattice", "kerr_passage/mid_lat_dt0.01",
             r"$2.2\times10^{-6}$, $5.3\times10^{-6}$, $5.1\times10^{-5}$", "and $2.2\\times10^{-6},5.1\\times10^{-5}$ for coordinate midpoint"),
            ("spacetime Boris, Cholesky gauge, Hermite lattice", "kerr_passage/bchol_lat_dt0.01",
             r"$2.0\times10^{-6}$, $3.8\times10^{-6}$, $5.3\times10^{-5}$", "in $E,Q$ are $2.0\\times10^{-6},5.3\\times10^{-5}$ for DGREM--Boris")):
        r = runs[key]
        here = ", ".join(sci(r[q], 3) if r[q] else "$0$" for q in ("max_dE", "max_dLz", "max_dQ"))
        rows.append((rf"\quad {name}",
                     Cell(here, f"{gsrc}, C.runs['{key}']: max_dE, max_dLz, max_dQ (dt = 0.01 M, t = 230 M)"),
                     Cell(olab, osrc(pat, "text, Kerr geodesics"))))
    conv = geo["C"]["dt_convergence_ks"]
    oo = [conv[p]["order"] for p in ("mid", "bsym", "bchol")]
    rows.append((r"Passage, order of convergence in $\Delta t$ (three pushers, analytic metric)",
                 Cell(f"{min(oo):.3f}--{max(oo):.3f}", f"{gsrc}, C.dt_convergence_ks.{{mid,bsym,bchol}}.order: least-squares slope "
                                                       "of the final-position error against dt = 0.005-0.08 M"),
                 Cell("second order", osrc("Both methods are second-order accurate", "text"))))
    dxc = geo["E"]["dx_convergence"]["mid_mesh"]
    rows.append((r"Inclined Kerr orbit on the mesh, order in $h$ of position and $\Egeo$ errors",
                 Cell(f"{dxc['order']:.2f}, {dxc['order_dE']:.2f}", f"{gsrc}, E.dx_convergence.mid_mesh: order, order_dE "
                                                                   "(dx = 0.125, 0.25, 0.5 M, dt = 0.01 M, t = 600 M)"), NA))
    exc = json.load(open(TPC_DIR / "excision.json"))
    e0, e9 = exc["plunge_a0.0_mid"], exc["plunge_a0.9_mid"]
    rows.append((r"Plunging clusters ($N=10^4$): removed by excision, against exact geodesics; $a\to0$ and $a=0.9M$",
                 Cell(f"{e0['n_excised_hist']} vs {e0['n_pred_plunge']}; {e9['n_excised_hist']} vs {e9['n_pred_plunge']}",
                      f"{rel(TPC_DIR / 'excision.json')}: plunge_a0.0_mid and plunge_a0.9_mid, n_excised_hist against n_pred_plunge "
                      "(particles on plunging orbits by the exact invariants)"), NA))
    dc = json.load(open(TPC_DIR / "density_convergence.json"))
    s0, s9 = dc["a0.0"]["slope_raw_late_mean_std"], dc["a0.9"]["slope_raw_late_mean_std"]
    rows.append((r"Bound clusters, exponent of the filtered-$E$ differences against $N$; $a\to0$ and $a=0.9M$",
                 Cell(f"${s0[0]:.2f}$, ${s9[0]:.2f}$", f"{rel(TPC_DIR / 'density_convergence.json')}: a0.0 and a0.9, "
                                                    f"slope_raw_late_mean_std (mean over {s0[2]} dumps, 200-1000 M; std {s0[1]:.3f}, {s9[1]:.3f})"),
                 NA))
    G.append(("Fixed black hole", rows))

    # ---- evolving black holes
    rows = []
    k = "puncture/single_v3"
    tr = read_traj_tagged(str(RUNS_DIR / k / "punc.traj.bin"))
    dl = []
    for tag in (0, 1, 2, 3):
        q = tr[tag]
        L = q[:, 2] * q[:, 6] - q[:, 3] * q[:, 5]
        dl.append(float(np.abs(L / L[0] - 1).max()))
    rows.append((r"Puncture: largest relative change of $L_z$ of the four circular tracers",
                 Cell(f"{sci(min(dl))}--{sci(max(dl))}", f"{R[k]['dir']}, punc.traj.bin: L_z = x u_y - y u_x of tags 0-3, "
                                                        f"max |L_z/L_z(0) - 1| over 0-{tr[0][-1, 0]:.0f} M: " +
                                                        ", ".join(f"{x:.3e}" for x in dl)), NA))
    trem = [float(tr[5][-1, 0]), float(tr[4][-1, 0])]
    rows.append((r"Puncture: radial infall and plunge removed at $\aexc$, $t/M$",
                 Cell(f"{trem[0]:.0f}, {trem[1]:.0f}", f"{R[k]['dir']}, punc.traj.bin: last record of tags 5 and 4 "
                                                     f"({trem[0]:.2f}, {trem[1]:.2f} M); particle history n_excised steps at "
                                                     + ", ".join(f"{t:.2f}" for t in np.unique(CACHE[k]['hst'][np.r_[0, np.diff(CACHE[k]['hst'][:, H['n_excised']])] > 0, 0]))),
                 NA))
    if do_slice:
        S = {key: slice_mass(key, tt) for key, tt in (("puncture/hcal/dx4", 50.0), ("puncture/single_v3", 50.0),
                                                        ("puncture/hcal/dx16", 50.0), ("puncture/hcal/dx8_fixed", 12.0))}
    else:
        S = {}
    CACHE["slice"] = S

    def scell(key, digits):
        if key not in S:
            return Cell("not computed", "run without --no-slice")
        s = S[key]
        return Cell(f"{s['mass']:.{digits}f}", f"{R[key]['dir']}, {Path(s['file']).name} (t = {s['time']:.2f} M): "
                                               f"Misner-Sharp mass at the outermost 2m/R = 1 (analysis/diag/slicemass.py, "
                                               f"16 shells per factor 2); uncertainty {s['unc_shells']:.1e} (shells), "
                                               f"{s['unc_spread']:.1e} (spread of m)")
    c = scell("puncture/single_v3", 4)
    rows.append((r"Puncture ($\Delta x=M/8$), slice Misner--Sharp horizon mass at $t=50M$", c, NA))
    k = "puncture/headon_v4"
    o = R[k]["outcomes"]["horizon"]
    ah = CACHE[k]["ah"]
    rows.append((r"Head-on: first common apparent horizon $t/M$; its mass at the end",
                 Cell(f"{o['first_t']:.2f}; {o['last_mass']:.4f}", f"{R[k]['dir']}, bbh.horizon_summary_0.txt: first row with a "
                                                                f"finite mass (t = {o['first_t']}), last row (t = {o['last_t']}, "
                                                                f"rms expansion {ah[-1, 3]:.1e})"), NA))
    tr = read_traj_tagged(str(RUNS_DIR / k / "bbh.traj.bin"))
    dl, rest = [], None
    for tag, q in sorted(tr.items()):
        L = q[:, 3] * q[:, 7] - q[:, 4] * q[:, 6]
        if abs(L[0]) > 1e-12:
            dl.append(float(np.abs(L / L[0] - 1).max()))
        else:
            rest = (tag, float(np.abs(L).max()), float(q[-1, 0]))
    rows.append((r"Head-on: largest relative change of $L_x$ (five orbiting tracers); $|L_x|$ of the tracer from rest",
                 Cell(f"{sci(max(dl))}; {sci(rest[1], 1)}", f"{R[k]['dir']}, bbh.traj.bin: L_x = y u_z - z u_y per tag over 0-160 M; "
                                                            f"orbiting tags max |dL/L| = " + ", ".join(f"{x:.2e}" for x in dl) +
                                                            f"; tag {rest[0]} (L_x(0) = 0) max |L_x| until its removal at t = {rest[2]:.2f} M"),
                 NA))
    G.append(("Evolving black holes", rows))

    # ---- horizon check
    rows = []
    vals, srcs = [], []
    for key in ("puncture/hcal/dx4", "puncture/single_v3", "puncture/hcal/dx16"):
        t_, m_, e_ = finder_at(key, 50.0)
        vals.append(f"{m_:.4f}")
        srcs.append(f"{R[key]['dir']} t = {t_:g}: {m_:.6f} (rms expansion {e_:.1e})")
    rows.append((r"Finder as distributed, $t=50M$, at $\Delta x=M/4$, $M/8$, $M/16$",
                 Cell(", ".join(vals), "punc.horizon_summary_0.txt, row nearest to t = 50 M: " + "; ".join(srcs)), NA))
    cs = [scell(key, 4) for key in ("puncture/hcal/dx4", "puncture/single_v3", "puncture/hcal/dx16")]
    rows.append((r"Slice Misner--Sharp horizon mass, same slices",
                 Cell(", ".join(c.tex for c in cs), " | ".join(c.src for c in cs)), NA))
    t1, m1, _ = finder_at("puncture/hcal/dx8_tight", 50.0)
    t2, m2, _ = finder_at("puncture/single_v3", 50.0)
    k = "puncture/hcal/dx8_tight"
    rows.append((r"Finder as distributed ($M/8$), stopping tolerance $10^{-5}$ and $10^{-8}$, $t\simeq50M$",
                 Cell(f"{m2:.4f}, {m1:.4f}", f"runs/puncture/single_v3 (mass_tol {R['puncture/single_v3']['horizon_finder']['mass_tolerance']:g}) "
                                             f"t = {t2:g}: {m2:.6f}; {R[k]['dir']} (mass_tol {R[k]['horizon_finder']['mass_tolerance']:g}, "
                                             f"command-line override) t = {t1:g}: {m1:.6f}; horizon summaries, row nearest to 50 M"), NA))
    k = "puncture/hcal/dx8_fixed"
    o = R[k]["outcomes"]["horizon"]
    c = scell(k, 4)
    rows.append((r"Corrected finder in a live run ($M/8$), last search; slice mass at $t=12M$",
                 Cell(f"{o['last_mass']:.4f}; {c.tex}", f"{R[k]['dir']}, punc.horizon_summary_0.txt last row (t = {o['last_t']}, "
                                                        f"{o['last_mass']:.6f}) | {c.src}"), NA))
    G.append(("Apparent-horizon check", rows))

    # ---- dust collapse
    rows = []
    k = "os/nocap_sc"
    h = CACHE[k]["hst"]
    tau, a = h[:, H["tau_probe"]], h[:, H["alpha_probe"]]
    tc = osn.collapse_time()
    al = np.array([float(osn.staley_lower_bound(x)) if x < tc else np.nan for x in tau])
    dep_tau = {thr: float(tau[np.argmax(a - al > thr)]) for thr in (1e-3, 1e-2)}
    rows.append((r"Central proper time $\tau_c/M$ at which $\alpha_c$ exceeds the lapse bound by $10^{-2}$",
                 Cell(f"{dep_tau[1e-2]:.2f}", f"{R[k]['dir']}, os.nrpic.hst: first record with alpha_probe - (1 + 6 ln(R(tau)/R_0)) > 1e-2, "
                                              f"tau = tau_probe (python/nrpic/oppenheimer_snyder.staley_lower_bound); "
                                              f"for 1e-3: {dep_tau[1e-3]:.2f}"),
                 Cell(r"$\simeq3.5$", osrc("until $\\tau_c\\simeq3.5M$", "text"))))
    mr = osn.rest_mass()
    kp = "os/nocap_v4"
    rows.append((r"Rest mass $\sum_p m_p/M$: published lattice rule; surface-corrected (continuum $M_0$)",
                 Cell(f"{R[kp]['outcomes']['rest_mass_start']:.4f}; {R[k]['outcomes']['rest_mass_start']:.4f}",
                      f"{R[kp]['dir']} and {R[k]['dir']}, nrpic.hst sum_m of the first record; continuum M_0 = {mr:.5f} "
                      f"(python/nrpic/oppenheimer_snyder.rest_mass)"),
                 Cell(r"$\simeq1.155$ ($N\simeq10^6$)", osrc("a total particle rest mass", "text"))))
    o = R[k]["outcomes"]["horizon"]
    rows.append((r"First apparent horizon $t/M$ (finest-level clouds, corrected masses)",
                 Cell(f"{o['first_t']:.2f}", f"{R[k]['dir']}, os.horizon_summary_0.txt, first row with a finite mass"), NA))
    rows.append((r"$M_{\rm AH}/M$ at formation; at $t=60M$ (finest-level clouds, corrected masses)",
                 Cell(f"{o['first_mass']:.4f}; {o['last_mass']:.4f}", f"{R[k]['dir']}, os.horizon_summary_0.txt, first row "
                                                                    f"(t = {o['first_t']}) and last row (t = {o['last_t']})"),
                 Cell(r"$|M_{\rm AH}/M-1|\lesssim10^{-3}$ at $60M$", osrc("relative error of $\\Delta M/M_{ADM}\\lesssim 10^{-3}$", "text"))))
    o = R[kp]["outcomes"]["horizon"]
    rows.append((r"$M_{\rm AH}/M$ at formation; at $t=60M$ (published lattice masses)",
                 Cell(f"{o['first_mass']:.4f}; {o['last_mass']:.4f}", f"{R[kp]['dir']}, os.horizon_summary_0.txt, first row "
                                                                    f"(t = {o['first_t']}) and last row (t = {o['last_t']})"), NA))
    cap = [("finest level", "os/nocap_sc"), ("cap, any", "os/adapt_sc"), (r"cap, $\le2$", "os/adapt_mc2"),
           (r"cap, $\le1$", "os/adapt_mc1")]
    txt, src = [], []
    for lab, key in cap:
        tr_, mr_ = removal_mass(key)
        ml = R[key]["outcomes"]["horizon"]["last_mass"]
        txt.append(f"{mr_:.4f}$\\to${ml:.4f}")
        src.append(f"{R[key]['dir']}: horizon row nearest to the last removal (t = {tr_:g}, particles gone at "
                   f"{R[key]['outcomes']['all_removed_t']:.2f}) and last row (t = {R[key]['outcomes']['horizon']['last_t']})")
    rows.append((r"$M_{\rm AH}/M$ when the last macroparticle is removed $\to$ at $t=60M$: finest level; level cap with any, $\le2$, $\le1$ levels of coarsening",
                 Cell("; ".join(txt), "os.horizon_summary_0.txt: " + "; ".join(src)), NA))
    txt = [f"{R[key]['outcomes']['H_norm']['max']:.1f}" for _, key in cap]
    rows.append((r"Largest $\|\Ham\|$, same four runs",
                 Cell(", ".join(txt), "os.z4c.user.hst: max of sqrt(H-norm2) over the run: " +
                      "; ".join(f"{R[key]['dir']} {R[key]['outcomes']['H_norm']['max']:.3f} at t = {R[key]['outcomes']['H_norm']['t_max']:.1f}"
                                for _, key in cap)), NA))
    tref = [refine_steps(key)[1] for _, key in cap]
    txt, src = [], []
    for (_, key), t1_ in zip(cap, tref):
        z = CACHE[key]["z"]
        s = (z["time"] >= t1_) & (z["time"] < t1_ + 1.0)
        hm = float(np.sqrt(z["H-norm2"][s]).max())
        hb = float(np.sqrt(z["H-norm2"][z["time"] < t1_][-1]))
        txt.append(f"{hm:.2f}")
        src.append(f"{R[key]['dir']} refinement at t = {t1_:.2f}: {hb:.3f} before, {hm:.3f} max")
    rows.append((r"Largest $\|\Ham\|$ within $1M$ after the refinement to $\Delta x=h/4$, same four runs",
                 Cell(", ".join(txt), "os.z4c.user.hst; refinement time = second step of the MeshBlock count in os.nrpic.hst (the first, "
                                      "at t = 0.64 M, refines to h/2 and keeps the central reading exact): " + "; ".join(src)), NA))
    txt, src = [], []
    for (_, key), t1_ in zip(cap, tref):
        if key == "os/adapt_mc2":
            continue
        h = CACHE[key]["hst"]
        rho = np.array([float(osn.cycloid_rho(x)) if x < 0.99 * tc else np.nan for x in h[:, H["tau_probe"]]])
        r = h[:, H["e_probe"]] / rho
        s = (h[:, 0] >= t1_) & (h[:, 0] < t1_ + 3.0) & (h[:, H["n_excised"]] == 0)
        s0 = (h[:, 0] < t1_)
        txt.append(f"{np.nanmin(r[s]):.2f}--{np.nanmax(r[s]):.2f}")
        src.append(f"{R[key]['dir']} t = {t1_:.2f}-{t1_ + 3:.2f}: {np.nanmin(r[s]):.4f}-{np.nanmax(r[s]):.4f} "
                   f"(before the refinement: {np.nanmin(r[s0]):.4f}-{np.nanmax(r[s0]):.4f})")
    rows.append((r"Central reading of $E$ (eight central cells, after the filter) over the cycloid at the same $\tau_c$, in the "
                 r"$3M$ after the refinement to $h/4$: finest level; level cap with any, $\le1$ levels of coarsening",
                 Cell("; ".join(txt), "os.nrpic.hst e_probe divided by the cycloid density at tau_probe "
                                      "(python/nrpic/oppenheimer_snyder.cycloid_rho), records before the first removal: " + "; ".join(src)), NA))
    kp, kc_ = "os/nocap_v4", "os/nocap_sc"
    h = CACHE[kp]["hst"]
    tau, a = h[:, H["tau_probe"]], h[:, H["alpha_probe"]]
    alp = np.array([float(osn.staley_lower_bound(x)) if x < tc else np.nan for x in tau])
    dpub = float(tau[np.argmax(a - alp > 1e-2)])
    rho = np.array([float(osn.cycloid_rho(x)) if x < 0.99 * tc else np.nan for x in tau])
    r = h[:, H["e_probe"]] / rho
    t_h4 = refine_steps(kp)[1]
    s0 = h[:, 0] < t_h4
    tl = min(R[kp]["outcomes"]["all_removed_t"], R[kc_]["outcomes"]["all_removed_t"])
    da = max_diff(kp, kc_, tl)
    rows.append((r"Published lattice masses: $\tau_c/M$ at which $\alpha_c$ exceeds the lapse bound by $10^{-2}$; central "
                 r"reading of $E$ over the cycloid before the refinement to $h/4$; largest $|\Delta\alpha_c|$ from the "
                 r"corrected-mass run while macroparticles remain",
                 Cell(f"{dpub:.2f}; {np.nanmin(r[s0]):.3f}--{np.nanmax(r[s0]):.3f}; {sci(da)}",
                      f"{R[kp]['dir']}, os.nrpic.hst: first record with alpha_probe - (1 + 6 ln(R(tau)/R_0)) > 1e-2; e_probe "
                      f"over the cycloid density at tau_probe for t < {t_h4:.3f} M (second step of the MeshBlock count); alpha_probe "
                      f"against {R[kc_]['dir']} interpolated, t <= {tl:.2f} M (all particles removed): {da:.3e}"), NA))
    G.append(("Dust collapse on a lattice", rows))

    # ---- dust collapse from a random sample
    rows = []
    mc = [("os/mc_adapt2", "capped, full depth, $n_{\\rm f}=1$"), ("os/mc_adapt3", "capped, full depth, 4+c"),
          ("os/mc_nocap4", "finest level, one level fewer"), ("os/mc_adapt4", "capped, one level fewer")]
    order = (r"capped clouds at the full depth with $n_{\rm f}=1$ and 4+c; one level fewer, finest-level and capped "
             r"clouds (4+c)")
    rows.append((r"Random sample, order of the runs below: " + order, Cell(""), Cell("")))
    hz = [R[k]["outcomes"]["horizon"] for k, _ in mc]
    rows.append((r"\quad first apparent horizon $t/M$, $M_{\rm AH}/M$",
                 Cell("; ".join(f"{x['first_t']:.2f}, {x['first_mass']:.4f}" for x in hz),
                      "os.horizon_summary_0.txt, first row with a finite mass: " +
                      "; ".join(f"{R[k]['dir']} t = {x['first_t']}, {x['first_mass']:.6f}" for (k, _), x in zip(mc, hz))),
                 NA))
    txt, src = [], []
    for k, _ in mc:
        ah = CACHE[k]["ah"]
        w = [(lo, hi) for lo, hi in ((19.0, 21.0), (39.0, 41.0), (ah[-1, 0] - 2.0, ah[-1, 0] + 0.01))]
        med = []
        for lo, hi in w:
            v = ah[(ah[:, 0] >= lo) & (ah[:, 0] <= hi), 1]
            med.append((float(np.median(v)), float(v.min()), float(v.max()), len(v)))
        txt.append(f"{med[0][0]:.4f}, {med[1][0]:.4f}, {med[2][0]:.4f} ({ah[-1, 0]:.0f})")
        src.append(f"{R[k]['dir']}: " + "; ".join(f"t = {lo:.2f}-{hi:.2f}: median {m_[0]:.5f} of {m_[3]} searches "
                                                  f"(range {m_[1]:.5f}-{m_[2]:.5f})" for (lo, hi), m_ in zip(w, med)) +
                   f" (run {R[k]['status']})")
    rows.append((r"\quad $M_{\rm AH}/M$ at $t=20M$, $40M$, and over the last $2M$ (last search $t/M$); medians over "
                 r"$\pm1M$, as successive searches scatter by up to $10^{-3}$",
                 Cell("; ".join(txt), "os.horizon_summary_0.txt, median of the rows with a finite mass in each window: " +
                      "; ".join(src)), NA))
    kr = fam("dustmc_runaway")
    rows.append((r"Largest MeshBlock count: the four runs above; finest-level clouds at the full depth with "
                 r"$n_{\rm f}=1$ and 4+c, count asked for when the run stopped ($t/M$)",
                 Cell(", ".join(f"{R[k]['outcomes']['nmb_max']}" for k, _ in mc) + "; " +
                      ", ".join(f"{R[k]['block_limit_exceeded'][0]} ({R[k]['outcomes']['t_final']:.1f})" for k in kr),
                      "particle history, max of the nmb column: " +
                      "; ".join(f"{R[k]['dir']} {R[k]['outcomes']['nmb_max']}" for k, _ in mc) +
                      "; log fatal error 'MeshBlocks ... on new tree = N exceeds max_nmb_per_rank': " +
                      "; ".join(f"{R[k]['dir']} N = {R[k]['block_limit_exceeded'][0]}, limit {R[k]['block_limit_exceeded'][1]}, "
                                f"largest count held {R[k]['outcomes']['nmb_max']}, last record t = {R[k]['outcomes']['t_final']:.3f}"
                                for k in kr)),
                 NA))
    pair = ["os/mc_nocap4", "os/mc_adapt4"]
    txt, src = [], []
    for k in pair:
        z = CACHE[k]["z"]
        Hn, tz = np.sqrt(z["H-norm2"]), z["time"]
        tf = R[k]["outcomes"]["horizon"]["first_t"]
        tr_ = R[k]["outcomes"]["all_removed_t"]
        parts = [(tz < tf), (tz >= tf) & (tz < tr_), (tz >= tr_)]
        mx = [(float(Hn[q].max()), float(tz[q][Hn[q].argmax()])) for q in parts]
        txt.append(", ".join(f"{v:.2f}" for v, _ in mx))
        src.append(f"{R[k]['dir']} first horizon t = {tf}, last macroparticle removed t = {tr_:.2f}: " +
                   ", ".join(f"{v:.3f} at {tt_:.2f}" for v, tt_ in mx))
    rows.append((r"One level fewer, largest $\|\Ham\|$ before the first horizon, from it until the last macroparticle "
                 r"is removed, and afterwards: finest-level; capped clouds",
                 Cell("; ".join(txt), "os.z4c.user.hst, sqrt(H-norm2): " + "; ".join(src)), NA))
    G.append(("Dust collapse from a random sample", rows))
    G.extend(prolate_rows(do_slice))

    # ---- stable cluster: filter
    rows = []
    a0 = lapse("st/ctl/s1_nf4")[1][0]
    eq = R["st/ctl/s1_nf4"]["model"]["components"][0]["header"]["alpha_c"]

    def rise(key, tmax=130.0):
        t, a = lapse(key)
        s = t <= tmax
        i = int(np.argmax(np.where(s, a, -np.inf)))
        return float(a[i] - a[0]), float(t[i])
    order = [("st/ctl/s1_nf0", "0"), ("st/ctl/s1_nf2", "2"), ("st/ctl/s1_nf4", "4"), ("st/ctl/s1_nf2c", "2+c"),
             ("st/ctl/s1_nf4c", "4+c")]
    rr = [rise(key) for key, _ in order]
    rows.append((r"Rise of $\alpha_c$ above $\alpha_c(0)$ within $130M$, sample 1, $n_{\rm f}=0$, 2, 4, 2+c, 4+c",
                 Cell(", ".join(f"{x[0]:.4f}" for x in rr), "st.nrpic.hst: max of alpha_probe over t <= 130 M minus its value at t = 0 "
                      f"({a0:.5f}; the tabulated equilibrium has {eq:.5f}): " +
                      "; ".join(f"{R[key]['dir']} {x[0]:.4f} at t = {x[1]:.0f}" for (key, _), x in zip(order, rr))),
                 Cell(r"$\approx0.01$ (kicked model; " + FIG + ")", figsrc("st_dynamics.pdf", "y_c = 0.819 lapse panel, broad rise of about 0.01 "
                                                                                "near t = 150-250 M on an axis 0-1 (this run has the inward kick)"))))
    rs = [rise(f"st/ctl/s{i}_nf4") for i in (1, 2, 3)]
    rc = [rise(f"st/ctl/s{i}_nf4c") for i in (1, 2, 3)]
    rows.append((r"Same rise, samples 1--3, four plain passes; with compensation",
                 Cell(", ".join(f"{x[0]:.4f}" for x in rs) + "; " + ", ".join(f"{x[0]:.4f}" for x in rc),
                      "st.nrpic.hst as above: " + "; ".join(f"s{i}_nf4 {x[0]:.4f} at {x[1]:.0f} M" for i, x in enumerate(rs, 1)) +
                      "; " + "; ".join(f"s{i}_nf4c {x[0]:.4f} at {x[1]:.0f} M" for i, x in enumerate(rc, 1))), NA))
    fe = [(key, R[key]["outcomes"]["filtered_energy_change"]["mean"]) for key in ("st/ctl/s1_nf4", "st/ctl/s1_nf4c")]
    rows.append((r"Filtered over deposited proper-volume integral of $E$, minus one: four plain passes; with compensation",
                 Cell(f"{sci(fe[0][1])}; {sci(fe[1][1])}", "st.nrpic.hst int_E_filtered/int_E - 1, mean over the run: " +
                      "; ".join(f"{R[key]['dir']} mean {v:.3e}, end {R[key]['outcomes']['filtered_energy_change']['end']:.3e}"
                                for key, v in fe)), NA))
    hn = [(key, R[key]["outcomes"]["H_norm"]["end"]) for key in ("st/ctl/s1_nf0", "st/ctl/s1_nf4", "st/ctl/s1_nf4c")]
    rows.append((r"$\|\Ham\|$ at $t=300M$: no filter; four plain passes; with compensation",
                 Cell("; ".join(f"{v:.3f}" for _, v in hn), "st.z4c.user.hst sqrt(H-norm2) of the last record: " +
                      "; ".join(f"{R[key]['dir']} {v:.4f}" for key, v in hn)), NA))
    txt, src = [], []
    for key in ("st/ctl/s1_nf4", "st/ctl/s1_nf4c"):
        T, Rq, _, _ = radii(key)
        s5 = T <= 300.0
        g50, g90 = float(Rq[s5, 4].max() / Rq[0, 4]), float(Rq[s5, 8].max() / Rq[0, 8])
        h = CACHE[key]["hst"]
        tt, ee = smooth(h[:, 0], h[:, H["e_probe"]], 20.0)
        e0 = float(ee[0])
        emin = float(ee.min())
        txt.append(f"{g50:.2f}, {g90:.2f}, {emin / e0:.2f}")
        src.append(f"{R[key]['dir']}: radii about the origin enclosing 50 and 90 percent of the rest mass from the particle "
                   f"snapshots ({len(T)} times, paper/scripts/make_data_clusters.shells), largest over the initial value "
                   f"{g50:.4f}, {g90:.4f} (initial {Rq[0, 4]:.3f}, {Rq[0, 8]:.3f} M); e_probe (central E) in 20 M boxcar "
                   f"means, lowest {emin:.4e} at {tt[ee.argmin()]:.0f} M over the first mean {e0:.4e}")
    rows.append((r"Sample 1, four plain passes; with compensation: largest radius enclosing 50 and 90 percent of the rest mass "
                 r"over its initial value; lowest central $E$ ($20M$ means) over its first value",
                 Cell("; ".join(txt), "; ".join(src)), NA))
    G.append((r"Stable cluster $y_c=0.819$: filter", rows))

    # ---- core oscillation
    rows = []
    base = ["st/ctl/s1_nf4c", "st/osc/long", "st/osc/long2"]
    t, a = concat(base)
    ts, as_ = smooth(t, a, 4.0)
    tt, trend = smooth(ts, as_, 150.0)
    sig = as_[(ts >= tt[0]) & (ts <= tt[-1])][: len(tt)] - trend
    s = (tt >= 100) & (tt <= t[-1])
    x = sig[s] - sig[s].mean()
    nfft = 1 << 18
    f = np.fft.rfftfreq(nfft, d=0.25)
    P = np.abs(np.fft.rfft(x * np.hanning(len(x)), nfft)) ** 2
    band = (f > 1 / 200) & (f < 1 / 30)
    period = float(1 / f[band][np.argmax(P[band])])
    rho_c = R["st/ctl/s1_nf4c"]["model"]["components"][0]["header"]["rho_c"]
    tcore = float(np.pi * np.sqrt(3 / (4 * np.pi * rho_c)))
    rows.append((r"Period of $\alpha_c$ ($100$--$1200M$); radial period in the core, $\pi[3/(4\pi E_c)]^{1/2}$",
                 Cell(f"{period:.0f}; {tcore:.0f}", f"{', '.join(R[q]['dir'] for q in base)}, st.nrpic.hst alpha_probe joined in time, "
                                                   f"4 M boxcar, 150 M running mean removed, peak of the periodogram (Hann window) "
                                                   f"between 30 and 200 M: {period:.1f} M; E_c = rho_c = {rho_c:.4e} from the "
                                                   f"initial-data table header: {tcore:.1f} M"), NA))
    sw = []
    for w0 in range(100, int(t[-1]) - 99, 100):
        s = (ts >= w0) & (ts < w0 + 100)
        sw.append((w0, 0.5 * float(as_[s].max() - as_[s].min())))
    sat = [v for w0, v in sw if w0 >= 500]
    rows.append((r"Half the swing of $\alpha_c$ in windows of $100M$: growth phase ($100$--$500M$); after $500M$",
                 Cell(f"{sw[0][1]:.3f}$\\to${max(v for w0, v in sw if w0 < 500):.3f}; {min(sat):.3f}--{max(sat):.3f}",
                      "same joined series, 4 M boxcar, half of max - min per window: " +
                      ", ".join(f"{w0}: {v:.4f}" for w0, v in sw)), NA))
    ctl = [("st/osc/dt2", r"$\Delta t/2$"), ("st/osc/k1_0p1", r"$\kappa_1=0.1$"), ("st/osc/k1_0", r"$\kappa_1=0$"),
           ("st/osc/ch0p05", r"$c_H$")]
    dd = [max_diff(key, "st/ctl/s1_nf4c", 300.0) for key, _ in ctl]
    rows.append((r"Largest $|\Delta\alpha_c|$ from sample 1 over $300M$: $\Delta t/2$, $\kappa_1=0.1$, $\kappa_1=0$, $c_H$",
                 Cell(", ".join(sci(v) for v in dd), "st.nrpic.hst alpha_probe of each control minus that of runs/st/ctl/s1_nf4c "
                      "interpolated to the control's records: " + "; ".join(f"{R[key]['dir']} {v:.2e}" for (key, _), v in zip(ctl, dd))), NA))
    v = max_diff("st/osc/ccloud", "st/ctl/s1_nf4c", 300.0)
    rows.append((r"Same, compensation that also cancels the cloud width",
                 Cell(sci(v), f"{R['st/osc/ccloud']['dir']}, st.nrpic.hst against runs/st/ctl/s1_nf4c as above: {v:.3e}"), NA))
    T, Rq = [], []
    for key in base:
        T_, R_, _, _ = radii(key)
        keep = T_ > (T[-1][-1] if T else -1.0)
        T.append(T_[keep])
        Rq.append(R_[keep])
    T, Rq = np.concatenate(T), np.concatenate(Rq)
    win = [(0.0, 300.0), (300.0, T[-1])]
    sw = []
    for lo, hi in win:
        q_ = (T >= lo) & (T <= hi)
        sw.append(((Rq[q_, 0].max() - Rq[q_, 0].min()) / Rq[0, 0], (Rq[q_, 8].max() - Rq[q_, 8].min()) / Rq[0, 8],
                   Rq[q_, 0].min(), Rq[q_, 0].max(), Rq[q_, 8].min(), Rq[q_, 8].max()))
    rows.append((r"Sample 1: range of the radius enclosing 10 and of that enclosing 90 percent of the rest mass over its "
                 r"initial value, $0$--$300M$; $300$--$1200M$",
                 Cell("; ".join(f"{x[0]:.2f}, {x[1]:.2f}" for x in sw),
                      f"{', '.join(R[q]['dir'] for q in base)}, particle snapshots joined in time ({len(T)} times, "
                      f"{T[0]:g}-{T[-1]:g} M), radii about the origin (paper/scripts/make_data_clusters.shells), initial r10 "
                      f"{Rq[0, 0]:.3f}, r90 {Rq[0, 8]:.3f} M: " +
                      "; ".join(f"t = {lo:g}-{hi:g} M: r10 {x[2]:.3f}-{x[3]:.3f}, r90 {x[4]:.3f}-{x[5]:.3f}"
                                for (lo, hi), x in zip(win, sw))), NA))
    oa = {key: osc_fit(key) for key in ("st/ctl/s1_nf4c", "st/osc/dx2b")}
    def ofx(x):
        first = x["ext"][0]
        last = x["ext"][-1]
        return first, last
    txt, src = [], []
    for key in ("st/ctl/s1_nf4c", "st/osc/dx2b"):
        x = oa[key]
        (t1, v1), (t2, v2) = x["ext"][0], x["ext"][-1]
        txt.append(f"${v1:+.4f}$ ({t1:.0f}), {sci(x['slope'])}, ${v2:+.4f}$ ({t2:.0f}), ${x['mid']:+.4f}$")
        src.append(f"{R[key]['dir']}: extrema of the 4 M boxcar (at least 15 M apart, 8 M < t < t_end - 4 M) minus "
                   f"alpha_c(0) = {x['a0']:.5f}: " + ", ".join(f"{tt_:.0f}: {vv:+.4f}" for tt_, vv in x["ext"]) +
                   f"; straight-line fit of half the difference of successive extrema against time: {x['icpt']:.4f} + "
                   f"{x['slope']:.3e} t; mean of the last two extrema {x['mid']:+.4f} (as analysis/diag/cluster_osc.py)")
    rows.append((r"Half the cell spacing over the cluster against sample 1 (to $300M$): first maximum of "
                 r"$\alpha_c-\alpha_c(0)$ ($t/M$), growth rate of the half-swing per $M$, last minimum ($t/M$), mean of the last "
                 r"two extrema; sample 1 first",
                 Cell("; ".join(txt), "; ".join(src)), NA))
    rho_n = R["st/reconf_yc0756_hc"]["model"]["components"][0]["header"]["unperturbed.rho_c"]
    tn = float(np.pi * np.sqrt(3 / (4 * np.pi * rho_n)))
    rows.append((r"Near-critical $y_c=0.756$ in " + CITE + r": period of $\alpha_c$; here the core radial period of that model",
                 Cell(f"{tn:.0f}", f"{R['st/reconf_yc0756_hc']['dir']}/cluster.tab header unperturbed.rho_c = {rho_n:.4e}: "
                                   f"pi (3/(4 pi rho_c))^(1/2) = {tn:.1f} M"),
                 Cell(r"$\approx50$ (" + FIG + ")", figsrc("migration_lapse_redshift_shells.pdf",
                                                         "panel (a), about six lapse maxima in the first 300 M"))))
    G.append((r"Stable cluster $y_c=0.819$: core oscillation", rows))

    # ---- particle number
    rows = []
    k4, k3 = "st/yc0819_mc_n10000_v4", "st/yc0819_mc_n1000_v4"
    sm4, sm3 = smooth(*lapse(k4), 4.0), smooth(*lapse(k3), 4.0)
    a04, a03 = lapse(k4)[1][0], lapse(k3)[1][0]
    s = sm4[0] <= 190
    d13 = float(np.abs((sm4[1][s] - a04) - (np.interp(sm4[0][s], *sm3) - a03)).max())
    lo4 = float((sm4[1][sm4[0] > 190] - a04).min())
    lo3 = float((sm3[1][sm3[0] > 190] - a03).min())
    m4 = float((sm4[1][sm4[0] > 400] - a04).mean())
    m3 = float((sm3[1][sm3[0] > 400] - a03).mean())
    rows.append((r"Monte Carlo, $N=10^3$ against $10^4$: largest difference of $\alpha_c-\alpha_c(0)$ to $190M$; "
                 r"lowest $\alpha_c-\alpha_c(0)$ after $190M$ ($10^4$, $10^3$); mean over $400$--$500M$ ($10^4$, $10^3$)",
                 Cell(f"{d13:.3f}; ${lo4:.3f}$, ${lo3:.3f}$; ${m4:.3f}$, ${m3:.3f}$",
                      f"{R[k4]['dir']} and {R[k3]['dir']}, st.nrpic.hst alpha_probe minus its first value "
                      f"({a04:.5f}, {a03:.5f}), 4 M boxcar: max |difference| for t <= 190 M {d13:.4f}; min for t > 190 M "
                      f"{lo4:.4f}, {lo3:.4f}; mean for t > 400 M {m4:.4f}, {m3:.4f}"), NA))
    key = "st/yc0819_mc_n100_v4"
    t, a = lapse(key)
    o = R[key]["outcomes"]
    rows.append((r"Monte Carlo $N=10^2$: $\alpha_c$ at $t=0$, $200M$, $500M$; mean Lorentz factor at start and end; largest $|\sum_p m_p u_{i,p}|/M_0$",
                 Cell(f"{a[0]:.2f}, {at(t, a, 200):.2f}, {at(t, a, 500):.2f}; {o['mean_lorentz']['start']:.3f}, "
                      f"{o['mean_lorentz']['end_live']:.3f}; {o['net_momentum_max']:.3f}",
                      f"{R[key]['dir']}, st.nrpic.hst: alpha_probe interpolated at 0, 200, 500 M; sum_mW/sum_m first and last "
                      f"record; max over records of |(sum_mux, sum_muy, sum_muz)|/sum_m"), NA))
    G.append((r"Stable cluster $y_c=0.819$: particle number", rows))

    # ---- cluster sequence
    rows = []
    st = ["st/yc0900_v4", "st/yc0819_v4"]
    rows.append((r"$\alpha_c$ range over $300M$, $y_c=0.900$; $0.819$; particles kept",
                 Cell("; ".join(f"{R[q]['outcomes']['central_lapse']['min']:.3f}--{R[q]['outcomes']['central_lapse']['max']:.3f}" for q in st) +
                      "; " + ("all" if all(R[q]['outcomes']['np_end'] == R[q]['outcomes']['np_start'] for q in st) else "not all"),
                      "st.nrpic.hst min and max of alpha_probe, np of the last record: " +
                      "; ".join(f"{R[q]['dir']} {R[q]['outcomes']['central_lapse']['min']:.4f}-{R[q]['outcomes']['central_lapse']['max']:.4f}, "
                                f"np {R[q]['outcomes']['np_start']}->{R[q]['outcomes']['np_end']}" for q in st)),
                 Cell(r"$\approx0.89$; $0.81$--$0.82$ (" + FIG + ")",
                      figsrc("st_dynamics.pdf", "lapse panels of y_c = 0.900 (flat near 0.89) and 0.819 (0.81 with a rise to about 0.82)"))))
    lw = {}
    for q in st:
        h = CACHE[q]["hst"]
        w = h[:, H["sum_mw"]] / h[:, H["sum_m"]]
        lw[q] = (float(np.abs(w - w[0]).max()), float(w[0]))
    rows.append((r"Largest change of the mean Lorentz factor $\sum_p m_pW_p/\sum_p m_p$ over $300M$, $y_c=0.900$; $0.819$",
                 Cell("; ".join(sci(lw[q][0]) for q in st),
                      "st.nrpic.hst sum_mW/sum_m, largest |value - first value|: " +
                      "; ".join(f"{R[q]['dir']} {lw[q][0]:.3e} (first value {lw[q][1]:.5f})" for q in st)), NA))
    un = ["st/yc0605_v5", "st/yc0500_v5"]
    rows.append((r"First apparent horizon $t/M$: $y_c=0.605$; $0.500$",
                 Cell("; ".join(f"{R[q]['outcomes']['horizon']['first_t']:.1f}" for q in un),
                      "st.horizon_summary_0.txt, first row with a finite mass: " +
                      "; ".join(f"{R[q]['dir']} {R[q]['outcomes']['horizon']['first_t']}" for q in un)),
                 Cell("109; 73", osrc("0.605 & 0.592", "table of the monoenergetic models, t_BH") + "; " +
                      osrc("0.500 & 0.817", "same table"))))
    rows.append((r"$M_{\rm AH}/M$ at the end; macroparticles left of $10^4$",
                 Cell("; ".join(f"{R[q]['outcomes']['horizon']['last_mass']:.4f}" for q in un) + "; " +
                      ", ".join(str(R[q]["outcomes"]["np_end"]) for q in un),
                      "st.horizon_summary_0.txt last row; st.nrpic.hst np of the last record: " +
                      "; ".join(f"{R[q]['dir']} M_AH {R[q]['outcomes']['horizon']['last_mass']:.5f} at t = "
                                f"{R[q]['outcomes']['horizon']['last_t']}, np {R[q]['outcomes']['np_end']} at t = "
                                f"{R[q]['outcomes']['t_final']:.2f}" for q in un)),
                 Cell(r"$\simeq1$ (stated)", osrc("The detected AH mass is consistent with the initial ADM mass", "text"))))
    rows.append((r"$\alpha_c$ at the end, after the horizon forms: $y_c=0.605$; $0.500$",
                 Cell("; ".join(f"{R[q]['outcomes']['central_lapse']['end']:.3f}" for q in un),
                      "st.nrpic.hst alpha_probe of the last record: " +
                      "; ".join(f"{R[q]['dir']} t = {R[q]['outcomes']['t_final']:.2f}" for q in un)),
                 Cell(r"$\approx0.20$ (" + FIG + ")", figsrc("st_dynamics.pdf", "lapse panels of y_c = 0.605 and 0.500 after the "
                                                                              "horizon (dashed line), level near 0.20"))))
    q = "st/yc0283_v5"
    o = R[q]["outcomes"]
    rows.append((r"$y_c=0.283$: $\alpha_c$ at the end ($t/M$); particles kept",
                 Cell(f"{o['central_lapse']['end']:.3f} ({o['t_final']:.0f}); all", f"{R[q]['dir']}, st.nrpic.hst last record "
                                                                                 f"(np {o['np_end']} of {o['np_start']}; {R[q]['status']})"),
                 Cell(r"$\approx0.98$ (300; " + FIG + ")", figsrc("st_dynamics.pdf", "lapse panel of y_c = 0.283 at t = 300 M"))))
    G.append(("Cluster sequence with inward kick", rows))

    # ---- unperturbed y_c = 0.5
    rows = []
    dirs = [("st/dir_yc0500_plain", "plain"), ("st/dir_yc0500_comp", "c1"), ("st/dir_yc0500_comp_s2", "c2"),
            ("st/dir_yc0500_comp_s3", "c3")]
    tx = [first_cross(*lapse(key), 0.8) for key, _ in dirs]
    km = "st/migration_yc0500_v4"
    tm = first_cross(*lapse(km), 0.8)
    rows.append((r"Time $t/M$ at which $\alpha_c$ first reaches 0.8: plain filter; compensated, samples 1--3",
                 Cell(f"{tx[0]:.0f}; " + ", ".join(f"{v:.0f}" for v in tx[1:]),
                      "st.nrpic.hst alpha_probe, linear interpolation at the first upward crossing of 0.8: " +
                      "; ".join(f"{R[key]['dir']} {v:.2f}" for (key, _), v in zip(dirs, tx)) +
                      f"; {R[km]['dir']} (same sample 1, compensated) {tm:.2f}"),
                 Cell(r"$\approx120$ (" + FIG + ")", figsrc("migration_central_evolution.pdf", "panel (a), first upward crossing of 0.8"))))
    t, a = lapse(km)
    ex = mig_extrema(t, a, smooth=10.0, swing=0.02)
    early = [e for e in ex if e[1] < 1000.0]
    late = [e for e in ex if e[1] >= 1000.0]
    fmt = lambda e: f"{e[2]:.3f} ({e[1]:.0f})"  # noqa: E731
    here1 = f"{a[0]:.3f} (0); " + "; ".join(fmt(e) for e in early)
    exsrc = (f"{R[km]['dir']}, st.nrpic.hst alpha_probe ({R[km]['status']}, records to t = {t[-1]:.0f} M); start = first "
             f"record; extrema as in paper/scripts/make_data_migration.extrema (10 M running mean, prominence 0.02, "
             f"moved to the extreme record within 10 M): ")
    O = MIG_ORIGINAL
    def two(x):                      # 0.9 -> 0.90, 0.905 -> 0.905 (as read off the figure)
        v = f"{x:.3f}"
        return v[:-1] if v.endswith("0") else v

    def ofmt(r):
        tt_ = f"{r[0]:.0f}" if r[1] == r[2] else f"{r[1]:.0f}--{r[2]:.0f}"
        aa = two(r[3]) if r[4] == r[5] else f"{two(r[4])}--{two(r[5])}"
        return f"{aa} ({tt_})"
    osrc_mig = (f"{rel(HERE / 'make_data_migration.py')}, array ORIGINAL (t, t_lo, t_hi, alpha, alpha_lo, alpha_hi), read by "
                f"eye from the rendered figure refs/arxiv_2611.12831/src/Figures/migration_central_evolution.pdf: ")
    oe = [r for r in O if r[0] < 1000.0]
    ol = [r for r in O if r[0] >= 1000.0]
    rows.append((r"Migration: $\alpha_c$ at the start and at its extrema to $1000M$ ($t/M$)",
                 Cell(here1, exsrc + "; ".join(f"{k_} {x:.4f} at {y:.2f}" for k_, y, x in early)),
                 Cell("; ".join(ofmt(r) for r in oe) + " (" + FIG + ")",
                      osrc_mig + "; ".join(ofmt(r) for r in oe))))
    m_late = float(a[t >= 1500.0].mean())
    rows.append((r"Migration: extrema after $1000M$ ($t/M$); $\alpha_c$ at the end; mean over $1500$--$2500M$",
                 Cell("; ".join(fmt(e) for e in late) + f"; {a[-1]:.3f} ({t[-1]:.0f}); {m_late:.3f}",
                      exsrc + "; ".join(f"{k_} {x:.4f} at {y:.2f}" for k_, y, x in late) +
                      f"; last record {a[-1]:.4f} at {t[-1]:.2f}; mean of alpha_probe over the records with t >= 1500 M"),
                 Cell("; ".join(ofmt(r) for r in ol) + " (" + FIG + r"); late mean 0.834 (from its text)",
                      osrc_mig + "; ".join(ofmt(r) for r in ol) + "; " +
                      osrc(r"\langle\alpha_c\rangle&=0.833530", "text: time-averaged late core lapse 0.833530"))))
    o = R[km]["outcomes"]
    esc = ", ".join(f"{x:.0f}" for x in o["escape_times"])
    rows.append((r"Migration: macroparticles removed by excision; leaving the domain (at $t/M$)",
                 Cell(f"{o['n_excised_end']}; {o['n_escaped_end']}" + (f" ({esc})" if esc else ""),
                      f"{R[km]['dir']}, st.nrpic.hst columns n_excised and n_escaped of the last record (t = "
                      f"{o['t_final']:.0f}), times at which n_escaped steps; np {o['np_start']} -> {o['np_end']}; "
                      f"domain half-width {R[km]['mesh']['domain_half_width']:g} M; run {R[km]['status']}"),
                 NA))
    G.append((r"Unperturbed $y_c=0.5$", rows))

    # ---- near-critical model
    rows = []
    k = "st/reconf_yc0756_hc"
    o = R[k]["outcomes"]
    hd = R[k]["model"]["components"][0]["header"]
    rows.append((r"Compressed by ten percent: $\alpha_c(0)$; first apparent horizon $t/M$",
                 Cell(f"{o['central_lapse']['t0']:.3f}; {o['horizon']['first_t']:.1f}",
                      f"{R[k]['dir']}, st.nrpic.hst first alpha_probe (table alpha_c {hd['alpha_c']:.5f}); "
                      f"st.horizon_summary_0.txt first row with a finite mass"),
                 Cell(r"$\simeq0.75$; none", osrc("compared with the initial values $\\alpha_c\\simeq0.75$", "text") + "; " +
                      osrc("By $2000M$, the cluster has reorganized", "text: no collapse"))))
    rows.append((r"Compressed: $M_{\rm AH}/M$ at the end; $M$ of the initial data; macroparticles left",
                 Cell(f"{o['horizon']['last_mass']:.4f}; {hd['M_ADM']:.4f}; {o['np_end']}",
                      f"{R[k]['dir']}, st.horizon_summary_0.txt last row (t = {o['horizon']['last_t']}); cluster.tab header "
                      f"M_ADM = {hd['M_ADM']:.6f}; st.nrpic.hst np of the last record (t = {o['t_final']:.1f})"),
                 Cell(r"all kept", osrc("All particles remain present throughout the displayed interval", "text"))))
    v = max_diff("st/reconf_yc0756_v4", k, 120.0)
    rows.append((r"Compressed: largest $|\Delta\alpha_c|$ to $120M$ between the consistent and the unperturbed initial metric",
                 Cell(f"{v:.3f}", f"runs/st/reconf_yc0756_v4 against {R[k]['dir']}, st.nrpic.hst alpha_probe interpolated, t <= 120 M: {v:.4f}"),
                 NA))
    # density lowered by ten percent
    k = "st/reconf_yc0756_hc_m"
    t, a = lapse(k)
    o = R[k]["outcomes"]
    T, Rq, Nq, Mq = radii(k)
    rows.append((r"Density lowered by ten percent: $\alpha_c$ range; mean over $600M$; radii enclosing 90 and 10 percent of "
                 r"the rest mass, range ($t=0$); macroparticles kept",
                 Cell(f"{a.min():.3f}--{a.max():.3f}; {a.mean():.3f}; {Rq[:, 8].min():.1f}--{Rq[:, 8].max():.1f} ({Rq[0, 8]:.1f}), "
                      f"{Rq[:, 0].min():.1f}--{Rq[:, 0].max():.1f} ({Rq[0, 0]:.1f}); "
                      + ("all" if o["np_end"] == o["np_start"] else f"{o['np_end']} of {o['np_start']}"),
                      f"{R[k]['dir']}, st.nrpic.hst alpha_probe min, max, mean over all records (to {t[-1]:.0f} M); "
                      f"particle snapshots st.part.*.bin ({len(T)} times, {T[0]:g}-{T[-1]:g} M): radii about the origin "
                      f"enclosing 90 and 10 percent of the rest mass present (paper/scripts/make_data_clusters.shells); "
                      f"np {o['np_start']} -> {o['np_end']}"),
                 NA))
    # unperturbed model
    k = "st/yc0756_unpert"
    t, a = lapse(k)
    o = R[k]["outcomes"]
    eq = R[k]["model"]["components"][0]["header"]["alpha_c"]
    ex = mig_extrema(t, a, smooth=5.0, swing=0.01)
    mins = [y for kind, y, x in ex if kind == "min" and y >= 200.0]
    sp = np.diff(mins)
    tm = [0.5 * (y0 + y1) for y0, y1 in zip(mins[:-1], mins[1:])]
    sp_a = [d_ for d_, c_ in zip(sp, tm) if c_ < 600.0]
    sp_b = [d_ for d_, c_ in zip(sp, tm) if c_ >= 600.0]
    hs = [(ex[i][1], abs(ex[i][2] - ex[i - 1][2]) / 2, (ex[i][2] + ex[i - 1][2]) / 2) for i in range(1, len(ex))]
    j = int(np.argmax([x[1] for x in hs]))
    Oc = NC_ORIGINAL
    Oe = Oc[Oc[:, 0] <= 600.0]
    imax = [i for i in range(1, len(Oe) - 1) if Oe[i, 1] > Oe[i - 1, 1] and Oe[i, 1] > Oe[i + 1, 1]]
    ohs = [(0.5 * (Oe[i - 1, 0] + Oe[i, 0]), abs(Oe[i, 1] - Oe[i - 1, 1]) / 2, Oe[i - 1, 0], Oe[i, 0]) for i in range(2, len(Oe))]
    oj = int(np.argmax([x[1] for x in ohs]))
    osp = np.diff(Oe[imax, 0])
    omid = 0.5 * (Oe[imax, 0][:-1] + Oe[imax, 0][1:])
    t_split = Oe[imax, 0][int(np.argmax(osp > 55.0))] if (osp > 55.0).any() else 600.0
    osp_a, osp_b = osp[omid < t_split], osp[omid >= t_split]
    ncsrc = (f"{rel(HERE / 'make_data_nearcritical.py')}, array ORIGINAL (t, alpha_c), read by eye from the rendered figure "
             f"refs/arxiv_2611.12831/src/Figures/migration_lapse_redshift_shells.pdf (accuracy about 10 M and 0.005); ")
    rows.append((r"Unperturbed: spacing of successive minima of $\alpha_c$ from $200M$, before and after $600M$",
                 Cell(f"{min(sp_a):.0f}--{max(sp_a):.0f}; {min(sp_b):.0f}--{max(sp_b):.0f}",
                      f"{R[k]['dir']}, st.nrpic.hst alpha_probe; extrema as in paper/scripts/make_data_migration.extrema with "
                      f"5 M running mean and prominence 0.01 (as make_data_nearcritical.py); minima from 200 M at " +
                      ", ".join(f"{y:.1f}" for y in mins) + "; spacings " + ", ".join(f"{d_:.2f}" for d_ in sp)),
                 Cell(f"maxima {min(osp_a):.0f}--{max(osp_a):.0f} to {t_split:.0f}, {min(osp_b):.0f}--{max(osp_b):.0f} after "
                      f"(perturbed run; {FIG})",
                      ncsrc + "maxima at " + ", ".join(f"{x:.0f}" for x in Oe[imax, 0]) + "; spacings " +
                      ", ".join(f"{x:.0f}" for x in osp))))
    rows.append((r"Unperturbed: largest half-swing of $\alpha_c$ between successive extrema ($t/M$)",
                 Cell(f"{hs[j][1]:.3f} ({hs[j][0]:.0f})",
                      f"{R[k]['dir']}, same extrema: half of |difference| of successive extrema, largest {hs[j][1]:.4f} "
                      f"ending at {hs[j][0]:.1f} M"),
                 Cell(f"{ohs[oj][1]:.3f} ({ohs[oj][2]:.0f}--{ohs[oj][3]:.0f}; perturbed run; {FIG})",
                      ncsrc + f"half of |difference| of successive rows to 600 M, largest between {ohs[oj][2]:.0f} and "
                              f"{ohs[oj][3]:.0f} M")))
    last = hs[-2:]
    rows.append((r"Unperturbed: $\alpha_c$ range; mean of the last two pairs of successive extrema ($t/M$); "
                 r"macroparticles kept",
                 Cell(f"{a.min():.3f}--{a.max():.3f}; " + ", ".join(f"{x[2]:.3f} ({x[0]:.0f})" for x in last) + "; "
                      + ("all" if o["np_end"] == o["np_start"] else f"{o['np_end']} of {o['np_start']}"),
                      f"{R[k]['dir']}, st.nrpic.hst alpha_probe min and max over the run (to {t[-1]:.0f} M), mean of successive "
                      f"extrema (equilibrium {eq:.4f}): " + ", ".join(f"{x[2]:.4f} ending at {x[0]:.1f}" for x in last) +
                      f"; np {o['np_start']} -> {o['np_end']}"),
                 Cell(f"{Oe[:, 1].min():.3f}--{Oe[:, 1].max():.3f}; {Oc[-1, 1]:.3f} ({Oc[-1, 0]:.0f}; perturbed run; {FIG}); "
                      r"all kept",
                      ncsrc + f"min and max of the rows to 600 M; last row; " +
                      osrc("All particles remain present throughout the displayed interval", "text"))))
    G.append((r"Near-critical $y_c=0.756$", rows))
    G.extend(jeans_rows(do_slice))
    return G


def prolate_rows(do_slice):
    """Outcome rows of the prolate collapse."""
    k = "prolate/e09_v8"
    d = RUNS_DIR / k
    rows, NA = [], Cell("--", "not given in the original")
    c = np.loadtxt(d / "prol.curv.hst", comments="#", ndmin=2)
    c = c[current(c[:, 0])]
    i = int(np.argmax(c[:, 1]))
    R[k]["outcomes"]["kretschmann_max"] = {"value": float(c[i, 1]), "t": float(c[i, 0]),
                                          "x": float(c[i, 2]), "y": float(c[i, 3]), "z": float(c[i, 4]),
                                          "note": "largest |I| on the mesh, prol.curv.hst; depends on the cell size"}
    rows.append((r"Largest Kretschmann scalar: time $t/M$ and $|z|/M$ (on the axis)",
                 Cell(f"{c[i, 0]:.2f}; {abs(c[i, 4]):.2f}",
                      f"{R[k]['dir']}, prol.curv.hst (columns time, max|I|, x, y, z), record with the largest max|I|: "
                      f"t = {c[i, 0]:.4f}, |I| = {c[i, 1]:.1f} M^-4 (value kept out of the table: it depends on the cell size), "
                      f"(x, y, z) = ({c[i, 2]:.3f}, {c[i, 3]:.3f}, {c[i, 4]:.3f})"), NA))
    o = R[k]["outcomes"]
    hz = o["horizon"]
    rows.append((r"First apparent horizon $t/M$; $M_{\rm AH}/M$",
                 Cell(f"{hz['first_t']:.2f}; {hz['first_mass']:.3f}",
                      f"{R[k]['dir']}, prol.horizon_summary_0.txt, first row with a finite mass: t = {hz['first_t']}, "
                      f"{hz['first_mass']:.6f} (searches every {R[k]['horizon_finder']['search_every_cycles']:g} cycles)"),
                 Cell("32 (from its text)", osrc("the configuration after apparent-horizon detection at $t=32M$", "text"))))
    ah = CACHE[k]["ah"]
    j = int(np.argmax(ah[:, 1]))
    rows.append((r"Largest $M_{\rm AH}/M$ ($t/M$); $M_{\rm AH}/M$ at the last search ($t/M$)",
                 Cell(f"{ah[j, 1]:.4f} ({ah[j, 0]:.2f}); {ah[-1, 1]:.4f} ({ah[-1, 0]:.2f})",
                      f"{R[k]['dir']}, prol.horizon_summary_0.txt: largest mass {ah[j, 1]:.6f} at t = {ah[j, 0]}; last row "
                      f"{ah[-1, 1]:.6f} at t = {ah[-1, 0]}"), NA))
    rows.append((r"First and last removal of macroparticles $t/M$ (macroparticles left)",
                 Cell(f"{o['removal_first_t']:.2f}; {o['all_removed_t']:.2f} ({o['np_end']})",
                      f"{R[k]['dir']}, prol.nrpic.hst: first record with n_excised > 0; first record with np = 0; np of the "
                      f"last record; removed rest mass {CACHE[k]['hst'][-1, H['m_excised']]:.4f} of "
                      f"{CACHE[k]['hst'][0, H['sum_m']]:.4f}"), NA))
    S = CACHE.get("slice", {})
    if do_slice:
        last = sorted(d.glob("rst/prol.[0-9][0-9][0-9][0-9][0-9].rst"))[-1]
        A = sm.analyse(sm.rst_open(str(last), strict=True))
        X = A["X"][sm.NPER2_H]
        S[k] = {"time": float(A["time"]), "file": rel(last), "mass": float(X["RH"] / 2),
                "unc_shells": float(A["dMH_shell"]), "unc_spread": float(A["dMH_spread"]),
                "m_inf": float(A["m_inf"]), "flat": bool(A["flat"])}
        CACHE["slice"] = S
        s_ = S[k]
        rows.append((r"Misner--Sharp mass on the last slice, at the horizon ($\pm$ its spread over angle) and at large "
                     r"radius ($t/M$ of the slice)",
                     Cell(f"{s_['mass']:.3f} $\\pm$ {s_['unc_spread']:.3f}; {s_['m_inf']:.3f} ({s_['time']:.0f})",
                          f"{R[k]['dir']}, {Path(s_['file']).name} (t = {s_['time']:.2f} M), recomputed here with "
                          f"analysis/diag/slicemass.analyse: outermost 2m/R = 1, M_H = {s_['mass']:.5f} +- {s_['unc_shells']:.1e} "
                          f"(shells) +- {s_['unc_spread']:.1e} (spread of m); asymptotic m = {s_['m_inf']:.6f} "
                          f"({'flat' if s_['flat'] else 'NOT FLAT: median over the outermost factor 2 in r'}); agrees with "
                          f".work/slicemass_prolate_last.out (t = 45: M_H = 0.91950 +- 6e-04 +- 3e-02, m_inf = 0.998989 NOT FLAT)"),
                     NA))
    else:
        rows.append((r"Misner--Sharp mass on the last slice: at the horizon; at large radius",
                     Cell("not computed", "run without --no-slice"), NA))
    z = CACHE[k]["z"]
    Hn = np.sqrt(z["H-norm2"])
    zl = CACHE["os/nocap_sc"]["z"]
    Hl = np.sqrt(zl["H-norm2"])
    rows.append((r"Largest $\|\Ham\|$ ($t/M$); lattice dust collapse (finest level, corrected masses) on the same measure",
                 Cell(f"{Hn.max():.2f} ({z['time'][Hn.argmax()]:.1f}); {Hl.max():.2f}",
                      f"{R[k]['dir']}, prol.z4c.user.hst sqrt(H-norm2), max {Hn.max():.4f} at t = {z['time'][Hn.argmax()]:.2f}; "
                      f"runs/os/nocap_sc, os.z4c.user.hst, max {Hl.max():.4f} at t = {zl['time'][Hl.argmax()]:.2f}"), NA))
    return [("Prolate collapse", rows)]


def jeans_setup_row():
    """Setups-table row of the cluster with two collapsing overdensities: the run with
    finest cells M/64 (family "jeans"; the M/128 comparison is not tabulated). Returns
    (name, run keys, base run, varied columns, model Cell) as the rows of setup_rows()."""
    keys = fam("jeans")
    k = keys[0]
    ic = R[k]["model"]["particles"]
    gen = REPO / (ic["generator_file"][:-4] + ".json")
    meta = json.load(open(gen))
    env, cl = meta["envelope"], meta["clumps"]
    n = [c["N"] for c in meta["components"]]
    assert n[1] == n[2], n
    return ("Two overdensities", keys, k, set(), Cell(
        rf"envelope $y_c={env['yc']:g}$ of ${env['M_env']:g}M$, areal radius ${env['R_areal']:.1f}M$; Gaussian clumps of "
        rf"${cl['m_c']:g}M$, width ${cl['sigma']:g}M$, at $x=\pm{abs(cl['x_A'][0]):g}M$, speed ${abs(cl['v_B'][1]):.3f}$; "
        rf"${n[0]}+2\times{n[1]}$ macroparticles",
        runs_src(keys, f"generator metadata {rel(gen)} (its .nrp matched to the run's particle file): envelope.yc = "
                       f"{env['yc']}, envelope.M_env = {env['M_env']}, envelope.R_areal = {env['R_areal']:.4f} (isolated "
                       f"envelope; with the clumps R_areal_composite = {env['R_areal_composite']:.4f}), clumps.m_c = "
                       f"{cl['m_c']}, clumps.sigma = {cl['sigma']}, clumps.x_A = {cl['x_A']}, clumps.x_B = {cl['x_B']}, "
                       f"clumps.v_A = {cl['v_A']}, clumps.v_B = {cl['v_B']}, components N = {n}")))


def jeans_rows(do_slice=True):
    """Outcome rows of the cluster with two collapsing overdensities (finest cells M/64),
    appended to the last cluster float. The horizon records (stale rows and searches of A
    or B that converged on the common horizon left out) and the tracker positions come
    from make_data_overdensities.reduce_run, so table and figure agree."""
    keys = fam("jeans")
    k = keys[0]
    assert OD_MESHES["64"] == [(Path(k).name, 0.0)], OD_MESHES["64"]
    d = RUNS_DIR / k
    D, files = od_reduce_run(OD_MESHES["64"], with_snapshots=False)
    NA = Cell("--", "not given in the original")
    src0 = R[k]["dir"]
    flt = ("rows with a finite mass, without stale rows (equal in every column to the previous found row) and without "
           "rows of A or B within 1 percent of the common-horizon mass of the same search time "
           "(paper/scripts/make_data_overdensities.reduce_run)")
    rows = []

    def found(lab):
        M = D[f"ah{lab}_M"]
        ok = np.isfinite(M)
        return D[f"ah{lab}_t"][ok], M[ok], D[f"ah{lab}_S"][ok], D[f"ah{lab}_Svec"][ok]

    def near(lab, t0):
        t, M, S, Sv = found(lab)
        j = int(np.argmin(np.abs(t - t0)))
        return float(t[j]), float(M[j]), float(S[j]), Sv[j]

    def rec(key, t0):
        t, y = D["pos_t"], D[key]
        ok = np.isfinite(y) if y.ndim == 1 else np.isfinite(y).all(1)
        return np.interp(t0, t[ok], y[ok]) if y.ndim == 1 else \
            np.array([np.interp(t0, t[ok], y[ok, c]) for c in range(y.shape[1])])

    par = PARAMS[k]
    every, t_start = int(num(par[("fastflow", "find_every")])), num(par[("fastflow", "start_time_0")])
    tA, MA, _, _ = found("A")
    tB, MB, _, _ = found("B")
    tC, MC, SC, SvC = found("C")
    tc0, tf = float(tC[0]), float(D["t_first"])
    rows.append((r"First apparent horizons of A, B: $t/M$; $M_{\rm AH}/M$",
                 Cell(f"{tA[0]:.2f}, {tB[0]:.2f}; {MA[0]:.4f}, {MB[0]:.4f}",
                      f"{src0}, jeans.horizon_summary_0.txt and _1.txt (columns time, mass), first row with a finite mass: "
                      f"A t = {tA[0]:g}, {MA[0]:.6f}; B t = {tB[0]:g}, {MB[0]:.6f} (searches every {every} cycles from "
                      f"t = {t_start:g} M)"),
                 Cell("8.475, 8.525; --", osrc("at $t=8.475M$ and $8.525M$", "text"))))
    a20, b20 = near("A", 20.0), near("B", 20.0)
    a40, b40 = near("A", 40.0), near("B", 40.0)
    la, lb = (tA[tA < tc0][-1], MA[tA < tc0][-1]), (tB[tB < tc0][-1], MB[tB < tc0][-1])
    rows.append((r"$M_{\rm AH}/M$ of A, B at $t=20M$; $40M$; at the last search before the first common horizon ($t/M$)",
                 Cell(f"{a20[1]:.4f}, {b20[1]:.4f}; {a40[1]:.4f}, {b40[1]:.4f}; {la[1]:.4f}, {lb[1]:.4f} "
                      f"({la[0]:.2f}, {lb[0]:.2f})",
                      f"{src0}, jeans.horizon_summary_0.txt and _1.txt, {flt}: A at t = {a20[0]:g}, {a40[0]:g}, {la[0]:g}: "
                      f"{a20[1]:.6f}, {a40[1]:.6f}, {la[1]:.6f}; B at t = {b20[0]:g}, {b40[0]:g}, {lb[0]:g}: {b20[1]:.6f}, "
                      f"{b40[1]:.6f}, {lb[1]:.6f}"),
                 Cell(r"0.0880, 0.0877 at $10M$; 0.1742, 0.1761 at $60M$",
                      osrc("the individual masses are $0.08802M$ and $0.08772M$", "text") + "; " +
                      osrc("they have increased to $0.17421M$ and $0.17605M$", "text"))))
    s0, s1 = rec("pos_sep", tf), rec("pos_sep", tc0)
    turn = (rec("pos_phi", tc0) - rec("pos_phi", tf)) / (2 * np.pi)
    rows.append((r"Coordinate separation of the trackers $d/M$ at the first apparent horizon; at the first common "
                 r"horizon; turns of the line from A to B between the two",
                 Cell(f"{s0:.2f}; {s1:.2f}; {turn:.2f}",
                      f"{src0}: tracker positions from the restart-dump headers and the tracker files jeans.co_0.txt, "
                      f"jeans.co_1.txt with their copies in co_archive/, monotone cubic between restart dumps before the "
                      f"tracker files begin (paper/scripts/make_data_overdensities.reduce_run): d = {s0:.4f} at t = {tf:g}, "
                      f"{s1:.4f} at t = {tc0:g}; unwrapped angle of B - A about the z axis changes by "
                      f"{np.degrees(2 * np.pi * turn):.1f} deg"), NA))
    md = num(par[("fastflow", "merger_distance")])
    mco = num(par[("z4c", "co_0_mass")]) + num(par[("z4c", "co_1_mass")])
    t_search = float(D["ahC_t"][0])
    at_first = abs(t_search - tc0) < 1e-9
    rows.append((r"First common apparent horizon" + (", found at the first search of it" if at_first else "") +
                 r" (searched only while the trackers are closer than $" + f"{md * mco:.2f}" + r"M$): $t/M$; "
                 r"$M_{\rm AH}/M$; $\chi=S/M_{\rm AH}^2$",
                 Cell(f"{tc0:.2f}; {MC[0]:.4f}; {SC[0] / MC[0] ** 2:.3f}",
                      f"{src0}, jeans.horizon_summary_2.txt (columns time, mass, S): first row with a finite mass t = {tc0:g}, "
                      f"M = {MC[0]:.6f}, S = {SC[0]:.6f}; first row of the file (first search) t = {t_search:g}; search "
                      f"condition: maximal tracker distance < fastflow/merger_distance ({md:g}) times z4c/co_0_mass + "
                      f"co_1_mass ({mco:g}) (athenak/src/z4c/fastflow.cpp, PuncAreClose)"),
                 Cell("64.16; 0.3833; 0.504", osrc("is found at $t_{\\rm m}=64.15625M$", "text") + "; " +
                      osrc("Initially, it has $M_{\\rm AH}=0.38326M$ and $\\chi=0.50355$", "text"))))
    tl = (70.0, 80.0, 90.0, 100.0)
    vals = [near("C", x) for x in tl]
    rows.append((r"Common horizon $M_{\rm AH}/M$, $\chi$ at $t=70$, $80$, $90$, $100M$",
                 Cell("; ".join(f"{v[1]:.4f}, {v[2] / v[1] ** 2:.3f}" for v in vals),
                      f"{src0}, jeans.horizon_summary_2.txt, row nearest to each time: " +
                      "; ".join(f"t = {v[0]:g}: M = {v[1]:.6f}, S = {v[2]:.6f}" for v in vals) +
                      f" (found in {len(tC)} of {len(D['ahC_t'])} searches)"),
                 Cell(r"0.6474, 0.171 at $100M$", osrc("By $t=100M$, the mass has grown to $0.64740M$", "text") + "; " +
                      osrc("decreases to $\\chi=0.17132$", "text"))))
    v90, v100 = vals[2], vals[3]
    dM, dchi = v100[1] - v90[1], v100[2] / v100[1] ** 2 - v90[2] / v90[1] ** 2
    rows.append((r"Change of the common-horizon $M_{\rm AH}/M$; of $\chi$, from $t=90M$ to the last search",
                 Cell(f"${dM:+.4f}$; ${dchi:+.4f}$",
                      f"{src0}, jeans.horizon_summary_2.txt rows at t = {v90[0]:g} and {v100[0]:g}: M {v90[1]:.6f} -> "
                      f"{v100[1]:.6f}, chi {v90[2] / v90[1] ** 2:.5f} -> {v100[2] / v100[1] ** 2:.5f}"), NA))
    tpos, okp = D["pos_t"], np.isfinite(D["pos_A"]).all(1) & np.isfinite(D["pos_B"]).all(1)
    mid = 0.5 * (D["pos_A"] + D["pos_B"])
    J = []
    for p in files:
        ts, q, _, _ = read_snapshot(p)
        if ts < tc0 - 1e-9:
            continue
        c = np.array([np.interp(ts, tpos[okp], mid[okp, i]) for i in range(3)])
        x = q[:, :3] - c
        Lz = float((q[:, 6] * (x[:, 0] * q[:, 4] - x[:, 1] * q[:, 3])).sum())
        j = int(np.argmin(np.abs(tC - ts)))
        J.append((ts, float(SvC[j][2]), Lz, float(SvC[j][2]) + Lz))
    J = np.array(J)
    rows.append((r"$S$ of the common horizon at the first and at the last search; $S_z$ plus $L_z$ of the macroparticles "
                 r"left (about the merged black hole), first common horizon to $100M$: first, last, range",
                 Cell(f"{SC[0]:.4f}, {SC[-1]:.4f}; {J[0, 3]:.4f}, {J[-1, 3]:.4f}, {J[:, 3].min():.3f}--{J[:, 3].max():.3f}",
                      f"{src0}, jeans.horizon_summary_2.txt column S (t = {tC[0]:g}, {tC[-1]:g}) and columns Sx, Sy, Sz; particle "
                      f"snapshots jeans.part.*.bin from t = {J[0, 0]:g} to {J[-1, 0]:g} M ({len(J)} times): L_z = sum m "
                      f"[(x - c) u_y - (y - c_y) u_x] with the stored spatial momenta u_i, c = midpoint of the trackers; "
                      f"S_z of the search at the snapshot time; at the first and last snapshot S_z = {J[0, 1]:.4f}, "
                      f"{J[-1, 1]:.4f}, L_z = {J[0, 2]:.4f}, {J[-1, 2]:.4f}"),
                 Cell(r"$J=\chi M_{\rm AH}^2$ conserved to 2\%", osrc("is conserved to within 2\\%", "text"))))
    h = CACHE[k]["hst"]
    th = h[:, 0]
    i1, i2, i3 = int(np.argmin(np.abs(th - tf))), int(np.argmin(np.abs(th - tc0))), len(h) - 1
    nx_, mx_ = h[:, H["n_excised"]], h[:, H["m_excised"]]
    st = [(0, i1), (i1, i2), (i2, i3)]
    rows.append((r"Macroparticles removed (rest mass$/M$): before the first apparent horizon; from it to the first common "
                 r"horizon; after it. Left at $100M$ (rest mass$/M$); left the domain",
                 Cell("; ".join(f"{nx_[b] - nx_[a]:.0f} ({mx_[b] - mx_[a]:.3f})" for a, b in st) +
                      f". {h[i3, H['np']]:.0f} ({h[i3, H['sum_m']]:.4f}); {h[i3, H['n_escaped']]:.0f}",
                      f"{src0}, jeans.nrpic.hst columns n_excised, m_excised at the records t = {th[i1]:g}, {th[i2]:g}, "
                      f"{th[i3]:g}; np, sum_m, n_escaped ({h[i3, H['m_escaped']]:g} rest mass) of the last record; rest mass "
                      f"at the start {h[0, H['sum_m']]:.6f}; first removal at t = {th[np.argmax(nx_ > 0)]:g}"), NA))
    if do_slice:
        rst = sorted(d.glob("rst/jeans.[0-9][0-9][0-9][0-9][0-9].rst"))
        tr = od_rst_trackers(str(rst[-1]))
        c = tuple(float(v) for v in tr[1].mean(0))
        A0 = sm.analyse(sm.rst_open(str(rst[0]), strict=True))
        A1 = sm.analyse(sm.rst_open(str(rst[-1]), strict=True), center=c)
        X = A1["X"][sm.NPER2_H]
        S = CACHE.setdefault("slice", {})
        S[k + " first dump"] = {"time": float(A0["time"]), "file": rel(rst[0]), "m_inf": float(A0["m_inf"]),
                                "flat": bool(A0["flat"])}
        S[k + " last dump"] = {"time": float(A1["time"]), "file": rel(rst[-1]), "mass": float(X["RH"] / 2),
                               "unc_shells": float(A1["dMH_shell"]), "unc_spread": float(A1["dMH_spread"]),
                               "m_inf": float(A1["m_inf"]), "flat": bool(A1["flat"]), "centre": c}
        rows.append((r"Slice Misner--Sharp mass at large radius at $t=0$ and $100M$; at the outermost $2m/R=1$ at "
                     r"$100M$ ($\pm$ its spread over angle)",
                     Cell(f"{A0['m_inf']:.4f}, {A1['m_inf']:.4f}; {X['RH'] / 2:.3f} $\\pm$ {A1['dMH_spread']:.3f}",
                          f"{src0}, {rst[0].name} (t = {A0['time']:g}) and {rst[-1].name} (t = {A1['time']:g}, centre at the "
                          f"trackers of its header {c}), recomputed here with analysis/diag/slicemass.analyse: m at large "
                          f"radius {A0['m_inf']:.5f} over r = {A0['flat_r'][0]:.1f}-{A0['flat_r'][1]:.1f} M and "
                          f"{A1['m_inf']:.5f} over r = {A1['flat_r'][0]:.1f}-{A1['flat_r'][1]:.1f} M "
                          f"({'flat' if A1['flat'] else 'NOT FLAT: median over the outermost factor 2 in r'}); "
                          f"M_H = {X['RH'] / 2:.5f} +- {A1['dMH_shell']:.1e} (shells) +- {A1['dMH_spread']:.1e} (spread)"),
                     NA))
    else:
        rows.append((r"Slice Misner--Sharp mass at large radius at $t=0$ and $100M$; at the horizon at $100M$",
                     Cell("not computed", "run without --no-slice"), NA))
    z = CACHE[k]["z"]
    Hn, tz = np.sqrt(z["H-norm2"]), z["time"]
    jm, jc = int(np.argmax(Hn)), int(np.argmin(np.abs(tz - tc0)))
    rows.append((r"$\|\Ham\|$ at $t=0$; largest ($t/M$); at the first common horizon; at $100M$",
                 Cell(f"{Hn[0]:.2f}; {Hn[jm]:.2f} ({tz[jm]:.1f}); {Hn[jc]:.2f}; {Hn[-1]:.2f}",
                      f"{src0}, jeans.z4c.user.hst sqrt(H-norm2): t = 0 {Hn[0]:.4f}; max {Hn[jm]:.4f} at t = {tz[jm]:g}; "
                      f"t = {tz[jc]:g} {Hn[jc]:.4f}; last record t = {tz[-1]:g} {Hn[-1]:.4f}"), NA))
    tlast = float(tpos[okp][-1])
    z30, zc, zend = (0.5 * (rec("pos_A", x) + rec("pos_B", x)) for x in (30.0, tc0, tlast))
    rows.append((r"Out of the orbital plane: $z/M$ of the midpoint of the trackers at $t=30M$; at the first common "
                 r"horizon; of the merged tracker at $100M$",
                 Cell(f"{z30[2]:.2f}; {zc[2]:.2f}; {zend[2]:.2f}",
                      f"{src0}: tracker positions as above (z resolved to 1/128 M in the tracker files): midpoint z at "
                      f"t = 30: {z30[2]:.4f}, t = {tc0:g}: {zc[2]:.4f}, t = {tlast:g}: {zend[2]:.4f}"), NA))
    return [("Two overdensities in a cluster", rows)]


OUT_FLOATS = [  # label, first and last group title (inclusive), caption
    ("tab:outcomes", "Fixed black hole", "Apparent-horizon check",
     r"Measured quantities to which the text refers for test particles and the apparent-horizon check, with the "
     r"values of " + CITE + r" where it gives them (from its text, or read from its figures). Masses in units of the "
     r"total mass $M$, times in units of $M$; listed values follow the order named in the first column."),
    ("tab:outcomes_dust", "Dust collapse on a lattice", "Dust collapse from a random sample",
     r"As Table~\ref{tab:outcomes}, for dust collapse. Hamiltonian constraint norm $\|\Ham\|=(\int\Ham^2\sqrt{\gamma}\,"
     r"\dd^3x)^{1/2}$, integrated over the grid cells with $\chi\ge1/16$ (a total, without division by a volume); the "
     r"same measure in every table."),
    ("tab:outcomes_prolate", "Prolate collapse", "Prolate collapse",
     r"As Table~\ref{tab:outcomes}, for the collapse of a prolate spheroid; $\|\Ham\|$ as in "
     r"Table~\ref{tab:outcomes_dust}."),
    ("tab:outcomes_clusters", r"Stable cluster $y_c=0.819$: filter", "Cluster sequence with inward kick",
     r"As Table~\ref{tab:outcomes}, for the relativistic clusters; $\|\Ham\|$ as in Table~\ref{tab:outcomes_dust}. "
     r"Central lapse $\alpha_c$ in the eight central cells; $\alpha_c(0)$ is its value at $t=0$."),
    ("tab:outcomes_migration", r"Unperturbed $y_c=0.5$", None,
     r"As Table~\ref{tab:outcomes_clusters}, for the unperturbed model past the binding-energy maximum, the "
     r"near-critical model, and the cluster with two collapsing overdensities (finest cells $M/64$; "
     r"$\chi=S/M_{\rm AH}^2$; $L_z$ from the stored spatial momenta $u_i$ of the macroparticles)."),
]


def write_outcomes(G):
    """One float per scenario block (labels in OUT_FLOATS), all in tab_outcomes.tex."""
    titles = [g[0] for g in G]
    L, led = [], []
    for label, first, lastt, caption in OUT_FLOATS:
        i0 = titles.index(first)
        i1 = titles.index(lastt) if lastt else len(G) - 1
        groups = G[i0:i1 + 1]
        L += [r"\begin{table*}", rf"\caption{{{caption}}}", rf"\label{{{label}}}", r"\footnotesize",
              r"\setlength{\tabcolsep}{3pt}", r"\begin{ruledtabular}",
              r"\begin{tabular}{p{0.49\textwidth}p{0.26\textwidth}p{0.205\textwidth}}",
              r"Quantity & This work & " + CITE + r" \tabularnewline", r"\colrule"]
        for gi, (title, rows) in enumerate(groups):
            if gi:
                L.append(r"\colrule")
            L.append(rf"\multicolumn{{3}}{{l}}{{\textit{{{title}}}}} \tabularnewline")
            for q, here, orig in rows:
                L.append(rf"\raggedright {q} & \raggedright {here.tex} & \raggedright {orig.tex} \tabularnewline")
                for col, c in (("This work", here), ("Ref.", orig)):
                    if re.search(r"\d", detex(c.tex)):
                        led.append(f"{label}, {detex(title)} / {detex(q)}, {col}: {detex(c.tex)} <- {c.src}")
        L += [r"\end{tabular}", r"\end{ruledtabular}", r"\end{table*}", ""]
        led.append(f"{label}, caption: {detex(caption)}")
    (OUT_TAB / "tab_outcomes.tex").write_text("\n".join(L))
    return led


# ---------------------------------------------------------------------------------------
def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    return x


R = {}


def main():
    do_slice = "--no-slice" not in sys.argv[1:]
    for key in RUNS:
        R[key] = collect(key)
        o = R[key]["outcomes"]
        print(f"{key:28s} {R[key]['status']:28s} t_final {o.get('t_final', float('nan')):8.2f}  "
              f"np {o.get('np_start')}->{o.get('np_end')}  notes {len(R[key]['notes'])}")
    rows = setups()
    G = outcomes(do_slice)
    OUT_TAB.mkdir(parents=True, exist_ok=True)
    led = write_setups(rows) + write_outcomes(G)
    doc = {"generated_by": rel(Path(__file__)),
           "units": "G = c = 1, lengths and times in units of the total (ADM) mass M",
           "notes": ["Parameters are those of the parameter dump of the first restart file (what the code read); "
                     "where a run has none, those of the copied input file plus the command-line overrides.",
                     "Wall-clock times and zone-cycles per second are of the job segments in this directory "
                     "(one graphics card); they are not quoted in the paper.",
                     "Delta x in the matter: levels of the MeshBlocks holding particles in the restart dumps; "
                     "finest_dx_reached: finest MeshBlock over all dumps."],
           "slice_masses": CACHE.get("slice", {}),
           "runs": R}
    OUT_JSON.write_text(json.dumps(jsonable(doc), indent=1, sort_keys=False))
    hdr = ["# Ledger of the numbers in tab_setups.tex and tab_outcomes.tex",
           "# table, row, column: value <- run directory (or result file), file, how computed",
           f"# written by {rel(Path(__file__))}; run directories are below the repository root",
           "# Terms: 'parameter dump' = the text before <par_end> in the first restart file rst/<basename>.00000.rst",
           "#   of the run directory (what the code read, overrides and defaults included); the one run without restart",
           "#   files (runs/puncture/hcal/dx8_tight) uses its copied input file plus the command-line overrides of its log;",
           "#   'particle history' = <basename>.nrpic.hst; 'constraint history' = <basename>.z4c.user.hst (norms are",
           "#   sqrt(H-norm2)); 'horizon summary' = <basename>.horizon_summary_0.txt (rows with a finite mass);",
           "#   'log' = athena.<timestamp>.log in the run directory or chain/seg*.log for chained runs;",
           "#   'generator metadata' = the .json written by the initial-data generator next to the original particle file,",
           "#   matched to the run's particle file by identical positions and masses (see runs.json, model.particles).",
           "# tab:outcomes, tab:outcomes_dust, tab:outcomes_prolate, tab:outcomes_clusters and tab:outcomes_migration are the floats of",
           "#   tab_outcomes.tex.", ""]
    OUT_LEDGER.write_text("\n".join(hdr + led) + "\n")
    print(f"{rel(OUT_JSON)}, {rel(OUT_LEDGER)} ({len(led)} lines), {rel(OUT_TAB)}/tab_setups.tex, tab_outcomes.tex")
    for key in RUNS:
        for n in R[key]["notes"]:
            print(f"NOTE {key}: {n}")


if __name__ == "__main__":
    main()
