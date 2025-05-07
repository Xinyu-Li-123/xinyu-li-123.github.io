---
date: '2025-04-03T19:29:00-04:00'
draft: false
title: 'Chapter 17: Async Programming in Rust'
mathjax: true
---

## Asynchronous Programming (Language Agnostic)

This section aims to provide an introduction to the mechanism of asynchronous programming in a language-agnostic way. We will provide a python-ish pseudocode for a simple single-threaded event-loop-based async runtime. It should illustrate the underlying mechanism of async runtime in different languages at a high level. By that, I mean the pseudocode should show you what constructs are needed, but the exact implementation of that construct doesn't matter. E.g. there must be a data structure maintaining a collection of tasks that are ready to execute, but the exact choice of data structure varies by runtime and langauge, and doesn't matter for a high-level understanding.

> Note: This section results from a discussion with ChatGPT 4o and ChatGPT o3 on 2025/05/06. I can't guarantee its correctness in any way since I'm learning all these concepts as well.

### Intuition

If a task (a piece of code) needs to execute an I/O-bounded operation, instead of blocking on the operation until finished, it would be nice if the process can

1. yield (give up) control voluntarily

2. let an external runtime (another process) periodically check if the operation is done

3. only give control back when the operation is done

At the meantime, the CPU is idle and the external runtime can switch to execute other tasks.

This is the purpose of **asynchronous programming**: we want certain I/O-bounded operation to not block the entire thread, instead, the calling piece of code yields control and is resumed when the operation is done.

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

- **Task**: a scheduling unit, i.e. a resumable computation that can voluntarily suspend at certain points, and resume when woken by external async runtime.

- **Event**: the trigger that makes a waiting task runnable again.

### Pseudocode of Event Loop

To understand the implementation details of event loop, we need to give clearer definition of some concepts:

- **Task**: A task is a scheduling unit. It's what the event loop puts on a queue, polls, suspends, and drops when finished. A task is also a wrapper around a future (a future is an async operation. See next item for details). The full code of the task is compiled into a giant future that consists of multiple smaller child futures. Think of an async function that internally awaits on other async functions. We will refer to this "giant future compiled from task code" as "the task's future"

- **Future**:

  Conceptually, a future is an object that represents a value that is not yet available but will be produced in the future. When such a value is produced, we say the future is "resolved". We can `await` a future, and proceeds only when the future is resolved.

  Implementation-wise, a future is implemented as a state machine:

  - state: each `await` point corresponds to one state

  - transition: a `poll(waker) -> READY | PENDING` api is exposed. It checks whether the future is ready. It contains the transition logic of the state machine.
  
    - In the event loop, at the start of each iteration, the `poll` method of all ready tasks will be called. Calling the `poll` method of a task will call the `poll` method of the task's future, which may call `poll` of its child futures. This will lead to one of three kinds of state transition:

      - the task's future was at the starting point, and now it proceed to the first `await` point / task end

      - the current `await` point is not completed, so the task's future remains at the current `await` point

      - the current `await` point is finished, and the task's future proceeds to next `await` point / task ends

      As part of the state transition logic, `poll` method of child futures may be called. More specifically, if the parent future remains in the same state after transition, the `poll` method of the child future at that state will be called.

    - `waker` is the callback / handler of all events associated with the task. It simply reschedules the task. The implementation of `poll` of the task's future (and its child futures) specifies where the `waker` function of that task should be called.

    > Each task also exposes a `poll` method of the same signature, which simply calls the `poll` method of the task's future.

Now, we will present a python-ish pseudocode for the event loop, along with other construct that facilitate the implementation. We will also show psuedocode for the async runtime, and define two async functions: `sleep(duration)` and `read_socket(sock, nbytes)` (read `nbytes` from socket `sock` asynchronously).

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

- `TASKS: Dict[int, Task]`: a mapping from task id to taskid

