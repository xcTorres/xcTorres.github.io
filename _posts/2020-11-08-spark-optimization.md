---
layout:     post
title:      "Spark optimization"
date:       2020-11-08
author:     "xcTorres"
header-img: "img/in-post/pyspark-custom-package/Apache_Spark_logo.svg.png"
catalog:    true
mathjax: true
tags:
    - Spark
---  

Since I was a postgraduate in college, I have been using Spark cluster for 4 years. Especially when I work, I feel the super power of Spark. It is very easy for us to handle the big data. Right now it is a necessary tool in our daily work. So here I want to summarize some optimization usage that I have used before.  

## Spark Init
#### Jupyter
```python

    import os
    os.environ["SPARK_HOME"] = '/usr/share/spark-2.4'  # add this before "import findspark" if you cannot find pyspark
    os.environ["PYSPARK_PYTHON"] = './python-3.6/pyarrow/bin/python'
    os.environ["PYSPARK_DRIVER_PYTHON"] = '/ldap_home/chong.xie/.conda/envs/foody/bin/python'

    import findspark
    findspark.init()

    from pyspark import SparkContext, SparkConf
    from pyspark.sql import SparkSession

    name = 'demo'
    port = 30011
    SPARK_SERVICE = None
    SPARK_CONF = SparkConf().set('spark.locality.wait', '1000ms') \
        .set('spark.executor.instances', '64') \
        .set('spark.executor.cores', '3') \
        .set('spark.executor.memory', '10g') \
        .set('spark.ui.port', port) \
        .set('spark.yarn.queue', 'ds-regular')\
        .set('spark.sql.session.timeZone', 'GMT+7') \
        .set("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .set("spark.yarn.dist.archives","file:/ldap_home/chong.xie/.conda/envs/pyarrow_env.tgz#python-3.6")


    sc = SparkContext(SPARK_SERVICE, appName=name, conf=SPARK_CONF)
    spark = SparkSession.builder \
        .enableHiveSupport() \
        .getOrCreate()

```
Here are some configuration we need to notice.

- spark.executor.instances
- spark.executor.cores  
- spark.executor.memory  
- spark.sql.session.timeZone

#### Command
We could also use pyspark-submit to run the Spark job.
```python

    spark-submit --conf spark.pyspark.python=/usr/share/miniconda2/envs/py36/bin/python \
                --conf spark.pyspark.driver.python=/ldap_home/chong.xie/.conda/envs/foody/bin/python \
                --py-files ./utils.zip \
                ./feature/merchant_features.py
```

## Read data to dataframe
#### From csv
#### From json
#### From hdfs
#### From parquet
#### From kafka streaming


## Common Spark SQL

#### Filter null value
```python 
    # Method 1
    df = df.where(col("dt_mvmt").isNull())  
    df = df.where(col("dt_mvmt").isNotNull())
    
    # Method 2
    df = df.na.drop(subset=["dt_mvmt"])

    # Method 3
    df = df.filter(col("dt_mvmt").isNotNull())

```

#### Spark UDF


#### 





## Reference 
[https://spark.apache.org/docs/2.3.0/tuning.html](https://spark.apache.org/docs/2.3.0/tuning.html)  
[https://medium.com/@ch.nabarun/apache-spark-optimization-techniques-54864d4fdc0c](https://medium.com/@ch.nabarun/apache-spark-optimization-techniques-54864d4fdc0c)  



spark-submit --conf spark.pyspark.python=/usr/share/miniconda2/envs/py36/bin/python \
             --conf spark.pyspark.driver.python=/ldap_home/chong.xie/.conda/envs/foody/bin/python 
             ./feature/merchant_features.py




