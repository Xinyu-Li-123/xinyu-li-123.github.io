---
date: '2024-11-19T00:54:34-05:00'
draft: false
title: 'LeetCode刷题笔记 - 贪心算法'
mathjax: true
tags: ['Grinding', 'LeetCode']
---

## 区间贪心

### 区间调度问题

**Interval Scheduling Problem (ISP)**: Given a set of nonempty intervals \(I = \{I_k = (s_{I_k}, f_{I_k}) \:|\: k=1,2,\dots,n\}\), find a subset \(OPT(I) \subset I \) s.t. 


\[\begin{align*}
     OPT(I) = 
    \arg\max_{J \subset I} & \quad |J| \\
             \textrm{s.t.} & \quad \forall I_a,I_b \in J, I_a \cap I_b = \emptyset
\end{align*}\]

i.e. \(OPT(I)\) is the largest among all subsets of \(I\) consisting of non-overlapping invervals.

An equivalent (and more intuitive) definition of \(OPT(I)\) is 

> \(OPT(I)\) is the largest subset of \(I\) s.t. for any \(J \in I\) and \(J' \in OPT(I)\), we have \(J \cap J' \not= \emptyset\).

**Algorithm: Earliest Finishing Time**

The solution \(EFT(I) \subset I\) is constructed as follows

1. Sort the intervals by their finish time \(f_k\),
 
2. Pick the first interval \(I_a\), add \(I_a\) in \(EFT(I)\), remove all intervals intersecting with \(I_a\)
 
3. Repeat 2. until no more interval left

What makes this algorithm interesting is this property: 

> For any \(J \in I\) and \(J' \in EFT(I)\), if \(J \cap J' \not= \emptyset\), we have \(f_J \geq f_{J'}\)

**Proof**

Let \(OPT(I)\) be an arbitrary solution to ISP. We prove that \(EFT(I)\) is an optimal solution by constructing an injective mapping from \(EFT(I)\) to \(OPT(I)\). 

If this is true, by property of injectivity, we have \(|EFT(I)| \leq |OPT(I)|\). Since \(OPT(I)\) is an solution to the interval scheduling problem, we have \(|OPT(I)| \leq |EFT(I)|\). This indicates that \(|EFT(I)| = |OPT(I)|\), i.e. \(EFT(I)\) is a solution to ISP.

We define the relation \(h \subset OPT(I) \times EFT(I)\), and will prove that it's an injective mapping: 

> for \(J \in OPT(I)\) and \(J' \in EFT(I)\), \((J, J') \subset h\) if \(J'\) has the earliest finish time among all intervals in \(EFT(I)\) that intersects with \(J\).

1. \(h\) is a mapping

    Existence: Suppose there exists \(J \in OPT(I)\) s.t. no \(J' \in EFT(I)\) satisfies \((J, J') \in h\). By def of relation \(h\), we know that \(J\) doesn't intersect with any \(J' \in EFT(I)\). However, by def of \(EFT(I)\), we must encounter \(J\) at some point in step 2 as the "first interval", thus \(J\) must be added into \(EFT(I)\). This leads to a contradiction.

    Uniqueness: Suppose there exists \(J \in OPT(I)\), distinct \(J', J'' \in EFT(I)\) s.t. \((J, J'), (J, J'') \in h\). By def of \(h\), we know that \(J'\) and \(J''\) has the same finishing time. By def of \(EFT(I)\), we know that \(J' \cap J'' = \emptyset \). This leads to a contradiction.

2. \(h\) is injective

    Suppose there exists \(J_1,J_2 \in OPT(I)\) s.t. \(h(J_1) = h(J_2) = J' \in EFT(I)\). 
    
    WLOG, we assumes \(f_{J_1} \leq s_{J_2}\).

    Since \(h(J_1) = J'\), by the property of \(EFT(I)\), we have \(f_{J_1} \geq f_{J'}\).

    Combining the two inequalities, we have \(f_{J'} \leq f_{J_1} \leq s_{J_2}\), which indicates that \(J' \cap J_2 = \emptyset\). This leads to a contradiction.

This concludes the proof.

### [452. Minimum Number of Arrows to Burst Balloons](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/description/)

我们将气球看作闭区间，将“戳破多个相叠气球”看作“多个闭区间相交，在交集中射一箭”，则题目可以转换成以下问题：

> 对于`points`，最优解`opt_points`是满足以下性质的最小子数组
> 
> 1. 任意`points`中的区间和任意`opt_points`中的区间都有交集 

根据前文所属ISP问题的等价定义，可知该问题等价于ISP。则根据\(EFT\)可以构造出一组最优解。

具体实现思路如下

1. 按结束时间对所有区间排序

2. 从第一个区间开始，取当前区间和所有与之相交的区间，记录箭数+1，跳过这些区间

3. 重复2.直到所有区间都被遍历过。

在理解了ISP的解法后，这道题是简单的。然而没听说过ISP的情况下，很容易尝试一些错误的贪心解法，我第一次就陷入“每次向相交气球最多的区间射箭”的错误思路，结果完全写不出这道题。

### [435. Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/description/)

比较明显的ISP的应用，根据ISP求出的最大不相交子集的补集，就是题解。

### [763. Partition Labels](https://leetcode.com/problems/partition-labels/description/)

Convert each letter into an interval that tightly covers its presence, sort by start index, and greedily iterate-and-merge the intervals

### [56. Merge Intervals](https://leetcode.com/problems/merge-intervals/description/)

略，同763

## 杂项

没什么规律的贪心题目。

### [113. Gas Station](https://leetcode.com/problems/gas-station/description/)

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

