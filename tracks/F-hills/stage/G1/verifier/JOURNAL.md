# JOURNAL of stage/G1/verifier (fresh verifier of G1 of F-hills, checklist C18)

Helper package, batch 22 (2026-11-25, processors only, 0 card-hours). Task: recompute the G1
material named in `../OPEN.md` item 2 with readers of my own, everything but the tail of the
passage (A2 beyond its last record).

## Entry 0 (2026-11-25 09:42 PST, commit 57c7a67dc): what I read before the predictions

Read: CLAUDE.md, CHARTER (to "Owners" and sheet 9.9), decisions 0016 item 4, 0041 items 4-6,
0042; `../OPEN.md` (the lead's list of material); `../../G0/SCOPING.md` section 5 (the G1
criteria (i)-(iv)) and section 6; brief lines 466-492; the deck
`binary_conv/inputs/p1b_R16n.athinput`; manifests of A (F-20261121-203144-b2cf16b), A2
(F-20261124-210400-902c650), C (F-20261121-203247-961801d), R8, R12, R16n, B, P1; the result
JSON of the lead's analyses F-20261125-170453-1175d44 (b21_a2_state.json: spans, S1-S6 values)
and F-20261125-170646-6dd4ae4 (b11_passage.json: Newton and A numbers); the lead's prediction
paragraphs JOURNAL.md lines 828-849 (A2-1..A2-5, batch 11) and 1025-1058 (S1-S6, H1-H4, batch 21);
`outputs/history.cpp` lines 172-260 (what H-norm2 is). By accident my read of the owner's journal
ran on to lines 1060-1075, the first outcome lines of batch 21 (S1-S3 MET, with the numbers that
are also in b21_a2_state.json). I have not read REVIEW-wave3.md, CHECKLIST.md, VERIFY_RESULTS,
EVIDENCE, STAGE_REPORT or the rest of the outcome entries.

The claims I test, with where they are stated:
- C1 Newton from the deck state (bare masses, v = p/m): pair closest approach 3.67 M at 87.6 M,
  m1 (comp0) to M 12.07 M at 95.75 M, m2 to M 5.78 M at 122.1 M, m1 ejected, m2 bound
  (b11_passage.json "newton"); centre of mass closest to M 9.81 M at 104.35 M (JOURNAL l. 832).
- C2 Trackers A + A2 join to 0-96.23 M without a gap; overlaps agree to 1.1e-12 M (S1, S2).
- C3 Pair closest approach 2.110 M at 76.37 M; A2-1 (2.0-2.7 M at 63-75 M) refuted on timing.
- C4 At 96.23 M the pair's centre of mass is 13.06 M from M and closing; members 12.05 and
  14.16 M from M; both bound to M and to each other (b11_passage.json "A").
- C5 Horizons of A2 (made without the diagnostics): no failed search by signature; member medians
  0.12944, 0.12940, heavy 1.00385; member drift 3.1e-5 and -8.1e-6 per M (65-95 M); heavy-hole
  change 6.9e-4 (S6).
