---
date: '2024-10-21T21:19:34-04:00'
draft: false
title: 'Rust Cheatsheet'
mathjax: true
---

One-page cheatsheet to refresh my memory on Rust. Many examples are copied from [Rust by Example](https://doc.rust-lang.org/rust-by-example/).


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