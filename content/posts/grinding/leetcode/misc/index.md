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
