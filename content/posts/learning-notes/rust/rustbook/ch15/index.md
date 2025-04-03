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

This gives error `recursive type`Node`has infinite size`. Instead, we can use a box to hold the next node.

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

In other words, if `A` implements `Deref` with `Target=B`, Rust will find a way to do **implicit type conversion from `&A` to `&B`**. Logically, we can explicitly write out this implicit conversion as `&*(A.deref())`.

A useful example is implicitly convert `&String` to `&str`. `String` implements `Deref` with `Target = str`, meaing we can pass `&String` to functions that takes `&str` as parameter. The implementation is actually quite short

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

To take one step further, you can even chain deref coersion together, like this

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

### Mutability of Deref Coersion

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

A slightly unexpected result of this implementation is that passing in any argument that implements `Copy` trait, such as `i32`, will take no effect. This is because the argument will be copied into the `std::mem::drop` function.

## Reference-counting Pointer `Rc<T>`

The type `Rc<T>` in `std::rc` is a reference-counting pointer. It allows shared ownership of a value of type `T`, allocated in the heap. Similar construct in cpp is `std::shared_ptr<T>`.

The typical usage of `Rc<T>` is to

- create a value on stack

- create the first `Rc<T>` using `Rc::new()`. This will **initialize a `Rc<T>` by copying the value to heap**.

- create more `Rc<T>` using `Rc::clone()`. These `Rc<T>` will **refer to the same value allocated on heap**.

```rust
use std::rc::Rc;

let five = Rc::new(5);

let _ = Rc::clone(&five);
```

Internally,

- When `Rc::new()` is called, ref counter is set to 1

- When `Rc::clone()` is called, ref counter increment by 1

- When the `Rc<T>` goes out of scope, `std::ops::Drop::drop()` is called automatically, which decrement ref counter by 1. If the ref counter reaches 0, the value on heap is deallocated automatically.

> Note that the convention is to use `Rc::clone(&value)` instead of `value.clone()`. This is because most `Clone` implementation will do a deep copy, while `Rc`'s implementation only do shallow copy. Writing the code this way helps emphasize this point.

To get the number of strong referneces, we can call

```rust
Rc::strong_count(&a);
```

### Interior Mutability and `RefCell<T>`

`Rc<T>` provides multiple owning immutable reference to the heap value. Sometimes, we want have multiple owning mutable reference. For example, in a DAG, we can write our code s.t. a node is owned by all its neighbors. It would be convenient to modify the node value as we traverse the graph. `RefCell<T>` provides this feature: we can define an immutable variable of type `RefCell<T>` that points to a value of type `T` on heap, and modify the value using `RefCell::borrow_mut()`. This pattern is called **Interior Mutability**:

- **Interior Mutability**: we hold an immutable reference of an abstraction of a value (`RefCell<T>`), and mutate the interior value (`T`) through this immutable abstraction.

As an example, we can define a list where both the node value and next node pointer is interiorly mutable.

```rust
#[derive(Debug)]
pub enum List {
    Cons(Rc<RefCell<String>>, RefCell<Rc<List>>),
    Nil
}

mod tests {
 use std::ops::Deref;
    use super::*;

    fn mut_val() {
        println!("## Test mutable value in list node");
        let value = Rc::new(RefCell::new("AAA".to_string()));
        let a = Rc::new(List::Cons(Rc::clone(&value), RefCell::new(Rc::new(List::Nil))));
        println!("a: {a:?}");
        *value.borrow_mut() = "BBB".to_string();
        println!("a: {a:?}");
        if let List::Cons(ref_val, _) = Rc::deref(&a) {
            // We have two immutable reference to one i32 value 
            // that allows us to mutate the value
            *ref_val.borrow_mut() = "CCC".to_string();
            println!("a: {a:?}");
        };
        println!("a: {a:?}");
        println!();
    }    

    #[test]
    fn mut_next() {
        println!("## Test mutable next node in list node");
        let a1 = Rc::new(List::Cons(Rc::new(RefCell::new("A1".to_string())), RefCell::new(Rc::new(List::Nil))));
        let a2 = Rc::new(List::Cons(Rc::new(RefCell::new("A2".to_string())), RefCell::new(Rc::new(List::Nil))));

        let b = Rc::new(List::Cons(Rc::new(RefCell::new("B".to_string())), RefCell::new(Rc::clone(&a1))));
        // Initially, b -> a1
        println!("List: {:?}", b);

        // We can change it to b -> a2
        if let List::Cons(_, ref_next) = Rc::deref(&b) {
            *ref_next.borrow_mut() = Rc::clone(&a2);
        }
        println!("List: {:?}", b);
        println!();
    }
}
```

