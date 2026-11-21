#!/usr/bin/env python3
"""Numerical ledger of the working note of core (its Supplemental Material).

Every number the note states, with the registered run that produced it or the source
locator it was read from, and the claim of the fresh verifier that recomputed it
(stage/G2/VERIFIER.md, rows V1 to V11; empty where no second agent has checked it).
Rows of the data figures come from OUTDIR/numbers_*.json (written by the figure
scripts in the same run); the other rows are read here from the documents named in
their source column.

    ledger.py OUTDIR   (writes OUTDIR/tables/ledger.tex and OUTDIR/tables/ledger.json)
"""
import json
import sys
from pathlib import Path

# figure rows: key -> quantity (wording of the ledger)
FIG = [
    ("Row 1: Kerr passage, a = 0.9 M, e = 0.99, dt = 0.01 M to 230 M (regression G)", [
        ("geo.E0", "E at t = 0", 5), ("geo.Lz0", "L_z at t = 0", 5), ("geo.Q0", "Q at t = 0", 4),
        ("geo.mid_ks_dt0.01.max_dE", "midpoint, analytic metric: largest |dE/E|", 4),
        ("geo.mid_ks_dt0.01.max_dLz", "midpoint, analytic metric: largest |dL_z/L_z|", 4),
        ("geo.mid_ks_dt0.01.max_dQ", "midpoint, analytic metric: largest |dQ/Q|", 4),
        ("geo.bsym_ks_dt0.01.max_dE", "Boris symmetric, analytic: largest |dE/E|", 4),
        ("geo.bsym_ks_dt0.01.max_dLz", "Boris symmetric, analytic: largest |dL_z/L_z|", 4),
        ("geo.bsym_ks_dt0.01.max_dQ", "Boris symmetric, analytic: largest |dQ/Q|", 4),
        ("geo.mid_lat_dt0.01.max_dE", "midpoint, Hermite lattice: largest |dE/E|", 4),
        ("geo.mid_lat_dt0.01.max_dLz", "midpoint, Hermite lattice: largest |dL_z/L_z|", 4),
        ("geo.mid_lat_dt0.01.max_dQ", "midpoint, Hermite lattice: largest |dQ/Q|", 4),
        ("geo.bchol_lat_dt0.01.max_dE", "Boris Cholesky, lattice: largest |dE/E|", 4),
        ("geo.bchol_lat_dt0.01.max_dLz", "Boris Cholesky, lattice: largest |dL_z/L_z|", 4),
        ("geo.bchol_lat_dt0.01.max_dQ", "Boris Cholesky, lattice: largest |dQ/Q|", 4),
        ("geo.mid.order_pair1", "midpoint: order in dt of the final position error (0.005-0.01)", 5),
        ("geo.mid.order_pair2", "midpoint: same (0.01-0.02)", 5),
        ("geo.bsym.order_pair1", "Boris symmetric: order (0.005-0.01)", 5),
        ("geo.bsym.order_pair2", "Boris symmetric: order (0.01-0.02)", 5),
        ("geo.bchol.order_pair1", "Boris Cholesky: order (0.005-0.01)", 5),
        ("geo.bchol.order_pair2", "Boris Cholesky: order (0.01-0.02)", 5),
        ("geo.r_peri", "pericentre radius (M)", 7), ("geo.t_peri", "pericentre time (M)", 5),
    ]),
    ("Row 2: Oppenheimer-Snyder collapse, lattice of 9328 particles", [
        ("os.sc.n0", "particles at t = 0", 0),
        ("os.sc.t_first", "reference run: first apparent horizon (M)", 6),
        ("os.sc.m_first", "reference run: M_AH/M at formation", 7),
        ("os.sc.max_dev_to60", "reference run: largest |M_AH/M - 1| to 60 M", 4),
        ("os.sc.m_at20", "reference run: M_AH/M near 20 M", 7),
        ("os.sc.m_at40", "reference run: M_AH/M near 40 M", 7),
        ("os.sc.m_at60", "reference run: M_AH/M near 60 M", 7),
        ("os.sc.dev_above_1e-3_from", "reference run: first search with |M_AH/M - 1| > 1e-3 (M)", 4),
        ("os.sc.stays_above_1e-3_from", "reference run: above 1e-3 at every search from (M)", 4),
        ("os.sc.t_all_removed", "reference run: all particles removed by (M)", 4),
        ("os.O.t_first", "merged card build: first apparent horizon (M)", 6),
        ("os.O.m_first", "merged card build: M_AH/M at formation", 7),
        ("os.O.max_dev_to25", "merged card build: largest |M_AH/M - 1| to 25 M", 4),
    ]),
    ("Row 3: prolate collapse, 10^4 particles", [
        ("prolate.m16.t_first", "finest cells M/16: first apparent horizon (M)", 4),
        ("prolate.m16.m_first", "M/16: M_AH/M at formation", 4),
        ("prolate.m16.m_max", "M/16: largest M_AH/M", 4),
        ("prolate.m16.m_last", "M/16: M_AH/M at the last search (44.75 M)", 4),
        ("prolate.m8.t_first", "finest cells M/8: first apparent horizon (M)", 4),
        ("prolate.m8.m_first", "M/8: M_AH/M at formation", 4),
        ("prolate.m8.m_max", "M/8: largest M_AH/M", 4),
        ("prolate.m8.m_last", "M/8: M_AH/M at the last search (44.75 M)", 4),
    ]),
    ("Row 4: cluster sequence, 10^4 particles, one-per-cent inward kick", [
        ("cl.yc0900.alpha_min", "y_c = 0.900: smallest central lapse to 300 M", 4),
        ("cl.yc0900.alpha_max", "y_c = 0.900: largest central lapse to 300 M", 4),
        ("cl.yc0900.np_end", "y_c = 0.900: particles kept (of 10^4)", 0),
        ("cl.yc0819.alpha_min", "y_c = 0.819: smallest central lapse to 300 M", 4),
        ("cl.yc0819.alpha_max", "y_c = 0.819: largest central lapse to 300 M", 4),
        ("cl.yc0819.np_end", "y_c = 0.819: particles kept", 0),
        ("cl.yc0605.t_first_ah", "y_c = 0.605: first apparent horizon (M)", 4),
        ("cl.yc0605.m_ah_end", "y_c = 0.605: M_AH/M at the end", 5),
        ("cl.yc0500.t_first_ah", "y_c = 0.500: first apparent horizon (M)", 5),
        ("cl.yc0500.m_ah_end", "y_c = 0.500: M_AH/M at the end", 5),
        ("cl.yc0283.alpha_at270", "y_c = 0.283: central lapse at 270 M", 5),
        ("cl.yc0283.np_end", "y_c = 0.283: particles kept", 0),
        ("bis.0.72.mean_alpha_200_300", "M/4 bisection, y_c = 0.72: mean central lapse 200-300 M", 4),
        ("bis.0.70.mean_alpha_200_300", "y_c = 0.70: same", 4),
        ("bis.0.69.mean_alpha_200_300", "y_c = 0.69: same", 4),
        ("bis.0.67.mean_alpha_200_300", "y_c = 0.67: same", 4),
        ("bis.0.66.mean_alpha_200_300", "y_c = 0.66: same", 4),
        ("bis.0.64.mean_alpha_200_300", "y_c = 0.64: same", 4),
        ("bis.0.605.mean_alpha_200_250", "control y_c = 0.605: mean central lapse 200-250 M", 4),
    ]),
]

