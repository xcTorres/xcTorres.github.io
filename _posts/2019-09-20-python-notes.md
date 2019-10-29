---
layout:     post
title:      "Python Notes"
date:       2019-09-20
author:     "xcTorres"
header-img: "img/in-post/offer.jpg"
catalog:    true
tags:
    - Python
---

[algorithms](https://github.com/keon/algorithms)  
[python进阶](https://docs.pythontab.com/interpy/args_kwargs/README/)

####迭代器和生成器  
生成器同时也是一个迭代器，通过yield字段来实现。yield在函数中的功能类似于return，不同的是yield每次返回结果之后函数并没有退出，而是每次遇到yield关键字后返回相应结果，并保留函数当前的运行状态，等待下一次的调用。如果一个函数需要多次循环执行一个动作，并且每次执行的结果都是需要的，这种场景很适合使用yield实现。
包含yield的函数成为一个生成器，生成器同时也是一个迭代器，支持通过next方法获取下一个值。

