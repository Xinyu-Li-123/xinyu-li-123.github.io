---
title: 'LeetCode 刷题笔记 - 常用的 Rust 代码'
date: '2026-01-05T19:51:47-05:00'
draft: true
mathjax: true
tags: ['Grinding', 'LeetCode']
---

## Common Data Structures

### Vec

**Init**

```rust
let mut v: Vec<i32> = vec![];
let v = vec![0; n];   // n zeros
let v = vec![vec![0; n]; m]   // a mxn 2d array (m rows, n cols)
```

**Ops**

```rust
v.push(x);
let last = v.pop();   // Option<T>

for x in &v {}
for x in v.iter() {}
for x in v.iter_mut() { *x += 1; }

for (i, x) in v.iter().enumerate() {}
```

**Sort**

```rust
let mut v: Vec<i32> = vec![-3, 4, 42, 1];

// sort in ascending order
v.sort();
assert_eq!(v, [-3, 1, 4, 42]);

// sort in descending order (cmp comes from impl of Ord trait)
v.sort_by(|a, b| b.cmp(a));
assert_eq!(v, [42, 4, 1, -3]);

// ascending sort by absolute value of key
v.sort_by_key(|a| a.abs());
assert_eq!(v, [1, -3, 4, 42]);

// sort by descending order, but 42 is smaller than all other numbers
v.sort_by(|a, b| match (*a == 42, *b == 42) {
    (true, false) => std::cmp::Ordering::Greater,
    (false, true) => std::cmp::Ordering::Less,
    _ => b.cmp(a),
});
assert_eq!(v, [4, 1, -3, 42]);
```

### String

`std::string::String` is UTF-8-encoded string. It can't be simply indexed with `s[i]`. Instead, indexing needs to be done with `s.as_bytes()` or `s.chars().collect()`.

```rust
let s: String = "abc".to_string();
let t: &str = s.as_str();

let bytes: &[u8] = s.as_bytes();
let chars: Vec<char> = s.chars().collect();

// If you know for sure the string slice is ascii, you can do this
let s = "hello";
let sub = &s[1..4];

// However, such indexing will fail if index boundary doesn't land on UTF-8 boundary, 
// Such as this one
// let s = "abc你好e";
// let sub = &s[1..4];
```

