# g1close: close-out of gate G1 of A-emd-pbh (wave 3, round 1)

Helper package of A-emd-pbh (2026-11-20). It applies or rebuts the corrections of the
wave-2b verifier (`../stage/G1/VERIFIER.md`, run A-20261119-142905-c813c01), puts its
data-flow schematic into the working note, records checksums of the wave-1 outputs behind
the note's ledger, regenerates the note (v1) and the G1 stage package, and judges checklist
items C11 and C18. Predictions and outcomes, in order: `JOURNAL.md` (entries 1-8). No card
time. The work was cut once by the five-hour usage limit (14:35 PST, after entry 4) and
continued from the worktree at 18:54 PST (entry 5).

## What is here

| Path | Content |
|---|---|
| `JOURNAL.md` | the plan with the verifier's locators, predictions P1-P10 written before each run, outcomes |
| `scripts/check_findings.py` | checks verifier findings 1-5 and section 4 item 2 at their sources (median of the read-off ratios, ages of the shells of data set 2t, units, criteria tallies, Newtonian band); writes `findings.json` and `fig_g1close_findings.png` |
| `scripts/wave1_sha256.py` | integrity listing: sha256 of every file of the run directories behind the ledger that recorded no `sha256sums.txt`, verification of those that did, before/after size and mtime check |

## Runs (registered with `nrpic-run`, manifests under `../runs/`)

| Run | What | Outcome |
|---|---|---|
| A-20261120-222454-d16dbc6 | `check_findings.py` | findings 1, 2, 3, 5 confirmed; section 4 item 2 confirmed wrong as written, its replacement too narrow (9 of 14 points in the band, not 4); entry 2 |
| A-20261120-222620-0304d9d | `wave1_sha256.py` over the 15 directories of `note/scripts/common.py` | 55 files of 7 directories listed; 8 directories with `sha256sums.txt` verify, 0 mismatches; nothing in them changed; entry 3 |
| A-20261120-223316-92c27f5 | `note/scripts/run_all.py` (first pass) | 8 of 8 scripts, ledger 53 rows, 71 claims with the 2 known differences; entry 5 |
| A-20261121-030037-3f015fa | `note/scripts/run_all.py` (timeline updated; the committed note copies) | identical to the first pass except the timeline; entry 7 |

## What was done (each with its commit)

- Verifier findings checked at their sources before any change (d16dbc63, d34bcb87).
- Corrections in `note/scripts/ledger.py`, `common.py`, `schem_dataflow.py`, `note/main.tex`,
  `stage/G1/STATUS.md` (2c115cb1): median label; bang time in the surface taper; unit M_0
  and a row in units of the total mass; six threshold names; checksum sentence of App. B;
  wave-2 state (criteria 41 of 41, Newtonian limit, first evolutions, runs since named in
  Sec. V without numbers); labels of the 42.30, the SR-1 breakdown criterion, the SR-2
  estimator, the half box; "several times below the hoop line"; Fig. 7 (data flow).
- Integrity listing of the wave-1 outputs (0304d9d9, f26e7f58).
- Note regenerated, compiled, checked, every page read; verifier scope stated exactly in the
  abstract, Sec. IV E and App. B; timeline brought to the wave-3 state (3f015fa0, 8b7304f5).
- Stage package: `nrpic-stage collect`, items C7, C8, C11, C16, C17, C18, C20 judged,
  EVIDENCE.md (close-out runs; hand-written manifests of waves 1-2), OPEN.md rewritten,
  `nrpic-stage verify` and `report`, README section "Close-out, wave 3" (see the last
  commits of this package).

## How to rerun

