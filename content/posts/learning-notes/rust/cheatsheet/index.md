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

## Naming Convention

This is a list of naming conventions. It's not enforced by the Rust compiler but it's commonly adopted.

- The `new()` method (`fn MyStruct::new(arg1: type1, ...) -> Self`) returns an instance of type `MyStruct`. `new()` is expected to never fail.

- The `build()` method (`fn MyStruct::build(arg1: type1, ...) -> Result<Self, ...>`) builds an instance of type, and return `Result<MyStruct, ...>`. This function carries out some validation, and may fail if the validation fails. E.g. a nonexistent path to config file is provided.

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

## testing

`assert!(is_even(3))`

`assert_eq(triple(3), 9)`

A test that should panic

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic]
    fn zero_div() {
        // 3/0 is invalid
        let res = div(3, 0);
    }
}
```

## Ownership

## Lifetime

## Trait

### Default implementation

```rust
trait Licensed {
    fn licensing_info(&self) -> String {
        "Default license".to_string()
    }
}
```

### `impl`, `Box`, and representing "any type that implement some trait"

Rust enforces that size of type must be known at compile time. This is why you almost never see `str` used directly, b/c it's a variable length string. Instead, the fixed-size `&str` reference is used.

The implication of this rule on function call is as follows:

To represent "any type that implements some trait",

- for function argument, we can use `impl Trait`.

    This is called **static dispatch**. Rust will determine the concrete type of parameter at each function call, i.e. Rust will monomorphize each function call.

- for function return value, we must use `Box<dyn Trait>`.

    This is called **dynamic dispatch**. Instead of concrete type, we return a pointer to value of that type. The pointer size is known at compile time, and the actual type is stored on heap.

    Technically, we can use `impl Trait` as the returned type if there is only one returned type, for example,

    ```rust
    fn static_types() -> impl Any {
        4
    }
    ```

    This could be useful when we want to hide implementation details, and only add restriction on the behavior of the returned type. However, to have true dynamic dispatch, we must use `Box<dyn Trait>`.

Below is an example showing how dispatch works differently for function parameter and return value.

```rust
trait Roll {
    fn roll() -> u8;
}

trait Animal {}

fn random_animal(dice: impl Roll) -> Box<dyn Animal> {
    if dice.roll() < 3 {
        Box::new(Sheep {})
    } else {
        Box::new(Cow {})
    }
}
```

#### More about `impl`

When `impl` appears to the left of `->` function signature, it is equivalent to a generic parameter with a bound, like this

```rust
fn random_animal(dice: impl Roll) -> Box<dyn Animal> {}
fn random_animal<T: Roll>(dice: T) -> Box<dyn Animal> {}
```

`impl` can also be used to the right of `->` as a returned type. We sometimes prefer this over returning a concrete type b/c we don't want to define a named type and only want the caller to know the returned type implement some trait. For example,

```rust
trait Animal {
    fn description() -> String {
        format!("This is an animal")
    }
}

struct Dog;
impl Animal for Dog;

struct Cat;
impl Animal for Cat;

fn get_fav_animal() -> impl Animal {
    // Today my fav animal is Dog
    Dog
    // Maybe tomorrow my fav animal is Cat
    // Cat
}

fn main() {
    let animal = get_fav_animal();
    println!("Fav animal: {}", anima.description());
}
```

For the above def of `get_fav_animal`, the concrete type of `impl Animal` is inferred from the function's definition.

The benefit of returning an `impl Animal` instead of `Dog` is that the caller only need to know *the returned type implements `Animal` trait*. When we change the implementation of `get_fav_animal()`, the caller doesn't need to change how they use the returned value of `get_fav_animal()`, because they always use it as some type that implements `Animal`.

Also, there is no way to write an equivalent signature using generics if `impl` appears in function return type.

```rust
// This is incorrect
fn get_val_animal<T: Animal> -> T {
    Dog
}
```

This is incorrect because `T` is provided by the caller, while the concrete type of `impl Animal` is determined by function definition.

### Trait Bound

We can require a generic type to implement some traits. This is called "trait bound".

```rust
struct Message<T: Display>(T);

