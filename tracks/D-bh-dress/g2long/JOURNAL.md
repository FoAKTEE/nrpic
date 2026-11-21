# JOURNAL of g2long (Track D: long card runs toward G2, plain 1+log)

Package of the D-bh-dress lead, batch 5 (2026-11-21, decision 0025 items 3-5). Newest at the
bottom. Inputs: `inputs/*.athinput`, built by `tools/make_inputs.py` (its self-check rebuilds
V-1B of drift_controls from V-1 exactly). Executable of every card run: release core-v0.6,
`/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena`. No run sets `lapse_leak`.

## Entry 1 (2026-11-21 12:50 PST, before any run): design, criteria and predictions

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
