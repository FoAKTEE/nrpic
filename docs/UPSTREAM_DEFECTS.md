# Defects found in upstream AthenaK code and what this repository does about them

Each item was found in a file that this repository carries unchanged from upstream
AthenaK (the state vendored under `athenak/`, before the change named in the item).
Nobody outside has been contacted about any of them: reporting upstream is the group's
decision (CLAUDE.md, rule 9). Evidence: run ids in `tracks/core/JOURNAL-bfix.md`.

## 1. `z4c_linear_wave`: the polarization tensor is not transverse for oblique waves

File: `athenak/src/pgen/tests/z4c_linear_wave.cpp`, upstream lines 107-112 (the
assignment of `axx` ... `azz`). Found by Track B (helper package periodic_z4c, confirmed
by its lead; `tracks/B-emd-gw/periodic_z4c/README.md`, Results item 2), confirmed by core
with an independent derivation (`tracks/core/JOURNAL-bfix.md`, "Source reading").

The generator sets a linear gravitational wave gt_ij = delta_ij + A e_ij sin(2 pi k.x),
At_ij = pi |k| A e_ij cos(2 pi k.x), with the angles
theta = atan2(sqrt(k1^2 + k2^2), k3) and phi = atan2(k1, k2), so that
khat = (sin theta sin phi, sin theta cos phi, cos theta). Four of the six components are
those of e+ = theta-hat theta-hat - phi-hat phi-hat (theta-hat = (cos theta sin phi,
cos theta cos phi, -sin theta), phi-hat = (-cos phi, sin phi, 0)); two have the wrong
sign:

| component | upstream | correct |
|---|---|---|
| `axy` | `-0.25*(3+cos(2*theta))*sin(2*phi)` | `+0.25*(3+cos(2*theta))*sin(2*phi)` |
| `ayz` | `+cos(theta)*sin(theta)*cos(phi)` | `-cos(theta)*sin(theta)*cos(phi)` |

Consequence: with the upstream signs e.khat vanishes only for k2 = 0 (any direction in
the x1-x3 plane) and for k along x2 or x3. For every other direction the data are not a
gravitational wave and violate the Hamiltonian and momentum constraints at first order
in the amplitude. For k = (1,1,1), the default of
`athenak/inputs/tests/linear_wave_z4c.athinput`, |e.khat| = 0.943 (largest component
0.770) and, at A = 1e-6 on 16^3 cells, the integrals of H^2 and M^2 are 1.385e-9 and
1.558e-9, against 4.6e-21 and 1.1e-21 with the corrected signs (what remains is of second
order in A: the wave's own energy). The trace and e:e = 2 are right with either sign, and
a test along a coordinate axis does not show the error.

Here: both signs are corrected (branch `core/requests-b`); for k2 = 0 and along the axes
the data change by rounding only (the terms are multiplied by sin(2 phi) or cos(phi),
which are 1e-16 there instead of 0). Added: the cross tensor
ex = theta-hat phi-hat + phi-hat theta-hat with `<problem> amp_cross`, `phase_cross`;
the error routine compares with the exact linear solution at the final time.

Remaining property, not a defect: for a general oblique k the data are transverse in
the continuum; the discrete divergence (sixth-order differences at `nghost = 4`) differs
from zero by the truncation error, so the constraints of the initial data converge as
h^6 (squared integrals as h^12) down to the second-order floor. Along (1,1,1) and along
the axes they are at the floor at every resolution.

## 2. Weyl scalar and waveforms: the time label is one step early; the mesh output lags

Files: `athenak/src/z4c/z4c_tasks.cpp` (`InitRecvWeyl`, `CalcWeylScalar`, `CalcWaveForm`
and the six Weyl communication tasks), `athenak/src/z4c/z4c_wave_extr.cpp` (the time
written to `waveforms/rpsi4_*.txt`), `athenak/src/driver/driver.cpp` (the time is
advanced after the task lists). Measured by Track B (gw_diag, run
B-emd-gw-20261115-120128-7dfaa38), confirmed at the source by core.

`InitRecvWeyl` runs before the last stage of the step that starts at a time
t >= last + `waveform_dt` (or at t = 0) and stores t. `CalcWeylScalar` and `CalcWaveForm`
run after the last stage, on the updated state, i.e. the state of t + dt, while
`pmesh->time` is still t. So:

- the rows of `waveforms/rpsi4_real_*.txt`, `rpsi4_imag_*.txt` are labelled t and hold
  Psi_4 of t + dt: every extracted waveform is early by one time step (a phase of
  omega dt, first order in dt);
- the mesh variable `weyl` keeps that array until the next waveform step, so a `weyl`
  output written at t_n holds the scalar of t_(n-1) + dt when the output and waveform
  cadences are equal (Track B: 7 steps of 1/128 before t_n with `waveform_dt` = 1/16);
- the scalar of the initial data is never computed (the row labelled 0 is the state of
  dt).

Here: `<z4c> waveform_at_new_time = true` chooses the step by the time at its end and
labels with that time: the row labelled t is Psi_4 of t, and a `weyl` mesh output at a
waveform time holds the scalar of that time. The default (parameter absent or false)
is upstream's behaviour, so that existing waveform runs keep their bytes. With the
option there is no row at t = 0.

## 3. Restart files carry 36 never-set bytes

File: `athenak/src/mesh/mesh.cpp` (constructor) and `athenak/src/outputs/restart.cpp`
(line 227 writes `Mesh::mesh_indcs` as a whole). The coarse-cell indices `cnx1`, `cnx2`,
`cnx3`, `cis` ... `cke` of `mesh_indcs` (9 integers) have no meaning for the Mesh as a
whole and are never assigned; the restart file therefore holds whatever the memory held
(leftover text of the input file in Track B's runs, lead's re-execution
B-emd-gw-20261115-131016-03b1119; also OPEN item 15 of core's G2 package). Two identical
runs give restart files that differ in these 36 bytes and in nothing else, which defeats
checksum-based verification of restart outputs.

Here: `Mesh::ZeroUnusedMeshIndcs()` sets the nine integers to zero in the constructor
and after a restart file is read. Restart files written before the fix are read as
before.

## 4. Remarks on the same files (behaviour kept, documented)

- The problem generator `z4c_linear_wave` sets the Z4c variables only; the ADM variables
  and the constraints are first computed in the first time step. The first history row
  and `adm`, `con` outputs at t = 0 therefore hold zeros. Use `variable = z4c` at t = 0.
- A history file of a Z4c run is called `<basename>.z4c.user.hst` (`scripts/README.md`).
