"""The single-writer lock of the knowledge base (brief 12.1, 14.2: locks/kb-writer.lock).

Every write to kb-data (database, manifests copy, SHA256SUMS, logs) happens inside
`writer_lock(layout)`. The lock is an flock on the file; the holder writes its pid and the
time into it so that a waiting process can say who holds it.
"""
import contextlib
import fcntl
import os
import time


class LockTimeout(RuntimeError):
    pass


def _flock_blocking(fd, timeout):
    """Wait in the kernel for the lock (woken at the holder's unlock, so a writer that
    releases and re-takes the lock in a loop cannot starve this one, as polling could).
    Uses SIGALRM for the timeout, hence the main thread only; returns None elsewhere."""
    import signal
    import threading
    if threading.current_thread() is not threading.main_thread() or timeout <= 0:
        return None

    def _alarm(signum, frame):
        raise TimeoutError

    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        return True
    except TimeoutError:
        return False
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


@contextlib.contextmanager
def writer_lock(lay, timeout=600.0, poll=0.5, what="write"):
    os.makedirs(os.path.dirname(lay.lock), exist_ok=True)
    fd = os.open(lay.lock, os.O_RDWR | os.O_CREAT, 0o664)
    t0 = time.monotonic()
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                got = _flock_blocking(fd, timeout - (time.monotonic() - t0))
                if got:
                    break
                if got is False or time.monotonic() - t0 > timeout:
                    holder = os.pread(fd, 200, 0).decode(errors="replace").strip()
                    raise LockTimeout(f"{lay.lock} held for > {timeout:.0f} s by: {holder or '?'}")
                time.sleep(poll)
        os.ftruncate(fd, 0)
        os.pwrite(fd, f"pid {os.getpid()} since {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}"
                      f" for {what}\n".encode(), 0)
        try:
            yield
        finally:
            os.ftruncate(fd, 0)
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)
