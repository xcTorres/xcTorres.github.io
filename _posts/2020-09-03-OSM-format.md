---
layout:     post
title:      "OSM数据格式"
date:       2020-09-03
author:     "xcTorres"
header-img: "img/in-post/osm/osm-bg.png"
catalog:    true
mathjax: true
tags:
    - GIS
---  

有着地图界的维基百科之称的OpenStreetMap（OSM）为我们打开了一扇通往新世界的大门，包含了丰富的地理数据，给予了地理、规划以及对空间句法、空间分析、空间规划感兴趣的人提供了许多便利, 也让我们得以在商业发展初期可以有这样好的地理数据做基础。  

## 数据
#### 格式
两种主要使用的格式分别是XML文件以及PBF文件。XML文件好处是可读，但所占内存很大。而PBF指protoBuf文件，是一种高压缩文件。关于格式的细节可在wiki上查找。  

[https://wiki.openstreetmap.org/wiki/PBF_Format](https://wiki.openstreetmap.org/wiki/PBF_Format)  
[https://wiki.openstreetmap.org/wiki/OSM_XML](https://wiki.openstreetmap.org/wiki/OSM_XML)

#### 内容
无论是采用XML还是PBF的数据格式，只是数据的组织和解析不同，内容都是一致的。OpenStreetMap有三种元素，分别是Node， Way，还有Relation，并通过Tag给不同的元素添加属性。有了这些元素，就可以用来表示地图上的所有特征了。  

- **Node**  

一个Node通过经纬度代表地球表面上的一个特定节点，其最少包含一个id，还有经纬度字段。Node既可以用来定义某个单一点要素，比如某个公园长凳，某个水井，多个Node也可以用来定义一条路的形状。当其用来表示路时，通常节点是不需要Tag来添加属性的。但有时候也会给路上的特定节点添加属性，比如交通信号灯🚥，比如高压电线塔等等。

- **Way**   

Way是地图数据中非常重要的一环，是由2-2000个Node组成的一个点序列，通常被用来定义线性要素比如道路和河流。Way也能用来表示封闭区域，比如建筑物🏠，森林。在封闭区域中，点序列是首尾相连的，被称作**closed_way**，所以这个字段非常重要，我们可以用来区分Way是否是封闭区域。对于一些带洞的面要素或者超过2000节点的面要素，不能被一条Way来表示，OSM所采取的办法就是分成多个面要素并用Relation关联起来。

- **Relation**  

Relation是一种能够同时记录两个或多个Nodes，Ways等元素关系的这样一种数据结构。  
在**route relation**中， 其可以表示多个路的关系，比如多条路组成一条高速公路🛣，一条自行车🚲路，或一条公交车🚌路线。  
在**turn restriction**中，其表示从一条路直接进入另一条路是不被允许的。
 that says you can't turn from one way into another way.  
在**multipolygon**中，其可以用来表示polygon之间的关系，比如是内含还是外包。  
从以上示例中不难发现，Relation可以表示很多不一样的关系，而这个关系是通过Tag中的type来定义的。

#### 下载  

可以通过该网站下载世界各地的OpenStreetMap地图矢量数据
[http://download.geofabrik.de/](http://download.geofabrik.de/)  
该网站中包含了各个大陆以及国家的OSM数据，可以先下载下来再用其他相应的工具根据Boundingbox切割。如以[osmium](https://github.com/osmcode/osmium-tool)为例，可用以下命令切割,拿到印尼首都雅加达的数据。
```bat

    # extract data by bounding box
    osmium extract -b 106.6360,-6.3644,107.0927,-6.0794 ~/Desktop/indonesia-latest.osm.pbf -o ~/Desktop/jakarta.osm.pbf

```

## POSTGIS+QGIS 
[QGIS](https://docs.qgis.org/2.14/en/docs/user_manual/working_with_ogc/ogc_client_support.html)是一个开源的功能齐全的地图编辑软件，其本身就支持直接打开OSM文件，但是当OSM文件较大时，在QGIS加载就会变的很卡很慢，甚至加载不出来。  

一种比较好的组合方式是通过Osm2pgsql工具先将OSM文件导入到PostgreSQL数据库中，并且可以根据需要在PostGIS中添加空间索引，用于之后提高空间查询效率。之所以选用PostgreSQL的原因是其是一个开源的功能齐全的关系型数据库，且有非常好的地理支撑（PostGIS），且OpenStreetMap本身也是将数据存在PostgreSQL数据库中的，有足够多的开源工具能够一键从OSM文件导入到数据库中。  

![Osm2pgsql database design](/img/in-post/osm/osm2pgsql.png)

[osm2pgsql](https://wiki.openstreetmap.org/wiki/Osm2pgsql)是OpenStreetMap的官方工具库，下面先看看它是如何把原始的OSM转化成Postgresql数据库中的各个数据表。不难看出如果选择slim模式其仍能够保存OSM原始的Node，Way，Relation三要素，且除此之外该工具已经帮我们提炼出来planet_osm_point, planet_osm_line， planet_osm_polygon三大要素集合。此外还有一个planet_osm_roads数据表，其所有数据都是重复的，是planet_osm_line有的。其保存了一些更粗粒度的geometry，用于地图渲染用途，因为渲染时无需处理所有细小的Geometry[(https://github.com/openstreetmap/osm2pgsql/issues/610)](https://github.com/openstreetmap/osm2pgsql/issues/610)。








## Reference  

[https://wiki.openstreetmap.org/wiki/Elements](https://wiki.openstreetmap.org/wiki/Elements)  
[https://wiki.openstreetmap.org/wiki/Map_Features](https://wiki.openstreetmap.org/wiki/Map_Features)  
[https://wiki.openstreetmap.org/wiki/Osm2pgsql/schema](https://wiki.openstreetmap.org/wiki/Osm2pgsql/schema)

