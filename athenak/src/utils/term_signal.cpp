//========================================================================================
// AthenaK astrophysical fluid dynamics & numerical relativity code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
//! \file term_signal.cpp
//! \brief Orderly stop on the termination signal (SIGTERM): see term_signal.hpp.

#include <signal.h>   // sigaction (POSIX)
#include <time.h>     // clock_gettime (POSIX, async-signal-safe)

#include <csignal>

#include "athena.hpp"
#include "globals.hpp"
#include "utils/term_signal.hpp"

#if MPI_PARALLEL_ENABLED
#include <mpi.h>
#endif

namespace term_signal {

namespace {
// written by the handler: only objects of these types may be touched there
volatile std::sig_atomic_t received_ = 0;   // the signal has reached this process
volatile std::sig_atomic_t t_sec_ = 0;      // monotonic clock at the first signal (s)
volatile std::sig_atomic_t t_msec_ = 0;     // and its milliseconds
bool stopped_ = false;                      // latched result of Check()

// The handler does nothing but note the signal and the time of its first arrival.
// It stays installed: Slurm sends SIGTERM at the preemption and again at the end of the
// grace time, and job wrappers forward the signal as well.
extern "C" void Handler(int) {
  if (received_ == 0) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
      t_sec_ = static_cast<std::sig_atomic_t>(ts.tv_sec);
      t_msec_ = static_cast<std::sig_atomic_t>(ts.tv_nsec/1000000);
    }
    received_ = 1;
  }
}
} // namespace

//----------------------------------------------------------------------------------------
//! \fn void term_signal::Install()

void Install() {
  struct sigaction sa;
  sa.sa_handler = Handler;
  sigemptyset(&sa.sa_mask);
  sa.sa_flags = SA_RESTART;   // interrupted reads and writes of the run are resumed
  sigaction(SIGTERM, &sa, nullptr);
}

//----------------------------------------------------------------------------------------
//! \fn bool term_signal::Check()

bool Check() {
  int flag = (received_ != 0) ? 1 : 0;
#if MPI_PARALLEL_ENABLED
  // the ranks receive the signal at different moments: all leave after the same cycle
  MPI_Allreduce(MPI_IN_PLACE, &flag, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
#endif
  if (flag != 0) { stopped_ = true; }
  return stopped_;
}

//----------------------------------------------------------------------------------------
//! \fn bool term_signal::Stopped()

bool Stopped() {
  return stopped_;
}

//----------------------------------------------------------------------------------------
//! \fn double term_signal::SecondsSinceSignal()

double SecondsSinceSignal() {
  if (received_ == 0) { return -1.0; }
  struct timespec ts;
  if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) { return -1.0; }
  return static_cast<double>(ts.tv_sec - static_cast<time_t>(t_sec_)) +
         1.0e-3*(static_cast<double>(ts.tv_nsec/1000000) - static_cast<double>(t_msec_));
}

//----------------------------------------------------------------------------------------
//! \fn int term_signal::ExitStatus()

int ExitStatus() {
  return 128 + SIGTERM;
}

} // namespace term_signal
