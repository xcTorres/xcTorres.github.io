---
layout:     post
title:      "GIS in Python"
date:       2021-06-02
author:     "xcTorres"
header-img: "img/in-post/2019.jpg"
catalog:    true
tags:
    - Finance
---  

In the daily work, we often use python to do the data analysis job. Currently, there are more and more spatial python packages, which makes it also very easy for us to do the GIS analysis. In the blog, I would like to introduce some basic usages.

# Geometry Format
#### **WKT**
Well-known text (WKT) is a text markup language for representing vector geometry objects. A binary equivalent, known as well-known binary (WKB), is used to transfer and store the same information in a more compact form convenient for computer processing but that is not human-readable. Here are some samples of WKT. For more details you may refer to [this](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry).

| Type     | Examples |  
| :------: |:--------:|   
| Point         | POINT (30 10) |  
| LineString    | LINESTRING (30 10, 10 30, 40 40)      |  
| Polygon       | POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))      |  
| Polygon(with hole) | POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))  |


#### **GeoJSON**
GeoJSON is an open standard format designed for representing simple geographical features, along with their non-spatial attributes. It is based on the JSON format. The format is very readable. First of all the type should be **FeatureCollection**, which means the GeoJSON file contains sets of geometric objects called **feature**. In features array it lists all of the geometric objects, including Point, LineString, Polygon. For more details you may refer to [this](https://en.wikipedia.org/wiki/GeoJSON).
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [102.0, 0.5]
      },
      "properties": {
        "prop0": "value0"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]
        ]
      },
      "properties": {
        "prop0": "value0",
        "prop1": 0.0
      }
    }
  ]
}
```

# [Shapely](https://shapely.readthedocs.io/en/stable/manual.html) 
The JTS Topology Suite (JTS) is an open source Java software library that provides an object model for planar geometry together with a set of fundamental geometric functions. GEOS (Geometry Engine - Open Source) is a C++ port of JTS. The two packages are very commonly used in GIS field.  

Shapely is just a python wrapper of GEOS. So you don't need to be afraid of the performance.
Here are many functions in its [manual page](https://shapely.readthedocs.io/en/stable/manual.html). Here I just introduce a few of them.

#### Create geomety  
- From coordinates  

```python
from shapely.geometry import Point
point = Point(0.0, 0.0)

from shapely.geometry import LineString
line = LineString([(0, 0), (1, 1)])

from shapely.geometry import Polygon
polygon = Polygon([(0, 0), (1, 1), (1, 0)])
```
--- 
- From geojson  

Shapely cannot directly read GeoJSON format, but it could convert feature part into geometric object.  

```python
from shapely.geometry import shape
data = {"type": "Point", "coordinates": (0.0, 0.0)}
geom = shape(data)
```

---

- From WKT    

```python
from shapely import wkt
p1 = wkt.loads('POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))')
p2 = wkt.loads('POLYGON((0.5 0, 1.5 0, 1.5 1, 0.5 1, 0.5 0))')
```
--- 

- From WKB 

```python
>>> from shapely import wkb
>>> pt = Point(0, 0)
>>> wkb.dumps(pt)
b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
>>> pt.wkb
b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
>>> pt.wkb_hex
'010100000000000000000000000000000000000000'
>>> wkb.loads(pt.wkb).wkt
'POINT (0 0)'
```

#### Rtree
When we use contain, intersect, within and other spatial function, if there are a great number of the polygons, it will be very slow if we use for loop to check one by one. Using Rtree will be very fast. 
```python
from shapely.strtree import STRtree

# polygon_list
polygon_id_list = [id(i) for i in polygon_list]
r_tree = STRtree(polygon_list)

pt = Point(0, 0)
target = None
candidate_result = r_tree.query(pt)
for polygon in candidate_result:
    if polygon.touches(pt):
        target = polygon
```

# Geopandas  
Geopandas is a combination of pandas, shapely, pyproj package.   

#### Read csv file
- If there is no wkt columns in the file but two coordinates columns. Here we assume the column names are 'latitude' and 'longtidue'.  

```python
import pandas as pd
import geopandas as gpd

df = pd.read_csv('myFile.csv')
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.latitude, df.longitude))
```
---  

- If there is one wkt column. We assume it called 'geometry'.

```python
import pandas as pd
import geopandas as gpd

df = pd.read_csv('myFile.csv')
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, crs='epsg:4326')
```
---  

- If there is a column whose format is GeoJSON format.    

```python
feature_coll = {
    "type": "FeatureCollection",
    "features": [
        {
            "id": "0",
            "type": "Feature",
            "properties": {"col1": "name1"},
            "geometry": {"type": "Point", "coordinates": (1.0, 2.0)},
            "bbox": (1.0, 2.0, 1.0, 2.0),
        },
        {
            "id": "1",
            "type": "Feature",
            "properties": {"col1": "name2"},
            "geometry": {"type": "Point", "coordinates": (2.0, 1.0)},
            "bbox": (2.0, 1.0, 2.0, 1.0),
        },
    ],
    "bbox": (1.0, 1.0, 2.0, 2.0),
}
df = geopandas.GeoDataFrame.from_features(feature_coll)
df
                  geometry   col1
0  POINT (1.00000 2.00000)  name1
1  POINT (2.00000 1.00000)  name2
```

#### Spatial Join


