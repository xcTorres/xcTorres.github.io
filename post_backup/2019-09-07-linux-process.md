---
layout:     post
title:      "Linux Process"
date:       2019-09-07
author:     "xcTorres"
header-img: "img/in-post/java.jpg"
catalog:    true
tags:
    - Linux
---

## 查看物理CPU  
**总核数 = 物理CPU个数 X 每颗物理CPU的核数**  
**总逻辑CPU数 = 物理CPU个数 X 每颗物理CPU的核数 X 超线程数**
**查看物理CPU个数**  
```bash

    cat /proc/cpuinfo| grep "physical id"| sort| uniq| wc -l  

```
**查看每个物理CPU中core的个数(即核数)**  
```bash

    cat /proc/cpuinfo| grep "cpu cores"| uniq  

```
**查看逻辑CPU的个数**  
```bash

    cat /proc/cpuinfo| grep "processor"| wc -l  

```  

## 监控特定端口号的进程。

#### 检测进程脚本
```ruby

    FILE_NAME="/var/log/dass/cron.log"
    REDIS_PORT=6379
    JAVA_PORT=25335

    APP_DIR=/app_root
    number=`ps -ef | grep  $REDIS_PORT | grep -v grep | wc -l`
    if [ $number -eq 0 ]
    then
        sh ${APP_DIR}/scripts/start-redis.sh
        sleep 2s
        pid=`ps -ef | grep $REDIS_PORT | grep -v grep | awk '{print $2}'`
        echo "Redis restarted succesfully", ${pid}, `date` >> $FILE_NAME
    fi

    number=`lsof -i tcp:${JAVA_PORT} | grep java | wc -l`
    if [ $number -eq 0 ]
    then
        sh ${APP_DIR}/scripts/start-jvm.sh &
        sleep 2s
        pid=`lsof -i tcp:${JAVA_PORT} | grep java | awk '{print $2}'`
        echo "Java Gateway restarted succesfully", ${pid}, `date` >> $FILE_NAME
    fi

```  

#### 定时任务
将检查脚本添加到定时任务  
crontab -e 编辑  
crontab -l list  
```ruby

    echo "* * * * * root sh ${APP_DIR}/scripts/monitor.sh >> /var/log/dass/cron.log 2>&1 &" >> /etc/cron.d/dass
    echo "* * * * * root sleep 15; sh ${APP_DIR}/scripts/monitor.sh >> /var/log/dass/cron.log 2>&1 &" >> /etc/cron.d/dass
    echo "* * * * * root sleep 30; sh ${APP_DIR}/scripts/monitor.sh >> /var/log/dass/cron.log 2>&1 &" >> /etc/cron.d/dass
    echo "* * * * * root sleep 45; sh ${APP_DIR}/scripts/monitor.sh >> /var/log/dass/cron.log 2>&1 &" >> /etc/cron.d/dass

```




