# Ledger of the G1 sections of the note (slow-roll reproduction)

Written by `note/scripts/ledger.py`. Every number of the G1 sections with its value, its source and its evidence label. Run labels: R9-R18 below, R1 of the G0 ledger (`E-stoch-inf-20261115-122806-ef0d039`); V = the verifier's report; C = core's statement in its interface text (released with core-v0.5, not yet checked by the track).

| Quantity | Value | Source | Label |
|---|---|---|---|
| A1: box means of $\phi$, $\Pi$, $K$ against the Friedmann reference, largest over the rungs | $2.0\times10^{-12}$, $8.6\times10^{-12}$, $3.6\times10^{-12}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A1: e-folds from $\langle\chi\rangle$ after 8.1 e-folds, $32^3$, $64^3$, $128^3$ | $5.5\times10^{-6}$, $3.3\times10^{-7}$, $2.0\times10^{-8}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A2: largest $D_n$ for $k\leq k_\mathrm{max}/2$, ladder $32^3$, $64^3$, $128^3$, $256^3$ | $8.8\times10^{-5}$, $2.7\times10^{-6}$, $2.5\times10^{-6}$, $1.7\times10^{-6}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A2: the same in the paper's set-up, $64^3$, $128^3$, $256^3$ | $9.7\times10^{-5}$, $9.9\times10^{-5}$, $1.21\times10^{-4}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A2: modes of the $256^3$ run, all and with $k\leq k_\mathrm{max}/2$ | $548958$, $68532$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A2: largest $D_n$ over all modes, ladder $32^3$, $64^3$, $128^3$ | $4.08\times10^{-3}$, $9.65\times10^{-5}$, $7.09\times10^{-6}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A2: $256^3$ against a reference with the stencil's wave number | $6.16\times10^{-3}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| Spectrum: shell ratio against the reference with the same $\alpha_k$, largest over the rungs | $1.9\times10^{-4}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| Spectrum: linear power over the slow-roll formula, $k\leq7\,k_{\sigma*}$ | $1.0104$--$1.0109$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A3: modes with $N_f-N_k\geq6$ per rung | $1051$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A3: largest $|Q_n(N_f)/Q_n(N_k+4)-1|$ over the rungs | $4.6\times10^{-6}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A3: largest drift of $\ln|\mathcal{R}_n|^2$ per e-fold, range over the rungs | $1.379\times10^{-4}$--$1.405\times10^{-4}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A3: drift of the code minus that of the full equation, largest | $1.75\times10^{-6}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A3: drift of the FLRW lattice for the same shells; over the largest drift of the code | $0.0513$--$0.0527$; $365$ | E-stoch-inf-20261115-122806-ef0d039, E-20261115-194633-9e04ed8 | [VERIFIED] |
| A4: largest odd over even part of $\mathcal{H}$ at dumps where both runs of the pair share the time, paper set-up, $32^3$, $64^3$, $128^3$, $256^3$ | $745$, $655$, $869$, $25$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A4: e-folds of these maxima; last time-matched dump of the $256^3$ pair | $2.47$, $2.97$, $3.91$, $3.91$; $3.91$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A4: first dump with odd above even part (e-folds); $\ln(N/8)$, same lattices | $1.51$, $1.99$, $2.96$, $3.44$; $1.39$, $2.08$, $2.77$, $3.47$ | E-20261119-142713-32c883a | [VERIFIED] |
| A4: largest record $\langle|\mathcal{H}|/[\mathcal{H}]\rangle$; $\langle|\mathcal{M}|/[\mathcal{M}]\rangle$, paper set-up | $5.1\times10^{-11}$; $3.8\times10^{-4}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A4: halving factors at $32^3$, odd part; even part | $1.9999$--$2.0000$; $3.991$--$4.000$ | E-20261119-142713-32c883a | [VERIFIED] |
| A4: largest odd over even part, convergence set-up, $64^3$, $128^3$, $256^3$ | $15.4$, $0.27$, $0.53$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| Negative control: record $\mathcal{H}$ over the proper run, range of the maxima; $\langle|\mathcal{M}|/[\mathcal{M}]\rangle$ | $4.0\times10^{4}$--$1.5\times10^{5}$; $0.20$--$0.22$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A5: order of the odd part before the floor, $32^3\to64^3\to128^3$, $\mathcal{H}$; $\mathcal{M}$ | $4.20$--$5.82$; $5.55$--$5.91$ | E-20261119-142713-32c883a | [VERIFIED (floor fixed after the data)] |
| Floor: growth with the cells per side, exponent for $\mathcal{H}$; $\mathcal{M}$ | $2.48$; $2.63$ | E-20261119-142713-32c883a | [VERIFIED (attribution: JUDGEMENT)] |
| Floor: odd part of $\mathcal{H}$ at $256^3$, first and last dump of the comparison | $6.0\times10^{-13}$, $6.9\times10^{-15}$ | E-20261119-142713-32c883a | [VERIFIED] |
| Even part: $64^3$ against $128^3$, largest relative difference | $0.022$ | E-20261119-142713-32c883a | [VERIFIED] |
| Record $\langle|\mathcal{H}|/[\mathcal{H}]\rangle$ at $N_f$, $32^3$, $64^3$, $128^3$ | $3.12\times10^{-12}$, $1.83\times10^{-13}$, $1.12\times10^{-14}$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| A6: orders of the differences between Courant factors | $3.93$--$4.08$ | E-20261119-145230-ff0dff2 | [VERIFIED] |
| A6: largest difference of $\mathcal{R}^\mathrm{NR}_n$ between $\theta=0.25$ and $0.125$ | $2.9\times10^{-4}$ | E-20261119-145230-ff0dff2 | [VERIFIED] |
| A6: largest $D_n$ of the top shells at $\theta=0.25$, $0.125$, $0.0625$ | $3.97\times10^{-3}$, $3.75\times10^{-3}$, $3.74\times10^{-3}$ | E-20261119-145230-ff0dff2 | [VERIFIED] |
| A6: odd part of $\mathcal{H}$ in the late entry, largest change per halving of $\theta$ | $0.041$ | E-20261119-145230-ff0dff2 | [VERIFIED] |
| A6: order of the uniform residual of $\mathcal{H}$ | $4.10$ | E-20261119-145230-ff0dff2 | [VERIFIED] |
| A7: noise for one, eight, sixty-four MeshBlocks; restart on processors, card; card against processors | $0$; $0$, $0$; $2.2\times10^{-15}$ | E-20261115-180533-24a7781, E-20261119-141654-c2a10d1, E-20261115-184748-9b010fa | [VERIFIED] |
| A7: variables bit-identical between one and eight MeshBlocks and through a restart, the executable of the slow-roll runs at $32^3$ | $22$ of $22$ | `stage/G1/VERIFIER.md` lines 303, 332, 374 and `stage/G1/STATUS.md` line 30; runs E-20261121-030207-fb6f090, -031951-82984f8, -030522-c6907b6, -031049-27cdc06, -031251-c48670d | [VERIFIED (by the verifier)] |
| A7: released processor build against the executable of the slow-roll runs, $32^3$ pair: 64-bit words compared; differing | $18.9\times10^{6}$; $0$ | `stage/REVIEW-wave3.md` line 111; run E-20261121-064707-77ec326 | [VERIFIED (by the lead)] |
| Analysis: synthetic tests passed | $15$ of $15$ | E-20261115-171445-36152c4 | [VERIFIED] |
| Analysis: $\mathcal{R}^\mathrm{NR}$ at amplitude $10^{-5}$, error and its slope; without the metric term | $2.35\times10^{-4}$, $0.999$; $0.657$ | E-20261115-171445-36152c4 | [VERIFIED] |
| Analysis: reader against core's, largest difference; $D_n$ at the start | $0$; $7.5\times10^{-10}$ | E-20261115-172935-ddfade0 | [VERIFIED] |
| Analysis: largest $D_n$ ($32^3$, $k\leq k_\mathrm{max}/2$) with the factor $1/4$, $1/2$, $-1/4$, none | $8.8\times10^{-5}$, $5.2\times10^{-3}$, $0.010$, $5.1\times10^{-3}$ | E-20261115-174214-74becdd | [VERIFIED] |
| Cost of one $256^3$ realisation, 8.1 e-folds: card-hours; seconds; steps | $0.503$; $1811$; $1386$ | E-20261115-172618-f948386, E-20261115-194633-9e04ed8 | [VERIFIED] |
| Cost: seconds per step at $256^3$ on one card | $1.13$--$1.30$ | E-20261115-194633-9e04ed8 | [VERIFIED] |
| Verifier: control over proper first-order part, ratio of the maxima over the entry; pointwise at the end of the entry, lowest | $1709$--$1874$; $89$ | `stage/G1/VERIFIER.md` lines 303, 332, 374 and `stage/G1/STATUS.md` line 30; runs E-20261121-030207-fb6f090, -031951-82984f8, -030522-c6907b6, -031049-27cdc06, -031251-c48670d | [VERIFIED (by the verifier)] |
| Verifier: even part, $128^3$ against $256^3$ in the convergence set-up after each run's floor is removed (percent) | $0.8$ | `stage/G1/VERIFIER.md` lines 303, 332, 374 and `stage/G1/STATUS.md` line 30; runs E-20261121-030207-fb6f090, -031951-82984f8, -030522-c6907b6, -031049-27cdc06, -031251-c48670d | [VERIFIED (by the verifier)] |
| Core: stencil mismatch $\mu/k^2$ at four, eight, sixteen cells per wavelength | $0.110$, $2.6\times10^{-3}$, $4.4\times10^{-5}$ | release core-v0.5, `coord/INTERFACES/scalar_field_3.md` lines 143-164; runs core-20261119-151758-51d9a71, -152243-1754ebc, -161111-9d05d14 | [TO VERIFY] |
| Core: largest odd over even part at four cells per wavelength; cells where it falls below one | $692$; $12.7$ | release core-v0.5, `coord/INTERFACES/scalar_field_3.md` lines 143-164; runs core-20261119-151758-51d9a71, -152243-1754ebc, -161111-9d05d14 | [TO VERIFY] |
| Core: largest noise cutoff at $256^3$ for second-order constraints | $20\,\Delta k$ | release core-v0.5, `coord/INTERFACES/scalar_field_3.md` lines 143-164; runs core-20261119-151758-51d9a71, -152243-1754ebc, -161111-9d05d14 | [TO VERIFY] |

