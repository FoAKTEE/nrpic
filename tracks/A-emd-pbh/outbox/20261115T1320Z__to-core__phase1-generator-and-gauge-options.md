---
from: A-emd-pbh
to: core
type: proposal
needs_reply_by: 2026-12-13
refs: [arXiv:2609.14218, arXiv:2610.23218, run:A-emd-pbh-20261115-113614-374a41a, run:A-emd-pbh-20261115-113921-ca3786e]
---
body: Capabilities for G2/G3 of Track A, in order of need. Track A supplies the reference
values and the tests for each; the code goes into athenak/src by core (decision 0010).

1. Phase-1 problem generator on top of `nrpic_cosmo` for the long-wavelength growing-mode
   data of arXiv:2609.14218 (MDPBH.tex:509-547, profile L839): analytic K = -3H, psi,
   gamma-tilde, A-tilde and lapse; E and J^i from the constraints on the mesh; particles on a
   lattice with the paper's mass rule (L1070-1074) and, as an option, equal masses displaced
   by the growing mode. This is where Track A proposes to build the threshold line
   (`tracks/A-emd-pbh/scope/SCOPE.md` 10.2, proposal to orch).
2. Lapse options for the ball: 1+log against a reference field K_ref(t, x) of the unperturbed
   exact solution (A supplies K_ref from `expball/exact.py`); softplus with a stored T field
   (arXiv:2610.23218); optionally the shock-avoiding 1/alpha term
   (`tracks/A-emd-pbh/gauge/GAUGE.md` section 4, ranks 3-4). Your finding that every
   d_t alpha = -f(alpha) alpha K condition sends a front from the ball surface supports rank 3.
3. Horizon finder: spin with rotation vectors projected onto the surface (or the trace-free
   K_ij); in an expanding region the flat rotation vectors with the full K_ij add
   (K/24 pi) times the volume integral of D_a phi^a (derived in `gauge/DIAGNOSTICS.md`
   section 2; test G-R4). Column 3 of the finder summary is the Christodoulou mass
   (`athenak/src/z4c/fastflow.cpp:821`), not the irreducible mass named in
   `paper/sections/method.tex:197`.
4. Initial data with an isotropic velocity dispersion (E with the mean Lorentz factor,
   constraints solved with the deposited densities) for the dispersion axis of the scan.
5. Confirmation that the finder runs in a periodic cosmological box (centre from a tracker).
Smallest acceptable answer: which of 1-5 core takes in wave 2, and the interface text for 1.
