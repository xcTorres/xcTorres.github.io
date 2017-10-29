---
layout:     post
title:      "kaggle House Price"
subtitle:   "kaggle入门(1)"
date:       2017-10-25 
author:     "xcTorres"
header-img: "img/post-bg-ios9-web.jpg"
tags:
    - 机器学习
---

最近学习机器学习和数据挖掘，并注册了kaggle，由于才开始学习，其中有个新手入门的房价预测的比赛，便翻译了其中第一名的kenel，用python实现的代码，原文档是Notebook。我重新整理一遍用于学习整个数据挖掘的过程。

1.在我们每次写一个kenel时，我们首先需要了解问题是什么，分析每个变量的意义以及对该问题的重要性程度。

2.单变量研究，比如我们会关注非独立变量房价'SalePrice'，并且尽可能的了解该变量。

3.多元变量分析。尝试去了解这些独立变量与非独立变量的相关性。

4.基本清理数据。学会清理数据，处理缺失数据，离群值。

5.进行测试，来判断我们的模型是否有效。

首先是引入各个必要的库。
其中pandas是用来方便操作数据的库
其中matplotlib和seaborn是用来进行可视化

```
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')
%matplotlib inline
```

首先读入数据
```
df_train = pd.read_csv('../input/train.csv')
```

#检查数据所有存在的列

```
df_train.columns
```
结果：
```
Index(['Id', 'MSSubClass', 'MSZoning', 'LotFrontage', 'LotArea', 'Street',
       'Alley', 'LotShape', 'LandContour', 'Utilities', 'LotConfig',
       'LandSlope', 'Neighborhood', 'Condition1', 'Condition2', 'BldgType',
       'HouseStyle', 'OverallQual', 'OverallCond', 'YearBuilt', 'YearRemodAdd',
       'RoofStyle', 'RoofMatl', 'Exterior1st', 'Exterior2nd', 'MasVnrType',
       'MasVnrArea', 'ExterQual', 'ExterCond', 'Foundation', 'BsmtQual',
       'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinSF1',
       'BsmtFinType2', 'BsmtFinSF2', 'BsmtUnfSF', 'TotalBsmtSF', 'Heating',
       'HeatingQC', 'CentralAir', 'Electrical', '1stFlrSF', '2ndFlrSF',
       'LowQualFinSF', 'GrLivArea', 'BsmtFullBath', 'BsmtHalfBath', 'FullBath',
       'HalfBath', 'BedroomAbvGr', 'KitchenAbvGr', 'KitchenQual',
       'TotRmsAbvGrd', 'Functional', 'Fireplaces', 'FireplaceQu', 'GarageType',
       'GarageYrBlt', 'GarageFinish', 'GarageCars', 'GarageArea', 'GarageQual',
       'GarageCond', 'PavedDrive', 'WoodDeckSF', 'OpenPorchSF',
       'EnclosedPorch', '3SsnPorch', 'ScreenPorch', 'PoolArea', 'PoolQC',
       'Fence', 'MiscFeature', 'MiscVal', 'MoSold', 'YrSold', 'SaleType',
       'SaleCondition', 'SalePrice'],
      dtype='object')
```

房屋售价是我们要研究的问题，我们可以首先看看其分布
```
df_train['SalePrice'].describe()
```
结果如下

```
count      1460.000000
mean     180921.195890
std       79442.502883
min       34900.000000
25%      129975.000000
50%      163000.000000
75%      214000.000000
max      755000.000000
Name: SalePrice, dtype: float64
```

接下来便可用seaborn库直接查看其直方图分布

```
#histogram
sns.distplot(df_train['SalePrice']);
```

