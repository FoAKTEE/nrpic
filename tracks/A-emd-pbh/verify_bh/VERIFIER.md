# VERIFIER: first horizon of the expanding ball (BH-1R) and no horizon at uniform M/8 (BH-1)

Independent verifier (decision 0009), helper of A-emd-pbh, wave 3, gate G2. Written
2026-11-21 from the artefacts only: data set 3 (A-20261119-143524-334e553, lattice
n = 136 of A-20261119-164113-74f0f32), BH-1R (A-20261119-164634-f1fe887/bh_smr) and BH-1
(A-20261119-144419-13d5601/bh_n128, bh_n192, bh_n256). Not read before sections 1-3 were
committed: runs_ball/JOURNAL.md entries 11 and later, runs_ball/README.md and figs/, the
analysis runs of 2026-11-20 on these card runs, any REVIEW or GATE_REVIEW file, the
owner's STATUS and HANDOFF, the orchestrator's reports. Own code only (scripts/, nothing
imported from runs_ball/, expball/, analysis/, criteria/, stage/G1/verifier/); predictions
first (JOURNAL.md entries 1 and 3, outcomes in entries 3 and 4).

Registered runs (local, processors, all completed; outputs under
`scratch/A-emd-pbh/<run id>/`):

| Run id | Script | What |
|---|---|---|
| A-20261121-125359-22858c4 | c1_exact.py | C1: LTB events from the format-2 table |
| A-20261121-125427-35117a2 | c2_initial.py | C2: initial slice of the four runs against the table |
| A-20261121-125512-6df0ee3 | c3_horizon.py bh_smr | C3: finder masses against the exact slice mass |
| A-20261121-125921-9c96b3f | c3b_firstdetect.py | C3 follow-up: area check, field mass at the finder radius |
| A-20261121-125449-689b5ec | c4_lines.py | C4: finder results, non-finite times, trapped line points |
| A-20261121-130002-56a4c88 | c4b_stencil.py | C4 follow-up: four readings of the line |
| A-20261121-125646-166ae06 | c5_shells.py | C5: shell errors, per-particle turnaround and trapping |
| A-20261121-125939-80054f8 | c5b_edge.py | C5 follow-up: errors against distance from the core edge |

## 1. Verdicts

