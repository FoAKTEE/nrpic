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
