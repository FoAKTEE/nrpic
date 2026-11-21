# JOURNAL of the package verify_bh (independent verifier, helper of A-emd-pbh, wave 3 round 1)

Gate G2. Card cap 0 card-hours (processor only). Decision 0009: I check the claims of
BH-1R and BH-1 from the artefacts, with my own readers and my own exact solution, without
reading the producer's analysis of this round (runs_ball/JOURNAL.md entries 11 and later,
its README, its figures, its analysis runs of 2026-11-20) before VERIFIER.md sections 1-3
are committed.

## 2026-11-20, entry 1: what was read, method, predictions (written before any code of mine ran)

Read: CLAUDE.md; coord/CHARTER.md to "Owners" and 9.4 (Track A; G2: errors of the
turnaround and horizon-formation times converge in particle number, mesh spacing and ball
radius; horizon-mass error of the order of the Oppenheimer-Snyder test of Wu and Most);
decisions 0009, 0010, 0016, 0019; harness/RULES.md; docs/FORMATS.md;
coord/INTERFACES/diagnostics.md, spherical_id_format2.md;
athenak/src/particles/nrpic_io.cpp lines 799-937 (trajectory writer); runs_ball decks
bh.athinput and bh_smr.athinput, prep_bh.py; expball/README.md and DERIVATION.md
sections 1-6 (definitions and formulas); runs_ball/JOURNAL.md entry 7 from "Data set 3 and
prediction B" and entry 10 with its amendment; main.tex of arXiv:2611.12831 lines 925-950
and 1470-1490; manifests of A-20261119-143524-334e553, -164113-74f0f32, -164634-f1fe887,
-144419-13d5601; header lines of ball.horizon_summary_0.txt, of the table outputs in tab/,
of ball.nrpic.hst, ball.cstat.hst, ball.z4c.user.hst; the header of the format-2 table.
Only the first two data rows of the BH-1R horizon summary were seen (t = 9 and 9.125:
nan, i.e. not found), nothing else of the run data.

Facts read from code and files (not yet a computation of mine):
- `.trajmet.bin` records hold 17 float64, not 12 as docs/FORMATS.md line 122 says:
  nrpic_io.cpp lines 811-814 and 917-927 write time, tag, then NRM_NVAR + 5 values;
  NRM_NVAR = 10 (athenak/src/particles/particles.hpp line 40): alpha, beta^i (3),
  gamma_ij (6), then the particle's proper time pr(IPTAU), E, S_x, S_y, S_z.
  diagnostics.md section 6 agrees [VERIFIED from the source of the worktree; the
  executable of the runs is core_gauge b4430da, whose record length I check from the file
  size against the record count of `.traj.bin`].
- Snapshots `.part.NNNNN.bin` carry the proper time of every particle (diagnostics.md
  section 7); BH-1R snapshot size 94839584 = 32 + 72 x 1317216 is consistent with that.
- The table outputs are lines at y = z = 0.01, cell-centre values of the cells containing
  that plane (outputs/basetype_output.cpp line 795-798, `CellCenterIndex`): the line sits
  at y = z = dx/2 of the local level (M/16 inside the refined region of BH-1R, M/8 outside),
  not on the axis. My spherical decomposition uses n = (x, dx/2, dx/2)/r.
- Horizon summary columns: 1 iter, 2 time, 3 mass (Christodoulou), 4-6 S_i, 7 S, 8 area,
  9 hrms, 10 hmean, 11 meanradius, 12 minradius (header line, and diagnostics.md
  section 10).
- The source paper's horizon-mass numbers are FINAL masses after excision at t = 60 M
  against the ADM mass (main.tex:945 "<~ 10^-3"; main.tex:1484 RMS over five seeds
  2.061e-3, 9.362e-4, 7.347e-4 for A1-A3), not the mass of a forming horizon against the
  exact mass of its slice. C3's "compare with the source paper's level" therefore compares
  different quantities [JUDGEMENT]; I report both and say so.

