# Caption and numbers for the figure of the cluster with two collapsing overdensities (to be edited by the writer)

State: both runs still running. Numbers below as of 2026-11-13 19:10 PST: the M/64
evolution has reached t = 15.94 M, the M/128 evolution t = 10.77 M (of 100 M). Rerun
both scripts before using any number; the figure and every value here follow the data.

    python3 paper/scripts/make_data_overdensities.py   # reads the runs, writes paper/data/overdensities.npz, prints all numbers below
    python3 paper/scripts/fig_overdensities.py         # reads only the .npz, writes paper/figures/fig_overdensities.pdf and .png

fig_overdensities is a full-width figure (`figure*`, `width=\textwidth`, drawn at
7.0 in). The caption below has 696 visible characters by the checker's count, an
estimated 4.7 lines at full width (147 characters per line). Labels inside the panels
(envelope, A, B, separation, orbital phase, original, apparent horizon, the mesh
legend) explain the rest.

\caption{Each overdensity collapses to a black hole with about the apparent-horizon
mass of Ref.~\cite{Wu:2026nrpic}, which then accretes most of the remaining
overdensity while the envelope is barely touched; so far the two black holes keep their
separation. Top: macroparticles projected on the orbital plane (envelope grey,
overdensities of black holes A and B red and blue); black circles, apparent horizons at
the tracker positions. Bottom left: separation $d$ of the two trackers and orbital phase
$\varphi$. Bottom middle: apparent-horizon masses. Bottom right: fraction of
macroparticles remaining per species. Thick solid, finest cells $\Delta x = M/64$; thin
dashed, $M/128$; open circles and ticks, values and times of Ref.~\cite{Wu:2026nrpic}.}

To adapt when the runs go further:
- The first sentence states what the data show at the time of the last rerun. Once a
  common horizon is found, replace its last clause by the observation (for example
  "the two black holes spiral together and merge at a later/earlier time than in
  Ref.~..., and the remnant keeps accreting the envelope") and add to "Bottom right":
  "and spin $S/M_{\rm AH}^2$ of the common horizon (right axis)" (118 characters;
  shorten elsewhere to stay within five lines).
- The figure chooses the particle panels itself: 0, 12 M, 50 M and the last snapshot;
  while the M/64 run has not passed 60 M the third panel is half-way between 12 M and
  the last snapshot (now 0, 12, 13.5, 15.5 M). The time axes end at the M/64 run's last
  time rounded up to 5 M (now 20 M), so the original's values at 60, 64.16 and 100 M
  and its merger tick appear only once the run gets there.

## What the text must say next to the figure

- The M/64 evolution is one physical run stored in three directories (restarts with
  changed settings), stitched at 10.0 and 13.0 M; the M/128 evolution two, stitched at
  6.31 M. No quantity jumps at the stitching times (see the checks below).
- The finder reports the individual horizons only from 10.31 M (M/64) and 9.52 M
  (M/128) on, later than the original's first horizons (8.475 and 8.525 M, ticks in the
  middle panel). The brief's Misner-Sharp result (first trapped surface at 8.66 M at
  M/128) is the formation time to quote; the finder's first success is not.
- Particles of the overdensities are removed by the lapse rule before the finder sees a
  horizon: from 8.13 M at M/128 and 9.11 M at M/64 (bottom right: the dashed curves
  drop first). This is what the earlier drop of the M/128 curves shows.
- The two black holes are mirror images: masses of A and B agree to 1 percent on both
  meshes, and so do their particle counts.
- The orbit is slow: the line from A to B has turned by 27 degrees by 15.9 M (0.076
  orbits), about 1.5 degrees per M after 8 M, which is one orbit per about 240 M if it
  stayed so. The separation stays between 5.97 and 6.10 M after 8 M. The original
  merges at 64.16 M.
- The step of the orbital phase near 5.8 M is the trackers catching up with the
  overdensities before collapse (see "looks wrong" below), not a feature of the orbit.

## Numbers (from the runs; t, lengths in M, masses in units of the total ADM mass M)

Setup (for the appendix table):
- Envelope: 6000 macroparticles, rest mass 0.78608. Each overdensity: 2000
  macroparticles, rest mass 0.13207, centred at x = -3.00 (A, species 1) and +3.00 (B,
  species 2). Total rest mass 1.05022.
- M/64: finest cells M/64 within a region about each tracker of radius 0.3 M up to
  13.0 M and 0.2 M from 13.0 M on (changed at the last restart, see below); block limit
  2100, from 13.0 M on 2280. Lapse removal at 0.05 throughout; removal inside 0.8 of the
  smallest radius of a found horizon from 10.0 M on. Time step 0.00390625 M.
