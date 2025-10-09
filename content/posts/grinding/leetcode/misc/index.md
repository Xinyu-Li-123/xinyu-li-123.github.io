---
title: 'LeetCode刷题笔记 - 杂项'
date: 2024-11-20T22:41:16-05:00
draft: false
mathjax: true
tags: ['Grinding', 'LeetCode']
---

## 哈希表

### [15. 3Sum](https://leetcode.com/problems/3sum/description/)

题目：给定一个数组，寻找所有和为0的三元组，要求任意两个三元组不能含有完全相同的数字，例如`[1, 1, 2]`和`[1, 2, 1]`只能取一个。

从2sum类推，我们可以先预先计算两元组之和，并构造`和 -> [两元组, 两元组, ...]`的哈希表，预先记录和为特定值的所有二元组。然后遍历所有数`n`，在哈希表中寻找和为`-n`的二元组，以此构造三元组。

为了防止重复记录，我们采用以下设计

- 对数组排序，在遍历时跳过重复的数字

    排序后，重复的数字一定相连

- 要求三元组的顺序必须符合排序后的数组顺序

算法如下：

```cpp
vector<vector<int>> threeSum(vector<int>& nums) {
    // To avoid duplicate, we enforce each triplet to be ordered
    // and skip over duplicated elements when calculating.
    
    // sum => list of ordered pair with sum
    unordered_map<int, vector<pair<int, int>>> mem;
    vector<vector<int>> results; 

    sort(nums.begin(), nums.end());

    int n = nums.size();
    int i = 0;
    int j;

    // map sum to list of pairs
    int curi, curj;
    while (i < n) {
        curi = nums[i];
        int j = i+1;
        while (j < n) {
            curj = nums[j];
            // add pair to mem
            int sum = curi + curj;
            if (mem.find(sum) == mem.end()) {
                mem[sum] = vector<pair<int, int>>{};
            }
            mem[sum].emplace_back(i, j);
            // skip j over dup elem
            while (j+1 < n && nums[j+1] == nums[j]) {
                j++;
            }
            j++;
        }
        // skip i over dup elem
        while (i+1 < n && nums[i+1] == nums[i]) {
            i++;
        }
        i++;
    }

    // find num equal to negative sum
    int k = 0;
    while (k < n) {
        // skip k over dup elem. Need to do this first, o/w we will select same index as i and skip all the duplicate.
        // think about [1,1,1,1,1,1]. targetSum=3, pairSum=2, i=0, j=1.
        // if we start k = 0, we will skip all 1's.
        // instead, we start k at the last one of the duplicated elements
        while (k+1 < n && nums[k+1] == nums[k]) {
            k++;
        }
        int curk = nums[k];
        if (mem.find(-curk) != mem.end()) {
            for (auto [i, j] : mem[-curk]) {
                if (k <= j) {
                    continue;
                }
                int curi = nums[i];
                int curj = nums[j];
                results.push_back(vector<int>{curi, curj, curk});
            }
        }    
        k++;
    }

    return results;
}
```

## 双指针 / 快慢指针

### 图中找环

### [3. Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/description/)

双指针，start指向子字符串的首，end指向子字符串的尾。end向前迭代，过程中在一个集合里记录见过的所有字母

- 如果无重复，end++

- 如果有重复，start++，过程中把start经过的字母移出集合，直到集合中不再有当前字母。

### [76. 最小覆盖子串](https://leetcode.cn/problems/minimum-window-substring/description)

双指针收缩和扩展窗口。指针移动过程比较复杂，容易出错。

一些简化解题的思路

- 不要在一次循环中做太多事情，比如遇到不在`t`中的字符时，直接跳到下一次循环，而非在一个循环内遍历到在`t`中的字符。

- 判断`s`的子字符串是否覆盖`t`，只需要`O(1)`时间，所以可以大胆使用这个操作。

