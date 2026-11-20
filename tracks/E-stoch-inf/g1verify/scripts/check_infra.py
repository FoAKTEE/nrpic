"""C0: checks of my own tools before they are used (g1verify, JOURNAL entry 1, P-C0a-c).

usage: check_infra.py OUTDIR
- reader against core's read_dump (git show core/scalar-2:python/nrpic/{__init__,rng,
  scalar_field}.py into OUTDIR/corepkg/nrpic);
- own Philox against numpy.random.Philox; own alpha against core's mode_alpha twin;
- own background fixing against the input deck; own Bunch-Davies modes against the mode
  files; lists against the run-directory copies; sha256 of inputs against the manifests;
- R^NR of the slice at t = 0 against L^(-3/2) W R alpha (L32p, L64p, L128p).
"""
import os
import sys
import json
import subprocess
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nrsf, alpha as A, ref, rnr, catalog as C  # noqa: E402

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
res = {}

# ------------------------------------------------------------------ core's reader (twin)
pkg = os.path.join(out, "corepkg", "nrpic")
os.makedirs(pkg, exist_ok=True)
for f in ("__init__.py", "rng.py", "scalar_field.py"):
    src = subprocess.run(["git", "-C", C.WT, "show", f"core/scalar-2:python/nrpic/{f}"],
                         check=True, capture_output=True).stdout
    with open(os.path.join(pkg, f), "wb") as fh:
        fh.write(src if f != "__init__.py" else b"")
sys.path.insert(0, os.path.join(out, "corepkg"))
from nrpic import scalar_field as csf  # noqa: E402

runs = C.catalog()
rd = {}
for key in ("L32p", "L64p", "L128p"):
    path = nrsf.dumps(runs[key]["dir"])[5]
    h = nrsf.header(path)
    mine = nrsf.read(path, h["names"], h)
    core = csf.read_dump(path)
    cf = core["fields"]
    nd = {}
    for n in h["names"]:
        c = np.ascontiguousarray(np.asarray(cf[n]).transpose(2, 1, 0))
        nd[n] = int(np.sum(mine[n].view(np.uint64) != c.view(np.uint64)))
    rd[key] = dict(file=path, time=h["time"], cycle=h["cycle"], names=h["names"],
                   differing_elements=nd, all_identical=all(v == 0 for v in nd.values()))
res["reader"] = rd

# ------------------------------------------------------------------ alpha
seed = 20261115
nv = A.hemisphere(4096)
rng = np.random.default_rng(1)
samp = np.concatenate([np.arange(0, len(nv), 97), rng.choice(len(nv), 1500, replace=False)])
off = 1 << 20
ent = A.cell_entity(nv[samp, 0] + off, nv[samp, 1] + off, nv[samp, 2] + off)
strm = A.stream(3, 1 << 16)
w = A.philox4x64([ent, np.zeros(len(samp), np.uint64), np.zeros(len(samp), np.uint64),
                  np.full(len(samp), 16, np.uint64)], (np.uint64(seed), strm))
bad = 0
for q in range(len(samp)):
    g = np.random.Philox(counter=[int(ent[q]) - 1, 0, 0, 16], key=[seed, int(strm)])
    if not np.array_equal(g.random_raw(4), w[:, q]):
        bad += 1
al = A.alphas(nv, seed)
al_log = A.alphas(nv, seed, use_agm=False)
try:
    ca = np.asarray(csf.mode_alpha(seed, 0, 0, nv[samp]))
    core_diff = float(np.max(np.abs(ca - al[samp])))
except Exception as e:  # report, do not hide
    core_diff = f"failed: {e!r}"
res["alpha"] = dict(nmodes_4096=int(len(nv)), philox_sample=int(len(samp)),
                    philox_mismatch=bad, agm_vs_log_maxrel=float(np.max(np.abs(al - al_log) / np.abs(al))),
                    mean_abs2=float(np.mean(np.abs(al) ** 2)), expected_sigma=float(1 / np.sqrt(len(nv))),
                    mean_re_im_corr=float(np.mean(al.real * al.imag)),
                    core_twin_maxabs=core_diff)
np.save(os.path.join(out, "alpha_4096.npy"), al)

# ------------------------------------------------------------------ background and modes
fix = ref.quadratic_fix()
bgp = ref.phys_background(fix)
st = ref.phys_state(bgp, fix, 5.0)
cc = ref.to_code(fix, st)
deck = {"phi0": -2.66679478988261254e+00, "pi0": 2.97300406808996935e-02,
        "mass": 1.82877655899024605e-01}
