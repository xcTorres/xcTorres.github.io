---
layout:     post
title:      "CentOS7 命令大全"
date:       2019-03-03
author:     "xcTorres"
header-img: "img/in-post/java.jpg"
catalog:    true
tags:
    - Linux
---
https://www.cnblogs.com/MacoLee/p/5664306.html

1） 查看进程及端口号并删除进程号
lsof -i tcp:*port*  
kill -9 PID

2）查看磁盘分布
df -h

3）查看磁盘容量
du 命令

4) 根据PID查看进程内存消耗情况
top -pid xxx


