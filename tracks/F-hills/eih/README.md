# eih: first post-Newtonian (EIH) three-body reference for the Hills passages

Helper package of F-hills (wave 3a). The second check of G0 (`stage/G0/SECOND_CHECK.md`, "Which
tests would tell", item 3) found that neither the Newtonian baseline (`newton3`) nor the
geodesic-plus-Newtonian baseline (HRNA, `geodesic_binary`) is a controlled approximation at mass
ratio ten. This package adds the first post-Newtonian (Einstein-Infeld-Hoffmann) equations of
motion for three point masses with the large black hole free, tests them, runs the plan's
encounters against both older baselines, predicts the passage P1, and says where 1PN itself
stops being trustworthy. Predictions and outcomes, including the failed ones: `JOURNAL.md`
(entries 0-10). Labels: [VERIFIED] (a registered run or a source read at its locator),
[JUDGEMENT], [BACKGROUND], [TO VERIFY].

Decision 0010: ordinary differential equations for point masses are a reference solution; no
outside code, nothing for `athenak/src/`.

## Contents

| Path | What |
|---|---|
| `eih.py` | the equations (`accel`), the 1PN integrals (`energy`, `momentum`, `canonical_momenta`, `angular_momentum`, `centre_of_mass`), `velocities_from_momenta`, the test-mass 1PN invariants of 2404 (`testmass_E_L`, `testmass_state`), a vectorised DOP853 with per-trajectory stop, the drivers with newton3's interface (`evolve_states`, `scatter`, `run_encounter`; option `reading='velocity'/'canonical'`), the far release (`parabola_pair_1pn`, `far_states`) and the 1PN-consistent start state (`state_at_r0_1pn`) |
| `tests/test_eih.py` | T0 (Newtonian limit; 2404's restricted form; integrals' identities), T1 (local consistency of the integrals with the equations), T2 (two-body periastron advance and period), T3 (conservation scaling in a Hills encounter) |
| `scripts/trust.py` | T4: test-mass parabolic orbits, EIH against exact Schwarzschild: where 1PN stops being trustworthy |
| `scripts/scan.py`, `scan_figs.py` | phase scans of the plan's lines (q = 10: r_p = 7-17 M; q = 4: 9.82-16 M; prograde and retrograde; 360 phases) with Newton, HRNA and EIH (two readings of the start velocities) from the same coordinate start state at 4 r_t; analysis and figures |
| `scripts/scan_far.py` | the same lines with EIH released at 40 r_t on its 1PN parabola (J of the GR parabola), Newton from 40 r_t, HRNA with 2404's data at 4 r_t |
| `scripts/p1.py` | predictions for the passages from the start states of `nr_first/inputs/p1_q4.athinput` (P1, q = 4) and `three_punctures/inputs/hills_q10_m8.athinput` (q = 10): Newton, HRNA, EIH (velocity reading, canonical reading, horizon-mass variant) |
| `scripts/p1_state.py` | 1PN-consistent start states for the two inputs (positions and canonical momenta as `<problem>` blocks) and the predictions from them |
| `figures/`, `results/` | copies of the inspected figures and the JSON summaries of the runs named below |

Run outputs: `scratch/F-hills/<run id>/`; manifests: `tracks/F-hills/runs/<run id>/`.

## Equations (read at the locators; JOURNAL entry 0)

Acceleration of body a (G = c = 1; `c2inv` multiplies the 1PN terms), x_ab = x_a - x_b,
n_ab = x_ab/r_ab:

    a_a = - sum_b m_b x_ab/r_ab^3
          + sum_b (m_b x_ab/r_ab^3) [ 4 m_b/r_ab + 5 m_a/r_ab
                + sum_{c != a,b} ( m_c/r_bc + 4 m_c/r_ac - (1/2)(m_c/r_bc^3)(x_ab.x_bc) )
                - v_a^2 + 4 v_a.v_b - 2 v_b^2 + (3/2)(v_b.n_ab)^2 ]
          - (7/2) sum_b (m_b/r_ab) sum_{c != a,b} m_c x_bc/r_bc^3
          + sum_b (m_b/r_ab^3) [x_ab.(4 v_a - 3 v_b)] (v_a - v_b)

Source: Will, arXiv:1312.1289v3, `PN-NbodyDraft.tex` l. 338-355 (Eq. eq:EIH). The same
equation: 2404.16270 `appendix.tex` l. 117-124 (Eq. eab.1, the c = a terms absorbed into
-5 m_a/r_ab) and 2604.27429 `template.tex` l. 100-120; the three agree term by term [VERIFIED:
reading], and EIH evaluated at M at rest at the origin equals 2404's restricted equation
(`appendix.tex` l. 127-131) to 4e-15 (T0b). Conserved 1PN energy and momentum: Will l. 357-380
(Eqs. energy2, momentum). Derived here and tested (T0c, T1): canonical momenta p_a, J = sum
x_a x p_a, centre of mass G (the general form of Will's truncated l. 545-547). Test-mass 1PN
energy and angular momentum: 2404 `appendix.tex` l. 182-188. Periastron advance and radial
period at 1PN: 1805.07240v5 `LRRSJarXiv_v5.tex` l. 3169-3184.

## Tests (all registered; JOURNAL entries 2, 4, 7)

| Test | Result | Run |
|---|---|---|
| T0a Newtonian limit (c2inv = 0) vs newton3 | 1.5e-16 | F-20261119-144536-fc9bf86 |
| T0b EIH at M at rest vs 2404's restricted equation, m/M = 1e-9 ... 0.1 | PN part equal to 4e-15 | same |
| T0c sum of canonical momenta = Will's P; T0d momentum inversion | 2e-16; 1.5e-16 | same |
| T1 d/dt of Will's E, P, of J and G - P t along EIH, ratio c2inv 1e-2 / 1e-3 | 99.98, 99.995, 99.997, 100.01 (second order); Newtonian ones 10.000 | same |
| T2 periastron advance vs 3/j^2 (nu = 0.25, q = 10, test mass; p = 80-640 M) | deviation slope -1.89 to -1.91 in j, coefficient 4.4-5.5/j^2; period slope -1.98 to -1.99 in p | same, `figures/fig_t2_periastron.png` |
| T3 conservation in the q = 10 encounter scaled by lambda = 8 ... 128 | slopes -2.10 (E), -1.74 (P), -1.92 (J), -1.81 (c.o.m.), Newtonian -1.05/-1.06; same outcome | same, `figures/fig_t3_conservation.png` |
| T4 test-mass parabolas, EIH vs exact Schwarzschild | below | F-20261119-143753-d82e9e3, `figures/fig_t4_trust.png` |

The first designs of T2 and T3 failed (run F-20261119-143636-aae25fb: the angle was unwrapped
only at the periastra; the scaling range lambda = 1-4 is not perturbative). Both are on record
in JOURNAL entry 4.

## Where the first post-Newtonian order stops being trustworthy (T4; JOURNAL entry 4)

Parabolic test-mass orbits of equal angular momentum L, EIH against exact Schwarzschild, error
of the relativistic part of the swept angle (Delta phi - Delta phi_Newton) and of its L
derivative (the differential deflection of two members, which drives the tidal separation)
[VERIFIED, run F-20261119-143753-d82e9e3]:

| areal r_p (M) | 4.2 | 6 | 8 | 10 | 12 | 16 | 20 | 30 | 40 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|
| error of the excess | -88 % | -61 % | -39 % | -27 % | -20 % | -12 % | -9 % | -5 % | -3.5 % | -1.2 % |
| error of its L derivative | -100 % | -102 % | -83 % | -61 % | -46 % | -29 % | -20 % | -11 % | -7.6 % | -2.5 % |

- Below 10 / 20 / 30 / 50 percent beyond areal r_p = 20 / 12 / 10 / 7 M (excess) and 40 / 25 /
  16 / 12 M (derivative). 1PN underestimates the relativistic deflection everywhere.
- EIH has no capture: every parabolic orbit turns around, at harmonic r = 2.7-5.35 M for
  L = 0.5-4 M, where GR captures every L < 4 M. Below about 7 M EIH's excess even decreases
  with decreasing r_p.
- The 1PN truncation ambiguity (EIH against a quadrature of the conserved 1PN E and L, equal
  at 1PN) is 7-16 percent of the excess at 10-40 M, as large as the error against GR.
- In the three-body runs the pair force between the members carries 1PN factors of the heavy
  hole's potential and the binary's motion, about 5 M/r + V^2 ~ 0.2-0.3 at 4 r_t and larger
  near pericentre, so the expansion parameter of the binary's internal dynamics is about
  5 M/r, not M/r [JUDGEMENT from the equations; consistent with the scans].

[JUDGEMENT] For the Hills problem: EIH is a controlled correction to Newton (relativistic part
off by less than about 20 percent) for pericentres beyond about 25 M (areal); between about 12
and 25 M it gives the sign and rough size of the relativistic correction; inside about 12 M -
every pericentre of the plan's lines (7-17 M at q = 10, 9.8-16 M at q = 4) - it is not a
controlled approximation either; below about 7 M, and for any member with L < 4 M, it is
qualitatively wrong (no capture).

## Scans of the plan's lines (JOURNAL entries 6-8)

From the same coordinate start state at 4 r_t (run F-20261119-144537-4db7530, analysis
F-20261119-144830-1aaea9d, `figures/fig_scan_lines.png`, `fig_scan_phase.png`,
`results/scan_summary.json`) [VERIFIED as outputs]:
- The start state dominates. Read as EIH coordinate velocities, the Newtonian-circular binary
  at 4 r_t comes apart by itself (q = 10, r_p = 17 M retrograde: 360 of 360 phases "both
  free", the members never closer than their initial 3.0 M; Newton keeps all 360 bound). Read
  as canonical momenta (the Bowen-York reading) it shrinks instead and survives. The EIH
  counterpart of SC3's Gamma effect for HRNA.
- No two models agree phase by phase (EIH-Newton 0.01-0.16 at q = 10 prograde; EIH-HRNA
  0.01-0.37; Newton-HRNA 0.01-0.39).
- An EIH member comes inside 5.35 M (the GR-capture proxy: EIH's turning radius of the L = 4 M
  parabola) in 0.77 / 0.64 of the phases at r_p = 7 / 8 M (q = 10 prograde), in 1.00 / 0.91
  with the canonical reading; and a member comes inside the trust radius 12 M in 0.81-1.00 of
  the phases at every r_p <= 13 M.
- EIH's own 2PN-level error, the change of the 1PN energy along the encounter: median
  0.16-0.48 energy units (unit (m1 m2/a) q^(1/3) = 1.80e-3 M at q = 10, 4.96e-3 M at q = 4),
  against mean ejection energies of 0.4-0.8 units.

Far release (EIH on its 1PN parabola from 40 r_t; run F-20261119-145315-2d18c52): see JOURNAL
entry 10 and the section "State" below.

## P1 (JOURNAL entries 6, 7, 9)

From the input start states (run F-20261119-144642-1ca3da1, `figures/fig_p1_q4.png`,
`fig_p1_q10.png`, `results/p1.json`) [VERIFIED as model outputs]:

| | Newton | HRNA (hole fixed) | EIH, v = P/m | EIH, P canonical | EIH, P canonical, horizon masses |
|---|---|---|---|---|---|
| q = 4 (`p1_q4`) | m1 ejected +1.31 u, m2 bound (5.78 M) | m2 ejected +0.97 u, m1 bound (7.26 M, later 5.08) | m1 to 3.66 M (GR would capture), m2 recedes slowly (+0.11 u) | no ejection by t = 1500 (binary re-bound) | m2 ejected +0.21 u, m1 bound |
| q = 10 (`hills_q10_m8`) | m1 ejected +1.61 u, m2 bound (5.64 M) | m1 plunges (t = 97), m2 ejected +1.16 u | m2 ejected +0.71 u, m1 to 3.10 M | binary not separated by t = 1500, m1 to 4.63 M | m2 ejected +1.51 u, m1 bound to 5.32 M |

(u = the energy unit above.) Read in 1PN, the start states are not parabolic: the centre of
mass is unbound with the velocity reading (E/mu = +0.0071 at q = 4, +0.0086 at q = 10) and
bound with the canonical reading (-0.0029, -0.0037).
[JUDGEMENT] q = 10: robust across HRNA and all three EIH variants, against Newton: m1 enters the
region where GR captures (inside 5.35 M), m2 does not. q = 4: no robust 1PN prediction; the
outcome changes with the reading of the momenta (13 percent in the velocities) and with 2
percent in the masses.

## How to rerun (from `/data/haiyangw/nrpic/wt/F-hills`)

    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/F-hills/eih --cores 1 \
        --purpose "..." -- python tracks/F-hills/eih/tests/test_eih.py                       # 2 min
    ... --cores 1 -- python tracks/F-hills/eih/scripts/trust.py                              # 1 min
    ... --cores 13 -- /data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python \
        tracks/F-hills/eih/scripts/scan.py --workers 13                                      # 3 min
    ... --cores 1 -- python tracks/F-hills/eih/scripts/scan_figs.py scratch/F-hills/<scan run>
    ... --cores 13 -- /data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python \
        tracks/F-hills/eih/scripts/scan_far.py --workers 13
    ... --cores 1 -- /data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python tracks/F-hills/eih/scripts/p1.py
    ... --cores 1 -- /data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python tracks/F-hills/eih/scripts/p1_state.py

`python` is the worktree's `.venv` (numpy, scipy, matplotlib); scripts that call HRNA need numba
(`scratch/F-hills/venv-gb`). Outputs go to `$NRPIC_RUN_DIR`. Driver use:

```python
import sys; sys.path.insert(0, "tracks/F-hills/eih")
import eih
from hills3.threebody import HillsSetup          # newton3's setup (eih puts newton3 on the path)
s = HillsSetup(M=1, m1=0.05, m2=0.05, a=3, rp=8, phase=2.27)
res = eih.scatter([s], k0=4, k_end=30, reading="canonical")   # newton3-style result dict
one = eih.run_encounter(law="eih", m1=0.05, m2=0.05, a=3, rp=8, phase=2.27, sense=1)
```

## State

Deliverables done and tested: the equations with sources, tests T0-T4 (7 of 7 checks pass after
the redesign; T4 complete), the scans from the common start state, the P1 predictions from the
input states, the trust statement. Being finished in this session: the far-release line
(entry 10) and the 1PN-consistent start states (entry 9); their outcomes are in JOURNAL.

Not done: inclined (non-coplanar) encounters; a 2PN reference (the 1PN truncation ambiguity
is measured only for test masses, T4); an EIH reading of the horizon masses beyond the one
variant; HRNA from 40 r_t (not converged in release radius at q = 10, SC6).

## Requests

1. To the F-hills lead (for P1 and every later passage): the NR start states built from
   Newtonian momenta at 4 r_t are, read in 1PN, either a loosened or a tightened binary on a
   hyperbolic or bound centre-of-mass orbit, depending on how the Bowen-York momenta are read;
   at q = 4 this changes the predicted outcome of P1. Either build the inputs from a
   1PN-consistent state (`scripts/p1_state.py` writes `<problem>` blocks: release at 40 r_t,
   EIH inward, canonical momenta; positions harmonic = isotropic at 1PN [BACKGROUND]) or state
   P1's purpose as a test of the given data, not of "r_p = 9.82 M". The q = 10 statement
   "m1 enters the GR capture region, m2 does not" is the robust reference prediction.
2. To core (through the lead; interface `multi_puncture`, section 9 item 4 "post-Newtonian
   momenta" open): confirm [TO VERIFY] that the Bowen-York momentum parameter of a puncture
   equals the canonical 1PN momentum of the EIH Lagrangian to 1PN order (ADM momentum), and
   that the puncture coordinates are harmonic to 1PN; this package's `velocities_from_momenta`
   and `canonical_momenta` then give the matching velocities and momenta. Also: the member
   masses of the EIH reference should be the horizon masses at t = 0 (variant `eih_p_m` of
   `p1.py`); the readers of the NR runs should report them.
3. To the geodesic_binary helper (same owner): HRNA's start-state convention matters as much as
   its dynamics (SC3); the EIH far-release line is the cross-check.
