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
    paper/sections/tables/tab_outcomes.tex  measured numbers the text points to
    paper/data/ledger.txt                   one line per number of the two tables

    python3 paper/scripts/make_tables.py [--no-slice]

--no-slice skips the Misner-Sharp masses of four restart dumps (about a minute) and
writes "not computed" in their place.
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
from common import (H, keep_last, read_athena_hst, read_horizon,  # noqa: E402
                    read_nrpic_hst, read_traj_tagged)
from nrpic import oppenheimer_snyder as osn  # noqa: E402

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
    "st/reconf_yc0756_hc": ["nearcrit"], "st/reconf_yc0756_hc_m": ["nearcrit"],
    "st/reconf_yc0756_v4": ["nearcrit"],
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
    "st/migration_yc0500_v4": "migration of the unperturbed y_c = 0.5 model (statements; figure to come)",
    "st/reconf_yc0756_hc": "near-critical model compressed by ten percent, consistent initial data (statement)",
    "st/reconf_yc0756_hc_m": "near-critical model expanded by ten percent (not yet in the text)",
    "st/reconf_yc0756_v4": "statement: the compressed particles on the unperturbed metric contract alike",
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
    m = re.search(r"NRPIC: read (\d+) particles", txt)
    out["particles_read"] = int(m.group(1)) if m else None
    return out


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
            "alpha_c", "rho_c", "zc", "R_areal")
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
    rec["status"] = status
    rec["notes"] = notes
    # ---- histories
    hp = d / f"{base}.nrpic.hst"
    hst = read_nrpic_hst(str(hp)) if hp.exists() else None
    zp = d / f"{base}.z4c.user.hst"
    z = read_athena_hst(str(zp)) if zp.exists() else {}
    ap = d / f"{base}.horizon_summary_0.txt"
    ah = keep_last(read_horizon(str(ap))) if ap.exists() else np.zeros((0, 6))
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