```python
class Solution:
    def minWindow(self, s: str, t: str) -> str:
        m = len(s)
        n = len(t)
        if m < n:
            return ""
        
        freq_t = {}
        for ch in t:
            if ch not in freq_t:
                freq_t[ch] = 1
            else:
                freq_t[ch] += 1
        
        freq_s = {ch: 0 for ch in freq_t}
        # consider substring s[left: right+1]
        result = None
        left = 0
        right = 0

        # start window at first matching char
        while left < m:
            if s[left] in freq_t:
                break
            left += 1
        right = left

        while right < m:
            r_ch = s[right]
            if r_ch not in freq_t:
                right += 1
                continue
            
            # expand window with matching char (move right ptr)
            freq_s[r_ch] += 1
            if not self.has_s_cover_t(freq_s, freq_t):
                right += 1
                continue;
            # print(f"after expanding, with cover, left={left}, right={right}, sub_s={s[left: right+1]}")
            if result is None or right - left + 1 < len(result):
                result = s[left: right+1]

            # shrink window till min if possible (move left ptr)
            while left <= right:
                l_ch = s[left]
                if l_ch not in freq_t:
                    left += 1
                    continue
                freq_s[l_ch] -= 1
                left += 1
                # stop shrinking if won't cover
                if not self.has_s_cover_t(freq_s, freq_t):
                    freq_s[l_ch] += 1
                    left -= 1
                    break 
            
            # print(f"after shriking, with cover, left={left}, right={right}, sub_s={s[left: right+1]}")
            if result is None or right - left < len(result):
                result = s[left: right+1]
            
            right += 1

        if result is None:
            return ""
        return result
        
    def has_s_cover_t(self, freq_s, freq_t) -> bool:
        """time complexity of one run is O(56) = O(1)"""
        for (ch, cnt) in freq_t.items():
            if ch not in freq_s:
                return False
            if freq_s[ch] < freq_t[ch]:
                return False
        return True
```

## KMP

**KMP思路**

在字符串haystack中，匹配字符串needle，返回needle第一次出现的位置。例如在"ababcaababcaabc"中匹配"ababcaabc"，返回6。

KMP算法的核心是：在遍历haystack时，如果当前字符串不匹配，不需要重新从needle[0]开始匹配，而是可以利用needle相同的前后缀少回退几步。

我们对needle计算数组`lps`，`lps[i] = p`表示`needle[0: p] == needle[i-p+1: i+1]`，假如在匹配haystack[:j+1]和needle[:i+1]时，发现`haystack[j] != needle[i]`，由于在上一次迭代中已经确定了`haystack[j-i: j] == needle[0: i]`，我们可以使用`lps`数组简化计算

- 已知`haystack[j-i: j] == needle[0: i]`

- 令`lps[i-1] = p`，则可知`needle[0: p] == needle[i-p: i]`

- 由此可知`haystack[j-i: j-i+p] == needle[i-p: i]`，

因此我们可以直接比较字母`haystack[j-i+p+1]`和`needle[i+1]`，以比较字符串`haystack[j-i: j-i+p+1]`和`needle[i-p: i+1]`是否相等。

图例如下

```
haystack    = ababcaababcaabc
needle      = ababcaabc

    a b a b c a a b c

lsp:0 0 1 2 0 1 1 2 0

Example of algorithm: 

Say we have matched up to haystack[0: 8] == needle[0: 8], 
and now we will compare haystack[8] and needle[8]

ababcaababcaabc
--------^
ababcaabc
--------^

- haystack[8] = a, needle[8] = c, not equal! 

- lps[8-1] = 2, we know needle[6: 8] == needle[0: 2] == haystack[0: 2]

now we compare haystack[8] and needle[2]

ababcaababcaabc
      --^
ababcaabc
--^      

- haystack[8] = a, needle[2] = a, equal! Now we know haystack[5: 8] == needle[0: 3], move on.
```

**计算`lps`数组的思路**

在构造`lps`数组时，我们可以用`lps[:i]`简化计算`lps[i]`。

以下面的lps为例，加入我们已经计算了lps[:9]，现在要计算lps[9]，

