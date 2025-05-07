---
date: '2025-04-03T19:29:00-04:00'
draft: false
title: 'Chapter 17: Async Programming in Rust'
mathjax: true
---

## Asynchronous Programming

> Note: This section results from a discussion with ChatGPT 4o and ChatGPT o3 on 2025/05/06. I attempt to have a language-agnostic understanding of asynchrounous programming. I can't guarantee its correctness in any way since I'm learning all these concepts as well.

### Intuition

If a process needs to execute an I/O-bounded operation, instead of blocking on the operation until finished, it would be nice if the process can

1. yield (give up) control voluntarily

2. let an external runtime (another process) periodically check if the operation is done

3. only give control back when the operation is done

At the meantime, the CPU is idle and the external runtime can switch to execute other processes.

This is the purpose of **asynchronous programming**: we want certain I/O-bounded operation to not block the entire thread, instead, the calling thread yields control and is resumed when the operation is done.

For example, we might write code like this

```python
async def delay_message() -> None:
    """Print, wait 10 seconds, print again."""
    print("step 1")
    await sleep(10.0) 
    print("step 2")
```

Executing 1000 `delay_message()` concurrently should still takes around 10 seconds, because each `delay_message()` doesn't make much use of CPU and only waits for 10 seconds.

### Mechanism of Async Runtime: Event Loop

Async function like `delay_message()` is made possible with an **async runtime** that does the heavy-lifting: switching between async functions, check if one `await` is ready, etc. The async runtime is usually implemented as an event loop: a loop that waits for events to happen, and dispatches tasks in response.

At a high level, an event loop does these

```text
while true:
  1. Run all tasks that are ready to proceed
  2. Wait for external events to happen. 
    This includes
    - timeout expires for sleep. E.g. a task yields on a call to `sleep(3)` previously, and 4 seconds have passed since then.
    - block of data is ready to read in a socket. Only block of data, not necessarily the full data.
  3. Wake up the task associated with the external event, and mark it as ready to proceed
```

To understand event loop from a high level, we need to define exactly two nouns:

- **Task**: a scheduling unit, and a resumable computation that can voluntarily suspend at certain points, and resume when woken by external async runtime.

- **Event**: the trigger that makes a waiting task runnable again.

### Pseudocode of Event Loop

To understand the implementation details of event loop, we need to re-define some concepts, and define some new concepts:

- **Task**: A task is a scheduling unit. It's what the event loop puts on a queue, polls, suspends, and drops when finished. A task is also a wrapper around a future (a future is an async operation. See next item for details). The full code of the task is compiled into a giant future that consists of multiple smaller child futures. Think of an async function that internally awaits on other async functions. We will refer to this "giant future compiled from task code" as "the task's future"

- **Future**:

  Conceptually, a future is an object that represents a value that is not yet available but will be produced in the future. When such a value is produced, we say the future is "resolved". We can `await` a future, and proceeds only when the future is resolved.

  Implementation-wise, a future is implemented as a state machine:

  - state: each `await` point corresponds to one state

  - transition: a `poll(waker) -> READY | PENDING` api is exposed. It contains the transition logic of the state machine.
  
    - In the event loop, at the start of each iteration, the `poll` method of all ready tasks will be called. Calling the `poll` method of a task will call the `poll` method of the task's future, which may call `poll` of its child futures. This will lead to one of three kinds of state transition:

      - the task's future was at the starting point, and now it proceed to the first `await` point / task end

      - the current `await` point is not completed, so the task's future remains at the current `await` point

      - the current `await` point is finished, and the task's future proceeds to next `await` point or the task ends

      As part of the state transition logic, `poll` method of child futures may be called. More specifically, if the parent future remains in the same state after transition, the `poll` method of the child future at that state will be called.

    - `waker` is the callback / handler of all events associated with the task. It simply reschedules the task. The implementation of `poll` of the task's future (and its child futures) specifies where the `waker` function should be called.

    > Each task also exposes a `poll` method of the same signature, which simply calls the `poll` method of the task's future.

