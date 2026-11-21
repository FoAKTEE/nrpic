"""V7c: bit-identity of the G1 executable across MeshBlock layouts and restart (P-V7c).

usage: v7_g1exe.py OUTDIR A7_RUN_DIR
Compares, bit for bit, every variable of the dumps of
  L32p  (registered E-20261115-172636-ce98836, one MeshBlock of 32^3),
  mb8   (A7_RUN_DIR/mb8: 8 MeshBlocks of 16^3),
  rst8  (A7_RUN_DIR/rst8: mb8 restarted from its restart file of cycle 12),
at equal cycle and time; the .modes files byte for byte; the records column by column.
The sha256 of the L32p dumps is checked against its run's list.
"""
import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nrsf, catalog as C  # noqa: E402

out, a7 = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
runs = C.catalog()
ref = runs["L32p"]
sums = C.sums(ref["run_id"])
res = dict(comparisons=[], modes={}, records={}, sha={})


def index(d):
    o = {}
    for p in nrsf.dumps(d):
        h = nrsf.header(p)
        o[(h["cycle"], np.float64(h["time"]).view(np.uint64).item())] = (p, h)
    return o


iref, imb, irs = index(ref["dir"]), index(os.path.join(a7, "mb8")), index(os.path.join(a7, "rst8"))
for label, A, B in (("L32p vs mb8", iref, imb), ("L32p vs rst8", iref, irs), ("mb8 vs rst8", imb, irs)):
    for key in sorted(set(A) & set(B)):
        pa, ha = A[key]
        pb, hb = B[key]
        if pa.startswith(ref["dir"]):
            rel = os.path.relpath(pa, os.path.join(C.SCR, ref["run_id"]))
            res["sha"][rel] = sums.get(rel) == C.sha256(pa)
        names = [n for n in ha["names"] if n in hb["names"]]
        fa, fb = nrsf.read(pa, names, ha), nrsf.read(pb, names, hb)
        nd = {n: int(np.sum(fa[n].view(np.uint64) != fb[n].view(np.uint64))) for n in names}
        res["comparisons"].append(dict(pair=label, cycle=ha["cycle"], time=ha["time"], nmb=[ha["nmb"], hb["nmb"]],
                                       nvar=len(names), ncells=int(fa[names[0]].size), differing=nd,
                                       identical=all(v == 0 for v in nd.values())))
        ma, mb = pa.replace(".dump", ".modes"), pb.replace(".dump", ".modes")
        if os.path.exists(ma) and os.path.exists(mb):
            res["modes"][f"{label} c{ha['cycle']}"] = open(ma, "rb").read() == open(mb, "rb").read()
for rec in ("sr.sf.hst", "sr.sf.con.hst"):
    for label, da, db in (("L32p vs mb8", ref["dir"], os.path.join(a7, "mb8")),
                          ("mb8 vs rst8", os.path.join(a7, "mb8"), os.path.join(a7, "rst8"))):
        ca, xa = nrsf.read_record(os.path.join(da, rec))
        cb, xb = nrsf.read_record(os.path.join(db, rec))
        ta, tb = xa[:, 0], xb[:, 0]
        common = [t for t in tb if np.any(ta == t)]
        A = xa[[int(np.where(ta == t)[0][0]) for t in common]]
        B = xb[[int(np.where(tb == t)[0][0]) for t in common]]
        same = A == B
        rel = np.abs(A - B) / np.maximum(np.abs(A), 1e-300)
        res["records"][f"{rec} {label}"] = dict(rows=len(common), all_equal=bool(same.all()),
                                                 columns_differing=[ca[j] for j in range(A.shape[1]) if not same[:, j].all()],
                                                 max_reldiff=float(rel.max()) if rel.size else None)
res["all_dumps_identical"] = bool(res["comparisons"]) and all(c["identical"] for c in res["comparisons"])
res["sha_all_ok"] = bool(all(res["sha"].values()))
with open(os.path.join(out, "v7_g1exe.json"), "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps({k: res[k] for k in ("all_dumps_identical", "sha_all_ok", "modes", "records")}, indent=1))
for c in res["comparisons"]:
    print(c["pair"], c["cycle"], round(c["time"], 4), c["nmb"], c["identical"], sum(c["differing"].values()))