- C6 Constraint norm: rms H = sqrt(H-norm2 / Volume) below 1e-4, max 3.13e-5 on A2 (S6).
- C7 Waveforms of A2: 137 samples per sphere, 62-96 M, from 160 raw rows (S3); A's 0-61.8 M.
- C8 Mesh members (binary_conv README table): separation of the binary alone at 7.5 M: m/8
  4.8863, m/16 4.9477, P1 (three holes, m/8) 4.8539; at 20 M: P1 4.2855, alone m/8 4.3753;
  "R12 = R16n alone within 0.002 M" (C's manifest); C vs A within 0.0023 M to 22 M (JOURNAL l. 849).
- C9 P1's merger (H3, scope section 6): tracker separation below 0.1 M at 48.79 M, finder 0 first
  above 0.2 at 48.81 M (0.2686), finder 1 at 49.06 M (0.2693); remnant passes M at 7.0 M at 155 M.

### Predictions (written before any of my readers ran on the data)

- P0 Reader tests on analytic cases. (a) Tracker join: a Kepler orbit written as a tracker file
  split into five segments with overlapping restarts (later segment wins from its first time)
  is joined back exactly (max |dx| = 0), the gap check reports the step, and an injected 1e-6
  offset in an overlap is reported as 1e-6. (b) Closest approach with parabolic refinement on an
  eccentric Kepler orbit sampled at 2^-9: pericentre distance to 1e-8 relative and time to 1e-5.
  (c) My Newton integrator (DOP853, rtol 1e-12): a Kepler ellipse returns after one period to
  1e-9 and energy is kept to 1e-11 relative; a three-body run keeps energy and angular momentum to
  1e-9 over 200 M. (d) Horizon reader: on a synthetic summary with restart repeats, two exact
  repeats of the previous row at a new time and one NaN row, it counts 3 failures and keeps the
  last row per time. (e) Waveform reader: synthetic file with duplicated times gives the unique
  grid. Refuted: any of these misses its bound (then the reader is fixed before use).
- P1 (C1) My Newton integration reproduces the lead's Newton numbers to at least three digits
  (same model, independent code): r12 min 3.67 at 87.6 M, comp0-M min 12.07, comp1-M 5.78 at
  122 M, centre of mass 9.81 M at 104.3 M, comp0 ejected and comp1 bound to M at 200 M.
  Refuted: a difference in the second digit, or the fates swapped.
- P2 (C2) My join of A's 31 kept copies + live file and A2's 12 copies + live file covers
  0-96.2285 M with every step equal to 2^-9 M (no gap); positions at common cycles in overlaps
  agree below 1e-10 M; A's failed attempts after 61.80 M agree with A2's first segment below
  1e-10 M (same restart file 23, same build). Refuted: a gap above two steps, or an overlap
  difference above 1e-5 M.
- P3 (C3) s_min = 2.110 +- 0.001 M at t = 76.37 +- 0.02 M; no other local minimum after 61.8 M;
  s > 1 M throughout. So A2-1 fails on timing as written (window 63-75 M). Refuted: a minimum
  inside 63-75 M or below 2.0 M.
- P4 (C4) Centre of mass (horizon-mass weighted; masses equal to 4e-4, so the midpoint) at
  96.23 M: 13.06 +- 0.01 M from M's tracker and d/dt < 0. Coordinate Newtonian energies from the
  tracker positions and velocities: pair energy negative; each member's energy relative to M
  negative or of either sign? I predict both negative at 96 M, as the claim says [weak: the
  coordinate velocities include gauge drift]. Refuted: a positive pair energy.
- P5 (C5) A2 finders: 0 failures by signature in each of the three finders; medians reproduce to
  5 digits; member slopes over 65-95 M below 1e-4 per M in absolute mass (and in fraction);
  heavy-hole max - min below 1e-3. Refuted: any failure found, or a slope above 1e-4 per M.
- P6 (C6) sqrt(H-norm2/Volume) on A2 max 3.1e-5 (reproduced to 2 digits); H-norm2 itself does
  not grow by more than a factor 2 between 62 and 96 M. Comment to check: this volume-weighted
  rms over the 512^3 box is diluted by the vacuum far zone; I will also give H-norm2 itself.
  Refuted: rms above 1e-4.
- P7 (C7) A2: 137 unique times on the 0.25-M grid 62-96, none missing, at each of the four radii,
  from 160 raw rows; A: 248 samples 0-61.75 M (none missing). Refuted: a missing sample.
- P8 (C8) My readers give the binary-alone separations at 7.5 M and 20 M to 4 digits as tabled;
  R12 - R16n within 0.002 M up to the end of R12; C - A within 0.0025 M up to 22 M. With three
  resolutions the order of convergence from (s8 - s12)/(s12 - s16) at 7.5 M is between 2 and 5
  [JUDGEMENT: fourth-order finite differences, but the members' interior is not in the convergent
  regime]. Refuted: a table entry not reproduced to 3 digits.
- P9 (C9) P1: my tracker separation first below 0.1 M at 48.79 +- 0.01 M; finder 0's first mass
  above 0.2 at 48.81 M with 0.2686, finder 1 at 49.06 M with 0.2693; the remnant's closest
  approach to M about 7.0 M at about 155 M. Refuted: a difference above 0.05 M in a time or in
  the third digit of a mass.
</content>
</invoke>

## Entry 1 (2026-11-25 09:54 PST, commit 8afb440c8): predictions for criterion (iii), written before vjunk.py ran

Claims (from `junk_gauge/README.md` lines 9-31 and 69-91, the T3 evidence text): (K1) at m/8 the
t = 0 Hamiltonian norm is 4.7e-5 (card smoke 4.713e-5); truncation converges at order 7.6-8; the
corrected data's own residual 4.9e-7 is 1/33 of the uncorrected data (runs F-20261115-173547-a02af7d,
-181434-b9c8916, card F-20261115-174602-c6879fe). (J1) The three-hole data's junk at P1's spheres
r = 40, 48, 70, 90 M in the retarded-time window [-35, 6] M (record cut at u = 14, FFI omega_0 =
0.2): 2.8, 2.6, 2.5, 2.5 e-6 M, l <= 8, 67-70 percent in l >= 4 (runs F-20261121-075600-4480a13,
-075803-8e1955b). Scope criterion (iii): two radii agree within 20 percent.

