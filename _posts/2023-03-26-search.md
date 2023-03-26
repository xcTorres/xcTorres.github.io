---
layout:     post
title:      "Search System"
date:       2023-03-26
author:     "xcTorres"
catalog:    true
mathjax: true
tags:
    - algorithms
    - search
---  

之前在原来的工作中做过一点搜索业务的Query预处理。在后面面试Apple搜索组的时候，面试官也问到了如何设计一个Apple Music搜索系统。当时由于经验不足，感觉答的是一塌糊涂，现在想着有机会系统的了解一下整个搜索系统的结构。 

![](https://intranetproxy.alipay.com/skylark/lark/0/2021/png/318810/1618470126165-fc000bd9-c39b-423b-b4ec-9ee5c2f02e06.png#from=url&id=pQ6RS&margin=%5Bobject%20Object%5D&originHeight=863&originWidth=1617&originalType=binary&ratio=1&status=done&style=none)
ES文本搜索引擎以及faiss这样的向量引擎  

# Query改写
这里应该有Query纠错，Query扩展。
#### Query纠错  
- N grams
- Noisy Channel
- HMM  
- Deep Learning(Transformer)

#### Query扩展  
- Alias


- 关键字召回  
文本匹配，能够做到完全精确的匹配（Exact Match）。通常先对query进行分词，得到更细粒度的词（Term)；再用Term去检索Doc，Term出现于Doc则命中；然后取各个Term检索结果的交集返回。
这里常用ElasticSearch系统，倒排索引查询关键字。当然在导入文档到ES集群时，对于不同语言也需要用不同的分词器。



# 个性化向量召回  
向量引擎faiss这样的向量引擎， Query-Doc双塔模型。 
如果是文档搜索引擎，这里考虑到分别给Query和Doc做embedding。如果是电商，这里是给Query和Item做embedding。  
#### Query Embedding  



#### Doc Embedding
https://radimrehurek.com/gensim/models/doc2vec.html  
https://zhuanlan.zhihu.com/p/136096645


#### Item Embedding  

各个特征占用一个维度，组成dense的向量，并用于双塔模型进行Embedding


# 个性化召回




# 案例分析