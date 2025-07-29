---
date: '2024-11-19T00:54:34-05:00'
draft: false
title: 'LeetCode刷题笔记 - 双指针'
mathjax: true
tags: ['Grinding', 'LeetCode']
---

## 双指针

### [11. 盛最多水的容器](https://leetcode.cn/problems/container-with-most-water/description)

维护左右指针，

- 如果左侧值小于右侧值，左指针右移到更高的柱子

- 如果右侧值小于左侧值，右指针左移到更高的柱子

- 如果两侧值相等，两侧都移动

每次移动后，得到的面积有可能更大。这是因为面积计算公式为

```
area = ( q - p ) * min(height[p], height[q])
       -- t1 --    -----      t2       -----
```

无论右移p还是左移q,`t1 = (q - p)`都会减小。只有让`t2 = min(height[p], height[q])`增大，移动后的面积才可能增大。

- 当两值不同，移动较小值到更大的值能让`t2`增大

- 当两值相同，必须同时移动两者才能让`t2`可能增大

### [15. 三数之和](https://leetcode.cn/problems/3sum/description)

## 快慢指针

