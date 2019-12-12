---
layout:     post
title:      "Python Web"
date:       2019-12-12
author:     "xcTorres"
header-img: "img/in-post/leetcode.jpg"
catalog:    true
tags:
    - Python
    - Web
--- 
## 背景
由于机器学习，深度学习，数据分析，数据挖掘的兴起，且因为Python脚本语言上手极快，使得Python这门语言非常火热🔥。但其应用场景多在运维，爬虫，以及机器学习数据挖掘。  

每当提及用Python作为后台开发语言，很多技术人士都会嗤之以鼻，担心其过慢的运行效率无法解决高并发问题。但Google搜索引擎的部分代码，Instagram，国内的豆瓣知乎等很多知名互联网企业都是Python语言的后台。这些成功的产品证明，只要处理得当，Python后台完全能处理一定量级的高并发问题。  

Java的确是一门不错的语言，但其Spring框架比较庞大，且我所在公司使用Go和Python语言，没有Java开发的环境。所以最终打算通过Python作为后台开发语言。每个人都要记得自己的长处和短处，如果说非要我和阿里的Java后台工程师和腾讯的C++工程师去比后台开发能力，那无疑是被碾成渣渣。  

现在本人的职位是算法工程师，更希望注重于算法的效果及实现，但在项目中不免要给算法做稳定的微服务。所以在工作过程中，算法的逻辑和稳定性和后台的稳定性有时候得一把抓，综合考虑打算使用flask，gunicorn，nginx的的方法来实现稳定的后台服务，特写此文用来记录Python后台记录的点点滴滴。  

## Flask
[flask](https://github.com/pallets/flask)是一个用于创建web应用的微服务框架，其主要由[werkzeug](https://github.com/pallets/werkzeug)作为WSGI服务器, 以及[jinja](https://github.com/pallets/jinja)进行前端渲染，在这二者的帮助下，我们可以用flask做一个业务逻辑的后台系统以及前端渲染的界面。  

由于工作原因，在我的日常工作中不需要去考虑界面，更多的是做一个能够接受http请求并返回数据的后台，则可以只考虑flask路由的部分。

## Guincorn
Gunciorn又是什么呢，首先Gunicorn是一个WSGI服务器。它不在乎它所运行的应用是哪一种，django也好，flask也好都OK，只要你应用的是WSGI接口。其采用的是pre-fork方式，其特点是具有使用非常简单，轻量级的资源消耗，以及高性能等特点。  

协程gevent+多进程提高效率



## 参考
[https://toutiao.io/posts/45fmtc/preview](https://toutiao.io/posts/45fmtc/preview)  
[gunicorn适用类型](https://medium.com/@genchilu/brief-introduction-about-the-types-of-worker-in-gunicorn-and-respective-suitable-scenario-67b0c0e7bd62)
[https://vsupalov.com/what-is-gunicorn/](https://vsupalov.com/what-is-gunicorn/)  
[深入理解uwsgi和gunicorn网络模型上](http://xiaorui.cc/2017/02/16/%e6%b7%b1%e5%85%a5%e7%90%86%e8%a7%a3uwsgi%e5%92%8cgunicorn%e7%bd%91%e7%bb%9c%e6%a8%a1%e5%9e%8b%e4%b8%8a/)
[https://juejin.im/post/5ce8cab8e51d4577523f22f8](https://juejin.im/post/5ce8cab8e51d4577523f22f8)

