# Journal of the fresh verifier of gate G2, Track C (checklist item C18)

Helper package `tracks/C-sidm/stage/G2/verifier/`, batch 33 (2026-11-27). Processors only, at
most three cores while the lead's `nrpic-stage verify C-sidm G2 --full` runs (started 00:53 PST,
pid 3893805, log `scratch/C-sidm/tmp/verify_full_g2.log`; left alone).

What was read before any recomputation: CLAUDE.md, CHARTER.md (to "Owners" and section 9.6),
decision 0010, stage/G2/RERUN.md, the list "What the verifier should recompute first" of
stage/G2/OPEN.md, Table VI of the note (`tab:ledgerG2`, note/main.tex:311-334), the scope text
(scope/SCOPE.md:124-140 and 323-330), the King ansatz and Table 1 of arXiv:2009.08163
(kb-data/raw/arxiv/2009.08163/v1/src/paper.tex:631-686, 920-960), the prediction entries of
the lead's JOURNAL as committed before the runs (git show 12183c5d5, b7007c99a, 77a69997a,
f261c3ec4, a5b72829a), the history headers of the runs, and coord/INTERFACES/collisions.md
(equation 1, history columns). NOT read: the outcome entries of the lead's journals,
stage/REVIEW-wave3.md, the verdict column of stage/G2/CHECKLIST.md, STAGE_REPORT.md,
VERIFY_RESULTS.*, EVIDENCE.md, the lead's analysis scripts (nseries.py, d2_analysis.py,
blockA_delta.py) beyond the run-id lists in their manifests' commands.

## 2026-11-27T09:05Z  predictions before any recomputation

V1 Equilibrium sequence (own solver of the King ansatz f = (exp(1 - E/E0) - 1)_+ of
arXiv:2009.08163 eq. Ansatz_King, isotropic, Schwarzschild coordinates; binding energy
(N - M)/N; tested first on the constant-density Schwarzschild interior and on the identity
dh/dy = g + h).
- V1.a The first maximum of the binding energy lies at y_max = 0.33403 +- 2e-4 (lead 0.334032;
  printed 0.334, paper.tex:953). Refuted if |y_max - 0.334032| > 1e-3.
- V1.b eps_max = 0.0356 +- 0.0001, R/M = 13.6 +- 0.1, Z(0) = 0.512 +- 0.002 (note Table
  tab:parameters). Refuted outside these.
- V1.c 0.324 and 0.344 lie on opposite sides of y_max, each 3.0 +- 0.1 per cent away in y0.
  The binding energies of the two differ from eps_max by only ~1e-5 absolute (quadratic
  maximum): the bracket is narrow in eps but not in the stability exponent.

V2 Fates at N = 1e6 and the marker (own reader of cc.nrpic.hst with the restart rule; tested
on a synthetic history with an overlapping continuation and a known crossing).
- V2.a The first crossing of alpha_min (column 16) below 0.3, linear between records,
  reproduces 252.31 (N6b344), 217.97 (A16b344), 252.41 (N6b344e1), 229.79 (A344s1i) to 0.01 M.
  Refuted by a difference above 0.25 M (one record) or a different fate.
- V2.b N6b324, A16b324, N6b324e1, A324s1i, N6c have alpha_min >= 0.3 at every record to
  600 M, and their histories reach t >= 599.75 M. Refuted by a crossing or a history that ends
  early (then "holds 600 M" is not shown).
- V2.c No output directory of the eleven threshold runs nor of the D2 series holds a horizon
  file (no `*horizon*`, `*ahf*`, `*.ah*` files, no `<fastflow>` or `<ahf>` block in the decks).
- V2.d The stable members' central lapse (alpha_probe, column 13, probe at the origin): 20 M
  block means of alpha_c - alpha_c(0) within [-0.03, +0.03] over 0-600 M for N6b324,
  A16b324, N6b324e1; N6b324e1 minus N6b324 below 0.01 in every block (B20.3 as written).
- V2.e The decks of the legs differ from N6b344/N6b324 only in the refined region of M/16 or
  in shift_eta; all N = 1e6 members share the sampler and seed of N6c. Refuted by any other
  differing physics line.
- V2.f What the marker can show [JUDGEMENT, before looking]: alpha_min < 0.3 on a 1+log slice
  marks a strong-field region that, in the collapse runs, is followed by the end of the run or
  excision; it is a slicing-dependent time, not a horizon, and its absence by 600 M is not
  proof of stability beyond 600 M.

V3 Controls without the kick.
- V3.a Crossing times 295.78 M (N4c) and 534.81 M (A334s1c) reproduced to 0.01 M; N6c none.
- V3.b The Hamiltonian-constraint "floor" over 100-300 M scales as 1/N between the three runs
  if it is a squared norm (column H-norm2 of cc.z4c.user.hst, or a mean of squares), as
  N^-1/2 if it is a norm of the field itself. The lead's values 7.68e-2, 7.86e-3, 7.90e-4 fall
  by 9.8 and 9.9 per decade: I predict that whichever column reproduces them is a squared
  quantity or a mean of the absolute constraint, and say which.
- V3.c [JUDGEMENT] "the controls' collapses are particle noise" is consistent with, but not
  shown by, three runs that differ only in N (one seed each, one mesh): N changes both the
  noise and the sampled model's discreteness; no seed spread of t_c at fixed N exists for the
  N = 1e4 control, and t_c grows much more slowly than N.

V4 Collisional members (CC2, Kn_c = 10).
- V4.a Crossing times 163.41 (D2f2s1, M/8), 158.42 (M16), 164.01 (D2eta1), 165.65 (D2f2s2),
  and the f = 1, f = 4 members, reproduced to 0.01 M. 206.64 M (M/4) is the mean of two
  earlier runs of the decisive package: checkable only if those runs are found.
- V4.b Sum of n_coll over sum of sum_P (column 7 over 6 of cc.coll.hst) over 0-100 M for
  D2f2s1: 1.0008 +- 0.0005; |z| = |n - P|/sqrt(P) < 3 for every member.
- V4.c An expected rate computed by me from a particle snapshot of D2f2s1 (cell occupation and
  Moller speeds of random pairs of the actual particles in each collision cell, equation 1 of
  collisions.md) equals the code's sum_P at that time within 2 per cent (the flat-space
  factor alpha/sqrt(gamma) taken from the snapshot's metric if it carries it, else bounded).
- V4.d Collision energy budget: |sum of dE_particles| (column 31) over sum_MH_particles (column
  32) below 1e-15 to the first excision on M/8, M/16 and shift_eta 1.
- V4.e The seed pair differs by |165.65 - 163.41| = 2.24 M > 2 M: D2.3 seed-pair part failed
  as written; reproduced if my crossings give a difference above 2 M.

V5 Threshold location against collapse time.
- V5.a (252.31 - 217.97)/252.31 = 13.6 per cent from my crossings. The location claim rests on
  fates only; with one seed per member, two meshes and two gauges at one N = 1e6 and one
  (M/8) at N = 1e5, G2 can claim a bracket (0.324, 0.344) around y_max, i.e. +-3 per cent,
  not a located threshold with an error bar from three-way convergence of a growth rate
  [JUDGEMENT].