P = "paper main.tex"   # refs/arxiv_2611.12831/src/main.tex (untracked), line numbers
LOC = [
    ("Paper (Wu and Most), read with line locators", [
        ("Kerr passage, midpoint analytic: largest errors E, L_z, Q", "2.8e-8, round-off, 1.3e-7", f"{P} 824-833", ""),
        ("Kerr passage, Boris Cholesky lattice: same", "2.0e-6, 3.8e-6, 5.3e-5", f"{P} 824-833", ""),
        ("Oppenheimer-Snyder: relative horizon-mass error", "<~ 1e-3", f"{P} 945", ""),
        ("Oppenheimer-Snyder fiducial lattice particles", "998592", f"{P} 917", ""),
        ("prolate collapse: first apparent horizon (M)", "32", f"{P} 971", ""),
        ("clusters y_c = 0.605, 0.500: first horizons (M)", "109, 73", f"{P} 1138", ""),
        ("migration of y_c = 0.5: late mean central lapse", "0.833530", f"{P} 1199", ""),
    ]),
    ("Turning point and bisection protocol", [
        ("turning point of the sequence y_c*", "0.6796", "core-20261115-152805-47d8f25", ""),
        ("E_b/M_0 at y_c*", "0.036058", "core-20261115-152805-47d8f25", ""),
        ("card time of the seven M/4 bisection runs (card-hours)", "2.0", "verify/LADDER.md row 4, wave 2", ""),
    ]),
    ("Constraints and conservation (C3)", [
        ("homogeneous universe: H-norm2 (proper-volume integral of H^2)", "3.7e-10", "core-20261115-065903-3629622", "V4"),
        ("homogeneous universe: Theta-norm2 (proper-volume integral of Theta^2)", "1.1e-11", "core-20261115-065903-3629622", "V4"),
        ("homogeneous universe: pointwise max|Theta|, max|H|", "2.27e-7, 1.69e-6", "core-20261121-212248-a7972d1", "V4"),
        ("homogeneous universe against Einstein-de Sitter: lapse, mean K, proper volume (relative)", "1.9e-7, 3.8e-7, 1.1e-6", "core-20261121-212248-a7972d1", "V4"),
        ("dust collapse: deposition identity (mesh integral against particle sum)", "1.0e-15", "core-20261115-065901-3629622", "V5a"),
        ("MPI, periodic cosmology on 2, 4 ranks: particle positions against one rank", "1.6e-14", "core-20261119-163641-ddb47b0", "V5b"),
        ("MPI, periodic cosmology on 1, 2, 4 ranks: deposition identity", "1e-14", "core-20261119-163641-ddb47b0", "V5b"),
        ("Bowen-York puncture after the solve, card and processor: max|H|", "6.4e-12", "core-20261121-154700-2de4974", ""),
    ]),
    ("Restart (fresh verifier, release core-v0.6 processor build)", [
        ("periodic Z4c, 4096 particles, restart at cycle 10 of 20: differing bytes", "0", "core-20261121-213713-952a0c4", "V6"),
        ("Oppenheimer-Snyder, refinement, outflow faces, restart at cycle 3 of 6: mesh words differing", "64 per cent", "core-20261121-215228-d1f36f4", "V6"),
        ("same: median, 99th percentile of the relative difference", "2.8e-13, 1.7e-7", "core-20261121-215228-d1f36f4", "V6"),
        ("same: histories within", "5e-13", "core-20261121-215228-d1f36f4", "V6"),
    ]),
    ("Capabilities of core-v0.3 to core-v0.6 (package runs; verifier's rerun where named)", [
        ("v0.3 Newtonian point mass: rms relative force error at N = 32, 64; order", "1.61e-2, 4.94e-3; 1.70", "core-20261115-150209-3629622", "V7a"),
        ("same: tracers at r >= 0.5", "706", "core-20261121-212516-0f0a65b", "V7a"),
        ("v0.3 collisions, box relaxation: Kolmogorov-Smirnov p of the four end states", "0.26 to 0.90", "core-20261115-134036-5684674", "V8"),
        ("v0.3 scalar field test 1a: spatial orders for nghost 2, 3, 4", "1.991, 3.957, 5.918", "core-20261115-150004-3629622", "V9"),
        ("same: Omega/omega_h - 1 at dt = 1/512", "-1.21e-9 to -1.31e-9", "core-20261121-212422-b616c6e", "V9"),
        ("v0.4 solver T1: relative error of psi - 1 at the centre, code, dx = 1, 0.5, 0.25", "-1.92e-2, -5.22e-3, -1.33e-3", "core-20261121-214108-0960a46", "V10a"),
        ("v0.6 solver on static refinement: relative error of psi - 1 over r < 1, refined against uniform", "-5.01e-3, -5.03e-3", "core-20261119-153510-d1eaa30", "V10b"),
        ("v0.6 Fourier solver, exact pancake: slab I_xx error, spectral and seven-point", "9.1e-6, 3.1e-3", "core-20261119-160919-c6a7279", "V7b"),
        ("v0.6 faces: stock boundary-layer |H| over the stencil estimate", "0.79", "core-20261119-143938-eded041", "V11"),
        ("v0.6 faces: reduction of the layer by the fall-off ghosts", "12", "core-20261121-214547-7a21ed3", "V11"),
        ("byte regression of v0.6 against v0.5", "75 of 75", "core-20261121-130202-7cf7db8", ""),
        ("byte regression of v0.5 against v0.4", "PASS", "core-20261121-063859-e410ee3", ""),
        ("byte regression of v0.4 against v0.3", "PASS", "core-20261120-221607-4985804", ""),
        ("card check of the merged v0.6 card build: cases", "15, PASS", "core-20261121-154700-2de4974", ""),
    ]),
    ("Known defects (numbers of other owners, not recomputed by core)", [
        ("relaxed lapse, vacuum puncture: horizon-mass band 100-199.5 M with lapse_leak = 0.5", "-5.6e-4 to +1.27e-3", "D-20261121-125909-06f856e, D-20261121-144657-cf510fc", ""),
        ("same without the option", "-4.8e-5 to +2.0e-5", "D-20261121-125909-06f856e, D-20261121-144657-cf510fc", ""),
        ("Gamma-driver shift: stability bound dt/dx (nghost 4, RK4, dissipation 0.5)", "0.685", "A-20261121-212800-d7f31a4", ""),
        ("rule until the step limit counts the gauge speeds: cfl_number at most", "0.6", "coord/DECISIONS/0027 item 2", ""),
    ]),
]


