"""Measurement of one Z4c dump with the two diagnostics of gw_diag.

Reader: AthenaK `bin` mesh output of the Z4c group in single or double precision
(`<outputN> double_precision = true` of core/requests-b; layout as in
python/nrpic/athena_bin.py on that branch and athenak/src/outputs/binary.cpp), assembled on
a uniform mesh into gw_diag's layout f[k, j, i].

TT diagnostic: h^TT, d_tau h^TT = tt.tt_from_conformal(gt, At) (flat Lambda projector);
h'^TT = <alpha> d_tau h^TT (zero shift); amplitudes (P, X, P', X') at +k.
Weyl diagnostic: gamma, K = readers.z4c_to_adm; E, B = weyl.electric_magnetic (finite
differences of order 6, the stencil of the code with nghost = 4, or spectral); Psi_4 along
+khat and -khat; the eight coefficients at +-k inverted with the closed form of
weylref.py at the measured background a = <chi>^(-1/2), calH = -<alpha K>/3.
"""
import numpy as np

from . import HERE  # noqa: F401
from gwdiag import readers, tt, weyl
from gwdiag.grid import Grid

from .refs import pol_amplitudes
from . import weylref


def read_bin(path):
    """dict: time, cycle, variables, vsize, params, grid, and one float64 array (nz, ny, nx)
    per variable, the prefix 'z4c_' removed from the names."""
    with open(path, "rb") as f:
        raw = f.read()
    pos = 0
    info, names, hoff = {}, None, None
    while True:
        e = raw.index(b"\n", pos)
        line = raw[pos:e].decode()
        pos = e + 1
        if "variables:" in line:
            names = line.split("variables:")[1].split()
        elif "header offset" in line:
            hoff = int(line.split("=")[1])
            break
        elif "=" in line:
            k, v = line.split("=", 1)
            info[k.strip()] = v.strip()
    params = readers.parse_params(raw[pos:pos + hoff].decode(errors="replace"))
    pos += hoff
    lsize = int(info["size of location"])
    vsize = int(info.get("size of variable", "4"))
    ltype = np.float64 if lsize == 8 else np.float32
    vtype = np.float64 if vsize == 8 else np.float32
    nvar = len(names)
    blocks = []
    while pos < len(raw):
        ii = np.frombuffer(raw, np.int32, 10, pos)
        pos += 40
        ois, oie, ojs, oje, oks, oke, lx1, lx2, lx3, lev = (int(v) for v in ii)
        pos += 6 * lsize
        n1, n2, n3 = oie - ois + 1, oje - ojs + 1, oke - oks + 1
        cnt = n1 * n2 * n3
        arr = np.frombuffer(raw, vtype, nvar * cnt, pos).reshape(nvar, n3, n2, n1)
        pos += vsize * nvar * cnt
        blocks.append(((lx1, lx2, lx3, lev), arr))
    if any(b[0][3] != blocks[0][0][3] for b in blocks):
        raise ValueError(f"{path}: refined mesh")
    bn3, bn2, bn1 = blocks[0][1].shape[1:]
    m1 = max(b[0][0] for b in blocks) + 1
    m2 = max(b[0][1] for b in blocks) + 1
    m3 = max(b[0][2] for b in blocks) + 1
    full = np.empty((nvar, m3 * bn3, m2 * bn2, m1 * bn1))
    for (l1, l2, l3, _), arr in blocks:
        full[:, l3 * bn3:(l3 + 1) * bn3, l2 * bn2:(l2 + 1) * bn2, l1 * bn1:(l1 + 1) * bn1] = arr
    mesh = params["mesh"]
    lo = [float(mesh[f"x{a}min"]) for a in (1, 2, 3)]
    hi = [float(mesh[f"x{a}max"]) for a in (1, 2, 3)]
    grid = Grid((m1 * bn1, m2 * bn2, m3 * bn3), [h - l for h, l in zip(hi, lo)], lo)
    out = {"time": float(info["time"]), "cycle": int(info["cycle"]), "variables": names,
           "vsize": vsize, "params": params, "grid": grid}
    for i, n in enumerate(names):
        out[n[4:] if n.startswith("z4c_") else n] = full[i]
    return out


def measure(d, kvec, weyl_orders=(6, "spectral")):
    """Both diagnostics on one dump d (read_bin). Returns a dict of complex amplitudes and
    background numbers."""
    g = d["grid"]
    kv = np.asarray(kvec, float)
    n = kv / np.linalg.norm(kv)
    chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
    abar = float(np.mean(alpha))
    a_bg = float(np.mean(chi)) ** -0.5
    calH = -float(np.mean(alpha * trK)) / 3.0
    out = {"time": d["time"], "cycle": d["cycle"], "a": a_bg, "alpha": abar, "calH": calH,
           "max_beta": float(np.max(np.abs(beta)))}
    # TT
    h = gt - np.eye(3)[:, :, None, None, None]
    hTT, hdTT = tt.tt_from_conformal(gt, At, g)
    hpTT = abar * hdTT
    P, X = pol_amplitudes(hTT, g, kv)
    Pd, Xd = pol_amplitudes(hpTT, g, kv)
    out["tt"] = (P, X, Pd, Xd)
    nrm = np.sqrt(np.mean(hTT ** 2))
    out["nonTT_rel"] = float(np.sqrt(np.mean((h - hTT) ** 2)) / nrm) if nrm > 0 else np.nan
    # the TT field outside the mode +-k
    hk = tensor_from_mode(P, X, g, kv)
    out["tt_offmode_rel"] = float(np.sqrt(np.mean((hTT - hk) ** 2)) / nrm) if nrm > 0 else np.nan
    # Weyl
    gamma, K, _, _ = readers.z4c_to_adm(d)
    M = weylref.inversion_matrix(g, kv, a_bg, calH)
    out["weyl"] = {}
    for order in weyl_orders:
        E, B = weyl.electric_magnetic(gamma, K, g, order=order)
        f = weyl.psi4(E, B, gamma, g, direction=n)
        b = weyl.psi4(E, B, gamma, g, direction=-n)
        c = weylref.psi4_coeffs(f, b, g, kv)
        out["weyl"][str(order)] = weylref.invert(c, M)
        if order == weyl_orders[0]:
            out["psi4_fwd_coeffs"] = c
            # closed form from the TT measurement, pointwise, for the field comparison
            ff = weylref.psi4_from_tt(hTT, hpTT, a_bg, calH, g, n)
            out["psi4_field_rel"] = float(np.sqrt(np.mean(np.abs(f - ff) ** 2))
                                          / np.sqrt(np.mean(np.abs(ff) ** 2)))
            out["psi4_rms"] = float(np.sqrt(np.mean(np.abs(f) ** 2)))
    return out


def tensor_from_mode(P, X, g, kv):
    from .refs import tensor_field
    return tensor_field(P, X, g, kv)
