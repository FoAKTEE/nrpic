#!/usr/bin/env python3
"""Publication-grade Cyclic-Zoom 2x2 visualization of Bug 6 (T_munu filtering, pushers, & SpEC Ecc1)."""
import os, sys
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/emri_1000to1")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz
from analyze_emri_gw import read_single_traj, read_single_trajmet, safe_load_table
from pn_2sf_reference import EMRIReferenceModel

ROOT = "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/emri_1000to1/phaseA_it5"
OUT = "/home/schmidt/ssci-haiyangw/.gemini/antigravity/brain/3d042f0d-783f-49ae-b143-9b8687f98c94"

ref = EMRIReferenceModel()
R0, q = 6.25, 1.0e-3
fe_1sf = float(ref.flux_1sf(R0, q=q))
om0 = R0 ** (-1.5)
fj_1sf = fe_1sf / om0
# Exact 1SF specific orbital L_z loss rate
m_bare_ref = q * (1.0 + q / (np.sqrt(2.0 * np.pi) * 0.2602))
Lz0_ref = 3.4686
dLz_dt_1sf = -fj_1sf / m_bare_ref
gamma_1sf = dLz_dt_1sf / Lz0_ref  # ~ -3.34e-6 (at exact R0=6.25)
ev_1sf = ref.evolve_inspiral("1SF", R0=R0, q=q, t_max=160.0, dt=0.5)


def load_run(nm):
    rdir = os.path.join(ROOT, nm)
    tr = read_single_traj(os.path.join(rdir, f"{nm}.traj.bin"))
    tm = read_single_trajmet(os.path.join(rdir, f"{nm}.trajmet.bin"))
    co = safe_load_table(os.path.join(rdir, f"{nm}.co_0.txt"), min_cols=5, tcol=1)
    if tr is None or len(tr) < 15:
        return None
    t = tr[:, 0]
    xp = tr[:, 2:5]
    up = tr[:, 5:8]
    if co is not None and len(co) > 1:
        xbh = np.column_stack([np.interp(t, co[:, 1], co[:, j]) for j in (2, 3, 4)])
    else:
        xbh = np.zeros_like(xp)
    xr = xp - xbh
    r_iso = np.linalg.norm(xr, axis=1)
    if tm is not None and len(tm) > 1:
        gzz = np.interp(t, tm[:, 0], tm[:, 11])
        Rg = r_iso * np.sqrt(np.maximum(gzz, 1e-6))
    else:
        Rg = r_iso * (1.0 + 0.5 / r_iso) ** 2
    Lz = xr[:, 0] * up[:, 1] - xr[:, 1] * up[:, 0]
    return {"t": t, "Lz": Lz, "Rg": Rg}


def measure_ratio(d, t0=50.0):
    if d is None:
        return np.nan
    t, Lz = d["t"], d["Lz"]
    if t[-1] < t0 + 12.0:
        t0 = max(25.0, float(t[-1]) - 25.0)
    m = t >= t0
    if np.sum(m) < 12:
        return np.nan
    gam = np.polyfit(t[m], Lz[m], 1)[0] / np.mean(Lz[m])
    return gam / gamma_1sf


def rolling_ratio(d, win=24.0):
    t, Lz = d["t"], d["Lz"]
    tc, rc = [], []
    t_start = 42.0
    if t[-1] < t_start + 8.0:
        return np.array([]), np.array([])
    grid = np.arange(t_start, float(t[-1]) - 0.5 * win + 1e-6, 2.0)
    if len(grid) == 0:
        grid = np.array([0.5 * (t_start + float(t[-1]))])
    for tmid in grid:
        m = (t >= max(30.0, tmid - 0.5 * win)) & (t <= min(float(t[-1]), tmid + 0.5 * win))
        if np.sum(m) >= 12:
            gam = np.polyfit(t[m], Lz[m], 1)[0] / np.mean(Lz[m])
            tc.append(tmid)
            rc.append(gam / gamma_1sf)
    return np.array(tc), np.array(rc)


