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


#### Process  
1） 查看进程及端口号并删除进程号  
```bash

    lsof -i tcp:port 
    kill -9 PID  

```

2) 监控进程并重启
```bash

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
3）查找指定进程
```bash

    ps -ef  |grep xxx

```

4) 根据PID查看进程内存消耗情况
```bash 

    top -pid xxx

```

#### Disk  
1）查看磁盘分布
```bash
    
    df -h

```

2）查看磁盘容量  
```bash
    
    du 命令

```

#### 文本命令  
1）grep 命令:  
2）awk 命令: [http://www.runoob.com/linux/linux-comm-awk.html](http://www.runoob.com/linux/linux-comm-awk.html)  
3）sed 命令: [https://man.linuxde.net/sed](https://man.linuxde.net/sed)
```bash 

    - sed -i '' -e 's/^\(appendonly \).*/\1yes/' ~/Desktop/redis.conf  
    appendonly no => appendonly yes  
    # 注释 save 开头的配置 
    - sed -i '' -e 's/^[[:blank:]]*save/#&/' ~/Desktop/redis.conf 
    # 取消 save开头的配置
    - sed -i '' -e 's/^#\([[:blank:]]*save\)/\1/' ~/Desktop/redis.conf  

```

#### 定时任务
crontab -e 编辑  
crontab -l list  
```bash

    echo "* * * * * root sh ${APP_DIR}/scripts/monitor.sh >> /var/log/dass/cron.log 2>&1 &" >> /etc/cron.d/dass
    echo "* * * * * root sleep 15; sh ${APP_DIR}/scripts/monitor.sh >> /var/log/dass/cron.log 2>&1 &" >> /etc/cron.d/dass
    echo "* * * * * root sleep 30; sh ${APP_DIR}/scripts/monitor.sh >> /var/log/dass/cron.log 2>&1 &" >> /etc/cron.d/dass
    echo "* * * * * root sleep 45; sh ${APP_DIR}/scripts/monitor.sh >> /var/log/dass/cron.log 2>&1 &" >> /etc/cron.d/dass

```




