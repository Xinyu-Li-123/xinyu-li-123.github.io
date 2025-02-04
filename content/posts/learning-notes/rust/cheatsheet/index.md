---
date: '2024-10-21T21:19:34-04:00'
draft: false
title: 'Rust Cheatsheet'
mathjax: true
---

One-page cheatsheet to refresh my memory on Rust. Reading note of the *The Rust Programming Language*.


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

## Ownership (ch4)

## Structs (ch5)

## Enum and Pattern Matching (ch6)

## Packages, Crates, and Modules (ch7)

## Common Collections (ch8)

## Error Handling (ch9)

## Generic Types, Traits, and Lifetimes (ch10)

## Tests (ch11)

## Closures and Iterators (ch13)