---
date: '2025-11-30T23:58:52-05:00'
draft: false
title: 'Common Design Pattern in Compute System'
---

Some design pattern appears in very different subfield of Computer Science. This post is a list of such patterns.

## Cache

## Pipeline

## Separation of Control Path and Data Path

In digital circuit, in distributed system (e.g. GFS), etc.

## Pool

Thread pool in server, Buffer pool in database

Pre-allocate resource from system in advance, and use a data structure to let others obtain and release resource without construction / destruction.

Centralized management, good for ???

## Log-structured / Append-only

Write at random position can be costly

Process one write at a time can be costly

Introducing, append-only / log-structured.

We use a log to record "write requests" (append new write request to log), and process a batch of requests at a time.

Also the added benefit of having historical version of data.

Can be found in

- database (LevelDB and Log-Structured Merge Tree)

- storage system (Log-structured File System, SSD Flash Translation Layer?)
