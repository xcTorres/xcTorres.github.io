---
layout:     post
title:      "How to use custom packages in spark cluster"
date:       2020-09-24
author:     "xcTorres"
header-img: "img/in-post/pyspark-custom-package/Apache_Spark_logo.svg.png"
catalog:    true
mathjax: true
tags:
    - Spark
---  

Sometimes when we use Spark to do the data analysis job, we want to use our own python package. We know the Spark cluster has the driver node  and executor nodes. Usually driver is our own server so we have the permission to install the python package, but we don't have the permission to install the package on hundreds of executor nodes. When we directly run our pySpark code, it will report **"Import Error"**.  

There are two ways to let the executor nodes find out the target python packages.  
 1) Upload  certain custom python package to Spark.    
 2) Upload an entire python environment to Spark and make it as executor python environment. 

## Upload certain python package  

1） Enter into you python env directory, and find the package that you want to upload. For example, the package is **shapely**.  
```bat

    cd ~/.conda/envs/foody/lib/python3.6/site-packages

```

2) Upload the local package file to hdfs system, so that executors are able to download the file from hdfs system.
If you are not familiar with the hadoop fs command, you could refer to this guide.
Your hdfs path should be **/user/your_name/**, for example, my hdfs directory is **/user/chong.xie/**.  you could use following command to check the path exists or not.
```bat
    
    ## create dir in hdfs system
    hadoop fs -ls /user/chong.xie/ 
    hadoop fs -mkdir /user/chong.xie/gecoding_thrid_packages/ 


    ## upload the local package to hdfs system
    hadoop fs -copyFromLocal  ./shapely/  /user/chong.xie/gecoding_thrid_packages/

```

3) Before we run the pySpark code, do remember to add file path to Spark.  
```python
    
    sc.addFile('hdfs:///user/chong.xie/gecoding_thrid_packages/shapely', True)

```

4) import the package just like the code is run on local server.
```python

    import geopandas as gpd

```

## Upload entire python environment  

Now we have a way to upload custom packages, but sometimes the packages that we are going to use have many third-party dependencies, and it is very redundant to upload all of the dependencies.  Under the circumstances, the simplest way is to upload the entire python environment and let the executor servers use our own python env.

1) Create a new python environment and install your required packages. For example, the env name is geocoding.
```bat

    conda create --name geocoding python=3.6
    
    conda activate geocoding
    pip install geopandas
    pip install shapely

```

2) Compress your python into a tgz file
```bat

    cd ~/.conda/envs
    tar -zcf python-3.6.tgz ./geocoding/*

```

3) When we set the spark conf, don't forget to set **spark.yarn.dist.archives**, which will distribute your python compression file to the working directory of every executor servers, and uncompress it to the Newname after #.  Here Newname is python-3.6.
```python

    SPARK_CONF = SparkConf().set(...) \
                            .set("spark.yarn.dist.archives","file:/ldap_home/chong.xie/.conda/envs/python-3.6.tgz#python-3.6")

```
4) And then you need to set the python environment. PYSPARK_DRIVER_PYTHON is your driver python path, it should be only local path.  PYSPARK_PYTHON is the executor python path, so the configuration should be ./Newname/env_name/bin/python.
```python

    import os
    os.environ["PYSPARK_PYTHON"] = './python-3.6/geocoding/bin/python'
    os.environ["PYSPARK_DRIVER_PYTHON"] = '/ldap_home/chong.xie/.conda/envs/geocoding/bin/python'

```

5) Run the pySpark code. If there is no any error, it means it is using your own python environment.

## Reference
[https://hadoop.apache.org/docs/r1.0.4/cn/hdfs_shell.html](https://hadoop.apache.org/docs/r1.0.4/cn/hdfs_shell.html)  
[https://www.jianshu.com/p/d77e16008957](https://www.jianshu.com/p/d77e16008957)

