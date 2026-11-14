# Cosmology with NRPIC: test log

Rules as in `docs/TESTLOG.md`: every explanation is written with a prediction before the
run that could refute it; later entries and entries titled "Correction" override earlier
ones; "not determined" where no run isolates a cause. Times are local (PST).

## Plan and design (2026-11-13, 23:40)

Sources of arXiv:1908.05683, 1711.06681, 1904.07841, 2001.07968, 1905.08890, 1101.3555
and 1111.2997 downloaded to `refs/`. Paper 1 and the method part of its predecessor read
in full by me; specifications of papers 2 and 3 being extracted by two agents into
`cosmo/notes/`. Plan in `cosmo/PLAN.md`; working paper `cosmo/paper/main.pdf`.

Design decisions and the estimates they rest on (to be checked by the first tests):
- Lapse condition d_t alpha = -(1/3) alpha^2 K gives alpha = a on the homogeneous
  solution, so t is conformal time and the time step can stay fixed. Estimate: a = 1 to
  56 takes 2 (sqrt(56) - 1)/H_0 = 13.0/H_0 = 3.2 box lengths (L = 4/H_0), i.e. 830 steps
  at 64 cells per side and a step of a quarter cell.
- Constraint solve with the particles held fixed: linearized Hamiltonian operator
  Laplacian - (5/12) K^2 - 2 pi E = Laplacian - (9/2) H^2 on the background.
- Relativistic Zel'dovich displacement: divergence of the displacement equals
  -(delta_N - 5 psi_N); for the single-wavelength data of paper 1 the displacement is
  (1 + 7.5 (H/k)^2) = 4.04 times the Newtonian one.
