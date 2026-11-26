# Next source session of core (one Fable session of about two hours)

Written 2026-11-25T12:20Z by the core lead (batch 17); rewritten 2026-11-26T02:55Z (batch 23).
Items 1-3 of batch 17 are DONE on branch `core/restart-finder` (source 01d4aeeb), merged into
`core/nrpic` at b755cdcf; the release (core-v0.8) waits for its card check q0049. Order below:
defects first, then what a gate waits for, small and default-off items before large ones.
Every item leaves runs without its option byte-identical (byte regression
`analysis/release/regress_v04.py` against the release then current, 75 items) and goes onto
its own branch from `core/nrpic` with a READY and a new directory under `scratch/core/exe/`
(never replacing a published one: `EXE_PROVENANCE.md`). Source facts below were read at
`core/nrpic` b755cdcf [VERIFIED by reading]; numbers of tracks are theirs.

## For the Fable session, in this order

0. **Defect: `deposit_fine_shape` with the linear cloud (CIC) is not inert at a level
   boundary without a cap** (found by core's test for Track A's question, run
   core-20261126-022953-21b8455, case `cic_fs`; JOURNAL 2026-11-26T02:25Z, outcome D4a).
   - Where: `athenak/src/particles/nrpic.cpp`, `NrpicDepositSources`: with fine shape and
     the linear cloud the lattice cells beside the cloud are visited (`nx = 1`, `ns = nb +
     2`, lines 812-814, 993-1003); a side cell (`own == false`) that lies in a finer block
     (`kd > 0`) enters the fine-shape branch (1032-1072) and receives the tent integral minus
     a constant, a zero-sum dipole, while the cloud's own cells are coarse leaves (`kd <= 0`,
     1009-1021) that keep the plain weight. Without a cap `ldep` is the finest level of the
     stencil's owners, so the own cells are never subdivided and nothing cancels the dipole:
     a uniform lattice of one particle per local cell gets -0.125 and +0.125 in the two fine
     cells next to each boundary (x1 = 7.25, 7.75 of the test), mass conserved. TSC and PCS
     are inert (byte-identical tables), as is every run without the option.
   - Fix (proposal): visit side cells only when the cloud was capped (`lev0 > lcap`, or
     `lmax > lcap` before the clamp at 932): carry a flag `capped` from step (1) and
     `if (!own && !capped) continue;` before the branch on `kd`. Check by reading whether a
     capped cloud whose own cells straddle a level face has the same mismatch (case
     `cic_capfs` of the test equals `cic_cap`, so not on the line tested).
   - Test: `tracks/core/analysis/deposit_levels/dep_levels.py --exe <new> --out DIR`: case
     `cic_fs` byte-identical to `cic` (D4a), every other case unchanged against
     core-20261126-022953-21b8455 (tables of `tsc*`, `pcs*`, `*_cap*` byte-identical; `cic_capfs`
     too if the flag leaves capped clouds alone); byte regression 75 of 75 (no regression
     set-up uses the option).
