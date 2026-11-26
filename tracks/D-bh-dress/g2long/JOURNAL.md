# JOURNAL of g2long (Track D: long card runs toward G2, plain 1+log)

Package of the D-bh-dress lead, batch 5 (2026-11-21, decision 0025 items 3-5). Newest at the
bottom. Inputs: `inputs/*.athinput`, built by `tools/make_inputs.py` (its self-check rebuilds
V-1B of drift_controls from V-1 exactly). Executable of every card run: release core-v0.6,
`/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena`. No run sets `lapse_leak`.

## Entry 1 (2026-11-21 12:28 PST, before any run; committed 53afc1a): design, criteria and predictions

Why. G1 (signed with reservations, coord/GATES.md) left for G2: the null test quoted against
the matched control (V-1B, floor [-4.8e-5, +2.0e-5] on 100-200 M at M/8) and kept off the
relaxed lapse; one resolution. ES-F (D-20261121-144631-aa7ce9b, closed today; analyses
D-20261121-202137-7bc388e, -202142-ce0f509) showed the growth following the exact LTB curve
to 0.25 per cent up to t = 200 M (lead's REVIEW-wave3 section 11). The faces at +-192 or
+-384 M limit every run: with 1+log the gauge speed far out is about sqrt(2), so a signal
from faces at +-F reaches the hole after about F/1.41 (136 M for V-1, 272 M for V-1B)
[JUDGEMENT; V-1 left V-1B from about 100-140 M]. For runs to 500 M the faces go to +-768 M
(one more coarser root level than V-1B: 456 MeshBlocks against 400; the mesh inside +-384 M
is V-1B's, inside +-192 M ES-1's).

Runs (all chains of `scripts/submit_chain.sh` through `nrpic-run submit --launcher chain`):

| Run | Input | tlim | Role | Card-hours (estimate; cap) |
|---|---|---|---|---|
| R1 V-1L | `inputs/v1l.athinput` | 500 M | vacuum control, noise floor | 2.2 (V-1 0.672 per 200 M x 456/344 x 2.5); cap 3.5 |
| R2 ES-1L | `inputs/es1l.athinput` | 500 M | null test (vacuum bubble in expanding dust) | 2.5 (ES-1 0.769 x 456/344 x 2.5); cap 4.0 |
| R3 ES-FL | `inputs/esfl.athinput` | 500 M | growth of the hole and dress, against flux and LTB | 2.6 (ES-F 0.81 per 200 M); cap 4.0 |
| R4 V-1L16 | `inputs/v1l16.athinput` | 300 M | floor at M/16 (mesh convergence) | from smoke S3; cap 4.0 |
| R5 ES-1L16 | `inputs/es1l16.athinput` | 300 M | null test at M/16 | from smoke S3; cap 5.0 |

Order: R1 and R2 eligible at once; R3, R4, R5 submitted and held (`scontrol hold`), released
in this order by `tools/sequencer.sh` whenever fewer than two D chains are active
(decision 0025 item 5).

Definitions. M_X(t): finder mass (horizon_summary column 3, unique times). D_X(t) = M_X(t) -
M_X(100 M). Floor F_V(T) = max |D_V1L(t)| over 100 <= t <= T.

### Criteria fixed here (for G2; judged when the runs end)

N (null test, track sheet G2 "drift does not exceed the noise floor"): max over 100 <= t <= 500
of |D_ES1L(t) - D_V1L(t)| <= max(2 F_V(500), 1e-4). Refuted (a drift beyond the floor) if
|D_ES1L - D_V1L| exceeds 3 max(F_V(500), 5e-5) over a window longer than 50 M.
G (growth against flux, track sheet G2): ES-FL meets criterion (iii) of flux_tools JOURNAL
entry 7 (bins of 10 M of tau_rem, every median within +-0.01 of the exact LTB curve) for
tau_rem <= 650 M, and D2 of entry 7 (F_rem - 3e-3 <= M_AH - M_V1L <= F_sph + 3e-3 for t >= 20
M) with V-1L as the control.

### Predictions

Smoke tests on processors (release core-v0.6 `build_cpu_v06`, 2 cycles, one core each):
S1 v1l starts, 456 MeshBlocks, finder at t = 0 equal to V-1's 0.99239 within 1e-5.
S2 esfl starts, 456 MeshBlocks, 850724 particles, finder at t = 0 equal to ES-F's 0.991521
   within 1e-5.
S3 es1l16 starts; MeshBlocks between 500 and 900 [JUDGEMENT: the level-8 blocks on +-3 M force
   level 7 out to about +-6 M]; finder at t = 0 finite in [0.98, 1.00].
Refuted (and no card run of that input) if an input fails to start or a count is outside.

R1 V-1L:
V1 finite to 500 M, horizon found at every sample, no tracer leaves the mesh.
V2 equals V-1B (core-v0.4, faces +-384 M) within 1e-6 in M_AH for t <= 200 M (neither run's
   faces reach the hole before ~270 M; v0.5 and v0.6 change nothing these inputs use
   without an option). Refuted above 1e-5 (then the executable changed the vacuum run).
V3 floor: F_V(500) <= 1e-4 (V-1B: 4.8e-5 to 200 M); refuted above 3e-4. Mean coordinate
   radius at 500 M 2.2-2.6 M (V-1B 2.20 M at 200 M).
V4 cost 2.0-2.6 card-hours.

R2 ES-1L:
E1 equals ES-1 (D-20261115-172726-60ba4c2, faces +-192 M) within 1e-5 in M_AH up to 130 M;
   refuted above 1e-4 before 130 M. Finite; the dust outside the bubble stays on the mesh.
E2 null test: criterion N holds [JUDGEMENT, p ~ 0.6]: max |D_ES1L - D_V1L| <= 1e-4 on 100-300
   M and <= 2e-4 on 100-500 M. (At +-192 M ES-1 drifted [-3.4e-4, +9.4e-5] and V-1
   [-1.37e-4, +2.1e-5] on 100-200 M, both with the faces in reach.) A coupling M ~ a^k would
   give dM/M = k ln a; with a(t) ~ (1 + 1.5 H t)^(2/3), H = 5.58e-3/M, ln a(500 M) ~ 1.1
   [JUDGEMENT: Einstein-de Sitter for the dust at the wall], so a difference below 2e-4
   bounds k below about 2e-4 (k = 3 would give dM/M ~ 3.3).
E3 mean coordinate radius at 500 M 2.6-3.1 M (ES-1: 2.56 M at 200 M).
E4 cost 2.2-2.9 card-hours.

R3 ES-FL:
F1 equals ES-F within 3e-4 in M_AH up to 130 M (card deposition is not reproducible bit for
   bit; the removal times differ by steps).
F2 M_AH(t) = M_LTB(kappa t) + 9e-4 with kappa falling from 1.32 (ES-F at 199.5 M; 1.47 at
   50 M) to 1.25-1.33: M_AH(300) 1.364-1.390, M_AH(400) 1.497-1.530, M_AH(500) 1.625-1.665
   (results/esf_growth.csv of flux_tools). Refuted outside [1.33, 1.43], [1.45, 1.58],
   [1.56, 1.72] (then the gauge model kappa is wrong, not G).
F3 criterion G holds; overall median of (iii) +0.2 per cent (0.1-0.4); D1 closure at 500 M,
   control-subtracted, within [0, +8e-3].
F4 removed sum of m E_K at 500 M 0.60-0.70; every removal by reason 3; none escapes.
F5 the finder keeps the horizon at every sample while it grows to a mean coordinate radius of
   4-5.5 M (3.19 M at 199.5 M), i.e. out of the M/8 region. Failure mode named in advance:
   the finder losing the horizon there (then (iii) is judged only up to the loss).
F6 cost 2.3-3.0 card-hours.

R4 V-1L16, R5 ES-1L16 (to 300 M):
H1 the late finder bias falls with resolution: M_V1L16 - 1 on 100-300 M in [3e-5, 4e-4]
   (V-1B at M/8: +9.4e-4).
H2 F_V16(300) <= 5e-5, below the M/8 floor on the same window.
H3 |D_ES1L16 - D_V1L16| on 100-300 M no larger than |D_ES1L - D_V1L| on the same window.
H4 cost from S3's block count: (blocks/456) x 2 (half the step) x the M/8 cost per M.

## Entry 2 (2026-11-21 12:31 PST, before any card run; committed a34cf1f): ES-F's table does not reach the new corner

The smoke S2 log (D-20261121-202936-ebc09f0) prints for esf.tab "table covers the mesh corner
of ES-1 (+-192 M -> 332.6 M) ... exterior = zero": beyond rbar = 345 M the curvature KL, KT
of the ES-F slice is set to zero, a jump in the momentum constraint at 345 M that would
reach the hole after ~250 M on the +-768 M mesh (corner 1330 M). ES-1 and V-1 tables have
exterior = pg (exact continuation), so only ES-FL is affected. Fix: the ES-F data maker with
`--rbar_max 1340` (run D-20261121-203042-82deeec): its 17250 table rows up to 345 M are
byte-identical to those of D-20261119-145022-2208a19, its header lines are identical, and
its particle file esf.nrp is byte-identical (cmp). `inputs/esfl.athinput` now reads table and
particles of that run (tools/make_inputs.py). S2 is repeated on the new input (S2b) with
the same prediction as S2.

## Entry 3 (2026-11-21 12:33 PST): submissions

All chains through `harness/bin/nrpic-run submit --launcher chain --exe
/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena` (MAX_SEGMENTS = floor(card-hours cap /
59 min)); then, by hand, `PROC_NAME=D-<name>` written into each chain's `chain/config.sh`
before its first segment started (nrpic-run passes no PROC_NAME; the chain re-reads the file
at every segment and links `chain/athena` to that name).

| Run | Run id | First job | Cap (segments) | State at 12:33 |
|---|---|---|---|---|
| R1 V-1L | D-20261121-203124-a34cf1f | 4830 | 3.5 (3) | pending (Priority) |
| R2 ES-1L | D-20261121-203131-8ee2a49 | 4831 | 4.0 (4) | pending (Priority) |
| R3 ES-FL | D-20261121-203150-15f2bad | 4833 | 4.0 (4) | held |
| R4 V-1L16 | D-20261121-203151-37e7b2d | 4834 | 5.0 (5) | held |
| R5 ES-1L16 | D-20261121-203151-59c54fb | 4835 | 6.0 (6) | held |

Sequencer: `tools/sequencer.sh`, copy started with setsid nohup from
`/data/haiyangw/nrpic/scratch/D-bh-dress/g2long_seq/` (pid in `pid`, log in `log`, queue R3,
R4, R5 in `queue`); it releases the next held job when fewer than two D jobs are running or
pending without a hold. Stop: `touch .../g2long_seq/STOP`. Smoke runs: S1
D-20261121-202935-53afc1a, S2 D-20261121-202936-ebc09f0 (old table), S3
D-20261121-202936-992542e, S2b D-20261121-203149-4904e96 (new table); outcomes below when
they end. Block counts already in the logs: v1l and esfl 456 (S1, S2 held), es1l16 512 (S3
held: 56 per level on levels 0-7 and 64 on level 8).

## Entry 4 (2026-11-21 12:53 PST): outcome of the smoke tests (processors, release core-v0.6)

All four ran 2 cycles and stopped on the cycle limit, exit 0 (18-21 min each on one core,
1.28e4 zone-cycles per second).
S1 v1l (D-20261121-202935-53afc1a): 456 MeshBlocks (56 on each of levels 0-6, 64 on level 7);
   140 particles; finder at t = 0 M = 0.9923902364485537 against V-1's 0.9923902364485533:
   HELD (4e-16).
S2 esfl, old table (D-20261121-202936-ebc09f0): 456 MeshBlocks, 850724 particles, finder
   0.9915211031392506 against ES-F's 0.9915211031392509: HELD. Superseded by S2b (entry 2).
S2b esfl, table to 1340 M (D-20261121-203149-4904e96): table read with 67001 rows; 456
   MeshBlocks; 850724 particles; finder 0.9915211031392506: HELD (the extension changes
   nothing inside the ES-F mesh, as built).
S3 es1l16 (D-20261121-202936-992542e): 512 MeshBlocks (56 on each of levels 0-7, 64 on level
   8; inside the predicted 500-900); 696828 particles; finder 0.9998168466897429: HELD. At
   t = 0 the finder's offset from the bare data is -7.6e-3 at M/8 (ES-1 and V-1:
   0.99239024) and -1.8e-4 at M/16.
