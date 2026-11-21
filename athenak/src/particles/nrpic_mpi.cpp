//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file nrpic_mpi.cpp
//! \brief The NRPIC module on more than one MPI rank (tracks/core/interfaces/mpi.md).
//!
//! A run on several ranks is the same computation as on one rank: the same MeshBlocks,
//! the same particles with the same tags, the same contributions to every cell; only the
//! order of additions differs.  What this file adds to the one-rank module:
//!   - a table of all MeshBlocks of the mesh (extent, level, rank), so that a point that
//!     the MeshBlocks of this rank do not contain is found on another rank or outside;
//!   - ownership: a particle lives on the rank of the MeshBlock that contains it and is
//!     handed over when it leaves; the particles of a rank stay ordered by tag;
//!   - deposit: a cloud that reaches MeshBlocks of other ranks is sent to them as a
//!     packet, and each rank adds the cloud cells that lie in its own MeshBlocks;
//!   - sums over the ranks, the probe, and files written by rank 0 in the order of the
//!     tags with the formats of the one-rank module.
//! Rank 0 reads the particle file and the particle restart file; the first ownership
//! pass distributes the particles.  Nothing in this file runs on one rank.

#include <algorithm>
#include <climits>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <numeric>
#include <string>
#include <utility>
#include <vector>

#include "athena.hpp"
#include "globals.hpp"
#include "parameter_input.hpp"
#include "mesh/mesh.hpp"
#include "bvals/bvals.hpp"
#include "coordinates/cell_locations.hpp"
#include "z4c/tmunu.hpp"
#include "particles/particles.hpp"
#include "particles/nrpic_kernels.hpp"
#include "particles/nrpic_mesh.hpp"
#include "particles/nrpic_cloud.hpp"
#include "particles/nrpic_mpi.hpp"

