---
layout:     post
title:      "找工作流水账"
date:       2018-10-30
author:     "xcTorres"
header-img: "img/in-post/offer.jpg"
catalog:    true
tags:
    - 生活
---

## 基本情况 

楼主普通九八五本硕，硕士地理信息系统方向。不是其他帖子里那些手拿BAT offer求比较的大牛，也算运气好找到了份工作。之前没有任何机器学习深度学习相关经验，去年年底打算找互联网算法工作，从零基础准备算法到找工作近一年，体会到个中辛酸和残酷。现在秋招差不多也结束了，便在这根据今年的找到工作经历记个流水账，供以后找工作的同学参考，也给自己近一年找工作的经历总个结，画个句号。

## 建议

众所周知，算法的薪水的确很诱人，且近两年各个行业，如电气物理通信数学统计专业跨行来找算法岗工作的人越来越多，还要跟科班的人一起抢饭碗，竞争异常残酷。 接下来我就按照我找工作的经历谈一下几点。  
1）目前看来算法细分的话，主要是数据挖掘，CV深度学习、NLP三个方向。第一步就是确立好找其中哪一个细分的工作。由于楼主没有CV深度学习基础，最后便打算找数据挖掘推荐方向。  
2）怎么在简历填上有跟算法相关的项目。如果是非科班的，就不会有算法相关的顶刊和项目。所以参加如天池大赛，kaggle等相关比赛是捷径，不论能拿到什么名次，只要是你自己亲身参与的，起码你能让面试官觉得你的简历是匹配的，在面试时有相关的项目可以聊。在这里感谢邦哥，童哥，晶哥，我们也是一起参加比赛丰富项目经验，虽没有拿到好名次，但是对于零基础的楼主后来找到实习，找到工作帮助很大。  
3）如果是去参加比赛，在比赛之前需要哪些基础呢。第一步就是语言基础。只要学会基本的python语法，一般比赛都可以调用一些算法包，外加学会pandas的基本操作，参加这些比赛的语言基础应该就合格了。学会用xgboost，lightgbm这些模型，之后再看李航老师的《统计学习方法》，周志华的西瓜书了解这些基本的原理就行。  
4）通过楼主周围的同学以及楼主本人找工作经历来看，虽然秋招找工作是八九月份，但是春招三四月份的实习机会可能更重要。因为如果能去大场，实习转正的几率肯定比秋招千军万马火拼要来的大得多。且实习如果去的平台好，对于秋招去面其他大场也是有很大优势的。在这里感谢导师，能够放我出去实习~也感谢滴滴的leader，收我去滴滴实习且最后转正。  
5) 除了python语言，c++和java还是要掌握一门的，且在平时刷题应该用c++或java中一门，以及python来做，因为有些问题python真的很取巧，本人一直没有用python刷题，日后感觉吃了不少亏；如果是用c++的话，一定要熟用STL中的vector，map，priority_queue,lower_bound等,因为可以简化很多问题。无论算法AI是不是泡沫，对于程序员来说，普通的算法数据结构，编程能力都是必备的基本素质。

## 面试经历

以上是楼主目前想到的一些注意事项，以下是楼主的一些面试题目。  
#### 2018/08/30 美团外卖

1.逻辑回归 LR推导  
2.交叉熵的理解  
3.因为项目里有用到基于密度峰值聚类，面试官问了DBScan聚类算法原理  
4.在处理大数据使用Spark时，Spark executor丢失的一般原因是什么  
5.在做模型融合时，模型融合加权的方式一般有哪些。  
6.特征做归一化的几种方式，以及各种归一化的区别。 
这是自实习以来第一回面试，当时我是把参与的实习的项目整个写上去了，写的太空太大，然后被面试官强怼，最后导致气场败下阵来，影响到后续回答问题上，奈何一面就凉了。面试官最后专门送我走，把我送上了电梯，还按了按钮，有种赶我走的感觉。记得刚出门有种欲哭无泪的感觉，在望京的地铁站旁坐了个把小时。 
  
#### 2018/09/01 头条

可能宇宙条投递的人太多，面试官对我感觉兴趣不很大，就问了问xgboost的损失函数推导，发现不是非常流畅的写出来之后，就问了个概率题n条记录，等概率取m条（蓄水池抽样），这个当时也没答上来，遂凉。

#### 2018/09/17 华为

简单问了问简历上的项目，面试官是做通信中的算法的，主要问说会不会matab之类的，本硕学校，英语六级之类，是否保研。感觉华为比较看重学校。

#### 2018/09/18 搜狗一二面

1.项目中基于密度峰值聚类的原理  
2.树模型不好处理广告中id这些稀疏特征，一般怎么处理比较好。面试官最后说目前搜狗的方法是Facebook的gbdt+lr模型  
3.编程题 求最长公共子序列  
4.lightgbm xgboost的联系及区别  
5.项目中ffm算法中嵌入层的维度，即隐向量的维度。  
6.二叉树按Z字型广度遍历

#### 2018/09/27 好未来面试

1.深copy，浅copy  
2.判别模型，生成模型。  
3.HMM解决的三个问题；  
4.c++构造函数能否是虚函数  
5.找出最大的k个数，topK  
6.二叉树层次遍历  
7.最近邻算法knn的k怎么取；  
8.boosting算法能否用多个强分类器，效果是否更好。  
9.手推svm  
10.含重复数字的数组求所有排列的总个数

#### 2018/09/27 腾讯一面凉  
1.LR和SVM的区别，优缺点。  
2.map底层红黑树实现 ，红黑树优缺点。 
3.手写快排  
虽然都答上来了但是还是凉了，估计是腾讯所剩的hc已经不多了。

#### 2018/09/28 shopee（新加坡)

一面：面试官首先自我介绍，感觉很亲切友好。然后耐心问我简历中的项目。  
1.做广告点击转化率预测的一些基本问题。  
2.普通的推荐算法，由于我只晓得协同过滤，我就说了协同过滤以及SVD分解之类。  
3.xgboost里面特征重要度排序，然后面试官考了个leetcode的岛屿问题，即二维数组中由1和0组成，求有多少个1构成的连通域。
二面：面试官是 head of data science，是后面hr告诉我的。其之前在新加坡的grab（类似国内滴滴的东南亚打车软件）工作过，便对我简历中滴滴的实习经历比较感兴趣，以及询问我在项目中的任务分工。如何做的数据清洗。后面就说东南亚市场份额很大，且由于东南亚各个国家的环境不同，还有阿里收购的lazada这样的竞争对手，虾皮公司面对的挑战机遇并存。相比于BAT大场，虾皮这样的小规模公司员工个人存在感可能更高等等。  
HR面：主要问有没有在新加坡工作的意愿，有跟家里人商量么。然后说了一些新加坡的生活以及消费之类，感觉很贴心。  

其他大场中，一开始心里首选是杭州，奈何阿里是秋招笔试不通过，网易笔试不通过，只能作罢。京东百度因为时间原因未能参加笔试。还有一些其他公司就没有参加面试了，毕竟面试多了身心俱疲。看完自己的面试历程楼主觉得算法的工作太TM难找了，真的艰辛。  
  

最后只靠拿到了实习转正的滴滴offer和新加坡的Shopee offer。