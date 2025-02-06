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

### Print each layer in tree on separate line 

Use BFS. In each iteration of for loop, print the entire layer. 

Layer length = queue length 

```cpp
while (!qu.empty()) {
    int len = qu.size();
    for (int i = 0; i < len; i++) {
        auto cur = qu.pop();
        cout << cur.val << ", ";
        for (const auto& child : cur.children) {
            qu.push(child);
        }
    }
    cout << endl;
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

### [542. 01 Matrix](https://leetcode.com/problems/01-matrix/description/)

给定一个01矩阵，求每个格子到最近的0的距离（需要走几步能到0）。

思路是bfs，把0想象成水，把1想象成海绵，算法的思路就是让水一步步向海面深处渗透。

换句话说，我们的遍历顺序是

- 所有0 (水)

- 所有和0距离为1的格子（水向距离为1的海绵格子渗透）

- 所有和0距离为2的格子（通过距离为1的海绵，水向距离为2的海绵格子渗透）

- ...

这就又回到了如何在bfs时特殊处理每一层的问题了。我们在遍历的过程中，记录层数，层数就是当前格子到0的距离。

算法实现上，可以使用[另一篇文章](https://xinyu-li-123.github.io/en/posts/grinding/leetcode/tips/#%E9%81%8D%E5%8E%86%E4%B8%80%E6%A0%BC%E7%9A%84%E4%B8%8A%E4%B8%8B%E5%B7%A6%E5%8F%B3%E6%A0%BC%E5%AD%90)里提到的在格子中遍历上下左右邻居的方法。

算法如下

```cpp
vector<vector<int>> updateMatrix(vector<vector<int>>& mat) {
    // a m x n matrix
    int m = mat.size();
    int n = mat[0].size();

    vector<vector<int>> dist(m, vector<int>(n, 0));
    vector<vector<bool>> visited(m, vector<bool>(n, false));
    queue<pair<int, int>> que;

    // push all 0 on queue
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            if (mat[i][j] != 0) {
                continue;
            }
            visited[i][j] = true;
            que.emplace(i, j);
        }
    }

    // iterate over each layer
    int curDist = 0;
    while (!que.empty()) {
        int numCell = que.size();
        for (int q = 0; q < numCell; q++) {
            auto [i, j] = que.front();
            que.pop();
            // push all unvisited neighbors on queue
            for (int p = 0; p < 4; p++) {
                int dx = dxs[p];
                int dy = dys[p];
                if (i + dx < 0 || i + dx >= m) { continue; }
                if (j + dy < 0 || j + dy >= n) { continue; }
                if (visited[i + dx][j + dy]) { continue; }
                que.emplace(i + dx, j + dy);
            }
            // record distance of current node if it's unvisited
            if (visited[i][j]) {
                continue;
            }
            visited[i][j] = true;
            dist[i][j] = curDist;
        }
        curDist++;
    }

    return dist;
}
```

### [133. Clone Graph](https://leetcode.com/problems/clone-graph/description/)

给定一张连通无向图，和一个图中的节点R，深拷贝（deep copy）这张图，并返回拷贝的图中对应节点R的节点。图中每个节点的`val`都是唯一的。

思路是dfs，从R开始dfs，过程中记录拷贝过的节点的`val`和地址。如果dfs过程中遇到拷贝过的节点，直接使用其地址;否则创建一个新的节点。

## Union-Find Set

并查集适用于判断**无向图的连通性**，既判断无向图中两个节点是否相连。

并查集有两个操作：将两个元素并入同一个集合，或者判断两个元素是否属于同一个集合。

我们维护每一个节点的根节点

- 初始化时，每个节点的根节点是自己，表示所有节点都不相连

- 我们遍历无向图的边，并将每条边的端点并入同一个集合：对于边`(A, B)`，我们把B的根节点接在A的根节点下，这样所有与B相连的节点都与A相连。

- 最后，所有相连的节点都会有相同的根节点

**路径压缩**：

依照这个算法，我们最后会得到多颗树，每颗树表示一群相连接的节点。但这些树的高度可能会很高，使得查询节点是否相连变得困难。实际上，我们只在乎一个节点的根节点是什么，我们完全可以在合并时，直接把一个节点连接到另一个节点的根节点上，最后得到一颗高度只有2的树。

为了实现这个优化，每次调用`find(u)`时我们都把从`u`到根节点的所有节点直接连接到根节点上。例如从节点`u0`到根节点`r`，需要经过`u1, u2`。调用`find(u0)`时，`find`会递归调用直到找到根节点，从而将`u0, u1, u2`都直接连接到`r`。对应的代码如下

```cpp
// find the root of u
int find(int u) {
    if (u == father[u]) {
        return u;
    }
    // Path compression
    // Note that both isSameSet() and join() would invoke
    // find(), which would compress the path
    father[u] = find(father[u]);
    return father[u];
}
```

值得注意，并查集不适用于有向图的连通性。

以判断两节点是否相连为例，并查集模板代码如下：

```cpp
class UnionFind {
private:
    int n;
    vector<int> father;
public:
    // check if two nodes are connected
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
        // Path compression
        // Note that both isSameSet() and join() would invoke
        // find(), which would compress the path
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

## Minimal Spanning Tree

### Minimal Spanning Tree, Prim

Goal: Given an **undirected, weighted graph**, find the **spanning tree with minimal cost** (sum of edge weight in the tree).

Idea: **Greedly rebuild the spanning tree by adding node**, starting from an arbitrary node.

1. Start with an arbitrary node,

2. Among all nodes not in the current tree, include the node whose connection to nodes in the tree has minimal weight.

We maintain an array `minDist` where, if point i is not included in the current tree, `minDist[i]` is the minimal weight among all connections from point i to points in the current tree.

The time complexity is `O(V^2)` because we need to compute the adjacent matrix (whose entry records the weight between two nodes).

The algorithm is as follows

```cpp
// Given an nxn matrix weights, where weights[i][j]
// is the weight between edge from i to j
// If i and j are not connected, weights[i][j] = INT_MAX
int costOfMST(vector<vector<int>> weights) {
    int n = weights.size();
    vector<int> minDist(n, INT_MAX);
    vector<bool> isInTree(n, false);
    
    // This will make the first iteration of loop to choose node 0
    minDist[0] = 0;

    for (int i = 0; i < n; i++) {
        // 1. Find point w/ minimal distance

        // Exclude nodes already in tree
        if (isInTree[j]) {
            continue;
        }
        int minIdx = -1;
        int minVal = INT_MAX;
        if (minDist[i] < minVal) {
            minIdx = i;
            minVal = minDist[i];
        }

        // 2. Add that point to tree
        isInTree[i] = true;

        // 3. Update minDist for neighboring points
        for (int i = 0; i < n; i++) {
            if (isInTree[i]) {
                continue;
            }
            if (weights[i][minIdx] < minDist[i]) {
                minDist[i] = weights[i][minIdx];
            }
        }
    }

    int result = accumulate(minDist.begin(), minDist.end(), 0);

    return cost;
}
```

### Min Spanning Tree, Prim w/ Min heap.

If the graph is sparse (i.e. number of edge is low), we can replace adjacent matrix with a min heap of node, ordered by distance to MST.

0. Push node 0 to min heap

1. Pop heap until heap top has a node p not in tree, add p to the tree

2. Push all neighboring node of p to heap, ordered by the weight of their connection to p.

The time complexity is `O(ElogE)`. If the graph is complete (all pairs of nodes are directly connected), E is `O(n^2)` and this algorithm has poorer time complexity comapred to the adjacent matrix-based one above. It works best if the graph is sparse.

### Minimal Spanning Tree, Kruskal

Idea: **Greedly rebuild the MST by adding edges with smallest weight that won't create a cycle**.

0. Walk over all edges, and maintain a min-heap of edge ordered by weight.

1. Start by picking the edge with smallest weight.

2. For each top edge on heap

  - if adding it to graph create cycle, pop it

  - if not, add it to the tree

To tell if adding an edge to graph will create cycle, we use union-find set: we check if two endpoints of an edge are in the same set. If so, adding this edge will create a cycle.

Time Complexity: `O(ElogE)`, best for sparse graph.

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

实现算法时，我们在第2步中不需要真的移除节点，只需要维护一个记录每个节点入度的数组，并在移除某个节点时将其邻居节点的入度减一。

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

## Shortest Path

### Dijkstra

### Dijkstra w/ heap

### Bellman ford

### Floyd

### A\*