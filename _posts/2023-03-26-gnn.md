---
layout:     post
title:      "Graph Convolutional Network"
date:       2023-03-26
author:     "xcTorres"
catalog:    true
mathjax: true
tags:
    - algorithms
    - graph
---  

# Main Task
图卷积神经网络主要有以下几个任务  
- Node classification(点分类): GCN can be used to classify nodes in a graph based on their attributes and the local and global structure of the graph.
- Link prediction(边分类): GCN can predict missing or future links in a graph based on the existing links and node attributes.
- Graph classification(图分类): GCN can classify entire graphs based on their structure and attributes.
- Recommendation systems(推荐系统的embedding特征): GCN can be used to build personalized recommendation systems that take into account the relationships between users and items in a graph.



# GCN
我们知道CNN中，主要是通过filter或者kernel这个算子处理图像，提取领域像素的特征。而在图卷积神经网络GCN中，虽然没有格网这样的欧式结构，但是同样可以提取邻居的特征。在GCN中，主要通过得到邻接矩阵，归一化之后再处理到图上，得到最终结果。  

$  
H^{(l+1)} = f(D^{-1/2} A D^{-1/2} H^{(l)} W^{(l)})  
$

- 这里 $H^{(l)}$ 是l层的node特征向量, 维度为N x F_l, 这里N是node个数，F_l是node的特征个数。  
- A为邻接矩阵，维度为N x N。
- D在这里为对角度矩阵，主要用于邻接矩阵的归一化。
- $W^{(l)}$为l层神经网络的权重参数  
- f为激活函数。
- $H^{(l+1)}$为l+1层的node特征。  

即使GCN在图上有不错的表现，但其也有一些缺点。其中一个缺点是当图的规模较大时，**计算归一化邻接矩阵需要付出很多成本**。且其是transductive(直推)，也就是其只能在训练集中出现过的node上做预测，无法泛化到之前未出现过的点。

# GraphSAGE
由于这些局限性，也就有了GraphSAGE的诞生。不像GCN通过邻接矩阵获取所有邻居信息去聚合，GraphSAGE是采用采样的方式，采样固定个数的邻居再进行聚合。

$h_{\mathcal{N}(v)}^k = \sigma(\mathbf{W}^k \cdot \text{CONCAT}(h_u^{k-1}, \forall u \in \mathcal{N}(v)))$  

- 这里$h_u^{k-1}$是在node $u$在$(k-1)$-th层的向量, $\mathbf{W}^k$是权重矩阵。

- $\mathcal{N}(v)$ 是node $v$采样的邻居。
- $\sigma$ 是非线性激活函数。 

这样采样处理的好处是更加灵活，也支持inductive，能够对训练集之外未出现过的点进行预测。具体步骤是找到新node在原先训练集中的邻居。并用原先GraphSage的采样方式以及网络进行预测即可。  
这里对于之前训练图中的node，不作任何处理，仍然使用原先的embedding。  

---

# Graph Attention Network  
相比于GraphSAG用采样聚合的方法表示node的embedding，GAT是用注意力机制去学习不同邻居节点的重要性。
$$ a_ji = LeakyReLU ( (a^T [Wx_j || Wx_i]) ) $$
$$ alpha_ji = softmax(a_ji) $$
$$ h_j' = sum( alpha_ji * h_i ) $$  

---

# Heterogeneous Graph
Relational Graph Convolutional Networks (R-GCN)  
Heterogeneous Graph Attention Network (HAN)  
Metapath2Vec  
Heterogeneous Graph Transformer (HGT)  

---
# Code Example  
主要比较好用的开源库有[stellargraph](https://github.com/stellargraph/stellargraph)以及dmlc的[dgl](https://github.com/dmlc/dgl)库，这里先以stellargraph为例。  

```python
import stellargraph as sg
from stellargraph.mapper import GraphSAGENodeGenerator
from stellargraph.layer import GraphSAGE

# Load the Cora citation network dataset
dataset = sg.datasets.Cora()
graph = dataset.load()

# Define the feature and target columns
feature_names = dataset.feature_names
target_name = dataset.target_name

# Split the data into training and testing sets
train_nodes, test_nodes = sg.utils.train_test_split(graph.nodes(), test_size=0.2, stratify=graph.node[target_name])
train_targets = graph.node.loc[train_nodes, target_name]
test_targets = graph.node.loc[test_nodes, target_name]

# Define the GraphSAGE model architecture
generator = GraphSAGENodeGenerator(graph, batch_size=32, num_samples=[4, 4])
train_flow = generator.flow(train_nodes, train_targets, shuffle=True)
test_flow = generator.flow(test_nodes, test_targets)
sage = GraphSAGE(layer_sizes=[32, 32], activations=["relu", "relu"], generator=generator, dropout=0.5)
x_inp, x_out = sage.in_out_tensors()

# Compile the model and train it on the training data
model = tf.keras.Model(inputs=x_inp, outputs=x_out)
model.compile(optimizer=tf.optimizers.Adam(lr=0.01), loss="categorical_crossentropy", metrics=["acc"])
model.fit(train_flow, epochs=100)

# Evaluate the model on the testing data
test_metrics = model.evaluate(test_flow)
print("Test loss: {:.4f}".format(test_metrics[0]))
print("Test accuracy: {:.4f}".format(test_metrics[1]))

```
可以看到num_samples=[4,4]这里指2层隐藏层网络均只采样周围四个邻居节点，  
layer_sizes=[32,32]这里指2层隐藏层大小均为32。 


# Reference  
[https://distill.pub/2021/gnn-intro/](https://distill.pub/2021/gnn-intro/)  
[https://towardsdatascience.com/understanding-graph-convolutional-networks-for-node-classification-a2bfdb7aba7b](https://towardsdatascience.com/understanding-graph-convolutional-networks-for-node-classification-a2bfdb7aba7b)