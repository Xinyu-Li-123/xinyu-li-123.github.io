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

This post explains transformation, trigger, watermark, and accumulation of a streaming system using Apache Beam model.

We will read a stream of logs from input, parse it, and compute the sum of score for each team. For demo purpose, we only show the scores of one team.

## Preparation

Read from input and parse into key-value pair of (`TeamId`, `Score`)(assume `ParseFn` is given)

```java
PCollection<String> raw = IO.read();
PCollection<KV<Team, Integer>> input = raw.apply(new ParseFn());
```

## What: Transformation

Sum over key to get the total score of each team.

```java
PCollection<KV<Team, Integer>> totals = input
  .apply(Sum.integersPerKey());
```

<video controls>
  <source src="images/figures/stsy_0203.mp4" type="video/mp4">
</video>

## When: Windowing

Group data into certain windows, and process each window. This make it possible to practically handle an infinite stream of data.

Sum for data points collected within each window of 2-minutes in event time.

```java
PCollection<KV<Team, Integer>> totals = input
  .apply(Window.into(FixedWindows.of(TWO_MINUTES)))
  .apply(Sum.integersPerKey());
```

<video controls>
  <source src="images/figures/stsy_0205.mp4" type="video/mp4">
</video>

## Trigger

The sums computed in the figures above are stored internally. To emit it to downstream, we need a trigger.

Triggers tell us **when in processing time should results of each window be materialized (output to next transform)**. Each specific output for a window is called a *pane* of the window. Whenever a trigger fires for a window, we output the pane of that window.

### Types of repeated update triggers

There are two types of triggers:

- Repeated update triggers

  Periodically materialize updated pane for a window as its contents evolve.

- Completeness triggers

  Materialize a pane for a window only after the input for that window is believed to be complete. Ideally, this means all inputs of that window are received. Practically, we will use a watermark to provide an estimate of when all inputs are received.

We will discuss repeated update triggers here, and completeness triggers later after introducing watermark.

- Per-record trigger

  Trigger that fires with every new record

  ```java
  PCollection<KV<Team, Integer>> totals = input
    .apply(Window.into(FixedWindows.of(TWO_MINUTES))
                 .triggering(Repeatedly(AfterCount(1))))
    .apply(Sum.integersPerKey());
  ```

  <video controls>
    <source src="images/figures/stsy_0206.mp4" type="video/mp4">
  </video>

The downside of this trigger is that there will be too much output when dealing with large-scale data. To deal with this, we can emit panes only after some processing time delay (e.g. 2 minutes). There are two approaches to this: aligned delay and unaligned delay

- Aligned delay triggers

  Starting from time 0, trigger every 2 minutes in processing time. The trigger fires at the same time for each window.

  ```java
  PCollection<KV<Team, Integer>> totals = input
    .apply(Window.into(FixedWindows.of(TWO_MINUTES))
                 .triggering(Repeatedly(AlignedDelay(TWO_MINUTES))))
    .apply(Sum.integersPerKey());
  ```

  This is like micro-batching streaming system. The pros is predictability: the panes are updated regularlly. The cons is that **all updates happen at once, which results in bursty workloads**. Greater peak provisioning is required to handle such workloads. Using an unaligned delay trigger solves this issue.

  <video controls>
    <source src="images/figures/stsy_0207.mp4" type="video/mp4">
  </video>

- Unaligned delay trigger

  For each window, starting from the time when first input of the window is received, trigger every 2 minutes in processing time. The trigger fires at different time for each window.

  ```java
  PCollection<KV<Team, Integer>> totals = input
    .apply(Window.into(FixedWindows.of(TWO_MINUTES))
                 .triggering(Repeatedly(UnalignedDelay(TWO_MINUTES))))
    .apply(Sum.integersPerKey());
  ```

  <video controls>
    <source src="images/figures/stsy_0208.mp4" type="video/mp4">
  </video>

  Unaligned delay trigger **spreads the workload more evenly across processing time**. For this reason, it's typically the better choice than aligned delay trigger for large-scale processing.

## When: Watermark

To achieve (some level of) completeness, we need watermark. It answer the question **when in processing time are all inputs to a window received**. In practice, watermark only provides an estimate of the time of completeness, but a good estimate if designed correctly. It is a monotonically increasing function \(f(P) \to E\) that maps from processing time \(P\) to event time \(E\), meaning that **all events before event time \(E\) should arrive at processing time \(P\)**.

