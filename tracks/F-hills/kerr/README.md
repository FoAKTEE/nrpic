# kerr: F-pre-2 for Kerr (arXiv:2402.02178) and HRNA's spurious self-acceleration (R3)

Helper package of track F-hills (wave 3, round 1). It asks whether the relativistic baseline
F-pre-2 (HRNA: exact black-hole acceleration of each member plus Newtonian self-gravity,
`../geodesic_binary/hrna.py`, the model of arXiv:2404.16270) follows the Kerr results of
arXiv:2402.02178, and it measures HRNA's spurious self-acceleration of a moving binary (R3, open
from the second check of G0). Predictions and outcomes, failed ones included, are in
`JOURNAL.md` (entries 0-5). Every number below carries a run id; the runs are registered under
`tracks/F-hills/runs/<run_id>/`, their outputs are in `scratch/F-hills/<run_id>/`.

HRNA stays a semi-analytic reference outside `athenak/src` (decision 0010). Nothing of
`hrna.py` is copied or changed: the extensions import it.

## Contents

| file | what |
|---|---|
| `hrna_incl.py` | inclined set-ups: E = 1 Kerr orbit from (r_p, L_z) with Carter Q from Eq. (rp) of 2402 (`main.tex:357-362`), L_z range Eq. (Lz) (`main.tex:368-372`), CM released at BL r0 in the equatorial plane (`main.tex:495-502`); circular binary of any orientation (iota, node Omega, phase); final binary elements; flat-space moving binary (R3); `run_incl` driver |
| `hrna_bks.py` | coordinate chart 'bks' = Boyer-Lindquist time with Cartesian Kerr-Schild space (`t' = t_KS - F(r)`, `F' = 2Mr/Delta`); equal to hrna's Schwarzschild form 'sch' at a = 0; hrna's `accel_one`, `rhs`, `integrate`, `energy_lz` recompiled from their own code objects with this metric added |
| `tests/t5_rotation.py` | T5: inclined set-up = rotated coplanar one (a = 0); regression against `hrna.initial_state`; Kerr +-0.9 mirror |
| `tests/t6_kerr_single.py` | T6: single body on inclined Kerr orbits (a = 0.9) against `python/nrpic` (positions, E, L_z, Q, pericentre) |
| `tests/t7_spin_limit.py` | T7: a -> 0 limit in 'bks'; 'cks' vs 'sch' outcomes over 64 orientations |
| `tests/t8_bks_chart.py` | T8: the 'bks' chart (identities, equality with 'sch', single body vs python/nrpic) and the binary-energy pump of 'cks' against its leading-order prediction |
| `scripts/r3_selfacc.py` | R3: reproduction of F-20261115-175620-df20ffe, scan in V, a0/m_b, q, psi, phase; CM pericentre shift of 2404 encounters; effect on separation fractions; `--figure` mode |
| `scripts/scan_2402.py` | reproduction scan: Fig. InclD families and Fig. afin cells with 24 / 8 orientations per cell |
| `scripts/analysis_2402.py` | digitizes the paper's figures (data only), compares, writes `kerr_2402_summary.json` and the figures |
| `scripts/spin_trend.py` | survival against spin at r_p = 10 |
| `scripts/digitize_2402.py`, `scripts/paper_2402.py` | vector-content reader and calibration of Figs. InclD and afin (the PDFs are parsed as text, never executed or rendered) |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `results/` | copies of the runs' JSON outputs (named below); the paper's numbers read off its figures (`paper_2402_digitized.json`) are NOT in git (decision 0023 item 4, CLAUDE.md rule 9): copy at `/data/haiyangw/nrpic/scratch/F-hills/kerr_2402/paper_2402_digitized.json` (sha256 51ea5694...fdfd7d), and in the output directory of the analysis run F-20261121-132817-eacfe46 |
| `figures/` | copies of the inspected figures (named below) |

## Model extension and conventions

