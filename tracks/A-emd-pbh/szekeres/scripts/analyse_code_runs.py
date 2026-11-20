"""Comparison of AthenaK field dumps of the Szekeres hole with the exact solution (DESIGN.md
sections 4 and 6; JOURNAL entries 7 to 9).

For every member (a run directory with szk.field.*.bin dumps) and every dump: the code's
K = Khat + 2 Theta_Z4c, E, chi, H, M_i, alpha against the exact values at the same cells
(labels r, bn of slice_t0.npz written by prep_code_files.py; the dust stays at its cell in
geodesic slicing), by region of the label (core r < 2.4, shell, outside r > 6):
  K:   max and rms of |K - K_exact| / H(tau)   (H(tau) the background rate; K changes sign
       at turnaround, so a relative error of K is not used for orders)
  E:   max and rms of |E - rho| / rho;  chi: the same against psi^-4 (rho(t)/rho(t_i))^(2/3)
  H, M: rms over the region / (16 pi rho_b(tau))
  the non-spherical signal: max |X_Szekeres - X_LTB| at the same cells (rho relative,
  K / H(tau)), the part a spherical solution would miss.
Orders between successive members of a series: log2(e_N / e_2N) at the same dump index.
Members are given as NAME[=PREP] (PREP: the member of the preparation run whose files the
run used; default NAME); NAME may be a restart continuation of another member
(--cont A:B appends the dumps of B to A).

    python3 scripts/analyse_code_runs.py --run DIR --prep DIR --members N64 N128 N256 \
        [--cont N256:N256r] [--label series] [--eps 0.2]
"""

import argparse
import glob
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import numpy as np  # noqa: E402

REG = ("core", "shell", "outside")
CHUNK = 1 << 21


def read_field_flat(path):
    """Header and flat arrays in file order (x fastest)."""
    with open(path, "rb") as f:
        magic = f.read(8)
        t = float(np.frombuffer(f.read(8), "<f8")[0])
        n1, n2, n3 = (int(v) for v in np.frombuffer(f.read(24), "<i8"))
        nc = n1 * n2 * n3
        out = dict(t=t, n=(n1, n2, n3))
        out["E"] = np.frombuffer(f.read(4 * nc), "<f4").astype(float)
        out["chi"] = np.frombuffer(f.read(4 * nc), "<f4").astype(float)
        if magic == b"NRFIELD2":
            for k in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
                out[k] = np.frombuffer(f.read(8 * nc), "<f8")
    return out


def flat(a):
    """[i, j, k] array -> file order."""
    return np.ascontiguousarray(np.asarray(a).transpose(2, 1, 0)).ravel()


