---
layout:     post
title:      "匈牙利算法介绍"
date:       2019-12-01
author:     "xcTorres"
header-img: "img/in-post/leetcode.jpg"
catalog:    true
tags:
    - algorithms
---
## 背景
因为入职不久，最近在接手一个外卖的分配问题，即在一个区域同时产生多个订单，且该区域有多个骑手，在只考虑一个骑手只能接一单的情况下，订单与骑手之间到底应该如何分配。在第一版解决方案中我们使用的是匈牙利算法，目前还在测试当中，还没有上线，希望其能有不错的效果。写此博客，专门为了好好了解其基本原理，而不是只会按部就班写个库，跟着去做矩阵运算。  

## 匈牙利算法原理  
在了解匈牙利算法之前，首先需要掌握几个图论中的基本概念。 

**二分图**：在图论中，二分图是一类特殊的图，又称为双分图、二部图、偶图。二分图的顶点可以分成两个互斥的独立集U和V的图，使得所有边都是连结一个U中的点和一个V中的点。顶点集 U、V 被称为是图的两个部分。等价的，二分图可以被定义成图中所有的环都有偶数个顶点。

<img src="/img/in-post/Bipartite graph.png" width="200" height="200" title="二分图">  

**匹配**：在图论中，一个「匹配」（matching）是一个边的集合，其中任意两条边都没有公共顶点。例如，图 3、图 4 中红色的边就是图 2 的匹配。  

| --- | --- | --- | --- | 
| <img src="/img/in-post/graph_1.png" width="100" height="100"> | <img src="/img/in-post/graph_2.png" width="100" height="100"> | <img src="/img/in-post/graph_3.png" width="100" height="100"> | <img src="/img/in-post/graph_4.png" width="100" height="100"> |  

我们定义匹配点、匹配边、未匹配点、非匹配边，它们的含义非常显然。例如Fig.3中 1、4、5、7 为匹配点，其他顶点为未匹配点；1-5、4-7为匹配边，其他边为非匹配边。

**最大匹配**：一个图所有匹配中，所含匹配边数最多的匹配，称为这个图的最大匹配。图 4 是一个最大匹配，它包含 4 条匹配边。

**完美匹配**：如果一个图的某个匹配中，所有的顶点都是匹配点，那么它就是一个完美匹配。图 4 是一个完美匹配。显然，完美匹配一定是最大匹配（完美匹配的任何一个点都已经匹配，添加一条新的匹配边一定会与已有的匹配边冲突）。但并非每个图都存在完美匹配。

**增广路径**


## KM算法


## 参考  
[https://www.renfei.org/blog/bipartite-matching.html](https://www.renfei.org/blog/bipartite-matching.html)  
[https://www.geeksforgeeks.org/hungarian-algorithm-assignment-problem-set-1-introduction/](https://www.geeksforgeeks.org/hungarian-algorithm-assignment-problem-set-1-introduction/)
[https://keson96.github.io/2016/08/29/2016-08-29-Assignment-Problem-And-Hungrian-Method/](https://keson96.github.io/2016/08/29/2016-08-29-Assignment-Problem-And-Hungrian-Method/)  
[https://www.youtube.com/watch?v=rrfFTdO2Z7I](https://www.youtube.com/watch?v=rrfFTdO2Z7I)
[http://longrm.com/2018/05/05/2018-05-05-KM/](http://longrm.com/2018/05/05/2018-05-05-KM/)
