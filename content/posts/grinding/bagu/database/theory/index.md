---
title: "数据库原理"
date: 2024-11-21T01:17:58-05:00
draft: false
mathjax: true
tags: ['Grinding', '八股', '数据库']
---

以下八股主要基于 15-445 的课程内容（slide + note）

## SQL 语法

### 关系模型 & 关系代数

（喜欢考但没啥用的东西）1-NF，2-NF，3-NF，BNF

### 现代 SQL

## 存储

## 缓存池

#### 缓冲池的页面淘汰算法为什么使用 LRU-K，而非 LRU

扫描一张巨大的表时，会有新的页被不断写入，且多数页在短时间内不会被再次访问。如果我们使用 LRU,常被访问的页会被淘汰。

因此，我们使用 LRU-K

- 对于访问次数小于 K 的页，我们优先淘汰

- 对于访问次数大于等于 K 的页，我们按倒数第 K 次的访问时间排序，淘汰最老的页。

LRU-K 的实现方式是

## 索引

### 哈希表

### B+树

### LSM 树

### 索引上的并发控制

## 算法 / 算子

### 排序合并

### 优化方法

#### 谓词下推

## 事务（Transaction）与并发控制

### ???

READ COMMITTED, ...

Phantom read, ...

### 两阶段锁

### Timestamp Ordering Concurrency Protocol

### MVCC

## Logging

### Write-Ahead Logging

## Recovery