Method (my own code in scripts/, nothing imported from runs_ball/, expball/, analysis/,
criteria/, stage/G1/verifier/):
- LTB from the table alone. psi = 1 + u, areal radius R = psi^2 rbar, v = -R KT (code sign,
  KT = -v/R), |DR|^2 = (dR/drbar)^2 / psi^4 = 1 + 2E, Misner-Sharp mass
  m = (R/2)(1 + v^2 - |DR|^2); density from the Hamiltonian constraint read off the table,
  16 pi rho = 16 pi E_dust, and also from dm/dR = 4 pi R^2 rho; rest mass
  int rho dV_proper. Each shell (R_i, m, E < 0) follows the cycloid R = A(1 - cos eta),
  t = T0(eta - sin eta), A = m/(-2E), T0 = m/(-2E)^(3/2), with its own starting eta_i from
  R(0) = R_i, dR/dtau(0) = v > 0 (no assumption of a common bang time; I check it instead).
  Turnaround eta = pi, trapping eta_AH in (pi, 2 pi) with cos eta_AH = 1 + 4E, crunch
  eta = 2 pi. Shells with E >= 0 by the parabolic/hyperbolic forms. dR/drbar one-sided
  at the two breaks.
- C3 slice mass: on a code slice t, every tracked particle has its proper time tau_p(t)
  (trajmet) and its label R_i (from its t = 0 position and the table); the shell is
  trapped on that slice when tau_p >= tau_AH(R_i); m_exact(slice) is the Misner-Sharp mass
  of the outermost trapped shell, located by interpolating tau_p - tau_AH against R_i over
  all tracked particles (bands and random sample), cross-checked with all particles of
  the snapshots (every 2 M).
- C5: per tracked particle the areal radius R = r sqrt(B), B the tangential eigenvalue of
  gamma_ij at the particle (trajmet), against the cycloid at the particle's own proper
  time; eps interpolated per particle to tau_p = 3.37 and 9.0.
- C4: from the adm table outputs, R(r), K^theta_theta on the line, |DR|^2 by differences
  of R against r divided by the radial eigenvalue; 2m/R = 1 + (R KT)^2 - |DR|^2; trapped
  where 2m/R > 1 and KT > 0.

Predictions (what I expect; what would make the claim WRONG):

- P1 (C1, exact events). My table-based LTB reproduces the claimed numbers to the
  accuracy of the table (rows 1.06e-3 apart, m from a derivative of psi): turnaround
  3.3716 +- 3e-4, R_max/R_i = 1.1623 +- 2e-4, first trapped sphere at the core edge
  R_i = 2.65306 +- 2e-3 with tau_AH = 9.5511 +- 2e-3, m = 0.68656 +- 2e-4,
  R_AH = 2m = 1.37313 +- 4e-4, crunch 10.6305 +- 2e-3; m_AH(tau_AH + 2, 4, 8) =
  0.69610, 0.70437, 0.71804 each +- 1e-3; bang time common to all shells to 1e-6; no shell
  crossing before the crunch. WRONG if a number differs by more than ten times these
  tolerances, if the first trapped sphere is not the core edge, or if shells cross before
  10.63.
- P2 (C2, initial slice). At t = 0, adm_psi4 of the line equals (1 + u)^4 of the table
  within 1e-6 relative and K_ij within 1e-6 of psi^4 [KT delta + (KL - KT) n n] (largest
  deviations in the cell next to a break); total mass from KT at the last row,
  M = R^3 KT^2 / 2 = 1.00046 within 1e-6; the sum of particle masses of the nrp files
  equals 1.14594 and equals the continuum rest mass of my integral within 1e-4; the
  history column sum_m at t = 0 equals the file sum to 1e-12; deposited E at t = 0 equals
  the table density within 2e-2 in the interior of the core and of the shell (one
  particle per cell; the jumps smeared over about two cells). WRONG if psi or K differ by
  more than 1e-4 away from the breaks, or the rest mass by more than 1e-3.