namespace particles {

namespace {

void MpiFatal(const std::string &msg) {
  std::cout << "### FATAL ERROR in nrpic_mpi.cpp" << std::endl << msg << std::endl;
#if MPI_PARALLEL_ENABLED
  MPI_Abort(MPI_COMM_WORLD, 1);
#endif
  std::exit(EXIT_FAILURE);
}

// number of Reals of a deposit packet: position, lattice spacing, level, amounts
constexpr int kPacket = 7 + Tmunu::N_Tmunu;
// largest number of ranks a cloud can reach (one per lattice cell)
constexpr int kMaxCloudRanks = 64;

#if MPI_PARALLEL_ENABLED
//! number of entries of the ascending array a (length n) that are smaller than t
template <class ViewT>
KOKKOS_INLINE_FUNCTION
int LowerBound(const ViewT &a, const int n, const int t) {
  int lo = 0, hi = n;
  while (lo < hi) {
    const int mid = lo + (hi - lo)/2;
    if (a(mid) < t) { lo = mid + 1; } else { hi = mid; }
  }
  return lo;
}

//! ranks other than this one that hold lattice cells of the cloud of a particle in
//! MeshBlock mo; returns their number
template <class SizeViewT>
KOKKOS_INLINE_FUNCTION
int CloudRanks(const nrpic::CloudGeometry &cg, const SizeViewT &sz, const int nmb,
               const int mo, const DvceArray2D<Real> &gbx, const DvceArray2D<int> &gbl,
               const int gnmb, const int myrank, const Real xp[3], const Real gmin[3],
               const Real h[3], int rk[kMaxCloudRanks]) {
  Real xb[3], wt[3][4];
  nrpic::CloudWeights(cg.nb, xp, gmin, h, xb, wt);
  // all cell centres inside the particle's own MeshBlock: nothing to send
  const Real e = static_cast<Real>(cg.nb - 1);
  if (xb[0] >= sz(mo).x1min && xb[0] + e*h[0] < sz(mo).x1max &&
      xb[1] >= sz(mo).x2min && xb[1] + e*h[1] < sz(mo).x2max &&
      xb[2] >= sz(mo).x3min && xb[2] + e*h[2] < sz(mo).x3max) {
    return 0;
  }
  const int nb = cg.nb;
  int n = 0;
  for (int c=0; c<nb*nb*nb; ++c) {
    const int c1 = c % nb, c2 = (c/nb) % nb, c3 = c/(nb*nb);
    const Real xf = nrpic::WrapCoord(xb[0] + c1*h[0], cg.dmin[0], cg.dlen[0], cg.per[0]);
    const Real yf = nrpic::WrapCoord(xb[1] + c2*h[1], cg.dmin[1], cg.dlen[1], cg.per[1]);
    const Real zf = nrpic::WrapCoord(xb[2] + c3*h[2], cg.dmin[2], cg.dlen[2], cg.per[2]);
    if (nrpic::FindBlock(sz, nmb, mo, xf, yf, zf) >= 0) continue;
    const int g = nrpic::FindBlockGlobal(gbx, gnmb, xf, yf, zf);
    if (g < 0) continue;                  // outside the mesh
    const int r = gbl(g,1);
    if (r == myrank) continue;
    bool known = false;
    for (int q=0; q<n; ++q) { known = known || (rk[q] == r); }
    if (!known) { rk[n++] = r; }
  }
  return n;
}

//! lattice spacing of the cloud of a particle: that of its MeshBlock, scaled by the
//! power of two that the deposit kernel applied (ls = level of the cloud - level of the
//! MeshBlock)
KOKKOS_INLINE_FUNCTION
void CloudSpacing(const int ls, Real h[3]) {
  if (ls < 0) {
    const Real fac = static_cast<Real>(1 << (-ls));
    h[0] *= fac; h[1] *= fac; h[2] *= fac;
  } else if (ls > 0) {
    const Real fac = 1.0/static_cast<Real>(1 << ls);
    h[0] *= fac; h[1] *= fac; h[2] *= fac;
  }
}

//! exchange of records between all pairs of ranks: sbuf holds the records for the
//! ranks in ascending order (scnt[r] records of nrec entries each for rank r); returns
//! what arrived, ordered by the rank it came from, and the numbers in rcnt
template <typename T>
void ExchangeRecords(MPI_Comm comm, MPI_Datatype type, const int nrec, const int tag,
                     const std::vector<int> &scnt, const std::vector<T> &sbuf,
                     std::vector<int> &rcnt, std::vector<T> &rbuf) {
  const int nranks = global_variable::nranks;
  rcnt.assign(nranks, 0);
  MPI_Alltoall(const_cast<int*>(scnt.data()), 1, MPI_INT, rcnt.data(), 1, MPI_INT, comm);
  std::size_t ntot = 0;
  for (int r=0; r<nranks; ++r) { ntot += static_cast<std::size_t>(rcnt[r]); }
  rbuf.resize(ntot*nrec);
  std::vector<MPI_Request> req;
  std::size_t off = 0;
  for (int r=0; r<nranks; ++r) {
    if (rcnt[r] == 0) continue;
    if (static_cast<std::int64_t>(rcnt[r])*nrec > INT_MAX) {
      MpiFatal("a message between two ranks exceeds 2^31 entries");
    }
    req.emplace_back(MPI_REQUEST_NULL);
    MPI_Irecv(rbuf.data() + off, rcnt[r]*nrec, type, r, tag, comm, &req.back());
    off += static_cast<std::size_t>(rcnt[r])*nrec;
  }
  off = 0;
  for (int r=0; r<nranks; ++r) {
    if (scnt[r] == 0) continue;
    if (static_cast<std::int64_t>(scnt[r])*nrec > INT_MAX) {
      MpiFatal("a message between two ranks exceeds 2^31 entries");
    }
    req.emplace_back(MPI_REQUEST_NULL);
    MPI_Isend(const_cast<T*>(sbuf.data()) + off, scnt[r]*nrec, type, r, tag, comm,
              &req.back());
    off += static_cast<std::size_t>(scnt[r])*nrec;
  }
  if (!req.empty()) {
    MPI_Waitall(static_cast<int>(req.size()), req.data(), MPI_STATUSES_IGNORE);
  }
}
#endif // MPI_PARALLEL_ENABLED

} // namespace

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiInit
//! \brief notes whether the run has more than one rank, and stops when an option that
//! has not been ported to several ranks is switched on

void Particles::NrpicMpiInit(ParameterInput *pin) {
  nr_multirank = (global_variable::nranks > 1);
  if (!nr_multirank) return;
  std::string what;
  if (nropt.newton) { what = "pusher = newton (Newtonian mode)"; }
  if (coll.on) { what = "collisions"; }
  if (kick.on) { what = "test_kick"; }
  if (nropt.curv_dt > 0.0) { what = "curv_dt (curvature records)"; }
  // options of releases core-v0.4 and core-v0.5 whose sums, records or deposit are those
  // of one rank (merge of core/mpi into core/nrpic)
  if (acc.on || acc.record) {
    what = "removal_record, acc_nsphere, peri_count (accretion diagnostics)";
  }
  if (pert.on) { what = "perturb_gamma"; }
  if (ids.on) { what = "id_solve (initial-data solver)"; }
  if (region.dcycle > 0) { what = "region_dcycle (region norms)"; }
  if (nropt.deposit_fine) {
    what = "deposit_fine_shape (the part of a cloud on another rank has no fine shape)";
  }
  if (!what.empty()) {
    MpiFatal("<particles> " + what + " has not been ported to more than one MPI rank "
             "(tracks/core/interfaces/mpi.md, section 6)");
  }
  if (global_variable::my_rank == 0) {
    std::cout << "NRPIC: " << global_variable::nranks << " MPI ranks; particle files are "
              << "read and written by rank 0" << std::endl;
  }
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiBuildBlockTable
//! \brief extent, level and rank of every MeshBlock of the mesh, on the device.  The
//! edges are computed as in the MeshBlock constructor (mesh/meshblock.cpp), so they
//! equal those of mb_size bit for bit; this is checked for the MeshBlocks of this rank.

void Particles::NrpicMpiBuildBlockTable() {
  Mesh *pm = pmy_pack->pmesh;
  const int seq = pm->GetAMRLoadBalanceUpdateSeq();
  const int nt = pm->nmb_total;
  if (gb_nmb == nt && gb_seq == seq) return;
  Kokkos::realloc(gb_ext, nt, 6);
  Kokkos::realloc(gb_lr, nt, 2);
  auto eh = Kokkos::create_mirror_view(gb_ext);
  auto lh = Kokkos::create_mirror_view(gb_lr);
  auto &ms = pm->mesh_size;
  for (int g=0; g<nt; ++g) {
    const LogicalLocation &ll = pm->lloc_eachmb[g];
    const std::int32_t n1 = pm->nmb_rootx1 << (ll.level - pm->root_level);
    const std::int32_t n2 = pm->nmb_rootx2 << (ll.level - pm->root_level);
    const std::int32_t n3 = pm->nmb_rootx3 << (ll.level - pm->root_level);
    eh(g,0) = (ll.lx1 == 0) ? ms.x1min : LeftEdgeX(ll.lx1, n1, ms.x1min, ms.x1max);
    eh(g,1) = (ll.lx1 == n1-1) ? ms.x1max : LeftEdgeX(ll.lx1+1, n1, ms.x1min, ms.x1max);
    eh(g,2) = (ll.lx2 == 0) ? ms.x2min : LeftEdgeX(ll.lx2, n2, ms.x2min, ms.x2max);
    eh(g,3) = (ll.lx2 == n2-1) ? ms.x2max : LeftEdgeX(ll.lx2+1, n2, ms.x2min, ms.x2max);
    eh(g,4) = (ll.lx3 == 0) ? ms.x3min : LeftEdgeX(ll.lx3, n3, ms.x3min, ms.x3max);
    eh(g,5) = (ll.lx3 == n3-1) ? ms.x3max : LeftEdgeX(ll.lx3+1, n3, ms.x3min, ms.x3max);
    lh(g,0) = ll.level;
    lh(g,1) = pm->rank_eachmb[g];
  }
  // the MeshBlocks of this rank must appear in the table with their own edges
  auto &mbs = pmy_pack->pmb->mb_size;
  const int gids = pmy_pack->gids;
  for (int m=0; m<pmy_pack->nmb_thispack; ++m) {
    const int g = gids + m;
    const auto &s = mbs.h_view(m);
    if (eh(g,0) != s.x1min || eh(g,1) != s.x1max || eh(g,2) != s.x2min ||
        eh(g,3) != s.x2max || eh(g,4) != s.x3min || eh(g,5) != s.x3max ||
        lh(g,1) != global_variable::my_rank) {
      MpiFatal("the table of all MeshBlocks disagrees with MeshBlock "
               + std::to_string(g) + " of rank "
               + std::to_string(global_variable::my_rank));
    }
  }
  Kokkos::deep_copy(gb_ext, eh);
  Kokkos::deep_copy(gb_lr, lh);
  gb_nmb = nt;
  gb_seq = seq;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiUpdateCounts
//! \brief particle numbers of the mesh: this rank, each rank, all ranks

void Particles::NrpicMpiUpdateCounts() {
  Mesh *pm = pmy_pack->pmesh;
  pm->nprtcl_thisrank = nprtcl_thispack;
  pm->nprtcl_eachrank[global_variable::my_rank] = nprtcl_thispack;
#if MPI_PARALLEL_ENABLED
  int np = nprtcl_thispack;
  MPI_Allgather(&np, 1, MPI_INT, pm->nprtcl_eachrank, 1, MPI_INT, MPI_COMM_WORLD);
#endif
  std::int64_t ntot = 0;
  for (int r=0; r<global_variable::nranks; ++r) { ntot += pm->nprtcl_eachrank[r]; }
  if (ntot > INT_MAX) { MpiFatal("more than 2^31 particles"); }
  pm->nprtcl_total = static_cast<int>(ntot);
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiAssignBlocks
//! \brief NrpicAssignBlocks on several ranks: the grid ID of each particle becomes the
//! global ID of the MeshBlock that contains it, on this rank or on another, or -1 if it
//! has left the mesh

void Particles::NrpicMpiAssignBlocks() {
  NrpicMpiBuildBlockTable();
  const int np = nprtcl_thispack;
  if (np == 0) return;
  auto &pr = prtcl_rdata;
  auto &pi = prtcl_idata;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int gids = pmy_pack->gids;
  const int nmb = pmy_pack->nmb_thispack;
  auto gbx = gb_ext;
  const int gnmb = gb_nmb;
  const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3] = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
  par_for("nrpic_mpi_assign", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
    if (pi(PGID,p) >= 0) {
      pr(IPX,p) = nrpic::WrapCoord(pr(IPX,p), dmin[0], dlen[0], per[0]);
      pr(IPY,p) = nrpic::WrapCoord(pr(IPY,p), dmin[1], dlen[1], per[1]);
      pr(IPZ,p) = nrpic::WrapCoord(pr(IPZ,p), dmin[2], dlen[2], per[2]);
      const int m = nrpic::FindBlock(sz, nmb, pi(PGID,p) - gids, pr(IPX,p), pr(IPY,p),
                                     pr(IPZ,p));
      if (m >= 0) {
        pi(PGID,p) = m + gids;
      } else {
        pi(PGID,p) = nrpic::FindBlockGlobal(gbx, gnmb, pr(IPX,p), pr(IPY,p), pr(IPZ,p));
      }
    }
  });
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiRemoveFlagged
//! \brief NrpicRemoveFlagged on several ranks: counts and removes the particles with a
//! negative grid ID, hands the particles whose MeshBlock is on another rank to that
//! rank, and takes those that arrive.  The particles of a rank stay ordered by tag.

void Particles::NrpicMpiRemoveFlagged() {
#if MPI_PARALLEL_ENABLED
  const int np = nprtcl_thispack;
  const int nranks = global_variable::nranks;
  const int gids = pmy_pack->gids;
  const int gide = gids + pmy_pack->nmb_thispack - 1;
  const int nr = nrdata, ni = nidata;
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  auto gbl = gb_lr;
  MPI_Comm comm = pbval_part->mpi_comm_part;

  // (1) escaped and excised particles; the counters are those of all ranks
  int nesc = 0, nexc = 0;
  Real mesc = 0.0, mexc = 0.0;
  if (np > 0) {
    Kokkos::parallel_reduce("nrpic_mpi_count", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, int &lnesc, int &lnexc, Real &lmesc, Real &lmexc) {
      if (pi(PGID,p) == -1) {
        lnesc += 1;
        lmesc += pr(IPM,p);
      } else if (pi(PGID,p) < -1) {
        lnexc += 1;
        lmexc += pr(IPM,p);
      }
    }, Kokkos::Sum<int>(nesc), Kokkos::Sum<int>(nexc), Kokkos::Sum<Real>(mesc),
       Kokkos::Sum<Real>(mexc));
  }
  nrpic::MpiSum({&nesc, &nexc});
  nrpic::MpiSum({&mesc, &mexc});
  n_escaped += nesc;
  n_excised += nexc;
  mass_escaped += mesc;
  mass_excised += mexc;

  // (2) particles that stay (position among them) and particles that leave
  int nkeep = 0, nleave = 0;
  DvceArray1D<int> kpos("nrpic_mpi_kpos", np);
  if (np > 0) {
    Kokkos::parallel_scan("nrpic_mpi_keep", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, int &upd, const bool final) {
      const int g = pi(PGID,p);
      const bool keep = (g >= gids && g <= gide);
      if (final) { kpos(p) = keep ? upd : -1; }
      if (keep) { upd += 1; }
    }, nkeep);
    Kokkos::parallel_reduce("nrpic_mpi_nleave", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, int &ln) {
      const int g = pi(PGID,p);
      if (g >= 0 && (g < gids || g > gide)) { ln += 1; }
    }, Kokkos::Sum<int>(nleave));
  }

