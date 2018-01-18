---
layout:     post
title:      "leaflet前端学习"
subtitle:   " "
date:       2018-01-18
author:     "xcTorres"
header-img: "img/post-bg-unix-linux.jpg"
tags:
    - 前端
---

L.GridLayer 是一个一般类，其用于HTML元素的格网切片。它是所有切片层(Tile Layer)的基类，且替换了之前版本的TileLayer.Canvas. GridLayer可以被用于扩展canvas, img 或者 div类型的html元素，支持切片的创建以及动画响应。


----------
用法示例：

 1） 同步
&nbsp;&nbsp;&nbsp;&nbsp;想要自定义切片层，则需继承GridLayer并且重写createTile()函数来绘制切片,该函数传递参数coords（其中 x，y为切片的序号 , z为缩放层级）

```
var CanvasLayer = L.GridLayer.extend({
    createTile: function(coords){
        // 创建画布
        var tile = L.DomUtil.create('canvas', 'leaflet-tile');
        // 获取Tile尺寸
        var size = this.getTileSize();
        tile.width = size.x;
        tile.height = size.y;
	   // 得到画布上下文，通过coords的x,y,z进行绘制
        var ctx = tile.getContext('2d');

        // return the tile so it can be rendered on screen
        return tile;
    }
});

```

 2） 异步
 &nbsp;&nbsp;&nbsp;&nbsp;切片的绘制也可以是异步的，当需要用到第三方库绘制的时候就显得格外有用了。一旦切片绘制完就可以将参数传递给done回调函数
 

```
var CanvasLayer = L.GridLayer.extend({
    createTile: function(coords, done){
        var error;
        // 创建画布
        var tile = L.DomUtil.create('canvas', 'leaflet-tile');
        // 获取Tile尺寸
        var size = this.getTileSize();
        tile.width = size.x;
        tile.height = size.y;
		// 异步绘制
        setTimeout(function() {
            done(error, tile);
        }, 1000);
        return tile;
    }
});

```
----------
示例： 绘制切片格网，显示每个切片的切片号，缩放层级。以及计算并显示每个切片左上角的经纬度。效果如下图：

![这里写图片描述](http://img.blog.csdn.net/20170625201250830?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvdTAxMDc5MzIzNg==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

代码如下：

```
<!DOCTYPE html>
<html>  
<head>
    <title>GridLayer Test</title>
    <meta charset="utf-8" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.1/dist/leaflet.css" />
    <style>
        body {
            padding: 0;
            margin: 0;
        }
        html, body, #map {
            height: 100%;
            width: 100%;
        }
    </style>
</head>
<body>
    <div id="map"></div>

    <script src="https://unpkg.com/leaflet@1.0.1/dist/leaflet.js"></script>

    <script>
		var map = new L.Map('map', {  center: [10, 0], zoom: 2});
		
		var tiles = new L.GridLayer();
		tiles.createTile = function(coords) {
		  var tile = L.DomUtil.create('canvas', 'leaflet-tile');
		  var ctx = tile.getContext('2d');
		  var size = this.getTileSize()
		  tile.width = size.x
		  tile.height = size.y
		  
		  // 将切片号乘以切片分辨率，默认为256pixel,得到切片左上角的绝对像素坐标
		  var nwPoint = coords.scaleBy(size)
		  
		  // 根据绝对像素坐标，以及缩放层级，反投影得到其经纬度
		  var nw = map.unproject(nwPoint, coords.z)
		  
		  ctx.fillStyle = 'white';
		  ctx.fillRect(0, 0, size.x, 50);
		  ctx.fillStyle = 'black';
		  ctx.fillText('x: ' + coords.x + ', y: ' + coords.y + ', zoom: ' + coords.z, 20, 20);
		  ctx.fillText('lat: ' + nw.lat + ', lon: ' + nw.lng, 20, 40);
		  ctx.strokeStyle = 'red';
		  ctx.beginPath();
		  ctx.moveTo(0, 0);
		  ctx.lineTo(size.x-1, 0);
		  ctx.lineTo(size.x-1, size.y-1);
		  ctx.lineTo(0, size.y-1);
		  ctx.closePath();
		  ctx.stroke();
		  return tile;
		}
		
		L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		   attribution: 'Map data &copy; <a href="http://www.osm.org">OpenStreetMap</a>'
		}).addTo(map)
			
		tiles.addTo(map)
    </script>
</body>
</html>
```


