//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file vlasov_tasks.cpp
//! \brief AthenaK TaskList wrappers for the modular Vlasov/GR-LBV solver.
//! Exposes explicit PrepareStep -> SyncMetric -> Advance -> Excise stages (managing the
//! 3-level metric history for quadratic time interpolation) before NrpicDeposit/Diagnostics.

#include <utility>

#include "athena.hpp"
#include "driver/driver.hpp"
#include "mesh/mesh.hpp"
#include "particles/particles.hpp"
#include "particles/vlasov/vlasov_types.hpp"

namespace particles {

TaskStatus Particles::NrpicVlasovPrepareStep(Driver *pdriver, int stage) {
  NrpicAccSaveCentre();
  if (nropt.metric == NrpicMetric::mesh && !metric_is_static) {
    const bool quad = (vlv != nullptr &&
                       vlv->opt.time_interp == VLASOV_TINTERP_QUADRATIC);
    if (quad) {
      // 3-way zero-copy rotation: met_prev <- met0 <- met1 <- stale
      if (vlv->dt_step_cur > 0.0) {
        std::swap(met_prev, met0);
        if (nropt.interp_bspline) { std::swap(met_prevs, met0s); }
        vlv->met_prev_valid = true;
        vlv->dt_prev = vlv->dt_step_cur;
      }
      std::swap(met0, met1);
      if (nropt.interp_bspline) { std::swap(met0s, met1s); }
      vlv->dt_step_cur = pmy_pack->pmesh->dt;
    } else {
      std::swap(met0, met1);
      if (nropt.interp_bspline) { std::swap(met0s, met1s); }
    }
  }
  return TaskStatus::complete;
}

TaskStatus Particles::NrpicVlasovSyncMetric(Driver *pdriver, int stage) {
  if (nropt.metric == NrpicMetric::mesh && !metric_is_static) {
    NrpicFillMetric(met1);
    if (nropt.interp_bspline) { NrpicSharpenMetric(met1, met1s); }
  }
  return TaskStatus::complete;
}

TaskStatus Particles::NrpicVlasovAdvanceTask(Driver *pdriver, int stage) {
  NrpicAccBeforePush();
  NrpicVlasovPush();
  NrpicAccAfterPush();
  return TaskStatus::complete;
}

TaskStatus Particles::NrpicVlasovExciseTask(Driver *pdriver, int stage) {
  NrpicVlasovExcise();
  return TaskStatus::complete;
}

}  // namespace particles
