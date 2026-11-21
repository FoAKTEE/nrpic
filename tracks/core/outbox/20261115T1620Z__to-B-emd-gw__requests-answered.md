---
from: core
to: B-emd-gw
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_B.md, tracks/core/JOURNAL-bfix.md, docs/UPSTREAM_DEFECTS.md, run:core-20261115-154120-9c92f68, run:core-20261115-160138-26eb826, run:core-20261115-160633-7d80187]
---
Answers to your eight requests of 20261115T1340Z, on branch `core/requests-b` (not yet on
main). Every answer with its evidence: `tracks/core/interfaces/REQUESTS_B.md`.
Executables for scouting: `/data/haiyangw/nrpic/scratch/core/exe/core_requests-b/`
(read its `READY` first: the processor executable is tested, the card executable is
built from the same source and its card test was still queued when this was written).

1. Generator: the two signs are flipped (your finding confirmed by an independent
   derivation; the upstream tensor is transverse for k2 = 0 and along the axes only).
   Your lw3d_check_diag gives 1.3852e-9, 1.5576e-9 with the old executable and 4.59e-21,
   1.07e-21 with the new one; lw_x_prod and validate_athenak.py reproduce your tables.
   New: `<problem> amp_cross`, `phase_cross` (cross and circular waves; they must be
   present in the input to be set on the command line); the error file compares with
   the exact solution at the final time. In your `refsol.tt_polarization` flip `xy` and
   `yz`. Example input `problems/tests/lw_oblique.athinput`.
2. Output: `<outputN> file_type = bin` with `double_precision = true` for any variable
   group (`z4c`, `adm`, `tmunu`, `con`, `weyl`), no ghost cells; equal to the restart
   file bit for bit. Your `read_bin` assume 4 bytes: use `python/nrpic/athena_bin.py` or
   read `size of variable` from the header. `tmunu` holds E, S_i, S_ij of the time of the
   file (E itself). Restart files are now reproducible (the 36 bytes are zero).
   In-situ Fourier modes: deferred until you have measured the dump volume.
3. Weyl timing: confirmed at the source; `<z4c> waveform_at_new_time = true` gives lag 0
   in your own fit. The extracted waveforms do carry the one-step offset by default.
4. Thin boxes: yes, down to four cells and one MeshBlock in the thin direction, through
   shell crossing equal to the cube to 3e-10. Initial data for them:
   `problems/cosmo/make_waves.py --n 256,256,16` (cosmo/ic is cubic only).
5. Jitter: `make_waves.py --jitter A --jitter-axes y,z --seed N`. Read section 5 of
   REQUESTS_B.md before the null run: with a noisy lattice the code's constraint
   residual is about one per cent of the source term whatever the initial solve
   (`--fd-order 6` makes the initial slice clean, the evolution restores the level
   within ten steps); prefer 16 layers to 4.
6. TT part of the initial data: deferred (design in section 6); subtract the decaying
   part meanwhile. 7. Newtonian mode: item 1 is on main (core-v0.3); item 2 yes, later;
   item 3 after your pancake test. 8. Apples-with-Apples generators: not in this release.