def dep_text(keys):
    vals = []
    for k in keys:
        p = R[k]["particles"]
        if not p["deposit"]:
            v = "none"
        elif p["deposit_max_coarsen"] is not None:
            v = "cap"
        else:
            v = "finest"
        vals.append(v)
    caps = sorted({R[k]["particles"]["deposit_max_coarsen"] for k in keys
                   if R[k]["particles"]["deposit_max_coarsen"] is not None})
    if set(vals) == {"cap"}:
        return "level-capped (" + ", ".join(r"$\le" + f"{c}$" if c < 31 else "any" for c in caps) + ")"
    return mode_and_others(vals, lambda v: {"finest": "finest level", "none": "none"}[v])


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
        Cell(r"$a=0.9M$, $a\to0$; cloud at $r_0=10M$", f"{tpc}, section 1 (initial data)"),
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

    def row(name, keys, model_cell):
        cells = [model_cell]
        ns = sorted({R[k]["outcomes"]["np_start"] for k in keys})
        smp = sorted({sampler_text(k) for k in keys})
        ntx = n_text(ns[0]) if len(ns) == 1 else f"{n_text(ns[0])}--{n_text(ns[-1])}"
        cells.append(Cell(f"{ntx}, {', '.join(smp)}",
                          runs_src(keys, "particle history, np of the first record; sampler from the generator metadata "
                                         "matched to the run's particle file") + " | " +
                          per_run(keys, lambda k: f"N={R[k]['outcomes']['np_start']} {sampler_text(k)}")))
        cells.append(Cell(mode_and_others([R[k]["mesh"]["domain_half_width"] for k in keys], frac),
                          runs_src(keys, "parameter dump, mesh/x1max (x1min = -x1max)") + " | " +
                          per_run(keys, lambda k: frac(R[k]["mesh"]["domain_half_width"]))))
        refs = {R[k]["mesh"]["refinement"] for k in keys}
        mtxt = (f"{refs.pop()}, " + mode_and_others(dx_cell(keys), str)) if len(refs) == 1 else \
            mode_and_others([f"{R[k]['mesh']['refinement']}, {dx_cell([k])[0]}" for k in keys], str, sep="; ")
        cells.append(Cell(mtxt,
                          runs_src(keys, "parameter dump, mesh_refinement/refinement; "
                                         "root spacing (x1max - x1min)/nx1 halved per level; levels of the MeshBlocks holding "
                                         "particles in the first restart dump and its particle restart file (gid -> block level); "
                                         "finest level of any MeshBlock over all dumps; for vacuum runs the finest level (at the puncture)") +
                          " | " + per_run(keys, lambda k: dx_cell([k])[0])))
        cells.append(Cell(mode_and_others([R[k]["dt_start"] or float("nan") for k in keys if R[k]["dt_start"]], frac),
                          runs_src([k for k in keys if R[k]["dt_start"]], "log, dt of the first step line (cycle 0)") + " | " +
                          per_run([k for k in keys if R[k]["dt_start"]], lambda k: f"{R[k]['dt_start']:.6g}")))
        cells.append(Cell(", ".join(sorted({nf_text(k) for k in keys})),
                          runs_src(keys, "parameter dump, particles/nfilter and particles/filter_compensate")))
        cells.append(Cell(dep_text(keys), runs_src(keys, "parameter dump, particles/deposit, deposit_adaptive, deposit_max_coarsen")))
        cells.append(Cell(mode_and_others([R[k]["particles"]["alpha_exc"] for k in keys], lambda v: f"{v:g}"),
                          runs_src(keys, "parameter dump, particles/alpha_exc")))
        cells.append(Cell(mode_and_others([R[k]["spacetime"]["kappa1"] for k in keys], lambda v: f"{v:g}"),
                          runs_src(keys, "parameter dump, z4c/damp_kappa1")))
        tf = [R[k]["outcomes"]["t_final"] for k in keys]
        tt = f"{tf[0]:.0f}" if max(tf) - min(tf) < 0.5 else f"{min(tf):.0f}--{max(tf):.0f}"
        cells.append(Cell(tt, runs_src(keys, "particle history, time of the last record") + " | " +
                          per_run(keys, lambda k: f"{R[k]['outcomes']['t_final']:.2f} ({R[k]['status']})")))
        rows.append((name, cells))

    def hdr(k):
        return R[k]["model"]["components"][0].get("header", {})

    k = "puncture/single_v3"
    row("Vacuum black hole", fam("vacuum"), Cell(
        f"puncture of mass $M$; {R[k]['particles']['tracers']} tracers",
        runs_src(fam("vacuum"), "parameter dump, problem/comp0_type = puncture, comp0_mass; particles/nparticles"
                                " (all five runs carry the six tracers)")))
    k = "puncture/headon_v4"
    c = R[k]["model"]["components"]
    row("Head-on collision", [k], Cell(
        rf"punctures $M/2$ at $x=\pm{abs(c[0]['position'][0]):g}M$; {R[k]['particles']['tracers']} tracers",
        runs_src([k], f"parameter dump, problem/comp0,1: masses {c[0]['mass']}, {c[1]['mass']}, "
                      f"x = {c[0]['position'][0]}, {c[1]['position'][0]}; particles/nparticles")))
    k = "os/nocap_sc"
    ic = R[k]["model"]["particles"]
    row("Dust collapse", fam("dust"), Cell(
        rf"$R_0={ic['R0_areal']:g}M$, $h={ic['lattice_h']:.2f}M$; masses corrected, published",
        runs_src(fam("dust"), f"generator metadata matched to the particle file: R0_areal = {ic['R0_areal']}, "
                              f"lattice_h = {ic['lattice_h']:.6f}, lattice_surface_correction = "
                              + per_run(fam('dust'), lambda q: str(R[q]['model']['particles'].get('lattice_surface_correction', False))))))
    row("Dust collapse, level cap", fam("dustcap"), Cell(
        r"as above, corrected masses",
        runs_src(fam("dustcap"), "generator metadata: " + per_run(
            fam("dustcap"), lambda q: f"lattice_surface_correction={R[q]['model']['particles'].get('lattice_surface_correction')}"))))
    keys = fam("filter")
    row("Stable cluster, filter", keys, Cell(
        rf"$y_c={hdr(keys[0])['yc']:g}$, unperturbed; samples 1--3",
        runs_src(keys, "initial-data table header yc; generator metadata seed and vpert: " +
                 per_run(keys, lambda q: f"seed {R[q]['model']['particles']['seed']} vpert {R[q]['model']['particles']['vpert']}"))))
    keys = fam("osc")
    row("Stable cluster, oscillation", keys, Cell(
        rf"$y_c={hdr(keys[0])['yc']:g}$, unperturbed; sample 1",
        runs_src(keys, "initial-data table header yc; generator metadata seed and vpert: " +
                 per_run(keys, lambda q: f"seed {R[q]['model']['particles']['seed']} vpert {R[q]['model']['particles']['vpert']}"))))
    keys = fam("nnum")
    row("Particle number", keys, Cell(
        rf"$y_c={hdr(keys[0])['yc']:g}$; kick 0.01 or none",
        runs_src(keys, "initial-data table header yc; generator metadata vpert: " +
                 per_run(keys, lambda q: f"vpert {R[q]['model']['particles']['vpert']}"))))
    keys = fam("stable")
    row("Sequence, stable", keys, Cell(
        r"$y_c=" + ", ".join(f"{hdr(q)['yc']:.3f}" for q in keys) + r"$; kick 0.01",
        runs_src(keys, "initial-data table header yc; generator metadata vpert: " +
                 per_run(keys, lambda q: f"yc {hdr(q)['yc']} vpert {R[q]['model']['particles']['vpert']}"))))
    keys = fam("unstable")
    row("Sequence, unstable", keys, Cell(
        r"$y_c=" + ", ".join(f"{hdr(q)['yc']:.3f}" for q in keys) + r"$; kick 0.01",
        runs_src(keys, "initial-data table header yc; generator metadata vpert: " +
                 per_run(keys, lambda q: f"yc {hdr(q)['yc']} vpert {R[q]['model']['particles']['vpert']}"))))
    keys = fam("unpert")
    row("Unperturbed unstable", keys, Cell(
        rf"$y_c={hdr(keys[0])['yc']:.3f}$, unperturbed; samples 1--3",
        runs_src(keys, "initial-data table header yc; generator metadata seed, vpert: " +
                 per_run(keys, lambda q: f"seed {R[q]['model']['particles']['seed']} vpert {R[q]['model']['particles']['vpert']}"))))
    keys = fam("nearcrit")
    row("Near-critical", keys, Cell(
        rf"$y_c={hdr(keys[0])['unperturbed.yc']:.3f}$; density $\times(1\pm0.1)$",
        runs_src(keys, "initial-data table header unperturbed.yc (or yc); generator metadata dpert: " +
                 per_run(keys, lambda q: f"dpert {R[q]['model']['particles']['dpert']}"))))
    return rows


