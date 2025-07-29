---
title: 'LeetCode刷题笔记 - 常用的Python代码'
date: 2025-07-28T23:50:16-05:00
draft: false
mathjax: true
tags: ['Grinding', 'LeetCode']
---

We assume python 3.11, which is the python version used in LeetCode (see [doc](https://support.leetcode.com/hc/en-us/articles/360011833974-What-are-the-environments-for-the-programming-languages))

## Common Data Structures

### List

```python
lst = [2,4,6]
lst.append(x)        # Add at end
lst.pop()            # Remove from end
lst.pop(i)           # Remove at index
lst.insert(i, x)     # Insert at index. 
                     # For lst=[y, z], lst.insert(1, x) results in [y, x, z]
lst.remove(x)        # Remove first occurrence
lst.sort()           # In-place sort
lst.reverse()        # In-place reverse
sorted(lst)          # Returns new sorted list
lst.index(x)         # Find first index of x
```

### Tuple

Immutable, and hashable (can be used as element in set / key in dict)

### Set

```python
s = set([2,2,2,4,6])  # the same as `s = {2, 4, 6}`
s.add(x)              # Add to set, dedup
s.remove(x)           # Remove elem, if not exists throw err
s.discard(x)          # Remove elem, if not exists ignore
s.pop()               # Randomly pop one elem
s.union(t)
s.intersection(t)
s.difference(t)
s.symmetric_difference(t)
```

### Dictionary

```python
d.get(k, default)
d.keys(), d.values(), d.items()
d.pop(k)
d.popitem()
d.setdefault(k, default)
```

### Deque: `collections.deque`

Double-ended queue.

```python
from collections import deque

dq = deque([2,4,6])
dq.append(x)
dq.appendleft(x)
dq.pop()
dq.popleft()
dq.rotate(n)
```

### Heap: `heapq`

`heapq` provides min-heap. A min-heap is a complete binary tree where every parent node <= its children.

Time complexity of useful ops:

- access min elem: `O(1)`

- insert / remove elem: `O(log N)`

- create heap: `O(N)`

Min-heap can be used to efficiently implement priority queue where tasks of highest priority is processed first.

```python
nums = [(5, "task A"), (3, "task B"), (8, "task C"), (1, "task D")]
# nums is ordered after heapify
heapq.heapify(nums)
# nums is [(1, 'task D'), (3, 'task B'), (8, 'task C'), (5, 'task A')]
heapq.heappush(nums, (2, "task E"))
# nums is [(1, 'task D'), (2, 'task E'), (3, 'task B'), (8, 'task C'), (5, 'task A')]

# Peak smallest
smallest = nums[0]
# Pop smallest, re-heapify
# Elements are swapped in place to simulate ops on binary tree, so that heappop is O(log N)
smallest = heapq.heappop(nums)    # (1, 'task D')
```

> Note: Conceptually, heap is a tree. In practice, we represent it as a sorted list. For each element at index `i`,
>
> - it's left child is at `2*i + 1`
> - it's right child is at `2*i + 2`
> - it's parent is at `(i - 1) // 2`

### Counter `collections.Counter`

Counter w/ efficient top-k most common retrieval (heap-based impl).

```python
from collections import Counter
lst = [1,1,2,3,3,3,3,4,4,5]
c = Counter(lst)

# c.most_common(k) returns top k most common elements
# in the form [(elem, freq)]
c.most_common(2)    # [(3, 4), (1, 2)]
c.most_common(3)    # [(3, 4), (1, 2), (4, 2)]

# Iterator
c.elements()
# <itertools.chain object at 0x7fe91b2f2a70>

# Update
c.update([1,1,1,1,1,1])
c.most_common(2)    # [(1, 8), (3, 4)]
```

### Dictionary w/ Default Value: `collections.defaultdict`

Just a "nice to have", not really a substantially different data structure.

Instead of

```python
d = dict()
# ...
if key not in d:
  d[key] = []
d[key].append(10)
```

we can use `defaultdict` and write

```python
from collections import defaultdict

# defaultdict(default_factory)
# e.g. defaultdict(lamdba: "foobar")
d = defaultdict(list)
# ...
d[key].append(10)
```

Note that an item is created when you call

```python
d[key]
```

If you don't want it to be created, you can just call `d.get(key)`.

## Common Code Snippets

### Heap with custom comparator

```python
class Task
    def __init__(self, name, prio):
      self.name = name
      # Smaller means higher priority
      self.prio = prio

    def __lt__(self, other):
      return self.prio < other.prio

import heapq
heap = []
heapq.heappush(heap, Task("Do laundry", 2))
heapq.heappush(heap, Task("Write code", 1))

print(heapq.heappop(heap).name)   # "Write code"
```

