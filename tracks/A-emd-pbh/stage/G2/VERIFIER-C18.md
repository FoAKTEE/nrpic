# Verifier report: item C18 of gate G2, Track A (conv_ball and threshold_ball numbers)

Fresh verifier, batch 18, 2026-11-25 (decision 0016 item 4; decision 0039 item 2(b)). Processors
only, no card time. Package: `stage/G2/verifier-c18/` (JOURNAL.md with every prediction before its
run and every outcome, README.md, scripts). Claims were taken from the result tables and bullet
lists of `conv_ball/README.md` and `threshold_ball/README.md`, the criteria from `scope/SCOPE.md`
(sections 3 and 7) and the predictions as committed before the runs (`conv_ball/JOURNAL.md` entry 3;
`threshold_ball/JOURNAL.md` entry 1, commit c48bd33b, and the statement of T4 in entry 11). The
lead's verdicts (outcome entries of both journals, `stage/REVIEW-wave3.md`, `stage/G2/CHECKLIST.md`)
were not read before sections 1-6 were written; section 7 compares.

Independence. My readers (`scripts/vread.py`) follow `docs/FORMATS.md` and
`coord/INTERFACES/{diagnostics,cosmo_amr}.md`; my exact reference (`scripts/vref.py`) is the LTB dust
solution built from the format-2 table alone (Misner-Sharp mass and energy per shell, cycloid);
nothing of conv_ball, threshold_ball, runs_ball, expball or python/nrpic is imported. The raw card
outputs read are those of the runs named in the two READMEs (`scripts/vmembers.py`).

## 1. Runs of this package

| run id | what | outcome |
|---|---|---|
| A-20261125-130535-b79555d | V0: readers and reference on analytic fields, exact events of the 11 tables | superseded by -131605 (same tests, fewer cases) |
| A-20261125-131605-f9e71ee | V0 final (after both reader fixes) | V0a-d, V0f pass; V0e: MOTS location 3e-3 off (mass within 6e-4) |
| A-20261125-130753-314837e, A-20261125-131436-e9ef7fb | V1: conv_ball recomputed (identical outputs; the second after the reader change) | section 3 |
| A-20261125-131148-99204e1, A-20261125-131458-396f809 | V2 first attempts: rule outcomes withdrawn (my reader defects, section 5a) | on record |
| A-20261125-131608-2269f36, A-20261125-131745-5388fde | V2: threshold_ball recomputed (the second adds the mass series figure) | section 4 |
| A-20261125-131935-bbac6fd | claim-by-claim tables (`tables.md`) | sections 3, 4 |
| A-20261125-131954-8c80a3f | mass medians over the windows named in threshold_ball entry 11 | section 4 |

Figures looked at: fig_v0a, fig_v0e (-130535); fig_vconv_orders, fig_vconv_mass (-130753);
fig_vthresh_searches, fig_vthresh_summary (-131608); fig_vthresh_masses (-131745).

## 2. The exact solution [VERIFIED]

My reference reproduces the packages' exact columns from the tables alone (V0f, run
A-20261125-131605-f9e71ee; after a closed-FLRW test to 2e-11, V0a): data set 3 core turnaround
3.371611 M, core-edge tau_AH 9.551093 M, m 0.686562 (quoted 3.3716, 9.5511, 0.686563); threshold
tables tau_AH(core edge) 15.386139, 23.404718, 35.159637, 40.053600, 43.656126, 46.415299,
54.979747, 114.574469 for delta_c = 1.0, 0.7, 0.5, 0.45, 0.42, 0.40, 0.35, 0.20 (threshold_ball
DESIGN section 1 to its last digit). The core turns around as one shell (tau_ta equal at rbar = 1, 2
and the edge to 1e-6) and the core edge is the first trapped shell in every table.

## 3. conv_ball (analysis A-20261121-120257-a2eb839), recomputed in A-20261125-131436-e9ef7fb

