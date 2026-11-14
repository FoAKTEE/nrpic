"""Shared paths and readers of the working-paper figure scripts."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PAPER))
DATA = os.path.join(PAPER, "data")
FIGS = os.path.join(PAPER, "figures")
RUNS = os.path.join(REPO, "runs", "cosmo")
for p in (os.path.join(REPO, "python"), os.path.join(REPO, "cosmo", "ic"),
          os.path.join(REPO, "cosmo", "newton"), os.path.join(REPO, "cosmo", "analysis")):
    if p not in sys.path:
        sys.path.insert(0, p)
from nrpic import figstyle as fs  # noqa: E402,F401

H0, L = 1.0, 4.0
RHO0 = 3.0*H0**2/(8.0*np.pi)


def scale_factor(t):
    """Homogeneous solution in conformal time."""
    return (1.0 + 0.5*H0*t)**2


def a_of_tau(tau):
    """Proper-time scale factor."""
    return (1.0 + 1.5*H0*tau)**(2.0/3.0)


def savefig(fig, name):
    os.makedirs(FIGS, exist_ok=True)
    fig.savefig(os.path.join(FIGS, name + ".pdf"))
    fig.savefig(os.path.join(FIGS, name + ".png"), dpi=200)
    print(os.path.join(FIGS, name + ".png"))
