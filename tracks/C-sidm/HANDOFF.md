# HANDOFF of C-sidm

Written for a reader with no memory of the last session (lead of wave 2b, 2026-11-19).

State in three lines: G0 package complete for the orchestrator's review (decision 0016 item
4); G1 NOT MET only because the heat-conduction tests T6-T8 (package `heat/`, a wave-3a
helper working in this same worktree) have not finished. The collision operator passes every
other box test, also with `coll_energy = particle` and in a static curved metric (T12); the
first collisional King-cluster runs collapse, and which of physics, the old energy defect or
the mesh drives CC2's collapse is undecided (decisive runs D1-D3 written, none submitted).

Owner: C-sidm, branch `track/C-sidm`, worktree `/data/haiyangw/nrpic/wt/C-sidm`.
Run next: `cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && harness/bin/nrpic-ctx inbox --show && cat /data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/CARD_TESTS.log && squeue -u haiyangw`
(then: if core says the collisions-2 card executable is usable and the owner has a free card
slot, write the D1 predictions into `JOURNAL.md`, make decks from
`threshold_scan/inputs/cc{1,2}_kn10.athinput` plus `particles/coll_energy = particle` (the key
must be in the deck, not only on the command line) and submit D1 with
`harness/bin/nrpic-run submit --launcher batch --gate G2 --list <list>`; if the heat helper
has finished, review `heat/` from its run outputs first.)

Files to read first: `STATUS.md`; `stage/REVIEW-wave2.md` sections 6-8 (wave 2b) and 1-5
(wave 2); `stage/G1/OPEN.md`; `stage/G0/OPEN.md`; `JOURNAL.md` last two entries (predictions
and outcomes L12-L16, failed clauses included); `collide/TESTS.md` (section 2a);
`box_tests/README.md` (section "Wave 2b"); `threshold_scan/JOURNAL.md` entry 6.

Key numbers (with runs): King threshold y0 = 0.334032 (collisionless E_b maximum); Juttner
fluid onset of the King family y0 = 0.32143 (run C-20261119-151502-cb831a8); F21 b = 0.1
anchor Z(0) = 0.5331, eps maximum 0.5404; K = 1/(rho0_c H_c) = 168.895 (CC1), 186.081 (CC2),
sigma~ = K/Kn. Collisional cluster runs C-20261115-171058-c26cfad, -171059-4b70228,
-171059-35441e3 (analysis -191420-8538aa4; rechecks C-20261119-151502-cb831a8,
-151944-08f3220).

Decisions pending: G0 review (orch); core's statement on the collisions-2 card executable
(outbox 20261119T151725Z); core's answers on format findings, ADM-energy diagnostic, refined
mesh and non-finite stop (outbox 20261119T1517*); orch on a core share for leads. Lead
decisions of this session: `coll_energy = particle` for every collisional run in a field; the
T12 twin as the sharp form of its criterion (TESTS.md 2a); no Synge fluid equation of state
scheduled at core (answer in outbox); collapse "within 300 M" is no threshold criterion
(RISKS 7).

Traps:
- The heat helper (wave 3a) commits in this worktree too: commit with explicit paths
  (`git commit -- <paths>`), retry while `index.lock` exists, never `git add -A`; its
  untracked files are not yours to commit.
- One owner allotment of 16 cores and two queued card jobs is shared with that helper:
  `nrpic-run submit` refuses while it holds them; retry in a background loop.
- `nrpic-run submit --package <dir>`: uncommitted edits elsewhere in `tracks/C-sidm/` are
  recorded, inside the package refused; commit first.
- A command-line override `particles/coll_energy=...` works only if the deck has the key.
- Card runs with deposition are not byte-reproducible: compare collapse times with a seed
  scatter, never one run against another.
- The controls drift outward by more than the stability margin on the M/4 mesh: read
  collisional effects relative to the control of the same mesh and seed.
- Never kill by pattern; at most 16 cores; card runs within the 41.4 card-hours left.