Seen before writing (no hiding it): the first history row of each E2 case (H-norm2 and Volume at
t = 0, printed by a listing); so K1 is arithmetic on numbers I have looked at, not a blind test.
Definitions I take: rms H = sqrt(H-norm2 / Volume) (history.cpp lines 226-231: H-norm2 is the
proper-volume integral of H^2 outside the excised punctures); L9, L10, L11 = m/4, m/8, m/16.

- K1 prediction: rms H(approx, L10) = 4.71e-5 to 3 digits; order between L9 and L10 7.6-8.0 for
  both corrections; none/approx at L11 between 25 and 40 (claim 33). Refuted: rms H at L10 off in
  the second digit, or the ratio outside 25-40.
- J0 (analytic test of my energy pipeline, before use): a (2,2) wave h = A exp(-(t-t0)^2/s^2)
  exp(-i w t) with w = 0.5, sampled every 0.25 M as psi4 = d2h/dt2, FFI with omega_0 = 0.2: radiated
  energy (1/16 pi) int |dh/dt|^2 dt reproduced within 1 percent. Refuted: more than 1 percent off.
- J1 prediction: my FFI (omega_0 = 0.2 for every mode, FFT over the record cut at u = 14 with the
  mean of the record removed, no taper), u = t - r* with r* = r + 2 M_adm ln(r / (2 M_adm) - 1),
  M_adm = 1.25, energy over u in [-35, 6]: each radius 1.5-3.9e-6 M and within 20 percent of the
  others; l >= 4 share 0.6-0.75. Refuted: a radius outside 1.5-3.9e-6 or two radii more than 20
  percent apart [JUDGEMENT: FFI edge effects and the choice of r* move the number at the tens of
  percent level; the band is the lead's own spread over integration choices].

## Entry 2 (2026-11-25 09:57 PST, commit 05e52ce51): outcomes

Reference run: F-20261125-175533-141e4f1 (run_all.sh; supersedes the passes F-20261125-175038-4719d4a,
-175132-e7c6c68, -175235-e0fdde6, whose numbers for the same quantities are identical; they differ
only in what was added). A2's chain resumed at 09:49 PST (Slurm 5294) while I worked, so the
passage is read twice: cut at 96.2285 M (the owner's last record; `results/cut_96.23/`) and to
the live record (96.89 M in the reference run). Development runs into scratch/F-hills/tmp/verifier/
preceded each registered pass; no number below comes from them.

- P0 reader tests: (a) join, (b) minima, (d) horizon failures, (e) waveform times PASS. (c) FAILED
  AS WRITTEN on one bound: the Kepler energy is kept to 3.2e-11, not 1e-11; the return after one
  period (4.9e-11) and the three-body energy (1.05e-10) and angular momentum (3.4e-12) over 200 M
  meet theirs. Harmless for every use here (the Newton numbers are quoted to 5 digits).
- P1 Newton: pair minimum 3.67475 M at 87.598 M; comp0-M 12.0683 M at 95.761 M; comp1-M 5.77712 M
  at 122.090 M; comp0 ejected (v_inf 0.365 relative to M), comp1 bound; energies at 200 M 1.49387,
  -1.62560 (pair 0.87396) units, equal to the lead's to 10 digits. MET, except the centre of mass:
  the three-body Newtonian centre of mass passes M at 9.762 M (104.337 M), not 9.81 M; 9.809 M is
  the two-body conic pericentre of the centre of mass from the initial state (my 9.8087). The claim
  "Newton 9.81 M at 104.35 M" mixes the two; the time is the three-body one. P1 FAILED AS WRITTEN for
  that one number.
- P2 MET: 45 tracker files per tracker (31 of A, 13 of A2 at the cut, the 14th since 09:49), joined
  0-96.2285 M with every step exactly 2^-9 M (49270 times); overlaps A-A 1.13e-12, A-A2 4.8e-14,
  A2-A2 6.2e-14 M; the new segment from 96.23 M joins without a gap.
- P3 MET: s_min 2.10963 M at 76.3727 M (refined; sampled 2.109625 at 76.373); the only minimum
  after 61.8 M; s > 1 M throughout. A2-1 fails on timing only (its 2.0-2.7 M band holds).
- P4 MET: at 96.2285 M the centre of mass is 13.0626 M from M (claim 13.0628; my weights are A2's
  median horizon masses), closing at -0.237 per M; members 12.0530 and 14.1600 M from M (equal to
  the claim to all digits); pair energy -0.823, member-M energies -0.362, -0.161 units (claim
  -0.823, -0.363, -0.162; my masses differ in the fourth digit); the pair stays bound after 61.8 M
  (maximum -0.807 units). At the live record (96.89 M) the centre of mass is 12.904 M from M and
  still closing.
- P5 MET with a finding: no failed search in any of A2's three finders (1102 times at the cut);
  medians reproduced to all digits; member drifts 3.09e-5 and -8.05e-6 per M in fraction of the
  mass (4.0e-6 and -1.0e-6 per M in absolute mass: the "per M" of the claim is fractional); heavy
  max - min 6.887e-4. Finding (fig_v_horizons, looked at): the heavy hole's mass falls smoothly
  from 1.00401 (63 M) to 1.00358 (86 M), -1.72e-5 per M, then the finder alternates between an upper
  branch (median 1.00422) and a lower one that keeps falling (1.00379 to 1.00354, -1.25e-5 per M).
  The fitted -2.7e-6 per M over 65-95 M mixes the branches. If the lower branch keeps its slope, the
  heavy hole's change exceeds 1e-3 before 150 M, against A2-5 [JUDGEMENT: an extrapolation].
- P6 MET: max sqrt(H-norm2/Volume) on A2 3.126e-5 at 84.5 M; H-norm2 0.0795 at 62 M, 0.102 at 96 M
  (factor 1.28), range 0.056-0.134.
- P7: A2 MET (137 samples 62-96 M on the 0.25 grid, none missing, from 160 raw rows at the time of
  the first pass). A FAILED AS WRITTEN: A's files hold 257 samples 0-64 M (A's cut attempts after
  61.80 M wrote 62-64 M), not 248 to 61.75 M; those nine samples equal A2's to 1.4e-12 (largest value
  1.9e-4). Joined A + A2: 385 samples 0-96 M, none missing.
