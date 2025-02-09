---
date: '2024-10-21T21:19:34-04:00'
draft: false
title: 'Rust Cheatsheet'
mathjax: true
---

One-page cheatsheet to refresh my memory on Rust. Many examples are copied from [Rust by Example](https://doc.rust-lang.org/rust-by-example/).

## Tips for Learning Rust

- Think about an error, and figure out how to modify the example code to cause that error. E.g. what line of code do I need to add to make `coerce_static(&lifetime_num)` fail to work in the example below?

    ```rust
    // Make a constant with `'static` lifetime.
    static NUM: i32 = 18;

    // Returns a reference to `NUM` where its `'static`
    // lifetime is coerced to that of the input argument.
    fn coerce_static<'a>(_: &'a i32) -> &'a i32 {
        &NUM
    }

    fn main() {
        {
            // Make a `string` literal and print it:
            let static_string = "I'm in read-only memory";
            println!("static_string: {}", static_string);

            // When `static_string` goes out of scope, the reference
            // can no longer be used, but the data remains in the binary.
        }

        {
            // Make an integer to use for `coerce_static`:
            let lifetime_num = 9;

            // Coerce `NUM` to lifetime of `lifetime_num`:
            let coerced_static = coerce_static(&lifetime_num);

            println!("coerced_static: {}", coerced_static);
        }

        println!("NUM: {} stays accessible!", NUM);
    }
    ```

- Read the source code. Seems like many of them are more concise than I expected.

## Cargo

Cargo is Rust's **build systems** and **package manager**. No more messy Make and CMake!

```bash
# basics
cargo new <project_name>
cargo build                 # build for debug mode
cargo build --release       # build an optimized ver. of the binary
cargo run
cargo check                 # fast way to check for compilation errors

# dependency
cargo add <crate_name>
cargo remove <crate_name>
cargo update

# testing & linting
cargo test [<test_name>]               
cargo bench                 # benchmark
cargo clippy                # linter
cargo fmt                   # format code

# misc
cargo tree                  # show dependency tree
cargo clean                 # remove `target/` directory
```

## Ownership & Scoping Rules

## Structs

## Enum

## Trait