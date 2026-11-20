#!/usr/bin/env python3
"""V2 of verifier3: tests of my readers, TT projection and Weyl/Psi_4 code on analytic
fields and on the initial dumps (JOURNAL entry 2, predictions P2.1-P2.6).

Run through nrpic-run; writes $NRPIC_RUN_DIR/v2.json and figures v2_*.png/pdf.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
import exact  # noqa: E402
import figstyle as fs  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results", "tmp_v2"))
os.makedirs(OUT, exist_ok=True)
SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
F16 = f"{SCR}/B-20261119-142016-ee73a03/N16/bin/lwo.z4c.00000.bin"
X64 = f"{SCR}/B-20261119-142124-feb2daf/expN64/bin/xw.z4c.00000.bin"
X16 = f"{SCR}/B-20261119-142021-8f4c441/N16/bin/xw.z4c.00000.bin"
LW3 = f"{SCR}/B-emd-gw-20261115-112947-b7b431d/bin/lw3.z4c.00000.bin"
res = {}
t0 = time.time()


def rel(a, b):
    return float(np.max(np.abs(a - b)) / np.max(np.abs(b)))


# ------------------------------------------------------------------ P2.1 reader, double
d = diag.read_bin(F16)
g = d["grid"]
X = g.coords()
fw = exact.FlatWave()
h, hd = fw.fields(X, 0.0)
v = d["vars"]
gt = diag.sym_from(v, "z4c_g")
At = diag.sym_from(v, "z4c_A")
eye = np.eye(3)[:, :, None, None, None]
r21 = {
    "header": {k: d["header"][k] for k in ("time", "cycle", "size of variable", "number of variables")},
    "grid n, L, xmin": [list(g.n), g.L.tolist(), g.xmin.tolist()], "nblocks": d["nblocks"],
    "max|gt - (delta + h_exact)|": float(np.max(np.abs(gt - eye - h))),
    "max|At - (-hdot/2)|": float(np.max(np.abs(At + 0.5 * hd))),
    "max|chi-1|, |alpha-1|, |Khat|, |Theta|, |Gam|, |beta|": [
        float(np.max(np.abs(v["z4c_chi"] - 1))), float(np.max(np.abs(v["z4c_alpha"] - 1))),
        float(np.max(np.abs(v["z4c_Khat"]))), float(np.max(np.abs(v["z4c_Theta"]))),
        float(max(np.max(np.abs(v[f"z4c_Gam{c}"])) for c in "xyz")),
        float(max(np.max(np.abs(v[f"z4c_beta{c}"])) for c in "xyz"))],
}
# synthetic multi-block file: the same data re-blocked into 2x2x2 blocks of 8^3
with open(F16, "rb") as f:
    raw = f.read()
pre_end = raw.index(b"header offset=")
pre_end = raw.index(b"\n", pre_end) + 1
hoff = int(d["header"]["header offset"])
par = raw[pre_end:pre_end + hoff].decode("latin1")
par2 = par.replace("<meshblock>\nnx1 = 16", "<meshblock>\nnx1 = 8")
import re  # noqa: E402
blk = par[par.index("<meshblock>"):]
blk = blk[:blk.index("<", 2)]
blk2 = re.sub(r"(nx[123]\s*=\s*)16", r"\g<1>8", blk)
par2 = par.replace(blk, blk2)
assert par2 != par
pre = raw[:pre_end].replace(f"header offset={hoff}".encode(), f"header offset={len(par2)}".encode())
names = d["header"]["variables"]
body = b""
order = [(1, 0, 1), (0, 0, 0), (1, 1, 0), (0, 1, 1), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]
for (l1, l2, l3) in order:
    ints = np.array([4, 11, 4, 11, 4, 11, l1, l2, l3, 0], "<i4").tobytes()
    xs = np.array([-0.5 + 0.5 * l1, 0.5 * l1, -0.5 + 0.5 * l2, 0.5 * l2, -0.5 + 0.5 * l3, 0.5 * l3], "<f8").tobytes()
    dat = np.stack([v[nm][8 * l1:8 * l1 + 8, 8 * l2:8 * l2 + 8, 8 * l3:8 * l3 + 8].transpose(2, 1, 0)
                    for nm in names]).astype("<f8").tobytes()
    body += ints + xs + dat
syn = os.path.join(OUT, "synthetic_multiblock.bin")
with open(syn, "wb") as f:
    f.write(pre + par2.encode("latin1") + body)
ds = diag.read_bin(syn)
r21["synthetic 8 blocks (shuffled order): max|diff| vs single block"] = float(
    max(np.max(np.abs(ds["vars"][nm] - v[nm])) for nm in names))
r21["synthetic nblocks"] = ds["nblocks"]
os.remove(syn)
# a broken file must be refused
try:
    with open(F16, "rb") as f:
        bad = f.read()[:-8]
    tmpb = os.path.join(OUT, "truncated.bin")
    with open(tmpb, "wb") as f:
        f.write(bad)
    diag.read_bin(tmpb)
    r21["truncated file refused"] = False
except ValueError as e:
    r21["truncated file refused"] = str(e)[-80:]
finally:
    os.remove(tmpb)
res["P2.1"] = r21

# ------------------------------------------------------------------ P2.2 reader, single
d3 = diag.read_bin(LW3)
g3 = d3["grid"]
fw3 = exact.FlatWave(k_cycles=(1.0, 0.0, 0.0), amp=1e-6, amp_x=0.0, phi_x=0.0)
A3, _ = exact.generator_tensors(1.0, 0.0, 0.0)
P3 = 2 * np.pi * g3.coords()[0]
gt3_exact = np.eye(3)[:, :, None, None, None] + 1e-6 * A3[:, :, None, None, None] * np.sin(P3)
gt3 = diag.sym_from(d3["vars"], "z4c_g")
f32 = gt3_exact.astype(np.float32).astype(np.float64)
res["P2.2"] = {
    "header size of variable": d3["header"]["size of variable"], "time": d3["time"],
    "grid n": list(g3.n),
    "max|reader - float32(closed form)|": float(np.max(np.abs(gt3 - f32))),
    "max|reader - closed form| (float rounding)": float(np.max(np.abs(gt3 - gt3_exact))),
    "float32 ulp at 1": float(np.spacing(np.float32(1.0))),
}

# ------------------------------------------------------------------ P2.3 TT projection
rng = np.random.default_rng(7)
ga = diag.Grid((32, 24, 20), (1.0, 1.3, 0.8), (-0.2, 0.1, 0.3))
Xa = ga.coords()
TT = np.zeros((3, 3) + ga.n)
for _ in range(20):
    m = rng.integers(-5, 6, size=3)
    if not m.any():
        continue
    K = 2 * np.pi * m / ga.L
    ep, ex, n, _, _ = exact.pol_tensors(K)
    ph = K[0] * Xa[0] + K[1] * Xa[1] + K[2] * Xa[2]
    TT += (rng.normal() * ep[:, :, None, None, None] * np.cos(ph + rng.uniform(0, 6.3))
           + rng.normal() * ex[:, :, None, None, None] * np.sin(ph + rng.uniform(0, 6.3)))
# gauge part d_i xi_j + d_j xi_i and trace part, random smooth fields
xi = np.zeros((3,) + ga.n)
trf = np.zeros(ga.n)
for _ in range(10):
    m = rng.integers(-4, 5, size=3)
    K = 2 * np.pi * m / ga.L
    ph = K[0] * Xa[0] + K[1] * Xa[1] + K[2] * Xa[2] + rng.uniform(0, 6.3)
    xi += rng.normal(size=3)[:, None, None, None] * np.sin(ph)
    trf += rng.normal() * np.cos(ph)
dxi = np.array([[diag.dspec(xi[j], ga, i) for j in range(3)] for i in range(3)])
gauge = dxi + np.swapaxes(dxi, 0, 1) + np.eye(3)[:, :, None, None, None] * trf
LT = diag.tt_project(TT, ga)
LG = diag.tt_project(gauge, ga)
LL = diag.tt_project(TT + gauge, ga)
div = np.array([sum(diag.dspec(LL[a, b], ga, a) for a in range(3)) for b in range(3)])
res["P2.3"] = {
    "max|Lambda(TT) - TT| / max|TT|": rel(LT, TT),
    "max|Lambda(gauge+trace)| / max|gauge+trace|": float(np.max(np.abs(LG)) / np.max(np.abs(gauge))),
    "max|Lambda^2 - Lambda| / max|Lambda|": rel(diag.tt_project(LL, ga), LL),
    "max|trace Lambda|": float(np.max(np.abs(np.einsum("aa...->...", LL)))),
    "max|div Lambda| / (kmax max|Lambda|)": float(np.max(np.abs(div)) / (2 * np.pi * 5 / 0.8 * np.max(np.abs(LL)))),
    "mode coefficient of a known cos field": None,
}
# mode coefficient check
m0 = (2, -1, 1)
K0 = 2 * np.pi * np.array(m0) / ga.L
f0 = 0.7 * np.cos(K0[0] * Xa[0] + K0[1] * Xa[1] + K0[2] * Xa[2] + 0.4)
c0 = diag.mode_coeff(f0, ga, m0)
res["P2.3"]["mode coefficient of a known cos field"] = [float(abs(2 * c0) - 0.7), float(np.angle(c0) - 0.4)]

# ------------------------------------------------------------------ P2.4 Weyl, flat wave
r24 = {}
for N in (16, 32):
    gf = diag.Grid((N, N, N), (1.0, 1.0, 1.0), (-0.5, -0.5, -0.5))
    Xf = gf.coords()
    for amp_scale in (1.0, 10.0):
        fwv = exact.FlatWave(amp=1e-6 * amp_scale, amp_x=5e-7 * amp_scale)
        hf, hdf = fwv.fields(Xf, 0.37)
        gam = np.eye(3)[:, :, None, None, None] + hf
        Kf = -0.5 * hdf
        E, B = diag.weyl_EB(gam, Kf, gf)
        E_pred = 0.5 * fwv.w ** 2 * hf
        dhd = np.array([diag.dspec(hdf, gf, c) for c in range(3)])
        Bm = -0.5 * np.einsum("ikl,klj...->ij...", diag.LC, dhd)
        B_pred = 0.5 * (Bm + np.swapaxes(Bm, 0, 1))
        p4 = diag.psi4(E, B, gam, fwv.K)
        p4r = diag.psi4(E, B, gam, -fwv.K)
        m = (1, 1, 1)
        cp, cx = fwv.complex_amp(0.37)
        hp_W = 2j * diag.mode_coeff(-p4.real / fwv.w ** 2, gf, m)
        hx_W = 2j * diag.mode_coeff(p4.imag / fwv.w ** 2, gf, m)
        key = f"N{N} amp x{amp_scale:g}"
        r24[key] = {
            "E rel err": rel(E, E_pred), "B rel err": rel(B, B_pred),
            "Psi4 -> h_+ complex amp rel err": float(abs(hp_W - cp) / abs(cp)),
            "Psi4 -> h_x complex amp rel err": float(abs(hx_W - cx) / abs(cx)),
            "max|Psi4(-n)| / (w^2 A_+)": float(np.max(np.abs(p4r)) / (fwv.w ** 2 * fwv.amp)),
        }
        if amp_scale == 1.0:
            E6, B6 = diag.weyl_EB(gam, Kf, gf, deriv="fd6")
            r24[key]["FD6: E rel err"] = rel(E6, E_pred)
            r24[key]["FD6: B rel err"] = rel(B6, B_pred)
res["P2.4"] = r24

# ------------------------------------------------------------------ P2.5 Weyl, FLRW mode
r25 = {}
gx = diag.Grid((32, 32, 32), (4.0, 4.0, 4.0), (0.0, 0.0, 0.0))
Xx = gx.coords()
mX = (1, 1, 0)
for es in (1.0, 10.0):
    xw = exact.ExpandingWave(eps_p=2e-6 * es, eps_x=1e-6 * es)
    for tt in (0.0, 0.6, 3.0, 9.0):
        gam, Kx, a = xw.fields(Xx, tt)
        E, B = diag.weyl_EB(gam, Kx, gx)
        T, dT = xw.mode.T(tt), xw.mode.dT(tt)
        calH = exact.eds_calH(tt)
        # exact linear: E = (k^2/2) h + (calH/2) h', h = eps T e cos; coefficients 2c
        Ep, Ex = diag.pol_components(E, xw.K)
        Bp, Bx = diag.pol_components(B, xw.K)
        cE = [2 * diag.mode_coeff(q, gx, mX) for q in (Ep, Ex)]
        cB = [2 * diag.mode_coeff(q, gx, mX) for q in (Bp, Bx)]
        (hp, hx), (dhp, dhx) = xw.coeff(tt)
        Ep_ex = 0.5 * xw.kn ** 2 * hp + 0.5 * calH * dhp
        Ex_ex = 0.5 * xw.kn ** 2 * hx + 0.5 * calH * dhx
        # B: for h' = p e+ cos(.), B = (|K|/2) p sin(.) ex ; sin -> coefficient 2c = -i
        Bx_ex = 0.5 * xw.kn * dhp * (-1j)
        Bp_ex = -0.5 * xw.kn * dhx * (-1j)
        scaleE = max(abs(Ep_ex), 1e-30)
        scaleB = max(abs(Bx_ex), 1e-30)
        # conformal-metric route of the TT diagnostic: h = gt - delta, h' = -2 a At
        chi = np.linalg.det(np.moveaxis(gam, (0, 1), (-2, -1))) ** (-1.0 / 3.0)
        gtX = chi * gam
        trK = np.einsum("ij...,ij...->...", diag.inv3(gam)[0], Kx)
        AtX = chi * (Kx - gam * trK / 3.0)
        hTT = diag.tt_project(gtX - np.eye(3)[:, :, None, None, None], gx)
        dTT = diag.tt_project(-2 * a * AtX, gx)
        ch = [2 * diag.mode_coeff(q, gx, mX) for q in diag.pol_components(hTT, xw.K)]
        cd = [2 * diag.mode_coeff(q, gx, mX) for q in diag.pol_components(dTT, xw.K)]
        r25[f"eps x{es:g} t={tt}"] = {
            "E_+ err / |E_+|": float(abs(cE[0] - Ep_ex) / scaleE),
            "E_x err / |E_+|": float(abs(cE[1] - Ex_ex) / scaleE),
            "B_x err / |B_x|": float(abs(cB[1] - Bx_ex) / scaleB),
            "B_+ err / |B_x|": float(abs(cB[0] - Bp_ex) / scaleB),
            "TT h_+ err / eps max|T|": float(abs(ch[0] - hp) / (xw.eps_p * 0.27)),
            "TT h_x err / eps max|T|": float(abs(ch[1] - hx) / (xw.eps_p * 0.27)),
            "TT h'_+ err / eps": float(abs(cd[0] - dhp) / xw.eps_p),
            "TT h'_x err / eps": float(abs(cd[1] - dhx) / xw.eps_p),
        }
res["P2.5"] = r25

# ------------------------------------------------------------------ P2.6 initial dumps of X
r26 = {}
for lab, path in (("N16", X16), ("N64", X64)):
    dx_ = diag.read_bin(path)
    gxx = dx_["grid"]
    gam, Kx, alp, chi, gtx, Atx, trK = diag.z4c_to_adm(dx_)
    xw = exact.ExpandingWave()
    Xq = gxx.coords()
    gam_ex, K_ex, a = xw.fields(Xq, 0.0)
    hTT = diag.tt_project(gtx - np.eye(3)[:, :, None, None, None], gxx)
    dTT = diag.tt_project(-2 * 1.0 * Atx, gxx)
    cd = [2 * diag.mode_coeff(q, gxx, mX) for q in diag.pol_components(dTT, xw.K)]
    r26[lab] = {
        "time": dx_["time"], "var size": dx_["header"]["size of variable"],
        "max|gamma - delta|": float(np.max(np.abs(gam - np.eye(3)[:, :, None, None, None]))),
        "max|K - K_exact|": float(np.max(np.abs(Kx - K_ex))),
        "max|alpha - 1|": float(np.max(np.abs(alp - 1))),
        "h'_+ coefficient (expect eps_+ = 2e-6)": [float(cd[0].real), float(cd[0].imag)],
        "h'_x coefficient (expect eps_x e^{i phi_x})": [float(abs(cd[1])), float(np.angle(cd[1]))],
        "max|Theta|": float(np.max(np.abs(dx_["vars"]["z4c_Theta"]))),
        "max|Gam|": float(max(np.max(np.abs(dx_["vars"][f"z4c_Gam{c}"])) for c in "xyz")),
    }
res["P2.6"] = r26
res["wall_s"] = time.time() - t0
with open(os.path.join(OUT, "v2.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str))

# ------------------------------------------------------------------ figure: Weyl errors
fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402

fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.9, wspace=0.3)
ax = axs[0]
labs = ["E", "B", r"$\Psi_4\to h_+$", r"$\Psi_4\to h_\times$"]
keys = ["E rel err", "B rel err", "Psi4 -> h_+ complex amp rel err", "Psi4 -> h_x complex amp rel err"]
for j, (kk, col) in enumerate((("N32 amp x1", fs.PAL["blue"]), ("N32 amp x10", fs.PAL["red"]))):
    vals = [max(r24[kk][q], 1e-18) for q in keys]
    ax.bar(np.arange(4) + 0.38 * j, vals, width=0.36, color=col, label=kk.replace("N32 ", "flat, 32$^3$, "))
ax.set_yscale("log")
ax.set_xticks(np.arange(4) + 0.19)
ax.set_xticklabels(labs)
ax.set_ylabel("relative error vs linear exact")
ax.legend(loc="upper left")
ax.set_title("flat plane wave (spectral derivatives)")
ax = axs[1]
ts = [0.0, 0.6, 3.0, 9.0]
for es, col in ((1.0, fs.PAL["blue"]), (10.0, fs.PAL["red"])):
    ax.semilogy(ts, [max(r25[f"eps x{es:g} t={t}"]["E_+ err / |E_+|"], 1e-18) for t in ts], "o-", color=col,
                label=rf"$E_+$, $\epsilon\times{es:g}$")
    ax.semilogy(ts, [max(r25[f"eps x{es:g} t={t}"]["B_x err / |B_x|"], 1e-18) for t in ts], "s--", color=col,
                label=rf"$B_\times$, $\epsilon\times{es:g}$")
ax.set_xlabel(r"conformal time $t$")
ax.set_ylabel("relative error vs linear exact")
ax.set_title("EdS tensor mode, 32$^3$")
ax.legend(loc="lower right", ncol=2, fontsize=8)
fs.save(fig, os.path.join(OUT, "v2_weyl"))
print("done", time.time() - t0)
