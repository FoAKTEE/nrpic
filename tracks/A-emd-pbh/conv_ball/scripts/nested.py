"""Nested static-refinement geometry and nested particle lattice of the package conv_ball
(Track A, wave 3). No evolution here (decision 0010): geometry bookkeeping, a lattice
generator on top of expball's model, and the cost and memory model of DESIGN.md.

Geometry "nest(h_f, outer)": a root level over [-outer, outer]^3 and L = log2(outer) refined
levels; level l (0 = root) covers the cube |x|_inf < b_l = outer / 2^l with cells
h_l = h_f 2^(L - l). Every level box therefore holds n = 2 b_l / h_l = 2 / h_f cells per
direction, the finest box is always [-1, 1]^3, and the level boundaries sit at the radii
1, 2, 4, 8 (, 16) M for every finest cell h_f: halving h_f halves every cell and keeps every
boundary. MeshBlocks of n/4 cells per direction make each level box 4 blocks wide, so that
the next box is exactly the central 2 x 2 x 2 blocks (one block of margin: 2:1 nesting).
Leaf MeshBlocks: 56 per level below the finest (64 - 8) and 64 on the finest.

Nested lattice: one site per cell of the local level (sub = 1) or sub^3 sites per cell,
at the centres of the cells of a mesh of spacing h_l / sub, inside the matter
(rbar <= rbar_m); site mass rho_* psi^6 s^3 (expball/particles.lattice, mass-weighted
midpoint rule), the sites within one local spacing of the matter edge scaled together so
that the sum equals the rest mass of the ball (expball's surface correction).
"""
import math

import numpy as np


def nest_levels(h_f, outer=16.0):
    """[(b_l, h_l)] from the root (l = 0) to the finest level."""
    L = int(round(math.log2(outer)))
    assert abs(2 ** L - outer) < 1e-12, outer
    return [(outer / 2 ** l, h_f * 2 ** (L - l)) for l in range(L + 1)]


def nest_blocks(h_f, outer=16.0):
    """Mesh numbers of the geometry: root cells per direction, block size, leaf blocks,
    leaf cells."""
    lev = nest_levels(h_f, outer)
    n = int(round(2 * lev[0][0] / lev[0][1]))
    nb = n // 4
    assert 4 * nb == n, n
    L = len(lev) - 1
    leaf_blocks = 56 * L + 64
    return dict(levels=lev, n_root=n, block=nb, leaf_blocks=leaf_blocks,
                leaf_cells=leaf_blocks * nb ** 3, finest=h_f, outer=outer, L=L)


def nested_sites(levels, sub=1, rmax=None):
    """Site positions of the nested lattice (all of space within rmax): levels from the
    root (largest box) to the finest, as returned by nest_levels. Returns (x[N,3], s[N])
    with s the local site spacing."""
    out_x, out_s = [], []
    nlev = len(levels)
    for l, (b, h) in enumerate(levels):
        s = h / sub
        bin_ = levels[l + 1][0] if l + 1 < nlev else 0.0
        lim = b if rmax is None else min(b, rmax + s)
        nh = int(math.ceil(lim / s - 1e-9))
        k = (np.arange(-nh, nh, dtype=np.int64) + 0.5) * s
        # build per x-slab to keep the memory small
        for xi in k:
            Y, Z = np.meshgrid(k, k, indexing="ij")
            Y, Z = Y.ravel(), Z.ravel()
            X = np.full_like(Y, xi)
            ax = np.maximum(np.abs(X), np.maximum(np.abs(Y), np.abs(Z)))
            keep = (ax < b) & (ax >= bin_)
            if rmax is not None:
                keep &= X * X + Y * Y + Z * Z <= (rmax + 0.0) ** 2 + 1e-300
            if np.any(keep):
                out_x.append(np.stack([X[keep], Y[keep], Z[keep]], axis=-1))
                out_s.append(np.full(int(keep.sum()), s))
    return np.concatenate(out_x), np.concatenate(out_s)


def nested_lattice(ball, levels, sub=1, surface_correction=True, species=0):
    """Mass-weighted nested lattice inside the matter of an expball Ball; the counterpart of
    expball/particles.lattice for a nested mesh. Returns (x, u, m, sp, s) with s the local
    spacing of each site."""
    rm = ball.matter_rbar()
    x, s = nested_sites(levels, sub, rmax=rm)
    r = np.sqrt(np.sum(x * x, axis=1))
    f = ball.fields(r, ("rho", "u"))
    m = f["rho"] * (1.0 + f["u"]) ** 6 * s ** 3
    pos = m > 0
    x, r, m, s = x[pos], r[pos], m[pos], s[pos]
    if surface_correction:
        layer = r > rm - s
        M0 = ball.rest_mass()
        m = m.copy()
        m[layer] *= (M0 - m[~layer].sum()) / m[layer].sum()
    n = len(m)
    return x, np.zeros((n, 3)), m, np.full(n, species, dtype=np.int32), s


def count_sites(levels, sub, rm):
    """Number of nested-lattice sites inside the sphere rbar <= rm (geometry only; the
    lattice drops sites of zero density, none inside the matter)."""
    x, s = nested_sites(levels, sub, rmax=rm)
    return int(len(s)), {float(v): int(np.sum(s == v)) for v in np.unique(s)}


# ------------------------------------------------------------------ cost and memory model
# Measured (run ids in DESIGN.md section 3):
#   BH-1R A-20261119-164634-f1fe887: 568 blocks of 32^3 (static refinement), 1317216
#     particles, 1024 cycles, 1.7187 s per cycle, gpu_mem_peak 80633 MiB;
#   BH-1 bh_n256 and SR-1L sr1l_n256 of A-20261119-144419-13d5601: 64 blocks of 64^3,
#     uniform, 164968 and 28768 particles: 1.0645 and 1.0561 s per cycle, peaks 41223
#     and 41195 MiB.
MIB_PER_BLOCK32 = 80633.0 / 568          # static refinement, ghosts 4, includes the particle part
MIB_PER_PARTICLE = (41223.0 - 41195.0) / (164968 - 28768)
S_PER_PARTICLE_STEP = (1.0645 - 1.0561) / (164968 - 28768)
S_PER_CELL_STEP32 = (1.7187 - 1317216 * S_PER_PARTICLE_STEP) / (568 * 32 ** 3)
S_STEP_FLOOR = 0.03                       # JUDGEMENT: launch latency of a step on a tiny mesh


def ghost_factor(nb, ng=4):
    """Ghosted over interior volume of a block, relative to a 32^3 block."""
    return ((nb + 2 * ng) / nb) ** 3 / ((32 + 2 * ng) / 32) ** 3


def memory_mib(blocks, nb, nparticles):
    """[JUDGEMENT] memory of a static-refinement run: per block the 32^3 value scaled by the
    ghosted volume, plus the particles (the particle part of BH-1R is inside the block
    value, so this slightly over-counts)."""
    per_block = MIB_PER_BLOCK32 * ((nb + 8) / 40.0) ** 3
    return blocks * per_block + nparticles * MIB_PER_PARTICLE + 500.0


def seconds_per_step(cells, nb, nparticles):
    """[JUDGEMENT] cost per step: the per-cell cost of BH-1R scaled by the ghosted volume of
    the block size, plus the particles, with a floor for tiny meshes."""
    return max(S_STEP_FLOOR, cells * S_PER_CELL_STEP32 * ghost_factor(nb) + nparticles * S_PER_PARTICLE_STEP)
