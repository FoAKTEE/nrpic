"""Analysis of the scalar-field output of AthenaK for Track E (stochastic inflation).

Reader and estimators named by the lead (tracks/E-stoch-inf/stage/G1/STATUS.md): the
curvature perturbation R^NR (P-c of spec/SPEC.md section 7.1), per-mode amplitudes and
their ratio to linear theory (A2, freezing of SPEC 7.3), shell spectra, and constraint
ratios |H|/[H], |M|/[M] (P-d, P-e; PRD_v2.tex:740-743). No simulation code: everything here reads
what the release executable writes (coord/INTERFACES/scalar_field.md section 6).

Inputs, all from one run directory:
- <basename>.sf.NNNNN.dump (double precision; phi, Pi, chi, K = Khat + 2 Theta, alpha, H,
  M_i, E and the stochastic fields; reader nrpic.scalar_field.read_dump),
- <basename>.sf.NNNNN.modes (lockstep background and mode functions R_q, dR_q/dt and the
  shell factor at the dump time, MS model only),
- <basename>.sf.hst (box means, constraint norms; [H] of the code in column H_norm),
- optionally a standard `bin` output with the z4c variables (single precision) for the
  conformal metric gt_ij and At_ij, which the dump does not hold.

Conventions (interface section 2, 7): G = c = 1, K = -3H on the background, chi =
(det gamma)^(-1/3) (chi_psi_power = -4), cell centres x - x0 = (j + 1/2) h, a mesh field
xi(x) = sum_{n in H} 2 Re[c_n exp(i k_n.(x - x0))] over the hemisphere H of
nrpic.scalar_field.mode_set; the coarse-grained noise field of the MS model is
L^(-3/2) sum 2 Re[W_q R_q alpha_n exp(i k_n.(x - x0))].
"""
import glob
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import scalar_field as nsf  # noqa: E402

EIGHT_PI = 8.0 * np.pi


# ============================================================================ reading
def read_dump(fname):
    """One dump on a uniform mesh of cubic cells: dict with time, cycle, shape, Lvec, x0,
    h, N and L (None unless the mesh is cubic) and the fields (phi, Pi, chi, K, alpha, H,
    Mx, My, Mz, E, noise0, ...) as [i, j, k] arrays."""
    d = nsf.read_dump(fname)
    if "fields" not in d:
        raise ValueError(f"{fname}: refined mesh; only uniform meshes are analysed")
    ext = np.array([b["extent"] for b in d["blocks"]])
    lo = ext[:, 0::2].min(axis=0)
    hi = ext[:, 1::2].max(axis=0)
    shape = d["fields"]["phi"].shape
    hv = (hi - lo) / np.array(shape)
    if not np.allclose(hv, hv[0], rtol=1e-12, atol=0):
        raise ValueError(f"{fname}: cells are not cubic ({hv})")
    cubic = len(set(shape)) == 1
    out = dict(time=d["time"], cycle=d["cycle"], shape=shape, Lvec=hi - lo,
               x0=lo.astype(float), h=float(hv[0]), names=d["names"], file=fname,
               N=shape[0] if cubic else None, L=float(hi[0] - lo[0]) if cubic else None)
    out.update(d["fields"])
    return out


def dump_files(rundir):
    """Dumps of a run directory, sorted by number."""
    return sorted(glob.glob(os.path.join(rundir, "*.sf.[0-9][0-9][0-9][0-9][0-9].dump")))