- P8 MET for the table, FAILED for the order: separations at 7.5 M R8 4.88625, R16n 4.94769, P1
  4.85393; at 20 M P1 4.28549, R8 4.37531; Newton (binary alone) 4.94300, 4.96926: all equal to the
  binary_conv table to its 4-5 digits. R12 - R16n: largest 2.12e-3 M at 0.71 M (the start), -3.4e-4
  at R12's end (21.06 M): "within 0.002 M" holds after the first M only. C - A: largest 2.33e-3 M at
  0.59 M (claim 0.0023). No order of convergence exists from the three binary-alone members: s12 - s16
  changes sign between 7.5 and 10 M (7.7e-6 then -4.4e-4) while s8 - s16 is -0.06 to -0.38; the
  three-member order is undefined at 5, 7.5, 10 and 20 M. The claim "order >= 3.3 (3.96 from Delta s)"
  was made from m/8 and m/16 alone before R12 existed; it is not reproducible as an order.
- P9 MET: P1's tracker separation first below 0.1 M at 48.793 M; finder 0 first above 0.2 at 48.8125 M
  (0.26857), finder 1 at 49.0625 M (0.26930); remnant closest to M 6.99168 M at 154.598 M. Not
  reproduced: p1_280.json's d_at_112 = 11.816 (my 11.895 at 112.0 M; all its other d_at rows equal
  mine to 10 digits). P1's rms H over 60-280 M 4.66e-5 to 8.79e-5 (claim 4.7e-5 to 8.8e-5: MET).
  Remnant mass change 60-280 M -0.43 percent (claim -0.42) with medians of all accepted rows (my
  medians are lower than p1_280.json's by about 9e-4 because it keeps only 'good' rows).
- Horizon scan (H1-H4 of the owner's batch 21): failures by signature P1 4, 5, 18 (finders 0, 1, 2),
  R8 2, 2, none in R12, R16n+B, A+A2, C. H1 MET. H2: m/8 members 1.12e-3, 1.65e-3 (P1 10-40 M) and
  0.92e-3, 1.43e-3 (R8 10-21 M), so the written band 1.0-1.7e-3 fails for R8's member 0 and
  0.9-1.7e-3 holds; m/16 members at most 3.1e-5 per M (R16n+B, A, A2); C's members -1.20e-4 and
  -1.69e-4 (15-22.3 M); slopes over all rows equal those over accepted rows to 3 digits. H3 MET.
  H4 FAILS AS WRITTEN for P1: its heavy finder reads 0.9961, 0.9915, 0.9844 at t <= 0.125 M (2.3
  percent below its median 1.0071), within 0.70 percent after 1 M; A, A2, C within 0.05 percent; no
  member finder above 0.5. All horizon numbers: made without the diagnostics.
- K1: rms H at t = 0: approx L10 (m/8) 4.7134e-5, the card smoke the same to the 6 digits of the
  history; order L9 -> L10 7.98 (approx), 7.91 (none); L10 -> L11 6.42 (approx), 1.62 (none: its own
  residual); none/approx at L11 29.6 (prediction 25-40 MET; the claim's 33 and "own residual 4.9e-7"
  are not reproduced as raw numbers: my raw approx L11 rms is 5.51e-7, which still holds truncation).
- J0 MET: the FFI energy of the analytic wave is exact to 3.5e-6.
- J1 MET: junk in u in [-35, 6] M: 2.73, 2.50, 2.28, 2.36 e-6 M at r = 40, 48, 70, 90 M (claim 2.8,
  2.6, 2.5, 2.5); largest over smallest 1.198 (within 20 percent, barely); l >= 4 share 0.69-0.71
  (claim 0.67-0.70); with u = t - r 1.7-2.4e-6, omega_0 = 0.1 3.3-4.2e-6, omega_0 = 0.3 1.7-2.1e-6
  (claim 1.5-3.9e-6 over omega_0 0.1-0.3). fig_v_junk (looked at): a pulse at u = -33 M and then a
  steady flux of 3-8e-8 per M that carries most of the window's energy, flat in l: what OPEN item 4
  calls an emission of unidentified source.

## Entry 3 (2026-11-25 09:59 PST, commit 32701e43c): note ledger rows that overlap my readers, predictions first

Read after sections 1-9 of VERIFIER.md: `note/tables/ledger.tex` rows 122, 126, 128, 168, 194,
200-208 (grep for the quantities my readers already compute). Predictions for the rows not yet
computed by my readers (vmesh.py extended; bracket of the three-member order widened to 0.05-40):
- L1 (row 194) three-member order of the binary-alone separation at 15 and 20 M: 12, 14.5. I predict
  11.98 (already seen) and 14-15 at 20 M; I keep my reading that such orders are not asymptotic.
- L2 (row 200) distance of the common horizon from the heavy hole at 48.81 M: 24.9 M (+-0.1).
- L3 (row 201) rate of the remnant's distance at 280 M: 0.158 per M (+-0.002).
- L4 (row 205) heavy hole at t = 4 M: 1.00419 (to 5 digits); so "+0.32 percent" is 1.00736/1.00419 - 1.
- L5 (row 207) rms H of P1 at t = 1, 112, 280 M: 3.2e-4, 6e-5, 4.7e-5 (2 digits).
- Row 126 (orders 7.98, 7.68; 7.96, 7.62) is not computable from the history alone: the note says the
  truncation error is measured against a closed form; my raw-norm orders (7.98, 6.42; 7.91, 1.62)
  are a different quantity. Not checkable here.

### Outcomes of entry 3 (run F-20261125-175931-32701e4, the final reference pass; its passage numbers
at the cut equal those of F-20261125-175533-141e4f1)

- L1 MET: three-member orders 11.98 (15 M), 14.46 (20 M), and 13.4 at 10 M; none at 5 and 7.5 M.
- L2 MET: 24.879 M. L3 MET: 0.159 per M (fit 275-280 M). L4 MET: 1.004190 at 4.0 M (an accepted
  search); 1.007359/1.004190 - 1 = +0.316 percent, so "+0.32 percent" is measured from 4 M.
- L5 MET: 3.17e-4 (1 M), 6.02e-5 (112 M), 4.66e-5 (280 M); largest over 112-280 M 8.79e-5.
- Row 126: not checkable from the history (closed-form truncation error); row 122 (0.0119, 4.71e-5,
  5.51e-7) MET to 3 digits; row 168 (conic 9.809, e 1.00023) MET (9.8087, 1.000235).
- Figures of the final pass looked at: fig_v_tests, fig_v_passage, fig_v_horizons (live and cut),
  fig_v_mesh, fig_v_junk (the development versions, identical in content, were read before; the
  final versions of fig_v_tests and cut_96.23/fig_v_horizons were read from the registered runs).

## Entry 4 (2026-11-25 10:02 PST): KHSR K3 with my own integrator, predictions first

Claim (khsr_note/results/khsr_ecc.json "direct", run F-20261121-212757-77cdc15, 512 phases; read
before writing this): prograde, M/m = 1e6, m1/m2 = 3, circular binary a = 1, r_t = a (M/m)^(1/3),
centre-of-mass orbit with r_p = D r_t and semi-major axis r_a (e = 1 - D r_t / r_a), start 10 r_t
inbound, end when the unperturbed conic is at 30 r_t outbound:
- D = 0.5: parabola P1 = P2 = 0.485, Pdis = 0.971; r_a = 100 r_t: P1 = 0.068, P2 = 0.484, Pdis
  = 0.973, both bound to M 0.420.
- D = 1.0: parabola P1 = P2 = 0.459, Pdis = 0.918; r_a = 100 r_t: P1 = 0.070, P2 = 0.457, Pdis =
  0.922, both bound 0.395. Ledger row 60: P1/P2 at r_a = 100 r_t 0.141 (D = 0.5), 0.154 (D = 1).
My check (vkhsr.py): my DOP853 integrator (vnewton.rhs, full three-body, rtol 1e-11), 256 phases
uniform in [0, 2 pi) at the start, stop when the members' centre of mass is at 30 r_t outbound;
classification by two-body energies at the end (pair energy > 0: disrupted; member-M energy > 0:
that member ejected).
- K3a prediction: each of P1, P2, Pdis, P(both bound) within 2.5 binomial sigma of my sample
  (sigma = sqrt(p(1-p)/256): 0.031 at 0.48, 0.016 at 0.07, 0.011-0.017 at 0.92-0.97) of the claim
  (raised from 128 to 256 phases after an 8-phase smoke test that only checked the code ran).
- K3b prediction: at r_a = 100 r_t the primary is ejected 4-15 times less often than the secondary
  (P1/P2 between 0.07 and 0.25), and P1 = P2 on the parabola within 1 sigma.
Refuted: any probability more than 3 sigma off, or P1/P2 outside 0.05-0.3.