- P3 (C3, BH-1R horizon). The finder finds a horizon (my probability 0.7), first between
  t = 10.5 and 13 (0.6 given found). At first detection the particles at the horizon have
  tau_p - tau_AH(R_i) between 0 and 0.5 M (I give 0.6 to the claimed 0 to 0.3). The
  irreducible mass sqrt(A/16 pi) against m_exact(slice): at first detection between 1e-3
  and 1e-2; I give the claimed bound 3e-3 a probability of 0.5, at first detection and
  as median over the first 4 M. The Christodoulou mass equals the irreducible mass to
  1e-6 (S ~ 0 by symmetry). Against the source paper: their numbers are final masses
  (see above); a forming-horizon error of 3e-3 is "the same order" as 1e-3 only in the
  loose sense. WRONG if no horizon is found by t = 16, if the first detection lies
  outside 10.5-13, or if the mass error exceeds 3e-3 by more than a factor 1.5 in my
  measurement with an uncertainty of the slice mass below that difference.
- P4 (C4, BH-1). The bh_n256 summary holds no finite mass (probability 0.95). My
  Misner-Sharp scan of the adm lines finds the first trapped point (2m/R > 1, KT > 0) at
  t = 11.0 +- 0.25 at coordinate radius 0.45 +- 0.13 M (one cell), later at 0.2-0.35 M; the
  histories turn non-finite between t = 15 and 16. M/4 and M/6: no finite horizon mass;
  trapped points later or not at all (resolution). WRONG if the bh_n256 summary holds a
  finite mass, if no trapped point is on the lines, or if the first one is more than
  0.5 M off in time.
- P5 (C5, shells). If the core-shell error at the turnaround converges at second order
  from 1.4e-2 at M/2 (entry 9 of runs_ball, a claim I do not verify), M/8 gives about 1e-3
  and M/16 about 2e-4; at first order 3.5e-3 and 1.8e-3. I predict BH-1R largest core
  |eps| at tau = 3.37 below 1.5e-3 (probability 0.7); BH-1 at M/8 below 2e-3 at 3.37
  (0.65) and below 2e-2 at 9.0 (0.5). WRONG if my largest |eps| exceeds the claimed bound
  by more than 30 per cent (my reading of R from the metric at the particle has its own
  interpolation error, which I estimate from the t = 0 records, where eps must vanish).

## 2026-11-20 14:34 PST, entry 2: PAUSED (flag locks/PAUSE, five-hour window at 97 per cent) - where I stopped

Done: scripts/ (vbio.py readers, ltb.py LTB from the table, partdata.py tracked particles,
c1_exact.py, c2_initial.py, c3_horizon.py, c4_lines.py, c5_shells.py, figstyle.py copy),
committed. Each script was run once UNREGISTERED to debug it (outputs in
scratch/A-emd-pbh/tmp/verify_bh/dev/; figures fig_c1_exact, fig_c2_initial,
fig_c3_horizon_bh_smr looked at). Those numbers are NOT evidence; no outcome is recorded
yet. Not started: no registered run (nrpic-run submit) exists, no VERIFIER.md, no
README.md.

Restart here: (1) commit state is clean for scripts/; (2) register the five runs, each with
`harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/A-emd-pbh/verify_bh
--launcher local --cores 2 --purpose '...' -- bash -c 'OMP_NUM_THREADS=2 .venv/bin/python
tracks/A-emd-pbh/verify_bh/scripts/<c?>.py [bh_smr]'` (c3 takes the run name), then
`nrpic-run finish <id>`; (3) copy the figures into verify_bh/figs/, read them, write the
outcomes of P1-P5 here; (4) VERIFIER.md sections 1-3, commit, push; then section 4.
Points to settle in the registered runs (seen in the debug outputs, not yet established):
the first-detection horizon mass of BH-1R against the slice mass; the stencil dependence
of the first trapped line point of BH-1 M/8 (t = 11.0 or 11.25); the time the BH-1 M/8
histories turn non-finite; the C5 bounds at tau = 3.37 (BH-1R and M/8).

