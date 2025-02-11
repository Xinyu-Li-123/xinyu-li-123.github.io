---
date: '2025-02-11T15:22:51-05:00'
draft: false
title: 'Chapter 15: Smart Pointers'
mathjax: true
---

# Smart Pointers

A smart pointer is a pointer with additional metadata and capabilities, such as counting reference to an object.

Typically, a smart pointer is a struct that implements two traits: 

- `Deref`: allow the smart pointer to behave like a reference. Making functions that takes reference also takes smart pointer.

- `Drop`: properly handle the pointed value when the pointer goes out of scope

## `Box<T>`

A box is a pointer on stack that points to some data on heap.

It's similar to `unique_ptr` in CPP.

When a box goes out of scope, both the pointer on stack and the data it points to on heap will be deallocated.

### Basic Usage

```rust
fn main() {
	let b = Box::new(5);
	println!("b = {}", b);
}
```

### Recursive Types

There are types who contains itself, such as a Node pointing to another node. They are called recursive types. The size of these types is unknown at compile time.

Rust needs to know the size of a type at compile time. As a solution, we store a pointer to the type in the type.

An example would be a node in a singly linked list.

The most intuitive way to define a node won't work

```rust
struct Node<T> {
	value: T,
	next: Option<Node<T>>
}
```

This gives error `recursive type `Node` has infinite size`. Instead, we can use a box to hold the next node.

```rust
// A node in singly linked list.
struct Node<T> {
	value: T,
	// either "null", or pointer to next node
	next: Option<Box<Node<T>>>,
}
```

Below is a struct of singly linked list based on this `Node` type.

```rust
pub struct SLL<T> {
	head: Option<Box<Node<T>>>,
	length: usize,
}

impl<T: Default + Debug> SLL<T> {
	pub fn new() -> SLL<T> {
		SLL { 
			head: None, 
			length: 0 
		}
	}

	pub fn push_front(&mut self, value: T) {
		let new_head = Box::new(Node {
			value, 
			next: self.head.take(),
		});
		self.head = Some(new_head);
		self.length += 1;
	}

	pub fn pop_front(&mut self) -> Option<T> {
		self.head.take().map(|node| {
			self.head = node.next;
			self.length -= 1;
			node.value
		})
	}

	pub fn print_list(&self) {
		// cur_opt is a mutable variable that immutably borrows an Option<Box<Node<T>>>
		let mut cur_opt = &self.head;
		while let Some(cur_node) = cur_opt {
			print!("{:?} -> ", cur_node.value);
			cur_opt = &cur_node.next;
		}
		println!("None");
	}
}

#[allow(dead_code)]
fn recursive_type_demo() {
	let mut list = SLL::new();
	list.push_front(3);
	list.push_front(4);
	list.push_front(5);
	list.push_front(6);
	list.push_front(7);
	list.print_list();
	list.pop_front();
	list.pop_front();
	list.print_list();
}
```

Side note: similar problem occurs in cpp, but with a different error report

```cpp
struct Node {
	int value;
	Node next;
};
```

The `Node` above gives this error 

```bash
sll.cpp:10:7: error: field has incomplete type 'Node'
        Node next;
             ^
sll.cpp:8:8: note: definition of 'Node' is not complete until the closing '}'
struct Node {
       ^
1 error generated.
```

## Deref 

The trait `Deref` has an associated type called `Target`. The implementor of `Deref` will return a `&Target` when calling `deref()`.

```rust
pub trait Deref {
    type Target: ?Sized;

    // Required method
    fn deref(&self) -> &Self::Target;
}
```

Typically, we would define a way to dereference a custom type like this

```rust
struct MyStruct {val: i32}

impl Deref for MyStruct {
	type Target = i32;

	fn deref(&self) -> &Self::Target {
		&self.val
	}
}

#[allow(dead_code)]
fn deref_demo() {
	let val = 31;
	let my_var = MyStruct { val };
	assert_eq!(val, *my_var);
	assert_eq!(val, *my_var.deref());
}
```

Note that `deref` returns a reference to type `Target`, instead of the actual `Target` value. This is due to the ownership system of Rust: if `Target` value is returned, it would be moved out of `self`. `Deref` is typically implemeneted for smart pointer, and we don't want to tranfer ownership when we deref a pointer.

### Deref Coersion

When type A implements `Deref` trait with `Target` type `B`, we can pass a variable of type `&A` to a function that takes `&B`, and Rust will automatically calls `A.deref()` to convert `A` to `&B`.

