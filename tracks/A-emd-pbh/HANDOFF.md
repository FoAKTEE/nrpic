# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 41 (wave 3), 2026-11-28 ~08:40 PST.

State in three lines: G0 and G1 are signed. Gate G2 was NOT PASSED (decision 0047); the second review is limited to
conditions (a)-(d), whose state is in stage/G2/OPEN.md: (a) NOT met (mesh A 0.907 at detection; mesh B queued),
(b) met, (c) PARTLY (first order confirmed, c ~ 1.5; ruling asked), (d) NOT met (box violation not mesh-limited).

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short &&
harness/bin/nrpic-queue list | grep A-emd; harness/bin/nrpic-ctx inbox; test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `threshold_ball/JOURNAL.md` entries 20 and 21 (RT2a
predictions R1-R3; RT2a-A outcomes RA1-RA3, GA); `periodic_threshold/JOURNAL.md` from "2026-11-28 08:14 PST" (A2Q
outcome, DR); `stage/REVIEW-wave3.md` section 16; `coord/DECISIONS/0051-*.md` item 4 (the ruling on (a)).

## Card runs of A (shared queue, priority 2)

| queue id | label | run | what it is | read with | prediction |
|---|---|---|---|---|---|
| q0109 | a-rt2a-B | (registered at dispatch) WAITING at 08:40 (five jobs of other owners in Slurm) | bracket member d0.42 on mesh B (deck threshold_ball/decks/nest32_L32_fr: faces at 32 + core-v0.6 face set + region norms), core-v0.9 card build, to t = 51, cap 1.2 | `threshold_ball/scripts/rt2a_read.py --out $NRPIC_RUN_DIR A-F=<scratch>/A-20261128-081045-1e001cd B-F=<B's run dir>` (registered), and `analyse.py` (detection rule) | R1-R3 of threshold_ball entry 20: R1 detection within 0.5 of 45.875, no guard stop; R2 ratio at detection in (0.1, 0.5); R3 matter part falls A -> B by >= 1.5, part 13-32 does not. Also judge (a) per 0051 item 4 (exterior at detection; inner part against A's 0.890; outer against A's 0.150) |

Close it with `harness/bin/nrpic-run finish <run_id>` before reading; check its jobs completed (`nrpic-queue status`).
A chain cut between segments is continued with `threshold_ball/scripts/continue_chain.sh <run_id> <max_segments>`
via `nrpic-queue add --cmd`. The dispatcher submits from this worktree: keep it committed.

Done this session: q0089 (S1L-q, 2.2517 card-hours, completed) and q0108 (RT2a-A, FAILED at the guard at t = 48.14
after its reading time; marked done; 0.0908 card-hours).

## Processor runs

None running. This session: A2Q readers (A-20261128-160444-e6c646e, -160447-c41d66a, -160446-6c171f3), GA
reproducer (A-20261128-160727-0d75d4e, 4 threads, 48 s), RT2a reader (A-20261128-160831-6fd1da1), DR reader
(A-20261128-161728-cabd2c5).

## Next, in order

1. (a): read q0109 when it ends (above). If the inner part on B is still above 0.1 (expected ~0.2 if second order),
   the route is mesh C (8.6 card-hours on v0.6) or a smooth-profile bracket; the outer part needs a domain leg with the
   faces at 64 and the face set (deck to build from nest32_L32_fr with one more coarse level; smoke-test on the v0.9
   processor build; prediction first: outer part in whole-box E units 0.0071 -> <= 0.0047).
2. (d): the sampling leg at fixed mesh (P0L's deck peak_leak with 8x the particles: make_peak_ic.py with a finer
   particle lattice; processors to t ~ 50, or one card member to 100), prediction first (DR showed two more levels do
   not lower the box violation at the same particles).
3. (c): wait for orch's ruling (outbox b41-condition-c-ruling-and-a-on-mesh-a). In either case run the Newtonian
   quarter control (a2_newton.sh with the quarter data: N-z128 at mu = 0.075, eta scaled x2; ~2 h on one core) to turn
   the scaled premise (28.7-29.8 t_H) into a measurement; prediction first.

## Packages

| Package | State | What remains |
|---|---|---|
| `periodic_threshold/` | A2Q and DR judged this session | Newtonian quarter control; sampling leg for (d) |
| `threshold_ball/` | entry 21 (RT2a-A, GA) judged | q0109 reading (R1-R3); domain leg |
| `conv_ball/` | unchanged | turnaround columns and A-R1.35 unchecked by any verifier |
| `note/`, `szekeres/` | unchanged | new results of the next review |

## Traps

- The ball's exterior ratio at detection divides by the E OUTSIDE the found horizon (4.7 per cent of the box on mesh
  A): read every part also in whole-box units (rt2a_read.py writes E_exterior_over_box), or a constant face part
  looks like a jump at detection.
- Region rows hold a horizon only where the latest finder search found one; on mesh A the finder holds it at 46.0 and
  47.0 only. Mesh A stops at the guard at 48.14 (deterministic; reproducer ga_repro.sh): read A only to t = 46.
- A whole-line section-3 ratio to an outflow face never converges with the mesh (FC); split it by region.
- History files of chains continued from earlier restart files hold repeated time ranges: later rows win.
- `nrpic.hst` momentum sums are round-off (|x| < 1e-12): compare them by absolute difference.
- Box decks: `flow = shear`; found or not found is ONLY in `<base>.horizon_status_<n>.txt`. P0L6's region history has
  spikes to ~2 at t = 118-133: never read a single row near there. At most 6 cores per session.
