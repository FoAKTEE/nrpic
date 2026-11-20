# JOURNAL of C-sidm/drift (wave 3, round 1, helper of C-sidm)

Package: the origin of the slow outward excursion of the central lapse in the two
collisionless King controls of wave 2 (`../threshold_scan/JOURNAL.md` entry 6, P3.8;
`../RISKS.md` item 3): numerical (mesh), particle noise, or a physical mode excited by the
initial data. The answer decides the mesh of block A of `../threshold_scan/SCAN.md`.
Predictions are written here before each test; outcomes after it, also when they fail.
Run ids: `../runs/<run_id>/manifest.json`. Labels: [VERIFIED] computed in a registered run
named next to it; [BACKGROUND]; [JUDGEMENT]; [TO VERIFY].

## 2026-11-20 22:20 UTC Entry 1: state, and predictions for the processor analysis (test D1)

State found: no `drift/` directory, no run of this package registered (fresh start). Pause
flag absent. Slurm: no job of C-* queued or running (22:15 UTC).

Inputs [VERIFIED from files]:
- wave-2 controls: cc1_kninf in card run C-20261115-171058-c26cfad, cc2_kninf in
  C-20261115-171059-4b70228 (decks `../threshold_scan/inputs/cc{1,2}_kninf.athinput`:
  static mesh, level-6 region |x|_inf < 7.9 M, dx = M/4 there, N = 1e5, dt = M/16, 300 M,
  four compensated binomial passes, 1+log lapse and Gamma-driver shift); restart files
  `rst/cc.00001.rst(.prt)` of both were written at the end of the run (10:21:29 and
  10:40:11 PST on 2026-11-15, `<output2> dt = 300`), i.e. at t = 300 M.
- the batch executables of both runs (`batch.list.exe`) and the release card executable
  `.work/build_gpu_v03/src/athena` have the same sha256 f9f2dc12...be3a1: a restart with the
  release executable is exact.
- What the wave-2 analysis (run C-20261115-191420-8538aa4, `fig_cc_controls.png`, looked at
  again today) shows: alpha_c - alpha_c(0) rises to +0.0334 (CC1) and +0.0185 (CC2) near
  200 M and falls back to about +0.017 and +0.004 at 300 M; a ripple of about 1e-3 on top.

Questions of test D1 (processor analysis of the two controls, run to be registered):
alpha_c(t); radii enclosing 10 and 50 percent of the rest mass (coordinate, and the areal
radius of the same shells from the metric at the particles, so that a pure change of the
spatial coordinates can be told from a physical expansion); the Hamiltonian-constraint
norm; rest mass, mean Lorentz factor sum mW/sum m and Killing-energy sum; particle count;
period and amplitude of the excursion (fit of A (1 - cos 2 pi t/P) + c, and a free-phase
sinusoid with a trend as a second estimator); whether it returns by 300 M; and the period
of the fundamental radial mode from the track's own pulsation tool (`tmb.fem_lowest` via
`models/fluid_onset.omega2`, King family b = 1 as in the lead's check L15, run
C-20261119-151502-cb831a8), converted to the time at infinity in units of M.

Predictions (written before the analysis runs; I have seen only `fig_cc_controls.png`):

- D1.1 Fit period. P(CC1) in [330, 550] M, P(CC2) in [280, 480] M, and P(CC2) < P(CC1)
  (the threshold model is the softer one). Refuted if P(CC2) >= P(CC1) or either lies
  outside its band.
- D1.2 Not a coordinate effect. The coordinate radius r50 grows when alpha_c grows
  (Pearson correlation of the two series, interpolated to the snapshot times, > +0.7), and
  the areal radius of the same shell moves by at least half the relative amount of the
  coordinate r50. Refuted if r50 is flat or anti-correlated, or the areal radius stays
  within a quarter of the coordinate change (then the lapse excursion is mostly slicing and
  shift, a gauge drift).
- D1.3 An expansion slows the particles: the mean Lorentz factor sum mW/sum m is
  anti-correlated with alpha_c (correlation < -0.7). Refuted otherwise.
- D1.4 Bookkeeping: rest mass bit-identical and np = 1e5 at every record (as in P3.1);
  the squared H-norm does not follow the excursion (|correlation with alpha_c| < 0.5).
- D1.5 The fundamental radial mode of a fluid with the model's own adiabatic index
  (F21 gamma = 1 + p/u) has a period of order the dynamical estimate
  pi (3/(4 pi rho_c))^(1/2) = 22.0 M (CC1) and 23.6 M (CC2) (threshold_scan entry 3):
  within a factor four of it, i.e. far below the excursion's P. With the Juttner index
  (onset y0 = 0.32143, L15) CC1 has omega^2 < 0 and no period. So the excursion is not the
  fundamental mode of a fluid; for the collisionless cluster the lowest radial frequency
  vanishes at the binding-energy maximum (2009.08163 places the onset there [BACKGROUND,
  as quoted in `../threshold_scan/SCAN.md` 'What each block decides']), so a period of
  10-20 dynamical times is possible only for a near-marginal collisionless mode
  [JUDGEMENT]. Refuted if a fluid period lies within 30 percent of the fitted P.
