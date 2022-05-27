---
layout:     post
title:      "Attention机制与Transformer模型"
date:       2022-05-27
author:     "xcTorres"
header-img: "img/in-post/machine-learning.jpeg"
catalog:    true
mathjax: true
tags:
    - NLP
    - Machine Learning
---  

如果想要了解Attention机制，最重要的当然是先读[论文](https://arxiv.org/abs/1706.03762)了，不过原始论文非常简练，很难一次读懂, 感谢李沐老师逐段讲解论文，非常清晰，强烈推荐[Transformer论文逐段精读](https://www.bilibili.com/video/BV1pu411o7BE?spm_id_from=333.999.0.0)。
当然最重要的当然是可以跟[代码](https://github.com/xcTorres/machine_learning/tree/master/transformer)学习。以该repo为例，各个子模块相应代码如下。
- Encoder [link](https://github.com/xcTorres/machine_learning/blob/master/transformer/Models.py#L11)
- Decoder [link](https://github.com/xcTorres/machine_learning/blob/master/transformer/Models.py#L26)  
- Attention [link](https://github.com/xcTorres/machine_learning/blob/master/transformer/Sublayers.py#L40)  
- PositionEncoding [link](https://github.com/xcTorres/machine_learning/blob/master/transformer/Embed.py#L14)  
- Mask [link](https://github.com/xcTorres/machine_learning/blob/master/transformer/Batch.py#L15)

<img src="/img/in-post/attention/attention.png" width="500"/>

一般面试过程中，可能会有以下一些问题。  
1. 问: **Q,K,V到底是什么东西？**  
   答：Query、Key的作用是用来在token之间搬运信息的，而Value本身就是从当前token当中提取出来的信息。所以从公式中可以看出，
   $ H = softmax(QK^T/\sqrt{d_k}*V) $  
---  
2. 问：**为什么用Layer Normal？**  
   答：Layer Normal与Batch Normal的区别  
---  
3. 问：**Mask的作用**  
   答：In the encoder and decoder: To zero attention outputs wherever there is just padding in the input sentences. In the decoder: To prevent the decoder ‘peaking’ ahead at the rest of the translated sentence when predicting the next word.



## Reference  
[https://towardsdatascience.com/how-to-code-the-transformer-in-pytorch-24db27c8f9ec](https://towardsdatascience.com/how-to-code-the-transformer-in-pytorch-24db27c8f9ec)




