# JOURNAL of package floor (Track E, gate G2): does the floor of the spectral convergence scale with the noise amplitude?

## entry-1 (2026-11-24 15:40 PST, lead of E, batch 13): question, runs, predictions, written before submission

Question. The spectral convergence of the slow-roll case (Fig. 7 of arXiv:2512.14649, remade in
`../repro/figs/RESULTS.md` Fig. 7 and the working note `../repro/note/manuscript/main.pdf`) stops at the
lowest injected shells: at N_f (t = 8.5) the 128- and 256-cell curves lie on each other there. Values at
s = 1 [VERIFIED by the lead from the dump-pass files, `scratch/E-stoch-inf/E-20261124-133251-42e8aab/C128S/
d00017.npz` and `E-20261124-213029-e937f69/CL256Sc/d00017.npz`; the ten shells n^2 = 2, 3, 4, 5, 6, 8, 9, 10,
11, 12]:

| statistic over the ten shells | C128S (s = 1) | CL256S (s = 1) |
|---|---|---|
| median of abs(1 - P_NR/P_lin) | 1.48e-7 | 1.55e-7 |
| sqrt(median of sum abs(c_NR - c_lin)^2 / sum abs(c_lin)^2), amplitude | 3.78e-7 | 3.78e-7 |
| signs of 1 - P_NR/P_lin, in that order | ++----+--+ | ++----+--+ |
| median abs(1 - P_NR/P_lin), shells n^2 >= 49 (13 shells) | 6.03e-7 (stencil) | 3.64e-8 |
| per-mode relative rms (`fig7_fig8.json`, all modes with W > 1/2) | 7.11e-7 | 6.71e-7 |

The verifier showed the floor independent of dx, dt and the linear reference (`../repro/verify/
VERIFIER.md` 8.3). Candidate named in RESULTS.md: the second order of the field. Its relative size
delta_2/delta_1 is proportional to s, so at s = 1/2 it halves.

Runs (two, shared card queue, priority 2, release card build core-v0.6
`/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena`, kind production, gate G2): each is its s = 1
counterpart with one change, `scalar_field/noise_mode_scale=0.5` (factor on the mode functions: the slice
and the sources together; coord/INTERFACES/scalar_field_2.md).
- FL128h: as C128S of repro/scope's SMALL batch (`../repro/scope/inputs/small.list`, line C128S): SR deck
  `../repro/scope/inputs/sr_paper.athinput`, 128^3, nmax2 = 64, `ladder/inputs/modes_n64.txt`, dump_dt 0.5.
  Cost 0.01-0.05 card-hours expected (SMALL ran eight such runs in 0.081); ceiling 0.25.
- FL256h: as CL256S of `../repro/scope/queue.txt`: SR deck, 256^3, nmax2 = 64, same mode file,
  dump_constraints and dump_magnitudes false, dump_dt 0.5, to N_f. Cost 0.35-0.6 card-hours expected
  (CL256S 0.352 + 0.140 with a preemption between); ceiling 1.0.

Reading (next session): `../repro/figs/figures/dumppass.py --run <dir> --base sr --label ... --last
--scale 0.5 --save-modes` on each, the s = 1 counterparts again with `--last --save-modes`, the same
ten shells; figure of abs(1 - P_NR/P_lin) per shell for the four runs, with s = 1 curves divided by 2.

Predictions:
- F1 (main; second order): at both 128 and 256 the ratios R = value(s = 1)/value(s = 1/2) of the median
  power statistic and of the amplitude statistic lie in [1.6, 2.5]; expected values at s = 1/2: median
  about 7.4e-8 (128) and 7.8e-8 (256), amplitude about 1.9e-7 at both; the 256 per-mode relative rms about
  3.4e-7. Refuted if any of the four ratios lies outside [1.6, 2.5]. Readings named in advance:
  R in [0.8, 1.25] = a floor independent of the amplitude (a relative error of the linear part: the
  reference mode functions, the synthesis or a reduction in the reader); R in [3.2, 5] = third order
  (relative size proportional to s^2, like the common-mode part of g2prod entry 2.3); 1.25-1.6 or 2.5-3.2
  = mixed.
- F2 (same realisation): the signs of 1 - P_NR/P_lin over the ten shells stay ++----+--+ at both
  resolutions. Refuted if more than two of the ten change (then the floor is not a deterministic
  function of the realisation; F1 would then be read as noise).