fn print_stuff_1<T: Display>(stuff: T) -> i32 {
    println!("#### {} ####", stuff);
    42
}

// equivalent to print_stuff_1
fn print_stuff_2<T>(stuff: T) -> i32 
where T: Display
{
    println!("#### {} ####", stuff);
    42
}
```

## Hashmap shenanigan

### Insert if not exists

```rust
let name2grade: HashMap<&str, Option<u8>> = HashMap::new();
name2grade.entry("Tom").or_insert(None);
```

### Insert default value if not exists

```rust
let name2grade: HashMap<&str, Option<u8>> = HashMap::new();
// default of Option<T> is None
name2grade.entry("Tom").or_default();
```

## iterator

### Commonly used chain of iter methods

Filter + Count

```rust
// a Grade struct representing both numerical score and letter grade
pub struct Grade {
    pub score: f64,
    pub letter: String,
}

pub fn count_letter_grade(grades: &[Grade], letter: &str) -> usize {
    grades.iter().filter(|&grade| grade.letter == letter).count()
}

pub fn count_score_range(grades: &[Grade], score_range: std::ops::Range<f64>) -> usize {
    grades.iter().filter(|&grade| score_range.contains(&grade.score)).count()
}
```

Map

Sum

Map from `Result<T, E>` to `Result<T, F>`

### Collecting an `impl Iterator<Item = Result<T, E>>`

Given an `impl Iterator<Item = Result<T, E>>`, for example `let res = vec![3, 4, 1, 2].iter().map(|v| checked_sub_1(v, v-1))`, `res.collect()` can return two types:

- `Result<Vec<i32>, Error>`: a result that contains either a vector of `i32` or an error

- `Vec<Result<i32, Error>>`: a vector of results that contains either `i32 or error

A full example is below

```rust
use std::fmt::Display;

#[derive(PartialEq, Debug)]
pub enum CheckError {
    UnderflowError(i32)
}

pub fn checked_sub_1(val: &i32) -> Result<i32, CheckError> {
    match val {
        ..1 => Err(CheckError::UnderflowError(*val)),
        _ => Ok(val - 1)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn fn1() -> Result<Vec<i32>, CheckError> {
        let values: Vec<i32> = vec![3,2,1,0];
        values
            .iter()
            .map(checked_sub_1)
            .collect()
    }

    #[test]
    fn test_error_1() {
        assert_eq!(fn1(), Err(CheckError::UnderflowError(0)));
    }
    
    fn fn2() -> Vec<Result<i32, CheckError>> {
        let values: Vec<i32> = vec![3,2,1,0];
        values
            .iter()
            .map(checked_sub_1)
            .collect()
    }

    #[test]
    fn test_error_2() {
        assert_eq!(fn2(), [Ok(2), Ok(1), Ok(0), Err(CheckError::UnderflowError(0))]);
    }
}
```

This is because `collect()` returns a type that implements `FromIterator<Self::Item>`, statically dispatched. The signature of `collect` is below

```rust
pub trait Iterator {
    fn collect<B: FromIterator<Self::Item>>(self) -> B
    where
        Self: Sized;
}
```

Here, `Item = Result<i32, CheckError>`. Furthermore, both `Vec<T>` and `Result<T, E>` implements `FromIterator` trait. Thus, `collect()` can return both types using their `FromIterator` implementation respectively.

- `collect(self) -> Vec<Result<i32, CheckError>>`

    This one is quite straight forward. Given an iterator of `T`, we return a `Vec<T>`. Here, `T = Result<i32, CheckError>`.

