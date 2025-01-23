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

### [200. Number of Islands](https://leetcode.com/problems/number-of-islands/description/)

遍历所有格子。
- 遇到'1'，开始搜索岛屿（dfs or bfs）。走过的格子都标记为已遍历。搜索结束后，岛屿（相连的'1‘）及其边缘（环岛一周的'0'）都被遍历过。

- 遇到'0'继续遍历

注意dfs时，需要**上下左右都搜索**，如果只搜索下右侧，那么会遗漏部分岛屿，例如

'''
// 从(1,1)开始dfs，只向下右搜索会遗漏(2,0)
// 导致搜索结果中，(1,1)和(2,0)不再同一个岛屿
0 0 0 0 0
0 1 0 0 0
1 1 1 0 0
1 0 0 0 0

// 从(0,0)开始dfs，只向左下右搜索会遗漏(1,2)
// 导致搜索结果中，(0,0)和(1,2)不再同一个岛屿
1 0 1 1 1
1 0 1 0 1
1 1 1 0 1
'''

以下分别时dfs和bfs的解法

```cpp
class Solution {
private:
    vector<vector<bool>> visited;
    int count;
    int numRows;
    int numCols;

    // Start dfs from grid[i][j]
    void dfs(int i, int j, vector<vector<char>>& grid) {
        if ((i < 0 || i >= numRows) || (j < 0 || j >= numCols)) {
            return;
        }
        if (visited[i][j]) {
            return;
        }
        visited[i][j] = true;
        // explore top, right down, bottom.
        if (grid[i][j] == '0') {
            return;
        }
        // dfs(i-1, j, grid);
        dfs(i, j+1, grid);
        dfs(i+1, j, grid);
        dfs(i, j-1, grid);
    }

    // Start bfs from grid[i][j]
    void bfs(int i, int j, vector<vector<char>>& grid) {
        // a queue of coordinate on grid
        queue<pair<int, int>> qu;

        qu.emplace(i, j);

        while (!qu.empty()) {
            auto [row, col] = qu.front();
            qu.pop();
            // cout << row << ", " << col << endl;
            if ((row < 0 || row >= numRows) || (col < 0 || col >= numCols)) {
                continue;
            }
            if (visited[row][col]) {
                continue;
            }
            visited[row][col] = true;
            if (grid[row][col] == '0') {
                continue;
            }
            qu.emplace(row-1, col);
            qu.emplace(row, col+1);
            qu.emplace(row+1, col);
            qu.emplace(row, col-1);
        }
    }

public:
    int numIslands(vector<vector<char>>& grid) {
        numRows = grid.size();
        numCols = grid[0].size();
        visited = vector<vector<bool>>(numRows, vector<bool>(numCols, false));
        for (int i = 0; i < numRows; i++) {
            for (int j = 0; j < numCols; j++) {
                if (visited[i][j]) {
                    continue;
                }
                if (grid[i][j] == '1') {
                    count++;
                }
                dfs(i, j, grid);
                // bfs(i, j, grid);
                // cout << endl;
            }
        }
        return count;
    }
};
```

### [695. Max Area of Island](https://leetcode.com/problems/max-area-of-island/description/)

同200，只是在每一次dfs/bfs时，统计1的数量，得到岛屿面积。

### [417. Pacific Atlantic Water Flow](https://leetcode.com/problems/pacific-atlantic-water-flow/description/)

逆转思路，考虑从海里往陆地上爬，逆着水流的方向走到最高处，则走过的地方都可以有水流流入海洋。

对于每一个靠近海洋的格子（既岛屿边缘），进行dfs。如果dfs当前格比上一个低，则无法继续搜索。

基于dfs搜索算法实现如下

