+++
date = '2025-09-12T18:20:35-04:00'
draft = true
title = 'LazyVim Cheatsheet for Vim User'
mathjax = false
+++

About half a year ago, I switched from Vim to LazyVim. The experience so far is great: nice UI, nice tools like rg and lazygit. However, I haven't spent much time on learning how LazyVim work (because I'm lazy :D). All I have done is going over [the official LazyVim website](https://www.lazyvim.org/) and the introduction video ([YouTube](https://www.youtube.com/watch?v=N93cTbtLCIM), [BiliBili](https://www.bilibili.com/video/BV1DEy3YvEbb)). Maybe chat with GPT if I want some customized plugins / configs, but nothing more than that. Heck, I don't even know how to run a hello world lua program. In this post, I will go over the stuff a Vim user needs to know to understand how LazyVim work. It will cover a quick start on Lua, NeoVim, and finally LazyVim.

## Lua

### Basic syntax

### Table

### `require()` and module

How path resolution works in lua

## NeoVim

### Config

### Plugin

### What happens in NeoVim, step-by-step from `nv .`

`nv .` will open the neovim, but have you wondered what happens in the process? How is config files read? What is running? etc. We will investigate this process step by step from the very beginning.

## LazyVim

### Plugin

### What happens in LazyVim, step-by-step from `nv .`

## Common use cases

These are common use cases, some may apply to both NeoVim and LazyVim, while others are LazyVim specific.

### Change color theme

### Configure LSP for a language

[Language Server Protocl (LSP)](https://microsoft.github.io/language-server-protocol/) defines a unified interface for editors to interact with language server. A language server is a program that analyze codebase and provide useful functionalities like "find all usage of a variable in the workspace" (with `textDocument/reference` request). We can configure LSP in LazyVim.

### Debug a project with the language DAP

Similar to LSP, [Debug Adapter Protocol (DAP)](https://microsoft.github.io/debug-adapter-protocol//) defines a unified interface for editors to interact with debuggers of different languages. It allows you to launch or attach to a process, and do stuff like "set a breakpoint" or "inspect current stack" within the editor. And similarly, we can configure DAP in LazyVim.