```
    a a b a a a b a a b

lsp:0 1 0 1 2 2 3 4 5 ?

- lps[8] = 5, meaning that neelde[:5] == needle[8+1-5: 8+1] = needle[4: 9]

- We can compare needle[5] and needle[9] to see if needle[:6] == needle[4: 10].

- Not equal, jump backward. 

    We consider the at the longest prefix which is suffix in needle[:6], and in needle[4: 10]. 
    Since the two substring equals, all these prefix/suffix equal to each other. 
    This allow us to jump back only to lps[needle[4]], 
    and compare needle[:lps[needle[4]]] with needle[9-needle[4]: 10].
```

由此可得KMP算法实现如下

```cpp
class Solution {
private:
    void compute_lps(vector<int>& lps, string needle) {
        lps[0] = 0;
        for (int i = 1; i < needle.size(); i++) {
            int j = lps[i - 1];
            while (j > 0 && needle[j] != needle[i]) {
                j = lps[j - 1];
            }
            if (needle[j] == needle[i]) {
                lps[i] = j + 1;
            } else {
                lps[i] = 0;
            }
        }
    }

public:
    int strStr(string haystack, string needle) {
        // Longest prefix that is also suffix
        // For lps[i] = p, we have needle[0:p] == needle[i-p+1:i+1]
        // e.g.
        // For needle = AABBAAC, lps[5] = 2, meaning needle[0:2] = needle[4:6]
        vector<int> lps(needle.size(), 0);
        compute_lps(lps, needle);

        int ni = 0;
        int hi = 0;
        while (hi < haystack.size() && ni < needle.size()) {
            if (haystack[hi] == needle[ni]) {
                hi++;
                ni++;
                continue;
            }

            while (ni > 0 && haystack[hi] != needle[ni]) {
                ni = lps[ni - 1];
            }

            if (haystack[hi] == needle[ni]) {
                hi++;
                ni++;
            } else {
                hi++;
            }
        }

        if (ni == needle.size()) {
            return hi - needle.size();
        } 
        return -1;
    }
};
```

### Implement substr

## 前缀和 Prefix Sum

关键性质：

```python
pre[i] = sum(mylist[:i])
pre[j] - pre[i] = sum(mylist[i:j])
```

### [560. 和为 K 的子数组](https://leetcode.cn/problems/subarray-sum-equals-k/description/?envType=study-plan-v2&envId=top-100-liked)

Two-sum over prefix sum array.

在前缀和数组`pre`中寻找`i, j`，使得`i < j`，`pre[j] - pre[i] = target_sum`。根据前缀和定义，`pre[j] - pre[i] := sum(nums[i: j])`。

```python
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        # two-sum on prefix sum array
        n = len(nums)
        # pre[i] = sum(nums[:i])
        # pre[j] - pre[i] = sum(nums[i: j])
        pre = [0 for _ in range(n+1)]
        for i, num in enumerate(nums):
            pre[i+1] = pre[i] + num
        
        # mem[pre_j] = [i1, i2, i3]: pre_j - pre_i1 = k (same for i2, i3)
        mem = {}
        # look for (i, j) s.t. k = pre[j] - pre[i] := sum(nums[i: j])
        for i, pre_i in enumerate(pre):
            target_pre_j = k + pre_i
            if target_pre_j not in mem:
                mem[target_pre_j] = [i]
            else:
                mem[target_pre_j].append(i)
        
        count = 0
        for j, pre_j in enumerate(pre):
            if pre_j in mem:
                for i in mem[pre_j]:
                    if i >= j:
                        break
                    count += 1
        
        return count 

```

### [53. 最大子数组和](https://leetcode.cn/problems/maximum-subarray/description)

前缀和 + DP

转换成前缀和，遍历前缀和数组，令当前下标为`cur`，我们维护`left_pre_min = min(pre[:cur])`，既在当前下标左侧的前缀和中的最小值。这可以用于计算以`cur`为结尾的子数组中的最小子数组和。

