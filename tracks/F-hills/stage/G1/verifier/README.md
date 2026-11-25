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
| `scripts/run_all.sh` | the registered analysis: the three scripts above into one output directory |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |
| `results/` | copies of the JSON outputs of the registered run |
| `figures/` | copies of the figures of the registered run (all looked at) |

## How to rerun (from `/data/haiyangw/nrpic/wt/F-hills`)

```
harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 \
  --package tracks/F-hills/stage/G1/verifier --purpose "G1 verifier rerun" \
  -- bash tracks/F-hills/stage/G1/verifier/scripts/run_all.sh '$NRPIC_RUN_DIR'
```

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