names_all = [
    "A4_lean_l512_cvec", "A3_full_it5_cvec",
    "P1_push_midpoint", "P2_push_boris",
    "D1_step_extrap", "B3_nosse", "D2_mcons_unsplit",
    "B1_diss020", "B2_nf4", "B4_lean_dxp16",
    "D3_nomcons", "D4_nf6_pcs", "D5_nomcons_nf6",
    "M2_nx128_mb32_L512", "E1_spec_ecc1",
]
data = {nm: load_run(nm) for nm in names_all}

print("=== LIVE SNAPSHOT FOR FIGURE ===")
for nm in names_all:
    d = data[nm]
    if d is not None:
        r60 = measure_ratio(d, 60.0)
        r45 = measure_ratio(d, 45.0)
        print(f"  {nm:20s}: t={d['t'][-1]:6.1f}M | ratio(>=45)={r45:5.2f}x | ratio(>=60)={r60:5.2f}x | R_end={d['Rg'][-1]:.3f}M")

cz.use_style()
fig = plt.figure(figsize=(13.6, 8.8))
fig.subplots_adjust(left=0.075, right=0.975, bottom=0.075, top=0.895, wspace=0.50, hspace=0.35)
axes = fig.subplots(2, 2)

# -------------------------------------------------------------------------
# Panel (0,0): Cumulative Delta L_z(t) = L_z(t) - L_z(30 M) vs Exact 1SF
# -------------------------------------------------------------------------
ax = axes[0, 0]
t_ref = np.linspace(30.0, 150.0, 200)
ax.plot(t_ref, 1e3 * dLz_dt_1sf * (t_ref - 30.0), color="k", ls="--", lw=1.8, zorder=10, label="Exact 1SF (RWZ)")

curves_00 = [
    ("A4_lean_l512_cvec",  cz.PAL["blue"],   "-",  1.7, r"mcons=T, $n_f=8$ (gl4)"),
    ("P1_push_midpoint",   "#7B1FA2",        ":",  1.6, r"mcons=T, $n_f=8$ (midpoint)"),
    ("P2_push_boris",      "#00838F",        "-.", 1.3, r"mcons=T, $n_f=8$ (boris)"),
    ("D3_nomcons",         cz.PAL["red"],    "-",  2.2, r"mcons=F, $n_f=8$ (D3)"),
    ("D4_nf6_pcs",         cz.PAL["green"],  "-",  2.0, r"mcons=T, $n_f=6$ (D4)"),
    ("D5_nomcons_nf6",     "#E91E63",        "-",  2.0, r"mcons=F, $n_f=6$ (D5)"),
    ("B2_nf4",             cz.PAL["orange"], "--", 1.5, r"mcons=T, $n_f=4$ (B2)"),
    ("B4_lean_dxp16",      "#795548",        "-.", 1.5, r"mcons=T, $\Delta x_p=M/16$ (B4)"),
]
for nm, col, ls, lw, lbl in curves_00:
    d = data.get(nm)
    if d is None or d["t"][-1] < 32.0:
        continue
    t, Lz = d["t"], d["Lz"]
    m = t >= 30.0
    Lz30 = float(np.interp(30.0, t, Lz))
    ax.plot(t[m], 1e3 * (Lz[m] - Lz30), color=col, ls=ls, lw=lw, label=lbl)

ax.set_xlim(30.0, 150.0)
ax.set_ylim(-2.95, 0.22)
ax.set_xlabel(r"Time $t\,[M]$")
ax.set_ylabel(r"$10^3\,[L_z(t) - L_z(30\,M)]$")
ax.legend(loc="lower left", ncol=1, fontsize=7.2, frameon=False, handlelength=2.0, labelspacing=0.30)
ax.set_title(r"Orbital angular-momentum loss $\Delta L_z(t)$ vs 1SF")