```python

class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        # convert to prefix sum, iterate from left to right, maintain smallest prefix sum to the left of cur_idx, that gives the max subarray sum in subarray nums[:cur_idx+1]
        pre = Solution.toPrefixSum(nums)
        # min prefix sum to the left of cur idx
        left_pre_min = pre[0]
        max_sum = pre[1]
        for cur in range(1, len(nums)+1):
            left_pre_min = min(left_pre_min, pre[cur-1])
            max_sum = max(max_sum, pre[cur] - left_pre_min)
            # print(f"left_pre_min={left_pre_min}, max_sum={max_sum}")
        return max_sum


    def toPrefixSum(nums: List[int]) -> List[int]:
        """
        pre[i] = sum(nums[:i]) = nums[0] + nums[1] + ... + nums[i-1]
        sum(nums[i: j]) = pre[j] - pre[i]
        """
        pre = [0 for _ in range(len(nums)+1)]
        for i, num in enumerate(nums):
            pre[i+1] = num + pre[i]
        return pre
```

### [238. 除自身以外数组的乘积](https://leetcode.cn/problems/product-of-array-except-self/description)

维护前缀积和后缀积，用于对每个下标计算乘积

```python
class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        # We compute prefix product and suffix product

        n = len(nums)
        # product of nums before nums[i]
        # prefix[i] = 1 * nums[0] * nums[1] * ... * nums[i-1], i=1...n
        prefix = [1 for _ in range(n+1)]
        # product of nums after nums[i]
        # suffix[i+1] = 1 * nums[i+1] * nums[i+2] * ... * nums[n-1], i=n-2...0
        suffix = [1 for _ in range(n+1)]
        for i in range(n):
            num = nums[i]
            prefix[i+1] = prefix[i] * num
        for i in range(n-1, -1, -1):
            num = nums[i]
            suffix[i] = suffix[i+1] * num

        results = [1 for _ in range(n)]
        for i in range(n):
            results[i] = prefix[i] * suffix[i+1]
        
        return results
```

### [42. 接雨水](https://leetcode.cn/problems/trapping-rain-water/description)

在列`i`上，能存储的雨水取决于列`i`左侧最高柱子和右侧最高柱子的长度，即

```python
leftBorderHeight = max(height[:i])
rightBorderHeight = max(height[i+1:])
borderHeight = min(leftBorderHeight, rightBorderHeight)
rain[i] = 0 if borderHeight <= height[i] else borderHeight - height[i]
```

如果对每个柱子都计算一次左侧和右侧的最大值，时间复杂度就是`O(N)`，由于`N = 2e4`，复杂度太高。

我们借鉴前缀和的思想，对每个列维护前缀最大值和后缀最大值，即

```python
prefixLeftBorder[i] = max(height[:i]) = max(prefixLeftBorder[i-1], height[i-1])
suffixRightBorder[i] = max(height[i+1:]) = max(suffixRightBorder[i+1], height[i+1])
```

### [437. 路径总和 III](https://leetcode.cn/problems/path-sum-iii/description)

求从父节点到子节点路径和为X的路径总数。

方法是在树上计算前缀和，使用类似回溯的方法，维护一个哈希表，记录所经历路径的前缀和（前缀和的值 -> 前缀和出现次数），并在当前节点寻找是否有相减为X的前缀和。

## 区间

好像按左边界 / 右边界排序后，总会有解法

### [56. 合并区间](https://leetcode.cn/problems/merge-intervals/description)

按左边界排序，从左往右合并

### [452. Minimum Number of Arrows to Burst Balloons](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/description/)

区间调度问题，按右边界排序，然后从小到大：选取区间，删除所有重叠区间，循环

## 矩阵

## 无法分类

### [189. 轮转数组](https://leetcode.cn/problems/rotate-array/description)

#### 解法1：开一个数组用于存储轮转后的数组

#### 解法2: GCD (?)

没看懂，数论难啊