- `collect(self) -> Result<Vec<i32>, CheckError>`

    This one is more interesting. To return `Result<Vec<i32>, CheckError>`, we consumes values in iterator to build up the vector, and shortcircuit on the first error. That is, we either creates a vector for all values, or return the first error encountered.

    One catch is that the values are consumed even if an error occur. When an error occur, all values before this error are consumed. For details, see this [Rust By Example page](https://doc.rust-lang.org/rust-by-example/error/iter_result.html)

## Misc

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

### `while let` and nested pattern matching

```rust
let myvec = vec![100, 100, 100, 100]
while let Some(Some(integer)) = myvec.pop() {
    assert_eq!(integer, 100);
}
```

WTF?

- `while let` will keep iterating until `None` is encountered;

- `Vec::pop` will return `Some(T)` if vector contains elements, or `None` if vector is empty.

- `Vec::pop` returns `Some(T)`, so we need another pattern matching, thus the `Some(Some(integer))`.

### Use Test to Structure Tutorial

When reading a tutorial, you may want to write executable codes along with the tutorial. For example, when learning about smart pointer in the rust book, you may want to write code for Box, Drop&Deref, Rc, RefCell respectively. Test is a good way to do this. You can divide each feature into a file, and write executable tests within each file about each feature.

For example, we could have the following folder structure

```
$ tree .
.
├── Cargo.lock
├── Cargo.toml
└── src
    ├── main.rs
    ├── tu_box.rs
    └── tu_deref.rs
```

The file `tu_box.rs` showcase the usage of box

```rust
/// file: tu_box.rs
#[cfg(test)]
mod tests {
    #[test]
    fn simple_box() {
        let b = Box::new(5);
        println!("b = {} ({:?})", b, b);
    }
}
```

and another file `tu_deref.rs`, where we define a struct with custom `Deref` trait implementation

```rust
/// file: tu_deref.rs
use std::ops::Deref;

struct MyStruct {
    val: i32,
}

impl Deref for MyStruct {
    type Target = i32;

    fn deref(&self) -> &Self::Target {
        &self.val
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn simple_deref() {
        let val = 31;
        let my_var = MyStruct { val };
        println!("my_var.val = {}", *my_var.deref());
        assert_eq!(val, *my_var);
        assert_eq!(val, *my_var.deref());
    }
}
```

Just remember to declare these files as mod in `main.rs`.

```rust
/// file: main.rs
mod tu_box;
mod tu_deref;

// main is not strictly necessary if we only need to run the test
fn main() {
    println!("Hello, world!");
}
```

This way, we can call specific tests with

```bash
// cargo test <test_function_name_keyword> -- --nocapture
cargo test simple_box -- --nocapture
cargo test deref -- --nocapture
cargo test simple -- --nocapture
```

The `-- --nocapture` flag tell rustc to redirect the test output to stdout.

### The `?` Operator

TODO: Finish this section

The `?` operator simplifies error handling. It's a unary postfix operator that can only be applied to `Result<T, E>` or `Option<T>`.

- When applied to a value `res` of type `Result<T, E>`,

  - if its `Ok(x)`, `res?` evaluates to `x`. For example,

  - if its `Err(e)`, `res?` returns `Err(e)`.

  As an example,

  ```rust
  fn try_to_parse() -> Result<i32, ParseIntError> {
      let x: i32 = "123".parse()?; // x = 123
      let y: i32 = "24a".parse()?; // returns an Err() immediately
      Ok(x + y)                    // Doesn't run.
  }

  let res = try_to_parse();
  println!("{:?}", res);
  ```

- When applied to a value `opt` of type `Option<T>`,

  - if it's `Some(x)`, `res?` evaluates to `x`,

  - if it's `None`, `res?` returns `None`

  As an example,

  ```rust
  fn try_option_some() -> Option<u8> {
      let val = Some(1)?;
      Some(val)
  }
  assert_eq!(try_option_some(), Some(1));

  fn try_option_none() -> Option<u8> {
      let val = None?;
      Some(val)
  }
  assert_eq!(try_option_none(), None); 
  ```

`?` operator allows us to chain results / options with minimal boilerplate code.
