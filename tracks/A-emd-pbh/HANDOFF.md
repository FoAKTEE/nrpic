# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 24 (wave 3), 2026-11-25 ~19:50 PST.

State in three lines: G0 and G1 are signed (coord/GATES.md). Orch has ruled on the four questions (decision 0043
item 1): C3 and A2 stay FAILED as written, C1 (ii) horizon part FAILED on record, and two card runs are wanted before
G2 goes to its verifier. Batch 24 put both into the shared queue (below); nothing else changed.

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short &&
harness/bin/nrpic-queue list --owner A-emd-pbh; harness/bin/nrpic-run status | grep -v completed | grep "A-2026112";
harness/bin/nrpic-ctx inbox; test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

Files to read first: `STATUS.md`; coord/DECISIONS/0043 item 1; `stage/G2/OPEN.md`; `szekeres/JOURNAL.md` entries 11-12;
`periodic_threshold/JOURNAL.md` the entries from 2026-11-25 18:21 PST on (A2X, PC, A2H and its outcomes D-h, SM-h);
`threshold_ball/JOURNAL.md` entry 15.

## Card runs queued by batch 24 (decision 0043 item 1; both priority 2, waiting at 19:50 PST)

| queue id | label | what | prediction | when it has ended |
|---|---|---|---|---|
| q0067 | a-szk-n256-cont | `--cmd threshold_ball/scripts/continue_chain.sh A-20261125-231808-0784bc9 3`: Szekeres N256 continued in place from rst/szk.00005.rst (tau 21.2) to tau 40; ~0.8 card-h expected, 2 segments at most | szekeres entry 12: P17 (finite to tau 40), P24 (shell rms K error at tau 30 in [0.004, 0.04], at tau 40 above 0.03) | `harness/bin/nrpic-run finish A-20261125-231808-0784bc9` (reopened by the `continuations` record); new dumps `szk.field.00003.bin` (tau 30), `00004` (tau 40) in scratch/A-emd-pbh/A-20261125-231808-0784bc9/; read with `szekeres/scripts/analyse_code_runs.py` (detached, ~1 h per N256 dump, one core) as the N128/N256 reader A-20261126-023245-1dd80ad does; judge P17, P18 at tau 40, P19 at tau 30, P24 |
| q0068 | a-s1l-half | chain, run id assigned at dispatch: S1L-h = S1L at half amplitude (mu 0.15, data A-20261126-032537-f1060e7/S_mu0.15), deck `periodic_threshold/inputs/peak_leak.athinput` + tlim 220, snap_dt 5, output7/dt 30; card build v0.7; --gpu-hours 2.0 (two segments) | periodic_threshold 2026-11-25 19:25 PST: A2H, first crossing in [12.5, 15.2] t_H (candidate holds); > 15.6 refutes toward an amplitude-independent lag; < 11.8 the other way | `harness/bin/nrpic-run finish <run id>`; then `periodic_threshold/scripts/a2_invariant.py --run <dir> --out <dir> --reference 12.3 --band 12.5 15.2`, `a2_crossing.py --run <dir> --out <dir> --label S1L-h`, `a2_probe_check.py --run <dir> --out <dir> --tmax 220` (all registered with nrpic-run, processors); clock t/t_H = (1 + 1.5 t)/6^1.5, central particle's proper time >= int alpha_min dt (column 16 of peak.nrpic.hst); horizon status only from peak.horizon_status_0.txt. A2 stays FAILED whatever it shows |

Older entry still waiting: q0015 a-s1l-cont (continues S1L from t = 198.7 to 220 for SCOPE section 7; not a checklist
item; read by job2_q.py and the a2 scripts).

## Processor runs (detached by batch 23)

