---
layout:     post
title:      "CDH离线安装及卸载"
subtitle:   "CDH离线安装及卸载"
date:       2017-4-27 
author:     "xcTorres"
header-img: "img/post-bg-ios9-web.jpg"
tags:
    - 大数据
---

时间：2017/4/19

环境：CentOS-6.8;CM-5.9.0;CDH-5.10.0;


ip | host name
---|---
192.168.0.18 | cu18
192.168.0.19 | cu19
192.168.0.20 | cu20
192.168.0.28 | cu28
192.168.0.29 | cu29
192.168.0.17 | cu17(已搭建好的内网cm的yum源和cdh的parcels)

---


1、准备工作

1.1、修改机器的hostname。参考《搭建Hadoop伪分布式（Setting up a Single Node Cluster）》

1.2、关闭SELinux 。参考《CentOS配置selinux》

1.3、关闭iptables。参考《搭建Hadoop伪分布式（Setting up a Single Node Cluster）》

1.4、修改/etc/hosts文件，加入此次集群所用的到机器ip与hostname映射。参考《搭建Hadoop伪分布式（Setting up a Single Node Cluster）》

1.5、打通cu17的root用户到其他机器的root用户ssh（可选）。参考《CentOS配置允许root用户远程登录》、《搭建Hadoop伪分布式（Setting up a Single Node Cluster）》

1.6、重启机器

---

**2、搭建本地cm的yum源和cdh的parcels下载**

（分别参考《CentOS配置本地yum源（http方式）》和《CentOS配置本地服务器提供下载（http方式）》）

源包需从官网下载

cm5:http://archive.cloudera.com/cm5/


```
所需文件：

cloudera-manager-agent-5.9.0-1.cm590.p0.249.el6.x86_64.rpm

cloudera-manager-daemons-5.9.0-1.cm590.p0.249.el6.x86_64.rpm

cloudera-manager-server-5.9.0-1.cm590.p0.249.el6.x86_64.rpm

cloudera-manager-server-db-2-5.9.0-1.cm590.p0.249.el6.x86_64.rpm

enterprise-debuginfo-5.9.0-1.cm590.p0.249.el6.x86_64.rpm

jdk-6u31-linux-amd64.rpm

oracle-j2sdk1.7-1.7.0+update67-1.x86_64.rpm

repodata

cdh5:http://archive.cloudera.com/cdh5/

所需文件：
CDH-5.8.0-1.cdh5.8.0.p0.42-el6.parcel

CDH-5.8.0-1.cdh5.8.0.p0.42-el6.parcel.sha1

manifest.json
```


---



**3、下载installer脚本上传到cu17上：**

http://archive.cloudera.com/cm5/installer/5.x.x/

cloudera-manager-installer.bin

---


**4、安装CM**

给bin文件赋予可执行权限

sudo chmod u+x ./cloudera-manager-installer.bin

执行(使用root用户)

sudo ./cloudera-manager-installer.bin –-skip_repo_package=1  
![](/img/in-post/cdh-install/01.PNG)
![](/img/in-post/cdh-install/02.PNG)


一路NEXT+OK即可，最后提示访问http://${ip}:7180/,即CM安装成功

---

**5、CM使用外部数据库（可选）**

参考《CM配置使用外部数据库》

**6、界面部署**

6.1、登录CM
http://${ip}:7180/   admin/admin
![](/img/in-post/cdh-install/03.png)
6.2、版本选择（可使用数据集线器试用版60天）
![](/img/in-post/cdh-install/04.png)

6.3、检测可用机器（配置ssh很关键，不然检测不到其他机器）
![](/img/in-post/cdh-install/05.png)
![](/img/in-post/cdh-install/06.png)

6.4、配置CM和CDH包路径
![](/img/in-post/cdh-install/07.png)
![](/img/in-post/cdh-install/08.png)


6.5、安装JDK

![](/img/in-post/cdh-install/09.png)

6.7、集群用户模式

![](/img/in-post/cdh-install/10.png)

6.8、提供SSH凭据

![](/img/in-post/cdh-install/11.png)

6.9、安装cloudera-scm-agent（有可能报错，参考《安装cloudera-manager-agent报错》）
![](/img/in-post/cdh-install/12.png)

6.10、安装CDH的parcel
![](/img/in-post/cdh-install/13.png)

6.11、检查主机正确性（如果机器swap内存不为0,参考《CentOS配置swap》）
![](/img/in-post/cdh-install/14.png)

---


**7、集群设置**

这一步需要先在mysql数据库中建好对应的库并授权，示例如下


```
create database hive;
grant all privileges on hive.* to 'hive'@'%' identified by 'hive' with grant option;
create database hue;
grant all privileges on hue.* to 'hue'@'%' identified by 'hue' with grant option;
create database amon;
grant all privileges on amon.* to 'amon'@'%' identified by 'amon' with grant option;
create database rman;
grant all privileges on rman.* to 'rman'@'%' identified by 'rman' with grant option;
create database oozie;
grant all privileges on oozie.* to 'oozie'@'%' identified by 'oozie' with grant option;
flush privileges;
```


7.1、配置hive、hue等的外部数据库
![](/img/in-post/cdh-install/15.png)
![](/img/in-post/cdh-install/16.png)

7.2、集群部署

7.3、集群部署成功页面
![](/img/in-post/cdh-install/17.png)
![](/img/in-post/cdh-install/18.png)

------------------------------------------------------------------
## **卸载**


