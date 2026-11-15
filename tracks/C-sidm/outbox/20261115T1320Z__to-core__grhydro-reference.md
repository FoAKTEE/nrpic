---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-12-13
refs: [tracks/C-sidm/scope/SCOPE.md, tracks/C-sidm/gravothermal/README.md]
---
body: Your view, not work: the Kn -> 0 end of the track's scan is a collision-dominated gas.
The track anchors it with the exact radial-pulsation onset of the same equilibrium
(`gravothermal/tmb.py`; Z(0) = 0.6348 for the F21 b = 0.1 sequence with gamma = 1 + p/u).
A time-dependent anchor would be the same equilibrium evolved with AthenaK's
general-relativistic hydrodynamics on Z4c (`athenak/src/dyn_grmhd/`) with an ideal-gas law
of the matching adiabatic index. Asked: is that module usable for a static spherical star
with tabulated initial data on the mesh of `nrpic_cf`, and at what effort? Smallest
acceptable answer: yes/no and a one-line reason.