def fmt(v, sig):
    if isinstance(v, int) or sig == 0:
        return str(int(v))
    if v == 0:
        return "0"
    a = abs(v)
    if 1e-3 <= a < 1e4:
        return f"{v:.{sig}g}"
    return f"{v:.{max(sig - 1, 0)}e}"


def tex(s):
    return (s.replace("\\", "/").replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")
            .replace("#", r"\#").replace("<~", r"$\lesssim$").replace(">=", r"$\geq$")
            .replace("^4", r"$^4$").replace("^2", r"$^2$").replace("|", r"$|$"))


def main():
    out = Path(sys.argv[1])
    (out / "tables").mkdir(parents=True, exist_ok=True)
    nums = {}
    for f in sorted(out.glob("numbers_*.json")):
        nums.update(json.loads(f.read_text()))
    rows = []
    for head, items in FIG:
        rows.append(("head", head))
        for key, q, sig in items:
            r = nums[key]
            note = f" ({r['note']})" if r.get("note") else ""
            rows.append(("row", q + note, fmt(r["value"], sig), r["source"], r.get("verifier", "")))
    for head, items in LOC:
        rows.append(("head", head))
        for q, v, s, ver in items:
            rows.append(("row", q, v, s, ver))
    lines = [r"\begin{longtable}{@{}r p{0.46\textwidth} p{0.15\textwidth} p{0.25\textwidth} l@{}}",
             r"\hline\hline", r"\# & Quantity & Value & Source & Verifier\\ \hline", r"\endhead",
             r"\hline\hline", r"\endlastfoot"]
    n = 0
    js = []
    for r in rows:
        if r[0] == "head":
            lines.append(r"\multicolumn{5}{@{}l}{\textit{" + tex(r[1]) + r"}}\\")
            continue
        n += 1
        _, q, v, s, ver = r
        js.append(dict(n=n, quantity=q, value=v, source=s, verifier=ver))
        lines.append(f"{n} & {tex(q)} & {tex(v)} & \\texttt{{\\footnotesize {tex(s)}}} & {ver}\\\\")
    lines.append(r"\end{longtable}")
    (out / "tables" / "ledger.tex").write_text("\n".join(lines) + "\n")
    (out / "tables" / "ledger.json").write_text(json.dumps(js, indent=1))
    nv = sum(1 for r in js if r["verifier"])
    print(f"ledger: {n} rows, {nv} recomputed by the fresh verifier")


if __name__ == "__main__":
    main()
