---
layout:     post
title:      "Spark Cheat Sheet"
date:       2020-12-11
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

#### Command
We could also use pyspark-submit to run the Spark job.
```bash
spark-submit --conf spark.pyspark.python=/usr/share/miniconda2/envs/py36/bin/python \
             --conf spark.pyspark.driver.python=/ldap_home/chong.xie/.conda/envs/foody/bin/python \
             ./feature/merchant_features.py  
```

#### Configuration
Here are some configurations we need to notice.

- **spark.executor.instances**  
configuration property controls the number of executors requested

- **spark.executor.cores**   
configuration property controls the number of concurrent tasks an executor can run

- **spark.executor.memory**  
configuration property controls the heap size

- **spark.sql.session.timeZone**  
The session time zone is set with the configuration ‘spark.sql.session.timeZone’ and will default to the JVM system local time zone if not set.


## Read & Write
#### From json

```python
    
    # A JSON dataset is pointed to by path.
    # The path can be either a single text file or a directory storing text files
    path = "examples/src/main/resources/people.json"
    peopleDF = spark.read.json(path)

    # The inferred schema can be visualized using the printSchema() method
    peopleDF.printSchema()
    # root
    #  |-- age: long (nullable = true)
    #  |-- name: string (nullable = true)

```

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
    servers="ip:port"
    df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", servers) \
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
    servers="ip:port"
    df = spark.read \
            .format("kafka") \
            .option("kafka.bootstrap.servers", servers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "earlist") \
            .option("endingOffsets", "earliest") \
            .option("failOnDataLoss", False) \
            .load() \
            .selectExpr("CAST(value AS STRING)")
```

## Spark DataFrame

#### Select & from
```python

    sql =  '''
                select * 
                from {} 
                where create_time >= unix_timestamp('{}')
                and create_time < unix_timestamp('{}')
           '''.format(table, time_from, time_to)
    df = spark.sql(sql)
```

#### udf
```python
    @F.udf(returnType=T.BooleanType())
    def filter_no_delivered_traj(segment):
        no_delivered_flag = True
        for pt in segment:
            if not pt.order_info:
                no_delivered_flag = False
                break
        return no_delivered_flag

    filter_df = df.withColumn('is_delivery', filter_no_delivered_traj('segment'))
```

#### unix_timestamp
Convert time string with given pattern (**‘yyyy-MM-dd HH:mm:ss’**, by default) to Unix time stamp (in seconds), using the default timezone and the default locale, return null if fail.

```python
    import pyspark.sql.functions as F 
    df.select(F.unix_timestamp('dt', 'yyyy-MM-dd').alias('unix_time'))
```

#### from_unixtime
Converts the number of seconds from unix epoch (1970-01-01 00:00:00 UTC) to a string representing the timestamp of that moment in the current system time zone in the given format.
```python
    import pyspark.sql.functions as F
    import pyspark.sql.types as T
    df = df.withColumn('date_time', F.from_unixtime(F.col('timestamp')))
```


#### filter value
```python 
    # Filter null value
    df = df.where(col("dt_mvmt").isNull())  
    df = df.na.drop(subset=["dt_mvmt"])
    df = df.filter(col("dt_mvmt").isNull())

    # Condition
    df = df.filter(col("col") > 2)
    df = df.filter('col > 2')

    #  Multi conditions
    df = df.filter('(col>2) and (col<34)')
```

#### summary
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

    # min, max, avg
    df.select(F.min('create_time')).show()
    df.select(F.max('create_time'))).show()
    df.select(F.avg('create_time')).show()
```

