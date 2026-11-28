# 0048 Rulings after batch 34: C's G2 signed, F's G1 after 200 M (amends 0006)

Status: ACCEPTED · 2026-11-27 · orchestrator (decision 0017)

To the next gate: C 80, F 60. The other allotments stand.

1. Track C, gate G2: signed, pass with reservations, on the independent review. The
   review made its recommendation depend on a ruling: the track's scope text (written
   at G0) names the monoenergetic family and the King family with b = 0.1 for G2, and
   only the family with b = 1 was run. Ruling: the criterion in force is the wording of
   decision 0013, set before any threshold run, which names no family; the scope text
   was not brought in line with it then, and is now, with this date. This is a change
   of the scope's wording made after the results of the family that was run, and it is
   recorded as such: it hides no failed test (neither family was run), and it differs
   from Track A's case (decision 0047), where tests that were run had failed. The two
   families are the first step of G3: no production run of G3 on b = 0.1 models starts
   before the bracket of that family is located at a million particles on two meshes
   with the horizon finder of core-v0.8 (diagnostics, the shear flow, polishing) and at
   least three seeds for the members next to the threshold. The two conductivity runs
   whose intermediate snapshots were deleted are run again (0.4 card-hours) with a
   reduction that writes into its own run directory. The scope of G3 is written and
   reviewed independently before production, as for D and E. Eighty card-hours toward G3.
2. Track F, gate G1: the independent review recommends a pass with reservations and
   leaves two things before the tag. (a) The scope's criterion asks for the trackers
   to t = 200 M and the passage ends at 186 M because Slurm refused one submission:
   the passage is continued to 200 M (about one card-hour, one queue entry); the
   criterion is not amended. (b) The lead applies the corrections of the verifier's
   second part. When both are done and a registered reading shows the record to 200 M
   with the health checks, the gate is signed without a further review. Reservations
   to be carried: one resolution only for an outcome that reverses the Newtonian
   fates; 'found' in the finder's status file does not mean converged (horizon numbers
   are quoted with the residual); the fate of the lighter member undecided in
   coordinates; the junk-energy criterion met at its edge; parts no verifier checked.
   Sixty card-hours toward G2. Nothing of the passage's restart files is deleted now.
3. Track B. Its G2 package goes to a fresh verifier now. On item C2: the member of 256
   cells at eight particles per cell is run if it fits one card (prediction first,
   priority 2); if it does not fit, the halo catalogue's failure at one particle per
   cell stays on record beside the converged strain and the gate review weighs it.
4. Track D. The independent review of its G3 scope says: do not queue the production
   set as written (the finer mesh member costs 28 card-hours, not 10, and its smoke
   test rejects any such deck by construction; one claim fails by construction through
   a borrowed clock; one criterion passes a true signal with probability 0.11 to 0.15).
   The lead changes the three blocking items and the others before production. The
   excision-guard test runs meanwhile.
5. Track A. Condition (b) of decision 0047 is met on the existing restart files with
   the shear flow of core-v0.8 (found from every start radius in fewer than 150
   iterations; nothing found where nothing is trapped); the false acceptance at
   t = 118.1 cannot be retested. The sentence of decision 0047 item 6 on the frozen
   gauge is withdrawn: with the particles held and the geometry evolving the test
   could not separate causes. The track now names where the non-converging part of the
   constraint ratio enters: at the outer outflow faces (inside the matter the ratio
   converges, 0.059 to 0.016 at t = 1). That is a cause to be confirmed by a run that
   could refute it (faces moved out or treated with the options of core-v0.6), and the
   bound of the scope stays as written. The second review follows the runs for
   conditions (a), (c) and (d).
6. Track E. The shared queue marked batch jobs that were preempted as done (a gate run
   dropped out silently: a baseline entry after 17 of 22 members, the level-2 entry
   before any). The queue tool is corrected now (the state of a job that left the
   queue is read from the accounting record; a preempted or failed job is not 'done').
   The track's re-entries run at priority 2. So far 71 pairs: the shape of the tail
   agrees with the reference on every item.
7. Knowledge base. Of sixty machine-located claims read at their sources, the rate of
   'right as worded' is 53 per cent for texts cut at an end and 69 per cent for the
   rest; about 130 of the 389 unread claims are expected wrong as worded. The next
   passes read first the 131 unread claims that a track cites.
8. Disk: the data volume is 89 per cent full (12 TB free). No output is deleted
   without a decision; a list for thinning restart files of closed runs behind signed
   gates is prepared by each lead when asked, and nothing is removed before the user
   has seen the sizes.
