"""Lead's re-check of the packages of A-emd-pbh finished since 2026-11-15 (batch 2b, wave 3).

Predictions L1-L9: tracks/A-emd-pbh/JOURNAL.md, entry 2026-11-21T07:55Z (written first).
Each part reruns a finished package's analysis from its registered outputs into a
subdirectory of the run directory and compares every value with the registered run:

  L1 G1 verifier      stage/G1/verifier/run_all.py          vs A-20261119-142905-c813c01
  L2 g1close          g1close/scripts/check_findings.py     vs A-20261120-222454-d16dbc6
  L3 g1close          g1close/scripts/wave1_sha256.py       vs A-20261120-222620-0304d9d
  L4 gate review G1   stage/G1/gate_review/review_checks.py vs A-20261121-064537-2bcf310
  L5 szekeres         run_ltb_limit, run_dipole_order, run_error_budget
                      vs A-20261119-151501-9cff966, -151501-3e344a4, -153842-a1db5d6
  L6 szekeres         unit tests (pytest)
and reads raw outputs with its own code:
  L7 N32/szk.cstat.hst of A-20261119-152010-94a9461: first non-finite record
  L8 prep_ppc1.json of A-20261120-223422-8cc4241: deposit error and rest masses against N
  L9 run.log of A-20261120-223123-f436c39 (periodic P0L data) against prediction D3

Writes review_wave3.json and fig_review_wave3.{pdf,png} (style python/nrpic/figstyle.py)
into $NRPIC_RUN_DIR (or argv[1]). Usage: python tracks/A-emd-pbh/analysis/review_wave3.py
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.dirname(HERE)                      # tracks/A-emd-pbh
WT = os.path.dirname(os.path.dirname(TR))       # worktree root
SCR = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
OUT = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else None)
if not OUT:
    sys.exit("no output directory (NRPIC_RUN_DIR or argv[1])")
os.makedirs(OUT, exist_ok=True)
PY = sys.executable
RTOL = 1e-9
IGNORE_KEYS = {"wall_s", "walltime_s", "date_utc", "run_id", "commit", "elapsed_s", "date"}
REVIEWER_SHA = "4d72c147376253343704e474f59c1ffaab0c98f34356d5d7fae7f5c7d1f8eeae"

LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s, flush=True)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def compare(a, b, path=""):
    """Walk two JSON trees; return dict with counts and the largest relative difference."""
    st = {"numbers": 0, "strings": 0, "num_diff": 0, "str_diff": 0, "struct_diff": 0,
          "max_rel": 0.0, "first": []}

    def rec(x, y, p):
        if isinstance(x, dict) and isinstance(y, dict):
            for k in sorted(set(x) | set(y)):
                if k in IGNORE_KEYS:
                    continue
                if k not in x or k not in y:
                    st["struct_diff"] += 1
                    if len(st["first"]) < 12:
                        st["first"].append(f"{p}/{k}: key only on one side")
                    continue
                rec(x[k], y[k], f"{p}/{k}")
        elif isinstance(x, list) and isinstance(y, list):
            if len(x) != len(y):
                st["struct_diff"] += 1
                if len(st["first"]) < 12:
                    st["first"].append(f"{p}: lengths {len(x)} vs {len(y)}")
            for i, (u, v) in enumerate(zip(x, y)):
                rec(u, v, f"{p}[{i}]")
        elif isinstance(x, bool) or isinstance(y, bool) or x is None or y is None:
            st["strings"] += 1
            if x != y:
                st["str_diff"] += 1
                if len(st["first"]) < 12:
                    st["first"].append(f"{p}: {x!r} vs {y!r}")
        elif isinstance(x, (int, float)) and isinstance(y, (int, float)):
            st["numbers"] += 1
            fx, fy = float(x), float(y)
            if math.isnan(fx) and math.isnan(fy):
                return
            if fx == fy:
                return
            rel = abs(fx - fy) / max(abs(fx), abs(fy), 1e-300)
            st["max_rel"] = max(st["max_rel"], rel)
            if rel > RTOL and abs(fx - fy) > 1e-14:
                st["num_diff"] += 1
                if len(st["first"]) < 12:
                    st["first"].append(f"{p}: {fx!r} vs {fy!r}")
        elif isinstance(x, str) and isinstance(y, str):
            st["strings"] += 1
            if x != y:
                # paths of the run directory itself differ by construction
                if "/scratch/" in x and "/scratch/" in y:
                    return
                st["str_diff"] += 1
                if len(st["first"]) < 12:
                    st["first"].append(f"{p}: {x[:80]!r} vs {y[:80]!r}")
        else:
            st["struct_diff"] += 1
            if len(st["first"]) < 12:
                st["first"].append(f"{p}: types {type(x).__name__} vs {type(y).__name__}")

    rec(a, b, path)
    st["identical"] = st["num_diff"] == 0 and st["str_diff"] == 0 and st["struct_diff"] == 0
    return st


def run(cmd, cwd, logname, env=None):
    e = dict(os.environ)
    e.update({"OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2", "MKL_NUM_THREADS": "2"})
    if env:
        e.update(env)
    t0 = time.time()
    with open(os.path.join(OUT, logname), "w") as f:
        rc = subprocess.call(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, env=e)
    log(f"  {logname}: exit {rc} in {time.time() - t0:.1f} s")
    return rc


def load(p):
    with open(p) as f:
        return json.load(f)


R = {"predictions": "tracks/A-emd-pbh/JOURNAL.md entry 2026-11-21T07:55Z", "parts": {}}
CMPS = []   # (label, max_rel, identical)


def cmp_files(label, pairs):
    res = []
    for new, old in pairs:
        st = compare(load(new), load(old))
        st["new"], st["old"] = os.path.relpath(new, OUT), old
        res.append(st)
        CMPS.append((label + ":" + os.path.basename(new), st["max_rel"], st["identical"]))
        log(f"  {label} {os.path.basename(new)}: numbers {st['numbers']}, strings {st['strings']}, "
            f"diffs num/str/struct {st['num_diff']}/{st['str_diff']}/{st['struct_diff']}, "
            f"max rel {st['max_rel']:.2e}" + (f"; first: {st['first'][:3]}" if not st["identical"] else ""))
    return res


# ------------------------------------------------------------------ L1 verifier
log("L1 G1 verifier rerun")
old = os.path.join(SCR, "A-20261119-142905-c813c01")
d = os.path.join(OUT, "verifier")
rc = run([PY, os.path.join(TR, "stage/G1/verifier/run_all.py"), "--out", d],
         os.path.join(TR, "stage/G1/verifier"), "verifier.log")
files = ["ledger/ledger.json", "criteria/criteria.json", "newton/newton.json",
         "newton/newton_recomputed.json", "ball/ball.json", "ball/ball_recomputed.json"]
cm = cmp_files("L1", [(os.path.join(d, f), os.path.join(old, f)) for f in files])
tallies = {}
for f in ("ledger/ledger.json", "criteria/criteria.json", "newton/newton.json", "ball/ball.json"):
    rows = load(os.path.join(d, f))["rows"]
    t = {}
    for r in rows:
        t[r.get("verdict")] = t.get(r.get("verdict"), 0) + 1
    tallies[f] = t
log("  tallies", tallies)
ok = (rc == 0 and all(c["identical"] for c in cm)
      and tallies["ledger/ledger.json"] == {"CONFIRMED": 39, "NOT CONFIRMED": 1, "WRONG": 2}
      and tallies["criteria/criteria.json"] == {"CONFIRMED": 19}
      and tallies["newton/newton.json"] == {"CONFIRMED": 17}
      and tallies["ball/ball.json"] == {"CONFIRMED": 12})
R["parts"]["L1"] = {"exit": rc, "compare": cm, "tallies": tallies, "holds": ok}

# ------------------------------------------------------------------ L2, L3 g1close
log("L2 g1close check_findings rerun")
d = os.path.join(OUT, "g1close_findings")
rc = run([PY, os.path.join(TR, "g1close/scripts/check_findings.py"), "--out", d], WT, "g1close_findings.log")
cm = cmp_files("L2", [(os.path.join(d, "findings.json"),
                       os.path.join(SCR, "A-20261120-222454-d16dbc6", "findings.json"))])
R["parts"]["L2"] = {"exit": rc, "compare": cm, "holds": rc == 0 and cm[0]["identical"]}

log("L3 g1close wave1_sha256 rerun")
d = os.path.join(OUT, "wave1_integrity")
rc = run([PY, os.path.join(TR, "g1close/scripts/wave1_sha256.py"), "--out", d], WT, "wave1_integrity.log")
cm = cmp_files("L3", [(os.path.join(d, "integrity.json"),
                       os.path.join(SCR, "A-20261120-222620-0304d9d", "integrity.json"))])
lst_same = 0
lst_all = 0
oldd = os.path.join(SCR, "A-20261120-222620-0304d9d")
for fn in sorted(os.listdir(oldd)):
    if fn.endswith(".sha256"):
        lst_all += 1
        if open(os.path.join(oldd, fn)).read() == open(os.path.join(d, fn)).read():
            lst_same += 1
newi = load(os.path.join(d, "integrity.json"))
log(f"  listings identical {lst_same} of {lst_all}; n_files_listed_now {newi.get('n_files_listed_now')}, "
    f"n_mismatch {newi.get('n_mismatch')}, all_unchanged {newi.get('all_unchanged')}")
R["parts"]["L3"] = {"exit": rc, "compare": cm, "listings_identical": [lst_same, lst_all],
                    "n_files_listed_now": newi.get("n_files_listed_now"), "n_mismatch": newi.get("n_mismatch"),
                    "holds": rc == 0 and cm[0]["identical"] and lst_same == lst_all
                    and newi.get("n_files_listed_now") == 55 and newi.get("n_mismatch") == 0}

# ------------------------------------------------------------------ L4 gate review
log("L4 gate reviewer's checks rerun")
scr = os.path.join(TR, "stage/G1/gate_review/review_checks.py")
sh = sha256(scr)
d = os.path.join(OUT, "gate_review")
rc = run([PY, scr, d], WT, "gate_review.log")
cm = cmp_files("L4", [(os.path.join(d, "review_checks.json"),
                       os.path.join(SCR, "A-20261121-064537-2bcf310", "review_checks.json"))])
R["parts"]["L4"] = {"exit": rc, "script_sha256": sh, "sha_as_recorded": sh == REVIEWER_SHA,
                    "compare": cm, "holds": rc == 0 and sh == REVIEWER_SHA and cm[0]["identical"]}

# ------------------------------------------------------------------ L5, L6 szekeres
log("L5 szekeres reruns (figure directory redirected)")
SZ = os.path.join(TR, "szekeres")
cms = []
rcs = {}
for name, oldrun, js in (("run_ltb_limit", "A-20261119-151501-9cff966", "ltb_limit.json"),
                         ("run_dipole_order", "A-20261119-151501-3e344a4", "dipole_order.json"),
                         ("run_error_budget", "A-20261119-153842-a1db5d6", "error_budget.json")):
    d = os.path.join(OUT, "szekeres", name)
    os.makedirs(d, exist_ok=True)
    wrapper = ("import sys, runpy; sys.path.insert(0, {s!r}); import common; common.FIGDIR = {d!r}; "
               "sys.argv = [{p!r}]; runpy.run_path({p!r}, run_name='__main__')").format(
        s=os.path.join(SZ, "scripts"), d=d, p=os.path.join(SZ, "scripts", name + ".py"))
    rcs[name] = run([PY, "-c", wrapper], WT, f"szekeres_{name}.log", env={"NRPIC_RUN_DIR": d})
    cms += cmp_files("L5", [(os.path.join(d, js), os.path.join(SCR, oldrun, js))])
R["parts"]["L5"] = {"exit": rcs, "compare": cms,
                    "holds": all(v == 0 for v in rcs.values()) and all(c["identical"] for c in cms)}

log("L6 szekeres unit tests")
rc = run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", os.path.join(SZ, "tests")], SZ, "szekeres_pytest.log")
txt = open(os.path.join(OUT, "szekeres_pytest.log")).read()
m = re.search(r"(\d+) passed", txt)
f = re.search(r"(\d+) failed", txt)
npass, nfail = (int(m.group(1)) if m else 0), (int(f.group(1)) if f else 0)
log(f"  passed {npass}, failed {nfail}")
R["parts"]["L6"] = {"exit": rc, "passed": npass, "failed": nfail, "holds": npass == 15 and nfail == 0}

# ------------------------------------------------------------------ L7 own reading of N32 history
log("L7 Szekeres N32 constraint history (own reader)")
hist = {}
for n in ("N32", "N64"):
    p = os.path.join(SCR, "A-20261119-152010-94a9461", n, "szk.cstat.hst")
    rows = []
    for line in open(p):
        if line.startswith("#") or not line.strip():
            continue
        rows.append([float(v) for v in line.split()])
    a = np.array(rows)
    bad = ~np.isfinite(a[:, 1:]).all(axis=1) | (np.abs(a[:, 1:]) > 1e300).any(axis=1)
    t_bad = float(a[bad, 0][0]) if bad.any() else None
    good = a[~bad]
    hist[n] = {"t": a[:, 0].tolist(), "Hmax": [x if math.isfinite(x) and abs(x) < 1e300 else None for x in a[:, 8]],
               "Hmean": [x if math.isfinite(x) and abs(x) < 1e300 else None for x in a[:, 9]],
               "first_bad_t": t_bad, "last_good_t": float(good[-1, 0]) if len(good) else None,
               "records": int(len(a))}
    log(f"  {n}: {len(a)} records, last finite at tau = {hist[n]['last_good_t']}, first bad at tau = {t_bad}")
tb = hist["N32"]["first_bad_t"]
R["parts"]["L7"] = {"N32": {k: v for k, v in hist["N32"].items() if k not in ("t", "Hmax", "Hmean")},
                    "N64": {k: v for k, v in hist["N64"].items() if k not in ("t", "Hmax", "Hmean")},
                    "holds": tb is not None and 24.0 < tb <= 28.0}

# ------------------------------------------------------------------ L8 Szekeres files
log("L8 Szekeres file preparation (prep_ppc1.json)")
pj = load(os.path.join(SCR, "A-20261120-223422-8cc4241", "prep_ppc1.json"))
Ns, mass, e0 = [], [], []
for k, v in sorted(pj["members"].items(), key=lambda kv: kv[1]["N"]):
    Ns.append(v["N"])
    mass.append(v["mass_total"])
    e0.append(max(r["max"] for r in v["predicted_E0_rel_err"].values()))
mass = np.array(mass)
dm = np.abs(np.diff(mass))
spread = float((mass.max() - mass.min()) / mass.mean())
log(f"  N {Ns}; mass {mass.tolist()}; |successive differences| {dm.tolist()}; max E0 rel err {max(e0):.2e}")
R["parts"]["L8"] = {"N": Ns, "mass_total": mass.tolist(), "successive_abs_diff": dm.tolist(),
                    "relative_spread": spread, "max_E0_rel_err": e0,
                    "holds": max(e0) < 1e-14 and spread < 1e-2 and bool(np.all(np.diff(dm) < 0))}

# ------------------------------------------------------------------ L9 periodic P0L data
log("L9 periodic P0L data against prediction D3")
txt = open(os.path.join(SCR, "A-20261120-223123-f436c39", "P0_mu0.3.log")).read()
outer = [(int(a), int(b), float(c), float(e)) for a, b, c, e in
         re.findall(r"outer (\d+): inner iterations (\d+), residual ([0-9.e+-]+), change of psi ([0-9.e+-]+)", txt)]


def val(key):
    m = re.search(rf"^{key}: ([0-9.e+-]+)", txt, re.M)
    return float(m.group(1)) if m else None


v = {k: val(k) for k in ("delta_N_max", "alpha_min", "solve_change_over_dictionary_c",
                         "max_hamiltonian_residual", "max_momentum_residual", "max_displacement_over_h")}
v["max_inner"] = max(o[1] for o in outer)
v["max_outer_residual"] = max(o[2] for o in outer)
log("  ", v)
holds = (max(v["max_hamiltonian_residual"], v["max_momentum_residual"], v["max_outer_residual"]) < 1e-10
         and 0.05 <= v["solve_change_over_dictionary_c"] <= 0.2 and 0.10 <= v["delta_N_max"] <= 0.14
         and 0.78 <= v["alpha_min"] <= 0.82 and v["max_inner"] < 60)
R["parts"]["L9"] = {"values": v, "outer": outer, "holds": holds}

# ------------------------------------------------------------------ figure
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
import matplotlib.ticker  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

fs.use_style()
fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4))
a0 = ax[0, 0]
labels = [c[0].replace(".json", "") for c in CMPS]
FLOOR = 1e-16
vals = [max(c[1], FLOOR) for c in CMPS]
y = np.arange(len(labels))
for yi, v, c in zip(y, vals, CMPS):
    col = fs.PAL["blue"] if c[2] else fs.PAL["red"]
    a0.plot([FLOOR / 10, v], [yi, yi], color=col, lw=1.0)
    a0.plot([v], [yi], "o", color=col, ms=5)
    a0.text(v * 3, yi, "identical" if c[1] == 0 else f"{c[1]:.1e}", va="center", fontsize=6)
a0.axvline(RTOL, **fs.GUIDE)
a0.text(RTOL * 1.5, len(labels) - 0.6, "tolerance 1e-9", fontsize=6)
a0.set_xscale("log")
a0.set_xlim(1e-17, 1e-3)
a0.set_yticks(y)
a0.set_yticklabels(labels, fontsize=6)
a0.invert_yaxis()
a0.set_xlabel("largest relative difference to the registered run")
a0.set_title("(a) reruns from registered outputs", fontsize=8)

a1 = ax[0, 1]
for n, c in (("N32", fs.PAL["blue"]), ("N64", fs.PAL["red"])):
    t = np.array(hist[n]["t"])
    hm = np.array([np.nan if x is None else x for x in hist[n]["Hmax"]])
    a1.semilogy(t, hm, "o-", color=c, ms=3, label=f"{n}: H_max")
fs.band(a1, [24, 28], [1e-6, 1e-6], [1e6, 1e6], fs.PAL["yellow"], alpha=0.25)
if tb is not None:
    a1.axvline(tb, **fs.MASK_LINE)
a1.set_ylim(1e-5, 1e3)
a1.set_xlabel("tau (proper time of the dust)")
a1.set_ylabel("largest |H| on the mesh")
a1.set_title(f"(b) Szekeres N32: first non-finite at tau = {tb}", fontsize=8)
a1.text(18.5, 2e2, "claim: 24-28", fontsize=6)
a1.legend(fontsize=7)

a2 = ax[1, 0]
a2.loglog(Ns[1:], dm, "o-", color=fs.PAL["blue"], label="|M(N) - M(N/2)| (total rest mass)")
a2.loglog(Ns, e0, "s-", color=fs.PAL["red"], label="max predicted rel. error of E at t = 0")
a2.set_xlabel("N (cells per side)")
a2.set_ylabel("value")
a2.set_xticks(Ns)
a2.set_xticklabels([str(n) for n in Ns])
a2.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
a2.legend(fontsize=7)
a2.set_title("(c) Szekeres files, eps = 0.2, one particle per cell", fontsize=8)

a3 = ax[1, 1]
io = np.array([o[0] for o in outer])
a3.semilogy(io, [o[2] for o in outer], "o-", color=fs.PAL["blue"], label="residual of the inner solve")
a3.semilogy(io, [o[3] for o in outer], "s-", color=fs.PAL["red"], label="change of psi")
a3.axhline(1e-10, **fs.GUIDE)
a3b = a3.twinx()
a3b.plot(io, [o[1] for o in outer], "^", color=fs.PAL["green"], ms=4)
a3b.set_ylim(0, 65)
a3b.axhline(60, **fs.MASK_LINE)
a3b.set_ylabel("inner iterations (limit 60)", color=fs.PAL["green"])
a3.set_xlabel("outer iteration")
a3.legend(fontsize=6, loc="center left", bbox_to_anchor=(0.0, 0.3))
a3.set_title("(d) periodic P0L data (mu = 0.3, e = 0): solve against D3", fontsize=8)
fig.tight_layout()
figs = fs.save(fig, os.path.join(OUT, "fig_review_wave3"))
R["figures"] = [os.path.basename(p) for p in figs]
R["summary"] = {k: v["holds"] for k, v in R["parts"].items()}
log("summary", R["summary"])
with open(os.path.join(OUT, "review_wave3.json"), "w") as f:
    json.dump(R, f, indent=1)
with open(os.path.join(OUT, "review_wave3.log"), "w") as f:
    f.write("\n".join(LOG) + "\n")