```cpp
class Solution {
private:
    // whether (i,j) can reach Pacific Ocean
    vector<vector<bool>> reachPa;
    // whether (i,j) can reach Atalantic Ocean
    vector<vector<bool>> reachAt;
    vector<vector<bool>> heights;
    int m;
    int n;

private:
    // Water flows upward starting from (i,j)
    void dfs(int i, int j, int prevHeight, vector<vector<int>>& heights, vector<vector<bool>> &reach) {
        if (i < 0 || i >= m) {
            return;
        }
        if (j < 0 || j >= n) {
            return;
        }
        if (reach[i][j]) {
            return;
        }

        int curHeight = heights[i][j];
        if (prevHeight > curHeight) {
            return;
        }
        reach[i][j] = true;
        dfs(i-1, j, curHeight, heights, reach);
        dfs(i, j-1, curHeight, heights, reach);
        dfs(i+1, j, curHeight, heights, reach);
        dfs(i, j+1, curHeight, heights, reach);
    }

public:
    vector<vector<int>> pacificAtlantic(vector<vector<int>>& heights) {
        // heights is an m*n matrix
        m = heights.size();
        n = heights[0].size();
        reachPa = vector<vector<bool>>(m, vector<bool>(n, false));
        reachAt = vector<vector<bool>>(m, vector<bool>(n, false));
        // go from the ocean against the height, mark each cell in the path
        
        for (int i = 0; i < m; i++) {
            dfs(i, 0, 0, heights, reachPa);
            dfs(i, n-1, 0, heights, reachAt);
        }

        for (int j = 0; j < n; j++) {
            dfs(0, j, 0, heights, reachPa);
            dfs(m-1, j, 0, heights, reachAt);
        }

        vector<vector<int>> result;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (reachPa[i][j] && reachAt[i][j]) {
                    vector<int> pos(2, 0);
                    pos[0] = i;
                    pos[1] = j;
                    result.push_back(pos);
                }
            }
        }
        return result;
    }
};
```

这道题也可以用bfs搜索：对于每一个节点，我们考虑其上下左右的邻居节点，将满足以下两个性质的节点放入队列

1. 该邻居节点没有被访问过 

2. 该邻居节点的高度不小于当前节点

### [827. Making A Large Island](https://leetcode.com/problems/making-a-large-island/description/)

考虑以下岛屿

```
1 0 0 0
0 1 0 0
0 0 1 1
0 0 0 0
```

对于一个0，我们观察它的上下左右，如果是1，说明有岛屿相连，那就bfs/dfs求出岛屿的面积，并累加。对于上面的grid，考虑坐标(1,2)的0,其面积是：左侧面积为1的岛 + 下侧面积为2的岛 + 1。

为了防止重复计算，我们可以只使用一遍bfs/dfs，提前求出所有岛屿面积，并在每一格上标记其岛屿面积，方便求和。标记后的岛屿如下

```
// grid of area
1 0 0 0
0 1 0 0
0 0 2 2
0 0 0 0
```

但这么计算有可能把同一个岛屿计算两边，比如这个grid

```
// grid of area
1 0 0 0
0 2 0 0
0 2 2 2
1 0 0 0
```

还是看坐标(1,2)的0,按照上文的算法，面积为2的岛屿会被累加两次。为了防止这一情况，我们给每一个岛屿一个id，然后在每一个标记岛屿的id，并维护一个岛屿id到面积的map，如下

```
// grid of id
1 0 0 0
0 2 0 0
0 2 2 2
3 0 0 0

// id -> area map
1 -> 1
2 -> 4
3 -> 1
```

对应的算法如下：

