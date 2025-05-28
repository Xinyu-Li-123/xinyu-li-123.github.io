---
date: '2025-05-04T17:20:15-04:00'
draft: true
title: 'Chapter 17.5: Tokio Quick Start'
mathjax: true
---

The chapter on async in the rust book only talks about async from a high level, and all the async utilities are provided in a custom `trpl` crate that hides details of specific runtime. This is nice for learning, but not so if we want to actually write async code in a project.

To write some concrete async code, we need to first choose an async runtime. We will only focus on `tokio` in this post, since it's the most popular async runtime: `tokio` has been downloaded over 312 million times as of 2025/05/04, versus 41.6 million for `async-std`.
