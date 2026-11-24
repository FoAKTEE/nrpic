#ifndef UTILS_TERM_SIGNAL_HPP_
#define UTILS_TERM_SIGNAL_HPP_
//========================================================================================
// AthenaK astrophysical fluid dynamics & numerical relativity code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file term_signal.hpp
//! \brief Orderly stop on the termination signal (SIGTERM).
//!
//! A batch system that preempts, cancels or times out a job sends SIGTERM and, after a
//! grace period, SIGKILL.  Without a handler the run dies on the first signal and all
//! work since its last restart file is lost.  With the handler installed by
//! term_signal::Install() the signal only sets a flag; Driver::Execute asks for it once
//! per cycle (term_signal::Check, agreed over the MPI ranks), leaves the main loop after
//! the cycle in progress, Driver::Finalize writes every restart output once and nothing
//! else, and main returns term_signal::ExitStatus() (143, the status of a process killed
//! by SIGTERM), so that wrappers still see a run that did not end by itself.  The state
//! of the run is not touched: a run that is never signalled is bit-identical to one
//! without the handler.  The handler stays installed (batch systems and wrappers send
//! the signal more than once); SIGKILL remains the way to stop a run at once.
//! Interface text: tracks/core/interfaces/preempted_runs.md.

namespace term_signal {

//! install the SIGTERM handler (call once, after MPI and Kokkos are initialized)
void Install();
//! has any rank received the signal?  Collective under MPI (one reduction per call).
//! A true result is latched: from then on Stopped() is true.
bool Check();
//! true once Check() has returned true: the main loop ended because of the signal
bool Stopped();
//! seconds since the first signal reached this process (negative: none received)
double SecondsSinceSignal();
//! exit status of a run stopped by the signal (128 + SIGTERM)
int ExitStatus();

} // namespace term_signal

#endif // UTILS_TERM_SIGNAL_HPP_