Cost of R4, R5 from S3 (H4): 512/456 x 2 = 2.25 times the M/8 cost per M: V-1L16 to 300 M
~3.0 card-hours (cap 5.0), ES-1L16 ~3.4 (cap 6.0).

## Entry 5 (2026-11-22 17:59 PST, lead of batch 10a): outcomes of R1-R4, of ES-FL, and of R5 to 225.6 M

Chains: R1 V-1L DONE at 500 M (jobs 4830, 4852, 4864; 2.24 card-hours), R2 ES-1L DONE at 500 M
(4831, 4853, 4865; 2.49), R3 ES-FL DONE at 500 M (4833, 4876, 4887, 4897; 2.60), R4 V-1L16 DONE
at 300 M (4834, 4877, 4888, 4898; 3.00), R5 ES-1L16 at t = 225.6 M after three segments (4835,
4906, 4913; 2.51), its fourth segment queued as job 4920. Card time 12.84 h (Slurm elapsed
times, one card each). The sequencer released R5 at 11:12 and exited at 11:14 with its queue
empty (scratch/D-bh-dress/g2long_seq/log): it has ended normally, nothing is held.
Analysis first run into scratch/D-bh-dress/tmp/ by hand; the registered reruns (run ids in
entry 7) repeat the same commands. Tools: `tools/judge_long.py` (written here, from the
definitions of entry 1), `../flux_tools/esf_analyse.py`, `../g2runs/tools/esf_criteria.py` with
a new `--tau_max` option (default 250 as before; 650 here, as entry 1 asks). Figures looked at:
judge_long.png, esf_criteria.png, esf_growth.png, esf_bracket.png.

R1 V-1L
- V1 HELD: finite to 500 M, horizon at every 0.5 M sample (largest gap 0.5 M), no tracer escaped
  (140 -> 98 tracers: 42 fell into the hole, none left the mesh).
- V2 HELD: |M_V1L - M_V1B| <= 5.0e-8 for t <= 200 M (largest at 186.5 M; below 1e-14 until
  ~165 M): the executables v0.4 and v0.6 give the same vacuum run.
- V3 FAILED as predicted (not refuted): F_V(500) = 1.25e-4 (> 1e-4, < 3e-4). D_V1L lies in
  [-4.8e-5, +1.25e-4]; the maximum comes from a step of about +1.2e-4 between 240 and 300 M
  (judge_long.png panel b), after which D stays at +1.15e-4 to 495 M; the last sample (499.5 M)
  drops back to -1e-5. Mean coordinate radius at 500 M 2.18 M, below the predicted 2.2-2.6 M:
  the radius is stationary (2.197 at 200 M, 2.189 at 400 M), not growing as entry 1 assumed.
- V4 HELD: 2.24 card-hours (2.0-2.6).

R2 ES-1L
- E1 HELD: |M_ES1L - M_ES1| <= 8.4e-6 up to 130 M; beyond 130 M ES-1 (faces +-192 M) leaves,
  5e-4 by 200 M (panel d).
- E2: criterion N HOLDS (max |D_ES1L - D_V1L| on 100-500 M = 2.28e-4 at 256.5 M, threshold
  max(2 F_V, 1e-4) = 2.51e-4; nowhere above the refutation level 3.76e-4). The sharper
  predictions FAILED: <= 1e-4 on 100-300 M (2.28e-4) and <= 2e-4 on 100-500 M. Shape: the ES run
  has its step of ~+1.8e-4 at 150-160 M, the vacuum run its step at 240-300 M; after 300 M the
  difference sits at +7.5e-5 +- 1e-5 to 495 M (panel c).