#### quantile  
``` python
    # Quantile
    df.approxQuantile("origin_speed", [0.80, 0.90, 0.95, 0.99, 0.995, 0.999], 0)
    # [8.28824234008789, 10.089457511901855, 11.575858116149902, 14.782051086425781, 16.42580223083496]

    # Spark SQL
    sql = '''
            select 
                experiment_group,
                count(*),
                percentile_approx(CreatedOnToConfirm, 0.25) as CreatedOnToConfirmQuantile25,
                percentile_approx(CreatedOnToConfirm, 0.5) as CreatedOnToConfirmQuantile50,
                percentile_approx(CreatedOnToConfirm, 0.75) as CreatedOnToConfirmQuantile75,
                
            from order_complete_info
            group by experiment_group
    
          '''
    a = spark.sql(sql)

    sql = '''
            select percentile_approx(create_time, array(0.25,0.5,0.75)) as create_quantile
            from tmp
          '''
    a = spark.sql(sql)
```


#### nan value count
```python
    from pyspark.sql.functions import isnan, when, count, col
    df.select([count(when(isnan(c), c)).alias(c) for c in ['create_time']]).show()
```
#### repartition

Sometimes you need the records in one partition in some constraints. For example, all records of some certain user_id must be in one single partion so that you are allowed to use groupBy function in mapPartition function.

```
    stages_time_df = raw_order_status_log_df\
    .repartition('order_id') \
    .rdd \
    .mapPartitions(calculate_stages_time).toDF(sampleRatio=0.1)
```

#### mapPartition  
It will run the function in each partition, so you are allowed to set global variable for each partition. For example, if you want to send http requests and it is more efficient to maintain the http connection pool for each partition. 

```
    SCHEMA_RESPONSE = sdf.schema.add(
        T.StructField("mm_response", T.StringType(), True)
    )

    # Here map_matching maintain a connection pool for all of the records within partitions.
    mm_df = sdf.rdd.mapPartitions(map_matching).toDF(schema=SCHEMA_RESPONSE)
```


#### groupBy
Groups the DataFrame using the specified columns, so we can run aggregation on them. See GroupedData for all the available aggregate functions.

```python
    values = [(1, 2.0), (1, 4.0), (2, 0.0), (2, 100.0), (3, 5.0)]
    columns = ['id', 'count']
    df = spark.createDataFrame(values, columns)
    df.show()

    +---+-----+
    | id|count|
    +---+-----+
    |  1|  2.0|
    |  1|  4.0|
    |  2|  0.0|
    |  2|100.0|
    |  3|  5.0|
    +---+-----+

    df.groupBy('id').agg(F.mean('count').alias('count_mean')).show()
    +---+----------+
    | id|count_mean|
    +---+----------+
    |  1|       3.0|
    |  3|       5.0|
    |  2|      50.0|
    +---+----------+

    # groupBy and collect all of the records into one array
    df.groupBy('id').agg(F.collect_list('count').alias('count_list')).show()
    +---+------------+
    | id|  count_list|
    +---+------------+
    |  1|  [4.0, 2.0]|
    |  3|       [5.0]|
    |  2|[0.0, 100.0]| 
```

#### explode
If the type of one column is an array and you want to explode all of elementa of array into multi Rows, explode fucntion could meet this demand.

```python

    values = [(1, [2,3,4])]
    columns = ['id', 'array']
    df = spark.createDataFrame(values, columns)
    df.show()

    +---+---------+
    | id|    array|
    +---+---------+
    |  1|[2, 3, 4]|
    +---+---------+

    df.select('id', F.explode('array').alias('element')).show()
    +---+-------+
    | id|element|
    +---+-------+
    |  1|      2|
    |  1|      3|
    |  1|      4|
    +---+-------+
```



## Optimization





## Reference 
[https://spark.apache.org/docs/2.3.0/tuning.html](https://spark.apache.org/docs/2.3.0/tuning.html)  
[https://medium.com/@ch.nabarun/apache-spark-optimization-techniques-54864d4fdc0c](https://medium.com/@ch.nabarun/apache-spark-optimization-techniques-54864d4fdc0c)  
[https://stackoverflow.com/questions/47669895/how-to-add-multiple-columns-using-udf/51908455](https://stackoverflow.com/questions/47669895/how-to-add-multiple-columns-using-udf/51908455)
[https://spark.apache.org/docs/2.2.0/structured-streaming-kafka-integration.html](https://spark.apache.org/docs/2.2.0/structured-streaming-kafka-integration.html)