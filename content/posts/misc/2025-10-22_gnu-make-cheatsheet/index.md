---
date: '2025-10-22T10:50:02-04:00'
draft: false
title: 'GNU Make Cheatsheet'
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

This file create a `hello.txt` file using the command `@echo "Hello, $(shell cat name.txt)" > hello.txt` if the file `name.txt` exists (`@` suppress printing the command to stdout )

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

### Default target

By default, make builds the **first target** it sees in the first rule of the file.

This can be overridden with the special variable `.DEFAULT_GOAL`

```make
.DEFAULT_GOAL := help

app: main.o util.o
 $(CC) $(CFLAGS) -o $@ $^

main.o: main.c
 $(CC) $(CFLAGS) -c $<

util.o: util.c
 $(CC) $(CFLAGS) -c $<

help:
 @echo "Targets:"
 @echo "  app   - build the executable"
 @echo "  clean - remove build artifacts"
```

### Phony target

A normal target is the name of a file. A phony target, instead, is not a file name but a name for a recipe to be executed.

We need phony target to avoid a conflict with a file of the same name, and to improve performance.

Consider this makefile

```make
clean:
  rm *.o temp
```

We would want `make clean` to clean the files every time we run it. However, if there is another file named `clean`, `make clean` won't execute the recipe at all. This is because the file `clean` exists, and it has no prerequisite, so it's considered already up to date.

To avoid this issue, we can make `clean` a prerequisite of a special target `.PHONY`,

```make
.PHONY: clean
clean:
  rm *.o temp
```

This way, `make clean` will always execute the recipe.

Here are some common phony targets

```make
.PHONY: all
all: app docs
```

### Automatic variables

Given target and prerequisite of

```make
out.o: src.c src.h
  xxx
```

We can use these variables in the recipe

- `$@`: "out.o" (target)

- `$<`: "src.c" (first prerequisite)

- `$^`: "src.c src.h" (all prerequisites, deduped)

- `$+`: prerequisites (all, with duplication)

- `$?`: prerequisites (new ones, those with newer timestamp than targets)

- `$*`: stem in pattern rules

    ```make
    %.o: %.c
    ```

    `$*` is `foo` in `foo.c`

### Pattern rules

Write one recipe that applies for many similarly named files.

We use `%` as a wildcard. Each recipe may contain exactly one `%`

```make
%.o: %.c
  $(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@
```

If we have `main.c`, `utils.c`, `core.c`, this is equivalent to writing three recipes

```make
main.o: main.c
  $(CC) $(CPPFLAGS) $(CFLAGS) -c main.c -o main.o

utils.o: utils.c
  $(CC) $(CPPFLAGS) $(CFLAGS) -c utils.c -o utils.o

core.o: core.c
  $(CC) $(CPPFLAGS) $(CFLAGS) -c core.c -o core.o
```

### Variables

#### Assignment

There are various types of assignment when defining a variable

- Recursive (deferred) expansion: `=`

    Right-hand side is expanded when used (deferred)

    ```make
    .PHONY: all

    A = foo 
    B = $(A) bar 
    A = baz

    all:
      @echo \'$(B)\'
    ```

    `make` gives `'baz bar'`

- Simple (immediate) expansion: `:=`

    Right-hand side is expanded when defined (immediately)

    ```make
    .PHONY: all

    A = foo 
    B = $(A) bar 
    A = baz

    all:
      @echo $(B)
    ```

    `make` gives `'foo bar'`

- Conditional set: `?=`

    Set variable if it isn't already set (by env, command line, or earlier in the file)

    ```make
    .PHONY: all

    C ?= default value

    all:
      @echo \'$C\'
    ```

    `make` gives `'default value'`; while `C='my C value' make` gives `'my C value'`.

    Also, conditional set is deferred, so given makefile below

    ```make
    .PHONY: all

    A = foo
    C ?= $(A)
    A = bar

    all:
      @echo \'$C\'
    ```

    `make` gives `'bar'`.

- Append: `+=`

    Append RHS to LHS. Inherit the evaluation timing of LHS var: if LHS is defined with immediate (deferred) assginment, RHS is evaluated immediately (deferred)

    E.g. deferred append

    ```make
    .PHONY: all

    A = old A val
    B = B val
    B += $(A)
    A = new A val

    all:
      @echo \'$B\'
    ```

    `make` gives `'B val new A val'`

    E.g. immediate append

    ```make
    .PHONY: all

    A = old A val
    B := B val
    B += $(A)
    A = new A val

    all:
      @echo \'$B\'
    ```

    `make` gives `'B val old A val'`

- Exec shell command and assign to foo: `!=`

    ```make
    foo != echo fooo
    ```

#### Referencing variables

When referencing a variable, we use `$(VAR)`

#### Precedence of assignment

1. command line

2. `override` in makefile, such as

    ```make
    override CFLAGS := -O2 -g
    ```

3. Makefile assignments

4. Environment

5. Built-in defaults

#### Substitution reference

When referencing a variable, we can do substitution.

```make
SRC := main.c foo.c bar.c
OBJ := $(SRC:%.c=%.o)
```

`OBJ` becomes `main.o foo.o bar.o`

This is equivalent to

```make
SRC := main.c foo.c bar.c
OBJ := $(patsubst %.c,%.o,$(SRC))
```

### Avoid unnecessary rebuild

GNU Make uses file timestamp to determine if rebuild is needed. This gives a conservative estimate: given a target, if all its prerequisites are older than the target, the target don't need rebuild

#### Order-only prerequisites

Normally, a rebuild of a target is triggered if one of the following holds

- the target doesn't exist

- one prereq is newer than target

- one prereq is missing

  Make will try to build the prereq. If that succeeds, we got a prereq newer than target, which triggers a rebuild

- one prereq is `.PHONY`

However, there are cases when we only need the prerequiste to exists, but don't want its timestamp to trigger rebuild. For example, we need a `build/` directory to exists before building, but touching the folder (updating its timestamp) should not trigger a rebuild.

We call these types of prerequisites as **order-only prerequisites**, and use a pipe `|` to separate normal and order-only prereqs.

```make
target: normal_prereq_1, normal_prereq_2 | order_only_prereq_1, order_only_prereq_2
  xxx
```

For example, we can make `build/` directory an order-only prereq

```make
build/%.o: src/%.c | build/

build/:
  mkdir -p $@
```

Or we can require a certain tool to exists before building

```make
site: content/* | bin/hugo
  bin/hugo -s .

bin/hugo:
  curl -L -o $@ https://example/hugo && chmod +x $@
```

### Functions

Make's functions are expanded by make (not shell) into strings. The format is

```make
$(func_name arg1,arg2,...)
```

#### Commonly used functions

- `$(patsubst pattern,repl,text)`: pattern substitution with `%`
  
    `$(patsubst %.c,%.o,src/a.c src/b.c)` -> `src/a.o src/b.o`

- `$(subst from,to,text)`: literal text replace
  
    `$(subst foo,bar,foo.c foo.h)` -> `bar.c bar.h`

- `$(filter patterns...,text)`: keep matches
  
    `$(filter %.c %.h,main.c notes.txt)` -> `main.c`

- `$(filter-out patterns...,text)`: drop matches
  
    `$(filter-out %.tmp,a.o b.tmp c.o)` -> `a.o c.o`

- `$(wildcard pattern...)`: expand to existing files
  
    `$(wildcard src/*.c)` -> `src/a.c src/b.c`

- `$(addprefix p,LIST)` / `$(addsuffix s,LIST)`: add path parts
  
    `$(addprefix build/,$(OBJS))` -> `build/a.o ...`

- `$(dir names)` / `$(notdir names)` / `$(basename names)` / `$(suffix names)`: path pieces
  
    `$(suffix foo.c bar.cpp)` -> `.c .cpp`

- `$(foreach v,LIST,body)`: loop over words
  
    `$(foreach f,$(SRCS),$(patsubst %.c,%.o,$(f)))`

- `$(if cond,then[,else])`: conditional expansion
  
    `CFLAGS += $(if $(DEBUG),-g,)`

- `$(strip x)` / `$(sort LIST)` / `$(words LIST)` / `$(word n,LIST)`:
  whitespace, de-dupe, counts, indexing
  
    `$(words a b c)` -> `3`

- `$(shell cmd)`: run a shell command, capture stdout
  
    `GITREV := $(shell git rev-parse --short HEAD)`

- `$(info ...)` / `$(warning ...)` / `$(error ...)`: diagnostics
  
    `$(error missing compiler)`

#### Less commonly used functions

- `$(findstring needle,haystack)`: return `needle` if it’s a literal substring of `haystack`, else empty

    `$(findstring foo,src/foo.c)` -> `foo`

- `$(wordlist s,e,LIST)` / `$(firstword LIST)`: slice words `s..e` (1-based, inclusive) / get the first word

    `$(wordlist 2,3,a b c d)` -> `b c`  
    `$(firstword a b c)` -> `a`