- E3 FAILED: radius at 500 M 2.36 M (predicted 2.6-3.1); it shrinks slowly, 2.45 at 200 M,
  2.36 at 500 M (ES-1's 2.56 at 200 M was its faces).
- E4 HELD: 2.49 card-hours (2.2-2.9).
- Bound on a coupling M ~ a^k (the [JUDGEMENT] reading of entry 1): the difference never
  exceeds 2.3e-4 while ln a grows by ~1.1, so |k| below ~2e-4 at this resolution and boundary,
  if the whole difference were a coupling.

R3 ES-FL
- F1 HELD: |M_ESFL - M_ESF| <= 6.1e-8 up to 130 M (cards are not bit-reproducible, but here they
  agree far inside 3e-4); after 130 M ES-F's faces (+-192 M) act: 3.0e-3 at 190.5 M. So the ES-F
  growth quoted at 200 M carried a face error of up to 3e-3 in M after 130 M.
- F2 partly FAILED: M_AH(300) = 1.3708 HELD (1.364-1.390); M_AH(400) = 1.4920 FAILED (1.497-
  1.530) and M_AH(500) = 1.6090 FAILED (1.625-1.665); neither outside the refutation windows
  ([1.45, 1.58], [1.56, 1.72]). kappa_late = tau/t of the last removals = 1.20 (predicted
  1.25-1.33): the gauge model of entry 1 overestimated kappa at late times; the exact LTB
  comparison (G) does not use kappa.
- F3: criterion G HOLDS. (iii) to tau_rem <= 650 M: 61 bins of 10 M counted, every dust median
  within +-0.62 per cent (largest 6.2e-3), so within +-1 per cent; D2 holds at all 960 samples
  after 20 M (margins 3.3e-3 below the upper bound F_rem side, 1.2e-2 below F_sph). The
  predicted overall median +0.2 per cent (0.1-0.4) FAILED: +0.52 per cent, because the medians
  step from +0.25 to +0.6 per cent at tau_rem ~ 285 M (esf_criteria.png panel b). D1 closure,
  control-subtracted, at 499.5 M = +9.4e-3, outside the predicted [0, +8e-3]: FAILED narrowly
  (raw 1.80e-2). D3 holds (no violation, smallest margin 1.9e-4); D4: 0.23 per cent of the
  removals precede the LTB horizon crossing, none by more than 0.084 M of proper time.
- F4 partly FAILED: removed sum of m E_K at 500 M 0.601 (0.60-0.70: HELD), none escaped (HELD),
  but NOT every removal by reason 3: 84496 of 147840 dust removals are by reason 2 (lapse below
  alpha_exc = 0.05). Every removal before 218.9 M is reason 3, every one after 224.0 M reason 2
  (median coordinate radius at removal 1.12 M against 2.04 M). [VERIFIED by source and data]
  athenak/src/particles/nrpic.cpp:451-455 empties a horizon only while its smallest
  coordinate radius is below 4 x initial_radius (here 4 x 0.8 = 3.2 M); the finder's smallest
  radius (summary column 12) passes 3.2 M between t = 219.0 (3.19986 M) and 219.5 M (3.20419 M).
  The steps at ~220 M in D3 (margin 0.001 -> 0.0065, panel c), in the residual of
  esf_bracket.png and at tau_rem ~ 285 M in (iii) coincide with that switch: particles are now
  removed deeper and later in coordinate time, where the finder mass is larger [JUDGEMENT on the
  mechanism; ESFLK in entry 6 is the run in which it can fail].
- F5 HELD: horizon found at every sample (no gap above 1 M), mean coordinate radius 5.30 M at
  499.5 M (predicted 4-5.5 M), out of the M/8 region (+-1.5 M requested, level-7 blocks reach
  further) without loss.
- F6 HELD: 2.60 card-hours (2.3-3.0).

R4 V-1L16 (to 300 M) and R5 ES-1L16 (to 225.6 M so far)
- H1 FAILED: M_V1L16 - 1 on 100-300 M lies in [-3.1e-4, -1.3e-4], not in [3e-5, 4e-4]; the
  late finder bias changes sign between M/8 (+8.9e-4 to +1.06e-3) and M/16, and falls in
  magnitude by a factor ~3-7. At t = 0 the offsets are -7.6e-3 (M/8) and -1.8e-4 (M/16)
  (entry 4). Two resolutions cannot give an order here; a third is queued (entry 6).
- H2 FAILED: F_V16(300) = 1.34e-4, above 5e-5 and above the M/8 floor on the same window
  (1.22e-4). The drift of V-1L16 repeats V-1L's step at 240-300 M in time and size (panel b):
  the floor is not set by the resolution at the horizon [VERIFIED for M/8 against M/16].
- H3 HOLDS on the window reached (100-225.5 M, partial): max |D_ES1L16 - D_V1L16| = 1.86e-4
  against 2.09e-4 at M/8; the two differences follow each other within ~3e-5 (panel c), so the
  null-test difference is not a truncation error at the horizon either. Final judgement when R5
  reaches 300 M.
- H4 HELD for R4 (3.00 card-hours against ~3.0); R5 at 2.51 for 225.6 M, on course for ~3.35.

## Entry 6 (2026-11-22 18:05 PST, before any follow-up run): follow-ups, criteria and predictions

Why. (a) G2 asks for convergence in mesh spacing (brief 9.2, scope/SCOPE.md section 5: "at
three resolutions, converging"), and H1 shows the late finder mass changing sign between M/8
and M/16: two members cannot give an order. The cheapest third member is the coarser one:
the finest level M/8 -> M/4 on the same +-1.5 M request (the M/16 nest costs 2.25x M/8, an M/32
nest that still holds the 2.2 M horizon about 13 card-hours per run). (b) Entry 5 names a
mechanism for the step in (iii) and D3 at ~220 M (horizon excision ends at 4 x initial_radius);
a run in which it can fail keeps the excision on. Inputs: `tools/make_followups.py` (one change
each from v1l, es1l, esfl; cfl_number 0.25, plain 1+log with the Gamma-driver shift, no
lapse_leak: decisions 0025 item 3 and 0027 item 2).

| Run | Input | tlim | Change | Card-hours (estimate; cap) |
|---|---|---|---|---|
| FV4 V-1L4 | inputs/v1l4.athinput | 300 M | finest level M/4 | 0.6 (392/456 blocks x half the steps x V-1L's 0.0045 per M); cap 2.0 |
| FE4 ES-1L4 | inputs/es1l4.athinput | 300 M | finest level M/4 | 0.65; cap 2.0 |
| FK ES-FLK | inputs/esflk.athinput | 400 M | initial_radius_0 1.6 | 2.1; cap 3.0 |
| FF4 ES-FL4 | inputs/esfl4.athinput | 500 M | finest level M/4 | 1.1; cap 2.0 |

Order: FV4 eligible beside R5 (job 4920); FE4, FK, FF4 held and released in this order by
`tools/sequencer.sh` (at most two D jobs eligible). Expected 4.5 card-hours; caps 9.0.

Smoke tests (processors, release core-v0.6, 2 cycles, one core each), before any card job:
S4 v1l4 and es1l4 start, MeshBlocks 392 +- 8; the finder at t = 0 either finds a surface with
   mass in [0.85, 1.0] or reports none (the t = 0 horizon has a coordinate radius of 0.48 M,
   two M/4 cells) [JUDGEMENT]. S5 esfl4 the same, 850724 particles. S6 esflk starts, 456
   MeshBlocks, finder at t = 0 equal to ES-F's 0.9915211 within 1e-4 (the flow starts at 1.6 M
   instead of 0.8 M and should end on the same surface). Refuted, and no card run of that input,
   if an input fails to start, exits non-zero, or S6's mass differs by more than 1e-3.

Predictions for the card runs:
FV4 P1 finite to 300 M; horizon at every sample after 20 M.
    P2 late bias in the convergent regime: with e(h) = e_inf + C h^p fitted to M/8 (+9.4e-4)
       and M/16 (-2.4e-4), orders p = 2, 3, 4 give e(M/4) = +5.7e-3, +1.0e-2, +2.0e-2, so
       M_V1L4 - 1 on 100-300 M in [+4e-3, +2.5e-2]. Refuted (M/4 not in the convergent regime,
       and the three-member order is then not quoted) if below 0 or above 5e-2.
    P3 the vacuum drift step of V-1L and V-1L16 at 240-300 M appears again within 10 M in time and
       within a factor 2 in size. Refuted if it is absent.
    P4 cost 0.45-0.75 card-hours.
FE4 P5 null test at M/4: max |D_ES1L4 - D_V1L4| on 100-300 M in [1e-4, 4e-4] and within 1e-4 of the
       M/8 difference at every common sample after 110 M (the difference does not depend on the
       horizon resolution, entry 5 H3). Refuted if it departs from the M/8 difference by more
       than 2e-4 over a window longer than 20 M.
    P6 cost 0.5-0.8.
FK  P7 equal to ES-FL within 3e-4 in M_AH up to 219 M (before the switch only the first search
       differs).
    P8 every dust removal by reason 3 up to 400 M (smallest horizon radius 4.5 M < 6.4 M).
    P9 the mechanism test: the (iii) medians for tau_rem in 285-500 M stay at +0.25 +- 0.15 per
       cent (no step to +0.6 per cent) and the D3 margin after 220 M stays below 3e-3. Refuted (the
       end of horizon excision is not what moves them) if the medians after tau_rem = 285 M are
       above +0.45 per cent.
    P10 M_AH(400) within 3e-3 of ES-FL's 1.4920 (the depth of removal inside the horizon does not
       move the horizon mass); refuted above 5e-3.
    P11 cost 1.8-2.4.
FF4 P12 criterion G at M/4: (iii) to tau_rem 650 M with every median within +-1 per cent, D2 holds.
       Refuted if any counted bin is beyond +-2 per cent (then G is shown at one mesh spacing only).
    P13 M_AH(t) of ES-FL4 within 1.5 per cent of the growth Delta M of ES-FL at 100, 200, 300, 400,
       500 M [JUDGEMENT]; the excision switch within 10 M of ES-FL's 219 M.
    P14 cost 0.9-1.4.

## Entry 7 (2026-11-22 18:09 PST): registered analyses and smoke tests of entry 6

Registered reruns of entry 5 (outputs byte-identical to the hand-run versions, cmp):
judge_long D-20261123-020550-f9a3482 (judge_long.json, judge_long.png); esf_analyse
D-20261123-020606-fa0046c (esf_growth.png, esf_bracket.png); esf_criteria --tau_max 650
D-20261123-020614-7ba5874 (esf_criteria.json, esf_criteria.png). Closed chains: R1-R4 finished
with nrpic-run finish (manifests committed). Smoke tests of entry 6 started on one core each:
v1l4 D-20261123-020011-bd47394, es1l4 D-20261123-020531-6dbd75c, esfl4 D-20261123-020535-dccfd30,
esflk D-20261123-020538-0290d15; outcomes in entry 8.

## Entry 8 (2026-11-22 18:14 PST, before the analysis runs): constraint norms of the long runs

Prediction (checklist C3/C11 of G2): the volume norms H-norm2 and M-norm2 of `<base>.z4c.user.hst`
stay bounded in V-1L, ES-1L, ES-FL (to 500 M), V-1L16 (300 M) and ES-1L16 (as far as it has run):
in none of them does a norm grow by more than a factor 10 between t = 100 M and the end, and
none jumps by a factor 3 within 10 M [JUDGEMENT; ES-1/V-1 at +-192 M stayed bounded to 200 M].
Refuted by either. Tool: `tools/constraints_long.py`.

Outcome of entry 8 (18:18 PST; run D-20261123-021027-e3af9b8, constraints_long.png looked at): the
prediction HOLDS as written: growth between 100 M and the end 1.00-1.03 for the M/8 runs, 3.6 (H)
and 2.5 (M) for V-1L16, 3.1 and 2.4 for ES-1L16 to 225.6 M; largest rise within 10 M a factor 1.43;
all finite. But the figure does not show that "constraints behave" outside the hole: the norms
are volume integrals over the points with chi >= excise_chi = 0.0625 (athenak/src/outputs/
history.cpp:226-228, default at z4c.cpp:172), so they are dominated by the region just outside
the chi cut, inside the horizon. Signs of it [JUDGEMENT]: the M/16 norms lie ~100 times below the
M/8 ones (no resolution law gives that), and ES-FL's norms drop in steps at ~115, 205, 300 and
385 M while its horizon grows. For G2 item C3 the exterior needs its own norm: `<particles>
region_*` (release core-v0.5, constraint norms inside and outside spheres) in the next inputs,
with a sphere outside the horizon; not in the inputs of R1-R5 or of entry 6.

## Entry 9 (2026-11-22 18:26 PST): smoke tests of entry 6, all held; release order changed

All four ran 2 cycles on one core (release core-v0.6 build_cpu_v06), exit 0, 16-19 min each.
S4 v1l4 (D-20261123-020011-bd47394): 400 MeshBlocks (392 +- 8: at the edge), 140 particles,
   finder at t = 0 reports no surface (nan): HELD (allowed outcome).
S4 es1l4 (D-20261123-020531-6dbd75c): 400 MeshBlocks, 696828 particles, no surface at t = 0: HELD.
S5 esfl4 (D-20261123-020535-dccfd30): 400 MeshBlocks, 850724 particles, no surface at t = 0: HELD.
S6 esflk (D-20261123-020538-0290d15): 456 MeshBlocks, 850724 particles, finder at t = 0 =
   0.99152073 against ES-F's 0.99152110 (3.7e-7, bound 1e-4): HELD; the flow started at 1.6 M
   ends on the same surface.
Consequence for the M/4 runs: horizon excision (reason 3) needs a found surface, so until the
finder finds the trumpet horizon (coordinate radius ~2.2 M, nine M/4 cells) only the lapse rule
removes dust; P1 (horizon at every sample after 20 M) is the first thing to read in FV4.
Release order changed from entry 6 before any submission: FV4 eligible now, then FK, FE4, FF4.
FK does not depend on the M/4 finder; putting FE4 and FF4 last lets the next session read FV4's
P1 before they start and cancel them if the M/4 finder never finds the horizon.

## Entry 10 (2026-11-24 05:10 PST, lead of batch 11, before the runs named here): state, tests FP and XC, new card runs

State at 04:51 PST. Sequencer g2long_seq2 ended normally on 2026-11-23 08:23 (every job released).
R5 ES-1L16 DONE at 300 M (job 4920, 20:07 on 11-22); FV4 V-1L4 DONE at 300 M (job 4933, one segment of
35.4 min). The other three were cut by preemptions (another user's priority jobs, 11-23) and closed
as "FAILED (MAX_SEGMENTS reached)" though only cut: FK ES-FLK at 225.5 M (newest restart 200 M,
segment counter 4), FE4 ES-1L4 at 28 M (restart only at t = 0), FF4 ES-FL4 at 456.1 M (restart at
456.1 M). All three resumed from their newest restart with the same input and executable
(`submit_chain.sh <rundir> <input>`, PROC_NAME kept): FF4 job 5142, FE4 job 5143 (both preempted
again at 05:00:43 and resubmitted as 5152, 5153), FK job 5144 held behind a new sequencer
(scratch/D-bh-dress/g2long_seq3/). Segment caps raised in chain/config.sh to 10, 10, 12 because each
preemption consumes a segment; card time is what the segments run, not the cap.

Looked at before writing what follows (so not blind): the finder masses of FV4 against V-1L and
V-1L16 (a quick print and a trial of tools/judge_conv.py into scratch/D-bh-dress/tmp/jc/, figure
looked at), and a trial of tools/xc_plane.py on V-1L4 and V-1L only (scratch/D-bh-dress/tmp/xc/; its
momentum norm was wrong, fixed since). Outcomes of P1-P4 and H3 follow in entry 11 from registered
runs; the predictions are those of entries 1 and 6.

What the quick look showed, for the record: (a) at M/4 the late finder offset is -7.9e-3 to -9.9e-3
(P2 predicted +4e-3 to +2.5e-2: refuted as written, below 0); the offsets at 100-300 M change sign
twice over M/4, M/8, M/16 (-8.8e-3, +9.5e-4, -2.6e-4), while at t = 0 they converge (q = 5.2, order
2.4). (b) The excursions of the vacuum mass at 230-300 M are not a single step: the mass switches
between plateaus about 1.3e-4 apart (240-244.5 M low, 247.5-252.5 M high, 256-261 M low, ...), at the
same times and with the same size at M/8 and M/16, and, on top of a secular decline, at M/4. The
finder's residual (summary column 9, the area mean of the squared expansion, fastflow.cpp:825 with
the integrand at :1504) sits
at 6-8e-9 on each plateau and drops to 1e-11 to 1e-10 while the mass moves between plateaus. The
finder stops as soon as two successive flow iterations change the mass by less than mass_tol = 1e-5
(fastflow.cpp:914), starting from the previous surface.

### Test FP: is the vacuum excursion the finder's or the slice's? (processors, no card)

Named cause C1: the finder's stopping rule (|Delta M| < 1e-5 between iterations, warm start,
ntheta 16, lmax 8) reports a surface whose expansion residual is ~1e-4 (column 9 ~ 7e-9), and the
plateaus are such surfaces; the slice's horizon mass does not move by 1e-4.
Run: tools/probe_long.py (wrapper of puncture_drift/tools/probe_finder.py) with the threaded release
processor build (scratch/core/exe/core_nrpic_v06/athena_cpu_omp), one cycle from each dump, horizons
h0 (production stopping, from the dump's radius), h1 (mass_tol 1e-9, 4000 iterations, from 1 M),
h2 (production stopping, from 2 M). Dumps (restart files, times exact): V-1L 100, 150, 200, 250, 300,
450 M; V-1L16 100, 200, 250, 300 M; V-1L4 100, 200, 250, 300 M; ES-1L 100, 200, 250, 300 M; ES-1L16 100,
200, 250, 300 M; grid A16 for all, A32 (ntheta 32, lmax 16) in addition for V-1L4, V-1L, V-1L16 at 200
and 250 M.
FP1 (sanity) h0 reproduces the run's own mass at the dump time within 3e-5 (it starts from the stored
    mean radius, not from the run's full surface) and h1, h2 find a surface at every dump.
FP2 (C1) V-1L, tight h1: |M_h1(t) - M_h1(100 M)| <= 3e-5 at 150, 200, 250, 300, 450 M, while the run's
    own D is +1.2e-4 at 250, 300 and 450 M. C1 is REFUTED if M_h1(250) - M_h1(200) >= 8e-5 (the slice's
    horizon moves with the plateau); then the excursion is in the slice. [JUDGEMENT, p ~ 0.65: a
    surface with expansion residual ~1e-4 at r ~ 2.2 M misplaces the radius by ~1e-4 r, which is the
    size of the plateau gap]
FP3 the same for V-1L16 (|M_h1(t) - M_h1(100)| <= 3e-5 at 200, 250, 300 M; refuted as FP2).
FP4 with the finder converged (h1 on A32) the offsets e(h) = M - 1 at 200 M are monotone over M/4,
    M/8, M/16 and give an order p in [1.5, 4.5] [JUDGEMENT, p ~ 0.4]. Refuted (no mesh order even with
    the finder converged) if they change sign or q = (e4 - e8)/(e8 - e16) < 1.
FP5 null test with the tight finder: |(M_h1,ES(t) - M_h1,ES(100)) - (M_h1,V(t) - M_h1,V(100))| <= 1e-4 at
    200, 250, 300 M, at M/8 and M/16 (the run's own difference reaches 2.3e-4 at M/8).
Cost: 28 one-cycle restarts, 2 threads each, three at a time (6 cores); ~1-1.5 h wall [JUDGEMENT].

### Test XC: constraint norms outside the horizon from the z = 0 slices (processors)

Tool tools/xc_plane.py: plane L2 norms of H and |M| (con_M = g_ab M^a M^b) on the annuli A1 = [1.2
r_AH, 6 M], A2 = [6, 30 M], A3 = [30, 100 M] of every con slice (every 25 M). Runs: V-1L4, V-1L, V-1L16,
ES-1L, ES-1L16, ES-FL, FF4 (to 456 M), FK (to 225 M); the others when they end.
XC1 bounded: in every run and annulus the norm at the last slice is below 10 times its value at 100 M,
    and no norm rises by more than a factor 10 between consecutive slices after 100 M. Refuted by
    either. (Not blind for V-1L4 and V-1L, whose H norms were looked at: largest rise there 6.5.)
XC2 near the hole, vacuum: the mean of ||H||_A1 over the slices of 100-300 M falls from M/8 to M/16
    (V-1L16 below V-1L) [JUDGEMENT; beyond +-3 to +-6 M the two meshes are identical, so the fall is
    expected to be modest, a factor 1.3-3]. Refuted if the M/16 mean is not below the M/8 mean.
    (M/4 against M/8 was seen in the trial: 1.3e-5 against 8e-6, not blind.)

### New card runs (inputs by tools/make_followups2.py; release core-v0.6 card executable)

Why: the scope's relaxation control (SCOPE.md section 5, G2: "capture rate and spike profile
unchanged between N and 4N") and the G2 general item "three-way convergence in particle number"
have no run; the growth comparison G has two meshes (FF4 M/4 pending, ES-FL M/8), not three; the
exterior constraint norms (stage/G2/OPEN.md item 2) have only the z = 0 plane. Every new input carries
`<particles> region_*` (region_dcycle 160; spheres of radius 6, 12, 30, 60 M and one of 1.2 times the
finder's mean radius). Step and gauge of the parents (cfl_number 0.25, plain 1+log with the
Gamma-driver shift, no lapse_leak: decisions 0025 item 3, 0027 item 2).

| Run | Input | Parent, change | tlim | Card-hours (estimate; cap) |
|---|---|---|---|---|
| FN4 ES-FLK4N | inputs/esflk4n.athinput | esflk; dust lattice h_p = 4^(-1/3) M (4N) | 400 M | 2.8; cap 4.5 |
| FNQ ES-FLKQ | inputs/esflkq.athinput | esflk; h_p = 4^(1/3) M (N/4) | 400 M | 1.9; cap 3.0 |
| FL16 ES-FL16 | inputs/esfl16.athinput | esfl; a level M/16 on +-3 M (as es1l16) | 300 M | 3.5; cap 5.0 |

Order: behind FK in the sequencer (FK, FN4, FNQ, FL16; at most two D jobs eligible). Expected 8.2
card-hours, caps 12.5 (announced in STATUS.md, decision 0014). The N member of the particle sequence
is FK (esflk, 850724 particles); the mesh members of the growth sequence are FF4 (M/4), ES-FL (M/8)
and FL16 (M/16), all with initial_radius 0.8.

Data (flux_tools/esf_data.py --rbar_max 1340 with --hp 0.62996 and --hp 1.5874; processors, seconds):
D1 the dust particle count is 4 and 1/4 times the N data's (850584 dust particles) within 3 per cent;
   the total dust rest mass equals the N data's within 1e-3 relative; esf.tab is byte-identical to
   the N data's (the table does not depend on h_p). Refuted, and no input built on it, if the table
   differs or the mass differs by more than 1 per cent.
Smoke tests (release core-v0.6 processor build build_cpu_v06, 2 cycles, one core each, with
`particles/region_dcycle=1` on the command line so that the region file is written):
S7 esflk4n starts, 456 MeshBlocks, 140 + 4N dust particles as written by D1, finder at t = 0 equal to
   S6's 0.99152073 within 1e-6 (the finder sees the metric, which the lattice does not change at t = 0);
   region.hst written with finite columns.
S8 esflkq the same with N/4.
S9 esfl16 starts, 512 MeshBlocks (as es1l16), 850724 particles, finder at t = 0 finite in [0.98, 1.0]
   and nearer to 1 than ES-FL's M/8 value 0.99152 [JUDGEMENT]; region.hst written.
Refuted, and no card run of that input, if an input fails to start, exits non-zero, or a count or the
S7/S8 finder value is outside.

Predictions for the card runs (judged when they end; FK is the N member):
FN4 N1 criterion G holds: (iii) every 10 M bin of tau_rem reached within +-1 per cent of the exact LTB
       mass, D2 holds after 20 M (esf_criteria.py with --data of the 4N data run, control V-1L).
    N2 relaxation control: the removed sum of m E_K at 100, 200, 300, 400 M within 1 per cent (relative)
       of FK's [JUDGEMENT: the lattice samples the same continuum; capture is set by the metric];
       refuted above 3 per cent at any of them.
    N3 M_AH(t) within 2e-3 of FK at 100-400 M, and |M_4N - M_N| <= |M_N - M_N/4| at three of the four
       times (convergent ordering in particle number) [JUDGEMENT, p ~ 0.6].
    N4 cost 2.3-3.4 card-hours.
FNQ Q1 criterion G holds with every bin within +-2 per cent; Q2 removed m E_K within 3 per cent of FK's
       at 100-400 M; Q3 cost 1.6-2.3.
FL16 L1 finite to 300 M; horizon at every sample.
    L2 criterion G holds on the tau_rem reached (every bin within +-1 per cent, D2 holds).
    L3 mesh order of the growth: with DeltaM(t) = M_AH(t) - M_AH(20 M), |DeltaM_16 - DeltaM_8| <
       |DeltaM_8 - DeltaM_4| at 100, 200 and 300 M [JUDGEMENT, p ~ 0.6]; refuted if larger at all three.
    L4 cost 3.0-4.0.

## Entry 11 (2026-11-24 05:45 PST, lead of batch 11): outcomes of R5, FV4, D1, S7, S8; prediction for FP-ext

Closed with `nrpic-run finish`: R5 ES-1L16 D-20261121-203151-59c54fb (DONE at 300 M; 129 files),
FV4 V-1L4 D-20261123-022715-ab5d983 (DONE at 300 M; 104 files). Registered analyses: judge_long
rerun with R5 complete D-20261124-131138-0b8ffc5 (judge_long.png looked at), judge_conv
D-20261124-131149-9f0166d (judge_conv.png looked at; byte-identical to the trial of entry 10),
boundary_gauge D-20261124-131657-89cd963 (boundary_gauge.png looked at).

R5 (entry 1):
- H3 HOLDS (final): max |D_ES1L16 - D_V1L16| on 100-300 M = 1.99e-4 (at 243.0 M) against 2.28e-4 at
  M/8 on the same window; the two differences follow each other (judge_long.png panel c).
- H4 HELD: 3.33 card-hours by Slurm elapsed (four segments: 50:05, 50:07, 50:06, 49:29), against ~3.4 from S3.
FV4 (entry 6):
- P1 HOLDS: finite to 299 M (last sample; tlim 300), horizon at every 1 M sample (the finder runs
  every 16 cycles, 1 M at M/4), already at t = 0 on the card (0.9538; the processor smoke S4 found none).
- P2 REFUTED: M_V1L4 - 1 on 100-300 M lies in [-9.86e-3, -7.89e-3], below 0 (predicted +4e-3 to
  +2.5e-2). Over M/4, M/8, M/16 the late offsets change sign twice (q = -7.3 at 100 M, -8.4 at 200 M,
  -9.0 at 300 M); at t = 0 they converge (q = 5.2, order 2.4). So the production-finder offset has no
  mesh order after the gauge transient; no three-member order is quoted from it.
- P3 HOLDS on the measure written into tools/judge_conv.py before FE4 ran but after V-1L4 was seen
  (a description, not a blind test): after removing its secular decline (-8.9e-6 per M on 150-240 M)
  M/4 shows the same plateau switching from 226 M, size +1.25e-4 against +9.2e-5 at M/8 (ratio 1.36).
- P4 HOLDS: 0.59 card-hours (one segment of 35.4 min; predicted 0.45-0.75).
Data and smoke tests (entry 10):
- D1 HOLDS: 4N data D-20261124-130942-29c5de2 has 3402632 dust particles (4.0004 N), N/4 data
  D-20261124-131050-ed0a535 212872 (0.2503 N); lattice rest masses within -1.9e-7 and -5.3e-6 of the
  continuum (N: -4.3e-7); both esf.tab byte-identical to the N data's (cmp).
- S7 HOLDS (D-20261124-131123-05e5bfe): 456 MeshBlocks, 3402772 particles, finder 0.99152073 at t = 0
  (S6: 0.99152073), region.hst written with finite columns, exit 0 in 21 min on one core.
- S8 HOLDS (D-20261124-131125-c928380): the same with 213012 particles, 19 min.
Card runs: FN4 registered as D-20261124-134157-b17938b (cap 4.0, job 5170, held; PROC_NAME D-esflk4n
and MAX_SEGMENTS 7 set in chain/config.sh before its first segment: preemptions consume segments),
queued behind FK in scratch/D-bh-dress/g2long_seq3/. FNQ and FL16 are NOT registered: the G2
allotment has 4.29 card-hours left (nrpic-run budget, 05:17) and FN4 takes 4.0; request to orch
outbox/20261124T134216Z__to-orch__g2-card-allotment.md.

Prediction for FP-ext (before it runs): the tight finder (h1, A16) on the remaining dumps of V-1L
(350, 400, 500 M) and ES-1L (150, 350, 400, 450, 500 M). Seen before writing this: FP's tight V-1L
masses at 100-450 M lie within 1.8e-5 of each other and V-1L16's within 7e-6 (run log of
D-20261124-130935-fdca920). Prediction: (i) V-1L tight |M(t) - M(100)| <= 3e-5 at 350, 400, 500 M;
(ii) the tight null-test difference |D_ES - D_V| <= 5e-5 at every dump 100-500 M [JUDGEMENT: the
production-finder difference of 2.3e-4 is mostly the plateau switching of the two runs at different
times]. Refuted if (ii) exceeds 1e-4 at any dump.

## Entry 12 (2026-11-24 05:46 PST): outcome of test XC; prediction XN for FN4 before it runs

Run D-20261124-134211-c6fce88 (tools/xc_plane.py, 3.6 min on one core; xc_plane.png looked at). Plane
L2 norms on z = 0 of H and |M| (from con_M = g_ab M^a M^b) on A1 = [1.2 r_AH, 6 M], A2 = [6, 30 M],
A3 = [30, 100 M], every con slice (25 M) of V-1L4, V-1L, V-1L16, ES-1L, ES-1L16, ES-FL, ES-FL4 (to 475 M)
and ES-FLK (to 225 M).
- XC1 HOLDS: in every run and annulus the last slice is below 2.2 times its 100 M value (largest:
  ES-FL A2 H 1.59, M 2.16; the vacuum and bubble runs fall to 0.04-1.35 of it), and no norm rises by
  more than a factor 6.5 between two slices after 100 M (V-1L A1: 2.8e-6 at 100 M to 1.85e-5 at 125 M;
  the near-hole annulus carries passing pulses of 3-7 times its running level). ES-FL's A1 annulus is
  empty from 475 M on (1.2 r_AH > 6 M), so its growth there is quoted to 450 M.
- XC2 HOLDS as written, narrowly: the mean of ||H||_A1 over 100-300 M is 7.30e-6 at M/16 against
  7.66e-6 at M/8 (M/4: 1.25e-5). The expected fall by a factor 1.3-3 FAILED (factor 1.05): beyond
  +-3 M the M/8 and M/16 meshes are the same, and A1 reaches to 6 M, so the exterior residual near
  the hole is set by the shared coarser levels, not by the finest one [JUDGEMENT on the cause; no run
  here could fail on it].
- Not predicted, read off the figure: with dust the exterior H residual is about 1e-3 on A1 and 1e-4
  on A2 (ES-FL, ES-FLK), a hundred times the dust-free runs, and four times LOWER at M/4 (ES-FL4: 2.5e-4
  on A1) than at M/8: the residual in the dust behaves like particle sampling noise of the deposit
  (more particles per cell on the coarser mesh), not like truncation error [JUDGEMENT]. The dust-free
  bubble (ES-1L) has 2-4 times the vacuum residual in A2/A3, where its dust wall and shell lie.

Prediction XN (FN4, 4N particles; before it runs, job 5170 held): if the dust residual is sampling
noise of the deposit, ||H|| of the z = 0 plane on A1 and A2 at 100 and 200 M in ES-FLK4N is 0.5 times
ES-FLK's (N^-1/2; between 0.35 and 0.7) [JUDGEMENT]; refuted (not particle noise) if the ratio is
0.9 or more at both times. The same with the region norms H2_out of the 6 and 12 M spheres
(esflk4n.region.hst) against xc_plane's A1/A2 of ES-FLK as a cross-check of the two norms (no bound).

## Entry 13 (2026-11-24 06:19 PST): PAUSED here (pause flag); FP and FP-ext still running, not yet judged

The pause flag appeared at 06:18 PST; nothing new was started after it. Running at that moment, left to
finish on their own (processors; registered): FP D-20261124-130935-fdca920 (24 of 28 probes done, the
last A32 ones running) and FP-ext D-20261124-140606-286a302 (2 of 8). Neither is closed with
`nrpic-run finish` and neither is judged yet: the next session runs `tools/fp_analyse.py --probes
$S/D-20261124-130935-fdca920/fp/probes.json $S/D-20261124-140606-286a302/fpx/probes.json --out
'$NRPIC_RUN_DIR' V-1L=... V-1L16=... V-1L4=... ES-1L=... ES-1L16=...` (registered), looks at
fp_analyse.png, and writes the outcomes of FP1-FP5 and FP-ext (i), (ii) here.
What the run log of FP already shows (raw finder output, not a judgement): the tight finder (h1, A16)
gives V-1L 1.0009973, 1.0009794, 1.0009934, 1.0009933, 1.0009851, 1.0009910 at 100, 150, 200, 250,
300, 450 M (largest |M - M(100)| 1.8e-5) where the run's own finder jumps by 1.2e-4; V-1L16
0.9997965-0.9997994 at 100-300 M; V-1L4 falls from 0.9921716 (100 M) to 0.9900715 (300 M); ES-1L
1.0010193, 1.0010603, 1.0010806, 1.0010687 at 100, 200, 250, 300 M; ES-1L16 0.9997697 (100 M), 0.9997940
(200 M). The production rule from outside (h2) lands on the low plateau and from the stored radius (h0)
reproduces the run to 3e-6. If fp_analyse confirms these, FP2 and FP3 hold (C1 not refuted), and FP-ext
(ii) fails its 5e-5 bound at M/8 (6.5e-5 at 250 M) without being refuted (< 1e-4).
Also open: the ladder schematic (tools/schem_ladder.py, trial in scratch/D-bh-dress/tmp/ladder, looked
at) is not yet a registered run; the draft request to core on the finder's stopping rule is in
scratch/D-bh-dress/tmp/outbox/finder.md (post it after FP is judged).

## Entry 14 (2026-11-24 09:25 PST, lead of batch 11b, resumed after the pause): outcomes of FP and FP-ext

Closed with `nrpic-run finish`: FP D-20261124-130935-fdca920 (84 probes; exit 0, 79 min) and FP-ext
D-20261124-140606-286a302 (24 probes; exit 0, 39 min). Judged by `tools/fp_analyse.py`, registered
D-20261124-172410-e8afc73 and, with only the figure layout changed (legend, title), D-20261124-172508-c847ee4
(fp_analyse.json byte-identical; fp_analyse.png of the second run looked at). Predictions: entry 10 (FP1-FP5),
entry 11 (FP-ext). The raw log had been seen at the pause (entry 13), so the judgement of FP2, FP3 and FP-ext (ii)
is a confirmation from the registered analysis, not blind.

- FP1 HOLDS: h0 (production rule from the dump's radius) reproduces the run's own mass within 3.6e-6 at
  all 29 dumps (largest at ES-1L16 300 M); h1 and h2 find a surface at every dump.
- FP2 HOLDS, C1 NOT REFUTED: V-1L tight |M_h1(t) - M_h1(100)| <= 1.80e-5 at 150-450 M (largest at 150 M),
  M_h1(250) - M_h1(200) = -3.4e-8 (refutation needed >= 8e-5), while the run's own D is +1.20e-4 at 250 M,
  +8.6e-5 at 300 M and +1.21e-4 at 450 M. The plateaus of the vacuum mass are surfaces the production
  stopping rule accepts: from outside (h2, from 2 M) it lands on the low plateau (0.000915-0.000933),
  from the stored radius on whichever the run was on; the tight finder sits between them (0.00098-0.00100).
  So the 1.2e-4 "floor" of the vacuum null test at M/8 is the finder's, not the slice's. [VERIFIED for
  V-1L and V-1L16 on the dumps named; the cause is named after a run in which it could have failed]
- FP3 HOLDS: V-1L16 tight |M_h1(t) - M_h1(100)| <= 3.9e-6 at 200, 250, 300 M (run's own D: +1.34e-4 at 250 M).
- FP4 REFUTED (failed prediction): the converged-finder offsets e = M_h1(A32) - 1 at 200 M are -8.91e-3
  (M/4), +1.18e-3 (M/8), -1.77e-5 (M/16): a sign change, q = -8.4. Their size falls by 7.6 and by 67, so
  the horizon mass does converge toward 1 with the mesh, but not as one power of h (M/4 is outside the
  asymptotic range, or two error terms of opposite sign cancel near M/16) [JUDGEMENT]; no order is quoted.
  Found on the way: the finder's angular truncation A16 - A32 is -1.80e-4, -1.85e-4, -1.85e-4 at M/4,
  M/8, M/16, the same on all three meshes; at M/16 it is ten times the mesh offset. It is a constant
  and cancels in every difference the null test takes.
- FP5 HOLDS: tight-finder null test |D_ES - D_V| <= 6.5e-5 at 200-300 M at M/8 and <= 3.7e-5 at M/16
  (bound 1e-4), against 2.3e-4 (M/8) and 2.0e-4 (M/16) with the runs' own finder.
- FP-ext (i) HOLDS: V-1L tight |M(t) - M(100)| = 2.9e-6, 1.22e-5, 8.5e-6 at 350, 400, 500 M (bound 3e-5).
- FP-ext (ii) FAILED its 5e-5 bound, NOT refuted (< 1e-4): the M/8 tight null difference is 6.8e-5 at
  150 M and then flat, 4.5e-5 to 7.3e-5 at every dump to 500 M (largest 400 M).

Not predicted, read off panel (c): the tight-finder null difference is not a drift but a step between 100
and 150 M that then stays constant to 500 M within +-1.4e-5 (no trend with the expansion), and the step is
about half as large at M/16 (2.3-3.7e-5) as at M/8 (4.5-6.5e-5) [JUDGEMENT: a resolution-dependent step of
the bubble's transient, near first order; two meshes only, no order is claimed]. This is the form the G2
criterion N ("drift of the horizon mass in the vacuum bubble does not exceed the noise floor") should be
judged in: with a converged finder the vacuum floor at M/8 is 1.8e-5 over 100-500 M, the bubble's
difference 7.3e-5 is a one-time step, not a growth with a/a_i.

Consequences: (1) request to core on the stopping rule, posted from scratch/D-bh-dress/tmp/outbox/finder.md
with these numbers; (2) G2 criterion N is restated in stage/G2/OPEN.md with the tight finder as the
measurement and the step as a separate item; (3) new D inputs set `mass_tol_0 = 1e-8` (HANDOFF item 4);
(4) the claim "noise floor 1.2e-4 at M/8" leaves the note: the floor is 1.8e-5 (tight finder, V-1L,
100-500 M) and the production finder's plateau gap of 1.3e-4 is quoted as the finder's.

## Entry 15 (2026-11-24 09:27 PST, before FNQ and FL16 are registered): allotment, restart cadence, two more predictions

Decision 0032 item 3 raised D's allotment by 10 card-hours for runs already designed; `nrpic-run budget`
(09:30) leaves 11.73 card-hours for G2 with FK, FE4, FF4, FN4 reserved. FNQ ES-FLKQ (cap 3.0) and FL16
ES-FL16 (cap 5.0) of entry 10 are registered now (inputs and smoke tests S8, S9 unchanged), held at once
and queued behind FN4 in the sequencer g2long_seq3 (alive, pid 3757609; it reads the queue at every check).
Their predictions are those of entry 10 (Q1-Q3, L1-L4); nothing about them has been seen since.

Restart cadence (decision 0032 item 2, "a restart file at least every ten minutes of wall time"): the
inputs write one every 50 M, which is 14-35 min of card time. Set on the command line through the chain's
EXTRA_ARGS (chain/config.sh, applied to every segment; the registered inputs stay as smoke-tested):
`output2/dt=25` for FN4 (~143 M per card-hour, 10.5 min) and FNQ (~210 M/h, 7 min), `output2/dt=12.5`
for FL16 (~86 M/h, 8.7 min). FN4's first segment has not run (job 5170 held), so its outputs are not
mixed. Disk: about 16, 16 and 24 restart files of 2.6-3 GB (~150 GB; /data has 17 TB free). The denser
dumps also serve as re-search points for the tight finder (entry 14), at no card cost.
Finder: the inputs keep the production finder (mass_tol 1e-5) so that the runs compare with their
parents FK, ES-FL and FF4; the null-test and floor measurements are made by re-searching dumps (FP).

New predictions (before any of the three runs):
XQ (FNQ, N/4): ||H|| of the z = 0 plane (tools/xc_plane.py) on A1 and A2 at 100 and 200 M is 2 times
   ES-FLK's (N^-1/2; between 1.4 and 2.9) [JUDGEMENT, the companion of XN]; refuted (not particle noise)
   if the ratio is 1.1 or less at both times.
L5 (FL16, M/16): ||H||_A1 at 100 and 200 M is at least ES-FL's (fewer particles per cell on the finest
   level, so more deposit noise) [JUDGEMENT, p ~ 0.6]; refuted if it is below 0.8 times ES-FL's at both.

## Entry 16 (2026-11-24 09:31 PST, before the run): test FE (early dumps) - where does the null-test step happen?

Entry 14 found that, with the converged finder, the bubble-minus-vacuum difference is a step between 100
and 150 M (6.8e-5 at M/8) that then stays flat to 500 M. Test FE re-searches the earlier and intermediate
dumps with the same tool and settings as FP (tools/probe_long.py, A16, h0/h1/h2, release processor build
athena_cpu_omp, 2 threads, 2 at a time): V-1L and ES-1L dump 00001 (50 M); V-1L16 and ES-1L16 dumps 00001,
00004, 00005 (50 M and the two dumps between 100 and 200 M, one of which is 150 M; the other is a
wall-time restart). Judged by a new tools/fe_analyse.py together with the FP and FP-ext probes.
With S(t) = (M_ES(t) - M_V(t)) - (M_ES(100) - M_V(100)) from the tight finder (h1):
FE1 (M/8) the step is confined to 100-150 M: |S(50)| <= 2e-5 [JUDGEMENT, p ~ 0.5]; refuted (the
    difference also moves before 100 M) if |S(50)| >= 4e-5.
FE2 (M/16) S(150) lies between 2.0e-5 and 5.1e-5 (0.3 to 0.75 of the M/8 value 6.76e-5, as the halving at
    200-300 M) [JUDGEMENT, p ~ 0.6]; refuted if S(150) >= 6.8e-5 (not smaller than at M/8).
FE3 (sanity) h0 reproduces the run's own mass within 3e-5 at every new dump; the vacuum tight mass moves
    by at most 3e-5 between 50 and 100 M at both meshes.
Cost: 8 one-cycle restarts, ~5.5 min each, two at a time: ~25 min on 4 cores.

## Entry 17 (2026-11-24 09:54 PST): outcome of test FE - the "step" is a dip of the bubble's horizon mass at 100 M

Run FE D-20261124-173137-f358715 (8 dumps, exit 0, 22 min on 4 cores; closed by nrpic-run). Judged by
tools/fe_analyse.py, registered D-20261124-175356-0f40f1a (fe_analyse.png looked at). Prediction: entry 16.
(The dumps es1l16.00004/.00005 and v1l16.00004/.00005 turned out to be 150 M and a wall-time restart;
the ES-1L16 wall-time dump and the V-1L16 one at 166.66 M do not pair, so M/16 has 50, 100, 150, 200,
250, 300 M.)

- FE1 FAILED its bound, NOT refuted: S(50) = +3.47e-5 at M/8 (bound 2e-5, refutation 4e-5).
- FE2 FAILED its bound, NOT refuted: S(150) = +5.45e-5 at M/16 (window 2.0-5.1e-5, refutation 6.8e-5);
  the M/16-to-M/8 ratio at 150 M is 0.81, not 0.3-0.75.
- FE3 HOLDS: h0 reproduces every run's mass within 5.9e-6 at the new dumps; vacuum tight mass moves by
  6.9e-6 (M/8) and 1.6e-6 (M/16) between 50 and 100 M.

What the figure shows (panel b): the vacuum horizon masses are flat to within 2.5e-5 from 50 to 500 M
at both meshes; the BUBBLE's horizon mass has a dip at 100 M, 4.2e-5 (M/8) and 5.8e-5 (M/16) below its
50 M value, and is back by 150 M. Referenced to 50 M instead of 100 M, the bubble-minus-vacuum
difference over 150-500 M lies in [+1.0, +3.8]e-5 at M/8 and [-3.3, -0.2]e-5 at M/16, with no trend in
time. So the "step by 150 M, half as large at M/16" of entry 14 (a reading, not a prediction) is
withdrawn: it was the reference time falling into the dip. The dip does not shrink from M/8 to M/16
[VERIFIED on these dumps]; the meshes differ only inside +-3 M, so the dip may come from the shared
coarser levels (a gauge pulse from the bubble wall reaching the hole) [JUDGEMENT; no run here could
fail on it - FE4 at M/4, whose finest level is coarser, can: a dip of the same size there would point
to the coarse levels, a larger one to the finest].
In the exact solution the bubble interior is Schwarzschild (Birkhoff) and a spherical marginally trapped
surface sits at r = 2M on every spherical slice, so any dip or band is numerical [BACKGROUND].

For G2 (criterion C7): with the converged finder, |D_ES - D_V| <= 7.3e-5 at M/8 over 100-500 M and
<= 5.5e-5 at M/16 over 100-300 M (reference 100 M, as criterion N); <= 3.8e-5 and <= 3.3e-5 with the
reference at 50 M. Both are below the production-finder floor and show no growth with the expansion.
Next for this item: the tight re-search of FE4's dumps (M/4) when it ends, with S(t) at three meshes.

## Entry 18 (2026-11-25 03:55 PST, lead of batch 17, before the registered readings): FK ended; plan

State: FK ES-FLK (D-20261123-022725-a553496) ran to tlim 400 M (chain DONE, job 5243 ended 2026-11-24
20:45 PST after ten segments, many cut by preemption). FF4 and FE4 ran to tlim earlier (DONE, not yet closed).
FN4 ES-FLK4N (job 5280, segment 7) is at 389.5 M of 400; FNQ ES-FLKQ (job 5279, segment 1 of the in-place
continuation) at 135.5 M of 400; FL16 still waits (q0011). Closing: `nrpic-run finish` refuses FK because
its manifest carries `continuations` (written by tools/continue_chain.sh): new tools/close_by_hand.py runs
nrpic-run's own chain-close code (status, wall, sacct card-hours, sha256sums) and writes the manifest; FF4
and FE4 close with nrpic-run finish.

Readings of this session (predictions unchanged from entry 6: P7-P11 for FK; entries 10, 12, 15: N1-N3, XN,
Q1-Q2, XQ for FN4/FNQ):
- tools/fk_compare.py (new, written after FK ended): FK and ES-FL read by the same code (the reading of
  g2runs/tools/esf_criteria.py), P7 (common finder times <= 219 M), P8 (reasons of dust removals), P9 ((iii)
  bin medians with lo >= 280 M, D3 margin after 220 M), P10 (M_AH at the last sample 399.5 M). A smoke run
  of the tool on the FK data was made at 03:50 to fix the figure layout (scratch tmp/fk_smoke, not a
  result); the judgement below uses the registered run only.
- g2runs/tools/esf_criteria.py --base esflk (criterion G for FK itself, as for ES-FL).
- tools/np_partial.py (new): PARTIAL particle-number reading. Running chains are cut at their second-newest
  restart time (what follows the newest restart of a preempted chain is written again); FK is read whole.
  N2/Q2 (removed m E_K against FK), N3 (M_AH against FK), (iii) bins on the removals before the cut. Labelled
  partial; N1-N4, Q1-Q3 are judged only when the runs end and are closed. A smoke run on the data was made
  at 03:52 (tmp/np_smoke) to debug the cut.

## Entry 19 (2026-11-25 04:00 PST, lead of batch 17): outcome of FK; partial particle-number reading

FK ES-FLK D-20261123-022725-a553496 closed by hand (tools/close_by_hand.py; completed, exit 0; 2.70
card-hours by sacct over 11 jobs, 39.3 GB checksummed). Judged by tools/fk_compare.py, registered
D-20261125-115637-7ee26c1 (fk_compare.png looked at), and criterion G of FK itself by
g2runs/tools/esf_criteria.py --base esflk, registered D-20261125-115647-fd2f3f7 (esf_criteria.png looked at).
Predictions: entry 6.
- P7 HOLDS: max |M_FK - M_ES-FL| over the 439 common finder times t <= 219 M is 1.8e-6 (at 1.5 M; zero to
  round-off from 50 to 219 M). After ES-FL's excision ends the difference grows to +2.8e-5 near 330 M and is
  +2.2e-5 at 399.5 M (one spike of 1.5e-5 near 248 M).
- Excision: ES-FL's smallest horizon radius passes 4 x 0.8 = 3.2 M at 219.5 M; FK's reaches 4.53 M at
  399.5 M, below 6.4 M, so FK excises to its end.
- P8 HOLDS: all 119848 dust removals of FK are by reason 3; ES-FL removed 54944 by reason 2 and 63344 by
  reason 3 up to 399.5 M.
- P9 HOLDS (the mechanism test): FK's (iii) medians in the bins from tau_rem = 280 M to 500 M lie in
  [+0.162, +0.243] per cent (ES-FL in the same range: up to +0.620 per cent); none above the refutation
  line +0.45 per cent. The D3 margin of the removals after t_rem = 220 M is at most 2.88e-3 (bound 3e-3,
  narrowly; ES-FL 8.6e-3). So the step of ES-FL's (iii) medians to +0.6 per cent at tau_rem ~285 M and its
  D3 jump after 220 M ARE caused by the end of horizon excision at 4 x initial_radius [VERIFIED: a run in
  which it could have failed; the step is absent when excision stays on].
- P10 HOLDS: M_FK(399.5) = 1.491638, 3.6e-4 below ES-FL's 1.4920 (bound 3e-3): how deep the matter is
  removed inside the horizon does not move the horizon mass.
- P11 FAILED: 2.70 card-hours against 1.8-2.4 (the run was preempted many times; sacct counts the repeated
  stretches between restarts).
- Criterion G for FK alone HOLDS to its end: 50 counted (iii) bins to tau_rem 500 M, largest |median|
  0.249 per cent; D2 at all 760 samples after 20 M; D3 no violation (min margin -1.4e-4). D1 closure with
  the control subtracted 2.2e-3 at 399.5 M (ES-FL: 9.4e-3 at 500 M).
- NOT predicted, read off panel (d): 29.5 per cent of FK's removals have tau_rem below the exact horizon
  crossing tau_H(R0) (min -0.50 M, none below -1 M; median +0.127 M), against 0.23 per cent in ES-FL (min
  -0.084 M). The excision radius is 0.8 x rr_min in both (nrpic.cpp:446-460), and the masses agree to
  1.8e-6 before 219 M, so the cause is not known [TO VERIFY: D4 of both runs restricted to t_rem <= 219 M;
  the restart rule "rr_min is -1 until a search of this run has succeeded" (nrpic.cpp:448-450) acts after
  every one of FK's ten resumptions]. It does not touch a criterion (D4 has no bound; D3 holds).

Partial particle-number reading, tools/np_partial.py, registered D-20261125-115729-011d028 (np_partial.png
looked at). FN4's chain ended (tlim 400 M, job 5280) at 03:55:32, two minutes before this reading, so FN4
is read whole; it was not yet closed (its close by hand runs now). FNQ is cut at its second-newest restart,
125 M. Labelled PARTIAL for FNQ; N1-N4 are judged in full below when FN4 is closed.
- N2 HOLDS (FN4, read before the close): removed m E_K relative to FK at 100, 200, 300, 399.5 M: -0.39,
  +0.30, +0.21, +0.08 per cent (bound 1 per cent). At 50 M +1.24 per cent (not a named time).
- N3 HOLDS for the bound: |M_4N - M_N| at 100, 200, 300, 399.5 M = 3.7e-4, 3.6e-4, 9.4e-6, 4.9e-4 (bound
  2e-3); the curve has noise of about 1e-3 peak to peak (left panel), fifty times the FK - ES-FL difference.
  The ordering part has one time so far (FNQ): at 100 M |M_4N - M_N| = 3.7e-4 < |M_N - M_N/4| = 1.43e-3.
- Q2 PARTIAL, holds so far: FNQ's removed m E_K at 100 M is -0.86 per cent off FK's (bound 3 per cent).
- (iii) PARTIAL: FNQ 18 counted bins to tau_rem 180 M, largest |median| 0.265 per cent (Q1 bound 2 per cent).

## Entry 20 (2026-11-25 04:12 PST, lead of batch 17): outcome of FF4 (M/4 member of the growth)

FF4 ES-FL4 D-20261123-022727-1c17e73 closed by nrpic-run finish (completed, 1.34 card-hours, 174 files).
Read with g2runs/tools/esf_criteria.py --base esfl4 --tau_max 650 twice: with the control V-1L (M/8) as in
the ES-FL reading, D-20261125-121034-8f82998, and with the control at the same mesh, V-1L4 (FV4, the M/4
vacuum run made for this purpose in entry 6), D-20261125-121123-143a007 (esf_criteria.png looked at). The
choice of the same-mesh control is made here, after the first reading was seen [JUDGEMENT; labelled so].
Predictions: entry 6.
- P12 HOLDS with the same-mesh control, FAILED with the M/8 control: (iii) 60 counted bins to tau_rem
  650 M, largest |median| 0.685 per cent (bound 1, refutation 2); D2 holds at all 480 samples with V-1L4,
  fails at 207 of 480 with V-1L (largest excess 5.4e-3: the M/4 horizon mass sits ~8e-3 below M/8's, the
  finder offset of the coarse mesh, FP4). The (iii) medians step from about -0.45 per cent to about 0 at
  tau_rem ~290 M: the same end-of-excision step as ES-FL, of the same size, in the other direction.
- P13 FAILED as written: with Delta M = M_AH(t) - M_AH(0) the M/4 growth is 43, 20, 13, 9.9 per cent below
  ES-FL's at 100, 200, 300, 400 M, because the M/4 finder's t = 0 mass is 1.0330 (M/8: 0.9915; smoke test S4
  expected [0.85, 1.0]). The absolute masses differ by -7.9e-3 to -8.0e-3 over 100-400 M (0.5-0.7 per cent
  of M). The excision switch part HOLDS: 225.0 M against ES-FL's 219.5 M (within 10 M).
- P14 HOLDS: 1.34 card-hours (0.9-1.4).
- Not predicted: D3 fails at M/4 with either control (with V-1L4: 1704 of 146616 removals below -3e-4, min
  -1.66e-3, all at t_rem < 30 M, panel c); D1 closure -3.1e-2 raw (ES-FL +1.8e-2). D4: every removal 0.22 to
  3.8 M of proper time after the exact crossing (ES-FL: median 0.26 M): the coarse horizon removes later.
So criterion G ((iii) and D2) holds at M/4 and M/8 with the control of each mesh; the growth has a third mesh
member when FL16 (M/16, q0011) runs. A mesh ORDER of the growth needs a reference time after the t = 0
transient (L3 uses Delta M from 20 M, entry 10).

## Entry 21 (2026-11-25 04:25 PST, lead of batch 17): outcome of FE4 (M/4 member of the null test)

FE4 ES-1L4 D-20261123-022726-1b133af closed by nrpic-run finish (completed, 0.83 card-hours). Judged by
tools/judge_conv.py with ES-1L4 added, registered D-20261125-122227-3eb563a (judge_conv.png looked at).
Prediction: entry 6.
- P5 REFUTED: at M/4 the bubble-minus-vacuum difference D_ES1L4 - D_V1L4 grows steadily from 100 M to
  4.57e-3 at 299 M (panel c), twenty times the M/8 difference (2.28e-4) and above criterion N's threshold
  from about 105 M on; it departs from the M/8 difference by more than 2e-4 for 189 M. The prediction that
  the difference does not depend on the horizon resolution is wrong at M/4. At M/8 and M/16 the two curves
  lie on each other (2.3e-4 and 2.0e-4, entry 5, H3).
- P6 FAILED narrowly: 0.83 card-hours against 0.5-0.8.
- Reading [JUDGEMENT; no run here could fail on the cause]: the M/4 horizon (radius ~2 M, 8 cells) sits
  where the finder offset itself is -8e-3 (P2 refuted, FP4) and the vacuum M/4 mass declines secularly
  (P3's detrended line, slope -8.9e-6 per M on 150-240 M); in the bubble the same mesh lets the mass grow.
  So the null test converges only from M/8 on: M/4 is outside the convergent regime, M/8 and M/16 agree at
  the floor. For criterion N's three-way convergence this is the third member, and it fails; the statement
  for G2 is "N holds at M/8 and M/16, and fails at M/4 by a factor 20" (stage/G2 C1, C2, C7).
- The tight re-search of FE4's dumps (dip at 100 M, entry 17) is still to do; with a 4.6e-3 drift at M/4
  the dip of 4-6e-5 is not measurable there and the item is dropped.

## Entry 22 (2026-11-25 04:31 PST, lead of batch 17): FN4 closed; N1, N4 and XN

FN4 ES-FLK4N D-20261124-134157-b17938b closed by hand (tools/close_by_hand.py; completed, 3.19 card-hours by
sacct over 8 jobs, 59.4 GB checksummed). Predictions: entries 10 (N1-N4) and 12 (XN).
- N1 HOLDS (esf_criteria --base esflk4n with the 4N data, registered D-20261125-122827-c5735f8): 50 counted
  (iii) bins to tau_rem 500 M, largest |median| 0.239 per cent (FK: 0.249); D2 at all 760 samples; D3 no
  violation (min margin +1.75e-4); all 479200 dust removals by reason 3; D1 closure with the control
  subtracted 2.3e-3 at 399.5 M (FK 2.2e-3).
- N2, N3 (read in entry 19 before the close, unchanged by it: the outputs are those of the ended chain) HOLD.
- N4 HOLDS: 3.19 card-hours (2.3-3.4).
- XN HOLDS (xc_plane on ES-FLK and ES-FLK4N, registered D-20261125-122849-43db157, xc_plane.png looked at):
  the 4N/N ratio of ||H|| on the z = 0 plane is 0.491 (A1) and 0.464 (A2) at 100 M, 0.426 and 0.447 at 200 M,
  all inside [0.35, 0.7] around N^-1/2 = 0.5; ||M|| alike (0.43-0.53). So the exterior constraint residual
  near the hole in the dust runs is particle sampling noise of the deposit [VERIFIED: a run in which it could
  have failed]. Not predicted: on A3 (30-100 M) the ratio is 0.93-0.96 at 100-200 M (that residual is not
  particle noise), and on A1 the N run's norm grows to 2.0e-3 by 400 M while the 4N run's stays near 6e-4.
- Not predicted: FN4's D4 also shows 34.4 per cent of removals before the exact crossing (min -0.66 M, none
  below -1 M), like FK (29.5 per cent) and unlike ES-FL (0.23 per cent): the early removal goes with the
  ES-FLK set-up (initial_radius_0 1.6), not with the particle number [TO VERIFY: cause].
The particle sequence now has N and 4N complete; N/4 (FNQ, q0010) runs.

## Entry 23 (2026-11-25 07:59 PST, lead of batch 20, processors only): predictions before the readings

Three readings of registered outputs, written before each analysis runs.

**H, horizon searches (decision 0040 item 3).** Facts, not predictions: no D input sets `<fastflow>
diagnostics` (grep of g2long/inputs, es_runs/inputs), and no `horizon_status_*` file exists under
scratch/D-bh-dress (find, 0 files): every D run, card and processor, was made WITHOUT the diagnostics.
So the recheck uses the two signatures that the source fixes [VERIFIED by reading athenak/src/z4c/
fastflow.cpp:228-231 and 455-474]: the summary line writes `ah_prop[]`, which is set only by an accepted
surface and is NaN until the first one of a process; a failed search therefore writes NaN (no surface
accepted yet in this process, e.g. the first search after a restart) or the bit-identical values of the
predecessor line. Disclosed: before writing this entry I counted V-1L's file once by hand (1000 lines, one
bit-identical repeat, at 0.5 M); that count is not a prediction.
- H1: in every G2 production summary (V-1L, V-1L16, V-1L4, ES-1L, ES-1L16, ES-1L4 FE4, ES-FL, FF4, FK,
  FN4, FNQ partial) failed searches are fewer than 1 per cent of the lines after 20 M; on the V-1L and
  V-1L16 plateaus (230-500 M) none. Refuted if any plateau line is a repeat or NaN, or any run has >= 1
  per cent failed lines after 20 M.
- H2: every re-search probe of FP and FP-ext (one fresh search per horizon per dump) is found: one finite
  line per horizon (a failed first search would write NaN). For the four V-1L dumps (100, 250, 400, 500 M)
  that core searched again with the diagnostics (core-20261125-144142-5858c3d, status found = 1), D's
  tight-rule mass equals core's horizon-1 mass bit for bit. Refuted by a NaN line or a difference.
- H3: the numbers of criteria G and N do not move in their quoted digits when failed lines are dropped:
  fewer than 1 per cent of the removals take M_AH from a repeated line (first sample >= t_rem).
  Refuted if >= 1 per cent do, or a quoted maximum changes in its second digit.

**R, region norms of FN4 (C3, C11).** Shells from the sphere norms (sqrt<H^2> is volume-weighted, so
H2^2 V adds): S_A1 = [1.2 r_AH, 6 M] (horizon sphere and sphere 1), S_A2 = [6, 30 M] (spheres 1 and 3).
- R1: V_in + V_out = V at every record to 1e-10 relative; every column finite.
- R2: FN4's shell norms at 100 and 200 M lie within a factor 2 of FN4's z = 0 plane norms on the same
  annuli (xc_plane D-20261125-122849-43db157: A1 4.06e-4 at 100 M) [JUDGEMENT: the plane is a section of
  the same shell; the volume weight favours its outer part, so the shell norm may be lower]. Refuted if
  the two differ by more than a factor 3.
- R3: FNQ (N/4) over FN4 (4N) shell-norm ratio at 100 M (FNQ readable to its second-newest restart) is 4
  (N^-1/2 over a factor 16), inside [2.8, 5.6]; refuted (not particle noise) if <= 1.5.

**T, the D4 timing (entries 19, 22).** D4 = tau_rem - tau_H(R0) per removed dust particle. Before 219 M
ES-FL and FK remove by the same rule (horizon excision inside 0.8 rr_min; their horizon masses agree to
1.8e-6), after it ES-FL removes by the lapse rule further in.
- T1: restricted to t_rem <= 219 M, FK's fraction below 0 is that of ES-FL within a factor 2 and at most
  1 per cent in both, minima within 0.1 M: FK's 29.5 per cent (FN4's 34.4) comes from the removals after
  219 M, where FK keeps excising at 0.8 rr_min soon after the exact crossing while ES-FL removes deeper.
  Refuted if FK's fraction before 219 M is 5 per cent or more (then the early removal has another cause,
  e.g. the restart rule rr_min = -1 of nrpic.cpp:448-450).
- T2: after 219 M FK's and FN4's fractions below 0 are larger than their whole-run values (29.5, 34.4).

**Ruling 0039 item 4, decided here (no run).** The mesh leg of the null test is stated with two members
(M/8, M/16) and no order, and no M/12 member is queued. Reason [JUDGEMENT]: with the converged finder the
bubble-minus-vacuum difference is at the floor at both meshes (<= 7.3e-5 at M/8 on 100-500 M, <= 5.5e-5 at
M/16 on 100-300 M, no trend; fp_analyse D-20261124-172508-c847ee4): there is no error above the floor
whose order a third member could measure; an M/12 pair (bubble and vacuum) would add a third number at
the floor for up to four card-hours in a week the usage ruling (0040 item 5) keeps tight and with the
cards held since the morning. M/4 stays outside the regime (0039 item 4).

## Entry 24 (2026-11-25 08:05 PST, lead of batch 20): outcomes of H, R, T

**H (horizon searches; hz_check D-20261125-160142-b1c51b5, figure of record D-20261125-160241-2b7ba3b,
hz_check.png looked at; D-20261125-160123-f86d73c failed on the status-line comment, on record).**
- H1 HOLDS. Over 13 summaries (the 11 of entry 23 and the G1 pair V-1B, ES-1) every failed search lies
  before 5 M: one bit-identical repeat at 0.5-1 M in V-1L, ES-1L, ES-FL, FK, FN4, FNQ, V-1B, ES-1; three at
  1, 2, 4 M in V-1L4 and ES-1L4; in FF4 NaN at 0-3 M (no surface accepted before 4 M) and a repeat at 5 M.
  After 20 M: zero failed lines in every run (panel c); the V-1L and V-1L16 plateaus (230-500 M, 540 and
  280 lines) are found surfaces of the loose stopping rule, not repeats (panel a).
- H2 HOLDS. 36 probes of FP/FP-ext, one finite line per horizon each (a failed first search writes NaN).
  At the four V-1L dumps core searched with the diagnostics (core-20261125-144142-5858c3d) the status says
  found (129 flow iterations) and D's tight masses equal core's bit for bit (100, 250, 400, 500 M).
- H3 HOLDS. No removal of ES-FL, FF4, FK, FN4, FNQ takes M_AH from a failed line (0 of 147512, 146672,
  119640, 478752, 26392); criterion N recomputed on found lines only: 2.28e-4 (M/8), 1.99e-4 (M/16),
  4.57e-3 (M/4), unchanged.
- Without the diagnostics, all of them (stated beside every horizon number of the package): every D card
  and processor run. The "found" verdicts above rest on the signature, which the source makes complete
  (ah_found reset at each search, fastflow.cpp:777; ah_prop written only after an accepted surface,
  :925-935) [VERIFIED by reading]; four dumps also by a status file (core's run).

**R (region norms; region_norms D-20261125-160355-bda7e38, region_norms.png looked at).**
- R1 HOLDS for the identity (V_in + V_out = V to 3.9e-16 in FN4, 5.2e-16 in FNQ); FAILED as written for
  "every column finite": Hmax_in_h0 is NaN at t = 0 in both (the horizon sphere is empty before the first
  search). Harmless; on record.
- R2 HOLDS: FN4's shell norm over its own plane norm is 0.82 (A1) and 0.61 (A2) at 100 M, 0.74 and 0.52 at
  200 M, lower as foreseen (volume weight), within a factor 2.
- R3 HOLDS: FNQ/FN4 = 3.91 (A1) and 3.46 (A2) at 100 M; 3.4-4.4 on A1 and A2 at 50-300 M: the constraint
  residual outside the hole to 30 M is particle noise of the deposit (N^-1/2) [VERIFIED: a run in which
  it could have failed]. Not predicted: on [30, 60] M (the dust edge) the ratio is 1.1 to 150 M and rises
  to 2.4 by 300 M (deterministic residual early, as XN's A3 0.93-0.96); outside 60 M (no dust) it is
  1.000 (vacuum residual identical). FNQ read to 350 M (its second-newest restart; chain running).

**T (D4; d4_timing D-20261125-160450-9326390, d4_timing.png looked at).**
- T1 HOLDS for FK and ES-FL: before 219 M none of the 63344 dust removals of either precedes the exact
  crossing; minimum +0.0715 M and median +0.180 M in both, the same to 1e-8 M (the same removals). FK's
  29.5 per cent all come after 235 M: per 10 M bin 5 per cent at 240 M, 62 per cent at 280 M, 96-100 per
  cent from 330 M (panel c). So the FK/ES-FL difference of entry 19 is the removal rule after 219 M (ES-FL
  removes by the lapse rule, later) [VERIFIED by this split]. FAILED for FN4 as an extension of the
  bound: 3.4 per cent of its removals before 219 M precede the crossing (from 170 M on, min -0.108 M),
  above the 1 per cent written for FK and ES-FL, below the 5 per cent refutation.
- T2 HOLDS: after 219 M, FK 62.6 per cent (min -0.364 M), FN4 69.2 per cent (min -0.663 M), all by reason 3.
- Open [TO VERIFY]: why horizon excision at 0.8 rr_min removes dust up to 0.66 M of proper time before the
  exact LTB crossing once the hole has grown, and why the onset moves from ~235 M (N) to ~170 M (4N). No
  criterion depends on it (D4 has no bound; (iii), D2, D3 hold); not named as a cause.

## Entry 25 (2026-11-25 21:45 PST, lead of batch 25, before any reading of the ended runs): plan and predictions

State: both chains ended at tlim (chain STATUS DONE): FNQ ES-FLKQ D-20261124-172725-2f426b6 at 400 M
(job 5293, 10:02 PST), FL16 ES-FL16 D-20261124-172745-72472ed at 300 M (job 5347, 20:09 PST). Nothing of
FNQ after 350 M and nothing of FL16 has been read. Both are closed with `nrpic-run finish` (started
21:41 in the background, one after the other) before any reading below.

Judged with the predictions written before the runs (entries 10 and 15), unchanged: Q1-Q3 and XQ for FNQ;
L1-L5 for FL16 (L3 with Delta M(t) = M_AH(t) - M_AH(20 M)). Readers (all registered, each figure looked at):
g2runs/tools/esf_criteria.py (Q1 with FNQ's data D-20261124-131050-ed0a535 and control V-1L; L2 with ES-FL's
data D-20261121-203042-82deeec and the same-mesh control V-1L16 D-20261121-203151-37e7b2d, as entry 20 judged
each mesh against its own-mesh vacuum control); np_partial.py (FNQ whole now: Q2, N3's ordering);
xc_plane.py (XQ: ES-FLK against ES-FLKQ; L5: ES-FL against ES-FL16); region_norms.py without --running;
hz_check.py on FNQ and FL16 (decision 0041 item 4: made without the diagnostics, rechecked by the signature).

New reader tools/conv3.py (written now, before it runs): the three-way convergence of item C2 in one
figure, (a) particle number N/4 (FNQ), N (FK), 4N (FN4) at 100, 200, 300, 399.5 M; (b) mesh of the growth
M/8 (ES-FL), M/16 (FL16), with M/4 (FF4) drawn and labelled "outside the convergent regime" (ruling 0039
item 4), Delta M from 20 M; (c) the same mesh members with each own-mesh vacuum control subtracted (as D2).
Predictions for what conv3 adds (beyond N3 and L3, which stand as written):
C2a (particle) |M_4N - M_N| <= |M_N - M_N/4| at three of the four times (this is N3's ordering, p ~ 0.6).
C2b (mesh, two members in the regime) |Delta M_16 - Delta M_8| <= 3e-3 (D2's tolerance) at 100, 200 and
    300 M [JUDGEMENT]; refuted above 3e-3 at any of them. No order is claimed from two members.
C2c (horizon searches, decision 0041 item 4) in FNQ (whole) and FL16 no failed search after 20 M by the
    signature (NaN or bit-identical repeat); refuted by any such line after 20 M.

## Entry 26 (2026-11-25 21:49 PST, lead of batch 25): outcomes of FNQ (Q1-Q3, XQ, R3 to 400 M)

FNQ ES-FLKQ D-20261124-172725-2f426b6 closed by `nrpic-run finish` (completed, exit 0; 168 files, 51.1 GB
checksummed; 1.90 card-hours by sacct over 4 jobs, one continuation in place). Predictions: entries 10, 15.
Horizon masses below are from a run made without `<fastflow> diagnostics` (decision 0041 item 4).
- Q1 HOLDS (esf_criteria D-20261126-054616-a13a888, esf_criteria.png looked at): 50 counted (iii) bins to
  tau_rem 500 M, largest |median| 0.290 per cent (bound 2; FK 0.249, FN4 0.239); D2 at all 760 samples after
  20 M; all 29984 dust removals by reason 3; D1 closure with the control subtracted 2.7e-4 at 399.5 M.
  Not predicted: D3 fails at N/4 (8352 of 29984 removals below -3e-4, min margin -8.6e-4, all after
  ~220 M, panel c), where FK and FN4 hold it; D4 41 per cent before the exact crossing (min -0.669 M).
- Q2 HOLDS (np_partial D-20261126-054636-93618ee, FK, FN4, FNQ all read whole; np_partial.png looked at):
  FNQ's removed m E_K relative to FK at 100, 200, 300, 399.5 M: -0.86, +0.49, +0.47, +0.28 per cent
  (bound 3). The tool's labels still say "partial" (its json label and panel title); every run was read
  whole (chain_done true, t_cut 399.5 M for all three): a label defect of the reader, not of the numbers.
- Q3 HOLDS: 1.90 card-hours (1.6-2.3).
- N3's ordering (C2a) HOLDS at all four times: |M_4N - M_N| = 3.7e-4, 3.6e-4, 9.4e-6, 4.9e-4 against
  |M_N - M_N/4| = 1.43e-3, 3.9e-4, 3.9e-4, 5.9e-4 at 100, 200, 300, 399.5 M (narrowly at 200 M). The
  FNQ - FK curve carries noise of +-3.7e-3 peak (left panel), about 3.5 times FN4's, so the single-time
  ordering is a weak statement; conv3 adds window rms values.
- XQ HOLDS (xc_plane D-20261126-054718-afa783e, xc_plane.png looked at): N/4 over N of ||H|| on the
  z = 0 plane = 1.89 (A1) and 1.65 (A2) at 100 M, 1.85 and 1.77 at 200 M, all in [1.4, 2.9] around
  N^1/2 = 2 (||M|| 1.70-2.31). On A3 (30-100 M) 0.98 and 1.14 (deterministic residual early, as XN),
  rising to 2.1 at 400 M. The three particle numbers order cleanly on A1 and A2 at every slice.
- R3 to the end (region_norms D-20261126-054736-10c837a, both runs whole; region_norms.png looked at):
  FNQ/FN4 on [1.2 r_AH, 6 M] and [6, 30] M stays in 3.2-5.2 from 20 to 400 M (3.41-4.39 at the named
  times 50-300 M, unchanged from entry 24); [30, 60] M rises from 1.1 to ~4 by 400 M; outside 60 M 1.000.

FL16 ES-FL16 D-20261124-172745-72472ed closed by `nrpic-run finish` (completed, exit 0; 180 files, 85.9 GB
checksummed; 3.66 card-hours by sacct over 8 jobs, one continuation in place). Predictions: entries 10, 15.
Made without `<fastflow> diagnostics` (decision 0041 item 4).
- L1 HOLDS: finite to 300 M (finder to 299.75 M, no gap above 1 M, every finder value finite; 763140
  particles kept, none escaped; esf_criteria P6) and a horizon at every sample (hz_check below).
- L2 HOLDS (esf_criteria D-20261126-055158-30ae09c with ES-FL's data and the same-mesh control V-1L16;
  esf_criteria.png looked at): 38 counted (iii) bins to tau_rem 380 M, largest |median| 0.485 per cent
  (bound 1); D2 at all 1120 samples after 20 M; D3 holds (min margin -1.5e-4); D4 every removal after the
  exact crossing (min +0.227 M). The (iii) medians step from ~+0.1 to ~+0.48 per cent at tau_rem ~285 M,
  and the D3 margin jumps at t_rem ~220 M: the end of horizon excision at 4 x initial_radius, as in ES-FL
  (entry 19; 24112 removals by reason 2, 63416 by reason 3).
- L4 HOLDS: 3.66 card-hours (3.0-4.0).
- L5 HOLDS (xc_plane D-20261126-055159-6c40115, xc_plane.png looked at): ||H||_A1 of M/16 over M/8 = 2.11
  at 100 M and 1.08 at 200 M (refuted only below 0.8 at both); A2 1.11 and 1.06; A3 1.00 and 1.02. The
  M/16 excess on A1 fades by ~220 M and is 1.00 at 300 M.
- C2c HOLDS (hz_check D-20261126-055208-4e0fd0e, hz_check.png looked at): FNQ one bit-identical repeat
  at 1 M, none after; FL16 no failed search in 1252 lines. No failed search after 20 M in either.

## Entry 27 (2026-11-25 21:58 PST, lead of batch 25): the three-way convergence of item C2 (L3, C2a, C2b)

conv3 registered twice: D-20261126-055207-0137c53 read the mesh members only at 100 and 200 M, because the
common end of FL16 and its control V-1L16 is 299 M and the reader skipped the named 300 M. The reader was
changed after that reading (a named time at most 1.5 M past the common end is read at the end and
labelled; commit after a13a888) and rerun as D-20261126-055249-505b079 (conv3.png looked at); this change
is post hoc and labelled so; the 100 and 200 M numbers are identical in both runs.
- C2a (particle number) HOLDS at all four times (entry 26). Not predicted: the rms over +-25 M windows of
  M_N - M_N/4 is 0.85, 1.19, 1.49, 1.31e-3 and of M_4N - M_N 0.27, 0.48, 0.59, 0.70e-3 at 100, 200, 300,
  399.5 M: ratios 3.1, 2.5, 2.5, 1.9, against sqrt(5/1.25) = 2 for independent sampling noise scaling as
  N^-1/2 [JUDGEMENT]. The horizon mass converges in particle number with the noise of the deposit.
- L3 HOLDS as written: |Delta M_16 - Delta M_8| = 4.4e-4, 1.2e-4, 8.6e-5 against |Delta M_8 - Delta M_4| =
  1.24e-3, 9.4e-4, 1.22e-3 at 100, 200, 300 (read at 299) M. Ruling 0039 item 4 puts M/4 outside the
  convergent regime, so this ordering is NOT an order of convergence and none is claimed.
- C2b HOLDS: the two members in the regime agree in Delta M to 4.4e-4, 1.2e-4, 8.6e-5 (bound 3e-3); with
  each own-mesh vacuum control subtracted 3.6e-4, 2.9e-5, 1.3e-5. Window rms of the M/16 - M/8 difference
  3.2-6.3e-4. Not predicted: the raw difference rises from 0 to about +5e-4 by 150 M and stays there
  (panel b), a systematic offset the size of the finder noise; the M/4 member departs by -1 to -2e-3 raw
  and by up to -4e-3 with its control off (panel c), outside the D2 band after ~200 M.
Statement for item C2: particle number, three members N/4, N, 4N, ordered, with N^-1/2 noise; mesh of the
growth, two members in the regime (M/8, M/16) that agree to 4.4e-4 or better, M/4 drawn and labelled
outside the regime; mesh of the null test, two members and no order (ruling 0041 item 4); boundary, three
face distances (boundary_gauge D-20261124-131657-89cd963); gauge, plain 1+log only (the relaxed lapse
cannot serve, OPEN.md section 2). Every horizon number made without the diagnostics, rechecked by the
signature (entries 24, 26).
