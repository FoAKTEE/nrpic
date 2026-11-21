"""V7 (A7): bit-identity of the noise unit-test dumps across MeshBlock layouts and restart,
checked on the files themselves (g1verify, JOURNAL entry 3, P-V7a), and the cost of one
256^3 realisation from the manifests (P-V7b).

usage: v7.py OUTDIR
Runs (release core-v0.3, inputs tracks/E-stoch-inf/analysis/inputs/u64/):
  card  E-20261115-170645-3b21217: U1 (1 MeshBlock), U2 (8), U3 (64), 64^3 x 300 cycles
  proc  E-20261115-170727-d15df12: U2 and U4 (= U2 restarted at cycle 150)
  card  E-20261115-180526-6b68c33: U4 (card U2 restarted at cycle 150)
Every dump is read whole, sequentially, its sha256 compared with the run's sha256sums.txt,
assembled by logical location, and compared bit for bit (uint64 views) per variable. The
lockstep mode files (.modes, text) are compared byte for byte; the records (.sf.hst)
column by column (box means are reductions, so their last bits may depend on the layout).
Also, for information: card against processor (U2), and the slow-roll L64p on the card
(E-20261115-172625-416fec0) against L64p on processors (E-20261115-173719-e810503).
"""
import os
import sys
import json
import hashlib
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nrsf, catalog as C  # noqa: E402

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
SCR = C.SCR
CARD, PROC, CARD4 = "E-20261115-170645-3b21217", "E-20261115-170727-d15df12", "E-20261115-180526-6b68c33"
res = dict(sha={}, layouts={}, restart={}, cross_platform={}, modes={}, records={})
_sums = {}


def sums(rid):
    if rid not in _sums:
        _sums[rid] = C.sums(rid)
    return _sums[rid]


def load(rid, sub, fname):
    p = os.path.join(SCR, rid, sub, fname)
    digest = C.sha256(p)
    rel = os.path.join(sub, fname)
    ok = sums(rid).get(rel) == digest
    res["sha"][f"{rid}/{rel}"] = ok
    h = nrsf.header(p)
    f = nrsf.read(p, h["names"], h)
    return f, h


def bitdiff(a, b):
    return {n: int(np.sum(a[n].view(np.uint64) != b[n].view(np.uint64))) for n in a}


def reldiff(a, b):
    o = {}
    for n in a:
        s = max(float(np.max(np.abs(a[n]))), 1e-300)
        o[n] = float(np.max(np.abs(a[n] - b[n]))) / s
    return o


def textsame(p, q):
    with open(p, "rb") as f, open(q, "rb") as g:
        return f.read() == g.read()


# ----------------------------------------------------------------- layouts (card U1/U2/U3)
for d in range(4):
    fn = f"u.sf.{d:05d}.dump"
    f1, h1 = load(CARD, "U1", fn)
    row = dict(time=h1["time"], cycle=h1["cycle"], nmb={"U1": h1["nmb"]}, nvar=h1["nvar"],
               names=h1["names"])
    for u in ("U2", "U3"):
        fu, hu = load(CARD, u, fn)
        row["nmb"][u] = hu["nmb"]
        bd = bitdiff(f1, fu)
        row[f"U1_vs_{u}_differing"] = bd
        row[f"U1_vs_{u}_identical"] = all(v == 0 for v in bd.values())
        row[f"U1_vs_{u}_ncells"] = int(f1["phi"].size)
    # the noise fields are not trivially zero
    row["noise_rms"] = {n: float(np.sqrt(np.mean(f1[n] ** 2))) for n in f1 if n.startswith("noise")}
    res["layouts"][fn] = row
    mf = fn.replace(".dump", ".modes")
    res["modes"][f"layout {mf}"] = {u: textsame(os.path.join(SCR, CARD, "U1", mf), os.path.join(SCR, CARD, u, mf))
                                    for u in ("U2", "U3")}

# ----------------------------------------------------------------- restart
for label, (ra, sa), (rb, sb) in (("proc", (PROC, "U2"), (PROC, "U4")), ("card", (CARD, "U2"), (CARD4, "U4"))):
    rr = {}
    for d in (2, 3):
        fn = f"u.sf.{d:05d}.dump"
        fa, ha = load(ra, sa, fn)
        fb, hb = load(rb, sb, fn)
        bd = bitdiff(fa, fb)
        rr[fn] = dict(time_a=ha["time"], time_b=hb["time"], cycle_a=ha["cycle"], cycle_b=hb["cycle"],
                      nmb_a=ha["nmb"], nmb_b=hb["nmb"], differing=bd, identical=all(v == 0 for v in bd.values()),
                      time_bits_equal=bool(np.float64(ha["time"]).view(np.uint64) == np.float64(hb["time"]).view(np.uint64)))
        mf = fn.replace(".dump", ".modes")
        res["modes"][f"restart {label} {mf}"] = textsame(os.path.join(SCR, ra, sa, mf), os.path.join(SCR, rb, sb, mf))
    res["restart"][label] = rr

