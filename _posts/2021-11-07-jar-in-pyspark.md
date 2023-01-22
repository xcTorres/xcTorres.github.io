---
layout:     post
title:      "How to run Java function in pySpark"
date:       2021-11-07
author:     "xcTorres"
header-img: "img/in-post/pyspark-custom-package/Apache_Spark_logo.svg.png"
catalog:    true
tags:
    - Spark
    - Java
---    

For data analyst and data scientist, we are more likely to use pySpark to analyze the data instead of scala Spark. But sometimes we may use some third party package written in Java. So this post will teach you how to call java function in pySpark job.  

## Write your Java code    
The class needs to implement the UDF1 interface and override the call function.

```java
import org.apache.spark.sql.api.java.UDF1;

public class HelloWorld implements UDF1<String, String>{

    public String hello(String s){
        long unixTime = System.currentTimeMillis() / 1000L;
        String str = s  +  Long.toString(unixTime);
        return str;
    }

    @Override
    public String call(String s) throws Exception {
        return hello(s);
    }
}
```

In the example above, the type of input in UDF1 is String type. But if the input is an array, the type is not the java array or java ArrayList, it is the scala WrappedArray.    

```java 
import org.apache.spark.sql.api.java.UDF1;
import scala.collection.mutable.WrappedArray;

public class HelloWorld1 implements UDF1<WrappedArray<String>, Double> {

    @Override
    public Double call(WrappedArray<String> stringArray) throws Exception {
        return Double.parseDouble(stringArray.apply(0)) + Double.parseDouble(stringArray.apply(1));
    }
}
```  

## Upload the jar 
When we set the config for Spark, we could set the **spark.jars** and Spark will help to distribute the jar to both drivers and executors.
```python
 SPARK_CONF = SparkConf() \
    .set(...) \
    .set("spark.jars", "file:///ldap_home/chong.xie/hello-world-1.0-SNAPSHOT.jar")
```

## Register UDF
```python
import pyspark.sql.types as T
spark.udf.registerJavaFunction("hello_world", "hello.HelloWorld", T.DoubleType())

```    

## Call UDF in SparkSQL  
```python  
spark.sql("SELECT hello_world1(array('test', 'testa')) as hello_str").show()  

## Or

df.withColumn("hello_str", F.expr("hello_world1(array('test', 'testa'))")).show()
```

