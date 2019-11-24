---
layout:     post
title:      "Python Notes"
date:       2019-11-21
author:     "xcTorres"
header-img: "img/in-post/offer.jpg"
catalog:    true
tags:
    - Python
---

[algorithms](https://github.com/keon/algorithms)  
[python进阶](https://docs.pythontab.com/interpy/args_kwargs/README/)

#### 迭代器和生成器  
生成器同时也是一个迭代器，通过yield字段来实现。yield在函数中的功能类似于return，不同的是yield每次返回结果之后函数并没有退出，而是每次遇到yield关键字后返回相应结果，并保留函数当前的运行状态，等待下一次的调用。如果一个函数需要多次循环执行一个动作，并且每次执行的结果都是需要的，这种场景很适合使用yield实现。
包含yield的函数成为一个生成器，生成器同时也是一个迭代器，支持通过next方法获取下一个值。  
[[https://www.programiz.com/python-programming/generator]([https://www.programiz.com/python-programming/generator])

#### 拷贝和深拷贝的区别
[https://www.geeksforgeeks.org/copy-python-deep-copy-shallow-copy/](https://www.geeksforgeeks.org/copy-python-deep-copy-shallow-copy/)  
直接赋值：其实就是对象的引用（别名）。  
浅拷贝(copy)：拷贝父对象，不会拷贝对象的内部的子对象。  
深拷贝(deepcopy)： copy模块的deepcopy方法，完全拷贝了父对象及其子对象。

#### 装饰器到底该怎么用
[https://www.zhihu.com/question/26930016](https://www.zhihu.com/question/26930016)  

#### @staticmethod 和 @classmethod的区别  
- A class method takes cls as first parameter while a static method needs no specific parameters.  
- A class method can access or modify class state while a static method can’t access or modify it.  
- In general, static methods know nothing about class state. They are utility type methods that take some parameters and work upon those parameters. On the other hand class methods must have class as parameter.
- We use @classmethod decorator in python to create a class method and we use @staticmethod decorator to create a static method in python.

When to use what?

We generally use class method to create factory methods. Factory methods return class object ( similar to a constructor ) for different use cases.
We generally use static methods to create utility functions.
How to define a class method and a static method?

To define a class method in python, we use @classmethod decorator and to define a static method we use @staticmethod decorator.
Let us look at an example to understand the difference between both of them. Let us say we want to create a class Person. Now, python doesn’t support method overloading like C++ or Java so we use class methods to create factory methods. In the below example we use a class method to create a person object from birth year.

As explained above we use static methods to create utility functions. In the below example we use a static method to check if a person is adult or not.

```python

    # Python program to demonstrate 
    # use of class method and static method. 
    from datetime import date 

    class Person: 
        def __init__(self, name, age): 
            self.name = name 
            self.age = age 
        
        # a class method to create a Person object by birth year. 
        @classmethod
        def fromBirthYear(cls, name, year): 
            return cls(name, date.today().year - year) 
        
        # a static method to check if a Person is adult or not. 
        @staticmethod
        def isAdult(age): 
            return age > 18

    person1 = Person('mayank', 21) 
    person2 = Person.fromBirthYear('mayank', 1996) 

    print person1.age 
    print person2.age 

    # print the result 
    print Person.isAdult(22) 

```

#### 魔法方法
[https://pyzh.readthedocs.io/en/latest/python-magic-methods-guide.html](https://pyzh.readthedocs.io/en/latest/python-magic-methods-guide.html)