Now, we will present a python-ish pseudocode for the event loop, along with other construct that facilitate the implementation. We will show psuedocode for the async runtime, and define two async functions: `sleep(duration)` and `read_socket(sock, nbytes)` (read `nbytes` from socket `sock` asynchronously).

First, we will define some fundamental concepts: enum `Poll`, class `Waker`, `Future`, `Task`:

```python
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
```

The `Task.coro` is another future (**coro**utine) that is compiled from the async code of the task.

Now we will define the data structures that the async runtime depends on:

- `READY_QUEUE: Deque[int]`: a FIFO queue of runnable tasks

- `POLLER`: a poller for events. The core api is `POLLER.wait(timeout)`, which blocks until either an I/O complete or the timeout expires, and return the completed file descriptor (if timeout expires, no fd will be returned). In Python specifically, this depends on the class `selectors.DefaultSelector`.

- `TASKS: Dict[int, Task]`: a mapping from task id to taskkjo

- `TIMER_HEAP: List[Tuple[float, Waker]]`: a min-heap of `(deadline, waker)`. A min-heap is used to efficiently obtain the closest deadline among all timers. The `poll` method of apis like `sleep(duration)` will push the task's waker, along with `duration = now + duration` to the heap.

  - `deadline`: In each iteration of the event loop, the runtime will decide the timeout of `POLLER.wait(timeout)` based on the cloest deadline: `timeout = closest_deadline - now()`

  - `waker`: Whenever a timer expires, `waker` will be called to schedule the task by pushing it to the `READY_QUEUE`.

```python
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
```

Now, we are ready to present the actual event loop, which is a function called `run()`

```python
def run() -> None:
    # Either there is any ready task, or the selector isn't tracking any I/O events (get_map() returns an empty map)
    while READY_QUEUE or POLLER.sel.get_map():
        # 1. execute all tasks that are immediately runnable
        while READY_QUEUE:
            task_id = READY_QUEUE.popleft()
            task = TASKS[task_id]
            state, _ = task.poll(Waker(task_id))
            if state is Poll.READY:
                TASKS.pop(task_id, None)              # drop completed task

        # 2. figure out how long we may sleep
        now = time.monotonic()
        timeout = None
        if TIMER_HEAP:
            timeout = max(0.0, TIMER_HEAP[0][0] - now)

        # 3. block on I/O (or not at all if timeout == 0)
        events = POLLER.wait(timeout)

        # 4. wake any tasks whose fds became ready
        for fd, _mask in events:
            POLLER.waker_for(fd)()                    # call the waker

        # 5. expire timers
        now = time.monotonic()
        while TIMER_HEAP and TIMER_HEAP[0][0] <= now:
            _, waker = heapq.heappop(TIMER_HEAP)
            waker()
```

To make the runtime usable, we need `spawn(awaitable: Future)`, an api to schedule tasks, and `main()`, an entry point of the process.

```python
def spawn(awaitable: Future) -> None:
    """Wrap an awaitable in a Task and make it runnable *now*."""
    task = Task(awaitable)
    TASKS[task.id] = task
    READY_QUEUE.append(task.id)               # first poll will happen next loop‑tick


def main() -> None:
    """
    User‑visible entry point.
    Schedule initial coroutines, then hand control to the event loop.
    """

    # Obtain a future by calling an async function
    fut = ...

    # spawn a task whose future is `fut`
    spawn(fut)

    # Finally transfer control to the scheduler
    run()

# Conventional Python process entry check
if __name__ == "__main__":
    main()
```

Let's now look at some concrete example async functions.

First, the classic `sleep(duration)` function.

```python
def sleep(duration: float) -> Future:
    deadline = time.monotonic() + duration

    class SleepFuture(Future):
        def poll(self, waker: Waker) -> Tuple[Poll, Any]:
            if time.monotonic() >= deadline:
                return Poll.READY, None
            heapq.heappush(TIMER_HEAP, (deadline, waker))
            return Poll.PENDING, None
    return SleepFuture()
```

Next, an async function that awaits on `sleep`.

```python
async def delay_message() -> None:
    print("step 1")
    await sleep(1.0)
    print("step 2")
```

