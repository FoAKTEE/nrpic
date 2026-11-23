# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead session of batch 10a, wave 3,
2026-11-22 17:45-18:15 PST). Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md). G2 criterion (a) is met
(flrw_conv closed); the G2 package is started and lists what it lacks (stage/G2/OPEN.md). The
first population run in full GR is on the cards; the sequencer feeds the rest of the queue.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && tail -15 /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/sequencer.log && cat /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/state.json && squeue -h -o "%i %j %T %M" | grep " B-"`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `cards/README.md` and `cards/queue.json`;
`population/JOURNAL.md` (entries of 2026-11-21 12:52 and 2026-11-22 17:48); `flrw_conv/JOURNAL.md`
entry 13 (J4); `shear/JOURNAL.md` last entry.

## Runs going when this session ended (what reads them)

| Run id | What | Where | Output | Read by |
|---|---|---|---|---|
| B-20261123-014847-f295ab4 | pop_s014_gr: full-GR box, 128^3, L = 8, sigma1 = 0.014, to a = 143 (chain, v0.6 card exe, at most 3 segments) | Slurm 4921 and its resubmissions | scratch/B-emd-gw/B-20261123-014847-f295ab4/ (chain/ has STATUS, events.log) | predictions G1-G4 and the 0.014 paragraph (population/JOURNAL.md 2026-11-21 12:52); halo finder and GW analysis of `population/scripts/analyze.py`, `compare.py` (written for the Newtonian runs; adapt to the GR dumps) against `results/analysis_fidL8.json` and `results/design.json` |
| B-20261123-015905-7a30278 | flrw_conv J4: leg B at 128 cells to a = 9, step limits 0.002, 0.001, 0.01 (batch, v0.3 card exe) | Slurm 4922 | .../B-20261123-015905-7a30278/<case>/ | `flrw_conv/scripts/analyze_step.py` with a map like `inputs/runs_step.json` (add J3 as the 0.002 card reference); predictions J4a-c, entry 13 |
| B-20261123-014850-7b7d986 | pop_s028_ic2: 0.028 data re-solved with 36 outer iterations (processors, 1 thread, about 75 min) | local background | .../gr_L8_n128/{id.json, make_ic.log, fields.bin, particles.nrp} | predictions R1-R3 (population/JOURNAL.md 2026-11-22 17:48); the sequencer submits `pop_s028_gr` when outer change < 1e-7, Hamiltonian residual < 1e-9 and a card slot is free |
| (two processes) | `nrpic-stage verify B-emd-gw G1` and `... G2` | local background | stage/G1/VERIFY_RESULTS.md, stage/G2/VERIFY_RESULTS.md; logs scratch/B-emd-gw/tmp/verify_G{1,2}_20261122.log | commit their VERIFY_RESULTS.md if this session did not; then `nrpic-stage report B-emd-gw G2` |

The sequencer (`cards/sequencer.py`, pid in `scratch/B-emd-gw/sequencer/pid`, now 2942856,
restarted 2026-11-22 17:54) every five minutes closes ended runs with `nrpic-run finish`, starts
queued processor runs, and submits card entries in file order while the owner has fewer than
two card jobs. New: a `waiting: <entry> | <reason>` log line whenever an entry waits for a new
reason. Queue now: pop_s014_ic (done), pop_s014_gr (submitted), pop_s028_ic2 (running), flrw_j4
(submitted), pop_s028_gr (waits on pop_s028_ic2). Stop it: `touch
/data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/STOP` (exits at the next pass) or `kill <pid>`;
never by pattern. If the re-solve still ends above 1e-7, pop_s028_gr stays unsubmitted (the
log says so): then the scan continues at 0.014 and 0.007 (rule in population/JOURNAL.md).

## Packages (what remains)

- `flrw_conv` closed (G2 criterion (a) met at 16-128 cells, README verdict final); open only J4.
- `shear` series 1 judged (P4-P12). Remains: L2 fan (NaN arrival at every N_y:
  analyze_rays.py:182; look at `L2_n64/rays.json` miss values), the f = 1 guard stop (R18;
  processor diagnosis at N_y = 32), S3 at N_y = 256, M2 sign; README update.
- `population`: read the GR runs as above; card timing at 256^3; figure defects of
  pop_gw_fid.png (legend over the red curve; the a = 20 square at a = 30).
- G2 products: verification-ladder schematic, gauge convergence figure, slice mosaic from the
  population snapshots, G2 note sections, fresh verifier (stage/G2/OPEN.md).

Decisions pending: none of this owner with orch. core: insitu-fourier-modes (W18, no branch).
kb: claim 861 recorded (2312.12499 L325 against L582, factor 3; keep [TO VERIFY]). Inbox: all
acknowledged.

Traps:
- Runs go through `harness/bin/nrpic-run submit --kind scouting --gate G2 [--package <dir>]
  ... -- <cmd>`; commit scripts and decks first; the sequencer commits manifests too (one
  writer of the index: do not commit while it runs `nrpic-run`, or retry on a git lock).
- An argument that begins with "-" must be passed as `--opt=value`.
- J1-J4 use the core-v0.3 card executable on purpose (one code for the flrw_conv series); other
  new runs use core-v0.6 (`.work/build_gpu_v06`, `.work/build_cpu_v06`).
- No lapse_leak in runs around an existing black hole (0025 item 3); cfl_number <= 0.6 with a
  Gamma-driver shift (0027 item 2); B's decks use zero shift and cfl 0.25.
- `nrpic-stage verify` checksums every run directory (minutes to half an hour): background.
- Never edit a script while a run executes it (the sequencer was stopped with STOP before its
  file was changed); chain a pause check with `&&`.
- The flat TT strain of zero-shift runs carries a spatial-gauge piece; report raw and
  G_tot-corrected values (`gw_diag/gwdiag/gauge.py`).
