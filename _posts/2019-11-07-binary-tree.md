---
layout:     post
title:      "Binary tree"
date:       2019-11-07
author:     "xcTorres"
header-img: "img/in-post/leetcode.jpg"
catalog:    true
tags:
    - Data structure
    - algorithms
---
# Binary tree
A tree whose elements have at most 2 children is called a binary tree. Since each element in a binary tree can have only 2 children, we typically name them the left and right child.  
![binary-tree](/img/in-post/binary-tree.png)

There are different ways to traverse all nodes of binary tree as follows.
### Preorder traversal
[https://leetcode.com/problems/binary-tree-preorder-traversal/](https://leetcode.com/problems/binary-tree-preorder-traversal/)

#### java solution
```java

    /**
    * Definition for a binary tree node.
    * public class TreeNode {
    *     int val;
    *     TreeNode left;
    *     TreeNode right;
    *     TreeNode(int x) { val = x; }
    * }
    */

    // Version 1
    class Solution {
        public List<Integer> preorderTraversal(TreeNode root) {
            
            List<Integer> result = new ArrayList<>();
            if(root==null)
                return result;
            
            Stack<TreeNode> stk = new Stack<TreeNode>();
            TreeNode node = root;
            while(!stk.empty() || node!=null){
                
                while(node!=null){
                    result.add(node.val);
                    stk.push(node);
                    node = node.left;
                }
                node = stk.pop();
                node = node.right;
            }
            
            return result;
        }
    }

    // Version 2
    public List<Integer> preorderIt(TreeNode root) {
		List<Integer> pre = new LinkedList<Integer>();
		if(root==null) return pre;
		Stack<TreeNode> tovisit = new Stack<TreeNode>();
		tovisit.push(root);
		while(!tovisit.empty()) {
			TreeNode visiting = tovisit.pop();
			pre.add(visiting.val);
			if(visiting.right!=null) tovisit.push(visiting.right);
			if(visiting.left!=null) tovisit.push(visiting.left);
		}
		return pre;
	}

```
#### python solution
```python

    def preorderTraversal(self, root):
        ret = []
        stack = [root]
        while stack:
            node = stack.pop()
            if node:
                ret.append(node.val)
                stack.append(node.right)
                stack.append(node.left)
        return ret

            if root is None:
            return []
        
    def preorderTraversal(self, root):
        stk, ret = [], []
        node = root
        while stk or node:
            while node:
                ret.append(node.val)
                stk.append(node)
                node = node.left
        
            node = stk.pop()
            node = node.right
        
        return ret

```
### Inorder traversal
[https://leetcode.com/problems/binary-tree-inorder-traversal/](https://leetcode.com/problems/binary-tree-inorder-traversal/)
#### java solution
```java

    /**
    * Definition for a binary tree node.
    * public class TreeNode {
    *     int val;
    *     TreeNode left;
    *     TreeNode right;
    *     TreeNode(int x) { val = x; }
    * }
    */
    class Solution {
        public List<Integer> inorderTraversal(TreeNode root) {
                    
            List<Integer> result = new ArrayList<>();
            if(root==null)
                return result;
            
            Stack<TreeNode> stk = new Stack<>();
            TreeNode node = root;
            
            while(!stk.empty() || node != null){
                
                while(node != null){
                    stk.push(node);
                    node = node.left;
                }
                
                node = stk.pop();
                result.add(node.val);
                node = node.right;
            }
            
            return result;
        }
    }

```
#### python solution
```python

    class Solution:
        # @param {TreeNode} root
        # @return {integer[]}
        def postorderTraversal(self, root):
            traversal, stack = [], [(root, False)]
            while stack:
                node, visited = stack.pop()
                if node:
                    if visited:
                        # add to result if visited
                        traversal.append(node.val)
                    else:
                        # post-order
                        stack.append((node.right, False))
                        stack.append((node, True))
                        stack.append((node.left, False))

```

### Postorder traversal
[https://leetcode.com/problems/binary-tree-postorder-traversal/](https://leetcode.com/problems/binary-tree-postorder-traversal/)

#### java solution
```java

    /**
    * Definition for a binary tree node.
    * public class TreeNode {
    *     int val;
    *     TreeNode left;
    *     TreeNode right;
    *     TreeNode(int x) { val = x; }
    * }
    */
    class Solution {
        public List<Integer> postorderTraversal(TreeNode root) {
            
            List<Integer> result = new ArrayList<>();
            if(root==null)
                return result;
            
            Stack<TreeNode> stk = new Stack<TreeNode>();
            
            TreeNode node = root;
            TreeNode lastVisited = root;
            
            while(!stk.empty() || node!=null){
                
                while(node!=null){
                    stk.push(node);
                    node = node.left;
                }
                
                node = stk.peek();
                
                if(node.right==null || node.right==lastVisited){
                    
                    result.add(node.val);
                    stk.pop();
                    lastVisited = node;
                    node = null;
                    
                }else{
                    node = node.right;
                }
            }
            return result;
        }
    }

```

#### python solution
```python

    class Solution:
        # @param {TreeNode} root
        # @return {integer[]}
        def postorderTraversal(self, root):
            traversal, stack = [], [(root, False)]
            while stack:
                node, visited = stack.pop()
                if node:
                    if visited:
                        # add to result if visited
                        traversal.append(node.val)
                    else:
                        # post-order
                        stack.append((node, True))
                        stack.append((node.right, False))
                        stack.append((node.left, False))

    class Solution:
    def postorderTraversal(self, root: TreeNode) -> List[int]:
        
        if root is None:
            return []
        
        stk,ret = [],[]
        node, last_visited = root, root
        
        while stk or node:
            while node:
                stk.append(node)
                node = node.left
            
            node = stk[-1]
            if node.right is None or last_visited == node.right:
                ret.append(node.val)
                last_visited = stk.pop()
                node = None
            else:
                node = node.right
        
        return ret
                
        

```