FAMILY_ROW = {"vacuum": "Vacuum black hole", "headon": "Head-on collision", "dust": "Dust collapse",
              "dustcap": "Dust collapse, level cap", "filter": "Stable cluster, filter",
              "osc": "Stable cluster, oscillation", "nnum": "Particle number", "stable": "Sequence, stable",
              "unstable": "Sequence, unstable", "unpert": "Unperturbed unstable", "nearcrit": "Near-critical"}
SETUP_HEAD = ["Scenario and model", r"$N$, sampling", r"$L/M$", r"Mesh, $\Delta x/M$", r"$\Delta t/M$",
              r"$n_{\rm f}$", "Deposition", r"$\aexc$", r"$\kappa_1$", r"$t_{\rm end}/M$"]
SETUP_COLS = [0.22, 0.1, 0.05, 0.135, 0.07, 0.06, 0.085, 0.035, 0.065, 0.065]   # fractions of the text width


def write_setups(rows):
    # control runs marked by footnotes (single runs of the oscillation family)
    osc = [r for r in rows if r[0] == "Stable cluster, oscillation"][0][1]
    kch = [k for k in fam("osc") if R[k]["spacetime"]["c_H"]]
    kcc = [k for k in fam("osc") if R[k]["particles"]["compensation_c"] not in (None, R[k]["particles"]["nfilter"] / 4)]
    osc[SETUP_HEAD.index(r"$\kappa_1$")].tex += r"\footnotemark[1]"
    osc[SETUP_HEAD.index(r"$n_{\rm f}$")].tex += r"\footnotemark[2]"
    ch = R[kch[0]]["spacetime"]["c_H"]
    ccv = R[kcc[0]]["particles"]["compensation_c"]
    nf = R[kcc[0]]["particles"]["nfilter"]
    extra = 12 * (ccv - nf / 4)
    notes = [(rf"One run adds parabolic relaxation of $\Ham$ with $c_H={ch:g}\,M$.",
              runs_src(kch, "parameter dump, z4c/damp_ch")),
             (rf"One run uses $c=n_{{\rm f}}/4+{extra:.0f}/12$, which also cancels the cloud width.",
              runs_src(kcc, f"parameter dump, particles/filter_comp_c = {ccv!r}"))]
    running = [k for k in RUNS if R[k]["status"] == "running"]
    if running:
        for name, cells in rows:
            keys = [k for k in running if any(name == FAMILY_ROW[f] for f in RUNS[k])]
            if keys:
                cells[-1].tex += r"\footnotemark[3]"
        notes.append((r"Run in progress; values up to its last record.",
                      runs_src(running, "chain/STATUS = RUNNING; last record of the particle history at t = " +
                               ", ".join(f"{R[k]['outcomes']['t_final']:.2f}" for k in running))))
    cells_all = {(tuple(R[k]["mesh"]["root_cells"]), tuple(R[k]["mesh"]["cells_per_meshblock"])) for k in RUNS}
    assert cells_all == {((64, 64, 64), (16, 16, 16))}, cells_all
    caption = (r"Setups, one row per family of runs: model, macroparticle number $N$ and sampling, domain half-width $L$, "
               r"mesh and cell spacing $\Delta x$ in the matter at the start and the finest reached (vacuum runs: at the "
               r"puncture), first time step $\Delta t$, filter passes $n_{\rm f}$ (+c: compensation pass), deposition, "
               r"excision threshold $\aexc$, constraint damping $\kappa_1$, final time. Meshes other than uniform have "
               r"$64^3$ root cells in MeshBlocks of $16^3$ cells. Parentheses: single runs of a family.")
    notes.append(("caption: 64^3 root cells, 16^3-cell MeshBlocks",
                  runs_src(list(RUNS), "parameter dump, mesh/nx1..3 = 64 and meshblock/nx1..3 = 16 in every run "
                                       "(checked); docs/results_cluster_test.md, Mesh, for the test-particle clusters")))
    spec = "".join(rf"p{{{w}\textwidth}}" for w in SETUP_COLS)
    L = [r"\begin{table*}",
         rf"\caption{{{caption}}}",
         r"\label{tab:setups}",
         r"\footnotesize",
         r"\setlength{\tabcolsep}{2pt}",
         r"\begin{ruledtabular}",
         r"\begin{tabular}{" + spec + "}",
         " & ".join(rf"\raggedright {h}" for h in SETUP_HEAD) + r" \tabularnewline", r"\colrule"]
    for name, cells in rows:
        first = rf"{name}: {cells[0].tex}"
        L.append(" & ".join(rf"\raggedright {c}" for c in [first] + [c.tex for c in cells[1:]]) + r" \tabularnewline")
    L += [r"\end{tabular}", r"\end{ruledtabular}",
          *[rf"\footnotetext[{i}]{{{t}}}" for i, (t, _) in enumerate(notes, 1) if not t.startswith("caption")],
          r"\end{table*}", ""]
    (OUT_TAB / "tab_setups.tex").write_text("\n".join(L))
    led = []
    for name, cells in rows:
        for h, c in zip(["Model"] + SETUP_HEAD[1:], cells):
            if re.search(r"\d", detex(c.tex)):
                led.append(f"tab_setups, {name}, {detex(h)}: {detex(c.tex)} <- {c.src}")
    for i, (t, s) in enumerate(notes, 1):
        led.append(f"tab_setups, {t if t.startswith('caption') else f'footnote {i}: ' + detex(t)} <- {s}")
    return led


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
    tref = [R[key]["outcomes"]["dt_halvings"][1] for _, key in cap]
    txt, src = [], []
    for (_, key), t1_ in zip(cap, tref):
        z = CACHE[key]["z"]
        s = (z["time"] >= t1_) & (z["time"] < t1_ + 1.0)
        hm = float(np.sqrt(z["H-norm2"][s]).max())
        hb = float(np.sqrt(z["H-norm2"][z["time"] < t1_][-1]))
        txt.append(f"{hm:.2f}")
        src.append(f"{R[key]['dir']} refinement at t = {t1_:.2f}: {hb:.3f} before, {hm:.3f} max")
    rows.append((r"Largest $\|\Ham\|$ within $1M$ after the refinement to $\Delta x=h/4$, same four runs",
                 Cell(", ".join(txt), "os.z4c.user.hst; refinement time = second halving of dt in the dt column (the first, "
                                      "near t = 0.7 M, refines to h/2 and keeps the central reading exact): " + "; ".join(src)), NA))
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
    rows.append((r"$E_c$ over the cycloid in the $3M$ after the refinement to $h/4$: finest level; level cap with any, $\le1$ levels",
                 Cell("; ".join(txt), "os.nrpic.hst e_probe divided by the cycloid density at tau_probe "
                                      "(python/nrpic/oppenheimer_snyder.cycloid_rho), records before the first removal: " + "; ".join(src)), NA))
    G.append(("Dust collapse", rows))

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
                 Cell(r"$\approx0.01$ (" + FIG + ")", figsrc("st_dynamics.pdf", "y_c = 0.819 lapse panel, broad rise of about 0.01 "
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
    ts, as_ = smooth(t, a, 4.0)
    ext = zigzag(ts, as_, 0.08)
    names = ["start", "first maximum", "first minimum", "second maximum", "second minimum"]
    ex = [(float(t[0]), float(a[0]), "start")] + ext[1:5]
    here = "; ".join(f"{v:.2f}" + ("" if i == 0 else f" ({tt_:.0f})") for i, (tt_, v, _) in enumerate(ex))
    orig = r"0.56; 0.91 (230--320); 0.55--0.56 (450--490); 0.90 (670); 0.76 (830)"
    rows.append((r"Migration, $\alpha_c$ at the start and at its first extrema ($t/M$)",
                 Cell(here, f"{R[km]['dir']}, st.nrpic.hst alpha_probe ({R[km]['status']}, records to t = {t[-1]:.0f} M); "
                            f"start = first record; extrema of the 4 M boxcar, alternating with successive differences above 0.08: " +
                            ", ".join(f"{n} {v:.4f} at {tt_:.1f}" for n, (tt_, v, _) in zip(names, ex))),
                 Cell(orig + " (" + FIG + ")", figsrc("migration_central_evolution.pdf", "panel (a): start 0.56, plateau 0.91 at "
                                                     "230-320 M, minima 0.55-0.56 at 450-490 M, maximum 0.90 near 670 M, minimum 0.76 "
                                                     "near 830 M") + "; " + osrc("lapse rises from approximately 0.56 to 0.91", "text"))))
    o = R[km]["outcomes"]
    esc = ", ".join(f"{x:.0f}" for x in o["escape_times"])
    rows.append((r"Migration (run in progress, records to $t/M$ given): macroparticles removed by excision; leaving the domain (at $t/M$)",
                 Cell(f"{o['n_excised_end']}; {o['n_escaped_end']}" + (f" ({esc})" if esc else "") + f"; to {o['t_final']:.0f}",
                      f"{R[km]['dir']}, st.nrpic.hst columns n_excised and n_escaped of the last record, times at which "
                      f"n_escaped steps; np {o['np_start']} -> {o['np_end']}; domain half-width "
                      f"{R[km]['mesh']['domain_half_width']:g} M; run {R[km]['status']}"),
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
    G.append((r"Near-critical $y_c=0.756$", rows))
    return G


def write_outcomes(G):
    """Two floats in one file: test particles, horizon check and dust collapse; clusters."""
    parts = [(G[:4], "tab:outcomes",
              r"Measured quantities to which the text refers for test particles, the apparent-horizon check and "
              r"dust collapse, with the values of " + CITE + r" where it gives them (from its text, or read from its "
              r"figures). Masses in units of the total mass $M$, times in units of $M$; listed values follow the "
              r"order named in the first column."),
             (G[4:], "tab:outcomes_clusters",
              r"As Table~\ref{tab:outcomes}, for the relativistic clusters. Central lapse $\alpha_c$ in the eight "
              r"central cells; $\alpha_c(0)$ is its value at $t=0$.")]
    L, led = [], []
    for groups, label, caption in parts:
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
           "# tab:outcomes and tab:outcomes_clusters are the two floats of tab_outcomes.tex.", ""]
    OUT_LEDGER.write_text("\n".join(hdr + led) + "\n")
    print(f"{rel(OUT_JSON)}, {rel(OUT_LEDGER)} ({len(led)} lines), {rel(OUT_TAB)}/tab_setups.tex, tab_outcomes.tex")
    for key in RUNS:
        for n in R[key]["notes"]:
            print(f"NOTE {key}: {n}")


if __name__ == "__main__":
    main()
