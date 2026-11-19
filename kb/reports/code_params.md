# Parameter index (K6, brief 12.7)

Every call of the ParameterInput interface in the C/C++ sources (`kbtool/code_params.py`; cross-checked against a tree-sitter extractor, test P2). `access`: get = required, get_or_add = optional with the default shown, exists = `DoesParameterExist`. A block in braces is computed at run time (the expression is shown). Full tables: `code_params_<repository>.tsv` next to this file.

## AthenaK upstream (inputs/): `IAS-Astrophysics/athenak` at c5a0d7f9155a

- calls: 1165 (block_exists 49, exists 27, get 293, get_or_add 730, set 66)
- reads (get, get_or_add): 1023; distinct literal (block, name): 574; reads with a computed block or name: 242
- input files: 148 with 8670 parameter lines; literal 6356, computed block 1871, computed name fitting its pattern 101, `<comment>` block 234, name read under another block 9, unmatched 99; literal or computed block: 8227 = 94.9 %; with the patterns: 8328 = 96.1 %; without the <comment> lines: 98.7 %

Unmatched lines are typing errors in input files, options that the code no longer reads, or names built from a plain variable (no literal to match, for example `<particles> field_time1`).

Input parameters not read with that block and name (count of input lines, first file):

| block | name | lines | status | first file |
|---|---|---|---|---|
| coord | m | 7 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:79 |
| z4c | nco | 7 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:144 |
| problem | l | 7 | unmatched | inputs/grhydro/gr_fm_torus_smr.athinput:105 |
| problem | do_initial_debug_output | 5 | unmatched | inputs/z4c/onepuncture/z4c_onepuncture_spinning_ahf.athinput:139 |
| amr_criterion1 | trun_fac_0 | 5 | unmatched | inputs/zoom/zoom_bondi.athinput:57 |
| amr_criterion1 | trun_fac_1 | 5 | unmatched | inputs/zoom/zoom_bondi.athinput:58 |
| amr_criterion1 | trun_fac_2 | 5 | unmatched | inputs/zoom/zoom_bondi.athinput:59 |
| fastflow | store_metric_drvts | 4 | unmatched | inputs/z4c/onepuncture/z4c_onepuncture_ahf.athinput:92 |
| mhd | ohmic_resistivity | 3 | unmatched | inputs/mhd/resistivity.athinput:44 |
| output2 | user_hist | 3 | other_block | inputs/z4c/awa/z4c_gauge_wave.athinput:66 |
| z4c | npunct | 3 | other_block | inputs/z4c/spectre_bbh/z4c_spectre_bbh.athinput:91 |
| z4c | bh_0_x | 3 | unmatched | inputs/z4c/spectre_bbh/z4c_spectre_bbh.athinput:92 |
| z4c | bh_1_x | 3 | unmatched | inputs/z4c/spectre_bbh/z4c_spectre_bbh.athinput:93 |
| mhd | pwp_density_pieces_0 | 2 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:101 |
| mhd | pwp_density_pieces_1 | 2 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:102 |
| mhd | pwp_density_pieces_2 | 2 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:103 |
| mhd | pwp_density_pieces_3 | 2 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:104 |
| mhd | pwp_gamma_pieces_0 | 2 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:105 |
| mhd | pwp_gamma_pieces_1 | 2 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:106 |
| mhd | pwp_gamma_pieces_2 | 2 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:107 |
| mhd | pwp_gamma_pieces_3 | 2 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:108 |
| mhd | pwp_gamma_thermal | 2 | unmatched | inputs/dyn_grmhd/kadath_bns.athinput:109 |
| problem | bamb | 2 | unmatched | inputs/grmhd/blast_grmhd_amr.athinput:79 |
| radiation | beam_source | 2 | unmatched | inputs/radiation/beam.athinput:47 |
| problem | n_waves | 2 | unmatched | inputs/tests/jeans_wave.athinput:77 |
| job | reference | 2 | unmatched | inputs/zoom/zoom_bondi.athinput:8 |
| problem | hist_nr | 2 | unmatched | inputs/zoom/zoom_bondi.athinput:92 |
| mhd | npieces | 1 | unmatched | inputs/dyn_grmhd/sod.athinput:64 |
| mhd | gamma1 | 1 | unmatched | inputs/dyn_grmhd/sod.athinput:65 |
| mhd | gamma2 | 1 | unmatched | inputs/dyn_grmhd/sod.athinput:66 |
| mhd | gamma3 | 1 | unmatched | inputs/dyn_grmhd/sod.athinput:67 |
| mhd | density1 | 1 | unmatched | inputs/dyn_grmhd/sod.athinput:68 |
| mhd | density2 | 1 | unmatched | inputs/dyn_grmhd/sod.athinput:69 |
| mhd | density3 | 1 | unmatched | inputs/dyn_grmhd/sod.athinput:70 |
| mhd | P0 | 1 | unmatched | inputs/dyn_grmhd/sod.athinput:71 |
| mhd | rho_min | 1 | other_block | inputs/dyn_grmhd/sod.athinput:72 |
| turb_driving | type | 1 | unmatched | inputs/hydro/turb.athinput:51 |
| hydro | viscosity | 1 | unmatched | inputs/hydro/viscosity.athinput:45 |
| output2 | ghozt_zones | 1 | unmatched | inputs/ion-neutral/oblique_cshock.athinput:81 |
| output3 | ghozt_zones | 1 | unmatched | inputs/ion-neutral/oblique_cshock.athinput:89 |
| ... | 7 more in inputs_vs_code.json | | | |

