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
