# JOURNAL of package repro/ablation (Track E, batch R1c, 2026-11-22)

Ablation of the stochastic backreaction of arXiv:2512.14649 (P1 =
`kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`; Fig. 9 = `fig:ablationback`, P1:777-790; the
statement P1:520) onto the cards: level 2 and level 1 against level 0, all three with the mode
equation of the noise on the mesh (decision 0031 item 1). Executable: branch `core/noise-level2`,
`/data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu` (source 6ca93cba, READY there;
the exception of decision 0031 item 3). Predictions are written here before each run.

## Entry 0 (2026-11-22 19:45 PST): the inputs, checked against the scope audit and the figure

Copied with `git show core/noise-level2:tracks/core/analysis/noise_level2/inputs/...` into
`inputs/` (six 256^3 decks) and `inputs/card/` (four 64^3 decks of core's T5).

Check against `repro/scope/SETUP_AUDIT.md` [VERIFIED by diff, commands in README]: each of core's
six 256^3 decks differs from `repro/scope/inputs/{sr,usr}_paper.athinput` in exactly three places:
`basename` (sr256_l0m, ...), `noise_level` (0, 1, 2) and the added line `noise_mode_eq = mesh` (l0m,
l1m; level 2 implies mesh). Seed (rng_seed 20261115 = seed A), mode files (`ladder/inputs/modes_n4096.txt`,
`usr/inputs/modes_usr_n4096.txt`, both present), nmax2 = 4096, window s = 5, sigma = 1, projector
stencil, kicks, slice options, Courant 0.25, tlim (8.5; 10.437508874065651), gauge, damping and
dissipation are those of the audited decks: audit items 1-17 and 20-26 hold unchanged; item 18
(backreaction level) and item 19 (mode equation on the mesh, now P1's own form) are what the
ablation varies.

Check against what the figure needs (`repro/scope/HANDOFF.md`, Fig. 9 row: "dumps at N_f, shell
spectra L1/L0 - 1"): core's decks write 35 (SR) / 41 (USR) dumps every 0.25 / tlim/40 with H, M_i, E
and the magnitudes [H], [M] (27 variables, 3.6 GB each at 256^3): 127-148 GB per run, 0.83 TB for
the six, for a figure that reads the final dump. R^NR needs phi, Pi, K, chi and gt_ij only (scope
audit item 24). Changed, output only: `dump_dt` 0.5 (SR) and 0.5218754437032825 = tlim/20 (USR),
the cadence of RL1/UL1 in the scope queue (18 / 21 dumps, the last at N_f: P256v6 has dump 17 at t =
8.5, U256ap 21 dumps); `dump_constraints = false`, `dump_magnitudes = false` (the record
`.sf.con.hst` every cycle stays); added `noise_rmodes_dump = true` (per-mode projections of the
mesh R, 549 k lines, about 60 MB per dump), so that the per-mode difference of the noise field
(core's test quantity of T1c and the USR check) can be read beside the spectra. Expected disk:
about 43 GB per SR run, 50 GB per USR run, 0.28 TB for the six (plus restart files every 2.0).
The dump cadence does not change the steps (scope entry 0, run E-20261123-020506-a459085).

Smoke list `inputs/smoke.list`: core's four T5 decks unchanged (sr64_l0, sr64_l2, usr64_l0, usr64_l2)
and two of mine, `card/sr64_l1m` (level 1 on the mesh) and `card/usr64_l0m` (level 0 on the mesh),
each with `noise_rmodes_dump = true`, so that the card runs every code path of the six ablation
runs (mesh levels 0, 1, 2 and the per-mode writer) before they reach the cards.

Prediction X0 (processor parse check of the eight edited or new decks, release-free branch
processor executable `athena_cpu`, overrides 32^3, nmax2 = 64, nlim = 2, one core): every run exits
0, writes the t = 0 dump and, for the seven decks with `noise_rmodes_dump`, a `.rmodes` file of
`# time 0` with one line per mode of nmax2 = 64 (the number in its header). Refuted by any parse
error, a fatal message of the noise options, or a missing `.rmodes`.

## Entry 1 (2026-11-22 19:50 PST): predictions of the card runs, written before any submission

Quantity of Fig. 9: per shell |n| (integer bins of |k|/dk, shells with more than 10 modes, P1:454,
559) the dimensionless power Delta(k) = k^3 <|R^NR_k|^2>/(2 pi^2) at N_f, R^NR as in
`ladder/scripts/ladder_lib.py` (scope audit item 24), and the ratios
r20(k) = Delta_L2/Delta_L0m - 1, r10(k) = Delta_L1m/Delta_L0m - 1 (same seed, same steps).

Why the sizes below [JUDGEMENT]. Level 2 changes the coefficients of the mode equation by the local
values; relative to the uniform ones they differ at first order in the perturbations, so the
projected coefficients c_n of the mesh R change at relative first order in the amplitude (second
order absolute): core measured 1.1e-4 rms (9.0e-4 max) in slow roll (T1c, 32^3) and 1.9e-3 rms at the
end of the inflection case (run core-20261123-032120-3d5b69f, 32^3, k <= 8 dk). The cross term of
such a quadratic correction with the Gaussian first-order coefficients vanishes in expectation
(odd moment), so a shell's power changes by a scatter of order 2 rms(dc/c)/sqrt(N_shell) with a
random sign from shell to shell, plus the square (dc/c)^2: largest at the lowest shells, falling
about as 1/k. Level 1 changes only the uniform background (box means against the Friedmann
lockstep: 2.0e-12 in phi, 8.6e-12 in Pi, ladder A1, run E-20261115-194633-9e04ed8), so r10 is coherent
in k and tiny in slow roll; in the inflection case the box means pick up the second-order mean of
the grown perturbations, still small while modes cross the window (they cross by N* + 4.2, the
growth of R comes later).

P-T5 (smoke batch at 64^3 = core's pending test T5, six runs, kind scouting):
(a) every run exits 0, reaches tlim (8.44 SR, 10.5 USR: 344 and 428 cycles) with finite records and
writes its dumps (9 SR, 22 USR) and, where asked, `.rmodes` files;
(b) card against core's processor runs of the same four decks (core-20261123-030705-6b6a4bd, 30
cycles, threaded branch build): over cycles 0-30 the box means <phi>, <Pi>, <K>, <chi> (record
columns 3-6) agree within 1e-12 relative and rms(phi - <phi>), rms(Pi - <Pi>) (columns 8, 9) within
1e-7 relative (the perturbation is 1e-7 of phi, so summation order costs about 1e-9 of it);
(c) wall per cycle on the card, level 2 over level 0: between 0.95 and 1.5 for each scenario;
(d) preview of the ablation at 64^3 from the records at tlim: |rms_phi(l2)/rms_phi(l1m) - 1| < 1e-4
(SR) and |rms_phi(l2)/rms_phi(l0m) - 1| < 1e-2 (USR).
Refuted (a defect to report to core, and the 256^3 runs are held): any non-zero exit or guard stop,
non-finite records, a missing output, or a card/processor difference above 1e-5 relative in (b).
Outcomes of (c) and (d) outside their bands are recorded, they do not hold the runs.

P-A1 (slow roll, 256^3): |r10| < 1e-8 at every shell; r20: largest values at the lowest shells,
rms over the shells with |n| <= 32 between 1e-7 and 1e-4, max over all shells <= 2e-4, no common sign
(between 30 and 70 per cent of shells positive), no rise towards the cut. Consistent with P1:520
(".. <~ 1 per ten thousand" for all scales) if max |r20| <= 2e-4.

P-A2 (inflection, 256^3): |r10| < 1e-5 at every shell, smooth in k (one sign over most shells);
r20: rms over shells between 1e-5 and 1e-3, max <= 3e-3, larger for the shells that cross during the
USR phase (k > e^2.52 dk = 12 dk) than below. Consistent with P1:520 if max |r20| <= 2e-4 (the paper's
bound; our band is wider because its USR set-up and ours share the seed only in kind).

P-A3 (controls, no new run): (i) at t = 0 the dumps of the three levels of a scenario are bit-identical
in phi, Pi, chi, K, gt_ij, At_ij (the slice does not depend on the level), and identical to the t = 0
dump of P256v6 (E-20261121-202935-31520bc) / U256ap (E-20261121-211214-0377aab) in the common
variables; (ii) level 0 on the mesh against the released level 0 on shells (P256v6, U256ap):
|Delta_L0m/Delta_L0shells - 1| at the top shells (|n| >= 56) between 1e-3 and 5e-2, falling towards
low k about as (k dx)^6, below 1e-4 for |n| <= 16 (the stencil symbol of the Laplacian, 1.83 per cent
in k^2 at the cut on the axes, core T3); (iii) the record <|H|/[H]> of each level-2 run within a factor
2 of its level-0-mesh twin at every cycle.

Refutation of the implementation (report to core, decision 0031): a first-order difference between
levels, i.e. any |r10| above 1e-6 (SR) or 1e-3 (USR); any |r20| above 1e-3 (SR) or 3e-2 (USR); r20 of
one sign over more than 90 per cent of the shells with |r20| > 1e-4; a rise of r20 or r10 towards the
cut with the (k dx)^6 shape of the stencil (a shells/mesh mix-up); a failure of P-A3 (i); a guard stop.

Cost (prediction): SR 0.55-0.65 card-hours per run (P256v6 0.509 for 1386 cycles; the mesh R and its
projection +5-15 per cent, core section 7; fewer dumps), USR 0.65-0.75 (U256ap 0.619 for 1701
cycles); smoke about 0.05. Total 3.7-4.3 card-hours, below the package cap of 5. Refuted by a 256^3 run
above 1.0 card-hours; the sequencer then holds the remaining ablation runs (`scripts/sequencer.sh`,
cap 5.0 card-hours for this package).
