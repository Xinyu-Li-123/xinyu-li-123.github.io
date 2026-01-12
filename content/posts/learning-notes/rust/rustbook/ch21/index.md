---
date: '2025-09-12T23:52:32-04:00'
draft: true
title: 'Chapter 21: Macro'
mathjax: true
---

This is not really part of the rust book. It's from the book [](), which discusses macro in Rust in details.

C/C++ macro is processed after tokenization, Rust macro is processed after AST construction

There is also something called token trees that sits between token and AST. All tokens excepts `{,},(,),[,]` are token trees.
