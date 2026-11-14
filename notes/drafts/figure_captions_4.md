# Caption and numbers for the figure of the cluster with two collapsing overdensities (to be edited by the writer)

State: both runs still running. Numbers below as of 2026-11-13 23:00 PST: the M/64 run
has reached t = 47.98 M, the M/128 run t = 38.33 M (of 100 M). Rerun both scripts
before using any number; the figure and every value here follow the data.

    python3 paper/scripts/make_data_overdensities.py   # reads the runs, writes paper/data/overdensities.npz, prints all numbers below
    python3 paper/scripts/fig_overdensities.py         # reads only the .npz, writes paper/figures/fig_overdensities.pdf and .png

Runs: M/64 is one run from t = 0 on a domain of +-80 M (eight levels, every fix in
place from the start). M/128 is the earlier run on +-256 M, stored in two directories
stitched at 6.31 M. The earlier M/64 run on +-256 M (three directories, to 27.6 M) is
not drawn; it is compared below.

fig_overdensities is a full-width figure (`figure*`, `width=\textwidth`, drawn at
7.0 in). The caption below has 678 visible characters by the checker's count, an
estimated 4.6 lines at full width (147 characters per line). Labels inside the panels
(envelope, A, B, separation, orbital phase, original, apparent horizon, the mesh
legend) explain the rest.

\caption{Each overdensity collapses to a black hole with about the apparent-horizon
mass of Ref.~\cite{Wu:2026nrpic} and soon accretes most of its overdensity; the two
black holes then spiral inward through the envelope. Top: macroparticles projected on
the orbital plane (envelope grey, overdensities of black holes A and B red and blue);
black circles, apparent horizons. Bottom left: separation $d$ and orbital phase
$\varphi$ of the black holes; dots, recorded positions, interpolated between. Bottom
middle: apparent-horizon masses. Bottom right: fraction of macroparticles remaining per
species. Thick solid, finest cells $\Delta x = M/64$; thin dashed, $M/128$; open
circles and ticks, values and times of Ref.~\cite{Wu:2026nrpic}.}

