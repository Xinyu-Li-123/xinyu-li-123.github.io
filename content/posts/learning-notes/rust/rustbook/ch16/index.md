---
date: '2025-03-15T03:03:17-04:00'
draft: false
title: 'Chapter 16: Fearless Concurrency'
mathjax: true
---

With Rust's ownership and type systems, many concurrency bugs become compile-time errors, instead of runtime errors.

## Thread

An example of thread api usage. We use the `std::thread::spawn` and `std::thread::join` similar to most languages.

```rust
fn test_multi_thread() {
    let mut handlers = vec![];
    for _ in 1..10 {
        let handler = thread::spawn(|| {
            println!("Hello world!");
            thread::sleep(Duration::from_millis(1));
        });
        handlers.push(handler);
    }

    for handler in handlers {
        handler.join().unwrap();
    }
}
```

We may want to access to a variable in the closure from the main thread context. If such access requires ownership, we must explicitly mark the thread body (the closure) with `move` keyword

```rust
fn test_move_to_thread() {
    let mut handlers = vec![];
    for i in 1..10 {
        // the move keyword will force the spawned thread to take ownership of i
        let my_struct = MyStruct { val: i };
        println!("{:?}", my_struct);
        let handler = thread::spawn(move || {
            println!("[{:?}] Hello world!", my_struct);
            thread::sleep(Duration::from_millis(1));
        });
        // This line will cause an error b/c my_struct is moved into the spawned thread at this
        // point
        // println!("{:?}", my_struct);
        handlers.push(handler);
    }

    for handler in handlers {
        handler.join().unwrap();
    }
}
```

Note that, since `move` transfer ownership from main thread to the spawned thread, we won't be able to access the variable after creating the thread.

## Message-Passing Concurrency

Rust std provides a mpsc channel:

```rust
let (tx, rv) = mpsc::Channel();
```

`tx` is for "transmitter", and `rv` is for "receiver".

We can send / receive using `send` and `recv`

```rust
fn send_recv_block() {
    let (tx, rx): (Sender<i32>, Receiver<i32>) = mpsc::channel();
    let val = 42;
    tx.send(val).unwrap();
    println!("Send: {}", val);
    let received = rx.recv().unwrap();
    println!("Recv: {}", received);
}
```

Sender won't block and receiver will.

We can send in one thread and receive in another thread.

```rust
fn spsc_basic() {
    // There is no need to explicitly annotate the type in this example
    // We are doing this only for illustration purpose
    let (tx, rx): (Sender<String>, Receiver<String>) = mpsc::channel();

    let handle = thread::spawn(move || {
        let val = String::from("hi");
        println!("Send: {}", val);
        tx.send(val).unwrap();
        // This line will cause error b/c the ownership of `val` is taken by `tx.send()`
        // println!("Send: {}", val);
    });

    handle.join().unwrap();

    let received = rx.recv().unwrap();
    println!("Recv: {}", received);

    println!("Done!");
}
```

Sender will take ownership of the sent value, so `move` must be used when declaring the thread's body (a closure). Intuitively, this makes sense because if we send something to someone, we don't hold that something anymore afterwards.

When multiple messages are sent, we can receive in a for loop

```rust
fn spsc_many_message() {
    let (tx, rx): (Sender<String>, Receiver<String>) = mpsc::channel();

    let handle = thread::spawn(move || {
        let val1 = String::from("hi");
        let val2 = String::from("from");
        let val3 = String::from("thread");
        tx.send(val1).unwrap();
        tx.send(val2).unwrap();
        tx.send(val3).unwrap();
    });

    handle.join().unwrap();

    // A for loop to iterate all received messages
    for received in rx {
        println!("Recv: {}", received);
    }

    println!("Done!");
}
```

We can have multiple sender by cloning `tx` using `mpsc::Sender::clone(&Self)`

```rust
fn mpsc_basic() {
    let vals = [
        String::from("hi"),
        String::from("from"),
        String::from("many"),
        String::from("threads"),
    ];
    let mut handles = vec![];

    let (tx, rx) = mpsc::channel();

    for val in vals {
        let send_val = val.clone();
        let tx_clone = mpsc::Sender::clone(&tx);
        let handle = thread::spawn(move || {
            println!("Send: {}", send_val);
            tx_clone.send(send_val).unwrap();
        });
        handles.push(handle);
    }

    // If we don't drop tx, the rx will keep blocking
    // In fact, rx will keep blocking until all clones (including original) of tx are dropped

    // If we create a clone of tx b/f dropping it, rx will still keep blocking.
    // let tx_clone = tx.clone();
    // println!("{:?}", tx_clone);

    drop(tx);

    for handle in handles {
        handle.join().unwrap();
    }

    for recv_val in rx {
        println!("Recv: {}", recv_val);
    }
}
```

