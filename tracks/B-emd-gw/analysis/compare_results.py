"""Compare the reruns of lead_recheck.sh with the committed or original results.

    python3 compare_results.py RUN_DIR

Numbers are compared leaf by leaf in the JSON trees: a leaf passes when
|a - b| <= RTOL * max(|a|, |b|) or |a - b| <= ATOL (rounding-level values). AthenaK outputs
are compared byte by byte (athena.log, stdout and checksum files excluded). Writes
RUN_DIR/compare.json and prints a summary; exit status 0 always (the lead reads it).
"""
import filecmp
import json
import math
import os
import sys

RTOL = 1e-8
ATOL = 1e-13
SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"


def leaves(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{path}/{k}")
    elif isinstance(x, (list, tuple)):
        for i, v in enumerate(x):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, x


def cmp_json(a_path, b_path):
    with open(a_path) as f:
        a = dict(leaves(json.load(f)))
    with open(b_path) as f:
        b = dict(leaves(json.load(f)))
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    n = same = 0
    worst = []
    for k in sorted(set(a) & set(b)):
        x, y = a[k], b[k]
        n += 1
        if isinstance(x, bool) or isinstance(y, bool) or not (
                isinstance(x, (int, float)) and isinstance(y, (int, float))):
            if x == y:
                same += 1
            else:
                worst.append((math.inf, k, str(x)[:60], str(y)[:60]))
            continue
        if x == y or (isinstance(x, float) and isinstance(y, float)
                      and math.isnan(x) and math.isnan(y)):
            same += 1
            continue
        d = abs(x - y)
        rel = d/max(abs(x), abs(y))
        ok = d <= RTOL*max(abs(x), abs(y)) or d <= ATOL
        worst.append((rel if not ok else -rel, k, x, y))
    bad = [w for w in worst if w[0] > 0]
    small = [w for w in worst if w[0] <= 0]
    return {
        "rerun": a_path, "reference": b_path, "leaves": n, "identical": same,
        "within_tolerance": len(small), "outside_tolerance": len(bad),
        "max_rel_within_tolerance": max([-w[0] for w in small], default=0.0),
        "keys_only_in_rerun": only_a[:20], "keys_only_in_reference": only_b[:20],
        "worst_outside": [(w[1], w[2], w[3], w[0]) for w in sorted(bad, reverse=True)[:12]],
    }


def cmp_tree(new, old):
    skip = ("athena.log", "stdout.txt", "sha256sums.txt", "time.txt")
    res = {"identical": 0, "different": [], "missing_in_rerun": []}
    for root, _, files in os.walk(old):
        for fn in files:
            if fn in skip or fn.endswith(".log"):
                continue
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, old)
            q = os.path.join(new, rel)
            if not os.path.exists(q):
                res["missing_in_rerun"].append(rel)
            elif filecmp.cmp(p, q, shallow=False):
                res["identical"] += 1
            else:
                res["different"].append(rel)
    return res


def main():
    run = sys.argv[1]
    T = os.path.join(run, "export", "tracks", "B-emd-gw")
    pairs = {
        "scope/check_item3": ("scope_item3/check_item3.json", f"{T}/scope/results/check_item3.json"),
        "scope/crossed_waves_tt": ("scope_tt/crossed_waves_tt.json",
                                   f"{T}/scope/results/crossed_waves_tt.json"),
        "scope/regime_estimates": ("scope_regime/regime_estimates.json",
                                   f"{T}/scope/results/regime_estimates.json"),
        "gw_diag/results_tt": ("gw_tt/results_tt.json",
                               f"{SCR}/B-emd-gw-20261115-115206-2e6c497/results_tt.json"),
        "gw_diag/results_weyl": ("gw_weyl/results_weyl.json",
                                 f"{SCR}/B-emd-gw-20261115-115637-175cbca/results_weyl.json"),
        "gw_diag/results_athenak": ("gw_athenak/results_athenak.json",
                                    f"{SCR}/B-emd-gw-20261115-120128-7dfaa38/results_athenak.json"),
        "baseline/baseline_results": ("baseline/baseline_results.json",
                                      f"{T}/baseline/results/baseline_results.json"),
        "verify_cosmo/flrw_recheck": ("vc_flrw/flrw_recheck.json",
                                      f"{T}/verify_cosmo/results/flrw_recheck.json"),
        "verify_cosmo/pancake": ("vc_pancake/pancake.json", f"{T}/verify_cosmo/results/pancake.json"),
        "verify_cosmo/pancake_profiles": ("vc_pancake/pancake_profiles.json",
                                          f"{T}/verify_cosmo/results/pancake_profiles.json"),
    }
    committed = os.path.join(run, "pz_tables_committed")
    if os.path.isdir(committed):
        for fn in sorted(os.listdir(committed)):
            if fn.endswith(".json"):
                pairs[f"periodic_z4c/{fn}"] = (f"{T}/periodic_z4c/tables/{fn}",
                                               os.path.join(committed, fn))
    out = {"rtol": RTOL, "atol": ATOL, "json": {}, "text": {}, "athenak": {}, "steps": {}}
    for name, (a, b) in pairs.items():
        a = a if os.path.isabs(a) else os.path.join(run, a)
        if not os.path.exists(a) or not os.path.exists(b):
            out["json"][name] = {"error": f"missing: rerun {os.path.exists(a)}, "
                                          f"reference {os.path.exists(b)}"}
            continue
        out["json"][name] = cmp_json(a, b)
    if os.path.isdir(committed):
        for fn in sorted(os.listdir(committed)):
            if fn.endswith(".md"):
                with open(os.path.join(committed, fn)) as f:
                    x = f.read()
                with open(f"{T}/periodic_z4c/tables/{fn}") as f:
                    y = f.read()
                out["text"][f"periodic_z4c/{fn}"] = "identical" if x == y else "different"
    orig = {"lw_x_prod_N16": "B-emd-gw-20261115-113219-0ea0f74",
            "lw_x_prod_N32": "B-emd-gw-20261115-113220-0ea0f74",
            "lw3d_check_diag": "B-emd-gw-20261115-113216-0ea0f74",
            "gauge_nl_conformal_N64": "B-emd-gw-20261115-115139-42096b9"}
    for name, rid in orig.items():
        new = os.path.join(run, "athenak", name)
        out["athenak"][name] = cmp_tree(new, os.path.join(SCR, rid)) if os.path.isdir(new) \
            else {"error": "no rerun directory"}
    for fn in ("rc.txt", "rc_athenak.txt"):
        p = os.path.join(run, fn)
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    k, v = line.split()
                    out["steps"][k] = int(v)
    with open(os.path.join(run, "compare.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    print("steps (return codes):", out["steps"])
    for name, r in out["json"].items():
        if "error" in r:
            print(f"{name:34s} ERROR {r['error']}")
            continue
        print(f"{name:34s} leaves {r['leaves']:6d} identical {r['identical']:6d} "
              f"tol {r['within_tolerance']:5d} (max rel {r['max_rel_within_tolerance']:.1e}) "
              f"OUT {r['outside_tolerance']:4d} only-rerun {len(r['keys_only_in_rerun'])} "
              f"only-ref {len(r['keys_only_in_reference'])}")
        for w in r["worst_outside"][:5]:
            print("    ", w)
    for name, r in out["text"].items():
        print(f"{name:34s} {r}")
    for name, r in out["athenak"].items():
        print(f"athenak {name:26s} {r if 'error' in r else (r['identical'], r['different'][:5], r['missing_in_rerun'][:5])}")


if __name__ == "__main__":
    main()