- M/128: finest cells M/128 within 0.125 M of each tracker (from 6.31 M; mesh of the
  earlier run before that); lapse removal at 0.05 and removal inside found horizons
  from 6.31 M (lapse guard 0.02 before 6.31 M, where nothing was removed). Time step
  0.001953125 M.
- Horizon searches every 16 steps: 0.0625 M (M/64), 0.03125 M (M/128), from 5 M; the
  common horizon is searched from 20 M once the trackers are within 1 M.

First found apparent horizons (finder):
| mesh | A: t, M_AH | B: t, M_AH | original |
|---|---|---|---|
| M/64 | 10.375, 0.09461 | 10.3125, 0.09318 | first horizons at 8.475 and 8.525 |
| M/128 | 9.609, 0.08012 | 9.516, 0.07817 | |

Apparent-horizon masses at fixed times (nearest found search within 0.25 M):
| t | M/64 A | M/64 B | M/128 A | M/128 B | original A, B |
|---|---|---|---|---|---|
| 10 | none found yet (first at 10.31) | none | 0.08553 | 0.08556 | 0.0880, 0.0877 |
| 15 | 0.13597 | 0.13625 | not reached | not reached | |
| 20, 30, ... | not reached | | | | 0.1742, 0.1761 at 60 |
| last | 0.13735 (15.875) | 0.13831 (15.875) | 0.10046 (10.766) | 0.10072 (10.766) | |
Mean coordinate radius of the horizons: 0.058 M at first detection (M/64), 0.102 M at
15 M; 0.053 M at 10 M (M/128).

Separation of the trackers and orbital phase (angle of the line from A to B):
| t | M/64 d | M/64 phase | M/128 d | M/128 phase |
|---|---|---|---|---|
| 0 | 5.969 | 0 | (no tracker record before 6.31) | |
| 8.5 | 6.038 | 16.2 deg | 6.013 | 16.2 deg |
| 10 | 6.078 | 18.9 deg | 6.001 | 18.6 deg |
| 15 | 6.003 | 26.1 deg | not reached | |
| last | 5.968 (15.93) | 27.4 deg | 5.985 (10.77) | 19.8 deg |
- Completed orbits: none (0.076 orbits at 15.93 M, M/64; 0.055 at 10.77 M, M/128).
- Separation below 1 M: not yet. Common horizon: not searched yet (needs 20 M and a
  separation below 1 M); no time, mass or spin to quote.

Macroparticles remaining (envelope, A, B; fractions of 6000, 2000, 2000):
| t | M/64 | M/128 |
|---|---|---|
| 8.5 | 6000, 2000, 2000 | 5999, 1551, 1554 (1.000, 0.776, 0.777) |
| 10 | 5995, 836, 837 (0.999, 0.418, 0.419) | 5994, 753, 756 (0.999, 0.377, 0.378) |
| 15 | 5962, 86, 88 (0.994, 0.043, 0.044) | not reached |
| last snapshot | 15.5: 5958, 71, 70 (0.993, 0.036, 0.035) | 10.5: 5992, 599, 593 (0.999, 0.300, 0.297) |
- First removal: 9.109 M (M/64; 1680 removed by 9.18 M in one burst at the lapse
  threshold), 8.135 M (M/128; 896 removed by 8.5 M, 993 by 8.66 M).
- Removed rest mass so far: 0.26 of 1.05 (M/64, 15.6 M), 0.19 (M/128, 10.6 M).

Spins of the individual black holes (finder): S between 7e-5 and 4e-4 M^2, S/M_AH^2
between 0.007 and 0.031 (median 0.014 for A and 0.017 for B at M/64; 0.010 and 0.015 at M/128).
The original's "of order 1e-5" is 10 times smaller than our S and 1000 times smaller
than our S/M_AH^2; which of the two the original quotes is to be checked against its
text. Our value is at the level the finder resolves on horizons of 3 to 7 cells' radius;
it should not be presented as a measured spin.

MeshBlocks, largest count: M/64 1828 (at 2.35 M; 1779 in 10-13 M; 1814 so far after
13 M, at 15.55 M). M/128 2164 (at 5.91 M; 2108 so far after 6.31 M).

## Checks done, and what looks wrong

Spot checks against the raw files (independent awk and struct readers; all equal to the
values in the .npz to the last digit):
- Particle panels: species counts 5987/329/320 at t = 12 M and 5962/86/88 at 15 M;
  horizon radius of B drawn at 12 M 0.083745 M (finder file: 8.374475e-02).
- Separation: 6.0777 M and 18.90 deg at 10.0 M (trackers (-2.8828, -0.9766, 0.0234)
  and (2.8672, 0.9922, 0.0234)); 6.0027 M and 26.10 deg at 15.0 M.
