#!/usr/bin/env python3
"""Physics figure: Shapiro-Teukolsky relativistic cluster migration, dispersal, & collapse phase space.

Reduces Wave 4B M5c `.vlasov.*.bin` snapshots into `vlasov_gr/paper/data/physics_st_mig_disp.npz`
and renders `vlasov_gr/paper/figures/fig_physics_st_migration_dispersal.{pdf,png}`.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib.ticker as mticker

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/python")
import czstyle as cz  # noqa: E402
from nrpic.vlasov_gr import read_grlbv  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
DATA_OUT = os.path.join(PAPER_DIR, "data", "physics_st_mig_disp.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_physics_st_migration_dispersal")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
M5C_BASE = os.path.join(SCRATCH, "runs", "repro_wave4b", "m5c")


def radial_state(snap_path: str):
    s = read_grlbv(snap_path)
    x = s["x"]
    u = s["u_bar"][:, 0, :]
    m = s["m"][:, 0]
    r = np.linalg.norm(x, axis=1)
    rm = np.maximum(r, 1e-30)
    ur = np.sum(x * u, axis=1) / rm
    w = 1.0e4 * m / max(float(np.sum(m)), 1e-30)
    return float(s["time"]), r, ur, w


def init_envelope(r: np.ndarray, ur: np.ndarray, nbins: int = 22):
    r_max = float(np.max(r))
    edges = np.linspace(0.0, r_max, nbins + 1)
    rc, umx = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (r >= a) & (r <= b)
        if np.any(m):
            rc.append(0.5 * (a + b))
            umx.append(float(np.max(np.abs(ur[m]))))
    rc = np.asarray(rc)
    umx = np.asarray(umx)
    r_loop = np.concatenate([[0.0], rc, [r_max, r_max], rc[::-1], [0.0, 0.0]])
    u_loop = np.concatenate([[umx[0]], umx, [0.0, 0.0], -umx[::-1], [-umx[0], umx[0]]])
    return r_loop.astype(np.float32), u_loop.astype(np.float32)


def build_npz() -> dict:
    out = {}
    panels = [
        ("mig100",  "st_yc0500_mig_10k_hyb",  "st_yc0500_mig_10k_hyb.vlasov.00002.bin",  (0.0, 26.0),  (-1.6, 1.6)),
        ("mig300",  "st_yc0500_mig_10k_hyb",  "st_yc0500_mig_10k_hyb.vlasov.00006.bin",  (0.0, 31.0),  (-1.6, 1.6)),
        ("disp300", "st_yc0283_vp01_100k_hyb", "st_yc0283_vp01_100k_hyb.vlasov.00006.bin", (0.0, 145.0), (-0.18, 0.88)),
        ("col50",   "st_yc0500_vp01_100k_hyb", "st_yc0500_vp01_100k_hyb.vlasov.00001.bin", (0.0, 5.2),   (-2.4, 2.2)),
    ]
    for key, run, fn, rlim, ulim in panels:
        t, r, ur, w = radial_state(os.path.join(M5C_BASE, run, fn))
        H, xe, ye = np.histogram2d(r, ur, bins=56, range=[rlim, ulim], weights=w)
        out[f"{key}_t"] = np.float64(t)
        out[f"{key}_H"] = H.astype(np.float32)
        out[f"{key}_xe"] = xe.astype(np.float32)
        out[f"{key}_ye"] = ye.astype(np.float32)
        print(f"  [{key:7s}] t={t:5.1f}M max_bin={np.max(H):.2f} r95={np.percentile(r,95):.2f} ur(min/max)=({np.min(ur):.2f}/{np.max(ur):.2f})", flush=True)

    # Extract t=0 envelopes for yc=0.500 and yc=0.283
    _, r0_5, ur0_5, _ = radial_state(os.path.join(M5C_BASE, "st_yc0500_mig_10k_hyb", "st_yc0500_mig_10k_hyb.vlasov.00000.bin"))
    rl5, ul5 = init_envelope(r0_5, ur0_5)
    out["env05_r"] = rl5
    out["env05_u"] = ul5

    _, r0_2, ur0_2, _ = radial_state(os.path.join(M5C_BASE, "st_yc0283_vp01_100k_hyb", "st_yc0283_vp01_100k_hyb.vlasov.00000.bin"))
    rl2, ul2 = init_envelope(r0_2, ur0_2)
    out["env028_r"] = rl2
    out["env028_u"] = ul2

    os.makedirs(os.path.dirname(DATA_OUT), exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"Saved {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def main():
    cz.use_style()
    D = build_npz()

    W, H = 7.8, 5.7
    fig = plt.figure(figsize=(W, H))

    left, gap_x, gap_y, right, top, bot = 0.68, 0.76, 0.56, 0.86, 0.25, 0.56
    cb_w, cb_pad = 0.14, 0.12
    pw = (W - left - right - gap_x - cb_w - cb_pad) / 2.0
    ph = (H - top - bot - gap_y) / 2.0

    axes = [
        cz.inch_axes(fig, left,              bot + ph + gap_y, pw, ph),
        cz.inch_axes(fig, left + pw + gap_x, bot + ph + gap_y, pw, ph),
        cz.inch_axes(fig, left,              bot,              pw, ph),
        cz.inch_axes(fig, left + pw + gap_x, bot,              pw, ph),
    ]

    cmap = cz.CMAP["dens"]
    norm = LogNorm(vmin=0.25, vmax=2.2e2)

    panel_meta = [
        ("mig100",  "env05",  r"Migrate ($y_c=0.500$, $10^4$, $t=100\,M$)" "\n" r"Envelope breaks out past $R_0=4.5M$"),
        ("mig300",  "env05",  r"Migrated halo ($y_c=0.500$, $10^4$, $t=300\,M$)" "\n" "Core\u2013halo breathing shells " r"($r_{50}=9.8M$)"),
        ("disp300", "env028", r"Dispersal ($y_c=0.283$, $10^5$, $t=300\,M$)" "\n" r"Ballistic radial outflow $u_r \propto r$"),
        ("col50",   "env05",  r"Collapse ($y_c=0.500$, $10^5$, $t=50\,M$)" "\n" r"Core infall & crossing ($t_{\rm AH}=70.8\,M$)"),
    ]

    mesh_ref = None
    for idx, (ax, (key, ekey, note)) in enumerate(zip(axes, panel_meta)):
        H2 = np.ma.masked_less(D[f"{key}_H"].T, 0.25)
        xe, ye = D[f"{key}_xe"], D[f"{key}_ye"]
        mesh_ref = ax.pcolormesh(xe, ye, H2, cmap=cmap, norm=norm, shading="flat", rasterized=True)
        ax.axhline(0.0, ls=":", color="0.45", lw=0.75)
        ax.plot(D[f"{ekey}_r"], D[f"{ekey}_u"], color="k", ls="--", lw=1.0, alpha=0.75, label=r"$t=0$ support")
        ax.set_xlim(float(xe[0]), float(xe[-1]))
        ax.set_ylim(float(ye[0]), float(ye[-1]))
        ax.set_xlabel(r"Radius $r\,[M]$")
        if idx % 2 == 0 or key == "col50":
            ax.set_ylabel(r"Radial 4-velocity $u_r$")
        if key == "mig300":
            ax.set_yticklabels([])
        ax.text(0.96, 0.94, note, transform=ax.transAxes, ha="right", va="top", fontsize=6.3, color="0.12")
        if key == "mig100":
            ax.legend(loc="lower right", fontsize=6.2, frameon=False)

    cax = cz.inch_axes(fig, left + 2 * pw + gap_x + cb_pad, bot, cb_w, 2 * ph + gap_y)
    cb = fig.colorbar(mesh_ref, cax=cax)
    cb.set_label(r"Rest-mass density $10^4\,\Delta M / M_0$ per bin", fontsize=7.6)
    cb.set_ticks([1, 10, 100])
    cb.ax.minorticks_off()
    cb.ax.tick_params(labelsize=7.2)

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
