---
title: 'LeetCode刷题笔记 - 栈与队列'
date: 2024-11-20T22:41:16-05:00
draft: false
mathjax: false
tags: ['Grinding', 'LeetCode']
---
## 栈

### [394. 字符串解码](https://leetcode.cn/problems/decode-string/description)

将字符串类似`3[abc]`的字符串转换为`abcabcabc`,`2[abc]3[cd]ef`转换为`abcabccdcdcdef`。

解法是从右往左扫描字符串，维护一个栈`stack`，栈里第 k 个元素是对于嵌套层数为 n - k 的方括号，当前能构造的字符串。具体逻辑如下：

- On "]", create empty str and push to stack

- On chars, prepend to str at stack top

- On "[", pop str from stack, ready for duplicate by k

- On num, duplicate prev str, and push new str to top stack

### [295. 数据流的中位数](https://leetcode.cn/problems/find-median-from-data-stream/description)

设计一个类`MedianFinder`，提供两个 API :

- `addNum(num: int) -> None`：添加一个数字

- `findMedian() -> int`：找出添加过的所有数字的中位数

解法思路是维护一个较小数的最大堆`smallNums`，和较大数的最小堆`largeNums`，满足以下条件

- `smallNums[i] <= smallNums.top() <= largeNums.top() <= largeNums[j]` for all i, j

- 平分数组：`len(smallNums) == len(largeNums) or len(smallNums == len(largeNums) + 1`。这样，中位数就是`smallNums.top()`或`(smallNums.top() + largeNums.top()) / 2`

## 单调队列

### [347. Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/description/)

Iterate over the array to compute frequency of each element, and use a max heap (priority queue) to record top k most frequent elements.

## 单调栈

### [739. Daily Temperatures](https://leetcode.com/problems/daily-temperatures/description/)

一个自底向上单调递增的栈，储存`(day, temperature)`。入栈前先把所有小于当前温度的天弹出，同时记录这些天和当前天的差距。

### [496. Next Greater Element I]()

Constraint: Solution must be `O(nums1.length + nums2.length)`

### [503. Next Greater Element II](https://leetcode.com/problems/next-greater-element-ii/description/)

For array `nums`, duplicate `nums` to `double_nums = nums + nums`, and do the monotone stack thing as in 496.

### [42. Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/description/)

#### Double pointer (more intuitive)

Compute the amount of water trapped at each column.

For column `i`, the amount of water trapped at column `i` is determined by **the shorter bar between the tallest bar on the left and the taller bar on the right**. That is,

```cpp
trappedWater = min(max(heights[:i]), max(heights[i+1:])) - heights[i];
```

For example, consider column 3 of height 1, column 4 is of height inf, column 0, 1, 2 are of height 3, 6, 4. The tallest left bar has height 6, and tallest right bar has height inf. So `min(max([3,6,4]), inf) - 1 = 5` water can be trapped at column 3.

To avoid redundent computation, we first compuet `maxLeft` and `maxRight` for all columns, then compute the amount of water trapped at each column.

```cpp
int trap(vector<int>& height) {
    int n = height.size();
    vector<int> maxLeft(n);
    vector<int> maxRight(n);

    maxLeft[0] = height[0];
    for (int i = 1; i < n; i++) {
        maxLeft[i] = max(height[i], maxLeft[i-1]);
    }

    maxRight[n-1] = height[n-1];
    for (int i = n-2; i >= 0; i--) {
        maxRight[i] = max(height[i], maxRight[i+1]);
    }

    int count = 0;
    for (int i = 1; i < n-1; i++) {
        count += min(maxLeft[i], maxRight[i]) - height[i];
    }

    return count;
}
```

#### Prev solution

1. Scan from left to right to find all ponds with left bar <= right bar;

2. Scan from right to left to find all ponds with left bar > right bar;

3. Sum the two results to get total pond size.

Don't really need a monotone stack...

### [84. Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/description/)

For bar i, consider the max rectangle that contains bar i. This rectangle must consist of consecutive bars where each bar is no shorter than bar i.

首先，最大长方形一定会刚好包含一根柱子，既高度等于某一根柱子。这是因为任何符合提议的长方形，其高度不大于所包含的柱子。假如最大长方形的高度小于所有被包含的长方形，那么在其基础上往上扩展一格仍符合题意，且面积更大。

由此可知，我们只需要**对每一个柱子，考虑完整包含它的最大长方形就可以**。

对于柱子i，**刚好包含它的最大长方形由一连串经过柱子i，且高度不小于柱子i的柱子组成**。它的高度和柱子i相同，**长度则是由柱子i左右第一根高度小于i的柱子决定**。

为防止重复计算，我们提前计算`minLeft`和`minRight`。在计算`minLeft[k]`时，我们可以通过已经计算的`minLeft[:k]`简化计算。

由此可得算法

```cpp
int largestRectangleArea(vector<int>& heights) {
    int n = heights.size();
    // minLeft[i] is the index of first bar to the left of bar i w/ height < bar i
    // we prepend and append a 0 to heights, so that such bar must exists left and right.
    vector<int> minLeft(n+2);
    vector<int> minRight(n+2);
    heights.insert(heights.begin(), 0);
    heights.push_back(0);

    minLeft[0] = 0;
    for (int curIdx = 1; curIdx < n+1; curIdx++) {
        int leftIdx = curIdx-1;
        while (leftIdx > 0) {
            if (heights[leftIdx] < heights[curIdx]) {
                break;
            }
            leftIdx = minLeft[leftIdx];
        }
        minLeft[curIdx] = leftIdx;
        // cout << leftIdx << ", ";
    }
    // cout << endl;

    minRight[n+1] = n+1;
    for (int curIdx = n; curIdx >= 0; curIdx--) {
        int rightIdx = curIdx+1;
        while (rightIdx < n+1) {
            if (heights[rightIdx] < heights[curIdx]) {
                break;
            }
            rightIdx = minRight[rightIdx];
        }
        minRight[curIdx] = rightIdx;
        // cout << rightIdx << ", ";
    }
    // cout << endl;

    int maxRect = 0;
    for (int i = 1; i < n+1; i++) {
        int curRect = (minRight[i] - minLeft[i] - 1) * heights[i];
        maxRect = max(maxRect, curRect);
    }
    return maxRect;
}
```