  mpi_nmoved += nleave;

  // (3) records of the leaving particles, by destination rank (and by tag within it)
  std::vector<int> scnt(nranks, 0), rcnt;
  std::vector<Real> rsend, rrecv;
  std::vector<int> isend, irecv;
  if (nleave > 0) {
    DvceArray1D<int> lv("nrpic_mpi_lv", nleave), ld("nrpic_mpi_ld", nleave);
    int ntot = 0;
    Kokkos::parallel_scan("nrpic_mpi_leave", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, int &upd, const bool final) {
      const int g = pi(PGID,p);
      if (g >= 0 && (g < gids || g > gide)) {
        if (final) {
          lv(upd) = p;
          ld(upd) = gbl(g,1);
        }
        upd += 1;
      }
    }, ntot);
    auto lvh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), lv);
    auto ldh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), ld);
    std::vector<int> start(nranks + 1, 0);
    for (int n=0; n<nleave; ++n) { scnt[ldh(n)] += 1; }
    for (int r=0; r<nranks; ++r) { start[r+1] = start[r] + scnt[r]; }
    DvceArray1D<int> ord("nrpic_mpi_ord", nleave);
    auto ordh = Kokkos::create_mirror_view(ord);
    {
      std::vector<int> fill(start.begin(), start.end() - 1);
      for (int n=0; n<nleave; ++n) { ordh(fill[ldh(n)]++) = lvh(n); }
    }
    Kokkos::deep_copy(ord, ordh);
    DvceArray1D<Real> sbr("nrpic_mpi_sbr", static_cast<size_t>(nr)*nleave);
    DvceArray1D<int> sbi("nrpic_mpi_sbi", static_cast<size_t>(ni)*nleave);
    par_for("nrpic_mpi_pack", DevExeSpace(), 0, nleave-1, KOKKOS_LAMBDA(const int n) {
      const int p = ord(n);
      for (int i=0; i<nr; ++i) { sbr(nr*n + i) = pr(i,p); }
      for (int i=0; i<ni; ++i) { sbi(ni*n + i) = pi(i,p); }
    });
    auto sbrh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), sbr);
    auto sbih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), sbi);
    rsend.assign(sbrh.data(), sbrh.data() + sbrh.size());
    isend.assign(sbih.data(), sbih.data() + sbih.size());
  }
  std::vector<int> rcnt2;
  ExchangeRecords<Real>(comm, MPI_ATHENA_REAL, nr, 0, scnt, rsend, rcnt, rrecv);
  ExchangeRecords<int>(comm, MPI_INT, ni, 1, scnt, isend, rcnt2, irecv);
  int nrecv = 0;
  for (int r=0; r<nranks; ++r) { nrecv += rcnt[r]; }

  // (4) new arrays: the particles that stay and those that arrived, ordered by tag
  const int nnew = nkeep + nrecv;
  if (!(nkeep == np && nrecv == 0)) {
    DvceArray2D<Real> rnew("prtcl_rdata", nr, nnew);
    DvceArray2D<int>  inew("prtcl_idata", ni, nnew);
    // is the sequence of the staying particles ascending in the tag?
    int nbad = 0;
    DvceArray1D<int> ktag("nrpic_mpi_ktag", nkeep);
    if (nkeep > 0) {
      par_for("nrpic_mpi_ktag", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
        if (kpos(p) >= 0) { ktag(kpos(p)) = pi(PTAG,p); }
      });
      if (nkeep > 1) {
        Kokkos::parallel_reduce("nrpic_mpi_order",
                                Kokkos::RangePolicy<DevExeSpace>(1, nkeep),
        KOKKOS_LAMBDA(const int k, int &lb) {
          if (ktag(k) <= ktag(k-1)) { lb += 1; }
        }, Kokkos::Sum<int>(nbad));
      }
    }
    if (nbad == 0) {
      // received records in the order of their tags
      std::vector<int> rord(nrecv);
      std::iota(rord.begin(), rord.end(), 0);
      std::sort(rord.begin(), rord.end(), [&](const int a, const int b) {
        return irecv[static_cast<size_t>(ni)*a + PTAG] <
               irecv[static_cast<size_t>(ni)*b + PTAG];
      });
      DvceArray1D<int> rtag("nrpic_mpi_rtag", nrecv);
      DvceArray1D<Real> rbr("nrpic_mpi_rbr", static_cast<size_t>(nr)*nrecv);
      DvceArray1D<int> rbi("nrpic_mpi_rbi", static_cast<size_t>(ni)*nrecv);
      if (nrecv > 0) {
        auto rtagh = Kokkos::create_mirror_view(rtag);
        auto rbrh = Kokkos::create_mirror_view(rbr);
        auto rbih = Kokkos::create_mirror_view(rbi);
        for (int j=0; j<nrecv; ++j) {
          const size_t s = static_cast<size_t>(rord[j]);
          rtagh(j) = irecv[ni*s + PTAG];
          const size_t jr = static_cast<size_t>(nr)*j, ji = static_cast<size_t>(ni)*j;
          for (int i=0; i<nr; ++i) { rbrh(jr + i) = rrecv[nr*s + i]; }
          for (int i=0; i<ni; ++i) { rbih(ji + i) = irecv[ni*s + i]; }
        }
        Kokkos::deep_copy(rtag, rtagh);
        Kokkos::deep_copy(rbr, rbrh);
        Kokkos::deep_copy(rbi, rbih);
      }
      if (np > 0) {
        par_for("nrpic_mpi_stay", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
          const int k = kpos(p);
          if (k < 0) return;
          const int q = k + LowerBound(rtag, nrecv, pi(PTAG,p));
          for (int i=0; i<nr; ++i) { rnew(i,q) = pr(i,p); }
          for (int i=0; i<ni; ++i) { inew(i,q) = pi(i,p); }
        });
      }
      if (nrecv > 0) {
        par_for("nrpic_mpi_arrive", DevExeSpace(), 0, nrecv-1,
        KOKKOS_LAMBDA(const int j) {
          const int q = j + LowerBound(ktag, nkeep, rtag(j));
          for (int i=0; i<nr; ++i) { rnew(i,q) = rbr(nr*j + i); }
          for (int i=0; i<ni; ++i) { inew(i,q) = rbi(ni*j + i); }
        });
      }
    } else {
      // The particles of this rank were not in the order of their tags (a particle or
      // restart file that is not): order everything on the host, once.
      auto prh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), pr);
      auto pih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), pi);
      auto kph = Kokkos::create_mirror_view_and_copy(HostMemSpace(), kpos);
      std::vector<std::pair<int,int>> key;     // (tag, source: p or np + j)
      key.reserve(nnew);
      for (int p=0; p<np; ++p) {
        if (kph(p) >= 0) { key.emplace_back(pih(PTAG,p), p); }
      }
      for (int j=0; j<nrecv; ++j) {
        key.emplace_back(irecv[static_cast<size_t>(ni)*j + PTAG], np + j);
      }
      std::sort(key.begin(), key.end());
      auto rnh = Kokkos::create_mirror_view(rnew);
      auto inh = Kokkos::create_mirror_view(inew);
      for (int q=0; q<nnew; ++q) {
        const int s = key[q].second;
        if (s < np) {
          for (int i=0; i<nr; ++i) { rnh(i,q) = prh(i,s); }
          for (int i=0; i<ni; ++i) { inh(i,q) = pih(i,s); }
        } else {
          const size_t j = static_cast<size_t>(s - np);
          for (int i=0; i<nr; ++i) { rnh(i,q) = rrecv[nr*j + i]; }
          for (int i=0; i<ni; ++i) { inh(i,q) = irecv[ni*j + i]; }
        }
      }
      Kokkos::deep_copy(rnew, rnh);
      Kokkos::deep_copy(inew, inh);
    }
    prtcl_rdata = rnew;
    prtcl_idata = inew;
    nprtcl_thispack = nnew;
  }
  NrpicMpiUpdateCounts();
