DeepFM  

由于DeepFM算法有效地结合了因子分解机与神经网络在特征学习中的优点：同时提取到低阶组合特征与高阶组合特征，所以越来越被广泛使用。在DeepFM中，FM算法负责对一阶特征以及由一阶特征两两组合而成的二阶特征进行特征的提取；DNN算法负责对由输入的一阶特征进行全连接等操作形成的高阶特征进行特征的提取。DeepFM具有以下特点：

1. 结合了广度和深度模型的优点，联合训练FM模型和DNN模型，同时学习低阶特征组合和高阶特征组合。

2. 端到端模型，无需特征工程。

3. DeepFM 共享相同的输入和 embedding vector，训练更高效。

DeepFM模型的预测结果输出为：  


https://www.cnblogs.com/pinard/p/6349233.html  

协同过滤


class LRUCache(object):

    def __init__(self, capacity):
        """
        :type capacity: int
        """

        

    def get(self, key):
        """
        :type key: int
        :rtype: int
        """

            
        

    def put(self, key, value):
        """
        :type key: int
        :type value: int
        :rtype: None
        """
