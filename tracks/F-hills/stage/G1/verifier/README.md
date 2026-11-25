# stage/G1/verifier: fresh verifier of G1 of F-hills (checklist C18)

Helper package of batch 22 (2026-11-25), processors only, 0 card-hours. It recomputes the G1
material of `../OPEN.md` item 2 with readers written here (not the packages' readers), for
everything but the tail of the passage (A2 after its last record, 96.23 M). The report is
`../VERIFIER.md`; predictions and outcomes are in `JOURNAL.md`.

## Contents

| Path | What |
|---|---|
| `scripts/vread.py` | readers: tracker files and the join of kept copies (later segment supersedes from its first time; overlap and gap checks), local minima with parabolic refinement, horizon summaries with the failure signature (non-finite or non-positive mass, or columns 3-12 identical as text to the previous kept row), Z4c history, waveform sample times |
| `scripts/vnewton.py` | Newtonian N-body reference (G = 1, DOP853 at rtol = atol = 1e-12), initial data from a deck's `<problem>` block (bare masses, v = p/m), two-body energies |
| `scripts/vtest.py` | P0: the readers and the integrator on analytic cases (Kepler ellipse split into overlapping tracker segments with an injected offset; pericentres; energy and angular momentum of the deck's three-body run; synthetic horizon summary with restart repeats and failures; waveform times with duplicates) |
| `scripts/vpassage.py` | P1-P7: passage P1b (A + A2): trackers joined, pair closest approach, centre of mass, coordinate energies, horizon numbers, rms H, waveform samples, Newtonian reference from the deck |
| `scripts/vmesh.py` | P8, P9 and the horizon scan: binary alone at m/8, m/12, m/16, P1b at m/16 and m/12, P1's merger and remnant to 280 M, member drifts in the owner's windows, failures by signature in every finder of P1, R8, R12, R16n+B, A+A2, C |
| `scripts/vjunk.py` | criterion (iii): t = 0 Hamiltonian residual of the E2 cases, FFI junk energy of P1's data at its four spheres (with an analytic test of the FFI) |
| `scripts/vkhsr.py` | KHSR K3 at four prograde points with the integrator of vnewton.py (4 worker processes) |
| `scripts/run_all.sh` | the registered analysis: vtest, vpassage (to the last record and cut at 96.2285 M), vmesh, vjunk into one output directory |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |
| `results/` | copies of the JSON outputs of the registered run |
| `figures/` | copies of the figures of the registered run (all looked at) |

## Results (registered runs; details in `../VERIFIER.md`, outcomes in `JOURNAL.md` entries 2-4)

- Reference pass **F-20261125-175931-32701e4** (run_all.sh; supersedes F-20261125-175038-4719d4a,
  -175132-e7c6c68, -175235-e0fdde6, -175533-141e4f1, whose numbers for the same quantities agree):
  passage A + A2 joined 0-96.2285 M without a gap (overlaps <= 1.1e-12 M), pair closest 2.10963 M
  at 76.373 M, centre of mass 13.0626 M from M at 96.2285 M and closing; Newtonian reference to 6-7
  digits (c.o.m. pass 9.762 M, not the conic's 9.809 M); binary_conv table to 5 digits, no
  asymptotic convergence order; P1 merger 48.79-49.06 M, remnant pass 6.9917 M at 154.598 M; horizon
  failures by signature only in the m/8 runs; A2's heavy hole falls -1.7e-5 per M and splits into two
  finder branches from 86.6 M (finding F1); t = 0 rms H 4.71e-5 at m/8; junk 2.28-2.73e-6 M at the
  four spheres (within 19.8 percent).
- KHSR check **F-20261125-180244-25c98a5**: four prograde points within 0.41 sigma of the scan;
  P1/P2 0.144, 0.155 at r_a = 100 r_t.
- Copies: `results/` (JSON; `results/cut_96.23/` the passage at the owner's last record),
  `figures/` (PNG, each looked at).

## How to rerun (from `/data/haiyangw/nrpic/wt/F-hills`)

```
harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 \
  --package tracks/F-hills/stage/G1/verifier --purpose "G1 verifier rerun" \
  -- bash tracks/F-hills/stage/G1/verifier/scripts/run_all.sh '$NRPIC_RUN_DIR'
```

The KHSR check: `-- python tracks/F-hills/stage/G1/verifier/scripts/vkhsr.py --out '$NRPIC_RUN_DIR'
--nphase 256 --workers 4` with `--cores 4` (about 1.5 minutes).

Every reader works to the last record present, so the same command run after A2's chain has
reached its separation (at least 170 M) verifies the completed passage unchanged: the tracker
join picks up every new kept copy under `trk_keep/` and the live file, the horizon, history and
waveform readers read to the end, and the Newtonian reference runs to max(200 M, last NR time).
What has to be judged by hand then: A2-2 (`state_at_end.d_cm_minima` in `vpassage.json` gives
the centre of mass's closest approach), A2-3 (distances and two-body energies of each member with
M at the end), A2-4/A2-5 (horizon blocks `horizon_A2_*`). If a further continuation writes into a
new run directory, add it after A2 in `RUN_A2`'s place (vpassage.py) and in `RUNS["A"]` (vmesh.py).

## Requests

See `../VERIFIER.md` section "Requests". In short: to the lead (F-hills), the corrections listed
there; to core, nothing new beyond the open request on the finder's diagnostics after a restart.