```rust
// Deref coersion that convert type `A` to type `&B`
struct A {val: B}
struct B {}

impl Deref for A {
	type Target = B;

	fn deref(&self) -> &Self::Target {
		println!("A -> &B");
		&self.val
	}
}
fn accept_b(_val: &B) {
	println!("Accepting a parameter of type &B.")
}

fn abs_deref_coersion_demo() {
	let b = B {};
	let a = A {val: b};
	accept_b(&a);

	println!("Manually calling A.deref()");
	let arb = a.deref();
	accept_b(arb);
}
```

The output is 

```
## Deref Coersion
A -> &B
Accepting a parameter of type &B.
## Manually ref and deref w/ & and *
A -> &B
Accepting a parameter of type &B.
## Manually calling deref()
Manually calling A.deref()
A -> &B
Accepting a parameter of type &B.
```

A useful example is that `String` implements `Deref` with `Target = str`, meaing we can pass `&String` to functions that takes `&str` as parameter. The implementation is actually quite short

```rust
#[stable(feature = "rust1", since = "1.0.0")]
impl ops::Deref for String {
    type Target = str;

    #[inline]
    fn deref(&self) -> &str {
        self.as_str()
    }
}
```

You can even chain deref coersion together, like this 

```rust

// Chain of deref coersion that convert type `D` to type `&F`
struct D {val: E}
struct E {val: F}
struct F {}

impl Deref for D {
	type Target = E;

	fn deref(&self) -> &Self::Target {
		println!("D -> &E");
		&self.val
	}
}

impl Deref for E {
	type Target = F;

	fn deref(&self) -> &Self::Target {
		println!("E -> &F");
		&self.val
	}
}

fn accept_e(_val: &E) {
	println!("Accepting a parameter of type &E.")
}

fn accept_f(_val: &F) {
	println!("Accepting a parameter of type &F.")
}

#[allow(dead_code)]
fn abs_chain_deref_coersion_demo() {
	let f = F {};
	let e = E {val: f};
	let d = D {val: e};
	println!("## Deref Coersion");
	accept_e(&d);
	accept_f(&d);

	println!("## Manually ref and deref w/ & and *");
	accept_e(&*d);
	accept_f(&*&*d);
	
	println!("## Manually calling deref()");
	println!("Manually calling A.deref()");
	let dre = d.deref();
	accept_e(dre);
	println!("Manually calling B.deref()");
	let erf = (*dre).deref();
	accept_f(erf);
}
```

The output is 

```
## Deref Coersion
D -> &E
Accepting a parameter of type &E.
D -> &E
E -> &F
Accepting a parameter of type &F.
## Manually ref and deref w/ & and *
D -> &E
Accepting a parameter of type &E.
D -> &E
E -> &F
Accepting a parameter of type &F.
## Manually calling deref()
Manually calling A.deref()
D -> &E
Accepting a parameter of type &E.
Manually calling B.deref()
E -> &F
Accepting a parameter of type &F.
```

Deref coersion happens at compile time, so no penalty at runtime for using this feature!

### Mutability of Derefe Coersion

Deref coersion is possible when converting

- `&T` to `&U` where `T: Deref<Target=U>`

- `&mut T` to `&mut U` where `T: DerefMut<Target=U>`

- `&mut T` to `&U` where `T: Deref<Target=U>`

Note that `&T` to `&mut U` is impossible, b/c there could be multiple immutable reference to `T` when doing the conversion. If this is allowed, we would end up with one mutable ref and potentially multiple immutable ref to the same `T`, which violate Rust's borrowing rules.

For the same reason, the third conversion is possible, b/c we would go from "only one mutable ref" to "only one immutable ref".

## Drop

Trait `Drop` allows us to define a function `Drop::drop()` that customizes what would happen when a variable goes out of scope.

For variables within the same scope, as they goes out of scope, they are dropped in the reverse order of their definition, i.e. LIFO.

### Early Drop

You might want to call `drop` before the variable goes out of scope. For example, a smart pointer holding a lock may need to be dropped early so that other variables can obtain the lock. Think about PageGuard in BusTub, and how they work when implementing B+Tree.

Manually calling `Drop::drop()` is not allowed, o/w there would be a double-free issue. As an alternative, we can use `std::mem::drop` and pass in the variable to-be-dropped, like `std::mem::drop(my_ptr)`.

To quote from the doc: *This function is not magic; it is literally defined as*

```
pub fn drop<T>(_x: T) {}
```

It moves the argument into the function, thus the argument is automatically dropped before the function returns.

As a result of this implementation, passing in any argument that implements `Copy` trait, such as `i32`, will take no effect, since the argument will be copied into the `std::mem::drop` function.

## `Rc<T>`

To be continued...