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
