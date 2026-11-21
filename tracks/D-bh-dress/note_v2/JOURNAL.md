# note_v2: journal (predictions first, then outcomes)

Helper package of D-bh-dress, batch 6 (2026-11-21 afternoon, processors only, 0 card-hours).
Two deliverables: (1) the working note v2 (the state after gate G1 plus the first G2 result
ES-F); (2) a second sampler seed of the Kerr spike stationarity test (gate review G1, section 5
item 3). The history of note v0/v1 is `../note/JOURNAL.md` (entries P1-P15); this journal
starts at N1.

## N0 (2026-11-21T21:14Z): setup

`git merge --no-edit main` (aa164a54). `note_v2/` is a copy of the committed files of `note/`
at aa164a54 (every tracked file but JOURNAL.md and README.md), so that v2 lives in this
package's own directory; the lead decides whether it replaces `note/`. Read: CLAUDE.md,
CHARTER to "Owners", `stage/G1/GATE_REVIEW.md` in full, `spike/README.md` sections 1-7, the
verifier's V4 (`verifier_g1/VERIFIER.md` 160-190, `verifier_g1/JOURNAL.md` entries 7-8),
`spike/sample_kerr.py`, the head of `spike/analyze_kerr.py`, the analysis output of seed 1
(D-bh-dress-20261115-174954-786ddcc/kerr_main_analysis.json).

## N1 (2026-11-21T21:20Z): Kerr spike, second sampler seed: prediction

**What is tested.** Seed 1 (IC D-bh-dress-20261115-172335-9e5ccf9, seed 20261116, 48000
particles, Hernquist-grown DF of FdRW, a = 0.8, E <= 0.99, Kerr-Schild slice; AthenaK run
-172611-1e40191 on the analytic Cartesian Kerr-Schild metric to 20000 M; analysis
-174954-786ddcc against the reference grid -172646-ed6a510) has time-averaged counts below the
reference in the three inner ranges: time average over expected 0.9590, 0.9823, 0.9896 in
0-4, 4-6, 6-10 Gm (deviations -4.1, -1.8, -1.0 per cent, z = -1.11, -0.91, -1.01 with the
error of a time average over independent orbit draws, sigma_rel = 3.69, 1.94, 1.03 per cent),
and 0.9993, 1.0016 in 10-16, 16-40 Gm (z = -0.11, +0.59). Against the fresh verifier's own
reference (D-20261121-040826-9d5051a) the same deficits read 3.1, 1.8, 0.9 per cent. Question
of the gate review: a bias of the sampler (or of the evolution) at r < 10 Gm, or noise?

**Run.** Same sampler, same arguments, only the seed changed: `sample_kerr.py --n 48000
--nfiles 6 --a 0.8 --ecut 0.99 --slice ks --seed 20261121` (6 files of 8000 instead of 12 of
4000, to stay within six cores; the files only split the particles, every geodesic is
independent). Same executable as seed 1 (release core-v0.3 processor build,
`.work/build_cpu_v03/src/athena`), same input `spike/kerr_geodesic.athinput`, same overrides
(`time/tlim=20000 particles/snap_dt=100 particles/dt=0.05`), so the seed is the only change.
Same analysis (`spike/analyze_kerr.py`, reference grid -172646-ed6a510). The comparison of the
two seeds is a new script `note_v2/kerr_seed2/compare_seeds.py` with a figure.

**Prediction (H0, no bias: the deficits of seed 1 are the noise of one set of 48000 orbits).**
For seed 2 the time-average deviations d2 in 0-4, 4-6, 6-10 Gm are independent draws with
standard deviations close to seed 1's sigma_rel (3.7, 1.9, 1.0 per cent; the sampler's own
estimate for seed 2 should lie within 20 per cent of these); their signs are not tied to
seed 1's. Quantitatively: the sum of the three inner z values of seed 2, Z2 = z(0-4) +
z(4-6) + z(6-10), is N(0, sqrt 3) under H0 and N(-3.0, sqrt 3) under the bias hypothesis H1
(bias equal to seed 1's deviations). I predict H0 and take Z2 > -1.5 as holding it.
Refuted (bias indicated) if Z2 <= -1.5; strongly if Z2 <= -3 or if all three inner ranges
are again below the reference with |z| > 1. This is a weak test and I say so beforehand: the
two hypotheses are 3.0/sqrt 3 = 1.7 standard deviations apart, so a single seed misclassifies
either way with probability about 0.19. The two-seed mean deviation has an error of
sigma/sqrt 2 = 2.6, 1.4, 0.7 per cent; I will quote it as the bound on a bias.

Side predictions (each refutes the run as a valid repeat if it fails): no non-finite record;
no particle within r_+ = 1.6 M; max |dE/E| < 2e-5 (seed 1: 7.9e-6); chi^2 of the binned counts
(dof near 47) has its median within the 3-sigma band [0.38, 1.62] dof (seed 1: 43.8);
late/early-half ratios within 2 sigma_rel of 1 in every range; the outer two ranges within
2 sigma of the reference (H0 and H1 agree there).

Cost: seed 1 took 1278 s on 12 single-core processes (4000 particles each); seed 2 with
8000 per process on 6 cores, about 45 min. No card-hour.

## N2 (2026-11-21T21:33Z): note v2 build, predictions

Text changes made (from stage/G1/GATE_REVIEW.md sections 5-6 and the task): the sentences of
v1's "Plan and open items" (old main.tex lines 198-200: run to a larger scale factor "belongs
to the next version", D-pre-3 criterion "open, ruling requested", late drift "open") are
replaced; the infall section says that the criterion was changed after the first runs by a
ruling (decision 0021 item 2) and that the power law itself is not tested and why (errata row
1.7); Q16 is in the text, in a new figure (fig_q16) and in ledger part 7; the matched vacuum
control with the faces at +-384 M (V-1B) is named as the floor of the null test (floor
subsection, first-run subsection, ledger part 8); the relaxed-lapse finding (decisions 0022
item 3, 0025 item 3) has its own subsection and ledger rows (V-1GB, ES-1G, ES-1GB); ES-F is a new
subsection with fig_esf and ledger part 9; the timeline header and the architecture chain are
at the post-G1 state. Scripts developed into scratch/D-bh-dress/tmp/note_v2_dev* (not
registered; development only, nothing from there is committed or cited).

Checks of my own figure scripts against the packages' registered analyses, before the
registered run (development output, recorded here so the run can refute them):
- fig_esf.py recomputes from the raw ES-F outputs (finder summary, removed record, energies by
  tag, V-1 finder summary) D1 raw 9.879e-3 and control-subtracted 1.469e-3, F_rem 0.24137 and
  the (iii) overall median 2.198e-3: equal to esf_criteria.json / esf_analysis.json to all
  printed digits. New number of mine: the largest |control-subtracted closure| after 20 M is
  3.9e-3 (the end value 1.5e-3 is one sample of a band of about 1e-3 around 2e-3).
- fig_q16.py: largest |run/hybrid_cc - 1| over all snapshots with 3 <= a/a_i <= 12 is 0.43 per
  cent (M_ta) and 0.91 per cent (dress); the infall README's 0.2-0.6 and 0.5 per cent are at
  the tabulated epochs 4, 8, 12 only. The note quotes "within half a per cent" (M_ta) and
  "within one per cent" (dress), which hold for every snapshot.

Predictions for the registered build (run_all with the 14 scripts; then latexmk; then the
checker with --compile and the forbid list of WRITING_GUIDE.md):
- B1: run_all reports every script clean; the regenerated fig_esf_numbers.json and
  fig_q16_numbers.json equal the development ones (same inputs, same code).
- B2: ledger.py writes ten ledger parts (1-6 of v1 unchanged in content, 7 Q16, 8 vacuum
  controls and relaxed lapse, 9 ES-F, 10 Kerr seeds) and the claims check of v1 (76
  statements, 66 agree) unchanged, because no v1 input changed.
- B3: the checker reports 0 undefined references, 0 undefined citations, 0 overfull boxes;
  forbidden-name hits only in the ledger appendix and scripts (exception 1 of the guide).
- B4: 22-24 pages.
Refuted if any script fails, a v1 ledger value changes, or the checker finds a defect I then
have to fix (I will record what and fix it).

## N3 (2026-11-21T22:02Z): outcome of N1 (Kerr spike, second sampler seed)

Runs: initial data D-20261121-211717-7b6374b (seed 20261121; 12 pilot cells without a hit,
seed 1 had 13; 0 envelope violations, seed 1 had 1), AthenaK D-20261121-212016-7e090f9 (exit 0,
2355 s on 6 single-core processes), analysis D-20261121-215955-0fb4ea2 (analyze_kerr.py, same
reference grid), comparison D-20261121-220011-d0deb0b (compare_seeds.py; figure
fig_kerr_seeds.png of that run looked at: panel (a) both seeds per range with the two-seed
mean, panel (b) running means; the seed-2 running means settle by ~5000 M).

| Range (r/M) | seed 1: d, sigma, z | seed 2: d, sigma, z | two-seed mean +- error |
|---|---|---|---|
| 0-4 | -4.10, 3.69, -1.11 | -1.06, 3.83, -0.28 | -2.64 +- 2.66 |
| 4-6 | -1.77, 1.94, -0.91 | -1.04, 1.97, -0.53 | -1.41 +- 1.38 |
| 6-10 | -1.04, 1.03, -1.01 | -0.04, 1.03, -0.03 | -0.54 +- 0.73 |
| 10-16 | -0.07, 0.67, -0.11 | +1.41, 0.68, +2.08 | +0.66 +- 0.48 |
| 16-40 | +0.16, 0.27, +0.59 | -0.07, 0.27, -0.27 | +0.04 +- 0.19 |

(d and sigma in per cent of the expected count; reference grid D-bh-dress-20261115-172646-ed6a510.)

- Main test: Z2 = z(0-4) + z(4-6) + z(6-10) = -0.84 > -1.5: **H0 HELD** (no bias indicated);
  not strong-bias either. Seed 2's sigma within 4 per cent of seed 1's (predicted within 20):
  held. The two seeds differ by 0.57, 0.26, 0.69 sigma in the inner ranges. The signs in the
  inner ranges are again all negative, but small (z -0.28, -0.53, -0.03); the combined
  two-seed z of the three inner ranges is -1.59 (sum over sqrt 3). So: no evidence of a bias
  at the 1.5-sigma level; the two-seed means bound a bias in 0-4, 4-6, 6-10 to about
  -2.6 +- 2.7, -1.4 +- 1.4, -0.5 +- 0.7 per cent. As written beforehand, a single seed decides
  weakly; this outcome halves seed 1's deficits but does not exclude a 1-per-cent bias.
- Side predictions: no non-finite record (0): held; chi^2 median 48.4 for 47 dof, inside
  [0.38, 1.62] dof: held; late/early within 2 sigma in every range (largest |late/early - 1|
  1.0 per cent in 0-4, sigma 3.8): held. **Refuted**: (i) the outer range 10-16 lies +1.41 per
  cent above the reference, z = +2.08, just outside the predicted 2 sigma (16-40 holds at
  -0.27); among ten range-seed values one beyond 2 sigma is expected about one time in three
  [JUDGEMENT], so I do not read it as a defect, but it is outside what I predicted. (ii) one
  particle of 48000 went inside r_+ (smallest r 0.400; seed 1: none, smallest 2.288), and with
  it max |dE/E| is not finite (prediction: < 2e-5); 15 particles went below their predicted
  pericentre by more than 1e-3 (seed 1: 14), the largest by 3.26 (seed 1: 3.1e-3). The
  plunging particle is diagnosed in N4 before anything else is concluded from it.

## N4 (2026-11-21T22:04Z): the plunging particle of seed 2, prediction

Script `kerr_seed2/plunger.py` (analysis only): find the particles whose max |dE/E| is not
finite or above 1e-3 in the seed-2 analysis (kerr_seed2_series.npz), read their radius at all
201 snapshots, and from the initial invariants (ic_meta.npz: E, Lz, C, rp) compute their
distance from the capture boundary, (C - C_crit)/C_crit with C_crit from kerr_lib.ccrit at
their starting radius, and the effect of their post-plunge snapshots on the 0-4 count.
Prediction: exactly one such particle; its initial C lies within 1e-3 (relative) of C_crit,
i.e. on the edge of the loss cone, where an energy error of the size seen in seed 1 (|dE/E| up
to 8e-6 near pericentres of 2.3 M) can carry it across [JUDGEMENT]; it plunges at a pericentre
passage and is then counted in the 0-4 range at every later snapshot (the analytic metric has
no excision), which raises seed 2's 0-4 time average by (fraction of snapshots after the
plunge) / (expected count 137.8), at most +0.73 per cent. Refuted if its C is farther than
1e-2 from C_crit (then a defect of the sampler or the pusher beyond separatrix sensitivity),
or if it never sits at r < 4 after the plunge.