cb = ref.CodeBackground(deck["phi0"], deck["pi0"], deck["mass"])
res["background"] = dict(
    phys=dict(phi0_N0=float(fix["phi0"]), m=float(fix["m"]), Hstar=float(st["H"]),
              eps1_star=float(st["eps1"]), eps2_star=float(st["eps2"])),
    code_from_fix={k: float(v) for k, v in cc.items()},
    rel_diff_to_deck={k: float(cc[k] / deck[k] - 1) for k in deck},
    H0_code=float(cb.h0), N_at_t85=float(cb(8.5)["lna"]), N_at_t45=float(cb(4.5)["lna"]),
    friedmann_residual_t85=float(cb(8.5)["friedmann"]))

mf = {}
files = {n: os.path.join(C.LISTS, f"modes_n{n}.txt") for n in (64, 256, 1024, 4096)}
tabs = {n: ref.read_mode_file(p) for n, p in files.items()}
n2s = np.array([1, 2, 3, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096])
bd = ref.bd_modes_phys(bgp, fix, 5.0, np.sqrt(n2s) * st["H"])
hs = st["H"]
for n, (n2, R, dR) in tabs.items():
    rows = []
    for q, (Rk, dRk) in zip(n2s, bd):
        if q > n:
            continue
        i = int(np.where(n2 == q)[0][0])
        Rc = Rk * hs ** 1.5
        dRc = dRk / hs * hs ** 1.5
        rows.append(dict(n2=int(q), modR=float(abs(Rc) / abs(R[i]) - 1),
                         moddR=float(abs(dRc) / abs(dR[i]) - 1),
                         relphase=float(np.angle((dRc / Rc) / (dR[i] / R[i])))))
    same = None
    if n != 64:
        n2a, Ra, dRa = tabs[64]
        k = n2 <= 64
        same = float(max(np.max(np.abs(R[k] - Ra)), np.max(np.abs(dR[k] - dRa))))
    mf[n] = dict(file=files[n], sha256=C.sha256(files[n]), rows=len(n2), bd=rows,
                 max_absdiff_to_n64_rows=same)
res["mode_files"] = mf

# ------------------------------------------------------------------ lists and manifests
lst = {}
for name, (rid, kind) in C.JOBS.items():
    m = C.manifest(rid)
    p = os.path.join(C.LISTS, name)
    shas = {os.path.basename(i["path"]): i.get("sha256") for i in m.get("inputs", [])}
    rec = dict(run_id=rid, status=m.get("status"), exit_code=m.get("exit_code"),
               list_sha_now=C.sha256(p), list_sha_manifest=shas.get(name))
    mod = {}
    for k, v in shas.items():
        if k.startswith("modes_n"):
            mod[k] = (v == C.sha256(os.path.join(C.LISTS, k)))
    rec["mode_file_sha_match"] = mod
    if kind == "card":
        copy = os.path.join(C.SCR, rid, "batch.list")
        same = True
        for (nm, deck_, args), line in zip(C.parse_list(p), [l for l in open(copy) if l.strip()]):
            tok = line.split()
            same &= os.path.basename(tok[0]) == nm and all(f"{k}={v}" in tok for k, v in args.items()
                                                            if k not in C.BASE_DEFAULTS or f"{k}=" in line)
        rec["copy_in_rundir_matches"] = bool(same)
    lst[name] = rec
res["lists"] = lst

# ------------------------------------------------------------------ slice at t = 0
sl = {}
L = 2 * np.pi
for key in ("L32p", "L64p", "L128p"):
    r = runs[key]
    path = nrsf.dumps(r["dir"])[0]
    h = nrsf.header(path)
    f = nrsf.read(path, ["phi", "Pi", "chi", "K", "alpha"] + rnr.GT, h)
    nv = A.hemisphere(r["nmax2"])
    Rn, m = rnr.rnr_coefficients(f, nv)
    n2, R0, dR0 = ref.read_mode_file(r["mode_file"])
    lut = {int(q): i for i, q in enumerate(n2)}
    q2 = np.sum(nv * nv, axis=1)
    idx = np.array([lut[int(q)] for q in q2])
    s0 = cb(0.0)
    W = ref.window(np.sqrt(q2), s0["a"], s0["H"])
    al = A.alphas(nv, seed)
    pred = L ** -1.5 * W * R0[idx] * al * r["scale"]
    rel = Rn / pred - 1
    byq = {}
    for q in sorted(set(q2.tolist()))[:6]:
        k = q2 == q
        byq[int(q)] = dict(W=float(W[k][0]), max_abs_rel=float(np.max(np.abs(rel[k]))),
                           max_phase=float(np.max(np.abs(np.angle(Rn[k] / pred[k])))))
    sl[key] = dict(time=h["time"], by_n2=byq,
                   means=m)
res["slice_t0"] = sl

with open(os.path.join(out, "check_infra.json"), "w") as fh:
    json.dump(res, fh, indent=1, default=str)
print(json.dumps(res, indent=1, default=str)[:6000])