1、记录用户数据路径
删除用户数据 中列出的用户数据路径 /var/lib/flume-ng /var/lib/hadoop* /var/lib/hue /var/lib/navigator /var/lib/oozie /var/lib/solr /var/lib/sqoop* /var/lib/zookeeper /dfs /mapred /yarn 是默认设置。但是，在某些情况下它们可能已在 Cloudera Manager 中被重新配置。如果要从群集中删除所有用户数据且已更改了路径，那么，在安装 CDH 和托管服务时或在未来某个时间，检查每个服务中的配置并记下路径位置。

---

2、停止所有服务
2.1、停止 Cloudera Manager 管理的每个群集：在主页上，单击群集名称右侧的下拉图标并选择停止。确认单击停止。命令详细信息窗口显示了停止服务的进度。当出现已成功停止所有服务时，则该任务已完成。
2.2、停止 Cloudera Management Service：在主页上，单击 Cloudera Management Service 条目右侧的下拉图标并选择停止。命令详细信息窗口显示了停止服务的进度。当出现已成功停止所有服务时，则该任务已完成。

---

3、停用并删除 Parcel
3.1、如果安装时使用的是软件包，请跳过此步骤并转到卸载 Cloudera Manager Server；将删除卸载 Cloudera Manager Agent 和托管软件 中的软件包。
3.2、如果安装时使用的是 parcel，请删除它们，如下所示：
          单击主导航栏中的 Parcel 指示符 。
          对于每个激活的 parcel，选择操作 > 停用。完成此操作时，parcel 按钮将更改为激活。
          对于每个激活的包裹，选择操作 > 从主机删除。完成此操作时，parcel 按钮将更改为分配。
          对于每个激活的 parcel，选择操作 > 删除。这将从本地 parcel 存储库删除 parcel。
可能存在多个已下载和分配的 parcel，但处于非活动状态。在这种情况下，也应该从其已分发到的任何主机上删除这些 parcel，并从本地存储库中删除 parcel。

---

4、卸载 Cloudera Manager Server
卸载 Cloudera Manager Server 的命令取决于用于安装的方法。请参阅以下用于安装 Cloudera Manager Server 的方法相对应的步骤。

4.1、如果使用了 cloudera-manager-installer.bin文件 - 在 Cloudera Manager Server 主机上运行以下命令（自己只使用过这种方法）
sudo /usr/share/cmf/uninstall-cloudera-manager.sh

4.2、如果未使用 cloudera-manager-installer.bin 文件 - 如果使用其他安装方法（例如 Puppet）安装了 Cloudera Manager Server，在 Cloudera Manager Server 主机上执行以下命令。
停止 Cloudera Manager Server 及其数据库：
sudo service cloudera-scm-server stop
sudo service cloudera-scm-server-db stop
卸载 Cloudera Manager Server 及其数据库。上述过程还将删除嵌入式 PostgreSQL 数据库软件（如果您安装了该选项）。如果未使用嵌入式 PostgreSQL 数据库，则忽略 cloudera-manager-server-db 步骤。
sudo yum remove cloudera-manager-server
sudo yum remove cloudera-manager-server-db-2

---

5、卸载 Cloudera Manager Agent 和托管软件（在所有 Agent 主机上执行以下操作，建议使用pdsh这种批量工具，参考《pdsh》）

5.1、停止 Cloudera Manager Agent
sudo service cloudera-scm-agent hard_stop_confirmed

5.2、卸载软件
sudo yum remove 'cloudera-manager-*'

5.3、运行 clean 命令
sudo yum clean all

---

6、删除 Cloudera Manager 和用户数据（在所有 Agent 主机上执行以下操作，建议使用pdsh这种批量工具，参考《pdsh》）

6.1、终止 Cloudera Manager 和托管软件，在所有 Agent 主机上，终止正在运行的 Cloudera Manager 和托管进程
for u in cloudera-scm flume hadoop hdfs hbase hive httpfs hue impala llama mapred oozie solr spark sqoop sqoop2 yarn zookeeper; do sudo kill $(ps -u $u -o pid=); done

6.2、删除 Cloudera Manager 数据,此步骤将永久删除 Cloudera Manager 数据。如果希望能够在未来访问该数据，必须在删除前先将其备份。如果使用嵌入式 PostgreSQL 数据库，该数据存储在 /var/lib/cloudera-scm-server-db 中。在所有 Agent 主机上，请运行以下命令
sudo rm -Rf /usr/share/cmf /var/lib/cloudera* /var/cache/yum/cloudera* /var/log/cloudera* /var/run/cloudera*

6.3、删除 Cloudera Manager 锁定文件，在所有 Agent 主机上，请运行以下命令以删除 Cloudera Manager 锁定文件：
sudo rm /tmp/.scm_prepare_node.lock

6.4、删除用户数据，此步骤将永久删除所有用户数据。要保留数据，在开始卸载过程之前使用 distcp 命令将其复制到其他群集。在所有 Agent 主机上，请运行以下命令：
sudo rm -Rf /var/lib/flume-ng /var/lib/hadoop* /var/lib/hue /var/lib/navigator /var/lib/oozie /var/lib/solr /var/lib/sqoop* /var/lib/zookeeper
sudo rm -Rf /dfs /mapred /yarn 

---

7、停止和删除外部数据库
如果选择将 Cloudera Manager 或用户数据存储在外部数据库中，则查看数据库供应商文档以了解有关如何删除数据库的详细信息。

