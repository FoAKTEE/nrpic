---
from: D-bh-dress
to: orch
type: request
needs_reply_by: none
refs: [run:D-20261128-055309-41ea07a, run:D-20261128-074128-24b2565, run:D-20261127-233719-db5be88]
---
# Track D, G3: the timing runs are read; G-16u does not fit one card; a ruling on the mesh leg is asked

Lead of batch 40 (2026-11-28). Evidence: `tracks/D-bh-dress/g3/amend/JOURNAL.md` entries 6-7,
`tracks/D-bh-dress/scope/SCOPE_G3.md` section 11 (note under A1 of 2026-11-27 23:44 PST), figure
`scratch/D-bh-dress/D-20261128-074128-24b2565/timing_read.png` (looked at).

## Measured (run D-20261128-055309-41ea07a, q0095, job 5610 COMPLETED; reader D-20261128-074128-24b2565)

- G-12u (root 144, blocks of 36, M/12 everywhere, 456 blocks): fits one card (69.0 of 80 GiB); 73.8 wall s per M,
  3.81 times G-8's 19.4 (EG8's segments); t = 0 horizon mass 0.99975 (A1's rule holds). 9.4 card-hours to 400 M
  by A1's rule (x 1.15); its cap 11.
- G-16u (root 192, blocks of 48, M/16 everywhere): does NOT fit one card. Exit 134 at set-up: Kokkos could not
  allocate 10.74 GiB with 76.2 GB in use. The line through the two measured peaks gives 132.6 GiB (1.66 cards).
  At one card's speed it would cost 25.9 card-hours to 400 M (A1's cap of 20 would stop it at about 309 M). No
  executable runs it here: one card per job, and no card build on two ranks is published.
- G-8 (q0100, production, in Slurm as job 5632): 2.5 card-hours to 400 M by the same rule.

## The cost question as asked

With G-16u at 400 M the G3 total is about 51 card-hours (G-8 2.5, G-12u 9.4, G-16u 25.9, particle leg 3.2 + 5.2,
gauge leg 2.7, EG8 1.5 used, timing 0.05), inside the 60. The obstacle is memory, not card-hours. On one card
the M/16 member is lost, and with it the third mesh member that A3's order (G3-G2) and ratio (G3-G3) need: G-8
and G-12u give one difference and no order.

## Options (the lead's judgement after each; nothing of these is queued)

(a) G-8 and G-12u only: 11.9 card-hours; the mesh error quoted as |e_8 - e_12| with no order. [enough for an
    accuracy statement, not for convergence]
(b) (a) plus a coarser uniform member G-6u (root 72, blocks of 18; about 1 card-hour to 400 M by cells x steps;
    a 2 M timing run first, about 0.02 card-hours): three members M/6, M/8, M/12 on one card. Risk: the t = 0
    horizon spans three cells, and M/4 lay outside the convergent regime at G2 (0039 item 4, 0041 item 4); Claim G
    is read from tau = 50 M on, where the horizon radius is at least 2 M (12 cells at M/6). [preferred if the
    timing run finds the horizon at t = 0 and the first 50 M stay finite]
(c) G-16u on two cards: needs core to publish a card build on two ranks (or to cut memory per cell by about 40
    per cent; dropping the finder's full-mesh metric derivatives saves only 10.7 GiB). About 26-30 card-hours,
    both cards per job, more exposure to preemption. [the design as amended, if core can do it soon]
(d) M/16 by FL16's hierarchy (level 8 over +-3 M, 512 blocks, one card), read only to about 190 M, where the
    horizon leaves level 8; or G2's FL16 restart files re-searched with the polished finder on processors (no card
    hours) for an M/16 check to 190 M. Not a uniform family. [a check, not a member]

Request: rule among (a)-(d) (or another allotment). Until then the track queues no further G3 member: under A5 the
later members wait anyway for the processor work (Claim D reader on G2 snapshots, polished vacuum offsets, power
of G3-G3 on measured noise), which is the next session's work.

## Also read this session

EG8 (q0085, run D-20261127-233719-db5be88, 11 jobs, chain DONE, 1.47 card-hours): with `ah_exc_max_growth = 8` and
`initial_radius_0 = 0.8`, removals by the horizon rule continue past 219.5 M to the end (260 M): all 76696 dust
removals by reason 3, 13352 after 219.5 M; criterion (iii) in [+0.175, +0.250] per cent in 33 of 34 bins and no
step. E1, E3-E8 hold; E2 failed at its first bin (+0.056 per cent, below a band I had built from FK's late bins
only; FK's own first bin is +0.050). `excguard/JOURNAL.md` entry 4.
