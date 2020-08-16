---
layout:     post
title:      "最短路径算法"
date:       2020-08-16
author:     "xcTorres"
header-img: "img/in-post/graph/graph.png"
catalog:    true
tags:
    - graph
    - 算法
---

#### Dijkstra 算法
Dijkstra算法是图算法中，寻找两个节点最短路径的算法。在路网做路径规划中，也常常用到该算法的变种。  

- 基本思想  
1. 通过Dijkstra计算图G中的最短路径时，需要指定起点s(即从顶点s开始计算)。  
2. 此外，引进两个集合S和U。S的作用是记录已求出最短路径的顶点(以及相应的最短路径长度)，而U则是记录还未求出最短路径的顶点(以及该顶点到起点s的距离)。  
3. 初始时，S中只有起点s；U中是除s之外的顶点，并且U中顶点的路径是”起点s到该顶点的路径”。然后，从U中找出路径最短的顶点，并将其加入到S中；接着，更新U中的顶点和顶点对应的路径。 然后，再从U中找出路径最短的顶点，并将其加入到S中；接着，更新U中的顶点和顶点对应的路径。 … 重复该操作，直到遍历完所有顶点。

- 证明  
[https://www.cnblogs.com/jiangshaoyin/p/9954937.html](https://www.cnblogs.com/jiangshaoyin/p/9954937.html)

- Demo  
![sample](/img/in-post/graph/dijkstra-demo-0.png)
以上图G4为例，来对迪杰斯特拉进行算法演示(以第4个顶点D为起点)。以下B节点中23应为13。  
![sample](/img/in-post/graph/dijkstra-demo-1.png)

**代码**

leetcod而有个求网络延迟时间的问题，可以由Dijkstra算法解决。
[https://leetcode.com/problems/network-delay-time/submissions/](https://leetcode.com/problems/network-delay-time/submissions/)  

方法一： 邻接图
```python

    class Solution:    
        def networkDelayTime(self, times: List[List[int]], N: int, K: int) -> int:
            
            # init the graph using matrix
            graph = []
            for i in range(N):
                tmp = [sys.maxsize]*N
                tmp[i] = 0
                graph.append(tmp)
                
            for t in times:
                start, end, cost = tuple(t)
                graph[start-1][end-1] = cost

            dist = [sys.maxsize] * N
            dist[K-1] = 0
            sptSet = [False] * N
            for count in range(N):
                
                # Pick the minimum distance vertex from  
                # the set of vertices not yet processed.  
                # u is always equal to src in first iteration 
                min_dis = sys.maxsize
                for v in range(N):
                    if dist[v] < min_dis and sptSet[v] == False: 
                        min_dis = dist[v] 
                        min_index = v
                u = min_index
                sptSet[u] = True
                
                for v in range(N): 
                    if graph[u][v] < sys.maxsize and sptSet[v] == False and dist[v] > dist[u] + graph[u][v]: 
                            dist[v] = dist[u] + graph[u][v] 
            
            res = 0
            for d in dist:
                if d == sys.maxsize:
                    return -1
                res = max(res, d)
                
            return res

```  
    
方法二： 优先队列
```python
    class Solution:
        
        def networkDelayTime(self, times: List[List[int]], N: int, K: int) -> int:
            
                
            graph = {}
            for t in times:
                start, end, cost = tuple(t)
                if start not in graph:
                    graph[start] = {end: cost}
                else:
                    graph[start][end] = cost
            
            h = []
            dis = [sys.maxsize] * (N+1)
            dis[K] = 0
                
            heapq.heappush(h, (0, K))
                
            while h:
                min_dis, u = heapq.heappop(h)
                if dis[u] < min_dis or u not in graph:
                    continue
                    
                for end, cost in graph[u].items():
                    if dis[u] + cost < dis[end]:
                        dis[end] = dis[u] + cost
                        heapq.heappush(h, (dis[end], end))  
                            
                
            res = 0
            for d in dis[1:]:
                if d == sys.maxsize:
                    return -1
                res = max(res, d)
                
            return res
```



#### Bellman-Ford算法  
Bellman-Ford算法同样也是解决单源最短路径问题，但是Dijkstra算法无法解决负权边的问题，而Bellman-Ford可以做到。从Dijkstra算法的证明不难看出其是一种贪心算法。Bellman-Ford基本思想如下：

**步骤：**  
1. 初始化：将除源点外的所有顶点的最短距离估计值 dist[v] ← +∞, dist[s] ←0;  
2. 迭代求解：反复对边集E中的每条边进行松弛操作，使得顶点集V中的每个顶点v到s的最短距离最小。在这里需要运行顶点个数v-1次，其原理是每多运行一次，则相当于允许多加一条边的情况下，各个顶点v到s的最短距离。如果一个顶点是从源点可达的，那么最多则相隔v-1条边。即v-1次后，如若没有负权回路则已经收敛。
3. 检验负权回路：判断边集E中的每一条边的两个端点是否收敛。如果存在未收敛的顶点，则算法返回false，表明问题无解；否则算法返回true，并且从源点可达的顶点v的最短距离保存在 dist[v]中。  

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
[https://blog.csdn.net/heroacool/article/details/51014824](https://blog.csdn.net/heroacool/article/details/51014824)  
[https://www.cnblogs.com/gaochundong/p/bellman_ford_algorithm.html](https://www.cnblogs.com/gaochundong/p/bellman_ford_algorithm.html)  
[https://zhuanlan.zhihu.com/p/36295603](https://zhuanlan.zhihu.com/p/36295603)  
[https://www.geeksforgeeks.org/bellman-ford-algorithm-dp-23/](https://www.geeksforgeeks.org/bellman-ford-algorithm-dp-23/)
