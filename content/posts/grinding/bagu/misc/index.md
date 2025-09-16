---
title: "八股 - 杂项"
date: 2024-11-21T01:17:48-05:00
draft: false
mathjax: true
tags: ['Grinding', '八股']
---

## Bloom Filter 布隆过滤器

A space-efficient probabilistic data structure that tells you whether an element "definitely not in a set" or "possibly in a set". Allow quick check of membership at the cost of occasional false positive.

It provides two apis

```typescript
put(elem: T) -> void
might_contains(elem: T) -> boolean
```

A bloom filter uses:

- A bit array of size `m` (initially all zeros)

- `k` independent hash functions that map elements to array positions

**Adding an element:**

1. Hash the element with each of the `k` hash functions

2. Set the corresponding bits in the array to 1

**Checking membership:**

1. Hash the element with the same `k` hash functions  

2. Check if ALL corresponding bits are 1

3. If any bit is 0 → element is definitely NOT in the set

4. If all bits are 1 → element MIGHT be in the set

**Why false positives occur:** Different elements can hash to the same bit positions. If enough other elements have set all the bits that your query element hashes to, you'll get a false positive.

### Calculation of false positive rate

TODO:

### Key properties

- **Space efficient:** Uses much less space than storing actual elements

- **Fast operations:** O(k) time for both insertion and lookup

- **One-way errors:** Can have false positives, but never false negatives

- **No deletions:** Standard bloom filters don't support removing elements (though variants like counting bloom filters do)

### Common applications

- **Database query optimization:** Check if a record might exist before expensive disk lookup

- **Web caching:** Quickly determine if a URL might be cached

- **Network routing:** Efficiently represent routing tables

- **Distributed systems:** Coordinate between nodes about what data they might have

### Example: Avoid revisiting URL in a web crawler

TODO:

## 缓存淘汰算法

缓存容量有限，因此我们需要决定哪些数据需要被淘汰。

### LRU 缓存

LRU 缓存的思路是仅保留最近使用过的前 K 个数据。

LRU 缓存提供两个 API：

- `get(key)`: 返回键对应的值。时间复杂度 **O(1)**

- `put(key, value)`: 插入或更新一个键值对。时间复杂度 **O(1)**

其实现基于**哈希表**和**双链表**。

- 双链表的头节点是最近使用的键值对，尾节点是最久未使用的键值对。

- 哈希表存储键到链表节点（指针）的映射。

为了做到`O(1)`的读写，双链表需提供以下 API

```python
class ListNode:
  key: int
  value: int
  prev: ListNode
  next: ListNode

# O(1), Remove a specific node (pass in a pointer)
removeNode(node: ListNode) -> None
# O(1), Insert a node at head
pushAtHead(node: ListNode) -> None
# O(1), Remove a node at tail
popAtTail() -> ListNode
```

每读取一个键，或改写一个已存在的键的值，我们都要把它**移到链表头部**，以此表示这个键值对最近被使用过。"移到链表头部"是通过`removeNode` + `pushAtHead`实现的

```python
# move node to head
curNode = table[key]
self.dll.removeNode(curNode)
self.dll.pushAtHead(curNode)
```

每插入一对新的键值对，如果双链表的长度超过 K ，我们**删除链表尾节点**（淘汰），再将新的键值对作为新的头节点， 以此保证我们只存储最近使用过的前 K 个键值对。

LRUCache 的 Python 代码如下

```python
class LRUCache:
  def __init__(self, capacity: int):
    self.table: dict[int, ListNode] = {}
    self.dll = DoublyLinkedList()
    self.capacity = capacity

  def get(self, key) -> int:
    if key not in self.table:
      return -1
    node = self.table[key]
    self._refresh_node(node)
    return node.value

  def put(self, key, value) -> None:
    if key in self.table:
      # move node in dll to head
      curNode = self.table[key]
      curNode.value = value
      self._refresh_node(curNode)
    else:
      # create new node (evict if full), insert at head 
      if self._isFull():
        self._evict()
      newNode = ListNode(key, value)
      self.dll.pushAtHead(newNode)
      self.table[key] = newNode

  def _refresh_node(self, node: ListNode) -> None:
    """
    When a key is used, we refresh its node in the doubly-linked list by moving it to head. 
    """
    self.dll.removeNode(node)
    self.dll.pushAtHead(node)

  def _isFull(self) -> bool:
    return len(self.table) >= self.capacity

  def _evict(self) -> None:
    deletedNode = self.dll.popAtTail()
    self.table.pop(deletedNode.key)
```

`DoublyLinkedList` 和 `ListNode` 的实现如下

```python
class ListNode:
  def __init__(self, key: int, value: int):
    self.key = key
    self.value = value
    self.prev = None
    self.next = None

class DoublyLinkedList:
  def __init__(self):
    # 虚拟头尾节点
    self.vhead = ListNode(0, 0)
    self.vtail = ListNode(0, 0)
    self.vhead.next = self.vtail
    self.vtail.prev = self.vhead

  def removeNode(self, node: ListNode) -> None:
    prevNode, nextNode = node.prev, node.next
    prevNode.next = nextNode
    nextNode.prev = prevNode
    node.prev = node.next = None

  def pushAtHead(self, node: ListNode) -> None:
    node.next = self.vhead.next
    node.prev = self.vhead
    self.vhead.next.prev = node
    self.vhead.next = node

  def popAtTail(self) -> ListNode:
    if self.vtail.prev == self.vhead:
      return None
    tailNode = self.vtail.prev
    self.removeNode(tailNode)
    return tailNode
```

注：

- 双链表可以使用虚拟头/尾节点，简化实现

### LRU 变种：LRU-K 缓存

### LRU 变种：Clock 算法

### LFU

### FIFO

### 各类算法的优劣
