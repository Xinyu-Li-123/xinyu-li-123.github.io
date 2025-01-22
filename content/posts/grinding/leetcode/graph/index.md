---
date: '2024-11-19T00:54:34-05:00'
draft: false
title: 'LeetCode刷题笔记 - 图论'
mathjax: true
tags: ['Grinding', 'LeetCode']
---

## DFS & BFS

```cpp
// Backtracing
void dfs(cur_node, path) {
    process node
    dfs(next_node, path)
    backtrace, undo result
}
```

### [797. All Paths From Source to Target](https://leetcode.com/problems/all-paths-from-source-to-target/description/)

DFS search the DAG. Backtracking from 0 to n-1.

### []

## Union-Find Set

Given a graph (node, edge), determine if two elements are connected.

```cpp
class UnionFind {
private:
    int n;
    vector<int> father;
public:
    bool validPath(int n, vector<vector<int>>& edges, int source, int destination) {
        father = vector<int>(n);
        for (int i = 0; i < n; i++) {
            father[i] = i;
        }        

        for (const auto&[u, v] : edges) {
            join(u, v);
        }
        return isSameSet(source, destination);
    } 

    // find the root of u
    int find(int u) {
        if (u == father[u]) {
            return u;
        }
        father[u] = find(father[u]);
        return father[u];
    }

    bool isSameSet(int u, int v) {
        // Note that we need another round of path compression before judging if u and v are in the same set.
        // Simply using father[u] == father[v] won't work.
        u = find(u);
        v = find(v);
        return u == v;
    }

    // join v to the root of u
    void join(int u, int v) {
        int ru = find(u);
        int rv = find(v);
        if (ru == rv) {
            return;
        }
        father[rv] = ru;
    }
}
```

### Redundant Connection I & II 

### Minimal Spanning Tree, Prim & Kruskal

## Topological Sorting

给定N个文件，文件编号0到N-1，文件之间有依赖关系，请编写一个算法，确定文件处理的顺序。

```
deps = [[0, 1], [0, 2], [1, 3], [2, 4]]

dep graph
    1 -> 3
  /
0
  \ 
    2 -> 4

equiv linear order
0 1 3 2 4
or 
0 2 4 1 3
or 
0 1 2 3 4
or 
...
```

这类问题是将**有向图中的排序关系转换成线性排序**，或者**检测出有向图中存在环**，无法线性排序。

首先，我们想找到线性排序的第一个节点。**一个节点是第一个节点当且仅当它的入度为0**。基于这条性质，我们可以给出拓扑排序的主要思路

1. 找到入度为0的节点

2. 将节点从图中移除（将与该节点相连的其他节点的入度减一），在移除的图中找入度为0的节点

如果存在环，那么环里的节点入度肯定大于0，这会导致我们无法移除所有节点。那么在循环退出时判断一下移除节点的数量，就可以知道图中是否存在环。

算法如下

```cpp
// Given `vector<vector<int>> edges`, and number of nodes `int n` 
// edges[i][0] -> edges[i][1]
unordered_map<int, vector<int>> deps;
vector<int> inDegrees(n, 0);
vector<int> result;

for (const auto&edge: edges) {
    deps[edge[0]].push_back(edge[1]);
    inDegrees[edge[1]]++;
}

queue<int> que;

// push all 0-in-degree nodes into queue
// Since we use bfs and only push connected nodes into queue, if we don't push a 0-in-degree node here, it will never be pushed later.
for (int i = 0; i < n; i++) {
    if (inDegrees[i] == 0) {
        que.push_back(i);
    }
}

while (!que.empty()) {
    auto cur = que.front();
    que.pop();
    result.push_back(cur);
    for (auto node : deps[cur]) {
        inDegrees[node]--;
        if (inDegrees[node] == 0) {
            que.push(node);
        }
    }
}

if (result.size() < n) {
    cout << "Found circle!" << endl;
} else {
    cout << "Topological sorting done." << endl;
}
```
### [207. Course Schedule](https://leetcode.com/problems/course-schedule/description/)

### [210. Course Schedule II](https://leetcode.com/problems/course-schedule-ii/description/)