```cpp
class Solution {
private:
    int m;
    int n;
    // islandId -> area
    unordered_map<int, int> id2area;
    // islandId of each area
    // Need id to avoid counting same island twice
    vector<vector<int>> ids;
    vector<vector<bool>> visited;

    // bfs to search for connected 1's, starting from (i,j)
    // then bfs to mark each connected 1 using island area
    void bfs(int row, int col, vector<vector<int>>& grid, int id) {
        // assert(grid[row][col] == 1 && "Cannot compute island area if initial pos is not part of an island!");
        // assert(id2area.find(id) == id2area.end() && "already computed island");
        // q1 is used to compute area
        queue<pair<int, int>> q1;
        // q2 is used to mark entry with area.
        // q2 can be constructed w/ entries poped from q1
        queue<pair<int, int>> q2;

        q1.emplace(row, col);
        visited[row][col] = true;
        while (!q1.empty()) {
            auto [i, j] = q1.front();
            q2.emplace(i, j);
            q1.pop();
            // cout << "id " << id << ", visit " << i << ", " << j << endl;
            if (i >= 1) {
                if (!visited[i-1][j] && grid[i-1][j] == 1) {
                    q1.emplace(i-1, j);
                    visited[i-1][j] = true;
                }
            }
            if (j >= 1) {
                if (!visited[i][j-1] && grid[i][j-1] == 1) {
                    q1.emplace(i, j-1);
                    visited[i][j-1] = true;
                }
            }
            if (i <= m-2) {
                if (!visited[i+1][j] && grid[i+1][j] == 1) {
                    q1.emplace(i+1, j);
                    visited[i+1][j] = true;
                }
            }
            if (j <= n-2) {
                if (!visited[i][j+1] && grid[i][j+1] == 1) {
                    q1.emplace(i, j+1);
                    visited[i][j+1] = true;
                }
            }
        }
        int area = q2.size();
        while (!q2.empty()) {
            auto [i, j] = q2.front();
            q2.pop();
            ids[i][j] = id;
            id2area[id] = area;
        }
    }

public:
    int largestIsland(vector<vector<int>>& grid) {
        // - search for all island and compute their sizes (O(n))
        // - mark each entry in each island by the island size (O(n))
        // - walk over all 0's, look around 0's neighbors to see if (O(n))
        //   0 is connected to any island 
        m =  grid.size();
        n = grid[0].size();
        // areas = vector<vector<pair<int, int>>>(m, vector<pair<int, int>>(n));
        ids = vector<vector<int>>(m, vector<int>(n, -1));
        visited = vector<vector<bool>>(m, vector<bool>(n, false));

        // compute area of each island
        for (int i = 0, id = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == 0 || visited[i][j]) {
                    continue;
                }
                bfs(i, j, grid, id);
                id++;
            }
        }

        int maxArea = 0;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == 1) {
                    // auto id = ids[i][j];
                    // auto curArea = id2area[id];
                    // maxArea = max(maxArea, curArea);
                    continue;
                }
                int curArea = 1;
                set<int> neighIslands;
                if (i >= 1) {
                    neighIslands.insert(ids[i-1][j]);
                }
                if (j >= 1) {
                    neighIslands.insert(ids[i][j-1]);
                }
                if (i <= m-2) {
                    neighIslands.insert(ids[i+1][j]);
                }
                if (j <= n-2) {
                    neighIslands.insert(ids[i][j+1]);
                }               

                for (auto id : neighIslands) {
                    curArea += id2area[id];
                }
                maxArea = max(maxArea, curArea);
            }
        }

        for (const auto& [id, curArea] : id2area) {
            maxArea = max(maxArea, curArea);
        }

        return maxArea;
    }
}
```

### [127. Word Ladder](https://leetcode.com/problems/word-ladder/description/)

### [463. Island Perimeter](https://leetcode.com/problems/island-perimeter/description/)

dfs的过程中，在当前格子周长+4；假如上方（或者下左右）的格子为1，则向上dfs。此时格子上方的边会被下一次dfs加入周长，导致这条边被计算了两次。因此在向上dfs前，周长-1。

由此得算法

```cpp
class Solution {
private:
    int m;
    int n;
    vector<int> di = vector<int>{-1, 0, 1, 0};
    vector<int> dj = vector<int>{0, -1, 0, 1};
    int perimeter = 0;

    vector<vector<bool>> visited;

    void dfs(int row, int col, vector<vector<int>>& grid) {
        if (visited[row][col]) {
            return;
        }
        visited[row][col] = true;
        perimeter += 4;
        for (int p = 0; p < 4; p++) {
            int i = row + di[p];
            int j = col + dj[p];
            if (i < 0 || i >= m || j < 0 || j >= n) {
                continue;
            }
            if (grid[i][j] == 0) {
                continue;
            }
            perimeter -= 1;
            dfs(i, j, grid);
        }
    }
public:
    int islandPerimeter(vector<vector<int>>& grid) {
        m = grid.size();
        n = grid[0].size();
        visited = vector<vector<bool>>(m, vector<bool>(n, false));

        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == 1) {
                    dfs(i, j, grid);
                    return perimeter;
                }
            }
        }
        return 0;
    }
}
```

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