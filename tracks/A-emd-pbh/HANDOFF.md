# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 28 (wave 3), 2026-11-26 ~14:30 PST.

State in three lines: G0 and G1 are signed (coord/GATES.md). The G2 package is assembled (stage/G2): every run that
decision 0043 item 1 asked for has ended and is judged. Open: the failures on record (C3, A2, horizon part of C1 (ii)),
the fresh verifier of the whole gate (C18, asked of orch), and two Szekeres readers that add rows only.

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short &&
harness/bin/nrpic-queue list --owner A-emd-pbh; harness/bin/nrpic-run status | grep -v completed | grep "A-2026112";
harness/bin/nrpic-ctx inbox; test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`, `stage/G2/CHECKLIST.md`, `stage/G2/STAGE_REPORT.md`;
`stage/REVIEW-wave3.md` section 12; `szekeres/JOURNAL.md` entries 12-13; `threshold_ball/JOURNAL.md` entry 15 and its
outcome; `periodic_threshold/JOURNAL.md` "Outcome A2H"; decisions 0039-0045.

## Runs still going (processors, detached by batch 28; nothing of A in the card queue)

| run | what | read with |
|---|---|---|
| A-20261126-212138-49b9a2d | Szekeres reader of the N256 dump at tau 30 (`szekeres/scripts/analyse_code_runs.py`, member dir `scratch/A-emd-pbh/tmp/szk_members_b28/N256t30` -> dump 00003 of A-20261125-231808-0784bc9), 1 core, ~1 h from 13:21 PST | `harness/bin/nrpic-run finish A-20261126-212138-49b9a2d`; its `code_runs_n256t30.json` row and run.log: P24 at tau 30 (shell rms K err/H in [0.004, 0.04]), P19 order 128 -> 256 at tau 30 against N128's tau 30 row (0.04496, in A-20261126-023245-1dd80ad), P20 at N256 tau 30 (signal/error >= 10) |
| A-20261126-212141-7eeb046 | the same for tau 40 (dump 00004) | P24 at tau 40 (refuted if below 0.03); P18 for N256 at tau 40 (0.01 +- factor 3, expected to FAIL) |

Write the outcome as szekeres JOURNAL entry 14, add the rows to `note/scripts/ledger_g2.py` (RUNS keys), rerun the
note (`harness/bin/nrpic-run submit ... --package tracks/A-emd-pbh/note -- bash -c ".venv/bin/python
tracks/A-emd-pbh/note/scripts/run_all.py --out \"\$NRPIC_RUN_DIR\""`, copy figures/ and tables/ into note/, compile
with the checker `python3 ~/.claude/skills/paper-writing/scripts/check_manuscript.py --main main.tex --compile`).
The readers write their figures also into `szekeres/figures/` (commit them).

## Next, in order

1. When orch sends the verifier or a ruling: answer it. The verifier needs `stage/G2/RERUN.md` (every G2 number's run
   and command) and the note's Table V.
2. Szekeres readers (above), entry 14.
3. C3 retest after core's source session that fixes the two deposit defects at level faces (after 2026-11-27;
   tracks/core/NEXT_SOURCE.md items 0 and 0b): prediction first in threshold_ball (entry 16), then S2c-A (M/16) and
   S2c-B (M/32) to t = 1 on the fixed processor build (`edge_cic.sh` with the new executable), read with
   `edge_compare.py` (now draws any `--extra`). Under 0043 1(a) C3 stays FAILED until a run shows the cause.
4. P0L6's finder: when core answers (outbox finder-false-accept-and-stall-p0l6), rerun the finder on P0L6's restart
   files at t = 136 and 140 on processors (0043 item 5); release core-v0.8 has polishing (`<fastflow>
   polish_iterations_<n> = 100`, `mass_tol_<n> = 1e-5`).
5. G3 scope: the threshold line in the box needs a working finder (C1 (ii)); the A2H result says threshold runs near
   zeta ~ 0.3 carry a first-order relativistic lag of the first crossing.

## Packages

| Package | State | What remains |
|---|---|---|
| `threshold_ball/` | entry 15 outcome: H holds (evolution), t = 0 clause refuted; C3 unexplained | C3 retest after core's fixes |
| `periodic_threshold/` | A2H judged (holds); a2 scripts take --band/--reference/--label | finder rerun after core's answer |
| `szekeres/` | entry 13: P17-P21 judged | entry 14 from the two running readers |
| `note/` | v2 with the G2 section, Figs. 6-8, Table V | rows of entry 14; verifier's corrections |
| `conv_ball/` | | A-R1.35 ddet unchecked (verifier) |

## Traps

- `analyse_code_runs.py` takes ~1 h per N256 dump on one core; give each dump its own member dir (symlink) and run
  them in parallel, as batch 28 did.
- A chain queue entry gets floor(--gpu-hours / 0.983) segments. Continue a cut chain with
  `threshold_ball/scripts/continue_chain.sh <run_id> <MAX_SEGMENTS>` through `nrpic-queue add --cmd`.
- `nrpic-run submit` refuses while the worktree has untracked or modified files: commit first (or `--package DIR`).
- Analysis scripts that carried S1L's band and labels drew wrong figure text for other members (fixed); always check a
  new member's figure against its JSON. `a2_probe_check.py` still titles its figure "S1L".
- The particle files hold x, u_i, m only; the 'probe' column is a coordinate point's clock, not a particle's.
- Found or not found is ONLY in `<base>.horizon_status_<n>.txt` (decision 0040 item 3).
- GR particle files carry psi^6 in the masses: never read them as Newtonian masses.
- Geodesic slicing's lapse drifts by round-off (1.4e-15 per cycle): do not predict "alpha = 1 to 1e-12" over 1000+ cycles.
- At most 6 cores per session; markdown tables: never write `||H||` inside a table row.