详见[这篇帖子](https://leetcode.cn/problems/rotate-array/solutions/551039/xuan-zhuan-shu-zu-by-leetcode-solution-nipk)

#### 解法3：三次翻转

翻转完整数组，然后翻转`arr[:k]`，然后翻转`arr[k:]`

注意，我们需要使用`k % n`，而非`k`，因为`k`可以大于`n`（多转几圈）

### [41. 缺失的第一个正数](https://leetcode.cn/problems/first-missing-positive/description)

注意到，对于长度为`N`的数组，其第一个缺失的正整数最大只能是`N+1`。这是因为如果第一个缺失正整数为`M > N` (如`M = N+10`，数组需要储存`1, 2, ..., M-1`（如`1, 2, ..., N+9`），即`M-1`个数字。这超出了数组长度，因此不可能。

我们把数组本身当作一个哈希表，使用以下哈希函数重新放置数组中各数字

```python
def hash(num: int):
  assert(num > 0 and num <= len(nums))
  return num-1
```

题解为

```python
class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        # For an array of size N, the largest possible missing positive number is N+1, in the case of arr = [1, 2, ..., N]

        # swap numbers to makes nums[i] = i+1 if possible
        # after swapping, for the first i s.t. nums[i] != i, we know i+1 is the missing positive number

        n = len(nums)

        # print(nums)
        for i in range(n):
            while (nums[i] > 0) and (nums[i] <= n) and (nums[i] != i+1) and (nums[i] != nums[nums[i]-1]):
                j = nums[i]-1
                # print(f"swap nums[{i}]={nums[i]} with nums[{j}]={nums[j]}")
                nums[i], nums[j] = nums[j], nums[i]
                # print(nums)
            
        for i, num in enumerate(nums):
            if num != i + 1:
                return i + 1
        return n + 1
```

关于while loop：在for loop中，我们使用一个while loop一直交换数字，直到以下两个条件中有一个成立

1. `nums[i]`符合要求（`nums[i] == i + 1`）

2. 无法交换（`nums[i] not in range(1, n+1)`，或`nums[i] == nums[nums[i]-1]`，使得交换进入死循环）

即使使用了while loop，时间复杂度仍然是`O(N)`。这是因为任意一个数字都只会被处理一次。

### [73. 矩阵置零](https://leetcode.cn/problems/set-matrix-zeroes/description)

最基础的方法是使用两个数组，一个用来追踪每一行是否出现0，一个用来追踪每一列是否出现0。这个方法时间`O(mn)`，空间`O(m+n)`。

一个更好的方法是直接使用矩阵的第一行和第一列，用来追踪行 / 列中是否出现0。这会覆盖第一行第一列原来的值，所以我们额外使用两个变量用来表示第一行和第一列是否出现0。

```python
class solution:
    def setzeroes(self, matrix: list[list[int]]) -> none:
        """
        do not return anything, modify matrix in-place instead.
        """
        # matrix[i] is row i, matrix[i][j] is row j col j

        m = len(matrix)
        n = len(matrix[0])

        # use two variables to track if row 0 & col 0 contains zero
        row0_contain_zero = any(matrix[0][j] == 0 for j in range(n))
        col0_contain_zero = any(matrix[i][0] == 0 for i in range(m))

        for i in range(1, m):
            for j in range(1, n):
                if matrix[i][j] == 0:
                    matrix[i][0] = 0
                    matrix[0][j] = 0
        
        for i in range(1, m):
            for j in range(1, n):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0
        
        if row0_contain_zero:
            for j in range(n):
                matrix[0][j] = 0

        if col0_contain_zero:
            for i in range(m):
                matrix[i][0] = 0
```

进一步优化，我们可以只使用一个变量，用来追踪第一列是否有0。这需要我们从最后一行开始，倒序处理元素，以防每一列的第一个元素被提前覆盖。

```python
class Solution:
    def setZeroes(self, matrix: List[List[int]]) -> None:
        m, n = len(matrix), len(matrix[0])
        flag_col0 = False
        
        for i in range(m):
            if matrix[i][0] == 0:
                flag_col0 = True
            for j in range(1, n):
                if matrix[i][j] == 0:
                    matrix[i][0] = matrix[0][j] = 0
        
        for i in range(m - 1, -1, -1):
            for j in range(1, n):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0
            if flag_col0:
                matrix[i][0] = 0
```