## this tree (problems/, cosmo/): `local/nrpic` at a1c223753952

- calls: 1259 (block_exists 49, exists 28, get 315, get_or_add 800, set 67)
- reads (get, get_or_add): 1115; distinct literal (block, name): 643; reads with a computed block or name: 264
- input files: 29 with 2549 parameter lines; literal 1816, computed block 351, computed name fitting its pattern 338, `<comment>` block 27, name read under another block 0, unmatched 17; literal or computed block: 2167 = 85.0 %; with the patterns: 2505 = 98.3 %; without the <comment> lines: 99.3 %

Unmatched lines are typing errors in input files, options that the code no longer reads, or names built from a plain variable (no literal to match, for example `<particles> field_time1`).

Input parameters not read with that block and name (count of input lines, first file):

| block | name | lines | status | first file |
|---|---|---|---|---|
| z4c_amr | radius_0_rad | 5 | unmatched | problems/jeans/jeans.athinput:53 |
| particles | field_time1 | 2 | unmatched | problems/cosmo/daverio_field.athinput:91 |
| particles | field_time2 | 2 | unmatched | problems/cosmo/daverio_field.athinput:92 |
| particles | field_time3 | 2 | unmatched | problems/cosmo/daverio_field.athinput:93 |
| particles | field_time4 | 2 | unmatched | problems/cosmo/daverio_field.athinput:94 |
| z4c | nco | 2 | unmatched | problems/jeans/jeans.athinput:127 |
| z4c_amr | radius_1_rad | 1 | unmatched | problems/jeans/jeans.athinput:55 |
| z4c_amr | radius_2_rad | 1 | unmatched | problems/jeans/jeans.athinput:57 |

## Athena++ (inputs/): `PrincetonUniversity/athena` at 1395e2f543f4

- calls: 999 (exists 13, get 394, get_or_add 576, set 16)
- reads (get, get_or_add): 970; distinct literal (block, name): 493; reads with a computed block or name: 46
- input files: 108 with 4886 parameter lines; literal 3822, computed block 713, computed name fitting its pattern 17, `<comment>` block 318, name read under another block 0, unmatched 16; literal or computed block: 4535 = 92.8 %; with the patterns: 4552 = 93.2 %; without the <comment> lines: 99.6 %

Unmatched lines are typing errors in input files, options that the code no longer reads, or names built from a plain variable (no literal to match, for example `<particles> field_time1`).

Input parameters not read with that block and name (count of input lines, first file):

| block | name | lines | status | first file |
|---|---|---|---|---|
| chemistry | xS | 5 | unmatched | inputs/chemistry/athinput.chem_gow17:71 |
| problem | p0overr0 | 2 | unmatched | inputs/hydro/athinput.disk_cyl:63 |
| problem | chi_min | 1 | unmatched | inputs/chemistry/athinput.chem_gow17_Pn:54 |
| problem | chi_max | 1 | unmatched | inputs/chemistry/athinput.chem_gow17_Pn:55 |
| problem | cr_min | 1 | unmatched | inputs/chemistry/athinput.chem_gow17_Pn:56 |
| problem | cr_max | 1 | unmatched | inputs/chemistry/athinput.chem_gow17_Pn:57 |
| problem | Tw | 1 | unmatched | inputs/chemistry/athinput.pdr_moving:55 |
| crdiffusion | zeta_factor | 1 | unmatched | inputs/cosmic_ray/athinput.cr_diffusion_mg:73 |
| problem | flux_radius_1 | 1 | unmatched | inputs/mhd_gr/athinput.fm_torus:146 |
| problem | flux_radius_2 | 1 | unmatched | inputs/mhd_gr/athinput.fm_torus:147 |
| job | configure | 1 | unmatched | inputs/mhd_gr/athinput.magnetized_inflow:3 |

## The `<particles>` options of the NRPIC module (this tree, athenak/src/particles)

