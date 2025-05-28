---
date: '2025-04-21T19:50:00-04:00'
draft: true
title: 'Chapter 02: The Basics'
mathjax: false
---

## Tips

- char type stores **Unicode** of the character. You can use `\u####` to represent a Unicode-encoded character.

- String is a reference to a collection of char's.

  ```java
  String s = "hello";
  String s = "world";
  System.out.println("s: ", s);   // "s: world"
  ```

  In the example above, JVM create both string `"hello"` and `"world"`, and change `s` from pointing to `"hello"` to `"world"`.

- "equal" in java

  For primitive types like `int` or `boolean`, the `==` operator compares values

  For reference variables, which are instances of classes like `String` or `ArrayList`, these variables hold a reference (pointer) to an object in memory, not the object itself. Thus `==` operator compares the pointer value, i.e. whether the two references are referring to the same memory address.

  The proper way to compare whether two reference variables have the same value is to use the `equals` method, such as

  ```java
  String s1 = "Hello";
  String s1 = "HELLO".toLowerCase();
  assertFalse(s1 == s2);
  assertTrue(s1.equals(s2));
  ```

- "return" in a switch statement

  This requires Java >= 14. We can use `yield` within one block of switch to return a value.

  ```java
  int opt = switch (fruit) {
      case "apple" -> 1;
      case "banana" -> 2;
      default -> {
          int code = fruit.hashCode();
          yield code;
      }
  };
  ```

- for each loop

  ```java
  int [] nums = {3, 5, 7, 98};
  int sum = 0;
  for (int n : nums) {
    sum += n;
  }
  ```
