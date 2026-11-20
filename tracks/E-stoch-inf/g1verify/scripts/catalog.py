"""Catalogue of the G1 runs (g1verify): name -> run id, directory, options from the lists.

The options come from the list files the manifests name (ladder/inputs/*.list); check_infra
compares them with the copies in the run directories and the sha256 of the manifests.
"""
import os
import json
import hashlib

ROOT = "/data/haiyangw/nrpic"
WT = os.path.join(ROOT, "wt/E-stoch-inf")
TRK = os.path.join(WT, "tracks/E-stoch-inf")
SCR = os.path.join(ROOT, "scratch/E-stoch-inf")
LISTS = os.path.join(TRK, "ladder/inputs")

JOBS = {
    "jobA.list": ("E-20261115-172618-f948386", "card"),
    "jobB.list": ("E-20261115-172629-312a82c", "card"),
    "jobC.list": ("E-20261115-172625-416fec0", "card"),
    "proc32.list": ("E-20261115-172636-ce98836", "proc"),
    "proc64.list": ("E-20261115-173719-e810503", "proc"),
    "a6proc.list": ("E-20261119-142317-c851f27", "proc"),
}

BASE_DEFAULTS = {"scalar_field/noise_mode_scale": "1.0", "scalar_field/noise_pi_sign": "1.0",
                 "scalar_field/dump_metric": "true", "time/cfl_number": "0.25"}


def parse_list(path):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            tok = line.split()
            args = dict(BASE_DEFAULTS)
            for t in tok[2:]:
                k, v = t.split("=", 1)
                args[k] = v
            out.append((tok[0], tok[1], args))
    return out


def catalog():
    runs = {}
    for lst, (rid, kind) in JOBS.items():
        for name, deck, args in parse_list(os.path.join(LISTS, lst)):
            key = name + "_proc" if lst == "proc64.list" else name
            N = int(args["mesh/nx1"])
            runs[key] = dict(name=name, run_id=rid, kind=kind, list=lst, deck=deck,
                             dir=os.path.join(SCR, rid, name), N=N,
                             nmax2=int(args["scalar_field/noise_nmax2"]),
                             mode_file=args["scalar_field/noise_mode_file"],
                             scale=float(args["scalar_field/noise_mode_scale"]),
                             pi_sign=float(args["scalar_field/noise_pi_sign"]),
                             metric=args["scalar_field/dump_metric"] == "true",
                             cfl=float(args["time/cfl_number"]),
                             tlim=float(args["time/tlim"]), args=args)
    return runs


def sha256(path, bufsize=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def manifest(run_id):
    with open(os.path.join(TRK, "runs", run_id, "manifest.json")) as f:
        return json.load(f)


def sums(run_id):
    """sha256sums.txt of a run directory as {relative path: hash}."""
    p = os.path.join(SCR, run_id, "sha256sums.txt")
    out = {}
    with open(p) as f:
        for line in f:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                out[parts[1].lstrip("*").lstrip("./")] = parts[0]
    return out