def read_modes(fname):
    """The .modes record next to a dump: header numbers (time, phi_b, Pi_b, ln_a, H, a,
    eps1, eps2, kick factors) and per shell n2, R, dR (complex), shell factor (complex)."""
    head, num = {}, re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s+([-+0-9.eEinfa]+)")
    with open(fname) as fp:
        lines = fp.readlines()
    for line in lines:
        if not line.startswith("#"):
            break
        text = line[1:]
        if text.strip().startswith("kick factors:"):
            text = " ".join(f"kick_{w}" if i % 2 == 0 else w for i, w in
                            enumerate(text.split(":", 1)[1].split()))
        if "lockstep time" in text:
            text = text.replace("lockstep time", "lockstep_time").replace("alpha epoch",
                                                                         "alpha_epoch")
        for key, val in num.findall(text):
            try:
                head[key] = float(val)
            except ValueError:
                pass
    rows = np.atleast_2d(np.loadtxt(fname))
    return dict(head=head, n2=rows[:, 0].astype(np.int64), R=rows[:, 1] + 1j * rows[:, 2],
                dR=rows[:, 3] + 1j * rows[:, 4], shell=rows[:, 5] + 1j * rows[:, 6])


def read_history(rundir_or_file):
    """Columns of <basename>.sf.hst (nrpic.scalar_field.read_history)."""
    f = rundir_or_file
    if os.path.isdir(f):
        f = glob.glob(os.path.join(f, "*.sf.hst"))[0]
    return nsf.read_history(f)


def history_row(hist, cycle):
    """The history record of one cycle (dict of floats); KeyError if not written."""
    idx = np.nonzero(hist["cycle"] == cycle)[0]
    if idx.size == 0:
        raise KeyError(f"cycle {cycle} not in the history")
    return {k: float(v[idx[-1]]) for k, v in hist.items()}


def read_bin_metric(fname):
    """Conformal metric gt_ij and At_ij (single precision) from a `bin` output with the
    z4c variables, assembled on the root mesh as float64 arrays [i, j, k]. Returns dict
    gt[(a, b)], At[(a, b)] for a <= b, chi, time, cycle."""
    sys.path.insert(0, os.path.join(REPO, "athenak", "vis", "python"))
    import bin_convert  # noqa: E402
    fd = bin_convert.read_binary(fname)
    nx = (fd["Nx1"], fd["Nx2"], fd["Nx3"])
    nb = (fd["nx1_out_mb"], fd["nx2_out_mb"], fd["nx3_out_mb"])

    def assemble(var):
        out = np.empty(nx[::-1])
        for m, (lx1, lx2, lx3) in enumerate(fd["mb_logical"][:, :3]):
            out[lx3 * nb[2]:(lx3 + 1) * nb[2], lx2 * nb[1]:(lx2 + 1) * nb[1],
                lx1 * nb[0]:(lx1 + 1) * nb[0]] = fd["mb_data"][var][m]
        return out.transpose(2, 1, 0).astype(np.float64)

    comp = {"x": 0, "y": 1, "z": 2}
    gt, at = {}, {}
    for var in fd["var_names"]:
        m = re.fullmatch(r"z4c_([gA])([xyz])([xyz])", var)
        if m:
            key = tuple(sorted((comp[m.group(2)], comp[m.group(3)])))
            (gt if m.group(1) == "g" else at)[key] = assemble(var)
    out = dict(time=fd["time"], cycle=fd["cycle"], gt=gt, At=at)
    if "z4c_chi" in fd["var_names"]:
        out["chi"] = assemble("z4c_chi")
    return out


# ============================================================================ lattice
class Lattice:
    """Wave vectors of the hemisphere with 0 < |n|^2 <= nmax2 on an N^3 mesh of side L."""

    def __init__(self, N, L, nmax2):
        if 2 * int(np.floor(np.sqrt(nmax2))) >= N:
            raise ValueError("2 n_max must be below N")
        self.N, self.L, self.nmax2 = int(N), float(L), int(nmax2)
        self.n, self.n2 = nsf.mode_set(nmax2)
        self.q = np.sqrt(self.n2.astype(float))
        self.k = 2.0 * np.pi * self.q / self.L
        self.h = self.L / self.N

    @classmethod
    def of_dump(cls, d, nmax2):
        return cls(d["N"], d["L"], nmax2)

    def coefficients(self, field):
        """c_n of a real mesh field for every wave vector of the lattice."""
        return nsf.analyse(field, self.n)[0]

    def synthesise(self, c):
        return nsf.synthesise(c, self.n, self.N)

    def alpha(self, seed, dof=0, epoch=0):
        """The code's unit complex Gaussians alpha_n (keys of interface section 7.1)."""
        return nsf.mode_alpha(seed, dof, epoch, self.n)

    def shells(self):
        """Distinct |n|^2 and the index of each mode's shell."""
        s, inv = np.unique(self.n2, return_inverse=True)
        return s, inv


