---
date: '2025-10-24T16:23:58-04:00'
draft: true
title: 'Design Pattern Cheatsheet'
---

This is my note on [refactoring.guru](https://refactoring.guru/) that summarize each design pattern, along with code example I encountered in the past.

## Why Patterns?

The following list are what we want to achieve with design pattern. This list is not mutual exclusive: some may overlap, some may be a result of others combined, but all are worth mentioning.

- Modularity

- Extensibility

- Abstraction

  Hide dirty impl below an API. Users (may also be developer that uses this package) only need to know the input, output, and expected behavior of the API

  Less mental burden for devs

  Can swap the actual impl without modifying how people use the API

- Less likely to make mistake

  E.g. RAII, so that we don't accidentally forget to free resources.

- Ease of Use

  E.g. thread pool, so that we don't need to manage thread resources ourselves.

- Ease of Debugging

  - Modularity -> Unit test a module

  - Extensibility -> Mock test (when testing module A that depends on an external service like database, use a mock database)

## Creational Patterns

## Structural Patterns

## Behavioral Patterns

## Others

### Config

## Language-specific Patterns

Design patterns that makes assumption about what the programming language provide. E.g. RAII is extremely important for C++, but not as meaningful for Java.

### ???
