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
