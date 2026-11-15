# Journal of work package D-pre-2 (spike in the probe limit)

Helper of D-bh-dress. Predictions are written before each registered run; outcomes after,
also when a prediction failed. Units G = c = m_BH = 1 unless stated; R_S = 2 G m.

## 2026-11-15 Setup and development probes (not registered)

- Source fetched: arXiv:1305.2619 v1 (SFW), `kb-data/raw/arxiv/1305.2619/v1/src/SFWpaper.tex`;
  Kerr sequel arXiv:1707.06302 v2 (FdRW) already in `kb-data/raw/arxiv/1707.06302/v2/src/`.
- [VERIFIED] SFW eq. (3.19) (SFWpaper.tex lines 412-418) and its dimensionless form (4.13)
  (lines 660-663) use oint sqrt(V) dr, i.e. u^r, not the canonical u_r = sqrt(V)/(1-2Gm/r);
  their Kerr form (line 349) has the factor r^2/Delta. FdRW say so in a footnote
  (kerrdm.tex line 919: "the Schwarzschild limit of the radial invariant in Eq. (3.19) in
  SFW is missing a factor of r^2/Delta = 1/(1-2Gm/r)"). `spike_lib.py` computes both.
- [VERIFIED] SFW Fig. 3 does not state the black-hole mass; the only value in the paper is
  m = 4e6 M_sun in Sec. V (line 808). The halo is M = 1e12 M_sun, a = 20 kpc (line 124).
- Development probes of `spike_lib.py` (unit checks, not results): E_min of SFW eq. (3.17)
  equals a brute-force scan of the non-captured region to the grid spacing (1e-5) at
  r = 4.05 ... 20; the Hernquist action table inverts to 1e-5 in delta = 1 - eps against
  direct bisection; Kepler limit of the relativistic radial action at E = 1 - 1e-4,
  L = 50: 130.34 vs 130.13 (relativistic correction), period 2.2223e6 vs 2.2214e6.
- Seen during development, before the predictions below (so not a test): with
  m = 4e6 M_sun our relativistic Hernquist spike peaks at 2.44e18 GeV/cm^3 near r = 7.6 Gm,
  while the digitized SFW Fig. 3 peaks at 10^19.40 = 2.5e19 GeV/cm^3; the digitized FdRW
  Schwarzschild curve (fig_rho_hern.pgf) peaks at 2.44e18 at r = 7.68 Gm. The red
  "initial Hernquist profile" line of SFW Fig. 3 (10^10.892 GeV/cm^3 at r = 2 R_S, slope -1)
  implies R_S = 9.7e-8 pc, i.e. m = 1.0e6 M_sun if a = 20 kpc and M = 1e12 M_sun.

## P1 Reference calculation against the printed numbers and curves (prediction)

Run: `spike_reference.py` (registered as D-bh-dress-<time>-<commit>, kind scouting).

Predictions, each with what refutes it:
1. Constant f (SFW Fig. 1): relativistic rho vanishes at r = 4 Gm, GS at 8 Gm; our
   relativistic peak 0.87e8 GeV/cm^3 at r = 7.6 +- 0.3 Gm and GS peak 0.336e8 at 15.9 Gm
   (digitized SFW Fig. 1). Refuted if our peak values differ from the digitized ones by
   more than 2 %. SFW text (line 443): GS peak "a factor of three smaller"; GS with
   8 -> 4 Gm peaks "about 15 % higher" than the relativistic result. Refuted if our
   ratios are outside 2.5-3.5 and 10-20 %.
2. Hernquist, m = 4e6 M_sun, canonical action: our curve equals the FdRW Schwarzschild
   curve (blue dash-dot of fig_rho_hern.pgf) within 3 % at 5 < r/Gm < 40. Refuted if not.
   FdRW say the spike meets the Hernquist profile at 12.4 pc (kerrdm.tex line 1053):
   refuted if our crossing is outside 11-14 pc.
3. Hernquist, m = 1.0e6 M_sun, SFW action (as printed): our relativistic and
   non-relativistic (GS) curves reproduce SFW Fig. 3 within 0.1 dex for
   0.45 < log10(r/R_S) < 4; refuted if the offset exceeds 0.2 dex anywhere there.
   Expected peaks: relativistic 10^19.40 at log10(r/R_S) = 0.58, GS 10^18.86 at 0.94.
4. The canonical action lowers the inner spike relative to the SFW action by a few per
   cent at the peak (5 % at r = 7.6 Gm in the development probe), less than 1 % beyond
   100 Gm. Refuted if the difference exceeds 10 % at the peak or changes sign.
5. Relativistic/GS ratio at the peak (Hernquist): SFW text (line 124) "2-3 times higher";
   at r > 50 R_S the two agree "with standard results". Refuted if our peak ratio is
   outside 2-4 or the curves differ by more than 5 % beyond 100 R_S.