#endif
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiDepositRemote
//! \brief the part of the deposit that crosses rank boundaries.  Called behind the
//! deposit kernel, which has added the cloud cells that lie in MeshBlocks of this rank
//! and has stored the Lorentz factor and the level of each cloud (dep_aux).  A cloud
//! with cells in MeshBlocks of other ranks is sent to those ranks as a packet (position,
//! lattice spacing, level, the ten amounts); the clouds received are added here with
//! the same weights, restricted again to the MeshBlocks of this rank.  Every cloud cell
//! is thus added once, by the rank that holds its leaf cell.

void Particles::NrpicMpiDepositRemote() {
#if MPI_PARALLEL_ENABLED
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  auto tm = pmy_pack->ptmunu->u_tmunu;
  const int np = nprtcl_thispack;
  const int nranks = global_variable::nranks;
  const int myrank = global_variable::my_rank;
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  auto lev = pmy_pack->pmb->mb_lev.d_view;
  const int gids = pmy_pack->gids;
  const int nmb = pmy_pack->nmb_thispack;
  auto gbx = gb_ext;
  auto gbl = gb_lr;
  const int gnmb = gb_nmb;
  auto daux = dep_aux;
  const Real gmin[3] = {pm->mesh_size.x1min, pm->mesh_size.x2min, pm->mesh_size.x3min};
  const bool newton = nropt.newton;
  nrpic::CloudGeometry cg;
  cg.nb = nropt.deposit_shape + 1;
  cg.is = indcs.is; cg.js = indcs.js; cg.ks = indcs.ks;
  cg.ie = indcs.ie; cg.je = indcs.je; cg.ke = indcs.ke;
  for (int d=0; d<3; ++d) {
    cg.dmin[d] = nropt.dom_min[d];
    cg.dlen[d] = nropt.dom_len[d];
    cg.per[d] = nropt.periodic[d];
  }
  MPI_Comm comm = pbval_part->mpi_comm_part;

  // (1) number of ranks each cloud reaches, and where its packets go in the list
  int npk = 0;
  DvceArray1D<int> poff("nrpic_mpi_poff", np + 1);
  if (np > 0) {
    Kokkos::parallel_scan("nrpic_mpi_cloudranks", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, int &upd, const bool final) {
      int n = 0;
      if (pr(IPM,p) > 0.0) {
        const int mo = pi(PGID,p) - gids;
        const Real xp[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
        Real h[3] = {sz(mo).dx1, sz(mo).dx2, sz(mo).dx3};
        CloudSpacing(static_cast<int>(daux(1,p)), h);
        int rk[kMaxCloudRanks];
        n = CloudRanks(cg, sz, nmb, mo, gbx, gbl, gnmb, myrank, xp, gmin, h, rk);
      }
      if (final) { poff(p) = upd; }
      upd += n;
    }, npk);
  }

  mpi_npacket += npk;

  // (2) the packets, then ordered by destination rank on the host
  std::vector<int> scnt(nranks, 0), rcnt;
  std::vector<Real> sbuf, rbuf;
  if (npk > 0) {
    DvceArray1D<int> prank("nrpic_mpi_prank", npk);
    DvceArray1D<Real> pdat("nrpic_mpi_pdat", static_cast<size_t>(kPacket)*npk);
    par_for("nrpic_mpi_packets", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
      const Real mp = pr(IPM,p);
      if (!(mp > 0.0)) return;
      const int mo = pi(PGID,p) - gids;
      const Real xp[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
      const Real up[3] = {pr(IPVX,p), pr(IPVY,p), pr(IPVZ,p)};
      Real h[3] = {sz(mo).dx1, sz(mo).dx2, sz(mo).dx3};
      const int ls = static_cast<int>(daux(1,p));
      CloudSpacing(ls, h);
      int rk[kMaxCloudRanks];
      const int n = CloudRanks(cg, sz, nmb, mo, gbx, gbl, gnmb, myrank, xp, gmin, h, rk);
      if (n == 0) return;
      // the amounts of the deposit kernel, with the Lorentz factor it computed
      const Real wrel = daux(0,p);
      const Real W = newton ? 1.0 : wrel;
      Real q[Tmunu::N_Tmunu];
      q[Tmunu::I_Tmunu_Sxx] = mp*up[0]*up[0]/W;
      q[Tmunu::I_Tmunu_Sxy] = mp*up[0]*up[1]/W;
      q[Tmunu::I_Tmunu_Sxz] = mp*up[0]*up[2]/W;
      q[Tmunu::I_Tmunu_Syy] = mp*up[1]*up[1]/W;
      q[Tmunu::I_Tmunu_Syz] = mp*up[1]*up[2]/W;
      q[Tmunu::I_Tmunu_Szz] = mp*up[2]*up[2]/W;
      q[Tmunu::I_Tmunu_E]   = mp*W;
      q[Tmunu::I_Tmunu_Sx]  = mp*up[0];
      q[Tmunu::I_Tmunu_Sy]  = mp*up[1];
      q[Tmunu::I_Tmunu_Sz]  = mp*up[2];
      for (int s=0; s<n; ++s) {
        const size_t o = static_cast<size_t>(kPacket)*(poff(p) + s);
        prank(poff(p) + s) = rk[s];
        pdat(o+0) = xp[0]; pdat(o+1) = xp[1]; pdat(o+2) = xp[2];
        pdat(o+3) = h[0];  pdat(o+4) = h[1];  pdat(o+5) = h[2];
        pdat(o+6) = static_cast<Real>(lev(mo) + ls);
        for (int v=0; v<Tmunu::N_Tmunu; ++v) { pdat(o+7+v) = q[v]; }
      }
    });
    auto prh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prank);
    auto pdh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), pdat);
    std::vector<int> start(nranks + 1, 0);
    for (int n=0; n<npk; ++n) { scnt[prh(n)] += 1; }
    for (int r=0; r<nranks; ++r) { start[r+1] = start[r] + scnt[r]; }
    sbuf.resize(static_cast<size_t>(kPacket)*npk);
    std::vector<int> fill(start.begin(), start.end() - 1);
    for (int n=0; n<npk; ++n) {
      const size_t dst = static_cast<size_t>(kPacket)*(fill[prh(n)]++);
      const size_t src = static_cast<size_t>(kPacket)*n;
      for (int v=0; v<kPacket; ++v) { sbuf[dst+v] = pdh(src+v); }
    }
  }
  ExchangeRecords<Real>(comm, MPI_ATHENA_REAL, kPacket, 2, scnt, sbuf, rcnt, rbuf);
  const int nrcv = static_cast<int>(rbuf.size()/kPacket);

  // (3) the clouds of other ranks on the MeshBlocks of this rank
  if (nrcv > 0) {
    DvceArray1D<Real> rdat("nrpic_mpi_rdat", rbuf.size());
    auto rdh = Kokkos::create_mirror_view(rdat);
    std::memcpy(rdh.data(), rbuf.data(), rbuf.size()*sizeof(Real));
    Kokkos::deep_copy(rdat, rdh);
    par_for("nrpic_mpi_deposit", DevExeSpace(), 0, nrcv-1, KOKKOS_LAMBDA(const int n) {
      const size_t o = static_cast<size_t>(kPacket)*n;
      const Real xp[3] = {rdat(o+0), rdat(o+1), rdat(o+2)};
      const Real h[3] = {rdat(o+3), rdat(o+4), rdat(o+5)};
      const int ldep = static_cast<int>(rdat(o+6));
      Real q[Tmunu::N_Tmunu];
      for (int v=0; v<Tmunu::N_Tmunu; ++v) { q[v] = rdat(o+7+v); }
      Real xb[3], wt[3][4];
      nrpic::CloudWeights(cg.nb, xp, gmin, h, xb, wt);
      nrpic::CloudDeposit(cg, sz, lev, nmb, -1, xb, wt, h, ldep, q, tm);
    });
  }
  // the particle sum of m W of all ranks
  nrpic::MpiSum({&sum_mw});
