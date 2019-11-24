---
layout:     post
title:      "动态规划题目"
date:       2019-11-24
author:     "xcTorres"
header-img: "img/in-post/leetcode.jpg"
catalog:    true
tags:
    - Leetcode
---
引自维基百科
> dynamic programming is a method for solving a complex problem by breaking it down into a collection of simpler subproblems.  

Dynamic Programming is a method for solving a complex problem by breaking it down into a collection of simpler subproblems, solving each of those subproblems just once, and storing their solutions using a memory-based data structure (array, map,etc). Each of the subproblem solutions is indexed in some way, typically based on the values of its input parameters, so as to facilitate its lookup. So the next time the same subproblem occurs, instead of recomputing its solution, one simply looks up the previously computed solution, thereby saving computation time. This technique of storing solutions to subproblems instead of recomputing them is called memoization.



简而言之，就是把一个问题分解成多个子问题。但其需要遵循以下几个性质  
1. **无后效性**  
从不同的路径走到一个共同状态，而后续的状态变迁都是一样的，和之前采用何种路径到这个状态没有关系，即前面的各种决策结果由这个状态表示，在考虑后半段的决策方面没有任何区别

#### Triangle问题
[https://leetcode.com/problems/triangle/](https://leetcode.com/problems/triangle/)

```java

    class Solution {
        public int minimumTotal(List<List<Integer>> triangle) {
            
            int n = triangle.size();
            int[] dp = new int[n+1];
            
            for(int i=n-1;i>=0;i--){
                for(int j=0;j<triangle.get(i).size();j++){    
                    dp[j] = Math.min(dp[j], dp[j+1]) + triangle.get(i).get(j);
                }
            }
            
            return dp[0];
        }
    }

```
#### Maximum Subarray（最大子数组和[连续]）
[https://leetcode.com/problems/maximum-subarray/](https://leetcode.com/problems/maximum-subarray/)
```java

    class Solution {
        public int maxSubArray(int[] nums) {
            
            int[] dp = new int[nums.length+1];
            int result = nums[0];
            for(int i=1;i<dp.length;i++){
                dp[i] = nums[i-1] + (dp[i-1]>0?dp[i-1]:0);
                result = Math.max(result, dp[i]);
            }     
            return result;
        }
    }
```

#### 求矩阵从左上到右下角，最小路径和
[https://leetcode.com/problems/minimum-path-sum/](https://leetcode.com/problems/minimum-path-sum/)
```java

    class Solution {
        public int minPathSum(int[][] grid) {
            
            int m = grid.length;
            int n = grid[0].length;
            int[][] dp = new int[m][n];
            
            dp[0][0] = grid[0][0];
            
            for(int i=1; i<m;i++){
                dp[i][0] = dp[i-1][0] + grid[i][0];
            }
            
            for(int j=1; j<n;j++){
                dp[0][j] = dp[0][j-1] + grid[0][j];
            }
            
            for(int i=1;i<m;i++){
                for(int j=1;j<n;j++){
                    dp[i][j] = Math.min(dp[i-1][j], dp[i][j-1]) + grid[i][j];
                }
            }
            
            return dp[m-1][n-1];
            
        }
    }

```  
#### Edit Distance(编辑距离)
```java

    class Solution {
        public int minDistance(String word1, String word2) {
            
            
            int len1 = word1.length();
            int len2 = word2.length();
            int[][] dp = new int[len1+1][len2+1];
            
            for(int j=0;j<=len2;j++)
                dp[0][j] = j;
            
            for(int i=0;i<=len1;i++)
                dp[i][0] = i;
            
            for(int i=1;i<=len1;i++){
                for(int j=1;j<=len2;j++){
                    if(word1.charAt(i-1)==word2.charAt(j-1)){
                        dp[i][j] = dp[i-1][j-1];
                    }else{
                        dp[i][j] = Math.min(Math.min(dp[i-1][j] , dp[i][j-1]),dp[i-1][j-1]) + 1;
                    }     
                }
            }
            return dp[len1][len2];     
        }
    }

```

#### 最长递增子序列  
[https://leetcode.com/problems/longest-increasing-subsequence/](https://leetcode.com/problems/longest-increasing-subsequence/)  

**O(n^2)解法**（也为动态规划）
```java

    class Solution {
        public int lengthOfLIS(int[] nums) {
            
            int[] dp = new int[nums.length];
            for(int i=0; i<nums.length;i++){
                dp[i] = 1; 
            }
            int res = 0;
            for(int i=0;i<nums.length;i++){
                for(int j=0;j<i;j++){
                    if(nums[i]>nums[j]){
                        dp[i] = Math.max(dp[i], dp[j]+1);
                    }   
                }
                res = Math.max(res, dp[i]);
            }
            
            return res;
        }
    }
```

**O(nlgn)解法** 存数组并用二分查找  
```java

    /*
        数组：[10,9,2,5,3,7,101,18]  
        tails[0] = 10 => LIS序列长度为1的子序列，末尾最小为10.  
        tails[0] = 9  => LIS序列长度为1的子序列，末尾最小为9(替换).  
        tails[0] = 2  => LIS序列长度为1的子序列，末尾最小为2(替换).   
        tails[1] = 5  => LIS序列长度为2的子序列，末尾最小为5(添加).   
        tails[1] = 3  => LIS序列长度为2的子序列，末尾最小为3(替换).   
        tails[2] = 7  => LIS序列长度为3的子序列，末尾最小为7(添加).   
        tails[3] = 101  => LIS序列长度为4的子序列，末尾最小为101(添加). 
        tails[3] = 18 => LIS序列长度为4的子序列，末尾最小为18(替换).
    */
    class Solution {
        public int lengthOfLIS(int[] nums) {
            
            if(nums == null || nums.length==0)
                return 0;
            
            int[] tails = new int[nums.length];
            tails[0] = nums[0];
            int len = 0;
            for(int i=0; i<nums.length; i++){
                int idx = binarySearchAndReplace(tails, len, nums[i]);
                if(nums[i] < tails[idx]){
                    tails[idx] = nums[i];
                }
                if(len < idx){
                    tails[idx] = nums[i];
                    len = idx;
                }
            }
            
            return len+1;
        }
        
        public int binarySearchAndReplace(int[] array, int len, int num){
            
            int start = 0;
            int end = len;
            
            while(start<=end){
                
                int mid = start + ((end - start) >> 1);
                
                if(num == array[mid]){
                    return mid;
                }
                
                if(num > array[mid] ){
                    start = mid+1;
                }else if(num < array[mid]){
                    end = mid-1;
                }
            }
            
            return start;
        }
    }

```


