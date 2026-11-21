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

## 2026-11-21 BC-0 / BC-1 item 6, outcome of the mesh check (run F-20261121-130405-77ad9f6)

`athena -m` of release core-v0.5 (processor build) gives start trees of 1170 (bin_m8), 1784
(bin_m12) and 1744 (bin_m16) MeshBlocks, equal to the tree model in every case [VERIFIED,
`mesh_m*/athena_m.log` and `tree_cost_m*.json` of the run]. Model along the Newtonian tracks to
100 M (sampled every 0.5 M): mean 1262 / 1704 / 1725, maximum 1632 / 1896 / 2024, all below the
slots of the inputs (2000 / 2400 / 2400). Card cost to 100 M at 2000 MeshBlock-cycles/s: 4.5,
9.1, 12.3 card-hours (26 in all). Item 6 (start trees) MET; rates and advance per segment wait
for the cards.

P1b candidates (run F-20261121-131003-75a2b29, `athena -m`): `inputs/p1b_R16n.athinput` starts
with 2514 MeshBlocks (g2mesh's model and card test: 2514), `p1b_R12.athinput` with 2414.

## 2026-11-21 BC-2, outcome: references (run F-20261121-130646-56612a0; figure read)

`scripts/refs.py` from bin_m8's punctures; figure `fig_refs.png` read [VERIFIED for the run]:
- Newton (v = P/m): separation 4.943-5.279 M over 0-100 M (e = 0.033 ellipse), 4.944 at 10 M,
  4.953 at 15 M, 4.969 at 20 M; orbital phase 0.462 rad at 10 M, 0.922 at 20 M, 4.30 at 100 M.
- EIH with P read as canonical 1PN momenta: 4.946 (10), 4.941 (15), 4.930 (20), minimum 4.375
  at about 73 M; phase 0.386 (10), 0.773 (20), 4.32 (100).
- EIH with v = P/m: widens to 9.67 M by 100 M. With the binary moving at 0.22 c, reading the
  Bowen-York momenta as velocities is not a consistent 1PN state (its v^2 terms are as large as
  the binding); the canonical reading is the consistent one [JUDGEMENT]. Kept on the figure as
  the spread of the 1PN start-state ambiguity.
- Newton plus the 2.5PN dissipative Hamiltonian (1805.07240 Eq. H2.5PN): Iddd self-test 5e-6
  (finite difference); the binary reaches a separation of 2 (m1 + m2) at T = 3400 M, against
  Peters' 3388 M for the same bare masses (0.4 percent) and 3012 / 2574 M for masses 0.130 /
  0.137. Over 0-20 M the radiation changes the separation by less than 0.003 M (Newton
  4.969 against 4.966 at 20 M).
So every reference keeps the separation within 4.93-4.97 M to t = 20 M, while P1 (m/8) was at
4.286 at 20 M; the physical inspiral time is about 2600-3400 M.

## 2026-11-21 BC-3, outcome of the first card segments (intermediate; analysis run F-20261121-153844-fbc75ac)

Runs: R8 alone F-20261121-130358-6cf186a (one segment, Slurm 4797, t = 0-20.94 M, complete as
planned; its chain resubmitted itself past MAX_SEGMENTS = 1 as job 4808, which I cancelled with
`submit_chain.sh --stop` before it started, so the run is closed at its single segment); R16n alone
F-20261121-130351-04074e1 (segment 1 of 3, Slurm 4796, t = 0-7.74 M; segment 2 queued as Slurm
4807); R12 F-20261121-153707-1eaa5d4 submitted 07:37 PST (Slurm 4809, queued). Analysis
`scripts/analyze.py` (first pass F-20261121-153759-af77173, second pass with the deviations from
the references F-20261121-153844-fbc75ac); figures `fig_orbit_conv_intermediate.png`,
`fig_horizons_H_intermediate.png` read. All numbers below are from these runs [VERIFIED].

Separation s(t) (coordinate distance of the trackers), M:

| t | Newton | EIH canonical | P1 (m/8, 3 holes) | R8 alone (m/8) | R16n alone (m/16) |
|---|---|---|---|---|---|
| 0 | 4.9519 | 4.9519 | 4.9519 | 4.9519 | 4.9519 |
| 2.5 | 4.9469 | 4.9503 | 4.9421 | 4.9478 | 4.9502 |
| 5 | 4.9439 | 4.9490 | 4.9115 | 4.9301 | 4.9548 |
| 7.5 | 4.9430 | 4.9478 | 4.8539 | 4.8863 | 4.9477 |
| 10 | 4.9442 | 4.9464 | 4.7798 | 4.8257 | - |
| 15 | 4.9528 | 4.9412 | 4.5760 | 4.6465 | - |
| 20 | 4.9693 | 4.9302 | 4.2855 | 4.3753 | - |

- The m/16 binary follows the EIH (canonical) separation to 1e-4 M at t = 2.5 and 7.5 M; between
  them it wobbles by at most 0.006 M (4.9548 at 5 M, above both references), a coordinate
  oscillation of the same size as the Newton-EIH spread (0.005 M). Its deviation from EIH stays
  within +-0.006 M over 0-7.74 M.
- The m/8 binary alone decays like P1 from t of about 3 M on, with |Delta s| growing as t^2
  (figure, lower left): 0.066 M at 7.5 M, 0.305 at 15, 0.577 at 20; minimum 4.3125 at 20.94 M.
  It decays 0.67-0.87 times as fast as P1 (Delta s ratio 0.67 at 7.5 M, 0.84 at 15, 0.87 at
  20). Time stretch against P1 (s_8(t) ~ s_P1(lambda t)): lambda = 0.914 (rms 0.014 M over
  0.5-20.9 M), so the m/8 binary alone would merge at about 48.8/0.914 = 53 M if the stretch
  held to the merger [JUDGEMENT].
- At t = 7.5 M the m/8 binary is 0.0615 M inside EIH, the m/16 binary 0.0001 M; with the wobble
  as the error of the m/16 value, the ratio is at most 0.006/0.0615 = 0.1, i.e. the m/8 error
  falls by at least 10 when the cells are halved: an order p >= 3.3 (two-point; the Delta s ratio
  gives 3.96 at 7.5 M) [arithmetic on VERIFIED numbers; no three-point order until R12 lands].
- Phase (rad) at 7.5 M: Newton 0.346, EIH 0.289 (linear interpolation in `refs.json` of run
  F-20261121-130646-56612a0), P1 0.201, R8 0.225, R16n 0.239. The coordinate phase lags the
  references at every resolution (gauge: the trackers start at rest with zero shift, multi_puncture
  section 4) and converges far less than the separation (R8 0.225 against R16n 0.239).
- Horizons: R16n finds both members in all 248 searches; masses 0.12742 / 0.12766 at the first
  search and 0.12736 / 0.12763 at 7.7 M (flat: fitted drift -7e-5 and -5e-7 per M over 3-7.7 M),
  mean coordinate radius 0.107-0.109 (14 cells). R8: 2 failed searches per finder, all at
  t <= 0.25; masses 0.1257 / 0.1275 at first, 0.1303 / 0.1316 at 20.9 M (drift +1.0e-3 and
  +1.4e-3 per M, P1 1.4e-3 / 1.7e-3), coordinate radius 0.110-0.112 (7 cells).
- Constraint norm (history, rms H over the domain +-128): R16n 4e-5 after t = 1, R8 6e-4 (ratio
  14 for a halved cell: order 3.8). R8 has one sample at t = 0.5 with H-norm2 = 1.83e4 (P1:
  5.99 at the same time; R8 back to 10.9 at t = 1.0). A transient of one history sample, cause not
  determined [TO VERIFY: a regrid at t = 0.5 with the release core-v0.5 executable on +-128; P1 ran
  core-v0.3 on +-256]. All history columns finite; Volume constant.
- Cost (segment logs, sacct): R8 2241 MeshBlock-cycles/s, 5362 cycles, 20.94 M in 0.835
  card-hours, GPU peak 48.8 GB at 2000 slots, tree 1170 -> 1240; R16n 2302 MeshBlock-cycles/s,
  3963 cycles, 7.74 M in 0.835 card-hours, peak 58.6 GB at 2400 slots, tree 1744 -> 1618.

Predictions of BC-1:
1. R8 alone within 0.10 M of P1 to the end of its window: MET (largest difference 0.0898 M at
   20.94 M; 0.032 at 7.5, 0.070 at 15). Its sub-ranges: s(10) = 4.8257 in 4.73-4.83 MET (at the
   edge); s(15) = 4.6465 outside 4.53-4.63, FAILED by 0.017 M. The isolated binary decays more
   slowly than P1 by 13-33 percent: the third body (or the mesh and executable differences of
   R8 against P1: +-128 against +-256, core-v0.5 against core-v0.3) adds to the decay, but most of
   it is present without the heavy hole.
2. Decay resolution driven, R16n's Delta s at most half of R8's: MET on the window available
   (7.5 M: 0.0042 against 0.0657, ratio 0.064); the 15 M comparison waits for R16n segment 2.
3. Order 1-4: two-point only, 3.96 (Delta s at 7.5 M) and >= 3.3 (deviation from EIH); inside the
   range, three-point order NOT DONE (R12 queued).
4. Horizons: every R16n search found; growth at R16n below half of R8's: MET. Member masses at
   5 M in 0.128-0.140 at all resolutions: FAILED for R16n (0.1274, 0.1276), met for R8 (0.1282,
   0.1285): the finer mesh gives the smaller (closer to bare) mass, i.e. the m/8 masses carry a
   resolution excess of about 0.001.
5. Finite fields, exit 0 at the wall clock, Volume constant: MET; the R8 constraint transient at
   t = 0.5 was not predicted.
6. Cost: start trees MET (exact). Rates: R8 2241 in 1800-2300 MET; R16n 2302 FAILED by 2
   MeshBlock-cycles/s (above). Advance per segment: R8 20.94 M in 15-21 MET; R16n 7.74 M outside
   5.5-7.5, FAILED (above): the measured trees (1618 at the end of the segment) are smaller than
   the model's Newtonian mean (1725), so the cost model is slightly pessimistic.
7. Verdict: next entry.

## 2026-11-21 BC-4. Verdict and the input of P1b [JUDGEMENT unless marked]

1. P1's merger at 48.8 M is a resolution effect of the m/8 members: the binary alone at m/8 decays
   the same way (87 percent of P1's Delta s at 20 M), the binary alone at m/16 follows the 1PN
   reference within 0.006 M over the first 7.7 M, and the error between them falls by at least ten
   for a halved cell [VERIFIED numbers above]. The heavy hole adds a smaller part (13-33 percent of
   the decay over 7.5-20 M) that this package does not separate from the mesh and executable
   differences.
2. Survival time. Physical inspiral 2600-3400 M (BC-2). Numerical: m/8 merges at about 49 M (P1)
   or 53 M alone (stretch estimate). If the numerical decay rate scales as h^p with p >= 3.3, the
   m/16 decay is at least ten times slower and the binary at m/16 merges after more than about
   500 M; even p = 2 would give about 210 M. So m/16 should survive the 100 M of a passage, by
   extrapolation from a 7.7 M window; R16n segments 2-3 (to about 23 M, queued) are the check:
   refuted if R16n departs from EIH by more than 0.05 M by 20 M. m/12: with p >= 3.3 about 200 M,
   with p = 2 about 120 M, i.e. likely but not shown; R12 (queued, 2 segments, about 16 M) decides
   whether the 30 percent cheaper m/12 is enough.
3. Resolution of P1b: m/16 (R16n: P1's mesh with an 11th level), constant shift_eta = 2 as P1 and
   as tested here. The mass-scaled profile of junk_gauge's recommendation is not needed for the
   orbit at m/16 and was not tested in this package.
4. Input: `inputs/p1b_R16n.athinput` (written by `scripts/make_p1b.py` from P1's input; only the
   comment, num_levels = 11 and max_nmb_per_rank = 3000 differ; start tree 2514 by `athena -m`,
   run F-20261121-131003-75a2b29). 3000 slots ran on one card at 78785 MiB of 81920 (g2mesh,
   F-20261120-222810-e408386); model maximum 2864 along the Newtonian tracks to 280 M.
5. Cost from the measured R16n rate (2302 MeshBlock-cycles/s, elapsed/computing 1.002) and the
   g2mesh model trees of P1's set-up at R16n along the Newtonian three-body tracks (mean 2428 to
   150 M, 2470 to 200 M, 2527 to 280 M; run F-20261120-222426-86392c3), 512 cycles per M
   [arithmetic, analysis run F-20261121-153844-fbc75ac]: 22.6 card-hours to 150 M, 30.6 to 200 M,
   43.8 to 280 M, i.e. 27, 37 and 53 segments of 50 minutes. P1's own trees at m/8 were 10 percent
   below the Newtonian model (g2mesh G2M-1 item 3), so these are upper estimates. m/12 for
   comparison: 15.6 / 21.2 / 30.4 card-hours (if R12 shows it survives).
6. Chain command for P1b (NOT submitted; the lead decides; the request is above eight card-hours,
   so decision 0014 asks for an announcement in STATUS.md first; 200 M shown):

       harness/bin/nrpic-run submit --kind scouting --gate G1 --launcher chain --gpu-hours 32 \
           --package tracks/F-hills/binary_conv \
           --exe tracks/F-hills/binary_conv/scripts/athena_keep_trackers_bc.sh \
           --input /data/haiyangw/nrpic/scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu \
           --parent F-20261119-150017-b45ec5f --parent F-20261121-130351-04074e1 \
           --preregistered '<the lead's P1b prediction in tracks/F-hills/JOURNAL.md>' \
           --purpose "P1b: Hills passage q = 4 as P1 with the members at m/16 (R16n), 200 M" \
           -- tracks/F-hills/binary_conv/inputs/p1b_R16n.athinput time/tlim=200

   (`--gpu-hours 32` gives floor(32/0.983) = 32 segments of 50 min, about 26.7 card-hours and
   about 32 x 6.3 M; raise it to about 38 for the full 200 M; `time/tlim=280` and about 54 for
   280 M.) The chain resubmits one segment at a time; a segment advances about 5.3-6.3 M (three
   holes, 2428-2527 blocks at 2302 MeshBlock-cycles/s).
