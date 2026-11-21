"""V4 (constraints: odd and even parts, halving, negative controls, records) and the data of
V5 (spatial order of the odd part, the floor) from my own reads of the dumps (g1verify).

usage: constraints.py OUTDIR [--verified RUN_ID ...] [--sets NAME ...]
Sets (p, m[, ph, mh]): the pair of mirrored runs s = +-1 and, where it exists, the halved
pair s = +-1/2.  odd = (C(s) - C(-s))/2, even = (C(s) + C(-s))/2 for C = H and M_i.
Bands of the odd part by wave vector: in = |n|^2 <= nmax2 (where a first-order quantity
lives), mid = nmax2 < |n|^2 <= 9 nmax2 (third order at most), out = |n|^2 > 9 nmax2 (no
physics up to third order: rounding).  Files of runs named with --verified had their
sha256 checked in pass 1 (permode) and are read by seek (four variables); every other file
is read whole, once, and hashed.
"""
import os
import sys
import json
import numpy as np
import scipy.fft as sfft

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nrsf, catalog as C  # noqa: E402

args = sys.argv[1:]
out = args.pop(0)
verified, sets_req = [], None
while args:
    a = args.pop(0)
    if a == "--verified":
        while args and not args[0].startswith("--"):
            verified.append(args.pop(0))
    elif a == "--sets":
        sets_req = []
        while args and not args[0].startswith("--"):
            sets_req.append(args.pop(0))
os.makedirs(out, exist_ok=True)
runs = C.catalog()
CV = ["H", "Mx", "My", "Mz"]
WORKERS = int(os.environ.get("OMP_NUM_THREADS", "4"))

SETS = {
    "L32": ("L32p", "L32m", "L32ph", "L32mh"), "NC32": ("NC32p", "NC32m"),
    "L64": ("L64p", "L64m"), "L64proc": ("L64p_proc", "L64m_proc"),
    "L128": ("L128p", "L128m"), "L256": ("L256p", "L256m"),
    "Q64": ("Q64p", "Q64m", "Q64ph", "Q64mh"), "NC64": ("NC64p", "NC64m"),
    "Q128": ("Q128p", "Q128m", "Q128ph", "Q128mh"), "NC128": ("NC128p", "NC128m"),
    "P256": ("P256", "P256m"),
}
if sets_req:
    SETS = {k: SETS[k] for k in sets_req}

shacheck = {}


def load(key, path):
    r = runs[key]
    if r["run_id"] in verified:
        h = nrsf.header(path)
        return nrsf.read(path, CV, h), h
    f, dig, h = nrsf.read_hashed(path, CV)
    rel = os.path.relpath(path, os.path.join(C.SCR, r["run_id"]))
    shacheck[f"{key}/{os.path.basename(path)}"] = C.sums(r["run_id"]).get(rel) == dig
    return {k: np.array(v) for k, v in f.items()}, h


def kgrid(N):
    n = np.fft.fftfreq(N, 1.0 / N)
    return (n[:, None, None] ** 2 + n[None, :, None] ** 2 + n[None, None, :] ** 2)


def bands(field, n2, nmax2):
    """rms contributions (Parseval) of the bands in, mid, out of a real field."""
    N = field.shape[0]
    F = sfft.fftn(field, workers=WORKERS)
    p = np.abs(F) ** 2 / N ** 6
    b_in = n2 <= nmax2
    b_mid = (n2 > nmax2) & (n2 <= 9 * nmax2)
    b_out = n2 > 9 * nmax2
    return dict(inb=float(np.sqrt(p[b_in & (n2 > 0)].sum())), mid=float(np.sqrt(p[b_mid].sum())),
                out=float(np.sqrt(p[b_out].sum())), zero=float(np.sqrt(p[0, 0, 0]))), F


def shell_spec(F, n2, nbin):
    """mean |c_n|^2 per integer shell |n| (c = F/N^3)."""
    N = F.shape[0]
    q = np.rint(np.sqrt(n2)).astype(int)
    p = np.abs(F) ** 2 / N ** 6
    s = np.bincount(q.ravel(), weights=p.ravel(), minlength=nbin)[:nbin]
    c = np.bincount(q.ravel(), minlength=nbin)[:nbin]
    return s / np.maximum(c, 1)


def parts(A, B):
    """odd and even parts of H and M_i; their statistics and bands."""
    oH = 0.5 * (A["H"] - B["H"])
    eH = 0.5 * (A["H"] + B["H"])
    oM = [0.5 * (A[c] - B[c]) for c in CV[1:]]
    eM = [0.5 * (A[c] + B[c]) for c in CV[1:]]
    return oH, eH, oM, eM


def rms(x):
    return float(np.sqrt(np.mean(x * x)))


