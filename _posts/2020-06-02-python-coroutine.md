---
layout:     post
title:      "Python的协程与异步"
date:       2020-06-02
author:     "xcTorres"
header-img: "img/in-post/python/python.png"
catalog:    true
tags:
    - Python
---  

为了提高计算效率，在c++与java开发中我们经常听到高并发多线程的概念。而在Python语言中，由于GIL的存在，导致Python多线程性能甚至比单线程更糟。  
> GIL: 全局解释器锁（英语：Global Interpreter Lock，缩写GIL），是计算机程序设计语言解释器用于同步线程的一种机制，它使得任何时刻仅有一个线程在执行。[1]即便在多核心处理器上，使用 GIL 的解释器也只允许同一时间执行一个线程。 
> 这有Python官网的解释  [GlobalInterpreterLock](https://wiki.python.org/moin/GlobalInterpreterLock#:~:text=In%20CPython%2C%20the%20global%20interpreter,management%20is%20not%20thread%2Dsafe).  

Python为了克服这个问题，引入了协程Coroutine的概念。协程由于由程序主动控制切换，没有线程切换的开销，所以执行效率极高。对于IO密集型任务非常适用，如果是cpu密集型，推荐多进程+协程的方式。在Python3.4之前，官方没有对协程的支持，存在一些三方库的实现，比如gevent和Tornado。3.4之后就内置了asyncio标准库，官方真正实现了协程这一特性。而Python对协程的支持，是通过Generator实现的，协程是遵循某些规则的生成器，关于生成器Generator的好处可以参考如下介绍[https://www.programiz.com/python-programming/generator](https://www.programiz.com/python-programming/generator)。 


#### 参考  
[廖雪峰](https://www.liaoxuefeng.com/wiki/1016959663602400/1017968846697824)  
[https://juejin.im/post/5c13245ee51d455fa5451f33](https://juejin.im/post/5c13245ee51d455fa5451f33)  
[Python并行编程](https://python-parallel-programmning-cookbook.readthedocs.io/zh_CN/latest/)



