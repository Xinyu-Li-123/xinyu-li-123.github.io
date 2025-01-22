---
date: '2024-11-19T00:54:34-05:00'
draft: false
title: 'LeetCode刷题笔记 - 回溯'
mathjax: true
tags: ['Grinding', 'LeetCode']
---

## 回溯算法 Backtracking

回溯算法是聪明的枚举。其本质仍然是暴力枚举，所以除非n很小，否则很容易TLE。

回溯适用于那些很难的问题，如

- 组合问题：N个数里面按一定规则找出k个数的集合

- 切割问题：一个字符串按一定规则有几种切割方式

- 子集问题：一个N个数的集合里有多少符合条件的子集

- 排列问题：N个数按一定规则全排列，有几种排列方式

- 棋盘问题：N皇后，解数独等等

伪代码如下

```cpp
// Backtracking
void backtracking(param) {
    if (should_end) {
        save result;
        return;
    }

    for (elem : current layer) {
        process node
        backtracing(next_node, path)
        backtrace, undo result
    }
}
```

回溯算法可以抽象为在N叉树上DFS。

### [77. Combinations](https://leetcode.com/problems/combinations/description/)

One trick to make life easier is to store vectors (path and result) as the class's member.

```
class Solution {
private:
    vector<int> nums;
    vector<int> path;
    vector<vector<int>> results;
    int n;
    int k;

    void backtracking(int rem, int startIdx) {
        if (rem == 0) {
            results.push_back(path);
            // for (const auto num : path) {
            //     cout << num << ", ";
            // }
            // cout << endl;
            return;
        }
        // Optimization:
        // If nums[i:].size() < rem, won't have enough 
        element to construct path, so skip
        for (int i = startIdx; i <= nums.size() - rem; i++) {
            int num = nums[i];
            path.push_back(num);
            backtracking(rem-1, i+1);
            path.pop_back();
        }
    }   

public:
    vector<vector<int>> combine(int n, int k) {
        nums = vector<int>(n);
        
        for (int i = 0; i < n; i++) {
            nums[i] = i+1;
        }    
        backtracking(k, 0);
        return results;
    }
};
```

### [216. Combination Sum III](https://leetcode.com/problems/combination-sum-iii/description/)

Done.