# -------------------------------------------------------------------------
# Panel (0,1): Horizontal bar summary of (dln J_orb / dt) / (1SF target)
# -------------------------------------------------------------------------
ax = axes[0, 1]
bar_spec = [
    ("D5_nomcons_nf6",     r"mcons=F, $n_f=6$ (D5)",             "#E91E63"),
    ("D4_nf6_pcs",         r"mcons=T, $n_f=6$ (D4)",             cz.PAL["green"]),
    ("D3_nomcons",         r"mcons=F, $n_f=8$ (D3)",             cz.PAL["red"]),
    ("B4_lean_dxp16",      r"mcons=T, $\Delta x_p=M/16$ (B4)",   "#795548"),
    ("B2_nf4",             r"mcons=T, $n_f=4$ (B2)",             cz.PAL["orange"]),
    ("D1_step_extrap",     "step_extrap, $n_f=8$ (D1)",          "#607D8B"),
    ("P2_push_boris",      "pusher=boris (P2)",                  "#00838F"),
    ("P1_push_midpoint",   "pusher=midpoint (P1)",               "#7B1FA2"),
    ("A4_lean_l512_cvec",  r"mcons=T, $n_f=8$, gl4 (A4)",        cz.PAL["blue"]),
    ("B1_diss020",         r"diss=0.20, $n_f=8$ (B1)",           "#9E9E9E"),
    ("D2_mcons_unsplit",   "mcons_unsplit (D2)",                 "#B71C1C"),
    ("B3_nosse",           "source=raw (B3)",                    "#4A148C"),
]
ypos, vals, lbls, cols, clipped = [], [], [], [], []
y_i = 0
for nm, lbl, col in bar_spec:
    d = data.get(nm)
    if d is None or d["t"][-1] < 38.0:
        continue
    t_end = float(d["t"][-1])
    t_win0 = 60.0 if t_end >= 80.0 else max(30.0, t_end - 22.0)
    val = measure_ratio(d, t_win0)
    if not np.isfinite(val):
        continue
    ypos.append(y_i)
    vals.append(val)
    lbls.append(lbl)
    cols.append(col)
    clipped.append(min(val, 2.75))
    y_i += 1

ax.axvline(1.0, color="k", ls="--", lw=1.5, zorder=5)
ax.axvspan(0.85, 1.15, color=cz.PAL["green"], alpha=0.10, zorder=0)
ax.barh(ypos, clipped, height=0.68, color=cols, alpha=0.88, edgecolor="none", zorder=3)
for y, v, vc in zip(ypos, vals, clipped):
    if v > 2.75:
        ax.text(2.70, y, rf"$\rightarrow {v:.1f}\times$", va="center", ha="right", color="white", fontsize=7.6, fontweight="bold")
    elif 0.62 <= v <= 1.05:
        ax.text(vc - 0.05, y, rf"${v:.2f}\times$", va="center", ha="right", color="white", fontsize=7.6, fontweight="bold", zorder=6)
    else:
        ax.text(vc + 0.05, y, rf"${v:.2f}\times$", va="center", ha="left", color="k", fontsize=7.6)

ax.set_yticks(ypos)
ax.set_yticklabels(lbls, fontsize=8.0)
ax.invert_yaxis()
ax.set_xlim(0.0, 2.90)
ax.set_xlabel(r"Inspiral rate ratio $(\dot J_{\rm orb}/J_{\rm orb})\,/\,(-F_J^{\rm 1SF}/J_{\rm orb})$")
ax.set_title(r"Bug 6 ablation summary (exact 1SF $= 1.0\times$)")

# -------------------------------------------------------------------------
# Panel (1,0): Time-resolved rolling inspiral rate gamma(t) / gamma_1SF
# -------------------------------------------------------------------------
ax = axes[1, 0]
ax.axhline(1.0, color="k", ls="--", lw=1.6, zorder=10, label=r"Exact 1SF ($1.0\times$)")
ax.axhspan(0.85, 1.15, color=cz.PAL["green"], alpha=0.10, zorder=0)

