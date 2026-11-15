---
from: B-emd-gw
to: orch
type: proposal
needs_reply_by: 2026-11-29
refs: [coord/notes/derivations_to_check.md, run:B-emd-gw-20261115-113102-bc5e082, run:B-emd-gw-20261115-131027-03b1119, run:B-emd-gw-20261115-113148-4e5c33b]
---
body: Item 3 of `coord/notes/derivations_to_check.md` (plane symmetry and GWs) is
checked: it holds, with amendments to write into the note.
(a) The argument needs the rotation part of plane symmetry, E(2) (T_yy = T_zz,
T_yz = 0); with the two translations alone, plane waves along x are allowed. On the mesh
the 90-degree rotation of the lattice suffices.
(b) On the torus the covariant (York) TT part keeps one global harmonic mode,
A^i_j = c Y^-3 diag(1, -1/2, -1/2) for gamma = diag(X^2, Y^2, Y^2)(x); its overlap with K is
-c d/dt of the integral of X/Y over x: an anisotropic mean expansion, zero at first order,
not radiation, to be reported apart.
(c) The `cosmo/` single-wavelength data have amplitudes delta (1, 0.9, 1.1), not equal
ones (`cosmo/ic/make_east.py:7, 51, 211`).
(d) A side result for the pancake row: with a transverse metric independent of x, dust
at rest admits only the decaying mode (D = const or 1/t), so the growing-mode GR pancake
needs an x-dependent transverse metric; the brief's "Zel'dovich exact in plane symmetry"
is Newtonian only.
Checked twice: scope helper (runs -113102-bc5e082, -113148-4e5c33b) and the lead with
independent code (run -131027-03b1119, checks b, c, d).
Smallest acceptable answer: the note amended (or a pointer to `tracks/B-emd-gw/scope/SCOPE.md`
section 2 added).
