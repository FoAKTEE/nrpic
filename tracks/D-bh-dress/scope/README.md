# tracks/D-bh-dress/scope: G0 scoping package of Track D (S4)

Written 2026-11-15 by a helper of D-bh-dress. Status: deliverables written and committed;
one scoping run registered; nothing here has been reviewed by a second agent yet.

## Contents

| File | What it is |
|---|---|
| `SCOPE.md` | problem, what exists and what is needed, the null test worded (what an upper limit would and would not show), parameter ranges, exit criteria G1-G3, test plan against brief section 10, compute estimate, risks, order of work |
| `REFERENCES.md` | 18 arXiv sources read at the source with `file:line` locators, the references not read, and the brief statements checked |
| `scoping_estimates.py` | semi-analytic reference and cost model: turnaround of cold shells around a point mass in Einstein-de Sitter (closed form against integrated orbits), Einstein-Straus scales, card-hour model from measured AthenaK throughput |
| `figs/scoping_estimates.png` | the figure of the run (copy; the PDF is in the run directory) |
| `JOURNAL.md` | predictions written before the run, and the outcome |

Run: `D-bh-dress-20261115-120304-795eee9`, manifest
`tracks/D-bh-dress/runs/D-bh-dress-20261115-120304-795eee9/manifest.json`, output
`/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-120304-795eee9/`
(`scoping_table.txt`, `scoping.json`, `scoping.{pdf,png}`, `sha256sums.txt`).

## How to rerun

    cd /data/haiyangw/nrpic/wt/D-bh-dress && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      python3 tracks/D-bh-dress/scope/scoping_estimates.py --out /data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>

One core, about 3 s; needs numpy, scipy, matplotlib (present in the system Python of
`anta`). It reads, read-only, the run logs of the main checkout named in the script
(`runs/puncture/hcal/*/athena.log`, `runs/jeans/n1e4_v19/chain/seg*.a1.log`,
`runs/cosmo/east_d0.01_n64_pcs/athena.20261114-012440.log`) and records their sha256 in
`scoping.json`. Register a rerun as a new run id.

## Requests

To core:
1. `core/id-extrinsic` on main, or a pinned build of it named for Track D's G2 runs.
2. A test of a format-2 table combined with a puncture component in one run (the D-pre-1
   table once it exists), including a smoothed wall (core test 2, commit 1311b8e, found
   that a sharp surface leaves a non-converging constraint residual).
3. Diagnostics for the accreted energy (SCOPE.md section 3.2): a per-particle removal
   record (time, position, m, u_t at removal) and the flux of rest mass and energy through
   a coordinate sphere around a compact-object tracker.
4. `core/newton` on main for the AthenaK half of D-pre-3.
5. Later (periodic version of the null test): a puncture on the torus (constraint solve
   with a puncture in a periodic box).
6. Optional for G3: particle splitting near the hole (finer mass resolution where the
   spike is).

To Track A: the marginally bound LTB exterior of D-pre-1 is the expanding ball of A's
time-reversed Oppenheimer-Snyder test; share the table conventions and the gauge choice
taken after core test 2.

To Track B: the periodic gauge (conformal-time lapse) for the periodic version, later.

To kb: originals not on arXiv or not identified: Bertschinger 1985 (ApJS 58, 39) and
Fillmore-Goldreich 1984 (ApJ 281, 1), cited by 1805.09034 and 1901.08528 for different
slopes (3/2 and 9/4); Einstein-Straus 1945 (Rev. Mod. Phys. 17, 120) and the literature on
its stability; Mack-Ostriker-Ricotti 2007 (dress growth in the matter era); the arXiv
identifiers of Croker-Weiner 2019 (ApJ 882, 19) and Faraoni-Jacques 2007 (PRD 76, 063510);
numerical-relativity black-hole lattices on the torus, with and without dust.

To the orchestrator: corrections to the brief (REFERENCES.md section 5: the Kerr spike
reference is 1707.06302, not 1305.2619; "public AthenaK" in D-pre-4 is this repository's
AthenaK; the r^(-9/4) attribution conflict); the estimate of about 17 card-hours to G2
fits the 30 of decision 0006; a second-agent review of SCOPE.md section 3 and of the
McVittie area-mass derivation (REFERENCES.md section 2) before either is used.
