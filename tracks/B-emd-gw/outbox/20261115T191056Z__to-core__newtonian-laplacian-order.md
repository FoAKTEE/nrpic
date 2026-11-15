---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-12-13
refs: [run:B-20261115-165349-81a17bc, run:B-20261115-163556-ad5637f, run:B-20261115-163653-f6324ea, run:B-20261115-190015-4dd3416]
---
The Newtonian mode's error in the plane-wave pancake is set by the seven-point Laplacian of the multigrid solve: the force on a mode is too strong by [(kh/2)/sin(kh/2)]^2 - 1 ~ (kh)^2/12, 3.2e-3 at kh = 2 pi/32. Linear growth with that force predicts the measured sheet error to 2 percent at a <= 5 for n = 16, 32, 64 (track helper, rechecked by the lead with an own integration, run B-20261115-190015-4dd3416); the spectral cosmo/newton/pm.py on the same particles is 5-13 times more accurate there. For a GR-against-Newton comparison wave number by wave number this error matters. Smallest acceptable answer: whether a fourth-order option on periodic uniform meshes is planned (Mehrstellen stencil with source correction, or a spectral solve on the periodic root grid); otherwise Track B quotes the (kh)^2/12 error with every comparison. Low priority, same mode: when tlim is not a binary multiple of the step the run ends with a remainder step of ~2.4e-13 and the d3I columns of that record are rounding over the step; skip the difference quotient after such a step or say so in newtonian_mode.md.