To adapt when the runs go further:
- The first sentence states what the data show at the last rerun. Once a common
  horizon is found, add the merger to it (time against the original's 64.16 M) and add
  to "Bottom right": "and spin $S/M_{\rm AH}^2$ of the common horizon (right axis)"
  (about 0.8 line; shorten elsewhere to stay within five lines).
- The figure chooses the particle panels itself: 0, 12 M, 50 M and the last snapshot;
  while the M/64 run has not passed 60 M the third panel is half-way between 12 M and
  the last snapshot (now 0, 12, 29.5, 47.5 M). The time axes end at the M/64 run's last
  time rounded up to 5 M (now 50 M). The original's values at 60, 64.16 and 100 M and
  its merger tick appear only once the run gets there.

## Where the positions come from (text and caption must not call them "trackers" throughout)

The tracker files hold only the latest job segment: every restart rewrites them. In the
M/64 run their first record is at 43.75 M, and in the M/128 run at 36.19 M. The horizon
shape files do not carry the centre either. Each block holds the time and 81
coefficients about the expansion centre, which is the tracker. The finder writes that
centre only to its verbose log, which is off (fastflow.cpp). The data script therefore
builds the positions from three sources:
1. Exact: the tracker positions stored in the header of every restart dump (the host
   code writes them after the Z4c output time, before the MeshBlock data). The header
   reader agrees with the tracker file to the last digit at the one dump that both
   cover (43.7539 M, cycle 11201). M/64 dumps: 0, 5.0, 8.867, 15.0, 16.281, 23.684,
   30.0, 30.703, 37.238, 43.754 M. M/128 dumps: 0, 5.0, 6.307, 12.219, 17.893, 23.559,
   29.889, 35.0, 36.188 M. Also exact: the current tracker files, sampled every 0.25 M
   (M/64 44.0 to 47.75 M, M/128 36.25 to 38.25 M).
2. Interpolated between the exact positions: a monotone cubic (PCHIP) in the midpoint,
   separation, orbital phase and z difference. The anchors are thinned to at least 1 M
   apart, because dense, lattice-rounded tracker samples next to a long gap make any
   cubic overshoot (a plain cubic in x, y, z missed the earlier run's separation at
   15 M by 0.08 M). There is no interpolation across a gap longer than 10 M, across a
   turn of the line A-B by more than 40 degrees, or once the separation is below 1 M
   (the line breaks there). Accuracy, from leaving out one dump at a time (so over
   gaps twice as long as the real ones):
   - M/64: 0.006 to 0.014 M per black hole, separation within 0.014 M;
   - M/128: 0.002 to 0.010 M, separation within 0.009 M.
3. Before collapse: the densest point of each overdensity in every snapshot (mean of
   the half of its macroparticles nearest to it, iterated), as the coordinator asked
   before the first horizon. Before collapse the trackers lag the overdensities by
   about 0.1 M. Accuracy against the exact positions:
   - t = 0: 0.061 M per black hole, separation 0.077 M short of the exact 6.000 M
     (sampling noise of the Gaussian overdensity, mirrored between A and B);
   - 5 M: 0.06 M (here the tracker lag dominates);
   - after collapse (15 M): 0.08 to 0.11 M.
   The record uses it up to the first horizon (M/64: 10.5 M) or up to the first exact
   position after 7 M if that is later (M/128: 12.22 M).
Continuity where the sources meet:
- M/64 at 10.5 M: A moves by 0.012 M, B by 0.025 M; the separation jumps by +0.024 M
  and the phase by +0.15 degrees.
- M/128 at 12.22 M: 0.034 and 0.039 M; separation +0.063 M, phase +0.27 degrees.
The horizon circles in the particle panels sit at these positions. At t = 12 M
(interpolated between the dumps at 8.87 and 15.0 M) they are 0.04 M from the densest
point of the remaining overdensity particles.
Recommendation for the run chain: copy jeans.co_0.txt and jeans.co_1.txt before each
restart into <run>/co_archive/ (any name containing co_0 or co_1). The data script reads
such copies, and the record near the merger then becomes exact instead of interpolated
across 5 to 7 M.

## What the text must say next to the figure

- The finder reports the individual horizons from 10.5 M (M/64) and 9.52 M (M/128),
  later than the original's first horizons (8.475 and 8.525 M, ticks in the middle
  panel). The Misner-Sharp result of the brief (first trapped surface at 8.66 M at
  M/128) is the formation time to quote.
- Particles are removed by the lapse rule before the finder sees a horizon: from 9.11 M
  (M/64) and 8.13 M (M/128).
- A and B are mirror images; their masses agree to 1 percent on both meshes.
- After formation the black holes spiral inward. M/64: 6.05 M at 10 M, 5.36 M at 30 M,
  4.11 M at 40 M, 2.54 M at 47.75 M. The M/128 run spirals in faster (5.15 M at 30 M
  against 5.36 M) and its black holes are lighter (0.144 against 0.154 M at 30 M).
- The envelope is depleted slowly: 95 percent of its macroparticles remain at 40 M
  (M/64).

## Numbers (from the runs; t, lengths in M, masses in units of the total ADM mass M)

Setup (for the appendix table):
- Envelope: 6000 macroparticles, rest mass 0.78608. Each overdensity: 2000
  macroparticles, rest mass 0.13207, centred at x = -3.00 (A, species 1) and +3.00 (B,
  species 2). Total rest mass 1.05022.
- M/64: domain +-80 M, eight levels, finest cells M/64 within 0.2 M of each tracker,
  block limit 2280; lapse removal at 0.05 and removal inside 0.8 of the smallest radius
  of a found horizon from the start. Time step 0.00390625 M.
- M/128: domain +-256 M, finest cells M/128 within 0.125 M of each tracker (from
  6.31 M); lapse removal at 0.05 and removal inside found horizons from 6.31 M (lapse
  guard 0.02 before, when nothing was removed). Time step 0.001953125 M.
