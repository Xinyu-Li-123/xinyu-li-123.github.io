---
date: '2026-02-04T15:19:23-05:00'
draft: false
title: '记一次 SSH 登录的问题'
---

**TLDR: 假如远程服务器上的`.bash_profile`有 bug，导致 login shell 崩溃、无法用 SSH 登录，可以通过在适当的时机按下`Ctrl+C`，在登录之后、执行到 bug 之前的时间窗口打断`.bash_profile`的加载。**
