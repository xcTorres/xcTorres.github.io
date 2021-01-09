---
layout:     post
title:      "Bellman ford算法"
date:       2021-01-09
author:     "xcTorres"
header-img: "img/in-post/graph/graph.png"
catalog:    true
mathjax: true

tags:
    - graph
    - algorithms
---    


Bellman-Ford算法同样也是解决单源最短路径问题，从Dijkstra算法的证明不难看出其是一种贪心算法。，因为其有一个大前提-所有边为非负边。所以Dijkstra算法无法解决负权边的问题，而Bellman-Ford可以做到。Bellman-Ford基本思想如下：

**步骤：**  
1. 初始化：将除源点外的所有顶点的最短距离估计值 dist[v] ← +∞, dist[s] ←0;  
2. 迭代求解：反复对边集E中的每条边进行松弛操作，使得顶点集V中的每个顶点v到s的最短距离最小。在这里需要运行顶点个数v-1次。因为如果一个顶点是从源点可达的，那么最多则相隔v-1条边。即v-1次后，如若没有负权回路则已经收敛。
3. 检验负权回路：判断边集E中的每一条边的两个端点是否收敛。如果存在未收敛的顶点，则算法返回false，表明问题无解；否则算法返回true，并且从源点可达的顶点v的最短距离保存在 dist[v]中。  

不难看出其时间复杂度为 $ O(EV) $。

**代码：**

```python

    # Python3 program for Bellman-Ford's single source 
    # shortest path algorithm. 

    # Class to represent a graph 
    class Graph: 

        def __init__(self, vertices): 
            self.V = vertices # No. of vertices 
            self.graph = [] 

        # function to add an edge to graph 
        def addEdge(self, u, v, w): 
            self.graph.append([u, v, w]) 
            
        # utility function used to print the solution 
        def printArr(self, dist): 
            print("Vertex Distance from Source") 
            for i in range(self.V): 
                print("{0}\t\t{1}".format(i, dist[i])) 
        # The main function that finds shortest distances from src to 
        # all other vertices using Bellman-Ford algorithm. The function 
        # also detects negative weight cycle 

	def BellmanFord(self, src): 

		# Step 1: Initialize distances from src to all other vertices 
		# as INFINITE 
		dist = [float("Inf")] * self.V 
		dist[src] = 0


		# Step 2: Relax all edges |V| - 1 times. A simple shortest 
		# path from src to any other vertex can have at-most |V| - 1 
		# edges 
		for _ in range(self.V - 1): 
            # Update dist value and parent index of the adjacent vertices of 
			# the picked vertex. Consider only those vertices which are still in 
			# queue 
			for u, v, w in self.graph: 
			    if dist[u] != float("Inf") and dist[u] + w < dist[v]: 
					dist[v] = dist[u] + w 

		# Step 3: check for negative-weight cycles. The above step 
		# guarantees shortest distances if graph doesn't contain 
		# negative weight cycle. If we get a shorter path, then there 
		# is a cycle. 

		for u, v, w in self.graph: 
			if dist[u] != float("Inf") and dist[u] + w < dist[v]: 
				print("Graph contains negative weight cycle") 
				return
						
		# print all distance 
		self.printArr(dist) 
```

#### 参考  
[https://www.cnblogs.com/gaochundong/p/bellman_ford_algorithm.html](https://www.cnblogs.com/gaochundong/p/bellman_ford_algorithm.html)  
[https://zhuanlan.zhihu.com/p/36295603](https://zhuanlan.zhihu.com/p/36295603)  
[https://www.geeksforgeeks.org/bellman-ford-algorithm-dp-23/](https://www.geeksforgeeks.org/bellman-ford-algorithm-dp-23/)
