---
layout:     post
title:      "HBase性能调优"
date:       2019-03-03
author:     "xcTorres"
header-img: "img/in-post/java.jpg"
catalog:    true
tags:
    - Linux
---

## 问题一 JVM抛出 java.lang.OutOfMemoryError: GC overhead limit exceeded   
在做HBase相关实验时，由于从数据库中直接获取的数据量过多，报出问题一错误。

