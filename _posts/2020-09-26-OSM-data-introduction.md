---
layout:     post
title:      "OSM data introduction"
date:       2020-09-26
author:     "xcTorres"
header-img: "img/in-post/osm/osm-bg.png"
catalog:    true
mathjax: true
tags:
    - GIS
---  

# Overview  

OpenStreetMap (OSM) is a collaborative project to create a free editable map of the world. In this page, I want to introduce the structure of OSM data and how to use OSM data into our business.


# Data content  
## Elements  
Elements are the basic components of OpenStreetMap's conceptual data model of the physical world. They consist of
- [nodes](https://wiki.openstreetmap.org/wiki/Node) (defining points in space). 
- [ways](https://wiki.openstreetmap.org/wiki/Way) (defining linear features and area boundaries), and
- [relations](https://wiki.openstreetmap.org/wiki/Relation) (which are sometimes used to explain how other elements work together).
All of the above can have one or more associated tags (which describe the meaning of a particular element).

### Node
A node is one of the core elements in the OpenStreetMap data model. It consists of a single point in space defined by its latitude, longitude and node id.  
Nodes can be used to define standalone point features, but are more often used to define the shape or "path" of a way.  
As of September 2020, OpenStreetMap contains over 6 billion nodes.

- Point features  
Nodes can be used on their own to define point features. When used in this way, a node will normally have at least one tag to define its purpose. Nodes may have multiple tags and/or be part of a relation. For example, a telephone box may be tagged simply with amenity=telephone.

- Nodes on Ways  
Many nodes form part of one or more ways, defining the shape or "path" of the way.  

- Structure  

|  name   | value  |  description  |  
|  ----   | ----   |     ----      |  
| id    |  64-bit integer number≥ 1  |     Node ids are unique between nodes. (However, a way or a relation can have the same id number as a node.) Editors may temporarily save node ids as negative to denote ids that haven't yet been saved to the server. Node ids on the server are persistent, meaning that the assigned id of an existing node will remain unchanged each time data are added or corrected. Deleted node ids must not be reused, unless a former node is now undeleted.     |  
| lat   | decimal number ≥ −90.0000000 and ≤ 90.0000000 with 7 decimal places  |     Latitude coordinate in degrees (North of equator is positive) using the standard WGS84 projection. Some applications may not accept latitudes above/below ±85 degrees for some projections.     |  
| lon   | decimal number ≥ −180.0000000 and ≤ 180.0000000 with 7 decimal places  |     Longitude coordinate in degrees (East of Greenwich is positive) using the standard WGS84 projection. Note that the geographic poles will be exactly at latitude ±90 degrees but in that case the longitude will be set to an arbitrary value within this range.     |  
| tags   | A set of key/value pairs, with unique key  |     See [Map Features](https://wiki.openstreetmap.org/wiki/Map_Features) for tagging guidelines.     | 

#### Example

```html

    <node id="25496583" lat="51.5173639" lon="-0.140043" version="1" changeset="203496" user="80n" uid="1238" visible="true" timestamp="2007-01-28T11:40:26Z">
        <tag k="highway" v="traffic_signals"/>
    </node>

```  
Visualization: [https://www.openstreetmap.org/node/25496583#map=19/51.52092/-0.14281](https://www.openstreetmap.org/node/25496583#map=19/51.52092/-0.14281)


### Way
A way is an ordered list of nodes which normally also has at least one tag or is included within a Relation. A way can have between 2 and 2,000 nodes, although it's possible that faulty ways with zero or a single node exist. A way can be open or closed. A closed way is one whose last node on the way is also the first on that way. A closed way may be interpreted either as a closed polyline, or an area, or both.

- Open way (Open polyline) way

An open way is way describing a linear feature which does not share a first and last node. Many roads, streams and railway lines are open ways. Identifying the direction of a 'way'.

- Closed way (Closed polyline) closed way

A closed way is a way where the last node of the way is shared with the first node with suitable tagging. A closed way that also has a area=yes tag should be interpreted as an area (but the tag is not required most of the time, see section below).  
The following closed way would be interpreted as closed polylines:  
highway=* Closed ways are used to define roundabouts and circular walks  
barrier=* Closed ways are used to define barriers, such as hedges and walls, that go completely round a property.

- Area area 

An area (also polygon) is an enclosed filled area of territory defined as a closed way. Most closed ways are considered to be areas even without an area=yes tag (see above for some exceptions). Examples of areas defined as closed ways include:  
leisure=park to define the perimeter of a park  
amenity=school to define the outline of a school  
For tags which can be used to define closed polylines it is necessary to also add an area=yes if an area is desired. Examples include:  
highway=pedestrian + area=yes to define a pedestrian square or plaza.  
Areas can also be described using one or more ways which are associated with a multipolygon relation.

- Combined closed-polyline and area 

It is possible for a closed way to be tagged in a way that it should be interpreted both as a closed-polylines and also as an area.  
For example, a closed way defining a roundabout surrounding a grassy area might be tagged simultaneously as :  
highway=primary + junction=roundabout, both being interpreted as a polyline along the closed way, and landuse=grass, interpreted on the area enclosed by the way.

#### Example
```html

    <way id="5090250" visible="true" timestamp="2009-01-19T19:07:25Z" version="8" changeset="816806" user="Blumpsy" uid="64226">
        <nd ref="822403"/>
        <nd ref="21533912"/>
        <nd ref="821601"/>
        <nd ref="21533910"/>
        <nd ref="135791608"/>
        <nd ref="333725784"/>
        <nd ref="333725781"/>
        <nd ref="333725774"/>
        <nd ref="333725776"/>
        <nd ref="823771"/>
        <tag k="highway" v="residential"/>
        <tag k="name" v="Clipstone Street"/>
        <tag k="oneway" v="yes"/>
    </way>

```
Visualization: [https://www.openstreetmap.org/way/5090250](https://www.openstreetmap.org/way/5090250)

### Relation  

A relation is a group of elements. To be more exact it is one of the core data elements that consists of one or more tags and also an ordered list of one or more nodes, ways and/or relations as members which is used to define logical or geographic relationships between other elements. A member of a relation can optionally have a role which describes the part that a particular feature plays within a relation.  


Main article: [Types of relation](https://wiki.openstreetmap.org/wiki/Types_of_relation)

- Multipolygon  
Multipolygons are one of two methods to represent area areas in OpenStreetMap. While most areas are represented as a single closed way closed way, almost all area features can also be mapped using multipolygon relations. This is needed when the area needs to exclude inner rings (holes), has multiple outer areas (exclaves), or uses more than ~2000 nodes.  
In the multipolygon relation, the inner and outer roles are used to specify whether a member way forms the inner or outer part of that polygon enclosing an area. For example, an inner way could define an island in a lake (which is mapped as relation).

- Bus route  
Each variation of a bus route itinerary is represented by a relation with type=route, route=bus and ref=* and operator=* tags. The first members in the route relation are the nodes representing the stops. These are ordered in the way the vehicles travel along them. Then the ways are added. In PT v2 the ways form an ordered sequence, along the stop nodes. The ways don't get roles. If they form a continuous sequence this is apparent from the continuous line along them (in JOSM's relation editor).

#### Example

```html

    <relation id="13" visible="true" version="25" changeset="74363810" timestamp="2019-09-11T16:30:55Z" user="Ferdinand0101" uid="9080271">
        <member type="way" ref="2907748" role="outer"/>
        <member type="way" ref="8125203" role="inner"/>
        <tag k="landuse" v="reservoir"/>
        <tag k="name" v="Swithland Reservoir"/>
        <tag k="type" v="multipolygon"/>
        <tag k="wikidata" v="Q7349363"/>
    </relation>
    
```
Visualization: [https://www.openstreetmap.org/relation/13](https://www.openstreetmap.org/relation/13)

# Data format


The most important formats are:

- PBF Format – highly compressed, optimized binary format similar to the API, recommended for data processing  
- OSM XML – XML format provided by the API. Please use PBF if you can.  
- OSM JSON - JSON format provided by the API, based on Overpass API JSON format.  
- o5m – for high-speed processing, uses PBF coding, has same structure as XML format, limited support by appliations  
- Overpass JSON – JSON variant of OSM XML, used by Overpass API  
- Level0L – more human readable OSM XML without <> and lowered redundancy  

The most two popular formats are XML and PBF format. XML format is easy to parse and readable. PBF format is a highly compressed file, so it is commonly used because the map data size is very huge in production environment .

# Reference 
[https://wiki.openstreetmap.org/wiki/Elements](https://wiki.openstreetmap.org/wiki/Elements)  
[https://wiki.openstreetmap.org/wiki/Node](https://wiki.openstreetmap.org/wiki/Elements)   
[https://wiki.openstreetmap.org/wiki/Way](https://wiki.openstreetmap.org/wiki/Elements)  
[https://wiki.openstreetmap.org/wiki/Relation](https://wiki.openstreetmap.org/wiki/Relation)  
[https://wiki.openstreetmap.org/wiki/Tags](https://wiki.openstreetmap.org/wiki/Tags)  
[https://wiki.openstreetmap.org/wiki/OSM_file_formats](https://wiki.openstreetmap.org/wiki/OSM_file_formats)

