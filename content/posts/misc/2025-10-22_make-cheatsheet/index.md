---
date: '2025-10-22T10:50:02-04:00'
draft: false
title: 'Make Cheatsheet'
---

For details and precise definition, refer to [the official GNU Make manual](https://www.gnu.org/software/make/manual/make.html)

## Basic Concepts

Compiled from [this ChatGPT session](<https://chatgpt.com/c/68f8f0a2-9148-8322-b400-860628fdcace>)

### The Smallest Makefile

GNU Make is a build system. It allows developers to define **rules** in the form of

> Do **something** to generate **target files** if **prerequisite files** exist`

The simplest Makefile looks like this:

```Makefile
hello.txt: name.txt
 @echo "Hello, $(shell cat name.txt)" > hello.txt
```

This file create a `hello.txt` file using the command `@echo "Hello, $(shell cat name.txt)" > hello.txt` if the file `name.txt` exists.

In general, a **rule** is defined by three items as follows:

```
target_1 target_2 ...: prerequisite_1 prerequisite_2 ...
<TAB> recipe
```

- **targets**:

  Target files to generate.

  `hello.txt` in the example above.

- **prerequisites**:

  Prerequisite files that must exist to generate target file.

  `name.txt` in the example above.

- **recipe**:

  Bash command to execute to generate target file. Typically use prerequisite files as input.

  `@echo "Hello, $(shell cat name.txt)" > hello.txt` in the example above

### Default target & phony targets

### Variables

```
CFLAGS = -O0
CFLAGS += -g
```

### Automatic variables

### Pattern rules

### Avoid unnecessary rebuild

Make uses file timestamp to determine if rebuild is needed. This gives a conservative estimate (?)

#### Order-only prerequisites

### Functions

### Include and splitting Makefiles

### Error handling

### Control flow

## Nice-to-have features

These are the features that are nothing essential, but can make our life easier.

### Built-in rules

## An example to put things together

TODO: Add a nested folder of Makefiles for a C project here

```
src/foo/foo.make
src/bar/foo.make
Makefile
```

## Common pitfalls

### Tabs

Recipe lines **must start with a tab**. Space indent won't compile.

## Common code snippets

### Silence a command

Prepend `@`

TOOD: Why we want to do this?

### Dry run: print bash commands but don't execute

`make -n`
