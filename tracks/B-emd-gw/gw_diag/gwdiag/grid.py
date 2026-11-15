"""Periodic uniform mesh and the array layout used by every function of gwdiag.

Array layout (the same as AthenaK, Kokkos LayoutRight, and the NRFIELD dumps):

* a scalar field is a float64 array f[k, j, i] of shape (nz, ny, nx); the last index i
  runs along x and is the fastest, j along y, k along z;
* a vector is an array v[a, k, j, i] of shape (3, nz, ny, nx), component a = 0, 1, 2 for
  x, y, z;
* a symmetric rank-2 tensor is stored in full, T[a, b, k, j, i] of shape
  (3, 3, nz, ny, nx), with T[a, b] == T[b, a];
* coordinates are cell centres, x_i = xmin + (i + 1/2) dx, as in AthenaK.

So the spatial direction a lives on array axis -1 - a (x on axis -1, z on axis -3).
Every routine converts between the two numberings through ``axis_of``.
"""
import numpy as np


def axis_of(a):
    """Array axis of spatial direction a (0 = x, 1 = y, 2 = z) for a field f[k, j, i]."""
    return -1 - a


class Grid:
    """Uniform periodic cell-centred mesh.

    n    = (nx, ny, nz) number of cells,
    L    = (Lx, Ly, Lz) box lengths,
    xmin = lower corner (default -L/2, a box centred on the origin).
    """

    def __init__(self, n, L, xmin=None):
        self.n = tuple(int(v) for v in n)
        self.L = tuple(float(v) for v in L)
        if xmin is None:
            xmin = tuple(-0.5 * v for v in self.L)
        self.xmin = tuple(float(v) for v in xmin)
        self.dx = tuple(l / m for l, m in zip(self.L, self.n))
        self.shape = (self.n[2], self.n[1], self.n[0])
        self.ncell = self.n[0] * self.n[1] * self.n[2]

    def __repr__(self):
        return f"Grid(n={self.n}, L={self.L}, xmin={self.xmin})"

    def axes(self):
        """Cell-centre coordinates along x, y, z (three 1D arrays)."""
        return [self.xmin[a] + (np.arange(self.n[a]) + 0.5) * self.dx[a] for a in range(3)]

    def mesh(self):
        """X, Y, Z arrays of shape (nz, ny, nx)."""
        x, y, z = self.axes()
        Z, Y, X = np.meshgrid(z, y, x, indexing="ij")
        return X, Y, Z

    def kvec(self, real=True):
        """Angular wavevectors (3, nz, ny, nkx) of the discrete Fourier modes.

        real=True: the half space of numpy.fft.rfftn (nkx = nx//2 + 1); otherwise the
        full space of fftn (nkx = nx). Component 0 is k_x, 1 is k_y, 2 is k_z.
        """
        kx = (np.fft.rfftfreq if real else np.fft.fftfreq)(self.n[0], self.dx[0]) * 2 * np.pi
        ky = np.fft.fftfreq(self.n[1], self.dx[1]) * 2 * np.pi
        kz = np.fft.fftfreq(self.n[2], self.dx[2]) * 2 * np.pi
        KZ, KY, KX = np.meshgrid(kz, ky, kx, indexing="ij")
        return np.array([KX, KY, KZ])

    def nyquist_mask(self, real=True):
        """True on the Nyquist planes (k_a = -pi/dx_a for even n_a) of the Fourier array."""
        shp = self.kvec(real).shape[1:]
        m = np.zeros(shp, dtype=bool)
        if self.n[0] % 2 == 0:
            if real:
                m[:, :, -1] = True
            else:
                m[:, :, self.n[0] // 2] = True
        if self.n[1] % 2 == 0:
            m[:, self.n[1] // 2, :] = True
        if self.n[2] % 2 == 0:
            m[self.n[2] // 2, :, :] = True
        return m

    def rfft_weights(self):
        """Multiplicity of each rfftn mode in a sum over the full Fourier space: 2 for
        modes whose conjugate partner is not stored, 1 on the planes k_x = 0 and (even nx)
        k_x = Nyquist."""
        nkx = self.n[0] // 2 + 1
        w = np.full(nkx, 2.0)
        w[0] = 1.0
        if self.n[0] % 2 == 0:
            w[-1] = 1.0
        return np.broadcast_to(w, (self.n[2], self.n[1], nkx))

    def wavenumber_bins(self, dk=None):
        """Bin edges in |k| of width dk (default: the smallest lattice spacing 2 pi / max L),
        centred on integer multiples of dk."""
        if dk is None:
            dk = 2 * np.pi / max(self.L)
        kmax = np.sqrt(sum((np.pi / d) ** 2 for d in self.dx))
        nb = int(np.ceil(kmax / dk)) + 1
        return (np.arange(nb + 1) - 0.5) * dk, dk
