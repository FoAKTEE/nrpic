# nrpic

Independent re-implementation of the numerical-relativity particle-in-cell (NRPIC)
method for the Einstein-Vlasov system (Wu & Most, arXiv:2611.12831) on top of
[AthenaK](https://github.com/IAS-Astrophysics/athenak), with reduced-particle-number
tests run on GPUs and a Physical Review D style write-up.

- `PLAN.md`: scope, design, milestones, and target numbers.
- `athenak/`: AthenaK source (upstream commit `c5a0d7f`, BSD 3-clause, see
  `athenak/LICENSE`) with the NRPIC additions. Kokkos is a git submodule.
- `python/nrpic/`: reference geodesic integrators, pusher prototypes, initial data.
- `problems/`, `analysis/`, `paper/`, `docs/`: runs, post-processing, manuscript, notes.

Clone with `git clone --recursive`. Build instructions are in `scripts/`.

## Paper

- Manuscript, complete (PDF, rebuilt with the sources; author list and funding line
  left for the authors): [paper/main.pdf](paper/main.pdf)
- LaTeX sources: [paper/](paper/) (`main.tex`, `sections/`, figure scripts in `scripts/`,
  reduced data in `data/`)
- Record of every test, prediction and outcome: [docs/TESTLOG.md](docs/TESTLOG.md)
- Build: `cd paper && latexmk -pdf main.tex`

## Cosmology extension

The code extended to an expanding, periodic universe, with three source papers redone
(East, Wojtak & Pretorius, arXiv:1908.05683; Daverio, Dirian & Mitsou, arXiv:1904.07841;
Barrera-Hinojosa & Li, arXiv:2001.07968).

- Overview, options, a run from start to finish: [cosmo/README.md](cosmo/README.md)
- Working paper (text, figures, ledger of numbers): [cosmo/paper/main.pdf](cosmo/paper/main.pdf)
- Plan and state: [cosmo/PLAN.md](cosmo/PLAN.md); every test with its prediction and
  outcome: [cosmo/TESTLOG.md](cosmo/TESTLOG.md)