- Horizon searches every 16 steps (0.0625 M at M/64, 0.03125 M at M/128) from 5 M; the
  common horizon is searched from 20 M once the trackers are within 1 M.

First found apparent horizons:
| mesh | A: t, M_AH | B: t, M_AH | original |
|---|---|---|---|
| M/64 | 10.5, 0.09763 | 10.5625, 0.09923 | first horizons at 8.475 and 8.525 |
| M/128 | 9.609, 0.08012 | 9.516, 0.07817 | |

| t | M/64 d | M/64 phase | M/64 M_A, M_B | M/128 d | M/128 phase | M/128 M_A, M_B | original M_A, M_B |
|---|---|---|---|---|---|---|---|
| 10 | 6.049 | 18.5 deg | not yet found | 5.988 | 18.4 deg | 0.08553, 0.08556 | 0.0880, 0.0877 |
| 20 | 5.955 | 32.4 deg | 0.14475, 0.14415 | 5.748 | 34.9 deg | 0.13676, 0.13754 | |
| 30 | 5.360 | 45.6 deg | 0.15376, 0.15268 | 5.147 | 52.3 deg | 0.14386, 0.14483 | |
| 40 | 4.110 | 61.0 deg | 0.16257, 0.16223 | not reached | | | |
| last | 2.538 (47.75) | 79.6 deg | 0.17232, 0.17128 (47.94) | 4.266 (38.25) | 68.0 deg | 0.15044, 0.15172 (38.30) | 0.1742, 0.1761 at 60 |
- Completed orbits: none (0.221 orbits by 47.75 M at M/64, 0.189 by 38.25 M at M/128).
- Separation below 1 M: not yet. Common horizon: not searched yet (needs a separation
  below 1 M); no time, mass or spin to quote.

Macroparticles remaining (envelope, A, B; fractions of 6000, 2000, 2000):
| t | M/64 | M/128 |
|---|---|---|
| 10 | 5995, 843, 841 (0.999, 0.421, 0.420) | 5994, 753, 756 (0.999, 0.377, 0.378) |
| 20 | 5911, 9, 7 (0.985, 0.004, 0.004) | 5919, 8, 8 (0.987, 0.004, 0.004) |
| 30 | 5811, 0, 0 (0.969) | 5822, 0, 0 (0.970) |
| 40 | 5688, 0, 0 (0.948) | not reached |
- First removal: 9.113 M (M/64), 8.135 M (M/128).
- Largest MeshBlock count: M/64 1980 (at 44.58 M; limit 2280); M/128 2164 (5.91 M).
- Smallest lapse now: 0.027 (M/64), 0.015 (M/128).

Spins of the individual black holes (finder): S/M_AH^2 median 0.033 (A) and 0.022 (B)
at M/64, 0.027 and 0.011 at M/128; the original's "of order 1e-5" is far smaller (S or
S/M^2 is to be checked in its text). Not a measured spin at this resolution.

## The two M/64 domains (+-80 M now, +-256 M before; same particles, same mesh at the black holes)

| t | M_A new/old (diff) | M_B new/old (diff) | separation new/old (diff) |
|---|---|---|---|
| 10.5 | 0.09763/0.09785 (-0.00022) | first found at 10.5625 (0.09923); old 0.09721 | 6.048/6.094 (-0.047) |
| 15 | 0.13592/0.13597 (-0.00005) | 0.13607/0.13625 (-0.00018) | 6.059/5.989 (+0.070) |
| 20 | 0.14475/0.14453 (+0.00022) | 0.14415/0.14434 (-0.00019) | 5.955/5.853 (+0.103) |
| 25 | 0.14978/0.14918 (+0.00060) | 0.14750/0.14782 (-0.00032) | 5.739/5.564 (+0.175) |
| 27 | 0.15075/0.15031 (+0.00044) | 0.14978/0.15032 (-0.00054) | 5.596/5.427 (+0.168) |
| 28 | 0.15153 | 0.15079 | 5.516 (old ends at 27.5 M with 5.392) |
- Prediction logged before the run: "masses agree to 0.002 M" holds (largest
  difference 0.0006 M). "Separation at 28 M is 5.3 M" does not: the new run has 5.52 M
  at 28 M; the old run had 5.39 M at 27.5 M. On the smaller domain the black holes
  spiral in more slowly up to 27 M (0.07 to 0.18 M wider from 15 M on).