## 2026-11-21 05:00 PST, entry 3: restart; outcomes of the five registered runs; predictions of the follow-ups

Restart after the pause of entry 2: merged main, scripts unchanged since bccf7d36. Registered
runs (local, processors, all completed): C1 A-20261121-125359-22858c4, C2
A-20261121-125427-35117a2, C4 A-20261121-125449-689b5ec, C3 A-20261121-125512-6df0ee3,
C5 A-20261121-125646-166ae06. Figures looked at: fig_c1_exact, fig_c2_initial,
fig_c3_horizon_bh_smr, fig_c4_lines, fig_c5_shells (in each run directory).

Outcomes against the predictions of entry 1:
- P1 (C1) HELD. Turnaround 3.37161, R_max/R_i 1.162312, first trapped sphere at the core edge
  (inner side of break 1) R_i 2.653061 at tau_AH 9.551092, m 0.6865625, R_AH 1.373125, crunch
  10.630490; m_AH at tau_AH + 2, 4, 8 = 0.696098, 0.704369, 0.718042; bang time common to
  2.5e-8 (core) and 6e-10 (shell), equal to the header t_i 3.887269; no shell crossing up to
  0.999 of the crunch (smallest neighbour separation 1.7e-4 M on 2098 shells x 600 times).
  Momentum constraint |KL + dv/dR| < 5.5e-6 (KL up to 0.37), Hamiltonian mass against the
  metric mass 7.2e-7. [VERIFIED, C1 run]
