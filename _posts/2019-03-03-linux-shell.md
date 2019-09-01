---
layout:     post
title:      "linux 命令"
date:       2019-03-03
author:     "xcTorres"
header-img: "img/in-post/java.jpg"
catalog:    true
tags:
    - Linux
---
https://www.cnblogs.com/MacoLee/p/5664306.html


#### Process  
1） 查看进程及端口号并删除进程号  
```python

    lsof -i tcp:port 
    kill -9 PID

```
2）查找指定进程
```python

    ps -ef  |grep xxx

```

2) 根据PID查看进程内存消耗情况
```python 

    top -pid xxx

```

#### Disk  
1）查看磁盘分布
df -h

2）查看磁盘容量  
du 命令

#### 文本命令
1）grep 命令:  
2）awk 命令: [http://www.runoob.com/linux/linux-comm-awk.html](http://www.runoob.com/linux/linux-comm-awk.html)  
3）sed 命令: [https://man.linuxde.net/sed](https://man.linuxde.net/sed)
```python 

    - sed -i '' -e 's/^\(appendonly \).*/\1yes/' ~/Desktop/redis.conf  
    appendonly no => appendonly yes  
    # 注释 save 开头的配置 
    - sed -i '' -e 's/^[[:blank:]]*save/#&/' ~/Desktop/redis.conf 
    # 取消 save开头的配置
    - sed -i '' -e 's/^#\([[:blank:]]*save\)/\1/' ~/Desktop/redis.conf  

```