Runs:

- R9 `E-20261115-194633-9e04ed8`: final analysis of the slow-roll ladder (A1-A5, spectrum, negative control)
- R10 `E-20261119-142713-32c883a`: floor analysis of the odd constraint parts (A5, halving, crossing)
- R11 `E-20261119-145230-ff0dff2`: temporal order A6 (three Courant factors at $32^3$)
- R12 `E-20261115-172618-f948386`: $256^3$ slow-roll run in the paper's set-up on one card (cost)
- R13 `E-20261115-171445-36152c4`: synthetic tests of the analysis module
- R14 `E-20261115-172935-ddfade0`: reader of the dumps against core's reader
- R15 `E-20261115-174214-74becdd`: extraction factor of the anisotropic term of the curvature perturbation
- R16 `E-20261115-180533-24a7781`: noise for three MeshBlock layouts on a card
- R17 `E-20261115-184748-9b010fa`: card against processors
- R18 `E-20261119-141654-c2a10d1`: restart on processors and on a card

Core's numbers found on their lines: core.mu4 yes, core.mu8 yes, core.mu16 yes, core.slope yes, core.peak4 yes, core.cells1 yes, core.kmax256 yes

Reproducibility numbers found on their lines: rep.ver.vars yes, rep.lr1.words yes, rep.lr1.diff yes

The verifier's numbers found on their lines: ver.nc.point yes, ver.nc.max.lo yes, ver.nc.max.hi yes, ver.even.128.256 yes