def analyse_dump(F, sl, szk, ltb):
    tau = F["t"]
    t = szk.t_i + tau
    a = (1 + tau / szk.t_i) ** (2.0 / 3.0)
    Hb, rb = szk.H / a ** 1.5, szk.rho_b / a ** 3
    n = len(F["E"])
    acc = {r: dict(n=0, K2=0.0, Kmax=0.0, E2=0.0, Emax=0.0, c2=0.0, cmax=0.0, H2=0.0, Hmax=0.0, M2=0.0,
                   amax=0.0, sig_rho=0.0, sig_K=0.0, nonfinite=0) for r in REG}
    keep = {}
    for s in range(0, n, CHUNK):
        sel = slice(s, min(n, s + CHUNK))
        r, bn, psi, rho0 = sl["r"][sel], sl["bn"][sel], sl["psi"][sel], sl["rho"][sel]
        ex = szk.fields(t, r, bn)
        lt = ltb.fields(t, sl["r_ltb"][sel], np.zeros_like(r))
        K = F["Khat"][sel] + 2 * F["Theta"][sel]
        chi_ex = psi ** -4 * (ex["rho"] / rho0) ** (2.0 / 3.0)
        eK = np.abs(K - ex["K"]) / Hb
        eE = np.abs(F["E"][sel] - ex["rho"]) / ex["rho"]
        ec = np.abs(F["chi"][sel] - chi_ex) / chi_ex
        eH = np.abs(F["H"][sel]) / (16 * math.pi * rb)
        eM = (F["Mx"][sel] ** 2 + F["My"][sel] ** 2 + F["Mz"][sel] ** 2) / (16 * math.pi * rb) ** 2
        ea = np.abs(F["alpha"][sel] - 1.0)
        sr = np.abs(ex["rho"] - lt["rho"]) / ex["rho"]
        sK = np.abs(ex["K"] - lt["K"]) / Hb
        masks = {"core": r < common.PROFILE[1], "shell": (r >= common.PROFILE[1]) & (r <= common.PROFILE[2]),
                 "outside": r > common.PROFILE[2]}
        for name, m in masks.items():
            if not np.any(m):
                continue
            A = acc[name]
            bad = ~np.isfinite(eK[m]) | ~np.isfinite(eE[m]) | ~np.isfinite(eH[m])
            A["nonfinite"] += int(bad.sum())
            A["n"] += int(m.sum())
            for key, arr, mx in (("K2", eK, "Kmax"), ("E2", eE, "Emax"), ("c2", ec, "cmax"), ("H2", eH, "Hmax")):
                v = arr[m]
                A[key] += float(np.nansum(v ** 2))
                A[mx] = max(A[mx], float(np.nanmax(v)) if np.any(np.isfinite(v)) else float("nan"))
            A["M2"] += float(np.nansum(eM[m]))
            A["amax"] = max(A["amax"], float(np.nanmax(ea[m])))
            A["sig_rho"] = max(A["sig_rho"], float(np.max(sr[m])))
            A["sig_K"] = max(A["sig_K"], float(np.max(sK[m])))
        for key, arr in (("K", K), ("K_ex", ex["K"]), ("E", F["E"][sel]), ("rho", ex["rho"]), ("chi", F["chi"][sel]),
                         ("chi_ex", chi_ex), ("rho_ltb", lt["rho"]), ("K_ltb", lt["K"])):
            keep.setdefault(key, []).append(arr)
    row = dict(tau=tau, H_bg=Hb, rho_bg=rb)
    for name, A in acc.items():
        nn = max(A["n"], 1)
        row[name] = dict(cells=A["n"], nonfinite=A["nonfinite"],
                         K_err_over_H_max=A["Kmax"], K_err_over_H_rms=math.sqrt(A["K2"] / nn),
                         E_rel_max=A["Emax"], E_rel_rms=math.sqrt(A["E2"] / nn),
                         chi_rel_max=A["cmax"], chi_rel_rms=math.sqrt(A["c2"] / nn),
                         H_over_16pirho_rms=math.sqrt(A["H2"] / nn), H_over_16pirho_max=A["Hmax"],
                         M_over_16pirho_rms=math.sqrt(A["M2"] / nn), alpha_dev_max=A["amax"],
                         signal_rho_rel_max=A["sig_rho"], signal_K_over_H_max=A["sig_K"])
    full = {k: np.concatenate(v) for k, v in keep.items()}
    return row, full