分布结果如图
![](https://www.kaggle.io/svf/1630295/90ae958666db7d760b0c0e3185ab0323/__results___files/__results___9_0.png)

在分析各个独立变量，给人的直觉，“GrLivArea”(客厅的面积)，“totalbsmtsf”(地下室面积)，"overallqual"(房屋整体评价),以及房子年代("YearBuilt")有关系。

接下来就来看看他们与SalesPrice之间的关系：

数值变量（客厅面积，地下室面积）
---

```
#scatter plot grlivarea/saleprice
var = 'GrLivArea'
data = pd.concat([df_train['SalePrice'], df_train[var]], axis=1)
data.plot.scatter(x=var, y='SalePrice', ylim=(0,800000));
```
得到结果：
![](https://www.kaggle.io/svf/1630295/90ae958666db7d760b0c0e3185ab0323/__results___files/__results___16_0.png)

从上图不难发现，客厅面积与房屋价格似乎呈线性相关。


```
#scatter plot totalbsmtsf/saleprice
var = 'TotalBsmtSF'
data = pd.concat([df_train['SalePrice'], df_train[var]], axis=1)
data.plot.scatter(x=var, y='SalePrice', ylim=(0,800000));
```
![](https://www.kaggle.io/svf/1630295/90ae958666db7d760b0c0e3185ab0323/__results___files/__results___18_0.png)
从上图不难发现，在一定范围内，地下室面积与房屋价格似乎呈更强烈的线性相关。

---
种类变量（房屋整体评价，房屋年代）

```
#box plot overallqual/saleprice
var = 'OverallQual'
data = pd.concat([df_train['SalePrice'], df_train[var]], axis=1)
f, ax = plt.subplots(figsize=(8, 6))
fig = sns.boxplot(x=var, y="SalePrice", data=data)
fig.axis(ymin=0, ymax=800000);
```

![](https://www.kaggle.io/svf/1630295/90ae958666db7d760b0c0e3185ab0323/__results___files/__results___21_0.png)

显而易见，评分越高，房屋价格也越高。




```
var = 'YearBuilt'
data = pd.concat([df_train['SalePrice'], df_train[var]], axis=1)
f, ax = plt.subplots(figsize=(16, 8))
fig = sns.boxplot(x=var, y="SalePrice", data=data)
fig.axis(ymin=0, ymax=800000);
plt.xticks(rotation=90);

```
![](https://www.kaggle.io/svf/1630295/90ae958666db7d760b0c0e3185ab0323/__results___files/__results___23_0.png)

可以看出，虽然房价与年代没有某种特定的趋势，但是年代近的房屋，价格还是要高一些。

而上面的四个变量只是我们主管认为比较重要的变量。那么其他变量有多重要呢。我们需要看看协方差矩阵。

```
#correlation matrix
corrmat = df_train.corr()
f, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(corrmat, vmax=.8, square=True);
```

![](https://www.kaggle.io/svf/1630295/90ae958666db7d760b0c0e3185ab0323/__results___files/__results___30_0.png)

通过这个图，我们便可以很容易的看出其他变量与房价之间的关系。映入眼帘的，我们可以看出来、有两个白色的小方块。则表明， 'TotalBsmtSF' and '1stFlrSF' 相关性极强，GarageX属性相关性极强，甚至是共线关系。我们则可认为他们对于房价的影响贡献是一样的，

'GrLivArea', 'TotalBsmtSF', and 'OverallQual' 这三个变量跟房价有着比较重要的关系。现在可以发现还有一些其他变量跟房价有着比较重要的关系。接下来我们就再来看看。


```
#saleprice correlation matrix
k = 10 #number of variables for heatmap
cols = corrmat.nlargest(k, 'SalePrice')['SalePrice'].index
cm = np.corrcoef(df_train[cols].values.T)
sns.set(font_scale=1.25)
hm = sns.heatmap(cm, cbar=True, annot=True, square=True, fmt='.2f', annot_kws={'size': 10}, yticklabels=cols.values, xticklabels=cols.values)
plt.show()

```
![](https://www.kaggle.io/svf/1630295/90ae958666db7d760b0c0e3185ab0323/__results___files/__results___33_0.png)

如图我们不难发现，以下变量与房价比较相关

'OverallQual'（整体评价）, 'GrLivArea' （客厅面积）and 'TotalBsmtSF'（地下室面积）的确与房价强烈相关

'GarageCars'（车库车位） and 'GarageArea'（车库面积） 这两个等同于同一个概念，由于GarageCars与房价更相关，我们就取GarageCars变量就可以了

'TotalBsmtSF' and '1stFloor' 也像双胞胎兄弟，在这里我们就取TotalBsmtSF

'FullBath'配备洗浴设备，也是需要的。

'TotRmsAbvGrd' and 'GrLivArea', 也是一样。


处理缺省数据
---
当处理缺失数据的时候我们得想到，如下的问题。

1.缺失数据很普遍么？
2.缺省数据是随机的还是有一定特征

在实践过程中这些问题非常关键。因为有可能数据缺失会导致样本数据量减少从而影响我们分析。我们得确定缺失数据是无偏差的。


```
#missing data
total = df_train.isnull().sum().sort_values(ascending=False)
percent = (df_train.isnull().sum()/df_train.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
missing_data.head(20)
```
![](/img/post-house_price-missing.png)

对于缺失数据我们主要有如下几种方法
1.当某一种数据缺失率超过15%，我们应该删掉相关变量。在该例中 应该删除( 'PoolQC', 'MiscFeature', 'Alley', etc.)


删除缺失数据变量
```
#dealing with missing data
df_train = df_train.drop((missing_data[missing_data['Total'] > 1]).index,1)
df_train = df_train.drop(df_train.loc[df_train['Electrical'].isnull()].index)
df_train.isnull().sum().max() #just checking that there's no missing data missing...
```
离群点

离群点同样应该是我们需要注意的，因为其可能显著的影响模型，并含有有用的信息供我们思考