def box_mean(f):
    """Mean over the cells (equal coordinate volumes on a uniform mesh)."""
    return float(np.mean(f))


def _kvec(N, L):
    k1 = 2.0 * np.pi * np.fft.fftfreq(N, d=L / N)
    return np.meshgrid(k1, k1, k1, indexing="ij")


# ============================================================ curvature perturbation
def metric_potential(chi, gt=None, a2=None):
    """Phi of the extraction of 2610.32592 appendix (chap. "Cosmological extractions",
    appendix.tex:513-522): Phi_k = (a^2 X_k - 1)/2 + (1/4) sum_ij k_i k_j/k^2 (gt_ij -
    delta_ij)_k, X = chi, a^2 = 1/<chi> unless given. gt: dict {(a, b): array} for a <= b
    or None (then the second term is left out and Phi is (a^2 chi - 1)/2). Returns the real
    field Phi (zero mode removed) and the size of the gt term (rms), 0 if not used."""
    if a2 is None:
        a2 = 1.0 / box_mean(chi)
    phi_ = 0.5 * (a2 * chi - 1.0)
    phi_ = phi_ - box_mean(phi_)
    rms_gt = 0.0
    if gt is not None:
        N = chi.shape[0]
        kx, ky, kz = _kvec(N, 1.0)
        kv = (kx, ky, kz)
        k2 = kx * kx + ky * ky + kz * kz
        k2[0, 0, 0] = 1.0
        acc = np.zeros(chi.shape, dtype=complex)
        for a in range(3):
            for b in range(3):
                g = gt[tuple(sorted((a, b)))] - (1.0 if a == b else 0.0)
                acc += kv[a] * kv[b] * np.fft.fftn(g)
        acc /= k2
        acc[0, 0, 0] = 0.0
        term = 0.25 * np.fft.ifftn(acc).real
        rms_gt = float(np.sqrt(np.mean(term ** 2)))
        phi_ = phi_ + term
    return phi_, rms_gt


def curvature_perturbation(d, gt=None):
    """R^NR = Phi - <K>/(3 <alpha> <Pi>) (phi - <phi>) (2610.32592 appendix.tex:521;
    2512.14649 PRD_v2.tex:525 with alpha = 1). d: a dump (read_dump). Returns dict with
    the field R, Phi, the coefficient of the field term and the rms of the gt term."""
    phi_, rms_gt = metric_potential(d["chi"], gt)
    coef = -box_mean(d["K"]) / (3.0 * box_mean(d["alpha"]) * box_mean(d["Pi"]))
    r = phi_ + coef * (d["phi"] - box_mean(d["phi"]))
    return dict(R=r, Phi=phi_, field_coef=coef, rms_gt_term=rms_gt,
                efolds=-0.5 * np.log(box_mean(d["chi"])))


# ======================================================================= per mode
def window(k, a, hub, sigma=1.0, sharpness=5.0):
    """W = (1 + tanh[s ln(sigma a H / k)])/2 (SPEC section 3; interface 7.3)."""
    return 0.5 * (1.0 + np.tanh(sharpness * np.log(sigma * a * hub / k)))