| Claim | Verdict | Claimed | This verifier | Run |
|---|---|---|---|---|
| C1 core turnaround | CONFIRMED | 3.3716, R_max = 1.1623 R_i | 3.371611 (spread over core shells 1e-7), 1.162312 | 125359 |
| C1 first trapped sphere | CONFIRMED | core edge R_i = 2.65306, tau_AH 9.55109, m 0.686563, R_AH 1.37313 | inner side of break 1, R_i 2.653061, tau_AH 9.551092, m 0.6865625, R_AH 1.373125 | 125359 |
| C1 crunch | CONFIRMED | 10.6305 | 10.630490 | 125359 |
| C1 m_AH(tau_AH + 2, 4, 8) | CONFIRMED | 0.69610, 0.70437, 0.71804 | 0.696098, 0.704369, 0.718042 (constant-tau slices) | 125359 |
| C1 no shell crossing before the crunch | CONFIRMED | none | none on 2098 shells x 600 times to 0.999 tau_c; least neighbour gap 1.7e-4 M | 125359 |
| C2 initial slice reproduces the table | CONFIRMED | psi, K, particle masses | psi^4, gamma within 4.7e-13, K within 1.6e-12 of max K (all four runs, four-point Lagrange rule of the interface); m_p / (rho psi^6 h^3) = 1 within 5e-7 inside the pieces | 125427 |
| C2 total mass, rest mass | CONFIRMED | 1.00046, 1.14594 | 1.00046406 (last row); rest mass 1.1459385723 (table integral), particles 1.1459385718 on all four lattices; history sum_m at t = 0 equal to the file to 7e-16 | 125427 |
| C3 horizon found, first between t = 10.5 and 13 | CONFIRMED | 10.5-13 | t = 10.875; 41 of 56 searches (9.0-15.875) finite, continuous after the first | 125512 |
| C3 particles at the horizon 0 to 0.3 M past tau_AH | CONFIRMED within scatter | 0 to 0.3 | tau_p - tau_AH(R_i): -0.024 (bin medians at r_h), +0.024 mean of the 14 particles within 0.0625 of r_h, individual -0.10 to +0.13 | 125512 |
| C3 m_irr within 3e-3 of the exact slice mass at the first detection | WRONG | <= 3e-3 | +1.96e-2 (0.701055 against 0.687585); +1.25e-2 at 11.0, +3.7e-3 at 11.125, -3.1e-3, -5.9e-3, -4.2e-3 at 11.25-11.5; within 3e-3 from t = 11.625, within 6e-4 from 11.75 to 15.875 | 125512, 125921 |
| C3 median over the first 4 M within 3e-3 | CONFIRMED | <= 3e-3 | -4.6e-4 (33 finder times; +2.5e-4 with the quadratic location of the trapped shell); largest single |error| 1.96e-2 | 125512 |
| C3 comparison with the source paper | NOT CONFIRMED (different quantity) | "the source paper's level" | the paper reports final masses after excision at t = 60 M against M_ADM: <~1e-3 (main.tex:945), RMS over five seeds 2.061e-3, 9.362e-4, 7.347e-4 for A1-A3 (main.tex:1484). BH-1R ends at t = 16 and has no final mass against M = 1.00046; its forming-horizon error after 11.75 (<= 6e-4) is of that order [JUDGEMENT] | 125512 |
| C4 BH-1 M/8: finder reports nothing | CONFIRMED | nothing | 64 searches t = 8.0-15.875, all columns NaN | 125449 |
| C4 M/8: 2m/R > 1 with K_T > 0 on the x line from t = 11.0 at r = 0.45 M, then 0.21-0.33 M | CONFIRMED (reading-dependent) | 11.0 at 0.45 | 11.0 at r = 0.4463 (2m/R 1.006) with a fourth-order stencil; 11.25 at 0.4463 (second order), 11.25 at 0.386 (staggered), 11.75 at 0.3125 (line taken as the axis); afterwards 0.32, 0.21, 0.11 | 125449, 130002 |
| C4 M/8 turns non-finite near t = 15.5 | WRONG (by 0.25-0.47 M) | near 15.5 | nrpic.hst and cstat.hst first non-finite at 15.031; z4c.user.hst and the adm line at 15.25 | 125449 |
| C4 M/4, M/6 (no number claimed) | reported | - | no finite finder result in either; trapped line points from 12.0 (M/4, r 0.415; 11.75 at fourth order) and 11.5 (M/6, r 0.433; 11.25 at fourth order); non-finite from 14.375 (M/4) and 14.5 (M/6) | 125449, 130002 |
| C5 BH-1R core |R/R_exact - 1| < 1.5e-3 at tau = 3.37 | WRONG for all tracked core particles; holds 0.05 M inside the edge | < 1.5e-3 | max 2.77e-3 (R_i 2.6511, 0.002 M inside the edge), 99th percentile 1.75e-3, median 8e-7; 9.7e-4 without the particles within 0.05 M of the edge | 125646, 125939 |
| C5 BH-1 M/8 < 2e-3 at tau = 3.37 | WRONG; holds 0.2 M inside the edge | < 2e-3 | max 5.3e-3 (p99 3.7e-3); 4.1e-3 (d > 0.05), 2.5e-3 (d > 0.1), 1.45e-3 (d > 0.2) | 125646, 125939 |
| C5 BH-1 M/8 < 2e-2 at tau = 9.0 | WRONG; holds 0.2 M inside the edge | < 2e-2 | max 5.7e-2 (p99 3.8e-2, median -1.7e-3); 2.3e-2 (d > 0.05), 2.2e-2 (d > 0.1), 1.5e-2 (d > 0.2) | 125646, 125939 |

d is the distance R1 - R_i of a particle's shell label from the core edge R1 = 2.653061.
The C5 verdict depends on which particles "core-shell errors" means; read literally (all
tracked core particles) the bounds fail by factors 1.8 (BH-1R), 2.6 and 2.9 (M/8), and all
excess comes from the outermost 0.05-0.2 M of the core (fig_c5b_edge).

Additional findings, not claimed:
- First-detection excess (C3): the finder's area is that of the code's sphere (sqrt(A/4 pi)
  1.40211 against 1.40292 from the metric at the particles at r_h; within 5e-4 later), but the
  tracked particle nearest r_h at t = 10.875 (R_i 2.6684) is not yet trapped in the exact
  solution (2m/R_exact = 0.977). The line's Misner-Sharp mass at r_h is +1.0e-2 at 11.0 (the
  finder +1.2e-2), so the excess is at least partly in the fields, but the line's mass
  scatters by 1e-2 near the edge before 11.5, so field against finder is not decided
  [TO VERIFY] (fig_c3b_firstdetect).
- BH-1R line: trapped from t = 11.0 at r = 0.41 in all four readings (130002), consistent with
  the finder's first detection at 10.875 within one output.
- BH-1R deposit: the history's mesh integral int_E at t = 0 is 1.145039 against sum_m
  1.145939 (-7.9e-4); the three uniform runs agree to 1e-15 (125427) [cause TO VERIFY:
  deposit or integral across the two levels].
