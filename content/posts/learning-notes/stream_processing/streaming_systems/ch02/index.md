---
date: '2025-04-17T12:41:12-04:00'
draft: false
title: 'Chapter 02. The What, Where, When, and How of Data Processing'
mathjax: true
---

We will read a stream of logs from input, parse it, and compute the sum of score for each team.

**Preparation**:

```java
PCollection<String> raw = IO.read();
PCollection<KV<Team, Integer>> input = raw.apply(new ParseFn());
```

**What: Transformation**:

```java
PCollection<KV<Team, Integer>> totals = input
  .apply(Sum.integersPerKey());
```

<iframe style="width: 100%; height: 400px" src="http://www.streamingbook.net/static/images/figures/stsy_0203.mp4
"></iframe>

**Where: Windowing**:

```java

```
