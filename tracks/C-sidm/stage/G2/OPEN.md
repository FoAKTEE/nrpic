# C-sidm G2: what the gate still lacks

State at the end of the lead session of batch 17 (2026-11-25). G2 is NOT met and the package is
not ready for an independent review. Seven items pass (C3, C4, C8, C12, C14, C19, C20), four
fail (C1, C2, C7, C9) and nine are open.

## What changed in batch 17

- N6c (C-20261124-221122-928c9eb): the control of the threshold model at N = 1e6 on M/8 holds
  600 M (NS.1 held, NS.2 failed; analysis C-20261125-122010-fb3cc08). The control collapse at
  N = 1e5 is particle-noise relaxation, not a secular error of the scheme. The threshold is
  therefore read at N = 1e6.
- M16 (C-20261125-044843-2d048b6): collisional t_c 158.42 M on M/16 against 163.41 M on M/8 and
  206.64 M on M/4 (analysis C-20261125-122020-031b67e; M16.1, M16.2 held).

## Item by item, and the queue entry that serves it

| Item | What is missing | Queue entry (shared queue) | Prediction |
|---|---|---|---|
| C1, C7, C9 threshold located and compared with the turning point | a bracket at N = 1e6 on M/8: a model below y_max that does not collapse when kicked inward, one above that does | q0046 N6b344 (y0 0.344 kin, N 1e6), q0047 N6b324 (y0 0.324 kin, N 1e6), priority 2 | B17.5, B17.6 (JOURNAL 2026-11-25T12:01Z) |
| C2 particle number | third point of the N-series on M/8; seed scatter of the N = 1e5 control collapse time | q0018 N4c (priority 2); q0022 A334s2c+, q0023 A334s3c+ (priority 5) | NS.3 (2026-11-24T13:14Z) |
| C2 mesh | seed scatter of the collisional t_c at M/8, to judge the 3.1 per cent shift M/8 -> M/16 | q0024 D2f2s2+ (priority 5) | D2.3 seed pair |
| C2 gauge or boundary | no run existed | q0048 D2eta1 (shift_eta 1.0, priority 2) | B17.4 (2026-11-25T11:56Z) |
| C2/C7 mesh and gauge legs of the threshold itself | the bracket on M/16 at N = 1e6 and with a second gauge | not queued: about 4 x 2.5 card-hours on M/8, more on M/16 (request to orch) | to be written before queueing |
| C10, C11, C13, C15, C16, C17 figures and note | drawn once the bracket and the legs have data | none (processor work) | - |
| C18 verifier | not started; scope below | none | - |
| C5, C6 report and reproducibility package | complete only with the items above | none | - |

Removed from the queue in this session (they serve no G2 item once the threshold is read at
N = 1e6): q0019 A334s3o+, q0020 A344s1o+, q0021 A324s1o+, q0025 A334s2i+, q0026 A334s2o+,
q0027 A334s3i+ (the kicked runs of block A at N = 1e5, whose bracket is unfit by A.4). Their
partial records stay on record with their manifests.

Housekeeping owed: A324s1c+ (C-20261123-032324-938ecbd) ended at 600 M (chain DONE) but
`nrpic-run finish` refuses its manifest (a `continuations` field marks it hand-written), so
`qitem.sh close` fails for every run continued in place; close it by hand and read it with
blockA_delta.py (a first look, not registered, shows the y0 = 0.324 control at N = 1e5
crossing alpha_min = 0.3 at about 600 M [TO VERIFY]).

## What a G2 verifier must cover (unchanged items from batch 11, plus batch 17)

- Recompute from the raw histories, with readers of its own: the collapse times and alpha_c
  changes of block A (15 runs), D2 (5 runs and M16) and the N-series (N6c, later N4c, the
  bracket at N = 1e6), and the collision counts per particle and per M.
- The count test of the collision rate before t_c (z = -3.39 at f = 4; REVIEW-wave3 section 14).
- The conductivity series (1.020 +- 0.004 at zero cell and k lambda).
- Run (v): N.4 and N.6 with a trend estimator that separates the pulsation from a trend.
- The resume of cut chains against an uninterrupted run within the card noise.
- The block A noise model as written and as applied; every failed prediction (JOURNAL
  2026-11-24T13:12Z, 2026-11-25T12:21Z).
- That the decks of batch 17 differ from their series only where make_decks_b17.py says, and
  that the N = 1e6 particle files are the same sampler and seed as N6c.

## Reservations of G1 and where they stand

| G1 reservation | State |
|---|---|
| 1 conductivity at the per-cent level | answered: kappa/kappa_1 = 1.020 +- 0.004 at zero cell and k lambda (batch 11) |
| 2 threshold from collapse times or contraction against a control, three seeds | controls hold at N = 1e6 (N6c); the bracket runs at N = 1e6 have one seed each |
| 3 quantities named after the data | the block A ripple window was changed after the data (labelled) |
| 4 card tests without a second check | open: verifier above |
| 5 M/4 mesh does not hold the equilibrium | M/8 does not either at N = 1e5 over 600 M; M/8 at N = 1e6 does (N6c) |