0b. **The compensation of the cloud is not conservative across a level face** (same run,
   case `pcs_comp`: line sum 32.0413 instead of 32, +0.13 per cent of the mass; by the
   symmetry of the set-up the same for the volume integral). Where: `nrpic.cpp` 1123-1139,
   `NrpicFilterPass(1 + 2c, -c)` / `NrpicCompensateLimited` on each level with ghost values
   from the other level. Cause by reading, not isolated by a run [TO VERIFY]: a pass in
   non-flux form is conservative on one uniform grid only. Options: the flux form that
   exists (`deposit_comp_limit > 0`; not tried on this set-up) or correct the face fluxes
   as the conservative deposit does (fine faces summed onto the coarse face). Test: case
   `pcs_comp` of `dep_levels.py` with line sum 32 to round-off. Track A runs PCS with
   `deposit_comp_c = 1/6`, `deposit_comp_c2 = 0.4667` on nested static meshes: the error is
   O(1e-3) of the mass per level face there [JUDGEMENT; A's set-up not rerun].
1. **`<fastflow> diagnostics` (any new parameter) in a run continued from a restart file**
   (decision 0042 item 4; Tracks D and F: chains started without the option never get a
   status file; Track B's inbox item 21 `restart-new-parameters`, the same cause for
   `<z4c> dt_gauge`, `dt_lightspeed` on its population restarts; F's item 29
   `finder-diagnostics-on-restart`).
   - Where: `athenak/src/parameter_input.cpp` 370-409, `ParameterInput::ModifyFromCmdline`,
     exits with "Parameter '<name>' in block '<block>' on command line not found" for any
     parameter that is not in the parameter set already loaded; on a restart that set is
     the one stored in the restart file (`main.cpp` 279-291), so a parameter added after
     the run started cannot be given on the command line. `fastflow.cpp` 299-300 reads
     `diagnostics` only if present, and the status file is opened for appending with its
     header only when new (454-457): nothing else stands in the way.
   - Workaround that exists today [VERIFIED, run core-20261126-023323-c8fad52, prediction F1
     of JOURNAL 2026-11-26T02:36Z]: `athena -r <file>.rst -i add.athinput ...` where
     `add.athinput` holds only `<fastflow>` / `diagnostics = true`: `-i` after `-r` adds the
     line (`LoadFromFile`), and the continued run writes `<basename>.horizon_status_0.txt`
     (two records, exit 0); the same on the command line exits with status 1. A chain needs
     its continuation line to carry `-i add.athinput` (the chain script takes the restart
     line from its own state: check `scripts/submit_chain.sh` before telling a track it
     works inside a chain).
   - Fix (proposal): on a restart only (`res_flag`), let `ModifyFromCmdline` add a missing
     parameter (and a missing block) with a line in the log ("added from the command line
     on restart: <block>/<name>"); keep the fatal error on a fresh start, where it catches
     typos. Alternatively an explicit form `+block/name=value` that adds. F's smaller
     proposal, `GetOrAddBoolean("fastflow", "diagnostics", false)` in `fastflow.cpp`, makes
     restart files written from then on carry the line, but helps neither restart files
     that exist nor B's step-limit options, and it adds a line to every parameter dump
     (check the byte regression: the stored input is part of a restart file). Test:
     `tracks/core/analysis/restart_diag/diag_restart.py` with the new build: case a must then
     start and write the status file like case b (change F1a's expectation in the script),
     b and c unchanged; byte regression 75 of 75.
2. (was 1-3 of batch 17) **Done on `core/restart-finder`**: outputs that survive a restart
   (tracker file, history headers, the lost `cons.hst` record), finder polishing and the
   excision growth guard (`ah_exc_max_growth`), figstyle without a creation date. Release
   after card check q0049 (`JOURNAL-restart-finder.md` entry 20).

## Not for this session, in order (named so that the next round can plan them)

4. **core/oblate into a release** (gates: core G2 ladder row 3; Track A asked for a ruling on
   the oblate/prolate row). Not a Fable item: the branch (tip 4f01a81f, 2026-11-20) merges
   main, reruns its T1 (conformal factor equal to the potential of a homogeneous oblate
   spheroid to float32 rounding) and T2 (byte-identical without the component), publishes
   with READY; then the lead reviews it. Reference: the analytic potential the branch
   already uses; collapse runs at M/8 (first horizon 41.875 M, `JOURNAL-oblate.md` entry 9
   on the branch, not judged by the lead).
5. **The drift of collisionless clusters on the M/8 mesh** (gates: core G2 ladder row 4;
   Track C G2, whose King controls collapse on their own at 534.8 and 549.3 M). Not a source
   item yet: diagnosis first. Core's row-4 control of y_c = 0.73625, STABLE by the 300-M
   rule, collapses at 421.25 M (fates run core-20261125-120724-246d2a5); with level 3 every
   model from 0.605 to 0.73625 collapses by 421 M (core-20261126-023040-b755cdc). Whether the drift
   rate depends on N (particle noise) or not (the scheme) is decided by runs at a second N:
   Track C queued N = 1e4 and 1e6 controls; core's row 4 has a second cell size or N as its
   open item. Only an N-independent drift becomes a source item, with C's reproducing deck.
6. **The cure of the relaxed lapse around a hole** (W30; gates: Track D G2/G3 runs around a
   hole with `lapse_leak`; core-v0.7 has the mitigation `lapse_leak_hole` only). Design work
   (candidates a-c in REQUESTS_WAVE3.md W30); tests owed: D's V-1GB and ES-1GB to 200 M
   within the band of the control without `lapse_leak` (6.8e-5 late), the collapse test of
   core/gauge-2, the byte regression. Larger than two hours.
7. Later, no gate waits now: W18 in-situ Fourier modes (Track B, for the 256^3 GW cadence,
   reply by 2026-12-11); W25 sub-steps of E's lockstep record (E gates U-A2 to k <= 32 dk
   meanwhile); W22 collisions on several ranks (C, test T10 on 1 and 4 ranks); W6 ADM
   energy on spheres (C); W1 an hrms criterion of the finder (F); F's wave extraction
   beyond l = 8 and the HRNA pair-force specification; W31 ii, a step limit for
   `lapse_leak` x dt.

## Already served without new source (answers owed, no session needed)

- Restart on SIGTERM (Track C item 2 of `control-drift-and-sigterm-restart`, Track F
  `restart-on-sigterm`): in release core-v0.7 a run that receives SIGTERM finishes its
  cycle, writes a restart file and exits 143; chains need the chain script of core-v0.7
  (`coord/INTERFACES/preempted_runs.md`). Not tested under a real preemption (OPEN.md
  core-v0.7 item f).
- Track B `newton-fft-threaded`: a processor test, not a source change: `newton_poisson =
  fft` with `athena_cpu_omp` at one thread against `athena_cpu` on a reduced copy of B's
  deck; a line in the READY. The lead or a package can run it.
- Track C item 1 (drift rate of core's controls): the 50-M window means are in the fates
  runs core-20261124-130055-9fc9901 and core-20261125-120724-246d2a5 (`windows_50M` of
  `row4_fate.json`), at one N (1e4) only.