# ----------------------------------------------------------------- card vs processor (information)
cp = {}
for d in range(4):
    fn = f"u.sf.{d:05d}.dump"
    fa, ha = load(CARD, "U2", fn)
    fb, hb = load(PROC, "U2", fn)
    bd = bitdiff(fa, fb)
    cp[fn] = dict(identical=all(v == 0 for v in bd.values()), differing_total=int(sum(bd.values())),
                  max_reldiff=reldiff(fa, fb))
res["cross_platform"]["U2 card vs proc"] = cp
runs = C.catalog()
sr = {}
ca, pr = runs["L64p"], runs["L64p_proc"]
for pa, pb in zip(nrsf.dumps(ca["dir"]), nrsf.dumps(pr["dir"])):
    ha, hb = nrsf.header(pa), nrsf.header(pb)
    if ha["cycle"] != hb["cycle"]:
        continue
    names = ["phi", "Pi", "chi", "K", "gxx", "Axx"]
    fa, fb = nrsf.read(pa, names, ha), nrsf.read(pb, names, hb)
    pert = {}
    for n in names:
        da, db = fa[n] - fa[n].mean(), fb[n] - fb[n].mean()
        pert[n] = float(np.max(np.abs(da - db)) / max(np.max(np.abs(da)), 1e-300))
    sr[os.path.basename(pa)] = dict(time=ha["time"], cycle=ha["cycle"],
                                    identical=all(np.array_equal(fa[n].view(np.uint64), fb[n].view(np.uint64)) for n in names),
                                    max_reldiff_of_perturbation=pert)
res["cross_platform"]["L64p card vs proc"] = sr

# ----------------------------------------------------------------- records
for label, (ra, sa), (rb, sb) in (("layout U1-U2", (CARD, "U1"), (CARD, "U2")), ("layout U1-U3", (CARD, "U1"), (CARD, "U3")),
                                  ("restart proc", (PROC, "U2"), (PROC, "U4")), ("restart card", (CARD, "U2"), (CARD4, "U4"))):
    ca_, da = nrsf.read_record(os.path.join(SCR, ra, sa, "u.sf.hst"))
    cb_, db = nrsf.read_record(os.path.join(SCR, rb, sb, "u.sf.hst"))
    ta, tb = da[:, 0], db[:, 0]
    common = [t for t in tb if np.any(ta == t)]
    ia = [int(np.where(ta == t)[0][0]) for t in common]
    ib = [int(np.where(tb == t)[0][0]) for t in common]
    A, B = da[ia], db[ib]
    same = (A == B)
    den = np.maximum(np.abs(A), 1e-300)
    res["records"][label] = dict(rows_compared=len(common), all_equal=bool(same.all()),
                                 columns_differing=[ca_[j] for j in range(A.shape[1]) if not same[:, j].all()],
                                 max_reldiff=float(np.max(np.abs(A - B) / den)))

# ----------------------------------------------------------------- cost from the manifests
cost = {}
for rid in ("E-20261115-172618-f948386", "E-20261115-172629-312a82c", "E-20261115-172625-416fec0",
            "E-20261115-172636-ce98836", "E-20261115-173719-e810503"):
    m = C.manifest(rid)
    keep = {k: m.get(k) for k in ("status", "exit_code", "launcher", "kind", "resources", "slurm", "started",
                                  "ended", "finished")}
    cost[rid] = {k: v for k, v in keep.items() if v is not None}
    cost[rid]["entries"] = [e.get("name") for e in (m.get("batch_entries") or [])]
    st = os.path.join(SCR, rid, "batch.list.status")
    if os.path.exists(st):
        cost[rid]["batch_status"] = open(st).read()[-3000:]
res["cost_manifests"] = cost
for name in ("P256",):
    lg = os.path.join(runs[name]["dir"], "athena.log")
    if os.path.exists(lg):
        with open(lg) as f:
            res["cost_P256_athena_log_tail"] = f.read()[-2500:]

res["sha_all_ok"] = bool(all(res["sha"].values()))
res["layouts_all_identical"] = bool(all(r[f"U1_vs_{u}_identical"] for r in res["layouts"].values() for u in ("U2", "U3")))
res["restart_all_identical"] = bool(all(x["identical"] for r in res["restart"].values() for x in r.values()))
with open(os.path.join(out, "v7.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps({k: res[k] for k in ("sha_all_ok", "layouts_all_identical", "restart_all_identical", "modes", "records")},
                 indent=1))
