---
date: '2026-01-06T05:26:26-05:00'
draft: true
title: 'Some desugared rust code snippet'
---

In Rust, it seems to be a common practice to first define a very fundamental method as a trait, and then implement some more ergonomic methods based on such trait (like how iterator works in cpp?). For learning purpose, it would be helpful to understand what the desugared code actually look like, so that it's easier to reason about Rust code.

## For loop <=> IntoIterator

Source: [The Rust Reference: Iterator loops](https://doc.rust-lang.org/reference/expressions/loop-expr.html#r-expr.loop.for)

A `for` loop is equivalent to a `loop` expression containing a match expression as follows:

```rust
for PATTERN in iter_expr {
    /* loop body */
}
```

is equivalent to

```rust
{
    let result = match IntoIterator::into_iter(iter_expr) {
        mut iter => loop {
            let mut next;
            match Iterator::next(&mut iter) {
                Option::Some(val) => next = val,
                Option::None => break,
            };
            let PATTERN = next;
            let () = { /* loop body */ };
        },
    };
    result
}
```

Notes

- `IntoIterator::into_iter(iter_expr)` calls the `IntoIterator::into_iter` implementation of `iter_expr`, and returns a specific iterator converted from `iter_expr`

## While let loop <=> Match

## Result-related

## Option-related