- `TIMER_HEAP: List[Tuple[float, Waker]]`: a min-heap of `(deadline, waker)`. A min-heap is used to efficiently obtain the closest deadline among all timers. The `poll` method of futures returned by `sleep(duration)` will push the task's waker, along with `deadline = now + duration` to the heap.

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
    fut: Future = my_async_fn()

    # spawn a task whose future is `fut`
    spawn(fut)

    # Start the event loop
    run()

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
      # will hold SleepFuture
      _sleep: Future | None = None

      def poll(self, waker: Waker) -> tuple[Poll, None]:
          # STATE 0 – entry
          if self._state == 0:
              print("step 1")
              # create child future
              self._sleep = sleep(1.0)
              self._state = 1

          # STATE 1 – waiting on the child future
          if self._state == 1:
              # forward the waker
              outcome, _ = self._sleep.poll(waker)
              if outcome is Poll.PENDING:
                  # not ready yet
                  return Poll.PENDING, None
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

Let's work on another example. This times, we define an async function called `echo_once(sock: socket.socket)`, which read 1KiB from a socket, and echo it back once. It depends on two async functions:

- `read_socket(sock: socket.socket, nbytes: int)` that reads exactly `nbytes` from a socket without blocking the entire thread. Within each call of `poll`, it will read whatever is available from the socket (e.g. using the non-blocking mode of `epoll`), and stop reading until `nbytes` are read.

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
                m = sock.recv_into(
                  memoryview(buffer)[read_so_far:], 
                  nbytes - read_so_far
                )
                # orderly shutdown
                if m == 0:
                    raise ConnectionError("peer closed")
                read_so_far += m
                if read_so_far == nbytes:
                    return Poll.READY, bytes(buffer)
            # nothing available *yet*
            except (BlockingIOError, WouldBlockError):
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
      # ReadFuture
      _read: Future | None = None
      # Future from sendall
      _send: Future | None = None
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
              self._send = self._sock.sendall(data)
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
    # make the socket non‑blocking, so that read returns immediately
    # (return data if any data is available, or error if blocking is needed)
    server.setblocking(False)

    async def accept_loop() -> None:
        while True:
            # assume accept_client() Future resolves when a client is accepted
            client, _ = await accept_client(server)
            # echo connection in its own task
            spawn(echo_once(client))
            # schedule the listener
    spawn(accept_loop())

    run()
```

## Basic Usage of Future in Rust

> Note: Throughout this post, we will use the `trpl` crate, which provides common apis related to future, and hides details of async runtime.

Rust provides a `std::future::Future` trait, and the `async` and `await` keyword.

Here is the definition of `Future` trait

```rust
pub trait Future {
    type Output;

    // Required method
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

As a user of async feature, instead of a dev of async runtime, we are unlikely to implement `Future` trait on custom struct by ourselves. But it's still important to understand the apis provided by `Future`.

We can apply `async` keyword to blocks and functions, within which we can use `await` keyword to await a future (wait for it to resolve). Any site of await is a potential spot for pause / resume. Rust will compile block / function marked by `async` into equivalent code using the `Future` trait.

Below is a simple async program that fetches the title of a web page

```rust
use trpl::Html;

async fn page_title(url: &str) -> Option<String> {
    let response = trpl::get(url).await;
    let response_text = response.text().await;
    Html::parse(&response_text)
        .select_first("title")
        .map(|title_element| title_element.inner_html())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();

    trpl::run(async {
        let url = &args[1];
        match page_title(url).await {
            Some(title) => println!("The title for {url} was {title}"),
            None => println!("{url} had no title"),
        }
    })
}
```

- `trpl::run`: block on a specific future. The signature is

  ```rust
  pub fn run<F: Future>(future: F) -> F::Output
  ```

  To actually execute the async functions, we must call this `trpl::run` on a future at certain point.