def expected_coefficients(lat, modes, alpha, sigma=1.0, sharpness=5.0, windowed=True):
    """Linear-theory coefficients L^(-3/2) W_q R_q alpha_n of the coarse-grained R at the
    time of a .modes record (its lockstep a, H and R_q). windowed=False drops W."""
    shell_of = {int(s): i for i, s in enumerate(modes["n2"])}
    try:
        idx = np.array([shell_of[int(s)] for s in lat.n2])
    except KeyError as e:
        raise ValueError(f"shell |n|^2 = {e} missing in the .modes record") from None
    r = modes["R"][idx]
    w = window(lat.k, modes["head"]["a"], modes["head"]["H"], sigma, sharpness) \
        if windowed else 1.0
    return lat.L ** -1.5 * w * r * alpha


def per_mode_ratio(c_nr, c_exp, floor=0.0):
    """c_nr/c_exp - 1 (complex) where |c_exp| > floor, NaN elsewhere."""
    out = np.full(c_nr.shape, np.nan + 1j * np.nan)
    m = np.abs(c_exp) > floor
    out[m] = c_nr[m] / c_exp[m] - 1.0
    return out


def shell_spectrum(lat, c):
    """Dimensionless spectrum per lattice shell, Delta(k) = k^3 L^3 <|c_n|^2>/(2 pi^2)
    (QFT normalisation <f^2> = int d^3k/(2pi)^3 |f_k|^2, SPEC section 1, with |f_k|^2 =
    L^3 |c_n|^2 for unit-variance amplitudes). Returns k, Delta, mode count per shell."""
    s, inv = lat.shells()
    p = np.bincount(inv, weights=np.abs(c) ** 2) / np.bincount(inv)
    k = 2.0 * np.pi * np.sqrt(s) / lat.L
    return k, k ** 3 * lat.L ** 3 * p / (2.0 * np.pi ** 2), np.bincount(inv)


def drift(c_a, c_b, n_a, n_b):
    """Per-mode drift of ln |c|^2 per e-fold between two outputs (SPEC 7.3)."""
    return (np.log(np.abs(c_b) ** 2) - np.log(np.abs(c_a) ** 2)) / (n_b - n_a)


# ===================================================================== constraints
_D1 = {2: [1 / 2], 3: [2 / 3, -1 / 12], 4: [3 / 4, -3 / 20, 1 / 60]}


def d1(f, h, axis, nghost=4):
    """Centred first difference of the code (utils/finite_diff.hpp; order 2 (nghost - 1))
    on a periodic mesh."""
    out = np.zeros_like(f)
    for m, c in enumerate(_D1[nghost], start=1):
        out += c * (np.roll(f, -m, axis=axis) - np.roll(f, m, axis=axis))
    return out / h


def ham_norm_cells(d, aa=None):
    """[H] per cell, |R| + (2/3) K^2 + |At_ij At^ij| + 16 pi |E| (2512.14649 PRD_v2.tex:740 with
    Mpl^-2 rho = 8 pi E), with the three-Ricci scalar recovered from the dumped H =
    R + (2/3) K^2 - At At - 16 pi E. aa: At_ij At^ij per cell, or None: then it is left out
    (a term of second order in the perturbations; the code's [H] keeps it)."""
    k23 = (2.0 / 3.0) * d["K"] ** 2
    aa_ = 0.0 if aa is None else aa
    ricci = d["H"] - k23 + aa_ + 16.0 * np.pi * d["E"]
    return np.abs(ricci) + k23 + np.abs(aa_) + 16.0 * np.pi * np.abs(d["E"])


def mom_norm_cells(d, nghost=4, at_terms=None):
    """[M] = sqrt(sum_i [M_i]^2) per cell with [M_i] = |(2/3) d_i K| + |8 pi S_i|, S_i =
    -Pi d_i phi (PRD_v2.tex:741-743 with Mpl^-2 J_i = 8 pi S_i). The At terms of P1 are added
    when at_terms (array [3, ...] of |gt^kl d_k At_il| + |3 gt^kl At_ik d_l chi/(2 chi)|)
    is given; without them [M] is a lower bound of P1's (same order: all terms are first
    order in the perturbations on the background)."""
    h = d["h"]
    comps = []
    for i in range(3):
        mi = np.abs((2.0 / 3.0) * d1(d["K"], h, i, nghost)) + \
            np.abs(EIGHT_PI * d["Pi"] * d1(d["phi"], h, i, nghost))
        if at_terms is not None:
            mi = mi + at_terms[i]
        comps.append(mi)
    return np.sqrt(sum(c * c for c in comps))


