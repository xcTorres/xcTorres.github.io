---
layout:     post
title:      "Spark Cheat Sheet"
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
        .set('spark.yarn.queue', 'ds-regular')

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
```bash

    spark-submit --conf spark.pyspark.python=/usr/share/miniconda2/envs/py36/bin/python \
                 --conf spark.pyspark.driver.python=/ldap_home/chong.xie/.conda/envs/foody/bin/python \
                 ./feature/merchant_features.py  

```

## Read & Write
#### From json

```python
    
    df = spark.read.json("path")

```

#### **From csv**
#### **From hdfs** 

#### **From parquet**

```python

    # Read
    df = spark.read.parquet('path')

    # Write
    df.write.parquet(path, mode='overwrite') # Overwrite
    df.write.parquet(path, mode='append') # Append

```

#### **From kafka streaming**  
- **Stream** 

```python

    topic = 'topic'
    df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "10.70.15.78:9092") \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", False) \
            .load() \
            .selectExpr("CAST(value AS STRING)")

    query = df.writeStream\
              .format('console')\
              .start()

```  
- **Batch query**   

```python

    topic = 'topic'
    df = spark.read \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "10.70.15.78:9092") \
            .option("subscribe", topic) \
            .option("startingOffsets", "earlist") \
            .option("endingOffsets", "earliest") \
            .option("failOnDataLoss", False) \
            .load() \
            .selectExpr("CAST(value AS STRING)")

```

## Spark DataFrame

#### Filter value
```python 
    # Filter null value
    df = df.where(col("dt_mvmt").isNull())  
    df = df.na.drop(subset=["dt_mvmt"])
    df = df.filter(col("dt_mvmt").isNull())

    # Condition
    df = df.filter(col("col") > 2)
    df = df.filter('col > 2')

```

#### Get Statistic data
```python

    df.select('origin_speed').summary().show()

    # +-------+------------------+
    # |summary|      origin_speed|
    # +-------+------------------+
    # |  count|           7066188|
    # |   mean|4.3542590483886805|
    # | stddev| 4.069686621970696|
    # |    min|              -2.0|
    # |    25%|        0.55032253|
    # |    50%|         3.6093123|
    # |    75%|          7.272925|
    # |    max|             210.0|
    # +-------+------------------+

    # Quantile
    df.approxQuantile("origin_speed", [0.80, 0.90, 0.95, 0.99, 0.995, 0.999], 0)
    # [8.28824234008789, 10.089457511901855, 11.575858116149902, 14.782051086425781, 16.42580223083496]

    #min, max
    df.select(F.min(F.col('create_time'))).show()
    df.select(F.max(F.col('create_time'))).show()

```

#### mapPartition  
```



```


#### GroupBy

## Spark SQL

#### select & from
```python

    sql =  '''
                select * 
                from {} 
                where create_time >= unix_timestamp('{}')
                and create_time < unix_timestamp('{}')
           '''.format(table, time_from, time_to)
    df = spark.sql(sql)

```

#### unix_timestamp
Convert time string with given pattern (**‘yyyy-MM-dd HH:mm:ss’**, by default) to Unix time stamp (in seconds), using the default timezone and the default locale, return null if fail.

```python

    import pyspark.sql.functions as F 
    df.select(F.unix_timestamp('dt', 'yyyy-MM-dd').alias('unix_time'))

```

## Optimization





## Reference 
[https://spark.apache.org/docs/2.3.0/tuning.html](https://spark.apache.org/docs/2.3.0/tuning.html)  
[https://medium.com/@ch.nabarun/apache-spark-optimization-techniques-54864d4fdc0c](https://medium.com/@ch.nabarun/apache-spark-optimization-techniques-54864d4fdc0c)  
[https://stackoverflow.com/questions/47669895/how-to-add-multiple-columns-using-udf/51908455](https://stackoverflow.com/questions/47669895/how-to-add-multiple-columns-using-udf/51908455)
[https://spark.apache.org/docs/2.2.0/structured-streaming-kafka-integration.html](https://spark.apache.org/docs/2.2.0/structured-streaming-kafka-integration.html)




