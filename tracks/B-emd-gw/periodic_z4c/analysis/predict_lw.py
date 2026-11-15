#!/usr/bin/env python3
"""Prediction (written before the runs) of the amplitude and phase errors of the linear
TT wave along x, from the Fourier symbol of the discrete operators of the code.

For a TT wave along x with chi = 1 and Gamma = 0, the Z4c system reduces to
  d_t gt = -2 At - d gt,   d_t At = -(1/2) D2 gt - d At,
with D2 the centred second-derivative stencil of athenak/src/utils/finite_diff.hpp
(order 2(ng-1)) and d the Kreiss-Oliger damping rate of the mode,
  d = sigma 2^(-2 ng) (2 sin(theta/2))^(2 ng) / dx,   theta = k dx,
(Diss<NGHOST> times diss = sigma 2^(-2ng) (-1)^(ng+1), athenak/src/z4c/z4c.cpp line 168).
The eigenvalues of the semi-discrete system are -d +- i w_h, w_h^2 = -symbol(D2)/... ;
RK4 multiplies each mode by R(lambda dt) per step, R(z) = 1 + z + z^2/2 + z^3/6 + z^4/24.
The step is dt = cfl dx (the Z4c step limit of athenak/src/z4c/z4c_newdt.cpp for a unit
lapse; checked against the cycle count of the trial run, 128 cycles for t = 1 at 32 cells
and cfl 0.25). Output: relative amplitude error and phase error (radians, negative =
lagging) after time T, per resolution, and the local orders.

    python3 predict_lw.py [--ng 4 --cfl 0.25 --sigma 0.5 --T 10]
"""
import argparse
import numpy as np

D2 = {2: [1.0, -2.0], 3: [-1/12, 4/3, -5/2], 4: [1/90, -3/20, 3/2, -49/18]}


def symbol_d2(ng, th):
    c = D2[ng]
    n = len(c) - 1
    s = c[-1]*np.ones_like(th)
    for j in range(1, n + 1):
        s = s + 2*c[n - j]*np.cos(j*th)
    return s                       # times 1/dx^2: symbol of D2


def predict(ng, cfl, sigma, T, N, k=2*np.pi, L=1.0):
    dx = L/N
    th = k*dx
    w2 = -symbol_d2(ng, th)/dx**2           # D2 e^{ikx} = symbol/dx^2 e^{ikx}
    wh = np.sqrt(w2)
    d = sigma*2.0**(-2*ng)*(2*np.sin(th/2))**(2*ng)/dx
    nsteps = int(np.ceil(T/(cfl*dx) - 1e-9))
    dt = T/nsteps                       # the last step is shortened to reach T; an
    lam = -d + 1j*wh                    # equal-step approximation is used here
    z = lam*dt
    R = 1 + z + z**2/2 + z**3/6 + z**4/24
    G = R**nsteps
    amp_err = abs(G) - 1.0
    ph_err = np.angle(G*np.exp(-1j*k*T))     # numerical minus exact phase advance
    return amp_err, ph_err, nsteps, d, wh/k - 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ng", type=int, default=4)
    ap.add_argument("--cfl", type=float, default=0.25)
    ap.add_argument("--sigma", type=float, default=0.5)
    ap.add_argument("--T", type=float, default=10.0)
    ap.add_argument("--N", type=int, nargs="*", default=[16, 32, 64, 128])
    a = ap.parse_args()
    print(f"ng={a.ng} cfl={a.cfl} sigma={a.sigma} T={a.T}")
    print(" N   steps   amp_err      phase_err    semi-discrete dw/w   KO rate")
    prev = None
    for N in a.N:
        ae, pe, ns, d, dw = predict(a.ng, a.cfl, a.sigma, a.T, N)
        s = f"{N:4d} {ns:6d}  {ae:+.3e}  {pe:+.3e}   {dw:+.3e}        {d:.3e}"
        if prev is not None:
            s += f"   orders amp {np.log2(abs(prev[0]/ae)):.2f} phase {np.log2(abs(prev[1]/pe)):.2f}"
        print(s)
        prev = (ae, pe)


if __name__ == "__main__":
    main()
