---
date: '2024-11-19T00:54:34-05:00'
draft: false
title: 'LeetCode刷题笔记 - 贪心算法'
mathjax: true
tags: ['LeetCode', 'Grinding']
---

## 贪心算法

### [113. Gas Station](https://leetcode.com/problems/gas-station)

思路：

1. 从第`i`个加油站移动，需要满足`diff[i] = gas[i] - cost[i] >= 0`;

2. 从第`i`个加油站移动一圈，需要对任意`k=0,1,...,n-1`，满足`sum(diff[i: i + k]) >= 0`

    此时的思路是对于`i=0,1,..,n-1`，尝试从`diff[i]`一路加下去。如果和一直不小于零，则可以从第`i`个加油站出发；如果出现负数和，则尝试从`diff[i+1]`加下去。

    这个解法是\(O(n^2)\)，还得优化。

3. （贪心）局部最优推导全局最优

    如果`sum(diff[i: i + k]) >= 0 for all k=0,1,..,m-1`，但`sum(diff[i: i + m]) < 0`，那么从`i`到`i+m-1`中任何一点出发，加到`i+m`都会小于零。

    > 证明（反证法）：
    > 假如存在`i < j < i + m`使得`sum(diff[j: i + m]) >= 0`。由于`sum(diff[i: i + m]) < 0`，可以推出`sum(diff[i: j]) < 0`。
    > 
    > 根据条件`sum(diff[i: i + k]) >= 0 for all k=0,1,..,m-1`，取`k=j-i`，可得`sum(diff[i: j]) >= 0`。矛盾。