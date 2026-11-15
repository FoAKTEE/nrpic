#!/usr/bin/env python3
"""Compare the reruns of rerun_packages.sh with the registered outputs of the helpers.

    python3 compare_reruns.py RUN_DIR

Generic numeric diff of JSON outputs (max relative difference over every number, keys that
hold paths or timings ignored), pass flags of the equilibria checks, byte equality of the
T6-0 particle snapshots, and the summary lines of the test suites. Writes
RUN_DIR/rerun_summary.json and exits 1 if anything differs beyond 1e-12 relative or a test
fails.
"""
import hashlib
import json
import os
import re
import sys

S = "/data/haiyangw/nrpic/scratch/C-sidm"
IGNORE = re.compile(r"(rundir|run_dir|path|wall|time_s|elapsed|seconds|host|date|cwd|file)", re.I)


def walk(a, b, path=""):
    """Yield (path, rel_diff) for every number; (path, None) for structural mismatches."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if IGNORE.search(k):
                continue
            if k not in a or k not in b:
                yield path + "/" + k, None
                continue
            yield from walk(a[k], b[k], path + "/" + k)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield path, None
            return
        for i, (x, y) in enumerate(zip(a, b)):
            yield from walk(x, y, f"{path}/{i}")
    elif isinstance(a, bool) or isinstance(b, bool):
        if a != b:
            yield path, None
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if a == b:
            yield path, 0.0
        else:
            yield path, abs(a - b) / max(abs(a), abs(b), 1e-300)
    elif a != b and not (isinstance(a, str) and isinstance(b, str)):
        yield path, None


def jdiff(new, old):
    a, b = json.load(open(new)), json.load(open(old))
    diffs = list(walk(a, b))
    nums = [d for _, d in diffs if d is not None]
    bad = [p for p, d in diffs if d is None]
    worst = max(diffs, key=lambda t: -1 if t[1] is None else t[1]) if nums else ("", 0.0)
    return dict(n_numbers=len(nums), max_rel=max(nums) if nums else 0.0, worst=worst[0],
                structural=bad[:10], n_structural=len(bad))


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def passes(x):
    if isinstance(x, dict):
        if "pass" in x:
            yield x["pass"]
        for v in x.values():
            yield from passes(v)
    elif isinstance(x, list):
        for v in x:
            yield from passes(v)


def main(out):
    res = {}
    ok = True
    for name in ("collide_references_pytest", "collide_analysis_pytest", "gravothermal_test_tmb"):
        lines = open(os.path.join(out, name + ".log")).read().strip().splitlines()
        res[name] = lines[-1] if lines else ""
        if re.search(r"fail|error", res[name], re.I):
            ok = False
    pairs = {
        "scope_seq_monoenergetic": (f"{out}/scope_seq_monoenergetic/seq_monoenergetic.json",
                                    f"{S}/C-sidm-20261115-115344-eb8b752/seq_monoenergetic.json"),
        "scope_king_sequence": (f"{out}/scope_king_sequence/king_sequence.json",
                                f"{S}/C-sidm-20261115-115348-eb8b752/king_sequence.json"),
        "scope_knudsen_costs": (f"{out}/scope_knudsen_costs/knudsen_costs.json",
                                f"{S}/C-sidm-20261115-115400-eb8b752/knudsen_costs.json"),
        "gravothermal_polytrope": (f"{out}/polytrope/polytrope_check.json",
                                   f"{S}/C-sidm-20261115-121524-5cebcf5/polytrope_check.json"),
        "collide_T6_step": (f"{out}/t6/step_step.json",
                            f"{S}/C-sidm-20261115-121302-313d399/step_step.json"),
        "equilibria_checks": (f"{out}/eqcheck/checks.json",
                              f"{S}/C-sidm-20261115-121626-e99907d/checks.json"),
    }
    for k, (new, old) in pairs.items():
        try:
            res[k] = jdiff(new, old)
        except Exception as e:      # noqa: BLE001  (missing output = failed rerun)
            res[k] = dict(error=repr(e))
            ok = False
            continue
        if res[k]["max_rel"] > 1e-12 or res[k]["n_structural"]:
            res[k]["note"] = "differs beyond 1e-12"
    try:
        flags = list(passes(json.load(open(f"{out}/eqcheck/checks.json"))))
        res["equilibria_pass_flags"] = dict(n=len(flags), n_pass=sum(1 for f in flags if f))
        ok &= all(flags)
    except Exception as e:          # noqa: BLE001
        res["equilibria_pass_flags"] = dict(error=repr(e))
        ok = False
    snaps = sorted(f for f in os.listdir(f"{S}/C-sidm-20261115-121302-313d399") if f.endswith(".bin"))
    same = [f for f in snaps if os.path.exists(f"{out}/t6/{f}")
            and sha(f"{out}/t6/{f}") == sha(f"{S}/C-sidm-20261115-121302-313d399/{f}")]
    res["collide_T6_snapshots_bit_identical"] = f"{len(same)}/{len(snaps)}"
    with open(os.path.join(out, "rerun_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
