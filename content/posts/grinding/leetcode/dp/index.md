---
title: 'LeetCode刷题笔记 - 动态规划'
date: 2024-11-20T22:41:16-05:00
draft: false
mathjax: true
tags: ['Grinding', 'LeetCode']
---

## 概述

动态规划

DP三问：

- 状态表示什么？

- 状态如何转移？

- 初始状态是什么？

动态规划可以分为以下几类（参考[这篇文章](https://leetcode.cn/circle/discuss/NfHhXD/)和[这篇文章](https://github.com/youngyangyang04/leetcode-master?tab=readme-ov-file#%E5%8A%A8%E6%80%81%E8%A7%84%E5%88%92))

## 基础DP

状态用一维数组存储，状态转移比较明显，即题目有明显的”从状态A转向状态B“的描述。比如帕楼梯，从台阶\(i\)爬到台阶\(j\)。

<!-- ### 300. 最长上升子序列
### 1143. 最长公共子序列
### 120. 三角形最小路径和
### 53. 最大子序和
### 152. 乘积最大子数组
### 887. 鸡蛋掉落（DP+二分）
### 354. 俄罗斯套娃信封问题
### 198. 打家劫舍
### 213. 打家劫舍 II
### 121. 买卖股票的最佳时机
### 122. 买卖股票的最佳时机 II
### 123. 买卖股票的最佳时机 III
### 188. 买卖股票的最佳时机 IV
### 309. 最佳买卖股票时机含冷冻期
### 714. 买卖股票的最佳时机含手续费
### 72. 编辑距离
### 44. 通配符匹配
### 10. 正则表达式匹配 -->


<!-- ### 516. 最长回文子序列
### 730. 统计不同回文子字符串
### 1039. 多边形三角剖分的最低得分
### 664. 奇怪的打印机
### 312. 戳气球 -->

## 背包 DP

### 基础理论

> 有`n`个物品和容量为`W`的背包，每个物品有重量`weight[i]`和价值`value[i]`两种属性。要求选取若干物品放入背包，使得总价值最大且不超过背包重量。

#### 0-1背包

在上述题目基础上，每个物品只能选一次。

**二维DP**

构造`(n, W)`二维DP数组`dp`。`dp[i][j]`表示

> 在物品`0`到物品`i`中选择，容量为`j`的背包所能装下的最大价值为`dp[i][j]`。

到达`dp[i][j]`的方式有两种：

1. 不放物品`i`

    则最大价值为只能选前`i-1`个物品，容量为`j`的背包所能装下的最大价值

2. 放物品`i` 

    则最大价值为`value[i]`加上选前`i-1`个物品，容量为`j-weight[i]`的背包所能装下的最大价值

对应的状态转移方程为

```cpp
dp[i][j] = max(dp[i-1][j], dp[i-1][j-weight[i]] + value[i]])
```

对应的核心代码为

```cpp 
// We declare a 2d array of size (n+1, W) for convenience
for (int i = 0; i < n; i++) {
    for (int j = W - weight[i]; j < W; j++) {
        dp[i+1][j+1] = max(dp[i][j], dp[i][j-weight[i]] + value[i]])
    }
}
```

**滚动数组**

考虑空间复杂度，我们可以用滚动数组代替二维数组。

对于当前的`i`，`dp[j]`表示选前`i`个物品，容量`j`的背包所能装下的最大价值。

对应的核心代码为

```cpp
// We declare a 1d array of size W
for (int i = 0; i < n; i++) {
    for (int j = W-1; j >= weight[i]; j--) {
        dp[j] = max(dp[j], dp[j - weight[i]] + value[i]);
    }
}
```

值得注意的是，里面一层循环是**从后往前**的。这是因为`dp[i][j]`是由`dp[i-1][j]`和`dp[i-1][j-weight[i]]`决定的。从后往前更新一维数组时，在对`i`更新到`dp[j]`时，`dp[j-weight[i]]`还没有被更新，仍然是`i-1`时更新的结果，**此时的`dp[j-weight[i]]`表示“选前`i-1`个物品，容量为`j-weight[i]`的背包所能装下的最大价值”**。

#### 完全背包

完全背包中，物品可被选择无数次。

由上文滚动数组的分析，我们可以引申出完全背包的滚动数组解法：和0-1背包类似，但从前往后更新滚动数组。

这是因为从前往后更新，对`i`更新到`dp[j]`时，`dp[j-weight[i]]`已经是对`i`更新后的结果，**其含义为“选前`i`个物品，容量为`j-weight[i]`的背包所能装下的最大价值”**。

在上述题目基础上，每个物品可以选取无数次。

### [416. Partition Equal Subset Sum](https://leetcode.com/problems/partition-equal-subset-sum/description/)

思路：目标和`tgt_sum`为`nums`总和的一半。则可以把问题转换为对于容量为`tgt_sum`的背包，让`weight[i] = value[i] = nums[i]`。如果最大价值等于`tgt_sum`，则表示可以等分集合。

### [1049. Last Stone Weight II](https://leetcode.com/problems/last-stone-weight-ii/description/)

考虑题目给出的例1，石头相撞的过程如下

```
We can combine 2 and 4 to get 2, so the array converts to [2,7,1,8,1] then,
we can combine 7 and 8 to get 1, so the array converts to [2,1,1,1] then,
we can combine 2 and 1 to get 1, so the array converts to [1,1,1] then,
we can combine 1 and 1 to get 0, so the array converts to [1], then that's the optimal value.
```

可以表示成
```
Given [2, 7, 4, 1, 8, 1]
4 - 2 => [(4-2), 7, 1, 8, 1]
8 - 7 => [(4-2), 1, 1, (8-7)]
(4-2) - 1 = 2 - 1 => [(4-2-1), 1, (8-7)]
(4-2-1) - 1 = 1 - 1 => [(8-7)]

The entire process is the same as saying 
4 - 2 - 1 - 1 + 8 - 7 = 1
```

上述过程可以被解释为“加或减每个数组中的数字，所能得到的最小非负值”。

这一过程也可以被解释为“分割数组为两个子数组，求两个子数组之和的最小差值”。这就回到了416的分割子集的思路。

### [494. Target Sum](https://leetcode.com/problems/target-sum/description/)

题目可以这样理解：将数组分割成两个子数组，各自的和分别为`x`和`y`（不妨设`x > y`）。求能满足`x-y=target`的分割方法的数量。

已知`x+y=sum(nums), x-y=target`，则可知`y=(sum(nums)-target)/2`，题目可以等价为求出在数组中任选数字、其和为`y`的选择方法数量。

`dp[j]`表示选前`i`个物品，可以填满容量为`j`的背包的选择方法的数量。对应的状态转移方程为`dp[i][j] = dp[i-1][j] + dp[i-1][j-weight[i]]`。

### [474. Ones and Zeroes](https://leetcode.com/problems/ones-and-zeroes/description/)

`dp`是大小为`(m+1, n+1)`的二维滚动数组。

对于当前的`i`，`dp[j][k]`表示在前`i`个字符串里选择，能满足`at most j 0's and n 1's in the subset`的最大子集大小。

状态转移方程为`dp[j][k] = max(dp[j][k], dp[j-count_0[i]][k-count_1[i]])`，即选或不选`strs[i]`得到的最大子集大小。

### [518. Coin Change II](https://leetcode.com/problems/coin-change-ii/description/)

比较明显的完全背包。一个注意的点是`dp`数组得是`uint64_t`，否则在存储中间结果时会integer overflow。

### [377. Combination Sum IV](https://leetcode.com/problems/combination-sum-iv/description/)

很有意思的一个问题。如果求所有可能的排列 / 组合，那么就只能回溯。但这道题求的是排列的数量，就能DP。

另外，用DP可以求完全背包的排列数量和组合数量，其代码正好是相反的。

首先明确一下定义：排列（permutation）是有顺序的，组合（combination）是没有顺序的。`(1, 5)`和`(5, 1)`是同一个组合，不同的排列。

对于完全背包的组合数量，我们先循环物品，再循环背包。

```cpp
for (int i = 0; i < nums.size(); i++) {
    for (int j = nums[i]; j <= capacity; j++) {
        dp[j] = dp[j] + dp[j - nums[i]];
    }
}
```

这一写法会使最后的选择方案里，物品必然按照`nums`的顺序排序。假如`nums = {1, 2, 3, 4, 5}`，那么就不可能出现`5`在`1`前的方案。换句话说，对于属于统一组合的不同排列，我们只取按照物品排序和`nums`相同的方案（这一方案显然是唯一的）。

对于完全背包的排列数量，我们先循环背包，再循环物品

```cpp
for (int j = 0; j <= capacity; j++) {
    for (int i = 0; i < nums.size() && nums[i] <= j; i++) {
        dp[j] = dp[j] + dp[j - nums[i]];
    }
}
```

这一写法则保证了在考虑`dp[j]`时，`dp[k]， k < j`的方案数量时考虑了全部物品的方案数量。

### [322. Coin Change](https://leetcode.com/problems/coin-change/)

At `i`, `dp[j]` is the fewest number of coins needed to reach amount `j` considering `coins[0]` to `coins[i]`.

## 打家劫舍

## 股票

有通解。

## 子序列

## 区间 DP

<!-- ### 416. 分割等和子集 (01背包-要求恰好取到背包容量)
### 494. 目标和 (01背包-求方案数)
### 322. 零钱兑换 (完全背包)
### 518. 零钱兑换 II (完全背包-求方案数)
### 474. 一和零 (二维费用背包) -->

## 树形 DP

树的定义是“无环无向连通图”。在树上DP，可以对树后序遍历，当前节点的状态由子节点状态推出。

### [968. Binary Tree Cameras](https://leetcode.com/problems/binary-tree-cameras/)

Hard题。虽然做了三个小时，但最后居然真的做出来了...

代码随想录里把这道题划分到了贪心，但我用dp也能做的出来。

等有精力了再研究一下贪心的解法...

我的整体思路是后序遍历整颗树，每个节点的状态由其直接子节点推出。

每个节点有三个状态

- `dp[node_ptr][0]`: 没有摄像头、未被子节点监视时，最小摄像头数

- `dp[node_ptr][1]`: 没有摄像头，但被子节点监视时，最小摄像头数

- `dp[node_ptr][2]`: 有摄像头时，最小摄像头数量

状态转移的方式如下

```cpp
// cur has no cam and is not monitored 
// => left and right has no cam, and they must be monitored by child
dp[cur][0] = dp[cur->left][1] + dp[cur->right][1];
// cur has no cam but is monitored by child 
// = left or right or both have cam, and whichever has no cam must be monitored by child
dp[cur][1] = min({
    dp[cur->left][2] + dp[cur->right][1], 
    dp[cur->left][1] + dp[cur->right][2],
    dp[cur->left][2] + dp[cur->right][2]
});
// cur has cam
// min among all possible combination of states of left and right
dp[cur][2] = 
        *min_element(dp[cur->left].begin(), dp[cur->left].end()) 
    +   *min_element(dp[cur->right].begin(), dp[cur->right].end()) 
    +   1
```

然而事情并没有这么简单。有一些情况下，是会存在非法的状态的。考虑以下树中的A节点。`dp[A][0]`就是一个非法的状态。如果`dp[A][0]`合法，那就意味着A没有摄像头，也没有子节点监视A，由此可知A、B、C都没有摄像头，这会导致B和C无法被任何节点监视到。

```
        [A]
      /     \
    [B]     [C]
```

为了解决这一问题，我们可以使用一个很大的数字表示非法状态。题干中节点数量范围为\([1,1000]\)，摄像头数量最多为1000。所以我们可以用`10000`表示非法状态。在初始化叶子节点时，`dp[node][1]`就是非法状态，因为叶子节点没有子节点，不可能被子节点监视。因此，有以下代码

```cpp
if (cur->left == nullptr || cur->right == nullptr) {
    auto child = cur->left == nullptr ? cur->right : cur->left;
    dp[cur][0] = dp[child][1];
    dp[cur][1] = dp[child][2];
    dp[cur][2] = *min_element(dp[child].begin(), dp[child].end()) + 1;
} else {
    // 上述状态转移的代码
}
```


<!-- ### 124. 二叉树中的最大路径和
### 1245. 树的直径 (邻接表上的树形 DP)
### 543. 二叉树的直径
### 333. 最大 BST 子树
### 337. 打家劫舍 III -->

<!-- ## 状态压缩 DP -->

<!-- ### 464. 我能赢吗
### 526. 优美的排列
### 935. 骑士拨号器
### 1349. 参加考试的最大学生数 -->

<!-- ## 数位 DP -->

<!-- ### 233. 数字 1 的个数
### 902. 最大为 N 的数字组合
### 1015. 可被 K 整除的最小整数 -->

<!-- ## 计数型 DP -->

<!-- ### 62. 不同路径
### 63. 不同路径 II
### 96. 不同的二叉搜索树 (卡特兰数)
### 1259. 不相交的握手 (卢卡斯定理求大组合数模质数) -->

<!-- ## 递推型 DP -->

<!-- ### 70. 爬楼梯
### 509. 斐波那契数
### 935. 骑士拨号器
### 957. N 天后的牢房
### 1137. 第 N 个泰波那契数 -->

<!-- ## 概率型 DP -->

<!-- ### 808. 分汤
### 837. 新21点 -->

<!-- ## 博弈型 DP -->

<!-- ### 293. 翻转游戏
### 294. 翻转游戏 II
### 292. Nim 游戏
### 877. 石子游戏
### 1140. 石子游戏 II
### 348. 判定井字棋胜负
### 794. 有效的井字游戏
### 1275. 找出井字棋的获胜者 -->

<!-- ## 记忆化搜索 -->

<!-- ### 329. 矩阵中的最长递增路径
### 576. 出界的路径数 -->