- Per-particle turnaround (proper time of the largest areal radius against the exact one):
  mean offset -1.2e-3 (BH-1R), -1.1e-2 (M/8), -1.1e-2 (M/6), +7.1e-2 (M/4); R_max -6e-5,
  -5.5e-4, -6.4e-4, +3.9e-3 (125646). Per-particle trapping time (R_p through 2m of its
  shell): BH-1R mean -2.1e-3, std 1.6e-2 over 248 particles near the edge.
- Records: `.trajmet.bin` holds 17 float64 per record (file size against the record count of
  `.traj.bin`, all four runs); docs/FORMATS.md now says 17 (its row records that it said 12
  until core-v0.5), as does diagnostics.md section 6.

## 2. Method and its uncertainties

- Exact solution: Lemaitre-Tolman-Bondi dust rebuilt from the format-2 table alone
  (ltb.py): psi = 1 + u, R = psi^2 rbar, v = -R K_T, 1 + 2E = (dR/drbar)^2 / psi^4,
  m = (R/2)(1 + v^2 - |DR|^2); each shell on its own cycloid from (R_i, m, E) with its own
  starting phase. Checks on the table: momentum constraint |K_L + dv/dR| < 5.5e-6, mass from
  the Hamiltonian constraint against the metric mass 7.2e-7, bang time common to 2.5e-8 and
  equal to the header t_i (125359).
- Readers (vbio.py) written from docs/FORMATS.md, coord/INTERFACES/diagnostics.md and
  spherical_id_format2.md. The table outputs are lines at y = z = dx/2 of the local level;
  the 1e-13 agreement of psi^4 at t = 0 depends on that offset and confirms it.
- Areal radius of a particle: r sqrt(B), B the tangential eigenvalue of gamma_ij at the
  particle (trajmet). Reading error at t = 0: 4e-6 (BH-1R), 1.7e-5 (M/8), 1.1e-4 (M/6),
  6.6e-5 (M/4).
- Exact slice mass (C3): every tracked particle's label R_i from its t = 0 position; a shell is
  trapped on the code slice when the particle's proper time tau_p >= tau_AH(R_i); the
  outermost trapped label from bin medians (linear and quadratic). Tracked (1320) against all
  1.3e6 particles of the snapshots: 1.2e-4, 6e-5, 6e-6 relative at t = 12, 14, 16. tau_AH(R_i)
  rises by about 18 M per M of R_i outside the edge, so proper-time errors of 0.1 M move the
  slice mass by 5e-4 only: the 1.96e-2 at the first detection is not a slice-mass error.
- Line Misner-Sharp mass (C4): 2m/R = 1 + (R K_T)^2 - |DR|^2 with |DR|^2 = (dR/dr)^2 / A on
  each half line. The first trapped time moves by up to 0.75 M between readings at M/8
  (130002); at M/16 (BH-1R) it does not move.
- Not done: the constraint histories (cstat.hst) are not analysed; no run of mine changes
  the card runs; the finder's settings are not examined.

## 3. What the G2 criterion still lacks (CHARTER.md line 110; general G2 row line 71)

The criterion: errors of the turnaround time and of the horizon-formation time relative to
the exact solution converge in particle number, mesh spacing and ball radius; the
horizon-mass error is of the same order as in the Oppenheimer-Snyder test of Wu and Most.
Judging from these artefacts [JUDGEMENT]:

1. Horizon-formation time: one run only. The uniform runs M/4-M/8 never give a finder result
   although trapped spheres exist on their lines from t = 11.0-12.0, and they turn non-finite
   at t = 14.4-15.3. A convergence statement needs at least three runs with the horizon
   region at M/12-M/24 or finer (refined like BH-1R) and a defined formation time (first
   detection is biased: +2e-2 in mass, 0.75 M transient here).
2. Particle number and mesh spacing move together in every run seen (one particle per cell:
   n = 34, 51, 68, 136 for M/4, M/6, M/8, M/16). A fixed-mesh particle sequence and a
   fixed-particle mesh sequence are missing, and there is one ball radius (data set 3) only.
3. Turnaround: per-particle offsets -1.1e-2, -1.1e-2, -1.2e-3 (M/6, M/8, M/16) and +7.1e-2
   (M/4); M/6 to M/8 does not decrease. The output cadence (0.125 M) and the edge particles
   limit this estimator; a converging sequence is not shown yet.
4. Horizon mass against the Wu-Most level: needs the final mass against M = 1.00046 at late
   time (the paper: t = 60 M after excision, main.tex:945, 1484), several seeds or lattices,
   and the same estimator. BH-1R stops at t = 16; its forming-horizon mass after t = 11.75 is
   within 6e-4 of the exact slice mass, the right order, in one run.
5. The core edge carries the largest errors (C5 bounds fail only there; the first horizon
   forms there). G2 tables should state the particle selection, or report the edge band
   separately.
6. Constraints ("constraints behave", line 71) were not checked by me.
