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

- Current draft (PDF, rebuilt with the sources): [paper/main.pdf](paper/main.pdf)
- LaTeX sources: [paper/](paper/) (`main.tex`, `sections/`, figure scripts in `scripts/`,
  reduced data in `data/`)
- Record of every test, prediction and outcome: [docs/TESTLOG.md](docs/TESTLOG.md)
- Build: `cd paper && latexmk -pdf main.tex`
