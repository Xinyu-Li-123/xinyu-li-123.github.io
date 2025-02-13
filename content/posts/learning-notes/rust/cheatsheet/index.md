---
date: '2024-10-21T21:19:34-04:00'
draft: false
title: 'Rust Cheatsheet'
mathjax: true
---

One-page cheatsheet to refresh my memory on Rust. Many examples are copied from [Rust by Example](https://doc.rust-lang.org/rust-by-example/).

## Tips for Learning Rust

- Learn by fixing error: 

    [rustlings](https://github.com/rust-lang/rustlings) is a great example that adopts this method of learning by fixing error.

    Think about an error, and figure out how to modify the example code to cause that error. E.g. what line of code do I need to add to make `coerce_static(&lifetime_num)` fail to work in the example below?

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

## Rust By Example, but in one post.

### Create a slice

```rust
let a = [1,2,3,4,5];
let slice_a = &a[1..4];
assert_eq!([2,3,4], slice_a);
```

### Destruct a tuple

```rust
let point = (3.9, 4.5, "positive");
let (x, y, label) = point;
```

### Function parameter's mutability

When describing a function's parameter, we can use the word "mutability", and its variants, in these situations:

- an immutable parameter of `MyStruct`

    commonly used, input is read-only

- an immutable parameter of an immutable reference to `MyStruct`

    commonly used, need to take ownership of input, i.e. move it inside the function

- a mutable parameter of `MyStruct`, 

    rarely used

- an immutable parameter of mutable reference to `MyStruct`, 

    commonly used, need to modify input

- a mutable parameter of immutable reference to `MyStruct`

    rarely used

- a mutable parameter of mutable reference to `MyStruct`

    rarely used

Below is a concrete example that uses all the types of parameters above:

```rust
struct MyStruct {}
fn wtf(
    a: &MyStruct,
    // commonly used, need to take ownership of input, i.e. move it inside the function
    b: MyStruct,
    // rarely used
    mut c: MyStruct, 
    // commonly used, need to modify input
    d: &mut MyStruct, 
    // rarely used
    mut e: &MyStruct, 
    // rarely used
    mut f: &mut MyStruct,

) {
    println!("WTF???");
}

#[allow(dead_code)]
fn wtf_demo() {
    let my_struct_1 = MyStruct {};
    let mut my_struct_2 = MyStruct {};
    let my_struct_3 = MyStruct {};
    let mut my_struct_4 = MyStruct {};
    wtf(
        &MyStruct{}, 
        MyStruct{}, 
        my_struct_1, 
        &mut my_struct_2, 
        &my_struct_3, &mut my_struct_4);
}
```

### Use `..` to destruct part of struct to create another struct

```rust
let your_order = Order {
    name: String::from("Hacker in Rust"),
    count: 1, 
    ..order_template_1
};
```