**Why `let sub = &s[1..4]` instead of `let sub = s[1..4]` (source: [doc](https://doc.rust-lang.org/std/ops/trait.Index.html))?**

Indexing operations like `container[index]` is actually syntax sugar for

```rust
*std::ops::Index::index(&container, index)
```

where `container` implements the trait `std::ops::Index` who has a method

```rust
fn index(&self, index: Idx) -> &Self::Output`
```

Therefore, `container[index]` is of type `Output`.

Thus, the desugared code for `s[1..4]` would evaluate to a value of type `str`, which is `unsized` and thus can't be compiled. Therefore, we need a reference `&s[1..4]` (i.e. `&(s[1..4])`).

Also, since `str` implements `std::ops::Index` but `&str` doesn't, Rust will do autoderef when we call `std::ops::Index::index(...)` on `s`. So `let sub = &s[1..4]` is actually desugared into

```rust
let sub = &*(std::ops::Index::index(&*s, 1..4))`
```

**Iteration**

```rust
for &c in s.as_bytes() {
  // c: u8
}

for ch in s.chars() {
  // ch: char
}

for (i, &ch) in s.char_indices() {
  // i is byte index of this char, so it is not necess 1, 2, 3, 4, ...
}

for (k, ch) in s.chars().enumerate() {
  // ch is k'th character in s
}
```

**Concatenation**

```rust
let mut out = String::new();
out.push('a');
out.push_str("bc");
assert_eq!(out, "abc".to_string());

let parts = vec!["a", "bb", "ccc"];
let out = parts.join("-");
assert_eq!(out, "a-bb-ccc".to_string());

// Convenient but slower
let out = format!("{}_{}", "foo", "bar");
assert_eq!(out, "foo_bar".to_string());

```

**Other useful methods**

```rust
let c: u8 = b'k';
assert!(c.is_ascii_digit());
assert!(!c.is_ascii_alphabetic());
assert!(c.is_ascii_lowercase());

// c is the k'th letter in lowercase alphabet, i.e. k offset from 'a'
let k: usize = (c - b'a') as usize;

let ok: bool = s.contains("needle");
let pos: Option<usize> = s.find("needle");

for token in s.split_whitespace() {}
let parts: Vec<&str> = s.split(',').collect();

let t = s.trim();
```

**char vs byte**: char is Unicode code point while byte is raw data of `u8`.

These are chars: `'a'`, `あ`, `'你'`, `'\n'`. These are bytes: `b'a'`, `b'\n'`.

### HashSet

```rust
```

### HashMap

**Init and Ops**

```rust
use std::collections::HashMap;

let mut freq: HashMap<u8, i32> = HashMap::new();
let mut freq = HashMap::<u8, i32>::new();
let mut freq: HashMap<u8, i32> = HashMap::with_capacity(26);

let old: Option<i32> = freq.insert(b'a', 3); // return Option<V>, old value if existed
freq.insert(b'b', 5);
freq.insert(b'c', 2);
assert_eq!(freq, HashMap::from([(b'a', 3), (b'b', 5), (b'c', 2)]));

let k = b'a';
if let Some(vref) = freq.get(&k) {
    assert_eq!(*vref, 3);
}
if let Some(vref) = freq.get_mut(&k) {
    // vref: mutable ref to value of key k
    assert_eq!(*vref, 3);
    *vref += 1;
    assert_eq!(*vref, 4);
}

let no_k = b'd';
assert!(!freq.contains_key(&no_k));

let removed: Option<i32> = freq.remove(&b'c');
assert_eq!(removed, Some(2));

// Use entry to handle "present vs missing" without double lookup
// - and_modify: modify if present
// - or_insert: insert value if abscent
// - or_insert_with: insert return value of a function with no arg if abscent
// - or_insert_with_key: insert the return value of a function with key as arg if abscent

// insert if abscent
let x = b'd';
*freq.entry(x).or_insert(0) += 1;
assert_eq!(freq, HashMap::from([(b'a', 4), (b'b', 5), (b'd', 1)]));

// insert if abscent, modify if present
let x = b'a';
freq.entry(x).and_modify(|v| *v += 100).or_insert(1);
assert_eq!(freq, HashMap::from([(b'a', 104), (b'b', 5), (b'd', 1)]));

assert_eq!(freq.len(), 3);
assert!(!freq.is_empty());
freq.clear();
assert!(freq.is_empty());
```

For example,

```rust
let hay = "aabbccssaaaacc";
let mut freq: HashMap<char, i32> = HashMap::new();
for c in hay.chars() {
    *freq.entry(c).or_insert(0) += 1;
}
println!("freq: {:?}", freq);
```

**Iteration**

```rust
freq.iter();
freq.iter_mut();    // (&K, &mut V), immut ref to key, mut ref to value
freq.into_iter();   // the map can't be used after calling this

freq.keys();
freq.into_keys();   // the map can't be used after calling this

freq.values();
freq.values_mut();
freq.into_values();   // the map can't be used after calling this
```

For example, convert a map of `char -> freq` to a vector of `(freq, char)`, and sort by freq desc then char acs

```rust
let freq = HashMap::from([(b'c', 3), (b'b', 5), (b'a', 3)]);
let mut items: Vec<(i32, u8)> = freq.into_iter().map(|x| (x.1, x.0)).collect();
items.sort_by(|a, b| {
    let first_cmp = b.0.cmp(&a.0);
    match first_cmp {
        Ordering::Equal => a.1.cmp(&b.1),
        _ => first_cmp,
    }
});
assert_eq!(items, [(5, b'b'), (3, b'a'), (3, b'c')]);
```

**Filter**

```rust
pub fn retain<F>(&mut self, f: F)
where
  F: FnMut(&K, &mut V) -> bool
```

Update entry value with `f`, and keep only entry where `f(key, value)` return true.

For example, decrease value by 1, and keep only those above 2.

```rust
let mut freq = HashMap::from([(b'a', 4), (b'b', 3), (b'c', 2)]);
freq.retain(|_, v| {
    *v -= 1;
    *v > 2
});
assert_eq!(freq, HashMap::from([(b'a', 3)]));
```

#### Examples

**Frequency counter**

```rust
for x in nums {
    *m.entry(x).or_insert(0) += 1;
}
```

**Two-sum map (value -> index)**

```rust
pub fn two_sum(nums: Vec<i32>, target: i32) -> Option<(i32, i32)> {
    use std::collections::HashMap;

    // m: target - x -> index of x
    let mut m: HashMap<i32, usize> = HashMap::new();
    for (i, &num) in nums.iter().enumerate() {
        if let Some(&j) = m.get(&num) {
            return Some((i as i32, j as i32));
        }
        m.insert(target - num, i);
    }
    None
}
```

**Decrease value by 1, and delete on reaching zero**

```rust
let mut freq = HashMap::from([(b'c', 1), (b'b', 3), (b'a', 2)]);
match freq.entry(b'c') {
    Entry::Occupied(mut e) => {
        let v = e.get_mut();
        *v -= 1;
        if *v <= 0 {
            e.remove();
        }
    }
    Entry::Vacant(_) => {}
}
assert_eq!(freq, HashMap::from([(b'b', 3), (b'a', 2)]));
```

### Deque

```rust
```

### Heap

```rust
```

## Common Code Snippets

### Initialize a 2d array

```rust
let mut grid = vec![vec![0; m]; n];
```

### Linked List

```rust
```

### Tree

`node: Option<Rc<RefCell<TreeNode>>>`

```rust
```

### Sort by specific cmp

```rust
```
