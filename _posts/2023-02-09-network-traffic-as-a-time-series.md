---
layout: math_post
title: Network Trace as a Time Series / Stochastic Process
---

In this post, we will discuss how a network trace can be represented as a time series, i.e. a stochastic process. Then, we will analyze the [NetShare model]() using our framework.

## Intuition

A network trace is just a sequence of packets (captured on a node), and a packet is just a set of values (IP address, port number, etc). Practically, we can use a pcap file or a [table](https://en.wikipedia.org/wiki/Panel_data) to represent a network trace. Then, why am I writing this post?

The thing is, we don't really care about a single network trace, we care about the **pattern** hidden inside. For example, the frequency of source IP address, or the long-term dependency between packets. To analyze this pattern rigorously, we need a mathematical formulation of network traces.

Intuitively, a good mathematical model should be able to capture these patterns in network traces:

1. **Statistical pattern**

    The distribution of packet size, inter-arrival time, IP, port, protocol, flow size, etc.

2. **Temporal pattern**

    How certain property change over time. Examples are traffic volume, traffic burstiness, packet size, inter-arrival time. 

Note the subtle difference between **the distribution of packet size** and **the change of packet size over time**. Given a network trace, to analyze the distribution of packet size, we consider each observation (size of a captured packet) as an **independent** sample of an underlying distribution. In contrast, the temporal change of packet size require us to drop the assumption of independence between samples, and consider the correlation of sizes of different packets. This will become clearer when we have a concrete math model.

## Network Trace as a Time Series

### Stochastic Process
Given a probability space $$(\Omega, \mathcal{F}, \mathcal{P})$$ and a measurable space (state space) $$(\mathcal{S}, \Sigma)$$, a **stochastic process** is a collection of $$S$$-valued random variables $$X=\{X_t\}_{t=1,...,T}$$ indexed by $$t$$.[^1] We assume that $$X_t$$'s are identically distributed, but not necessarily independent.

A natural choice of $$t$$ is time, and $$X_t$$ is thus a random variable representing the values observed at time t.

In practice, we care about three things: 
- the state space $$S$$
- the distribution of $$X_t$$
- the correlation between $$X_t$$'s. 

### Time Series
Given a stochastic process $$X=\{X_t\}_{t=1,...,T}$$, a **time series** $$D=\{D_t\}_{t=1,...,T}$$ is a realization of $$X_t$$ ($$D$$ is for data). 

Whereas the stochastic process $$X_t$$ is a collection of random variables (measureable functions from $$\Omega$$ to $$S$$), a time series is a collection of values in state space $$S$$.

One can analyze time series data to infer properties of the underlying stochastic process, that is distribution of r.v. and temporal dependence between r.v.'s.

### Network Trace and Network Traffic Process
A **network trace** $$D$$ is a time series. It is sampled from a stochastic process, which we will refer to as the **Network Traffic Process**. 

The state space $$S$$ contains all header values and derived values of interest. For example, 

$$S=\{(srcip,\, dstip,\, srcport,\, dstport,\, proto)\} \in \mathbb{\{0,1\}}^{32+32+16+16+16+16}$$ 

We can also add values derived from the observation to the state space, such as packet length or attack type.

### Network Trace and Panel Data

Here, we will bridge the panel data representation of network trace to our definition.

A network trace can be represented as a [panel data](https://en.wikipedia.org/wiki/Panel_data) (table) $$D = (D^i_t)$$ for state $$i=1,...,M$$ and time $$t = 0,...,T$$. We can use $$D^i$$ to represent the $$i^{th}$$ column of the panel, and $$D_t$$ the $$t^{th}$$ row. 

Here, the column $$D_t$$ is the packet captured at time $$t$$, whereas row $$D^i$$ is the temporal evolution of state $$i$$ (e.g. first bit of source ip address).

Using our time-series definition of network trace, we can see that 
- the state space is $$M$$ dimension.
- $$D_t$$ is a sample from $$X_t$$, the stochastic process at time $$t$$.

## [Unfinshed] Implication of the Model


This section will talk about how we can better understand network traffic using the theory of stochastic process and time series.

A raw network trace is a sample of an unknown network traffic process. Our goal is to ?? generate another sample from the same process ??.

To evaluate the fidelity of generated data is to ???

what are the special properties of network traffic?
- discrete value with no simple numeric semantic
- long-term dependency, self similarity, burstiness


## [Unfinished] NetShare, from a Time Series Perspective

The biggest problem with netshare is that it only learn the statistical pattern of the so-called metadata (five-tuple).


[^1]:Note the difference between a **stochastic process** and a **realization  of a stochastic process** (sample, observation). Some people define a time series as a stochastic process, while others define it as a realization of a stochastic process. 
