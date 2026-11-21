# binary_conv journal (helper of F-hills, wave 3 batch 3)

Question: does P1's binary (q = 4 passage, members m = 0.125 at m/8; run
F-20261119-150017-b45ec5f) merge at t = 48.8 M because of the members' resolution? Which member
resolution lets the binary survive the 100 M the next passage (P1b) needs? Predictions before
each test, outcomes after, failed ones included. Labels [VERIFIED], [BACKGROUND], [JUDGEMENT],
[TO VERIFY].

## 2026-11-21 BC-0. Design and cost (written before any card run)

Set-up [JUDGEMENT on each choice]:
- The binary of P1 alone: P1's `<problem>` without comp2 (the heavy hole), so the same bare
  masses, positions, Bowen-York momenta, corrections and gauge (constant shift_eta = 2, so
  eta m = 0.25 at a member). The binary keeps P1's centre-of-mass momentum, |P| = 0.0561, i.e.
  it moves at about 0.22 c across the grid as in P1 (members' grid speeds 0.23 and 0.27):
  "same separation and momenta" taken literally, because a resolution loss of the members'
  grid motion is the suspected cause and a rest-frame binary would test something else.
- Mesh: P1's cells (root cells 8 M; member level 9 at m/8) on +-128 instead of +-256; root
  32^3, 48^3, 32^3 for m/8 (R8, 10 levels), m/12 (R12, 10 levels, every cell 2/3) and m/16
  (R16n, 11 levels, members at level 10, wave zone and coarse levels as R8): the triple of
  g2mesh (JOURNAL G2M-1) on half the domain. The tree model (g2mesh `tree3.py`, exact against
  `athena -m` and P1's restart trees) along the Newtonian tracks gives 9-12 percent fewer
  blocks on +-128 (R8 mean 1234 against 1360 over t = 0-25; R12 1730 against 1968; R16n 1694
  against 1820). Boundary signals: the binary sits within about 25-35 M of the centre; a signal
  leaving it at t = 0 at the gauge speed sqrt(2) reaches the face and returns after about
  2 x (128 - 30)/sqrt(2) = 139 M, so nothing from the boundary reaches it before t = 100 M.
- Executable: release core-v0.5 card build, byte copy `scratch/F-hills/tmp/binary_conv/exe/
  bc-ak05-gpu` (sha256 2512c8d5...61ea4, equal to `.work/build_gpu_v05/src/athena`), behind
  `scripts/athena_keep_trackers_bc.sh` (keeps the tracker files across restarts; process name
  not `athena`, so an outside `pkill -x athena` misses it, p1 JOURNAL entry 0).

Cost [arithmetic from the model, rate 2000 MeshBlock-cycles/s from P1's segments 1963-2242;
one global step dt = 0.25 h_finest, so 256, 384, 512 cycles per M]: the binary alone has
nearly P1's tree (start 1170 / 1784 / 1744 blocks on +-128 for R8 / R12 / R16n; the heavy hole's
nest was only about 400 of P1's 1716). To 100 M this costs about 4.4 (R8), 9.2 (R12) and
12.1 (R16n) card-hours, 26 in all, against the package's cap of 6. So the package cannot run
the three to 100 M. What 6 card-hours buy: one 50-minute segment advances R8 by about 17-20 M,
R12 by about 8 M and R16n by about 6.3-7 M.

Plan within the cap [JUDGEMENT]: R8 1 segment (to about 17 M), R12 2 segments (about 16 M),
R16n 3 segments (about 19 M): 6 segments, about 5.0 card-hours measured (0.835 per segment),
1 card-hour kept for one more R8 segment if the first window does not decide. Order (two card
jobs of the owner at a time): R16n and R8 first (decision 0021 item 7 names m/8 and m/16), R12
when R8 is done. The verdict on 100 M is then an extrapolation from the common window
0-15 M, stated as such.

## 2026-11-21 BC-1. Prediction for the three runs (written before submission)

References [arithmetic; formulas BACKGROUND]: Newtonian elements of the input (v = p/m, bare
masses): coordinate separation 4.952, a = 5.111, e = 0.033, period 145.2 M, orbital angular
frequency 0.0433/M. Quadrupole (Peters) inspiral time (5/256) a^4/(m1 m2 (m1+m2)) / F(e):
3388 M with the bare masses, 3012 M with 0.130, 2574 M with 0.137 (P1's last member horizon
masses 0.137-0.139). So physically the binary loses about 0.01 M of its separation in 20 M
(a(t) = a0 (1 - t/T)^(1/4)) and 0.05 M in 100 M; the eccentric oscillation is +-0.17 M over
145 M. The 1PN orbit (eih) and the quadrupole decay are computed in the analysis run (BC-2).
P1 at m/8 [VERIFIED, trackers of run F-20261119-150017-b45ec5f read with nr_first/nrread]:
separation 4.952 (t = 0), 4.912 (5), 4.780 (10), 4.576 (15), 4.286 (20), 3.356 (30), 1.841 (40),
0.189 (48); coordinate phase 0.273 rad at 10 M and 0.586 at 20 M against Newton's 0.43 and 0.87.

What a resolution-driven merger looks like: the separation's decay over a fixed window shrinks
steeply with the cell size (by (h2/h1)^p for a scheme of order p) and the merger time grows as
h^-p; a physical (or gauge-only, continuum) effect gives the same curve at every resolution.

Predictions:
1. R8 alone follows P1's separation within 0.10 M to the end of its window (about 17 M):
   s(10) = 4.73-4.83, s(15) = 4.53-4.63 [JUDGEMENT: the heavy hole's tidal acceleration at
   31.75 M is about 2 M s / r^3 = 3e-4, 3 percent of the binary's own 1e-2, worth about
   0.04 M of separation in 17 M]. Refuted by a difference above 0.10 M at any t <= 17: then the
   third body (its gauge or its field) is part of P1's merger.
2. The decay is resolution driven: Delta s(15) = s(0) - s(15) falls with resolution, R16n's at
   most half of R8's (R8 about 0.38 M), R12 between the two [JUDGEMENT: p >= 1 for any part of
   a fourth-order scheme that converges]. Refuted if R16n's Delta s(15) exceeds 0.6 of R8's
   (then resolution is not the main cause at these cells).
3. Order: from Delta s at t = 10 and 15 with h = 1, 2/3, 1/2 (times m/8), p between 1 and 4
   [JUDGEMENT]. Refuted by p outside 0.5-5 or by a non-monotone sequence.
4. Horizons: both member finders find horizons in every search after the first few M; member
   masses at t = 5 M between 0.128 and 0.140 at all three resolutions; mass growth over
   5-15 M at R16n at most half of R8's (P1: 1.6-2.0e-4 per member mass per M before the merger).
   Refuted by a missed horizon after 5 M or by a growth at R16n above 0.6 of R8's.
5. No non-finite value (guard of core-v0.5 silent, exit 0 at the wall clock), history Volume
   constant.
6. Cost: start trees 1170 (R8), 1784 (R12), 1744 (R16n) +-2 percent (model; the restart headers
   and the log decide), rates 1800-2300 MeshBlock-cycles/s, advance per 50-minute segment
   15-21 M (R8), 7-9.5 M (R12), 5.5-7.5 M (R16n). Refuted outside these ranges.
7. Extrapolated verdict [JUDGEMENT, to be decided by 2 and 3]: if p is about 2, the merger time
   scales as h^-2: about 49 M at m/8, 110 M at m/12, 195 M at m/16, so m/16 survives 100 M and
   m/12 is marginal; if p is about 1, 73 M and 98 M, and m/16 is marginal.