res = {}
spec = {}
for sname, keys in SETS.items():
    rp, rm = runs[keys[0]], runs[keys[1]]
    N, nmax2 = rp["N"], rp["nmax2"]
    n2 = kgrid(N)
    fp, fm = nrsf.dumps(rp["dir"]), nrsf.dumps(rm["dir"])
    fh = [nrsf.dumps(runs[k]["dir"]) for k in keys[2:4]] if len(keys) == 4 else None
    hp = {nrsf.header(p)["cycle"]: p for p in fp}
    hm = {nrsf.header(p)["cycle"]: p for p in fm}
    common = sorted(set(hp) & set(hm))
    if fh:
        hph = {nrsf.header(p)["cycle"]: p for p in fh[0]}
        hmh = {nrsf.header(p)["cycle"]: p for p in fh[1]}
        common = [c for c in common if c in hph and c in hmh]
    rows = []
    for cyc in common:
        A, ha = load(keys[0], hp[cyc])
        B, hb = load(keys[1], hm[cyc])
        assert abs(ha["time"] - hb["time"]) < 1e-12
        oH, eH, oM, eM = parts(A, B)
        bo, Fo = bands(oH, n2, nmax2)
        be, Fe = bands(eH - eH.mean(), n2, nmax2)
        boM = [bands(x, n2, nmax2)[0] for x in oM]
        row = dict(cycle=int(cyc), time=float(ha["time"]),
                   rms_H_p=rms(A["H"]), mean_H_p=float(A["H"].mean()),
                   rms_odd_H=rms(oH), rms_even_H_nomean=rms(eH - eH.mean()), mean_even_H=float(eH.mean()),
                   rms_odd_M=float(np.sqrt(sum(np.mean(x * x) for x in oM))),
                   rms_even_M=float(np.sqrt(sum(np.mean((x - x.mean()) ** 2) for x in eM))),
                   odd_H_bands=bo, even_H_bands=be,
                   odd_M_bands={b: float(np.sqrt(sum(d[b] ** 2 for d in boM))) for b in ("inb", "mid", "out")})
        if fh:
            Ah, _ = load(keys[2], hph[cyc])
            Bh, _ = load(keys[3], hmh[cyc])
            oHh, eHh, oMh, eMh = parts(Ah, Bh)
            boh, _ = bands(oHh, n2, nmax2)
            beh, _ = bands(eHh - eHh.mean(), n2, nmax2)
            boMh = [bands(x, n2, nmax2)[0] for x in oMh]
            row.update(h_rms_odd_H=rms(oHh), h_rms_even_H_nomean=rms(eHh - eHh.mean()),
                       h_mean_even_H=float(eHh.mean()),
                       h_rms_odd_M=float(np.sqrt(sum(np.mean(x * x) for x in oMh))),
                       h_rms_even_M=float(np.sqrt(sum(np.mean((x - x.mean()) ** 2) for x in eMh))),
                       h_odd_H_bands=boh, h_even_H_bands=beh,
                       h_odd_M_bands={b: float(np.sqrt(sum(d[b] ** 2 for d in boMh))) for b in ("inb", "mid", "out")},
                       # residual of the linear scaling of the odd part: floor (does not scale with s)
                       rms_odd_H_minus_2half=rms(oH - 2.0 * oHh),
                       rms_odd_M_minus_2half=float(np.sqrt(sum(np.mean((a - 2.0 * b) ** 2) for a, b in zip(oM, oMh)))),
                       rms_even_H_minus_4half=rms((eH - eH.mean()) - 4.0 * (eHh - eHh.mean())))
            del Ah, Bh
        nb = int(np.sqrt(3) * N / 2) + 2
        spec[f"{sname}_c{cyc}_odd"] = shell_spec(Fo, n2, nb)
        spec[f"{sname}_c{cyc}_even"] = shell_spec(Fe, n2, nb)
        rows.append(row)
        print(sname, cyc, f"t={row['time']:.3f} oddH={row['rms_odd_H']:.3e} evenH={row['rms_even_H_nomean']:.3e} "
              f"out={bo['out']:.2e}", flush=True)
        del A, B
    # the records at every cycle: ratios and halving factors
    rec = {}
    for k in keys:
        cols, d = nrsf.read_record(os.path.join(runs[k]["dir"], "sr.sf.con.hst"))
        rec[k] = (cols, d)
    cols = rec[keys[0]][0]
    iH, iM = cols.index("<|H|/[H]>"), cols.index("<|M|/[M]>")
    dP = rec[keys[0]][1]
    recd = dict(time=dP[:, 0].tolist(), H_p=dP[:, iH].tolist(), M_p=dP[:, iM].tolist(),
                maxH_p=float(dP[:, iH].max()), maxM_p=float(dP[:, iM].max()),
                maxH_m=float(rec[keys[1]][1][:, iH].max()), maxM_m=float(rec[keys[1]][1][:, iM].max()))
    if fh:
        dh = rec[keys[2]][1]
        n = min(len(dP), len(dh))
        ok = np.abs(dP[:n, 0] - dh[:n, 0]) < 1e-12          # same cycle and time (last step of
        recd.update(time_h=dP[:n, 0][ok].tolist(),            # a run may be shortened to tlim)
                    F_H=(dP[:n, iH] / dh[:n, iH])[ok].tolist(),
                    F_M=(dP[:n, iM] / dh[:n, iM])[ok].tolist())
    res[sname] = dict(keys=list(keys), N=N, nmax2=nmax2, rows=rows, record=recd)

res["sha_checked"] = shacheck
res["sha_all_ok"] = bool(all(shacheck.values())) if shacheck else None
with open(os.path.join(out, "constraints.json"), "w") as f:
    json.dump(res, f)
np.savez(os.path.join(out, "constraints_spec.npz"), **spec)
print("sha_all_ok", res["sha_all_ok"], len(shacheck))