#endif
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiProbe
//! \brief the sums of NrpicProbe on several ranks: each rank evaluates the cells it
//! holds of the eight around the probe, the values are collected (a cell belongs to one
//! rank) and added in the order of the one-rank loop

void Particles::NrpicMpiProbe(const Real px, const Real py, const Real pz, Real &sa,
                              Real &se, Real &sw) {
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int nmb = pmy_pack->nmb_thispack;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
  const int nx1 = indcs.nx1, nx2 = indcs.nx2, nx3 = indcs.nx3;
  const Real gmin[3] = {pm->mesh_size.x1min, pm->mesh_size.x2min, pm->mesh_size.x3min};
  const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3] = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
  auto m1 = met1;
  const bool has_tm = nropt.deposit;
  DvceArray5D<Real> tm;
  if (has_tm) { tm = pmy_pack->ptmunu->u_tmunu; }
  auto gbx = gb_ext;
  const int gnmb = gb_nmb;
  DvceArray1D<Real> val("nrpic_mpi_probe", 24);
  par_for("nrpic_mpi_probe", DevExeSpace(), 0, 7, KOKKOS_LAMBDA(const int c) {
    // cell sizes of the MeshBlock that contains the probe, on whatever rank
    const int g = nrpic::FindBlockGlobal(gbx, gnmb, px, py, pz);
    if (g < 0) return;
    const Real h[3] = {(gbx(g,1) - gbx(g,0))/static_cast<Real>(nx1),
                       (gbx(g,3) - gbx(g,2))/static_cast<Real>(nx2),
                       (gbx(g,5) - gbx(g,4))/static_cast<Real>(nx3)};
    const Real xp[3] = {px, py, pz};
    Real xb[3], s[3];
    for (int d=0; d<3; ++d) {
      Real xi = (xp[d] - gmin[d])/h[d] - 0.5;
      Real fl = floor(xi);
      s[d] = xi - fl;
      xb[d] = gmin[d] + (fl + 0.5)*h[d];
    }
    const Real xf = nrpic::WrapCoord(xb[0] + ((c & 1) ? h[0] : 0.0),
                                     dmin[0], dlen[0], per[0]);
    const Real yf = nrpic::WrapCoord(xb[1] + ((c & 2) ? h[1] : 0.0),
                                     dmin[1], dlen[1], per[1]);
    const Real zf = nrpic::WrapCoord(xb[2] + ((c & 4) ? h[2] : 0.0),
                                     dmin[2], dlen[2], per[2]);
    const Real w = ((c & 1) ? s[0] : 1.0 - s[0])*((c & 2) ? s[1] : 1.0 - s[1])
                  *((c & 4) ? s[2] : 1.0 - s[2]);
    const int mb = nrpic::FindBlock(sz, nmb, 0, xf, yf, zf);
    if (mb < 0) return;
    int i = is + static_cast<int>(floor((xf - sz(mb).x1min)/sz(mb).dx1));
    int j = js + static_cast<int>(floor((yf - sz(mb).x2min)/sz(mb).dx2));
    int k = ks + static_cast<int>(floor((zf - sz(mb).x3min)/sz(mb).dx3));
    i = (i < is) ? is : ((i > ie) ? ie : i);
    j = (j < js) ? js : ((j > je) ? je : j);
    k = (k < ks) ? ks : ((k > ke) ? ke : k);
    val(3*c) = w;
    val(3*c+1) = m1(mb,NRM_ALP,k,j,i);
    val(3*c+2) = has_tm ? tm(mb,Tmunu::I_Tmunu_E,k,j,i) : 0.0;
  });
  auto vh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), val);
  Real v[24];
  for (int n=0; n<24; ++n) { v[n] = vh(n); }
  nrpic::MpiSumArray(v, 24);
  Real la = 0.0, le = 0.0, lw = 0.0;
  for (int c=0; c<8; ++c) {
    const Real w = v[3*c];
    la += w*v[3*c+1];
    if (has_tm) { le += w*v[3*c+2]; }
    lw += w;
  }
  sa = la; se = le; sw = lw;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiTrajSources
//! \brief the deposited E and S_i at the tracked particles (trajectory record) on
//! several ranks.  The kernel of NrpicWriteTrajectories has summed the cells of the
//! eight around each particle that this rank holds, without dividing by the sum of the
//! weights (rows NRM_NVAR+1..4 of pmet, weights in row NRM_NVAR+5).  Here the cells that
//! other ranks hold are asked for, added, and the sums divided.  A rank without
//! particles calls this with an empty array and only answers.