Units G = c = M = 1. The CM starts at BL radius r0 = 100 M in the equatorial plane moving inwards,
on the E = 1 orbit with pericentre r_p and L_z, Q = Q(r_p, L_z) from Eq. (rp), sign of u_theta +1
(the paper does not give it). Binary frame at release: e_a = unit CM position, L_hat = unit
(x_cm x v_cm), e_b = L_hat x e_a; binary basis [e_a e_b L_hat] Rz(Omega) Rx(iota); member 1
(m1 = 15/25 m_b) at +(m2/m_b) a0 (cos phase, sin phase, 0) in that basis. iota is the angle of the
binary's angular momentum to L_hat; 2402 measures it from the rotation axis of the local inertial
frame (`main.tex:516-518`), which coincides with L_hat for equatorial orbits [JUDGEMENT: to O(a/r0)
for inclined ones]. The binary is circular in the CM's proper time (internal angular velocity
divided by the CM's dt/dtau; hrna's `ic_gamma`). Outcome when the CM is back at r = 100 M
(`main.tex:610-611`): survived = no member captured and E_b < 0 with the relative velocity
multiplied by the CM's dt/dtau.

Charts. 'sch' (hrna, Schwarzschild only), 'cks' (hrna, Cartesian Kerr-Schild) and 'bks' (this
package). Use 'sch' or 'bks' only: in 'cks' the slices are tilted by dt = (2Mr/Delta) dr, HRNA
evaluates the pair force at equal coordinate time, and a moving binary is pumped (prograde) or
drained (retrograde) at first order in M/r, d ln|E_b|/dt = -2 H omega_b (n x V).L_hat_b, with a
runaway at 2402's binary frequency (JOURNAL entries 2 and 4, T8). In 'bks' only the frame-dragging
part of g^{0i} remains (a few 1e-3 in ln|E_b| over the infall at a = 0.9, T8).

## Tests (all passed; numbers in JOURNAL entry 4)

| test | result | run | figure |
|---|---|---|---|
| T5 rotation | inclined = rotated coplanar, positions 1e-10 to 2.5e-9 r_g at matched times (rounding control 4e-11 to 1.3e-9); regression 5e-14 a0; Kerr mirror 1.1e-9 | F-20261121-131507-d9da8f1 | `figures/t5_rotation.png` |
| T6 single body, Kerr a = 0.9 | positions within 3.8e-8 r_g of python/nrpic (r_p = 6 whirl), E 1e-12, Q 6e-11, pericentre 1e-11, Q = Eq. (rp) | F-20261121-131516-34d8c26 | `figures/t6_kerr_single.png` |
| T7 a -> 0 ('bks') | orientation difference proportional to a (slopes 0.9998-1.0000); E_b and e within 1e-3 of a = 0 for a <= 1e-3; 'cks' vs 'sch' at a = 0: 17-23 of 64 outcomes differ (the defect) | F-20261121-132010-a654642 (first run -131522-058291d) | `figures/t7_spin_limit.png` |
| T8 chart 'bks' | g g^-1 = 1 to 2e-15, derivatives 8e-11, = 'sch' at a = 0 to 1e-15; encounters equal to 'sch' (8.8e-11 to 4.2e-10 r_g); single body at a = 0.9 within 3e-9 r_g; 'cks' pump 0.0398 vs predicted 0.0412 at r = 50 | F-20261121-132028-86ae5d0 (first run -131539-417caed) | `figures/t8_bks_chart.png` |

## R3: spurious self-acceleration (JOURNAL entry 4)

