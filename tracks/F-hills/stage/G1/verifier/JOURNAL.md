# JOURNAL of stage/G1/verifier (fresh verifier of G1 of F-hills, checklist C18)

Helper package, batch 22 (2026-11-25, processors only, 0 card-hours). Task: recompute the G1
material named in `../OPEN.md` item 2 with readers of my own, everything but the tail of the
passage (A2 beyond its last record).

## Entry 0 (2026-11-25 09:45 PST): what I read before the predictions

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

## Entry 1 (2026-11-25 09:58 PST): predictions for criterion (iii), written before vjunk.py ran

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
