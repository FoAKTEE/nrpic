"""gwdiag: gravitational-wave diagnostics for a periodic domain (track B-emd-gw, B-pre-3).

Modules: grid (mesh and array layout), tt (transverse-traceless projection, polarizations,
energy spectra), weyl (E_ij, B_ij, Psi_4), analytic (reference fields), readers (AthenaK
restart, binary and NRFIELD dumps). See ../README.md.
"""
from .grid import Grid, axis_of  # noqa: F401
from . import tt, weyl, analytic, readers  # noqa: F401
