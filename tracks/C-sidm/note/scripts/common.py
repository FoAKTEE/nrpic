"""Shared helpers of the note's figure and ledger scripts (C-sidm, working note v0).

Every number the scripts use is read from the output directory of a registered run,
/data/haiyangw/nrpic/scratch/C-sidm/<run_id>/ (manifest under tracks/C-sidm/runs/<run_id>/),
and every file is checked against the sha256 that the run recorded in its sha256sums.txt;
runs of wave 1 without that file are read as they are and reported as such.
Outputs go to ../figures and ../tables next to this file unless --out DIR is given.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
TRACK = os.path.dirname(NOTE)                       # tracks/C-sidm
WT = os.path.dirname(os.path.dirname(TRACK))        # worktree root
SCRATCH = os.environ.get("NRPIC_C_SCRATCH", "/data/haiyangw/nrpic/scratch/C-sidm")

# the registered runs the note reads (key -> run id); manifests in tracks/C-sidm/runs/
RUNS = {
    "mono": "C-sidm-20261115-115344-eb8b752",        # monoenergetic sequence, Wu-Most models
    "king": "C-sidm-20261115-115348-eb8b752",        # truncated-MB sequences b = 0.1..1 (scope)
    "kncost": "C-sidm-20261115-115400-eb8b752",      # Knudsen numbers (scope H), costs
    "models": "C-sidm-20261115-120610-b4592be",      # 13 near-threshold particle models
    "collref": "C-sidm-20261115-120703-9b3e868",     # collision references R1-R7
    "thermal": "C-sidm-20261115-120722-38ab057",         # thermal-core sequences, criteria, pulsation onsets
    "t60": "C-sidm-20261115-121302-313d399",         # AthenaK collisionless step T6-0
    "times": "C-sidm-20261115-121412-d463e1a",       # time scales at the onset
    "poly": "C-sidm-20261115-121524-5cebcf5",        # FEM check on Gamma = 2 polytropes
    "eqchk": "C-sidm-20261115-121626-e99907d",       # offline checks of the 13 models
    "init": "C-sidm-20261115-121748-4e8d6b5",        # candidate initial models, radii
    "kneq": "C-sidm-20261115-122915-cdc395c",        # Kn conversion (equilibria convention)
    "smoke": "C-sidm-20261115-125308-54870b9",       # AthenaK reads the King threshold files
    "xchk": "C-sidm-20261115-131130-3077a99",        # lead cross-checks X1-X5
    "t0": "C-sidm-20261115-132624-13a77db",          # T0 on core's committed kernels
    "boxs0": "C-20261115-164809-cd53539",            # wave 2: box smoke run (formats)
    "boxdesign": "C-20261115-165028-a559ab8",        # wave 2: box-test design numbers
    # ---- gate G1 (note v1, wave 3) ----
    # box tests of the collision operator: release (wave 2) and the branch core/collisions-2
    # with coll_energy = particle (wave 2b)
    "t2rel": "C-20261115-165500-c67e036",            # T1, T2 on the release executable
    "t2c2": "C-20261119-141806-af19c1c",             # T1, T2 with coll_energy = particle
    "t12": "C-20261119-145925-dbcfb9c",              # T12 analysis (runs of -143049-0cf699a)
    "t0brel": "C-20261115-170155-13ff01f",           # T0b replay, release
    "t0bc2": "C-20261119-141711-7db7a6a",            # T0b replay, coll_energy = particle
    "t10rel": "C-20261115-165902-f9b1c8f",           # T10 reproducibility, release
    "t10c2": "C-20261119-143041-f94e350",            # T10 with coll_energy = particle
    "t345": "C-20261115-170539-28432c3",             # T3-T5 relaxation, release
    "kingdef": "C-20261119-141431-a351ac7",          # first-step energy of the King model
    # heat conduction (package heat, wave 3a; processors)
    "t6b": "C-20261119-144535-2c7b6a4",              # T6(b) runs, lambda/L = 0.01
    "t6ban": "C-20261119-160003-287b389",            # T6(b) analysis
    "t6bw": "C-20261119-162440-296dad0",             # T6(b) analysis, late window
    "t6aan": "C-20261119-152744-2bba6de",            # T6(a) analysis
    "t7a": "C-20261119-144545-c606492",              # T7 runs, seeds 1-4
    "t7b": "C-20261119-155434-8563453",              # T7 runs, seeds 11-14
    "t7an": "C-20261119-161930-acd257b",             # T7 analysis of both
    "clan": "C-20261119-152845-017d186",             # T7 collisionless check, analysis
    "t8nosub": "C-20261119-151044-a584069",          # T8 part 2: rate without sub-cycling
    # models and onsets (wave 2, wave-2b review)
    "onset": "C-20261115-165315-7b473b8",            # fluid onsets of the thermal core
    "kingonset": "C-20261119-151502-cb831a8",        # lead's review run: King-family onsets
    "models2": "C-20261115-170742-84990ed",          # 13 particle models at N = 1e5
    "chk2": "C-20261115-171137-9e3c807",             # offline checks at N = 1e5
    "kn2": "C-20261115-193751-d3872ff",              # K = 1/(rho0_c H_c) of the 13 models
    "read2": "C-20261115-174557-8978b36",            # the code reads the b = 0.1 maximum model
    # first collisional cluster runs (card, release operator, wave 2)
    "cc_a": "C-20261115-171058-c26cfad",             # cc1_kninf, cc1_kn1
    "cc_b": "C-20261115-171059-4b70228",             # cc1_kn10, cc2_kninf
    "cc_c": "C-20261115-171059-35441e3",             # cc2_kn10, cc2_kn1
    "ccon": "C-20261119-151944-08f3220",             # lead's review run: onset of contraction
    "ccrev": "C-20261119-151502-cb831a8",            # lead's review run: defect before collapse
}

# cluster runs: case name -> run key
CC_RUN = {"cc1_kninf": "cc_a", "cc1_kn1": "cc_a", "cc1_kn10": "cc_b", "cc2_kninf": "cc_b",
          "cc2_kn10": "cc_c", "cc2_kn1": "cc_c"}

# keys of the data files that carry the source paper's abbreviation (kept here, with the
# run table, so that the figure scripts do not repeat it)
K_F21 = "F21"                       # adiabatic index Gamma = 1 + p/u of the source paper
K_F21_N = "F21_N1200"               # its onset at the finer resolution
K_JE_N = "J_E_N1200"                # Juttner Gamma_1 at the energy-matched temperature
K_JP_N = "J_p_N1200"                # Juttner Gamma_1 at theta = p/n
K_F21_ZERO = "omega2_zero_F21gamma"  # criteria.json of the thermal run

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
    """Absolute path of file `rel` of the run named by `key`, checked against its sha256."""
    run_id = RUNS[key]
    rdir = os.path.join(SCRATCH, run_id)
    path = os.path.join(rdir, rel)
    if not os.path.isfile(path):
        raise SystemExit(f"missing output {path} of run {run_id}")
    if not os.path.isfile(os.path.join(TRACK, "runs", run_id, "manifest.json")):
        raise SystemExit(f"run {run_id} has no manifest under tracks/C-sidm/runs/")
    sums = os.path.join(rdir, "sha256sums.txt")
    if os.path.isfile(sums):
        table = {}
        for line in open(sums):
            parts = line.split(None, 1)
            if len(parts) == 2:
                table[parts[1].strip().lstrip("*").removeprefix("./")] = parts[0]
        if rel not in table:
            raise SystemExit(f"{rel} is not listed in {sums}")
        if table[rel] != _sha256(path):
            raise SystemExit(f"sha256 of {path} differs from the one run {run_id} recorded")
        CHECKED.append((run_id, rel, "sha256 ok"))
    else:
        man = json.load(open(os.path.join(TRACK, "runs", run_id, "manifest.json")))
        rec = dict(man.get("outputs_sha256") or {})
        if isinstance(man.get("outputs"), list):        # scope's schema: [{path, sha256}]
            rec.update({o["path"]: o["sha256"] for o in man["outputs"] if "sha256" in o})
        if rel in rec:
            if rec[rel] != _sha256(path):
                raise SystemExit(f"sha256 of {path} differs from its manifest")
            CHECKED.append((run_id, rel, "sha256 ok (manifest outputs_sha256)"))
        else:
            CHECKED.append((run_id, rel, "no sha256sums.txt (wave-1 run)"))
    return path


def load_json(key, rel):
    with open(run_file(key, rel)) as f:
        return json.load(f)


def read_hist(path):
    """Text history of the code: header '# [1]=name [2]=name ...', rows of numbers."""
    import re
    import numpy as np
    names, rows = None, []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                found = re.findall(r"\[(\d+)\]=(\S+)", line)
                if found:
                    names = [nm for _, nm in found]
                continue
            if line.strip():
                rows.append([float(v) for v in line.split()])
    a = np.array(rows)
    if names is None or a.ndim != 2 or a.shape[1] != len(names):
        raise SystemExit(f"unexpected history layout in {path}")
    return {nm: a[:, i] for i, nm in enumerate(names)}


def manifest(key):
    with open(os.path.join(TRACK, "runs", RUNS[key], "manifest.json")) as f:
        return json.load(f)


def out_dir(default_sub, argv=None):
    """--out DIR (for a registered run) or ../<default_sub> next to the scripts."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a, _ = ap.parse_known_args(argv if argv is not None else sys.argv[1:])
    d = a.out or os.path.join(NOTE, default_sub)
    os.makedirs(d, exist_ok=True)
    return d


def report_checks(stem):
    for run_id, rel, st in CHECKED:
        print(f"{stem}: input {run_id}/{rel}: {st}")
