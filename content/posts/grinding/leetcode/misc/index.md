
---
title: 'LeetCode刷题笔记 - 杂项'
date: 2024-11-20T22:41:16-05:00
draft: false
mathjax: true
tags: ['Grinding', 'LeetCode']
---

## KMP

### Implement substr

## 单调栈

### [739. Daily Temperatures](https://leetcode.com/problems/daily-temperatures/description/)

一个自底向上单调递增的栈，储存`(day, temperature)`。入栈前先把所有小于当前温度的天弹出，同时记录这些天和当前天的差距。

### [496. Next Greater Element I]()

Constraint: Solution must be `O(nums1.length + nums2.length)`

### [503. Next Greater Element II](https://leetcode.com/problems/next-greater-element-ii/description/)

For array `nums`, duplicate `nums` to `double_nums = nums + nums`, and do the monotone stack thing as in 496.

### [42. Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/description/)

1. Scan from left to right to find all ponds with left bar <= right bar;

2. Scan from right to left to find all ponds with left bar > right bar;

3. Sum the two results to get total pond size.

Don't really need a monotone stack...