- The old run's positions come from the same procedure. Its interpolation between its
  dumps (13.0, 19.45, 26.15 M) was checked at 15 M against its tracker file, read
  before it was rewritten: 5.988 against 6.003 M.

## Checks done, and what looks wrong

Spot checks against the raw files (awk, a separate struct reader, the restart headers;
all equal to the values in the .npz):
- Separation and phase at 30 M from the dump header: 5.3596 M and 45.59 degrees; the
  record has 5.3596 and 45.59 (an exact point).
- Horizon positions in the 47.5 M panel: equal to the tracker files.
- Masses: A at 20 M 0.1447543; B at 40 M 0.1622270; old run A at 25 M 0.1491846; M/128
  B at 29.984 M 0.1448310.
- Species counts: 5911/9/7 at 20 M and 5688/0/0 at 40 M (M/64); 5822/0/0 at 30 M
  (M/128).
- Across every restart of the M/64 run (the dump times above) the particle number,
  smallest lapse, block count and rest mass are continuous; same for M/128, including
  the change of directory at 6.31 M.

Looks wrong, or needs saying:
1. The M/64 black holes drift out of the orbital plane, both in +z. In the new run they
   are at z = +0.62 and +0.57 M by 47.75 M; in the old run (+-256 M) at +0.34 and
   +0.32 M by 27.5 M. The macroparticles' mass-weighted mean u_z grows from 0 to +0.015
   by 48 M, and the envelope centroid moves from z = +0.009 to +0.097 M. The M/128
   run, with the same particles, stays within 0.06 M of the plane (mean u_z below
   0.002). Cause not determined; it is a property of the M/64 mesh, not of the domain.
2. The tracker files are rewritten at every restart (see "Where the positions come
   from"). Near the merger the dumps are 5 to 7 M apart, while the orbit then turns
   quickly, so the record will break there unless the tracker files are archived
   before each restart.
3. The finder re-writes its previous result after a failed search (rows identical in
   all ten columns): 3 and 2 times at M/64, 5 and 6 at M/128. These are counted as not
   found; there is no other stretch longer than 0.5 M without a horizon after the first
   detection.
4. After formation each horizon's centre lies within 0.011 M of its tracker (M/64) and
   0.006 M (M/128): no tracker leaves its black hole.
5. The M/64 and M/128 runs differ by more than the M/64 domain change: the M/128
   black holes are 0.01 M (6 percent) lighter from 15 M on and spiral in faster.

## Against notes/results_brief_selfgravity.md, part D

- Item 2, M/64 masses ("0.0885 and 0.0929 M at t = 10.1 and 10.25 M"): from a run that
  is no longer the M/64 source. The figure's M/64 run first finds A at 10.5 M
  (0.0976 M) and B at 10.5625 M (0.0992 M).
- Item 2, "0.128 M each at t = 12.9 M (M/64)": the new run has 0.1281 (A) and 0.1282 M
  (B) at 12.94 M; still holds.
- Item 1, "nothing removed yet" at the first trapped surface (8.66 M, M/128): holds
  only for the run that measured it. The M/128 run in the figure has removed 993
  macroparticles by 8.66 M.
- Setup paragraph: the M/64 run now uses a domain of +-80 M with eight levels and a
  finest region of 0.2 M about each tracker; the M/128 run keeps +-256 M.
- Item 4 (inspiral, merger): the black holes do spiral in (6.05 to 2.54 M from 10 to
  47.75 M at M/64); no merger yet.