void Particles::NrpicMpiTrajSources(DvceArray2D<Real> &pmet) {
#if MPI_PARALLEL_ENABLED
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  const int np = (pmet.extent(0) == 0) ? 0 : nprtcl_thispack;
  const int nranks = global_variable::nranks;
  const int myrank = global_variable::my_rank;
  auto pr = prtcl_rdata;
  auto pi = prtcl_idata;
  auto sz = pmy_pack->pmb->mb_size.d_view;
  const int gids = pmy_pack->gids;
  const int nmb = pmy_pack->nmb_thispack;
  const int is = indcs.is, js = indcs.js, ks = indcs.ks;
  const int ie = indcs.ie, je = indcs.je, ke = indcs.ke;
  const int ntrack = nropt.traj_ntrack;
  auto gbx = gb_ext;
  auto gbl = gb_lr;
  const int gnmb = gb_nmb;
  auto tm = pmy_pack->ptmunu->u_tmunu;
  const Real gmin[3] = {pm->mesh_size.x1min, pm->mesh_size.x2min, pm->mesh_size.x3min};
  const Real dmin[3] = {nropt.dom_min[0], nropt.dom_min[1], nropt.dom_min[2]};
  const Real dlen[3] = {nropt.dom_len[0], nropt.dom_len[1], nropt.dom_len[2]};
  const bool per[3] = {nropt.periodic[0], nropt.periodic[1], nropt.periodic[2]};
  MPI_Comm comm = pbval_part->mpi_comm_part;
  auto pm_ = pmet;

  // (1) cells of the eight around a tracked particle that another rank holds
  int nreq = 0;
  DvceArray1D<int> roff("nrpic_mpi_roff", np + 1);
  if (np > 0) {
    Kokkos::parallel_scan("nrpic_mpi_trajcount", Kokkos::RangePolicy<DevExeSpace>(0, np),
    KOKKOS_LAMBDA(const int p, int &upd, const bool final) {
      int n = 0;
      if (pi(PTAG,p) < ntrack) {
        const int m = pi(PGID,p) - gids;
        const Real h[3] = {sz(m).dx1, sz(m).dx2, sz(m).dx3};
        const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
        Real xb[3];
        for (int d=0; d<3; ++d) {
          Real xi = (x[d] - gmin[d])/h[d] - 0.5;
          xb[d] = gmin[d] + (floor(xi) + 0.5)*h[d];
        }
        for (int c=0; c<8; ++c) {
          const Real xf = nrpic::WrapCoord(xb[0] + ((c & 1) ? h[0] : 0.0),
                                           dmin[0], dlen[0], per[0]);
          const Real yf = nrpic::WrapCoord(xb[1] + ((c & 2) ? h[1] : 0.0),
                                           dmin[1], dlen[1], per[1]);
          const Real zf = nrpic::WrapCoord(xb[2] + ((c & 4) ? h[2] : 0.0),
                                           dmin[2], dlen[2], per[2]);
          if (nrpic::FindBlock(sz, nmb, m, xf, yf, zf) >= 0) continue;
          const int g = nrpic::FindBlockGlobal(gbx, gnmb, xf, yf, zf);
          if (g >= 0 && gbl(g,1) != myrank) { n += 1; }
        }
      }
      if (final) { roff(p) = upd; }
      upd += n;
    }, nreq);
  }

  // (2) requests (position of the cell, 8 x particle + corner), by rank
  std::vector<int> scnt(nranks, 0), rcnt, rcnt2;
  std::vector<Real> sbuf, rbuf, abuf, rep;
  if (nreq > 0) {
    DvceArray1D<int> qrank("nrpic_mpi_qrank", nreq);
    DvceArray1D<Real> qdat("nrpic_mpi_qdat", static_cast<size_t>(4)*nreq);
    par_for("nrpic_mpi_trajreq", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
      if (pi(PTAG,p) >= ntrack) return;
      const int m = pi(PGID,p) - gids;
      const Real h[3] = {sz(m).dx1, sz(m).dx2, sz(m).dx3};
      const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
      Real xb[3];
      for (int d=0; d<3; ++d) {
        Real xi = (x[d] - gmin[d])/h[d] - 0.5;
        xb[d] = gmin[d] + (floor(xi) + 0.5)*h[d];
      }
      int n = 0;
      for (int c=0; c<8; ++c) {
        const Real xf = nrpic::WrapCoord(xb[0] + ((c & 1) ? h[0] : 0.0),
                                         dmin[0], dlen[0], per[0]);
        const Real yf = nrpic::WrapCoord(xb[1] + ((c & 2) ? h[1] : 0.0),
                                         dmin[1], dlen[1], per[1]);
        const Real zf = nrpic::WrapCoord(xb[2] + ((c & 4) ? h[2] : 0.0),
                                         dmin[2], dlen[2], per[2]);
        if (nrpic::FindBlock(sz, nmb, m, xf, yf, zf) >= 0) continue;
        const int g = nrpic::FindBlockGlobal(gbx, gnmb, xf, yf, zf);
        if (g < 0 || gbl(g,1) == myrank) continue;
        const size_t o = static_cast<size_t>(4)*(roff(p) + n);
        qrank(roff(p) + n) = gbl(g,1);
        qdat(o) = xf; qdat(o+1) = yf; qdat(o+2) = zf;
        qdat(o+3) = static_cast<Real>(8)*static_cast<Real>(p) + static_cast<Real>(c);
        n += 1;
      }
    });
    auto qrh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), qrank);
    auto qdh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), qdat);
    std::vector<int> start(nranks + 1, 0);
    for (int n=0; n<nreq; ++n) { scnt[qrh(n)] += 1; }
    for (int r=0; r<nranks; ++r) { start[r+1] = start[r] + scnt[r]; }
    sbuf.resize(static_cast<size_t>(4)*nreq);
    std::vector<int> fill(start.begin(), start.end() - 1);
    for (int n=0; n<nreq; ++n) {
      const size_t dst = static_cast<size_t>(4)*(fill[qrh(n)]++);
      for (int v=0; v<4; ++v) { sbuf[dst+v] = qdh(static_cast<size_t>(4)*n + v); }
    }
  }
  ExchangeRecords<Real>(comm, MPI_ATHENA_REAL, 4, 8, scnt, sbuf, rcnt, rbuf);

  // (3) answers: the label and E, S_i of the leaf cell that contains the position
  const int nans = static_cast<int>(rbuf.size()/4);
  abuf.resize(static_cast<size_t>(5)*nans);
  if (nans > 0) {
    DvceArray1D<Real> rq("nrpic_mpi_rq", rbuf.size());
    DvceArray1D<Real> an("nrpic_mpi_an", abuf.size());
    auto rqh = Kokkos::create_mirror_view(rq);
    std::memcpy(rqh.data(), rbuf.data(), rbuf.size()*sizeof(Real));
    Kokkos::deep_copy(rq, rqh);
    par_for("nrpic_mpi_trajans", DevExeSpace(), 0, nans-1,
    KOKKOS_LAMBDA(const int n) {
      const size_t o = static_cast<size_t>(4)*n, a = static_cast<size_t>(5)*n;
      const Real xf = rq(o), yf = rq(o+1), zf = rq(o+2);
      const int mb = nrpic::FindBlock(sz, nmb, 0, xf, yf, zf);
      if (mb < 0) {                 // not here after all: marked, and skipped by the asker
        an(a) = -1.0;
        an(a+1) = 0.0; an(a+2) = 0.0; an(a+3) = 0.0; an(a+4) = 0.0;
        return;
      }
      int i = is + static_cast<int>(floor((xf - sz(mb).x1min)/sz(mb).dx1));
      int j = js + static_cast<int>(floor((yf - sz(mb).x2min)/sz(mb).dx2));
      int k = ks + static_cast<int>(floor((zf - sz(mb).x3min)/sz(mb).dx3));
      i = (i < is) ? is : ((i > ie) ? ie : i);
      j = (j < js) ? js : ((j > je) ? je : j);
      k = (k < ks) ? ks : ((k > ke) ? ke : k);
      an(a) = rq(o+3);
      an(a+1) = tm(mb,Tmunu::I_Tmunu_E,k,j,i);
      an(a+2) = tm(mb,Tmunu::I_Tmunu_Sx,k,j,i);
      an(a+3) = tm(mb,Tmunu::I_Tmunu_Sy,k,j,i);
      an(a+4) = tm(mb,Tmunu::I_Tmunu_Sz,k,j,i);
    });
    auto anh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), an);
    std::memcpy(abuf.data(), anh.data(), abuf.size()*sizeof(Real));
  }
  ExchangeRecords<Real>(comm, MPI_ATHENA_REAL, 5, 9, rcnt, abuf, rcnt2, rep);

  // (4) add the cells of the other ranks, then divide by the sum of the weights
  const int nrep = static_cast<int>(rep.size()/5);
  if (nrep > 0) {
    DvceArray1D<Real> rp("nrpic_mpi_rp", rep.size());
    auto rph = Kokkos::create_mirror_view(rp);
    std::memcpy(rph.data(), rep.data(), rep.size()*sizeof(Real));
    Kokkos::deep_copy(rp, rph);
    par_for("nrpic_mpi_trajadd", DevExeSpace(), 0, nrep-1, KOKKOS_LAMBDA(const int n) {
      const size_t a = static_cast<size_t>(5)*n;
      if (rp(a) < 0.0) return;
      const std::int64_t id = static_cast<std::int64_t>(rp(a));
      const int p = static_cast<int>(id/8), c = static_cast<int>(id % 8);
      const int m = pi(PGID,p) - gids;
      const Real h[3] = {sz(m).dx1, sz(m).dx2, sz(m).dx3};
      const Real x[3] = {pr(IPX,p), pr(IPY,p), pr(IPZ,p)};
      Real s[3];
      for (int d=0; d<3; ++d) {
        Real xi = (x[d] - gmin[d])/h[d] - 0.5;
        s[d] = xi - floor(xi);
      }
      const Real w = ((c & 1) ? s[0] : 1.0 - s[0])*((c & 2) ? s[1] : 1.0 - s[1])
                    *((c & 4) ? s[2] : 1.0 - s[2]);
      Kokkos::atomic_add(&pm_(NRM_NVAR+1,p), w*rp(a+1));
      Kokkos::atomic_add(&pm_(NRM_NVAR+2,p), w*rp(a+2));
      Kokkos::atomic_add(&pm_(NRM_NVAR+3,p), w*rp(a+3));
      Kokkos::atomic_add(&pm_(NRM_NVAR+4,p), w*rp(a+4));
      Kokkos::atomic_add(&pm_(NRM_NVAR+5,p), w);
    });
  }
  if (np > 0) {
    par_for("nrpic_mpi_trajnorm", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
      if (pi(PTAG,p) >= ntrack) return;
      const Real sw = pm_(NRM_NVAR+5,p);
      const Real isw = (sw > 0.0) ? 1.0/sw : 0.0;
      pm_(NRM_NVAR+1,p) *= isw;
      pm_(NRM_NVAR+2,p) *= isw;
      pm_(NRM_NVAR+3,p) *= isw;
      pm_(NRM_NVAR+4,p) *= isw;
    });
  }