Note that the for loop over all received message won't break until all senders are dropped in the thread that holds the receiver. If we remove the `drop(tx)` in the example above, the main thread will keep blocking even when all spawned threads have exited.

## Shared-State Concurrency

Mutex provides to a thread the exclusive access to a piece of data. Mutex in Rust is a bit different from that in CPP: in CPP, mutex protect a piece of code by wrapping them in lock/unlock, while in Rust mutex is used to protect a specific value.

```rust
fn mutex_basic() {
    let m = Mutex::new(5);

    println!("{:?}", m);

    {
        // Return a MutexGuard<i32>, which is a smart pointer acting as a RAII guard
        // That is, the mutex will be unlocked when the MutexGuard goes out of scope,
        let mut num = m.lock().unwrap();
        *num = 6;
    }

    println!("{:?}", m);
}
```

To create a counter that is incremented by multiple threads concurrently, we need `std::sync::Arc`. Arc (Atomic Reference Counter) is the concurrent version of Rc: it allows atomic update of ref count.

With Arc, we can allow concurrent access to a piece of data

```rust
fn arc_basic() {
    // Arc is just like Rc, except it allows concurrent access b/c it guarantee atomic
    // increment of the internal counter
    let number = Arc::new(42);
    // Rc doesn't implement Send trait, which is required for it to be safely sent between threads
    // let number = Rc::new(42);
    let mut handlers = vec![];
    for i in 0..5 {
        let number = Arc::clone(&number);
        let handler = thread::spawn(move || {
            let number = *number;
            println!("[{}] The number is: {}", i, number);
        });
        handlers.push(handler);
    }

    for handler in handlers {
        handler.join().unwrap();
    }

    println!("[main] Number: {:?}", *number);
}
```

Furthermore, Mutex + Arc allows us to define the counter mentioned earlier

```rust
fn mutex_counter_arc() {
    let counter = Arc::new(Mutex::new(0));
    println!("Before: {:?}", counter);
    let mut handlers = vec![];
    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handler = thread::spawn(move || {
            let mut val = counter.lock().unwrap();
            *val += 1;
        });
        handlers.push(handler);
    }

    for handler in handlers {
        handler.join().unwrap();
    }

    println!("After : {:?}", counter);
}
```

The combination of Mutex + Arc is similar to RefCell + RC, both provides interior mutability, i.e. immutable variable that can provide
a mutable reference to the underlying value.

Note that Mutex + Arc can't prevent deadlock, just like RefCell + Rc can't prevent from creating a cycle of reference and ref count of all var will stay equal 1 even when all refs are dropped. In fact, both are caused by some form of cyclic reference

Below is an example of a deadlock. It happens because thread 1 holds mutex on `num1` and waits for mutex on `num2`, while thread 2 holds mutex on `num2` and waits for mutex on `num1`

```rust
fn deadlock_example() {
    let num1 = Arc::new(Mutex::new(10));
    let num2 = Arc::new(Mutex::new(100));
    println!("Before: {:?}, {:?}", num1, num2);

    let num1_arc1 = Arc::clone(&num1);
    let num1_arc2 = Arc::clone(&num1);
    let num2_arc1 = Arc::clone(&num2);
    let num2_arc2 = Arc::clone(&num2);

    let handle1 = thread::spawn(move || {
        let mut num1 = num1_arc1.lock().unwrap();
        println!("[1] Got num1");
        thread::sleep(Duration::from_millis(2000));
        let mut num2 = num2_arc1.lock().unwrap();
        println!("[1] Got num2");
        *num1 += 1;
        *num2 += 1;
        println!("[1] {}, {}", num1, num2);
    });

    let handle2 = thread::spawn(move || {
        let mut num2 = num2_arc2.lock().unwrap();
        println!("[2] Got num2");
        thread::sleep(Duration::from_millis(2000));
        let mut num1 = num1_arc2.lock().unwrap();
        println!("[2] Got num1");
        *num1 += 1;
        *num2 += 1;
        println!("[2] {}, {}", num1, num2);
    });

    handle1.join().unwrap();
    handle2.join().unwrap();

    println!("After: {:?}, {:?}", num1, num2);
}
```

