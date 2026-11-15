# tracks/A-emd-pbh/scope: G0 scoping material for S1

Helper "scope" of owner A-emd-pbh, wave 1, 2026-11-15. For the lead, who writes the G0
stage package from it.

## Contents

| File | What it is |
|---|---|
| `SCOPE.md` | problem statement; position against arXiv:2609.14218 with hypotheses H1-H4; the threshold definition fixed before any run; set-ups (phase 1 periodic, phase 0 ball); parameter ranges of the first scan; diagnostics; exit criteria and the test plan on the rows of brief section 10 that Track A holds; risks; compute estimate |
| `REFERENCES.md` | the twelve key references of brief S1 read at the source: set-up, quantities, threshold and spin statements, method, particle numbers and resolution, what is not computed, each with `file:line` locators in the shared store |
| `scope_calc.py` | semi-analytic tests T1-T5 (hoop criterion, collapse times, ball geometry, dispersion axis and particle floor, compute model); only reference relations and arithmetic, no simulation |
| `JOURNAL.md` | predictions written before each run and the outcomes, including the failed first run |
| `results/` | copy of the output of run `A-emd-pbh-20261115-112625-e854f12`: `scope_numbers.json` and the four figures (`fig_hoop`, `fig_timing`, `fig_design`, `fig_cost`), each inspected |
| `run_manifests/` | copies of the three run manifests (see Requests: the originals under `tracks/A-emd-pbh/runs/` are ignored by git) |

## How to rerun

From the worktree root, on a processor (2.7 s, one core):

    RID=A-emd-pbh-$(date -u +%Y%m%d-%H%M%S)-$(git rev-parse --short=7 HEAD)
    OUT=/data/haiyangw/nrpic/scratch/A-emd-pbh/$RID
    mkdir -p $OUT
    OMP_NUM_THREADS=1 python3 tracks/A-emd-pbh/scope/scope_calc.py --out $OUT

then write `tracks/A-emd-pbh/runs/$RID/manifest.json` (template: `run_manifests/`).
Needs numpy, scipy, matplotlib (user site; do not use `python3 -I`, which hides them; the
script reads no downloaded file). The compute model reads the chain logs of
`/data/haiyangw/nrpic/runs/jeans/n1e4_v19` (read only; option `--v19`); without them it
falls back to the measured total written in the script.

## Status

Done: (a) references with locators; (b) problem statement and position; (c) parameter
ranges and the threshold definition; (d) exit criteria and test plan; (e) risks;
(f) compute estimate. T1-T4 hold as predicted; T2 has one read-off outside its interval
(mu = 0.3, e = 0.2), within the stated tolerance; T5 is a model that only production runs
can test.

Not done: no AthenaK run (the package has no card time and the capabilities for phase 0
and phase 1 are not on main yet); arXiv:1708.09143 (Szekeres, row A4), arXiv:2608.13206
and arXiv:2403.15126 not read; the horizon-mass error of the source paper's
Oppenheimer-Snyder test not looked up (G2 criterion, marked [TO VERIFY]); the boundary
conditions of arXiv:2609.14218 are not stated in its source and remain [TO VERIFY].

## Requests

- orch: `.gitignore` line 12 (`runs/`) also matches `tracks/*/runs/`, so the run manifests
  that the protocol puts there cannot be committed (CLAUDE.md forbids committing ignored
  paths). Proposed: add `!tracks/*/runs/` after it. Until then copies live in
  `scope/run_manifests/`.
- core: (1) a problem generator on top of `nrpic_cosmo` for the long-wavelength
  growing-mode data of arXiv:2609.14218 (MDPBH.tex L509-547 and L839: analytic K, psi,
  gamma-tilde, A-tilde, lapse; E and J from the constraints on the mesh; particles on a
  lattice with the paper's mass rule, L1070-1074, and as an option equal masses displaced
  by the growing mode); Track A supplies the reference values and the tests; (2) initial
  data with an isotropic velocity dispersion (E with the mean Lorentz factor, the
  constraints solved with the deposited densities, design note item 2); (3) the halting
  tests A6 (SCOPE.md section 7) as acceptance tests of `core/newton`; (4) confirmation that
  the horizon finder runs in a periodic cosmological box (initial guess at a tracker,
  mass and spin).
- B-emd-gw: the slicing and shift for collapse in a periodic box, shared with A-pre-4
  (arXiv:2610.23218 shows the standard choices fail); a test that A can reuse: the
  spherical profile of arXiv:2609.14218 at mu = 0.5, e = 0 (their "HF w/o crash" case).
- kb: ingest arXiv:1708.09143, arXiv:2608.13206, arXiv:2403.15126 and arXiv:2605.30145
  (Galoppo, Bruni, Harada, spherical dust collapse from CDM-curvature peaks; cited by
  arXiv:2610.23218, Ref.bib L280-286, not read here); the statements
  and locators of `REFERENCES.md` can seed the entries of the twelve key references.
- A-emd-pbh lead: decide the order phase 1 before phase 0 for the threshold line
  (SCOPE.md section 4, from T3); ask for the card-hour raise for G3 (~155, factor-3 band)
  when G2 passes.
