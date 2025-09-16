---
title: 'LeetCode刷题笔记 - 链表'
date: 2024-11-20T22:41:16-05:00
draft: false
mathjax: false
tags: ['Grinding', 'LeetCode']
---

## 技巧

### virtual header

在第一个节点前添加一个虚拟节点`dummy`，这样任意真实节点都有`prev`。这会简化很多算法的实现。

值得注意，这个方法并不适用于任何链表相关题目，对于类似“翻转链表”的题目，使用虚拟头节点反而会使问题更复杂。

### 修改链表

有些看似不可能的空间复杂度优化，可以通过修改链表实现。比如判断回文链表，可以通过翻转后半段链表，以`O(1)`空间复杂度实现。

## 题目

### [19.删除链表的倒数第N个节点](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/)

先使用一个快指针从头走N步，再添加一个从头开始的慢指针，两个指针每次走一步，直到快指针走到底。此时慢指针指向倒数第N个节点。

### [160.链表相交](https://leetcode.cn/problems/intersection-of-two-linked-lists-lcci/)

先分别遍历两链表求出各自的长度，得到长度的差值。长链表先走完差值，两个链表再同时遍历直至相遇或走到结尾。

### [141. Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/description/)

快慢指针，从头节点开始，一个慢指针一次走一步，一个快指针一次走两步，如果在快指针走到底前二者相遇，那么图里有环。

### [142. Linked List Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/description/)

使用快慢指针判断是否有环，快慢指针相遇的点一定在环内。根据指针相遇的点和环的入口，我们可以将链表话分成三个部分：x,y,z。

```
Fast-slow pointers meet at "*"

|--------- x -----------|------ y  ------- \
_____________________________________      |
                     ---|            |     |
                      | |            |     |
                      | |            * ------
                      | |            |     |
                      | |____________|     |
                      |------- z ----------/
```

我们考虑快慢指针分别走过的长度

```
1. Slow = (x + y) + m(y + z)
2. Fast = (x + y) + n(y + z), n > m
3. Fast = 2  *slow

3. => 2 * ((x + y) + m(y + z)) = (x + y) + n(y + z)
   => x + y = (n - 2m) (y + z)
   let k = n - 2m
   => x + y = k(y + z)
   => x = k(y + z) -  y
   => x = (k - 1) (y + z) + z
```

由此可知，从x和z出发，每次走一步，则一定会在环入口相遇。这是因为从起点出发，走(k - 1) (y + z) + z步会到环入口，并且这是x第一次进入环;从快慢指针相遇的点出发，对任意p >= 0，走z + p(y + z)步都可以到环入口。由此可知，当p = k - 1时，x和z会相遇，且因为这是x第一次进入环，而z只在环内，x和z第一次相遇一定在环入口。

### [146. LRU 缓存](https://leetcode.cn/problems/lru-cache/description)

TODO:

