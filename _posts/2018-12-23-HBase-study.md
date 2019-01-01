---
layout:     post
title:      "HBase学习"
date:       2018-12-23
author:     "xcTorres"
header-img: "img/in-post/books.jpg"
catalog:    true
tags:
    - 编程
    - HBase
---

https://cloud.tencent.com/developer/column/1908/tag-10824


## HBase 协处理器

#### 为什么引入协处理器？
HBase作为列数据库最经常被人诟病的特性包括：无法轻易建立“二级索引”，难以执行求和、计数、排序等操作。

比如，在旧版本(<0.92)的Hbase中，统计数据表的总行数，需要使用Counter方法，执行一次MapReduce Job才能得到。

虽然HBase在数据存储层中集成了MapReduce，能够有效用于数据表的分布式计算。然而在很多情况下，做一些简单的相加或者聚合计算的时候，如果直接将计算过程放置在server端，能够减少通讯开销，从而获得很好的性能提升。于是， HBase在0.92之后引入了协处理器(coprocessors)。 
协处理器实现了一些激动人心的新特性：能够轻易建立二次索引、复杂过滤器以及访问控制等。

#### 灵感来源
HBase协处理器的灵感来自于Jeff Dean 09年的演讲。它根据该演讲实现了类似于bigtable的协处理器，包括以下特性:   
1、每个表服务器的任意子表都可以运行代码。  
2、客户端的高层调用接口 (客户端能够直接访问数据表的行地址，多行读写会自动分片成多个并行的RPC调用)。  
3、提供一个非常灵活的、可用于建立分布式服务的数据模型。  
4。能够自动化扩展、负载均衡、应用请求路由。

HBase的协处理器灵感来自 bigtable，但是实现细节不尽相同。 HBase建立了一个框架，它为用户提供类库和运行时环境，使得他们的代码能够在HBase region server和master上处理。