- F3 (control of the reading): at 128 the median over the shells n^2 >= 49, where the stencil error
  dominates, stays within [0.8, 1.25] of 6.03e-7 (a linear relative error does not depend on s).
  Refuted outside: then the scale enters the comparison wrongly or the stencil error is not linear,
  and F1 is not judged until that is found.
- F4 (independent of dx at s = 1/2 too): the medians of the power statistic at 128 and 256 differ by
  at most 15 per cent.
- F5 (cost): FL128h below 0.05, FL256h at most 1.0 card-hours.
A cause is named only if F1 and F3 hold.

## entry-2 (2026-11-25 03:53 PST, lead of E, batch 17): FL128h has run; first reading; the corrected reading

FL128h ran as E-20261125-041742-71d74fb (queue q0037, Slurm job 5245, one segment, 110 s wall, 693
cycles to t = 8.5; 0.0308 card-hours from its finished manifest). F5 for FL128h HOLDS (below 0.05).

First reading, E-20261125-115056-983a32a (`floor_read.py`, the recipe of entry 1 with `--scale 0.5`
on the s = 1/2 run). The s = 1 re-pass of C128S gives the values of entry 1 digit for digit (median
1.482e-7, amplitude 3.777e-7, signs ++----+--+, median n^2 >= 49 6.029e-7, per-mode rms 7.111e-7). The
s = 1/2 statistics are 3.0000003 (median), 1.0000001 (amplitude), all signs negative: P_NR/P_lin = 4.
F3, the control of the reading, is REFUTED as the recipe stood (3.0 against 6.03e-7 +- 25 per cent),
so F1 is not judged on this reading, as entry 1 required. Cause, found on the files: the lockstep
`.modes` record of a run with `noise_mode_scale = 0.5` already carries the factor (record ratio
R(FL128h)/R(C128S) = 0.5 exactly at t = 8.5 on every shell; coord/INTERFACES/scalar_field_2.md line
74: the scale is applied to the mode file), and dumppass multiplies c_lin by --scale once more. The
recipe of entry 1 was wrong, not the run. The corrected reading passes --scale 1 for the s = 1/2 run
(`floor_read.py --sh-scale 1`, default now) and stores the record ratio it checks.

Not blind: the same first reading printed a split that does not depend on c_lin (with e = c_NR - c_lin
per mode and e = s L + s^2 Q, Q = 2 [c_NR(1) - 2 c_NR(1/2)]); its shell norms equal those of e(1)
within 2 per cent on all ten shells, which already says the floor is second order. The corrected
reading is therefore judged against F1-F4 of entry 1 unchanged, and its outcome is labelled as read
after that split was seen. Expected from the split: R about 2 for the amplitude statistic and the
per-mode rms (relative error proportional to s), about 2 for the median power statistic, signs kept,
F3 within [0.8, 1.25].

## entry-3 (2026-11-25 03:55 PST, lead of E, batch 17): outcome at 128 (corrected reading E-20261125-115344-a22128b)

Reading E-20261125-115344-a22128b (`floor_stats.json`, `fig_floor.png` looked at): record ratio of the
two lockstep records 0.5 exactly at t = 8.5 (the check of entry 2); s = 1 values as in entry 1.

| statistic (ten shells n^2 = 2-12) | C128S, s = 1 | FL128h, s = 1/2 | R = s1/sh | entry 1 band |
|---|---|---|---|---|
| median abs(1 - P_NR/P_lin) | 1.482e-7 | 7.79e-8 | 1.903 | F1 [1.6, 2.5]: HOLDS |
| amplitude statistic | 3.777e-7 | 1.887e-7 | 2.001 | F1 [1.6, 2.5]: HOLDS |
| signs | ++----+--+ | ++----+--+ | 0 flips | F2 <= 2 flips: HOLDS |
| median over n^2 >= 49 (13 shells, stencil) | 6.029e-7 | 6.222e-7 | 0.969 | F3 [0.8, 1.25]: HOLDS |
| per-mode relative rms (W > 1/2, all injected modes) | 7.11e-7 | 4.08e-7 | 1.74 | reported (F1 names it at 256 only) |