def at_terms_of(metric, chi, h, nghost=4):
    """|gt^kl d_k At_il| + |3 gt^kl At_ik d_l chi/(2 chi)| per component i from a bin
    metric (read_bin_metric). The Christoffel term of P1 is left out (second order)."""
    def g(a, b, src):
        return src[tuple(sorted((a, b)))]
    gt = metric["gt"]
    mat = np.stack([np.stack([g(a, b, gt) for b in range(3)]) for a in range(3)])
    inv = np.linalg.inv(np.moveaxis(mat, (0, 1), (-2, -1)))
    inv = np.moveaxis(inv, (-2, -1), (0, 1))
    out = []
    for i in range(3):
        t1 = sum(inv[k, l] * d1(g(i, l, metric["At"]), h, k, nghost)
                 for k in range(3) for l in range(3))
        t2 = sum(inv[k, l] * g(i, k, metric["At"]) * d1(chi, h, l, nghost)
                 for k in range(3) for l in range(3)) * 1.5 / chi
        out.append(np.abs(t1) + np.abs(t2))
    return np.array(out)


def constraint_ratios(d, hist=None, nghost=4, aa=None, at_terms=None):
    """Constraint statistics of one dump. Returns dict:
    H_l1, H_rms, H_max (of the dumped H); Hn_mean (box mean of [H] per cell, this
    module) and Hn_hist (the code's box mean of [H] from the history at the dump's cycle,
    if hist is given); ratios H_l1/[H], H_rms/[H] with the history's [H] when available;
    the largest local |H|/[H]; M_rms = sqrt(<M^2>) of the dumped M_i (code: covariant);
    Mn_mean, Mn_rms of [M]; M_rms/Mn_rms and the mean of the local |M|/[M]."""
    hn = ham_norm_cells(d, aa)
    absh = np.abs(d["H"])
    out = dict(cycle=d["cycle"], time=d["time"], H_l1=float(absh.mean()),
               H_rms=float(np.sqrt(np.mean(d["H"] ** 2))), H_max=float(absh.max()),
               Hn_mean=float(hn.mean()), H_local_max_ratio=float((absh / hn).max()))
    norm = out["Hn_mean"]
    if hist is not None:
        try:
            row = history_row(hist, d["cycle"])
            out.update(Hn_hist=row["H_norm"], H_l1_hist=row["H_l1"], H_rms_hist=row["H_rms"],
                       M_rms_hist=row["M_rms"])
            norm = row["H_norm"]
        except KeyError:
            pass
    out["ratio_H_l1"] = out["H_l1"] / norm
    out["ratio_H_rms"] = out["H_rms"] / norm
    m2 = d["Mx"] ** 2 + d["My"] ** 2 + d["Mz"] ** 2
    mn = mom_norm_cells(d, nghost, at_terms)
    # flat norm of the covariant components (as P1's [M]); the history's M_rms is the
    # physical norm sqrt(gamma^ab M_a M_b) = sqrt(chi gt^ab M_a M_b), here with gt = delta
    out.update(M_rms=float(np.sqrt(m2.mean())), M_rms_phys=float(np.sqrt(np.mean(d["chi"] * m2))),
               Mn_mean=float(mn.mean()),
               Mn_rms=float(np.sqrt(np.mean(mn ** 2))))
    out["ratio_M_rms"] = out["M_rms"] / out["Mn_rms"] if out["Mn_rms"] > 0 else np.nan
    good = mn > 0
    out["ratio_M_local_mean"] = float(np.mean(np.sqrt(m2[good]) / mn[good])) \
        if good.any() else np.nan
    return out
