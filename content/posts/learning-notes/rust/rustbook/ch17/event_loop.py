from __future__ import annotations

import heapq
import selectors
import socket
import time
from collections import deque
from enum import Enum, auto
from typing import Any, Callable, Deque, Dict, List, MutableMapping, Tuple

# ---------------------------------------------------------------------------
# 0. Fundamental protocol ----------------------------------------------------
# ---------------------------------------------------------------------------

class Poll(Enum):
    READY = 0
    PENDING = 1

class Waker:
    """Callable that re‑schedules a specific task."""
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id

    def __call__(self) -> None:
        READY_QUEUE.append(self.task_id)

class Future:
    """All user‑visible awaitables ultimately subclass this and implement poll."""
    def poll(self, waker: Waker) -> Tuple[Poll, Any]:
        raise NotImplementedError

class Task(Future):
    """Thin wrapper around a compiler‑generated coroutine state‑machine."""
    _next_id: int = 0

    def __init__(self, coro: Future) -> None:
        self.coro: Future = coro
        self.id: int = Task._next_id
        Task._next_id += 1

    # Transparent delegate  
    def poll(self, waker: Waker) -> Tuple[Poll, Any]:
        return self.coro.poll(waker)

# ---------------------------------------------------------------------------
# 1. Global scheduler data‑structures ----------------------------------------
# ---------------------------------------------------------------------------

READY_QUEUE: Deque[int] = deque()                     # FIFO of runnable task‑ids

class SimplePoller:
    """Tiny wrapper over selectors.DefaultSelector for cross‑platform I/O."""
    def __init__(self) -> None:
        self.sel = selectors.DefaultSelector()        # kqueue/epoll/select/etc.
        self._wakers: Dict[int, Waker] = {}           # fd -> waker

    def register(self, sock: socket.socket, events: int, waker: Waker) -> None:
        key = sock.fileno()
        if key not in self._wakers:
            self.sel.register(sock, events)
        self._wakers[key] = waker

    def wait(self, timeout: float | None) -> List[Tuple[int, int]]:
        """Block until fd ready or timer expires; returns list[(fd, mask)]."""
        return [(key.fd, mask) for key, mask in self.sel.select(timeout)]

    def waker_for(self, fd: int) -> Waker:
        return self._wakers[fd]

POLLER = SimplePoller()                                # singleton reactor

TASKS: Dict[int, Task] = {}                            # id -> Task instance

TIMER_HEAP: List[Tuple[float, Waker]] = []             # (deadline, waker)

# ---------------------------------------------------------------------------
# 2. Event‑loop --------------------------------------------------------------
# ---------------------------------------------------------------------------

def run() -> None:
    while READY_QUEUE or POLLER.sel.get_map():
        # 2.1 execute all tasks that are immediately runnable
        while READY_QUEUE:
            task_id = READY_QUEUE.popleft()
            task = TASKS[task_id]
            state, _ = task.poll(Waker(task_id))
            if state is Poll.READY:
                TASKS.pop(task_id, None)              # drop completed task

        # 2.2 figure out how long we may sleep
        now = time.monotonic()
        timeout = None
        if TIMER_HEAP:
            timeout = max(0.0, TIMER_HEAP[0][0] - now)

        # 2.3 block on I/O (or not at all if timeout == 0)
        events = POLLER.wait(timeout)

        # 2.4 wake any tasks whose fds became ready
        for fd, _mask in events:
            POLLER.waker_for(fd)()                    # call the waker

        # 2.5 expire timers
        now = time.monotonic()
        while TIMER_HEAP and TIMER_HEAP[0][0] <= now:
            _, waker = heapq.heappop(TIMER_HEAP)
            waker()

# ---------------------------------------------------------------------------
# 3. Library primitives ------------------------------------------------------
# ---------------------------------------------------------------------------

def sleep(duration: float) -> Future:
    deadline = time.monotonic() + duration

    class SleepFuture(Future):
        def poll(self, waker: Waker) -> Tuple[Poll, Any]:
            if time.monotonic() >= deadline:
                return Poll.READY, None
            heapq.heappush(TIMER_HEAP, (deadline, waker))
            return Poll.PENDING, None
    return SleepFuture()

def read_socket(sock: socket.socket, nbytes: int) -> Future:
    """Returns a Future that resolves with exactly `nbytes` bytes."""
    buffer = bytearray(nbytes)
    read_so_far = 0

    class ReadFuture(Future):
        nonlocal read_so_far

        def poll(self, waker: Waker) -> Tuple[Poll, Any]:
            nonlocal read_so_far
            try:
                m = sock.recv_into(memoryview(buffer)[read_so_far:], nbytes - read_so_far)
                if m == 0:                       # orderly shutdown
                    raise ConnectionError("peer closed")
                read_so_far += m
                if read_so_far == nbytes:
                    return Poll.READY, bytes(buffer)
            except (BlockingIOError, WouldBlockError):   # nothing available *yet*
                POLLER.register(sock, selectors.EVENT_READ, waker)
            return Poll.PENDING, None
    return ReadFuture()

# ---------------------------------------------------------------------------
# 4. User‑level “async” functions (before compilation) -----------------------
# ---------------------------------------------------------------------------

def delay_message() -> DelayMessageSM:
    async def _impl():
        print("step 1")
        await sleep(1.0)
        print("step 2")
    return _impl()  # imaginary awaitable — real compiler rewrites this…

def echo_once(sock: socket.socket) -> EchoOnceSM:
    async def _impl():
        data = await read_socket(sock, 1024)
        await sock.sendall(data)     # assume sendall is awaitable in this runtime
    return _impl()

# What the compiler WOULD produce is the state‑machine versions

class DelayMessageSM(Future):
    """
    State‑machine version of `delay_message`.
    _state: 0=entry, 1=waiting-for-sleep, 2=finished
    """
    _state: int = 0
    _sleep: Future | None = None                                # will hold SleepFuture

    def poll(self, waker: Waker) -> tuple[Poll, None]:
        # STATE 0 – entry
        if self._state == 0:
            print("step 1")
            self._sleep = sleep(1.0)                            # create child future
            self._state = 1

        # STATE 1 – waiting on the child future
        if self._state == 1:
            outcome, _ = self._sleep.poll(waker)                # forward the waker
            if outcome is Poll.PENDING:
                return Poll.PENDING, None                       # not ready yet
            # child finished
            print("step 2")
            self._state = 2

        # STATE 2 – terminal
        return Poll.READY, None

class EchoOnceSM(Future):
    """
    State‑machine version of `echo_once`.
    _state: 0=entry, 1=reading, 2=sending, 3=done
    """
    _state: int = 0
    _read: Future | None = None                                 # ReadFuture
    _send: Future | None = None                                 # Future from sendall
    _sock: socket.socket

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock

    def poll(self, waker: Waker) -> tuple[Poll, None]:
        # STATE 0 – start read
        if self._state == 0:
            self._read = read_socket(self._sock, 1024)
            self._state = 1

        # STATE 1 – waiting for the read to complete
        if self._state == 1:
            outcome, data = self._read.poll(waker)
            if outcome is Poll.PENDING:
                return Poll.PENDING, None
            # have full payload; start send
            self._send = self._sock.sendall(data)               # again, returns Future
            self._state = 2

        # STATE 2 – waiting for sendall to finish
        if self._state == 2:
            outcome, _ = self._send.poll(waker)
            if outcome is Poll.PENDING:
                return Poll.PENDING, None
            self._state = 3

        # STATE 3 – terminal
        return Poll.READY, None
