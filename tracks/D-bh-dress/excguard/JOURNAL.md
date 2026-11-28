# JOURNAL of package excguard (Track D): core's guard on horizon excision on the long deck

Owner D-bh-dress. Package of the lead (batch 34). Purpose: the test that decision 0045 item 2 puts first in
the scope of G3 ("horizon excision kept on, with core's excision guard tested first on the track's long
deck"), and that core left to Track D (`coord/INTERFACES/finder_stop.md` section 7: "Track D's deck to
240 M is a card run of Track D").

## Entry 1 (2026-11-27 15:35 PST, lead of batch 34, before any run): design, predictions, refutations

Background [VERIFIED, g2long JOURNAL entries 5, 6, 19 and 24]. ES-FL (run D-20261121-203150-15f2bad,
`initial_radius_0 = 0.8`, release core-v0.6) loses horizon excision at 219.5 M, when the smallest
coordinate radius of the horizon passes 4 x 0.8 = 3.2 M (nrpic.cpp guard, 4 x when absent); its dust is
then removed by the lapse rule (54944 removals by reason 2 to 399.5 M) and the (iii) medians step from
about +0.2 to +0.62 per cent. FK (run D-20261123-022725-a553496, `initial_radius_0 = 1.6`, guard radius
6.4 M) excises to its end: all 119848 dust removals by reason 3, (iii) medians in [+0.162, +0.249] per
cent from tau_rem 280 to 500 M, M_FK - M_ES-FL at most 1.8e-6 up to 219 M. Release core-v0.8 adds
`<particles> ah_exc_max_growth` (the guard radius is that factor times `initial_radius_<n>`) and
`<fastflow> polish_iterations_<n>` (finder_stop.md sections 1-3, 6).

Run EG8 (input `inputs/esflg8.athinput`, written by `tools/make_input.py`; diff against ES-FL's deck:
basename, tlim 500 -> 260 M, `ah_exc_max_growth = 8.0` with `initial_radius_0 = 0.8` kept (guard radius
6.4 M, FK's), `polish_iterations_0 = 100` with `mass_tol_0 = 1e-5` and `flow_iterations_0 = 400`,
`<fastflow> diagnostics = true`, restart every 25 M instead of 50 M). Executable: release core-v0.8,
`.work/build_gpu_v08/src/athena`. One card, chain, priority 2, cap 2.5 card-hours. Mesh, gauge (plain
1+log, Gamma-driver shift, no lapse_leak), step (cfl 0.25), data (run D-20261121-203042-82deeec) and the
other outputs are ES-FL's, so ES-FL, FK and the vacuum control V-1L are its comparisons.

Readers (existing, registered tools of g2long and g2runs, unchanged): `g2runs/tools/esf_criteria.py
--base esflg8` for (iii), D2, D3 against the control V-1L; `g2long/tools/d4_timing.py` for D4 with the
split at 219 M; `g2long/tools/fk_compare.py` (or an equivalent comparison of horizon summaries) for the
mass against FK and ES-FL; the removal reasons from `<base>.removed.bin` (fluxio). The status file of
the finder is read for every horizon number (decision 0040 item 3; finder_stop.md section 2).

Smoke test S1 (processors, `.work/build_cpu_v08/src/athena`, two cycles, one core) before the card run:
the input starts; the parameter dump holds `polish_iterations_0 = 100`, `ah_exc_max_growth = 8`,
`diagnostics = true`; `esflg8.horizon_status_0.txt` is written with the search at t = 0 found; that
mass equals ES-F's 0.9915211 (unpolished, from 0.8 M) within 3e-4. Refuted, and no card run, if the
input fails to start, the status file is missing, or the mass differs by more than 3e-4.

Predictions for EG8 (judged when it ends; each with what refutes it):

- E1 (the guard holds excision on). The smallest horizon radius (summary column 12) passes 3.2 M within
  3 M of 219.5 M and stays below 6.4 M to 260 M; every dust removal (tags >= 140) after t = 219.5 M is
  by reason 3. Refuted if a dust removal after 219.5 M is by reason 2 other than in the first 2 M after
  a resumption of the chain (the rule waits for the first successful search of a continued run; such
  removals are counted and named separately), or if excision stops before 260 M.
- E2 (the mass against the exact solution). Criterion (iii) of G2 read as written (median of
  M_AH(first finder sample >= t_rem) / M_LTB(tau_rem) - 1 per 10 M bin of tau_rem with at least 20
  removals): every counted bin within [+0.10, +0.32] per cent (FK's range [+0.162, +0.249], widened for
  polishing, about +5e-3 per cent, and particle noise). Refuted if any counted bin is above +0.45 per
  cent (the line of FK's P9: the step of ES-FL returns) or below 0.
- E3 (polished against FK's unpolished finder). M_EG8 - M_FK at common finder times on 20-219 M has a
  median in [+2e-5, +1.2e-4] (core's 6.0e-5 to 6.8e-5 below the converged mass for the rule of FK, on
  the vacuum puncture at M/8, finder_stop.md section 5; FK's plateaus 1.3e-4 apart). Refuted if the
  median is negative or above 3e-4.
- E4 (the finder's status). At least 99 per cent of the searches after t = 2 M are found; the found ones
  take 100 to 200 flow iterations. Refuted if more than 1 per cent fail after 2 M.
- E5 (D2 and D3 of G2 against V-1L). D2 holds at every sample after 20 M; D3 has no violation (FK: min
  margin -1.4e-4 against -3e-4). Refuted by any violation.
- E6 (D4). Before t_rem = 219 M no dust removal precedes its exact crossing (FK, ES-FL: none; minimum
  +0.0715 M); in the bin t_rem 240-250 M the fraction that precedes it is within 5 percentage points of
  FK's (about 5 per cent). Refuted if more than 1 per cent precede before 219 M.
- E7 (cost). 1.2 to 1.7 card-hours to 260 M (ES-FL 2.60 card-hours to 500 M, 5.2e-3 per M; about 520
  polished searches at 0.33 s). Refuted above 2.0 card-hours.
- E8. Finite to 260 M, exit 0, no guard stop.

What a pass means: with core-v0.8 the guard factor replaces the larger start radius of FK, so the G3
runs can keep `initial_radius_0 = 0.8` (the flow starts inside the horizon of the seed) and excise to
the end. A failure of E1 means the guard factor does not do what finder_stop.md section 3 says on this
deck, and the G3 runs then use FK's remedy (a larger start radius) until core has answered.

## Entry 2 (2026-11-27 15:50 PST, lead of batch 34): outcome of S1; EG8 queued

S1 HOLDS (run D-20261127-232517-6111945, `.work/build_cpu_v08/src/athena`, two cycles, one core, exit 0,
1044 s of processor time at 1.21e4 zone-cycles per second, as ES-FL's smoke tests of g2long entry 4):
- the parameter dump (header of `rst/esflg8.00000.rst`) holds `polish_iterations_0 = 100`,
  `mass_tol_0 = 1.0e-5`, `initial_radius_0 = 0.8`, `diagnostics = true`, `ah_exc_max_growth = 8.0`;
- `esflg8.horizon_status_0.txt` is written; the search at t = 0 is found (reason 0) after 126 flow
  iterations (the mass rule plus the 100 polishing iterations), mass 0.9915146861;
- ES-F's unpolished search at t = 0 gave 0.9915211031 (g2long entry 4, S2b): the polished mass is 6.4e-6
  below it, within the bound 3e-4. [Not predicted: the sign. Core's offset of the unpolished rule, 6e-5
  BELOW the converged mass, was measured on late dumps of the vacuum puncture; at t = 0 of these data
  the unpolished search from 0.8 M ended 6.4e-6 ABOVE the polished one. E3 concerns 20-219 M and stands
  as written.]
No figure: a two-cycle start-up check with three numbers, not a test of the physics.

EG8 entered the shared queue at priority 2 at 15:37 PST: q0085, run D-20261127-233719-db5be88, job 5536
(pending, Priority, at 15:48 PST). E1-E8 are judged when it ends, by the readers named in entry 1, with
figures; the outcome goes to core (core asked for it, outbox 2026-11-26 "v08-guard-and-polishing").

## Entry 3 (2026-11-27 23:38 PST, lead of batch 40, before the reader is run): what was seen, the reader

Seen before this entry (needed to close the run): the chain's STATUS is DONE (11 attempts, 10 cut by a
signal and not counted; the last, job 5596, ended at t = 260 M, cycle 8320, exit 0); sacct of 5596
COMPLETED; the segment logs' start and end stamps (E7's input). The run was closed with `nrpic-run finish`
in this session. Nothing of the finder, the removal record or the criteria had been read.
Reader `tools/eg8_read.py` (written now, one registered processor run, one core): the finder summary
filtered by the status file (searches not found dropped, decision 0040 item 3), then the existing tools
`g2runs/tools/esf_criteria.py` (E2, E5) and `g2long/tools/d4_timing.py` (E6, EG8 beside FK), and its own
E1, E3, E4, E7, E8; one figure `eg8_read.png`. E1-E8 are judged as entry 1 wrote them; nothing is
re-banded.

## Entry 4 (2026-11-27 23:43 PST, lead of batch 40): outcome of EG8 (run D-20261127-233719-db5be88; reader run D-20261128-074210-aa0a37a, figure `eg8_read.png` looked at)

Outputs: `scratch/D-bh-dress/D-20261128-074210-aa0a37a/eg8_read.json`, `criteria/esf_criteria.json`,
`d4/d4_timing.json`, `eg8_read.png`. One search not found (t = 1.0 M, iteration limit) was dropped from the
summary before the criteria were read.

- E1 HOLDS. The smallest horizon radius passes 3.2 M at t = 219.0 M and reaches 3.49 M at 259.5 M, below the
  guard radius 6.4 M; all 76696 dust removals are by reason 3 (horizon), 13352 of them after 219.5 M, none by
  reason 2 or any other reason; the last at t = 259.81 M. No record overlap had to be dropped. Answer to the
  question of the batch: yes, removals by the horizon rule continue past 219.5 M with the guard factor 8 and
  `initial_radius_0 = 0.8`, to the end of the run (panels a, b).
- E2 FAILED as written, not refuted. 34 counted bins of criterion (iii); 33 lie in [+0.175, +0.250] per cent;
  the first (tau_rem 0-10 M, 128 removals) is +0.056 per cent, below the band's lower edge 0.10. No bin above
  0.45 per cent or below 0: the step of ES-FL (+0.62 per cent after 219.5 M) does not appear; the bins after
  tau_rem 220 M lie in [+0.175, +0.250] per cent (panel c). Cause of the failure is in the prediction, not in
  the run: I built the band from FK's late bins (tau_rem 280-500 M) only; FK's own first bin is +0.050 per cent
  (n = 128, run D-20261125-115647-fd2f3f7), EG8's +6e-5 above it, the size of E3.
- E3 HOLDS. M_EG8 - M_FK at 399 common finder times on 20-219 M: median +8.6e-5 (5-95 per cent +6.1e-5 to
  +1.09e-4), band [2e-5, 1.2e-4]. Not predicted (panel d): the difference rises from +6e-5 at 20 M to +1.1e-4 at
  219 M, and between about 38 and 48 M it is -7e-5, a 10 M window in which FK's unpolished finder sat on the
  plateau 1.4e-4 higher (FK's plateaus, entry 1) while the horizon radius has its bump (panel a). [JUDGEMENT:
  the unpolished rule's offset is not one number; G3's members all polish.]
- E4 HOLDS. 515 of 515 searches after 2 M found; 112-145 flow iterations (median 126).
- E5 HOLDS. D2: 480 samples after 20 M, no violation. D3: 76168 removals, smallest margin +1.2e-4 (FK -1.4e-4).
- E6 HOLDS. Before t_rem = 219 M: 0 of 63344 removals precede their exact crossing, smallest lead +0.0715 M
  (FK +0.0715 M). Bin t_rem 240-250 M: 5.4 per cent precede (192 of 3528), FK 5.4 per cent.
- E7 HOLDS. 1.47 card-hours by sacct over the 11 jobs (`nrpic-run finish`), 1.49 by the segment stamps; band
  1.2-1.7. Ten of the eleven attempts were cut by preemption; the guard of core-v0.7 wrote restart files each time.
- E8 HOLDS. Chain DONE, last segment exit 0 at t = 260 M, no guard file.

What it means [JUDGEMENT]: on this deck core's `ah_exc_max_growth = 8` with `initial_radius_0 = 0.8` does what
finder_stop.md section 3 says: excision stays on past the radius where the default factor 4 stopped it, and the
mass against the exact solution keeps FK's level. G3 needs nothing from it (A1 chose FK's remedy, start radius
1.6 with factor 4), but either remedy is now tested to 260 M. Limits: one deck (M/8, N), to 260 M (the horizon
radius 3.49 M at the end; the guard 6.4 M was never approached), so the factor is tested against loss of
excision near 4 x 0.8 M, not near its own limit. Outcome posted to core (outbox, this session).
