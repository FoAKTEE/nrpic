#ifndef UTILS_RNG_MESH_HPP_
#define UTILS_RNG_MESH_HPP_
//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file rng_mesh.hpp
//! \brief The entity of a cell for the reproducible random numbers (utils/rng.hpp): its
//! global index on its own refinement level and that level, which do not depend on the
//! division of the mesh into MeshBlocks.  Also the entity of a Fourier mode of a periodic
//! box (ModeEntity) and the stream word of the stochastic sources keyed by modes
//! (StochasticModeStream), at the end of the file.
//!
//! Use in a kernel over the cells (m,k,j,i) of a MeshBlockPack:
//!   auto off = rng::CellOffsets(pmbp);                    // once, outside the kernel
//!   ...
//!   rng::Key key{seed, stream, rng::CellEntity(off(m,0) + (i - is), off(m,1) + (j - js),
//!                                              off(m,2) + (k - ks)), step,
//!                static_cast<std::uint64_t>(off(m,3))};
//! The indices handed to CellEntity must lie in [0, 2^21).  In a ghost cell of a
//! periodic direction wrap the index first, WrapIndex(index, off(m,4+d)), so that the
//! cell and its periodic image draw the same numbers; other ghost cells have no entity.

#include <cstdint>

#include "athena.hpp"
#include "mesh/mesh.hpp"
#include "utils/rng.hpp"

namespace rng {

//----------------------------------------------------------------------------------------
//! \fn CellOffsets
//! \brief for every MeshBlock m of the pack: off(m,0..2) the global index, on the
//! refinement level of the MeshBlock, of its first active cell in x1, x2, x3; off(m,3)
//! the level relative to the root mesh; off(m,4..6) the number of cells of the whole mesh
//! on that level in x1, x2, x3.  Rebuild it after the mesh has changed.

inline DvceArray2D<std::int64_t> CellOffsets(MeshBlockPack *pmbp) {
  Mesh *pm = pmbp->pmesh;
  const int nmb = pmbp->nmb_thispack;
  auto &indcs = pm->mb_indcs;
  DvceArray2D<std::int64_t> off("rng_cell_offsets", nmb, 7);
  auto oh = Kokkos::create_mirror_view(off);
  for (int m=0; m<nmb; ++m) {
    const LogicalLocation &ll = pm->lloc_eachmb[pmbp->gids + m];
    const int lev = ll.level - pm->root_level;
    oh(m,0) = static_cast<std::int64_t>(ll.lx1)*indcs.nx1;
    oh(m,1) = static_cast<std::int64_t>(ll.lx2)*indcs.nx2;
    oh(m,2) = static_cast<std::int64_t>(ll.lx3)*indcs.nx3;
    oh(m,3) = lev;
    oh(m,4) = static_cast<std::int64_t>(pm->mesh_indcs.nx1) << lev;
    oh(m,5) = static_cast<std::int64_t>(pm->mesh_indcs.nx2) << lev;
    oh(m,6) = static_cast<std::int64_t>(pm->mesh_indcs.nx3) << lev;
  }
  Kokkos::deep_copy(off, oh);
  return off;
}

//! index mapped into [0, n) (periodic direction with n cells)
KOKKOS_INLINE_FUNCTION
std::int64_t WrapIndex(const std::int64_t i, const std::int64_t n) {
  const std::int64_t r = i % n;
  return (r < 0) ? r + n : r;
}

//----------------------------------------------------------------------------------------
// Entity of a Fourier mode of a periodic box, and the sub-streams of the stochastic
// sources (stream kStreamStochastic; registry: coord/INTERFACES/rng.md, section 6).

//! offset that maps a signed wave number onto the index range of CellEntity
constexpr std::int64_t kModeEntityOffset = static_cast<std::int64_t>(1) << 20;

//! bit of the sub-stream of kStreamStochastic that marks draws keyed by modes; the 16
//! bits below it number the degree of freedom.  Sub-streams with the bit clear are left
//! to draws keyed by cells.
constexpr std::uint32_t kStochasticModeBit = static_cast<std::uint32_t>(1) << 16;

//! entity of the Fourier mode with the integer wave numbers (nx, ny, nz), each in
//! [-2^20, 2^20): CellEntity(nx + 2^20, ny + 2^20, nz + 2^20).  The wave numbers are
//! those of the mode on the root mesh, so the entity does not depend on the resolution;
//! entity_hi stays 0.
KOKKOS_INLINE_FUNCTION
std::uint64_t ModeEntity(const std::int64_t nx, const std::int64_t ny,
                         const std::int64_t nz) {
  return CellEntity(static_cast<std::uint64_t>(nx + kModeEntityOffset),
                    static_cast<std::uint64_t>(ny + kModeEntityOffset),
                    static_cast<std::uint64_t>(nz + kModeEntityOffset));
}

//! stream word of the amplitudes of degree of freedom dof (below 2^16) keyed by modes:
//! Stream(kStreamStochastic, 2^16 + dof)
KOKKOS_INLINE_FUNCTION
std::uint64_t StochasticModeStream(const std::uint32_t dof) {
  return Stream(kStreamStochastic, kStochasticModeBit | dof);
}

} // namespace rng
#endif // UTILS_RNG_MESH_HPP_
