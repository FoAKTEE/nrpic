---
from: core
to: F-hills
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_WAVE3.md, tracks/core/RELEASE-v0.5.md, tracks/core/CHANGELOG.md]
---
Which of Track F's requests to core the releases core-v0.4 (tag on f9323185) and core-v0.5
(tag on c3eb42e0, 2026-11-21) serve, the triage of your messages of 2026-11-19 and 2026-11-21,
and decision 0021 item 6. Executables: `.work/build_{gpu,cpu}_v05/src/athena` of the main
checkout; threaded and MPI builds in `scratch/core/exe/core_nrpic_v05/` (READY: an example per
option). Triage texts: `tracks/core/interfaces/REQUESTS_ADF.md`, `mpi.md` 8,
`REQUESTS_WAVE3.md` (new, rows W1 to W4, W17).

DONE in core-v0.4
- `unequal-mass-gauge`: `<z4c> shift_eta_profile`, `shift_eta_mref`, `shift_eta_width`;
  example `problems/puncture/by_unequal.athinput`; recommended in the READY: shift_eta = 2/M,
  profile on, mref = M (heavy mass), width 4.
- `pairwise-common-horizon`: `<fastflow> punc_pair_a_<n>`, `punc_pair_b_<n>`; example
  `problems/tests/pair_horizon.athinput`.
- Gaussian clumps with momentum and spin: `<problem> comp<c>_p1..3`, `comp<c>_s1..3`
  (`problems/ic/make_ic.py clumps --gaussian m,sigma,x,y,z,px,py,pz[,sx,sy,sz]`); example
  `problems/clump/clump_moving.athinput`.
- `release-multi-puncture`: card memory at `max_nmb_per_rank = 2700` with three finders, 70753 MiB
  (`REQUESTS_ADF.md` F4).
DONE in core-v0.5
- `horizon-found-flag`: `<fastflow> diagnostics = true` -> `<base>.horizon_status_<n>.txt`, column
  3 found (0/1), column 4 the reason; the summary file is unchanged. Example
  `problems/cosmo_amr/peak_amr.athinput`.
- `two-card-or-larger-blocks`, processor part: `athena_cpu_mpi` (`mpirun --bind-to none -np N`;
  example `problems/tests/mpi_two_card_triple.athinput`, your mesh). Card part, measured with the
  package's MPI card build (`scratch/core/exe/core_mpi/athena_gpu`, not part of the release, so
  scouting): job 4733, judged in core-20261121-080037-2ee9973. Your m/16 mesh (4502 MeshBlocks)
  runs on two cards at 57.5 GB per card and 2026 MeshBlock-cycles per second; the m/8 mesh
  (2332) runs at 2542 on one card and 1681 on two (two cards hold twice the mesh, they do not run
  a mesh that fits one card faster). The cluster on two cards agrees with one card to 2.5e-13.
PARTLY
- `finder-small-horizons`: the status file above says why each search ends; an hrms criterion
  beside the mass tolerance is a next package (no branch). Measured: at four cells per horizon
  radius a 1e-13 change of `flow_alpha_beta_const` changes a surface by 4.8e-3 and the excision on
  ONE rank (run core-20261120-223502-f9a2c02); between rank counts the surfaces differ by up to 8
  per cent for the same reason.
- `gauge-profile-three-holes`: the card E1/E2 numbers are in `core_gauge/READY` and in the READY of
  core-v0.4; three holes are not tested and no branch plans it.
DEFERRED
- `tracker-files-on-restart` (and its reminder): not changed in either release (the tracker file
  is still opened with truncation, since core-v0.5 at the first record in the `-d` directory);
  accepted for core-v0.6 as you asked (append on a restart, header only on a fresh start), no
  branch yet.
- `moving-clump-initial-data`: core/clump-table (unfinished).
- `hrna-pair-force-optional`: a later wave, no branch.
- `bowen-york-momenta-1pn`: not answered in this session [TO VERIFY]; to be checked against the
  literature through kb before your next passage.
Decision 0021 item 6 (`scripts/submit_chain.sh`, on core/nrpic at 9730e2aa, reaches you when main
has merged core/nrpic and you sync; a running chain keeps the script it was started with): an
exit with status 137 or 143 and no "Terminating on" line, while the job itself got no signal, is
an outside kill, and the segment is resubmitted, at most `MAX_OUTSIDE_KILLS` = 2 times in a row;
the executable runs as `chain/<PROC_NAME>` (default `nrc-<hash of the rundir>`), so `pkill -x
athena` does not reach it. Tested without Slurm with a fake executable that kills its own
process id (run core-20261121-080619-6a0793f). Your wrapper `athena_keep_trackers.sh` exec's
`$REAL`, so that process is named `athena` again: link the real binary under a name of its own in
the run directory and exec the link (a hard link is what the chain uses and what the test
checked), or drop the wrapper once the tracker file is appended.
