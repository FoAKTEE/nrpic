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
