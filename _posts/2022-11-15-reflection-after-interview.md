---
layout:     post
title:      "Reflection After Interview"
author:     "xcTorres"
header-img: "img/in-post/reflect.jpg"
catalog:    true
mathjax: true

tags:
    - Leetcode
    - Deep Learning
---  

It has been 3 years working in Singapore since I graduated. During the period in Shopee, I learned a lot not only the coding skills but also the understanding of projects. Since Shopee has decided to shift the engineering center to China mainland, the projects that we Singapore team could do are becoming limited, which result in the thoughts to pursue other opportunities.  

There are not many opportunities avaliable in Singapore as expected, some local big company like Lazada and Grab freeze their head count, Amreican company like Google and facebook also don't have enough engineer head count. I got my permanent resident before I subimitted my CV, which helps me a lot to have more interview opportunities. Here are recent interview experience, unluckily I don't have any offer due to short of time to fully prepare.

# Interview  
#### Tiktok  
- **Machine learning engineer(recommendation)**  
Because of lack of recomendation-related experience, the interviewer in both 2 rounds doesn't have too much interests on my experience. So the coding problem appears to be very important，but I didn't prepare for a long time so coding performance sucks, failed the interview.  
  1st round: Leetcode 3(Longest Substring Without Repeating Characters)  
  2nd round: Leetcode 297(Serialize and Deserialize Binary Tree)

- **Machine learning engineer(platform governance)**  
Bert: how to pretrain; Q, K, V  
batch norm and layer norm  
How does GBDT do classfication?  
How to pretrain your own Bert?

#### Indeed  
The coding problem is easy, merge 2 sorted array. Here are some machine learning related problems.  

- Unfair coin(Bayesian probability)  
- Overfitting and underfitting  
- Variance, boosting and bagging  
- Dropout mechanisum


#### Apple
Coding: Top k frequent elements  
word2vec, Search System introduction, Bilstm-CRF


#### Huawei
leetcode: lognest valid parentheses, coin change  


#### Grab  
leetcode 1011

# Reflection  
To be honest, I am frustrated for a while, but I think I deserve it because I didn't fully prepare the coding and related machine learning knowledge on the CV. Right now I don't have chance and have to change my mind to look for new roles at the end of the year. It is not too bad because I have 4 months to prepare, this time I don't have any excuse. First I need to know which position I should apply for, I think machine learning engineer(search or NLP) should be more related, it is also okay if the job needs me to still work on map-related projects except assignment field.


# Preparation

#### Coding
[Leetcode](https://docs.google.com/spreadsheets/d/1l7Gvrubuscs0iwDPov053wGWV_uNg0yK_991JDeNIH0/edit#gid=2023823697)

#### Machine learning & Deep learning
- **Underfitting and Overfitting**  
  [link](https://www.cnblogs.com/zhhfan/p/10476761.html)
- **Bias and Variance**  
  [link](https://towardsdatascience.com/understanding-the-bias-variance-tradeoff-165e6942b229)  
- **Generative Model vs Discriminative Model**  
  [link](https://medium.com/@mlengineer/generative-and-discriminative-models-af5637a66a3)  
- **Bagging vs Boost**  
  [link](https://www.zhihu.com/question/26760839)  
- **Feature Selection**  
  [link](https://blog.csdn.net/weixin_38286298/article/details/93972300)
- **Bayesian Model**  
  [link](https://zhuanlan.zhihu.com/p/26262151)  
- **Logistic Regression**  
  [link](https://zhuanlan.zhihu.com/p/139122386)
- **GBDT VS Xgboost VS LightGBM**  
  [link](https://www.cnblogs.com/pinard/p/10979808.html)  
- **Metrics**: (MSE,MAE, Logloss, AUC curve)   
  [link](https://blog.csdn.net/Dby_freedom/article/details/89814644#:~:text=AUC%20%E6%8C%87%E6%A0%87%E7%9A%84%E4%BC%98%E7%82%B9%EF%BC%9A,%E6%96%B9%E9%9D%A2%E8%A1%A1%E9%87%8F%E7%AE%97%E6%B3%95%E7%9A%84%E8%A1%A8%E7%8E%B0%E3%80%82)
  
  [AUC](https://blog.csdn.net/Dby_freedom/article/details/89814644)  
- **L1, L2 regularization**  
  [link](https://www.cnblogs.com/zingp/p/10375691.html#:~:text=L1%E6%AD%A3%E5%88%99%E5%8C%96%E5%92%8CL2%E6%AD%A3%E5%88%99%E5%8C%96%E7%9A%84%E8%AF%B4%E6%98%8E%E5%A6%82%E4%B8%8B,%E4%B9%8B%E5%89%8D%E6%B7%BB%E5%8A%A0%E4%B8%80%E4%B8%AA%E7%B3%BB%E6%95%B0%CE%BB%E3%80%82) 
- **Hidden Markov Model**  
  [link](https://www.cnblogs.com/pinard/p/6945257.html)
- **Conditional Random Field**  
  [link](https://www.cnblogs.com/pinard/p/7048333.html)
- **Activate function**  
  [link](https://towardsdatascience.com/comparison-of-activation-functions-for-deep-neural-networks-706ac4284c8a)
- **Optimization algorithm**  
  [link](https://www.kdnuggets.com/2020/12/optimization-algorithms-neural-networks.html)  
- **Batch Norm VS Layer Norm**  
  [link](https://bbs.huaweicloud.com/blogs/329066)

#### NLP  
- RNN  
  [link](https://www.cnblogs.com/pinard/p/6509630.html)
- Gradient vanish & gradient explode
- **LSTM**  
  [Understanding LSTM Networks](https://colah.github.io/posts/2015-08-Understanding-LSTMs/)  
  [LSTM模型与前向反向传播算法](https://www.cnblogs.com/pinard/p/6519110.html)  
  [Solving the Vanishing Gradient Problem with LSTM](https://www.codingninjas.com/codestudio/library/solving-the-vanishing-gradient-problem-with-lstm)
- Word2vec  
- **Bert**  
  1) [The number of Bert parameters](https://zhuanlan.zhihu.com/p/144582114)  
  2) [Why does self-attention divide root of dk](https://blog.csdn.net/suibianshen2012/article/details/122141294)  
  3) [The comparison of all attentions]
  

- **Bi-lstm + CRF**  
  [CRF Layer on the Top of BiLSTM](https://createmomo.github.io/)  
  [Pytorch Code](https://pytorch.org/tutorials/beginner/nlp/advanced_tutorial.html)

#### Recommendation  
- FM  
- FFM  
- DeepFM  
- DSSM


#### Rank


#### Graph