- P2 (C2) HELD, better than predicted: psi^4 and gamma of the line at t = 0 equal the table
  (four-point Lagrange rule, line at y = z = dx/2) to 4.7e-13 relative; K to 1.6e-12 of
  max |K|; the 1e-13 agreement also confirms the line's offset. Total mass from the last row
  1.00046406; particle masses sum to 1.1459385718 on all four lattices (n = 34, 51, 68, 136),
  table rest mass 1.1459385723 (rel. -4.3e-10); interior ratio m_p / (rho psi^6 h^3) within
  5e-7 of 1; history sum_m at t = 0 equals the file sum to 7e-16. Deposited E at t = 0
  against the table density: within 2e-8 rho_c (BH-1R, M/8), 3.4e-5 (M/4) and 4.6e-4 (M/6,
  core) away from the jumps. Not predicted: int_E at t = 0 in BH-1R is 1.145039 against
  sum_m 1.145939 (7.9e-4 low), while the uniform runs agree to 1e-15 [cause TO VERIFY: the
  refined run's deposit or its integral over two levels].
- P3 (C3) PARTLY FAILED. Horizon found (41 of 56 searches finite, 9.0-15.875, continuous after
  the first, gap 0.125): first at t = 10.875, inside 10.5-13 (held). At the first detection the
  14 particles within 0.0625 of r_h have tau_p - tau_AH(R_i) = +0.024 mean (-0.10 to +0.13);
  bin medians interpolated to r_h give -0.024. The mass prediction failed: m_irr = 0.701055
  against m_exact(slice) = 0.687585 (outermost trapped label R_i* = 2.6642): +1.96e-2 at the
  first detection, +1.25e-2 at 11.0, +3.7e-3 at 11.125, then -3.1e-3, -5.9e-3, -4.2e-3,
  -1.3e-3 (11.25-11.625) and within 6e-4 from 11.75 to 15.875. Median over the first 4 M
  (33 finder times) -4.6e-4, largest |err| 1.96e-2. Slice-mass uncertainty: tracked particles
  against all 1.3e6 particles of the snapshots at t = 12, 14, 16: 1.2e-4, 6e-5, 6e-6 relative;
  quadratic against linear location of R_i*: up to 1e-3 near the first detection. The
  Christodoulou mass equals m_irr to 2e-12 (held).
- P4 (C4) mostly held. No finite mass in any BH-1 summary (M/4, M/6, M/8; searches 8-16). My
  first trapped line point at M/8 is at t = 11.25, r = 0.4463 (2m/R = 1.007), not 11.0 (at
  11.0 the largest 2m/R is 0.976); then r = 0.32, 0.21, 0.11. Non-finite: M/8 nrpic.hst and
  cstat.hst from t = 15.031, z4c.user.hst and the line from 15.25 (claimed "near 15.5").
  M/6: trapped from 11.5 (r 0.433), non-finite from 14.5; M/4: trapped from 12.0 (r 0.415),
  non-finite from 14.375. BH-1R line: trapped from 11.0 at r = 0.4086; no non-finite value.
- P5 (C5) FAILED as stated for the largest error. Core particles at tau = 3.3716: BH-1R
  max |eps| 2.77e-3 (99th percentile 1.75e-3, median 8e-7), the maximum at R_i = 2.6511, the
  particle next to the edge; M/8 max 5.3e-3 (p99 3.7e-3); at tau = 9.0 M/8 max 5.7e-2 (p99
  3.8e-2). Reading error at t = 0: 4e-6 (BH-1R), 1.7e-5 (M/8). Per-particle turnaround in
  BH-1R: dtau mean -1.2e-3 (std 6.9e-3), R_max mean -5.6e-5. Per-particle trapping (R_p
  through 2m of its shell) in BH-1R: mean -2.1e-3, std 1.6e-2 over 248 particles.

Predictions of the three follow-ups (scripts c3b_firstdetect.py, c4b_stencil.py,
c5b_edge.py, written now, nothing run yet):
- Q3 (finder or field at the first detection?). I expect the field: the code's Misner-Sharp
  mass m_code(r_h) on the x line at t = 11.0 within 3e-3 of the finder's 0.6966 (I give 0.6),
  i.e. the excess over the exact 0.688 is in the fields near the core edge (a transient of
  the jump at the edge as it passes through r_h), not a finder fault. Refuted if m_code(r_h)
  at 11.0 is within 3e-3 of the exact shell mass while m_irr is 1.2e-2 above it. The areal
  radius of the particles at r_h equals the finder's sqrt(A/4 pi) within 2e-3 at every finder
  time of the first 2 M (refuted if off by more than 5e-3).
- Q4 (stencil). At least one of the variants b, c, d puts the first trapped M/8 point at
  t = 11.0 (probability 0.5); none puts it before 11.0 or after 11.5. The first time differs
  between variants by at most one output (0.25).
- Q5 (edge). The largest core errors come from the particles within one cell of the edge:
  excluding R1 - R_i < 0.05 drops the BH-1R maximum at tau = 3.37 below 1.5e-3 and the M/8
  maximum below 2e-3 (probability 0.6); at tau = 9.0 M/8 below 2e-2 after excluding 0.1
  (0.5).

## 2026-11-21 05:02 PST, entry 4: outcomes of the follow-ups Q3-Q5

Runs: C3b A-20261121-125921-9c96b3f, C5b A-20261121-125939-80054f8, C4b
A-20261121-130002-56a4c88 (local, completed). Figures fig_c3b_firstdetect, fig_c5b_edge,
fig_c4b_stencil looked at.

- Q3 UNDECIDED (finder or field). Area: the finder's sqrt(A/4 pi) equals the areal radius of the
  metric at the tracked particles at r_h within 8e-4 at the first detection (1.40211 against
  1.40292 by bin medians, 1.40737 by a local quadratic) and within 5e-4 afterwards: the
  finder measures the area of the code's sphere correctly (held). Mass: the line's
  Misner-Sharp mass at r_h at t = 11.0 is 0.69546 (+1.0e-2 over the exact shell mass 0.68851
  at r_h), the finder 0.69660 (+1.2e-2): agreement within 1.1e-3 as predicted, but at 11.25
  the line gives +9.9e-3 where the finder gives -3.4e-3, and the line's mass near the edge
  scatters by 1e-2 to 9e-2 from point to point at t <= 11.25 (the horizon sits on the steep
  m(r) of the core edge, dm/dr ~ 1-2: an r error of 5e-3 is 1e-2 in m). The line cannot
  decide between field and finder before t = 11.5; from 12.0 on line, finder and exact agree
  within 2e-3. Particles at t = 10.875: the tracked particle nearest r_h (r 0.4420, R_i
  2.6684) has code R 1.4022, exact R(tau_p) 1.4088 and 2m/R_exact = 0.977: the exact solution
  has this shell not yet trapped, the code's finder puts a marginally trapped sphere through
  it. Particles at the edge (R_i 2.635-2.661, r 0.38-0.42) have code R above exact R(tau_p) by
  1 to 7 per cent, where R(tau) of the edge shells is steep (dR/dtau ~ -1 near the crunch of
  the core at 10.63): small proper-time errors give large R errors there.
- Q4 HELD. M/8 first trapped point: a (offsets, 2nd order) 11.25 at r 0.4463; b (axis) 11.75 at
  0.3125; c (4th order) 11.0 at 0.4463 (2m/R 1.0064); d (staggered) 11.25 at 0.3855. One
  variant gives the claimed 11.0; the spread is 0.75 M (one output more than predicted: b is
  three outputs late). BH-1R: all four variants 11.0. M/6: 11.25-14.0; M/4: 11.75-14.0.
- Q5 HALF HELD. BH-1R at tau = 3.37: excluding R1 - R_i < 0.05 the largest |eps| is 9.7e-4
  (< 1.5e-3, held); < 0.02 excluded 1.9e-3. M/8 at tau = 3.37: 4.1e-3 (d > 0.05), 2.5e-3
  (d > 0.1), 1.45e-3 (d > 0.2) (prediction failed for d > 0.05). M/8 at tau = 9.0: 2.3e-2
  (d > 0.05), 2.2e-2 (d > 0.1), 1.5e-2 (d > 0.2) (failed for d > 0.1). M/4 sits at 7e-3 in the
  whole core at tau = 3.37 (median +3.3e-3), a systematic offset, not an edge effect.

## 2026-11-21 05:05 PST, entry 5: comparison with the producer's analysis; package closed

After VERIFIER.md sections 1-3 were committed (c2fde301) I read runs_ball/JOURNAL.md entries
11 and 12 (analyses A-20261121-074923-d396d73, -080558-02c3188, -081153-b92c08c), nothing
else of that package. Every number I recomputed agrees with the producer's to the digits
given where the estimators coincide (first detection 10.875; mass error +1.96e-2 against
their +1.97e-2; 4 M median -4.59e-4 against -4.46e-4; C5 maxima 2.77e-3, 1.38e-2, 6.75e-3,
5.29e-3 identical; non-finite times identical; turnaround offsets identical). Differences,
each traced in VERIFIER.md section 4: (a) the clock at the horizon at the first detection,
theirs -0.046 M (REFUTED), mine -0.024 (bin medians) with a lenient CONFIRMED in section 1:
both negative, the producer's verdict is the stricter and better one; (b) field against
finder: they judge the transient to be in the slice (line mass at the line's own marginal
sphere), my line mass at the finder's radius agrees at 11.0 and 11.5 but not at 11.25, so I
keep it open; (c) the M/8 first trapped line point: their reading behaves like my
fourth-order variant (11.0, 11.25, 11.75 for M/8, M/6, M/4). New and not in their
entries: int_E at t = 0 of BH-1R 7.9e-4 below sum_m. README.md written with the requests.
Figures copied to figs/ (all eight looked at). No card time used.