  This is the reason why `main` can't be an async function, otherwise no function will be calling `trpl::run`.

Here is a slightly more complex example that fetch title of two urls, and print the one that returns earlier

```rust
use trpl::{Either, Html};

fn main() {
    let args: Vec<String> = std::env::args().collect();

    trpl::run(async {
        let title_fut_1 = page_title(&args[1]);
        let title_fut_2 = page_title(&args[2]);

        let (url, maybe_title) =
            match trpl::race(title_fut_1, title_fut_2).await {
                Either::Left(left) => left,
                Either::Right(right) => right,
            };

        println!("{url} returned first");
        match maybe_title {
            Some(title) => println!("Its page title is: '{title}'"),
            None => println!("Its title could not be parsed."),
        }
    })
}

async fn page_title(url: &str) -> (&str, Option<String>) {
    let text = trpl::get(url).await.text().await;
    let title = Html::parse(&text)
        .select_first("title")
        .map(|title| title.inner_html());
    (url, title)
}
```

- `trpl::Either`: an enum representing the concept of "either this or that".

    ```rust
    pub enum Either<A, B> {
        Left(A),
        Right(B),
    }
    ```

- `trpl::race`: run two futures, taking whichever finishes first and canceling the other.

    ```rust
    pub async fn race<A, B, F1, F2>(f1: F1, f2: F2) -> Either<A, B> ⓘ
    where
        F1: Future<Output = A>,
        F2: Future<Output = B>,
    ```

## Applying Concurrency with Async

### Concurrently Execute Two Futures with Join

Given two futures `A` and `B`, if we await them sequentially, we won't be able to get concurrency

```rust
async {
  let A = async { 
    for _ in 0..10 {
      trpl::sleep(Duration::from_secs(1))
      println!("A once") 
    }
    println!("A done") 
  };
  let B = async { 
    for _ in 0..10 {
      trpl::sleep(Duration::from_secs(1))
      println!("B once") 
    }
    println!("B done") 
  };
  A.await
  B.await
}
```

Instead, `A` will first finish execution. Afterwards, B will start and execute. This is because future in rust is lazy: only when a future is awaited will it start execution.

To execute A and B concurrently, one way is to use `join`.

```rust
trpl::join(A, B).await;
```

The signature of `join` is

```rust
pub fn join<Fut1, Fut2>(future1: Fut1, future2: Fut2) -> Join<Fut1, Fut2>
where
    Fut1: Future,
    Fut2: Future,
```

`join` will return a new future which awaits both futures. Internally, it will poll the two futures alternatively, so that they can be executed concurrently.

### Creating New Tasks using `spawn_task`

We can also spawn multiple tasks to execute async code concurrently using the `trpl::spawn_task` api. Below is such an example. There are three tasks: task1 sleep for 3 seconds, task2 and task3 prints stuff every 500 miliseconds.

> Note: we build the runtime manually because `trpl::run` uses a multi-threaded runtime, but we need a single-threaded runtime later to show the difference between sync sleep and async sleep.

```rust
#[test]
fn test_async_sleep() {
    let rt = Builder::new_current_thread().enable_all().build().unwrap();
    rt.block_on(async {
        let handle1 = trpl::spawn_task(async {
            println!("Start sleeping");
            for sec in 1..4 {
                trpl::sleep(Duration::from_secs(1)).await;
                println!("{} seconds has passed", sec);
            }
            println!("End sleeping, what a nice nap!");
        });

        let handle2 = trpl::spawn_task(async {
            for i in 0..4 {
                println!("Task 2: i = {}", i);
                trpl::sleep(Duration::from_millis(500)).await;
            }
        });

        let handle3 = trpl::spawn_task(async {
            for j in 100..104 {
                println!("Task 3: j = {}", j);
                trpl::sleep(Duration::from_millis(500)).await;
            }
        });

        trpl::join_all(vec![handle1, handle2, handle3]).await;
    });
}
```

The output is

```text
Start sleeping
Task 2: i = 0
Task 3: j = 100
Task 2: i = 1
Task 3: j = 101
1 seconds has passed
Task 2: i = 2
Task 3: j = 102
Task 2: i = 3
Task 3: j = 103
2 seconds has passed
3 seconds has passed
End sleeping, what a nice nap!
```

Note that the sleep in task1 doesn't block the print in task2 and task3. This is because we are using `trpl::sleep`, which is a non-blocking sleep. This is still aligned with the semantics of sleep, where the caller of sleep pause for some time, and resume execution afterwards. Yet it is non-blocking in the sense that it won't block the execution of other tasks.

If we use `std::thread::sleep` instead, we will block the entire thread on which the async runtime executes, and thus blocking other tasks. The code below modify task1 to use a blocking sleep

```rust
#[test]
fn test_sync_sleep() {
    // Since trpl uses multi-threaded tokio runtime by default, we need to manually build a
    // single threaded runtime to see how `thread::sleep` blocking the entire thread
    let rt = Builder::new_current_thread().enable_all().build().unwrap();
    rt.block_on(async {
        let handle1 = trpl::spawn_task(async {
            println!("Start sleeping");
            for sec in 1..4 {
                thread::sleep(Duration::from_secs(1));
                println!("{} seconds has passed", sec);
            }
            println!("End sleeping, what a nice nap!");
        });

        let handle2 = trpl::spawn_task(async {
            for i in 0..4 {
                println!("Task 2: i = {}", i);
                trpl::sleep(Duration::from_millis(500)).await;
            }
        });

        let handle3 = trpl::spawn_task(async {
            for j in 100..104 {
                println!("Task 3: j = {}", j);
                trpl::sleep(Duration::from_millis(500)).await;
            }
        });

        trpl::join_all(vec![handle1, handle2, handle3]).await;
    });
}
```

The output is

```text
Start sleeping
1 seconds has passed
2 seconds has passed
3 seconds has passed
End sleeping, what a nice nap!
Task 2: i = 0
Task 3: j = 100
Task 2: i = 1
Task 3: j = 101
Task 2: i = 2
Task 3: j = 102
Task 2: i = 3
Task 3: j = 103
```

From the output, we can see that task1 indeed blocks task2 and task3.

Even if task1 sleeps 1 second at a time in the loop, the scheduler won't be able to switch from task1 to other tasks between each sleep. This is because the task can only be paused at `await` points. This also shows that the scheduling is cooperative: it is the task that specifies where to pause, and the scheduler won't interrupt a task preemptively.

> Note: If we use `trpl::run`, task2 and task3 won't be blocked by task1 because the underlying async runtime is multi-threaded. Task1 only blocks one thread, and task2 and task3 can run on other threads.

### Message Passing between Tasks

Similar to threads, tasks can communicate with each others using channels as well. We have `trpl::channel()`, which is an async channel. It's different from the sync channel in two ways

Here is an example usage

```rust
#[test]
fn test_multi_messages() {
    let vals = vec![
        String::from("hi"),
        String::from("from"),
        String::from("the"),
        String::from("future"),
    ];

    trpl::run(async {
        let (tx, mut rx) = trpl::channel();

        // move tx to the async block, so that on execution end, sender will be dropped and
        // receiver will end
        let tx_fut = async move {
            for val in vals {
                tx.send(val).unwrap();
                trpl::sleep(Duration::from_millis(500)).await;
            }
        };

        let rx_fut = async {
            while let Some(msg) = rx.recv().await {
                println!("Recv: {msg}");
            }
        };

        trpl::join(tx_fut, rx_fut).await;
    })
}
```

- Async channel is different from sync channel in these aspects