def line_and_plane(full, N):
    """x-line at (j, k) = (N/2, N/2) and the plane k = N/2 (cells next to 0) from file-order arrays."""
    mid = N // 2
    out = {}
    for k, v in full.items():
        cube = v.reshape(N, N, N)          # [k, j, i]
        out[k] = dict(line=cube[mid, mid, :].copy(), plane=cube[mid, :, :].copy())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--prep", required=True)
    ap.add_argument("--members", nargs="+", required=True)
    ap.add_argument("--cont", action="append", default=[], help="A:B, dumps of B continue member A")
    ap.add_argument("--label", default="series")
    ap.add_argument("--eps", type=float, default=0.2)
    a = ap.parse_args()
    rdir = common.run_dir("analyse_code_runs")
    ltb, szk = common.models(eps=a.eps)
    cont = dict(c.split(":", 1) for c in a.cont)
    out = dict(run_id=common.run_id(), commit=common.git_commit(), run=a.run, prep=a.prep, eps=a.eps,
               label=a.label, members={})
    shown = {}
    for spec in a.members:
        name, prep = (spec.split("=", 1) + [None])[:2]
        prep = prep or name
        z = np.load(os.path.join(a.prep, prep, "slice_t0.npz"))
        N = z["r"].shape[0]
        sl = {k: flat(z[k]) for k in ("r", "bn", "psi", "rho", "r_ltb", "E_dep")}
        files = sorted(glob.glob(os.path.join(a.run, name, "szk.field.*.bin")))
        if name in cont:
            files += sorted(glob.glob(os.path.join(a.run, cont[name], "szk.field.*.bin")))
        rows, seen = [], set()
        for fn in files:
            F = read_field_flat(fn)
            if round(F["t"], 6) in seen:
                continue
            seen.add(round(F["t"], 6))
            row, full = analyse_dump(F, sl, szk, ltb)
            row["file"] = os.path.relpath(fn, a.run)
            if F["t"] == 0.0:
                dE = np.abs(F["E"] - sl["E_dep"]) / sl["E_dep"]
                row["E0_vs_predicted_deposit_rel_max"] = float(np.max(dE))
            rows.append(row)
            shown[name, round(F["t"], 3)] = line_and_plane(full, N)
            print(name, f"tau = {F['t']:.4f}", {r: {k: f"{v:.3g}" for k, v in row[r].items()} for r in REG}, flush=True)
        out["members"][name] = dict(N=N, h=float(z["h"]), prep=prep, dumps=rows)
    # orders between successive members (same dump index)
    names = [s.split("=", 1)[0] for s in a.members]
    orders = []
    for n1, n2 in zip(names[:-1], names[1:]):
        m1, m2 = out["members"][n1], out["members"][n2]
        if m1["N"] == m2["N"]:
            continue
        ratio = m1["h"] / m2["h"]
        for d1 in m1["dumps"]:
            d2 = min(m2["dumps"], key=lambda d: abs(d["tau"] - d1["tau"]), default=None)
            if d2 is None or abs(d2["tau"] - d1["tau"]) > 0.5 * m1["h"]:
                continue
            o = dict(pair=f"{n1}->{n2}", tau1=d1["tau"], tau2=d2["tau"])
            for r in REG:
                o[r] = {}
                for q in ("K_err_over_H_rms", "K_err_over_H_max", "E_rel_rms", "E_rel_max", "chi_rel_rms", "chi_rel_max",
                          "H_over_16pirho_rms", "M_over_16pirho_rms"):
                    e1, e2 = d1[r][q], d2[r][q]
                    o[r][q] = float(math.log(e1 / e2) / math.log(ratio)) if (e1 > 0 and e2 > 0 and np.isfinite(e1 / e2)) else None
            orders.append(o)
            print("order", o["pair"], f"tau = {o['tau1']:.2f}", {r: {k: (f"{v:.2f}" if v is not None else None)
                                                                     for k, v in o[r].items()} for r in REG}, flush=True)
    out["orders"] = orders
    common.dump(os.path.join(rdir, f"code_runs_{a.label}.json"), out)

    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    cols = dict(zip(names, fs.series_colors(len(names))))
    # 1. errors against time
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.95, wspace=0.28, hspace=0.32)
    panels = (("K_err_over_H_rms", r"rms $|K - K_{\rm exact}|/H(\tau)$"), ("E_rel_rms", r"rms $|E - \rho|/\rho$"),
              ("chi_rel_rms", r"rms $|\chi - \chi_{\rm exact}|/\chi$"), ("H_over_16pirho_rms", r"rms $H/(16\pi\bar\rho)$"))
    for ax, (q, lab) in zip(axs.ravel(), panels):
        for nm in names:
            rows = out["members"][nm]["dumps"]
            if not rows:
                continue
            tau = [d["tau"] for d in rows]
            for reg, ls in (("shell", "-"), ("core", ":"), ("outside", "--")):
                v = [max(d[reg][q], 1e-17) if np.isfinite(d[reg][q]) else np.nan for d in rows]
                ax.semilogy(tau, v, ls=ls, marker="o", ms=3, color=cols[nm], label=f"{nm}, {reg}")
        ax.set_xlabel(r"proper time $\tau$")
        ax.set_ylabel(lab)
    axs[0, 0].legend(fontsize=6, ncol=3, loc="lower right")
    common.save_fig(fig, f"fig_code_{a.label}_errors", rdir)
    # 2. error against cell size at each common dump, shell and core, with slope guides
    if len(names) > 1 and len({out["members"][n]["N"] for n in names}) > 1:
        taus = [d["tau"] for d in out["members"][names[0]]["dumps"] if d["tau"] > 0]
        fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
        fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.9, wspace=0.35)
        tcol = fs.series_colors(max(len(taus), 1))
        for ax, (q, lab) in zip(axs, panels[:3]):
            for it, ta in enumerate(taus):
                hs, es, ec = [], [], []
                for nm in names:
                    m = out["members"][nm]
                    d = min(m["dumps"], key=lambda dd: abs(dd["tau"] - ta), default=None)
                    if d is None or abs(d["tau"] - ta) > 0.5 * out["members"][names[0]]["h"]:
                        continue
                    hs.append(m["h"])
                    es.append(d["shell"][q])
                    ec.append(d["core"][q])
                if len(hs) < 2:
                    continue
                ax.loglog(hs, es, "o-", color=tcol[it], ms=4, label=rf"shell, $\tau={ta:.0f}$")
                ax.loglog(hs, ec, "s:", color=tcol[it], ms=3)
            hh = np.array(sorted({out["members"][n]["h"] for n in names}))
            ref = ax.get_lines()[0].get_ydata()[-1] if ax.get_lines() else 1e-3
            ax.loglog(hh, ref * (hh / hh[0]) ** 2, **fs.GUIDE)
            ax.loglog(hh, ref * (hh / hh[0]) ** 4, color="k", lw=1.0, ls=":")
            ax.set_xlabel("cell size h")
            ax.set_ylabel(lab)
        axs[0].legend(fontsize=6, loc="upper left")
        axs[0].set_title(r"dashed: $h^2$, dotted: $h^4$ (from the finest point)", fontsize=7)
        common.save_fig(fig, f"fig_code_{a.label}_convergence", rdir)
    # 3. profiles along x of the finest member and error profiles of every member
    fin = max(names, key=lambda n: out["members"][n]["N"])
    keys = sorted(k for k in shown if k[0] == fin)
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.9, wspace=0.35)
    Nf = out["members"][fin]["N"]
    hf = out["members"][fin]["h"]
    xf = -8.0 + (np.arange(Nf) + 0.5) * hf
    tc = fs.series_colors(len(keys))
    for (nm, ta), c in zip(keys, tc):
        L = shown[nm, ta]
        axs[0].plot(xf, L["K_ex"]["line"], color=c, lw=2.5, alpha=0.35)
        axs[0].plot(xf, L["K"]["line"], color=c, lw=1.0, ls="--", label=rf"$\tau={ta:.0f}$")
        axs[0].plot(xf, L["K_ltb"]["line"], color=c, lw=0.8, ls=":")
        axs[1].semilogy(xf, L["rho"]["line"], color=c, lw=2.5, alpha=0.35)
        axs[1].semilogy(xf, L["E"]["line"], color=c, lw=1.0, ls="--")
        axs[1].semilogy(xf, L["rho_ltb"]["line"], color=c, lw=0.8, ls=":")
    last = {}
    for nm in names:
        ks = [k for k in shown if k[0] == nm]
        if ks:
            last[nm] = max(ks, key=lambda k: k[1])
    for nm, k in last.items():
        L = shown[k]
        N = out["members"][nm]["N"]
        x = -8.0 + (np.arange(N) + 0.5) * out["members"][nm]["h"]
        a_ = (1 + k[1] / szk.t_i) ** (2.0 / 3.0)
        axs[2].semilogy(x, np.abs(L["K"]["line"] - L["K_ex"]["line"]) / (szk.H / a_ ** 1.5) + 1e-17, color=cols[nm],
                        lw=1.0, label=rf"{nm}, $\tau={k[1]:.0f}$")
        axs[2].semilogy(x, np.abs(L["K_ltb"]["line"] - L["K_ex"]["line"]) / (szk.H / a_ ** 1.5) + 1e-17,
                        color="k", lw=0.6, ls=":")
    axs[0].set_xlabel("x")
    axs[0].set_title(f"{fin}: thick exact, dashed AthenaK, dotted LTB", fontsize=7)
    axs[0].set_ylabel(r"$K$")
    axs[0].legend(fontsize=6)
    axs[1].set_xlabel("x")
    axs[1].set_ylabel(r"$E$ and $\rho$")
    axs[2].set_xlabel("x")
    axs[2].set_ylabel(r"$|K - K_{\rm exact}|/H(\tau)$")
    axs[2].set_title("dotted: |LTB - exact| (the non-spherical part)", fontsize=7)
    axs[2].legend(fontsize=6)
    common.save_fig(fig, f"fig_code_{a.label}_profiles", rdir)
    # 4. map of the relative error of E in the plane z ~ 0 at the last dump of the finest member
    if fin in last:
        L = shown[last[fin]]
        fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
        fig.subplots_adjust(left=0.07, right=0.93, bottom=0.13, top=0.9, wspace=0.35)
        ext = (-8, 8, -8, 8)
        im0 = axs[0].imshow(np.log10(L["rho"]["plane"] / L["rho"]["plane"].min()), origin="lower", extent=ext,
                            cmap="viridis")
        fs.side_colorbar(fig, axs[0], im0, r"$\log_{10}\rho/\rho_{\min}$ (exact)")
        err = (L["E"]["plane"] - L["rho"]["plane"]) / L["rho"]["plane"]
        v = np.nanmax(np.abs(err))
        im1 = axs[1].imshow(err, origin="lower", extent=ext, cmap="RdBu_r", vmin=-v, vmax=v)
        fs.side_colorbar(fig, axs[1], im1, r"$(E - \rho)/\rho$")
        for ax in axs:
            ax.set_xlabel("x")
            ax.set_ylabel("y")
        axs[0].set_title(rf"{fin}, $\tau = {last[fin][1]:.0f}$, plane $z \approx 0$", fontsize=8)
        common.save_fig(fig, f"fig_code_{a.label}_maps", rdir)
    print("written", rdir)


if __name__ == "__main__":
    main()