From the worktree root with the worktree environment (`harness/bin/nrpic-env create
--no-kokkos` if `.venv` is missing):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/A-emd-pbh/g1close \
        --launcher local --cores 1 --purpose "..." -- python tracks/A-emd-pbh/g1close/scripts/check_findings.py --out '$NRPIC_RUN_DIR'
    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/A-emd-pbh/g1close \
        --launcher local --cores 1 --purpose "..." -- python tracks/A-emd-pbh/g1close/scripts/wave1_sha256.py --out '$NRPIC_RUN_DIR'
    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/A-emd-pbh/note \
        --package tracks/A-emd-pbh/g1close --launcher local --cores 2 --purpose "..." -- \
        python tracks/A-emd-pbh/note/scripts/run_all.py --out '$NRPIC_RUN_DIR'
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then in note/:
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'expball|runs_ball|periodic_threshold|nrpic_cf|nrpic_cosmo|make_field|athinput|nrpic-run|scope_calc|anta|A100|Slurm'
    harness/bin/nrpic-stage collect A-emd-pbh G1; harness/bin/nrpic-stage verify A-emd-pbh G1; harness/bin/nrpic-stage report A-emd-pbh G1

## Not done here

- The owner's STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md (the lead's; C20 stays FAIL until
  the lead rewrites them).
- `stage/G1/GATE_REVIEW.md` (the independent reviewer's).
- The re-judgement of runs_ball prediction R2 with a window-independent turnaround estimator
  (VERIFIER.md finding 6, weak point 1, section 4 item 1): the runs_ball helper's this round.
- A fresh-verifier recomputation of the five rows added to Table IV in note v1 (OPEN.md
  item 2): I applied the corrections, so a check by me would not be a fresh one.

## Requests

- **Lead of A-emd-pbh.**
  1. Rewrite `STATUS.md`, `HANDOFF.md` (and a JOURNAL entry) for the G1 close-out (C20): G0
     passed on 2026-11-19 (`coord/GATES.md`); C11 and C18 closed; in `STATUS.md` line 13
     replace "14 scan points within 6.3e-4 of the ellipsoid" by "the 9 scan points at 128^3
     with >= 2.7e5 particles other than the spindle within +2.2e-4 to +6.3e-4 (spindle
     +1.5e-3, 64^3 controls +8.8e-4 and +1.5e-3, 3.4e4-particle controls -2.4e-4 and
     -4.6e-4)" (run A-20261120-222454-d16dbc6); the criteria state is 41 of 41 with 4
     diagnostics, not 33 of 37; the scouting data's masses and times are in units of
     M_0 = 1 (total mass 1.0096 M_0); the SR-1 breakdown times need their criterion (first
     non-positive metric determinant 30.25 / 32.875, norm(H) > 1e10 at 30.5 / 33.0, first
     non-finite line output 31.0 / 33.25, at dx = M / M/2); "SR-2 fails R2's turnaround
     bound" is estimator-dependent (VERIFIER.md finding 6) until the runs_ball helper
     re-judges it. RISKS.md row 2 ("non-finite at t = 30.8 (dx = M), 33.1 (M/2)") likewise
     needs the criterion.
  2. Extend exception 1 of `WRITING_GUIDE.md` to `scripts/schem_dataflow.py` and Fig. 7 (the
     data-flow schematic in the ledger appendix names the track's files and scripts; the
     checker's 5.8 hits there are accepted as for `ledger.py`), and add a row for the data
     flow to its "Figures" table.
  3. Decide C18: PASS on the scope the gate asked of the verifier, or a short fresh-verifier
     pass on the five new Table IV rows (OPEN.md item 2).
  4. Recheck this package, then call the gate reviewer for `GATE_REVIEW.md`.
- **runs_ball helper (this round):** VERIFIER.md finding 6 / weak point 1 / section 4 item 1
  (SR-2 turnaround estimator; R2 verdict) are yours; the note already quotes the SR-2 value
  only as the three-point-vertex estimate and makes no pass/fail statement from it. When the
  BH-1R manifest A-20261119-164634-f1fe887 (status "submitted") is finished, `nrpic-stage
  verify` loses one of its `runs` failures.
- **core:** `docs/FORMATS.md` line 122 describes `.trajmet.bin` records as 12 values; the code
  (`athenak/src/particles/nrpic_io.cpp:811`) and `coord/INTERFACES/diagnostics.md` section 6
  write 17 (the verifier's request, unchanged).
- **orch:** none from this package.