#endif
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiWriteHistory
//! \brief appends one record to <basename>.mpi.hst (runs on several ranks only): the
//! particles handed between ranks and the deposit packets sent since the last record,
//! summed over the ranks, and the number of particles on each rank

void Particles::NrpicMpiWriteHistory(Real time, int ncycle, bool header) {
#if MPI_PARALLEL_ENABLED
  Mesh *pm = pmy_pack->pmesh;
  std::int64_t cnt[2] = {mpi_nmoved, mpi_npacket};
  MPI_Allreduce(MPI_IN_PLACE, cnt, 2, MPI_INT64_T, MPI_SUM, MPI_COMM_WORLD);
  mpi_nmoved = 0;
  mpi_npacket = 0;
  if (global_variable::my_rank != 0) return;
  std::string fname = nr_basename + ".mpi.hst";
  std::FILE *fp = std::fopen(fname.c_str(), header ? "w" : "a");
  if (fp == nullptr) MpiFatal("cannot open " + fname);
  if (header) {
    std::fprintf(fp, "# NRPIC on %d MPI ranks\n", global_variable::nranks);
    std::fprintf(fp, "# [1]=time [2]=ncycle [3]=particles_handed_over [4]=deposit_packets"
                 " [5..]=particles on rank 0, 1, ...\n");
  }
  std::fprintf(fp, "%.15e %d %lld %lld", time, ncycle, static_cast<long long>(cnt[0]),
               static_cast<long long>(cnt[1]));
  for (int r=0; r<global_variable::nranks; ++r) {
    std::fprintf(fp, " %d", pm->nprtcl_eachrank[r]);
  }
  std::fprintf(fp, "\n");
  std::fclose(fp);
#endif
}

//----------------------------------------------------------------------------------------
//! \fn  bool Particles::NrpicMpiGatherBegin
//! \brief for the duration of a file write on several ranks, the particle arrays of
//! rank 0 hold the particles of all ranks in the order of their tags.  Returns true on
//! the rank that writes the file (always on one rank).  NrpicMpiGatherEnd puts the
//! arrays of rank 0 back.

bool Particles::NrpicMpiGatherBegin() {
  if (!nr_multirank) return true;
#if MPI_PARALLEL_ENABLED
  const int np = nprtcl_thispack;
  const int nranks = global_variable::nranks;
  const int nr = nrdata, ni = nidata;
  MPI_Comm comm = pbval_part->mpi_comm_part;
  // records of this rank on the host
  std::vector<Real> rb(static_cast<size_t>(nr)*np);
  std::vector<int> ib(static_cast<size_t>(ni)*np);
  if (np > 0) {
    auto rh = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_rdata);
    auto ih = Kokkos::create_mirror_view_and_copy(HostMemSpace(), prtcl_idata);
    for (int p=0; p<np; ++p) {
      for (int i=0; i<nr; ++i) { rb[static_cast<size_t>(nr)*p + i] = rh(i,p); }
      for (int i=0; i<ni; ++i) { ib[static_cast<size_t>(ni)*p + i] = ih(i,p); }
    }
  }
  std::vector<int> cnt(nranks, 0);
  int mynp = np;
  MPI_Gather(&mynp, 1, MPI_INT, cnt.data(), 1, MPI_INT, 0, comm);
  if (global_variable::my_rank != 0) {
    if (np > 0) {
      if (static_cast<std::int64_t>(nr)*np > INT_MAX) {
        MpiFatal("too many particles on one rank for one message");
      }
      MPI_Send(rb.data(), nr*np, MPI_ATHENA_REAL, 0, 3, comm);
      MPI_Send(ib.data(), ni*np, MPI_INT, 0, 4, comm);
    }
    return false;
  }
  std::int64_t ntot64 = 0;
  for (int r=0; r<nranks; ++r) { ntot64 += cnt[r]; }
  if (ntot64 > INT_MAX) { MpiFatal("more than 2^31 particles"); }
  const int ntot = static_cast<int>(ntot64);
  rb.resize(static_cast<size_t>(nr)*ntot);
  ib.resize(static_cast<size_t>(ni)*ntot);
  size_t off = static_cast<size_t>(np);
  for (int r=1; r<nranks; ++r) {
    if (cnt[r] == 0) continue;
    MPI_Recv(rb.data() + nr*off, nr*cnt[r], MPI_ATHENA_REAL, r, 3, comm,
             MPI_STATUS_IGNORE);
    MPI_Recv(ib.data() + ni*off, ni*cnt[r], MPI_INT, r, 4, comm, MPI_STATUS_IGNORE);
    off += static_cast<size_t>(cnt[r]);
  }
  std::vector<int> ord(ntot);
  std::iota(ord.begin(), ord.end(), 0);
  std::stable_sort(ord.begin(), ord.end(), [&](const int a, const int b) {
    return ib[static_cast<size_t>(ni)*a + PTAG] < ib[static_cast<size_t>(ni)*b + PTAG];
  });
  DvceArray2D<Real> gr("prtcl_rdata_all", nr, ntot);
  DvceArray2D<int>  gi("prtcl_idata_all", ni, ntot);
  auto grh = Kokkos::create_mirror_view(gr);
  auto gih = Kokkos::create_mirror_view(gi);
  for (int q=0; q<ntot; ++q) {
    const size_t s = static_cast<size_t>(ord[q]);
    for (int i=0; i<nr; ++i) { grh(i,q) = rb[nr*s + i]; }
    for (int i=0; i<ni; ++i) { gih(i,q) = ib[ni*s + i]; }
  }
  Kokkos::deep_copy(gr, grh);
  Kokkos::deep_copy(gi, gih);
  mpi_save_r = prtcl_rdata;
  mpi_save_i = prtcl_idata;
  mpi_save_np = nprtcl_thispack;
  prtcl_rdata = gr;
  prtcl_idata = gi;
  nprtcl_thispack = ntot;
#endif
  return true;
}

