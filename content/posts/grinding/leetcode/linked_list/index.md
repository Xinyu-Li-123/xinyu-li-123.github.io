---
title: 'LeetCode刷题笔记 - 链表'
date: 2024-11-20T22:41:16-05:00
draft: false
mathjax: false
tags: ['Grinding', 'LeetCode']
---

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