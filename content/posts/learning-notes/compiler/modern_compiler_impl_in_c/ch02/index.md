---
date: '2026-01-07T21:39:46-05:00'
draft: true
title: 'Chapter 02. Lexical Analysis'
mathjax: true
---

Given a stream of character (source code), how to group them into a stream of token? This is what lexer does. We use **regular expression** to specify lexical token, and use **finite automata** to implement matching regular expression against a character stream.

## Regular Expression (inline code ver.)

We are given a set `A`

**Alphabet and symbols**: we call the set `A` alphabet, and its element `a` symbol.

**String**: a finite sequence of symbols, such as `"abcd"`.

**Language**: a set of strings, such as `{"abcd", "efg"}`.

**Regular expression (regex)**: same as language. It comes with the following operations

- For each symbol `a`, we denote **`a`** to be the regex of singleton set `{"a"}`

- **Alternation** (op): Given regexs **`M`** and **`N`**, alternation **`M|N`** is a regex of the set `{s | s in M or N}`, i.e. union of the two regex sets

- **Concatenation** (op): Given regexs **`M`** and **`N`**, concatenation **`MN`** is a regex of the set `{s1 + s2 | s1 in M, s2 in N}`, where `s1 + s2` is the concatenation of string `s1` and `s2`.

- **Epsilon `eps`** (regex): The regex of `{""}`, i.e. empty string.

- **Repitition** (op): Given a regex **`M`**, **`M*`**, the repitition of **`M`**, is the closure of **`M|eps`** w.r.t. alternation and concatenation.

- order of precedence: repitition > concatenation > alternation

- some abbreviations

  - **`[abcd]`** = **`a|b|c|d`**

  - **`[a-eA-E]`** = **`[abcdeABCDE]`**

  - **`M?`** = **`M|eps`** (0 or 1)

  - **`M+`** = **`MM*`** (1 or more)

For example,

- **`(0|1)*0`**: elements include `"0"`, `"00"`, `"00010"`, `"01110"`... All 0-1 string ending with 0, or binary number that are multiples of two.

Given a string and a language described by regular expression, we are only interested in **if the string belongs to the language**.

The table below shows how some tokens of C language are matched by regular expression:

| regular expression | what lexer emits|
|-|-|
| `if` | `{return IF;}` |
| `[a-z][a-z0-9]*` | `{return ID;}` |
| `[0-9]+` | `{return NUM;}` |
| `("--"[^"\n"]*"\n")\|(" " \| "\n" \| "\t")` | `{ /*comment or whitespace, do nothing*/ }` |
| `.` | `{error();}` |

Lexer match character stream against this table of regular expression following two rules

- **Longest match**: longest string that can match any regex is taken as next token (i.e. if one char longer, can't match any)

- **Rule priority**: for the matched longest string, we determine its token type by the first matching the first matched regex.

  This is why `.`, which calls `error()`, is the last regex. It is only matched if no regex of any token matches

## Finite Automata

### Deterministic Finite Automata (DFA)

#### Match char stream with regex using DFA

### Nondeterministic Finite Automata (NFA)

### Epsilon move

Epsilon move makes it easier to combine NFAs (alternation, concatenation, repitition).

### Regex to NFA

### NFA to DFA

## Generate lexer program from spec

### Lex / Flex (C)

### Logos (Rust)