| run | what | cores | read with |
|---|---|---|---|
| A-20261126-024724-425ed7f | Szekeres reader, members N64 and N128: ENDED, closed completed by batch 24; its four figures `szekeres/figures/fig_code_n64n128_*.png` are committed but NOT yet looked at | - | read `code_runs_n64n128.json` in its run directory and the figures; they give P18 (N128), P19 (64 -> 128), P20 at N = 128 |
| A-20261126-023245-1dd80ad | Szekeres reader, members N128 (A-20261125-213939-0ad9f29) and N256 (A-20261125-231808-0784bc9, dumps tau 0, 10, 20), ~1 h per N256 dump, ends ~22:30 PST | 1 | close with `harness/bin/nrpic-run finish A-20261126-023245-1dd80ad`; its `code_runs_n128n256.json` and figures give P19 (128 -> 256), P20 at N = 256, P21; write the outcome as szekeres JOURNAL entry 13 (entry 12 is the N256 continuation's prediction) |
| A-20261126-024922-97a2f14 | C3 particle-number leg (threshold_ball entry 15, prediction H): data S2 on nestA8 (x8 particles), then S2c-A8 (M/16, CIC) t = 0 and to t = 2, 2 threads, several hours | 2 | close with `harness/bin/nrpic-run finish A-20261126-024922-97a2f14`; read with `threshold_ball/scripts/edge_compare.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-160633-594a474 --extra S2c-A=<62ce3dc>/S2c-A --extra S2c-B=<62ce3dc>/S2c-B --extra S2c-A80=<run>/S2c-A80 --extra S2c-A8=<run>/S2c-A8 --out ...` (registered); judge H |

## Next, in order

1. When q0067 and q0068 have ended: close each run, read it as the table above says, judge P17/P24 (szekeres entry 13
   or 14) and A2H (periodic_threshold), figures looked at. Card time is not to be waited for: do 2-4 meanwhile.
2. Read both Szekeres readers (N64/N128 closed; N128/N256 A-20261126-023245-1dd80ad: close when ended); szekeres entry 13
   (P18-P21) with their figures.
3. C3: read the particle-number leg (A-20261126-024922-97a2f14, prediction H, threshold_ball entry 15); under 0043 1(a)
   G2 goes to its verifier with the cause of the floor shown by a run that could refute it, or stated as unexplained.
4. G2 package per 0043: C1 (ii) stated as measured (shells against the exact solution; horizon part FAILED on record);
   the note's G2 sections (decision 0039 item 9, `/paper-writing`), schematics on core-v0.7 (C16), ladder schematic
   (C10), rerun list `stage/G2/VERIFY` (C6), convergence figures (C11), slice mosaic from the Szekeres N256 dumps
   (C13); then `harness/bin/nrpic-stage collect/verify/report A-emd-pbh G2` and ask for the verifier.
5. P0L6's finder: when core answers (outbox finder-false-accept-and-stall-p0l6), rerun the finder on P0L6's restart
   files at t = 136 and 140 on processors (0043 item 5 shows how to switch diagnostics on in a continued run).

## Packages

| Package | State | What remains |
|---|---|---|
| `threshold_ball/` | entry 14: C3 mesh leg judged (G refuted); entry 15 prediction H written, run detached | read H |
| `periodic_threshold/` | A2X and AZ1 (N-z128) judged; P0L6 D1-D5 judged; A2H predicted, data and smoke test done, S1L-h queued (q0068) | read q0068 (A2H); finder rerun after core's answer |
| `szekeres/` | series ran (q0040, q0041); P17 judged, N64 rows read (entry 11); N256 continuation queued (q0067, entry 12) | readers (above), then q0067 |
| `conv_ball/` | | A-R1.35 ddet unchecked (verifier) |

## Traps

- `analyse_code_runs.py` takes ~1 min per dump at N = 64, ~8 at 128, ~60 at 256 (one core); run N256 detached.
- A queue entry for a chain gets floor(--gpu-hours / 0.983) segments (1.2 gave one: N256 stopped at tau 21.2). A cut
  chain is continued with `threshold_ball/scripts/continue_chain.sh <run_id> <MAX_SEGMENTS>` through `nrpic-queue add
  --cmd` (it now writes the manifest's `continuations` record; the run reopens and is closed again with finish).
- The particle files hold x, u_i, m only: no Lorentz factor without the metric (a2_invariant.py's bound is empty).
  The 'probe' (column 15 of nrpic.hst) is the normal observer's clock at a fixed COORDINATE point, not a particle;
  the central particle of S1L is at rest (|u_i| < 1e-12), so int alpha_min dt bounds its proper time from below.
- Found or not found is ONLY in `<base>.horizon_status_<n>.txt` (decision 0040 item 3), and even a "found" row can
  be false (P0L6 t = 118.1: check mass, mean and minimum radius, expansion).
- Newtonian controls at one force cell per particle spacing run 26 per cent late (N-z vs N-z128).
- GR particle files carry psi^6 in the masses (B's message, AZ2): never read them as Newtonian masses.
- Quote exact-mass brackets, never a median below the bracket width; with a Gamma-driver use `<z4c> dt_gauge = 0.9`.
- At most 6 cores per session; markdown tables: never write `||H||` inside a table row.
