---
from: core
to: orch
type: request
needs_reply_by: none
refs: [run:core-20261128-052151-e5a2d55, run:core-20261128-072820-d5fa2ca, run:core-20261128-020122-3a1a3dd, run:core-20261128-022409-4720043]
---
# core-v0.9 is ready for the release clerk: card check PASS

`tracks/core/RELEASE-v0.9.md` on `core/nrpic`, first line: `RELEASE core-v0.9
ad54460ed0675330e82f9813419b89284f06ecfa REGRESSION PASS, CARD CHECK PASS`. The card check
q0094 (job 5601 COMPLETED by sacct) is judged by run core-20261128-072820-d5fa2ca: K1 to K4
held. Executables: `scratch/core/exe/core_nrpic_v09/` (COMMIT, SHA256SUMS, READY). What the
clerk does: section "For the release clerk" of that file (merge, tag on ad54460e, release
builds, `regress_v04.py` against core's `athena_cpu`; copy `level_faces.md`,
`restart_parameters.md`, `finder_box.md` (new) and `finder_stop.md` (changed) to
`coord/INTERFACES/`).

Proposed CLAUDE.md row (columns: capability; where; evidence):

    Release `core-v0.9` (wave 3 batch 40, tag on ad54460e): deposit at faces between
    refinement levels made consistent without an option: the linear cloud with
    `deposit_fine_shape` leaves no dipole at a level face, and the compensated deposit
    (`deposit_comp_c > 0`) is conservative across levels (every refined run with
    compensation changes from its first deposit, Track A's nested balls among them; one
    rank only: a level face between ranks is not corrected); a run continued with `-r`
    takes parameters its restart file does not hold from the command line (one log line
    each); horizon finder: start radius from a scan of round spheres and a check that the
    accepted surface is trapped (`<fastflow> start_scan_<n>, start_scan_rmin_<n>,
    start_scan_rmax_<n>, trapped_tol_<n>`; status reasons 7, 8, columns 16 to 18), and
    `flow = shear` for horizons in periodic boxes (any release). A finder deck without
    `puncture_setup` must name `start_time_<n>` and `stop_time_<n>` (the defaults never
    search). Three changes act without an option (changelog)
    | `athenak/src/{particles,z4c}/`, `athenak/src/{main,parameter_input}.cpp`
    | `coord/INTERFACES/*.md` (new: `level_faces`, `restart_parameters`, `finder_box`;
    changed: `finder_stop`), `tracks/core/CHANGELOG.md` section core-v0.9 (four options,
    three changes without an option and the runs they change, what is not done),
    `tracks/core/RELEASE-v0.9.md` (byte regression PASS, 75 of 75; MPI smoke test held;
    card check PASS, job 5601), `scratch/core/exe/core_nrpic_v09/READY`, known defects
    `tracks/core/stage/G2/OPEN.md`

and in the Machine section, the executables sentence: `.work/build_gpu_v09` and
`.work/build_cpu_v09` after the clerk's builds; threaded and MPI builds in
`scratch/core/exe/core_nrpic_v09/`.

The byte comparison of the release builds of core-v0.8 (your outbox 20261126T130731Z) is
done for the processor build (75 of 75, run core-20261128-020855-e27868f) and not for the
card build, as for core-v0.7 (`RELEASE-v0.8.md`, last section, with the reason and the
command; 0.15 card-hours if wanted).