| name | type | access | default | read at |
|---|---|---|---|---|
| ah_exc_factor | Real | get_or_add | -1.0 | particles/nrpic.cpp:118 |
| alpha_exc | Real | get_or_add | -1.0 | particles/nrpic.cpp:117 |
| assign_tag | String | get_or_add | "index_order" | particles/particles.cpp:129 |
| bh_mass | Real | get_or_add | 1.0 | particles/nrpic.cpp:94 |
| bh_spin | Real | get_or_add | 0.0 | particles/nrpic.cpp:95 |
| cons_dcycle | Integer | get_or_add | 0 | particles/nrpic.cpp:122 |
| cstat_dcycle | Integer | get_or_add | 0 | particles/nrpic.cpp:121 |
| curv_dt | Real | get_or_add | -1.0 | particles/nrpic.cpp:134 |
| curv_plane_y | Real | get_or_add | 1.0e-6 | particles/nrpic.cpp:136 |
| curv_slice | Boolean | get_or_add | false | particles/nrpic.cpp:135 |
| deposit | Boolean | get_or_add | (mesh_metric && pmy_pack->pz4c != nullptr) | particles/nrpic.cpp:220 |
| deposit_adaptive | Boolean | get_or_add | false | particles/nrpic.cpp:108 |
| deposit_comp_c | Real | get_or_add | 0.0 | particles/nrpic.cpp:100 |
| deposit_comp_c2 | Real | get_or_add | 0.0 | particles/nrpic.cpp:102 |
| deposit_comp_limit | Real | get_or_add | 0.0 | particles/nrpic.cpp:101 |
| deposit_max_coarsen | Integer | get_or_add | 31 | particles/nrpic.cpp:111 |
| deposit_max_level | Integer | get_or_add | 31 | particles/nrpic.cpp:103 |
| deposit_min_level | Integer | get_or_add | 0 | particles/nrpic.cpp:109 |
| deposit_ppc | Real | get_or_add | 2.0 | particles/nrpic.cpp:110 |
| deposit_shape | String | get_or_add | "cic" | particles/nrpic.cpp:158 |
| dt | Real | get_or_add | static_cast<Real>(std::numeric_limits<float>::max()) | particles/nrpic.cpp:182 |
| dt_expansion | Real | get_or_add | 0.0 | particles/nrpic.cpp:185 |
| field_constraints | Boolean | get_or_add | false | particles/nrpic.cpp:186 |
| filter_comp_c | Real | get_or_add | -1.0 | particles/nrpic.cpp:99 |
| filter_compensate | Boolean | get_or_add | false | particles/nrpic.cpp:98 |
| hist_dcycle | Integer | get_or_add | 1 | particles/nrpic.cpp:119 |
| interp | String | get_or_add | "hermite" | particles/nrpic.cpp:188 |
| key | Real | get |  | particles/nrpic.cpp:129 |
| lambda | Real | get_or_add | 0.0 | particles/nrpic.cpp:152 |
| lattice_dx | Real | get_or_add | 0.025 | particles/nrpic.cpp:96 |
| line_dcycle | Integer | get_or_add | 0 | particles/nrpic.cpp:123 |
| max_iterations | Integer | get_or_add | 50 | particles/nrpic.cpp:93 |
| metric | String | get_or_add | "mesh" | particles/nrpic.cpp:66 |
| nfilter | Integer | get_or_add | 1 | particles/nrpic.cpp:97 |
| nparticles | Integer | get_or_add | 0 | particles/nrpic.cpp:204 |
| nprobe | Integer | get_or_add | 0 | particles/nrpic.cpp:140 |
| particle_file | String | get_or_add | "" | particles/nrpic.cpp:202 |
| particle_type | String | get |  | particles/particles.cpp:45 |
| ppc | Real | get_or_add | 1.0 | particles/particles.cpp:34 |
| pre + "m" | Real | get_or_add | 0.0 | particles/nrpic.cpp:214 |
| pre + "u1" | Real | get |  | particles/nrpic.cpp:211 |
| pre + "u2" | Real | get |  | particles/nrpic.cpp:212 |
| pre + "u3" | Real | get |  | particles/nrpic.cpp:213 |
| pre + "x1" | Real | get |  | particles/nrpic.cpp:148 |
| pre + "x1" | Real | get |  | particles/nrpic.cpp:208 |
| pre + "x2" | Real | get |  | particles/nrpic.cpp:149 |
| pre + "x2" | Real | get |  | particles/nrpic.cpp:209 |
| pre + "x3" | Real | get |  | particles/nrpic.cpp:150 |
| pre + "x3" | Real | get |  | particles/nrpic.cpp:210 |
| probe_x1 | Real | get_or_add | 0.0 | particles/nrpic.cpp:137 |
| probe_x2 | Real | get_or_add | 0.0 | particles/nrpic.cpp:138 |
| probe_x3 | Real | get_or_add | 0.0 | particles/nrpic.cpp:139 |
| pusher | String | get |  | particles/particles.cpp:63 |
| snap_dt | Real | get_or_add | -1.0 | particles/nrpic.cpp:133 |
| source_density | Boolean | get_or_add | false | particles/nrpic.cpp:153 |
| source_extrap | Boolean | get_or_add | false | particles/nrpic.cpp:154 |
| tolerance | Real | get_or_add | 1.0e-7 | particles/nrpic.cpp:92 |
| traj_dcycle | Integer | get_or_add | 0 | particles/nrpic.cpp:120 |
| traj_ntrack | Integer | get_or_add | 0 | particles/nrpic.cpp:132 |
| triad | String | get_or_add | "symmetric" | particles/nrpic.cpp:82 |