roll_curves = [
    ("A4_lean_l512_cvec",  cz.PAL["blue"],   "-",  1.7, r"mcons=T, $n_f=8$ (A4)"),
    ("D3_nomcons",         cz.PAL["red"],    "-",  2.2, r"mcons=F, $n_f=8$ (D3)"),
    ("D4_nf6_pcs",         cz.PAL["green"],  "-",  2.0, r"mcons=T, $n_f=6$ (D4)"),
    ("D5_nomcons_nf6",     "#E91E63",        "-",  2.0, r"mcons=F, $n_f=6$ (D5)"),
    ("B1_diss020",         "#9E9E9E",        ":",  1.5, r"diss=0.20 (B1)"),
    ("B2_nf4",             cz.PAL["orange"], "--", 1.5, r"mcons=T, $n_f=4$ (B2)"),
    ("B4_lean_dxp16",      "#795548",        "-.", 1.5, r"$\Delta x_p=M/16$ (B4)"),
]
for nm, col, ls, lw, lbl in roll_curves:
    d = data.get(nm)
    if d is None:
        continue
    tc, rc = rolling_ratio(d, win=24.0)
    if len(tc) > 0:
        ax.plot(tc, rc, color=col, ls=ls, lw=lw, label=lbl)

ax.set_xlim(40.0, 142.0)
ax.set_ylim(0.0, 3.45)
ax.set_xlabel(r"Window center time $t\,[M]$ ($24\,M$ rolling fit)")
ax.set_ylabel(r"Instantaneous $\gamma_{\rm orb}(t)\,/\,\gamma_{\rm 1SF}$")
ax.legend(loc="upper right", ncol=2, fontsize=7.4, frameon=False, columnspacing=1.0, labelspacing=0.32)
ax.set_title(r"Time evolution of inspiral rate: mcons=F vs mcons=T")

# -------------------------------------------------------------------------
# Panel (1,1): Orbital radius R_geom(t) — Ecc0 vs SpEC Ecc1 vs 1SF RWZ
# -------------------------------------------------------------------------
ax = axes[1, 1]
ax.plot(ev_1sf["t"], ev_1sf["R"], color="k", ls="--", lw=1.7, zorder=10, label="Exact 1SF (RWZ)")
rad_curves = [
    ("A4_lean_l512_cvec",  cz.PAL["blue"],   "-",  1.7, r"A4 Ecc0 ($\omega_{\rm sc}=1.0$)"),
    ("D3_nomcons",         cz.PAL["red"],    "-",  2.0, r"D3 mcons=F (Ecc0)"),
    ("D4_nf6_pcs",         cz.PAL["green"],  "-",  1.8, r"D4 $n_f=6$ (Ecc0)"),
    ("M2_nx128_mb32_L512", "#FF6F00",        "-.", 1.8, r"M2 $32^3$ MB (Ecc0)"),
    ("E1_spec_ecc1",       "#9C27B0",        "-",  2.3, r"E1 SpEC Ecc1 ($\omega_{\rm sc}=0.9977$)"),
]
for nm, col, ls, lw, lbl in rad_curves:
    d = data.get(nm)
    if d is None:
        continue
    ax.plot(d["t"], d["Rg"], color=col, ls=ls, lw=lw, label=lbl)

ax.set_xlim(0.0, 150.0)
ax.set_ylim(6.10, 6.72)
ax.set_xlabel(r"Time $t\,[M]$")
ax.set_ylabel(r"Areal separation $R_{\rm geom}(t)\,[M]$")
ax.legend(loc="upper left", ncol=1, fontsize=7.6, frameon=False)
ax.set_title(r"Orbit $R_{\rm geom}(t)$: Ecc0 vs SpEC/SpECTRE Ecc1")

for row in axes:
    for a in row:
        a.tick_params(which="both", direction="in", top=True, right=True)

fig.suptitle(r"Bug 6 Investigation: $T_{\mu\nu}$ Filtering, Pushers, & SpEC Eccentricity Control ($R_0=6.25\,M$, $q=10^{-3}$)", fontsize=12.0, y=0.955)
out_png = os.path.join(OUT, "fig_bug6_tmunu_ablation.png")
fig.savefig(out_png, dpi=300)
plt.close(fig)
print(f"Wrote {out_png}")
