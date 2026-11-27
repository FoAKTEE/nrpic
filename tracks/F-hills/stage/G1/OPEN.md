# G1 of F-hills: what the gate still lacks (2026-11-27, lead, batch 34)

The lead judges the package complete for an independent review (decision 0016 item 4): C8 is now
met; what remains open is the verifier's rerun on the completed passage (item 2), failed
predictions on record, and finding F1 decided in part. The lead does not pass the gate.

1. **A complete vacuum Hills passage (T4, CHECKLIST C8): MET.** P1b at m/16: A
   (F-20261121-203144-b2cf16b, 0-61.8 M) + A2 (F-20261124-210400-902c650; 133.0-186.0 M by queue
   entry q0069 with `<fastflow> diagnostics = true`) joined 0-186.0 M without a gap
   (F-20261127-232849-14345be). The chain ended at 186.0 M because Slurm refused the next
   submission ("I/O error writing script/environment to file", chain/slurm-5492.out), not at its
   cap; closed `--status stopped`. Outcome from the horizons (F-20261127-232657-163727d): the
   binary is disrupted between 120 and 133 M; m1 is captured by M (common horizon from 137.5 M,
   area mass 1.0053 -> 1.1137); m2's horizon is found at every search to 186 M with constant
   mass, m2 passes M at 8.73 M (134.3 M, tracker) and recedes on a marginal orbit (bound or not
   undecided). Newton from the same deck ejects m1 and binds m2 (F-20261127-232940-3f652bf). One
   resolution only; C2 (m/12) stopped at 106.69 M and belongs to G2.
2. **Verifier of the G1 material (C18): PARTIAL; the rerun follows this session.** The fresh
   verifier (batch 22, VERIFIER.md) checked the passage to 96.23 M. To rerun on the completed
   passage (VERIFIER.md section 7: `stage/G1/verifier/scripts/run_all.sh`):
   - the passage 96.23-186.0 M from its own readers: A2-2 from `vpassage.json`
     `state_at_end.d_cm_minima`; A2-3 from `d0`, `d1`, `E_0M_units`, `E_1M_units` and the
     Newtonian fates; A2-4 and A2-5 from the member and heavy horizon blocks and
     `heavy_A2_branches` (F1);
   - NEW for the verifier: the finders' status files `hills.horizon_status_<n>.txt` of A2
     (133.0-186.0 M). Their rows end with `# <reason in words>`: a reader that splits on
     whitespace and parses every token as a number (as nr_first/scripts/nrread.py read_table
     does) reads no row at all (the lead's first run failed this way, F-20261127-232531-8d16e2c).
     The common horizon of m1 and M (finder 2's jump at 137.5 M), the end of m1's own horizon
     (about 141 M), the spurious "found" surfaces of finder 0 after 141 M (area mass 0.8-1.04,
     |mean expansion| 1-24) and m2's horizon to 186 M are the lead's readings to check;
   - left unchecked by the verifier (VERIFIER.md section 6, unchanged): F-pre-1 (newton3,
     0911.1136, 1804.02911) and KHSR beyond four points (retrograde, r_a = 500, 200, 130, K3c/K3d);
     F-pre-2 (geodesic_binary, kerr); the eih package (EIH separations, 1PN scans); the note v2
     ledger except rows 122, 126 (in part), 128, 168, 194, 200, 201, 203, 205, 207; P1's remnant
     spin (row 204), radiated energy (row 208) and recoil; the batch-11 card analysis beyond the
     quantities of its section 3.3 (N1/N1m tide, F-20261124-132934-375a163); the single-member
     junk (S2g) and its scaling; the junk at P1b's spheres.
3. **Failed predictions on record (not blocking; C19).** A2-1 (timing), A2-2 (the centre of mass
   did not turn in 95-115 M), A2-3 (m1 captured, no member beyond 30 M at 170 M), A2-4 (common
   horizon of m1 and M), A2-5's heavy-hole clause (1.55e-3 by 133 M, then the merger), H2 in
   part, H4 (batch 21), C25-1's tracker clause, C25-3's rate clause, D34-1, D34-2 in part
   (JOURNAL batches 21, 25, 34; VERIFIER.md section 4 for the verifier's own).
4. **Note v3.** The passage section to 186 M (disruption, capture of m1 with the common horizon,
   m2's recession, against Newton's reverse fates), what is a coordinate reading and what the
   horizons show; the junk at P1b's spheres (T3 reservation); ledger row 194 without an "order"
   (verifier F2); "5.5e-7 raw" and "+0.32 percent from the search at 4 M" (verifier f); the
   duplicated legend of fig_elliptic; floats after Sec. VI; the reviewer step.
5. **Finding F1 (verifier): decided in part.** From the status files (F-20261127-232657-163727d,
   fig_b34_f1): after the restart at 133.0 M the heavy hole's finder gives ONE branch to 135.2 M,
   at the upper level (1.00443 at 133.0 M); two branches reappear when m1 is within about 2 M,
   both "found", with equal median |mean expansion| (4.64e-3, 4.61e-3). The status file does not
   separate them: the finder stops after a median of 6 flow iterations at puncture_setup's
   tolerance, so "found" means the mass rule held, not a vanishing expansion. Which branch of
   86.6-133 M is the converged surface is not established [JUDGEMENT: the lower one is a plateau
   of a flow stopped early, as in coord/INTERFACES/finder_stop.md]. Decisive test (G2 list):
   polished searches (core-v0.8, `polish_iterations = 100`, `mass_tol = 1e-5`, and `mass_tol =
   1e-9`) on two or three of A2's restart files between 87 and 133 M. Heavy-hole numbers quoted
   to 1e-3 before 133 M carry the branch named.
6. **Reservations on T3 (C7)** as before: criterion (iii) met at its edge (19.8 against 20
   percent, verifier F4); junk measured with P1's m/8 binary; to be remeasured at P1b's spheres
   (A2's waveforms are now complete to 186.0 M).
7. **Small defects listed, not fixed.** `three_punctures/scripts/newton_start.py` reads the
   pre-fix energy fields; `nr_first/scripts/single_analysis.py` repeats the last mass after a
   run's end; binary_conv's README "Results" row for 20 M at m/16 out of date; geodesic_binary
   S4 (chart 'cks') carries the slicing pump; `nrread.read_table` skips status rows (item 2);
   b11_passage's energies of m1 after the merger are meaningless (distance to M 1e-9) and its
   M is the pre-merger mass; the title of fig_b21_a2_state still says PARTIAL.
8. **For G2 (not G1).** B2 (F-20261126-052133-10f9a5f, done at 140 M) and C2
   (F-20261126-131751-89eaff8, stopped at 106.69 M; continue from its restart file) to analyse;
   F1's polished-finder test; g2mesh G2M-2/3; the gauge leg; C's member drift above A4's bound.
