# HANDOFF of C-sidm

Written for a reader with no memory of the last session (lead of batch 2b, wave 3,
2026-11-21 07:48-08:40 UTC).

State in three lines: G0 is signed (coord/GATES.md). G1 is NOT MET only for two package items:
the working note's G1 sections (C16; the note session was cut and left uncommitted text) and
the fresh verifier's VERIFIER.md (C17; package verify_g1 works on it in batch 2b); every
track-sheet criterion is met. G2 scouting: the M/4 controls' drift is a mesh effect, the
threshold model's collapse time scatters by about 3 M between seeds, and the collisional
collapses come from collisional contraction, not from the relativistic onset.

Owner: C-sidm, branch `track/C-sidm`, worktree `/data/haiyangw/nrpic/wt/C-sidm`.
Run next: `cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox && squeue -u haiyangw && test -e tracks/C-sidm/stage/G1/VERIFIER.md && echo verifier-done`
(then: if VERIFIER.md exists, answer every WRONG or NOT CONFIRMED item in
`stage/REVIEW-wave3.md` (new section) and in `stage/G1/CHECKLIST.md` C17; if the note is
finished, set C16; then `harness/bin/nrpic-stage collect C-sidm G1`, `verify`, `report`, and
ask orch for the G1 review.)

Packages still in progress (leave the files of a package to its session):
- note (cut 2026-11-20 22:35 UTC; not continued in batch 2b). Committed: scripts (53ffec35)
  and the outputs of registered run C-20261120-223007-fe3f39c (077b849d). UNCOMMITTED in the
  worktree, belonging to it: `note/main.tex` (G1 sections partly written), `references.bib`,
  `scripts/common.py`, `scripts/ledger.py`, `scripts/schem_timeline.py`, `tables/ledger.tex`,
  `tables/runinfo.tex`, `figures/schem_timeline.{png,svg}`. Remaining: outcome of N3 in
  `note/JOURNAL.md`; G1 sections (box tests waves 2/2b, heat T6-T8 with the wave-3 numbers of
  `heat/README.md`, models with the rate restriction of C2, Juttner anchor and King onset,
  cluster runs as G2 scouting); in the architecture schematic, "growth-rate fit" is decided
  (C2) and T7/T8 also ran on the card; registered run_all; compile; checker with --compile;
  pages read; commit.
- verify_g1 (resumed in batch 2b, same worktree): V1a-V1c, V2, V3 done; the rest and
  `stage/G1/VERIFIER.md` to come.
- models (paused 2026-11-20): left over are step 5 (reading of the King runs: alpha_coll
  minus control, period from the control; predictions K in `models/JOURNAL.md` entry 9), its
  README section and the C2 statement (C2 is now decided by the lead: rates only with their
  interval, REVIEW-wave3 section 4); figures of its validation drawn by the lead
  (C-20261121-075535-b35b8fb).
- drift (paused 2026-11-20; run (i) judged by the lead, `drift/JOURNAL.md` entry 8): next card
  runs (iii) CC1 at M/8 and (v) N = 1e4 (decks and lists in `drift/inputs/`, commands in
  `drift/README.md` "How to rerun"; predictions M8 and N in entries 2 and 5); (ii) and (iv)
  are dropped.
- decisive and heat: closed. D2 (collision cell size, 2-5 card-hours) has no decks yet.

Card jobs of this owner: none queued or running (08:30 UTC). No pending runs.

Files to read first: `STATUS.md`; `stage/REVIEW-wave3.md`; `stage/G1/OPEN.md` and
`CHECKLIST.md`; `JOURNAL.md` last two entries (L17-L22); `collide/TESTS.md` section 2b;
`drift/JOURNAL.md` entry 8; `decisive/JOURNAL.md` entry 15; `heat/README.md` "Verdict for G1
C6"; `PLAN-wave3.md`.

Key numbers (with runs): T7 at theta 0.003 kappa/kappa_1 = 1.019 +- 0.004 (processors,
C-20261119-161930-acd257b), 1.0250 +- 0.0025 (with card seeds, C-20261120-223203-b38a7d7);
King threshold y0 = 0.334032, Juttner onset y0 = 0.32143 (C-20261119-151502-cb831a8); t_c at
Kn = 10: CC2 206.26-206.73 M (four runs), CC1 178.86-185.85 M (five runs)
(C-20261121-075202-1a37fb9); control periods at M/4 399 (CC1), 355 (CC2), 282 M (D3); M/8
excursion ratio 0.10-0.25 (C-20261121-075359-26e3b31).

Decisions pending: orch on the next batch (outbox 20261121T081156Z next-batch); core on the
heat-conduction text and on collisions over several ranks; core's earlier requests (ADM-energy
diagnostic, collisions on refined meshes, format findings; outbox 20261119T1517*); kb on the
conductivity sources. Lead decisions of this session: C6 met with the TESTS.md 2b wording; C2
met with rates only with their interval; block A of SCAN.md on M/8 (or an M/4-M/8 pair) after
run (iii); at least three seeds per model near the threshold; drift (ii), (iv) dropped.

Traps:
- Two sessions write in this worktree (lead and helpers): commit with explicit paths
  (`git commit -- <paths>`), wait while `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock`
  exists, never `git add -A`; another package's uncommitted files are not yours.
- `nrpic-run submit --package <dir>` refuses uncommitted edits inside the package; commit
  first. A command-line override `particles/coll_energy=...` works only if the deck has the key.
- `nrpic-stage verify C-sidm G1` checksums the large run outputs and runs for more than ten
  minutes: run it in the background.
- Card runs with deposition are not byte-reproducible: compare collapse times with a seed
  scatter. Read collisional effects against a control of the same mesh and seed.
- Collisions stop on more than one MPI rank (core-v0.5); the threaded processor build is not
  a byte reference.
- Never kill by pattern; at most 6 cores per session; card runs within the allotment
  (39.14 card-hours left to G2).
