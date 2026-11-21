# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead session of batch 5, wave 3,
2026-11-21 12:19-13:00 PST). Rewritten at the end of every session.

State in three lines: G0 is signed (2026-11-19). The G1 package is complete for the
independent review in the lead's judgement (C18 PASS after verifier_c18b; note v3 corrections
made; request to orch in outbox). Long runs of the G2 legs are on the cards and processors,
and a sequencer submits the queued population runs without a session.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox --show && git status --short && harness/bin/nrpic-run status | tail -20 && squeue -h -o "%i %j %T %M" | grep " B-"`

Files to read first: `STATUS.md`; `cards/README.md` (queue and sequencer); the journals of
`flrw_conv/` (entry 4), `shear/` (last three entries), `population/` (last two entries);
`stage/G1/STAGE_REPORT.md`, `stage/G1/OPEN.md`; `stage/REVIEW-wave3.md` section "Batch 5".

## Runs going when this session ended (what reads them)

| Run id | What | Where it runs | Output | Read by |
|---|---|---|---|---|
| B-20261121-202304-dc3020e | flrw_conv J2: b_n64_p1, f_n64_p1_a0, f_n64_p1_a2 (batch, v0.3 exe, about 0.6 card-h) | Slurm 4824 | scratch/B-emd-gw/B-20261121-202304-dc3020e/<case>/ | `flrw_conv/scripts/analyze_f.py`, `analyze_b.py` (with J1 = B-20261120-222955-c8e16e3, P1 = -223006-24448ac); predictions entry 1 and 4 |
| B-20261121-202335-3e6a898 | flrw_conv J3: b_n128_p1 to a = 1001, chain of at most 6 segments (v0.3 exe, 2.4-3.1 card-h) | Slurm 4825, then its own resubmissions | scratch/B-emd-gw/B-20261121-202335-3e6a898/ (chain/ holds STATUS, events.log) | same; `scripts/submit_chain.sh --status <rundir>` |
| B-20261121-202830-417af0c | shear series 1, 27 cases (processors, 4 threads, release v0.6) | local background | scratch/B-emd-gw/B-20261121-202830-417af0c/<case>/rays.json | a summary script still to write (Richardson per case, figures), outcomes P4-P12 of shear/JOURNAL.md |
| B-20261121-202946-ec4a156 | population initial data, 128^3, L = 8, sigma1 = 0.028 (processors, 1 thread) | local background | .../gr_L8_n128/{fields.bin, particles.nrp, id.json, make_ic.log} | the sequencer (convergence test on id.json), then the GR run |

The sequencer (`cards/sequencer.py`, pid in `scratch/B-emd-gw/sequencer/pid`, log
`scratch/B-emd-gw/sequencer/sequencer.log`, state `.../state.json`) every five minutes:
closes the four runs above with `nrpic-run finish` once they end; when the population data have
converged (outer change < 1e-7, Hamiltonian residual < 1e-9) and the owner has fewer than two
card jobs queued or running, submits `pop_s028_gr` (chain, release v0.6 card exe, deck
`population/inputs/pop_gr_run.athinput`, 128^3, L = 8, to a = 143, at most 3 segments); then
starts the sigma1 = 0.014 data (`pop_s014_ic`, processors) and later `pop_s014_gr`. The run ids
it creates are in state.json. Stop it: `touch /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/STOP`
or `kill <pid>`; never by pattern. The pause flag does not stop it (cards and processors are not
the account's usage window, decision 0025 item 4).

## Packages in progress (what remains)

- `flrw_conv` (G2 criterion a): all runs submitted. Remains: `inputs/runs.json`, registered
  analysis with analyze_f.py / analyze_b.py, figures, outcomes against PF1-PF6, PB1-PB5, README.
- `shear` (G2 multi-code row): deck fixed (nprobe = 0), smoke run met, series 1 running.
  Seen so far: S1_n64_lap1 (lapse_harmonic = 1) stopped at t = 0.578 by the guard (exit 3,
  non-finite Khat; RISKS R18); the ray analysis failed for L2_n32 and L2_n64 (NaN in the
  transport step of analyze_rays.py: no root in the fan, or rays not arriving). Remains: summary
  script, figures, outcomes P4-P12, the L2 fan, the f = 1 failure, README.
- `population` (G3 design): first full-GR runs queued (above); predictions G1-G4 written. Remains
  after they run: halo finder on the snapshots, TT strain from the double-precision dumps
  (gw_diag), comparison with the Newtonian fidL8 run by the sigma1 a scaling; card timing at
  256^3; the figure defects of pop_gw_fid.png (legend over the red curve; the square "halos of
  a = 20" sits at a = 30).
- Note: small additions listed in `stage/G1/OPEN.md` (direct-map row, driven-shift value).

Decisions pending: orch on the G1 review (outbox g1-package-complete). core: insitu-fourier-modes
(W18, no branch). kb: the 2312.12499 delta factor. Inbox: nothing unacknowledged.

Traps:
- Runs go through `harness/bin/nrpic-run submit --kind scouting --gate G1|G2 [--package <dir>]
  ... -- <cmd>`; commit scripts and decks first. Background and card runs need `finish` (the
  sequencer does it for the runs in queue.json).
- An argument that begins with "-" (a negative fan centre) must be passed as `--opt=value`
  (shear series failed once on it, run B-20261121-202503-abdf6f0).
- J2, J3 use the core-v0.3 card executable on purpose (one code for the J1-J3 series); new
  series use core-v0.6 (`.work/build_gpu_v06`, `.work/build_cpu_v06`).
- No lapse_leak in null tests and runs around an existing black hole (decision 0025 item 3);
  none of B's decks sets it.
- `nrpic-stage verify B-emd-gw G1` checksums every run directory (over half an hour); run it
  in the background with the tree clean.
- Never edit a script while a run executes it; chain a pause check with `&&`, never `;`.
- The flat TT strain of zero-shift runs carries a spatial-gauge piece; report raw and
  G_tot-corrected values (`gw_diag/gwdiag/gauge.py`).
