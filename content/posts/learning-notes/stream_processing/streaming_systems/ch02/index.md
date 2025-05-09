---
date: '2025-04-17T12:41:12-04:00'
draft: false
title: 'Chapter 02. The What, Where, When, and How of Data Processing'
mathjax: true
---

<style>
  video {
    width: 100%;
    height: 400px;
  }
</style>

We will read a stream of logs from input, parse it, and compute the sum of score for each team. For demo purpose, we only show the scores of one team.

**Preparation**:

Read from input and parse into key-value pair of (`TeamId`, `Score`)(assume `ParseFn` is given)

```java
PCollection<String> raw = IO.read();
PCollection<KV<Team, Integer>> input = raw.apply(new ParseFn());
```

**What: Transformation**:

Sum over key to get the total score of each team.

```java
PCollection<KV<Team, Integer>> totals = input
  .apply(Sum.integersPerKey());
```

<video controls>
  <source src="images/figures/stsy_0203.mp4" type="video/mp4">
</video>

**Where: Windowing**:

Do the sum for data points collected within each window of 2-minutes in processing time.

```java
PCollection<KV<Team, Integer>> totals = input
  .apply(Window.into(FixedWindows.of(TWO_MINUTES)))
  .apply(Sum.integersPerKey());
```

<video controls>
  <source src="images/figures/stsy_0205.mp4" type="video/mp4">
</video>
