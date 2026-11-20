# Journal of package a4res (E-stoch-inf, wave 3 round 1)

Pre-registered test of the resolution criterion for the strict A4 (the constraints second
order in the noise amplitude during the entry; SCOPE 4) against the reading A4' (SCOPE 4b;
outbox 20261119T151727Z__to-orch__a4-a5-rewording.md). Times in UTC.

## Entry 1, 2026-11-20 22:22Z: what was read, step 1 (stencil symbols) set up

Read: CLAUDE.md, coord/CHARTER.md to "Owners", decisions 0010 and 0016-0019, SCOPE 4 and
4b, the outbox proposal, `../ladder/README.md` and `../ladder/JOURNAL.md` entries 1, 6, 8,
9, 11, `../ladder/scripts/ladder_lib.py` and `ladder_analysis.py` (pair, judge),
core's `tracks/core/interfaces/scalar_field_3.md` section 4, `python/nrpic/sf_lattice.py`
and `tracks/core/analysis/scalar3/a1_twin.py` on `core/scalar-3` (18bae3c), the READY of
`scratch/core/exe/core_scalar-2/` (executables of a58e95b), `athenak/src/utils/
finite_diff.hpp` and the derivative calls of `z4c_calcrhs.cpp`, `z4c_adm.cpp`,
`scalar_field_rhs.cpp`.

What core claims (another owner, unmerged branch) [TO VERIFY by this package]:
C1 the first-order part of H, M_i at late entry is the defect mu = kap - q^2 of the
discrete contracted Bianchi identity, mu/k^2 = 0.110, 2.6e-3, 4.4e-5 at 4, 8, 16 cells per
wavelength; C2 the largest ratio in time of first- to second-order part falls below 1 at
12.7 and below 0.1 at 18.7 cells per shortest source wavelength (scan at nmax2 = 64 with N
varied: twin odd part over the measured even part of core's 64^3 runs; values 692, 213,
77, 14.9, 4.0, 1.38, 0.25 at 4, 5, 6, 8, 10, 12, 16 cells); C3 strict A4 needs
nmax2 <= (N/12.7)^2; C4 (remark on SCOPE 4 A2) the ladder's stencil-k^2 reference (6.2e-3
against 1.2e-4 at 256^3) "may use the second-order stencil symbol", the code's sixth-order
symbol being 1.8 percent low at k dx = pi/2.

Facts read in the source [VERIFIED by reading]:
- Z4c and the scalar field use `Dx` (first difference), `Dxx` (second difference, the
  diagonal second derivatives) and `Dxy` (the product of two first differences, the mixed
  ones) of `finite_diff.hpp`; with `nghost = 4` (input) these are the sixth-order stencils.
- The mode file: `scalar_field_noise.cpp` at a58e95b (the commit of the executable),
  lines 401-431: a row whose |n|^2 is not a shell of the mode set (0 < |n|^2 <= nmax2) is
  skipped ("if (it == shell_of.end()) continue;"); a missing shell is fatal;
  `noise_mode_scale` multiplies R and dR/dtau of every shell (slice and sources). So the
  rows of `modes_n4096.txt` beyond noise_nmax2 are ignored, as coord/INTERFACES/
  scalar_field.md section 7.3 says ("extra rows ignored"). CONFIRMED.
- `ladder_lib.py:270-277` (`k2_stencil`, used by `reference_modes_stencil` for the A2
  'stencil-k^2' reference) is the sixth-order symbol per axis,
  -(-49/18 + 3 cos th - 0.3 cos 2th + (2/90) cos 3th)/h^2, not the second-order one.

Step 1 (script `scripts/stencil_symbols.py`): parses the coefficients of Dx and Dxx for
NGHOST = 2, 3, 4 from the source, forms q h, kap h^2 and mu/k^2 at 4, 5, 6, 8, 10, 12, 16
cells, and evolves the ladder's linear reference with the continuum k^2 and with the
sixth-, fourth- and second-order k^2 for all 3363 wave-vector classes |n|^2 <= 1024 of
P256 to t = 8.5.
Expectation: C1 holds to the quoted digits (it is arithmetic on the coefficients, which
the ladder's entry 8 already read as 1/90, -3/20, 3/2, -49/18); for C4, the sub-horizon
phase error of the sixth-order k^2 accumulated over about 31 radians for |n| = 32,
k dx = pi/4 (0.5 x 3.8e-4 x 31 = 6e-3), reproduces the ladder's 6.25e-3, while the
second-order symbol (5 percent low in k^2 at pi/4) would give an O(1) difference: C4
refuted. Refuted if the sixth-order reference differs from the ladder's number by more
than 1 percent, or the second-order one matches it.
Disclosure: a development run of the script (not registered, `scratch/E-stoch-inf/tmp/
sym_test`, 22:20Z) already printed the numbers before this entry; the registered run
below is the one cited.