F1 at 128 HOLDS (both ratios; the expected values of entry 1, 7.4e-8 and 1.9e-7, are met to 5 and 1
per cent); F2 and F3 HOLD at 128; F5 holds for FL128h. F1 at 256 and F4 wait for FL256h (q0038,
waiting). Figure: on every one of the ten shells the s = 1/2 curve lies on the s = 1 curve divided by
2, not on the curve itself (an amplitude-independent floor) nor on the curve divided by 4 (third
order). The after-data split of entry 2 agrees: Q (from the two c_NR alone) equals e(1) in norm within
2 per cent on every shell. Status [VERIFIED at 128 by this run; the cause is named because F1 and F3
hold, as entry 1 requires]: the floor of the slow-roll spectral convergence at the lowest shells is
the second order of the field (relative size proportional to the amplitude), not a numerical floor.
The per-mode rms ratio 1.74 (below 2) says that a part of the per-mode scatter at s = 1/2 does not
halve; it is reported, not judged at 128. Risk R28 is answered at 128; it closes when FL256h has run.

## entry-4 (2026-11-25 07:45 PST, lead of E, batch 19): FL256h has run; outcome at 256; the floor is closed

FL256h ran as E-20261125-115534-8414659 (queue q0038, Slurm job 5284, one segment, 1573 s, 1386 cycles to
t = 8.5; 0.44 card-hours from its finished manifest). F5 for FL256h HOLDS (at most 1.0).
Reading E-20261125-151222-d5a5f2f (`floor_read.py --pair FL256:...`, the corrected recipe of entry 2,
--sh-scale 1; `floor_stats.json`, `fig_floor.png` looked at). Record ratio of the two lockstep records 0.5
(min 0.49999999999999994, max 0.5) at t = 8.5, as the reading requires. The s = 1 re-pass of CL256S (dump 17
of E-20261124-130952-4be980b) gives the values of entry 1 (median 1.555e-7, amplitude 3.784e-7, signs
++----+--+, median n^2 >= 49 3.64e-8, per-mode rms 6.71e-7).

| statistic (ten shells n^2 = 2-12) | CL256S, s = 1 | FL256h, s = 1/2 | R = s1/sh | entry 1 band |
|---|---|---|---|---|
| median abs(1 - P_NR/P_lin) | 1.555e-7 | 7.78e-8 | 1.997 | F1 [1.6, 2.5]: HOLDS |
| amplitude statistic | 3.784e-7 | 1.892e-7 | 2.000 | F1 [1.6, 2.5]: HOLDS |
| signs | ++----+--+ | ++----+--+ | 0 flips | F2 <= 2 flips: HOLDS |
| per-mode relative rms (W > 1/2) | 6.71e-7 | 3.35e-7 | 2.001 | expected 3.4e-7: met |
| median over n^2 >= 49 (13 shells) | 3.64e-8 | 2.14e-8 | 1.70 | reported (F3 is a 128 control; at 256 the stencil part is small, so this median mixes the two parts) |

F1 at 256 HOLDS (the expected values of entry 1, 7.8e-8, 1.9e-7 and 3.4e-7, are met to 0.3, 0.4 and 1.4 per
cent). F4 HOLDS: the s = 1/2 medians at 128 and 256 are 7.79e-8 (E-20261125-115344-a22128b) and 7.78e-8,
0.1 per cent apart (band 15 per cent). F2 holds at both resolutions, F3 held at 128, F5 holds for both runs
(0.0308 and 0.44 card-hours). The after-data split (entry 2) agrees again: Q from the two c_NR alone equals
e(1) in norm within 0.4 per cent on every shell at 256 (largest 0.32 per cent, n^2 = 4). Figure: on every shell the s = 1/2 curve lies on the
s = 1 curve divided by 2, not on the curve itself nor on the curve divided by 4.
Status [VERIFIED at 128 and 256 by runs E-20261125-115344-a22128b and E-20261125-151222-d5a5f2f]: the floor of
the slow-roll spectral convergence at the lowest shells is the second order of the field (relative size
proportional to the amplitude), independent of the spacing; risk R28 is closed. The per-mode rms ratio,
1.74 at 128 and 2.00 at 256, says that at 128 a part of the per-mode scatter at s = 1/2 is the stencil
part, which does not depend on s; at 256 that part is negligible at these shells.