Here, we have two usage of `RefCell`, mixed with `RC`. Let's see how they work

- Node value: `Rc<RefCell<String>>`

 `Rc` allows us to create multiple immutable reference to the underlying `RefCell<String>`, while `RefCell` allows each of these reference to modify the underlying `String`.

 Note that the multiple reference can't modify `RefCell<String>`. They can only modify the `String` holded by `RefCell`.

- Next node: `RefCell<Rc<List>>`

 `RefCell` allows the current node to change the next node to point to. The next node itself can also be pointed by multiple nodes, thanks to `Rc`.

### Memory Leak and `Weak<T>`

Such a reference-counting pointer can lead to cyclic reference like this

```rust
#[derive(Debug)]
pub enum List {
    Cons(Rc<RefCell<String>>, RefCell<Rc<List>>),
    Nil
}

mod tests {
 use std::ops::Deref;
    use super::*;

 #[test]
 fn test_cyclic_ref() {
  // ####### block 1
  let a = Rc::new(List::Cons(Rc::new(RefCell::new("A".to_string())), RefCell::new(Rc::new(List::Nil))));
  let b = Rc::new(List::Cons(Rc::new(RefCell::new("B".to_string())), RefCell::new(Rc::clone(&a))));
  // b -> a
  println!("List: {:?}", b);

  // ####### block 2
  // link a to b, causing cyclic ref
  if let List::Cons(_, ref_next) = Rc::deref(&a) {
   *ref_next.borrow_mut() = Rc::clone(&b);
  }
  
  // ####### block 3
  // uncomment this line to cause a stack overflow runtime error
  // b -> a -> b, 
  // - compile successfully
  // - but cause stack overflow at runtime
  // println!("List: {:?}", b);
 }
}
```

In this example, A points to B, and B points to A. This creates a cyclic reference. Technically, if we keep record of the referrer of the heap value in `Rc<T>`, and we are able to check if the referrer is in scope, cyclic reference won't cause any memory leak: when dropping, we simply check if all referrers are valid to decide if we should deallocate value on heap. However, `Rc<T>` only count the number of reference. This means, by the end of block 2, both A and B have ref count of 2. When both are dropped, the ref count only goes to 1. This leads to memory leak.

Memory leak doesn't stop the program from compiling. Rust compiler is not able to check this kind of error, because the ref count is managed *at runtime*. If we uncomment block 3, we will get a stack overflow runtime error.

To avoid this problem, we can use the smart pointer `Weak<T>`. It's similar to `Rc<T>`, except the reference to heap value is non-owning. Internally, `Rc<T>` keep track of two kinds of counter

- strong count: number of owning reference (`Rc<T>`) to the heap value

- weak count: number of non-owning reference (`Weak<T>`) to the heap value

the heap value is deallocated only if strong count goes to 0, even if weak count is above 0.

`Rc<T>` and `Weak<T>` are conceptually similar to hard link and soft link in file system:

- when a file is deleted, its hard link counter decrement by 1

- a file is not actually deleted unless #hard link goes to 0

- when #hard link goes to 0, the file can be deleted even if #soft link is nonzero.

  - in this case, the soft link becomes invalid

- if hard link to directory is allowed, it would create a cycle in the directory tree, similar to how a cyclic reference can be created by `Rc<T>`

To use `Weak<T>`, we would

- create a `Weak<T>` from `Rc<T>` using `Rc::downgrade(rc: &Rc<T>) -> Weak<T>`

- access the value in `Weak<T>` as an `Option<Rc<T>>` using `Weak::upgrade(&self) -> Option<Rc<T>>`. The option is `None` if the value is deallocated, similar to how we would access an invalid soft link in file system.