Definitions as written in conv_ball/DESIGN.md section 4. "v2" is the literal reading of ddet
(proper time and shell label of the tracked particles interpolated linearly in coordinate radius
to the finder's mean radius, exact tau_AH at that label); v1 and v3 are two other reasonable
interpolations, reported as a spread.

| claim | verifier | verdict |
|---|---|---|
| first detection t (10 members) | identical | reproduced to the printed digits |
| ddet A, B, C = 0.193, 0.068, 0.017 M | 0.1924, 0.0675, 0.0166 (v2); v1 0.156, 0.056, 0.017; v3 0.187, 0.093, 0.038 | reproduced (v2) to 6e-4 M; interpolation spread up to 0.036 M (A), 0.025 M (B), 0.022 M (C) |
| ddet orders 1.5, 2.0 | 1.51, 2.03 (v2); 1.48, 1.76 (v1); 1.01, 1.27 (v3) | reproduced with v2; the B->C order is not robust (1.3-2.0) |
| dtrap -0.093, -0.022, -0.0077 M, orders 2.1, 1.5 | -0.0925, -0.0224, -0.0077; 2.05, 1.53 | reproduced to the printed digits |
| mass median 7.4e-3, -2.1e-3, -2.1e-4 | 6.3e-3 [5.3e-3, 7.4e-3], -2.09e-3 [-2.7e-3, -1.6e-3], -2.25e-4 [-9.6e-4, +5.0e-4] | B, C reproduced; A 1.1e-3 lower (the claim is the upper end of my bracket); C's value is below the resolution of the exact mass (bracket width 1.5e-3), so an order B->C is not defined |
| N leg: at B the times do not depend on N, the mass does (-2.1e-3 vs -3.0e-4) | ddet 0.0675 vs 0.0705; mass -2.09e-3 vs -3.05e-4 | reproduced |
| fixed N = 4969736: mass 2-5e-4 on all meshes | 2.7e-4, -3.05e-4, -2.25e-4 (A-N64, B-N8, C) | reproduced |
| R leg: time errors vary by 0.09 M at A, 0.04 M at B; mass by under 1e-3 | ddet A, A-R1.25, A-R1.35 = 0.192, 0.100, 0.175 (spread 0.09); B 0.068, 0.065, 0.107 (0.04); mass at A 6.3e-3, 6.5e-3, 10.2e-3 (spread 3.9e-3) | times reproduced; "mass by under 1e-3" holds at B (spread 0.8e-3) but NOT at A (3.9e-3 in mine; the table's own A values 7.4e-3, 6.7e-3, 1.0e-2 spread 3.3e-3) |
| A-R1.35 ddet 0.164 | 0.1746 | differs by 0.011 M |
| L leg: A-L32 = A to 1e-7, B-L32 = B to 1e-11 | ddet differences 1.0e-7 and 1.2e-11; mass medians 1.2e-7 and 1.2e-8 | reproduced for the times; B-L32's mass median differs at 1e-8 |
| C below the source's OS level 1e-3 (main.tex:945) | |dm(C)| <= 9.6e-4 for any exact mass in my bracket | reproduced, at the edge of what the tracked set resolves |

Every member forms a horizon by the persistence rule of threshold_ball entry 1 (found in every
search from the first, no repeats in the summaries). The convergence in mesh spacing of the two
time errors is real (all three interpolations fall A > B > C); the stated orders depend on how one
interpolates across the core edge, where the finder sits and tau_AH has a kink (section 5b). The
mass "convergence" along A, B, C is mostly a particle-number effect (one particle per cell: N grows
8-fold per halving), as the README itself says; at fixed N the mass errors are flat at 2-3e-4.

## 4. threshold_ball (A-20261124-131120-5c974ce, A-20261125-115027-17b419e, A-20261125-115550-fe60ff1), recomputed in A-20261125-131608-2269f36 and A-20261125-131745-5388fde

| claim | verifier | verdict |
|---|---|---|
| BH by the entry-1 rule: B-d1.00 ... B-d0.35, C-R1.25, C-d0.42; not BH: B-d0.20, A-d0.42, A-d0.40 | same classification; A-d0.42 and A-d0.40 have 3 finds each, then the guard stop (47.875, 50.625; tlim 51, 54); B-d0.20 never found to 69.94, core band contracting (dR/dt = -0.035 at the end) | reproduced |
| persistent from 17.000, 25.250, 37.188, 42.250, 45.875, 48.625, 58.312, every search, 45.906 | 17.0, 25.25, 37.1875, 42.25, 45.875, 48.625, 58.3125, every search from 10.71875, 45.90625 | reproduced to the printed digits |
| exact tau_AH column | section 2 | reproduced to all printed digits |
| tau_det 15.513, 23.472, 35.131, 40.117, 43.686, 46.402, 54.929; A 43.442, 46.103; C-R1.25 9.603; C-d0.42 43.705 | 15.5129, 23.4721, 35.1309, 40.1166, 43.6863, 46.4022, 54.9293; 43.4377, 46.1027; 9.6031; 43.6892 | reproduced to the printed digits except A-d0.42 (0.004 M) and C-d0.42 (0.016 M) |
| ddet +0.126 ... -0.142 (B), -0.232, -0.331 (A), +0.040 (C-R1.25), -0.014 (C-d0.42) | v2 equal to 1e-3 M for B and C-R1.25; A -0.238, -0.331; C-d0.42 -0.0095 (v1 -0.062, v3 +0.030) | reproduced except C-d0.42, whose value depends on the interpolation by 0.09 M |
| dmmed -3.8e-4, -1.9e-3, -9.4e-3, +1.9e-3 (B-d1.00 ... B-d0.45) | -9.3e-4, -2.6e-3, -9.5e-3, +1.0e-3 | reproduced within 1e-3 |
| dmmed +2.8e-3, +3.2e-4, +2.4e-3 (B-d0.42, B-d0.40, B-d0.35) | -2.4e-3 [-5.4e-3, -0.05e-3], -6.7e-3 [-9.7e-3, -3.7e-3], -1.0e-3 [-8.0e-3, +0.4e-3] | NOT reproduced: claims outside my brackets |
| dmmed C-d0.42 +2.4e-2 (window 46.1-47.2, 50.9-51) | +1.0e-3 over all finds with an exact mass; -1.5e-3 over that window; +3.2e-2 if the exact mass is taken at the last trapped tracked particle (run -131954) | NOT reproduced with the interpolated exact mass; reproduced in size only with the coarser convention, i.e. the number measures the sampling of the tracked particles |
| dmmed A -3.8e-2, -4.6e-2 | -8.8e-3, -2.9e-2 (one value each: 3 finds) | not reproduced; three finds make a median meaningless |
| bracket at t_end = 45 on B: (0.40, 0.42], interpolation 0.4103 (B), 0.4103 exact, 0.4083 (A) | tau_det 43.686 < 45 < 46.402; 0.41033, 0.41026, 0.40828 | reproduced |
| mesh C: C-d0.42 is a BH with tau_det < 45 (upper end holds) | BH, tau_det 43.689 | reproduced |
| first-detection mass excess up to 4-7 per cent at threshold | C-d0.42: up to +7.8 per cent in the first 0.45 M (exact mass low while the trapped tracked shells lie inside the core edge); B members: none (largest +0.6 per cent, at delta_c <= 0.5 between -0.2 and -1.2 per cent) | reproduced for C-d0.42 only |
| finder vs line MOTS within 0.3-1.5 per cent | C-d0.42 -0.06 to -0.84 per cent (median -0.63), C-R1.25 -0.02; B members -0.9 to -4.8 per cent, and no line MOTS at the tab output of the first detection | reproduced on mesh C; on mesh B not checkable with my second-order line reader (5 cells across the horizon; V0e) |
| constraint ratio 0.3-3 on the line (T6 failed) | at the first detection 0.70-2.1 (B), 0.87 (C-d0.42), 3.0 (C-R1.25), 0.93-1.6 (A) with r^2 weight; 0.16-3.6 with line weight; 0.4-1.5 in the matter only | reproduced |
| T5 failed (ball-radius effect at M/64 0.024 > 0.02) | |0.0403 - 0.0166| = 0.024 M | reproduced |

## 5. Criteria as written and findings

(a) My own reader defects, on record. The finder's summary file repeats the values of the last
success after a failed search (coord/INTERFACES/cosmo_amr.md 2.3); my first reader counted those
repeats as finds and classified A-d0.42 and A-d0.40 as black holes (run A-20261125-131148-99204e1).
Then the summary prints time with %g (45.90625 -> 45.9062), and exact matching against the status
file dropped every C-d0.42 find (run A-20261125-131458-396f809). Both are fixed and tested (V0d v, vi);
the classifications above use the status files. Any reader of these outputs must do the same.

(b) Criterion C3 (SCOPE section 3: L2 norm of H outside the horizon below 0.1 of that of 16 pi E at
t_AH) FAILED as written for every top-hat member, on every mesh, in every weighting I tried. It is
also violated on the initial slice: at t = 0 the r^2-weighted ratio is 0.22 (A), 0.11-0.20 (B), 0.105
(C-d0.42), 0.12 (C-R1.25) (line weight 0.086-0.19); con_H carries the matter term (otherwise the
ratio would be about 1), so this is the residual of the top-hat data, falling only slowly with the
mesh (A 0.22, B 0.12, C 0.105 at delta_c = 0.42). [VERIFIED as measured; JUDGEMENT on the cause]

(c) T4, mesh-C half (entry 11: |ddet(C-d0.42)| <= 0.0075 M and |dmmed| <= 1.4e-3) FAILED as
written: |ddet| = 0.0095 (v2), 0.030 (v3), 0.062 (v1). The mass half cannot be judged: my C-d0.42
median (+1.0e-3) would pass and the claim (+2.4e-2) would fail, and the bracket of the exact mass
(-3.9e-3, +6.5e-3) is wider than the bound.

(d) T5 FAILED as written (0.024 M > 0.02 M).

(e) ddet near the core edge is interpolation-limited. At first detection the finder's radius lies
between the last tracked particle inside the core and the first outside (B: r 0.4185 and 0.4501
at t = 10.78, label 2.4957 against the break at 2.4937), where tau_AH(label) has a kink. Three
reasonable interpolations differ by 0.01-0.04 M at A and B and by up to 0.09 M at C-d0.42 —
comparable with the claimed errors at B and C. The claimed values are reproduced with the literal
definition, but their last digit (and the B -> C order 2.0) carries this uncertainty. dtrap (per
particle, no interpolation in radius) is free of it and converges at 2.05, 1.53.

(f) The exact horizon mass on the code's slice is sampled by the tracked particles. Between the
last trapped tracked shell and the next one outward the exact mass is uncertain by 0.1-0.3 per cent
at A and B and 0.15 per cent at C in conv_ball, and by up to 3.5 per cent in C-d0.42. Mass errors
below that width (conv_ball C's 2.2e-4; the threshold medians near delta_c = 0.4) are not measured
by this diagnostic. A denser tracked set near the core edge, or the line Misner-Sharp mass at the
exact label, would remove the limitation [JUDGEMENT].

(g) Time measure [JUDGEMENT]. SCOPE section 3 measures time by the proper time of comoving particles
in the unperturbed outer layers. On the code's slice those particles read 46.50 M at the first
detection of B-d0.42 (core edge 43.69, coordinate time 45.875): taken literally with the code's
slicing, B-d0.42 would fall after t_end = 45 and the bracket would move to (0.42, 0.45]. In the exact
solution's own synchronous slicing every shell shares one proper time, so the exact bracket is the
same (0.40, 0.42] under either reading; threshold_ball/DESIGN.md section 1 chose the invariant
core-edge proper time for this reason. The gate text should name that choice.

## 6. Not checked

The turnaround columns (turnaround C, eta) and the turnaround leg of conv_ball; the guard-stop
restarts G1-G3 and the K-series of threshold_ball (entries 5-10); costs; the common-window
measurement of A-20261125-115550-fe60ff1 beyond the window medians above; the line MOTS on mesh B
(section 4); anything requiring a card run.

## 7. Comparison with the lead's verdicts (written after sections 1-6)

(Section added after the lead's material was read; see below.)
