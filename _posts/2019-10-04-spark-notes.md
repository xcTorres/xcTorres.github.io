---
layout:     post
title:      "Spark Notes"
date:       2019-10-04
author:     "xcTorres"
header-img: "img/in-post/offer.jpg"
catalog:    true
tags:
    - Python
    - Spark
---  
[Spark SQL, DataFrames and Datasets Guide](https://spark.apache.org/docs/2.2.0/sql-programming-guide.html#overview)  

## Spark init
```python
    from pyspark import SparkContext, SparkConf
    from pyspark.sql import SparkSession

    name = 'fdy_delivery_study'
    port = 30011
    SPARK_SERVICE = None
    
    SPARK_CONF = SparkConf().set('spark.locality.wait', '1000ms') \
        .set('spark.executor.instances', '64') \
        .set('spark.executor.cores', '2') \
        .set('spark.executor.memory', '10g') \
        .set('spark.ui.port', port) \
        .set('spark.yarn.queue', 'ds-regular')\
        .set('spark.sql.session.timeZone', 'GMT+7')

    sc = SparkContext(SPARK_SERVICE, appName=name, conf=SPARK_CONF)
    spark = SparkSession.builder \
        .enableHiveSupport() \
        .getOrCreate()
```