  - receiver is mutable

  - calling `recv()` won't block. Instead, it will return a future. In comparison, the sync mpsc `recv()` will block until receiving the value.

    the future `recv()` will resolve only when a message is received or when the sender is closed

  - `send()` won't block b/c the channel is unbounded (number of msg is infinite)

- The `rx.recv()` returns a future that resolves to `Option<T>`. It resolves to `Some(T)` if a message is received, and `None` if all transmitters are dropped.

- Note that we are using `async move` instead of `async` when spawning the task that uses transmitter to send messages. This is so that the transmitter will be dropped once all messages are sent. The loop of receiving won't end until all transmitters are dropped.

Here is a more complex example that creates multiple senders to send messages concurrently.

```rust
#[test]
fn test_multi_sender() {
  let (tx, mut rx) = trpl::channel();

  let tx1 = tx.clone();
  let tx1_fut = async move {
      let vals = vec![
          String::from("hi"),
          String::from("from"),
          String::from("the"),
          String::from("future"),
      ];

      for val in vals {
          tx1.send(val).unwrap();
          trpl::sleep(Duration::from_millis(500)).await;
      }
  };

  let rx_fut = async {
      while let Some(value) = rx.recv().await {
          println!("received '{value}'");
      }
  };

  let tx_fut = async move {
      let vals = vec![
          String::from("more"),
          String::from("messages"),
          String::from("for"),
          String::from("you"),
      ];

      for val in vals {
          tx.send(val).unwrap();
          trpl::sleep(Duration::from_millis(1500)).await;
      }
  };
  trpl::join3(tx1_fut, tx_fut, rx_fut).await;
}
```

## Working with Any Number of Futures

### Join Any Number of Futures

How can we join any number of futures? One way is to use the `join!` macro, such as

```rust
trpl::join!(tx1_fut, tx_fut, rx_fut);
```

The downside of this approach is that we must know exactly which futures we want to join at compile time. If the exact futures must be determined at runtime (e.g. a random number of futures), this approach won't work.

An alternative approach is to use `trpl::join_all`. Here is its signature

```rust
pub fn join_all<I>(iter: I) -> JoinAll<<I as IntoIterator>::Item>
where
    I: IntoIterator,
    <I as IntoIterator>::Item: Future,
```

This function takes in a collection of futures, and return a future that resolves when all input futures resolve.

But how can we use `join_all`? The obvious way is to write

```rust
let futures = vec![tx1_fut, rx_fut, tx_fut];
trpl::join_all(futures).await;
```

However this won't work because entries in vector must be of same type, but compiler creates a unique enum for each async block, so no two async blocks, even if identical, have the same type.

We can solve this by using a trait object:

```rust
let futures: Vec<Box<dyn Future<Output = ()>>> = vec![
  Box::new(tx1_fut), 
  Box::new(tx_fut), 
  Box::new(rx_fut), 
];
trpl::join_all(futures).await;
```

But this won't work either. This is because async blocks are compiled into a state machine which may internally store pointers to local variables. If the future is moved, its memory address may change, and the internal points may become invalid.

As a result, we need to guarantee the future won't be moved in memory. This can be done using the `Box::pin` method:

```rust
let futures: Vec<Pin<Box<dyn Future<Output = ()>>>> = vec![
  Box::pin(tx1_fut), 
  Box::pin(tx_fut), 
  Box::pin(rx_fut), 
];
trpl::join_all(futures).await;
```

`Box::pin(x: T) -> Pin<Box<T>>` constructs a `Pin<Box<T>>`. If `T` doesn't implements `Unpin` trait, then `x` will be pinned in memory and unable to be moved.

To sum up, there are two approachs to join multiple futures

- `join!`: this requires us to know the exact number of futures at compile time. But we have the benefits that we can join futures of different types

- `join_all`: this allows us to join a dynamic number of futures, but these futures must have the same type.

### Starvation

If a future runs for a long time without any await point, other futures won't be able to make progress. For example,

```rust
fn slow(name: &str, ms: u64) {
    thread::sleep(Duration::from_millis(ms));
    println!("'{name}' ran for {ms}ms");
}

fn main() {
  trpl::run(async {
    let a = async {
        println!("'a' started.");
        slow("a", 30);
        slow("a", 10);
        slow("a", 20);
        println!("'a' finished.");
    };

    let b = async {
        println!("'b' started.");
        slow("b", 75);
        slow("b", 10);
        slow("b", 15);
        slow("b", 350);
        println!("'b' finished.");
    };

    trpl::race(a, b).await;
  });
}
```

We will be stucked at future `a` for a long time, and only start executing future `b` when `a` is finished. This is because each call to `slow` is synchronous, meaning there is no way to pause `a` and switch to `b`. To deal with this, we can voluntarily yield control between each `slow` operation, so that we can switch to `b` in between of two `slow` operations.

```rust
  let a = async {
      println!("'a' started.");
      slow("a", 30);
      trpl::yield_now().await;
      slow("a", 10);
      trpl::yield_now().await;
      slow("a", 20);
      trpl::yield_now().await;
      println!("'a' finished.");
  };

  let b = async {
      println!("'b' started.");
      slow("b", 75);
      trpl::yield_now().await;
      slow("b", 10);
      trpl::yield_now().await;
      slow("b", 15);
      trpl::yield_now().await;
      slow("b", 35);
      trpl::yield_now().await;
      println!("'b' finished.");
  };
```

### Building Our Own Async Abstractions

Using what we have learnt, we can build our own async abstractions. For example, we can build an async function `timeout` that try to execute a future, and abort if a timeout expires.

```rust
pub async fn timeout<F: Future>(fut: F, max_timeout: Duration) -> Result<F::Output, Duration> {
    // Either finish before timeout and return result, or timeout and return None
    match trpl::race(fut, trpl::sleep(max_timeout)).await {
        Either::Left(res) => Ok(res),
        Either::Right(()) => Err(max_timeout),
    }
}
```

Below is an example usage

```rust
fn test_timeout() {
    trpl::run(async {
        let fast = async {
            trpl::sleep(Duration::from_millis(500)).await;
            "fast-result"
        };
        let slow = async {
            trpl::sleep(Duration::from_millis(2000)).await;
            "slow-result"
        };
        let max_timeout = 1000;
        let max_timeout = Duration::from_millis(max_timeout);

        match timeout(slow, max_timeout).await {
            Ok(res) => println!("Finish within timeout, return {:?}", res),
            Err(duration) => println!("Error: Exceed timeout of {:?}", duration),
        };
        match timeout(fast, max_timeout).await {
            Ok(res) => println!("Finish within timeout, return {:?}", res),
            Err(duration) => println!("Error: Exceed timeout of {:?}", duration),
        };
    })
}
```

The output is

```text
Error: Exceed timeout of 1s
Finish within timeout, return "fast-result"
```

## Streams: Futures in Sequence

TODO: Finish this section

Stream is the asynchronous version of iterator. Each next value is a future that can be await'ed. To use stream similar to iterator (e.g. in a `while let` loop), we need to bring the `StreamExt` trait in scope. For example,

```rust
use trpl::StreamExt;

fn main() {
    trpl::run(async {
        let values = 1..101;
        let iter = values.map(|n| n * 2);
        let stream = trpl::stream_from_iter(iter);

        let mut filtered =
            stream.filter(|value| value % 3 == 0 || value % 5 == 0);

        while let Some(value) = filtered.next().await {
            println!("The value was: {value}");
        }
    });
}
```

The `Stream` trait defines the low-level `poll_next()` method that polls to check if next value is ready, while the `StreamExt` trait (**Stream** **Ext**ension) provides high-level `next()` method that returns a future of next value we can await. We will usually be working with `StreamExt`.

Similar to `Iterator` trait, `StreamExt` also provides many methods that are based on the `next` method. Below is a usage of the `filter` method.

```rust
use trpl::StreamExt;

fn main() {
    trpl::run(async {
        let values = 1..101;
        let iter = values.map(|n| n * 2);
        let stream = trpl::stream_from_iter(iter);

        let mut filtered =
            stream.filter(|value| value % 3 == 0 || value % 5 == 0);

        while let Some(value) = filtered.next().await {
            println!("The value was: {value}");
        }
    });
}
```

### Composing Streams

Many concepts are naturally represented as streams:

- items becoming available in a queue

- chunks of data being pulled incrementally from the filesystem when the full data set is too large for the computer

- or data arriving over the network over time.

### Merging Streams

## Traits for Async

### `Future` Trait

### `Pin` Struct and `Unpin` Traits

### `Stream` Trait
