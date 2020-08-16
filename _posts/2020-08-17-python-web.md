---
layout:     post
title:      "Python Web"
date:       2020-08-17
author:     "xcTorres"
header-img: "img/in-post/leetcode.jpg"
catalog:    true
tags:
    - Python
    - Web
--- 
## 背景
由于机器学习，深度学习，数据分析，数据挖掘的兴起，且因为Python脚本语言上手极快，使得Python这门语言非常火热🔥。但其应用场景多在运维，爬虫，以及机器学习数据挖掘方面。现在本人的职位是算法工程师，更希望注重于机器学习深度学习算法的效果及实现，但在项目中不免要给算法做稳定的网络微服务。所以在工作过程中，算法的逻辑和稳定性和后台的稳定性有时候得一把抓。Java的确是一门不错的语言，但其Spring框架比较庞大，且我所在公司使用Go和Python语言，没有Java开发的环境。所以最终打算通过Python作为后台开发语言。  
每当提及用Python作为后台开发语言，很多技术人士都会嗤之以鼻，担心其过慢的运行效率无法解决高并发问题。但Google搜索引擎的部分代码，Instagram，国内的豆瓣知乎等很多知名互联网企业都是Python语言的后台。这些成功的产品证明，只要处理得当，Python后台完全能处理一定量级的高并发问题。综合考虑打算使用flask，gunicorn，nginx的的方法来实现稳定的后台服务，特写此文用来记录Python后台记录的点点滴滴。

先将代码地址放在此处[https://github.com/xcTorres/python_web](https://github.com/xcTorres/python_web)，欢迎star。

## Flask
[flask](https://github.com/pallets/flask)是一个用于创建web应用的微服务框架，其主要由[werkzeug](https://github.com/pallets/werkzeug)作为WSGI网络应用程序, 以及[jinja](https://github.com/pallets/jinja)进行前端渲染，在这二者的帮助下，我们可以用flask做一个业务逻辑的后台系统以及前端渲染的界面。  

由于工作原因，在我的日常工作中不需要去考虑界面，更多的是做一个能够接受http请求并返回数据的后台，则可以只考虑flask路由的部分。只需简单的几句话，就能跑起来一个web框架。Flask的确是一个轻便的web服务框架。

```python

    app = Flask(__name__)

    @app.route('/')
    def hello():
        name = request.args.get("name", "World")
        return f'Hello, {escape(name)}!'

```

如在使用flask编写个人博客的时候，该网站需要用户，博客，管理员，默认网页等各个视图。这样一来每个视图都会有其自己的路由函数，所有路由都堆在一起了。使用蓝图可以将其模块化，其组织方式一般有功能式架构和分区式架构。可以看到功能式架构中，所有模板在一起，所有蓝图注册视图函数在views文件夹下。在分区式架构中，按照每一部分所属的蓝图来组织你的应用。管理面板的所有的模板，视图和静态文件放在一个文件夹中，用户控制面板的则放在另一个文件夹中。选择使用哪种架构实际上是一个个人问题。两者间的唯一区别是表达层次性的方式不同 -- 你可以使用任意一种方式架构Flask应用 -- 所以你所需的就是选择贴近你的需求的那个。如果你的应用是由独立的，仅仅共享模型和配置的各组件组成，分区式将是个好选择。一个例子是允许用户建立网站的SaaS应用。你将会有独立的蓝图用于主页，控制面板，用户网站，和高亮面板。这些组件有着完全不同的静态文件和布局。如果你想要将你的蓝图提取成插件，或用之于别的项目，一个分区式架构将是正确的选择。  
  
更多关于URL路由详情以及flask扩展可以了解官网[https://flask.palletsprojects.com/en/1.1.x/](https://flask.palletsprojects.com/en/1.1.x/)

**功能式架构**
```python

    yourapp/
    __init__.py
    static/
    templates/
        home/
        control_panel/
        admin/
    views/
        __init__.py
        home.py
        control_panel.py
        admin.py
    models.py

```

**分区式架构**

```python

    yourapp/
        __init__.py
        admin/
            __init__.py
            views.py
            static/
            templates/
        home/
            __init__.py
            views.py
            static/
            templates/
        control_panel/
            __init__.py
            views.py
            static/
            templates/
        models.py

```

## Guincorn

Gunciorn又是什么呢，首先Gunicorn是一个WSGI服务器。它不在乎它所运行的应用是哪一种，django也好，flask也好都OK，只要你应用的是WSGI接口。其采用的是pre-fork方式，其特点是具有使用非常简单，轻量级的资源消耗，以及高性能等特点。那什么是WSGI呢。其全称Python Web Server Gateway Interface，指定了web服务器和Python web应用或web框架之间的标准接口，以提高web应用在一系列web服务器间的移植性。Gunicorn擅长管理多进程。且命令及其方便，可以使用sync，gevent，gthread等多种进程模式。可以根据不同场景需求选择不同的参数。

- Flask 内置 WebServer + Flask App = 弱鸡版本的 Server, 单进程（单 worker) / 失败挂掉 / 不易 Scale  
- Gunicorn + Flask App = 多进程（多 worker) / 多线程 / 失败自动帮你重启 Worker / 可简单Scale  
- 多 Nginx + 多 Gunicorn + Flask App = 小型多实例 Web 应用，一般也会给 gunicorn 挂 supervisor

## Supervisor
Gunicorn采取的主从模式，即master进程将管理多个子进程，若某个子进程挂了，主进程可以重新启动子进程。那么万一主进程也挂了怎么办，常用的方法是通过[supervisor](https://github.com/Supervisor/supervisor)进行监控。 

## 参考
[https://toutiao.io/posts/45fmtc/preview](https://toutiao.io/posts/45fmtc/preview)  
[gunicorn适用类型](https://medium.com/@genchilu/brief-introduction-about-the-types-of-worker-in-gunicorn-and-respective-suitable-scenario-67b0c0e7bd62)  
[https://vsupalov.com/what-is-gunicorn/](https://vsupalov.com/what-is-gunicorn/)  
[深入理解uwsgi和gunicorn网络模型上](http://xiaorui.cc/2017/02/16/%e6%b7%b1%e5%85%a5%e7%90%86%e8%a7%a3uwsgi%e5%92%8cgunicorn%e7%bd%91%e7%bb%9c%e6%a8%a1%e5%9e%8b%e4%b8%8a/)  
[https://juejin.im/post/5ce8cab8e51d4577523f22f8](https://juejin.im/post/5ce8cab8e51d4577523f22f8)  
[Flask+Gunicorn(协程)高并发的解决方法探究](https://youyou-tech.com/2019/09/11/Flask%2BGunicorn%28%E5%8D%8F%E7%A8%8B%29%E9%AB%98%E5%B9%B6/)  
[https://blog.csdn.net/huwh_/article/details/80497790](https://blog.csdn.net/huwh_/article/details/80497790)