- Masses: B first found at 10.3125 M with 0.0931809; A at 15.0 M 0.1359691; B at 12 M
  0.1205694.
- Fractions: 5995/836/837 at 10 M (M/64), 5998/1207/1214 at 9 M (M/128).

Stitching:
- 10.0 M: the directory after the restart starts from a dump of a sibling run that
  repeated the first directory from 5 M; at 10.0 M the two are identical (particle
  number 7668, trackers to the last digit, smallest lapse 0.0419, 1716 blocks). No jump.
- 13.0 M: particle number 6407 on both sides, smallest lapse 0.0540/0.0544, 1779
  blocks, separation 6.0340 on both sides, masses 0.12811/0.12845 (A) and
  0.12808/0.12867 (B) from 12.9375 to 13.0 M, as the growth rate gives. No jump.
- 6.31 M (M/128): particle number 10000, lapse 0.6183/0.6179, 2108 blocks. No jump.

Looks wrong, or needs saying:
1. The M/64 chain failed at t = 19.1 M: the refinement asked for 2388 MeshBlocks
   against a limit of 2100. It was restarted from the dump at 13.0 M with a smaller
   finest region about each tracker (radius 0.2 M instead of 0.3 M) and a limit of 2280.
   The records of the failed segment (13.0 to 19.1 M) are superseded and not used.
   For reference, that segment had reached masses 0.14371 (A) and 0.14330 (B) at
   19.06 M, 1863 blocks at most (14.08 M), 5946 particles at 19.1 M; at 15 M it agrees
   with the new segment (A 0.13592 against 0.13597, 6136 particles in both). The
   tracker files were rewritten at the restart, so the old tracker record from 13 to
   19.1 M is gone. Caution for later: the horizon's mean coordinate radius is 0.10 M at
   15 M and grows with the mass; the finest region now reaches only 0.2 M from the
   tracker.
2. The finder re-writes its previous result when a search fails: rows identical in all
   ten columns to the previous found row. Seen 1 time for A and 6 times for B at M/64
   (all between 10.4 and 11.4 M), 5 and 6 times at M/128 (9.5 to 9.8 M). These are
   counted as not found (the script flags them as stale). After its first detection the
   finder otherwise succeeds in every search; no stretch longer than 0.5 M without a
   horizon.
3. Before collapse the trackers lag the overdensities: 0.09 to 0.19 M from the densest
   point of their overdensity between 0.5 and 5.5 M, catching up near 5.8 M (the step
   of about 2 degrees in the orbital phase) and staying within 0.03 M of it from 7 M on
   (within 0.013 M from 7 to 9.5 M). After
   formation each horizon's centre is within 0.011 M of its tracker (at most 0.18 of
   its mean radius) at M/64 and within 0.006 M at M/128: no tracker leaves its black
   hole.
4. The tracker files of the first M/128 directory begin at 12.30 M (rewritten by one of
   its restarts), so there is no M/128 tracker record before 6.31 M; the M/128
   separation begins there.
5. Tracker positions are written on a lattice (multiples of 1/128 M at M/64, 1/256 M
   at M/128), so the separation and phase move in steps of that size.

## Against notes/results_brief_selfgravity.md, part D

- Item 2, M/64 masses: the brief's "0.0885 and 0.0929 M at t = 10.1 and 10.25 M" come
  from the sibling run that the 10.0 M restart was taken from, not from the stitched
  M/64 record. In the stitched record (the figure) the finder first finds B at
  10.3125 M (0.0932 M) and A at 10.375 M (0.0946 M). The slices are identical at 10.0 M;
  the finder's first successes differ after the restart. Text and table should quote
  the figure's values or name the run they come from.
- Item 1, "first trapped surface ... at 8.66 M with a mass of 0.05 M, nothing removed
  yet": "nothing removed" holds for the run that measured it (lapse removal off), not
  for the M/128 record in this figure, which uses lapse removal at 0.05 and has removed
  993 macroparticles (about a quarter of each overdensity) by 8.66 M, from 8.13 M on.
- Item 2, M/128 values (0.078 and 0.080 M at 9.5 and 9.6 M, 0.083 M at 9.8 M) and
  "0.128 M each at t = 12.9 M (M/64)": confirmed (0.07817 at 9.516, 0.08012 at 9.609,
  0.0827/0.0830 at 9.797; 0.12811/0.12808 at 12.9375).
- Setup paragraph: the M/64 refinement region about each tracker changed from 0.3 M to
  0.2 M at 13.0 M (restart after the block-limit failure at 19.1 M); the brief does not
  say so.
- Item 4 (inspiral, merger): still no outcome to state. So far: no inspiral by 15.9 M
  (separation 5.97 to 6.10 M after 8 M), 0.076 orbits.