There are two types of watermarks

- Perfrect watermark

  If we have perfect knowledge of data, we can know exactly when in processing time all data have arrived

- Heuristic watermark

  Use a heuristic to estimate when in processing time all data have arrived.

  For example, we may provide an estimate like this
  \[
    f(P) = \max_{\text{events observed before \(P\)}} \text{event.event_time} + \text{2 min}
  \]

  That is, at processing time \(P\), we estimate all events before the max event time we have observed so far, minus 2 minutes, have arrived. For example, if current processing time is 12:02, and among all events observed so far, 12:01 is the largest event time, we estimate that all events before 11:59 have arrived.

An example usage of watermark may look like this in Apache Beam

```java
PCollection<KV<Team, Integer>> totals = input
  .apply(Window.into(FixedWindows.of(TWO_MINUTES))
                .triggering(AfterWatermark())
  .apply(Sum.integersPerKey());
```

The figure below compares a perfect watermark with a heuristic watermark. Note how data 9 is missed in the window `[12:00, 12:02)` when using heuristic watermark.

<video controls>
  <source src="images/figures/stsy_0210.mp4" type="video/mp4">
</video>

Many use cases requires knowing when the data is completely received for each window. E.g. partial join.

Watermarks also have some problems

- Too slow: the emission of a window can take too long for two reasons

  1. It simply takes too long for all data to arrive within the window. The window `[12:00, 12:02)` in the left diagram of figure above (perfect watermark) is a good example. It takes around 9 minutes for the first emission to happen.

  2. If previous window has a data with late processing time, the emission of current window can also take too long even if it completes very early. Window `[12:02, 12:04)` in the left diagram of figure above (perfect watermark) is a good example: while all data for window `[12:02, 12:04)` arrives at `12:07`, the emission only happens at `12:09` because there is a data 9 in previous window `[12:00, 12:02)` that arrives late in processing time.

  The takeaway is this: it's not ideal to depend on completeness to emit output from a latency perspective.

- Too fast: for heuristic watermark only, the emission can happen too early and miss some late data.

## When: Early/On-Time/Late Triggers

Repeated updated trigger has low latency but no guarantee of completeness, while watermark has completeness but poor latency. We can combine both trigger and get the best of both worlds. Apache Beam achieves this by allowing us to add repeated update triggers on both size of watermark

The panes are thus categorized into three types

- Zero or more early panes: generated by a repeated update trigger before watermark is reached. This solves the "too slow" problem of watermark.

- A single on-time pane: generated by a completeness trigger.

- Zero or more late panes: generated by a repeated update trigger after watermark passes on late data. This solves the "too fast" problem of watermark.

An example usage of early/on-time/late trigger would look like this

```java
PCollection<KV<Team, Integer>> totals = input
  .apply(Window.into(FixedWindows.of(TWO_MINUTES))
                .triggering(AfterWatermark()
                              .withEarlyFirings(AlignedDelay(ONE_MINUTE))
                              .withLateFirings(AfterCount(1)))
  .apply(Sum.integersPerKey());
```

<video controls>
  <source src="images/figures/stsy_0211.mp4" type="video/mp4">
</video>

One side effect of these triggers is that the output pattern is normalized: whereas the perfect and heuristic watermark's pattern are drastically different, their output patterns are quite similar, and both resembles that of a repeated update trigger.

## When: Allowed Lateness for Garbage Collection

In the above usecase of heuristic watermark, we must maintain the state of all past windows, since we don't know when all late data of the windows will arrive. This quickly becomes a problem for large-scale data due to the sheer amount of old, useless window state.

Let watermark function be \(f(P) \to E\). For event time window \([E_1, E_2)\), we estimate all data of the window to arrive before the watermark \(P_2 = f(E_2)\). We accept late data for the window until processing time \(P_{late} = f^{-1}(E_2 + delay)\). \(P_{late}\) is called the **horizon** of the window.

The code and figure below shows how to apply a 1 minute allowed lateness.

```java
PCollection<KV<Team, Integer>> totals = input
  .apply(Window.into(FixedWindows.of(TWO_MINUTES))
                .triggering(AfterWatermark()
                              .withEarlyFirings(AlignedDelay(ONE_MINUTE))
                              .withLateFirings(AfterCount(1)))
                .withAllowedLateness(ONE_MINUTE)
  .apply(Sum.integersPerKey());
```