void Particles::NrpicMpiGatherEnd() {
  if (!nr_multirank || mpi_save_np < 0) return;
  prtcl_rdata = mpi_save_r;
  prtcl_idata = mpi_save_i;
  nprtcl_thispack = mpi_save_np;
  mpi_save_r = DvceArray2D<Real>();
  mpi_save_i = DvceArray2D<int>();
  mpi_save_np = -1;
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiGatherRecords
//! \brief collects records of nrec doubles from all ranks on rank 0, ordered by the tag
//! in their second entry; the list of every other rank is emptied.  Nothing on one rank.

void Particles::NrpicMpiGatherRecords(std::vector<double> &buf, const int nrec) {
  if (!nr_multirank) return;
#if MPI_PARALLEL_ENABLED
  const int nranks = global_variable::nranks;
  MPI_Comm comm = pbval_part->mpi_comm_part;
  if (buf.size() > static_cast<size_t>(INT_MAX)) { MpiFatal("record list too long"); }
  int n = static_cast<int>(buf.size());
  std::vector<int> cnt(nranks, 0);
  MPI_Gather(&n, 1, MPI_INT, cnt.data(), 1, MPI_INT, 0, comm);
  if (global_variable::my_rank != 0) {
    if (n > 0) { MPI_Send(buf.data(), n, MPI_DOUBLE, 0, 5, comm); }
    buf.clear();
    return;
  }
  size_t ntot = 0;
  for (int r=0; r<nranks; ++r) { ntot += static_cast<size_t>(cnt[r]); }
  std::vector<double> all(ntot);
  std::memcpy(all.data(), buf.data(), buf.size()*sizeof(double));
  size_t off = buf.size();
  for (int r=1; r<nranks; ++r) {
    if (cnt[r] == 0) continue;
    MPI_Recv(all.data() + off, cnt[r], MPI_DOUBLE, r, 5, comm, MPI_STATUS_IGNORE);
    off += static_cast<size_t>(cnt[r]);
  }
  const size_t nrecs = ntot/nrec;
  std::vector<size_t> ord(nrecs);
  std::iota(ord.begin(), ord.end(), static_cast<size_t>(0));
  std::stable_sort(ord.begin(), ord.end(), [&](const size_t a, const size_t b) {
    return all[a*nrec + 1] < all[b*nrec + 1];
  });
  buf.resize(ntot);
  for (size_t q=0; q<nrecs; ++q) {
    std::memcpy(buf.data() + q*nrec, all.data() + ord[q]*nrec, nrec*sizeof(double));
  }
#endif
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiWriteStepSources
//! \brief the source densities of the coming step (source_extrap) in the particle
//! restart file of a run on several ranks: five int64 (number of MeshBlocks of the mesh,
//! components, cells per direction with ghost cells), then the arrays of all MeshBlocks
//! in the order of their global IDs.  Rank 0 writes (fp), the other ranks send (fp is
//! null).  The file of a one-rank run has the same layout with the number of MeshBlock
//! slots of that run in the first place.

void Particles::NrpicMpiWriteStepSources(std::FILE *fp) {
#if MPI_PARALLEL_ENABLED
  if (!(nropt.deposit && nropt.source_density && nropt.source_extrap &&
        pmy_pack->ptmunu != nullptr && pmy_pack->ptmunu->step_density && tm_prev_valid)) {
    return;
  }
  Mesh *pm = pmy_pack->pmesh;
  MPI_Comm comm = pbval_part->mpi_comm_part;
  auto tsh = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(),
                                                 pmy_pack->ptmunu->u_tmunu_step);
  const size_t bs = tsh.extent(1)*tsh.extent(2)*tsh.extent(3)*tsh.extent(4);
  if (bs > static_cast<size_t>(INT_MAX)) {
    MpiFatal("MeshBlock too large for a message");
  }
  const int nmb = pmy_pack->nmb_thispack;
  if (global_variable::my_rank != 0) {
    for (int m=0; m<nmb; ++m) {
      MPI_Send(tsh.data() + m*bs, static_cast<int>(bs), MPI_DOUBLE, 0, 6, comm);
    }
    return;
  }
  std::int64_t dims[5];
  for (int d=0; d<5; ++d) { dims[d] = static_cast<std::int64_t>(tsh.extent(d)); }
  dims[0] = pm->nmb_total;
  std::fwrite(dims, sizeof(std::int64_t), 5, fp);
  std::fwrite(tsh.data(), sizeof(double), bs*nmb, fp);
  std::vector<double> blk(bs);
  for (int r=1; r<global_variable::nranks; ++r) {
    for (int m=0; m<pm->nmb_eachrank[r]; ++m) {
      MPI_Recv(blk.data(), static_cast<int>(bs), MPI_DOUBLE, r, 6, comm,
               MPI_STATUS_IGNORE);
      std::fwrite(blk.data(), sizeof(double), bs, fp);
    }
  }
#endif
}

//----------------------------------------------------------------------------------------
//! \fn  void Particles::NrpicMpiShareRestart
//! \brief after rank 0 has read the particle restart file: the scalar state of the
//! module goes to all ranks, and the source densities of the coming step to the ranks
//! of their MeshBlocks, in the layout NrpicStepSources expects (the array of the pack).
//! The particles stay on rank 0 until the first ownership pass.

void Particles::NrpicMpiShareRestart() {
#if MPI_PARALLEL_ENABLED
  Mesh *pm = pmy_pack->pmesh;
  auto &indcs = pm->mb_indcs;
  MPI_Comm comm = pbval_part->mpi_comm_part;
  const int myrank = global_variable::my_rank;
  double d[64];
  std::int64_t n[16];
  int nd = 0, nn = 0;
  if (myrank == 0) {
    d[nd++] = tau_probe; d[nd++] = alpha_probe; d[nd++] = e_probe;
    d[nd++] = mass_excised; d[nd++] = mass_escaped;
    d[nd++] = snap_next_time; d[nd++] = curv_next_time; d[nd++] = dt_probe_old;
    for (int q=0; q<8; ++q) { d[nd++] = tau_probes[q]; }
    for (int q=0; q<8; ++q) { d[nd++] = alpha_probes[q]; }
    for (int q=0; q<8; ++q) { d[nd++] = e_probes[q]; }
    for (int q=0; q<9; ++q) { d[nd++] = alpha_probe_old[q]; }
    n[nn++] = n_excised; n[nn++] = n_escaped; n[nn++] = snap_number;
    n[nn++] = curv_number;
    n[nn++] = ts_restart.empty() ? 0 : 1;
    for (int q=0; q<5; ++q) { n[nn++] = ts_restart_dims[q]; }
  } else {
    nd = 8 + 24 + 9;
    nn = 10;
  }
  MPI_Bcast(d, nd, MPI_DOUBLE, 0, comm);
  MPI_Bcast(n, nn, MPI_INT64_T, 0, comm);
  if (myrank != 0) {
    int q = 0;
    tau_probe = d[q++]; alpha_probe = d[q++]; e_probe = d[q++];
    mass_excised = d[q++]; mass_escaped = d[q++];
    snap_next_time = d[q++]; curv_next_time = d[q++]; dt_probe_old = d[q++];
    for (int c=0; c<8; ++c) { tau_probes[c] = d[q++]; }
    for (int c=0; c<8; ++c) { alpha_probes[c] = d[q++]; }
    for (int c=0; c<8; ++c) { e_probes[c] = d[q++]; }
    for (int c=0; c<9; ++c) { alpha_probe_old[c] = d[q++]; }
    n_excised = static_cast<int>(n[0]);
    n_escaped = static_cast<int>(n[1]);
    snap_number = static_cast<int>(n[2]);
    curv_number = static_cast<int>(n[3]);
  }
  // source densities of the coming step: the file holds them for at least all
  // MeshBlocks of the mesh, in the order of the global IDs
  const bool has_ts = (n[4] == 1);
  if (has_ts) {
    const std::int64_t e1 = Tmunu::N_Tmunu, e2 = indcs.nx3 + 2*indcs.ng;
    const std::int64_t e3 = indcs.nx2 + 2*indcs.ng, e4 = indcs.nx1 + 2*indcs.ng;
    const bool fits = (n[5] >= pm->nmb_total && n[6] == e1 && n[7] == e2 && n[8] == e3 &&
                       n[9] == e4);
    const size_t bs = static_cast<size_t>(e1*e2*e3*e4);
    const int nalloc = std::max(pmy_pack->nmb_thispack, pm->nmb_maxperrank);
    std::vector<double> loc;
    if (fits) {
      loc.assign(bs*nalloc, 0.0);
      if (myrank == 0) {
        std::memcpy(loc.data(), ts_restart.data(),
                    bs*pmy_pack->nmb_thispack*sizeof(double));
        for (int r=1; r<global_variable::nranks; ++r) {
          for (int m=0; m<pm->nmb_eachrank[r]; ++m) {
            MPI_Send(ts_restart.data() + bs*(pm->gids_eachrank[r] + m),
                     static_cast<int>(bs), MPI_DOUBLE, r, 7, comm);
          }
        }
      } else {
        for (int m=0; m<pmy_pack->nmb_thispack; ++m) {
          MPI_Recv(loc.data() + bs*m, static_cast<int>(bs), MPI_DOUBLE, 0, 7, comm,
                   MPI_STATUS_IGNORE);
        }
      }
      ts_restart_dims[0] = nalloc; ts_restart_dims[1] = e1; ts_restart_dims[2] = e2;
      ts_restart_dims[3] = e3; ts_restart_dims[4] = e4;
    } else if (myrank == 0) {
      std::cout << "NRPIC: the source densities of the coming step in the restart file "
                << "do not fit the mesh and are not used" << std::endl;
    }
    ts_restart.swap(loc);
  } else {
    ts_restart.clear();
  }
#endif
  NrpicMpiUpdateCounts();
}

} // namespace particles
