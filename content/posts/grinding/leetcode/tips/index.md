---
title: 'LeetCode刷题笔记 - 常用的CPP代码'
date: 2024-11-20T22:41:16-05:00
draft: false
mathjax: true
tags: ['Grinding', 'LeetCode']
---

这个文档整理了一些常用的CPP代码，例如如何确认unordered map中是否存在某一元素，如何定义一个min heap...

本文档默认遵循C++17标准。

# Language

## for loop

A typical for loop

```cpp
for (int i = 0; i < arr.size(); i++) {
    // ...
}
```

Iterator-based one (with auto type specifier in init-statement)

```cpp
for (auto iter = arr.begin(); iter != arr.end(); ++iter) {
    // ...
}
```

For loop with structured bindings in init-statement
```cpp
for (const auto&[k, v] : freqs) {
    // ...
}
```

# STL

## max的各种方法

```cpp
/* Given a vector... */

vector<int> vec = {10, 20, 5, 30, 40, -50};

// max of vec
cout << *max_element(vec.begin(), vec.end()) << endl;

// max of vec[1: 4]
cout << *max_element(vec.begin()+1, vec.begin()+4) << endl;

// max of abs val, use of anonymous fn
int ans = *max_element(vec.begin(), vec.end(), [](int a, int b) {
    return abs(a) < abs(b);
});
cout << ans << endl;

/* Given some elements... */

cout << max({10, 20, 30}) << endl;
```

## 最大的int / unsigned int / ...

```cpp
#include <climits>

INT_MAX;
// or 
numeric_limits<int>::max();
```

## Vector常用操作

```cpp
vector<int> arr(10, 0);

// access
arr[3];
arr.front();
arr.back();

// capacity
arr.empty();
arr.size();
arr.reserve(20);
arr.capacity();

// modifier
arr.insert(arr.begin() + 3, 20);
arr.emplace(arr.begin() + 3, 20);
arr.push_back(5);
arr.emplace_back(34);
arr.pop_back();
```

## Misc

### Define a 2d array using vector

```cpp
vector<vector<int>>(numRows, vector<int>(numCols, 0));
```

### Is element in set

```cpp
template <typename T>
bool exists(T elem, unordered_set<T> &uset) {
    return uset.find(elem) == uset.end();
}
```

### Create a min heap (top is min element)

```cpp
// priority_queue<T, Container, Compare>
// Compare(A, B) returns true if A < B.
// Since priority queue output the largest elements first, 
// B is actually outputed before A
priority_queue<int, vector<int>, std::greater<int>> minHeap;

minHeap.push(40);
minHeap.push(20);
minHeap.push(30);
minHeap.push(10);

while (!minHeap.empty()) {
    // 10, 20, 30, 40 
    cout << minHeap.top() << ", ";
    minHeap.pop();
}
cout << endl;
```

### Create a max heap with custom comparison function

```cpp
struct Log {
    char user;
    int ts;
};

// Obtain K earliest logs from an unsorted vector of logs
vector<Log> earliestKLogs(vector<Log> logs, int k) {
    auto logCmp = [](const Log& a, const Log& b) {
        // if a has smaller timestamp than b, Compare(a, b) return true
        // priority queue will output b before a
        // b will be popped before a
        return a.ts < b.ts;
    };
    priority_queue<Log, vector<Log>, decltype(logCmp)> maxHeap(logCmp);

    for (const auto&log : logs) {
        maxHeap.push(log);
        if (maxHeap.size() > k) {
            maxHeap.pop();
        }
    }

    vector<Log> result;
    result.reserve(k);
    while (!maxHeap.empty()) {
        result.push_back(maxHeap.top());
        maxHeap.pop();
    }
    reverse(result.begin(), result.end());
    return result;
}

void customCmpDemo() {
    auto logs = vector<Log>{
        Log{'A', 3},
        Log{'B', 1},
        Log{'C', 2},
        Log{'D', 4},
        Log{'E', 0},
    };

    auto result = earliestKLogs(logs, 3);

    for (const auto& log : result) {
        // E, 0
        // B, 1
        // C, 2
        cout << log.user << ", " << log.ts << endl;
    }
}
```

## Common code snippet

#### 遍历一格的上下左右格子

```cpp
dRows = {-1, 0, 1, 0};
dCols = {0, -1, 0, 1};

// iterate through the up/left/down/right neighbors of (curRow, curCol)

for (int p = 0; p < 4; p++) {
    process(curRow + dRows[p], curCol + dCols[p]);
}
```