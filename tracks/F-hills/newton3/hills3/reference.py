"""Numbers printed in the three reference papers, each with its locator.

SKR  = arXiv:0911.1136 v1, kb-data/raw/arxiv/0911.1136/v1/src/prp.tex
KHSR = arXiv:1201.4794 v1, kb-data/raw/arxiv/1201.4794/v1/src/ms.tex
BKRS = arXiv:1804.02911 v1, kb-data/raw/arxiv/1804.02911/v1/src/mnras.tex
Energies in units of (G m1 m2 / a)(M/m)^(1/3). Probabilities as fractions.
"""
import numpy as np

SKR = {
    "Dmax_prograde": (2.1, "SKR prp.tex:846-847 (also 777-778)"),
    "Dmax_retrograde": (0.44, "SKR prp.tex:846-847 (also 778-779)"),
    "D_best_prograde": (0.15, "SKR prp.tex:737-738, 854"),
    "P_prograde_0.06_0.3": ((0.980, 0.988), "SKR prp.tex:1086-1087"),
    "P_deep_saturation": (0.80, "SKR prp.tex:735-736 ('~80%')"),
    "survival_radial": (0.19, "SKR prp.tex:748-749"),
    "survivors_harder_radial": (0.90, "SKR prp.tex:752-753"),
    "survival_windows_radial_pi": (((-0.31, -0.12), (0.69, 0.88)), "SKR prp.tex:785"),
    "Emax_prograde": (27.3, "SKR prp.tex:848-849 (peak near D ~ 0.1, 832-834)"),
    "Emax_retrograde": (1.8, "SKR prp.tex:848-849"),
    "Emean_prograde_Duniform": (1.46, "SKR prp.tex:850-853"),
    "Emean_retrograde_Duniform": (0.50, "SKR prp.tex:850-853"),
    "Emean_both_Duniform": (1.36, "SKR prp.tex:850-853"),
    "vmean_deep": (0.99, "SKR prp.tex:993-994, units sqrt(2 G m2/a)(M/m)^(1/6)"),
    "full_vs_restricted": (1e-3, "SKR prp.tex:631 (D=0.1, phi=4pi/5, prograde, M/m=1e6, m1/m2=3, r0=10 r_t)"),
    "phase_sampling": ("3000 equally spaced phases in [0, pi] per D", "SKR prp.tex:763-764"),
    "start_radius": ("r0 = 10 r_t", "SKR prp.tex:599"),
}

KHSR = {
    "full_vs_restricted": (1e-3, "KHSR ms.tex:604-605"),
    "deep_disruption_e1": (0.80, "KHSR ms.tex:677-679"),
    "dE_definition": ("dE = (m1/m) E2 - (m2/m) E1", "KHSR ms.tex:1102-1103"),
    "start_radius": ("r0 = 15 r_t", "KHSR ms.tex:617-618"),
    "spike_prograde_D0.1": (30.0, "KHSR ms.tex:307-309 (footnote)"),
}

# polynomial fits for general (isotropic) orientation, D < 2.1
BKRS_PDIS = np.array([0.8830, -0.0809, -1.0541, 1.5377, -0.9249, 0.1881])
BKRS_EMEAN = np.array([0.9582, 3.3268, -6.6801, 5.2785, -1.8731, 0.2260])

BKRS = {
    "Pdis_fit": (BKRS_PDIS, "BKRS mnras.tex:372-376; accuracy < 1% for D <~ 1, 5% at 1.8, 20% at 2 (377-379)"),
    "Emean_fit": (BKRS_EMEAN, "BKRS mnras.tex:433-439; accuracy < 1% for D <~ 1, 3% at 1.8, 10% at 2 (440-441)"),
    "Dmax_all": (2.1, "BKRS mnras.tex:361-362"),
    "P_deep_plateau": (0.88, "BKRS mnras.tex:368-370"),
    "P_at_1e-3_and_0.1": (0.87, "BKRS mnras.tex:606"),
    "coplanar_saturation": (0.80, "BKRS mnras.tex:380-383"),
    "deep_Emean_Emax": ((1.0, 2.0), "BKRS mnras.tex:462 ('<E> ~ 1 and E_max ~ 2 for D << 1')"),
    "survivor_theta_range_pi": ((0.15, 0.85), "BKRS mnras.tex:507-509"),
    "deep_P_min_theta_pi2": (0.80, "BKRS mnras.tex:509"),
    "Emean_ratio_pi2_over_0": ((1.4, 1.7), "BKRS mnras.tex:524-525"),
    "radial_vs_parabolic": (0.02, "BKRS mnras.tex:506 (P difference < 2% for D < 1e-4)"),
    "collision_deep": ((0.05, 0.07), "BKRS mnras.tex:757-763 (r_min < a/5, D < 0.1)"),
    "collision_peak": ((1.6, 0.14), "BKRS mnras.tex:763-764 (peak D ~ 1.6, ~14%)"),
    "Dmax_eccentric_prograde": ({0.0: 2.1, 0.3: 2.8, 0.6: 3.2, 0.9: 3.2}, "BKRS mnras.tex:623-624"),
    "sampling": ("2000 orientations on the sphere x 200 phases in [0, pi)", "BKRS mnras.tex:352-357"),
    "sampling_convergence": ("< 0.3% change for 1/4..1 of the points", "BKRS mnras.tex:605-606"),
}


def bkrs_pdis(D):
    D = np.asarray(D, dtype=float)
    return np.polynomial.polynomial.polyval(D, BKRS_PDIS)


def bkrs_emean(D):
    D = np.asarray(D, dtype=float)
    return np.polynomial.polynomial.polyval(D, BKRS_EMEAN)
