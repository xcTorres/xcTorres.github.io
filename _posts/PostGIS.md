---
layout:     post
title:      "PostGIS"
date:       2020-09-10
author:     "xcTorres"
header-img: "img/in-post/osm/osm-bg.png"
catalog:    true
mathjax: true
tags:
    - GIS
---  

# Overview
From OSM data introduction, we are more familiar with the original OSM data. But if we want to apply it to more scenarios, it is necessary to manage the map data in database.  

Besides all kinds of attributes, the map data have an important geometry feature. In our scenarios, we will have a lot of spatial queries. For example, query all of the records within certain bounding box, query the nearest points or polygons of certain point, etc. So compared to general query, we need a database which support spatial extension so that it is efficient to retrieve the data in spatial query.  

There are some databases that support spatial extension. PostGIS is an extension of the powerful PostgreSQL, one of the most reliable open source DBMS available, which has spent a lot of time on the market, but what makes it such a good platform for PostGIS is the fact that it implements something called Generic Index Structure (GIST), which allows it to build indexes in almost any kind of data type. It is an open source, many other open source is very easy to be compatible with it.

The whole world OSM data itself in [https://www.openstreetmap.org/](https://www.openstreetmap.org/) is also stored in postgreSQL and postGIS.

From my point of view,  there are  2 stages to manage the map data. 
- Just query the data
- Support the update, insert and delete operation.  

Update, insert and delete are more hard to implement, because it is complicated to consider both geometry and topology factors. So in current stage, we only focus on query the map data.  

# Deploy PostGIS
It is very easy to deploy the PostGIS using docker image. We could use docker-compose file because it could combine pgAdmin and postGIS together. Here is the docker-compose.yml file. The two service share an external network and the postGIS data is stored in mount volumes.

```yml

    version: '3'
    services:
    postgis:
        image: "postgis/postgis"
        ports:
        - "5432:5432"
        environment:
        - POSTGRES_PASSWORD=123456
        networks:
        - postgis
        volumes:
        - postgres-data:/var/lib/postgresql/data

    pgAdmin:
        image: "dpage/pgadmin4"
        ports:
        - "5433:80"
        environment:
        - PGADMIN_DEFAULT_EMAIL=test@123.com
        - PGADMIN_DEFAULT_PASSWORD=123456
        networks:
        - postgis

    volumes:
      postgres-data:

    networks:
      postgis:
        # Use a custom driver
        external:
        name: postgis

```
And then we could use following command to deploy.
```bat
 
    docker network create postgis
    docker-compose build
    docker-compose up

```

# Data ingestion  

In production environment, the map data format of Point, Line, Polygon is more understandable and more easy to transfer. [Osm2pgsql](https://wiki.openstreetmap.org/wiki/Osm2pgsql) is a mature tool to ingest osm data into postgresSQL database. It will create origin node, way, relation table from OSM data, and extract the point, line, polygon. One last table is roads table, which is a subset of line table and is used for rendering to map tile.  

<img src="/img/in-post/osm/osm2pgsql.png" width="600" height="500" title="Osm2pgsql database design">  

Before we upload the osm data, we need to use psql command to create a database and add spatial extention accordingly.
```bat

    ## Enter into the psql command
    docker run -it --network postgis --link postgis_postgis_1 --rm postgres  sh -c 'exec psql -h postgis -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres'


    1. \l  #list the datbase
    2. CREATE DATABASE test;
    3. \connect test
    4. CREATE EXTENSION IF NOT EXISTS postgis;
    5. CREATE EXTENSION IF NOT EXISTS hstore;

```
Upload the data, there are many options, plz refer to this [guide](https://wiki.openstreetmap.org/wiki/Osm2pgsql).
```bat

    osm2pgsql -s -U postgres -H 127.0.0.1 -P 5432 -W -d test ~/jakarta.osm.pbf

```
After completing the upload, you will see these table exists. And for point, line, polygon tables, they all have the extra spatial index.  

<img src="/img/in-post/osm/pgAdmin.jpg" width="700" height="700" title="pgAdmin"> 

<img src="/img/in-post/osm/qgis-postGIS-layer.png" width="700" height="700" title="pgAdmin"> 

# Spatial Query

- Query all of the data in certain bounding box

```SQL

    select * 
    from planet_osm_line 
    where way && ST_MakeEnvelope(106.620651, 10.73265, 106.725327, 10.8422, 4326)

```

- KNN Query  

```SQL

    SELECT
    *
    FROM
    (
        SELECT *, st_distance(
            st_transform(ST_GeomFromText('SRID=4326;Point(106.66169 10.75114)')::geometry, 3857),
            way) AS d
        FROM planet_osm_line
        ORDER BY way <-> st_transform(ST_GeomFromText('SRID=4326;Point(106.66169 10.75114)')::geometry, 3857) 
    ) as innerTable
    WHERE d < 100

```

- Get the distance, remember that st_distance function doesn't use gist spatial index  

```SQL

   select *, st_distance(
        ST_GeomFromText('SRID=4326;Point(106.620651 10.73265)')::geometry,
        way
    )
    from ho_chi_minh_way
    order by st_distance(
        ST_GeomFromText('SRID=4326;Point(106.620651 10.73265)')::geometry,
        way
    )
    limit 10

```


# Reference
[https://wiki.openstreetmap.org/wiki/Osm2pgsql](https://wiki.openstreetmap.org/wiki/Osm2pgsql)