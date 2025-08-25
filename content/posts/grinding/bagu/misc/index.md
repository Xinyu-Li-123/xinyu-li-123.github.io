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