| item | result | run |
|---|---|---|
| reproduction | -1.06473294303476e-4, equal to F-20261115-175620-df20ffe; that number is a short-window fit without a linear term | F-20261121-131555-91aa063 |
| nature | the force is perpendicular to V: V turns at constant size, the CM moves on a circle of radius V^2/a_s (about 730 r_g for SC0d's binary) | same |
| law, q = 1 | a_s = (m1 m2/m_b)(omega0/a0) V cos(psi) ((1-e)/(1+e))^(3/2), e = 1/(1 - V^2 - w0^2/4) - 1: within 0.8 percent for V <= 0.4 and a0/m_b = 30-1000, 2.3 percent at V = 0.5, a0/m_b = 30; zero for V perpendicular to the binary plane | same |
| unequal masses | a second artefact: e grows secularly, at 2402's ratio 2/3 and a0/m_b = 20000 by 1.25e-3 (V = 0.14) to 3.8e-3 (V = 0.45) per period | same |
| encounters | CM pericentre of 2404's binary, HRNA minus Newton: within 18 percent of the R3 shift at r0 = 70 r_t (beta = 1, 3, both senses); at 50 and 20 r_t the phase scatter is as large as the signal | same; figure F-20261121-132235-7df540a, `figures/r3_selfacc.png` |
| effect on s.f. | <= 3.2e-3 (2404, beta = 10, 70 r_t), <= 1.1e-3 at beta <= 5; wrong sign and 17 times too small to cause C2 (0.6975 -> 0.68); 2402: Delta r_p/r_p = 1.1e-3 to 3.2e-3; F's binary (m1 = m2 = 0.05, a0 = 3): Delta L/L = 0.02-0.04 from 4 r_t, 0.8-0.95 from 20 r_t | same, `results/r3_selfacc.json` |

## Reproduction of 2402.02178 (JOURNAL entries 0, 3, 5)

Statements chosen (entry 0): K1, the survival boundary iota_c(beta) of Fig. InclD
(`main.tex:582-605`); K2, its text that L_z < 0 binaries at beta > 0.9 are more stable than the
Newtonian criterion Eq. (cosiN) (`main.tex:586-593`); K3, Fig. afin at r_p = 10 (survivors mostly
at iota >~ pi/2, L_z minor; `main.tex:524-562`). The paper's node and binary phase are not given,
so every cell is run for several orientations. Scan F-20261121-132131-326dfd1 (41904 encounters),
analysis F-20261121-132817-eacfe46 (`results/kerr_2402_summary.json`, figures `fig_incld.png`,
`fig_incld_sf.png`, `fig_afin.png`, `fig_afin_sf.png`), spin trend F-20261121-132821-5610cdb
(`figures/spin_trend.png`). Steps are the paper's grid, pi/6.

| statement | paper | HRNA | verdict |
|---|---|---|---|
| K1, s = 0 | shaded boundary | within one step of the HRNA median at 15/15 r_p; paper inside the orientation range 15/15 | reproduced |
| K1, s = 0.9, L_z < 0 | markers | 15/15 within one step; 14/15 inside range | reproduced |
| K1, s = 0.9, L_z = 0 | markers | 15/15 within one step; 15/15 inside range | reproduced |
| K1, s = 0.9, L_z > 0 | 2-4 steps at beta = 0.52-0.68 | 0-1 step there (11/15 within one step overall) | not reproduced at beta = 0.52-0.68; HRNA's spin trend (survival at iota = pi/6 from 0.08 at a = -0.9 to 0.67 at 0.9) follows the weaker tide of prograde Kerr orbits [JUDGEMENT] |
| K2 | figure: L_z < 0 at beta = 0.97, 1.13 at pi (above Eq. cosiN 0.60-0.62 pi); text: "more stable" | 5 pi/6, above the criterion | figure reproduced within one step; text refuted |
| K3 | survival 0.563; prograde half 0.13, retrograde 0.995; no survivor below 0.41 pi | 0.718; prograde 0.48 (0.23-0.63 per orientation), retrograde 0.953; a_fin of retrograde survivors median 0.995 vs 1.012 | retrograde half and a_fin reproduced; empty prograde half not reproduced (also not by the Newton law of the same set-up: 0.17-0.33) |
| Newton law vs Eq. (cosiN) (control) | - | within one step at 12/15 r_p; more stable at beta = 0.48-0.57 | criterion approximate there |

Text of the T2 row for G1 (Kerr part) [JUDGEMENT]: "F-pre-2 (HRNA) follows 2402.02178 in part.
Run in a static slicing (chart 'sch', and 'bks' added for Kerr), it reproduces Fig. InclD within
the paper's pi/6 grid for s = 0 (15/15 pericentres), s = 0.9 L_z < 0 and L_z = 0 (15/15), and the
figure of the K2 claim (L_z < 0 binaries at beta > 0.9 less stable than the Newtonian criterion;
the paper's text says the opposite and is refuted); the retrograde half of Fig. afin (survival
0.95 vs 0.995, a_fin median 0.995 vs 1.012). It does not reproduce the L_z > 0 boundary at
beta = 0.52-0.68 (HRNA 2-3 grid steps more stable, consistent with the weaker tide of prograde
Kerr orbits) nor the empty prograde half of Fig. afin (0.48 vs 0.13, orientation-dependent; the
paper's node and phase are not given). In the Kerr-Schild slicing of hrna.py ('cks') HRNA pumps
moving binaries at first order in M/r and must not be used for binaries with M omega_b of 2402's
size. HRNA's own artefacts at 2402's parameters (R3: Delta r_p/r_p <= 3e-3; unequal-mass
eccentricity pump ~1e-3 per period) are small for the outcome. Runs F-20261121-132131-326dfd1,
-132817-eacfe46, -132821-5610cdb; tests -131507-d9da8f1, -131516-34d8c26, -132010-a654642,
-132028-86ae5d0; R3 -131555-91aa063. Figures `kerr/figures/fig_incld.png`, `fig_afin_sf.png`,
`t8_bks_chart.png`."

What F-pre-2 can claim: a relativistic baseline that agrees with 2402's Schwarzschild and
L_z <= 0 Kerr boundaries within one grid step; for prograde Kerr orbits at beta ~ 0.5-0.7 and for
the fraction of prograde survivors it disagrees with the paper, and which is right needs a
Fermi-frame tidal reference (open).

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/F-hills
PY=/data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python   # numba is not in the worktree .venv
K=tracks/F-hills/kerr
R="harness/bin/nrpic-run submit --kind scouting --gate G1 --package $K"
$R --cores 1 --purpose "T5" -- env OMP_NUM_THREADS=1 $PY -I $K/tests/t5_rotation.py '$NRPIC_RUN_DIR'   # likewise t6, t7, t8
$R --cores 4 --purpose "R3" -- env OMP_NUM_THREADS=1 $PY -I $K/scripts/r3_selfacc.py '$NRPIC_RUN_DIR' --workers 4
$R --cores 5 --purpose "scan" -- env OMP_NUM_THREADS=1 $PY -I $K/scripts/scan_2402.py '$NRPIC_RUN_DIR' --workers 5
$R --cores 1 --input <scan_2402.json> --purpose "analysis" -- env OMP_NUM_THREADS=1 $PY -I $K/scripts/analysis_2402.py <scan_2402.json> '$NRPIC_RUN_DIR'
$R --cores 4 --purpose "spin trend" -- env OMP_NUM_THREADS=1 $PY -I $K/scripts/spin_trend.py '$NRPIC_RUN_DIR' --workers 4
```

Costs: tests under a minute each; R3 5 min on 4 cores; scan 2 min on 5 cores; analysis 30 s.

## Not done / open

- Which of HRNA and the paper is right for prograde Kerr orbits at beta ~ 0.5-0.7 and for the
  prograde half of Fig. afin: needs the paper's own model (Fermi-frame geodesic deviation) as an
  independent reference; not built here.
- The factor 1 + 3K/(2 r_p^2) used to read the spin trend is quoted without a locator [TO VERIFY].
- K4-K6 of entry 0 (eccentricities, lifetimes, chi_eff) not attempted.
- geodesic_binary S4 (Kerr a = +-0.9 in 'cks' with 2404's binary) was not rerun in 'bks'; the pump
  is about 58 times weaker there (K ~ 6e-3), probably below its 0.04-0.05 effect [JUDGEMENT].
- R3 at r0 = 20 and 50 r_t is below the phase scatter of four phases; more phases would sharpen it.

## Requests

1. To the lead: put numba into the track's requirements (`tracks/F-hills/env/requirements.txt`);
   the worktree `.venv` has none, and every run here used `scratch/F-hills/venv-gb`.
2. To the lead, for geodesic_binary: note in its README that 'cks' must not be used for binaries
   with M omega_b >~ 1e-2 (slicing pump, JOURNAL entry 2), and consider rerunning S4 in 'bks'.
3. To core, through the lead (affects geodesic_binary request 1, the HRNA pair force in the
   `nrpic_geodesic` pusher): AthenaK's pusher works in Cartesian Kerr-Schild coordinates, whose
   slicing produces this pump if the pair force is taken at equal coordinate time. Specify the
   pair force at equal proper time in the CM frame (or in a static slicing), and add to its
   acceptance tests T8 (d): the odd part in iota of ln|E_b| of 2402's binary from r = 100 to 50 M
   must stay below 1e-2 (HRNA in 'cks' gives 0.04, in 'bks' 0.005).
4. To the lead (future package): a Fermi-frame tidal reference (2402's model without PN terms) to
   settle the L_z > 0 and Fig. afin differences; HRNA cannot settle them alone.
