"""Unit tests of tmb.py (run: python3 -E test_tmb.py; exit code 0 when all pass).

1. Gauss-Legendre integrals against adaptive quadrature (also scaled, large w).
2. Limits of the equation of state: gamma -> 5/3 (b w -> 0), gamma -> 4/3 (b w -> 1).
3. Killing-energy form (prediction P3 of JOURNAL.md): the moments of
   f(E) = e^{-E/b} - e^{-1/b} at lapse e^Phi = 1 - b w equal F21's integrals.
4. Convergence of the TOV solve in the tolerance and the start radius.
5. Rayleigh quotient of zeta = r^3 equals 9 P0 (<gamma> - gamma_cr): the closed form of
   gamma_cr (main.tex:208-219) against the un-integrated pulsation operator.
6. Finite-element Rayleigh-Ritz: convergence in N, never above the trial value.
7. Fixed gamma = 4/3 in the Newtonian limit: marginal mode, nearly homologous.
"""
import math
import sys

import tmb

FAIL = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    if not ok:
        FAIL.append(name)


# 1 ---------------------------------------------------------------------------
worst = 0.0
for b in (0.001, 0.01, 0.1, 0.5, 5.0):
    for w in (1e-3, 0.05, 0.5, 1.5, 4.0, 30.0, 300.0):
        if b * w >= 0.999:
            continue
        for scaled in (False, True):
            if not scaled and w > 50:
                continue
            a = tmb.integrals(b, w, scaled)
            q = tmb.integrals_quad(b, w, scaled)
            worst = max(worst, max(abs(x / y - 1) for x, y in zip(a, q)))
check("integrals GL96 vs quad", worst < 1e-10, f"max rel diff {worst:.2e}")

# 2 ---------------------------------------------------------------------------
g_nr = tmb.gamma_local(0.001, 0.01)
g_ur = tmb.gamma_local(0.5, 1.999999 - 1e-6)
check("gamma -> 5/3 at b w = 1e-5", abs(g_nr - 5 / 3) < 1e-4, f"{g_nr:.6f}")
check("gamma -> 4/3 at b w -> 1", abs(g_ur - 4 / 3) < 2e-2, f"{g_ur:.6f}")
v_nr = tmb.v_over_c(0.001, 300.0)   # untruncated MB limit: v^2 = 3 kT/m, kT = b/(1-bw)
check("v -> sqrt(3 kT/m) for w >> 1, b << 1", abs(v_nr / math.sqrt(3 * 0.001 / 0.7) - 1) < 3e-3,
      f"{v_nr:.6f} vs {math.sqrt(3 * 0.001 / 0.7):.6f}")

# 3 ---------------------------------------------------------------------------
worst = 0.0
for b in (0.1, 0.3, 0.5):
    for w in (0.2, 1.0, 3.0):
        if b * w >= 0.99:
            continue
        nn, rho, p = tmb.phase_space_moments(b, w)
        In, Ir, Iu, Ip = tmb.integrals(b, w)
        sc = math.exp(-1.0 / b)
        ref = (tmb.K4 * In * sc, tmb.K4 * Ir * sc, 2 / 3 * tmb.K4 * Ip * sc)
        worst = max(worst, max(abs(x / y - 1) for x, y in zip((nn, rho, p), ref)))
check("f depends on Killing energy only (P3)", worst < 1e-10, f"max rel diff {worst:.2e}")

# 4 ---------------------------------------------------------------------------
ref = tmb.solve(0.1, 3.2)
old = tmb.RTOL
tmb.RTOL = 1e-10
lo = tmb.solve(0.1, 3.2)
tmb.RTOL = old
d = max(abs(lo[k] / ref[k] - 1) for k in ("E", "Erest", "R", "gavg", "gcr"))
dB = abs(lo["B"] / ref["B"] - 1)
check("TOV tolerance 1e-10 vs 1e-12", d < 1e-9 and dB < 1e-7, f"max rel {d:.1e}, B {dB:.1e}")

# 5 ---------------------------------------------------------------------------
for b, w0 in ((0.1, 3.2), (0.1, 4.0515), (0.5, 0.3)):
    e = tmb.solve(b, w0)
    ratio = tmb.pulsation(b, w0, N=200)["check"]
    diff = ratio - (e["gavg"] - e["gcr"])
    check(f"Rayleigh(r^3)/9P0 = <gamma>-gamma_cr  b={b} w0={w0}", abs(diff) < 2e-5,
          f"{ratio:+.6f} vs {e['gavg'] - e['gcr']:+.6f}")

# 6 ---------------------------------------------------------------------------
vals = [tmb.pulsation(0.1, 3.6, N=n)["omega2"][0] for n in (200, 400, 800, 1600)]
mono = all(vals[i + 1] <= vals[i] + 1e-12 for i in range(len(vals) - 1))
conv = abs(vals[-1] - vals[-2]) <= 1e-4 * abs(vals[-1])
check("FEM Rayleigh-Ritz decreases and converges in N (b=0.1, w0=3.6)", mono and conv,
      " ".join(f"{v:.6e}" for v in vals))
d = tmb.pulsation(0.1, 3.2, N=400)
check("FEM lowest omega^2 below the trial value", d["omega2"][0] <= d["trial"],
      f"{d['omega2'][0]:.4e} <= {d['trial']:.4e}")

# 7 ---------------------------------------------------------------------------
# fixed gamma = 4/3 on a nearly Newtonian model (C = 0.004): Newtonian theory gives a
# marginal homologous mode (omega^2 = 0, xi ~ r); GR makes it slightly unstable, and the
# trial xi = r e^Phi should be close to the eigenfunction, so FEM ~ trial < 0.
d = tmb.pulsation(0.1, 0.1, N=400, gamma_mode=4.0 / 3.0)
rel = d["omega2"][0] / d["trial"] - 1
check("gamma=4/3, C=0.004: omega^2 < 0 and FEM within 5% of the trial",
      d["omega2"][0] < 0 and d["trial"] < 0 and abs(rel) < 0.05,
      f"FEM {d['omega2'][0]:.4e}, trial {d['trial']:.4e}")
rho_c = tmb.local(0.1, 0.1)[1]
check("gamma=4/3, C=0.004: |omega^2| << 4 pi rho_c (Newtonian marginality)",
      abs(d["omega2"][0]) < 0.05 * 4 * math.pi * rho_c,
      f"|omega^2|/(4 pi rho_c) = {abs(d['omega2'][0]) / (4 * math.pi * rho_c):.3e}")

print("ALL PASS" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
