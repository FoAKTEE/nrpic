"""Initial data of the single-wavelength problem at small amplitude, for a lattice with
particles at the cell centres and for the lattice shifted by half a spacing: deposited
density contrast and solved conformal factor along the mesh line next to the density
peak, with the dictionary values (working paper, initial-data figure)."""
import os

import numpy as np

from common import DATA, H0, L, RHO0
import make_east as me

delta, n = 1e-4, 32
k = 2.0*np.pi/L
hk2 = (H0/k)**2
h = L/n
xc = (np.arange(n) + 0.5)*h
j = int(round(0.25*L/h))          # first cell beyond the peak in y and z
out = {"x": xc, "delta": delta, "n": n}
for key, stagger in (("centred", False), ("shifted", True)):
    x, u, m, r, K, alpha, info, fid = me.build(delta, n, nfilter=0, stagger=stagger,
                                               verbose=False)
    E = r["E"]
    out[f"{key}_contrast"] = E[:, j, j]/RHO0 - 1.0
    out[f"{key}_psi"] = r["psi"][:, j, j] - 1.0
    out[f"{key}_psi_err"] = info["max_psi_minus_dictionary"]
    print(key, "largest difference of psi from the dictionary:",
          info["max_psi_minus_dictionary"], "of", 0.5*info["max_abs_psiN"])
d = [delta, 0.9*delta, 1.1*delta]
dN = d[0]*np.sin(k*xc) + (d[1] + d[2])*np.sin(k*xc[j])
out["target_contrast"] = (1.0 + 3.0*hk2)*dN
out["target_psi"] = (1.0 + 3.0*hk2*dN)**0.25 - 1.0
np.savez(os.path.join(DATA, "id_profiles.npz"), **out)
print("wrote", os.path.join(DATA, "id_profiles.npz"))
