---
layout:     post
title:      "隐马尔科夫模型"
date:       2020-11-08
author:     "xcTorres"
header-img: "img/in-post/HMM/hmm-bg.png"
catalog:    true
mathjax: true
tags:
    - algorithms
---  

# 算法简介  
网上有很多隐马尔科夫算法模型的介绍，内容都非常详实，如果大家感兴趣可在Reference中查阅相关link。本文的目的是对隐马尔科夫模型做一个简单的概括， 并尝试探索其如何应用到**语言领域**和**地图匹配领域**。  

首先最重要的有两个集合  
- 隐藏状态集合  
- 观测状态集合

有三个输入
- 初始状态分布 $ \Pi $
- 状态转移概率分布概率  $ A $
- 观测状态概率矩阵 $ B $  

HMM算法主要可以解决一下三类问题  

### 评估观察序列概率
即给定模型𝜆=(𝐴,𝐵,Π)和观测序列𝑂={𝑜1,𝑜2,...𝑜𝑇}，计算在模型𝜆下观测序列𝑂出现的概率
$ P \left( O |\lambda \right) $。这个问题的求解需要用到前向后向算法。   

前向后向算法用到的是动态规划算法，即可以用递推来存储中间结果，从而将计算量数量级从$ TN^{T}$ 降到了$ TN^{2} $  
  

### 模型参数学习问题 
即给定观测序列𝑂={𝑜1,𝑜2,...𝑜𝑇}，估计模型𝜆=(𝐴,𝐵,Π)的参数，使该模型下观测序列的条件概率
$P \left( O |\lambda \right)$最大。这个问题的求解需要用到基于EM算法的鲍姆-韦尔奇算法，这个问题是HMM模型三个问题中最复杂的。   
  

###  预测问题，也称为解码问题  
即给定模型𝜆=(𝐴,𝐵,Π)和观测序列𝑂={𝑜1,𝑜2,...𝑜𝑇}，求给定观测序列条件下，最可能出现的对应的状态序列，这个问题的求解需要用到基于动态规划的维特比算法。  

关于HMM算法的介绍可参照该link:
[https://github.com/xcTorres/machine_learning/blob/master/HMM.ipynb](https://github.com/xcTorres/machine_learning/blob/master/HMM.ipynb),其中有维特比算法的代码。

# 具体应用

### 算法库
[Hmmlearn](https://hmmlearn.readthedocs.io/en/latest/)是一个比较成熟的算法库，以维特比算法为例，我们要做的就是填好转化概率transform probability matrix以及发射概率emission probability matrix。如下为demo代码示例，隐藏状态为天气情况，下雨☔️或者晴天🌞，而观测状态为人的行为，徒步，购物，或者在家打扫卫生。在定义完转化概率以及发射概率，以及初始概率之后，给定一个观察序列-人的行为，用维特比算法就能得到概率最大的隐藏序列-天气状况。
```python

    import numpy as np
    from hmmlearn import hmm

    states = ["Rainy", "Sunny"]
    n_states = len(states)

    observations = ["walk", "shop", "clean"]
    n_observations = len(observations)

    model = hmm.MultinomialHMM(n_components=n_states, init_params="")
    model.startprob_ = np.array([0.6, 0.4])
    model.transprob_ = np.array([
    [0.7, 0.3],
    [0.4, 0.6]
    ])
    model.emissionprob_ = np.array([
    [0.1, 0.4, 0.5],
    [0.6, 0.3, 0.1]
    ])

    # predict a sequence of hidden states based on visible states
    bob_says = np.array([[0, 2, 1, 1, 2, 0]]).T

    model = model.fit(bob_says)
    logprob, alice_hears = model.decode(bob_says, algorithm="viterbi")
    print("Bob says:", ", ".join(map(lambda x: observations[x], bob_says)))
    print("Alice hears:", ", ".join(map(lambda x: states[x], alice_hears)))

```

### 地图匹配  
在我们收集行车或者骑手GPS序列的数据时，由于GPS数据的误差，这些点都不一定能是刚好在路上的。 而用基于HMM的地图匹配算法我们可以得到映射在路网上的真实轨迹。  如下图可以看出,原始的GPS 1，2，3点都不在路上，他们都有一定概率映射在其附近的道路上，但由于1,2，3点是GPS时间序列，那么他们之间也就产生了联系。所以用HMM算法来解决地图匹配问题就理所当然了。
<img src="/img/in-post/HMM/hmm-1.png" width="300" height="300" title="hmm-1">    

在地图匹配问题中，我们可以理解为隐变量是GPS真实的在其附近候选路上的点序列TracePoint， 那么观察变量就是我们收集的原始的GPS轨迹。接下来就是如何描述发射概率和转换概率：
- 发射概率，即各个路上的TracePoint到其对应的原始GPS的概率，这个可以由$\beta$分布来表达，而$\beta$分布的自变量即是TracePoint到Raw GPS的球面距离，距离越近则该表明TracePoint为此时刻真实路上的GPS点的概率越大。
- 转换概率， 即各个候选路上的TracePoint之间的概率，可以用正态分布来表达这个概率，自变量即是各个TracePoint的network distance即路网距离减去球面距离的差的绝对值。绝对值越小的情况下则代表，两个TracePoint越有可能同在一条路上或相近路上，有很大的概率进行转换。  
<img src="/img/in-post/HMM/hmm-2.png" width="400" height="400" title="hmm-2">  

这些就是HMM应用在地图匹配中的算法原理，在实现过程中，我们所需要的两个API是nearest API（给定一个点，用于寻找其附近的道路，并得到该点在各个道路上的投影点）， route API（给定起点和终点，返回两点之间的路网距离而非球面距离）。有了这两个API就能实现一版简易版本的地图匹配算法了。如下为地图匹配的demo, [https://github.com/xcTorres/machine_learning/tree/master/hmm_demo](https://github.com/xcTorres/machine_learning/tree/master/hmm_demo)。


## Reference  
[https://towardsdatascience.com/introduction-to-hidden-markov-models-cd2c93e6b781](https://towardsdatascience.com/introduction-to-hidden-markov-models-cd2c93e6b781)  
[https://medium.com/@postsanjay/hidden-markov-models-simplified-c3f58728caab](https://medium.com/@postsanjay/hidden-markov-models-simplified-c3f58728caab)  
[https://github.com/hmmlearn/hmmlearn](https://github.com/hmmlearn/hmmlearn)  
[https://zhuanlan.zhihu.com/p/27907806](https://zhuanlan.zhihu.com/p/27907806)  
[https://zhuanlan.zhihu.com/p/38343732](https://zhuanlan.zhihu.com/p/38343732)  
[https://www.cnblogs.com/pinard/p/6945257.html](https://www.cnblogs.com/pinard/p/6945257.html)  
[https://www.cnblogs.com/mindpuzzle/p/3653043.html](https://www.cnblogs.com/mindpuzzle/p/3653043.html)   
[https://github.com/jagodki/Offline-MapMatching](https://github.com/jagodki/Offline-MapMatching) 





