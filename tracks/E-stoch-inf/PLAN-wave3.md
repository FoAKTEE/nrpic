# PLAN of E-stoch-inf for wave 3

Written by the planner of each round (decision 0019 item 3). Helpers work in parallel in this
worktree, each in its own directory `tracks/E-stoch-inf/<key>/`, with path-limited commits; the
lead rechecks them afterwards (`stage/REVIEW-wave3.md`).

## Round 1 (planned 2026-11-20 22:09Z)

**Gate aimed at: G1** (a package complete for the independent gate review), with the first
G2 runs in parallel because their prerequisites exist and the cards are free.

State read at the start (worktree clean, main merged at cf00f6a8; no pause flag; no card job of
this owner queued or running; 1.43 of 10 card-hours used, 8.57 left, `nrpic-run budget`):

- G0: package complete (every item PASS or NA, verifier report present); `coord/GATES.md` has
  no row for this owner yet. The lead of this round should list G0 as complete so that the
  gate reviewer of decision 0019 item 3 judges it.
- G1 (`stage/G1/STATUS.md`, `OPEN.md`): SR spectrum (A2) and freezing (A3) met at up to 256^3;
  A1, A6, A7 met; the owner's strict A4 fails in P1's set-up (proposal A4'/A5' to orch,
  `outbox/20261119T151727Z__to-orch__a4-a5-rewording.md`, not answered); missing: a
  fresh-context verifier of the G1 material (C16), the updated architecture and data-flow
  schematics (C8, C9, C14), one script per data figure (C13), the G1 sections of the note (C15).
- Core: no merged executable yet (`scratch/core/exe/core_nrpic_v04/` absent); every SR result
  rests on `core_scalar-2` a58e95b (scouting). Core's package scalar3 (branch `core/scalar-3`,
  not merged, executables not published) explains the first-order constraint part as the
  defect of the discrete contracted Bianchi identity and says strict A4 needs about 12.7 cells
  per shortest source wavelength (`tracks/core/interfaces/scalar_field_3.md` section 4 on that
  branch; its reply to this owner is an uncommitted draft in `wt/core-scalar3`).
- Wave 3a package `usr/` (USR case): reference, inputs and 32^3 processor runs done; the card
  ladder and the 256^3 production run were never submitted (`usr/inputs/card_usr.list`).
- Inbox: two info messages (kb snapshot, threaded processor build; the threaded build has no
  `id = stochastic`, so the SR/USR runs still need `core_scalar-2`).

Card time: caps sum to 3.5 card-hours (fits the 8.57 left). Shared queue: at most two jobs of
this owner at a time; every card package submits one job at a time and only when
`squeue -h -u $USER -o %j | grep -c '^E-'` is below 2. Processor cores per package (owner
limit 16): g1verify 4, ladder 3, usr 3, note 2, a4res 2, window 2.

| Key | Goal | Deliverables | Why now | Card cap |
|---|---|---|---|---|
| `g1verify` | fresh-context verifier of the G1 material (SR ladder 32^3-256^3): A1-A7 recomputed with own code from the registered raw outputs; strict A4 and A4' judged on the data | `g1verify/VERIFIER.md` (the lead copies it to `stage/G1/VERIFIER.md`), own scripts, registered analysis runs, figures, JOURNAL | the only G1 item besides the products and orch's ruling (C16, decision 0016 item 4); its input exists and is independent of the other packages | 0 |
| `note` | G1 products of the working note: updated architecture schematic, new data-flow schematic, redrawn timeline and fig_background, one script per G1 data figure from registered outputs, G1 sections of `note/main.tex`, ledger, checker with `--compile`, pages read | `note/` scripts, figures, tables, main.tex, main.pdf, JOURNAL | C8, C9, C13, C14, C15 of the G1 checklist; nothing they need is missing | 0 |
| `a4res` | pre-registered test of the resolution criterion for strict A4 (core's 12.7 cells per wavelength, sixth order): SR runs at 64^3/128^3 with 8-16 cells per shortest source wavelength, +-s and halved pairs; own check of the stencil symbols; core's A2 remark on the k^2 symbol | `a4res/` predictions, card runs, odd/even analysis, verdict table, figure, a five-line "For the A4 ruling" | turns the after-the-data rewording A4' into a test that could fail, the basis for orch's ruling on G1's constraint criterion | 0.5 |
| `ladder` | close G1's smaller items: last-dump time mismatch of the analysis (fig_a4_paper), A6 at 64^3 on a card, L5 single kick (risk R2), and either a P256 rerun on a merged core executable (if `core_nrpic_v04/v05` appears) or a second seed of P256 | new `ladder/results/*2/`, `fig/*2/`, JOURNAL entries 12+, README rows | G1 OPEN item 5 and the review's listed defects; cheap on free cards | 1.0 |
| `usr` | USR case on the cards (first G2 criterion): pre-registered acceptance U-A0..U-A6 with amendments, ladder 64^3/128^3 with +-s and halving at k_max/dk = 8, production 256^3 in P1's set-up, measured cost | `usr/` JOURNAL entries, summaries, figures, README results | prepared in wave 3a and never submitted; the cards are free | 1.5 |
| `window` | second G2 criterion, sensitivity to the window (L9): USR at 128^3 for s = 2.5, 5, 10 and sigma = 0.5, 1, 2 against the linear reference of each window | `window/` reference, card runs, sensitivity table, figures | independent of the other packages; the options `noise_sharpness`, `noise_sigma` exist in `core_scalar-2` | 0.5 |

Fallbacks: no package waits for something that does not exist. If a card job cannot start
within the session, the package commits its list, inputs, predictions and analysis script and
names the pending job; `ladder` item (d) uses `core_scalar-2` when no merged executable is
published; `usr` uses `core_scalar-2` and the dumped H (box mean removed) when
`core_scalar-3` (signed record) is not published.

Not planned (and why): the G3 reference checks of `langevin/` (end-of-inflation delta-N after
USR, importance sampling; G0 OPEN) wait for round 2 or the G2 scope decision; the release
rerun of the SR case waits for core-v0.4; the field-to-particle hand-over is G3+.

For the lead of round 1: forward `a4res`'s "For the A4 ruling" to orch (outbox); copy
`g1verify/VERIFIER.md` to `stage/G1/VERIFIER.md`; bring `stage/G1/` up to date with the note's
G1 products; acknowledge the two inbox messages.
