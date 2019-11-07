---
layout:     post
title:      "Permutations"
date:       2019-11-07
author:     "xcTorres"
header-img: "img/in-post/leetcode.jpg"
catalog:    true
tags:
    - Leetcode
---  

## 46. Permutations
>**参考:**
[Permutations](https://leetcode.com/problems/permutations/)  

**Example**
```java

    Given a collection of distinct integers, return all possible permutations.

    Example:

    Input: [1,2,3]
    Output:
    [
    [1,2,3],
    [1,3,2],
    [2,1,3],
    [2,3,1],
    [3,1,2],
    [3,2,1]
    ]

```
#### Java Solution
```java

    class Solution {
        
        public List<List<Integer>> permute(int[] nums) {
            
            List<List<Integer>> result = new ArrayList<>();
            
            if(nums.length == 0){
                return result;
            }
            
            dfs(nums, 0, result);
            return result;
        }
        
        public void dfs(int[] curArray, int curIdx, List<List<Integer>> result) {
            
            if(curIdx == curArray.length){
                List<Integer> array = new ArrayList<>(curArray.length);
                for(int num: curArray){
                    array.add(num);
                }
                result.add(array);
            }
            
            for(int i=curIdx; i< curArray.length; i++){
                swap(curArray, curIdx, i);
                dfs(curArray, curIdx+1, result);
                swap(curArray, curIdx, i);
            }
        }
        
        public void swap(int[] array, int idx1, int idx2){
            int tmp;
            tmp = array[idx1];
            array[idx1] = array[idx2];
            array[idx2] = tmp; 
    }
}

```

## 47. Permutations II
>**参考:**
[Permutations II](https://leetcode.com/problems/permutations-ii/)  

**Example**
```java

    Given a collection of numbers that might contain duplicates, 
    return all possible unique permutations.

    Example:

    Input: [1,1,2]
    Output:
    [
    [1,1,2],
    [1,2,1],
    [2,1,1]
    ]

```

#### Java Solution
```java

    class Solution {
            
            public List<List<Integer>> permuteUnique(int[] nums) {
                
                List<List<Integer>> result = new ArrayList<>();
                
                if(nums.length == 0){
                    return result;
                }
                
                dfs(nums, 0, result);
                return result;
            }
            
            public void dfs(int[] curArray, int curIdx, List<List<Integer>> result) {
                
                if(curIdx == curArray.length){
                    List<Integer> array = new ArrayList<>(curArray.length);
                    for(int num: curArray){
                        array.add(num);
                    }
                    result.add(array);
                }
                
                for(int i=curIdx; i< curArray.length; i++){
                    if(!isSwap(curArray,i)){
                        continue;
                    }
                    swap(curArray, curIdx, i);
                    dfs(curArray, curIdx+1, result);
                    swap(curArray, curIdx, i);
                }
            }
            
            public void swap(int[] array, int idx1, int idx2){
                int tmp;
                tmp = array[idx1];
                array[idx1] = array[idx2];
                array[idx2] = tmp; 
            }
        
            public boolean isSwap(int[] array, int index){
                
                for(int i=index+1; i< array.length; i++){
                    if(array[i] == array[index])
                        return false;
                }
                return true;
            }
    }

```
