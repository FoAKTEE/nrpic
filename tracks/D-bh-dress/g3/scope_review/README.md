# g3/scope_review: independent review of Track D's G3 scope before its runs

Helper package of D-bh-dress (batch 34, 2026-11-27). Reviews `scope/SCOPE_G3.md` against decision 0045
item 2 and the G2 reservations (`stage/G2/GATE_REVIEW.md` section 5). The scope text is changed by the
lead, not here. No card time was used.

Verdict (SCOPE_REVIEW.md): do not queue the production set as written; change B1 (mesh members and
budget), B2 (Claim D's statistic) and B3 (G3-G2, G3-G3) first, then S1-S8.

## Contents

- `SCOPE_REVIEW.md`: findings ranked (blocking / should change / note), with evidence, run ids and
  proposed wordings; a table of every criterion; the order of work; the verdict.
- `JOURNAL.md`: predictions before every calculation (committed first) and the outcomes, failed ones
  included (A3, B1, B3, C1, B2b, half of B2c).
- `tools/make_decks.py`: writes the decks G-8, G-12, G-16 (as SCOPE_G3 section 3 describes them) and
  G-16b (blocks of 12) into `decks/`, for block counts only.
- `tools/block_counts.py`: `athena -m` (mesh structure, no physics) on each deck; blocks per physical
  level and the extent of each level.
- `tools/g2_analogs.py`: the Claim G criteria applied to G2's registered outputs (rms ratios of the
  particle leg, Monte Carlo power of G3-G3 as written, e_h at M/8 and M/16, slope test on the known
  excision-end defect, the converged null test).
- `tools/g3g3_power.py`: power and false-pass rate of a whole-run form of G3-G3, with the anchor of
  Delta M at the 20 M sample or at the 20-40 M mean.
- `tools/dress_model.py`: exact LTB shells on FK's per-particle clocks; the lead-induced q; the scope's
  nearest-tracer-label clock; counting noise of the inner slope.
- `tools/figstyle.py`: copy of `python/nrpic/figstyle.py`.

## Runs (all registered, processors, one core; manifests under tracks/D-bh-dress/runs/)

| Run | Script | Output (scratch/D-bh-dress/<run>/) |
|---|---|---|
| D-20261128-004218-80cf6ab | block_counts.py (first; level labels counted from the coarsest leaf level) | block_counts.json |
| D-20261128-004344-1119b6f | block_counts.py (physical levels, level extents) | block_counts.json, */mesh_structure.dat |
| D-20261128-004801-cd648e5 | g2_analogs.py | g2_analogs.json, g2_analogs.png |
| D-20261128-005059-e65d075 | dress_model.py | dress_model.json, dress_model.png |
| D-20261128-005416-65b4dde | g3g3_power.py (sample anchor) | g3g3_power.json, .png |
| D-20261128-005447-0705a41 | g3g3_power.py window | g3g3_power.json, .png |

## How to rerun (from the worktree root)

    python3 tracks/D-bh-dress/g3/scope_review/tools/make_decks.py
    harness/bin/nrpic-run submit --kind scouting --gate G3 --package tracks/D-bh-dress/g3/scope_review \
        --cores 1 --purpose "..." -- python3 tracks/D-bh-dress/g3/scope_review/tools/<script>.py '$NRPIC_RUN_DIR' [window]

`block_counts.py` calls `/data/haiyangw/nrpic/.work/build_cpu_v08/src/athena -i <deck> -m` (seconds per
deck). The other scripts read only registered outputs under scratch/D-bh-dress/ (run ids in each
script's header) and are deterministic (fixed seeds).

## Requests

- To the lead of D-bh-dress: amend `scope/SCOPE_G3.md` for B1-B3 and S1-S8 by dated amendments before any
  production run is queued; G-8 may be queued once EG8's E1 is read. The no-card items of
  SCOPE_REVIEW.md section 4 (block counts of every candidate deck; the per-particle-clock reader on G2's
  snapshots; polished vacuum offsets of M/8 and M/16; power of the amended mesh criteria) come first.
- To core (through the lead's outbox): the cheapest hierarchy that holds M/16 (and M/12) over +-6 M
  without the 2:1 cascade to the root, and the card memory per MeshBlock of a Z4c run with particles.
- To orch: with measured block counts the mesh leg as written costs about half of the 60 card-hours of
  decision 0045 item 2 (G-16 alone about 28); a ruling is needed if the amended family still exceeds the
  allotment (time-restricted mesh leg or a larger allotment).
