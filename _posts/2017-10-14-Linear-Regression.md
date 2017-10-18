---
layout:     post
title:      "Linear Regression"
subtitle:   "线性回归"
date:       2017-10-14 
author:     "xcTorres"
header-img: "img/post-bg-unix-linux.jpg"
tags:
    - 机器学习
---


在现实生活中普遍存在着变量之间的关系，有确定的和非确定的。确定关系指的是变量之间可以使用函数关系式表示，还有一种是属于非确定的（相关），比如人的身高和体重，一样的身高体重是不一样的。

**线性回归**

首先介绍其函数模型：

<img src="http://latex.codecogs.com/gif.latex?h_w(x^i) = w_0+w_1x_1+ w_2x_2+\cdots+w_nx_n"/>


<img src="http://latex.codecogs.com/gif.latex?X =\left[
       \begin{matrix}    
        1 \\
       x_1 \\
       \vdots \\
       x_n
      \end{matrix} 
      \right]  ,
	  W =\left[
       \begin{matrix}    
       w_0 \\
       w_1 \\
       \vdots \\
       w_n
      \end{matrix} 
      \right]"/> 
<img src="http://latex.codecogs.com/gif.latex?XW = h_w(x^i)"/> 
<br> 假设有训练数据集
<img src="http://latex.codecogs.com/gif.latex?D=\{(X_1,Y_1),(X_2,Y_2),\cdots,(X_n,Y_n)\}"/> 

<br>则可以得到其矩阵形式
<img src="http://latex.codecogs.com/gif.latex?   X =\left[
       \begin{matrix}    
        1 & x_1^1 & x_2^1 & \cdots & x_n^1\\
        1 & x_1^2 & x_2^2 & \cdots & x_n^2\\
        \\
        &&\cdots\cdots \\
        1 & x_1^n & x_2^n & \cdots & x_n^n\\
      \end{matrix} 
      \right]  ,
   XW = h_w(x^i)"/> 



**损失函数（cost）：**
现在我们需要根据给定的X求解W的值，这里采用最小二乘法。   

**最小二乘法**
何为最小二乘法，其实很简单。我们有很多的给定点，这时候我们需要找出一条线去拟合它，那么我先假设这个线的方程，然后把数据点代入假设的方程得到观测值，求使得实际值与观测值相减的平方和最小的参数。对变量求偏导联立便可求。



因此损失代价函数为：

<img src="http://latex.codecogs.com/gif.latex?J(W) = \frac{1}{2M}\sum_{i=1}^M(h_w(x^i)-y_i)^2  
= \frac{1}{2M}(XW-Y)^T(XW-Y)"/> 

现在我们的目的就是求解出一个使得代价函数最小的W：

<img src="http://latex.codecogs.com/gif.latex?L(W) = \frac{1}{2}(XW-y)^T(XW-y)   
= \frac{1}{2}[W^TX^TXW-W^TX^Ty-yTXW+yTy]   
= \frac{1}{2}[W^TX^TXW-2W^TX^Ty+yTy] "/> 

***     
**a.矩阵满秩可求解时（求导等于0）**

<img src="http://latex.codecogs.com/gif.latex?\frac{\partial L(W)}{\partial W} = 0    
 \frac{\partial L(W)}{\partial W} = \frac{1}{2}[2X^TXW-2X^Ty] = 0"/>  
 
<img src="http://latex.codecogs.com/gif.latex?X^TXW-X^Ty  = 0"/> 

<img src="http://latex.codecogs.com/gif.latex? X^TXW = X^Ty"/>   

<img src="http://latex.codecogs.com/gif.latex? W = (X^TX)^{-1}X^Ty"/>   

***


**b.矩阵不满秩时（梯度下降）：**


梯度下降算法是一种求局部最优解的方法，对于F(x)，在a点的梯度是F(x)增长最快的方向，那么它的相反方向则是该点下降最快的方向，具体参考wikipedia。

原理：将函数比作一座山，我们站在某个山坡上，往四周看，从哪个方向向下走一小步，能够下降的最快；

注意：当变量之间大小相差很大时，应该先将他们做处理，使得他们的值在同一个范围，这样比较准确。

1）首先对θ赋值，这个值可以是随机的，也可以让θ是一个全零的向量。

2）改变θ的值，使得J(θ)按梯度下降的方向进行减少。

***


具体原理介绍可以参考如下链接，里面有详细的介绍。
[http://www.cnblogs.com/pinard/p/5970503.html](http://www.cnblogs.com/pinard/p/5970503.html)

而如下链接为简易梯度下降的python代码实现
[https://github.com/mattnedrich/GradientDescentExample](https://github.com/mattnedrich/GradientDescentExample)

***
接下来介绍线性回归的实例，所用库为scikit-learn，如下为官方线性回归代码
```
print(__doc__)


# Code source: Jaques Grobler
# License: BSD 3 clause


import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

# Load the diabetes dataset(该库自带的糖尿病数据)
diabetes = datasets.load_diabetes()


# Use only one feature
diabetes_X = diabetes.data[:, np.newaxis, 2]

# Split the data into training/testing sets
diabetes_X_train = diabetes_X[:-20]
diabetes_X_test = diabetes_X[-20:]

# Split the targets into training/testing sets
diabetes_y_train = diabetes.target[:-20]
diabetes_y_test = diabetes.target[-20:]

# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(diabetes_X_train, diabetes_y_train)

# Make predictions using the testing set
diabetes_y_pred = regr.predict(diabetes_X_test)

# The coefficients
print('Coefficients: \n', regr.coef_)
# The mean squared error
print("Mean squared error: %.2f"

      % mean_squared_error(diabetes_y_test, diabetes_y_pred))
# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % r2_score(diabetes_y_test, diabetes_y_pred))

# Plot outputs
plt.scatter(diabetes_X_test, diabetes_y_test,  color='black')
plt.plot(diabetes_X_test, diabetes_y_pred, color='blue', linewidth=3)

plt.xticks(())
plt.yticks(())

plt.show()
```
***

最终得到结果如图
![](/img/in-post/post-scikit-lr.png)