- `$(abspath names)` / `$(realpath names)`: make absolute paths syntactically (no filesystem) / canonicalize using the filesystem (resolves symlinks)

    `$(abspath ./src/../inc)` -> `/abs/path/inc`  
    `$(realpath ./link/to/file)` -> `/abs/path/target`  *(if symlink exists)*

- `$(join LIST1,LIST2)`: pairwise concatenate words (position 1 with 1, 2 with 2, ...)

    `$(join a b, 1 2)` -> `a1 b2`

- `$(call macro,arg1,arg2,...)`: invoke a user-defined “macro” (a variable whose body uses `$(1)`, `$(2)`, ...)

    `define RULE`  
    `$(1): $(2)`  
    `endef`  
    `$(call RULE,app.o,app.c)` -> `app.o: app.c`

- `$(eval text)`: parse `text` now as if it were written in the Makefile (generate vars/rules dynamically)

    `$(eval OBJS := $(patsubst %.c,%.o,$(SRCS)))`

- `$(origin VAR)` / `$(flavor VAR)` / `$(value VAR)`: introspection of a variable’s source, kind, and raw text

    `$(origin CFLAGS)` -> `file`  
    `$(flavor A)` -> `simple`  
    `A = $(B)` ⇒ `$(value A)` -> `$(B)`

- `$(file >path,text)` / `$(file >>path,text)`: write/append to a file during expansion

    `$(file >build/stamp, ready)`  
    `$(file >>build/manifest.txt,$(OBJS))`

### Include and splitting Makefiles

When writing code, we don't want to cram all source code into one file. Instead, we want to split the code into multiple files, and reference other files in a file.

This applies to Makefile as well. We can split the build into small, topic-focused files, and stitch them together with `include` keyword. For example, we can have a makefile dedicated to flags, one for rules, or a collection of makefiles for each sub-module.

#### Example

Here is the folder structure

```
codebase/
├── Makefile
├── mk
│   └── flags.mk
```

We have a "main" makefile at `codebase/Makefile`

```make
include $(wildcard mk/*.mk)

.PHONY: all run clean

all: build/main

SRC := $(wildcard src/*.c)
INCLUDE_FOLDER := include/
INCLUDE_HEADERS := $(wildcard $(INCLUDE_FOLDER)/*.h)
OBJ := $(patsubst src/%.c,build/%.o,$(SRC))

CC := gcc

build/%.o: src/%.c $(INCLUDE_HEADERS) | build/
 $(CC) $(CFLAGS) -I$(INCLUDE_FOLDER) -c $< -o $@

build/main: $(OBJ)
 $(CC) $(CFLAGS) $^ -o build/main

run: build/main
 ./$<

build/:
 mkdir -p $@

clean:
 rm -rf build/
include mk/flags.mk
```

and a makefile for flags at `codebase/mk/flags.mk`

```makefile
CFLAGS := -Wall
CFLAGS += -O3
```

### Error handling

### Control flow

#### If

"If equal" flow:

```make
ifeq ($(CC),clang)
  CFLAGS += -Weverything
else ifeq ($(CC),gcc)
  CFLAGS += -Wall -Wextra
else
  $(warning Unknown CC='$(CC)'; using generic warnings)
  CFLAGS += -Wall
endif
```

"If def" flow:

```make
ifdef DEBUG
  CFLAGS += -O0 -g
endif

ifndef PREFIX
  PREFIX := /usr/local
endif
```

We can also use the `$(if condition, then, else)`, such as

```make
CFLAGS += $(if $(findstring sanitize,$(FEATURES)),-fsanitize=address,)
OUTDIR  := $(if $(OUT),$(OUT),build)
```

#### Loop

Make doesn't have a typical loop statement as in C, but it can iterate over texts via functions, using the `$(foreach var, list, text)` function.

Here is the logic of `foreach` function

1. expand `list`, and split int words on whitespace

2. expand `text` once per item in list, with `$(var)` variable set to that item.

Here is an example

```make
SRCS := foo.c bar.c baz.c
OBJS := $(SRCS:.c=.o)

$(foreach o,$(OBJS),$(eval $(o)_FLAGS := -DOBJ=$(o)))
```

#### Control flows within Recipe

Within recipe, we can use the typical shell control flows, such as

```make
deploy:
 @if [ -z "$(HOST)" ]; then \
   echo "HOST is required" >&2; exit 2; \
 fi
 @rsync -a build/ "$(HOST):/srv/app/"
```

## Nice-to-have features

These are the features that are nothing essential, but can make our life easier.

### Built-in rules

e.g. c source code to object of same name

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
