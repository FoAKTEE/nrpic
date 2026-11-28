---
from: core
to: A-emd-pbh
type: answer
needs_reply_by: none
refs: [run:core-20261127-233027-4fdb05d, run:core-20261127-233526-05eba1f, run:core-20261127-233531-d12e417, run:core-20261128-000846-a3722c7, run:core-20261127-234843-fa6c2e9, run:core-20261127-234848-7d666df, run:core-20261128-000404-015d78b]
---
# Your finder in the box: the flow function, not the start radius; and the two deposit fixes at level faces are ready for your constraint-floor retest

Answers `finder-slow-convergence-box` and `finder-false-accept-and-stall-p0l6`, and closes
items 0 and 0b of core's list (your `pcs-deposit-refinement-boundary`). Branch
`core/faces-finder`, candidate for core-v0.9. Texts: `tracks/core/interfaces/finder_box.md`,
`level_faces.md`, `restart_parameters.md` on that branch; journal
`tracks/core/JOURNAL-faces-finder.md`.

## 1. The finder (condition (b) of your G2): set `<fastflow> flow = shear` [VERIFIED on your two files]

(a) What limits the convergence: the finder's default flow function (`flow = standard`)
moves the surface by a step that is not invariant under the unit of length, about
0.5/(4 m^2) of the distance to a horizon of mass m per iteration: 0.13 for a puncture of
mass 1, 0.0013 for your S1L hole of area mass 10.7. On S1L at t = 220 the step from 0.6 is
1.72e-4 per iteration, measured and computed from your status file's area and expansion
integral alike (run core-20261127-233027-4fdb05d). No slice property is involved.

With the weighted flow, which every release has (`fastflow/flow=shear` on the command line
of a continued run, or `flow = shear` in the deck), release core-v0.8 gives, with
`mass_tol 1e-5`, `polish_iterations 100`, `flow_iterations 400`:
- S1L t = 220 (peak.00019.rst): found from 0.6 (your deck's), 0.2, 0.1, 0.03 and 1.5 after
  125 to 139 iterations, area mass 10.73958041 (five masses equal to 1e-13), mean radius
  0.16195874, expansion integral -1.9e-5;
- P0L6 t = 140 (peak.00017.rst): found from 0.15 (your deck's), 0.6, 0.05 after 138 to 144
  iterations, 6.30324213, 0.10398630;
- P0L6 t = 130 (peak.00016.rst, nothing trapped): not found after 16 and 18 iterations
  (mean radius negative, reason 4).
Your surfaces of the standard flow (S1L 10.73 after 1927 iterations, expansion integral
-0.63) are the same horizon, not converged in shape: with a start scan the standard flow
ends after 241 iterations at 10.7274, 1.1e-3 low, smallest radius 0.1596 against 0.1565.
So: 4000 iterations and a hand-made start radius are not needed, and masses read from
standard-flow searches of the box runs carry an error of 1e-3.

(b) The false acceptance: `<fastflow> trapped_tol_<n> = x` (new, off when absent) accepts
a surface only if its smallest radius is positive and the rms of its expansion times its
area mass is below x; column 16 of the status file then holds that number. It is 1.6e-3
on both converged horizons, 0.042 on the unconverged standard-flow surface of S1L, 0.5 on
a sphere well outside. A false acceptance of the same class as yours is reproduced and
refused: the finder's default `mass_tol 1e-2` with the standard flow is "found" at
iteration 2 on S1L (radius 0.5998, mass 21.8) and on P0L6 at t = 130 where nothing is
trapped (radius 0.5996, mass 15.3); with `trapped_tol 0.05` both are not found (reason
7). **Your event at t = 118.12 itself is NOT retested** (no restart file between 110 and
120): by the numbers of your status file its surface fails the check twice (smallest
radius -3.59; expansion integral times mass over area 7.4), which is a reading, not a run.

(c) Regression case: yes. S1L's file with the probe of your request is in core's card
check (entry q0086) and in `tracks/core/analysis/faces_finder/case_*.json`.

Also new: `start_scan_<n> = N` (start from the outermost trapped round sphere of a scan;
no trapped sphere: no flow, reason 8, at the cost of N evaluations). On S1L it starts at
0.16151, on P0L6 at 0.103970. With the weighted flow it saves little; it makes a search
where nothing is trapped cost 24 evaluations instead of a flow.

Recommended deck lines for the box runs:
```
<fastflow>
flow = shear
diagnostics = true
mass_tol_0 = 1.0e-5
polish_iterations_0 = 100
flow_iterations_0 = 400
trapped_tol_0 = 0.01       # needs the executable below; the rest works with core-v0.8
```
For condition (b) on the existing restart files you need no new executable:
`.work/build_gpu_v08` or `build_cpu_v08` with `fastflow/flow=shear`.

## 2. Deposit at level faces: every one of your refined runs with compensation changes

Two changes without an option (`level_faces.md`): (i) the linear cloud with
`deposit_fine_shape` no longer leaves a dipole of -+1/8 at a level face that is not
capped; (ii) the compensation pass (`deposit_comp_c`) is conservative across level faces.
With your settings (cubic cloud, c = 1/6, c2 = 0.4667) on a three-level test mesh the
integral of E now equals the particle sum to 2.7e-14 where core-v0.8 loses up to 9.9e-4
(run core-20261127-234843-fa6c2e9); on the lead's uniform lattice the line sum is 32
instead of 32.0413 (run core-20261127-234848-7d666df). What it does NOT do: the ripple of
the deposit itself at a level face (0.2 to 0.34 of the density in the cells at the face
in the lead's lattice test) stays; the coarse cells at level faces change by c times the
jump of the deposit. Core has not run your set-up: whether your constraint floor moves
is your retest (decision 0047 item 2(a)), and a null result is a result.

## 3. Executable for the retest

`/data/haiyangw/nrpic/scratch/core/exe/core_faces-finder/athena_gpu` (sha256 20172cae7f46...;
READY, COMMIT, SHA256SUMS there), processors `athena_cpu` (serial) and `athena_cpu_omp`
(threaded: your S1L probe with three threads gives the serial surfaces to 1e-14 in 81 s,
run core-20261128-001900-aefdc7b). Scouting status (decision 0013): byte regression against core-v0.8 PASS, 75
of 75 (run core-20261128-000404-015d78b); **the card build is untested until core's card
check q0086 has run**: look at `nrpic-queue show q0086` or the READY before you put card
hours on it. Processor retests can start now. Parameters that your restart files do not
hold can be given on the command line of a continued run with this executable
(`restart_parameters.md`).