## Sync & Send

When we use `Rc` instead of `Arc` in the `arc_basic` example above, we will get a **compile error** instead of **runtime error**. Below is the error we will get

```
   Compiling ch16_fearless_concurrency v0.1.0 (/home/eiger/Tutorials/rust-tutorial/chapters/ch16_fearless_concurrency)
error[E0277]: `Rc<i32>` cannot be sent between threads safely
   --> src/mutex_demo.rs:41:41
    |
41  |               let handler = thread::spawn(move || {
    |                             ------------- ^------
    |                             |             |
    |  ___________________________|_____________within this `{closure@src/mutex_demo.rs:41:41: 41:48}`
    | |                           |
    | |                           required by a bound introduced by this call
42  | |                 let number = *number;
43  | |                 println!("[{}] The number is: {}", i, number);
44  | |             });
    | |_____________^ `Rc<i32>` cannot be sent between threads safely
    |
    = help: within `{closure@src/mutex_demo.rs:41:41: 41:48}`, the trait `Send` is not implemented for `Rc<i32>`, which is required by `{closure@src/mutex_demo.rs:41:41: 41:48}: Send`
note: required because it's used within this closure
   --> src/mutex_demo.rs:41:41
    |
41  |             let handler = thread::spawn(move || {
    |                                         ^^^^^^^
note: required by a bound in `spawn`
   --> /home/eiger/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/std/src/thread/mod.rs:691:8
    |
688 | pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    |        ----- required by a bound in this function
...
691 |     F: Send + 'static,
    |        ^^^^ required by this bound in `spawn`

For more information about this error, try `rustc --explain E0277`.
error: could not compile `ch16_fearless_concurrency` (bin "ch16_fearless_concurrency" test) due to 1 previous error
```

This is made possible by the marker trait `std::marker::Send` and `std::marker::Sync`. These two traits don't have actual implementation. They are used only to tell compiler if the type satisfies certain condition.

### `Send`

`Send` allows transference of ownership between threads. Almost all Rust types are `Send`, and all types consisting of `Send` types are automatically `Send`. Exceptions includes `Rc<T>`. `Rc<T>` is not send because the implementation of `Rc<T>` doesn't guarantee safe concurrent update of ref count. Were we allowed to transfer ownership of `Rc<T>` between threads, we could hold an `Rc<T>` in thread 1, clone it and move it to thread 2, in which case both threads can update the ref count concurrently.

`Rc<T>` is not `Send` because that allows an efficient implementation of the rec count mechanism. When `Send` is needed, we should use `std::Sync::Arc`.

By not marking `Rc<T>` as `Send`, there is no way for us to accidentally use `Rc<T>` in a concurrent setting at runtime because such error is reported at compile time.

### `Sync`

`Sync` allows access from multiple threads. This means any type `T` is `Sync` if `&T` is `Send` ("access a value from a thread must be done via a reference to the value"). `Rc<T>` is not `Sync` for the same reason above. Moreover, `RefCell<T>` is not `Sync` because the internal borrow checker of `RefCell<T>` is not thread-safe.

Note that `RefCell<T>` is `Send` whenever `T` is `Send`. In the example below, we move a `RefCell<i32>` inside a thread. This is allowed because `i32` is `Send`, which makes `RefCell<i32>` also `Send`.

```rust
#[test]
fn send_refcell() {
    let val = RefCell::new(40);
    println!("val: {:?}", val);

    let mut val_ref = val.borrow_mut();
    *val_ref += 1;
    println!("val: {:?}", *val_ref);
    // need to drop the mutable ref to val before moving it into thread.
    drop(val_ref);

    let handle = thread::spawn(move || {
        // RefCell<i32> is moved from one thread to another.
        let mut val_ref_thread = val.borrow_mut();
        *val_ref_thread += 1;
        println!("val: {:?}", *val_ref_thread);
    });

    handle.join().unwrap();
}
```

`Mutex<T>` is `Sync`.

## Popular Concurrency Library

## Asynchronous Programming