As an example,

```rust
#[derive(Debug)]
pub enum ListWeakRef {
    Cons(Rc<RefCell<String>>, RefCell<Weak<ListWeakRef>>),
    Nil
}

mod tests {
 use std::ops::Deref;
    use super::*;

 #[test]
 fn test_weak_ref() {
  let a = Rc::new(ListWeakRef::Cons(Rc::new(RefCell::new("A".to_string())), RefCell::new(Weak::new())));
  let b = Rc::new(ListWeakRef::Cons(Rc::new(RefCell::new("B".to_string())), RefCell::new(Rc::downgrade(&a))));
  // b -> a
  println!("a: {:?}", a);
  println!("b: {:?}", b);

  // b -> a -> b
  if let ListWeakRef::Cons(_, ref_next) = Rc::deref(&a) {
   *ref_next.borrow_mut() = Rc::downgrade(&b);
  }
  println!("a: {:?}", a);
  println!("b: {:?}", b);

  if let ListWeakRef::Cons(_, ref_next) = Rc::deref(&a) {
   let a_next = ref_next.borrow();
   // since it's weak ref, no problem
   println!("a.next = {:?}", a_next.upgrade());
  }
  
  println!();
 }
}
```

The following will be printed

```
a: Cons(RefCell { value: "A" }, RefCell { value: (Weak) })
b: Cons(RefCell { value: "B" }, RefCell { value: (Weak) })
a: Cons(RefCell { value: "A" }, RefCell { value: (Weak) })
b: Cons(RefCell { value: "B" }, RefCell { value: (Weak) })
a.next = Some(Cons(RefCell { value: "B" }, RefCell { value: (Weak) }))
```

The actual content of `Weak<T>` won't be printed, since `upgrade()` needs to be called to access that content.

To get the number of weak referneces, we can call

```rust
Rc::weak_count(&a);
```

## `Cow` and `std::borrow`

`std::borrow::Cow` represents a copy-on-write pointer. It can holds either a borrowed value or an owned value. When it holds a borrowed value, and we modify the underlying value, `Cow` will call the `std::borrow::ToOwned::to_owned()` method of the borrowed value, which will creates owned data from borrowed data, usually by cloning.

This is the signature of `Cow`

```rust
pub enum Cow<'a, B>
where
    B: 'a + ToOwned + ?Sized,
{
    Borrowed(&'a B),
    Owned(<B as ToOwned>::Owned),
}
```

It is an enum with two variants: `Cow::Borrowed` and `Cow::Owned`. When the internal value is borrowed, the `Cow` enum is `Borrowed`; when its owned, the `Cow` enum is `Owned`.

As an example, we can write a function that test if a cow pointer's value is borrowed or owned:

```rust
fn is_borrowed_or_owned<B: ToOwned + ?Sized>(cow_ptr: &Cow<B>) {
    match cow_ptr {
        Cow::Borrowed(_) => {
            println!("cow's value is borrowed");
        }
        Cow::Owned(_) => {
            println!("cow's value is owned");
        }
    }
}
```

Below is an example where we create a page wrapped in `Cow::Owned()`, and copy it using `Cow::Borrowed()`

```rust
fn cow_basic() {
    let page: Cow<[i32]> = Cow::Owned(vec![0, 1, 2]);
    let mut page_copy = Cow::Borrowed(&page[..]);
    println!("cow's value: {:?}", page_copy);
    is_borrowed_or_owned(&page_copy);
    page_copy.to_mut()[0] = 33;
    println!("cow's value: {:?}", page_copy);
    is_borrowed_or_owned(&page_copy);
}
```

We can actually let the compiler decide if `Cow` should be initialized as `Owned` or `Borrowed` by passing the value to `Cow::from()`

```rust
fn cow_from_basic() {
    let page: Cow<[i32]> = Cow::from(vec![0, 1, 2]);
    let mut page_copy = Cow::from(&page[..]);
    println!("cow's value: {:?}", page_copy);
    is_borrowed_or_owned(&page_copy);
    page_copy.to_mut()[0] = 33;
    println!("cow's value: {:?}", page_copy);
    is_borrowed_or_owned(&page_copy);
}
```