<video controls>
  <source src="images/figures/stsy_0212.mp4" type="video/mp4">
</video>

It may feel weird to define the allowed lateness using watermark function. After all, the most obvious method would be to simply add delay to the watermark, i.e. \(P_{late} = P_2 + delay\). The problem with this intuitive approach is that processing time is not a reliable estimate of event time.

To illustrate this, we can think about the example heuristic watermark:

\[
  f(P) = \max_{\text{events observed before \(P\)}} \text{event.event_time} + \text{2 min}
\]

Below is a concrete example that shows the output of this watermark function. The pipeline stalls from 12:03 to 12:13, and recovers at 12:04. thus no new events are observed during the stall. The watermark output thus stays the same during the stall.

> Note: "pipeline stall" is not that different from a "large network delay": both result in "no event seen within a long period of processing time".

| Processing Time | Observed Max Event Time | Watermark |
|-----------------|----------------------|------------------|
| 12:00           | 11:59                | 11:57            |
| 12:01           | 12:00                | 11:58            |
| 12:02           | 12:01                | 11:59            |
| 12:03 (stall)   | 12:01                | 11:59            |
| 12:13 (stall)   | 12:01                | 11:59            |
| 12:14           | 12:03                | 12:01            |
| 12:15           | 12:06                | 12:04            |

Let's see how a 2-min allowed lateness for event time window `[11:57, 11:59)` work. At processing time 12:02, the observed max event time is 12:01. Using watermark function \(f\), we estimate that all events before 11:59 has arrived. Thus, the watermark for the event time window `[11:57, 11:59)` is processing time 12:02. But how long in processing time should we wait for late data of this window? Let's assume there is an event within the window arriving at 12:09, but is only processed at 12:14 due to the stall.

- Bad idea: \(P_{late} = P_{end} + \text{2 min}\)

  Using this approach, we would accept late data until processing time 12:02 + 2 min = 12:04. However, our system stalls until 12:04. We would thus miss the late data arriving at 12:09.

- Good idea: \(P_{late} = f^{-1}(E_{end} + \text{2 min})\)

  Using this approach, we would accept late data until processing time
  \(
    f^{-1}(\text{11:59} + \text{2 min}) = f^{-1}(\text{12:01}) = \text{12:14}
  \)

  Since our watermark function evolves only as we observe more events, our estimate take into account the effect of the stall. We are thus able to incorporate the late data arriving at 12:09.

## How: Accumulation

How should each pane of a window be outputed? More specifically, how can we use each pane to gradually refine the final result of the window? There are three approaches

- Discarding: discard results from previous pane. Last pane doesn't reflect final result, summation of all panes reflects final result

- Accumulating: output sum of all previous results in the pane. Last pane reflects final result, summation of all panes doesn't reflect final result

- Accumulating and retracting: output both the sum of all previous results, and how previous pane can be cancelled. Last pane reflects final result, summation of all panes reflects final result

For example,

| Pane               | Discarding | Accumulating | Accumulating & Retracting |
|--------------------|------------|--------------|----------------------------|
| Pane 1: inputs=[3] | 3          | 3            | 3                          |
| Pane 2: inputs=[8, 1] | 9       | 12           | 12, –3                     |
| Final pane         | <div style="color: red">9</div>          | 12           | 12                         |
| Sum of all panes   | 12         | <div style="color: red">15</div>           | 12                         |

Here is an example of discarding accumulation

```java
PCollection<KV<Team, Integer>> totals = input
  .apply(Window.into(FixedWindows.of(TWO_MINUTES))
                .triggering(AfterWatermark()
                              .withEarlyFirings(AlignedDelay(ONE_MINUTE))
                              .withLateFirings(AfterCount(1)))
                .discardingFiredPanes()
  .apply(Sum.integersPerKey());
```

<video controls>
  <source src="images/figures/stsy_0213.mp4" type="video/mp4">
</video>

Here is an example of accumulating and retracting accumulation

```java
PCollection<KV<Team, Integer>> totals = input
  .apply(Window.into(FixedWindows.of(TWO_MINUTES))
                .triggering(AfterWatermark()
                              .withEarlyFirings(AlignedDelay(ONE_MINUTE))
                              .withLateFirings(AfterCount(1)))
                .accumulatingAndRetractingFiredPane()
  .apply(Sum.integersPerKey());
```

<video controls>
  <source src="images/figures/stsy_0214.mp4" type="video/mp4">
</video>