## N4 outcome (2026-11-21T22:05Z): run D-20261121-220137-5123361 (plunger.py; plunger.png looked at)

**Prediction held** on every count. Exactly one particle (index 29068, file kerr_0) has a
non-conserved energy. Its initial invariants lie (C - C_crit)/C_crit = 7.2e-6 from the capture
boundary: the closest of all 48000 (rank 0; 74 particles lie within 1e-3, 562 within 1e-2), far
inside the predicted 1e-3. It starts at r = 20.1 M with predicted pericentre 3.66 M, reaches
3.64 M at the snapshot before, and is inside r_+ at the snapshot of t = 300 M (plunge between
200 and 300 M, at its first pericentre passage); afterwards it sits at r = 0.40 M (the analytic
metric has no excision) for 198 of 201 snapshots and is counted in 0-4 M. It raises seed 2's
0-4 time average by 0.715 per cent (predicted at most 0.73): 0.9894 with it, 0.9822 without
its post-plunge snapshots. [JUDGEMENT] The plunge is the separatrix sensitivity of an orbit that
the sampler drew on the edge of the loss cone (a relative distance of 7e-6 against energy
errors of order 1e-6 near pericentres of 2-4 M), not a defect of the sampler; seed 1 had no
particle that close, which would explain why it had none.