The `async` and `await` keywords make it easier to write async code. Internally, `delay_message()` is converted to a function that returns a future that resolves to None when completed, something like this:

```python
def delay_message() -> Future: 
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
  return DelayMessageSM()
```

The `main()` function using `delay_message()` would look like this

```python
def main() -> None:
    spawn(delay_message())
    run()
```

Let's work on another example. This times, we define an async function called `echo_once(sock: socket.socket)`, which read 1KiB from a socket, and echo it back one. It depends on two async functions:

- `read_socket(sock: socket.socket, nbytes: int)` that reads exactly `nbytes` from a socket without blocking the entire thread. This is done by reading whatever is available from the socket within each call of `poll`, until `nbytes` are read.

- `sock.sendall(data: bytes)` that returns a future which resolves when all `data` are sent.

Here is the `read_socket` function

```python
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
```

Here is the `echo_once` function, written with `async`/`await` keyword, and written directly as a function that returns `Future`

```python
async def echo_once(sock: socket.socket) -> None:
    """
    Read exactly 1 KiB from `sock` and echo it back once.
    Assumes `sock.sendall` is itself awaitable in this runtime.
    """
    data: bytes = await read_socket(sock, 1024)
    await sock.sendall(data)  # returns a Future that resolves when bytes sent

def echo_once(sock: socket.socket) -> Future:
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
  return EchoOnceSM(sock)
```

Here is one `main` function that uses `echo_once`:

```python
def main() -> None:
    # Example: echo server on localhost:9000
    server = socket.create_server(("127.0.0.1", 9000))
    server.setblocking(False)                 # make it non‑blocking

    async def accept_loop() -> None:
        while True:
            client, _ = await accept_client(server)  # assume accept_client() Future that resolves when a client is accepted
            spawn(echo_once(client))                 # echo connection in its own task

    spawn(accept_loop())                     # schedule the listener

    run()
```

## List of APIs

```rust
fn trpl::run<F: Future>(future: F) -> F::Output;

// the concept of "either", an enum w/ two variants `Left` and `Right`
enum trpl::Either;

// - Run two futures
// - Take whichever finished first and cancel another one
// - Return the result as a new future wrapped in `Either`
async fn trpl::race<A, B, F1, F2>(f1: F1, f2: F2) -> Either<A, B>
where
    F1: Future<Output = A>,
    F2: Future<Output = B>;

// spawn an async task and run it immediately in the background
// similar to std::spread::spawn
fn spawn_task<F>(future: F) -> JoinHandle<<F as Future>::Output>
where F: Future + Send + 'static,
      <F as Future>::Output: Send + 'static;

// message-passing

// multiple futures

/// join multiple futures
/// - futures can be of diff types
/// - num of futures known at compile time
macro join!
/// join multiple futures
/// - futures must be of same types
/// - num of futures known at run time
fn join_all()

// Streams: async iteration
trait StreamExt;

fn merge()

fn throttle()
```

Future represents a piece of code that can be paused

This is made possible by future runtime and the `Future` trait.

The pseudocode of the runtime is:

Mark a fn as async:

Equiv sync fn is:

Futures in Rust are lazy: they won't execute until you ask them to with the `await` keyword.

## Apply Concurrency with Async

### Task

### Message Passing

```rust
let (tx, mut rx) = trpl::channel();

let val = String::from("hi");
tx.send(val).unwrap();

let received = rx.recv().await.unwrap();
println!("Got: {received}");
```

Async channel is diff from sync channel in these aspects

- receiver is mutable

- calling `recv()` won't block. Instead, it will return a future. In comparison, the sync mpsc `recv()` will block until receiving the value.

  the future `recv()` will resolve only when a message is received or when the sender is closed

- `send()` won't block b/c the channel is unbounded (number of msg is infinite)

And it's same as sync channel in these aspects

## Working with Multiple Futures

## Streams

### Composing Streams

### Merging Streams

## Traits for Async

### `Future`

### `Pin` and `Unpin`

### `Stream` and `StreamExt`