Consequence for N1, re-read with the post-plunge snapshots of that particle removed (a
correction found after the run; the pre-registered reading above stays the primary one): seed
2's deviations become -1.78, -1.04, -0.04 per cent in 0-4, 4-6, 6-10; Z2 about -1.0, still above
-1.5 (H0 holds); but now all three inner ranges lie below the reference in both seeds, and the
two-seed means are about -3.0 +- 2.7, -1.4 +- 1.4, -0.5 +- 0.7 per cent with a combined inner z
of about -1.7 (computed exactly by fig_kerr_seeds.py of the note). Reading: no significant
bias; a deficit of one to two per cent inside 10 M is neither shown nor excluded by two seeds.
What would decide it without the evolution: a direct test of the sampler at t = 0 with many
more particles (the expected count in 0-4 M is 138 per 48000), or a third and fourth seed.

## N2 outcome (2026-11-21T22:10Z): the build of note v2

Registered builds (run_all.py, every one 14 of 14 scripts clean): D-20261121-220354-daadc10
(first), -220513-c666211 (after the checker's wording points), -220624-879d83e (parameter table
without the overfull row), **-220728-a41c2f0 (final; its figures/ and tables/ are the committed
ones)**. The earlier three are superseded intermediate passes and stay on record.
- B1 HELD: every script clean; fig_esf_numbers.json and fig_q16_numbers.json of the first build
  equal the development ones byte for byte; the eight v1 *_numbers.json files equal v1's.
- B2 PARTLY REFUTED: ledger parts 1-6 are byte-identical to v1's ledger.tex, and parts 7-10 are
  new as planned; the claims check still counts 76 statements, 66 agree, but 15 of its
  locators are no longer found because the lead rewrote stage/G1/STATUS.md (and other
  documents) after v1 (values unchanged; the check is of the lead's documents, not of the note
  text). Not fixed here: the claims check is v1's tool; the lead may retire it or re-anchor it.
- B3 HELD after two fixes: the first checker pass found 9 negations, one "defect" (5.7), and one
  overfull box of 1.9 pt in the parameter table (my new rows); rewritten and split, the final
  pass gives 0 undefined references, 0 undefined citations, 0 overfull boxes; remaining hits:
  4 negations whose content needs them (the power law not tested, not excluded, rather than
  the boundary, not -9/4), 126 run ids in the ledger and scripts (exception 1 of the guide), 30
  project names in scripts only (exception 1). Checker log: scratch/D-bh-dress/tmp/check_v2_final.log
  (not registered: a check of the source, as in v1).
- B4 HELD: 22 pages.
Pages read (all 22, after the last build): the reading found Fig. 7 (the two Kerr seeds) out of
citation order, ahead of the Schwarzschild and Kerr spike figures; the float was moved after the
Kerr figure and the order checked again on pages 8-13. Every figure of the note was looked at as
a PNG this session: fig_es, fig_constraints, fig_floor, fig_esrun, fig_spike, fig_kerr,
fig_infall, fig_newton (v1 copies, regenerated identically), fig_esf, fig_q16, fig_kerr_seeds,
schem_architecture, schem_timeline (new or redrawn).

Observation, not tested: in the seed-2 profile figure of the analysis run
(kerr_seed2_profile.png) the outermost radial bin (about 80-100 M) lies 7-9 per cent below the
reference in every band at all three times; it lies outside the five ranges of the test.
Whether seed 1 shows the same (an edge effect of the energy cut or of the reference grid) was
not checked.

Correction (22:12Z): N4 and the first draft of the note said "the analytic metric has no
excision". That holds for the executable both seeds used (release core-v0.3, chosen so that
the seed is the only change); release core-v0.4 added lapse-threshold removal on the analytic
metrics (tracks/core/interfaces/REQUESTS_ADF.md on main, row D4). The note and README now say so.
